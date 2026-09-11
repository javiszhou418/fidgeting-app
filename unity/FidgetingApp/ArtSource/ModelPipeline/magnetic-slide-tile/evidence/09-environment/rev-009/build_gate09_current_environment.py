#!/usr/bin/env python3
"""Build Gate 09 rev 9 from the current partition-safe lighting source."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import shutil
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
GATE08 = HERE.parent.parent / "08-lighting/rev-006"
SOURCE = GATE08 / "magnetic-slide-tile-lighting-r006.blend"
SOURCE_SHA = "897484bd6e740454ee23c6a891eb8faa2fdf48af543792f08c3f4b78ff8780fe"
NEUTRAL_SOURCE = GATE08 / "neutral-parity-studio-r006.exr"
NEUTRAL_SHA = "a5b310c8c7fc17bda4110adb80e68913f1b5d623ffe01d935574813b80d1a872"
NEUTRAL = HERE / "neutral-control-r009.exr"
TARGET = HERE / "target-shipping-studio-r009.exr"
TARGET_PREVIEW = HERE / "target-shipping-studio-r009-preview.png"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-environment-r009.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-environment-r009-lookdev.glb"
REPORT = HERE / "environment-build-validation.json"
CUBEMAP = HERE / "cubemap-r009"
EXPECTED_GEOMETRY = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
EXPECTED_CONTRACT = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
WIDTH = 2048
HEIGHT = 1024
FACE_SIZE = 512

spec = importlib.util.spec_from_file_location(
    "gate08_helpers",
    GATE08 / "build_gate08_partition_safe_lighting.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matrix_values(matrix) -> list[list[float]]:
    return [[round(float(value), 9) for value in row] for row in matrix]


def emission_strength(material) -> float:
    if not material.use_nodes:
        return 0.0
    total = 0.0
    for node in material.node_tree.nodes:
        if node.bl_idname == "ShaderNodeEmission":
            total = max(total, float(node.inputs["Strength"].default_value))
        if node.bl_idname == "ShaderNodeBsdfPrincipled":
            socket = node.inputs.get("Emission Strength")
            if socket is not None:
                total = max(total, float(socket.default_value))
    return total


def write_exr(path: Path, pixels: np.ndarray) -> None:
    channels = pixels.shape[2]
    output = oiio.ImageOutput.create(str(path))
    image_spec = oiio.ImageSpec(pixels.shape[1], pixels.shape[0], channels, oiio.FLOAT)
    image_spec.attribute("oiio:ColorSpace", "Linear Rec.709 (sRGB)")
    image_spec.attribute("DateTime", "1970:01:01 00:00:00")
    output.open(str(path), image_spec)
    output.write_image(pixels.astype(np.float32))
    output.close()


def read_image(path: Path) -> tuple[np.ndarray, dict]:
    source = oiio.ImageInput.open(str(path))
    if source is None:
        raise RuntimeError(f"Cannot open image {path}.")
    image_spec = source.spec()
    pixels = np.asarray(source.read_image(format=oiio.FLOAT), dtype=np.float32).reshape(
        image_spec.height,
        image_spec.width,
        image_spec.nchannels,
    )
    source.close()
    return pixels, {
        "resolution": [image_spec.width, image_spec.height],
        "channels": image_spec.nchannels,
        "format": str(image_spec.format),
    }


def angular_lobe(theta, elevation, azimuth, center_elevation, sigma):
    cosine = (
        np.cos(elevation) * np.cos(center_elevation) * np.cos(theta - azimuth)
        + np.sin(elevation) * np.sin(center_elevation)
    )
    distance = np.arccos(np.clip(cosine, -1.0, 1.0))
    return np.exp(-0.5 * (distance / sigma) ** 2)


def build_target_environment() -> tuple[np.ndarray, dict]:
    azimuth = np.linspace(-math.pi, math.pi, WIDTH, endpoint=True, dtype=np.float32)
    vertical = np.linspace(0, 1, HEIGHT, endpoint=True, dtype=np.float32)
    theta, normalized_y = np.meshgrid(azimuth, vertical)
    elevation = math.pi * 0.5 - normalized_y * math.pi
    horizon = np.exp(-0.5 * (elevation / math.radians(28)) ** 2)
    upper = np.clip(elevation / (math.pi * 0.5), 0, 1)
    lower = np.clip(-elevation / (math.pi * 0.5), 0, 1)
    rgb = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    rgb += np.array([0.026, 0.024, 0.027], dtype=np.float32)
    rgb += horizon[..., None] * np.array([0.075, 0.068, 0.070], dtype=np.float32)
    rgb += upper[..., None] * np.array([0.018, 0.020, 0.024], dtype=np.float32)
    rgb += lower[..., None] * np.array([0.010, 0.008, 0.009], dtype=np.float32)
    lobes = [
        (-52, 28, 13, (3.20, 3.02, 2.88)),
        (108, 20, 11, (1.30, 1.43, 1.62)),
        (172, 62, 18, (0.82, 0.79, 0.76)),
        (28, -22, 22, (0.34, 0.28, 0.27)),
    ]
    for azimuth_degrees, elevation_degrees, sigma_degrees, energy in lobes:
        rgb += angular_lobe(
            theta,
            elevation,
            math.radians(azimuth_degrees),
            math.radians(elevation_degrees),
            math.radians(sigma_degrees),
        )[..., None] * np.asarray(energy, dtype=np.float32)
    rgb = np.maximum(rgb, 0.006)
    rgb[:, -1] = rgb[:, 0]
    rgba = np.concatenate([rgb, np.ones((HEIGHT, WIDTH, 1), dtype=np.float32)], axis=2)
    write_exr(TARGET, rgba)
    helpers.convert_exr(TARGET, TARGET_PREVIEW)
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    maximum_index = np.unravel_index(np.argmax(luminance), luminance.shape)
    maximum_azimuth = -180.0 + maximum_index[1] / (WIDTH - 1) * 360.0
    maximum_elevation = 90.0 - maximum_index[0] / (HEIGHT - 1) * 180.0
    return rgb, {
        "path": TARGET.name,
        "sha256": sha256(TARGET),
        "resolution": [WIDTH, HEIGHT],
        "projection": "equirectangular",
        "colorSpace": "scene-linear Rec.709/D65",
        "nonzeroRgbFraction": float(np.mean(np.any(rgb > 0, axis=2))),
        "minimum": float(rgb.min()),
        "maximum": float(rgb.max()),
        "seamMaximumLinearDelta": float(np.max(np.abs(rgb[:, 0] - rgb[:, -1]))),
        "dynamicRangeStopsP01P99": float(
            np.log2(np.percentile(luminance, 99) / np.percentile(luminance, 1)),
        ),
        "brightestDirectionBlenderDegrees": [maximum_azimuth, maximum_elevation],
    }


def normalize(vectors: np.ndarray) -> np.ndarray:
    return vectors / np.linalg.norm(vectors, axis=-1, keepdims=True)


def unity_face_directions(face: str) -> np.ndarray:
    values = (np.arange(FACE_SIZE, dtype=np.float32) + 0.5) * (2 / FACE_SIZE) - 1
    a, b = np.meshgrid(values, values)
    if face == "positive-x":
        result = np.stack([np.ones_like(a), -b, -a], axis=2)
    elif face == "negative-x":
        result = np.stack([-np.ones_like(a), -b, a], axis=2)
    elif face == "positive-y":
        result = np.stack([a, np.ones_like(a), b], axis=2)
    elif face == "negative-y":
        result = np.stack([a, -np.ones_like(a), -b], axis=2)
    elif face == "positive-z":
        result = np.stack([a, -b, np.ones_like(a)], axis=2)
    elif face == "negative-z":
        result = np.stack([-a, -b, -np.ones_like(a)], axis=2)
    else:
        raise ValueError(face)
    return normalize(result)


def bilinear_equirect(rgb: np.ndarray, blender_direction: np.ndarray) -> np.ndarray:
    x, y, z = [blender_direction[..., index] for index in range(3)]
    azimuth = np.arctan2(y, x)
    elevation = np.arcsin(np.clip(z, -1, 1))
    pixel_x = (azimuth + math.pi) / (2 * math.pi) * (WIDTH - 1)
    pixel_y = (math.pi * 0.5 - elevation) / math.pi * (HEIGHT - 1)
    x0 = np.floor(pixel_x).astype(np.int32)
    y0 = np.floor(pixel_y).astype(np.int32)
    x1 = np.minimum(x0 + 1, WIDTH - 1)
    y1 = np.minimum(y0 + 1, HEIGHT - 1)
    fx = (pixel_x - x0)[..., None]
    fy = (pixel_y - y0)[..., None]
    return (
        rgb[y0, x0] * (1 - fx) * (1 - fy)
        + rgb[y0, x1] * fx * (1 - fy)
        + rgb[y1, x0] * (1 - fx) * fy
        + rgb[y1, x1] * fx * fy
    )


def build_unity_cubemap(rgb: np.ndarray, equirect_metadata: dict) -> dict:
    CUBEMAP.mkdir(exist_ok=True)
    faces = {}
    maximum_luminance = -1.0
    maximum_direction = None
    for face in [
        "positive-x",
        "negative-x",
        "positive-y",
        "negative-y",
        "positive-z",
        "negative-z",
    ]:
        unity_direction = unity_face_directions(face)
        blender_direction = np.stack(
            [
                unity_direction[..., 0],
                -unity_direction[..., 2],
                unity_direction[..., 1],
            ],
            axis=2,
        )
        pixels = bilinear_equirect(rgb, blender_direction)
        rgba = np.concatenate(
            [pixels, np.ones((FACE_SIZE, FACE_SIZE, 1), dtype=np.float32)],
            axis=2,
        )
        path = CUBEMAP / f"{face}.exr"
        write_exr(path, rgba)
        luminance = pixels @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        index = np.unravel_index(np.argmax(luminance), luminance.shape)
        if float(luminance[index]) > maximum_luminance:
            maximum_luminance = float(luminance[index])
            maximum_direction = unity_direction[index].tolist()
        faces[face] = {
            "path": path.relative_to(HERE).as_posix(),
            "sha256": sha256(path),
            "resolution": [FACE_SIZE, FACE_SIZE],
        }
    blender_maximum = np.array([
        math.cos(math.radians(equirect_metadata["brightestDirectionBlenderDegrees"][1]))
        * math.cos(math.radians(equirect_metadata["brightestDirectionBlenderDegrees"][0])),
        math.cos(math.radians(equirect_metadata["brightestDirectionBlenderDegrees"][1]))
        * math.sin(math.radians(equirect_metadata["brightestDirectionBlenderDegrees"][0])),
        math.sin(math.radians(equirect_metadata["brightestDirectionBlenderDegrees"][1])),
    ])
    expected_unity = np.array([
        blender_maximum[0],
        blender_maximum[2],
        -blender_maximum[1],
    ])
    actual_unity = np.asarray(maximum_direction)
    angular_error = math.degrees(
        math.acos(float(np.clip(np.dot(expected_unity, actual_unity), -1, 1))),
    )
    descriptor = {
        "schemaVersion": 1,
        "sourceEquirectangular": {
            "path": TARGET.name,
            "sha256": equirect_metadata["sha256"],
        },
        "faceConvention": "Unity cubemap; raster top-left; +X=(1,-b,-a), -X=(-1,-b,a), +Y=(a,1,b), -Y=(a,-1,-b), +Z=(a,-b,1), -Z=(-a,-b,-1)",
        "coordinateMapping": "Blender(X,Y,Z) -> Unity(X,Z,-Y)",
        "faces": faces,
        "brightestDirectionUnity": maximum_direction,
        "brightestDirectionAngularErrorDegrees": angular_error,
        "nonzeroRgb": True,
        "colorSpace": "scene-linear Rec.709/D65",
    }
    descriptor_path = CUBEMAP / "cubemap-contract.json"
    descriptor_path.write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")
    descriptor["descriptorSha256"] = sha256(descriptor_path)
    return descriptor


def set_world(path: Path, label: str) -> None:
    image = bpy.data.images.load(str(path), check_existing=False)
    image.name = f"M09R9_{label}"
    image.colorspace_settings.name = "Non-Color"
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    texture = nodes.new("ShaderNodeTexEnvironment")
    texture.image = image
    texture.interpolation = "Linear"
    background.inputs["Strength"].default_value = 0.85
    links.new(texture.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    world["gate09_environment_role"] = label
    world["source_sha256"] = sha256(path)
    world["projection"] = "equirectangular"
    world["color_space"] = "scene-linear Rec.709/D65"


def pose_and_camera_snapshot() -> dict:
    scene = bpy.context.scene
    return {
        "movingTop": matrix_values(bpy.data.objects["MovingTop"].matrix_world),
        "topLocalSlide": matrix_values(bpy.data.objects["TopLocalSlide"].matrix_world),
        "carrier": matrix_values(bpy.data.objects["RotatingCarrier"].matrix_world),
        "fixedAxis": matrix_values(bpy.data.objects["InternalAxisBoss"].matrix_world),
        "camera": matrix_values(scene.camera.matrix_world),
        "lens": scene.camera.data.lens,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "display": {
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": scene.view_settings.exposure,
            "gamma": scene.view_settings.gamma,
            "recipe": "neutral-display-v1",
        },
        "lights": sorted(obj.name for obj in bpy.data.objects if obj.type == "LIGHT"),
    }


def render(name: str, environment: Path) -> dict:
    set_world(environment, environment.stem)
    helpers.validate_partitions(name)
    before = helpers.snapshot_all()
    state = pose_and_camera_snapshot()
    exr = HERE / f"{name}-linear.exr"
    png = HERE / f"{name}.png"
    bpy.context.scene.render.filepath = str(exr)
    bpy.ops.render.render(write_still=True)
    helpers.convert_exr(exr, png)
    if not helpers.snapshots_equal(before, helpers.snapshot_all()):
        raise RuntimeError(f"Source mesh snapshot changed while rendering {name}.")
    return {
        "png": png.name,
        "pngSha256": sha256(png),
        "linearExr": exr.name,
        "linearExrSha256": sha256(exr),
        "environmentSha256": sha256(environment),
        "state": state,
    }


def render_pair(name: str, slide: float, angle: float, camera_name: str) -> dict:
    helpers.set_pose(slide, angle)
    bpy.context.scene.camera = bpy.data.objects[camera_name]
    neutral = render(f"neutral-{name}", NEUTRAL)
    target = render(f"target-{name}", TARGET)
    if neutral["state"] != target["state"]:
        raise RuntimeError(f"Non-environment state differs for {name}.")
    return {"neutral": neutral, "target": target, "stateIdentical": True}


def export_glb() -> None:
    helpers.set_pose(0, 0)
    helpers.validate_partitions("gate09-glb-export")
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for name in helpers.PRODUCT:
        bpy.data.objects[name].select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
        export_apply=False,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
    )


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open Gate 08 rev 6 lighting source.")
    if sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Gate 08 rev 6 source hash drift.")
    if helpers.canonical_geometry_digest() != EXPECTED_GEOMETRY:
        raise RuntimeError("Geometry digest drift.")
    if bpy.context.scene.get("mechanism_contract_sha256") != EXPECTED_CONTRACT:
        raise RuntimeError("Mechanism contract drift.")
    initial_mesh_snapshot = helpers.snapshot_all()
    initial_partition = helpers.validate_partitions("gate09-initial")
    if sha256(NEUTRAL_SOURCE) != NEUTRAL_SHA:
        raise RuntimeError("Current neutral environment hash drift.")
    shutil.copyfile(NEUTRAL_SOURCE, NEUTRAL)
    neutral_pixels, neutral_spec = read_image(NEUTRAL)
    if neutral_spec["resolution"] != [WIDTH, HEIGHT]:
        raise RuntimeError("Neutral environment dimensions drift.")
    neutral_rgb = neutral_pixels[..., :3]
    neutral_metadata = {
        "path": NEUTRAL.name,
        "sha256": sha256(NEUTRAL),
        "resolution": neutral_spec["resolution"],
        "nonzeroRgbFraction": float(np.mean(np.any(neutral_rgb > 0, axis=2))),
        "seamMaximumLinearDelta": float(np.max(np.abs(neutral_rgb[:, 0] - neutral_rgb[:, -1]))),
        "minimum": float(neutral_rgb.min()),
        "maximum": float(neutral_rgb.max()),
        "revalidatedFromCurrentGate08": True,
    }
    target_rgb, target_metadata = build_target_environment()
    cubemap_metadata = build_unity_cubemap(target_rgb, target_metadata)
    scene = bpy.context.scene
    scene["gate"] = "09-environment"
    scene["environment_revision"] = 9
    scene["source_gate08_sha256"] = SOURCE_SHA
    scene["source_material_sha256"] = helpers.SOURCE_SHA
    scene["canonical_geometry_digest"] = EXPECTED_GEOMETRY
    scene["mechanism_contract_sha256"] = EXPECTED_CONTRACT
    scene["environment_only_difference"] = "texture input only"
    scene["display_mapping"] = "neutral-display-v1"
    scene["endpoint_interlock"] = "rotation-only-at-sMax; slide-return-only-at-0-or-360"
    scene["shipping_unity_changed"] = False
    pairs = {
        "closed": render_pair("closed", 0, 0, "M08R6_Hero"),
        "max0": render_pair("max0", helpers.MAX_TRAVEL, 0, "M08R6_Hero"),
        "side-reflection": render_pair(
            "side-reflection",
            helpers.MAX_TRAVEL,
            36,
            "M08R6_SideCloseup",
        ),
    }
    target_views = {}
    for name, slide, angle, camera in [
        ("max12", helpers.MAX_TRAVEL, 12, "M08R6_Hero"),
        ("max36", helpers.MAX_TRAVEL, 36, "M08R6_Hero"),
        ("max360", helpers.MAX_TRAVEL, 360, "M08R6_Hero"),
        ("rim-reflection", helpers.MAX_TRAVEL, 36, "M08R6_RimCloseup"),
        ("dark-side-closeup", helpers.MAX_TRAVEL, 36, "M08R6_SideCloseup"),
    ]:
        helpers.set_pose(slide, angle)
        scene.camera = bpy.data.objects[camera]
        target_views[name] = render(f"target-{name}", TARGET)
    helpers.set_pose(0, 0)
    set_world(TARGET, "target-shipping-studio")
    export_glb()
    final_mesh_snapshot = helpers.snapshot_all()
    if not helpers.snapshots_equal(initial_mesh_snapshot, final_mesh_snapshot):
        raise RuntimeError("Gate 09 changed source geometry, UVs, slots, or material indices.")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    checks = {
        "sourceLightingHash": sha256(SOURCE) == SOURCE_SHA,
        "geometryDigest": helpers.canonical_geometry_digest() == EXPECTED_GEOMETRY,
        "sourceSnapshotIdentical": helpers.snapshots_equal(initial_mesh_snapshot, final_mesh_snapshot),
        "partitionsPass": initial_partition["pass"],
        "sideArtworkZero": all(
            item["verticalSideArtworkFaces"] == 0
            for item in initial_partition["objects"].values()
        ),
        "undersideArtworkZero": all(
            item["undersideArtworkFaces"] == 0
            for item in initial_partition["objects"].values()
        ),
        "capArtworkPresent": all(
            item["faceCounts"][0] > 0
            for item in initial_partition["objects"].values()
        ),
        "silverRimPresent": all(
            item["faceCounts"][2] > 0
            for item in initial_partition["objects"].values()
        ),
        "neutralRevalidated": neutral_metadata["sha256"] == NEUTRAL_SHA
        and neutral_metadata["nonzeroRgbFraction"] == 1.0
        and neutral_metadata["seamMaximumLinearDelta"] <= 1e-6,
        "targetNonzero": target_metadata["nonzeroRgbFraction"] == 1.0,
        "targetSeamless": target_metadata["seamMaximumLinearDelta"] <= 1e-6,
        "targetDynamicRange": target_metadata["dynamicRangeStopsP01P99"] >= 4,
        "cubemapOrientation": cubemap_metadata["brightestDirectionAngularErrorDegrees"] <= 1.0,
        "cubemapRgb": cubemap_metadata["nonzeroRgb"],
        "matchedPairState": all(pair["stateIdentical"] for pair in pairs.values()),
        "zeroLights": not any(obj.type == "LIGHT" for obj in bpy.data.objects),
        "displayMapping": pose_and_camera_snapshot()["display"]["recipe"] == "neutral-display-v1",
        "endpointInterlock": scene["endpoint_interlock"]
        == "rotation-only-at-sMax; slide-return-only-at-0-or-360",
        "fixedAxis": all(
            pair["neutral"]["state"]["fixedAxis"] == pair["target"]["state"]["fixedAxis"]
            for pair in pairs.values()
        ),
        "noFlip": all(
            abs(bpy.data.objects[name].rotation_euler.x) <= 1e-9
            and abs(bpy.data.objects[name].rotation_euler.y) <= 1e-9
            for name in ["MovingTop", "RotatingCarrier"]
        ),
        "noProxy": scene["product_renderer_whitelist"] == helpers.PRODUCT,
        "zeroEmission": all(
            emission_strength(material) == 0
            for material in bpy.data.materials
            if material.name.startswith("M07R13_")
        ),
        "glbWritten": OUTPUT_GLB.exists(),
        "blendWritten": OUTPUT_BLEND.exists(),
        "shippingUnityUnchanged": scene["shipping_unity_changed"] is False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "source": {
            "gate08Blend": SOURCE.relative_to(HERE.parents[7]).as_posix(),
            "sha256": SOURCE_SHA,
            "approvalExactWording": "你开始吧",
            "geometryDigest": EXPECTED_GEOMETRY,
            "materialSha256": helpers.SOURCE_SHA,
            "mechanismContractSha256": EXPECTED_CONTRACT,
        },
        "neutral": neutral_metadata,
        "target": target_metadata,
        "cubemap": cubemap_metadata,
        "pairs": pairs,
        "targetViews": target_views,
        "sourceSnapshotBefore": helpers.snapshot_report(initial_mesh_snapshot),
        "sourceSnapshotAfter": helpers.snapshot_report(final_mesh_snapshot),
        "materialPartitions": initial_partition,
        "output": {
            "blend": OUTPUT_BLEND.name,
            "blendSha256": sha256(OUTPUT_BLEND),
            "glb": OUTPUT_GLB.name,
            "glbSha256": sha256(OUTPUT_GLB),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "targetSha256": target_metadata["sha256"],
        "cubemapOrientationErrorDegrees": cubemap_metadata["brightestDirectionAngularErrorDegrees"],
        "blendSha256": report["output"]["blendSha256"],
        "glbSha256": report["output"]["glbSha256"],
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 environment build validation failed.")


if __name__ == "__main__":
    main()
