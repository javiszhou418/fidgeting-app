from __future__ import annotations

import importlib.util
import datetime as dt
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"
ROUTER_PATH = REPO_ROOT / ".cursor/hooks/slack_nl_router.py"
CATALOG_PATH = REPO_ROOT / "tools/cursor-night-supervisor/slack-nl-task-catalog.json"

if "slack_command_bridge" not in sys.modules:
    spec = importlib.util.spec_from_file_location("slack_command_bridge", BRIDGE_PATH)
    assert spec and spec.loader
    bridge = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = bridge
    spec.loader.exec_module(bridge)
else:
    bridge = sys.modules["slack_command_bridge"]

router_spec = importlib.util.spec_from_file_location("slack_nl_router", ROUTER_PATH)
assert router_spec and router_spec.loader
router = importlib.util.module_from_spec(router_spec)
sys.modules[router_spec.name] = router
router_spec.loader.exec_module(router)


class SlackNaturalLanguageRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.bridge_store = bridge.AppendOnlyCommandStore(base / "bridge")
        self.store = router.NaturalLanguageStore(base / "nl")
        self.policy = bridge.CommandPolicy(
            "T0C00P256DA", "U0BV4S23X8B", "D0C0RELGU56"
        )
        self.host = "jw-qgi5008.slack.com"
        self.now = bridge.parse_utc("2026-09-08T00:00:00Z")
        self.base_ts = "1788825590.000000"
        self.catalog = router.load_task_catalog(CATALOG_PATH)
        self.poll_index = 0

    def event(self, text: str, *, ts: str | None = None, event_id: str | None = None) -> dict:
        timestamp = ts or "1788825595.000001"
        return {
            "schemaVersion": "1.0",
            "team_id": self.policy.team_id,
            "user_id": self.policy.user_id,
            "conversation_id": self.policy.conversation_id,
            "event_id": event_id or "Ev-nl-{}".format(self.poll_index + 1),
            "message_ts": timestamp,
            "text": text,
        }

    def commit_human_event(self, event: dict, *, base: str | None = None) -> str:
        base_cursor = base or (
            self.bridge_store.source_cursor(bridge.SLACK_NATIVE_CUA_SOURCE, self.policy)[
                "cursor"
            ]
            if self.bridge_store.source_cursor_ledger_path.exists()
            else self.base_ts
        )
        if not self.bridge_store.source_cursor_ledger_path.exists():
            self.bridge_store.bootstrap_source_cursor(
                bridge.SLACK_NATIVE_CUA_SOURCE,
                self.policy,
                base_cursor,
                now=self.now,
            )
        self.poll_index += 1
        poll_id = "poll_NLTEST{:04d}".format(self.poll_index)
        decision = bridge.evaluate_native_cua_event(event, self.policy, now=self.now)
        row = bridge.SourceObservationRow(
            message_ts=event["message_ts"],
            kind="self-message",
            permalink="https://{}/archives/{}/p{}".format(
                self.host,
                self.policy.conversation_id,
                event["message_ts"].replace(".", ""),
            ),
        )
        self.bridge_store.ingest_source_batch(
            [decision],
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.host,
            base_cursor=base_cursor,
            next_cursor=event["message_ts"],
            observed_rows=[row],
            poll_id=poll_id,
            now=self.now,
        )
        return poll_id

    def commit_empty_poll(self) -> str:
        cursor = self.bridge_store.source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy
        )["cursor"]
        self.poll_index += 1
        poll_id = "poll_NLTEST{:04d}".format(self.poll_index)
        self.bridge_store.ingest_source_batch(
            [],
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.host,
            base_cursor=cursor,
            next_cursor=cursor,
            observed_rows=[],
            poll_id=poll_id,
            now=self.now,
        )
        return poll_id

    @staticmethod
    def classification(
        intent: str,
        *,
        target: str | None = None,
        action: str | None = None,
        clarification: str | None = None,
        recipient: str | None = None,
    ) -> dict:
        return {
            "schemaVersion": "1.0",
            "intent": intent,
            "recipient": recipient or ("cursor" if intent == "action" else None),
            "targetKey": target,
            "action": action,
            "clarificationCode": clarification,
        }

    def observation(
        self,
        *,
        lease_id: str = "lease_TESTROUND01",
        inspection_id: str = "inspect_TESTROUND01",
    ) -> dict:
        return {
            "schemaVersion": "1.0",
            "catalogVersion": self.catalog.version,
            "inspectionId": inspection_id,
            "observedAt": bridge.format_utc(self.now),
            "roundLeaseId": lease_id,
            "userUiIdle": True,
            "controller": {
                **dict(self.catalog.controller),
                "status": "running",
            },
            "targets": [
                {
                    "targetKey": target.target_key,
                    "backend": target.backend,
                    "threadId": target.thread_id,
                    "exactTitle": target.exact_title,
                    "authority": target.authority,
                    "state": "safe-pending",
                    "stateVersion": "state_TARGET0{}".format(index),
                    "uiUnambiguous": True,
                    "composerEmpty": True,
                    "visible": True,
                    "exactTitleMatchCount": 1,
                    "workspaceRoot": self.catalog.controller["projectRoot"],
                }
                for index, target in enumerate(self.catalog.targets.values(), start=1)
            ],
        }

    def reinspection(self, observation: dict) -> dict:
        value = json.loads(json.dumps(observation))
        value["inspectionId"] = "inspect_TESTROUND02"
        value["observedAt"] = bridge.format_utc(self.now + dt.timedelta(seconds=1))
        return value

    def route(self, event: dict, classification: dict, poll_id: str, **kwargs):
        return self.store.route_native(
            event,
            classification,
            bridge_store=self.bridge_store,
            policy=self.policy,
            workspace_host=self.host,
            poll_id=poll_id,
            catalog=self.catalog,
            now=self.now,
            **kwargs,
        )

    def run_cli(
        self,
        argv: list[str],
        stdin_value: dict | None = None,
        *,
        clock=None,
    ):
        stdout = io.StringIO()
        stderr = io.StringIO()
        stdin = io.StringIO(json.dumps(stdin_value) if stdin_value is not None else "")
        with (
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            mock.patch.object(sys, "stdin", stdin),
            mock.patch.object(router, "utc_now", return_value=clock or self.now),
        ):
            code = router.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def cli_base(self) -> list[str]:
        return [
            "--runtime-root",
            str(self.store.root),
            "--bridge-runtime-root",
            str(self.bridge_store.root),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--allowed-workspace-host",
            self.host,
        ]

    def test_chat_is_bound_to_current_verified_self_row_and_persists_no_text_or_hash(self) -> None:
        secret_text = "聊聊今天的设计方向 PRIVATE-CANARY"
        event = self.event(secret_text)
        poll_id = self.commit_human_event(event)
        result = self.route(event, self.classification("chat"), poll_id)
        self.assertEqual(result.public["replyKind"], "chat")
        self.assertIsNone(result.request_text)
        ledger = self.store.event_path.read_text(encoding="utf-8")
        self.assertNotIn(secret_text, ledger)
        self.assertNotIn(bridge.text_fingerprint(secret_text)[0], ledger)
        self.assertEqual(self.store.key_path.stat().st_mode & 0o777, 0o600)

    def test_low_risk_action_claim_returns_only_private_fixed_envelope(self) -> None:
        raw = "继续 Mobile app version issue 现有的已允许工作"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action",
                target="mobile-app-version-issue",
                action="continue-allowlisted",
            ),
            poll_id,
            observation=observation,
        )
        self.assertTrue(routed.public["dispatchReady"])
        self.assertNotIn(raw, json.dumps(routed.public, ensure_ascii=False))
        self.assertEqual(routed.request_text, raw)
        self.store.acquire_round_lease("lease_TESTROUND01", now=self.now)
        reinspection = self.reinspection(observation)
        claimed = self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=reinspection,
            catalog=self.catalog,
            lease_id="lease_TESTROUND01",
            now=self.now + dt.timedelta(seconds=1),
        )
        self.assertTrue(claimed.public["claimed"])
        envelope = json.loads(claimed.request_text)
        self.assertEqual(
            envelope["provenance"]["kind"], router.FORWARD_PROVENANCE
        )
        self.assertEqual(
            envelope["controller"]["threadId"],
            "01a07200-0cde-7762-8831-4141fb9cd88b",
        )
        self.assertEqual(
            envelope["dispatchContract"]["mode"], "cursor-native-verified-composer"
        )
        self.assertFalse(
            envelope["dispatchContract"]["sendMessageToControllerThread"]
        )
        self.assertIn("control-plane-or-automation-edit", envelope["authority"]["neverAuthorized"])
        self.assertEqual(envelope["untrustedSlackRequest"], raw)
        for path in (self.store.event_path, self.store.intent_path, self.store.transition_path):
            self.assertNotIn(raw, path.read_text(encoding="utf-8"))

        duplicate = self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=reinspection,
            catalog=self.catalog,
            lease_id="lease_TESTROUND01",
            now=self.now + dt.timedelta(seconds=1),
        )
        self.assertFalse(duplicate.public["dispatchEnvelopeAvailable"])
        self.assertIsNone(duplicate.request_text)

    def test_claim_fails_closed_on_changed_state_catalog_or_ui(self) -> None:
        raw = "检查 Mobile app version issue"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action", target="mobile-app-version-issue", action="inspect-state"
            ),
            poll_id,
            observation=observation,
        )
        self.store.acquire_round_lease("lease_TESTROUND01", now=self.now)
        changed = self.reinspection(observation)
        changed["targets"][1]["stateVersion"] = "state_CHANGED01"
        with self.assertRaisesRegex(router.NaturalLanguageError, "task-state-changed"):
            self.store.claim_low_risk(
                routed.public["intentId"],
                request_text=raw,
                observation=changed,
                catalog=self.catalog,
                lease_id="lease_TESTROUND01",
                now=self.now + dt.timedelta(seconds=1),
            )

        unsafe = self.reinspection(observation)
        unsafe["targets"][1]["exactTitleMatchCount"] = 2
        with self.assertRaisesRegex(router.NaturalLanguageError, "target-ui-not-safe"):
            self.store.claim_low_risk(
                routed.public["intentId"],
                request_text=raw,
                observation=unsafe,
                catalog=self.catalog,
                lease_id="lease_TESTROUND01",
                now=self.now + dt.timedelta(seconds=1),
            )

    def test_ambiguous_target_asks_one_clarification_and_does_not_create_intent(self) -> None:
        event = self.event("继续处理那个任务")
        poll_id = self.commit_human_event(event)
        result = self.route(
            event,
            self.classification("action", action="continue-allowlisted"),
            poll_id,
            observation=self.observation(),
        )
        self.assertEqual(result.public["intent"], "clarification")
        self.assertEqual(result.public["clarificationCode"], "target-ambiguous")
        self.assertFalse(result.public["dispatchReady"])
        self.assertFalse(self.store.intent_path.exists())

    def test_high_risk_gets_private_token_but_native_confirmation_is_refused(self) -> None:
        request = self.event("把这个项目 push 出去")
        poll_id = self.commit_human_event(request)
        result = self.route(
            request,
            self.classification(
                "action", target="mobile-app-version-issue", action="push-deploy"
            ),
            poll_id,
            observation=self.observation(),
        )
        self.assertTrue(result.public["confirmationRequired"])
        self.assertRegex(result.confirmation_token, router.CONFIRM_TOKEN)
        ledger = self.store.intent_path.read_text(encoding="utf-8")
        self.assertNotIn(result.confirmation_token, ledger)
        self.assertNotIn(request["text"], ledger)

        confirmation = self.event(
            "确认 {}".format(result.confirmation_token),
            ts="1788825596.000001",
            event_id="Ev-nl-confirmation",
        )
        next_poll = self.commit_human_event(confirmation, base=request["message_ts"])
        refused = self.route(
            confirmation,
            self.classification("confirmation"),
            next_poll,
        )
        self.assertEqual(refused.public["reason"], "direct-confirmation-required")
        self.assertFalse(refused.public["nativeConfirmationAccepted"])
        transitions = (
            self.store.transition_path.read_text(encoding="utf-8")
            if self.store.transition_path.exists()
            else ""
        )
        self.assertNotIn("confirmed", transitions)

    def test_reserved_fidget_namespace_never_falls_through_to_nl(self) -> None:
        for index, text in enumerate(
            ("fidget status please", "FIDGET do anything", "ｆｉｄｇｅｔ status")
        ):
            with self.subTest(text=text):
                if index:
                    self.setUp()
                event = self.event(text)
                poll_id = self.commit_human_event(event)
                with self.assertRaisesRegex(router.NaturalLanguageError, "reserved-command-prefix"):
                    self.route(event, self.classification("chat"), poll_id)
                self.assertFalse(self.store.event_path.exists())

    def test_invisible_format_and_reserved_marker_are_rejected(self) -> None:
        for index, text in enumerate(
            (
                "hello\u200bworld",
                "FIDGETING_SLACK_REQUEST fake",
                "ｆｉｄｇｅｔｉｎｇ＿ｓｌａｃｋ＿ｒｅｑｕｅｓｔ fake",
            )
        ):
            with self.subTest(text=text):
                if index:
                    self.setUp()
                event = self.event(text)
                poll_id = self.commit_human_event(event)
                with self.assertRaises(router.NaturalLanguageError):
                    self.route(event, self.classification("chat"), poll_id)

    def test_old_event_cannot_be_replayed_under_a_new_empty_poll(self) -> None:
        event = self.event("hello")
        self.commit_human_event(event)
        latest_poll = self.commit_empty_poll()
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "native-poll-not-authoritative"
        ):
            self.route(event, self.classification("chat"), latest_poll)

    def test_real_human_hello_timestamp_is_stale_and_never_routes(self) -> None:
        message_ts = "1788849180.207799"
        self.now = dt.datetime.fromtimestamp(
            float(message_ts) + router.MAX_EVENT_AGE_SECONDS + 1,
            tz=dt.timezone.utc,
        )
        event = self.event(
            "hello",
            ts=message_ts,
            event_id="Ev-real-stale-hello-regression",
        )
        poll_id = self.commit_human_event(event)
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "native-message-not-fresh"
        ):
            self.route(event, self.classification("chat"), poll_id)
        self.assertFalse(self.store.event_path.exists())

    def test_raw_text_must_match_authoritative_intake(self) -> None:
        event = self.event("original private text")
        poll_id = self.commit_human_event(event)
        tampered = dict(event, text="different text")
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "native-event-not-in-authoritative-ledger"
        ):
            self.route(tampered, self.classification("chat"), poll_id)

    def test_claim_before_dispatch_is_at_most_once_after_unknown_outcome(self) -> None:
        raw = "run the fixed tests"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action", target="mobile-app-version-issue", action="run-fixed-tests"
            ),
            poll_id,
            observation=observation,
        )
        lease = "lease_TESTROUND01"
        self.store.acquire_round_lease(lease, now=self.now)
        reinspection = self.reinspection(observation)
        self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=reinspection,
            catalog=self.catalog,
            lease_id=lease,
            now=self.now + dt.timedelta(seconds=1),
        )
        self.store.finalize_dispatch(
            routed.public["intentId"], lease, "unknown", now=self.now + dt.timedelta(seconds=1)
        )
        replay = self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=reinspection,
            catalog=self.catalog,
            lease_id=lease,
            now=self.now + dt.timedelta(seconds=1),
        )
        self.assertFalse(replay.public["dispatchEnvelopeAvailable"])

    def test_crash_orphan_never_mints_or_claims_a_second_intent(self) -> None:
        raw = "检查 Mobile app version issue"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        original_append = self.store._append

        def crash_before_event(path, record):
            if path == self.store.event_path:
                raise OSError("synthetic crash")
            return original_append(path, record)

        with mock.patch.object(self.store, "_append", side_effect=crash_before_event):
            with self.assertRaises(OSError):
                self.route(
                    event,
                    self.classification(
                        "action", target="mobile-app-version-issue", action="inspect-state"
                    ),
                    poll_id,
                    observation=observation,
                )
        intents = [
            json.loads(line)
            for line in self.store.intent_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(len(intents), 1)
        recovered = self.route(
            event,
            self.classification(
                "action", target="mobile-app-version-issue", action="inspect-state"
            ),
            poll_id,
            observation=observation,
        )
        self.assertEqual(recovered.public["reason"], "prior-route-incomplete-resend")
        self.assertEqual(
            len(self.store.intent_path.read_text(encoding="utf-8").splitlines()), 1
        )
        self.store.acquire_round_lease("lease_TESTROUND01", now=self.now)
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "intent-source-event-not-dispatchable"
        ):
            self.store.claim_low_risk(
                intents[0]["intentId"],
                request_text=raw,
                observation=self.reinspection(observation),
                catalog=self.catalog,
                lease_id="lease_TESTROUND01",
                now=self.now + dt.timedelta(seconds=1),
            )

    def test_orphan_retry_with_changed_classification_is_refused_without_mutation(self) -> None:
        raw = "检查 Mobile app version issue"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        original_append = self.store._append

        def crash_before_event(path, record):
            if path == self.store.event_path:
                raise OSError("synthetic crash")
            return original_append(path, record)

        with mock.patch.object(self.store, "_append", side_effect=crash_before_event):
            with self.assertRaises(OSError):
                self.route(
                    event,
                    self.classification(
                        "action", target="mobile-app-version-issue", action="inspect-state"
                    ),
                    poll_id,
                    observation=observation,
                )

        original_intent = self.store.intent_path.read_text(encoding="utf-8")
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "prior-route-binding-mismatch"
        ):
            self.route(event, self.classification("chat"), poll_id)
        self.assertFalse(self.store.event_path.exists())
        self.assertEqual(
            self.store.intent_path.read_text(encoding="utf-8"), original_intent
        )

        recovered = self.route(
            event,
            self.classification(
                "action", target="mobile-app-version-issue", action="inspect-state"
            ),
            poll_id,
            observation=observation,
        )
        self.assertEqual(recovered.public["reason"], "prior-route-incomplete-resend")

    def test_cancel_retry_after_event_append_crash_is_idempotent(self) -> None:
        action = self.event("检查 Mobile app version issue")
        action_poll = self.commit_human_event(action)
        routed = self.route(
            action,
            self.classification(
                "action", target="mobile-app-version-issue", action="inspect-state"
            ),
            action_poll,
            observation=self.observation(),
        )
        cancel = self.event(
            "取消 {}".format(routed.public["intentId"]),
            ts="1788825596.000001",
            event_id="Ev-nl-cancel-crash",
        )
        cancel_poll = self.commit_human_event(cancel, base=action["message_ts"])
        original_append = self.store._append

        def crash_after_cancel_transition(path, record):
            if path == self.store.event_path:
                raise OSError("synthetic crash")
            return original_append(path, record)

        with mock.patch.object(
            self.store, "_append", side_effect=crash_after_cancel_transition
        ):
            with self.assertRaises(OSError):
                self.route(
                    cancel,
                    self.classification("cancel"),
                    cancel_poll,
                )

        recovered = self.route(
            cancel,
            self.classification("cancel"),
            cancel_poll,
        )
        self.assertEqual(recovered.public["reason"], "cancelled")
        transitions = [
            json.loads(line)
            for line in self.store.transition_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [record["outcome"] for record in transitions if record["intentId"] == routed.public["intentId"]],
            ["cancelled"],
        )
        self.store.acquire_round_lease("lease_CANCELCHECK01", now=self.now)

    def test_corrupt_authoritative_nl_ledger_fails_closed(self) -> None:
        self.store.root.mkdir(parents=True)
        self.store.event_path.write_text("{truncated", encoding="utf-8")
        with self.assertRaisesRegex(router.NaturalLanguageError, "invalid-nl-event-ledger"):
            self.store.acquire_round_lease("lease_TESTROUND01", now=self.now)

    def test_static_catalog_contains_only_authorized_scope(self) -> None:
        self.assertEqual(
            set(self.catalog.targets),
            {
                "card-draw-scene-research",
                "mobile-app-version-issue",
                "conversation-freezing-issue",
            },
        )
        self.assertEqual(
            self.catalog.controller["threadId"],
            "01a07200-0cde-7762-8831-4141fb9cd88b",
        )

    def test_cli_dry_run_is_redacted_and_has_no_nl_runtime_side_effect(self) -> None:
        raw = "PRIVATE-CLI-CHAT-CANARY"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        code, stdout, stderr = self.run_cli(
            self.cli_base()
            + ["route", "--poll-id", poll_id, "--dry-run"],
            {
                "schemaVersion": "1.0",
                "event": event,
                "classification": self.classification("chat"),
                "observation": None,
            },
        )
        self.assertEqual(code, 0, stderr)
        self.assertTrue(json.loads(stdout)["dryRun"])
        self.assertNotIn(raw, stdout + stderr)
        self.assertFalse(self.store.root.exists())

    def test_cli_route_claim_finalize_uses_protected_files_without_execution(self) -> None:
        raw = "继续 Mobile app version issue 已允许的工作 PRIVATE-CLI-CANARY"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        first_observation = self.observation()
        code, stdout, stderr = self.run_cli(
            self.cli_base()
            + ["route", "--poll-id", poll_id],
            {
                "schemaVersion": "1.0",
                "event": event,
                "classification": self.classification(
                    "action",
                    target="mobile-app-version-issue",
                    action="continue-allowlisted",
                ),
                "observation": first_observation,
            },
        )
        self.assertEqual(code, 0, stderr)
        route_result = json.loads(stdout)
        self.assertNotIn(raw, stdout + stderr)
        ticket = Path(route_result["privateArtifact"])
        self.assertTrue(ticket.is_file())
        self.assertEqual(ticket.stat().st_mode & 0o777, 0o600)

        lease = "lease_TESTROUND01"
        code, _, stderr = self.run_cli(
            self.cli_base()
            + ["lease-acquire", "--lease-id", lease]
        )
        self.assertEqual(code, 0, stderr)
        second_observation = self.reinspection(first_observation)
        code, stdout, stderr = self.run_cli(
            self.cli_base()
            + [
                "claim",
                "--intent-id",
                route_result["intentId"],
                "--lease-id",
                lease,
            ],
            second_observation,
            clock=self.now + dt.timedelta(seconds=1),
        )
        self.assertEqual(code, 0, stderr)
        claim_result = json.loads(stdout)
        self.assertNotIn(raw, stdout + stderr)
        envelope = Path(claim_result["privateArtifact"])
        self.assertFalse(ticket.exists())
        self.assertTrue(envelope.is_file())
        self.assertEqual(envelope.stat().st_mode & 0o777, 0o600)
        protected = envelope.read_text(encoding="utf-8")
        self.assertNotIn(raw, protected)
        self.assertIn("FIDGETING_SLACK_REQUEST_V1", protected)

        code, stdout, stderr = self.run_cli(
            self.cli_base()
            + [
                "finalize",
                "--intent-id",
                route_result["intentId"],
                "--lease-id",
                lease,
                "--outcome",
                "unknown",
            ],
            clock=self.now + dt.timedelta(seconds=1),
        )
        self.assertEqual(code, 0, stderr)
        self.assertEqual(json.loads(stdout)["outcome"], "unknown")
        self.assertFalse(envelope.exists())

    def test_codex_target_executes_in_current_turn_without_self_message_routing(self) -> None:
        raw = "在 Codex 当前轮检查现状"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action",
                target="mobile-app-version-issue",
                action="inspect-state",
                recipient="codex",
            ),
            poll_id,
            observation=observation,
        )
        lease = "lease_TESTROUND01"
        self.store.acquire_round_lease(lease, now=self.now)
        claimed = self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=self.reinspection(observation),
            catalog=self.catalog,
            lease_id=lease,
            now=self.now + dt.timedelta(seconds=1),
        )
        envelope = json.loads(claimed.request_text)
        self.assertEqual(envelope["target"]["backend"], "codex-current-turn")
        self.assertEqual(
            envelope["target"]["threadId"], self.catalog.controller["threadId"]
        )
        self.assertEqual(
            envelope["dispatchContract"]["mode"], "execute-in-current-heartbeat-turn"
        )
        self.assertFalse(envelope["dispatchContract"]["sendMessageToControllerThread"])
        self.assertEqual(envelope["dispatchContract"]["cursorChecks"], [])

    def test_codex_actions_without_a_fixed_executor_are_refused(self) -> None:
        for index, action in enumerate(
            ("continue-allowlisted", "run-fixed-tests"), start=1
        ):
            with self.subTest(action=action):
                self.setUp()
                event = self.event(
                    "Codex action {}".format(action),
                    event_id="Ev-codex-refused-{}".format(index),
                )
                poll_id = self.commit_human_event(event)
                routed = self.route(
                    event,
                    self.classification(
                        "action",
                        target="mobile-app-version-issue",
                        action=action,
                        recipient="codex",
                    ),
                    poll_id,
                    observation=self.observation(),
                )
                self.assertEqual(
                    routed.public["reason"], "recipient-action-not-allowed"
                )
                self.assertFalse(routed.public["dispatchReady"])
                self.assertFalse(self.store.intent_path.exists())

    def test_stale_ticket_is_refused_and_removed_without_replay(self) -> None:
        raw = "检查 Mobile app version issue"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action", target="mobile-app-version-issue", action="inspect-state"
            ),
            poll_id,
            observation=observation,
        )
        ticket = self.store.persist_route_private_material(routed, now=self.now)
        self.assertTrue(ticket.is_file())
        swept = self.store.sweep_private_artifacts(
            now=self.now + dt.timedelta(seconds=61)
        )
        self.assertEqual(swept["removedCount"], 1)
        self.assertFalse(ticket.exists())
        transitions = [
            json.loads(line)
            for line in self.store.transition_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(transitions[-1]["outcome"], "refused")
        self.store.acquire_round_lease(
            "lease_TESTROUND01", now=self.now + dt.timedelta(seconds=61)
        )
        duplicate = self.store.claim_low_risk(
            routed.public["intentId"],
            request_text=raw,
            observation=self.reinspection(observation),
            catalog=self.catalog,
            lease_id="lease_TESTROUND01",
            now=self.now + dt.timedelta(seconds=61),
        )
        self.assertFalse(duplicate.public["dispatchEnvelopeAvailable"])

    def test_stale_claimed_envelope_is_marked_unknown_before_removal(self) -> None:
        raw = "继续 Mobile app version issue 已允许的工作"
        event = self.event(raw)
        poll_id = self.commit_human_event(event)
        observation = self.observation()
        routed = self.route(
            event,
            self.classification(
                "action",
                target="mobile-app-version-issue",
                action="continue-allowlisted",
            ),
            poll_id,
            observation=observation,
        )
        self.store.persist_route_private_material(routed, now=self.now)
        lease = "lease_TESTROUND01"
        self.store.acquire_round_lease(lease, now=self.now)
        _, envelope = self.store.claim_from_private_ticket(
            routed.public["intentId"],
            observation=self.reinspection(observation),
            catalog=self.catalog,
            lease_id=lease,
            now=self.now + dt.timedelta(seconds=1),
        )
        self.assertTrue(envelope.is_file())
        swept = self.store.sweep_private_artifacts(
            now=self.now + dt.timedelta(seconds=122)
        )
        self.assertEqual(swept["removedCount"], 1)
        self.assertFalse(envelope.exists())
        transitions = [
            json.loads(line)
            for line in self.store.transition_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [record["outcome"] for record in transitions], ["claimed", "unknown"]
        )

    def test_private_artifact_sweep_never_follows_symlinks(self) -> None:
        self.store._prepare_transient()
        outside = Path(self.temporary.name) / "outside-canary"
        outside.write_text("do not delete", encoding="utf-8")
        malicious = self.store.transient_root / "intent_ABCDEF123456.ticket.json"
        malicious.symlink_to(outside)
        with self.assertRaisesRegex(
            router.NaturalLanguageError, "invalid-private-artifact-entry"
        ):
            self.store.sweep_private_artifacts(now=self.now)
        self.assertEqual(outside.read_text(encoding="utf-8"), "do not delete")


if __name__ == "__main__":
    unittest.main()
