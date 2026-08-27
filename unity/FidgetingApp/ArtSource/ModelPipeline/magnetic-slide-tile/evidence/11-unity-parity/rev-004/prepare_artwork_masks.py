#!/usr/bin/env python3
"""Preserve artwork placement while narrowing the editable black perimeter."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
IMPORTED = (
    ROOT.parents[5]
    / "Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001/Imported"
)
NEW_WIDTH_PX = 42


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def outer_capsule(border: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(
        (border > 127).astype(np.uint8) * 255,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    if not contours:
        raise RuntimeError("Border mask has no outer contour.")
    result = np.zeros_like(border)
    cv2.drawContours(result, [max(contours, key=cv2.contourArea)], -1, 255, cv2.FILLED)
    return result


def narrow_border(border: np.ndarray) -> np.ndarray:
    outer = outer_capsule(border)
    distance = cv2.distanceTransform(outer, cv2.DIST_L2, 5)
    narrowed = ((outer > 0) & (distance <= NEW_WIDTH_PX)).astype(np.uint8) * 255
    return narrowed


def build(name: str) -> dict:
    source = IMPORTED / f"artwork-{name}-channel-pack.png"
    rgba = np.array(Image.open(source).convert("RGBA"))
    motif = rgba[:, :, 0]
    old_border = rgba[:, :, 1]
    border = narrow_border(old_border)
    combined = np.maximum(motif, border)
    output = np.dstack([motif, border, combined, rgba[:, :, 3]])
    output_path = ROOT / f"artwork-{name}-channel-pack-r004.png"
    border_path = ROOT / f"artwork-{name}-border-r004.png"
    Image.fromarray(output, "RGBA").save(output_path)
    Image.fromarray(border, "L").save(border_path)
    return {
        "slot": name,
        "source": str(source),
        "sourceSha256": sha256(source),
        "output": output_path.name,
        "outputSha256": sha256(output_path),
        "border": border_path.name,
        "borderSha256": sha256(border_path),
        "motifByteIdentical": bool(np.array_equal(motif, output[:, :, 0])),
        "outerInsetPx": 0,
        "oldWidthPx": 64,
        "newWidthPx": NEW_WIDTH_PX,
        "size": [int(output.shape[1]), int(output.shape[0])],
    }


def main() -> None:
    records = [build("upper"), build("lower")]
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 4,
        "purpose": "narrow border without changing accepted motif placement",
        "records": records,
        "pass": all(
            record["motifByteIdentical"]
            and record["outerInsetPx"] == 0
            and record["newWidthPx"] == NEW_WIDTH_PX
            for record in records
        ),
    }
    (ROOT / "artwork-mask-preparation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Artwork mask preparation failed.")


if __name__ == "__main__":
    main()
