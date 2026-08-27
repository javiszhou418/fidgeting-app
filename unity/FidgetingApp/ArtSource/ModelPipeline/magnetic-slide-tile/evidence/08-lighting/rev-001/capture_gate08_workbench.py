#!/usr/bin/env python3
"""Capture the real Gate 08 Blender Workbench view."""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
scene = bpy.context.scene
scene.camera = bpy.data.objects["M08R1_HeroCamera"]
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.studio_light = "rim.sl"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "WORLD"
scene.display.shading.curvature_ridge_factor = 1.6
scene.display.shading.curvature_valley_factor = 1.2
scene.render.resolution_x = 1500
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(ROOT / "gate08-workbench.png")
bpy.ops.render.render(write_still=True)
