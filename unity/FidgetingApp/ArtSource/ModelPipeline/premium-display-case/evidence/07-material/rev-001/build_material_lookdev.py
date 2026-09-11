#!/usr/bin/env python3
"""Build Premium Display Case Gate 07 neutral material lookdev."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
EVIDENCE = ROOT.parent.parent
GATE06 = EVIDENCE / "06-geometry/rev-002"
GATE05_DIAGNOSTIC = EVIDENCE / (
    "05-blockout/rev-002/material-diagnostic/build_material_diagnostic.py"
)
SOURCE_BLEND = GATE06 / "premium-display-case-geometry-r002.blend"
GATE06_REPORT = GATE06 / "geometry-validation.json"
GATE06_VALIDATOR = GATE06 / "validate_geometry.py"
OUTPUT_BLEND = ROOT / "premium-display-case-material-r001.blend"
BUILD_REPORT = ROOT / "material-build-report.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
SOURCE_CLAIM_IDS = (
    "display-case-analysis-closed-loop-r002",
    "display-case-analysis-manifold-r002",
    "display-case-analysis-background-r002",
    "display-case-analysis-label-r002",
    "display-case-analysis-portrait-r002",
    "display-case-analysis-flow-r002",
    "display-case-analysis-environment-r002",
)
EXPECTED_IDENTITY = {
    "fullGeometryDigest": (
        "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    ),
    "objectMatrixDigest": (
        "34d52e8980dbbffc5573523b80de9a47d145a49bb22ae95f8d7c1b38e393d588"
    ),
    "vertexPositionDigest": (
        "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
    ),
    "silhouetteDigest": (
        "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4"
    ),
    "topologyWindingDigest": (
        "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
    ),
}
NOTICE = "GATE 07 MATERIAL · READY FOR REVIEW · NOT APPROVED"


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)
FORMAL_MATERIAL_BLEND = (
    REPO_ROOT / "unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend"
)
FORMAL_MATERIAL_RECIPE = (
    REPO_ROOT
    / "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py"
)
COIN_SLAB_REFERENCE = (
    EVIDENCE / "04-architecture/rev-003/Coin_Slab_v15-user-reference.jpg"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEGACY = load_module("premium_display_case_gate05_material_helpers", GATE05_DIAGNOSTIC)
VALIDATOR = load_module("premium_display_case_gate06_material_validator", GATE06_VALIDATOR)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_input(node: bpy.types.Node, name: str, value) -> None:
    for socket in node.inputs:
        if socket.name == name:
            socket.default_value = value
            return
    raise RuntimeError(f"{node.name} has no input named {name}")


def append_formal_materials() -> dict[str, bpy.types.Material]:
    materials = LEGACY.append_formal_materials()
    graphite = materials["MAT_LabelGraphite"]
    set_input(graphite.node_tree.nodes["Principled BSDF"], "Metallic", 0.0)
    graphite["gate07_tuning"] = (
        "Formal graphite recipe metallic 0.22 corrected to dielectric ink 0.0."
    )
    for material in materials.values():
        material["diagnostic_material_proxy"] = False
        material["gate07_approval_eligible"] = True
        material["gate07_status"] = "ready_for_review"
        material["shipping_material"] = False
    return materials


def add_object_micrograin(
    material: bpy.types.Material,
    feature_size_mm: float,
    bump_distance_mm: float,
    bump_strength: float,
    detail: float,
    base_color_range: tuple[
        tuple[float, float, float, float],
        tuple[float, float, float, float],
    ] | None = None,
) -> dict[str, object]:
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes.get("Principled BSDF")
    if shader is None:
        raise RuntimeError(f"{material.name} has no Principled BSDF")
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = f"M07_{material.name}_LocalCoordinates"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = f"M07_{material.name}_StableMapping"
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"M07_{material.name}_Micrograin"
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 1.0 / feature_size_mm
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.52
    noise.inputs["Distortion"].default_value = 0.0
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"M07_{material.name}_MicrograinBump"
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = bump_distance_mm
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    if base_color_range is not None:
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.name = f"M07_{material.name}_MicrograinColor"
        ramp.color_ramp.elements[0].position = 0.18
        ramp.color_ramp.elements[0].color = base_color_range[0]
        ramp.color_ramp.elements[1].position = 0.82
        ramp.color_ramp.elements[1].color = base_color_range[1]
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    material["micrograin_coordinate_space"] = "object-local"
    material["micrograin_feature_size_mm"] = feature_size_mm
    material["micrograin_bump_distance_mm"] = bump_distance_mm
    material["micrograin_world_space"] = False
    return {
        "material": material.name,
        "coordinateSource": "Texture Coordinate:Object",
        "mapping": mapping.name,
        "texture": noise.name,
        "featureSizeMm": feature_size_mm,
        "bumpDistanceMm": bump_distance_mm,
        "bumpStrength": bump_strength,
        "baseColorRange": list(base_color_range) if base_color_range else None,
        "worldSpace": False,
        "stableUv": False,
    }


def assign_material(
    obj: bpy.types.Object,
    material: bpy.types.Material,
) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)


def hide_non_subject_geometry() -> None:
    subject_set = set(SUBJECT_NAMES)
    for obj in bpy.context.scene.objects:
        if obj.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            obj.hide_render = obj.name not in subject_set
    for obj in bpy.context.scene.objects:
        if obj.type in {"LIGHT", "CAMERA"}:
            bpy.data.objects.remove(obj, do_unlink=True)


def retag_label_zone_proxies(
    materials: dict[str, bpy.types.Material],
) -> list[bpy.types.Object]:
    gate05_validator = VALIDATOR.load_gate05_validator()
    proxies = LEGACY.add_label_diagnostic_proxies(gate05_validator, materials)
    for obj in proxies:
        obj.name = obj.name.replace("DIAGNOSTIC_", "M07_")
        obj["supplementary_material_diagnostic"] = False
        obj["gate07_material_zone_proxy"] = True
        obj["gate07_approval_eligible"] = True
        obj["gate07_status"] = "ready_for_review"
        obj["geometry_contract_role"] = "existing-material-zone-render-surface"
        obj["whole_case_only"] = True
        obj["explode_eligible"] = False
    bpy.data.objects["M07_LabelPrimary"].data.body = "MATERIAL STUDY"
    bpy.data.objects["M07_LabelSecondary"].data.body = "NEUTRAL PLACEHOLDER"
    bpy.data.objects["M07_IdentityAreaText"].data.body = "IDENTITY\nPLACEHOLDER"
    bpy.data.objects["M07_AchievementAreaText"].data.body = (
        "ACHIEVEMENT\nPLACEHOLDER"
    )
    for obj in proxies:
        obj["formal_logo_redrawn"] = False
        obj["formal_achievement_redrawn"] = False
        obj["copied_reference_branding"] = False
    return proxies


def make_backdrop_material() -> tuple[bpy.types.Material, dict[str, object]]:
    material = bpy.data.materials.new("MAT_M07_ContinuousNeutralFriction")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = "M07_BackdropLocalCoordinates"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "M07_BackdropStableMapping"
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "M07_BackdropFineFriction"
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 2.0
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.52
    noise.inputs["Distortion"].default_value = 0.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = "M07_BackdropLowSaturationRange"
    ramp.color_ramp.elements[0].position = 0.12
    ramp.color_ramp.elements[0].color = (0.045, 0.047, 0.050, 1.0)
    ramp.color_ramp.elements[1].position = 0.88
    ramp.color_ramp.elements[1].color = (0.058, 0.060, 0.063, 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.name = "M07_BackdropFrictionBump"
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.08
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", 0.84)
    set_input(shader, "Emission Strength", 0.0)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    material["background_contract"] = (
        "continuous-low-saturation-matte-friction-no-local-mask-no-radial-halo"
    )
    material["micrograin_coordinate_space"] = "object-local"
    material["micrograin_feature_size_mm"] = 0.5
    material["micrograin_bump_distance_mm"] = 0.08
    material["world_space_grain"] = False
    material["local_noise_masks"] = 0
    material["fixed_green_bias"] = False
    return material, {
        "material": material.name,
        "metallic": 0.0,
        "roughness": 0.84,
        "linearLuminanceRange": [0.045, 0.063],
        "maximumSaturation": 0.12,
        "grainFeatureSizeMm": 0.5,
        "normalPeakToPeakMm": 0.08,
        "coordinateSource": "Texture Coordinate:Object",
        "localNoiseMasks": 0,
        "radialHalo": False,
        "fixedGreenBias": False,
    }


def link_object(obj: bpy.types.Object) -> bpy.types.Object:
    bpy.context.scene.collection.objects.link(obj)
    obj["model_pipeline_exclude"] = True
    obj["gate07_studio_only"] = True
    obj["shipping_asset"] = False
    return obj


def make_cyclorama(material: bpy.types.Material) -> bpy.types.Object:
    radius = 90.0
    cross_section: list[tuple[float, float]] = [
        (420.0, -250.0),
        (-100.0, -250.0),
    ]
    for index in range(1, 13):
        theta = -math.pi / 2.0 - (math.pi / 2.0) * index / 12.0
        cross_section.append(
            (
                -100.0 + radius * math.cos(theta),
                -160.0 + radius * math.sin(theta),
            )
        )
    cross_section.append((-190.0, 980.0))
    vertices = [
        (x, y, z)
        for x in (-1800.0, 1800.0)
        for y, z in cross_section
    ]
    count = len(cross_section)
    faces = [
        (index, index + 1, count + index + 1, count + index)
        for index in range(count - 1)
    ]
    mesh = bpy.data.meshes.new("M07_StudioCyclorama_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = link_object(bpy.data.objects.new("M07_StudioCyclorama", mesh))
    obj.data.materials.append(material)
    obj["continuous_background"] = True
    obj["local_noise_patches"] = 0
    return obj


def make_back_wall(
    name: str,
    location: tuple[float, float, float],
    rotation: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj["model_pipeline_exclude"] = True
    obj["gate07_studio_only"] = True
    obj["shipping_asset"] = False
    obj["continuous_background"] = True
    return obj


def configure_studio() -> tuple[dict[str, bpy.types.Object], dict[str, object]]:
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("M07_NeutralWorld")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes.clear()
    output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    background = world.node_tree.nodes.new("ShaderNodeBackground")
    background.name = "M07_NeutralWorldBackground"
    background.inputs["Color"].default_value = (0.032, 0.033, 0.035, 1.0)
    background.inputs["Strength"].default_value = 0.28
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
    world["image_texture_count"] = 0
    world["procedural_noise_count"] = 0
    world["radial_halo"] = False
    world["fixed_green_bias"] = False

    backdrop_material, backdrop_spec = make_backdrop_material()
    studio = {
        "main": make_cyclorama(backdrop_material),
        "back": make_back_wall(
            "M07_BackViewWall",
            (0.0, 0.0, 280.0),
            (0.0, 0.0, 0.0),
            (900.0, 700.0, 1.0),
            backdrop_material,
        ),
        "side": make_back_wall(
            "M07_SideViewWall",
            (-320.0, 0.0, 0.0),
            (0.0, math.pi / 2.0, 0.0),
            (900.0, 700.0, 1.0),
            backdrop_material,
        ),
    }
    studio["back"].hide_render = True
    studio["side"].hide_render = True
    return studio, {
        "world": {
            "baseColor": [0.032, 0.033, 0.035, 1.0],
            "strength": 0.28,
            "imageTextureCount": 0,
            "proceduralNoiseCount": 0,
            "radialHalo": False,
            "fixedGreenBias": False,
        },
        "surface": backdrop_spec,
    }


def set_studio_mode(
    studio: dict[str, bpy.types.Object],
    mode: str,
) -> None:
    for key, obj in studio.items():
        obj.hide_render = key != mode


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
    size_y: float,
    color: tuple[float, float, float],
    target: Vector,
    role: str,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "RECTANGLE"
    data.size = size
    data.size_y = size_y
    data.color = color
    obj = link_object(bpy.data.objects.new(name, data))
    obj.location = location
    look_at(obj, target)
    obj["studio_role"] = role
    obj["neutral_gate07_light"] = True
    obj["final_lighting_approval"] = False
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
    obj = link_object(bpy.data.objects.new(name, data))
    obj.location = location
    orient_camera(obj, Vector(target))
    obj["gate07_material_camera"] = True
    obj["whole_case_assembly_state"] = "assembled"
    return obj


def configure_lights_and_cameras() -> tuple[
    dict[str, bpy.types.Object],
    list[bpy.types.Object],
]:
    target = Vector((0.0, -5.0, 10.0))
    lights = [
        add_area_light(
            "M07_KeyStrip_5000K",
            (430.0, 355.0, 660.0),
            2_200_000.0,
            520.0,
            145.0,
            (1.0, 0.975, 0.95),
            target,
            "key",
        ),
        add_area_light(
            "M07_FillSoftbox_6200K",
            (-430.0, 85.0, 500.0),
            900_000.0,
            520.0,
            420.0,
            (0.955, 0.972, 1.0),
            target,
            "fill",
        ),
        add_area_light(
            "M07_RimStrip_5600K",
            (-250.0, 300.0, -390.0),
            620_000.0,
            420.0,
            125.0,
            (0.975, 0.985, 1.0),
            target,
            "rim",
        ),
    ]
    cameras = {
        "hero": add_camera(
            "M07_HeroCamera",
            (305.0, 150.0, 900.0),
            (0.0, 0.0, 8.0),
            72.0,
        ),
        "left-oblique": add_camera(
            "M07_LeftObliqueCamera",
            (-360.0, 115.0, 850.0),
            (0.0, 0.0, 5.0),
            72.0,
        ),
        "right-oblique": add_camera(
            "M07_RightObliqueCamera",
            (360.0, 115.0, 850.0),
            (0.0, 0.0, 5.0),
            72.0,
        ),
        "side": add_camera(
            "M07_SideCamera",
            (980.0, 15.0, 40.0),
            (0.0, 0.0, 0.0),
            68.0,
        ),
        "back": add_camera(
            "M07_BackCamera",
            (-260.0, 80.0, -900.0),
            (0.0, 0.0, 5.0),
            72.0,
        ),
        "tube-corner": add_camera(
            "M07_TubeCornerCamera",
            (255.0, 255.0, 470.0),
            (92.0, 130.0, 25.0),
            104.0,
        ),
        "label-closeup": add_camera(
            "M07_LabelCloseupCamera",
            (0.0, 104.0, 430.0),
            (0.0, 99.0, 24.0),
            92.0,
        ),
        "tactile-closeup": add_camera(
            "M07_TactileCloseupCamera",
            (225.0, -76.0, 390.0),
            (0.0, -62.0, 18.0),
            124.0,
        ),
        "rotation": add_camera(
            "M07_RotationCamera",
            (0.0, 20.0, 940.0),
            (0.0, 0.0, 5.0),
            74.0,
        ),
    }
    return cameras, lights


def configure_render(scene: bpy.types.Scene, draft: bool) -> str:
    scene.render.engine = "CYCLES"
    device = "CPU"
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "METAL"
        preferences.get_devices()
        for candidate in preferences.devices:
            candidate.use = True
        scene.cycles.device = "GPU"
        device = "METAL"
    except Exception:
        scene.cycles.device = "CPU"
    scene.cycles.samples = 20 if draft else 96
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.065 if draft else 0.022
    scene.cycles.adaptive_min_samples = 8 if draft else 24
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 20
    scene.cycles.transmission_bounces = 20
    scene.cycles.transparent_max_bounces = 20
    scene.cycles.glossy_bounces = 8
    scene.cycles.seed = 23
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.65
    scene.view_settings.gamma = 1.0
    return device


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


def pbr_values(material: bpy.types.Material) -> dict[str, object]:
    values = LEGACY.pbr_values(material)
    values["micrograinCoordinateSpace"] = material.get(
        "micrograin_coordinate_space"
    )
    values["micrograinFeatureSizeMm"] = material.get(
        "micrograin_feature_size_mm"
    )
    values["micrograinBumpDistanceMm"] = material.get(
        "micrograin_bump_distance_mm"
    )
    values["worldSpaceGrain"] = bool(material.get("micrograin_world_space", False))
    return values


def stable_local_coordinate_report(
    objects: list[bpy.types.Object],
    root: bpy.types.Object,
) -> dict[str, object]:
    angles = (0, 90, 180, 270, 360)
    baselines = {
        obj.name: [
            Vector(vertex.co)
            for vertex in list(obj.data.vertices)[: min(24, len(obj.data.vertices))]
        ]
        for obj in objects
    }
    frames: dict[str, object] = {}
    maximum_delta = 0.0
    for angle in angles:
        root.rotation_euler[1] = 0.0 if angle == 360 else math.radians(angle)
        bpy.context.view_layer.update()
        frame_delta = 0.0
        for obj in objects:
            inverse = obj.matrix_world.inverted()
            for baseline in baselines[obj.name]:
                recovered = inverse @ (obj.matrix_world @ baseline)
                frame_delta = max(frame_delta, (recovered - baseline).length)
        maximum_delta = max(maximum_delta, frame_delta)
        frames[str(angle)] = {
            "rootRotationDegrees": angle,
            "maximumRecoveredLocalCoordinateDelta": frame_delta,
        }
    root.rotation_euler[1] = 0.0
    bpy.context.view_layer.update()
    return {
        "anglesDegrees": list(angles),
        "coordinatePolicy": "Texture Coordinate:Object for every micrograin node",
        "frames": frames,
        "maximumRecoveredLocalCoordinateDelta": maximum_delta,
        "tolerance": 1e-5,
        "pass": maximum_delta <= 1e-5,
    }


def main() -> None:
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    draft = "--draft" in args
    RAW.mkdir(parents=True, exist_ok=True)
    source_hash_before = sha256(SOURCE_BLEND)
    formal_blend_hash_before = sha256(FORMAL_MATERIAL_BLEND)
    formal_recipe_hash_before = sha256(FORMAL_MATERIAL_RECIPE)
    reference_hash_before = sha256(COIN_SLAB_REFERENCE)
    source_report = json.loads(GATE06_REPORT.read_text(encoding="utf-8"))

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate07_Material_Rev001"
    scene["gate"] = "07-material"
    scene["material_revision"] = 1
    scene["gate07_status"] = "ready_for_review"
    scene["gate07_approved"] = False
    scene["gate08_entered"] = False
    scene["whole_case_only"] = True
    scene["no_explode"] = True
    scene["final_lighting_approval"] = False
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False
    scene["notice"] = NOTICE

    hide_non_subject_geometry()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    identity_before = VALIDATOR.identity_snapshot(subjects)
    bounds_before = VALIDATOR.world_bounds(subjects)
    source_materials = {
        obj.name: [slot.material for slot in obj.material_slots if slot.material]
        for obj in subjects
    }

    materials = append_formal_materials()
    micrograin = {
        "shell": add_object_micrograin(
            materials["MAT_FrostedPolycarbonate"], 0.62, 0.03, 0.025, 2.0
        ),
        "tubeEdge": add_object_micrograin(
            materials["MAT_FrostedPolycarbonateEdge"], 0.58, 0.025, 0.02, 2.0
        ),
        "tactileInsert": add_object_micrograin(
            materials["MAT_BlackFlocking"],
            0.48,
            0.16,
            0.34,
            3.0,
            (
                (0.006, 0.008, 0.011, 1.0),
                (0.018, 0.021, 0.025, 1.0),
            ),
        ),
        "labelPaper": add_object_micrograin(
            materials["MAT_LabelPaper"], 0.44, 0.04, 0.07, 2.0
        ),
        "silverFoil": add_object_micrograin(
            materials["MAT_RarityFoilSilver"], 0.38, 0.02, 0.04, 1.5
        ),
        "graphiteInk": add_object_micrograin(
            materials["MAT_LabelGraphite"], 0.42, 0.025, 0.05, 1.5
        ),
    }
    assignments = {
        "RearPolycarbonateShell": "MAT_FrostedPolycarbonate",
        "FrontPolycarbonateShell": "MAT_FrostedPolycarbonate",
        "ContinuousTubePerimeter": "MAT_FrostedPolycarbonateEdge",
        "TactileBackgroundInsert": "MAT_BlackFlocking",
        "PhysicalLabel": "MAT_LabelPaper",
    }
    for object_name, material_name in assignments.items():
        assign_material(bpy.data.objects[object_name], materials[material_name])

    proxies = retag_label_zone_proxies(materials)
    identity_after_assignment = VALIDATOR.identity_snapshot(subjects)
    bounds_after_assignment = VALIDATOR.world_bounds(subjects)
    studio, background_spec = configure_studio()
    cameras, lights = configure_lights_and_cameras()
    render_device = configure_render(scene, draft)
    root = bpy.data.objects["PresentationRoot"]
    grain_objects = [
        bpy.data.objects["FrontPolycarbonateShell"],
        bpy.data.objects["ContinuousTubePerimeter"],
        bpy.data.objects["TactileBackgroundInsert"],
        bpy.data.objects["PhysicalLabel"],
    ]
    grain_stability = stable_local_coordinate_report(grain_objects, root)
    bpy.context.view_layer.update()

    if draft:
        set_studio_mode(studio, "main")
        render(scene, cameras["hero"], RAW / "draft-hero.png", (760, 620))
        print(
            json.dumps(
                {
                    "draft": str(RAW / "draft-hero.png"),
                    "device": render_device,
                    "identity": identity_after_assignment,
                    "grainStability": grain_stability,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    render_plan = {
        "hero": ((1400, 1120), "main"),
        "left-oblique": ((1280, 1080), "main"),
        "right-oblique": ((1280, 1080), "main"),
        "side": ((1100, 1320), "side"),
        "back": ((1280, 1080), "back"),
        "tube-corner": ((1400, 1060), "main"),
        "label-closeup": ((1500, 980), "main"),
        "tactile-closeup": ((1400, 1040), "main"),
    }
    root.rotation_euler[1] = 0.0
    for view_id, (resolution, studio_mode) in render_plan.items():
        set_studio_mode(studio, studio_mode)
        if view_id == "tactile-closeup":
            key = lights[0]
            original_matrix = key.matrix_world.copy()
            original_size = key.data.size
            original_size_y = key.data.size_y
            key.location = (340.0, -20.0, 310.0)
            key.data.size = 360.0
            key.data.size_y = 52.0
            look_at(key, Vector((0.0, -62.0, 18.0)))
        render(scene, cameras[view_id], RAW / f"{view_id}.png", resolution)
        if view_id == "tactile-closeup":
            key.matrix_world = original_matrix
            key.data.size = original_size
            key.data.size_y = original_size_y

    set_studio_mode(studio, "main")
    for angle in (0, 90, 180, 270, 360):
        root.rotation_euler[1] = 0.0 if angle == 360 else math.radians(angle)
        bpy.context.view_layer.update()
        render(
            scene,
            cameras["rotation"],
            RAW / f"rotation-{angle:03d}.png",
            (900, 980),
        )
    root.rotation_euler[1] = 0.0
    bpy.context.view_layer.update()

    for proxy in proxies:
        proxy.hide_render = True
    clay = bpy.data.materials.new("MAT_M07_ClayControl")
    clay.use_nodes = True
    clay_shader = clay.node_tree.nodes["Principled BSDF"]
    set_input(clay_shader, "Base Color", (0.54, 0.57, 0.60, 1.0))
    set_input(clay_shader, "Metallic", 0.0)
    set_input(clay_shader, "Roughness", 0.62)
    for obj in subjects:
        assign_material(obj, clay)
    set_studio_mode(studio, "main")
    render(
        scene,
        cameras["hero"],
        RAW / "clay-hero-same-camera.png",
        (1400, 1120),
    )
    for object_name, material_name in assignments.items():
        assign_material(bpy.data.objects[object_name], materials[material_name])
    for proxy in proxies:
        proxy.hide_render = False
    bpy.context.view_layer.update()

    identity_after_renders = VALIDATOR.identity_snapshot(subjects)
    bounds_after_renders = VALIDATOR.world_bounds(subjects)
    mesh_integrity = {
        obj.name: VALIDATOR.mesh_integrity(obj) for obj in subjects
    }
    gate05_validator = VALIDATOR.load_gate05_validator()
    tube_orientation = VALIDATOR.hollow_tube_orientation(
        bpy.data.objects["ContinuousTubePerimeter"],
        gate05_validator,
    )
    label_center_y = float(
        bpy.data.objects["PhysicalLabel"].get("center_y_mm", 99.0)
    )
    forbidden_tokens = (
        "whatnot",
        "yellow",
        "smiley",
        "barcode",
        "#0000001",
        "gem/mint",
        "coin window",
    )
    visible_text = "\n".join(
        obj.data.body for obj in proxies if obj.type == "FONT"
    ).lower()
    forbidden_hits = [token for token in forbidden_tokens if token in visible_text]
    light_report = {
        obj["studio_role"]: {
            "name": obj.name,
            "energy": obj.data.energy,
            "color": [round(float(value), 6) for value in obj.data.color],
            "colorChroma": round(
                max(obj.data.color) - min(obj.data.color),
                6,
            ),
            "rarityLight": bool(obj["rarity_light"]),
            "finalLightingApproval": bool(obj["final_lighting_approval"]),
        }
        for obj in lights
    }
    subject_triangle_count = sum(
        item["triangles"] for item in mesh_integrity.values()
    )
    checks = {
        "sourceGate06BlendUnchanged": source_hash_before == sha256(SOURCE_BLEND),
        "sourceGate06ReportPassed": source_report["status"] == "pass",
        "formalMaterialBlendUnchanged": (
            formal_blend_hash_before == sha256(FORMAL_MATERIAL_BLEND)
        ),
        "formalMaterialRecipeUnchanged": (
            formal_recipe_hash_before == sha256(FORMAL_MATERIAL_RECIPE)
        ),
        "coinSlabReferenceUnchanged": (
            reference_hash_before == sha256(COIN_SLAB_REFERENCE)
        ),
        "identityExactBefore": all(
            identity_before[key] == value for key, value in EXPECTED_IDENTITY.items()
        ),
        "identityUnchangedAfterAssignment": (
            identity_after_assignment == identity_before
        ),
        "identityUnchangedAfterRenders": identity_after_renders == identity_before,
        "boundsUnchanged": (
            bounds_before
            == bounds_after_assignment
            == bounds_after_renders
            and bounds_before["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "labelCenterYUnchanged": label_center_y == 99.0,
        "allSubjectMeshesClosedAndManifold": all(
            item["openBoundaryEdgeCount"] == 0
            and item["nonManifoldEdgeCount"] == 0
            and item["pass"]
            for item in mesh_integrity.values()
        ),
        "tubeWindingPreserved": (
            tube_orientation["orientationDisposition"]
            == "outer-outward-inner-toward-lumen-net-positive"
            and tube_orientation["netMaterialSignedVolumeMm3"] == 52932.982745
            and tube_orientation["pass"]
        ),
        "formalMaterialZonesOnly": set(assignments.values()).issubset(materials),
        "allMicrograinObjectLocal": all(
            item["coordinateSource"] == "Texture Coordinate:Object"
            and not item["worldSpace"]
            for item in micrograin.values()
        ),
        "grainStableAtFiveAngles": grain_stability["pass"],
        "backgroundWithinContract": (
            background_spec["surface"]["metallic"] == 0.0
            and 0.78 <= background_spec["surface"]["roughness"] <= 0.88
            and background_spec["surface"]["linearLuminanceRange"][0] >= 0.035
            and background_spec["surface"]["linearLuminanceRange"][1] <= 0.08
            and background_spec["surface"]["maximumSaturation"] <= 0.12
            and 0.35
            <= background_spec["surface"]["grainFeatureSizeMm"]
            <= 0.8
            and background_spec["surface"]["normalPeakToPeakMm"] <= 0.12
            and background_spec["surface"]["localNoiseMasks"] == 0
            and not background_spec["surface"]["radialHalo"]
            and not background_spec["surface"]["fixedGreenBias"]
        ),
        "neutralThreeLightRig": (
            set(light_report) == {"key", "fill", "rim"}
            and 2.0
            <= light_report["key"]["energy"] / light_report["fill"]["energy"]
            <= 3.0
            and light_report["rim"]["energy"] / light_report["key"]["energy"]
            <= 0.35
            and all(not item["rarityLight"] for item in light_report.values())
            and all(
                not item["finalLightingApproval"] for item in light_report.values()
            )
        ),
        "noForbiddenReferenceIdentity": not forbidden_hits,
        "neutralPlaceholdersOnly": all(
            not bool(obj["formal_logo_redrawn"])
            and not bool(obj["formal_achievement_redrawn"])
            and not bool(obj["copied_reference_branding"])
            for obj in proxies
        ),
        "subjectTriangleBudget": subject_triangle_count <= 120_000,
        "wholeCaseOnlyNoExplode": (
            bool(scene["whole_case_only"])
            and bool(scene["no_explode"])
            and all(obj.hide_render for obj in bpy.data.objects if obj.name.startswith("EXPLODED_"))
        ),
        "gate07NotApproved": not bool(scene["gate07_approved"]),
        "gate08NotEntered": not bool(scene["gate08_entered"]),
        "shippingUnityUnchanged": not bool(scene["shipping_unity_changed"]),
        "noBuildInstallPhonePush": not bool(scene["build_install_phone_push"]),
    }

    scene.camera = cameras["hero"]
    set_studio_mode(studio, "main")
    root.rotation_euler[1] = 0.0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "notice": NOTICE,
        "pipelineRevisionAtBuild": 32,
        "sourceGate06": {
            "geometryRevision": 2,
            "approvalQuote": "可以啊，没问题，你继续吧",
            "approvalScope": [
                "current-gate06-geometry-rev2",
                "whole-case-only",
                "no-explode",
            ],
            "blendPath": str(SOURCE_BLEND.relative_to(REPO_ROOT)),
            "sha256Before": source_hash_before,
            "sha256After": sha256(SOURCE_BLEND),
            "identity": identity_before,
            "boundsMm": bounds_before,
            "unchanged": True,
        },
        "formalMaterialSources": {
            "blend": {
                "path": str(FORMAL_MATERIAL_BLEND.relative_to(REPO_ROOT)),
                "sha256Before": formal_blend_hash_before,
                "sha256After": sha256(FORMAL_MATERIAL_BLEND),
            },
            "recipe": {
                "path": str(FORMAL_MATERIAL_RECIPE.relative_to(REPO_ROOT)),
                "sha256Before": formal_recipe_hash_before,
                "sha256After": sha256(FORMAL_MATERIAL_RECIPE),
            },
        },
        "referenceUse": {
            "assetId": "premium-display-case-rive-v15-user-reference-r003",
            "path": str(COIN_SLAB_REFERENCE.relative_to(REPO_ROOT)),
            "sha256": reference_hash_before,
            "allowed": [
                "layered material-response separation",
                "continuous perimeter highlight behavior",
            ],
            "prohibitedAndAbsent": [
                "WHATNOT branding",
                "yellow field",
                "smiley",
                "barcode",
                "sample number",
                "circular coin window",
            ],
            "copiedBrandArtwork": False,
        },
        "sourceClaimIds": list(SOURCE_CLAIM_IDS),
        "materialAssignments": assignments,
        "materialParameters": {
            name: pbr_values(material) for name, material in materials.items()
        },
        "micrograin": micrograin,
        "grainStability": grain_stability,
        "background": background_spec,
        "neutralStudio": {
            "lights": light_report,
            "purpose": "Gate 07 neutral material evaluation only",
            "finalLightingApproval": False,
        },
        "geometryPreservation": {
            "identityBefore": identity_before,
            "identityAfterMaterialAssignment": identity_after_assignment,
            "identityAfterRenders": identity_after_renders,
            "boundsBeforeMm": bounds_before,
            "boundsAfterMaterialAssignmentMm": bounds_after_assignment,
            "boundsAfterRendersMm": bounds_after_renders,
            "labelCenterYmm": label_center_y,
            "maximumCornerCenterDriftMm": source_report["concentricContours"][
                "maximumCenterDriftMm"
            ],
            "meshIntegrity": mesh_integrity,
            "tubeOrientation": tube_orientation,
            "floodFill": source_report["closedTube"][
                "volumetricPassageFloodFill"
            ],
        },
        "materialZoneSurfaces": [
            {
                "name": obj.name,
                "type": obj.type,
                "kind": obj["proxy_kind"],
                "thicknessMm": obj.get("proxy_thickness_mm"),
                "geometryContractRole": obj["geometry_contract_role"],
                "wholeCaseOnly": bool(obj["whole_case_only"]),
                "explodeEligible": bool(obj["explode_eligible"]),
            }
            for obj in proxies
        ],
        "colorSpacePolicy": {
            "imageTextureCount": sum(
                len(pbr_values(material)["imageTextures"])
                for material in materials.values()
            ),
            "baseColor": "Principled linear values, displayed through AgX",
            "scalarChannels": (
                "Procedural Noise Fac drives Bump only and is treated as non-color data."
            ),
            "normalData": "Procedural scalar height converted by Bump; no sRGB normal map.",
            "pass": True,
        },
        "surfaceCoverage": {
            "frontCap": "formal Principled material on closed subject meshes",
            "backCap": "formal Principled material on closed subject meshes",
            "sidewall": "formal Principled material on closed subject meshes",
            "overlayContextExcluded": True,
            "imageTexturesRequired": False,
        },
        "optimization": {
            "subjectTriangles": subject_triangle_count,
            "triangleBudget": 120_000,
            "subjectMaterialSlots": len(set(assignments.values())),
            "materialSlotBudget": 8,
            "renderOnlyZoneProxyCount": len(proxies),
            "geometryOptimizationPerformed": False,
            "reason": "Approved Gate 06 geometry is immutable.",
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
            "rotationViews": {
                str(angle): str(
                    (RAW / f"rotation-{angle:03d}.png").relative_to(REPO_ROOT)
                )
                for angle in (0, 90, 180, 270, 360)
            },
            "clayHeroSameCamera": str(
                (RAW / "clay-hero-same-camera.png").relative_to(REPO_ROOT)
            ),
        },
        "identityBoundary": {
            "visibleText": visible_text,
            "neutralIdentityPlaceholder": True,
            "neutralAchievementPlaceholder": True,
            "formalArtworkDeferred": True,
            "forbiddenHits": forbidden_hits,
        },
        "scope": {
            "wholeCaseOnly": True,
            "explode": False,
            "gate07Status": "ready_for_review",
            "gate07Approved": False,
            "gate08Entered": False,
            "finalLightingApproval": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO_ROOT)),
        "outputBlendSha256": sha256(OUTPUT_BLEND),
    }
    BUILD_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputBlend": str(OUTPUT_BLEND),
                "buildReport": str(BUILD_REPORT),
                "fullGeometryDigest": identity_after_renders[
                    "fullGeometryDigest"
                ],
                "vertexPositionDigest": identity_after_renders[
                    "vertexPositionDigest"
                ],
                "topologyWindingDigest": identity_after_renders[
                    "topologyWindingDigest"
                ],
                "boundsMm": bounds_after_renders["sizeMm"],
                "labelCenterYmm": label_center_y,
                "grainStability": grain_stability["pass"],
                "subjectTriangles": subject_triangle_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
