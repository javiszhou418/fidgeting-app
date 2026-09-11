#!/usr/bin/env python3
"""Capture legal endpoint silver response at the approved low exposure."""

import math
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
MAX_TRAVEL = 18.076433121019107
scene = bpy.context.scene
scene.view_settings.exposure = -2.0
moving = bpy.data.objects["MovingTop"]
moving.location = (0.0, -9.0, 5.875)
moving.rotation_euler = (0.0, 0.0, math.radians(12.0))
bpy.data.objects["RotatingCarrier"].rotation_euler = (0.0, 0.0, math.radians(12.0))
bpy.data.objects["TopLocalSlide"].location = (0.0, 9.0 - MAX_TRAVEL, 0.0)
bpy.context.view_layer.update()
scene.camera = bpy.data.objects["M07R12_Side"]
scene.render.resolution_x = 1400
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.filepath = str(HERE / "side-reflection.png")
bpy.ops.render.render(write_still=True)
print("side-reflection.png rendered at legal max-open 12° and EV -2.0")
