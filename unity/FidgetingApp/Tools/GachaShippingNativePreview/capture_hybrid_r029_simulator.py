#!/usr/bin/env python3
"""Capture an R029 or R030 Unity iOS Simulator hybrid proof."""

from __future__ import annotations

import argparse
import json
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image


VISUAL_STAGES = ("sealed", "partial")
CHECKPOINTS = ("F0", "F1", "F2", "F3", "F4")
REVISION = "r029"
TRACE_FILE_NAME = "gacha-native-hybrid-r029-trace.ndjson"
BASE_ARGUMENT = "--premium-display-case-gate04-native-hybrid-r029"
CAPTURE_ARGUMENT = "--premium-display-case-gate04-native-hybrid-r029-capture="


def configure_revision(revision: str) -> None:
    global REVISION, TRACE_FILE_NAME, BASE_ARGUMENT, CAPTURE_ARGUMENT
    if revision not in {"r029", "r030"}:
        raise ValueError(f"unsupported native hybrid revision: {revision}")
    REVISION = revision
    TRACE_FILE_NAME = f"gacha-native-hybrid-{REVISION}-trace.ndjson"
    BASE_ARGUMENT = f"--premium-display-case-gate04-native-hybrid-{REVISION}"
    CAPTURE_ARGUMENT = f"{BASE_ARGUMENT}-capture="


