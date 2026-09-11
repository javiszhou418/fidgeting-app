#!/usr/bin/env python3
"""Render Gate 10 rev 11 Blender and GLB from one camera and HDR."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent / "10-export" / "rev-011" / "package"
GLB = PACKAGE / "magnetic-slide-tile-render-r011.glb"
ENVIRONMENT = PACKAGE / "environment" / "target-shipping-studio-r009.exr"
OUTPUT = HERE / "parity-source"
CORE = ["BottomExterior", "MovingTopBody"]


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        item.matrix_world @ Vector(corner)
        for item in objects
        for corner in item.bound_box
    ]
    return (
        Vector(tuple(min(point[index] for point in points) for index in range(3))),
        Vector(tuple(max(point[index] for point in points) for index in range(3))),
    )


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.frame_set(0)
    scene.render.engine = "BLENDER_EEVEE"
    scene.camera = bpy.data.objects["M08R6_Hero"]
    scene.camera.location = (74.0, -116.0, 72.0)
    direction = Vector((0.0, -2.0, 5.0)) - scene.camera.location
    scene.camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera.data.lens = 76.0
    scene.camera.data.sensor_width = 36.0
    scene.camera.data.sensor_fit = "HORIZONTAL"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 620
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.view_settings.look = "None"
    scene.view_settings.view_transform = "Raw"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    for item in list(bpy.data.objects):
        if item.type == "LIGHT":
            bpy.data.objects.remove(item, do_unlink=True)
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes.clear()
    output = world.node_tree.nodes.new("ShaderNodeOutputWorld")
    background = world.node_tree.nodes.new("ShaderNodeBackground")
    environment = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
    environment.image = bpy.data.images.load(str(ENVIRONMENT), check_existing=True)
    environment.image.colorspace_settings.name = "Non-Color"
    background.inputs["Strength"].default_value = 0.85
    world.node_tree.links.new(environment.outputs["Color"], background.inputs["Color"])
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])


def render(path: Path, file_format: str) -> None:
    scene = bpy.context.scene
    scene.render.film_transparent = True
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = file_format
    scene.render.image_settings.color_mode = "RGBA"
    if file_format == "OPEN_EXR":
        scene.render.image_settings.color_depth = "32"
        scene.render.image_settings.exr_codec = "ZIP"
    bpy.ops.render.render(write_still=True)


def diagnostic_material(name: str, color: tuple[float, float, float, float]):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = 1.0
    material.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def swap_for_diagnostic(objects: list[bpy.types.Object], mode: str):
    originals = {
        item.name: [slot.material for slot in item.material_slots]
        for item in objects
    }
    palette = {
        "UpperTopArtwork": (0.86, 0.12, 0.15, 1.0),
        "LowerTopArtwork": (0.68, 0.06, 0.09, 1.0),
        "SolidDarkSide": (0.10, 0.34, 0.60, 1.0),
        "PolishedBrightSilverRim": (0.82, 0.86, 0.90, 1.0),
        "NeutralUnderside": (0.24, 0.62, 0.42, 1.0),
    }
    white = diagnostic_material(f"DiagWhite_{mode}", (1, 1, 1, 1))
    materials = {key: diagnostic_material(f"Diag_{key}_{mode}", value)
                 for key, value in palette.items()}
    for item in objects:
        for slot in item.material_slots:
            if mode == "silhouette":
                slot.material = white
                continue
            semantic = slot.material.name.removesuffix(".001")
            matched = next((value for key, value in materials.items()
                            if key in semantic), None)
            if matched is None:
                raise RuntimeError(f"Unknown partition material: {semantic}")
            slot.material = matched
    return originals


def restore(objects: list[bpy.types.Object], originals) -> None:
    for item in objects:
        for index, material in enumerate(originals[item.name]):
            item.material_slots[index].material = material


def render_isolated_glb(objects: list[bpy.types.Object], semantic: str, label: str) -> None:
    originals = {
        item.name: [slot.material for slot in item.material_slots]
        for item in objects
    }
    target = next(
        slot.material
        for item in objects
        for slot in item.material_slots
        if semantic in slot.material.name
    )
    for item in objects:
        for slot in item.material_slots:
            slot.material = target
    render(OUTPUT / f"glb-isolated-{label}-linear.exr", "OPEN_EXR")
    restore(objects, originals)


def render_set(label: str, objects: list[bpy.types.Object]) -> None:
    render(OUTPUT / f"{label}-full-linear.exr", "OPEN_EXR")
    for mode in ("silhouette", "partitions"):
        originals = swap_for_diagnostic(objects, mode)
        render(OUTPUT / f"{label}-{mode}-linear.exr", "OPEN_EXR")
        restore(objects, originals)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configure_scene()
    source_objects = [bpy.data.objects[name] for name in CORE]
    render_set("blender-authoritative", source_objects)
    source_min, source_max = bounds(source_objects)

    before = {item.as_pointer() for item in bpy.data.objects}
    bpy.ops.import_scene.gltf(
        filepath=str(GLB), import_pack_images=True, merge_vertices=False)
    imported = [item for item in bpy.data.objects if item.as_pointer() not in before]
    meshes = [item for item in imported if item.type == "MESH"]
    roots = [item for item in imported if item.parent is None]
    imported_min, imported_max = bounds(meshes)
    source_size = source_max - source_min
    imported_size = imported_max - imported_min
    scale = source_size.length / imported_size.length
    for root in roots:
        root.scale *= scale
    bpy.context.view_layer.update()
    imported_min, imported_max = bounds(meshes)
    delta = (source_min + source_max) * 0.5 - (imported_min + imported_max) * 0.5
    for root in roots:
        root.location += delta
    for item in source_objects:
        item.hide_render = True
    for item in meshes:
        item.hide_render = True
    imported_product = [
        item for item in meshes
        if item.data.name.startswith("BottomExterior_Mesh")
        or item.data.name.startswith("MovingTopBody_Mesh")
    ]
    for item in imported_product:
        item.hide_render = False
    render_set("glb-baseline", imported_product)
    render_isolated_glb(
        imported_product, "PolishedBrightSilverRim", "silver")
    render_isolated_glb(
        imported_product, "UpperTopArtwork", "blood-red")
    report = {
        "schemaVersion": 1,
        "camera": "M08R6_Hero",
        "cameraLocationMillimeters": list(bpy.data.objects["M08R6_Hero"].location),
        "cameraLensMillimeters": 76.0,
        "cameraSensorWidthMillimeters": 36.0,
        "resolution": [1000, 620],
        "environment": str(ENVIRONMENT.relative_to(HERE.parents[5])),
        "environmentStrength": 0.85,
        "lightCount": 0,
        "displayMapping": "linear outputs; neutral-display-v1 applied downstream",
        "sourceBoundsMillimeters": list(source_size),
        "glbBoundsMillimeters": list(imported_max - imported_min),
        "importScale": scale,
        "sourceProductMeshes": [item.name for item in source_objects],
        "glbProductMeshes": [item.name for item in imported_product],
        "pass": abs(scale - 1.0) <= 0.001
        and all(abs(a - b) <= 0.002
                for a, b in zip(source_size, imported_max - imported_min)),
    }
    (HERE / "blender-glb-capture-report.json").write_text(
        json.dumps(report, indent=2) + "\n")
    if not report["pass"]:
        raise RuntimeError("Blender/GLB same-camera capture validation failed.")


if __name__ == "__main__":
    main()
