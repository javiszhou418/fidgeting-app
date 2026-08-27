#!/usr/bin/env python3
"""Build the Premium Display Case Gate 05 real Blender white model."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "premium-display-case-blockout.blend"
VALIDATOR_PATH = ROOT / "validate_blockout.py"

SPEC = importlib.util.spec_from_file_location("premium_display_case_blockout_validation", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {VALIDATOR_PATH}")
VALIDATION = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATION)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.materials,
        bpy.data.curves,
        bpy.data.meshes,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_principled_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    return material


def make_emission_material(
    name: str,
    color: tuple[float, float, float, float],
    strength: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def link_object(obj: bpy.types.Object, collection: bpy.types.Collection | None = None) -> None:
    (collection or bpy.context.scene.collection).objects.link(obj)


def parent_keep_world(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    bpy.context.view_layer.update()
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world
    bpy.context.view_layer.update()


def empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    link_object(obj)
    if parent:
        parent_keep_world(obj, parent)
    return obj


def rounded_prism(
    name: str,
    width: float,
    height: float,
    depth: float,
    radius: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object,
    corner_steps: int = 16,
) -> bpy.types.Object:
    profile = VALIDATION.rounded_profile(width, height, radius, corner_steps)
    count = len(profile)
    vertices = [(x, y, -depth / 2.0) for x, y in profile]
    vertices.extend((x, y, depth / 2.0) for x, y in profile)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj)
    obj.location = location
    obj.data.materials.append(material)
    obj["model_pipeline_subject"] = True
    obj["gate"] = "05-blockout"
    parent_keep_world(obj, parent)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    bevel = obj.modifiers.new("DiagnosticEdgeSoftening", "BEVEL")
    bevel.width = min(0.8, depth * 0.18)
    bevel.segments = 3
    bevel.limit_method = "ANGLE"
    return obj


def closed_tube(
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    path = VALIDATION.rounded_rectangle_path()
    outer_profile = VALIDATION.rounded_profile(
        VALIDATION.TUBE_OUTER_WIDTH_MM,
        VALIDATION.TUBE_OUTER_DEPTH_MM,
        VALIDATION.TUBE_PROFILE_RADIUS_MM,
    )
    inner_profile = VALIDATION.rounded_profile(
        VALIDATION.TUBE_PASSAGE_WIDTH_MM,
        VALIDATION.TUBE_PASSAGE_DEPTH_MM,
        VALIDATION.TUBE_PASSAGE_RADIUS_MM,
    )
    outer_count = len(outer_profile)
    inner_count = len(inner_profile)
    ring_stride = outer_count + inner_count
    vertices: list[tuple[float, float, float]] = []
    for sample in path:
        x, y = sample["point"]
        tangent_x, tangent_y = sample["tangent"]
        normal_x, normal_y = -tangent_y, tangent_x
        for profile_u, profile_z in outer_profile:
            vertices.append((
                x + normal_x * profile_u,
                y + normal_y * profile_u,
                25.0 + profile_z,
            ))
        for profile_u, profile_z in inner_profile:
            vertices.append((
                x + normal_x * profile_u,
                y + normal_y * profile_u,
                25.0 + profile_z,
            ))
    faces: list[tuple[int, int, int, int]] = []
    path_count = len(path)
    for ring_index in range(path_count):
        next_ring = (ring_index + 1) % path_count
        current_base = ring_index * ring_stride
        next_base = next_ring * ring_stride
        for profile_index in range(outer_count):
            next_profile = (profile_index + 1) % outer_count
            faces.append((
                current_base + profile_index,
                next_base + profile_index,
                next_base + next_profile,
                current_base + next_profile,
            ))
        inner_base = current_base + outer_count
        next_inner_base = next_base + outer_count
        for profile_index in range(inner_count):
            next_profile = (profile_index + 1) % inner_count
            faces.append((
                inner_base + profile_index,
                inner_base + next_profile,
                next_inner_base + next_profile,
                next_inner_base + profile_index,
            ))
    mesh = bpy.data.meshes.new("ContinuousTubePerimeter_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new("ContinuousTubePerimeter", mesh)
    link_object(obj)
    obj.data.materials.append(material)
    obj["model_pipeline_subject"] = True
    obj["gate"] = "05-blockout"
    obj["construction"] = "one-cyclic-hollow-tube-sweep"
    obj["path_closed"] = True
    obj["path_sample_count"] = path_count
    obj["outer_profile_count"] = outer_count
    obj["inner_profile_count"] = inner_count
    obj["outer_section_mm"] = [
        VALIDATION.TUBE_OUTER_WIDTH_MM,
        VALIDATION.TUBE_OUTER_DEPTH_MM,
    ]
    obj["wall_thickness_mm"] = VALIDATION.TUBE_WALL_MM
    obj["passage_section_mm"] = [
        VALIDATION.TUBE_PASSAGE_WIDTH_MM,
        VALIDATION.TUBE_PASSAGE_DEPTH_MM,
    ]
    obj["corner_radii_mm"] = [
        VALIDATION.OUTER_CORNER_RADIUS_MM,
        VALIDATION.CENTERLINE_CORNER_RADIUS_MM,
        VALIDATION.INNER_CORNER_RADIUS_MM,
    ]
    parent_keep_world(obj, parent)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def orient_camera(camera: bpy.types.Object, target: Vector) -> None:
    backward = (camera.location - target).normalized()
    world_up = Vector((0.0, 1.0, 0.0))
    if abs(backward.dot(world_up)) > 0.999:
        world_up = Vector((0.0, 0.0, 1.0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    color: tuple[float, float, float],
    target: Vector,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    link_object(light)
    light.location = location
    look_at(light, target)
    return light


def add_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    orthographic_scale: float | None = None,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    data.dof.use_dof = False
    data.clip_end = 5000.0
    if orthographic_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = orthographic_scale
    camera = bpy.data.objects.new(name, data)
    link_object(camera)
    camera.location = location
    orient_camera(camera, Vector(target))
    return camera


def add_camera_band(
    camera: bpy.types.Object,
    name: str,
    y: float,
    width: float,
    height: float,
    depth: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add()
    band = bpy.context.object
    band.name = name
    band.parent = camera
    band.matrix_parent_inverse = Matrix.Identity(4)
    band.location = (0.0, y, -120.0)
    band.rotation_euler = (0.0, 0.0, 0.0)
    band.dimensions = (width, height, depth)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    band.data.materials.append(material)
    band["model_pipeline_exclude"] = True
    return band


def add_camera_text(
    camera: bpy.types.Object,
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.015
    curve.bevel_depth = 0.005
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    obj.parent = camera
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = location
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.data.materials.append(material)
    obj["model_pipeline_exclude"] = True
    return obj


def render(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    path: Path,
    resolution: tuple[int, int],
) -> None:
    scene.camera = camera
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def image_plane(
    scene: bpy.types.Scene,
    name: str,
    image_path: Path,
    center: tuple[float, float],
    cell_size: tuple[float, float],
) -> bpy.types.Object:
    image = bpy.data.images.load(str(image_path), check_existing=False)
    image_aspect = image.size[0] / image.size[1]
    cell_aspect = cell_size[0] / cell_size[1]
    if image_aspect >= cell_aspect:
        width = cell_size[0]
        height = width / image_aspect
    else:
        height = cell_size[1]
        width = height * image_aspect
    vertices = [
        (-width / 2.0, -height / 2.0, 0.05),
        (width / 2.0, -height / 2.0, 0.05),
        (width / 2.0, height / 2.0, 0.05),
        (-width / 2.0, height / 2.0, 0.05),
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_values = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    for loop, uv in zip(mesh.loops, uv_values):
        uv_layer.data[loop.index].uv = uv
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = (center[0], center[1], 0.0)
    material = bpy.data.materials.new(f"{name}_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(texture.outputs["Alpha"], emission.inputs["Strength"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    obj.data.materials.append(material)
    return obj


def contact_text(
    scene: bpy.types.Scene,
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(material)
    return obj


def build_contact_sheet(paths: list[tuple[str, Path]]) -> None:
    source_scene = bpy.context.window.scene
    scene = bpy.data.scenes.new("Gate05ContactSheet")
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2400
    scene.render.resolution_y = 2200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("Gate05ContactWorld")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.018, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

    camera_data = bpy.data.cameras.new("ContactSheetCamera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 12.0
    camera = bpy.data.objects.new("ContactSheetCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, 0.0, 10.0)
    scene.camera = camera

    white = make_emission_material("MAT_CONTACT_White", (0.92, 0.95, 0.98, 1.0), 1.0)
    cyan = make_emission_material("MAT_CONTACT_Cyan", (0.30, 0.78, 0.90, 1.0), 1.0)
    red = make_emission_material("MAT_CONTACT_Red", (0.95, 0.40, 0.44, 1.0), 1.0)
    card = make_emission_material("MAT_CONTACT_Card", (0.035, 0.045, 0.060, 1.0), 1.0)
    centers = ((-3.2, 2.25), (3.2, 2.25), (-3.2, -2.45), (3.2, -2.45))
    for index, ((label, image_path), center) in enumerate(zip(paths, centers)):
        mesh = bpy.data.meshes.new(f"ContactCard_{index}_Mesh")
        width, height = 6.05, 4.35
        mesh.from_pydata(
            [
                (-width / 2.0, -height / 2.0, -0.05),
                (width / 2.0, -height / 2.0, -0.05),
                (width / 2.0, height / 2.0, -0.05),
                (-width / 2.0, height / 2.0, -0.05),
            ],
            [],
            [(0, 1, 2, 3)],
        )
        card_obj = bpy.data.objects.new(f"ContactCard_{index}", mesh)
        scene.collection.objects.link(card_obj)
        card_obj.location = (center[0], center[1], 0.0)
        card_obj.data.materials.append(card)
        image_plane(scene, f"ContactImage_{index}", image_path, (center[0], center[1] - 0.12), (5.75, 3.75))
        contact_text(scene, f"ContactLabel_{index}", label, (center[0], center[1] + 1.88, 0.12), 0.30, cyan)

    contact_text(scene, "ContactTitle", "GATE 05 · REAL BLENDER BLOCKOUT", (0.0, 5.35, 0.12), 0.48, white)
    contact_text(
        scene,
        "ContactSubtitle",
        "228 x 304 x 59 MM · PORTRAIT 3:4 · NOT SCHEMATIC",
        (0.0, 4.83, 0.12),
        0.24,
        cyan,
    )
    contact_text(
        scene,
        "ContactFooter",
        "ONE CYCLIC HOLLOW TUBE · 10 x 9 MM · WALL 2 MM · R20 · GATE 06 FULL VALIDATION DEFERRED",
        (0.0, -5.65, 0.12),
        0.20,
        red,
    )
    scene.render.filepath = str(ROOT / "blockout-contact-sheet.png")
    bpy.ops.render.render(write_still=True)
    bpy.context.window.scene = source_scene
    bpy.data.scenes.remove(scene)


def main() -> None:
    clear_scene()
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate05_Blockout"
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene["model_pipeline_up_axis"] = "Y"
    scene["model_pipeline_front_axis"] = "+Z"
    scene["coordinate_contract"] = "X-width/Y-height/Z-front"
    scene["gate"] = "05-blockout"
    scene["blockout_revision"] = 1
    scene["locked_total_duration_seconds"] = 4.520833
    scene["shipping_unity_changed"] = False
    scene["full_gate06_validation_deferred"] = True

    world = scene.world or bpy.data.worlds.new("Gate05World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.019, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42

    shell_clay = make_principled_material("MAT_DIAGNOSTIC_ShellClay", (0.68, 0.73, 0.78, 1.0), 0.62)
    tube_clay = make_principled_material("MAT_DIAGNOSTIC_TubeClay", (0.94, 0.96, 0.98, 1.0), 0.48)
    label_clay = make_principled_material("MAT_DIAGNOSTIC_LabelClay", (0.80, 0.82, 0.79, 1.0), 0.72)
    insert_clay = make_principled_material("MAT_DIAGNOSTIC_InsertClay", (0.34, 0.38, 0.43, 1.0), 0.86)
    studio_material = make_principled_material("MAT_STUDIO_Backdrop", (0.020, 0.028, 0.040, 1.0), 0.92)
    overlay_dark = make_emission_material("MAT_OVERLAY_Dark", (0.012, 0.018, 0.028, 1.0), 1.0)
    overlay_white = make_emission_material("MAT_OVERLAY_White", (0.94, 0.96, 0.98, 1.0), 1.0)
    overlay_cyan = make_emission_material("MAT_OVERLAY_Cyan", (0.25, 0.80, 0.92, 1.0), 1.0)
    overlay_red = make_emission_material("MAT_OVERLAY_Red", (0.98, 0.42, 0.45, 1.0), 1.0)

    presentation_root = empty("PresentationRoot")
    presentation_root["role"] = "transform-root"
    presentation_root["motion_owner"] = True
    presentation_root["angular_velocity"] = 0.0
    presentation_root["locked_total_duration_seconds"] = 4.520833
    case_assembly = empty("CaseAssembly", presentation_root)
    case_assembly["role"] = "always-assembled-transform-group"

    rear_shell = rounded_prism(
        "RearPolycarbonateShell",
        224.0,
        300.0,
        7.0,
        13.0,
        (0.0, 0.0, -26.0),
        shell_clay,
        case_assembly,
    )
    rear_shell["dimension_source"] = "approved-envelope-and-retained-shipping-baseline"
    tactile_insert = rounded_prism(
        "TactileBackgroundInsert",
        182.0,
        202.0,
        9.0,
        10.0,
        (0.0, -42.0, -4.0),
        insert_clay,
        rear_shell,
    )
    tactile_insert["surface_scope"] = "neutral-clay-only-no-final-grain"
    content_slot = empty("ContentSlot", rear_shell)
    content_slot.location = (0.0, -42.0, 16.0)
    content_slot.empty_display_type = "CUBE"
    content_slot.empty_display_size = 90.0
    content_slot["role"] = "runtime-anchor"
    content_slot["width_mm"] = 180.0
    content_slot["height_mm"] = 198.0
    content_slot["depth_mm"] = 48.0
    content_slot["corner_radius_mm"] = 16.0
    content_slot["prize_content_modeled"] = False

    front_shell = rounded_prism(
        "FrontPolycarbonateShell",
        224.0,
        300.0,
        6.0,
        13.0,
        (0.0, 0.0, 20.0),
        shell_clay,
        case_assembly,
    )
    front_shell["dimension_source"] = "retained-shipping-inset-adapted-to-approved-width"
    tube = closed_tube(tube_clay, front_shell)
    physical_label = rounded_prism(
        "PhysicalLabel",
        184.0,
        58.0,
        3.0,
        4.0,
        (0.0, 105.0, 24.0),
        label_clay,
        front_shell,
    )
    physical_label["content"] = "blank-white-model-zone"
    for zone_name in ("LogoZone", "AchievementZone", "NarrowFoil"):
        zone = empty(zone_name, physical_label)
        zone["gate05_geometry_status"] = "deferred-no-artwork"
    transparent_cover = empty("TransparentCover", front_shell)
    transparent_cover["gate05_geometry_status"] = "deferred-no-approved-thickness"
    transparent_cover["physical_part_geometry"] = False

    bpy.ops.mesh.primitive_cube_add(location=(0.0, -157.0, 0.0))
    ground = bpy.context.object
    ground.name = "StudioGround"
    ground.dimensions = (900.0, 6.0, 900.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ground.data.materials.append(studio_material)
    ground["model_pipeline_exclude"] = True
    bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, -390.0))
    backdrop = bpy.context.object
    backdrop.name = "StudioBackdrop"
    backdrop.dimensions = (1100.0, 900.0, 8.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    backdrop.data.materials.append(studio_material)
    backdrop["model_pipeline_exclude"] = True

    target = Vector((0.0, 0.0, 5.0))
    add_area_light("Gate05Key", (330.0, 390.0, 520.0), 1400000.0, 310.0, (1.0, 0.93, 0.84), target)
    add_area_light("Gate05Fill", (-360.0, 70.0, 350.0), 780000.0, 360.0, (0.72, 0.84, 1.0), target)
    add_area_light("Gate05Rim", (-120.0, 250.0, -260.0), 980000.0, 260.0, (0.58, 0.72, 1.0), target)
    add_area_light("Gate05SideFill", (560.0, 60.0, 40.0), 820000.0, 300.0, (0.88, 0.93, 1.0), target)
    add_area_light("Gate05RearFill", (-80.0, 80.0, -520.0), 860000.0, 320.0, (0.72, 0.84, 1.0), target)

    hero_camera = add_camera("Gate05HeroCamera", (230.0, 115.0, 1300.0), (0.0, 0.0, 0.0), 70.0)
    front_camera = add_camera("Gate05FrontCamera", (0.0, 0.0, 700.0), (0.0, 0.0, 0.0), 70.0, 345.0)
    side_camera = add_camera("Gate05SideCamera", (700.0, 0.0, 0.0), (0.0, 0.0, 0.0), 70.0, 345.0)
    rear_camera = add_camera("Gate05RearCamera", (0.0, 0.0, -700.0), (0.0, 0.0, 0.0), 70.0, 345.0)
    tube_camera = add_camera("Gate05TubeCamera", (310.0, 270.0, 460.0), (96.0, 132.0, 24.0), 88.0)

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)

    overlay_objects = [
        add_camera_band(hero_camera, "HeroTopBand", 20.0, 64.0, 8.0, 0.12, overlay_dark),
        add_camera_band(hero_camera, "HeroBottomBand", -20.0, 64.0, 8.0, 0.12, overlay_dark),
        add_camera_text(
            hero_camera,
            "HeroTitle",
            "REAL BLENDER BLOCKOUT · GATE 05",
            (0.0, 21.1, -119.8),
            2.05,
            overlay_white,
        ),
        add_camera_text(
            hero_camera,
            "HeroSubtitle",
            "228 x 304 x 59 MM · PORTRAIT 3:4 · NOT SCHEMATIC",
            (0.0, 17.9, -119.8),
            1.08,
            overlay_cyan,
        ),
        add_camera_text(
            hero_camera,
            "HeroFooter",
            "ONE CYCLIC TUBE · 10 x 9 · WALL 2 · R20",
            (0.0, -18.5, -119.8),
            1.15,
            overlay_white,
        ),
        add_camera_text(
            hero_camera,
            "HeroGateBoundary",
            "WHITE MODEL ONLY · GATE 06 FULL VALIDATION DEFERRED",
            (0.0, -21.5, -119.8),
            0.92,
            overlay_red,
        ),
    ]
    render(scene, hero_camera, ROOT / "blockout-hero.png", (1800, 1400))
    for obj in overlay_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    render(scene, front_camera, ROOT / "blockout-front.png", (1200, 1600))
    ground.hide_render = True
    backdrop.hide_render = True
    render(scene, side_camera, ROOT / "blockout-side.png", (1200, 1600))
    render(scene, rear_camera, ROOT / "blockout-rear.png", (1200, 1600))
    ground.hide_render = False
    backdrop.hide_render = False

    isolated = [rear_shell, tactile_insert, front_shell, physical_label]
    for obj in isolated:
        obj.hide_render = True
    render(scene, tube_camera, ROOT / "blockout-tube-closeup.png", (1600, 1200))
    for obj in isolated:
        obj.hide_render = False

    build_contact_sheet([
        ("FRONT · PORTRAIT + LABEL ZONE", ROOT / "blockout-front.png"),
        ("SIDE · 59 MM DEPTH", ROOT / "blockout-side.png"),
        ("REAR · SHELL ENVELOPE", ROOT / "blockout-rear.png"),
        ("TUBE CORNER · ONE CYCLIC MESH", ROOT / "blockout-tube-closeup.png"),
    ])

    scene.camera = hero_camera
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    report = VALIDATION.validate_scene()
    VALIDATION.REPORT_PATH.write_text(
        __import__("json").dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(__import__("json").dumps({
        "blend": str(BLEND_PATH),
        "hero": str(ROOT / "blockout-hero.png"),
        "contactSheet": str(ROOT / "blockout-contact-sheet.png"),
        "validationStatus": report["status"],
        "dimensionsMm": report["dimensionsMm"]["measured"],
        "tubeTopology": report["closedTube"]["topology"],
    }, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(__import__("json").dumps(report["checks"], indent=2))


if __name__ == "__main__":
    main()
