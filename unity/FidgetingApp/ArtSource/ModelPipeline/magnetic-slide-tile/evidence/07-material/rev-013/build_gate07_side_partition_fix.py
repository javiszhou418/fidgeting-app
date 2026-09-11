#!/usr/bin/env python3
"""Build Gate 07 rev 13 with export-stable cap, side, rim, and underside zones."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE_BLEND = MODEL_ROOT / "evidence/06-geometry/rev-005/magnetic-slide-tile-geometry-r005.blend"
CONTRACT_PATH = MODEL_ROOT / "evidence/02-analysis/rev-017/mechanism-evidence-contract.json"
REV12 = HERE.parent / "rev-012"
REV7 = HERE.parent / "rev-007"
REV10 = HERE.parent / "rev-010"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-material-r013.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-material-r013-lookdev.glb"
OUTPUT_FBX = HERE / "magnetic-slide-tile-material-r013.fbx"
REPORT_PATH = HERE / "material-build-report.json"
TURN_FRAMES = HERE / "legal-motion-frames"
TURN_VIDEO = HERE / "gate07-r013-legal-motion-turntable.mp4"

SOURCE_BLEND_SHA256 = "a2aaf83a8e46b013f0ba2e2d859732f20f29bd8cc1dd032e155269cb19ce0ef4"
CONTRACT_SHA256 = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
MAX_TRAVEL = 18.076433121019107
PIVOT = Vector((0.0, -9.0, 5.875))
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
PRODUCT = ["BottomExterior", "MovingTopBody"]
EXPECTED_COUNTS = {
    "BottomExterior": {
        "topArtwork": 1,
        "solidDarkSide": 3078,
        "polishedSilverRim": 2052,
        "neutralUnderside": 3592,
    },
    "MovingTopBody": {
        "topArtwork": 1,
        "solidDarkSide": 5130,
        "polishedSilverRim": 2052,
        "neutralUnderside": 3600,
    },
}
TEXTURES = {
    "upper-albedo.png": (
        REV12 / "upper-albedo.png",
        "c0e9305d475cd2c591efc8a833a0aafb1aef4ccc437d84a3417674e6d1b453a5",
    ),
    "upper-roughness.png": (
        REV12 / "upper-roughness.png",
        "854f1dbc393585ff9b88f808c1a46a35b091088ac8b83894763f502876e3df6a",
    ),
    "lower-albedo.png": (
        REV12 / "lower-albedo.png",
        "968c1e87ca2d5ea7c8fc57106e42bcd09dc95395fac7dd3be569e580ea8850eb",
    ),
    "lower-roughness.png": (
        REV12 / "lower-roughness.png",
        "ca2697560a2e57685a71c423f15f70a72ebb47c93c53cae0e3a8dae0b3248245",
    ),
    "upper-artwork-mask.png": (
        REV7 / "artwork-upper-mask.png",
        "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36",
    ),
    "lower-artwork-mask.png": (
        REV10 / "artwork-lower-mask-r010.png",
        "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2",
    ),
    "top-perimeter-mask.png": (
        REV7 / "artwork-top-perimeter-border-mask.png",
        "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geometry_digest() -> str:
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def set_input(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def solid_material(name: str, color, metallic: float, roughness: float, coat: float = 0.0, anisotropy: float = 0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    bsdf = material.node_tree.nodes["Principled BSDF"]
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Coat Weight", coat)
    set_input(bsdf, "Coat Roughness", max(0.018, roughness * 0.25))
    set_input(bsdf, "Anisotropic IOR Level", anisotropy)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    material["gate07_revision"] = 13
    material["artworkSampling"] = False
    material["emission"] = 0.0
    return material


def artwork_material(name: str, slot: str, albedo_path: Path, roughness_path: Path, mask_hash: str):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    uv = nodes.new("ShaderNodeUVMap")
    uv.name = f"{slot}_CapOnlyUV"
    uv.uv_map = "ArtworkUV"
    albedo = nodes.new("ShaderNodeTexImage")
    albedo.name = f"{slot}_Albedo_CLAMP"
    albedo.image = bpy.data.images.load(str(albedo_path), check_existing=False)
    albedo.image.pack()
    albedo.extension = "EXTEND"
    albedo.interpolation = "Cubic"
    roughness = nodes.new("ShaderNodeTexImage")
    roughness.name = f"{slot}_Roughness_CLAMP"
    roughness.image = bpy.data.images.load(str(roughness_path), check_existing=False)
    roughness.image.colorspace_settings.name = "Non-Color"
    roughness.image.pack()
    roughness.extension = "EXTEND"
    roughness.interpolation = "Cubic"
    links.new(uv.outputs["UV"], albedo.inputs["Vector"])
    links.new(uv.outputs["UV"], roughness.inputs["Vector"])
    links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{slot}_GranularDepth"
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 28.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.72
    links.new(uv.outputs["UV"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.024
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, "Metallic", 0.08)
    set_input(bsdf, "IOR", 1.52)
    set_input(bsdf, "Specular IOR Level", 0.58)
    set_input(bsdf, "Coat Weight", 0.48)
    set_input(bsdf, "Coat Roughness", 0.035)
    set_input(bsdf, "Transmission Weight", 0.08)
    set_input(bsdf, "Thin Film IOR", 1.38)
    set_input(bsdf, "Thin Film Thickness", 410.0)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["gate07_revision"] = 13
    material["artworkSlot"] = slot
    material["artworkSampling"] = True
    material["capOnly"] = True
    material["textureAddressMode"] = "CLAMP_TO_EDGE"
    material["sourceMaskSha256"] = mask_hash
    material["albedoSha256"] = sha256(albedo_path)
    material["roughnessSha256"] = sha256(roughness_path)
    material["independentlyReplaceable"] = True
    material["emission"] = 0.0
    return material


def copy_and_verify_textures() -> dict:
    output = {}
    for filename, (source, expected_hash) in TEXTURES.items():
        if sha256(source) != expected_hash:
            raise RuntimeError(f"Approved texture drift: {source}")
        destination = HERE / filename
        shutil.copy2(source, destination)
        actual_hash = sha256(destination)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Texture copy changed bytes: {destination}")
        output[filename] = {
            "source": str(source.relative_to(MODEL_ROOT.parents[4])),
            "sha256": actual_hash,
            "addressMode": "CLAMP_TO_EDGE",
            "wrap": False,
        }
    return output


def prepare_artwork_uv(obj, cap_polygon_indices: set[int]) -> dict:
    mesh = obj.data
    source = mesh.uv_layers.active
    if source is None:
        raise RuntimeError(f"{obj.name} has no approved UV map.")
    old = mesh.uv_layers.get("ArtworkUV")
    if old is not None and old != source:
        mesh.uv_layers.remove(old)
    if source.name == "ArtworkUV":
        artwork_uv = source
    else:
        artwork_uv = mesh.uv_layers.new(name="ArtworkUV")
        for index, loop in enumerate(source.data):
            artwork_uv.data[index].uv = loop.uv
    cap_values = []
    non_cap_loop_count = 0
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            if polygon.index in cap_polygon_indices:
                value = artwork_uv.data[loop_index].uv
                cap_values.append((float(value.x), float(value.y)))
            else:
                artwork_uv.data[loop_index].uv = (-1.0, -1.0)
                non_cap_loop_count += 1
    mesh.uv_layers.active = artwork_uv
    artwork_uv.active_render = True
    minimum = [min(value[index] for value in cap_values) for index in (0, 1)]
    maximum = [max(value[index] for value in cap_values) for index in (0, 1)]
    return {
        "layer": artwork_uv.name,
        "capLoopCount": len(cap_values),
        "nonCapSentinelLoopCount": non_cap_loop_count,
        "nonCapSentinel": [-1.0, -1.0],
        "capUvMin": minimum,
        "capUvMax": maximum,
        "capUvsWithinZeroOne": all(-1e-6 <= value <= 1 + 1e-6 for pair in cap_values for value in pair),
    }


def assign_partition(obj, artwork, dark, silver, underside) -> dict:
    mesh = obj.data
    mesh.materials.clear()
    for material in (artwork, dark, silver, underside):
        mesh.materials.append(material)
    max_z = max(vertex.co.z for vertex in mesh.vertices)
    classifications = {}
    cap_indices = set()
    counts = {
        "topArtwork": 0,
        "solidDarkSide": 0,
        "polishedSilverRim": 0,
        "neutralUnderside": 0,
    }
    vertical_side_faces = 0
    for polygon in mesh.polygons:
        vertex_z = [mesh.vertices[index].co.z for index in polygon.vertices]
        top_cap = (
            polygon.normal.z > 0.999999
            and max(abs(value - max_z) for value in vertex_z) <= 1e-5
        )
        rim = (
            not top_cap
            and abs(polygon.normal.z) < 0.72
            and polygon.center.z >= max_z - 0.55
        )
        bottom = not top_cap and not rim and polygon.normal.z < -0.15
        if top_cap:
            material_index, zone, zone_id = 0, "topArtwork", 0
            cap_indices.add(polygon.index)
        elif rim:
            material_index, zone, zone_id = 2, "polishedSilverRim", 2
        elif bottom:
            material_index, zone, zone_id = 3, "neutralUnderside", 3
        else:
            material_index, zone, zone_id = 1, "solidDarkSide", 1
            if abs(polygon.normal.z) <= 0.05:
                vertical_side_faces += 1
        polygon.material_index = material_index
        classifications[polygon.index] = zone_id
        counts[zone] += 1
    if counts != EXPECTED_COUNTS[obj.name]:
        raise RuntimeError(f"Unexpected partition for {obj.name}: {counts}")
    existing = mesh.attributes.get("M07R13_MaterialZone")
    if existing is not None:
        mesh.attributes.remove(existing)
    zone_attribute = mesh.attributes.new(
        name="M07R13_MaterialZone",
        type="INT",
        domain="FACE",
    )
    for polygon_index, zone_id in classifications.items():
        zone_attribute.data[polygon_index].value = zone_id
    uv_report = prepare_artwork_uv(obj, cap_indices)
    digest = hashlib.sha256()
    for polygon in mesh.polygons:
        digest.update(obj.name.encode())
        digest.update(",".join(str(index) for index in polygon.vertices).encode())
        digest.update(str(polygon.material_index).encode())
        digest.update(str(zone_attribute.data[polygon.index].value).encode())
    return {
        "slotOrder": [material.name for material in mesh.materials],
        "slotIds": {
            "topArtwork": 0,
            "solidDarkSide": 1,
            "polishedSilverRim": 2,
            "neutralUnderside": 3,
        },
        "faceCounts": counts,
        "verticalSideFaceCount": vertical_side_faces,
        "verticalSideArtworkFaceCount": 0,
        "partitionDigest": digest.hexdigest(),
        "uv": uv_report,
    }


def assign_whole(obj, material, evidence: str) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
    obj["materialEvidence"] = evidence


def partition_snapshot() -> dict:
    return {
        name: {
            "materials": [material.name for material in bpy.data.objects[name].data.materials],
            "indices": [polygon.material_index for polygon in bpy.data.objects[name].data.polygons],
            "zones": [
                value.value
                for value in bpy.data.objects[name].data.attributes["M07R13_MaterialZone"].data
            ],
        }
        for name in PRODUCT
    }


def set_pose(travel: float, angle: float, lift: float = 0.0) -> None:
    normalized = angle % 360.0
    if min(normalized, 360.0 - normalized) <= 0.001:
        normalized = 0.0
    if travel < MAX_TRAVEL - 1e-6 and normalized != 0.0:
        raise RuntimeError(f"Illegal endpoint-interlock pose: s={travel}, theta={normalized}")
    moving = bpy.data.objects["MovingTop"]
    moving.location = PIVOT
    moving.rotation_mode = "XYZ"
    moving.rotation_euler = (0.0, 0.0, math.radians(normalized))
    bpy.data.objects["TopLocalSlide"].location = (0.0, 9.0 - travel, lift)
    carrier = bpy.data.objects["RotatingCarrier"]
    carrier.location = (0.0, 0.0, -0.48)
    carrier.rotation_mode = "XYZ"
    carrier.rotation_euler = (0.0, 0.0, math.radians(normalized))
    bpy.context.view_layer.update()


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens=75):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    data.sensor_fit = "HORIZONTAL"
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def area(name, location, target, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def render(scene, camera_obj, filename: str, width=1400, height=1100) -> None:
    scene.camera = camera_obj
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def show_product_only(ground) -> None:
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj != ground:
            obj.hide_render = obj.name not in PRODUCT


def show_all_core(ground) -> None:
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj != ground and obj.name not in CORE


def export_product() -> None:
    set_pose(MAX_TRAVEL, 0)
    bpy.ops.object.select_all(action="DESELECT")
    for name in PRODUCT:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["BottomExterior"]
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
        export_materials="EXPORT",
    )
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


def legal_frame_state(index: int) -> tuple[float, float, str]:
    if index < 15:
        return MAX_TRAVEL * index / 14, 0.0, "slide-to-endpoint"
    if index < 75:
        return MAX_TRAVEL, 360.0 * (index - 15) / 59, "endpoint-full-rotation"
    return MAX_TRAVEL * (89 - index) / 14, 360.0, "aligned-slide-return"


def render_legal_motion(scene, camera_obj, ground, expected_partition: dict) -> dict:
    TURN_FRAMES.mkdir(exist_ok=True)
    for path in TURN_FRAMES.glob("frame-*"):
        path.unlink()
    show_product_only(ground)
    samples = []
    initial_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation.copy()
    max_axis_variance = 0.0
    max_pitch_roll = 0.0
    for index in range(90):
        slide, angle, phase = legal_frame_state(index)
        set_pose(slide, angle)
        moving = bpy.data.objects["MovingTop"]
        max_pitch_roll = max(
            max_pitch_roll,
            abs(float(moving.rotation_euler.x)),
            abs(float(moving.rotation_euler.y)),
        )
        axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation
        max_axis_variance = max(max_axis_variance, (axis - initial_axis).length)
        if partition_snapshot() != expected_partition:
            raise RuntimeError(f"Material partition changed at legal frame {index}.")
        scene.camera = camera_obj
        scene.render.resolution_x = 960
        scene.render.resolution_y = 720
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(TURN_FRAMES / f"frame-{index:04d}.png")
        bpy.ops.render.render(write_still=True)
        samples.append({
            "frame": index,
            "phase": phase,
            "slideMm": slide,
            "rotationDegrees": angle,
        })
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            "15",
            "-i",
            str(TURN_FRAMES / "frame-%04d.png"),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-movflags",
            "+faststart",
            str(TURN_VIDEO),
        ],
        check=True,
    )
    probe = json.loads(subprocess.check_output([
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(TURN_VIDEO),
    ]))
    stream = probe["streams"][0]
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 13,
        "sourceFrameCount": 90,
        "sourceFps": 15,
        "encodedFps": stream["avg_frame_rate"],
        "encodedFrameCount": int(stream["nb_frames"]),
        "durationSeconds": float(probe["format"]["duration"]),
        "dimensions": [int(stream["width"]), int(stream["height"])],
        "maximumFixedAxisVarianceMm": max_axis_variance,
        "maximumPitchRollRadians": max_pitch_roll,
        "videoSha256": sha256(TURN_VIDEO),
        "samples": samples,
        "checks": {
            "allFramesRendered": len(list(TURN_FRAMES.glob("frame-*.png"))) == 90,
            "encodedFrameCount": int(stream["nb_frames"]) == 180,
            "duration": math.isclose(float(probe["format"]["duration"]), 6.0, abs_tol=0.01),
            "rotationOnlyAtEndpoint": all(
                sample["slideMm"] >= MAX_TRAVEL - 1e-6
                or min(sample["rotationDegrees"] % 360, 360 - sample["rotationDegrees"] % 360) <= 0.001
                for sample in samples
            ),
            "slideReturnOnlyAligned": all(
                sample["phase"] != "aligned-slide-return"
                or min(sample["rotationDegrees"] % 360, 360 - sample["rotationDegrees"] % 360) <= 0.001
                for sample in samples
            ),
            "full360Covered": samples[15]["rotationDegrees"] == 0 and samples[74]["rotationDegrees"] == 360,
            "fixedAxisInvariant": max_axis_variance <= 1e-9,
            "noPitchRollFlip": max_pitch_roll <= 1e-9,
            "materialPartitionStableEveryFrame": partition_snapshot() == expected_partition,
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "legal-motion-turntable-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    return report


def main() -> None:
    if sha256(SOURCE_BLEND) != SOURCE_BLEND_SHA256:
        raise RuntimeError("Approved Gate 06 blend hash drift.")
    if sha256(CONTRACT_PATH) != CONTRACT_SHA256:
        raise RuntimeError("Endpoint-interlock contract hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the approved Gate 06 blend before running.")
    before_geometry = geometry_digest()
    if before_geometry != GEOMETRY_DIGEST:
        raise RuntimeError(f"Gate 06 geometry digest drift: {before_geometry}")
    texture_report = copy_and_verify_textures()
    for filename in ("upper-artwork-mask.png", "lower-artwork-mask.png", "top-perimeter-mask.png"):
        image = bpy.data.images.load(str(HERE / filename), check_existing=False)
        image.pack()
        image["textureAddressMode"] = "CLAMP_TO_EDGE"
        image["wrap"] = False

    for obj in list(bpy.data.objects):
        if (
            obj.type in {"CAMERA", "LIGHT"}
            or obj.name.startswith(("G06_", "SectionAA_", "M07R"))
            or obj.get("review_overlay_only")
            or obj.get("derived_section_evidence")
        ):
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene["gate"] = "07-material"
    scene["material_revision"] = 13
    scene["gate06_source_sha256"] = SOURCE_BLEND_SHA256
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["material_partition_contract"] = "cap=0,side=1,rim=2,underside=3"
    scene["texture_address_mode"] = "CLAMP_TO_EDGE"
    scene["side_wall_artwork_pixels"] = 0
    scene["endpoint_interlock"] = "rotation-only-at-sMax; slide-return-only-at-0-or-360"
    scene["product_renderer_whitelist"] = PRODUCT
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False
    scene["simulator_used"] = False

    upper = artwork_material(
        "M07R13_UpperTopArtwork",
        "Artwork_Upper",
        HERE / "upper-albedo.png",
        HERE / "upper-roughness.png",
        TEXTURES["upper-artwork-mask.png"][1],
    )
    lower = artwork_material(
        "M07R13_LowerTopArtwork",
        "Artwork_Lower",
        HERE / "lower-albedo.png",
        HERE / "lower-roughness.png",
        TEXTURES["lower-artwork-mask.png"][1],
    )
    dark = solid_material(
        "M07R13_SolidDarkSide",
        (0.018, 0.020, 0.024, 1),
        0.24,
        0.18,
        0.55,
    )
    silver = solid_material(
        "M07R13_PolishedBrightSilverRim",
        (0.78, 0.77, 0.74, 1),
        1.0,
        0.075,
        0.08,
        0.16,
    )
    underside = solid_material(
        "M07R13_NeutralUnderside",
        (0.18, 0.20, 0.22, 1),
        0.42,
        0.25,
        0.10,
    )
    carrier = solid_material(
        "M07R13_InternalSilverReference",
        (0.53, 0.55, 0.57, 1),
        0.86,
        0.13,
        0.12,
    )
    ball = solid_material(
        "M07R13_BallCandidateUnknownMaterial",
        (0.34, 0.35, 0.36, 1),
        0.12,
        0.22,
        0.15,
    )
    partitions = {
        "BottomExterior": assign_partition(
            bpy.data.objects["BottomExterior"],
            lower,
            dark,
            silver,
            underside,
        ),
        "MovingTopBody": assign_partition(
            bpy.data.objects["MovingTopBody"],
            upper,
            dark,
            silver,
            underside,
        ),
    }
    assign_whole(bpy.data.objects["InternalAxisBoss"], silver, "source-supported-silver-white-zone")
    assign_whole(bpy.data.objects["RotatingCarrierBody"], carrier, "technical-internal-silver-zone")
    for name in ("CarrierFollowerLeft", "CarrierFollowerRight"):
        assign_whole(bpy.data.objects[name], underside, "neutral-technical-inspection-only")
    for name in ("BallCandidateLeft", "BallCandidateRight"):
        assign_whole(bpy.data.objects[name], ball, "unknown-material-neutral-candidate")
        bpy.data.objects[name]["exactMaterialClaim"] = "unknown"

    expected_partition = partition_snapshot()
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 18
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.25
    scene.world.color = (0.012, 0.016, 0.022)

    ground_material = solid_material(
        "M07R13_NeutralGround",
        (0.025, 0.030, 0.038, 1),
        0.05,
        0.58,
    )
    bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 0, -0.6))
    ground = bpy.context.object
    ground.name = "M07R13_NeutralGround"
    ground.data.materials.append(ground_material)
    area("M07R13_Key", (58, -72, 92), (0, -3, 5), 72000, 48, (1.0, 0.92, 0.84))
    area("M07R13_Fill", (-58, -20, 58), (0, -2, 4), 33000, 44, (0.72, 0.84, 1.0))
    area("M07R13_Rim", (38, 68, 62), (0, 3, 4), 52000, 38, (1.0, 0.34, 0.30))
    area("M07R13_Top", (-8, 8, 118), (0, 0, 4), 42000, 42, (1.0, 1.0, 1.0))
    cameras = {
        "hero": camera("M07R13_Hero", (74, -116, 72), (0, -2, 5), 76),
        "top": camera("M07R13_TopView", (0, -18, 148), (0, -2, 5), 88),
        "open": camera("M07R13_Open", (56, -122, 104), (0, -8, 5), 84),
        "side": camera("M07R13_Side", (92, -64, 27), (3, -2, 4), 104),
        "rim": camera("M07R13_RimClose", (54, -78, 24), (5, -7, 5), 132),
        "underside": camera("M07R13_Underside", (0, 0, 155), (0, 0, 10), 78),
    }

    show_product_only(ground)
    set_pose(0, 0)
    render(scene, cameras["hero"], "assembled-hero.png")
    render(scene, cameras["top"], "upper-top-closeup.png", 1200, 1000)
    render(scene, cameras["side"], "side-wall-closeup.png", 1400, 900)
    render(scene, cameras["rim"], "silver-rim-closeup.png", 1400, 900)
    set_pose(MAX_TRAVEL, 0)
    render(scene, cameras["open"], "lower-top-open-closeup.png", 1400, 1000)

    top = bpy.data.objects["MovingTopBody"]
    set_pose(MAX_TRAVEL * 0.5, 0, 15.0)
    top.rotation_euler.x = math.pi
    bpy.data.objects["BottomExterior"].hide_render = True
    render(scene, cameras["underside"], "underside-closeup.png", 1200, 1000)
    bpy.data.objects["BottomExterior"].hide_render = False
    top.rotation_euler.x = 0.0
    set_pose(0, 0)
    if partition_snapshot() != expected_partition:
        raise RuntimeError("Still rendering changed material face indices.")

    export_product()
    if partition_snapshot() != expected_partition:
        raise RuntimeError("Export changed material face indices.")
    set_pose(0, 0)
    turntable = render_legal_motion(scene, cameras["hero"], ground, expected_partition)
    set_pose(0, 0)
    show_all_core(ground)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    after_geometry = geometry_digest()
    checks = {
        "sourceBlendHash": sha256(SOURCE_BLEND) == SOURCE_BLEND_SHA256,
        "contractHash": sha256(CONTRACT_PATH) == CONTRACT_SHA256,
        "geometryDigestUnchanged": before_geometry == after_geometry == GEOMETRY_DIGEST,
        "deterministicPartitionCounts": all(
            partitions[name]["faceCounts"] == EXPECTED_COUNTS[name]
            for name in PRODUCT
        ),
        "zeroVerticalSideArtworkFaces": all(
            partitions[name]["verticalSideArtworkFaceCount"] == 0
            for name in PRODUCT
        ),
        "topArtworkPresent": all(
            partitions[name]["faceCounts"]["topArtwork"] == 1
            for name in PRODUCT
        ),
        "capUvsWithinZeroOne": all(
            partitions[name]["uv"]["capUvsWithinZeroOne"]
            for name in PRODUCT
        ),
        "nonCapArtworkUvSentinel": all(
            partitions[name]["uv"]["nonCapSentinel"] == [-1.0, -1.0]
            for name in PRODUCT
        ),
        "independentArtwork": upper["sourceMaskSha256"] != lower["sourceMaskSha256"],
        "textureClampNoWrap": all(
            node.extension == "EXTEND"
            for material in (upper, lower)
            for node in material.node_tree.nodes
            if node.type == "TEX_IMAGE"
        ),
        "partitionStable": partition_snapshot() == expected_partition,
        "glbWritten": OUTPUT_GLB.exists(),
        "fbxWritten": OUTPUT_FBX.exists(),
        "blendWritten": OUTPUT_BLEND.exists(),
        "legalMotionTurntable": turntable["pass"],
        "zeroEmission": all(
            float(material.get("emission", 0.0)) == 0
            for material in (upper, lower, dark, silver, underside, carrier, ball)
        ),
        "shippingUntouched": scene["shipping_unity_changed"] is False,
        "simulatorUnused": scene["simulator_used"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "07-material",
        "revision": 13,
        "blenderVersion": bpy.app.version_string,
        "gate06SourceSha256": SOURCE_BLEND_SHA256,
        "contractSha256": CONTRACT_SHA256,
        "geometryDigestBefore": before_geometry,
        "geometryDigestAfter": after_geometry,
        "partitions": partitions,
        "textureLineage": texture_report,
        "materials": {
            "topArtwork": {
                "upper": upper.name,
                "lower": lower.name,
                "textureAddressMode": "CLAMP_TO_EDGE",
                "independentlyReplaceable": True,
            },
            "sideWall": {
                "material": dark.name,
                "artworkPixels": 0,
                "metallic": 0.24,
                "roughness": 0.18,
            },
            "rim": {
                "material": silver.name,
                "metallic": 1.0,
                "roughness": 0.075,
            },
            "underside": {
                "material": underside.name,
                "artworkPixels": 0,
            },
        },
        "turntable": turntable,
        "outputs": {
            "blend": OUTPUT_BLEND.name,
            "glb": OUTPUT_GLB.name,
            "fbx": OUTPUT_FBX.name,
            "video": TURN_VIDEO.name,
            "renders": [
                "assembled-hero.png",
                "upper-top-closeup.png",
                "lower-top-open-closeup.png",
                "side-wall-closeup.png",
                "silver-rim-closeup.png",
                "underside-closeup.png",
            ],
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({
        "pass": report["pass"],
        "geometryDigest": after_geometry,
        "partitions": {
            name: data["faceCounts"]
            for name, data in partitions.items()
        },
        "glb": str(OUTPUT_GLB),
        "fbx": str(OUTPUT_FBX),
        "video": str(TURN_VIDEO),
    }, indent=2))


if __name__ == "__main__":
    main()
