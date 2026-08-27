"""Render the selected 80 mm / 32° true-depth scene at 2× quality."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = HERE / "fan-card-depth-light-camera-sweep.blend"
PARAMETER_SCRIPT = (
    HERE.parents[1] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT_BLEND = HERE / "fan-card-depth32-final.blend"
OUTPUT_IMAGE = HERE / "depth32-final-raw-2x.png"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_depth32_parameter_source", PARAMETER_SCRIPT)


def camera_ray_point(
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    u: float,
    v: float,
    distance: float,
) -> Vector:
    frame = camera.data.view_frame(scene=scene)
    min_x = min(point.x for point in frame)
    max_x = max(point.x for point in frame)
    min_y = min(point.y for point in frame)
    max_y = max(point.y for point in frame)
    z = sum(point.z for point in frame) / len(frame)
    local_direction = Vector((
        min_x + (max_x - min_x) * u,
        min_y + (max_y - min_y) * v,
        z,
    )).normalized()
    world_direction = camera.matrix_world.to_quaternion() @ local_direction
    return camera.location + world_direction * distance


def place_depth_props(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
) -> None:
    placements = {
        "PROP_Card_Background_Left": (0.40, 0.84, 0.60, 1.10),
        "PROP_Card_Depth_Center": (0.66, 0.89, 0.64, 0.95),
        "PROP_Chip_Depth_Background": (0.91, 0.80, 0.66, 0.82),
        "PROP_Chip_Foreground_Left": (-0.08, 0.12, 0.44, 0.60),
        "PROP_Chip_Foreground_Right": (1.08, 0.10, 0.44, 0.55),
    }
    bpy.data.objects["PROP_Card_Background_Right"].hide_render = True
    for name, (u, v, distance, scale) in placements.items():
        obj = bpy.data.objects[name]
        obj.location = camera_ray_point(camera, scene, u, v, distance)
        obj.scale = (scale, scale, scale)
        obj.hide_render = False


def add_final_depth_dust(center: Vector) -> int:
    rng = random.Random(2026082532)
    target = bpy.data.collections["COL_FX"]
    material = bpy.data.materials["MAT_FX_DepthGoldHot"]
    count = 0
    for index in range(58):
        x = center.x + rng.uniform(-0.26, -0.04)
        y = center.y + rng.uniform(0.018, 0.145)
        z = rng.uniform(0.025, 0.165)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=rng.uniform(0.00055, 0.00165),
            location=(x, y, z),
        )
        particle = bpy.context.object
        particle.name = f"FX_FinalDepthDust_{index:02d}"
        particle.data.materials.append(material)
        if target not in particle.users_collection:
            target.objects.link(particle)
        for current in list(particle.users_collection):
            if current != target:
                current.objects.unlink(particle)
        count += 1
    for index in range(12):
        x = center.x + rng.uniform(-0.245, -0.045)
        y = center.y + rng.uniform(0.040, 0.145)
        z = rng.uniform(0.040, 0.170)
        size = rng.uniform(0.0018, 0.0040)
        vertices = [
            (x - size, y, z),
            (x, y + size * 1.55, z),
            (x + size, y, z),
            (x, y - size * 1.55, z),
        ]
        mesh = bpy.data.meshes.new(f"FX_FinalDepthShard_{index:02d}_Mesh")
        mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
        shard = bpy.data.objects.new(f"FX_FinalDepthShard_{index:02d}", mesh)
        target.objects.link(shard)
        shard.data.materials.append(material)
        shard.rotation_euler = (
            rng.uniform(-0.45, 0.45),
            rng.uniform(-0.45, 0.45),
            rng.uniform(-math.pi, math.pi),
        )
        count += 1
    return count


def cull_fx_over_product(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
) -> int:
    prefixes = (
        "ENV_Bokeh_",
        "FX_Depth_BackBokeh_",
        "FX_Depth_MidSpark_",
        "FX_Depth_DiagonalSpark_",
        "FX_Depth_ForegroundDroplet_",
        "FX_FinalDepthDust_",
        "FX_FinalDepthShard_",
    )
    count = 0
    for obj in scene.objects:
        if not obj.name.startswith(prefixes):
            continue
        projected = world_to_camera_view(
            scene, camera, obj.matrix_world.translation)
        if 0.30 < projected.x < 0.85 and 0.12 < projected.y < 0.72:
            obj.hide_render = True
            count += 1
    return count


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
    product_collection = bpy.data.collections["COL_Product_Locked"]
    product_objects = [
        obj for obj in product_collection.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    for obj in scene.objects:
        if obj.name.startswith("FX_Depth_SuitShard_"):
            obj.hide_render = True
    bpy.data.objects["FX_Depth_ForegroundDroplet_05"].hide_render = True
    final_depth_fx_count = add_final_depth_dust(center)

    camera = bpy.data.objects["CAM_Hero_Selected"]
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center + Vector((0.0, 0.012, 0.018)))
    camera.data.dof.aperture_fstop = 4.2
    scene.camera = camera
    place_depth_props(scene, camera)
    culled_product_overlap_count = cull_fx_over_product(scene, camera)

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
    (HERE / "depth32-final-render-report.json").write_text(
        json.dumps({
            "selectedCamera": {"lensMm": 80, "elevationDegrees": 32},
            "resolution": [2358, 1308],
            "samples": 256,
            "adaptiveThreshold": 0.015,
            "denoising": True,
            "exposure": -0.60,
            "fStop": 4.2,
            "renderer": renderer,
            "screenSpaceParticles": 0,
            "additionalFinal3dFxObjects": final_depth_fx_count,
            "culledProductOverlapFxObjects": culled_product_overlap_count,
            "productGeometryModified": False,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
