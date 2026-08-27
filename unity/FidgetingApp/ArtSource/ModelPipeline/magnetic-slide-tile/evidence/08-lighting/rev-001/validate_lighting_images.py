#!/usr/bin/env python3
"""Validate Gate 08 lighting views, passes, color, clipping, and seams."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
LIGHTING = ROOT / "lighting-validation.json"
OUTPUT = ROOT / "image-lighting-validation.json"
BEAUTY_VIEWS = {
    "hero": ("hero.png", (470, 400, 1120, 900)),
    "leftOblique": ("left-oblique.png", (350, 250, 1100, 850)),
    "rightOblique": ("right-oblique.png", (350, 250, 1100, 850)),
    "low": ("low-angle.png", (350, 350, 1100, 780)),
    "beauty": ("pass-beauty.png", (400, 400, 1250, 1000)),
    "openSide": ("open-side-reflection.png", (150, 300, 1350, 1000)),
}


def silver_metrics(path: Path, roi: tuple[int, int, int, int]) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    x1, y1, x2, y2 = roi
    rgb = image[y1:y2, x1:x2]
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    selected = rgb[(chroma <= 15) & (luma >= 145) & (luma <= 248)]
    lab = cv2.cvtColor(selected.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float64)
    l_star = lab[:, 0] * 100 / 255
    a_star = lab[:, 1] - 128
    b_star = lab[:, 2] - 128
    c_star = np.sqrt(a_star ** 2 + b_star ** 2)
    return {
        "roiPx": list(roi),
        "neutralHighlightSamples": int(len(selected)),
        "medianLStar": round(float(np.median(l_star)), 6),
        "p90LStar": round(float(np.percentile(l_star, 90)), 6),
        "medianAStar": round(float(np.median(a_star)), 6),
        "medianBStar": round(float(np.median(b_star)), 6),
        "medianCStar": round(float(np.median(c_star)), 6),
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
    if not selected:
        return {"selectedPixels": 0, "signedHueMedianDegrees": None, "pinkFraction": None, "bloodRedFraction": None}
    return {
        "selectedPixels": len(selected),
        "signedHueMedianDegrees": round(float(np.median([item[0] for item in selected])), 6),
        "pinkFraction": round(float(np.mean([-65 <= item[0] < -20 for item in selected])), 8),
        "bloodRedFraction": round(float(np.mean([-20 <= item[0] <= 15 for item in selected])), 8),
    }


def structure_metrics(path: Path, roi: tuple[int, int, int, int]) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    x1, y1, x2, y2 = roi
    gray = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_RGB2GRAY)
    return {
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 48, 144))),
        "darkPixelFraction": round(float(np.mean(gray <= 36)), 8),
    }


def pass_metrics(path: Path) -> dict:
    rgb = np.asarray(Image.open(path).convert("RGB"))
    roi = rgb[300:900, 300:1150]
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    return {
        "channelStd": [round(float(value), 6) for value in roi.reshape(-1, 3).std(axis=0)],
        "medianChannelChroma": round(float(np.median(roi.max(axis=2) - roi.min(axis=2))), 6),
        "grayP05": round(float(np.percentile(gray, 5)), 6),
        "grayP95": round(float(np.percentile(gray, 95)), 6),
        "grayRangeP05P95": round(float(np.percentile(gray, 95) - np.percentile(gray, 5)), 6),
    }


def difference_metric(left: Path, right: Path) -> float:
    a = np.asarray(Image.open(left).convert("RGB").resize((320, 240))).astype(np.float64)
    b = np.asarray(Image.open(right).convert("RGB").resize((320, 240))).astype(np.float64)
    return round(float(np.mean(np.abs(a - b))), 6)


def make_board(entries: list[tuple[str, Path]], output: str, title_text: str) -> None:
    canvas = Image.new("RGB", (2200, 1500), (18, 22, 28))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=22)
    draw.text((55, 38), title_text, fill=(244, 246, 250), font=title)
    positions = [(55, 115), (1100, 115), (55, 810), (1100, 810)]
    for (name, path), position in zip(entries, positions):
        image = ImageOps.contain(Image.open(path).convert("RGB"), (1000, 610))
        frame = Image.new("RGB", (1000, 610), (35, 40, 48))
        frame.paste(image, ((1000 - image.width) // 2, (610 - image.height) // 2))
        canvas.paste(frame, position)
        draw.text((position[0], position[1] + 620), name, fill=(204, 212, 224), font=label)
    canvas.save(ROOT / output)


def main() -> None:
    lighting = json.loads(LIGHTING.read_text(encoding="utf-8"))
    view_metrics = {}
    for name, (filename, roi) in BEAUTY_VIEWS.items():
        path = ROOT / filename
        view_metrics[name] = {
            "silver": silver_metrics(path, roi),
            "bloodRed": red_metrics(path),
            "structure": structure_metrics(path, roi),
        }
    passes = {
        name: pass_metrics(ROOT / filename)
        for name, filename in {
            "clay": "pass-clay.png",
            "normal": "pass-normal.png",
            "depth": "pass-depth.png",
            "roughness": "pass-roughness.png",
        }.items()
    }
    view_differences = {
        "leftVsRight": difference_metric(ROOT / "left-oblique.png", ROOT / "right-oblique.png"),
        "heroVsLow": difference_metric(ROOT / "hero.png", ROOT / "low-angle.png"),
    }
    make_board(
        [
            ("AUTHORED HERO", ROOT / "hero.png"),
            ("LEFT OBLIQUE", ROOT / "left-oblique.png"),
            ("RIGHT OBLIQUE", ROOT / "right-oblique.png"),
            ("LOW ANGLE", ROOT / "low-angle.png"),
        ],
        "lighting-view-board.png",
        "GATE 08 REV 1 · CONTROLLED LIGHTING VIEWS",
    )
    make_board(
        [
            ("BEAUTY", ROOT / "pass-beauty.png"),
            ("CLAY", ROOT / "pass-clay.png"),
            ("NORMAL", ROOT / "pass-normal.png"),
            ("DEPTH", ROOT / "pass-depth.png"),
        ],
        "lighting-pass-board.png",
        "GATE 08 REV 1 · BEAUTY / CLAY / NORMAL / DEPTH",
    )
    required_beauty = ["hero", "leftOblique", "rightOblique", "beauty"]
    checks = {
        "lightingBuilderPasses": lighting["pass"],
        "silverNeutralAndBright": all(
            view_metrics[name]["silver"]["neutralHighlightSamples"] >= 1000
            and view_metrics[name]["silver"]["medianLStar"] >= 70
            and view_metrics[name]["silver"]["medianCStar"] <= 4
            and view_metrics[name]["silver"]["medianBStar"] >= -1
            for name in ["hero", "leftOblique", "rightOblique", "low", "beauty"]
        ),
        "clippingControlled": all(
            metrics["silver"]["wholeImageClipAbove250Fraction"] <= 0.001
            for metrics in view_metrics.values()
        ),
        "bloodRedNotPink": all(
            view_metrics[name]["bloodRed"]["selectedPixels"] >= 30000
            and view_metrics[name]["bloodRed"]["pinkFraction"] <= 0.02
            and view_metrics[name]["bloodRed"]["bloodRedFraction"] >= 0.90
            for name in required_beauty
        ),
        "motifAndSeamsRemainLegible": all(
            view_metrics[name]["structure"]["laplacianVariance"] >= 35
            and view_metrics[name]["structure"]["cannyEdgePixels"] >= 2000
            for name in ["hero", "leftOblique", "rightOblique", "beauty", "openSide"]
        ),
        "distinctAuthoredViews": view_differences["leftVsRight"] >= 4 and view_differences["heroVsLow"] >= 8,
        "clayPassValid": passes["clay"]["medianChannelChroma"] <= 4 and passes["clay"]["grayRangeP05P95"] >= 45,
        "normalPassValid": min(passes["normal"]["channelStd"]) >= 12 and passes["normal"]["medianChannelChroma"] >= 20,
        "depthPassValid": passes["depth"]["medianChannelChroma"] <= 1 and passes["depth"]["grayRangeP05P95"] >= 90,
        "roughnessPassValid": passes["roughness"]["medianChannelChroma"] <= 1 and passes["roughness"]["grayRangeP05P95"] >= 35,
        "shippingMaterialEmissionZero": lighting["materials"]["shippingEmissionZero"],
        "geometryAndMaterialPreserved": lighting["geometry"]["unchanged"]
        and lighting["materials"]["assignmentsRestored"]
        and lighting["materials"]["fullBlackPerimeterPreserved"],
        "unityReflectionSpecifiedOnly": lighting["unityReflectionPlan"]["deliveryState"] == "specified-only-not-integrated",
        "gate08Only": not any(lighting["scope"].values()),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "views": view_metrics,
        "passes": passes,
        "viewDifferences": view_differences,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 image lighting validation failed.")


if __name__ == "__main__":
    main()
