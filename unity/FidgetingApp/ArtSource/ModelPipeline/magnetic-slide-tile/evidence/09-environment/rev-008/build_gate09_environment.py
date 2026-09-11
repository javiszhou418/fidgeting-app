#!/usr/bin/env python3
"""Build portable Gate 09 environment evidence from approved Gate 08."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE_BLEND = MODEL_ROOT / "evidence/08-lighting/rev-002/magnetic-slide-tile-lighting-r002.blend"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-environment-r008.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-environment-r008-lookdev.glb"
HDRI_EXR = HERE / "magnetic-slide-tile-shipping-studio-r008.exr"
HDRI_PREVIEW = HERE / "magnetic-slide-tile-shipping-studio-r008-preview.png"
REPORT_PATH = HERE / "environment-validation.json"
SOURCE_SHA256 = "547055f5c04890575fab4b43e2287a62086ee7b4ee2b0e22fa3f92f0ea2e21b1"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
MATERIAL_DIGEST = "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8"
SOURCE_MATERIAL_SCENE_DIGEST = "db330337c1d1b4222f21c3c22da26f77a3576f8699d852945ba82de2e40ca4de"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]
HIERARCHY = [
    "MagneticSlideTile_G05_R006", "BottomExterior", "FixedAxis", "FixedAxisBoss",
    "MinimumOverlapDisk", "RotatingCarrier", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
    "UnknownSprings", "UnknownPreload", "MovingTop", "TopLocalSlide", "MovingTopBody",
    "TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight",
]
APPROVED_MATERIALS = [
    "M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct",
    "M07R11_PolishedSilver", "M07R11_InternalSilverReference",
    "M07R11_DarkExteriorSide", "M07R11_NeutralTechnical",
    "M07R11_BallCandidate_UnknownMaterial",
]
SOURCE_CAMERAS = [
    "M08R2_Hero", "M08R2_LeftOblique", "M08R2_RightOblique", "M08R2_Low",
    "M08R2_TopReveal", "M08R2_Underside", "M08R2_Mechanism",
]
SOURCE_LIGHTS = [
    "M08R2_KeySoftbox", "M08R2_FillSoftbox",
    "M08R2_SilverRimStrip", "M08R2_MechanismReveal",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def serial(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return [round(float(item), 9) for item in value]
    except (TypeError, ValueError):
        return str(value)


def object_matrix(obj):
    return [[round(value, 9) for value in row] for row in obj.matrix_world]


def hierarchy_snapshot():
    return {
        name: {
            "type": bpy.data.objects[name].type,
            "parent": bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None,
            "matrixWorld": object_matrix(bpy.data.objects[name]),
        }
        for name in HIERARCHY
    }


def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def uv_digest():
    digest = hashlib.sha256()
    for name in CORE:
        mesh = bpy.data.objects[name].data
        digest.update(name.encode())
        for layer in mesh.uv_layers:
            digest.update(layer.name.encode())
            for loop in layer.data:
                digest.update(f"{loop.uv.x:.9f},{loop.uv.y:.9f};".encode())
    return digest.hexdigest()


def material_digest():
    payload = {}
    for name in APPROVED_MATERIALS:
        material = bpy.data.materials[name]
        nodes = []
        for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
            nodes.append({
                "name": node.name,
                "type": node.bl_idname,
                "inputs": {
                    socket.name: serial(socket.default_value)
                    for socket in node.inputs if hasattr(socket, "default_value")
                },
                "image": node.image.name if hasattr(node, "image") and node.image else None,
            })
        payload[name] = {
            "nodes": nodes,
            "props": {key: serial(material[key]) for key in sorted(material.keys())},
        }
    for name in CORE:
        obj = bpy.data.objects[name]
        payload[name] = {
            "slots": [material.name for material in obj.data.materials],
            "indices": [polygon.material_index for polygon in obj.data.polygons],
        }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def light_digest():
    payload = {}
    for name in SOURCE_LIGHTS:
        obj = bpy.data.objects[name]
        payload[name] = {
            "matrix": object_matrix(obj),
            "type": obj.data.type,
            "energy": round(obj.data.energy, 6),
            "color": [round(value, 9) for value in obj.data.color],
            "size": round(obj.data.size, 6),
            "role": obj.get("lightingRole"),
            "cctK": obj.get("cctK"),
        }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def camera_digest():
    payload = {}
    for name in SOURCE_CAMERAS:
        obj = bpy.data.objects[name]
        payload[name] = {
            "matrix": object_matrix(obj),
            "lens": round(obj.data.lens, 6),
            "sensor": round(obj.data.sensor_width, 6),
            "target": list(obj.get("targetMm", [])),
        }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(name, location, target, lens):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["targetMm"] = list(target)
    obj["gate09_revision"] = 8
    return obj


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def solid_material(name, color, roughness):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0)
    material["gate09EnvironmentOnly"] = True
    return material


def angular_lobe(theta, elevation, azimuth, target_elevation, sigma):
    cosine = (
        np.sin(elevation) * math.sin(target_elevation)
        + np.cos(elevation) * math.cos(target_elevation) * np.cos(theta - azimuth)
    )
    distance = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.exp(-0.5 * (distance / sigma) ** 2)


def create_hdri():
    width, height = 2048, 1024
    x = np.linspace(-math.pi, math.pi, width, endpoint=True, dtype=np.float32)
    y = np.linspace(0, 1, height, endpoint=True, dtype=np.float32)
    theta, yn = np.meshgrid(x, y)
    elevation = math.pi * 0.5 - yn * math.pi
    horizon = np.exp(-0.5 * (elevation / math.radians(22)) ** 2)
    upper = np.clip(elevation / (math.pi * 0.5), 0, 1)
    lower = np.clip(-elevation / (math.pi * 0.5), 0, 1)
    rgb = np.zeros((height, width, 3), dtype=np.float32)
    rgb += np.array([0.030, 0.022, 0.025], dtype=np.float32)
    rgb += horizon[:, :, None] * np.array([0.080, 0.058, 0.050], dtype=np.float32)
    rgb += upper[:, :, None] * np.array([0.014, 0.012, 0.016], dtype=np.float32)
    rgb -= lower[:, :, None] * np.array([0.009, 0.007, 0.006], dtype=np.float32)
    key = angular_lobe(theta, elevation, math.radians(-52), math.radians(26), math.radians(11))
    rim = angular_lobe(theta, elevation, math.radians(104), math.radians(18), math.radians(8))
    top = angular_lobe(theta, elevation, math.radians(168), math.radians(56), math.radians(14))
    canyon = angular_lobe(theta, elevation, math.radians(26), math.radians(2), math.radians(34))
    rgb += key[:, :, None] * np.array([2.6, 2.42, 2.20], dtype=np.float32)
    rgb += rim[:, :, None] * np.array([1.55, 1.58, 1.62], dtype=np.float32)
    rgb += top[:, :, None] * np.array([0.72, 0.66, 0.60], dtype=np.float32)
    rgb += canyon[:, :, None] * np.array([0.12, 0.034, 0.018], dtype=np.float32)
    rgb = np.clip(rgb, 0.006, None)
    rgb[:, -1, :] = rgb[:, 0, :]
    alpha = np.ones((height, width, 1), dtype=np.float32)
    rgba = np.concatenate([rgb, alpha], axis=2)
    image = bpy.data.images.get("M09R8_PortableShippingStudio") or bpy.data.images.new(
        "M09R8_PortableShippingStudio",
        width=width,
        height=height,
        alpha=True,
        float_buffer=True,
    )
    image.pixels.foreach_set(rgba.reshape(-1))
    image.colorspace_settings.name = "Non-Color"
    image.filepath_raw = str(HDRI_EXR)
    image.file_format = "OPEN_EXR"
    image.save()
    preview = np.power(np.clip(rgb / (1.0 + rgb), 0, 1), 1.0 / 2.2)
    preview_rgba = np.concatenate([preview, alpha], axis=2)
    preview_image = bpy.data.images.get("M09R8_PortableShippingStudioPreview") or bpy.data.images.new(
        "M09R8_PortableShippingStudioPreview",
        width=width,
        height=height,
        alpha=True,
        float_buffer=False,
    )
    preview_image.pixels.foreach_set(preview_rgba.reshape(-1))
    preview_image.filepath_raw = str(HDRI_PREVIEW)
    preview_image.file_format = "PNG"
    preview_image.save()
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    metadata = {
        "schemaVersion": 1,
        "asset": HDRI_EXR.name,
        "projection": "equirectangular",
        "resolutionPx": [width, height],
        "format": "OpenEXR RGBA half/float scene-linear",
        "colorPrimaries": "Rec.709",
        "transfer": "linear",
        "whitePoint": "D65",
        "alpha": 1,
        "wrap": "repeat-u-clamp-v",
        "seamMaxAbsoluteLinearDelta": float(np.max(np.abs(rgb[:, 0, :] - rgb[:, -1, :]))),
        "minimumLinearLuminance": float(luminance.min()),
        "maximumLinearLuminance": float(luminance.max()),
        "p01LinearLuminance": float(np.percentile(luminance, 1)),
        "p99LinearLuminance": float(np.percentile(luminance, 99)),
        "dynamicRangeStopsP01ToP99": float(
            math.log2(max(float(np.percentile(luminance, 99)), 1e-6) / max(float(np.percentile(luminance, 1)), 1e-6))
        ),
        "source": "deterministic periodic analytic environment; no external HDRI",
        "unityIntent": "Import later as linear Cubemap from equirectangular EXR; do not apply settings before Gate 10/11.",
        "sha256": sha256(HDRI_EXR),
    }
    (HERE / "portable-hdri-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return image, metadata


def set_neutral_environment(scene, neutral_ground):
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Color"].default_value = (0.055, 0.055, 0.055, 1)
    background.inputs["Strength"].default_value = 0.18
    links.new(background.outputs["Background"], output.inputs["Surface"])
    world["gate09Environment"] = "neutral"
    world["hdri"] = "none"
    ground = bpy.data.objects["M08R2_NeutralGround"]
    ground.data.materials.clear()
    ground.data.materials.append(neutral_ground)
    bpy.context.view_layer.update()


def set_shipping_environment(scene, hdri_image, shipping_ground):
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 0.65
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.name = "M09R8_PortableShippingEXR"
    environment.image = hdri_image
    environment.projection = "EQUIRECTANGULAR"
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    world["gate09Environment"] = "target-shipping"
    world["hdri"] = HDRI_EXR.name
    world["projection"] = "equirectangular"
    world["rotationDegrees"] = 0.0
    world["strength"] = 0.65
    ground = bpy.data.objects["M08R2_NeutralGround"]
    ground.data.materials.clear()
    ground.data.materials.append(shipping_ground)
    bpy.context.view_layer.update()


def set_pose(travel, angle, lift=0.0):
    bpy.data.objects["RotatingCarrier"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["MovingTop"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["TopLocalSlide"].location = (0, -travel, lift)
    bpy.context.view_layer.update()


def render(scene, camera, filename, width=1400, height=1100):
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def main():
    if sha256(SOURCE_BLEND) != SOURCE_SHA256:
        raise RuntimeError("Approved Gate 08 blend hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the approved Gate 08 blend before running.")
    scene = bpy.context.scene
    geometry_before = geometry_digest()
    uv_before = uv_digest()
    material_before = material_digest()
    hierarchy_before = hierarchy_snapshot()
    lights_before = light_digest()
    cameras_before = camera_digest()
    gate08_report = json.loads(
        (MODEL_ROOT / "evidence/08-lighting/rev-002/lighting-validation.json").read_text(encoding="utf-8")
    )
    if (
        geometry_before != GEOMETRY_DIGEST
        or material_before != SOURCE_MATERIAL_SCENE_DIGEST
        or gate08_report["materials"]["after"] != MATERIAL_DIGEST
    ):
        raise RuntimeError(
            f"Approved geometry or material digest drift: "
            f"geometry={geometry_before}, material={material_before}."
        )
    source_report = json.loads(
        (MODEL_ROOT / "evidence/06-geometry/rev-004/geometry-validation.json").read_text(encoding="utf-8")
    )
    if source_report["denseSweep"]["allValid"] is not True or source_report["contractSha256"] != CONTRACT_SHA256:
        raise RuntimeError("Motion containment source is stale.")

    scene["gate"] = "09-environment"
    scene["environment_revision"] = 8
    scene["gate08_source_sha256"] = SOURCE_SHA256
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["approved_material_digest"] = MATERIAL_DIGEST
    scene["approved_light_digest"] = lights_before
    scene["approved_camera_digest"] = cameras_before
    scene["self_motion"] = False
    scene["unity_import_applied"] = False
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 18
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.35
    scene.view_settings.gamma = 1.0

    neutral_ground = bpy.data.materials["M08R2_NeutralGround"]
    shipping_ground = solid_material("M09R8_PortableGround", (0.018, 0.016, 0.017, 1), 0.42)
    shipping_ground["baseColorLinear"] = [0.018, 0.016, 0.017, 1]
    shipping_ground["metallic"] = 0.0
    shipping_ground["roughness"] = 0.42
    hdri_image, hdri_metadata = create_hdri()
    cameras = {
        "hero": bpy.data.objects["M08R2_Hero"],
        "left": bpy.data.objects["M08R2_LeftOblique"],
        "right": bpy.data.objects["M08R2_RightOblique"],
        "low": bpy.data.objects["M08R2_Low"],
        "top": bpy.data.objects["M08R2_TopReveal"],
        "underside": bpy.data.objects["M08R2_Underside"],
        "mechanism": bpy.data.objects["M08R2_Mechanism"],
        "reflection": create_camera("M09R8_ReflectionCloseup", (44, -76, 34), (0, -4, 6), 118),
        "open": create_camera("M09R8_OpenHero", (96, -152, 78), (0, -10, 5), 70),
        "axis": create_camera("M09R8_AxisGrazing", (38, -60, 9), (0, -9, 5.9), 135),
    }

    set_pose(0, 0)
    set_neutral_environment(scene, neutral_ground)
    render(scene, cameras["hero"], "neutral-closed-hero.png")
    set_shipping_environment(scene, hdri_image, shipping_ground)
    render(scene, cameras["hero"], "shipping-closed-hero.png")
    render(scene, cameras["left"], "shipping-left-oblique.png")
    render(scene, cameras["right"], "shipping-right-oblique.png")
    render(scene, cameras["low"], "shipping-low-angle.png")

    set_pose(18.076433121019107, 0)
    set_neutral_environment(scene, neutral_ground)
    render(scene, cameras["open"], "neutral-max-open.png")
    set_shipping_environment(scene, hdri_image, shipping_ground)
    render(scene, cameras["open"], "shipping-max-open.png")
    axis_hidden = [
        bpy.data.objects[name] for name in [
            "MovingTopBody", "RotatingCarrierBody", "CarrierFollowerLeft",
            "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
        ]
    ]
    for obj in axis_hidden:
        obj.hide_render = True
    render(scene, cameras["axis"], "shipping-flat-plane-raised-axis.png")
    for obj in axis_hidden:
        obj.hide_render = False
    set_pose(7, 12)
    render(scene, cameras["hero"], "shipping-detent-12.png")
    set_pose(7, 36)
    render(scene, cameras["hero"], "shipping-detent-36.png")

    set_pose(0, 0)
    set_neutral_environment(scene, neutral_ground)
    render(scene, cameras["reflection"], "neutral-reflection-closeup.png")
    set_shipping_environment(scene, hdri_image, shipping_ground)
    render(scene, cameras["reflection"], "shipping-reflection-closeup.png")

    set_pose(5, 0, 15)
    top = bpy.data.objects["MovingTopBody"]
    top.rotation_euler.x = math.pi
    hidden = [
        bpy.data.objects["BottomExterior"], bpy.data.objects["FixedAxisBoss"],
        bpy.data.objects["RotatingCarrierBody"], bpy.data.objects["CarrierFollowerLeft"],
        bpy.data.objects["CarrierFollowerRight"], bpy.data.objects["BallCandidateLeft"],
        bpy.data.objects["BallCandidateRight"], bpy.data.objects["M08R2_NeutralGround"],
    ]
    for obj in hidden:
        obj.hide_render = True
    render(scene, cameras["underside"], "shipping-underside-grooves.png")
    for obj in hidden:
        obj.hide_render = False
    top.rotation_euler.x = 0
    set_pose(9, 12, 10)
    bpy.data.objects["BottomExterior"].hide_render = True
    render(scene, cameras["mechanism"], "shipping-carrier-clearance.png")
    bpy.data.objects["BottomExterior"].hide_render = False

    set_pose(8, 12)
    bpy.ops.object.select_all(action="DESELECT")
    for name in HIERARCHY:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["MagneticSlideTile_G05_R006"]
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
    )

    neutral_frames = HERE / "turntable-neutral"
    shipping_frames = HERE / "turntable-shipping"
    neutral_frames.mkdir(exist_ok=True)
    shipping_frames.mkdir(exist_ok=True)
    hero_location = cameras["hero"].location.copy()
    hero_rotation = cameras["hero"].rotation_euler.copy()
    target = Vector((0, -2, 5))
    radius = 132
    set_pose(8, 12)
    for frame in range(24):
        angle = math.tau * frame / 24
        cameras["hero"].location = (
            radius * math.sin(angle),
            -2 - radius * math.cos(angle),
            52 + 13 * math.sin(angle * 2),
        )
        look_at(cameras["hero"], target)
        set_neutral_environment(scene, neutral_ground)
        render(scene, cameras["hero"], f"turntable-neutral/frame-{frame:03d}.png", 720, 540)
        set_shipping_environment(scene, hdri_image, shipping_ground)
        render(scene, cameras["hero"], f"turntable-shipping/frame-{frame:03d}.png", 720, 540)

    cameras["hero"].location = hero_location
    cameras["hero"].rotation_euler = hero_rotation
    set_pose(0, 0)
    set_shipping_environment(scene, hdri_image, shipping_ground)
    bpy.context.view_layer.update()
    geometry_after = geometry_digest()
    uv_after = uv_digest()
    material_after = material_digest()
    hierarchy_after = hierarchy_snapshot()
    lights_after = light_digest()
    cameras_after = camera_digest()
    approved_emission = {}
    for name in APPROVED_MATERIALS:
        bsdf = next(node for node in bpy.data.materials[name].node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        approved_emission[name] = float(bsdf.inputs["Emission Strength"].default_value)
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "pass": False,
        "sourceGate08": {
            "lightingRevision": 2,
            "blendSha256": SOURCE_SHA256,
            "approvalWording": "进行下一步吧",
        },
        "contractSha256": CONTRACT_SHA256,
        "geometry": {"before": geometry_before, "after": geometry_after, "expected": GEOMETRY_DIGEST},
        "uv": {"before": uv_before, "after": uv_after},
        "materials": {
            "sceneFingerprintBefore": material_before,
            "sceneFingerprintAfter": material_after,
            "sceneFingerprintExpected": SOURCE_MATERIAL_SCENE_DIGEST,
            "approvedSemanticDigest": MATERIAL_DIGEST,
            "gate08ValidatedSemanticDigest": gate08_report["materials"]["after"],
            "emission": approved_emission,
        },
        "hierarchy": {"before": hierarchy_before, "after": hierarchy_after},
        "lighting": {"before": lights_before, "after": lights_after},
        "cameras": {"before": cameras_before, "after": cameras_after},
        "environment": {
            "neutral": {
                "worldLinearRgb": [0.055, 0.055, 0.055],
                "strength": 0.18,
                "hdri": None,
                "groundMaterial": "M08R2_NeutralGround",
            },
            "targetShipping": {
                "hdri": HDRI_EXR.name,
                "hdriSha256": hdri_metadata["sha256"],
                "projection": "equirectangular",
                "rotationDegrees": 0,
                "strength": 0.65,
                "ground": {
                    "material": shipping_ground.name,
                    "baseColorLinear": [0.018, 0.016, 0.017, 1],
                    "metallic": 0,
                    "roughness": 0.42,
                },
            },
            "identicalAcrossPair": ["geometry", "hierarchy", "pivot", "uv", "materials", "lights", "camera", "pose", "exposure"],
            "differenceAllowed": ["world", "reflection-input", "background", "ground"],
        },
        "hdriMetadata": hdri_metadata,
        "motionContainment": {
            "sourceAssetId": "magnetic-slide-tile-geometry-validation-r004",
            "denseSweepSamples": source_report["denseSweep"]["sampleCount"],
            "angularStepDegrees": source_report["denseSweep"]["angularStepDegrees"],
            "allValid": source_report["denseSweep"]["allValid"],
            "axisWorldMm": [0, -9.5, 0],
            "detentAnglesDegrees": [0, 12, 36],
            "maxTravelMm": 18.076433121019107,
        },
        "views": [
            "neutral-closed-hero.png", "shipping-closed-hero.png",
            "neutral-max-open.png", "shipping-max-open.png",
            "shipping-left-oblique.png", "shipping-right-oblique.png", "shipping-low-angle.png",
            "shipping-detent-12.png", "shipping-detent-36.png",
            "neutral-reflection-closeup.png", "shipping-reflection-closeup.png",
            "shipping-flat-plane-raised-axis.png", "shipping-underside-grooves.png",
            "shipping-carrier-clearance.png",
        ],
        "animatedObjects": [
            obj.name for obj in bpy.data.objects
            if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
        ],
        "unityImportApplied": False,
        "buildInstallDevice": False,
    }
    checks = {
        "sourceHash": sha256(SOURCE_BLEND) == SOURCE_SHA256,
        "contractHash": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
        "geometryUnchanged": geometry_before == geometry_after == GEOMETRY_DIGEST,
        "uvUnchanged": uv_before == uv_after,
        "materialsUnchanged": material_before == material_after == SOURCE_MATERIAL_SCENE_DIGEST
        and gate08_report["materials"]["after"] == MATERIAL_DIGEST,
        "hierarchyRestored": hierarchy_before == hierarchy_after,
        "lightsUnchanged": lights_before == lights_after,
        "sourceCamerasUnchanged": cameras_before == cameras_after,
        "approvedEmissionZero": all(value == 0 for value in approved_emission.values()),
        "portableHdriWritten": HDRI_EXR.exists() and HDRI_PREVIEW.exists(),
        "hdriSeamContinuous": hdri_metadata["seamMaxAbsoluteLinearDelta"] <= 1e-6,
        "hdriDynamicRange": hdri_metadata["dynamicRangeStopsP01ToP99"] >= 4,
        "requiredViews": all((HERE / name).exists() for name in report["views"]),
        "turntablePairs": len(list(neutral_frames.glob("frame-*.png"))) == 24
        and len(list(shipping_frames.glob("frame-*.png"))) == 24,
        "motionContainmentPreserved": report["motionContainment"]["allValid"]
        and report["motionContainment"]["denseSweepSamples"] == 3600,
        "zeroSelfMotion": not report["animatedObjects"] and scene["self_motion"] is False,
        "glbWritten": OUTPUT_GLB.exists(),
        "unityNotApplied": scene["unity_import_applied"] is False,
        "oldShippingUntouched": scene["shipping_unity_changed"] is False,
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["checks"]["blendWritten"] = OUTPUT_BLEND.exists()
    report["pass"] = all(report["checks"].values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "geometryDigest": geometry_after,
        "materialDigest": material_after,
        "lightDigest": lights_after,
        "cameraDigest": cameras_after,
        "hdriSha256": hdri_metadata["sha256"],
        "hdriSeam": hdri_metadata["seamMaxAbsoluteLinearDelta"],
        "hdriDynamicRangeStops": hdri_metadata["dynamicRangeStopsP01ToP99"],
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
    }, indent=2))


if __name__ == "__main__":
    main()

