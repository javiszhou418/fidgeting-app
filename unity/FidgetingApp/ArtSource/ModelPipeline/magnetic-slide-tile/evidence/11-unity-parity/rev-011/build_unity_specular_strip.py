#!/usr/bin/env python3
"""Pack approved Unity-oriented HDR faces for Unity GGX convolution."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
FACES = HERE.parent.parent / "10-export" / "rev-011" / "package" / "environment" / "cubemap"
OUTPUT = HERE / "unity-specular-strip-r011.exr"
ORDER = [
    "positive-x",
    "negative-x",
    "positive-y",
    "negative-y",
    "positive-z",
    "negative-z",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    images = []
    source_hashes = {}
    for name in ORDER:
        path = FACES / f"{name}.exr"
        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if image is None or image.shape != (512, 512, 4):
            raise RuntimeError(f"Invalid approved cubemap face: {path}")
        images.append(image.astype(np.float32))
        source_hashes[name] = sha256(path)
    strip = np.concatenate(images, axis=1)
    if not cv2.imwrite(str(OUTPUT), strip):
        raise RuntimeError(f"Failed to write {OUTPUT}")
    report = {
        "schemaVersion": 1,
        "layout": "horizontal +X,-X,+Y,-Y,+Z,-Z",
        "resolution": [3072, 512],
        "colorSpace": "scene-linear Rec.709/D65",
        "sourceFaces": source_hashes,
        "output": OUTPUT.name,
        "sha256": sha256(OUTPUT),
        "minimum": float(strip[..., :3].min()),
        "maximum": float(strip[..., :3].max()),
        "nonzeroRgbFraction": float(np.mean(np.any(strip[..., :3] > 0, axis=2))),
        "unityImport": {
            "textureShape": "TextureCube",
            "generateCubemap": "FullCubemap",
            "cubemapConvolution": "Specular",
            "sRGB": False,
            "mipmaps": True,
            "compression": "Uncompressed",
        },
        "pass": bool(np.isfinite(strip).all() and np.all(strip[..., :3] >= 0)),
    }
    (HERE / "unity-specular-strip-report.json").write_text(
        json.dumps(report, indent=2) + "\n")
    if not report["pass"]:
        raise RuntimeError("Unity specular strip audit failed.")


if __name__ == "__main__":
    main()
