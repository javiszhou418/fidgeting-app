#!/usr/bin/env python3
"""Render the exported collision capsules as a separate wireframe-only panel."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
COLLISION = ROOT / "magnetic-slide-tile-collision-r002.fbx"
OUTPUT = ROOT / "collision-wireframe-only.png"
REPORT = ROOT / "collision-wireframe-validation.json"


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(COLLISION), use_custom_normals=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("CollisionWireframeWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.014, 0.024, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.1
    scene.world = world
    material = bpy.data.materials.new("CollisionWireframeCyan")
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (0.01, 0.72, 0.95, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.4
    shader.inputs["Emission Color"].default_value = (0.01, 0.72, 0.95, 1.0)
    shader.inputs["Emission Strength"].default_value = 3.5
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    for obj in meshes:
        obj.data.materials.clear()
        obj.data.materials.append(material)
        modifier = obj.modifiers.new("ReviewWireframeOnly", "WIREFRAME")
        modifier.thickness = 0.035
        modifier.use_replace = True
        if "Upper" in obj.name:
            obj.location.x += 40.0
    camera_data = bpy.data.cameras.new("CollisionWireframeCamera")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.020, 0.0, 0.120)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 0.085
    look_at(camera, Vector((0.020, 0.0, 0.0)))
    scene.camera = camera
    scene.render.filepath = str(OUTPUT)
    bpy.ops.render.render(write_still=True)
    triangles = {obj.name: sum(len(poly.vertices) - 2 for poly in obj.data.polygons) for obj in meshes}
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "source": COLLISION.name,
        "output": OUTPUT.name,
        "renderMode": "wireframe-only",
        "labelRequired": "仅碰撞，不会显示 / NON-RENDERING COLLISION",
        "triangles": triangles,
        "totalTriangles": sum(triangles.values()),
        "affectsRenderAppearance": False,
        "pass": len(meshes) == 2 and sum(triangles.values()) == 256 and OUTPUT.exists(),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Collision wireframe render failed.")


if __name__ == "__main__":
    main()
