"""Build and render the complete front-visible and rear mechanism geometry."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[8]
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
MECHANISM_SCRIPT = (
    REPO / "unity/FidgetingApp/ArtSource/FanCard/"
    "build_fan_card_back_mechanism.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-geometry-validation.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep", PARAMETER_SCRIPT)
mechanism = load_module("fan_card_back_mechanism", MECHANISM_SCRIPT)


def set_display(mat: bpy.types.Material,
                color: tuple[float, float, float, float]) -> None:
    mat.diffuse_color = color


def parent_local(obj: bpy.types.Object, parent: bpy.types.Object,
                 z: float) -> None:
    obj.parent = parent
    obj.location.z = z


def add_track(root: bpy.types.Object,
              gunmetal: bpy.types.Material,
              gold: bpy.types.Material) -> list[bpy.types.Object]:
    visual_start = mechanism.rotate_2d(
        mechanism.FOLLOWER, -mechanism.TRACK_CAP_ANGLE_DEGREES)
    visual_sweep = (
        mechanism.SWEEP_DEGREES
        + mechanism.TRACK_CAP_ANGLE_DEGREES * 2.0)
    undercut = mechanism.create_arc_ribbon_solid(
        root.name + "_Track_Undercut",
        visual_start,
        visual_sweep,
        mechanism.TRACK_SHELL_WIDTH,
        0.00012,
        64,
        gunmetal,
    )
    grille = mechanism.create_woven_grille(gold)
    grille.name = root.name + "_Track_Grille"
    parent_local(
        undercut, root,
        -mechanism.UNDERCUT_OFFSET)
    parent_local(
        grille, root,
        -mechanism.GRILLE_OFFSET)
    objects = [undercut, grille]
    for detent in range(1, 4):
        center = mechanism.rotate_2d(
            mechanism.FOLLOWER,
            mechanism.SWEEP_DEGREES * detent / 3.0)
        magnet = mechanism.create_magnet(
            f"{root.name}_Magnet_{detent:02d}", center, gold)
        parent_local(magnet, root, -mechanism.MAGNET_OFFSET)
        objects.append(magnet)
    return objects


def add_follower(root: bpy.types.Object,
                 chrome: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=12,
        location=(
            mechanism.FOLLOWER.x,
            mechanism.FOLLOWER.y,
            source.CARD_T + 0.00045 - 0.00100,
        ),
    )
    follower = bpy.context.object
    follower.name = root.name + "_FollowerBearing"
    follower.scale = Vector((0.001, 0.001, 0.001))
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    follower.data.materials.append(chrome)
    follower.parent = root
    return follower


def add_spindle(gunmetal: bpy.types.Material) -> bpy.types.Object:
    total = source.PITCH * 2 + source.CARD_T
    bottom = 0.00012
    top = total - 0.00012
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,
        radius=0.002,
        depth=top - bottom,
        location=(0.0, 0.0, (bottom + top) * 0.5),
    )
    spindle = bpy.context.object
    spindle.name = "CommonAxis_RecessedMatteSpindle"
    spindle.data.materials.append(gunmetal)
    return spindle


def scene_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points: list[Vector] = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    return (minimum + maximum) * 0.5, maximum - minimum


def workbench(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.shading.show_specular_highlight = True
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False


def render_ortho(camera: bpy.types.Object, center: Vector,
                 extent: Vector, direction: Vector,
                 filename: str) -> None:
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(extent.x, extent.y, extent.z) * 1.32
    camera.location = center + direction.normalized() * 0.8
    source.aim(camera, center)
    bpy.context.scene.render.filepath = str(OUTPUT / filename)
    bpy.ops.render.render(write_still=True)


def render_perspective(camera: bpy.types.Object, center: Vector,
                       extent: Vector, filename: str) -> None:
    camera.data.type = "PERSP"
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = 0.0
    camera.location = source.camera_position(
        center, 80.0, 32.0, max(extent.x, extent.y) * 0.55)
    source.aim(camera, center)
    bpy.context.scene.render.resolution_x = 1179
    bpy.context.scene.render.resolution_y = 654
    bpy.context.scene.render.filepath = str(OUTPUT / filename)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source.clean()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    clay = source.material(
        "MAT_Clay", (0.32, 0.33, 0.35, 1.0), 0.0, 0.62, 0.0)
    face = source.material(
        "MAT_Face", (0.52, 0.50, 0.47, 1.0), 0.0, 0.58, 0.0)
    dark = source.material(
        "MAT_Dark", (0.045, 0.052, 0.060, 1.0), 0.0, 0.72, 0.0)
    gold = source.material(
        "MAT_GoldMechanism", (0.54, 0.28, 0.055, 1.0), 0.0, 0.52, 0.0)
    chrome = source.material(
        "MAT_Chrome", (0.72, 0.76, 0.82, 1.0), 0.0, 0.35, 0.0)
    for mat, color in (
            (clay, (0.42, 0.44, 0.47, 1.0)),
            (face, (0.70, 0.68, 0.64, 1.0)),
            (dark, (0.07, 0.08, 0.09, 1.0)),
            (gold, (0.55, 0.30, 0.08, 1.0)),
            (chrome, (0.78, 0.82, 0.88, 1.0))):
        set_display(mat, color)

    assembly = bpy.data.objects.new("MagneticFanCard_Root", None)
    bpy.context.collection.objects.link(assembly)
    roots: list[bpy.types.Object] = []
    for index, (rank, angle) in enumerate(
            (("Q", 0), ("K", 45), ("A", 90))):
        root = source.create_layer(
            index, rank, angle, clay, face, dark)
        root.parent = assembly
        roots.append(root)
    assembly.rotation_euler.z = math.radians(90.0)
    add_track(roots[1], dark, gold)
    add_track(roots[2], dark, gold)
    add_follower(roots[0], chrome)
    add_follower(roots[1], chrome)
    add_spindle(dark)
    source.add_bearing(chrome)
    bpy.context.view_layer.update()

    product_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, extent = scene_bounds(product_objects)
    camera_data = bpy.data.cameras.new("CAM_Geometry")
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10.0
    camera = bpy.data.objects.new("CAM_Geometry", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.color = (0.015, 0.017, 0.020)
    workbench(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    render_ortho(camera, center, extent, Vector((0, -1, 0)), "view-front.png")
    render_ortho(camera, center, extent, Vector((0, 1, 0)), "view-back.png")
    render_ortho(camera, center, extent, Vector((0, 0, 1)), "view-top.png")
    render_ortho(camera, center, extent, Vector((0, 0, -1)), "view-bottom.png")
    render_ortho(camera, center, extent, Vector((-1, 0, 0)), "view-left.png")
    render_ortho(camera, center, extent, Vector((1, 0, 0)), "view-right.png")
    render_perspective(camera, center, extent, "workbench.png")

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, radius=0.0028,
        location=(0.0, 0.0, extent.z + 0.012))
    marker = bpy.context.object
    marker.name = "Pivot_Validation_Marker"
    marker.data.materials.append(gold)
    product_objects.append(marker)
    render_ortho(camera, center, extent, Vector((0, 0, 1)),
                 "pivot-overlay.png")
    bpy.data.objects.remove(marker, do_unlink=True)

    saved_positions = [root.location.copy() for root in roots]
    for index, root in enumerate(roots):
        root.location.z += index * 0.018
    cap = bpy.data.objects.get("CommonAxis_BearingCap_Chrome")
    cap_position = cap.location.copy()
    cap.location.z += 0.054
    bpy.context.view_layer.update()
    exploded_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    exploded_center, exploded_extent = scene_bounds(exploded_objects)
    render_perspective(
        camera, exploded_center, exploded_extent, "exploded-geometry.png")
    for root, position in zip(roots, saved_positions):
        root.location = position
    cap.location = cap_position
    bpy.context.view_layer.update()

    report = {
        "cardMm": [63.5, 88.9, 2.5],
        "airGapMm": 1.0,
        "anglesDegrees": [0, 45, 90],
        "rankOrder": ["Q", "K", "A"],
        "trackLayers": ["MiddleCard", "TopCard"],
        "followerLayers": ["BottomCard", "MiddleCard"],
        "views": [
            "front", "back", "top", "bottom", "left", "right",
            "workbench", "pivot", "exploded"
        ],
        "shippingAssetModified": False
    }
    (OUTPUT / "geometry-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
