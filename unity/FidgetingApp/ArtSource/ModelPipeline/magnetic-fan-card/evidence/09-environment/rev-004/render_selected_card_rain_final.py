"""Render the selected Card Rain direction at 2× production-preview quality."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = HERE / "fan-card-full-scene-redesign.blend"
OUTPUT_BLEND = HERE / "fan-card-card-rain-final.blend"
OUTPUT_IMAGE = HERE / "card-rain-final-raw-2x.png"


def object_world_center(obj: bpy.types.Object) -> Vector:
    if obj.type == "MESH" and obj.bound_box:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        return sum(points, Vector()) / len(points)
    return obj.matrix_world.translation


def configure_selected_direction(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
) -> int:
    product_points = []
    for obj in bpy.data.collections["COL_Product_Locked"].objects:
        if obj.type == "MESH":
            product_points.extend(
                obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    product_center = sum(product_points, Vector()) / len(product_points)
    product_depth = world_to_camera_view(
        scene, camera, product_center).z
    culled = 0
    for obj in scene.objects:
        if obj.name.startswith(("PROP_A_", "FX_A_", "PROP_C_", "FX_C_")):
            obj.hide_render = True
        elif obj.name.startswith(("PROP_B_", "FX_B_")):
            obj.hide_render = False
            obj.visible_shadow = False
            if obj.name.startswith("FX_B_"):
                projected = world_to_camera_view(
                    scene, camera, object_world_center(obj))
                if (
                    0.25 < projected.x < 0.82
                    and 0.13 < projected.y < 0.77
                    and projected.z < product_depth
                ):
                    obj.hide_render = True
                    culled += 1
    return culled


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
    camera = bpy.data.objects["CAM_Hero_Selected"]
    scene.camera = camera
    culled = configure_selected_direction(scene, camera)
    bpy.data.objects["LGT_STAGE_GoldRim"].data.energy = 3.4
    bpy.data.objects["LGT_STAGE_TableGold"].data.energy = 0.56

    scene.render.resolution_x = 2358
    scene.render.resolution_y = 1308
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.60
    scene.render.filepath = str(OUTPUT_IMAGE)
    renderer = configure_metal(scene)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    (HERE / "card-rain-final-render-report.json").write_text(
        json.dumps({
            "selectedDirection": "B-card-rain",
            "resolution": [2358, 1308],
            "samples": 256,
            "adaptiveThreshold": 0.015,
            "denoising": True,
            "exposure": -0.60,
            "screenSpaceParticles": 0,
            "culledProductOverlapFxObjects": culled,
            "renderer": renderer,
            "productGeometryModified": False,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
