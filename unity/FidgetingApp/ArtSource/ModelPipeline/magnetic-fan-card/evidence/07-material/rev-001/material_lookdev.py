"""Apply physically based product and support materials to approved geometry."""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
GEOMETRY_BLEND = (
    SCRIPT.parents[2] / "06-geometry/rev-001/"
    "fan-card-geometry-validation.blend"
)
PARAMETER_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-002/parameter_sweep.py"
)
OUTPUT = SCRIPT.parent
BLEND = OUTPUT / "fan-card-material-lookdev.blend"
TEXTURES = OUTPUT / "textures"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


source = load_module("fan_card_parameter_sweep", PARAMETER_SCRIPT)


def input_if(shader, name: str, value) -> None:
    if name in shader.inputs:
        shader.inputs[name].default_value = value


def metal_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    noise_scale: float,
    bump_strength: float,
    anisotropic: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = 1.0
    shader.inputs["Roughness"].default_value = roughness
    input_if(shader, "Anisotropic IOR Level", anisotropic)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 2.4
    noise.inputs["Roughness"].default_value = 0.68
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = (roughness * 0.72,) * 3 + (1.0,)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (
        min(1.0, roughness * 1.22),) * 3 + (1.0,)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.000025
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Roughness"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def support_material(name: str, kind: str) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    bump = nodes.new("ShaderNodeBump")
    if kind == "walnut":
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 5.0
        noise.inputs["Detail"].default_value = 5.0
        noise.inputs["Roughness"].default_value = 0.72
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        wave.inputs["Scale"].default_value = 7.0
        wave.inputs["Distortion"].default_value = 7.0
        wave.inputs["Detail"].default_value = 5.0
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 0.62
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.018, 0.006, 0.002, 1.0)
        ramp.color_ramp.elements[1].color = (0.16, 0.045, 0.012, 1.0)
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(texcoord.outputs["Generated"], wave.inputs["Vector"])
        links.new(noise.outputs["Fac"], mix.inputs[1])
        links.new(wave.outputs["Color"], mix.inputs[2])
        links.new(mix.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = 0.48
        bump.inputs["Strength"].default_value = 0.19
        bump.inputs["Distance"].default_value = 0.00045
        links.new(mix.outputs["Color"], bump.inputs["Height"])
    elif kind == "eva":
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 145.0
        noise.inputs["Detail"].default_value = 2.0
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.006, 0.008, 0.011, 1.0)
        ramp.color_ramp.elements[1].color = (0.030, 0.034, 0.040, 1.0)
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = 0.84
        bump.inputs["Strength"].default_value = 0.14
        bump.inputs["Distance"].default_value = 0.00018
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
    else:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 34.0
        noise.inputs["Detail"].default_value = 6.0
        voronoi = nodes.new("ShaderNodeTexVoronoi")
        voronoi.distance = "EUCLIDEAN"
        voronoi.feature = "DISTANCE_TO_EDGE"
        voronoi.inputs["Scale"].default_value = 52.0
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 0.70
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.055, 0.018, 0.004, 1.0)
        ramp.color_ramp.elements[1].color = (0.34, 0.14, 0.035, 1.0)
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(texcoord.outputs["Generated"], voronoi.inputs["Vector"])
        links.new(noise.outputs["Fac"], mix.inputs[1])
        links.new(voronoi.outputs["Distance"], mix.inputs[2])
        links.new(mix.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
        shader.inputs["Roughness"].default_value = 0.72
        bump.inputs["Strength"].default_value = 0.28
        bump.inputs["Distance"].default_value = 0.0007
        links.new(mix.outputs["Color"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def image_support_material(
    name: str,
    diffuse_path: Path | None,
    normal_path: Path,
    roughness_path: Path,
    scale: tuple[float, float, float],
    base_color: tuple[float, float, float, float] | None = None,
    saturation: float = 1.0,
    value: float = 1.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = scale
    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    if diffuse_path is not None:
        diffuse = nodes.new("ShaderNodeTexImage")
        diffuse.image = bpy.data.images.load(str(diffuse_path))
        diffuse.extension = "REPEAT"
        grade = nodes.new("ShaderNodeHueSaturation")
        grade.inputs["Saturation"].default_value = saturation
        grade.inputs["Value"].default_value = value
        links.new(mapping.outputs["Vector"], diffuse.inputs["Vector"])
        links.new(diffuse.outputs["Color"], grade.inputs["Color"])
        links.new(grade.outputs["Color"], shader.inputs["Base Color"])
    else:
        shader.inputs["Base Color"].default_value = (
            base_color or (0.008, 0.010, 0.013, 1.0))
    roughness = nodes.new("ShaderNodeTexImage")
    roughness.image = bpy.data.images.load(str(roughness_path))
    roughness.image.colorspace_settings.name = "Non-Color"
    roughness.extension = "REPEAT"
    normal = nodes.new("ShaderNodeTexImage")
    normal.image = bpy.data.images.load(str(normal_path))
    normal.image.colorspace_settings.name = "Non-Color"
    normal.extension = "REPEAT"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.48
    links.new(mapping.outputs["Vector"], roughness.inputs["Vector"])
    links.new(mapping.outputs["Vector"], normal.inputs["Vector"])
    links.new(roughness.outputs["Color"], shader.inputs["Roughness"])
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def configure_cycles(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(GEOMETRY_BLEND))
    scene = bpy.context.scene
    silver = metal_material(
        "MAT_WarmSilver_PBR", (0.36, 0.30, 0.23, 1.0),
        0.42, 760.0, 0.055, 0.32)
    gunmetal = metal_material(
        "MAT_Gunmetal_PBR", (0.028, 0.034, 0.042, 1.0),
        0.50, 620.0, 0.07, 0.18)
    etching = metal_material(
        "MAT_Etching_PBR", (0.006, 0.008, 0.010, 1.0),
        0.62, 480.0, 0.03)
    chrome = metal_material(
        "MAT_Chrome_PBR", (0.68, 0.74, 0.82, 1.0),
        0.12, 920.0, 0.02, 0.46)
    gold = metal_material(
        "MAT_RearGold_PBR", (0.46, 0.22, 0.045, 1.0),
        0.30, 720.0, 0.045, 0.20)
    for obj in scene.objects:
        name = obj.name
        if "WarmSilverFace" in name:
            assign(obj, silver)
        elif any(token in name for token in (
                "Rank_", "Spade", "Dot_")):
            assign(obj, etching)
        elif any(token in name for token in (
                "Track_Grille", "Magnet_")):
            assign(obj, gold)
        elif any(token in name for token in (
                "Bearing", "Follower")):
            assign(obj, chrome)
        elif obj.type in {"MESH", "CURVE", "FONT"}:
            assign(obj, gunmetal)
    product_objects = [
        obj for obj in scene.objects
        if obj.type in {"MESH", "CURVE", "FONT"}
    ]
    center, half_extent = source.bounds_for(product_objects)
    center.z = 0.008
    bpy.ops.mesh.primitive_plane_add(
        size=1.0, location=(center.x, center.y, -0.0001))
    support = bpy.context.object
    support.name = "GEO_Support_Base"
    support.scale = (0.80, 0.60, 1.0)
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True)
    supports = {
        "A-dark-walnut": image_support_material(
            "MAT_A_DarkWalnut",
            TEXTURES / "dark_wood/diffuse.jpg",
            TEXTURES / "dark_wood/normal.jpg",
            TEXTURES / "dark_wood/roughness.jpg",
            (2.3, 2.3, 2.3),
            saturation=0.78,
            value=0.62),
        "B-charcoal-hard-case": image_support_material(
            "MAT_B_CharcoalEVA",
            None,
            TEXTURES / "rubberized_track/normal.jpg",
            TEXTURES / "rubberized_track/roughness.jpg",
            (7.0, 7.0, 7.0),
            (0.008, 0.010, 0.013, 1.0)),
        "C-cork-slab": image_support_material(
            "MAT_C_Cork",
            TEXTURES / "cork/Cork001_1K-JPG_Color.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_NormalGL.jpg",
            TEXTURES / "cork/Cork001_1K-JPG_Roughness.jpg",
            (4.0, 4.0, 4.0),
            saturation=0.72,
            value=0.70),
    }
    support.data.materials.append(supports["A-dark-walnut"])

    camera = bpy.data.objects.get("CAM_Geometry")
    camera.name = "CAM_Hero_Selected"
    camera.data.type = "PERSP"
    camera.data.lens = 80.0
    camera.data.sensor_width = 36.0
    camera.data.shift_x = -0.22
    camera.location = source.camera_position(
        center, 80.0, 32.0, half_extent)
    source.aim(camera, center)
    scene.camera = camera

    for obj in list(scene.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj, do_unlink=True)
    key_data = bpy.data.lights.new("LGT_Key_Broad", "AREA")
    key_data.energy = 3.0
    key_data.shape = "DISK"
    key_data.size = 0.35
    key_data.color = source.kelvin(5000)
    key = bpy.data.objects.new("LGT_Key_Broad", key_data)
    bpy.context.collection.objects.link(key)
    key.location = center + Vector((0.16, -0.14, 0.24))
    source.aim(key, center)
    fill_data = bpy.data.lights.new("LGT_Fill_Weak", "AREA")
    fill_data.energy = 0.6
    fill_data.shape = "DISK"
    fill_data.size = 0.50
    fill_data.color = source.kelvin(6500)
    fill = bpy.data.objects.new("LGT_Fill_Weak", fill_data)
    bpy.context.collection.objects.link(fill)
    fill.location = center + Vector((-0.18, -0.05, 0.12))
    source.aim(fill, center)
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.006, 0.007, 0.009, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.018
    configure_cycles(scene)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    outputs = {}
    for variant, mat in supports.items():
        support.data.materials[0] = mat
        path = OUTPUT / f"material-{variant}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs[variant] = path.name

    support.data.materials[0] = supports["B-charcoal-hard-case"]
    camera.data.shift_x = 0.0
    camera.data.lens = 105.0
    close_extent = half_extent * 0.52
    camera.location = source.camera_position(
        center, 105.0, 38.0, close_extent)
    source.aim(camera, center)
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.filepath = str(OUTPUT / "material-closeup.png")
    bpy.ops.render.render(write_still=True)

    report = {
        "productMaterials": {
            "warmSilver": {"metallic": 1.0, "roughness": 0.42},
            "gunmetal": {"metallic": 1.0, "roughness": 0.50},
            "etching": {"metallic": 1.0, "roughness": 0.62},
            "chrome": {"metallic": 1.0, "roughness": 0.12},
            "rearGold": {"metallic": 1.0, "roughness": 0.30}
        },
        "supportVariants": outputs,
        "camera": {"lensMm": 80, "elevationDegrees": 32},
        "light": {"temperatureKelvin": 5000, "sourceSizeMm": 350},
        "shippingAssetModified": False
    }
    (OUTPUT / "material-lookdev-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
