"""Render shared-light beauty views and diagnostics for exact selected geometry."""

from __future__ import annotations

import importlib.util
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
SOURCE_BLEND = (
    SCRIPT.parents[2] / "07-material/rev-004/"
    "fan-card-exact-material-lookdev.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
MATERIAL_SCRIPT = (
    SCRIPT.parents[2] / "07-material/rev-002/material_variants.py"
)
TEXTURES = SCRIPT.parents[2] / "07-material/rev-001/textures"
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-exact-lighting.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep_lighting", PARAMETER_SCRIPT)
materials = load_module("fan_card_material_variants_lighting", MATERIAL_SCRIPT)


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (
        target - obj.location).to_track_quat("-Z", "Y").to_euler()


def set_camera(
    camera: bpy.types.Object,
    center: Vector,
    half_extent: float,
    azimuth: float,
    elevation: float,
    shift_x: float,
    lens: float = 80.0,
) -> None:
    sensor = 0.036
    horizontal_fov = 2 * math.atan(sensor / (2 * (lens / 1000)))
    distance = half_extent / (math.tan(horizontal_fov * 0.5) * 0.62)
    azimuth_radians = math.radians(azimuth)
    elevation_radians = math.radians(elevation)
    camera.location = center + Vector((
        math.cos(elevation_radians) * math.cos(azimuth_radians) * distance,
        math.cos(elevation_radians) * math.sin(azimuth_radians) * distance,
        math.sin(elevation_radians) * distance,
    ))
    camera.data.type = "PERSP"
    camera.data.lens = lens
    camera.data.sensor_width = 36.0
    camera.data.shift_x = shift_x
    aim(camera, center)


def configure_cycles(scene: bpy.types.Scene) -> dict:
    report = {"backend": "Cycles", "device": "CPU fallback"}
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.cycles.preview_samples = 16
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
            report["device"] = ", ".join(enabled)
    except Exception as error:
        report["deviceError"] = str(error)
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    return report


def render(scene: bpy.types.Scene, path: Path) -> None:
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.9,
    emission: bool = False,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    if emission:
        shader = nodes.new("ShaderNodeEmission")
        shader.inputs["Color"].default_value = color
        shader.inputs["Strength"].default_value = 1.0
        links.new(shader.outputs["Emission"], output.inputs["Surface"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Metallic"].default_value = 0.0
        shader.inputs["Roughness"].default_value = roughness
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def normal_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_Pass_Normal")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "SCALE"
    multiply.inputs[3].default_value = 0.5
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Normal"], multiply.inputs[0])
    links.new(multiply.outputs["Vector"], add.inputs[0])
    links.new(add.outputs["Vector"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def roughness_value(obj: bpy.types.Object) -> float:
    name = obj.name
    if "BearingCap" in name:
        return 0.12
    if "GoldTrim" in name or "Track_Grille" in name or "Magnet_" in name:
        return 0.29
    if "WarmSilverFace" in name:
        return 0.53
    if any(token in name for token in ("Rank_", "Spade")):
        return 0.62
    if "Support" in name:
        return 0.84
    return 0.48


def assign(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    support = bpy.data.objects["GEO_Support_Base"]
    supports = {
        "A-dark-walnut": materials.image_support_material(
            "MAT_A_DarkWalnut_Lighting_Exact",
            TEXTURES / "dark_wood/diffuse.jpg",
            TEXTURES / "dark_wood/normal.jpg",
            TEXTURES / "dark_wood/roughness.jpg",
            (2.3, 2.3, 2.3),
            saturation=0.78,
            value=0.62),
        "B-charcoal-hard-case": materials.image_support_material(
            "MAT_B_CharcoalEVA_Lighting_Exact",
            None,
            TEXTURES / "rubberized_track/normal.jpg",
            TEXTURES / "rubberized_track/roughness.jpg",
            (7.0, 7.0, 7.0),
            (0.008, 0.010, 0.013, 1.0)),
        "C-cork-slab": materials.image_support_material(
            "MAT_C_Cork_Lighting_Exact",
            TEXTURES / "cork/Cork001_1K-JPG_Color.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_NormalGL.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_Roughness.jpg",
            (4.0, 4.0, 4.0),
            saturation=0.72,
            value=0.70),
    }
    product_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
        and obj.name != support.name
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    camera = bpy.data.objects["CAM_Hero_Selected"]
    scene.camera = camera
    set_camera(camera, center, half_extent, -35.0, 32.0, -0.22)

    key = bpy.data.objects["LGT_Key_Broad"]
    key.data.energy = 4.0
    key.data.size = 0.35
    key.data.color = source.kelvin(5000)
    key.location = center + Vector((0.16, -0.14, 0.24))
    aim(key, center)
    fill = bpy.data.objects["LGT_Fill_Weak"]
    fill.data.energy = 0.8
    fill.data.size = 0.50
    fill.location = center + Vector((-0.18, -0.05, 0.12))
    aim(fill, center)
    scene.world.node_tree.nodes["Background"].inputs[
        "Strength"].default_value = 0.015

    renderer = configure_cycles(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    hero_outputs = {}
    for variant, material in supports.items():
        support.data.materials[0] = material
        path = OUTPUT / f"hero-{variant}.png"
        render(scene, path)
        hero_outputs[variant] = path.name
    shutil.copy2(
        OUTPUT / "hero-B-charcoal-hard-case.png",
        OUTPUT / "pass-beauty.png")

    support.data.materials[0] = supports["B-charcoal-hard-case"]
    angle_outputs = {}
    for name, azimuth, elevation in (
            ("left-oblique", -55.0, 32.0),
            ("right-oblique", -15.0, 32.0),
            ("low-angle", -35.0, 18.0),
            ("top-oblique", -35.0, 48.0)):
        set_camera(camera, center, half_extent, azimuth, elevation, 0.0)
        path = OUTPUT / f"{name}.png"
        render(scene, path)
        angle_outputs[name] = path.name
    set_camera(camera, center, half_extent, -35.0, 32.0, 0.0)

    scene.render.engine = "BLENDER_EEVEE"
    view_layer = scene.view_layers[0]
    view_layer.material_override = simple_material(
        "MAT_Pass_Clay", (0.38, 0.40, 0.43, 1.0))
    render(scene, OUTPUT / "pass-clay.png")
    view_layer.material_override = normal_material()
    render(scene, OUTPUT / "pass-normal.png")
    view_layer.material_override = None

    for obj in scene.objects:
        if obj.type in {"MESH", "CURVE", "FONT"}:
            value = roughness_value(obj)
            assign(
                obj,
                simple_material(
                    f"MAT_Roughness_{value:.2f}_{obj.name}",
                    (value, value, value, 1.0),
                    emission=True))
    render(scene, OUTPUT / "pass-roughness.png")

    report = {
        "geometry": {
            "cardThicknessMm": 3.5,
            "cornerRadiusMm": 9.5,
            "blackBorderMm": 1.0,
            "goldTrimMm": 0.8,
            "goldTrimBevelMm": 0.38,
        },
        "renderer": renderer,
        "samples": 48,
        "denoising": True,
        "camera": {
            "lensMm": 80,
            "heroElevationDegrees": 32,
            "heroAzimuthDegrees": -35,
        },
        "light": {
            "keyKelvin": 5000,
            "keySizeMm": 350,
            "keyToFill": "5:1",
        },
        "heroVariants": hero_outputs,
        "angleVariants": angle_outputs,
        "diagnostics": ["beauty", "clay", "normal", "roughness"],
        "shippingAssetModified": False,
    }
    (OUTPUT / "exact-lighting-validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
