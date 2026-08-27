#!/usr/bin/env python3
"""Audit Gate 09 rev 2 open pose, cameras, materials, and environment."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-environment-open-r002.blend"
SCENE_REPORT = ROOT / "open-environment-validation.json"
IMAGE_REPORT = ROOT / "open-image-validation.json"
OUTPUT = ROOT / "blender-open-audit.json"
MODEL_OBJECTS = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]
SHIPPING_MATERIALS = [
    "M07R7_DaylightNeutralPolishedSilver",
    "M07R7_BloodRedCrystal_WideBorder_Upper",
    "M07R7_BloodRedCrystal_WideBorder_Lower",
]


def matrix(obj: bpy.types.Object) -> list[list[float]]:
    return [[round(float(value), 9) for value in row] for row in obj.matrix_world]


def main() -> None:
    scene_report = json.loads(SCENE_REPORT.read_text(encoding="utf-8"))
    image_report = json.loads(IMAGE_REPORT.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    triangles = {}
    for name in MODEL_OBJECTS:
        mesh = bpy.data.objects[name].data
        mesh.calc_loop_triangles()
        triangles[name] = len(mesh.loop_triangles)
    emission = {}
    for name in SHIPPING_MATERIALS:
        shader = next(
            node for node in bpy.data.materials[name].node_tree.nodes
            if node.bl_idname == "ShaderNodeBsdfPrincipled"
        )
        emission[name] = float(shader.inputs["Emission Strength"].default_value)
    camera_names = [
        "M09R2_OpenHeroCamera",
        "M09R2_OpenObliqueCamera",
        "M09R2_OpenTopCamera",
        "M09R2_OpenLayerCamera",
    ]
    cameras = {
        name: {
            "matrixWorld": matrix(bpy.data.objects[name]),
            "lensMm": float(bpy.data.objects[name].data.lens),
        }
        for name in camera_names
    }
    lod_objects = [
        obj.name for obj in bpy.data.objects
        if obj.name.lower().startswith("lod")
        or "_lod" in obj.name.lower()
        or ".lod" in obj.name.lower()
    ]
    decimate = [
        f"{obj.name}:{modifier.name}"
        for obj in bpy.data.objects
        for modifier in obj.modifiers
        if modifier.type == "DECIMATE"
    ]
    controlled_lights = [
        obj.name for obj in bpy.data.objects
        if obj.type == "LIGHT" and obj.get("gate08_controlled_lighting") and not obj.hide_render
    ]
    visible_internal_meshes = [
        obj.name for obj in bpy.data.objects
        if obj.type == "MESH"
        and obj.get("internal_mechanism")
        and not obj.hide_render
    ]
    artwork = {
        group_name: {
            "externalMaskNode": next(
                node.name for node in bpy.data.node_groups[group_name].nodes
                if node.name.endswith("_ExternalMask")
            ),
            "imagePath": bpy.path.abspath(next(
                node.image.filepath for node in bpy.data.node_groups[group_name].nodes
                if node.name.endswith("_ExternalMask")
            )),
        }
        for group_name in ["Artwork_Upper", "Artwork_Lower"]
    }
    checks = {
        "gateAndRevision": scene["gate"] == "09-environment" and scene["environment_revision"] == 2,
        "rev1RecordedIncomplete": scene["source_gate09_rev1_status"] == "rejected-incomplete-no-open-view",
        "exact21MmPositiveY": list(translation.location) == [0.0, 21.0, 0.0],
        "zeroSpin": all(abs(value) < 1e-9 for value in translation.rotation_euler)
        and all(abs(value) < 1e-9 for value in pivot.rotation_euler)
        and all(abs(value) < 1e-9 for value in upper.rotation_euler),
        "fixedLowerMatrix": matrix(lower) == scene_report["pose"]["lowerMatrixBefore"]
        == scene_report["pose"]["lowerMatrixAfter"],
        "upperWorldTranslation": matrix(upper)[1][3] == 21.0,
        "single4096TriangleModel": sum(triangles.values()) == 4096,
        "noLodsOrDecimate": not lod_objects and not decimate,
        "geometryUnchanged": scene_report["checks"]["geometryUnchanged"],
        "materialsUnchanged": scene_report["checks"]["materialsUnchanged"],
        "approvedLightingUnchanged": scene_report["checks"]["approvedLightingUnchanged"]
        and len(controlled_lights) == 4,
        "approvedEnvironmentUnchanged": scene_report["checks"]["approvedEnvironmentUnchanged"]
        and scene.world.name == "M09R2_ShippingAdaptiveWorld",
        "camerasRealAndRecorded": all(
            cameras[name]["matrixWorld"] == scene_report["cameras"][name]["matrixWorld"]
            and cameras[name]["matrixWorld"] != [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
            for name in camera_names
        ),
        "artworkSlotsIndependent": artwork["Artwork_Upper"]["imagePath"]
        != artwork["Artwork_Lower"]["imagePath"]
        and scene_report["checks"]["independentArtworkSlots"],
        "mechanismConcealed": envelope.type == "EMPTY"
        and envelope.hide_render
        and envelope["geometry"] == "none"
        and not visible_internal_meshes,
        "shippingEmissionZero": all(value == 0.0 for value in emission.values()),
        "imageValidationPasses": image_report["pass"],
        "gate09Only": not scene["unity_change_authorized"]
        and not scene["gate10_authorized"]
        and scene_report["checks"]["gate09Only"],
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 2,
        "blender": bpy.app.version_string,
        "triangles": triangles,
        "pose": {
            "upperTranslationMm": list(translation.location),
            "upperRotationRadians": list(translation.rotation_euler),
            "upperWorldMatrix": matrix(upper),
            "lowerWorldMatrix": matrix(lower),
            "pointAxisClosedLocalMm": list(pivot.location),
            "pointAxisOpenWorldMm": list(pivot.matrix_world.translation),
        },
        "cameras": cameras,
        "controlledLights": sorted(controlled_lights),
        "artwork": artwork,
        "shippingMaterialEmissionStrengths": emission,
        "lodObjects": lod_objects,
        "decimateModifiers": decimate,
        "visibleInternalMechanismMeshes": visible_internal_meshes,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 rev 2 Blender audit failed.")


if __name__ == "__main__":
    main()
