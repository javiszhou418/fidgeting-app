"""Render truthful Blender checkpoints for the authored display-case model."""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def principled_material(name: str, base: tuple[float, float, float, float],
                        metallic: float, roughness: float,
                        transmission: float = 0.0, alpha: float = 1.0) -> None:
    material = bpy.data.materials.get(name)
    if material is None:
        return
    material.use_nodes = True
    node = material.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = base
    node.inputs["Metallic IOR Level" if "Metallic IOR Level" in node.inputs else "Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    if "Transmission Weight" in node.inputs:
        node.inputs["Transmission Weight"].default_value = transmission
    if "Alpha" in node.inputs:
        node.inputs["Alpha"].default_value = alpha
    if "IOR" in node.inputs:
        node.inputs["IOR"].default_value = 1.49
    material.diffuse_color = (*base[:3], alpha)
    if alpha < 1 and hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"


def area_light(name: str, location: tuple[float, float, float], energy: float,
               color: tuple[float, float, float], size: float,
               target: Vector) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)


def configure_scene() -> bpy.types.Object:
    scene = bpy.context.scene
    # Blender 5.2 exposes Eevee Next through the stable BLENDER_EEVEE enum.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1100
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.render.fps = 60
    scene.world.color = (0.28, 0.035, 0.14)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.34, 0.045, 0.17, 1.0)
    background.inputs["Strength"].default_value = 0.30

    principled_material("MAT_Acrylic_Clear", (0.70, 0.84, 0.92, 1.0), 0.0, 0.045, 1.0, 0.13)
    principled_material("MAT_BrushedMetal", (0.62, 0.66, 0.72, 1.0), 0.98, 0.18)
    principled_material("MAT_NeutralGraphite", (0.055, 0.068, 0.084, 1.0), 0.46, 0.34)
    principled_material("MAT_BlackVelvet", (0.012, 0.016, 0.022, 1.0), 0.0, 0.84)
    principled_material("MAT_MatteBlackBox", (0.003, 0.004, 0.006, 1.0), 0.10, 0.22)

    camera_data = bpy.data.cameras.new("ValidationCamera")
    camera_data.lens = 58
    camera = bpy.data.objects.new("ValidationCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera

    target = Vector((0.0, 0.0, 0.0))
    area_light("Key_Softbox", (-0.30, -0.38, 0.40), 52, (1.0, 0.60, 0.82), 0.28, target)
    area_light("Fill_Softbox", (0.34, -0.20, 0.12), 28, (0.64, 0.82, 1.0), 0.22, target)
    area_light("Rim_Strip", (0.08, 0.32, 0.30), 72, (1.0, 0.22, 0.66), 0.16, target)
    return camera


def render(camera: bpy.types.Object, path: Path,
           location: tuple[float, float, float], target: tuple[float, float, float],
           transparent: bool) -> None:
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    scene.render.film_transparent = transparent
    camera.location = location
    look_at(camera, Vector(target))
    bpy.ops.render.render(write_still=True)


def main() -> None:
    unity_root = Path(bpy.data.filepath).resolve().parent.parent.parent
    output = unity_root / "Artifacts" / "PremiumDisplayCaseBlenderPreview"
    output.mkdir(parents=True, exist_ok=True)
    camera = configure_scene()

    render(camera, output / "blender-assembled-hero.png",
           (0.30, -0.43, 0.26), (0.0, 0.0, 0.0), False)

    offsets = {
        # Unity offsets converted back through U=(-Bx, Bz, By) so the DCC
        # checkpoint and shipping runtime share the same authored spread.
        "Layer_01_FrontPlate": (0.130, -0.090, 0.100),
        "Layer_02_Fasteners": (0.101, -0.070, 0.076),
        "Layer_03_SpacerFrame": (0.071, -0.051, 0.052),
        "Layer_04_Capsule": (0.037, -0.027, 0.027),
        "Layer_05_VelvetInsert": (-0.030, 0.021, -0.021),
        "Layer_06_RearPlate": (-0.064, 0.043, -0.047),
        "Layer_07_OuterTray": (-0.102, 0.069, -0.076),
        "Layer_08_BoxLid": (-0.142, 0.105, 0.105),
    }
    for name, offset in offsets.items():
        bpy.data.objects[name].location += Vector(offset)
    content_anchor = bpy.data.objects.get("ContentSlot_Anchor")
    if content_anchor is not None:
        content_anchor.hide_render = True

    render(camera, output / "blender-exploded-transparent.png",
           (0.46, -0.66, 0.38), (0.005, 0.012, 0.018), True)
    print(f"BLENDER_PREVIEW_DIR={output}")


if __name__ == "__main__":
    main()
