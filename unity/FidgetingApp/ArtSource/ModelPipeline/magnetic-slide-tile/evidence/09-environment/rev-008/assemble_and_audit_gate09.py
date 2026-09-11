#!/usr/bin/env python3
"""Assemble Gate 09 review boards and audit rendered evidence."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def open_rgb(name):
    return Image.open(HERE / name).convert("RGB")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fit(image, size):
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (13, 14, 16))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def board(filename, title, cells, columns=2, cell_size=(700, 550)):
    rows = math.ceil(len(cells) / columns)
    header = 100
    caption = 50
    canvas = Image.new("RGB", (cell_size[0] * columns, header + (cell_size[1] + caption) * rows), (10, 11, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((32, 24), title, font=font(36), fill=(246, 246, 248))
    for index, (label, image_name) in enumerate(cells):
        x = (index % columns) * cell_size[0]
        y = header + (index // columns) * (cell_size[1] + caption)
        canvas.paste(fit(open_rgb(image_name), cell_size), (x, y))
        draw.rectangle((x, y + cell_size[1], x + cell_size[0], y + cell_size[1] + caption), fill=(19, 20, 24))
        draw.text((x + 22, y + cell_size[1] + 10), label, font=font(22), fill=(226, 226, 230))
    canvas.save(HERE / filename, quality=96)


def image_metrics(name):
    image = open_rgb(name)
    array = np.asarray(image, dtype=np.float32)
    luminance = array[:, :, 0] * 0.2126 + array[:, :, 1] * 0.7152 + array[:, :, 2] * 0.0722
    red = (array[:, :, 0] > 24) & (array[:, :, 0] > array[:, :, 1] * 1.42) & (array[:, :, 0] > array[:, :, 2] * 1.25)
    red_pixels = array[red]
    if red_pixels.size:
        maximum = red_pixels.max(axis=1)
        minimum = red_pixels.min(axis=1)
        chroma = maximum - minimum
        hue = np.zeros_like(maximum)
        safe = chroma > 0
        indices = safe & (maximum == red_pixels[:, 0])
        hue[indices] = 60 * ((red_pixels[indices, 1] - red_pixels[indices, 2]) / chroma[indices])
        indices = safe & (maximum == red_pixels[:, 1])
        hue[indices] = 60 * (2 + (red_pixels[indices, 2] - red_pixels[indices, 0]) / chroma[indices])
        indices = safe & (maximum == red_pixels[:, 2])
        hue[indices] = 60 * (4 + (red_pixels[indices, 0] - red_pixels[indices, 1]) / chroma[indices])
        red_hue = float(np.median(hue))
        red_luminance_std = float(luminance[red].std())
    else:
        red_hue = 999
        red_luminance_std = 0
    low_chroma = array.max(axis=2) - array.min(axis=2) <= 10
    silver = low_chroma & (luminance >= 70) & (luminance <= 245)
    silver_pixels = array[silver]
    silver_channel_spread = float(np.mean(silver_pixels.max(axis=1) - silver_pixels.min(axis=1))) if silver_pixels.size else 999
    edge = np.asarray(image.filter(ImageFilter.FIND_EDGES).convert("L"), dtype=np.uint8)
    return {
        "path": name,
        "pixelSha256": hashlib.sha256(array.astype(np.uint8).tobytes()).hexdigest(),
        "fileSha256": sha256(HERE / name),
        "dimensionsPx": list(image.size),
        "luminanceMean": float(luminance.mean()),
        "luminanceStd": float(luminance.std()),
        "dynamicRange": float(np.percentile(luminance, 99.5) - np.percentile(luminance, 0.5)),
        "clippedFraction": float(np.mean((array >= 254).all(axis=2))),
        "redPixelFraction": float(red.mean()),
        "redMedianHueDegrees": red_hue,
        "redLuminanceStd": red_luminance_std,
        "silverNeutralPixelFraction": float(silver.mean()),
        "silverMeanChannelSpread": silver_channel_spread,
        "edgeFraction": float(np.mean(edge > 24)),
    }


def pair_metrics(neutral_name, shipping_name):
    neutral = np.asarray(open_rgb(neutral_name), dtype=np.int16)
    shipping = np.asarray(open_rgb(shipping_name), dtype=np.int16)
    difference = np.abs(neutral - shipping)
    return {
        "neutral": neutral_name,
        "shipping": shipping_name,
        "dimensionsIdentical": neutral.shape == shipping.shape,
        "meanAbsoluteRgbDelta": float(difference.mean()),
        "p95AbsoluteRgbDelta": float(np.percentile(difference, 95)),
        "changedPixelFractionOver2": float(np.mean(np.max(difference, axis=2) > 2)),
        "neutralPixelSha256": hashlib.sha256(neutral.astype(np.uint8).tobytes()).hexdigest(),
        "shippingPixelSha256": hashlib.sha256(shipping.astype(np.uint8).tobytes()).hexdigest(),
    }


def create_turntable_comparison():
    output = HERE / "turntable-comparison"
    output.mkdir(exist_ok=True)
    labels = font(28)
    for frame in range(24):
        neutral = open_rgb(f"turntable-neutral/frame-{frame:03d}.png")
        shipping = open_rgb(f"turntable-shipping/frame-{frame:03d}.png")
        canvas = Image.new("RGB", (1440, 590), (8, 9, 11))
        canvas.paste(neutral, (0, 50))
        canvas.paste(shipping, (720, 50))
        draw = ImageDraw.Draw(canvas)
        draw.text((24, 10), "NEUTRAL · matched light/camera/pose", font=labels, fill=(230, 230, 232))
        draw.text((744, 10), "TARGET SHIPPING · portable EXR", font=labels, fill=(230, 230, 232))
        canvas.save(output / f"frame-{frame:03d}.png")
    return output


def create_hdri_board(metadata):
    preview = open_rgb("magnetic-slide-tile-shipping-studio-r008-preview.png")
    canvas = Image.new("RGB", (2048, 1370), (11, 12, 15))
    canvas.paste(preview, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 1024, 2048, 1370), fill=(15, 16, 20))
    lines = [
        "PORTABLE SHIPPING ENVIRONMENT · Gate 09 rev 8",
        f"OpenEXR {metadata['resolutionPx'][0]}×{metadata['resolutionPx'][1]} · equirectangular · scene-linear Rec.709 / D65",
        f"Seam max linear delta {metadata['seamMaxAbsoluteLinearDelta']:.8f} · dynamic range {metadata['dynamicRangeStopsP01ToP99']:.3f} stops",
        f"SHA-256 {metadata['sha256']}",
        "World strength 0.65 · rotation 0° · no procedural Blender-only environment nodes",
    ]
    for index, line in enumerate(lines):
        draw.text((42, 1052 + index * 56), line, font=font(30 if index == 0 else 24), fill=(240, 240, 243))
    canvas.save(HERE / "portable-environment-board.png")


def main():
    environment = json.loads((HERE / "environment-validation.json").read_text(encoding="utf-8"))
    metadata = json.loads((HERE / "portable-hdri-metadata.json").read_text(encoding="utf-8"))
    stills = environment["views"]
    metrics = {name: image_metrics(name) for name in stills}
    pairs = {
        "closedHero": pair_metrics("neutral-closed-hero.png", "shipping-closed-hero.png"),
        "maxOpen": pair_metrics("neutral-max-open.png", "shipping-max-open.png"),
        "reflectionCloseup": pair_metrics("neutral-reflection-closeup.png", "shipping-reflection-closeup.png"),
    }
    board(
        "environment-comparison-board.png",
        "Gate 09 · matched neutral versus portable target environment",
        [
            ("Neutral · Closed Hero", "neutral-closed-hero.png"),
            ("Target shipping · Closed Hero", "shipping-closed-hero.png"),
            ("Neutral · Maximum open", "neutral-max-open.png"),
            ("Target shipping · Maximum open", "shipping-max-open.png"),
        ],
    )
    board(
        "shipping-environment-views-board.png",
        "Target shipping environment · model and motion readability",
        [
            ("Closed Hero", "shipping-closed-hero.png"),
            ("Maximum open", "shipping-max-open.png"),
            ("Detent 12°", "shipping-detent-12.png"),
            ("Detent 36°", "shipping-detent-36.png"),
            ("Left oblique", "shipping-left-oblique.png"),
            ("Low angle", "shipping-low-angle.png"),
        ],
    )
    board(
        "reflection-comparison-board.png",
        "Same-camera silver and crystal reflection comparison",
        [
            ("Neutral environment", "neutral-reflection-closeup.png"),
            ("Target shipping EXR", "shipping-reflection-closeup.png"),
        ],
        columns=2,
    )
    board(
        "mechanical-readability-board.png",
        "Target environment · flat plane, raised axis, four grooves, carrier clearance",
        [
            ("Flat plane + raised axis", "shipping-flat-plane-raised-axis.png"),
            ("Four recessed underside grooves", "shipping-underside-grooves.png"),
            ("Carrier + followers + ball candidates", "shipping-carrier-clearance.png"),
        ],
        columns=3,
        cell_size=(600, 472),
    )
    create_hdri_board(metadata)
    create_turntable_comparison()
    target_names = [name for name in stills if name.startswith("shipping-")]
    target_metrics = [metrics[name] for name in target_names]
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "pass": False,
        "environmentSha256": metadata["sha256"],
        "geometryDigest": environment["geometry"]["after"],
        "materialDigest": environment["materials"]["approvedSemanticDigest"],
        "lightDigest": environment["lighting"]["after"],
        "cameraDigest": environment["cameras"]["after"],
        "metrics": metrics,
        "matchedPairs": pairs,
        "aggregate": {
            "maximumClippedFraction": max(item["clippedFraction"] for item in target_metrics),
            "minimumTargetDynamicRange": min(item["dynamicRange"] for item in target_metrics),
            "minimumTargetRedFraction": min(item["redPixelFraction"] for item in target_metrics if "underside" not in item["path"] and "carrier" not in item["path"] and "flat-plane" not in item["path"]),
            "targetRedMedianHueRange": [
                min(item["redMedianHueDegrees"] for item in target_metrics if item["redPixelFraction"] > 0.001),
                max(item["redMedianHueDegrees"] for item in target_metrics if item["redPixelFraction"] > 0.001),
            ],
            "minimumCrystalVariation": min(
                metrics[name]["redLuminanceStd"]
                for name in [
                    "shipping-closed-hero.png", "shipping-max-open.png",
                    "shipping-detent-12.png", "shipping-detent-36.png",
                    "shipping-reflection-closeup.png",
                ]
            ),
            "minimumMechanicalEdgeFraction": min(
                metrics[name]["edgeFraction"]
                for name in ["shipping-flat-plane-raised-axis.png", "shipping-underside-grooves.png", "shipping-carrier-clearance.png"]
            ),
        },
    }
    checks = {
        "matchedPairDimensions": all(pair["dimensionsIdentical"] for pair in pairs.values()),
        "environmentDifferenceVisible": pairs["closedHero"]["changedPixelFractionOver2"] > 0.01
        and pairs["reflectionCloseup"]["changedPixelFractionOver2"] > 0.005,
        "environmentOnlySourceInvariants": environment["checks"]["geometryUnchanged"]
        and environment["checks"]["materialsUnchanged"]
        and environment["checks"]["lightsUnchanged"]
        and environment["checks"]["sourceCamerasUnchanged"],
        "hdriSeam": metadata["seamMaxAbsoluteLinearDelta"] <= 1e-6,
        "hdriDynamicRange": metadata["dynamicRangeStopsP01ToP99"] >= 4,
        "bloodRedHue": report["aggregate"]["targetRedMedianHueRange"][0] >= -22
        and report["aggregate"]["targetRedMedianHueRange"][1] <= 15,
        "crystalVariation": report["aggregate"]["minimumCrystalVariation"] >= 10,
        "motifContrast": report["aggregate"]["minimumTargetDynamicRange"] >= 80,
        "silverNeutral": metrics["shipping-reflection-closeup.png"]["silverMeanChannelSpread"] <= 10
        and metrics["shipping-reflection-closeup.png"]["silverNeutralPixelFraction"] > 0.01,
        "noClipping": report["aggregate"]["maximumClippedFraction"] <= 0.001,
        "mechanicalReadable": report["aggregate"]["minimumMechanicalEdgeFraction"] > 0.0085,
        "noEmission": environment["checks"]["approvedEmissionZero"],
        "motionContainment": environment["checks"]["motionContainmentPreserved"],
        "turntablePairs": len(list((HERE / "turntable-comparison").glob("frame-*.png"))) == 24,
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    (HERE / "image-environment-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps({"checks": checks, "aggregate": report["aggregate"], "pairs": pairs}, indent=2))
    print(json.dumps({"pass": True, "checks": checks, "aggregate": report["aggregate"], "pairs": pairs}, indent=2))


if __name__ == "__main__":
    main()

