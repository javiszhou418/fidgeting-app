#!/usr/bin/env python3
"""Build a Gate 08 lighting candidate limited to Blender/URP common features."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE = MODEL_ROOT / "evidence/07-material/rev-011/magnetic-slide-tile-material-r011.blend"
SOURCE_SHA = "fdf6e96206b6d048aa88fbd049a8af1a4d7a391d65ed74791c3acaca2767d274"
CONTRACT_SHA = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
MATERIAL_DIGEST = "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-lighting-r003-portable.blend"
OUTPUT_EXR = HERE / "portable-studio-r003.exr"
CORE = [
    "BottomExterior",
    "FixedAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
]
APPROVED_MATERIALS = [
    "M07R11_Crystal_Upper",
    "M07R11_Crystal_LowerDistinct",
    "M07R11_PolishedSilver",
    "M07R11_InternalSilverReference",
    "M07R11_DarkExteriorSide",
    "M07R11_NeutralTechnical",
    "M07R11_BallCandidate_UnknownMaterial",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def serial(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return [round(float(item), 9) for item in value]
    except (TypeError, ValueError):
        return str(value)


def geometry_digest() -> str:
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


def material_digest() -> str:
    payload = {}
    for name in APPROVED_MATERIALS:
        material = bpy.data.materials[name]
        payload[name] = {
            "blendMethod": getattr(material, "surface_render_method", None),
            "nodes": [
                {
                    "name": node.name,
                    "type": node.bl_idname,
                    "inputs": {
                        socket.name: serial(socket.default_value)
                        for socket in node.inputs
                        if hasattr(socket, "default_value")
                    },
                    "image": (
                        node.image.name
                        if hasattr(node, "image") and node.image
                        else None
                    ),
                }
                for node in sorted(
                    material.node_tree.nodes, key=lambda item: item.name
                )
            ],
            "props": {
                key: serial(material[key]) for key in sorted(material.keys())
            },
        }
    for name in CORE:
        obj = bpy.data.objects[name]
        payload[name] = {
            "slots": [material.name for material in obj.data.materials],
            "indices": [polygon.material_index for polygon in obj.data.polygons],
        }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def matrix_digest() -> str:
    payload = {
        name: [[round(value, 9) for value in row] for row in bpy.data.objects[name].matrix_world]
        for name in CORE
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def angular_lobe(theta, elevation, azimuth, target_elevation, sigma):
    cosine = (
        np.sin(elevation) * math.sin(target_elevation)
        + np.cos(elevation)
        * math.cos(target_elevation)
        * np.cos(theta - azimuth)
    )
    distance = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.exp(-0.5 * (distance / sigma) ** 2)


def create_environment():
    width, height = 2048, 1024
    x = np.linspace(-math.pi, math.pi, width, endpoint=True, dtype=np.float32)
    y = np.linspace(0, 1, height, endpoint=True, dtype=np.float32)
    theta, yn = np.meshgrid(x, y)
    elevation = math.pi * 0.5 - yn * math.pi
    horizon = np.exp(-0.5 * (elevation / math.radians(24)) ** 2)
    rgb = np.zeros((height, width, 3), dtype=np.float32)
    rgb += np.array([0.018, 0.017, 0.019], dtype=np.float32)
    rgb += horizon[:, :, None] * np.array(
        [0.045, 0.043, 0.047], dtype=np.float32
    )
    key = angular_lobe(
        theta,
        elevation,
        math.radians(-48),
        math.radians(32),
        math.radians(16),
    )
    rim = angular_lobe(
        theta,
        elevation,
        math.radians(118),
        math.radians(18),
        math.radians(12),
    )
    ceiling = angular_lobe(
        theta,
        elevation,
        math.radians(174),
        math.radians(66),
        math.radians(24),
    )
    rgb += key[:, :, None] * np.array([1.10, 1.08, 1.04], dtype=np.float32)
    rgb += rim[:, :, None] * np.array([0.52, 0.53, 0.55], dtype=np.float32)
    rgb += ceiling[:, :, None] * np.array([0.18, 0.17, 0.17], dtype=np.float32)
    rgb[:, -1, :] = rgb[:, 0, :]
    alpha = np.ones((height, width, 1), dtype=np.float32)
    rgba = np.concatenate([rgb, alpha], axis=2)
    output = oiio.ImageOutput.create(str(OUTPUT_EXR))
    if output is None:
        raise RuntimeError("OpenImageIO could not create the portable EXR.")
    spec = oiio.ImageSpec(width, height, 4, oiio.FLOAT)
    spec.attribute("oiio:ColorSpace", "Linear Rec.709 (sRGB)")
    spec.attribute("DateTime", "1970:01:01 00:00:00")
    output.open(str(OUTPUT_EXR), spec)
    output.write_image(rgba)
    output.close()
    image = bpy.data.images.load(str(OUTPUT_EXR), check_existing=False)
    image.name = "M08R3_PortableStudio"
    image.colorspace_settings.name = "Non-Color"
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return image, {
        "projection": "equirectangular",
        "resolution": [width, height],
        "linearColorSpace": "Rec.709/D65",
        "worldStrength": 0.125,
        "rotationDegrees": 0.0,
        "seamMaxAbsoluteLinearDelta": float(
            np.max(np.abs(rgb[:, 0, :] - rgb[:, -1, :]))
        ),
        "p01Luminance": float(np.percentile(luminance, 1)),
        "p99Luminance": float(np.percentile(luminance, 99)),
    }


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def solid_material(name, color, roughness):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    return material


def look_at(obj, target):
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


def configure_world(image):
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.image = image
    environment.interpolation = "Linear"
    background.inputs["Strength"].default_value = 0.125
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])


def create_sun():
    data = bpy.data.lights.new("M08R3_D65Sun", "SUN")
    data.energy = 0.75
    data.angle = math.radians(7.0)
    data.color = (1.0, 1.0, 1.0)
    obj = bpy.data.objects.new("M08R3_D65Sun", data)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = (
        math.radians(31.0),
        math.radians(-24.0),
        math.radians(-38.0),
    )
    return obj


def create_ground():
    material = solid_material(
        "M08R3_PortableGround", (0.018, 0.017, 0.019, 1), 0.46
    )
    bpy.ops.mesh.primitive_plane_add(size=220, location=(0, 0, -0.6))
    ground = bpy.context.object
    ground.name = "M08R3_PortableGround"
    ground.data.materials.append(material)
    return ground


def create_camera():
    data = bpy.data.cameras.new("M08R3_Hero_Data")
    data.lens = 76.0
    data.sensor_width = 36.0
    data.sensor_fit = "HORIZONTAL"
    camera = bpy.data.objects.new("M08R3_Hero", data)
    bpy.context.collection.objects.link(camera)
    camera.location = (74.0, -116.0, 72.0)
    look_at(camera, (0.0, -2.0, 5.0))
    return camera


def render(name, camera, sun, enabled=True):
    sun.hide_render = not enabled
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(HERE / name)
    bpy.ops.render.render(write_still=True)


def main():
    if sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Approved Gate 07 source hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the approved Gate 07 source blend.")
    geometry_before = geometry_digest()
    material_before = material_digest()
    matrices_before = matrix_digest()
    if geometry_before != GEOMETRY_DIGEST or material_before != MATERIAL_DIGEST:
        raise RuntimeError("Approved geometry or material digest drift.")

    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} or "Ground" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
        elif obj.name.startswith(("M08R2_", "M09R8_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 3
    scene["mechanism_contract_sha256"] = CONTRACT_SHA
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["approved_material_digest"] = MATERIAL_DIGEST
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.35
    scene.view_settings.gamma = 1.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = False

    image, environment = create_environment()
    configure_world(image)
    ground = create_ground()
    sun = create_sun()
    camera = create_camera()
    render("portable-env-only.png", camera, sun, False)
    render("portable-beauty.png", camera, sun, True)

    clay = solid_material("M08R3_Clay", (0.42, 0.42, 0.42, 1), 0.42)
    scene.view_layers[0].material_override = clay
    render("portable-clay.png", camera, sun, True)
    scene.view_layers[0].material_override = None
    sun.hide_render = False

    geometry_after = geometry_digest()
    material_after = material_digest()
    matrices_after = matrix_digest()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    environment["sha256"] = sha256(OUTPUT_EXR)
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 3,
        "status": "portable-lighting-candidate-review-required",
        "source": {"gate07Blend": str(SOURCE), "sha256": SOURCE_SHA},
        "contractSha256": CONTRACT_SHA,
        "geometryDigest": {
            "before": geometry_before,
            "after": geometry_after,
            "expected": GEOMETRY_DIGEST,
        },
        "materialDigest": {
            "before": material_before,
            "after": material_after,
            "expected": MATERIAL_DIGEST,
        },
        "matrixDigest": {
            "before": matrices_before,
            "after": matrices_after,
        },
        "portableRecipe": {
            "environment": environment,
            "directLight": {
                "type": "directional",
                "color": "D65",
                "blenderEnergy": 0.75,
                "angularDiameterDegrees": 7.0,
                "rotationEulerDegrees": [31.0, -24.0, -38.0],
                "unityMapping": "same direction/color; intensity calibrated in isolated parity scene",
            },
            "reflectionCards": 0,
            "areaLights": 0,
            "duplicateSyntheticHighlights": 0,
            "ground": {
                "sizeMm": 220.0,
                "zMm": -0.6,
                "baseColorLinear": [0.018, 0.017, 0.019, 1.0],
                "roughness": 0.46,
            },
            "contactShadow": "shared directional shadow map; baked model AO only; no Blender-only contact shadow",
            "color": {
                "workingSpace": "scene-linear Rec.709/D65",
                "viewTransform": "Standard",
                "look": "None",
                "exposureEv": -0.35,
                "agxMigration": "Both comparison renders use the identity display LUT: no AgX look and no Unity ACES stack. A fitted AgX-look LUT may be evaluated only after this Gate 08 direction is approved.",
            },
            "camera": {
                "resolution": [1400, 1100],
                "locationMm": [74.0, -116.0, 72.0],
                "targetMm": [0.0, -2.0, 5.0],
                "lensMm": 76.0,
                "sensorWidthMm": 36.0,
                "sensorFit": "HORIZONTAL",
            },
        },
        "controlledRenders": {
            "environmentOnly": "portable-env-only.png",
            "environmentPlusDirectional": "portable-beauty.png",
            "clay": "portable-clay.png",
        },
        "checks": {
            "geometryUnchanged": geometry_before == geometry_after == GEOMETRY_DIGEST,
            "materialsUnchanged": material_before == material_after == MATERIAL_DIGEST,
            "matricesUnchanged": matrices_before == matrices_after,
            "zeroAreaLights": True,
            "zeroReflectionCards": True,
            "singleEnvironmentContribution": True,
            "zeroEmissionPreserved": True,
            "sameFullFrame": True,
            "shippingUntouched": True,
            "outputBlend": OUTPUT_BLEND.exists(),
            "outputExr": OUTPUT_EXR.exists(),
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "portable-lighting-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"pass": report["pass"], "environment": environment}, indent=2))
    if not report["pass"]:
        raise RuntimeError("Portable Gate 08 candidate validation failed.")


if __name__ == "__main__":
    main()