def command(
    *args: str,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def app_container(device: str, bundle_id: str) -> Path:
    result = command(
        "xcrun",
        "simctl",
        "get_app_container",
        device,
        bundle_id,
        "data",
        capture_output=True,
    )
    return Path(result.stdout.strip())


def trace_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if isinstance(value, dict):
                events.append(value)
    return events


def wait_for_checkpoint(
    trace_path: Path,
    checkpoint: str,
    timeout: float,
) -> list[dict[str, Any]]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        events = trace_events(trace_path)
        if any(
            event.get("checkpoint") == checkpoint
            and event.get("caseRootName") == "PremiumDisplayCaseGate12R004"
            for event in events
        ):
            return events
        time.sleep(0.04)
    raise TimeoutError(f"timed out waiting for {checkpoint} in {trace_path}")


def wait_for_file(path: Path, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            return
        time.sleep(0.04)
    raise TimeoutError(f"timed out waiting for diagnostic {path}")


def install_fresh_player(
    device: str,
    bundle_id: str,
    app: Path,
) -> Path:
    command(
        "xcrun",
        "simctl",
        "terminate",
        device,
        bundle_id,
        check=False,
    )
    command(
        "xcrun",
        "simctl",
        "uninstall",
        device,
        bundle_id,
        check=False,
    )
    command("xcrun", "simctl", "install", device, str(app))
    return app_container(device, bundle_id)


def launch(
    device: str,
    bundle_id: str,
    checkpoint: str | None,
) -> None:
    arguments = [BASE_ARGUMENT]
    if checkpoint is not None:
        arguments.append(CAPTURE_ARGUMENT + checkpoint)
    command(
        "xcrun",
        "simctl",
        "launch",
        "--terminate-running-process",
        device,
        bundle_id,
        *arguments,
    )


def copy_checkpoint_artifacts(
    container: Path,
    checkpoint: str,
    output: Path,
    timeout: float,
) -> tuple[Path, Path, Path]:
    documents = container / "Documents"
    trace = documents / TRACE_FILE_NAME
    wait_for_checkpoint(trace, checkpoint, timeout)
    overlay = documents / (
        f"gacha-native-hybrid-{REVISION}-{checkpoint}-overlay.json")
    overlay_alpha = documents / (
        f"gacha-native-hybrid-{REVISION}-{checkpoint}-overlay.png")
    wait_for_file(overlay, timeout)
    wait_for_file(overlay_alpha, timeout)
    destination_trace = output / f"{checkpoint}.trace.ndjson"
    destination_overlay = output / f"{checkpoint}.overlay.json"
    destination_overlay_alpha = output / f"{checkpoint}.overlay.png"
    shutil.copy2(trace, destination_trace)
    shutil.copy2(overlay, destination_overlay)
    shutil.copy2(overlay_alpha, destination_overlay_alpha)
    return destination_trace, destination_overlay, destination_overlay_alpha


def capture_checkpoint(
    device: str,
    bundle_id: str,
    app: Path,
    checkpoint: str,
    output: Path,
    timeout: float,
) -> None:
    container = install_fresh_player(device, bundle_id, app)
    launch(device, bundle_id, checkpoint)
    try:
        copy_checkpoint_artifacts(container, checkpoint, output, timeout)
        command(
            "xcrun",
            "simctl",
            "io",
            device,
            "screenshot",
            str(output / f"{checkpoint}.png"),
        )
    finally:
        command(
            "xcrun",
            "simctl",
            "terminate",
            device,
            bundle_id,
            check=False,
        )


def capture_visual_stage(
    device: str,
    bundle_id: str,
    app: Path,
    stage: str,
    output: Path,
    timeout: float,
) -> None:
    container = install_fresh_player(device, bundle_id, app)
    launch(device, bundle_id, stage)
    try:
        overlay = (
            container
            / "Documents"
            / f"gacha-native-hybrid-{REVISION}-{stage}-overlay.json"
        )
        overlay_alpha = (
            container
            / "Documents"
            / f"gacha-native-hybrid-{REVISION}-{stage}-overlay.png"
        )
        wait_for_file(overlay, timeout)
        wait_for_file(overlay_alpha, timeout)
        shutil.copy2(overlay, output / f"{stage}.overlay.json")
        shutil.copy2(overlay_alpha, output / f"{stage}.overlay.png")
        command(
            "xcrun",
            "simctl",
            "io",
            device,
            "screenshot",
            str(output / f"{stage}.png"),
        )
    finally:
        command(
            "xcrun",
            "simctl",
            "terminate",
            device,
            bundle_id,
            check=False,
        )


def event_for_checkpoint(
    events: list[dict[str, Any]],
    checkpoint: str,
) -> dict[str, Any]:
    matches = [
        event for event in events
        if event.get("checkpoint") == checkpoint
        and event.get("caseRootName") == "PremiumDisplayCaseGate12R004"
    ]
    if not matches:
        raise ValueError(f"normal trace lacks {checkpoint}")
    return matches[-1]


def capture_normal_video(
    device: str,
    bundle_id: str,
    app: Path,
    output: Path,
    timeout: float,
) -> tuple[Path, float]:
    container = install_fresh_player(device, bundle_id, app)
    documents = container / "Documents"
    trace = documents / TRACE_FILE_NAME
    raw_video = output / f"{REVISION}-normal-raw.mp4"
    video_started_at = time.time()
    recorder = subprocess.Popen(
        [
            "xcrun",
            "simctl",
            "io",
            device,
            "recordVideo",
            "--codec=h264",
            str(raw_video),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(0.12)
        launch(device, bundle_id, None)
        events = wait_for_checkpoint(trace, "F4", timeout)
    finally:
        recorder.send_signal(signal.SIGINT)
        try:
            recorder.wait(timeout=8)
        except subprocess.TimeoutExpired:
            recorder.kill()
            recorder.wait(timeout=8)
        command(
            "xcrun",
            "simctl",
            "terminate",
            device,
            bundle_id,
            check=False,
        )

    normal_trace = output / "normal.trace.ndjson"
    shutil.copy2(trace, normal_trace)
    f4 = event_for_checkpoint(events, "F4")
    started_at = float(f4.get("candidateSequenceStartedAtUnix", 0))
    completed_at = float(f4.get("recordedAtUnix", 0))
    duration = completed_at - started_at
    if not 1.2 <= duration <= 1.8:
        raise ValueError(
            f"normal {REVISION.upper()} sequence is {duration:.3f}s; "
            "expected 1.2–1.8s"
        )
    trim_start = max(0, started_at - video_started_at)
    normal_video = output / f"{REVISION}-normal.mp4"
    command(
        "ffmpeg",
        "-y",
        "-ss",
        f"{trim_start:.3f}",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(raw_video),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(normal_video),
    )
    return normal_video, duration


def make_derived_media(output: Path, normal_video: Path) -> None:
    stages = (*VISUAL_STAGES, *CHECKPOINTS)
    images = [output / f"{stage}.png" for stage in stages]
    filter_parts = [
        f"[{index}:v]scale=168:-1[s{index}]"
        for index, _ in enumerate(stages)
    ]
    stacked = "".join(f"[s{index}]" for index, _ in enumerate(stages))
    command(
        "ffmpeg",
        "-y",
        *sum((("-i", str(image)) for image in images), ()),
        "-filter_complex",
        ";".join(filter_parts)
        + f";{stacked}hstack=inputs={len(stages)}[out]",
        "-map",
        "[out]",
        "-frames:v",
        "1",
        str(output / f"{REVISION}-primary-contact-sheet.png"),
    )
    with Image.open(output / "F2.png") as image:
        width, height = image.size
    crop_height = round(height * 0.34)
    crop_y = round(height * 0.24)
    command(
        "ffmpeg",
        "-y",
        "-t",
        "0.64",
        "-i",
        str(normal_video),
        "-an",
        "-vf",
        f"crop={width}:{crop_height}:0:{crop_y},setpts=4*PTS",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output / f"{REVISION}-quarter-speed-tear-closeup.mp4"),
    )


def write_trace_diagnostic(output: Path) -> None:
    report_path = output / f"{REVISION}-integration-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    payload = {
        "candidate": f"{REVISION.upper()} isolated native hybrid",
        "integrationVerdict": report.get("verdict"),
        "traceFiles": {
            checkpoint: f"{checkpoint}.trace.ndjson"
            for checkpoint in CHECKPOINTS
        },
        "checks": report.get("checks", {}),
        "metrics": report.get("metrics", {}),
    }
    (output / f"{REVISION}-trace-diagnostic.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify(project_root: Path, output: Path) -> None:
    command(
        sys.executable,
        str(project_root / "Tools/GachaShippingNativePreview/verify_hybrid_r029.py"),
        "--revision",
        REVISION,
        *sum(
            (
                (
                    f"--{checkpoint.lower()}",
                    str(output / f"{checkpoint}.png"),
                    f"--{checkpoint.lower()}-trace",
                    str(output / f"{checkpoint}.trace.ndjson"),
                    f"--{checkpoint.lower()}-overlay",
                    str(output / f"{checkpoint}.overlay.json"),
                    f"--{checkpoint.lower()}-overlay-alpha",
                    str(output / f"{checkpoint}.overlay.png"),
                )
                for checkpoint in CHECKPOINTS
            ),
            (),
        ),
        "--sealed",
        str(output / "sealed.png"),
        "--sealed-overlay",
        str(output / "sealed.overlay.json"),
        "--partial",
        str(output / "partial.png"),
        "--partial-overlay",
        str(output / "partial.overlay.json"),
        "--candidate-source",
        str(
            project_root
            / "Assets/Plugins/iOS"
            / f"FidgetGachaNativeHybrid{REVISION.upper()}Candidate.swift"
        ),
        "--components-source",
        str(project_root / "Assets/Plugins/iOS/FidgetProductUIComponents.swift"),
        "--rules-source",
        str(project_root / "Assets/Plugins/iOS/FidgetGachaPackPresentation.swift"),
        "--coordinator-source",
        str(project_root / "Assets/Scripts/Product/FidgetAppCoordinator.cs"),
        "--isolation-source",
        str(
            project_root
            / "Assets/Scripts/Product/Gacha"
            / "GachaNativeHybridSceneIsolation.cs"
        ),
        "--runner-source",
        str(project_root / "Tools/GachaShippingNativePreview/capture_hybrid_r029_simulator.py"),
        "--report",
        str(output / f"{REVISION}-integration-report.json"),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--revision",
        choices=("r029", "r030"),
        default="r029",
    )
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument(
        "--bundle-id",
        default="com.jiaweizhou.fidgetspinner.codex",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=25)
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()

    configure_revision(args.revision)
    if not args.app.is_dir():
        raise ValueError(f"exported Simulator Player is missing: {args.app}")
    args.output = args.output.resolve()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError(f"refusing to overwrite existing evidence: {args.output}")
    args.output.mkdir(parents=True, exist_ok=True)
    command("xcrun", "simctl", "boot", args.device, check=False)
    command("xcrun", "simctl", "bootstatus", args.device, "-b")

    for stage in VISUAL_STAGES:
        capture_visual_stage(
            args.device,
            args.bundle_id,
            args.app,
            stage,
            args.output,
            args.timeout,
        )
    for checkpoint in CHECKPOINTS:
        capture_checkpoint(
            args.device,
            args.bundle_id,
            args.app,
            checkpoint,
            args.output,
            args.timeout,
        )
    project_root = Path(__file__).resolve().parents[2]
    verify(project_root, args.output)
    write_trace_diagnostic(args.output)
    duration: float | None = None
    if not args.static_only:
        normal_video, duration = capture_normal_video(
            args.device,
            args.bundle_id,
            args.app,
            args.output,
            args.timeout,
        )
        make_derived_media(args.output, normal_video)
    manifest = {
        "candidate": f"{REVISION.upper()} isolated native hybrid",
        "player": str(args.app),
        "simulatorDevice": args.device,
        "normalSequenceDurationSeconds": duration,
        "visualStages": list(VISUAL_STAGES),
        "captureModes": list(CHECKPOINTS),
        "staticOnly": args.static_only,
        "physicalDeviceInstalled": False,
        "shippingReady": False,
    }
    (args.output / f"{REVISION}-capture-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
