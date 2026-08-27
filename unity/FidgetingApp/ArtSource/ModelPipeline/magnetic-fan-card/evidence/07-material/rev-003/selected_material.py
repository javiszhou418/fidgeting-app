"""Render the user-selected no-dot, medium bead-blast material revision."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import bpy


SCRIPT = Path(__file__).resolve()
SOURCE_BLEND = (
    SCRIPT.parents[1] / "rev-002/fan-card-material-variants.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
MATERIAL_SCRIPT = (
    SCRIPT.parents[1] / "rev-001/material_lookdev.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-selected-material.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep", PARAMETER_SCRIPT)
materials = load_module("fan_card_material_lookdev", MATERIAL_SCRIPT)


def assign(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    for obj in scene.objects:
        if "Follower" in obj.name or "_Dot_" in obj.name:
            obj.hide_render = True
    medium = bpy.data.materials["MAT_WarmSilver_Medium"]
    for obj in scene.objects:
        if "WarmSilverFace" in obj.name:
            assign(obj, medium)
    support = bpy.data.objects["GEO_Support_Base"]
    supports = {
        "A-dark-walnut": materials.image_support_material(
            "MAT_A_DarkWalnut_Selected",
            materials.TEXTURES / "dark_wood/diffuse.jpg",
            materials.TEXTURES / "dark_wood/normal.jpg",
            materials.TEXTURES / "dark_wood/roughness.jpg",
            (2.3, 2.3, 2.3),
            saturation=0.78,
            value=0.62),
        "B-charcoal-hard-case": materials.image_support_material(
            "MAT_B_CharcoalEVA_Selected",
            None,
            materials.TEXTURES / "rubberized_track/normal.jpg",
            materials.TEXTURES / "rubberized_track/roughness.jpg",
            (7.0, 7.0, 7.0),
            (0.008, 0.010, 0.013, 1.0)),
        "C-cork-slab": materials.image_support_material(
            "MAT_C_Cork_Selected",
            materials.TEXTURES / "cork/Cork001_1K-JPG_Color.jpg",
            materials.TEXTURES / "cork/Cork001_1K-JPG_NormalGL.jpg",
            materials.TEXTURES / "cork/Cork001_1K-JPG_Roughness.jpg",
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
    camera.data.type = "PERSP"
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center)
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    outputs = {}
    for variant, material in supports.items():
        support.data.materials[0] = material
        path = OUTPUT / f"selected-{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name
    support.data.materials[0] = supports["B-charcoal-hard-case"]
    camera.data.shift_x = 0.0
    camera.data.lens = 105.0
    camera.location = source.camera_position(
        center, 105.0, 38.0, half_extent * 0.52)
    source.aim(camera, center)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.filepath = str(OUTPUT / "selected-material-closeup.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    (OUTPUT / "selected-material-report.json").write_text(
        json.dumps({
            "decorativeDotsPerFront": 0,
            "followersVisibleOnFront": False,
            "warmSilver": {
                "variant": "medium-bead-blast",
                "roughness": 0.53,
                "bumpStrength": 0.17,
                "bumpDistanceMm": 0.075
            },
            "supportVariants": outputs,
            "shippingIntegration": "not-started"
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
