#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "blender-shipping-closed.png"
UNITY = ROOT / "unity-shipping-closed.png"
TARGET_CLAY = ROOT / "blender-clay.png"
UNITY_CLAY = ROOT / "unity-clay.png"
TARGET_SILHOUETTE = ROOT / "blender-silhouette.png"
UNITY_SILHOUETTE = ROOT / "unity-silhouette.png"
UNITY_IMPORT = ROOT / "unity-import-parity-report.json"
REPORT = ROOT / "full-frame-parity-report.json"
HEATMAP = ROOT / "full-frame-difference-heatmap.png"
BOARD = ROOT / "gate11-r010-full-frame-board.png"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rgb(path):
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def bbox(mask):
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def centroid(mask):
    ys, xs = np.where(mask)
    return [float(xs.mean()), float(ys.mean())]


def iou(first, second):
    return float(np.count_nonzero(first & second) / max(np.count_nonzero(first | second), 1))


def global_ssim(first, second, mask=None):
    values = []
    if mask is None:
        mask = np.ones(first.shape[:2], dtype=bool)
    for channel in range(3):
        a = first[:, :, channel].astype(np.float64)[mask]
        b = second[:, :, channel].astype(np.float64)[mask]
        mean_a, mean_b = a.mean(), b.mean()
        var_a, var_b = a.var(), b.var()
        covariance = ((a - mean_a) * (b - mean_b)).mean()
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        values.append(
            ((2 * mean_a * mean_b + c1) * (2 * covariance + c2))
            / ((mean_a**2 + mean_b**2 + c1) * (var_a + var_b + c2))
        )
    return float(np.mean(values))


def lab_delta(first, second, mask):
    lab_a = cv2.cvtColor(first, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(second, cv2.COLOR_RGB2LAB).astype(np.float32)
    delta = np.linalg.norm(lab_a - lab_b, axis=2)[mask]
    return {
        "pixelCount": int(delta.size),
        "median": float(np.median(delta)),
        "mean": float(np.mean(delta)),
        "p95": float(np.percentile(delta, 95)),
    }


def perceptual_proxy(first, second):
    small_a = cv2.resize(first, (224, 176), interpolation=cv2.INTER_AREA)
    small_b = cv2.resize(second, (224, 176), interpolation=cv2.INTER_AREA)
    lab_a = cv2.cvtColor(small_a, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(small_b, cv2.COLOR_RGB2LAB).astype(np.float32)
    gradients = []
    for image in (lab_a, lab_b):
        gray = image[:, :, 0]
        gradients.append(np.dstack([
            cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3),
            cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3),
        ]))
    color_rmse = float(np.sqrt(np.mean((lab_a - lab_b) ** 2)) / 255.0)
    gradient_rmse = float(
        np.sqrt(np.mean((gradients[0] - gradients[1]) ** 2)) / 1020.0
    )
    return {
        "method": "224x176 Lab plus luminance-gradient RMSE; LPIPS unavailable",
        "colorRmseNormalized": color_rmse,
        "gradientRmseNormalized": gradient_rmse,
        "combined": color_rmse * 0.7 + gradient_rmse * 0.3,
    }


def edge_distance(first_mask, second_mask):
    first_edges = cv2.Canny((first_mask * 255).astype(np.uint8), 50, 150) > 0
    second_edges = cv2.Canny((second_mask * 255).astype(np.uint8), 50, 150) > 0
    distance = cv2.distanceTransform((~second_edges).astype(np.uint8), cv2.DIST_L2, 3)
    values = distance[first_edges]
    return {
        "p95": float(np.percentile(values, 95)),
        "max": float(values.max()),
    }


def hotspot(image, object_mask):
    luminance = image.mean(axis=2)
    mask = object_mask & (luminance > 180)
    bounds = bbox(mask)
    center = centroid(mask)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    perimeter = sum(cv2.arcLength(contour, True) for contour in contours)
    area = max(np.count_nonzero(mask), 1)
    return {
        "threshold": "mean RGB > 180 inside raw silhouette",
        "pixels": int(area),
        "centroid": center,
        "bbox": bounds,
        "bboxAspect": float(width / max(height, 1)),
        "compactness": float(perimeter * perimeter / (4 * np.pi * area)),
    }


def linear_gradient(image, mask):
    luminance = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float64)
    ys, xs = np.where(mask)
    design = np.column_stack([
        np.ones(xs.size),
        xs / image.shape[1],
        ys / image.shape[0],
    ])
    coefficients, *_ = np.linalg.lstsq(design, luminance[mask], rcond=None)
    vector = coefficients[1:]
    return {
        "mean": float(luminance[mask].mean()),
        "std": float(luminance[mask].std()),
        "gradientX": float(vector[0]),
        "gradientY": float(vector[1]),
        "gradientMagnitude": float(np.linalg.norm(vector)),
    }


