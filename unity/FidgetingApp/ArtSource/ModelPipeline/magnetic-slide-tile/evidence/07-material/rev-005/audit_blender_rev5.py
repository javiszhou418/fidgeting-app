#!/usr/bin/env python3
"""Audit Gate 07 rev 5 Blender material, artwork slots, and geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-material-r005.blend"
REPORT = ROOT / "blender-audit.json"
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
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    upper_material = bpy.data.materials["M07R5_BloodRedCrystal_Artwork_Upper"]
    lower_material = bpy.data.materials["M07R5_BloodRedCrystal_Artwork_Lower"]
    groups = {}
    for name in ("Artwork_Upper", "Artwork_Lower"):
        group = bpy.data.node_groups[name]
        image_nodes = [node for node in group.nodes if node.bl_idname == "ShaderNodeTexImage"]
        groups[name] = {
            "externalMaskRepositoryRelative": group["externalMaskRepositoryRelative"],
            "externalMaskSha256": group["externalMaskSha256"],
            "swapWithoutGeometryRebuild": group["swapWithoutGeometryRebuild"],
            "imageNodeCount": len(image_nodes),
            "packed": any(node.image and node.image.packed_file for node in image_nodes),
            "sourcePaths": [bpy.path.abspath(node.image.filepath) for node in image_nodes if node.image],
        }
    digest = geometry_digest([lower, upper])
    emissions = {}
    for material in (upper_material, lower_material):
        shader = material.node_tree.nodes["Principled BSDF"]
        emissions[material.name] = shader.inputs["Emission Strength"].default_value
    light_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "LIGHT" and obj.name.startswith("M07R5_"))
    camera_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "CAMERA" and obj.name.startswith("M07R5_"))
    checks = {
        "geometryDigestUnchanged": digest == EXPECTED_DIGEST,
        "closedPoseRestored": tuple(translation.location) == (0.0, 0.0, 0.0),
        "hiddenEnvelopeUnchanged": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none",
        "upperSlotExists": "Artwork_Upper" in bpy.data.node_groups,
        "lowerSlotExists": "Artwork_Lower" in bpy.data.node_groups,
        "externalMasksNotPacked": all(not item["packed"] for item in groups.values()),
        "independentMaskHashes": groups["Artwork_Upper"]["externalMaskSha256"]
        != groups["Artwork_Lower"]["externalMaskSha256"],
        "upperMaterialAssigned": upper.material_slots[1].material == upper_material,
        "lowerMaterialAssigned": lower.material_slots[1].material == lower_material,
        "noEmission": all(value == 0.0 for value in emissions.values()),
        "diagnosticLightsPresent": {
            "M07R5_Diagnostic_Crystal_KeyRim",
            "M07R5_Diagnostic_SideDirect",
        }.issubset(light_names),
        "diagnosticCamerasPresent": {
            "M07R5_NeutralFrontCamera",
            "M07R5_SideReflectionCamera",
            "M07R5_OpenArtworkCamera",
        }.issubset(camera_names),
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 5,
        "blender": bpy.app.version_string,
        "geometryDigest": digest,
        "artworkNodeGroups": groups,
        "materialSlots": {
            lower.name: [slot.material.name for slot in lower.material_slots],
            upper.name: [slot.material.name for slot in upper.material_slots],
        },
        "emissionStrengths": emissions,
        "lights": light_names,
        "cameras": camera_names,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 5 Blender audit failed.")


if __name__ == "__main__":
    main()
