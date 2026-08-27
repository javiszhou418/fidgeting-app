#!/usr/bin/env python3
"""Derive a reproducible visual-trace mask from the exact NXEDC face closeup."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageOps


OUTPUT = Path(__file__).resolve().parent
SOURCE = OUTPUT.parents[1] / "01-intake/rev-002/external-nxedc/reference-01.jpg"
MASK = OUTPUT / "source-derived-motif-visual-trace.png"
METADATA = OUTPUT / "motif-trace-provenance.json"
SOURCE_ASSET_ID = "slider-intake-nxedc-ref-01"
SOURCE_CROP_NORMALIZED = [0.2890625, 0.142578125, 0.7109375, 0.8369140625]
OUTPUT_SIZE = (620, 1000)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capsule_mask(size: tuple[int, int], inset: int) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    radius = (width - inset * 2) // 2
    pixels = mask.load()
    left = inset
    right = width - inset - 1
    top_center = inset + radius
    bottom_center = height - inset - radius - 1
    for y in range(height):
        for x in range(width):
            if left <= x <= right and top_center <= y <= bottom_center:
                pixels[x, y] = 255
                continue
            center_y = top_center if y < top_center else bottom_center
            if (x - width / 2) ** 2 + (y - center_y) ** 2 <= radius**2:
                pixels[x, y] = 255
    return mask


def main() -> None:
    source_hash_before = sha256(SOURCE)
    source = Image.open(SOURCE).convert("RGB")
    width, height = source.size
    crop_box = (
        round(SOURCE_CROP_NORMALIZED[0] * width),
        round(SOURCE_CROP_NORMALIZED[1] * height),
        round(SOURCE_CROP_NORMALIZED[2] * width),
        round(SOURCE_CROP_NORMALIZED[3] * height),
    )
    crop = source.crop(crop_box).resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(crop)
    local_mean = gray.filter(ImageFilter.GaussianBlur(12))
    relative_dark = ImageChops.subtract(local_mean, gray)
    relative_mask = relative_dark.point(lambda value: 255 if value >= 20 else 0)
    absolute_mask = gray.point(lambda value: 255 if value <= 70 else 0)
    combined = ImageChops.lighter(relative_mask, absolute_mask)
    combined = combined.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MedianFilter(3))
    interior = capsule_mask(OUTPUT_SIZE, inset=45)
    combined = ImageChops.multiply(combined, interior)

    # Remove isolated photographic noise while preserving the linked Gothic floral linework.
    combined = combined.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
    combined.save(MASK)
    source_hash_after = sha256(SOURCE)
    if source_hash_before != source_hash_after:
        raise RuntimeError("Exact source changed while deriving motif trace.")

    dark_pixels = sum(1 for value in combined.getdata() if value > 127)
    coverage = dark_pixels / (OUTPUT_SIZE[0] * OUTPUT_SIZE[1])
    report = {
        "schemaVersion": 1,
        "kind": "visual-trace-not-production-vector",
        "sourceAssetIds": [SOURCE_ASSET_ID],
        "sourcePath": str(SOURCE.relative_to(OUTPUT.parents[7])),
        "sourceSha256": source_hash_before,
        "sourceCropNormalized": SOURCE_CROP_NORMALIZED,
        "sourceCropPixels": list(crop_box),
        "recipe": {
            "outputSizePx": list(OUTPUT_SIZE),
            "grayscale": "Pillow ImageOps.grayscale",
            "localContrast": "GaussianBlur radius 12; localMean - gray >= 20",
            "absoluteDark": "gray <= 70",
            "interiorMask": "analytic capsule inset 45 px",
            "cleanup": "MaxFilter 3; MedianFilter 3; MinFilter 3; MaxFilter 3",
        },
        "outputPath": MASK.name,
        "outputSha256": sha256(MASK),
        "foregroundCoverage": round(coverage, 6),
        "limitations": [
            "The mask is a visual trace from a raster closeup, not an exact production vector.",
            "Dark low-luma substrate regions can enter the trace; the Blender shader uses restrained strength.",
            "No hidden manufacturing path, engraving depth, or production tolerance is asserted.",
        ],
        "pass": 0.11 <= coverage <= 0.48,
    }
    METADATA.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(f"Motif trace coverage out of range: {coverage:.4f}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
