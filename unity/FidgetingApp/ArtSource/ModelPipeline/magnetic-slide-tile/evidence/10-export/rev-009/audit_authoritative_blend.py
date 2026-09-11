#!/usr/bin/env python3
"""Audit the immutable Gate 10 authoritative Blend."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
EXPECTED_FILE = PACKAGE / "magnetic-slide-tile-authoritative-r009.blend"
CORE = ["BottomExterior", "FixedAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight", "MovingTopBody"]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        evaluated = bpy.data.objects[name].evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode()); digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode()); digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def z_extents(name):
    obj = bpy.data.objects[name]
    values = [(obj.matrix_world @ vertex.co).z for vertex in obj.data.vertices]
    return min(values), max(values)


def sharp_edge_count(name):
    attribute = bpy.data.objects[name].data.attributes.get("sharp_edge")
    return sum(1 for value in attribute.data if value.value) if attribute else 0


def main():
    root = bpy.data.objects["MagneticSlideTile_G05_R006"]
    world_nodes = {node.type for node in bpy.context.scene.world.node_tree.nodes}
    approved_materials = [material for material in bpy.data.materials if material.name.startswith("M07R11_")]
    checks = {
        "savedFile": Path(bpy.data.filepath).resolve() == EXPECTED_FILE.resolve(),
        "geometryDigest": geometry_digest() == "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
        "geometryMetadata": root["canonicalGeometryDigest"] == "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
        "materialMetadata": root["approvedMaterialDigest"] == "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8",
        "contractMetadata": root["mechanismContractSha256"] == "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
        "portabilityMetadata": root["unityPortabilityContractSha256"] == "fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134",
        "closedZeroMotion": root["defaultPose"] == "closed-zero-motion" and not root["selfMotion"] and root["animationClips"] == 0,
        "noAnimations": not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
        "eightRenderMeshes": all(bpy.data.objects[name].type == "MESH" for name in CORE),
        "fourGrooveMetadata": all(bpy.data.objects.get(name) for name in ["TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"]),
        "flatBottom": abs(z_extents("BottomExterior")[1] - 5.875) <= 0.001 and not bpy.data.objects.get("_BottomExteriorUpperRim"),
        "raisedAxisBoss": abs(z_extents("FixedAxisBoss")[1] - 6.075) <= 0.001,
        "smoothSidesHardCaps": all(
            any(polygon.use_smooth and abs(polygon.normal.z) < 0.995 for polygon in bpy.data.objects[name].data.polygons)
            and any(not polygon.use_smooth and abs(polygon.normal.z) >= 0.9999 for polygon in bpy.data.objects[name].data.polygons)
            for name in ["BottomExterior", "MovingTopBody"]
        ),
        "validNormals": all(all(0.99 <= vertex.normal.length <= 1.01 for vertex in bpy.data.objects[name].data.vertices) for name in CORE),
        "uvs": all(len(bpy.data.objects[name].data.uv_layers) >= 1 for name in CORE),
        "zeroEmission": all(float(material.get("emissionStrength", 0.0)) == 0.0 for material in approved_materials),
        "portableWorld": world_nodes == {"TEX_ENVIRONMENT", "BACKGROUND", "OUTPUT_WORLD"},
        "noReflectionBand": not any("reflectedBand" in node.name or "softPanel" in node.name for material in approved_materials if material.use_nodes for node in material.node_tree.nodes),
        "singleRenderModel": root["lodPolicy"].startswith("single approved render model"),
        "noCollisionInBlend": not any(obj.name.startswith("COL_") for obj in bpy.data.objects),
    }
    report = {
        "schemaVersion": 1, "gate": "10-export", "revision": 9,
        "blenderVersion": bpy.app.version_string, "blendSha256": sha256(EXPECTED_FILE),
        "checks": checks, "pass": all(checks.values()),
    }
    (HERE / "authoritative-blend-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

