from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOL_ROOT.parents[1]
PREFLIGHT_PATH = TOOL_ROOT / "preflight.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PERMISSIONS_PATH = REPO_ROOT / ".cursor/permissions.json"

SPEC = importlib.util.spec_from_file_location("cursor_night_preflight", PREFLIGHT_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class PreflightFixtureTests(unittest.TestCase):
    def run_fixture(self, name: str, *extra_args: str) -> tuple[int, dict]:
        completed = subprocess.run(
            [
                sys.executable,
                str(PREFLIGHT_PATH),
                "--fixture",
                str(FIXTURES / name),
                *extra_args,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.stderr, "")
        return completed.returncode, json.loads(completed.stdout)

    def test_ready_fixture_is_stable_and_ready(self) -> None:
        first_code, first = self.run_fixture("ready.json")
        second_code, second = self.run_fixture("ready.json")

        self.assertEqual(first_code, 0)
        self.assertEqual(second_code, 0)
        self.assertEqual(first, second)
        self.assertEqual(first["schemaVersion"], "1.0")
        self.assertEqual(first["overall"], {"blockers": [], "status": "ready", "warnings": []})
        self.assertTrue(first["power"]["onAcPower"])
        self.assertTrue(first["power"]["preventsDisplaySleep"])
        self.assertEqual(first["terminalLogs"]["logs"][0]["lastExitCode"], 0)
        self.assertEqual(first["worktree"]["untrackedCount"], 1)

    def test_blocked_fixture_reports_every_safety_gate(self) -> None:
        code, report = self.run_fixture("blocked.json", "--fail-on-blocker")

        self.assertEqual(code, 2)
        self.assertEqual(report["overall"]["status"], "blocked")
        self.assertEqual(
            set(report["overall"]["blockers"]),
            {
                "disk.below-minimum",
                "pipeline-core.conflicted",
                "power.display-sleep-not-prevented",
                "power.not-on-ac",
                "unity.lock-present",
                "worktree.conflicts-present",
            },
        )
        self.assertEqual(report["pipelineCore"]["state"], "conflicted")
        self.assertEqual(report["terminalLogs"]["status"], "attention")
        self.assertEqual(report["terminalLogs"]["logs"][1]["lastExitCode"], 65)

    def test_porcelain_summary_separates_staged_unstaged_and_conflicts(self) -> None:
        summary = preflight.parse_porcelain(
            "M  staged.txt\n M unstaged.txt\nMM both.txt\n?? new.txt\nUU conflict.txt\n"
        )
        self.assertEqual(
            summary,
            {
                "changedCount": 5,
                "stagedCount": 3,
                "unstagedCount": 3,
                "untrackedCount": 1,
                "conflictedCount": 1,
            },
        )


class ReadOnlyPolicyTests(unittest.TestCase):
    def test_collector_command_table_is_read_only_and_has_no_ui(self) -> None:
        forbidden_tokens = {
            "commit",
            "push",
            "reset",
            "clean",
            "checkout",
            "restore",
            "switch",
            "refresh",
            "osascript",
            "open",
            "rm",
        }
        allowed_executables = {"pmset", "df", "git"}
        for name, command in preflight.READ_ONLY_COMMANDS.items():
            with self.subTest(name=name):
                self.assertIn(command[0], allowed_executables)
                self.assertTrue(forbidden_tokens.isdisjoint(command))
        self.assertIn("GIT_OPTIONAL_LOCKS", preflight.run_read_only_commands.__doc__ or "")

    def test_cursor_permissions_encode_unattended_boundaries(self) -> None:
        permissions = json.loads(PERMISSIONS_PATH.read_text(encoding="utf-8"))["autoRun"]
        allowed = "\n".join(permissions["allow_instructions"])
        blocked = "\n".join(permissions["block_instructions"])

        self.assertNotIn("validate-pipelines.mjs --refresh", allowed)
        self.assertIn("validate-pipelines.mjs --refresh", blocked)
        self.assertIn("/tmp/fidgeting-edc-research/", allowed)
        self.assertIn("/tmp/dragon-scale-gate02/", allowed)
        self.assertIn("yt-dlp", allowed)
        self.assertIn("YYYY-MM-DD Markdown notes", allowed)
        for private_tree in (".claudian", ".obsidian", ".git metadata"):
            self.assertIn(private_tree, blocked)
        for phrase in (
            "Gate approval",
            "visual approval",
            "git commit",
            "git push",
            "git reset",
            "git clean",
            "git checkout",
            "history rewrite",
            "physical iPhone",
            "shipping build",
            "credentials",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, blocked)


if __name__ == "__main__":
    unittest.main()
