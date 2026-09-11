#!/usr/bin/env python3
"""Transport-neutral Slack command ingress for the Fidgeting Cursor supervisor.

The bridge accepts a small, sanitized Slack event object and turns only four
exact commands into an append-only local command ledger. It does not call
Slack, execute shell commands, click UI, or alter a Codex automation.

Runtime policy is supplied with command-line flags or the non-secret
FIDGETING_SLACK_ALLOWED_* environment variables. No Slack token is used here.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence
from urllib.parse import urlsplit


SCHEMA_VERSION = "1.0"
SLACK_NATIVE_CUA_SOURCE = "slack-native-cua"
NATIVE_CUA_ALLOWED_COMMANDS = frozenset({"status", "pause", "resume"})
COMMAND_PREFIX = "fidget"
ALLOWED_COMMANDS = ("status", "pause", "resume", "approve-safe")
TERMINAL_OUTCOMES = ("applied", "reported", "refused", "expired")
NON_REPLAY_OUTCOMES = ("claimed", *TERMINAL_OUTCOMES)
MAX_FUTURE_SKEW_SECONDS = 60
COMMAND_MAX_AGE_SECONDS = {
    "status": 900,
    "pause": 300,
    "resume": 300,
    "approve-safe": 300,
}
COMMAND_TTL_SECONDS = {"status": 900, "approve-safe": 300}

SLACK_TEAM_ID = re.compile(r"^T[A-Z0-9]{2,31}$")
SLACK_USER_ID = re.compile(r"^[UW][A-Z0-9]{2,31}$")
SLACK_CONVERSATION_ID = re.compile(r"^[CDG][A-Z0-9]{2,31}$")
SLACK_WORKSPACE_HOST = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}\.slack\.com$")
SLACK_EVENT_ID = re.compile(r"^[A-Za-z0-9._:-]{1,160}$")
SLACK_TIMESTAMP = re.compile(r"^[0-9]{9,13}(?:\.[0-9]{1,10})?$")
SLACK_NATIVE_TIMESTAMP = re.compile(r"^[0-9]{10}\.[0-9]{6}$")
SLACK_POLL_ID = re.compile(r"^poll_[A-Za-z0-9]{8,64}$")
APPROVAL_REQUEST_ID = re.compile(r"^safe_[A-Za-z0-9]{5,32}$")
SHA256_HEX = re.compile(r"^[a-f0-9]{64}$")
GROUPED_APP_CONTINUATION_KIND = "app-message-group-continuation"
SOURCE_ROW_KINDS = frozenset(
    {"self-message", "app-message", GROUPED_APP_CONTINUATION_KIND}
)
SOURCE_POLL_FAILURE_REASONS = frozenset(
    {
        "identity-failed",
        "anchor-missing",
        "chronology-ambiguous",
        "stable-bottom-not-proven",
        "ui-read-failed",
        "no-new-stable-row",
    }
)
SANITIZED_EVENT_KEYS = {
    "schemaVersion",
    "team_id",
    "user_id",
    "conversation_id",
    "event_id",
    "message_ts",
    "text",
}


class BridgeError(Exception):
    """Base error safe to render without including event text or secrets."""


class ConfigurationError(BridgeError):
    pass


class StoreError(BridgeError):
    pass


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def format_utc(value: dt.datetime) -> str:
    utc_value = value.astimezone(dt.timezone.utc)
    timespec = "microseconds" if utc_value.microsecond else "seconds"
    return utc_value.isoformat(timespec=timespec).replace("+00:00", "Z")


def parse_utc(value: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("invalid UTC timestamp")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def parse_slack_timestamp(value: str) -> Decimal:
    if not isinstance(value, str) or not SLACK_TIMESTAMP.fullmatch(value):
        raise ValueError("invalid Slack timestamp")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid Slack timestamp") from exc


def valid_source_permalink(
    permalink: str,
    workspace_host: str,
    conversation_id: str,
    message_ts: str,
) -> bool:
    """Validate that a row permalink encodes the exact DM and message timestamp."""

    if (
        not isinstance(permalink, str)
        or len(permalink) > 512
        or not isinstance(message_ts, str)
        or not SLACK_NATIVE_TIMESTAMP.fullmatch(message_ts)
    ):
        return False
    try:
        parsed = urlsplit(permalink)
        invalid_origin = (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.hostname != workspace_host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.query
            or parsed.fragment
        )
    except ValueError:
        return False
    if invalid_origin:
        return False
    expected_path = "/archives/{}/p{}".format(
        conversation_id, message_ts.replace(".", "")
    )
    return parsed.path.rstrip("/") == expected_path


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def text_fingerprint(value: Any) -> tuple[str, int]:
    text = value if isinstance(value, str) else ""
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(), len(text)


@dataclass(frozen=True)
class CommandPolicy:
    team_id: str
    user_id: str
    conversation_id: str

    def __post_init__(self) -> None:
        checks = (
            ("team_id", self.team_id, SLACK_TEAM_ID),
            ("user_id", self.user_id, SLACK_USER_ID),
            ("conversation_id", self.conversation_id, SLACK_CONVERSATION_ID),
        )
        for name, value, pattern in checks:
            if not isinstance(value, str) or not pattern.fullmatch(value):
                raise ConfigurationError("invalid-allowed-{}".format(name.replace("_", "-")))

    @classmethod
    def from_values(
        cls,
        team_id: Optional[str],
        user_id: Optional[str],
        conversation_id: Optional[str],
    ) -> "CommandPolicy":
        return cls(
            team_id=team_id or os.environ.get("FIDGETING_SLACK_ALLOWED_TEAM_ID", ""),
            user_id=user_id or os.environ.get("FIDGETING_SLACK_ALLOWED_USER_ID", ""),
            conversation_id=conversation_id
            or os.environ.get("FIDGETING_SLACK_ALLOWED_CONVERSATION_ID", ""),
        )


@dataclass(frozen=True)
class IngressDecision:
    accepted: bool
    reason: str
    event_id: str
    command: Optional[str]
    request_id: Optional[str]
    team_id: str
    user_id: str
    conversation_id: str
    message_ts: str
    text_sha256: str
    text_length: int

    def public_result(self, *, duplicate: bool = False, dry_run: bool = False) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "accepted": self.accepted and not duplicate,
            "command": self.command if self.accepted else None,
            "requestId": self.request_id if self.accepted else None,
            "reason": "duplicate-event" if duplicate else self.reason,
            "duplicate": duplicate,
            "dryRun": dry_run,
            "eventId": self.event_id,
        }


@dataclass(frozen=True)
class SourceObservationRow:
    """One classified top-level row in a continuous exact-DM chronology scan."""

    message_ts: str
    kind: str
    permalink: str


def _derived_event_id(team_id: str, conversation_id: str, message_ts: str) -> str:
    material = "\x1f".join((team_id, conversation_id, message_ts)).encode("utf-8", "strict")
    return "slack:" + hashlib.sha256(material).hexdigest()


def _safe_event_id(raw: Any, team_id: str, conversation_id: str, message_ts: str) -> str:
    if isinstance(raw, str) and SLACK_EVENT_ID.fullmatch(raw):
        return raw
    return _derived_event_id(team_id, conversation_id, message_ts)


def parse_exact_command(text: Any) -> tuple[Optional[str], Optional[str], str]:
    if not isinstance(text, str):
        return None, None, "text-not-string"
    if len(text) > 64:
        return None, None, "text-too-long"
    if any(ord(character) < 32 and character not in "\t\n\r" for character in text):
        return None, None, "text-control-character"
    normalized = text.strip()
    exact_without_argument = {
        "{} {}".format(COMMAND_PREFIX, command): command
        for command in ("status", "pause", "resume")
    }
    command = exact_without_argument.get(normalized)
    if command is not None:
        return command, None, "accepted"

    approval_prefix = "{} approve-safe".format(COMMAND_PREFIX)
    if normalized == approval_prefix:
        return None, None, "approval-request-id-required"
    if normalized.startswith(approval_prefix + " "):
        request_id = normalized[len(approval_prefix) + 1 :]
        if APPROVAL_REQUEST_ID.fullmatch(request_id):
            return "approve-safe", request_id, "accepted"
        return None, None, "invalid-approval-request-id"
    return None, None, "command-not-allowlisted"


def evaluate_event(
    event: Mapping[str, Any], policy: CommandPolicy, *, now: Optional[dt.datetime] = None
) -> IngressDecision:
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    unknown_keys = set(event) - SANITIZED_EVENT_KEYS
    team_id = event.get("team_id") if isinstance(event.get("team_id"), str) else ""
    user_id = event.get("user_id") if isinstance(event.get("user_id"), str) else ""
    conversation_id = (
        event.get("conversation_id") if isinstance(event.get("conversation_id"), str) else ""
    )
    message_ts = event.get("message_ts") if isinstance(event.get("message_ts"), str) else ""
    event_id = _safe_event_id(event.get("event_id"), team_id, conversation_id, message_ts)
    fingerprint, text_length = text_fingerprint(event.get("text"))

    reason = "accepted"
    command: Optional[str] = None
    request_id: Optional[str] = None
    if unknown_keys:
        reason = "unexpected-event-fields"
    elif "schemaVersion" not in event:
        reason = "missing-schema-version"
    elif event.get("schemaVersion") != SCHEMA_VERSION:
        reason = "unsupported-schema-version"
    elif "event_id" in event and (
        not isinstance(event.get("event_id"), str)
        or not SLACK_EVENT_ID.fullmatch(event["event_id"])
    ):
        reason = "invalid-event-id"
    elif team_id != policy.team_id:
        reason = "team-not-allowed"
    elif user_id != policy.user_id:
        reason = "user-not-allowed"
    elif conversation_id != policy.conversation_id:
        reason = "conversation-not-allowed"
    elif not SLACK_TIMESTAMP.fullmatch(message_ts):
        reason = "invalid-message-timestamp"
    else:
        try:
            message_time = dt.datetime.fromtimestamp(float(message_ts), tz=dt.timezone.utc)
        except (OverflowError, OSError, ValueError):
            reason = "invalid-message-timestamp"
        else:
            age = (current - message_time).total_seconds()
            if age < -MAX_FUTURE_SKEW_SECONDS:
                reason = "future-message"
            else:
                command, request_id, reason = parse_exact_command(event.get("text"))
                if (
                    reason == "accepted"
                    and command is not None
                    and age > COMMAND_MAX_AGE_SECONDS[command]
                ):
                    reason = "stale-message"
                    command = None
                    request_id = None

    return IngressDecision(
        accepted=reason == "accepted",
        reason=reason,
        event_id=event_id,
        command=command,
        request_id=request_id,
        team_id=team_id,
        user_id=user_id,
        conversation_id=conversation_id,
        message_ts=message_ts,
        text_sha256=fingerprint,
        text_length=text_length,
    )


def evaluate_native_cua_event(
    event: Mapping[str, Any], policy: CommandPolicy, *, now: Optional[dt.datetime] = None
) -> IngressDecision:
    """Evaluate a native-CUA event with a fail-safe pause exception.

    A native batch can only reach this function after an observe-only bootstrap
    and a monotonic exact-DM chronology scan. A delayed ``pause`` therefore
    still narrows authority and is safe to apply, while ``resume`` retains the
    normal five-minute freshness requirement because it restores authority.
    """

    decision = evaluate_event(event, policy, now=now)
    if decision.reason != "stale-message":
        return decision
    command, request_id, reason = parse_exact_command(event.get("text"))
    if command != "pause" or request_id is not None or reason != "accepted":
        return decision
    return replace(
        decision,
        accepted=True,
        reason="accepted",
        command="pause",
        request_id=None,
    )


def _decision_at_ingest_time(
    decision: IngressDecision,
    current: dt.datetime,
    *,
    allow_stale_native_pause: bool = False,
) -> IngressDecision:
    """Recheck freshness at the authoritative append boundary.

    Evaluation and append normally happen back-to-back, but a caller must not
    be able to retain an accepted pause/resume decision and persist it after its
    Slack timestamp is stale.
    """

    if not decision.accepted or decision.command is None:
        return decision
    try:
        message_time = dt.datetime.fromtimestamp(
            float(decision.message_ts), tz=dt.timezone.utc
        )
    except (OverflowError, OSError, ValueError):
        return replace(
            decision,
            accepted=False,
            reason="invalid-message-timestamp",
            command=None,
            request_id=None,
        )
    age = (current - message_time).total_seconds()
    if age > COMMAND_MAX_AGE_SECONDS[decision.command] and not (
        allow_stale_native_pause and decision.command == "pause"
    ):
        return replace(
            decision,
            accepted=False,
            reason="stale-message",
            command=None,
            request_id=None,
        )
    if age < -MAX_FUTURE_SKEW_SECONDS:
        return replace(
            decision,
            accepted=False,
            reason="future-message",
            command=None,
            request_id=None,
        )
    return decision


def _read_json_lines_strict(path: Path, error: str) -> Iterator[dict[str, Any]]:
    if not path.exists():
        return
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            if not raw.strip():
                raise StoreError(error)
            try:
                value = json.loads(raw)
            except ValueError as exc:
                raise StoreError(error) from exc
            if not isinstance(value, dict):
                raise StoreError(error)
            yield value


def source_batch_digest(
    source: str,
    policy: CommandPolicy,
    base_cursor: Optional[str],
    next_cursor: Optional[str],
    decisions: Sequence[IngressDecision],
    *,
    observed_rows: Sequence[SourceObservationRow] = (),
    poll_id: Optional[str] = None,
    workspace_host: Optional[str] = None,
) -> str:
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "source": source,
        "teamId": policy.team_id,
        "userId": policy.user_id,
        "conversationId": policy.conversation_id,
        "workspaceHost": workspace_host,
        "baseObservedThrough": base_cursor,
        "observedThrough": next_cursor,
        "pollId": poll_id,
        "rows": [
            {
                "messageTs": row.message_ts,
                "kind": row.kind,
                "permalinkSha256": hashlib.sha256(
                    row.permalink.encode("utf-8", "strict")
                ).hexdigest(),
            }
            for row in observed_rows
        ],
        "events": [
            {
                "eventId": decision.event_id,
                "messageTs": decision.message_ts,
                "textSha256": decision.text_sha256,
                "textLength": decision.text_length,
            }
            for decision in decisions
        ],
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8", "strict")).hexdigest()


def source_bootstrap_digest(source: str, policy: CommandPolicy, cursor: str) -> str:
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "operation": "observe-only-bootstrap",
        "source": source,
        "teamId": policy.team_id,
        "userId": policy.user_id,
        "conversationId": policy.conversation_id,
        "cursor": cursor,
        "activationCutoff": cursor,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8", "strict")).hexdigest()


class AppendOnlyCommandStore:
    """Append-only ledgers plus an atomically replaced derived-state cache."""

    def __init__(self, root: Path):
        self.root = root.expanduser().resolve(strict=False)
        self.queue_path = self.root / "commands.ndjson"
        self.audit_path = self.root / "audit.ndjson"
        self.consumption_path = self.root / "consumption.ndjson"
        self.status_delivery_path = self.root / "status-delivery.ndjson"
        self.state_path = self.root / "control-state.json"
        self.source_cursor_ledger_path = self.root / "source-cursors.ndjson"
        self.source_poll_ledger_path = self.root / "source-polls.ndjson"
        self.source_cursor_path = self.root / "source-cursor.json"
        self.lock_path = self.root / ".lock"

    def _prepare(self) -> None:
        if self.root.exists() and self.root.is_symlink():
            raise StoreError("runtime-root-is-symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        for path in (
            self.queue_path,
            self.audit_path,
            self.consumption_path,
            self.status_delivery_path,
            self.state_path,
            self.source_cursor_ledger_path,
            self.source_poll_ledger_path,
            self.source_cursor_path,
            self.lock_path,
        ):
            if path.is_symlink():
                raise StoreError("runtime-file-is-symlink")

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
                    raise StoreError("append-write-failed")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.chmod(path, 0o600)

    @staticmethod
    def _valid_source_record(value: Any) -> bool:
        if not isinstance(value, Mapping) or set(value) != {
            "teamId",
            "userId",
            "conversationId",
            "messageTs",
        }:
            return False
        return bool(
            isinstance(value.get("teamId"), str)
            and SLACK_TEAM_ID.fullmatch(value["teamId"])
            and isinstance(value.get("userId"), str)
            and SLACK_USER_ID.fullmatch(value["userId"])
            and isinstance(value.get("conversationId"), str)
            and SLACK_CONVERSATION_ID.fullmatch(value["conversationId"])
            and isinstance(value.get("messageTs"), str)
            and SLACK_TIMESTAMP.fullmatch(value["messageTs"])
        )

    @staticmethod
    def _valid_audit_source_record(value: Any) -> bool:
        """Rejected inputs may have invalid IDs; keep them bounded but auditable."""

        if not isinstance(value, Mapping) or set(value) != {
            "teamId",
            "userId",
            "conversationId",
            "messageTs",
        }:
            return False
        return all(
            isinstance(value.get(key), str) and len(value[key]) <= 64
            for key in ("teamId", "userId", "conversationId", "messageTs")
        )

    def _command_records(self) -> Iterator[dict[str, Any]]:
        required = {
            "schemaVersion",
            "recordType",
            "eventId",
            "receivedAt",
            "expiresAt",
            "command",
            "requestId",
            "sourceTextSha256",
            "sourceTextLength",
            "source",
        }
        seen: set[str] = set()
        for record in _read_json_lines_strict(
            self.queue_path, "invalid-command-ledger"
        ):
            event_id = record.get("eventId")
            command = record.get("command")
            request_id = record.get("requestId")
            expires_at = record.get("expiresAt")
            valid_expiry = expires_at is None
            if isinstance(expires_at, str):
                try:
                    parse_utc(expires_at)
                    valid_expiry = True
                except (TypeError, ValueError):
                    valid_expiry = False
            try:
                parse_utc(record.get("receivedAt"))
            except (TypeError, ValueError):
                valid_received_at = False
            else:
                valid_received_at = True
            valid_request = (
                isinstance(request_id, str)
                and APPROVAL_REQUEST_ID.fullmatch(request_id) is not None
                if command == "approve-safe"
                else request_id is None
            )
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "command"
                or not isinstance(event_id, str)
                or not SLACK_EVENT_ID.fullmatch(event_id)
                or event_id in seen
                or command not in ALLOWED_COMMANDS
                or not valid_request
                or not valid_received_at
                or not valid_expiry
                or (command in {"status", "approve-safe"}) != isinstance(expires_at, str)
                or not isinstance(record.get("sourceTextSha256"), str)
                or not SHA256_HEX.fullmatch(record["sourceTextSha256"])
                or isinstance(record.get("sourceTextLength"), bool)
                or not isinstance(record.get("sourceTextLength"), int)
                or record["sourceTextLength"] < 0
                or not self._valid_source_record(record.get("source"))
            ):
                raise StoreError("invalid-command-ledger")
            seen.add(event_id)
            yield record

    def _audit_records(self) -> Iterator[dict[str, Any]]:
        audit_keys = {
            "schemaVersion",
            "recordType",
            "at",
            "eventId",
            "outcome",
            "reason",
            "command",
            "requestId",
            "source",
            "textSha256",
            "textLength",
        }
        runtime_keys = {
            "schemaVersion",
            "recordType",
            "at",
            "outcome",
            "reason",
            "retryAfterSeconds",
        }
        for record in _read_json_lines_strict(self.audit_path, "invalid-audit-ledger"):
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError):
                raise StoreError("invalid-audit-ledger")
            record_type = record.get("recordType")
            if record_type == "runtime":
                retry_after = record.get("retryAfterSeconds")
                if (
                    set(record) != runtime_keys
                    or record.get("schemaVersion") != SCHEMA_VERSION
                    or record.get("outcome")
                    not in {"connected", "disconnected", "retrying", "failed", "ignored"}
                    or not isinstance(record.get("reason"), str)
                    or not re.fullmatch(r"[a-z0-9-]{1,80}", record["reason"])
                    or not (
                        retry_after is None
                        or (
                            isinstance(retry_after, int)
                            and not isinstance(retry_after, bool)
                            and retry_after >= 0
                        )
                    )
                ):
                    raise StoreError("invalid-audit-ledger")
            elif record_type == "audit":
                command = record.get("command")
                request_id = record.get("requestId")
                if (
                    set(record) != audit_keys
                    or record.get("schemaVersion") != SCHEMA_VERSION
                    or not isinstance(record.get("eventId"), str)
                    or not SLACK_EVENT_ID.fullmatch(record["eventId"])
                    or record.get("outcome") not in {"accepted", "rejected", "duplicate"}
                    or not isinstance(record.get("reason"), str)
                    or not re.fullmatch(r"[a-z0-9-]{1,80}", record["reason"])
                    or not (command is None or command in ALLOWED_COMMANDS)
                    or not (
                        request_id is None
                        or (
                            isinstance(request_id, str)
                            and APPROVAL_REQUEST_ID.fullmatch(request_id)
                        )
                    )
                    or not self._valid_audit_source_record(record.get("source"))
                    or not isinstance(record.get("textSha256"), str)
                    or not SHA256_HEX.fullmatch(record["textSha256"])
                    or isinstance(record.get("textLength"), bool)
                    or not isinstance(record.get("textLength"), int)
                    or record["textLength"] < 0
                ):
                    raise StoreError("invalid-audit-ledger")
            else:
                raise StoreError("invalid-audit-ledger")
            yield record

    def _consumption_records(self) -> Iterator[dict[str, Any]]:
        required = {
            "schemaVersion",
            "recordType",
            "at",
            "eventId",
            "command",
            "requestId",
            "outcome",
            "actor",
        }
        for record in _read_json_lines_strict(
            self.consumption_path, "invalid-consumption-ledger"
        ):
            command = record.get("command")
            request_id = record.get("requestId")
            outcome = record.get("outcome")
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError):
                valid_at = False
            else:
                valid_at = True
            valid_outcomes = {
                "status": {"reported", "refused", "expired"},
                "pause": {"applied", "refused"},
                "resume": {"applied", "refused"},
                "approve-safe": {"claimed", "applied", "refused", "expired"},
            }
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") not in {"claim", "consumption"}
                or not valid_at
                or not isinstance(record.get("eventId"), str)
                or not SLACK_EVENT_ID.fullmatch(record["eventId"])
                or command not in ALLOWED_COMMANDS
                or (
                    command == "approve-safe"
                    and not (
                        isinstance(request_id, str)
                        and APPROVAL_REQUEST_ID.fullmatch(request_id)
                    )
                )
                or (command != "approve-safe" and request_id is not None)
                or outcome not in NON_REPLAY_OUTCOMES
                or outcome not in valid_outcomes.get(command, set())
                or (record.get("recordType") == "claim") != (outcome == "claimed")
                or record.get("actor") != "fidgeting-cursor-heartbeat"
            ):
                raise StoreError("invalid-consumption-ledger")
            yield record

    def _status_delivery_records(self) -> Iterator[dict[str, Any]]:
        required = {
            "schemaVersion",
            "recordType",
            "at",
            "eventId",
            "outcome",
            "reason",
            "payloadSha256",
            "teamId",
            "conversationId",
            "httpStatus",
        }
        delivered: set[str] = set()
        for record in _read_json_lines_strict(
            self.status_delivery_path, "invalid-status-delivery-ledger"
        ):
            try:
                parse_utc(record.get("at"))
            except (TypeError, ValueError):
                valid_at = False
            else:
                valid_at = True
            event_id = record.get("eventId")
            outcome = record.get("outcome")
            http_status = record.get("httpStatus")
            valid_outcome = (
                outcome == "delivered"
                and record.get("reason") == "webhook-ok"
                and http_status == 200
            ) or (
                outcome == "failed"
                and record.get("reason")
                in {"network-error", "http-error", "unexpected-response"}
                and (
                    http_status is None
                    or (
                        isinstance(http_status, int)
                        and not isinstance(http_status, bool)
                        and 100 <= http_status <= 599
                    )
                )
            )
            if (
                set(record) != required
                or record.get("schemaVersion") != SCHEMA_VERSION
                or record.get("recordType") != "status-delivery"
                or not valid_at
                or not isinstance(event_id, str)
                or not SLACK_EVENT_ID.fullmatch(event_id)
                or not valid_outcome
                or not isinstance(record.get("payloadSha256"), str)
                or not SHA256_HEX.fullmatch(record["payloadSha256"])
                or not isinstance(record.get("teamId"), str)
                or not SLACK_TEAM_ID.fullmatch(record["teamId"])
                or not isinstance(record.get("conversationId"), str)
                or not SLACK_CONVERSATION_ID.fullmatch(record["conversationId"])
                or (outcome == "delivered" and event_id in delivered)
            ):
                raise StoreError("invalid-status-delivery-ledger")
            if outcome == "delivered":
                delivered.add(event_id)
            yield record

    def _source_poll_records(self) -> Iterator[dict[str, Any]]:
        required = {
            "schemaVersion",
            "recordType",
            "at",
            "source",
            "teamId",
            "userId",
            "conversationId",
            "workspaceHost",
            "pollId",
            "outcome",
            "reason",
            "baseObservedThrough",
            "observedThrough",
            "batchDigest",
            "observedRowCount",
            "eventCount",
        }
        seen_poll_ids: set[str] = set()
        for record in _read_json_lines_strict(
            self.source_poll_ledger_path, "invalid-source-poll-ledger"
        ):
            try:
                if not (
                    isinstance(record.get("baseObservedThrough"), str)
                    and SLACK_NATIVE_TIMESTAMP.fullmatch(record["baseObservedThrough"])
                    and isinstance(record.get("observedThrough"), str)
                    and SLACK_NATIVE_TIMESTAMP.fullmatch(record["observedThrough"])
                ):
                    raise ValueError("noncanonical native timestamp")
                at = parse_utc(record.get("at"))
                base_value = parse_slack_timestamp(record.get("baseObservedThrough"))
                observed_value = parse_slack_timestamp(record.get("observedThrough"))
            except (TypeError, ValueError):
                raise StoreError("invalid-source-poll-ledger")
            poll_id = record.get("pollId")
            outcome = record.get("outcome")
            reason = record.get("reason")
            row_count = record.get("observedRowCount")
            event_count = record.get("eventCount")
            common_valid = (
                set(record) == required
                and record.get("schemaVersion") == SCHEMA_VERSION
                and record.get("recordType") == "source-poll"
                and at.tzinfo is not None
                and record.get("source") == SLACK_NATIVE_CUA_SOURCE
                and isinstance(record.get("teamId"), str)
                and SLACK_TEAM_ID.fullmatch(record["teamId"])
                and isinstance(record.get("userId"), str)
                and SLACK_USER_ID.fullmatch(record["userId"])
                and isinstance(record.get("conversationId"), str)
                and SLACK_CONVERSATION_ID.fullmatch(record["conversationId"])
                and isinstance(record.get("workspaceHost"), str)
                and SLACK_WORKSPACE_HOST.fullmatch(record["workspaceHost"])
                and isinstance(poll_id, str)
                and SLACK_POLL_ID.fullmatch(poll_id)
                and poll_id not in seen_poll_ids
                and outcome in {"verified", "failed"}
                and isinstance(row_count, int)
                and not isinstance(row_count, bool)
                and isinstance(event_count, int)
                and not isinstance(event_count, bool)
            )
            verified_valid = bool(
                outcome == "verified"
                and reason == "continuous-stable-bottom"
                and isinstance(record.get("batchDigest"), str)
                and SHA256_HEX.fullmatch(record["batchDigest"])
                and (
                    (row_count == 0 and observed_value == base_value)
                    or (row_count >= 1 and observed_value > base_value)
                )
                and 0 <= event_count <= row_count
            )
            failed_valid = bool(
                outcome == "failed"
                and reason in SOURCE_POLL_FAILURE_REASONS
                and record.get("batchDigest") is None
                and observed_value == base_value
                and row_count == 0
                and event_count == 0
            )
            if not common_valid or not (verified_valid or failed_valid):
                raise StoreError("invalid-source-poll-ledger")
            seen_poll_ids.add(poll_id)
            yield record

    def _assert_authoritative_ledgers_unlocked(self) -> None:
        """Refuse all state derivation/mutation if any authoritative ledger is corrupt."""

        list(self._command_records())
        list(self._audit_records())
        list(self._consumption_records())
        list(self._status_delivery_records())
        list(self._source_poll_records())

    def _atomic_write(self, path: Path, value: Mapping[str, Any]) -> None:
        descriptor, temporary = tempfile.mkstemp(prefix=".{}-".format(path.name), dir=str(self.root))
        try:
            os.fchmod(descriptor, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(value, handle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            directory = os.open(str(self.root), os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _known_event_ids(self) -> set[str]:
        ids: set[str] = set()
        for record in self._command_records():
            ids.add(record["eventId"])
        for record in self._audit_records():
            event_id = record.get("eventId")
            if isinstance(event_id, str):
                ids.add(event_id)
        return ids

    @staticmethod
    def _decision_fingerprint(decision: IngressDecision) -> str:
        return canonical_json(
            {
                "teamId": decision.team_id,
                "userId": decision.user_id,
                "conversationId": decision.conversation_id,
                "messageTs": decision.message_ts,
                "textSha256": decision.text_sha256,
                "textLength": decision.text_length,
            }
        )

    def _stored_event_fingerprint(self, event_id: str) -> Optional[str]:
        for record in self._command_records():
            if record.get("eventId") != event_id:
                continue
            source = record.get("source")
            if not isinstance(source, Mapping):
                return None
            fingerprint = {
                "teamId": source.get("teamId"),
                "userId": source.get("userId"),
                "conversationId": source.get("conversationId"),
                "messageTs": source.get("messageTs"),
                "textSha256": record.get("sourceTextSha256"),
                "textLength": record.get("sourceTextLength"),
            }
            if not SHA256_HEX.fullmatch(str(fingerprint["textSha256"])):
                return None
            return canonical_json(fingerprint)

        for record in self._audit_records():
            if record.get("recordType") != "audit" or record.get("eventId") != event_id:
                continue
            source = record.get("source")
            if not isinstance(source, Mapping):
                return None
            fingerprint = {
                "teamId": source.get("teamId"),
                "userId": source.get("userId"),
                "conversationId": source.get("conversationId"),
                "messageTs": source.get("messageTs"),
                "textSha256": record.get("textSha256"),
                "textLength": record.get("textLength"),
            }
            if not SHA256_HEX.fullmatch(str(fingerprint["textSha256"])):
                return None
            return canonical_json(fingerprint)
        return None

    def _record_decision_unlocked(
        self, decision: IngressDecision, current: dt.datetime
    ) -> dict[str, Any]:
        duplicate = decision.event_id in self._known_event_ids()
        if duplicate:
            stored_fingerprint = self._stored_event_fingerprint(decision.event_id)
            if stored_fingerprint != self._decision_fingerprint(decision):
                collision = replace(
                    decision,
                    accepted=False,
                    reason="event-id-collision",
                    command=None,
                    request_id=None,
                )
                self._append(
                    self.audit_path,
                    self._audit_record(collision, current, "rejected", collision.reason),
                )
                return collision.public_result()
            self._append(
                self.audit_path,
                self._audit_record(decision, current, "duplicate", "duplicate-event"),
            )
            return decision.public_result(duplicate=True)

        if decision.accepted and decision.command:
            received_at = format_utc(current)
            ttl = COMMAND_TTL_SECONDS.get(decision.command)
            message_time = dt.datetime.fromtimestamp(
                float(decision.message_ts), tz=dt.timezone.utc
            )
            expires_at = (
                format_utc(message_time + dt.timedelta(seconds=ttl)) if ttl else None
            )
            command_record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "command",
                "eventId": decision.event_id,
                "receivedAt": received_at,
                "expiresAt": expires_at,
                "command": decision.command,
                "requestId": decision.request_id,
                "sourceTextSha256": decision.text_sha256,
                "sourceTextLength": decision.text_length,
                "source": {
                    "teamId": decision.team_id,
                    "userId": decision.user_id,
                    "conversationId": decision.conversation_id,
                    "messageTs": decision.message_ts,
                },
            }
            self._append(self.queue_path, command_record)
            self._append(
                self.audit_path,
                self._audit_record(decision, current, "accepted", "allowlisted-command"),
            )
        else:
            self._append(
                self.audit_path,
                self._audit_record(decision, current, "rejected", decision.reason),
            )
        return decision.public_result()

    def ingest(
        self,
        decision: IngressDecision,
        *,
        now: Optional[dt.datetime] = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        decision = _decision_at_ingest_time(decision, current)
        if dry_run:
            return decision.public_result(dry_run=True)

        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            result = self._record_decision_unlocked(decision, current)
            # Heal a stale/missing cache after a crash between an authoritative
            # ledger append and the derived-state rename.
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return result

    def _latest_source_cursor_unlocked(
        self, source: str, policy: CommandPolicy
    ) -> Optional[dict[str, Any]]:
        required_keys = {
            "schemaVersion",
            "recordType",
            "at",
            "source",
            "teamId",
            "userId",
            "conversationId",
            "baseCursor",
            "cursor",
            "activationCutoff",
            "batchDigest",
            "eventCount",
        }
        latest: Optional[dict[str, Any]] = None
        expected_base: Optional[str] = None
        activation_cutoff: Optional[str] = None
        for record in _read_json_lines_strict(
            self.source_cursor_ledger_path, "invalid-source-cursor-ledger"
        ):
            record_type = record.get("recordType")
            if set(record) != required_keys:
                raise StoreError("invalid-source-cursor-ledger")
            if (
                record.get("schemaVersion") != SCHEMA_VERSION
                or record_type not in {"source-bootstrap", "source-cursor"}
                or record.get("source") != source
                or record.get("teamId") != policy.team_id
                or record.get("userId") != policy.user_id
                or record.get("conversationId") != policy.conversation_id
                or record.get("baseCursor") != expected_base
                or not isinstance(record.get("cursor"), str)
                or not SLACK_NATIVE_TIMESTAMP.fullmatch(record["cursor"])
                or not isinstance(record.get("activationCutoff"), str)
                or not SLACK_NATIVE_TIMESTAMP.fullmatch(record["activationCutoff"])
                or not SHA256_HEX.fullmatch(str(record.get("batchDigest")))
                or isinstance(record.get("eventCount"), bool)
                or not isinstance(record.get("eventCount"), int)
            ):
                raise StoreError("invalid-source-cursor-ledger")
            if latest is None:
                if (
                    record_type != "source-bootstrap"
                    or record["eventCount"] != 0
                    or record["baseCursor"] is not None
                    or record["activationCutoff"] != record["cursor"]
                    or record["batchDigest"]
                    != source_bootstrap_digest(source, policy, record["cursor"])
                ):
                    raise StoreError("invalid-source-cursor-ledger")
                activation_cutoff = record["activationCutoff"]
            elif (
                record_type != "source-cursor"
                or record["eventCount"] < 0
                or record["activationCutoff"] != activation_cutoff
            ):
                raise StoreError("invalid-source-cursor-ledger")
            try:
                parse_utc(record["at"])
                cursor_value = parse_slack_timestamp(record["cursor"])
                cutoff_value = parse_slack_timestamp(record["activationCutoff"])
                if cursor_value < cutoff_value:
                    raise ValueError("cursor-before-activation-cutoff")
                if expected_base is not None and cursor_value <= parse_slack_timestamp(expected_base):
                    raise ValueError("non-monotonic cursor")
            except (TypeError, ValueError) as exc:
                raise StoreError("invalid-source-cursor-ledger") from exc
            latest = record
            expected_base = record["cursor"]

        if latest is None and self.source_cursor_path.exists():
            raise StoreError("source-cursor-cache-without-ledger")
        return latest

    @staticmethod
    def _cursor_public(
        source: str, policy: CommandPolicy, latest: Optional[Mapping[str, Any]]
    ) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "source": source,
            "teamId": policy.team_id,
            "userId": policy.user_id,
            "conversationId": policy.conversation_id,
            "cursor": latest.get("cursor") if latest else None,
            "observedThrough": latest.get("cursor") if latest else None,
            "lastBatchDigest": latest.get("batchDigest") if latest else None,
            "activationCutoff": latest.get("activationCutoff") if latest else None,
            "bootstrapped": latest is not None,
        }

    @staticmethod
    def _poll_record(
        *,
        current: dt.datetime,
        source: str,
        policy: CommandPolicy,
        workspace_host: str,
        poll_id: str,
        outcome: str,
        reason: str,
        base_observed_through: str,
        observed_through: str,
        batch_digest: Optional[str],
        observed_row_count: int,
        event_count: int,
    ) -> dict[str, Any]:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "recordType": "source-poll",
            "at": format_utc(current),
            "source": source,
            "teamId": policy.team_id,
            "userId": policy.user_id,
            "conversationId": policy.conversation_id,
            "workspaceHost": workspace_host,
            "pollId": poll_id,
            "outcome": outcome,
            "reason": reason,
            "baseObservedThrough": base_observed_through,
            "observedThrough": observed_through,
            "batchDigest": batch_digest,
            "observedRowCount": observed_row_count,
            "eventCount": event_count,
        }

    @staticmethod
    def _poll_fingerprint(record: Mapping[str, Any]) -> str:
        return canonical_json(
            {
                key: record.get(key)
                for key in (
                    "source",
                    "teamId",
                    "userId",
                    "conversationId",
                    "workspaceHost",
                    "pollId",
                    "outcome",
                    "reason",
                    "baseObservedThrough",
                    "observedThrough",
                    "batchDigest",
                    "observedRowCount",
                    "eventCount",
                )
            }
        )

    def _poll_duplicate_unlocked(self, record: Mapping[str, Any]) -> bool:
        """Preflight poll identity without mutating any authoritative ledger."""
        for existing in self._source_poll_records():
            if existing["pollId"] != record["pollId"]:
                continue
            if self._poll_fingerprint(existing) != self._poll_fingerprint(record):
                raise StoreError("source-poll-id-conflict")
            return True
        return False

    def _append_poll_or_duplicate_unlocked(
        self, record: Mapping[str, Any]
    ) -> bool:
        """Append a unique poll receipt; return True for an identical retry."""

        if self._poll_duplicate_unlocked(record):
            return True
        self._append(self.source_poll_ledger_path, record)
        return False

    def bootstrap_source_cursor(
        self,
        source: str,
        policy: CommandPolicy,
        cursor: str,
        *,
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        """Record an observe-only activation point without ingesting any message."""

        if source != SLACK_NATIVE_CUA_SOURCE:
            raise StoreError("unsupported-source")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        try:
            cursor_value = parse_slack_timestamp(cursor)
        except ValueError as exc:
            raise StoreError("invalid-source-cursor") from exc
        if (
            not SLACK_NATIVE_TIMESTAMP.fullmatch(cursor)
            or cursor_value > Decimal(str(current.timestamp() + MAX_FUTURE_SKEW_SECONDS))
        ):
            raise StoreError("invalid-source-cursor")
        digest = source_bootstrap_digest(source, policy, cursor)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            latest = self._latest_source_cursor_unlocked(source, policy)
            if latest is not None:
                if (
                    latest.get("recordType") == "source-bootstrap"
                    and latest.get("cursor") == cursor
                    and latest.get("batchDigest") == digest
                ):
                    self._atomic_write(
                        self.source_cursor_path,
                        self._cursor_public(source, policy, latest),
                    )
                    self._atomic_write(self.state_path, self._snapshot_unlocked(current))
                    return {
                        "schemaVersion": SCHEMA_VERSION,
                        "bootstrapped": True,
                        "duplicate": True,
                        "sourceCursor": cursor,
                        "activationCutoff": cursor,
                        "batchDigest": digest,
                    }
                raise StoreError("source-already-bootstrapped")

            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "source-bootstrap",
                "at": format_utc(current),
                "source": source,
                "teamId": policy.team_id,
                "userId": policy.user_id,
                "conversationId": policy.conversation_id,
                "baseCursor": None,
                "cursor": cursor,
                "activationCutoff": cursor,
                "batchDigest": digest,
                "eventCount": 0,
            }
            self._append(self.source_cursor_ledger_path, record)
            self._atomic_write(
                self.source_cursor_path, self._cursor_public(source, policy, record)
            )
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "bootstrapped": True,
                "duplicate": False,
                "sourceCursor": cursor,
                "activationCutoff": cursor,
                "batchDigest": digest,
            }

    def source_cursor(self, source: str, policy: CommandPolicy) -> dict[str, Any]:
        if source != SLACK_NATIVE_CUA_SOURCE:
            raise StoreError("unsupported-source")
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            latest = self._latest_source_cursor_unlocked(source, policy)
            public = self._cursor_public(source, policy, latest)
            if latest is not None:
                self._atomic_write(self.source_cursor_path, public)
            return public

    def record_source_poll_failure(
        self,
        *,
        source: str,
        policy: CommandPolicy,
        workspace_host: str,
        poll_id: str,
        base_observed_through: str,
        reason: str,
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        """Persist a failed/ambiguous poll so an earlier success cannot be reused."""

        if source != SLACK_NATIVE_CUA_SOURCE:
            raise StoreError("unsupported-source")
        if not isinstance(workspace_host, str) or not SLACK_WORKSPACE_HOST.fullmatch(
            workspace_host
        ):
            raise StoreError("invalid-workspace-host")
        if not isinstance(poll_id, str) or not SLACK_POLL_ID.fullmatch(poll_id):
            raise StoreError("invalid-source-poll-id")
        if reason not in SOURCE_POLL_FAILURE_REASONS:
            raise StoreError("invalid-source-poll-failure-reason")
        try:
            parse_slack_timestamp(base_observed_through)
        except ValueError as exc:
            raise StoreError("invalid-source-cursor") from exc
        if not SLACK_NATIVE_TIMESTAMP.fullmatch(base_observed_through):
            raise StoreError("invalid-source-cursor")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        record = self._poll_record(
            current=current,
            source=source,
            policy=policy,
            workspace_host=workspace_host,
            poll_id=poll_id,
            outcome="failed",
            reason=reason,
            base_observed_through=base_observed_through,
            observed_through=base_observed_through,
            batch_digest=None,
            observed_row_count=0,
            event_count=0,
        )
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            latest = self._latest_source_cursor_unlocked(source, policy)
            if latest is None:
                raise StoreError("source-not-bootstrapped")
            if latest.get("cursor") != base_observed_through:
                raise StoreError("source-cursor-conflict")
            duplicate = self._append_poll_or_duplicate_unlocked(record)
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "recorded": not duplicate,
                "duplicate": duplicate,
                "pollId": poll_id,
                "outcome": "failed",
                "reason": reason,
                "observedThrough": base_observed_through,
            }

    def ingest_source_batch(
        self,
        decisions: Sequence[IngressDecision],
        *,
        source: str,
        policy: CommandPolicy,
        workspace_host: str,
        base_cursor: Optional[str],
        next_cursor: Optional[str],
        observed_rows: Sequence[SourceObservationRow],
        poll_id: str,
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        if source != SLACK_NATIVE_CUA_SOURCE:
            raise StoreError("unsupported-source")
        if not isinstance(workspace_host, str) or not SLACK_WORKSPACE_HOST.fullmatch(
            workspace_host
        ):
            raise StoreError("invalid-workspace-host")
        if not isinstance(poll_id, str) or not SLACK_POLL_ID.fullmatch(poll_id):
            raise StoreError("invalid-source-poll-id")
        if base_cursor is None or next_cursor is None:
            raise StoreError("source-not-bootstrapped")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        try:
            base_value = parse_slack_timestamp(base_cursor)
            next_value = parse_slack_timestamp(next_cursor)
        except ValueError as exc:
            raise StoreError("invalid-source-cursor") from exc
        if (
            not SLACK_NATIVE_TIMESTAMP.fullmatch(base_cursor)
            or not SLACK_NATIVE_TIMESTAMP.fullmatch(next_cursor)
            or next_value > Decimal(str(current.timestamp() + MAX_FUTURE_SKEW_SECONDS))
        ):
            raise StoreError("invalid-source-cursor")
        if len(observed_rows) > 500:
            raise StoreError("too-many-observed-rows")

        previous = base_value
        previous_row: Optional[SourceObservationRow] = None
        for row in observed_rows:
            if not isinstance(row, SourceObservationRow):
                raise StoreError("invalid-source-observation-row")
            try:
                row_value = parse_slack_timestamp(row.message_ts)
            except ValueError as exc:
                raise StoreError("invalid-source-observation-row") from exc
            if (
                row.kind not in SOURCE_ROW_KINDS
                or not valid_source_permalink(
                    row.permalink, workspace_host, policy.conversation_id, row.message_ts
                )
                or row_value <= previous
            ):
                raise StoreError("invalid-source-observation-row")
            if row.kind == GROUPED_APP_CONTINUATION_KIND and (
                previous_row is None or previous_row.kind != "app-message"
            ):
                # The closed continuation kind is itself the CUA attestation
                # that both AX rows were simultaneously visible, adjacent, and
                # in one uninterrupted Slack render group.  It may only anchor
                # to a directly verified app row in this same batch; never to
                # a cursor from an earlier poll or another continuation.
                raise StoreError("unanchored-app-group-continuation")
            previous = row_value
            previous_row = row
        if observed_rows:
            if next_value <= base_value or previous != next_value:
                raise StoreError("observed-through-mismatch")
        elif next_value != base_value:
            raise StoreError("empty-observation-cursor-change")

        self_message_timestamps = [
            row.message_ts for row in observed_rows if row.kind == "self-message"
        ]
        if [decision.message_ts for decision in decisions] != self_message_timestamps:
            raise StoreError("events-do-not-cover-self-message-rows")
        for decision in decisions:
            if (
                decision.team_id != policy.team_id
                or decision.user_id != policy.user_id
                or decision.conversation_id != policy.conversation_id
            ):
                raise StoreError("event-source-not-allowlisted")

        checked = []
        for original in decisions:
            decision = _decision_at_ingest_time(
                original, current, allow_stale_native_pause=True
            )
            if (
                decision.accepted
                and decision.command not in NATIVE_CUA_ALLOWED_COMMANDS
            ):
                decision = replace(
                    decision,
                    accepted=False,
                    reason="command-not-allowed-for-native-cua",
                    command=None,
                    request_id=None,
                )
            checked.append(decision)
        digest = source_batch_digest(
            source,
            policy,
            base_cursor,
            next_cursor,
            checked,
            observed_rows=observed_rows,
            poll_id=poll_id,
            workspace_host=workspace_host,
        )
        poll_record = self._poll_record(
            current=current,
            source=source,
            policy=policy,
            workspace_host=workspace_host,
            poll_id=poll_id,
            outcome="verified",
            reason="continuous-stable-bottom",
            base_observed_through=base_cursor,
            observed_through=next_cursor,
            batch_digest=digest,
            observed_row_count=len(observed_rows),
            event_count=len(checked),
        )
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            latest = self._latest_source_cursor_unlocked(source, policy)
            if latest is None:
                raise StoreError("source-not-bootstrapped")
            persisted_cursor = latest.get("cursor")
            # Poll identity is part of the transaction boundary. A conflicting
            # ID must be rejected before a resume/command or cursor is appended.
            poll_duplicate = self._poll_duplicate_unlocked(poll_record)

            if observed_rows and persisted_cursor == next_cursor:
                if latest.get("batchDigest") != digest:
                    raise StoreError("source-cursor-digest-conflict")
                if not poll_duplicate:
                    self._append(self.source_poll_ledger_path, poll_record)
                self._atomic_write(
                    self.source_cursor_path, self._cursor_public(source, policy, latest)
                )
                self._atomic_write(self.state_path, self._snapshot_unlocked(current))
                return {
                    "schemaVersion": SCHEMA_VERSION,
                    "committed": True,
                    "duplicateBatch": True,
                    "sourceCursor": persisted_cursor,
                    "observedThrough": persisted_cursor,
                    "pollId": poll_id,
                    "pollOutcome": "verified",
                    "batchDigest": digest,
                    "eventResults": [],
                }

            if persisted_cursor != base_cursor:
                raise StoreError("source-cursor-conflict")

            if not observed_rows:
                if not poll_duplicate:
                    self._append(self.source_poll_ledger_path, poll_record)
                self._atomic_write(
                    self.source_cursor_path, self._cursor_public(source, policy, latest)
                )
                self._atomic_write(self.state_path, self._snapshot_unlocked(current))
                return {
                    "schemaVersion": SCHEMA_VERSION,
                    "committed": True,
                    "duplicateBatch": poll_duplicate,
                    "sourceCursor": persisted_cursor,
                    "observedThrough": persisted_cursor,
                    "pollId": poll_id,
                    "pollOutcome": "verified",
                    "batchDigest": digest,
                    "acceptedCount": 0,
                    "duplicateEventCount": 0,
                    "rejectedCount": 0,
                    "eventResults": [],
                }

            seen: set[str] = set()
            for decision in checked:
                if decision.event_id in seen:
                    raise StoreError("duplicate-event-id-in-batch")
                seen.add(decision.event_id)
                if decision.event_id in self._known_event_ids():
                    stored = self._stored_event_fingerprint(decision.event_id)
                    if stored != self._decision_fingerprint(decision):
                        raise StoreError("event-id-collision")

            results = [
                self._record_decision_unlocked(decision, current) for decision in checked
            ]
            cursor_record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "source-cursor",
                "at": format_utc(current),
                "source": source,
                "teamId": policy.team_id,
                "userId": policy.user_id,
                "conversationId": policy.conversation_id,
                "baseCursor": base_cursor,
                "cursor": next_cursor,
                "activationCutoff": latest["activationCutoff"],
                "batchDigest": digest,
                "eventCount": len(checked),
            }
            self._append(self.source_cursor_ledger_path, cursor_record)
            if not poll_duplicate:
                self._append(self.source_poll_ledger_path, poll_record)
            public_cursor = self._cursor_public(source, policy, cursor_record)
            self._atomic_write(self.source_cursor_path, public_cursor)
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "committed": True,
                "duplicateBatch": False,
                "sourceCursor": next_cursor,
                "observedThrough": next_cursor,
                "pollId": poll_id,
                "pollOutcome": "verified",
                "batchDigest": digest,
                "acceptedCount": sum(1 for result in results if result["accepted"]),
                "duplicateEventCount": sum(1 for result in results if result["duplicate"]),
                "rejectedCount": sum(
                    1
                    for result in results
                    if not result["accepted"] and not result["duplicate"]
                ),
                "eventResults": results,
            }

    def status_delivery_state(self, event_id: str) -> dict[str, Any]:
        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            records = [
                record
                for record in self._status_delivery_records()
                if record["eventId"] == event_id
            ]
            delivered = next(
                (record for record in reversed(records) if record["outcome"] == "delivered"),
                None,
            )
            return {
                "schemaVersion": SCHEMA_VERSION,
                "eventId": event_id,
                "delivered": delivered is not None,
                "lastOutcome": records[-1]["outcome"] if records else None,
            }

    def pending_status_source(
        self, event_id: str, *, now: Optional[dt.datetime] = None
    ) -> dict[str, str]:
        """Return only the verified source IDs for one live status request."""

        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            queue = {record["eventId"]: record for record in self._command_records()}
            record = queue.get(event_id)
            if record is None or record.get("command") != "status":
                raise StoreError("event-is-not-pending-status")
            if event_id in self._consumed():
                raise StoreError("status-command-already-consumed")
            expires_at = record.get("expiresAt")
            try:
                expired = not isinstance(expires_at, str) or parse_utc(expires_at) <= current
            except ValueError:
                expired = True
            if expired:
                raise StoreError("status-command-expired")
            source = record["source"]
            return {
                "teamId": source["teamId"],
                "userId": source["userId"],
                "conversationId": source["conversationId"],
            }

    def record_status_delivery(
        self,
        event_id: str,
        *,
        outcome: str,
        reason: str,
        payload_sha256: str,
        team_id: str,
        conversation_id: str,
        http_status: Optional[int],
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        if not SHA256_HEX.fullmatch(payload_sha256):
            raise StoreError("invalid-payload-digest")
        if not SLACK_TEAM_ID.fullmatch(team_id):
            raise StoreError("invalid-delivery-team-id")
        if not SLACK_CONVERSATION_ID.fullmatch(conversation_id):
            raise StoreError("invalid-delivery-conversation-id")
        valid_result = (
            outcome == "delivered" and reason == "webhook-ok" and http_status == 200
        ) or (
            outcome == "failed"
            and reason in {"network-error", "http-error", "unexpected-response"}
            and (
                http_status is None
                or (
                    isinstance(http_status, int)
                    and not isinstance(http_status, bool)
                    and 100 <= http_status <= 599
                )
            )
        )
        if not valid_result:
            raise StoreError("invalid-status-delivery-result")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            existing = [
                record
                for record in self._status_delivery_records()
                if record["eventId"] == event_id
            ]
            delivered = next(
                (record for record in reversed(existing) if record["outcome"] == "delivered"),
                None,
            )
            if delivered is not None:
                return {
                    "schemaVersion": SCHEMA_VERSION,
                    "recorded": False,
                    "duplicate": True,
                    "eventId": event_id,
                    "outcome": "delivered",
                }
            queue = {record["eventId"]: record for record in self._command_records()}
            command_record = queue.get(event_id)
            if command_record is None or command_record.get("command") != "status":
                raise StoreError("event-is-not-pending-status")
            source = command_record["source"]
            if source["teamId"] != team_id or source["conversationId"] != conversation_id:
                raise StoreError("status-delivery-destination-mismatch")
            if event_id in self._consumed():
                raise StoreError("status-command-already-consumed")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "status-delivery",
                "at": format_utc(current),
                "eventId": event_id,
                "outcome": outcome,
                "reason": reason,
                "payloadSha256": payload_sha256,
                "teamId": team_id,
                "conversationId": conversation_id,
                "httpStatus": http_status,
            }
            self._append(self.status_delivery_path, record)
            return {
                "schemaVersion": SCHEMA_VERSION,
                "recorded": True,
                "duplicate": False,
                "eventId": event_id,
                "outcome": outcome,
            }

    def audit_runtime(
        self,
        outcome: str,
        reason: str,
        *,
        retry_after_seconds: Optional[int] = None,
        now: Optional[dt.datetime] = None,
    ) -> None:
        """Append a transport lifecycle record without URLs, tokens, or message text."""

        if outcome not in {"connected", "disconnected", "retrying", "failed", "ignored"}:
            raise StoreError("invalid-runtime-audit-outcome")
        if not re.fullmatch(r"[a-z0-9-]{1,80}", reason):
            raise StoreError("invalid-runtime-audit-reason")
        if retry_after_seconds is not None and (
            isinstance(retry_after_seconds, bool)
            or not isinstance(retry_after_seconds, int)
            or retry_after_seconds < 0
        ):
            raise StoreError("invalid-runtime-retry-after")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        record = {
            "schemaVersion": SCHEMA_VERSION,
            "recordType": "runtime",
            "at": format_utc(current),
            "outcome": outcome,
            "reason": reason,
            "retryAfterSeconds": retry_after_seconds,
        }
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            self._append(self.audit_path, record)

    @staticmethod
    def _audit_record(
        decision: IngressDecision, current: dt.datetime, outcome: str, reason: str
    ) -> dict[str, Any]:
        # Rejected/free-form text is deliberately represented only by a digest and length.
        return {
            "schemaVersion": SCHEMA_VERSION,
            "recordType": "audit",
            "at": format_utc(current),
            "eventId": decision.event_id,
            "outcome": outcome,
            "reason": reason,
            "command": decision.command if decision.accepted else None,
            "requestId": decision.request_id if decision.accepted else None,
            "source": {
                "teamId": decision.team_id,
                "userId": decision.user_id,
                "conversationId": decision.conversation_id,
                "messageTs": decision.message_ts,
            },
            "textSha256": decision.text_sha256,
            "textLength": decision.text_length,
        }

    def _consumed(self) -> dict[str, dict[str, Any]]:
        consumed: dict[str, dict[str, Any]] = {}
        for record in self._consumption_records():
            event_id = record["eventId"]
            previous = consumed.get(event_id)
            if previous is None and (
                record.get("command") == "approve-safe"
                and record.get("outcome") == "applied"
            ):
                raise StoreError("invalid-consumption-ledger")
            if previous is not None and not (
                previous.get("outcome") == "claimed"
                and record.get("outcome") in {"applied", "refused"}
                and record.get("command") == "approve-safe"
                and record.get("requestId") == previous.get("requestId")
            ):
                raise StoreError("invalid-consumption-ledger")
            consumed[event_id] = record
        return consumed

    def _native_poll_state_unlocked(self) -> Optional[dict[str, Any]]:
        records = list(self._source_poll_records())
        if not records:
            return None
        record = records[-1]
        policy = CommandPolicy(
            record["teamId"], record["userId"], record["conversationId"]
        )
        latest_cursor = self._latest_source_cursor_unlocked(
            SLACK_NATIVE_CUA_SOURCE, policy
        )
        cursor_consistent = bool(
            latest_cursor is not None
            and latest_cursor.get("cursor") == record["observedThrough"]
            and (
                record["outcome"] != "verified"
                or record["observedRowCount"] == 0
                or latest_cursor.get("batchDigest") == record["batchDigest"]
            )
        )
        return {
            "source": record["source"],
            "teamId": record["teamId"],
            "userId": record["userId"],
            "conversationId": record["conversationId"],
            "workspaceHost": record["workspaceHost"],
            "pollId": record["pollId"],
            "outcome": record["outcome"],
            "reason": record["reason"],
            "recordedAt": record["at"],
            "verifiedPollAt": record["at"] if record["outcome"] == "verified" else None,
            "baseObservedThrough": record["baseObservedThrough"],
            "observedThrough": record["observedThrough"],
            "batchDigest": record["batchDigest"],
            "observedRowCount": record["observedRowCount"],
            "eventCount": record["eventCount"],
            "cursorConsistent": cursor_consistent,
        }

    def _snapshot_unlocked(self, current: dt.datetime) -> dict[str, Any]:
        commands = list(self._command_records())
        consumed = self._consumed()
        paused = False
        pause_source: Optional[str] = None
        pending = []
        for record in commands:
            command = record.get("command")
            event_id = record.get("eventId")
            if command == "pause":
                paused = True
                pause_source = event_id if isinstance(event_id, str) else None
            elif command == "resume":
                paused = False
                pause_source = event_id if isinstance(event_id, str) else None

            if not isinstance(event_id, str) or event_id in consumed:
                continue
            expires_at = record.get("expiresAt")
            expired = False
            if isinstance(expires_at, str):
                try:
                    expired = parse_utc(expires_at) <= current
                except ValueError:
                    expired = True
            pending.append(
                {
                    "eventId": event_id,
                    "command": command,
                    "requestId": record.get("requestId"),
                    "receivedAt": record.get("receivedAt"),
                    "expiresAt": expires_at,
                    "expired": expired,
                }
            )

        return {
            "schemaVersion": SCHEMA_VERSION,
            "generatedAt": format_utc(current),
            "paused": paused,
            "pauseStateSourceEventId": pause_source,
            "pending": pending,
            "pendingStatusCount": sum(
                1 for item in pending if item["command"] == "status" and not item["expired"]
            ),
            "pendingApproveSafeCount": sum(
                1 for item in pending if item["command"] == "approve-safe" and not item["expired"]
            ),
            "nativePoll": self._native_poll_state_unlocked(),
            "commandCount": len(commands),
            "consumedCount": len(consumed),
        }

    def snapshot(self, *, now: Optional[dt.datetime] = None) -> dict[str, Any]:
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            snapshot = self._snapshot_unlocked(current)
            self._atomic_write(self.state_path, snapshot)
            return snapshot

    def acknowledge(
        self,
        event_id: str,
        outcome: str,
        *,
        actor: str = "fidgeting-cursor-heartbeat",
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        if outcome not in TERMINAL_OUTCOMES:
            raise StoreError("invalid-consumption-outcome")
        if actor != "fidgeting-cursor-heartbeat":
            raise StoreError("invalid-consumption-actor")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            queue = {
                record.get("eventId"): record
                for record in self._command_records()
                if isinstance(record.get("eventId"), str)
            }
            if event_id not in queue:
                raise StoreError("event-not-in-command-queue")
            consumed = self._consumed()
            if event_id in consumed:
                return {
                    "schemaVersion": SCHEMA_VERSION,
                    "acknowledged": False,
                    "duplicate": True,
                    "eventId": event_id,
                    "outcome": consumed[event_id].get("outcome"),
                }
            command = queue[event_id].get("command")
            request_id = queue[event_id].get("requestId")
            valid_for_command = {
                "status": {"reported", "refused", "expired"},
                "pause": {"applied", "refused"},
                "resume": {"applied", "refused"},
                "approve-safe": {"refused", "expired"},
            }
            if outcome not in valid_for_command.get(command, set()):
                raise StoreError("outcome-not-valid-for-command")
            if command == "status" and outcome == "reported":
                source = queue[event_id].get("source")
                if not isinstance(source, Mapping) or not any(
                    record["eventId"] == event_id
                    and record["outcome"] == "delivered"
                    and record["teamId"] == source.get("teamId")
                    and record["conversationId"] == source.get("conversationId")
                    for record in self._status_delivery_records()
                ):
                    raise StoreError("status-not-delivered")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "consumption",
                "at": format_utc(current),
                "eventId": event_id,
                "command": command,
                "requestId": request_id,
                "outcome": outcome,
                "actor": actor,
            }
            self._append(self.consumption_path, record)
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "acknowledged": True,
                "duplicate": False,
                "eventId": event_id,
                "command": command,
                "requestId": request_id,
                "outcome": outcome,
            }

    def claim_approval(
        self,
        event_id: str,
        request_id: str,
        *,
        actor: str = "fidgeting-cursor-heartbeat",
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        """Atomically make one matching approval non-replayable before a click."""

        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        if not APPROVAL_REQUEST_ID.fullmatch(request_id):
            raise StoreError("invalid-approval-request-id")
        if actor != "fidgeting-cursor-heartbeat":
            raise StoreError("invalid-consumption-actor")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            queue = {
                record.get("eventId"): record
                for record in self._command_records()
                if isinstance(record.get("eventId"), str)
            }
            command_record = queue.get(event_id)
            if command_record is None:
                raise StoreError("event-not-in-command-queue")
            if command_record.get("command") != "approve-safe":
                raise StoreError("event-is-not-approval")
            if command_record.get("requestId") != request_id:
                raise StoreError("approval-request-id-mismatch")
            expires_at = command_record.get("expiresAt")
            try:
                expired = not isinstance(expires_at, str) or parse_utc(expires_at) <= current
            except ValueError:
                expired = True
            if expired:
                raise StoreError("approval-expired")

            consumed = self._consumed()
            if event_id in consumed:
                return {
                    "schemaVersion": SCHEMA_VERSION,
                    "claimed": False,
                    "duplicate": True,
                    "eventId": event_id,
                    "requestId": request_id,
                    "outcome": consumed[event_id].get("outcome"),
                }
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "claim",
                "at": format_utc(current),
                "eventId": event_id,
                "command": "approve-safe",
                "requestId": request_id,
                "outcome": "claimed",
                "actor": actor,
            }
            self._append(self.consumption_path, record)
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "claimed": True,
                "duplicate": False,
                "eventId": event_id,
                "requestId": request_id,
                "outcome": "claimed",
            }

    def finalize_approval(
        self,
        event_id: str,
        request_id: str,
        outcome: str,
        *,
        actor: str = "fidgeting-cursor-heartbeat",
        now: Optional[dt.datetime] = None,
    ) -> dict[str, Any]:
        """Append the verified terminal result for an already claimed approval."""

        if not SLACK_EVENT_ID.fullmatch(event_id):
            raise StoreError("invalid-event-id")
        if not APPROVAL_REQUEST_ID.fullmatch(request_id):
            raise StoreError("invalid-approval-request-id")
        if outcome not in {"applied", "refused"}:
            raise StoreError("invalid-approval-final-outcome")
        if actor != "fidgeting-cursor-heartbeat":
            raise StoreError("invalid-consumption-actor")
        current = (now or utc_now()).astimezone(dt.timezone.utc)
        with self.locked():
            self._assert_authoritative_ledgers_unlocked()
            queue = {
                record.get("eventId"): record
                for record in self._command_records()
                if isinstance(record.get("eventId"), str)
            }
            command_record = queue.get(event_id)
            if command_record is None:
                raise StoreError("event-not-in-command-queue")
            if command_record.get("command") != "approve-safe":
                raise StoreError("event-is-not-approval")
            if command_record.get("requestId") != request_id:
                raise StoreError("approval-request-id-mismatch")
            consumed = self._consumed()
            previous = consumed.get(event_id)
            if previous is None or previous.get("outcome") != "claimed":
                if previous and previous.get("outcome") in TERMINAL_OUTCOMES:
                    return {
                        "schemaVersion": SCHEMA_VERSION,
                        "finalized": False,
                        "duplicate": True,
                        "eventId": event_id,
                        "requestId": request_id,
                        "outcome": previous.get("outcome"),
                    }
                raise StoreError("approval-not-claimed")
            record = {
                "schemaVersion": SCHEMA_VERSION,
                "recordType": "consumption",
                "at": format_utc(current),
                "eventId": event_id,
                "command": "approve-safe",
                "requestId": request_id,
                "outcome": outcome,
                "actor": actor,
            }
            self._append(self.consumption_path, record)
            self._atomic_write(self.state_path, self._snapshot_unlocked(current))
            return {
                "schemaVersion": SCHEMA_VERSION,
                "finalized": True,
                "duplicate": False,
                "eventId": event_id,
                "requestId": request_id,
                "outcome": outcome,
            }


def load_event(path: Optional[Path]) -> Mapping[str, Any]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise BridgeError("invalid-input-json") from exc
    if not isinstance(value, dict):
        raise BridgeError("input-must-be-object")
    return value


def default_runtime_root() -> Path:
    return Path(__file__).resolve().parents[1] / "runtime" / "slack-command-bridge"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="sanitized Slack event JSON; stdin if omitted")
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    parser.add_argument("--dry-run", action="store_true", help="evaluate only; no files or network")
    parser.add_argument(
        "--now",
        help="test-only RFC3339 clock override; omit during real ingestion",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = CommandPolicy.from_values(
            args.allowed_team_id, args.allowed_user_id, args.allowed_conversation_id
        )
        event = load_event(args.input)
        current = parse_utc(args.now) if args.now else utc_now()
        decision = evaluate_event(event, policy, now=current)
        store = AppendOnlyCommandStore(args.runtime_root)
        result = store.ingest(decision, now=current, dry_run=args.dry_run)
        sys.stdout.write(canonical_json(result) + "\n")
        return 0 if result["accepted"] or result["duplicate"] else 2
    except BridgeError as exc:
        sys.stderr.write(canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
