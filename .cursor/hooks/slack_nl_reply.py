#!/usr/bin/env python3
"""Send one bounded NL-router reply to the attested Slack self-DM.

The input is a strict union.  Chat text is bounded and stripped of Slack
mention syntax; every other reply is built from fixed local templates.  The
helper verifies the NL event and exact source policy, claims delivery in an
append-only ledger before the network call, and never retries an uncertain
POST.  It does not print response text, confirmation tokens, or webhook data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import os
import re
import stat
import sys
import unicodedata
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from slack_command_bridge import (
    BridgeError,
    CommandPolicy,
    SCHEMA_VERSION,
    canonical_json,
    parse_utc,
    utc_now,
)
from slack_nl_router import (
    CONFIRM_TOKEN,
    DEFAULT_CATALOG_PATH,
    NaturalLanguageError,
    NaturalLanguageStore,
    default_runtime_root,
    load_task_catalog,
    validate_observation,
)
from slack_status_reply import (
    DEFAULT_ATTESTATION_PATH,
    DEFAULT_ENV_PATH,
    _load_destination_attestation,
    _load_webhook,
    _post,
)


MAX_INPUT_BYTES = 65_536
MAX_CHAT_CHARS = 1200
REPLY_KEYS = {
    "schemaVersion",
    "requestEventId",
    "replyKind",
    "responseText",
    "clarificationCode",
    "intentId",
    "confirmationToken",
    "observation",
}
REPLY_KINDS = frozenset(
    {"chat", "status", "clarification", "confirmation-preview", "receipt"}
)
CLARIFICATIONS = {
    "target-ambiguous": (
        "我还没有执行。你指的是 “Card draw scene research”、"
        "“Mobile app version issue” 还是 “Conversation freezing issue”？"
    ),
    "success-criteria-ambiguous": "我还没有执行。请只补充这次完成的判断标准。",
    "unsupported-request": "我还没有执行。这个请求不能从 Slack 自动执行，请在 Codex 中继续。",
}
RECEIPTS = {
    "low-risk-awaiting-atomic-claim": "请求已登记，但尚未验证执行结果。",
    "target-authority-inspect-only": "该目标目前只允许只读检查；没有执行更改。",
    "cancelled": "请求已取消。",
    "cancel-too-late": "请求已被领取或结果未知；不会自动重放，请在 Codex 中检查。",
    "cancel-target-not-found": "没有找到可取消的请求；没有执行任何操作。",
    "direct-confirmation-required": "原生 Slack 不能授权该操作；没有执行任何操作。",
    "prior-route-incomplete-resend": "上次路由结果不确定，未自动重放；如仍需要请重新发送请求。",
    "recipient-action-not-allowed": "该动作不能交给所选执行端；没有执行任何操作。",
}
STATUS_LABELS = {
    "running": "运行中",
    "idle": "空闲",
    "safe-pending": "等待安全动作",
    "risky-pending": "等待人工处理",
    "failed": "失败",
    "waiting-user": "等待用户",
    "complete": "完成",
    "archived": "已归档",
}
SLACK_SPECIAL = re.compile(r"<(?:!|@|#)[^>]*>")
RESERVED_MARKER = "FIDGETING_SLACK_REQUEST"


def _read_input(path: Optional[Path]) -> Mapping[str, Any]:
    try:
        if path is None:
            raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
        else:
            descriptor = os.open(
                str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                info = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(info.st_mode)
                    or info.st_uid != os.getuid()
                    or stat.S_IMODE(info.st_mode) != 0o600
                    or info.st_size > MAX_INPUT_BYTES
                ):
                    raise NaturalLanguageError("invalid-nl-reply-input")
                raw = os.read(descriptor, MAX_INPUT_BYTES + 1).decode(
                    "utf-8", "strict"
                )
            finally:
                os.close(descriptor)
            if len(raw.encode("utf-8", "strict")) > MAX_INPUT_BYTES:
                raise NaturalLanguageError("invalid-nl-reply-input")
    except (OSError, UnicodeError) as exc:
        raise NaturalLanguageError("invalid-nl-reply-input") from exc
    if len(raw.encode("utf-8", "replace")) > MAX_INPUT_BYTES:
        raise NaturalLanguageError("nl-reply-input-too-large")
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise NaturalLanguageError("invalid-nl-reply-json") from exc
    if not isinstance(value, dict) or set(value) != REPLY_KEYS:
        raise NaturalLanguageError("invalid-nl-reply-fields")
    return value


def _safe_chat_text(value: Any) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= MAX_CHAT_CHARS:
        raise NaturalLanguageError("invalid-chat-response")
    if value != unicodedata.normalize("NFC", value) or value.count("\n") > 24:
        raise NaturalLanguageError("invalid-chat-response")
    if any(
        character not in {"\n", "\t"}
        and unicodedata.category(character) in {"Cc", "Cf"}
        for character in value
    ):
        raise NaturalLanguageError("invalid-chat-response")
    guard_text = unicodedata.normalize("NFKC", value).casefold()
    if SLACK_SPECIAL.search(value) or RESERVED_MARKER.casefold() in guard_text:
        raise NaturalLanguageError("unsafe-chat-response")
    return value


def _validate_union(value: Mapping[str, Any]) -> dict[str, Any]:
    if value.get("schemaVersion") != SCHEMA_VERSION:
        raise NaturalLanguageError("unsupported-nl-reply-schema")
    event_id = value.get("requestEventId")
    kind = value.get("replyKind")
    if not isinstance(event_id, str) or not re.fullmatch(r"[A-Za-z0-9._:-]{1,160}", event_id):
        raise NaturalLanguageError("invalid-nl-reply-event-id")
    if kind not in REPLY_KINDS:
        raise NaturalLanguageError("invalid-nl-reply-kind")
    response = value.get("responseText")
    clarification = value.get("clarificationCode")
    intent_id = value.get("intentId")
    token = value.get("confirmationToken")
    observation = value.get("observation")
    if kind == "chat":
        _safe_chat_text(response)
        valid = clarification is None and intent_id is None and token is None and observation is None
    elif kind == "status":
        valid = response is None and clarification is None and intent_id is None and token is None and isinstance(observation, dict)
    elif kind == "clarification":
        valid = response is None and clarification in CLARIFICATIONS and intent_id is None and token is None and observation is None
    elif kind == "confirmation-preview":
        valid = (
            response is None
            and clarification is None
            and isinstance(intent_id, str)
            and isinstance(token, str)
            and CONFIRM_TOKEN.fullmatch(token) is not None
            and observation is None
        )
    else:
        valid = response is None and clarification is None and intent_id is None and token is None and observation is None
    if not valid:
        raise NaturalLanguageError("invalid-nl-reply-payload")
    return dict(value)


def _build_payload(
    value: Mapping[str, Any],
    *,
    store: NaturalLanguageStore,
    event: Mapping[str, Any],
    catalog,
    now,
) -> dict[str, str]:
    kind = value["replyKind"]
    if kind == "chat":
        text = "Fidgeting 助手\n{}".format(_safe_chat_text(value["responseText"]))
    elif kind == "clarification":
        expected = event.get("clarificationCode") or event.get("reason")
        if value["clarificationCode"] != expected:
            raise NaturalLanguageError("clarification-code-mismatch")
        text = CLARIFICATIONS[value["clarificationCode"]]
    elif kind == "receipt":
        reason = event.get("reason")
        if reason not in RECEIPTS:
            raise NaturalLanguageError("unsupported-receipt-reason")
        text = RECEIPTS[reason]
    elif kind == "confirmation-preview":
        preview = store.confirmation_preview(
            value["requestEventId"],
            value["intentId"],
            value["confirmationToken"],
            now=now,
        )
        text = (
            "高风险请求预览\n"
            "目标：{}\n类别：{}\n未执行。若仍需继续，请打开 Codex 任务“{}”并直接输入：确认 {}\n"
            "有效期至：{}"
        ).format(
            preview["targetTitle"],
            preview["action"],
            catalog.controller["exactTitle"],
            value["confirmationToken"],
            preview["expiresAt"],
        )
    else:
        checked, _ = validate_observation(
            value["observation"],
            catalog=catalog,
            target_key=None,
            now=now,
            require_dispatch_ui=False,
        )
        states = {row["targetKey"]: row["state"] for row in checked["targets"]}
        lines = ["Fidgeting 当前状态（只读）"]
        for target in catalog.targets.values():
            lines.append("{}：{}".format(target.exact_title, STATUS_LABELS[states[target.target_key]]))
        lines.append("观测时间：{}".format(checked["observedAt"]))
        text = "\n".join(lines)
    return {"text": text, "unfurl_links": False, "unfurl_media": False}


def send_reply(
    value: Mapping[str, Any],
    *,
    store: NaturalLanguageStore,
    policy: CommandPolicy,
    env_file: Path,
    attestation_file: Path,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    now=None,
    dry_run: bool,
) -> dict[str, Any]:
    current = (now or utc_now()).astimezone(dt.timezone.utc)
    checked = _validate_union(value)
    event = store.pending_reply(checked["requestEventId"], checked["replyKind"])
    if (
        event.get("teamId") != policy.team_id
        or event.get("userId") != policy.user_id
        or event.get("conversationId") != policy.conversation_id
    ):
        raise NaturalLanguageError("nl-reply-source-not-allowlisted")
    catalog = load_task_catalog(catalog_path)
    webhook, webhook_path = _load_webhook(env_file)
    webhook_sha256 = hashlib.sha256(
        webhook.encode("utf-8", "strict")
    ).hexdigest()
    _load_destination_attestation(
        attestation_file,
        expected_team_id=policy.team_id,
        expected_conversation_id=policy.conversation_id,
        expected_webhook_sha256=webhook_sha256,
    )
    payload = _build_payload(checked, store=store, event=event, catalog=catalog, now=current)
    if dry_run:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "eventId": checked["requestEventId"],
            "replyKind": checked["replyKind"],
            "dryRun": True,
            "networkAttempted": False,
            "delivered": False,
        }
    if not store.claim_reply(checked["requestEventId"], checked["replyKind"], now=current):
        return {
            "schemaVersion": SCHEMA_VERSION,
            "eventId": checked["requestEventId"],
            "replyKind": checked["replyKind"],
            "duplicate": True,
            "networkAttempted": False,
            "delivered": False,
            "reason": "prior-delivery-outcome-not-retried",
        }
    del webhook
    try:
        http_status, response_body = _post(webhook_path, payload)
    except (OSError, http.client.HTTPException):
        store.finalize_reply(
            checked["requestEventId"],
            checked["replyKind"],
            "unknown",
            "network-outcome-unknown",
            None,
            now=current,
        )
        raise NaturalLanguageError("nl-reply-network-outcome-unknown")
    if http_status == 200 and response_body.strip() == "ok":
        store.finalize_reply(
            checked["requestEventId"],
            checked["replyKind"],
            "delivered",
            "webhook-ok",
            200,
            now=current,
        )
        return {
            "schemaVersion": SCHEMA_VERSION,
            "eventId": checked["requestEventId"],
            "replyKind": checked["replyKind"],
            "duplicate": False,
            "networkAttempted": True,
            "delivered": True,
        }
    reason = "http-error" if http_status != 200 else "unexpected-response"
    store.finalize_reply(
        checked["requestEventId"],
        checked["replyKind"],
        "failed",
        reason,
        http_status,
        now=current,
    )
    raise NaturalLanguageError("nl-reply-delivery-failed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="strict reply JSON; stdin if omitted")
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--destination-attestation", type=Path, default=DEFAULT_ATTESTATION_PATH)
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--send", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # Production CLI freshness always comes from the host wall clock.
        # Unit tests inject ``utc_now`` in process instead of exposing a bypass.
        current = utc_now()
        policy = CommandPolicy.from_values(
            args.allowed_team_id, args.allowed_user_id, args.allowed_conversation_id
        )
        result = send_reply(
            _read_input(args.input),
            store=NaturalLanguageStore(args.runtime_root),
            policy=policy,
            env_file=args.env_file,
            attestation_file=args.destination_attestation,
            now=current,
            dry_run=args.dry_run,
        )
        # The public result never includes response text, token, payload, or URL.
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except (BridgeError, ValueError) as exc:
        sys.stderr.write(canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
