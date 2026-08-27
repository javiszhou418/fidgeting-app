#!/usr/bin/env python3
"""Render the approved Gate 10 source with the shared Gate 11 neutral camera."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
RECIPE = json.loads((ROOT / "neutral-camera-recipe.json").read_text())
OUTPUT = ROOT / "blender-neutral.png"
SILHOUETTE = ROOT / "blender-neutral-silhouette.png"
REPORT = ROOT / "blender-neutral-report.json"


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def main() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = RECIPE["resolution"]
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = RECIPE["exposure"]
    scene.view_settings.gamma = 1.0

    world = scene.world or bpy.data.worlds.new("Gate11NeutralWorld")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    camera_background = nodes.new("ShaderNodeBackground")
    camera_background.inputs["Color"].default_value = (*RECIPE["backgroundLinearRgb"], 1.0)
    camera_background.inputs["Strength"].default_value = 1.0
    reflection_background = nodes.new("ShaderNodeBackground")
    reflection_background.inputs["Color"].default_value = (0.34, 0.35, 0.35, 1.0)
    reflection_background.inputs["Strength"].default_value = 0.85
    light_path = nodes.new("ShaderNodeLightPath")
    mix = nodes.new("ShaderNodeMixShader")
    world.node_tree.links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    world.node_tree.links.new(reflection_background.outputs[0], mix.inputs[1])
    world.node_tree.links.new(camera_background.outputs[0], mix.inputs[2])
    world.node_tree.links.new(mix.outputs[0], output.inputs["Surface"])

    camera_data = bpy.data.cameras.new("CAM_Gate11Neutral")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = Vector(RECIPE["camera"]["blenderPositionMm"])
    camera_data.lens = RECIPE["camera"]["lensMm"]
    camera_data.sensor_width = RECIPE["camera"]["sensorWidthMm"]
    camera_data.sensor_fit = "HORIZONTAL"
    camera_data.clip_start = RECIPE["camera"]["nearMeters"] * 1000.0
    camera_data.clip_end = RECIPE["camera"]["farMeters"] * 1000.0
    look_at(camera, Vector(RECIPE["camera"]["blenderLookAtMm"]))
    scene.camera = camera

    lights = [
        ("NeutralKey", (-52.0, -42.0, 52.0), (0.0, 0.0, 0.0), 62000.0, (1.0, 0.99, 0.97), 60.0, 8.0),
        ("NeutralFill", (44.0, -50.0, 30.0), (0.0, -8.0, 0.0), 30000.0, (1.0, 1.0, 1.0), 28.0, 22.0),
        ("NeutralRim", (30.0, 55.0, 25.0), (0.0, 10.0, 0.0), 48000.0, (0.95, 0.98, 1.0), 40.0, 7.0),
    ]
    for name, location, target, energy, color, size, size_y in lights:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = "RECTANGLE"
        data.size = size
        data.size_y = size_y
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        look_at(light, Vector(target))

    card_material = bpy.data.materials.new("Gate11NeutralReflectionCard")
    card_material.use_nodes = True
    card_shader = card_material.node_tree.nodes["Principled BSDF"]
    card_shader.inputs["Base Color"].default_value = (0.92, 0.92, 0.90, 1.0)
    card_shader.inputs["Roughness"].default_value = 0.82
    for name, location, size in [
        ("ReflectionCardLeft", (-70.0, -38.0, 22.0), 92.0),
        ("ReflectionCardRight", (64.0, 14.0, 28.0), 74.0),
        ("ReflectionCardTop", (0.0, 4.0, 82.0), 110.0),
    ]:
        bpy.ops.mesh.primitive_plane_add(size=size, location=location)
        card = bpy.context.object
        card.name = name
        card.data.materials.append(card_material)
        look_at(card, Vector((0.0, 0.0, 0.0)))
        card.visible_camera = False
        card.visible_diffuse = False
        card.visible_glossy = True
        card.visible_shadow = False

    render_meshes = [
        obj for obj in scene.objects
        if obj.type == "MESH"
        and not obj.name.startswith("UCX_")
        and not obj.name.startswith("ReflectionCard")
    ]
    for obj in render_meshes:
        obj.hide_render = False
    scene.render.filepath = str(OUTPUT)
    bpy.ops.render.render(write_still=True)
    original_materials = {
        obj.name: [material for material in obj.data.materials]
        for obj in render_meshes
    }
    silhouette_material = bpy.data.materials.new("Gate11SilhouetteWhite")
    silhouette_material.use_nodes = True
    silhouette_shader = silhouette_material.node_tree.nodes["Principled BSDF"]
    silhouette_shader.inputs["Base Color"].default_value = (0.75, 0.75, 0.75, 1.0)
    silhouette_shader.inputs["Metallic"].default_value = 0.0
    silhouette_shader.inputs["Roughness"].default_value = 1.0
    for obj in render_meshes:
        obj.data.materials.clear()
        obj.data.materials.append(silhouette_material)
    scene.render.filepath = str(SILHOUETTE)
    bpy.ops.render.render(write_still=True)
    for obj in render_meshes:
        obj.data.materials.clear()
        for material in original_materials[obj.name]:
            obj.data.materials.append(material)

    materials = {
        obj.name: [slot.material.name if slot.material else None for slot in obj.material_slots]
        for obj in render_meshes
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "11-unity-parity",
        "revision": 1,
        "output": OUTPUT.name,
        "silhouetteOutput": SILHOUETTE.name,
        "resolution": RECIPE["resolution"],
        "camera": RECIPE["camera"],
        "renderMeshes": [obj.name for obj in render_meshes],
        "materials": materials,
        "materialState": "approved Gate 07 rev 7 procedural Blender materials",
        "emission": 0.0,
        "shippingSceneModified": False,
        "pass": OUTPUT.exists() and SILHOUETTE.exists() and len(render_meshes) == 2,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Blender neutral render did not satisfy Gate 11.")


if __name__ == "__main__":
    main()
