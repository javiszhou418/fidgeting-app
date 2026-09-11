from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
IDENTITY_PATH = REPO_ROOT / ".cursor/hooks/slack_native_identity.py"
BRIDGE_PATH = REPO_ROOT / ".cursor/hooks/slack_command_bridge.py"

if "slack_command_bridge" not in sys.modules:
    BRIDGE_SPEC = importlib.util.spec_from_file_location("slack_command_bridge", BRIDGE_PATH)
    assert BRIDGE_SPEC and BRIDGE_SPEC.loader
    bridge = importlib.util.module_from_spec(BRIDGE_SPEC)
    sys.modules[BRIDGE_SPEC.name] = bridge
    BRIDGE_SPEC.loader.exec_module(bridge)
else:
    bridge = sys.modules["slack_command_bridge"]

IDENTITY_SPEC = importlib.util.spec_from_file_location("slack_native_identity", IDENTITY_PATH)
assert IDENTITY_SPEC and IDENTITY_SPEC.loader
identity = importlib.util.module_from_spec(IDENTITY_SPEC)
sys.modules[IDENTITY_SPEC.name] = identity
IDENTITY_SPEC.loader.exec_module(identity)


class SlackNativeIdentityTests(unittest.TestCase):
    @staticmethod
    def run_identity(root_state: Path) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(identity, "CANONICAL_ROOT_STATE_PATH", root_state):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = identity.main(
                    [
                        "--root-state",
                        str(root_state),
                        "--team-id",
                        "T0C00P256DA",
                        "--expected-user-id",
                        "U0BV4S23X8B",
                    ]
                )
        return code, stdout.getvalue(), stderr.getvalue()

    def test_extracts_only_exact_team_user_mapping_not_selected_user(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root_state = Path(temporary) / "root-state.json"
            secret = "xoxc-secret-canary"
            root_state.write_text(
                json.dumps(
                    {
                        "selectedUserId": "U0STALE0000",
                        "token": secret,
                        "webapp": {
                            "teams": {
                                "T0C00P256DA": {"userId": "U0BV4S23X8B"},
                                "T0OTHER000": {"userId": "U0OTHER0000"},
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            code, stdout, stderr = self.run_identity(root_state)
            self.assertEqual(code, 0, stderr)
            self.assertEqual(
                json.loads(stdout),
                {
                    "schemaVersion": "1.0",
                    "verified": True,
                    "teamId": "T0C00P256DA",
                    "userId": "U0BV4S23X8B",
                },
            )
            self.assertNotIn(secret, stdout + stderr)
            self.assertNotIn("U0STALE0000", stdout + stderr)
            self.assertNotIn("U0OTHER0000", stdout + stderr)

    def test_mismatch_fails_without_disclosing_observed_user(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root_state = Path(temporary) / "root-state.json"
            observed = "U0ATTACKER00"
            root_state.write_text(
                json.dumps(
                    {"webapp": {"teams": {"T0C00P256DA": {"userId": observed}}}}
                ),
                encoding="utf-8",
            )
            code, stdout, stderr = self.run_identity(root_state)
            self.assertEqual(code, 2)
            self.assertIn("root-state-user-id-mismatch", stderr)
            self.assertNotIn(observed, stdout + stderr)

    def test_arbitrary_root_state_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "canonical" / "root-state.json"
            attacker = root / "attacker.json"
            attacker.write_text(
                json.dumps(
                    {
                        "webapp": {
                            "teams": {
                                "T0C00P256DA": {"userId": "U0BV4S23X8B"}
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(identity, "CANONICAL_ROOT_STATE_PATH", canonical):
                with self.assertRaisesRegex(
                    bridge.BridgeError, "noncanonical-root-state-path"
                ):
                    identity.load_root_state(attacker)


if __name__ == "__main__":
    unittest.main()
