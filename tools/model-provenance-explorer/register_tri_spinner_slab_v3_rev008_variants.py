"""Attach the rarity-tier variation study and the soft-focus A/B to the existing
tri-spinner-slab-v3-cmf Gate 05 rev-008 evidence (stage revision 12 unchanged).

Geometry is untouched; this is a CMF study rendered from the rev-008 blockout
with the preview script's --tier / --medium / --bold / --soft-focus options.
Nothing is approved; the aperture choice, the Signature colour and the
soft-focus decision stay with the user (Gate 07 / Gate 08).
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
SCRIPT = "register_tri_spinner_slab_v3_rev008_variants.py"

USER_WORDING = (
    "我觉得现在整体的结构，材质和细节比较到位了，我想根据这个创作几个variation，因为抽出来的陀螺是有稀有度区分的，"
    "所以我希望这个slab也能在颜色和金银铜材质上做出区分，所以你能做一些variation吗，能表示稀有度，然后我不确定那种柔光效果是不是应该在这个步骤加上"
)
SOURCE_ID = "src.user_gate05_rev008_variation_request_20260910"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


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


def asset(asset_id, slot, path, cls, note, sources):
    return {
        "id": asset_id, "stageId": "05-blockout", "slot": slot, "path": rel(path), "sha256": sha256(path), "role": "blender-render",
        "producer": {"name": SCRIPT, "version": "2026-09-10", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": sources, "exists": True, "sizeBytes": path.stat().st_size, "variantId": VARIANT,
        "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS", "studyOnly": True,
    }


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    s05 = next(s for s in manifest["stages"] if s["id"] == "05-blockout")
    assert s05["revision"] == 12, s05["revision"]
    src = ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"]
    ids = []
    for aid, file, cls, note in [
        ("pdc-v3-r008-variants-matrix", "gate05-r008-variants-matrix-front.png", "rarity-variation-matrix-3x4",
         "Rows: narrow (accents + liner tint only, FDB-DSP-014 as approved) / medium (polished parts take the tier metal) / bold (bezels too, "
         "would supersede FDB-DSP-014). Columns: Steel=Standard, Copper=Refined, Silver=Signature, Gold=Heirloom per PremiumDisplayCaseFoilTier order."),
        ("pdc-v3-r008-variants-accent-hero", "gate05-r008-variants-accent-tiers-hero.png", "rarity-variation-narrow-hero", "Narrow aperture, hero camera."),
        ("pdc-v3-r008-variants-medium-hero", "gate05-r008-variants-medium-tiers-hero.png", "rarity-variation-medium-hero", "Medium aperture, hero camera."),
        ("pdc-v3-r008-variants-bold-compare", "gate05-r008-variants-bold-compare-front.png", "rarity-variation-bold-compare", "Silver/Gold narrow vs bold."),
        ("pdc-v3-r008-variants-signature-alt", "gate05-r008-variants-signature-silver-vs-titanium.png", "rarity-variation-signature-alternative",
         "Signature as bright silver (shipping foil tier) vs blue titanium (FDB-DSP-014 middle-tier colour)."),
        ("pdc-v3-r008-softfocus-ab", "gate05-r008-softfocus-ab-gold-hero.png", "soft-focus-ab-beauty-clean-vs-soft",
         "contract.soft_focus applied as a compositor node group (masks crystal/mirror/spinner, smoothstep 0.9-1.8, blur 5/20 px, mix 0.10/0.025). "
         "1.07 % of pixels change by > 8/255. Gate 08 final-beauty feature; shown for the user's decision only."),
    ]:
        upsert(manifest, asset(aid, "rarity-variation-study", ART / file, cls, note, src))
        ids.append(aid)
    for tier in ("steel", "copper", "silver", "gold", "titanium"):
        for aperture in ("", "-medium", "-bold"):
            for view in ("hero", "front"):
                p = B05 / f"cmf-preview-{view}-tier-{tier}{aperture}.png"
                if p.exists():
                    aid = f"pdc-v3-r008-tier-{tier}{aperture}-{view}"
                    upsert(manifest, asset(aid, "rarity-variation-still", p, f"cycles-tier-{tier}{aperture or '-narrow'}-{view}",
                                           "Study still; geometry rev-008; SCHEME-A + REVIEW-BRIGHT preview materials.", src))
                    ids.append(aid)
    for view in ("clean", "soft"):
        p = B05 / f"cmf-preview-hero-tier-gold-{view}.png"
        upsert(manifest, asset(f"pdc-v3-r008-softfocus-gold-{view}", "soft-focus-study", p, f"beauty-{view}-gold-narrow", "contract.soft_focus required output pair.", src))
        ids.append(f"pdc-v3-r008-softfocus-gold-{view}")
    for aid in ids:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)
    for aid in ("pdc-v3-r008-variants-matrix", "pdc-v3-r008-variants-medium-hero", "pdc-v3-r008-variants-signature-alt", "pdc-v3-r008-softfocus-ab"):
        if aid not in s05["reviewArtifactIds"]:
            s05["reviewArtifactIds"].append(aid)
    s05["validations"].append({"id": "rarity-variation-study-attached", "status": "pass",
                               "evidence": "3 apertures x 4 tiers (+ blue-titanium Signature alternative) rendered from the unchanged rev-008 blockout; "
                                           "tier metals from PremiumDisplayCaseLabelPlate.foilByTier; no geometry or contract change; user choice pending."})
    s05["validations"].append({"id": "soft-focus-deferred-to-gate-08", "status": "pass",
                               "evidence": "contract.soft_focus.enabled_only_for_final_beauty = true; A/B rendered as evidence only; not applied to Gate 05 review renders."})
    s05.setdefault("blockoutSpec", {})["rarityVariationStudy"] = {
        "requestSourceId": SOURCE_ID, "wording": USER_WORDING, "tierOrder": ["steel=Standard", "copper=Refined", "silver=Signature", "gold=Heirloom"],
        "apertures": ["narrow (FDB-DSP-014 as approved)", "medium (polished parts)", "bold (bezels too; needs FDB-DSP-014 supersession)"],
        "signatureAlternative": "blue titanium", "softFocus": "Gate 08 final beauty; A/B shown", "decisionState": "awaiting-user-choice",
    }
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"]["diagnosis"] = (manifest["currentState"].get("diagnosis", "") +
        " 14:33 用户认可结构/材质/细节方向，要求按稀有度做颜色与金银铜变体：已附 3 口径 × 4 档矩阵（几何不变）与柔光 A/B；口径、Signature 颜色、柔光时机待用户选择。视觉批准待确认，未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                 "variantId": VARIANT, "type": "user-variation-request", "stageId": "05-blockout", "revision": 12,
                                 "notes": USER_WORDING, "sourceId": SOURCE_ID, "attachedAssetCount": len(ids)}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids)}))


if __name__ == "__main__":
    main()
