#!/usr/bin/env python3
"""Build Premium Display Case Gate 08 controlled-lighting evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
EVIDENCE = ROOT.parent.parent
MODEL_ROOT = ROOT.parents[2]
GATE07 = EVIDENCE / "07-material/rev-001"
SOURCE_BLEND = GATE07 / "premium-display-case-material-r001.blend"
SOURCE_BUILD_REPORT = GATE07 / "material-build-report.json"
SOURCE_AUDIT_REPORT = GATE07 / "blender-audit.json"
SOURCE_IMAGE_REPORT = GATE07 / "material-image-validation.json"
GATE06_VALIDATOR = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
MANIFEST = MODEL_ROOT / "pipeline.json"
OUTPUT_BLEND = ROOT / "premium-display-case-lighting-r001.blend"
REPORT = ROOT / "lighting-build-report.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_GEOMETRY = {
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
SOURCE_ASSET_IDS = (
    "premium-display-case-material-blend-r001",
    "premium-display-case-material-build-report-r001",
    "premium-display-case-material-blender-audit-r001",
    "premium-display-case-material-image-validation-r001",
    "premium-display-case-material-board-r001",
    "premium-display-case-material-closeup-r001",
    "premium-display-case-material-grain-stability-r001",
    "premium-display-case-geometry-blend-r002",
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

KEY_ENERGY = 2_400_000.0
FILL_RATIO = 0.30
RIM_RATIO = 0.40
EXPOSURE_EV = 0.55
VIEW_TRANSFORM = "AgX"
LOOK = "AgX - Medium High Contrast"


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("premium_display_case_gate08_validator", GATE06_VALIDATOR)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def json_value(value):
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return round(value, 12)
    try:
        return [json_value(item) for item in value]
    except TypeError:
        return str(value)


def material_payload(material: bpy.types.Material) -> dict[str, object]:
    nodes = []
    links = []
    if material.use_nodes and material.node_tree:
        for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
            attributes = {}
            for name in (
                "blend_type",
                "clamp",
                "data_type",
                "gradient_type",
                "interpolation_type",
                "mapping",
                "noise_dimensions",
                "operation",
                "vector_type",
                "wave_type",
            ):
                if hasattr(node, name):
                    attributes[name] = json_value(getattr(node, name))
            if hasattr(node, "color_ramp"):
                attributes["colorRamp"] = [
                    {
                        "position": round(float(element.position), 12),
                        "color": json_value(element.color),
                    }
                    for element in node.color_ramp.elements
                ]
            inputs = []
            for socket in node.inputs:
                item = {"name": socket.name, "linked": bool(socket.is_linked)}
                if not socket.is_linked and hasattr(socket, "default_value"):
                    item["value"] = json_value(socket.default_value)
                inputs.append(item)
            nodes.append(
                {
                    "name": node.name,
                    "type": node.bl_idname,
                    "attributes": attributes,
                    "inputs": inputs,
                }
            )
        links = sorted(
            (
                link.from_node.name,
                link.from_socket.name,
                link.to_node.name,
                link.to_socket.name,
            )
            for link in material.node_tree.links
        )
    return {
        "name": material.name,
        "useNodes": bool(material.use_nodes),
        "diffuseColor": json_value(material.diffuse_color),
        "custom": {
            key: json_value(material[key])
            for key in sorted(material.keys())
            if key != "_RNA_UI"
        },
        "nodes": nodes,
        "links": links,
    }


def approved_material_digest(
    material_names: list[str],
    assignment_objects: list[bpy.types.Object],
) -> tuple[str, dict[str, object]]:
    payload = {
        "materials": [
            material_payload(bpy.data.materials[name])
            for name in sorted(material_names)
        ],
        "assignments": {
            obj.name: [
                slot.material.name if slot.material else None
                for slot in obj.material_slots
            ]
            for obj in sorted(assignment_objects, key=lambda item: item.name)
        },
    }
    return hashlib.sha256(stable_json(payload).encode("utf-8")).hexdigest(), payload


def set_input(node: bpy.types.Node, name: str, value) -> None:
    socket = next((item for item in node.inputs if item.name == name), None)
    if socket is None:
        raise RuntimeError(f"{node.name} has no input named {name}")
    socket.default_value = value


def orient_camera(camera: bpy.types.Object, target: Vector) -> None:
    backward = (camera.location - target).normalized()
    world_up = Vector((0.0, 1.0, 0.0))
    if abs(backward.dot(world_up)) > 0.999:
        world_up = Vector((0.0, 0.0, 1.0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def aim_light(light: bpy.types.Object, target: Vector) -> None:
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()


def spherical_position(
    target: tuple[float, float, float],
    distance: float,
    azimuth_degrees: float,
    elevation_degrees: float,
) -> tuple[float, float, float]:
    azimuth = math.radians(azimuth_degrees)
    elevation = math.radians(elevation_degrees)
    center = Vector(target)
    offset = Vector(
        (
            math.sin(azimuth) * math.cos(elevation) * distance,
            math.sin(elevation) * distance,
            math.cos(azimuth) * math.cos(elevation) * distance,
        )
    )
    return tuple(center + offset)


def add_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens_mm: float,
    view_id: str,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.type = "PERSP"
    data.lens = lens_mm
    data.sensor_fit = "VERTICAL"
    data.sensor_width = 36.0
    data.sensor_height = 32.0
    data.dof.use_dof = False
    data.clip_start = 1.0
    data.clip_end = 5000.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    orient_camera(obj, Vector(target))
    obj["gate08_authored_camera"] = True
    obj["camera_id"] = view_id
    obj["target_mm"] = list(target)
    obj["whole_case_assembly_state"] = "assembled"
    obj["shipping_camera"] = False
    return obj


def add_area_light(
    name: str,
    role: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    energy: float,
    size: float,
    size_y: float,
    color: tuple[float, float, float],
    kelvin: int,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE"
    data.energy = energy
    data.size = size
    data.size_y = size_y
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim_light(obj, Vector(target))
    obj["gate08_controlled_light"] = True
    obj["studio_role"] = role
    obj["color_temperature_kelvin"] = kelvin
    obj["target_mm"] = list(target)
    obj["rarity_light"] = False
    obj["shipping_light"] = False
    return obj


def configure_render(scene: bpy.types.Scene) -> dict[str, object]:
    scene.render.engine = "CYCLES"
    device = "CPU fallback"
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "METAL"
        preferences.get_devices()
        enabled = []
        for candidate in preferences.devices:
            candidate.use = candidate.type != "CPU"
            if candidate.use:
                enabled.append(candidate.name)
        if enabled:
            scene.cycles.device = "GPU"
            device = ", ".join(enabled)
    except Exception as error:
        device = f"CPU fallback: {error}"
        scene.cycles.device = "CPU"
    scene.cycles.samples = 96
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.018
    scene.cycles.adaptive_min_samples = 24
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 20
    scene.cycles.transmission_bounces = 20
    scene.cycles.transparent_max_bounces = 20
    scene.cycles.glossy_bounces = 8
    scene.cycles.seed = 31
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = True
    scene.view_settings.view_transform = VIEW_TRANSFORM
    scene.view_settings.look = LOOK
    scene.view_settings.exposure = EXPOSURE_EV
    scene.view_settings.gamma = 1.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 5600
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 0.0
    return {
        "engine": scene.render.engine,
        "device": device,
        "samples": scene.cycles.samples,
        "adaptiveThreshold": scene.cycles.adaptive_threshold,
        "denoiser": scene.cycles.denoiser,
        "transmissionBounces": scene.cycles.transmission_bounces,
    }


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
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def simple_principled(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    set_input(shader, "Base Color", color)
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", roughness)
    set_input(shader, "Emission Strength", 0.0)
    material["gate08_technical_pass_only"] = True
    material["shipping_material"] = False
    return material


def emission_material(
    name: str,
    color: tuple[float, float, float, float],
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_pass_only"] = True
    material["shipping_material"] = False
    return material


def normal_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_M08_Pass_Normal")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "SCALE"
    multiply.inputs[3].default_value = 0.5
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Normal"], multiply.inputs[0])
    links.new(multiply.outputs["Vector"], add.inputs[0])
    links.new(add.outputs["Vector"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_pass_only"] = True
    material["shipping_material"] = False
    return material


def depth_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_M08_Pass_Depth")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    camera_data = nodes.new("ShaderNodeCameraData")
    mapping = nodes.new("ShaderNodeMapRange")
    mapping.inputs["From Min"].default_value = 780.0
    mapping.inputs["From Max"].default_value = 1020.0
    mapping.inputs["To Min"].default_value = 1.0
    mapping.inputs["To Max"].default_value = 0.05
    mapping.clamp = True
    emission = nodes.new("ShaderNodeEmission")
    links.new(camera_data.outputs["View Z Depth"], mapping.inputs["Value"])
    links.new(mapping.outputs["Result"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_pass_only"] = True
    material["shipping_material"] = False
    material["depth_near_mm"] = 780.0
    material["depth_far_mm"] = 1020.0
    return material


def principled_roughness(material: bpy.types.Material | None) -> float:
    if material is None or not material.use_nodes or not material.node_tree:
        return 0.5
    shader = next(
        (
            node
            for node in material.node_tree.nodes
            if node.bl_idname == "ShaderNodeBsdfPrincipled"
        ),
        None,
    )
    if shader is None:
        return 0.5
    socket = next((item for item in shader.inputs if item.name == "Roughness"), None)
    if socket is None:
        return 0.5
    return float(socket.default_value)


def restore_slots(
    objects: list[bpy.types.Object],
    original_slots: dict[str, list[bpy.types.Material | None]],
) -> None:
    for obj in objects:
        obj.data.materials.clear()
        for material in original_slots[obj.name]:
            obj.data.materials.append(material)


def rotation_degrees(obj: bpy.types.Object) -> list[float]:
    return [round(math.degrees(float(value)), 6) for value in obj.rotation_euler]


def framing_report(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    subjects: list[bpy.types.Object],
    resolution: tuple[int, int],
) -> dict[str, object]:
    scene.camera = camera
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in subjects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        points.extend(
            world_to_camera_view(scene, camera, obj.matrix_world @ vertex.co)
            for vertex in mesh.vertices
        )
        evaluated.to_mesh_clear()
    minimum_x = min(point.x for point in points)
    maximum_x = max(point.x for point in points)
    minimum_y = min(point.y for point in points)
    maximum_y = max(point.y for point in points)
    minimum_margin = min(
        minimum_x,
        minimum_y,
        1.0 - maximum_x,
        1.0 - maximum_y,
    )
    return {
        "normalizedBounds": [
            round(minimum_x, 8),
            round(minimum_y, 8),
            round(maximum_x, 8),
            round(maximum_y, 8),
        ],
        "minimumMargin": round(minimum_margin, 8),
        "notCropped": (
            minimum_x >= 0.0
            and minimum_y >= 0.0
            and maximum_x <= 1.0
            and maximum_y <= 1.0
        ),
        "comfortableMargin": minimum_margin >= 0.035,
    }


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
    frames = {}
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
            "maximumRecoveredLocalCoordinateDeltaMm": frame_delta,
        }
    root.rotation_euler[1] = 0.0
    bpy.context.view_layer.update()
    return {
        "anglesDegrees": list(angles),
        "coordinatePolicy": "Texture Coordinate:Object",
        "frames": frames,
        "maximumRecoveredLocalCoordinateDeltaMm": maximum_delta,
        "toleranceMm": 1e-5,
        "pass": maximum_delta <= 1e-5,
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    source_hash_before = sha256(SOURCE_BLEND)
    source_build = json.loads(SOURCE_BUILD_REPORT.read_text(encoding="utf-8"))
    source_audit = json.loads(SOURCE_AUDIT_REPORT.read_text(encoding="utf-8"))
    source_images = json.loads(SOURCE_IMAGE_REPORT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    gate07 = manifest["stages"][6]
    if (
        manifest["revision"] != 34
        or gate07["status"] != "approved"
        or gate07["decision"]["notes"] != "挺好的"
    ):
        raise RuntimeError("Gate 07 rev 1 must be API-approved with exact quote ‘挺好的’.")
    if not all(
        report["status"] == "pass"
        for report in (source_build, source_audit, source_images)
    ):
        raise RuntimeError("Gate 07 source evidence is not valid.")
    if source_hash_before != source_build["outputBlendSha256"]:
        raise RuntimeError("Gate 07 source blend hash changed.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate08_Lighting_Rev001"
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 1
    scene["source_gate07_material_revision"] = 1
    scene["source_gate07_approval_quote"] = "挺好的"
    scene["whole_case_only"] = True
    scene["no_explode"] = True
    scene["gate08_status"] = "ready_for_review"
    scene["gate08_approved"] = False
    scene["gate09_entered"] = False
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False
    scene["blender_exposure_is_unity_runtime_parameter"] = False

    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    studio = [
        obj
        for name in ("M07_StudioCyclorama", "M07_BackViewWall", "M07_SideViewWall")
        if (obj := bpy.data.objects.get(name)) is not None
    ]
    product_renderables = subjects + proxies
    assignment_objects = product_renderables + studio
    approved_material_names = sorted(
        {
            *source_build["materialParameters"].keys(),
            "MAT_M07_ContinuousNeutralFriction",
        }
    )
    geometry_before = VALIDATOR.identity_snapshot(subjects)
    material_digest_before, material_payload_before = approved_material_digest(
        approved_material_names,
        assignment_objects,
    )
    original_slots = {
        obj.name: [slot.material for slot in obj.material_slots]
        for obj in product_renderables
    }
    original_studio_visibility = {obj.name: obj.hide_render for obj in studio}

    for obj in scene.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
        if obj.type == "CAMERA":
            obj.hide_render = True
    for obj in studio:
        obj.hide_render = obj.name != "M07_StudioCyclorama"

    world = scene.world or bpy.data.worlds.new("M08_NeutralWorld")
    scene.world = world
    world.use_nodes = True
    background_node = next(
        (
            node
            for node in world.node_tree.nodes
            if node.bl_idname == "ShaderNodeBackground"
        ),
        None,
    )
    if background_node is None:
        raise RuntimeError("Gate 07 world has no Background node.")
    world_strength_before = float(background_node.inputs["Strength"].default_value)
    world_color_before = tuple(background_node.inputs["Color"].default_value)
    background_node.inputs["Strength"].default_value = 0.20

    light_specs = [
        {
            "name": "M08_KeyStrip_5000K",
            "role": "key",
            "locationMm": (470.0, 360.0, 690.0),
            "targetMm": (0.0, 8.0, 12.0),
            "energy": KEY_ENERGY,
            "ratioToKey": 1.0,
            "sizeMm": 560.0,
            "sizeYmm": 150.0,
            "linearRgb": (1.0, 0.975, 0.95),
            "colorTemperatureKelvin": 5000,
        },
        {
            "name": "M08_FillSoftbox_6200K",
            "role": "fill",
            "locationMm": (-430.0, 100.0, 530.0),
            "targetMm": (0.0, -10.0, 10.0),
            "energy": KEY_ENERGY * FILL_RATIO,
            "ratioToKey": FILL_RATIO,
            "sizeMm": 620.0,
            "sizeYmm": 460.0,
            "linearRgb": (0.955, 0.972, 1.0),
            "colorTemperatureKelvin": 6200,
        },
        {
            "name": "M08_RimStrip_5600K",
            "role": "rim",
            "locationMm": (-300.0, 340.0, -430.0),
            "targetMm": (0.0, 10.0, 0.0),
            "energy": KEY_ENERGY * RIM_RATIO,
            "ratioToKey": RIM_RATIO,
            "sizeMm": 460.0,
            "sizeYmm": 105.0,
            "linearRgb": (0.975, 0.985, 1.0),
            "colorTemperatureKelvin": 5600,
        },
    ]
    lights = {
        spec["role"]: add_area_light(
            spec["name"],
            spec["role"],
            spec["locationMm"],
            spec["targetMm"],
            spec["energy"],
            spec["sizeMm"],
            spec["sizeYmm"],
            spec["linearRgb"],
            spec["colorTemperatureKelvin"],
        )
        for spec in light_specs
    }

    center = (0.0, 0.0, 4.0)
    camera_specs = {
        "hero": {
            "locationMm": spherical_position(center, 900.0, 18.0, 9.0),
            "targetMm": center,
            "lensMm": 60.0,
            "resolution": (1400, 1600),
        },
        "left-oblique": {
            "locationMm": spherical_position(center, 910.0, -24.0, 6.0),
            "targetMm": center,
            "lensMm": 60.0,
            "resolution": (1400, 1600),
        },
        "right-oblique": {
            "locationMm": spherical_position(center, 910.0, 24.0, 6.0),
            "targetMm": center,
            "lensMm": 60.0,
            "resolution": (1400, 1600),
        },
        "low": {
            "locationMm": spherical_position((0.0, -10.0, 2.0), 920.0, 20.0, -7.0),
            "targetMm": (0.0, -10.0, 2.0),
            "lensMm": 60.0,
            "resolution": (1400, 1600),
        },
        "label-closeup": {
            "locationMm": (0.0, 102.0, 450.0),
            "targetMm": (0.0, 99.0, 24.0),
            "lensMm": 92.0,
            "resolution": (1600, 1100),
        },
        "tube-corner": {
            "locationMm": (270.0, 270.0, 520.0),
            "targetMm": (92.0, 130.0, 25.0),
            "lensMm": 104.0,
            "resolution": (1500, 1200),
        },
        "black-panel": {
            "locationMm": (210.0, -72.0, 430.0),
            "targetMm": (0.0, -58.0, 18.0),
            "lensMm": 96.0,
            "resolution": (1500, 1200),
        },
    }
    cameras = {
        view_id: add_camera(
            f"M08_{view_id.replace('-', '_').title()}Camera",
            spec["locationMm"],
            spec["targetMm"],
            spec["lensMm"],
            view_id,
        )
        for view_id, spec in camera_specs.items()
    }
    renderer = configure_render(scene)

    framing = {
        view_id: framing_report(
            scene,
            cameras[view_id],
            subjects,
            camera_specs[view_id]["resolution"],
        )
        for view_id in ("hero", "left-oblique", "right-oblique", "low")
    }
    root = bpy.data.objects["PresentationRoot"]
    grain_objects = [
        bpy.data.objects["FrontPolycarbonateShell"],
        bpy.data.objects["ContinuousTubePerimeter"],
        bpy.data.objects["TactileBackgroundInsert"],
        bpy.data.objects["PhysicalLabel"],
    ]
    grain_stability = stable_local_coordinate_report(grain_objects, root)

    for view_id in ("hero", "left-oblique", "right-oblique", "low"):
        render(
            scene,
            cameras[view_id],
            RAW / f"{view_id}.png",
            camera_specs[view_id]["resolution"],
        )
    shutil.copy2(RAW / "hero.png", RAW / "pass-beauty.png")
    for view_id in ("label-closeup", "tube-corner", "black-panel"):
        render(
            scene,
            cameras[view_id],
            RAW / f"{view_id}.png",
            camera_specs[view_id]["resolution"],
        )

    view_layer = scene.view_layers[0]
    scene.render.engine = "BLENDER_EEVEE"
    technical_resolution = (1200, 1400)
    for obj in studio:
        obj.hide_render = True
    background_node.inputs["Strength"].default_value = 0.0
    technical_light_colors = {
        role: tuple(light.data.color) for role, light in lights.items()
    }
    for light in lights.values():
        light.data.color = (1.0, 1.0, 1.0)
    white_balance_enabled = (
        bool(scene.view_settings.use_white_balance)
        if hasattr(scene.view_settings, "use_white_balance")
        else None
    )
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = False

    clay = simple_principled(
        "MAT_M08_Pass_Clay",
        (0.50, 0.50, 0.50, 1.0),
        0.72,
    )
    view_layer.material_override = clay
    render(
        scene,
        cameras["hero"],
        RAW / "pass-clay.png",
        technical_resolution,
    )
    view_layer.material_override = normal_material()
    render(
        scene,
        cameras["hero"],
        RAW / "pass-normal.png",
        technical_resolution,
    )
    view_layer.material_override = depth_material()
    render(
        scene,
        cameras["hero"],
        RAW / "pass-depth.png",
        technical_resolution,
    )
    view_layer.material_override = None

    roughness_materials = {}
    for obj in product_renderables:
        obj.data.materials.clear()
        for source_material in original_slots[obj.name]:
            roughness = principled_roughness(source_material)
            key = round(roughness, 6)
            roughness_materials.setdefault(
                key,
                emission_material(
                    f"MAT_M08_Pass_Roughness_{key:.6f}",
                    (key, key, key, 1.0),
                ),
            )
            obj.data.materials.append(roughness_materials[key])
    render(
        scene,
        cameras["hero"],
        RAW / "pass-roughness.png",
        technical_resolution,
    )
    restore_slots(product_renderables, original_slots)

    scene.render.engine = "CYCLES"
    view_layer.material_override = None
    background_node.inputs["Strength"].default_value = world_strength_before
    for role, light in lights.items():
        light.data.color = technical_light_colors[role]
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = white_balance_enabled
    for obj in studio:
        obj.hide_render = original_studio_visibility[obj.name]
    root.rotation_euler[1] = 0.0
    bpy.context.view_layer.update()

    geometry_after = VALIDATOR.identity_snapshot(subjects)
    material_digest_after, material_payload_after = approved_material_digest(
        approved_material_names,
        assignment_objects,
    )
    source_hash_after = sha256(SOURCE_BLEND)
    required_outputs = {
        "hero": RAW / "hero.png",
        "leftOblique": RAW / "left-oblique.png",
        "rightOblique": RAW / "right-oblique.png",
        "low": RAW / "low.png",
        "beauty": RAW / "pass-beauty.png",
        "clay": RAW / "pass-clay.png",
        "normal": RAW / "pass-normal.png",
        "depth": RAW / "pass-depth.png",
        "roughness": RAW / "pass-roughness.png",
        "labelCloseup": RAW / "label-closeup.png",
        "tubeCorner": RAW / "tube-corner.png",
        "blackPanel": RAW / "black-panel.png",
    }
    checks = {
        "gate07ApiApprovalExact": (
            gate07["status"] == "approved"
            and gate07["decision"]["notes"] == "挺好的"
        ),
        "sourceBlendUnchanged": source_hash_before == source_hash_after,
        "sourceEvidencePassed": all(
            report["status"] == "pass"
            for report in (source_build, source_audit, source_images)
        ),
        "geometryDigestUnchanged": (
            geometry_before == geometry_after
            and all(
                geometry_after[key] == value
                for key, value in EXPECTED_GEOMETRY.items()
            )
        ),
        "materialDigestUnchanged": (
            material_digest_before == material_digest_after
            and material_payload_before == material_payload_after
        ),
        "requiredOutputsPresent": all(
            path.exists() and path.stat().st_size > 30_000
            for path in required_outputs.values()
        ),
        "grainStableAtFiveAngles": grain_stability["pass"],
        "transparentOrderingPreflight": source_audit["checks"][
            "transparentOrdering"
        ],
        "wholeCaseOnlyNoExplode": (
            bool(scene["whole_case_only"])
            and bool(scene["no_explode"])
            and all(
                obj.hide_render
                for obj in scene.objects
                if obj.name.startswith("EXPLODED_")
            )
        ),
        "fillRatioWithinRequestedRange": 0.25 <= FILL_RATIO <= 0.35,
        "rimRatioWithinRequestedRange": 0.30 <= RIM_RATIO <= 0.45,
        "noRarityOrGreenLight": (
            all(not bool(light["rarity_light"]) for light in lights.values())
            and all(
                float(light.data.color[1])
                <= max(float(light.data.color[0]), float(light.data.color[2]))
                + 0.025
                for light in lights.values()
            )
        ),
        "mainViewsNotCropped": all(
            item["notCropped"] and item["comfortableMargin"]
            for item in framing.values()
        ),
        "gate09NotEntered": not bool(scene["gate09_entered"]),
        "shippingUnityUnchanged": not bool(scene["shipping_unity_changed"]),
        "noBuildInstallPhonePush": not bool(scene["build_install_phone_push"]),
    }
    if not all(checks.values()):
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))

    scene.camera = cameras["hero"]
    scene.render.resolution_x, scene.render.resolution_y = camera_specs["hero"][
        "resolution"
    ]
    scene.render.resolution_percentage = 100
    scene["source_geometry_digest"] = geometry_after["fullGeometryDigest"]
    scene["source_material_digest"] = material_digest_after
    scene["key_fill_rim_ratios"] = [1.0, FILL_RATIO, RIM_RATIO]
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

    camera_report = {}
    for view_id, camera in cameras.items():
        spec = camera_specs[view_id]
        vertical_fov = math.degrees(
            2.0
            * math.atan(
                float(camera.data.sensor_height)
                / (2.0 * float(camera.data.lens))
            )
        )
        camera_report[view_id] = {
            "name": camera.name,
            "locationMm": [round(float(value), 6) for value in camera.location],
            "rotationEulerDegrees": rotation_degrees(camera),
            "targetMm": list(spec["targetMm"]),
            "lensMm": float(camera.data.lens),
            "sensorWidthMm": float(camera.data.sensor_width),
            "sensorHeightMm": float(camera.data.sensor_height),
            "sensorFit": camera.data.sensor_fit,
            "verticalFovDegrees": round(vertical_fov, 6),
            "depthOfField": False,
            "resolution": list(spec["resolution"]),
            "assemblyState": "assembled",
            "shippingRuntimeParameter": False,
        }
        if view_id in framing:
            camera_report[view_id]["framing"] = framing[view_id]

    light_report = []
    for spec in light_specs:
        light = lights[spec["role"]]
        light_report.append(
            {
                **{
                    key: list(value) if isinstance(value, tuple) else value
                    for key, value in spec.items()
                },
                "rotationEulerDegrees": rotation_degrees(light),
                "type": light.data.type,
                "shape": light.data.shape,
                "rarityLight": False,
                "shippingRuntimeParameter": False,
            }
        )

    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "status": "pass",
        "notice": "GATE 08 LIGHTING · READY FOR REVIEW · NOT APPROVED",
        "pipelineRevisionAtBuild": 34,
        "sourceGate07": {
            "materialRevision": 1,
            "approvalQuote": "挺好的",
            "blendPath": str(SOURCE_BLEND.relative_to(REPO_ROOT)),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "sourceAssetIds": list(SOURCE_ASSET_IDS),
            "sourceClaimIds": list(SOURCE_CLAIM_IDS),
        },
        "geometry": {
            "digestBefore": geometry_before["fullGeometryDigest"],
            "digestAfter": geometry_after["fullGeometryDigest"],
            "identityBefore": geometry_before,
            "identityAfter": geometry_after,
            "unchanged": geometry_before == geometry_after,
            "boundsMm": {"width": 228.0, "height": 304.0, "depth": 59.0},
        },
        "materials": {
            "digestMethod": (
                "SHA-256 of approved material node/input/link/custom-property "
                "payload plus product/studio material-slot assignments"
            ),
            "digestBefore": material_digest_before,
            "digestAfter": material_digest_after,
            "unchanged": material_digest_before == material_digest_after,
            "approvedMaterialNames": approved_material_names,
            "assignmentsRestored": material_payload_before["assignments"]
            == material_payload_after["assignments"],
            "transparentOrderingPreflight": source_audit["transparentOrdering"],
        },
        "lighting": {
            "classification": (
                "professional neutral controlled Blender product lookdev; "
                "not Unity runtime lighting"
            ),
            "ratios": {"key": 1.0, "fill": FILL_RATIO, "rim": RIM_RATIO},
            "lights": light_report,
            "world": {
                "linearRgb": list(world_color_before),
                "sourceStrength": world_strength_before,
                "renderStrength": 0.20,
                "hdri": None,
                "fixedGreenBias": False,
                "rarityLight": False,
            },
        },
        "render": {
            **renderer,
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposureEv": scene.view_settings.exposure,
            "gamma": scene.view_settings.gamma,
            "whiteBalanceKelvin": (
                scene.view_settings.white_balance_temperature
                if hasattr(scene.view_settings, "white_balance_temperature")
                else None
            ),
            "whiteBalanceTint": (
                scene.view_settings.white_balance_tint
                if hasattr(scene.view_settings, "white_balance_tint")
                else None
            ),
            "shutterSeconds": None,
            "iso": None,
            "unityRuntimeMapping": (
                "not claimed; Blender exposure, camera, and lights are "
                "Gate 08 review parameters only"
            ),
            "technicalPassEngine": "BLENDER_EEVEE",
        },
        "cameras": camera_report,
        "framing": framing,
        "grainStability": grain_stability,
        "outputs": {
            key: str(path.relative_to(REPO_ROOT))
            for key, path in required_outputs.items()
        },
        "technicalPassPolicy": {
            "beautyUsesApprovedGate07Materials": True,
            "clayNormalDepthRoughnessUseTemporaryOverrides": True,
            "temporaryOverridesAreShippingMaterials": False,
            "approvedAssignmentsRestoredBeforeSave": True,
        },
        "scope": {
            "wholeCaseOnly": True,
            "explode": False,
            "gate08Status": "ready_for_review",
            "gate08Approved": False,
            "gate09Entered": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO_ROOT)),
        "outputBlendSha256": sha256(OUTPUT_BLEND),
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputBlend": str(OUTPUT_BLEND),
                "geometryDigest": report["geometry"]["digestAfter"],
                "materialDigest": report["materials"]["digestAfter"],
                "ratios": report["lighting"]["ratios"],
                "verticalFovDegrees": report["cameras"]["hero"][
                    "verticalFovDegrees"
                ],
                "exposureEv": report["render"]["exposureEv"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
