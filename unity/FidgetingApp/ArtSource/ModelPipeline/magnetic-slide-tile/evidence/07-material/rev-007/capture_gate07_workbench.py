#!/usr/bin/env python3
"""Capture a real Blender Workbench screenshot for Gate 07 rev 7."""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
scene = bpy.context.scene
scene.camera = bpy.data.objects["M07R7_MaterialBoardCamera"]
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.studio_light = "rim.sl"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.display.shading.curvature_ridge_factor = 1.6
scene.display.shading.curvature_valley_factor = 1.2
scene.render.resolution_x = 1400
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "gate07-workbench.png")
bpy.ops.render.render(write_still=True)
