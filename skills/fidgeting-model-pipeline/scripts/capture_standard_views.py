#!/usr/bin/env python3
"""Probe CLIAnything and capture a deterministic Blender camera pack."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


VIEW_IDS = ["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"]


def probe_cli() -> dict:
    executable = shutil.which("cli-anything-blender")
    if not executable:
        return {"installed": False, "preview_available": False, "path": None}
    result = subprocess.run([executable, "--help"], capture_output=True, text=True, check=False)
    preview = subprocess.run([executable, "preview", "--help"], capture_output=True, text=True, check=False)
    return {"installed": result.returncode == 0, "preview_available": preview.returncode == 0, "path": executable, "help_returncode": result.returncode, "preview_returncode": preview.returncode}


def blender_binary() -> str | None:
    candidates = [shutil.which("blender"), "/Applications/Blender.app/Contents/MacOS/Blender"]
    return next((candidate for candidate in candidates if candidate and Path(candidate).is_file()), None)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args()
    probe = probe_cli()
    blender = blender_binary()
    if args.probe_only:
        print(json.dumps({"cli_anything": probe, "blender": blender}, indent=2))
        return 0 if blender else 1
    if not args.blend.is_absolute() or not args.output.is_absolute():
        parser.error("--blend and --output must use absolute paths")
    if not args.blend.is_file():
        parser.error(f"Blend file does not exist: {args.blend}")
    if not blender:
        print("Blender executable was not found.", file=sys.stderr)
        return 1
    args.output.mkdir(parents=True, exist_ok=True)
    capture_script = Path(__file__).with_name("blender_capture_standard_views.py")
    run_id = str(uuid.uuid4())
    command = [blender, "--background", str(args.blend), "--python", str(capture_script), "--", "--output", str(args.output), "--run-id", run_id]
    result = subprocess.run(command, check=False)
    capture_report_path = args.output / "capture-report.json"
    capture_report = {}
    try:
        capture_report = json.loads(capture_report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        capture_report = {}
    missing_views = [view_id for view_id in VIEW_IDS if not (args.output / f"{view_id}.png").is_file()]
    verified = result.returncode == 0 and capture_report.get("run_id") == run_id and not missing_views
    report = {
        "cli_anything": probe,
        "capture_backend": "cli-anything-preview" if probe["preview_available"] else "blender-bpy-fallback",
        "blender": blender,
        "command": command,
        "blender_returncode": result.returncode,
        "verified_capture": verified,
        "missing_views": missing_views,
        "run_id": run_id,
    }
    (args.output / "capture-wrapper-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
