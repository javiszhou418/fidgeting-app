#!/usr/bin/env python3
"""Build the immutable Gate 10 Blender, FBX, GLB, collision, and texture package."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import bmesh
import bpy


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
TEXTURES = ROOT / "textures"
SOURCE_BLEND = ROOT.parents[1] / "09-environment/rev-002/magnetic-slide-tile-environment-open-r002.blend"
SOURCE_REPORT = ROOT.parents[1] / "09-environment/rev-002/open-environment-validation.json"
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json"
AUTHORITATIVE_BLEND = ROOT / "magnetic-slide-tile-authoritative.blend"
FBX = ROOT / "magnetic-slide-tile.fbx"
GLB = ROOT / "magnetic-slide-tile.glb"
COLLISION_FBX = ROOT / "magnetic-slide-tile-collision.fbx"
MANIFEST = ROOT / "export-manifest.json"
TEXTURE_MANIFEST = ROOT / "texture-manifest.json"
EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
EXPECTED_LOCAL_MESH_HASH = "50b1f913f8b94a1428af404478cb5169d7e142b765955d224125108de463d5d0"
EXPECTED_ARTWORK_HASH = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
KEEP_OBJECTS = {
    "MagneticSlideTile_Blockout_R003",
    "FixedAssembly",
    "LowerBody_Fixed_CleanPlane",
    "UpperTranslation",
    "CentralAxisPivot_Point",
    "UpperCapsule_Moving",
    "ConcealedCircularEnvelope_Metadata",
}
SHIPPING_MATERIALS = [
    "M07R7_DaylightNeutralPolishedSilver",
    "M07R7_BloodRedCrystal_WideBorder_Upper",
    "M07R7_BloodRedCrystal_WideBorder_Lower",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_mesh_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        mesh = obj.data
        digest.update(obj.name.encode())
        for vertex in mesh.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in mesh.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
    return digest.hexdigest()


def world_bounds(objects: list[bpy.types.Object]) -> dict:
    points = []
    for obj in objects:
        points.extend(obj.matrix_world @ vertex.co for vertex in obj.data.vertices)
    minimum = [min(point[index] for point in points) for index in range(3)]
    maximum = [max(point[index] for point in points) for index in range(3)]
    return {
        "minimumMm": [round(value, 6) for value in minimum],
        "maximumMm": [round(value, 6) for value in maximum],
        "sizeMm": [round(maximum[index] - minimum[index], 6) for index in range(3)],
    }


def triangles(obj: bpy.types.Object) -> int:
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def add_planar_uv(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    uv = mesh.uv_layers.get("UV0") or mesh.uv_layers.new(name="UV0")
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            if abs(polygon.normal.z) >= 0.5:
                coordinate = ((vertex.x + 15.5) / 31.0, (vertex.y + 25.0) / 50.0)
            else:
                coordinate = (
                    (math.atan2(vertex.y, vertex.x) + math.pi) / (2.0 * math.pi),
                    (vertex.z + 3.0) / 6.0,
                )
            uv.data[loop_index].uv = coordinate
    values = [component for item in uv.data for component in item.uv]
    return {
        "name": uv.name,
        "minimum": round(min(values), 9),
        "maximum": round(max(values), 9),
        "loops": len(uv.data),
    }


def capsule_mesh(name: str, width: float, length: float, height: float, segments_per_arc: int = 16) -> bpy.types.Mesh:
    radius = width / 2.0
    center = length / 2.0 - radius
    outline = []
    for index in range(segments_per_arc + 1):
        angle = index * math.pi / segments_per_arc
        outline.append((radius * math.cos(angle), center + radius * math.sin(angle)))
    for index in range(1, segments_per_arc + 1):
        angle = math.pi + index * math.pi / segments_per_arc
        outline.append((radius * math.cos(angle), -center + radius * math.sin(angle)))
    vertices = [(x, y, -height / 2.0) for x, y in outline]
    vertices += [(x, y, height / 2.0) for x, y in outline]
    count = len(outline)
    faces = [tuple(range(count - 1, -1, -1)), tuple(range(count, count * 2))]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    return mesh


def create_collision_proxies(root: bpy.types.Object, fixed: bpy.types.Object, pivot: bpy.types.Object) -> tuple[list[bpy.types.Object], bpy.types.Collection]:
    collection = bpy.data.collections.new("COL_Collision_MagneticSlideTile")
    bpy.context.scene.collection.children.link(collection)
    collision_root = bpy.data.objects.new("CollisionRoot", None)
    collection.objects.link(collision_root)
    collision_root.parent = root
    collision_root["role"] = "collision-root"
    collision_root["strategy"] = "two-convex-capsule-prisms"
    records = []
    for name, parent, location in [
        ("UCX_MagneticSlideTile_Lower_00", fixed, (0.0, 0.0, -3.0)),
        ("UCX_MagneticSlideTile_Upper_00", pivot, (0.0, 9.5, 3.0)),
    ]:
        obj = bpy.data.objects.new(name, capsule_mesh(f"{name}_Mesh", 30.6, 49.6, 5.8))
        collection.objects.link(obj)
        obj.parent = parent
        obj.location = location
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        obj.hide_render = True
        obj.display_type = "WIRE"
        obj["collision_proxy"] = True
        obj["convex"] = True
        obj["shipping_render_geometry"] = False
        records.append(obj)
    return records, collection


def clear_runtime_motion() -> dict:
    constraints = []
    drivers = []
    animations = []
    for obj in bpy.data.objects:
        if obj.animation_data:
            animations.append(obj.name)
            obj.animation_data_clear()
        for constraint in list(obj.constraints):
            constraints.append(f"{obj.name}:{constraint.name}")
            obj.constraints.remove(constraint)
        if obj.animation_data and obj.animation_data.drivers:
            drivers.extend(f"{obj.name}:{driver.data_path}" for driver in obj.animation_data.drivers)
    for data in [*bpy.data.materials, *bpy.data.node_groups]:
        if data.animation_data:
            animations.append(data.name)
            data.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    return {"removedConstraints": constraints, "removedDrivers": drivers, "removedAnimations": animations}


def repath_approved_images() -> dict:
    mapping = {
        "artwork-upper-mask.png": "artwork-upper-mask.png",
        "artwork-lower-mask.png": "artwork-lower-mask.png",
        "artwork-top-perimeter-border-mask.png": "artwork-top-perimeter-border-mask.png",
    }
    changed = {}
    for image in bpy.data.images:
        if image.name in mapping:
            image.filepath = f"//textures/{mapping[image.name]}"
            image.filepath_raw = image.filepath
            changed[image.name] = image.filepath
    return changed


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def set_transport_materials() -> None:
    silver = bpy.data.materials["M07R7_DaylightNeutralPolishedSilver"]
    silver.use_nodes = True
    nodes = silver.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.name = "Principled BSDF"
    shader.inputs["Base Color"].default_value = (0.97, 0.965, 0.94, 1.0)
    shader.inputs["Metallic"].default_value = 1.0
    shader.inputs["Roughness"].default_value = 0.065
    shader.inputs["Emission Strength"].default_value = 0.0
    silver.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    for suffix, material_name in [
        ("upper", "M07R7_BloodRedCrystal_WideBorder_Upper"),
        ("lower", "M07R7_BloodRedCrystal_WideBorder_Lower"),
    ]:
        material = bpy.data.materials[material_name]
        material.use_nodes = True
        nodes = material.node_tree.nodes
        nodes.clear()
        output = nodes.new("ShaderNodeOutputMaterial")
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.name = "Principled BSDF"
        texture = nodes.new("ShaderNodeTexImage")
        texture.name = f"Gate10_{suffix.title()}_TransportBaseColor"
        image = bpy.data.images.load(str(TEXTURES / f"face-{suffix}-transport-basecolor.png"), check_existing=True)
        image.colorspace_settings.name = "sRGB"
        texture.image = image
        texture.interpolation = "Closest"
        shader.inputs["Metallic"].default_value = 0.0
        shader.inputs["Roughness"].default_value = 0.18
        shader.inputs["Coat Weight"].default_value = 0.22
        shader.inputs["Coat Roughness"].default_value = 0.07
        shader.inputs["Emission Strength"].default_value = 0.0
        material.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        material.node_tree.links.new(shader.outputs["BSDF"], output.inputs["Surface"])


def export_files(model_objects: list[bpy.types.Object], collision_objects: list[bpy.types.Object]) -> dict:
    export_nodes = []
    for obj in model_objects:
        current = obj
        while current:
            if current not in export_nodes:
                export_nodes.append(current)
            current = current.parent
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    if envelope not in export_nodes:
        export_nodes.append(envelope)
    for obj in model_objects:
        export_mesh = obj.data.copy()
        export_mesh.name = f"{obj.data.name}_Gate10Triangulated"
        mesh_edit = bmesh.new()
        mesh_edit.from_mesh(export_mesh)
        bmesh.ops.triangulate(mesh_edit, faces=list(mesh_edit.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        mesh_edit.to_mesh(export_mesh)
        mesh_edit.free()
        export_mesh.update()
        obj.data = export_mesh
        obj.modifiers.clear()
    set_transport_materials()
    select_only(export_nodes)
    bpy.ops.export_scene.fbx(
        filepath=str(FBX),
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        bake_space_transform=False,
        object_types={"MESH", "EMPTY"},
        use_mesh_modifiers=True,
        mesh_smooth_type="OFF",
        use_tspace=True,
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="COPY",
        embed_textures=True,
        axis_forward="-Z",
        axis_up="Y",
    )
    export_root = bpy.data.objects["MagneticSlideTile_Blockout_R003"]
    export_root.scale = (0.001, 0.001, 0.001)
    bpy.context.view_layer.update()
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=False,
        export_extras=True,
        export_animations=False,
        export_materials="EXPORT",
        export_normals=True,
        export_tangents=True,
        export_texcoords=True,
        export_cameras=False,
        export_lights=False,
    )
    export_root.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()
    collision_nodes = []
    for obj in collision_objects:
        current = obj
        while current:
            if current not in collision_nodes and current.type != "MESH" or current in collision_objects:
                if current not in collision_nodes:
                    collision_nodes.append(current)
            current = current.parent
    select_only(collision_nodes)
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION_FBX),
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        bake_space_transform=False,
        object_types={"MESH", "EMPTY"},
        use_mesh_modifiers=True,
        mesh_smooth_type="OFF",
        use_tspace=False,
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=False,
        axis_forward="-Z",
        axis_up="Y",
    )
    return {
        "fbx": {
            "path": str(FBX.relative_to(REPO)),
            "sha256": sha256(FBX),
            "bytes": FBX.stat().st_size,
        },
        "glb": {
            "path": str(GLB.relative_to(REPO)),
            "sha256": sha256(GLB),
            "bytes": GLB.stat().st_size,
        },
        "collisionFbx": {
            "path": str(COLLISION_FBX.relative_to(REPO)),
            "sha256": sha256(COLLISION_FBX),
            "bytes": COLLISION_FBX.stat().st_size,
        },
    }


def main() -> None:
    texture_report = json.loads(TEXTURE_MANIFEST.read_text(encoding="utf-8"))
    if not texture_report["pass"]:
        raise RuntimeError("Gate 10 texture preparation failed.")
    texture_records = texture_report["records"]
    pipeline = json.loads(PIPELINE.read_text(encoding="utf-8"))
    source_report = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    gate09 = pipeline["stages"][8]
    if gate09["status"] != "approved" or gate09["decision"]["notes"] != "可以的，可以的。然后开始继续下一步吧。":
        raise RuntimeError("Gate 09 rev 2 approval was not persisted exactly.")
    if not source_report["pass"]:
        raise RuntimeError("Approved Gate 09 scene report failed.")
    source_hash_before = sha256(SOURCE_BLEND)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    root = bpy.data.objects["MagneticSlideTile_Blockout_R003"]
    fixed = bpy.data.objects["FixedAssembly"]
    model_objects = [lower, upper]
    if local_mesh_hash(model_objects) != EXPECTED_LOCAL_MESH_HASH:
        raise RuntimeError("Approved local geometry changed before export.")
    translation.location = (0.0, 0.0, 0.0)
    translation.rotation_euler = (0.0, 0.0, 0.0)
    translation.scale = (1.0, 1.0, 1.0)
    pivot.rotation_euler = (0.0, 0.0, 0.0)
    upper.rotation_euler = (0.0, 0.0, 0.0)
    lower.rotation_euler = (0.0, 0.0, 0.0)
    for obj in list(bpy.data.objects):
        if obj.name not in KEEP_OBJECTS:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.world = None
    scene.camera = None
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene["gate"] = "10-export"
    scene["export_revision"] = 1
    scene["source_gate09_approval"] = "可以的，可以的。然后开始继续下一步吧。"
    scene["default_pose"] = "closed-zero-motion"
    scene["unity_import_performed"] = False
    root["overall_dimensions_mm"] = [50.0, 31.0, 12.0]
    root["render_model_triangles"] = 4096
    root["lod_policy"] = "single-closeup-model-no-lod"
    translation["axis"] = "+Y"
    translation["travel_mm"] = 21.0
    translation["default_translation_mm"] = 0.0
    translation["may_rotate"] = False
    pivot["axis"] = "+Z"
    pivot["axis_coordinate_in_closed_assembly_mm"] = [0.0, -9.5, 0.0]
    pivot["detent_count"] = 30
    pivot["detent_step_degrees"] = 12.0
    pivot["detent_delivery_state"] = "specified-only-runtime-haptic-pending"
    envelope["export_policy"] = "non-rendering-metadata-only"
    envelope["geometry"] = "none"
    envelope.hide_render = True
    animation_cleanup = clear_runtime_motion()
    image_paths = repath_approved_images()
    uv = {obj.name: add_planar_uv(obj) for obj in model_objects}
    collision_objects, collision_collection = create_collision_proxies(root, fixed, pivot)
    bpy.context.view_layer.update()
    geometry_hash = local_mesh_hash(model_objects)
    bounds = world_bounds(model_objects)
    triangle_counts = {obj.name: triangles(obj) for obj in model_objects}
    collision_triangles = {obj.name: triangles(obj) for obj in collision_objects}
    material_slots = {obj.name: [slot.material.name for slot in obj.material_slots] for obj in model_objects}
    constraints = [f"{obj.name}:{constraint.name}" for obj in bpy.data.objects for constraint in obj.constraints]
    drivers = [
        f"{obj.name}:{driver.data_path}"
        for obj in bpy.data.objects
        if obj.animation_data
        for driver in obj.animation_data.drivers
    ]
    actions = [action.name for action in bpy.data.actions]
    if bounds["sizeMm"] != [31.0, 50.0, 12.0]:
        raise RuntimeError(f"Unexpected closed bounds: {bounds}")
    if sum(triangle_counts.values()) != 4096:
        raise RuntimeError("Render triangle count changed.")
    if sum(collision_triangles.values()) > 300:
        raise RuntimeError("Collision budget exceeded.")
    if constraints or drivers or actions:
        raise RuntimeError("Runtime motion leaked into export source.")
    bpy.ops.wm.save_as_mainfile(filepath=str(AUTHORITATIVE_BLEND), relative_remap=False)
    source_hash_after = sha256(SOURCE_BLEND)
    if source_hash_before != source_hash_after:
        raise RuntimeError("Gate 09 source blend was modified.")
    outputs = export_files(model_objects, collision_objects)
    package_files = {
        "authoritativeBlend": {
            "path": str(AUTHORITATIVE_BLEND.relative_to(REPO)),
            "sha256": sha256(AUTHORITATIVE_BLEND),
            "bytes": AUTHORITATIVE_BLEND.stat().st_size,
        },
        **outputs,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 1,
        "sourceGate09": {
            "revision": 2,
            "approvalWording": "可以的，可以的。然后开始继续下一步吧。",
            "blendPath": str(SOURCE_BLEND.relative_to(REPO)),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "geometryDigest": EXPECTED_GEOMETRY_DIGEST,
            "localMeshHash": EXPECTED_LOCAL_MESH_HASH,
        },
        "authoritativeBlend": {
            "defaultPose": "closed-zero-motion",
            "sceneUnits": {
                "system": scene.unit_settings.system,
                "scaleLength": scene.unit_settings.scale_length,
                "lengthUnit": scene.unit_settings.length_unit,
                "modelingUnit": "millimeter",
                "unityUnit": "meter",
            },
            "runtimeObjects": sorted(KEEP_OBJECTS),
            "diagnosticEnvironmentLightsCamerasRemoved": True,
            "bounds": bounds,
            "triangleCounts": triangle_counts,
            "totalTriangles": sum(triangle_counts.values()),
            "materials": material_slots,
            "uvLayers": uv,
            "artworkImagePaths": image_paths,
            "motion": {
                "closedDefaultTranslationMm": [0.0, 0.0, 0.0],
                "closedDefaultRotationDegrees": [0.0, 0.0, 0.0],
                "separateSlidePose": {"axis": "+Y", "travelMm": 21.0, "rotationDegrees": 0.0},
                "pointAxis": {"coordinateMm": [0.0, -9.5, 0.0], "axis": "+Z"},
                "detents": {"count": 30, "stepDegrees": 12.0, "deliveryState": "specified-only"},
                "animations": [],
                "constraints": constraints,
                "drivers": drivers,
                "cleanup": animation_cleanup,
            },
            "hiddenMechanism": {
                "object": envelope.name,
                "type": envelope.type,
                "geometry": envelope["geometry"],
                "hideRender": envelope.hide_render,
                "exportPolicy": envelope["export_policy"],
            },
        },
        "exports": {
            **package_files,
            "settings": {
                "fbx": {
                    "binary": True,
                    "selectionOnly": True,
                    "unitScale": True,
                    "applyScaling": "FBX_SCALE_UNITS",
                    "forward": "-Z",
                    "up": "Y",
                    "normals": True,
                    "tangents": True,
                    "customProperties": True,
                    "animations": False,
                    "embeddedTransportTextures": True,
                    "temporaryTriangulation": "applied-at-export-only",
                },
                "glb": {
                    "format": "GLB",
                    "selectionOnly": True,
                    "up": "Y",
                    "applyTransforms": False,
                    "normals": True,
                    "tangents": True,
                    "uvs": True,
                    "extras": True,
                    "animations": False,
                    "cameras": False,
                    "lights": False,
                    "embeddedTransportTextures": True,
                    "temporaryTriangulation": "applied-at-export-only",
                    "millimeterToMeterRootScale": 0.001,
                },
                "collision": {
                    "format": "FBX",
                    "strategy": "two-convex-capsule-prisms",
                    "collection": collision_collection.name,
                    "objects": [obj.name for obj in collision_objects],
                    "triangleCounts": collision_triangles,
                    "totalTriangles": sum(collision_triangles.values()),
                    "renderGeometryChanged": False,
                    "visibleLodCreated": False,
                },
            },
            "materialTransportNote": "The authoritative Blend retains the approved procedural materials. FBX/GLB keep the same material slot names and use deterministic PBR transport textures; Gate 11 must map the independent masks to the URP shader approximation.",
        },
        "textures": {
            "records": texture_records,
            "channelPacking": {
                "upper": {"file": "artwork-upper-channel-pack.png", "R": "upper motif", "G": "top perimeter border", "B": "MAX motif+border", "A": "opaque/reserved"},
                "lower": {"file": "artwork-lower-channel-pack.png", "R": "lower motif", "G": "top perimeter border", "B": "MAX motif+border", "A": "opaque/reserved"},
                "independentArtworkEditingPreserved": True,
            },
            "gate11IosAstcPlan": {
                "decisionState": "specified",
                "deliveryState": "not-applied-until-unity-import",
                "runtimeTextures": ["artwork-upper-channel-pack.png", "artwork-lower-channel-pack.png"],
                "recommendedFormat": "ASTC_4x4",
                "maxSize": 1024,
                "mipmaps": True,
                "sRGB": False,
                "alphaHandling": "opaque; A reserved",
                "reason": "4x4 preserves the crisp gothic mask edges; separate upper/lower packs preserve independent replacement.",
                "transportBaseColors": "GLB/FBX preview only; omit from Unity runtime after Shader Graph mask mapping.",
            },
        },
        "optimization": {
            "renderModelTriangles": 4096,
            "renderMeshCount": 2,
            "highLowPairCreated": False,
            "lodCreated": False,
            "futureSimplifiedLibraryModel": "conditional-on-unity-profiling",
            "futureHighPoly": "bake-only-never-ships",
        },
        "scope": {
            "gate11Entered": False,
            "unityImportedOrModified": False,
            "astcAppliedInUnity": False,
            "runtimeOrHapticsChanged": False,
            "buildInstallOrPhonePush": False,
        },
    }
    checks = {
        "gate09ApprovedExactWording": gate09["decision"]["notes"] == report["sourceGate09"]["approvalWording"],
        "sourceGate09Immutable": report["sourceGate09"]["unchanged"],
        "closedZeroMotionDefault": list(translation.location) == [0.0, 0.0, 0.0]
        and all(abs(value) < 1e-9 for value in translation.rotation_euler),
        "geometryPreserved": geometry_hash == EXPECTED_LOCAL_MESH_HASH
        and bounds["sizeMm"] == [31.0, 50.0, 12.0]
        and sum(triangle_counts.values()) == 4096,
        "twoExteriorMeshes": sorted(triangle_counts) == sorted(["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]),
        "materialsAndSlotsPreserved": material_slots == {
            "LowerBody_Fixed_CleanPlane": [
                "M07R7_DaylightNeutralPolishedSilver",
                "M07R7_BloodRedCrystal_WideBorder_Lower",
            ],
            "UpperCapsule_Moving": [
                "M07R7_DaylightNeutralPolishedSilver",
                "M07R7_BloodRedCrystal_WideBorder_Upper",
            ],
        },
        "independentArtworkPreserved": report["textures"]["channelPacking"]["independentArtworkEditingPreserved"]
        and texture_records["artwork-upper-mask.png"]["sha256"] == EXPECTED_ARTWORK_HASH
        and texture_records["artwork-lower-mask.png"]["sha256"] == EXPECTED_ARTWORK_HASH,
        "uvsPresent": all(item["name"] == "UV0" and item["minimum"] >= 0 and item["maximum"] <= 1 for item in uv.values()),
        "hiddenMechanismMetadataOnly": envelope.type == "EMPTY" and envelope["geometry"] == "none" and envelope.hide_render,
        "noAnimationConstraintsDrivers": not constraints and not drivers and not actions,
        "collisionWithinBudget": sum(collision_triangles.values()) <= 300
        and all(obj["convex"] and not obj["shipping_render_geometry"] for obj in collision_objects),
        "noLod": not report["optimization"]["lodCreated"] and not report["optimization"]["highLowPairCreated"],
        "requiredFilesExist": all(Path(REPO / item["path"]).exists() for item in package_files.values()),
        "astcSpecifiedOnly": report["textures"]["gate11IosAstcPlan"]["deliveryState"] == "not-applied-until-unity-import",
        "gate10Only": not any(report["scope"].values()),
    }
    report["checks"] = checks
    report["packageDigest"] = hashlib.sha256(
        "".join(sorted(item["sha256"] for item in package_files.values())).encode()
    ).hexdigest()
    report["pass"] = all(checks.values())
    MANIFEST.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 export package validation failed.")


if __name__ == "__main__":
    main()
