#!/usr/bin/env python3
"""Pure dry-run decision layer for one Cursor heartbeat observation.

Input is a JSON observation. Output is a deterministic JSON decision. This module
does not import or call any UI API and cannot click a control by itself.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shlex
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "1.0"
OBSERVED_STATES = {"running", "safe_pending", "risky_pending", "failed", "waiting_user"}
TARGET_TASKS: Mapping[str, Mapping[str, bool]] = {
    "Card draw scene research": {"writeEnabled": False},
    "Mobile app version issue": {"writeEnabled": True},
    "Conversation freezing issue": {"writeEnabled": True},
}
TMP_OUTPUT_ROOTS = (Path("/tmp/fidgeting-edc-research"), Path("/tmp/dragon-scale-gate02"))
DEFAULT_VAULT_ROOT = Path("/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手")
SENSITIVE_PATH_PARTS = {
    ".claudian",
    ".git",
    ".obsidian",
    ".ssh",
    ".gnupg",
    ".aws",
}

READ_ONLY_EXECUTABLES = {"pwd", "ls", "cat", "head", "tail", "wc", "rg", "stat", "shasum", "ffprobe"}
FORBIDDEN_FIND_ACTIONS = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls"}
FORBIDDEN_TOKENS = {
    "--refresh",
    "approve",
    "approval",
    "accept",
    "reject",
    "supersede",
    "commit",
    "push",
    "reset",
    "clean",
    "checkout",
    "switch",
    "restore",
    "rebase",
    "merge",
    "cherry-pick",
    "revert",
    "install-package",
    "archive",
}
SHELL_CONTROL_PATTERN = re.compile(r"(?:&&|\|\||[;|<>`]|\$\()")
MODEL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
APPROVAL_REQUEST_ID_PATTERN = re.compile(r"^safe_[A-Za-z0-9]{5,32}$")
SLACK_EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")
SLACK_POLL_ID_PATTERN = re.compile(r"^poll_[A-Za-z0-9]{8,64}$")
SLACK_TIMESTAMP_PATTERN = re.compile(r"^[0-9]{10}\.[0-9]{6}$")
SLACK_TEAM_ID_PATTERN = re.compile(r"^T[A-Z0-9]{2,31}$")
SLACK_USER_ID_PATTERN = re.compile(r"^[UW][A-Z0-9]{2,31}$")
SLACK_CONVERSATION_ID_PATTERN = re.compile(r"^[CDG][A-Z0-9]{2,31}$")
SLACK_WORKSPACE_HOST_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}\.slack\.com$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
SLACK_CONTROL_COMMANDS = {"status", "pause", "resume", "approve-safe"}
SLACK_CONTROL_MODES = {"approval-required", "native-pause-only"}
SLACK_CONTROL_MAX_AGE_SECONDS = 60
SLACK_CONTROL_FUTURE_SKEW_SECONDS = 5
NATIVE_POLL_KEYS = {
    "source",
    "teamId",
    "userId",
    "conversationId",
    "workspaceHost",
    "pollId",
    "outcome",
    "reason",
    "recordedAt",
    "verifiedPollAt",
    "baseObservedThrough",
    "observedThrough",
    "batchDigest",
    "observedRowCount",
    "eventCount",
    "cursorConsistent",
}


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _is_within(path: Path, root: Path) -> bool:
    try:
        _resolve(path).relative_to(_resolve(root))
        return True
    except ValueError:
        return False


def _command_argv(value: Any) -> tuple[list[str], str | None]:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value), None
    if isinstance(value, str):
        if SHELL_CONTROL_PATTERN.search(value):
            return [], "shell-control-operator"
        try:
            return shlex.split(value), None
        except ValueError:
            return [], "command-parse-failed"
    return [], "command-missing"


def _contains_forbidden_token(argv: Sequence[str]) -> str | None:
    lowered = [token.lower() for token in argv]
    for forbidden in sorted(FORBIDDEN_TOKENS):
        if forbidden in lowered:
            return forbidden
        if any(forbidden in Path(token).name.lower() for token in argv):
            return forbidden
    return None


def _paths(action: Mapping[str, Any], field: str) -> list[Path]:
    value = action.get(field, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return []
    return [Path(item) for item in value]


def _all_outputs_in_tmp(action: Mapping[str, Any]) -> bool:
    outputs = _paths(action, "outputPaths")
    return bool(outputs) and all(output.is_absolute() for output in outputs) and all(
        any(_is_within(output, root) for root in TMP_OUTPUT_ROOTS) for output in outputs
    )


def _path_policy_error(
    argv: Sequence[str], working_directory: Path, repo_root: Path
) -> str | None:
    """Reject secret trees and path arguments outside the unattended read boundary."""

    allowed_roots = (repo_root, DEFAULT_VAULT_ROOT, *TMP_OUTPUT_ROOTS)
    for token in argv[1:]:
        if "://" in token:
            continue

        candidate_token = token
        if token.startswith("-"):
            if "=" not in token:
                continue
            candidate_token = token.split("=", 1)[1]

        if not candidate_token:
            continue
        candidate = Path(candidate_token)
        parts = {part.lower() for part in candidate.parts}
        sensitive = sorted(parts & SENSITIVE_PATH_PARTS)
        if sensitive:
            return f"sensitive-path:{sensitive[0]}"

        looks_like_path = (
            candidate.is_absolute()
            or candidate_token.startswith(".")
            or "/" in candidate_token
        )
        if not looks_like_path:
            continue
        resolved = candidate if candidate.is_absolute() else working_directory / candidate
        if not any(_is_within(resolved, root) for root in allowed_roots):
            return "path-outside-allowed-roots"
    return None


def _allowed_revision_root(action: Mapping[str, Any], repo_root: Path) -> Path | None:
    model_id = action.get("currentModelId")
    revision_value = action.get("currentRevisionRoot")
    if not isinstance(model_id, str) or not MODEL_ID_PATTERN.fullmatch(model_id):
        return None
    if not isinstance(revision_value, str):
        return None

    revision_root = Path(revision_value)
    if not revision_root.is_absolute():
        revision_root = repo_root / revision_root
    evidence_root = (
        repo_root
        / "unity/FidgetingApp/ArtSource/ModelPipeline"
        / model_id
        / "evidence"
    )
    if not _is_within(revision_root, evidence_root):
        return None
    if "rev-" not in revision_root.name:
        return None
    return revision_root


def _outputs_in_current_revision(action: Mapping[str, Any], repo_root: Path) -> bool:
    revision_root = _allowed_revision_root(action, repo_root)
    outputs = _paths(action, "outputPaths")
    return revision_root is not None and bool(outputs) and all(
        _is_within(output if output.is_absolute() else repo_root / output, revision_root)
        for output in outputs
    )


def _read_only_category(argv: Sequence[str]) -> str | None:
    executable = Path(argv[0]).name
    if any(SHELL_CONTROL_PATTERN.search(token) for token in argv):
        return None
    if executable in READ_ONLY_EXECUTABLES:
        if executable == "ffprobe" and any(
            token == "-o" or token.startswith("--output") for token in argv[1:]
        ):
            return None
        return "read-only-inspection"
    if executable == "find" and not any(token in FORBIDDEN_FIND_ACTIONS for token in argv[1:]):
        return "read-only-inspection"
    if executable == "pmset" and list(argv[1:]) in (["-g", "batt"], ["-g", "assertions"]):
        return "power-inspection"
    if executable == "df":
        return "disk-inspection"
    if executable == "git":
        tokens = [token for token in argv[1:] if token != "--no-optional-locks"]
        writes_output = any(token.startswith("--output") for token in tokens)
        if (
            tokens
            and tokens[0] in {"status", "diff", "log"}
            and "--ext-diff" not in tokens
            and not writes_output
        ):
            return "read-only-git"
    return None


def _known_test_or_validator(argv: Sequence[str], working_directory: Path, repo_root: Path) -> str | None:
    if list(argv) in (
        ["python3", "-m", "unittest", "discover", "-s", "tools/cursor-night-supervisor/tests"],
        ["python3", "-m", "unittest", "discover", "-s", "tools/cursor-night-supervisor/tests", "-v"],
    ):
        return "focused-supervisor-tests"
    if list(argv) == ["npm", "test"] and _resolve(working_directory) == _resolve(
        repo_root / "tools/model-provenance-explorer"
    ):
        return "known-model-workbench-tests"
    if len(argv) == 3 and list(argv[:2]) == [
        "node",
        "skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs",
    ] and MODEL_ID_PATTERN.fullmatch(argv[2]):
        return "read-only-model-validator"
    if len(argv) >= 2 and list(argv[:2]) == [
        "python3",
        "tools/cursor-night-supervisor/preflight.py",
    ]:
        allowed_flags = {
            "--fail-on-blocker",
            "--repo-root",
            "--terminal-log",
            "--cursor-logs-root",
            "--min-free-gib",
        }
        flags = {token for token in argv[2:] if token.startswith("--")}
        if flags <= allowed_flags:
            return "read-only-preflight"
    return None


def _bounded_media_category(argv: Sequence[str], action: Mapping[str, Any]) -> str | None:
    executable = Path(argv[0]).name
    if executable in {"ffmpeg", "yt-dlp"} and _all_outputs_in_tmp(action):
        return "bounded-temp-media"
    if len(argv) >= 3 and list(argv[:3]) == ["python3", "-m", "yt_dlp"] and _all_outputs_in_tmp(action):
        return "bounded-temp-media"
    return None


def _blender_category(argv: Sequence[str], action: Mapping[str, Any], repo_root: Path) -> str | None:
    executable = Path(argv[0]).name.lower()
    if "blender" not in executable or "--background" not in argv or "--python" not in argv:
        return None
    try:
        script = Path(argv[argv.index("--python") + 1])
    except (ValueError, IndexError):
        return None
    if script.is_absolute() or not _is_within(repo_root / script, repo_root / "tools/blender"):
        return None
    if _all_outputs_in_tmp(action) or _outputs_in_current_revision(action, repo_root):
        return "deterministic-blender"
    return None


def _simulator_category(argv: Sequence[str], action: Mapping[str, Any]) -> str | None:
    if Path(argv[0]).name == "xcodebuild":
        joined = " ".join(argv)
        if "platform=iOS Simulator" in joined and "-derivedDataPath" in argv:
            try:
                derived_data = Path(argv[argv.index("-derivedDataPath") + 1])
            except (ValueError, IndexError):
                return None
            if (
                derived_data.is_absolute()
                and any(_is_within(derived_data, root) for root in TMP_OUTPUT_ROOTS)
                and _all_outputs_in_tmp(action)
            ):
                return "simulator-only"
    if len(argv) >= 3 and list(argv[:2]) == ["xcrun", "simctl"]:
        # simctl cannot address a physical iPhone; still require temp-only products.
        if _all_outputs_in_tmp(action):
            return "simulator-only"
    return None


def _evidence_category(argv: Sequence[str], action: Mapping[str, Any], repo_root: Path) -> str | None:
    if not _outputs_in_current_revision(action, repo_root):
        return None
    if not argv or Path(argv[0]).name not in {"python3", "node"} or len(argv) < 2:
        return None
    script = Path(argv[1])
    if script.is_absolute():
        script_path = script
    else:
        script_path = repo_root / script
    revision_root = _allowed_revision_root(action, repo_root)
    if revision_root is not None and _is_within(script_path, revision_root):
        return "current-revision-evidence"
    return None


def classify_command(action: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    argv, parse_error = _command_argv(action.get("command"))
    if parse_error:
        return {"allowed": False, "category": None, "reason": parse_error, "argv": []}
    if not argv:
        return {"allowed": False, "category": None, "reason": "command-empty", "argv": []}

    forbidden = _contains_forbidden_token(argv)
    if forbidden:
        return {
            "allowed": False,
            "category": None,
            "reason": f"forbidden-token:{forbidden}",
            "argv": argv,
        }

    working_value = action.get("workingDirectory", str(repo_root))
    working_directory = Path(working_value) if isinstance(working_value, str) else repo_root
    if not working_directory.is_absolute():
        working_directory = repo_root / working_directory
    if not _is_within(working_directory, repo_root):
        return {
            "allowed": False,
            "category": None,
            "reason": "working-directory-outside-repo",
            "argv": argv,
        }

    path_error = _path_policy_error(argv, working_directory, repo_root)
    if path_error:
        return {
            "allowed": False,
            "category": None,
            "reason": path_error,
            "argv": argv,
        }

    category = (
        _read_only_category(argv)
        or _known_test_or_validator(argv, working_directory, repo_root)
        or _bounded_media_category(argv, action)
        or _blender_category(argv, action, repo_root)
        or _simulator_category(argv, action)
        or _evidence_category(argv, action, repo_root)
    )
    return {
        "allowed": category is not None,
        "category": category,
        "reason": "allowlisted" if category else "not-allowlisted",
        "argv": argv,
    }


def _control_timestamp(value: Any) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(dt.timezone.utc)


def _valid_slack_pending_item(value: Any, generated_at: dt.datetime) -> bool:
    if not isinstance(value, Mapping):
        return False
    event_id = value.get("eventId")
    command = value.get("command")
    request_id = value.get("requestId")
    if not isinstance(event_id, str) or not SLACK_EVENT_ID_PATTERN.fullmatch(event_id):
        return False
    if command not in SLACK_CONTROL_COMMANDS or not isinstance(value.get("expired"), bool):
        return False
    if command == "approve-safe" and not (
        isinstance(request_id, str)
        and APPROVAL_REQUEST_ID_PATTERN.fullmatch(request_id) is not None
    ):
        return False
    if command != "approve-safe" and request_id is not None:
        return False

    expires_at = _control_timestamp(value.get("expiresAt"))
    if command in {"status", "approve-safe"}:
        return expires_at is not None and value["expired"] == (expires_at <= generated_at)
    return value.get("expiresAt") is None and value["expired"] is False


def _native_poll_gate(
    slack_control: Any,
    expected_poll_id: Any,
    expected_team_id: Any,
    expected_user_id: Any,
    expected_conversation_id: Any,
    expected_workspace_host: Any,
    current: dt.datetime,
) -> dict[str, Any]:
    expected_valid = bool(
        isinstance(expected_poll_id, str)
        and SLACK_POLL_ID_PATTERN.fullmatch(expected_poll_id)
    )
    policy_valid = bool(
        isinstance(expected_team_id, str)
        and SLACK_TEAM_ID_PATTERN.fullmatch(expected_team_id)
        and isinstance(expected_user_id, str)
        and SLACK_USER_ID_PATTERN.fullmatch(expected_user_id)
        and isinstance(expected_conversation_id, str)
        and SLACK_CONVERSATION_ID_PATTERN.fullmatch(expected_conversation_id)
        and isinstance(expected_workspace_host, str)
        and SLACK_WORKSPACE_HOST_PATTERN.fullmatch(expected_workspace_host)
    )
    poll = slack_control.get("nativePoll") if isinstance(slack_control, Mapping) else None
    structure_valid = False
    verified = False
    fresh = False
    matched = False
    if isinstance(poll, Mapping) and set(poll) == NATIVE_POLL_KEYS:
        recorded_at = _control_timestamp(poll.get("recordedAt"))
        verified_at = _control_timestamp(poll.get("verifiedPollAt"))
        row_count = poll.get("observedRowCount")
        event_count = poll.get("eventCount")
        base_raw = poll.get("baseObservedThrough")
        observed_raw = poll.get("observedThrough")
        try:
            base_value = (
                Decimal(base_raw)
                if isinstance(base_raw, str) and SLACK_TIMESTAMP_PATTERN.fullmatch(base_raw)
                else None
            )
            observed_value = (
                Decimal(observed_raw)
                if isinstance(observed_raw, str)
                and SLACK_TIMESTAMP_PATTERN.fullmatch(observed_raw)
                else None
            )
        except InvalidOperation:
            base_value = None
            observed_value = None
        counts_valid = bool(
            isinstance(row_count, int)
            and not isinstance(row_count, bool)
            and isinstance(event_count, int)
            and not isinstance(event_count, bool)
            and row_count >= 0
            and 0 <= event_count <= row_count
        )
        position_valid = bool(
            base_value is not None
            and observed_value is not None
            and (
                (row_count == 0 and observed_value == base_value)
                or (isinstance(row_count, int) and row_count > 0 and observed_value > base_value)
            )
        )
        outcome = poll.get("outcome")
        verified = bool(
            outcome == "verified"
            and poll.get("reason") == "continuous-stable-bottom"
            and verified_at is not None
            and recorded_at == verified_at
            and isinstance(poll.get("batchDigest"), str)
            and SHA256_PATTERN.fullmatch(poll["batchDigest"])
        )
        failed_shape = bool(
            outcome == "failed"
            and isinstance(poll.get("reason"), str)
            and re.fullmatch(r"[a-z0-9-]{1,80}", poll["reason"])
            and poll.get("verifiedPollAt") is None
            and poll.get("batchDigest") is None
            and row_count == 0
            and event_count == 0
            and base_value is not None
            and observed_value == base_value
        )
        structure_valid = bool(
            poll.get("source") == "slack-native-cua"
            and isinstance(poll.get("teamId"), str)
            and SLACK_TEAM_ID_PATTERN.fullmatch(poll["teamId"])
            and isinstance(poll.get("userId"), str)
            and SLACK_USER_ID_PATTERN.fullmatch(poll["userId"])
            and isinstance(poll.get("conversationId"), str)
            and SLACK_CONVERSATION_ID_PATTERN.fullmatch(poll["conversationId"])
            and isinstance(poll.get("workspaceHost"), str)
            and SLACK_WORKSPACE_HOST_PATTERN.fullmatch(poll["workspaceHost"])
            and isinstance(poll.get("pollId"), str)
            and SLACK_POLL_ID_PATTERN.fullmatch(poll["pollId"])
            and isinstance(poll.get("cursorConsistent"), bool)
            and recorded_at is not None
            and counts_valid
            and position_valid
            and (verified or failed_shape)
        )
        matched = bool(
            structure_valid and expected_valid and poll.get("pollId") == expected_poll_id
        )
        age = (current - verified_at).total_seconds() if verified_at is not None else None
        fresh = bool(
            structure_valid
            and verified
            and age is not None
            and -SLACK_CONTROL_FUTURE_SKEW_SECONDS
            <= age
            <= SLACK_CONTROL_MAX_AGE_SECONDS
        )
    return {
        "expectedPollId": expected_poll_id if expected_valid else None,
        "expectedPollIdValid": expected_valid,
        "pollSupplied": poll is not None,
        "pollValid": structure_valid,
        "pollVerified": verified,
        "pollFresh": fresh,
        "pollIdMatched": matched,
        "expectedPolicyValid": policy_valid,
        "pollPolicyMatched": bool(
            structure_valid
            and policy_valid
            and isinstance(poll, Mapping)
            and poll.get("teamId") == expected_team_id
            and poll.get("userId") == expected_user_id
            and poll.get("conversationId") == expected_conversation_id
            and poll.get("workspaceHost") == expected_workspace_host
        ),
        "pollCursorConsistent": bool(
            structure_valid and isinstance(poll, Mapping) and poll.get("cursorConsistent") is True
        ),
    }


def _slack_approval_gate(
    slack_control: Any,
    *,
    supplied: bool,
    pending_action: Any,
    current: dt.datetime,
) -> dict[str, Any]:
    pending_items = slack_control.get("pending") if isinstance(slack_control, Mapping) else None
    generated_at = _control_timestamp(
        slack_control.get("generatedAt") if isinstance(slack_control, Mapping) else None
    )
    structure_valid = bool(
        supplied
        and isinstance(slack_control, Mapping)
        and slack_control.get("schemaVersion") == SCHEMA_VERSION
        and isinstance(slack_control.get("paused"), bool)
        and isinstance(pending_items, list)
        and generated_at is not None
        and all(_valid_slack_pending_item(item, generated_at) for item in pending_items)
    )
    state_age = (current - generated_at).total_seconds() if structure_valid else None
    fresh = bool(
        structure_valid
        and state_age is not None
        and -SLACK_CONTROL_FUTURE_SKEW_SECONDS <= state_age <= SLACK_CONTROL_MAX_AGE_SECONDS
    )
    valid = structure_valid and fresh
    paused = bool(valid and slack_control.get("paused") is True)
    action_request_id = (
        pending_action.get("approvalRequestId")
        if isinstance(pending_action, Mapping)
        else None
    )
    action_request_id_valid = bool(
        isinstance(action_request_id, str)
        and APPROVAL_REQUEST_ID_PATTERN.fullmatch(action_request_id)
    )

    approval_items = [
        item for item in pending_items if item.get("command") == "approve-safe"
    ] if structure_valid else []
    expired_approvals = [
        item
        for item in approval_items
        if item.get("expired") is True
        or (_control_timestamp(item.get("expiresAt")) or current) <= current
    ]
    active_approvals = [
        item for item in approval_items if valid and item not in expired_approvals
    ]
    matches = [
        item for item in active_approvals if item.get("requestId") == action_request_id
    ] if action_request_id_valid else []
    matched = matches[0] if matches else None

    return {
        "supplied": supplied,
        "valid": valid,
        "fresh": fresh,
        "paused": paused,
        "approvalRequestId": action_request_id if action_request_id_valid else None,
        "approvalRequestIdValid": action_request_id_valid,
        "approvalMatched": matched is not None,
        "approvalEventId": matched.get("eventId") if matched else None,
        "activeApprovalEventIds": [item["eventId"] for item in active_approvals],
        "expiredApprovalEventIds": [item["eventId"] for item in expired_approvals],
    }


def decide(
    observation: Mapping[str, Any], *, now: dt.datetime | None = None
) -> dict[str, Any]:
    current = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
    state = observation.get("state")
    task_title = observation.get("taskTitle")
    repo_root = Path(str(observation.get("repoRoot", "/fixture/Fidgeting app")))
    target = task_title in TARGET_TASKS
    write_enabled = bool(TARGET_TASKS.get(str(task_title), {}).get("writeEnabled", False))
    preflight_status = observation.get("preflightStatus", "unknown")
    pending = observation.get("pendingAction")
    slack_control = observation.get("slackControlState")
    slack_control_supplied = "slackControlState" in observation
    slack_control_mode = observation.get("slackControlMode", "approval-required")
    slack_control_mode_valid = slack_control_mode in SLACK_CONTROL_MODES
    slack_gate = _slack_approval_gate(
        slack_control,
        supplied=slack_control_supplied,
        pending_action=pending,
        current=current,
    )
    native_poll_gate = _native_poll_gate(
        slack_control,
        observation.get("slackPollId"),
        observation.get("slackAllowedTeamId"),
        observation.get("slackAllowedUserId"),
        observation.get("slackAllowedConversationId"),
        observation.get("slackAllowedWorkspaceHost"),
        current,
    )
    command_policy = None
    if isinstance(pending, Mapping):
        command_policy = classify_command(pending, repo_root)

    action = "notify"
    click = False
    notify = True
    control = None
    requested_control = None
    claim_required = False
    reason = "unsupported-state"

    if state == "running":
        action, notify, reason = "inspect", False, "task-running"
    elif state == "safe_pending":
        requested_control = pending.get("control") if isinstance(pending, Mapping) else None
        safe = (
            target
            and write_enabled
            and preflight_status in {"ready", "warning"}
            and requested_control in {"run", "approve"}
            and bool(command_policy and command_policy["allowed"])
        )
        if safe:
            action = "click"
            click = True
            notify = False
            control = requested_control
            reason = "target-task-allowlisted-command"
        else:
            reason = "safe-pending-preconditions-failed"
    elif state == "risky_pending":
        reason = "risky-action-requires-user"
    elif state == "failed":
        reason = "task-failed"
    elif state == "waiting_user":
        reason = "user-decision-required"

    # Native CUA supplies a fail-closed pause gate but no real per-message user
    # identity, so it cannot add approval authority or remove the supervisor's
    # pre-existing allowlisted safe clicks. The stronger connector mode keeps
    # exact request-bound, claim-before-click approval semantics.
    if click:
        if not slack_control_mode_valid:
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-control-mode-invalid",
            )
        elif not slack_gate["supplied"]:
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-control-required",
            )
        elif not slack_gate["valid"]:
            action, click, control, notify, reason = (
                "notify" if slack_control_mode == "native-pause-only" else "inspect",
                False,
                None,
                slack_control_mode == "native-pause-only",
                "slack-control-invalid",
            )
        elif slack_gate["paused"]:
            action, click, control, notify, reason = (
                "inspect",
                False,
                None,
                False,
                "slack-control-paused",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["expectedPollIdValid"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-id-required",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["expectedPolicyValid"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-policy-required",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollValid"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-invalid",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollIdMatched"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-id-mismatch",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollPolicyMatched"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-policy-mismatch",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollVerified"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-unverified",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollCursorConsistent"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-cursor-inconsistent",
            )
        elif (
            slack_control_mode == "native-pause-only"
            and not native_poll_gate["pollFresh"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "slack-poll-stale",
            )
        elif (
            slack_control_mode == "approval-required"
            and not slack_gate["approvalRequestIdValid"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "approval-request-id-required",
            )
        elif (
            slack_control_mode == "approval-required"
            and not slack_gate["approvalMatched"]
        ):
            action, click, control, notify, reason = (
                "notify",
                False,
                None,
                True,
                "approval-request-id-mismatch",
            )

    if click and slack_control_mode == "approval-required":
        # This is eligibility to claim, not permission to click yet. The
        # executor must atomically claim this exact event/request pair, inspect
        # the same UI action again, and only then use postClaimControl.
        action = "claim"
        click = False
        control = None
        notify = False
        claim_required = True
        reason = "approval-claim-required"

    # An approval is single-observation and single-action. Anything not used by
    # this exact click is returned as a refusal target so the consumer can
    # append a terminal `refused` record before the next heartbeat.
    used_approval_event_id = slack_gate["approvalEventId"] if claim_required else None
    refusal_event_ids = [
        event_id
        for event_id in slack_gate["activeApprovalEventIds"]
        if event_id != used_approval_event_id
    ] if slack_control_mode == "approval-required" else []

    # Preserve normal quiet inspection unless an otherwise quiet observation
    # contains an approval that must be terminally refused.
    if refusal_event_ids and action == "inspect" and not notify and not slack_gate["paused"]:
        action, notify, reason = "notify", True, "approval-request-refused"

    return {
        "schemaVersion": SCHEMA_VERSION,
        "observationId": observation.get("observationId"),
        "task": {
            "title": task_title,
            "isTarget": target,
            "writeEnabledTonight": write_enabled,
        },
        "observedState": state,
        "preflightStatus": preflight_status,
        "slackControl": {
            **slack_gate,
            **native_poll_gate,
            "mode": slack_control_mode if slack_control_mode_valid else None,
            "modeValid": slack_control_mode_valid,
            "refuseApprovalEventIds": refusal_event_ids,
        },
        "commandPolicy": command_policy,
        "decision": {
            "action": action,
            "click": click,
            "control": control,
            "claimRequired": claim_required,
            "claimEventId": slack_gate["approvalEventId"] if claim_required else None,
            "claimRequestId": slack_gate["approvalRequestId"] if claim_required else None,
            "postClaimControl": requested_control if claim_required else None,
            "notify": notify,
            "reason": reason,
        },
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument(
        "--control-state",
        type=Path,
        help="optional control-state.json from slack_command_consumer.py snapshot",
    )
    parser.add_argument(
        "--slack-control-mode",
        choices=tuple(sorted(SLACK_CONTROL_MODES)),
        help="interpret supplied Slack control as approval-required or native pause-only",
    )
    parser.add_argument(
        "--slack-poll-id",
        help="exact pollId returned by this heartbeat's native Slack ingest/failure call",
    )
    parser.add_argument("--slack-allowed-team-id")
    parser.add_argument("--slack-allowed-user-id")
    parser.add_argument("--slack-allowed-conversation-id")
    parser.add_argument("--slack-allowed-workspace-host")
    parser.add_argument("--now", help="test-only RFC3339 decision clock override")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    with args.fixture.open("r", encoding="utf-8") as handle:
        observation = json.load(handle)
    if args.control_state:
        with args.control_state.open("r", encoding="utf-8") as handle:
            observation["slackControlState"] = json.load(handle)
    if args.slack_control_mode:
        observation["slackControlMode"] = args.slack_control_mode
    if args.slack_poll_id:
        observation["slackPollId"] = args.slack_poll_id
    for argument, field in (
        (args.slack_allowed_team_id, "slackAllowedTeamId"),
        (args.slack_allowed_user_id, "slackAllowedUserId"),
        (args.slack_allowed_conversation_id, "slackAllowedConversationId"),
        (args.slack_allowed_workspace_host, "slackAllowedWorkspaceHost"),
    ):
        if argument:
            observation[field] = argument
    current = _control_timestamp(args.now) if args.now else dt.datetime.now(dt.timezone.utc)
    if current is None:
        raise SystemExit("invalid --now timestamp")
    report = decide(observation, now=current)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
