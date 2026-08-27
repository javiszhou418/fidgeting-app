#!/usr/bin/env python3
"""Capture a real Blender Workbench image of the +21 mm open pose."""

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "magnetic-slide-tile-environment-open-r002.blend"
OUTPUT = ROOT / "gate09-open-workbench.png"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["M09R2_OpenHeroCamera"]
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUTPUT)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.012, 0.016, 0.023)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.show_specular_highlight = True
    bpy.data.materials["M07R7_DaylightNeutralPolishedSilver"].diffuse_color = (0.62, 0.62, 0.62, 1.0)
    bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Upper"].diffuse_color = (0.30, 0.015, 0.025, 1.0)
    bpy.data.materials["M07R7_BloodRedCrystal_WideBorder_Lower"].diffuse_color = (0.30, 0.015, 0.025, 1.0)
    for obj in bpy.data.objects:
        if obj.get("gate08_reflection_card"):
            obj.hide_render = True
    bpy.ops.render.render(write_still=True)
    if not OUTPUT.exists():
        raise RuntimeError("Gate 09 rev 2 Workbench capture was not written.")
    print(OUTPUT)


if __name__ == "__main__":
    main()
