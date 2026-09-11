#!/usr/bin/env python3
"""Capture the silver response at the viewer's low-exposure setting."""

import math
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
scene = bpy.context.scene
scene.view_settings.exposure = -2.0
bpy.data.objects["RotatingCarrier"].rotation_euler.z = math.radians(12)
bpy.data.objects["MovingTop"].rotation_euler.z = math.radians(12)
bpy.data.objects["TopLocalSlide"].location = (0, -12, 0)
bpy.context.view_layer.update()
scene.camera = bpy.data.objects["M07R11_Side"]
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERE / "side-reflection.png")
bpy.ops.render.render(write_still=True)
print("side-reflection.png rendered at exposure EV -2.0")

