"""Gate 07 material + Gate 08 lighting + Gate 09 environment lookdev · GEEONE 龙鳞三叶 (on geometry rev-007).
rev-004 (user 2026-09-07 22:51): materials / lights / environment unchanged from rev-003; re-rendered on geometry rev-007 (dish 8°, taller skirt rows).
rev-003 (user 2026-09-07 19:42 '切分成 14 片的细节又丢了…应该是向内凹一点的'): disc anisotropy 0.7 -> 0.4 and the turning-mark bump softened so the
14 planar sectors of the 5° concave dish read as slices (tonal steps between neighbours) instead of being washed out by the sunburst
highlight; new "disc-macro" view reproduces the user's reference screenshot angle (near top-down, slightly oblique).

    blender -b <geeone-geometry-r006.blend> --python lookdev_geeone.py -- --out <07-material/rev-003 dir> [--turntable 36]

Material (Gate 07): satin steel everywhere (metallic 1, roughness 0.36, base 0.78/0.79/0.80), turned disc = anisotropic radial
0.4 + fine concentric bump (roughness 0.30), hub seat = dark bearing steel. Anisotropy ONLY on the disc (user 2026-09-05).
Lighting (Gate 08): three area lights (key upper-left, fill right, thin top strip for facet sparkle) + dark gradient world.
Environment (Gate 09): matte dark studio floor with soft contact shadow, product floating 2 mm above.
Cycles, AgX, GPU if available. Turntable frames -> ffmpeg by the caller.
"""
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
    p.add_argument("--turntable", type=int, default=0)
    p.add_argument("--samples", type=int, default=96)
    p.add_argument("--res", type=int, default=1400)
    p.add_argument("--views", default="")  # comma list to render a subset (e.g. disc-macro)
    p.add_argument("--blend-name", default="geeone-lookdev-r004.blend")
    return p.parse_args(argv)


A = args()
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
S = 42.5  # mm per R (85 mm provisional)


