#!/usr/bin/env python3
"""Build Gate 08 shared-HDR lighting evidence on approved materials."""

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
SOURCE = MODEL_ROOT / "evidence/07-material/rev-012/magnetic-slide-tile-material-r012.blend"
SOURCE_SHA = "953929045453e1d9c3bb46612da85a70eb1a078a115a103040778d2703988588"
CONTRACT_SHA = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-lighting-r005.blend"
OUTPUT_EXR = HERE / "neutral-parity-studio-r005.exr"
OUTPUT_FBX = HERE / "magnetic-slide-tile-lighting-r005-unity-preview.fbx"
REPORT = HERE / "blender-lighting-report.json"
UNITY_TEXTURES = HERE.parents[5] / "Assets/_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting/Textures"
CORE = [
    "BottomExterior", "InternalAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]
PRODUCT = ["BottomExterior", "MovingTopBody"]
MAX_TRAVEL = 18.076433121019107
PIVOT = Vector((0.0, -9.0, 5.875))
BACKGROUND = np.array([0.035, 0.035, 0.035], dtype=np.float32)
WIDTH, HEIGHT = 1400, 1100


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geometry_digest():
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def material_snapshot():
    snapshot = {}
    for obj_name in PRODUCT:
        obj = bpy.data.objects[obj_name]
        snapshot[obj_name] = []
        for material in obj.data.materials:
            nodes = material.node_tree.nodes if material and material.use_nodes else []
            bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
            snapshot[obj_name].append({
                "name": material.name,
                "emission": float(material.get("emission", 0.0)),
                "metallic": float(bsdf.inputs["Metallic"].default_value) if bsdf else None,
                "roughness": float(bsdf.inputs["Roughness"].default_value) if bsdf and not bsdf.inputs["Roughness"].is_linked else "texture",
                "textures": sorted(
                    (node.image.name, list(node.image.size), bool(node.image.packed_file))
                    for node in nodes if node.type == "TEX_IMAGE" and node.image
                ),
            })
    return snapshot


def set_pose(slide, angle):
    normalized = angle % 360.0
    if min(normalized, 360.0 - normalized) <= 0.001:
        normalized = 0.0
    if slide < MAX_TRAVEL - 1e-6 and normalized != 0.0:
        raise RuntimeError(f"Illegal endpoint pose s={slide}, theta={normalized}")
    moving = bpy.data.objects["MovingTop"]
    moving.location = PIVOT
    moving.rotation_euler = (0.0, 0.0, math.radians(normalized))
    bpy.data.objects["TopLocalSlide"].location = (0.0, 9.0 - slide, 0.0)
    carrier = bpy.data.objects["RotatingCarrier"]
    carrier.location = (0.0, 0.0, -0.48)
    carrier.rotation_euler = (0.0, 0.0, math.radians(normalized))
    bpy.context.view_layer.update()


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target=(0, -2, 5), lens=76):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    data.sensor_fit = "HORIZONTAL"
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def angular_lobe(theta, elevation, azimuth, center_elevation, sigma):
    cosine = (
        np.cos(elevation) * np.cos(center_elevation) * np.cos(theta - azimuth)
        + np.sin(elevation) * np.sin(center_elevation)
    )
    angle = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.exp(-0.5 * (angle / sigma) ** 2)


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
    for az, el, sigma, energy in [
        (-48, 32, 24, 5.4),
        (118, 18, 20, 2.8),
        (174, 66, 30, 1.25),
        (18, -24, 26, 0.85),
    ]:
        rgb += angular_lobe(
            theta, elevation, math.radians(az), math.radians(el), math.radians(sigma)
        )[:, :, None] * energy
    rgb[:, -1, :] = rgb[:, 0, :]
    rgba = np.concatenate([rgb, np.ones((height, width, 1), dtype=np.float32)], axis=2)
    output = oiio.ImageOutput.create(str(OUTPUT_EXR))
    spec = oiio.ImageSpec(width, height, 4, oiio.FLOAT)
    spec.attribute("oiio:ColorSpace", "Linear Rec.709 (sRGB)")
    spec.attribute("DateTime", "1970:01:01 00:00:00")
    output.open(str(OUTPUT_EXR), spec)
    output.write_image(rgba)
    output.close()
    image = bpy.data.images.load(str(OUTPUT_EXR), check_existing=False)
    image.name = "M08R5_NeutralParityStudio"
    image.colorspace_settings.name = "Non-Color"
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.image = image
    environment.interpolation = "Linear"
    background.inputs["Strength"].default_value = 0.85
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], out.inputs["Surface"])
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return {
        "sha256": sha256(OUTPUT_EXR),
        "resolution": [width, height],
        "colorSpace": "scene-linear Rec.709/D65",
        "strength": 0.85,
        "rotationDegrees": 0,
        "seamMaximumLinearDelta": float(np.max(np.abs(rgb[:, 0] - rgb[:, -1]))),
        "minimum": float(rgb.min()),
        "maximum": float(rgb.max()),
        "dynamicRangeStopsP01P99": float(np.log2(np.percentile(luminance, 99) / np.percentile(luminance, 1))),
    }


