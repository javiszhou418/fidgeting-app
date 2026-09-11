#!/usr/bin/env python3
"""Post one fixed-format structured status reply through a verified webhook.

The helper accepts no free-form Slack text. It never prints the webhook URL,
and a successful append-only delivery record is required before it reports
that the caller may acknowledge the matching status command.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from slack_command_bridge import (
    AppendOnlyCommandStore,
    BridgeError,
    CommandPolicy,
    SCHEMA_VERSION,
    SHA256_HEX,
    SLACK_EVENT_ID,
    canonical_json,
    default_runtime_root,
    parse_utc,
    utc_now,
)


DEFAULT_ENV_PATH = Path.home() / ".cursor" / "slack-progress.env"
DEFAULT_ATTESTATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "tools"
    / "cursor-night-supervisor"
    / "slack-status-destination.json"
)
MAX_INPUT_BYTES = 8192
STATUS_KEYS = {
    "schemaVersion",
    "requestEventId",
    "state",
    "paused",
    "safeActionPending",
    "riskyActionPending",
    "pendingStatusCount",
    "pendingApprovalCount",
    "blockingCode",
    "observedAt",
}
STATES = {
    "running": "运行中",
    "idle": "空闲",
    "safe-pending": "等待安全动作",
    "risky-pending": "等待人工处理",
    "failed": "失败",
    "waiting-user": "等待用户",
    "complete": "完成",
    "unknown": "未知",
}
BLOCKING_CODES = {
    "none": "无",
    "preflight": "预检未通过",
    "visual-approval": "等待视觉确认",
    "device-acceptance": "等待真机验收",
    "user-input": "等待用户输入",
    "workspace-mismatch": "Slack 工作区不匹配",
    "transport-error": "通知传输失败",
    "ledger-corrupt": "本地控制账本损坏",
    "unknown": "未知",
}
CONFIG_KEYS = {"SLACK_WEBHOOK_URL"}
ATTESTATION_KEYS = {
    "schemaVersion",
    "teamId",
    "conversationId",
    "verifiedAt",
    "evidenceCode",
    "webhookSha256",
}
DESTINATION_EVIDENCE_CODE = "verified-outgoing-self-dm-permalink-v1"


def _read_status(path: Optional[Path]) -> Mapping[str, Any]:
    if path:
        try:
            if path.stat().st_size > MAX_INPUT_BYTES:
                raise BridgeError("status-input-too-large")
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BridgeError("status-input-unreadable") from exc
    else:
        raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
        if len(raw.encode("utf-8", "replace")) > MAX_INPUT_BYTES:
            raise BridgeError("status-input-too-large")
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise BridgeError("invalid-status-json") from exc
    if not isinstance(value, dict) or set(value) != STATUS_KEYS:
        raise BridgeError("invalid-status-fields")
    return value


def _validate_status(value: Mapping[str, Any], *, now) -> dict[str, Any]:
    event_id = value.get("requestEventId")
    if value.get("schemaVersion") != SCHEMA_VERSION:
        raise BridgeError("unsupported-status-schema-version")
    if not isinstance(event_id, str) or not SLACK_EVENT_ID.fullmatch(event_id):
        raise BridgeError("invalid-event-id")
    state = value.get("state")
    blocking_code = value.get("blockingCode")
    if state not in STATES:
        raise BridgeError("invalid-status-state")
    if blocking_code not in BLOCKING_CODES:
        raise BridgeError("invalid-blocking-code")
    for key in ("paused", "safeActionPending", "riskyActionPending"):
        if not isinstance(value.get(key), bool):
            raise BridgeError("invalid-status-boolean")
    for key in ("pendingStatusCount", "pendingApprovalCount"):
        count = value.get(key)
        if isinstance(count, bool) or not isinstance(count, int) or not 0 <= count <= 100:
            raise BridgeError("invalid-status-count")
    try:
        observed_at = parse_utc(value.get("observedAt"))
    except (TypeError, ValueError) as exc:
        raise BridgeError("invalid-observed-at") from exc
    age = (now - observed_at).total_seconds()
    if age > 120:
        raise BridgeError("stale-status-observation")
    if age < -60:
        raise BridgeError("future-status-observation")
    return dict(value)


def _load_webhook(path: Path) -> tuple[str, str]:
    try:
        if path.is_symlink() or not path.is_file():
            raise BridgeError("status-webhook-config-unavailable")
        selected: dict[str, str] = {}
        with path.open(encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, raw_value = line.split("=", 1)
                key = key.strip()
                if key not in CONFIG_KEYS:
                    continue
                if key in selected:
                    raise BridgeError("duplicate-status-webhook-config-key")
                selected[key] = raw_value.strip().strip('"').strip("'")
    except OSError as exc:
        raise BridgeError("status-webhook-config-unavailable") from exc

    webhook = selected.get("SLACK_WEBHOOK_URL", "")
    parsed = urllib.parse.urlsplit(webhook)
    path_parts = parsed.path.split("/")
    if (
        parsed.scheme != "https"
        or parsed.netloc != "hooks.slack.com"
        or parsed.query
        or parsed.fragment
        or len(path_parts) != 5
        or path_parts[1] != "services"
        or not all(
            part and all(character.isalnum() or character in "_-" for character in part)
            for part in path_parts[2:]
        )
    ):
        raise BridgeError("invalid-status-webhook-url")
    return webhook, parsed.path


def _load_destination_attestation(
    path: Path,
    *,
    expected_team_id: str,
    expected_conversation_id: str,
    expected_webhook_sha256: str,
) -> dict[str, Any]:
    try:
        if path.is_symlink() or not path.is_file():
            raise BridgeError("status-destination-attestation-unavailable")
        value = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise BridgeError("invalid-status-destination-attestation") from exc
    except OSError as exc:
        raise BridgeError("status-destination-attestation-unavailable") from exc
    if not isinstance(value, dict) or set(value) != ATTESTATION_KEYS:
        raise BridgeError("invalid-status-destination-attestation")
    try:
        parse_utc(value.get("verifiedAt"))
    except (TypeError, ValueError) as exc:
        raise BridgeError("invalid-status-destination-attestation") from exc
    if value.get("schemaVersion") != SCHEMA_VERSION:
        raise BridgeError("invalid-status-destination-attestation")
    if value.get("evidenceCode") != DESTINATION_EVIDENCE_CODE:
        raise BridgeError("status-destination-evidence-not-verified")
    webhook_sha256 = value.get("webhookSha256")
    if (
        not isinstance(webhook_sha256, str)
        or not SHA256_HEX.fullmatch(webhook_sha256)
        or webhook_sha256 != expected_webhook_sha256
    ):
        raise BridgeError("status-webhook-not-attested")
    if value.get("teamId") != expected_team_id:
        raise BridgeError("status-webhook-team-not-verified")
    if value.get("conversationId") != expected_conversation_id:
        raise BridgeError("status-webhook-conversation-not-verified")
    return value


def _payload(value: Mapping[str, Any]) -> dict[str, str]:
    yes_no = {True: "是", False: "否"}
    lines = [
        "Fidgeting Cursor 状态",
        "状态：{}".format(STATES[value["state"]]),
        "已暂停：{}".format(yes_no[value["paused"]]),
        "待处理安全动作：{}".format(yes_no[value["safeActionPending"]]),
        "待处理风险动作：{}".format(yes_no[value["riskyActionPending"]]),
        "待回复状态请求：{}".format(value["pendingStatusCount"]),
        "待处理审批：{}".format(value["pendingApprovalCount"]),
        "阻塞：{}".format(BLOCKING_CODES[value["blockingCode"]]),
        "观测时间：{}".format(value["observedAt"]),
    ]
    return {"text": "\n".join(lines)}


def _post(path: str, payload: Mapping[str, Any]) -> tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    connection = http.client.HTTPSConnection("hooks.slack.com", 443, timeout=10)
    try:
        connection.request(
            "POST", path, body=body, headers={"Content-Type": "application/json"}
        )
        response = connection.getresponse()
        response_body = response.read(64).decode("utf-8", "replace")
        return response.status, response_body
    finally:
        connection.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="structured local status JSON; stdin if omitted")
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument(
        "--destination-attestation",
        type=Path,
        default=DEFAULT_ATTESTATION_PATH,
    )
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    parser.add_argument("--now", help="test-only RFC3339 clock override")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="validate only; no network/audit")
    mode.add_argument("--send", action="store_true", help="perform one verified webhook POST")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        current = parse_utc(args.now) if args.now else utc_now()
        policy = CommandPolicy.from_values(
            args.allowed_team_id, args.allowed_user_id, args.allowed_conversation_id
        )
        status = _validate_status(_read_status(args.input), now=current)
        webhook, webhook_path = _load_webhook(args.env_file)
        webhook_sha256 = hashlib.sha256(webhook.encode("utf-8", "strict")).hexdigest()
        _load_destination_attestation(
            args.destination_attestation,
            expected_team_id=policy.team_id,
            expected_conversation_id=policy.conversation_id,
            expected_webhook_sha256=webhook_sha256,
        )
        payload = _payload(status)
        payload_sha256 = hashlib.sha256(
            canonical_json(payload).encode("utf-8", "strict")
        ).hexdigest()
        store = AppendOnlyCommandStore(args.runtime_root)
        source = store.pending_status_source(status["requestEventId"], now=current)
        if (
            source["teamId"] != policy.team_id
            or source["userId"] != policy.user_id
            or source["conversationId"] != policy.conversation_id
        ):
            raise BridgeError("status-request-source-not-allowlisted")

        existing = store.status_delivery_state(status["requestEventId"])
        if existing["delivered"]:
            result = {
                "schemaVersion": SCHEMA_VERSION,
                "delivered": True,
                "duplicate": True,
                "ackAllowed": True,
                "eventId": status["requestEventId"],
            }
        elif args.dry_run:
            result = {
                "schemaVersion": SCHEMA_VERSION,
                "delivered": False,
                "duplicate": False,
                "dryRun": True,
                "networkAttempted": False,
                "ackAllowed": False,
                "eventId": status["requestEventId"],
                "payloadSha256": payload_sha256,
            }
        else:
            del webhook  # The URL is validated but only its path is sent to the pinned host.
            try:
                http_status, response_body = _post(webhook_path, payload)
            except (OSError, http.client.HTTPException):
                store.record_status_delivery(
                    status["requestEventId"],
                    outcome="failed",
                    reason="network-error",
                    payload_sha256=payload_sha256,
                    team_id=policy.team_id,
                    conversation_id=policy.conversation_id,
                    http_status=None,
                    now=current,
                )
                raise BridgeError("status-webhook-network-error")
            if http_status == 200 and response_body.strip() == "ok":
                recorded = store.record_status_delivery(
                    status["requestEventId"],
                    outcome="delivered",
                    reason="webhook-ok",
                    payload_sha256=payload_sha256,
                    team_id=policy.team_id,
                    conversation_id=policy.conversation_id,
                    http_status=http_status,
                    now=current,
                )
                result = {
                    "schemaVersion": SCHEMA_VERSION,
                    "delivered": True,
                    "duplicate": recorded["duplicate"],
                    "ackAllowed": True,
                    "eventId": status["requestEventId"],
                }
            else:
                reason = "http-error" if http_status != 200 else "unexpected-response"
                store.record_status_delivery(
                    status["requestEventId"],
                    outcome="failed",
                    reason=reason,
                    payload_sha256=payload_sha256,
                    team_id=policy.team_id,
                    conversation_id=policy.conversation_id,
                    http_status=http_status,
                    now=current,
                )
                raise BridgeError("status-webhook-delivery-failed")
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except (BridgeError, ValueError) as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
