"""Lift the locked Card Rain product and add denser surreal 3D FX."""

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
REV4 = HERE.parent / "rev-004"
SOURCE_BLEND = REV4 / "fan-card-card-rain-final.blend"
STAGE_SCRIPT = REV4 / "full_scene_redesign.py"
OUTPUT_BLEND = HERE / "fan-card-surreal-levitation.blend"
OUTPUT_IMAGE = HERE / "surreal-levitation-preview.png"
HOVER_METRES = 0.014


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


stage = load_module("fan_card_surreal_stage_source", STAGE_SCRIPT)
helper = stage.helper


def product_objects() -> list[bpy.types.Object]:
    collection = bpy.data.collections["COL_Product_Locked"]
    return [
        obj for obj in collection.all_objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]


def world_center(obj: bpy.types.Object) -> Vector:
    if obj.type == "MESH" and obj.bound_box:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        return sum(points, Vector()) / len(points)
    return obj.matrix_world.translation


def projected_product_rect(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    objects: list[bpy.types.Object],
) -> tuple[float, float, float, float, float]:
    projected = [
        world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner))
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    product_center = sum(
        (world_center(obj) for obj in objects if obj.type == "MESH"),
        Vector(),
    ) / len([obj for obj in objects if obj.type == "MESH"])
    depth = world_to_camera_view(scene, camera, product_center).z
    return (
        max(0.0, min(point.x for point in projected) - 0.01),
        min(1.0, max(point.x for point in projected) + 0.01),
        max(0.0, min(point.y for point in projected) - 0.01),
        min(1.0, max(point.y for point in projected) + 0.01),
        depth,
    )


def add_particle(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    target: bpy.types.Collection,
    material: bpy.types.Material,
    u: float,
    v: float,
    distance: float,
    radius: float,
) -> bpy.types.Object:
    obj = helper.add_uv_sphere(
        name,
        stage.camera_ray_point(camera, scene, u, v, distance),
        radius,
        material,
        target,
        8,
    )
    obj.visible_shadow = False
    return obj


def add_screen_diamond(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    target: bpy.types.Collection,
    material: bpy.types.Material,
    u: float,
    v: float,
    distance: float,
    size: float,
) -> bpy.types.Object:
    center = stage.camera_ray_point(camera, scene, u, v, distance)
    right = camera.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    up = camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(
        [
            center - right * size,
            center + up * size * 1.7,
            center + right * size,
            center - up * size * 1.7,
        ],
        [],
        [(0, 1, 2, 3)],
    )
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.data.materials.append(material)
    obj.visible_shadow = False
    return obj


def create_dense_depth_fx(
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    target: bpy.types.Collection,
    gold: bpy.types.Material,
    hot: bpy.types.Material,
) -> list[bpy.types.Object]:
    rng = random.Random(2026082505)
    objects = []
    bands = (
        ("Back", 125, (0.04, 0.97), (0.37, 0.98), (0.64, 0.76), (0.0012, 0.0042)),
        ("Mid", 95, (0.03, 0.97), (0.18, 0.97), (0.50, 0.63), (0.0007, 0.0024)),
        ("Front", 42, (-0.05, 1.05), (0.05, 0.91), (0.37, 0.46), (0.0016, 0.0048)),
    )
    for band, count, u_range, v_range, d_range, r_range in bands:
        for index in range(count):
            u = rng.uniform(*u_range)
            v = rng.uniform(*v_range)
            if band == "Front" and 0.12 < u < 0.90 and 0.18 < v < 0.80:
                u = rng.choice((rng.uniform(-0.08, 0.12), rng.uniform(0.90, 1.08)))
            distance = rng.uniform(*d_range)
            radius = rng.uniform(*r_range)
            material = hot if index % 8 == 0 else gold
            if index % 7 == 0:
                objects.append(add_screen_diamond(
                    f"FX_Surreal_{band}_Diamond_{index:03d}",
                    camera, scene, target, material,
                    u, v, distance, radius * 1.4))
            else:
                objects.append(add_particle(
                    f"FX_Surreal_{band}_Particle_{index:03d}",
                    camera, scene, target, material,
                    u, v, distance, radius))
    return objects


def create_levitation_column(
    center: Vector,
    target: bpy.types.Collection,
    gold: bpy.types.Material,
    hot: bpy.types.Material,
) -> list[bpy.types.Object]:
    rng = random.Random(14000)
    objects = []
    for index in range(72):
        progress = index / 71
        angle = progress * math.tau * 2.4 + rng.uniform(-0.22, 0.22)
        radius = (0.052 - progress * 0.024) * rng.uniform(0.72, 1.02)
        location = center + Vector((
            math.cos(angle) * radius,
            math.sin(angle) * radius * 0.70,
            0.002 + progress * 0.087,
        ))
        obj = helper.add_uv_sphere(
            f"FX_Surreal_Updraft_{index:03d}",
            location,
            rng.uniform(0.00045, 0.00155),
            hot if index % 9 == 0 else gold,
            target,
            8,
        )
        obj.visible_shadow = False
        objects.append(obj)
    for ribbon_index, phase in enumerate((0.0, math.pi)):
        points = []
        for index in range(72):
            progress = index / 71
            angle = phase + progress * math.tau * (
                1.10 if ribbon_index == 0 else 0.72)
            radius = (
                0.066 - progress * 0.014
                if ribbon_index == 0
                else 0.046 - progress * 0.012
            )
            points.append((
                center.x + math.cos(angle) * radius,
                center.y
                    + math.sin(angle) * radius * 0.64
                    + (0.074 if ribbon_index else 0.0),
                (
                    0.004 + progress * 0.007
                    if ribbon_index == 0
                    else 0.026 + progress * 0.054
                ),
            ))
        ribbon = helper.polyline(
            f"FX_Surreal_OpenRibbon_{ribbon_index:02d}",
            points,
            0.00028 if ribbon_index else 0.00040,
            hot if ribbon_index else gold,
            target,
        )
        ribbon.visible_shadow = False
        objects.append(ribbon)
    return objects


