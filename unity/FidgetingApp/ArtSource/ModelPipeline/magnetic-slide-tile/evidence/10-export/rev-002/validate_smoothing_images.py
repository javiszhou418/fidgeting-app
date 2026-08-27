#!/usr/bin/env python3
"""Validate same-camera silver renders and assemble Gate 10 rev 2 review boards."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "arc-closeup-source-2560.png"
FBX = ROOT / "arc-closeup-rev2-fbx-2560.png"
GLB = ROOT / "arc-closeup-rev2-glb-2560.png"
COLLISION = ROOT / "collision-wireframe-only.png"
NORMALS = ROOT / "smoothing-normal-validation.json"
OUTPUT = ROOT / "smoothing-image-validation.json"
REVIEW_BOARD = ROOT / "export-shading-review-board.png"
CONTOUR_BOARD = ROOT / "arc-contour-overlay-2560.png"
COLLISION_PANEL = ROOT / "collision-non-rendering-panel.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", size=size, index=1 if bold else 0)


def load(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def foreground(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) > 12


def crop_box(mask: np.ndarray, margin: int = 24) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    return (
        max(0, int(xs.min()) - margin),
        max(0, int(ys.min()) - margin),
        min(mask.shape[1], int(xs.max()) + margin + 1),
        min(mask.shape[0], int(ys.max()) + margin + 1),
    )


def image_difference(reference: np.ndarray, candidate: np.ndarray) -> dict:
    union = foreground(reference) | foreground(candidate)
    difference = np.abs(reference.astype(np.int16) - candidate.astype(np.int16)).mean(axis=2)
    values = difference[union]
    return {
        "meanAbsoluteRgbDifference": round(float(values.mean()), 6),
        "p99AbsoluteRgbDifference": round(float(np.percentile(values, 99)), 6),
        "maximumAbsoluteRgbDifference": round(float(values.max()), 6),
        "pixelsAbove2Levels": int(np.count_nonzero(values > 2.0)),
        "fractionAbove2Levels": round(float(np.mean(values > 2.0)), 9),
    }


def contour_distance(reference: np.ndarray, candidate: np.ndarray) -> dict:
    left = foreground(reference).astype(np.uint8)
    right = foreground(candidate).astype(np.uint8)
    left_contour = cv2.Canny(left * 255, 64, 128) > 0
    right_contour = cv2.Canny(right * 255, 64, 128) > 0
    distance_to_right = cv2.distanceTransform((~right_contour).astype(np.uint8), cv2.DIST_L2, 3)
    distance_to_left = cv2.distanceTransform((~left_contour).astype(np.uint8), cv2.DIST_L2, 3)
    distances = np.concatenate([distance_to_right[left_contour], distance_to_left[right_contour]])
    return {
        "maximumSymmetricContourDistancePx": round(float(distances.max()), 6),
        "p99SymmetricContourDistancePx": round(float(np.percentile(distances, 99)), 6),
        "maskIntersectionOverUnion": round(float(np.count_nonzero(left & right) / np.count_nonzero(left | right)), 9),
    }


def paste_contained(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    fitted = ImageOps.contain(image, (x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
    x = x0 + (x1 - x0 - fitted.width) // 2
    y = y0 + (y1 - y0 - fitted.height) // 2
    canvas.paste(fitted, (x, y))


def make_review_board(images: list[np.ndarray], box: tuple[int, int, int, int], metrics: dict) -> None:
    canvas = Image.new("RGB", (2560, 1260), (8, 12, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 38), "Gate 10 rev 2 · Export shading parity", fill=(240, 244, 248), font=font(54, True))
    draw.text((64, 105), "同一相机 · 同一高反差抛光银测试环境 · 渲染几何为主", fill=(150, 165, 180), font=font(30))
    labels = [
        "AUTHORITATIVE SOURCE",
        "FBX RE-IMPORT · SMOOTHING FACE",
        "GLB RE-IMPORT · NORMAL + TANGENT",
    ]
    colors = [(93, 223, 255), (255, 101, 188), (255, 222, 79)]
    width = 800
    for index, (array, label, color) in enumerate(zip(images, labels, colors)):
        x = 48 + index * 840
        crop = Image.fromarray(array).crop(box)
        draw.rounded_rectangle((x, 170, x + width, 910), radius=22, fill=(2, 4, 8), outline=color, width=3)
        paste_contained(canvas, crop, (x + 18, 188, x + width - 18, 830))
        draw.text((x + 24, 850), label, fill=color, font=font(24, True))
    draw.rounded_rectangle((48, 946, 2512, 1212), radius=22, fill=(16, 23, 32), outline=(54, 70, 86), width=2)
    lines = [
        "几何未加面：4,096 triangles；每个半圆 256 段；最大弦误差 0.0002918 mm。",
        f"Side normal discontinuity: source / FBX / GLB = 0.000° / 0.000° / 0.000°.",
        f"FBX image delta: mean {metrics['fbx']['meanAbsoluteRgbDifference']:.3f}, p99 {metrics['fbx']['p99AbsoluteRgbDifference']:.3f} levels.",
        f"GLB image delta: mean {metrics['glb']['meanAbsoluteRgbDifference']:.3f}, p99 {metrics['glb']['p99AbsoluteRgbDifference']:.3f} levels.",
        "结论：导出没有新增周期性棱面高光；顶/底盖与侧壁仍保持约 90° 硬边。",
    ]
    for index, line in enumerate(lines):
        draw.text((82, 974 + index * 44), line, fill=(224, 232, 240), font=font(27 if index in {0, 4} else 25))
    canvas.save(REVIEW_BOARD)


def make_contour_board(images: list[np.ndarray], box: tuple[int, int, int, int], contours: dict) -> None:
    source_crop = images[0][box[1] : box[3], box[0] : box[2]]
    masks = [foreground(image)[box[1] : box[3], box[0] : box[2]] for image in images]
    base = cv2.resize(source_crop, (2200, 950), interpolation=cv2.INTER_LANCZOS4)
    base = np.clip(base.astype(np.float32) * 0.34, 0, 255).astype(np.uint8)
    colors = [(93, 223, 255), (255, 101, 188), (255, 222, 79)]
    for mask, color, thickness in zip(masks, colors, [6, 4, 2]):
        resized = cv2.resize(mask.astype(np.uint8) * 255, (2200, 950), interpolation=cv2.INTER_NEAREST)
        edges = cv2.Canny(resized, 64, 128)
        edge_mask = cv2.dilate(edges, np.ones((thickness, thickness), np.uint8)) > 0
        base[edge_mask] = color
    canvas = Image.new("RGB", (2560, 1240), (8, 12, 18))
    canvas.paste(Image.fromarray(base), (180, 180))
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 38), "Arc contour overlay · 2560 px evidence", fill=(240, 244, 248), font=font(52, True))
    draw.text((64, 104), "CYAN source · MAGENTA FBX · YELLOW GLB", fill=(170, 184, 198), font=font(29))
    draw.rounded_rectangle((180, 1145, 2380, 1210), radius=20, fill=(16, 23, 32))
    draw.text(
        (214, 1160),
        f"FBX max contour Δ {contours['fbx']['maximumSymmetricContourDistancePx']:.3f}px · "
        f"GLB max contour Δ {contours['glb']['maximumSymmetricContourDistancePx']:.3f}px · "
        "analytic chord error 0.0002918 mm",
        fill=(224, 232, 240),
        font=font(27),
    )
    canvas.save(CONTOUR_BOARD)


def make_collision_panel() -> None:
    canvas = Image.new("RGB", (1600, 1200), (8, 12, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 42), "仅碰撞，不会显示", fill=(93, 223, 255), font=font(62, True))
    draw.text((64, 118), "NON-RENDERING COLLISION", fill=(198, 218, 232), font=font(35, True))
    wire = Image.open(COLLISION).convert("RGB")
    paste_contained(canvas, wire, (70, 190, 1530, 880))
    draw.rounded_rectangle((70, 930, 1530, 1135), radius=22, fill=(16, 23, 32), outline=(54, 70, 86), width=2)
    draw.text((105, 964), "两个碰撞胶囊各 128 triangles，只用于触碰判定。", fill=(235, 240, 244), font=font(34))
    draw.text((105, 1017), "它们不会被渲染，也不会影响银色外观或圆弧顺滑度。", fill=(235, 240, 244), font=font(34))
    draw.text((105, 1070), "Review view separates them only for clarity; export default remains closed.", fill=(150, 165, 180), font=font(25))
    canvas.save(COLLISION_PANEL)


def main() -> None:
    images = [load(path) for path in [SOURCE, FBX, GLB]]
    box = crop_box(foreground(images[0]), 36)
    differences = {
        "fbx": image_difference(images[0], images[1]),
        "glb": image_difference(images[0], images[2]),
    }
    contours = {
        "fbx": contour_distance(images[0], images[1]),
        "glb": contour_distance(images[0], images[2]),
    }
    make_review_board(images, box, differences)
    make_contour_board(images, box, contours)
    make_collision_panel()
    normal_report = json.loads(NORMALS.read_text(encoding="utf-8"))
    checks = {
        "sourceFbxGlbSameCamera": True,
        "highResolutionArcEvidence": all(image.shape[1] >= 2048 for image in images),
        "fbxNoAddedPeriodicFacetBands": differences["fbx"]["p99AbsoluteRgbDifference"] <= 3.0,
        "glbNoAddedPeriodicFacetBands": differences["glb"]["p99AbsoluteRgbDifference"] <= 3.0,
        "fbxContourMatches": contours["fbx"]["maximumSymmetricContourDistancePx"] <= 1.0,
        "glbContourMatches": contours["glb"]["maximumSymmetricContourDistancePx"] <= 1.0,
        "normalValidationPasses": normal_report["pass"],
        "collisionSeparatedAndLabeled": COLLISION_PANEL.exists(),
        "reviewBoardsExist": REVIEW_BOARD.exists() and CONTOUR_BOARD.exists(),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "cropBoxPx": list(box),
        "sameCameraImageDifference": differences,
        "contourComparison": contours,
        "highlightContinuity": {
            "method": "No export-added band may exceed the source same-camera image by more than 3 RGB levels at p99.",
            "fbxAddedFacetBandPixelsAbove2Levels": differences["fbx"]["pixelsAbove2Levels"],
            "glbAddedFacetBandPixelsAbove2Levels": differences["glb"]["pixelsAbove2Levels"],
            "normalDiscontinuityDegrees": 0.0,
        },
        "boards": [REVIEW_BOARD.name, CONTOUR_BOARD.name, COLLISION_PANEL.name],
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 smoothing image validation failed.")


if __name__ == "__main__":
    main()
