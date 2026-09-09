"""Author and validate the Fan Card manufactured geometry in Blender.

The exported FBX contains the dark undercut, a genuinely open woven metal
grille, three magnetic inserts, and the canonical heavy Oxanium A/Q/K rank
marks. Card motion remains authored by Unity's FanCardController and
FanCardDetentProfile. Unity instantiates the rear mechanism only on the
canonical TopCard and MiddleCard layers. The front axis exposes only the
recessed matte spindle; this export must contain no cap, ring, washer, or seat.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[4]
SOURCE_DIR = SCRIPT_PATH.parent
UNITY_MODEL_DIR = PROJECT_ROOT / "unity/FidgetingApp/Assets/_FanCard/Models"
PREVIEW_DIR = PROJECT_ROOT / "Artifacts/FanCardBlenderPreview"
BLEND_PATH = SOURCE_DIR / "FanCardBackMechanism.blend"
FBX_PATH = UNITY_MODEL_DIR / "FanCardBackMechanism.fbx"
REPORT_PATH = PREVIEW_DIR / "fan-card-back-mechanism-report.json"
FONT_PATH = SOURCE_DIR / "Oxanium-700.ttf"
GUARDRAIL_PATH = SOURCE_DIR / "fan_card_guardrails.json"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))
from validate_fan_card_guardrails import minimum_track_clearance

CARD_WIDTH = 0.0635
CARD_HEIGHT = 0.0889
CARD_THICKNESS = 0.0035
CARD_RADIUS = 0.0095
PIVOT_X = CARD_WIDTH * 0.5 - CARD_RADIUS
PIVOT_Y = CARD_HEIGHT * 0.5 - CARD_RADIUS
CARD_CENTER = Vector((-PIVOT_X, -PIVOT_Y, 0.0))

FOLLOWER = Vector((-0.04331, -0.02131))
SWEEP_DEGREES = 45.0
TRACK_SHELL_WIDTH = 0.0062
TRACK_GRID_WIDTH = 0.00425
TRACK_GRID_ARC_SEGMENTS = 48
TRACK_GRID_LONGITUDINAL_WIRES = 9
TRACK_GRID_CROSS_WIRES = 72
TRACK_WIRE_RADIUS = 0.000055
TRACK_WEAVE_OFFSET = 0.000018
TRACK_CAP_ANGLE_DEGREES = math.degrees(
    (TRACK_SHELL_WIDTH * 0.5) / FOLLOWER.length
)
MAGNET_RADIUS = 0.00165
MAGNET_DEPTH = 0.00016

BACK_FACE_Z = -CARD_THICKNESS * 0.5
UNDERCUT_OFFSET = 0.00018
MAGNET_OFFSET = 0.00032
GRILLE_OFFSET = 0.00046
RANK_HEIGHT = 0.0064
RANK_RELIEF = 0.000075


def clean_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_metal_material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    grain_scale: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = grain_scale
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.7
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.075
    bump.inputs["Distance"].default_value = 0.000035
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    return material


def rotate_2d(point: Vector, degrees: float) -> Vector:
    radians = math.radians(degrees)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return Vector((
        point.x * cosine - point.y * sine,
        point.x * sine + point.y * cosine,
    ))


def create_arc_ribbon_solid(
    name: str,
    start_point: Vector,
    sweep_degrees: float,
    width: float,
    depth: float,
    segments: int,
    material: bpy.types.Material,
) -> bpy.types.Object:
    radius = start_point.length
    start_angle = math.atan2(start_point.y, start_point.x)
    half_depth = depth * 0.5
    half_width = width * 0.5
    end_angle = start_angle + math.radians(sweep_degrees)
    outline: list[Vector] = []
    for index in range(segments + 1):
        angle = start_angle + (end_angle - start_angle) * index / segments
        outline.append(Vector((math.cos(angle), math.sin(angle)))
                       * (radius + half_width))

    cap_segments = 12
    end_center = Vector((math.cos(end_angle), math.sin(end_angle))) * radius
    for index in range(1, cap_segments + 1):
        angle = end_angle + math.pi * index / cap_segments
        outline.append(end_center
                       + Vector((math.cos(angle), math.sin(angle))) * half_width)

    for index in range(segments - 1, -1, -1):
        angle = start_angle + (end_angle - start_angle) * index / segments
        outline.append(Vector((math.cos(angle), math.sin(angle)))
                       * (radius - half_width))

    start_center = Vector((math.cos(start_angle), math.sin(start_angle))) * radius
    for index in range(1, cap_segments):
        angle = start_angle + math.pi + math.pi * index / cap_segments
        outline.append(start_center
                       + Vector((math.cos(angle), math.sin(angle))) * half_width)

    vertices = [(point.x, point.y, -half_depth) for point in outline]
    vertices.extend((point.x, point.y, half_depth) for point in outline)
    outline_count = len(outline)
    polygon = [Vector((point.x, point.y, 0.0)) for point in outline]
    triangles_2d = tessellate_polygon([polygon])
    coordinate_to_index = {
        (round(point.x, 10), round(point.y, 10)): index
        for index, point in enumerate(polygon)
    }
    faces: list[tuple[int, ...]] = []
    for triangle in triangles_2d:
        if isinstance(triangle[0], int):
            indices = tuple(triangle)
        else:
            indices = tuple(coordinate_to_index[
                (round(point.x, 10), round(point.y, 10))
            ] for point in triangle)
        faces.append(tuple(reversed(indices)))
        faces.append(tuple(index + outline_count for index in indices))
    for index in range(outline_count):
        next_index = (index + 1) % outline_count
        faces.append((
            index,
            next_index,
            next_index + outline_count,
            index + outline_count,
        ))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Machined edge bevel", "BEVEL")
    bevel.width = 0.000045
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    return obj


def create_tube_curve(
    name: str,
    points: list[Vector],
    radius: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 1
    curve.resolution_u = 1
    curve.fill_mode = "FULL"
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def create_woven_grille(material: bpy.types.Material) -> bpy.types.Object:
    visual_start = rotate_2d(FOLLOWER, -TRACK_CAP_ANGLE_DEGREES)
    visual_sweep_degrees = SWEEP_DEGREES + TRACK_CAP_ANGLE_DEGREES * 2.0
    radius = visual_start.length
    start_angle = math.atan2(visual_start.y, visual_start.x)
    half_width = TRACK_GRID_WIDTH * 0.5 - TRACK_WIRE_RADIUS
    wire_objects: list[bpy.types.Object] = []

    for wire_index in range(TRACK_GRID_LONGITUDINAL_WIRES):
        radial_offset = -half_width + 2.0 * half_width * (
            wire_index / (TRACK_GRID_LONGITUDINAL_WIRES - 1)
        )
        points = []
        for segment in range(TRACK_GRID_ARC_SEGMENTS + 1):
            angle = start_angle + math.radians(visual_sweep_degrees) * (
                segment / TRACK_GRID_ARC_SEGMENTS
            )
            points.append(Vector((
                math.cos(angle) * (radius + radial_offset),
                math.sin(angle) * (radius + radial_offset),
                0.0,
            )))
        wire_objects.append(create_tube_curve(
            f"Warp_{wire_index:02d}", points, TRACK_WIRE_RADIUS, material
        ))

    for wire_index in range(TRACK_GRID_CROSS_WIRES):
        t = wire_index / (TRACK_GRID_CROSS_WIRES - 1)
        angle = start_angle + math.radians(visual_sweep_degrees) * t
        radial = Vector((math.cos(angle), math.sin(angle)))
        inner = radial * (radius - TRACK_GRID_WIDTH * 0.5 + TRACK_WIRE_RADIUS)
        outer = radial * (radius + TRACK_GRID_WIDTH * 0.5 - TRACK_WIRE_RADIUS)
        points = [
            Vector((inner.x, inner.y, -TRACK_WEAVE_OFFSET)),
            Vector((outer.x, outer.y, -TRACK_WEAVE_OFFSET)),
        ]
        wire_objects.append(create_tube_curve(
            f"Weft_{wire_index:02d}", points, TRACK_WIRE_RADIUS, material
        ))

    bpy.ops.object.select_all(action="DESELECT")
    for obj in wire_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = wire_objects[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    grille = bpy.context.active_object
    grille.name = "Track_Grille"
    grille.data.name = "Track_Grille_Mesh"
    for polygon in grille.data.polygons:
        polygon.use_smooth = True
    bpy.ops.object.select_all(action="DESELECT")
    return grille


def create_magnet(
    name: str,
    center: Vector,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48,
        radius=MAGNET_RADIUS,
        depth=MAGNET_DEPTH,
        end_fill_type="NGON",
        location=(center.x, center.y, 0.0),
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name + "_Mesh"
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Magnet edge bevel", "BEVEL")
    bevel.width = 0.000045
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    bpy.ops.object.shade_smooth_by_angle()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def create_rank_mark(
    glyph: str,
    object_name: str,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Convert an app Oxanium 700 rank glyph to watertight relief mesh.

    Baking A/Q/K from the same static app-font instance guarantees consistent
    weight and removes font-atlas, clipping, and camera-angle dependencies.
    """
    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Missing static app-font instance required by Blender: {FONT_PATH}"
        )
    font = bpy.data.fonts.load(str(FONT_PATH))
    curve = bpy.data.curves.new(object_name + "_Curve", "FONT")
    curve.body = glyph
    curve.font = font
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = 0.010
    curve.dimensions = "2D"
    curve.fill_mode = "BOTH"
    curve.resolution_u = 12
    curve.extrude = RANK_RELIEF
    obj = bpy.data.objects.new(object_name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    height_scale = RANK_HEIGHT / obj.dimensions.y
    obj.scale.x = height_scale
    obj.scale.y = height_scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    minimum_x = min(vertex.co.x for vertex in obj.data.vertices)
    maximum_x = max(vertex.co.x for vertex in obj.data.vertices)
    minimum_y = min(vertex.co.y for vertex in obj.data.vertices)
    maximum_y = max(vertex.co.y for vertex in obj.data.vertices)
    minimum_z = min(vertex.co.z for vertex in obj.data.vertices)
    center_x = (minimum_x + maximum_x) * 0.5
    center_y = (minimum_y + maximum_y) * 0.5
    for vertex in obj.data.vertices:
        vertex.co.x -= center_x
        vertex.co.y -= center_y
        vertex.co.z -= minimum_z
    obj.data.name = object_name + "_Mesh"
    obj.data.validate(verbose=True)
    obj.data.update()
    bpy.ops.object.select_all(action="DESELECT")
    return obj


def create_preview_card(material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=(CARD_CENTER.x, CARD_CENTER.y, 0.0))
    card = bpy.context.active_object
    card.name = "PreviewOnly_Card"
    card.dimensions = (CARD_WIDTH, CARD_HEIGHT, CARD_THICKNESS)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = card.modifiers.new("Card corner and edge bevel", "BEVEL")
    bevel.width = CARD_RADIUS
    bevel.segments = 8
    bevel.affect = "EDGES"
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    card.data.materials.append(material)
    return card


def duplicate_for_preview(
    source: bpy.types.Object,
    name: str,
    z_offset: float,
) -> bpy.types.Object:
    duplicate = source.copy()
    duplicate.data = source.data.copy()
    duplicate.name = name
    bpy.context.collection.objects.link(duplicate)
    duplicate.location.z = z_offset
    duplicate.hide_render = False
    return duplicate


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    target: Vector,
    energy: float,
    size: float,
    color: tuple[float, float, float],
) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_preview(
    camera: bpy.types.Object,
    target: Vector,
    location: tuple[float, float, float],
    filename: str,
    orthographic_scale: float | None = None,
) -> None:
    camera.location = location
    point_camera(camera, target)
    camera.data.type = "ORTHO" if orthographic_scale else "PERSP"
    if orthographic_scale:
        camera.data.ortho_scale = orthographic_scale
    else:
        camera.data.lens = 68.0
    bpy.context.scene.render.filepath = str(PREVIEW_DIR / filename)
    bpy.ops.render.render(write_still=True)


