#!/usr/bin/env python3
"""Audit Gate 09 Blender environment and frozen model contracts."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-environment-r001.blend"
ENVIRONMENT = ROOT / "environment-validation.json"
OPTIMIZATION = ROOT / "optimization-decision.json"
OUTPUT = ROOT / "blender-environment-audit.json"
MODEL_OBJECTS = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]
SHIPPING_MATERIALS = [
    "M07R7_DaylightNeutralPolishedSilver",
    "M07R7_BloodRedCrystal_WideBorder_Upper",
    "M07R7_BloodRedCrystal_WideBorder_Lower",
]


def main() -> None:
    environment = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))
    optimization = json.loads(OPTIMIZATION.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    triangles = {}
    for name in MODEL_OBJECTS:
        mesh = bpy.data.objects[name].data
        mesh.calc_loop_triangles()
        triangles[name] = len(mesh.loop_triangles)
    emission = {}
    for name in SHIPPING_MATERIALS:
        material = bpy.data.materials[name]
        shader = next(node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
        emission[name] = float(shader.inputs["Emission Strength"].default_value)
    world_nodes = {node.name for node in scene.world.node_tree.nodes}
    controlled_lights = sorted(
        obj.name for obj in bpy.data.objects
        if obj.type == "LIGHT" and obj.get("gate08_controlled_lighting") and not obj.hide_render
    )
    lod_objects = [
        obj.name for obj in bpy.data.objects
        if obj.name.lower().startswith("lod")
        or "_lod" in obj.name.lower()
        or ".lod" in obj.name.lower()
    ]
    decimate_modifiers = [
        f"{obj.name}:{modifier.name}"
        for obj in bpy.data.objects
        for modifier in obj.modifiers
        if modifier.type == "DECIMATE"
    ]
    checks = {
        "gateAndRevision": scene["gate"] == "09-environment" and scene["environment_revision"] == 1,
        "approvalWording": scene["source_gate08_approval_wording"] == "可以吧，然后你继续",
        "geometryDigestFrozen": environment["invariants"]["geometryUnchanged"],
        "cameraContractFrozen": environment["invariants"]["camerasUnchanged"],
        "lightContractFrozen": environment["invariants"]["lightsUnchanged"] and len(controlled_lights) == 4,
        "materialContractFrozen": environment["invariants"]["materialsUnchanged"]
        and environment["invariants"]["materialAssignmentsUnchanged"],
        "shippingEmissionZero": all(value == 0.0 for value in emission.values()),
        "shippingWorldNodesPresent": {
            "M09R1_AdaptiveBackground",
            "M09R1_TopDownAdaptiveField",
            "M09R1_StaticFineGrain",
            "M09R1_EnvironmentReflectionContent",
        }.issubset(world_nodes),
        "shippingGroundPresent": bpy.data.objects["PresentationGround"].data.materials[0].name == "M09R1_ShippingAdaptiveGround",
        "single4096TriangleModel": sum(triangles.values()) == 4096,
        "noLods": not lod_objects and not decimate_modifiers,
        "independentArtworkMasks": optimization["checks"]["upperLowerMasksRemainIndependent"],
        "scopeFlags": not scene["geometry_change_authorized"]
        and not scene["lod_creation_authorized"]
        and not scene["unity_change_authorized"]
        and not scene["blender_environment_is_unity_integration"],
        "pointAxisAndEnvelope": list(bpy.data.objects["CentralAxisPivot_Point"].location) == [0.0, -9.5, 0.0]
        and bpy.data.objects["ConcealedCircularEnvelope_Metadata"].type == "EMPTY"
        and bpy.data.objects["ConcealedCircularEnvelope_Metadata"].hide_render,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 1,
        "blender": bpy.app.version_string,
        "triangles": triangles,
        "controlledLights": controlled_lights,
        "worldNodes": sorted(world_nodes),
        "shippingMaterialEmissionStrengths": emission,
        "lodObjects": lod_objects,
        "decimateModifiers": decimate_modifiers,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 Blender environment audit failed.")


if __name__ == "__main__":
    main()
