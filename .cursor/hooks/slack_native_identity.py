#!/usr/bin/env python3
"""Extract one verified team->user mapping from a local Slack root-state JSON.

Only ``webapp.teams[TEAM_ID].userId`` is accessed after the canonical JSON is
parsed. The script never accesses token/cookie fields or serializes the root
object, and emits only the expected verified IDs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from slack_command_bridge import (
    BridgeError,
    SCHEMA_VERSION,
    SLACK_TEAM_ID,
    SLACK_USER_ID,
    canonical_json,
)


MAX_ROOT_STATE_BYTES = 50 * 1024 * 1024
CANONICAL_ROOT_STATE_PATH = (
    Path.home()
    / "Library"
    / "Containers"
    / "com.tinyspeck.slackmacgap"
    / "Data"
    / "Library"
    / "Application Support"
    / "Slack"
    / "storage"
    / "root-state.json"
)


def extract_identity(
    value: Mapping[str, Any], team_id: str, expected_user_id: str
) -> dict[str, Any]:
    if not SLACK_TEAM_ID.fullmatch(team_id):
        raise BridgeError("invalid-team-id")
    if not SLACK_USER_ID.fullmatch(expected_user_id):
        raise BridgeError("invalid-expected-user-id")
    webapp = value.get("webapp")
    teams = webapp.get("teams") if isinstance(webapp, Mapping) else None
    team = teams.get(team_id) if isinstance(teams, Mapping) else None
    user_id = team.get("userId") if isinstance(team, Mapping) else None
    if not isinstance(user_id, str) or not SLACK_USER_ID.fullmatch(user_id):
        raise BridgeError("root-state-user-id-unavailable")
    if user_id != expected_user_id:
        raise BridgeError("root-state-user-id-mismatch")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "verified": True,
        "teamId": team_id,
        "userId": expected_user_id,
    }


def load_root_state(path: Path) -> Mapping[str, Any]:
    try:
        if path.expanduser().resolve(strict=False) != CANONICAL_ROOT_STATE_PATH.resolve(
            strict=False
        ):
            raise BridgeError("noncanonical-root-state-path")
        if path.is_symlink() or not path.is_file():
            raise BridgeError("root-state-unavailable")
        if path.stat().st_size > MAX_ROOT_STATE_BYTES:
            raise BridgeError("root-state-too-large")
        value = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise BridgeError("invalid-root-state-json") from exc
    except OSError as exc:
        raise BridgeError("root-state-unavailable") from exc
    if not isinstance(value, dict):
        raise BridgeError("root-state-must-be-object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root-state", type=Path, default=CANONICAL_ROOT_STATE_PATH
    )
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--expected-user-id", required=True)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = extract_identity(
            load_root_state(args.root_state), args.team_id, args.expected_user_id
        )
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except BridgeError as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
