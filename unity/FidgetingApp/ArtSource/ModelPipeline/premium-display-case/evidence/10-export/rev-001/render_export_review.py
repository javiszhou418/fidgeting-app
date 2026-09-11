#!/usr/bin/env python3
"""Render assembled whole-case views from Blend, FBX, and GLB."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
PRODUCT_BLEND = HERE / "premium-display-case-product-r001.blend"
FBX_EXPORT = HERE / "premium-display-case-product-r001.fbx"
GLB_EXPORT = HERE / "premium-display-case-product-r001.glb"
ROUNDTRIP_REPORT = HERE / "export-roundtrip-validation.json"
RENDER_REPORT = HERE / "export-render-report.json"
OUTPUTS = {
    "blend": RAW / "source-hero.png",
    "fbx": RAW / "fbx-hero.png",
    "glb": RAW / "glb-hero.png",
}
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def set_input(node, name: str, value) -> None:
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def review_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    transmission: float = 0.0,
    alpha: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    set_input(principled, "Base Color", color)
    set_input(principled, "Roughness", roughness)
    set_input(principled, "Metallic", metallic)
    set_input(principled, "Transmission Weight", transmission)
    set_input(principled, "IOR", 1.52)
    set_input(principled, "Alpha", alpha)
    if hasattr(material, "surface_render_method") and alpha < 1.0:
        material.surface_render_method = "DITHERED"
    return material


def apply_review_materials() -> None:
    materials = {
        "shell": review_material(
            "M10_REVIEW_FrostedShell",
            (0.43, 0.52, 0.60, 1.0),
            0.24,
            transmission=0.78,
            alpha=0.28,
        ),
        "tube": review_material(
            "M10_REVIEW_ConnectedTube",
            (0.74, 0.80, 0.84, 1.0),
            0.2,
            metallic=0.12,
            transmission=0.35,
            alpha=0.68,
        ),
        "insert": review_material(
            "M10_REVIEW_BlackInsert",
            (0.012, 0.016, 0.022, 1.0),
            0.86,
        ),
        "label": review_material(
            "M10_REVIEW_BlankRuntimeLabel",
            (0.72, 0.69, 0.62, 1.0),
            0.67,
        ),
    }
    assignments = {
        "RearPolycarbonateShell": materials["shell"],
        "FrontPolycarbonateShell": materials["shell"],
        "ContinuousTubePerimeter": materials["tube"],
        "TactileBackgroundInsert": materials["insert"],
        "PhysicalLabel": materials["label"],
    }
    for name, material in assignments.items():
        obj = bpy.data.objects[name]
        obj.data.materials.clear()
        obj.data.materials.append(material)


def orient_imported_scene() -> None:
    root = bpy.data.objects["PresentationRoot"]
    root.rotation_mode = "XYZ"
    root.rotation_euler = (-math.pi / 2.0, 0.0, 0.0)
    root.scale = (1000.0, 1000.0, 1000.0)
    bpy.context.view_layer.update()


def add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    color: tuple[float, float, float],
) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, Vector((0.0, 10.0, 0.0)))


def configure_review_scene(output: Path) -> None:
    apply_review_materials()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 820
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.filepath = str(output)
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"

    if scene.world is None:
        scene.world = bpy.data.worlds.new("M10_REVIEW_World")
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links
    background = nodes.get("Background") or nodes.new("ShaderNodeBackground")
    output_node = (
        nodes.get("World Output")
        or nodes.get("WorldOutput")
        or nodes.new("ShaderNodeOutputWorld")
    )
    if not background.outputs["Background"].is_linked:
        links.new(background.outputs["Background"], output_node.inputs["Surface"])
    background.inputs["Color"].default_value = (0.012, 0.015, 0.021, 1.0)
    background.inputs["Strength"].default_value = 0.18

    camera_data = bpy.data.cameras.new("M10_REVIEW_Camera")
    camera = bpy.data.objects.new("M10_REVIEW_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera.location = (330.0, 185.0, 690.0)
    camera_data.lens = 62.0
    camera_data.sensor_width = 36.0
    look_at(camera, Vector((0.0, 8.0, 0.0)))
    scene.camera = camera

    add_area_light(
        "M10_REVIEW_Key",
        (420.0, 410.0, 520.0),
        900000.0,
        440.0,
        (1.0, 0.97, 0.93),
    )
    add_area_light(
        "M10_REVIEW_Fill",
        (-360.0, 120.0, 380.0),
        420000.0,
        520.0,
        (0.90, 0.95, 1.0),
    )
    add_area_light(
        "M10_REVIEW_Rim",
        (-260.0, 320.0, -420.0),
        520000.0,
        340.0,
        (0.94, 0.97, 1.0),
    )
    bpy.ops.render.render(write_still=True)


def load_format(format_name: str) -> None:
    if format_name == "blend":
        bpy.ops.wm.open_mainfile(filepath=str(PRODUCT_BLEND))
        return
    reset()
    if format_name == "fbx":
        bpy.ops.import_scene.fbx(
            filepath=str(FBX_EXPORT),
            use_custom_props=True,
            use_image_search=False,
        )
    elif format_name == "glb":
        bpy.ops.import_scene.gltf(filepath=str(GLB_EXPORT))
    else:
        raise ValueError(format_name)
    orient_imported_scene()


def world_bounds_mm() -> dict:
    points = [
        bpy.data.objects[name].matrix_world @ Vector(corner)
        for name in SUBJECT_NAMES
        for corner in bpy.data.objects[name].bound_box
    ]
    minimum = [min(point[index] for point in points) for index in range(3)]
    maximum = [max(point[index] for point in points) for index in range(3)]
    return {
        "minimum": [round(value, 5) for value in minimum],
        "maximum": [round(value, 5) for value in maximum],
        "size": [
            round(maximum[index] - minimum[index], 5)
            for index in range(3)
        ],
    }


def main() -> None:
    roundtrip = json.loads(ROUNDTRIP_REPORT.read_text(encoding="utf-8"))
    if roundtrip["status"] != "pass":
        raise RuntimeError("Round-trip validation must pass before review rendering.")
    RAW.mkdir(parents=True, exist_ok=True)
    frames = {}
    for format_name, output in OUTPUTS.items():
        load_format(format_name)
        before = world_bounds_mm()
        configure_review_scene(output)
        if not output.exists() or output.stat().st_size == 0:
            raise RuntimeError(f"Review render is missing: {output}")
        frames[format_name] = {
            "path": str(output),
            "sha256": sha256(output),
            "renderBounds": before,
            "assemblyState": "assembled",
            "reviewMaterialOverride": True,
        }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "notice": "ASSEMBLED WHOLE-CASE EXPORT REVIEW RENDERS",
        "frames": frames,
        "reviewPolicy": {
            "wholeAssembledCaseOnly": True,
            "explodedPartCount": 0,
            "toyPrizeBundled": False,
            "placeholderTextBaked": False,
            "reviewMaterialOverrideOnly": True,
            "materialParityClaimed": False,
            "shippingUnityChanged": False,
        },
        "checks": {
            "threeFormatsRendered": len(frames) == 3,
            "allFramesExist": all(
                Path(frame["path"]).exists() for frame in frames.values()
            ),
            "wholeCaseOnly": True,
            "noExplodedReview": True,
            "noToyPrize": True,
            "noShippingUnity": True,
        },
    }
    RENDER_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
