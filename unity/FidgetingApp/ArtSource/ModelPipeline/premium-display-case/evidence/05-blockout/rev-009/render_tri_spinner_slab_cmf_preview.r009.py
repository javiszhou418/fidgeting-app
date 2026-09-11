"""CMF material preview for the Gate 05 rev-009 tri-spinner-slab blockout.

rev-009: wings retired (contract rev-009). Soft-focus study options added so the
user can see the effect: --soft-level mid|max (contract ranges) and --soft-gain
K / --soft-threshold lo,hi for an out-of-contract demo (always labelled DEMO).

rev-008: CMF scheme A preview overrides (user decision 2026-09-10): brushed
steel flats, bright mirror bevels/lip/wings, dark sandblasted field, piano-black
plates. Overrides are flagged in the report; contract material values remain
the Gate 07 authority.

rev-007: `--no-review-bright` disables the review brightness boost (neutral
grey world + soft top fill + p97 0.86). The boost is a review aid requested by
the user on 2026-09-10 12:22; the contract beauty rig itself is unchanged.

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
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-009/modeling-contract.json"
OUT_DIR = PIPELINE / "evidence/05-blockout/rev-009"
# fresh, unique frame directory per run; nothing is ever deleted from /tmp
TURNTABLE_DIR = Path(f"/tmp/tri-spinner-slab-g05-r009-cmf-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
SCHEME_A = "--no-scheme-a" not in ARGS
# --- rarity tier variations (user request 2026-09-10 14:33). Accent metal follows the shipping
# PremiumDisplayCaseFoilTier order Steel / Copper / Silver / Gold (Assets/_DisplayCase/Runtime/PremiumDisplayCaseLabelPlate.cs
# foilByTier) mapped onto GachaRarity Standard / Refined / Signature / Heirloom. Liner/seam tint follows FDB-DSP-014
# (low cold silver, mid blue-titanium/champagne, high smoke-purple black chrome). Body zones stay constant unless --bold.
TIER = ARGS[ARGS.index("--tier") + 1] if "--tier" in ARGS else None
BOLD = "--bold" in ARGS                       # tier metal also on bezels (5) and mirrors (6): needs FDB-DSP-014 supersession
MEDIUM = "--medium" in ARGS                   # tier metal on the polished parts only (6: lip, bevels, wings, divider) + accents; bezels stay steel
SOFT_FOCUS = "--soft-focus" in ARGS           # highlight-only soft focus per contract.soft_focus, hero only, writes -soft twin
SOFT_LEVEL = ARGS[ARGS.index("--soft-level") + 1] if "--soft-level" in ARGS else "mid"      # mid | max of the contract ranges
SOFT_GAIN = float(ARGS[ARGS.index("--soft-gain") + 1]) if "--soft-gain" in ARGS else 1.0    # > 1 = out-of-contract DEMO
SOFT_THRESHOLD = ([float(v) for v in ARGS[ARGS.index("--soft-threshold") + 1].split(",")] if "--soft-threshold" in ARGS else None)
SOFT_RADIUS_SCALE = float(ARGS[ARGS.index("--soft-radius-scale") + 1]) if "--soft-radius-scale" in ARGS else 1.0   # > 1 = DEMO
SOFT_DEMO = SOFT_GAIN != 1.0 or SOFT_THRESHOLD is not None or SOFT_RADIUS_SCALE != 1.0
SOFT_TAG = ("" if SOFT_LEVEL == "mid" else "-max") + (f"-demo-gain{SOFT_GAIN:g}-r{SOFT_RADIUS_SCALE:g}" if SOFT_DEMO else "")
OUT_SUFFIX = ("-tier-" + TIER + ("-bold" if BOLD else "-medium" if MEDIUM else "")) if TIER else ""
TIERS = {
    #            accent (zone 7) sRGB 0-1 from foilByTier,  roughness, liner/seam tint (zone 2 base + absorption), rarity
    "steel":  {"rarity": "Standard",  "accent": (0.62, 0.65, 0.69), "accent_rough": 0.30, "liner": (0.86, 0.88, 0.92), "absorb": (0.50, 0.55, 0.62)},
    "copper": {"rarity": "Refined",   "accent": (0.80, 0.50, 0.30), "accent_rough": 0.26, "liner": (0.93, 0.87, 0.82), "absorb": (0.62, 0.48, 0.40)},
    "silver": {"rarity": "Signature", "accent": (0.88, 0.90, 0.93), "accent_rough": 0.18, "liner": (0.90, 0.92, 0.96), "absorb": (0.58, 0.64, 0.74)},
    "gold":   {"rarity": "Heirloom",  "accent": (0.96, 0.78, 0.38), "accent_rough": 0.22, "liner": (0.90, 0.86, 0.94), "absorb": (0.52, 0.42, 0.64)},
    # alternative for Signature: FDB-DSP-014 names blue-titanium for the middle tier; not in PremiumDisplayCaseFoilTier
    "titanium": {"rarity": "Signature (alt: blue titanium)", "accent": (0.58, 0.66, 0.80), "accent_rough": 0.24, "liner": (0.84, 0.88, 0.96), "absorb": (0.42, 0.52, 0.72)},
}
if TIER is not None and TIER not in TIERS:
    raise SystemExit(f"unknown --tier {TIER}; choose {sorted(TIERS)}")
SCHEME_A_OVERRIDES = {
    "3": {"base_color_srgb_hex": "#5C6266", "roughness": 0.55, "bump_strength": 0.6, "intent": "dark sandblast, recessed field"},
    "4": {"roughness": 0.12, "coat_weight": 0.35, "coat_roughness": 0.05, "intent": "piano-black gloss plates"},
    "5": {"roughness": 0.30, "anisotropic": 0.8, "anisotropic_rotation": 0.0, "intent": "directional brushed steel flats"},
    "6": {"base_color_srgb_hex": "#C9D0D6", "roughness": 0.04, "intent": "bright mirror polish: bevels, lip, wings, divider"},
}
REVIEW_BRIGHT = "--no-review-bright" not in ARGS
REVIEW_WORLD_STRENGTH = 0.05     # neutral grey ambient so recessed microblast/graphite read in review
REVIEW_TOP_FILL_POWER = 0.45     # relative to the soft key; large overhead card
REVIEW_TARGET_P97 = 0.86
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
    if TIER:
        b.inputs["Base Color"].default_value = (*[c ** 2.2 for c in TIERS[TIER]["liner"]], 1.0)
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    b.inputs["Transmission Weight"].default_value = mid(m["transmission_weight_range"])
    b.inputs["IOR"].default_value = m["ior"]
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (*TIERS[TIER]["absorb"], 1.0) if TIER else (0.55, 0.48, 0.66, 1.0)
    vol.inputs["Density"].default_value = 900.0
    nt.links.new(vol.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    mats[2] = mat

    m = MATERIALS[3]["blender"]
    mat, b, nt = principled("MAT_PDC_MICROBLAST")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    if SCHEME_A:
        b.inputs["Base Color"].default_value = srgb_hex_to_linear(SCHEME_A_OVERRIDES["3"]["base_color_srgb_hex"])
        b.inputs["Roughness"].default_value = SCHEME_A_OVERRIDES["3"]["roughness"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9000.0
    noise.inputs["Detail"].default_value = 3.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = SCHEME_A_OVERRIDES["3"]["bump_strength"] if SCHEME_A else 0.35
    bump.inputs["Distance"].default_value = 0.00002
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    mats[3] = mat

    m = MATERIALS[4]["blender"]
    mat, b, nt = principled("MAT_PDC_GRAPHITE")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = m["metallic"]
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    if SCHEME_A:
        b.inputs["Roughness"].default_value = SCHEME_A_OVERRIDES["4"]["roughness"]
        b.inputs["Coat Weight"].default_value = SCHEME_A_OVERRIDES["4"]["coat_weight"]
        b.inputs["Coat Roughness"].default_value = SCHEME_A_OVERRIDES["4"]["coat_roughness"]
    mats[4] = mat

    m = MATERIALS[5]["blender_reference"]
    mat, b, nt = principled("MAT_PDC_STEEL_SATIN")
    b.inputs["Base Color"].default_value = (*m["base_color_registered"], 1.0)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = m["roughness"]
    b.inputs["Anisotropic"].default_value = mid(m["anisotropy_start_range"])
    b.inputs["Anisotropic Rotation"].default_value = 0.25
    if SCHEME_A:
        b.inputs["Roughness"].default_value = SCHEME_A_OVERRIDES["5"]["roughness"]
        b.inputs["Anisotropic"].default_value = SCHEME_A_OVERRIDES["5"]["anisotropic"]
        b.inputs["Anisotropic Rotation"].default_value = SCHEME_A_OVERRIDES["5"]["anisotropic_rotation"]
    if TIER and BOLD:
        b.inputs["Base Color"].default_value = (*[c ** 2.2 for c in TIERS[TIER]["accent"]], 1.0)
    mats[5] = mat

    m = MATERIALS[6]["blender"]
    mat, b, nt = principled("MAT_PDC_SMOKED_MIRROR")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    if SCHEME_A:
        b.inputs["Base Color"].default_value = srgb_hex_to_linear(SCHEME_A_OVERRIDES["6"]["base_color_srgb_hex"])
        b.inputs["Roughness"].default_value = SCHEME_A_OVERRIDES["6"]["roughness"]
    if TIER and (BOLD or MEDIUM):
        b.inputs["Base Color"].default_value = (*[min(1.0, c * 1.05) ** 2.2 for c in TIERS[TIER]["accent"]], 1.0)
    mats[6] = mat

    m = MATERIALS[7]["blender"]
    mat, b, nt = principled("MAT_PDC_CHAMPAGNE_GOLD" if not TIER else f"MAT_PDC_TIER_ACCENT_{TIER.upper()}")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m["base_color_srgb_hex"])
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = mid(m["roughness_range"])
    if TIER:
        b.inputs["Base Color"].default_value = (*[c ** 2.2 for c in TIERS[TIER]["accent"]], 1.0)
        b.inputs["Roughness"].default_value = TIERS[TIER]["accent_rough"]
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
    if REVIEW_BRIGHT:
        # review aid only (user 2026-09-10 12:22: "光照还是有点黑…环境光射得更亮一些"): a large soft card above the case
        data = bpy.data.lights.new("LGT_PDC_REVIEW_TOP_FILL", "AREA")
        data.shape = "RECTANGLE"
        data.size, data.size_y = 2.2 * diag, 2.2 * diag
        data.color = kelvin_to_rgb(5600)
        data["relative_power"] = REVIEW_TOP_FILL_POWER
        data["review_only"] = True
        ob = bpy.data.objects.new("LGT_PDC_REVIEW_TOP_FILL", data)
        col.objects.link(ob)
        ob.location = target + Vector((0, 0, 1)) * 1.6 * diag - toward * 0.4 * diag
        ob.rotation_euler = (target - ob.location).normalized().to_track_quat("-Z", "Y").to_euler()
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
    if REVIEW_BRIGHT:
        bg.inputs["Color"].default_value = (0.62, 0.64, 0.68, 1.0)
        bg.inputs["Strength"].default_value = REVIEW_WORLD_STRENGTH
    else:
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
    scene.render.stamp_note_text = (f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 05 r009 CMF PREVIEW (indicative; Gate 07 lookdev pending{', REVIEW-BRIGHT' if REVIEW_BRIGHT else ''}{', SCHEME-A' if SCHEME_A else ''}{f', TIER {TIER.upper()} = {TIERS[TIER]["rarity"]}' + (' BOLD' if BOLD else ' MEDIUM' if MEDIUM else ' NARROW') if TIER else ''}{' | SOFT-FOCUS DEMO OUT OF CONTRACT' if SOFT_FOCUS and SOFT_DEMO else ''}) | "
                                    f"contract {CONTRACT_SHA[:12]} | Cycles {SAMPLES} spp")
    scene.render.stamp_font_size = 22
    scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0)
    scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def setup_soft_focus(scene, clean_path: Path, soft_path: Path, long_edge_px: int):
    """Highlight-only soft focus per contract.soft_focus (Blender 5.x compositor node group):
    luminance smoothstep 0.9-1.8 gated by the crystal / mirror-bevel / spinner-facet object masks,
    two Gaussian passes (0.25 % and 1 % of the long edge) added at 10 % and 2.5 %. Beauty is never
    blurred directly; typography/backplate are outside the masks. Writes beauty-clean and beauty-soft."""
    sf = CONTRACT["soft_focus"]
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        zone = int(ob.get("cmf_zone_id", -1))
        ob.pass_index = 3 if ob.name.startswith("GEO_PDC_REVIEW_SPINNER") else 1 if zone == 1 else 2 if zone == 6 else 0
    scene.view_layers[0].use_pass_object_index = True
    nt = bpy.data.node_groups.new("NG_PDC_SOFT_FOCUS_PREVIEW", "CompositorNodeTree")
    nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.compositing_node_group = nt
    rl = nt.nodes.new("CompositorNodeRLayers"); rl.scene = scene
    scene.view_layers[0].use_pass_object_index = False       # toggling after node creation makes the pass socket appear (5.x)
    scene.view_layers[0].use_pass_object_index = True
    image = rl.outputs["Image"]
    index_out = rl.outputs["Object Index"] if "Object Index" in rl.outputs else rl.outputs["IndexOB"]

    def math(op, a, b=None, const_b=None):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = op
        nt.links.new(a, n.inputs[0])
        if b is not None:
            nt.links.new(b, n.inputs[1])
        elif const_b is not None:
            n.inputs[1].default_value = const_b
        return n.outputs[0]

    def mix_rgb(blend, fac, a, b):
        n = nt.nodes.new("ShaderNodeMix"); n.data_type = "RGBA"; n.blend_type = blend
        n.inputs[0].default_value = fac
        nt.links.new(a, n.inputs[6]); nt.links.new(b, n.inputs[7])
        return n.outputs[2]

    masks = []
    for idx in (1, 2, 3):
        m = nt.nodes.new("CompositorNodeIDMask"); m.inputs["Index"].default_value = idx; m.inputs["Anti-Alias"].default_value = True
        nt.links.new(index_out, m.inputs["ID value"]); masks.append(m.outputs["Alpha"])
    mask = math("MAXIMUM", math("MAXIMUM", masks[0], masks[1]), masks[2])
    lum = nt.nodes.new("CompositorNodeRGBToBW"); nt.links.new(image, lum.inputs["Image"])
    rng = nt.nodes.new("ShaderNodeMapRange"); rng.data_type = "FLOAT"; rng.interpolation_type = "SMOOTHSTEP"; rng.clamp = True
    threshold = SOFT_THRESHOLD or sf["highlight_smoothstep"]
    rng.inputs["From Min"].default_value, rng.inputs["From Max"].default_value = threshold
    nt.links.new(lum.outputs[0], rng.inputs["Value"])
    gate = math("MULTIPLY", rng.outputs["Result"], mask)
    # highlight layer = image * gate (per-pixel): Mix(MULTIPLY) with the gate broadcast as a colour
    gate_col = nt.nodes.new("CompositorNodeCombineColor")
    for i in range(3):
        nt.links.new(gate, gate_col.inputs[i])
    gate_col.inputs[3].default_value = 1.0
    glow = mix_rgb("MULTIPLY", 1.0, image, gate_col.outputs[0])
    acc = image
    blur_px = []
    radii = sf["blur_radius_relative_to_long_edge"]
    if SOFT_LEVEL == "max":
        radii = [radii[0], radii[1]]            # both passes keep their own radius; only the mix goes to the top of its range
    mixes = []
    for rel_radius, weights in zip(radii, sf["blur_mix_weight_ranges"]):
        px = max(1, int(round(rel_radius * SOFT_RADIUS_SCALE * long_edge_px))); blur_px.append(px)
        blur = nt.nodes.new("CompositorNodeBlur"); blur.inputs["Size"].default_value = (px, px)
        nt.links.new(glow, blur.inputs["Image"])
        w = (max(weights) if SOFT_LEVEL == "max" else mid(weights)) * SOFT_GAIN; mixes.append(round(w, 4))
        acc = mix_rgb("ADD", min(w, 1.0), acc, blur.outputs["Image"])
    out = nt.nodes.new("NodeGroupOutput"); nt.links.new(acc, out.inputs[0])
    return {"masks": ["crystal(1)", "mirror(2)", "spinner(3)"], "highlight_smoothstep": threshold, "blur_px": blur_px,
            "mix": mixes, "level": SOFT_LEVEL, "gain": SOFT_GAIN, "radius_scale": SOFT_RADIUS_SCALE, "within_contract": not SOFT_DEMO,
            "outputs": [clean_path.name, soft_path.name],
            "note": "compositor node group; beauty-clean rendered first with compositing off, beauty-soft through the group"}


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
    calib = calibrate(scene, hero, lights, target_p97=REVIEW_TARGET_P97 if REVIEW_BRIGHT else 0.80)
    calib["cmf_scheme_a_preview_overrides"] = SCHEME_A_OVERRIDES if SCHEME_A else None
    calib["review_bright"] = {"enabled": REVIEW_BRIGHT, "world_strength": REVIEW_WORLD_STRENGTH if REVIEW_BRIGHT else None,
                              "top_fill_relative_power": REVIEW_TOP_FILL_POWER if REVIEW_BRIGHT else None,
                              "note": "review aid; contract beauty rig unchanged; not Gate 08 lighting"}
    scene["cmf_preview_calibration"] = json.dumps(calib)

    stills = {
        "cmf-preview-hero.png": ("CAM_PDC_HERO", (2048, 1365)),
        "cmf-preview-front.png": ("CAM_PDC_FRONT", (2048, 2048)),
        "cmf-preview-low-oblique.png": ("CAM_PDC_LOW_OBLIQUE", (2048, 1365)),
        "cmf-preview-corner-macro.png": ("CAM_PDC_CORNER_MACRO", (2048, 1365)),
        "cmf-preview-pocket-rim-macro.png": ("CAM_PDC_POCKET_RIM_MACRO", (2048, 1365)),
    }
    soft_info = None
    for filename, (cam_name, res) in stills.items():
        if STILLS_ONLY is not None and filename not in STILLS_ONLY:
            continue
        out_name = filename.replace(".png", OUT_SUFFIX + ".png")
        if SOFT_FOCUS and cam_name == "CAM_PDC_HERO":
            clean = OUT_DIR / out_name.replace(".png", "-clean.png")
            soft = OUT_DIR / out_name.replace(".png", f"-soft{SOFT_TAG}.png")
            scene.render.use_compositing = False
            render(scene, bpy.data.objects[cam_name], clean, res)
            soft_info = setup_soft_focus(scene, clean, soft, max(res))
            scene.render.use_compositing = True
            render(scene, bpy.data.objects[cam_name], soft, res)
            scene.render.use_compositing = False
            scene.compositing_node_group = None
            continue
        render(scene, bpy.data.objects[cam_name], OUT_DIR / out_name, res)

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
              "stills": [f.replace(".png", OUT_SUFFIX + ".png") for f in stills], "turntable_frames": FRAMES if RENDER_TURNTABLE else 0,
              "tier": ({"id": TIER, "rarity": TIERS[TIER]["rarity"], "aperture": "bold" if BOLD else "medium" if MEDIUM else "narrow",
                        **{k: v for k, v in TIERS[TIER].items() if k != "rarity"},
                        "source": "PremiumDisplayCaseLabelPlate.foilByTier order Steel/Copper/Silver/Gold; FDB-DSP-014 liner tints"} if TIER else None),
              "soft_focus": soft_info,
              "status": "supplementary CMF preview; not Gate 07 lookdev" + ("; rarity variation study" if TIER else "")}
    (OUT_DIR / f"cmf-preview-report{OUT_SUFFIX}{SOFT_TAG if SOFT_FOCUS else ''}.json").write_text(json.dumps(report, indent=2) + "\n")
    if not TIER:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "tri-spinner-slab-cmf-preview-r009.blend"))
    print("CMF_PREVIEW_RESULT=" + json.dumps(report))


main()