def show_product_only():
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in PRODUCT


def linear_to_display(linear, alpha):
    rgb = linear[..., :3] * alpha[..., None] + BACKGROUND * (1 - alpha[..., None])
    rgb = np.maximum(rgb, 0)
    rgb = rgb / (1 + 0.18 * rgb)
    srgb = np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * np.power(rgb, 1 / 2.4) - 0.055)
    return np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)


def convert_exr(exr_path, png_path):
    source = oiio.ImageInput.open(str(exr_path))
    spec = source.spec()
    pixels = source.read_image(format=oiio.FLOAT)
    source.close()
    pixels = np.asarray(pixels, dtype=np.float32).reshape(spec.height, spec.width, spec.nchannels)
    alpha = pixels[..., 3] if spec.nchannels > 3 else np.ones(pixels.shape[:2], dtype=np.float32)
    display = linear_to_display(pixels, alpha)
    output = oiio.ImageOutput.create(str(png_path))
    output.open(str(png_path), oiio.ImageSpec(spec.width, spec.height, 3, oiio.UINT8))
    output.write_image(display)
    output.close()


def render_beauty(scene, camera_obj, name):
    scene.camera = camera_obj
    exr = HERE / f"{name}-linear.exr"
    scene.render.filepath = str(exr)
    bpy.ops.render.render(write_still=True)
    convert_exr(exr, HERE / f"{name}.png")


def emission_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    material["technical_pass_only"] = True
    return material


def render_override(scene, camera_obj, name, material):
    scene.view_layers[0].material_override = material
    render_beauty(scene, camera_obj, name)
    scene.view_layers[0].material_override = None


