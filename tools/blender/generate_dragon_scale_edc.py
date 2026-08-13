"""Generate the reference-driven Dragon Scale EDC spinner in Blender.

Executed inside Blender through ahujasid/blender-mcp. All dimensions are in
meters. Blender +Z is the mechanical spin axis and exports as Unity +Y.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


REPO_ROOT = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
UNITY_ROOT = REPO_ROOT / "unity" / "FidgetingApp"
SOURCE_DIR = UNITY_ROOT / "ArtSource" / "DragonScaleEDC"
MODEL_DIR = UNITY_ROOT / "Assets" / "_Fidgeting" / "Models" / "BlenderDragonScale"
ARTIFACT_DIR = UNITY_ROOT / "Artifacts" / "BlenderDragonScale"

BLEND_PATH = SOURCE_DIR / "DragonScaleEDC.blend"
FBX_PATH = MODEL_DIR / "DragonScaleEDC.fbx"
GLB_PATH = MODEL_DIR / "DragonScaleEDC.glb"
COLLISION_FBX_PATH = MODEL_DIR / "DragonScaleEDC_Collision.fbx"
HERO_PATH = ARTIFACT_DIR / "dragon-scale-edc-hero.png"
TOP_PATH = ARTIFACT_DIR / "dragon-scale-edc-top.png"
SIDE_PATH = ARTIFACT_DIR / "dragon-scale-edc-side.png"
EXPLODED_PATH = ARTIFACT_DIR / "dragon-scale-edc-exploded.png"
STATS_PATH = ARTIFACT_DIR / "dragon-scale-edc-stats.json"

BODY_DEPTH = 0.0066
CAP_RADIUS = 0.0182
CAP_DEPTH = 0.0040
PRIMARY_CIRCLE_SEGMENTS = 128
ACCENT_CIRCLE_SEGMENTS = 96
SECONDARY_CIRCLE_SEGMENTS = 72
RING_BEVEL_SEGMENTS = 2
PRIMARY_RING_BEVEL_SEGMENTS = 3
CAP_BEVEL_SEGMENTS = 4

FORBIDDEN_DECORATIVE_AXIS_RINGS = (
    "RotorCrownTrim",
    "FingerCapTop_AccentLine",
    "FingerCapBottom_AccentLine",
)


def ensure_dirs() -> None:
    for directory in (SOURCE_DIR, MODEL_DIR, ARTIFACT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def clear_scene() -> None:
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def apply_bevel(
    obj: bpy.types.Object,
    width: float,
    segments: int = 2,
    angle_degrees: float = 20.0,
) -> None:
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Machined Edge Bevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(angle_degrees)
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
    vertices = [(x, y, z_center - half) for x, y in points]
    vertices += [(x, y, z_center + half) for x, y in points]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, nxt + count, index + count))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    if bevel > 0.0:
        apply_bevel(obj, bevel, 3)
    return obj


def create_rounded_tapered_blade(
    name: str,
    inner_x: float,
    outer_x: float,
    inner_depth: float,
    outer_depth: float,
    mat: bpy.types.Material,
    outer_base_width: float = 0.0205,
    outer_tip_width: float = 0.00090,
    outer_shoulder: float = 0.0016,
) -> bpy.types.Object:
    """Create a native arrowhead frame with a recessed triangular cavity."""

    sample_count = 40

    def profile_loop(
        start_x: float,
        end_x: float,
        base_width: float,
        tip_width: float,
        shoulder: float,
    ) -> list[tuple[float, float]]:
        upper: list[tuple[float, float]] = []
        for index in range(sample_count):
            parameter = index / (sample_count - 1)
            x_value = start_x + (end_x - start_x) * parameter
            width = (
                base_width * (1.0 - parameter) ** 0.74
                + tip_width * parameter
                + shoulder * math.sin(math.pi * parameter) * (1.0 - parameter)
            )
            # Ease the two inner prongs into the hub instead of terminating
            # the broad shoulder at a sharp vertical corner.
            base_round = min(0.0028, base_width * 0.22)
            cap_progress = min(1.0, parameter / 0.10)
            width -= base_round * (1.0 - cap_progress) ** 2
            upper.append((x_value, width))
        lower = [(x_value, -width) for x_value, width in reversed(upper)]
        return upper + lower

    # The reference is a broad dragon-scale/arrow shoulder that curls around
    # the centre ring, not a long triangular paddle.  The outer shoulder is
    # deliberately wider than the 19 mm finger cap so it stays visible beside
    # the hub; the cavity remains a much smaller inset.
    outer_loop = profile_loop(
        inner_x,
        outer_x,
        outer_base_width,
        outer_tip_width,
        outer_shoulder,
    )
    inner_loop = profile_loop(0.0228, 0.0412, 0.0067, 0.00034, 0.0)
    loop_count = len(outer_loop)

    def half_depth(x_value: float) -> float:
        fraction = max(0.0, min(1.0, (x_value - inner_x) / (outer_x - inner_x)))
        return 0.5 * (inner_depth + (outer_depth - inner_depth) * fraction)

    vertices: list[tuple[float, float, float]] = []

    def append_loop(
        points: list[tuple[float, float]],
        z_resolver,
    ) -> list[int]:
        indices: list[int] = []
        for x_value, y_value in points:
            indices.append(len(vertices))
            vertices.append((x_value, y_value, z_resolver(x_value, y_value)))
        return indices

    ridge_points = [
        (
            0.55 * outer_loop[index][0] + 0.45 * inner_loop[index][0],
            0.55 * outer_loop[index][1] + 0.45 * inner_loop[index][1],
        )
        for index in range(loop_count)
    ]

    def blend_loops(
        source: list[tuple[float, float]],
        target: list[tuple[float, float]],
        amount: float,
    ) -> list[tuple[float, float]]:
        return [
            (
                (1.0 - amount) * source[index][0] + amount * target[index][0],
                (1.0 - amount) * source[index][1] + amount * target[index][1],
            )
            for index in range(loop_count)
        ]

    # Model the edge radii directly instead of applying Blender's Bevel
    # modifier.  On this converging arrow topology the modifier could leave
    # boundary edges at the tip; these nested loops stay watertight and give
    # the same soft machined transition in Unity.
    outer_side_top = append_loop(
        outer_loop,
        lambda x_value, _y: half_depth(x_value) - 0.00048,
    )
    outer_chamfer = append_loop(
        blend_loops(outer_loop, ridge_points, 0.035),
        lambda x_value, _y: half_depth(x_value) - 0.00014,
    )
    outer_top = append_loop(
        blend_loops(outer_loop, ridge_points, 0.080),
        lambda x_value, _y: half_depth(x_value),
    )
    ridge_top = append_loop(
        ridge_points,
        lambda x_value, _y: half_depth(x_value)
        + 0.00092
        * (1.0 - 0.18 * max(0.0, min(1.0, (x_value - inner_x) / (outer_x - inner_x)))),
    )
    inner_top = append_loop(
        blend_loops(inner_loop, ridge_points, 0.090),
        lambda x_value, _y: half_depth(x_value) + 0.00012,
    )
    inner_chamfer = append_loop(
        blend_loops(inner_loop, ridge_points, 0.035),
        lambda x_value, _y: half_depth(x_value) - 0.00012,
    )
    inner_side_top = append_loop(
        inner_loop,
        lambda x_value, _y: half_depth(x_value) - 0.00043,
    )
    outer_side_bottom = append_loop(
        outer_loop,
        lambda x_value, _y: -half_depth(x_value) + 0.00042,
    )
    outer_bottom = append_loop(
        blend_loops(outer_loop, ridge_points, 0.070),
        lambda x_value, _y: -half_depth(x_value),
    )
    cavity_floor = append_loop(
        inner_loop,
        lambda _x, _y: 0.00105,
    )

    bottom_center = len(vertices)
    vertices.append((0.0300, 0.0, -0.5 * inner_depth))
    floor_center = len(vertices)
    vertices.append((0.0315, 0.0, 0.00105))

    faces: list[tuple[int, ...]] = []
    for index in range(loop_count):
        nxt = (index + 1) % loop_count
        faces.extend(
            [
                (outer_top[index], outer_top[nxt], ridge_top[nxt], ridge_top[index]),
                (ridge_top[index], ridge_top[nxt], inner_top[nxt], inner_top[index]),
                (outer_side_top[index], outer_side_top[nxt], outer_chamfer[nxt], outer_chamfer[index]),
                (outer_chamfer[index], outer_chamfer[nxt], outer_top[nxt], outer_top[index]),
                (outer_side_bottom[index], outer_side_bottom[nxt], outer_side_top[nxt], outer_side_top[index]),
                (outer_bottom[index], outer_bottom[nxt], outer_side_bottom[nxt], outer_side_bottom[index]),
                (inner_top[index], inner_top[nxt], inner_chamfer[nxt], inner_chamfer[index]),
                (inner_chamfer[index], inner_chamfer[nxt], inner_side_top[nxt], inner_side_top[index]),
                (inner_side_top[index], inner_side_top[nxt], cavity_floor[nxt], cavity_floor[index]),
                (bottom_center, outer_bottom[index], outer_bottom[nxt]),
                (floor_center, cavity_floor[nxt], cavity_floor[index]),
            ]
        )

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    shade_smooth_by_angle(obj, 50.0)
    # Keep the raised machined fold around the inset legible while the outer
    # edge radii remain smooth.
    ridge_vertices = set(ridge_top)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for edge in bm.edges:
        if all(vertex.index in ridge_vertices for vertex in edge.verts):
            edge.smooth = False
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def shade_smooth_by_angle(obj: bpy.types.Object, angle_degrees: float = 38.0) -> None:
    """Smooth continuous curvature while keeping machined seams crisp."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for face in bm.faces:
        face.smooth = True
    threshold = math.radians(angle_degrees)
    for edge in bm.edges:
        edge.smooth = (
            len(edge.link_faces) == 2
            and edge.calc_face_angle(0.0) <= threshold
        )
    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)


