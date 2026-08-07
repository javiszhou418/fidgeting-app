#!/usr/bin/env python3
"""Import a Rodin GLB into a separate Blender file and render inspection views."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--renders", required=True)
    return parser.parse_args(argv)


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners))),
        Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners))),
    )


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_area(name: str, location: tuple[float, float, float], energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    look_at(light, Vector((0.0, 0.0, 0.0)))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).resolve()
    blend_path = Path(args.blend).resolve()
    render_dir = Path(args.renders).resolve()
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(input_path))

    imported = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not imported:
        raise RuntimeError("Rodin GLB contained no mesh objects")

    root = bpy.data.objects.new("DragonScaleEDC_Rodin_Root", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in imported:
        if obj.parent is None:
            world = obj.matrix_world.copy()
            obj.parent = root
            obj.matrix_world = world

    lower, upper = world_bounds(imported)
    dimensions = upper - lower
    thinnest_axis = min(range(3), key=lambda index: dimensions[index])
    if thinnest_axis == 0:
        root.rotation_euler[1] = math.radians(90.0)
    elif thinnest_axis == 1:
        root.rotation_euler[0] = math.radians(-90.0)
    bpy.context.view_layer.update()

    lower, upper = world_bounds(imported)
    root.location -= (lower + upper) * 0.5
    bpy.context.view_layer.update()
    lower, upper = world_bounds(imported)
    dimensions = upper - lower
    root.scale *= 0.065 / max(dimensions.x, dimensions.y)
    bpy.context.view_layer.update()
    lower, upper = world_bounds(imported)
    root.location.z -= lower.z
    bpy.context.view_layer.update()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -1.5
    scene.world.color = (0.008, 0.008, 0.008)

    inspection = bpy.data.materials.new("Inspection_Silver")
    inspection.use_nodes = True
    principled = inspection.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.22, 0.25, 0.29, 1.0)
    principled.inputs["Metallic"].default_value = 0.72
    principled.inputs["Roughness"].default_value = 0.34
    bpy.context.view_layer.material_override = inspection

    lower, upper = world_bounds(imported)
    center = (lower + upper) * 0.5
    width = max(upper.x - lower.x, upper.y - lower.y)
    height = upper.z - lower.z

    add_area("Key", (0.08, -0.10, 0.13), 22.0, 0.09)
    add_area("Fill", (-0.10, -0.03, 0.08), 10.0, 0.08)
    add_area("Rim", (0.02, 0.11, 0.10), 16.0, 0.07)

    camera_data = bpy.data.cameras.new("Inspection_Camera")
    camera = bpy.data.objects.new("Inspection_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"

    views = {
        "top": (Vector((0.0, 0.0, max(0.12, height * 8.0))), center, width * 1.18),
        "side": (Vector((0.0, -0.12, center.z)), center, max(width * 1.15, height * 5.0)),
        "iso": (Vector((0.09, -0.10, 0.09)), center, width * 1.65),
        "bottom_iso": (Vector((-0.08, 0.10, -0.055)), center, width * 1.65),
    }
    for name, (location, target, ortho_scale) in views.items():
        camera.location = location
        camera.data.ortho_scale = ortho_scale
        look_at(camera, target)
        scene.render.filepath = str(render_dir / f"DragonScaleEDC_Rodin_{name}.png")
        bpy.ops.render.render(write_still=True)

    bpy.context.view_layer.material_override = None
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    print(
        {
            "blend": str(blend_path),
            "mesh_objects": [obj.name for obj in imported],
            "bounds_mm": [round(value * 1000.0, 3) for value in (upper - lower)],
            "renders": str(render_dir),
        }
    )


if __name__ == "__main__":
    main()
