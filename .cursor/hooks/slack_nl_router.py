#!/usr/bin/env python3
"""Fail-closed natural-language routing for the Fidgeting Slack self-DM.

This module is deliberately not a Slack client or an executor.  It validates a
transient human self-message against the authoritative native-CUA poll/audit
ledgers, validates model output against a tiny enum-only schema, binds any
action to the checked-in task catalog and a fresh state observation, and writes
only privacy-preserving metadata to append-only ledgers.

An in-process controller may claim a low-risk intent and receive a fixed policy
envelope containing the bounded, JSON-escaped Slack request.  The public CLI
never emits that request, a confirmation token, or a webhook secret.  It never
runs a shell command, controls a UI, sends a task message, or posts to Slack.
"""

from __future__ import annotations

import argparse
import contextlib
import base64
import datetime as dt
import fcntl
import hashlib
import hmac
import json
import os
import re
import secrets
import stat
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence

from slack_command_bridge import (
    AppendOnlyCommandStore,
    BridgeError,
    CommandPolicy,
    MAX_FUTURE_SKEW_SECONDS,
    SCHEMA_VERSION,
    SHA256_HEX,
    SLACK_EVENT_ID,
    SLACK_TEAM_ID,
    SLACK_USER_ID,
    SLACK_CONVERSATION_ID,
    SLACK_NATIVE_CUA_SOURCE,
    SLACK_NATIVE_TIMESTAMP,
    SLACK_POLL_ID,
    SLACK_WORKSPACE_HOST,
    StoreError,
    canonical_json,
    default_runtime_root as default_bridge_runtime_root,
    format_utc,
    parse_slack_timestamp,
    parse_utc,
    text_fingerprint,
    utc_now,
)


POLICY_VERSION = "fidgeting-slack-nl-v1"
NATIVE_AUTHOR_PROOF = "native-from-me-self-dm-verified-user-map-v1"
FORWARD_PROVENANCE = "fidgeting-slack-self-dm-v1"
DEFAULT_CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "cursor-night-supervisor"
    / "slack-nl-task-catalog.json"
)
MAX_EVENT_AGE_SECONDS = 900
MAX_OBSERVATION_AGE_SECONDS = 60
CONFIRMATION_TTL_SECONDS = 600
ROUND_LEASE_SECONDS = 120
PRIVATE_TICKET_TTL_SECONDS = 60
MAX_RAW_TEXT_BYTES = 4096

CLASSIFICATION_KEYS = {
    "schemaVersion",
    "intent",
    "recipient",
    "targetKey",
    "action",
    "clarificationCode",
}
INTENTS = frozenset(
    {"chat", "status", "action", "clarification", "confirmation", "cancel"}
)
SAFE_ACTIONS = frozenset(
    {"inspect-state", "continue-allowlisted", "run-fixed-tests"}
)
RISKY_ACTIONS = frozenset(
    {
        "approval",
        "credential",
        "destructive",
        "external-send",
        "gate-visual-device",
        "install",
        "other",
        "payment",
        "push-deploy",
    }
)
ALL_ACTIONS = SAFE_ACTIONS | RISKY_ACTIONS
RECIPIENTS = frozenset({"cursor", "codex"})
CLARIFICATION_CODES = frozenset(
    {"target-ambiguous", "success-criteria-ambiguous", "unsupported-request"}
)
NL_EVENT_REASONS = frozenset(
    {
        "chat",
        "status",
        "clarification",
        "cancelled",
        "cancel-too-late",
        "cancel-target-not-found",
        "direct-confirmation-required",
        "low-risk-awaiting-atomic-claim",
        "prior-route-incomplete-resend",
        "recipient-action-not-allowed",
        "target-ambiguous",
        "target-authority-inspect-only",
    }
)
RECEIPT_REASONS = frozenset(
    {
        "cancel-too-late",
        "cancel-target-not-found",
        "cancelled",
        "direct-confirmation-required",
        "low-risk-awaiting-atomic-claim",
        "prior-route-incomplete-resend",
        "recipient-action-not-allowed",
        "target-authority-inspect-only",
    }
)
TARGET_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){0,7}$")
THREAD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{7,127}$")
INSPECTION_ID = re.compile(r"^inspect_[A-Za-z0-9]{8,64}$")
STATE_VERSION = re.compile(r"^state_[A-Za-z0-9]{8,64}$")
LEASE_ID = re.compile(r"^lease_[A-Za-z0-9]{8,64}$")
INTENT_ID = re.compile(r"^intent_[A-Za-z0-9]{12,64}$")
CONFIRM_TOKEN = re.compile(r"^[A-HJ-NP-Z2-9]{6}$")
CONFIRM_MESSAGE = re.compile(r"^确认 ([A-HJ-NP-Z2-9]{6})$")
CANCEL_MESSAGE = re.compile(r"^取消 (intent_[A-Za-z0-9]{12,64})$")

CATALOG_KEYS = {"schemaVersion", "catalogVersion", "controller", "targets"}
CONTROLLER_KEYS = {
    "backend",
    "threadId",
    "projectId",
    "hostId",
    "projectRoot",
    "exactTitle",
}
CATALOG_TARGET_KEYS = {
    "targetKey",
    "backend",
    "threadId",
    "exactTitle",
    "authority",
}
OBSERVATION_KEYS = {
    "schemaVersion",
    "catalogVersion",
    "inspectionId",
    "observedAt",
    "roundLeaseId",
    "userUiIdle",
    "controller",
    "targets",
}
OBSERVED_CONTROLLER_KEYS = CONTROLLER_KEYS | {"status"}
OBSERVED_TARGET_KEYS = CATALOG_TARGET_KEYS | {
    "state",
    "stateVersion",
    "uiUnambiguous",
    "composerEmpty",
    "visible",
    "exactTitleMatchCount",
    "workspaceRoot",
}
TARGET_STATES = frozenset(
    {
        "running",
        "idle",
        "safe-pending",
        "risky-pending",
        "failed",
        "waiting-user",
        "complete",
        "archived",
    }
)
REPLY_FINAL_REASONS = {
    "delivered": frozenset({"webhook-ok"}),
    "failed": frozenset({"http-error", "unexpected-response"}),
    "unknown": frozenset({"network-outcome-unknown"}),
}
CONTROLLER_STATES = frozenset({"running", "idle", "waiting", "blocked"})


class NaturalLanguageError(BridgeError):
    """An error safe to expose without message text or credentials."""


@dataclass(frozen=True)
class TaskTarget:
    target_key: str
    backend: str
    thread_id: Optional[str]
    exact_title: str
    authority: str


@dataclass(frozen=True)
class TaskCatalog:
    version: str
    controller: Mapping[str, str]
    targets: Mapping[str, TaskTarget]


@dataclass(frozen=True)
class PreparedRoute:
    """Public metadata plus private in-memory material for a controller.

    ``request_text`` and ``confirmation_token`` must never be serialized to a
    terminal, ledger, status hook, or diagnostic log.
    """

    public: Mapping[str, Any]
    request_text: Optional[str] = None
    confirmation_token: Optional[str] = None


def default_runtime_root() -> Path:
    return Path(__file__).resolve().parents[1] / "runtime" / "slack-nl-router"


def _read_json_file(path: Path, *, max_bytes: int, error: str) -> Mapping[str, Any]:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > max_bytes:
            raise NaturalLanguageError(error)
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise NaturalLanguageError(error) from exc
    if not isinstance(value, dict):
        raise NaturalLanguageError(error)
    return value


def _bounded_string(value: Any, *, limit: int, pattern: Optional[re.Pattern[str]] = None) -> bool:
    return bool(
        isinstance(value, str)
        and 0 < len(value) <= limit
        and value == unicodedata.normalize("NFC", value)
        and all(
            character in {"\n", "\t"}
            or unicodedata.category(character) not in {"Cc", "Cf"}
            for character in value
        )
        and (pattern is None or pattern.fullmatch(value))
    )


def load_task_catalog(path: Path = DEFAULT_CATALOG_PATH) -> TaskCatalog:
    value = _read_json_file(path, max_bytes=16_384, error="invalid-task-catalog")
    if set(value) != CATALOG_KEYS or value.get("schemaVersion") != SCHEMA_VERSION:
        raise NaturalLanguageError("invalid-task-catalog")
    version = value.get("catalogVersion")
    controller = value.get("controller")
    targets = value.get("targets")
    if (
        not _bounded_string(version, limit=80, pattern=TARGET_KEY)
        or not isinstance(controller, dict)
        or set(controller) != CONTROLLER_KEYS
        or controller.get("backend") != "codex"
        or not _bounded_string(controller.get("threadId"), limit=128, pattern=THREAD_ID)
        or not _bounded_string(controller.get("projectId"), limit=128, pattern=THREAD_ID)
        or controller.get("hostId") != "local"
        or not isinstance(controller.get("projectRoot"), str)
        or not Path(controller["projectRoot"]).is_absolute()
        or not _bounded_string(controller.get("exactTitle"), limit=120)
        or not isinstance(targets, list)
        or not 1 <= len(targets) <= 20
    ):
        raise NaturalLanguageError("invalid-task-catalog")
    mapped: dict[str, TaskTarget] = {}
    for raw in targets:
        if not isinstance(raw, dict) or set(raw) != CATALOG_TARGET_KEYS:
            raise NaturalLanguageError("invalid-task-catalog")
        key = raw.get("targetKey")
        if (
            not _bounded_string(key, limit=80, pattern=TARGET_KEY)
            or key in mapped
            or raw.get("backend") != "cursor-native"
            or not _bounded_string(raw.get("exactTitle"), limit=120)
            or raw.get("authority") not in {"inspect-only", "allowlisted-safe"}
        ):
            raise NaturalLanguageError("invalid-task-catalog")
        thread_id = raw.get("threadId")
        if thread_id is not None:
            raise NaturalLanguageError("invalid-task-catalog")
        mapped[key] = TaskTarget(
            target_key=key,
            backend=raw["backend"],
            thread_id=thread_id,
            exact_title=raw["exactTitle"],
            authority=raw["authority"],
        )
    return TaskCatalog(version=version, controller=dict(controller), targets=mapped)


