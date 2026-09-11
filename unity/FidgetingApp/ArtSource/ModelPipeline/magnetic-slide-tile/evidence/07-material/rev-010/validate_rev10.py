#!/usr/bin/env python3
"""Validate Gate 07 rev 10 material, artwork, provenance and motion evidence."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np


OUT = Path(__file__).resolve().parent
REV9 = OUT.parent / "rev-009"
REPORT = OUT / "material-axis-validation.json"
LOWER = OUT / "lower-artwork-provenance.json"


def image(path):
    result = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if result is None:
        raise FileNotFoundError(path)
    return result


def red_mask(img):
    b, g, r = cv2.split(img)
    return (r > 45) & (r.astype(np.float32) > g * 1.34) & (r.astype(np.float32) > b * 1.18)


def material_metrics(path):
    img = image(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    red = red_mask(img)
    red_values = gray[red]
    if red_values.size < 100:
        raise RuntimeError(f"Insufficient crystal pixels in {path}")
    blur = cv2.GaussianBlur(gray, (0, 0), 7.0)
    local_delta = gray.astype(np.float32) - blur.astype(np.float32)
    sparkle = red & (local_delta > 18) & (gray > 70)
    edges = cv2.Canny(gray, 45, 120) > 0
    height, width = gray.shape
    quadrants = [
        sparkle[: height // 2, : width // 2],
        sparkle[: height // 2, width // 2 :],
        sparkle[height // 2 :, : width // 2],
        sparkle[height // 2 :, width // 2 :],
    ]
    return {
        "redPixelCount": int(red.sum()),
        "redLumaStd": float(red_values.std()),
        "redLumaP05P95": [float(np.percentile(red_values, 5)), float(np.percentile(red_values, 95))],
        "sparklePixelCount": int(sparkle.sum()),
        "sparkleQuadrantCounts": [int(item.sum()) for item in quadrants],
        "sparkleQuadrantsPopulated": int(sum(item.sum() > 10 for item in quadrants)),
        "crystalEdgeDensity": float((edges & red).sum() / max(1, red.sum())),
        "highlightClippingFraction": float(np.mean(np.all(img >= 250, axis=2))),
    }


def side_metrics(path):
    img = image(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    neutral = hsv[:, :, 1] < 55
    values = gray[neutral]
    return {
        "neutralP05P95Range": float(np.percentile(values, 95) - np.percentile(values, 5)),
        "darkFraction": float(np.mean(gray < 35)),
        "brightReflectionFraction": float(np.mean((gray > 170) & neutral)),
    }


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    lower = json.loads(LOWER.read_text(encoding="utf-8"))
    front = material_metrics(OUT / "upper-front.png")
    macro = material_metrics(OUT / "crystal-microflake-macro.png")
    oblique = material_metrics(OUT / "oblique-crystal.png")
    lower_open = material_metrics(OUT / "lower-open-macro.png")
    side = side_metrics(OUT / "side-rim.png")
    source_front = material_metrics(REV9 / "source-normalized-front.png")
    source_oblique = material_metrics(REV9 / "source-normalized-oblique.png")
    front_range = front["redLumaP05P95"][1] - front["redLumaP05P95"][0]
    oblique_range = oblique["redLumaP05P95"][1] - oblique["redLumaP05P95"][0]
    source_front_range = source_front["redLumaP05P95"][1] - source_front["redLumaP05P95"][0]
    source_oblique_range = source_oblique["redLumaP05P95"][1] - source_oblique["redLumaP05P95"][0]
    motion = report["motionEvidence"]
    expected_sources = {
        "slider-intake-obs-frame-01",
        "slider-intake-obs-frame-03",
        "slider-intake-obs-frame-05",
        "slider-intake-obs-frame-10",
        "slider-intake-haloo-official-08",
    }
    checks = {
        "geometryDigestUnchanged": report["geometry"]["unchanged"] and report["geometry"]["matricesUnchanged"],
        "maskHashesDistinct": lower["mask"]["hashesDistinct"],
        "maskIndependentSlots": (
            report["recipe"]["lowerArtwork"]["hashesDistinct"]
            and report["geometry"]["assignments"]["LowerBody_Fixed_CleanPlane"]["topCapFaces"] == 1
            and report["geometry"]["assignments"]["UpperCapsule_Moving"]["topCapFaces"] == 1
        ),
        "directReconstructedProvenance": (
            lower["directTrace"]["pixelCount"] > 12000
            and lower["reconstruction"]["pixelCount"] > 3000
            and "not an exact trace" in lower["reconstruction"]["claim"]
        ),
        "lowerCompositionDifference": lower["mask"]["binaryDifferenceFraction"] >= 0.20,
        "sourceColorRange": (
            front_range >= source_front_range * 0.30
            and oblique_range >= source_oblique_range * 0.50
        ),
        "crystalLocalVariation": (
            front["redLumaStd"] >= 15.0
            and macro["redLumaStd"] >= 7.5
            and oblique["redLumaStd"] >= 24.0
        ),
        "microflakeDistribution": macro["sparklePixelCount"] >= 220 and macro["sparkleQuadrantsPopulated"] >= 3,
        "mosaicDepthEdges": macro["crystalEdgeDensity"] >= 0.03,
        "zeroHighlightClipping": max(
            front["highlightClippingFraction"],
            macro["highlightClippingFraction"],
            oblique["highlightClippingFraction"],
        ) <= 0.003,
        "silverBrightDarkResponse": side["neutralP05P95Range"] >= 70 and side["brightReflectionFraction"] >= 0.003,
        "darkSideResponse": side["darkFraction"] >= 0.20,
        "lowerArtworkVisible": lower_open["redPixelCount"] >= 300000 and lower_open["crystalEdgeDensity"] >= 0.03,
        "zeroEmissionBloom": report["render"]["emission"] == 0 and report["render"]["bloom"] is False,
        "sourceLinksComplete": expected_sources.issubset(set(report["sourceAssetIds"])),
        "detentAnglesExact": [item["angleDeg"] for item in motion["spin"]] == [0, 12, 36],
        "detentIndicesExact": [item["detentIndex"] for item in motion["spin"]] == [0, 1, 3],
        "detentEquationExact": motion["detentEquation"] == "360° / 12° = 30",
        "axisPointExact": motion["axisPointWorldMm"] == [0.0, -9.5, 0.0] and motion["axisDirection"] == "+Z",
        "spinTranslationZero": motion["allSpinTranslationsZero"],
        "spinPivotDriftZero": motion["allPivotDriftZero"],
        "slidePoseExact": (
            motion["slide"]["translationLocalMm"] == [0.0, 21.0, 0.0]
            and motion["slide"]["rotationDeg"] == 0
            and motion["slide"]["upperRotationDeg"] == 0.0
        ),
        "noFortyFivePrimaryPose": motion["fortyFiveDegreePrimaryPoseUsed"] is False,
        "renderRecipeConsistent": all(
            camera["recipe"] == "Gate07Rev10-neutral-material-axis-review"
            for camera in report["render"]["cameras"].values()
        ),
    }
    result = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 10,
        "metrics": {
            "front": front,
            "macro": macro,
            "oblique": oblique,
            "lowerOpen": lower_open,
            "side": side,
            "sourceFront": source_front,
            "sourceOblique": source_oblique,
            "rangeRatios": {
                "frontVsSource": front_range / source_front_range,
                "obliqueVsSource": oblique_range / source_oblique_range,
            },
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    (OUT / "source-fidelity-validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failed = [key for key, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"Gate 07 rev 10 validation failed: {failed}")


if __name__ == "__main__":
    main()
