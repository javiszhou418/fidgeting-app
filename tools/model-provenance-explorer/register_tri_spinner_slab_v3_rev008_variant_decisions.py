"""Persist the user's 2026-09-10 rarity-variation decisions for tri-spinner-slab-v3-cmf
(Gate 05 rev-008 study; geometry and stage revision unchanged) and attach the final
bold-aperture renders.

Decisions (AskQuestion form, exact option labels):
  aperture  = 宽：边框也换（推翻 FDB-DSP-014 禁止大面积）
  signature = 烧钛蓝（与 Standard 冷钢区分明显）
  softfocus = 留到 Gate 08 灯光定稿时再开，Gate 05–07 审阅图保持 clean
The rarity material map will enter the modeling contract at the next contract
revision (Gate 07 material contract); until then the manifest and the Design
Bible FDB-DSP-059 carry it.
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
B05 = PIPELINE_DIR / "evidence/05-blockout/rev-008"
ART = REPO / "Artifacts/TriSpinnerSlab/gate05-r008-variants"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_rev008_variant_decisions.py"
SOURCE_ID = "src.user_gate05_rev008_variation_decisions_20260910"
DECISIONS = {
    "aperture": {"choice": "bold", "wording": "宽：边框也换（推翻 FDB-DSP-014 禁止大面积）"},
    "signature": {"choice": "titanium", "wording": "烧钛蓝（与 Standard 冷钢区分明显）"},
    "softfocus": {"choice": "gate08", "wording": "留到 Gate 08 灯光定稿时再开，Gate 05–07 审阅图保持 clean"},
}
TIER_MAP = [
    {"rarity": "Standard", "tier": "steel", "accent_srgb": [0.62, 0.65, 0.69], "liner_srgb": [0.86, 0.88, 0.92]},
    {"rarity": "Refined", "tier": "copper", "accent_srgb": [0.80, 0.50, 0.30], "liner_srgb": [0.93, 0.87, 0.82]},
    {"rarity": "Signature", "tier": "titanium", "accent_srgb": [0.58, 0.66, 0.80], "liner_srgb": [0.84, 0.88, 0.96]},
    {"rarity": "Heirloom", "tier": "gold", "accent_srgb": [0.96, 0.78, 0.38], "liner_srgb": [0.90, 0.86, 0.94]},
]


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
    assert s05["revision"] == 12
    ids = []
    for aid, file, cls, note in [
        ("pdc-v3-r008-variants-final-bold-front", "gate05-r008-variants-final-bold-front.png", "rarity-variation-decided-bold-front",
         "User-decided set: bold aperture, Steel/Copper/Titanium/Gold = Standard/Refined/Signature/Heirloom."),
        ("pdc-v3-r008-variants-final-bold-hero", "gate05-r008-variants-final-bold-hero.png", "rarity-variation-decided-bold-hero", "Same set, hero camera."),
    ]:
        upsert(manifest, asset(aid, "rarity-variation-decision", ART / file, cls, note)); ids.append(aid)
    for tier in ("steel", "copper", "titanium", "gold"):
        for view in ("hero", "front"):
            p = B05 / f"cmf-preview-{view}-tier-{tier}-bold.png"
            aid = f"pdc-v3-r008-tier-{tier}-bold-{view}"
            upsert(manifest, asset(aid, "rarity-variation-still", p, f"cycles-tier-{tier}-bold-{view}", "Decided bold aperture; geometry rev-008; preview materials.")); ids.append(aid)
    for aid in ids:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)
    for aid in ("pdc-v3-r008-variants-final-bold-front", "pdc-v3-r008-variants-final-bold-hero"):
        if aid not in s05["reviewArtifactIds"]:
            s05["reviewArtifactIds"].append(aid)
    study = s05["blockoutSpec"]["rarityVariationStudy"]
    study.update({
        "decisionState": "user-decided", "decisionSourceId": SOURCE_ID, "decisions": DECISIONS, "decidedTierMap": TIER_MAP,
        "rule": "bold aperture: zones 5 (bezels), 6 (polished parts), 7 (accents/trait fills) and the zone-2 liner tint follow the rarity tier; "
                "zones 1 (crystal), 3 (sandblasted field), 4 (piano-black plates) stay constant",
        "contractFollowUp": "enter as cmf.rarity_tier_map at the next modeling-contract revision (Gate 07 material contract); rev-008 contract unchanged",
        "supersedes": "FDB-DSP-014 narrow-aperture rule for the tri-spinner-slab-v3-cmf variant only",
    })
    s05["validations"].append({"id": "rarity-variation-user-decided", "status": "pass",
                               "evidence": "bold aperture + blue-titanium Signature + soft focus deferred to Gate 08; recorded with exact option wording; "
                                           "final bold set rendered for all four tiers"})
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"]["diagnosis"] += (" 15:4x 用户选定：宽口径（边框随档换金属，推翻 FDB-DSP-014 窄口径规则，仅限本变体）、Signature 烧钛蓝、柔光留 Gate 08。"
                                              "稀有度材质映射待并入下一版 contract；几何仍 rev-008。视觉批准待确认，未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                 "variantId": VARIANT, "type": "user-decision", "stageId": "05-blockout", "revision": 12,
                                 "notes": "; ".join(f"{k}={v['wording']}" for k, v in DECISIONS.items()), "sourceId": SOURCE_ID,
                                 "decisions": DECISIONS}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids)}))


if __name__ == "__main__":
    main()
