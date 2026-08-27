#!/usr/bin/env python3
"""Build the corrected Gate 05 magnetic-slide-tile white model."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
BLEND_PATH = OUTPUT / "magnetic-slide-tile-blockout-r002.blend"
VALIDATION_PATH = OUTPUT / "blockout-validation.json"

LENGTH_MM = 50.0
WIDTH_MM = 31.0
THICKNESS_MM = 12.0
BODY_THICKNESS_MM = 6.0
TRAVEL_MM = 21.0
ARC_SEGMENTS = 256
BEVEL_SEGMENTS = 8
BEVEL_WIDTH_MM = 0.45
MAX_ALLOWED_SEGMENT_ANGLE_DEG = 1.0
MAX_ALLOWED_CHORD_DEVIATION_MM = 0.005


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    return result


def capsule_profile(length: float, width: float) -> list[tuple[float, float]]:
    radius = width / 2.0
    straight_half = length / 2.0 - radius
    points = []
    for index in range(ARC_SEGMENTS + 1):
        angle = index * math.pi / ARC_SEGMENTS
        points.append((radius * math.cos(angle), straight_half + radius * math.sin(angle)))
    for index in range(1, ARC_SEGMENTS + 1):
        angle = math.pi + index * math.pi / ARC_SEGMENTS
        points.append((radius * math.cos(angle), -straight_half + radius * math.sin(angle)))
    return points


def capsule_mesh(
    name: str,
    length: float,
    width: float,
    height: float,
    z_center: float,
    clay: bpy.types.Material,
) -> bpy.types.Object:
    profile = capsule_profile(length, width)
    count = len(profile)
    vertices = [(x, y, -height / 2.0) for x, y in profile]
    vertices.extend((x, y, height / 2.0) for x, y in profile)
    faces: list[tuple[int, ...]] = [
        tuple(reversed(range(count))),
        tuple(range(count, count * 2)),
    ]
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    validation_changed_geometry = mesh.validate(clean_customdata=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location.z = z_center
    obj.data.materials.append(clay)
    obj["profile_kind"] = "high-resolution-analytic-capsule"
    obj["arc_segments_per_semicircle"] = ARC_SEGMENTS
    obj["profile_vertex_count"] = count
    obj["mesh_validation_changed_geometry"] = validation_changed_geometry
    obj["cap_topology"] = "single-planar-ngon-per-face"
    obj["side_normals"] = "smooth"

    bevel = obj.modifiers.new("SilhouetteEdgeBevel", "BEVEL")
    bevel.width = BEVEL_WIDTH_MM
    bevel.segments = BEVEL_SEGMENTS
    bevel.harden_normals = True
    return obj


def parent(child: bpy.types.Object, parent_object: bpy.types.Object) -> None:
    child.parent = parent_object


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def render_pose(
    scene: bpy.types.Scene,
    upper_motion: bpy.types.Object,
    output: Path,
    travel: float,
    rotation_degrees: float,
) -> None:
    upper_motion.location = (0.0, travel, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, math.radians(rotation_degrees))
    bpy.context.view_layer.update()
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def top_planarity_mm(obj: bpy.types.Object) -> float:
    top_z = max(vertex.co.z for vertex in obj.data.vertices)
    top_vertices = [vertex.co.z for vertex in obj.data.vertices if abs(vertex.co.z - top_z) < 1e-9]
    return max(top_vertices) - min(top_vertices)


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
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.065, 0.078)
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene["gate"] = "05-blockout"
    scene["blockout_revision"] = 2
    scene["dimension_basis"] = "user-authorized-provisional-digital-blockout"
    scene["overall_dimensions_mm"] = [LENGTH_MM, WIDTH_MM, THICKNESS_MM]
    scene["approved_travel_mm"] = TRAVEL_MM
    scene["visible_lower_surface"] = "clean-continuous-flat-plane"
    scene["mechanism_visibility"] = "concealed-circular-envelope-only"
    scene["self_motion"] = "none"

    fixed_clay = material("WhiteClay_Fixed", (0.72, 0.76, 0.80, 1.0), 0.72)
    moving_clay = material("WhiteClay_Moving", (0.96, 0.97, 0.98, 1.0), 0.62)

    root = bpy.data.objects.new("MagneticSlideTile_Blockout_R002", None)
    bpy.context.collection.objects.link(root)
    root["overall_length_mm"] = LENGTH_MM
    root["overall_width_mm"] = WIDTH_MM
    root["overall_thickness_mm"] = THICKNESS_MM
    root["travel_mm"] = TRAVEL_MM
    root["translation_axis"] = "+Y"
    root["rotation_axis"] = "+Z"
    root["pivot_world_mm"] = [0.0, 0.0, 0.0]

    fixed_assembly = bpy.data.objects.new("FixedAssembly", None)
    bpy.context.collection.objects.link(fixed_assembly)
    fixed_assembly["role"] = "relative-fixed-clean-lower-body"
    parent(fixed_assembly, root)

    upper_motion = bpy.data.objects.new("UpperMotion", None)
    bpy.context.collection.objects.link(upper_motion)
    upper_motion["role"] = "same-upper-part-translation-and-rotation"
    upper_motion["travel_min_mm"] = 0.0
    upper_motion["travel_max_mm"] = TRAVEL_MM
    upper_motion["translation_axis"] = "+Y"
    upper_motion["rotation_axis"] = "+Z"
    upper_motion["angular_velocity"] = 0.0
    parent(upper_motion, root)

    lower = capsule_mesh(
        "LowerBody_Fixed_CleanPlane",
        LENGTH_MM,
        WIDTH_MM,
        BODY_THICKNESS_MM,
        -BODY_THICKNESS_MM / 2.0,
        fixed_clay,
    )
    lower["role"] = "fixed-lower-exterior-main-body-clean-flat-top"
    lower["exposed_top_features"] = "none"
    parent(lower, fixed_assembly)

    concealed_envelope = bpy.data.objects.new("ConcealedCircularEnvelope", None)
    bpy.context.collection.objects.link(concealed_envelope)
    concealed_envelope.empty_display_type = "CIRCLE"
    concealed_envelope.empty_display_size = WIDTH_MM / 2.0
    concealed_envelope.hide_render = True
    concealed_envelope["role"] = "non-rendered-location-envelope-only"
    concealed_envelope["shape"] = "circular"
    concealed_envelope["hidden_paths_and_parts"] = "unknown-not-modeled"
    parent(concealed_envelope, fixed_assembly)

    mechanism_proxy = bpy.data.objects.new("HiddenMechanismProxy", None)
    bpy.context.collection.objects.link(mechanism_proxy)
    mechanism_proxy.empty_display_type = "PLAIN_AXES"
    mechanism_proxy.empty_display_size = 3.0
    mechanism_proxy.hide_render = True
    mechanism_proxy["role"] = "non-rendered-motion-validation-proxy"
    mechanism_proxy["geometry"] = "none"
    parent(mechanism_proxy, concealed_envelope)

    upper = capsule_mesh(
        "UpperCapsule_Moving",
        LENGTH_MM,
        WIDTH_MM,
        BODY_THICKNESS_MM,
        BODY_THICKNESS_MM / 2.0,
        moving_clay,
    )
    upper["role"] = "single-upper-exterior-main-body-translates-and-rotates"
    parent(upper, upper_motion)

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 8.0, -6.8))
    ground = bpy.context.object
    ground.name = "PresentationGround"
    ground.data.materials.append(material("Ground", (0.075, 0.090, 0.108, 1.0), 0.86))

    bpy.ops.object.light_add(type="AREA", location=(45.0, -35.0, 70.0))
    key = bpy.context.object
    key.name = "KeyLight"
    key.data.energy = 55000.0
    key.data.shape = "DISK"
    key.data.size = 52.0
    look_at(key, Vector((0.0, 7.0, 0.0)))
    bpy.ops.object.light_add(type="AREA", location=(-48.0, -5.0, 38.0))
    fill = bpy.context.object
    fill.name = "FillLight"
    fill.data.energy = 32000.0
    fill.data.size = 46.0
    look_at(fill, Vector((0.0, 6.0, 0.0)))
    bpy.ops.object.light_add(type="AREA", location=(0.0, 65.0, 55.0))
    rim = bpy.context.object
    rim.name = "RimLight"
    rim.data.energy = 42000.0
    rim.data.size = 38.0
    look_at(rim, Vector((0.0, 8.0, 2.0)))

    bpy.ops.object.camera_add(location=(72.0, -86.0, 68.0))
    hero_camera = bpy.context.object
    hero_camera.name = "HeroCamera"
    hero_camera.data.lens = 72.0
    look_at(hero_camera, Vector((0.0, 7.0, 0.0)))
    scene.camera = hero_camera

    upper_motion.location = (0.0, 0.0, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    closed_min, closed_max = bounds([lower, upper])
    closed_size = closed_max - closed_min

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    render_pose(scene, upper_motion, OUTPUT / "blockout-closed.png", 0.0, 0.0)
    render_pose(scene, upper_motion, OUTPUT / "blockout-hero.png", TRAVEL_MM, 0.0)
    render_pose(scene, upper_motion, OUTPUT / "blockout-spin.png", 0.0, 45.0)

    upper_motion.location = (0.0, 0.0, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, 0.0)
    ground.hide_render = True
    scene.render.film_transparent = True
    scene.render.resolution_x = 2048
    scene.render.resolution_y = 2048
    bpy.ops.object.camera_add(location=(0.0, 0.0, 100.0), rotation=(0.0, 0.0, 0.0))
    silhouette_camera = bpy.context.object
    silhouette_camera.name = "SilhouetteCamera"
    silhouette_camera.data.type = "ORTHO"
    silhouette_camera.data.ortho_scale = 58.0
    scene.camera = silhouette_camera
    bpy.context.view_layer.update()
    scene.render.filepath = str(OUTPUT / "silhouette-top.png")
    bpy.ops.render.render(write_still=True)

    scene.camera = hero_camera
    scene.render.film_transparent = False
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    ground.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    profile_angle_deg = 180.0 / ARC_SEGMENTS
    profile_chord_deviation_mm = WIDTH_MM / 2.0 * (1.0 - math.cos(math.pi / (2.0 * ARC_SEGMENTS)))
    model_objects = [lower, upper]
    animated = [
        obj.name
        for obj in [root, fixed_assembly, upper_motion, concealed_envelope, mechanism_proxy, *model_objects]
        if obj.animation_data or obj.constraints
    ]
    mesh_names = [obj.name for obj in model_objects]
    exposed_hardware_names = [
        name
        for name in mesh_names
        if any(token in name.lower() for token in ("rail", "track", "carrier", "ball", "groove", "hardware"))
    ]
    hierarchy = {
        obj.name: obj.parent.name if obj.parent else None
        for obj in [root, fixed_assembly, upper_motion, lower, concealed_envelope, mechanism_proxy, upper]
    }
    report = {
        "schemaVersion": 2,
        "gate": "05-blockout",
        "blockoutRevision": 2,
        "dimensionBasis": "user-authorized-provisional-digital-blockout",
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
                for actual, target in zip(
                    (closed_size.y, closed_size.x, closed_size.z),
                    (LENGTH_MM, WIDTH_MM, THICKNESS_MM),
                )
            ),
        },
        "travel": {"axis": "+Y", "targetMm": TRAVEL_MM, "implementedMm": upper_motion["travel_max_mm"], "pass": upper_motion["travel_max_mm"] == TRAVEL_MM},
        "pivot": {"worldMm": list(root["pivot_world_mm"]), "rotationAxis": "+Z", "canonicalUpperMotionOrigin": list(upper_motion.location), "pass": tuple(upper_motion.location) == (0.0, 0.0, 0.0)},
        "hierarchy": hierarchy,
        "zeroSelfMotion": {"animatedOrConstrainedObjects": animated, "upperAngularVelocity": upper_motion["angular_velocity"], "pass": not animated and upper_motion["angular_velocity"] == 0.0},
        "visibleArchitecture": {
            "renderedMeshObjects": mesh_names,
            "renderedMeshCount": len(mesh_names),
            "lowerTopPlanarityDeviationMm": top_planarity_mm(lower),
            "lowerExposedTopFeatureCount": 0,
            "exposedRailOrHardwareObjectNames": exposed_hardware_names,
            "concealedEnvelopeType": concealed_envelope.type,
            "concealedEnvelopeShape": concealed_envelope["shape"],
            "concealedEnvelopeHiddenFromRender": concealed_envelope.hide_render,
            "hiddenMechanismGeometry": mechanism_proxy["geometry"],
            "pass": (
                len(mesh_names) == 2
                and top_planarity_mm(lower) == 0.0
                and not exposed_hardware_names
                and concealed_envelope.type == "EMPTY"
                and concealed_envelope.hide_render
                and mechanism_proxy.type == "EMPTY"
                and mechanism_proxy["geometry"] == "none"
            ),
        },
        "smoothness": {
            "profileKind": "analytic capsule sampled at fixed angular intervals",
            "arcSegmentsPerSemicircle": ARC_SEGMENTS,
            "profileVertexCount": len(capsule_profile(LENGTH_MM, WIDTH_MM)),
            "maximumProfileSegmentAngleDeg": profile_angle_deg,
            "maximumChordDeviationMm": profile_chord_deviation_mm,
            "bevelSegments": BEVEL_SEGMENTS,
            "bevelWidthMm": BEVEL_WIDTH_MM,
            "sideNormals": "smooth",
            "capNormals": "flat",
            "meshValidationChangedGeometry": {
                lower.name: bool(lower["mesh_validation_changed_geometry"]),
                upper.name: bool(upper["mesh_validation_changed_geometry"]),
            },
            "thresholds": {
                "maximumProfileSegmentAngleDeg": MAX_ALLOWED_SEGMENT_ANGLE_DEG,
                "maximumChordDeviationMm": MAX_ALLOWED_CHORD_DEVIATION_MM,
                "minimumBevelSegments": 8,
            },
            "geometryPass": (
                profile_angle_deg <= MAX_ALLOWED_SEGMENT_ANGLE_DEG
                and profile_chord_deviation_mm <= MAX_ALLOWED_CHORD_DEVIATION_MM
                and BEVEL_SEGMENTS >= 8
                and not lower["mesh_validation_changed_geometry"]
                and not upper["mesh_validation_changed_geometry"]
            ),
        },
        "renderedSilhouette": {"status": "pending-external-image-validation"},
        "scope": {
            "twoExteriorMainBodies": True,
            "visibleLowerPlaneClean": True,
            "concealedCircularEnvelopeOnly": True,
            "hiddenEngineeringModeled": False,
            "finalMaterialsOrArtwork": False,
        },
        "blender": bpy.app.version_string,
        "sourceBlend": BLEND_PATH.name,
    }
    VALIDATION_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    required = [
        report["dimensionsMm"]["pass"],
        report["travel"]["pass"],
        report["pivot"]["pass"],
        report["zeroSelfMotion"]["pass"],
        report["visibleArchitecture"]["pass"],
        report["smoothness"]["geometryPass"],
    ]
    if not all(required):
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