def validate_classification(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != CLASSIFICATION_KEYS:
        raise NaturalLanguageError("invalid-classification-fields")
    if value.get("schemaVersion") != SCHEMA_VERSION or value.get("intent") not in INTENTS:
        raise NaturalLanguageError("invalid-classification")
    intent = value["intent"]
    recipient = value.get("recipient")
    target = value.get("targetKey")
    action = value.get("action")
    clarification = value.get("clarificationCode")
    if target is not None and not _bounded_string(target, limit=80, pattern=TARGET_KEY):
        raise NaturalLanguageError("invalid-classification-target")
    valid = False
    if intent == "chat":
        valid = recipient is None and target is None and action is None and clarification is None
    elif intent == "status":
        valid = recipient is None and action is None and clarification is None
    elif intent == "action":
        valid = recipient in RECIPIENTS and action in ALL_ACTIONS and clarification is None
    elif intent == "clarification":
        valid = recipient is None and action is None and clarification in CLARIFICATION_CODES
    elif intent in {"confirmation", "cancel"}:
        valid = recipient is None and target is None and action is None and clarification is None
    if not valid:
        raise NaturalLanguageError("invalid-classification")
    return dict(value)


def _validate_raw_text(value: Any) -> str:
    if not isinstance(value, str):
        raise NaturalLanguageError("message-text-not-string")
    if not value or len(value.encode("utf-8", "strict")) > MAX_RAW_TEXT_BYTES:
        raise NaturalLanguageError("message-text-size-invalid")
    if value != unicodedata.normalize("NFC", value):
        raise NaturalLanguageError("message-text-not-nfc")
    if value.count("\n") > 31 or any(
        character not in {"\n", "\t"}
        and unicodedata.category(character) in {"Cc", "Cf"}
        for character in value
    ):
        raise NaturalLanguageError("message-text-control-character")
    guard_text = unicodedata.normalize("NFKC", value).casefold()
    if "fidgeting_slack_request" in guard_text:
        raise NaturalLanguageError("message-text-reserved-marker")
    return value


def _native_event_context(
    event: Mapping[str, Any],
    *,
    bridge_store: AppendOnlyCommandStore,
    policy: CommandPolicy,
    workspace_host: str,
    poll_id: str,
    now: dt.datetime,
) -> tuple[str, str]:
    allowed = {
        "schemaVersion",
        "team_id",
        "user_id",
        "conversation_id",
        "event_id",
        "message_ts",
        "text",
    }
    if not isinstance(event, Mapping) or set(event) - allowed:
        raise NaturalLanguageError("invalid-native-event-fields")
    if event.get("schemaVersion") != SCHEMA_VERSION:
        raise NaturalLanguageError("unsupported-native-event-schema")
    if (
        event.get("team_id") != policy.team_id
        or event.get("user_id") != policy.user_id
        or event.get("conversation_id") != policy.conversation_id
    ):
        raise NaturalLanguageError("native-event-source-not-allowlisted")
    message_ts = event.get("message_ts")
    if not isinstance(message_ts, str) or not SLACK_NATIVE_TIMESTAMP.fullmatch(message_ts):
        raise NaturalLanguageError("invalid-native-message-timestamp")
    text = _validate_raw_text(event.get("text"))
    namespace_guard = unicodedata.normalize("NFKC", text).casefold().lstrip()
    if namespace_guard.startswith("fidget"):
        # The exact command bridge owns this namespace.  A malformed, extended,
        # or otherwise rejected command must never gain authority by falling
        # through to natural-language classification.
        raise NaturalLanguageError("reserved-command-prefix")
    raw_event_id = event.get("event_id")
    if raw_event_id is None:
        material = "\x1f".join(
            (policy.team_id, policy.conversation_id, message_ts)
        ).encode("utf-8", "strict")
        event_id = "slack:" + hashlib.sha256(material).hexdigest()
    elif isinstance(raw_event_id, str) and SLACK_EVENT_ID.fullmatch(raw_event_id):
        event_id = raw_event_id
    else:
        raise NaturalLanguageError("invalid-native-event-id")
    if not isinstance(workspace_host, str) or not SLACK_WORKSPACE_HOST.fullmatch(workspace_host):
        raise NaturalLanguageError("invalid-native-workspace-host")
    if not isinstance(poll_id, str) or not SLACK_POLL_ID.fullmatch(poll_id):
        raise NaturalLanguageError("invalid-native-poll-id")

    fingerprint, length = text_fingerprint(text)
    expected = canonical_json(
        {
            "teamId": policy.team_id,
            "userId": policy.user_id,
            "conversationId": policy.conversation_id,
            "messageTs": message_ts,
            "textSha256": fingerprint,
            "textLength": length,
        }
    )
    with bridge_store.locked():
        bridge_store._assert_authoritative_ledgers_unlocked()
        if bridge_store._stored_event_fingerprint(event_id) != expected:
            raise NaturalLanguageError("native-event-not-in-authoritative-ledger")
        poll = bridge_store._native_poll_state_unlocked()
    if not isinstance(poll, Mapping):
        raise NaturalLanguageError("native-poll-missing")
    required_match = (
        poll.get("source") == SLACK_NATIVE_CUA_SOURCE
        and poll.get("teamId") == policy.team_id
        and poll.get("userId") == policy.user_id
        and poll.get("conversationId") == policy.conversation_id
        and poll.get("workspaceHost") == workspace_host
        and poll.get("pollId") == poll_id
        and poll.get("outcome") == "verified"
        and poll.get("reason") == "continuous-stable-bottom"
        and poll.get("cursorConsistent") is True
        and isinstance(poll.get("eventCount"), int)
        and poll["eventCount"] > 0
    )
    if not required_match:
        raise NaturalLanguageError("native-poll-not-authoritative")
    try:
        recorded_at = parse_utc(poll.get("verifiedPollAt"))
        base = parse_slack_timestamp(poll.get("baseObservedThrough"))
        observed = parse_slack_timestamp(poll.get("observedThrough"))
        message_value = parse_slack_timestamp(message_ts)
        message_time = dt.datetime.fromtimestamp(float(message_ts), tz=dt.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError) as exc:
        raise NaturalLanguageError("native-poll-not-authoritative") from exc
    poll_age = (now - recorded_at).total_seconds()
    message_age = (now - message_time).total_seconds()
    if poll_age < -MAX_FUTURE_SKEW_SECONDS or poll_age > MAX_OBSERVATION_AGE_SECONDS:
        raise NaturalLanguageError("native-poll-not-fresh")
    if message_age < -MAX_FUTURE_SKEW_SECONDS or message_age > MAX_EVENT_AGE_SECONDS:
        raise NaturalLanguageError("native-message-not-fresh")
    if not base < message_value <= observed:
        raise NaturalLanguageError("native-event-not-in-current-poll-range")
    return event_id, text


def validate_observation(
    value: Mapping[str, Any],
    *,
    catalog: TaskCatalog,
    target_key: Optional[str],
    now: dt.datetime,
    require_dispatch_ui: bool,
) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
    if not isinstance(value, Mapping) or set(value) != OBSERVATION_KEYS:
        raise NaturalLanguageError("invalid-task-observation-fields")
    if value.get("schemaVersion") != SCHEMA_VERSION or value.get("catalogVersion") != catalog.version:
        raise NaturalLanguageError("task-observation-catalog-mismatch")
    inspection_id = value.get("inspectionId")
    lease_id = value.get("roundLeaseId")
    if (
        not _bounded_string(inspection_id, limit=80, pattern=INSPECTION_ID)
        or not _bounded_string(lease_id, limit=80, pattern=LEASE_ID)
        or not isinstance(value.get("userUiIdle"), bool)
    ):
        raise NaturalLanguageError("invalid-task-observation")
    try:
        observed_at = parse_utc(value.get("observedAt"))
    except (TypeError, ValueError) as exc:
        raise NaturalLanguageError("invalid-task-observation-time") from exc
    age = (now - observed_at).total_seconds()
    if age > MAX_OBSERVATION_AGE_SECONDS:
        raise NaturalLanguageError("stale-task-observation")
    if age < -MAX_FUTURE_SKEW_SECONDS:
        raise NaturalLanguageError("future-task-observation")
    controller = value.get("controller")
    expected_controller = dict(catalog.controller)
    if (
        not isinstance(controller, dict)
        or set(controller) != OBSERVED_CONTROLLER_KEYS
        or controller.get("status") not in CONTROLLER_STATES
        or any(controller.get(key) != expected for key, expected in expected_controller.items())
    ):
        raise NaturalLanguageError("task-controller-mismatch")
    rows = value.get("targets")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
        raise NaturalLanguageError("invalid-task-observation-targets")
    observed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != OBSERVED_TARGET_KEYS:
            raise NaturalLanguageError("invalid-task-observation-target")
        key = row.get("targetKey")
        configured = catalog.targets.get(key)
        if (
            configured is None
            or key in observed
            or row.get("backend") != configured.backend
            or row.get("threadId") != configured.thread_id
            or row.get("exactTitle") != configured.exact_title
            or row.get("authority") != configured.authority
            or row.get("state") not in TARGET_STATES
            or not _bounded_string(row.get("stateVersion"), limit=80, pattern=STATE_VERSION)
            or not isinstance(row.get("uiUnambiguous"), bool)
            or not isinstance(row.get("composerEmpty"), bool)
            or not isinstance(row.get("visible"), bool)
            or isinstance(row.get("exactTitleMatchCount"), bool)
            or not isinstance(row.get("exactTitleMatchCount"), int)
            or row.get("workspaceRoot") != catalog.controller["projectRoot"]
        ):
            raise NaturalLanguageError("task-observation-target-mismatch")
        observed[key] = dict(row)
    if set(observed) != set(catalog.targets):
        raise NaturalLanguageError("task-observation-incomplete")
    selected = observed.get(target_key) if target_key is not None else None
    if target_key is not None and selected is None:
        raise NaturalLanguageError("target-not-in-static-catalog")
    if require_dispatch_ui and selected is not None:
        if selected["state"] in {"complete", "archived"}:
            raise NaturalLanguageError("target-not-actionable")
        if (
            selected["uiUnambiguous"] is not True
            or selected["composerEmpty"] is not True
            or selected["visible"] is not True
            or selected["exactTitleMatchCount"] != 1
        ):
            raise NaturalLanguageError("target-ui-not-safe")
        if value["userUiIdle"] is not True:
            raise NaturalLanguageError("local-ui-in-use")
    return dict(value), selected


def _read_json_lines_strict(path: Path, error: str) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                raise NaturalLanguageError(error)
            try:
                value = json.loads(line)
            except ValueError as exc:
                raise NaturalLanguageError(error) from exc
            if not isinstance(value, dict):
                raise NaturalLanguageError(error)
            yield value


class NaturalLanguageStore:
    """Strict append-only metadata/intent/transition/reply ledgers."""

    def __init__(self, root: Path):
        self.root = root.expanduser().resolve(strict=False)
        self.event_path = self.root / "events.ndjson"
        self.intent_path = self.root / "intents.ndjson"
        self.transition_path = self.root / "transitions.ndjson"
        self.reply_path = self.root / "reply-deliveries.ndjson"
        self.lease_path = self.root / "leases.ndjson"
        self.key_path = self.root / "privacy.key"
        self.lock_path = self.root / ".lock"
        self.transient_root = self.root / "transient"

    def _prepare(self) -> None:
        if self.root.exists() and self.root.is_symlink():
            raise NaturalLanguageError("nl-runtime-root-is-symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        for path in (
            self.event_path,
            self.intent_path,
            self.transition_path,
            self.reply_path,
            self.lease_path,
            self.key_path,
            self.lock_path,
            self.transient_root,
        ):
            if path.is_symlink():
                raise NaturalLanguageError("nl-runtime-file-is-symlink")

    def _prepare_transient(self) -> None:
        self._prepare()
        self.transient_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.transient_root, 0o700)
        if self.transient_root.is_symlink():
            raise NaturalLanguageError("nl-transient-root-is-symlink")

    def _artifact_path(self, intent_id: str, kind: str) -> Path:
        if not isinstance(intent_id, str) or not INTENT_ID.fullmatch(intent_id):
            raise NaturalLanguageError("invalid-intent-id")
        if kind not in {"ticket", "envelope", "confirmation-preview"}:
            raise NaturalLanguageError("invalid-private-artifact-kind")
        return self.transient_root / "{}.{}.json".format(intent_id, kind)

    def _write_private_artifact(
        self, intent_id: str, kind: str, value: Mapping[str, Any]
    ) -> Path:
        self._prepare_transient()
        path = self._artifact_path(intent_id, kind)
        if path.exists() or path.is_symlink():
            raise NaturalLanguageError("private-artifact-already-exists")
        descriptor, temporary = tempfile.mkstemp(prefix=".nl-private-", dir=str(self.transient_root))
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            directory = os.open(str(self.transient_root), os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return path

    def _read_private_artifact(
        self, intent_id: str, kind: str, *, max_bytes: int = 16_384
    ) -> Mapping[str, Any]:
        self._prepare_transient()
        path = self._artifact_path(intent_id, kind)
        descriptor: Optional[int] = None
        try:
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(str(path), flags)
            info = os.fstat(descriptor)
            if (
                not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
                or info.st_size > max_bytes
            ):
                raise NaturalLanguageError("invalid-private-artifact")
            raw = os.read(descriptor, max_bytes + 1)
            if len(raw) > max_bytes:
                raise NaturalLanguageError("invalid-private-artifact")
            value = json.loads(raw.decode("utf-8", "strict"))
        except (OSError, ValueError) as exc:
            raise NaturalLanguageError("invalid-private-artifact") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
        if not isinstance(value, dict):
            raise NaturalLanguageError("invalid-private-artifact")
        return value

    def _delete_private_artifact(self, intent_id: str, kind: str) -> None:
        path = self._artifact_path(intent_id, kind)
        try:
            info = path.lstat()
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
            ):
                raise NaturalLanguageError("invalid-private-artifact")
            path.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise NaturalLanguageError("private-artifact-delete-failed") from exc

    def _expire_artifact_intent_unlocked(
        self, intent_id: str, kind: str, current: dt.datetime
    ) -> None:
        intents = {record["intentId"]: record for record in self._intent_records()}
        if intent_id not in intents:
            raise NaturalLanguageError("private-artifact-intent-missing")
        transitions = [
            record for record in self._transition_records() if record["intentId"] == intent_id
        ]
        latest = transitions[-1] if transitions else None
        if latest is not None and latest["outcome"] in {"dispatched", "refused", "unknown", "cancelled"}:
            return
        if latest is not None and latest["outcome"] == "claimed":
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-transition",
                "at": format_utc(current),
                "intentId": intent_id,
                "outcome": "unknown",
                "actor": "private-artifact-expiry",
                "leaseId": latest["leaseId"],
                "inspectionId": latest["inspectionId"],
                "stateVersion": latest["stateVersion"],
            }
        elif latest is None:
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-transition",
                "at": format_utc(current),
                "intentId": intent_id,
                "outcome": "refused",
                "actor": "private-artifact-expiry",
                "leaseId": None,
                "inspectionId": None,
                "stateVersion": None,
            }
        else:
            # A confirmed high-risk intent is not runnable in this native MVP;
            # expiry removes rather than broadens its authority.
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-transition",
                "at": format_utc(current),
                "intentId": intent_id,
                "outcome": "refused",
                "actor": "private-artifact-expiry",
                "leaseId": None,
                "inspectionId": None,
                "stateVersion": None,
            }
        self._append(self.transition_path, record)

    def _sweep_private_artifacts_unlocked(self, current: dt.datetime) -> dict[str, Any]:
        self._prepare_transient()
        removed: list[str] = []
        artifact_name = re.compile(
            r"^(intent_[A-Za-z0-9]{12,64})\.(ticket|envelope|confirmation-preview)\.json$"
        )
        for path in sorted(self.transient_root.iterdir(), key=lambda item: item.name):
            try:
                info = path.lstat()
            except OSError as exc:
                raise NaturalLanguageError("invalid-private-artifact-entry") from exc
            if (
                stat.S_ISLNK(info.st_mode)
                or not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600
            ):
                raise NaturalLanguageError("invalid-private-artifact-entry")
            if path.name.startswith(".nl-private-"):
                age = current.timestamp() - info.st_mtime
                if age > PRIVATE_TICKET_TTL_SECONDS:
                    path.unlink()
                    removed.append(path.name)
                continue
            match = artifact_name.fullmatch(path.name)
            if match is None:
                raise NaturalLanguageError("invalid-private-artifact-entry")
            intent_id, kind = match.groups()
            value = self._read_private_artifact(intent_id, kind)
            expected_keys = {
                "ticket": {"schemaVersion", "kind", "intentId", "createdAt", "requestText"},
                "envelope": {"schemaVersion", "kind", "intentId", "createdAt", "prompt"},
                "confirmation-preview": {
                    "schemaVersion", "kind", "intentId", "eventId", "createdAt", "confirmationToken"
                },
            }[kind]
            expected_kind = {
                "ticket": "route-ticket",
                "envelope": "dispatch-envelope",
                "confirmation-preview": "confirmation-preview",
            }[kind]
            if (
                set(value) != expected_keys
                or value.get("schemaVersion") != SCHEMA_VERSION
                or value.get("kind") != expected_kind
                or value.get("intentId") != intent_id
            ):
                raise NaturalLanguageError("invalid-private-artifact-entry")
            try:
                created = parse_utc(value.get("createdAt"))
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-private-artifact-entry") from exc
            age = (current - created).total_seconds()
            if age < -MAX_FUTURE_SKEW_SECONDS:
                raise NaturalLanguageError("future-private-artifact")
            ttl = {
                "ticket": PRIVATE_TICKET_TTL_SECONDS,
                "envelope": ROUND_LEASE_SECONDS,
                "confirmation-preview": CONFIRMATION_TTL_SECONDS,
            }[kind]
            if age <= ttl:
                continue
            self._expire_artifact_intent_unlocked(intent_id, kind, current)
            self._delete_private_artifact(intent_id, kind)
            removed.append(path.name)
        return {"schemaVersion": SCHEMA_VERSION, "removedCount": len(removed)}

    def sweep_private_artifacts(
        self, *, now: Optional[dt.datetime] = None
    ) -> dict[str, Any]:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            return self._sweep_private_artifacts_unlocked(current)

    def persist_route_private_material(
        self, prepared: PreparedRoute, *, now: Optional[dt.datetime] = None
    ) -> Optional[Path]:
        """Persist the minimum short-lived material needed by the next fixed step."""

        intent_id = prepared.public.get("intentId")
        if not isinstance(intent_id, str):
            return None
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        if prepared.request_text is not None:
            return self._write_private_artifact(
                intent_id,
                "ticket",
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "kind": "route-ticket",
                    "intentId": intent_id,
                    "createdAt": format_utc(current),
                    "requestText": prepared.request_text,
                },
            )
        if prepared.confirmation_token is not None:
            return self._write_private_artifact(
                intent_id,
                "confirmation-preview",
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "kind": "confirmation-preview",
                    "intentId": intent_id,
                    "eventId": prepared.public["eventId"],
                    "createdAt": format_utc(current),
                    "confirmationToken": prepared.confirmation_token,
                },
            )
        return None

    def claim_from_private_ticket(
        self,
        intent_id: str,
        *,
        observation: Mapping[str, Any],
        catalog: TaskCatalog,
        lease_id: str,
        now: Optional[dt.datetime] = None,
    ) -> tuple[PreparedRoute, Optional[Path]]:
        self.sweep_private_artifacts(now=now)
        ticket = self._read_private_artifact(intent_id, "ticket")
        if set(ticket) != {"schemaVersion", "kind", "intentId", "createdAt", "requestText"}:
            raise NaturalLanguageError("invalid-private-route-ticket")
        if (
            ticket.get("schemaVersion") != SCHEMA_VERSION
            or ticket.get("kind") != "route-ticket"
            or ticket.get("intentId") != intent_id
        ):
            raise NaturalLanguageError("invalid-private-route-ticket")
        try:
            created = parse_utc(ticket.get("createdAt"))
        except (TypeError, ValueError) as exc:
            raise NaturalLanguageError("invalid-private-route-ticket") from exc
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        if (current - created).total_seconds() > MAX_OBSERVATION_AGE_SECONDS:
            raise NaturalLanguageError("private-route-ticket-expired")
        prepared = self.claim_low_risk(
            intent_id,
            request_text=ticket.get("requestText"),
            observation=observation,
            catalog=catalog,
            lease_id=lease_id,
            now=current,
        )
        if prepared.request_text is None:
            return prepared, None
        envelope_path = self._write_private_artifact(
            intent_id,
            "envelope",
            {
                "schemaVersion": SCHEMA_VERSION,
                "kind": "dispatch-envelope",
                "intentId": intent_id,
                "createdAt": format_utc(current),
                "prompt": forwarded_transcript_prompt(prepared.request_text),
            },
        )
        self._delete_private_artifact(intent_id, "ticket")
        return prepared, envelope_path

    @contextlib.contextmanager
    def locked(self) -> Iterator[None]:
        self._prepare()
        descriptor = os.open(str(self.lock_path), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    @staticmethod
    def _append(path: Path, record: Mapping[str, Any]) -> None:
        payload = (canonical_json(record) + "\n").encode("utf-8")
        descriptor = os.open(str(path), os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise NaturalLanguageError("nl-append-failed")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.chmod(path, 0o600)

    def _privacy_key_unlocked(self) -> bytes:
        if self.key_path.exists():
            try:
                if self.key_path.is_symlink() or self.key_path.stat().st_mode & 0o077:
                    raise NaturalLanguageError("nl-privacy-key-invalid")
                key = self.key_path.read_bytes()
            except OSError as exc:
                raise NaturalLanguageError("nl-privacy-key-invalid") from exc
            if len(key) != 32:
                raise NaturalLanguageError("nl-privacy-key-invalid")
            return key
        if any(path.exists() for path in (self.event_path, self.intent_path, self.transition_path)):
            raise NaturalLanguageError("nl-privacy-key-missing")
        key = os.urandom(32)
        descriptor = os.open(str(self.key_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(descriptor, key)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        return key

    @staticmethod
    def _mac(key: bytes, purpose: str, value: str) -> str:
        return hmac.new(key, (purpose + "\x00" + value).encode("utf-8"), hashlib.sha256).hexdigest()

    def _event_records(self) -> list[dict[str, Any]]:
        required = {
            "schemaVersion", "recordType", "at", "eventId", "messageTs",
            "teamId", "userId", "conversationId", "intent", "targetKey",
            "recipient", "action", "clarificationCode", "outcome", "reason", "intentId",
        }
        records = list(_read_json_lines_strict(self.event_path, "invalid-nl-event-ledger"))
        seen: set[str] = set()
        for record in records:
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-nl-event-ledger") from exc
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "nl-event"
                or not isinstance(record.get("eventId"), str)
                or not SLACK_EVENT_ID.fullmatch(record["eventId"])
                or record["eventId"] in seen
                or not isinstance(record.get("messageTs"), str)
                or not SLACK_NATIVE_TIMESTAMP.fullmatch(record["messageTs"])
                or not isinstance(record.get("teamId"), str)
                or not SLACK_TEAM_ID.fullmatch(record["teamId"])
                or not isinstance(record.get("userId"), str)
                or not SLACK_USER_ID.fullmatch(record["userId"])
                or not isinstance(record.get("conversationId"), str)
                or not SLACK_CONVERSATION_ID.fullmatch(record["conversationId"])
                or record.get("intent") not in INTENTS
                or record.get("outcome") not in {"reply-pending", "dispatch-pending", "confirmation-pending", "cancelled", "refused"}
                or record.get("reason") not in NL_EVENT_REASONS
            ):
                raise NaturalLanguageError("invalid-nl-event-ledger")
            seen.add(record["eventId"])
        return records

    def _intent_records(self) -> list[dict[str, Any]]:
        required = {
            "schemaVersion", "recordType", "at", "intentId", "sourceEventId",
            "teamId", "userId", "conversationId", "targetKey", "targetTitle",
            "controllerThreadId", "controllerHostId", "projectRoot", "recipient", "action",
            "risk", "authority", "catalogVersion", "inspectionId", "stateVersion",
            "requestMac", "intentDigest", "confirmationTokenMac", "expiresAt",
            "policyVersion",
        }
        records = list(_read_json_lines_strict(self.intent_path, "invalid-nl-intent-ledger"))
        seen: set[str] = set()
        source_events: set[str] = set()
        for record in records:
            try:
                parsed_at = parse_utc(record.get("at"))
                if record.get("expiresAt") is not None:
                    parse_utc(record["expiresAt"])
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-nl-intent-ledger") from exc
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "nl-intent"
                or not isinstance(record.get("intentId"), str)
                or not INTENT_ID.fullmatch(record["intentId"])
                or record["intentId"] in seen
                or record.get("sourceEventId") in source_events
                or not isinstance(record.get("sourceEventId"), str)
                or not SLACK_EVENT_ID.fullmatch(record["sourceEventId"])
                or not isinstance(record.get("teamId"), str)
                or not SLACK_TEAM_ID.fullmatch(record["teamId"])
                or not isinstance(record.get("userId"), str)
                or not SLACK_USER_ID.fullmatch(record["userId"])
                or not isinstance(record.get("conversationId"), str)
                or not SLACK_CONVERSATION_ID.fullmatch(record["conversationId"])
                or record.get("action") not in ALL_ACTIONS
                or record.get("risk") not in {"low", "high"}
                or record.get("policyVersion") != POLICY_VERSION
                or not _bounded_string(record.get("targetKey"), limit=80, pattern=TARGET_KEY)
                or not _bounded_string(record.get("targetTitle"), limit=120)
                or not _bounded_string(record.get("controllerThreadId"), limit=128, pattern=THREAD_ID)
                or record.get("controllerHostId") != "local"
                or record.get("recipient") not in RECIPIENTS
                or not isinstance(record.get("projectRoot"), str)
                or not Path(record["projectRoot"]).is_absolute()
                or record.get("authority") not in {"inspect-only", "allowlisted-safe"}
                or not _bounded_string(record.get("catalogVersion"), limit=80, pattern=TARGET_KEY)
                or not _bounded_string(record.get("inspectionId"), limit=80, pattern=INSPECTION_ID)
                or not _bounded_string(record.get("stateVersion"), limit=80, pattern=STATE_VERSION)
                or not isinstance(record.get("requestMac"), str)
                or not SHA256_HEX.fullmatch(record["requestMac"])
                or not isinstance(record.get("intentDigest"), str)
                or not SHA256_HEX.fullmatch(record["intentDigest"])
                or (
                    record["risk"] == "high"
                    and not isinstance(record.get("confirmationTokenMac"), str)
                )
                or (
                    record["risk"] == "low"
                    and (record.get("confirmationTokenMac") is not None or record.get("expiresAt") is not None)
                )
            ):
                raise NaturalLanguageError("invalid-nl-intent-ledger")
            if record.get("confirmationTokenMac") is not None and not SHA256_HEX.fullmatch(record["confirmationTokenMac"]):
                raise NaturalLanguageError("invalid-nl-intent-ledger")
            if (record["action"] in SAFE_ACTIONS) != (record["risk"] == "low"):
                raise NaturalLanguageError("invalid-nl-intent-ledger")
            if record["risk"] == "high" and (
                record.get("expiresAt") is None
                or parse_utc(record["expiresAt"]) <= parsed_at
            ):
                raise NaturalLanguageError("invalid-nl-intent-ledger")
            binding = {
                key: record[key]
                for key in (
                    "sourceEventId",
                    "teamId",
                    "userId",
                    "conversationId",
                    "targetKey",
                    "targetTitle",
                    "controllerThreadId",
                    "controllerHostId",
                    "projectRoot",
                    "recipient",
                    "action",
                    "risk",
                    "authority",
                    "catalogVersion",
                    "inspectionId",
                    "stateVersion",
                    "requestMac",
                    "policyVersion",
                )
            }
            if not hmac.compare_digest(
                hashlib.sha256(canonical_json(binding).encode("utf-8", "strict")).hexdigest(),
                record["intentDigest"],
            ):
                raise NaturalLanguageError("invalid-nl-intent-ledger")
            seen.add(record["intentId"])
            source_events.add(record["sourceEventId"])
        return records

    def _transition_records(self) -> list[dict[str, Any]]:
        required = {
            "schemaVersion", "recordType", "at", "intentId", "outcome", "actor",
            "leaseId", "inspectionId", "stateVersion",
        }
        records = list(_read_json_lines_strict(self.transition_path, "invalid-nl-transition-ledger"))
        states: dict[str, dict[str, Any]] = {}
        for record in records:
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-nl-transition-ledger") from exc
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "nl-transition"
                or not isinstance(record.get("intentId"), str)
                or not INTENT_ID.fullmatch(record["intentId"])
                or record.get("outcome") not in {"confirmed", "claimed", "cancelled", "dispatched", "refused", "unknown"}
                or not isinstance(record.get("actor"), str)
                or len(record["actor"]) > 80
            ):
                raise NaturalLanguageError("invalid-nl-transition-ledger")
            previous_record = states.get(record["intentId"])
            previous = previous_record["outcome"] if previous_record is not None else None
            outcome = record["outcome"]
            valid_transition = (
                (previous is None and outcome in {"confirmed", "claimed", "cancelled", "refused"})
                or (previous == "confirmed" and outcome in {"claimed", "cancelled", "refused"})
                or (previous == "claimed" and outcome in {"dispatched", "refused", "unknown"})
            )
            if not valid_transition:
                raise NaturalLanguageError("invalid-nl-transition-ledger")
            if outcome == "claimed" and (
                not isinstance(record.get("leaseId"), str)
                or not LEASE_ID.fullmatch(record["leaseId"])
                or not isinstance(record.get("inspectionId"), str)
                or not INSPECTION_ID.fullmatch(record["inspectionId"])
                or not isinstance(record.get("stateVersion"), str)
                or not STATE_VERSION.fullmatch(record["stateVersion"])
            ):
                raise NaturalLanguageError("invalid-nl-transition-ledger")
            if outcome in {"dispatched", "unknown"} and (
                previous_record is None
                or record.get("leaseId") != previous_record.get("leaseId")
                or record.get("inspectionId") != previous_record.get("inspectionId")
                or record.get("stateVersion") != previous_record.get("stateVersion")
            ):
                raise NaturalLanguageError("invalid-nl-transition-ledger")
            if outcome == "cancelled" and any(
                record.get(key) is not None
                for key in ("leaseId", "inspectionId", "stateVersion")
            ):
                raise NaturalLanguageError("invalid-nl-transition-ledger")
            states[record["intentId"]] = record
        return records

    def _lease_records(self) -> list[dict[str, Any]]:
        required = {"schemaVersion", "recordType", "at", "leaseId", "outcome", "expiresAt"}
        records = list(_read_json_lines_strict(self.lease_path, "invalid-nl-lease-ledger"))
        for record in records:
            try:
                parse_utc(record.get("at"))
                parse_utc(record.get("expiresAt"))
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-nl-lease-ledger") from exc
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "nl-lease"
                or not isinstance(record.get("leaseId"), str)
                or not LEASE_ID.fullmatch(record["leaseId"])
                or record.get("outcome") not in {"acquired", "released"}
            ):
                raise NaturalLanguageError("invalid-nl-lease-ledger")
        return records

    def _reply_records(self) -> list[dict[str, Any]]:
        required = {
            "schemaVersion", "recordType", "at", "eventId", "replyKind",
            "outcome", "reason", "httpStatus",
        }
        records = list(_read_json_lines_strict(self.reply_path, "invalid-nl-reply-ledger"))
        states: dict[tuple[str, str], str] = {}
        for record in records:
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError) as exc:
                raise NaturalLanguageError("invalid-nl-reply-ledger") from exc
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "nl-reply"
                or not isinstance(record.get("eventId"), str)
                or not SLACK_EVENT_ID.fullmatch(record["eventId"])
                or record.get("replyKind") not in {"chat", "status", "clarification", "confirmation-preview", "receipt"}
                or record.get("outcome") not in {"claimed", "delivered", "failed", "unknown"}
            ):
                raise NaturalLanguageError("invalid-nl-reply-ledger")
            outcome = record["outcome"]
            reason = record.get("reason")
            status = record.get("httpStatus")
            if outcome == "claimed":
                record_valid = reason == "claimed-before-post" and status is None
            else:
                record_valid = reason in REPLY_FINAL_REASONS[outcome] and (
                    (outcome == "delivered" and status == 200)
                    or (outcome == "unknown" and status is None)
                    or (
                        outcome == "failed"
                        and isinstance(status, int)
                        and not isinstance(status, bool)
                        and 100 <= status <= 599
                    )
                )
            if not record_valid:
                raise NaturalLanguageError("invalid-nl-reply-ledger")
            key = (record["eventId"], record["replyKind"])
            previous = states.get(key)
            if (previous is None and record["outcome"] != "claimed") or (
                previous is not None
                and not (
                    previous == "claimed"
                    and record["outcome"] in {"delivered", "failed", "unknown"}
                )
            ):
                raise NaturalLanguageError("invalid-nl-reply-ledger")
            states[key] = record["outcome"]
        return records

    def _assert_ledgers_unlocked(self) -> None:
        events = self._event_records()
        intents = self._intent_records()
        self._transition_records()
        self._lease_records()
        self._reply_records()
        intents_by_id = {record["intentId"]: record for record in intents}
        for event in events:
            intent_id = event.get("intentId")
            if intent_id is None:
                continue
            intent = intents_by_id.get(intent_id)
            if intent is None:
                raise NaturalLanguageError("invalid-nl-event-intent-binding")
            if (
                intent.get("sourceEventId") != event["eventId"]
                or intent.get("teamId") != event["teamId"]
                or intent.get("userId") != event["userId"]
                or intent.get("conversationId") != event["conversationId"]
                or intent.get("targetKey") != event["targetKey"]
                or intent.get("recipient") != event["recipient"]
                or intent.get("action") != event["action"]
            ):
                raise NaturalLanguageError("invalid-nl-event-intent-binding")

    def acquire_round_lease(self, lease_id: str, *, now: Optional[dt.datetime] = None) -> dict[str, Any]:
        if not isinstance(lease_id, str) or not LEASE_ID.fullmatch(lease_id):
            raise NaturalLanguageError("invalid-round-lease-id")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            self._sweep_private_artifacts_unlocked(current)
            transition_state: dict[str, str] = {}
            for transition in self._transition_records():
                transition_state[transition["intentId"]] = transition["outcome"]
            if any(outcome == "claimed" for outcome in transition_state.values()):
                raise NaturalLanguageError("dispatch-outcome-unknown")
            active: Optional[dict[str, Any]] = None
            for record in self._lease_records():
                if record["outcome"] == "acquired":
                    active = record
                elif active is not None and record["leaseId"] == active["leaseId"]:
                    active = None
            if active is not None and parse_utc(active["expiresAt"]) > current:
                if active["leaseId"] == lease_id:
                    return {"acquired": True, "duplicate": True, "leaseId": lease_id}
                raise NaturalLanguageError("round-lease-held")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-lease",
                "at": format_utc(current),
                "leaseId": lease_id,
                "outcome": "acquired",
                "expiresAt": format_utc(current + dt.timedelta(seconds=ROUND_LEASE_SECONDS)),
            }
            self._append(self.lease_path, record)
            return {"acquired": True, "duplicate": False, "leaseId": lease_id}

    def _require_active_lease_unlocked(self, lease_id: str, current: dt.datetime) -> None:
        active: Optional[dict[str, Any]] = None
        for record in self._lease_records():
            if record["outcome"] == "acquired":
                active = record
            elif active is not None and record["leaseId"] == active["leaseId"]:
                active = None
        if (
            active is None
            or active["leaseId"] != lease_id
            or parse_utc(active["expiresAt"]) <= current
        ):
            raise NaturalLanguageError("round-lease-not-active")

    def release_round_lease(self, lease_id: str, *, now: Optional[dt.datetime] = None) -> dict[str, Any]:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            self._require_active_lease_unlocked(lease_id, current)
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-lease",
                "at": format_utc(current),
                "leaseId": lease_id,
                "outcome": "released",
                "expiresAt": format_utc(current),
            }
            self._append(self.lease_path, record)
            return {"released": True, "leaseId": lease_id}

    def route_native(
        self,
        event: Mapping[str, Any],
        classification: Mapping[str, Any],
        *,
        bridge_store: AppendOnlyCommandStore,
        policy: CommandPolicy,
        workspace_host: str,
        poll_id: str,
        catalog: TaskCatalog,
        observation: Optional[Mapping[str, Any]] = None,
        now: Optional[dt.datetime] = None,
    ) -> PreparedRoute:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        event_id, text = _native_event_context(
            event,
            bridge_store=bridge_store,
            policy=policy,
            workspace_host=workspace_host,
            poll_id=poll_id,
            now=current,
        )
        classified = validate_classification(classification)
        intent = classified["intent"]
        recipient = classified.get("recipient")
        target_key = classified.get("targetKey")
        action = classified.get("action")
        clarification = classified.get("clarificationCode")

        confirmation_match = CONFIRM_MESSAGE.fullmatch(text)
        cancel_match = CANCEL_MESSAGE.fullmatch(text)
        if intent == "confirmation" and confirmation_match is None:
            raise NaturalLanguageError("confirmation-message-not-exact")
        if intent == "cancel" and cancel_match is None:
            raise NaturalLanguageError("cancel-message-not-exact")
        if intent not in {"confirmation", "cancel"} and (confirmation_match or cancel_match):
            raise NaturalLanguageError("reserved-message-misclassified")

        selected: Optional[dict[str, Any]] = None
        checked_observation: Optional[dict[str, Any]] = None
        if intent in {"status", "action"}:
            if observation is None:
                raise NaturalLanguageError("fresh-task-observation-required")
            checked_observation, selected = validate_observation(
                observation,
                catalog=catalog,
                target_key=target_key,
                now=current,
                require_dispatch_ui=intent == "action" and action in SAFE_ACTIONS,
            )

        outcome = "reply-pending"
        reason = intent
        intent_id: Optional[str] = None
        confirmation_token: Optional[str] = None
        request_text: Optional[str] = None
        public: dict[str, Any] = {
            "schemaVersion": SCHEMA_VERSION,
            "eventId": event_id,
            "intent": intent,
            "recipient": recipient,
            "targetKey": target_key,
            "action": action,
            "replyKind": None,
            "dispatchReady": False,
            "confirmationRequired": False,
            "nativeConfirmationAccepted": False,
            "intentId": None,
            "reason": reason,
        }

        with self.locked():
            self._assert_ledgers_unlocked()
            self._sweep_private_artifacts_unlocked(current)
            key = self._privacy_key_unlocked()
            existing = next((r for r in self._event_records() if r["eventId"] == event_id), None)
            if existing is not None:
                return PreparedRoute(
                    public={
                        "schemaVersion": SCHEMA_VERSION,
                        "eventId": event_id,
                        "duplicate": True,
                        "intent": existing["intent"],
                        "recipient": existing["recipient"],
                        "targetKey": existing["targetKey"],
                        "action": existing["action"],
                        "intentId": existing["intentId"],
                        "dispatchReady": False,
                        "confirmationRequired": existing["outcome"] == "confirmation-pending",
                        "nativeConfirmationAccepted": False,
                        "replyKind": None,
                        "reason": "duplicate-event",
                    }
                )

            orphan_intent = next(
                (r for r in self._intent_records() if r["sourceEventId"] == event_id),
                None,
            )
            if orphan_intent is not None:
                # A crash between the intent and event appends is treated as an
                # unknown one-shot outcome.  Never mint another intent/token.
                if (
                    orphan_intent.get("teamId") != policy.team_id
                    or orphan_intent.get("userId") != policy.user_id
                    or orphan_intent.get("conversationId") != policy.conversation_id
                    or orphan_intent.get("targetKey") != target_key
                    or orphan_intent.get("recipient") != recipient
                    or orphan_intent.get("action") != action
                ):
                    raise NaturalLanguageError("prior-route-binding-mismatch")
                event_record = {
                    "schemaVersion": SCHEMA_VERSION,
                    "recordType": "nl-event",
                    "at": format_utc(current),
                    "eventId": event_id,
                    "messageTs": event["message_ts"],
                    "teamId": policy.team_id,
                    "userId": policy.user_id,
                    "conversationId": policy.conversation_id,
                    "intent": intent,
                    "recipient": recipient,
                    "targetKey": target_key,
                    "action": action,
                    "clarificationCode": clarification,
                    "outcome": "refused",
                    "reason": "prior-route-incomplete-resend",
                    "intentId": orphan_intent["intentId"],
                }
                self._append(self.event_path, event_record)
                return PreparedRoute(
                    public={
                        "schemaVersion": SCHEMA_VERSION,
                        "eventId": event_id,
                        "duplicate": True,
                        "intent": intent,
                        "recipient": recipient,
                        "targetKey": target_key,
                        "action": action,
                        "intentId": orphan_intent["intentId"],
                        "dispatchReady": False,
                        "confirmationRequired": False,
                        "nativeConfirmationAccepted": False,
                        "replyKind": "receipt",
                        "reason": "prior-route-incomplete-resend",
                    }
                )

            if intent == "confirmation":
                # Native CUA has only indirect author identity.  It can never
                # turn a confirmation capability into execution authority.
                outcome = "refused"
                reason = "direct-confirmation-required"
                public.update({"reason": reason, "replyKind": "receipt"})
            elif intent == "cancel":
                referenced = cancel_match.group(1) if cancel_match else ""
                intents = {record["intentId"]: record for record in self._intent_records()}
                if referenced not in intents:
                    outcome = "refused"
                    reason = "cancel-target-not-found"
                else:
                    transitions = [r for r in self._transition_records() if r["intentId"] == referenced]
                    latest_transition = transitions[-1] if transitions else None
                    if latest_transition is not None and latest_transition["outcome"] == "cancelled":
                        # A crash can occur after the revocation transition is
                        # durable but before this cancel event is recorded.
                        # Treat that exact retry as idempotent: a second
                        # cancelled transition would corrupt the strict ledger.
                        outcome = "cancelled"
                        reason = "cancelled"
                    elif latest_transition is None or latest_transition["outcome"] == "confirmed":
                        outcome = "cancelled"
                        reason = "cancelled"
                        self._append(
                            self.transition_path,
                            {
                                "schemaVersion": SCHEMA_VERSION,
                                "recordType": "nl-transition",
                                "at": format_utc(current),
                                "intentId": referenced,
                                "outcome": "cancelled",
                                "actor": "native-self-dm-revocation",
                                "leaseId": None,
                                "inspectionId": None,
                                "stateVersion": None,
                            },
                        )
                    else:
                        outcome = "refused"
                        reason = "cancel-too-late"
                public["reason"] = reason
                public["replyKind"] = "receipt"
            elif intent == "chat":
                public["replyKind"] = "chat"
            elif intent == "status":
                public["replyKind"] = "status"
                public["inspectionId"] = checked_observation["inspectionId"]
            elif intent == "clarification":
                reason = clarification
                public["replyKind"] = "clarification"
                public["clarificationCode"] = clarification
                public["reason"] = reason
            elif intent == "action":
                if target_key is None or selected is None:
                    outcome = "reply-pending"
                    reason = "target-ambiguous"
                    public.update(
                        {
                            "intent": "clarification",
                            "replyKind": "clarification",
                            "clarificationCode": "target-ambiguous",
                            "reason": reason,
                        }
                    )
                elif action != "inspect-state" and selected["authority"] == "inspect-only":
                    outcome = "refused"
                    reason = "target-authority-inspect-only"
                    public.update({"replyKind": "receipt", "reason": reason})
                elif recipient == "codex" and action != "inspect-state":
                    # This MVP has no immutable target->argv test catalog and
                    # no safe Codex continuation executor.  Do not make the
                    # controller invent tool arguments or mirror Cursor-side
                    # authority implicitly.
                    outcome = "refused"
                    reason = "recipient-action-not-allowed"
                    public.update({"replyKind": "receipt", "reason": reason})
                else:
                    risk = "low" if action in SAFE_ACTIONS else "high"
                    intent_id = "intent_" + secrets.token_hex(12)
                    request_mac = self._mac(key, "request", text)
                    token_mac: Optional[str] = None
                    expires_at: Optional[str] = None
                    if risk == "high":
                        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
                        confirmation_token = "".join(secrets.choice(alphabet) for _ in range(6))
                        token_mac = self._mac(key, "confirmation-token", confirmation_token)
                        expires_at = format_utc(
                            current + dt.timedelta(seconds=CONFIRMATION_TTL_SECONDS)
                        )
                    binding = {
                        "sourceEventId": event_id,
                        "teamId": policy.team_id,
                        "userId": policy.user_id,
                        "conversationId": policy.conversation_id,
                        "targetKey": target_key,
                        "targetTitle": selected["exactTitle"],
                        "controllerThreadId": catalog.controller["threadId"],
                        "controllerHostId": catalog.controller["hostId"],
                        "projectRoot": catalog.controller["projectRoot"],
                        "recipient": recipient,
                        "action": action,
                        "risk": risk,
                        "authority": selected["authority"],
                        "catalogVersion": catalog.version,
                        "inspectionId": checked_observation["inspectionId"],
                        "stateVersion": selected["stateVersion"],
                        "requestMac": request_mac,
                        "policyVersion": POLICY_VERSION,
                    }
                    intent_digest = hashlib.sha256(
                        canonical_json(binding).encode("utf-8", "strict")
                    ).hexdigest()
                    self._append(
                        self.intent_path,
                        {
                            "schemaVersion": SCHEMA_VERSION,
                            "recordType": "nl-intent",
                            "at": format_utc(current),
                            "intentId": intent_id,
                            **binding,
                            "intentDigest": intent_digest,
                            "confirmationTokenMac": token_mac,
                            "expiresAt": expires_at,
                        },
                    )
                    public.update(
                        {
                            "intentId": intent_id,
                            "risk": risk,
                            "inspectionId": checked_observation["inspectionId"],
                            "stateVersion": selected["stateVersion"],
                        }
                    )
                    if risk == "low":
                        outcome = "dispatch-pending"
                        reason = "low-risk-awaiting-atomic-claim"
                        request_text = text
                        public.update({"dispatchReady": True, "replyKind": "receipt", "reason": reason})
                    else:
                        outcome = "confirmation-pending"
                        reason = "direct-confirmation-required"
                        public.update(
                            {
                                "confirmationRequired": True,
                                "replyKind": "confirmation-preview",
                                "reason": reason,
                                "confirmationExpiresAt": expires_at,
                            }
                        )

            event_record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-event",
                "at": format_utc(current),
                "eventId": event_id,
                "messageTs": event["message_ts"],
                "teamId": policy.team_id,
                "userId": policy.user_id,
                "conversationId": policy.conversation_id,
                "intent": intent,
                "recipient": recipient,
                "targetKey": target_key,
                "action": action,
                "clarificationCode": clarification,
                "outcome": outcome,
                "reason": reason,
                "intentId": intent_id,
            }
            self._append(self.event_path, event_record)
        public["duplicate"] = False
        return PreparedRoute(
            public=public,
            request_text=request_text,
            confirmation_token=confirmation_token,
        )

    def claim_low_risk(
        self,
        intent_id: str,
        *,
        request_text: str,
        observation: Mapping[str, Any],
        catalog: TaskCatalog,
        lease_id: str,
        now: Optional[dt.datetime] = None,
    ) -> PreparedRoute:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        request_text = _validate_raw_text(request_text)
        with self.locked():
            self._assert_ledgers_unlocked()
            self._require_active_lease_unlocked(lease_id, current)
            intents = {record["intentId"]: record for record in self._intent_records()}
            intent = intents.get(intent_id)
            if intent is None:
                raise NaturalLanguageError("intent-not-found")
            if intent["risk"] != "low" or intent["action"] not in SAFE_ACTIONS:
                raise NaturalLanguageError("intent-not-low-risk")
            source_event = next(
                (record for record in self._event_records() if record["eventId"] == intent["sourceEventId"]),
                None,
            )
            if (
                source_event is None
                or source_event.get("intentId") != intent_id
                or source_event.get("outcome") != "dispatch-pending"
                or source_event.get("targetKey") != intent["targetKey"]
                or source_event.get("recipient") != intent["recipient"]
                or source_event.get("action") != intent["action"]
                or source_event.get("teamId") != intent["teamId"]
                or source_event.get("userId") != intent["userId"]
                or source_event.get("conversationId") != intent["conversationId"]
            ):
                raise NaturalLanguageError("intent-source-event-not-dispatchable")
            configured = catalog.targets.get(intent["targetKey"])
            if (
                catalog.version != intent["catalogVersion"]
                or configured is None
                or configured.exact_title != intent["targetTitle"]
                or configured.authority != intent["authority"]
                or catalog.controller["threadId"] != intent["controllerThreadId"]
                or catalog.controller["hostId"] != intent["controllerHostId"]
                or catalog.controller["projectRoot"] != intent["projectRoot"]
            ):
                raise NaturalLanguageError("intent-catalog-binding-changed")
            transitions = [r for r in self._transition_records() if r["intentId"] == intent_id]
            if transitions:
                return PreparedRoute(
                    public={
                        "schemaVersion": SCHEMA_VERSION,
                        "intentId": intent_id,
                        "claimed": False,
                        "duplicate": True,
                        "dispatchEnvelopeAvailable": False,
                        "reason": "intent-already-transitioned",
                    }
                )
            checked, selected = validate_observation(
                observation,
                catalog=catalog,
                target_key=intent["targetKey"],
                now=current,
                require_dispatch_ui=True,
            )
            if checked["roundLeaseId"] != lease_id:
                raise NaturalLanguageError("observation-lease-mismatch")
            if checked["inspectionId"] == intent["inspectionId"]:
                raise NaturalLanguageError("dispatch-reinspection-required")
            if parse_utc(checked["observedAt"]) <= parse_utc(intent["at"]):
                raise NaturalLanguageError("dispatch-reinspection-required")
            if (
                selected is None
                or selected["stateVersion"] != intent["stateVersion"]
            ):
                raise NaturalLanguageError("task-state-changed")
            key = self._privacy_key_unlocked()
            if not hmac.compare_digest(
                self._mac(key, "request", request_text), intent["requestMac"]
            ):
                raise NaturalLanguageError("request-does-not-match-intent")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-transition",
                "at": format_utc(current),
                "intentId": intent_id,
                "outcome": "claimed",
                "actor": "fidgeting-slack-nl-controller",
                "leaseId": lease_id,
                "inspectionId": checked["inspectionId"],
                "stateVersion": selected["stateVersion"],
            }
            self._append(self.transition_path, record)
            envelope = {
                "schemaVersion": SCHEMA_VERSION,
                "provenance": {
                    "kind": FORWARD_PROVENANCE,
                    "eventId": intent["sourceEventId"],
                    "intentId": intent_id,
                    "policyVersion": POLICY_VERSION,
                },
                "controller": {
                    "backend": "codex",
                    "threadId": intent["controllerThreadId"],
                    "hostId": intent["controllerHostId"],
                    "projectRoot": intent["projectRoot"],
                },
                "target": {
                    "backend": (
                        "codex-current-turn"
                        if intent["recipient"] == "codex"
                        else "cursor-native"
                    ),
                    "threadId": (
                        intent["controllerThreadId"]
                        if intent["recipient"] == "codex"
                        else None
                    ),
                    "targetKey": intent["targetKey"],
                    "exactTitle": intent["targetTitle"],
                    "stateVersion": intent["stateVersion"],
                },
                "authority": {
                    "action": intent["action"],
                    "ceiling": (
                        "read-only"
                        if intent["action"] == "inspect-state"
                        else (
                            "fixed-test-suite-only"
                            if intent["action"] == "run-fixed-tests"
                            else "existing-supervisor-allowlist-only"
                        )
                    ),
                    "neverAuthorized": [
                        "arbitrary-shell-or-tool-arguments",
                        "credential-or-permission-change",
                        "delete-or-destructive-git",
                        "external-send-push-deploy-install",
                        "gate-visual-device-or-payment-approval",
                        "new-task-fork-or-handoff",
                        "control-plane-or-automation-edit",
                    ],
                    "protectedPaths": [
                        ".cursor/hooks/**",
                        ".cursor/runtime/**",
                        ".codex/automations/**",
                        "tools/cursor-night-supervisor/**",
                        "~/.cursor/slack-progress.env",
                        "Slack root-state.json",
                    ],
                },
                "untrustedSlackRequest": request_text,
                "dispatchContract": {
                    "mode": (
                        "execute-in-current-heartbeat-turn"
                        if intent["recipient"] == "codex"
                        else "cursor-native-verified-composer"
                    ),
                    "sendMessageToControllerThread": False,
                    "cursorChecks": (
                        []
                        if intent["recipient"] == "codex"
                        else [
                            "unique-visible-exact-title",
                            "same-workspace-root",
                            "empty-composer",
                            "readback-before-explicit-send",
                            "post-send-proof",
                        ]
                    ),
                },
            }
            return PreparedRoute(
                public={
                    "schemaVersion": SCHEMA_VERSION,
                    "intentId": intent_id,
                    "claimed": True,
                    "duplicate": False,
                    "dispatchEnvelopeAvailable": True,
                    "controllerThreadId": intent["controllerThreadId"],
                    "targetKey": intent["targetKey"],
                    "reason": "claimed-before-dispatch",
                },
                request_text=canonical_json(envelope),
            )

    def finalize_dispatch(
        self,
        intent_id: str,
        lease_id: str,
        outcome: str,
        *,
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        if outcome not in {"dispatched", "refused", "unknown"}:
            raise NaturalLanguageError("invalid-dispatch-outcome")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            records = [r for r in self._transition_records() if r["intentId"] == intent_id]
            if not records or records[-1]["outcome"] != "claimed" or records[-1]["leaseId"] != lease_id:
                raise NaturalLanguageError("intent-not-claimed-by-lease")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "nl-transition",
                "at": format_utc(current),
                "intentId": intent_id,
                "outcome": outcome,
                "actor": "fidgeting-slack-nl-controller",
                "leaseId": lease_id,
                "inspectionId": records[-1]["inspectionId"],
                "stateVersion": records[-1]["stateVersion"],
            }
            self._append(self.transition_path, record)
            self._delete_private_artifact(intent_id, "envelope")
            return {"schemaVersion": SCHEMA_VERSION, "intentId": intent_id, "outcome": outcome}

    def pending_reply(self, event_id: str, reply_kind: str) -> dict[str, Any]:
        with self.locked():
            self._assert_ledgers_unlocked()
            event = next((r for r in self._event_records() if r["eventId"] == event_id), None)
            if event is None:
                raise NaturalLanguageError("reply-event-not-found")
            allowed = {
                "chat": {"chat"},
                "status": {"status"},
                "clarification": {"clarification", "action"},
                "confirmation-preview": {"action"},
                "receipt": {"action", "cancel", "confirmation"},
            }
            if event["intent"] not in allowed.get(reply_kind, set()):
                raise NaturalLanguageError("reply-kind-does-not-match-event")
            if not self._event_allows_reply(event, reply_kind):
                raise NaturalLanguageError("reply-not-pending")
            return dict(event)

    @staticmethod
    def _event_allows_reply(event: Mapping[str, Any], reply_kind: str) -> bool:
        outcome = event.get("outcome")
        reason = event.get("reason")
        if reply_kind == "chat":
            return outcome == "reply-pending" and reason == "chat"
        if reply_kind == "status":
            return outcome == "reply-pending" and reason == "status"
        if reply_kind == "clarification":
            return outcome == "reply-pending" and reason in CLARIFICATION_CODES
        if reply_kind == "confirmation-preview":
            return outcome == "confirmation-pending" and reason == "direct-confirmation-required"
        if reply_kind == "receipt":
            return outcome in {"dispatch-pending", "cancelled", "refused"} and reason in RECEIPT_REASONS
        return False

    def confirmation_preview(
        self,
        event_id: str,
        intent_id: str,
        token: str,
        *,
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        if not isinstance(token, str) or not CONFIRM_TOKEN.fullmatch(token):
            raise NaturalLanguageError("invalid-confirmation-token")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            event = next((r for r in self._event_records() if r["eventId"] == event_id), None)
            intent = next((r for r in self._intent_records() if r["intentId"] == intent_id), None)
            if (
                event is None
                or intent is None
                or event.get("intentId") != intent_id
                or intent.get("sourceEventId") != event_id
                or intent.get("risk") != "high"
                or event.get("outcome") != "confirmation-pending"
            ):
                raise NaturalLanguageError("confirmation-preview-not-pending")
            if parse_utc(intent["expiresAt"]) <= current:
                raise NaturalLanguageError("confirmation-preview-expired")
            key = self._privacy_key_unlocked()
            if not hmac.compare_digest(
                self._mac(key, "confirmation-token", token),
                intent["confirmationTokenMac"],
            ):
                raise NaturalLanguageError("confirmation-token-mismatch")
            return {
                "eventId": event_id,
                "intentId": intent_id,
                "targetKey": intent["targetKey"],
                "targetTitle": intent["targetTitle"],
                "risk": intent["risk"],
                "action": intent["action"],
                "expiresAt": intent["expiresAt"],
            }

    def reply_state(self, event_id: str, reply_kind: str) -> dict[str, Any]:
        with self.locked():
            self._assert_ledgers_unlocked()
            records = [
                r for r in self._reply_records()
                if r["eventId"] == event_id and r["replyKind"] == reply_kind
            ]
            return {"records": records, "terminal": bool(records)}

    def claim_reply(
        self, event_id: str, reply_kind: str, *, now: Optional[dt.datetime] = None
    ) -> bool:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            event = next((r for r in self._event_records() if r["eventId"] == event_id), None)
            allowed = {
                "chat": {"chat"},
                "status": {"status"},
                "clarification": {"clarification", "action"},
                "confirmation-preview": {"action"},
                "receipt": {"action", "cancel", "confirmation"},
            }
            if event is None or event["intent"] not in allowed.get(reply_kind, set()):
                raise NaturalLanguageError("reply-not-pending")
            if not self._event_allows_reply(event, reply_kind):
                raise NaturalLanguageError("reply-not-pending")
            if any(
                r["eventId"] == event_id and r["replyKind"] == reply_kind
                for r in self._reply_records()
            ):
                return False
            self._append(
                self.reply_path,
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "recordType": "nl-reply",
                    "at": format_utc(current),
                    "eventId": event_id,
                    "replyKind": reply_kind,
                    "outcome": "claimed",
                    "reason": "claimed-before-post",
                    "httpStatus": None,
                },
            )
            return True

    def finalize_reply(
        self,
        event_id: str,
        reply_kind: str,
        outcome: str,
        reason: str,
        http_status: Optional[int],
        *,
        now: Optional[dt.datetime] = None,
    ) -> None:
        if outcome not in {"delivered", "failed", "unknown"}:
            raise NaturalLanguageError("invalid-reply-outcome")
        if reason not in REPLY_FINAL_REASONS[outcome]:
            raise NaturalLanguageError("invalid-reply-reason")
        if (
            (outcome == "delivered" and http_status != 200)
            or (outcome == "unknown" and http_status is not None)
            or (
                outcome == "failed"
                and (
                    isinstance(http_status, bool)
                    or not isinstance(http_status, int)
                    or not 100 <= http_status <= 599
                )
            )
        ):
            raise NaturalLanguageError("invalid-reply-http-status")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_ledgers_unlocked()
            records = [
                r for r in self._reply_records()
                if r["eventId"] == event_id and r["replyKind"] == reply_kind
            ]
            if len(records) != 1 or records[0]["outcome"] != "claimed":
                raise NaturalLanguageError("reply-not-claimed")
            self._append(
                self.reply_path,
                {
                    "schemaVersion": SCHEMA_VERSION,
                    "recordType": "nl-reply",
                    "at": format_utc(current),
                    "eventId": event_id,
                    "replyKind": reply_kind,
                    "outcome": outcome,
                    "reason": reason,
                    "httpStatus": http_status,
                },
            )


