#!/usr/bin/env python3
"""Derive blood-red masks with explicit exact, occluded, and reconstructed regions."""

from __future__ import annotations

import colorsys
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


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
SUPPLEMENTAL_SOURCES = [
    {
        "id": "chromehearts-official-ch-plus-matchstick-holder",
        "url": "https://www.chromehearts.com/scents/matchstick-holder/148310SLVXXX186.html",
        "page": "supplemental/chromehearts-ch-plus-matchstick-holder.html",
        "imageUrl": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw9d7b3726/img_products/hi-res/148310SLVXXX186_1.png?sw=1600&sh=2000",
        "image": "supplemental/chromehearts-ch-plus-matchstick-holder.png",
        "confirmedOfficialText": ".925 sterling silver; CH Plus top",
        "styleUse": "CH Plus lobe proportions and blackened-silver recess language",
    },
    {
        "id": "chromehearts-official-crosstail-water",
        "url": "https://www.chromehearts.com/baccarat/water/177732CRYXXX042.html",
        "page": "supplemental/chromehearts-crosstail-water.html",
        "imageUrl": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw2513c62d/img_products/hi-res/503177732CRYXXX042_0632.png?sw=1600&sh=2000",
        "image": "supplemental/chromehearts-crosstail-water.png",
        "confirmedOfficialText": "Baccarat for Chrome Hearts; CROSSTAIL design",
        "styleUse": "radial floral composition and pointed petal endings",
    },
    {
        "id": "chromehearts-official-stencil-dagger-socks",
        "url": "https://www.chromehearts.com/socks/stencil-socks/176354MB3XXX465.html",
        "page": "supplemental/chromehearts-stencil-dagger-socks.html",
        "imageUrl": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw35e5a211/img_products/hi-res/316176354MB3MED465_1.png?sw=1600&sh=2000",
        "image": "supplemental/chromehearts-stencil-dagger-socks.png",
        "confirmedOfficialText": "Stencil motif; embroidered dagger detail",
        "styleUse": "repeated CH Plus field and pointed dagger rhythm",
    },
]


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


def gothic_plus_mask(unknown_region: Image.Image) -> Image.Image:
    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)

    def plus(cx: int, cy: int, radius: int) -> None:
        neck = round(radius * 0.24)
        top_arm = [
            (-neck, 0),
            (-neck, -round(radius * 0.52)),
            (-round(radius * 0.46), -round(radius * 0.63)),
            (-round(radius * 0.28), -round(radius * 0.79)),
            (0, -radius),
            (round(radius * 0.28), -round(radius * 0.79)),
            (round(radius * 0.46), -round(radius * 0.63)),
            (neck, -round(radius * 0.52)),
            (neck, 0),
        ]
        for angle in (0, 90, 180, 270):
            radians = math.radians(angle)
            points = [
                (
                    cx + round(x * math.cos(radians) - y * math.sin(radians)),
                    cy + round(x * math.sin(radians) + y * math.cos(radians)),
                )
                for x, y in top_arm
            ]
            draw.polygon(points, fill=255)
        draw.ellipse((cx - neck, cy - neck, cx + neck, cy + neck), fill=255)

    plus(310, 150, 105)
    plus(170, 390, 76)
    plus(450, 390, 76)
    draw.arc((84, 228, 536, 640), 198, 342, fill=255, width=18)
    draw.arc((118, 262, 502, 608), 198, 342, fill=255, width=10)
    for cx, direction in ((122, -1), (498, 1)):
        for cy in (250, 330, 420, 505):
            draw.polygon([
                (cx, cy),
                (cx + direction * 64, cy - 34),
                (cx + direction * 40, cy + 12),
                (cx + direction * 70, cy + 42),
            ], fill=255)
    return ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(0.6)), unknown_region)


