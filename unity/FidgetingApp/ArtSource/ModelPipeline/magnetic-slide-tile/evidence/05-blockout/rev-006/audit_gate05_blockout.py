#!/usr/bin/env python3
"""Audit the saved Gate 05 rev 6 Blender scene independently."""

import json
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "blender-audit.json"
TOLERANCE_MM = 0.001


def nonmanifold_edges(obj):
    mesh = obj.data
    counts = {tuple(sorted(edge.vertices)): 0 for edge in mesh.edges}
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] = counts.get(edge, 0) + 1
    return sum(count != 2 for count in counts.values())


def main():
    scene = bpy.context.scene
    expected_parents = {
        "BottomExterior": "MagneticSlideTile_G05_R006",
        "FixedAxisBoss": "BottomExterior",
        "FixedAxis": "FixedAxisBoss",
        "MinimumOverlapDisk": "BottomExterior",
        "RotatingCarrier": "FixedAxisBoss",
        "RotatingCarrierBody": "RotatingCarrier",
        "CarrierFollowerLeft": "RotatingCarrier",
        "CarrierFollowerRight": "RotatingCarrier",
        "BallCandidateLeft": "RotatingCarrier",
        "BallCandidateRight": "RotatingCarrier",
        "UnknownSprings": "RotatingCarrier",
        "UnknownPreload": "RotatingCarrier",
        "MovingTop": "MagneticSlideTile_G05_R006",
        "TopLocalSlide": "MovingTop",
        "MovingTopBody": "TopLocalSlide",
        "TopOuterGrooveLeft": "MovingTopBody",
        "TopInnerGrooveLeft": "MovingTopBody",
        "TopInnerGrooveRight": "MovingTopBody",
        "TopOuterGrooveRight": "MovingTopBody",
    }
    bottom = bpy.data.objects["BottomExterior"]
    top_plane_z = float(bottom["top_plane_z_mm"])
    top_polygons = [polygon for polygon in bottom.data.polygons if polygon.normal.z > 0.999999]
    top_vertex_z = [
        (bottom.matrix_world @ bottom.data.vertices[index].co).z
        for polygon in top_polygons
        for index in polygon.vertices
    ]
    carrier_names = [
        "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight",
        "BallCandidateLeft", "BallCandidateRight",
    ]
    carrier_max_z = max(
        max((bpy.data.objects[name].matrix_world @ Vector(corner)).z for corner in bpy.data.objects[name].bound_box)
        for name in carrier_names
    )
    manifold_names = [
        "BottomExterior", "MovingTopBody", "FixedAxisBoss", "RotatingCarrierBody",
        "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
    ]
    nonmanifold = {name: nonmanifold_edges(bpy.data.objects[name]) for name in manifold_names}
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    checks = {
        "revision": scene["revision"] == 6,
        "contractHash": scene["mechanism_contract_sha256"] == "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
        "flatSurfaceDeclaration": scene["bottom_top_surface"] == "continuous-flat-plane",
        "hierarchy": all(bpy.data.objects[name].parent.name == parent for name, parent in expected_parents.items()),
        "flatTopVertices": min(top_vertex_z) >= top_plane_z - TOLERANCE_MM
        and max(top_vertex_z) <= top_plane_z + TOLERANCE_MM,
        "noBottomModifiers": not list(bottom.modifiers),
        "noRecessDepth": bottom["recess_depth_mm"] == 0.0,
        "noCavity": bottom["cavity"] is False and "_BottomExteriorUpperRim" not in bpy.data.objects,
        "raisedAxis": bpy.data.objects["FixedAxisBoss"]["protrusion_mm"] > 0,
        "carrierHidden": carrier_max_z <= top_plane_z - 0.049,
        "fourGrooves": bpy.data.objects["MovingTopBody"]["groove_count"] == 4,
        "unknownsRemainUnknown": bpy.data.objects["UnknownSprings"]["count"] == "unknown"
        and bpy.data.objects["UnknownPreload"]["value"] == "unknown",
        "manifold": all(value == 0 for value in nonmanifold.values()),
        "zeroAnimation": not animated and scene.frame_start == scene.frame_end == 1,
        "zeroSelfMotion": scene["self_motion"] is False,
        "shippingUntouched": scene["shipping_unity_changed"] is False,
    }
    report = {
        "pass": all(checks.values()),
        "blenderVersion": bpy.app.version_string,
        "checks": checks,
        "topPlaneZMm": top_plane_z,
        "topVertexRangeMm": [min(top_vertex_z), max(top_vertex_z)],
        "topVertexCount": len(top_vertex_z),
        "carrierMaximumZMm": carrier_max_z,
        "carrierClearanceBelowPlaneMm": top_plane_z - carrier_max_z,
        "nonmanifoldEdges": nonmanifold,
        "animatedObjects": animated,
        "objectCount": len(bpy.data.objects),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

