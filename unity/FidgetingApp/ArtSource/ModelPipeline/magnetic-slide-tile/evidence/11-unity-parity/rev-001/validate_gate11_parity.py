#!/usr/bin/env python3
"""Validate and present Blender↔Unity Gate 11 neutral parity."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
BLENDER = ROOT / "blender-neutral.png"
UNITY = ROOT / "unity-neutral.png"
BLENDER_SILHOUETTE = ROOT / "blender-neutral-silhouette.png"
UNITY_SILHOUETTE = ROOT / "unity-neutral-all-silver-diagnostic.png"
BLENDER_REPORT = ROOT / "blender-neutral-report.json"
UNITY_REPORT = ROOT / "unity-import-parity-report.json"
REPORT = ROOT / "parity-report.json"
BOARD = ROOT / "gate11-parity-board.png"
OVERLAY = ROOT / "silhouette-overlay.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size=size,
        index=1 if bold else 0,
    )


def object_mask(image: np.ndarray) -> np.ndarray:
    maximum = image.max(axis=2)
    chroma = image.max(axis=2) - image.min(axis=2)
    mask = ((maximum > 22) | ((image[:, :, 0] > 18) & (chroma > 8))).astype(np.uint8) * 255
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return mask
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (labels == largest).astype(np.uint8) * 255


def bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def bbox_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, ix1 - ix0) * max(0, iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / max(1, area_a + area_b - intersection)


def contour_metrics(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    edge_a = cv2.Canny(a, 50, 120)
    edge_b = cv2.Canny(b, 50, 120)
    distance_b = cv2.distanceTransform(255 - edge_b, cv2.DIST_L2, 3)
    distance_a = cv2.distanceTransform(255 - edge_a, cv2.DIST_L2, 3)
    distances = np.concatenate([distance_b[edge_a > 0], distance_a[edge_b > 0]])
    return float(np.percentile(distances, 95)), float(distances.max())


def image_metrics(path: Path, image: np.ndarray, mask: np.ndarray) -> dict:
    pixels = image[mask > 0].astype(np.float32)
    red = pixels[
        (pixels[:, 0] > pixels[:, 1] * 1.35)
        & (pixels[:, 0] > pixels[:, 2] * 1.35)
        & (pixels[:, 0] > 55)
    ]
    neutral = pixels[
        (np.max(pixels, axis=1) - np.min(pixels, axis=1) < 18)
        & (pixels.mean(axis=1) > 70)
    ]
    return {
        "file": path.name,
        "objectPixels": int(len(pixels)),
        "redArtworkPixels": int(len(red)),
        "neutralSilverMedianRgb": [round(float(value), 3) for value in np.median(neutral, axis=0)] if len(neutral) else [],
        "clippedFraction": round(float((pixels.max(axis=1) >= 250).mean()), 8),
    }


def make_overlay(blender_mask: np.ndarray, unity_mask: np.ndarray) -> None:
    canvas = np.zeros((*blender_mask.shape, 3), dtype=np.uint8)
    blender_edge = cv2.Canny(blender_mask, 50, 120) > 0
    unity_edge = cv2.Canny(unity_mask, 50, 120) > 0
    canvas[blender_edge] = (255, 118, 67)
    canvas[unity_edge] = (68, 199, 255)
    Image.fromarray(canvas).save(OVERLAY)


def make_board(blender: Image.Image, unity: Image.Image, metrics: dict) -> None:
    canvas = Image.new("RGB", (3200, 1800), (13, 15, 17))
    draw = ImageDraw.Draw(canvas)
    draw.text((90, 55), "同一机位：Blender 与 Unity", fill=(244, 243, 238), font=font(64, True))
    draw.text((92, 140), "先看外形是否一致，再看材质近似差异。", fill=(181, 183, 180), font=font(34))
    for index, (image, title, subtitle) in enumerate([
        (blender, "Blender 中性图", "获批程序材质"),
        (unity, "Unity 中性图", "隔离 URP 场景"),
    ]):
        x = 70 + index * 1570
        fitted = ImageOps.contain(image, (1480, 835), Image.Resampling.LANCZOS)
        canvas.paste(fitted, (x, 245), fitted if fitted.mode == "RGBA" else None)
        draw.text((x, 1105), title, fill=(244, 243, 238), font=font(42, True))
        draw.text((x, 1163), subtitle, fill=(167, 169, 166), font=font(30))
    draw.rounded_rectangle((70, 1260, 3130, 1735), radius=24, fill=(24, 27, 31))
    draw.text((115, 1302), "外形检查", fill=(255, 164, 91), font=font(38, True))
    draw.text(
        (115, 1364),
        f"边界框重合 {metrics['visual']['boundingBoxIoU'] * 100:.2f}% · "
        f"轮廓 P95 差 {metrics['visual']['contourP95Pixels']:.2f} px · "
        f"相机位置/FOV 完全匹配",
        fill=(233, 232, 227),
        font=font(34),
    )
    draw.text((115, 1450), "已一致：尺寸、两片外壳、圆边、闭合姿态、图案位置。", fill=(205, 206, 202), font=font(32))
    draw.text((115, 1510), "仍是近似：Unity 水晶没有 Blender 薄膜干涉/透射；银色反射来自静态环境贴图。", fill=(205, 206, 202), font=font(32))
    draw.text((115, 1570), "上/下图案仍为两个独立贴图；30 档仍只记录规格，没有接入运行时或触感。", fill=(205, 206, 202), font=font(32))
    draw.text((115, 1650), "本场景完全隔离，现有正式场景未改动。", fill=(145, 214, 168), font=font(32, True))
    canvas.save(BOARD)


def main() -> None:
    blender_pil = Image.open(BLENDER).convert("RGB")
    unity_pil = Image.open(UNITY).convert("RGB")
    blender = np.asarray(blender_pil)
    unity = np.asarray(unity_pil)
    blender_mask = object_mask(np.asarray(Image.open(BLENDER_SILHOUETTE).convert("RGB")))
    unity_mask = object_mask(np.asarray(Image.open(UNITY_SILHOUETTE).convert("RGB")))
    blender_bbox = bbox(blender_mask)
    unity_bbox = bbox(unity_mask)
    intersection = np.logical_and(blender_mask > 0, unity_mask > 0).sum()
    union = np.logical_or(blender_mask > 0, unity_mask > 0).sum()
    contour_p95, contour_max = contour_metrics(blender_mask, unity_mask)
    blender_center = np.array([(blender_bbox[0] + blender_bbox[2]) / 2, (blender_bbox[1] + blender_bbox[3]) / 2])
    unity_center = np.array([(unity_bbox[0] + unity_bbox[2]) / 2, (unity_bbox[1] + unity_bbox[3]) / 2])

    blender_report = json.loads(BLENDER_REPORT.read_text())
    unity_report = json.loads(UNITY_REPORT.read_text())
    camera_position_delta = float(np.max(np.abs(
        np.array(blender_report["camera"]["unityPositionMeters"])
        - np.array([
            unity_report["camera"]["position"]["x"],
            unity_report["camera"]["position"]["y"],
            unity_report["camera"]["position"]["z"],
        ])
    )))
    fov_delta = abs(
        blender_report["camera"]["verticalFovDegrees"]
        - unity_report["camera"]["verticalFovDegrees"]
    )
    visual = {
        "blenderBoundingBox": list(blender_bbox),
        "unityBoundingBox": list(unity_bbox),
        "boundingBoxIoU": round(bbox_iou(blender_bbox, unity_bbox), 8),
        "silhouetteIoU": round(float(intersection / max(1, union)), 8),
        "centroidDeltaPixels": round(float(np.linalg.norm(blender_center - unity_center)), 6),
        "contourP95Pixels": round(contour_p95, 6),
        "contourMaximumPixels": round(contour_max, 6),
        "cameraPositionMaximumDeltaMeters": camera_position_delta,
        "verticalFovDeltaDegrees": fov_delta,
        "materialResponseIsApproximate": True,
    }
    checks = {
        "blenderRenderPassed": blender_report["pass"],
        "unityImportPassed": unity_report["pass"],
        "sameResolution": blender.shape == unity.shape == (900, 1600, 3),
        "sameCameraPosition": camera_position_delta < 1e-7,
        "sameVerticalFov": fov_delta < 0.001,
        "boundsMatch": unity_report["boundsRelativeError"] < 0.001,
        "trianglesMatch": unity_report["triangles"] == 4096,
        "twoRenderMeshes": unity_report["renderMeshes"] == 2,
        "twoCollisionMeshes": unity_report["collisionTriangles"] == [128, 128],
        "smoothSides": unity_report["normalMetrics"]["smoothSidePass"],
        "hardCapSideBoundary": unity_report["normalMetrics"]["hardCapSidePass"],
        "artworkIndependent": unity_report["upperLowerArtworkIndependent"],
        "shippingSceneUnchanged": not unity_report["shippingSceneModified"],
        "boundingBoxAlignment": bbox_iou(blender_bbox, unity_bbox) > 0.96,
        "centroidAlignment": np.linalg.norm(blender_center - unity_center) < 12.0,
        "contourAlignment": contour_p95 < 18.0,
    }
    checks = {key: bool(value) for key, value in checks.items()}
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "11-unity-parity",
        "revision": 1,
        "blender": image_metrics(BLENDER, blender, blender_mask),
        "unity": image_metrics(UNITY, unity, unity_mask),
        "visual": visual,
        "importMetrics": {
            "boundsMeters": unity_report["sortedBoundsMeters"],
            "boundsRelativeError": unity_report["boundsRelativeError"],
            "renderMeshes": unity_report["renderMeshes"],
            "vertices": unity_report["vertices"],
            "triangles": unity_report["triangles"],
            "collisionTriangles": unity_report["collisionTriangles"],
            "normalMetrics": unity_report["normalMetrics"],
            "textureImports": unity_report["textures"],
        },
        "materialGaps": unity_report["materialGaps"],
        "deliveryState": {
            "isolatedParityScene": True,
            "shippingSceneModified": False,
            "runtimeIntegrated": False,
            "hapticsIntegrated": False,
            "deviceMemoryMeasured": False,
            "deviceAcceptance": "pending",
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    make_overlay(blender_mask, unity_mask)
    make_board(blender_pil, unity_pil, report)
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 11 image parity validation failed.")


if __name__ == "__main__":
    main()
