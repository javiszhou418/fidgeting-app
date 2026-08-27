#!/usr/bin/env python3
"""Build Gate 05 rev 3 with a point pivot distinct from its enclosure."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
BLEND_PATH = OUTPUT / "magnetic-slide-tile-blockout-r003.blend"
REPORT_PATH = OUTPUT / "blockout-validation.json"

LENGTH_MM = 50.0
WIDTH_MM = 31.0
THICKNESS_MM = 12.0
BODY_THICKNESS_MM = 6.0
TRAVEL_MM = 21.0
CAP_RADIUS_MM = WIDTH_MM / 2.0
AXIS_Y_MM = -(LENGTH_MM - WIDTH_MM) / 2.0
AXIS_WORLD_MM = Vector((0.0, AXIS_Y_MM, 0.0))
ARC_SEGMENTS = 256
BEVEL_SEGMENTS = 8
BEVEL_WIDTH_MM = 0.45
SPIN_DEGREES = 45.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], roughness: float, emission: float = 0.0) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    if emission:
        shader.inputs["Emission Color"].default_value = color
        shader.inputs["Emission Strength"].default_value = emission
    return result


def capsule_profile() -> list[tuple[float, float]]:
    straight_half = LENGTH_MM / 2.0 - CAP_RADIUS_MM
    points = []
    for index in range(ARC_SEGMENTS + 1):
        angle = index * math.pi / ARC_SEGMENTS
        points.append((CAP_RADIUS_MM * math.cos(angle), straight_half + CAP_RADIUS_MM * math.sin(angle)))
    for index in range(1, ARC_SEGMENTS + 1):
        angle = math.pi + index * math.pi / ARC_SEGMENTS
        points.append((CAP_RADIUS_MM * math.cos(angle), -straight_half + CAP_RADIUS_MM * math.sin(angle)))
    return points


def capsule_mesh(name: str, z_center: float, clay: bpy.types.Material) -> bpy.types.Object:
    profile = capsule_profile()
    count = len(profile)
    vertices = [(x, y, -BODY_THICKNESS_MM / 2.0) for x, y in profile]
    vertices += [(x, y, BODY_THICKNESS_MM / 2.0) for x, y in profile]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [
        (index, (index + 1) % count, count + (index + 1) % count, count + index)
        for index in range(count)
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    validation_changed = mesh.validate(clean_customdata=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location.z = z_center
    obj.data.materials.append(clay)
    obj["profile_kind"] = "high-resolution-analytic-capsule"
    obj["arc_segments_per_semicircle"] = ARC_SEGMENTS
    obj["profile_vertex_count"] = count
    obj["mesh_validation_changed_geometry"] = validation_changed
    bevel = obj.modifiers.new("SilhouetteEdgeBevel", "BEVEL")
    bevel.width = BEVEL_WIDTH_MM
    bevel.segments = BEVEL_SEGMENTS
    bevel.harden_normals = True
    return obj


def parent(child: bpy.types.Object, parent_object: bpy.types.Object) -> None:
    child.parent = parent_object


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def world_point(obj: bpy.types.Object) -> Vector:
    return obj.matrix_world.translation.copy()


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def matrix_values(matrix: Matrix) -> list[list[float]]:
    return [[round(value, 9) for value in row] for row in matrix]


def set_pose(translation: bpy.types.Object, pivot: bpy.types.Object, travel_mm: float, spin_degrees: float) -> None:
    if abs(travel_mm) > 1e-9 and abs(spin_degrees) > 1e-9:
        raise ValueError("Slide and spin are separate poses; combined motion is forbidden.")
    translation.location = (0.0, travel_mm, 0.0)
    pivot.rotation_euler = (0.0, 0.0, math.radians(spin_degrees))
    bpy.context.view_layer.update()


def pose_state(
    name: str,
    translation: bpy.types.Object,
    pivot: bpy.types.Object,
    upper: bpy.types.Object,
    lower: bpy.types.Object,
) -> dict:
    return {
        "name": name,
        "translationMm": [round(value, 9) for value in translation.location],
        "pivotRotationDeg": round(math.degrees(pivot.rotation_euler.z), 9),
        "pivotWorldMm": [round(value, 9) for value in world_point(pivot)],
        "upperOriginWorldMm": [round(value, 9) for value in world_point(upper)],
        "lowerMatrixWorld": matrix_values(lower.matrix_world),
    }


def render(scene: bpy.types.Scene, output: str, camera: bpy.types.Object) -> None:
    scene.camera = camera
    scene.render.filepath = str(OUTPUT / output)
    bpy.ops.render.render(write_still=True)


def curve_segments(
    name: str,
    segments: list[list[tuple[float, float, float]]],
    bevel_depth: float,
    overlay_material: bpy.types.Material,
) -> bpy.types.Object:
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = bevel_depth
    data.bevel_resolution = 3
    for points in segments:
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, coordinate in zip(spline.points, points):
            point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(overlay_material)
    obj.hide_render = True
    obj["review_overlay_only"] = True
    return obj


def create_overlay(pivot_world: Vector) -> list[bpy.types.Object]:
    blue = material("OverlayBlue", (0.06, 0.68, 1.0, 1.0), 0.35, 5.0)
    yellow = material("OverlayYellow", (1.0, 0.72, 0.05, 1.0), 0.3, 7.0)
    white = material("OverlayWhite", (0.95, 0.97, 1.0, 1.0), 0.5, 4.0)
    z = THICKNESS_MM + 1.2
    dash_segments = []
    for index in range(36):
        start = math.radians(index * 10.0)
        end = start + math.radians(5.5)
        dash_segments.append([
            (
                pivot_world.x + CAP_RADIUS_MM * math.cos(start + step * (end - start) / 5.0),
                pivot_world.y + CAP_RADIUS_MM * math.sin(start + step * (end - start) / 5.0),
                z,
            )
            for step in range(6)
        ])
    envelope = curve_segments("Review_Envelope_Dashed", dash_segments, 0.16, blue)
    crosshair = curve_segments(
        "Review_PointAxis_Crosshair",
        [
            [(pivot_world.x - 2.8, pivot_world.y, z + 0.1), (pivot_world.x + 2.8, pivot_world.y, z + 0.1)],
            [(pivot_world.x, pivot_world.y - 2.8, z + 0.1), (pivot_world.x, pivot_world.y + 2.8, z + 0.1)],
        ],
        0.22,
        yellow,
    )
    ring_points = [
        (
            pivot_world.x + 1.25 * math.cos(index * 2.0 * math.pi / 64.0),
            pivot_world.y + 1.25 * math.sin(index * 2.0 * math.pi / 64.0),
            z + 0.1,
        )
        for index in range(65)
    ]
    ring = curve_segments("Review_PointAxis_Ring", [ring_points], 0.19, yellow)
    labels = []
    for name, text, location, size, label_material in [
        ("Review_Label_PointAxis", "POINT AXIS +Z", (2.4, AXIS_Y_MM - 1.0, z + 0.1), 1.8, yellow),
        ("Review_Label_Envelope", "FIXED HIDDEN ENCLOSURE - NOT A ROTATING PART", (-22.0, AXIS_Y_MM - 20.0, z + 0.1), 1.35, blue),
        ("Review_Label_State", "SPIN POSE: TRANSLATION = 0 mm", (-22.0, AXIS_Y_MM + 20.0, z + 0.1), 1.35, white),
    ]:
        data = bpy.data.curves.new(f"{name}_Curve", "FONT")
        data.body = text
        data.align_x = "LEFT"
        data.size = size
        data.extrude = 0.02
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        obj.data.materials.append(label_material)
        obj.hide_render = True
        obj["review_overlay_only"] = True
        labels.append(obj)
    return [envelope, crosshair, ring, *labels]


def top_planarity_mm(obj: bpy.types.Object) -> float:
    top = max(vertex.co.z for vertex in obj.data.vertices)
    values = [vertex.co.z for vertex in obj.data.vertices if abs(vertex.co.z - top) < 1e-9]
    return max(values) - min(values)


def main() -> None:
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.055, 0.065, 0.078)
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene["gate"] = "05-blockout"
    scene["blockout_revision"] = 3
    scene["closed_assembly_origin_mm"] = [0.0, 0.0, 0.0]
    scene["point_axis_world_mm"] = list(AXIS_WORLD_MM)
    scene["point_axis_basis"] = "trailing-rounded-end-center-under-provisional-capsule"
    scene["pose_rule"] = "slide-and-spin-mutually-exclusive"

    fixed_clay = material("WhiteClay_Fixed", (0.72, 0.76, 0.80, 1.0), 0.72)
    moving_clay = material("WhiteClay_Moving", (0.96, 0.97, 0.98, 1.0), 0.62)

    root = bpy.data.objects.new("MagneticSlideTile_Blockout_R003", None)
    bpy.context.collection.objects.link(root)
    root["origin_role"] = "closed-assembly-center"
    root["overall_dimensions_mm"] = [LENGTH_MM, WIDTH_MM, THICKNESS_MM]

    fixed = bpy.data.objects.new("FixedAssembly", None)
    bpy.context.collection.objects.link(fixed)
    parent(fixed, root)

    lower = capsule_mesh("LowerBody_Fixed_CleanPlane", -BODY_THICKNESS_MM / 2.0, fixed_clay)
    lower["role"] = "fixed-lower-exterior-clean-flat-top"
    parent(lower, fixed)

    envelope = bpy.data.objects.new("ConcealedCircularEnvelope_Metadata", None)
    bpy.context.collection.objects.link(envelope)
    envelope.location = AXIS_WORLD_MM
    envelope.empty_display_type = "CIRCLE"
    envelope.empty_display_size = CAP_RADIUS_MM
    envelope.hide_render = True
    envelope["role"] = "fixed-non-rendering-enclosure-evidence-metadata"
    envelope["rotating_object"] = False
    envelope["geometry"] = "none"
    parent(envelope, fixed)

    translation = bpy.data.objects.new("UpperTranslation", None)
    bpy.context.collection.objects.link(translation)
    translation["axis"] = "+Y"
    translation["travel_mm"] = TRAVEL_MM
    translation["may_rotate"] = False
    parent(translation, root)

    pivot = bpy.data.objects.new("CentralAxisPivot_Point", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = AXIS_WORLD_MM
    pivot.empty_display_type = "ARROWS"
    pivot.empty_display_size = 2.2
    pivot.hide_render = True
    pivot["role"] = "single-point-plus-z-rotation-axis"
    pivot["axis"] = "+Z"
    pivot["axis_coordinate_in_closed_assembly_mm"] = list(AXIS_WORLD_MM)
    pivot["may_translate_directly"] = False
    parent(pivot, translation)

    upper = capsule_mesh("UpperCapsule_Moving", BODY_THICKNESS_MM / 2.0, moving_clay)
    upper.location.y = -AXIS_Y_MM
    upper["role"] = "upper-exterior-translates-or-spins-in-separate-poses"
    upper["local_offset_from_point_axis_mm"] = [0.0, -AXIS_Y_MM, BODY_THICKNESS_MM / 2.0]
    parent(upper, pivot)

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 8.0, -6.8))
    ground = bpy.context.object
    ground.name = "PresentationGround"
    ground.data.materials.append(material("Ground", (0.075, 0.090, 0.108, 1.0), 0.86))

    for name, location, energy, size in [
        ("KeyLight", (45.0, -35.0, 70.0), 55000.0, 52.0),
        ("FillLight", (-48.0, -5.0, 38.0), 32000.0, 46.0),
        ("RimLight", (0.0, 65.0, 55.0), 42000.0, 38.0),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.size = size
        look_at(light, Vector((0.0, 5.0, 0.0)))

    bpy.ops.object.camera_add(location=(72.0, -86.0, 68.0))
    hero_camera = bpy.context.object
    hero_camera.name = "HeroCamera"
    hero_camera.data.lens = 72.0
    look_at(hero_camera, Vector((0.0, 7.0, 0.0)))
    bpy.ops.object.camera_add(location=(0.0, -92.0, 92.0))
    slide_camera = bpy.context.object
    slide_camera.name = "SlideCamera"
    slide_camera.data.lens = 78.0
    look_at(slide_camera, Vector((0.0, 8.0, 0.0)))
    bpy.ops.object.camera_add(location=(0.0, 0.0, 100.0), rotation=(0.0, 0.0, 0.0))
    top_camera = bpy.context.object
    top_camera.name = "TopCamera"
    top_camera.data.type = "ORTHO"
    top_camera.data.ortho_scale = 70.0

    set_pose(translation, pivot, 0.0, 0.0)
    closed_lower_matrix = lower.matrix_world.copy()
    closed_state = pose_state("closed", translation, pivot, upper, lower)
    closed_min, closed_max = bounds([lower, upper])
    closed_size = closed_max - closed_min
    render(scene, "blockout-closed.png", hero_camera)

    set_pose(translation, pivot, TRAVEL_MM, 0.0)
    slide_state = pose_state("slide", translation, pivot, upper, lower)
    render(scene, "blockout-hero.png", hero_camera)
    render(scene, "blockout-slide.png", slide_camera)

    set_pose(translation, pivot, 0.0, SPIN_DEGREES)
    spin_state = pose_state("spin", translation, pivot, upper, lower)
    render(scene, "blockout-spin.png", hero_camera)
    spin_pivot_world_before_overlay = world_point(pivot)
    overlay_objects = create_overlay(spin_pivot_world_before_overlay)
    for obj in overlay_objects:
        obj.hide_render = False
    render(scene, "pivot-overlay.png", top_camera)
    for obj in overlay_objects:
        obj.hide_render = True

    set_pose(translation, pivot, 0.0, 0.0)
    ground.hide_render = True
    scene.render.film_transparent = True
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 2048
    top_camera.data.ortho_scale = 58.0
    render(scene, "silhouette-top.png", top_camera)
    scene.render.film_transparent = False
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    top_camera.data.ortho_scale = 70.0
    ground.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    point_axis = list(AXIS_WORLD_MM)
    spin_pivot_drift = (Vector(spin_state["pivotWorldMm"]) - AXIS_WORLD_MM).length
    closed_radius = (Vector(closed_state["upperOriginWorldMm"]) - Vector(closed_state["pivotWorldMm"])).xy.length
    spin_radius = (Vector(spin_state["upperOriginWorldMm"]) - Vector(spin_state["pivotWorldMm"])).xy.length
    lower_invariant = all(
        state["lowerMatrixWorld"] == matrix_values(closed_lower_matrix)
        for state in (closed_state, slide_state, spin_state)
    )
    profile_angle = 180.0 / ARC_SEGMENTS
    chord_deviation = CAP_RADIUS_MM * (1.0 - math.cos(math.pi / (2.0 * ARC_SEGMENTS)))
    animated = [
        obj.name
        for obj in (root, fixed, lower, envelope, translation, pivot, upper)
        if obj.animation_data or obj.constraints
    ]
    report = {
        "schemaVersion": 3,
        "gate": "05-blockout",
        "blockoutRevision": 3,
        "dimensionBasis": "user-authorized-provisional-digital-blockout",
        "rootCauseCorrection": {
            "rejectedRevision": 2,
            "rejectedAxis": "upper-capsule-geometric-center-at-closed-assembly-origin",
            "correctAxis": "single-point-at-trailing-rounded-end-center",
            "gate04RemainsApproved": True,
        },
        "dimensionsMm": {
            "target": {"length": LENGTH_MM, "width": WIDTH_MM, "thickness": THICKNESS_MM},
            "closedMeasured": {
                "length": round(closed_size.y, 6),
                "width": round(closed_size.x, 6),
                "thickness": round(closed_size.z, 6),
            },
            "toleranceMm": 0.01,
            "pass": all(
                abs(actual - target) <= 0.01
                for actual, target in zip((closed_size.y, closed_size.x, closed_size.z), (LENGTH_MM, WIDTH_MM, THICKNESS_MM))
            ),
        },
        "axis": {
            "coordinateFrame": "closed-assembly-center-origin",
            "pointWorldMm": point_axis,
            "axis": "+Z",
            "pointDerivation": "y = -(length - width) / 2 = -9.5 mm, the trailing rounded-end center",
            "upperClosedOriginWorldMm": closed_state["upperOriginWorldMm"],
            "upperLocalOffsetFromPivotMm": [0.0, -AXIS_Y_MM, BODY_THICKNESS_MM / 2.0],
            "enclosureRadiusMm": CAP_RADIUS_MM,
            "enclosureIsPivot": False,
            "pass": point_axis == [0.0, -9.5, 0.0] and envelope["rotating_object"] is False,
        },
        "poses": {
            "closed": closed_state,
            "slide": slide_state,
            "spin": spin_state,
            "slideTravelMm": slide_state["translationMm"][1],
            "slideRotationDeg": slide_state["pivotRotationDeg"],
            "spinTranslationMm": spin_state["translationMm"],
            "spinRotationDeg": spin_state["pivotRotationDeg"],
            "spinPivotWorldDriftMm": spin_pivot_drift,
            "closedCentroidRadiusToPivotMm": closed_radius,
            "spinCentroidRadiusToPivotMm": spin_radius,
            "centroidRadiusDriftMm": abs(closed_radius - spin_radius),
            "combinedSlideAndSpinAllowed": False,
            "pass": (
                slide_state["translationMm"] == [0.0, TRAVEL_MM, 0.0]
                and slide_state["pivotRotationDeg"] == 0.0
                and spin_state["translationMm"] == [0.0, 0.0, 0.0]
                and abs(spin_state["pivotRotationDeg"] - SPIN_DEGREES) <= 0.00001
                and spin_pivot_drift <= 1e-9
                and abs(closed_radius - spin_radius) <= 1e-9
            ),
        },
        "fixedLower": {
            "matrixWorld": matrix_values(closed_lower_matrix),
            "invariantAcrossPoses": lower_invariant,
            "topPlanarityDeviationMm": top_planarity_mm(lower),
            "exposedFeatureCount": 0,
            "pass": lower_invariant and top_planarity_mm(lower) == 0.0,
        },
        "concealedEnvelope": {
            "object": envelope.name,
            "type": envelope.type,
            "worldPointMm": [round(value, 9) for value in world_point(envelope)],
            "radiusMm": envelope.empty_display_size,
            "hideRender": envelope.hide_render,
            "geometry": envelope["geometry"],
            "rotatingObject": envelope["rotating_object"],
            "affectsVisibleSilhouette": False,
            "pass": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none" and not envelope["rotating_object"],
        },
        "hierarchy": {
            obj.name: obj.parent.name if obj.parent else None
            for obj in (root, fixed, lower, envelope, translation, pivot, upper)
        },
        "zeroSelfMotion": {
            "animatedOrConstrainedObjects": animated,
            "angularVelocity": 0.0,
            "pass": not animated,
        },
        "smoothness": {
            "arcSegmentsPerSemicircle": ARC_SEGMENTS,
            "profileVertexCount": len(capsule_profile()),
            "maximumProfileSegmentAngleDeg": profile_angle,
            "maximumChordDeviationMm": chord_deviation,
            "bevelSegments": BEVEL_SEGMENTS,
            "bevelWidthMm": BEVEL_WIDTH_MM,
            "geometryPass": profile_angle <= 1.0 and chord_deviation <= 0.005 and BEVEL_SEGMENTS >= 8,
        },
        "overlayEvidence": {
            "render": "pivot-overlay.png",
            "yellowCrosshair": "single point axis at [0,-9.5,0]",
            "blueDashedCircle": "fixed hidden enclosure metadata only",
            "spinTranslationMm": 0.0,
            "pass": True,
        },
        "renderedSilhouette": {"status": "pending-external-image-validation"},
        "scope": {
            "hiddenEngineeringModeled": False,
            "finalMaterialsOrArtwork": False,
            "unityAssetChanged": False,
        },
        "blender": bpy.app.version_string,
        "sourceBlend": BLEND_PATH.name,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    required = [
        report["dimensionsMm"]["pass"],
        report["axis"]["pass"],
        report["poses"]["pass"],
        report["fixedLower"]["pass"],
        report["concealedEnvelope"]["pass"],
        report["zeroSelfMotion"]["pass"],
        report["smoothness"]["geometryPass"],
        report["overlayEvidence"]["pass"],
    ]
    if not all(required):
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
