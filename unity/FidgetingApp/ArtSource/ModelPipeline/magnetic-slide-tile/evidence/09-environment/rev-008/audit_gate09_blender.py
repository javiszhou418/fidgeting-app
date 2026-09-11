#!/usr/bin/env python3
"""Independently audit the saved Gate 09 Blender environment scene."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
REPORT = json.loads((HERE / "environment-validation.json").read_text(encoding="utf-8"))
PORTABILITY = json.loads((HERE / "portability-validation.json").read_text(encoding="utf-8"))
EXPECTED_CONTRACT = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_glb(path):
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError("Invalid GLB header.")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RuntimeError("Missing GLB JSON chunk.")
    return json.loads(data[20:20 + chunk_length].decode("utf-8"))


def main():
    scene = bpy.context.scene
    world = scene.world
    environment_nodes = [node for node in world.node_tree.nodes if node.type == "TEX_ENVIRONMENT"]
    procedural_world_nodes = [
        node.name for node in world.node_tree.nodes
        if node.type not in {"TEX_ENVIRONMENT", "BACKGROUND", "OUTPUT_WORLD"}
    ]
    environment_node = environment_nodes[0] if len(environment_nodes) == 1 else None
    hdri = environment_node.image if environment_node else None
    hdri_path = Path(bpy.path.abspath(hdri.filepath)) if hdri else None
    pixels = list(hdri.pixels[:]) if hdri else []
    seam_delta = 999.0
    if hdri and pixels:
        width, height = hdri.size
        seam_delta = 0.0
        for row in range(height):
            first = (row * width) * 4
            last = (row * width + width - 1) * 4
            seam_delta = max(
                seam_delta,
                *(abs(float(pixels[first + channel]) - float(pixels[last + channel])) for channel in range(3)),
            )
    gltf = parse_glb(HERE / "magnetic-slide-tile-environment-r008-lookdev.glb")
    material_names = {material.get("name") for material in gltf.get("materials", [])}
    expected_materials = {
        "M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct",
        "M07R11_PolishedSilver", "M07R11_InternalSilverReference",
        "M07R11_DarkExteriorSide", "M07R11_NeutralTechnical",
        "M07R11_BallCandidate_UnknownMaterial",
    }
    checks = {
        "savedBlend": Path(bpy.data.filepath).name == "magnetic-slide-tile-environment-r008.blend",
        "sceneGate": scene.get("gate") == "09-environment" and scene.get("environment_revision") == 8,
        "sourceHashLocked": scene.get("gate08_source_sha256") == "547055f5c04890575fab4b43e2287a62086ee7b4ee2b0e22fa3f92f0ea2e21b1",
        "contractHashLocked": scene.get("mechanism_contract_sha256") == EXPECTED_CONTRACT,
        "geometryDigestLocked": scene.get("canonical_geometry_digest") == REPORT["geometry"]["expected"],
        "materialDigestLocked": scene.get("approved_material_digest") == REPORT["materials"]["approvedSemanticDigest"],
        "lightDigestLocked": scene.get("approved_light_digest") == REPORT["lighting"]["after"],
        "cameraDigestLocked": scene.get("approved_camera_digest") == REPORT["cameras"]["after"],
        "portableWorldOnly": len(environment_nodes) == 1 and not procedural_world_nodes,
        "portableProjection": environment_node is not None and environment_node.projection == "EQUIRECTANGULAR",
        "portableHdriExternal": hdri_path == (HERE / REPORT["environment"]["targetShipping"]["hdri"]),
        "portableHdriHash": hdri_path is not None and sha256(hdri_path) == REPORT["hdriMetadata"]["sha256"],
        "portableHdriResolution": hdri is not None and list(hdri.size) == [2048, 1024],
        "portableHdriSeam": seam_delta <= 1e-6,
        "portableHdriLinearInterpretation": hdri is not None and hdri.colorspace_settings.name == "Non-Color",
        "worldStrength": math.isclose(float(world["strength"]), 0.65, abs_tol=1e-9),
        "groundMaterial": bpy.data.objects["M08R2_NeutralGround"].active_material.name == "M09R8_PortableGround",
        "groundValues": list(bpy.data.materials["M09R8_PortableGround"]["baseColorLinear"]) == [0.018, 0.016, 0.017, 1]
        and bpy.data.materials["M09R8_PortableGround"]["roughness"] == 0.42,
        "fixedAxisObjectMatrix": [
            round(float(bpy.data.objects["FixedAxis"].matrix_world[row][column]), 9)
            for row in range(4) for column in range(4)
        ] == [
            value for row in REPORT["hierarchy"]["after"]["FixedAxis"]["matrixWorld"] for value in row
        ],
        "hierarchy": all(
            (bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None) == values["parent"]
            for name, values in REPORT["hierarchy"]["after"].items()
        ),
        "noAnimation": not any(
            obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
            for obj in bpy.data.objects
        ),
        "zeroEmission": REPORT["checks"]["approvedEmissionZero"],
        "glbMeshes": len(gltf.get("meshes", [])) == 8,
        "glbMaterials": expected_materials.issubset(material_names),
        "glbTexturesEmbedded": len(gltf.get("images", [])) == 4 and len(gltf.get("textures", [])) == 4,
        "glbNoAnimations": not gltf.get("animations"),
        "portabilityContractHash": PORTABILITY["pass"] and sha256(HERE / "unity-portability-contract.json") == PORTABILITY["contractSha256"],
        "unityUntouched": scene.get("unity_import_applied") is False and scene.get("shipping_unity_changed") is False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "blenderVersion": bpy.app.version_string,
        "pass": all(checks.values()),
        "checks": checks,
        "worldNodeTypes": [node.type for node in world.node_tree.nodes],
        "proceduralWorldNodes": procedural_world_nodes,
        "hdri": {
            "path": str(hdri_path) if hdri_path else None,
            "sha256": sha256(hdri_path) if hdri_path else None,
            "resolutionPx": list(hdri.size) if hdri else None,
            "seamMaxAbsoluteLinearDelta": seam_delta,
            "colorspace": hdri.colorspace_settings.name if hdri else None,
        },
        "glb": {
            "meshCount": len(gltf.get("meshes", [])),
            "materialNames": sorted(material_names),
            "imageCount": len(gltf.get("images", [])),
            "animationCount": len(gltf.get("animations", [])),
        },
    }
    (HERE / "blender-environment-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

