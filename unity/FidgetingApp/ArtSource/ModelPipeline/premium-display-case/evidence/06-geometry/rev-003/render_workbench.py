#!/usr/bin/env python3
"""Render the approved whole-case geometry in Blender Workbench."""

from __future__ import annotations

from pathlib import Path

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE = OUTPUT / "premium-display-case-geometry-r003.blend"
TARGET = OUTPUT / "geometry-workbench.png"
SUBJECT_NAMES = {
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
}


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    return (
        Vector(tuple(min(point[index] for point in corners) for index in range(3))),
        Vector(tuple(max(point[index] for point in corners) for index in range(3))),
    )


def orient_camera(camera: bpy.types.Object, target: Vector) -> None:
    backward = (camera.location - target).normalized()
    world_up = Vector((0, 1, 0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in SUBJECT_NAMES
    minimum, maximum = world_bounds(subjects)
    center = (minimum + maximum) * 0.5
    radius = max((maximum - minimum).length * 0.5, 0.001)
    camera_data = bpy.data.cameras.new("Gate06Rev3WorkbenchCamera")
    camera = bpy.data.objects.new("Gate06Rev3WorkbenchCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((1.25, 0.8, 1.6)).normalized() * radius * 3.4
    orient_camera(camera, center)
    camera.data.type = "PERSP"
    camera.data.lens = 58
    camera.data.clip_end = max(1000.0, radius * 10.0)
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.72, 0.74, 0.78)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.curvature_ridge_factor = 1.4
    scene.display.shading.curvature_valley_factor = 1.2
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.025, 0.03, 0.04)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(TARGET)
    bpy.ops.render.render(write_still=True)
    print(str(TARGET))


if __name__ == "__main__":
    main()
