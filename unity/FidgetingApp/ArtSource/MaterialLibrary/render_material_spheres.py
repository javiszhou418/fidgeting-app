"""Render one calibration sphere per material in materials.json.

    blender -b --python render_material_spheres.py -- --library materials.json --out spheres [--ids a,b] [--size 384] [--samples 64]

Same three-light rig as the metal-three-blade Gate 07/08 lookdev (key upper-left, fill right, thin top strip),
matte dark floor with a soft contact shadow, Cycles + AgX. The sphere is the swatch: it shows how the Blender
Principled values read, not the Unity result. Materials with `blender.authority == derived-from-unity` are
labelled as such in the JSON; the sphere still uses the derived Principled values.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ids", default="")
    parser.add_argument("--size", type=int, default=384)
    parser.add_argument("--samples", type=int, default=64)
    return parser.parse_args(argv)


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value
        return True
    return False


def build_material(spec):
    material = bpy.data.materials.new(f"LIB_{spec['id']}")
    material.use_nodes = True
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    blender = spec["blender"]
    set_input(bsdf, "Base Color", (*blender["baseColor"], 1.0))
    set_input(bsdf, "Metallic", float(blender["metallic"]))
    set_input(bsdf, "Roughness", float(blender["roughness"]))
    if "specularIorLevel" in blender:
        set_input(bsdf, "Specular IOR Level", float(blender["specularIorLevel"]))
    if "anisotropic" in blender:
        set_input(bsdf, "Anisotropic", float(blender["anisotropic"]))
        tangent = tree.nodes.new("ShaderNodeTangent")
        tangent.direction_type = "RADIAL"
        tangent.axis = "Z"
        if "Tangent" in bsdf.inputs:
            tree.links.new(tangent.outputs[0], bsdf.inputs["Tangent"])
    bump_spec = blender.get("bump")
    if bump_spec:
        coord = tree.nodes.new("ShaderNodeTexCoord")
        wave = tree.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"
        wave.rings_direction = "Z"
        wave.inputs["Scale"].default_value = 2 * math.pi / (10.0 * 0.12)
        wave.inputs["Distortion"].default_value = 0.0
        wave.inputs["Detail"].default_value = 1.0
        bump = tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = float(bump_spec.get("strength", 0.1))
        bump.inputs["Distance"].default_value = float(bump_spec.get("distance", 0.004))
        tree.links.new(coord.outputs["Object"], wave.inputs["Vector"])
        tree.links.new(wave.outputs["Fac"], bump.inputs["Height"])
        tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    tree.links.new(bsdf.outputs[0], output.inputs[0])
    return material


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def area_light(name, location, target, size, energy, size_y=None):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE" if size_y else "SQUARE"
    data.size = size
    if size_y:
        data.size_y = size_y
    data.energy = energy
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = Vector(location)
    look_at(obj, target)
    return obj


def build_scene(size, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("LIB_World")
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.02, 0.022, 0.026, 1.0)
    background.inputs["Strength"].default_value = 1.0
    scene.world = world

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=96, ring_count=48, location=(0, 0, 1.0))
    sphere = bpy.context.active_object
    sphere.name = "Swatch"
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.02))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor_material = bpy.data.materials.new("LIB_Floor")
    floor_material.use_nodes = True
    floor_bsdf = floor_material.node_tree.nodes["Principled BSDF"]
    set_input(floor_bsdf, "Base Color", (0.035, 0.035, 0.038, 1.0))
    set_input(floor_bsdf, "Metallic", 0.0)
    set_input(floor_bsdf, "Roughness", 0.85)
    floor.data.materials.append(floor_material)

    area_light("Key", (-3.2, -3.6, 4.6), (0, 0, 1.0), 3.2, 900)
    area_light("Fill", (4.2, -2.4, 2.6), (0, 0, 1.0), 4.0, 260)
    area_light("TopStrip", (0.4, 1.8, 5.2), (0, 0, 1.0), 0.35, 420, size_y=5.0)

    camera_data = bpy.data.cameras.new("Camera")
    camera_data.lens = 65
    camera = bpy.data.objects.new("Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = Vector((0.0, -6.4, 2.35))
    look_at(camera, (0, 0, 1.0))
    scene.camera = camera
    return scene, sphere


def main():
    args = parse_args()
    library = json.loads(Path(args.library).read_text(encoding="utf8"))
    wanted = {value for value in args.ids.split(",") if value}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    scene, sphere = build_scene(args.size, args.samples)
    rendered = []
    for spec in library["materials"]:
        if wanted and spec["id"] not in wanted:
            continue
        material = build_material(spec)
        sphere.data.materials.clear()
        sphere.data.materials.append(material)
        target = out / f"{spec['id']}.png"
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        rendered.append(str(target))
        print(f"rendered {target}")
    (out / "render-manifest.json").write_text(json.dumps({
        "blender": bpy.app.version_string,
        "engine": scene.render.engine,
        "samples": args.samples,
        "size": args.size,
        "rendered": rendered
    }, indent=2), encoding="utf8")


main()
