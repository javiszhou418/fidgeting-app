#!/usr/bin/env python3
"""Audit Gate 07 rev 7 border, daylight silver, artwork, and geometry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-material-r007.blend"
REPORT = ROOT / "blender-audit.json"
EXPECTED_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
EXPECTED_MASK_SHA256 = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
EXPECTED_BORDER_SHA256 = "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc"


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
    upper_material = bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Upper"]
    lower_material = bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Lower"]
    silver_material = bpy.data.materials["M07R7_DaylightNeutralPolishedSilver"]
    groups = {}
    for name in ("Artwork_Upper", "Artwork_Lower"):
        group = bpy.data.node_groups[name]
        image_nodes = [node for node in group.nodes if node.bl_idname == "ShaderNodeTexImage"]
        groups[name] = {
            "externalMaskRepositoryRelative": group["externalMaskRepositoryRelative"],
            "externalMaskSha256": group["externalMaskSha256"],
            "borderMaskRepositoryRelative": group["borderMaskRepositoryRelative"],
            "borderMaskSha256": group["borderMaskSha256"],
            "borderOverlayEnabled": group["borderOverlayEnabled"],
            "borderCompositionOperation": group["borderCompositionOperation"],
            "swapWithoutGeometryRebuild": group["swapWithoutGeometryRebuild"],
            "imageNodeCount": len(image_nodes),
            "packed": any(node.image and node.image.packed_file for node in image_nodes),
            "sourcePaths": [bpy.path.abspath(node.image.filepath) for node in image_nodes if node.image],
            "interpolation": [node.interpolation for node in image_nodes],
        }
    digest = geometry_digest([lower, upper])
    emissions = {}
    for material in (upper_material, lower_material, silver_material):
        shader = material.node_tree.nodes["Principled BSDF"]
        emissions[material.name] = shader.inputs["Emission Strength"].default_value
    silver_shader = silver_material.node_tree.nodes["Principled BSDF"]
    light_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "LIGHT" and obj.name.startswith("M07R7_"))
    camera_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "CAMERA" and obj.name.startswith("M07R7_"))
    card_names = sorted(obj.name for obj in bpy.data.objects if obj.get("gate07_calibrated_reflection_card"))
    checks = {
        "geometryDigestUnchanged": digest == EXPECTED_DIGEST,
        "closedPoseRestored": tuple(translation.location) == (0.0, 0.0, 0.0),
        "hiddenEnvelopeUnchanged": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none",
        "upperSlotExists": "Artwork_Upper" in bpy.data.node_groups,
        "lowerSlotExists": "Artwork_Lower" in bpy.data.node_groups,
        "externalMasksNotPacked": all(not item["packed"] for item in groups.values()),
        "losslessPriorMaskHashes": groups["Artwork_Upper"]["externalMaskSha256"]
        == groups["Artwork_Lower"]["externalMaskSha256"]
        == EXPECTED_MASK_SHA256,
        "independentMaskPaths": groups["Artwork_Upper"]["externalMaskRepositoryRelative"]
        != groups["Artwork_Lower"]["externalMaskRepositoryRelative"],
        "nearestMaskSampling": all(
            item["interpolation"] == ["Closest", "Closest"] for item in groups.values()
        ),
        "externalBorderMask": all(
            item["borderOverlayEnabled"]
            and item["borderMaskSha256"] == EXPECTED_BORDER_SHA256
            and item["borderCompositionOperation"] == "MAXIMUM"
            for item in groups.values()
        ),
        "upperMaterialAssigned": upper.material_slots[1].material == upper_material,
        "lowerMaterialAssigned": lower.material_slots[1].material == lower_material,
        "noEmission": all(value == 0.0 for value in emissions.values()),
        "pureSilverShader": all(
            abs(actual - expected) < 1e-5
            for actual, expected in zip(list(silver_shader.inputs["Base Color"].default_value)[:3], [0.97, 0.965, 0.94])
        )
        and abs(silver_shader.inputs["Metallic"].default_value - 1.0) < 1e-5
        and abs(silver_shader.inputs["Roughness"].default_value - 0.03) < 1e-5
        and abs(silver_shader.inputs["Anisotropic"].default_value - 0.14) < 1e-5,
        "silverMicroScratchBump": any(node.bl_idname == "ShaderNodeBump" for node in silver_material.node_tree.nodes),
        "reflectionCardsPresent": {
            "M07R7_D65Reference_White80",
            "M07R7_D65Reference_Gray18",
            "M07R7_D65Reference_Black",
            "M07R7_Studio_WhiteReflector",
            "M07R7_Studio_BlackReflector",
        }.issubset(card_names),
        "d65DiagnosticLightsPresent": {
            "M07R7_D65_6504K_Sun",
            "M07R7_D65_NeutralOvercastFill",
        }.issubset(light_names),
        "diagnosticCamerasPresent": {
            "M07R7_NeutralFrontCamera",
            "M07R7_OpenArtworkCamera",
            "M07R7_D65HeroCamera",
            "M07R7_D65SideCamera",
        }.issubset(camera_names),
        "sceneBorderParameters": bpy.context.scene["top_face_black_border_width_px"] == 64
        and bpy.context.scene["top_face_black_border_outer_inset_px"] == 0,
        "d65FixedExposure": bpy.context.scene["daylight_diagnostic_cct_kelvin"] == 6504
        and bpy.context.scene["daylight_diagnostic_fixed_exposure_ev"] == 0.0,
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 7,
        "blender": bpy.app.version_string,
        "geometryDigest": digest,
        "artworkNodeGroups": groups,
        "materialSlots": {
            lower.name: [slot.material.name for slot in lower.material_slots],
            upper.name: [slot.material.name for slot in upper.material_slots],
        },
        "emissionStrengths": emissions,
        "silverPbr": {
            "baseColor": list(silver_shader.inputs["Base Color"].default_value),
            "metallic": silver_shader.inputs["Metallic"].default_value,
            "roughness": silver_shader.inputs["Roughness"].default_value,
            "anisotropy": silver_shader.inputs["Anisotropic"].default_value,
            "anisotropyRotation": silver_shader.inputs["Anisotropic Rotation"].default_value,
            "coatWeight": silver_shader.inputs["Coat Weight"].default_value,
            "coatRoughness": silver_shader.inputs["Coat Roughness"].default_value,
        },
        "reflectionCards": card_names,
        "lights": light_names,
        "cameras": camera_names,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 7 Blender audit failed.")


if __name__ == "__main__":
    main()