def cull_front_fx_over_product(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    objects: list[bpy.types.Object],
    rect: tuple[float, float, float, float, float],
) -> int:
    min_x, max_x, min_y, max_y, product_depth = rect
    culled = 0
    for obj in objects:
        if not obj.name.startswith((
            "FX_Surreal_Front_",
            "FX_Surreal_Mid_",
            "FX_Surreal_Updraft_",
        )):
            continue
        projected = world_to_camera_view(scene, camera, world_center(obj))
        if (
            min_x < projected.x < max_x
            and min_y < projected.y < max_y
            and projected.z < product_depth
        ):
            obj.hide_render = True
            culled += 1
    return culled


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    camera = bpy.data.objects["CAM_Hero_Selected"]
    scene.camera = camera
    product = product_objects()

    for name in (
        "MagneticFanCard_Root",
        "CommonAxis_RecessedMatteSpindle",
        "CommonAxis_BearingCap_Chrome",
    ):
        obj = bpy.data.objects[name]
        obj.location.z += HOVER_METRES
    focus = bpy.data.objects["EMPTY_CamTarget_FullScene"]
    focus.location.z += HOVER_METRES
    bpy.context.view_layer.update()

    fx_collection = bpy.data.collections.new("COL_FX_SurrealLevitation")
    scene.collection.children.link(fx_collection)
    gold = bpy.data.materials["MAT_STAGE_GoldGlow"]
    hot = bpy.data.materials["MAT_STAGE_GoldHot"]
    dense_fx = create_dense_depth_fx(
        camera, scene, fx_collection, gold, hot)

    product_center = sum(
        (world_center(obj) for obj in product if obj.type == "MESH"),
        Vector(),
    ) / len([obj for obj in product if obj.type == "MESH"])
    column_fx = create_levitation_column(
        Vector((product_center.x, product_center.y, 0.0)),
        fx_collection,
        gold,
        hot,
    )
    rect = projected_product_rect(scene, camera, product)
    culled = cull_front_fx_over_product(
        scene, camera, [*dense_fx, *column_fx], rect)

    uplight = helper.add_light(
        "LGT_Surreal_UnderGold",
        "POINT",
        Vector((product_center.x, product_center.y, 0.006)),
        1.35,
        stage.source.kelvin(2450),
        product_center + Vector((0.0, 0.0, 0.025)),
        bpy.data.collections["COL_Lights"],
    )
    uplight.data.shadow_soft_size = 0.045
    volume_light = helper.add_light(
        "LGT_Surreal_VolumeLift",
        "SPOT",
        Vector((product_center.x, product_center.y - 0.025, 0.010)),
        6.0,
        stage.source.kelvin(2850),
        product_center + Vector((0.0, 0.0, 0.085)),
        bpy.data.collections["COL_Lights"],
    )
    volume_light.data.spot_size = math.radians(42)
    volume_light.data.spot_blend = 0.60
    volume = bpy.data.objects["FX_STAGE_LocalVolume"]
    volume.scale.z *= 1.25
    volume.location.z += 0.012
    volume_material = volume.data.materials[0]
    volume_node = next(
        node for node in volume_material.node_tree.nodes
        if node.bl_idname == "ShaderNodeVolumePrincipled")
    volume_node.inputs["Density"].default_value = 0.0075
    volume_node.inputs["Anisotropy"].default_value = 0.78

    bpy.data.objects["LGT_STAGE_GoldRim"].data.energy = 4.3
    bpy.data.objects["LGT_STAGE_TableGold"].data.energy = 0.72
    bpy.data.objects["LGT_Key_Broad"].data.energy = 2.8
    bpy.data.objects["LGT_Fill_Weak"].data.energy = 0.18

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.020
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.58
    scene.render.filepath = str(OUTPUT_IMAGE)
    renderer = helper.configure_cycles(scene)
    scene.cycles.samples = 128
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    (HERE / "surreal-levitation-report.json").write_text(
        json.dumps({
            "source": SOURCE_BLEND.name,
            "hoverMillimetres": HOVER_METRES * 1000,
            "newDepthFxObjects": len(dense_fx),
            "levitationColumnObjects": len(column_fx),
            "culledFrontFxObjects": culled,
            "screenSpaceParticles": 0,
            "productGeometryModified": False,
            "productMaterialModified": False,
            "productHierarchyModified": False,
            "renderer": renderer,
            "samples": 128,
            "resolution": [1179, 654],
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
