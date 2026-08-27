#!/usr/bin/env python3
"""Audit Premium Display Case Gate 08 rev 2 Blender evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parent.parent
BLEND = ROOT / "premium-display-case-lighting-r002.blend"
BUILD_REPORT = ROOT / "lighting-revalidation.json"
IMAGE_REPORT = ROOT / "lighting-image-validation.json"
AUDIT_REPORT = ROOT / "blender-lighting-audit.json"
QA_REPORT = ROOT / "qa-verdict.json"
VALIDATOR_PATH = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
LEGACY_BUILDER = ROOT.parent / "rev-001/build_lighting_lookdev.py"
EXPECTED_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    images = json.loads(IMAGE_REPORT.read_text(encoding="utf-8"))
    validator = load_module("premium_display_case_gate08_rev2_validator", VALIDATOR_PATH)
    helpers = load_module("premium_display_case_gate08_rev2_helpers", LEGACY_BUILDER)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    studio = [
        obj
        for name in ("M07_StudioCyclorama", "M07_BackViewWall", "M07_SideViewWall")
        if (obj := bpy.data.objects.get(name)) is not None
    ]
    identity = validator.identity_snapshot(subjects)
    material_digest, _ = helpers.approved_material_digest(
        build["materials"]["approvedMaterialNames"],
        subjects + proxies + studio,
    )
    active_lights = [
        obj
        for obj in scene.objects
        if obj.type == "LIGHT" and not obj.hide_render
    ]
    candidate_lights = [
        obj for obj in active_lights if obj.name.startswith("M08_")
    ]
    candidate_cameras = [
        obj
        for obj in scene.objects
        if obj.type == "CAMERA" and obj.name.startswith("M08_")
    ]
    root = bpy.data.objects["PresentationRoot"]
    no_actions = all(
        not (obj.animation_data and obj.animation_data.action)
        for obj in [root, *candidate_lights, *candidate_cameras]
    )
    no_external_effect_objects = all(
        not any(token in obj.name.lower() for token in ("halo", "particle", "flash"))
        for obj in scene.objects
        if not obj.hide_render
    )
    neutral_lights = all(
        float(light.data.color[1])
        <= max(float(light.data.color[0]), float(light.data.color[2])) + 0.025
        for light in candidate_lights
    )
    required_outputs = [
        ROOT / "lighting-review.png",
        ROOT / "lighting-details-contact-sheet.png",
        ROOT / "lighting-passes-contact-sheet.png",
        ROOT / "lighting-parameters-board.png",
        ROOT / "label-placeholder-review.png",
        ROOT / "mesh-clipped-sheen-compatibility.png",
        *(ROOT / "raw" / f"{name}.png" for name in (
            "hero",
            "left-oblique",
            "right-oblique",
            "low",
            "pass-beauty",
            "pass-clay",
            "pass-normal",
            "pass-depth",
            "pass-roughness",
            "label-closeup",
            "tube-corner",
            "black-panel",
        )),
    ]
    checks = {
        "buildAndImageReportsPassed": (
            build["status"] == "pass" and images["status"] == "pass"
        ),
        "outputBlendHashMatches": sha256(BLEND) == build["outputBlendSha256"],
        "sceneRevisionAndSourcesMatch": (
            scene.get("gate") == "08-lighting"
            and scene.get("lighting_revision") == 2
            and scene.get("source_gate07_material_revision") == 2
            and scene.get("source_gate04_architecture_revision") == 7
        ),
        "geometryDigestUnchanged": (
            identity["fullGeometryDigest"] == EXPECTED_GEOMETRY_DIGEST
            and identity["fullGeometryDigest"] == build["geometry"]["digestAfter"]
        ),
        "materialDigestUnchanged": material_digest == build["materials"]["digestAfter"],
        "wholeCaseOnlyNoExplode": (
            bool(scene.get("whole_case_only"))
            and bool(scene.get("no_explode"))
            and all(
                obj.hide_render
                for obj in scene.objects
                if obj.name.startswith("EXPLODED_")
            )
        ),
        "threeNeutralAreaLightsOnly": (
            len(active_lights) == 3
            and len(candidate_lights) == 3
            and all(light.data.type == "AREA" for light in candidate_lights)
            and neutral_lights
        ),
        "lightsAreCandidateOnly": all(
            bool(light.get("lookdev_candidate_only"))
            and not bool(light.get("unity_runtime_constant"))
            for light in candidate_lights
        ),
        "camerasAreCandidateOnly": (
            len(candidate_cameras) >= 7
            and all(
                bool(camera.get("lookdev_candidate_only"))
                and not bool(camera.get("unity_runtime_constant"))
                for camera in candidate_cameras
            )
        ),
        "labelMarkedPlaceholder": (
            scene.get("label_content_state") == "placeholder-not-approved"
            and scene.get("label_runtime_authority") == "Unity real product data"
        ),
        "meshClippedSheenBoundary": (
            scene.get("mesh_clipped_sheen_owner") == "Unity MaterialPropertyBlock"
            and scene.get("mesh_clipped_sheen_outside_silhouette_pixels") == 0
        ),
        "noExternalHaloBloomParticlesOrPersistentEmission": (
            not bool(scene.get("external_halo"))
            and not bool(scene.get("large_bloom"))
            and not bool(scene.get("particles"))
            and not bool(scene.get("persistent_emission"))
            and no_external_effect_objects
        ),
        "noTimingOrEasingBaked": (
            not bool(scene.get("runtime_timing_baked"))
            and not bool(scene.get("animation_easing_baked"))
            and no_actions
        ),
        "lookdevValuesNotRuntimeConstants": not bool(
            scene.get("lookdev_values_are_unity_runtime_constants")
        ),
        "requiredOutputsPresent": all(
            path.exists() and path.stat().st_size > 10_000
            for path in required_outputs
        ),
        "gate09ShippingAndDeviceUntouched": (
            not bool(scene.get("gate09_entered"))
            and not bool(scene.get("shipping_unity_changed"))
            and not bool(scene.get("build_install_phone_push"))
        ),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "blendPath": str(BLEND),
        "blendSha256": sha256(BLEND),
        "geometryDigest": identity["fullGeometryDigest"],
        "materialDigest": material_digest,
        "activeLightNames": [obj.name for obj in active_lights],
        "candidateCameraNames": [obj.name for obj in candidate_cameras],
        "labelContentApproved": False,
        "meshClippedSheenOutsideSilhouettePixels": 0,
        "checks": checks,
        "blender": bpy.app.version_string,
    }
    AUDIT_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    qa = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 2,
        "status": report["status"],
        "result": (
            "READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING"
            if report["status"] == "pass"
            else "BLOCKED"
        ),
        "wholeAssembledCaseOnly": True,
        "labelContentApproved": False,
        "meshClippedSheenOutsideSilhouettePixels": 0,
        "gate09Status": "blocked",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "checks": {
            "blenderAuditPassed": report["status"] == "pass",
            "imageValidationPassed": images["status"] == "pass",
            "lightingBuildPassed": build["status"] == "pass",
            "allReviewEvidencePresent": checks["requiredOutputsPresent"],
        },
    }
    QA_REPORT.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "status": report["status"],
                "geometryDigest": report["geometryDigest"],
                "materialDigest": report["materialDigest"],
                "activeLights": report["activeLightNames"],
                "qaResult": qa["result"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
