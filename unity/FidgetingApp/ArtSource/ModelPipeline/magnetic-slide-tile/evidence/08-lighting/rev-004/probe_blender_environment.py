#!/usr/bin/env python3
"""Record Blender's equirectangular cardinal-direction convention."""

import json
from pathlib import Path

import bpy
import OpenImageIO as oiio
from mathutils import Vector


HERE = Path(__file__).resolve().parent
scene = bpy.context.scene
scene.render.film_transparent = False
scene.render.resolution_x = 16
scene.render.resolution_y = 16
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = "Raw"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0
scene.render.image_settings.file_format = "OPEN_EXR"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "32"
camera = scene.camera
camera.data.lens = 1000
camera.location = (0, 0, 0)
directions = {
    "blenderPositiveX": (1, 0, 0),
    "blenderNegativeX": (-1, 0, 0),
    "blenderPositiveY": (0, 1, 0),
    "blenderNegativeY": (0, -1, 0),
    "blenderPositiveZ": (0, 0, 1),
    "blenderNegativeZ": (0, 0, -1),
}
samples = {}
for name, direction in directions.items():
    camera.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    output = HERE / f".direction-probe-{name}.exr"
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
    pixels = oiio.ImageInput.open(str(output)).read_image()
    samples[name] = [float(value) for value in pixels[8, 8, :3]]
    output.unlink()
(HERE / "blender-environment-direction-probe.json").write_text(
    json.dumps(samples, indent=2) + "\n", encoding="utf-8"
)
print("DIRECTION_PROBE", json.dumps(samples))
