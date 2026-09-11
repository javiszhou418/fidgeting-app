from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"
CUA_PATH = REPO_ROOT / ".cursor/hooks/slack_command_cua_ingest.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures/slack_cua_batches.json"

BRIDGE_SPEC = importlib.util.spec_from_file_location("slack_command_bridge", BRIDGE_PATH)
assert BRIDGE_SPEC and BRIDGE_SPEC.loader
bridge = importlib.util.module_from_spec(BRIDGE_SPEC)
sys.modules[BRIDGE_SPEC.name] = bridge
BRIDGE_SPEC.loader.exec_module(bridge)

CUA_SPEC = importlib.util.spec_from_file_location("slack_command_cua_ingest", CUA_PATH)
assert CUA_SPEC and CUA_SPEC.loader
cua_ingest = importlib.util.module_from_spec(CUA_SPEC)
sys.modules[CUA_SPEC.name] = cua_ingest
CUA_SPEC.loader.exec_module(cua_ingest)


class NativeSlackCuaIngestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        config = self.fixture["policy"]
        self.policy = bridge.CommandPolicy(
            config["team_id"], config["user_id"], config["conversation_id"]
        )
        self.workspace_host = "jw-qgi5008.slack.com"
        self.now = bridge.parse_utc(self.fixture["now"])
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.runtime_root = Path(self.temporary.name) / "runtime"
        self.store = bridge.AppendOnlyCommandStore(self.runtime_root)

    def batch(self, name: str) -> dict:
        return json.loads(json.dumps(self.fixture["batches"][name]))

    def validate(self, batch: dict):
        return cua_ingest.validate_batch(
            batch, self.policy, self.workspace_host, now=self.now
        )

    def commit(self, name: str, store=None):
        base, next_cursor, rows, poll_id, decisions = self.validate(self.batch(name))
        target = store or self.store
        if not target.source_cursor_ledger_path.exists():
            assert base is not None
            target.bootstrap_source_cursor(
                bridge.SLACK_NATIVE_CUA_SOURCE,
                self.policy,
                base,
                now=self.now,
            )
        return target.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=next_cursor,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )

    @staticmethod
    def json_lines(path: Path) -> list[dict]:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_exact_allowlisted_batch_commits_events_then_cursor(self) -> None:
        result = self.commit("first")
        self.assertTrue(result["committed"])
        self.assertFalse(result["duplicateBatch"])
        self.assertEqual(result["acceptedCount"], 2)
        self.assertEqual(result["sourceCursor"], "1788825595.000002")
        self.assertEqual(len(self.json_lines(self.store.queue_path)), 2)
        self.assertEqual(len(self.json_lines(self.store.source_cursor_ledger_path)), 2)
        self.assertEqual(len(self.json_lines(self.store.source_poll_ledger_path)), 1)

        cursor = self.store.source_cursor(bridge.SLACK_NATIVE_CUA_SOURCE, self.policy)
        self.assertEqual(cursor["teamId"], "T0C00P256DA")
        self.assertEqual(cursor["userId"], "U0BV4S23X8B")
        self.assertEqual(cursor["conversationId"], "D0C0RELGU56")
        self.assertEqual(cursor["cursor"], result["sourceCursor"])
        self.assertEqual(cursor["observedThrough"], result["sourceCursor"])
        self.assertEqual(self.store.source_cursor_path.stat().st_mode & 0o777, 0o600)
        native_poll = self.store.snapshot(now=self.now)["nativePoll"]
        self.assertEqual(native_poll["pollId"], "poll_FIRST0001")
        self.assertEqual(native_poll["observedThrough"], result["sourceCursor"])
        self.assertTrue(native_poll["cursorConsistent"])

    def test_observe_only_bootstrap_is_explicit_atomic_and_idempotent(self) -> None:
        cursor = self.batch("first")["baseObservedThrough"]
        result = self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, cursor, now=self.now
        )
        self.assertTrue(result["bootstrapped"])
        self.assertFalse(result["duplicate"])
        self.assertEqual(result["activationCutoff"], cursor)
        self.assertFalse(self.store.queue_path.exists())
        self.assertFalse(self.store.audit_path.exists())

        records = self.json_lines(self.store.source_cursor_ledger_path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["recordType"], "source-bootstrap")
        self.assertEqual(records[0]["eventCount"], 0)
        self.assertEqual(records[0]["cursor"], cursor)
        self.assertEqual(records[0]["activationCutoff"], cursor)
        self.assertTrue(self.store.source_cursor_path.exists())

        retry = self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, cursor, now=self.now
        )
        self.assertTrue(retry["duplicate"])
        self.assertEqual(len(self.json_lines(self.store.source_cursor_ledger_path)), 1)
        with self.assertRaisesRegex(bridge.StoreError, "source-already-bootstrapped"):
            self.store.bootstrap_source_cursor(
                bridge.SLACK_NATIVE_CUA_SOURCE,
                self.policy,
                "1788825581.000000",
                now=self.now,
            )

    def test_bootstrap_cli_requires_proof_and_never_ingests_history(self) -> None:
        cursor = self.batch("first")["baseObservedThrough"]
        base_args = [
            sys.executable,
            str(CUA_PATH),
            "--runtime-root",
            str(self.runtime_root),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--allowed-workspace-host",
            self.workspace_host,
            "--now",
            self.fixture["now"],
            "bootstrap",
            "--cursor",
            cursor,
            "--author-proof",
        ]
        denied = subprocess.run(
            base_args + ["display-name-only"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(denied.returncode, 2)
        self.assertIn("unverified-self-dm-author", denied.stderr)
        self.assertFalse(self.runtime_root.exists())

        accepted = subprocess.run(
            base_args + [cua_ingest.AUTHOR_PROOF],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        result = json.loads(accepted.stdout)
        self.assertTrue(result["bootstrapped"])
        self.assertEqual(result["activationCutoff"], cursor)
        self.assertFalse(self.store.queue_path.exists())
        self.assertFalse(self.store.audit_path.exists())

    def test_ingest_refuses_unbootstrapped_source(self) -> None:
        base, next_cursor, rows, poll_id, decisions = self.validate(self.batch("first"))
        with self.assertRaisesRegex(bridge.StoreError, "source-not-bootstrapped"):
            self.store.ingest_source_batch(
                decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                next_cursor=next_cursor,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )
        self.assertFalse(self.store.queue_path.exists())
        self.assertFalse(self.store.source_cursor_ledger_path.exists())

    def test_store_independently_enforces_event_cursor_range(self) -> None:
        batch = self.batch("first")
        base, next_cursor, rows, poll_id, decisions = self.validate(batch)
        assert base is not None
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        outside = bridge.replace(decisions[0], message_ts=base)
        with self.assertRaisesRegex(
            bridge.StoreError, "events-do-not-cover-self-message-rows"
        ):
            self.store.ingest_source_batch(
                [outside, decisions[1]],
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                next_cursor=next_cursor,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )
        self.assertFalse(self.store.queue_path.exists())

    def test_dry_run_validates_without_network_or_runtime_files(self) -> None:
        args = [
            sys.executable,
            str(CUA_PATH),
            "--runtime-root",
            str(self.runtime_root),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--allowed-workspace-host",
            self.workspace_host,
            "--now",
            self.fixture["now"],
            "ingest",
            "--dry-run",
        ]
        completed = subprocess.run(
            args,
            input=json.dumps(self.batch("first")),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertTrue(result["dryRun"])
        self.assertEqual(result["acceptedCount"], 2)
        self.assertFalse(self.runtime_root.exists())
        self.assertNotIn("fidget status", completed.stdout)

    def test_stale_command_is_rejected_but_well_formed_cursor_commits(self) -> None:
        result = self.commit("stale")
        self.assertTrue(result["committed"])
        self.assertEqual(result["acceptedCount"], 0)
        self.assertEqual(result["rejectedCount"], 1)
        self.assertEqual(result["eventResults"][0]["reason"], "stale-message")
        self.assertFalse(self.store.queue_path.exists())
        self.assertEqual(
            self.store.source_cursor(bridge.SLACK_NATIVE_CUA_SOURCE, self.policy)["cursor"],
            "1788824699.000001",
        )

    def test_native_pause_just_over_five_minutes_still_applies_but_resume_expires(self) -> None:
        message_ts = "{:.6f}".format(self.now.timestamp() - 301)
        base_ts = "{:.6f}".format(self.now.timestamp() - 302)
        pause = self.batch("first")
        pause["baseObservedThrough"] = base_ts
        pause["observedThrough"] = message_ts
        pause["pollProof"]["pollId"] = "poll_LATEPAUSE1"
        pause["rows"] = [
            {
                "message_ts": message_ts,
                "kind": "self-message",
                "permalink": "https://jw-qgi5008.slack.com/archives/{}/p{}".format(
                    self.policy.conversation_id, message_ts.replace(".", "")
                ),
            }
        ]
        pause["events"] = [
            {
                "schemaVersion": "1.0",
                "team_id": self.policy.team_id,
                "user_id": self.policy.user_id,
                "conversation_id": self.policy.conversation_id,
                "event_id": "Ev-cua-late-pause-001",
                "message_ts": message_ts,
                "text": "fidget pause",
            }
        ]
        base, observed, rows, poll_id, decisions = self.validate(pause)
        self.assertTrue(decisions[0].accepted)
        self.assertEqual(decisions[0].command, "pause")
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        result = self.store.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=observed,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )
        self.assertEqual(result["acceptedCount"], 1)
        self.assertTrue(self.store.snapshot(now=self.now)["paused"])

        resume = json.loads(json.dumps(pause))
        resume["events"][0]["text"] = "fidget resume"
        resume["events"][0]["event_id"] = "Ev-cua-late-resume-001"
        resume["pollProof"]["pollId"] = "poll_LATERESUM1"
        _, _, _, _, resume_decisions = self.validate(resume)
        self.assertFalse(resume_decisions[0].accepted)
        self.assertEqual(resume_decisions[0].reason, "stale-message")

    def test_app_row_advances_observed_through_without_becoming_an_event(self) -> None:
        batch = self.batch("first")
        batch["rows"][0]["kind"] = "app-message"
        batch["events"] = [batch["events"][1]]
        base, observed, rows, poll_id, decisions = self.validate(batch)
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        result = self.store.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=observed,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )
        self.assertEqual(result["acceptedCount"], 1)
        self.assertEqual(result["observedThrough"], batch["rows"][-1]["message_ts"])
        receipt = self.json_lines(self.store.source_poll_ledger_path)[0]
        self.assertEqual(receipt["observedRowCount"], 2)
        self.assertEqual(receipt["eventCount"], 1)

    def grouped_app_batch(self) -> dict:
        batch = self.batch("first")
        batch["rows"][0]["kind"] = "app-message"
        batch["rows"][1]["kind"] = bridge.GROUPED_APP_CONTINUATION_KIND
        batch["events"] = []
        batch["pollProof"]["pollId"] = "poll_GROUPAPP01"
        return batch

    def test_grouped_app_continuation_advances_only_after_direct_app_anchor(self) -> None:
        batch = self.grouped_app_batch()
        base, observed, rows, poll_id, decisions = self.validate(batch)
        self.assertEqual(decisions, [])
        self.assertEqual(
            [row.kind for row in rows],
            ["app-message", bridge.GROUPED_APP_CONTINUATION_KIND],
        )
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        result = self.store.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=observed,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )
        self.assertEqual(result["acceptedCount"], 0)
        self.assertEqual(result["observedThrough"], batch["rows"][-1]["message_ts"])
        self.assertFalse(self.store.queue_path.exists())
        self.assertFalse(self.store.audit_path.exists())

    def test_observed_real_grouped_sequence_shape_validates_without_app_body(self) -> None:
        batch = self.grouped_app_batch()
        timestamps = (
            "1788843615.194199",
            "1788845164.898959",
            "1788845440.539029",
        )
        batch["baseObservedThrough"] = "1788842939.837369"
        batch["observedThrough"] = timestamps[-1]
        batch["rows"] = [
            {
                "message_ts": message_ts,
                "kind": (
                    bridge.GROUPED_APP_CONTINUATION_KIND
                    if index == len(timestamps) - 1
                    else "app-message"
                ),
                "permalink": "https://{}/archives/{}/p{}".format(
                    self.workspace_host,
                    self.policy.conversation_id,
                    message_ts.replace(".", ""),
                ),
            }
            for index, message_ts in enumerate(timestamps)
        ]
        observed_at = dt.datetime.fromtimestamp(
            float(timestamps[-1]) + 1, tz=dt.timezone.utc
        )
        _, observed, rows, _, decisions = cua_ingest.validate_batch(
            batch, self.policy, self.workspace_host, now=observed_at
        )
        self.assertEqual(observed, timestamps[-1])
        self.assertEqual(decisions, [])
        self.assertEqual(rows[-1].kind, bridge.GROUPED_APP_CONTINUATION_KIND)
        self.assertTrue(all(not hasattr(row, "text") for row in rows))

    def test_grouped_app_continuation_rejects_missing_or_non_app_anchor(self) -> None:
        continuation_first = self.grouped_app_batch()
        continuation_first["rows"] = [continuation_first["rows"][1]]
        continuation_first["baseObservedThrough"] = "1788825590.000001"

        after_self = self.grouped_app_batch()
        after_self["rows"][0]["kind"] = "self-message"
        after_self["events"] = [self.batch("first")["events"][0]]

        continuation_chain = self.grouped_app_batch()
        chained_ts = "1788825596.000003"
        continuation_chain["rows"].append(
            {
                "message_ts": chained_ts,
                "kind": bridge.GROUPED_APP_CONTINUATION_KIND,
                "permalink": "https://{}/archives/{}/p{}".format(
                    self.workspace_host,
                    self.policy.conversation_id,
                    chained_ts.replace(".", ""),
                ),
            }
        )
        continuation_chain["observedThrough"] = chained_ts

        for batch in (continuation_first, after_self, continuation_chain):
            with self.subTest(rows=batch["rows"]):
                with self.assertRaisesRegex(
                    bridge.BridgeError, "unanchored-app-group-continuation"
                ):
                    self.validate(batch)

    def test_grouped_app_continuation_cannot_carry_an_event(self) -> None:
        batch = self.grouped_app_batch()
        event = self.batch("first")["events"][1]
        batch["events"] = [event]
        with self.assertRaisesRegex(
            bridge.BridgeError, "events-do-not-cover-self-message-rows"
        ):
            self.validate(batch)

    def test_store_rejects_unanchored_group_continuation_without_mutation(self) -> None:
        batch = self.grouped_app_batch()
        base = batch["baseObservedThrough"]
        continuation = batch["rows"][1]
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        before = self.store.source_cursor_ledger_path.read_bytes()
        with self.assertRaisesRegex(
            bridge.StoreError, "unanchored-app-group-continuation"
        ):
            self.store.ingest_source_batch(
                [],
                source=bridge.SLACK_NATIVE_CUA_SOURCE,
                policy=self.policy,
                workspace_host=self.workspace_host,
                base_cursor=base,
                next_cursor=continuation["message_ts"],
                observed_rows=[
                    bridge.SourceObservationRow(
                        continuation["message_ts"],
                        continuation["kind"],
                        continuation["permalink"],
                    )
                ],
                poll_id="poll_BYPASS001",
                now=self.now,
            )
        self.assertEqual(self.store.source_cursor_ledger_path.read_bytes(), before)
        self.assertFalse(self.store.source_poll_ledger_path.exists())
        self.assertFalse(self.store.queue_path.exists())
        self.assertFalse(self.store.audit_path.exists())

    def test_grouped_kind_is_digest_bound_on_same_poll_retry(self) -> None:
        batch = self.grouped_app_batch()
        base, observed, rows, poll_id, decisions = self.validate(batch)
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        self.store.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=observed,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )

        changed = self.grouped_app_batch()
        changed["rows"][1]["kind"] = "app-message"
        base, observed, rows, poll_id, decisions = self.validate(changed)
        with self.assertRaisesRegex(bridge.StoreError, "source-poll-id-conflict"):
            self.store.ingest_source_batch(
                decisions,
                source=bridge.SLACK_NATIVE_CUA_SOURCE,
                policy=self.policy,
                workspace_host=self.workspace_host,
                base_cursor=base,
                next_cursor=observed,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )

    def test_failed_poll_is_append_only_and_supersedes_prior_success(self) -> None:
        first = self.commit("first")
        failed = self.store.record_source_poll_failure(
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            poll_id="poll_FAILED001",
            base_observed_through=first["observedThrough"],
            reason="chronology-ambiguous",
            now=self.now,
        )
        self.assertTrue(failed["recorded"])
        snapshot = self.store.snapshot(now=self.now)
        self.assertEqual(snapshot["nativePoll"]["outcome"], "failed")
        self.assertIsNone(snapshot["nativePoll"]["verifiedPollAt"])
        self.assertEqual(len(self.json_lines(self.store.source_poll_ledger_path)), 2)

    def test_native_cua_transport_rejects_approve_safe_in_code(self) -> None:
        self.commit("first")
        result = self.commit("second")
        self.assertTrue(result["committed"])
        self.assertEqual(result["acceptedCount"], 0)
        self.assertEqual(result["rejectedCount"], 1)
        self.assertEqual(
            result["eventResults"][0]["reason"],
            "command-not-allowed-for-native-cua",
        )
        self.assertEqual(self.store.snapshot(now=self.now)["pendingApproveSafeCount"], 0)

        # Defense in depth: bypassing the adapter cannot re-enable approval on
        # a store operation explicitly labelled as native CUA.
        direct_store = bridge.AppendOnlyCommandStore(
            Path(self.temporary.name) / "direct-native-store"
        )
        direct_batch = self.batch("second")
        direct_store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE,
            self.policy,
            direct_batch["baseObservedThrough"],
            now=self.now,
        )
        direct_decision = bridge.evaluate_event(
            direct_batch["events"][0], self.policy, now=self.now
        )
        self.assertTrue(direct_decision.accepted)
        direct_result = direct_store.ingest_source_batch(
            [direct_decision],
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=direct_batch["baseObservedThrough"],
            next_cursor=direct_batch["observedThrough"],
            observed_rows=[
                bridge.SourceObservationRow(
                    row["message_ts"], row["kind"], row["permalink"]
                )
                for row in direct_batch["rows"]
            ],
            poll_id=direct_batch["pollProof"]["pollId"],
            now=self.now,
        )
        self.assertEqual(direct_result["acceptedCount"], 0)
        self.assertEqual(
            direct_result["eventResults"][0]["reason"],
            "command-not-allowed-for-native-cua",
        )
        self.assertFalse(direct_store.queue_path.exists())

    def test_same_batch_retry_is_idempotent_and_digest_conflict_fails_closed(self) -> None:
        first = self.commit("first")
        queue_before = self.store.queue_path.read_bytes()
        retry = self.commit("first")
        self.assertTrue(retry["duplicateBatch"])
        self.assertEqual(retry["batchDigest"], first["batchDigest"])
        self.assertEqual(self.store.queue_path.read_bytes(), queue_before)
        self.assertEqual(len(self.json_lines(self.store.source_cursor_ledger_path)), 2)

        changed = self.batch("first")
        changed["events"][0]["text"] = "fidget resume"
        base, next_cursor, rows, poll_id, decisions = self.validate(changed)
        with self.assertRaisesRegex(bridge.StoreError, "source-poll-id-conflict"):
            self.store.ingest_source_batch(
                decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                next_cursor=next_cursor,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )

    def test_conflicting_poll_id_cannot_partially_append_resume_or_cursor(self) -> None:
        self.commit("first")
        self.assertTrue(self.store.snapshot(now=self.now)["paused"])
        conflicting = self.batch("second")
        conflicting["pollProof"]["pollId"] = "poll_FIRST0001"
        conflicting["events"][0]["event_id"] = "Ev-cua-resume-conflict-001"
        conflicting["events"][0]["text"] = "fidget resume"
        base, observed, rows, poll_id, decisions = self.validate(conflicting)
        paths = (
            self.store.queue_path,
            self.store.audit_path,
            self.store.source_cursor_ledger_path,
            self.store.source_poll_ledger_path,
            self.store.state_path,
        )
        before = {path: path.read_bytes() for path in paths}
        with self.assertRaisesRegex(bridge.StoreError, "source-poll-id-conflict"):
            self.store.ingest_source_batch(
                decisions,
                source=bridge.SLACK_NATIVE_CUA_SOURCE,
                policy=self.policy,
                workspace_host=self.workspace_host,
                base_cursor=base,
                next_cursor=observed,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )
        self.assertEqual(before, {path: path.read_bytes() for path in paths})
        self.assertTrue(self.store.snapshot(now=self.now)["paused"])
        self.assertEqual(
            self.store.source_cursor(bridge.SLACK_NATIVE_CUA_SOURCE, self.policy)[
                "cursor"
            ],
            base,
        )

    def test_cursor_conflict_event_collision_and_rewind_do_not_advance(self) -> None:
        self.commit("first")
        second = self.batch("second")

        wrong_base = json.loads(json.dumps(second))
        wrong_base["baseObservedThrough"] = "1788825590.000001"
        base, next_cursor, rows, poll_id, decisions = self.validate(wrong_base)
        with self.assertRaisesRegex(bridge.StoreError, "source-cursor-conflict"):
            self.store.ingest_source_batch(
                decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                next_cursor=next_cursor,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )

        collision = json.loads(json.dumps(second))
        collision["events"][0]["event_id"] = "Ev-cua-status-001"
        base, next_cursor, rows, poll_id, decisions = self.validate(collision)
        with self.assertRaisesRegex(bridge.StoreError, "event-id-collision"):
            self.store.ingest_source_batch(
                decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                next_cursor=next_cursor,
                observed_rows=rows,
                poll_id=poll_id,
                now=self.now,
            )

        self.assertEqual(
            self.store.source_cursor(bridge.SLACK_NATIVE_CUA_SOURCE, self.policy)["cursor"],
            "1788825595.000002",
        )

    def test_crash_after_cursor_ledger_append_recovers_without_replay(self) -> None:
        batch = self.batch("first")
        base, next_cursor, rows, poll_id, decisions = self.validate(batch)
        assert base is not None
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        original_atomic_write = self.store._atomic_write

        def fail_cursor_cache(path, value):
            if path == self.store.source_cursor_path:
                raise OSError("synthetic crash")
            return original_atomic_write(path, value)

        with mock.patch.object(self.store, "_atomic_write", side_effect=fail_cursor_cache):
            with self.assertRaisesRegex(OSError, "synthetic crash"):
                self.store.ingest_source_batch(
                    decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
                    next_cursor=next_cursor,
                    observed_rows=rows,
                    poll_id=poll_id,
                    now=self.now,
                )

        recovered = bridge.AppendOnlyCommandStore(self.runtime_root)
        result = recovered.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=next_cursor,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )
        self.assertTrue(result["duplicateBatch"])
        self.assertEqual(len(self.json_lines(recovered.queue_path)), 2)
        self.assertEqual(len(self.json_lines(recovered.source_cursor_ledger_path)), 2)
        self.assertTrue(recovered.source_cursor_path.exists())
        self.assertTrue(recovered.state_path.exists())

    def test_malformed_or_unproven_native_source_never_creates_state(self) -> None:
        variants = []

        no_proof = self.batch("first")
        del no_proof["source"]["authorProof"]
        variants.append(no_proof)

        wrong_proof = self.batch("first")
        wrong_proof["source"]["authorProof"] = "display-name-only"
        variants.append(wrong_proof)

        wrong_host = self.batch("first")
        wrong_host["source"]["workspace_host"] = "whatnot.slack.com"
        variants.append(wrong_host)

        wrong_user = self.batch("first")
        wrong_user["events"][0]["user_id"] = "U0ATTACKER00"
        variants.append(wrong_user)

        out_of_order = self.batch("first")
        out_of_order["events"].reverse()
        variants.append(out_of_order)

        wrong_next = self.batch("first")
        wrong_next["observedThrough"] = wrong_next["events"][0]["message_ts"]
        variants.append(wrong_next)

        incomplete_poll = self.batch("first")
        incomplete_poll["pollProof"]["chronologyComplete"] = False
        variants.append(incomplete_poll)

        wrong_permalink_host = self.batch("first")
        wrong_permalink_host["rows"][0]["permalink"] = wrong_permalink_host["rows"][0][
            "permalink"
        ].replace("jw-qgi5008.slack.com", "whatnot.slack.com")
        variants.append(wrong_permalink_host)

        unknown_field = self.batch("first")
        unknown_field["events"][0]["attachments"] = []
        variants.append(unknown_field)

        for batch in variants:
            with self.subTest(batch=batch):
                with self.assertRaises(bridge.BridgeError):
                    self.validate(batch)
        self.assertFalse(self.runtime_root.exists())

    def test_misplaced_decimal_and_future_app_row_cannot_advance_cursor(self) -> None:
        misplaced = self.batch("first")
        ambiguous_ts = "17888255950.00002"
        misplaced["observedThrough"] = ambiguous_ts
        misplaced["rows"][-1]["message_ts"] = ambiguous_ts
        misplaced["events"][-1]["message_ts"] = ambiguous_ts
        with self.assertRaisesRegex(bridge.BridgeError, "invalid-source-cursor"):
            self.validate(misplaced)

        future_ts = "{:.6f}".format(self.now.timestamp() + 61)
        future = self.batch("first")
        future["baseObservedThrough"] = "{:.6f}".format(self.now.timestamp())
        future["observedThrough"] = future_ts
        future["pollProof"]["pollId"] = "poll_FUTURE001"
        future["rows"] = [
            {
                "message_ts": future_ts,
                "kind": "app-message",
                "permalink": "https://{}/archives/{}/p{}".format(
                    self.workspace_host,
                    self.policy.conversation_id,
                    future_ts.replace(".", ""),
                ),
            }
        ]
        future["events"] = []
        with self.assertRaisesRegex(bridge.BridgeError, "future-observed-through"):
            self.validate(future)

    def test_corrupt_poll_ledger_makes_snapshot_fail_closed(self) -> None:
        self.commit("first")
        with self.store.source_poll_ledger_path.open("a", encoding="utf-8") as handle:
            handle.write("{truncated\n")
        with self.assertRaisesRegex(bridge.StoreError, "invalid-source-poll-ledger"):
            self.store.snapshot(now=self.now)

    def test_empty_successful_poll_refreshes_receipt_without_cursor_advance(self) -> None:
        empty = self.batch("first")
        empty["events"] = []
        empty["rows"] = []
        empty["observedThrough"] = empty["baseObservedThrough"]
        empty["pollProof"]["pollId"] = "poll_EMPTY0001"
        base, next_cursor, rows, poll_id, decisions = self.validate(empty)
        assert base is not None
        self.store.bootstrap_source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, base, now=self.now
        )
        result = self.store.ingest_source_batch(
            decisions,
            source=bridge.SLACK_NATIVE_CUA_SOURCE,
            policy=self.policy,
            workspace_host=self.workspace_host,
            base_cursor=base,
            next_cursor=next_cursor,
            observed_rows=rows,
            poll_id=poll_id,
            now=self.now,
        )
        self.assertTrue(result["committed"])
        self.assertEqual(result["pollOutcome"], "verified")
        self.assertEqual(len(self.json_lines(self.store.source_cursor_ledger_path)), 1)
        self.assertEqual(len(self.json_lines(self.store.source_poll_ledger_path)), 1)
        snapshot = self.store.snapshot(now=self.now)
        self.assertEqual(snapshot["nativePoll"]["pollId"], "poll_EMPTY0001")
        self.assertTrue(snapshot["nativePoll"]["cursorConsistent"])

        empty["observedThrough"] = "1788825595.000002"
        with self.assertRaisesRegex(bridge.BridgeError, "empty-observation-cursor-change"):
            self.validate(empty)


if __name__ == "__main__":
    unittest.main()
