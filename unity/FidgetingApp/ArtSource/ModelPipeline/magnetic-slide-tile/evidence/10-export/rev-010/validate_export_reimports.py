#!/usr/bin/env python3
"""Independently reimport and audit Gate 10 FBX, GLB, and collision exports."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
FBX = PACKAGE / "magnetic-slide-tile-render-r010.fbx"
GLB = PACKAGE / "magnetic-slide-tile-render-r010.glb"
COLLISION = PACKAGE / "magnetic-slide-tile-collision-r010.fbx"
BUILD = json.loads((HERE / "export-build-report.json").read_text())
ROOT = "MagneticSlideTile_G06_R005"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
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
GROOVES = [
    "TopOuterGrooveLeft",
    "TopInnerGrooveLeft",
    "TopInnerGrooveRight",
    "TopOuterGrooveRight",
]
EXPECTED_IMAGES = {
    "lower-albedo": PACKAGE / "textures/lower-albedo.png",
    "lower-roughness": PACKAGE / "textures/lower-roughness.png",
    "upper-albedo": PACKAGE / "textures/upper-albedo.png",
    "upper-roughness": PACKAGE / "textures/upper-roughness.png",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clear() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def bounds(names: list[str]) -> dict:
    points = []
    for name in names:
        obj = bpy.data.objects[name]
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {
        "min": minimum,
        "max": maximum,
        "size": [maximum[index] - minimum[index] for index in range(3)],
    }


def material_triangles(name: str) -> dict:
    mesh = bpy.data.objects[name].data
    mesh.calc_loop_triangles()
    counts = [0] * len(mesh.materials)
    for triangle in mesh.loop_triangles:
        counts[triangle.material_index] += 1
    return {
        "slots": [material.name for material in mesh.materials],
        "triangleCounts": counts,
    }


def model_snapshot(fmt: str) -> dict:
    names = set(bpy.data.objects.keys())
    model_bounds = bounds(PRODUCT)
    expected_sorted = sorted([0.031, 0.05, 0.012])
    size_sorted = sorted(model_bounds["size"])
    hierarchy = {
        name: bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None
        for name in names
    }
    mesh_records = {}
    for name in CORE:
        obj = bpy.data.objects[name]
        mesh_records[name] = {
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "materials": [material.name for material in obj.data.materials],
            "uvLayers": len(obj.data.uv_layers),
            "normalLengthsValid": all(
                0.99 <= normal.vector.length <= 1.01 for normal in obj.data.corner_normals
            ),
        }
    partitions = {name: material_triangles(name) for name in PRODUCT}
    expected_partitions = BUILD["before"]["materialFaceCounts"]
    root = bpy.data.objects[ROOT]
    boss = bpy.data.objects["InternalAxisBoss"]
    checks = {
        "coreMeshes": all(name in names and bpy.data.objects[name].type == "MESH" for name in CORE),
        "fourGrooves": all(name in names and bpy.data.objects[name].type == "EMPTY" for name in GROOVES),
        "singlePivot": sum(name == "FixedAxis" and bpy.data.objects[name].type == "EMPTY" for name in names) == 1,
        "hierarchy": hierarchy.get("FixedAxis") == "BottomExterior"
            and hierarchy.get("RotatingCarrier") == "FixedAxis"
            and hierarchy.get("TopLocalSlide") == "MovingTop"
            and hierarchy.get("MovingTopBody") == "TopLocalSlide"
            and hierarchy.get("RotatingCarrierBody") == "RotatingCarrier",
        "boundsMeters": all(abs(actual - expected) <= 0.00001 for actual, expected in zip(size_sorted, expected_sorted)),
        "normals": all(record["normalLengthsValid"] for record in mesh_records.values()),
        "uvs": all(record["uvLayers"] >= 1 for record in mesh_records.values()),
        "partitionSlots": all(
            partitions[name]["slots"][:4] == expected_partitions[name]["slots"][:4]
            for name in PRODUCT
        ),
        "partitionTriangles": all(
            partitions[name]["triangleCounts"][:4] == expected_partitions[name]["triangleCounts"][:4]
            for name in PRODUCT
        ),
        "topArtworkPresent": all(partitions[name]["triangleCounts"][0] > 0 for name in PRODUCT),
        "sideArtworkZero": all(expected_partitions[name]["sideArtworkTriangles"] == 0 for name in PRODUCT),
        "undersideArtworkZero": all(expected_partitions[name]["undersideArtworkTriangles"] == 0 for name in PRODUCT),
        "silverRimPresent": all(partitions[name]["triangleCounts"][2] > 0 for name in PRODUCT),
        "metadata": str(root.get("canonicalGeometryDigest")) == GEOMETRY_DIGEST
            and str(root.get("sourceGate09ApprovalExactWording")) == "继续"
            and bool(root.get("rotationLockedBelowSMax"))
            and bool(root.get("slideLockedAtNonzeroAngle"))
            and int(root.get("detentCount")) == 30
            and int(root.get("detentStepDegrees")) == 12,
        "raisedBossNoRecess": abs(float(boss.get("protrusion_mm")) - 0.2) <= 0.001
            and not bool(boss.get("recessed_axis")),
        "minimumOverlapNotMesh": bpy.data.objects["MinimumOverlapDisk"].type == "EMPTY",
        "noCavityMesh": "_BottomExteriorUpperRim" not in names,
        "closedZeroMotion": str(root.get("defaultPose")) == "closed-zero-motion"
            and not bool(root.get("selfMotion"))
            and float(root.get("linearVelocityMmPerSecond")) == 0
            and float(root.get("angularVelocityDegreesPerSecond")) == 0,
        "noAnimations": not bpy.data.actions
            and not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
    }
    return {
        "format": fmt,
        "boundsMeters": model_bounds,
        "hierarchy": hierarchy,
        "meshes": mesh_records,
        "partitions": partitions,
        "checks": checks,
        "pass": all(checks.values()),
    }


def parse_glb() -> tuple[dict, bytes]:
    raw = GLB.read_bytes()
    magic, version, total_length = struct.unpack_from("<4sII", raw, 0)
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", raw, binary_header)
    binary_start = binary_header + 8
    if not (
        magic == b"glTF"
        and version == 2
        and total_length == len(raw)
        and json_type == 0x4E4F534A
        and binary_type == 0x004E4942
        and binary_start + binary_length <= len(raw)
    ):
        raise RuntimeError("Invalid GLB container.")
    return document, raw[binary_start:binary_start + binary_length]


def inspect_glb() -> dict:
    document, binary = parse_glb()
    primitives = [
        primitive
        for mesh in document.get("meshes", [])
        for primitive in mesh.get("primitives", [])
    ]
    embedded = {}
    for image in document.get("images", []):
        view = document["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset", 0)
        data = binary[start:start + view["byteLength"]]
        if data[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Embedded image {image.get('name')} is not PNG.")
        dimensions = list(struct.unpack_from(">II", data, 16))
        key = Path(image.get("name", "")).stem
        expected = next((path for name, path in EXPECTED_IMAGES.items() if name in key), None)
        embedded[key] = {
            "sha256": sha256_bytes(data),
            "dimensions": dimensions,
            "expectedSha256": sha256_bytes(expected.read_bytes()) if expected else None,
            "exact": bool(expected and sha256_bytes(data) == sha256_bytes(expected.read_bytes())),
        }
    samplers = document.get("samplers", [])
    checks = {
        "eightMeshes": len(document.get("meshes", [])) == 8,
        "hierarchyNodes": len(document.get("nodes", [])) >= 20,
        "materials": len(document.get("materials", [])) >= 7,
        "embeddedImages": len(embedded) == 4
            and all(item["exact"] for name, item in embedded.items() if "albedo" in name),
        "nativeImageDimensions": all(item["dimensions"] == [620, 1000] for item in embedded.values()),
        "clampSamplers": bool(samplers) and all(
            sampler.get("wrapS") == 33071 and sampler.get("wrapT") == 33071
            for sampler in samplers
        ),
        "normals": all("NORMAL" in primitive.get("attributes", {}) for primitive in primitives),
        "tangents": all("TANGENT" in primitive.get("attributes", {}) for primitive in primitives),
        "uvs": all("TEXCOORD_0" in primitive.get("attributes", {}) for primitive in primitives),
        "noAnimations": not document.get("animations"),
    }
    return {
        "counts": {
            key: len(document.get(key, []))
            for key in ["nodes", "meshes", "materials", "textures", "images", "animations"]
        },
        "embeddedImages": embedded,
        "samplers": samplers,
        "checks": checks,
        "pass": all(checks.values()),
    }


def point_camera(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def render_glb_review() -> dict:
    for name in CORE:
        bpy.data.objects[name].hide_render = name not in PRODUCT
    world = bpy.data.worlds.new("Gate10ReviewWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.008, 0.006, 0.007, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
    bpy.ops.object.light_add(type="AREA", location=(0.07, -0.05, 0.10))
    key = bpy.context.object
    key.data.energy = 75
    key.data.shape = "DISK"
    key.data.size = 0.06
    point_camera(key, Vector((0, 0, 0.006)))
    bpy.ops.object.light_add(type="AREA", location=(-0.06, 0.03, 0.05))
    fill = bpy.context.object
    fill.data.energy = 42
    fill.data.size = 0.05
    point_camera(fill, Vector((0, 0, 0.006)))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    views = [
        ("gate10-r010-glb-hero.png", Vector((0.075, -0.105, 0.074)), Vector((0, 0, 0.005))),
        ("gate10-r010-glb-top.png", Vector((0, -0.055, 0.12)), Vector((0, 0, 0.004))),
    ]
    output = []
    for filename, location, target in views:
        bpy.ops.object.camera_add(location=location)
        camera = bpy.context.object
        camera.data.lens = 72
        camera.data.sensor_width = 36
        point_camera(camera, target)
        scene.camera = camera
        scene.render.filepath = str(HERE / filename)
        bpy.ops.render.render(write_still=True)
        output.append(HERE / filename)
        bpy.data.objects.remove(camera, do_unlink=True)
    return {
        "hero": {"path": str(output[0]), "sha256": sha256_bytes(output[0].read_bytes())},
        "top": {"path": str(output[1]), "sha256": sha256_bytes(output[1].read_bytes())},
    }


def main() -> None:
    results = {}
    clear()
    bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True)
    results["fbx"] = model_snapshot("fbx")
    clear()
    bpy.ops.import_scene.gltf(filepath=str(GLB), import_pack_images=False)
    results["glb"] = model_snapshot("glb")
    results["glbStructure"] = inspect_glb()
    results["reviewRenders"] = render_glb_review()
    clear()
    bpy.ops.import_scene.fbx(filepath=str(COLLISION), use_custom_normals=True)
    collision_names = sorted(obj.name for obj in bpy.data.objects if obj.type == "MESH")
    collision_checks = {
        "separateTwoMeshes": collision_names == ["COL_BottomExterior", "COL_MovingTop"],
        "nonRenderingMetadata": all(
            bool(bpy.data.objects[name].get("collisionOnly"))
            and not bool(bpy.data.objects[name].get("rendering"))
            for name in collision_names
        ),
        "noMaterials": all(len(bpy.data.objects[name].data.materials) == 0 for name in collision_names),
        "noAnimations": not bpy.data.actions,
    }
    results["collision"] = {
        "names": collision_names,
        "bounds": bounds(collision_names),
        "checks": collision_checks,
        "pass": all(collision_checks.values()),
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "results": results,
    }
    report["pass"] = all(
        results[key]["pass"] for key in ["fbx", "glb", "glbStructure", "collision"]
    )
    (HERE / "reimport-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({
        "pass": True,
        "fbxBounds": results["fbx"]["boundsMeters"],
        "glbBounds": results["glb"]["boundsMeters"],
        "glbCounts": results["glbStructure"]["counts"],
        "collision": collision_names,
    }, indent=2))


if __name__ == "__main__":
    main()
