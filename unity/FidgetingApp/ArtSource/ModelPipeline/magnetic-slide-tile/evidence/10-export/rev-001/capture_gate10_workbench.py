#!/usr/bin/env python3
"""Capture the clean authoritative Gate 10 Blender source in Workbench."""

from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-authoritative.blend"
OUTPUT = ROOT / "gate10-workbench.png"


def point_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = 1400
scene.render.resolution_y = 1050
scene.render.resolution_percentage = 100
scene.render.filepath = str(OUTPUT)
scene.render.image_settings.file_format = "PNG"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.background_type = "WORLD"
if scene.world is None:
    scene.world = bpy.data.worlds.new("Gate10_WorkbenchWorld")
scene.world.color = (0.01, 0.014, 0.021)
for material in bpy.data.materials:
    if "Silver" in material.name:
        material.diffuse_color = (0.72, 0.72, 0.70, 1.0)
    elif "BloodRed" in material.name:
        material.diffuse_color = (0.34, 0.012, 0.024, 1.0)
for obj in bpy.data.objects:
    if obj.get("collision_proxy"):
        obj.hide_render = True
camera_data = bpy.data.cameras.new("Gate10_WorkbenchCameraData")
camera = bpy.data.objects.new("Gate10_WorkbenchCamera", camera_data)
scene.collection.objects.link(camera)
camera.location = (90.0, -130.0, 75.0)
camera_data.lens = 70
point_camera(camera, (0.0, 0.0, 0.0))
scene.camera = camera
bpy.ops.render.render(write_still=True)
print(OUTPUT)
