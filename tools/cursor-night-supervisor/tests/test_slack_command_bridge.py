from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"
CONSUMER_PATH = REPO_ROOT / ".cursor/hooks/slack_command_consumer.py"
SOCKET_PATH = REPO_ROOT / ".cursor/hooks/slack_command_socket_mode.py"
HEARTBEAT_PATH = REPO_ROOT / "tools/cursor-night-supervisor/heartbeat_decision.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures/slack_command_events.json"

SPEC = importlib.util.spec_from_file_location("slack_command_bridge", BRIDGE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)

SOCKET_SPEC = importlib.util.spec_from_file_location("slack_command_socket_mode", SOCKET_PATH)
assert SOCKET_SPEC and SOCKET_SPEC.loader
socket_mode = importlib.util.module_from_spec(SOCKET_SPEC)
sys.modules[SOCKET_SPEC.name] = socket_mode
SOCKET_SPEC.loader.exec_module(socket_mode)

HEARTBEAT_SPEC = importlib.util.spec_from_file_location("heartbeat_decision_integration", HEARTBEAT_PATH)
assert HEARTBEAT_SPEC and HEARTBEAT_SPEC.loader
heartbeat = importlib.util.module_from_spec(HEARTBEAT_SPEC)
HEARTBEAT_SPEC.loader.exec_module(heartbeat)


class SlackCommandBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        policy = self.fixture["policy"]
        self.policy = bridge.CommandPolicy(
            policy["team_id"], policy["user_id"], policy["conversation_id"]
        )
        self.now = bridge.parse_utc(self.fixture["now"])
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.runtime_root = Path(self.temporary.name) / "runtime"
        self.store = bridge.AppendOnlyCommandStore(self.runtime_root)

    def event(self, name: str) -> dict:
        return dict(self.fixture["events"][name])

    def ingest(self, name: str, **kwargs) -> dict:
        decision = bridge.evaluate_event(self.event(name), self.policy, now=self.now)
        return self.store.ingest(decision, now=self.now, **kwargs)

    def json_lines(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_only_exact_commands_and_bound_approval_are_accepted(self) -> None:
        for name, expected in (
            ("status", "status"),
            ("pause", "pause"),
            ("resume", "resume"),
            ("approve_safe", "approve-safe"),
        ):
            with self.subTest(name=name):
                decision = bridge.evaluate_event(self.event(name), self.policy, now=self.now)
                self.assertTrue(decision.accepted)
                self.assertEqual(decision.command, expected)
                self.assertEqual(
                    decision.request_id,
                    "safe_ABCDE1" if expected == "approve-safe" else None,
                )

        variants = (
            ("status", "command-not-allowlisted"),
            ("fidget status now", "command-not-allowlisted"),
            ("FIDGET STATUS", "command-not-allowlisted"),
            ("fidget approve-safe", "approval-request-id-required"),
            ("fidget approve-safe safe_ABCD", "invalid-approval-request-id"),
            ("fidget approve-safe safe_" + "A" * 33, "invalid-approval-request-id"),
            ("fidget approve-safe safe_ABC!E", "invalid-approval-request-id"),
            ("fidget approve-safe  safe_ABCDE1", "invalid-approval-request-id"),
            ("fidget approve-safe safe_ABCDE1 && rm -rf /", "invalid-approval-request-id"),
            ("fidget run echo hello", "command-not-allowlisted"),
            ("please fidget pause", "command-not-allowlisted"),
        )
        for index, (text, expected_reason) in enumerate(variants):
            with self.subTest(text=text):
                event = self.event("status")
                event["event_id"] = "Ev-invalid-{}".format(index)
                event["text"] = text
                decision = bridge.evaluate_event(event, self.policy, now=self.now)
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.reason, expected_reason)
                self.assertIsNone(decision.request_id)

        for suffix_length in (5, 32):
            with self.subTest(suffix_length=suffix_length):
                command, request_id, reason = bridge.parse_exact_command(
                    "fidget approve-safe safe_" + "A" * suffix_length
                )
                self.assertEqual((command, reason), ("approve-safe", "accepted"))
                self.assertEqual(request_id, "safe_" + "A" * suffix_length)

    def test_team_user_and_conversation_are_exact_allowlists(self) -> None:
        fields = {
            "team_id": "TOTHER001",
            "user_id": "UOTHER001",
            "conversation_id": "DOTHER001",
        }
        expected = {
            "team_id": "team-not-allowed",
            "user_id": "user-not-allowed",
            "conversation_id": "conversation-not-allowed",
        }
        for field, value in fields.items():
            with self.subTest(field=field):
                event = self.event("status")
                event["event_id"] = "Ev-{}-mismatch".format(field)
                event[field] = value
                decision = bridge.evaluate_event(event, self.policy, now=self.now)
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.reason, expected[field])

    def test_unknown_fields_per_command_age_and_future_messages_are_rejected(self) -> None:
        extra = self.event("status")
        extra["raw_payload"] = {"dangerous": "content"}
        self.assertEqual(
            bridge.evaluate_event(extra, self.policy, now=self.now).reason,
            "unexpected-event-fields",
        )

        for name in ("pause", "resume", "approve_safe"):
            at_boundary = self.event(name)
            at_boundary["event_id"] = "Ev-{}-boundary".format(name)
            at_boundary["message_ts"] = "{:.6f}".format(self.now.timestamp() - 300)
            self.assertTrue(
                bridge.evaluate_event(at_boundary, self.policy, now=self.now).accepted,
                name,
            )

            stale = self.event(name)
            stale["event_id"] = "Ev-{}-stale".format(name)
            stale["message_ts"] = "{:.6f}".format(self.now.timestamp() - 300.001)
            self.assertEqual(
                bridge.evaluate_event(stale, self.policy, now=self.now).reason,
                "stale-message",
            )

        status_boundary = self.event("status")
        status_boundary["event_id"] = "Ev-status-boundary"
        status_boundary["message_ts"] = "{:.6f}".format(self.now.timestamp() - 900)
        self.assertTrue(bridge.evaluate_event(status_boundary, self.policy, now=self.now).accepted)

        stale_status = self.event("status")
        stale_status["event_id"] = "Ev-status-stale"
        stale_status["message_ts"] = "{:.6f}".format(self.now.timestamp() - 900.001)
        self.assertEqual(
            bridge.evaluate_event(stale_status, self.policy, now=self.now).reason,
            "stale-message",
        )

        future = self.event("status")
        future["event_id"] = "Ev-future"
        future["message_ts"] = str(int(self.now.timestamp()) + 61)
        self.assertEqual(
            bridge.evaluate_event(future, self.policy, now=self.now).reason, "future-message"
        )

    def test_store_rechecks_message_age_at_the_append_boundary(self) -> None:
        decision = bridge.evaluate_event(self.event("pause"), self.policy, now=self.now)
        self.assertTrue(decision.accepted)
        result = self.store.ingest(decision, now=self.now + dt.timedelta(seconds=301))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "stale-message")
        self.assertFalse(self.store.queue_path.exists())
        self.assertEqual(self.json_lines(self.store.audit_path)[0]["reason"], "stale-message")

    def test_status_expiry_also_uses_slack_message_time(self) -> None:
        event = self.event("status")
        event["message_ts"] = "{:.6f}".format(self.now.timestamp() - 899)
        decision = bridge.evaluate_event(event, self.policy, now=self.now)
        self.store.ingest(decision, now=self.now)
        queue = self.json_lines(self.store.queue_path)[0]
        self.assertEqual(
            queue["expiresAt"], bridge.format_utc(self.now + dt.timedelta(seconds=1))
        )

    def test_fractional_slack_timestamp_expiry_is_not_extended_or_truncated(self) -> None:
        for index, (age, remaining) in enumerate(((299.1, 0.9), (299.9, 0.1))):
            with self.subTest(age=age):
                event = self.event("approve_safe")
                event["event_id"] = "Ev-fractional-{}".format(index)
                event["message_ts"] = "{:.6f}".format(self.now.timestamp() - age)
                decision = bridge.evaluate_event(event, self.policy, now=self.now)
                store = bridge.AppendOnlyCommandStore(
                    Path(self.temporary.name) / "fractional-{}".format(index)
                )
                store.ingest(decision, now=self.now)
                queue = self.json_lines(store.queue_path)[0]
                self.assertEqual(
                    queue["expiresAt"],
                    bridge.format_utc(self.now + dt.timedelta(seconds=remaining)),
                )

    def test_rejected_free_text_is_hashed_not_persisted(self) -> None:
        result = self.ingest("shell_text")
        self.assertFalse(result["accepted"])
        self.assertFalse(self.store.queue_path.exists())
        audit_text = self.store.audit_path.read_text(encoding="utf-8")
        self.assertNotIn("rm -rf", audit_text)
        audit = json.loads(audit_text)
        self.assertEqual(audit["reason"], "command-not-allowlisted")
        self.assertEqual(audit["textLength"], len("rm -rf /"))
        self.assertEqual(len(audit["textSha256"]), 64)

    def test_dedupe_survives_new_store_instance(self) -> None:
        first = self.ingest("status")
        queue_before = self.store.queue_path.read_bytes()
        self.store.state_path.unlink()
        second_store = bridge.AppendOnlyCommandStore(self.runtime_root)
        decision = bridge.evaluate_event(self.event("status"), self.policy, now=self.now)
        second = second_store.ingest(decision, now=self.now)
        self.assertTrue(first["accepted"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(second["reason"], "duplicate-event")
        self.assertEqual(self.store.queue_path.read_bytes(), queue_before)
        self.assertEqual(len(self.json_lines(self.store.queue_path)), 1)
        self.assertEqual(
            json.loads(self.store.state_path.read_text(encoding="utf-8"))["pendingStatusCount"],
            1,
        )

    def test_dry_run_makes_no_runtime_files(self) -> None:
        result = self.ingest("pause", dry_run=True)
        self.assertTrue(result["accepted"])
        self.assertTrue(result["dryRun"])
        self.assertFalse(self.runtime_root.exists())

    def test_pause_resume_and_pending_state_are_derived_atomically(self) -> None:
        self.ingest("pause")
        pause_state = json.loads(self.store.state_path.read_text(encoding="utf-8"))
        self.assertTrue(pause_state["paused"])

        self.ingest("status")
        self.ingest("approve_safe")
        self.ingest("resume")
        state = self.store.snapshot(now=self.now)
        self.assertFalse(state["paused"])
        self.assertEqual(state["pendingStatusCount"], 1)
        self.assertEqual(state["pendingApproveSafeCount"], 1)
        self.assertEqual(state, json.loads(self.store.state_path.read_text(encoding="utf-8")))
        self.assertEqual(self.store.state_path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.runtime_root.stat().st_mode & 0o777, 0o700)

    def test_ack_is_append_only_idempotent_and_command_specific(self) -> None:
        self.ingest("status")
        queue_before = self.store.queue_path.read_bytes()
        with self.assertRaisesRegex(bridge.StoreError, "status-not-delivered"):
            self.store.acknowledge("Ev-status-001", "reported", now=self.now)
        self.store.record_status_delivery(
            "Ev-status-001",
            outcome="delivered",
            reason="webhook-ok",
            payload_sha256="0" * 64,
            team_id=self.policy.team_id,
            conversation_id=self.policy.conversation_id,
            http_status=200,
            now=self.now,
        )
        result = self.store.acknowledge("Ev-status-001", "reported", now=self.now)
        duplicate = self.store.acknowledge("Ev-status-001", "reported", now=self.now)
        self.assertTrue(result["acknowledged"])
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(self.store.queue_path.read_bytes(), queue_before)
        self.assertEqual(len(self.json_lines(self.store.consumption_path)), 1)
        self.assertEqual(self.store.snapshot(now=self.now)["pendingStatusCount"], 0)
        with self.assertRaisesRegex(bridge.StoreError, "outcome-not-valid-for-command"):
            other = bridge.AppendOnlyCommandStore(Path(self.temporary.name) / "other")
            decision = bridge.evaluate_event(self.event("status"), self.policy, now=self.now)
            other.ingest(decision, now=self.now)
            other.acknowledge("Ev-status-001", "applied", now=self.now)

    def test_approval_id_is_separate_and_expiry_uses_slack_message_time(self) -> None:
        event = self.event("approve_safe")
        event["message_ts"] = "{:.6f}".format(self.now.timestamp() - 299)
        decision = bridge.evaluate_event(event, self.policy, now=self.now)
        result = self.store.ingest(decision, now=self.now)
        self.assertEqual(result["requestId"], "safe_ABCDE1")

        queue = self.json_lines(self.store.queue_path)[0]
        audit = self.json_lines(self.store.audit_path)[0]
        self.assertEqual(queue["command"], "approve-safe")
        self.assertEqual(queue["requestId"], "safe_ABCDE1")
        self.assertEqual(audit["requestId"], "safe_ABCDE1")
        self.assertEqual(queue["receivedAt"], bridge.format_utc(self.now))
        self.assertEqual(
            queue["expiresAt"], bridge.format_utc(self.now + dt.timedelta(seconds=1))
        )

        state = self.store.snapshot(now=self.now)
        item = next(entry for entry in state["pending"] if entry["command"] == "approve-safe")
        self.assertEqual(item["requestId"], "safe_ABCDE1")
        self.assertFalse(item["expired"])
        state = self.store.snapshot(now=self.now + dt.timedelta(seconds=1))
        item = next(entry for entry in state["pending"] if entry["command"] == "approve-safe")
        self.assertTrue(item["expired"])
        self.assertEqual(state["pendingApproveSafeCount"], 0)

        acknowledged = self.store.acknowledge(
            "Ev-approve-001", "expired", now=self.now + dt.timedelta(seconds=1)
        )
        consumption = self.json_lines(self.store.consumption_path)[0]
        self.assertEqual(acknowledged["requestId"], "safe_ABCDE1")
        self.assertEqual(consumption["requestId"], "safe_ABCDE1")
        raw = self.store.queue_path.read_text(encoding="utf-8")
        self.assertNotIn("shell", raw.lower())
        self.assertNotIn("commandLine", raw)

    def test_refused_approval_is_consumed_and_cannot_reappear(self) -> None:
        self.ingest("approve_safe")
        self.assertEqual(self.store.snapshot(now=self.now)["pendingApproveSafeCount"], 1)
        result = self.store.acknowledge("Ev-approve-001", "refused", now=self.now)
        self.assertTrue(result["acknowledged"])
        state = self.store.snapshot(now=self.now)
        self.assertEqual(state["pendingApproveSafeCount"], 0)
        self.assertNotIn(
            "Ev-approve-001", {item["eventId"] for item in state["pending"]}
        )

    def test_claim_before_click_is_atomic_and_crash_non_replayable(self) -> None:
        self.ingest("approve_safe")
        observation = json.loads(
            (
                REPO_ROOT
                / "tools/cursor-night-supervisor/tests/fixtures/heartbeat/safe_pending.json"
            ).read_text(encoding="utf-8")
        )
        observation["slackControlState"] = self.store.snapshot(now=self.now)
        eligible = heartbeat.decide(observation, now=self.now)
        self.assertEqual(eligible["decision"]["action"], "claim")
        self.assertFalse(eligible["decision"]["click"])

        with self.assertRaisesRegex(bridge.StoreError, "outcome-not-valid-for-command"):
            self.store.acknowledge("Ev-approve-001", "applied", now=self.now)
        with self.assertRaisesRegex(bridge.StoreError, "approval-request-id-mismatch"):
            self.store.claim_approval("Ev-approve-001", "safe_OTHER1", now=self.now)

        claimed = self.store.claim_approval(
            "Ev-approve-001", "safe_ABCDE1", now=self.now
        )
        self.assertTrue(claimed["claimed"])
        after_crash = self.store.snapshot(now=self.now)
        self.assertEqual(after_crash["pendingApproveSafeCount"], 0)

        observation["slackControlState"] = after_crash
        replay = heartbeat.decide(observation, now=self.now)
        self.assertFalse(replay["decision"]["click"])
        self.assertFalse(replay["decision"]["claimRequired"])

        finalized = self.store.finalize_approval(
            "Ev-approve-001", "safe_ABCDE1", "applied", now=self.now
        )
        self.assertTrue(finalized["finalized"])
        self.assertEqual(
            [record["outcome"] for record in self.json_lines(self.store.consumption_path)],
            ["claimed", "applied"],
        )

    def test_missing_event_id_gets_a_stable_derived_identifier(self) -> None:
        event = self.event("status")
        del event["event_id"]
        first = bridge.evaluate_event(event, self.policy, now=self.now)
        second = bridge.evaluate_event(event, self.policy, now=self.now)
        self.assertTrue(first.event_id.startswith("slack:"))
        self.assertEqual(first.event_id, second.event_id)

    def test_schema_is_required_and_supplied_invalid_event_id_is_rejected(self) -> None:
        missing_schema = self.event("status")
        del missing_schema["schemaVersion"]
        decision = bridge.evaluate_event(missing_schema, self.policy, now=self.now)
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.reason, "missing-schema-version")

        for value in (None, "", "contains space", "x" * 161):
            with self.subTest(event_id=value):
                invalid_id = self.event("status")
                invalid_id["event_id"] = value
                decision = bridge.evaluate_event(invalid_id, self.policy, now=self.now)
                self.assertFalse(decision.accepted)
                self.assertEqual(decision.reason, "invalid-event-id")
                self.assertTrue(decision.event_id.startswith("slack:"))

    def test_any_authoritative_ledger_corruption_fails_closed(self) -> None:
        cases = (
            ("queue_path", "{\"schemaVersion\":\"1.0\"}\n", "invalid-command-ledger"),
            ("audit_path", "{not-json\n", "invalid-audit-ledger"),
            ("consumption_path", "{}\n", "invalid-consumption-ledger"),
        )
        for index, (attribute, corrupt_line, expected) in enumerate(cases):
            with self.subTest(ledger=attribute):
                store = bridge.AppendOnlyCommandStore(
                    Path(self.temporary.name) / "corrupt-{}".format(index)
                )
                decision = bridge.evaluate_event(self.event("pause"), self.policy, now=self.now)
                store.ingest(decision, now=self.now)
                path = getattr(store, attribute)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(corrupt_line)
                with self.assertRaisesRegex(bridge.StoreError, expected):
                    store.snapshot(now=self.now)
                with self.assertRaisesRegex(bridge.StoreError, expected):
                    store.acknowledge("Ev-pause-001", "applied", now=self.now)

    def test_consumer_cli_snapshot_and_ack(self) -> None:
        self.ingest("status")
        self.store.record_status_delivery(
            "Ev-status-001",
            outcome="delivered",
            reason="webhook-ok",
            payload_sha256="0" * 64,
            team_id=self.policy.team_id,
            conversation_id=self.policy.conversation_id,
            http_status=200,
            now=self.now,
        )
        snapshot = subprocess.run(
            [
                sys.executable,
                str(CONSUMER_PATH),
                "--runtime-root",
                str(self.runtime_root),
                "--now",
                self.fixture["now"],
                "snapshot",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(snapshot.returncode, 0, snapshot.stderr)
        self.assertEqual(json.loads(snapshot.stdout)["pendingStatusCount"], 1)

        acknowledge = subprocess.run(
            [
                sys.executable,
                str(CONSUMER_PATH),
                "--runtime-root",
                str(self.runtime_root),
                "--now",
                self.fixture["now"],
                "ack",
                "--event-id",
                "Ev-status-001",
                "--outcome",
                "reported",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(acknowledge.returncode, 0, acknowledge.stderr)
        self.assertTrue(json.loads(acknowledge.stdout)["acknowledged"])

    def test_ingest_cli_reads_sanitized_stdin_without_echoing_text(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(BRIDGE_PATH),
                "--dry-run",
                "--runtime-root",
                str(self.runtime_root),
                "--allowed-team-id",
                self.policy.team_id,
                "--allowed-user-id",
                self.policy.user_id,
                "--allowed-conversation-id",
                self.policy.conversation_id,
                "--now",
                self.fixture["now"],
            ],
            input=json.dumps(self.event("status")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["command"], "status")
        self.assertNotIn("fidget status", completed.stdout)
        self.assertFalse(self.runtime_root.exists())

    def test_parallel_ingest_processes_append_the_command_once(self) -> None:
        argv = [
            sys.executable,
            str(BRIDGE_PATH),
            "--runtime-root",
            str(self.runtime_root),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--now",
            self.fixture["now"],
        ]
        payload = json.dumps(self.event("status"))
        processes = [
            subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(2)
        ]
        results = [process.communicate(payload, timeout=10) for process in processes]
        self.assertEqual([process.returncode for process in processes], [0, 0])
        decoded = [json.loads(stdout) for stdout, _ in results]
        self.assertEqual(sum(1 for result in decoded if result["accepted"]), 1)
        self.assertEqual(sum(1 for result in decoded if result["duplicate"]), 1)
        self.assertEqual(len(self.json_lines(self.store.queue_path)), 1)


class SlackSocketModeAdapterTests(unittest.TestCase):
    def test_socket_event_is_reduced_to_sanitized_fields(self) -> None:
        envelope = {
            "type": "events_api",
            "envelope_id": "env-001",
            "payload": {
                "type": "event_callback",
                "team_id": "TWHATNOT1",
                "event_id": "Ev-live-001",
                "event": {
                    "type": "message",
                    "user": "UJIAWEI01",
                    "channel": "DCTRL0001",
                    "ts": "1788782395.000001",
                    "text": "fidget status",
                    "attachments": [{"text": "must not cross the boundary"}],
                },
            },
        }
        item = socket_mode.socket_event(envelope)
        self.assertEqual(item.control, "ingest")
        self.assertEqual(item.envelope_id, "env-001")
        self.assertEqual(set(item.sanitized), bridge.SANITIZED_EVENT_KEYS)
        self.assertNotIn("attachments", item.sanitized)

    def test_socket_adapter_ignores_subtypes_bots_and_threads(self) -> None:
        base = {
            "type": "events_api",
            "envelope_id": "env-001",
            "payload": {
                "type": "event_callback",
                "team_id": "TWHATNOT1",
                "event_id": "Ev-live-001",
                "event": {
                    "type": "message",
                    "user": "UJIAWEI01",
                    "channel": "DCTRL0001",
                    "ts": "1788782395.000001",
                    "text": "fidget status",
                },
            },
        }
        for field, value, reason in (
            ("subtype", "message_changed", "message-subtype"),
            ("bot_id", "B123", "bot-message"),
            ("thread_ts", "1788782300.1", "thread-message"),
        ):
            with self.subTest(field=field):
                envelope = json.loads(json.dumps(base))
                envelope["payload"]["event"][field] = value
                item = socket_mode.socket_event(envelope)
                self.assertEqual(item.control, "ignore")
                self.assertEqual(item.ignore_reason, reason)

    def test_rate_limit_retry_after_and_exponential_backoff(self) -> None:
        headers = Message()
        headers["Retry-After"] = "37"
        error = urllib.error.HTTPError(
            socket_mode.CONNECTIONS_OPEN_URL, 429, "rate limited", headers, None
        )
        with mock.patch.object(socket_mode.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(socket_mode.RetryableTransportError) as caught:
                socket_mode.open_socket_url("xapp-" + "a" * 30)
        self.assertEqual(caught.exception.reason, "rate-limited")
        self.assertEqual(caught.exception.retry_after, 37)
        self.assertEqual(socket_mode.retry_delay(1, retry_after=37, jitter=0.9), 37.0)
        self.assertEqual(socket_mode.retry_delay(9, jitter=1.0), 61.0)

    def test_socket_cli_dry_run_has_no_network_or_runtime_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary) / "runtime"
            env = dict(os.environ)
            env["SLACK_COMMAND_APP_TOKEN"] = "xapp-" + "a" * 30
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SOCKET_PATH),
                    "--dry-run",
                    "--runtime-root",
                    str(runtime),
                    "--allowed-team-id",
                    "TWHATNOT1",
                    "--allowed-user-id",
                    "UJIAWEI01",
                    "--allowed-conversation-id",
                    "DCTRL0001",
                ],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertFalse(result["networkAttempted"])
            self.assertFalse(result["runtimeWritten"])
            self.assertNotIn(env["SLACK_COMMAND_APP_TOKEN"], completed.stdout)
            self.assertFalse(runtime.exists())


if __name__ == "__main__":
    unittest.main()
