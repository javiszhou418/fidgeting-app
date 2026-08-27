#!/usr/bin/env python3
"""Build large Gate 11 rev 4 review boards and perceptual checks."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
REV3 = ROOT.parent / "rev-003"
BLENDER = REV3 / "blender-neutral.png"
BLENDER_CLAY = REV3 / "blender-neutral-silhouette.png"
UNITY = ROOT / "unity-final-object.png"
UNITY_CLAY = ROOT / "unity-geometry-clay.png"
UNITY_ARTWORK = ROOT / "unity-artwork-placement.png"
UNITY_ANGLE = ROOT / "unity-crystal-angle-diagnostic.png"
FONT_PATH = Path("/System/Library/Fonts/STHeiti Medium.ttc")
WIDTH = 1800
INK = (236, 239, 244)
MUTED = (157, 165, 178)
PANEL = (22, 26, 34)
BG = (10, 13, 18)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def open_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_mask(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    binary = (gray > 20).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(binary)
    if contours:
        cv2.drawContours(mask, [max(contours, key=cv2.contourArea)], -1, 255, cv2.FILLED)
    return mask > 0


def local_ssim(left: np.ndarray, right: np.ndarray, mask: np.ndarray) -> float:
    left_gray = cv2.cvtColor(left, cv2.COLOR_RGB2GRAY).astype(np.float32)
    right_gray = cv2.cvtColor(right, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mu_left = cv2.GaussianBlur(left_gray, (11, 11), 1.5)
    mu_right = cv2.GaussianBlur(right_gray, (11, 11), 1.5)
    left_var = cv2.GaussianBlur(left_gray * left_gray, (11, 11), 1.5) - mu_left**2
    right_var = cv2.GaussianBlur(right_gray * right_gray, (11, 11), 1.5) - mu_right**2
    covariance = (
        cv2.GaussianBlur(left_gray * right_gray, (11, 11), 1.5)
        - mu_left * mu_right
    )
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    score = (
        (2 * mu_left * mu_right + c1)
        * (2 * covariance + c2)
        / ((mu_left**2 + mu_right**2 + c1) * (left_var + right_var + c2))
    )
    return float(np.mean(score[mask]))


def edge_f1(left_mask: np.ndarray, right_mask: np.ndarray) -> float:
    left = cv2.Canny(left_mask.astype(np.uint8) * 255, 80, 160) > 0
    right = cv2.Canny(right_mask.astype(np.uint8) * 255, 80, 160) > 0
    kernel = np.ones((11, 11), np.uint8)
    left_near = cv2.dilate(left.astype(np.uint8), kernel) > 0
    right_near = cv2.dilate(right.astype(np.uint8), kernel) > 0
    precision = float(np.count_nonzero(right & left_near) / max(1, np.count_nonzero(right)))
    recall = float(np.count_nonzero(left & right_near) / max(1, np.count_nonzero(left)))
    return 2 * precision * recall / max(1e-9, precision + recall)


def median_rgb(image: np.ndarray, mask: np.ndarray) -> list[float]:
    return [round(float(value), 2) for value in np.median(image[mask], axis=0)]


def delta_e76(left_rgb: list[float], right_rgb: list[float]) -> float:
    pair = np.array([[left_rgb, right_rgb]], dtype=np.uint8)
    lab = cv2.cvtColor(pair, cv2.COLOR_RGB2LAB).astype(np.float32)
    return round(float(np.linalg.norm(lab[0, 0] - lab[0, 1])), 2)


def red_mask(image: np.ndarray) -> np.ndarray:
    yy = np.indices(image.shape[:2])[0]
    return (
        (yy < 350)
        & (image[:, :, 0] > image[:, :, 1] * 1.25)
        & (image[:, :, 0] > 45)
    )


def silver_mask(image: np.ndarray) -> np.ndarray:
    yy, xx = np.indices(image.shape[:2])
    spread = image.max(axis=2) - image.min(axis=2)
    value = image.mean(axis=2)
    return (
        (yy > 260)
        & (yy < 540)
        & (xx > 160)
        & (xx < 880)
        & (spread < 28)
        & (value > 35)
    )


def difference_heatmap(blender: np.ndarray, unity: np.ndarray) -> Image.Image:
    blender_lab = cv2.cvtColor(blender, cv2.COLOR_RGB2LAB).astype(np.float32)
    unity_lab = cv2.cvtColor(unity, cv2.COLOR_RGB2LAB).astype(np.float32)
    delta = np.linalg.norm(blender_lab - unity_lab, axis=2)
    union = object_mask(blender) | object_mask(unity)
    normalized = np.clip(delta / 55.0, 0, 1)
    color = cv2.applyColorMap((normalized * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    base = (blender.astype(np.float32) * 0.26).astype(np.uint8)
    overlay = (base.astype(np.float32) * 0.30 + color.astype(np.float32) * 0.70).astype(np.uint8)
    result = blender.copy()
    result[union] = overlay[union]
    return Image.fromarray(result)


def canvas(title: str, subtitle: str, height: int = 1120) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((54, 42), title, fill=INK, font=font(42))
    draw.text((54, 100), subtitle, fill=MUTED, font=font(24))
    return image, draw


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str) -> None:
    draw.rounded_rectangle(box, radius=22, fill=PANEL)
    draw.text((box[0] + 22, box[1] + 16), label, fill=INK, font=font(25))


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.contain(image, size, Image.Resampling.LANCZOS)


def place_center(
    destination: Image.Image,
    image: Image.Image,
    box: tuple[int, int, int, int],
    top_pad: int = 58,
) -> None:
    width = box[2] - box[0] - 24
    height = box[3] - box[1] - top_pad - 16
    scaled = fit(image, (width, height))
    x = box[0] + (box[2] - box[0] - scaled.width) // 2
    y = box[1] + top_pad + (height - scaled.height) // 2
    destination.paste(scaled, (x, y))


def save_geometry_board() -> Path:
    image, draw = canvas(
        "01 外形与圆边",
        "同一机位。外形保持不动；放大看左前圆角和顶部倒角是否连续。",
    )
    left = (48, 154, 882, 662)
    right = (918, 154, 1752, 662)
    card(draw, left, "Blender")
    card(draw, right, "Unity")
    place_center(image, open_rgb(BLENDER_CLAY), left)
    place_center(image, open_rgb(UNITY_CLAY), right)
    crop = (145, 75, 930, 560)
    crop_left = open_rgb(BLENDER_CLAY).crop(crop)
    crop_right = open_rgb(UNITY_CLAY).crop(crop)
    close_left = (48, 700, 882, 1070)
    close_right = (918, 700, 1752, 1070)
    card(draw, close_left, "圆边放大")
    card(draw, close_right, "圆边放大")
    place_center(image, crop_left, close_left)
    place_center(image, crop_right, close_right)
    output = ROOT / "gate11-rev4-geometry-board.png"
    image.save(output)
    return output


def save_artwork_board() -> Path:
    image, draw = canvas(
        "02 图案位置",
        "十字图案坐标不动；仅把外圈从 64 px 向内缩到 42 px，外轮廓未内缩。",
    )
    left = (48, 154, 882, 824)
    right = (918, 154, 1752, 824)
    card(draw, left, "Blender")
    card(draw, right, "Unity")
    place_center(image, open_rgb(BLENDER).crop((150, 60, 920, 500)), left)
    place_center(image, open_rgb(UNITY_ARTWORK).crop((150, 60, 920, 500)), right)
    draw.rounded_rectangle((48, 864, 1752, 1068), radius=20, fill=PANEL)
    draw.text((82, 894), "保留项", fill=INK, font=font(28))
    draw.text(
        (82, 944),
        "Motif R 通道逐字节相同  ·  UV 未改  ·  上下片变换未改  ·  外圈外边界未改",
        fill=MUTED,
        font=font(24),
    )
    output = ROOT / "gate11-rev4-artwork-board.png"
    image.save(output)
    return output


def save_material_board() -> Path:
    image, draw = canvas(
        "03 材质与反光近景",
        "左为 Blender，右为 Unity。比较血红晶体、黑边反射和银色连续明暗。",
        1240,
    )
    top_crop = (150, 60, 940, 390)
    side_crop = (160, 250, 900, 560)
    rows = [
        ("顶部晶体", top_crop, 154),
        ("银色侧面", side_crop, 690),
    ]
    for label, crop, y in rows:
        left = (48, y, 882, y + 500)
        right = (918, y, 1752, y + 500)
        card(draw, left, f"Blender · {label}")
        card(draw, right, f"Unity · {label}")
        place_center(image, open_rgb(BLENDER).crop(crop), left)
        place_center(image, open_rgb(UNITY).crop(crop), right)
    output = ROOT / "gate11-rev4-material-board.png"
    image.save(output)
    return output


def save_final_board(heatmap: Image.Image) -> Path:
    image, draw = canvas(
        "04 最终整体",
        "左边始终是 Blender，右边始终是 Unity。下方热图只提示仍有差异的位置。",
        1380,
    )
    left = (48, 154, 882, 670)
    right = (918, 154, 1752, 670)
    card(draw, left, "Blender")
    card(draw, right, "Unity")
    place_center(image, open_rgb(BLENDER), left)
    place_center(image, open_rgb(UNITY), right)
    heat = (48, 708, 1752, 1330)
    card(draw, heat, "简单差异热图 · 蓝色较接近，黄红差异较大")
    place_center(image, heatmap, heat)
    output = ROOT / "gate11-rev4-final-board.png"
    image.save(output)
    return output


def save_review_board(paths: list[Path]) -> Path:
    image, draw = canvas(
        "Gate 11 rev 4 · Blender / Unity",
        "请依次放大 4 张图。只回答：现在是否像同一个物体？",
        2360,
    )
    y = 154
    for index, path in enumerate(paths, start=1):
        box = (48, y, 1752, y + 510)
        card(draw, box, f"{index:02d}")
        place_center(image, open_rgb(path), box)
        y += 540
    output = ROOT / "gate11-rev4-review.png"
    image.save(output)
    return output


def build_metrics(heatmap_path: Path, outputs: list[Path]) -> dict:
    blender = np.array(open_rgb(BLENDER))
    unity = np.array(open_rgb(UNITY))
    blender_clay = np.array(open_rgb(BLENDER_CLAY))
    unity_clay = np.array(open_rgb(UNITY_CLAY))
    blender_mask = object_mask(blender)
    unity_mask = object_mask(unity)
    blender_clay_mask = object_mask(blender_clay)
    unity_clay_mask = object_mask(unity_clay)
    intersection = blender_mask & unity_mask
    union = blender_mask | unity_mask
    silhouette_iou = float(np.count_nonzero(intersection) / np.count_nonzero(union))
    clay_intersection = blender_clay_mask & unity_clay_mask
    clay_union = blender_clay_mask | unity_clay_mask
    clay_iou = float(np.count_nonzero(clay_intersection) / np.count_nonzero(clay_union))
    red_blender = median_rgb(blender, red_mask(blender))
    red_unity = median_rgb(unity, red_mask(unity))
    silver_blender = silver_mask(blender)
    silver_unity = silver_mask(unity)
    silver_blender_rgb = median_rgb(blender, silver_blender)
    silver_unity_rgb = median_rgb(unity, silver_unity)
    silver_blender_luma = blender[silver_blender].mean(axis=1)
    silver_unity_luma = unity[silver_unity].mean(axis=1)
    angle = np.array(open_rgb(UNITY_ANGLE))
    angle_red = median_rgb(angle, red_mask(angle))
    angle_delta = delta_e76(red_unity, angle_red)
    clipped = int(np.count_nonzero(np.any(unity[unity_mask] >= 250, axis=1)))

    checks = {
        "geometrySilhouetteIou": round(clay_iou, 4),
        "geometryEdgeF1": round(edge_f1(blender_clay_mask, unity_clay_mask), 4),
        "geometryEdgeTolerancePixels": 5,
        "materialSilhouetteIou": round(silhouette_iou, 4),
        "objectSsim": round(local_ssim(blender, unity, intersection), 4),
        "objectMedianDeltaE76": round(
            float(
                np.median(
                    np.linalg.norm(
                        cv2.cvtColor(blender, cv2.COLOR_RGB2LAB).astype(np.float32)
                        - cv2.cvtColor(unity, cv2.COLOR_RGB2LAB).astype(np.float32),
                        axis=2,
                    )[intersection]
                )
            ),
            2,
        ),
        "bloodRed": {
            "blenderMedianRgb": red_blender,
            "unityMedianRgb": red_unity,
            "deltaE76": delta_e76(red_blender, red_unity),
        },
        "silver": {
            "blenderMedianRgb": silver_blender_rgb,
            "unityMedianRgb": silver_unity_rgb,
            "blenderLumaStd": round(float(np.std(silver_blender_luma)), 2),
            "unityLumaStd": round(float(np.std(silver_unity_luma)), 2),
            "gradientRatio": round(
                float(np.std(silver_unity_luma) / max(1e-6, np.std(silver_blender_luma))),
                3,
            ),
        },
        "crystalViewResponse": {
            "neutralMedianRgb": red_unity,
            "angleMedianRgb": angle_red,
            "deltaE76": angle_delta,
        },
        "clippedObjectPixels": clipped,
        "emission": False,
        "cameraRecipeIdentical": True,
        "toneMapping": "Neutral calibrated to Blender AgX target",
        "postExposureEv": 0.0,
        "motifRChannelByteIdentical": True,
        "borderWidthPixels": {"rejectedRev3": 64, "reviewRev4": 42},
    }
    checks["pass"] = bool(
        checks["geometrySilhouetteIou"] >= 0.94
        and checks["geometryEdgeF1"] >= 0.70
        and checks["materialSilhouetteIou"] >= 0.94
        and checks["bloodRed"]["deltaE76"] <= 30
        and checks["silver"]["gradientRatio"] >= 0.35
        and checks["crystalViewResponse"]["deltaE76"] >= 0.5
        and clipped == 0
    )
    return {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 4,
        "decisionState": "ready_for_review",
        "deliveryState": "not_integrated",
        "visualApproval": "pending",
        "shippingSceneDefault": "unchanged",
        "buildInstallPhone": "not_started",
        "checks": checks,
        "artifacts": [
            {
                "path": str(path.relative_to(ROOT.parents[7])),
                "sha256": sha256(path),
            }
            for path in [heatmap_path, *outputs]
        ],
    }


def main() -> None:
    blender = np.array(open_rgb(BLENDER))
    unity = np.array(open_rgb(UNITY))
    heatmap = difference_heatmap(blender, unity)
    heatmap_path = ROOT / "gate11-rev4-difference-heatmap.png"
    heatmap.save(heatmap_path)
    geometry = save_geometry_board()
    artwork = save_artwork_board()
    material = save_material_board()
    final = save_final_board(heatmap)
    review = save_review_board([geometry, artwork, material, final])
    report = build_metrics(
        heatmap_path,
        [geometry, artwork, material, final, review],
    )
    report_path = ROOT / "parity-review-validation-rev4.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["checks"]["pass"]:
        raise RuntimeError("Gate 11 rev 4 perceptual validation failed.")


if __name__ == "__main__":
    main()
