#!/usr/bin/env python3
"""Derive source-linked blood-red targets and editable upper/lower artwork masks."""

from __future__ import annotations

import colorsys
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps, ImageStat


OUTPUT = Path(__file__).resolve().parent
INTAKE = OUTPUT.parents[1] / "01-intake"
UPPER_SOURCE = INTAKE / "rev-001/obsidian-frames/frame-01.jpg"
UPPER_COLOR_SOURCE = INTAKE / "rev-001/obsidian-frames/frame-05.jpg"
LOWER_SOURCE = INTAKE / "rev-001/obsidian-frames/frame-10.jpg"
OFFICIAL_RED_SOURCE = INTAKE / "rev-002/haloo-official/03.png"
SIZE = (620, 1000)

UPPER_QUAD = (289, 530, 429, 546, 466, 901, 256, 873)
LOWER_VISIBLE_QUAD = (272, 716, 439, 733, 438, 884, 274, 871)
LOWER_VISIBLE_Y = 620


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capsule_mask(size: tuple[int, int], inset: int = 18) -> Image.Image:
    width, height = size
    image = Image.new("L", size, 0)
    ImageDraw.Draw(image).rounded_rectangle(
        (inset, inset, width - inset - 1, height - inset - 1),
        radius=(width - inset * 2) // 2,
        fill=255,
    )
    return image


def rectify(path: Path, quad: tuple[int, ...], size: tuple[int, int]) -> Image.Image:
    source = np.asarray(Image.open(path).convert("RGB"))
    source_points = np.float32(list(zip(quad[0::2], quad[1::2])))
    width, height = size
    destination_points = np.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ])
    matrix = cv2.getPerspectiveTransform(source_points, destination_points)
    rectified = cv2.warpPerspective(
        source,
        matrix,
        size,
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return Image.fromarray(rectified, "RGB")


def dark_trace(image: Image.Image, interior: Image.Image) -> Image.Image:
    softened = image.filter(ImageFilter.GaussianBlur(1.2))
    trace = Image.new("L", image.size, 0)
    trace_pixels = trace.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = softened.getpixel((x, y))
            h, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            dark_fill = value < 0.40 and (
                saturation < 0.72
                or r < max(g, b) * 2.6
                or value < 0.16
            )
            trace_pixels[x, y] = 255 if dark_fill else 0
    trace = trace.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.MaxFilter(3))
    return ImageChops.multiply(trace, interior)


def percentile(values: list[float], fraction: float) -> float:
    values.sort()
    return values[min(len(values) - 1, round((len(values) - 1) * fraction))]


def source_color_report(rectified: Image.Image, trace: Image.Image) -> dict:
    pixels = list(rectified.getdata())
    mask = list(trace.getdata())
    steel = []
    red = []
    width, height = rectified.size
    for index, (r, g, b) in enumerate(pixels):
        x = index % width
        y = index // width
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if mask[index] < 64 and r > 45 and r > g * 1.55 and r > b * 1.25 and s > 0.55 and 0.18 < v < 0.82:
            red.append((r, g, b))
        border = x < 62 or x > width - 63
        if border and 90 < y < height - 90 and s < 0.26 and 35 < max(r, g, b) < 205:
            steel.append((r, g, b))
    if len(red) < 1000 or len(steel) < 80:
        raise RuntimeError(f"Insufficient source samples: red={len(red)}, steel={len(steel)}")
    steel_mean = [ImageStat.Stat(Image.new("L", (len(steel), 1), 0)).mean[0]] * 3
    steel_mean = [sum(pixel[channel] for pixel in steel) / len(steel) for channel in range(3)]
    neutral = sum(steel_mean) / 3
    gains = [neutral / value for value in steel_mean]
    corrected = [
        tuple(max(0, min(255, channel * gains[index])) for index, channel in enumerate(pixel))
        for pixel in red
    ]
    channels = list(zip(*corrected))
    median = [round(percentile(list(channel), 0.5), 2) for channel in channels]
    p10 = [round(percentile(list(channel), 0.1), 2) for channel in channels]
    p90 = [round(percentile(list(channel), 0.9), 2) for channel in channels]
    hsv = [colorsys.rgb_to_hsv(*(channel / 255 for channel in pixel)) for pixel in corrected]
    red_hues = [((item[0] * 360 + 180) % 360) - 180 for item in hsv]
    return {
        "sampleCount": len(red),
        "nearbyNeutralSteelSampleCount": len(steel),
        "nearbyNeutralSteelMeanSrgb": [round(value, 3) for value in steel_mean],
        "whiteBalanceGains": [round(value, 6) for value in gains],
        "correctedBloodRedSrgb": {"p10": p10, "median": median, "p90": p90},
        "correctedHsv": {
            "hueSignedMedianDegrees": round(percentile(red_hues, 0.5), 3),
            "saturationMedian": round(percentile([item[1] for item in hsv], 0.5), 4),
            "valueMedian": round(percentile([item[2] for item in hsv], 0.5), 4),
        },
        "shaderTargetLinearRgb": [0.22, 0.008, 0.018],
        "shaderAllowedLinearRange": {
            "red": [0.08, 0.42],
            "green": [0.002, 0.028],
            "blue": [0.004, 0.045],
        },
        "userAuthority": "deep blood red, not pink",
        "chemistryClaimed": False,
    }


