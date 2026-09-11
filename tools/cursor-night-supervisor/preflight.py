#!/usr/bin/env python3
"""Read-only readiness snapshot for the Fidgeting Cursor night supervisor.

The collector deliberately has no UI automation and opens no file for writing.  It
uses only read-only macOS, filesystem, and Git queries, then writes one JSON report
to stdout.  A fixture mode keeps the parsers and policy deterministic in tests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.0"
PIPELINE_CORE_PATH = "tools/model-provenance-explorer/pipeline-core.mjs"
UNITY_LOCK_PATH = "unity/FidgetingApp/Temp/UnityLockfile"
DEFAULT_MIN_FREE_GIB = 20.0
TAIL_LIMIT_BYTES = 64 * 1024

# Kept public so the focused test can prove that collection never invokes a
# mutating Git operation or a UI command.
READ_ONLY_COMMANDS: Mapping[str, tuple[str, ...]] = {
    "pmsetBattery": ("pmset", "-g", "batt"),
    "pmsetAssertions": ("pmset", "-g", "assertions"),
    "disk": ("df", "-Pk", "."),
    "gitStatus": (
        "git",
        "--no-optional-locks",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--no-renames",
    ),
    "pipelineStatus": (
        "git",
        "--no-optional-locks",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--no-renames",
        "--",
        PIPELINE_CORE_PATH,
    ),
    "pipelineDiff": (
        "git",
        "--no-optional-locks",
        "diff",
        "--no-ext-diff",
        "--binary",
        "HEAD",
        "--",
        PIPELINE_CORE_PATH,
    ),
}

CONFLICT_CODES = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}
EXIT_CODE_PATTERNS = (
    re.compile(r"\bprocess\s+exited\s+with\s+code\s+(-?\d+)\b", re.I),
    re.compile(r"\b(?:exit|return)\s+(?:code|status)\s*[:=]?\s*(-?\d+)\b", re.I),
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _iso_utc_from_timestamp(value: float) -> str:
    return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _empty_result(exit_code: int = 127, stderr: str = "unavailable") -> dict[str, Any]:
    return {"exitCode": exit_code, "stdout": "", "stderr": stderr}


def _normalize_command_result(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return _empty_result()
    return {
        "exitCode": int(value.get("exitCode", 127)),
        "stdout": str(value.get("stdout", "")),
        "stderr": str(value.get("stderr", "")),
    }


def run_read_only_commands(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Run the fixed read-only command set with GIT_OPTIONAL_LOCKS disabled."""

    results: dict[str, dict[str, Any]] = {}
    environment = os.environ.copy()
    environment["GIT_OPTIONAL_LOCKS"] = "0"

    for name, command in READ_ONLY_COMMANDS.items():
        argv = list(command)
        if name == "disk":
            argv[-1] = str(repo_root)
        try:
            completed = subprocess.run(
                argv,
                cwd=repo_root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
                check=False,
            )
            results[name] = {
                "exitCode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
        except (OSError, subprocess.TimeoutExpired) as error:
            results[name] = _empty_result(stderr=type(error).__name__)

    return results


def read_file_snapshot(path: Path, *, include_tail: bool) -> dict[str, Any]:
    """Return metadata (and an optional bounded tail) without touching mtime."""

    display_path = str(path)
    try:
        stat = path.stat()
    except FileNotFoundError:
        return {"path": display_path, "exists": False}
    except OSError as error:
        return {
            "path": display_path,
            "exists": False,
            "readError": type(error).__name__,
        }

    snapshot: dict[str, Any] = {
        "path": display_path,
        "exists": True,
        "sizeBytes": stat.st_size,
        "modifiedAt": _iso_utc_from_timestamp(stat.st_mtime),
    }
    try:
        with path.open("rb") as handle:
            if include_tail and stat.st_size > TAIL_LIMIT_BYTES:
                handle.seek(-TAIL_LIMIT_BYTES, os.SEEK_END)
            content = handle.read() if include_tail else b""
            if not include_tail:
                hasher = hashlib.sha256()
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    hasher.update(chunk)
                snapshot["contentSha256"] = hasher.hexdigest()
            else:
                snapshot["tail"] = content.decode("utf-8", errors="replace")
    except OSError as error:
        snapshot["readError"] = type(error).__name__
    return snapshot


def discover_latest_cursor_terminal_logs(logs_root: Path) -> list[Path]:
    """Find only terminal/PTY logs from the newest Cursor log session."""

    try:
        sessions = sorted(path for path in logs_root.iterdir() if path.is_dir())
    except OSError:
        return []
    if not sessions:
        return []

    latest = sessions[-1]
    candidates = [*latest.glob("terminal*.log"), latest / "ptyhost.log"]
    return sorted({path for path in candidates if path.is_file()}, key=str)


def collect_inputs(
    repo_root: Path,
    terminal_log_paths: Sequence[Path],
    cursor_logs_root: Path,
) -> dict[str, Any]:
    log_paths = list(terminal_log_paths)
    discovery = "explicit"
    if not log_paths:
        log_paths = discover_latest_cursor_terminal_logs(cursor_logs_root)
        discovery = "latest-cursor-session"

    return {
        "commands": run_read_only_commands(repo_root),
        "files": {
            "unityLock": read_file_snapshot(repo_root / UNITY_LOCK_PATH, include_tail=False),
            "pipelineCore": read_file_snapshot(repo_root / PIPELINE_CORE_PATH, include_tail=False),
            "terminalLogs": [
                read_file_snapshot(path.expanduser(), include_tail=True) for path in log_paths
            ],
        },
        "terminalLogDiscovery": discovery,
    }


def parse_power(
    battery: Mapping[str, Any], assertions: Mapping[str, Any]
) -> dict[str, Any]:
    battery = _normalize_command_result(battery)
    assertions = _normalize_command_result(assertions)
    battery_ok = battery["exitCode"] == 0
    assertions_ok = assertions["exitCode"] == 0

    source_match = re.search(r"Now drawing from ['\"]([^'\"]+)['\"]", battery["stdout"])
    source = source_match.group(1) if source_match else None
    on_ac = bool(
        (source and ("ac power" in source.lower() or "ups power" in source.lower()))
        or re.search(r"\bAC attached\b", battery["stdout"], re.I)
    )

    counts = {
        "PreventSystemSleep": 0,
        "PreventUserIdleSystemSleep": 0,
        "PreventUserIdleDisplaySleep": 0,
    }
    for line in assertions["stdout"].splitlines():
        match = re.match(
            r"^\s*(PreventSystemSleep|PreventUserIdleSystemSleep|PreventUserIdleDisplaySleep)\s+(\d+)\s*$",
            line,
        )
        if match:
            counts[match.group(1)] = int(match.group(2))

    prevents_system_sleep = bool(
        counts["PreventSystemSleep"] or counts["PreventUserIdleSystemSleep"]
    )
    prevents_display_sleep = bool(counts["PreventUserIdleDisplaySleep"])

    if not battery_ok or not assertions_ok:
        status = "unknown"
    elif on_ac and prevents_system_sleep and prevents_display_sleep:
        status = "ready"
    else:
        status = "blocked"

    return {
        "status": status,
        "source": source,
        "onAcPower": on_ac if battery_ok else None,
        "preventsSystemSleep": prevents_system_sleep if assertions_ok else None,
        "preventsDisplaySleep": prevents_display_sleep if assertions_ok else None,
        "assertionCounts": counts,
        "checksReadable": battery_ok and assertions_ok,
    }


def parse_disk(result: Mapping[str, Any], minimum_free_bytes: int) -> dict[str, Any]:
    result = _normalize_command_result(result)
    lines = [line for line in result["stdout"].splitlines() if line.strip()]
    total_bytes: int | None = None
    available_bytes: int | None = None
    used_percent: int | None = None
    if result["exitCode"] == 0 and len(lines) >= 2:
        columns = lines[-1].split()
        try:
            total_bytes = int(columns[1]) * 1024
            available_bytes = int(columns[3]) * 1024
            used_percent = int(columns[4].rstrip("%"))
        except (IndexError, ValueError):
            pass

    if available_bytes is None:
        status = "unknown"
    elif available_bytes < minimum_free_bytes:
        status = "blocked"
    else:
        status = "ready"
    return {
        "status": status,
        "totalBytes": total_bytes,
        "availableBytes": available_bytes,
        "usedPercent": used_percent,
        "minimumFreeBytes": minimum_free_bytes,
    }


def parse_porcelain(output: str) -> dict[str, Any]:
    records = [line for line in output.splitlines() if line]
    staged = 0
    unstaged = 0
    untracked = 0
    conflicted = 0
    for record in records:
        code = record[:2] if len(record) >= 2 else ""
        if code == "??":
            untracked += 1
            continue
        if code in CONFLICT_CODES:
            conflicted += 1
        if code and code[0] not in {" ", "!", "?"}:
            staged += 1
        if len(code) == 2 and code[1] not in {" ", "!", "?"}:
            unstaged += 1
    return {
        "changedCount": len(records),
        "stagedCount": staged,
        "unstagedCount": unstaged,
        "untrackedCount": untracked,
        "conflictedCount": conflicted,
    }


def parse_worktree(result: Mapping[str, Any]) -> dict[str, Any]:
    result = _normalize_command_result(result)
    if result["exitCode"] != 0:
        return {
            "status": "unknown",
            "changedCount": None,
            "stagedCount": None,
            "unstagedCount": None,
            "untrackedCount": None,
            "conflictedCount": None,
        }
    summary = parse_porcelain(result["stdout"])
    summary["status"] = "clean" if summary["changedCount"] == 0 else "dirty"
    return {key: summary[key] for key in sorted(summary)}


def _pipeline_state(status_output: str, exists: bool) -> tuple[str, str | None]:
    line = next((line for line in status_output.splitlines() if line), "")
    code = line[:2] if len(line) >= 2 else None
    if code == "??":
        return "untracked", code
    if code in CONFLICT_CODES:
        return "conflicted", code
    if code:
        return "modified", code
    return ("clean" if exists else "missing"), None


def parse_pipeline_core(
    status_result: Mapping[str, Any],
    diff_result: Mapping[str, Any],
    file_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    status_result = _normalize_command_result(status_result)
    diff_result = _normalize_command_result(diff_result)
    exists = bool(file_snapshot.get("exists", False))
    if status_result["exitCode"] == 0:
        state, git_code = _pipeline_state(status_result["stdout"], exists)
    else:
        state, git_code = "unknown", None

    diff_bytes = diff_result["stdout"].encode("utf-8")
    return {
        "path": PIPELINE_CORE_PATH,
        "state": state,
        "gitCode": git_code,
        "exists": exists,
        "contentSha256": file_snapshot.get("contentSha256"),
        "diffReadable": diff_result["exitCode"] == 0,
        "diffLineCount": len(diff_result["stdout"].splitlines()),
        "diffSha256": _sha256_bytes(diff_bytes) if diff_bytes else None,
    }


def _last_exit_code(tail: str) -> int | None:
    matches: list[tuple[int, int]] = []
    for pattern in EXIT_CODE_PATTERNS:
        for match in pattern.finditer(tail):
            matches.append((match.start(), int(match.group(1))))
    return max(matches, default=(0, None), key=lambda item: item[0])[1]


def parse_terminal_logs(
    snapshots: Iterable[Mapping[str, Any]], now: datetime, discovery: str
) -> dict[str, Any]:
    logs: list[dict[str, Any]] = []
    for snapshot in sorted(snapshots, key=lambda value: str(value.get("path", ""))):
        exists = bool(snapshot.get("exists", False))
        tail = str(snapshot.get("tail", "")) if exists else ""
        exit_code = _last_exit_code(tail)
        if not exists:
            state = "missing"
        elif snapshot.get("readError"):
            state = "unreadable"
        elif int(snapshot.get("sizeBytes", 0)) == 0:
            state = "empty"
        elif exit_code is None:
            state = "updated"
        elif exit_code == 0:
            state = "succeeded"
        else:
            state = "failed"

        age_seconds: int | None = None
        modified_at = snapshot.get("modifiedAt")
        if isinstance(modified_at, str):
            try:
                modified = _parse_now(modified_at)
                age_seconds = max(0, int((now - modified).total_seconds()))
            except ValueError:
                pass

        logs.append(
            {
                "path": str(snapshot.get("path", "")),
                "state": state,
                "exists": exists,
                "sizeBytes": snapshot.get("sizeBytes") if exists else None,
                "modifiedAt": modified_at if exists else None,
                "ageSeconds": age_seconds,
                "lastExitCode": exit_code,
                "tailSha256": _sha256_bytes(tail.encode("utf-8")) if tail else None,
            }
        )

    states = {entry["state"] for entry in logs}
    if not logs:
        status = "none"
    elif states & {"failed", "missing", "unreadable"}:
        status = "attention"
    else:
        status = "observed"
    return {"status": status, "discovery": discovery, "logs": logs}


def command_errors(commands: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    for name in sorted(READ_ONLY_COMMANDS):
        result = _normalize_command_result(commands.get(name))
        if result["exitCode"] != 0:
            stderr = result["stderr"].encode("utf-8")
            errors.append(
                {
                    "check": name,
                    "exitCode": result["exitCode"],
                    "stderrSha256": _sha256_bytes(stderr) if stderr else None,
                }
            )
    return errors


def derive_overall(
    power: Mapping[str, Any],
    disk: Mapping[str, Any],
    unity: Mapping[str, Any],
    pipeline: Mapping[str, Any],
    worktree: Mapping[str, Any],
    terminal_logs: Mapping[str, Any],
    errors: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    if not power.get("checksReadable"):
        blockers.append("power.read-failed")
    else:
        if not power.get("onAcPower"):
            blockers.append("power.not-on-ac")
        if not power.get("preventsSystemSleep"):
            blockers.append("power.system-sleep-not-prevented")
        if not power.get("preventsDisplaySleep"):
            blockers.append("power.display-sleep-not-prevented")

    if disk.get("status") == "unknown":
        blockers.append("disk.read-failed")
    elif disk.get("status") == "blocked":
        blockers.append("disk.below-minimum")

    if unity.get("lockPresent"):
        blockers.append("unity.lock-present")
    if worktree.get("status") == "unknown":
        blockers.append("worktree.read-failed")
    elif worktree.get("conflictedCount", 0):
        blockers.append("worktree.conflicts-present")

    pipeline_state = pipeline.get("state")
    if pipeline_state == "conflicted":
        blockers.append("pipeline-core.conflicted")
    elif pipeline_state in {"modified", "untracked", "missing"}:
        warnings.append(f"pipeline-core.{pipeline_state}")
    elif pipeline_state == "unknown":
        blockers.append("pipeline-core.read-failed")

    if terminal_logs.get("status") == "none":
        warnings.append("terminal-logs.none-found")
    elif terminal_logs.get("status") == "attention":
        warnings.append("terminal-logs.attention")

    required_error_names = {
        "pmsetBattery",
        "pmsetAssertions",
        "disk",
        "gitStatus",
        "pipelineStatus",
        "pipelineDiff",
    }
    if any(error.get("check") in required_error_names for error in errors):
        # Section-specific blockers above explain the effect. This warning makes
        # command-level partial failures visible without duplicating blockers.
        warnings.append("commands.partial-failure")

    blockers = sorted(set(blockers))
    warnings = sorted(set(warnings))
    status = "blocked" if blockers else ("warning" if warnings else "ready")
    return {"status": status, "blockers": blockers, "warnings": warnings}


def build_report(raw: Mapping[str, Any], repo_root: Path, now: datetime, min_free_gib: float) -> dict[str, Any]:
    commands = raw.get("commands", {})
    files = raw.get("files", {})
    if not isinstance(commands, Mapping) or not isinstance(files, Mapping):
        raise ValueError("fixture commands/files must be objects")

    power = parse_power(commands.get("pmsetBattery", {}), commands.get("pmsetAssertions", {}))
    disk = parse_disk(commands.get("disk", {}), int(min_free_gib * 1024**3))
    worktree = parse_worktree(commands.get("gitStatus", {}))
    pipeline = parse_pipeline_core(
        commands.get("pipelineStatus", {}),
        commands.get("pipelineDiff", {}),
        files.get("pipelineCore", {}),
    )

    unity_snapshot = files.get("unityLock", {})
    unity = {
        "status": "blocked" if unity_snapshot.get("exists") else "clear",
        "lockPath": UNITY_LOCK_PATH,
        "lockPresent": bool(unity_snapshot.get("exists", False)),
        "lockModifiedAt": unity_snapshot.get("modifiedAt"),
        "lockSizeBytes": unity_snapshot.get("sizeBytes"),
    }
    terminal_logs = parse_terminal_logs(
        files.get("terminalLogs", []),
        now,
        str(raw.get("terminalLogDiscovery", "fixture")),
    )
    errors = command_errors(commands)
    overall = derive_overall(power, disk, unity, pipeline, worktree, terminal_logs, errors)

    return {
        "schemaVersion": SCHEMA_VERSION,
        "generatedAt": now.isoformat().replace("+00:00", "Z"),
        "repoRoot": str(repo_root),
        "overall": overall,
        "power": power,
        "disk": disk,
        "unity": unity,
        "pipelineCore": pipeline,
        "terminalLogs": terminal_logs,
        "worktree": worktree,
        "commandErrors": errors,
    }


def load_fixture(path: Path) -> tuple[dict[str, Any], Path, datetime]:
    with path.open("r", encoding="utf-8") as handle:
        fixture = json.load(handle)
    repo_root = Path(str(fixture.get("repoRoot", "/fixture/Fidgeting app")))
    now = _parse_now(str(fixture.get("now", "2026-09-05T16:00:00Z")))
    return fixture, repo_root, now


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    default_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--terminal-log", action="append", type=Path, default=[])
    parser.add_argument(
        "--cursor-logs-root",
        type=Path,
        default=Path.home() / "Library/Application Support/Cursor/logs",
    )
    parser.add_argument("--min-free-gib", type=float, default=DEFAULT_MIN_FREE_GIB)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--fail-on-blocker", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.min_free_gib < 0:
        raise SystemExit("--min-free-gib must be non-negative")

    if args.fixture:
        raw, repo_root, now = load_fixture(args.fixture)
    else:
        repo_root = args.repo_root.expanduser().resolve()
        now = datetime.now(timezone.utc)
        raw = collect_inputs(
            repo_root,
            [path.expanduser() for path in args.terminal_log],
            args.cursor_logs_root.expanduser(),
        )

    report = build_report(raw, repo_root, now, args.min_free_gib)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 2 if args.fail_on_blocker and report["overall"]["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
