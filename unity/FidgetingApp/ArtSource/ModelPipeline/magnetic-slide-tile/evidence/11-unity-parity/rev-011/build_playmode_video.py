#!/usr/bin/env python3
"""Encode and validate the corrected Unity-only Gate 11 recording."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
FRAMES = HERE / "unity-playmode-frames"
VIDEO = HERE / "magnetic-slide-tile-gate11-r011-unity-playmode.mp4"
CAPTURE = FRAMES / "unity-playmode-capture-report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "30",
        "-i", str(FRAMES / "frame-%04d.png"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(VIDEO),
    ], check=True)
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_streams", "-show_format", "-of", "json", str(VIDEO),
    ]))
    capture = json.loads(CAPTURE.read_text())
    stream = probe["streams"][0]
    checks = {
        "unityOnly": (
            capture["blenderFrames"] == 0
            and capture["offlineCompositeFrames"] == 0
        ),
        "endpointInterlock": capture["endpointInterlock"],
        "fullRotationThirtyDetents": capture["fullRotationDetents"] == 30,
        "closedZeroMotion": capture["closedZeroMotion"],
        "noPitchRollFlip": (
            capture["productPitchRollDegrees"] == 0
            and capture["cameraRollDegrees"] == 0
            and capture["cameraElevationVarianceMeters"] == 0
        ),
        "frameCount": int(stream["nb_read_frames"]) == 540,
        "resolution": [stream["width"], stream["height"]] == [1920, 1080],
        "frameRate": stream["avg_frame_rate"] == "30/1",
        "codec": stream["codec_name"] == "h264",
    }
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 11,
        "video": VIDEO.name,
        "sha256": sha256(VIDEO),
        "bytes": VIDEO.stat().st_size,
        "captureReportSha256": sha256(CAPTURE),
        "checks": checks,
        "probe": probe,
        "pass": all(checks.values()),
    }
    (HERE / "unity-playmode-video-validation.json").write_text(
        json.dumps(report, indent=2) + "\n")
    if not report["pass"]:
        raise RuntimeError("Unity-only Gate 11 video validation failed.")


if __name__ == "__main__":
    main()
