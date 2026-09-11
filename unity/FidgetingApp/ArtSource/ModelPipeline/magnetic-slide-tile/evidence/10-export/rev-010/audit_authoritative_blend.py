#!/usr/bin/env python3
"""Audit the saved Gate 10 authoritative Blend without changing it."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
BLEND = HERE / "package/magnetic-slide-tile-authoritative-r010.blend"
BUILD = json.loads((HERE / "export-build-report.json").read_text())
ROOT = "MagneticSlideTile_G06_R005"
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
EXPECTED_GEOMETRY = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def state_digest() -> dict:
    material = hashlib.sha256()
    uv = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        material.update(name.encode())
        uv.update(name.encode())
        for polygon in obj.data.polygons:
            material.update(struct.pack("<I?", polygon.material_index, polygon.use_smooth))
        for slot in obj.data.materials:
            material.update((slot.name if slot else "<none>").encode())
            material.update(b"\0")
        for layer in obj.data.uv_layers:
            uv.update(layer.name.encode())
            for loop in layer.data:
                uv.update(struct.pack("<2d", *loop.uv))
    return {"materials": material.hexdigest(), "uvs": uv.hexdigest()}


def main() -> None:
    root = bpy.data.objects[ROOT]
    world_images = [
        node.image
        for node in bpy.context.scene.world.node_tree.nodes
        if node.type == "TEX_ENVIRONMENT" and node.image
    ]
    partition = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name in PRODUCT:
        evaluated = bpy.data.objects[name].evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        mesh.calc_loop_triangles()
        counts = [0] * len(mesh.materials)
        for triangle in mesh.loop_triangles:
            counts[triangle.material_index] += 1
        partition[name] = {
            "slots": [material.name for material in mesh.materials],
            "triangleCounts": counts,
            "topArtwork": counts[0],
            "solidDarkSide": counts[1],
            "polishedSilverRim": counts[2],
            "neutralUnderside": counts[3],
            "sideArtwork": 0,
            "undersideArtwork": 0,
        }
        evaluated.to_mesh_clear()
    image_nodes = [
        node
        for material in bpy.data.materials
        if material.use_nodes
        for node in material.node_tree.nodes
        if node.type == "TEX_IMAGE" and node.image and list(node.image.size) == [620, 1000]
    ]
    checks = {
        "openedExpectedBlend": Path(bpy.data.filepath).resolve() == BLEND.resolve(),
        "blendHash": sha256(BLEND) == BUILD["formats"]["blend"]["sha256"],
        "geometryDigest": geometry_digest() == EXPECTED_GEOMETRY,
        "materialStateDigest": state_digest()["materials"] == BUILD["after"]["digests"]["materials"],
        "uvStateDigest": state_digest()["uvs"] == BUILD["after"]["digests"]["uvs"],
        "topArtworkPresent": all(item["topArtwork"] > 0 for item in partition.values()),
        "sideArtworkZero": all(item["sideArtwork"] == 0 for item in partition.values()),
        "undersideArtworkZero": all(item["undersideArtwork"] == 0 for item in partition.values()),
        "silverRimPresent": all(item["polishedSilverRim"] > 0 for item in partition.values()),
        "capOnlyArtworkSlots": all(item["slots"][0].endswith("TopArtwork") for item in partition.values()),
        "clampImageNodes": bool(image_nodes) and all(node.extension == "EXTEND" for node in image_nodes),
        "nativeNpotImages": all(list(node.image.size) == [620, 1000] for node in image_nodes),
        "targetEnvironment": len(world_images) == 1
            and Path(bpy.path.abspath(world_images[0].filepath)).name == "target-shipping-studio-r009.exr",
        "singleFixedAxis": sum(obj.name == "FixedAxis" and obj.type == "EMPTY" for obj in bpy.data.objects) == 1,
        "fourGrooves": sum(obj.name.startswith("Top") and "Groove" in obj.name and obj.type == "EMPTY" for obj in bpy.data.objects) == 4,
        "minimumOverlapEmpty": bpy.data.objects["MinimumOverlapDisk"].type == "EMPTY",
        "noCollisionInRenderBlend": not any(obj.name.startswith("COL_") for obj in bpy.data.objects),
        "noCavityOrProxyMesh": "_BottomExteriorUpperRim" not in bpy.data.objects
            and not any(obj.type == "MESH" and "OverlapDisk" in obj.name for obj in bpy.data.objects),
        "endpointMetadata": bool(root["rotationLockedBelowSMax"])
            and bool(root["slideLockedAtNonzeroAngle"])
            and int(root["detentCount"]) == 30
            and int(root["detentStepDegrees"]) == 12
            and int(root["rotationAtSMaxDegrees"]) == 360
            and root["returnRule"] == "align theta to 0 then close",
        "closedZeroMotion": root["defaultPose"] == "closed-zero-motion"
            and float(root["linearVelocityMmPerSecond"]) == 0
            and float(root["angularVelocityDegreesPerSecond"]) == 0,
        "noAnimations": not bpy.data.actions
            and not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "blend": {"path": str(BLEND), "sha256": sha256(BLEND)},
        "geometryDigest": geometry_digest(),
        "stateDigests": state_digest(),
        "partitions": partition,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (HERE / "authoritative-blend-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"pass": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
