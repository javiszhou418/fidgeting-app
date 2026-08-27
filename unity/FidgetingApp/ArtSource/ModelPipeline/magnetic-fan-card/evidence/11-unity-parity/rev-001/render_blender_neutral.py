"""Render the exported FBX with a fixed camera for Unity parity."""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
FBX = (
    HERE.parents[1] / "10-export/rev-001/"
    "magnetic-fan-card.fbx"
)
OUTPUT = HERE / "blender-neutral.png"
RECIPE = HERE / "neutral-camera-recipe.json"
REPORT = HERE / "blender-neutral-report.json"
WIDTH = 1179
HEIGHT = 654


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector, Vector]:
    points = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
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
    return minimum, maximum, (minimum + maximum) / 2


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y").to_euler()


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX))
    scene = bpy.context.scene
    objects = list(scene.objects)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    minimum, maximum, center = bounds(meshes)
    extent = maximum - minimum
    span = max(extent.x, extent.y)

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.filepath = str(OUTPUT)
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "OBJECT"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.show_specular_highlight = True
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.025, 0.028, 0.032)
    for obj in meshes:
        obj.color = (0.60, 0.57, 0.51, 1.0)

    camera_data = bpy.data.cameras.new("CAM_UnityParity")
    camera = bpy.data.objects.new("CAM_UnityParity", camera_data)
    scene.collection.objects.link(camera)
    camera_data.lens = 55.0
    camera_data.sensor_width = 36.0
    camera_data.sensor_fit = "HORIZONTAL"
    camera.location = center + Vector((
        span * 1.20,
        -span * 1.50,
        span * 1.10,
    ))
    aim(camera, center)
    scene.camera = camera
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)

    recipe = {
        "viewId": "hero",
        "resolution": [WIDTH, HEIGHT],
        "camera": {
            "position": [round(value, 9) for value in camera.location],
            "lookAt": [round(value, 9) for value in center],
            "lensMm": 55.0,
            "sensorWidthMm": 36.0,
            "verticalFovDegrees": round(
                math.degrees(2.0 * math.atan(
                    math.tan(camera_data.angle_x / 2.0)
                    / (WIDTH / HEIGHT))),
                7),
            "nearClip": 0.001,
            "farClip": 10.0,
        },
        "backgroundLinearRgb": [0.025, 0.028, 0.032],
        "neutralObjectColor": [0.60, 0.57, 0.51, 1.0],
        "sourceBounds": {
            "minimum": [round(value, 9) for value in minimum],
            "maximum": [round(value, 9) for value in maximum],
            "extent": [round(value, 9) for value in extent],
            "center": [round(value, 9) for value in center],
        },
    }
    RECIPE.write_text(
        json.dumps(recipe, indent=2) + "\n",
        encoding="utf-8")
    REPORT.write_text(
        json.dumps({
            "fbx": str(FBX),
            "objects": len(objects),
            "meshObjects": len(meshes),
            "triangles": sum(
                len(polygon.vertices) - 2
                for obj in meshes
                for polygon in obj.data.polygons
            ),
            "materials": sorted({
                material.name
                for obj in meshes
                for material in obj.data.materials
                if material is not None
            }),
            "root": "MagneticFanCard_Root",
            "cards": {
                name: bpy.data.objects[name].parent.name
                for name in ("BottomCard", "MiddleCard", "TopCard")
            },
            "cameraRecipe": RECIPE.name,
            "output": OUTPUT.name,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
