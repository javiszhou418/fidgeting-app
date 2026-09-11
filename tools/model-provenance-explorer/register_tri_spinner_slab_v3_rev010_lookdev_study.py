"""Attach the lighting ("bling") and muted-palette studies to tri-spinner-slab-v3-cmf
Gate 05 rev-010 (stage revision 14 unchanged; geometry and contract untouched).

User 2026-09-10 16:27: "光源是可以调整的吧？…不管是从光源还是光的颜色色相上面，好像我们这个都有点单一，
就是没有那种布灵布灵闪闪发光、光泽感的效果。"
User 2026-09-10 16:31: "这几个颜色饱和度都有点高，感觉土土的。觉得土豪的感觉。"

Both are proposals rendered with the preview script's --bling and --muted options.
Nothing is approved; adopting them changes contract lighting / cmf.rarity_tier_map
in a later contract revision.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_ID = "premium-display-case"
VARIANT = "tri-spinner-slab-v3-cmf"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
B05 = PIPELINE_DIR / "evidence/05-blockout/rev-010"
ART = REPO / "Artifacts/TriSpinnerSlab/gate05-r010"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_rev010_lookdev_study.py"
LIGHT_WORDING = ("光源是可以调整的吧？根据这个光源，按这个截图对比，我觉得不管是从光源还是光的颜色色相上面，好像我们这个都有点单一，"
                 "就是没有那种布灵布灵闪闪发光、光泽感的效果。")
PALETTE_WORDING = "然后，这几个颜色饱和度都有点高，感觉土土的。觉得土豪的感觉。"
LIGHT_SOURCE_ID = "src.user_gate05_rev010_lighting_feedback_20260910"
PALETTE_SOURCE_ID = "src.user_gate05_rev010_palette_feedback_20260910"
MUTED = {"steel": [0.62, 0.65, 0.69], "copper": [0.70, 0.58, 0.52], "titanium": [0.58, 0.63, 0.70], "gold": [0.80, 0.73, 0.60]}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value) -> str:
    if isinstance(value, list):
        return "[" + ",".join(stable_json(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{stable_json(value[k])}" for k in sorted(value)) + "}"
    return json.dumps(value, ensure_ascii=False)


def update_stage_digests(manifest) -> None:
    assets = {a["id"]: a for a in manifest["assets"]}
    previous = None
    for stage_record in manifest["stages"]:
        hashes = [assets[aid]["sha256"] for aid in stage_record["artifactIds"] if aid in assets and assets[aid].get("sha256")]
        claims = [stable_json(c) for c in manifest.get("claims", []) if c["stageId"] == stage_record["id"]]
        digest = hashlib.sha256("\n".join(sorted(hashes + claims)).encode("utf-8")).hexdigest()
        stage_record["inputDigest"] = digest if previous is None else previous
        stage_record["outputDigest"] = digest
        previous = digest


def upsert(manifest, record):
    for index, existing in enumerate(manifest["assets"]):
        if existing["id"] == record["id"]:
            manifest["assets"][index] = record
            return
    manifest["assets"].append(record)


def asset(asset_id, slot, path, cls, note):
    return {
        "id": asset_id, "stageId": "05-blockout", "slot": slot, "path": str(path.relative_to(REPO)), "sha256": sha256(path), "role": "blender-render",
        "producer": {"name": SCRIPT, "version": "2026-09-10", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"], "exists": True, "sizeBytes": path.stat().st_size, "variantId": VARIANT,
        "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS", "studyOnly": True,
    }


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    s05 = next(s for s in manifest["stages"] if s["id"] == "05-blockout")
    assert s05["revision"] == 14, s05["revision"]
    ids = []
    for aid, path, cls, note in [
        ("pdc-v3-r010-bling-proposal-sheet", ART / "gate05-r010-bling-lighting-proposal-v3-hero.png", "lighting-proposal-sheet",
         "reference screenshot / current review rig / contract-bling / reference-bling. Gate 08 direction proposal; not the contract rig."),
        ("pdc-v3-r010-bling-reference-front-macro", ART / "gate05-r010-bling-reference-front-macro.png", "lighting-proposal-front-macro", "reference-bling front + pocket lip macro."),
        ("pdc-v3-r010-palette-sheet", ART / "gate05-r010-rarity-palette-saturated-vs-muted.png", "rarity-palette-proposal-sheet",
         "rev-010 contract tier colours vs muted proposal (same hues, saturation ~40 %, value near the steel base)."),
        ("pdc-v3-r010-bling-contract-hero", B05 / "cmf-preview-hero-bling-contract.png", "cycles-bling-contract-hero",
         "thin film per contract materials[1] (pointiness+facing stand-in for COLOR0.g), rims at the 8 % cap, 8 sparkle lights, blur_glossy 0."),
        ("pdc-v3-r010-bling-contract-front", B05 / "cmf-preview-front-bling-contract.png", "cycles-bling-contract-front", "same rig, ortho front."),
        ("pdc-v3-r010-bling-reference-hero", B05 / "cmf-preview-hero-bling-reference.png", "cycles-bling-reference-hero",
         "4 backlit grazing edge strips (cyan/blue/magenta/pink, 0.8-1.3 x key), rims 30/26 %, whole-crystal film 300-650 nm, coloured sparkle, half top fill. "
         "Beyond contract lighting (8 % coloured cap) and beyond materials[1] film range; flagged."),
        ("pdc-v3-r010-bling-reference-front", B05 / "cmf-preview-front-bling-reference.png", "cycles-bling-reference-front", "same rig, ortho front."),
        ("pdc-v3-r010-bling-reference-pocket-macro", B05 / "cmf-preview-pocket-rim-macro-bling-reference.png", "cycles-bling-reference-macro", "same rig, pocket lip macro."),
    ]:
        upsert(manifest, asset(aid, "lookdev-study", path, cls, note)); ids.append(aid)
    for tier in ("copper", "titanium", "gold"):
        aid = f"pdc-v3-r010-tier-{tier}-bold-muted-hero"
        upsert(manifest, asset(aid, "rarity-palette-study", B05 / f"cmf-preview-hero-tier-{tier}-bold-muted.png", f"cycles-tier-{tier}-bold-muted-hero",
                               f"muted palette proposal accent sRGB {MUTED[tier]}; contract rev-010 value kept as the recorded map until the user decides."))
        ids.append(aid)
    for aid in ids:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)
    for aid in ("pdc-v3-r010-bling-proposal-sheet", "pdc-v3-r010-palette-sheet"):
        if aid not in s05["reviewArtifactIds"]:
            s05["reviewArtifactIds"].append(aid)
    s05["validations"].append({"id": "lighting-bling-study-attached", "status": "pass",
                               "evidence": "current rig vs contract-bling vs reference-bling rendered on rev-010; reference-bling exceeds the contract's 8 % coloured-light cap "
                                           "and the materials[1] film range; review renders unchanged; user choice pending."})
    s05["validations"].append({"id": "rarity-palette-muted-study-attached", "status": "pass",
                               "evidence": "copper/titanium/gold bold heroes re-rendered with the muted palette; contract cmf.rarity_tier_map unchanged until the user decides."})
    s05["blockoutSpec"]["lookdevStudy"] = {
        "lighting": {"sourceId": LIGHT_SOURCE_ID, "wording": LIGHT_WORDING, "variants": ["current", "contract-bling", "reference-bling"],
                     "referenceBling": {"edgeStrips": 4, "edgeStripPowerRelKey": [1.3, 0.9, 1.2, 0.8], "rimPower": {"cool": 0.30, "lilac": 0.26},
                                        "film": {"thickness_nm": [300, 650], "mask": "none"}, "sparkle": {"count": 8, "colors": ["#7FE0FF", "#FFFFFF", "#FF7AE0"]},
                                        "topFill": 0.55, "world": "neutral dark grey, half review strength"},
                     "contractBling": {"film": "materials[1] 280-380 nm, pointiness+facing mask", "rims": "8 % cap", "sparkle": 8},
                     "decisionState": "awaiting-user-choice", "stage": "Gate 08 direction"},
        "palette": {"sourceId": PALETTE_SOURCE_ID, "wording": PALETTE_WORDING, "mutedAccentSrgb": MUTED, "decisionState": "awaiting-user-choice"},
    }
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"]["diagnosis"] += (" 16:27/16:31 用户反馈：光源与色相单一、缺少闪闪发光的光泽感；四档颜色饱和度高、土。"
                                              "已出灯光三档（现状 / 合约内 bling / 对标参考图）与 muted 色板对比，均为提案，待用户选；合约与几何未改。视觉批准待确认，未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for sid, wording, kind in ((LIGHT_SOURCE_ID, LIGHT_WORDING, "lighting"), (PALETTE_SOURCE_ID, PALETTE_WORDING, "palette")):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                     "variantId": VARIANT, "type": "user-feedback", "stageId": "05-blockout", "revision": 14, "topic": kind,
                                     "notes": wording, "sourceId": sid}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids)}))


if __name__ == "__main__":
    main()
