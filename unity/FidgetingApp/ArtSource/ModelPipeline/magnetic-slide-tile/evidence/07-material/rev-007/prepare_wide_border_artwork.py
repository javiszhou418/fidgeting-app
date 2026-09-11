#!/usr/bin/env python3
"""Prepare Gate 07 rev 7 editable full-perimeter top-face border."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
REV2_MASK = ROOT.parent / "rev-002/source-derived-motif-visual-trace.png"
REV6_UPPER = ROOT.parent / "rev-006/artwork-upper-mask.png"
REV6_LOWER = ROOT.parent / "rev-006/artwork-lower-mask.png"
UPPER = ROOT / "artwork-upper-mask.png"
LOWER = ROOT / "artwork-lower-mask.png"
BORDER = ROOT / "artwork-top-perimeter-border-mask.png"
EXPECTED_MOTIF_SHA256 = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
BORDER_WIDTH_PX = 64
MINOR_AXIS_MM = 31.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capsule_mask(width: int, height: int) -> np.ndarray:
    radius = width / 2
    x = np.arange(width, dtype=np.float32) + 0.5
    y = np.arange(height, dtype=np.float32) + 0.5
    xx, yy = np.meshgrid(x, y)
    center_x = width / 2
    top_center_y = radius
    bottom_center_y = height - radius
    middle = (np.abs(xx - center_x) <= radius) & (yy >= top_center_y) & (yy <= bottom_center_y)
    top = (xx - center_x) ** 2 + (yy - top_center_y) ** 2 <= radius ** 2
    bottom = (xx - center_x) ** 2 + (yy - bottom_center_y) ** 2 <= radius ** 2
    return (middle | top | bottom).astype(np.uint8)


def make_border(width: int, height: int) -> dict:
    outer = capsule_mask(width, height)
    padded = np.pad(outer, 1, mode="constant", constant_values=0)
    distance = cv2.distanceTransform(padded, cv2.DIST_L2, 5)[1:-1, 1:-1]
    ring = ((outer == 1) & (distance <= BORDER_WIDTH_PX)).astype(np.uint8) * 255
    Image.fromarray(ring, "L").save(BORDER)
    center_row = ring[height // 2]
    white = np.flatnonzero(center_row == 255)
    left_reach = int(white.min())
    right_reach = int(width - 1 - white.max())
    inner_transition = int(np.flatnonzero(center_row == 0).min())
    return {
        "sizePx": [width, height],
        "widthPx": BORDER_WIDTH_PX,
        "widthFractionMinorAxis": round(BORDER_WIDTH_PX / width, 8),
        "approxVisualWidthMm": round(BORDER_WIDTH_PX * MINOR_AXIS_MM / width, 4),
        "outerPerimeterReachPx": {
            "left": left_reach,
            "right": right_reach,
            "top": int(np.flatnonzero(ring[:, width // 2] == 255).min()),
            "bottom": int(height - 1 - np.flatnonzero(ring[:, width // 2] == 255).max()),
        },
        "centerRowInnerTransitionPx": inner_transition,
        "coverage": round(float(np.mean(ring > 0)), 8),
    }


def boundary_diagram(border_metrics: dict) -> None:
    canvas = Image.new("RGB", (2000, 1250), (20, 24, 30))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=23)
    small = ImageFont.load_default(size=18)
    draw.text((60, 42), "GATE 07 REV 7 · TOP-FACE MATERIAL BOUNDARY", fill=(244, 246, 250), font=title)
    draw.text((60, 92), "Editable mask expansion only. Geometry and vertical side wall remain unchanged.", fill=(184, 192, 204), font=label)
    top = Image.new("RGB", (620, 1000), (174, 0, 18))
    border = np.asarray(Image.open(BORDER).convert("L"))
    motif = np.asarray(Image.open(UPPER).convert("L"))
    array = np.asarray(top).copy()
    array[border > 0] = (8, 8, 10)
    array[(motif > 0) & (border == 0)] = (18, 15, 18)
    preview = Image.fromarray(array)
    preview.thumbnail((520, 840))
    canvas.paste(preview, (90, 210))
    draw.text((90, 1080), "TOP FACE", fill=(240, 242, 246), font=label)
    draw.text((90, 1120), "BLACK = full outer perimeter + clean motif", fill=(198, 204, 214), font=small)
    draw.text((90, 1150), "RED = remaining blood-red crystal field", fill=(198, 204, 214), font=small)

    draw.rounded_rectangle((790, 300, 1830, 830), radius=48, fill=(48, 54, 64), outline=(120, 128, 142), width=3)
    draw.rectangle((830, 340, 1790, 460), fill=(10, 10, 12))
    draw.rectangle((830, 460, 1790, 520), fill=(174, 0, 18))
    draw.rectangle((830, 520, 1790, 770), fill=(196, 198, 198))
    draw.line((830, 520, 1790, 520), fill=(244, 246, 248), width=8)
    draw.text((910, 365), "BLACK TOP PERIMETER · EXTENDS TO OUTER TOP-FACE EDGE", fill=(238, 240, 244), font=label)
    draw.text((910, 474), "BLOOD-RED CRYSTAL FIELD", fill=(248, 216, 220), font=small)
    draw.text((910, 610), "SILVER STRUCTURAL VERTICAL SIDE WALL", fill=(34, 38, 44), font=label)
    draw.text((910, 680), "The silver side/rim is not replaced by the black artwork mask.", fill=(34, 38, 44), font=small)
    draw.text((790, 900), f"Editable border width: {border_metrics['widthPx']} px = {border_metrics['widthFractionMinorAxis']:.2%} of minor axis ≈ {border_metrics['approxVisualWidthMm']} mm", fill=(232, 236, 242), font=label)
    draw.text((790, 950), "Outer reach: 0 px inset on left / right / top / bottom.", fill=(134, 211, 166), font=label)
    draw.text((790, 1010), "Artwork_Upper and Artwork_Lower keep separate clean-motif files.", fill=(190, 198, 210), font=small)
    draw.text((790, 1050), "Shared top-perimeter border mask is independently replaceable and does not rebuild mesh.", fill=(190, 198, 210), font=small)
    canvas.save(ROOT / "top-face-boundary-diagram.png")


def main() -> None:
    hashes = {path.name: sha256(path) for path in (REV2_MASK, REV6_UPPER, REV6_LOWER, UPPER, LOWER)}
    if any(value != EXPECTED_MOTIF_SHA256 for value in hashes.values()):
        raise RuntimeError(f"Clean motif lineage changed: {hashes}")
    with Image.open(UPPER) as image:
        width, height = image.size
    border_metrics = make_border(width, height)
    settings = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "settingId": "TopFaceBlackPerimeterBorder",
        "mask": BORDER.name,
        "maskSha256": sha256(BORDER),
        "compositionOperation": "maximum(cleanMotifMask, topPerimeterBorderMask)",
        "borderWidthPx": BORDER_WIDTH_PX,
        "borderWidthFractionMinorAxis": border_metrics["widthFractionMinorAxis"],
        "approxVisualWidthMm": border_metrics["approxVisualWidthMm"],
        "outerPerimeterInsetPx": 0,
        "appliesTo": ["Artwork_Upper", "Artwork_Lower"],
        "geometryChanged": False,
        "topologyBoundary": {
            "black": "decorative top-face perimeter/inlay only",
            "silver": "structural vertical side wall and visible metal rim",
        },
        "metrics": border_metrics,
    }
    (ROOT / "border-settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    lineage = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "reuseClass": "user-authorized-prior-material-design-reuse-with-editable-border-overlay",
        "notNewExactTraceClaim": True,
        "sourceAssetId": "magnetic-slide-tile-motif-mask-r002",
        "sourceMaterialRevision": 2,
        "unchangedInMaterialRevisions": [3, 6, 7],
        "sourceSha256": EXPECTED_MOTIF_SHA256,
        "slots": {
            "Artwork_Upper": {"mask": UPPER.name, "sha256": sha256(UPPER), "independentlyEditable": True},
            "Artwork_Lower": {"mask": LOWER.name, "sha256": sha256(LOWER), "independentlyEditable": True},
        },
        "borderOverlay": {
            "mask": BORDER.name,
            "sha256": sha256(BORDER),
            "settings": "border-settings.json",
            "independentlyEditable": True,
            "sharedInitialSetting": True,
        },
    }
    (ROOT / "artwork-lineage.json").write_text(json.dumps(lineage, indent=2) + "\n", encoding="utf-8")
    artwork = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "geometryDigest": GEOMETRY_DIGEST,
        "reuseClass": lineage["reuseClass"],
        "notNewExactTraceClaim": True,
        "slots": {
            name: {
                "mask": slot["mask"],
                "maskSha256": slot["sha256"],
                "independentlyEditable": True,
                "sourceAssetIds": ["magnetic-slide-tile-motif-mask-r002"],
            }
            for name, slot in lineage["slots"].items()
        },
        "topPerimeterBorder": {
            "mask": BORDER.name,
            "maskSha256": sha256(BORDER),
            "settings": "border-settings.json",
            "independentlyEditable": True,
            "compositionOperation": settings["compositionOperation"],
        },
        "swapContract": "Upper/lower clean motif paths remain separate. The shared initial border overlay is a third external mask and parameterized setting.",
    }
    (ROOT / "artwork-layers.json").write_text(json.dumps(artwork, indent=2) + "\n", encoding="utf-8")
    boundary_diagram(border_metrics)
    checks = {
        "cleanMotifLineagePreserved": all(value == EXPECTED_MOTIF_SHA256 for value in hashes.values()),
        "borderMaskExternal": BORDER.exists() and sha256(BORDER) == settings["maskSha256"],
        "borderReachesOuterPerimeter": all(value == 0 for value in border_metrics["outerPerimeterReachPx"].values()),
        "borderWidthExposed": settings["borderWidthPx"] == BORDER_WIDTH_PX and settings["borderWidthFractionMinorAxis"] > 0,
        "geometryDigestUnchanged": artwork["geometryDigest"] == GEOMETRY_DIGEST,
        "independentArtworkSlots": UPPER != LOWER,
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "hashes": hashes,
        "border": settings,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (ROOT / "artwork-border-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 7 border preparation failed.")


if __name__ == "__main__":
    main()
