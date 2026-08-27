"""Render visual choices for requested fan-card geometry changes."""

from __future__ import annotations

import importlib.util
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
PARAMETER_SCRIPT = (
    SCRIPT.parents[1] / "rev-002/parameter_sweep.py"
)
OUTPUT = SCRIPT.parent / "model-change-sweep"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep", PARAMETER_SCRIPT)


@dataclass(frozen=True)
class Variant:
    thickness_mm: float = 2.5
    radius_mm: float = 3.81
    black_border_mm: float = 0.5
    gold_trim_mm: float = 0.0
    trim_bevel_mm: float = 0.0


def create_layer(
    index: int,
    rank: str,
    angle: float,
    variant: Variant,
    gunmetal: bpy.types.Material,
    silver: bpy.types.Material,
    etching: bpy.types.Material,
    gold: bpy.types.Material,
) -> bpy.types.Object:
    thickness = variant.thickness_mm / 1000.0
    radius = variant.radius_mm / 1000.0
    black_border = variant.black_border_mm / 1000.0
    gold_trim = variant.gold_trim_mm / 1000.0
    trim_bevel = variant.trim_bevel_mm / 1000.0
    gap = 0.001
    pivot_x = source.CARD_W * 0.5 - radius
    pivot_y = source.CARD_H * 0.5 - radius
    center = Vector((-pivot_x, -pivot_y, 0.0))
    root = bpy.data.objects.new(
        ("BottomCard", "MiddleCard", "TopCard")[index], None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler.z = math.radians(angle)
    root.location.z = index * (thickness + gap)

    source.CARD_T = thickness
    source.HOLE_R = 0.00215
    body_outline = source.rounded_outline(
        source.CARD_W, source.CARD_H, radius, center)
    body = source.prism(
        root.name + "_GunmetalFrame",
        body_outline,
        thickness,
        thickness * 0.5,
        gunmetal,
        bevel=min(thickness * 0.15, 0.00065),
    )
    source.subtract_axis_hole(body)
    body.parent = root

    face_inset = black_border + gold_trim
    face_width = source.CARD_W - face_inset * 2
    face_height = source.CARD_H - face_inset * 2
    face_radius = max(0.0008, radius - face_inset)
    if gold_trim > 0:
        trim_outline = source.rounded_outline(
            source.CARD_W - black_border * 2,
            source.CARD_H - black_border * 2,
            max(0.001, radius - black_border),
            center,
        )
        trim = source.prism(
            root.name + "_GoldTrim",
            trim_outline,
            0.00016,
            thickness + 0.00008,
            gold,
            bevel=max(0.00003, trim_bevel),
        )
        source.subtract_axis_hole(trim)
        trim.parent = root
    face_outline = source.rounded_outline(
        face_width, face_height, face_radius, center)
    face = source.prism(
        root.name + "_WarmSilverFace",
        face_outline,
        0.00010,
        thickness + 0.00018,
        silver,
        bevel=max(0.00003, trim_bevel * 0.65),
    )
    source.subtract_axis_hole(face)
    face.parent = root

    top_z = thickness + 0.00028
    hero = Vector((center.x + 0.003, center.y - 0.0035))
    source.add_spade(
        root, root.name + "_Spade", hero, top_z, 1.10,
        etching, silver, stripes=True)
    rank_offsets = (
        Vector((-0.0172, 0.0250)),
        Vector((0.0172, -0.0250)),
    )
    spade_offsets = (
        Vector((-0.0146, 0.0169)),
        Vector((0.0146, -0.0169)),
    )
    for corner, (rank_offset, spade_offset, rotation) in enumerate(zip(
            rank_offsets, spade_offsets, (0.0, math.pi))):
        source.add_rank(
            root, rank, f"{root.name}_Rank_{corner}",
            Vector((center.x + rank_offset.x,
                    center.y + rank_offset.y)),
            top_z + 0.00005, rotation, etching)
        source.add_spade(
            root, f"{root.name}_CornerSpade_{corner}",
            Vector((center.x + spade_offset.x,
                    center.y + spade_offset.y)),
            top_z + 0.00003, 0.245,
            etching, silver, stripes=False)
    return root


def setup_and_render(variant: Variant, filename: str) -> None:
    source.clean()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    gunmetal = source.material(
        "MAT_Gunmetal", (0.018, 0.024, 0.032, 1.0),
        0.92, 0.46, 620.0)
    silver = source.material(
        "MAT_WarmSilver", (0.46, 0.39, 0.30, 1.0),
        1.0, 0.53, 680.0)
    etching = source.material(
        "MAT_Etching", (0.004, 0.006, 0.008, 1.0),
        0.72, 0.64, 500.0)
    gold = source.material(
        "MAT_GoldTrim", (0.58, 0.27, 0.045, 1.0),
        0.96, 0.31, 720.0)
    support_mat = source.material(
        "MAT_CharcoalSupport", (0.010, 0.013, 0.018, 1.0),
        0.0, 0.84, 150.0)

    thickness = variant.thickness_mm / 1000.0
    source.CARD_T = thickness
    source.PITCH = thickness + 0.001
    source.CAP_H = 0.00065
    assembly = bpy.data.objects.new("MagneticFanCard_Root", None)
    bpy.context.collection.objects.link(assembly)
    for index, (rank, angle) in enumerate(
            (("Q", 0), ("K", 45), ("A", 90))):
        layer = create_layer(
            index, rank, angle, variant,
            gunmetal, silver, etching, gold)
        layer.parent = assembly
    assembly.rotation_euler.z = math.radians(90.0)
    source.add_bearing(gold)
    bpy.context.view_layer.update()
    product = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, half_extent = source.bounds_for(product)
    center.z = thickness + 0.004
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(center.x, center.y, -0.0001))
    support = bpy.context.object
    support.name = "GEO_Support"
    support.scale = (0.80, 0.60, 1.0)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    support.data.materials.append(support_mat)

    camera_data = bpy.data.cameras.new("CAM_VisualSweep")
    camera_data.sensor_width = 36.0
    camera_data.lens = 80.0
    camera_data.shift_x = -0.18
    camera = bpy.data.objects.new("CAM_VisualSweep", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center)
    scene.camera = camera
    key_data = bpy.data.lights.new("LGT_Key", "AREA")
    key_data.energy = 8.0
    key_data.shape = "DISK"
    key_data.size = 0.35
    key_data.color = source.kelvin(5000)
    key = bpy.data.objects.new("LGT_Key", key_data)
    bpy.context.collection.objects.link(key)
    key.location = center + Vector((0.16, -0.14, 0.24))
    source.aim(key, center)
    fill_data = bpy.data.lights.new("LGT_Fill", "AREA")
    fill_data.energy = 1.6
    fill_data.shape = "DISK"
    fill_data.size = 0.50
    fill_data.color = source.kelvin(6500)
    fill = bpy.data.objects.new("LGT_Fill", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = center + Vector((-0.18, -0.05, 0.12))
    source.aim(fill, center)
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.006, 0.007, 0.009, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.030
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 432
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.filepath = str(OUTPUT / filename)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    groups = {
        "thickness": [
            Variant(thickness_mm=2.5),
            Variant(thickness_mm=3.5),
            Variant(thickness_mm=4.5),
        ],
        "radius": [
            Variant(radius_mm=3.81),
            Variant(radius_mm=6.35),
            Variant(radius_mm=9.50),
        ],
        "border": [
            Variant(black_border_mm=0.5),
            Variant(black_border_mm=1.0),
            Variant(black_border_mm=1.5),
        ],
        "gold-trim": [
            Variant(
                thickness_mm=3.5, radius_mm=6.35,
                black_border_mm=1.0),
            Variant(
                thickness_mm=3.5, radius_mm=6.35,
                black_border_mm=1.0,
                gold_trim_mm=0.45, trim_bevel_mm=0.18),
            Variant(
                thickness_mm=3.5, radius_mm=6.35,
                black_border_mm=1.0,
                gold_trim_mm=0.80, trim_bevel_mm=0.38),
        ],
    }
    report = {}
    for group, variants in groups.items():
        report[group] = []
        for index, variant in enumerate(variants):
            filename = f"{group}-{index}.png"
            setup_and_render(variant, filename)
            report[group].append({
                "file": filename,
                "parameters": asdict(variant),
            })
    (OUTPUT / "model-change-sweep.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