def write_supplemental_manifest() -> dict:
    records = []
    for source in SUPPLEMENTAL_SOURCES:
        page = OUTPUT / source["page"]
        image = OUTPUT / source["image"]
        records.append({
            **source,
            "pageSha256": sha256(page),
            "imageSha256": sha256(image),
            "origin": "external-primary-official",
            "publisher": "Chrome Hearts",
            "retrievedAt": "2026-08-24",
            "priority": "supplemental-only-after-exact-product-evidence",
            "notExactProductEvidence": True,
        })
    manifest = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 5,
        "policy": "Exact HALOOPLAYER/NXEDC/archived product imagery remains first priority. Official Chrome Hearts sources may guide only unreadable regions and never become exact-product claims.",
        "sources": records,
    }
    (OUTPUT / "supplemental-source-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def make_boundary_board(upper_trace: Image.Image, lower_direct: Image.Image, lower_unknown: Image.Image, lower_reconstructed: Image.Image) -> None:
    canvas = Image.new("RGB", (2200, 1400), (22, 26, 33))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=17)
    draw.text((60, 34), "GATE 07 REV 5 · ARTWORK SOURCE BOUNDARIES", fill=(244, 246, 250), font=title)
    draw.text((60, 82), "Exact-product evidence first. Official Chrome Hearts references fill only unreadable regions.", fill=(178, 187, 200), font=label)
    panels = [
        ("A · DIRECT EXACT-PRODUCT UPPER", upper_trace, (62, 126), (76, 202, 128)),
        ("A · DIRECT EXACT-PRODUCT LOWER", lower_direct, (592, 126), (76, 202, 128)),
        ("B · OCCLUDED / INCOMPLETE LOWER", lower_unknown, (1122, 126), (238, 184, 74)),
        ("C · CH-STYLE RECONSTRUCTED LOWER", lower_reconstructed, (1652, 126), (202, 98, 214)),
    ]
    for heading, mask, origin, tint in panels:
        thumb = ImageOps.contain(mask.convert("RGB"), (440, 760))
        alpha = ImageOps.grayscale(thumb)
        colored = Image.new("RGBA", thumb.size, (*tint, 0))
        colored.putalpha(alpha)
        frame = Image.new("RGBA", (460, 780), (38, 44, 54, 255))
        frame.alpha_composite(colored, ((460 - thumb.width) // 2, (780 - thumb.height) // 2))
        canvas.paste(frame.convert("RGB"), origin)
        draw.text((origin[0], 920), heading, fill=tint, font=label)
    draw.text((62, 975), "High confidence · full visible face · exact product", fill=(192, 200, 211), font=small)
    draw.text((592, 975), "Medium confidence · source-visible open end", fill=(192, 200, 211), font=small)
    draw.text((1122, 975), "No exact detail claim · hidden behind upper shell", fill=(192, 200, 211), font=small)
    draw.text((1652, 975), "Low confidence · official CH style · not exact trace", fill=(192, 200, 211), font=small)
    for index, source in enumerate(SUPPLEMENTAL_SOURCES):
        image = ImageOps.contain(Image.open(OUTPUT / source["image"]).convert("RGB"), (240, 260))
        x = 62 + index * 690
        canvas.paste(image, (x, 1080))
        draw.text((x + 258, 1100), source["id"], fill=(225, 229, 236), font=small)
        draw.text((x + 258, 1134), "PRIMARY OFFICIAL · SUPPLEMENTAL ONLY", fill=(202, 98, 214), font=small)
    canvas.save(OUTPUT / "artwork-source-boundary-board.png")


def main() -> None:
    supplemental_manifest = write_supplemental_manifest()
    upper = rectify(UPPER_SOURCE, UPPER_QUAD, SIZE)
    upper.save(OUTPUT / "upper-source-rectified.png")
    interior = capsule_mask(SIZE, 45)
    upper_trace = dark_trace(upper, interior)
    upper_trace.save(OUTPUT / "artwork-upper-mask.png")

    lower_visible = rectify(LOWER_SOURCE, LOWER_VISIBLE_QUAD, (620, 380))
    lower_visible.save(OUTPUT / "lower-visible-source-rectified.png")
    lower_trace_visible = dark_trace(lower_visible, capsule_mask((620, 380), 24))
    lower_direct = Image.new("L", SIZE, 0)
    lower_direct.paste(lower_trace_visible, (0, LOWER_VISIBLE_Y))
    lower_direct.save(OUTPUT / "artwork-lower-direct-trace-mask.png")
    lower_unknown = Image.new("L", SIZE, 0)
    ImageDraw.Draw(lower_unknown).rectangle((0, 0, 619, LOWER_VISIBLE_Y - 1), fill=255)
    lower_unknown = ImageChops.multiply(lower_unknown, interior)
    lower_unknown.save(OUTPUT / "artwork-lower-occluded-unknown.png")
    lower_reconstructed = gothic_plus_mask(lower_unknown)
    lower_reconstructed.save(OUTPUT / "artwork-lower-reconstructed-mask.png")
    lower_trace = ImageChops.lighter(lower_direct, lower_reconstructed)
    lower_trace.save(OUTPUT / "artwork-lower-mask.png")
    make_boundary_board(upper_trace, lower_direct, lower_unknown, lower_reconstructed)

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
        "materialRevision": 5,
        "geometryDigest": "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f",
        "slots": {
            "Artwork_Upper": {
                "mask": "artwork-upper-mask.png",
                "sourceAssetIds": ["slider-intake-obs-frame-01", "slider-intake-haloo-official-03"],
                "sourceQuadPixels": list(UPPER_QUAD),
                "coverage": "full-visible-face",
                "occludedOrReconstructed": False,
                "regions": [
                    {
                        "id": "upper-direct-exact-product",
                        "class": "directly-traced-exact-product",
                        "mask": "artwork-upper-mask.png",
                        "confidence": "high",
                        "sourceAssetIds": ["slider-intake-obs-frame-01", "slider-intake-haloo-official-03"],
                    }
                ],
            },
            "Artwork_Lower": {
                "mask": "artwork-lower-mask.png",
                "unknownMask": "artwork-lower-occluded-unknown.png",
                "sourceAssetIds": ["slider-intake-obs-frame-10"],
                "sourceQuadPixels": list(LOWER_VISIBLE_QUAD),
                "coverage": "source-visible-open-end-plus-labeled-style-reconstruction",
                "occludedOrReconstructed": True,
                "policy": "The source-visible exposed end is traced first. The hidden region remains explicitly occluded/incomplete, then receives a separate low-confidence Chrome Hearts-style reconstruction from archived official sources.",
                "regions": [
                    {
                        "id": "lower-direct-exact-product",
                        "class": "directly-traced-exact-product",
                        "mask": "artwork-lower-direct-trace-mask.png",
                        "normalizedY": [0.62, 1.0],
                        "confidence": "medium",
                        "sourceAssetIds": ["slider-intake-obs-frame-10"],
                    },
                    {
                        "id": "lower-occluded-incomplete",
                        "class": "occluded-incomplete",
                        "mask": "artwork-lower-occluded-unknown.png",
                        "normalizedY": [0.0, 0.62],
                        "confidence": "none-for-exact-detail",
                        "sourceAssetIds": ["slider-intake-obs-frame-10"],
                    },
                    {
                        "id": "lower-chrome-hearts-style-reconstructed",
                        "class": "chrome-hearts-style-reconstructed",
                        "mask": "artwork-lower-reconstructed-mask.png",
                        "normalizedY": [0.0, 0.62],
                        "confidence": "low",
                        "sourceAssetIds": [source["id"] for source in supplemental_manifest["sources"]],
                        "allowedLanguage": ["classic-gothic-cross", "fleur-floral", "pointed-arch", "blackened-silver"],
                        "notExactProductTrace": True,
                    },
                ],
            },
        },
        "sourcePriority": [
            "exact-product-direct-trace",
            "explicit-occluded-incomplete-boundary",
            "official-Chrome-Hearts-style-reconstruction-only-where-unreadable",
        ],
        "supplementalSourceManifest": "supplemental-source-manifest.json",
        "supplementalSourceManifestSha256": sha256(OUTPUT / "supplemental-source-manifest.json"),
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
        for region in slot["regions"]:
            region["maskSha256"] = sha256(OUTPUT / region["mask"])
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
        "lowerDirectSha256": sha256(OUTPUT / "artwork-lower-direct-trace-mask.png"),
        "lowerReconstructedSha256": sha256(OUTPUT / "artwork-lower-reconstructed-mask.png"),
        "foregroundCoverage": foreground,
        "independentMasks": sha256(OUTPUT / "artwork-upper-mask.png") != sha256(OUTPUT / "artwork-lower-mask.png"),
        "lowerUnknownDeclared": True,
        "sourceBoundaryClasses": sorted({
            region["class"]
            for slot in manifest["slots"].values()
            for region in slot["regions"]
        }),
        "exactProductFirst": manifest["sourcePriority"][0] == "exact-product-direct-trace",
        "reconstructionSubsetOfUnknown": all(
            unknown > 0 or reconstructed == 0
            for unknown, reconstructed in zip(lower_unknown.getdata(), lower_reconstructed.getdata())
        ),
        "directAndReconstructedDisjoint": all(
            direct == 0 or reconstructed == 0
            for direct, reconstructed in zip(lower_direct.getdata(), lower_reconstructed.getdata())
        ),
        "supplementalSourcesOfficialAndSeparate": all(
            source["origin"] == "external-primary-official"
            and source["notExactProductEvidence"]
            for source in supplemental_manifest["sources"]
        ),
        "pass": 0.12 < foreground["upper"] < 0.65
        and 0.08 < foreground["lowerVisible"] < 0.72,
    }
    report["pass"] = report["pass"] and report["exactProductFirst"] and report["reconstructionSubsetOfUnknown"] and report["directAndReconstructedDisjoint"] and report["supplementalSourcesOfficialAndSeparate"]
    (OUTPUT / "artwork-derivation-validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"color": color_report, "artwork": report}, ensure_ascii=False, indent=2))
    if not report["pass"]:
        raise RuntimeError("Artwork derivation validation failed.")


if __name__ == "__main__":
    main()
