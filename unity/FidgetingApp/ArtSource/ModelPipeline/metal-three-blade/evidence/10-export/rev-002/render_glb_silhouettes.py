"""Flat white-on-black silhouettes of the exported GLB (Blender Workbench, FLAT single colour) with the Gate 11 camera recipe
(orthographic top 2.3 R wide; hero from (1.2R, -1.6R, 1.5R) looking at (0, 0, 0.3 * body_top), 50 mm).

    blender -b --python render_glb_silhouettes.py -- --glb <geeone-tri-spinner.glb> --out <review dir>
"""
import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--glb", required=True)
p.add_argument("--out", required=True)
A = p.parse_args(argv)
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
R = 0.0425

bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.import_scene.gltf(filepath=A.glb)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = 1200
sh = scene.display.shading
sh.light = "FLAT"
sh.color_type = "SINGLE"
sh.single_color = (1.0, 1.0, 1.0)
sh.show_cavity = False
sh.show_shadows = False
sh.show_object_outline = False
scene.display.render_aa = "8"
scene.world = scene.world or bpy.data.worlds.new("World")
scene.world.color = (0.0, 0.0, 0.0)
scene.view_settings.view_transform = "Standard"
cam = bpy.data.objects.new("SilCam", bpy.data.cameras.new("SilCam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.clip_start = 0.001
cam.data.clip_end = 10


def look_at(target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


cam.data.type = "ORTHO"
cam.data.ortho_scale = 2.3 * R
cam.location = Vector((0, 0, 1.0))
look_at((0, 0, 0))
scene.render.filepath = str(OUT / "glb-top-ortho-silhouette.png")
bpy.ops.render.render(write_still=True)
cam.data.type = "PERSP"
cam.data.lens = 50.0
cam.location = Vector((1.2 * R, -1.6 * R, 1.5 * R))
look_at((0, 0, 0.3 * 0.085 * R))
scene.render.filepath = str(OUT / "glb-hero-silhouette.png")
bpy.ops.render.render(write_still=True)
print("[g10] silhouettes written to", OUT)
