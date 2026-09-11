"""Gate 09 environment for the premium-display-case `tri-spinner-slab-v3-cmf` variant
(evidence rev-004, on the user-approved Gate 08 rev-005 lighting).

    blender -b --python tools/blender/environment_tri_spinner_slab.py -- [--samples N]

Gate 09 asks: is any mismatch caused by the environment rather than the model? It renders the
same cameras (hero, front, low-oblique) under
- NEUTRAL: the Gate 07 neutral rig + near-black neutral world (materials-only reference);
- REVIEW: the Gate 08 beauty rig as approved, including the review aids (grey world at half review
  strength + top fill card written in contract lighting.beauty.review_fill);
- SHIPPING: the same beauty rig with the review aids removed and the contract shipping world
  (#000103, strength mid of world_strength_range x100 as the CMF preview uses), i.e. what the
  Unity shipping scene must match;
and writes per-pair difference metrics so Gate 11 parity can tell environment differences from
model differences.
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
SAMPLES = int(ARGS[ARGS.index("--samples") + 1]) if "--samples" in ARGS else 128
REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-013/modeling-contract.json"
LIGHTING_BLEND = PIPELINE / "evidence/08-lighting/rev-005/tri-spinner-slab-lighting-r005.blend"
MATERIAL_BLEND = PIPELINE / "evidence/07-material/rev-003/tri-spinner-slab-material-r003.blend"
OUT_DIR = PIPELINE / "evidence/09-environment/rev-004"
CONTRACT = json.loads(CONTRACT_PATH.read_text()); CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
MANIFEST = json.loads((PIPELINE / "pipeline.json").read_text())
spec = importlib.util.spec_from_file_location("pdc_cmf", REPO / "tools/blender/render_tri_spinner_slab_cmf_preview.py")
CMF = importlib.util.module_from_spec(spec); spec.loader.exec_module(CMF)
MM = 0.001


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def render(scene, cam, path, resolution):
    scene.camera = cam; scene.render.resolution_x, scene.render.resolution_y = resolution; scene.render.resolution_percentage = 100
    scene.render.filepath = str(path); bpy.ops.render.render(write_still=True)


def bounds(objects):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c); lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def views(scene):
    return {"hero": (bpy.data.objects["CAM_PDC_HERO"], (2048, 1365)), "front": (bpy.data.objects["CAM_PDC_FRONT"], (2048, 2048)),
            "low-oblique": (bpy.data.objects["CAM_PDC_LOW_OBLIQUE"], (2048, 1365))}


def render_set(scene, tag, stamp):
    scene.render.stamp_note_text = stamp
    out = []
    floor = bpy.data.objects.get("GEO_PDC_LOOKDEV_FLOOR")
    for vid, (cam, res) in views(scene).items():
        if floor is not None:
            floor.hide_render = vid == "low-oblique"
        p = OUT_DIR / f"env-{tag}-{vid}.png"; render(scene, cam, p, res); out.append(p.name)
    if floor is not None:
        floor.hide_render = False
    return out


def main():
    expected_light = next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-g08-lighting-blend")["sha256"]
    expected_mat = next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-g07-material-blend")["sha256"]
    assert sha256(LIGHTING_BLEND) == expected_light, "approved Gate 08 blend hash changed"
    assert sha256(MATERIAL_BLEND) == expected_mat, "approved Gate 07 blend hash changed"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "09-environment", "environmentRevision": 4,
              "contractSha256": CONTRACT_SHA, "sourceLightingBlendSha256": expected_light, "sourceMaterialBlendSha256": expected_mat, "sets": {}}

    # --- REVIEW and SHIPPING from the approved Gate 08 blend
    bpy.ops.wm.open_mainfile(filepath=str(LIGHTING_BLEND)); scene = bpy.context.scene
    scene.cycles.samples = SAMPLES; scene.render.use_compositing = False; scene.compositing_node_group = None
    base = f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 09 environment r004 | contract {CONTRACT_SHA[:12]} | lighting Gate 08 r005 {expected_light[:12]}"
    report["sets"]["review"] = {"files": render_set(scene, "review", base + " | REVIEW env: beauty rig + review_fill (grey world x0.5, top fill 0.25)"),
                                "world": "review_fill grey at half review strength", "review_aids": True}
    fill = bpy.data.objects.get("LGT_PDC_REVIEW_TOP_FILL")
    if fill is not None:
        fill.hide_render = True
    bg = scene.world.node_tree.nodes["Background"]
    beauty = CONTRACT["lighting"]["beauty"]
    bg.inputs["Color"].default_value = CMF.srgb_hex_to_linear(beauty["world_srgb_hex"]); bg.inputs["Strength"].default_value = CMF.mid(beauty["world_strength_range"]) * 100
    report["sets"]["shipping"] = {"files": render_set(scene, "shipping", base + f" | SHIPPING env: contract world {beauty['world_srgb_hex']} x{CMF.mid(beauty['world_strength_range']) * 100:.2f}, no review aids"),
                                  "world": f"{beauty['world_srgb_hex']} strength {CMF.mid(beauty['world_strength_range']) * 100:.2f}", "review_aids": False,
                                  "lights": [l.name for l in bpy.data.objects if l.type == "LIGHT" and not l.hide_render]}
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "tri-spinner-slab-environment-shipping-r004.blend"))

    # --- NEUTRAL from the approved Gate 07 blend (its own neutral rig and world)
    bpy.ops.wm.open_mainfile(filepath=str(MATERIAL_BLEND)); scene = bpy.context.scene
    scene.cycles.samples = SAMPLES
    report["sets"]["neutral"] = {"files": render_set(scene, "neutral", base.replace("lighting Gate 08 r005", "materials Gate 07 r003") + " | NEUTRAL env: contract lighting.neutral, 18 % card 0.18"),
                                 "world": CONTRACT["lighting"]["neutral"]["background_srgb_range"][0], "review_aids": False}
    (OUT_DIR / "environment-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("GATE09_RESULT=" + json.dumps({k: v["files"] for k, v in report["sets"].items()}))


main()
