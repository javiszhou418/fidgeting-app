#!/usr/bin/env python3
import sys
from pathlib import Path

import bpy


CORE_MESHES = {
    "BottomExterior",
    "FixedAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
}


def main():
    arguments = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    output = Path(arguments[0]) if arguments else Path("blender-silhouette.png")
    output.parent.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    camera = bpy.data.objects.get("M08R2_Hero")
    if camera is None or camera.type != "CAMERA":
        raise RuntimeError("Approved Gate 08 hero camera is missing.")
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (1.0, 1.0, 1.0)
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.show_specular_highlight = False
    scene.render.film_transparent = True
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(output)

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in CORE_MESHES

    bpy.ops.render.render(write_still=True)
    print(output)


if __name__ == "__main__":
    main()
