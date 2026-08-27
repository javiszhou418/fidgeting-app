"""Round-trip the Gate 10 FBX, GLB, and collision exports in Blender."""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
FBX = HERE / "magnetic-fan-card.fbx"
GLB = HERE / "magnetic-fan-card.glb"
COLLISION_FBX = HERE / "magnetic-fan-card-collision.fbx"
REPORT = HERE / "export-roundtrip-report.json"
ROOT = "MagneticFanCard_Root"
CARDS = ("BottomCard", "MiddleCard", "TopCard")


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def world_bounds(objects: list[bpy.types.Object]) -> dict:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    extent = maximum - minimum
    return {
        "minimum": [round(value, 7) for value in minimum],
        "maximum": [round(value, 7) for value in maximum],
        "extent": [round(value, 7) for value in extent],
    }


def mesh_stats(objects: list[bpy.types.Object]) -> dict:
    meshes = [obj for obj in objects if obj.type == "MESH"]
    return {
        "meshObjects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "triangles": sum(
            len(polygon.vertices) - 2
            for obj in meshes
            for polygon in obj.data.polygons
        ),
        "materials": sorted({
            material.name
            for obj in meshes
            for material in obj.data.materials
            if material is not None
        }),
    }


def validate_product(format_name: str, path: Path) -> dict:
    reset()
    if format_name == "FBX":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        bpy.ops.import_scene.gltf(filepath=str(path))
    objects = list(bpy.context.scene.objects)
    by_name = {obj.name: obj for obj in objects}
    required = {
        ROOT,
        *CARDS,
        "CommonAxis_RecessedMatteSpindle",
        "CommonAxis_BearingCap_Chrome",
        "BottomCard_Rank_0",
        "BottomCard_Rank_1",
        "MiddleCard_Rank_0",
        "MiddleCard_Rank_1",
        "TopCard_Rank_0",
        "TopCard_Rank_1",
        "MiddleCard_Track_Undercut",
        "TopCard_Track_Undercut",
    }
    missing = sorted(required - set(by_name))
    hierarchy = {
        card: by_name[card].parent.name if card in by_name
        and by_name[card].parent else None
        for card in CARDS
    }
    rank_types = {
        name: by_name[name].type
        for name in required
        if "_Rank_" in name and name in by_name
    }
    bottom_tracks = [
        obj.name for obj in objects
        if obj.name.startswith("BottomCard_Track_")
    ]
    middle_top_tracks = [
        obj.name for obj in objects
        if (
            obj.name.startswith("MiddleCard_Track_")
            or obj.name.startswith("TopCard_Track_")
        )
    ]
    stats = mesh_stats(objects)
    checks = {
        "requiredNames": not missing,
        "cardParenting": all(parent == ROOT for parent in hierarchy.values()),
        "rankMeshes": len(rank_types) == 6
        and all(value == "MESH" for value in rank_types.values()),
        "bottomHasNoTrack": len(bottom_tracks) == 0,
        "topMiddleTrackObjects": len(middle_top_tracks) == 4,
        "triangleBudget": stats["triangles"] <= 50_000,
        "noCollisionInProduct": not any(
            obj.name.startswith("COLLIDER_") for obj in objects),
    }
    return {
        "format": format_name,
        "path": path.name,
        "objects": len(objects),
        "missingRequiredNames": missing,
        "hierarchy": hierarchy,
        "rankTypes": rank_types,
        "bottomTracks": bottom_tracks,
        "middleTopTracks": middle_top_tracks,
        "stats": stats,
        "bounds": world_bounds(objects),
        "checks": checks,
        "pass": all(checks.values()),
    }


def edge_face_counts(obj: bpy.types.Object) -> Counter:
    counts = Counter()
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] += 1
    return counts


def validate_collision(path: Path) -> dict:
    reset()
    bpy.ops.import_scene.fbx(filepath=str(path))
    objects = list(bpy.context.scene.objects)
    by_name = {obj.name: obj for obj in objects}
    expected = [f"COLLIDER_{card}" for card in CARDS]
    colliders = [by_name[name] for name in expected if name in by_name]
    watertight = {}
    for collider in colliders:
        counts = edge_face_counts(collider)
        watertight[collider.name] = bool(counts) and all(
            count == 2 for count in counts.values())
    parenting = {
        collider.name: collider.parent.name if collider.parent else None
        for collider in colliders
    }
    checks = {
        "threeColliders": len(colliders) == 3,
        "watertight": len(watertight) == 3 and all(watertight.values()),
        "parenting": all(
            parenting.get(f"COLLIDER_{card}") == card for card in CARDS),
        "renderMeshesAbsent": not any(
            "_WarmSilverFace" in obj.name
            or "_GunmetalFrame" in obj.name
            for obj in objects),
    }
    return {
        "format": "FBX collision",
        "path": path.name,
        "objects": len(objects),
        "colliders": expected,
        "watertight": watertight,
        "parenting": parenting,
        "bounds": world_bounds(colliders),
        "checks": checks,
        "pass": all(checks.values()),
    }


def relative_error(a: float, b: float) -> float:
    denominator = max(abs(a), abs(b), 1e-9)
    return abs(a - b) / denominator


def main() -> None:
    fbx = validate_product("FBX", FBX)
    glb = validate_product("GLB", GLB)
    collision = validate_collision(COLLISION_FBX)
    fbx_extent = sorted(fbx["bounds"]["extent"])
    glb_extent = sorted(glb["bounds"]["extent"])
    parity_errors = [
        relative_error(a, b) for a, b in zip(fbx_extent, glb_extent)
    ]
    cross_format = {
        "sortedExtentRelativeErrors": [
            round(value, 7) for value in parity_errors
        ],
        "boundsWithinOnePercent": max(parity_errors) <= 0.01,
        "triangleDifference": abs(
            fbx["stats"]["triangles"] - glb["stats"]["triangles"]),
        "triangleCountsWithinOnePercent": (
            relative_error(
                fbx["stats"]["triangles"],
                glb["stats"]["triangles"],
            ) <= 0.01
        ),
    }
    report = {
        "fbx": fbx,
        "glb": glb,
        "collisionFbx": collision,
        "crossFormat": cross_format,
        "pass": (
            fbx["pass"]
            and glb["pass"]
            and collision["pass"]
            and cross_format["boundsWithinOnePercent"]
            and cross_format["triangleCountsWithinOnePercent"]
        ),
    }
    REPORT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
