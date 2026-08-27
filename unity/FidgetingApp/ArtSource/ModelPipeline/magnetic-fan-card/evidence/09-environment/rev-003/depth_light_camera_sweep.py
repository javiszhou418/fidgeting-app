"""Rebuild true depth layers and render a 32° / 27° / 22° camera sweep."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REV2 = HERE.parent / "rev-002"
SOURCE_BLEND = REV2 / "fan-card-electronic-high-roller-C2-final.blend"
HELPER_SCRIPT = REV2 / "electronic_high_roller_styleframes.py"
PARAMETER_SCRIPT = (
    HERE.parents[1] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT_BLEND = HERE / "fan-card-depth-light-camera-sweep.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


helper = load_module("fan_card_high_roller_helper", HELPER_SCRIPT)
source = load_module("fan_card_depth_parameter_source", PARAMETER_SCRIPT)


def arch_points(
    center_x: float,
    y: float,
    width: float,
    height: float,
    z_base: float,
) -> list[tuple[float, float, float]]:
    radius = width * 0.20
    left = center_x - width * 0.5
    right = center_x + width * 0.5
    top = z_base + height
    points = [(left, y, z_base), (left, y, top - radius)]
    for index in range(9):
        angle = math.pi - index * math.pi / 8
        x = center_x + math.cos(angle) * (width * 0.5)
        z = top - radius + math.sin(angle) * radius
        points.append((x, y, z))
    points.append((right, y, z_base))
    return points


def glass_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_FX_ChampagneDroplet")
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.24, 0.065, 0.008, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.10
    if "Transmission Weight" in shader.inputs:
        shader.inputs["Transmission Weight"].default_value = 0.92
    shader.inputs["IOR"].default_value = 1.46
    return material


def create_local_volume(target: bpy.types.Collection) -> bpy.types.Object:
    material = helper.volume_material()
    volume = next(
        node for node in material.node_tree.nodes
        if node.bl_idname == "ShaderNodeVolumePrincipled")
    volume.inputs["Density"].default_value = 0.008
    volume.inputs["Anisotropy"].default_value = 0.68
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.object
    obj.name = "FX_Depth_LocalGoldVolume"
    obj.dimensions = (0.50, 0.31, 0.27)
    obj.location = (0.015, 0.075, 0.125)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    helper.move_to(obj, target)
    return obj


def set_camera(
    camera: bpy.types.Object,
    focus: bpy.types.Object,
    center: Vector,
    half_extent: float,
    elevation: float,
) -> None:
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, elevation, half_extent)
    source.aim(camera, center + Vector((0.0, 0.012, 0.018)))
    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = focus
    camera.data.dof.aperture_fstop = 4.5
    camera.data.dof.aperture_blades = 8


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    collections = {
        "product": bpy.data.collections["COL_Product_Locked"],
        "geo": bpy.data.collections["COL_Modular_Geo"],
        "dress": bpy.data.collections["COL_SetDressing"],
        "lights": bpy.data.collections["COL_Lights"],
        "cameras": bpy.data.collections["COL_Cameras"],
        "fx": bpy.data.collections["COL_FX"],
    }

    for obj in scene.objects:
        if obj.name.startswith((
            "ENV_Casino_BackWall",
            "ENV_Casino_BrassColumn",
            "ENV_Casino_LightBand",
            "ENV_Casino_FloatingLightBar",
            "ENV_Bokeh_",
            "FX_GoldDust_",
            "FX_HeroSpark_",
            "FX_DiagonalSpark_",
            "FX_SuitShard_",
            "FX_LocalGoldAtmosphere",
        )):
            obj.hide_render = True
            obj.hide_viewport = True

    product_objects = [
        obj for obj in collections["product"].objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008

    brass = bpy.data.materials["MAT_ENV_Brass"]
    dark = bpy.data.materials["MAT_ENV_CasinoWall"]
    gold_glow = helper.emission(
        "MAT_FX_DepthGoldGlow", (1.0, 0.30, 0.035, 1.0), 5.5)
    gold_hot = helper.emission(
        "MAT_FX_DepthGoldHot", (1.0, 0.52, 0.11, 1.0), 14.0)
    champagne = glass_material()

    wall = helper.add_cube(
        "ENV_Depth_CasinoWall",
        (center.x - 0.035, center.y + 0.205, 0.13),
        (0.78, 0.024, 0.34),
        dark,
        collections["geo"],
    )
    wall.hide_render = False
    arches = []
    for index, (y, width, height) in enumerate((
            (center.y + 0.058, 0.32, 0.18),
            (center.y + 0.115, 0.40, 0.23),
            (center.y + 0.172, 0.50, 0.29))):
        points = arch_points(
            center.x - 0.025, y, width, height, -0.008)
        outer = helper.polyline(
            f"ENV_Depth_ArchBrass_{index:02d}",
            points, 0.0032, brass, collections["geo"])
        inner = helper.polyline(
            f"ENV_Depth_ArchLight_{index:02d}",
            points, 0.00125, gold_glow, collections["geo"])
        arches.extend((outer, inner))
    for index, z in enumerate((0.035, 0.085, 0.14, 0.205)):
        helper.add_cube(
            f"ENV_Depth_BackLightBand_{index:02d}",
            (center.x - 0.03, center.y + 0.190, z),
            (0.70, 0.005, 0.006),
            gold_glow,
            collections["geo"],
        )

    foreground_right = bpy.data.objects["PROP_Chip_Foreground_Right"]
    foreground_right.location = (
        center.x + 0.190, center.y - 0.100, 0.025)
    foreground_right.scale = (0.55, 0.55, 0.55)
    foreground_left = bpy.data.objects["PROP_Chip_Foreground_Left"]
    foreground_left.location = (
        center.x - 0.190, center.y - 0.100, 0.022)
    foreground_left.scale = (0.50, 0.50, 0.50)
    dark_chip = bpy.data.materials["MAT_ENV_BlackLacquer"]
    for body_name in (
            "PROP_Chip_Foreground_Right_Body",
            "PROP_Chip_Foreground_Left_Body"):
        body = bpy.data.objects[body_name]
        body.data.materials.clear()
        body.data.materials.append(dark_chip)
    for prefix in ("PROP_Chip_Foreground_Right", "PROP_Chip_Foreground_Left"):
        for obj in scene.objects:
            if obj.name.startswith(prefix):
                obj.hide_render = False
                obj.hide_viewport = False

    card_left = bpy.data.objects["PROP_Card_Background_Left"]
    card_left.location = (
        center.x - 0.155, center.y + 0.040, 0.078)
    card_left.scale = (1.30, 1.30, 1.30)
    card_right = bpy.data.objects["PROP_Card_Background_Right"]
    card_right.location = (
        center.x + 0.175, center.y + 0.080, 0.110)
    card_right.scale = (1.30, 1.30, 1.30)
    for prefix in ("PROP_Card_Background_Left", "PROP_Card_Background_Right"):
        for obj in scene.objects:
            if obj.name.startswith(prefix):
                obj.hide_render = False
                obj.hide_viewport = False
    helper.create_dark_card(
        "PROP_Card_Depth_Center",
        Vector((center.x - 0.015, center.y + 0.105, 0.145)),
        (math.radians(18), math.radians(-16), math.radians(18)),
        bpy.data.materials["MAT_PROP_BlackCard"],
        brass,
        collections["dress"])
    helper.create_chip(
        "PROP_Chip_Depth_Background",
        Vector((center.x + 0.225, center.y + 0.120, 0.145)),
        0.035,
        (math.radians(-12), math.radians(-28), math.radians(26)),
        bpy.data.materials["MAT_ENV_BlackLacquer"],
        brass,
        collections["dress"])

    rng = random.Random(2026082503)
    for index in range(42):
        x = center.x + rng.uniform(-0.28, 0.27)
        y = center.y + rng.uniform(0.105, 0.195)
        z = rng.uniform(0.045, 0.255)
        radius = rng.uniform(0.0025, 0.0085)
        helper.add_uv_sphere(
            f"FX_Depth_BackBokeh_{index:02d}",
            (x, y, z), radius,
            gold_glow if index % 5 else gold_hot,
            collections["fx"], 12)

    for index in range(64):
        angle = rng.uniform(-0.55, 2.45)
        radius_from_hero = rng.uniform(0.085, 0.24)
        x = center.x + math.cos(angle) * radius_from_hero
        y = center.y + math.sin(angle) * radius_from_hero * 0.58
        z = rng.uniform(0.018, 0.105)
        size = rng.uniform(0.0012, 0.0032)
        if abs(x - center.x) < 0.10 and abs(y - center.y) < 0.075:
            continue
        helper.add_uv_sphere(
            f"FX_Depth_MidSpark_{index:02d}",
            (x, y, z), size, gold_hot, collections["fx"], 8)
    for index in range(28):
        t = index / 27
        x = center.x - 0.225 + t * 0.37
        y = center.y + 0.035 + t * 0.105
        z = 0.045 + math.sin(t * math.pi) * 0.095
        helper.add_uv_sphere(
            f"FX_Depth_DiagonalSpark_{index:02d}",
            (x, y, z),
            0.00125 + (index % 5) * 0.00022,
            gold_hot, collections["fx"], 10)
    for index in range(24):
        x = center.x + rng.uniform(-0.25, 0.24)
        y = center.y + rng.uniform(0.045, 0.155)
        z = rng.uniform(0.035, 0.185)
        size = rng.uniform(0.0024, 0.0060)
        vertices = [
            (x - size, y, z),
            (x, y + size * 1.5, z),
            (x + size, y, z),
            (x, y - size * 1.5, z),
        ]
        mesh = bpy.data.meshes.new(f"FX_Depth_SuitShard_{index:02d}_Mesh")
        mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
        shard = bpy.data.objects.new(f"FX_Depth_SuitShard_{index:02d}", mesh)
        collections["fx"].objects.link(shard)
        shard.data.materials.append(gold_glow)
        shard.rotation_euler = (
            rng.uniform(-0.5, 0.5),
            rng.uniform(-0.5, 0.5),
            rng.uniform(-math.pi, math.pi),
        )

    foreground_positions = (
        (-0.245, -0.110, 0.150, 0.009),
        (-0.205, -0.080, 0.095, 0.006),
        (0.225, -0.105, 0.135, 0.010),
        (0.255, -0.055, 0.090, 0.007),
        (-0.090, -0.145, 0.175, 0.006),
        (0.105, -0.135, 0.155, 0.008),
    )
    for index, (x, y, z, size) in enumerate(foreground_positions):
        helper.add_uv_sphere(
            f"FX_Depth_ForegroundDroplet_{index:02d}",
            (center.x + x, center.y + y, z),
            size, champagne, collections["fx"], 16)

    volume = create_local_volume(collections["fx"])
    volume.location.x = center.x - 0.015
    volume.location.y = center.y + 0.070

    back_spot = helper.add_light(
        "LGT_Depth_VolumeGold",
        "SPOT",
        center + Vector((-0.17, 0.19, 0.24)),
        7.5,
        source.kelvin(2700),
        center + Vector((0.0, 0.03, 0.075)),
        collections["lights"],
    )
    back_spot.data.spot_size = math.radians(24)
    back_spot.data.spot_blend = 0.42
    bpy.data.objects["LGT_Key_Broad"].data.energy = 3.2
    bpy.data.objects["LGT_Fill_Weak"].data.energy = 0.30
    bpy.data.objects["LGT_Rim_Gold"].data.energy = 1.35
    bpy.data.objects["LGT_Table_Amber"].data.energy = 0.16

    camera = bpy.data.objects["CAM_Hero_Selected"]
    focus = bpy.data.objects.get("EMPTY_CamTarget_HighRoller")
    if focus is None:
        focus = bpy.data.objects.new("EMPTY_CamTarget_HighRoller", None)
        collections["cameras"].objects.link(focus)
    focus.location = center + Vector((0.0, 0.0, 0.006))
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.45
    renderer = helper.configure_cycles(scene)
    scene.cycles.samples = 96
    scene.cycles.adaptive_threshold = 0.025

    outputs = {}
    for elevation in (32.0, 27.0, 22.0):
        set_camera(camera, focus, center, half_extent, elevation)
        path = HERE / f"depth-camera-{int(elevation):02d}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[str(int(elevation))] = path.name

    set_camera(camera, focus, center, half_extent, 27.0)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    (HERE / "depth-light-camera-report.json").write_text(
        json.dumps({
            "productGeometryModified": False,
            "lensMm": 80,
            "elevationSweepDegrees": [32, 27, 22],
            "fStop": 4.5,
            "depthBands": {
                "foreground": "two near-camera chips and six transmissive droplets",
                "midground": "approved Fan Card, table, and 64 bounded sparks",
                "background": "three arch planes, 42 bokeh lights, two floating dark cards",
            },
            "volumetric": {
                "localDensity": 0.008,
                "anisotropy": 0.68,
                "spotEnergy": 7.5,
            },
            "renderer": renderer,
            "samples": 96,
            "outputs": outputs,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
