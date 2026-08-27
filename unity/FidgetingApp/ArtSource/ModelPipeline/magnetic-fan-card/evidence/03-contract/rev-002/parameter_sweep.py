"""Render visual camera and light choices from the locked fan-card contract.

This is Gate 03 decision evidence, not a shipping asset. Product dimensions,
pivot, layer spacing, Q/K/A order, and face-art coordinates come from the
canonical fan-card guardrails and Unity specifications.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[8]
OUTPUT = SCRIPT.parent / "parameter-sweep"
BLEND = SCRIPT.parent / "fan-card-parameter-sweep.blend"
FONT = REPO / "unity/FidgetingApp/ArtSource/FanCard/Oxanium-700.ttf"

CARD_W = 0.0635
CARD_H = 0.0889
CARD_T = 0.0025
RADIUS = CARD_W * 0.06
FACE_INSET = 0.0005
GAP = 0.001
PITCH = CARD_T + GAP
PIVOT_X = CARD_W * 0.5 - RADIUS
PIVOT_Y = CARD_H * 0.5 - RADIUS
CENTER = Vector((-PIVOT_X, -PIVOT_Y, 0.0))
HOLE_R = 0.00215
CAP_R = 0.00207
CAP_H = 0.00065


def clean() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights):
        for block in list(blocks):
            if block.users == 0:
                blocks.remove(block)


def rounded_outline(width: float, height: float, radius: float,
                    center: Vector, segments: int = 12) -> list[Vector]:
    half_w = width * 0.5
    half_h = height * 0.5
    corners = [
        (half_w - radius, half_h - radius, 0.0),
        (-half_w + radius, half_h - radius, 90.0),
        (-half_w + radius, -half_h + radius, 180.0),
        (half_w - radius, -half_h + radius, 270.0),
    ]
    points: list[Vector] = []
    for cx, cy, start in corners:
        for index in range(segments + 1):
            angle = math.radians(start + index * 90.0 / segments)
            points.append(Vector((
                center.x + cx + math.cos(angle) * radius,
                center.y + cy + math.sin(angle) * radius,
            )))
    return points


def prism(name: str, outline: list[Vector], thickness: float,
          z_center: float, material: bpy.types.Material,
          bevel: float = 0.00022) -> bpy.types.Object:
    count = len(outline)
    z0 = z_center - thickness * 0.5
    z1 = z_center + thickness * 0.5
    vertices = [(p.x, p.y, z0) for p in outline]
    vertices += [(p.x, p.y, z1) for p in outline]
    polygon = [Vector((p.x, p.y, 0.0)) for p in outline]
    triangles = tessellate_polygon([polygon])
    lookup = {(round(p.x, 9), round(p.y, 9)): i
              for i, p in enumerate(polygon)}
    faces: list[tuple[int, ...]] = []
    for tri in triangles:
        if isinstance(tri[0], int):
            ids = tuple(tri)
        else:
            ids = tuple(
                lookup[(round(p.x, 9), round(p.y, 9))] for p in tri)
        faces.append(tuple(reversed(ids)))
        faces.append(tuple(i + count for i in ids))
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, nxt + count, index + count))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("Edge bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        obj.select_set(False)
    return obj


def subtract_axis_hole(obj: bpy.types.Object) -> None:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=HOLE_R,
        depth=CARD_T * 3.0,
        location=(0.0, 0.0, obj.location.z),
    )
    cutter = bpy.context.object
    modifier = obj.modifiers.new("Canonical axis hole", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)
    bpy.data.objects.remove(cutter, do_unlink=True)


def material(name: str, color: tuple[float, float, float, float],
             metallic: float, roughness: float,
             bump_strength: float = 0.0) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    if bump_strength > 0:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 520.0
        noise.inputs["Detail"].default_value = 2.0
        noise.inputs["Roughness"].default_value = 0.68
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.000025
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def polygon_object(name: str, points: list[Vector], z: float,
                   mat: bpy.types.Material, depth: float = 0.000055,
                   scale: float = 1.0) -> bpy.types.Object:
    scaled = [Vector((p.x * scale, p.y * scale)) for p in points]
    obj = prism(name, scaled, depth, z + depth * 0.5, mat, bevel=0.0)
    return obj


def spade_points() -> list[Vector]:
    mm = 0.001
    values = [
        (0, -13), (-2.5, -10.2), (-5.4, -7.4), (-8.2, -4.8),
        (-10, -1.2), (-10.1, 2), (-9, 4.8), (-6.8, 6.6),
        (-4.5, 7.2), (-2.2, 6.3), (-1.6, 8.4), (-4, 11.5),
        (-4, 13), (4, 13), (4, 11.5), (1.6, 8.4), (2.2, 6.3),
        (4.5, 7.2), (6.8, 6.6), (9, 4.8), (10.1, 2),
        (10, -1.2), (8.2, -4.8), (5.4, -7.4), (2.5, -10.2),
    ]
    return [Vector((x * mm, y * mm)) for x, y in values]


def vertical_range(points: list[Vector], x: float) -> tuple[float, float] | None:
    intersections: list[float] = []
    for index, a in enumerate(points):
        b = points[(index + 1) % len(points)]
        if x < min(a.x, b.x) or x > max(a.x, b.x):
            continue
        dx = b.x - a.x
        if abs(dx) < 1e-9:
            continue
        t = (x - a.x) / dx
        if 0 <= t < 1:
            intersections.append(a.y + (b.y - a.y) * t)
    if len(intersections) < 2:
        return None
    intersections.sort()
    return intersections[0], intersections[-1]


def add_spade(root: bpy.types.Object, name: str, position: Vector, z: float,
              scale: float, etched: bpy.types.Material,
              silver: bpy.types.Material, stripes: bool) -> None:
    points = spade_points()
    obj = polygon_object(name, points, z, etched, scale=scale)
    obj.location.x = position.x
    obj.location.y = position.y
    obj.parent = root
    if not stripes:
        return
    spacing = 0.00125 * scale
    stripe_width = 0.00058 * scale
    inset = 0.00072 * scale
    minimum = min(p.x for p in points) * scale + inset
    maximum = max(p.x for p in points) * scale - inset
    x = minimum
    index = 0
    while x <= maximum:
        span = vertical_range(
            [Vector((p.x * scale, p.y * scale)) for p in points], x)
        if span and span[1] - span[0] > inset * 2:
            center_y = (span[0] + span[1]) * 0.5
            height = span[1] - span[0] - inset * 2
            bpy.ops.mesh.primitive_cube_add(
                location=(position.x + x, position.y + center_y,
                          z + 0.000075))
            stripe = bpy.context.object
            stripe.name = f"{name}_Stripe_{index:02d}"
            stripe.dimensions = (stripe_width, height, 0.000035)
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True)
            stripe.data.materials.append(silver)
            stripe.parent = root
            index += 1
        x += spacing


def add_rank(root: bpy.types.Object, body: str, name: str,
             position: Vector, z: float, rotation: float,
             etched: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(name + "_Curve", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.extrude = 0.000075
    curve.resolution_u = 8
    curve.font = bpy.data.fonts.load(str(FONT))
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(etched)
    obj.location = (position.x, position.y, z)
    obj.rotation_euler.z = rotation
    obj.parent = root
    bpy.context.view_layer.update()
    obj.scale *= 0.0064 / max(obj.dimensions.y, 1e-6)


def add_dot(root: bpy.types.Object, name: str, position: Vector,
            z: float, etched: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24,
        radius=0.00118,
        depth=0.00008,
        location=(position.x, position.y, z + 0.00004),
    )
    dot = bpy.context.object
    dot.name = name
    dot.data.materials.append(etched)
    dot.parent = root


def create_layer(index: int, rank: str, angle: float,
                 gunmetal: bpy.types.Material,
                 silver: bpy.types.Material,
                 etched: bpy.types.Material) -> bpy.types.Object:
    root = bpy.data.objects.new(
        ("BottomCard", "MiddleCard", "TopCard")[index], None)
    bpy.context.collection.objects.link(root)
    root.rotation_euler.z = math.radians(angle)
    root.location.z = index * PITCH
    outline = rounded_outline(CARD_W, CARD_H, RADIUS, CENTER)
    body = prism(root.name + "_GunmetalFrame", outline, CARD_T,
                 CARD_T * 0.5, gunmetal, bevel=0.00022)
    subtract_axis_hole(body)
    body.parent = root
    face_outline = rounded_outline(
        CARD_W - FACE_INSET * 2,
        CARD_H - FACE_INSET * 2,
        RADIUS - FACE_INSET,
        CENTER,
    )
    face = prism(root.name + "_WarmSilverFace", face_outline, 0.00006,
                 CARD_T + 0.00003, silver, bevel=0.00003)
    subtract_axis_hole(face)
    face.parent = root
    top_z = CARD_T + 0.000075
    hero = Vector((CENTER.x + 0.003, CENTER.y - 0.0035))
    add_spade(root, root.name + "_Spade", hero, top_z, 1.10,
              etched, silver, stripes=True)
    rank_offsets = [Vector((-0.0172, 0.0250)),
                    Vector((0.0172, -0.0250))]
    spade_offsets = [Vector((-0.0146, 0.0169)),
                     Vector((0.0146, -0.0169))]
    for corner, (rank_offset, spade_offset, rotation) in enumerate(zip(
            rank_offsets, spade_offsets, (0.0, math.pi))):
        add_rank(root, rank, f"{root.name}_Rank_{corner}",
                 Vector((CENTER.x + rank_offset.x,
                         CENTER.y + rank_offset.y)),
                 top_z + 0.00005, rotation, etched)
        small_position = Vector((CENTER.x + spade_offset.x,
                                 CENTER.y + spade_offset.y))
        add_spade(root, f"{root.name}_CornerSpade_{corner}",
                  small_position, top_z + 0.00003, 0.245,
                  etched, silver, stripes=False)
    for dot_index, offset in enumerate((
            Vector((-0.0160, -0.0204)),
            Vector((-0.0107, -0.0173)),
            Vector((-0.0100, -0.0231)))):
        add_dot(root, f"{root.name}_Dot_{dot_index}",
                Vector((CENTER.x + offset.x, CENTER.y + offset.y)),
                top_z, etched)
    return root


def add_bearing(chrome: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=16,
        location=(0.0, 0.0, PITCH * 2 + CARD_T + CAP_H * 0.5),
    )
    cap = bpy.context.object
    cap.name = "CommonAxis_BearingCap_Chrome"
    cap.scale = (CAP_R, CAP_R, CAP_H * 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    cap.data.materials.append(chrome)


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (
        target - obj.location).to_track_quat("-Z", "Y").to_euler()


def kelvin(kelvin: float) -> tuple[float, float, float]:
    t = kelvin / 100.0
    red = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    green = (99.4708025861 * math.log(t) - 161.1195681661
             if t <= 66 else
             288.1221695283 * ((t - 60) ** -0.0755148492))
    blue = (255 if t >= 66 else
            0 if t <= 19 else
            138.5177312231 * math.log(t - 10) - 305.0447927307)
    return tuple(max(0.0, min(1.0, value / 255.0))
                 for value in (red, green, blue))


def camera_position(target: Vector, lens: float,
                    elevation: float, half_extent: float) -> Vector:
    sensor = 0.036
    horizontal_fov = 2 * math.atan(sensor / (2 * (lens / 1000)))
    distance = half_extent / (math.tan(horizontal_fov * 0.5) * 0.62)
    azimuth = math.radians(-35.0)
    elev = math.radians(elevation)
    return target + Vector((
        math.cos(elev) * math.cos(azimuth) * distance,
        math.cos(elev) * math.sin(azimuth) * distance,
        math.sin(elev) * distance,
    ))


def set_cycles() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 768
    scene.render.resolution_y = 432
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.film_transparent = False


def render(camera: bpy.types.Object, key: bpy.types.Object,
           filename: str, lens: float, elevation: float,
           temperature: float, size: float, target: Vector,
           half_extent: float) -> None:
    camera.data.lens = lens
    camera.location = camera_position(
        target, lens, elevation, half_extent)
    aim(camera, target)
    key.data.color = kelvin(temperature)
    key.data.shape = "DISK"
    key.data.size = size
    bpy.context.scene.render.filepath = str(OUTPUT / filename)
    bpy.ops.render.render(write_still=True)


def bounds_for(objects: list[bpy.types.Object]) -> tuple[Vector, float]:
    points: list[Vector] = []
    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    center = (minimum + maximum) * 0.5
    half_extent = max(maximum.x - minimum.x,
                      maximum.y - minimum.y) * 0.55
    return center, half_extent


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    clean()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    gunmetal = material(
        "MAT_Gunmetal", (0.045, 0.052, 0.060, 1.0), 0.9, 0.38, 0.06)
    silver = material(
        "MAT_WarmSilver", (0.26, 0.23, 0.19, 1.0), 1.0, 0.43, 0.045)
    etched = material(
        "MAT_Etching", (0.012, 0.014, 0.016, 1.0), 0.75, 0.58)
    chrome = material(
        "MAT_Chrome", (0.72, 0.76, 0.82, 1.0), 1.0, 0.10)
    support_mat = material(
        "MAT_NeutralSupport", (0.010, 0.012, 0.015, 1.0), 0.0, 0.82, 0.04)
    assembly = bpy.data.objects.new("MagneticFanCard_Root", None)
    bpy.context.collection.objects.link(assembly)
    for index, (rank, angle) in enumerate((("Q", 0), ("K", 45), ("A", 90))):
        layer = create_layer(index, rank, angle, gunmetal, silver, etched)
        layer.parent = assembly
    assembly.rotation_euler.z = math.radians(90.0)
    add_bearing(chrome)
    bpy.context.view_layer.update()
    product_meshes = [obj for obj in bpy.context.scene.objects
                      if obj.type == "MESH"]
    target, half_extent = bounds_for(product_meshes)
    bpy.ops.mesh.primitive_cube_add(
        location=(target.x, target.y, -0.005))
    support = bpy.context.object
    support.name = "Support_Neutral"
    support.dimensions = (0.22, 0.16, 0.010)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    support.data.materials.append(support_mat)
    bevel = support.modifiers.new("Support bevel", "BEVEL")
    bevel.width = 0.008
    bevel.segments = 6
    bpy.context.view_layer.objects.active = support
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    target.z = 0.008
    camera_data = bpy.data.cameras.new("CAM_ContractSweep")
    camera_data.sensor_width = 36.0
    camera = bpy.data.objects.new("CAM_ContractSweep", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    key_data = bpy.data.lights.new("LGT_Key_Sweep", "AREA")
    key_data.energy = 3.0
    key = bpy.data.objects.new("LGT_Key_Sweep", key_data)
    bpy.context.collection.objects.link(key)
    key.location = target + Vector((0.16, -0.14, 0.24))
    aim(key, target)
    fill_data = bpy.data.lights.new("LGT_Fill_Sweep", "AREA")
    fill_data.energy = 0.6
    fill_data.shape = "DISK"
    fill_data.size = 0.50
    fill_data.color = kelvin(6500)
    fill = bpy.data.objects.new("LGT_Fill_Sweep", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = target + Vector((-0.18, -0.05, 0.12))
    aim(fill, target)
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.010, 0.012, 0.015, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.012
    set_cycles()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    baseline = dict(lens=80.0, elevation=32.0,
                    temperature=5000.0, size=0.35)
    render(camera, key, "baseline-l80-e32-k5000-s350.png",
           target=target, half_extent=half_extent, **baseline)
    for lens in (50.0, 110.0):
        render(camera, key, f"lens-{int(lens)}.png",
               lens, baseline["elevation"], baseline["temperature"],
               baseline["size"], target, half_extent)
    for elevation in (20.0, 45.0):
        render(camera, key, f"elevation-{int(elevation)}.png",
               baseline["lens"], elevation, baseline["temperature"],
               baseline["size"], target, half_extent)
    for temperature in (3500.0, 6500.0):
        render(camera, key, f"temperature-{int(temperature)}.png",
               baseline["lens"], baseline["elevation"], temperature,
               baseline["size"], target, half_extent)
    for size in (0.15, 0.70):
        render(camera, key, f"source-size-{int(size * 1000)}.png",
               baseline["lens"], baseline["elevation"],
               baseline["temperature"], size, target, half_extent)
    report = {
        "baseline": baseline,
        "lens": [50, 80, 110],
        "elevation": [20, 32, 45],
        "temperature_kelvin": [3500, 5000, 6500],
        "source_size_mm": [150, 350, 700],
        "product_source": "canonical fan-card guardrails",
        "shipping_asset_modified": False,
    }
    (OUTPUT / "parameter-sweep.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
