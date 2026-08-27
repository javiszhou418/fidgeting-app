#!/usr/bin/env python3
"""Validate Gate 07 rev 5 color, reflections, artwork, and source boundaries."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "upper-source-rectified.png"
FRONT = ROOT / "neutral-front-blood-red.png"
NEUTRAL = ROOT / "neutral-pbr-material-closeup.png"
SECOND_LIGHT = ROOT / "diagnostic-second-light-crystal-response.png"
SIDE = ROOT / "diagnostic-side-direct-reflection.png"
OPEN = ROOT / "open-slide-lower-artwork.png"
MATERIAL_REPORT = ROOT / "material-validation.json"
COLOR_REPORT = ROOT / "blood-red-source-analysis.json"
ARTWORK_CONFIG = ROOT / "artwork-layers.json"
DERIVATION_REPORT = ROOT / "artwork-derivation-validation.json"
SUPPLEMENTAL_CONFIG = ROOT / "supplemental-source-manifest.json"
OUTPUT = ROOT / "image-artwork-validation.json"


def red_metrics(image: Image.Image) -> dict:
    pixels = list(image.convert("RGB").getdata())
    selected = []
    pink = 0
    blood = 0
    clipped = 0
    hard_clipped = 0
    for r, g, b in pixels:
        clipped += int(max(r, g, b) >= 250)
        hard_clipped += int(max(r, g, b) == 255)
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        signed_hue = ((h * 360 + 180) % 360) - 180
        if r > 35 and r > g * 1.35 and r > b * 1.18 and s > 0.42:
            selected.append((signed_hue, s, v))
            pink += int(-65 <= signed_hue < -20)
            blood += int(-20 <= signed_hue <= 15 and 0.45 <= s and 0.08 <= v <= 0.92)
    selected.sort(key=lambda item: item[0])
    if not selected:
        raise RuntimeError("No red face pixels found.")
    middle = len(selected) // 2
    return {
        "selectedPixels": len(selected),
        "signedHueMedianDegrees": round(selected[middle][0], 4),
        "saturationMedian": round(sorted(item[1] for item in selected)[middle], 4),
        "valueMedian": round(sorted(item[2] for item in selected)[middle], 4),
        "pinkFraction": round(pink / len(selected), 6),
        "bloodRedFraction": round(blood / len(selected), 6),
        "clippingAbove250Fraction": round(clipped / len(pixels), 8),
        "hard255Fraction": round(hard_clipped / len(pixels), 8),
    }


def highlight_metrics(image: Image.Image) -> dict:
    pixels = list(image.convert("RGB").getdata())
    luma = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in pixels]
    return {
        "above220Fraction": round(sum(value >= 220 for value in luma) / len(luma), 8),
        "above240Fraction": round(sum(value >= 240 for value in luma) / len(luma), 8),
        "maxLuma": round(max(luma), 4),
    }


def side_reflection_metrics(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    width, height = rgb.size
    row_spans = []
    bright_pixels = 0
    for y in range(round(height * 0.34), round(height * 0.78)):
        xs = []
        for x in range(round(width * 0.05), round(width * 0.95)):
            r, g, b = rgb.getpixel((x, y))
            luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if luma >= 145 and max(r, g, b) - min(r, g, b) <= 34:
                xs.append(x)
        bright_pixels += len(xs)
        if xs:
            row_spans.append(max(xs) - min(xs) + 1)
    return {
        "maximumReflectionSpanPx": max(row_spans, default=0),
        "maximumReflectionSpanFraction": round(max(row_spans, default=0) / width, 6),
        "brightNeutralPixels": bright_pixels,
        "metalCrystalBoundaryRowsDetected": sum(span >= width * 0.18 for span in row_spans),
    }


def lower_pattern_metrics(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    width, height = rgb.size
    crop = rgb.crop((round(width * 0.06), round(height * 0.46), round(width * 0.58), round(height * 0.88)))
    red = 0
    dark = 0
    for r, g, b in crop.getdata():
        if r > 35 and r > g * 1.25 and r > b * 1.12:
            red += 1
        if max(r, g, b) < 70:
            dark += 1
    total = crop.width * crop.height
    return {
        "roiPx": [crop.width, crop.height],
        "redSurfaceFraction": round(red / total, 6),
        "darkPatternFraction": round(dark / total, 6),
        "visiblePatternContrast": round((red + dark) / total, 6),
    }


def make_comparison() -> None:
    canvas = Image.new("RGB", (1800, 1050), (24, 28, 35))
    source = ImageOps.contain(Image.open(SOURCE).convert("RGB"), (780, 880))
    candidate = ImageOps.contain(Image.open(FRONT).convert("RGB"), (780, 880))
    canvas.paste(source, (60 + (780 - source.width) // 2, 120))
    canvas.paste(candidate, (960 + (780 - candidate.width) // 2, 120))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=28)
    small = ImageFont.load_default(size=19)
    draw.text((60, 38), "SOURCE · WHITE-BALANCE AUDIT INPUT", fill=(238, 240, 245), font=font)
    draw.text((960, 38), "BLENDER · NEUTRAL FRONT · REV 5", fill=(238, 240, 245), font=font)
    draw.text((60, 82), "Deep blood red; adjacent steel is the neutral reference.", fill=(180, 188, 200), font=small)
    draw.text((960, 82), "No emission · exposure 0 EV · Gate 07 diagnostic only.", fill=(180, 188, 200), font=small)
    canvas.save(ROOT / "blood-red-source-comparison.png")


def main() -> None:
    material = json.loads(MATERIAL_REPORT.read_text(encoding="utf-8"))
    color = json.loads(COLOR_REPORT.read_text(encoding="utf-8"))
    artwork = json.loads(ARTWORK_CONFIG.read_text(encoding="utf-8"))
    derivation = json.loads(DERIVATION_REPORT.read_text(encoding="utf-8"))
    supplemental = json.loads(SUPPLEMENTAL_CONFIG.read_text(encoding="utf-8"))
    make_comparison()
    front = red_metrics(Image.open(FRONT))
    neutral_highlight = highlight_metrics(Image.open(NEUTRAL))
    second_highlight = highlight_metrics(Image.open(SECOND_LIGHT))
    side = side_reflection_metrics(Image.open(SIDE))
    lower = lower_pattern_metrics(Image.open(OPEN))
    target_hue = color["correctedHsv"]["hueSignedMedianDegrees"]
    checks = {
        "bloodRedTargetDistance": abs(front["signedHueMedianDegrees"] - target_hue) <= 14,
        "pinkSuppressed": front["pinkFraction"] <= 0.04,
        "bloodRedDominant": front["bloodRedFraction"] >= 0.82,
        "noMeaningfulClipping": front["clippingAbove250Fraction"] <= 0.01
        and front["hard255Fraction"] <= 0.002,
        "noEmission": material["forbiddenLightingAndShaderTricks"]["pass"],
        "secondLightShowsCrystalResponse": second_highlight["above220Fraction"]
        > neutral_highlight["above220Fraction"],
        "sideReflectionVisible": side["maximumReflectionSpanFraction"] >= 0.16
        and side["metalCrystalBoundaryRowsDetected"] >= 2,
        "lowerPatternVisible": lower["redSurfaceFraction"] >= 0.08
        and lower["darkPatternFraction"] >= 0.08,
        "editableSlotsIndependent": artwork["slots"]["Artwork_Upper"]["maskSha256"]
        != artwork["slots"]["Artwork_Lower"]["maskSha256"],
        "lowerOcclusionDeclared": artwork["slots"]["Artwork_Lower"]["occludedOrReconstructed"],
        "sourceClassesDistinct": derivation["sourceBoundaryClasses"] == [
            "chrome-hearts-style-reconstructed",
            "directly-traced-exact-product",
            "occluded-incomplete",
        ],
        "exactProductFirst": derivation["exactProductFirst"],
        "reconstructionOnlyInsideOcclusion": derivation["reconstructionSubsetOfUnknown"],
        "directAndReconstructionDisjoint": derivation["directAndReconstructedDisjoint"],
        "supplementalOfficialAndSeparate": derivation["supplementalSourcesOfficialAndSeparate"]
        and all(source["notExactProductEvidence"] for source in supplemental["sources"])
        and all(source["origin"] == "external-primary-official" for source in supplemental["sources"]),
        "regionConfidenceExplained": {
            region["id"]: region["confidence"]
            for slot in artwork["slots"].values()
            for region in slot["regions"]
        } == {
            "upper-direct-exact-product": "high",
            "lower-direct-exact-product": "medium",
            "lower-occluded-incomplete": "none-for-exact-detail",
            "lower-chrome-hearts-style-reconstructed": "low",
        },
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 5,
        "target": {
            "sourceHueSignedMedianDegrees": target_hue,
            "sourceCorrectedSrgbRange": color["correctedBloodRedSrgb"],
            "shaderTargetLinearRgb": color["shaderTargetLinearRgb"],
        },
        "frontBloodRed": front,
        "crystalHighlight": {
            "neutral": neutral_highlight,
            "secondDiagnosticLight": second_highlight,
        },
        "sideReflection": side,
        "lowerArtwork": lower,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 5 image/artwork validation failed.")


if __name__ == "__main__":
    main()
