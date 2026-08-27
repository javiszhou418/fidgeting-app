#!/usr/bin/env python3
"""Validate the whole-case-only Gate 06 user review board."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat


ROOT = Path(__file__).resolve().parent
PIPELINE_ROOT = ROOT.parent.parent.parent
PIPELINE = PIPELINE_ROOT / "pipeline.json"
GEOMETRY_REPORT = ROOT / "geometry-validation.json"
COMPOSER = ROOT / "compose_user_review_r003.py"
BOARD = ROOT / "gate06-whole-case-review-r003.png"
OUTPUT = ROOT / "gate06-whole-case-review-validation-r003.json"

REQUIRED_PANELS = (
    "front",
    "back",
    "top",
    "side",
    "workbench",
    "dimensions",
    "pivot",
    "concentric",
    "closed-loop",
    "flood-fill",
    "normal-validation",
)

FORBIDDEN_SOURCE_REFERENCES = (
    "exploded-geometry.png",
    "geometry-review.png",
    "geometry-review-contact-sheet.png",
    "raw/exploded",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_repo_path(relative_path: str) -> Path:
    repo_root = PIPELINE_ROOT.parents[4]
    return repo_root / relative_path


def main() -> None:
    pipeline = json.loads(PIPELINE.read_text(encoding="utf-8"))
    geometry = json.loads(GEOMETRY_REPORT.read_text(encoding="utf-8"))
    composer = COMPOSER.read_text(encoding="utf-8")
    derivative = geometry["geometryIdentity"]["derivative"]
    source = geometry["geometryIdentity"]["source"]

    rev2_assets = [
        asset
        for asset in pipeline["assets"]
        if asset["stageId"] == "06-geometry"
        and asset["id"].endswith("-r002")
    ]
    mismatched_rev2_assets = []
    for asset in rev2_assets:
        absolute = resolve_repo_path(asset["path"])
        actual_hash = sha256(absolute) if absolute.is_file() else None
        if actual_hash != asset["sha256"]:
            mismatched_rev2_assets.append({
                "id": asset["id"],
                "expected": asset["sha256"],
                "actual": actual_hash,
            })

    forbidden_references = [
        value
        for value in FORBIDDEN_SOURCE_REFERENCES
        if value in composer
    ]
    expected_metadata = {
        "FidgetEvidenceTruth":
            "USER-FACING WHOLE-CASE GATE 06 REVIEW",
        "Gate": "06-geometry",
        "GeometryRevision": "2",
        "EvidenceRevision": "3",
        "ReviewPanels": ",".join(REQUIRED_PANELS),
        "SourceBlendSha256":
            geometry["sourceGate05"]["hashesBefore"]["blend"],
        "DerivativeFullGeometryDigest":
            derivative["fullGeometryDigest"],
        "VertexPositionDigest":
            derivative["vertexPositionDigest"],
        "SilhouetteDigest":
            derivative["silhouetteDigest"],
        "TopologyWindingDigest":
            derivative["topologyWindingDigest"],
        "ShippingRevealPolicy":
            "whole-case-only-no-explode-in-app-or-review",
    }

    with Image.open(BOARD) as image:
        rgb = image.convert("RGB")
        variance = ImageStat.Stat(rgb.resize((128, 128))).var
        board_record = {
            "path": str(BOARD),
            "sha256": sha256(BOARD),
            "sizeBytes": BOARD.stat().st_size,
            "dimensions": [image.width, image.height],
            "mode": image.mode,
            "channelVariance": [
                round(value, 6) for value in variance
            ],
            "metadata": {
                key: image.info.get(key)
                for key in expected_metadata
            },
        }

    orientation = geometry["closedTube"]["boundaryOrientation"]
    integrity = geometry["meshIntegrity"]
    flow = geometry["closedTube"]["volumetricPassageFloodFill"]
    checks = {
        "boardDimensionsExact":
            board_record["dimensions"] == [4800, 4000],
        "boardIsNonBlank":
            max(board_record["channelVariance"]) > 5,
        "embeddedMetadataExact":
            board_record["metadata"] == expected_metadata,
        "requiredPanelsExact":
            tuple(
                board_record["metadata"]["ReviewPanels"].split(",")
            ) == REQUIRED_PANELS,
        "noForbiddenPanelSources":
            not forbidden_references,
        "allRev2AssetHashesPreserved":
            len(rev2_assets) == 43 and not mismatched_rev2_assets,
        "geometryRevisionStillTwo":
            geometry["geometryRevision"] == 2,
        "dimensionsUnchanged":
            geometry["bounds"]["measured"]["sizeMm"]
            == {"width": 228, "height": 304, "depth": 59},
        "vertexPositionsUnchanged":
            source["vertexPositionDigest"]
            == derivative["vertexPositionDigest"],
        "silhouetteUnchanged":
            source["silhouetteDigest"]
            == derivative["silhouetteDigest"],
        "windingDigestUnchangedFromRev2":
            derivative["topologyWindingDigest"]
            == (
                "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605a"
                "deb21611a3bf7c79"
            ),
        "normalValidationPassed":
            orientation["outerBoundary"]["outward"] is True
            and orientation["innerBoundary"][
                "inwardTowardLumen"
            ] is True
            and orientation["netMaterialVolumePositive"] is True
            and integrity[
                "allSubjectMaterialSignedVolumesPositive"
            ] is True,
        "closedLoopValidationPassed":
            geometry["closedTube"]["connectedMaterialBodyCount"] == 1
            and integrity["allOpenBoundaryEdgeCount"] == 0
            and integrity["allNonManifoldEdgeCount"] == 0,
        "floodFillValidationPassed":
            flow["visitedSamples"] == 384
            and flow["sampleCount"] == 384
            and flow["pass"] is True,
        "gate07NotEntered":
            geometry["scope"]["gate07Entered"] is False,
        "shippingUnityUnchanged":
            geometry["scope"]["shippingUnityChanged"] is False,
        "noBuildInstallPhonePush":
            geometry["scope"]["buildInstallPhonePush"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 2,
        "evidenceRevision": 3,
        "status": "pass" if all(checks.values()) else "fail",
        "reviewArtifactId":
            "premium-display-case-gate06-whole-case-review-r003",
        "reviewBoard": board_record,
        "requiredPanels": list(REQUIRED_PANELS),
        "forbiddenSourceReferences": forbidden_references,
        "rev2AssetCount": len(rev2_assets),
        "mismatchedRev2Assets": mismatched_rev2_assets,
        "geometryIdentity": {
            "sourceFullGeometryDigest": source[
                "fullGeometryDigest"
            ],
            "derivativeFullGeometryDigest": derivative[
                "fullGeometryDigest"
            ],
            "vertexPositionDigest": derivative[
                "vertexPositionDigest"
            ],
            "silhouetteDigest": derivative[
                "silhouetteDigest"
            ],
            "topologyWindingDigest": derivative[
                "topologyWindingDigest"
            ],
        },
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "reviewBoard": board_record,
        "rev2AssetCount": len(rev2_assets),
        "forbiddenSourceReferences": forbidden_references,
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(
            json.dumps(checks, ensure_ascii=False, indent=2)
        )


if __name__ == "__main__":
    main()
