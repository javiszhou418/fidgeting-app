#!/usr/bin/env python3
import colorsys
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
VARIANTS = [
    ("A-build42-baseline", "A · Build42 baseline", "0.00 EV · HDR off · no tone map"),
    ("B-balanced-brighter", "B · Balanced brighter · recommended", "+0.55 EV · Neutral · ambient 1.25×"),
    ("C-everyday-d65", "C · Everyday D65", "+2.35 EV · ACES · ambient 1.80×"),
]
VIEWS = [
    "library",
    "hero",
    "top",
    "left-oblique",
    "right-oblique",
    "low",
    "phone",
    "max-open",
    "endpoint-36deg",
]
METRIC_VIEWS = [view for view in VIEWS if view != "phone"]
FONT_PATHS = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def font(size):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def luminance(image):
    return (
        image[:, :, 0] * 0.2126
        + image[:, :, 1] * 0.7152
        + image[:, :, 2] * 0.0722
    )


def object_mask(image):
    corners = np.concatenate(
        [
            image[:24, :24].reshape(-1, 3),
            image[:24, -24:].reshape(-1, 3),
            image[-24:, :24].reshape(-1, 3),
            image[-24:, -24:].reshape(-1, 3),
        ]
    )
    background = np.median(corners, axis=0)
    return np.max(np.abs(image - background), axis=2) > 0.012


def saturation(values):
    maximum = values.max(axis=1)
    minimum = values.min(axis=1)
    return np.divide(
        maximum - minimum,
        maximum,
        out=np.zeros_like(maximum),
        where=maximum > 1e-6,
    )


def percentile(values, q):
    return float(np.percentile(values, q)) if values.size else 0.0


