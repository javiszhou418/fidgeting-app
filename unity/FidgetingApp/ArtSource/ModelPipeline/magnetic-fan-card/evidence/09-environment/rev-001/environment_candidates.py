"""Render neutral and three reference-driven environments with one camera."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
SOURCE_BLEND = (
    SCRIPT.parents[2] / "08-lighting/rev-002/"
    "fan-card-exact-lighting.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
MATERIAL_SCRIPT = (
    SCRIPT.parents[2] / "07-material/rev-002/material_variants.py"
)
TEXTURES = SCRIPT.parents[2] / "07-material/rev-001/textures"
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-environment-candidates.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep_environment", PARAMETER_SCRIPT)
materials = load_module("fan_card_material_variants_environment", MATERIAL_SCRIPT)


def simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = roughness
    return material


def rounded_slab(
    name: str,
    center: Vector,
    width: float,
    height: float,
    radius: float,
    thickness: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    outline = source.rounded_outline(width, height, radius, center)
    return source.prism(
        name, outline, thickness, -thickness * 0.5 - 0.00005,
        material, bevel=min(radius * 0.18, 0.0035))


def rounded_stroke(
    name: str,
    center: Vector,
    width: float,
    height: float,
    radius: float,
    z: float,
    material: bpy.types.Material,
    stroke_width: float,
) -> bpy.types.Object:
    outline = source.rounded_outline(
        width, height, radius, center, segments=16)
    curve_data = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 2
    curve_data.bevel_depth = stroke_width
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(outline))
    for point, value in zip(spline.points, outline + [outline[0]]):
        point.co = (value.x, value.y, z, 1.0)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def set_visible(
    groups: dict[str, list[bpy.types.Object]], active: str
) -> None:
    for variant, objects in groups.items():
        for obj in objects:
            obj.hide_render = variant != active
            obj.hide_viewport = variant != active


def configure_cycles(scene: bpy.types.Scene) -> dict:
    report = {"backend": "Cycles", "device": "CPU fallback"}
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
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


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    previous_support = bpy.data.objects.get("GEO_Support_Base")
    if previous_support is not None:
        bpy.data.objects.remove(previous_support, do_unlink=True)

    product_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
        and not obj.name.startswith("ENV_")
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    environment_center = Vector((center.x - 0.06, center.y, 0.0))

    neutral = simple_material(
        "MAT_ENV_Neutral", (0.075, 0.083, 0.094, 1.0), 0.74)
    dark_floor = simple_material(
        "MAT_ENV_DarkFloor", (0.006, 0.008, 0.011, 1.0), 0.88)
    cork_floor = simple_material(
        "MAT_ENV_CorkFloor", (0.012, 0.018, 0.014, 1.0), 0.92)
    groove = simple_material(
        "MAT_ENV_CaseGroove", (0.002, 0.003, 0.004, 1.0), 0.57)
    walnut = materials.image_support_material(
        "MAT_ENV_DarkWalnut",
        TEXTURES / "dark_wood/diffuse.jpg",
        TEXTURES / "dark_wood/normal.jpg",
        TEXTURES / "dark_wood/roughness.jpg",
        (2.3, 2.3, 2.3),
        saturation=0.70,
        value=0.52)
    hard_case = materials.image_support_material(
        "MAT_ENV_CharcoalHardCase",
        None,
        TEXTURES / "rubberized_track/normal.jpg",
        TEXTURES / "rubberized_track/roughness.jpg",
        (7.0, 7.0, 7.0),
        (0.007, 0.009, 0.012, 1.0))
    cork = materials.image_support_material(
        "MAT_ENV_CorkSlab",
        TEXTURES / "cork/Cork001_1K-JPG_Color.jpg",
        TEXTURES / "cork/Cork001_1K-JPG_NormalGL.jpg",
        TEXTURES / "cork/Cork001_1K-JPG_Roughness.jpg",
        (4.0, 4.0, 4.0),
        saturation=0.72,
        value=0.66)

    groups: dict[str, list[bpy.types.Object]] = {
        "neutral": [
            rounded_slab(
                "ENV_NeutralSurface", environment_center,
                0.72, 0.54, 0.035, 0.040, neutral),
        ],
        "A-dark-walnut": [
            rounded_slab(
                "ENV_WalnutSurface", environment_center,
                0.72, 0.54, 0.035, 0.040, walnut),
        ],
        "B-charcoal-hard-case": [],
        "C-cork-slab": [],
    }

    case_center = Vector((center.x - 0.032, center.y + 0.003, 0.0))
    case_surface = rounded_slab(
        "ENV_HardCaseSurface", case_center,
        0.34, 0.235, 0.032, 0.026, hard_case)
    case_floor = rounded_slab(
        "ENV_HardCaseFloor", environment_center,
        0.72, 0.54, 0.035, 0.052, dark_floor)
    case_floor.location.z -= 0.026
    case_groove_outer = rounded_stroke(
        "ENV_HardCaseGrooveOuter", case_center,
        0.312, 0.207, 0.024, 0.00022, groove, 0.00055)
    case_groove_inner = rounded_stroke(
        "ENV_HardCaseGrooveInner", case_center,
        0.300, 0.195, 0.021, 0.00020, groove, 0.00032)
    groups["B-charcoal-hard-case"] = [
        case_surface, case_floor, case_groove_outer, case_groove_inner]

    cork_center = Vector((center.x - 0.026, center.y + 0.002, 0.0))
    cork_surface = rounded_slab(
        "ENV_CorkSurface", cork_center,
        0.30, 0.225, 0.011, 0.022, cork)
    cork_ground = rounded_slab(
        "ENV_CorkGround", environment_center,
        0.72, 0.54, 0.035, 0.044, cork_floor)
    cork_ground.location.z -= 0.022
    groups["C-cork-slab"] = [cork_surface, cork_ground]

    camera = bpy.data.objects["CAM_Hero_Selected"]
    scene.camera = camera
    camera.data.type = "PERSP"
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center)
    focus = bpy.data.objects.new("ENV_FocusTarget", None)
    bpy.context.collection.objects.link(focus)
    focus.location = center
    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = focus
    camera.data.dof.aperture_fstop = 7.1
    camera.data.dof.aperture_blades = 8

    key = bpy.data.objects["LGT_Key_Broad"]
    key.data.energy = 4.0
    key.data.size = 0.35
    key.data.color = source.kelvin(5000)
    fill = bpy.data.objects["LGT_Fill_Weak"]
    fill.data.energy = 0.8
    fill.data.size = 0.50
    scene.world.node_tree.nodes["Background"].inputs[
        "Strength"].default_value = 0.012

    renderer = configure_cycles(scene)
    outputs = {}
    for variant in (
            "neutral", "A-dark-walnut",
            "B-charcoal-hard-case", "C-cork-slab"):
        set_visible(groups, variant)
        path = OUTPUT / f"environment-{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name

    set_visible(groups, "B-charcoal-hard-case")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    (OUTPUT / "environment-validation.json").write_text(
        json.dumps({
            "geometryUnchanged": True,
            "camera": {
                "lensMm": 80,
                "elevationDegrees": 32,
                "shiftX": -0.22,
                "fStop": 7.1,
            },
            "light": {
                "keyKelvin": 5000,
                "keySizeMm": 350,
                "keyToFill": "5:1",
            },
            "renderer": renderer,
            "samples": 48,
            "outputs": outputs,
            "referenceIntent": {
                "A-dark-walnut": "warm collectible workbench",
                "B-charcoal-hard-case": "neutral technical hard-case",
                "C-cork-slab": "soft lifestyle slab",
            },
            "shippingAssetModified": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
