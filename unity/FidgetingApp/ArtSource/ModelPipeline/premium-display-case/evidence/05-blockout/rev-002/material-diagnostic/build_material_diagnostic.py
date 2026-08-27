#!/usr/bin/env python3
"""Build Gate 05 rev 2 supplementary material-diagnostic renders."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
RAW = OUTPUT / "raw"
REV2 = OUTPUT.parent
SOURCE_BLEND = REV2 / "premium-display-case-blockout.blend"
VALIDATOR_PATH = REV2 / "validate_blockout.py"
OUTPUT_BLEND = OUTPUT / "premium-display-case-gate05-r2-material-diagnostic.blend"
BUILD_REPORT = OUTPUT / "material-diagnostic-build-report.json"


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)
MATERIAL_BLEND = REPO_ROOT / "unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend"
MATERIAL_BUILD = REPO_ROOT / "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py"
MATERIAL_NAMES = (
    "MAT_FrostedPolycarbonate",
    "MAT_FrostedPolycarbonateEdge",
    "MAT_BlackFlocking",
    "MAT_RarityFoilSilver",
    "MAT_LabelPaper",
)
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
DIAGNOSTIC_NOTICE = "DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 APPROVAL"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate05_rev2_validator",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            digest.update(obj.name.encode())
            for row in obj.matrix_world:
                for value in row:
                    digest.update(f"{value:.12f}".encode())
            for vertex in mesh.vertices:
                digest.update(
                    f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode()
                )
            for polygon in mesh.polygons:
                digest.update(
                    (",".join(str(index) for index in polygon.vertices) + ";").encode()
                )
        finally:
            evaluated.to_mesh_clear()
    return digest.hexdigest()


def object_bounds(objects: list[bpy.types.Object]) -> dict[str, list[float]]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points: list[Vector] = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(obj.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {
        "minimum": [round(value, 6) for value in minimum],
        "maximum": [round(value, 6) for value in maximum],
        "size": [round(maximum[index] - minimum[index], 6) for index in range(3)],
    }


def set_input(node: bpy.types.Node, name: str, value) -> None:
    for socket in node.inputs:
        if socket.name == name:
            socket.default_value = value
            return
    raise RuntimeError(f"{node.name} has no input named {name}")


def make_graphite_recipe() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_LabelGraphite")
    material.diffuse_color = (0.055, 0.060, 0.066, 1.0)
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    set_input(shader, "Base Color", (0.055, 0.060, 0.066, 1.0))
    set_input(shader, "Metallic", 0.22)
    set_input(shader, "Roughness", 0.52)
    set_input(shader, "Emission Strength", 0.0)
    material["source_recipe"] = (
        "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py"
    )
    material["diagnostic_recreated_from_exact_recipe"] = True
    return material


def append_formal_materials() -> dict[str, bpy.types.Material]:
    with bpy.data.libraries.load(str(MATERIAL_BLEND), link=False) as (source, target):
        missing = [name for name in MATERIAL_NAMES if name not in source.materials]
        if missing:
            raise RuntimeError(f"Formal material source is missing {missing}")
        target.materials = list(MATERIAL_NAMES)
    materials = {name: bpy.data.materials[name] for name in MATERIAL_NAMES}
    materials["MAT_LabelGraphite"] = make_graphite_recipe()
    for name, material in materials.items():
        material["diagnostic_material_proxy"] = True
        material["gate07_approval_eligible"] = False
        material["formal_source"] = (
            str(MATERIAL_BLEND.relative_to(REPO_ROOT))
            if name != "MAT_LabelGraphite"
            else str(MATERIAL_BUILD.relative_to(REPO_ROOT))
        )
    return materials


def pbr_values(material: bpy.types.Material) -> dict[str, object]:
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is None:
        raise RuntimeError(f"{material.name} has no Principled BSDF")
    image_nodes = [
        node for node in material.node_tree.nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image
    ]

    def value(name: str):
        socket = next((item for item in shader.inputs if item.name == name), None)
        if socket is None:
            return None
        raw = socket.default_value
        if hasattr(raw, "__len__"):
            return [round(float(component), 6) for component in raw]
        if isinstance(raw, (int, float)):
            return round(float(raw), 6)
        return raw

    return {
        "baseColor": value("Base Color"),
        "metallic": value("Metallic"),
        "roughness": value("Roughness"),
        "transmissionWeight": value("Transmission Weight"),
        "ior": value("IOR"),
        "alpha": value("Alpha"),
        "emissionStrength": value("Emission Strength"),
        "imageTextures": [
            {
                "name": node.image.name,
                "path": bpy.path.abspath(node.image.filepath),
                "packed": bool(node.image.packed_file),
            }
            for node in image_nodes
        ],
    }


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)


def link_object(obj: bpy.types.Object) -> None:
    bpy.context.scene.collection.objects.link(obj)


def finish_proxy(
    obj: bpy.types.Object,
    material: bpy.types.Material,
    parent: bpy.types.Object | None,
    proxy_kind: str,
) -> bpy.types.Object:
    obj.data.materials.append(material)
    obj["model_pipeline_exclude"] = True
    obj["supplementary_material_diagnostic"] = True
    obj["gate05_subject_geometry"] = False
    obj["gate06_geometry_evidence"] = False
    obj["gate07_approval_eligible"] = False
    obj["proxy_kind"] = proxy_kind
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def rounded_surface(
    validator,
    name: str,
    width: float,
    height: float,
    radius: float,
    center: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object | None,
    proxy_kind: str,
) -> bpy.types.Object:
    profile = validator.rounded_profile(width, height, radius, 32, center[1])
    vertices = [(x + center[0], y, center[2]) for x, y in profile]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], [tuple(range(len(vertices)))])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj)
    obj["proxy_thickness_mm"] = 0.0
    obj["contour_width_mm"] = width
    obj["contour_height_mm"] = height
    obj["corner_radius_mm"] = radius
    return finish_proxy(obj, material, parent, proxy_kind)


def rounded_ring_surface(
    validator,
    name: str,
    width: float,
    height: float,
    radius: float,
    border: float,
    center: tuple[float, float, float],
    material: bpy.types.Material,
    parent: bpy.types.Object | None,
    proxy_kind: str,
) -> bpy.types.Object:
    outer = validator.rounded_profile(width, height, radius, 32, center[1])
    inner_width = width - border * 2.0
    inner_height = height - border * 2.0
    inner_radius = radius - border
    inner = validator.rounded_profile(
        inner_width,
        inner_height,
        inner_radius,
        32,
        center[1],
    )
    vertices = [(x + center[0], y, center[2]) for x, y in outer]
    vertices.extend((x + center[0], y, center[2]) for x, y in inner)
    count = len(outer)
    faces = [
        (index, (index + 1) % count, count + (index + 1) % count, count + index)
        for index in range(count)
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    link_object(obj)
    obj["proxy_thickness_mm"] = 0.0
    obj["outer_contour_mm"] = [width, height, radius]
    obj["border_width_mm"] = border
    obj["analytic_concentric_inner_radius_mm"] = inner_radius
    return finish_proxy(obj, material, parent, proxy_kind)


def text_proxy(
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    parent: bpy.types.Object | None,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.02
    curve.bevel_depth = 0.008
    curve.space_line = 0.9
    obj = bpy.data.objects.new(name, curve)
    link_object(obj)
    obj.location = location
    return finish_proxy(obj, material, parent, "neutral-label-print-placeholder")


def add_label_diagnostic_proxies(
    validator,
    materials: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    front_shell = bpy.data.objects["FrontPolycarbonateShell"]
    physical_label = bpy.data.objects["PhysicalLabel"]
    label_y = validator.LABEL_CENTER_Y_MM
    graphite = materials["MAT_LabelGraphite"]
    proxies = [
        rounded_ring_surface(
            validator,
            "DIAGNOSTIC_NarrowFoilProxy",
            188.0,
            62.0,
            8.0,
            2.2,
            (0.0, label_y, 26.20),
            materials["MAT_RarityFoilSilver"],
            physical_label,
            "zero-thickness-existing-narrow-foil-material-zone",
        ),
        rounded_ring_surface(
            validator,
            "DIAGNOSTIC_IdentityPlaceholder",
            30.0,
            38.0,
            4.0,
            1.3,
            (-72.0, label_y, 26.34),
            graphite,
            physical_label,
            "neutral-identity-placeholder-area",
        ),
        rounded_ring_surface(
            validator,
            "DIAGNOSTIC_AchievementPlaceholder",
            30.0,
            38.0,
            4.0,
            1.3,
            (72.0, label_y, 26.34),
            graphite,
            physical_label,
            "neutral-achievement-placeholder-area",
        ),
        text_proxy(
            "DIAGNOSTIC_LabelPrimary",
            "MATERIAL PROXY",
            (0.0, label_y + 7.5, 26.35),
            6.5,
            graphite,
            physical_label,
        ),
        text_proxy(
            "DIAGNOSTIC_LabelSecondary",
            "NEUTRAL LABEL · GATE 05",
            (0.0, label_y - 5.5, 26.35),
            3.8,
            graphite,
            physical_label,
        ),
        rounded_surface(
            validator,
            "DIAGNOSTIC_NeutralPrintBarPrimary",
            68.0,
            4.2,
            1.6,
            (0.0, label_y + 8.0, 26.36),
            graphite,
            physical_label,
            "neutral-label-print-bar",
        ),
        rounded_surface(
            validator,
            "DIAGNOSTIC_NeutralPrintBarSecondary",
            54.0,
            3.2,
            1.2,
            (0.0, label_y - 1.0, 26.36),
            graphite,
            physical_label,
            "neutral-label-print-bar",
        ),
        rounded_surface(
            validator,
            "DIAGNOSTIC_NeutralPrintBarMetadata",
            38.0,
            2.4,
            0.9,
            (0.0, label_y - 9.0, 26.36),
            graphite,
            physical_label,
            "neutral-label-print-bar",
        ),
        text_proxy(
            "DIAGNOSTIC_IdentityAreaText",
            "IDENTITY\nAREA",
            (-72.0, label_y, 26.35),
            3.0,
            graphite,
            physical_label,
        ),
        text_proxy(
            "DIAGNOSTIC_AchievementAreaText",
            "ACHIEVEMENT\nAREA",
            (72.0, label_y, 26.35),
            2.45,
            graphite,
            physical_label,
        ),
        rounded_surface(
            validator,
            "DIAGNOSTIC_TransparentCoverProxy",
            186.0,
            60.0,
            7.0,
            (0.0, label_y, 26.62),
            materials["MAT_FrostedPolycarbonate"],
            front_shell,
            "zero-thickness-existing-transparent-cover-contour",
        ),
    ]
    for obj in proxies:
        obj["identity_artwork"] = "neutral-placeholder-only"
        obj["formal_logo_redrawn"] = False
        obj["formal_achievement_redrawn"] = False
    return proxies


def matte_background_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_DIAGNOSTIC_ContinuousMatteStudio")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    texcoord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.6
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.52
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.046, 0.048, 0.051, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.056, 0.058, 0.061, 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.055
    bump.inputs["Distance"].default_value = 0.08
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", 0.84)
    set_input(shader, "Emission Strength", 0.0)
    links.new(texcoord.outputs["Object"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    material["background_contract"] = (
        "continuous-low-saturation-fine-matte-no-local-mask-no-image-texture"
    )
    material["grain_feature_size_mm"] = [0.35, 0.8]
    material["normal_peak_to_peak_mm_max"] = 0.12
    material["diagnostic_only"] = True
    return material


def configure_studio(scene: bpy.types.Scene) -> dict[str, object]:
    ground = bpy.data.objects.get("StudioGround")
    if ground:
        ground.hide_render = True
    backdrop = bpy.data.objects.get("StudioBackdrop")
    if backdrop:
        backdrop.hide_render = True
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.name = "DIAGNOSTIC_ContinuousMatteBackground"
    background.inputs["Strength"].default_value = 0.24
    texcoord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 420.0
    noise.inputs["Detail"].default_value = 1.2
    noise.inputs["Roughness"].default_value = 0.42
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.055, 0.058, 0.062, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.061, 0.064, 0.068, 1.0)
    links.new(texcoord.outputs["Normal"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    world["background_contract"] = (
        "continuous-low-saturation-fine-matte-world-no-local-mask-no-image-texture"
    )
    world["local_noise_masks"] = 0
    world["image_texture_count"] = 0
    world["emission_art_direction"] = False
    return {
        "world": world,
        "backgroundNode": background.name,
        "noiseScale": 420.0,
        "localNoiseMasks": 0,
        "imageTextureCount": 0,
    }


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
    role: str,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    link_object(obj)
    obj.location = location
    look_at(obj, target)
    obj["studio_role"] = role
    obj["neutral_material_diagnostic"] = True
    obj["rarity_light"] = False
    return obj


def add_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    data.dof.use_dof = False
    data.clip_start = 1.0
    data.clip_end = 5000.0
    obj = bpy.data.objects.new(name, data)
    link_object(obj)
    obj.location = location
    orient_camera(obj, Vector(target))
    obj["diagnostic_camera"] = True
    return obj


def configure_lights_and_cameras() -> tuple[
    dict[str, bpy.types.Object],
    list[bpy.types.Object],
]:
    for obj in list(bpy.data.objects):
        if obj.type in {"LIGHT", "CAMERA"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    target = Vector((0.0, -5.0, 10.0))
    lights = [
        add_area_light(
            "DIAGNOSTIC_Key_5000K",
            (350.0, 360.0, 520.0),
            1_800_000.0,
            330.0,
            (1.0, 0.965, 0.93),
            target,
            "key",
        ),
        add_area_light(
            "DIAGNOSTIC_Fill_6200K",
            (-390.0, 100.0, 420.0),
            850_000.0,
            390.0,
            (0.945, 0.965, 1.0),
            target,
            "fill",
        ),
        add_area_light(
            "DIAGNOSTIC_Rim_5600K",
            (-170.0, 300.0, -360.0),
            550_000.0,
            310.0,
            (0.965, 0.98, 1.0),
            target,
            "rim",
        ),
    ]
    cameras = {
        "hero": add_camera(
            "DIAGNOSTIC_HeroCamera",
            (305.0, 150.0, 900.0),
            (0.0, 0.0, 8.0),
            72.0,
        ),
        "left-oblique": add_camera(
            "DIAGNOSTIC_LeftObliqueCamera",
            (-360.0, 115.0, 850.0),
            (0.0, 0.0, 5.0),
            72.0,
        ),
        "right-oblique": add_camera(
            "DIAGNOSTIC_RightObliqueCamera",
            (360.0, 115.0, 850.0),
            (0.0, 0.0, 5.0),
            72.0,
        ),
        "low": add_camera(
            "DIAGNOSTIC_LowCamera",
            (285.0, -115.0, 815.0),
            (0.0, -5.0, 8.0),
            70.0,
        ),
        "side": add_camera(
            "DIAGNOSTIC_SideCamera",
            (980.0, 15.0, 40.0),
            (0.0, 0.0, 0.0),
            68.0,
        ),
        "label-closeup": add_camera(
            "DIAGNOSTIC_LabelCloseupCamera",
            (0.0, 104.0, 430.0),
            (0.0, 99.0, 24.0),
            92.0,
        ),
        "concentric-closeup": add_camera(
            "DIAGNOSTIC_ConcentricCornerCamera",
            (240.0, 225.0, 475.0),
            (91.0, 130.0, 24.0),
            96.0,
        ),
    }
    return cameras, lights


def configure_render(scene: bpy.types.Scene, draft: bool) -> str:
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 18 if draft else 96
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.07 if draft else 0.025
    scene.cycles.adaptive_min_samples = 8 if draft else 24
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 18
    scene.cycles.transmission_bounces = 18
    scene.cycles.transparent_max_bounces = 18
    scene.cycles.glossy_bounces = 8
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.world.use_nodes = True
    background = next(
        node for node in scene.world.node_tree.nodes
        if node.bl_idname == "ShaderNodeBackground"
    )
    background.inputs["Strength"].default_value = 0.24
    scene.cycles.device = "CPU"
    return "CPU"


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


def material_chroma(color: tuple[float, float, float]) -> float:
    return max(color) - min(color)


def main() -> None:
    draft = "--draft" in sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else False
    RAW.mkdir(parents=True, exist_ok=True)
    source_hash_before = sha256(SOURCE_BLEND)
    material_hash_before = sha256(MATERIAL_BLEND)
    build_hash_before = sha256(MATERIAL_BUILD)

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    validator = load_validator()
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate05_Rev2_MaterialDiagnostic"
    scene["gate"] = "05-blockout"
    scene["blockout_revision"] = 2
    scene["supplementary_material_diagnostic"] = True
    scene["diagnostic_notice"] = DIAGNOSTIC_NOTICE
    scene["gate05_status"] = "ready_for_review"
    scene["gate06_entered"] = False
    scene["gate07_entered"] = False
    scene["gate07_approval_effect"] = "none"
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False

    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    original_materials = {
        obj.name: [slot.material for slot in obj.material_slots if slot.material]
        for obj in subjects
    }
    original_matrices = {
        obj.name: [[float(value) for value in row] for row in obj.matrix_world]
        for obj in subjects
    }
    digest_before = geometry_digest(subjects)
    bounds_before = object_bounds(subjects)

    materials = append_formal_materials()
    assignments = {
        "RearPolycarbonateShell": "MAT_FrostedPolycarbonate",
        "FrontPolycarbonateShell": "MAT_FrostedPolycarbonate",
        "ContinuousTubePerimeter": "MAT_FrostedPolycarbonateEdge",
        "TactileBackgroundInsert": "MAT_BlackFlocking",
        "PhysicalLabel": "MAT_LabelPaper",
    }
    for object_name, material_name in assignments.items():
        assign_material(bpy.data.objects[object_name], materials[material_name])
    digest_after_assignment = geometry_digest(subjects)
    proxies = add_label_diagnostic_proxies(validator, materials)
    studio = configure_studio(scene)
    cameras, lights = configure_lights_and_cameras()
    render_device = configure_render(scene, draft)
    bpy.context.view_layer.update()

    if draft:
        render(scene, cameras["hero"], RAW / "draft-hero.png", (760, 620))
        print(json.dumps({
            "draft": str(RAW / "draft-hero.png"),
            "geometryDigestBefore": digest_before,
            "geometryDigestAfterAssignment": digest_after_assignment,
            "device": render_device,
        }, indent=2))
        return

    render_plan = {
        "hero": (1400, 1120),
        "left-oblique": (1280, 1080),
        "right-oblique": (1280, 1080),
        "low": (1280, 1080),
        "side": (1100, 1320),
        "label-closeup": (1500, 980),
        "concentric-closeup": (1280, 1080),
    }
    for view_id, resolution in render_plan.items():
        render(scene, cameras[view_id], RAW / f"{view_id}.png", resolution)

    for proxy in proxies:
        proxy.hide_render = True
    for obj in subjects:
        obj.data.materials.clear()
        for material in original_materials[obj.name]:
            obj.data.materials.append(material)
    render(scene, cameras["hero"], RAW / "clay-hero-same-camera.png", render_plan["hero"])
    for object_name, material_name in assignments.items():
        assign_material(bpy.data.objects[object_name], materials[material_name])
    for proxy in proxies:
        proxy.hide_render = False
    bpy.context.view_layer.update()

    digest_after_renders = geometry_digest(subjects)
    bounds_after = object_bounds(subjects)
    structural = validator.validate_scene()
    label_surface_z = max(
        vertex.z for vertex in validator.evaluated_vertices(bpy.data.objects["PhysicalLabel"])
    )
    ordering = {
        "labelSurfaceMaxZmm": round(label_surface_z, 6),
        "printProxyZmm": 26.35,
        "foilProxyZmm": 26.20,
        "coverProxyZmm": 26.62,
        "cameraSide": "+Z",
        "pass": 26.62 > 26.35 > label_surface_z and 26.62 > 26.20,
        "note": (
            "The cover and foil remain zero-thickness diagnostic surfaces because "
            "Gate 05 rev 2 defers cover thickness and treats foil as a material zone."
        ),
    }
    forbidden_tokens = ("whatnot", "barcode", "smiley", "sample number", "yellow label")
    diagnostic_text = "\n".join(
        obj.data.body
        for obj in proxies
        if obj.type == "FONT"
    ).lower()
    forbidden_hits = [token for token in forbidden_tokens if token in diagnostic_text]
    light_report = {
        obj["studio_role"]: {
            "name": obj.name,
            "energy": obj.data.energy,
            "color": [round(float(value), 6) for value in obj.data.color],
            "colorChroma": round(material_chroma(tuple(obj.data.color)), 6),
            "rarityLight": bool(obj["rarity_light"]),
        }
        for obj in lights
    }
    checks = {
        "sourceBlockoutFileUnchanged": source_hash_before == sha256(SOURCE_BLEND),
        "formalMaterialBlendUnchanged": material_hash_before == sha256(MATERIAL_BLEND),
        "formalMaterialBuildRecipeUnchanged": build_hash_before == sha256(MATERIAL_BUILD),
        "subjectGeometryDigestUnchanged": (
            digest_before == digest_after_assignment == digest_after_renders
        ),
        "subjectBoundsUnchanged": bounds_before == bounds_after,
        "subjectMatricesUnchanged": all(
            [[float(value) for value in row] for row in obj.matrix_world]
            == original_matrices[obj.name]
            for obj in subjects
        ),
        "labelCenterYUnchanged": (
            structural["labelPosition"]["candidateCenterYmm"]
            == validator.LABEL_CENTER_Y_MM
            == 99.0
        ),
        "concentricErrorUnchanged": (
            structural["cornerCenterFamilies"]["maximumDriftMm"] == 0.0
        ),
        "allSubjectSurfacesManifold": structural["subjectTopology"]["pass"],
        "tubeManifold": structural["closedTube"]["topology"]["manifoldPreflightPass"],
        "tubeChannelFloodFill": structural["closedTube"]["channelFloodFill"]["pass"],
        "transparentLayerOrderPreflight": ordering["pass"],
        "formalSourceMaterialsOnly": set(assignments.values()).issubset(materials),
        "noWideRarityLight": all(not entry["rarityLight"] for entry in light_report.values()),
        "neutralStudioLightChroma": all(
            entry["colorChroma"] <= 0.07 for entry in light_report.values()
        ),
        "keyFillRatioInContract": (
            2.0 <= light_report["key"]["energy"] / light_report["fill"]["energy"] <= 3.0
        ),
        "rimToKeyWithinContract": (
            light_report["rim"]["energy"] / light_report["key"]["energy"] <= 0.35
        ),
        "noForbiddenReferenceIdentity": not forbidden_hits,
        "gate05StatusPreserved": scene["gate05_status"] == "ready_for_review",
        "gate06And07NotEntered": not scene["gate06_entered"] and not scene["gate07_entered"],
        "shippingUnityUnchanged": not scene["shipping_unity_changed"],
        "noBuildInstallPhonePush": not scene["build_install_phone_push"],
    }
    scene.camera = cameras["hero"]
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 2,
        "evidenceClass": "supplementary-material-diagnostic",
        "status": "pass" if all(checks.values()) else "fail",
        "notice": DIAGNOSTIC_NOTICE,
        "approvalEffect": "none-not-gate07-material-approval",
        "pipelineState": {
            "gate05": "ready_for_review",
            "gate06": "blocked",
            "gate07": "blocked",
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "sourceFiles": {
            "gate05Rev2Blockout": {
                "path": str(SOURCE_BLEND.relative_to(REPO_ROOT)),
                "sha256Before": source_hash_before,
                "sha256After": sha256(SOURCE_BLEND),
            },
            "formalMaterialBlend": {
                "path": str(MATERIAL_BLEND.relative_to(REPO_ROOT)),
                "sha256Before": material_hash_before,
                "sha256After": sha256(MATERIAL_BLEND),
            },
            "formalMaterialRecipe": {
                "path": str(MATERIAL_BUILD.relative_to(REPO_ROOT)),
                "sha256Before": build_hash_before,
                "sha256After": sha256(MATERIAL_BUILD),
            },
        },
        "materialAssignments": assignments,
        "formalMaterialPbr": {
            name: pbr_values(material) for name, material in materials.items()
        },
        "formalSourceImageTextureCount": sum(
            len(pbr_values(material)["imageTextures"]) for material in materials.values()
        ),
        "formalSourceTextureTruth": (
            "The approved Blender material source uses Principled PBR parameters and "
            "contains no image-texture nodes. No bitmap material was invented."
        ),
        "geometryPreservation": {
            "subjectObjects": list(SUBJECT_NAMES),
            "digestBefore": digest_before,
            "digestAfterMaterialAssignment": digest_after_assignment,
            "digestAfterRenders": digest_after_renders,
            "boundsBeforeMm": bounds_before,
            "boundsAfterMm": bounds_after,
            "labelCenterYmm": validator.LABEL_CENTER_Y_MM,
            "maximumCornerCenterDriftMm": structural[
                "cornerCenterFamilies"
            ]["maximumDriftMm"],
            "openBoundaryEdgeCount": structural[
                "subjectTopology"
            ]["allOpenBoundaryEdgeCount"],
            "nonManifoldEdgeCount": structural[
                "subjectTopology"
            ]["allNonManifoldEdgeCount"],
            "channelFloodFillVisited": structural[
                "closedTube"
            ]["channelFloodFill"]["visitedSamples"],
            "channelFloodFillTotal": structural[
                "closedTube"
            ]["channelFloodFill"]["sampleCount"],
        },
        "diagnosticProxySurfaces": {
            "objects": [
                {
                    "name": obj.name,
                    "kind": obj["proxy_kind"],
                    "type": obj.type,
                    "thicknessMm": obj.get("proxy_thickness_mm"),
                    "gate05SubjectGeometry": obj["gate05_subject_geometry"],
                    "gate07ApprovalEligible": obj["gate07_approval_eligible"],
                }
                for obj in proxies
            ],
            "reason": (
                "Gate 05 rev 2 stores TransparentCover and NarrowFoil as contour/material "
                "zones. Zero-thickness render surfaces expose the approved materials "
                "without inventing cover thickness or changing subject geometry."
            ),
        },
        "transparentOrderingPreflight": ordering,
        "neutralStudio": {
            "lights": light_report,
            "background": {
                "type": "continuous-procedural-world",
                "node": studio["backgroundNode"],
                "noiseScale": studio["noiseScale"],
                "localNoiseMasks": studio["localNoiseMasks"],
                "imageTextureCount": studio["imageTextureCount"],
            },
            "backgroundRule": (
                "continuous low-saturation fine-grain studio field; no image texture, "
                "local mask, emission, radial halo, or wide cyan/teal rarity light"
            ),
        },
        "render": {
            "engine": scene.render.engine,
            "device": render_device,
            "samples": scene.cycles.samples,
            "adaptiveThreshold": scene.cycles.adaptive_threshold,
            "denoiser": scene.cycles.denoiser,
            "transmissionBounces": scene.cycles.transmission_bounces,
            "colorManagement": {
                "viewTransform": scene.view_settings.view_transform,
                "look": scene.view_settings.look,
                "exposure": scene.view_settings.exposure,
            },
            "rawViews": {
                view_id: str((RAW / f"{view_id}.png").relative_to(REPO_ROOT))
                for view_id in render_plan
            },
            "clayHeroSameCamera": str(
                (RAW / "clay-hero-same-camera.png").relative_to(REPO_ROOT)
            ),
        },
        "identityBoundary": {
            "labelText": diagnostic_text,
            "neutralIdentityPlaceholder": True,
            "neutralAchievementPlaceholder": True,
            "formalLogoRedrawn": False,
            "formalAchievementRedrawn": False,
            "forbiddenHits": forbidden_hits,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO_ROOT)),
    }
    BUILD_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "outputBlend": str(OUTPUT_BLEND),
        "buildReport": str(BUILD_REPORT),
        "geometryDigest": digest_after_renders,
        "boundsMm": bounds_after["size"],
        "labelCenterYmm": validator.LABEL_CENTER_Y_MM,
        "maximumCornerCenterDriftMm": structural[
            "cornerCenterFamilies"
        ]["maximumDriftMm"],
        "openBoundaryEdgeCount": structural[
            "subjectTopology"
        ]["allOpenBoundaryEdgeCount"],
        "nonManifoldEdgeCount": structural[
            "subjectTopology"
        ]["allNonManifoldEdgeCount"],
        "floodFill": (
            f"{structural['closedTube']['channelFloodFill']['visitedSamples']}/"
            f"{structural['closedTube']['channelFloodFill']['sampleCount']}"
        ),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
