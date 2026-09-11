#!/usr/bin/env python3
"""Validate Premium Display Case Gate 06 rev 3 evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
GEOMETRY = ROOT / "geometry-revalidation.json"
CAPTURE = ROOT / "fixed-views/capture-wrapper-report.json"
ORTHOS = ROOT / "orthographic-workbench-report.json"
INTERACTIVE = ROOT / "interactive-review-validation.json"
OUTPUT = ROOT / "geometry-review-validation.json"
EXPECTED_SOURCE_DIGEST = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
EXPECTED_DERIVATIVE_DIGEST = "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
ORTHOGRAPHIC_IDS = ("front", "back", "top", "bottom", "left", "right")
REVIEW_FILES = (
    "premium-display-case-gate06-review-r003.glb",
    "geometry-presentation-review.png",
    "geometry-workbench.png",
    "dimension-overlay.png",
    "pivot-presentation-root-overlay.png",
    *(f"ortho-{view_id}.png" for view_id in ORTHOGRAPHIC_IDS),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    capture = json.loads(CAPTURE.read_text(encoding="utf-8"))
    orthos = json.loads(ORTHOS.read_text(encoding="utf-8"))
    interactive = json.loads(INTERACTIVE.read_text(encoding="utf-8"))
    ortho_ids = {item["id"] for item in orthos.get("views", [])}
    image_sizes = {}
    for name in REVIEW_FILES:
        path = ROOT / name
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                image_sizes[name] = list(image.size)
    integrity = geometry["meshIntegrity"]
    tube = geometry["tubeOrientation"]
    ownership = geometry["presentationOwnership"]
    derivative = geometry["identity"]["derivative"]
    source = geometry["identity"]["source"]
    checks = {
        "geometryReportPassed": geometry.get("status") == "pass",
        "allGeometryChecksPassed": all(geometry.get("checks", {}).values()),
        "approvedGate05SourceDigest": (
            source["fullGeometryDigest"] == EXPECTED_SOURCE_DIGEST
        ),
        "stableDerivativeDigest": (
            derivative["fullGeometryDigest"] == EXPECTED_DERIVATIVE_DIGEST
            and geometry["output"]["geometryDigest"] == EXPECTED_DERIVATIVE_DIGEST
        ),
        "vertexPositionsStable": (
            source["vertexPositionDigest"] == derivative["vertexPositionDigest"]
        ),
        "silhouetteStable": (
            source["silhouetteDigest"] == derivative["silhouetteDigest"]
        ),
        "sixOrthographicViews": (
            orthos.get("status") == "pass"
            and ortho_ids == set(ORTHOGRAPHIC_IDS)
            and all((ROOT / f"ortho-{view_id}.png").is_file() for view_id in ORTHOGRAPHIC_IDS)
        ),
        "standardViewCaptureVerified": (
            capture.get("verified_capture") is True
            and capture.get("missing_views") == []
        ),
        "workbenchPresent": image_sizes.get("geometry-workbench.png") == [1600, 1400],
        "dimensionOverlayPresent": image_sizes.get("dimension-overlay.png") == [1800, 1200],
        "pivotOverlayPresent": (
            image_sizes.get("pivot-presentation-root-overlay.png") == [1800, 1200]
        ),
        "primaryBoardPresent": (
            image_sizes.get("geometry-presentation-review.png") == [3000, 2000]
        ),
        "interactiveReviewPassed": (
            interactive.get("status") == "pass"
            and all(interactive.get("checks", {}).values())
            and (ROOT / "premium-display-case-gate06-review-r003.glb").is_file()
            and sha256(ROOT / "premium-display-case-gate06-review-r003.glb")
            == interactive["reviewGlbSha256"]
        ),
        "boundsExact": (
            geometry["bounds"]["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "labelAndCornersExact": (
            geometry["structural"]["labelPosition"]["candidateCenterYmm"] == 99.0
            and geometry["structural"]["cornerCenterFamilies"]["maximumDriftMm"]
            == 0.0
        ),
        "closedManifold": (
            integrity["allOpenBoundaryEdgeCount"] == 0
            and integrity["allNonManifoldEdgeCount"] == 0
            and integrity["pass"] is True
        ),
        "noSelfIntersectionOrDegenerates": (
            integrity["allSelfIntersectionPairCount"] == 0
            and integrity["allDegenerateElementCount"] == 0
        ),
        "positiveSignedVolumesAndNormals": (
            integrity["allSubjectMaterialSignedVolumesPositive"] is True
            and tube["netMaterialSignedVolumeMm3"] == 52932.982745
            and tube["outerBoundary"]["outward"] is True
            and tube["innerBoundary"]["inwardTowardLumen"] is True
            and tube["pass"] is True
        ),
        "closedTubeConnected": (
            geometry["structural"]["closedTube"]["topology"][
                "connectedMaterialBodyCount"
            ]
            == 1
            and geometry["structural"]["closedTube"]["channelFloodFill"][
                "visitedSamples"
            ]
            == 384
            and geometry["structural"]["closedTube"]["channelFloodFill"][
                "sampleCount"
            ]
            == 384
        ),
        "presentationOwnershipRigid": (
            ownership["motionOwner"] == "Unity"
            and ownership["movingTransform"] == "PresentationRoot"
            and ownership["rigidChild"] == "CaseAssembly"
            and ownership["contentSlot"] == "caller-owned-static"
            and ownership["sameInstance"] is True
            and ownership["wholeCaseOnly"] is True
            and ownership["runtimeAnimationBakedInBlender"] is False
        ),
        "reviewArtifactsWholeCaseOnly": (
            geometry["reviewArtifactExplodedPartCount"] == 0
            and all("explode" not in name.lower() for name in REVIEW_FILES)
        ),
        "internalExplodedEvidenceOnly": (
            geometry["internalTechnicalExplodedSourceAssetId"]
            == "premium-display-case-geometry-exploded-r002"
        ),
        "scopeBoundariesPreserved": (
            geometry["shippingUnityChanged"] is False
            and geometry["buildInstallPhonePush"] is False
            and geometry["gate07Status"] == "blocked"
        ),
    }
    result = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 3,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "orthographicViewCount": len(ortho_ids),
            "reviewArtifactExplodedPartCount": geometry[
                "reviewArtifactExplodedPartCount"
            ],
            "openBoundaryEdgeCount": integrity["allOpenBoundaryEdgeCount"],
            "nonManifoldEdgeCount": integrity["allNonManifoldEdgeCount"],
            "selfIntersectionPairCount": integrity[
                "allSelfIntersectionPairCount"
            ],
            "degenerateElementCount": integrity["allDegenerateElementCount"],
            "tubeSignedVolumeMm3": tube["netMaterialSignedVolumeMm3"],
            "geometryDigest": derivative["fullGeometryDigest"],
            "vertexPositionDigest": derivative["vertexPositionDigest"],
            "silhouetteDigest": derivative["silhouetteDigest"],
        },
        "imageSizes": image_sizes,
        "reviewArtifactFiles": list(REVIEW_FILES),
        "internalTechnicalArtifactIds": [
            geometry["internalTechnicalExplodedSourceAssetId"]
        ],
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "gate07Status": "blocked",
    }
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "checks": checks}))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