def forwarded_transcript_prompt(envelope_json: str) -> str:
    """Wrap an already canonical envelope in a stable redaction marker."""

    try:
        envelope = json.loads(envelope_json)
    except ValueError as exc:
        raise NaturalLanguageError("invalid-dispatch-envelope") from exc
    provenance = envelope.get("provenance") if isinstance(envelope, dict) else None
    event_id = provenance.get("eventId") if isinstance(provenance, dict) else None
    if (
        not isinstance(provenance, dict)
        or provenance.get("kind") != FORWARD_PROVENANCE
        or not isinstance(event_id, str)
        or not SLACK_EVENT_ID.fullmatch(event_id)
    ):
        raise NaturalLanguageError("invalid-dispatch-envelope")
    encoded = base64.urlsafe_b64encode(
        canonical_json(envelope).encode("utf-8", "strict")
    ).decode("ascii")
    return (
        "<FIDGETING_SLACK_REQUEST_V1 event_id=\"{}\" encoding=\"base64url\">\n{}\n"
        "</FIDGETING_SLACK_REQUEST_V1>"
    ).format(event_id, encoded)


def _read_cli_json(*, max_bytes: int = 131_072) -> Mapping[str, Any]:
    raw = sys.stdin.read(max_bytes + 1)
    if len(raw.encode("utf-8", "replace")) > max_bytes:
        raise NaturalLanguageError("cli-input-too-large")
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise NaturalLanguageError("invalid-cli-json") from exc
    if not isinstance(value, dict):
        raise NaturalLanguageError("invalid-cli-json")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument(
        "--bridge-runtime-root", type=Path, default=default_bridge_runtime_root()
    )
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    parser.add_argument("--allowed-workspace-host")
    commands = parser.add_subparsers(dest="operation", required=True)

    acquire = commands.add_parser("lease-acquire", help="claim the single round lease")
    acquire.add_argument("--lease-id", required=True)
    release = commands.add_parser("lease-release", help="release the single round lease")
    release.add_argument("--lease-id", required=True)

    route = commands.add_parser("route", help="route one current-poll event from JSON stdin")
    route.add_argument("--poll-id", required=True)
    route.add_argument("--dry-run", action="store_true")

    claim = commands.add_parser(
        "claim", help="claim a low-risk intent; fresh observation JSON comes from stdin"
    )
    claim.add_argument("--intent-id", required=True)
    claim.add_argument("--lease-id", required=True)

    finalize = commands.add_parser("finalize", help="record the one-shot dispatch outcome")
    finalize.add_argument("--intent-id", required=True)
    finalize.add_argument("--lease-id", required=True)
    finalize.add_argument(
        "--outcome", choices=("dispatched", "refused", "unknown"), required=True
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # CLI always uses the host wall clock.  Tests inject ``utc_now`` in
        # process; no command-line value can extend freshness or lease TTLs.
        current = utc_now()
        store = NaturalLanguageStore(args.runtime_root)
        if args.operation == "lease-acquire":
            result = store.acquire_round_lease(args.lease_id, now=current)
        elif args.operation == "lease-release":
            result = store.release_round_lease(args.lease_id, now=current)
        elif args.operation == "finalize":
            result = store.finalize_dispatch(
                args.intent_id, args.lease_id, args.outcome, now=current
            )
        elif args.operation == "route":
            body = _read_cli_json()
            if set(body) != {"schemaVersion", "event", "classification", "observation"}:
                raise NaturalLanguageError("invalid-route-input-fields")
            if body.get("schemaVersion") != SCHEMA_VERSION:
                raise NaturalLanguageError("unsupported-route-input-schema")
            policy = CommandPolicy.from_values(
                args.allowed_team_id,
                args.allowed_user_id,
                args.allowed_conversation_id,
            )
            workspace_host = args.allowed_workspace_host or os.environ.get(
                "FIDGETING_SLACK_ALLOWED_WORKSPACE_HOST", ""
            )
            catalog = load_task_catalog()
            if args.dry_run:
                with tempfile.TemporaryDirectory(prefix="fidgeting-nl-dry-run-") as temporary:
                    dry_store = NaturalLanguageStore(Path(temporary))
                    prepared = dry_store.route_native(
                        body.get("event"),
                        body.get("classification"),
                        bridge_store=AppendOnlyCommandStore(args.bridge_runtime_root),
                        policy=policy,
                        workspace_host=workspace_host,
                        poll_id=args.poll_id,
                        catalog=catalog,
                        observation=body.get("observation"),
                        now=current,
                    )
                result = dict(prepared.public, dryRun=True, privateArtifact=None)
            else:
                prepared = store.route_native(
                    body.get("event"),
                    body.get("classification"),
                    bridge_store=AppendOnlyCommandStore(args.bridge_runtime_root),
                    policy=policy,
                    workspace_host=workspace_host,
                    poll_id=args.poll_id,
                    catalog=catalog,
                    observation=body.get("observation"),
                    now=current,
                )
                artifact = store.persist_route_private_material(prepared, now=current)
                result = dict(
                    prepared.public,
                    privateArtifact=str(artifact) if artifact is not None else None,
                )
        else:
            observation = _read_cli_json()
            catalog = load_task_catalog()
            prepared, artifact = store.claim_from_private_ticket(
                args.intent_id,
                observation=observation,
                catalog=catalog,
                lease_id=args.lease_id,
                now=current,
            )
            result = dict(
                prepared.public,
                privateArtifact=str(artifact) if artifact is not None else None,
            )
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except (BridgeError, ValueError, TypeError) as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


__all__ = [
    "DEFAULT_CATALOG_PATH",
    "FORWARD_PROVENANCE",
    "NaturalLanguageError",
    "NaturalLanguageStore",
    "PreparedRoute",
    "TaskCatalog",
    "default_runtime_root",
    "forwarded_transcript_prompt",
    "load_task_catalog",
    "validate_classification",
    "validate_observation",
]


if __name__ == "__main__":
    raise SystemExit(main())
