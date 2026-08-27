#!/usr/bin/env python3
"""Validate Gate 07 rev 6 motif, blood red, silver, diagnostics, and scope."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
MATERIAL_REPORT = ROOT / "material-validation.json"
LINEAGE_REPORT = ROOT / "artwork-lineage-validation.json"
COLOR_REPORT = ROOT / "blood-red-source-analysis.json"
NOISY = ROOT / "rev5-noisy-mask-same-camera.png"
CRISP = ROOT / "restored-crisp-mask-same-camera.png"
GRAY = ROOT / "gray-edge-same-camera.png"
SILVER = ROOT / "pure-silver-edge-same-camera.png"
FRONT = ROOT / "neutral-front-blood-red.png"
OPEN = ROOT / "open-slide-lower-artwork.png"
SIDE = ROOT / "diagnostic-side-white-card-reflection.png"
CARDS = ROOT / "diagnostic-silver-reflection-cards.png"
OUTPUT = ROOT / "image-material-validation.json"


def face_sharpness(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB"))
    crop = rgb[280:740, 120:780]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    return {
        "roiPx": [120, 280, 780, 740],
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 64, 192))),
    }


def neutral_body_metrics(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB"))[700:980, 100:800].reshape(-1, 3).astype(np.float64)
    chroma = rgb.max(axis=1) - rgb.min(axis=1)
    neutral = rgb[chroma <= 18]
    luma = 0.2126 * neutral[:, 0] + 0.7152 * neutral[:, 1] + 0.0722 * neutral[:, 2]
    return {
        "roiPx": [100, 700, 800, 980],
        "neutralSamples": int(len(neutral)),
        "neutralMedianLuma": round(float(np.median(luma)), 6),
        "neutralMeanChroma": round(float(np.mean(neutral.max(axis=1) - neutral.min(axis=1))), 6),
        "neutralP90Luma": round(float(np.percentile(luma, 90)), 6),
        "neutralHighlightAbove180Fraction": round(float(np.mean(luma >= 180)), 8),
        "neutralClipAbove250Fraction": round(float(np.mean(neutral.max(axis=1) >= 250)), 8),
    }


def red_metrics(path: Path) -> dict:
    pixels = np.asarray(Image.open(path).convert("RGB")).reshape(-1, 3)
    selected = []
    pink = 0
    blood = 0
    clipped = int(np.count_nonzero(pixels.max(axis=1) >= 250))
    for r, g, b in pixels:
        hue, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        signed_hue = ((hue * 360 + 180) % 360) - 180
        if r > 35 and r > g * 1.35 and r > b * 1.18 and saturation > 0.42:
            selected.append((signed_hue, saturation, value))
            pink += int(-65 <= signed_hue < -20)
            blood += int(-20 <= signed_hue <= 15 and value <= 0.92)
    if not selected:
        raise RuntimeError("No red pixels detected.")
    return {
        "selectedPixels": len(selected),
        "signedHueMedianDegrees": round(float(np.median([item[0] for item in selected])), 6),
        "pinkFraction": round(pink / len(selected), 8),
        "bloodRedFraction": round(blood / len(selected), 8),
        "wholeImageClipAbove250Fraction": round(clipped / len(pixels), 8),
    }


def card_metrics() -> dict:
    rgb = np.asarray(Image.open(CARDS).convert("RGB"))
    boxes = {
        "white": rgb[50:200, 900:1200],
        "gray": rgb[50:200, 400:700],
        "black": rgb[50:200, 1460:1495],
    }
    return {
        name: round(float(np.mean(0.2126 * box[..., 0] + 0.7152 * box[..., 1] + 0.0722 * box[..., 2])), 6)
        for name, box in boxes.items()
    }


def side_metrics() -> dict:
    rgb = np.asarray(Image.open(SIDE).convert("RGB"))
    height, width, _ = rgb.shape
    roi = rgb[round(height * 0.34):round(height * 0.9), 0:width]
    chroma = roi.max(axis=2) - roi.min(axis=2)
    luma = 0.2126 * roi[..., 0] + 0.7152 * roi[..., 1] + 0.0722 * roi[..., 2]
    neutral_highlight = (chroma <= 22) & (luma >= 145)
    spans = []
    for row in neutral_highlight:
        xs = np.flatnonzero(row)
        if len(xs):
            spans.append(int(xs[-1] - xs[0] + 1))
    return {
        "maximumNeutralHighlightSpanPx": max(spans, default=0),
        "maximumNeutralHighlightSpanFraction": round(max(spans, default=0) / width, 6),
        "neutralHighlightPixels": int(np.count_nonzero(neutral_highlight)),
    }


def lower_metrics() -> dict:
    rgb = np.asarray(Image.open(OPEN).convert("RGB"))
    crop = rgb[620:1180, 70:680]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    return {
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 64, 192))),
    }


def comparison_board(left_path: Path, right_path: Path, left_title: str, right_title: str, subtitle: str, output: str) -> None:
    canvas = Image.new("RGB", (2200, 1450), (21, 25, 31))
    left = ImageOps.contain(Image.open(left_path).convert("RGB"), (1020, 1260))
    right = ImageOps.contain(Image.open(right_path).convert("RGB"), (1020, 1260))
    canvas.paste(left, (50 + (1020 - left.width) // 2, 130))
    canvas.paste(right, (1130 + (1020 - right.width) // 2, 130))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=30)
    small = ImageFont.load_default(size=19)
    draw.text((50, 35), left_title, fill=(226, 110, 110), font=title)
    draw.text((1130, 35), right_title, fill=(92, 214, 150), font=title)
    draw.text((50, 82), subtitle, fill=(188, 196, 208), font=small)
    canvas.save(ROOT / output)


def main() -> None:
    material = json.loads(MATERIAL_REPORT.read_text(encoding="utf-8"))
    lineage = json.loads(LINEAGE_REPORT.read_text(encoding="utf-8"))
    color = json.loads(COLOR_REPORT.read_text(encoding="utf-8"))
    noisy = face_sharpness(NOISY)
    crisp = face_sharpness(CRISP)
    gray = neutral_body_metrics(GRAY)
    silver = neutral_body_metrics(SILVER)
    red = red_metrics(FRONT)
    cards = card_metrics()
    side = side_metrics()
    lower = lower_metrics()
    comparison_board(
        NOISY,
        CRISP,
        "REV 5 REJECTED · NOISY DIRECT TRACE",
        "REV 6 · RESTORED CLEAN REV 2/3 MOTIF",
        "Same camera, light, blood-red substrate, polished-silver body, and exposure.",
        "mask-comparison-same-camera.png",
    )
    comparison_board(
        GRAY,
        SILVER,
        "REV 5 GRAY-EDGE SHADER",
        "REV 6 POLISHED PURE-SILVER TARGET",
        "Same camera, clean motif, blood-red substrate, lights, and exposure.",
        "silver-comparison-same-camera.png",
    )
    target_hue = color["correctedHsv"]["hueSignedMedianDegrees"]
    pure_silver = material["materialZones"]["polished-pure-silver-visual-target-exterior"]
    checks = {
        "lineageAndLosslessIdentity": lineage["pass"],
        "renderedPatternSharperThanRev5": crisp["laplacianVariance"] >= noisy["laplacianVariance"] * 1.5,
        "renderedConnectedDetailImproved": crisp["cannyEdgePixels"] >= noisy["cannyEdgePixels"],
        "lowerPatternLegible": lower["laplacianVariance"] >= 70 and lower["cannyEdgePixels"] >= 3000,
        "silverNeutral": silver["neutralMeanChroma"] <= 12,
        "silverMedianBrighterThanGray": silver["neutralMedianLuma"] >= gray["neutralMedianLuma"] + 10,
        "silverHighlightsWithoutClipping": silver["neutralP90Luma"] >= 200
        and silver["neutralClipAbove250Fraction"] <= 0.002,
        "reflectionCardsOrdered": cards["white"] > cards["gray"] > cards["black"],
        "sideWhiteCardReflectionVisible": side["maximumNeutralHighlightSpanFraction"] >= 0.20,
        "bloodRedTarget": abs(red["signedHueMedianDegrees"] - target_hue) <= 14
        and red["pinkFraction"] <= 0.04
        and red["bloodRedFraction"] >= 0.82,
        "wholeImageClippingControlled": red["wholeImageClipAbove250Fraction"] <= 0.01,
        "silverShaderValues": pure_silver["metallic"] == 1.0
        and pure_silver["roughness"] == 0.045
        and pure_silver["anisotropy"] == 0.22
        and pure_silver["productionMaterialClaim"] is False,
        "steelClaimBoundary": material["uncertaintyPolicy"]["exactProductMaterialConfirmed"] == "steel"
        and material["uncertaintyPolicy"]["pureSilverIsProductionMaterialClaim"] is False,
        "noEmission": material["forbiddenLightingAndShaderTricks"]["pass"],
        "geometryDigestUnchanged": material["geometryPreservation"]["pass"],
        "mechanismScopeUnchanged": material["mechanismDecisionMetadata"]["detentCount"] == 30
        and material["mechanismDecisionMetadata"]["deliveryState"] == "specified-only-runtime-and-hardware-validation-pending",
        "gate07Only": not any(material["scope"].values()),
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 6,
        "motifSharpness": {"rev5Rejected": noisy, "rev6Restored": crisp},
        "silverComparison": {"rev5Gray": gray, "rev6PureSilverTarget": silver},
        "bloodRed": red,
        "reflectionCards": cards,
        "sideWhiteCard": side,
        "openLowerArtwork": lower,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 6 image/material validation failed.")


if __name__ == "__main__":
    main()
