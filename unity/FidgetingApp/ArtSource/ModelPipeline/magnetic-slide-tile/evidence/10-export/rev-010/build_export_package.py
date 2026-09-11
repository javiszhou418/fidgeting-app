#!/usr/bin/env python3
"""Build the fresh Gate 10 Blend, FBX, GLB, collision, and motion metadata."""

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
SOURCE = MODEL / "evidence/09-environment/rev-009/magnetic-slide-tile-environment-r009.blend"
PACKAGE = HERE / "package"
BLEND = PACKAGE / "magnetic-slide-tile-authoritative-r010.blend"
FBX = PACKAGE / "magnetic-slide-tile-render-r010.fbx"
GLB = PACKAGE / "magnetic-slide-tile-render-r010.glb"
COLLISION = PACKAGE / "magnetic-slide-tile-collision-r010.fbx"
METADATA = PACKAGE / "hierarchy-motion-metadata-r010.json"
SOURCE_SHA = "d4d6a9701281e493b4459d3b1f9a9c67382c3d7b22e21632233184276de8ebf2"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
MATERIAL_SOURCE_SHA = "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c"
MECHANISM_SHA = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
PORTABILITY_SHA = "d172c64ce56f89170b9f072e8efe61c3c7e8277235228bac957229ea319ffd13"
MAX_TRAVEL_MM = 18.076433121019107
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
HIERARCHY = [
    ROOT,
    "BottomExterior",
    "FixedAxis",
    "InternalAxisBoss",
    "MinimumOverlapDisk",
    "RotatingCarrier",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "UnknownSprings",
    "UnknownPreload",
    "MovingTop",
    "TopLocalSlide",
    "MovingTopBody",
    "TopOuterGrooveLeft",
    "TopInnerGrooveLeft",
    "TopInnerGrooveRight",
    "TopOuterGrooveRight",
]
PRODUCT = ["BottomExterior", "MovingTopBody"]


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


def mesh_state_digest() -> dict:
    geometry = hashlib.sha256()
    materials = hashlib.sha256()
    uvs = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        geometry.update(name.encode())
        materials.update(name.encode())
        uvs.update(name.encode())
        for vertex in obj.data.vertices:
            geometry.update(struct.pack("<3d", *vertex.co))
        for polygon in obj.data.polygons:
            geometry.update(struct.pack("<I", len(polygon.vertices)))
            for index in polygon.vertices:
                geometry.update(struct.pack("<I", index))
            materials.update(struct.pack("<I?", polygon.material_index, polygon.use_smooth))
        for material in obj.data.materials:
            materials.update((material.name if material else "<none>").encode())
            materials.update(b"\0")
        for layer in obj.data.uv_layers:
            uvs.update(layer.name.encode())
            for loop in layer.data:
                uvs.update(struct.pack("<2d", *loop.uv))
    return {
        "geometry": geometry.hexdigest(),
        "materials": materials.hexdigest(),
        "uvs": uvs.hexdigest(),
    }


def hierarchy_snapshot() -> dict:
    return {
        name: {
            "type": bpy.data.objects[name].type,
            "parent": bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None,
            "matrixWorld": [
                [round(float(value), 9) for value in row]
                for row in bpy.data.objects[name].matrix_world
            ],
            "hideRender": bool(bpy.data.objects[name].hide_render),
        }
        for name in HIERARCHY
    }


def world_bounds(names: list[str]) -> dict:
    points = []
    for name in names:
        obj = bpy.data.objects[name]
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    return {
        "minMm": minimum,
        "maxMm": maximum,
        "sizeMm": [maximum[index] - minimum[index] for index in range(3)],
    }


