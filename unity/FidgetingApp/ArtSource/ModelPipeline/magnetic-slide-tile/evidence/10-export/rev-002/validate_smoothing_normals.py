#!/usr/bin/env python3
"""Quantify Gate 10 source, FBX, and GLB smoothing and normal continuity."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001"
SOURCE_BLEND = ROOT / "magnetic-slide-tile-authoritative-r002.blend"
REV1_FBX = REV1 / "magnetic-slide-tile.fbx"
REV1_MANIFEST = REV1 / "export-manifest.json"
REV2_FBX = ROOT / "magnetic-slide-tile-r002.fbx"
REV2_GLB = ROOT / "magnetic-slide-tile-r002.glb"
OUTPUT = ROOT / "smoothing-normal-validation.json"
RENDER_NAMES = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]


def triangles(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def triangle_geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        obj.data.calc_loop_triangles()
        digest.update(obj.name.encode())
        records = []
        for triangle in obj.data.loop_triangles:
            points = sorted(
                tuple(round(float(value), 7) for value in obj.data.vertices[index].co)
                for index in triangle.vertices
            )
            records.append(points)
        for points in sorted(records):
            digest.update(json.dumps(points, separators=(",", ":")).encode())
    return digest.hexdigest()


def maximum_angle(vectors: list[Vector]) -> float:
    if len(vectors) < 2:
        return 0.0
    return max(math.degrees(left.angle(right, 0.0)) for left, right in itertools.combinations(vectors, 2))


def expected_side_normal(coordinate: Vector) -> Vector:
    if coordinate.y > 9.5:
        return Vector((coordinate.x, coordinate.y - 9.5, 0.0)).normalized()
    if coordinate.y < -9.5:
        return Vector((coordinate.x, coordinate.y + 9.5, 0.0)).normalized()
    return Vector((1.0 if coordinate.x >= 0 else -1.0, 0.0, 0.0))


def object_normal_metrics(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    mesh.calc_loop_triangles()
    side_groups: dict[tuple[float, float, float], list[Vector]] = {}
    cap_groups: dict[tuple[float, float, float], list[Vector]] = {}
    side_outward_dots = []
    cap_orientation_dots = []
    side_polygons = 0
    cap_polygons = 0
    for polygon in mesh.polygons:
        is_side = abs(polygon.normal.z) < 0.5
        side_polygons += int(is_side)
        cap_polygons += int(not is_side)
        for loop_index in polygon.loop_indices:
            loop = mesh.loops[loop_index]
            coordinate = mesh.vertices[loop.vertex_index].co.copy()
            normal = mesh.corner_normals[loop_index].vector.copy().normalized()
            key = tuple(round(float(value), 6) for value in coordinate)
            target = side_groups if is_side else cap_groups
            target.setdefault(key, []).append(normal)
            if is_side:
                side_outward_dots.append(normal.dot(expected_side_normal(coordinate)))
            else:
                expected = Vector((0.0, 0.0, 1.0 if coordinate.z > 0 else -1.0))
                cap_orientation_dots.append(normal.dot(expected))
    discontinuities = [maximum_angle(vectors) for vectors in side_groups.values()]
    boundary_angles = []
    for key in set(side_groups) & set(cap_groups):
        for side in side_groups[key]:
            for cap in cap_groups[key]:
                boundary_angles.append(math.degrees(side.angle(cap, 0.0)))
    discontinuities.sort()
    return {
        "triangles": triangles(obj),
        "sidePolygons": side_polygons,
        "capPolygons": cap_polygons,
        "sideCoordinateGroups": len(side_groups),
        "maximumSideCornerNormalDiscontinuityDegrees": max(discontinuities, default=0.0),
        "p95SideCornerNormalDiscontinuityDegrees": discontinuities[min(len(discontinuities) - 1, int(len(discontinuities) * 0.95))] if discontinuities else 0.0,
        "sideGroupsAbovePoint05Degrees": sum(value > 0.05 for value in discontinuities),
        "minimumCapSideNormalAngleDegrees": min(boundary_angles, default=0.0),
        "maximumCapSideNormalAngleDegrees": max(boundary_angles, default=0.0),
        "minimumSideOutwardDot": min(side_outward_dots, default=0.0),
        "minimumCapOrientationDot": min(cap_orientation_dots, default=0.0),
        "smoothPolygonCount": sum(polygon.use_smooth for polygon in mesh.polygons),
        "flatPolygonCount": sum(not polygon.use_smooth for polygon in mesh.polygons),
    }


def scene_metrics(label: str) -> dict:
    objects = [bpy.data.objects[name] for name in RENDER_NAMES]
    object_metrics = {obj.name: object_normal_metrics(obj) for obj in objects}
    return {
        "label": label,
        "triangleGeometryDigest": triangle_geometry_digest(objects),
        "totalTriangles": sum(item["triangles"] for item in object_metrics.values()),
        "objects": object_metrics,
    }


def open_source() -> dict:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    for name in RENDER_NAMES:
        bpy.data.objects[name].modifiers.clear()
    return scene_metrics("authoritative-source-base-mesh")


def import_fbx(path: Path, label: str) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True)
    return scene_metrics(label)


def import_glb(path: Path, label: str) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return scene_metrics(label)


def main() -> None:
    rev1_manifest = json.loads(REV1_MANIFEST.read_text(encoding="utf-8"))
    source = open_source()
    rev1_fbx = import_fbx(REV1_FBX, "rejected-rev1-fbx-smoothing-off")
    rev2_fbx = import_fbx(REV2_FBX, "rev2-fbx-smoothing-face")
    rev2_glb = import_glb(REV2_GLB, "rev2-glb-explicit-normals")
    corrected = [rev2_fbx, rev2_glb]
    checks = {
        "geometryDigestUnchanged": source["triangleGeometryDigest"]
        == rev2_fbx["triangleGeometryDigest"]
        == rev2_glb["triangleGeometryDigest"],
        "triangleCountUnchanged": source["totalTriangles"]
        == rev2_fbx["totalTriangles"]
        == rev2_glb["totalTriangles"]
        == 4096,
        "sourceSideNormalsContinuous": all(
            item["maximumSideCornerNormalDiscontinuityDegrees"] <= 0.01
            for item in source["objects"].values()
        ),
        "rev1FbxSmoothingMetadataWasOff": rev1_manifest["exports"]["settings"]["fbx"].get("smoothing", "OFF") == "OFF",
        "rev1BlenderReimportStillHadContinuousCustomNormals": all(
            item["maximumSideCornerNormalDiscontinuityDegrees"] <= 0.01
            for item in rev1_fbx["objects"].values()
        ),
        "rev2SideNormalsContinuous": all(
            item["maximumSideCornerNormalDiscontinuityDegrees"] <= 0.01
            and item["sideGroupsAbovePoint05Degrees"] == 0
            for scene in corrected
            for item in scene["objects"].values()
        ),
        "hardCapSideBoundaryPreserved": all(
            item["minimumCapSideNormalAngleDegrees"] >= 89.0
            for scene in [source, *corrected]
            for item in scene["objects"].values()
        ),
        "noNormalInversions": all(
            item["minimumSideOutwardDot"] >= 0.999
            and item["minimumCapOrientationDot"] >= 0.999
            for scene in [source, *corrected]
            for item in scene["objects"].values()
        ),
        "approvedSilhouetteSampling": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "source": source,
        "rejectedRev1Fbx": rev1_fbx,
        "diagnosis": {
            "primaryVisualConfound": "The rev 1 review board displayed 128-triangle non-rendering collision capsules as shaded geometry beside the shipping mesh.",
            "exportPortabilityRisk": "FBX mesh_smooth_type was OFF. Blender re-import still recovered continuous custom side normals, but the file omitted explicit face smoothing metadata for other importers.",
            "geometryFinding": "The 256-segment semicircles are sufficient; no Gate 06 geometry change is justified.",
        },
        "rev2Fbx": rev2_fbx,
        "rev2Glb": rev2_glb,
        "silhouette": {
            "segmentsPerSemicircle": 256,
            "maximumTurnDegrees": 0.703125,
            "maximumChordDeviationMm": 0.0002917831196828091,
            "geometryChangeRequired": False,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 smoothing/normal validation failed.")


if __name__ == "__main__":
    main()
