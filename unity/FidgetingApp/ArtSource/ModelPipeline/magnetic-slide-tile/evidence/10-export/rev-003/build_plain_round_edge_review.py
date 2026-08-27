#!/usr/bin/env python3
"""Build the two plain-Chinese Gate 10 review images from actual matched renders."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
BEFORE = ROOT / "plain-full-before.png"
AFTER = ROOT / "plain-full-after.png"
LOCATION = ROOT / "round-edge-location.png"
COMPARISON = ROOT / "round-edge-before-after.png"
REPORT = ROOT / "plain-review-image-validation.json"
ROI = (540, 1040, 1200, 1700)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size=size,
        index=1 if bold else 0,
    )


def contain(image: Image.Image, size: tuple[int, int]) -> tuple[Image.Image, float]:
    fitted = ImageOps.contain(image, size, Image.Resampling.LANCZOS)
    return fitted, fitted.width / image.width


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
    draw.line((start, end), fill=color, width=12)
    direction = np.array(start, dtype=float) - np.array(end, dtype=float)
    direction /= np.linalg.norm(direction)
    perpendicular = np.array((-direction[1], direction[0]))
    tip = np.array(end, dtype=float)
    left = tip + direction * 42 + perpendicular * 22
    right = tip + direction * 42 - perpendicular * 22
    draw.polygon([tuple(tip), tuple(left), tuple(right)], fill=color)


def make_location(after: Image.Image) -> dict:
    canvas = Image.new("RGB", (2600, 1700), (13, 15, 17))
    draw = ImageDraw.Draw(canvas)
    draw.text((90, 55), "只看这里：前端圆弧侧边", fill=(245, 244, 239), font=font(68, True))
    draw.text((92, 145), "橙色框里的圆边，是这次检查的位置。", fill=(180, 181, 177), font=font(36))
    fitted, scale = contain(after, (2360, 1330))
    x = (canvas.width - fitted.width) // 2
    y = 270 + (1330 - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    mapped = (
        round(x + ROI[0] * scale),
        round(y + ROI[1] * scale),
        round(x + ROI[2] * scale),
        round(y + ROI[3] * scale),
    )
    draw.rounded_rectangle(mapped, radius=22, outline=(255, 128, 48), width=14)
    label = (1650, 470)
    draw.rounded_rectangle((label[0] - 30, label[1] - 22, label[0] + 720, label[1] + 90), radius=22, fill=(22, 24, 27))
    draw.text(label, "这里的亮带要一路连续", fill=(255, 167, 92), font=font(39, True))
    arrow(draw, (label[0] + 80, label[1] + 115), (mapped[2] - 30, mapped[1] + 55), (255, 128, 48))
    canvas.save(LOCATION)
    return {"mappedRoiPx": list(mapped), "scale": scale}


def make_comparison(before: Image.Image, after: Image.Image) -> None:
    canvas = Image.new("RGB", (3200, 1800), (13, 15, 17))
    draw = ImageDraw.Draw(canvas)
    draw.text((90, 48), "同一个位置，放大约 4 倍", fill=(245, 244, 239), font=font(64, True))
    draw.text((92, 132), "两张图使用完全相同的角度和光线。", fill=(180, 181, 177), font=font(34))
    crops = [before.crop(ROI), after.crop(ROI)]
    labels = ["修复前（实际）：差别很小", "修复后：亮带连续"]
    label_colors = [(190, 190, 187), (255, 159, 78)]
    for index, (crop, label, color) in enumerate(zip(crops, labels, label_colors)):
        x0 = 80 + index * 1580
        draw.rounded_rectangle((x0, 230, x0 + 1500, 1450), radius=24, fill=(2, 3, 5), outline=(66, 69, 73), width=3)
        fitted, _ = contain(crop, (1440, 1120))
        canvas.paste(fitted, (x0 + 30, 265 + (1120 - fitted.height) // 2))
        draw.text((x0 + 34, 1375), label, fill=color, font=font(40, True))
    right_x = 1660
    points = [(right_x + 240, 1060), (right_x + 420, 1110), (right_x + 620, 1145), (right_x + 840, 1164)]
    draw.line(points, fill=(255, 139, 54), width=10, joint="curve")
    arrow(draw, points[-2], points[-1], (255, 139, 54))
    draw.text((right_x + 760, 1200), "亮带一路连续", fill=(255, 169, 98), font=font(34, True))
    draw.rounded_rectangle((80, 1510, 3120, 1730), radius=24, fill=(24, 27, 31))
    draw.text((120, 1545), "实际前后差异很小，所以不伪造“修复前一格一格”的画面。", fill=(235, 234, 228), font=font(39, True))
    draw.text((120, 1607), "之前明显分段的是另一张非外观图，现已从主评审移除。", fill=(203, 204, 200), font=font(34))
    draw.text((120, 1662), "上、下面保持平；只有圆弧侧边需要看起来顺滑。", fill=(203, 204, 200), font=font(34))
    canvas.save(COMPARISON)


def main() -> None:
    before = Image.open(BEFORE).convert("RGB")
    after = Image.open(AFTER).convert("RGB")
    before_array = np.asarray(before)
    after_array = np.asarray(after)
    difference = np.abs(before_array.astype(np.int16) - after_array.astype(np.int16)).mean(axis=2)
    roi_difference = difference[ROI[1] : ROI[3], ROI[0] : ROI[2]]
    location = make_location(after)
    make_comparison(before, after)
    checks = {
        "sourceImages3200x1800": before.size == after.size == (3200, 1800),
        "identicalCropCoordinates": True,
        "cropAtLeast3xInDefaultBoard": 1500 / ((2360 / 3200) * (ROI[2] - ROI[0])) >= 3.0,
        "actualDifferenceIsSubtle": float(np.percentile(roi_difference, 99)) <= 2.0,
        "plainLocationImageExists": LOCATION.exists(),
        "plainComparisonImageExists": COMPARISON.exists(),
        "userImagesHighResolution": Image.open(LOCATION).width >= 2048 and Image.open(COMPARISON).width >= 2048,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "reviewRevision": 3,
        "roiSourcePixels": list(ROI),
        "locationMapping": location,
        "actualBeforeAfterDifference": {
            "meanRgbLevels": round(float(roi_difference.mean()), 6),
            "p99RgbLevels": round(float(np.percentile(roi_difference, 99)), 6),
            "maximumRgbLevels": round(float(roi_difference.max()), 6),
            "visuallyObvious": False,
        },
        "honestyPolicy": "The actual rev 1/rev 2 difference is too subtle for a truthful 'before was faceted' claim. The review uses matched neutral continuity images and states that fact.",
        "defaultReviewAssets": [LOCATION.name, COMPARISON.name],
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Plain Gate 10 review image validation failed.")


if __name__ == "__main__":
    main()
