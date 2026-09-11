#!/usr/bin/env python3
"""Record the real library→detail entrance for every shipping toy on the iOS Simulator.

Per model: cold-launch the shipping app with the model preselected and the
`--fidgeting-preview-enter-detail-after=<s>` hook, record the Simulator, then
re-encode with libx264 and extract library / mid / detail frames.

Usage:
  capture_library_detail_simulator.py --udid <UDID> --app <path/to/.app> \
      --round r001 [--models a,b,c]
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

BUNDLE_ID = "com.jiaweizhou.fidgetspinner.codex"
# Shipping catalog after FDB-PREF-032 consolidation (4 toys).
MODELS = [
    "metal-three-blade",
    "graphite-two-lobe",
    "magnetic-slide-tile",
    "magnetic-fan-card",
]
REPO_ROOT = Path(__file__).resolve().parents[4]
OUT_ROOT = REPO_ROOT / "Artifacts" / "LibraryDetailConsistency"

ENTER_DETAIL_AFTER_S = 5.0   # measured from overlay install, after Unity boot
RECORD_SECONDS = 14.0
LAUNCH_LEAD_S = 1.0


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def capture_model(udid: str, model: str, out_dir: Path, round_id: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = out_dir / f"{model}-raw.mp4"
    clear = out_dir / f"{round_id}-{model}-library-to-detail-clear.mp4"
    subprocess.run(["xcrun", "simctl", "terminate", udid, BUNDLE_ID],
                   capture_output=True, text=True)
    time.sleep(0.5)
    recorder = subprocess.Popen(
        ["xcrun", "simctl", "io", udid, "recordVideo", "--codec=h264",
         "--force", str(raw)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(LAUNCH_LEAD_S)
    launch_wall = time.time()
    launch = run([
        "xcrun", "simctl", "launch", udid, BUNDLE_ID, "--args",
        "-fidgeting.selectedModel", model,
        # first-run quick-start would cover the detail view
        "-fidgeting.onboarding.spinner.v1.completed", "YES",
        f"--fidgeting-preview-enter-detail-after={ENTER_DETAIL_AFTER_S:g}",
    ])
    time.sleep(RECORD_SECONDS)
    recorder.send_signal(signal.SIGINT)
    try:
        recorder.wait(timeout=20)
    except subprocess.TimeoutExpired:
        recorder.kill()
    subprocess.run(["xcrun", "simctl", "terminate", udid, BUNDLE_ID],
                   capture_output=True, text=True)

    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw),
         "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(clear)])
    raw.unlink()

    # One frame per 0.5 s for review; named by time since launch.
    frames = out_dir / "frames"
    frames.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clear),
         "-vf", "fps=2", str(frames / f"{model}-t%03d.png")])
    return {
        "model": model,
        "video": str(clear.relative_to(REPO_ROOT)),
        "launchOutput": launch.stdout.strip(),
        "launchLeadSeconds": LAUNCH_LEAD_S,
        "enterDetailAfterSeconds": ENTER_DETAIL_AFTER_S,
        "recordSeconds": RECORD_SECONDS,
        "launchWallClock": launch_wall,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--udid", required=True)
    parser.add_argument("--app", required=True)
    parser.add_argument("--round", required=True)
    parser.add_argument("--models", default=",".join(MODELS))
    args = parser.parse_args()

    out_dir = OUT_ROOT / args.round
    out_dir.mkdir(parents=True, exist_ok=True)
    run(["xcrun", "simctl", "install", args.udid, args.app])
    app_path = Path(args.app)
    app_hash = run(["shasum", "-a", "256",
                    str(app_path / app_path.stem)]).stdout.split()[0]

    results = []
    for model in args.models.split(","):
        model = model.strip()
        if not model:
            continue
        print(f"[capture] {model}", flush=True)
        results.append(capture_model(args.udid, model, out_dir, args.round))

    manifest = {
        "round": args.round,
        "udid": args.udid,
        "bundleId": BUNDLE_ID,
        "appBinarySha256": app_hash,
        "app": args.app,
        "captures": results,
    }
    (out_dir / f"{args.round}-simulator-capture.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
