#!/usr/bin/env python3
"""Audit the clean authoritative Gate 10 Blender source and package hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-authoritative-r002.blend"
MANIFEST = ROOT / "export-manifest.json"
OUTPUT = ROOT / "blender-export-audit.json"
EXPECTED_LOCAL_MESH_HASH = "50b1f913f8b94a1428af404478cb5169d7e142b765955d224125108de463d5d0"
RENDER_NAMES = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_mesh_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode())
        for vertex in obj.data.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in obj.data.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
    return digest.hexdigest()


def triangles(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def emission_strength(material: bpy.types.Material) -> float:
    if not material.node_tree:
        return 0.0
    values = []
    for node in material.node_tree.nodes:
        if node.bl_idname == "ShaderNodeBsdfPrincipled" and "Emission Strength" in node.inputs:
            values.append(float(node.inputs["Emission Strength"].default_value))
    return max(values, default=0.0)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    render_objects = [bpy.data.objects[name] for name in RENDER_NAMES]
    collision = sorted(
        [obj for obj in bpy.data.objects if obj.get("collision_proxy")],
        key=lambda item: item.name,
    )
    unexpected_meshes = [
        obj.name for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name not in RENDER_NAMES and obj not in collision
    ]
    material_names = {
        slot.material.name
        for obj in render_objects
        for slot in obj.material_slots
        if slot.material
    }
    relative_images = {
        image.name: image.filepath
        for image in bpy.data.images
        if image.name.startswith("artwork-")
    }
    package_hashes = {
        key: sha256(ROOT.parents[7] / item["path"])
        for key, item in manifest["exports"].items()
        if isinstance(item, dict) and "path" in item
    }
    expected_hashes = {
        key: item["sha256"]
        for key, item in manifest["exports"].items()
        if isinstance(item, dict) and "sha256" in item
    }
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    checks = {
        "blendHash": sha256(BLEND) == manifest["exports"]["authoritativeBlend"]["sha256"],
        "packageHashes": package_hashes == expected_hashes,
        "noDiagnosticCamerasLights": not any(obj.type in {"CAMERA", "LIGHT"} for obj in bpy.data.objects),
        "noDiagnosticEnvironment": bpy.context.scene.world is None,
        "twoRenderMeshesOnly": not unexpected_meshes and len(render_objects) == 2,
        "renderTriangles4096": sum(triangles(obj) for obj in render_objects) == 4096,
        "approvedGeometryHash": local_mesh_hash(render_objects) == EXPECTED_LOCAL_MESH_HASH,
        "closedDefault": list(translation.location) == [0.0, 0.0, 0.0]
        and all(abs(value) < 1e-9 for value in translation.rotation_euler),
        "pointAxis": list(pivot.location) == [0.0, -9.5, 0.0]
        and pivot.get("axis") == "+Z",
        "slideMetadata": translation.get("axis") == "+Y"
        and translation.get("travel_mm") == 21.0
        and translation.get("may_rotate") is False,
        "detentSpecifiedOnly": pivot.get("detent_count") == 30
        and pivot.get("detent_step_degrees") == 12.0
        and pivot.get("detent_delivery_state") == "specified-only-runtime-haptic-pending",
        "hiddenEnvelopeMetadataOnly": envelope.type == "EMPTY"
        and envelope.get("geometry") == "none"
        and envelope.hide_render,
        "collisionTwoCapsules256": len(collision) == 2
        and sum(triangles(obj) for obj in collision) == 256
        and all(obj.hide_render and obj.get("convex") for obj in collision),
        "approvedMaterialSlots": material_names == {
            "M07R7_DaylightNeutralPolishedSilver",
            "M07R7_BloodRedCrystal_WideBorder_Upper",
            "M07R7_BloodRedCrystal_WideBorder_Lower",
        },
        "zeroEmission": all(emission_strength(bpy.data.materials[name]) == 0 for name in material_names),
        "uvsPresent": all(obj.data.uv_layers.get("UV0") is not None for obj in render_objects),
        "sideWallsSmooth": all(
            sum(polygon.use_smooth and abs(polygon.normal.z) < 0.5 for polygon in obj.data.polygons) == 513
            for obj in render_objects
        ),
        "capsFlat": all(
            sum(not polygon.use_smooth and abs(polygon.normal.z) >= 0.5 for polygon in obj.data.polygons) == 2
            for obj in render_objects
        ),
        "capSideEdgesSharp": all(
            sum(edge.use_edge_sharp for edge in obj.data.edges) == 1026
            for obj in render_objects
        ),
        "relativeArtworkPaths": len(relative_images) == 3
        and all(path.startswith("//textures/") for path in relative_images.values()),
        "noActions": not bpy.data.actions,
        "noConstraintsDrivers": not any(obj.constraints for obj in bpy.data.objects)
        and not any(obj.animation_data and obj.animation_data.drivers for obj in bpy.data.objects),
        "noLodObjects": not any("lod" in obj.name.lower() for obj in bpy.data.objects),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "blender": bpy.app.version_string,
        "objectNames": sorted(obj.name for obj in bpy.data.objects),
        "renderTriangles": {obj.name: triangles(obj) for obj in render_objects},
        "collisionTriangles": {obj.name: triangles(obj) for obj in collision},
        "materialNames": sorted(material_names),
        "imagePaths": relative_images,
        "unexpectedMeshes": unexpected_meshes,
        "packageHashes": package_hashes,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 Blender/package audit failed.")


if __name__ == "__main__":
    main()
