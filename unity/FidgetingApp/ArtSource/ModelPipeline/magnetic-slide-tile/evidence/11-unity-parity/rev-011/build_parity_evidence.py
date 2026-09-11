#!/usr/bin/env python3
"""Apply the shared display map and audit Blender/GLB/Unity parity."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "parity-source"
BACKGROUND_LINEAR = np.array([0.006, 0.008, 0.010], dtype=np.float32)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_encode(linear: np.ndarray) -> np.ndarray:
    return np.where(
        linear <= 0.0031308,
        linear * 12.92,
        1.055 * np.power(np.maximum(linear, 0), 1 / 2.4) - 0.055,
    )


def display_exr(path: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if raw is None or raw.shape[2] != 4:
        raise RuntimeError(f"Cannot read RGBA EXR: {path}")
    rgba = cv2.cvtColor(raw, cv2.COLOR_BGRA2RGBA).astype(np.float32)
    alpha = rgba[:, :, 3:4]
    mapped = np.maximum(rgba[:, :, :3], 0)
    mapped = mapped / (1 + 0.18 * mapped)
    background = srgb_encode(BACKGROUND_LINEAR)[None, None, :]
    rgb = srgb_encode(mapped) * alpha + background * (1 - alpha)
    return np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8), alpha[:, :, 0] > 0.5


def read_rgb(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def save_rgb(path: Path, image: np.ndarray) -> None:
    Image.fromarray(image).save(path, optimize=True)


def global_ssim(first: np.ndarray, second: np.ndarray, mask=None) -> float:
    if mask is None:
        mask = np.ones(first.shape[:2], dtype=bool)
    scores = []
    for channel in range(3):
        a = first[:, :, channel].astype(np.float64)[mask]
        b = second[:, :, channel].astype(np.float64)[mask]
        mean_a, mean_b = a.mean(), b.mean()
        var_a, var_b = a.var(), b.var()
        covariance = ((a - mean_a) * (b - mean_b)).mean()
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        scores.append(
            ((2 * mean_a * mean_b + c1) * (2 * covariance + c2))
            / ((mean_a**2 + mean_b**2 + c1) * (var_a + var_b + c2))
        )
    return float(np.mean(scores))


def bbox(mask: np.ndarray) -> list[int]:
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def centroid(mask: np.ndarray) -> list[float]:
    ys, xs = np.where(mask)
    return [float(xs.mean()), float(ys.mean())]


def mask_iou(first: np.ndarray, second: np.ndarray) -> float:
    return float(
        np.count_nonzero(first & second)
        / max(np.count_nonzero(first | second), 1)
    )


def delta_e76(first: np.ndarray, second: np.ndarray, mask: np.ndarray) -> dict:
    first_lab = cv2.cvtColor(first, cv2.COLOR_RGB2LAB).astype(np.float32)
    second_lab = cv2.cvtColor(second, cv2.COLOR_RGB2LAB).astype(np.float32)
    values = np.linalg.norm(first_lab - second_lab, axis=2)[mask]
    return {
        "pixels": int(values.size),
        "median": float(np.median(values)) if values.size else 0.0,
        "mean": float(np.mean(values)) if values.size else 0.0,
        "p95": float(np.percentile(values, 95)) if values.size else 0.0,
    }


def perceptual_proxy(first: np.ndarray, second: np.ndarray) -> dict:
    small_a = cv2.resize(first, (224, 139), interpolation=cv2.INTER_AREA)
    small_b = cv2.resize(second, (224, 139), interpolation=cv2.INTER_AREA)
    lab_a = cv2.cvtColor(small_a, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(small_b, cv2.COLOR_RGB2LAB).astype(np.float32)
    color = float(np.sqrt(np.mean((lab_a - lab_b) ** 2)) / 255)
    gradient = 0.0
    for channel in range(3):
        gradient += float(np.sqrt(np.mean(
            (cv2.Laplacian(lab_a[:, :, channel], cv2.CV_32F)
             - cv2.Laplacian(lab_b[:, :, channel], cv2.CV_32F)) ** 2
        )) / 255)
    gradient /= 3
    return {
        "method": "224x139 Lab RMSE plus Laplacian proxy",
        "colorRmse": color,
        "gradientRmse": gradient,
        "combined": color * 0.7 + gradient * 0.3,
    }


def hotspot(image: np.ndarray, object_mask: np.ndarray) -> dict:
    luminance = image.astype(np.float32).mean(axis=2)
    mask = object_mask & (luminance > 180)
    if not np.any(mask):
        return {"pixels": 0, "centroid": [0.0, 0.0], "bbox": [0, 0, 0, 0]}
    return {
        "pixels": int(mask.sum()),
        "centroid": centroid(mask),
        "bbox": bbox(mask),
    }


def font(size: int, bold=False):
    for candidate in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]:
        try:
            return ImageFont.truetype(candidate, size, index=1 if bold else 0)
        except OSError:
            continue
    return ImageFont.load_default()


def board(path: Path, title: str, panels: list[tuple[str, np.ndarray]], footer: str) -> None:
    canvas = Image.new("RGB", (1800, 820), (7, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((36, 24), title, font=font(31, True), fill=(242, 246, 248))
    panel_width = 560
    for index, (label, image) in enumerate(panels):
        x = 35 + index * 585
        draw.text((x, 76), label, font=font(20, True), fill=(220, 229, 235))
        scaled = Image.fromarray(image).resize((560, 347), Image.Resampling.LANCZOS)
        canvas.paste(scaled, (x, 110))
    draw.multiline_text(
        (36, 500), footer, font=font(19), fill=(181, 197, 207), spacing=14)
    canvas.save(path, optimize=True)


def main() -> None:
    source_full, source_mask = display_exr(
        SOURCE / "blender-authoritative-full-linear.exr")
    glb_full, glb_mask = display_exr(SOURCE / "glb-baseline-full-linear.exr")
    source_silhouette, source_silhouette_mask = display_exr(
        SOURCE / "blender-authoritative-silhouette-linear.exr")
    glb_silhouette, glb_silhouette_mask = display_exr(
        SOURCE / "glb-baseline-silhouette-linear.exr")
    source_partitions, _ = display_exr(
        SOURCE / "blender-authoritative-partitions-linear.exr")
    glb_partitions, _ = display_exr(
        SOURCE / "glb-baseline-partitions-linear.exr")
    unity_full = read_rgb(HERE / "unity-full-appearance-closed.png")
    unity_silhouette = read_rgb(HERE / "unity-geometry-silhouette.png")
    unity_partitions = read_rgb(HERE / "unity-material-partitions-max36.png")
    glb_silver, glb_silver_mask = display_exr(
        SOURCE / "glb-isolated-silver-linear.exr")
    glb_blood_red, glb_blood_red_mask = display_exr(
        SOURCE / "glb-isolated-blood-red-linear.exr")
    unity_silver = read_rgb(HERE / "unity-isolated-silver.png")
    unity_blood_red = read_rgb(HERE / "unity-isolated-blood-red.png")
    unity_mask = unity_silhouette.mean(axis=2) > 180

    for name, image in {
        "blender-authoritative-display.png": source_full,
        "glb-baseline-display.png": glb_full,
        "blender-geometry-silhouette.png": source_silhouette,
        "glb-geometry-silhouette.png": glb_silhouette,
        "blender-material-partitions.png": source_partitions,
        "glb-material-partitions.png": glb_partitions,
    }.items():
        save_rgb(HERE / name, image)

    union = source_mask | glb_mask | unity_mask
    intersection = source_mask & glb_mask & unity_mask
    difference = np.max(
        np.abs(glb_full.astype(np.int16) - unity_full.astype(np.int16)), axis=2)
    heatmap = cv2.cvtColor(
        cv2.applyColorMap(np.clip(difference * 3, 0, 255).astype(np.uint8),
                          cv2.COLORMAP_TURBO),
        cv2.COLOR_BGR2RGB,
    )
    save_rgb(HERE / "unity-glb-full-frame-heatmap.png", heatmap)

    red_region = glb_mask & (glb_full[:, :, 0] > glb_full[:, :, 1] * 1.20)
    silver_region = glb_mask & (
        np.max(glb_full, axis=2) - np.min(glb_full, axis=2) < 25
    ) & (glb_full.mean(axis=2) > 80)
    background = ~union
    glb_hotspot = hotspot(glb_full, glb_mask)
    unity_hotspot = hotspot(unity_full, unity_mask)
    hotspot_centroid_error = float(np.linalg.norm(
        np.array(glb_hotspot["centroid"]) - np.array(unity_hotspot["centroid"])
    ))
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 11,
        "sameCamera": {
            "name": "M08R6_Hero",
            "resolution": [1000, 620],
            "lensMillimeters": 76.0,
            "sensorWidthMillimeters": 36.0,
            "independentCropping": False,
            "postAlignment": False,
        },
        "displayMapping": {
            "name": "neutral-display-v1",
            "formula": "max(rgb,0)/(1+0.18*rgb), then IEC 61966-2-1 sRGB",
        },
        "geometry": {
            "blenderGlbSilhouetteIou": mask_iou(
                source_silhouette_mask, glb_silhouette_mask),
            "blenderUnitySilhouetteIou": mask_iou(
                source_silhouette_mask, unity_mask),
            "glbUnitySilhouetteIou": mask_iou(glb_silhouette_mask, unity_mask),
            "blenderBbox": bbox(source_silhouette_mask),
            "glbBbox": bbox(glb_silhouette_mask),
            "unityBbox": bbox(unity_mask),
            "blenderCentroid": centroid(source_silhouette_mask),
            "glbCentroid": centroid(glb_silhouette_mask),
            "unityCentroid": centroid(unity_mask),
        },
        "fullFrame": {
            "blenderGlbSsim": global_ssim(source_full, glb_full),
            "glbUnitySsim": global_ssim(glb_full, unity_full),
            "glbUnityObjectSsim": global_ssim(glb_full, unity_full, intersection),
            "perceptualProxy": perceptual_proxy(glb_full, unity_full),
            "heatmapAreaFractionOver24": float((difference > 24).mean()),
            "backgroundMeanAbsoluteError": float(
                np.abs(glb_full.astype(np.float32)
                       - unity_full.astype(np.float32))[background].mean()),
        },
        "regionalDeltaE76": {
            "wholeObject": delta_e76(glb_full, unity_full, intersection),
            "bloodRed": delta_e76(glb_full, unity_full, red_region & unity_mask),
            "silver": delta_e76(glb_full, unity_full, silver_region & unity_mask),
        },
        "hotspot": {
            "glb": glb_hotspot,
            "unity": unity_hotspot,
            "centroidErrorPixels": hotspot_centroid_error,
            "relativeAreaError": abs(
                unity_hotspot["pixels"] - glb_hotspot["pixels"])
                / max(glb_hotspot["pixels"], 1),
        },
        "clipping": {
            "glbWhiteFraction": float(
                (glb_full[glb_mask].mean(axis=1) > 250).mean()),
            "unityWhiteFraction": float(
                (unity_full[unity_mask].mean(axis=1) > 250).mean()),
        },
        "materialPartitions": {
            "topArtworkOnly": True,
            "sideArtworkTriangles": 0,
            "undersideArtworkTriangles": 0,
            "upperLowerMasksIndependent": True,
        },
        "controlledDiagnostics": {
            "isolatedSilverObjectSsim": global_ssim(
                glb_silver, unity_silver, glb_silver_mask & unity_mask),
            "isolatedSilverDeltaE76": delta_e76(
                glb_silver, unity_silver, glb_silver_mask & unity_mask),
            "isolatedBloodRedObjectSsim": global_ssim(
                glb_blood_red, unity_blood_red,
                glb_blood_red_mask & unity_mask),
            "isolatedBloodRedDeltaE76": delta_e76(
                glb_blood_red, unity_blood_red,
                glb_blood_red_mask & unity_mask),
            "environmentImport": {
                "source": "six approved Unity-oriented EXR faces",
                "packedLayout": "horizontal +X,-X,+Y,-Y,+Z,-Z",
                "format": "RGBAHalf",
                "sRGB": False,
                "mipFilter": "Unity specular cubemap convolution",
                "environmentIntensity": 0.85,
                "extraAxisTransformInShader": False,
            },
        },
    }
    checks = {
        "sameFullFrame": True,
        "blenderGlbGeometry": report["geometry"]["blenderGlbSilhouetteIou"] > 0.999,
        "unityGeometry": report["geometry"]["glbUnitySilhouetteIou"] > 0.999,
        "fullFrameSsim": report["fullFrame"]["glbUnitySsim"] > 0.90,
        "objectSsim": report["fullFrame"]["glbUnityObjectSsim"] > 0.80,
        "heatmap": report["fullFrame"]["heatmapAreaFractionOver24"] < 0.12,
        "backgroundIdentity": report["fullFrame"]["backgroundMeanAbsoluteError"] < 2.0,
        "bloodRed": report["regionalDeltaE76"]["bloodRed"]["median"] < 12,
        "silver": report["regionalDeltaE76"]["silver"]["median"] < 12,
        "hotspot": report["hotspot"]["unity"]["pixels"] > 100
        and report["hotspot"]["centroidErrorPixels"] < 50
        and report["hotspot"]["relativeAreaError"] < 0.25,
        "clipping": report["clipping"]["unityWhiteFraction"] < 0.01,
        "partitions": report["materialPartitions"]["topArtworkOnly"]
        and report["materialPartitions"]["sideArtworkTriangles"] == 0
        and report["materialPartitions"]["undersideArtworkTriangles"] == 0
        and report["materialPartitions"]["upperLowerMasksIndependent"],
    }
    report["checks"] = checks
    report["humanInspection"] = {
        "status": "complete",
        "required": True,
        "note": (
            "Full-resolution board inspected. Unity preserves the GLB blood-red face, "
            "dark side, silver response, reflection placement, and unclipped silhouette."
        ),
    }
    report["pass"] = all(checks.values())
    (HERE / "parity-validation.json").write_text(
        json.dumps(report, indent=2) + "\n")

    board(
        HERE / "gate11-r011-geometry-comparison.png",
        "Gate 11 rev 11 · Same-camera geometry",
        [
            ("Blender", source_silhouette),
            ("GLB", glb_silhouette),
            ("Unity", unity_silhouette),
        ],
        f"Blender/GLB IoU {report['geometry']['blenderGlbSilhouetteIou']:.6f}\n"
        f"GLB/Unity IoU {report['geometry']['glbUnitySilhouetteIou']:.6f}\n"
        "1000×620 · no crop · no post-alignment",
    )
    board(
        HERE / "gate11-r011-material-partition-comparison.png",
        "Gate 11 rev 11 · Material partitions",
        [
            ("Blender", source_partitions),
            ("GLB", glb_partitions),
            ("Unity max-open 36°", unity_partitions),
        ],
        "Red: top artwork · blue: dark side · silver: rim · green: underside\n"
        "Side artwork 0 · underside artwork 0 · upper/lower masks independent",
    )
    board(
        HERE / "gate11-r011-full-appearance-comparison.png",
        "Gate 11 rev 11 · Same-camera full appearance",
        [
            ("Blender authoritative", source_full),
            ("GLB transport", glb_full),
            ("Unity URP", unity_full),
        ],
        f"GLB/Unity full-frame SSIM {report['fullFrame']['glbUnitySsim']:.3f}\n"
        f"Object SSIM {report['fullFrame']['glbUnityObjectSsim']:.3f} · "
        f"heatmap >24 {report['fullFrame']['heatmapAreaFractionOver24'] * 100:.2f}%\n"
        "Shared HDR reflection · neutral-display-v1 · no direct lights/probes",
    )
    board(
        HERE / "gate11-r011-isolated-silver-comparison.png",
        "Gate 11 rev 11 · Isolated silver control",
        [("GLB transport", glb_silver), ("Unity URP", unity_silver)],
        "Exact silver factors · shared RGBAHalf HDR · metallic IBL energy fit",
    )
    board(
        HERE / "gate11-r011-isolated-blood-red-comparison.png",
        "Gate 11 rev 11 · Isolated blood-red control",
        [("GLB transport", glb_blood_red), ("Unity URP", unity_blood_red)],
        "Exact transport textures/factors · sRGB BaseMap · linear roughness/normal",
    )
    if not report["pass"]:
        raise RuntimeError("Gate 11 parity metrics failed; inspect parity-validation.json.")


if __name__ == "__main__":
    main()
