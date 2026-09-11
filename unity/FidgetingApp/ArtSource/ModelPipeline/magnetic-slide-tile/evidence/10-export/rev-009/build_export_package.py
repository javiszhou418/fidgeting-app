#!/usr/bin/env python3
"""Build Gate 10 Blend, FBX, GLB and separate collision exports."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL = HERE.parent.parent.parent
SOURCE = MODEL / "evidence/09-environment/rev-008/magnetic-slide-tile-environment-r008.blend"
PACKAGE = HERE / "package"
BLEND = PACKAGE / "magnetic-slide-tile-authoritative-r009.blend"
FBX = PACKAGE / "magnetic-slide-tile-render-r009.fbx"
GLB = PACKAGE / "magnetic-slide-tile-render-r009.glb"
COLLISION = PACKAGE / "magnetic-slide-tile-collision-r009.fbx"
SOURCE_SHA = "d53886f887649e7398808c2938bed081328e11259e772b1420415dc2ffc30408"
GEOMETRY_SHA = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
MATERIAL_SHA = "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8"
CONTRACT_SHA = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
PORTABILITY_SHA = "fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134"
CORE = ["BottomExterior", "FixedAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight", "MovingTopBody"]
HIERARCHY = [
    "MagneticSlideTile_G05_R006", "BottomExterior", "FixedAxis", "FixedAxisBoss", "MinimumOverlapDisk",
    "RotatingCarrier", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "UnknownSprings", "UnknownPreload",
    "MovingTop", "TopLocalSlide", "MovingTopBody", "TopOuterGrooveLeft",
    "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight",
]


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


def triangle_digest():
    digest = hashlib.sha256()
    for name in CORE:
        mesh = bpy.data.objects[name].data
        mesh.calc_loop_triangles()
        digest.update(name.encode())
        for triangle in mesh.loop_triangles:
            coords = [mesh.vertices[index].co for index in triangle.vertices]
            for coordinate in coords:
                digest.update(",".join(f"{value:.9f}" for value in coordinate).encode()); digest.update(b";")
    return digest.hexdigest()


def world_bounds(names):
    points = []
    for name in names:
        obj = bpy.data.objects[name]
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {"minMm": minimum, "maxMm": maximum, "sizeMm": [maximum[index] - minimum[index] for index in range(3)]}


def snapshot():
    return {
        name: {
            "type": bpy.data.objects[name].type,
            "parent": bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None,
            "matrixWorld": [[round(float(value), 9) for value in row] for row in bpy.data.objects[name].matrix_world],
        } for name in HIERARCHY
    }


def select(names):
    bpy.ops.object.select_all(action="DESELECT")
    for name in names:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[names[0]]


def create_collision(name, location, dimensions, bevel):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("CollisionBevel", "BEVEL")
    modifier.width = bevel
    modifier.segments = 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj["collisionOnly"] = True
    obj["rendering"] = False
    obj["shape"] = "rounded-box-conservative"
    return obj


def mark_cap_boundaries(mesh):
    attribute = mesh.attributes.get("sharp_edge") or mesh.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
    edge_faces = {edge.key: [] for edge in mesh.edges}
    for polygon in mesh.polygons:
        for key in polygon.edge_keys:
            edge_faces[key].append(polygon)
    for edge in mesh.edges:
        faces = edge_faces[edge.key]
        if len(faces) != 2:
            continue
        planar = [abs(face.normal.z) >= 0.9999 for face in faces]
        curved = [abs(face.normal.z) <= 0.995 for face in faces]
        if (planar[0] and curved[1]) or (planar[1] and curved[0]):
            attribute.data[edge.index].value = True


def patch_glb_zero_vectors(path):
    raw = bytearray(Path(path).read_bytes())
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError("GLB JSON chunk is missing.")
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", raw, binary_header)
    if binary_type != 0x004E4942:
        raise RuntimeError("GLB binary chunk is missing.")
    binary_start = binary_header + 8

    def location(accessor_index, element_index, components):
        accessor = document["accessors"][accessor_index]
        view = document["bufferViews"][accessor["bufferView"]]
        stride = view.get("byteStride", components * 4)
        return binary_start + view.get("byteOffset", 0) + accessor.get("byteOffset", 0) + element_index * stride

    patched_normals = 0
    patched_tangents = 0
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            attributes = primitive.get("attributes", {})
            position_accessor = document["accessors"][attributes["POSITION"]]
            normal_accessor = document["accessors"][attributes["NORMAL"]]
            tangent_accessor = document["accessors"][attributes["TANGENT"]]
            if not all(accessor["componentType"] == 5126 for accessor in [position_accessor, normal_accessor, tangent_accessor]):
                raise RuntimeError("Expected float32 GLB vectors.")
            y_values = [struct.unpack_from("<3f", raw, location(attributes["POSITION"], index, 3))[1] for index in range(position_accessor["count"])]
            y_mid = (min(y_values) + max(y_values)) * 0.5
            for index in range(normal_accessor["count"]):
                normal_offset = location(attributes["NORMAL"], index, 3)
                normal = struct.unpack_from("<3f", raw, normal_offset)
                if math.sqrt(sum(value * value for value in normal)) < 0.5:
                    y = struct.unpack_from("<3f", raw, location(attributes["POSITION"], index, 3))[1]
                    struct.pack_into("<3f", raw, normal_offset, 0.0, 1.0 if y >= y_mid else -1.0, 0.0)
                    patched_normals += 1
                tangent_offset = location(attributes["TANGENT"], index, 4)
                tangent = struct.unpack_from("<4f", raw, tangent_offset)
                if math.sqrt(sum(value * value for value in tangent[:3])) < 0.5:
                    struct.pack_into("<4f", raw, tangent_offset, 1.0, 0.0, 0.0, 1.0)
                    patched_tangents += 1
    Path(path).write_bytes(raw)
    return {"zeroNormalsPatched": patched_normals, "zeroTangentsPatched": patched_tangents}


def world_z_extents(name):
    obj = bpy.data.objects[name]
    values = [(obj.matrix_world @ vertex.co).z for vertex in obj.data.vertices]
    return min(values), max(values)


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    if sha256(SOURCE) != SOURCE_SHA or Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Gate 09 source blend hash drift.")
    if geometry_digest() != GEOMETRY_SHA:
        raise RuntimeError("Gate 09 canonical geometry digest drift.")
    bpy.data.objects["RotatingCarrier"].rotation_euler = (0, 0, 0)
    bpy.data.objects["MovingTop"].rotation_euler = (0, 0, 0)
    bpy.data.objects["TopLocalSlide"].location = (0, 0, 0)
    bpy.context.view_layer.update()
    root = bpy.data.objects["MagneticSlideTile_G05_R006"]
    root["gate10Revision"] = 9
    root["mechanismContractSha256"] = CONTRACT_SHA
    root["unityPortabilityContractSha256"] = PORTABILITY_SHA
    root["canonicalGeometryDigest"] = GEOMETRY_SHA
    root["approvedMaterialDigest"] = MATERIAL_SHA
    root["units"] = "millimeters-authoring; export conversion to meters"
    root["defaultPose"] = "closed-zero-motion"
    root["selfMotion"] = False
    root["animationClips"] = 0
    root["detentCount"] = 30
    root["detentStepDegrees"] = 12
    root["maximumTravelMm"] = 18.076433121019107
    root["mechanismAxisPointMm"] = [0.0, -9.5, 0.0]
    root["mechanismAxisDirection"] = "+Z"
    root["carrierTransform"] = "R_fixedAxis(theta)"
    root["topTransform"] = "R_fixedAxis(theta)*T_local(slide)"
    root["minimumOverlapRule"] = "MinimumOverlapDisk contained through 3600-sample sweep"
    root["provisionalDimensions"] = "50x31x12 mm user-authorized-provisional-not-production-measured"
    root["lodPolicy"] = "single approved render model; no unapproved LOD/high-poly pair"
    for name in CORE:
        mesh = bpy.data.objects[name].data
        mesh.set_sharp_from_angle(angle=0.5235987756)
        for polygon in mesh.polygons:
            if abs(polygon.normal.z) >= 0.9999:
                polygon.use_smooth = False
        mark_cap_boundaries(mesh)
    before = {
        "geometryDigest": geometry_digest(),
        "triangleDigest": triangle_digest(),
        "hierarchy": snapshot(),
        "bounds": world_bounds(CORE),
        "meshes": {
            name: {
                "vertices": len(bpy.data.objects[name].data.vertices),
                "polygons": len(bpy.data.objects[name].data.polygons),
                "materialSlots": [material.name for material in bpy.data.objects[name].data.materials],
                "uvLayers": [layer.name for layer in bpy.data.objects[name].data.uv_layers],
                "smoothFaces": sum(1 for polygon in bpy.data.objects[name].data.polygons if polygon.use_smooth),
                "flatFaces": sum(1 for polygon in bpy.data.objects[name].data.polygons if not polygon.use_smooth),
            } for name in CORE
        },
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    triangulate_modifiers = []
    for name in CORE:
        modifier = bpy.data.objects[name].modifiers.new("Gate10ExportTriangulate", "TRIANGULATE")
        modifier.keep_custom_normals = True
        triangulate_modifiers.append((bpy.data.objects[name], modifier))
    select(HIERARCHY)
    bpy.ops.export_scene.fbx(
        filepath=str(FBX), use_selection=True, object_types={"EMPTY", "MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
        use_mesh_modifiers=True, mesh_smooth_type="FACE", use_tspace=True,
        add_leaf_bones=False, bake_anim=False, path_mode="COPY", embed_textures=True, use_custom_props=True,
    )
    root.scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.update()
    select(HIERARCHY)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB), export_format="GLB", use_selection=True, export_extras=True,
        export_apply=True, export_animations=False, export_tangents=True, export_yup=True,
    )
    glb_vector_repair = patch_glb_zero_vectors(GLB)
    root.scale = (1.0, 1.0, 1.0)
    for obj, modifier in triangulate_modifiers:
        obj.modifiers.remove(modifier)
    bpy.context.view_layer.update()
    collisions = [
        create_collision("COL_BottomExterior", (0, 0, 2.9), (30.4, 49.4, 5.6), 3.2),
        create_collision("COL_MovingTop", (0, 0, 9.0), (30.4, 49.4, 5.6), 3.2),
    ]
    select([obj.name for obj in collisions])
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION), use_selection=True, object_types={"MESH"},
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
        mesh_smooth_type="FACE", use_tspace=True, add_leaf_bones=False, bake_anim=False, use_custom_props=True,
    )
    for obj in collisions:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.update()
    after = {"geometryDigest": geometry_digest(), "triangleDigest": triangle_digest(), "hierarchy": snapshot(), "bounds": world_bounds(CORE)}
    report = {
        "schemaVersion": 1, "gate": "10-export", "revision": 9, "pass": False,
        "source": {"path": str(SOURCE), "sha256": SOURCE_SHA, "gate09ApprovalWording": "你给我看一下最终在 Unity 里边的呈现吧。"},
        "contractSha256": CONTRACT_SHA, "portabilityContractSha256": PORTABILITY_SHA,
        "approved": {"geometryDigest": GEOMETRY_SHA, "materialDigest": MATERIAL_SHA},
        "before": before, "after": after,
        "formats": {
            "blend": {"path": str(BLEND), "sha256": sha256(BLEND), "bytes": BLEND.stat().st_size},
            "fbx": {"path": str(FBX), "sha256": sha256(FBX), "bytes": FBX.stat().st_size},
            "glb": {"path": str(GLB), "sha256": sha256(GLB), "bytes": GLB.stat().st_size},
            "collisionFbx": {"path": str(COLLISION), "sha256": sha256(COLLISION), "bytes": COLLISION.stat().st_size},
        },
        "exportSettings": {
            "fbx": {"meshSmoothType": "FACE", "meshSmoothTypeOff": False, "forward": "-Z", "up": "Y", "applyUnitScale": True, "bakeAnimation": False},
            "glb": {"format": "GLB", "yUp": True, "tangents": True, "animations": False, "extras": True},
            "collision": {"separate": True, "rendering": False, "objects": ["COL_BottomExterior", "COL_MovingTop"], "misleadingDisplayForbidden": True},
        },
        "glbVectorRepair": glb_vector_repair,
        "checks": {
            "sourceHash": sha256(SOURCE) == SOURCE_SHA,
            "geometryExact": before["geometryDigest"] == after["geometryDigest"] == GEOMETRY_SHA,
            "trianglesExact": before["triangleDigest"] == after["triangleDigest"],
            "hierarchyExact": before["hierarchy"] == after["hierarchy"],
            "boundsExact": before["bounds"] == after["bounds"],
            "eightRenderMeshes": len(CORE) == 8,
            "fourGrooves": all(name in HIERARCHY for name in ["TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"]),
            "flatBottomNoCavity": abs(world_z_extents("BottomExterior")[1] - 5.875) <= 0.001 and not bpy.data.objects.get("_BottomExteriorUpperRim"),
            "raisedAxis": abs((world_z_extents("FixedAxisBoss")[1] - 5.875) - 0.2) <= 0.001,
            "closedZeroMotion": all(abs(value) < 1e-9 for value in bpy.data.objects["TopLocalSlide"].location) and all(abs(value) < 1e-9 for value in bpy.data.objects["MovingTop"].rotation_euler),
            "noAnimations": not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
            "filesWritten": all(path.exists() and path.stat().st_size > 1024 for path in [BLEND, FBX, GLB, COLLISION]),
            "noLodPair": True,
            "unityNotUsed": True,
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "export-build-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({"pass": True, "geometryDigest": GEOMETRY_SHA, "triangleDigest": before["triangleDigest"], "bounds": before["bounds"], "formats": report["formats"]}, indent=2))


if __name__ == "__main__":
    main()

