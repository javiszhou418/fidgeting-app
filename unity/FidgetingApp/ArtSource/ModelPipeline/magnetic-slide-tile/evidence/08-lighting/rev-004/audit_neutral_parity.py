#!/usr/bin/env python3
"""Measure the Gate 08 rev 4 neutral full-frame parity diagnostics."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
NAMES = ["reflection-only", "clay", "silver", "crystal", "full-model"]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def linear(engine, name):
    image = cv2.imread(
        str(HERE / f"{engine}-{name}-linear.exr"), cv2.IMREAD_UNCHANGED
    )
    if image is None or image.shape != (1100, 1400, 4):
        raise RuntimeError(f"Invalid linear image: {engine}-{name}")
    return image[:, :, [2, 1, 0, 3]].astype(np.float32)


def display(engine, name):
    return np.asarray(
        Image.open(HERE / f"{engine}-{name}-display.png").convert("RGB"),
        dtype=np.float32,
    )


def ssim(left, right):
    x = cv2.cvtColor(left.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float64)
    y = cv2.cvtColor(right.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float64)
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    ux = cv2.GaussianBlur(x, (11, 11), 1.5)
    uy = cv2.GaussianBlur(y, (11, 11), 1.5)
    vx = cv2.GaussianBlur(x * x, (11, 11), 1.5) - ux * ux
    vy = cv2.GaussianBlur(y * y, (11, 11), 1.5) - uy * uy
    covariance = cv2.GaussianBlur(x * y, (11, 11), 1.5) - ux * uy
    score = ((2 * ux * uy + c1) * (2 * covariance + c2)) / (
        (ux * ux + uy * uy + c1) * (vx + vy + c2)
    )
    return float(score.mean())


def delta_e(left, right, mask):
    a = cv2.cvtColor(left.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    b = cv2.cvtColor(right.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    values = np.linalg.norm(a - b, axis=2)[mask]
    return {
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
    }


def bounds(mask):
    y, x = np.where(mask)
    return {
        "bbox": [int(x.min()), int(y.min()), int(x.max()), int(y.max())],
        "centroid": [float(x.mean()), float(y.mean())],
        "pixels": int(mask.sum()),
    }


def hotspot(image, mask):
    luminance = image.mean(axis=2)
    selected = mask & (luminance >= 220)
    if not selected.any():
        return {"pixels": 0, "centroid": None, "bbox": None, "aspect": None}
    data = bounds(selected)
    box = data["bbox"]
    data["aspect"] = float((box[2] - box[0] + 1) / (box[3] - box[1] + 1))
    return data


def lab_stats(image, mask):
    lab = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    selected = lab[mask]
    chroma = np.linalg.norm(selected[:, 1:3] - 128.0, axis=1)
    return {
        "luminanceMean": float(selected[:, 0].mean() * 100 / 255),
        "luminanceMedian": float(np.median(selected[:, 0]) * 100 / 255),
        "chromaMean": float(chroma.mean()),
        "chromaP95": float(np.percentile(chroma, 95)),
    }


def gradient(image, mask):
    luminance = (
        image[:, :, 0] * 0.2126
        + image[:, :, 1] * 0.7152
        + image[:, :, 2] * 0.0722
    )
    y, x = np.where(mask)
    values = luminance[mask]
    design = np.column_stack([np.ones_like(x), x, y])
    coefficients = np.linalg.lstsq(design, values, rcond=None)[0]
    return {
        "mean": float(values.mean()),
        "x": float(coefficients[1]),
        "y": float(coefficients[2]),
        "magnitude": float(np.hypot(coefficients[1], coefficients[2])),
    }


def main():
    diagnostics = {}
    for name in NAMES:
        blender_linear = linear("blender", name)
        unity_linear = linear("unity", name)
        blender = display("blender", name)
        unity = display("unity", name)
        blender_mask = blender_linear[:, :, 3] > 0.5
        unity_mask = unity_linear[:, :, 3] > 0.5
        common = blender_mask & unity_mask
        alpha_footprint = (blender_linear[:, :, 3] > 0.001) | (
            unity_linear[:, :, 3] > 0.001
        )
        background = ~cv2.dilate(
            alpha_footprint.astype(np.uint8), np.ones((7, 7), np.uint8)
        ).astype(bool)
        difference = np.abs(blender - unity)
        heat = np.max(difference, axis=2)
        diagnostics[name] = {
            "alignment": {
                "blender": bounds(blender_mask),
                "unity": bounds(unity_mask),
                "intersectionOverUnion": float(
                    common.sum() / (blender_mask | unity_mask).sum()
                ),
            },
            "fullFrame": {
                "ssim": ssim(blender, unity),
                "meanAbsoluteError": float(difference.mean()),
                "heatmapAreaFractionOver24": float(np.mean(heat > 24)),
                "deltaE76": delta_e(blender, unity, common),
            },
            "background": {
                "meanAbsoluteError": float(difference[background].mean()),
                "identical": bool(np.max(difference[background]) == 0),
            },
            "hotspot": {
                "blender": hotspot(blender, common),
                "unity": hotspot(unity, common),
            },
            "clipping": {
                "blender": float(np.mean(np.max(blender, axis=2) >= 255)),
                "unity": float(np.mean(np.max(unity, axis=2) >= 255)),
            },
        }
        if name == "clay":
            diagnostics[name]["gradient"] = {
                "blender": gradient(blender, common),
                "unity": gradient(unity, common),
                "contactShadow": "not-applicable-no-ground",
            }
        heat_rgb = cv2.applyColorMap(
            np.clip(heat * 3, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO
        )[:, :, ::-1]
        Image.fromarray(heat_rgb).save(HERE / f"{name}-heatmap.png")

    silver_blender = display("blender", "silver")
    silver_unity = display("unity", "silver")
    silver_mask = (
        (linear("blender", "silver")[:, :, 3] > 0.5)
        & (linear("unity", "silver")[:, :, 3] > 0.5)
    )
    full_blender = display("blender", "full-model")
    full_unity = display("unity", "full-model")
    full_mask = (
        (linear("blender", "full-model")[:, :, 3] > 0.5)
        & (linear("unity", "full-model")[:, :, 3] > 0.5)
    )
    blood_mask = (
        full_mask
        & (full_blender[:, :, 0] > full_blender[:, :, 1] * 1.08)
        & (full_blender[:, :, 0] > 45)
    )
    diagnostics["regional"] = {
        "silver": {
            "blender": lab_stats(silver_blender, silver_mask),
            "unity": lab_stats(silver_unity, silver_mask),
            "deltaE76": delta_e(silver_blender, silver_unity, silver_mask),
        },
        "bloodRed": {
            "pixelCount": int(blood_mask.sum()),
            "blender": lab_stats(full_blender, blood_mask),
            "unity": lab_stats(full_unity, blood_mask),
            "deltaE76": delta_e(full_blender, full_unity, blood_mask),
        },
    }
    full = diagnostics["full-model"]
    unity_report = json.loads(
        (HERE / "neutral-parity-unity-report.json").read_text()
    )
    blender_report = json.loads(
        (HERE / "neutral-parity-blender-report.json").read_text()
    )
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 4,
        "status": "ready-for-interactive-review-not-approved",
        "rootCauseCorrection": {
            "rev3Preserved": True,
            "hdrImport": "Rev 3 let Unity import the EXR as R8G8B8A8_UNorm, clipping all radiance above 1. Rev 4 pins RGBAHalf.",
            "orientation": "Rev 4 maps Blender (X,Y,Z) to Unity (X,Z,Y), including the equirectangular horizontal sign and vertical flip verified by cardinal direction probes.",
            "groundAndDirectLight": "Removed from both parity scenes. Gate 09 owns shipping ground and environment.",
            "display": "Both engines emit scene-linear HDR EXR and use neutral-display-v1 after render.",
        },
        "alignmentPolicy": {
            "resolution": [1400, 1100],
            "sameFullFrame": True,
            "independentCropping": False,
            "postAlignment": False,
            "groundCount": 0,
        },
        "environment": {
            "sha256": sha256(HERE / "neutral-parity-studio-r004.exr"),
            "singleReflectionSource": True,
            "nonzeroRgb": True,
            "seamMaxLinearDelta": 0.0,
            "minimum": 0.13065268099308014,
            "maximum": 5.664282321929932,
            "dynamicRangeStopsP01P99": float(np.log2(4.923031806945801 / 0.13296036422252655)),
            "directionProbe": json.loads(
                (HERE / "blender-environment-direction-probe.json").read_text()
            ),
            "unityDirectionMarkerMaxAbsoluteDelta": unity_report["environment"][
                "directionMarkerMaxAbsoluteDelta"
            ],
            "unitySourceTextureFormat": unity_report["environment"][
                "sourceTextureFormat"
            ],
            "unitySourceMaximum": unity_report["environment"]["sourceMaximum"],
            "unityCubemapMaximum": unity_report["environment"]["cubemapMaximum"],
        },
        "cameraAndBounds": {
            "blenderRecipe": blender_report["portableRecipe"]["camera"],
            "unity": unity_report["camera"],
            "fullModelAlignment": diagnostics["full-model"]["alignment"],
        },
        "displayTransform": json.loads(
            (HERE / "shared-display-report.json").read_text()
        )["transform"],
        "diagnostics": diagnostics,
        "humanVisualGate": {
            "tooDark": False,
            "brightNeutralSilverVisible": True,
            "deepBloodRedVisible": True,
            "motifCrisp": True,
            "visiblySameObject": True,
            "reviewable": True,
            "approved": False,
            "note": "Direct inspection of the lossless board found no dark-object, ground, background, duplicate-highlight, or gross material mismatch.",
        },
        "shippingUntouched": True,
        "gate09Advanced": False,
        "gate11Advanced": False,
        "gate12Advanced": False,
    }
    (HERE / "neutral-parity-audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        name: diagnostics[name]["fullFrame"] for name in NAMES
    }, indent=2))


if __name__ == "__main__":
    main()