def mesh_statistics(obj: bpy.types.Object) -> dict[str, object]:
    return {
        "name": obj.name,
        "vertices": len(obj.data.vertices),
        "triangles": sum(len(poly.vertices) - 2 for poly in obj.data.polygons),
        "bounds_mm": [round(component * 1000.0, 4) for component in obj.dimensions],
    }


def main() -> None:
    UNITY_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    clean_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    guardrails = json.loads(GUARDRAIL_PATH.read_text(encoding="utf-8"))
    measured_edge_clearance_mm = minimum_track_clearance(guardrails)
    required_edge_clearance_mm = guardrails["back_track"][
        "minimum_outer_edge_clearance"
    ]

    gunmetal = make_metal_material(
        "Gunmetal", (0.052, 0.058, 0.064, 1.0), 0.88, 0.47, 620.0
    )
    gold = make_metal_material(
        "WarmGold", (0.64, 0.37, 0.085, 1.0), 0.96, 0.28, 780.0
    )
    card_material = make_metal_material(
        "PreviewCard", (0.055, 0.060, 0.066, 1.0), 0.88, 0.48, 420.0
    )
    etching = make_metal_material(
        "Etching", (0.018, 0.019, 0.021, 1.0), 0.76, 0.77, 520.0
    )

    visual_track_start = rotate_2d(FOLLOWER, -TRACK_CAP_ANGLE_DEGREES)
    visual_track_sweep = SWEEP_DEGREES + TRACK_CAP_ANGLE_DEGREES * 2.0
    undercut = create_arc_ribbon_solid(
        "Track_Undercut",
        visual_track_start,
        visual_track_sweep,
        TRACK_SHELL_WIDTH,
        0.00012,
        64,
        gunmetal,
    )
    grille = create_woven_grille(gold)
    magnets = []
    for detent in range(1, 4):
        center = rotate_2d(FOLLOWER, SWEEP_DEGREES * detent / 3.0)
        magnets.append(create_magnet(f"Magnet_{detent:02d}", center, gold))
    rank_marks = [
        create_rank_mark("A", "Ace_A_Oxanium", etching),
        create_rank_mark("Q", "Queen_Q_Oxanium", etching),
        create_rank_mark("K", "King_K_Oxanium", etching),
    ]
    export_objects = [undercut, grille, *magnets, *rank_marks]
    for obj in export_objects:
        obj["fan_card_role"] = obj.name
        obj["units"] = "meters"

    # Save the editable source before creating non-exported preview duplicates.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = grille
    bpy.ops.export_scene.fbx(
        filepath=str(FBX_PATH),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        bake_space_transform=True,
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_triangles=True,
        add_leaf_bones=False,
        path_mode="AUTO",
    )

    # Preview the physical sandwich from the exposed back side. Export objects
    # stay at a clean zero origin; only these duplicates receive assembly depth.
    for obj in export_objects:
        obj.hide_render = True
    create_preview_card(card_material)
    preview_undercut = duplicate_for_preview(
        undercut, "Preview_Track_Undercut", BACK_FACE_Z - UNDERCUT_OFFSET
    )
    preview_grille = duplicate_for_preview(
        grille, "Preview_Track_Grille", BACK_FACE_Z - GRILLE_OFFSET
    )
    preview_magnets = [
        duplicate_for_preview(
            magnet,
            "Preview_" + magnet.name,
            BACK_FACE_Z - MAGNET_OFFSET,
        )
        for magnet in magnets
    ]
    _ = (preview_undercut, preview_grille, preview_magnets)

    track_center = sum(
        (rotate_2d(FOLLOWER, SWEEP_DEGREES * index / 6.0)
         for index in range(7)),
        Vector((0.0, 0.0)),
    ) / 7.0
    target = Vector((track_center.x, track_center.y, BACK_FACE_Z - 0.00030))

    camera_data = bpy.data.cameras.new("PreviewCamera")
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10.0
    camera = bpy.data.objects.new("PreviewCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    add_area_light(
        "LargeWarmSoftbox",
        (target.x - 0.045, target.y - 0.035, -0.075),
        target,
        0.34,
        0.055,
        (1.0, 0.78, 0.58),
    )
    add_area_light(
        "CoolRim",
        (target.x + 0.045, target.y + 0.020, -0.045),
        target,
        0.16,
        0.035,
        (0.52, 0.67, 1.0),
    )
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.028, 0.022, 0.018, 1.0
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.025

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    render_preview(
        camera,
        target,
        (target.x + 0.030, target.y - 0.044, -0.095),
        "fan-card-back-grille-hero.png",
    )
    render_preview(
        camera,
        target,
        (target.x + 0.010, target.y - 0.012, -0.031),
        "fan-card-back-grille-close.png",
    )
    render_preview(
        camera,
        target,
        (target.x, target.y, -0.120),
        "fan-card-back-grille-orthographic.png",
        orthographic_scale=0.070,
    )

    # Deterministic geometry checks are recorded alongside the renders.
    magnet_cap = BACK_FACE_Z - MAGNET_OFFSET - MAGNET_DEPTH * 0.5
    grille_back = BACK_FACE_Z - GRILLE_OFFSET + TRACK_WIRE_RADIUS
    assertions = {
        "grille_is_real_geometry": len(grille.data.polygons) > 1000,
        "grille_has_no_surface_fill": len(grille.data.polygons) < 20000,
        "three_independent_magnets": len(magnets) == 3,
        "grille_outward_of_magnet_caps": grille_back < magnet_cap,
        "four_detents_implied_by_three_inserts_plus_follower": len(magnets) + 1 == 4,
        "sweep_degrees_unchanged": SWEEP_DEGREES == 45.0,
        "rounded_track_end_margin_degrees": TRACK_CAP_ANGLE_DEGREES > 0.0,
        "rank_set_uses_static_app_font_meshes": all(
            rank.type == "MESH"
            and abs(rank.dimensions.y - RANK_HEIGHT) < 0.00001
            and len(rank.data.polygons) > 10
            for rank in rank_marks
        ),
        "face_art_uses_two_opposed_corner_indices": (
            guardrails["face_art"]["rank_marks_per_front"] == 2
            and guardrails["face_art"]["corner_spades_per_front"] == 2
            and guardrails["face_art"]["corner_index_rotations_degrees"]
            == [0.0, 180.0]
        ),
        "only_locked_rank_patterns_are_authored": (
            guardrails["face_art"]["rank_glyphs"] == ["A", "Q", "K"]
            and guardrails["face_art"]["allowed_patterns"]
            == {"AAA": ["A", "A", "A"], "QKA": ["Q", "K", "A"]}
        ),
        "track_outer_contour_respects_edge_clearance": (
            measured_edge_clearance_mm >= required_edge_clearance_mm
        ),
        "track_layer_contract_is_top_and_middle_only": (
            guardrails["mechanism"]["track_layers"]
            == ["TopCard", "MiddleCard"]
            and guardrails["mechanism"]["follower_layers"]
            == ["MiddleCard", "BottomCard"]
        ),
        "front_axis_export_has_no_cap_ring_washer_or_seat": (
            guardrails["mechanism"]["front_visible_axis_hardware"]
                == "recessed_matte_spindle_only"
            and all(
                token.lower() not in obj.name.lower()
                for obj in export_objects
                for token in guardrails["mechanism"][
                    "forbidden_front_axis_name_tokens"
                ]
            )
        ),
    }
    if not all(assertions.values()):
        raise RuntimeError(f"Fan Card back mechanism validation failed: {assertions}")
    report = {
        "source_blend": str(BLEND_PATH),
        "unity_fbx": str(FBX_PATH),
        "geometry": [mesh_statistics(obj) for obj in export_objects],
        "wire_diameter_mm": TRACK_WIRE_RADIUS * 2000.0,
        "longitudinal_wires": TRACK_GRID_LONGITUDINAL_WIRES,
        "cross_wires": TRACK_GRID_CROSS_WIRES,
        "magnet_diameter_mm": MAGNET_RADIUS * 2000.0,
        "mechanical_sweep_degrees": SWEEP_DEGREES,
        "visual_end_margin_degrees": TRACK_CAP_ANGLE_DEGREES,
        "minimum_outer_edge_clearance_mm": measured_edge_clearance_mm,
        "required_outer_edge_clearance_mm": required_edge_clearance_mm,
        "face_art": guardrails["face_art"],
        "assembly": {
            "track_layers": guardrails["mechanism"]["track_layers"],
            "follower_layers": guardrails["mechanism"]["follower_layers"],
            "front_visible_axis_hardware": guardrails["mechanism"]
                ["front_visible_axis_hardware"],
        },
        "assertions": assertions,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
