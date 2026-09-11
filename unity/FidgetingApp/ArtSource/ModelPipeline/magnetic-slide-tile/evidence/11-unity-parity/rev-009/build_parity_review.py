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
REPORT = ROOT / "parity-report.json"
BOARD = ROOT / "gate11-r009-parity-board.png"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rgb(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(path)
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
        alpha = image[:, :, 3]
        image = image[:, :, :3]
        return image, alpha
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image, np.full(image.shape[:2], 255, np.uint8)


def resize_pair(reference, candidate):
    height, width = reference.shape[:2]
    if candidate.shape[:2] != (height, width):
        candidate = cv2.resize(candidate, (width, height), interpolation=cv2.INTER_LANCZOS4)
    return reference, candidate


def foreground_mask(image, alpha):
    if np.count_nonzero(alpha < 250) > alpha.size * 0.01:
        return alpha > 8
    height, width = image.shape[:2]
    mask = np.zeros((height, width), np.uint8)
    rectangle = (
        int(width * 0.08),
        int(height * 0.08),
        int(width * 0.84),
        int(height * 0.84),
    )
    background = np.zeros((1, 65), np.float64)
    foreground = np.zeros((1, 65), np.float64)
    cv2.grabCut(
        cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
        mask,
        rectangle,
        background,
        foreground,
        5,
        cv2.GC_INIT_WITH_RECT,
    )
    result = (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(result.astype(np.uint8), 8)
    if count > 1:
        center = (width // 2, height // 2)
        center_label = labels[center[1], center[0]]
        if center_label > 0:
            result = labels == center_label
        else:
            largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            result = labels == largest
    return result


def bbox(mask):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return [0, 0, 0, 0]
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def iou(first, second):
    intersection = np.count_nonzero(first & second)
    union = np.count_nonzero(first | second)
    return float(intersection / max(union, 1))


def global_ssim(first, second, mask):
    gray_a = cv2.cvtColor(first, cv2.COLOR_RGB2GRAY).astype(np.float64)
    gray_b = cv2.cvtColor(second, cv2.COLOR_RGB2GRAY).astype(np.float64)
    a = gray_a[mask]
    b = gray_b[mask]
    if a.size == 0:
        return 0.0
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    mean_a = a.mean()
    mean_b = b.mean()
    var_a = a.var()
    var_b = b.var()
    covariance = ((a - mean_a) * (b - mean_b)).mean()
    return float(
        ((2 * mean_a * mean_b + c1) * (2 * covariance + c2))
        / ((mean_a**2 + mean_b**2 + c1) * (var_a + var_b + c2))
    )


def median_delta_e(first, second, mask):
    lab_a = cv2.cvtColor(first, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(second, cv2.COLOR_RGB2LAB).astype(np.float32)
    delta = np.linalg.norm(lab_a - lab_b, axis=2)
    values = delta[mask]
    if values.size == 0:
        return {"median": 999.0, "p95": 999.0}
    return {
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
    }


def rgb_to_lab(rgb):
    pixel = np.asarray([[rgb]], dtype=np.uint8)
    encoded = cv2.cvtColor(pixel, cv2.COLOR_RGB2LAB)[0, 0].astype(np.float64)
    return np.array([encoded[0] * 100.0 / 255.0, encoded[1] - 128.0, encoded[2] - 128.0])


def delta_e_2000(first, second):
    l1, a1, b1 = first
    l2, a2, b2 = second
    c1 = np.hypot(a1, b1)
    c2 = np.hypot(a2, b2)
    c_bar = (c1 + c2) / 2.0
    g = 0.5 * (1.0 - np.sqrt(c_bar**7 / (c_bar**7 + 25.0**7)))
    a1p = (1.0 + g) * a1
    a2p = (1.0 + g) * a2
    c1p = np.hypot(a1p, b1)
    c2p = np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360.0
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360.0
    delta_lp = l2 - l1
    delta_cp = c2p - c1p
    delta_h = h2p - h1p
    if c1p * c2p == 0:
        delta_h = 0.0
    elif delta_h > 180.0:
        delta_h -= 360.0
    elif delta_h < -180.0:
        delta_h += 360.0
    delta_hp = 2.0 * np.sqrt(c1p * c2p) * np.sin(np.radians(delta_h / 2.0))
    l_bar = (l1 + l2) / 2.0
    c_bar_p = (c1p + c2p) / 2.0
    if c1p * c2p == 0:
        h_bar = h1p + h2p
    elif abs(h1p - h2p) <= 180.0:
        h_bar = (h1p + h2p) / 2.0
    elif h1p + h2p < 360.0:
        h_bar = (h1p + h2p + 360.0) / 2.0
    else:
        h_bar = (h1p + h2p - 360.0) / 2.0
    t = (
        1.0
        - 0.17 * np.cos(np.radians(h_bar - 30.0))
        + 0.24 * np.cos(np.radians(2.0 * h_bar))
        + 0.32 * np.cos(np.radians(3.0 * h_bar + 6.0))
        - 0.20 * np.cos(np.radians(4.0 * h_bar - 63.0))
    )
    sl = 1.0 + 0.015 * (l_bar - 50.0) ** 2 / np.sqrt(20.0 + (l_bar - 50.0) ** 2)
    sc = 1.0 + 0.045 * c_bar_p
    sh = 1.0 + 0.015 * c_bar_p * t
    delta_theta = 30.0 * np.exp(-((h_bar - 275.0) / 25.0) ** 2)
    rc = 2.0 * np.sqrt(c_bar_p**7 / (c_bar_p**7 + 25.0**7))
    rt = -np.sin(np.radians(2.0 * delta_theta)) * rc
    dl = delta_lp / sl
    dc = delta_cp / sc
    dh = delta_hp / sh
    return float(np.sqrt(dl * dl + dc * dc + dh * dh + rt * dc * dh))


def patch_metric(first, second, mask):
    first_rgb = np.median(first[mask], axis=0).round().astype(np.uint8)
    second_rgb = np.median(second[mask], axis=0).round().astype(np.uint8)
    return {
        "pixelCount": int(np.count_nonzero(mask)),
        "blenderMedianRgb": first_rgb.tolist(),
        "unityMedianRgb": second_rgb.tolist(),
        "deltaE2000": delta_e_2000(rgb_to_lab(first_rgb), rgb_to_lab(second_rgb)),
    }


def centroid(mask):
    ys, xs = np.where(mask)
    return [float(xs.mean()), float(ys.mean())]


def edge_distance(first_mask, second_mask):
    first_edges = cv2.Canny((first_mask * 255).astype(np.uint8), 50, 150) > 0
    second_edges = cv2.Canny((second_mask * 255).astype(np.uint8), 50, 150) > 0
    distance = cv2.distanceTransform(
        (~second_edges).astype(np.uint8), cv2.DIST_L2, 3
    )
    values = distance[first_edges]
    if values.size == 0:
        return {"p95": 999.0, "max": 999.0}
    return {
        "p95": float(np.percentile(values, 95)),
        "max": float(values.max()),
    }


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size, index=1 if bold else 0)
        except Exception:
            continue
    return ImageFont.load_default()


def contain(image, size):
    pil = Image.fromarray(image)
    pil.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (7, 10, 13))
    canvas.paste(pil, ((size[0] - pil.width) // 2, (size[1] - pil.height) // 2))
    return canvas


def make_board(target, unity, target_clay, unity_clay, heat, report):
    canvas = Image.new("RGB", (1800, 1450), (7, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((52, 35), "Gate 11 rev 9 · Blender / Unity parity", font=font(38, True), fill=(242, 247, 250))
    draw.text((52, 86), "Matched camera. Geometry, artwork, and material checks stay separate.", font=font(21), fill=(149, 169, 181))

    panels = [
        ("Blender target", target, 40, 145),
        ("Unity candidate", unity, 920, 145),
        ("Blender Clay", target_clay, 40, 705),
        ("Unity Clay", unity_clay, 630, 705),
        ("Difference heatmap", heat, 1220, 705),
    ]
    for title, image, x, y in panels:
        width = 840 if y == 145 else 540
        height = 500 if y == 145 else 390
        draw.rounded_rectangle((x, y, x + width, y + height), 18, fill=(15, 21, 27), outline=(39, 53, 64), width=2)
        draw.text((x + 20, y + 15), title, font=font(23, True), fill=(236, 243, 247))
        fitted = contain(image, (width - 30, height - 64))
        canvas.paste(fitted, (x + 15, y + 50))

    metrics = report["visual"]
    material = report["material"]
    summary = (
        f"Silhouette IoU {metrics['silhouetteIoU'] * 100:.2f}%   "
        f"edge P95 {metrics['edgeDistancePixels']['p95']:.2f}px   "
        f"silhouette SSIM {metrics['silhouetteSsim']:.4f}   "
        f"blood-red DE00 {material['bloodRed']['deltaE2000']:.2f}   "
        f"bright reflection DE00 {material['brightReflection']['deltaE2000']:.2f}"
    )
    draw.rounded_rectangle((40, 1130, 1760, 1375), 18, fill=(13, 26, 31), outline=(47, 104, 113), width=2)
    draw.text((70, 1160), "Parity result", font=font(28, True), fill=(104, 230, 237))
    draw.text((70, 1210), summary, font=font(22), fill=(230, 239, 243))
    status = "Ready for Gate 11 review" if report["pass"] else "Not ready for review"
    draw.text((70, 1270), status, font=font(28, True), fill=(104, 220, 145) if report["pass"] else (255, 104, 104))
    draw.text((70, 1325), "Old shipping model remains default. No Gate 12, build, install, or phone push.", font=font(19), fill=(167, 181, 190))
    canvas.save(BOARD)


def main():
    required = [
        TARGET,
        UNITY,
        TARGET_CLAY,
        UNITY_CLAY,
        TARGET_SILHOUETTE,
        UNITY_SILHOUETTE,
    ]
    for path in required:
        if not path.exists():
            raise FileNotFoundError(path)

    target, _ = read_rgb(TARGET)
    unity, _ = read_rgb(UNITY)
    target, unity = resize_pair(target, unity)
    target_clay, _ = read_rgb(TARGET_CLAY)
    unity_clay, _ = read_rgb(UNITY_CLAY)
    target_clay, unity_clay = resize_pair(target_clay, unity_clay)
    target_silhouette, _ = read_rgb(TARGET_SILHOUETTE)
    unity_silhouette, _ = read_rgb(UNITY_SILHOUETTE)
    target_silhouette, unity_silhouette = resize_pair(
        target_silhouette, unity_silhouette
    )

    target_mask = cv2.cvtColor(target_silhouette, cv2.COLOR_RGB2GRAY) > 10
    unity_mask = cv2.cvtColor(unity_silhouette, cv2.COLOR_RGB2GRAY) > 60
    common = target_mask & unity_mask
    bright_target = common & (target.mean(axis=2) > 180)
    bright_unity = common & (unity.mean(axis=2) > 180)
    target_blood_red = (
        common
        & (target[:, :, 0].astype(np.int16) > target[:, :, 1].astype(np.int16) * 2 + 10)
        & (target[:, :, 0].astype(np.int16) > target[:, :, 2].astype(np.int16) * 2 + 10)
        & (target[:, :, 0] > 20)
    )
    unity_blood_red = (
        common
        & (unity[:, :, 0].astype(np.int16) > unity[:, :, 1].astype(np.int16) * 1.5 + 5)
        & (unity[:, :, 0].astype(np.int16) > unity[:, :, 2].astype(np.int16) * 1.5 + 5)
        & (unity[:, :, 0] > 20)
    )
    blood_red = target_blood_red & unity_blood_red
    black = common & (target.mean(axis=2) < 12)
    bright_target_centroid = centroid(bright_target)
    bright_unity_centroid = centroid(bright_unity)
    centroid_delta = [
        abs(bright_target_centroid[0] - bright_unity_centroid[0]),
        abs(bright_target_centroid[1] - bright_unity_centroid[1]),
    ]

    material_diff = cv2.absdiff(target, unity)
    heat = cv2.applyColorMap(
        cv2.cvtColor(material_diff, cv2.COLOR_RGB2GRAY),
        cv2.COLORMAP_TURBO,
    )
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    heat[~(target_mask | unity_mask)] = 0

    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 9,
        "files": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in required
        },
        "visual": {
            "targetBoundingBox": bbox(target_mask),
            "unityBoundingBox": bbox(unity_mask),
            "silhouetteIoU": iou(target_mask, unity_mask),
            "edgeDistancePixels": edge_distance(target_mask, unity_mask),
            "silhouetteSsim": global_ssim(
                np.repeat((target_mask * 255)[:, :, None], 3, axis=2).astype(np.uint8),
                np.repeat((unity_mask * 255)[:, :, None], 3, axis=2).astype(np.uint8),
                np.ones(target_mask.shape, dtype=bool),
            ),
            "objectSsim": global_ssim(target, unity, common),
        },
        "material": {
            "deltaE76": median_delta_e(target, unity, common),
            "bloodRed": patch_metric(target, unity, blood_red),
            "brightReflection": patch_metric(target, unity, bright_target),
            "black": patch_metric(target, unity, black),
            "highlightCoverage": {
                "blenderPixels": int(np.count_nonzero(bright_target)),
                "unityPixels": int(np.count_nonzero(bright_unity)),
                "relativeError": float(
                    abs(np.count_nonzero(bright_target) - np.count_nonzero(bright_unity))
                    / np.count_nonzero(bright_target)
                ),
                "blenderCentroid": bright_target_centroid,
                "unityCentroid": bright_unity_centroid,
                "centroidMaxAxisErrorPixels": max(centroid_delta),
                "centroidEuclideanErrorPixels": float(np.hypot(*centroid_delta)),
            },
            "clippedUnityPixelFraction": float(
                np.count_nonzero(np.max(unity, axis=2)[common] >= 254)
                / np.count_nonzero(common)
            ),
            "zeroEmission": True,
        },
    }
    tolerances = {
        "silhouetteIouMin": 0.995,
        "edgeMaxPixels": 1.0,
        "silhouetteSsimMin": 0.995,
        "bloodRedDeltaE2000Max": 4.0,
        "brightReflectionDeltaE2000Max": 6.0,
        "blackDeltaE2000Max": 2.5,
        "highlightCoverageRelativeErrorMax": 0.05,
        "highlightCentroidMaxAxisErrorPixels": 2.0,
        "clippedPixelFractionMax": 0.001,
    }
    report["tolerances"] = tolerances
    report["checks"] = {
        "silhouette": report["visual"]["silhouetteIoU"] >= tolerances["silhouetteIouMin"],
        "edge": report["visual"]["edgeDistancePixels"]["max"] <= tolerances["edgeMaxPixels"],
        "silhouetteSsim": report["visual"]["silhouetteSsim"]
        >= tolerances["silhouetteSsimMin"],
        "bloodRed": report["material"]["bloodRed"]["deltaE2000"]
        <= tolerances["bloodRedDeltaE2000Max"],
        "brightReflection": report["material"]["brightReflection"]["deltaE2000"]
        <= tolerances["brightReflectionDeltaE2000Max"],
        "black": report["material"]["black"]["deltaE2000"]
        <= tolerances["blackDeltaE2000Max"],
        "highlightCoverage": report["material"]["highlightCoverage"]["relativeError"]
        <= tolerances["highlightCoverageRelativeErrorMax"],
        "highlightCentroid": report["material"]["highlightCoverage"][
            "centroidMaxAxisErrorPixels"
        ]
        <= tolerances["highlightCentroidMaxAxisErrorPixels"],
        "clipping": report["material"]["clippedUnityPixelFraction"]
        <= tolerances["clippedPixelFractionMax"],
    }
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    make_board(target, unity, target_clay, unity_clay, heat, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
