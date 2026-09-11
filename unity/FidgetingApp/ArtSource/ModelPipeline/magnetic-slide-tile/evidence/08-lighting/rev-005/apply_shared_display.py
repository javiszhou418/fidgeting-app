#!/usr/bin/env python3
"""Apply one deterministic display transform to Blender and Unity linear EXRs."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
BACKGROUND = np.array([0.035, 0.035, 0.035], dtype=np.float32)
EXPOSURE = 1.0
SHOULDER = 0.18


def linear_to_srgb(value):
    return np.where(
        value <= 0.0031308,
        value * 12.92,
        1.055 * np.power(np.maximum(value, 0.0), 1.0 / 2.4) - 0.055,
    )


def transform(linear):
    exposed = np.maximum(linear * EXPOSURE, 0.0)
    compressed = exposed / (1.0 + exposed * SHOULDER)
    return np.clip(linear_to_srgb(compressed), 0.0, 1.0)


def process(path):
    rgba = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if rgba is None or rgba.shape != (1100, 1400, 4):
        raise RuntimeError(f"Invalid linear EXR: {path}")
    rgba = rgba[:, :, [2, 1, 0, 3]].astype(np.float32)
    alpha = np.clip(rgba[:, :, 3:4], 0.0, 1.0)
    linear = rgba[:, :, :3] * alpha + BACKGROUND * (1.0 - alpha)
    display = transform(linear)
    output = path.with_name(path.name.replace("-linear.exr", "-display.png"))
    Image.fromarray(np.round(display * 255).astype(np.uint8)).save(output)
    return {
        "source": path.name,
        "output": output.name,
        "linearMinimum": float(linear.min()),
        "linearMaximum": float(linear.max()),
        "linearMean": float(linear.mean()),
        "alphaObjectFraction": float(np.mean(alpha[:, :, 0] > 0.5)),
        "displayClippedFraction": float(np.mean(np.max(display, axis=2) >= 1.0)),
    }


def main():
    files = sorted(HERE.glob("blender-*-linear.exr"))
    files += sorted(HERE.glob("unity-*-linear.exr"))
    if not files:
        raise RuntimeError("No linear EXRs found.")
    report = {
        "schemaVersion": 1,
        "transform": {
            "name": "neutral-display-v1",
            "input": "scene-linear Rec.709/D65",
            "exposureMultiplier": EXPOSURE,
            "shoulder": f"x/(1+{SHOULDER}x)",
            "encoding": "IEC 61966-2-1 sRGB",
            "backgroundLinear": BACKGROUND.tolist(),
        },
        "images": [process(path) for path in files],
    }
    (HERE / "shared-display-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
