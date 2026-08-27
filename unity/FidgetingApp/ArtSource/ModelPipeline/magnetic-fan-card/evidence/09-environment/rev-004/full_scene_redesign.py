"""Render three rebuilt luxury Banner stages from the locked product scene."""

from __future__ import annotations

import importlib.util
import json
import math
import random
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


HERE = Path(__file__).resolve().parent
REV2 = HERE.parent / "rev-002"
SOURCE_BLEND = (
    HERE.parents[1] / "08-lighting/rev-002/"
    "fan-card-exact-lighting.blend"
)
HELPER_SCRIPT = REV2 / "electronic_high_roller_styleframes.py"
PARAMETER_SCRIPT = (
    HERE.parents[1] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT_BLEND = HERE / "fan-card-full-scene-redesign.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


helper = load_module("fan_card_full_scene_helper", HELPER_SCRIPT)
source = load_module("fan_card_full_scene_parameter_source", PARAMETER_SCRIPT)


def camera_ray_point(
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    u: float,
    v: float,
    distance: float,
) -> Vector:
    frame = camera.data.view_frame(scene=scene)
    min_x = min(point.x for point in frame)
    max_x = max(point.x for point in frame)
    min_y = min(point.y for point in frame)
    max_y = max(point.y for point in frame)
    z = sum(point.z for point in frame) / len(frame)
    local = Vector((
        min_x + (max_x - min_x) * u,
        min_y + (max_y - min_y) * v,
        z,
    )).normalized()
    return camera.location + (
        camera.matrix_world.to_quaternion() @ local) * distance


def felt_material() -> bpy.types.Material:
    material = bpy.data.materials.new("MAT_STAGE_DeepOxbloodVelvet")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = (
        0.020, 0.00012, 0.00018, 1.0)
    shader.inputs["Roughness"].default_value = 0.86
    if "Sheen Weight" in shader.inputs:
        shader.inputs["Sheen Weight"].default_value = 0.42
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 620.0
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.20
    bump.inputs["Distance"].default_value = 0.00014
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def configure_compositor(scene: bpy.types.Scene) -> None:
    tree = bpy.data.node_groups.new(
        "Full Scene Redesign Compositor", "CompositorNodeTree")
    scene.compositing_node_group = tree
    tree.interface.new_socket(
        name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    render_layers = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Quality"].default_value = "High"
    glare.inputs["Threshold"].default_value = 1.20
    glare.inputs["Size"].default_value = 0.76
    glare.inputs["Strength"].default_value = 0.28
    output = tree.nodes.new("NodeGroupOutput")
    tree.links.new(render_layers.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], output.inputs["Image"])


def add_backdrop_cube(
    name: str,
    root: bpy.types.Object,
    local_location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    obj = helper.add_cube(
        name, (0.0, 0.0, 0.0), dimensions, material, target)
    obj.parent = root
    obj.location = local_location
    return obj


def orient_root_to_camera(
    root: bpy.types.Object,
    camera: bpy.types.Object,
    angle: float,
    tilt_x: float = 0.0,
    tilt_y: float = 0.0,
) -> None:
    root.rotation_euler = camera.rotation_euler.copy()
    root.rotation_euler.rotate_axis("Z", math.radians(angle))
    root.rotation_euler.rotate_axis("X", math.radians(tilt_x))
    root.rotation_euler.rotate_axis("Y", math.radians(tilt_y))


def card_at(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    uv_depth: tuple[float, float, float],
    angle: float,
    scale: float,
    materials: tuple[bpy.types.Material, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    objects = helper.create_dark_card(
        name, Vector((0.0, 0.0, 0.0)), (0.0, 0.0, 0.0),
        materials[0], materials[1], target)
    root = objects[0]
    root.location = camera_ray_point(camera, scene, *uv_depth)
    orient_root_to_camera(root, camera, angle, 8.0, -5.0)
    root.scale = (scale, scale, scale)
    return objects


def chip_at(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    uv_depth: tuple[float, float, float],
    angle: float,
    scale: float,
    materials: tuple[bpy.types.Material, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    objects = helper.create_chip(
        name, Vector((0.0, 0.0, 0.0)), 0.048,
        (0.0, 0.0, 0.0), materials[0], materials[1], target)
    root = objects[0]
    root.location = camera_ray_point(camera, scene, *uv_depth)
    orient_root_to_camera(root, camera, angle, 6.0, -8.0)
    root.scale = (scale, scale, scale)
    return objects


def particle_at(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    uv_depth: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    return helper.add_uv_sphere(
        name,
        camera_ray_point(camera, scene, *uv_depth),
        radius,
        material,
        target,
        8,
    )


def add_diamond_at(
    name: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    uv_depth: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    angle: float,
) -> bpy.types.Object:
    center = camera_ray_point(camera, scene, *uv_depth)
    right = camera.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    up = camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
    vertices = [
        center - right * size,
        center + up * size * 1.6,
        center + right * size,
        center - up * size * 1.6,
    ]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def create_route_particles(
    route: str,
    camera: bpy.types.Object,
    scene: bpy.types.Scene,
    count: int,
    seed: int,
    gold: bpy.types.Material,
    hot: bpy.types.Material,
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    rng = random.Random(seed)
    objects = []
    for index in range(count):
        if route == "A":
            u = rng.uniform(0.06, 0.96)
            v = rng.uniform(0.46, 0.95)
            distance = rng.uniform(0.56, 0.73)
        elif route == "B":
            u = rng.uniform(0.05, 0.95)
            v = rng.uniform(0.25, 0.97)
            distance = rng.uniform(0.47, 0.70)
        else:
            theta = rng.uniform(-0.25, math.tau * 0.88)
            radial = rng.uniform(0.20, 0.48)
            u = 0.64 + math.cos(theta) * radial
            v = 0.53 + math.sin(theta) * radial * 0.70
            distance = rng.uniform(0.43, 0.70)
        u = max(-0.08, min(1.08, u))
        v = max(0.03, min(0.98, v))
        if 0.42 < u < 0.95 and 0.18 < v < 0.72:
            continue
        radius = rng.uniform(0.0007, 0.0025)
        if distance > 0.62:
            radius *= rng.uniform(1.4, 2.7)
        obj = particle_at(
            f"FX_{route}_Particle_{index:03d}",
            camera, scene, (u, v, distance), radius,
            hot if index % 7 == 0 else gold, target)
        objects.append(obj)
        if index % 8 == 0:
            objects.append(add_diamond_at(
                f"FX_{route}_Diamond_{index:03d}",
                camera, scene, (u, v, distance - 0.005),
                radius * 1.7, gold, target, rng.uniform(-45, 45)))
    return objects


def set_visible(
    groups: dict[str, list[bpy.types.Object]],
    visible: set[str],
) -> None:
    for name, objects in groups.items():
        show = name in visible
        for obj in objects:
            obj.hide_render = not show
            obj.hide_viewport = not show


def object_world_center(obj: bpy.types.Object) -> Vector:
    if obj.type == "MESH" and obj.bound_box:
        points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        return sum(points, Vector()) / len(points)
    return obj.matrix_world.translation


def cull_product_overlap_fx(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    objects: list[bpy.types.Object],
) -> int:
    count = 0
    for obj in objects:
        if not obj.name.startswith("FX_"):
            continue
        projected = world_to_camera_view(
            scene, camera, object_world_center(obj))
        if 0.27 < projected.x < 0.92 and 0.12 < projected.y < 0.76:
            obj.hide_render = True
            count += 1
    return count


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    collections = {
        "product": helper.collection("COL_Product_Locked"),
        "layout": helper.collection("COL_Layout"),
        "geo": helper.collection("COL_Modular_Geo"),
        "dress": helper.collection("COL_SetDressing"),
        "lights": helper.collection("COL_Lights"),
        "cameras": helper.collection("COL_Cameras"),
        "fx": helper.collection("COL_FX"),
    }
    support = bpy.data.objects.get("GEO_Support_Base")
    if support is not None:
        bpy.data.objects.remove(support, do_unlink=True)
    for obj in list(scene.objects):
        if obj.type == "CAMERA":
            helper.move_to(obj, collections["cameras"])
        elif obj.type == "LIGHT":
            helper.move_to(obj, collections["lights"])
        elif not obj.name.startswith(("ENV_", "FX_", "PROP_")):
            helper.move_to(obj, collections["product"])

    product_objects = [
        obj for obj in collections["product"].objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    camera = bpy.data.objects["CAM_Hero_Selected"]
    base_position = source.camera_position(
        center, 80.0, 32.0, half_extent)
    camera.location = center + (base_position - center) * 0.91
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.19
    source.aim(camera, center + Vector((0.0, 0.008, 0.013)))
    focus = bpy.data.objects.new("EMPTY_CamTarget_FullScene", None)
    collections["cameras"].objects.link(focus)
    focus.location = center + Vector((0.0, 0.0, 0.006))
    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = focus
    camera.data.dof.aperture_fstop = 3.8
    camera.data.dof.aperture_blades = 8
    scene.camera = camera

    felt = felt_material()
    black = helper.principled(
        "MAT_STAGE_BlackLacquer", (0.003, 0.0015, 0.001, 1.0), 0.48, 0.20)
    backdrop_black = helper.principled(
        "MAT_STAGE_BackdropBlack", (0.0015, 0.0008, 0.0006, 1.0), 0.15, 0.32)
    brass = helper.principled(
        "MAT_STAGE_RichBrass", (0.58, 0.18, 0.018, 1.0), 1.0, 0.19)
    oxblood = helper.principled(
        "MAT_STAGE_OxbloodChip", (0.24, 0.002, 0.004, 1.0), 0.30, 0.18)
    card_black = helper.principled(
        "MAT_STAGE_BlackCard", (0.0025, 0.0012, 0.0010, 1.0), 0.18, 0.30)
    gold = helper.emission(
        "MAT_STAGE_GoldGlow", (1.0, 0.30, 0.025, 1.0), 5.5)
    gold_hot = helper.emission(
        "MAT_STAGE_GoldHot", (1.0, 0.58, 0.12, 1.0), 13.0)

    groups: dict[str, list[bpy.types.Object]] = {
        "base": [],
        "A": [],
        "B": [],
        "C": [],
    }
    stage_center = Vector((center.x - 0.035, center.y + 0.008, 0.0))
    base = helper.rounded_slab(
        "ENV_STAGE_TableBase", stage_center,
        0.54, 0.33, 0.062, 0.034, -0.004,
        black, collections["layout"])
    top = helper.rounded_slab(
        "ENV_STAGE_VelvetTop", stage_center,
        0.51, 0.30, 0.053, 0.006, -0.00005,
        felt, collections["layout"])
    rail = helper.rounded_stroke(
        "ENV_STAGE_BrassRail", stage_center,
        0.507, 0.297, 0.052, 0.0012, 0.0024,
        brass, collections["layout"])
    light_rail = helper.rounded_stroke(
        "ENV_STAGE_LightRail", stage_center,
        0.472, 0.262, 0.041, 0.0010, 0.00075,
        gold, collections["layout"])
    groups["base"] += [base, top, rail, light_rail]

    backdrop_root = bpy.data.objects.new("ENV_STAGE_BackdropRoot", None)
    collections["geo"].objects.link(backdrop_root)
    backdrop_root.location = camera_ray_point(camera, scene, 0.5, 0.62, 0.73)
    backdrop_root.rotation_euler = camera.rotation_euler.copy()
    backdrop = add_backdrop_cube(
        "ENV_STAGE_Backdrop", backdrop_root,
        (0.0, 0.0, 0.0), (0.88, 0.52, 0.015),
        backdrop_black, collections["geo"])
    groups["base"] += [backdrop_root, backdrop]
    for index, y in enumerate((-0.18, -0.075, 0.035, 0.145, 0.225)):
        bar = add_backdrop_cube(
            f"ENV_STAGE_ShelfLight_{index:02d}",
            backdrop_root, (0.0, y, 0.012),
            (0.82, 0.006, 0.0045), gold,
            collections["geo"])
        groups["base"].append(bar)
    for index, x in enumerate((-0.34, -0.17, 0.0, 0.17, 0.34)):
        bar = add_backdrop_cube(
            f"ENV_STAGE_VerticalBrass_{index:02d}",
            backdrop_root, (x, 0.035, 0.010),
            (0.006, 0.46, 0.005), brass,
            collections["geo"])
        groups["base"].append(bar)
    rng = random.Random(2026082504)
    for index in range(30):
        u = rng.uniform(0.04, 0.96)
        v = rng.uniform(0.54, 0.96)
        if 0.03 < u < 0.40 and 0.62 < v < 0.82:
            continue
        orb = particle_at(
            f"ENV_STAGE_BackdropBokeh_{index:02d}",
            camera, scene, (u, v, rng.uniform(0.65, 0.72)),
            rng.uniform(0.003, 0.009),
            gold_hot if index % 5 == 0 else gold,
            collections["dress"])
        groups["base"].append(orb)

    trace_points = (
        [(-0.235, -0.08), (-0.17, -0.08), (-0.17, -0.025), (-0.08, -0.025)],
        [(-0.23, 0.045), (-0.15, 0.045), (-0.15, 0.10), (-0.055, 0.10)],
    )
    for index, local_points in enumerate(trace_points):
        points = [
            (stage_center.x + x, stage_center.y + y, 0.00085)
            for x, y in local_points
        ]
        trace = helper.polyline(
            f"FX_STAGE_Circuit_{index:02d}",
            points, 0.00038, gold, collections["fx"])
        groups["base"].append(trace)

    card_materials = (card_black, brass)
    chip_black = (black, brass)
    chip_red = (oxblood, brass)
    groups["A"] += chip_at(
        "PROP_A_ForegroundChipLeft", camera, scene,
        (-0.06, 0.10, 0.42), -18, 0.72, chip_black, collections["dress"])
    groups["A"] += chip_at(
        "PROP_A_ForegroundChipRight", camera, scene,
        (1.05, 0.12, 0.43), 22, 0.62, chip_red, collections["dress"])
    for index, placement in enumerate((
            (0.48, 0.84, 0.61, -20, 1.00),
            (0.70, 0.91, 0.66, 24, 0.86),
            (0.91, 0.76, 0.62, -8, 0.78))):
        u, v, d, angle, scale = placement
        groups["A"] += card_at(
            f"PROP_A_FloatingCard_{index:02d}", camera, scene,
            (u, v, d), angle, scale, card_materials, collections["dress"])
    groups["A"] += create_route_particles(
        "A", camera, scene, 88, 401,
        gold, gold_hot, collections["fx"])

    groups["B"] += chip_at(
        "PROP_B_ForegroundChipRight", camera, scene,
        (1.04, 0.11, 0.42), 18, 0.58, chip_red, collections["dress"])
    for index, placement in enumerate((
            (0.42, 0.90, 0.66, -26, 1.06),
            (0.60, 0.80, 0.59, 18, 0.92),
            (0.82, 0.92, 0.68, -12, 0.88),
            (0.90, 0.55, 0.56, 28, 0.72),
            (0.38, 0.48, 0.54, -8, 0.68))):
        u, v, d, angle, scale = placement
        groups["B"] += card_at(
            f"PROP_B_RainCard_{index:02d}", camera, scene,
            (u, v, d), angle, scale, card_materials, collections["dress"])
    groups["B"] += create_route_particles(
        "B", camera, scene, 126, 402,
        gold, gold_hot, collections["fx"])

    for index, placement in enumerate((
            (-0.06, 0.13, 0.41, -20, 0.70, chip_black),
            (1.05, 0.12, 0.42, 20, 0.66, chip_red),
            (0.08, 0.88, 0.64, 16, 0.58, chip_red),
            (0.92, 0.86, 0.65, -18, 0.56, chip_black))):
        u, v, d, angle, scale, mats = placement
        groups["C"] += chip_at(
            f"PROP_C_VortexChip_{index:02d}", camera, scene,
            (u, v, d), angle, scale, mats, collections["dress"])
    for index, placement in enumerate((
            (0.42, 0.91, 0.66, -24, 1.00),
            (0.75, 0.92, 0.68, 18, 0.86),
            (0.94, 0.58, 0.56, -12, 0.68))):
        u, v, d, angle, scale = placement
        groups["C"] += card_at(
            f"PROP_C_VortexCard_{index:02d}", camera, scene,
            (u, v, d), angle, scale, card_materials, collections["dress"])
    groups["C"] += create_route_particles(
        "C", camera, scene, 150, 403,
        gold, gold_hot, collections["fx"])

    local_volume = helper.volume_material()
    volume_node = next(
        node for node in local_volume.node_tree.nodes
        if node.bl_idname == "ShaderNodeVolumePrincipled")
    volume_node.inputs["Density"].default_value = 0.005
    volume_node.inputs["Anisotropy"].default_value = 0.72
    bpy.ops.mesh.primitive_cube_add(
        location=(center.x - 0.02, center.y + 0.06, 0.12))
    volume = bpy.context.object
    volume.name = "FX_STAGE_LocalVolume"
    volume.dimensions = (0.54, 0.34, 0.28)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    volume.data.materials.append(local_volume)
    helper.move_to(volume, collections["fx"])
    groups["base"].append(volume)

    bpy.data.objects["LGT_Key_Broad"].data.energy = 3.1
    bpy.data.objects["LGT_Key_Broad"].data.size = 0.24
    bpy.data.objects["LGT_Fill_Weak"].data.energy = 0.24
    rim = helper.add_light(
        "LGT_STAGE_GoldRim", "SPOT",
        center + Vector((-0.17, 0.19, 0.22)),
        3.0, source.kelvin(2750),
        center + Vector((0.0, 0.025, 0.065)),
        collections["lights"])
    rim.data.spot_size = math.radians(25)
    rim.data.spot_blend = 0.45
    groups["base"].append(rim)
    fill_gold = helper.add_light(
        "LGT_STAGE_TableGold", "AREA",
        center + Vector((-0.14, -0.03, 0.12)),
        0.55, source.kelvin(3200), center,
        collections["lights"], 0.12)
    groups["base"].append(fill_gold)
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.0007, 0.0003, 0.0002, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.003
    for obj in scene.objects:
        if obj.name.startswith(("FX_", "ENV_STAGE_BackdropBokeh_")):
            obj.visible_shadow = False

    renderer = helper.configure_cycles(scene)
    scene.cycles.samples = 96
    scene.cycles.adaptive_threshold = 0.025
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.50
    configure_compositor(scene)

    outputs = {}
    settings = {
        "A-golden-lounge": ({"base", "A"}, 2.6, 0.46),
        "B-card-rain": ({"base", "B"}, 3.4, 0.56),
        "C-high-stakes-vortex": ({"base", "C"}, 4.2, 0.68),
    }
    cull_counts = {}
    for name, (visible, rim_energy, fill_energy) in settings.items():
        set_visible(groups, visible)
        rim.hide_render = False
        fill_gold.hide_render = False
        rim.data.energy = rim_energy
        fill_gold.data.energy = fill_energy
        route_key = name[0]
        cull_counts[name] = cull_product_overlap_fx(
            scene, camera, groups[route_key])
        path = HERE / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[name] = path.name

    set_visible(groups, {"base", "A"})
    rim.hide_render = False
    fill_gold.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    (HERE / "full-scene-redesign-report.json").write_text(
        json.dumps({
            "productGeometryModified": False,
            "camera": {
                "lensMm": 80,
                "elevationDegrees": 32,
                "distanceScale": 0.91,
                "shiftX": -0.19,
                "fStop": 3.8,
            },
            "routes": {
                "A-golden-lounge": "reference-A bias: architecture, cards, droplets",
                "B-card-rain": "vertical card motion and stronger volume",
                "C-high-stakes-vortex": "reference-B bias: chips and spiral energy",
            },
            "renderer": renderer,
            "samples": 96,
            "outputs": outputs,
            "culledProductOverlapFx": cull_counts,
            "screenSpaceParticles": 0,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