# ---------------------------------------------------------------- materials (Gate 07)
def principled(name, base, rough, metallic=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*base, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    nt.links.new(b.outputs[0], out.inputs[0])
    return m, nt, b


def mat_satin():
    m, nt, b = principled("M_Steel_Satin", (0.78, 0.79, 0.80), 0.36)
    return m


def mat_disc_turned():
    """Anisotropic radial satin with fine concentric turning marks (disc only)."""
    m, nt, b = principled("M_Disc_Turned", (0.80, 0.81, 0.82), 0.30)
    if "Anisotropic" in b.inputs:
        b.inputs["Anisotropic"].default_value = 0.4  # rev-003: 0.7 hid the 14 sector facets
    tan = nt.nodes.new("ShaderNodeTangent")
    tan.direction_type = "RADIAL"
    tan.axis = "Z"
    if "Tangent" in b.inputs:
        nt.links.new(tan.outputs[0], b.inputs["Tangent"])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.rings_direction = "Z"
    wave.inputs["Scale"].default_value = 2 * math.pi / (10.0 * 0.12)  # 0.12 mm ring pitch
    wave.inputs["Distortion"].default_value = 0.0  # clean concentric turning rings
    wave.inputs["Detail"].default_value = 1.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12  # rev-003: softer so facet tone dominates
    bump.inputs["Distance"].default_value = 0.004
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m


def mat_hub_dark():
    m, nt, b = principled("M_Hub_Dark", (0.06, 0.06, 0.065), 0.45)
    return m


def mat_floor():
    m, nt, b = principled("M_Studio_Floor", (0.035, 0.035, 0.038), 0.85, metallic=0.0)
    return m


def assign_materials():
    satin, disc, dark = mat_satin(), mat_disc_turned(), mat_hub_dark()
    body = bpy.data.objects["Rotor_Body"]
    body.data.materials.clear()
    body.data.materials.append(satin)
    for name in ("Cap_Top", "Cap_Bottom"):
        cap = bpy.data.objects[name]
        me = cap.data
        me.materials.clear()
        me.materials.append(satin)
        me.materials.append(disc)
        for p in me.polygons:  # disc sectors = triangles touching the centre vertex
            p.material_index = 1 if (len(p.vertices) == 3 and any(abs(me.vertices[vi].co.x) < 1e-6 and abs(me.vertices[vi].co.y) < 1e-6 for vi in p.vertices)) else 0
    for name in ("Hub_Seat_Top", "Hub_Seat_Bottom"):
        hub = bpy.data.objects[name]
        hub.data.materials.clear()
        hub.data.materials.append(dark)


# ---------------------------------------------------------------- lighting (Gate 08) + environment (Gate 09)
def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def area(name, loc, target, size, energy, color=(1.0, 1.0, 1.0), shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = shape
    ld.size = size
    if size_y:
        ld.size_y = size_y
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(loc)
    look_at(ob, target)
    return ob


def setup_lights_and_env():
    scene = bpy.context.scene
    for o in list(bpy.data.objects):
        if o.type == "LIGHT" or o.name.startswith("Studio_"):
            bpy.data.objects.remove(o, do_unlink=True)
    R = S
    # scene units are mm (1 BU = 1 mm displayed) but Cycles treats 1 BU as 1 m for light falloff -> scale powers by 1e6
    K = 250.0
    area("Key_Soft", (-1.6 * R, -1.4 * R, 2.6 * R), (0, 0, 0), 2.4 * R, 1800 * K, (1.0, 0.97, 0.93), size_y=1.6 * R)  # Gate 08 key
    area("Fill_Cool", (2.4 * R, -0.6 * R, 1.4 * R), (0, 0, 0), 3.0 * R, 500 * K, (0.90, 0.94, 1.0), size_y=2.0 * R)
    area("Rim_Strip", (0.6 * R, 2.4 * R, 1.9 * R), (0, 0, 0.1 * R), 3.5 * R, 900 * K, (1.0, 1.0, 1.0), size_y=0.25 * R)  # thin strip -> facet sparkle
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = "LINEAR"
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.035, 0.04, 1)
    ramp.color_ramp.elements[1].color = (0.30, 0.31, 0.34, 1)  # bright soft top so satin steel has something to reflect
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0.0, math.radians(-90.0), 0.0)
    nt.links.new(coord.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], grad.inputs["Vector"])
    nt.links.new(grad.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs[0])
    # Gate 09 environment: matte floor 2 mm under the bottom cap, soft contact shadow
    bpy.ops.mesh.primitive_plane_add(size=14 * R, location=(0, 0, -(0.085 + 0.14) * R - 2.0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    floor.data.materials.append(mat_floor())
    floor.is_shadow_catcher = False


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons.get("cycles")
    if prefs:
        try:
            prefs.preferences.compute_device_type = "METAL"
            prefs.preferences.get_devices()
            for d in prefs.preferences.devices:
                d.use = True
            scene.cycles.device = "GPU"
        except Exception as exc:  # noqa: BLE001
            print("[lookdev] GPU setup failed, CPU:", exc)
    scene.cycles.samples = A.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = A.res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Base Contrast"
    scene.view_settings.exposure = 0.0


def render_views():
    scene = bpy.context.scene
    cam = bpy.data.objects.get("ReviewCam") or bpy.data.objects.new("ReviewCam", bpy.data.cameras.new("ReviewCam"))
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    scene.camera = cam
    R = S
    body_top = 0.085 * R
    views = {
        "hero": ((1.2 * R, -1.6 * R, 1.5 * R), (0, 0, 0.3 * body_top), None, 50.0),
        "top-ortho": ((0, 0, 300), (0, 0, body_top), 2.3 * R, None),
        "low": ((0.3 * R, -2.6 * R, 0.45 * R), (0, 0, 0.1 * body_top), None, 60.0),
        "blade-macro-f0132": ((0.0, -0.15 * R, 1.35 * R), (0.0, 0.62 * R, body_top * 0.9), None, 70.0),
        "cap-macro": ((0.75 * R, -1.15 * R, 0.62 * R), (0.12 * R, -0.05 * R, body_top * 1.6), None, 85.0),
        # user reference screenshot angle (disc-14 crop): ≈22° off the vertical, cap fills ≈80 % of the frame
        "disc-macro": ((0.35 * R, -1.05 * R, 2.65 * R), (0.0, 0.0, body_top * 1.6), None, 85.0),
        "edge-macro": ((1.3 * R, -0.9 * R, 0.55 * R), (0.55 * R, -0.35 * R, body_top * 0.6), None, 85.0),
    }
    wanted = [v for v in A.views.split(",") if v]
    for name, (loc, tgt, ortho, lens) in views.items():
        if wanted and name not in wanted:
            continue
        cam.location = Vector(loc)
        look_at(cam, tgt)
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        else:
            cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 2000
        scene.render.filepath = str(OUT / "renders" / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", name)
    if A.turntable:
        scene.render.resolution_x = scene.render.resolution_y = 720
        scene.cycles.samples = max(32, A.samples // 2)
        cam.data.type = "PERSP"
        cam.data.lens = 50.0
        for i in range(A.turntable):
            a = 2 * math.pi * i / A.turntable
            cam.location = Vector((2.0 * R * math.cos(a), 2.0 * R * math.sin(a), 1.25 * R))
            look_at(cam, (0, 0, 0.2 * body_top))
            scene.render.filepath = str(OUT / "turntable" / f"frame_{i:03d}.png")
            bpy.ops.render.render(write_still=True)
        print("[render] turntable", A.turntable, "frames")


def main():
    (OUT / "renders").mkdir(exist_ok=True)
    (OUT / "turntable").mkdir(exist_ok=True)
    assign_materials()
    setup_lights_and_env()
    setup_render()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / A.blend_name))
    render_views()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / A.blend_name))
    print("[lookdev] done")


main()
