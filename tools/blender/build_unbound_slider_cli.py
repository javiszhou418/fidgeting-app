"""Build the CLI Anything "Unbound" magnetic slider DCC candidate.

The stateful cli-anything-blender project remains the human/audit manifest for
the assembly, materials, and animation.  This deterministic Blender companion
creates the exact rounded lofts, through-holes, middle-pattern geometry, PBR
source, exchange assets, validation report, and truthful multi-angle renders.

All dimensions are metres. Blender +Z is the product normal. Any future Unity
integration must apply and validate its coordinate conversion explicitly.
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
SOURCE_DIR = UNITY_ROOT / "ArtSource" / "UnboundSlider" / "CLIAnything"
ARTIFACT_DIR = UNITY_ROOT / "Artifacts" / "UnboundSliderCLIAnything"
CLI_PROJECT_PATH = SOURCE_DIR / "UnboundSliderWhiteModel.blend-cli.json"
BLEND_PATH = SOURCE_DIR / "UnboundSlider_CLI.blend"
FBX_PATH = SOURCE_DIR / "UnboundSlider_CLI.fbx"
GLB_PATH = SOURCE_DIR / "UnboundSlider_CLI.glb"
COLLISION_FBX_PATH = SOURCE_DIR / "UnboundSlider_CLI_Collision.fbx"
VALIDATION_PATH = ARTIFACT_DIR / "unbound-slider-cli-validation.json"
BRUSHED_NORMAL_PATH = SOURCE_DIR / "T_Unbound_BrushedNormal.png"
METALLIC_SMOOTHNESS_PATH = (
    SOURCE_DIR / "T_Unbound_MetallicSmoothness.png"
)

PREVIEW_PATHS = {
    "top": ARTIFACT_DIR / "01_Top.png",
    "hero": ARTIFACT_DIR / "02_AuthoredHero.png",
    "left_oblique": ARTIFACT_DIR / "03_LeftOblique.png",
    "right_oblique": ARTIFACT_DIR / "04_RightOblique.png",
    "low": ARTIFACT_DIR / "05_LowAngle.png",
    "side": ARTIFACT_DIR / "06_Side.png",
    "exploded": ARTIFACT_DIR / "07_Exploded.png",
    "goggle_detail": ARTIFACT_DIR / "08_GoggleDetail.png",
    "open": ARTIFACT_DIR / "09_OpenTravel.png",
}

# User-approved planar direction. Absolute manufacturing dimensions remain a
# nominal reconstruction because the source is a perspective photograph/video.
OUTER_WIDTH = 0.0520
OUTER_HEIGHT = 0.0360
ASSEMBLED_THICKNESS = 0.0140
OUTER_RADIUS = 0.0048
ORNAMENT_THICKNESS = 0.00130
PATTERN_THICKNESS = 0.00070
GOGGLE_RADIUS = 0.00420
GOGGLE_CENTER_X = 0.0180
GOGGLE_CENTER_Y = 0.0068
GOGGLE_BRIDGE_WIDTH = 0.0035
TRIANGLE_RADIUS = 0.00250
TRIANGLE_CENTER_X = 0.0220
SLOT_INNER_HALF_WIDTH = 0.0110
SLOT_OUTER_HALF_WIDTH = 0.0102
SLOT_INNER_Y = 0.0122
SLOT_OUTER_Y = 0.0156
MAGNET_COUNT = 6
DEFAULT_VISUAL_TRAVEL = 0.0408


def ensure_dirs() -> None:
    for directory in (
        SOURCE_DIR,
        ARTIFACT_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def load_cli_contract() -> dict:
    contract = json.loads(CLI_PROJECT_PATH.read_text(encoding="utf-8"))
    required_objects = {
        "UnboundSlider_Root",
        "TopAssembly_Root",
        "BottomAssembly_Root",
        "Top_OrnamentalShell",
        "Bottom_OrnamentalShell",
        "MiddlePatternPlate",
    }
    names = {entry["name"] for entry in contract["objects"]}
    missing = sorted(required_objects - names)
    if missing:
        raise RuntimeError(f"CLI project is missing required objects: {missing}")
    white_metal = next(
        material for material in contract["materials"]
        if material["name"] == "WhiteMetal"
    )
    if white_metal["metallic"] < 0.95 or white_metal["roughness"] > 0.25:
        raise RuntimeError("CLI production gold material was not persisted.")
    return contract


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
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


def socket(node: bpy.types.Node, *names: str):
    for name in names:
        candidate = node.inputs.get(name)
        if candidate is not None:
            return candidate
    return None


def machined_material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    *,
    anisotropy: float = 0.0,
    micro_strength: float = 0.0,
    micro_scale: float = 420.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.metallic = metallic
    material.roughness = roughness
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    socket(bsdf, "Base Color").default_value = color
    socket(bsdf, "Metallic").default_value = metallic
    socket(bsdf, "Roughness").default_value = roughness
    anisotropy_input = socket(bsdf, "Anisotropic IOR Level", "Anisotropic")
    if anisotropy_input is not None:
        anisotropy_input.default_value = anisotropy
    if micro_strength > 0.0:
        texcoord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.noise_dimensions = "3D"
        socket(noise, "Scale").default_value = micro_scale
        socket(noise, "Detail").default_value = 3.0
        socket(noise, "Roughness").default_value = 0.64
        bump = nodes.new("ShaderNodeBump")
        socket(bump, "Strength").default_value = micro_strength
        socket(bump, "Distance").default_value = 0.000035
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], socket(bsdf, "Normal"))
    return material


def create_empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.008
    obj.parent = parent
    return obj


def select_only(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def apply_modifier(obj: bpy.types.Object, modifier: bpy.types.Modifier) -> None:
    select_only([obj])
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def rounded_box(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material | None,
    parent: bpy.types.Object | None,
    *,
    segments: int = 6,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material is not None:
        obj.data.materials.append(material)
    obj.parent = parent
    if radius > 0.0:
        bevel = obj.modifiers.new("MachinedRadius", "BEVEL")
        bevel.width = radius
        bevel.segments = segments
        bevel.limit_method = "ANGLE"
        bevel.angle_limit = math.radians(30.0)
        bevel.harden_normals = True
        apply_modifier(obj, bevel)
    return obj


def cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    material: bpy.types.Material | None,
    parent: bpy.types.Object | None,
    *,
    vertices: int = 64,
    bevel: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.parent = parent
    if material is not None:
        obj.data.materials.append(material)
    if bevel > 0.0:
        modifier = obj.modifiers.new("EdgeRadius", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        modifier.harden_normals = True
        apply_modifier(obj, modifier)
    return obj


def rounded_polygon_points(
    points: list[tuple[float, float]],
    radius: float,
    segments: int = 5,
) -> list[tuple[float, float]]:
    """Round a convex CCW polygon without adding a geometry dependency."""
    result: list[tuple[float, float]] = []
    for index, current_tuple in enumerate(points):
        previous = Vector(points[index - 1])
        current = Vector(current_tuple)
        following = Vector(points[(index + 1) % len(points)])
        incoming = (current - previous).normalized()
        outgoing = (following - current).normalized()
        interior = math.acos(max(-1.0, min(1.0, (-incoming).dot(outgoing))))
        tangent = min(
            radius / max(1.0e-8, math.tan(interior * 0.5)),
            (current - previous).length * 0.30,
            (following - current).length * 0.30,
        )
        first = current - incoming * tangent
        second = current + outgoing * tangent
        center_direction = (-incoming + outgoing).normalized()
        center = current + center_direction * radius / max(
            1.0e-8,
            math.sin(interior * 0.5),
        )
        start = math.atan2(first.y - center.y, first.x - center.x)
        finish = math.atan2(second.y - center.y, second.x - center.x)
        while finish <= start:
            finish += math.tau
        for step in range(segments + 1):
            angle = start + (finish - start) * step / segments
            result.append(
                (
                    center.x + math.cos(angle) * radius,
                    center.y + math.sin(angle) * radius,
                )
            )
    return result


def prism_from_polygon(
    name: str,
    points: list[tuple[float, float]],
    depth: float,
    center_z: float,
    material: bpy.types.Material | None,
    parent: bpy.types.Object | None,
) -> bpy.types.Object:
    count = len(points)
    bottom = center_z - depth * 0.5
    top = center_z + depth * 0.5
    vertices = [(x, y, bottom) for x, y in points] + [
        (x, y, top) for x, y in points
    ]
    faces: list[tuple[int, ...]] = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    if material is not None:
        mesh.materials.append(material)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    return obj


def rounded_rect_prism(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material | None,
    parent: bpy.types.Object | None,
    *,
    corner_segments: int = 8,
    edge_bevel: float = 0.0,
) -> bpy.types.Object:
    """Create a true planar rounded-rectangle prism.

    Blender's cube Bevel modifier treats the large XY corner radius as a Z edge
    radius too. On a thin face plate that consumes the whole top surface and
    produces non-planar triangle highlights after FBX import. This construction
    keeps the approved XY radius independent from the part thickness.
    """
    width, height, depth = dimensions
    outline = rounded_polygon_points(
        [
            (-width * 0.5, -height * 0.5),
            (width * 0.5, -height * 0.5),
            (width * 0.5, height * 0.5),
            (-width * 0.5, height * 0.5),
        ],
        min(radius, width * 0.49, height * 0.49),
        corner_segments,
    )
    obj = prism_from_polygon(
        name,
        outline,
        depth,
        location[2],
        material,
        parent,
    )
    obj.location.x = location[0]
    obj.location.y = location[1]
    if edge_bevel > 0.0:
        bevel = obj.modifiers.new("MachinedEdgeMicroChamfer", "BEVEL")
        bevel.width = min(edge_bevel, depth * 0.24)
        bevel.segments = 3
        bevel.limit_method = "ANGLE"
        bevel.angle_limit = math.radians(24.0)
        bevel.harden_normals = True
        apply_modifier(obj, bevel)
    return obj


def boolean_difference(target: bpy.types.Object, cutter: bpy.types.Object) -> None:
    modifier = target.modifiers.new(f"Cut_{cutter.name}", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    apply_modifier(target, modifier)
    bpy.data.objects.remove(cutter, do_unlink=True)


def clean_mesh(obj: bpy.types.Object) -> None:
    """Remove boolean slivers while preserving the authored closed surface."""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1.0e-8)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1.0e-9)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)


def triangulate_mesh(obj: bpy.types.Object) -> None:
    """Resolve concave boolean faces in Blender before FBX export.

    Leaving aperture faces as n-gons lets different importers choose different
    diagonals; Unity can then bridge across a hole and render giant triangular
    facets. The authored triangulation is deterministic and preview-identical.
    """
    if obj.type != "MESH":
        return
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(
        bm,
        faces=list(bm.faces),
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update(calc_edges=True)


def create_goggle_cutters(prefix: str, y: float, center_z: float) -> list[bpy.types.Object]:
    depth = ORNAMENT_THICKNESS + 0.004
    cutters = [
        cylinder(
            f"{prefix}_LeftCircle",
            GOGGLE_RADIUS,
            depth,
            (-GOGGLE_CENTER_X, y, center_z),
            None,
            None,
            vertices=96,
        ),
        rounded_box(
            f"{prefix}_StraightWaist",
            (GOGGLE_CENTER_X * 2.0, GOGGLE_BRIDGE_WIDTH, depth),
            (0.0, y, center_z),
            GOGGLE_BRIDGE_WIDTH * 0.48,
            None,
            None,
            segments=5,
        ),
        cylinder(
            f"{prefix}_RightCircle",
            GOGGLE_RADIUS,
            depth,
            (GOGGLE_CENTER_X, y, center_z),
            None,
            None,
            vertices=96,
        ),
    ]
    return cutters


def create_ornamental_shell(
    name: str,
    center_z: float,
    gold: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    shell = rounded_rect_prism(
        name,
        (OUTER_WIDTH, OUTER_HEIGHT, ORNAMENT_THICKNESS),
        (0.0, 0.0, center_z),
        OUTER_RADIUS,
        gold,
        parent,
        corner_segments=10,
    )
    cutter_depth = ORNAMENT_THICKNESS + 0.004
    cutters: list[bpy.types.Object] = []
    cutters.extend(create_goggle_cutters(f"{name}_GoggleUpper", GOGGLE_CENTER_Y, center_z))
    cutters.extend(create_goggle_cutters(f"{name}_GoggleLower", -GOGGLE_CENTER_Y, center_z))

    top_slot = [
        (-SLOT_INNER_HALF_WIDTH, SLOT_INNER_Y),
        (SLOT_INNER_HALF_WIDTH, SLOT_INNER_Y),
        (SLOT_OUTER_HALF_WIDTH, SLOT_OUTER_Y),
        (-SLOT_OUTER_HALF_WIDTH, SLOT_OUTER_Y),
    ]
    bottom_slot = [(x, -y) for x, y in reversed(top_slot)]
    cutters.append(
        prism_from_polygon(
            f"{name}_UpperTrapezoid",
            rounded_polygon_points(top_slot, 0.00065, 6),
            cutter_depth,
            center_z,
            None,
            None,
        )
    )
    cutters.append(
        prism_from_polygon(
            f"{name}_LowerTrapezoid",
            rounded_polygon_points(bottom_slot, 0.00065, 6),
            cutter_depth,
            center_z,
            None,
            None,
        )
    )

    for side, angle in ((-1.0, 0.0), (1.0, math.pi)):
        triangle = [
            (
                side * TRIANGLE_CENTER_X + math.cos(angle + step * math.tau / 3.0) * TRIANGLE_RADIUS,
                math.sin(angle + step * math.tau / 3.0) * TRIANGLE_RADIUS,
            )
            for step in range(3)
        ]
        area = sum(
            triangle[i][0] * triangle[(i + 1) % 3][1]
            - triangle[(i + 1) % 3][0] * triangle[i][1]
            for i in range(3)
        )
        if area < 0.0:
            triangle.reverse()
        cutters.append(
            prism_from_polygon(
                f"{name}_{'Left' if side < 0 else 'Right'}Triangle",
                rounded_polygon_points(triangle, 0.00048, 6),
                cutter_depth,
                center_z,
                None,
                None,
            )
        )

    for cutter in cutters:
        boolean_difference(shell, cutter)

    edge = shell.modifiers.new("CutEdgeMicroChamfer", "BEVEL")
    edge.width = 0.00022
    edge.segments = 3
    edge.limit_method = "ANGLE"
    edge.angle_limit = math.radians(24.0)
    edge.harden_normals = True
    apply_modifier(shell, edge)
    clean_mesh(shell)
    return shell


def create_border_ring(
    name: str,
    center_z: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    ring = rounded_rect_prism(
        name,
        (0.0502, 0.0342, 0.00030),
        (0.0, 0.0, center_z),
        0.0040,
        material,
        parent,
        corner_segments=8,
    )
    inner = rounded_rect_prism(
        f"{name}_InnerCut",
        (0.0478, 0.0318, 0.0012),
        (0.0, 0.0, center_z),
        0.0032,
        None,
        None,
        corner_segments=8,
    )
    boolean_difference(ring, inner)
    edge = ring.modifiers.new("RingEdgeMicroChamfer", "BEVEL")
    edge.width = 0.000055
    edge.segments = 2
    edge.limit_method = "ANGLE"
    edge.angle_limit = math.radians(24.0)
    edge.harden_normals = True
    apply_modifier(ring, edge)
    return ring


def polyline_ribbon(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    curve.resolution_u = 1
    curve.use_fill_caps = True
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    curve.materials.append(material)
    select_only([obj])
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def create_middle_pattern(
    prefix: str,
    center_z: float,
    facing: float,
    middle_material: bpy.types.Material,
    groove_material: bpy.types.Material,
    screw_material: bpy.types.Material,
    parent: bpy.types.Object,
) -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    plate = rounded_rect_prism(
        f"{prefix}_MiddlePatternPlate",
        (0.0492, 0.0332, PATTERN_THICKNESS),
        (0.0, 0.0, center_z),
        0.0040,
        middle_material,
        parent,
        corner_segments=8,
        edge_bevel=0.00012,
    )
    face_z = center_z + facing * (PATTERN_THICKNESS * 0.5 + 0.00010)
    grooves: list[bpy.types.Object] = []
    for row in range(6):
        outer_y = 0.0042 + row * 0.00195
        inner_y = outer_y * 0.58
        for x_sign in (-1.0, 1.0):
            for y_sign in (-1.0, 1.0):
                points = [
                    (x_sign * 0.0210, y_sign * outer_y, face_z),
                    (x_sign * 0.0140, y_sign * outer_y, face_z),
                    (x_sign * 0.0042, y_sign * inner_y, face_z),
                ]
                grooves.append(
                    polyline_ribbon(
                        f"{prefix}_PatternGroove_{row}_{int(x_sign)}_{int(y_sign)}",
                        points,
                        0.00018,
                        groove_material,
                        parent,
                    )
                )
    screw = cylinder(
        f"{prefix}_CenterScrew",
        0.00145,
        0.00048,
        (0.0, 0.0, face_z + facing * 0.00016),
        screw_material,
        parent,
        vertices=48,
        bevel=0.00016,
    )
    if facing < 0.0:
        screw.rotation_euler.x = math.pi
    socket_insert = cylinder(
        f"{prefix}_CenterScrewSocket",
        0.00046,
        0.00010,
        (0.0, 0.0, face_z + facing * 0.00042),
        groove_material,
        parent,
        vertices=6,
    )
    if facing < 0.0:
        socket_insert.rotation_euler.x = math.pi
    return plate, grooves + [screw, socket_insert]


def add_visual_magnets(
    parent: bpy.types.Object,
    prefix: str,
    z: float,
    material: bpy.types.Material,
    facing: float,
) -> list[bpy.types.Object]:
    magnets: list[bpy.types.Object] = []
    for index in range(MAGNET_COUNT):
        x = -0.020 + index * 0.008
        magnet = cylinder(
            f"{prefix}_Magnet_{index + 1:02d}",
            0.0027,
            0.00090,
            (x, 0.0, z),
            material,
            parent,
            vertices=48,
            bevel=0.00016,
        )
        if facing < 0.0:
            magnet.rotation_euler.x = math.pi
        magnets.append(magnet)
    return magnets


def create_texture_maps() -> None:
    size = 256
    normal_pixels: list[float] = []
    mask_pixels: list[float] = []
    for y in range(size):
        for x in range(size):
            phase = x * 0.19 + math.sin(y * 0.071) * 2.4
            scratch = math.sin(phase) * 0.020 + math.sin(phase * 2.71) * 0.008
            normal_pixels.extend((0.5 + scratch, 0.5, 1.0, 1.0))
            smoothness = 0.80 + math.sin(phase * 0.47) * 0.035
            mask_pixels.extend((1.0, 0.0, 0.0, smoothness))

    for name, path, pixels, colorspace in (
        ("T_Unbound_BrushedNormal", BRUSHED_NORMAL_PATH, normal_pixels, "Non-Color"),
        (
            "T_Unbound_MetallicSmoothness",
            METALLIC_SMOOTHNESS_PATH,
            mask_pixels,
            "Non-Color",
        ),
    ):
        image = bpy.data.images.new(name, width=size, height=size, alpha=True)
        image.pixels.foreach_set(pixels)
        image.colorspace_settings.name = colorspace
        image.filepath_raw = str(path)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_studio(
    ground_material: bpy.types.Material,
) -> tuple[bpy.types.Object, bpy.types.Object, list[bpy.types.Object]]:
    bpy.ops.mesh.primitive_plane_add(size=0.46, location=(0.0, 0.0, -0.0100))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_material)

    bpy.ops.object.camera_add(location=(0.082, -0.102, 0.094))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.lens = 68
    camera.data.sensor_width = 36
    look_at(camera, (0.0, 0.0, 0.0))
    bpy.context.scene.camera = camera

    specifications = [
        ("Key5000K", (-0.070, -0.060, 0.125), 6.0, 0.105, 0.070, (1.0, 0.76, 0.55)),
        ("Rim3200K", (0.095, 0.030, 0.070), 3.5, 0.080, 0.045, (1.0, 0.34, 0.11)),
        ("Fill6500K", (0.020, 0.110, 0.080), 2.5, 0.115, 0.075, (0.45, 0.66, 1.0)),
        ("TopStrip", (-0.010, 0.000, 0.155), 1.5, 0.140, 0.022, (0.82, 0.90, 1.0)),
    ]
    lights: list[bpy.types.Object] = []
    for suffix, location, energy, width, height, color in specifications:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Studio{suffix}_RenderOnly"
        light.data.energy = energy
        light.data.shape = "RECTANGLE"
        light.data.size = width
        light.data.size_y = height
        light.data.color = color
        look_at(light, (0.0, 0.0, 0.0))
        lights.append(light)
    return ground, camera, lights


def render_view(
    camera: bpy.types.Object,
    key: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    *,
    orthographic: bool = False,
    ortho_scale: float = 0.068,
) -> None:
    camera.location = location
    camera.data.lens = lens
    camera.data.type = "ORTHO" if orthographic else "PERSP"
    camera.data.ortho_scale = ortho_scale
    look_at(camera, target)
    bpy.context.scene.render.filepath = str(PREVIEW_PATHS[key])
    bpy.ops.render.render(write_still=True)


def exact_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    bpy.context.view_layer.update()
    points = [
        obj.matrix_world @ vertex.co
        for obj in objects
        if obj.type == "MESH" and not obj.hide_render
        for vertex in obj.data.vertices
    ]
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def mesh_audit(obj: bpy.types.Object) -> dict[str, int]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundaryEdges": sum(1 for edge in bm.edges if len(edge.link_faces) == 1),
        "nonManifoldEdges": sum(1 for edge in bm.edges if len(edge.link_faces) != 2),
        "zeroAreaFaces": sum(1 for face in bm.faces if face.calc_area() <= 1.0e-16),
    }
    bm.free()
    return result


def create_collision(parent: bpy.types.Object) -> bpy.types.Object:
    collision = rounded_box(
        "COL_UnboundSlider_Surface",
        (OUTER_WIDTH, OUTER_HEIGHT, ASSEMBLED_THICKNESS),
        (0.0, 0.0, 0.0),
        OUTER_RADIUS,
        None,
        parent,
        segments=4,
    )
    collision.hide_render = True
    collision.display_type = "WIRE"
    return collision


def main() -> None:
    ensure_dirs()
    cli_contract = load_cli_contract()
    clear_scene()
    create_texture_maps()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    scene.world.color = (0.006, 0.008, 0.013)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.006, 0.008, 0.013, 1.0)
    background.inputs["Strength"].default_value = 0.16
    scene.view_settings.look = "AgX - Medium High Contrast"

    gold = machined_material(
        "M_Unbound_Gold",
        (0.55, 0.15, 0.012, 1.0),
        1.0,
        0.20,
        anisotropy=0.48,
        micro_strength=0.055,
        micro_scale=520.0,
    )
    gold_edge = machined_material(
        "M_Unbound_GoldEdge",
        (0.82, 0.34, 0.030, 1.0),
        1.0,
        0.11,
        anisotropy=0.62,
    )
    graphite = machined_material(
        "M_Unbound_Graphite",
        (0.006, 0.010, 0.018, 1.0),
        0.62,
        0.40,
        micro_strength=0.12,
        micro_scale=720.0,
    )
    middle = machined_material(
        "M_Unbound_Middle",
        (0.075, 0.105, 0.155, 1.0),
        0.88,
        0.36,
        micro_strength=0.08,
        micro_scale=680.0,
    )
    groove = machined_material(
        "M_Unbound_Groove",
        (0.006, 0.010, 0.017, 1.0),
        0.42,
        0.52,
    )
    steel = machined_material(
        "M_Unbound_Steel",
        (0.32, 0.39, 0.48, 1.0),
        1.0,
        0.17,
        anisotropy=0.35,
    )
    contact = machined_material(
        "M_Unbound_Contact",
        (0.004, 0.007, 0.012, 1.0),
        0.0,
        0.62,
    )
    brass = machined_material(
        "M_Unbound_Brass",
        (0.36, 0.11, 0.012, 1.0),
        0.93,
        0.29,
    )
    ground_material = machined_material(
        "M_StudioGround_RenderOnly",
        (0.004, 0.006, 0.011, 1.0),
        0.10,
        0.78,
    )

    root = create_empty("UnboundSlider_Root")
    top = create_empty("TopAssembly", root)
    bottom = create_empty("BottomAssembly", root)
    collision_root = create_empty("Collision_Root")

    visual_objects: list[bpy.types.Object] = []
    top_carrier = rounded_box(
        "Top_CarrierShell",
        (0.0500, 0.0340, 0.00470),
        (0.0, 0.0, 0.00260),
        0.0041,
        graphite,
        top,
        segments=8,
    )
    visual_objects.append(top_carrier)
    top_contact = rounded_box(
        "Top_LowFrictionContact",
        (0.0474, 0.0306, 0.00034),
        (0.0, 0.0, 0.00017),
        0.0034,
        contact,
        top,
        segments=6,
    )
    visual_objects.append(top_contact)

    top_pattern, top_pattern_details = create_middle_pattern(
        "Top",
        0.00525,
        1.0,
        middle,
        groove,
        steel,
        top,
    )
    visual_objects.extend([top_pattern] + top_pattern_details)
    top_ornamental = create_ornamental_shell(
        "Top_OrnamentalShell",
        0.00625,
        gold,
        top,
    )
    visual_objects.append(top_ornamental)
    top_rim = create_border_ring(
        "Top_GoldRim",
        0.00685,
        gold_edge,
        top,
    )
    visual_objects.append(top_rim)

    bottom_carrier = rounded_box(
        "Bottom_CarrierShell",
        (0.0500, 0.0340, 0.00470),
        (0.0, 0.0, -0.00260),
        0.0041,
        graphite,
        bottom,
        segments=8,
    )
    visual_objects.append(bottom_carrier)
    bottom_contact = rounded_box(
        "Bottom_LowFrictionContact",
        (0.0474, 0.0306, 0.00034),
        (0.0, 0.0, -0.00017),
        0.0034,
        contact,
        bottom,
        segments=6,
    )
    visual_objects.append(bottom_contact)
    bottom_pattern, bottom_pattern_details = create_middle_pattern(
        "Bottom",
        -0.00525,
        -1.0,
        middle,
        groove,
        steel,
        bottom,
    )
    visual_objects.extend([bottom_pattern] + bottom_pattern_details)
    bottom_ornamental = create_ornamental_shell(
        "Bottom_OrnamentalShell",
        -0.00625,
        gold,
        bottom,
    )
    visual_objects.append(bottom_ornamental)
    bottom_rim = create_border_ring(
        "Bottom_GoldRim",
        -0.00685,
        gold_edge,
        bottom,
    )
    visual_objects.append(bottom_rim)

    base_rail_left = rounded_box(
        "Bottom_Rail_Left",
        (0.0450, 0.0018, 0.00078),
        (0.0, -0.0108, 0.00008),
        0.00075,
        contact,
        bottom,
        segments=4,
    )
    base_rail_right = rounded_box(
        "Bottom_Rail_Right",
        (0.0450, 0.0018, 0.00078),
        (0.0, 0.0108, 0.00008),
        0.00075,
        contact,
        bottom,
        segments=4,
    )
    visual_objects.extend((base_rail_left, base_rail_right))
    visual_objects.extend(add_visual_magnets(bottom, "Bottom", 0.00012, steel, 1.0))
    visual_objects.extend(add_visual_magnets(top, "Top", -0.00012, steel, -1.0))

    for side in (-1.0, 1.0):
        fork = rounded_box(
            f"Top_BrassFork_{'Left' if side < 0 else 'Right'}",
            (0.0260, 0.0011, 0.00048),
            (0.0, side * 0.0064, -0.00036),
            0.00020,
            brass,
            top,
            segments=3,
        )
        visual_objects.append(fork)

    for visual_object in visual_objects:
        triangulate_mesh(visual_object)

    collision = create_collision(collision_root)

    root["reference_width_mm"] = OUTER_WIDTH * 1000.0
    root["reference_height_mm"] = OUTER_HEIGHT * 1000.0
    root["reference_thickness_mm"] = ASSEMBLED_THICKNESS * 1000.0
    root["goggle_circle_radius_mm"] = GOGGLE_RADIUS * 1000.0
    root["goggle_bridge_width_mm"] = GOGGLE_BRIDGE_WIDTH * 1000.0
    root["goggle_centers_horizontal"] = True
    root["main_openings_center_symmetric"] = True
    root["triangle_centers_on_midline"] = True
    root["visual_magnet_count"] = MAGNET_COUNT
    root["interaction_authority"] = "Unity LinearMagneticDetentProfile"
    root["candidate_status"] = "DCC candidate; Unity visual rejected in round 5"

    ground, camera, lights = create_studio(ground_material)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    render_view(camera, "top", (0.0, 0.0, 0.145), (0.0, 0.0, 0.0), 70, orthographic=True, ortho_scale=0.064)
    render_view(camera, "hero", (0.082, -0.104, 0.090), (0.0, 0.0, 0.0), 72)
    render_view(camera, "left_oblique", (-0.085, -0.106, 0.074), (0.0, 0.0, 0.0), 74)
    render_view(camera, "right_oblique", (0.085, -0.106, 0.074), (0.0, 0.0, 0.0), 74)
    render_view(camera, "low", (0.076, -0.128, 0.026), (0.0, 0.0, 0.0), 78)
    render_view(camera, "side", (0.0, -0.150, 0.004), (0.0, 0.0, 0.0), 80)

    assembled_locations = {obj.name: obj.location.copy() for obj in visual_objects}
    top_ornamental.location.z += 0.042
    top_rim.location.z += 0.042
    for obj in [top_pattern] + top_pattern_details:
        obj.location.z += 0.025
    top_carrier.location.z += 0.010
    top_contact.location.z += 0.005
    for obj in visual_objects:
        if obj.parent == bottom and (
            "Ornamental" in obj.name or obj.name == "Bottom_GoldRim"
        ):
            obj.location.z -= 0.035
    for obj in [bottom_pattern] + bottom_pattern_details:
        obj.location.z -= 0.020
    render_view(camera, "exploded", (0.105, -0.142, 0.102), (0.0, 0.0, 0.004), 74)
    for obj in visual_objects:
        obj.location = assembled_locations[obj.name]

    render_view(camera, "goggle_detail", (0.0, 0.0, 0.115), (0.0, 0.0, 0.005), 88, orthographic=True, ortho_scale=0.058)
    top.location.x = DEFAULT_VISUAL_TRAVEL
    render_view(camera, "open", (0.105, -0.130, 0.086), (0.018, 0.0, 0.0), 74)
    top.location.x = 0.0

    export_objects = [root, top, bottom] + visual_objects
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
    select_only([collision_root, collision])
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
    bounds_min, bounds_max = exact_bounds(visual_objects)
    extents = bounds_max - bounds_min
    triangle_count = sum(
        max(1, len(polygon.vertices) - 2)
        for obj in visual_objects
        if obj.type == "MESH"
        for polygon in obj.data.polygons
    )
    triangle_vertical_extent = TRIANGLE_RADIUS * math.sin(math.tau / 3.0)
    aperture_gap = (GOGGLE_CENTER_Y - GOGGLE_RADIUS) - triangle_vertical_extent
    slot_gap = SLOT_INNER_Y - (GOGGLE_CENTER_Y + GOGGLE_RADIUS)
    validation = {
        "status": "dcc_candidate_unity_visual_rejected_round5",
        "cliProject": str(CLI_PROJECT_PATH.relative_to(REPO_ROOT)),
        "blend": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "shippingFbx": None,
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "previews": {
            key: str(path.relative_to(REPO_ROOT)) for key, path in PREVIEW_PATHS.items()
        },
        "contract": {
            "overallMm": [OUTER_WIDTH * 1000.0, OUTER_HEIGHT * 1000.0, ASSEMBLED_THICKNESS * 1000.0],
            "outerCornerRadiusMm": OUTER_RADIUS * 1000.0,
            "openingCountPerFace": 6,
            "goggleCircleRadiusMm": GOGGLE_RADIUS * 1000.0,
            "goggleCircleCentersMm": [
                [-GOGGLE_CENTER_X * 1000.0, GOGGLE_CENTER_Y * 1000.0],
                [GOGGLE_CENTER_X * 1000.0, GOGGLE_CENTER_Y * 1000.0],
                [-GOGGLE_CENTER_X * 1000.0, -GOGGLE_CENTER_Y * 1000.0],
                [GOGGLE_CENTER_X * 1000.0, -GOGGLE_CENTER_Y * 1000.0],
            ],
            "goggleBridgeWidthMm": GOGGLE_BRIDGE_WIDTH * 1000.0,
            "goggleCenterHeightErrorMm": 0.0,
            "leftRightMirrorErrorMm": 0.0,
            "upperLowerCenterSymmetryErrorMm": 0.0,
            "triangleCenterlineErrorMm": 0.0,
            "mainToTriangleMinimumGapMm": aperture_gap * 1000.0,
            "mainToTrapezoidMinimumGapMm": slot_gap * 1000.0,
            "visualMagnetCount": MAGNET_COUNT,
        },
        "measured": {
            "overallMm": [extents.x * 1000.0, extents.y * 1000.0, extents.z * 1000.0],
            "meshCount": sum(1 for obj in visual_objects if obj.type == "MESH"),
            "triangleCount": triangle_count,
            "topOrnamentalAudit": mesh_audit(top_ornamental),
            "bottomOrnamentalAudit": mesh_audit(bottom_ornamental),
        },
        "materials": {
            "gold": {"metallic": 1.0, "roughness": 0.20, "anisotropy": 0.48},
            "goldEdge": {"metallic": 1.0, "roughness": 0.11},
            "middle": {"metallic": 0.88, "roughness": 0.36},
            "graphite": {"metallic": 0.62, "roughness": 0.40},
        },
        "cliObjectCount": len(cli_contract["objects"]),
        "interaction": {
            "shippingController": "EdcSliderController",
            "detentAuthority": "LinearMagneticDetentProfile",
            "motionChanged": False,
            "initialVelocityMetersPerSecond": 0.0,
        },
    }
    if validation["measured"]["topOrnamentalAudit"]["nonManifoldEdges"] != 0:
        raise RuntimeError("Top ornamental shell is not manifold.")
    if validation["measured"]["bottomOrnamentalAudit"]["nonManifoldEdges"] != 0:
        raise RuntimeError("Bottom ornamental shell is not manifold.")
    if aperture_gap <= 0.0 or slot_gap <= 0.0:
        raise RuntimeError("Approved apertures overlap after exact reconstruction.")
    if triangle_count > 120_000:
        raise RuntimeError(f"Mobile visual budget exceeded: {triangle_count} triangles")
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    ground.hide_viewport = True
    for light in lights:
        light.hide_viewport = True
    select_only([root])
    bpy.context.view_layer.objects.active = root
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("UNBOUND_SLIDER_CLI_EXPORT " + json.dumps(validation, sort_keys=True))


if __name__ == "__main__":
    main()
