#!/usr/bin/env python3
"""Render the upper cap without the overhead key reflecting into the lens."""

from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "magnetic-slide-tile-material-r013.blend"

if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
    raise RuntimeError("Open Gate 07 rev 13 before rendering the top closeup.")

for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.hide_render = obj.name not in {
            "BottomExterior",
            "MovingTopBody",
            "M07R13_NeutralGround",
        }
camera = bpy.data.objects["M07R13_TopView"]
camera.location = (-34, -98, 128)
camera.rotation_euler = (
    Vector((0, -2, 5)) - camera.location
).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 92
scene = bpy.context.scene
scene.camera = camera
scene.view_settings.exposure = -0.7
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERE / "upper-top-closeup.png")
bpy.ops.render.render(write_still=True)
print(scene.render.filepath)
