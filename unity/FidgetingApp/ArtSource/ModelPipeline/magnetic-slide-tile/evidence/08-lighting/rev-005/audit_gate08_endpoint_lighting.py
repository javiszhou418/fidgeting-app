#!/usr/bin/env python3
"""Audit Gate 08 rev 5 lighting, parity, and endpoint evidence."""

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
SOURCE_SHA = "953929045453e1d9c3bb46612da85a70eb1a078a115a103040778d2703988588"
CONTRACT_SHA = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def linear(name):
    image = cv2.imread(str(HERE / name), cv2.IMREAD_UNCHANGED)
    if image is None or image.shape != (1100, 1400, 4):
        raise RuntimeError(f"Invalid EXR: {name}")
    return image[:, :, [2, 1, 0, 3]].astype(np.float32)


def display(name):
    image = np.asarray(Image.open(HERE / name).convert("RGB"), dtype=np.float32)
    if image.shape != (1100, 1400, 3):
        raise RuntimeError(f"Invalid display image: {name}")
    return image


def bounds(mask):
    y, x = np.where(mask)
    return {
        "bbox": [int(x.min()), int(y.min()), int(x.max()), int(y.max())],
        "centroid": [float(x.mean()), float(y.mean())],
        "pixels": int(mask.sum()),
    }


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
    return float(np.mean(((2 * ux * uy + c1) * (2 * covariance + c2)) / (
        (ux * ux + uy * uy + c1) * (vx + vy + c2)
    )))


def main():
    blender_report = json.loads((HERE / "blender-lighting-report.json").read_text())
    unity_report = json.loads((HERE / "neutral-parity-unity-report.json").read_text())
    display_report = json.loads((HERE / "shared-display-report.json").read_text())
    blender_linear = linear("blender-full-model-linear.exr")
    unity_linear = linear("unity-full-model-linear.exr")
    blender = display("blender-full-model-display.png")
    unity = display("unity-full-model-display.png")
    blender_mask = blender_linear[..., 3] > 0.5
    unity_mask = unity_linear[..., 3] > 0.5
    common = blender_mask & unity_mask
    union = blender_mask | unity_mask
    difference = np.abs(blender - unity)
    heat = np.max(difference, axis=2)
    heat_rgb = cv2.applyColorMap(
        np.clip(heat * 3, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO
    )[..., ::-1]
    Image.fromarray(heat_rgb).save(HERE / "full-model-heatmap.png")
    blender_object = blender[blender_mask]
    unity_object = unity[unity_mask]
    blender_red = (
        (blender_object[:, 0] > blender_object[:, 1] * 1.15)
        & (blender_object[:, 0] > 45)
    )
    unity_red = (
        (unity_object[:, 0] > unity_object[:, 1] * 1.15)
        & (unity_object[:, 0] > 45)
    )
    blender_dark = np.max(blender_object, axis=1) < 85
    unity_dark = np.max(unity_object, axis=1) < 85
    alignment = {
        "blender": bounds(blender_mask),
        "unity": bounds(unity_mask),
        "intersectionOverUnion": float(common.sum() / union.sum()),
        "centroidDeltaPixels": float(np.linalg.norm(
            np.array(bounds(blender_mask)["centroid"]) - np.array(bounds(unity_mask)["centroid"])
        )),
    }
    parity = {
        "ssim": ssim(blender, unity),
        "meanAbsoluteError": float(difference.mean()),
        "heatmapAreaFractionOver24": float(np.mean(heat > 24)),
        "alignment": alignment,
        "independentCropping": False,
        "postAlignment": False,
    }
    required = [
        "hero.png", "left-oblique.png", "right-oblique.png", "low.png",
        "pass-beauty.png", "pass-clay.png", "pass-normal.png",
        "pass-depth.png", "pass-roughness.png",
        "legal-mid-slide-0.png", "legal-max-open-0.png",
        "legal-max-open-12.png", "legal-max-open-36.png",
    ]
    checks = {
        "blenderBuilderPassed": blender_report["pass"],
        "unityBuilderPassed": unity_report["pass"],
        "geometryHashPreserved": blender_report["geometryDigestAfter"] == GEOMETRY_DIGEST,
        "materialHashPreserved": blender_report["sourceMaterialSha256"] == SOURCE_SHA,
        "contractHashCurrent": blender_report["contractSha256"] == CONTRACT_SHA,
        "sharedEnvironment": unity_report["environment"]["sourceExrSha256"] == blender_report["environment"]["sha256"],
        "sharedDisplay": display_report["transform"]["name"] == "neutral-display-v1",
        "unityHdrHalf": unity_report["environment"]["sourceTextureFormat"] == "R16G16B16A16_SFloat",
        "requiredCamerasAndPasses": all((HERE / name).exists() for name in required),
        "fullFrameParityMeasured": parity["ssim"] > 0.80 and alignment["intersectionOverUnion"] > 0.80,
        "bloodRedPreserved": float(blender_red.mean()) > 0.03 and float(unity_red.mean()) > 0.03,
        "blackPatternPreserved": float(blender_dark.mean()) > 0.20 and float(unity_dark.mean()) > 0.20,
        "zeroEmission": blender_report["checks"]["zeroEmission"] and unity_report["material"]["emission"] == 0,
        "noDisplayClipping": float(np.mean(np.max(unity, axis=2) >= 255)) < 0.001,
        "endpointEvidenceOnly": not any(HERE.glob("illegal-mid-slide-*.png")),
        "shippingUntouched": not unity_report["shippingSceneModified"],
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 5,
        "status": "validated-awaiting-recording",
        "sourceHashes": {
            "materialBlend": SOURCE_SHA,
            "contract": CONTRACT_SHA,
            "geometryDigest": GEOMETRY_DIGEST,
            "environment": blender_report["environment"]["sha256"],
            "displayTransform": sha256(HERE / "apply_shared_display.py"),
        },
        "environment": blender_report["environment"],
        "cameraRecipes": blender_report["cameraRecipes"],
        "parity": parity,
        "appearance": {
            "blenderRedFraction": float(blender_red.mean()),
            "unityRedFraction": float(unity_red.mean()),
            "blenderDarkFraction": float(blender_dark.mean()),
            "unityDarkFraction": float(unity_dark.mean()),
            "blenderClippedFraction": float(np.mean(np.max(blender, axis=2) >= 255)),
            "unityClippedFraction": float(np.mean(np.max(unity, axis=2) >= 255)),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    (HERE / "lighting-parity-audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 lighting audit failed.")


if __name__ == "__main__":
    main()
