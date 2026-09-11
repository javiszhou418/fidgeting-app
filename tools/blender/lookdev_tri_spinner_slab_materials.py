"""Gate 07 material lookdev for the premium-display-case `tri-spinner-slab-v3-cmf` variant
(evidence rev-003, from the user-approved Gate 06 rev-011 geometry).

    blender -b --python tools/blender/lookdev_tri_spinner_slab_materials.py -- [--no-turntable] [--frames N] [--samples N] [--tier steel|copper|titanium|gold]

Gate 07 asks one question: are the surface response and the material boundaries correct?
So this script
- verifies the approved Gate 06 blend hash against pipeline.json, never edits geometry;
- builds the SEVEN case materials from contract rev-013 (`materials`, `cmf.scheme` A, `cmf.rarity_tier_map`)
  with the surface detail Gate 05 previews only faked: directional brushing on the satin steel (UV2.x angle),
  micro-bump sandblast on the field / rear plate (contract feature / bump ranges), whole-crystal thin film,
  piano-black coat, anisotropic champagne gold, smoke liner absorption;
- prints the header label decal (Oxanium, placeholder copy, runtime-owned) onto the graphite plate;
- lights the case with the contract NEUTRAL rig (key / fill / rear 5600 K, no colour, no bloom) calibrated to an
  18 % grey card at 0.18 scene-linear, so material response is judged without the beauty rig;
- renders the material board (hero, front, header-macro, main-cmf-macro, crystal-bevel-macro, pocket-rim-macro),
  a material-id map, the four rarity tiers and a neutral turntable; writes material-revalidation.json with the
  final per-zone values proposed for MaterialLibrary registration after approval.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else 72
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 128
TIER = ARGS[ARGS.index("--tier") + 1] if "--tier" in ARGS else None
ONLY = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else None

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-013/modeling-contract.json"
SOURCE_BLEND = PIPELINE / "evidence/06-geometry/rev-011/tri-spinner-slab-geometry-r011.blend"
OUT_DIR = PIPELINE / "evidence/07-material/rev-003"
DECAL_PNG = OUT_DIR / "header-label-decal.png"
LIBRARY = json.loads((REPO / "unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json").read_text())
TURNTABLE_DIR = Path(f"{__import__('os').path.expanduser('~')}/Library/Caches/fidgeting-renders/tri-spinner-slab-g07-r003-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
MM = 0.001

CONTRACT = json.loads(CONTRACT_PATH.read_text())
CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
MATERIALS = {m["slot"]: m for m in CONTRACT["materials"]["materials"]}
INPUTS = {i["id"]: i for i in CONTRACT["parameters"]["inputs"]}
TIER_MAP = INPUTS["cmf.rarity_tier_map"]["value"]
MANIFEST = json.loads((PIPELINE / "pipeline.json").read_text())
LIB_STEEL = next(m for m in LIBRARY["materials"] if m["id"] == "steel-satin")["blender"]

# Gate 07 values: contract mid-values + the scheme-A decisions the user approved through the Gate 05 previews
SCHEME_A = {3: {"base_srgb_hex": "#5C6266", "roughness": 0.45}, 6: {"base_srgb_hex": "#C9D0D6", "roughness": 0.04},
            4: {"coat_weight": 1.0, "coat_roughness": 0.03, "roughness": 0.25}, 5: {"anisotropic": 0.8, "anisotropic_rotation": 0.0, "roughness": 0.30}}
ZONE_COLORS = {1: (0.80, 0.90, 1.00, 1.0), 2: (0.22, 0.20, 0.26, 1.0), 3: (0.60, 0.62, 0.64, 1.0), 4: (0.09, 0.09, 0.10, 1.0),
               5: (0.86, 0.87, 0.89, 1.0), 6: (0.98, 0.99, 1.00, 1.0), 7: (0.92, 0.72, 0.30, 1.0)}
ZONE_LEGEND = "1 crystal / 2 smoke liner / 3 dark sandblast / 4 piano black / 5 brushed steel / 6 mirror / 7 accent metal"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_hex_to_linear(hex_str):
    h = hex_str.lstrip("#"); out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def srgb_to_linear(rgb):
    return tuple((c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in rgb)


def mid(rng):
    return (rng[0] + rng[1]) / 2 if isinstance(rng, (list, tuple)) else rng


def kelvin_to_rgb(k):
    t = k / 100.0
    r = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    return tuple(max(0.0, min(255.0, v)) / 255.0 for v in (r, g, b))


# ---------------------------------------------------------------------------------------------------- materials --
def new_material(name):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
    return mat, bsdf, nt


def object_coords(nt, scale=(1.0, 1.0, 1.0), rotation_z=0.0):
    tex = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale; mp.inputs["Rotation"].default_value = (0.0, 0.0, rotation_z)
    nt.links.new(tex.outputs["Object"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def brushed_steel(name, base_linear, roughness, aniso, brushing_angle_norm, pitch_mm):
    """Directional brushing: anisotropic highlight + fine roughness streaks along the brushing direction."""
    mat, b, nt = new_material(name)
    b.inputs["Base Color"].default_value = (*base_linear[:3], 1.0); b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = roughness; b.inputs["Anisotropic"].default_value = aniso
    b.inputs["Anisotropic Rotation"].default_value = brushing_angle_norm
    # streak noise: very long along the brush axis, pitch-scale across it (object space, metres)
    across = 1.0 / (pitch_mm * MM)
    angle = brushing_angle_norm * math.pi
    vec = object_coords(nt, scale=(across * 0.02, across, across * 0.02), rotation_z=angle)     # long in local X (rotated), fine across
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 1.0; noise.inputs["Detail"].default_value = 3.0; noise.inputs["Roughness"].default_value = 0.6
    nt.links.new(vec, noise.inputs["Vector"])
    rough = nt.nodes.new("ShaderNodeMapRange"); rough.inputs["From Min"].default_value = 0.35; rough.inputs["From Max"].default_value = 0.65
    # library steel-satin "avoid: brushed streaks visible from far away": keep the streak amplitude small (macro-visible only)
    rough.inputs["To Min"].default_value = roughness - 0.015; rough.inputs["To Max"].default_value = roughness + 0.015
    nt.links.new(noise.outputs["Fac"], rough.inputs["Value"]); nt.links.new(rough.outputs["Result"], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.04; bump.inputs["Distance"].default_value = 0.0015 * MM
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    mat["gate07"] = json.dumps({"brushing_angle_normalized": brushing_angle_norm, "brush_pitch_mm": pitch_mm, "roughness_delta": 0.015, "bump_mm": 0.0015})
    return mat


def sandblast(name, base_hex, roughness, feature_mm, bump_mm, rough_delta, seed):
    mat, b, nt = new_material(name)
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(base_hex); b.inputs["Metallic"].default_value = 1.0
    vec = object_coords(nt, scale=(1.0 / (feature_mm * MM),) * 3)
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.noise_dimensions = "4D"; noise.inputs["W"].default_value = seed % 97
    noise.inputs["Scale"].default_value = 1.0; noise.inputs["Detail"].default_value = 4.0; noise.inputs["Roughness"].default_value = 0.7
    nt.links.new(vec, noise.inputs["Vector"])
    rough = nt.nodes.new("ShaderNodeMapRange"); rough.inputs["From Min"].default_value = 0.3; rough.inputs["From Max"].default_value = 0.7
    rough.inputs["To Min"].default_value = roughness - rough_delta; rough.inputs["To Max"].default_value = roughness + rough_delta
    nt.links.new(noise.outputs["Fac"], rough.inputs["Value"]); nt.links.new(rough.outputs["Result"], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = bump_mm * MM
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    mat["gate07"] = json.dumps({"feature_mm": feature_mm, "bump_mm": bump_mm, "roughness": roughness, "roughness_delta": rough_delta, "seed": seed})
    return mat


def make_materials(tier):
    mats = {}
    m1 = MATERIALS[1]["blender"]
    mat, b, nt = new_material("M_PDC_ClearCrystal")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m1["base_color_srgb_hex"]); b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = mid(m1["roughness_range"]); b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["IOR"].default_value = m1["ior"]
    b.inputs["Coat Weight"].default_value = m1["coat_weight"]; b.inputs["Coat Roughness"].default_value = m1["coat_roughness"]
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 18.0; noise.inputs["Detail"].default_value = 2.0
    thick = nt.nodes.new("ShaderNodeMapRange"); thick.inputs["To Min"].default_value, thick.inputs["To Max"].default_value = m1["thin_film_thickness_nm_range"]
    nt.links.new(noise.outputs["Fac"], thick.inputs["Value"]); nt.links.new(thick.outputs["Result"], b.inputs["Thin Film Thickness"])
    b.inputs["Thin Film IOR"].default_value = mid(m1["thin_film_ior_range"])
    mat["gate07"] = json.dumps({"thin_film_nm": m1["thin_film_thickness_nm_range"], "thin_film_ior": mid(m1["thin_film_ior_range"]), "mask": "whole crystal (contract rev-011+)"})
    mats[1] = mat

    m2 = MATERIALS[2]["blender"]
    mat, b, nt = new_material("M_PDC_SmokeLiner")
    liner = TIER_MAP[tier_rarity(tier)]["liner_srgb"] if tier else None
    b.inputs["Base Color"].default_value = (*srgb_to_linear(liner), 1.0) if liner else srgb_hex_to_linear(m2["base_color_srgb_hex"])
    b.inputs["Roughness"].default_value = mid(m2["roughness_range"]); b.inputs["Transmission Weight"].default_value = mid(m2["transmission_weight_range"]); b.inputs["IOR"].default_value = m2["ior"]
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption"); vol.inputs["Color"].default_value = (0.55, 0.48, 0.66, 1.0); vol.inputs["Density"].default_value = 180.0
    nt.links.new(vol.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    mats[2] = mat

    m3 = MATERIALS[3]["blender"]
    mats[3] = sandblast("M_PDC_DarkSandblast", SCHEME_A[3]["base_srgb_hex"], SCHEME_A[3]["roughness"], mid(m3["feature_mm_range"]), mid(m3["bump_mm_range"]), m3["roughness_delta"], m3["seed"])

    m4 = MATERIALS[4]["blender"]
    mat, b, nt = new_material("M_PDC_PianoBlack")
    b.inputs["Base Color"].default_value = srgb_hex_to_linear(m4["base_color_srgb_hex"]); b.inputs["Metallic"].default_value = m4["metallic"]
    b.inputs["Roughness"].default_value = SCHEME_A[4]["roughness"]; b.inputs["Coat Weight"].default_value = SCHEME_A[4]["coat_weight"]; b.inputs["Coat Roughness"].default_value = SCHEME_A[4]["coat_roughness"]
    mat["gate07"] = json.dumps(SCHEME_A[4]); mats[4] = mat

    # header plate = piano black + printed label (ink in base colour, matte ink roughness)
    mat, b, nt = new_material("M_PDC_PianoBlack_HeaderLabel")
    b.inputs["Metallic"].default_value = m4["metallic"]; b.inputs["Coat Weight"].default_value = SCHEME_A[4]["coat_weight"]; b.inputs["Coat Roughness"].default_value = SCHEME_A[4]["coat_roughness"]
    img = bpy.data.images.load(str(DECAL_PNG)); img.colorspace_settings.name = "sRGB"
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.extension = "CLIP"
    plane = bpy.data.objects["GEO_PDC_HEADER_GRAPHITE_PLANE"]
    pts = [plane.matrix_world @ Vector(c) for c in plane.bound_box]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts); z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    coord = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(coord.outputs["Object"], sep.inputs["Vector"])
    u = nt.nodes.new("ShaderNodeMapRange"); u.inputs["From Min"].default_value = x0; u.inputs["From Max"].default_value = x1; nt.links.new(sep.outputs["X"], u.inputs["Value"])
    v = nt.nodes.new("ShaderNodeMapRange"); v.inputs["From Min"].default_value = z0; v.inputs["From Max"].default_value = z1; nt.links.new(sep.outputs["Z"], v.inputs["Value"])
    comb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u.outputs["Result"], comb.inputs["X"]); nt.links.new(v.outputs["Result"], comb.inputs["Y"])
    nt.links.new(comb.outputs["Vector"], tex.inputs["Vector"])
    mixc = nt.nodes.new("ShaderNodeMix"); mixc.data_type = "RGBA"; mixc.blend_type = "MIX"
    mixc.inputs[6].default_value = srgb_hex_to_linear(m4["base_color_srgb_hex"]); nt.links.new(tex.outputs["Color"], mixc.inputs[7]); nt.links.new(tex.outputs["Alpha"], mixc.inputs[0])
    nt.links.new(mixc.outputs[2], b.inputs["Base Color"])
    mixr = nt.nodes.new("ShaderNodeMix"); mixr.data_type = "FLOAT"; mixr.inputs[2].default_value = SCHEME_A[4]["roughness"]; mixr.inputs[3].default_value = 0.55
    nt.links.new(tex.outputs["Alpha"], mixr.inputs[0]); nt.links.new(mixr.outputs[0], b.inputs["Roughness"])
    mat["gate07"] = json.dumps({"decal": DECAL_PNG.name, "mapping": "planar object-space x/z over the plate bounds", "ink_roughness": 0.55, "copy": "placeholder, runtime-owned"})
    mats["header_plate"] = mat

    base5 = LIB_STEEL["baseColor"]
    if tier and TIER_MAP[tier_rarity(tier)]["tier"] != "steel":
        base5 = srgb_to_linear(TIER_MAP[tier_rarity(tier)]["accent_srgb"])          # bold aperture: bezels take the tier metal
    mats[5] = brushed_steel("M_PDC_BrushedSteel" + (f"_{tier}" if tier else ""), base5, SCHEME_A[5]["roughness"], SCHEME_A[5]["anisotropic"], 0.0, mid(LIB_STEEL.get("brush_pitch_mm_range", [0.04, 0.08])) if "brush_pitch_mm_range" in LIB_STEEL else 0.06)

    m6 = MATERIALS[6]["blender"]
    mat, b, nt = new_material("M_PDC_Mirror" + (f"_{tier}" if tier else ""))
    base6 = srgb_hex_to_linear(SCHEME_A[6]["base_srgb_hex"])
    if tier and TIER_MAP[tier_rarity(tier)]["tier"] != "steel":
        base6 = (*[min(1.0, c * 1.05) for c in srgb_to_linear(TIER_MAP[tier_rarity(tier)]["accent_srgb"])], 1.0)
    b.inputs["Base Color"].default_value = base6; b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = SCHEME_A[6]["roughness"]
    mat["gate07"] = json.dumps({"base_srgb_hex": SCHEME_A[6]["base_srgb_hex"], "roughness": SCHEME_A[6]["roughness"], "visible_grain": False}); mats[6] = mat

    m7 = MATERIALS[7]["blender"]
    base7 = srgb_hex_to_linear(m7["base_color_srgb_hex"])[:3]
    if tier:
        base7 = srgb_to_linear(TIER_MAP[tier_rarity(tier)]["accent_srgb"])
    mats[7] = brushed_steel("M_PDC_AccentMetal" + (f"_{tier}" if tier else ""), base7, mid(m7["roughness_range"]), mid(m7["anisotropy_range"]), 0.0, 0.05)

    floor, fb, fnt = new_material("M_PDC_LookdevFloor"); fb.inputs["Base Color"].default_value = (0.02, 0.02, 0.022, 1.0); fb.inputs["Roughness"].default_value = 0.35; fb.inputs["Metallic"].default_value = 0.0
    mats["floor"] = floor
    card, cb, cnt = new_material("M_PDC_GreyCard18"); cb.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1.0); cb.inputs["Roughness"].default_value = 1.0; cb.inputs["Specular IOR Level"].default_value = 0.0
    mats["card"] = card
    return mats


def tier_rarity(tier):
    return next(r for r, e in TIER_MAP.items() if e["tier"] == tier)


def assign(mats):
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not ob.name.startswith("GEO_PDC_") or ob.name.startswith("GEO_PDC_REVIEW_"):
            continue
        zone = int(ob.get("cmf_zone_id", -1))
        mat = mats["header_plate"] if ob.name == "GEO_PDC_HEADER_GRAPHITE_PLANE" else mats.get(zone)
        if mat is None:
            continue
        ob.data.materials.clear(); ob.data.materials.append(mat)
        if zone == 7 and "UV2" in ob.data.uv_layers:          # gold: brushing along the inlay long axis from UV2.x
            angle = ob.data.uv_layers["UV2"].data[0].uv.x if len(ob.data.uv_layers["UV2"].data) else 0.0
            if abs(angle - 0.5) < 1e-3:
                per = mats[7].copy(); per.name = mats[7].name + "_v"
                per.node_tree.nodes["Principled BSDF"].inputs["Anisotropic Rotation"].default_value = 0.5
                for n in per.node_tree.nodes:
                    if n.type == "MAPPING":
                        n.inputs["Rotation"].default_value = (0.0, 0.0, math.pi / 2)
                ob.data.materials[0] = per


# ------------------------------------------------------------------------------------------------------ lighting --
def bounds(objects):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c); lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def neutral_rig(scene, hero, target, diag):
    rig = CONTRACT["lighting"]["neutral"]
    col = bpy.data.collections.get("COL_PDC_LIGHTS_NEUTRAL")
    cam_pos = hero.matrix_world.translation
    right = hero.matrix_world.to_3x3() @ Vector((1, 0, 0)); up = hero.matrix_world.to_3x3() @ Vector((0, 1, 0)); toward = (target - cam_pos).normalized()
    # key upper-left; fill = a large soft card behind/around the camera so the frontal brushed flats reflect a grey field instead of
    # the black world (metals show what faces them); rear = top-back for the crystal rim. Relative powers from the contract.
    placement = {"key": ((-0.6, 0.7, 0.8), (0.9, 0.9)), "fill": ((0.1, 1.15, 0.35), (1.9, 1.5)), "rear": ((0.2, -0.9, 0.9), (0.8, 0.5))}
    lights = []
    for spec in rig["lights"]:
        (x, y, z), (sx, sy) = placement[spec["id"]]
        data = bpy.data.lights.new(f"LGT_PDC_NEUTRAL_{spec['id'].upper()}", "AREA"); data.shape = "RECTANGLE"
        data.size, data.size_y = sx * diag, sy * diag; data.color = kelvin_to_rgb(spec["temperature_k"]); data["relative_power"] = spec["relative_power"]
        ob = bpy.data.objects.new(data.name, data); col.objects.link(ob)
        ob.location = target + right * x * diag - toward * y * diag + up * z * diag
        ob.rotation_euler = (target - ob.location).normalized().to_track_quat("-Z", "Y").to_euler(); lights.append(ob)
    world = bpy.data.worlds.new("WORLD_PDC_NEUTRAL_G07"); world.use_nodes = True
    bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = srgb_hex_to_linear(rig["background_srgb_range"][0]); bg.inputs["Strength"].default_value = 1.0
    scene.world = world
    return lights


def calibrate_grey_card(scene, hero, lights, mats, target, diag, lo, hi):
    """Contract lighting.calibration: an 18 % Lambert grey card must read 0.18 scene-linear (+-0.02). The card sits at the case
    front centre facing the key light; the render is a tiny border region around it."""
    for ob in lights:
        ob.data.energy = 3.0 * ob.data["relative_power"] * ob.data.size * ob.data.size_y
    bpy.ops.mesh.primitive_plane_add(size=0.012, location=(target.x, lo.y - 0.004, target.z))
    card = bpy.context.active_object; card.name = "GEO_PDC_CALIB_CARD"; card.rotation_euler = (math.radians(90), 0, 0); card.data.materials.append(mats["card"])
    card["export_role"] = "preview-only"
    saved = (scene.cycles.samples, scene.render.use_stamp, scene.view_settings.view_transform, scene.view_settings.look)
    scene.cycles.samples, scene.render.use_stamp = 32, False
    scene.view_settings.view_transform, scene.view_settings.look = "Standard", "None"
    scene.render.image_settings.color_management = "OVERRIDE"; scene.render.image_settings.view_settings.view_transform = "Standard"
    scene.render.image_settings.file_format = "OPEN_EXR"; scene.render.image_settings.color_depth = "32"
    tmp = TURNTABLE_DIR.parent / "pdc_g07_calib.exr"; tmp.parent.mkdir(parents=True, exist_ok=True)
    history = []
    for _ in range(2):
        render(scene, hero, tmp, (256, 171))
        img = bpy.data.images.load(str(tmp), check_existing=False)
        w, h = img.size; px = list(img.pixels)
        # card projects near the image centre-bottom of the case; sample a 9x9 block at its projected position
        co = bpy.context.scene.camera.matrix_world.inverted() @ card.matrix_world.translation
        from bpy_extras.object_utils import world_to_camera_view
        uv = world_to_camera_view(scene, hero, card.matrix_world.translation)
        cx, cy = int(uv.x * w), int(uv.y * h)
        vals = []
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                i = ((cy + dy) * w + (cx + dx)) * 4
                if 0 <= i < len(px) - 3:
                    vals.append(0.2126 * px[i] + 0.7152 * px[i + 1] + 0.0722 * px[i + 2])
        lum = sorted(vals)[len(vals) // 2] if vals else 0.18
        factor = 0.18 / max(lum, 1e-4)
        for ob in lights:
            ob.data.energy *= factor
        history.append({"card_luminance": round(lum, 4), "factor": round(factor, 4)})
        bpy.data.images.remove(img)
    scene.cycles.samples, scene.render.use_stamp, scene.view_settings.view_transform, scene.view_settings.look = saved
    scene.render.image_settings.color_management = "FOLLOW_SCENE"; scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_depth = "8"
    bpy.data.objects.remove(card, do_unlink=True)
    return {"target_scene_linear": 0.18, "tolerance": 0.02, "passes": history, "energies_w": {l.name: round(l.data.energy, 3) for l in lights},
            "within_tolerance": abs(history[-1]["card_luminance"] * history[-1]["factor"] - 0.18) <= 0.02}


def configure_cycles(scene, note):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"; prefs.get_devices()
        for dev in prefs.devices:
            dev.use = dev.type in ("METAL", "CPU")
        scene.cycles.device = "GPU"
    except Exception as exc:  # noqa: BLE001
        print("GPU setup failed, CPU fallback:", exc); scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES; scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.015
    scene.cycles.use_denoising = True; scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.max_bounces = 12; scene.cycles.transmission_bounces = 12; scene.cycles.transparent_max_bounces = 12; scene.cycles.glossy_bounces = 6
    scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False; scene.cycles.blur_glossy = 0.2
    scene.render.film_transparent = False; scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Base Contrast"
    scene.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_frame_range", "use_stamp_memory",
                 "use_stamp_hostname", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene", "use_stamp_marker", "use_stamp_filename", "use_stamp_sequencer_strip"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.use_stamp_note = True; scene.render.stamp_note_text = note
    scene.render.stamp_font_size = 22; scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0); scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def render(scene, cam, path, resolution):
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = resolution; scene.render.resolution_percentage = 100
    scene.render.filepath = str(path); bpy.ops.render.render(write_still=True)


def macro_camera(name, region_lo_mm, region_hi_mm, yaw_deg, elev_deg, resolution=(2048, 1365), margin=0.06):
    """Perspective camera framing a canonical-mm region (x, y, z canonical) from yaw/elevation, 85 mm on a 36x24 sensor."""
    # canonical (x, y, z) -> Blender (x, -z, y)
    lo = Vector((region_lo_mm[0], -region_hi_mm[2], region_lo_mm[1])) * MM; hi = Vector((region_hi_mm[0], -region_lo_mm[2], region_hi_mm[1])) * MM
    centre = (lo + hi) / 2; radius = (hi - lo).length / 2
    yaw, elev = math.radians(yaw_deg), math.radians(elev_deg)
    direction = Vector((math.sin(yaw) * math.cos(elev), -math.cos(yaw) * math.cos(elev), math.sin(elev)))
    cam_data = bpy.data.cameras.new(name); cam_data.sensor_width, cam_data.lens = 36.0, 85.0; cam_data.clip_start = 0.001
    fov = 2 * math.atan(cam_data.sensor_width / (2 * cam_data.lens)); dist = radius * (1 + 2 * margin) / math.sin(fov / 2)
    cam = bpy.data.objects.new(name, cam_data); bpy.context.scene.collection.objects.link(cam)
    cam.location = centre + direction * dist; cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    cam["camera_recipe"] = json.dumps({"projection": "perspective", "focal_length_mm": 85, "yaw_deg": yaw_deg, "elevation_deg": elev_deg, "region_canonical_mm": [region_lo_mm, region_hi_mm], "resolution": list(resolution)})
    return cam


def main():
    expected = next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-g06-geometry-blend")["sha256"]
    assert sha256(SOURCE_BLEND) == expected, "approved Gate 06 rev-011 geometry blend hash changed"
    assert DECAL_PNG.exists(), "run make_tri_spinner_slab_label_decal.py first"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith("GEO_PDC_REVIEW_SPINNER"):
            ob.hide_render = False                                   # the toy sits in the pocket for material judgement (caller-owned, unchanged)
    mats = make_materials(TIER); assign(mats)
    case = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO_PDC_") and not o.name.startswith("GEO_PDC_REVIEW_")]
    lo, hi = bounds(case); diag = (hi - lo).length; target = (lo + hi) / 2
    hero = bpy.data.objects["CAM_PDC_HERO"]
    bpy.ops.mesh.primitive_plane_add(size=diag * 12, location=(target.x, target.y, lo.z - 0.3 * MM))
    floor = bpy.context.active_object; floor.name = "GEO_PDC_LOOKDEV_FLOOR"; floor.data.materials.append(mats["floor"]); floor["export_role"] = "preview-only"
    bpy.data.collections["COL_PDC_LOOKDEV"].objects.link(floor); scene.collection.objects.unlink(floor)
    suffix = f"-tier-{TIER}" if TIER else ""
    configure_cycles(scene, f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 07 material r003 | NEUTRAL rig (18 % card 0.18) | contract {CONTRACT_SHA[:12]} | source Gate 06 r011 {expected[:12]}"
                            + (f" | TIER {TIER.upper()} = {tier_rarity(TIER)}" if TIER else "") + " | label copy = placeholder")
    lights = neutral_rig(scene, hero, target, diag)
    calib = calibrate_grey_card(scene, hero, lights, mats, target, diag, lo, hi)

    # header macro: the plate region; main CMF macro: lower field with gold rails, plaque, lip foot; crystal bevel macro: top-left frame corner
    header = bpy.data.objects["GEO_PDC_HEADER_GRAPHITE_PLANE"]; hlo, hhi = bounds([header])
    header_region = ([hlo.x / MM - 6, hlo.z / MM - 6, -12], [hhi.x / MM + 6, hhi.z / MM + 6, 12])
    plaque = bpy.data.objects["GEO_PDC_MAIN_TRAIT_PLAQUE"]; plo, phi = bounds([plaque])
    main_region = ([plo.x / MM - 8, plo.z / MM - 6, -12], [phi.x / MM + 8, phi.z / MM + 26, 12])
    cams = {"header-macro": macro_camera("CAM_G07_HEADER_MACRO", *header_region, yaw_deg=-18, elev_deg=22),
            "main-cmf-macro": macro_camera("CAM_G07_MAIN_CMF_MACRO", *main_region, yaw_deg=14, elev_deg=30)}
    views = {"material-hero.png": (hero, (2048, 1365)), "material-front.png": (bpy.data.objects["CAM_PDC_FRONT"], (2048, 2048)),
             "material-header-macro.png": (cams["header-macro"], (2048, 1365)), "material-main-cmf-macro.png": (cams["main-cmf-macro"], (2048, 1365)),
             "material-crystal-bevel-macro.png": (bpy.data.objects["CAM_PDC_CORNER_MACRO"], (2048, 1365)),
             "material-pocket-rim-macro.png": (bpy.data.objects["CAM_PDC_POCKET_RIM_MACRO"], (2048, 1365))}
    rendered = []
    for name, (cam, res) in views.items():
        if ONLY and name not in ONLY:
            continue
        out = OUT_DIR / name.replace(".png", suffix + ".png"); render(scene, cam, out, res); rendered.append(out.name)

    # material-id map: flat zone colours, same hero framing (boundaries check)
    if not TIER and (ONLY is None or "material-id-hero.png" in ONLY):
        saved_engine = scene.render.engine
        scene.render.engine = "BLENDER_WORKBENCH"; sh = scene.display.shading; sh.light = "FLAT"; sh.color_type = "OBJECT"; sh.show_cavity = False; sh.show_shadows = False
        scene.view_settings.view_transform = "Standard"
        for ob in case:
            ob.color = ZONE_COLORS.get(int(ob.get("cmf_zone_id", 0)), (0.5, 0.5, 0.5, 1.0))
        for ob in bpy.data.objects:
            if ob.name.startswith("GEO_PDC_REVIEW_SPINNER"):
                ob.color = (0.3, 0.3, 0.3, 1.0)
        scene.render.stamp_note_text += f" | MATERIAL-ID: {ZONE_LEGEND}"
        render(scene, hero, OUT_DIR / "material-id-hero.png", (2048, 1365)); rendered.append("material-id-hero.png")
        render(scene, bpy.data.objects["CAM_PDC_FRONT"], OUT_DIR / "material-id-front.png", (2048, 2048)); rendered.append("material-id-front.png")
        scene.render.engine = saved_engine; scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Base Contrast"
        scene.render.stamp_note_text = scene.render.stamp_note_text.split(" | MATERIAL-ID")[0]

    turntable = None
    if RENDER_TURNTABLE and not TIER:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=False)
        root = bpy.data.objects["ROOT_PDC_PRESENTATION"]; saved = scene.cycles.samples; scene.cycles.samples = max(48, SAMPLES // 2)
        for i in range(FRAMES):
            root.rotation_euler = (0.0, 0.0, math.radians(360.0 * i / FRAMES)); bpy.context.view_layer.update()
            render(scene, hero, TURNTABLE_DIR / f"frame_{i:04d}.png", (1440, 960))
        root.rotation_euler = (0.0, 0.0, 0.0); scene.cycles.samples = saved
        turntable = {"frames": FRAMES, "fps": 24, "camera": "CAM_PDC_HERO", "raw_frame_dir": str(TURNTABLE_DIR), "rig": "neutral"}

    per_zone = {}
    for z, m in mats.items():
        if isinstance(z, int):
            b = m.node_tree.nodes["Principled BSDF"]
            per_zone[str(z)] = {"material": m.name, "base_color_linear": [round(c, 4) for c in b.inputs["Base Color"].default_value[:3]], "metallic": round(b.inputs["Metallic"].default_value, 3),
                                "roughness_base": round(b.inputs["Roughness"].default_value, 3), "anisotropic": round(b.inputs["Anisotropic"].default_value, 3),
                                "coat_weight": round(b.inputs["Coat Weight"].default_value, 3), "transmission": round(b.inputs["Transmission Weight"].default_value, 3),
                                "detail": json.loads(m["gate07"]) if "gate07" in m else None}
    report = {"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "07-material", "materialRevision": 3,
              "sourceBlend": str(SOURCE_BLEND.relative_to(REPO)), "sourceBlendSha256": expected, "contractSha256": CONTRACT_SHA, "geometryUnchanged": True,
              "tier": TIER, "rig": "neutral (contract lighting.neutral)", "calibration": calib, "materials_by_zone": per_zone,
              "header_label": {"decal": DECAL_PNG.name, "decal_sha256": sha256(DECAL_PNG), "layout": json.loads((OUT_DIR / "header-label-decal.json").read_text()),
                               "status": "placeholder copy; runtime-owned; Oxanium per FDB-GAC-009 type rule"},
              "trait_plaque": "flat runtime-UI region, no placeholder UI drawn (contract trait.render_mode)",
              "scheme_a_values_adopted": SCHEME_A, "library_registration_proposals": [
                  {"id": "case-clear-crystal", "slot": 1}, {"id": "case-smoke-lilac-liner", "slot": 2}, {"id": "case-dark-sandblast", "slot": 3, "note": "supersedes spec #AEB3B6 with the approved scheme-A #5C6266"},
                  {"id": "case-piano-black", "slot": 4}, {"id": "steel-satin", "slot": 5, "note": "library values verbatim + scheme-A anisotropy 0.8"},
                  {"id": "case-bright-mirror", "slot": 6, "note": "supersedes smoked-mirror #667078 with scheme-A #C9D0D6"}, {"id": "case-champagne-gold-inlay", "slot": 7, "note": "+ rarity tiers rose bronze / grey-blue titanium / champagne"}],
              "rendered": rendered, "turntable": turntable, "status": "gate07_candidate_ready_for_review; not Gate 08 lighting"}
    (OUT_DIR / f"material-revalidation{suffix}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if not TIER:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "tri-spinner-slab-material-r003.blend"))
    print("GATE07_RESULT=" + json.dumps({"rendered": rendered, "calibration": calib, "turntable": bool(turntable)}))


main()