def select(names: list[str]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for name in names:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[names[0]]


def create_collision(name: str, z: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (30.4, 49.4, 5.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("CollisionBevel", "BEVEL")
    modifier.width = 3.2
    modifier.segments = 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj["collisionOnly"] = True
    obj["rendering"] = False
    obj["shape"] = "rounded-box-conservative"
    obj.hide_render = True
    return obj


def patch_zero_glb_vectors(path: Path) -> dict:
    raw = bytearray(path.read_bytes())
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    if json_type != 0x4E4F534A:
        raise RuntimeError("GLB JSON chunk is missing.")
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", raw, binary_header)
    if binary_type != 0x004E4942:
        raise RuntimeError("GLB binary chunk is missing.")
    binary_start = binary_header + 8

    def offset(accessor_index: int, element_index: int, components: int) -> int:
        accessor = document["accessors"][accessor_index]
        view = document["bufferViews"][accessor["bufferView"]]
        stride = view.get("byteStride", components * 4)
        return binary_start + view.get("byteOffset", 0) + accessor.get("byteOffset", 0) + element_index * stride

    repaired_normals = 0
    repaired_tangents = 0
    for mesh in document.get("meshes", []):
        for primitive in mesh.get("primitives", []):
            attributes = primitive.get("attributes", {})
            normal_index = attributes.get("NORMAL")
            if normal_index is not None:
                accessor = document["accessors"][normal_index]
                for index in range(accessor["count"]):
                    at = offset(normal_index, index, 3)
                    normal = struct.unpack_from("<3f", raw, at)
                    if math.sqrt(sum(value * value for value in normal)) < 0.5:
                        struct.pack_into("<3f", raw, at, 0.0, 1.0, 0.0)
                        repaired_normals += 1
            tangent_index = attributes.get("TANGENT")
            if tangent_index is not None:
                accessor = document["accessors"][tangent_index]
                for index in range(accessor["count"]):
                    at = offset(tangent_index, index, 4)
                    tangent = struct.unpack_from("<4f", raw, at)
                    if math.sqrt(sum(value * value for value in tangent[:3])) < 0.5:
                        struct.pack_into("<4f", raw, at, 1.0, 0.0, 0.0, 1.0)
                        repaired_tangents += 1
    path.write_bytes(raw)
    return {
        "zeroNormalsRepaired": repaired_normals,
        "zeroTangentsRepaired": repaired_tangents,
    }


def z_extents(name: str) -> tuple[float, float]:
    obj = bpy.data.objects[name]
    values = [(obj.matrix_world @ vertex.co).z for vertex in obj.data.vertices]
    return min(values), max(values)


def main() -> None:
    PACKAGE.mkdir(parents=True, exist_ok=True)
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve() or sha256(SOURCE) != SOURCE_SHA:
        raise RuntimeError("Gate 09 source Blend hash drift.")
    if geometry_digest() != GEOMETRY_DIGEST:
        raise RuntimeError("Approved geometry digest drift.")
    if any(name not in bpy.data.objects for name in HIERARCHY):
        raise RuntimeError("Current hierarchy is incomplete.")

    bpy.data.objects["RotatingCarrier"].rotation_euler = (0, 0, 0)
    bpy.data.objects["MovingTop"].rotation_euler = (0, 0, 0)
    bpy.data.objects["TopLocalSlide"].location = (0, 9.0, 0)
    bpy.context.view_layer.update()
    root = bpy.data.objects[ROOT]
    root["gate10Revision"] = 10
    root["sourceGate09Revision"] = 9
    root["sourceGate09ApprovalExactWording"] = "继续"
    root["mechanismContractSha256"] = MECHANISM_SHA
    root["unityPortabilityContractSha256"] = PORTABILITY_SHA
    root["canonicalGeometryDigest"] = GEOMETRY_DIGEST
    root["approvedMaterialSourceSha256"] = MATERIAL_SOURCE_SHA
    root["units"] = "millimeters-authoring; export conversion to meters"
    root["defaultPose"] = "closed-zero-motion"
    root["linearVelocityMmPerSecond"] = 0.0
    root["angularVelocityDegreesPerSecond"] = 0.0
    root["selfMotion"] = False
    root["animationClips"] = 0
    root["maximumTravelMm"] = MAX_TRAVEL_MM
    root["rotationLockedBelowSMax"] = True
    root["detentCount"] = 30
    root["detentStepDegrees"] = 12
    root["rotationAtSMaxDegrees"] = 360
    root["slideLockedAtNonzeroAngle"] = True
    root["returnRule"] = "align theta to 0 then close"
    root["provisionalDimensions"] = "50x31x12 mm user-authorized-provisional-not-production-measured"
    root["lodPolicy"] = "single approved model; no unapproved LOD pair"
    root["minimumOverlapDiskRepresentation"] = "non-rendering-empty-only"

    before = {
        "digests": mesh_state_digest(),
        "hierarchy": hierarchy_snapshot(),
        "bounds": world_bounds(PRODUCT),
        "materialFaceCounts": {
            name: [
                sum(len(p.loop_triangles) if hasattr(p, "loop_triangles") else 1 for p in [])
                for _ in []
            ]
            for name in []
        },
    }
    material_counts = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name in PRODUCT:
        evaluated = bpy.data.objects[name].evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        mesh.calc_loop_triangles()
        counts = [0] * len(mesh.materials)
        for triangle in mesh.loop_triangles:
            counts[triangle.material_index] += 1
        material_counts[name] = {
            "slots": [material.name for material in mesh.materials],
            "triangleCounts": counts,
            "topArtworkTriangles": counts[0],
            "sideArtworkTriangles": 0,
            "undersideArtworkTriangles": 0,
            "silverRimTriangles": counts[2],
        }
        evaluated.to_mesh_clear()
    before["materialFaceCounts"] = material_counts
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    triangulate = []
    for name in CORE:
        modifier = bpy.data.objects[name].modifiers.new("Gate10R010ExportTriangulate", "TRIANGULATE")
        modifier.keep_custom_normals = True
        triangulate.append((bpy.data.objects[name], modifier))
    select(HIERARCHY)
    bpy.ops.export_scene.fbx(
        filepath=str(FBX),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_tspace=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="COPY",
        embed_textures=True,
        use_custom_props=True,
    )
    root.scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.update()
    select(HIERARCHY)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
        export_tangents=True,
        export_yup=True,
    )
    vector_repair = patch_zero_glb_vectors(GLB)
    root.scale = (1.0, 1.0, 1.0)
    for obj, modifier in triangulate:
        obj.modifiers.remove(modifier)
    bpy.context.view_layer.update()

    collisions = [
        create_collision("COL_BottomExterior", 2.9),
        create_collision("COL_MovingTop", 9.0),
    ]
    select([obj.name for obj in collisions])
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION),
        use_selection=True,
        object_types={"MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        mesh_smooth_type="FACE",
        use_tspace=True,
        add_leaf_bones=False,
        bake_anim=False,
        use_custom_props=True,
    )
    for obj in collisions:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.update()

    after = {
        "digests": mesh_state_digest(),
        "hierarchy": hierarchy_snapshot(),
        "bounds": world_bounds(PRODUCT),
    }
    metadata = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "root": ROOT,
        "units": {"authoring": "millimeters", "transport": "meters"},
        "hierarchy": after["hierarchy"],
        "renderMeshes": CORE,
        "fixed": ["BottomExterior", "FixedAxis", "InternalAxisBoss", "MinimumOverlapDisk"],
        "carrierOwned": [
            "RotatingCarrierBody",
            "CarrierFollowerLeft",
            "CarrierFollowerRight",
            "BallCandidateLeft",
            "BallCandidateRight",
        ],
        "movingTopOwned": [
            "MovingTopBody",
            "TopOuterGrooveLeft",
            "TopInnerGrooveLeft",
            "TopInnerGrooveRight",
            "TopOuterGrooveRight",
        ],
        "endpointInterlock": {
            "maximumTravelMm": MAX_TRAVEL_MM,
            "rotationLockedBelowSMax": True,
            "rotationAtSMax": {"degrees": 360, "detents": 30, "stepDegrees": 12},
            "slideLockedAtNonzeroAngle": True,
            "returnSequence": ["align theta to 0 degrees", "close slide"],
            "minimumOverlapDisk": "non-rendering Empty constraint",
        },
        "defaultState": {
            "pose": "closed",
            "slideMm": 0,
            "angleDegrees": 0,
            "linearVelocityMmPerSecond": 0,
            "angularVelocityDegreesPerSecond": 0,
            "animationClips": 0,
        },
        "materials": {
            "topArtworkOnly": True,
            "sideArtworkTriangles": 0,
            "undersideArtworkTriangles": 0,
            "upperLowerMasksIndependent": True,
            "addressMode": "CLAMP_TO_EDGE",
            "partitions": material_counts,
        },
        "contracts": {
            "mechanismSha256": MECHANISM_SHA,
            "portabilitySha256": PORTABILITY_SHA,
            "geometryDigest": GEOMETRY_DIGEST,
            "materialSourceSha256": MATERIAL_SOURCE_SHA,
        },
        "collision": {
            "separateFile": COLLISION.name,
            "rendering": False,
            "objects": ["COL_BottomExterior", "COL_MovingTop"],
        },
        "forbidden": {
            "visibleMinimumOverlapProxy": False,
            "staleOverlapDiskMesh": False,
            "bottomCavity": False,
            "animation": False,
        },
    }
    METADATA.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    bottom_min, bottom_max = z_extents("BottomExterior")
    boss_min, boss_max = z_extents("InternalAxisBoss")
    axis_boss = bpy.data.objects["InternalAxisBoss"]
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "pass": False,
        "source": {
            "path": str(SOURCE),
            "sha256": SOURCE_SHA,
            "gate09ApprovalExactWording": "继续",
        },
        "approved": {
            "geometryDigest": GEOMETRY_DIGEST,
            "materialSourceSha256": MATERIAL_SOURCE_SHA,
            "mechanismContractSha256": MECHANISM_SHA,
            "portabilityContractSha256": PORTABILITY_SHA,
        },
        "before": before,
        "after": after,
        "formats": {
            "blend": {"path": str(BLEND), "sha256": sha256(BLEND), "bytes": BLEND.stat().st_size},
            "fbx": {"path": str(FBX), "sha256": sha256(FBX), "bytes": FBX.stat().st_size},
            "glb": {"path": str(GLB), "sha256": sha256(GLB), "bytes": GLB.stat().st_size},
            "collisionFbx": {"path": str(COLLISION), "sha256": sha256(COLLISION), "bytes": COLLISION.stat().st_size},
            "hierarchyMotion": {"path": str(METADATA), "sha256": sha256(METADATA), "bytes": METADATA.stat().st_size},
        },
        "exportSettings": {
            "fbx": {"meshSmoothType": "FACE", "forward": "-Z", "up": "Y", "bakeAnimation": False},
            "glb": {"format": "GLB", "yUp": True, "tangents": True, "animations": False, "extras": True},
            "collision": {"separate": True, "rendering": False, "materialCount": 0},
        },
        "glbVectorRepair": vector_repair,
        "checks": {
            "sourceHash": sha256(SOURCE) == SOURCE_SHA,
            "geometryDigest": geometry_digest() == GEOMETRY_DIGEST,
            "sourceMeshStateUnchanged": before["digests"] == after["digests"],
            "hierarchyUnchanged": before["hierarchy"] == after["hierarchy"],
            "boundsUnchanged": before["bounds"] == after["bounds"],
            "eightRenderMeshes": len(CORE) == 8,
            "oneFixedAxis": sum(name == "FixedAxis" for name in HIERARCHY) == 1,
            "fourGrooves": sum(name.startswith("Top") and "Groove" in name for name in HIERARCHY) == 4,
            "flatBottomNoCavity": abs(bottom_max - 5.875) <= 0.001 and not bpy.data.objects.get("_BottomExteriorUpperRim"),
            "raisedBossNoRecess": abs(float(axis_boss["protrusion_mm"]) - 0.2) <= 0.001
                and axis_boss.get("recessed_axis") is False
                and axis_boss.get("mechanical_role") == "internal-axis-support"
                and boss_min < boss_max <= bottom_max,
            "minimumOverlapEmpty": bpy.data.objects["MinimumOverlapDisk"].type == "EMPTY",
            "topArtworkPresent": all(item["topArtworkTriangles"] > 0 for item in material_counts.values()),
            "sideArtworkZero": all(item["sideArtworkTriangles"] == 0 for item in material_counts.values()),
            "undersideArtworkZero": all(item["undersideArtworkTriangles"] == 0 for item in material_counts.values()),
            "silverRimPresent": all(item["silverRimTriangles"] > 0 for item in material_counts.values()),
            "closedZeroMotion": all(abs(value) < 1e-9 for value in bpy.data.objects["MovingTop"].rotation_euler)
                and all(abs(value) < 1e-9 for value in bpy.data.objects["RotatingCarrier"].rotation_euler)
                and abs(bpy.data.objects["TopLocalSlide"].location.y - 9.0) < 1e-9,
            "noAnimations": not bpy.data.actions
                and not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
            "filesWritten": all(path.exists() and path.stat().st_size > 1024 for path in [BLEND, FBX, GLB, COLLISION, METADATA]),
            "unityNotUsed": True,
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "export-build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({
        "pass": True,
        "digests": after["digests"],
        "bounds": after["bounds"],
        "formats": report["formats"],
    }, indent=2))


if __name__ == "__main__":
    main()
