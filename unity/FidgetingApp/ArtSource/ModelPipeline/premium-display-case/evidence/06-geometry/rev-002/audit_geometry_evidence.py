#!/usr/bin/env python3
"""Audit Premium Display Case Gate 06 normals-only revision 2 in Blender."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001"
EVIDENCE_BLEND = ROOT / "premium-display-case-geometry-r002.blend"
VALIDATION_REPORT = ROOT / "geometry-validation.json"
AUDIT_PATH = ROOT / "blender-audit.json"
VALIDATOR_PATH = ROOT / "validate_geometry.py"
REV1_AUDITOR_PATH = REV1 / "audit_geometry_evidence.py"
GATE05 = ROOT.parent.parent / "05-blockout/rev-002"
SOURCE_BLEND = GATE05 / "premium-display-case-blockout.blend"
SOURCE_BUILDER = GATE05 / "build_blockout.py"
SOURCE_VALIDATOR = GATE05 / "validate_blockout.py"
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_SOURCE_BLEND_SHA256 = (
    "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module(
    "premium_display_case_gate06_rev2_audit_validator",
    VALIDATOR_PATH,
)
REV1_AUDIT = load_module(
    "premium_display_case_gate06_rev1_audit_helpers",
    REV1_AUDITOR_PATH,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    report = json.loads(VALIDATION_REPORT.read_text(encoding="utf-8"))
    if Path(bpy.data.filepath).resolve() != EVIDENCE_BLEND.resolve():
        bpy.ops.wm.open_mainfile(filepath=str(EVIDENCE_BLEND))

    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    identity = VALIDATOR.identity_snapshot(subjects)
    bounds = VALIDATOR.world_bounds(subjects)
    mesh_audit = {
        obj.name: VALIDATOR.mesh_integrity(obj) for obj in subjects
    }
    gate05_validator = VALIDATOR.load_gate05_validator()
    tube = bpy.data.objects["ContinuousTubePerimeter"]
    tube_orientation = VALIDATOR.hollow_tube_orientation(
        tube,
        gate05_validator,
    )
    flood = REV1_AUDIT.flood_fill_audit(gate05_validator, tube)
    source_hashes = {
        "blend": sha256(SOURCE_BLEND),
        "builder": sha256(SOURCE_BUILDER),
        "validator": sha256(SOURCE_VALIDATOR),
    }

    root = bpy.data.objects["PresentationRoot"]
    assembly = bpy.data.objects["CaseAssembly"]
    content = bpy.data.objects["ContentSlot"]
    exploded_tube = bpy.data.objects.get("EXPLODED_ContinuousTubePerimeter")
    exploded_objects = [
        obj for obj in bpy.data.objects if obj.name.startswith("EXPLODED_")
    ]
    annotations = [
        obj
        for obj in bpy.data.objects
        if bool(obj.get("gate06_review_annotation", False))
    ]
    source_identity = report["geometryIdentity"]["source"]
    before_volume = report["windingCorrection"]["before"][
        "netMaterialSignedVolumeMm3"
    ]
    checks = {
        "validationReportPassed": report["status"] == "pass",
        "validatorRecheckPassed": (
            report.get("validatorRecheck", {}).get("status") == "pass"
        ),
        "sourceHashesMatchBuildReport": (
            source_hashes
            == report["sourceGate05"]["hashesBefore"]
            == report["sourceGate05"]["hashesAfter"]
        ),
        "sourceBlendUnchanged": (
            source_hashes["blend"] == EXPECTED_SOURCE_BLEND_SHA256
        ),
        "objectMatrixDigestUnchanged": (
            identity["objectMatrixDigest"]
            == source_identity["objectMatrixDigest"]
        ),
        "vertexPositionDigestUnchanged": (
            identity["vertexPositionDigest"]
            == source_identity["vertexPositionDigest"]
        ),
        "silhouetteDigestUnchanged": (
            identity["silhouetteDigest"]
            == source_identity["silhouetteDigest"]
        ),
        "topologyWindingDigestChanged": (
            identity["topologyWindingDigest"]
            != source_identity["topologyWindingDigest"]
        ),
        "derivativeIdentityMatchesBuildReport": (
            identity == report["geometryIdentity"]["derivative"]
        ),
        "boundsExact": (
            bounds["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "portraitRatioExact": (
            bounds["sizeMm"]["width"] / bounds["sizeMm"]["height"] == 0.75
        ),
        "allSubjectSolidsPositive": all(
            item["signedVolumeMm3"] > 0.0
            and item["positiveMaterialSignedVolume"] is True
            and item["pass"] is True
            for item in mesh_audit.values()
        ),
        "rev1NegativeVolumeWouldFail": before_volume <= 0.0,
        "tubeOuterBoundaryOutward": (
            tube_orientation["outerBoundary"]["outward"] is True
            and tube_orientation["outerBoundary"]["signedVolumeMm3"] > 0.0
            and tube_orientation["outerBoundary"][
                "orientationMismatchFaceCount"
            ] == 0
        ),
        "tubeInnerBoundaryTowardLumen": (
            tube_orientation["innerBoundary"]["inwardTowardLumen"] is True
            and tube_orientation["innerBoundary"]["signedVolumeMm3"] < 0.0
            and tube_orientation["innerBoundary"][
                "orientationMismatchFaceCount"
            ] == 0
        ),
        "tubeNetMaterialVolumePositive": (
            tube_orientation["netMaterialSignedVolumeMm3"] > 0.0
            and tube_orientation["netMaterialVolumePositive"] is True
            and tube_orientation["pass"] is True
        ),
        "tubeFloodFillAndWall": flood["pass"],
        "presentationRootOwnsMotion": (
            root.parent is None
            and bool(root.get("motion_owner", False))
            and float(root.get("angular_velocity", math.nan)) == 0.0
            and assembly.parent is root
            and assembly.get("role")
            == "always-assembled-transform-group"
        ),
        "contentSlotPreserved": (
            content.type == "EMPTY"
            and content.parent.name == "RearPolycarbonateShell"
            and content.get("role") == "runtime-anchor"
            and float(content.get("width_mm", 0.0)) == 180.0
            and float(content.get("height_mm", 0.0)) == 198.0
            and float(content.get("depth_mm", 0.0)) == 48.0
        ),
        "explodedEvidenceUsesDerivativeTubeData": (
            len(exploded_objects) == 5
            and exploded_tube is not None
            and exploded_tube.data is tube.data
            and bool(
                exploded_tube.get(
                    "gate06_exploded_same_mesh_data",
                    False,
                )
            )
            and not bool(
                exploded_tube.get("shipping_animation_eligible", True)
            )
        ),
        "explodedAndAnnotationsHiddenInCanonicalScene": (
            all(obj.hide_render for obj in exploded_objects)
            and all(obj.hide_render for obj in annotations)
        ),
        "noHiddenStructureInvented": (
            report["hiddenStructure"]["inventedInternalPartCount"] == 0
            and bpy.data.objects["TransparentCover"].type == "EMPTY"
        ),
        "shippingRevealAlwaysAssembled": (
            bpy.context.scene["shipping_reveal_policy"]
            == "always-assembled-never-explodes"
        ),
        "gate07NotEntered": (
            bpy.context.scene["gate07_entered"] is False
        ),
        "shippingUnityUnchanged": (
            bpy.context.scene["shipping_unity_changed"] is False
        ),
        "noBuildInstallPhonePush": (
            bpy.context.scene["build_install_phone_push"] is False
        ),
    }
    audit = {
        "schemaVersion": 2,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceFiles": {
            "gate05Blend": {
                "path": str(SOURCE_BLEND),
                "sha256": source_hashes["blend"],
            },
            "gate05Builder": {
                "path": str(SOURCE_BUILDER),
                "sha256": source_hashes["builder"],
            },
            "gate05Validator": {
                "path": str(SOURCE_VALIDATOR),
                "sha256": source_hashes["validator"],
            },
        },
        "evidenceBlend": {
            "path": str(EVIDENCE_BLEND),
            "sha256": sha256(EVIDENCE_BLEND),
        },
        "geometryIdentity": {
            "source": source_identity,
            "derivative": identity,
        },
        "boundsMm": bounds["sizeMm"],
        "portraitWidthHeightRatio": (
            bounds["sizeMm"]["width"] / bounds["sizeMm"]["height"]
        ),
        "labelCenterYmm": 99.0,
        "labelDownshiftMm": 6.0,
        "outerRadiusMm": 20.0,
        "maximumCornerCenterDriftMm": report[
            "concentricContours"
        ]["maximumCenterDriftMm"],
        "meshAudit": mesh_audit,
        "tubeOrientation": tube_orientation,
        "tubeFloodFill": flood,
        "checks": checks,
        "blender": bpy.app.version_string,
    }
    AUDIT_PATH.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": audit["status"],
        "boundsMm": audit["boundsMm"],
        "windingBeforeAfter": {
            "before": before_volume,
            "after": tube_orientation["netMaterialSignedVolumeMm3"],
        },
        "tubeOrientation": tube_orientation,
        "tubeFloodFill": (
            f"{flood['visitedSamples']}/{flood['sampleCount']}"
        ),
        "allSubjectSignedVolumesMm3": {
            name: item["signedVolumeMm3"]
            for name, item in mesh_audit.items()
        },
    }, ensure_ascii=False, indent=2))
    if audit["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
