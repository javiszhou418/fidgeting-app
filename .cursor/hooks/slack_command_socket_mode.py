#!/usr/bin/env python3
"""Optional Socket Mode transport for ``slack_command_bridge``.

This adapter receives Slack Events API envelopes, converts only ordinary
message events to the bridge's sanitized schema, durably ingests them, and then
acknowledges the Socket Mode envelope. It never posts a Slack message and does
not use a bot token. Running it requires an explicit ``--run`` flag.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from slack_command_bridge import (
    AppendOnlyCommandStore,
    BridgeError,
    CommandPolicy,
    SCHEMA_VERSION,
    canonical_json,
    default_runtime_root,
    evaluate_event,
    utc_now,
)


CONNECTIONS_OPEN_URL = "https://slack.com/api/apps.connections.open"
PERMANENT_SLACK_ERRORS = {
    "access_denied",
    "enterprise_is_restricted",
    "invalid_auth",
    "missing_scope",
    "not_allowed_token_type",
    "team_access_not_granted",
    "token_expired",
    "token_revoked",
}


class RetryableTransportError(BridgeError):
    def __init__(self, reason: str, retry_after: Optional[int] = None):
        super().__init__(reason)
        self.reason = reason
        self.retry_after = retry_after


class PermanentTransportError(BridgeError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class SocketEvent:
    envelope_id: Optional[str]
    sanitized: Optional[dict[str, Any]]
    control: str
    ignore_reason: Optional[str] = None


def _safe_reason(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        normalized = value.lower().replace("_", "-")
        if normalized and all(character.isalnum() or character == "-" for character in normalized):
            return normalized[:80]
    return fallback


def socket_event(envelope: Mapping[str, Any]) -> SocketEvent:
    envelope_id = envelope.get("envelope_id")
    if not isinstance(envelope_id, str):
        envelope_id = None
    envelope_type = envelope.get("type")
    if envelope_type == "hello":
        return SocketEvent(envelope_id, None, "hello")
    if envelope_type == "disconnect":
        return SocketEvent(
            envelope_id,
            None,
            "disconnect",
            _safe_reason(envelope.get("reason"), "server-disconnect"),
        )
    if envelope_type != "events_api":
        return SocketEvent(envelope_id, None, "ignore", "unsupported-envelope")

    payload = envelope.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "event_callback":
        return SocketEvent(envelope_id, None, "ignore", "unsupported-events-payload")
    event = payload.get("event")
    if not isinstance(event, dict) or event.get("type") != "message":
        return SocketEvent(envelope_id, None, "ignore", "not-message-event")
    if event.get("subtype") is not None:
        return SocketEvent(envelope_id, None, "ignore", "message-subtype")
    if event.get("bot_id") is not None or event.get("app_id") is not None:
        return SocketEvent(envelope_id, None, "ignore", "bot-message")
    if event.get("thread_ts") is not None:
        return SocketEvent(envelope_id, None, "ignore", "thread-message")

    return SocketEvent(
        envelope_id,
        {
            "schemaVersion": SCHEMA_VERSION,
            "team_id": payload.get("team_id"),
            "user_id": event.get("user"),
            "conversation_id": event.get("channel"),
            "event_id": payload.get("event_id"),
            "message_ts": event.get("ts"),
            "text": event.get("text"),
        },
        "ingest",
    )


def retry_delay(attempt: int, retry_after: Optional[int] = None, jitter: float = 0.0) -> float:
    if retry_after is not None:
        return float(max(1, min(retry_after, 300)))
    base = min(2 ** max(0, attempt), 60)
    return float(base) + max(0.0, min(jitter, 1.0))


def validate_app_token(token: str) -> None:
    if not token.startswith("xapp-") or len(token) < 20 or any(character.isspace() for character in token):
        raise PermanentTransportError("invalid-app-token-shape")


def open_socket_url(app_token: str, timeout: float = 10.0) -> str:
    validate_app_token(app_token)
    request = urllib.request.Request(
        CONNECTIONS_OPEN_URL,
        data=b"",
        headers={
            "Authorization": "Bearer " + app_token,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "fidgeting-local-command-bridge/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(65536)
    except urllib.error.HTTPError as exc:
        retry_after: Optional[int] = None
        if exc.code == 429:
            try:
                retry_after = int(exc.headers.get("Retry-After", "1"))
            except (TypeError, ValueError):
                retry_after = 1
            raise RetryableTransportError("rate-limited", retry_after) from None
        if exc.code >= 500:
            raise RetryableTransportError("slack-http-server-error") from None
        raise PermanentTransportError("slack-http-client-error") from None
    except (urllib.error.URLError, TimeoutError):
        raise RetryableTransportError("connections-open-network-error") from None

    try:
        payload = json.loads(raw)
    except ValueError:
        raise RetryableTransportError("connections-open-invalid-json") from None
    if not isinstance(payload, dict) or not payload.get("ok"):
        reason = _safe_reason(payload.get("error") if isinstance(payload, dict) else None, "slack-api-error")
        if reason.replace("-", "_") in PERMANENT_SLACK_ERRORS:
            raise PermanentTransportError(reason)
        raise RetryableTransportError(reason)
    url = payload.get("url")
    if not isinstance(url, str):
        raise RetryableTransportError("connections-open-missing-url")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "wss" or not parsed.hostname or not parsed.hostname.endswith(".slack.com"):
        raise PermanentTransportError("unexpected-websocket-host")
    return url


async def receive_connection(
    websocket_url: str,
    policy: CommandPolicy,
    store: AppendOnlyCommandStore,
    *,
    max_envelopes: Optional[int] = None,
) -> int:
    try:
        import websockets
    except ImportError as exc:
        raise PermanentTransportError("websockets-dependency-missing") from exc

    handled = 0
    async with websockets.connect(
        websocket_url,
        open_timeout=10,
        close_timeout=5,
        ping_interval=20,
        ping_timeout=20,
        max_size=1_000_000,
    ) as socket:
        store.audit_runtime("connected", "socket-mode")
        async for raw in socket:
            try:
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", "strict")
                envelope = json.loads(raw)
            except (UnicodeDecodeError, ValueError):
                store.audit_runtime("ignored", "invalid-websocket-json")
                continue
            if not isinstance(envelope, dict):
                store.audit_runtime("ignored", "websocket-payload-not-object")
                continue

            item = socket_event(envelope)
            if item.control == "disconnect":
                store.audit_runtime("disconnected", item.ignore_reason or "server-disconnect")
                break
            if item.control == "hello":
                continue
            if item.control == "ignore":
                store.audit_runtime("ignored", item.ignore_reason or "unsupported-envelope")
            elif item.sanitized is not None:
                decision = evaluate_event(item.sanitized, policy, now=utc_now())
                store.ingest(decision, now=utc_now())

            # Persist the accepted/rejected decision before acknowledging so a
            # successful ack never precedes the local audit/queue write.
            if item.envelope_id:
                await socket.send(canonical_json({"envelope_id": item.envelope_id}))
            handled += 1
            if max_envelopes is not None and handled >= max_envelopes:
                return handled
    return handled


async def run_service(
    app_token: str,
    policy: CommandPolicy,
    store: AppendOnlyCommandStore,
    *,
    max_envelopes: Optional[int] = None,
    max_reconnects: Optional[int] = None,
) -> int:
    attempt = 0
    total = 0
    while True:
        try:
            websocket_url = await asyncio.to_thread(open_socket_url, app_token)
            remaining = None if max_envelopes is None else max_envelopes - total
            total += await receive_connection(
                websocket_url, policy, store, max_envelopes=remaining
            )
            if max_envelopes is not None and total >= max_envelopes:
                return 0
            attempt = 0
        except PermanentTransportError as exc:
            store.audit_runtime("failed", exc.reason)
            return 2
        except RetryableTransportError as exc:
            attempt += 1
            delay = retry_delay(attempt, exc.retry_after, random.random())
            store.audit_runtime(
                "retrying", exc.reason, retry_after_seconds=int(delay)
            )
        except Exception as exc:
            # Exception strings from WebSocket clients may contain the ticketed
            # URL, so only the exception class is mapped to a fixed audit code.
            attempt += 1
            reason = "socket-" + exc.__class__.__name__.lower().replace("_", "-")
            reason = _safe_reason(reason, "socket-error")
            delay = retry_delay(attempt, jitter=random.random())
            store.audit_runtime("retrying", reason, retry_after_seconds=int(delay))

        if max_reconnects is not None and attempt > max_reconnects:
            store.audit_runtime("failed", "reconnect-limit-reached")
            return 3
        await asyncio.sleep(delay)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="explicitly start the foreground service")
    parser.add_argument("--dry-run", action="store_true", help="validate only; no network or writes")
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    parser.add_argument("--max-envelopes", type=int)
    parser.add_argument("--max-reconnects", type=int)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.run == args.dry_run:
        sys.stderr.write(
            canonical_json(
                {"schemaVersion": SCHEMA_VERSION, "error": "choose-exactly-one-of-run-or-dry-run"}
            )
            + "\n"
        )
        return 2
    try:
        policy = CommandPolicy.from_values(
            args.allowed_team_id, args.allowed_user_id, args.allowed_conversation_id
        )
        app_token = os.environ.get("SLACK_COMMAND_APP_TOKEN", "")
        validate_app_token(app_token)
        try:
            import websockets  # noqa: F401

            dependency = "available"
        except ImportError:
            dependency = "missing"
            if args.run:
                raise PermanentTransportError("websockets-dependency-missing")
        if args.dry_run:
            sys.stdout.write(
                canonical_json(
                    {
                        "schemaVersion": SCHEMA_VERSION,
                        "mode": "dry-run",
                        "configurationValid": True,
                        "appToken": "configured",
                        "policy": "configured",
                        "websocketsDependency": dependency,
                        "networkAttempted": False,
                        "runtimeWritten": False,
                    }
                )
                + "\n"
            )
            return 0
        store = AppendOnlyCommandStore(args.runtime_root)
        return asyncio.run(
            run_service(
                app_token,
                policy,
                store,
                max_envelopes=args.max_envelopes,
                max_reconnects=args.max_reconnects,
            )
        )
    except (BridgeError, ValueError) as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
