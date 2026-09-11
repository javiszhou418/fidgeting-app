#!/usr/bin/env python3
"""Independently audit the saved Gate 06 rev 5 Blender geometry."""

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REPORT = HERE / "blender-audit.json"
EXPECTED_CONTRACT = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
EXPECTED_SOURCE = "f587be803cf98e134f173e961fe4e096708f08916af51d971b0ef381d51c11a2"
EXPECTED_GEOMETRY = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
PIVOT = Vector((0.0, -9.0, 5.875))
CORE = {
    "BottomExterior", "MovingTopBody", "InternalAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
}
INTERNAL = CORE - {"BottomExterior", "MovingTopBody"}


def fingerprint():
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def nonmanifold_edges(obj):
    counts = {tuple(sorted(edge.vertices)): 0 for edge in obj.data.edges}
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] = counts.get(edge, 0) + 1
    return sum(value != 2 for value in counts.values())


scene = bpy.context.scene
root = bpy.data.objects["MagneticSlideTile_G06_R005"]
bottom = bpy.data.objects["BottomExterior"]
top = bpy.data.objects["MovingTopBody"]
fixed = bpy.data.objects["FixedAxis"]
plane_z = [
    (bottom.matrix_world @ bottom.data.vertices[index].co).z
    for polygon in bottom.data.polygons if polygon.normal.z > 0.999999
    for index in polygon.vertices
]
points = [obj.matrix_world @ Vector(corner) for obj in (bottom, top) for corner in obj.bound_box]
bounds = [
    max(point.x for point in points) - min(point.x for point in points),
    max(point.y for point in points) - min(point.y for point in points),
    max(point.z for point in points) - min(point.z for point in points),
]
manifold = {name: nonmanifold_edges(bpy.data.objects[name]) for name in sorted(CORE)}
invalid_normals = {
    name: sum(
        polygon.normal.length < 0.99 or not all(math.isfinite(value) for value in polygon.normal)
        for polygon in bpy.data.objects[name].data.polygons
    )
    for name in sorted(CORE)
}
pivot_objects = [obj.name for obj in bpy.data.objects if obj.get("pivot_id")]
checks = {
    "gateAndRevision": scene["gate"] == "06-geometry" and scene["geometry_revision"] == 5,
    "contractHash": scene["mechanism_contract_sha256"] == EXPECTED_CONTRACT
    and root["mechanism_contract_sha256"] == EXPECTED_CONTRACT,
    "gate05SourceHash": scene["gate05_source_sha256"] == EXPECTED_SOURCE,
    "geometryDigest": fingerprint() == EXPECTED_GEOMETRY == scene["canonical_geometry_digest"],
    "exactBounds": all(abs(actual - expected) <= 1e-6 for actual, expected in zip(bounds, [31.0, 50.0, 12.0])),
    "flatBottomPlane": max(plane_z) - min(plane_z) <= 0.001,
    "singleFixedAxis": pivot_objects == ["FixedAxis"] and (fixed.matrix_world.translation - PIVOT).length <= 1e-12,
    "endpointInterlockMetadata": "0<=s<sMax:theta=0" in root["endpoint_interlock"]
    and root["prohibited_pose"] == "mid-slide rotation",
    "productWhitelist": list(scene["product_renderer_whitelist"]) == ["BottomExterior", "MovingTopBody"],
    "minimumDiskMetadataOnly": bpy.data.objects["MinimumOverlapDisk"].type == "EMPTY"
    and bpy.data.objects["MinimumOverlapDisk"].hide_render,
    "internalTechnicalOnly": all(bpy.data.objects[name].get("product_render") is False for name in INTERNAL),
    "fourGrooves": top["groove_count"] == 4,
    "manifold": all(value == 0 for value in manifold.values()),
    "normals": all(value == 0 for value in invalid_normals.values()),
    "uvs": all(len(bpy.data.objects[name].data.uv_layers) > 0 for name in CORE),
    "zeroSelfMotion": not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
    "noFinalMaterials": scene["final_materials_applied"] is False,
    "noSimulatorOrUnity": scene["simulator_used"] is False and scene["shipping_unity_changed"] is False,
}
report = {
    "schemaVersion": 1,
    "pass": all(checks.values()),
    "blenderVersion": bpy.app.version_string,
    "checks": checks,
    "contractSha256": EXPECTED_CONTRACT,
    "gate05SourceSha256": EXPECTED_SOURCE,
    "geometryDigest": fingerprint(),
    "boundsMm": bounds,
    "bottomTopPlaneMaximumDeviationMm": max(plane_z) - min(plane_z),
    "fixedPivotMm": list(fixed.matrix_world.translation),
    "pivotObjects": pivot_objects,
    "nonmanifoldEdges": manifold,
    "invalidPolygonNormals": invalid_normals,
    "objectCount": len(bpy.data.objects),
}
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
