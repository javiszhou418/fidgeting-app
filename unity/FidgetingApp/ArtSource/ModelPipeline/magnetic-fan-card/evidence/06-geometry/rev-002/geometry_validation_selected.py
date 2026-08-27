"""Render full geometry validation for the selected thicker rounded model."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
SWEEP_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-004/model_change_sweep.py"
)
GEOMETRY_HELPERS = (
    SCRIPT.parents[1] / "rev-001/geometry_validation.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-selected-geometry-validation.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


sweep = load_module("fan_card_model_change_sweep", SWEEP_SCRIPT)
geometry = load_module("fan_card_geometry_helpers", GEOMETRY_HELPERS)
geometry.OUTPUT = OUTPUT
variant = sweep.Variant(
    thickness_mm=3.5,
    radius_mm=9.5,
    black_border_mm=1.0,
    gold_trim_mm=0.8,
    trim_bevel_mm=0.38,
)


def main() -> None:
    sweep.source.clean()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    clay = sweep.source.material(
        "MAT_Clay", (0.32, 0.34, 0.37, 1.0), 0.0, 0.68, 0.0)
    face = sweep.source.material(
        "MAT_Face", (0.60, 0.58, 0.54, 1.0), 0.0, 0.62, 0.0)
    dark = sweep.source.material(
        "MAT_Dark", (0.035, 0.042, 0.052, 1.0), 0.0, 0.76, 0.0)
    gold = sweep.source.material(
        "MAT_Gold", (0.56, 0.30, 0.07, 1.0), 0.0, 0.54, 0.0)
    chrome = sweep.source.material(
        "MAT_Chrome", (0.72, 0.78, 0.86, 1.0), 0.0, 0.24, 0.0)
    for mat, color in (
            (clay, (0.40, 0.43, 0.47, 1.0)),
            (face, (0.70, 0.67, 0.62, 1.0)),
            (dark, (0.06, 0.07, 0.09, 1.0)),
            (gold, (0.63, 0.36, 0.08, 1.0)),
            (chrome, (0.78, 0.84, 0.92, 1.0))):
        geometry.set_display(mat, color)

    assembly = bpy.data.objects.new("MagneticFanCard_Root", None)
    bpy.context.collection.objects.link(assembly)
    roots = []
    for index, (rank, angle) in enumerate(
            (("Q", 0), ("K", 45), ("A", 90))):
        root = sweep.create_layer(
            index, rank, angle, variant,
            clay, face, dark, gold)
        root.parent = assembly
        roots.append(root)
    assembly.rotation_euler.z = math.radians(90.0)
    geometry.source.CARD_T = 0.0035
    geometry.source.PITCH = 0.0045
    geometry.add_track(roots[1], dark, gold)
    geometry.add_track(roots[2], dark, gold)
    followers = [
        geometry.add_follower(roots[0], chrome),
        geometry.add_follower(roots[1], chrome),
    ]
    geometry.add_spindle(dark)
    sweep.source.CARD_T = 0.0035
    sweep.source.PITCH = 0.0045
    original_add = sweep.source.add_bearing
    original_add(chrome)
    bpy.context.view_layer.update()

    objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, extent = geometry.scene_bounds(objects)
    camera_data = bpy.data.cameras.new("CAM_Geometry_Selected")
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10.0
    camera = bpy.data.objects.new("CAM_Geometry_Selected", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (0.015, 0.017, 0.020)
    geometry.workbench(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    views = (
        ("view-front.png", Vector((0, -1, 0))),
        ("view-back.png", Vector((0, 1, 0))),
        ("view-top.png", Vector((0, 0, 1))),
        ("view-bottom.png", Vector((0, 0, -1))),
        ("view-left.png", Vector((-1, 0, 0))),
        ("view-right.png", Vector((1, 0, 0))),
    )
    for filename, direction in views:
        visible = filename == "view-bottom.png"
        for follower in followers:
            follower.hide_render = not visible
        geometry.render_ortho(
            camera, center, extent, direction, filename)
    for follower in followers:
        follower.hide_render = True
    geometry.render_perspective(
        camera, center, extent, "workbench.png")

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, radius=0.0028,
        location=(0.0, 0.0, extent.z + 0.014))
    marker = bpy.context.object
    marker.name = "Pivot_Validation_Marker"
    marker.data.materials.append(gold)
    geometry.render_ortho(
        camera, center, extent, Vector((0, 0, 1)),
        "pivot-overlay.png")
    bpy.data.objects.remove(marker, do_unlink=True)

    positions = [root.location.copy() for root in roots]
    for index, root in enumerate(roots):
        root.location.z += index * 0.020
    cap = bpy.data.objects.get("CommonAxis_BearingCap_Chrome")
    cap_position = cap.location.copy()
    cap.location.z += 0.060
    bpy.context.view_layer.update()
    exploded_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    exploded_center, exploded_extent = geometry.scene_bounds(
        exploded_objects)
    geometry.render_perspective(
        camera, exploded_center, exploded_extent,
        "exploded-geometry.png")
    for root, position in zip(roots, positions):
        root.location = position
    cap.location = cap_position

    report = {
        "cardMm": [63.5, 88.9, 3.5],
        "cornerRadiusMm": 9.5,
        "airGapMm": 1.0,
        "blackBorderMm": 1.0,
        "goldTrimMm": 0.8,
        "goldTrimBevelMm": 0.38,
        "followerFromPivotMm": [-43.31, -21.31],
        "trackClearanceMm": 7.59,
        "decorativeDotsPerFront": 0,
        "views": [name.removesuffix(".png") for name, _ in views],
        "shippingAssetModified": False
    }
    (OUTPUT / "geometry-validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