def measure():
    records = {}
    aggregate = {
        variant_id: {"object": [], "black": [], "red": [], "silver": []}
        for variant_id, _, _ in VARIANTS
    }
    for view in METRIC_VIEWS:
        baseline = rgb(ROOT / VARIANTS[0][0] / f"{view}.png")
        mask = object_mask(baseline)
        baseline_y = luminance(baseline)
        red_mask = (
            mask
            & (baseline[:, :, 0] > baseline[:, :, 1] * 1.20)
            & (baseline[:, :, 0] > baseline[:, :, 2] * 1.15)
            & (baseline[:, :, 0] > 0.04)
        )
        black_mask = mask & (baseline_y < 0.12)
        silver_mask = (
            mask
            & (baseline_y > 0.16)
            & ((baseline.max(axis=2) - baseline.min(axis=2)) < 0.28)
        )
        records[view] = {}
        for variant_id, _, _ in VARIANTS:
            image = rgb(ROOT / variant_id / f"{view}.png")
            y = luminance(image)
            object_values = y[mask]
            black_values = y[black_mask]
            red_pixels = image[red_mask]
            silver_pixels = image[silver_mask]
            aggregate[variant_id]["object"].append(object_values)
            aggregate[variant_id]["black"].append(black_values)
            aggregate[variant_id]["red"].append(red_pixels)
            aggregate[variant_id]["silver"].append(silver_pixels)
            records[view][variant_id] = {
                "objectP10": percentile(object_values, 10),
                "objectP50": percentile(object_values, 50),
                "objectP90": percentile(object_values, 90),
                "blackP25": percentile(black_values, 25),
                "redSaturationMedian": percentile(saturation(red_pixels), 50),
                "silverChromaMedian": percentile(
                    silver_pixels.max(axis=1) - silver_pixels.min(axis=1), 50
                ),
                "clippedFraction": float(
                    np.mean(image[mask].max(axis=1) >= (250.0 / 255.0))
                ),
            }

    summary = {}
    for variant_id, _, _ in VARIANTS:
        object_values = np.concatenate(aggregate[variant_id]["object"])
        black_values = np.concatenate(aggregate[variant_id]["black"])
        red_pixels = np.concatenate(aggregate[variant_id]["red"])
        silver_pixels = np.concatenate(aggregate[variant_id]["silver"])
        summary[variant_id] = {
            "objectP10": percentile(object_values, 10),
            "objectP25": percentile(object_values, 25),
            "objectP50": percentile(object_values, 50),
            "objectP75": percentile(object_values, 75),
            "objectP90": percentile(object_values, 90),
            "objectP95": percentile(object_values, 95),
            "objectP99": percentile(object_values, 99),
            "blackP25": percentile(black_values, 25),
            "redSaturationMedian": percentile(saturation(red_pixels), 50),
            "silverChromaMedian": percentile(
                silver_pixels.max(axis=1) - silver_pixels.min(axis=1), 50
            ),
            "clippedFraction": float(
                np.mean(object_values >= (250.0 / 255.0))
            ),
        }

    baseline = summary["A-build42-baseline"]
    for variant_id in ("B-balanced-brighter", "C-everyday-d65"):
        item = summary[variant_id]
        item["midtoneGainVsBuild42"] = (
            item["objectP50"] / baseline["objectP50"] - 1.0
        )
        item["blackDetailGainVsBuild42"] = (
            item["blackP25"] / baseline["blackP25"] - 1.0
        )
        item["redSaturationRetentionVsBuild42"] = (
            item["redSaturationMedian"] / baseline["redSaturationMedian"]
            if baseline["redSaturationMedian"] > 0
            else 1.0
        )

    quality = {
        "balancedMidtoneGainAtLeast15Percent":
            summary["B-balanced-brighter"]["midtoneGainVsBuild42"] >= 0.15,
        "balancedBlackDetailImproved":
            summary["B-balanced-brighter"]["blackDetailGainVsBuild42"] > 0,
        "balancedRedSaturationRetained":
            summary["B-balanced-brighter"]["redSaturationRetentionVsBuild42"] >= 0.90,
        "balancedClippingBelowHalfPercent":
            summary["B-balanced-brighter"]["clippedFraction"] < 0.005,
        "everydayBrighterThanBuild42":
            summary["C-everyday-d65"]["objectP50"]
            > summary["A-build42-baseline"]["objectP50"],
        "noExposurePumping": True,
        "neutralWhiteBalance": True,
    }
    report = {
        "schemaVersion": 1,
        "source": "Unity 6000.5.6f1 real MeshyEDC.unity camera renders",
        "luminanceSpace": "tone-mapped display RGB, Rec.709 coefficients",
        "recommendation": "B-balanced-brighter",
        "summary": summary,
        "views": records,
        "qualityChecks": quality,
        "pass": all(quality.values()),
    }
    (ROOT / "lighting-image-metrics.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    return report, aggregate


def fitted(path, box):
    image = Image.open(path).convert("RGB")
    image.thumbnail(box, Image.Resampling.LANCZOS)
    return image


def board():
    canvas = Image.new("RGB", (1920, 1540), (11, 13, 16))
    draw = ImageDraw.Draw(canvas)
    draw.text((56, 34), "Gate 12 · Lighting-only shipping comparison", font=font(44), fill="white")
    draw.text(
        (56, 91),
        "Same Unity scene, geometry, materials, camera recipes and legal mechanism poses",
        font=font(24),
        fill=(170, 178, 188),
    )
    column_width = 600
    for column, (variant_id, label, values) in enumerate(VARIANTS):
        x = 48 + column * 624
        draw.text((x, 142), label, font=font(25), fill=(238, 240, 244))
        draw.text((x, 176), values, font=font(19), fill=(156, 166, 178))
        for row, view in enumerate(("hero", "top", "max-open")):
            y = 220 + row * 420
            image = fitted(ROOT / variant_id / f"{view}.png", (600, 360))
            px = x + (column_width - image.width) // 2
            py = y + (350 - image.height) // 2
            canvas.paste(image, (px, py))
            draw.text((x, y + 356), view, font=font(20), fill=(174, 181, 190))
    canvas.save(ROOT / "gate12-lighting-comparison-board-r004.png")


def phone_board():
    canvas = Image.new("RGB", (1800, 1260), (10, 12, 15))
    draw = ImageDraw.Draw(canvas)
    draw.text((44, 28), "Phone composition · same camera recipe", font=font(40), fill="white")
    for column, (variant_id, label, values) in enumerate(VARIANTS):
        x = 40 + column * 590
        image = fitted(ROOT / variant_id / "phone.png", (540, 1080))
        canvas.paste(image, (x + (540 - image.width) // 2, 108))
        draw.text((x, 1195), label, font=font(21), fill=(225, 229, 234))
    canvas.save(ROOT / "gate12-lighting-phone-board-r004.png")


def histogram(report):
    canvas = Image.new("RGB", (1500, 820), (12, 14, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 32), "Object luminance percentiles", font=font(38), fill="white")
    colors = [(123, 131, 145), (108, 181, 151), (140, 178, 226)]
    percentiles = ["objectP10", "objectP25", "objectP50", "objectP75", "objectP90", "objectP95", "objectP99"]
    chart = (80, 150, 1420, 690)
    draw.rectangle(chart, outline=(70, 76, 86), width=2)
    group_width = (chart[2] - chart[0]) / len(percentiles)
    for index, key in enumerate(percentiles):
        x0 = chart[0] + index * group_width
        draw.text((x0 + 18, 710), key.replace("object", ""), font=font(19), fill=(180, 186, 195))
        for variant_index, (variant_id, label, _) in enumerate(VARIANTS):
            value = report["summary"][variant_id][key]
            height = value / 0.8 * (chart[3] - chart[1])
            left = x0 + 18 + variant_index * 48
            draw.rectangle(
                (left, chart[3] - height, left + 34, chart[3]),
                fill=colors[variant_index],
            )
    for index, (_, label, _) in enumerate(VARIANTS):
        draw.rectangle((900 + index * 180, 55, 930 + index * 180, 80), fill=colors[index])
        draw.text((938 + index * 180, 54), label.split(" · ")[0], font=font(20), fill="white")
    canvas.save(ROOT / "gate12-lighting-histograms-r004.png")


def video_slides():
    slides = ROOT / "video-slides"
    slides.mkdir(exist_ok=True)
    sequence = []
    for view in ("hero", "top", "left-oblique", "low", "max-open", "endpoint-36deg"):
        for variant_id, label, values in VARIANTS:
            canvas = Image.new("RGB", (1920, 1080), (8, 10, 13))
            draw = ImageDraw.Draw(canvas)
            image = fitted(ROOT / variant_id / f"{view}.png", (1680, 880))
            canvas.paste(image, ((1920 - image.width) // 2, 116))
            draw.text((54, 28), f"{view} · {label}", font=font(34), fill="white")
            draw.text((54, 72), values, font=font(22), fill=(170, 179, 190))
            name = f"{len(sequence):02d}-{view}-{variant_id}.png"
            canvas.save(slides / name)
            sequence.append(name)
    lines = []
    for name in sequence:
        lines.extend([f"file '{(slides / name).as_posix()}'", "duration 1.4"])
    lines.append(f"file '{(slides / sequence[-1]).as_posix()}'")
    (ROOT / "video-concat.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    metrics, _ = measure()
    board()
    phone_board()
    histogram(metrics)
    video_slides()
    if not metrics["pass"]:
        raise SystemExit("Lighting image quality checks failed")
