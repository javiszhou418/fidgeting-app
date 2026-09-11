#!/usr/bin/env python3
"""Independently re-import Gate 10 FBX, GLB and collision exports."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
FBX = PACKAGE / "magnetic-slide-tile-render-r009.fbx"
GLB = PACKAGE / "magnetic-slide-tile-render-r009.glb"
COLLISION = PACKAGE / "magnetic-slide-tile-collision-r009.fbx"
CORE = ["BottomExterior", "FixedAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight", "MovingTopBody"]
GROOVES = ["TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"]


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


def bounds(names):
    points = []
    for name in names:
        obj = bpy.data.objects[name]
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {"min": minimum, "max": maximum, "size": [maximum[index] - minimum[index] for index in range(3)]}


def model_snapshot(fmt):
    names = set(bpy.data.objects.keys())
    model_bounds = bounds(CORE)
    size_sorted = sorted(model_bounds["size"])
    expected_sorted = sorted([0.031, 0.05, 0.012])
    hierarchy = {name: bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None for name in names}
    mesh_records = {}
    for name in CORE:
        obj = bpy.data.objects[name]
        mesh_records[name] = {
            "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons),
            "materials": [material.name for material in obj.data.materials],
            "uvLayers": len(obj.data.uv_layers),
            "normalLengthsValid": all(0.99 <= normal.vector.length <= 1.01 for normal in obj.data.corner_normals),
        }
    root = bpy.data.objects["MagneticSlideTile_G05_R006"]
    checks = {
        "coreMeshes": all(name in names and bpy.data.objects[name].type == "MESH" for name in CORE),
        "fourGrooves": all(name in names for name in GROOVES),
        "hierarchy": hierarchy.get("TopLocalSlide") == "MovingTop" and hierarchy.get("MovingTopBody") == "TopLocalSlide" and hierarchy.get("RotatingCarrierBody") == "RotatingCarrier",
        "boundsMeters": all(abs(actual - expected) <= 0.00001 for actual, expected in zip(size_sorted, expected_sorted)),
        "normals": all(record["normalLengthsValid"] for record in mesh_records.values()),
        "uvs": all(record["uvLayers"] >= 1 for record in mesh_records.values()),
        "materialSlots": len({slot for record in mesh_records.values() for slot in record["materials"]}) >= 6,
        "metadata": str(root.get("canonicalGeometryDigest")) == "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
        "closedZeroMotion": str(root.get("defaultPose")) == "closed-zero-motion" and not bool(root.get("selfMotion")),
        "noAnimations": not bpy.data.actions and not any(obj.animation_data for obj in bpy.data.objects),
    }
    return {"format": fmt, "boundsMeters": model_bounds, "hierarchy": hierarchy, "meshes": mesh_records, "checks": checks, "pass": all(checks.values())}


def inspect_glb():
    raw = GLB.read_bytes()
    magic, version, total_length = struct.unpack_from("<4sII", raw, 0)
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    primitives = [primitive for mesh in document.get("meshes", []) for primitive in mesh.get("primitives", [])]
    checks = {
        "header": magic == b"glTF" and version == 2 and total_length == len(raw) and json_type == 0x4E4F534A,
        "eightMeshes": len(document.get("meshes", [])) == 8,
        "hierarchyNodes": len(document.get("nodes", [])) >= 20,
        "materials": len(document.get("materials", [])) >= 6,
        "embeddedImages": bool(document.get("images")) and all("bufferView" in image for image in document.get("images", [])),
        "normals": all("NORMAL" in primitive.get("attributes", {}) for primitive in primitives),
        "tangents": all("TANGENT" in primitive.get("attributes", {}) for primitive in primitives),
        "uvs": all("TEXCOORD_0" in primitive.get("attributes", {}) for primitive in primitives),
        "noAnimations": not document.get("animations"),
    }
    return {"counts": {key: len(document.get(key, [])) for key in ["nodes", "meshes", "materials", "textures", "images", "animations"]}, "checks": checks, "pass": all(checks.values())}


def main():
    results = {}
    clear()
    bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True)
    results["fbx"] = model_snapshot("fbx")
    clear()
    bpy.ops.import_scene.gltf(filepath=str(GLB), import_pack_images=False)
    results["glb"] = model_snapshot("glb")
    results["glbStructure"] = inspect_glb()
    clear()
    bpy.ops.import_scene.fbx(filepath=str(COLLISION), use_custom_normals=True)
    collision_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "MESH")
    collision_bounds = bounds(collision_names)
    collision_checks = {
        "separateTwoMeshes": collision_names == ["COL_BottomExterior", "COL_MovingTop"],
        "nonRenderingMetadata": all(bool(bpy.data.objects[name].get("collisionOnly")) and not bool(bpy.data.objects[name].get("rendering")) for name in collision_names),
        "noMaterials": all(len(bpy.data.objects[name].data.materials) == 0 for name in collision_names),
        "noAnimations": not bpy.data.actions,
    }
    results["collision"] = {"names": collision_names, "bounds": collision_bounds, "checks": collision_checks, "pass": all(collision_checks.values())}
    report = {"schemaVersion": 1, "gate": "10-export", "revision": 9, "results": results}
    report["pass"] = all(result["pass"] for result in results.values())
    (HERE / "reimport-validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({"pass": True, "fbxBounds": results["fbx"]["boundsMeters"], "glbBounds": results["glb"]["boundsMeters"], "glbCounts": results["glbStructure"]["counts"], "collision": collision_names}, indent=2))


if __name__ == "__main__":
    main()

