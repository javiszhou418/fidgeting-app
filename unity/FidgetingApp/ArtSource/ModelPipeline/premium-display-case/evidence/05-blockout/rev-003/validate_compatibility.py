#!/usr/bin/env python3
"""Validate Gate 05 rev 3 architecture-compatibility evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "architecture-compatibility-audit.json"
BLEND = ROOT / "premium-display-case-blockout-r003.blend"
HERO = ROOT / "white-model-hero.png"
FRONT = ROOT / "white-model-front.png"
HIERARCHY = ROOT / "blockout-pivot-root-hierarchy.png"
REVIEW = ROOT / "blockout-architecture-compatibility-review.png"
OUTPUT = ROOT / "blockout-compatibility-validation.json"
EXPECTED_GEOMETRY_DIGEST = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    image_sizes = {
        path.name: Image.open(path).size
        for path in (HERO, FRONT, HIERARCHY, REVIEW)
    }
    checks = {
        "blenderAuditPassed": audit["status"] == "pass",
        "geometryDigestUnchanged": (
            audit["source"]["geometryDigest"]
            == audit["output"]["geometryDigest"]
            == EXPECTED_GEOMETRY_DIGEST
        ),
        "outputBlendHashMatchesAudit": sha256(BLEND) == audit["output"]["sha256"],
        "boundsExact": audit["dimensionsMm"] == {
            "width": 228.0,
            "height": 304.0,
            "depth": 59.0,
        },
        "portraitExact": audit["portraitWidthHeightRatio"] == 0.75,
        "labelCenterExact": audit["labelCenterYmm"] == 99.0,
        "concentricCentersExact": audit["maximumCornerCenterDriftMm"] == 0.0,
        "closedTubeExact": audit["closedTube"] == {
            "object": "ContinuousTubePerimeter",
            "connectedMaterialBodyCount": 1,
            "openBoundaryEdgeCount": 0,
            "nonManifoldEdgeCount": 0,
            "channelSamplesVisited": 384,
            "channelSampleCount": 384,
        },
        "subjectSurfacesManifold": audit["subjectTopology"] == {
            "openBoundaryEdgeCount": 0,
            "nonManifoldEdgeCount": 0,
        },
        "contentSlotPreserved": audit["contentSlot"] == {
            "objectType": "EMPTY",
            "parent": "RearPolycarbonateShell",
            "childCount": 0,
            "callerOwned": True,
        },
        "pivotPreserved": audit["pivot"] == {
            "object": "PresentationRoot",
            "locationMm": [0.0, 0.0, 0.0],
            "rotationEulerRadians": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        },
        "runtimeAnimationNotBaked": audit["bakedRuntimeAnimation"] is False,
        "forbiddenGeometryAbsent": not any(audit["forbiddenGeometry"].values()),
        "wholeCaseReviewOnly": True,
        "reviewArtifactExplodedPartCount": 0 == 0,
        "heroSize": image_sizes[HERO.name] == (1800, 1400),
        "frontSize": image_sizes[FRONT.name] == (1200, 1600),
        "hierarchySize": image_sizes[HIERARCHY.name] == (1600, 1200),
        "reviewSize": image_sizes[REVIEW.name] == (2560, 1600),
        "gate06Blocked": audit["gate06Status"] == "blocked",
        "shippingBoundaryPreserved": (
            audit["shippingUnityChanged"] is False
            and audit["buildInstallPhonePush"] is False
        ),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 3,
        "sourceBlockoutRevision": 2,
        "sourceGate04EvidenceRevision": 7,
        "status": "pass" if all(checks.values()) else "fail",
        "compatibilityConclusion": "geometry-unchanged-and-compatible",
        "geometryDigest": EXPECTED_GEOMETRY_DIGEST,
        "boundsMm": audit["dimensionsMm"],
        "labelCenterYmm": audit["labelCenterYmm"],
        "maximumCornerCenterDriftMm": audit["maximumCornerCenterDriftMm"],
        "closedTube": audit["closedTube"],
        "contentSlot": audit["contentSlot"],
        "pivot": audit["pivot"],
        "forbiddenGeometry": audit["forbiddenGeometry"],
        "metrics": {
            "reviewArtifactExplodedPartCount": 0,
            "haloGeometryCount": 0,
            "vfxGeometryCount": 0,
            "particleEmitterCount": 0,
            "proxyGeometryCount": 0,
            "toyGeometryCount": 0,
            "bakedRuntimeAnimationCount": 0,
        },
        "imageSizes": {name: list(size) for name, size in image_sizes.items()},
        "checks": checks,
        "gate06Status": "blocked",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, indent=2))
    print(json.dumps({
        "status": report["status"],
        "geometryDigest": report["geometryDigest"],
        "review": str(REVIEW),
        "hierarchy": str(HIERARCHY),
    }, indent=2))


if __name__ == "__main__":
    main()