def main() -> None:
    upper = rectify(UPPER_SOURCE, UPPER_QUAD, SIZE)
    upper.save(OUTPUT / "upper-source-rectified.png")
    interior = capsule_mask(SIZE, 45)
    upper_trace = dark_trace(upper, interior)
    upper_trace.save(OUTPUT / "artwork-upper-mask.png")

    lower_visible = rectify(LOWER_SOURCE, LOWER_VISIBLE_QUAD, (620, 380))
    lower_visible.save(OUTPUT / "lower-visible-source-rectified.png")
    lower_trace_visible = dark_trace(lower_visible, capsule_mask((620, 380), 24))
    lower_trace = Image.new("L", SIZE, 0)
    lower_trace.paste(lower_trace_visible, (0, LOWER_VISIBLE_Y))
    lower_trace.save(OUTPUT / "artwork-lower-mask.png")
    lower_unknown = Image.new("L", SIZE, 0)
    ImageDraw.Draw(lower_unknown).rectangle((0, 0, 619, LOWER_VISIBLE_Y - 1), fill=255)
    lower_unknown = ImageChops.multiply(lower_unknown, interior)
    lower_unknown.save(OUTPUT / "artwork-lower-occluded-unknown.png")

    color_report = source_color_report(upper, upper_trace)
    color_report.update({
        "schemaVersion": 1,
        "sourceAssetIds": [
            "slider-intake-obs-frame-01",
            "slider-intake-obs-frame-05",
            "slider-intake-obs-frame-10",
            "slider-intake-haloo-official-03",
        ],
        "sourceHashes": {
            "upper": sha256(UPPER_SOURCE),
            "upperColorCrossCheck": sha256(UPPER_COLOR_SOURCE),
            "lower": sha256(LOWER_SOURCE),
            "officialRedCrossCheck": sha256(OFFICIAL_RED_SOURCE),
        },
        "perspectiveRectification": {
            "upperQuadPixels": list(UPPER_QUAD),
            "lowerVisibleQuadPixels": list(LOWER_VISIBLE_QUAD),
            "outputSizePx": list(SIZE),
        },
    })
    (OUTPUT / "blood-red-source-analysis.json").write_text(
        json.dumps(color_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 4,
        "geometryDigest": "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f",
        "slots": {
            "Artwork_Upper": {
                "mask": "artwork-upper-mask.png",
                "sourceAssetIds": ["slider-intake-obs-frame-01", "slider-intake-haloo-official-03"],
                "sourceQuadPixels": list(UPPER_QUAD),
                "coverage": "full-visible-face",
                "occludedOrReconstructed": False,
            },
            "Artwork_Lower": {
                "mask": "artwork-lower-mask.png",
                "unknownMask": "artwork-lower-occluded-unknown.png",
                "sourceAssetIds": ["slider-intake-obs-frame-10"],
                "sourceQuadPixels": list(LOWER_VISIBLE_QUAD),
                "coverage": "source-visible-open-end-only",
                "occludedOrReconstructed": True,
                "policy": "The source-visible exposed end is traced. The region hidden under the upper shell remains explicitly unknown and receives no invented motif.",
            },
        },
        "editableControls": [
            "maskPath",
            "darkFillColor",
            "mixFactor",
            "etchBumpStrength",
            "etchDepthIllusionMm",
            "roughnessDelta",
        ],
        "swapContract": "Each slot points to an external repository-relative mask and can be replaced without changing mesh data.",
    }
    for slot in manifest["slots"].values():
        slot["maskSha256"] = sha256(OUTPUT / slot["mask"])
    manifest["slots"]["Artwork_Lower"]["unknownMaskSha256"] = sha256(
        OUTPUT / manifest["slots"]["Artwork_Lower"]["unknownMask"]
    )
    (OUTPUT / "artwork-layers.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    foreground = {
        "upper": sum(value > 127 for value in upper_trace.getdata()) / (SIZE[0] * SIZE[1]),
        "lowerVisible": sum(value > 127 for value in lower_trace_visible.getdata()) / (620 * 380),
    }
    report = {
        "upperMaskSha256": sha256(OUTPUT / "artwork-upper-mask.png"),
        "lowerMaskSha256": sha256(OUTPUT / "artwork-lower-mask.png"),
        "lowerUnknownSha256": sha256(OUTPUT / "artwork-lower-occluded-unknown.png"),
        "foregroundCoverage": foreground,
        "independentMasks": sha256(OUTPUT / "artwork-upper-mask.png") != sha256(OUTPUT / "artwork-lower-mask.png"),
        "lowerUnknownDeclared": True,
        "pass": 0.12 < foreground["upper"] < 0.65
        and 0.08 < foreground["lowerVisible"] < 0.72,
    }
    (OUTPUT / "artwork-derivation-validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"color": color_report, "artwork": report}, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise RuntimeError("Artwork derivation validation failed.")


if __name__ == "__main__":
    main()