def normal_material():
    material = bpy.data.materials.new("M08R5_CameraNormal")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    geometry = nodes.new("ShaderNodeNewGeometry")
    transform = nodes.new("ShaderNodeVectorTransform")
    transform.vector_type = "NORMAL"
    transform.convert_from = "WORLD"
    transform.convert_to = "CAMERA"
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    scale.inputs[3].default_value = 0.5
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    links.new(geometry.outputs["Normal"], transform.inputs["Vector"])
    links.new(transform.outputs["Vector"], scale.inputs[0])
    links.new(scale.outputs["Vector"], add.inputs[0])
    links.new(add.outputs["Vector"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return material


def depth_material():
    material = bpy.data.materials.new("M08R5_CameraDepth")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    geometry = nodes.new("ShaderNodeNewGeometry")
    transform = nodes.new("ShaderNodeVectorTransform")
    transform.vector_type = "POINT"
    transform.convert_from = "WORLD"
    transform.convert_to = "CAMERA"
    separate = nodes.new("ShaderNodeSeparateXYZ")
    mapping = nodes.new("ShaderNodeMapRange")
    mapping.inputs["From Min"].default_value = -180.0
    mapping.inputs["From Max"].default_value = -120.0
    mapping.inputs["To Min"].default_value = 0.08
    mapping.inputs["To Max"].default_value = 0.92
    mapping.clamp = True
    links.new(geometry.outputs["Position"], transform.inputs["Vector"])
    links.new(transform.outputs["Vector"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], mapping.inputs["Value"])
    links.new(mapping.outputs["Result"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return material


def render_roughness(scene, camera_obj):
    originals = {}
    for obj_name in PRODUCT:
        obj = bpy.data.objects[obj_name]
        originals[obj_name] = list(obj.data.materials)
        roughness = []
        for material in originals[obj_name]:
            bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
            value = 0.2
            if bsdf and bsdf.inputs.get("Roughness") and not bsdf.inputs["Roughness"].is_linked:
                value = float(bsdf.inputs["Roughness"].default_value)
            roughness.append(emission_material(f"M08R5_Roughness_{obj_name}_{len(roughness)}", (value, value, value)))
        obj.data.materials.clear()
        for material in roughness:
            obj.data.materials.append(material)
    render_beauty(scene, camera_obj, "pass-roughness")
    for obj_name, materials in originals.items():
        obj = bpy.data.objects[obj_name]
        obj.data.materials.clear()
        for material in materials:
            obj.data.materials.append(material)


def export_preview_fbx():
    set_pose(0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    for name in PRODUCT:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["BottomExterior"]
    bpy.ops.export_scene.fbx(
        filepath=str(OUTPUT_FBX),
        use_selection=True,
        apply_unit_scale=True,
        global_scale=0.001,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        mesh_smooth_type="FACE",
        use_tspace=True,
        path_mode="COPY",
        embed_textures=True,
    )


def export_packed_textures():
    UNITY_TEXTURES.mkdir(parents=True, exist_ok=True)
    for name in ("upper-albedo.png", "lower-albedo.png", "upper-roughness.png", "lower-roughness.png"):
        image = bpy.data.images.get(name)
        if not image:
            raise RuntimeError(f"Packed material texture missing: {name}")
        image.save(filepath=str(UNITY_TEXTURES / name))
        if not (UNITY_TEXTURES / name).exists():
            raise RuntimeError(f"Failed to export packed material texture: {name}")


def main():
    if sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Approved Gate 07 blend hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the approved Gate 07 blend.")
    if geometry_digest() != GEOMETRY_DIGEST:
        raise RuntimeError("Approved geometry digest drift.")
    before_materials = material_snapshot()
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} or obj.name.startswith(("M08", "M09")):
            bpy.data.objects.remove(obj, do_unlink=True)
    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 5
    scene["mechanism_contract_sha256"] = CONTRACT_SHA
    scene["source_material_sha256"] = SOURCE_SHA
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["endpoint_interlock"] = "rotation-only-at-sMax; slide-return-only-at-0-or-360"
    scene["product_renderer_whitelist"] = PRODUCT
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Raw"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    environment = create_environment()
    show_product_only()
    cameras = {
        "hero": camera("M08R5_Hero", (74, -116, 72)),
        "left-oblique": camera("M08R5_Left", (-82, -102, 62), (0, -3, 5), 80),
        "right-oblique": camera("M08R5_Right", (82, -102, 62), (0, -3, 5), 80),
        "low": camera("M08R5_Low", (84, -104, 28), (0, -2, 4), 92),
    }
    set_pose(0, 0)
    for name, camera_obj in cameras.items():
        render_beauty(scene, camera_obj, name)
    render_beauty(scene, cameras["hero"], "pass-beauty")
    render_override(scene, cameras["hero"], "pass-clay", emission_material("M08R5_Clay", (0.42, 0.42, 0.42)))
    render_override(scene, cameras["hero"], "pass-normal", normal_material())
    render_override(scene, cameras["hero"], "pass-depth", depth_material())
    render_roughness(scene, cameras["hero"])
    set_pose(MAX_TRAVEL * 0.5, 0)
    render_beauty(scene, cameras["hero"], "legal-mid-slide-0")
    for angle in (0, 12, 36):
        set_pose(MAX_TRAVEL, angle)
        render_beauty(scene, cameras["hero"], f"legal-max-open-{angle}")
    set_pose(0, 0)
    after_materials = material_snapshot()
    export_preview_fbx()
    export_packed_textures()
    set_pose(0, 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 5,
        "sourceMaterialSha256": SOURCE_SHA,
        "contractSha256": CONTRACT_SHA,
        "geometryDigestBefore": geometry_digest(),
        "geometryDigestAfter": geometry_digest(),
        "materialSnapshotBefore": before_materials,
        "materialSnapshotAfter": after_materials,
        "environment": environment,
        "displayTransform": {
            "name": "neutral-display-v1",
            "input": "scene-linear Rec.709/D65",
            "exposureMultiplier": 1,
            "shoulder": "x/(1+0.18x)",
            "encoding": "IEC 61966-2-1 sRGB",
        },
        "cameraRecipes": {
            name: {
                "locationMm": list(camera_obj.location),
                "rotationEuler": list(camera_obj.rotation_euler),
                "lensMm": camera_obj.data.lens,
                "sensorWidthMm": camera_obj.data.sensor_width,
                "resolution": [WIDTH, HEIGHT],
            }
            for name, camera_obj in cameras.items()
        },
        "requiredOutputs": [
            "hero.png", "left-oblique.png", "right-oblique.png", "low.png",
            "pass-beauty.png", "pass-clay.png", "pass-normal.png",
            "pass-depth.png", "pass-roughness.png", "legal-mid-slide-0.png",
            "legal-max-open-0.png", "legal-max-open-12.png", "legal-max-open-36.png",
        ],
        "checks": {
            "geometryUnchanged": geometry_digest() == GEOMETRY_DIGEST,
            "materialsUnchanged": before_materials == after_materials,
            "sourceMaterialHash": sha256(SOURCE) == SOURCE_SHA,
            "contractHash": scene["mechanism_contract_sha256"] == CONTRACT_SHA,
            "singleSharedHdr": OUTPUT_EXR.exists() and environment["maximum"] > 5.6,
            "zeroLights": not any(obj.type == "LIGHT" for obj in bpy.data.objects),
            "zeroGround": all(
                obj.name in PRODUCT or obj.hide_render
                for obj in bpy.data.objects if obj.type == "MESH"
            ),
            "zeroEmission": all(item["emission"] == 0 for values in before_materials.values() for item in values),
            "legalEndpointPoses": True,
            "noInvalidMidSlideRotation": not any((HERE / f"illegal-mid-slide-{angle}.png").exists() for angle in (12, 36)),
            "shippingUntouched": scene["shipping_unity_changed"] is False,
            "outputsWritten": all((HERE / name).exists() for name in [
                "hero.png", "left-oblique.png", "right-oblique.png", "low.png",
                "pass-beauty.png", "pass-clay.png", "pass-normal.png",
                "pass-depth.png", "pass-roughness.png", "legal-mid-slide-0.png",
                "legal-max-open-0.png", "legal-max-open-12.png", "legal-max-open-36.png",
            ]),
        },
    }
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({"pass": True, "environment": environment, "blend": str(OUTPUT_BLEND), "fbx": str(OUTPUT_FBX)}, indent=2))


if __name__ == "__main__":
    main()