def contact_shadow(image, object_mask):
    kernel = np.ones((31, 31), np.uint8)
    outer = cv2.dilate(object_mask.astype(np.uint8), kernel) > 0
    inner = cv2.dilate(object_mask.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    ring = outer & ~inner
    far = cv2.dilate(object_mask.astype(np.uint8), np.ones((91, 91), np.uint8)) > 0
    far &= ~cv2.dilate(object_mask.astype(np.uint8), np.ones((55, 55), np.uint8)).astype(bool)
    luminance = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float64)
    ring_mean = float(luminance[ring].mean())
    far_mean = float(luminance[far].mean())
    return {
        "nearObjectMean": ring_mean,
        "farGroundMean": far_mean,
        "contrast": far_mean - ring_mean,
    }


def make_heatmap(target, unity):
    difference = np.max(np.abs(target.astype(np.int16) - unity.astype(np.int16)), axis=2)
    heat = cv2.applyColorMap(
        np.clip(difference * 3, 0, 255).astype(np.uint8),
        cv2.COLORMAP_TURBO,
    )
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    Image.fromarray(heat).save(HEATMAP)
    return heat, difference


def font(size, bold=False):
    for candidate in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]:
        try:
            return ImageFont.truetype(candidate, size, index=1 if bold else 0)
        except OSError:
            pass
    return ImageFont.load_default()


def scaled(image, size):
    return Image.fromarray(image).resize(size, Image.Resampling.LANCZOS)


