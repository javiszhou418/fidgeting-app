#!/usr/bin/env python3
"""Audit Premium Display Case Gate 09 rev 1 Blender evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BUILD_SCRIPT = ROOT / "build_environment_revalidation.py"
BLEND = ROOT / "premium-display-case-environment-r001.blend"
BUILD_REPORT = ROOT / "environment-revalidation.json"
REPORT = ROOT / "blender-environment-audit.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    build = load_module("premium_display_case_gate09_build", BUILD_SCRIPT)
    report = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    if report.get("status") != "pass":
        raise RuntimeError("Gate 09 build report must pass before audit.")
    if build.sha256(BLEND) != report["outputBlendSha256"]:
        raise RuntimeError("Gate 09 Blender source hash changed.")

    gate08_builder = load_module(
        "premium_display_case_gate08_builder_for_gate09_audit",
        build.LIGHTING_BUILDER,
    )
    legacy = gate08_builder.load_module(
        "premium_display_case_gate08_legacy_for_gate09_audit",
        gate08_builder.LEGACY_BUILDER,
    )
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in build.SUBJECT_NAMES]
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    studios = [
        obj
        for name in build.STUDIO_NAMES
        if (obj := bpy.data.objects.get(name)) is not None
    ]
    lighting = json.loads(build.SOURCE_REPORT.read_text(encoding="utf-8"))
    approved_material_names = sorted(
        {
            *lighting["materials"]["materialGraphDigests"].keys(),
            "MAT_M07_ContinuousNeutralFriction",
        }
    )
    geometry = legacy.VALIDATOR.identity_snapshot(subjects)
    material_digest, _ = legacy.approved_material_digest(
        approved_material_names,
        subjects + proxies + studios,
    )
    cameras = build.camera_snapshot()
    lights = build.light_snapshot()
    shipping = bpy.data.objects["M09_ShippingCyclorama"]
    material = bpy.data.materials["MAT_M09_StaticNeutralFriction"]
    environment_nodes = list(material.node_tree.nodes)
    background_objects = [
        shipping,
        *(obj for obj in studios if obj is not None),
    ]
    active_lights = [
        obj
        for obj in scene.objects
        if obj.type == "LIGHT" and not obj.hide_render
    ]
    forbidden_named_objects = [
        obj.name
        for obj in scene.objects
        if any(
            token in obj.name.lower()
            for token in ("halo", "particle", "streak", "rarity", "bloom")
        )
        and not obj.name.startswith("M07_")
    ]
    checks = {
        "sourceBlendHashMatched": build.sha256(BLEND) == report["outputBlendSha256"],
        "sceneGateAndRevisionMatched": (
            scene.get("gate") == "09-environment"
            and scene.get("environment_revision") == 1
        ),
        "geometryDigestUnchanged": geometry["fullGeometryDigest"] == build.GEOMETRY_DIGEST,
        "materialDigestUnchanged": material_digest == build.MATERIAL_DIGEST,
        "approvedCameraDigestUnchanged": (
            build.digest_json(cameras) == report["matchedCamera"]["digestAfter"]
        ),
        "approvedLightingDigestUnchanged": (
            build.digest_json(lights) == report["approvedLighting"]["digestAfter"]
        ),
        "shippingEnvironmentPresent": (
            shipping.get("gate09_environment") is True
            and shipping.parent is None
            and shipping.hide_render is False
        ),
        "environmentMaterialNonEmissive": not any(
            node.bl_idname == "ShaderNodeEmission" for node in environment_nodes
        ),
        "environmentMaterialStaticGrain": (
            material.get("grain_intensity") == 0.012
            and material.get("grain_coordinate_space")
            == "environment-object-generated-static"
        ),
        "backgroundStatic": all(obj.animation_data is None for obj in background_objects),
        "cameraStatic": all(
            bpy.data.objects[name].animation_data is None
            for name, _ in build.VIEW_SPECS.values()
        ),
        "presentationRootStatic": bpy.data.objects["PresentationRoot"].animation_data is None,
        "callerOwnedContentSlotEmpty": len(bpy.data.objects["ContentSlot"].children) == 0,
        "onlyGate08LightsActive": (
            len(active_lights) == 3
            and all(obj.name.startswith("M08_") for obj in active_lights)
        ),
        "noGate09LightObjects": not any(
            obj.type == "LIGHT" and obj.name.startswith("M09_")
            for obj in scene.objects
        ),
        "noForbiddenEffectObjects": not forbidden_named_objects,
        "wholeAssembledCaseOnly": scene.get("whole_assembled_case_only") is True,
        "reviewExplodedPartCountZero": scene.get("review_exploded_part_count") == 0,
        "labelPlaceholderNotApproved": (
            scene.get("label_content_state") == "placeholder-not-approved"
        ),
        "meshClippedSheenInsideCase": (
            scene.get("mesh_clipped_sheen_outside_silhouette_pixels") == 0
        ),
        "unityValuesRemainTunable": scene.get("unity_values_locked") is False,
        "shippingUnityUnchanged": scene.get("shipping_unity_changed") is False,
        "buildInstallPhonePushFalse": scene.get("build_install_phone_push") is False,
    }
    payload = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "09-environment",
        "environmentRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceBlendPath": str(BLEND),
        "sourceBlendSha256": build.sha256(BLEND),
        "geometryDigest": geometry["fullGeometryDigest"],
        "materialDigest": material_digest,
        "cameraDigest": build.digest_json(cameras),
        "lightingDigest": build.digest_json(lights),
        "environmentObject": shipping.name,
        "environmentMaterial": material.name,
        "activeLightNames": [obj.name for obj in active_lights],
        "forbiddenNamedObjects": forbidden_named_objects,
        "checks": checks,
    }
    REPORT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if payload["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))
    print(json.dumps({"status": "pass", "checks": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
