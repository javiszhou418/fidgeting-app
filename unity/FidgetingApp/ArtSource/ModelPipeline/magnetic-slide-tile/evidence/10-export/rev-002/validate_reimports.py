#!/usr/bin/env python3
"""Re-import and inspect Gate 10 FBX, GLB, and collision exports."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
FBX = ROOT / "magnetic-slide-tile-r002.fbx"
GLB = ROOT / "magnetic-slide-tile-r002.glb"
COLLISION_FBX = ROOT / "magnetic-slide-tile-collision-r002.fbx"
EXPORT_MANIFEST = ROOT / "export-manifest.json"
GLB_STRUCTURE = ROOT / "glb-structure-validation.json"
OUTPUT = ROOT / "reimport-validation.json"


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mesh_objects() -> list[bpy.types.Object]:
    return sorted([obj for obj in bpy.data.objects if obj.type == "MESH"], key=lambda item: item.name)


def bounds(objects: list[bpy.types.Object]) -> dict:
    points = [obj.matrix_world @ vertex.co for obj in objects for vertex in obj.data.vertices]
    minimum = [min(point[index] for point in points) for index in range(3)]
    maximum = [max(point[index] for point in points) for index in range(3)]
    return {
        "minimumMeters": [round(value, 9) for value in minimum],
        "maximumMeters": [round(value, 9) for value in maximum],
        "sizeMeters": [round(maximum[index] - minimum[index], 9) for index in range(3)],
    }


def triangles(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def object_record(obj: bpy.types.Object) -> dict:
    return {
        "name": obj.name,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "location": [round(float(value), 9) for value in obj.location],
        "rotationRadians": [round(float(value), 9) for value in obj.rotation_euler],
        "scale": [round(float(value), 9) for value in obj.scale],
    }


def material_slots(obj: bpy.types.Object) -> list[str]:
    return [slot.material.name for slot in obj.material_slots if slot.material]


def inspect_render_import(kind: str) -> dict:
    objects = mesh_objects()
    by_name = {obj.name: obj for obj in objects}
    expected_names = {"LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"}
    root = bpy.data.objects.get("MagneticSlideTile_Blockout_R003")
    translation = bpy.data.objects.get("UpperTranslation")
    pivot = bpy.data.objects.get("CentralAxisPivot_Point")
    envelope = bpy.data.objects.get("ConcealedCircularEnvelope_Metadata")
    image_records = {
        image.name: {
            "size": list(image.size),
            "filepath": bpy.path.abspath(image.filepath),
        }
        for image in bpy.data.images
        if image.name != "Render Result"
    }
    records = {
        "kind": kind,
        "bounds": bounds(objects),
        "objects": {obj.name: object_record(obj) for obj in bpy.data.objects},
        "meshTriangles": {obj.name: triangles(obj) for obj in objects},
        "materialSlots": {obj.name: material_slots(obj) for obj in objects},
        "uvLayers": {obj.name: [layer.name for layer in obj.data.uv_layers] for obj in objects},
        "loopNormals": {obj.name: len(obj.data.corner_normals) for obj in objects},
        "meshLoops": {obj.name: len(obj.data.loops) for obj in objects},
        "images": image_records,
        "actions": [action.name for action in bpy.data.actions],
        "constraints": {
            obj.name: [constraint.name for constraint in obj.constraints]
            for obj in bpy.data.objects if obj.constraints
        },
        "drivers": {
            obj.name: [driver.data_path for driver in obj.animation_data.drivers]
            for obj in bpy.data.objects
            if obj.animation_data and obj.animation_data.drivers
        },
    }
    records["checks"] = {
        "twoRenderMeshes": set(by_name) == expected_names,
        "meterBounds": all(
            abs(actual - expected) <= 2e-6
            for actual, expected in zip(records["bounds"]["sizeMeters"], [0.031, 0.05, 0.012])
        ),
        "triangleCount4096": sum(records["meshTriangles"].values()) == 4096,
        "twoMaterialSlotsEach": all(len(records["materialSlots"][name]) == 2 for name in expected_names),
        "materialNamesPreserved": records["materialSlots"] == {
            "LowerBody_Fixed_CleanPlane": [
                "M07R7_DaylightNeutralPolishedSilver",
                "M07R7_BloodRedCrystal_WideBorder_Lower",
            ],
            "UpperCapsule_Moving": [
                "M07R7_DaylightNeutralPolishedSilver",
                "M07R7_BloodRedCrystal_WideBorder_Upper",
            ],
        },
        "uvPresent": all(records["uvLayers"][name] for name in expected_names),
        "normalsPresent": all(records["loopNormals"][name] == records["meshLoops"][name] for name in expected_names),
        "closedDefault": translation is not None
        and all(abs(value) < 1e-9 for value in translation.location)
        and all(abs(value) < 1e-9 for value in translation.rotation_euler),
        "pointPivotPreserved": pivot is not None
        and abs(pivot.location.y + 9.5) <= 1e-6
        and pivot.parent is translation,
        "rootMeterScale": root is not None and all(abs(value - 0.001) <= 1e-8 for value in root.scale),
        "hiddenEnvelopeMetadata": envelope is not None and envelope.type == "EMPTY",
        "noAnimationsConstraintsDrivers": not records["actions"] and not records["constraints"] and not records["drivers"],
        "transportTextures620x1000": len(image_records) >= 2
        and all(item["size"] == [620, 1000] for item in image_records.values()),
    }
    records["pass"] = all(records["checks"].values())
    return records


def import_glb() -> dict:
    reset()
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    return inspect_render_import("GLB")


def import_fbx() -> dict:
    reset()
    bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True)
    return inspect_render_import("FBX")


def import_collision() -> dict:
    reset()
    bpy.ops.import_scene.fbx(filepath=str(COLLISION_FBX), use_custom_normals=True)
    objects = mesh_objects()
    records = {
        "kind": "collision-FBX",
        "bounds": bounds(objects),
        "objects": {obj.name: object_record(obj) for obj in bpy.data.objects},
        "meshTriangles": {obj.name: triangles(obj) for obj in objects},
        "materials": {obj.name: material_slots(obj) for obj in objects},
        "actions": [action.name for action in bpy.data.actions],
    }
    records["checks"] = {
        "twoCapsules": [obj.name for obj in objects] == [
            "UCX_MagneticSlideTile_Lower_00",
            "UCX_MagneticSlideTile_Upper_00",
        ],
        "convexBudget": sum(records["meshTriangles"].values()) == 256,
        "noMaterials": all(not slots for slots in records["materials"].values()),
        "meterBoundsWithinRender": all(
            actual <= expected + 2e-6
            for actual, expected in zip(records["bounds"]["sizeMeters"], [0.031, 0.05, 0.012])
        ),
        "noAnimations": not records["actions"],
        "closedDefault": bpy.data.objects.get("UpperTranslation") is not None
        and all(abs(value) < 1e-9 for value in bpy.data.objects["UpperTranslation"].location),
    }
    records["pass"] = all(records["checks"].values())
    return records


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_import(path: Path, kind: str, output: Path, collision: bool = False) -> None:
    reset()
    if path.suffix.lower() == ".glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(output)
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.background_type = "WORLD"
    if scene.world is None:
        scene.world = bpy.data.worlds.new(f"{kind}_World")
    scene.world.color = (0.012, 0.016, 0.023)
    if collision:
        material = bpy.data.materials.new("CollisionReviewOrange")
        material.diffuse_color = (0.95, 0.26, 0.04, 1.0)
        for obj in mesh_objects():
            obj.data.materials.append(material)
    else:
        for material in bpy.data.materials:
            if "Silver" in material.name:
                material.diffuse_color = (0.62, 0.62, 0.62, 1.0)
            elif "BloodRed" in material.name:
                material.diffuse_color = (0.30, 0.015, 0.025, 1.0)
    camera_data = bpy.data.cameras.new(f"{kind}_CameraData")
    camera = bpy.data.objects.new(f"{kind}_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.09, -0.13, 0.075)
    camera_data.lens = 70
    point_camera(camera, (0.0, 0.0, 0.0))
    scene.camera = camera
    bpy.ops.render.render(write_still=True)


def main() -> None:
    manifest = json.loads(EXPORT_MANIFEST.read_text(encoding="utf-8"))
    glb_structure = json.loads(GLB_STRUCTURE.read_text(encoding="utf-8"))
    glb = import_glb()
    fbx = import_fbx()
    collision = import_collision()
    render_import(GLB, "GLBReimport", ROOT / "glb-reimport-workbench.png")
    render_import(FBX, "FBXReimport", ROOT / "fbx-reimport-workbench.png")
    render_import(COLLISION_FBX, "CollisionReimport", ROOT / "collision-reimport-workbench.png", collision=True)
    checks = {
        "exportManifestPasses": manifest["pass"],
        "glbStructurePasses": glb_structure["pass"],
        "glbReimportPasses": glb["pass"],
        "fbxReimportPasses": fbx["pass"],
        "collisionReimportPasses": collision["pass"],
        "matchingRenderMetrics": all(
            abs(left - right) <= 2e-6
            for left, right in zip(glb["bounds"]["sizeMeters"], fbx["bounds"]["sizeMeters"])
        )
        and glb["meshTriangles"] == fbx["meshTriangles"]
        and glb["materialSlots"] == fbx["materialSlots"],
        "requiredReimportImages": all(
            (ROOT / name).exists()
            for name in [
                "glb-reimport-workbench.png",
                "fbx-reimport-workbench.png",
                "collision-reimport-workbench.png",
            ]
        ),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "blender": bpy.app.version_string,
        "glb": glb,
        "fbx": fbx,
        "collision": collision,
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 deterministic re-import validation failed.")


if __name__ == "__main__":
    main()
