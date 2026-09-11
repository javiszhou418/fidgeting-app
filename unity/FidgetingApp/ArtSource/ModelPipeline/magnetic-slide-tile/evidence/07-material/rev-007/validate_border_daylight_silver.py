#!/usr/bin/env python3
"""Validate Gate 07 rev 7 border, D65 silver, blood red, and scope."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
REV6 = ROOT.parent / "rev-006"
MATERIAL = ROOT / "material-validation.json"
BORDER_REPORT = ROOT / "artwork-border-validation.json"
REV6_BORDER = ROOT / "rev6-border-same-camera.png"
WIDE_BORDER = ROOT / "wide-border-same-camera.png"
REV6_SILVER_ORIGINAL = REV6 / "pure-silver-edge-same-camera.png"
REV6_SILVER_NEUTRAL = ROOT / "rev6-silver-neutral-studio-same-camera.png"
REV7_SILVER_NEUTRAL = ROOT / "daylight-neutral-silver-neutral-studio-same-camera.png"
D65_HERO = ROOT / "outdoor-d65-hero-neutral-card.png"
D65_SIDE = ROOT / "outdoor-d65-silver-side-direct.png"
BLOOD_RED = ROOT / "blood-red-closeup.png"
OPEN = ROOT / "open-slide-lower-artwork.png"
OUTPUT = ROOT / "image-material-validation.json"


def lab_metrics(path: Path, roi: tuple[int, int, int, int], chroma_limit: int = 18) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    x1, y1, x2, y2 = roi
    rgb = image[y1:y2, x1:x2]
    channel_chroma = rgb.max(axis=2) - rgb.min(axis=2)
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    selected = rgb[(channel_chroma <= chroma_limit) & (luma >= 110) & (luma <= 248)]
    lab = cv2.cvtColor(selected.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float64)
    l_star = lab[:, 0] * 100 / 255
    a_star = lab[:, 1] - 128
    b_star = lab[:, 2] - 128
    c_star = np.sqrt(a_star ** 2 + b_star ** 2)
    return {
        "roiPx": list(roi),
        "neutralSamples": int(len(selected)),
        "medianRgb": [round(float(value), 4) for value in np.median(selected, axis=0)],
        "medianLStar": round(float(np.median(l_star)), 6),
        "medianAStar": round(float(np.median(a_star)), 6),
        "medianBStar": round(float(np.median(b_star)), 6),
        "medianCStar": round(float(np.median(c_star)), 6),
        "p90LStar": round(float(np.percentile(l_star, 90)), 6),
        "blueBiasBelowMinus2Fraction": round(float(np.mean(b_star < -2)), 8),
        "roiClipAbove250Fraction": round(float(np.mean(rgb.max(axis=2) >= 250)), 8),
    }


def studio_metrics(path: Path, chroma_limit: int) -> dict:
    return lab_metrics(path, (100, 650, 1000, 980), chroma_limit)


def border_render_metrics(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB"))[280:740, 120:780]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    red = (rgb[..., 0] > rgb[..., 1] * 1.3) & (rgb[..., 0] > rgb[..., 2] * 1.15) & (rgb[..., 0] > 40)
    return {
        "roiPx": [120, 280, 780, 740],
        "darkFraction": round(float(np.mean(gray < 30)), 8),
        "redFraction": round(float(np.mean(red)), 8),
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 64, 192))),
    }


def mask_metrics(path: Path) -> dict:
    gray = np.asarray(Image.open(path).convert("L"))
    return {
        "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 64, 192))),
        "intermediatePixelFraction": round(float(np.mean((gray > 0) & (gray < 255))), 8),
    }


def red_metrics(path: Path) -> dict:
    pixels = np.asarray(Image.open(path).convert("RGB")).reshape(-1, 3)
    selected = []
    for r, g, b in pixels:
        hue, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        signed_hue = ((hue * 360 + 180) % 360) - 180
        if r > 35 and r > g * 1.35 and r > b * 1.18 and saturation > 0.42:
            selected.append((signed_hue, saturation, value))
    if not selected:
        raise RuntimeError("No blood-red pixels detected.")
    return {
        "selectedPixels": len(selected),
        "signedHueMedianDegrees": round(float(np.median([item[0] for item in selected])), 6),
        "bloodRedFraction": round(float(np.mean([-20 <= item[0] <= 15 and item[2] <= 0.92 for item in selected])), 8),
        "pinkFraction": round(float(np.mean([-65 <= item[0] < -20 for item in selected])), 8),
        "wholeImageClipAbove250Fraction": round(float(np.mean(pixels.max(axis=1) >= 250)), 8),
    }


def open_metrics() -> dict:
    rgb = np.asarray(Image.open(OPEN).convert("RGB"))
    crop = rgb[620:1180, 70:680]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    return {
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 64, 192))),
    }


def reference_card_metrics() -> dict:
    rgb = np.asarray(Image.open(D65_HERO).convert("RGB"))
    boxes = {
        "white80": rgb[170:340, 270:380],
        "gray18": rgb[190:340, 405:500],
        "black": rgb[220:360, 550:640],
    }
    return {
        name: round(float(np.mean(0.2126 * box[..., 0] + 0.7152 * box[..., 1] + 0.0722 * box[..., 2])), 6)
        for name, box in boxes.items()
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
    material = json.loads(MATERIAL.read_text(encoding="utf-8"))
    border_report = json.loads(BORDER_REPORT.read_text(encoding="utf-8"))
    rev6_border = border_render_metrics(REV6_BORDER)
    wide_border = border_render_metrics(WIDE_BORDER)
    rev6_blue = studio_metrics(REV6_SILVER_ORIGINAL, 30)
    rev6_neutral = studio_metrics(REV6_SILVER_NEUTRAL, 18)
    rev7_neutral = studio_metrics(REV7_SILVER_NEUTRAL, 18)
    d65_hero = lab_metrics(D65_HERO, (470, 470, 1120, 790))
    d65_side = lab_metrics(D65_SIDE, (20, 350, 1000, 620))
    blood_red = red_metrics(BLOOD_RED)
    open_lower = open_metrics()
    cards = reference_card_metrics()
    upper_mask = mask_metrics(ROOT / "artwork-upper-mask.png")
    lower_mask = mask_metrics(ROOT / "artwork-lower-mask.png")

    comparison_board(
        REV6_BORDER,
        WIDE_BORDER,
        "REV 6 · INSET BLACK BORDER",
        "REV 7 · FULL OUTER TOP-FACE PERIMETER",
        "Same camera, geometry, blood-red substrate, clean motif, neutral studio, and exposure.",
        "black-border-comparison-same-camera.png",
    )
    comparison_board(
        REV6_SILVER_NEUTRAL,
        REV7_SILVER_NEUTRAL,
        "REV 6 SILVER SHADER · NEUTRAL STUDIO",
        "REV 7 DAYLIGHT-NEUTRAL SILVER · NEUTRAL STUDIO",
        "Same camera and neutral environment isolates the physically plausible shader adjustment.",
        "neutral-studio-silver-comparison.png",
    )
    comparison_board(
        REV6_SILVER_ORIGINAL,
        REV7_SILVER_NEUTRAL,
        "REV 6 · BLUE-BIASED STUDIO RESPONSE",
        "REV 7 · NEUTRAL STUDIO RESPONSE",
        "Same camera. Diagnosis: blue world tint dominated mirror-metal appearance; rev 7 removes that tint.",
        "silver-environment-diagnosis-same-camera.png",
    )

    silver_zone = material["materialZones"]["polished-pure-silver-visual-target-exterior"]
    border = material["artworkLayers"]["topPerimeterBorder"]
    checks = {
        "borderPreparationPasses": border_report["pass"],
        "borderReachesOuterPerimeter": border["outerPerimeterInsetPx"] == 0,
        "borderWidthExposed": border["widthPx"] == 64 and border["widthFractionMinorAxis"] > 0.10,
        "renderedBorderWider": wide_border["darkFraction"] >= rev6_border["darkFraction"] + 0.04,
        "cleanMotifIdentityPreserved": upper_mask["sha256"] == lower_mask["sha256"] == material["artworkLayers"]["lineage"]["sourceSha256"],
        "motifSharpnessIdentityPreserved": upper_mask == lower_mask,
        "independentArtworkSlots": material["artworkLayers"]["independentSwap"],
        "rev6BlueBiasDiagnosed": rev6_blue["blueBiasBelowMinus2Fraction"] >= 0.10,
        "neutralStudioBlueBiasRemoved": rev7_neutral["medianBStar"] >= -1 and rev7_neutral["medianCStar"] <= 4,
        "d65HeroBrightNeutralSilver": d65_hero["medianLStar"] >= 70 and d65_hero["medianCStar"] <= 4 and d65_hero["medianBStar"] >= -1,
        "d65SideBrightNeutralSilver": d65_side["medianLStar"] >= 65
        and d65_side["p90LStar"] >= 75
        and d65_side["medianCStar"] <= 4
        and d65_side["medianBStar"] >= -1,
        "d65HighlightsNotClipped": d65_hero["roiClipAbove250Fraction"] <= 0.001 and d65_side["roiClipAbove250Fraction"] <= 0.001,
        "referenceCardsOrdered": cards["white80"] > cards["gray18"] > cards["black"],
        "bloodRedTarget": -20 <= blood_red["signedHueMedianDegrees"] <= 15 and blood_red["pinkFraction"] <= 0.04 and blood_red["bloodRedFraction"] >= 0.82,
        "bloodRedClippingControlled": blood_red["wholeImageClipAbove250Fraction"] <= 0.01,
        "openLowerArtworkLegible": open_lower["laplacianVariance"] >= 70 and open_lower["cannyEdgePixels"] >= 3000,
        "physicallyPlausibleSilver": silver_zone["metallic"] == 1.0
        and 0.02 <= silver_zone["roughness"] <= 0.08
        and silver_zone["baseColor"][2] <= silver_zone["baseColor"][0]
        and silver_zone["productionMaterialClaim"] is False,
        "noEmission": material["forbiddenLightingAndShaderTricks"]["pass"],
        "geometryDigestUnchanged": material["geometryPreservation"]["pass"],
        "mechanismScopeUnchanged": material["mechanismDecisionMetadata"]["detentCount"] == 30
        and material["mechanismDecisionMetadata"]["deliveryState"] == "specified-only-runtime-and-hardware-validation-pending",
        "gate07Only": not any(material["scope"].values()),
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "borderComparison": {"rev6": rev6_border, "rev7": wide_border},
        "motifMasks": {"upper": upper_mask, "lower": lower_mask},
        "silverDiagnosis": {
            "rev6OriginalBlueStudio": rev6_blue,
            "rev6ShaderNeutralStudio": rev6_neutral,
            "rev7ShaderNeutralStudio": rev7_neutral,
            "cause": "Rev 6 mirror metal reflected a blue-tinted world. Rev 7 uses a neutral studio world and a D65-balanced daylight diagnostic.",
        },
        "d65Silver": {"hero": d65_hero, "sideDirect": d65_side},
        "d65ReferenceCards": cards,
        "bloodRed": blood_red,
        "openLowerArtwork": open_lower,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 7 image/material validation failed.")


if __name__ == "__main__":
    main()
