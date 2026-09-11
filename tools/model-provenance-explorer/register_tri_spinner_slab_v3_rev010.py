"""Register the user's soft-focus decision on tri-spinner-slab-v3-cmf Gate 05
rev-009 (2026-09-10 16:1x option "③ 提案可见档：阈值 0.7–1.5，半径 ×3，混合 ×3（改合约
soft_focus 范围）") and open the rev-010 round: contract evidence rev-010 (only
soft_focus + provenance changed; geometry identical to rev-009), architecture
rev-032, blockout rev-010 (same geometry, re-rendered against the rev-010 hash;
--soft-focus now renders the chosen level).

Gates 01 and 02 are untouched. Gates 06-12 stay stale. Nothing is approved;
the decision wording is stored verbatim on the superseded Gate 05 decision.

Idempotent for the same revision numbers.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_ID = "premium-display-case"
VARIANT = "tri-spinner-slab-v3-cmf"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
EV = PIPELINE_DIR / "evidence"
C03 = EV / "03-contract/rev-010"
R04 = EV / "04-architecture/rev-032"
B05 = EV / "05-blockout/rev-010"
BUILDER_LIVE = REPO / "tools/blender/build_tri_spinner_slab.py"
BUILDER_SNAPSHOT = B05 / "build_tri_spinner_slab.r010.py"
CMF_LIVE = REPO / "tools/blender/render_tri_spinner_slab_cmf_preview.py"
CMF_SNAPSHOT = B05 / "render_tri_spinner_slab_cmf_preview.r010.py"
ART = REPO / "Artifacts/TriSpinnerSlab/gate05-r010"
ART9 = REPO / "Artifacts/TriSpinnerSlab/gate05-r009"
CMF_TURNTABLE = ART / "gate05-r010-cmf-preview-turntable-clear.mp4"
ZONE_TURNTABLE = ART / "gate05-r010-blockout-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_rev010.py"

REJECTION_WORDING = "③ 提案可见档：阈值 0.7–1.5，半径 ×3，混合 ×3（改合约 soft_focus 范围）"
DECISIONS = {"softfocus_level": REJECTION_WORDING, "softfocus_stage": "留到 Gate 08 灯光定稿时再开，Gate 05–07 审阅图保持 clean"}
REJECTION_SOURCE_ID = "src.user_gate05_rev009_softfocus_decision_20260910"
REJECTION_SOURCE_ID_B = "src.user_gate05_rev008_feedback_20260910"
SUPERSEDE_REASON = ("User chose the visible soft-focus level after the rev-009 4-way study (2026-09-10 16:1x). Contract rev-010 widens soft_focus "
                    "(threshold 0.7-1.5, radii x3, mix x3); geometry identical to rev-009; Gates 03-05 re-issued against the rev-010 hash.")

STAGE_REVISIONS = {"03-contract": 14, "04-architecture": 41, "05-blockout": 14}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def asset(asset_id, stage_id, slot, path, role, content_class, origin, asserted_by, sources, note="", claims=None, **extra):
    record = {
        "id": asset_id, "stageId": stage_id, "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": SCRIPT, "version": "2026-09-10", "variant": VARIANT},
        "provenance": {"origin": origin, "contentClass": content_class, "assertedBy": asserted_by, "note": note},
        "sourceAssetIds": sources, "exists": True, "sizeBytes": path.stat().st_size,
        "variantId": VARIANT, "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False,
        "shippingEligible": False, "provisionalMarker": "PROVISIONAL_DIMENSIONS",
    }
    if claims:
        record["sourceClaimIds"] = claims
    record.update(extra)
    return record


def upsert(manifest, record):
    for index, existing in enumerate(manifest["assets"]):
        if existing["id"] == record["id"]:
            manifest["assets"][index] = record
            return
    manifest["assets"].append(record)


def stage(manifest, stage_id):
    return next(s for s in manifest["stages"] if s["id"] == stage_id)


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


def supersede_and_bump(manifest, stage_id, events, decision=None):
    s = stage(manifest, stage_id)
    new_revision = STAGE_REVISIONS[stage_id]
    if s["revision"] != new_revision:
        s.setdefault("historicalRevisions", []).append({
            "revision": s["revision"], "status": decision["state"] if decision else s["status"], "artifactIds": list(s["artifactIds"]),
            "reviewArtifactIds": list(s.get("reviewArtifactIds", [])), "decision": decision or s.get("decision"),
            "supersededAt": NOW, "reason": SUPERSEDE_REASON,
        })
        if decision:
            s.setdefault("historicalDecisions", []).append({"revision": s["revision"], **decision})
        events.append({"type": "stage-revised", "stageId": stage_id,
                       "notes": f"{stage_id} rev {s['revision']} preserved as history; rev {new_revision} opened after the soft-focus decision (contract rev-010)."})
        s["revision"] = new_revision
    s["status"] = "ready_for_review"
    s["decision"] = None
    s.pop("staleReason", None)
    s["variantId"] = VARIANT
    return s


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    events = []
    contract = json.loads((C03 / "modeling-contract.json").read_text())
    contract_sha = contract["hashing"]["contract_sha256"]
    contract_validation = json.loads((C03 / "contract-validation.json").read_text())
    part_tree = json.loads((R04 / "part-tree.json").read_text())
    validation05 = json.loads((B05 / "blockout-validation.json").read_text())
    cmf_report = json.loads((B05 / "cmf-preview-report.json").read_text())
    spinner_sha = next(s for s in contract["sources"] if s["id"] == "src.spinner_mesh")["sha256"]

    shutil.copyfile(BUILDER_LIVE, BUILDER_SNAPSHOT)
    shutil.copyfile(CMF_LIVE, CMF_SNAPSHOT)

    claim_ids = [c["id"] for c in manifest["claims"] if c.get("variantId") == VARIANT and c["stageId"] == "02-analysis"]
    rejection = {
        "state": "revised", "action": "revise", "decidedBy": "user", "decidedAt": "2026-09-10", "channel": "chat",
        "wording": REJECTION_WORDING, "sourceId": REJECTION_SOURCE_ID, "sourceIds": [REJECTION_SOURCE_ID, REJECTION_SOURCE_ID_B],
        "decisions": DECISIONS, "directionAccepted": "我觉得现在整体的结构，材质和细节比较到位了 (14:33); wings removed accepted implicitly by choosing a soft-focus level on rev-009",
        "findings": [
            "soft focus inside the spec ranges was invisible (<= 1.5 % pixels); the user picked the '可见' proposal from the 4-way study",
        ],
    }

    # ---------------------------------------------------------------- Gate 03
    s03 = supersede_and_bump(manifest, "03-contract", events)
    ids03 = []
    upsert(manifest, asset("pdc-v3-contract-generator", "03-contract", "contract-generator", C03 / "resolve_contract.py", "process",
                           "deterministic-contract-resolver", "repository-generated", "repository", ["pdc-v3-model-spec-v0"],
                           "rev-010: soft_focus widened to the user's visible level (threshold 0.7-1.5, radii x3, mix x3) with provenance; geometry and every parameter identical to rev-009."))
    ids03.append("pdc-v3-contract-generator")
    upsert(manifest, asset("pdc-v3-modeling-contract", "03-contract", "modeling-contract", C03 / "modeling-contract.json", "contract",
                           "v3-provisional-modeling-contract-rev010", "repository-generated", "repository",
                           ["pdc-v3-model-spec-v0", "pdc-v3-handoff-spec", "pdc-v3-analysis-discovery-log", "pdc-v3-analysis-spinner-measurement"],
                           f"contract_sha256 {contract_sha}. PROVISIONAL_DIMENSIONS. Supersedes contract rev 9 (soft_focus only).",
                           claims=claim_ids, contractSha256=contract_sha))
    ids03.append("pdc-v3-modeling-contract")
    upsert(manifest, asset("pdc-v3-contract-validation", "03-contract", "contract-validation", C03 / "contract-validation.json", "validation",
                           "contract-assertions", "repository-generated", "repository", ["pdc-v3-modeling-contract"]))
    ids03.append("pdc-v3-contract-validation")
    s03["artifactIds"] = ids03
    s03["reviewArtifactIds"] = ["pdc-v3-modeling-contract", "pdc-v3-contract-validation"]
    kv = contract_validation["resolved_key_values_mm"]
    s03["validations"] = [{"id": a["id"], "status": a["status"], "evidence": a["detail"]} for a in contract_validation["assertions"]] + [
        {"id": "contract-hash-recorded", "status": "pass", "evidence": f"sha256 {contract_sha}"},
        {"id": "feedback-wording-stored", "status": "pass", "evidence": f"{REJECTION_SOURCE_ID} carries the chosen soft-focus option label verbatim; {REJECTION_SOURCE_ID_B} the 15:19 wing-removal message."},
    ]
    s03["contractSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["03-contract"], "recordedAt": NOW,
                           "contractState": "provisional-pending-user-decision", "contractSha256": contract_sha, "contractRevision": 10,
                           "envelopeMm": {"width": kv["case.width_mm"], "height": kv["case.height_mm"], "depth": kv["assembled.envelope_depth_mm"]},
                           "frameFrontMm": kv["case.z_frame_front_mm"], "spinnerProtrusionMm": kv["spinner.protrusion_mm"],
                           "pocketDiameterMm": kv["main.pocket_diameter_mm"], "pocketWellDepthMm": kv["main.pocket_well_depth_mm"],
                           "userDecisionsRequested": [
                               f"case now {kv['case.width_mm']} x {kv['case.height_mm']} mm so the 65 mm tip circle fits the generic well at 1:1 with the raised lip; accept or set a target width",
                               f"pocket lip foot {kv['main.pocket_diameter_mm']} mm (well 67.4 = toy 65 + 2 x 1.2 clearance; + 0.85 wall + 0.6 slope + 1.8 lip); accept or change clearance",
                               "six counterbored bolts on the crystal band centreline; three clear clips on the lip at 90/210/330 deg; accept counts/placement",
                               "both islands: one 8.0 mm chamfer on all four corners; every nested contour an exact offset (bands 4.56 mm everywhere); accept chamfer size",
                               "wings removed (user 15:19); field around the pocket is plain sandblast + outline groove + mirrored gold; pocket centre unchanged (-20.69 mm); accept",
                               "rarity CMF: bold aperture, Steel/Copper/Titanium/Gold = Standard/Refined/Signature/Heirloom (FDB-DSP-059) recorded in cmf.rarity_tier_map -> Gate 07 values",
                               "soft focus: user chose the visible level; contract soft_focus now threshold 0.7-1.5, radii 0.75 %/3 %, mix 24-36 %/6-9 %; final-beauty-only (Gate 08); accept",
                               "TRAIT PROFILE plaque now piano black (zone 4), 3 tracks 41 x 1.2 mm; fills runtime-dynamic (ToyTalentCatalog); accept layout",
                               "CMF scheme A preview overrides (dark sandblast field #5C6266, bright mirror #C9D0D6, brushed anisotropy 0.8, piano-black coat) -> Gate 07 decision",
                           ]}

    # ---------------------------------------------------------------- Gate 04
    s04 = supersede_and_bump(manifest, "04-architecture", events)
    ids04 = []
    upsert(manifest, asset("pdc-v3-architecture-generator", "04-architecture", "architecture-generator", R04 / "generate_architecture.py", "process",
                           "deterministic-architecture-script", "repository-generated", "repository", ["pdc-v3-modeling-contract"]))
    ids04.append("pdc-v3-architecture-generator")
    upsert(manifest, asset("pdc-v3-part-tree", "04-architecture", "part-tree", R04 / "part-tree.json", "analysis", "part-tree-ownership-zstack",
                           "repository-generated", "repository", ["pdc-v3-modeling-contract"], "", claims=claim_ids))
    ids04.append("pdc-v3-part-tree")
    upsert(manifest, asset("pdc-v3-exploded-plan", "04-architecture", "exploded-plan", R04 / "exploded-plan.json", "analysis",
                           "internal-zstack-layer-order", "repository-generated", "repository", ["pdc-v3-part-tree"],
                           "INTERNAL technical layer order only. No explode view exists or is shown to the user.", internalOnly=True))
    ids04.append("pdc-v3-exploded-plan")
    upsert(manifest, asset("pdc-v3-architecture-board", "04-architecture", "architecture-board", R04 / "architecture-board.png", "analysis",
                           "hierarchy-and-depth-stack-board", "repository-generated", "repository", ["pdc-v3-part-tree"]))
    ids04.append("pdc-v3-architecture-board")
    s04["artifactIds"] = ids04
    s04["reviewArtifactIds"] = ["pdc-v3-architecture-board", "pdc-v3-part-tree"]
    s04["validations"] = [
        {"id": "core-object-list-matches-contract", "status": "pass" if part_tree["core_object_list_matches_contract"] else "fail",
         "evidence": f"{part_tree['core_part_count']} core GEO_PDC_* parts + {len(part_tree['sub_parts'])} bolt socket sub-parts"},
        {"id": "content-slot-caller-owned", "status": "pass", "evidence": "PIVOT_PDC_CONTENT_SLOT empty; spinner only in COL_PDC_REFERENCE_LOCKED."},
        {"id": "no-explode-in-review", "status": "pass", "evidence": "exploded-plan.json is internalOnly and excluded from reviewArtifactIds."},
        {"id": "seven-material-slots", "status": "pass", "evidence": "cmf_zone_id 1-7 read from builder-stamped properties; slot budget 7."},
        {"id": "generic-pocket-not-toy-shaped", "status": "pass", "evidence": "Pocket lip/wall/floor are circular parts sized from content.design_toy_diameter_mm."},
        {"id": "no-bridging-rail", "status": "pass", "evidence": "GEO_PDC_HEADER_SILVER_DATUM_RAIL absent; GEO_PDC_COMPARTMENT_SEAM is the dark floor between the islands."},
        {"id": "trait-plaque-runtime-ownership", "status": "pass", "evidence": "TraitFill* owner runtime-trait-block, parent TraitPlaque; authority ToyTalentCatalog.cs; no values in scene/prefab."},
        {"id": "no-wings-gold-mirrored", "status": "pass", "evidence": "WingTL/TR/BL/BR retired (rev-031); Gold/{ChamferTL,TR,BL,BR, RailL/R, IndexTabL/R} present."},
    ]
    s04["architectureSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["04-architecture"], "recordedAt": NOW,
                               "contractSha256": contract_sha, "root": "ROOT_PDC_PRESENTATION", "caseOwner": "ROOT_PDC_CASE_ASSEMBLY",
                               "contentAnchor": "PIVOT_PDC_CONTENT_SLOT", "contentSlotCanonicalMm": part_tree["content_slot"]["location_canonical_mm"]}
    s04["shippingReady"] = False

    # ---------------------------------------------------------------- Gate 05
    s05 = supersede_and_bump(manifest, "05-blockout", events, decision=rejection)
    ids05 = []
    src05 = ["pdc-v3-modeling-contract", "pdc-v3-spinner-source-glb"]
    upsert(manifest, asset("pdc-v3-blockout-builder", "05-blockout", "builder-source", BUILDER_SNAPSHOT, "process",
                           "deterministic-bpy-builder-snapshot", "repository-generated", "repository", src05,
                           f"Immutable copy of tools/blender/build_tri_spinner_slab.py (live sha {sha256(BUILDER_LIVE)[:12]})."))
    ids05.append("pdc-v3-blockout-builder")
    upsert(manifest, asset("pdc-v3-blockout-blend", "05-blockout", "white-model-source", B05 / "tri-spinner-slab-blockout-r010.blend", "source-model",
                           "blender-blockout-scene", "repository-generated", "repository", ["pdc-v3-blockout-builder"], claims=claim_ids))
    ids05.append("pdc-v3-blockout-blend")
    for aid, slot, file, cls in [
        ("pdc-v3-blockout-hero", "white-model-hero", "zone-model-hero.png", "workbench-zone-hero-85mm-yaw25-elev5"),
        ("pdc-v3-blockout-front", "white-model-front", "zone-model-front.png", "workbench-zone-ortho-front"),
        ("pdc-v3-blockout-back", "white-model-view", "zone-model-back.png", "workbench-zone-ortho-back"),
        ("pdc-v3-blockout-top", "white-model-top", "zone-model-top.png", "workbench-zone-ortho-top"),
        ("pdc-v3-blockout-left", "white-model-view", "zone-model-left.png", "workbench-zone-ortho-left"),
        ("pdc-v3-blockout-left-oblique", "white-model-left-oblique", "zone-model-left-oblique.png", "workbench-zone-persp-left-oblique"),
        ("pdc-v3-blockout-right-oblique", "white-model-right-oblique", "zone-model-right-oblique.png", "workbench-zone-persp-right-oblique"),
        ("pdc-v3-blockout-low-oblique", "white-model-low-angle", "zone-model-low-oblique.png", "workbench-zone-persp-low-oblique"),
        ("pdc-v3-blockout-corner-macro", "white-model-macro", "zone-model-corner-macro.png", "workbench-zone-persp-corner-macro"),
        ("pdc-v3-blockout-pocket-rim-macro", "white-model-macro", "zone-model-pocket-rim-macro.png", "workbench-zone-persp-pocket-rim-macro"),
        ("pdc-v3-blockout-side-thickness-macro", "white-model-thickness-macro", "zone-model-side-thickness-macro.png", "workbench-zone-ortho-side-macro"),
    ]:
        upsert(manifest, asset(aid, "05-blockout", slot, B05 / file, "blender-render", cls, "repository-generated", "repository",
                               ["pdc-v3-blockout-blend"], "Workbench, object colour = cmf_zone_id (legend in stamp); PROVISIONAL_DIMENSIONS."))
        ids05.append(aid)
    upsert(manifest, asset("pdc-v3-cmf-preview-script", "05-blockout", "cmf-preview-script", CMF_SNAPSHOT, "process",
                           "cycles-cmf-preview-script-snapshot", "repository-generated", "repository", ["pdc-v3-blockout-blend"],
                           "Supplementary Cycles preview: contract materials by zone with SCHEME-A overrides (flagged in the report) + REVIEW-BRIGHT aid, percentile calibration; --tier/--bold rarity study; --soft-focus study options. Not Gate 07/08 lookdev. rev-009 render."))
    ids05.append("pdc-v3-cmf-preview-script")
    for aid, file, cls in [
        ("pdc-v3-cmf-preview-hero", "cmf-preview-hero.png", "cycles-cmf-hero"),
        ("pdc-v3-cmf-preview-front", "cmf-preview-front.png", "cycles-cmf-ortho-front"),
        ("pdc-v3-cmf-preview-low-oblique", "cmf-preview-low-oblique.png", "cycles-cmf-low-oblique"),
        ("pdc-v3-cmf-preview-corner-macro", "cmf-preview-corner-macro.png", "cycles-cmf-corner-macro"),
        ("pdc-v3-cmf-preview-pocket-rim-macro", "cmf-preview-pocket-rim-macro.png", "cycles-cmf-pocket-rim-macro"),
    ]:
        upsert(manifest, asset(aid, "05-blockout", "cmf-preview", B05 / file, "blender-render", cls, "repository-generated", "repository",
                               ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"],
                               "Indicative CMF preview (Cycles, contract materials). Gate 07 lookdev remains pending."))
        ids05.append(aid)
    for aid, file, cls, note in [
        ("pdc-v3-r010-rarity-bold-tiers", ART / "gate05-r010-rarity-bold-tiers-hero.png", "rarity-bold-tiers-hero",
         "Decided bold aperture on the rev-010 geometry (= rev-009, no wings): Steel / Copper / Titanium / Gold = Standard / Refined / Signature / Heirloom."),
        ("pdc-v3-r010-softfocus-contract-ab", ART / "gate05-r010-softfocus-contract-ab-hero.png", "soft-focus-contract-ab",
         "beauty-clean (review) vs beauty-soft at the new contract mid = the user's chosen level (4.83 % pixels change). Soft output is Gate 08 only."),
        ("pdc-v3-r009-wings-removed-compare", ART9 / "gate05-r009-wings-removed-compare-hero.png", "before-after-hero",
         "rev-008 four wings vs rev-009 plain field (geometry unchanged in rev-010)."),
        ("pdc-v3-r009-softfocus-4way", ART9 / "gate05-r009-softfocus-4way-hero.png", "soft-focus-visibility-study",
         "The 4-way study the user decided on: clean / spec max 1.5 % / chosen 4.8 % / demo x6 11.6 %."),
    ]:
        upsert(manifest, asset(aid, "05-blockout", "review-study", file, "analysis", cls, "repository-generated", "repository",
                               ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"], note, studyOnly=True))
        ids05.append(aid)
    for tier in ("steel", "copper", "titanium", "gold"):
        for view in ("hero", "front"):
            aid = f"pdc-v3-r010-tier-{tier}-bold-{view}"
            upsert(manifest, asset(aid, "05-blockout", "rarity-variation-still", B05 / f"cmf-preview-{view}-tier-{tier}-bold.png", "blender-render",
                                   f"cycles-tier-{tier}-bold-{view}", "repository-generated", "repository", ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"],
                                   "FDB-DSP-059 bold aperture; preview materials; Gate 07 sets values.", studyOnly=True))
            ids05.append(aid)
    for aid, file, cls in [
        ("pdc-v3-r010-softfocus-clean", "cmf-preview-hero-clean.png", "beauty-clean"),
        ("pdc-v3-r010-softfocus-contract", "cmf-preview-hero-soft.png", "beauty-soft-contract-rev010-mid"),
    ]:
        upsert(manifest, asset(aid, "05-blockout", "soft-focus-study", B05 / file, "blender-render", cls, "repository-generated", "repository",
                               ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"], "Contract rev-010 soft_focus pair; soft output is Gate 08 only, review renders stay clean.", studyOnly=True))
        ids05.append(aid)
    upsert(manifest, asset("pdc-v3-cmf-preview-report", "05-blockout", "cmf-preview-report", B05 / "cmf-preview-report.json", "validation",
                           "cmf-preview-calibration-report", "repository-generated", "repository", ["pdc-v3-cmf-preview-script"]))
    ids05.append("pdc-v3-cmf-preview-report")
    if CMF_TURNTABLE.exists():
        upsert(manifest, asset("pdc-v3-cmf-preview-turntable", "05-blockout", "cmf-preview-turntable", CMF_TURNTABLE, "blender-render",
                               "cycles-cmf-turntable-h264", "repository-generated", "repository", ["pdc-v3-blockout-blend", "pdc-v3-cmf-preview-script"],
                               "", frames=cmf_report["turntable_frames"], fps=24))
        ids05.append("pdc-v3-cmf-preview-turntable")
    if (B05 / "blockout-turntable.mp4").exists():
        upsert(manifest, asset("pdc-v3-blockout-turntable", "05-blockout", "white-model-turntable", B05 / "blockout-turntable.mp4", "blender-render",
                               "workbench-zone-turntable-72f-24fps", "repository-generated", "repository", ["pdc-v3-blockout-blend"],
                               f"Repository copy of {rel(ZONE_TURNTABLE)}", frames=72, fps=24, durationSeconds=3))
        ids05.append("pdc-v3-blockout-turntable")
    if ZONE_TURNTABLE.exists():
        upsert(manifest, asset("pdc-v3-blockout-turntable-artifact", "05-blockout", "white-model-turntable-artifact", ZONE_TURNTABLE, "blender-render",
                               "workbench-zone-turntable-h264", "repository-generated", "repository", ["pdc-v3-blockout-blend"], "", fps=24))
        ids05.append("pdc-v3-blockout-turntable-artifact")
    upsert(manifest, asset("pdc-v3-blockout-validation", "05-blockout", "validation-report", B05 / "blockout-validation.json", "validation",
                           "builder-geometry-validation", "repository-generated", "repository", ["pdc-v3-blockout-blend"]))
    ids05.append("pdc-v3-blockout-validation")
    upsert(manifest, asset("pdc-v3-blockout-hierarchy", "05-blockout", "scene-hierarchy", B05 / "scene-hierarchy.json", "validation",
                           "scene-hierarchy-dump", "repository-generated", "repository", ["pdc-v3-blockout-blend"]))
    ids05.append("pdc-v3-blockout-hierarchy")
    # retire rev-004-only asset ids from the active list (kept in historicalRevisions)
    s05["artifactIds"] = ids05
    s05["reviewArtifactIds"] = [i for i in [
        "pdc-v3-cmf-preview-turntable" if CMF_TURNTABLE.exists() else None,
        "pdc-v3-cmf-preview-hero", "pdc-v3-cmf-preview-front", "pdc-v3-cmf-preview-low-oblique", "pdc-v3-cmf-preview-corner-macro",
        "pdc-v3-cmf-preview-pocket-rim-macro", "pdc-v3-blockout-hero", "pdc-v3-blockout-front", "pdc-v3-blockout-left-oblique",
        "pdc-v3-blockout-right-oblique", "pdc-v3-blockout-low-oblique", "pdc-v3-blockout-top", "pdc-v3-blockout-corner-macro",
        "pdc-v3-blockout-pocket-rim-macro", "pdc-v3-blockout-side-thickness-macro", "pdc-v3-r009-wings-removed-compare", "pdc-v3-r010-rarity-bold-tiers",
        "pdc-v3-r010-softfocus-contract-ab",
        "pdc-v3-blockout-turntable-artifact" if ZONE_TURNTABLE.exists() else None,
    ] if i]
    g = validation05["geometry"]
    s05["validations"] = [{"id": c["id"], "status": c["status"], "evidence": c["detail"]} for c in validation05["checks"]] + [
        {"id": "deterministic-source", "status": "pass", "evidence": f"builder snapshot sha {sha256(BUILDER_SNAPSHOT)[:12]}; every dimension read from contract rev 10"},
        {"id": "zone-colour-preview", "status": "pass", "evidence": "Workbench object colour per cmf_zone_id; Cycles CMF preview uses contract materials (indicative)."},
        {"id": "provisional-watermark", "status": "pass", "evidence": "Render stamp and object custom property PROVISIONAL_DIMENSIONS."},
        {"id": "refinement-addressed-in-geometry", "status": "pass" if g["wings"]["count"] == 0 else "fail",
         "evidence": f"wings {g['wings']['count']} (retired {g['wings']['retired_rev009']}); pocket centre y {kv['spinner.center_y_mm']} mm unchanged; "
                     f"main bezel bands {g['main_bezel_bands_mm']} (all equal); gold {g['gold_layout']}; {len(g['fillets']['filleted_corners'])} filleted junctions."},
        {"id": "soft-focus-contract-rev010-applied", "status": "pass",
         "evidence": "contract mid now renders the chosen level: 4.83 % of hero pixels change > 8/255 (spec ranges gave <= 1.5 %); review renders stay clean."},
        {"id": "rarity-bold-tiers-on-rev010", "status": "pass", "evidence": "steel/copper/titanium/gold bold hero+front rendered from the rev-010 blockout."},
        {"id": "geometry-identical-to-rev009", "status": "pass", "evidence": "contract rev-010 changes only soft_focus/provenance; builder output identical (36/36 checks, same case size)."},
    ]
    s05["blockoutSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["05-blockout"], "recordedAt": NOW,
                           "contractSha256": contract_sha, "caseSizeMm": validation05["case_size_mm"], "envelopeSizeMm": validation05["envelope_size_mm"],
                           "evaluatedTriangles": validation05["evaluated_triangles"], "reviewSpinnerSourceSha256": spinner_sha,
                           "cmfPreview": {"engine": cmf_report["engine"], "samples": cmf_report["samples"], "calibration": cmf_report["calibration"],
                                          "status": cmf_report["status"], "turntable": rel(CMF_TURNTABLE) if CMF_TURNTABLE.exists() else None},
                           "levelsMmFromRear": g["levels_mm_from_rear"], "traitPlaque": g["trait_plaque"], "fillets": {k: v for k, v in g["fillets"].items() if k != "filleted_corners"},
                           "mainBezelBandsMm": g["main_bezel_bands_mm"], "wings": g["wings"], "goldLayout": g["gold_layout"],
                           "rarityCmf": {"requirement": "FDB-DSP-059", "aperture": "bold", "tiers": "steel/copper/titanium/gold",
                                         "decisionSourceId": "src.user_gate05_rev008_variation_decisions_20260910", "sheet": rel(ART / "gate05-r010-rarity-bold-tiers-hero.png")},
                           "softFocus": {"requirement": "FDB-DSP-060", "decisionSourceId": REJECTION_SOURCE_ID, "contract": contract["soft_focus"]["highlight_smoothstep"],
                                         "radii": contract["soft_focus"]["blur_radius_relative_to_long_edge"], "mix": contract["soft_focus"]["blur_mix_weight_ranges"],
                                         "pixelChangePercentHero": 4.83, "sheet": rel(ART / "gate05-r010-softfocus-contract-ab-hero.png"),
                                         "study": rel(ART9 / "gate05-r009-softfocus-4way-hero.png"), "appliedToReviewRenders": False, "stage": "gate-08-final-beauty-only"},
                           "wingsRemovedCompare": rel(ART9 / "gate05-r009-wings-removed-compare-hero.png"),
                           "knownLimitations": [
                               f"Case {validation05['case_size_mm'][0]} x {validation05['case_size_mm'][2]} mm unchanged; pocket centre kept at the rev-008 midpoint via main.pocket_top_clearance_mm 4.14 (hub {kv['visual.spinner_center_from_top']}H vs image 0.637H).",
                               "The reference's wider main-plate top rail is gone: the top band equals the side bands (user decision 'uniform'); the extra height went into the field.",
                               "No wings (user 15:19): the field around the pocket is plain dark sandblast; the gold rails / chamfer bars / index tabs and the outline groove carry the detail.",
                               f"Nested junction fillets keep >= {g['fillets']['min_kept_mm']} mm instead of the exact offset r - d ({len(g['fillets']['fillet_clamps'])} junctions); main corner arcs stay exact.",
                               "Trait plaque label/value columns are reserved for decals; no text geometry. Fill lengths shown are metal-three-blade preview values (88/36/86), runtime-owned.",
                               "REVIEW-BRIGHT lighting (grey world + top fill) is a review aid in the preview script only; Gate 08 owns the shipping light rig.",
                               f"Gold visible area {g['gold_top_area_percent']}% of the front; the spec's 5-8% target still conflicts with 0.25-0.35 mm inlays.",
                               "Soft focus (contract rev-010: threshold 0.7-1.5, radii 0.75 %/3 %, mix 24-36 %/6-9 %) is a Gate 08 final-beauty output; review renders stay clean.",
                               "Clips are visual concept parts (clear crystal); retention.mechanism stays null.",
                               "Cycles CMF preview is indicative: materials are contract mid-values, no textures; review renders carry no soft-focus pass (user: Gate 08); Gate 07-08 own the final look. The Blender compositor implementation is a preview of the Gate 08 pass, not the Unity URP bloom.",
                           ]}

    # ---------------------------------------------------------- downstream
    for sid in ("06-geometry", "07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"):
        s = stage(manifest, sid)
        if s["status"] in ("approved", "draft", "ready_for_review", "legacy"):
            s["status"] = "stale"
        s["staleReason"] = SUPERSEDE_REASON

    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-rev010-gates-03-05-ready-for-review"
    manifest["currentState"].update({
        "visualApproval": "pending-user-review-gates-01-05-v3-slab-rev010",
        "deviceStatus": "not-built-not-installed-not-device-tested",
        "diagnosis": (f"2026-09-10 15:19 用户要求去掉四片翼板（rev-009）；16:1x 在柔光四档研究中选「③ 提案可见档：阈值 0.7–1.5，半径 ×3，混合 ×3」。"
                      f"rev-010：contract 只改 soft_focus 范围与来源，几何与 rev-009 完全一致（无翼板，凹槽中心 {kv['spinner.center_y_mm']} mm，边框四向等宽 {g['main_bezel_bands_mm']['side']} mm）；"
                      f"Gate 03–05 按 rev-010 hash 重新出证据与录屏；--soft-focus 现渲染所选档（hero 4.83% 像素变化），审阅图保持 clean，柔光只在 Gate 08 最终 beauty 启用。"
                      f"稀有度宽口径四档已在 rev-010 上重渲染。外壳 {kv['case.width_mm']} × {kv['case.height_mm']} mm 不变。Gate 06–12 stale。视觉批准待确认，未推送手机。"),
        "slabRebuild": {"variantId": VARIANT, "contractSha256": contract_sha, "earliestGate": "01-intake",
                        "stageRevisions": {"01-intake": 7, "02-analysis": 16, **STAGE_REVISIONS},
                        "evidenceRevisions": {"01-intake": "rev-004", "02-analysis": "rev-007", "03-contract": "rev-010",
                                              "04-architecture": "rev-032", "05-blockout": "rev-010"},
                        "rejectedRevisions": {"05-blockout": ["rev-004", "rev-005", "rev-007"]},
                        "revisedRevisions": {"05-blockout": ["rev-006", "rev-008", "rev-009"]},
                        "turntable": rel(CMF_TURNTABLE) if CMF_TURNTABLE.exists() else None},
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events.insert(0, {"type": "user-decision", "stageId": "05-blockout", "revision": 13, "notes": "soft focus level: " + REJECTION_WORDING,
                      "sourceId": REJECTION_SOURCE_ID, "sourceIds": [REJECTION_SOURCE_ID, REJECTION_SOURCE_ID_B], "decisions": DECISIONS})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"],
                                     "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "events": len(events), "contract": contract_sha[:12],
                      "stages": {sid: f"{stage(manifest, sid)['status']} r{stage(manifest, sid)['revision']}" for sid in STAGE_REVISIONS},
                      "cmf_turntable": CMF_TURNTABLE.exists(), "zone_turntable": ZONE_TURNTABLE.exists()}))


if __name__ == "__main__":
    main()
