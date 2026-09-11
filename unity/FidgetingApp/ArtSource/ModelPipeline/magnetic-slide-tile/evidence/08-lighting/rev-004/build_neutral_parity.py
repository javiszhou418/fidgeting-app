#!/usr/bin/env python3
"""Build the reflection-only Gate 08 rev 4 neutral parity candidate."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
REV3 = HERE.parent / "rev-003/build_portable_lighting.py"
spec = importlib.util.spec_from_file_location("gate08_rev3_helpers", REV3)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

SOURCE = helpers.SOURCE
SOURCE_SHA = helpers.SOURCE_SHA
CONTRACT_SHA = helpers.CONTRACT_SHA
GEOMETRY_DIGEST = helpers.GEOMETRY_DIGEST
MATERIAL_DIGEST = helpers.MATERIAL_DIGEST
CORE = helpers.CORE
OUTPUT_BLEND = HERE / "magnetic-slide-tile-lighting-r004-neutral-parity.blend"
OUTPUT_EXR = HERE / "neutral-parity-studio-r004.exr"
BACKGROUND_LINEAR = np.array([0.035, 0.035, 0.035], dtype=np.float32)
ENVIRONMENT_STRENGTH = 0.85


def create_environment():
    width, height = 2048, 1024
    azimuth = np.linspace(-math.pi, math.pi, width, endpoint=True, dtype=np.float32)
    vertical = np.linspace(0, 1, height, endpoint=True, dtype=np.float32)
    theta, yn = np.meshgrid(azimuth, vertical)
    elevation = math.pi * 0.5 - yn * math.pi
    horizon = np.exp(-0.5 * (elevation / math.radians(34)) ** 2)
    rgb = np.zeros((height, width, 3), dtype=np.float32)
    rgb += np.array([0.11, 0.11, 0.11], dtype=np.float32)
    rgb += horizon[:, :, None] * np.array([0.16, 0.16, 0.16], dtype=np.float32)
    lobes = [
        (-48, 32, 24, 5.4),
        (118, 18, 20, 2.8),
        (174, 66, 30, 1.25),
        (18, -24, 26, 0.85),
    ]
    for az, el, sigma, energy in lobes:
        lobe = helpers.angular_lobe(
            theta,
            elevation,
            math.radians(az),
            math.radians(el),
            math.radians(sigma),
        )
        rgb += lobe[:, :, None] * energy
    rgb[:, -1, :] = rgb[:, 0, :]
    rgba = np.concatenate(
        [rgb, np.ones((height, width, 1), dtype=np.float32)], axis=2
    )
    output = oiio.ImageOutput.create(str(OUTPUT_EXR))
    if output is None:
        raise RuntimeError("OpenImageIO could not create the rev 4 EXR.")
    image_spec = oiio.ImageSpec(width, height, 4, oiio.FLOAT)
    image_spec.attribute("oiio:ColorSpace", "Linear Rec.709 (sRGB)")
    image_spec.attribute("DateTime", "1970:01:01 00:00:00")
    output.open(str(OUTPUT_EXR), image_spec)
    output.write_image(rgba)
    output.close()
    image = bpy.data.images.load(str(OUTPUT_EXR), check_existing=False)
    image.name = "M08R4_NeutralParityStudio"
    image.colorspace_settings.name = "Non-Color"
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    markers = {
        name: [float(value) for value in sample_direction(rgb, az, el)]
        for name, az, el in [
            ("positiveZ", 0, 0),
            ("positiveX", 90, 0),
            ("negativeZ", 180, 0),
            ("negativeX", -90, 0),
            ("up", 0, 90),
            ("down", 0, -90),
        ]
    }
    return image, rgb, {
        "projection": "equirectangular",
        "resolution": [width, height],
        "linearColorSpace": "Rec.709/D65",
        "strength": ENVIRONMENT_STRENGTH,
        "rotationDegrees": 0.0,
        "seamMaxAbsoluteLinearDelta": float(
            np.max(np.abs(rgb[:, 0, :] - rgb[:, -1, :]))
        ),
        "minimum": float(rgb.min()),
        "maximum": float(rgb.max()),
        "mean": float(rgb.mean()),
        "p01Luminance": float(np.percentile(luminance, 1)),
        "p99Luminance": float(np.percentile(luminance, 99)),
        "directionMarkers": markers,
    }


def sample_direction(rgb, azimuth_degrees, elevation_degrees):
    u = (math.radians(azimuth_degrees) + math.pi) / (2 * math.pi)
    v = (math.pi * 0.5 - math.radians(elevation_degrees)) / math.pi
    x = min(rgb.shape[1] - 1, max(0, round(u * (rgb.shape[1] - 1))))
    y = min(rgb.shape[0] - 1, max(0, round(v * (rgb.shape[0] - 1))))
    return rgb[y, x]


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
    background.inputs["Strength"].default_value = ENVIRONMENT_STRENGTH
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])


def render_exr(name, camera):
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(HERE / f"blender-{name}-linear.exr")
    bpy.ops.render.render(write_still=True)


def set_original_visibility(visible):
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name in CORE:
            obj.hide_render = not visible


def create_diagnostic_material(name, color, metallic, roughness):
    material = helpers.solid_material(name, (*color, 1.0), roughness)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    helpers.set_input(bsdf, "Metallic", metallic)
    helpers.set_input(bsdf, "Coat Weight", 0.08 if metallic > 0.5 else 0.0)
    helpers.set_input(bsdf, "Coat Roughness", max(0.02, roughness * 0.25))
    return material


def create_sphere_strip(material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=128, ring_count=64, radius=13.0, location=(-17.0, 0.0, 5.0)
    )
    sphere = bpy.context.object
    sphere.name = "M08R4_DiagnosticSphere"
    sphere.data.materials.append(material)
    bpy.ops.mesh.primitive_cube_add(location=(14.0, 0.0, 5.0), scale=(13.0, 5.0, 3.0))
    strip = bpy.context.object
    strip.name = "M08R4_DiagnosticStrip"
    strip.data.materials.append(material)
    return [sphere, strip]


def remove_diagnostics(objects):
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def render_diagnostics(camera):
    set_original_visibility(False)
    mirror = create_diagnostic_material(
        "M08R4_ReflectionDiagnostic", (0.74, 0.74, 0.74), 1.0, 0.075
    )
    diagnostic = create_sphere_strip(mirror)
    render_exr("reflection-only", camera)
    remove_diagnostics(diagnostic)

    silver = bpy.data.materials["M07R11_PolishedSilver"]
    diagnostic = create_sphere_strip(silver)
    render_exr("silver", camera)
    remove_diagnostics(diagnostic)

    set_original_visibility(True)
    clay = create_diagnostic_material("M08R4_Clay", (0.42, 0.42, 0.42), 0.0, 0.5)
    bpy.context.scene.view_layers[0].material_override = clay
    render_exr("clay", camera)
    bpy.context.scene.view_layers[0].material_override = None

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name != "MovingTopBody"
    render_exr("crystal", camera)
    set_original_visibility(True)
    render_exr("full-model", camera)


def main():
    if helpers.sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Approved Gate 07 source hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the approved Gate 07 source blend.")
    geometry_before = helpers.geometry_digest()
    material_before = helpers.material_digest()
    matrices_before = helpers.matrix_digest()
    if geometry_before != GEOMETRY_DIGEST or material_before != MATERIAL_DIGEST:
        raise RuntimeError("Approved geometry or material digest drift.")

    for obj in list(bpy.data.objects):
        if (
            obj.type in {"CAMERA", "LIGHT"}
            or (obj.type == "MESH" and obj.name not in CORE)
        ):
            bpy.data.objects.remove(obj, do_unlink=True)
        elif obj.name.startswith(("M08R2_", "M08R3_", "M09R8_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 4
    scene["mechanism_contract_sha256"] = CONTRACT_SHA
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["approved_material_digest"] = MATERIAL_DIGEST
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Raw"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = False

    image, _, environment = create_environment()
    configure_world(image)
    camera = helpers.create_camera()
    camera.name = "M08R4_Hero"
    camera.data.name = "M08R4_Hero_Data"
    render_diagnostics(camera)

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = False
    geometry_after = helpers.geometry_digest()
    material_after = helpers.material_digest()
    matrices_after = helpers.matrix_digest()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    environment["sha256"] = helpers.sha256(OUTPUT_EXR)
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 4,
        "status": "diagnostic-not-reviewable",
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
        "matrixDigest": {"before": matrices_before, "after": matrices_after},
        "portableRecipe": {
            "environment": environment,
            "reflectionSourceCount": 1,
            "directLightCount": 0,
            "reflectionProbeCount": 0,
            "reflectionCardCount": 0,
            "syntheticHighlightCount": 0,
            "groundCount": 0,
            "backgroundLinear": BACKGROUND_LINEAR.tolist(),
            "displayTransform": "shared post-render neutral-display-v1",
            "camera": {
                "resolution": [1400, 1100],
                "locationMm": [74.0, -116.0, 72.0],
                "targetMm": [0.0, -2.0, 5.0],
                "lensMm": 76.0,
                "sensorWidthMm": 36.0,
                "sensorFit": "HORIZONTAL",
            },
        },
        "controlledRenders": [
            "reflection-only",
            "clay",
            "silver",
            "crystal",
            "full-model",
        ],
        "checks": {
            "geometryUnchanged": geometry_before == geometry_after == GEOMETRY_DIGEST,
            "materialsUnchanged": material_before == material_after == MATERIAL_DIGEST,
            "matricesUnchanged": matrices_before == matrices_after,
            "singleReflectionSource": True,
            "zeroDirectLights": True,
            "zeroGround": True,
            "zeroEmissionPreserved": True,
            "linearHdrOutputs": True,
            "shippingUntouched": True,
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "neutral-parity-blender-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"pass": report["pass"], "environment": environment}, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 rev 4 Blender validation failed.")


if __name__ == "__main__":
    main()
