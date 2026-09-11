#!/usr/bin/env python3
"""Render actual rev 1/rev 2 exports with one plain full-model review camera."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001" / "magnetic-slide-tile.fbx"
REV2 = ROOT.parent / "rev-002" / "magnetic-slide-tile-r002.fbx"
REPORT = ROOT / "plain-review-render-recipe.json"
CAMERA_LOCATION = Vector((0.072, -0.092, 0.046))
CAMERA_TARGET = Vector((0.0, -0.002, 0.0))


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_scene() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 3200
    scene.render.resolution_y = 1800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.35
    scene.view_settings.gamma = 1.0
    world = bpy.data.worlds.new("PlainReviewWorld")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.014, 0.017, 0.022, 1.0)
    background.inputs["Strength"].default_value = 0.3
    scene.world = world

    silver = bpy.data.materials.new("PlainReviewSilver")
    silver.use_nodes = True
    shader = silver.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (0.97, 0.965, 0.94, 1.0)
    shader.inputs["Metallic"].default_value = 1.0
    shader.inputs["Roughness"].default_value = 0.045
    shader.inputs["Emission Strength"].default_value = 0.0
    for obj in [item for item in bpy.data.objects if item.type == "MESH"]:
        obj.data.materials.clear()
        obj.data.materials.append(silver)
        for polygon in obj.data.polygons:
            polygon.material_index = 0

    camera_data = bpy.data.cameras.new("PlainReviewCamera")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = CAMERA_LOCATION
    camera_data.lens = 68.0
    camera_data.sensor_width = 36.0
    look_at(camera, CAMERA_TARGET)
    scene.camera = camera

    lights = [
        ("LongWhiteBand", (-0.052, -0.042, 0.052), (0.0, 0.0, 0.0), 980.0, (1.0, 0.99, 0.97), 0.060, 0.008),
        ("FrontFill", (0.044, -0.050, 0.030), (0.0, -0.008, 0.0), 520.0, (1.0, 1.0, 1.0), 0.028, 0.022),
        ("BackRim", (0.030, 0.055, 0.025), (0.0, 0.010, 0.0), 460.0, (0.95, 0.98, 1.0), 0.040, 0.007),
    ]
    for name, location, target, energy, color, size, size_y in lights:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "RECTANGLE"
        data.size = size
        data.size_y = size_y
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        look_at(light, Vector(target))


def render_export(path: Path, output: str) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
    setup_scene()
    scene = bpy.context.scene
    scene.render.filepath = str(ROOT / output)
    bpy.ops.render.render(write_still=True)
    return {
        "source": str(path.relative_to(ROOT.parents[7])),
        "output": output,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "cameraLocationMeters": list(CAMERA_LOCATION),
        "cameraTargetMeters": list(CAMERA_TARGET),
        "lensMm": scene.camera.data.lens,
    }


def main() -> None:
    records = [
        render_export(REV1, "plain-full-before.png"),
        render_export(REV2, "plain-full-after.png"),
    ]
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "reviewRevision": 3,
        "actualComparison": True,
        "records": records,
        "lighting": {
            "purpose": "one long reflection band makes discontinuities visible without changing geometry",
            "silverRoughness": 0.045,
            "exposure": -0.35,
            "emission": 0.0,
        },
        "pass": all((ROOT / item["output"]).exists() for item in records),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Plain Gate 10 review render failed.")


if __name__ == "__main__":
    main()
