#!/usr/bin/env python3
"""Build Gate 09 rev 9 review boards and image audit."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
REPORT = HERE / "image-environment-audit.json"


def font(size: int):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_rgb(name: str) -> Image.Image:
    return Image.open(HERE / name).convert("RGB")


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (12, 13, 15))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def board(filename: str, title: str, cells: list[tuple[str, str]], columns=2) -> None:
    cell_size = (640, 500)
    rows = math.ceil(len(cells) / columns)
    canvas = Image.new(
        "RGB",
        (cell_size[0] * columns, 92 + rows * (cell_size[1] + 48)),
        (8, 9, 11),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((28, 20), title, font=font(34), fill=(242, 242, 245))
    for index, (label, name) in enumerate(cells):
        x = index % columns * cell_size[0]
        y = 92 + index // columns * (cell_size[1] + 48)
        canvas.paste(fit(open_rgb(name), cell_size), (x, y))
        draw.rectangle((x, y + cell_size[1], x + cell_size[0], y + cell_size[1] + 48), fill=(18, 19, 22))
        draw.text((x + 18, y + cell_size[1] + 10), label, font=font(21), fill=(225, 225, 230))
    canvas.save(HERE / filename, quality=96)


def image_metrics(name: str) -> dict:
    pixels = np.asarray(open_rgb(name), dtype=np.uint8)
    corner = pixels[:20, :20].reshape(-1, 3).mean(axis=0)
    foreground = np.max(np.abs(pixels.astype(np.int16) - corner.astype(np.int16)), axis=2) > 5
    object_pixels = pixels[foreground].astype(np.float32)
    red = (
        (object_pixels[:, 0] > 35)
        & (object_pixels[:, 0] > object_pixels[:, 1] * 1.25)
        & (object_pixels[:, 0] > object_pixels[:, 2] * 1.15)
    )
    dark = np.max(object_pixels, axis=1) < 75
    channel_spread = object_pixels.max(axis=1) - object_pixels.min(axis=1)
    silver = (object_pixels.min(axis=1) > 110) & (channel_spread < 30)
    ys, xs = np.where(foreground)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    luminance = (
        object_pixels[:, 0] * 0.2126
        + object_pixels[:, 1] * 0.7152
        + object_pixels[:, 2] * 0.0722
    )
    return {
        "path": name,
        "sha256": sha256(HERE / name),
        "dimensions": [pixels.shape[1], pixels.shape[0]],
        "foregroundFraction": float(foreground.mean()),
        "bbox": bbox,
        "redFractionOfObject": float(red.mean()),
        "darkFractionOfObject": float(dark.mean()),
        "silverFractionOfObject": float(silver.mean()),
        "clippedFraction": float(np.mean(pixels.max(axis=2) >= 255)),
        "luminanceRangeP01P99": float(
            np.percentile(luminance, 99) - np.percentile(luminance, 1)
        ),
    }


def pair_metrics(neutral: str, target: str, metrics: dict) -> dict:
    left = np.asarray(open_rgb(neutral), dtype=np.int16)
    right = np.asarray(open_rgb(target), dtype=np.int16)
    difference = np.abs(left - right)
    return {
        "neutral": neutral,
        "target": target,
        "dimensionsIdentical": left.shape == right.shape,
        "bboxMaximumDeltaPx": max(
            abs(a - b)
            for a, b in zip(metrics[neutral]["bbox"], metrics[target]["bbox"])
        ),
        "changedPixelFractionOver2": float(np.mean(np.max(difference, axis=2) > 2)),
        "meanAbsoluteRgbDelta": float(difference.mean()),
    }


def portability_board(build: dict) -> None:
    preview = open_rgb("target-shipping-studio-r009-preview.png").resize((1280, 640))
    canvas = Image.new("RGB", (1280, 920), (9, 10, 12))
    canvas.paste(preview, (0, 0))
    draw = ImageDraw.Draw(canvas)
    target = build["target"]
    cubemap = build["cubemap"]
    lines = [
        "Gate 09 rev 9 · Unity-portable HDR environment",
        f"OpenEXR 2048×1024 · scene-linear Rec.709/D65 · SHA {target['sha256'][:16]}…",
        f"RGB nonzero {target['nonzeroRgbFraction']:.3f} · seam {target['seamMaximumLinearDelta']:.8f} · range {target['dynamicRangeStopsP01P99']:.2f} stops",
        f"Unity cubemap 6×512² EXR · orientation error {cubemap['brightestDirectionAngularErrorDegrees']:.3f}°",
        "Mapping: Blender (X,Y,Z) → Unity (X,Z,-Y) · neutral-display-v1 · strength 0.85",
    ]
    for index, line in enumerate(lines):
        draw.text((30, 672 + index * 46), line, font=font(26 if index == 0 else 21), fill=(235, 235, 239))
    canvas.save(HERE / "environment-portability-board.png", quality=96)


def video_poster() -> None:
    neutral = open_rgb("turntable-neutral/frame-010.png")
    target = open_rgb("turntable-target/frame-010.png")
    canvas = Image.new("RGB", (1600, 650), (8, 9, 11))
    canvas.paste(neutral, (0, 50))
    canvas.paste(target, (800, 50))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 10), "NEUTRAL CONTROL", font=font(27), fill=(240, 240, 243))
    draw.text((824, 10), "TARGET SHIPPING-LIKE HDR", font=font(27), fill=(240, 240, 243))
    canvas.save(HERE / "environment-turntable-poster.png", quality=96)


def main() -> None:
    build = json.loads((HERE / "environment-build-validation.json").read_text())
    blender = json.loads((HERE / "blender-environment-audit.json").read_text())
    turntable = json.loads((HERE / "environment-turntable-validation.json").read_text())
    names = [
        "neutral-closed.png",
        "target-closed.png",
        "neutral-max0.png",
        "target-max0.png",
        "neutral-side-reflection.png",
        "target-side-reflection.png",
        "target-max12.png",
        "target-max36.png",
        "target-max360.png",
        "target-rim-reflection.png",
        "target-dark-side-closeup.png",
    ]
    metrics = {name: image_metrics(name) for name in names}
    pairs = {
        "closed": pair_metrics("neutral-closed.png", "target-closed.png", metrics),
        "max0": pair_metrics("neutral-max0.png", "target-max0.png", metrics),
        "sideReflection": pair_metrics(
            "neutral-side-reflection.png",
            "target-side-reflection.png",
            metrics,
        ),
    }
    board(
        "environment-comparison-board.png",
        "Gate 09 · Matched neutral versus target environment",
        [
            ("Neutral · closed", "neutral-closed.png"),
            ("Target · closed", "target-closed.png"),
            ("Neutral · maximum open 0°", "neutral-max0.png"),
            ("Target · maximum open 0°", "target-max0.png"),
        ],
    )
    board(
        "environment-motion-board.png",
        "Target environment · legal endpoint states",
        [
            ("Closed 0°", "target-closed.png"),
            ("Maximum open 0°", "target-max0.png"),
            ("Maximum open 12°", "target-max12.png"),
            ("Maximum open 36°", "target-max36.png"),
            ("Maximum open 360°", "target-max360.png"),
        ],
    )
    board(
        "environment-reflection-board.png",
        "Side, rim, and material partition response",
        [
            ("Neutral · side reflection", "neutral-side-reflection.png"),
            ("Target · side reflection", "target-side-reflection.png"),
            ("Target · silver rim", "target-rim-reflection.png"),
            ("Target · dark side, zero artwork", "target-dark-side-closeup.png"),
        ],
    )
    portability_board(build)
    video_poster()
    target_names = [name for name in names if name.startswith("target-")]
    checks = {
        "buildPassed": build["pass"],
        "blenderPassed": blender["pass"],
        "turntablePassed": turntable["pass"],
        "requiredImages": all((HERE / name).exists() for name in names),
        "dimensions": all(metrics[name]["dimensions"] == [1400, 1100] for name in names),
        "pairDimensions": all(pair["dimensionsIdentical"] for pair in pairs.values()),
        "pairSilhouetteBbox": all(pair["bboxMaximumDeltaPx"] <= 1 for pair in pairs.values()),
        "environmentDifferenceVisible": all(
            pair["changedPixelFractionOver2"] > 0.01 for pair in pairs.values()
        ),
        "bloodRedVisible": min(
            metrics[name]["redFractionOfObject"]
            for name in [
                "target-closed.png",
                "target-max0.png",
                "target-max12.png",
                "target-max36.png",
                "target-max360.png",
            ]
        ) > 0.01,
        "darkSideVisible": metrics["target-dark-side-closeup.png"]["darkFractionOfObject"] > 0.25,
        "silverRimVisible": metrics["target-rim-reflection.png"]["silverFractionOfObject"] > 0.001,
        "clippingBounded": max(
            metrics[name]["clippedFraction"]
            for name in [
                "target-closed.png",
                "target-max0.png",
                "target-max12.png",
                "target-max36.png",
                "target-max360.png",
            ]
        ) <= 0.001
        and max(
            metrics[name]["clippedFraction"]
            for name in [
                "target-side-reflection.png",
                "target-rim-reflection.png",
                "target-dark-side-closeup.png",
            ]
        ) <= 0.002,
        "dynamicRange": min(metrics[name]["luminanceRangeP01P99"] for name in target_names) > 25,
        "sideArtworkZeroByPartitionAudit": all(
            item["sideArtworkTriangles"] == 0
            for item in blender["glb"]["importedObjects"].values()
        ),
        "undersideArtworkZeroByPartitionAudit": all(
            item["undersideArtworkTriangles"] == 0
            for item in blender["glb"]["importedObjects"].values()
        ),
    }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "metrics": metrics,
        "matchedPairs": pairs,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "pass": report["pass"],
        "maximumClipping": max(metrics[name]["clippedFraction"] for name in target_names),
        "closedChangedFraction": pairs["closed"]["changedPixelFractionOver2"],
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 image audit failed.")


if __name__ == "__main__":
    main()
