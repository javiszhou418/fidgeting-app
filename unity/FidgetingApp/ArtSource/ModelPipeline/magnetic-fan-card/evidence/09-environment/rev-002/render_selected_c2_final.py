"""Render the selected C2 environment at production-preview quality."""

from __future__ import annotations

import json
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = HERE / "fan-card-electronic-high-roller-styleframes.blend"
OUTPUT_BLEND = HERE / "fan-card-electronic-high-roller-C2-final.blend"
OUTPUT_IMAGE = HERE / "C2-final-raw-2x.png"


def configure_metal(scene: bpy.types.Scene) -> dict:
    result = {"backend": "Cycles", "device": "CPU fallback"}
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 256
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.015
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "METAL"
        preferences.get_devices()
        enabled = []
        for device in preferences.devices:
            device.use = device.type != "CPU"
            if device.use:
                enabled.append(device.name)
        if enabled:
            scene.cycles.device = "GPU"
            result["device"] = ", ".join(enabled)
    except Exception as error:
        result["deviceError"] = str(error)
    return result


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene.render.resolution_x = 2358
    scene.render.resolution_y = 1308
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.35
    scene.render.filepath = str(OUTPUT_IMAGE)

    bpy.data.objects["LGT_Rim_Gold"].data.energy = 0.85
    bpy.data.objects["LGT_Table_Amber"].data.energy = 0.20
    camera = bpy.data.objects["CAM_Hero_Selected"]
    camera.data.dof.aperture_fstop = 4.8

    renderer = configure_metal(scene)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    (HERE / "C2-final-render-report.json").write_text(
        json.dumps({
            "selectedStyleframe": "C2-electronic-stage",
            "resolution": [2358, 1308],
            "samples": 256,
            "adaptiveThreshold": 0.015,
            "denoising": True,
            "exposure": -0.35,
            "camera": {"lensMm": 80, "fStop": 4.8},
            "renderer": renderer,
            "productGeometryModified": False,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
