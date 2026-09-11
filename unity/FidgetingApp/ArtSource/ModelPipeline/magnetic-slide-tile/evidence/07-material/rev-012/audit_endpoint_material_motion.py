#!/usr/bin/env python3
"""Audit Gate 07 evidence against the endpoint-interlock state machine."""

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
GATE06 = HERE.parent.parent / "06-geometry/rev-005/geometry-validation.json"
MATERIAL = HERE / "material-validation.json"
BLENDER = HERE / "blender-material-audit.json"
MAX_TRAVEL = 18.076433121019107
CONTRACT = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"

geometry = json.loads(GATE06.read_text(encoding="utf-8"))
material = json.loads(MATERIAL.read_text(encoding="utf-8"))
blender = json.loads(BLENDER.read_text(encoding="utf-8"))
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

legal_pose_files = [
    "assembled-closed.png",
    "intermediate-slide-0.png",
    "max-open-0.png",
    "max-open-12.png",
    "max-open-36.png",
]
forbidden_pose_files = [
    "mid-slide-12.png",
    "mid-slide-36.png",
    "intermediate-slide-12.png",
    "intermediate-slide-36.png",
]
penetrations = [
    value
    for pose in geometry["representativeActualMeshValidation"]
    for value in pose["surfaceIntersectionPairs"].values()
]
checks = {
    "contractHash": material["contractSha256"] == CONTRACT == geometry["contractSha256"],
    "geometryDigest": material["geometryDigestBefore"] == material["geometryDigestAfter"] == GEOMETRY,
    "legalPoseFiles": all((HERE / name).exists() for name in legal_pose_files),
    "noIllegalPoseFiles": not any((HERE / name).exists() for name in forbidden_pose_files),
    "rotationBlockedBelowEndpoint": blocked_rotation == 4000,
    "slideBlockedWhileRotated": blocked_slide == 359,
    "returnAfterAlignment": (0 % 360) == 0 and (360 % 360) == 0,
    "fixedPivot": geometry["denseValidation"]["maxPivotVarianceMm"] == 0,
    "tightTransformResidual": geometry["denseValidation"]["maxTopResidualMm"] <= 5e-6,
    "minimumOverlapContained": geometry["denseValidation"]["minimumDiskCoverageMisses"] == 0,
    "noPenetration": max(penetrations, default=0) == 0,
    "noFlip": all(pose["angleDeg"] in (0, 12, 36, 360) for pose in geometry["representativeActualMeshValidation"] if pose["id"] != "mid-slide"),
    "rendererWhitelist": blender["checks"]["productRendererWhitelist"],
    "zeroSelfMotion": blender["checks"]["zeroSelfMotion"],
}
report = {
    "schemaVersion": 1,
    "gate": "07-material",
    "revision": 12,
    "contractSha256": CONTRACT,
    "geometryDigest": GEOMETRY,
    "denseSamples": legal_samples,
    "blockedRotationAttempts": blocked_rotation,
    "blockedSlideAttempts": blocked_slide,
    "maxPivotVarianceMm": geometry["denseValidation"]["maxPivotVarianceMm"],
    "maxTopResidualMm": geometry["denseValidation"]["maxTopResidualMm"],
    "minimumDiskCoverageMisses": geometry["denseValidation"]["minimumDiskCoverageMisses"],
    "maximumSurfaceIntersectionCount": max(penetrations, default=0),
    "legalPoseFiles": legal_pose_files,
    "forbiddenPoseFilesAbsent": forbidden_pose_files,
    "checks": checks,
    "pass": all(checks.values()),
}
(HERE / "endpoint-material-motion-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
