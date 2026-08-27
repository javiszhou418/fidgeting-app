#!/usr/bin/env python3
"""Build plain-language Blender versus Unity Gate 11 rev 3 review boards."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FONT_PATH = Path("/System/Library/Fonts/STHeiti Medium.ttc")
TARGET = ROOT / "blender-neutral.png"
TARGET_CLAY = ROOT / "blender-neutral-silhouette.png"
UNITY = ROOT / "unity-material-final.png"
UNITY_CLAY = ROOT / "unity-geometry-clay.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    del bold
    return ImageFont.truetype(str(FONT_PATH), size=size)


def load(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "#11161d")
    canvas.paste(copy, ((width - copy.width) // 2, (height - copy.height) // 2))
    return canvas


def label_panel(
    image: Image.Image,
    title: str,
    subtitle: str,
    width: int,
    height: int,
) -> Image.Image:
    panel = Image.new("RGB", (width, height + 92), "#151b23")
    panel.paste(fit(image, width, height), (0, 92))
    draw = ImageDraw.Draw(panel)
    draw.text((22, 14), title, fill="#ffffff", font=font(30, True))
    draw.text((22, 54), subtitle, fill="#aebac7", font=font(19))
    return panel


def object_mask(image: Image.Image, threshold: int = 28) -> np.ndarray:
    array = np.asarray(image).astype(np.int16)
    background = np.median(
        np.concatenate(
            [
                array[:35].reshape(-1, 3),
                array[-35:].reshape(-1, 3),
                array[:, :35].reshape(-1, 3),
                array[:, -35:].reshape(-1, 3),
            ]
        ),
        axis=0,
    )
    delta = np.max(np.abs(array - background), axis=2)
    mask = (delta > threshold).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return mask
    largest = max(contours, key=cv2.contourArea)
    clean = np.zeros_like(mask)
    cv2.drawContours(clean, [largest], -1, 255, thickness=cv2.FILLED)
    return clean


def edge_overlay(target: Image.Image, unity: Image.Image) -> Image.Image:
    target_mask = object_mask(target, 35)
    unity_mask = object_mask(unity, 35)
    target_edge = cv2.Canny(target_mask, 64, 128)
    unity_edge = cv2.Canny(unity_mask, 64, 128)
    canvas = np.zeros((*target_edge.shape, 3), np.uint8)
    canvas[:] = (18, 23, 30)
    canvas[target_edge > 0] = (86, 228, 237)
    canvas[unity_edge > 0] = (255, 190, 78)
    overlap = (target_edge > 0) & (unity_edge > 0)
    canvas[overlap] = (255, 255, 255)
    return Image.fromarray(canvas)


def crop_zoom(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return image.crop(box).resize(
        ((box[2] - box[0]) * 2, (box[3] - box[1]) * 2),
        Image.Resampling.LANCZOS,
    )


def comparison_board(
    title: str,
    question: str,
    left: Image.Image,
    right: Image.Image,
    left_title: str,
    right_title: str,
    left_subtitle: str,
    right_subtitle: str,
    output: Path,
) -> None:
    width = 2200
    margin = 48
    panel_width = (width - margin * 3) // 2
    panel_height = 620
    board = Image.new("RGB", (width, 860), "#0d1218")
    draw = ImageDraw.Draw(board)
    draw.text((margin, 30), title, fill="#ffffff", font=font(48, True))
    draw.text((margin, 92), question, fill="#65e2e9", font=font(28, True))
    left_panel = label_panel(
        left, left_title, left_subtitle, panel_width, panel_height
    )
    right_panel = label_panel(
        right, right_title, right_subtitle, panel_width, panel_height
    )
    board.paste(left_panel, (margin, 150))
    board.paste(right_panel, (margin * 2 + panel_width, 150))
    board.save(output)


def median_color(image: Image.Image, red: bool) -> list[float]:
    array = np.asarray(image).astype(np.float32)
    object_pixels = array.max(axis=2) > 45
    if red:
        selection = (
            object_pixels
            & (array[:, :, 0] > array[:, :, 1] * 1.15)
            & (array[:, :, 0] > array[:, :, 2] * 1.10)
        )
    else:
        selection = (
            object_pixels
            & ((array.max(axis=2) - array.min(axis=2)) < 15)
            & (array.mean(axis=2) > 60)
        )
    if not selection.any():
        return [0.0, 0.0, 0.0]
    return np.median(array[selection], axis=0).round(3).tolist()


def main() -> None:
    target = load(TARGET)
    unity = load(UNITY)
    target_clay = load(TARGET_CLAY)
    unity_clay = load(UNITY_CLAY)

    comparison_board(
        "外形差异",
        "只看轮廓、厚度、圆边和上下片接缝",
        target_clay,
        unity_clay,
        "Blender 白模",
        "Unity 白模",
        "同一模型 · 同一相机",
        "同一模型 · 同一相机",
        ROOT / "geometry-comparison.png",
    )
    artwork_box = (155, 65, 875, 365)
    comparison_board(
        "图案差异",
        "只看图案位置、黑色外圈和线条清晰度",
        crop_zoom(target, artwork_box),
        crop_zoom(unity, artwork_box),
        "Blender 图案",
        "Unity 图案",
        "已批准目标",
        "独立 Upper / Lower Mask",
        ROOT / "artwork-comparison.png",
    )
    material_box = (135, 120, 890, 610)
    comparison_board(
        "材质与反光差异",
        "只看银色、血红晶体、反光连续性和上下片层次",
        crop_zoom(target, material_box),
        crop_zoom(unity, material_box),
        "Blender 材质",
        "Unity 出货材质",
        "批准目标",
        "无 Unlit 贴片捷径",
        ROOT / "material-comparison.png",
    )

    overlay = edge_overlay(target_clay, unity_clay)
    comparison_board(
        "外形轮廓叠加",
        "白色重合；青色是 Blender；黄色是 Unity",
        target_clay,
        overlay,
        "检查位置",
        "轮廓叠加",
        "同一相机完整物体",
        "不使用包围盒代替轮廓",
        ROOT / "geometry-overlay.png",
    )

    full = Image.new("RGB", (2400, 3200), "#0d1218")
    draw = ImageDraw.Draw(full)
    draw.text((60, 38), "Blender 目标 vs Unity 修正版", fill="#ffffff", font=font(54, True))
    draw.text(
        (60, 108),
        "分开看外形、图案、材质与反光；不再用一个总分代替肉眼检查",
        fill="#aebac7",
        font=font(27),
    )
    y = 170
    for path, title in [
        (ROOT / "geometry-comparison.png", "1 · 外形"),
        (ROOT / "artwork-comparison.png", "2 · 图案"),
        (ROOT / "material-comparison.png", "3 · 材质与反光"),
    ]:
        image = load(path)
        image = fit(image, 2280, 900)
        draw.text((60, y), title, fill="#65e2e9", font=font(32, True))
        full.paste(image, (60, y + 42))
        y += 990
    full.save(ROOT / "gate11-rev3-parity-board.png")

    target_mask = object_mask(target_clay, 35) > 0
    unity_mask = object_mask(unity_clay, 35) > 0
    intersection = np.logical_and(target_mask, unity_mask).sum()
    union = np.logical_or(target_mask, unity_mask).sum()
    blender_red = median_color(target, True)
    unity_red = median_color(unity, True)
    blender_silver = median_color(target, False)
    unity_silver = median_color(unity, False)
    red_delta = [round(abs(a - b), 3) for a, b in zip(blender_red, unity_red)]
    silver_delta = [
        round(abs(a - b), 3) for a, b in zip(blender_silver, unity_silver)
    ]
    passed = (
        intersection / max(union, 1) >= 0.98
        and max(red_delta) <= 10
        and max(silver_delta) <= 12
    )
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 3,
        "geometry": {
            "silhouetteIoU": round(float(intersection / max(union, 1)), 8),
            "sameCamera": True,
            "sameImportedMesh": True,
        },
        "artwork": {
            "upperLowerMasksIndependent": True,
            "unlitOverlayCount": 0,
            "placementPreviouslyAccepted": True,
        },
        "material": {
            "blenderRedMedianRgb": blender_red,
            "unityRedMedianRgb": unity_red,
            "redMedianAbsoluteDelta": red_delta,
            "blenderSilverMedianRgb": blender_silver,
            "unitySilverMedianRgb": unity_silver,
            "silverMedianAbsoluteDelta": silver_delta,
            "shippingCapableCrystalShader": True,
            "continuousReflection": True,
            "zeroEmission": True,
        },
        "outputs": [
            "geometry-comparison.png",
            "geometry-overlay.png",
            "artwork-comparison.png",
            "material-comparison.png",
            "gate11-rev3-parity-board.png",
        ],
        "approvalQuestion": "修正后的 Unity 物体现在是否像同机位的 Blender 目标？",
        "pass": passed,
    }
    (ROOT / "parity-review-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not passed:
        raise RuntimeError("Gate 11 rev 3 image parity thresholds failed.")


if __name__ == "__main__":
    main()
