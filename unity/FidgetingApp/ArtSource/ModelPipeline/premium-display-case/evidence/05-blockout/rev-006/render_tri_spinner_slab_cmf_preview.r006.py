"""CMF material preview for the Gate 05 rev-006 tri-spinner-slab blockout.

    blender -b <blockout.blend> --python tools/blender/render_tri_spinner_slab_cmf_preview.py -- [--no-turntable] [--frames N] [--samples N]

Supplementary review evidence only: it shows the CMF partition, relief depth,
chamfers and bevels under the spec's beauty light rig. It is not the Gate 07
lookdev deliverable (no vertex channels, decals, soft focus or calibration
report). Materials come from `contract.materials` by `cmf_zone_id`; light
positions come from `contract.lighting.beauty` (hero-camera-local, scaled by
the assembled bbox diagonal). Exposure is auto-calibrated so the case's mean
luminance lands near mid grey, then written into the scene.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else 96
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 128
STILLS_ONLY = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else None

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-006/modeling-contract.json"
OUT_DIR = PIPELINE / "evidence/05-blockout/rev-006"
# fresh, unique frame directory per run; nothing is ever deleted from /tmp
TURNTABLE_DIR = Path(f"/tmp/tri-spinner-slab-g05-r006-cmf-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
MM = 0.001

CONTRACT = json.loads(CONTRACT_PATH.read_text())
CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
MATERIALS = {m["slot"]: m for m in CONTRACT["materials"]["materials"]}


def srgb_hex_to_linear(hex_str: str) -> tuple[float, float, float, float]:
    h = hex_str.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def mid(rng):
    return (rng[0] + rng[1]) / 2 if isinstance(rng, (list, tuple)) else rng


def principled(name: str) -> tuple[bpy.types.Material, bpy.types.ShaderNodeBsdfPrincipled, bpy.types.NodeTree]:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    return mat, bsdf, nt


def make_materials() -> dict[int, bpy.types.Material]:
    mats = {}

    m = MATERIALS[1]["blender"]
    mat, b, nt = principled("MAT_PDC_CLEAR_CRYSTAL")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = m["ior"]
    b.inputs["Coat Weight"].default_value = m["coat_weight"]
    b.inputs["Coat Roughness"].default_value = m["coat_roughness"]
    mats[1] = mat

    m = MATERIALS[2]["blender"]
    mat, b, nt = principled("MAT_PDC_SMOKE_LINER")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    b.inputs["Transmission Weight"].default_value = mid(m["transmission_weight_range"])
    b.inputs["IOR"].default_value = m["ior"]
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (0.55, 0.48, 0.66, 1.0)
    vol.inputs["Density"].default_value = 900.0
    nt.links.new(vol.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    mats[2] = mat

    m = MATERIALS[3]["blender"]
    mat, b, nt = principled("MAT_PDC_MICROBLAST")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9000.0
    noise.inputs["Detail"].default_value = 3.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.00002
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    mats[3] = mat

    m = MATERIALS[4]["blender"]
    mat, b, nt = principled("MAT_PDC_GRAPHITE")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = m["metallic"]
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    mats[4] = mat

    m = MATERIALS[5]["blender_reference"]
    mat, b, nt = principled("MAT_PDC_STEEL_SATIN")
    b.inputs["Base Color"].default_value = (*m["base_color_registered"], 1.0)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = m["roughness"]
    b.inputs["Anisotropic"].default_value = mid(m["anisotropy_start_range"])
    b.inputs["Anisotropic Rotation"].default_value = 0.25
    mats[5] = mat

    m = MATERIALS[6]["blender"]
    mat, b, nt = principled("MAT_PDC_SMOKED_MIRROR")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    mats[6] = mat

    m = MATERIALS[7]["blender"]
    mat, b, nt = principled("MAT_PDC_CHAMPAGNE_GOLD")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    b.inputs["Anisotropic"].default_value = mid(m["anisotropy_range"])
    mats[7] = mat

    mat, b, nt = principled("MAT_PDC_REVIEW_SPINNER_TITANIUM")
    b.inputs["Base Color"].default_value = (0.56, 0.57, 0.58, 1.0)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["Anisotropic"].default_value = 0.4
    mats[0] = mat

    mat, b, nt = principled("MAT_PDC_PREVIEW_FLOOR")
    b.inputs["Base Color"].default_value = (0.004, 0.004, 0.005, 1.0)
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Specular IOR Level"].default_value = 0.6
    mats["floor"] = mat
    return mats


def assign_materials(mats):
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        zone = int(ob.get("cmf_zone_id", -1))
        if ob.name.startswith("CUT_PDC_"):
            continue
        if zone in mats:
            ob.data.materials.clear()
            ob.data.materials.append(mats[zone])
            if zone == 1:
                ob.visible_shadow = True


def bounds(objects):
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return lo, hi


def kelvin_to_rgb(k: float) -> tuple[float, float, float]:
    t = k / 100.0
    r = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    return tuple(max(0.0, min(255.0, v)) / 255.0 for v in (r, g, b))


def build_lights(scene, hero_cam, target, diag):
    rig = CONTRACT["lighting"]["beauty"]
    col = bpy.data.collections.get("COL_PDC_LIGHTS_BEAUTY")
    cam_pos = hero_cam.matrix_world.translation
    right = hero_cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    up = hero_cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    toward = (target - cam_pos).normalized()
    lights = []
    for spec in rig["lights"]:
        if spec.get("optional"):
            power = spec["relative_power_max"]          # coloured rims at their spec maximum (<= 8 % of white energy)
        elif "relative_power_range" in spec:
            power = spec["relative_power_range"][1]     # strips at range max: the crystal edge must read
        else:
            power = spec["relative_power"]
        data = bpy.data.lights.new(spec["id"], "AREA")
        data.shape = "RECTANGLE"
        data.size, data.size_y = spec["size_b"][0] * diag, spec["size_b"][1] * diag
        data.color = srgb_hex_to_linear(spec["color_srgb_hex"])[:3] if "color_srgb_hex" in spec else kelvin_to_rgb(spec.get("temperature_k", 5600))
        data.energy = 1.0 * power           # scaled after calibration
        data["relative_power"] = power
        ob = bpy.data.objects.new(spec["id"], data)
        col.objects.link(ob)
        # target-anchored, camera-local axes: +x camera right, +y toward the camera, +z camera up
        x, y, z = spec["position_b"]
        ob.location = target + right * x * diag - toward * y * diag + up * z * diag
        d = (target - ob.location).normalized()
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        lights.append(ob)
    return lights


def configure_cycles(scene):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = dev.type in ("METAL", "CPU")
        scene.cycles.device = "GPU"
    except Exception as exc:  # noqa: BLE001
        print("GPU setup failed, CPU fallback:", exc)
        scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.02
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 12
    scene.cycles.transmission_bounces = 12
    scene.cycles.transparent_max_bounces = 12
    scene.cycles.glossy_bounces = 6
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.cycles.blur_glossy = 0.5
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("WORLD_PDC_BEAUTY")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = srgb_hex_to_linear(CONTRACT["lighting"]["beauty"]["world_srgb_hex"])
    bg.inputs["Strength"].default_value = mid(CONTRACT["lighting"]["beauty"]["world_strength_range"]) * 100
    scene.world = world
    scene.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_frame_range",
                 "use_stamp_memory", "use_stamp_hostname", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene",
                 "use_stamp_marker", "use_stamp_filename", "use_stamp_sequencer_strip"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.use_stamp_note = True
    scene.render.stamp_note_text = (f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 05 r006 CMF PREVIEW (indicative; Gate 07 lookdev pending) | "
                                    f"contract {CONTRACT_SHA[:12]} | Cycles {SAMPLES} spp")
    scene.render.stamp_font_size = 22
    scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0)
    scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def render(scene, cam, path: Path, resolution):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def calibrate(scene, cam, lights, target_p97=0.80, passes=2):
    """Every case surface is metallic, so the camera mostly sees the light
    sources themselves. Powers are set proportional to relative_power * area
    (equal relative radiance per light), then scaled together so the 97th
    percentile display luminance of object pixels in a low-res hero frame lands
    at target_p97: the brightest steel just below clipping, graphite near black."""
    for ob in lights:
        ob.data.energy = 5.0 * ob.data["relative_power"] * ob.data.size * ob.data.size_y
    tmp = Path("/tmp/pdc_cmf_calib.png")
    saved = (scene.cycles.samples, scene.render.use_stamp)
    scene.cycles.samples, scene.render.use_stamp = 24, False
    history = []
    for _ in range(passes):
        render(scene, cam, tmp, (320, 213))
        img = bpy.data.images.load(str(tmp))
        px = list(img.pixels)
        w, h = img.size
        lums = []
        for y in range(int(h * 0.1), int(h * 0.9)):
            for x in range(int(w * 0.25), int(w * 0.75)):
                i = (y * w + x) * 4
                l = 0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2]
                if l > 0.004:
                    lums.append(l)
        bpy.data.images.remove(img)
        lums.sort()
        p97 = lums[int(len(lums) * 0.97)] if lums else 0.01
        factor = max(0.05, min(50.0, (target_p97 / max(p97, 1e-4)) ** 2.2))
        for ob in lights:
            ob.data.energy *= factor
        history.append({"p97": round(p97, 4), "factor": round(factor, 3)})
    scene.cycles.samples, scene.render.use_stamp = saved
    return {"target_p97_display": target_p97, "passes": history,
            "energies_w": {ob.name: round(ob.data.energy, 4) for ob in lights}}


def main():
    scene = bpy.context.scene
    mats = make_materials()
    assign_materials(mats)
    case = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO_PDC_")]
    lo, hi = bounds(case)
    diag = (hi - lo).length
    target = (lo + hi) / 2
    hero = bpy.data.objects["CAM_PDC_HERO"]

    # dark glossy floor under the bottom edge
    bpy.ops.mesh.primitive_plane_add(size=diag * 12, location=(target.x, target.y, lo.z - 0.3 * MM))
    floor = bpy.context.active_object
    floor.name = "GEO_PDC_PREVIEW_FLOOR"
    floor.data.materials.append(mats["floor"])
    floor["export_role"] = "preview-only"
    bpy.data.collections["COL_PDC_LOOKDEV"].objects.link(floor)
    scene.collection.objects.unlink(floor)

    configure_cycles(scene)
    lights = build_lights(scene, hero, target, diag)
    calib = calibrate(scene, hero, lights)
    scene["cmf_preview_calibration"] = json.dumps(calib)

    stills = {
        "cmf-preview-hero.png": ("CAM_PDC_HERO", (2048, 1365)),
        "cmf-preview-front.png": ("CAM_PDC_FRONT", (2048, 2048)),
        "cmf-preview-low-oblique.png": ("CAM_PDC_LOW_OBLIQUE", (2048, 1365)),
        "cmf-preview-corner-macro.png": ("CAM_PDC_CORNER_MACRO", (2048, 1365)),
        "cmf-preview-pocket-rim-macro.png": ("CAM_PDC_POCKET_RIM_MACRO", (2048, 1365)),
    }
    for filename, (cam_name, res) in stills.items():
        if STILLS_ONLY is not None and filename not in STILLS_ONLY:
            continue
        render(scene, bpy.data.objects[cam_name], OUT_DIR / filename, res)

    if RENDER_TURNTABLE:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=False)     # fresh directory; never delete frames
        presentation = bpy.data.objects["ROOT_PDC_PRESENTATION"]
        saved = scene.cycles.samples
        scene.cycles.samples = max(32, SAMPLES // 2)
        for i in range(FRAMES):
            presentation.rotation_euler = (0.0, 0.0, math.radians(360.0 * i / FRAMES))
            bpy.context.view_layer.update()
            render(scene, hero, TURNTABLE_DIR / f"frame_{i:04d}.png", (1280, 852))
        presentation.rotation_euler = (0.0, 0.0, 0.0)
        scene.cycles.samples = saved

    report = {"contract_sha256": CONTRACT_SHA, "engine": "CYCLES", "samples": SAMPLES, "calibration": calib,
              "materials_by_zone": {str(k): v.name for k, v in mats.items()},
              "lights": [{"name": l.name, "energy_w": round(l.data.energy, 2), "size_m": [round(l.data.size, 4), round(l.data.size_y, 4)],
                          "location_m": [round(v, 4) for v in l.location]} for l in lights],
              "stills": list(stills), "turntable_frames": FRAMES if RENDER_TURNTABLE else 0,
              "status": "supplementary CMF preview; not Gate 07 lookdev"}
    (OUT_DIR / "cmf-preview-report.json").write_text(json.dumps(report, indent=2) + "\n")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "tri-spinner-slab-cmf-preview-r006.blend"))
    print("CMF_PREVIEW_RESULT=" + json.dumps(report))


main()