def apply_weighted_normals(obj: bpy.types.Object) -> None:
    """Keep broad machined faces visually calm after boolean/bevel topology."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    modifier = obj.modifiers.new("Area Weighted Machined Normals", "WEIGHTED_NORMAL")
    modifier.mode = "FACE_AREA_WITH_ANGLE"
    modifier.weight = 50
    modifier.thresh = 0.01
    modifier.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)


def apply_boolean(
    target: bpy.types.Object,
    tool: bpy.types.Object,
    operation: str,
    label: str,
) -> None:
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new(label, "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = tool
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def create_faceted_prism(
    name: str,
    points: list[tuple[float, float]],
    depth: float,
    mat: bpy.types.Material,
    ridge_xy: tuple[float, float],
    ridge_height: float,
    bevel: float,
) -> bpy.types.Object:
    """Create a flat-bottomed blade with a triangulated dragon-scale crown."""
    half = depth * 0.5
    count = len(points)
    vertices = [(x, y, -half) for x, y in points]
    vertices += [(x, y, half) for x, y in points]
    vertices.append((ridge_xy[0], ridge_xy[1], half + ridge_height))
    crown = count * 2
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count)))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, nxt + count, index + count))
        faces.append((count + index, count + nxt, crown))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    apply_bevel(obj, bevel, 2)
    return obj


def create_ring(
    name: str,
    outer_radius: float,
    inner_radius: float,
    depth: float,
    z_center: float,
    mat: bpy.types.Material,
    segments: int = SECONDARY_CIRCLE_SEGMENTS,
    bevel: float = 0.00035,
    bevel_segments: int = RING_BEVEL_SEGMENTS,
) -> bpy.types.Object:
    half = depth * 0.5
    vertices: list[tuple[float, float, float]] = []
    for z_value in (z_center - half, z_center + half):
        for radius in (outer_radius, inner_radius):
            for index in range(segments):
                angle = math.tau * index / segments
                vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_value))
    bo, bi, to, ti = 0, segments, segments * 2, segments * 3
    faces: list[tuple[int, int, int, int]] = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.extend(
            [
                (bo + index, bo + nxt, to + nxt, to + index),
                (bi + nxt, bi + index, ti + index, ti + nxt),
                (to + index, to + nxt, ti + nxt, ti + index),
                (bo + nxt, bo + index, bi + index, bi + nxt),
            ]
        )
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if bevel > 0.0:
        apply_bevel(obj, bevel, bevel_segments)
    return obj


def create_cylinder(
    name: str,
    radius: float,
    depth: float,
    z_center: float,
    mat: bpy.types.Material,
    vertices: int,
    bevel: float = 0.0,
    bevel_segments: int = PRIMARY_RING_BEVEL_SEGMENTS,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=(0.0, 0.0, z_center),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.data.materials.append(mat)
    if bevel > 0.0:
        apply_bevel(obj, bevel, bevel_segments)
    return obj


def create_radial_disc(
    name: str,
    radius: float,
    depth: float,
    z_center: float,
    materials: tuple[bpy.types.Material, bpy.types.Material],
    segments: int = 24,
) -> bpy.types.Object:
    half = depth * 0.5
    vertices = [(0.0, 0.0, z_center - half), (0.0, 0.0, z_center + half)]
    for z_value in (z_center - half, z_center + half):
        for index in range(segments):
            angle = math.tau * index / segments
            vertices.append((radius * math.cos(angle), radius * math.sin(angle), z_value))
    bottom = 2
    top = 2 + segments
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.extend(
            [
                (0, bottom + nxt, bottom + index),
                (bottom + index, bottom + nxt, top + nxt, top + index),
                (1, top + index, top + nxt),
            ]
        )
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(materials[0])
    obj.data.materials.append(materials[1])
    for index, polygon in enumerate(obj.data.polygons):
        if index % 3 == 2:
            polygon.material_index = (index // 3) % 2
    return obj


def create_uv_sphere(
    name: str,
    radius: float,
    location: tuple[float, float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=14,
        ring_count=7,
        radius=radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def empty(name: str, owner: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.008
    obj.parent = owner
    return obj


def parent(obj: bpy.types.Object, owner: bpy.types.Object) -> bpy.types.Object:
    obj.parent = owner
    return obj


def radial_copy(
    source: bpy.types.Object,
    name: str,
    degrees: float,
    owner: bpy.types.Object,
) -> bpy.types.Object:
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.collection.objects.link(obj)
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    obj.rotation_euler.z = math.radians(degrees)
    obj.parent = owner
    return obj


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_studio() -> tuple[bpy.types.Object, bpy.types.Object]:
    ground_mat = material("M_StudioGround", (0.0012, 0.0015, 0.0020, 1.0), 0.0, 0.40)
    bpy.ops.mesh.primitive_plane_add(size=0.7, location=(0.0, 0.0, -0.020))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_mat)

    bpy.ops.object.camera_add(location=(0.092, -0.118, 0.142))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.lens = 68
    look_at(camera, (0.0, 0.0, 0.0))
    bpy.context.scene.camera = camera

    lights = [
        ("Key", (0.085, -0.065, 0.125), 7.0, 0.10, (0.83, 0.89, 1.0)),
        ("Rim", (-0.090, 0.030, 0.090), 9.0, 0.085, (0.38, 0.55, 1.0)),
        ("WarmFill", (0.040, 0.120, 0.055), 4.0, 0.10, (1.0, 0.47, 0.18)),
    ]
    for suffix, location, energy, size, color in lights:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Studio{suffix}_RenderOnly"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        look_at(light, (0.0, 0.0, 0.0))
    return ground, camera


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def clean_export_meshes(objects: list[bpy.types.Object]) -> None:
    """Triangulate, clean and add the tangent basis required by Unity."""
    cleaned: set[int] = set()
    for obj in objects:
        if obj.type != "MESH" or obj.data.as_pointer() in cleaned:
            continue
        cleaned.add(obj.data.as_pointer())
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if obj.name == "RotorBody_OnePiece":
            bmesh.ops.remove_doubles(
                bm,
                verts=list(bm.verts),
                dist=1.0e-7,
            )
        bmesh.ops.triangulate(
            bm,
            faces=list(bm.faces),
            quad_method="BEAUTY",
            ngon_method="BEAUTY",
        )
        if obj.name == "RotorBody_OnePiece":
            # Boolean/bevel intersections can create numerical sliver
            # triangles.  Deleting those faces opened visible saw-tooth holes
            # around the recessed fan pockets.  Collapse their shortest edge
            # instead so the shell stays closed, then retriangulate locally.
            for _ in range(5000):
                numerical_sliver = next(
                    (
                        face for face in bm.faces
                        if face.is_valid and face.calc_area() <= 1.0e-10
                    ),
                    None,
                )
                if numerical_sliver is None:
                    break
                shortest_edge = min(
                    numerical_sliver.edges,
                    key=lambda edge: edge.calc_length(),
                )
                bmesh.ops.collapse(
                    bm,
                    edges=[shortest_edge],
                    uvs=True,
                )
            bmesh.ops.triangulate(
                bm,
                faces=list(bm.faces),
                quad_method="BEAUTY",
                ngon_method="BEAUTY",
            )
        bmesh.ops.dissolve_degenerate(
            bm,
            dist=1.0e-7 if obj.name == "RotorBody_OnePiece" else 1.0e-8,
            edges=list(bm.edges),
        )
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

        # The metal shaders do not sample textures, but Unity's MikkTSpace
        # importer still needs a non-degenerate UV basis to generate tangents.
        uv_layer = bm.loops.layers.uv.verify()
        for face in bm.faces:
            normal = face.normal
            axis = max(range(3), key=lambda index: abs(normal[index]))
            for loop in face.loops:
                coordinate = loop.vert.co
                if axis == 0:
                    loop[uv_layer].uv = (coordinate.y, coordinate.z)
                elif axis == 1:
                    loop[uv_layer].uv = (coordinate.x, coordinate.z)
                else:
                    loop[uv_layer].uv = (coordinate.x, coordinate.y)
        bm.to_mesh(mesh)
        bm.free()
        mesh.validate(clean_customdata=True)
        mesh.update(calc_edges=True)


def main() -> None:
    ensure_dirs()
    clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.003, 0.004, 0.006, 1.0)
    background.inputs["Strength"].default_value = 0.045
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.45

    titanium = material("M_Titanium_Satin", (0.25, 0.28, 0.32, 1.0), 1.0, 0.25)
    polished = material("M_Titanium_Polished", (0.48, 0.54, 0.61, 1.0), 1.0, 0.12)
    face_dark = material("M_Cap_RadialDark", (0.055, 0.065, 0.078, 1.0), 0.95, 0.18)
    face_light = material("M_Cap_RadialLight", (0.14, 0.16, 0.19, 1.0), 0.95, 0.16)
    recess = material("M_Recess_Black", (0.010, 0.013, 0.018, 1.0), 0.72, 0.31)
    bearing_mat = material("M_Bearing_Steel", (0.36, 0.40, 0.45, 1.0), 1.0, 0.12)
    gold = material("M_Warm_Gold_Accent", (0.43, 0.20, 0.045, 1.0), 1.0, 0.19)
    pom = material("M_Black_POM", (0.006, 0.008, 0.011, 1.0), 0.0, 0.38)

    root = empty("DragonScaleEDC_Root")
    rotor = empty("Rotor_Root", root)
    fixed = empty("Fixed_Root", root)
    bearing_root = empty("BearingAssembly_Root", root)
    cage = empty("BearingCage_Root", bearing_root)
    top_cap_root = empty("TopCap_Root", fixed)
    top_washer_root = empty("TopWasher_Root", fixed)
    bottom_washer_root = empty("BottomWasher_Root", fixed)
    bottom_cap_root = empty("BottomCap_Root", fixed)
    collision_root = empty("Collision_Root", root)

    # The exploded reference shows one continuous rotating carrier: a central
    # bearing ring unioned to all three arrowhead shells. Build that topology
    # literally, then cut three deep triangular pockets into the upper face.
    rotor_body = create_ring(
        "RotorBody_OnePiece",
        0.0187,
        0.0152,
        BODY_DEPTH,
        0.0,
        titanium,
        segments=PRIMARY_CIRCLE_SEGMENTS,
        bevel=0.00115,
        bevel_segments=PRIMARY_RING_BEVEL_SEGMENTS,
    )
    rotor_body.parent = rotor
    pocket_floor_outline = [
        (0.0233, -0.0061),
        (0.0407, 0.0000),
        (0.0233, 0.0061),
    ]
    pocket_inlay_outline = [
        (0.0241, -0.0053),
        (0.0398, 0.0000),
        (0.0241, 0.0053),
    ]

    visual_objects: list[bpy.types.Object] = [rotor_body]
    blade_bodies: list[bpy.types.Object] = []
    for index, angle in enumerate((90.0, 210.0, 330.0), start=1):
        blade_tool = create_rounded_tapered_blade(
            f"BladeUnionTool_{index:02d}",
            0.0172,
            0.0480,
            BODY_DEPTH + 0.0005,
            0.0034,
            titanium,
        )
        blade_tool.rotation_euler.z = math.radians(angle)
        select_only([blade_tool])
        bpy.context.view_layer.objects.active = blade_tool
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        blade_bodies.append(blade_tool)

        floor = create_prism(
            f"BladePocketFloor_{index:02d}",
            pocket_floor_outline,
            0.00022,
            0.00124,
            recess,
            0.00046,
        )
        floor.rotation_euler.z = math.radians(angle)
        floor.parent = rotor
        inlay = create_prism(
            f"BladePocketInlay_{index:02d}",
            pocket_inlay_outline,
            0.00020,
            0.00146,
            polished,
            0.00034,
        )
        inlay.rotation_euler.z = math.radians(angle)
        inlay.parent = rotor
        visual_objects.extend([floor, inlay])

    # The explicit edge-radius topology is watertight, so the three roots can
    # now be genuinely unioned into the carrier.  This removes the internal
    # intersecting faces that previously appeared as dark, ragged seams under
    # Unity's metallic highlights.
    for index, blade_body in enumerate(blade_bodies, start=1):
        apply_boolean(
            rotor_body,
            blade_body,
            "UNION",
            f"Union Dragon Blade {index:02d}",
        )
    rotor_body.data.name = "RotorBody_OnePiece_Mesh"
    shade_smooth_by_angle(rotor_body, 44.0)
    # The bearing is a separate exploded component seated inside the one-piece
    # rotor, matching the supplied lower-right assembly diagram.
    bearing_shell = parent(create_ring("BearingOuterRace", 0.0149, 0.0122, 0.0054, 0.0, bearing_mat, bevel=0.00028), bearing_root)
    inner_race = parent(create_ring("BearingInnerRace", 0.0106, 0.0060, 0.0056, 0.0, bearing_mat, bevel=0.00028), bearing_root)
    axle = parent(
        create_cylinder(
            "Axle",
            0.0058,
            0.0148,
            0.0,
            bearing_mat,
            64,
            0.00032,
            PRIMARY_RING_BEVEL_SEGMENTS,
        ),
        fixed,
    )
    visual_objects.extend([bearing_shell, inner_race, axle])

    ball_count = 10
    for index in range(ball_count):
        angle = math.tau * index / ball_count
        ball = create_uv_sphere(
            f"BearingBall_{index + 1:02d}",
            0.00127,
            (0.01135 * math.cos(angle), 0.01135 * math.sin(angle), 0.0),
            bearing_mat,
        )
        ball.parent = cage
        visual_objects.append(ball)

    top_washer = parent(create_ring("TopWasher", 0.0148, 0.0061, 0.00062, 0.00406, pom, bevel=0.00014), top_washer_root)
    bottom_washer = parent(create_ring("BottomWasher", 0.0148, 0.0061, 0.00062, -0.00406, pom, bevel=0.00014), bottom_washer_root)
    top_cap = parent(
        create_cylinder(
            "FingerCap_Top",
            0.0190,
            0.0040,
            0.00622,
            titanium,
            PRIMARY_CIRCLE_SEGMENTS,
            0.00105,
            CAP_BEVEL_SEGMENTS,
        ),
        top_cap_root,
    )
    bottom_cap = parent(
        create_cylinder(
            "FingerCap_Bottom",
            0.0190,
            0.0040,
            -0.00622,
            titanium,
            PRIMARY_CIRCLE_SEGMENTS,
            0.00105,
            CAP_BEVEL_SEGMENTS,
        ),
        bottom_cap_root,
    )
    top_face = parent(
        create_cylinder(
            "FingerCapTop_BrushedFace",
            0.01845,
            0.00028,
            0.00830,
            polished,
            PRIMARY_CIRCLE_SEGMENTS,
            0.00016,
        ),
        top_cap_root,
    )
    bottom_face = parent(
        create_cylinder(
            "FingerCapBottom_BrushedFace",
            0.01845,
            0.00028,
            -0.00830,
            polished,
            PRIMARY_CIRCLE_SEGMENTS,
            0.00016,
        ),
        bottom_cap_root,
    )
    visual_objects.extend(
        [top_washer, bottom_washer, top_cap, bottom_cap, top_face, bottom_face]
    )

    remaining_axis_rings = sorted(
        obj.name
        for obj in visual_objects
        if obj.name in FORBIDDEN_DECORATIVE_AXIS_RINGS
    )
    if remaining_axis_rings:
        raise RuntimeError(
            "Rejected decorative axis rings remain: "
            + ", ".join(remaining_axis_rings)
        )

    collision_outline = [
        (0.0170, -0.0180),
        (0.0260, -0.0188),
        (0.0410, -0.0108),
        (0.0490, 0.0),
        (0.0410, 0.0108),
        (0.0260, 0.0188),
        (0.0170, 0.0180),
    ]
    col_blade = create_prism("COL_DragonBlade_01", collision_outline, BODY_DEPTH, 0.0, None, 0.00030)
    col_blade.rotation_euler.z = math.radians(90.0)
    col_blade.parent = collision_root
    col_blade.hide_render = True
    col_blade.display_type = "WIRE"
    collision_objects = [col_blade]
    for index, angle in enumerate((210.0, 330.0), start=2):
        collision = radial_copy(col_blade, f"COL_DragonBlade_{index:02d}", angle, collision_root)
        collision.hide_render = True
        collision.display_type = "WIRE"
        collision_objects.append(collision)
    col_hub = parent(create_cylinder("COL_Hub", 0.0238, BODY_DEPTH, 0.0, pom, 20), collision_root)
    col_hub.hide_render = True
    col_hub.display_type = "WIRE"
    collision_objects.append(col_hub)

    root["spin_axis_blender"] = "+Z"
    root["spin_axis_unity"] = "+Y"
    root["units"] = "meters"
    root["initial_angular_velocity"] = 0.0
    root["reference_family"] = "Dragon Scale EDC"
    rotor["mechanism_role"] = "rotating_visual"
    fixed["mechanism_role"] = "fixed_finger_caps_and_axle"
    bearing_root["mechanism_role"] = "separate_bearing_assembly"
    cage["mechanism_role"] = "bearing_cage_visual"
    collision_root["mechanism_role"] = "collision_only"

    ground, camera = create_studio()
    ground.hide_render = True
    clean_export_meshes(visual_objects + collision_objects)
    # Smooth every visible circular component after cleanup.  Smooth shading
    # alone cannot repair a low-poly silhouette, so the 72/96/128 radial density
    # above provides the real outline while weighted normals calm the wide
    # machined faces and the five-segment bevel transitions.
    circular_objects = [
        rotor_body,
        bearing_shell,
        inner_race,
        axle,
        top_washer,
        bottom_washer,
        top_cap,
        bottom_cap,
        top_face,
        bottom_face,
    ]
    for circular_object in circular_objects:
        shade_smooth_by_angle(circular_object, 42.0)
        apply_weighted_normals(circular_object)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    scene.render.filepath = str(HERO_PATH)
    bpy.ops.render.render(write_still=True)

    camera.location = (0.0, -0.002, 0.238)
    camera.data.lens = 60
    look_at(camera, (0.0, 0.0, 0.0))
    scene.render.filepath = str(TOP_PATH)
    bpy.ops.render.render(write_still=True)

    camera.location = (0.0, -0.220, 0.003)
    camera.data.lens = 82
    look_at(camera, (0.0, 0.0, 0.0))
    scene.render.filepath = str(SIDE_PATH)
    bpy.ops.render.render(write_still=True)

    # Reproduce the exact assembly order from the supplied exploded view. The
    # offsets are render-only and are restored before exporting the asset.
    top_cap_root.location.z = 0.043
    top_washer_root.location.z = 0.024
    bearing_root.location.z = 0.010
    bottom_washer_root.location.z = -0.016
    bottom_cap_root.location.z = -0.036
    camera.location = (0.155, -0.210, 0.125)
    camera.data.lens = 72
    look_at(camera, (0.0, 0.0, 0.0))
    scene.render.filepath = str(EXPLODED_PATH)
    bpy.ops.render.render(write_still=True)
    for component_root in (
        top_cap_root,
        top_washer_root,
        bearing_root,
        bottom_washer_root,
        bottom_cap_root,
    ):
        component_root.location.z = 0.0

    export_objects = [
        root,
        rotor,
        fixed,
        bearing_root,
        cage,
        top_cap_root,
        top_washer_root,
        bottom_washer_root,
        bottom_cap_root,
    ] + visual_objects
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

    mesh_objects = [obj for obj in visual_objects if obj.type == "MESH"]
    world_points = [obj.matrix_world @ vertex.co for obj in mesh_objects for vertex in obj.data.vertices]
    x_extent = max(point.x for point in world_points) - min(point.x for point in world_points)
    y_extent = max(point.y for point in world_points) - min(point.y for point in world_points)
    z_extent = max(point.z for point in world_points) - min(point.z for point in world_points)
    stats = {
        "source": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "heroPreview": str(HERO_PATH.relative_to(REPO_ROOT)),
        "topPreview": str(TOP_PATH.relative_to(REPO_ROOT)),
        "sidePreview": str(SIDE_PATH.relative_to(REPO_ROOT)),
        "explodedPreview": str(EXPLODED_PATH.relative_to(REPO_ROOT)),
        "units": "meters",
        "blenderSpinAxis": "+Z",
        "unitySpinAxis": "+Y",
        "overallDiameterMeters": max(x_extent, y_extent),
        "bodyDepthMeters": BODY_DEPTH,
        "assembledDepthMeters": z_extent,
        "bladeCount": 3,
        "bearingBallCount": ball_count,
        "visualMeshCount": len(mesh_objects),
        "vertexCount": sum(len(obj.data.vertices) for obj in mesh_objects),
        "estimatedTriangleCount": sum(
            max(1, len(polygon.vertices) - 2)
            for obj in mesh_objects
            for polygon in obj.data.polygons
        ),
        "collisionMeshCount": len(collision_objects),
        "decorativeAxisRingCount": len(remaining_axis_rings),
        "forbiddenDecorativeAxisRings": list(FORBIDDEN_DECORATIVE_AXIS_RINGS),
        "initialAngularVelocity": 0.0,
    }
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    ground.hide_viewport = True
    select_only([root])
    bpy.context.view_layer.objects.active = root
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("DRAGON_SCALE_EDC_EXPORT " + json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
