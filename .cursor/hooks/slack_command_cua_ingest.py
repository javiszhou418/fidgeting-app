#!/usr/bin/env python3
"""Commit one sanitized native-Slack CUA batch and its source cursor.

This adapter is deliberately transport-only. It accepts structured JSON from a
heartbeat observation, never drives Slack itself, never emits message text, and
never turns Slack content into executable arguments.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from slack_command_bridge import (
    AppendOnlyCommandStore,
    BridgeError,
    CommandPolicy,
    ConfigurationError,
    GROUPED_APP_CONTINUATION_KIND,
    MAX_FUTURE_SKEW_SECONDS,
    SCHEMA_VERSION,
    SLACK_EVENT_ID,
    SLACK_NATIVE_CUA_SOURCE,
    SLACK_NATIVE_TIMESTAMP,
    SLACK_POLL_ID,
    SLACK_WORKSPACE_HOST,
    SOURCE_POLL_FAILURE_REASONS,
    SOURCE_ROW_KINDS,
    SourceObservationRow,
    canonical_json,
    default_runtime_root,
    evaluate_native_cua_event,
    parse_slack_timestamp,
    parse_utc,
    source_batch_digest,
    source_bootstrap_digest,
    utc_now,
    valid_source_permalink,
)


BATCH_SCHEMA_VERSION = "1.0"
MAX_BATCH_EVENTS = 100
MAX_BATCH_ROWS = 500
MAX_INPUT_BYTES = 65536
BATCH_KEYS = {
    "schemaVersion",
    "source",
    "baseObservedThrough",
    "observedThrough",
    "rows",
    "events",
    "pollProof",
}
AUTHOR_PROOF = "native-from-me-self-dm-verified-user-map-v1"
SOURCE_KEYS = {
    "kind",
    "team_id",
    "user_id",
    "conversation_id",
    "workspace_host",
    "authorProof",
}
POLL_PROOF_KEYS = {
    "pollId",
    "result",
    "anchorSeen",
    "chronologyComplete",
    "stableBottomSeen",
}
ROW_KEYS = {"message_ts", "kind", "permalink"}
EVENT_KEYS = {
    "schemaVersion",
    "team_id",
    "user_id",
    "conversation_id",
    "event_id",
    "message_ts",
    "text",
}
REQUIRED_EVENT_KEYS = EVENT_KEYS - {"event_id"}


def _read_input(path: Optional[Path]) -> Mapping[str, Any]:
    if path:
        try:
            if path.stat().st_size > MAX_INPUT_BYTES:
                raise BridgeError("batch-input-too-large")
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BridgeError("batch-input-unreadable") from exc
    else:
        raw = sys.stdin.read(MAX_INPUT_BYTES + 1)
        if len(raw.encode("utf-8", "replace")) > MAX_INPUT_BYTES:
            raise BridgeError("batch-input-too-large")
    try:
        value = json.loads(raw)
    except ValueError as exc:
        raise BridgeError("invalid-batch-json") from exc
    if not isinstance(value, dict):
        raise BridgeError("batch-must-be-object")
    return value


def _cursor(value: Any, *, optional: bool) -> Optional[str]:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not SLACK_NATIVE_TIMESTAMP.fullmatch(value):
        raise BridgeError("invalid-source-cursor")
    try:
        parse_slack_timestamp(value)
    except ValueError as exc:
        raise BridgeError("invalid-source-cursor") from exc
    return value


def validate_batch(
    batch: Mapping[str, Any],
    policy: CommandPolicy,
    workspace_host: str,
    *,
    now=None,
) -> tuple[str, str, list[SourceObservationRow], str, list[Any]]:
    if not isinstance(workspace_host, str) or not SLACK_WORKSPACE_HOST.fullmatch(
        workspace_host
    ):
        raise ConfigurationError("invalid-allowed-workspace-host")
    if set(batch) != BATCH_KEYS:
        raise BridgeError("invalid-batch-fields")
    if batch.get("schemaVersion") != BATCH_SCHEMA_VERSION:
        raise BridgeError("unsupported-batch-schema-version")
    source = batch.get("source")
    if not isinstance(source, Mapping) or set(source) != SOURCE_KEYS:
        raise BridgeError("invalid-batch-source")
    if source.get("kind") != SLACK_NATIVE_CUA_SOURCE:
        raise BridgeError("unsupported-source")
    if source.get("authorProof") != AUTHOR_PROOF:
        raise BridgeError("unverified-self-dm-author")
    if (
        source.get("team_id") != policy.team_id
        or source.get("user_id") != policy.user_id
        or source.get("conversation_id") != policy.conversation_id
        or source.get("workspace_host") != workspace_host
    ):
        raise ConfigurationError("batch-source-not-allowlisted")

    proof = batch.get("pollProof")
    if not isinstance(proof, Mapping) or set(proof) != POLL_PROOF_KEYS:
        raise BridgeError("invalid-poll-proof")
    poll_id = proof.get("pollId")
    if not isinstance(poll_id, str) or not SLACK_POLL_ID.fullmatch(poll_id):
        raise BridgeError("invalid-source-poll-id")
    if (
        proof.get("result") != "verified"
        or proof.get("anchorSeen") is not True
        or proof.get("chronologyComplete") is not True
        or proof.get("stableBottomSeen") is not True
    ):
        raise BridgeError("poll-not-continuously-verified")

    current = now or utc_now()
    base_cursor = _cursor(batch.get("baseObservedThrough"), optional=False)
    next_cursor = _cursor(batch.get("observedThrough"), optional=False)
    assert base_cursor is not None and next_cursor is not None
    base_value = parse_slack_timestamp(base_cursor)
    next_value = parse_slack_timestamp(next_cursor)
    if float(next_value) > current.timestamp() + MAX_FUTURE_SKEW_SECONDS:
        raise BridgeError("future-observed-through")

    raw_rows = batch.get("rows")
    if not isinstance(raw_rows, list) or len(raw_rows) > MAX_BATCH_ROWS:
        raise BridgeError("invalid-observed-rows")
    rows: list[SourceObservationRow] = []
    previous_value = base_value
    for raw_row in raw_rows:
        if not isinstance(raw_row, Mapping) or set(raw_row) != ROW_KEYS:
            raise BridgeError("invalid-observed-row")
        message_ts = raw_row.get("message_ts")
        try:
            row_value = parse_slack_timestamp(message_ts)
        except (TypeError, ValueError) as exc:
            raise BridgeError("invalid-observed-row") from exc
        kind = raw_row.get("kind")
        permalink = raw_row.get("permalink")
        if (
            kind not in SOURCE_ROW_KINDS
            or not isinstance(permalink, str)
            or not valid_source_permalink(
                permalink, workspace_host, policy.conversation_id, message_ts
            )
            or row_value <= previous_value
        ):
            raise BridgeError("invalid-observed-row")
        if kind == GROUPED_APP_CONTINUATION_KIND and (
            not rows or rows[-1].kind != "app-message"
        ):
            # This fixed kind attests that the collector saw the direct app
            # anchor and continuation simultaneously, adjacent, in one exact-DM
            # AX render group with no boundary/loading row.  Structural
            # anchoring is enforced here and again by the authoritative store.
            raise BridgeError("unanchored-app-group-continuation")
        rows.append(SourceObservationRow(message_ts, kind, permalink))
        previous_value = row_value
    if rows:
        if next_value <= base_value or previous_value != next_value:
            raise BridgeError("observed-through-mismatch")
    elif next_value != base_value:
        raise BridgeError("empty-observation-cursor-change")

    events = batch.get("events")
    if not isinstance(events, list) or len(events) > MAX_BATCH_EVENTS:
        raise BridgeError("invalid-batch-events")

    decisions = []
    event_ids: set[str] = set()
    self_row_timestamps = [row.message_ts for row in rows if row.kind == "self-message"]
    event_timestamps: list[str] = []
    for event in events:
        if not isinstance(event, Mapping):
            raise BridgeError("invalid-batch-event")
        keys = set(event)
        if not REQUIRED_EVENT_KEYS <= keys <= EVENT_KEYS:
            raise BridgeError("invalid-batch-event-fields")
        if event.get("schemaVersion") != SCHEMA_VERSION:
            raise BridgeError("unsupported-event-schema-version")
        if (
            event.get("team_id") != policy.team_id
            or event.get("user_id") != policy.user_id
            or event.get("conversation_id") != policy.conversation_id
        ):
            raise ConfigurationError("event-source-not-allowlisted")
        if not isinstance(event.get("text"), str):
            raise BridgeError("invalid-event-text")
        event_id = event.get("event_id")
        if event_id is not None and (
            not isinstance(event_id, str) or not SLACK_EVENT_ID.fullmatch(event_id)
        ):
            raise BridgeError("invalid-event-id")
        message_ts = event.get("message_ts")
        try:
            cursor_value = parse_slack_timestamp(message_ts)
        except (TypeError, ValueError) as exc:
            raise BridgeError("invalid-message-timestamp") from exc
        event_timestamps.append(message_ts)

        decision = evaluate_native_cua_event(event, policy, now=current)
        if decision.accepted and decision.command == "approve-safe":
            # Native Slack CUA can attest a visible self-sender row in the exact
            # DM chronology but does not expose a cryptographic per-message user
            # ID. That indirect provenance cannot authorize approve-safe.
            decision = replace(
                decision,
                accepted=False,
                reason="command-not-allowed-for-native-cua",
                command=None,
                request_id=None,
            )
        if decision.event_id in event_ids:
            raise BridgeError("duplicate-event-id-in-batch")
        event_ids.add(decision.event_id)
        decisions.append(decision)

    if event_timestamps != self_row_timestamps:
        raise BridgeError("events-do-not-cover-self-message-rows")
    return base_cursor, next_cursor, rows, poll_id, decisions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--allowed-team-id")
    parser.add_argument("--allowed-user-id")
    parser.add_argument("--allowed-conversation-id")
    parser.add_argument("--allowed-workspace-host")
    parser.add_argument("--now", help="test-only RFC3339 clock override")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    ingest = subparsers.add_parser("ingest", help="validate and commit one CUA event batch")
    ingest.add_argument("--input", type=Path, help="batch JSON; stdin if omitted")
    ingest.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    bootstrap = subparsers.add_parser(
        "bootstrap", help="observe only: activate after the newest verified message"
    )
    bootstrap.add_argument("--cursor", required=True, help="verified newest Slack message_ts")
    bootstrap.add_argument(
        "--author-proof",
        required=True,
        help="must be the fixed native self-DM proof label",
    )
    bootstrap.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    failure = subparsers.add_parser(
        "poll-failure", help="record an incomplete/ambiguous poll without advancing"
    )
    failure.add_argument("--poll-id", required=True)
    failure.add_argument("--base-observed-through", required=True)
    failure.add_argument("--reason", required=True, choices=tuple(sorted(SOURCE_POLL_FAILURE_REASONS)))
    failure.add_argument("--dry-run", action="store_true", help="validate only; write nothing")
    subparsers.add_parser("cursor", help="read the persisted source cursor")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        policy = CommandPolicy.from_values(
            args.allowed_team_id, args.allowed_user_id, args.allowed_conversation_id
        )
        workspace_host = args.allowed_workspace_host or os.environ.get(
            "FIDGETING_SLACK_ALLOWED_WORKSPACE_HOST", ""
        )
        if not SLACK_WORKSPACE_HOST.fullmatch(workspace_host):
            raise ConfigurationError("invalid-allowed-workspace-host")
        current = parse_utc(args.now) if args.now else utc_now()
        store = AppendOnlyCommandStore(args.runtime_root)
        if args.operation == "cursor":
            result = store.source_cursor(SLACK_NATIVE_CUA_SOURCE, policy)
        elif args.operation == "bootstrap":
            if args.author_proof != AUTHOR_PROOF:
                raise BridgeError("unverified-self-dm-author")
            cursor = _cursor(args.cursor, optional=False)
            assert cursor is not None
            if float(parse_slack_timestamp(cursor)) > current.timestamp() + MAX_FUTURE_SKEW_SECONDS:
                raise BridgeError("future-source-cursor")
            if args.dry_run:
                result = {
                    "schemaVersion": SCHEMA_VERSION,
                    "bootstrapped": False,
                    "dryRun": True,
                    "sourceCursor": cursor,
                    "activationCutoff": cursor,
                    "batchDigest": source_bootstrap_digest(
                        SLACK_NATIVE_CUA_SOURCE, policy, cursor
                    ),
                }
            else:
                result = store.bootstrap_source_cursor(
                    SLACK_NATIVE_CUA_SOURCE, policy, cursor, now=current
                )
        elif args.operation == "poll-failure":
            if not SLACK_POLL_ID.fullmatch(args.poll_id):
                raise BridgeError("invalid-source-poll-id")
            base_observed_through = _cursor(
                args.base_observed_through, optional=False
            )
            assert base_observed_through is not None
            if args.dry_run:
                result = {
                    "schemaVersion": SCHEMA_VERSION,
                    "recorded": False,
                    "dryRun": True,
                    "pollId": args.poll_id,
                    "outcome": "failed",
                    "reason": args.reason,
                    "observedThrough": base_observed_through,
                }
            else:
                result = store.record_source_poll_failure(
                    source=SLACK_NATIVE_CUA_SOURCE,
                    policy=policy,
                    workspace_host=workspace_host,
                    poll_id=args.poll_id,
                    base_observed_through=base_observed_through,
                    reason=args.reason,
                    now=current,
                )
        elif args.operation == "ingest":
            batch = _read_input(args.input)
            base_cursor, next_cursor, rows, poll_id, decisions = validate_batch(
                batch, policy, workspace_host, now=current
            )
            if args.dry_run:
                result = {
                    "schemaVersion": SCHEMA_VERSION,
                    "committed": False,
                    "dryRun": True,
                    "cursorUnchecked": True,
                    "sourceCursor": next_cursor,
                    "observedThrough": next_cursor,
                    "pollId": poll_id,
                    "pollOutcome": "verified",
                    "batchDigest": source_batch_digest(
                        SLACK_NATIVE_CUA_SOURCE,
                        policy,
                        base_cursor,
                        next_cursor,
                        decisions,
                        observed_rows=rows,
                        poll_id=poll_id,
                        workspace_host=workspace_host,
                    ),
                    "acceptedCount": sum(1 for item in decisions if item.accepted),
                    "rejectedCount": sum(1 for item in decisions if not item.accepted),
                    "eventResults": [item.public_result(dry_run=True) for item in decisions],
                }
            else:
                result = store.ingest_source_batch(
                    decisions,
                    source=SLACK_NATIVE_CUA_SOURCE,
                    policy=policy,
                    workspace_host=workspace_host,
                    base_cursor=base_cursor,
                    next_cursor=next_cursor,
                    observed_rows=rows,
                    poll_id=poll_id,
                    now=current,
                )
        else:
            raise BridgeError("unknown-operation")
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except (BridgeError, ValueError) as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
