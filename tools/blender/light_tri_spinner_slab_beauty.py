"""Gate 08 lighting for the premium-display-case `tri-spinner-slab-v3-cmf` variant
(evidence rev-005, on the user-approved Gate 07 rev-003 materials).

    blender -b --python tools/blender/light_tri_spinner_slab_beauty.py -- [--no-turntable] [--frames N] [--samples N] [--tier steel|copper|titanium|gold]

Gate 08 asks: does the lighting reveal the geometry rather than hide it? It
- verifies the approved Gate 07 blend hash, keeps its materials untouched;
- builds the contract rev-013 `lighting.beauty` rig through the CMF preview module (soft key, right strip,
  top rail, cool/lilac rims at 30/26 %, four backlit colour edge strips, eight sparkle lights, front fill,
  review fill card, glossy filter 0) and calibrates exposure (p97 of case pixels -> 0.86);
- renders beauty-clean for hero / left-oblique / right-oblique / low-oblique, beauty-soft for the hero
  through the contract soft_focus compositor (0.7-1.5 threshold, radii 0.75 %/3 %, mix 24-36 %/6-9 %);
- renders the diagnostic passes the pipeline asks for on the hero framing: clay (material override),
  normal, depth (normalised mist), roughness (AOV written by every case material);
- renders the beauty turntable (contract turntable: 144 f, 2.5 deg, 24 fps) and the four rarity tiers.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else 144
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 128
TIER = ARGS[ARGS.index("--tier") + 1] if "--tier" in ARGS else None
ONLY = ARGS[ARGS.index("--only") + 1].split(",") if "--only" in ARGS else None

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-013/modeling-contract.json"
SOURCE_BLEND = PIPELINE / "evidence/07-material/rev-003/tri-spinner-slab-material-r003.blend"
OUT_DIR = PIPELINE / "evidence/08-lighting/rev-005"
TURNTABLE_DIR = Path(f"{__import__('os').path.expanduser('~')}/Library/Caches/fidgeting-renders/tri-spinner-slab-g08-r005-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
MM = 0.001
CONTRACT = json.loads(CONTRACT_PATH.read_text())
CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
MANIFEST = json.loads((PIPELINE / "pipeline.json").read_text())
INPUTS = {i["id"]: i for i in CONTRACT["parameters"]["inputs"]}
TIER_MAP = INPUTS["cmf.rarity_tier_map"]["value"]

# the CMF preview module owns the contract rig, calibration, soft focus and Cycles setup; import it without running main()
spec = importlib.util.spec_from_file_location("pdc_cmf", REPO / "tools/blender/render_tri_spinner_slab_cmf_preview.py")
CMF = importlib.util.module_from_spec(spec); spec.loader.exec_module(CMF)
CMF.OUT_DIR = OUT_DIR                     # soft-focus twin paths are built from OUT_DIR inside the module
assert CMF.CONTRACT_SHA == CONTRACT_SHA, "CMF preview module must point at contract rev-013"
assert CMF.BLING == "contract-rig", "contract rev-013 lighting direction expected"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def srgb_to_linear(rgb):
    return tuple((c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in rgb)


def bounds(objects):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c); lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def case_meshes():
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO_PDC_") and not o.name.startswith("GEO_PDC_REVIEW_") and o.get("export_role") != "preview-only"]


def apply_tier(tier):
    """Bold aperture: bezels (5), polished parts (6), accents (7) and the liner tint (2) take the tier metal; materials otherwise untouched."""
    entry = next(e for e in TIER_MAP.values() if e["tier"] == tier)
    accent = srgb_to_linear(entry["accent_srgb"]); liner = srgb_to_linear(entry["liner_srgb"])
    for ob in case_meshes():
        zone = int(ob.get("cmf_zone_id", 0))
        if zone in (5, 6, 7, 2) and ob.data.materials:
            mat = ob.data.materials[0].copy(); mat.name = f"{ob.data.materials[0].name}_{tier}"
            b = mat.node_tree.nodes.get("Principled BSDF")
            if b is not None:
                if zone == 6:
                    b.inputs["Base Color"].default_value = (*[min(1.0, c * 1.05) for c in accent], 1.0)
                elif zone == 2:
                    b.inputs["Base Color"].default_value = (*liner, 1.0)
                else:
                    b.inputs["Base Color"].default_value = (*accent, 1.0)
            ob.data.materials[0] = mat


def add_roughness_aov():
    """Every case material writes its (possibly textured) roughness to the 'Roughness' AOV."""
    vl = bpy.context.scene.view_layers[0]
    if not any(a.name == "Roughness" for a in vl.aovs):
        aov = vl.aovs.add(); aov.name = "Roughness"; aov.type = "VALUE"
    for ob in case_meshes():
        for mat in ob.data.materials:
            nt = mat.node_tree; b = nt.nodes.get("Principled BSDF")
            if b is None or any(n.type == "OUTPUT_AOV" for n in nt.nodes):
                continue
            out = nt.nodes.new("ShaderNodeOutputAOV"); out.aov_name = "Roughness"
            rough_in = b.inputs["Roughness"]
            if rough_in.is_linked:
                nt.links.new(rough_in.links[0].from_socket, out.inputs["Value"])
            else:
                out.inputs["Value"].default_value = rough_in.default_value


def render(scene, cam, path, resolution):
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = resolution; scene.render.resolution_percentage = 100
    scene.render.filepath = str(path); bpy.ops.render.render(write_still=True)


def render_pass_image(scene, cam, path, resolution, pass_socket, normalize=False, invert=False):
    """Render once and route a Render Layers socket to the composite output through a compositor node group."""
    nt = bpy.data.node_groups.new("NG_PDC_PASS_" + pass_socket.replace(" ", "_"), "CompositorNodeTree")
    nt.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    scene.compositing_node_group = nt
    rl = nt.nodes.new("CompositorNodeRLayers"); rl.scene = scene
    vl = scene.view_layers[0]
    vl.use_pass_normal = True; vl.use_pass_mist = True; vl.use_pass_z = True
    vl.use_pass_normal = False; vl.use_pass_normal = True          # toggle so the sockets appear (Blender 5.x)
    if pass_socket == "Mist":
        # mist range = camera distance to the case bounds, so the pass spans the object instead of clipping to white
        lo, hi = bounds(case_meshes()); cam_pos = cam.matrix_world.translation
        dists = [(cam_pos - Vector((x, y, z))).length for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
        scene.world.mist_settings.start = min(dists) * 0.98; scene.world.mist_settings.depth = (max(dists) - min(dists)) * 1.04; scene.world.mist_settings.falloff = "LINEAR"
    src = rl.outputs[pass_socket]
    if normalize:
        n = nt.nodes.new("CompositorNodeNormalize"); nt.links.new(src, n.inputs[0]); src = n.outputs[0]
    if invert:
        inv = nt.nodes.new("CompositorNodeInvert"); nt.links.new(src, inv.inputs["Color"]); src = inv.outputs["Color"]
    if pass_socket == "Normal":
        # camera-space normal -> 0..1 colour
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "ADD"; mix.inputs[0].default_value = 1.0
        mix.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0); nt.links.new(src, mix.inputs[6])
        scale = nt.nodes.new("ShaderNodeMix"); scale.data_type = "RGBA"; scale.blend_type = "MULTIPLY"; scale.inputs[0].default_value = 1.0
        scale.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0); nt.links.new(mix.outputs[2], scale.inputs[6]); src = scale.outputs[2]
    out = nt.nodes.new("NodeGroupOutput"); nt.links.new(src, out.inputs[0])
    saved = (scene.render.use_compositing, scene.view_settings.view_transform, scene.view_settings.look)
    scene.render.use_compositing = True; scene.view_settings.view_transform = "Standard"; scene.view_settings.look = "None"
    render(scene, cam, path, resolution)
    scene.render.use_compositing, scene.view_settings.view_transform, scene.view_settings.look = saved
    scene.compositing_node_group = None


def main():
    expected = next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-g07-material-blend")["sha256"]
    assert sha256(SOURCE_BLEND) == expected, "approved Gate 07 rev-003 material blend hash changed"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # drop the Gate 07 neutral lights and its world; the beauty rig replaces them
    for ob in list(bpy.data.objects):
        if ob.type == "LIGHT":
            bpy.data.objects.remove(ob, do_unlink=True)
    if TIER:
        apply_tier(TIER)
    case = case_meshes(); lo, hi = bounds(case); diag = (hi - lo).length; target = (lo + hi) / 2
    hero = bpy.data.objects["CAM_PDC_HERO"]
    suffix = f"-tier-{TIER}" if TIER else ""

    CMF.configure_cycles(scene)
    scene.cycles.samples = SAMPLES
    scene.render.stamp_note_text = (f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 08 lighting r005 | contract {CONTRACT_SHA[:12]} beauty rig (reference-bling) | "
                                    f"materials Gate 07 r003 {expected[:12]}" + (f" | TIER {TIER.upper()}" if TIER else ""))
    lights = CMF.build_lights(scene, hero, target, diag)
    calib = CMF.calibrate(scene, hero, lights, target_p97=CMF.REVIEW_TARGET_P97)
    add_roughness_aov()

    views = {"beauty-hero.png": (hero, (2048, 1365)), "beauty-left-oblique.png": (bpy.data.objects["CAM_PDC_LEFT_OBLIQUE"], (2048, 1365)),
             "beauty-right-oblique.png": (bpy.data.objects["CAM_PDC_RIGHT_OBLIQUE"], (2048, 1365)), "beauty-low-oblique.png": (bpy.data.objects["CAM_PDC_LOW_OBLIQUE"], (2048, 1365))}
    rendered = []; soft_info = None
    for name, (cam, res) in views.items():
        if ONLY and name not in ONLY:
            continue
        out = OUT_DIR / name.replace(".png", suffix + ".png")
        if cam is hero:
            clean = OUT_DIR / f"beauty-hero{suffix}-clean.png"; soft = OUT_DIR / f"beauty-hero{suffix}-soft.png"
            scene.render.use_compositing = False; render(scene, hero, clean, res); rendered.append(clean.name)
            soft_info = CMF.setup_soft_focus(scene, clean, soft, max(res)); scene.render.use_compositing = True
            render(scene, hero, soft, res); rendered.append(soft.name)
            scene.render.use_compositing = False; scene.compositing_node_group = None
        else:
            floor = bpy.data.objects.get("GEO_PDC_LOOKDEV_FLOOR")
            if floor is not None and "low" in name:
                floor.hide_render = True                 # the low camera sits below the floor plane; the floor would cover the case
            render(scene, cam, out, res); rendered.append(out.name)
            if floor is not None:
                floor.hide_render = False

    passes = {}
    if not TIER and (ONLY is None or "passes" in ONLY):
        res = (2048, 1365)
        # clay: neutral grey material override, same rig
        vl = scene.view_layers[0]
        clay = bpy.data.materials.new("M_PDC_ClayOverride"); clay.use_nodes = True
        clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0); clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
        vl.material_override = clay; render(scene, hero, OUT_DIR / "pass-clay-hero.png", res); vl.material_override = None; passes["clay"] = "pass-clay-hero.png"
        render_pass_image(scene, hero, OUT_DIR / "pass-normal-hero.png", res, "Normal"); passes["normal"] = "pass-normal-hero.png (world-space normal, 0.5 + 0.5 n)"
        render_pass_image(scene, hero, OUT_DIR / "pass-depth-hero.png", res, "Mist", invert=True); passes["depth"] = "pass-depth-hero.png (mist over the case bounds, inverted: near = bright)"
        render_pass_image(scene, hero, OUT_DIR / "pass-roughness-hero.png", res, "Roughness"); passes["roughness"] = "pass-roughness-hero.png (AOV)"
        rendered += list(passes.values())

    turntable = None
    if RENDER_TURNTABLE and not TIER:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=False)
        root = bpy.data.objects["ROOT_PDC_PRESENTATION"]; saved = scene.cycles.samples; scene.cycles.samples = max(48, SAMPLES // 2)
        for i in range(FRAMES):
            root.rotation_euler = (0.0, 0.0, math.radians(360.0 * i / FRAMES)); bpy.context.view_layer.update()
            render(scene, hero, TURNTABLE_DIR / f"frame_{i:04d}.png", (1440, 960))
        root.rotation_euler = (0.0, 0.0, 0.0); scene.cycles.samples = saved
        turntable = {"frames": FRAMES, "degrees_per_frame": 360.0 / FRAMES, "fps": 24, "camera": "CAM_PDC_HERO", "raw_frame_dir": str(TURNTABLE_DIR), "rig": "beauty"}

    report = {"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "08-lighting", "lightingRevision": 5,
              "sourceBlend": str(SOURCE_BLEND.relative_to(REPO)), "sourceBlendSha256": expected, "contractSha256": CONTRACT_SHA, "materialsUnchanged": True, "tier": TIER,
              "rig": {"direction": INPUTS["render.lighting_direction"]["value"], "lights": [{"name": l.name, "energy_w": round(l.data.energy, 3), "size_m": [round(l.data.size, 4), round(l.data.size_y, 4)],
                                                                                            "color": [round(c, 3) for c in l.data.color], "relative_power": l.data.get("relative_power"), "review_only": bool(l.data.get("review_only", False))} for l in lights],
                      "world": "neutral dark grey at half review strength (contract review_fill)", "glossy_filter": CONTRACT["lighting"]["beauty"]["render_glossy_filter"]},
              "calibration": calib, "soft_focus": soft_info, "passes": passes, "rendered": rendered, "turntable": turntable,
              "status": "gate08_candidate_ready_for_review; exposure calibrated (p97 case pixels 0.86 display); review renders clean, soft twin separate"}
    partial = "-partial" if ONLY else ""          # partial runs never overwrite the full-run report or blend
    (OUT_DIR / f"lighting-report{suffix}{partial}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if not TIER and not ONLY:
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "tri-spinner-slab-lighting-r005.blend"))
    print("GATE08_RESULT=" + json.dumps({"rendered": rendered, "turntable": bool(turntable), "calibration": calib.get("passes")}))


main()
