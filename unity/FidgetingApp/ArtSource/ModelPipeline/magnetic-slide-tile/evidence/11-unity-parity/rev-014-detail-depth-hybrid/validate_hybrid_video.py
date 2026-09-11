#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
VIDEO = ROOT / "gate11-r014-rev12-rev13-hybrid-unity.mp4"


def frame(index):
    return np.asarray(
        Image.open(
            ROOT / "triptych-motion-frames" / f"frame-{index:04d}.png"
        ).convert("RGB"),
        dtype=np.float32,
    )


probe = json.loads(subprocess.check_output([
    "ffprobe",
    "-v", "error",
    "-show_streams",
    "-show_format",
    "-of", "json",
    str(VIDEO),
], text=True))
stream = probe["streams"][0]
first = frame(0)
middle = frame(75)
last = frame(149)
hybrid_red_fractions = []
hybrid_clipped_fractions = []
hybrid_luminance = []
for index in range(150):
    rgb = np.asarray(
        Image.open(
            ROOT / "C-rev14-hybrid-motion-frames"
            / f"frame-{index:04d}.png"
        ).convert("RGB"),
        dtype=np.float32,
    ) / 255.0
    red = (
        (rgb[..., 0] > 0.10)
        & (rgb[..., 0] > rgb[..., 1] * 1.35)
        & (rgb[..., 0] > rgb[..., 2] * 1.18)
    )
    hybrid_red_fractions.append(float(np.mean(red)))
    hybrid_clipped_fractions.append(
        float(np.mean(np.max(rgb, axis=2) >= 0.995)))
    hybrid_luminance.append(float(np.mean(rgb)))
red_frame_deltas = np.abs(np.diff(hybrid_red_fractions))
result = {
    "schemaVersion": 1,
    "source": "450 real Unity frames arranged as a three-way comparison",
    "codec": stream["codec_name"],
    "profile": stream["profile"],
    "width": stream["width"],
    "height": stream["height"],
    "frameRate": stream["avg_frame_rate"],
    "frameCount": int(stream["nb_frames"]),
    "durationSeconds": float(probe["format"]["duration"]),
    "firstMiddleMeanAbsoluteDifference":
        float(np.mean(np.abs(first - middle))),
    "middleLastMeanAbsoluteDifference":
        float(np.mean(np.abs(middle - last))),
    "hybridMaximumRedCoverageFrameDelta":
        float(np.max(red_frame_deltas)),
    "hybridMaximumClippedFraction":
        float(np.max(hybrid_clipped_fractions)),
    "hybridMinimumMeanLuminance":
        float(np.min(hybrid_luminance)),
}
result["checks"] = {
    "h264": result["codec"] == "h264",
    "dimensions": result["width"] == 1920 and result["height"] == 400,
    "frameCount": result["frameCount"] == 150,
    "duration": 4.9 <= result["durationSeconds"] <= 5.1,
    "movingNotFrozen":
        result["firstMiddleMeanAbsoluteDifference"] > 3.0
        and result["middleLastMeanAbsoluteDifference"] > 3.0,
    "noSortingOrZFightingCoverageJump":
        result["hybridMaximumRedCoverageFrameDelta"] < 0.02,
    "noWashoutOrBlankFrame":
        result["hybridMaximumClippedFraction"] < 0.005
        and result["hybridMinimumMeanLuminance"] > 0.01,
}
result["pass"] = all(result["checks"].values())
(ROOT / "hybrid-video-validation.json").write_text(
    json.dumps(result, indent=2) + "\n")
if not result["pass"]:
    raise SystemExit("Hybrid video validation failed.")
