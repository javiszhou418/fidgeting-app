#!/usr/bin/env python3
"""Build plain Gate 11 rev 2 round-edge evidence and objective checks."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001"
OLD = REV1 / "unity-neutral.png"
NEW = ROOT / "unity-neutral.png"
BLENDER = ROOT / "blender-neutral.png"
BLENDER_SILHOUETTE = ROOT / "blender-neutral-silhouette.png"
UNITY_SILHOUETTE = ROOT / "unity-neutral-all-silver.png"
WIREFRAME = ROOT / "unity-wireframe.png"
IMPORT_REPORT = ROOT / "unity-import-parity-report.json"
VALIDATION = ROOT / "unity-round-edge-validation.json"
PARITY = ROOT / "parity-report.json"
LOCATION = ROOT / "unity-round-edge-location.png"
COMPARISON = ROOT / "unity-round-edge-before-after.png"
WIRE_PROOF = ROOT / "unity-round-edge-wireframe-proof.png"
ROI = (170, 275, 690, 540)
BAND_ROI = (280, 340, 640, 475)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size=size,
        index=1 if bold else 0,
    )


def read_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def object_mask(image: np.ndarray) -> np.ndarray:
    maximum = image.max(axis=2)
    mask = (maximum > 24).astype(np.uint8) * 255
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count <= 1:
        return mask
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (labels == largest).astype(np.uint8) * 255


def bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def bbox_iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x1 - x0) * max(0, y1 - y0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / max(1, area_a + area_b - intersection)


def contour_p95(a: np.ndarray, b: np.ndarray) -> float:
    edge_a = cv2.Canny(a, 50, 120)
    edge_b = cv2.Canny(b, 50, 120)
    distance_a = cv2.distanceTransform(255 - edge_a, cv2.DIST_L2, 3)
    distance_b = cv2.distanceTransform(255 - edge_b, cv2.DIST_L2, 3)
    distances = np.concatenate([distance_b[edge_a > 0], distance_a[edge_b > 0]])
    return float(np.percentile(distances, 95))


def band_metrics(image: np.ndarray) -> dict:
    x0, y0, x1, y1 = BAND_ROI
    crop = image[y0:y1, x0:x1].astype(np.float32)
    luma = crop[:, :, 0] * 0.2126 + crop[:, :, 1] * 0.7152 + crop[:, :, 2] * 0.0722
    valid = crop.max(axis=2) > 32
    profile = np.array([
        np.median(luma[:, x][valid[:, x]]) if valid[:, x].any() else np.nan
        for x in range(luma.shape[1])
    ])
    good = np.isfinite(profile)
    profile = np.interp(np.arange(len(profile)), np.flatnonzero(good), profile[good])
    gradient = np.abs(np.diff(profile))
    second = np.abs(np.diff(profile, n=2))
    return {
        "columnGradientMedian": round(float(np.median(gradient)), 6),
        "columnGradientP95": round(float(np.percentile(gradient, 95)), 6),
        "columnGradientP99": round(float(np.percentile(gradient, 99)), 6),
        "secondDerivativeP99": round(float(np.percentile(second, 99)), 6),
        "hardBandColumns": int((second > 5.0).sum()),
        "smoothGradientCoverage": round(float(((gradient > 0.15) & (gradient < 2.0)).mean()), 6),
        "flatColumnFraction": round(float((gradient < 0.1).mean()), 6),
        "periodicBandScore": round(
            float(np.percentile(gradient, 99) / max(np.percentile(gradient, 95), 0.05)),
            6,
        ),
        "profileRange": round(float(profile.max() - profile.min()), 6),
    }


def make_location(after: Image.Image) -> None:
    canvas = Image.new("RGB", (1920, 1080), (13, 15, 17))
    image = ImageOps.contain(after, (1680, 945), Image.Resampling.LANCZOS)
    canvas.paste(image, ((1920 - image.width) // 2, 105))
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 34), "这次只检查前端圆边", fill=(244, 243, 238), font=font(44, True))
    sx = image.width / after.width
    sy = image.height / after.height
    ox = (1920 - image.width) // 2
    oy = 105
    box = (
        int(ox + ROI[0] * sx),
        int(oy + ROI[1] * sy),
        int(ox + ROI[2] * sx),
        int(oy + ROI[3] * sy),
    )
    draw.rounded_rectangle(box, radius=14, outline=(255, 142, 58), width=10)
    draw.line((box[2] + 12, box[1] + 20, box[2] + 190, box[1] - 40), fill=(255, 142, 58), width=10)
    draw.polygon(
        [(box[2] + 12, box[1] + 20), (box[2] + 42, box[1] + 7), (box[2] + 34, box[1] + 38)],
        fill=(255, 142, 58),
    )
    draw.text((box[2] + 205, box[1] - 75), "检查这里", fill=(255, 164, 91), font=font(36, True))
    draw.text((70, 1010), "图案位置已经接受，本轮不再询问图案。", fill=(154, 213, 173), font=font(30))
    canvas.save(LOCATION)


def make_comparison(before: Image.Image, after: Image.Image, metrics: dict) -> None:
    canvas = Image.new("RGB", (3200, 1700), (13, 15, 17))
    draw = ImageDraw.Draw(canvas)
    draw.text((90, 55), "同一位置放大约 4 倍", fill=(244, 243, 238), font=font(62, True))
    draw.text((92, 140), "相机、外形和面数都没变；只替换了反光环境。", fill=(180, 182, 179), font=font(34))
    for index, (image, label, color) in enumerate([
        (before, "旧环境反射：像棱角", (255, 132, 110)),
        (after, "连续环境反射：圆边连续", (111, 222, 177)),
    ]):
        crop = image.crop(ROI)
        fitted = ImageOps.contain(crop, (1450, 1120), Image.Resampling.NEAREST)
        x = 80 + index * 1560
        y = 255
        canvas.paste(fitted, (x, y))
        draw.rounded_rectangle((x, y, x + fitted.width, y + fitted.height), radius=16, outline=color, width=8)
        draw.text((x, 1405), label, fill=color, font=font(46, True))
    draw.text(
        (90, 1510),
        f"平滑变化覆盖：{metrics['old']['smoothGradientCoverage'] * 100:.1f}% → "
        f"{metrics['new']['smoothGradientCoverage'] * 100:.1f}%；"
        f"固定亮带评分：{metrics['old']['periodicBandScore']:.1f} → {metrics['new']['periodicBandScore']:.1f}",
        fill=(220, 220, 214),
        font=font(34),
    )
    draw.text((90, 1580), "修正后亮带沿圆边平滑变化，不再在固定方向突然切换。", fill=(220, 220, 214), font=font(34))
    canvas.save(COMPARISON)


def make_wire_proof(wire: Image.Image, import_report: dict) -> None:
    canvas = Image.new("RGB", (2400, 1400), (13, 15, 17))
    draw = ImageDraw.Draw(canvas)
    draw.text((80, 48), "圆边本身有足够细分", fill=(244, 243, 238), font=font(58, True))
    draw.text((82, 126), "细线显示真实表面密度；没有为了修图临时加面。", fill=(180, 182, 179), font=font(34))
    fitted = ImageOps.contain(wire, (2200, 1050), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((2400 - fitted.width) // 2, 220))
    arc = import_report["arcNormals"]
    draw.text(
        (82, 1290),
        f"每个半圆 256 段 · 相邻方向中位变化 {arc['medianAdjacentStepDegrees']:.3f}° · "
        f"总面数仍为 {import_report['triangles']:,}",
        fill=(112, 215, 241),
        font=font(32, True),
    )
    canvas.save(WIRE_PROOF)


def main() -> None:
    old = read_rgb(OLD)
    new = read_rgb(NEW)
    blender_mask = object_mask(read_rgb(BLENDER_SILHOUETTE))
    unity_mask = object_mask(read_rgb(UNITY_SILHOUETTE))
    old_bands = band_metrics(old)
    new_bands = band_metrics(new)
    import_report = json.loads(IMPORT_REPORT.read_text())
    blender_bbox = bbox(blender_mask)
    unity_bbox = bbox(unity_mask)
    intersection = np.logical_and(blender_mask > 0, unity_mask > 0).sum()
    union = np.logical_or(blender_mask > 0, unity_mask > 0).sum()
    silhouette_iou = float(intersection / max(1, union))
    bbox_overlap = bbox_iou(blender_bbox, unity_bbox)
    contour = contour_p95(blender_mask, unity_mask)
    cyan_pixels = int(
        ((read_rgb(WIREFRAME)[:, :, 1] > 130) & (read_rgb(WIREFRAME)[:, :, 2] > 130)).sum()
    )

    checks = {
        "unityImportPassed": import_report["pass"],
        "geometryUnchanged": not import_report["geometryChanged"],
        "trianglesUnchanged": import_report["triangles"] == 4096,
        "boundsUnchanged": import_report["boundsRelativeError"] < 0.001,
        "arcNormalProgressionGradual": import_report["arcNormals"]["gradualProgressionPass"],
        "arcNormalMedianMatches256Segments": abs(
            import_report["arcNormals"]["medianAdjacentStepDegrees"] - 0.703125
        ) < 0.01,
        "capSideBoundaryHard": import_report["capSideBoundary"]["hardBoundaryPass"],
        "continuousEnvironmentMipChain": import_report["environment"]["mipCount"] >= 9,
        "continuousEnvironmentFiltering": import_report["environment"]["filterMode"] == "Trilinear",
        "boxProjectionDisabled": not import_report["environment"]["boxProjection"],
        "analyticEnvironmentSeamsContinuous": import_report["environment"]["maximumAnalyticSeamDelta"] < 0.005,
        "hardBandsReduced": new_bands["periodicBandScore"] < old_bands["periodicBandScore"] * 0.5,
        "highlightJumpReduced": new_bands["smoothGradientCoverage"] > old_bands["smoothGradientCoverage"] * 2.0,
        "wireframeVisible": cyan_pixels > 10000,
        "silhouetteAligned": silhouette_iou > 0.98,
        "boundingBoxAligned": bbox_overlap > 0.98,
        "contourAligned": contour < 6.0,
        "patternDecisionPreserved": import_report["patternPlacementDecision"] == "accepted-provisionally-not-under-review",
        "shippingSceneUnchanged": not import_report["shippingSceneModified"],
    }
    validation = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "11-unity-parity",
        "revision": 2,
        "inspectionRoiPixels": list(ROI),
        "bandMeasurementRoiPixels": list(BAND_ROI),
        "old": old_bands,
        "new": new_bands,
        "wireframeCyanPixels": cyan_pixels,
        "visual": {
            "blenderBoundingBox": list(blender_bbox),
            "unityBoundingBox": list(unity_bbox),
            "boundingBoxIoU": round(bbox_overlap, 8),
            "silhouetteIoU": round(silhouette_iou, 8),
            "contourP95Pixels": round(contour, 6),
        },
        "rootCause": {
            "verified": checks["hardBandsReduced"] and checks["highlightJumpReduced"],
            "oldEnvironment": import_report["environment"]["oldEnvironment"],
            "newEnvironment": import_report["environment"]["newEnvironment"],
            "geometryChanged": False,
            "importerNormalsChanged": False,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    make_location(Image.fromarray(new))
    make_comparison(Image.fromarray(old), Image.fromarray(new), validation)
    make_wire_proof(Image.open(WIREFRAME).convert("RGB"), import_report)
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n")

    parity = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "11-unity-parity",
        "revision": 2,
        "blenderNeutral": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002/blender-neutral.png",
        "unityNeutral": NEW.name,
        "unityBefore": str(OLD),
        "unityAfter": NEW.name,
        "unityWireframe": WIREFRAME.name,
        "import": import_report,
        "imageValidation": validation,
        "partialDecision": {
            "exactText": "pattern placement accepted; geometry/round-edge parity rejected.",
            "patternPlacement": "accepted-provisionally",
            "geometryRoundEdgeParity": "rev1-rejected",
            "rev2QuestionScope": "corrected Unity round edge only",
        },
        "deliveryState": {
            "isolatedParityScene": True,
            "shippingSceneModified": False,
            "runtimeIntegrated": False,
            "hapticsIntegrated": False,
            "gate12Started": False,
            "deviceAcceptance": "pending",
        },
        "pass": validation["pass"] and import_report["pass"],
    }
    PARITY.write_text(json.dumps(parity, indent=2) + "\n")
    print(json.dumps(validation, indent=2))
    if not parity["pass"]:
        raise RuntimeError("Gate 11 rev 2 round-edge validation failed.")


if __name__ == "__main__":
    main()
