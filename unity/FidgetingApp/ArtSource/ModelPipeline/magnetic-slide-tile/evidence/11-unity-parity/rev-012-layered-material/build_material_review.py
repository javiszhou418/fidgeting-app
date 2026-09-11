#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[5]
SOURCE = (
    PROJECT
    / "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/"
    "rev-001/obsidian-frames/frame-01.jpg"
)
BLENDER = (
    PROJECT
    / "ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/"
    "rev-013/assembled-hero.png"
)
FLAT = ROOT / "A-current-flat-unity"
LAYERED = ROOT / "B-layered-unity"
VIEWS = [
    "front",
    "hero",
    "left-oblique",
    "right-oblique",
    "grazing",
    "low",
    "phone",
    "max-open",
]


def font(size):
    for path in (
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fitted(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    return image


def rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def object_mask(image):
    background = np.median(
        np.concatenate(
            [
                image[:20, :20].reshape(-1, 3),
                image[:20, -20:].reshape(-1, 3),
                image[-20:, :20].reshape(-1, 3),
                image[-20:, -20:].reshape(-1, 3),
            ]
        ),
        axis=0,
    )
    return np.max(np.abs(image - background), axis=2) > 0.025


def metrics(path):
    image = rgb(path)
    mask = object_mask(image)
    maximum = image.max(axis=2)
    minimum = image.min(axis=2)
    red = mask & (image[:, :, 0] > image[:, :, 1] * 1.35)
    black = mask & (maximum < 0.18)
    luminance = (
        image[:, :, 0] * 0.2126
        + image[:, :, 1] * 0.7152
        + image[:, :, 2] * 0.0722
    )
    blurred = np.asarray(
        Image.fromarray((luminance * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(3)
        ),
        dtype=np.float32,
    ) / 255.0
    local = np.abs(luminance - blurred)
    saturation = np.divide(
        maximum - minimum,
        maximum,
        out=np.zeros_like(maximum),
        where=maximum > 1e-6,
    )
    return {
        "objectMedianLuminance": float(np.median(luminance[mask])),
        "redPixelFraction": float(red.sum() / max(mask.sum(), 1)),
        "redMedianSaturation": float(np.median(saturation[red])) if red.any() else 0,
        "redLocalVariationP90": float(np.percentile(local[red], 90)) if red.any() else 0,
        "blackMedianLuminance": float(np.median(luminance[black])) if black.any() else 0,
        "clippedFraction": float(np.mean(maximum[mask] >= 250 / 255)),
    }


def authority_board():
    items = [
        ("Original product cue", SOURCE),
        ("Approved Blender lookdev", BLENDER),
        ("Current flat Unity", FLAT / "hero.png"),
        ("Corrected layered Unity", LAYERED / "hero.png"),
    ]
    canvas = Image.new("RGB", (2200, 720), (10, 12, 16))
    draw = ImageDraw.Draw(canvas)
    draw.text((42, 24), "Material authority chain", font=font(38), fill="white")
    draw.text(
        (42, 72),
        "Original reference → Blender target → installed flat transport → one-pass layered Unity",
        font=font(22),
        fill=(174, 182, 192),
    )
    for index, (label, path) in enumerate(items):
        x = 28 + index * 542
        image = fitted(path, (520, 520))
        canvas.paste(image, (x + (520 - image.width) // 2, 126))
        draw.text((x, 662), label, font=font(21), fill=(230, 233, 238))
    canvas.save(ROOT / "gate11-r012-material-authority-board.png")


def view_board():
    canvas = Image.new("RGB", (2100, 1510), (9, 11, 14))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (36, 24),
        "Real MeshyEDC.unity · corrected layered material",
        font=font(38),
        fill="white",
    )
    for index, view in enumerate(VIEWS):
        column = index % 4
        row = index // 4
        x = 26 + column * 518
        y = 94 + row * 690
        image = fitted(LAYERED / f"{view}.png", (500, 610))
        canvas.paste(image, (x + (500 - image.width) // 2, y))
        draw.text((x, y + 616), view, font=font(21), fill=(190, 198, 208))
    canvas.save(ROOT / "gate11-r012-layered-shipping-views.png")


def compare_board():
    views = ["hero", "grazing", "max-open"]
    canvas = Image.new("RGB", (1920, 1280), (9, 11, 14))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (38, 24),
        "Current flat vs corrected layered Unity",
        font=font(38),
        fill="white",
    )
    for row, view in enumerate(views):
        for column, (label, folder) in enumerate(
            [("Current flat", FLAT), ("Corrected layered", LAYERED)]
        ):
            x = 24 + column * 948
            y = 88 + row * 390
            image = fitted(folder / f"{view}.png", (920, 340))
            canvas.paste(image, (x + (920 - image.width) // 2, y))
            draw.text(
                (x, y + 344),
                f"{view} · {label}",
                font=font(20),
                fill=(205, 211, 220),
            )
    canvas.save(ROOT / "gate11-r012-flat-layered-comparison.png")


def write_metrics():
    flat = metrics(FLAT / "hero.png")
    layered = metrics(LAYERED / "hero.png")
    checks = {
        "deepRedPresent": layered["redPixelFraction"] > 0.12,
        "redSaturationRetained": layered["redMedianSaturation"] > 0.48,
        "localVariationVisible": layered["redLocalVariationP90"] > 0.006,
        "blackDetailNotCrushed": layered["blackMedianLuminance"] > 0.004,
        "highlightClippingBelowHalfPercent": layered["clippedFraction"] < 0.005,
        "materialResponseChanged": abs(
            layered["objectMedianLuminance"] - flat["objectMedianLuminance"]
        )
        > 0.005,
    }
    report = {
        "schemaVersion": 1,
        "source": "real MeshyEDC.unity camera renders",
        "flat": flat,
        "layered": layered,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (ROOT / "layered-material-image-metrics.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    if not report["pass"]:
        raise SystemExit(json.dumps(report, indent=2))


if __name__ == "__main__":
    authority_board()
    view_board()
    compare_board()
    write_metrics()
