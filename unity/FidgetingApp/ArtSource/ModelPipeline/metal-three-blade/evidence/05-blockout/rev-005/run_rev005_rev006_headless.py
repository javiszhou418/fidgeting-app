"""Headless driver: factory scene -> spinner_rev005.py -> save -> spinner_rev006_rootpocket.py -> save -> Workbench check renders.

    blender -b --factory-startup --python run_rev005_rev006_headless.py -- --out <rev-005 dir>

Renders are Workbench only (the user's D-checklist forbids Cycles at this stage)."""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


def run_script(path: Path):
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    exec(code, {"__name__": "__main__", "__file__": str(path)})


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def workbench_setup(scene, res=1600):
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "SINGLE"
    sh.single_color = (0.75, 0.75, 0.75)
    sh.show_cavity = False
    sh.show_shadows = False
    sh.show_object_outline = True
    sh.show_specular_highlight = True
    scene.display.render_aa = "8"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.18, 0.18, 0.18)
    for o in bpy.data.objects:
        if o.name.startswith("SP_cut_"):
            o.hide_render = True


def render_view(scene, cam, out_path: Path, location, target, ortho=None, lens=50.0):
    cam.location = Vector(location)
    look_at(cam, target)
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = ortho
    else:
        cam.data.lens = lens
    cam.data.clip_start = 0.1
    cam.data.clip_end = 1000.0
    scene.camera = cam
    scene.render.filepath = str(out_path)
    bpy.ops.render.render(write_still=True)
    print("[render]", out_path.name)


def main():
    a = args()
    out = Path(a.out)
    checks = out / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    clear_scene()
    run_script(out / "spinner_rev005.py")
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "geeone-blockout-r005.blend"))
    run_script(out / "spinner_rev006_rootpocket.py")
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "geeone-blockout-r005-rev006-rootpocket.blend"))

    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("CheckCam")
    cam = bpy.data.objects.new("CheckCam", cam_data)
    scene.collection.objects.link(cam)
    workbench_setup(scene)
    body_top = max(v.co.z for v in bpy.data.objects["SP_Body"].data.vertices)
    # D1/D2 顶视正交
    render_view(scene, cam, checks / "top-ortho.png", (0, 0, 200), (0, 0, body_top), ortho=76.0)
    # D3/D4 斜视：相机在盖体上方约 40 mm、朝 90° 叶尖看（模仿 f0132）
    render_view(scene, cam, checks / "oblique-f0132-like.png", (0.0, -6.0, body_top + 40.0), (0.0, 22.0, body_top - 1.0), lens=60.0)
    # 凹坑特写（同一方向，更近）
    render_view(scene, cam, checks / "pocket-closeup.png", (2.0, 4.0, body_top + 22.0), (0.0, 22.5, body_top - 1.5), lens=85.0)
    # D5 外轮廓两条折线：低角度看 330° 叶的外沿
    render_view(scene, cam, checks / "edge-steps-low.png", (70.0, -40.0, body_top + 18.0), (26.0, -15.0, body_top - 3.0), lens=85.0)
    # 侧视正交（阶梯剖影）
    render_view(scene, cam, checks / "side-ortho.png", (0, -200, body_top / 2), (0, 0, body_top / 2), ortho=76.0)
    # 底视（镜像检查：rev-005 机身无底面凹坑，说明书亦未要求）
    render_view(scene, cam, checks / "bottom-ortho.png", (0, 0, -200), (0, 0, 0), ortho=76.0)
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "geeone-blockout-r005-rev006-rootpocket.blend"))
    print("[done] renders in", checks)


main()
