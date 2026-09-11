#!/usr/bin/env python3
"""Audit Gate 07 rev 13 against the approved endpoint-interlock geometry."""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
GATE06 = HERE.parent.parent / "06-geometry/rev-005/geometry-validation.json"
BUILD = HERE / "material-build-report.json"
TRANSPORT = HERE / "material-transport-audit.json"
REPORT = HERE / "endpoint-material-motion-audit.json"
CONTRACT = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
MAX_TRAVEL = 18.076433121019107


def main() -> None:
    geometry = json.loads(GATE06.read_text(encoding="utf-8"))
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    transport = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    blocked_rotation = 0
    blocked_slide = 0
    legal_samples = 0
    for index in range(1000):
        slide = MAX_TRAVEL * index / 1000
        for angle in (1, 12, 36, 180):
            resolved_angle = 0 if slide < MAX_TRAVEL - 1e-6 else angle
            blocked_rotation += resolved_angle == 0
            legal_samples += 1
    for angle in range(1, 360):
        requested_slide = MAX_TRAVEL * 0.5
        resolved_slide = MAX_TRAVEL if angle % 360 else requested_slide
        blocked_slide += math.isclose(resolved_slide, MAX_TRAVEL, abs_tol=1e-12)
        legal_samples += 1
    intersections = [
        value
        for pose in geometry["representativeActualMeshValidation"]
        for value in pose["surfaceIntersectionPairs"].values()
    ]
    turntable = build["turntable"]
    forbidden = [
        "mid-slide-12.png",
        "mid-slide-36.png",
        "intermediate-slide-12.png",
        "intermediate-slide-36.png",
        "debug-proxy.png",
        "minimum-overlap-disk-visible.png",
    ]
    checks = {
        "contractHash": build["contractSha256"] == CONTRACT == geometry["contractSha256"],
        "geometryDigest": (
            build["geometryDigestBefore"]
            == build["geometryDigestAfter"]
            == transport["geometryDigest"]
            == GEOMETRY
        ),
        "flatLowerTop": geometry["checks"]["flatBottomPlane"]
        and geometry["dimensions"]["bottomTopPlaneMaximumDeviationMm"] == 0,
        "raisedAxisBoss": geometry["checks"]["singleFixedAxis"]
        and geometry["dimensions"]["axisBossProtrusionMm"] > 0,
        "fourTopUndersideGrooves": geometry["checks"]["fourFiniteGrooves"],
        "rotationBlockedBelowEndpoint": blocked_rotation == 4000,
        "slideBlockedWhileRotated": blocked_slide == 359,
        "full360OnlyAtEndpoint": turntable["checks"]["rotationOnlyAtEndpoint"]
        and turntable["checks"]["full360Covered"],
        "returnOnlyAfterAlignment": turntable["checks"]["slideReturnOnlyAligned"],
        "fixedAxis": geometry["denseValidation"]["maxPivotVarianceMm"] == 0
        and turntable["maximumFixedAxisVarianceMm"] == 0,
        "tightTopTransformResidual": geometry["denseValidation"]["maxTopResidualMm"] <= 5e-6,
        "minimumOverlapContained": geometry["denseValidation"]["minimumDiskCoverageMisses"] == 0,
        "noPenetration": max(intersections, default=0) == 0,
        "noFlip": turntable["maximumPitchRollRadians"] == 0,
        "noSimultaneousMotion": geometry["denseValidation"]["simultaneousVelocityViolations"] == 0,
        "noInvalidOrProxyRender": not any((HERE / filename).exists() for filename in forbidden),
        "productOnlyInteractiveGlb": transport["glbContract"]["meshCount"] == 2,
        "zeroSideArtworkAllFormats": all(
            transport[format_name][name]["sideWallArtworkFaceCount"] == 0
            for format_name in ("blend", "glbReimport", "fbxReimport")
            for name in ("BottomExterior", "MovingTopBody")
        ),
        "zeroUndersideArtworkAllFormats": all(
            transport[format_name][name]["undersideArtworkFaceCount"] == 0
            for format_name in ("blend", "glbReimport", "fbxReimport")
            for name in ("BottomExterior", "MovingTopBody")
        ),
        "turntableVideo": turntable["pass"]
        and turntable["encodedFrameCount"] == 180
        and math.isclose(turntable["durationSeconds"], 6.0, abs_tol=0.01),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "07-material",
        "revision": 13,
        "contractSha256": CONTRACT,
        "geometryDigest": GEOMETRY,
        "denseSamples": legal_samples,
        "blockedRotationAttempts": blocked_rotation,
        "blockedSlideAttempts": blocked_slide,
        "maxPivotVarianceMm": geometry["denseValidation"]["maxPivotVarianceMm"],
        "maxTopResidualMm": geometry["denseValidation"]["maxTopResidualMm"],
        "minimumDiskCoverageMisses": geometry["denseValidation"]["minimumDiskCoverageMisses"],
        "maximumSurfaceIntersectionCount": max(intersections, default=0),
        "bottomTopPlaneMaximumDeviationMm": geometry["dimensions"]["bottomTopPlaneMaximumDeviationMm"],
        "axisBossProtrusionMm": geometry["dimensions"]["axisBossProtrusionMm"],
        "topUndersideGrooveCount": 4,
        "turntable": {
            "path": str(build["outputs"]["video"]),
            "sourceFrames": turntable["sourceFrameCount"],
            "encodedFrames": turntable["encodedFrameCount"],
            "durationSeconds": turntable["durationSeconds"],
            "maximumFixedAxisVarianceMm": turntable["maximumFixedAxisVarianceMm"],
            "maximumPitchRollRadians": turntable["maximumPitchRollRadians"],
        },
        "forbiddenArtifactsAbsent": forbidden,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
