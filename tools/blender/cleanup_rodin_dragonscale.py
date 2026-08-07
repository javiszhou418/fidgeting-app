#!/usr/bin/env python3
"""Turn the Rodin Dragon Scale shell into a reviewable mechanical Blender assembly."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def args_from_blender() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--glb", required=True)
    parser.add_argument("--renders", required=True)
    return parser.parse_args(argv)


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return material


def object_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def look_at(obj: bpy.types.Object, point: Vector) -> None:
    obj.rotation_euler = (point - obj.location).to_track_quat("-Z", "Y").to_euler()


def compress_world_thickness(objects: list[bpy.types.Object], center_z: float, factor: float) -> None:
    """Reduce the generated shell thickness without disturbing its multiview silhouette."""
    for obj in objects:
        world_from_local = obj.matrix_world.copy()
        local_from_world = world_from_local.inverted()
        for vertex in obj.data.vertices:
            world = world_from_local @ vertex.co
            world.z = center_z + (world.z - center_z) * factor
            vertex.co = local_from_world @ world
        obj.data.update()


def empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    return obj


def cylinder(
    name: str,
    radius: float,
    depth: float,
    z: float,
    material: bpy.types.Material,
    vertices: int = 64,
    bevel: float = 0.00025,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(0.0, 0.0, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    obj.parent = parent
    if bevel > 0.0:
        modifier = obj.modifiers.new("Edge Softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def annulus(
    name: str,
    inner_radius: float,
    outer_radius: float,
    depth: float,
    z: float,
    material: bpy.types.Material,
    vertices: int = 64,
    parent: bpy.types.Object | None = None,
) -> bpy.types.Object:
    half = depth * 0.5
    mesh_vertices: list[tuple[float, float, float]] = []
    for ring_radius, ring_z in (
        (outer_radius, z - half),
        (outer_radius, z + half),
        (inner_radius, z + half),
        (inner_radius, z - half),
    ):
        for index in range(vertices):
            angle = 2.0 * math.pi * index / vertices
            mesh_vertices.append((ring_radius * math.cos(angle), ring_radius * math.sin(angle), ring_z))
    faces: list[tuple[int, int, int, int]] = []
    for index in range(vertices):
        nxt = (index + 1) % vertices
        faces.extend(
            [
                (index, nxt, vertices + nxt, vertices + index),
                (vertices + index, vertices + nxt, 2 * vertices + nxt, 2 * vertices + index),
                (2 * vertices + index, 2 * vertices + nxt, 3 * vertices + nxt, 3 * vertices + index),
                (3 * vertices + index, 3 * vertices + nxt, nxt, index),
            ]
        )
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(mesh_vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = parent
    return obj


def faceted_bezel(
    name: str,
    outer_radius: float,
    inner_radius: float,
    z_bottom: float,
    z_outer_top: float,
    z_inner_top: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
    segments: int = 20,
) -> bpy.types.Object:
    verts: list[tuple[float, float, float]] = []
    for radius, z in (
        (outer_radius, z_bottom),
        (outer_radius, z_outer_top),
        (inner_radius, z_inner_top),
        (inner_radius, z_bottom),
    ):
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            verts.append((radius * math.cos(angle), radius * math.sin(angle), z))
    faces: list[tuple[int, int, int, int]] = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.extend(
            [
                (index, nxt, segments + nxt, segments + index),
                (segments + index, segments + nxt, 2 * segments + nxt, 2 * segments + index),
                (2 * segments + index, 2 * segments + nxt, 3 * segments + nxt, 3 * segments + index),
                (3 * segments + index, 3 * segments + nxt, nxt, index),
            ]
        )
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = parent
    bevel = obj.modifiers.new("Micro Bevel", "BEVEL")
    bevel.width = 0.00016
    bevel.segments = 2
    return obj


def add_bearing_balls(parent: bpy.types.Object, z: float, material: bpy.types.Material) -> None:
    for index in range(10):
        angle = 2.0 * math.pi * index / 10.0
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20,
            ring_count=10,
            radius=0.00135,
            location=(0.0072 * math.cos(angle), 0.0072 * math.sin(angle), z),
        )
        ball = bpy.context.object
        ball.name = f"Bearing_Ball_{index + 1:02d}"
        ball.data.materials.append(material)
        ball.parent = parent


def add_area(name: str, location: tuple[float, float, float], energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "RECTANGLE"
    data.size = size
    data.size_y = size * 0.32
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = location
    look_at(light, Vector((0.0, 0.0, 0.006)))


def main() -> None:
    args = args_from_blender()
    input_path = Path(args.input).resolve()
    blend_path = Path(args.blend).resolve()
    glb_path = Path(args.glb).resolve()
    render_dir = Path(args.renders).resolve()
    blend_path.parent.mkdir(parents=True, exist_ok=True)
    glb_path.parent.mkdir(parents=True, exist_ok=True)
    render_dir.mkdir(parents=True, exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

    silver = make_material("Brushed Titanium", (0.32, 0.35, 0.39, 1.0), 0.82, 0.29)
    face_silver = make_material("Finger Cap Face", (0.26, 0.29, 0.33, 1.0), 0.9, 0.2)
    dark_steel = make_material("Bearing Dark Steel", (0.018, 0.022, 0.03, 1.0), 0.78, 0.2)
    bearing_steel = make_material("Bearing Steel", (0.2, 0.22, 0.25, 1.0), 0.92, 0.16)
    bronze = make_material("Warm Accent", (0.13, 0.055, 0.012, 1.0), 0.82, 0.24)

    bpy.ops.import_scene.gltf(filepath=str(input_path))
    shell_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not shell_objects:
        raise RuntimeError("Rodin GLB has no mesh")
    rotor_root = empty("DragonScaleEDC_Rotor_Root")
    for obj in shell_objects:
        obj.name = "DragonScaleEDC_Rotor_Sculpt_Rodin"
        obj.data.materials.clear()
        obj.data.materials.append(silver)
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        if obj.parent is None:
            world = obj.matrix_world.copy()
            obj.parent = rotor_root
            obj.matrix_world = world

    lower, upper = object_bounds(shell_objects)
    dims = upper - lower
    thin_axis = min(range(3), key=lambda index: dims[index])
    if thin_axis == 0:
        rotor_root.rotation_euler[1] = math.radians(90.0)
    elif thin_axis == 1:
        rotor_root.rotation_euler[0] = math.radians(-90.0)
    bpy.context.view_layer.update()
    lower, upper = object_bounds(shell_objects)
    rotor_root.location -= (lower + upper) * 0.5
    bpy.context.view_layer.update()
    lower, upper = object_bounds(shell_objects)
    dims = upper - lower
    rotor_root.scale *= 0.065 / max(dims.x, dims.y)
    bpy.context.view_layer.update()
    lower, upper = object_bounds(shell_objects)
    rotor_root.location.z -= lower.z
    bpy.context.view_layer.update()
    lower, upper = object_bounds(shell_objects)
    center_z = (lower.z + upper.z) * 0.5
    compress_world_thickness(shell_objects, center_z, 0.62)
    bpy.context.view_layer.update()
    lower, upper = object_bounds(shell_objects)

    assembly_root = empty("DragonScaleEDC_Assembly")
    rotor_root.parent = assembly_root

    hub_shroud = empty("Rotor_Hub_Shroud", assembly_root)
    cylinder("Rotor_Hub_Dark_Band", 0.0192, 0.00565, center_z, dark_steel, 96, 0.0004, hub_shroud)
    cylinder("Rotor_Hub_Top_Mask", 0.0192, 0.0007, 0.00935, dark_steel, 96, 0.00012, hub_shroud)
    cylinder("Rotor_Hub_Bottom_Mask", 0.0192, 0.0007, 0.00215, dark_steel, 96, 0.00012, hub_shroud)
    annulus("Rotor_Hub_Top_Accent", 0.01878, 0.01922, 0.0004, 0.00973, bronze, 96, hub_shroud)
    annulus("Rotor_Hub_Bottom_Accent", 0.01878, 0.01922, 0.0004, 0.00177, bronze, 96, hub_shroud)

    top_cap = empty("Top_Finger_Cap", assembly_root)
    faceted_bezel("Top_Cap_Faceted_Bezel", 0.01715, 0.0127, 0.00855, 0.01065, 0.01145, silver, top_cap)
    cylinder("Top_Cap_Brushed_Face", 0.01285, 0.00055, 0.01148, face_silver, 96, 0.00018, top_cap)
    annulus("Top_Cap_Accent_Ring", 0.0170, 0.01738, 0.00042, 0.00875, bronze, 96, top_cap)

    top_washer = empty("Top_Washer", assembly_root)
    annulus("Top_Washer_Mesh", 0.0041, 0.0112, 0.00045, 0.00825, bearing_steel, 64, top_washer)

    bearing = empty("Bearing_608", assembly_root)
    annulus("Bearing_Outer_Race", 0.00885, 0.0111, 0.0051, center_z, dark_steel, 96, bearing)
    annulus("Bearing_Inner_Race", 0.0040, 0.0060, 0.0051, center_z, bearing_steel, 96, bearing)
    add_bearing_balls(bearing, center_z, bearing_steel)

    bottom_washer = empty("Bottom_Washer", assembly_root)
    annulus("Bottom_Washer_Mesh", 0.0041, 0.0112, 0.00045, 0.00305, bearing_steel, 64, bottom_washer)

    bottom_cap = empty("Bottom_Finger_Cap", assembly_root)
    faceted_bezel("Bottom_Cap_Faceted_Bezel", 0.01715, 0.0127, 0.0030, 0.0009, 0.0001, silver, bottom_cap)
    cylinder("Bottom_Cap_Brushed_Face", 0.01285, 0.00055, 0.00008, face_silver, 96, 0.00018, bottom_cap)
    annulus("Bottom_Cap_Accent_Ring", 0.0170, 0.01738, 0.00042, 0.00282, bronze, 96, bottom_cap)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.006, 0.007, 0.009)
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -1.2

    add_area("Studio_Key", (0.07, -0.09, 0.12), 14.0, 0.045)
    add_area("Studio_Fill", (-0.08, -0.02, 0.07), 7.0, 0.055)
    add_area("Studio_Rim", (0.03, 0.08, 0.10), 11.0, 0.035)

    camera_data = bpy.data.cameras.new("Review_Camera")
    camera = bpy.data.objects.new("Review_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.type = "ORTHO"

    target = Vector((0.0, 0.0, center_z))
    assembled_views = {
        "top": (Vector((0.0, 0.0, 0.13)), target, 0.077),
        "side": (Vector((0.0, -0.13, center_z)), target, 0.078),
        "iso": (Vector((0.085, -0.105, 0.085)), target, 0.091),
    }
    for name, (location, view_target, ortho_scale) in assembled_views.items():
        camera.location = location
        camera.data.ortho_scale = ortho_scale
        look_at(camera, view_target)
        scene.render.filepath = str(render_dir / f"DragonScaleEDC_Cleanup_{name}.png")
        bpy.ops.render.render(write_still=True)

    exploded_offsets = {
        top_cap: 0.038,
        top_washer: 0.021,
        bearing: 0.010,
        bottom_washer: -0.018,
        bottom_cap: -0.036,
    }
    for obj, offset in exploded_offsets.items():
        obj.location.z += offset
    bpy.context.view_layer.update()
    camera.location = Vector((0.095, -0.15, 0.08))
    camera.data.ortho_scale = 0.125
    look_at(camera, Vector((0.0, 0.0, 0.006)))
    scene.render.filepath = str(render_dir / "DragonScaleEDC_Cleanup_exploded.png")
    bpy.ops.render.render(write_still=True)
    for obj, offset in exploded_offsets.items():
        obj.location.z -= offset

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.object.select_all(action="DESELECT")
    assembly_root.select_set(True)
    for obj in assembly_root.children_recursive:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_materials="EXPORT",
        export_extras=True,
    )
    print(
        {
            "blend": str(blend_path),
            "glb": str(glb_path),
            "outer_bounds_mm": [round(value * 1000.0, 3) for value in (upper - lower)],
            "render_dir": str(render_dir),
            "components": [rotor_root.name, top_cap.name, top_washer.name, bearing.name, bottom_washer.name, bottom_cap.name],
        }
    )


if __name__ == "__main__":
    main()
