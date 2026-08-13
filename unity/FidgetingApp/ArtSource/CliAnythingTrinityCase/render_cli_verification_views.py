"""Render verification views from the cli-anything-blender prototype blend."""

from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT_DIR = Path(
    "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/Artifacts/"
    "CliAnythingTrinityCasePreview"
)


def point_at(scene_object, target):
    direction = Vector(target) - scene_object.location
    scene_object.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_view(filename, location, target, lens):
    scene = bpy.context.scene
    camera = bpy.data.objects["HeroCamera"]
    camera.location = location
    camera.data.lens = lens
    point_at(camera, target)
    scene.camera = camera
    scene.render.resolution_x = 720
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 20
    scene.render.filepath = str(OUTPUT_DIR / filename)
    bpy.ops.render.render(write_still=True)


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
render_view("front-verification.png", (0.0, -0.98, 0.025), (0.0, 0.01, 0.015), 62.0)
render_view("left-oblique-verification.png", (-0.46, -0.94, 0.34), (0.0, 0.015, 0.012), 56.0)
