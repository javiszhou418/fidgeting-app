#!/usr/bin/env python3
"""Independently audit the saved Gate 06 geometry scene."""

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "blender-audit.json"
EXPECTED_CONTRACT = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
EXPECTED_GATE05 = "fc0676107d7d9846959a6495edd808e0ffe7dbb7e7625ba2dcc5c7a7287c4f7b"
EXPECTED_GEOMETRY = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]


def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def nonmanifold_edges(obj):
    counts = {tuple(sorted(edge.vertices)): 0 for edge in obj.data.edges}
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] = counts.get(edge, 0) + 1
    return sum(value != 2 for value in counts.values())


def main():
    scene = bpy.context.scene
    bottom = bpy.data.objects["BottomExterior"]
    top = bpy.data.objects["MovingTopBody"]
    top_plane_z = float(bottom["top_plane_z_mm"])
    top_vertex_z = [
        (bottom.matrix_world @ bottom.data.vertices[index].co).z
        for polygon in bottom.data.polygons if polygon.normal.z > 0.999999
        for index in polygon.vertices
    ]
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in (bottom, top)
        for corner in obj.bound_box
    ]
    bounds = [
        max(point.x for point in points) - min(point.x for point in points),
        max(point.y for point in points) - min(point.y for point in points),
        max(point.z for point in points) - min(point.z for point in points),
    ]
    carrier_names = [
        "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight",
        "BallCandidateLeft", "BallCandidateRight",
    ]
    carrier_max_z = max(
        max((bpy.data.objects[name].matrix_world @ Vector(corner)).z for corner in bpy.data.objects[name].bound_box)
        for name in carrier_names
    )
    manifold = {name: nonmanifold_edges(bpy.data.objects[name]) for name in CORE}
    invalid_normals = {
        name: sum(
            polygon.normal.length < 0.99 or not all(math.isfinite(value) for value in polygon.normal)
            for polygon in bpy.data.objects[name].data.polygons
        )
        for name in CORE
    }
    uv_layers = {name: len(bpy.data.objects[name].data.uv_layers) for name in CORE}
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    digest = geometry_digest()
    checks = {
        "gateAndRevision": scene["gate"] == "06-geometry" and scene["geometry_revision"] == 4,
        "contractHash": scene["mechanism_contract_sha256"] == EXPECTED_CONTRACT,
        "gate05Hash": scene["gate05_source_sha256"] == EXPECTED_GATE05,
        "geometryDigest": digest == EXPECTED_GEOMETRY == scene["canonical_geometry_digest"],
        "exactBounds": all(abs(value - expected) <= 1e-6 for value, expected in zip(bounds, [31, 50, 12])),
        "flatPlane": max(abs(value - top_plane_z) for value in top_vertex_z) <= 0.001,
        "noCavity": bottom["cavity"] is False and bottom["recess_depth_mm"] == 0.0,
        "axisBossPositive": bpy.data.objects["FixedAxisBoss"]["protrusion_mm"] > 0.0,
        "carrierHidden": carrier_max_z <= top_plane_z - 0.049,
        "fourGrooves": top["groove_count"] == 4,
        "grooveRoles": [
            bpy.data.objects[name]["role"] for name in (
                "TopOuterGrooveLeft", "TopInnerGrooveLeft",
                "TopInnerGrooveRight", "TopOuterGrooveRight",
            )
        ] == ["fore-aft-slide", "central-axis-link", "central-axis-link", "fore-aft-slide"],
        "manifold": all(value == 0 for value in manifold.values()),
        "normals": all(value == 0 for value in invalid_normals.values()),
        "uvs": all(value > 0 for value in uv_layers.values()),
        "hiddenUnknowns": bpy.data.objects["UnknownSprings"].hide_render
        and bpy.data.objects["UnknownPreload"].hide_render
        and bpy.data.objects["UnknownSprings"]["count"] == "unknown"
        and bpy.data.objects["UnknownPreload"]["value"] == "unknown",
        "zeroSelfMotion": not animated and scene["self_motion"] is False,
        "shippingUntouched": scene["shipping_unity_changed"] is False,
    }
    report = {
        "pass": all(checks.values()),
        "blenderVersion": bpy.app.version_string,
        "checks": checks,
        "geometryDigest": digest,
        "boundsMm": bounds,
        "topPlaneZMm": top_plane_z,
        "topPlaneMaximumDeviationMm": max(abs(value - top_plane_z) for value in top_vertex_z),
        "carrierClearanceBelowPlaneMm": top_plane_z - carrier_max_z,
        "nonmanifoldEdges": manifold,
        "invalidPolygonNormals": invalid_normals,
        "uvLayerCounts": uv_layers,
        "animatedObjects": animated,
        "objectCount": len(bpy.data.objects),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

