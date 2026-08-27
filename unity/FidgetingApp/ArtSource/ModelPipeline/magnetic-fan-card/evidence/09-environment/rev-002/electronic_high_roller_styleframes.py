"""Build and render three Electronic High-Roller environment styleframes."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
SOURCE_BLEND = (
    SCRIPT.parents[2] / "08-lighting/rev-002/"
    "fan-card-exact-lighting.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-electronic-high-roller-styleframes.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep_high_roller", PARAMETER_SCRIPT)


def collection(name: str) -> bpy.types.Collection:
    value = bpy.data.collections.get(name)
    if value is None:
        value = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(value)
    return value


def move_to(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    if target not in obj.users_collection:
        target.objects.link(obj)
    for current in list(obj.users_collection):
        if current != target:
            current.objects.unlink(obj)


def principled(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    return material


def felt_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_ENV_OxbloodElectronicFelt")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = (
        0.020, 0.0001, 0.00015, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.79
    if "Sheen Weight" in shader.inputs:
        shader.inputs["Sheen Weight"].default_value = 0.32
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 520.0
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.72
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.00016
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def emission(
    name: str,
    color: tuple[float, float, float, float],
    strength: float,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeEmission")
    shader.inputs["Color"].default_value = color
    shader.inputs["Strength"].default_value = strength
    links.new(shader.outputs["Emission"], output.inputs["Surface"])
    return material


def volume_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_FX_LocalGoldAtmosphere")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    volume = nodes.new("ShaderNodeVolumePrincipled")
    volume.inputs["Color"].default_value = (0.36, 0.12, 0.015, 1.0)
    volume.inputs["Density"].default_value = 0.002
    volume.inputs["Anisotropy"].default_value = 0.58
    links.new(volume.outputs["Volume"], output.inputs["Volume"])
    return material


def rounded_slab(
    name: str,
    center: Vector,
    width: float,
    height: float,
    radius: float,
    thickness: float,
    z_top: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    outline = source.rounded_outline(width, height, radius, center)
    obj = source.prism(
        name,
        outline,
        thickness,
        z_top - thickness * 0.5,
        material,
        bevel=min(radius * 0.16, 0.004),
    )
    move_to(obj, target)
    return obj


def polyline(
    name: str,
    points: list[tuple[float, float, float]],
    width: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    data = bpy.data.curves.new(name + "_Curve", "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = width
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, value in zip(spline.points, points):
        point.co = (*value, 1.0)
    obj = bpy.data.objects.new(name, data)
    target.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def rounded_stroke(
    name: str,
    center: Vector,
    width: float,
    height: float,
    radius: float,
    z: float,
    stroke_width: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    outline = source.rounded_outline(
        width, height, radius, center, segments=20)
    points = [(point.x, point.y, z) for point in outline]
    points.append(points[0])
    return polyline(name, points, stroke_width, material, target)


def add_cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    move_to(obj, target)
    return obj


def add_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    segments: int = 16,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    move_to(obj, target)
    return obj


def create_chip(
    name: str,
    location: Vector,
    radius: float,
    rotation: tuple[float, float, float],
    body_material: bpy.types.Material,
    brass_material: bpy.types.Material,
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    root = bpy.data.objects.new(name, None)
    target.objects.link(root)
    root.location = location
    root.rotation_euler = rotation
    objects = [root]

    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=radius, depth=0.004)
    body = bpy.context.object
    body.name = name + "_Body"
    body.parent = root
    body.location = (0.0, 0.0, 0.0)
    body.data.materials.append(body_material)
    move_to(body, target)
    objects.append(body)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius * 0.76,
        minor_radius=radius * 0.072,
        major_segments=64,
        minor_segments=12,
    )
    ring = bpy.context.object
    ring.name = name + "_BrassRing"
    ring.parent = root
    ring.location = (0.0, 0.0, 0.00225)
    ring.data.materials.append(brass_material)
    move_to(ring, target)
    objects.append(ring)

    for index in range(12):
        angle = math.tau * index / 12
        segment = add_cube(
            f"{name}_Inset_{index:02d}",
            (0.0, 0.0, 0.0),
            (radius * 0.19, radius * 0.075, 0.0012),
            brass_material,
            target,
        )
        segment.parent = root
        segment.location = (
            math.cos(angle) * radius * 0.79,
            math.sin(angle) * radius * 0.79,
            0.00245,
        )
        segment.rotation_euler.z = angle
        objects.append(segment)
    return objects


def create_dark_card(
    name: str,
    location: Vector,
    rotation: tuple[float, float, float],
    face_material: bpy.types.Material,
    brass_material: bpy.types.Material,
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    root = bpy.data.objects.new(name, None)
    target.objects.link(root)
    root.location = location
    root.rotation_euler = rotation
    outline = source.rounded_outline(
        0.055, 0.078, 0.0052, Vector((0.0, 0.0, 0.0)))
    card = source.prism(
        name + "_Face", outline, 0.0011, 0.0,
        face_material, bevel=0.0006)
    card.parent = root
    move_to(card, target)
    border = rounded_stroke(
        name + "_Border", Vector((0.0, 0.0, 0.0)),
        0.050, 0.073, 0.0045, 0.0007, 0.00045,
        brass_material, target)
    border.parent = root
    diamond_vertices = [
        (-0.0045, 0.0, 0.00075),
        (0.0, 0.008, 0.00075),
        (0.0045, 0.0, 0.00075),
        (0.0, -0.008, 0.00075),
    ]
    mesh = bpy.data.meshes.new(name + "_DiamondMesh")
    mesh.from_pydata(diamond_vertices, [], [(0, 1, 2, 3)])
    diamond = bpy.data.objects.new(name + "_Diamond", mesh)
    target.objects.link(diamond)
    diamond.parent = root
    diamond.data.materials.append(brass_material)
    return [root, card, border, diamond]


def add_light(
    name: str,
    kind: str,
    location: Vector,
    energy: float,
    color: tuple[float, float, float],
    target_point: Vector,
    target: bpy.types.Collection,
    size: float = 0.10,
) -> bpy.types.Object:
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    data.color = color
    if kind == "AREA":
        data.shape = "DISK"
        data.size = size
    if kind == "SPOT":
        data.spot_size = math.radians(31.0)
        data.spot_blend = 0.52
    obj = bpy.data.objects.new(name, data)
    target.objects.link(obj)
    obj.location = location
    source.aim(obj, target_point)
    return obj


def set_group_visibility(
    groups: dict[str, list[bpy.types.Object]],
    visible: set[str],
) -> None:
    for group_name, objects in groups.items():
        show = group_name in visible
        for obj in objects:
            obj.hide_render = not show
            obj.hide_viewport = not show


def configure_cycles(scene: bpy.types.Scene) -> dict:
    report = {"backend": "Cycles", "device": "CPU fallback"}
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.03
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "METAL"
        preferences.get_devices()
        enabled = []
        for device in preferences.devices:
            device.use = device.type != "CPU"
            if device.use:
                enabled.append(device.name)
        if enabled:
            scene.cycles.device = "GPU"
            report["device"] = ", ".join(enabled)
    except Exception as error:
        report["deviceError"] = str(error)
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    return report


def configure_compositor(scene: bpy.types.Scene) -> None:
    tree = bpy.data.node_groups.new(
        "High Roller Compositor", "CompositorNodeTree")
    scene.compositing_node_group = tree
    tree.interface.new_socket(
        name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    nodes = tree.nodes
    links = tree.links
    render_layers = nodes.new("CompositorNodeRLayers")
    glare = nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Quality"].default_value = "High"
    glare.inputs["Threshold"].default_value = 1.35
    glare.inputs["Size"].default_value = 0.72
    glare.inputs["Strength"].default_value = 0.22
    composite = nodes.new("NodeGroupOutput")
    links.new(render_layers.outputs["Image"], glare.inputs["Image"])
    links.new(glare.outputs["Image"], composite.inputs["Image"])


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene

    collections = {
        "product": collection("COL_Product_Locked"),
        "layout": collection("COL_Layout"),
        "geo": collection("COL_Modular_Geo"),
        "dress": collection("COL_SetDressing"),
        "lights": collection("COL_Lights"),
        "cameras": collection("COL_Cameras"),
        "fx": collection("COL_FX"),
    }
    previous_support = bpy.data.objects.get("GEO_Support_Base")
    if previous_support is not None:
        bpy.data.objects.remove(previous_support, do_unlink=True)
    for obj in list(scene.objects):
        if obj.type == "CAMERA":
            move_to(obj, collections["cameras"])
        elif obj.type == "LIGHT":
            move_to(obj, collections["lights"])
        elif not obj.name.startswith(("ENV_", "FX_", "PROP_")):
            move_to(obj, collections["product"])

    product_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
        and obj.users_collection
        and obj.users_collection[0] == collections["product"]
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    stage_center = Vector((center.x - 0.055, center.y + 0.018, 0.0))

    neutral_material = principled(
        "MAT_ENV_Neutral", (0.07, 0.075, 0.084, 1.0), 0.0, 0.76)
    felt = felt_material()
    dark_lacquer = principled(
        "MAT_ENV_BlackLacquer", (0.006, 0.004, 0.004, 1.0), 0.42, 0.24)
    wall_material = principled(
        "MAT_ENV_CasinoWall", (0.010, 0.006, 0.004, 1.0), 0.28, 0.31)
    brass = principled(
        "MAT_ENV_Brass", (0.48, 0.17, 0.025, 1.0), 1.0, 0.23)
    oxblood_chip = principled(
        "MAT_PROP_OxbloodChip", (0.19, 0.006, 0.010, 1.0), 0.22, 0.20)
    black_card = principled(
        "MAT_PROP_BlackCard", (0.006, 0.004, 0.004, 1.0), 0.25, 0.34)
    gold_glow = emission(
        "MAT_FX_GoldGlow", (1.0, 0.24, 0.028, 1.0), 2.0)
    gold_hot = emission(
        "MAT_FX_GoldHot", (1.0, 0.42, 0.075, 1.0), 6.0)

    groups: dict[str, list[bpy.types.Object]] = {
        "neutral": [],
        "base": [],
        "low": [],
        "medium": [],
        "high": [],
    }

    groups["neutral"].append(rounded_slab(
        "ENV_NeutralSurface", stage_center,
        0.72, 0.54, 0.05, 0.04, -0.00005,
        neutral_material, collections["layout"]))

    background_floor = rounded_slab(
        "ENV_Background_BlackLacquer", stage_center,
        0.78, 0.54, 0.045, 0.040, -0.036,
        dark_lacquer, collections["layout"])
    table_base = rounded_slab(
        "ENV_Table_BlackLacquer", stage_center,
        0.52, 0.32, 0.060, 0.032, -0.0038,
        dark_lacquer, collections["layout"])
    felt_top = rounded_slab(
        "ENV_Table_OxbloodFelt", stage_center,
        0.49, 0.29, 0.052, 0.006, -0.00005,
        felt, collections["layout"])
    outer_rail = rounded_stroke(
        "ENV_Table_BrassRail", stage_center,
        0.486, 0.286, 0.051, 0.0011, 0.0021,
        brass, collections["layout"])
    inner_rail = rounded_stroke(
        "ENV_Table_LightRail", stage_center,
        0.448, 0.248, 0.040, 0.0009, 0.00065,
        gold_glow, collections["layout"])
    groups["base"] += [
        background_floor, table_base, felt_top, outer_rail, inner_rail]

    wall_y = center.y + 0.085
    wall = add_cube(
        "ENV_Casino_BackWall",
        (stage_center.x, wall_y, 0.105),
        (0.68, 0.020, 0.24),
        wall_material,
        collections["geo"],
    )
    groups["base"].append(wall)
    for index, x in enumerate((-0.25, -0.08, 0.10, 0.27)):
        column = add_cube(
            f"ENV_Casino_BrassColumn_{index:02d}",
            (stage_center.x + x, wall_y - 0.012, 0.105),
            (0.008, 0.005, 0.24),
            brass,
            collections["geo"],
        )
        groups["base"].append(column)
    for index, z in enumerate((0.035, 0.080, 0.126, 0.172)):
        strip = add_cube(
            f"ENV_Casino_LightBand_{index:02d}",
            (stage_center.x, wall_y - 0.015, z),
            (0.65, 0.004, 0.005),
            gold_glow,
            collections["geo"],
        )
        groups["base"].append(strip)

    trace_sets = [
        [
            (-0.31, -0.11, 0.00085),
            (-0.23, -0.11, 0.00085),
            (-0.23, -0.055, 0.00085),
            (-0.13, -0.055, 0.00085),
            (-0.13, 0.005, 0.00085),
            (-0.035, 0.005, 0.00085),
        ],
        [
            (-0.30, 0.015, 0.00085),
            (-0.21, 0.015, 0.00085),
            (-0.21, 0.075, 0.00085),
            (-0.10, 0.075, 0.00085),
            (-0.10, 0.035, 0.00085),
            (-0.01, 0.035, 0.00085),
        ],
        [
            (-0.26, 0.13, 0.00085),
            (-0.16, 0.13, 0.00085),
            (-0.16, 0.105, 0.00085),
            (-0.055, 0.105, 0.00085),
        ],
    ]
    for index, local_points in enumerate(trace_sets):
        points = [
            (stage_center.x + x, stage_center.y + y, z)
            for x, y, z in local_points
        ]
        trace = polyline(
            f"FX_Table_Circuit_{index:02d}", points,
            0.00035 if index < 2 else 0.00026,
            gold_glow if index < 2 else gold_hot,
            collections["fx"],
        )
        groups["medium" if index < 2 else "high"].append(trace)
        for node_index, point in enumerate(points[1:-1:2]):
            node = add_uv_sphere(
                f"FX_Table_CircuitNode_{index:02d}_{node_index:02d}",
                point, 0.0018, gold_hot, collections["fx"], 12)
            groups["medium" if index < 2 else "high"].append(node)

    rng = random.Random(20260825)
    for index in range(38):
        x = stage_center.x + rng.uniform(-0.27, 0.26)
        y = stage_center.y + rng.uniform(0.070, 0.145)
        z = rng.uniform(0.040, 0.19)
        radius = rng.uniform(0.0015, 0.0048)
        sphere = add_uv_sphere(
            f"ENV_Bokeh_{index:02d}", (x, y, z), radius,
            gold_glow if index % 4 else gold_hot,
            collections["dress"], 12)
        groups["base"].append(sphere)
    for index, (x, y, z, length, angle) in enumerate((
            (-0.20, 0.070, 0.055, 0.15, 16),
            (-0.09, 0.092, 0.092, 0.12, -12),
            (0.08, 0.082, 0.128, 0.17, 10))):
        bar = add_cube(
            f"ENV_Casino_FloatingLightBar_{index:02d}",
            (stage_center.x + x, stage_center.y + y, z),
            (length, 0.004, 0.005),
            gold_glow,
            collections["dress"],
            rotation=(0.0, 0.0, math.radians(angle)),
        )
        groups["base"].append(bar)

    chip_low = create_chip(
        "PROP_Chip_Foreground_Right",
        Vector((center.x + 0.155, center.y - 0.072, 0.042)),
        0.052,
        (math.radians(19), math.radians(-24), math.radians(28)),
        oxblood_chip, brass, collections["dress"])
    groups["low"] += chip_low
    chip_medium = create_chip(
        "PROP_Chip_Foreground_Left",
        Vector((center.x - 0.165, center.y - 0.075, 0.036)),
        0.044,
        (math.radians(24), math.radians(18), math.radians(-33)),
        oxblood_chip, brass, collections["dress"])
    groups["medium"] += chip_medium
    chip_high = create_chip(
        "PROP_Chip_Background_Right",
        Vector((center.x + 0.145, center.y + 0.075, 0.095)),
        0.034,
        (math.radians(-10), math.radians(-33), math.radians(22)),
        dark_lacquer, brass, collections["dress"])
    groups["high"] += chip_high

    card_low = create_dark_card(
        "PROP_Card_Background_Left",
        Vector((center.x - 0.105, center.y + 0.045, 0.078)),
        (math.radians(14), math.radians(25), math.radians(-28)),
        black_card, brass, collections["dress"])
    groups["low"] += card_low
    card_medium = create_dark_card(
        "PROP_Card_Background_Right",
        Vector((center.x - 0.035, center.y - 0.010, 0.100)),
        (math.radians(-12), math.radians(-20), math.radians(32)),
        black_card, brass, collections["dress"])
    groups["medium"] += card_medium
    card_high = create_dark_card(
        "PROP_Card_Mid_Left",
        Vector((center.x + 0.095, center.y + 0.040, 0.120)),
        (math.radians(18), math.radians(10), math.radians(-12)),
        black_card, brass, collections["dress"])
    groups["high"] += card_high

    particle_mesh = None
    for index in range(92):
        t = index / 91
        x = stage_center.x - 0.22 + t * 0.44 + rng.uniform(-0.026, 0.026)
        y = stage_center.y - 0.075 + t * 0.20 + rng.uniform(-0.020, 0.020)
        z = 0.018 + t * 0.14 + rng.uniform(-0.014, 0.014)
        radius = rng.uniform(0.0012, 0.0030)
        if particle_mesh is None:
            prototype = add_uv_sphere(
                "FX_GoldDust_Prototype", (x, y, z), radius,
                gold_hot, collections["fx"], 8)
            particle_mesh = prototype.data
            obj = prototype
        else:
            obj = bpy.data.objects.new(
                f"FX_GoldDust_{index:03d}", particle_mesh)
            collections["fx"].objects.link(obj)
            obj.location = (x, y, z)
            obj.scale = (radius / 0.001, ) * 3
        level = "low" if index < 22 else "medium" if index < 58 else "high"
        groups[level].append(obj)
    hero_sparks = (
        (-0.15, -0.035, 0.035, "low"),
        (-0.11, 0.015, 0.055, "low"),
        (-0.06, 0.070, 0.085, "low"),
        (-0.02, -0.060, 0.045, "medium"),
        (0.04, 0.075, 0.105, "medium"),
        (0.11, 0.015, 0.070, "medium"),
        (0.17, 0.095, 0.135, "high"),
        (-0.20, 0.090, 0.115, "high"),
    )
    for index, (x, y, z, level) in enumerate(hero_sparks):
        spark = add_uv_sphere(
            f"FX_HeroSpark_{index:02d}",
            (center.x + x, center.y + y, z),
            0.0013 if level != "high" else 0.0018,
            gold_hot, collections["fx"], 12)
        groups[level].append(spark)
    for index in range(26):
        t = index / 25
        x = center.x - 0.17 + t * 0.30
        y = center.y - 0.045 + t * 0.105
        z = 0.026 + math.sin(t * math.pi) * 0.075
        if -0.01 < x - center.x < 0.11 and y - center.y < 0.035:
            continue
        spark = add_uv_sphere(
            f"FX_DiagonalSpark_{index:02d}",
            (x, y, z),
            0.0009 + (index % 4) * 0.00016,
            gold_hot, collections["fx"], 10)
        groups["medium" if index < 17 else "high"].append(spark)

    for index in range(18):
        x = stage_center.x + rng.uniform(-0.30, 0.30)
        y = stage_center.y + rng.uniform(-0.13, 0.20)
        z = rng.uniform(0.018, 0.18)
        size = rng.uniform(0.0018, 0.0052)
        vertices = [
            (x - size, y, z),
            (x, y + size * 1.7, z),
            (x + size, y, z),
            (x, y - size * 1.7, z),
        ]
        mesh = bpy.data.meshes.new(f"FX_SuitShard_{index:02d}_Mesh")
        mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
        shard = bpy.data.objects.new(f"FX_SuitShard_{index:02d}", mesh)
        collections["fx"].objects.link(shard)
        shard.data.materials.append(gold_glow)
        shard.rotation_euler = (
            rng.uniform(-0.5, 0.5),
            rng.uniform(-0.5, 0.5),
            rng.uniform(-math.pi, math.pi),
        )
        groups["medium" if index < 10 else "high"].append(shard)

    bpy.ops.mesh.primitive_cube_add(
        location=(stage_center.x + 0.03, stage_center.y + 0.105, 0.115))
    volume = bpy.context.object
    volume.name = "FX_LocalGoldAtmosphere"
    volume.dimensions = (0.42, 0.26, 0.25)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    volume.data.materials.append(volume_material())
    move_to(volume, collections["fx"])
    groups["high"].append(volume)

    camera = bpy.data.objects["CAM_Hero_Selected"]
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center)
    focus = bpy.data.objects.new("EMPTY_CamTarget_HighRoller", None)
    collections["cameras"].objects.link(focus)
    focus.location = center
    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = focus
    camera.data.dof.aperture_fstop = 4.5
    camera.data.dof.aperture_blades = 8
    scene.camera = camera

    key = bpy.data.objects["LGT_Key_Broad"]
    key.data.energy = 4.0
    key.data.size = 0.35
    key.data.color = source.kelvin(5000)
    fill = bpy.data.objects["LGT_Fill_Weak"]
    fill.data.energy = 0.72
    fill.data.size = 0.50
    rim = add_light(
        "LGT_Rim_Gold", "SPOT",
        center + Vector((-0.16, 0.19, 0.20)),
        0.85, source.kelvin(2850), center,
        collections["lights"])
    table_glow = add_light(
        "LGT_Table_Amber", "AREA",
        center + Vector((-0.08, 0.03, 0.12)),
        0.20, source.kelvin(3200), center,
        collections["lights"], 0.16)
    groups["base"] += [rim, table_glow]

    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.0015, 0.001, 0.0008, 1.0)
    background.inputs["Strength"].default_value = 0.006
    renderer = configure_cycles(scene)
    configure_compositor(scene)

    outputs = {}
    set_group_visibility(groups, {"neutral"})
    rim.hide_render = True
    table_glow.hide_render = True
    camera.data.dof.aperture_fstop = 7.1
    scene.render.filepath = str(OUTPUT / "high-roller-neutral.png")
    bpy.ops.render.render(write_still=True)
    outputs["neutral"] = "high-roller-neutral.png"

    variants = {
        "C1-grounded-luxury": {"base", "low"},
        "C2-electronic-stage": {"base", "low", "medium"},
        "C3-high-energy": {"base", "low", "medium", "high"},
    }
    for index, (variant, visible) in enumerate(variants.items(), start=1):
        set_group_visibility(groups, visible)
        rim.hide_render = False
        table_glow.hide_render = False
        camera.data.dof.aperture_fstop = 4.5
        rim.data.energy = (0.55, 0.85, 1.15)[index - 1]
        table_glow.data.energy = (0.12, 0.20, 0.28)[index - 1]
        path = OUTPUT / f"{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name

    set_group_visibility(groups, {"base", "low", "medium"})
    rim.hide_render = False
    table_glow.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    (OUTPUT / "electronic-high-roller-report.json").write_text(
        json.dumps({
            "route": "C-electronic-high-roller",
            "productGeometryModified": False,
            "lockedCamera": {"lensMm": 80, "elevationDegrees": 32},
            "sceneHierarchy": [
                "COL_Product_Locked",
                "COL_Layout",
                "COL_Modular_Geo",
                "COL_SetDressing",
                "COL_Lights",
                "COL_Cameras",
                "COL_FX",
            ],
            "renderer": renderer,
            "samples": 64,
            "outputs": outputs,
            "variants": {
                "C1-grounded-luxury": "lowest prop and particle density",
                "C2-electronic-stage": "balanced recommended density",
                "C3-high-energy": "maximum controlled cards, chips, and particles",
            },
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
