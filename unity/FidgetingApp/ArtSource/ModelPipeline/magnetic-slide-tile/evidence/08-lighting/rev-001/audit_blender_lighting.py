#!/usr/bin/env python3
"""Audit Gate 08 Blender cameras, lights, passes, materials, and geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-lighting-r001.blend"
REPORT = ROOT / "blender-lighting-audit.json"
EXPECTED_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"


def geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(obj.name.encode())
        for row in obj.matrix_world:
            for value in row:
                digest.update(f"{value:.12f}".encode())
        for vertex in mesh.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in mesh.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    digest = geometry_digest([lower, upper])
    cameras = {
        obj["camera_id"]: {
            "name": obj.name,
            "locationMm": list(obj.location),
            "targetMm": list(obj["target_mm"]),
            "lensMm": obj.data.lens,
        }
        for obj in bpy.data.objects
        if obj.type == "CAMERA" and obj.get("gate08_authored_camera")
    }
    lights = {
        obj.name: {
            "locationMm": list(obj.location),
            "powerW": obj.data.energy,
            "sizeMm": obj.data.size,
            "linearRgb": list(obj.data.color),
            "colorTemperatureKelvin": obj["color_temperature_kelvin"],
            "targetMm": list(obj["target_mm"]),
        }
        for obj in bpy.data.objects
        if obj.type == "LIGHT" and obj.get("gate08_controlled_lighting")
    }
    cards = {
        obj.name: {
            "cameraVisible": obj.visible_camera,
            "renderVisible": not obj.hide_render,
        }
        for obj in bpy.data.objects
        if obj.get("gate08_reflection_card")
    }
    shipping_materials = [
        bpy.data.materials["M07R7_DaylightNeutralPolishedSilver"],
        bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Upper"],
        bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Lower"],
    ]
    shipping_emission = {}
    for material in shipping_materials:
        shader = next(node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
        shipping_emission[material.name] = shader.inputs["Emission Strength"].default_value
    technical_materials = sorted(
        material.name for material in bpy.data.materials
        if material.get("gate08_technical_aov_only")
    )
    outputs = [
        "hero.png",
        "left-oblique.png",
        "right-oblique.png",
        "low-angle.png",
        "pass-beauty.png",
        "pass-clay.png",
        "pass-normal.png",
        "pass-depth.png",
        "pass-roughness.png",
        "open-side-reflection.png",
    ]
    checks = {
        "geometryDigestUnchanged": digest == EXPECTED_DIGEST,
        "closedPoseRestored": tuple(translation.location) == (0.0, 0.0, 0.0),
        "pointAxisPreserved": tuple(pivot.location) == (0.0, -9.5, 0.0),
        "hiddenEnvelopeUnchanged": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none",
        "materialSlotsRestored": [slot.material.name for slot in lower.material_slots]
        == ["M07R7_DaylightNeutralPolishedSilver", "M07R7_BloodRedCrystal_WideBorder_Lower"]
        and [slot.material.name for slot in upper.material_slots]
        == ["M07R7_DaylightNeutralPolishedSilver", "M07R7_BloodRedCrystal_WideBorder_Upper"],
        "shippingEmissionZero": all(value == 0.0 for value in shipping_emission.values()),
        "requiredCameras": {"hero", "left-oblique", "right-oblique", "low", "beauty", "open-side"}.issubset(cameras),
        "controlledLights": len(lights) == 4
        and all(item["powerW"] > 0 and item["sizeMm"] > 0 and item["colorTemperatureKelvin"] >= 5000 for item in lights.values()),
        "reflectionCardsCameraHidden": len(cards) == 4 and all(not item["cameraVisible"] for item in cards.values()),
        "technicalPassesSeparated": len(technical_materials) >= 5
        and all(bpy.data.materials[name].get("not_shipping_material") for name in technical_materials),
        "allOutputsPresent": all((ROOT / filename).exists() for filename in outputs),
        "gate08Only": scene["environment_composition_deferred_to_gate09"]
        and scene["unity_reflection_delivery_state"] == "specified-only-not-integrated"
        and scene["geometry_change_authorized"] is False
        and scene["material_change_authorized"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "blender": bpy.app.version_string,
        "renderer": scene.render.engine,
        "geometryDigest": digest,
        "cameras": cameras,
        "lights": lights,
        "reflectionCards": cards,
        "shippingEmissionStrengths": shipping_emission,
        "technicalPassMaterials": technical_materials,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 Blender lighting audit failed.")


if __name__ == "__main__":
    main()
