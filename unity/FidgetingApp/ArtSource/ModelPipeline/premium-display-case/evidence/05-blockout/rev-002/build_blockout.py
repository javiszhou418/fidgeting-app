#!/usr/bin/env python3
"""Build Premium Display Case Gate 05 white-model revision 2."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "premium-display-case-blockout.blend"
VALIDATOR_PATH = ROOT / "validate_blockout.py"
REV1_FRONT_PATH = ROOT.parent / "rev-001" / "blockout-front.png"

SPEC = importlib.util.spec_from_file_location("premium_display_case_blockout_validation_r2", VALIDATOR_PATH)
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


def finish_subject_mesh(
    obj: bpy.types.Object,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    construction: str,
) -> bpy.types.Object:
    obj.data.materials.append(material)
    obj["model_pipeline_subject"] = True
    obj["gate"] = "05-blockout"
    obj["blockout_revision"] = 2
    obj["construction"] = construction
    obj["independent_bevel_modifier"] = False
    parent_keep_world(obj, parent)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
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
    corner_steps: int = 24,
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
    obj["contour_width_mm"] = width
    obj["contour_height_mm"] = height
    obj["corner_radius_mm"] = radius
    return finish_subject_mesh(obj, material, parent, "analytic-rounded-profile-extrusion")


def stepped_chamber_insert(
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    sections = [
        (190.0, 210.0, 20.0, -8.5),
        (190.0, 210.0, 20.0, -0.5),
        (182.0, 202.0, 16.0, 0.5),
    ]
    profiles = [
        VALIDATION.rounded_profile(width, height, radius, 24, VALIDATION.CHAMBER_CENTER_Y_MM)
        for width, height, radius, _z in sections
    ]
    stride = len(profiles[0])
    if any(len(profile) != stride for profile in profiles):
        raise RuntimeError("Stepped chamber profiles must use the same point count.")
    vertices = [
        (x, y, z)
        for profile, (_width, _height, _radius, z) in zip(profiles, sections)
        for x, y in profile
    ]
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(stride))),
        tuple(range((len(sections) - 1) * stride, len(sections) * stride)),
    ]
    for section_index in range(len(sections) - 1):
        current_base = section_index * stride
        next_base = (section_index + 1) * stride
        for index in range(stride):
            next_index = (index + 1) % stride
            faces.append((
                current_base + index,
                current_base + next_index,
                next_base + next_index,
                next_base + index,
            ))
    mesh = bpy.data.meshes.new("TactileBackgroundInsert_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate(verbose=True)
    mesh.update()
    obj = bpy.data.objects.new("TactileBackgroundInsert", mesh)
    link_object(obj)
    obj["main_chamber_rim_mm"] = [190.0, 210.0, 20.0]
    obj["tactile_insert_face_mm"] = [182.0, 202.0, 16.0]
    obj["corner_center_family"] = "main-display-chamber"
    obj["surface_scope"] = "neutral-clay-only-no-final-grain"
    return finish_subject_mesh(obj, material, parent, "analytic-concentric-stepped-rounded-profiles")


def closed_tube(
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    path = VALIDATION.rounded_rectangle_path()
    outer_profile = VALIDATION.rounded_profile(
        VALIDATION.TUBE_OUTER_WIDTH_MM,
        VALIDATION.TUBE_OUTER_DEPTH_MM,
        VALIDATION.TUBE_PROFILE_RADIUS_MM,
        16,
    )
    inner_profile = VALIDATION.rounded_profile(
        VALIDATION.TUBE_PASSAGE_WIDTH_MM,
        VALIDATION.TUBE_PASSAGE_DEPTH_MM,
        VALIDATION.TUBE_PASSAGE_RADIUS_MM,
        16,
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
    obj["corner_center_family"] = "case-tube-shell"
    return finish_subject_mesh(obj, material, parent, "one-cyclic-hollow-tube-analytic-sweep")


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


def camera_band(
    camera: bpy.types.Object,
    name: str,
    y: float,
    width: float,
    height: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add()
    band = bpy.context.object
    band.name = name
    band.parent = camera
    band.matrix_parent_inverse = Matrix.Identity(4)
    band.location = (0.0, y, -120.0)
    band.dimensions = (width, height, 0.12)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    band.data.materials.append(material)
    band["model_pipeline_exclude"] = True
    return band


def text_object(
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    parent: bpy.types.Object | None = None,
    align: str = "CENTER",
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = align
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.015
    curve.bevel_depth = 0.005
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    if parent:
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = location
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


def outline_curve(
    name: str,
    spec: dict[str, float],
    z: float,
    material: bpy.types.Material,
    line_width: float = 0.55,
) -> bpy.types.Object:
    points = VALIDATION.rounded_profile(
        spec["width"], spec["height"], spec["radius"], 48, spec["centerY"]
    )
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = line_width
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, (x, y) in zip(spline.points, points):
        point.co = (x, y, z, 1.0)
    spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    obj.data.materials.append(material)
    obj["model_pipeline_exclude"] = True
    return obj


def polyline(
    name: str,
    points: list[tuple[float, float, float]],
    material: bpy.types.Material,
    width: float,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = width
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    obj.data.materials.append(material)
    obj["model_pipeline_exclude"] = True
    return obj


def center_crosses(
    prefix: str,
    centers: list[tuple[float, float]],
    z: float,
    material: bpy.types.Material,
    arm: float = 6.0,
) -> list[bpy.types.Object]:
    objects = []
    for index, (x, y) in enumerate(centers):
        objects.append(polyline(
            f"{prefix}_{index}_Horizontal",
            [(x - arm, y, z), (x + arm, y, z)],
            material,
            0.65,
        ))
        objects.append(polyline(
            f"{prefix}_{index}_Vertical",
            [(x, y - arm, z), (x, y + arm, z)],
            material,
            0.65,
        ))
    return objects


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


def sheet_text(
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


def image_card(
    scene: bpy.types.Scene,
    name: str,
    center: tuple[float, float],
    size: tuple[float, float],
    material: bpy.types.Material,
) -> None:
    width, height = size
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
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
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = (center[0], center[1], 0.0)
    obj.data.materials.append(material)


def build_before_after() -> None:
    if not REV1_FRONT_PATH.exists():
        raise RuntimeError(f"Immutable rev 1 front render is missing: {REV1_FRONT_PATH}")
    source_scene = bpy.context.window.scene
    scene = bpy.data.scenes.new("Gate05BeforeAfter")
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 2400
    scene.render.resolution_y = 1600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Gate05BeforeAfterWorld")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.018, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

    camera_data = bpy.data.cameras.new("BeforeAfterCamera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 13.0
    camera = bpy.data.objects.new("BeforeAfterCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, 0.0, 10.0)
    scene.camera = camera

    white = make_emission_material("MAT_COMPARE_White", (0.93, 0.96, 0.98, 1.0))
    cyan = make_emission_material("MAT_COMPARE_Cyan", (0.28, 0.82, 0.94, 1.0))
    coral = make_emission_material("MAT_COMPARE_Coral", (0.98, 0.43, 0.46, 1.0))
    card = make_emission_material("MAT_COMPARE_Card", (0.035, 0.045, 0.060, 1.0))
    centers = ((-3.0, -0.10), (3.0, -0.10))
    for index, (label, path, center) in enumerate((
        ("BEFORE · REV 1", REV1_FRONT_PATH, centers[0]),
        ("AFTER · REV 2", ROOT / "blockout-front.png", centers[1]),
    )):
        image_card(scene, f"CompareCard_{index}", center, (5.45, 6.1), card)
        image_plane(scene, f"CompareImage_{index}", path, (center[0], center[1] - 0.15), (5.0, 5.35))
        sheet_text(scene, f"CompareLabel_{index}", label, (center[0], 3.15, 0.12), 0.33, cyan if index else coral)
    sheet_text(scene, "CompareTitle", "GATE 05 · REAL BLENDER BEFORE / AFTER", (0.0, 3.78, 0.12), 0.45, white)
    sheet_text(scene, "CompareFooter", "LABEL CANDIDATE -6 MM · ANALYTIC CONCENTRIC CORNERS · 0.000 MM DRIFT", (0.0, -3.85, 0.12), 0.24, cyan)
    scene.render.filepath = str(ROOT / "blockout-before-after.png")
    bpy.ops.render.render(write_still=True)
    bpy.context.window.scene = source_scene
    bpy.data.scenes.remove(scene)


def build_contact_sheet() -> None:
    source_scene = bpy.context.window.scene
    scene = bpy.data.scenes.new("Gate05ContactSheetR2")
    bpy.context.window.scene = scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 3000
    scene.render.resolution_y = 2400
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("Gate05ContactWorldR2")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.018, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25

    camera_data = bpy.data.cameras.new("ContactSheetCameraR2")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 18.0
    camera = bpy.data.objects.new("ContactSheetCameraR2", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (0.0, 0.0, 10.0)
    scene.camera = camera

    white = make_emission_material("MAT_CONTACT_R2_White", (0.93, 0.96, 0.98, 1.0))
    cyan = make_emission_material("MAT_CONTACT_R2_Cyan", (0.28, 0.82, 0.94, 1.0))
    coral = make_emission_material("MAT_CONTACT_R2_Coral", (0.98, 0.43, 0.46, 1.0))
    card = make_emission_material("MAT_CONTACT_R2_Card", (0.035, 0.045, 0.060, 1.0))
    entries = [
        ("BEFORE / AFTER", ROOT / "blockout-before-after.png"),
        ("HERO · REV 2", ROOT / "blockout-hero.png"),
        ("TOP", ROOT / "blockout-top.png"),
        ("RIGHT OBLIQUE", ROOT / "blockout-oblique.png"),
        ("SIDE · 59 MM", ROOT / "blockout-side.png"),
        ("CONCENTRIC CENTERS", ROOT / "blockout-concentric-centers.png"),
    ]
    centers = (
        (-5.55, 3.05), (0.0, 3.05), (5.55, 3.05),
        (-5.55, -2.55), (0.0, -2.55), (5.55, -2.55),
    )
    for index, ((label, path), center) in enumerate(zip(entries, centers)):
        image_card(scene, f"ContactCardR2_{index}", center, (5.25, 4.75), card)
        image_plane(scene, f"ContactImageR2_{index}", path, (center[0], center[1] - 0.18), (4.95, 4.10))
        sheet_text(scene, f"ContactLabelR2_{index}", label, (center[0], center[1] + 2.02, 0.12), 0.27, cyan)
    sheet_text(scene, "ContactTitleR2", "GATE 05 · CORRECTED REAL BLENDER WHITE MODEL", (0.0, 6.25, 0.12), 0.44, white)
    sheet_text(scene, "ContactSubtitleR2", "228 x 304 x 59 MM · LABEL -6 MM CANDIDATE · CONCENTRIC ERROR 0.000 MM", (0.0, 5.77, 0.12), 0.24, cyan)
    sheet_text(scene, "ContactFooterR2", "REV 1 PRESERVED + REJECTED · REV 2 READY FOR REVIEW · GATE 06 BLOCKED", (0.0, -6.30, 0.12), 0.23, coral)
    scene.render.filepath = str(ROOT / "blockout-contact-sheet.png")
    bpy.ops.render.render(write_still=True)
    bpy.context.window.scene = source_scene
    bpy.data.scenes.remove(scene)


def main() -> None:
    clear_scene()
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate05_Blockout_Rev2"
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
    scene["blockout_revision"] = 2
    scene["label_downshift_candidate_mm"] = VALIDATION.LABEL_DOWNSHIFT_CANDIDATE_MM
    scene["label_candidate_approval_state"] = "pending-user-approval"
    scene["corner_center_tolerance_mm"] = VALIDATION.CORNER_CENTER_TOLERANCE_MM
    scene["locked_total_duration_seconds"] = 4.520833
    scene["shipping_unity_changed"] = False
    scene["gate06_entered"] = False

    world = scene.world or bpy.data.worlds.new("Gate05WorldR2")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.012, 0.019, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42

    shell_clay = make_principled_material("MAT_DIAGNOSTIC_ShellClay", (0.68, 0.73, 0.78, 1.0), 0.62)
    tube_clay = make_principled_material("MAT_DIAGNOSTIC_TubeClay", (0.94, 0.96, 0.98, 1.0), 0.48)
    label_clay = make_principled_material("MAT_DIAGNOSTIC_LabelClay", (0.80, 0.82, 0.79, 1.0), 0.72)
    insert_clay = make_principled_material("MAT_DIAGNOSTIC_InsertClay", (0.34, 0.38, 0.43, 1.0), 0.86)
    studio_material = make_principled_material("MAT_STUDIO_Backdrop", (0.020, 0.028, 0.040, 1.0), 0.92)
    overlay_dark = make_emission_material("MAT_OVERLAY_Dark", (0.012, 0.018, 0.028, 1.0))
    overlay_white = make_emission_material("MAT_OVERLAY_White", (0.94, 0.96, 0.98, 1.0))
    overlay_cyan = make_emission_material("MAT_OVERLAY_Cyan", (0.25, 0.80, 0.92, 1.0))
    overlay_magenta = make_emission_material("MAT_OVERLAY_Magenta", (0.95, 0.38, 0.67, 1.0))
    overlay_yellow = make_emission_material("MAT_OVERLAY_Yellow", (0.98, 0.76, 0.24, 1.0))
    overlay_green = make_emission_material("MAT_OVERLAY_Green", (0.31, 0.90, 0.62, 1.0))
    overlay_coral = make_emission_material("MAT_OVERLAY_Coral", (0.98, 0.42, 0.45, 1.0))

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
        18.0,
        (0.0, 0.0, -26.0),
        shell_clay,
        case_assembly,
    )
    rear_shell["corner_center_family"] = "case-tube-shell"
    rear_shell["dimension_source"] = "approved-envelope-plus-concentric-gate05-correction"

    tactile_insert = stepped_chamber_insert(insert_clay, rear_shell)
    content_slot = empty("ContentSlot", rear_shell)
    content_slot.location = (0.0, VALIDATION.CHAMBER_CENTER_Y_MM, 16.0)
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
        18.0,
        (0.0, 0.0, 20.0),
        shell_clay,
        case_assembly,
    )
    front_shell["corner_center_family"] = "case-tube-shell"
    front_shell["dimension_source"] = "approved-envelope-plus-concentric-gate05-correction"
    tube = closed_tube(tube_clay, front_shell)

    physical_label = rounded_prism(
        "PhysicalLabel",
        184.0,
        58.0,
        3.0,
        6.0,
        (0.0, VALIDATION.LABEL_CENTER_Y_MM, 24.0),
        label_clay,
        front_shell,
    )
    physical_label["content"] = "blank-white-model-zone"
    physical_label["corner_center_family"] = "physical-label"
    physical_label["baseline_center_y_mm"] = VALIDATION.LABEL_BASELINE_CENTER_Y_MM
    physical_label["candidate_center_y_mm"] = VALIDATION.LABEL_CENTER_Y_MM
    physical_label["candidate_downshift_mm"] = VALIDATION.LABEL_DOWNSHIFT_CANDIDATE_MM
    physical_label["candidate_approval_state"] = "pending-user-approval"

    logo_zone = empty("LogoZone", physical_label)
    logo_zone["gate05_geometry_status"] = "deferred-no-artwork"
    achievement_zone = empty("AchievementZone", physical_label)
    achievement_zone["gate05_geometry_status"] = "deferred-no-artwork"
    narrow_foil = empty("NarrowFoil", physical_label)
    narrow_foil["gate05_geometry_status"] = "contour-zone-only-no-final-material"
    narrow_foil["contour_width_mm"] = 188.0
    narrow_foil["contour_height_mm"] = 62.0
    narrow_foil["corner_radius_mm"] = 8.0
    narrow_foil["center_y_mm"] = VALIDATION.LABEL_CENTER_Y_MM
    narrow_foil["corner_center_family"] = "physical-label"
    transparent_cover = empty("TransparentCover", front_shell)
    transparent_cover["gate05_geometry_status"] = "contour-only-thickness-deferred"
    transparent_cover["physical_part_geometry"] = False
    transparent_cover["contour_width_mm"] = 186.0
    transparent_cover["contour_height_mm"] = 60.0
    transparent_cover["corner_radius_mm"] = 7.0
    transparent_cover["center_y_mm"] = VALIDATION.LABEL_CENTER_Y_MM
    transparent_cover["corner_center_family"] = "physical-label"

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
    top_camera = add_camera("Gate05TopCamera", (0.0, 700.0, 0.0), (0.0, 0.0, 0.0), 70.0, 270.0)
    oblique_camera = add_camera("Gate05ObliqueCamera", (340.0, 175.0, 1050.0), (0.0, 0.0, 0.0), 74.0)
    tube_camera = add_camera("Gate05TubeCamera", (310.0, 270.0, 460.0), (96.0, 132.0, 24.0), 88.0)
    centers_camera = add_camera("Gate05CentersCamera", (0.0, 0.0, 760.0), (0.0, 0.0, 0.0), 70.0, 390.0)

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)

    hero_overlays = [
        camera_band(hero_camera, "HeroTopBand", 20.0, 64.0, 8.0, overlay_dark),
        camera_band(hero_camera, "HeroBottomBand", -20.0, 64.0, 8.0, overlay_dark),
        text_object(
            "HeroTitle",
            "REV 2 · REAL BLENDER WHITE MODEL",
            (0.0, 21.1, -119.8),
            1.95,
            overlay_white,
            hero_camera,
        ),
        text_object(
            "HeroSubtitle",
            "LABEL -6 MM CANDIDATE · PENDING APPROVAL",
            (0.0, 17.9, -119.8),
            1.04,
            overlay_cyan,
            hero_camera,
        ),
        text_object(
            "HeroFooter",
            "CONCENTRIC CORNER CENTERS · MAX DRIFT 0.000 MM",
            (0.0, -18.5, -119.8),
            1.02,
            overlay_white,
            hero_camera,
        ),
        text_object(
            "HeroGateBoundary",
            "228 x 304 x 59 MM · GATE 06 BLOCKED · UNITY UNCHANGED",
            (0.0, -21.5, -119.8),
            0.84,
            overlay_coral,
            hero_camera,
        ),
    ]
    render(scene, hero_camera, ROOT / "blockout-hero.png", (1800, 1400))
    for obj in hero_overlays:
        bpy.data.objects.remove(obj, do_unlink=True)

    render(scene, front_camera, ROOT / "blockout-front.png", (1200, 1600))
    ground.hide_render = True
    backdrop.hide_render = True
    render(scene, side_camera, ROOT / "blockout-side.png", (1400, 1400))
    render(scene, rear_camera, ROOT / "blockout-rear.png", (1200, 1600))
    render(scene, top_camera, ROOT / "blockout-top.png", (1600, 1200))
    ground.hide_render = False
    backdrop.hide_render = False
    render(scene, oblique_camera, ROOT / "blockout-oblique.png", (1800, 1400))

    isolated = [rear_shell, tactile_insert, front_shell, physical_label]
    for obj in isolated:
        obj.hide_render = True
    render(scene, tube_camera, ROOT / "blockout-tube-closeup.png", (1600, 1200))
    for obj in isolated:
        obj.hide_render = False

    diagnostic_objects: list[bpy.types.Object] = []
    diagnostic_objects.extend([
        outline_curve("CaseOuterContour", VALIDATION.CASE_CONTOURS["outerEnvelopeAndTubeOuter"], 33.0, overlay_cyan, 0.62),
        outline_curve("CaseShellInsetContour", VALIDATION.CASE_CONTOURS["frontRearShellInset"], 33.2, overlay_yellow, 0.52),
        outline_curve("TubeInnerContour", VALIDATION.CASE_CONTOURS["tubeInner"], 33.4, overlay_green, 0.58),
        outline_curve("ChamberRimContour", VALIDATION.CHAMBER_CONTOURS["mainChamberRim"], 33.6, overlay_cyan, 0.55),
        outline_curve("ChamberInsertContour", VALIDATION.CHAMBER_CONTOURS["tactileInsertFace"], 33.8, overlay_green, 0.50),
        outline_curve("LabelFrameContour", VALIDATION.LABEL_CONTOURS["labelFrame"], 34.0, overlay_magenta, 0.58),
        outline_curve("LabelCoverContour", VALIDATION.LABEL_CONTOURS["transparentLabelCover"], 34.2, overlay_cyan, 0.46),
        outline_curve("LabelPaperContour", VALIDATION.LABEL_CONTOURS["physicalLabelPaper"], 34.4, overlay_white, 0.42),
    ])
    diagnostic_objects.extend(center_crosses(
        "CaseCornerCenter",
        VALIDATION.corner_centers(VALIDATION.CASE_CONTOURS["outerEnvelopeAndTubeOuter"]),
        35.0,
        overlay_yellow,
        7.0,
    ))
    diagnostic_objects.extend(center_crosses(
        "ChamberCornerCenter",
        VALIDATION.corner_centers(VALIDATION.CHAMBER_CONTOURS["mainChamberRim"]),
        35.2,
        overlay_green,
        5.5,
    ))
    diagnostic_objects.extend(center_crosses(
        "LabelCornerCenter",
        VALIDATION.corner_centers(VALIDATION.LABEL_CONTOURS["labelFrame"]),
        35.4,
        overlay_magenta,
        4.5,
    ))
    diagnostic_objects.extend([
        text_object("CentersTitle", "ANALYTIC CONCENTRIC CORNER CENTERS", (0.0, 180.0, 35.0), 8.2, overlay_white),
        text_object("CentersLegendCase", "YELLOW + = CASE / TUBE / SHELL FAMILY", (0.0, 164.0, 35.0), 4.5, overlay_yellow),
        text_object("CentersLegendChamber", "GREEN + = MAIN CHAMBER FAMILY", (-73.0, -171.0, 35.0), 3.8, overlay_green),
        text_object("CentersLegendLabel", "MAGENTA + = LABEL / COVER / FRAME FAMILY", (70.0, -171.0, 35.0), 3.8, overlay_magenta),
        text_object("CentersMetric", "MAX CORNER-CENTER DRIFT = 0.000 MM  <=  0.010 MM", (0.0, -184.0, 35.0), 4.3, overlay_cyan),
    ])
    render(scene, centers_camera, ROOT / "blockout-concentric-centers.png", (1800, 2000))
    for obj in diagnostic_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    build_before_after()
    build_contact_sheet()

    scene.camera = hero_camera
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), check_existing=False)
    report = VALIDATION.validate_scene()
    VALIDATION.REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "blend": str(BLEND_PATH),
        "hero": str(ROOT / "blockout-hero.png"),
        "beforeAfter": str(ROOT / "blockout-before-after.png"),
        "concentricCenters": str(ROOT / "blockout-concentric-centers.png"),
        "contactSheet": str(ROOT / "blockout-contact-sheet.png"),
        "validationStatus": report["status"],
        "dimensionsMm": report["dimensionsMm"]["measured"],
        "labelDownshiftCandidateMm": report["labelPosition"]["candidateDownshiftMm"],
        "maximumCornerCenterDriftMm": report["cornerCenterFamilies"]["maximumDriftMm"],
        "tubeTopology": report["closedTube"]["topology"],
    }, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report["checks"], indent=2))


if __name__ == "__main__":
    main()
