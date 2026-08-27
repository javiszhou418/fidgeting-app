"""Render the legacy 12-segment and proposed 48-segment card corners."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SWEEP_SCRIPT = HERE.parent / "rev-004/model_change_sweep.py"
OUTPUT_BLEND = HERE / "fan-card-high-tessellation.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sweep = load_module("fan_card_tessellation_sweep_source", SWEEP_SCRIPT)
original_rounded_outline = sweep.source.rounded_outline
variant = sweep.Variant(
    thickness_mm=3.5,
    radius_mm=9.5,
    black_border_mm=1.0,
    gold_trim_mm=0.8,
    trim_bevel_mm=0.38,
)


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y").to_euler()


def build(segments: int) -> dict:
    sweep.source.clean()

    def locked_outline(
        width: float,
        height: float,
        radius: float,
        center: Vector,
        ignored_segments: int = segments,
    ):
        return original_rounded_outline(
            width,
            height,
            radius,
            center,
            segments=segments,
        )

    sweep.source.rounded_outline = locked_outline
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    gunmetal = sweep.source.material(
        "MAT_Gunmetal", (0.025, 0.030, 0.038, 1.0),
        0.85, 0.42, 0.0)
    silver = sweep.source.material(
        "MAT_WarmSilver", (0.54, 0.47, 0.37, 1.0),
        0.95, 0.48, 0.0)
    etching = sweep.source.material(
        "MAT_Etching", (0.006, 0.008, 0.010, 1.0),
        0.65, 0.60, 0.0)
    gold = sweep.source.material(
        "MAT_GoldTrim", (0.64, 0.30, 0.055, 1.0),
        0.94, 0.28, 0.0)
    for material, color in (
        (gunmetal, (0.05, 0.06, 0.075, 1.0)),
        (silver, (0.70, 0.62, 0.50, 1.0)),
        (etching, (0.01, 0.012, 0.016, 1.0)),
        (gold, (0.72, 0.35, 0.08, 1.0)),
    ):
        material.diffuse_color = color

    root = sweep.create_layer(
        0, "A", 0.0, variant,
        gunmetal, silver, etching, gold)
    root.rotation_euler.z = math.radians(-12.0)
    bpy.context.view_layer.update()
    meshes = [
        obj for obj in scene.objects
        if obj.type == "MESH"
    ]
    body = bpy.data.objects["BottomCard_GunmetalFrame"]
    trim = bpy.data.objects["BottomCard_GoldTrim"]
    face = bpy.data.objects["BottomCard_WarmSilverFace"]
    bounds_points = [
        obj.matrix_world @ Vector(corner)
        for obj in (body, trim, face)
        for corner in obj.bound_box
    ]
    minimum = Vector((
        min(point.x for point in bounds_points),
        min(point.y for point in bounds_points),
        min(point.z for point in bounds_points),
    ))
    maximum = Vector((
        max(point.x for point in bounds_points),
        max(point.y for point in bounds_points),
        max(point.z for point in bounds_points),
    ))
    marker_material = sweep.source.material(
        "MAT_TessellationMarkers",
        (0.02, 0.75, 0.95, 1.0),
        0.15,
        0.24,
        0.0,
    )
    marker_material.diffuse_color = (0.02, 0.75, 0.95, 1.0)
    center = Vector((
        -(sweep.source.CARD_W * 0.5 - variant.radius_mm / 1000.0),
        -(sweep.source.CARD_H * 0.5 - variant.radius_mm / 1000.0),
    ))
    outline = original_rounded_outline(
        sweep.source.CARD_W,
        sweep.source.CARD_H,
        variant.radius_mm / 1000.0,
        center,
        segments=segments,
    )
    for index, point in enumerate(outline[:segments + 1]):
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10,
            ring_count=6,
            radius=0.00023,
            location=(point.x, point.y, variant.thickness_mm / 1000.0 + 0.00052),
        )
        marker = bpy.context.object
        marker.name = f"DIAG_CornerVertex_{index:02d}"
        marker.data.materials.append(marker_material)
        marker.parent = root
    corner_local = Vector((
        center.x + sweep.source.CARD_W * 0.5,
        center.y + sweep.source.CARD_H * 0.5,
        variant.thickness_mm / 1000.0,
    ))
    target = root.matrix_world @ corner_local

    camera_data = bpy.data.cameras.new("CAM_TessellationReview")
    camera_data.lens = 108.0
    camera_data.sensor_width = 36.0
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10.0
    camera = bpy.data.objects.new("CAM_TessellationReview", camera_data)
    scene.collection.objects.link(camera)
    camera.location = target + Vector((0.034, -0.043, 0.024))
    aim(camera, target)
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "rim.sl"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.012, 0.014, 0.018)
    for obj in meshes:
        obj.show_wire = True
        obj.show_all_edges = True
    scene.render.filepath = str(HERE / f"corner-{segments:02d}.png")
    bpy.ops.render.render(write_still=True)
    if segments == 48:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    return {
        "segmentsPerQuadrant": segments,
        "visibleMeshes": {
            obj.name: {
                "vertices": len(obj.data.vertices),
                "triangles": sum(
                    len(polygon.vertices) - 2
                    for polygon in obj.data.polygons),
            }
            for obj in (body, trim, face)
        },
        "totalSceneVertices": sum(
            len(obj.data.vertices) for obj in meshes),
        "totalSceneTriangles": sum(
            len(polygon.vertices) - 2
            for obj in meshes for polygon in obj.data.polygons),
        "cardBoundsMm": [
            round((maximum.x - minimum.x) * 1000, 6),
            round((maximum.y - minimum.y) * 1000, 6),
            round((maximum.z - minimum.z) * 1000, 6),
        ],
        "maximumCornerChordErrorMm": round(
            variant.radius_mm
            * (1.0 - math.cos(math.radians(90.0 / segments) * 0.5)),
            8),
    }


def main() -> None:
    results = [build(12), build(48)]
    (HERE / "tessellation-report.json").write_text(
        json.dumps({
            "modelId": "magnetic-fan-card",
            "comparison": results,
            "dimensionsChanged": False,
            "collisionSegmentsPerQuadrant": 8,
            "shippingModified": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
