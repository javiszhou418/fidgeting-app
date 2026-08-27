#!/usr/bin/env python3
"""Validate Gate 09 rev 2 open-pose visibility, color, and reflections."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SCENE_REPORT = ROOT / "open-environment-validation.json"
OUTPUT = ROOT / "open-image-validation.json"
LOWER_TOP_ROI = (150, 550, 850, 1300)


def array(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def red_mask(rgb: np.ndarray) -> np.ndarray:
    return (
        (rgb[..., 0] > 45)
        & (rgb[..., 0] > rgb[..., 1] * 1.30)
        & (rgb[..., 0] > rgb[..., 2] * 1.15)
    )


def red_metrics(path: Path) -> dict:
    rgb = array(path)
    pixels = rgb.reshape(-1, 3)
    hues = []
    for r, g, b in pixels:
        hue, saturation, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        signed = ((hue * 360 + 180) % 360) - 180
        if r > 45 and r > g * 1.30 and r > b * 1.15 and saturation > 0.35:
            hues.append(signed)
    return {
        "selectedPixels": len(hues),
        "signedHueMedianDegrees": round(float(np.median(hues)), 6),
        "pinkFraction": round(float(np.mean([-65 <= hue < -20 for hue in hues])), 8),
        "bloodRedFraction": round(float(np.mean([-20 <= hue <= 15 for hue in hues])), 8),
    }


def silver_metrics(path: Path) -> dict:
    rgb = array(path)
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
            "medianAStar": round(float(np.median(a_star)), 6),
            "medianBStar": round(float(np.median(b_star)), 6),
            "medianCStar": round(float(np.median(c_star)), 6),
        }

    return {
        "silverBody": sample(140),
        "brightReflection": sample(170),
        "clipAbove250Fraction": round(float(np.mean(rgb.max(axis=2) >= 250)), 8),
    }


def difference(left: Path, right: Path) -> dict:
    a = array(left).astype(np.int16)
    b = array(right).astype(np.int16)
    delta = np.abs(a - b)
    return {
        "meanAbsoluteChannelDelta": round(float(np.mean(delta)), 6),
        "p90AbsoluteChannelDelta": round(float(np.percentile(delta, 90)), 6),
        "fractionPixelsMaxDeltaAbove12": round(float(np.mean(delta.max(axis=2) > 12)), 8),
        "maxChannelDelta": int(delta.max()),
    }


def lower_visibility(path: Path) -> dict:
    rgb = array(path)
    x1, y1, x2, y2 = LOWER_TOP_ROI
    crop = rgb[y1:y2, x1:x2]
    red = red_mask(crop)
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    dark = gray <= 35
    red_luma = float(np.median(gray[red]))
    dark_luma = float(np.median(gray[dark]))
    return {
        "roiPx": list(LOWER_TOP_ROI),
        "redArtworkPixels": int(np.count_nonzero(red)),
        "redMedianLuma": red_luma,
        "darkMedianLuma": dark_luma,
        "contrastRatio": round((red_luma + 0.05) / (dark_luma + 0.05), 6),
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 6),
        "cannyEdgePixels": int(np.count_nonzero(cv2.Canny(gray, 48, 144))),
    }


def paste_fit(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, width, height = box
    fitted = ImageOps.contain(image, (width, height))
    canvas.paste(fitted, (x + (width - fitted.width) // 2, y + (height - fitted.height) // 2))


def comparison_board() -> None:
    canvas = Image.new("RGB", (2400, 980), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=24)
    draw.text((50, 30), "GATE 09 REV 2 · OPEN +21 MM · MATCHED ENVIRONMENT PAIR", fill=(245, 247, 250), font=title)
    for name, filename, x in [
        ("NEUTRAL CONTROL", "open-neutral-hero.png", 45),
        ("SHIPPING-LIKE ENVIRONMENT", "open-shipping-hero.png", 1215),
    ]:
        paste_fit(canvas, Image.open(ROOT / filename).convert("RGB"), (x, 95, 1140, 760))
        draw.text((x, 875), name, fill=(214, 221, 232), font=label)
    draw.text((50, 925), "SAME CAMERA · SAME +21 MM POSE · 0° ROTATION · ONLY ENVIRONMENT INPUTS CHANGE", fill=(155, 169, 187), font=label)
    canvas.save(ROOT / "open-environment-comparison-board.png")


def style_board() -> None:
    canvas = Image.new("RGB", (2400, 1860), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=23)
    draw.text((50, 28), "SLIDE-OPEN REVIEW · BOTH BODIES AND LOWER ARTWORK VISIBLE", fill=(245, 247, 250), font=title)
    records = [
        ("SHIPPING OPEN HERO", "open-shipping-hero.png", 45, 95),
        ("AUTHORED OPEN OBLIQUE", "open-shipping-oblique.png", 1215, 95),
        ("OPEN NEAR-TOP", "open-shipping-top.png", 45, 930),
        ("SILVER / LAYER CLOSEUP", "open-shipping-layer-closeup.png", 1215, 930),
    ]
    for name, filename, x, y in records:
        paste_fit(canvas, Image.open(ROOT / filename).convert("RGB"), (x, y, 1140, 720))
        draw.text((x, y + 735), name, fill=(214, 221, 232), font=label)
    draw.text((50, 1810), "+Y 21.000 MM · ROTATION 0° · CLEAN LOWER PLANE · CONCEALED MECHANISM", fill=(155, 169, 187), font=label)
    canvas.save(ROOT / "open-style-review-board.png")


def reflection_board() -> None:
    canvas = Image.new("RGB", (2200, 850), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=32)
    label = ImageFont.load_default(size=22)
    draw.text((45, 25), "OPEN LAYER REFLECTION · SAME CAMERA AND POSE", fill=(245, 247, 250), font=title)
    for name, filename, x in [
        ("NEUTRAL", "open-neutral-layer-closeup.png", 40),
        ("SHIPPING-LIKE", "open-shipping-layer-closeup.png", 1110),
    ]:
        paste_fit(canvas, Image.open(ROOT / filename).convert("RGB"), (x, 85, 1045, 660))
        draw.text((x, 765), name, fill=(214, 221, 232), font=label)
    draw.text((45, 812), "Environment response crosses both silver side walls; Blender preview only.", fill=(155, 169, 187), font=label)
    canvas.save(ROOT / "open-reflection-closeup-board.png")


def sequence_board() -> None:
    canvas = Image.new("RGB", (2400, 630), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=32)
    label = ImageFont.load_default(size=21)
    draw.text((45, 24), "CLOSED TO OPEN · PURE +Y SLIDE · NO SPIN", fill=(245, 247, 250), font=title)
    for index, travel in enumerate([0, 7, 14, 21]):
        filename = f"sequence-{index:02d}-{travel:02d}mm.png"
        x = 30 + index * 595
        paste_fit(canvas, Image.open(ROOT / filename).convert("RGB"), (x, 80, 565, 450))
        draw.text((x, 545), f"{travel} MM · 0°", fill=(214, 221, 232), font=label)
        if index < 3:
            arrow_x = x + 570
            draw.line((arrow_x - 12, 302, arrow_x + 12, 302), fill=(204, 213, 226), width=3)
            draw.polygon(
                [(arrow_x + 12, 302), (arrow_x + 3, 295), (arrow_x + 3, 309)],
                fill=(204, 213, 226),
            )
    draw.text((45, 592), "Lower matrix stays fixed in all four frames.", fill=(155, 169, 187), font=label)
    canvas.save(ROOT / "closed-open-sequence-board.png")


def lower_board() -> None:
    source = Image.open(ROOT / "open-shipping-top.png").convert("RGB")
    crop = source.crop(LOWER_TOP_ROI)
    canvas = Image.new("RGB", (2100, 980), (14, 17, 23))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=32)
    label = ImageFont.load_default(size=22)
    draw.text((45, 25), "LOWER ARTWORK VISIBILITY · INDEPENDENT ARTWORK_LOWER SLOT", fill=(245, 247, 250), font=title)
    paste_fit(canvas, source, (35, 85, 990, 810))
    paste_fit(canvas, crop, (1075, 85, 990, 810))
    draw.rectangle((1075, 85, 2065, 895), outline=(185, 197, 214), width=3)
    draw.text((35, 915), "OPEN NEAR-TOP", fill=(214, 221, 232), font=label)
    draw.text((1075, 915), "EXPOSED LOWER MOTIF CROP", fill=(214, 221, 232), font=label)
    canvas.save(ROOT / "lower-artwork-visibility-board.png")


def main() -> None:
    scene = json.loads(SCENE_REPORT.read_text(encoding="utf-8"))
    shipping_hero = ROOT / "open-shipping-hero.png"
    shipping_oblique = ROOT / "open-shipping-oblique.png"
    shipping_top = ROOT / "open-shipping-top.png"
    shipping_layer = ROOT / "open-shipping-layer-closeup.png"
    metrics = {
        "shippingHero": {
            "silver": silver_metrics(shipping_hero),
            "bloodRed": red_metrics(shipping_hero),
        },
        "shippingOblique": {
            "silver": silver_metrics(shipping_oblique),
            "bloodRed": red_metrics(shipping_oblique),
        },
        "shippingTop": {
            "bloodRed": red_metrics(shipping_top),
            "lowerArtwork": lower_visibility(shipping_top),
            "clipAbove250Fraction": round(float(np.mean(array(shipping_top).max(axis=2) >= 250)), 8),
        },
        "shippingLayer": {
            "silver": silver_metrics(shipping_layer),
            "bloodRed": red_metrics(shipping_layer),
        },
    }
    closed_red = int(np.count_nonzero(red_mask(array(ROOT / "sequence-00-00mm.png"))))
    open_red = int(np.count_nonzero(red_mask(array(ROOT / "sequence-03-21mm.png"))))
    differences = {
        "neutralShippingOpenHero": difference(ROOT / "open-neutral-hero.png", shipping_hero),
        "neutralShippingLayer": difference(ROOT / "open-neutral-layer-closeup.png", shipping_layer),
        "closedToOpen": difference(ROOT / "sequence-00-00mm.png", ROOT / "sequence-03-21mm.png"),
    }
    comparison_board()
    style_board()
    reflection_board()
    sequence_board()
    lower_board()
    checks = {
        "sceneValidationPasses": scene["pass"],
        "exactOpenPose": scene["checks"]["exactOpenTravel"]
        and scene["checks"]["zeroRotation"]
        and scene["checks"]["fixedLowerMatrix"],
        "sameCameraNeutralShipping": scene["comparison"]["neutralShippingCamera"]["name"] == "M09R2_OpenHeroCamera"
        and scene["comparison"]["neutralShippingPose"] == {"travelMm": 21.0, "rotationDegrees": 0.0},
        "lowerPatternVisible": metrics["shippingTop"]["lowerArtwork"]["redArtworkPixels"] >= 70000
        and metrics["shippingTop"]["lowerArtwork"]["contrastRatio"] >= 1.55
        and metrics["shippingTop"]["lowerArtwork"]["laplacianVariance"] >= 150
        and metrics["shippingTop"]["lowerArtwork"]["cannyEdgePixels"] >= 15000,
        "openShowsMoreArtworkThanClosed": open_red >= closed_red * 1.20,
        "silverNeutral": metrics["shippingHero"]["silver"]["silverBody"]["medianLStar"] >= 58
        and metrics["shippingHero"]["silver"]["silverBody"]["medianCStar"] <= 4
        and metrics["shippingHero"]["silver"]["silverBody"]["medianBStar"] >= -1,
        "silverReflectionsBright": all(
            metrics[name]["silver"]["brightReflection"]["samples"] >= 1000
            and metrics[name]["silver"]["brightReflection"]["medianLStar"] >= 80
            for name in ["shippingHero", "shippingOblique", "shippingLayer"]
        ),
        "bloodRedNoPink": all(
            metrics[name]["bloodRed"]["selectedPixels"] >= 50000
            and -20 <= metrics[name]["bloodRed"]["signedHueMedianDegrees"] <= 15
            and metrics[name]["bloodRed"]["pinkFraction"] <= 0.01
            and metrics[name]["bloodRed"]["bloodRedFraction"] >= 0.95
            for name in ["shippingHero", "shippingOblique", "shippingTop", "shippingLayer"]
        ),
        "clippingControlled": all(
            metrics[name]["silver"]["clipAbove250Fraction"] <= 0.001
            for name in ["shippingHero", "shippingOblique", "shippingLayer"]
        ) and metrics["shippingTop"]["clipAbove250Fraction"] <= 0.001,
        "environmentReflectionVisible": differences["neutralShippingOpenHero"]["meanAbsoluteChannelDelta"] >= 20
        and differences["neutralShippingLayer"]["meanAbsoluteChannelDelta"] >= 20,
        "openDifferenceVisible": differences["closedToOpen"]["fractionPixelsMaxDeltaAbove12"] >= 0.10,
        "artworkSlotsIndependent": scene["checks"]["independentArtworkSlots"],
        "mechanismNotExposed": scene["checks"]["mechanismConcealed"],
        "shippingEmissionZero": scene["checks"]["shippingEmissionZero"],
        "geometryMaterialLightEnvironmentPreserved": scene["checks"]["geometryUnchanged"]
        and scene["checks"]["materialsUnchanged"]
        and scene["checks"]["approvedLightingUnchanged"]
        and scene["checks"]["approvedEnvironmentUnchanged"],
        "gate09Only": scene["checks"]["gate09Only"],
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 2,
        "metrics": metrics,
        "sequence": {
            "closedRedArtworkPixels": closed_red,
            "openRedArtworkPixels": open_red,
            "openToClosedArtworkRatio": round(open_red / closed_red, 6),
        },
        "differences": differences,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 rev 2 open image validation failed.")


if __name__ == "__main__":
    main()
