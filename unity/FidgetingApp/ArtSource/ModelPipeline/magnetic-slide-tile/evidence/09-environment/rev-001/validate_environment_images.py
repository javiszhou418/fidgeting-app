#!/usr/bin/env python3
"""Validate matched environment isolation, color, reflection, and clipping."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
GATE08_BEAUTY = ROOT.parents[1] / "08-lighting/rev-001/pass-beauty.png"
ENVIRONMENT = ROOT / "environment-validation.json"
OUTPUT = ROOT / "image-environment-validation.json"
IMAGES = {
    "neutral": ("neutral-environment.png", (400, 400, 1250, 1000)),
    "shipping": ("shipping-environment.png", (400, 400, 1250, 1000)),
    "neutralSide": ("neutral-side-reflection.png", (350, 250, 1100, 850)),
    "shippingSide": ("shipping-side-reflection.png", (350, 250, 1100, 850)),
}


def lab_metrics(path: Path, roi: tuple[int, int, int, int]) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    x1, y1, x2, y2 = roi
    rgb = image[y1:y2, x1:x2]
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]

    def sample(min_luma: int) -> dict:
        selected = rgb[(chroma <= 15) & (luma >= min_luma) & (luma <= 248)]
        lab = cv2.cvtColor(selected.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float64)
        l_star = lab[:, 0] * 100 / 255
        a_star = lab[:, 1] - 128
        b_star = lab[:, 2] - 128
        c_star = np.sqrt(a_star ** 2 + b_star ** 2)
        return {
            "samples": int(len(selected)),
            "medianLStar": round(float(np.median(l_star)), 6),
            "p90LStar": round(float(np.percentile(l_star, 90)), 6),
            "medianAStar": round(float(np.median(a_star)), 6),
            "medianBStar": round(float(np.median(b_star)), 6),
            "medianCStar": round(float(np.median(c_star)), 6),
        }

    return {
        "roiPx": list(roi),
        "neutralSilverBody": sample(145),
        "brightSilverReflection": sample(170),
        "wholeImageClipAbove250Fraction": round(float(np.mean(image.max(axis=2) >= 250)), 8),
    }


def red_metrics(path: Path) -> dict:
    pixels = np.asarray(Image.open(path).convert("RGB")).reshape(-1, 3)
    selected = []
    for r, g, b in pixels:
        hue, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        signed_hue = ((hue * 360 + 180) % 360) - 180
        if r > 35 and r > g * 1.30 and r > b * 1.15 and saturation > 0.35:
            selected.append((signed_hue, saturation, value))
    return {
        "selectedPixels": len(selected),
        "signedHueMedianDegrees": round(float(np.median([item[0] for item in selected])), 6),
        "pinkFraction": round(float(np.mean([-65 <= item[0] < -20 for item in selected])), 8),
        "bloodRedFraction": round(float(np.mean([-20 <= item[0] <= 15 for item in selected])), 8),
    }


def motif_metrics(path: Path, roi: tuple[int, int, int, int]) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    x1, y1, x2, y2 = roi
    rgb = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    red_mask = (rgb[..., 0] >= 60) & (rgb[..., 0] >= rgb[..., 1] * 1.30) & (rgb[..., 0] >= rgb[..., 2] * 1.15)
    dark_mask = gray <= 42
    red_luma = float(np.median(gray[red_mask]))
    dark_luma = float(np.median(gray[dark_mask]))
    return {
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 48, 144))),
        "redMedianLuma": round(red_luma, 6),
        "darkMedianLuma": round(dark_luma, 6),
        "redDarkContrast": round(red_luma - dark_luma, 6),
        "redDarkContrastRatio": round((red_luma + 0.05) / (dark_luma + 0.05), 6),
    }


def image_difference(left: Path, right: Path, roi: tuple[int, int, int, int] | None = None) -> dict:
    a = np.asarray(Image.open(left).convert("RGB")).astype(np.int16)
    b = np.asarray(Image.open(right).convert("RGB")).astype(np.int16)
    if roi:
        x1, y1, x2, y2 = roi
        a = a[y1:y2, x1:x2]
        b = b[y1:y2, x1:x2]
    delta = np.abs(a - b)
    return {
        "meanAbsoluteChannelDelta": round(float(np.mean(delta)), 6),
        "p90AbsoluteChannelDelta": round(float(np.percentile(delta, 90)), 6),
        "fractionPixelsMaxDeltaAbove12": round(float(np.mean(delta.max(axis=2) > 12)), 8),
        "maxChannelDelta": int(delta.max()),
    }


def make_comparison_board(neutral: Path, shipping: Path) -> None:
    canvas = Image.new("RGB", (2400, 980), (15, 18, 24))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=24)
    draw.text((55, 32), "GATE 09 REV 1 · MATCHED CAMERA ENVIRONMENT ISOLATION", fill=(245, 247, 250), font=title)
    for name, path, x in [
        ("NEUTRAL CONTROL", neutral, 55),
        ("SHIPPING-LIKE ADAPTIVE PREVIEW", shipping, 1225),
    ]:
        image = ImageOps.contain(Image.open(path).convert("RGB"), (1120, 760))
        frame = Image.new("RGB", (1120, 760), (28, 33, 41))
        frame.paste(image, ((1120 - image.width) // 2, (760 - image.height) // 2))
        canvas.paste(frame, (x, 105))
        draw.text((x, 880), name, fill=(214, 221, 232), font=label)
    draw.text(
        (55, 928),
        "ONLY WORLD / GROUND / ENVIRONMENT REFLECTION INPUTS CHANGE · CAMERA / LIGHT / MODEL / MATERIAL / POSE / EV MATCH",
        fill=(156, 169, 187),
        font=label,
    )
    canvas.save(ROOT / "environment-comparison-board.png")


def make_reflection_board(neutral: Path, shipping: Path) -> None:
    crop = (280, 260, 1160, 820)
    canvas = Image.new("RGB", (2200, 790), (15, 18, 24))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=32)
    label = ImageFont.load_default(size=22)
    draw.text((45, 28), "SILVER REFLECTION CLOSEUP · SAME APPROVED RIGHT-OBLIQUE CAMERA", fill=(245, 247, 250), font=title)
    for name, path, x in [
        ("NEUTRAL WORLD RESPONSE", neutral, 45),
        ("ADAPTIVE SKYBOX-LIKE RESPONSE", shipping, 1115),
    ]:
        image = ImageOps.fit(Image.open(path).convert("RGB").crop(crop), (1040, 610))
        canvas.paste(image, (x, 95))
        draw.text((x, 720), name, fill=(214, 221, 232), font=label)
    draw.text((45, 758), "Blender reflection preview only · no Unity Reflection Probe integration", fill=(156, 169, 187), font=label)
    canvas.save(ROOT / "reflection-closeup-comparison.png")


def make_difference_map(neutral: Path, shipping: Path) -> None:
    a = np.asarray(Image.open(neutral).convert("RGB")).astype(np.int16)
    b = np.asarray(Image.open(shipping).convert("RGB")).astype(np.int16)
    delta = np.abs(a - b).mean(axis=2)
    normalized = np.clip(delta * 4.0, 0, 255).astype(np.uint8)
    heat = cv2.applyColorMap(normalized, cv2.COLORMAP_INFERNO)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    Image.fromarray(heat).save(ROOT / "environment-difference-map.png")


def main() -> None:
    environment = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))
    metrics = {}
    for name, (filename, roi) in IMAGES.items():
        path = ROOT / filename
        metrics[name] = {
            "silver": lab_metrics(path, roi),
            "bloodRed": red_metrics(path),
            "motif": motif_metrics(path, roi),
        }
    neutral_path = ROOT / "neutral-environment.png"
    shipping_path = ROOT / "shipping-environment.png"
    neutral_side = ROOT / "neutral-side-reflection.png"
    shipping_side = ROOT / "shipping-side-reflection.png"
    differences = {
        "fullMatchedCamera": image_difference(neutral_path, shipping_path),
        "sideReflectionRoi": image_difference(neutral_side, shipping_side, (350, 250, 1100, 850)),
        "neutralBaselineVsGate08Beauty": image_difference(GATE08_BEAUTY, neutral_path),
    }
    make_comparison_board(neutral_path, shipping_path)
    make_reflection_board(neutral_side, shipping_side)
    make_difference_map(neutral_path, shipping_path)
    checks = {
        "environmentBuilderPasses": environment["pass"],
        "neutralBaselinePixelIdentical": differences["neutralBaselineVsGate08Beauty"]["maxChannelDelta"] == 0,
        "onlyEnvironmentInputsDiffer": environment["invariants"]["geometryUnchanged"]
        and environment["invariants"]["camerasUnchanged"]
        and environment["invariants"]["lightsUnchanged"]
        and environment["invariants"]["materialsUnchanged"]
        and environment["invariants"]["materialAssignmentsUnchanged"],
        "shippingSilverNeutral": metrics["shipping"]["silver"]["neutralSilverBody"]["medianLStar"] >= 58
        and metrics["shipping"]["silver"]["neutralSilverBody"]["medianCStar"] <= 4
        and metrics["shipping"]["silver"]["neutralSilverBody"]["medianBStar"] >= -1,
        "shippingSilverReflectionBright": metrics["shipping"]["silver"]["brightSilverReflection"]["samples"] >= 1000
        and metrics["shipping"]["silver"]["brightSilverReflection"]["medianLStar"] >= 80
        and metrics["shippingSide"]["silver"]["brightSilverReflection"]["samples"] >= 1000
        and metrics["shippingSide"]["silver"]["brightSilverReflection"]["medianLStar"] >= 78,
        "clippingControlled": all(
            item["silver"]["wholeImageClipAbove250Fraction"] <= 0.001
            for item in metrics.values()
        ),
        "bloodRedPreserved": metrics["shipping"]["bloodRed"]["selectedPixels"] >= 50000
        and -20 <= metrics["shipping"]["bloodRed"]["signedHueMedianDegrees"] <= 15
        and metrics["shipping"]["bloodRed"]["pinkFraction"] <= 0.01
        and metrics["shipping"]["bloodRed"]["bloodRedFraction"] >= 0.95,
        "motifContrastPreserved": metrics["shipping"]["motif"]["redDarkContrastRatio"] >= 1.60
        and metrics["shipping"]["motif"]["laplacianVariance"] >= 150
        and metrics["shipping"]["motif"]["cannyEdgePixels"] >= 6000,
        "environmentDifferenceVisible": differences["fullMatchedCamera"]["meanAbsoluteChannelDelta"] >= 20
        and differences["fullMatchedCamera"]["fractionPixelsMaxDeltaAbove12"] >= 0.80,
        "silverReflectionDifferenceVisible": differences["sideReflectionRoi"]["meanAbsoluteChannelDelta"] >= 20
        and differences["sideReflectionRoi"]["fractionPixelsMaxDeltaAbove12"] >= 0.80,
        "shippingEmissionZero": environment["invariants"]["shippingEmissionZero"],
        "optimizationDecisionPreserved": environment["optimizationDecision"]["triangles"] == 4096
        and environment["optimizationDecision"]["decisionState"] == "locked-user-approved",
        "gate09Only": not any(environment["scope"].values()),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 1,
        "metrics": metrics,
        "differences": differences,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 image environment validation failed.")


if __name__ == "__main__":
    main()
