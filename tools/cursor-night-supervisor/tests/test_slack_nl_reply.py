from __future__ import annotations

import hashlib
import importlib.util
import json
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"
STATUS_REPLY_PATH = REPO_ROOT / ".cursor/hooks/slack_status_reply.py"
ROUTER_PATH = REPO_ROOT / ".cursor/hooks/slack_nl_router.py"
REPLY_PATH = REPO_ROOT / ".cursor/hooks/slack_nl_reply.py"
CATALOG_PATH = REPO_ROOT / "tools/cursor-night-supervisor/slack-nl-task-catalog.json"


def load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bridge = load("slack_command_bridge", BRIDGE_PATH)
load("slack_status_reply", STATUS_REPLY_PATH)
router = load("slack_nl_router", ROUTER_PATH)
reply = load("slack_nl_reply", REPLY_PATH)


class SlackNaturalLanguageReplyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.bridge_store = bridge.AppendOnlyCommandStore(root / "bridge")
        self.store = router.NaturalLanguageStore(root / "nl")
        self.env_file = root / "slack-progress.env"
        self.attestation = root / "slack-status-destination.json"
        self.policy = bridge.CommandPolicy(
            "T0C00P256DA", "U0BV4S23X8B", "D0C0RELGU56"
        )
        self.host = "jw-qgi5008.slack.com"
        self.now = bridge.parse_utc("2026-09-08T00:00:00Z")
        self.catalog = router.load_task_catalog(CATALOG_PATH)
        self.base = "1788825590.000000"
        self.index = 0
        self.secret = "NL-REPLY-SECRET-CANARY"
        self.webhook = "https://hooks.slack.com/services/T00000000/B00000000/{}".format(
            self.secret
        )
        self.env_file.write_text("SLACK_WEBHOOK_URL={}\n".format(self.webhook), encoding="utf-8")
        self.attestation.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0",
                    "teamId": self.policy.team_id,
                    "conversationId": self.policy.conversation_id,
                    "verifiedAt": "2026-09-08T00:00:00Z",
                    "evidenceCode": "verified-outgoing-self-dm-permalink-v1",
                    "webhookSha256": hashlib.sha256(self.webhook.encode()).hexdigest(),
                }
            ),
            encoding="utf-8",
        )

    def event(self, text: str) -> dict:
        self.index += 1
        timestamp = "178882559{}.000001".format(4 + self.index)
        return {
            "schemaVersion": "1.0",
            "team_id": self.policy.team_id,
            "user_id": self.policy.user_id,
            "conversation_id": self.policy.conversation_id,
            "event_id": "Ev-reply-{:03d}".format(self.index),
            "message_ts": timestamp,
            "text": text,
        }

    def ingest(self, event: dict) -> str:
        if not self.bridge_store.source_cursor_ledger_path.exists():
            self.bridge_store.bootstrap_source_cursor(
                bridge.SLACK_NATIVE_CUA_SOURCE, self.policy, self.base, now=self.now
            )
        cursor = self.bridge_store.source_cursor(
            bridge.SLACK_NATIVE_CUA_SOURCE, self.policy
        )["cursor"]
        poll_id = "poll_REPLY{:04d}".format(self.index)
        decision = bridge.evaluate_native_cua_event(event, self.policy, now=self.now)
        row = bridge.SourceObservationRow(
            event["message_ts"],
            "self-message",
            "https://{}/archives/{}/p{}".format(
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
            base_cursor=cursor,
            next_cursor=event["message_ts"],
            observed_rows=[row],
            poll_id=poll_id,
            now=self.now,
        )
        return poll_id

    @staticmethod
    def classification(
        intent, target=None, action=None, clarification=None, recipient=None
    ):
        return {
            "schemaVersion": "1.0",
            "intent": intent,
            "recipient": recipient or ("cursor" if intent == "action" else None),
            "targetKey": target,
            "action": action,
            "clarificationCode": clarification,
        }

    def observation(self):
        return {
            "schemaVersion": "1.0",
            "catalogVersion": self.catalog.version,
            "inspectionId": "inspect_REPLYTEST01",
            "observedAt": "2026-09-08T00:00:00Z",
            "roundLeaseId": "lease_REPLYTEST01",
            "userUiIdle": True,
            "controller": {**dict(self.catalog.controller), "status": "running"},
            "targets": [
                {
                    "targetKey": target.target_key,
                    "backend": target.backend,
                    "threadId": target.thread_id,
                    "exactTitle": target.exact_title,
                    "authority": target.authority,
                    "state": "safe-pending",
                    "stateVersion": "state_REPLY000{}".format(index),
                    "uiUnambiguous": True,
                    "composerEmpty": True,
                    "visible": True,
                    "exactTitleMatchCount": 1,
                    "workspaceRoot": self.catalog.controller["projectRoot"],
                }
                for index, target in enumerate(self.catalog.targets.values(), start=1)
            ],
        }

    def route(self, event, classification, observation=None):
        poll_id = self.ingest(event)
        return self.store.route_native(
            event,
            classification,
            bridge_store=self.bridge_store,
            policy=self.policy,
            workspace_host=self.host,
            poll_id=poll_id,
            catalog=self.catalog,
            observation=observation,
            now=self.now,
        )

    @staticmethod
    def reply_value(event_id, kind, **kwargs):
        return {
            "schemaVersion": "1.0",
            "requestEventId": event_id,
            "replyKind": kind,
            "responseText": kwargs.get("responseText"),
            "clarificationCode": kwargs.get("clarificationCode"),
            "intentId": kwargs.get("intentId"),
            "confirmationToken": kwargs.get("confirmationToken"),
            "observation": kwargs.get("observation"),
        }

    def send(self, value, dry_run=False):
        return reply.send_reply(
            value,
            store=self.store,
            policy=self.policy,
            env_file=self.env_file,
            attestation_file=self.attestation,
            catalog_path=CATALOG_PATH,
            now=self.now,
            dry_run=dry_run,
        )

    def test_chat_reply_is_bounded_and_dry_run_has_no_network_or_audit(self) -> None:
        event = self.event("private question")
        self.route(event, self.classification("chat"))
        value = self.reply_value(
            event["event_id"], "chat", responseText="这是一个简短回答。"
        )
        with mock.patch.object(reply, "_post") as post:
            result = self.send(value, dry_run=True)
        post.assert_not_called()
        self.assertTrue(result["dryRun"])
        self.assertFalse(self.store.reply_path.exists())
        self.assertNotIn("这是一个简短回答", json.dumps(result, ensure_ascii=False))

    def test_reply_claims_before_post_and_never_retries(self) -> None:
        response = "PRIVATE-LLM-RESPONSE"
        event = self.event("question")
        self.route(event, self.classification("chat"))
        value = self.reply_value(event["event_id"], "chat", responseText=response)
        with mock.patch.object(reply, "_post", return_value=(200, "ok")) as post:
            first = self.send(value)
            second = self.send(value)
        self.assertTrue(first["delivered"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(post.call_count, 1)
        ledger = self.store.reply_path.read_text(encoding="utf-8")
        self.assertNotIn(response, ledger)
        self.assertNotIn(self.secret, ledger)
        records = [json.loads(line) for line in ledger.splitlines()]
        self.assertEqual([r["outcome"] for r in records], ["claimed", "delivered"])

    def test_uncertain_network_outcome_is_terminal_and_not_retried(self) -> None:
        event = self.event("question")
        self.route(event, self.classification("chat"))
        value = self.reply_value(event["event_id"], "chat", responseText="answer")
        with mock.patch.object(reply, "_post", side_effect=OSError("synthetic")) as post:
            with self.assertRaisesRegex(
                router.NaturalLanguageError, "nl-reply-network-outcome-unknown"
            ):
                self.send(value)
        with mock.patch.object(reply, "_post") as retry:
            duplicate = self.send(value)
        retry.assert_not_called()
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual(post.call_count, 1)

    def test_chat_mentions_invisible_text_and_marker_are_rejected(self) -> None:
        event = self.event("question")
        self.route(event, self.classification("chat"))
        for text in ("hello <@U123>", "hello\u200bworld", "FIDGETING_SLACK_REQUEST"):
            with self.subTest(text=text), mock.patch.object(reply, "_post") as post:
                with self.assertRaises(router.NaturalLanguageError):
                    self.send(
                        self.reply_value(event["event_id"], "chat", responseText=text)
                    )
                post.assert_not_called()

    def test_high_risk_preview_is_fixed_and_token_is_not_audited(self) -> None:
        event = self.event("push this")
        routed = self.route(
            event,
            self.classification(
                "action", "mobile-app-version-issue", "push-deploy"
            ),
            self.observation(),
        )
        token = routed.confirmation_token
        value = self.reply_value(
            event["event_id"],
            "confirmation-preview",
            intentId=routed.public["intentId"],
            confirmationToken=token,
        )
        captured = {}

        def fake_post(path, payload):
            captured.update(payload)
            return 200, "ok"

        with mock.patch.object(reply, "_post", side_effect=fake_post):
            result = self.send(value)
        self.assertTrue(result["delivered"])
        self.assertIn("未执行", captured["text"])
        self.assertIn(self.catalog.controller["exactTitle"], captured["text"])
        self.assertNotIn("当前 Codex 对话", captured["text"])
        self.assertIn(token, captured["text"])
        self.assertFalse(captured["unfurl_links"])
        self.assertNotIn(token, self.store.reply_path.read_text(encoding="utf-8"))

    def test_clarification_is_one_fixed_question_and_says_not_executed(self) -> None:
        event = self.event("do that")
        routed = self.route(
            event,
            self.classification("clarification", clarification="target-ambiguous"),
        )
        value = self.reply_value(
            event["event_id"], "clarification", clarificationCode="target-ambiguous"
        )
        captured = {}
        with mock.patch.object(
            reply, "_post", side_effect=lambda path, payload: (captured.update(payload) or (200, "ok"))
        ):
            self.send(value)
        self.assertIn("还没有执行", captured["text"])
        self.assertEqual(captured["text"].count("？"), 1)
        self.assertEqual(routed.public["replyKind"], "clarification")

    def test_arbitrary_reply_claim_and_free_form_audit_reason_are_refused(self) -> None:
        with self.assertRaisesRegex(router.NaturalLanguageError, "reply-not-pending"):
            self.store.claim_reply("Ev-does-not-exist", "chat", now=self.now)
        event = self.event("question")
        self.route(event, self.classification("chat"))
        self.assertTrue(self.store.claim_reply(event["event_id"], "chat", now=self.now))
        with self.assertRaisesRegex(router.NaturalLanguageError, "invalid-reply-reason"):
            self.store.finalize_reply(
                event["event_id"],
                "chat",
                "failed",
                "PRIVATE SECRET arbitrary reason",
                500,
                now=self.now,
            )

    def test_cli_reads_stdin_once_and_dry_run_never_posts_or_echoes_text(self) -> None:
        response = "PRIVATE-CLI-REPLY-CANARY"
        event = self.event("question")
        self.route(event, self.classification("chat"))
        value = self.reply_value(event["event_id"], "chat", responseText=response)
        args = [
            "--runtime-root",
            str(self.store.root),
            "--env-file",
            str(self.env_file),
            "--destination-attestation",
            str(self.attestation),
            "--allowed-team-id",
            self.policy.team_id,
            "--allowed-user-id",
            self.policy.user_id,
            "--allowed-conversation-id",
            self.policy.conversation_id,
            "--dry-run",
        ]
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
            mock.patch.object(sys, "stdin", io.StringIO(json.dumps(value))),
            mock.patch.object(reply, "_post") as post,
            mock.patch.object(reply, "utc_now", return_value=self.now),
        ):
            code = reply.main(args)
        self.assertEqual(code, 0, stderr.getvalue())
        post.assert_not_called()
        self.assertNotIn(response, stdout.getvalue() + stderr.getvalue())
        self.assertTrue(json.loads(stdout.getvalue())["dryRun"])


if __name__ == "__main__":
    unittest.main()
