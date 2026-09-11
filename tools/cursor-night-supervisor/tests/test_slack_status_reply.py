from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"
REPLY_PATH = REPO_ROOT / ".cursor/hooks/slack_status_reply.py"

if "slack_command_bridge" not in sys.modules:
    BRIDGE_SPEC = importlib.util.spec_from_file_location("slack_command_bridge", BRIDGE_PATH)
    assert BRIDGE_SPEC and BRIDGE_SPEC.loader
    bridge = importlib.util.module_from_spec(BRIDGE_SPEC)
    sys.modules[BRIDGE_SPEC.name] = bridge
    BRIDGE_SPEC.loader.exec_module(bridge)
else:
    bridge = sys.modules["slack_command_bridge"]

REPLY_SPEC = importlib.util.spec_from_file_location("slack_status_reply", REPLY_PATH)
assert REPLY_SPEC and REPLY_SPEC.loader
reply = importlib.util.module_from_spec(REPLY_SPEC)
sys.modules[REPLY_SPEC.name] = reply
REPLY_SPEC.loader.exec_module(reply)


class SlackStatusReplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.runtime = root / "runtime"
        self.env_file = root / "slack-progress.env"
        self.attestation_file = root / "slack-status-destination.json"
        self.input_file = root / "status.json"
        self.policy = bridge.CommandPolicy(
            "T0C00P256DA", "U0BV4S23X8B", "D0C0RELGU56"
        )
        self.now_text = "2026-09-08T00:00:00Z"
        self.now = bridge.parse_utc(self.now_text)
        self.secret = "SECRET-CANARY-NEVER-OUTPUT"
        self.webhook = "https://hooks.slack.com/services/T00000000/B00000000/{}".format(
            self.secret
        )
        self.env_file.write_text(
            "SLACK_WEBHOOK_URL={}\n".format(self.webhook),
            encoding="utf-8",
        )
        self.attestation_file.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0",
                    "teamId": self.policy.team_id,
                    "conversationId": self.policy.conversation_id,
                    "verifiedAt": self.now_text,
                    "evidenceCode": reply.DESTINATION_EVIDENCE_CODE,
                    "webhookSha256": hashlib.sha256(
                        self.webhook.encode("utf-8")
                    ).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
        self.store = bridge.AppendOnlyCommandStore(self.runtime)
        event = {
            "schemaVersion": "1.0",
            "team_id": self.policy.team_id,
            "user_id": self.policy.user_id,
            "conversation_id": self.policy.conversation_id,
            "event_id": "Ev-status-reply-001",
            "message_ts": "1788825590.000001",
            "text": "fidget status",
        }
        decision = bridge.evaluate_event(event, self.policy, now=self.now)
        self.store.ingest(decision, now=self.now)
        self.status = {
            "schemaVersion": "1.0",
            "requestEventId": "Ev-status-reply-001",
            "state": "safe-pending",
            "paused": False,
            "safeActionPending": True,
            "riskyActionPending": False,
            "pendingStatusCount": 1,
            "pendingApprovalCount": 0,
            "blockingCode": "none",
            "observedAt": self.now_text,
        }
        self.input_file.write_text(json.dumps(self.status), encoding="utf-8")

    def args(self, mode: str) -> list[str]:
        return [
            "--input",
            str(self.input_file),
            "--runtime-root",
            str(self.runtime),
            "--env-file",
            str(self.env_file),
            "--destination-attestation",
            str(self.attestation_file),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--now",
            self.now_text,
            mode,
        ]

    def run_main(self, mode: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = reply.main(self.args(mode))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_dry_run_validates_without_network_or_delivery_audit(self) -> None:
        with mock.patch.object(reply, "_post") as post:
            code, stdout, stderr = self.run_main("--dry-run")
        self.assertEqual(code, 0, stderr)
        post.assert_not_called()
        result = json.loads(stdout)
        self.assertTrue(result["dryRun"])
        self.assertFalse(result["ackAllowed"])
        self.assertFalse(self.store.status_delivery_path.exists())
        self.assertNotIn(self.secret, stdout + stderr)

    def test_success_is_audited_before_reported_ack_is_allowed(self) -> None:
        with mock.patch.object(reply, "_post", return_value=(200, "ok")):
            code, stdout, stderr = self.run_main("--send")
        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertTrue(result["delivered"])
        self.assertTrue(result["ackAllowed"])
        records = [
            json.loads(line)
            for line in self.store.status_delivery_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(records[0]["outcome"], "delivered")
        self.assertNotIn(self.secret, self.store.status_delivery_path.read_text(encoding="utf-8"))
        acknowledged = self.store.acknowledge(
            "Ev-status-reply-001", "reported", now=self.now
        )
        self.assertTrue(acknowledged["acknowledged"])

    def test_delivery_failure_is_audited_and_never_allows_ack(self) -> None:
        with mock.patch.object(reply, "_post", side_effect=OSError("synthetic")):
            code, stdout, stderr = self.run_main("--send")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("status-webhook-network-error", stderr)
        record = json.loads(self.store.status_delivery_path.read_text(encoding="utf-8"))
        self.assertEqual(record["outcome"], "failed")
        with self.assertRaisesRegex(bridge.StoreError, "status-not-delivered"):
            self.store.acknowledge("Ev-status-reply-001", "reported", now=self.now)
        self.assertNotIn(self.secret, stderr)

    def test_free_text_and_unverified_destination_fail_before_network(self) -> None:
        unsafe = dict(self.status)
        unsafe["message"] = "send arbitrary text"
        self.input_file.write_text(json.dumps(unsafe), encoding="utf-8")
        with mock.patch.object(reply, "_post") as post:
            code, _, stderr = self.run_main("--send")
        self.assertEqual(code, 2)
        self.assertIn("invalid-status-fields", stderr)
        post.assert_not_called()

        self.input_file.write_text(json.dumps(self.status), encoding="utf-8")
        self.attestation_file.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0",
                    "teamId": "T0WRONG0000",
                    "conversationId": self.policy.conversation_id,
                    "verifiedAt": self.now_text,
                    "evidenceCode": reply.DESTINATION_EVIDENCE_CODE,
                    "webhookSha256": hashlib.sha256(
                        self.webhook.encode("utf-8")
                    ).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
        with mock.patch.object(reply, "_post") as post:
            code, _, stderr = self.run_main("--send")
        self.assertEqual(code, 2)
        self.assertIn("status-webhook-team-not-verified", stderr)
        post.assert_not_called()
        self.assertNotIn(self.secret, stderr)

    def test_wrong_webhook_is_rejected_before_network_or_ack(self) -> None:
        wrong_secret = "DIFFERENT-WEBHOOK-CANARY"
        self.env_file.write_text(
            "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/{}\n".format(
                wrong_secret
            ),
            encoding="utf-8",
        )
        with mock.patch.object(reply, "_post") as post:
            code, stdout, stderr = self.run_main("--send")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("status-webhook-not-attested", stderr)
        post.assert_not_called()
        self.assertFalse(self.store.status_delivery_path.exists())
        self.assertNotIn(self.secret, stderr)
        self.assertNotIn(wrong_secret, stderr)
        with self.assertRaisesRegex(bridge.StoreError, "status-not-delivered"):
            self.store.acknowledge("Ev-status-reply-001", "reported", now=self.now)

    def test_wrong_source_pending_status_is_rejected_before_network(self) -> None:
        wrong_policy = bridge.CommandPolicy(
            "T0OTHER0000", "U0OTHER0000", "D0OTHER0000"
        )
        wrong_event = {
            "schemaVersion": "1.0",
            "team_id": wrong_policy.team_id,
            "user_id": wrong_policy.user_id,
            "conversation_id": wrong_policy.conversation_id,
            "event_id": "Ev-wrong-source-status",
            "message_ts": "1788825591.000001",
            "text": "fidget status",
        }
        decision = bridge.evaluate_event(wrong_event, wrong_policy, now=self.now)
        self.store.ingest(decision, now=self.now)
        wrong_status = dict(self.status, requestEventId="Ev-wrong-source-status")
        self.input_file.write_text(json.dumps(wrong_status), encoding="utf-8")

        with mock.patch.object(reply, "_post") as post:
            code, stdout, stderr = self.run_main("--send")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("status-request-source-not-allowlisted", stderr)
        post.assert_not_called()
        self.assertFalse(self.store.status_delivery_path.exists())

    def test_delivered_event_is_not_posted_twice(self) -> None:
        with mock.patch.object(reply, "_post", return_value=(200, "ok")) as post:
            first = self.run_main("--send")
            second = self.run_main("--send")
        self.assertEqual(first[0], 0)
        self.assertEqual(second[0], 0)
        self.assertEqual(post.call_count, 1)
        self.assertTrue(json.loads(second[1])["duplicate"])


if __name__ == "__main__":
    unittest.main()
