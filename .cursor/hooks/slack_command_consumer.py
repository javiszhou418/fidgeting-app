#!/usr/bin/env python3
"""Read or acknowledge Slack control commands without executing them.

The heartbeat may use ``snapshot`` to decide what is pending, then ``ack`` only
after it has completed and independently verified the corresponding safe action.
This script never invokes Cursor, Slack, a shell command, or an automation API.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from slack_command_bridge import (
    AppendOnlyCommandStore,
    BridgeError,
    SCHEMA_VERSION,
    StoreError,
    canonical_json,
    default_runtime_root,
    parse_utc,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=default_runtime_root())
    parser.add_argument("--now", help="test-only RFC3339 clock override")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("snapshot", help="print current control state and pending commands")
    acknowledge = subparsers.add_parser("ack", help="append a terminal consumption record")
    acknowledge.add_argument("--event-id", required=True)
    acknowledge.add_argument(
        "--outcome",
        required=True,
        choices=("applied", "reported", "refused", "expired"),
    )
    claim = subparsers.add_parser(
        "claim", help="atomically reserve one exact approval before any UI click"
    )
    claim.add_argument("--event-id", required=True)
    claim.add_argument("--request-id", required=True)
    finalize = subparsers.add_parser(
        "finalize", help="record the verified result of an already claimed approval"
    )
    finalize.add_argument("--event-id", required=True)
    finalize.add_argument("--request-id", required=True)
    finalize.add_argument("--outcome", required=True, choices=("applied", "refused"))
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        current = parse_utc(args.now) if args.now else None
        store = AppendOnlyCommandStore(args.runtime_root)
        if args.operation == "snapshot":
            result = store.snapshot(now=current)
        elif args.operation == "ack":
            result = store.acknowledge(args.event_id, args.outcome, now=current)
        elif args.operation == "claim":
            result = store.claim_approval(args.event_id, args.request_id, now=current)
        elif args.operation == "finalize":
            result = store.finalize_approval(
                args.event_id, args.request_id, args.outcome, now=current
            )
        else:  # argparse makes this unreachable, but keep the failure explicit.
            raise StoreError("unknown-operation")
        sys.stdout.write(canonical_json(result) + "\n")
        return 0
    except (BridgeError, ValueError) as exc:
        sys.stderr.write(
            canonical_json({"schemaVersion": SCHEMA_VERSION, "error": str(exc)}) + "\n"
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
