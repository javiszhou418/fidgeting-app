"""Render three controlled white-model environment blockouts."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
CONTRACT_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-lookdev-blockout.blend"

spec = importlib.util.spec_from_file_location(
    "fan_card_parameter_sweep", CONTRACT_SCRIPT)
source = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(source)


def simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    texture_scale: float,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = roughness
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = texture_scale
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.65
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.0003
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def assign_single_material(obj: bpy.types.Object,
                           mat: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def main() -> None:
    source.clean()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    clay = simple_material(
        "MAT_Blockout_Product", (0.32, 0.33, 0.35, 1.0), 0.62, 900.0)
    assembly = bpy.data.objects.new("MagneticFanCard_Root", None)
    bpy.context.collection.objects.link(assembly)
    for index, (rank, angle) in enumerate(
            (("Q", 0), ("K", 45), ("A", 90))):
        layer = source.create_layer(
            index, rank, angle, clay, clay, clay)
        layer.parent = assembly
    assembly.rotation_euler.z = math.radians(90.0)
    source.add_bearing(clay)
    for obj in bpy.context.scene.objects:
        if obj.name != "MagneticFanCard_Root":
            assign_single_material(obj, clay)
    bpy.context.view_layer.update()
    product_meshes = [
        obj for obj in bpy.context.scene.objects if obj.type == "MESH"
    ]
    target, half_extent = source.bounds_for(product_meshes)
    target.z = 0.008

    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(target.x, target.y, 0.0))
    support = bpy.context.object
    support.name = "GEO_Support_Base"
    support.scale = (0.80, 0.60, 1.0)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    support_materials = {
        "A-dark-walnut": simple_material(
            "MAT_A_DarkWalnut", (0.075, 0.033, 0.014, 1.0), 0.54, 7.0),
        "B-charcoal-hard-case": simple_material(
            "MAT_B_CharcoalEVA", (0.012, 0.015, 0.020, 1.0), 0.82, 110.0),
        "C-cork-slab": simple_material(
            "MAT_C_Cork", (0.19, 0.095, 0.038, 1.0), 0.72, 38.0),
    }
    support.data.materials.append(support_materials["A-dark-walnut"])

    camera_data = bpy.data.cameras.new("CAM_Hero_Selected")
    camera_data.sensor_width = 36.0
    camera_data.lens = 80.0
    camera_data.shift_x = -0.22
    camera = bpy.data.objects.new("CAM_Hero_Selected", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = source.camera_position(
        target, 80.0, 32.0, half_extent)
    source.aim(camera, target)
    scene.camera = camera

    key_data = bpy.data.lights.new("LGT_Key_Broad", "AREA")
    key_data.energy = 3.0
    key_data.shape = "DISK"
    key_data.size = 0.35
    key_data.color = source.kelvin(5000)
    key = bpy.data.objects.new("LGT_Key_Broad", key_data)
    bpy.context.collection.objects.link(key)
    key.location = target + Vector((0.16, -0.14, 0.24))
    source.aim(key, target)

    fill_data = bpy.data.lights.new("LGT_Fill_Weak", "AREA")
    fill_data.energy = 0.6
    fill_data.shape = "DISK"
    fill_data.size = 0.50
    fill_data.color = source.kelvin(6500)
    fill = bpy.data.objects.new("LGT_Fill_Weak", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = target + Vector((-0.18, -0.05, 0.12))
    source.aim(fill, target)

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.006, 0.007, 0.009, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.012
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    outputs = {}
    for variant, mat in support_materials.items():
        support.data.materials[0] = mat
        path = OUTPUT / f"blockout-{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name
    (OUTPUT / "blockout-report.json").write_text(
        json.dumps({
            "camera": {
                "lensMm": 80,
                "elevationDegrees": 32,
                "shiftX": -0.22
            },
            "lighting": {
                "keyTemperatureKelvin": 5000,
                "keySourceSizeMm": 350,
                "keyToFill": "5:1"
            },
            "product": "canonical guardrail-derived white model",
            "variants": outputs,
            "shippingAssetModified": False
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
