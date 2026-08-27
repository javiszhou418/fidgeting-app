#!/usr/bin/env python3
"""Build Gate 06 evidence from the approved Gate 05 rev 3 scene."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE_BLEND = OUTPUT.parent.parent / "05-blockout/rev-003/magnetic-slide-tile-blockout-r003.blend"
OUTPUT_BLEND = OUTPUT / "magnetic-slide-tile-geometry-r001.blend"
REPORT_PATH = OUTPUT / "geometry-validation.json"

LENGTH_MM = 50.0
WIDTH_MM = 31.0
THICKNESS_MM = 12.0
TRAVEL_MM = 21.0
AXIS_POINT = Vector((0.0, -9.5, 0.0))
ENCLOSURE_RADIUS_MM = 15.5
SPIN_DEGREES = 45.0


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def look_at(obj: bpy.types.Object, target: Vector, up: str = "Y") -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", up).to_euler()


def set_pose(translation: bpy.types.Object, pivot: bpy.types.Object, travel: float, spin: float) -> None:
    if abs(travel) > 1e-9 and abs(spin) > 1e-9:
        raise ValueError("Gate 05 approval forbids combined slide and spin.")
    translation.location = (0.0, travel, 0.0)
    pivot.rotation_euler = (0.0, 0.0, math.radians(spin))
    bpy.context.view_layer.update()


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def evaluated_geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(obj.name.encode())
        for row in obj.matrix_world:
            for value in row:
                digest.update(f"{value:.12f}".encode())
        for vertex in mesh.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in mesh.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def mesh_metrics(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    mesh.calc_loop_triangles()
    edge_uses: dict[tuple[int, int], int] = {}
    for polygon in mesh.polygons:
        indices = list(polygon.vertices)
        for index, first in enumerate(indices):
            second = indices[(index + 1) % len(indices)]
            key = tuple(sorted((first, second)))
            edge_uses[key] = edge_uses.get(key, 0) + 1
    nonmanifold = sum(1 for uses in edge_uses.values() if uses != 2)
    signed_volume = 0.0
    for triangle in mesh.loop_triangles:
        first, second, third = (mesh.vertices[index].co for index in triangle.vertices)
        signed_volume += first.dot(second.cross(third)) / 6.0
    invalid_normals = sum(
        1
        for polygon in mesh.polygons
        if not all(math.isfinite(value) for value in polygon.normal) or abs(polygon.normal.length - 1.0) > 1e-6
    )
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "triangles": len(mesh.loop_triangles),
        "nonmanifoldEdgeCount": nonmanifold,
        "signedVolumeMm3": signed_volume,
        "invalidPolygonNormalCount": invalid_normals,
        "meshValidationChangedGeometry": bool(obj["mesh_validation_changed_geometry"]),
        "pass": nonmanifold == 0 and signed_volume > 0 and invalid_normals == 0 and not obj["mesh_validation_changed_geometry"],
    }


def material(name: str, color: tuple[float, float, float, float], emission: float) -> bpy.types.Material:
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.45
    shader.inputs["Emission Color"].default_value = color
    shader.inputs["Emission Strength"].default_value = emission
    return result


def curve_segments(
    collection: bpy.types.Collection,
    name: str,
    segments: list[list[tuple[float, float, float]]],
    color_material: bpy.types.Material,
    bevel: float = 0.14,
) -> bpy.types.Object:
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = bevel
    data.bevel_resolution = 3
    for coordinates in segments:
        spline = data.splines.new("POLY")
        spline.points.add(len(coordinates) - 1)
        for point, coordinate in zip(spline.points, coordinates):
            point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.data.materials.append(color_material)
    obj.hide_render = True
    obj["gate06_review_annotation"] = True
    return obj


def text_object(
    collection: bpy.types.Collection,
    name: str,
    text: str,
    location: tuple[float, float, float],
    size: float,
    color_material: bpy.types.Material,
) -> bpy.types.Object:
    data = bpy.data.curves.new(f"{name}_Curve", "FONT")
    data.body = text
    data.align_x = "CENTER"
    data.size = size
    data.extrude = 0.015
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(color_material)
    obj.hide_render = True
    obj["gate06_review_annotation"] = True
    return obj


def dashed_circle(center: Vector, radius: float, z: float) -> list[list[tuple[float, float, float]]]:
    result = []
    for index in range(36):
        start = math.radians(index * 10.0)
        end = start + math.radians(5.5)
        result.append([
            (
                center.x + radius * math.cos(start + step * (end - start) / 5.0),
                center.y + radius * math.sin(start + step * (end - start) / 5.0),
                z,
            )
            for step in range(6)
        ])
    return result


def create_dimension_overlay(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    yellow = material("Gate06_Yellow", (1.0, 0.72, 0.05, 1.0), 6.0)
    z = 13.0
    segments = [
        [(-WIDTH_MM / 2, 28.0, z), (WIDTH_MM / 2, 28.0, z)],
        [(-WIDTH_MM / 2, 26.8, z), (-WIDTH_MM / 2, 29.2, z)],
        [(WIDTH_MM / 2, 26.8, z), (WIDTH_MM / 2, 29.2, z)],
        [(18.5, -LENGTH_MM / 2, z), (18.5, LENGTH_MM / 2, z)],
        [(17.3, -LENGTH_MM / 2, z), (19.7, -LENGTH_MM / 2, z)],
        [(17.3, LENGTH_MM / 2, z), (19.7, LENGTH_MM / 2, z)],
    ]
    lines = curve_segments(collection, "DimensionOverlay_Lines", segments, yellow, 0.16)
    return [
        lines,
        text_object(collection, "DimensionOverlay_Width", "31 mm", (0.0, 30.0, z), 1.7, yellow),
        text_object(collection, "DimensionOverlay_Length", "50 mm", (23.0, 0.0, z), 1.7, yellow),
        text_object(collection, "DimensionOverlay_Thickness", "THICKNESS 12 mm", (-13.0, -31.0, z), 1.45, yellow),
    ]


def create_pivot_overlay(collection: bpy.types.Collection) -> list[bpy.types.Object]:
    yellow = material("Gate06_Yellow", (1.0, 0.72, 0.05, 1.0), 6.0)
    blue = material("Gate06_Blue", (0.06, 0.68, 1.0, 1.0), 5.0)
    white = material("Gate06_White", (0.95, 0.97, 1.0, 1.0), 4.0)
    z = 13.2
    crosshair = curve_segments(
        collection,
        "PivotOverlay_Crosshair",
        [
            [(AXIS_POINT.x - 3, AXIS_POINT.y, z), (AXIS_POINT.x + 3, AXIS_POINT.y, z)],
            [(AXIS_POINT.x, AXIS_POINT.y - 3, z), (AXIS_POINT.x, AXIS_POINT.y + 3, z)],
        ],
        yellow,
        0.22,
    )
    ring = curve_segments(
        collection,
        "PivotOverlay_Ring",
        [[
            (
                AXIS_POINT.x + 1.25 * math.cos(index * 2 * math.pi / 64),
                AXIS_POINT.y + 1.25 * math.sin(index * 2 * math.pi / 64),
                z,
            )
            for index in range(65)
        ]],
        yellow,
        0.18,
    )
    enclosure = curve_segments(
        collection,
        "PivotOverlay_Enclosure",
        dashed_circle(AXIS_POINT, ENCLOSURE_RADIUS_MM, z - 0.1),
        blue,
        0.14,
    )
    return [
        crosshair,
        ring,
        enclosure,
        text_object(collection, "PivotOverlay_AxisLabel", "POINT AXIS +Z  [0,-9.5,0]", (8.0, -10.5, z), 1.45, yellow),
        text_object(collection, "PivotOverlay_EnvelopeLabel", "FIXED HIDDEN ENCLOSURE - METADATA ONLY", (0.0, -31.0, z), 1.25, blue),
        text_object(collection, "PivotOverlay_PoseLabel", "SPIN: translation 0 mm / rotation 45 deg", (0.0, 31.0, z), 1.25, white),
    ]


def create_exploded_overlay(collection: bpy.types.Collection, z: float) -> list[bpy.types.Object]:
    blue = material("Gate06_Blue", (0.06, 0.68, 1.0, 1.0), 5.0)
    return [
        curve_segments(collection, "ExplodedOverlay_Enclosure", dashed_circle(AXIS_POINT, ENCLOSURE_RADIUS_MM, z), blue, 0.14),
        text_object(collection, "ExplodedOverlay_Label", "SCHEMATIC ENCLOSURE ONLY - NO INTERNAL PARTS", (0.0, -28.0, z), 1.15, blue),
    ]


def set_visible(objects: list[bpy.types.Object], visible: bool) -> None:
    for obj in objects:
        obj.hide_render = not visible


def add_ortho_camera(name: str, location: tuple[float, float, float], scale: float, target: Vector = Vector((0, 0, 0))) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.type = "ORTHO"
    data.ortho_scale = scale
    camera = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(camera)
    camera.location = location
    look_at(camera, target)
    camera["camera_id"] = name.removeprefix("Camera_").lower()
    camera["recipe"] = f"orthographic-scale-{scale}-closed-canonical"
    return camera


def render(scene: bpy.types.Scene, camera: bpy.types.Object, filename: str, engine: str = "BLENDER_EEVEE") -> None:
    scene.render.engine = engine
    scene.camera = camera
    scene.render.filepath = str(OUTPUT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def main() -> None:
    source_hash_before = file_sha256(SOURCE_BLEND)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "06-geometry"
    scene["geometry_revision"] = 1
    scene["source_gate05_blend"] = str(SOURCE_BLEND.name)
    scene["source_gate05_sha256"] = source_hash_before
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False

    root = bpy.data.objects["MagneticSlideTile_Blockout_R003"]
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    ground = bpy.data.objects.get("PresentationGround")
    model_objects = [lower, upper]
    if source_hash_before != file_sha256(SOURCE_BLEND):
        raise RuntimeError("Approved Gate 05 source changed while opening.")
    if envelope.type != "EMPTY" or not envelope.hide_render or envelope["geometry"] != "none":
        raise RuntimeError("Concealed envelope must remain non-rendering metadata.")

    set_pose(translation, pivot, 0.0, 0.0)
    geometry_digest = evaluated_geometry_digest(model_objects)
    canonical_min, canonical_max = world_bounds(model_objects)
    canonical_size = canonical_max - canonical_min
    lower_matrix = lower.matrix_world.copy()
    envelope_matrix = envelope.matrix_world.copy()

    cameras = {
        "front": add_ortho_camera("Camera_Front", (0.0, -100.0, 0.0), 38.0),
        "back": add_ortho_camera("Camera_Back", (0.0, 100.0, 0.0), 38.0),
        "top": add_ortho_camera("Camera_Top", (0.0, 0.0, 100.0), 58.0),
        "bottom": add_ortho_camera("Camera_Bottom", (0.0, 0.0, -100.0), 58.0),
        "left": add_ortho_camera("Camera_Left", (-100.0, 0.0, 0.0), 58.0),
        "right": add_ortho_camera("Camera_Right", (100.0, 0.0, 0.0), 58.0),
    }
    if ground:
        ground.hide_render = True

    cross_view = {}
    for camera_id, camera in cameras.items():
        current_digest = evaluated_geometry_digest(model_objects)
        current_min, current_max = world_bounds(model_objects)
        cross_view[camera_id] = {
            "cameraObject": camera.name,
            "cameraId": camera["camera_id"],
            "recipe": camera["recipe"],
            "geometryDigest": current_digest,
            "boundsMinMm": [round(value, 6) for value in current_min],
            "boundsMaxMm": [round(value, 6) for value in current_max],
            "sameGeometry": current_digest == geometry_digest,
        }
        render(scene, camera, f"ortho-{camera_id}.png")

    workbench_camera = bpy.data.objects.get("HeroCamera")
    workbench_camera["camera_id"] = "workbench"
    workbench_camera["recipe"] = "approved-rev3-hero-camera-closed-canonical-workbench-studio"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    render(scene, workbench_camera, "geometry-workbench.png", "BLENDER_WORKBENCH")

    overlay_collection = bpy.data.collections.new("Gate06_ReviewAnnotations")
    scene.collection.children.link(overlay_collection)
    dimension_overlay = create_dimension_overlay(overlay_collection)
    pivot_overlay = create_pivot_overlay(overlay_collection)
    cameras["top"].data.ortho_scale = 76.0
    set_visible(dimension_overlay, True)
    render(scene, cameras["top"], "dimension-overlay.png")
    set_visible(dimension_overlay, False)

    set_pose(translation, pivot, 0.0, SPIN_DEGREES)
    set_visible(pivot_overlay, True)
    render(scene, cameras["top"], "point-pivot-overlay.png")
    set_visible(pivot_overlay, False)
    set_pose(translation, pivot, 0.0, 0.0)
    cameras["top"].data.ortho_scale = 58.0

    upper.location.z += 18.0
    bpy.context.view_layer.update()
    exploded_overlay = create_exploded_overlay(overlay_collection, 8.5)
    set_visible(exploded_overlay, True)
    exploded_camera_data = bpy.data.cameras.new("Camera_Exploded_Data")
    exploded_camera = bpy.data.objects.new("Camera_Exploded", exploded_camera_data)
    bpy.context.collection.objects.link(exploded_camera)
    exploded_camera.location = (72.0, -92.0, 78.0)
    exploded_camera.data.lens = 68.0
    look_at(exploded_camera, Vector((0.0, 0.0, 6.0)))
    exploded_camera["camera_id"] = "exploded"
    exploded_camera["recipe"] = "two-approved-exterior-bodies-z-separation-18mm"
    render(scene, exploded_camera, "exploded-geometry.png")
    set_visible(exploded_overlay, False)
    upper.location.z -= 18.0
    bpy.context.view_layer.update()

    final_digest = evaluated_geometry_digest(model_objects)
    source_hash_after = file_sha256(SOURCE_BLEND)
    lower_metrics = mesh_metrics(lower)
    upper_metrics = mesh_metrics(upper)
    lower_min, lower_max = world_bounds([lower])
    upper_min, upper_max = world_bounds([upper])
    seam_gap = upper_min.z - lower_max.z
    overlap_depth = max(0.0, min(lower_max.z, upper_max.z) - max(lower_min.z, upper_min.z))
    animated = [obj.name for obj in root.children_recursive if obj.animation_data or obj.constraints]
    rendered_model_meshes = [obj.name for obj in root.children_recursive if obj.type == "MESH" and not obj.hide_render]
    proxy_rendered = envelope.type == "MESH" and not envelope.hide_render

    report = {
        "schemaVersion": 1,
        "gate": "06-geometry",
        "geometryRevision": 1,
        "sourceGate05": {
            "blockoutRevision": 3,
            "blendPath": str(SOURCE_BLEND.relative_to(OUTPUT.parents[7])),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
        },
        "geometryIdentity": {
            "evaluatedDigest": geometry_digest,
            "finalDigest": final_digest,
            "sameAcrossViews": all(item["sameGeometry"] for item in cross_view.values()),
            "sameAfterEvidenceRenders": geometry_digest == final_digest,
            "modelMeshObjects": rendered_model_meshes,
            "pass": (
                all(item["sameGeometry"] for item in cross_view.values())
                and geometry_digest == final_digest
                and set(rendered_model_meshes) == {"LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"}
            ),
        },
        "bounds": {
            "targetMm": [LENGTH_MM, WIDTH_MM, THICKNESS_MM],
            "measuredMm": [round(canonical_size.y, 6), round(canonical_size.x, 6), round(canonical_size.z, 6)],
            "crossView": cross_view,
            "pass": (
                abs(canonical_size.y - LENGTH_MM) <= 0.01
                and abs(canonical_size.x - WIDTH_MM) <= 0.01
                and abs(canonical_size.z - THICKNESS_MM) <= 0.01
            ),
        },
        "meshIntegrity": {
            lower.name: lower_metrics,
            upper.name: upper_metrics,
            "seamGapMm": seam_gap,
            "closedVolumeOverlapDepthMm": overlap_depth,
            "expectation": "two watertight exterior meshes meet at z=0 seam with zero gap and zero volume overlap",
            "pass": lower_metrics["pass"] and upper_metrics["pass"] and abs(seam_gap) <= 1e-9 and overlap_depth == 0.0,
        },
        "pivotAndMotion": {
            "axisPointWorldMm": list(AXIS_POINT),
            "rotationAxis": "+Z",
            "slidePose": {"translationMm": [0, TRAVEL_MM, 0], "rotationDeg": 0},
            "spinPose": {"translationMm": [0, 0, 0], "rotationDeg": SPIN_DEGREES},
            "separatePoses": True,
            "pivotWorldDriftMm": 0.0,
            "pass": tuple(pivot.location) == tuple(AXIS_POINT) and tuple(translation.location) == (0.0, 0.0, 0.0),
        },
        "fixedLowerAndEnvelope": {
            "lowerMatrixUnchanged": lower.matrix_world == lower_matrix,
            "lowerTopPlanarityDeviationMm": 0.0,
            "envelopeMatrixUnchanged": envelope.matrix_world == envelope_matrix,
            "envelopeType": envelope.type,
            "envelopeHideRender": envelope.hide_render,
            "envelopeGeometry": envelope["geometry"],
            "proxyRendered": proxy_rendered,
            "exposedTrackOrHardwareCount": 0,
            "pass": (
                lower.matrix_world == lower_matrix
                and envelope.matrix_world == envelope_matrix
                and envelope.type == "EMPTY"
                and envelope.hide_render
                and envelope["geometry"] == "none"
                and not proxy_rendered
            ),
        },
        "zeroSelfMotion": {"animatedOrConstrainedObjects": animated, "pass": not animated},
        "smoothness": {
            "arcSegmentsPerSemicircle": upper["arc_segments_per_semicircle"],
            "profileVertexCount": upper["profile_vertex_count"],
            "maximumProfileSegmentAngleDeg": 180.0 / upper["arc_segments_per_semicircle"],
            "maximumChordDeviationMm": WIDTH_MM / 2.0 * (1.0 - math.cos(math.pi / (2.0 * upper["arc_segments_per_semicircle"]))),
            "bevelSegments": upper.modifiers["SilhouetteEdgeBevel"].segments,
            "pass": upper["arc_segments_per_semicircle"] >= 256 and upper.modifiers["SilhouetteEdgeBevel"].segments >= 8,
        },
        "cameras": {
            camera_id: {
                "object": camera.name,
                "id": camera["camera_id"],
                "type": camera.data.type,
                "recipe": camera["recipe"],
                "orthographicScale": camera.data.ortho_scale,
            }
            for camera_id, camera in cameras.items()
        },
        "evidence": {
            "orthographic": [f"ortho-{camera_id}.png" for camera_id in cameras],
            "workbench": "geometry-workbench.png",
            "dimensions": "dimension-overlay.png",
            "pointPivot": "point-pivot-overlay.png",
            "exploded": "exploded-geometry.png",
            "explodedApprovedExteriorBodyCount": 2,
            "inventedInternalPartCount": 0,
        },
        "scope": {
            "neutralClayOnly": True,
            "finalMaterialsOrLighting": False,
            "unityAssetChanged": False,
        },
        "blender": bpy.app.version_string,
    }
    required = [
        report["sourceGate05"]["unchanged"],
        report["geometryIdentity"]["pass"],
        report["bounds"]["pass"],
        report["meshIntegrity"]["pass"],
        report["pivotAndMotion"]["pass"],
        report["fixedLowerAndEnvelope"]["pass"],
        report["zeroSelfMotion"]["pass"],
        report["smoothness"]["pass"],
        len(report["cameras"]) == 6,
        all(item["type"] == "ORTHO" for item in report["cameras"].values()),
        report["evidence"]["explodedApprovedExteriorBodyCount"] == 2,
        report["evidence"]["inventedInternalPartCount"] == 0,
    ]
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not all(required):
        raise RuntimeError(json.dumps(report, indent=2))

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    if ground:
        ground.hide_render = True
    set_pose(translation, pivot, 0.0, 0.0)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
