"""Apply approved materials to the exact Gate 06 selected geometry."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
GEOMETRY_BLEND = (
    SCRIPT.parents[2] / "06-geometry/rev-002/"
    "fan-card-selected-geometry-validation.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
MATERIAL_SCRIPT = (
    SCRIPT.parents[1] / "rev-002/material_variants.py"
)
TEXTURES = SCRIPT.parents[1] / "rev-001/textures"
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-exact-material-lookdev.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep_exact", PARAMETER_SCRIPT)
materials = load_module("fan_card_material_variants_exact", MATERIAL_SCRIPT)


def assign(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def set_camera(
    camera: bpy.types.Object,
    center: Vector,
    half_extent: float,
    lens: float = 80.0,
    elevation: float = 32.0,
    shift_x: float = -0.22,
) -> None:
    camera.data.type = "PERSP"
    camera.data.lens = lens
    camera.data.sensor_width = 36.0
    camera.data.shift_x = shift_x
    camera.location = source.camera_position(
        center, lens, elevation, half_extent)
    source.aim(camera, center)


def add_area_light(
    name: str,
    energy: float,
    size: float,
    temperature: float,
    location: Vector,
    target: Vector,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = source.kelvin(temperature)
    light = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(light)
    light.location = location
    source.aim(light, target)
    return light


def create_support(center: Vector) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(
        location=(center.x - 0.06, center.y, -0.01505))
    support = bpy.context.object
    support.name = "GEO_Support_Base"
    support.scale = (0.36, 0.27, 0.015)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    bevel = support.modifiers.new("Support edge radius", "BEVEL")
    bevel.width = 0.012
    bevel.segments = 5
    return support


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(GEOMETRY_BLEND))
    scene = bpy.context.scene
    for obj in list(scene.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)

    silver = materials.metal_material(
        "MAT_WarmSilver_Medium_Selected",
        (0.34, 0.29, 0.235, 1.0),
        0.53, 680.0, 0.17, 0.26, 0.000075)
    gunmetal = materials.metal_material(
        "MAT_Gunmetal_Selected",
        (0.020, 0.026, 0.034, 1.0),
        0.48, 620.0, 0.07, 0.18, 0.000025)
    etching = materials.metal_material(
        "MAT_Etching_Selected",
        (0.004, 0.006, 0.008, 1.0),
        0.62, 480.0, 0.03, 0.0, 0.000018)
    chrome = materials.metal_material(
        "MAT_Chrome_Selected",
        (0.68, 0.74, 0.82, 1.0),
        0.12, 920.0, 0.02, 0.46, 0.000012)
    warm_gold = materials.metal_material(
        "MAT_WarmGold_Selected",
        (0.52, 0.245, 0.052, 1.0),
        0.29, 720.0, 0.045, 0.20, 0.000018)

    product_objects = []
    for obj in scene.objects:
        name = obj.name
        if "Follower" in name:
            obj.hide_render = True
        if obj.type not in {"MESH", "CURVE", "FONT"}:
            continue
        product_objects.append(obj)
        if "WarmSilverFace" in name:
            assign(obj, silver)
        elif "GoldTrim" in name:
            assign(obj, warm_gold)
        elif any(token in name for token in (
                "Rank_", "Spade")):
            assign(obj, etching)
        elif any(token in name for token in (
                "Track_Grille", "Magnet_")):
            assign(obj, warm_gold)
        elif "BearingCap" in name:
            assign(obj, chrome)
        else:
            assign(obj, gunmetal)

    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    support = create_support(center)
    supports = {
        "A-dark-walnut": materials.image_support_material(
            "MAT_A_DarkWalnut_Exact",
            TEXTURES / "dark_wood/diffuse.jpg",
            TEXTURES / "dark_wood/normal.jpg",
            TEXTURES / "dark_wood/roughness.jpg",
            (2.3, 2.3, 2.3),
            saturation=0.78,
            value=0.62),
        "B-charcoal-hard-case": materials.image_support_material(
            "MAT_B_CharcoalEVA_Exact",
            None,
            TEXTURES / "rubberized_track/normal.jpg",
            TEXTURES / "rubberized_track/roughness.jpg",
            (7.0, 7.0, 7.0),
            (0.008, 0.010, 0.013, 1.0)),
        "C-cork-slab": materials.image_support_material(
            "MAT_C_Cork_Exact",
            TEXTURES / "cork/Cork001_1K-JPG_Color.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_NormalGL.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_Roughness.jpg",
            (4.0, 4.0, 4.0),
            saturation=0.72,
            value=0.70),
    }
    support.data.materials.append(supports["B-charcoal-hard-case"])

    camera = bpy.data.objects.get("CAM_Geometry_Selected")
    camera.name = "CAM_Hero_Selected"
    set_camera(camera, center, half_extent)
    scene.camera = camera

    add_area_light(
        "LGT_Key_Broad", 4.0, 0.35, 5000,
        center + Vector((0.16, -0.14, 0.24)), center)
    add_area_light(
        "LGT_Fill_Weak", 0.8, 0.50, 6500,
        center + Vector((-0.18, -0.05, 0.12)), center)

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (
        0.004, 0.005, 0.007, 1.0)
    background.inputs["Strength"].default_value = 0.015

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    outputs = {}
    for variant, material in supports.items():
        support.data.materials[0] = material
        path = OUTPUT / f"exact-{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name

    support.data.materials[0] = supports["B-charcoal-hard-case"]
    set_camera(
        camera, center, half_extent * 0.55,
        lens=105.0, elevation=38.0, shift_x=0.0)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.filepath = str(OUTPUT / "exact-material-closeup.png")
    bpy.ops.render.render(write_still=True)

    set_camera(camera, center, half_extent)
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    (OUTPUT / "exact-material-report.json").write_text(
        json.dumps({
            "geometrySource": str(GEOMETRY_BLEND),
            "selectedGeometry": {
                "cardThicknessMm": 3.5,
                "cornerRadiusMm": 9.5,
                "blackBorderMm": 1.0,
                "goldTrimMm": 0.8,
                "goldTrimBevelMm": 0.38,
                "trackClearanceMm": 7.590,
            },
            "selectedMaterials": {
                "decorativeDotsPerFront": 0,
                "followersVisibleOnFront": False,
                "warmSilver": "medium-bead-blast",
                "goldTrim": "warm-metallic-beveled",
            },
            "supportVariants": outputs,
            "shippingIntegration": "not-started",
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