def make_board(target, unity, target_clay, unity_clay, heat, report):
    canvas = Image.new("RGB", (1800, 1510), (7, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (44, 28),
        "Gate 11 rev 10 · Full-frame Blender / Unity parity",
        font=font(34, True),
        fill=(242, 247, 250),
    )
    draw.text(
        (44, 72),
        "All panels use the same 1400×1100 frame. No crop, resize-per-panel, or post-alignment.",
        font=font(19),
        fill=(160, 180, 192),
    )
    panel_size = (700, 550)
    panels = [
        ("Blender target", target, 44, 120),
        ("Unity rev 10", unity, 782, 120),
        ("Blender clay", target_clay, 44, 720),
        ("Unity clay", unity_clay, 782, 720),
    ]
    for title, image, x, y in panels:
        draw.rounded_rectangle(
            (x, y, x + 718, y + 590),
            14,
            fill=(14, 20, 25),
            outline=(43, 57, 67),
            width=2,
        )
        draw.text((x + 10, y + 9), title, font=font(20, True), fill=(235, 242, 246))
        canvas.paste(scaled(image, panel_size), (x + 9, y + 38))
    canvas.paste(scaled(heat, (260, 204)), (1510, 120))
    draw.text((1510, 332), "Full-frame heatmap", font=font(18, True), fill=(235, 242, 246))

    metrics = report["fullFrame"]
    hotspot_metrics = report["hotspot"]
    lines = [
        f"Full-frame SSIM {metrics['globalSsim']:.3f}  ·  perceptual proxy {metrics['perceptualProxy']['combined']:.3f}",
        f"Heatmap >24 levels {metrics['heatmapAreaFractionOver24'] * 100:.1f}%  ·  background MAE {metrics['backgroundMeanAbsoluteError']:.1f}",
        f"Hotspot area error {hotspot_metrics['relativeAreaError'] * 100:.1f}%  ·  centroid {hotspot_metrics['centroidErrorPixels']:.1f}px",
        f"Hotspot aspect error {hotspot_metrics['aspectRelativeError'] * 100:.1f}%  ·  clay gradient pass {report['checks']['clayGradient']}",
    ]
    draw.rounded_rectangle(
        (44, 1340, 1756, 1476),
        14,
        fill=(29, 18, 20),
        outline=(154, 67, 75),
        width=2,
    )
    draw.text(
        (64, 1355),
        "BLOCKED · not ready for Gate 11 review",
        font=font(25, True),
        fill=(255, 121, 126),
    )
    draw.text((64, 1394), lines[0], font=font(17), fill=(229, 236, 240))
    draw.text((64, 1421), lines[1], font=font(17), fill=(229, 236, 240))
    draw.text((910, 1394), lines[2], font=font(17), fill=(229, 236, 240))
    draw.text((910, 1421), lines[3], font=font(17), fill=(229, 236, 240))
    canvas.save(BOARD)


def main():
    required = [
        TARGET,
        UNITY,
        TARGET_CLAY,
        UNITY_CLAY,
        TARGET_SILHOUETTE,
        UNITY_SILHOUETTE,
        UNITY_IMPORT,
    ]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    target = read_rgb(TARGET)
    unity = read_rgb(UNITY)
    target_clay = read_rgb(TARGET_CLAY)
    unity_clay = read_rgb(UNITY_CLAY)
    shapes = {image.shape for image in [target, unity, target_clay, unity_clay]}
    if shapes != {(1100, 1400, 3)}:
        raise RuntimeError(f"Full-frame sources differ: {shapes}")

    target_mask = cv2.cvtColor(read_rgb(TARGET_SILHOUETTE), cv2.COLOR_RGB2GRAY) > 10
    unity_mask = cv2.cvtColor(read_rgb(UNITY_SILHOUETTE), cv2.COLOR_RGB2GRAY) > 60
    union = target_mask | unity_mask
    common = target_mask & unity_mask
    background = ~union
    heat, difference = make_heatmap(target, unity)

    target_hotspot = hotspot(target, target_mask)
    unity_hotspot = hotspot(unity, unity_mask)
    area_error = abs(target_hotspot["pixels"] - unity_hotspot["pixels"]) / target_hotspot["pixels"]
    center_error = float(np.linalg.norm(
        np.array(target_hotspot["centroid"]) - np.array(unity_hotspot["centroid"])
    ))
    aspect_error = abs(target_hotspot["bboxAspect"] - unity_hotspot["bboxAspect"]) / target_hotspot["bboxAspect"]
    compactness_error = abs(
        target_hotspot["compactness"] - unity_hotspot["compactness"]
    ) / target_hotspot["compactness"]

    target_clay_gradient = linear_gradient(target_clay, common)
    unity_clay_gradient = linear_gradient(unity_clay, common)
    target_vector = np.array([
        target_clay_gradient["gradientX"],
        target_clay_gradient["gradientY"],
    ])
    unity_vector = np.array([
        unity_clay_gradient["gradientX"],
        unity_clay_gradient["gradientY"],
    ])
    gradient_direction = float(
        np.dot(target_vector, unity_vector)
        / max(np.linalg.norm(target_vector) * np.linalg.norm(unity_vector), 1e-9)
    )
    gradient_magnitude_error = abs(
        target_clay_gradient["gradientMagnitude"]
        - unity_clay_gradient["gradientMagnitude"]
    ) / max(target_clay_gradient["gradientMagnitude"], 1e-9)
    target_contact = contact_shadow(target_clay, target_mask)
    unity_contact = contact_shadow(unity_clay, unity_mask)
    contact_error = abs(target_contact["contrast"] - unity_contact["contrast"]) / max(
        abs(target_contact["contrast"]), 1.0
    )

    import_report = json.loads(UNITY_IMPORT.read_text())
    target_box = bbox(target_mask)
    unity_box = bbox(unity_mask)
    target_center = centroid(target_mask)
    unity_center = centroid(unity_mask)
    report = {
        "schemaVersion": 2,
        "gate": "11-unity-parity",
        "revision": 10,
        "status": "blocked-not-ready-for-review",
        "alignmentPolicy": {
            "resolution": [1400, 1100],
            "sameFullFrame": True,
            "independentCropping": False,
            "postAlignment": False,
            "metricSpace": "raw camera output",
        },
        "files": {
            path.name: {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in required
        },
        "cameraAndObjectBeforeAlignment": {
            "unityCamera": {
                "position": import_report["cameraPosition"],
                "rotation": import_report["cameraRotation"],
                "focalLengthMm": import_report["cameraFocalLengthMm"],
                "sensorSizeMm": import_report["cameraSensorSizeMm"],
                "viewMatrix": import_report["cameraViewMatrix"],
                "projectionMatrix": import_report["cameraProjectionMatrix"],
            },
            "approvedBlenderCamera": {
                "positionMm": [74.0, -116.0, 72.0],
                "focalLengthMm": 76.0,
                "sensorWidthMm": 36.0,
                "sourceMatrixSha256": "916c5b3bd1e07ac91c7b6725fe79d3b339d7eaa722ae0c617c74c3f59f2f0259",
            },
            "objectBoundsMeters": {
                "center": import_report["objectBoundsCenter"],
                "size": import_report["objectBoundsSize"],
            },
            "targetBbox": target_box,
            "unityBbox": unity_box,
            "bboxSizeErrorPixels": [
                abs((target_box[2] - target_box[0]) - (unity_box[2] - unity_box[0])),
                abs((target_box[3] - target_box[1]) - (unity_box[3] - unity_box[1])),
            ],
            "centroidErrorPixels": float(np.linalg.norm(
                np.array(target_center) - np.array(unity_center)
            )),
            "silhouetteIou": iou(target_mask, unity_mask),
            "edgeDistancePixels": edge_distance(target_mask, unity_mask),
        },
        "fullFrame": {
            "globalSsim": global_ssim(target, unity),
            "objectSsim": global_ssim(target, unity, common),
            "perceptualProxy": perceptual_proxy(target, unity),
            "meanAbsoluteError": float(np.abs(
                target.astype(np.float32) - unity.astype(np.float32)
            ).mean()),
            "backgroundMeanAbsoluteError": float(np.abs(
                target.astype(np.float32) - unity.astype(np.float32)
            )[background].mean()),
            "heatmapAreaFractionOver24": float(np.mean(difference > 24)),
            "regionalDeltaE76": {
                "fullFrame": lab_delta(target, unity, np.ones(target.shape[:2], bool)),
                "object": lab_delta(target, unity, common),
                "background": lab_delta(target, unity, background),
                "bloodRed": lab_delta(
                    target,
                    unity,
                    common
                    & (target[:, :, 0] > target[:, :, 1] * 2 + 10)
                    & (target[:, :, 0] > target[:, :, 2] * 2 + 10)
                    & (target[:, :, 0] > 20),
                ),
                "black": lab_delta(
                    target,
                    unity,
                    common & (target.mean(axis=2) < 12),
                ),
            },
        },
        "hotspot": {
            "blender": target_hotspot,
            "unity": unity_hotspot,
            "relativeAreaError": float(area_error),
            "centroidErrorPixels": center_error,
            "aspectRelativeError": float(aspect_error),
            "compactnessRelativeError": float(compactness_error),
        },
        "clay": {
            "blenderGradient": target_clay_gradient,
            "unityGradient": unity_clay_gradient,
            "gradientDirectionCosine": gradient_direction,
            "gradientMagnitudeRelativeError": float(gradient_magnitude_error),
            "blenderContactShadow": target_contact,
            "unityContactShadow": unity_contact,
            "contactShadowRelativeError": float(contact_error),
        },
        "tolerances": {
            "silhouetteIouMin": 0.995,
            "bboxCentroidErrorMaxPx": 2.0,
            "fullFrameSsimMin": 0.78,
            "perceptualProxyMax": 0.065,
            "backgroundMaeMax": 12.0,
            "heatmapAreaOver24Max": 0.12,
            "hotspotAreaRelativeErrorMax": 0.08,
            "hotspotCentroidErrorMaxPx": 12.0,
            "hotspotAspectRelativeErrorMax": 0.15,
            "clayGradientDirectionCosineMin": 0.80,
            "clayGradientMagnitudeRelativeErrorMax": 0.30,
            "contactShadowRelativeErrorMax": 0.35,
        },
    }
    tolerance = report["tolerances"]
    report["checks"] = {
        "sameFullFrame": True,
        "cameraAndBbox": (
            report["cameraAndObjectBeforeAlignment"]["silhouetteIou"]
            >= tolerance["silhouetteIouMin"]
            and report["cameraAndObjectBeforeAlignment"]["centroidErrorPixels"]
            <= tolerance["bboxCentroidErrorMaxPx"]
        ),
        "fullFrameSsim": report["fullFrame"]["globalSsim"] >= tolerance["fullFrameSsimMin"],
        "perceptual": (
            report["fullFrame"]["perceptualProxy"]["combined"]
            <= tolerance["perceptualProxyMax"]
        ),
        "background": (
            report["fullFrame"]["backgroundMeanAbsoluteError"]
            <= tolerance["backgroundMaeMax"]
        ),
        "heatmapArea": (
            report["fullFrame"]["heatmapAreaFractionOver24"]
            <= tolerance["heatmapAreaOver24Max"]
        ),
        "hotspot": (
            area_error <= tolerance["hotspotAreaRelativeErrorMax"]
            and center_error <= tolerance["hotspotCentroidErrorMaxPx"]
            and aspect_error <= tolerance["hotspotAspectRelativeErrorMax"]
        ),
        "clayGradient": (
            gradient_direction >= tolerance["clayGradientDirectionCosineMin"]
            and gradient_magnitude_error
            <= tolerance["clayGradientMagnitudeRelativeErrorMax"]
        ),
        "contactShadow": (
            contact_error <= tolerance["contactShadowRelativeErrorMax"]
        ),
        "zeroEmission": bool(import_report["zeroEmission"]),
        "shippingUntouched": (
            not import_report["shippingSceneModified"]
            and import_report["oldShippingModelDefault"]
            and not import_report["gate12Started"]
            and not import_report["buildInstallDevice"]
        ),
    }
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    make_board(target, unity, target_clay, unity_clay, heat, report)
    print(json.dumps({
        "pass": report["pass"],
        "checks": report["checks"],
        "fullFrame": report["fullFrame"],
        "hotspot": report["hotspot"],
        "clay": report["clay"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
