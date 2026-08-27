#!/usr/bin/env python3
"""Reconstruct a distinct lower artwork mask from user frames."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
REPO = OUT.parents[7]
SIZE = (620, 1000)
SOURCES = {
    "user-frame-10": {
        "assetId": "slider-intake-obs-frame-10",
        "path": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-10.jpg",
        "quad": [[224, 584], [402, 582], [410, 704], [222, 704]],
        "visibleTargetY": [360, 965],
        "confidence": "primary-direct",
    },
    "user-frame-03": {
        "assetId": "slider-intake-obs-frame-03",
        "path": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-03.jpg",
        "quad": [[281, 567], [416, 565], [419, 694], [278, 695]],
        "visibleTargetY": [360, 965],
        "confidence": "secondary-direct",
    },
    "user-frame-05": {
        "assetId": "slider-intake-obs-frame-05",
        "path": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-05.jpg",
        "quad": [[250, 665], [420, 660], [423, 785], [248, 785]],
        "visibleTargetY": [400, 965],
        "confidence": "secondary-direct-motion-soft",
    },
    "official-frame-08": {
        "assetId": "slider-intake-haloo-official-08",
        "path": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/08.png",
        "quad": [[198, 670], [464, 666], [468, 870], [195, 872]],
        "visibleTargetY": [360, 965],
        "confidence": "reconstruction-language-only",
    },
}
UPPER_MASK = OUT.parent / "rev-007/artwork-upper-mask.png"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def font(size, bold=False):
    for path in ["/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/STHeiti Light.ttc"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=1 if bold else 0)
    return ImageFont.load_default()


def capsule_mask(width=620, height=1000, inset=52):
    mask = np.zeros((height, width), np.uint8)
    cv2.rectangle(mask, (inset, height // 2), (width - inset, height // 2), 255, -1)
    radius = (width - 2 * inset) // 2
    cv2.rectangle(mask, (inset, radius), (width - inset, height - radius), 255, -1)
    cv2.circle(mask, (width // 2, radius), radius, 255, -1)
    cv2.circle(mask, (width // 2, height - radius), radius, 255, -1)
    return mask


def rectify(source):
    image = cv2.imread(str(source["path"]), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(source["path"])
    source_quad = np.float32(source["quad"])
    y1, y2 = source["visibleTargetY"]
    destination = np.float32([[0, y1], [SIZE[0] - 1, y1], [SIZE[0] - 1, y2], [0, y2]])
    matrix = cv2.getPerspectiveTransform(source_quad, destination)
    warped = cv2.warpPerspective(image, matrix, SIZE, flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    source_coverage = np.ones(image.shape[:2], np.uint8) * 255
    coverage = cv2.warpPerspective(source_coverage, matrix, SIZE, flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT)
    return warped, coverage, matrix


def dark_artwork_score(image):
    b, g, r = cv2.split(image.astype(np.float32))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    redness = r - np.maximum(g, b)
    dark = np.clip((122.0 - gray) / 90.0, 0, 1)
    not_red = np.clip((58.0 - redness) / 58.0, 0, 1)
    score = dark * (0.45 + 0.55 * not_red)
    score = cv2.GaussianBlur(score, (0, 0), 1.2)
    return score


def save_gray(path, image):
    cv2.imwrite(str(path), image)


def build_board(rectified, direct_mask, reconstructed_mask, final_mask):
    board = Image.new("RGB", (2440, 1720), (7, 10, 14))
    draw = ImageDraw.Draw(board)
    draw.text((60, 45), "下片图案来源拆分｜实拍直见 vs 遮挡重建", font=font(50, True), fill=(246, 248, 251))
    draw.text((60, 108), "绿色只表示用户实拍中直接可见；橙色只表示遮挡区的官方哥特语言重建，不宣称精确描摹。", font=font(27), fill=(183, 194, 208))
    x = 60
    for key in ["user-frame-10", "user-frame-03", "user-frame-05", "official-frame-08"]:
        rgb = cv2.cvtColor(rectified[key], cv2.COLOR_BGR2RGB)
        panel = Image.fromarray(rgb).resize((520, 760), Image.Resampling.LANCZOS)
        board.paste(panel, (x, 180))
        label = "用户直接来源" if key.startswith("user") else "仅作遮挡区重建语言"
        draw.text((x, 960), f"{key}｜{label}", font=font(23, True), fill=(221, 227, 235))
        x += 590
    masks = [
        (direct_mask, "直接可见区域 Mask", (58, 218, 132)),
        (reconstructed_mask, "遮挡区重建 Mask", (236, 148, 55)),
        (final_mask, "最终独立下片 Mask", (238, 240, 244)),
    ]
    x = 160
    for mask, label, color in masks:
        image = np.zeros((1000, 620, 3), np.uint8)
        image[mask > 0] = color
        panel = Image.fromarray(image).resize((420, 620), Image.Resampling.LANCZOS)
        board.paste(panel, (x, 1040))
        draw.text((x, 1668), label, font=font(25, True), fill=color)
        x += 700
    path = OUT / "lower-artwork-direct-vs-reconstructed.png"
    board.save(path)
    return path


def main():
    for source in SOURCES.values():
        if not source["path"].exists():
            raise FileNotFoundError(source["path"])
    rectified = {}
    coverage = {}
    transforms = {}
    scores = {}
    interior = capsule_mask()
    for key, source in SOURCES.items():
        warped, source_coverage, matrix = rectify(source)
        rectified[key] = warped
        coverage[key] = source_coverage
        transforms[key] = matrix.tolist()
        cv2.imwrite(str(OUT / f"lower-rectified-{key}.png"), warped)
        scores[key] = dark_artwork_score(warped) * (source_coverage.astype(np.float32) / 255.0)

    direct_score = (
        scores["user-frame-10"] * 0.56
        + scores["user-frame-03"] * 0.29
        + scores["user-frame-05"] * 0.15
    )
    direct_visibility = np.zeros((1000, 620), np.float32)
    direct_visibility[360:965] = 1.0
    direct_mask = ((direct_score >= 0.48) & (direct_visibility > 0) & (interior > 0)).astype(np.uint8) * 255
    direct_mask = cv2.morphologyEx(direct_mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    direct_mask = cv2.morphologyEx(direct_mask, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))

    official_visible = scores["official-frame-08"][360:965]
    official_score = cv2.resize(official_visible, (620, 360), interpolation=cv2.INTER_AREA)
    reconstruction_zone = np.zeros((1000, 620), np.uint8)
    reconstruction_zone[:360] = 255
    reconstructed_canvas = np.zeros((1000, 620), np.float32)
    reconstructed_canvas[:360] = official_score
    reconstructed_mask = ((reconstructed_canvas >= 0.78) & (reconstruction_zone > 0) & (interior > 0)).astype(np.uint8) * 255
    reconstructed_mask = cv2.morphologyEx(reconstructed_mask, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))

    final_mask = cv2.max(direct_mask, reconstructed_mask)
    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    final_path = OUT / "artwork-lower-mask-r010.png"
    direct_path = OUT / "artwork-lower-direct-mask-r010.png"
    reconstructed_path = OUT / "artwork-lower-reconstructed-mask-r010.png"
    save_gray(final_path, final_mask)
    save_gray(direct_path, direct_mask)
    save_gray(reconstructed_path, reconstructed_mask)

    provenance = np.zeros((1000, 620, 3), np.uint8)
    provenance[direct_mask > 0] = (58, 218, 132)
    provenance[reconstructed_mask > 0] = (236, 148, 55)
    provenance_path = OUT / "artwork-lower-provenance-map-r010.png"
    cv2.imwrite(str(provenance_path), cv2.cvtColor(provenance, cv2.COLOR_RGB2BGR))
    board = build_board(rectified, direct_mask, reconstructed_mask, final_mask)

    upper = cv2.imread(str(UPPER_MASK), cv2.IMREAD_GRAYSCALE)
    lower = cv2.imread(str(final_path), cv2.IMREAD_GRAYSCALE)
    if upper is None or lower is None:
        raise RuntimeError("Missing upper or lower mask.")
    difference_fraction = float(np.mean((upper > 127) != (lower > 127)))
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 10,
        "method": "perspective-rectified multi-frame dark-line segmentation with explicit provenance zones",
        "sources": {
            key: {
                "assetId": source["assetId"],
                "path": str(source["path"].relative_to(REPO)),
                "sourceQuadPx": source["quad"],
                "visibleTargetY": source["visibleTargetY"],
                "confidence": source["confidence"],
                "homography": transforms[key],
            }
            for key, source in SOURCES.items()
        },
        "directTrace": {
            "sourceAssetIds": ["slider-intake-obs-frame-10", "slider-intake-obs-frame-03", "slider-intake-obs-frame-05"],
            "targetRegionY": [360, 965],
            "claim": "Only pixels directly visible in user frames; source blur and glare limit stroke precision.",
            "pixelCount": int((direct_mask > 0).sum()),
        },
        "reconstruction": {
            "sourceAssetIds": ["slider-intake-haloo-official-08"],
            "targetRegionY": [0, 360],
            "claim": "Occluded upper region uses authorized official gothic reference language only; not an exact trace of the red user variant.",
            "pixelCount": int((reconstructed_mask > 0).sum()),
        },
        "mask": {
            "sizePx": list(SIZE),
            "upperSha256": sha256(UPPER_MASK),
            "lowerSha256": sha256(final_path),
            "hashesDistinct": sha256(UPPER_MASK) != sha256(final_path),
            "binaryDifferenceFraction": round(difference_fraction, 6),
            "independentlyEditable": True,
        },
        "artifacts": {
            path.name: sha256(path)
            for path in [final_path, direct_path, reconstructed_path, provenance_path, board]
        },
        "pass": (
            sha256(UPPER_MASK) != sha256(final_path)
            and difference_fraction >= 0.20
            and int((direct_mask > 0).sum()) >= 12000
            and int((reconstructed_mask > 0).sum()) >= 3000
        ),
    }
    (OUT / "lower-artwork-provenance.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(f"Lower artwork reconstruction failed: {report}")


if __name__ == "__main__":
    main()
