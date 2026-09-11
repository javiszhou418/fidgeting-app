#!/usr/bin/env python3
"""Render source, rejected FBX, corrected FBX, and corrected GLB under one silver rig."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001"
SOURCE_BLEND = ROOT / "magnetic-slide-tile-authoritative-r002.blend"
REV1_FBX = REV1 / "magnetic-slide-tile.fbx"
REV2_FBX = ROOT / "magnetic-slide-tile-r002.fbx"
REV2_GLB = ROOT / "magnetic-slide-tile-r002.glb"
OUTPUT = ROOT / "smoothing-render-recipe.json"
RENDER_NAMES = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]
CAMERA_LOCATION = Vector((0.052, -0.058, 0.019))
CAMERA_TARGET = Vector((0.0, -0.011, 0.0005))


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def reset_render_scene() -> list[bpy.types.Object]:
    scene = bpy.context.scene
    root = bpy.data.objects.get("MagneticSlideTile_Blockout_R003")
    if root:
        root.scale = (0.001, 0.001, 0.001)
    objects = [bpy.data.objects[name] for name in RENDER_NAMES]
    for obj in objects:
        obj.hide_render = False
        obj.modifiers.clear()
    for obj in list(bpy.data.objects):
        if obj.type in {"LIGHT", "CAMERA"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.25
    scene.view_settings.gamma = 1.0
    world = bpy.data.worlds.new("Gate10R2_HighContrastWorld")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.012, 0.014, 0.018, 1.0)
    background.inputs["Strength"].default_value = 0.22
    scene.world = world

    material = bpy.data.materials.new("Gate10R2_NormalDiagnosticSilver")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.97, 0.965, 0.94, 1.0)
    shader.inputs["Metallic"].default_value = 1.0
    shader.inputs["Roughness"].default_value = 0.055
    shader.inputs["Coat Weight"].default_value = 0.0
    shader.inputs["Emission Strength"].default_value = 0.0
    for obj in objects:
        obj.data.materials.clear()
        obj.data.materials.append(material)
        for polygon in obj.data.polygons:
            polygon.material_index = 0

    camera_data = bpy.data.cameras.new("Gate10R2_ArcCloseup_Camera")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = CAMERA_LOCATION
    camera_data.lens = 92.0
    camera_data.sensor_width = 36.0
    look_at(camera, CAMERA_TARGET)
    scene.camera = camera

    lights = [
        ("WhiteStrip", (-0.034, -0.052, 0.036), (0.0, -0.007, 0.0), 820.0, (1.0, 0.985, 0.96), "RECTANGLE", 0.032, 0.006),
        ("NeutralKey", (0.038, -0.022, 0.026), (0.0, -0.010, 0.0), 560.0, (1.0, 1.0, 1.0), "RECTANGLE", 0.018, 0.045),
        ("RimStrip", (0.018, 0.035, 0.018), (0.0, 0.0, 0.0), 360.0, (0.96, 0.98, 1.0), "RECTANGLE", 0.025, 0.005),
    ]
    for name, location, target, energy, color, shape, size, size_y in lights:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = shape
        data.size = size
        data.size_y = size_y
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        look_at(light, Vector(target))
    bpy.context.view_layer.update()
    return objects


def render(label: str, output_name: str) -> dict:
    reset_render_scene()
    scene = bpy.context.scene
    path = ROOT / output_name
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return {
        "label": label,
        "path": path.name,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "cameraLocationMeters": list(CAMERA_LOCATION),
        "cameraTargetMeters": list(CAMERA_TARGET),
        "lensMm": scene.camera.data.lens,
    }


def open_source() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))


def import_fbx(path: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)


def import_glb(path: Path) -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))


def main() -> None:
    records = []
    open_source()
    records.append(render("authoritative source base mesh", "arc-closeup-source-2560.png"))
    import_fbx(REV1_FBX)
    records.append(render("rejected rev 1 FBX; smoothing metadata OFF", "arc-closeup-rev1-fbx-2560.png"))
    import_fbx(REV2_FBX)
    records.append(render("corrected rev 2 FBX; smoothing FACE", "arc-closeup-rev2-fbx-2560.png"))
    import_glb(REV2_GLB)
    records.append(render("corrected rev 2 GLB; explicit normals+tangents", "arc-closeup-rev2-glb-2560.png"))
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "renderer": "Blender EEVEE",
        "purpose": "same-camera high-contrast polished-silver normal and highlight continuity comparison",
        "records": records,
        "lighting": {
            "world": {"colorLinear": [0.012, 0.014, 0.018], "strength": 0.22},
            "silver": {"baseColorLinear": [0.97, 0.965, 0.94], "metallic": 1.0, "roughness": 0.055, "emission": 0.0},
            "exposure": -0.25,
            "look": "AgX - Medium High Contrast",
        },
        "pass": all((ROOT / item["path"]).exists() for item in records),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 smoothing renders failed.")


if __name__ == "__main__":
    main()
