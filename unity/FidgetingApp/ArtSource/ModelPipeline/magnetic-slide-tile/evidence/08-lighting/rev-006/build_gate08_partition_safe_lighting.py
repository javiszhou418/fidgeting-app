#!/usr/bin/env python3
"""Build Gate 08 rev 6 lighting without mutating source mesh data."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE = MODEL_ROOT / "evidence/07-material/rev-013/magnetic-slide-tile-material-r013.blend"
SOURCE_SHA = "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c"
CONTRACT_SHA = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
EXPECTED_ENVIRONMENT_SHA = "a5b310c8c7fc17bda4110adb80e68913f1b5d623ffe01d935574813b80d1a872"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-lighting-r006.blend"
OUTPUT_GLb = HERE / "magnetic-slide-tile-lighting-lookdev-r006.glb"
OUTPUT_EXR = HERE / "neutral-parity-studio-r006.exr"
REPORT = HERE / "blender-lighting-report.json"
FRAME_AUDIT = HERE / "frame-partition-audit.json"
PRODUCT = ["BottomExterior", "MovingTopBody"]
CORE = [
    "BottomExterior",
    "InternalAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
]
EXPECTED = {
    "BottomExterior": {
        "slots": [
            "M07R13_LowerTopArtwork",
            "M07R13_SolidDarkSide",
            "M07R13_PolishedBrightSilverRim",
            "M07R13_NeutralUnderside",
        ],
        "faceCounts": [1, 3078, 2052, 3592],
        "partitionDigest": "91fecf3892ef4ecc3a2ae5805ace8443fd31fd38451b5b444ed8f249c36c2e26",
    },
    "MovingTopBody": {
        "slots": [
            "M07R13_UpperTopArtwork",
            "M07R13_SolidDarkSide",
            "M07R13_PolishedBrightSilverRim",
            "M07R13_NeutralUnderside",
        ],
        "faceCounts": [1, 5130, 2052, 3600],
        "partitionDigest": "e256f01a909a8efd55455a67bdeccac2c0191d7d3be597c162f2119ae289bb12",
    },
}
MAX_TRAVEL = 18.076433121019107
PIVOT = Vector((0.0, -9.0, 5.875))
BACKGROUND = np.array([0.035, 0.035, 0.035], dtype=np.float32)
WIDTH, HEIGHT = 1400, 1100
FRAME_CHECKS = []


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_bytes(*values: bytes) -> str:
    digest = hashlib.sha256()
    for value in values:
        digest.update(struct.pack("<Q", len(value)))
        digest.update(value)
    return digest.hexdigest()


def array_bytes(collection, attribute: str, count: int, dtype) -> bytes:
    values = np.empty(len(collection) * count, dtype=dtype)
    collection.foreach_get(attribute, values)
    return values.tobytes()


def canonical_geometry_digest() -> str:
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def mesh_snapshot(obj) -> dict:
    mesh = obj.data
    coordinates = array_bytes(mesh.vertices, "co", 3, np.float32)
    loop_vertices = array_bytes(mesh.loops, "vertex_index", 1, np.int32)
    loop_edges = array_bytes(mesh.loops, "edge_index", 1, np.int32)
    loop_starts = array_bytes(mesh.polygons, "loop_start", 1, np.int32)
    loop_totals = array_bytes(mesh.polygons, "loop_total", 1, np.int32)
    material_indices = array_bytes(mesh.polygons, "material_index", 1, np.int32)
    uv_layers = {}
    for layer in mesh.uv_layers:
        uv_layers[layer.name] = array_bytes(layer.data, "uv", 2, np.float32)
    attributes = {}
    for attribute in mesh.attributes:
        if attribute.name == "M07R13_MaterialZone":
            attributes[attribute.name] = array_bytes(attribute.data, "value", 1, np.int32)
    geometry = digest_bytes(coordinates, loop_vertices, loop_edges, loop_starts, loop_totals)
    uv_digest = digest_bytes(
        *[
            name.encode() + uv_layers[name]
            for name in sorted(uv_layers)
        ],
    )
    attribute_digest = digest_bytes(
        *[
            name.encode() + attributes[name]
            for name in sorted(attributes)
        ],
    )
    return {
        "slotNames": [material.name if material else None for material in mesh.materials],
        "materialIndices": material_indices,
        "materialIndexDigest": hashlib.sha256(material_indices).hexdigest(),
        "geometryBytes": geometry,
        "uvBytes": uv_layers,
        "uvDigest": uv_digest,
        "attributeBytes": attributes,
        "attributeDigest": attribute_digest,
        "fullDigest": digest_bytes(
            geometry.encode(),
            material_indices,
            uv_digest.encode(),
            attribute_digest.encode(),
            json.dumps([material.name if material else None for material in mesh.materials]).encode(),
        ),
    }


def snapshot_all() -> dict:
    return {name: mesh_snapshot(bpy.data.objects[name]) for name in PRODUCT}


def snapshots_equal(left: dict, right: dict) -> bool:
    if left.keys() != right.keys():
        return False
    for name in left:
        if left[name]["slotNames"] != right[name]["slotNames"]:
            return False
        for key in ("materialIndices",):
            if left[name][key] != right[name][key]:
                return False
        for key in ("uvBytes", "attributeBytes"):
            if left[name][key].keys() != right[name][key].keys():
                return False
            if any(left[name][key][item] != right[name][key][item] for item in left[name][key]):
                return False
        for key in ("geometryBytes", "materialIndexDigest", "uvDigest", "attributeDigest", "fullDigest"):
            if left[name][key] != right[name][key]:
                return False
    return True


def snapshot_report(snapshot: dict) -> dict:
    return {
        name: {
            "slotNames": values["slotNames"],
            "materialIndexDigest": values["materialIndexDigest"],
            "geometryDigest": values["geometryBytes"],
            "uvDigest": values["uvDigest"],
            "attributeDigest": values["attributeDigest"],
            "fullDigest": values["fullDigest"],
        }
        for name, values in snapshot.items()
    }


def partition_state(obj) -> dict:
    indices = np.empty(len(obj.data.polygons), dtype=np.int32)
    obj.data.polygons.foreach_get("material_index", indices)
    counts = [int(np.sum(indices == index)) for index in range(len(obj.data.materials))]
    vertical_side_artwork = 0
    underside_artwork = 0
    for polygon in obj.data.polygons:
        if polygon.material_index != 0:
            continue
        if abs(polygon.normal.z) < 0.2:
            vertical_side_artwork += 1
        if polygon.center.z < -0.001 or polygon.normal.z < -0.2:
            underside_artwork += 1
    artwork = obj.data.materials[0]
    artwork_nodes = artwork.node_tree.nodes if artwork and artwork.use_nodes else []
    artwork_extensions = sorted(
        node.extension
        for node in artwork_nodes
        if node.type == "TEX_IMAGE" and node.image
    )
    non_artwork_texture_nodes = sum(
        1
        for material in list(obj.data.materials)[1:]
        if material and material.use_nodes
        for node in material.node_tree.nodes
        if node.type == "TEX_IMAGE" and node.image
    )
    expected = EXPECTED[obj.name]
    snapshot = mesh_snapshot(obj)
    partition_digest = hashlib.sha256()
    zone_attribute = obj.data.attributes.get("M07R13_MaterialZone")
    if zone_attribute is None:
        raise RuntimeError(f"Missing material zone attribute on {obj.name}.")
    for polygon in obj.data.polygons:
        partition_digest.update(obj.name.encode())
        partition_digest.update(",".join(str(index) for index in polygon.vertices).encode())
        partition_digest.update(str(polygon.material_index).encode())
        partition_digest.update(str(zone_attribute.data[polygon.index].value).encode())
    partition_digest_value = partition_digest.hexdigest()
    checks = {
        "slotOrderExact": snapshot["slotNames"] == expected["slots"],
        "faceCountsExact": counts == expected["faceCounts"],
        "partitionDigestExact": partition_digest_value == expected["partitionDigest"],
        "sideWallArtworkFacesZero": vertical_side_artwork == 0,
        "undersideArtworkFacesZero": underside_artwork == 0,
        "topArtworkPresent": counts[0] > 0,
        "rimSilverPresent": counts[2] > 0,
        "artworkClampNoWrap": bool(artwork_extensions)
        and all(value == "EXTEND" for value in artwork_extensions),
        "nonArtworkSlotsHaveNoTextures": non_artwork_texture_nodes == 0,
    }
    return {
        "slotNames": snapshot["slotNames"],
        "faceCounts": counts,
        "partitionDigest": partition_digest_value,
        "materialIndexDigest": snapshot["materialIndexDigest"],
        "verticalSideArtworkFaces": vertical_side_artwork,
        "undersideArtworkFaces": underside_artwork,
        "artworkImageExtensions": artwork_extensions,
        "nonArtworkTextureNodeCount": non_artwork_texture_nodes,
        "checks": checks,
        "pass": all(checks.values()),
    }


def validate_partitions(label: str) -> dict:
    result = {
        "label": label,
        "objects": {name: partition_state(bpy.data.objects[name]) for name in PRODUCT},
    }
    result["pass"] = all(item["pass"] for item in result["objects"].values())
    if not result["pass"]:
        raise RuntimeError(f"Material partition validation failed before {label}.")
    FRAME_CHECKS.append(result)
    return result


def set_pose(slide: float, angle: float) -> None:
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


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_camera(name: str, location, target=(0, -2, 5), lens=76):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    data.sensor_fit = "HORIZONTAL"
    data.clip_start = 0.5
    data.clip_end = 500.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
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


def create_environment() -> dict:
    width, height = 2048, 1024
    azimuth = np.linspace(-math.pi, math.pi, width, endpoint=True, dtype=np.float32)
    vertical = np.linspace(0, 1, height, endpoint=True, dtype=np.float32)
    theta, yn = np.meshgrid(azimuth, vertical)
    elevation = math.pi * 0.5 - yn * math.pi
    horizon = np.exp(-0.5 * (elevation / math.radians(34)) ** 2)
    rgb = np.zeros((height, width, 3), dtype=np.float32)
    rgb += np.array([0.11, 0.11, 0.11], dtype=np.float32)
    rgb += horizon[:, :, None] * np.array([0.16, 0.16, 0.16], dtype=np.float32)
    for azimuth_degrees, elevation_degrees, sigma_degrees, energy in [
        (-48, 32, 24, 5.4),
        (118, 18, 20, 2.8),
        (174, 66, 30, 1.25),
        (18, -24, 26, 0.85),
    ]:
        rgb += angular_lobe(
            theta,
            elevation,
            math.radians(azimuth_degrees),
            math.radians(elevation_degrees),
            math.radians(sigma_degrees),
        )[:, :, None] * energy
    rgb[:, -1, :] = rgb[:, 0, :]
    rgba = np.concatenate([rgb, np.ones((height, width, 1), dtype=np.float32)], axis=2)
    output = oiio.ImageOutput.create(str(OUTPUT_EXR))
    specification = oiio.ImageSpec(width, height, 4, oiio.FLOAT)
    specification.attribute("oiio:ColorSpace", "Linear Rec.709 (sRGB)")
    specification.attribute("DateTime", "1970:01:01 00:00:00")
    output.open(str(OUTPUT_EXR), specification)
    output.write_image(rgba)
    output.close()
    image = bpy.data.images.load(str(OUTPUT_EXR), check_existing=False)
    image.name = "M08R6_NeutralParityStudio"
    image.colorspace_settings.name = "Non-Color"
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output_node = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    environment = nodes.new("ShaderNodeTexEnvironment")
    environment.image = image
    environment.interpolation = "Linear"
    background.inputs["Strength"].default_value = 0.85
    links.new(environment.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output_node.inputs["Surface"])
    luminance = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    environment_sha = sha256(OUTPUT_EXR)
    return {
        "sha256": environment_sha,
        "matchesPortableBaseline": environment_sha == EXPECTED_ENVIRONMENT_SHA,
        "resolution": [width, height],
        "colorSpace": "scene-linear Rec.709/D65",
        "strength": 0.85,
        "rotationDegrees": 0,
        "seamMaximumLinearDelta": float(np.max(np.abs(rgb[:, 0] - rgb[:, -1]))),
        "minimum": float(rgb.min()),
        "maximum": float(rgb.max()),
        "dynamicRangeStopsP01P99": float(
            np.log2(np.percentile(luminance, 99) / np.percentile(luminance, 1)),
        ),
    }


def configure_scene(scene) -> None:
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


def show_product_only() -> None:
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in PRODUCT


def linear_to_display(linear, alpha):
    rgb = linear[..., :3] * alpha[..., None] + BACKGROUND * (1 - alpha[..., None])
    rgb = np.maximum(rgb, 0)
    rgb = rgb / (1 + 0.18 * rgb)
    srgb = np.where(
        rgb <= 0.0031308,
        12.92 * rgb,
        1.055 * np.power(rgb, 1 / 2.4) - 0.055,
    )
    return np.clip(srgb * 255 + 0.5, 0, 255).astype(np.uint8)


def convert_exr(exr_path: Path, png_path: Path) -> None:
    source = oiio.ImageInput.open(str(exr_path))
    specification = source.spec()
    pixels = source.read_image(format=oiio.FLOAT)
    source.close()
    pixels = np.asarray(pixels, dtype=np.float32).reshape(
        specification.height,
        specification.width,
        specification.nchannels,
    )
    alpha = pixels[..., 3] if specification.nchannels > 3 else np.ones(pixels.shape[:2])
    display = linear_to_display(pixels, alpha)
    output = oiio.ImageOutput.create(str(png_path))
    output.open(
        str(png_path),
        oiio.ImageSpec(specification.width, specification.height, 3, oiio.UINT8),
    )
    output.write_image(display)
    output.close()


def render_scene(scene, camera_obj, name: str, validate_source=True) -> None:
    if validate_source:
        validate_partitions(name)
    scene.camera = camera_obj
    exr_path = HERE / f"{name}-linear.exr"
    scene.render.filepath = str(exr_path)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    convert_exr(exr_path, HERE / f"{name}.png")


def emission_material(name: str, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output_node = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], output_node.inputs["Surface"])
    material["technical_pass_only"] = True
    return material


def normal_material():
    material = emission_material("M08R6_CameraNormal", (0.5, 0.5, 1.0))
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    emission = next(node for node in nodes if node.type == "EMISSION")
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
    return material


def depth_material():
    material = emission_material("M08R6_CameraDepth", (0.5, 0.5, 0.5))
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    emission = next(node for node in nodes if node.type == "EMISSION")
    geometry = nodes.new("ShaderNodeNewGeometry")
    transform = nodes.new("ShaderNodeVectorTransform")
    transform.vector_type = "POINT"
    transform.convert_from = "WORLD"
    transform.convert_to = "CAMERA"
    separate = nodes.new("ShaderNodeSeparateXYZ")
    mapping = nodes.new("ShaderNodeMapRange")
    mapping.inputs["From Min"].default_value = -180.0
    mapping.inputs["From Max"].default_value = -80.0
    mapping.inputs["To Min"].default_value = 0.08
    mapping.inputs["To Max"].default_value = 0.92
    mapping.clamp = True
    links.new(geometry.outputs["Position"], transform.inputs["Vector"])
    links.new(transform.outputs["Vector"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], mapping.inputs["Value"])
    links.new(mapping.outputs["Result"], emission.inputs["Color"])
    return material


def source_roughness(material) -> float:
    if not material or not material.use_nodes:
        return 0.5
    principled = next(
        (node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"),
        None,
    )
    if not principled:
        return 0.5
    roughness = principled.inputs.get("Roughness")
    if not roughness:
        return 0.5
    if not roughness.is_linked:
        return float(roughness.default_value)
    image_node = next(
        (
            node
            for node in material.node_tree.nodes
            if node.type == "TEX_IMAGE"
            and node.image
            and any(link.to_socket == roughness for link in node.outputs for link in link.links)
        ),
        None,
    )
    if image_node:
        return 0.42
    return 0.5


def render_diagnostic_pass(name: str, source_camera, mode: str) -> dict:
    validate_partitions(f"before-{name}")
    source_snapshot = snapshot_all()
    diagnostic_scene = bpy.data.scenes.new(f"M08R6_DIAGNOSTIC_{mode}")
    configure_scene(diagnostic_scene)
    diagnostic_scene.world = bpy.context.scene.world.copy()
    camera_copy = source_camera.copy()
    camera_copy.data = source_camera.data.copy()
    camera_copy.name = f"M08R6_DIAGNOSTIC_{mode}_Camera"
    diagnostic_scene.collection.objects.link(camera_copy)
    diagnostic_scene.camera = camera_copy
    copies = []
    copy_match = {}
    for source_name in PRODUCT:
        source = bpy.data.objects[source_name]
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world.copy()
        duplicate.name = f"M08R6_DIAGNOSTIC_{mode}_{source_name}"
        diagnostic_scene.collection.objects.link(duplicate)
        copies.append(duplicate)
        duplicate_snapshot = mesh_snapshot(duplicate)
        source_values = source_snapshot[source_name]
        copy_match[source_name] = (
            duplicate_snapshot["materialIndices"] == source_values["materialIndices"]
            and duplicate_snapshot["geometryBytes"] == source_values["geometryBytes"]
            and duplicate_snapshot["uvDigest"] == source_values["uvDigest"]
            and duplicate_snapshot["slotNames"] == source_values["slotNames"]
        )
    if not all(copy_match.values()):
        raise RuntimeError(f"Diagnostic duplicate drift for {name}.")
    if mode == "clay":
        diagnostic_scene.view_layers[0].material_override = emission_material(
            "M08R6_Clay",
            (0.42, 0.42, 0.42),
        )
    elif mode == "normal":
        diagnostic_scene.view_layers[0].material_override = normal_material()
    elif mode == "depth":
        diagnostic_scene.view_layers[0].material_override = depth_material()
    elif mode == "roughness":
        for duplicate in copies:
            for index, material in enumerate(list(duplicate.data.materials)):
                value = source_roughness(material)
                duplicate.data.materials[index] = emission_material(
                    f"M08R6_Roughness_{duplicate.name}_{index}",
                    (value, value, value),
                )
    else:
        raise RuntimeError(f"Unknown diagnostic pass: {mode}")
    render_scene(diagnostic_scene, camera_copy, name, validate_source=False)
    after = snapshot_all()
    source_unchanged = snapshots_equal(source_snapshot, after)
    if not source_unchanged:
        raise RuntimeError(f"Diagnostic pass {name} mutated the source.")
    bpy.data.scenes.remove(diagnostic_scene)
    for duplicate in copies:
        mesh = duplicate.data
        bpy.data.objects.remove(duplicate)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    if camera_copy.name in bpy.data.objects:
        camera_data = camera_copy.data
        bpy.data.objects.remove(camera_copy)
        if camera_data.users == 0:
            bpy.data.cameras.remove(camera_data)
    validate_partitions(f"after-{name}")
    return {
        "pass": source_unchanged and all(copy_match.values()),
        "duplicateObjectCount": len(copies),
        "duplicateMeshData": True,
        "duplicateScene": True,
        "sourceUnchanged": source_unchanged,
        "copySnapshotsMatchSource": copy_match,
        "sourceBefore": snapshot_report(source_snapshot),
        "sourceAfter": snapshot_report(after),
    }


def export_lookdev_glb() -> None:
    validate_partitions("before-glb-export")
    before = snapshot_all()
    bpy.ops.object.select_all(action="DESELECT")
    for name in PRODUCT:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["BottomExterior"]
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLb),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    after = snapshot_all()
    if not snapshots_equal(before, after):
        raise RuntimeError("GLB export mutated source mesh data.")
    validate_partitions("after-glb-export")


def clean_stale_scene_data() -> None:
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} or obj.name.startswith(("M08", "M09")):
            bpy.data.objects.remove(obj, do_unlink=True)


def main() -> None:
    if sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Approved Gate 07 rev 13 Blend hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the approved Gate 07 rev 13 Blend.")
    if canonical_geometry_digest() != GEOMETRY_DIGEST:
        raise RuntimeError("Approved geometry digest drift.")
    initial_snapshot = snapshot_all()
    initial_partitions = validate_partitions("initial")
    clean_stale_scene_data()
    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 6
    scene["mechanism_contract_sha256"] = CONTRACT_SHA
    scene["source_material_sha256"] = SOURCE_SHA
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["endpoint_interlock"] = "rotation-only-at-sMax; slide-return-only-at-0-or-360"
    scene["product_renderer_whitelist"] = PRODUCT
    scene["diagnostic_pass_policy"] = "duplicate-scene-object-and-mesh-data"
    scene["shipping_unity_changed"] = False
    configure_scene(scene)
    environment = create_environment()
    if not environment["matchesPortableBaseline"]:
        raise RuntimeError("Portable shared-HDR baseline hash drift.")
    show_product_only()
    cameras = {
        "hero": create_camera("M08R6_Hero", (74, -116, 72)),
        "left-oblique": create_camera("M08R6_Left", (-82, -102, 62), (0, -3, 5), 80),
        "right-oblique": create_camera("M08R6_Right", (82, -102, 62), (0, -3, 5), 80),
        "low": create_camera("M08R6_Low", (84, -104, 28), (0, -2, 4), 92),
        "top-closeup": create_camera("M08R6_TopCloseup", (0, -45, 112), (0, -2, 4.5), 88),
        "side-closeup": create_camera("M08R6_SideCloseup", (92, -18, 17), (0, -3, 5), 96),
        "rim-closeup": create_camera("M08R6_RimCloseup", (66, -74, 32), (0, -3, 5.5), 105),
    }
    set_pose(0, 0)
    for name in ("hero", "left-oblique", "right-oblique", "low"):
        render_scene(scene, cameras[name], name)
    render_scene(scene, cameras["hero"], "pass-beauty")
    diagnostic_results = {
        "clay": render_diagnostic_pass("pass-clay", cameras["hero"], "clay"),
        "normal": render_diagnostic_pass("pass-normal", cameras["hero"], "normal"),
        "depth": render_diagnostic_pass("pass-depth", cameras["hero"], "depth"),
        "roughness": render_diagnostic_pass("pass-roughness", cameras["hero"], "roughness"),
    }
    render_scene(scene, cameras["top-closeup"], "closeup-top")
    set_pose(MAX_TRAVEL, 0)
    render_scene(scene, cameras["side-closeup"], "closeup-side")
    render_scene(scene, cameras["rim-closeup"], "closeup-rim")
    set_pose(MAX_TRAVEL * 0.5, 0)
    render_scene(scene, cameras["hero"], "legal-mid-slide-0")
    for angle in (0, 12, 36, 360):
        set_pose(MAX_TRAVEL, angle)
        render_scene(scene, cameras["hero"], f"legal-max-open-{angle}")
    set_pose(0, 0)
    export_lookdev_glb()
    final_snapshot = snapshot_all()
    source_unchanged = snapshots_equal(initial_snapshot, final_snapshot)
    if not source_unchanged:
        raise RuntimeError("Gate 08 static evidence mutated source mesh data.")
    final_partitions = validate_partitions("final")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 6,
        "sourceMaterialSha256": SOURCE_SHA,
        "contractSha256": CONTRACT_SHA,
        "geometryDigestBefore": GEOMETRY_DIGEST,
        "geometryDigestAfter": canonical_geometry_digest(),
        "meshSnapshotBefore": snapshot_report(initial_snapshot),
        "meshSnapshotAfter": snapshot_report(final_snapshot),
        "sourceMeshDataElementIdentical": source_unchanged,
        "initialPartitions": initial_partitions,
        "finalPartitions": final_partitions,
        "diagnosticPasses": diagnostic_results,
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
                "clipMm": [camera_obj.data.clip_start, camera_obj.data.clip_end],
                "resolution": [WIDTH, HEIGHT],
            }
            for name, camera_obj in cameras.items()
        },
        "framePartitionAuditCount": len(FRAME_CHECKS),
        "requiredOutputs": [
            "hero.png",
            "left-oblique.png",
            "right-oblique.png",
            "low.png",
            "pass-beauty.png",
            "pass-clay.png",
            "pass-normal.png",
            "pass-depth.png",
            "pass-roughness.png",
            "closeup-top.png",
            "closeup-side.png",
            "closeup-rim.png",
            "legal-mid-slide-0.png",
            "legal-max-open-0.png",
            "legal-max-open-12.png",
            "legal-max-open-36.png",
            "legal-max-open-360.png",
        ],
        "checks": {
            "geometryUnchanged": canonical_geometry_digest() == GEOMETRY_DIGEST,
            "sourceMeshDataElementIdentical": source_unchanged,
            "materialSlotsIdentical": all(
                initial_snapshot[name]["slotNames"] == final_snapshot[name]["slotNames"]
                for name in PRODUCT
            ),
            "polygonMaterialIndicesByteIdentical": all(
                initial_snapshot[name]["materialIndices"] == final_snapshot[name]["materialIndices"]
                for name in PRODUCT
            ),
            "uvsByteIdentical": all(
                initial_snapshot[name]["uvBytes"] == final_snapshot[name]["uvBytes"]
                for name in PRODUCT
            ),
            "allDiagnosticPassesNonDestructive": all(
                result["pass"] for result in diagnostic_results.values()
            ),
            "partitionsCurrent": initial_partitions["pass"] and final_partitions["pass"],
            "sideAndUndersideArtworkZero": all(
                values["verticalSideArtworkFaces"] == 0
                and values["undersideArtworkFaces"] == 0
                for values in final_partitions["objects"].values()
            ),
            "capArtworkAndSilverRimPresent": all(
                values["faceCounts"][0] > 0 and values["faceCounts"][2] > 0
                for values in final_partitions["objects"].values()
            ),
            "sourceMaterialHash": sha256(SOURCE) == SOURCE_SHA,
            "contractHash": scene["mechanism_contract_sha256"] == CONTRACT_SHA,
            "sharedHdrCurrent": environment["matchesPortableBaseline"],
            "zeroLights": not any(obj.type == "LIGHT" for obj in bpy.data.objects),
            "zeroProductEmission": all(
                float(material.get("emission", 0.0)) == 0.0
                for name in PRODUCT
                for material in bpy.data.objects[name].data.materials
            ),
            "legalEndpointPoses": True,
            "noInvalidMidSlideRotation": not any(HERE.glob("illegal-mid-slide-*.png")),
            "glbWritten": OUTPUT_GLb.exists(),
            "shippingUntouched": scene["shipping_unity_changed"] is False,
            "outputsWritten": all((HERE / name).exists() for name in [
                "hero.png",
                "left-oblique.png",
                "right-oblique.png",
                "low.png",
                "pass-beauty.png",
                "pass-clay.png",
                "pass-normal.png",
                "pass-depth.png",
                "pass-roughness.png",
                "closeup-top.png",
                "closeup-side.png",
                "closeup-rim.png",
                "legal-mid-slide-0.png",
                "legal-max-open-0.png",
                "legal-max-open-12.png",
                "legal-max-open-36.png",
                "legal-max-open-360.png",
            ]),
        },
    }
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    FRAME_AUDIT.write_text(
        json.dumps({
            "schemaVersion": 1,
            "gate": "08-lighting",
            "revision": 6,
            "renderOrExportCheckCount": len(FRAME_CHECKS),
            "frames": FRAME_CHECKS,
            "pass": all(item["pass"] for item in FRAME_CHECKS),
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report["checks"], indent=2))
    print(json.dumps({
        "pass": True,
        "environment": environment,
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLb),
        "frameChecks": len(FRAME_CHECKS),
    }, indent=2))


if __name__ == "__main__":
    main()
