from __future__ import annotations

import datetime as dt
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = TOOL_ROOT / "heartbeat_decision.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures/heartbeat"
NOW = dt.datetime(2026, 9, 7, 12, 0, tzinfo=dt.timezone.utc)

SPEC = importlib.util.spec_from_file_location("heartbeat_decision", DECISION_PATH)
assert SPEC and SPEC.loader
decision = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(decision)


class HeartbeatFiveStateTests(unittest.TestCase):
    @staticmethod
    def native_poll(
        *, poll_id: str = "poll_HEARTBEAT1", at: str = "2026-09-07T11:59:50Z",
        outcome: str = "verified"
    ) -> dict:
        verified = outcome == "verified"
        return {
            "source": "slack-native-cua",
            "teamId": "T0C00P256DA",
            "userId": "U0BV4S23X8B",
            "conversationId": "D0C0RELGU56",
            "workspaceHost": "jw-qgi5008.slack.com",
            "pollId": poll_id,
            "outcome": outcome,
            "reason": "continuous-stable-bottom" if verified else "chronology-ambiguous",
            "recordedAt": at,
            "verifiedPollAt": at if verified else None,
            "baseObservedThrough": "1788840299.185749",
            "observedThrough": "1788840299.185749",
            "batchDigest": "a" * 64 if verified else None,
            "observedRowCount": 0,
            "eventCount": 0,
            "cursorConsistent": True,
        }

    def fixture(self, name: str) -> dict:
        completed = subprocess.run(
            [
                sys.executable,
                str(DECISION_PATH),
                "--fixture",
                str(FIXTURES / f"{name}.json"),
                "--now",
                "2026-09-07T12:00:00Z",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout)

    def test_running_inspects_without_click_or_notification(self) -> None:
        report = self.fixture("running")
        self.assertEqual(report["decision"]["action"], "inspect")
        self.assertFalse(report["decision"]["click"])
        self.assertFalse(report["decision"]["notify"])

    def test_safe_pending_requires_atomic_claim_before_any_click(self) -> None:
        report = self.fixture("safe_pending")
        self.assertTrue(report["task"]["isTarget"])
        self.assertTrue(report["task"]["writeEnabledTonight"])
        self.assertTrue(report["commandPolicy"]["allowed"])
        self.assertEqual(report["commandPolicy"]["category"], "read-only-model-validator")
        self.assertEqual(report["decision"]["action"], "claim")
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["claimRequired"])
        self.assertEqual(report["decision"]["claimEventId"], "Ev-approve-001")
        self.assertEqual(report["decision"]["claimRequestId"], "safe_ABCDE1")
        self.assertEqual(report["decision"]["postClaimControl"], "run")
        self.assertFalse(report["decision"]["notify"])
        self.assertTrue(report["slackControl"]["approvalMatched"])
        self.assertEqual(report["slackControl"]["approvalRequestId"], "safe_ABCDE1")
        self.assertEqual(report["slackControl"]["approvalEventId"], "Ev-approve-001")
        self.assertEqual(report["slackControl"]["refuseApprovalEventIds"], [])

    def test_safe_pending_rejects_non_target_paused_and_non_allowlisted_cases(self) -> None:
        base = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        variants = []

        non_target = dict(base, taskTitle="Unrelated task")
        variants.append(non_target)

        paused = dict(base, taskTitle="Card draw scene research")
        variants.append(paused)

        blocked_preflight = dict(base, preflightStatus="blocked")
        variants.append(blocked_preflight)

        dangerous = dict(base)
        dangerous["pendingAction"] = dict(base["pendingAction"])
        dangerous["pendingAction"]["command"] = "git push origin main"
        variants.append(dangerous)

        for observation in variants:
            with self.subTest(observation=observation):
                report = decision.decide(observation, now=NOW)
                self.assertFalse(report["decision"]["click"])
                self.assertTrue(report["decision"]["notify"])

    def test_slack_pause_can_only_narrow_a_safe_click(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        observation["slackControlState"] = dict(observation["slackControlState"], paused=True)
        report = decision.decide(observation, now=NOW)
        self.assertTrue(report["commandPolicy"]["allowed"])
        self.assertTrue(report["slackControl"]["valid"])
        self.assertTrue(report["slackControl"]["paused"])
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-control-paused")
        self.assertEqual(
            report["slackControl"]["refuseApprovalEventIds"], ["Ev-approve-001"]
        )

    def test_native_mode_is_fail_closed_pause_gate_not_approval_requirement(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        observation["slackControlMode"] = "native-pause-only"
        observation["slackPollId"] = "poll_HEARTBEAT1"
        observation["slackAllowedTeamId"] = "T0C00P256DA"
        observation["slackAllowedUserId"] = "U0BV4S23X8B"
        observation["slackAllowedConversationId"] = "D0C0RELGU56"
        observation["slackAllowedWorkspaceHost"] = "jw-qgi5008.slack.com"
        observation["slackControlState"]["pending"] = []
        observation["slackControlState"]["nativePoll"] = self.native_poll()
        del observation["pendingAction"]["approvalRequestId"]

        allowed = decision.decide(observation, now=NOW)
        self.assertTrue(allowed["slackControl"]["valid"])
        self.assertEqual(allowed["slackControl"]["mode"], "native-pause-only")
        self.assertTrue(allowed["decision"]["click"])
        self.assertEqual(allowed["decision"]["action"], "click")
        self.assertEqual(allowed["decision"]["control"], "run")
        self.assertFalse(allowed["decision"]["claimRequired"])

        paused = json.loads(json.dumps(observation))
        paused["slackControlState"]["paused"] = True
        blocked = decision.decide(paused, now=NOW)
        self.assertFalse(blocked["decision"]["click"])
        self.assertEqual(blocked["decision"]["reason"], "slack-control-paused")

        corrupt = json.loads(json.dumps(observation))
        corrupt["slackControlState"]["pending"] = "invalid"
        failed_closed = decision.decide(corrupt, now=NOW)
        self.assertFalse(failed_closed["decision"]["click"])
        self.assertTrue(failed_closed["decision"]["notify"])
        self.assertEqual(failed_closed["decision"]["reason"], "slack-control-invalid")

    def test_conversation_freezing_issue_is_an_allowlisted_safe_target(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        observation["taskTitle"] = "Conversation freezing issue"
        observation["slackControlMode"] = "native-pause-only"
        observation["slackPollId"] = "poll_HEARTBEAT1"
        observation["slackAllowedTeamId"] = "T0C00P256DA"
        observation["slackAllowedUserId"] = "U0BV4S23X8B"
        observation["slackAllowedConversationId"] = "D0C0RELGU56"
        observation["slackAllowedWorkspaceHost"] = "jw-qgi5008.slack.com"
        observation["slackControlState"]["pending"] = []
        observation["slackControlState"]["nativePoll"] = self.native_poll()
        del observation["pendingAction"]["approvalRequestId"]

        report = decision.decide(observation, now=NOW)

        self.assertTrue(report["task"]["isTarget"])
        self.assertTrue(report["task"]["writeEnabledTonight"])
        self.assertTrue(report["commandPolicy"]["allowed"])
        self.assertTrue(report["decision"]["click"])
        self.assertEqual(report["decision"]["control"], "run")

    def test_native_click_requires_same_round_verified_poll_receipt(self) -> None:
        base = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        base["slackControlMode"] = "native-pause-only"
        base["slackAllowedTeamId"] = "T0C00P256DA"
        base["slackAllowedUserId"] = "U0BV4S23X8B"
        base["slackAllowedConversationId"] = "D0C0RELGU56"
        base["slackAllowedWorkspaceHost"] = "jw-qgi5008.slack.com"
        base["slackControlState"]["pending"] = []
        base["slackControlState"]["nativePoll"] = self.native_poll()
        del base["pendingAction"]["approvalRequestId"]

        missing_id = json.loads(json.dumps(base))
        report = decision.decide(missing_id, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-poll-id-required")

        mismatched = json.loads(json.dumps(base))
        mismatched["slackPollId"] = "poll_DIFFERENT1"
        report = decision.decide(mismatched, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-poll-id-mismatch")

        wrong_policy = json.loads(json.dumps(base))
        wrong_policy["slackPollId"] = "poll_HEARTBEAT1"
        wrong_policy["slackAllowedTeamId"] = "T0WRONGTEAM1"
        report = decision.decide(wrong_policy, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-poll-policy-mismatch")

        stale = json.loads(json.dumps(base))
        stale["slackPollId"] = "poll_HEARTBEAT1"
        stale["slackControlState"]["nativePoll"] = self.native_poll(
            at="2026-09-07T11:58:00Z"
        )
        # A newly generated snapshot must not make an old receipt fresh.
        stale["slackControlState"]["generatedAt"] = "2026-09-07T12:00:00Z"
        report = decision.decide(stale, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-poll-stale")

        failed = json.loads(json.dumps(base))
        failed["slackPollId"] = "poll_FAILED001"
        failed["slackControlState"]["nativePoll"] = self.native_poll(
            poll_id="poll_FAILED001", at="2026-09-07T12:00:00Z", outcome="failed"
        )
        failed["slackControlState"]["generatedAt"] = "2026-09-07T12:00:00Z"
        report = decision.decide(failed, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-poll-unverified")

    def test_missing_mismatched_or_expired_approval_never_clicks(self) -> None:
        base = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))

        no_state = dict(base)
        del no_state["slackControlState"]

        missing_action_id = json.loads(json.dumps(base))
        del missing_action_id["pendingAction"]["approvalRequestId"]

        mismatched = json.loads(json.dumps(base))
        mismatched["slackControlState"]["pending"][0]["requestId"] = "safe_OTHER1"

        expired = json.loads(json.dumps(base))
        expired["slackControlState"]["pending"][0]["expired"] = True
        expired["slackControlState"]["pending"][0]["expiresAt"] = "2026-09-07T12:00:00Z"

        wrong_command = json.loads(json.dumps(base))
        wrong_command["slackControlState"]["pending"][0]["command"] = "status"
        wrong_command["slackControlState"]["pending"][0]["requestId"] = None

        malformed_pending = json.loads(json.dumps(base))
        malformed_pending["slackControlState"]["pending"] = "not-a-list"

        malformed_expiry = json.loads(json.dumps(base))
        del malformed_expiry["slackControlState"]["pending"][0]["expired"]

        invalid_expiry_time = json.loads(json.dumps(base))
        invalid_expiry_time["slackControlState"]["pending"][0]["expiresAt"] = "not-a-time"

        malformed_action_id = json.loads(json.dumps(base))
        malformed_action_id["pendingAction"]["approvalRequestId"] = "safe_AB!DE"

        variants = (
            (no_state, "slack-control-required", []),
            (missing_action_id, "approval-request-id-required", ["Ev-approve-001"]),
            (mismatched, "approval-request-id-mismatch", ["Ev-approve-001"]),
            (expired, "approval-request-id-mismatch", []),
            (wrong_command, "approval-request-id-mismatch", []),
            (malformed_pending, "slack-control-invalid", []),
            (malformed_expiry, "slack-control-invalid", []),
            (invalid_expiry_time, "slack-control-invalid", []),
            (malformed_action_id, "approval-request-id-required", ["Ev-approve-001"]),
        )
        for observation, expected_reason, expected_refusals in variants:
            with self.subTest(expected_reason=expected_reason, observation=observation):
                report = decision.decide(observation, now=NOW)
                self.assertFalse(report["decision"]["click"])
                self.assertEqual(report["decision"]["reason"], expected_reason)
                self.assertEqual(
                    report["slackControl"]["refuseApprovalEventIds"], expected_refusals
                )

    def test_unmatched_approval_is_terminal_refusal_target_not_future_permission(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        observation["pendingAction"]["approvalRequestId"] = "safe_FUTURE9"
        first = decision.decide(observation, now=NOW)
        self.assertFalse(first["decision"]["click"])
        self.assertEqual(
            first["slackControl"]["refuseApprovalEventIds"], ["Ev-approve-001"]
        )

        # A consumer appends `refused`, so the next derived snapshot has no
        # pending approval and cannot reuse the old event for the later action.
        observation["slackControlState"]["pending"] = []
        replay = decision.decide(observation, now=NOW)
        self.assertFalse(replay["decision"]["click"])
        self.assertFalse(replay["slackControl"]["approvalMatched"])
        self.assertEqual(replay["slackControl"]["refuseApprovalEventIds"], [])

    def test_approval_with_no_current_action_is_refused_immediately(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        observation["state"] = "running"
        observation["pendingAction"] = None
        report = decision.decide(observation, now=NOW)
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["notify"])
        self.assertEqual(report["decision"]["reason"], "approval-request-refused")
        self.assertEqual(
            report["slackControl"]["refuseApprovalEventIds"], ["Ev-approve-001"]
        )

    def test_duplicate_request_id_selects_once_and_refuses_the_extra_event(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        duplicate = dict(observation["slackControlState"]["pending"][0])
        duplicate["eventId"] = "Ev-approve-002"
        observation["slackControlState"]["pending"].append(duplicate)
        report = decision.decide(observation, now=NOW)
        self.assertEqual(report["decision"]["action"], "claim")
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["claimRequired"])
        self.assertEqual(report["slackControl"]["approvalEventId"], "Ev-approve-001")
        self.assertEqual(
            report["slackControl"]["refuseApprovalEventIds"], ["Ev-approve-002"]
        )

    def test_stale_cached_state_cannot_authorize_an_expired_approval(self) -> None:
        observation = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        later = NOW + dt.timedelta(minutes=10)
        report = decision.decide(observation, now=later)
        self.assertFalse(report["slackControl"]["fresh"])
        self.assertFalse(report["slackControl"]["valid"])
        self.assertFalse(report["decision"]["click"])
        self.assertEqual(report["decision"]["reason"], "slack-control-invalid")
        self.assertEqual(
            report["slackControl"]["expiredApprovalEventIds"], ["Ev-approve-001"]
        )

    def test_malformed_slack_control_fails_closed_for_clicks_only(self) -> None:
        safe = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        safe["slackControlState"] = {"schemaVersion": "999", "paused": "no"}
        safe_report = decision.decide(safe, now=NOW)
        self.assertFalse(safe_report["slackControl"]["valid"])
        self.assertFalse(safe_report["decision"]["click"])
        self.assertEqual(safe_report["decision"]["reason"], "slack-control-invalid")

        null_state = json.loads((FIXTURES / "safe_pending.json").read_text(encoding="utf-8"))
        null_state["slackControlState"] = None
        null_report = decision.decide(null_state, now=NOW)
        self.assertTrue(null_report["slackControl"]["supplied"])
        self.assertFalse(null_report["slackControl"]["valid"])
        self.assertFalse(null_report["decision"]["click"])

        failed = json.loads((FIXTURES / "failed.json").read_text(encoding="utf-8"))
        failed["slackControlState"] = {"paused": "bad"}
        failed_report = decision.decide(failed, now=NOW)
        self.assertTrue(failed_report["decision"]["notify"])
        self.assertEqual(failed_report["decision"]["reason"], "task-failed")

    def test_risky_pending_never_clicks_and_notifies(self) -> None:
        report = self.fixture("risky_pending")
        self.assertFalse(report["commandPolicy"]["allowed"])
        self.assertIn("forbidden-token", report["commandPolicy"]["reason"])
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["notify"])

    def test_failed_never_clicks_and_notifies(self) -> None:
        report = self.fixture("failed")
        self.assertEqual(report["decision"]["reason"], "task-failed")
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["notify"])

    def test_waiting_user_never_clicks_and_notifies(self) -> None:
        report = self.fixture("waiting_user")
        self.assertFalse(report["task"]["writeEnabledTonight"])
        self.assertEqual(report["decision"]["reason"], "user-decision-required")
        self.assertFalse(report["decision"]["click"])
        self.assertTrue(report["decision"]["notify"])


class CommandAllowlistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("/fixture/Fidgeting app")

    def classify(self, command, **extra):
        action = {
            "command": command,
            "workingDirectory": str(self.root),
            "outputPaths": [],
            **extra,
        }
        return decision.classify_command(action, self.root)

    def test_shell_controls_find_delete_and_refresh_are_rejected(self) -> None:
        commands = (
            "git status && git push",
            ["git", "status", "&&", "git", "push"],
            ["git", "diff", "--output=/tmp/fidgeting-edc-research/leak.diff"],
            ["find", ".", "-delete"],
            ["node", "tools/model-provenance-explorer/validate-pipelines.mjs", "--refresh"],
            ["ffprobe", "-o", "/tmp/fidgeting-edc-research/probe.json", "video.mp4"],
        )
        for command in commands:
            with self.subTest(command=command):
                self.assertFalse(self.classify(command)["allowed"])

    def test_media_write_requires_a_bounded_tmp_output(self) -> None:
        safe = self.classify(
            ["yt-dlp", "https://example.invalid/reference"],
            outputPaths=["/tmp/fidgeting-edc-research/source-001/video.mp4"],
        )
        unsafe = self.classify(
            ["yt-dlp", "https://example.invalid/reference"],
            outputPaths=["/fixture/Fidgeting app/video.mp4"],
        )
        self.assertTrue(safe["allowed"])
        self.assertFalse(unsafe["allowed"])

    def test_relative_temp_output_is_rejected_as_ambiguous(self) -> None:
        report = self.classify(
            ["ffmpeg", "-i", "input.mp4", "output.mp4"],
            outputPaths=["tmp/fidgeting-edc-research/output.mp4"],
        )
        self.assertFalse(report["allowed"])

    def test_read_only_paths_exclude_private_trees_and_unrelated_files(self) -> None:
        approved_note = self.classify(
            [
                "cat",
                "/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手/2026-08-01/source.md",
            ]
        )
        approved_tmp_media = self.classify(
            ["ffprobe", "/tmp/dragon-scale-gate02/video/geeone-source.mp4"]
        )
        rejected = (
            ["cat", "/Users/jiawei.zhou/.ssh/id_rsa"],
            [
                "rg",
                "token",
                "/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手/.claudian",
            ],
            ["cat", "/fixture/Fidgeting app/.git/config"],
            ["find", "/Users/jiawei.zhou/Documents", "-name", "*.md"],
        )

        self.assertTrue(approved_note["allowed"])
        self.assertTrue(approved_tmp_media["allowed"])
        for command in rejected:
            with self.subTest(command=command):
                self.assertFalse(self.classify(command)["allowed"])


if __name__ == "__main__":
    unittest.main()
