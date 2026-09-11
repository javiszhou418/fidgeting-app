#!/usr/bin/env python3
"""Audit Gate 09 rev 9 Blender, HDR, cubemap, and GLB evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "magnetic-slide-tile-environment-r009.blend"
GLB = HERE / "magnetic-slide-tile-environment-r009-lookdev.glb"
TARGET = HERE / "target-shipping-studio-r009.exr"
REPORT = HERE / "blender-environment-audit.json"
EXPECTED = {
    "BottomExterior": {
        "topArtwork": 511,
        "solidDarkSide": 6156,
        "polishedSilverRim": 4104,
        "neutralUnderside": 7693,
    },
    "MovingTopBody": {
        "topArtwork": 511,
        "solidDarkSide": 10268,
        "polishedSilverRim": 4104,
        "neutralUnderside": 11805,
    },
}

spec = importlib.util.spec_from_file_location(
    "gate09_builder",
    HERE / "build_gate09_current_environment.py",
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
helpers = builder.helpers


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError("Invalid GLB header.")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RuntimeError("Missing GLB JSON chunk.")
    return json.loads(data[20:20 + chunk_length].decode("utf-8").rstrip("\x00 \t\r\n"))


def material_zone(name: str) -> str:
    if "Artwork" in name:
        return "topArtwork"
    if "SolidDarkSide" in name:
        return "solidDarkSide"
    if "PolishedBrightSilverRim" in name:
        return "polishedSilverRim"
    if "NeutralUnderside" in name:
        return "neutralUnderside"
    return "other"


def inspect_imported_object(obj) -> dict:
    counts = {key: 0 for key in [
        "topArtwork",
        "solidDarkSide",
        "polishedSilverRim",
        "neutralUnderside",
        "other",
    ]}
    side_artwork = 0
    underside_artwork = 0
    artwork_uvs = []
    uv_layer = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        material = obj.data.materials[polygon.material_index]
        zone = material_zone(material.name)
        counts[zone] += 1
        if zone == "topArtwork":
            if abs(polygon.normal.z) < 0.2:
                side_artwork += 1
            if polygon.normal.z < -0.2:
                underside_artwork += 1
            if uv_layer:
                artwork_uvs.extend(
                    tuple(uv_layer.data[index].uv)
                    for index in polygon.loop_indices
                )
    uv_array = np.asarray(artwork_uvs, dtype=np.float64)
    checks = {
        "triangleCountsExact": all(
            counts[key] == value for key, value in EXPECTED[obj.name].items()
        ),
        "noUnknownMaterial": counts["other"] == 0,
        "sideArtworkZero": side_artwork == 0,
        "undersideArtworkZero": underside_artwork == 0,
        "capArtworkPresent": counts["topArtwork"] > 0,
        "silverRimPresent": counts["polishedSilverRim"] > 0,
        "capUvsWithinZeroOne": uv_array.size > 0
        and float(uv_array.min()) >= 0
        and float(uv_array.max()) <= 1,
    }
    return {
        "materialSlots": [material.name for material in obj.data.materials],
        "zoneTriangleCounts": counts,
        "sideArtworkTriangles": side_artwork,
        "undersideArtworkTriangles": underside_artwork,
        "artworkUvMin": uv_array.min(axis=0).tolist() if uv_array.size else None,
        "artworkUvMax": uv_array.max(axis=0).tolist() if uv_array.size else None,
        "checks": checks,
        "pass": all(checks.values()),
    }


def read_exr(path: Path) -> tuple[np.ndarray, dict]:
    source = oiio.ImageInput.open(str(path))
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
    }


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open Gate 09 rev 9 environment Blend.")
    build = json.loads((HERE / "environment-build-validation.json").read_text())
    turntable = json.loads((HERE / "environment-turntable-validation.json").read_text())
    cubemap = json.loads((HERE / "cubemap-r009/cubemap-contract.json").read_text())
    source_snapshot = helpers.snapshot_all()
    partitions = helpers.validate_partitions("gate09-audit-source")
    world = bpy.context.scene.world
    world_nodes = list(world.node_tree.nodes)
    environment_nodes = [node for node in world_nodes if node.type == "TEX_ENVIRONMENT"]
    target_pixels, target_spec = read_exr(TARGET)
    target_rgb = target_pixels[..., :3]
    face_checks = {}
    for face, record in cubemap["faces"].items():
        pixels, image_spec = read_exr(HERE / record["path"])
        face_checks[face] = {
            "sha256": sha256(HERE / record["path"]),
            "hashExact": sha256(HERE / record["path"]) == record["sha256"],
            "resolution": image_spec["resolution"],
            "nonzeroRgbFraction": float(np.mean(np.any(pixels[..., :3] > 0, axis=2))),
        }
    document = glb_json(GLB)
    sampler_clamp = bool(document.get("samplers")) and all(
        sampler.get("wrapS", 10497) == 33071
        and sampler.get("wrapT", 10497) == 33071
        for sampler in document["samplers"]
    )
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    imported = {
        obj.name: inspect_imported_object(obj)
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name in EXPECTED
    }
    checks = {
        "buildPassed": build["pass"],
        "turntablePassed": turntable["pass"],
        "sourceBlendHash": sha256(SOURCE) == build["output"]["blendSha256"],
        "sourceSnapshotLocked": build["checks"]["sourceSnapshotIdentical"]
        and bool(source_snapshot),
        "sourcePartitions": partitions["pass"],
        "worldEnvironmentOnly": len(environment_nodes) == 1
        and not any(obj.type == "LIGHT" for obj in bpy.data.objects),
        "worldUsesTarget": environment_nodes[0].image.filepath.endswith(TARGET.name),
        "worldStrength": any(
            node.type == "BACKGROUND"
            and abs(node.inputs["Strength"].default_value - 0.85) <= 1e-6
            for node in world_nodes
        ),
        "targetResolution": target_spec["resolution"] == [2048, 1024],
        "targetRgbNonzero": float(np.mean(np.any(target_rgb > 0, axis=2))) == 1.0,
        "targetSeam": float(np.max(np.abs(target_rgb[:, 0] - target_rgb[:, -1]))) <= 1e-6,
        "cubemapSixFaces": len(face_checks) == 6,
        "cubemapFaceHashes": all(item["hashExact"] for item in face_checks.values()),
        "cubemapFaceResolution": all(
            item["resolution"] == [512, 512] for item in face_checks.values()
        ),
        "cubemapRgbNonzero": all(
            item["nonzeroRgbFraction"] == 1.0 for item in face_checks.values()
        ),
        "cubemapOrientation": cubemap["brightestDirectionAngularErrorDegrees"] <= 1,
        "allImportedObjects": set(imported) == set(EXPECTED),
        "glbPartitions": imported and all(item["pass"] for item in imported.values()),
        "glbClampNoWrap": sampler_clamp,
        "glbNoAnimations": not document.get("animations"),
        "glbNoLights": "KHR_lights_punctual" not in document.get("extensionsUsed", []),
        "noEmission": all(
            builder.emission_strength(material) == 0
            for material in bpy.data.materials
            if material.name.startswith("M07R13_")
        ),
        "shippingUnityUnchanged": build["checks"]["shippingUnityUnchanged"],
    }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "sourceBlendSha256": sha256(SOURCE),
        "targetEnvironmentSha256": sha256(TARGET),
        "targetSpec": target_spec,
        "cubemapFaces": face_checks,
        "glb": {
            "sha256": sha256(GLB),
            "samplers": document.get("samplers", []),
            "importedObjects": imported,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "glbPartitions": checks["glbPartitions"],
        "targetRgbNonzero": checks["targetRgbNonzero"],
        "cubemapOrientation": checks["cubemapOrientation"],
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 Blender environment audit failed.")


if __name__ == "__main__":
    main()
