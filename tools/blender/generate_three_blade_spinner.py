"""Build the canonical Blender-authored three-blade EDC spinner.

This script is executed inside Blender through Blender MCP. Dimensions are in
meters. Blender's Z spin axis is converted to Unity's Y-up convention by the
FBX exporter.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


REPO_ROOT = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
UNITY_ROOT = REPO_ROOT / "unity" / "FidgetingApp"
SOURCE_DIR = UNITY_ROOT / "ArtSource" / "ThreeBladeSpinner"
MODEL_DIR = UNITY_ROOT / "Assets" / "_Fidgeting" / "Models" / "BlenderThreeBlade"
ARTIFACT_DIR = UNITY_ROOT / "Artifacts" / "BlenderThreeBlade"

BLEND_PATH = SOURCE_DIR / "ThreeBladeSpinner.blend"
FBX_PATH = MODEL_DIR / "ThreeBladeSpinner.fbx"
GLB_PATH = MODEL_DIR / "ThreeBladeSpinner.glb"
COLLISION_FBX_PATH = MODEL_DIR / "ThreeBladeSpinner_Collision.fbx"
PREVIEW_PATH = ARTIFACT_DIR / "three-blade-spinner-hero.png"
TOP_PREVIEW_PATH = ARTIFACT_DIR / "three-blade-spinner-top.png"
STATS_PATH = ARTIFACT_DIR / "three-blade-spinner-stats.json"

BODY_DEPTH = 0.0088
CAP_RADIUS = 0.0175
CAP_DEPTH = 0.0032


def ensure_dirs() -> None:
    for path in (SOURCE_DIR, MODEL_DIR, ARTIFACT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def clear_scene() -> None:
    # Direct datablock removal also clears hidden render-only objects from a
    # previous iteration; select/delete intentionally skips hidden objects.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], metallic: float, roughness: float):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Edge Bevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(24.0)
    modifier.harden_normals = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def create_prism(
    name: str,
    points: list[tuple[float, float]],
    depth: float,
    z_center: float,
    mat: bpy.types.Material | None,
    bevel: float = 0.0,
) -> bpy.types.Object:
    half = depth * 0.5
    count = len(points)
    verts = [(x, y, z_center - half) for x, y in points]
    verts += [(x, y, z_center + half) for x, y in points]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for i in range(count):
        nxt = (i + 1) % count
        faces.append((i, nxt, nxt + count, i + count))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel > 0.0:
        add_bevel(obj, bevel)
    return obj


def create_ring(
    name: str,
    outer_radius: float,
    inner_radius: float,
    depth: float,
    z_center: float,
    mat: bpy.types.Material,
    segments: int = 96,
    bevel: float = 0.00045,
) -> bpy.types.Object:
    half = depth * 0.5
    verts: list[tuple[float, float, float]] = []
    for z in (z_center - half, z_center + half):
        for radius in (outer_radius, inner_radius):
            for i in range(segments):
                angle = math.tau * i / segments
                verts.append((radius * math.cos(angle), radius * math.sin(angle), z))

    bottom_outer = 0
    bottom_inner = segments
    top_outer = segments * 2
    top_inner = segments * 3
    faces: list[tuple[int, int, int, int]] = []
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.extend(
            [
                (bottom_outer + i, bottom_outer + nxt, top_outer + nxt, top_outer + i),
                (bottom_inner + nxt, bottom_inner + i, top_inner + i, top_inner + nxt),
                (top_outer + i, top_outer + nxt, top_inner + nxt, top_inner + i),
                (bottom_outer + nxt, bottom_outer + i, bottom_inner + i, bottom_inner + nxt),
            ]
        )
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel > 0.0:
        add_bevel(obj, bevel, segments=2)
    return obj


def create_cylinder(
    name: str,
    radius: float,
    depth: float,
    z: float,
    mat: bpy.types.Material,
    vertices: int = 64,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(0.0, 0.0, z))
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.data.materials.append(mat)
    if bevel > 0.0:
        add_bevel(obj, bevel)
    return obj


def create_uv_sphere(name: str, radius: float, location: tuple[float, float, float], mat: bpy.types.Material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.008
    obj.parent = parent
    return obj


def parent(obj: bpy.types.Object, owner: bpy.types.Object) -> bpy.types.Object:
    obj.parent = owner
    return obj


def duplicate_radial(source: bpy.types.Object, name: str, angle_degrees: float, owner: bpy.types.Object):
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.rotation_euler.z = math.radians(angle_degrees)
    obj.parent = owner
    return obj


def add_textured_ground() -> bpy.types.Object:
    ground_mat = material("M_StudioGround", (0.008, 0.010, 0.014, 1.0), 0.0, 0.32)
    bpy.ops.mesh.primitive_plane_add(size=0.7, location=(0.0, 0.0, -0.020))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_mat)
    bevel = ground.modifiers.new("Soft Ground Bevel", "BEVEL")
    bevel.width = 0.01
    bevel.segments = 3
    return ground


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera_and_lights() -> bpy.types.Object:
    bpy.ops.object.camera_add(location=(0.105, -0.128, 0.092))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.lens = 62
    look_at(camera, (0.0, 0.0, 0.0))
    bpy.context.scene.camera = camera

    light_specs = [
        ("Key", (0.075, -0.045, 0.12), 14.0, 0.10, (0.72, 0.84, 1.0)),
        ("Rim", (-0.085, 0.025, 0.085), 20.0, 0.085, (0.34, 0.58, 1.0)),
        ("Fill", (0.025, 0.12, 0.055), 8.0, 0.12, (1.0, 0.52, 0.26)),
    ]
    for suffix, location, energy, size, color in light_specs:
        bpy.ops.object.light_add(type="AREA", location=location)
        lamp = bpy.context.object
        lamp.name = f"Studio{suffix}_RenderOnly"
        lamp.data.energy = energy
        lamp.data.shape = "DISK"
        lamp.data.size = size
        lamp.data.color = color
        look_at(lamp, (0.0, 0.0, 0.0))
    return camera


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def main() -> None:
    ensure_dirs()
    clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.003, 0.005, 0.012, 1.0)
    background.inputs["Strength"].default_value = 0.04
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.5

    titanium = material("M_Titanium_BeadBlast", (0.255, 0.285, 0.33, 1.0), 1.0, 0.27)
    polished = material("M_Titanium_Polished", (0.54, 0.61, 0.70, 1.0), 1.0, 0.105)
    dark_inlay = material("M_Dark_Recess", (0.018, 0.026, 0.040, 1.0), 0.78, 0.29)
    bearing_mat = material("M_Bearing_Steel", (0.48, 0.52, 0.58, 1.0), 1.0, 0.14)
    pom = material("M_Black_POM", (0.008, 0.010, 0.014, 1.0), 0.0, 0.38)

    root = empty("ThreeBladeSpinner_Root")
    rotor = empty("Rotor_Root", root)
    fixed = empty("Fixed_Root", root)
    cage = empty("BearingCage_Root", root)
    collision_root = empty("Collision_Root", root)

    # The source sector points along +X; all object origins remain exactly on
    # the mechanical axis so radial copies share a deterministic pivot.
    blade_outline = [
        (0.0185, -0.0090),
        (0.0235, -0.0168),
        (0.0335, -0.0210),
        (0.0440, -0.0115),
        (0.0490, 0.0000),
        (0.0440, 0.0115),
        (0.0335, 0.0210),
        (0.0235, 0.0168),
        (0.0185, 0.0090),
        (0.0208, 0.0000),
    ]
    inlay_outline = [
        (0.0240, -0.0071),
        (0.0290, -0.0122),
        (0.0365, -0.0112),
        (0.0432, 0.0000),
        (0.0365, 0.0112),
        (0.0290, 0.0122),
        (0.0240, 0.0071),
        (0.0260, 0.0000),
    ]
    accent_outline = [
        (0.0262, -0.0059),
        (0.0302, -0.0098),
        (0.0351, -0.0092),
        (0.0405, 0.0000),
        (0.0351, 0.0092),
        (0.0302, 0.0098),
        (0.0262, 0.0059),
        (0.0277, 0.0000),
    ]

    blade_source = create_prism("BladeShell_01", blade_outline, BODY_DEPTH, 0.0, titanium, 0.00155)
    blade_source.parent = rotor
    inlay_source = create_prism("BladeInlay_01", inlay_outline, 0.00062, BODY_DEPTH * 0.5 + 0.00010, dark_inlay, 0.00045)
    inlay_source.parent = rotor
    accent_source = create_prism("BladeAccent_01", accent_outline, 0.00024, BODY_DEPTH * 0.5 + 0.00043, polished, 0.00020)
    accent_source.parent = rotor

    visual_objects = [blade_source, inlay_source, accent_source]
    for index, angle in enumerate((120.0, 240.0), start=2):
        visual_objects.extend(
            [
                duplicate_radial(blade_source, f"BladeShell_{index:02d}", angle, rotor),
                duplicate_radial(inlay_source, f"BladeInlay_{index:02d}", angle, rotor),
                duplicate_radial(accent_source, f"BladeAccent_{index:02d}", angle, rotor),
            ]
        )

    hub = parent(create_ring("RotorHub", 0.0214, 0.0179, BODY_DEPTH, 0.0, titanium, bevel=0.00075), rotor)
    crown = parent(create_ring("RotorCrownTrim", 0.0220, 0.0200, 0.00105, BODY_DEPTH * 0.5 - 0.00030, polished, bevel=0.00028), rotor)
    outer_race = parent(create_ring("BearingOuterRace", 0.0176, 0.0142, 0.0062, 0.0, bearing_mat, bevel=0.00035), rotor)
    inner_race = parent(create_ring("BearingInnerRace", 0.0106, 0.0060, 0.0064, 0.0, bearing_mat, bevel=0.00032), fixed)
    axle = parent(create_cylinder("Axle", 0.0058, 0.0150, 0.0, bearing_mat, vertices=48, bevel=0.0004), fixed)

    ball_count = 10
    for index in range(ball_count):
        angle = math.tau * index / ball_count
        radius = 0.01225
        ball = create_uv_sphere(
            f"BearingBall_{index + 1:02d}",
            0.00135,
            (radius * math.cos(angle), radius * math.sin(angle), 0.0),
            bearing_mat,
        )
        ball.parent = cage
        visual_objects.append(ball)

    top_washer = parent(create_ring("TopWasher", 0.0157, 0.0062, 0.00075, 0.00465, pom, bevel=0.00018), fixed)
    bottom_washer = parent(create_ring("BottomWasher", 0.0157, 0.0062, 0.00075, -0.00465, pom, bevel=0.00018), fixed)
    top_cap = parent(create_cylinder("FingerCap_Top", CAP_RADIUS, CAP_DEPTH, 0.00615, titanium, vertices=48, bevel=0.00105), fixed)
    bottom_cap = parent(create_cylinder("FingerCap_Bottom", CAP_RADIUS, CAP_DEPTH, -0.00615, titanium, vertices=48, bevel=0.00105), fixed)
    top_face = parent(create_cylinder("FingerCapTop_Face", 0.0146, 0.00030, 0.00782, polished, vertices=48, bevel=0.00018), fixed)
    bottom_face = parent(create_cylinder("FingerCapBottom_Face", 0.0146, 0.00030, -0.00782, polished, vertices=48, bevel=0.00018), fixed)

    visual_objects.extend(
        [hub, crown, outer_race, inner_race, axle, top_washer, bottom_washer, top_cap, bottom_cap, top_face, bottom_face]
    )

    collision_outline = [
        (0.0185, -0.0090),
        (0.0260, -0.0180),
        (0.0415, -0.0120),
        (0.0490, 0.0),
        (0.0415, 0.0120),
        (0.0260, 0.0180),
        (0.0185, 0.0090),
    ]
    collision_source = create_prism("COL_Blade_01", collision_outline, BODY_DEPTH, 0.0, None, 0.0004)
    collision_source.parent = collision_root
    collision_source.display_type = "WIRE"
    collision_source.hide_render = True
    collision_objects = [collision_source]
    for index, angle in enumerate((120.0, 240.0), start=2):
        collision = duplicate_radial(collision_source, f"COL_Blade_{index:02d}", angle, collision_root)
        collision.hide_render = True
        collision.display_type = "WIRE"
        collision_objects.append(collision)
    hub_collision = parent(create_cylinder("COL_Hub", 0.0214, BODY_DEPTH, 0.0, pom, vertices=20, bevel=0.0), collision_root)
    hub_collision.hide_render = True
    hub_collision.display_type = "WIRE"
    collision_objects.append(hub_collision)

    # Record the intended mechanical hierarchy for downstream importers.
    root["spin_axis_blender"] = "+Z"
    root["spin_axis_unity"] = "+Y"
    root["units"] = "meters"
    root["initial_angular_velocity"] = 0.0
    rotor["mechanism_role"] = "rotating_visual"
    fixed["mechanism_role"] = "fixed_finger_caps_and_axle"
    cage["mechanism_role"] = "bearing_cage_visual"
    collision_root["mechanism_role"] = "collision_only"

    ground = add_textured_ground()
    camera = add_camera_and_lights()

    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.render.render(write_still=True)

    camera.location = (0.0, -0.003, 0.235)
    camera.data.lens = 58
    look_at(camera, (0.0, 0.0, 0.0))
    scene.render.filepath = str(TOP_PREVIEW_PATH)
    bpy.ops.render.render(write_still=True)
    camera.location = (0.105, -0.128, 0.092)
    camera.data.lens = 62
    look_at(camera, (0.0, 0.0, 0.0))

    export_objects = [root, rotor, fixed, cage] + visual_objects
    select_only(export_objects)
    bpy.ops.export_scene.fbx(
        filepath=str(FBX_PATH),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
    )
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_animations=False,
    )

    select_only([collision_root] + collision_objects)
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION_FBX_PATH),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
    )

    triangle_count = 0
    vertex_count = 0
    mesh_count = 0
    for obj in visual_objects:
        if obj.type != "MESH":
            continue
        mesh_count += 1
        vertex_count += len(obj.data.vertices)
        triangle_count += sum(max(1, len(poly.vertices) - 2) for poly in obj.data.polygons)
    world_points = [
        obj.matrix_world @ vertex.co
        for obj in visual_objects
        if obj.type == "MESH"
        for vertex in obj.data.vertices
    ]
    x_extent = max(point.x for point in world_points) - min(point.x for point in world_points)
    y_extent = max(point.y for point in world_points) - min(point.y for point in world_points)
    z_extent = max(point.z for point in world_points) - min(point.z for point in world_points)
    stats = {
        "source": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "preview": str(PREVIEW_PATH.relative_to(REPO_ROOT)),
        "topPreview": str(TOP_PREVIEW_PATH.relative_to(REPO_ROOT)),
        "units": "meters",
        "blenderSpinAxis": "+Z",
        "unitySpinAxis": "+Y",
        "overallDiameterMeters": max(x_extent, y_extent),
        "bodyDepthMeters": BODY_DEPTH,
        "assembledDepthMeters": z_extent,
        "bladeCount": 3,
        "bearingBallCount": ball_count,
        "visualMeshCount": mesh_count,
        "vertexCount": vertex_count,
        "estimatedTriangleCount": triangle_count,
        "collisionMeshCount": len(collision_objects),
        "initialAngularVelocity": 0.0,
    }
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    # Restore a useful viewport state and persist the completed source file.
    ground.hide_viewport = True
    select_only([root])
    bpy.context.view_layer.objects.active = root
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("THREE_BLADE_BLENDER_EXPORT " + json.dumps(stats, sort_keys=True))


main()
