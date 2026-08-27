"""Render neutral FBX, GLB, and collision round-trip review images."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
FBX = HERE / "magnetic-fan-card.fbx"
GLB = HERE / "magnetic-fan-card.glb"
COLLISION_FBX = HERE / "magnetic-fan-card-collision.fbx"
ROUNDTRIP = HERE / "export-roundtrip-report.json"


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    return (minimum + maximum) / 2, maximum - minimum


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y").to_euler()


def configure_scene(
    objects: list[bpy.types.Object],
    output: Path,
    collision: bool,
) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(output)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.show_specular_highlight = True
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.025, 0.028, 0.032)

    for obj in objects:
        if obj.type != "MESH":
            continue
        obj.color = (
            (0.78, 0.15, 0.06, 1.0)
            if collision
            else (0.60, 0.57, 0.51, 1.0)
        )

    center, extent = bounds(objects)
    span = max(extent.x, extent.y)
    camera_data = bpy.data.cameras.new("CAM_ExportReview")
    camera = bpy.data.objects.new("CAM_ExportReview", camera_data)
    scene.collection.objects.link(camera)
    camera_data.lens = 55.0
    camera.location = center + Vector((
        span * 1.20,
        -span * 1.50,
        span * 1.10,
    ))
    aim(camera, center)
    scene.camera = camera
    bpy.ops.render.render(write_still=True)


def render_import(
    path: Path,
    output: Path,
    format_name: str,
    collision: bool = False,
) -> None:
    reset()
    if format_name == "GLB":
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path))
    objects = list(bpy.context.scene.objects)
    configure_scene(objects, output, collision)


def main() -> None:
    fbx_image = HERE / "fbx-roundtrip-neutral.png"
    glb_image = HERE / "glb-roundtrip-neutral.png"
    collision_image = HERE / "collision-roundtrip.png"
    render_import(FBX, fbx_image, "FBX")
    render_import(GLB, glb_image, "GLB")
    render_import(COLLISION_FBX, collision_image, "FBX", True)


if __name__ == "__main__":
    main()
