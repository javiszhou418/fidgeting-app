#!/usr/bin/env python3
"""Build and render the Gate 05 magnetic-slide-tile white-model blockout."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
BLEND_PATH = OUTPUT / "magnetic-slide-tile-blockout.blend"
VALIDATION_PATH = OUTPUT / "blockout-validation.json"

LENGTH_MM = 50.0
WIDTH_MM = 31.0
THICKNESS_MM = 12.0
BODY_THICKNESS_MM = THICKNESS_MM / 2.0
TRAVEL_MM = 21.0


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def make_material(name: str, color: tuple[float, float, float, float], roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = 0.0
    return material


def capsule_mesh(name: str, length: float, width: float, height: float, z_center: float, material: bpy.types.Material) -> bpy.types.Object:
    radius = width / 2.0
    straight_half = length / 2.0 - radius
    profile: list[tuple[float, float]] = []
    arc_steps = 24
    for index in range(arc_steps + 1):
        angle = index * math.pi / arc_steps
        profile.append((radius * math.cos(angle), straight_half + radius * math.sin(angle)))
    for index in range(arc_steps + 1):
        angle = math.pi + index * math.pi / arc_steps
        profile.append((radius * math.cos(angle), -straight_half + radius * math.sin(angle)))

    count = len(profile)
    vertices = [(x, y, -height / 2.0) for x, y in profile] + [(x, y, height / 2.0) for x, y in profile]
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(reversed(range(count))))
    faces.append(tuple(range(count, count * 2)))
    for index in range(count):
        next_index = (index + 1) % count
        faces.append((index, next_index, count + next_index, count + index))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location.z = z_center
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("BlockoutEdgeSoftening", "BEVEL")
    bevel.width = 0.8
    bevel.segments = 4
    obj["scope"] = "approved-white-model-proxy"
    return obj


def add_box(name: str, dimensions: tuple[float, float, float], location: tuple[float, float, float], material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("ProxyEdgeSoftening", "BEVEL")
    bevel.width = min(dimensions) * 0.35
    bevel.segments = 4
    obj["scope"] = "visible-mechanism-proxy"
    return obj


def add_cylinder(name: str, radius: float, depth: float, location: tuple[float, float, float], material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("ProxyEdgeSoftening", "BEVEL")
    bevel.width = 0.25
    bevel.segments = 3
    obj["scope"] = "visible-central-interface-proxy"
    return obj


def parent(child: bpy.types.Object, parent_object: bpy.types.Object) -> None:
    child.parent = parent_object
    child.matrix_parent_inverse = parent_object.matrix_world.inverted()


def look_at(camera: bpy.types.Object, target: Vector) -> None:
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points))),
        Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points))),
    )


def render_pose(scene: bpy.types.Scene, upper_motion: bpy.types.Object, path: Path, travel: float, rotation_degrees: float) -> None:
    upper_motion.location = (0.0, travel, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, math.radians(rotation_degrees))
    bpy.context.view_layer.update()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.color = (0.055, 0.065, 0.078)
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene["gate"] = "05-blockout"
    scene["dimension_basis"] = "user-authorized-provisional-digital-blockout"
    scene["overall_dimensions_mm"] = [LENGTH_MM, WIDTH_MM, THICKNESS_MM]
    scene["approved_travel_mm"] = TRAVEL_MM
    scene["hidden_engineering_policy"] = "unknown-not-modeled"
    scene["self_motion"] = "none"

    fixed_clay = make_material("WhiteClay_Fixed", (0.72, 0.76, 0.80, 1.0), 0.72)
    moving_clay = make_material("WhiteClay_Moving", (0.96, 0.97, 0.98, 1.0), 0.62)
    proxy_clay = make_material("WhiteClay_Proxy", (0.46, 0.52, 0.58, 1.0), 0.78)

    root = bpy.data.objects.new("MagneticSlideTile_Blockout", None)
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
    parent(fixed_assembly, root)
    fixed_assembly["role"] = "relative-fixed-reference"

    upper_motion = bpy.data.objects.new("UpperMotion", None)
    bpy.context.collection.objects.link(upper_motion)
    parent(upper_motion, root)
    upper_motion["role"] = "same-part-translation-and-rotation"
    upper_motion["travel_min_mm"] = 0.0
    upper_motion["travel_max_mm"] = TRAVEL_MM
    upper_motion["translation_axis"] = "+Y"
    upper_motion["rotation_axis"] = "+Z"
    upper_motion["angular_velocity"] = 0.0

    lower = capsule_mesh("LowerBody_Fixed", LENGTH_MM, WIDTH_MM, BODY_THICKNESS_MM, -BODY_THICKNESS_MM / 2.0, fixed_clay)
    lower["role"] = "fixed-lower-exterior-main-body"
    parent(lower, fixed_assembly)

    carrier = capsule_mesh("TrackCarrier_VisibleProxy", 42.0, 23.0, 1.0, 0.25, proxy_clay)
    carrier["role"] = "visible-fixed-carrier-proxy"
    parent(carrier, fixed_assembly)

    for x, suffix in ((-4.2, "Left"), (4.2, "Right")):
        track = add_box(f"TrackZone_{suffix}_Proxy", (1.4, 25.0, 0.65), (x, 0.0, 1.05), moving_clay)
        track["role"] = "visible-linear-track-zone-proxy"
        parent(track, fixed_assembly)

    pivot = add_cylinder("PivotInterface_Proxy", 3.4, 1.4, (0.0, 0.0, 1.35), moving_clay)
    pivot["role"] = "visible-central-pivot-interface-proxy"
    parent(pivot, fixed_assembly)

    upper = capsule_mesh("UpperCapsule_Moving", LENGTH_MM, WIDTH_MM, BODY_THICKNESS_MM, BODY_THICKNESS_MM / 2.0, moving_clay)
    upper["role"] = "single-upper-exterior-main-body-translates-and-rotates"
    parent(upper, upper_motion)

    model_objects = [lower, carrier, pivot, upper, *[bpy.data.objects[name] for name in ("TrackZone_Left_Proxy", "TrackZone_Right_Proxy")]]

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 8.0, -6.8))
    ground = bpy.context.object
    ground.name = "PresentationGround"
    ground.data.materials.append(make_material("Ground", (0.075, 0.090, 0.108, 1.0), 0.86))

    bpy.ops.object.light_add(type="AREA", location=(45.0, -35.0, 70.0))
    key = bpy.context.object
    key.name = "KeyLight"
    key.data.energy = 55000.0
    key.data.shape = "DISK"
    key.data.size = 52.0
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
    camera = bpy.context.object
    camera.name = "HeroCamera"
    camera.data.lens = 72.0
    look_at(camera, Vector((0.0, 7.0, 0.0)))
    scene.camera = camera

    upper_motion.location = (0.0, 0.0, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    closed_min, closed_max = world_bounds([lower, upper])
    closed_size = closed_max - closed_min

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    render_pose(scene, upper_motion, OUTPUT / "blockout-closed.png", 0.0, 0.0)
    render_pose(scene, upper_motion, OUTPUT / "blockout-hero.png", TRAVEL_MM, 0.0)
    render_pose(scene, upper_motion, OUTPUT / "blockout-spin.png", 0.0, 45.0)

    upper_motion.location = (0.0, 0.0, 0.0)
    upper_motion.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    hierarchy = {
        obj.name: obj.parent.name if obj.parent else None
        for obj in [root, fixed_assembly, upper_motion, lower, carrier, pivot, upper, bpy.data.objects["TrackZone_Left_Proxy"], bpy.data.objects["TrackZone_Right_Proxy"]]
    }
    animated = [obj.name for obj in model_objects + [root, fixed_assembly, upper_motion] if obj.animation_data or obj.constraints]
    validation = {
        "schemaVersion": 1,
        "gate": "05-blockout",
        "dimensionBasis": "user-authorized-provisional-digital-blockout",
        "dimensionsMm": {
            "target": {"length": LENGTH_MM, "width": WIDTH_MM, "thickness": THICKNESS_MM},
            "closedMeasured": {
                "length": round(closed_size.y, 4),
                "width": round(closed_size.x, 4),
                "thickness": round(closed_size.z, 4),
            },
            "pass": all(abs(actual - target) <= 0.01 for actual, target in zip((closed_size.y, closed_size.x, closed_size.z), (LENGTH_MM, WIDTH_MM, THICKNESS_MM))),
        },
        "travel": {"axis": "+Y", "targetMm": TRAVEL_MM, "implementedMm": upper_motion["travel_max_mm"], "pass": upper_motion["travel_max_mm"] == TRAVEL_MM},
        "pivot": {"worldMm": list(root["pivot_world_mm"]), "rotationAxis": "+Z", "upperMotionOrigin": list(upper_motion.location), "pass": tuple(upper_motion.location) == (0.0, 0.0, 0.0)},
        "hierarchy": hierarchy,
        "zeroSelfMotion": {"animatedOrConstrainedObjects": animated, "upperAngularVelocity": upper_motion["angular_velocity"], "pass": not animated and upper_motion["angular_velocity"] == 0.0},
        "scope": {
            "twoExteriorMainBodies": True,
            "visibleCarrierTrackZones": True,
            "centralPivotProxy": True,
            "hiddenEngineeringModeled": False,
            "finalMaterialsOrArtwork": False,
        },
        "blender": bpy.app.version_string,
        "sourceBlend": BLEND_PATH.name,
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    if not validation["dimensionsMm"]["pass"] or not validation["travel"]["pass"] or not validation["pivot"]["pass"] or not validation["zeroSelfMotion"]["pass"]:
        raise RuntimeError(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
