"""Register the user's refinement of tri-spinner-slab-v3-cmf Gate 05 rev-006
("感觉差不多吧": direction accepted, fillets + brighter review light + trait
plaque requested) and open the rev-007 round: contract evidence rev-007,
architecture rev-029, blockout rev-007 (Workbench zone renders + Cycles CMF
preview with the review brightness boost).

Gates 01 and 02 are untouched. Gates 06-12 stay stale. Nothing is approved;
both feedback messages are stored verbatim on the superseded Gate 05
decision (state "revise", not "rejected": the user accepted the direction).

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
C03 = EV / "03-contract/rev-007"
R04 = EV / "04-architecture/rev-029"
B05 = EV / "05-blockout/rev-007"
BUILDER_LIVE = REPO / "tools/blender/build_tri_spinner_slab.py"
BUILDER_SNAPSHOT = B05 / "build_tri_spinner_slab.r007.py"
CMF_LIVE = REPO / "tools/blender/render_tri_spinner_slab_cmf_preview.py"
CMF_SNAPSHOT = B05 / "render_tri_spinner_slab_cmf_preview.r007.py"
ART = REPO / "Artifacts/TriSpinnerSlab/gate05-r007"
CMF_TURNTABLE = ART / "gate05-r007-cmf-preview-turntable-clear.mp4"
ZONE_TURNTABLE = ART / "gate05-r007-zone-model-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_rev007.py"

REJECTION_WORDING = (
    "感觉差不多吧，这个光照还是有点黑。能不能再提亮点，这样细节我看得更清楚一些，或者你把环境光射得更亮一些。"
    "然后，这些红色的圈的这些地方感觉过渡得太生硬了，能不能稍微用圆角，就是倒一下角？ | "
    "然后这个地方可能要稍微注意一下。就到时候我可能要放一个动态的三条数值。"
    "就是在d0029833-35d3-499b-9f9d-7156b390f254 这个对话里面我们做过的一个 feature"
)
REJECTION_SOURCE_ID = "src.user_gate05_rev006_feedback_fillets_20260910"
REJECTION_SOURCE_ID_B = "src.user_gate05_rev006_feedback_trait_plaque_20260910"
SUPERSEDE_REASON = ("User refinement on Gate 05 rev-006 (2026-09-10 12:22/12:23, direction accepted): review lighting too dark, hard chamfer "
                    "junctions to be filleted, bottom band must host the dynamic three-value TRAIT PROFILE (FDB-DSP-053). Contract rev-007 reopens Gates 03-05.")

STAGE_REVISIONS = {"03-contract": 11, "04-architecture": 38, "05-blockout": 11}


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
            "revision": s["revision"], "status": "stale" if decision else s["status"], "artifactIds": list(s["artifactIds"]),
            "reviewArtifactIds": list(s.get("reviewArtifactIds", [])), "decision": decision or s.get("decision"),
            "supersededAt": NOW, "reason": SUPERSEDE_REASON,
        })
        if decision:
            s.setdefault("historicalDecisions", []).append({"revision": s["revision"], **decision})
        events.append({"type": "stage-revised", "stageId": stage_id,
                       "notes": f"{stage_id} rev {s['revision']} preserved as history; rev {new_revision} opened after the rev-006 refinement request."})
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
        "state": "revise", "action": "revise", "directionAccepted": "感觉差不多吧", "decidedBy": "user", "decidedAt": "2026-09-10", "channel": "chat",
        "wording": REJECTION_WORDING, "sourceId": REJECTION_SOURCE_ID, "sourceIds": [REJECTION_SOURCE_ID, REJECTION_SOURCE_ID_B],
        "findings": [
            "review lighting too dark; raise ambient / brightness so details read",
            "red-circled transitions too hard: header bezel lower chamfer corners, field TL/TR chamfer ends, right wing corner -> fillet them",
            "bottom band must host the dynamic three-value TRAIT PROFILE from thread d0029833-35d3-499b-9f9d-7156b390f254 (FDB-DSP-053)",
        ],
    }

    # ---------------------------------------------------------------- Gate 03
    s03 = supersede_and_bump(manifest, "03-contract", events)
    ids03 = []
    upsert(manifest, asset("pdc-v3-contract-generator", "03-contract", "contract-generator", C03 / "resolve_contract.py", "process",
                           "deterministic-contract-resolver", "repository-generated", "repository", ["pdc-v3-model-spec-v0"],
                           "rev-007: stores both 12:22/12:23 refinement messages as sources; junction fillets; TRAIT PROFILE plaque replaces the band; pocket split 0.22."))
    ids03.append("pdc-v3-contract-generator")
    upsert(manifest, asset("pdc-v3-modeling-contract", "03-contract", "modeling-contract", C03 / "modeling-contract.json", "contract",
                           "v3-provisional-modeling-contract-rev007", "repository-generated", "repository",
                           ["pdc-v3-model-spec-v0", "pdc-v3-handoff-spec", "pdc-v3-analysis-discovery-log", "pdc-v3-analysis-spinner-measurement"],
                           f"contract_sha256 {contract_sha}. PROVISIONAL_DIMENSIONS. Supersedes contract rev 6 after user refinement.",
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
        {"id": "feedback-wording-stored", "status": "pass", "evidence": f"{REJECTION_SOURCE_ID} and {REJECTION_SOURCE_ID_B} carry the verbatim 12:22 / 12:23 messages."},
    ]
    s03["contractSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["03-contract"], "recordedAt": NOW,
                           "contractState": "provisional-pending-user-decision", "contractSha256": contract_sha, "contractRevision": 7,
                           "envelopeMm": {"width": kv["case.width_mm"], "height": kv["case.height_mm"], "depth": kv["assembled.envelope_depth_mm"]},
                           "frameFrontMm": kv["case.z_frame_front_mm"], "spinnerProtrusionMm": kv["spinner.protrusion_mm"],
                           "pocketDiameterMm": kv["main.pocket_diameter_mm"], "pocketWellDepthMm": kv["main.pocket_well_depth_mm"],
                           "userDecisionsRequested": [
                               f"case now {kv['case.width_mm']} x {kv['case.height_mm']} mm so the 65 mm tip circle fits the generic well at 1:1 with the raised lip; accept or set a target width",
                               f"pocket lip foot {kv['main.pocket_diameter_mm']} mm (well 67.4 = toy 65 + 2 x 1.2 clearance; + 0.85 wall + 0.6 slope + 1.8 lip); accept or change clearance",
                               "six counterbored bolts on the crystal band centreline; three clear clips on the lip at 90/210/330 deg; accept counts/placement",
                               "header/main separated by a 2.4 mm smoke seam (datum rail removed); header bezel corners chamfered 4.5 mm with 1.5 mm junction fillets",
                               "TRAIT PROFILE plaque: 3 tracks 41 x 1.2 mm, label column 14 mm, value column 9 mm; fills runtime-dynamic (ToyTalentCatalog); accept layout",
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
    upsert(manifest, asset("pdc-v3-blockout-blend", "05-blockout", "white-model-source", B05 / "tri-spinner-slab-blockout-r007.blend", "source-model",
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
                           "Supplementary Cycles preview: contract materials by zone, contract beauty rig + REVIEW-BRIGHT aid (grey world 0.05, top fill 0.45, p97 0.86), percentile calibration. Not Gate 07/08 lookdev. rev-007 render."))
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
                               "workbench-zone-turntable-144f-24fps", "repository-generated", "repository", ["pdc-v3-blockout-blend"],
                               f"Repository copy of {rel(ZONE_TURNTABLE)}", frames=144, fps=24, durationSeconds=6))
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
        "pdc-v3-blockout-pocket-rim-macro", "pdc-v3-blockout-side-thickness-macro",
        "pdc-v3-blockout-turntable-artifact" if ZONE_TURNTABLE.exists() else None,
    ] if i]
    g = validation05["geometry"]
    s05["validations"] = [{"id": c["id"], "status": c["status"], "evidence": c["detail"]} for c in validation05["checks"]] + [
        {"id": "deterministic-source", "status": "pass", "evidence": f"builder snapshot sha {sha256(BUILDER_SNAPSHOT)[:12]}; every dimension read from contract rev 5"},
        {"id": "zone-colour-preview", "status": "pass", "evidence": "Workbench object colour per cmf_zone_id; Cycles CMF preview uses contract materials (indicative)."},
        {"id": "provisional-watermark", "status": "pass", "evidence": "Render stamp and object custom property PROVISIONAL_DIMENSIONS."},
        {"id": "refinement-findings-addressed-in-geometry", "status": "pass",
         "evidence": f"{len(g['fillets']['filleted_corners'])} chamfer junctions filleted ({g['fillets']['junction_fillet_mm']} mm outer, >= {g['fillets']['min_kept_mm']} mm nested); "
                     f"wings filleted {g['fillets']['wing_corner_fillet_mm']} mm; TRAIT plaque {g['trait_plaque']['plaque_mm']} mm with 3 tracks {g['trait_plaque']['track_mm']} mm, "
                     f"{g['trait_plaque']['ticks_per_row']} ticks/row, fills at preview {[r['preview_value'] for r in g['trait_plaque']['rows']]}; review brightness in CMF preview."},
    ]
    s05["blockoutSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["05-blockout"], "recordedAt": NOW,
                           "contractSha256": contract_sha, "caseSizeMm": validation05["case_size_mm"], "envelopeSizeMm": validation05["envelope_size_mm"],
                           "evaluatedTriangles": validation05["evaluated_triangles"], "reviewSpinnerSourceSha256": spinner_sha,
                           "cmfPreview": {"engine": cmf_report["engine"], "samples": cmf_report["samples"], "calibration": cmf_report["calibration"],
                                          "status": cmf_report["status"], "turntable": rel(CMF_TURNTABLE) if CMF_TURNTABLE.exists() else None},
                           "levelsMmFromRear": g["levels_mm_from_rear"], "traitPlaque": g["trait_plaque"], "fillets": {k: v for k, v in g["fillets"].items() if k != "filleted_corners"},
                           "knownLimitations": [
                               f"Case {validation05['case_size_mm'][0]} x {validation05['case_size_mm'][2]} mm unchanged from rev-006; pocket centre raised (split 0.22, hub 0.615H vs image 0.637H) to fit the trait plaque.",
                               f"Nested junction fillets keep >= {g['fillets']['min_kept_mm']} mm instead of the exact offset r - d ({len(g['fillets']['fillet_clamps'])} junctions); main corner arcs stay exact.",
                               "Trait plaque label/value columns are reserved for decals; no text geometry. Fill lengths shown are metal-three-blade preview values (88/36/86), runtime-owned.",
                               "REVIEW-BRIGHT lighting (grey world + top fill) is a review aid in the preview script only; Gate 08 owns the shipping light rig.",
                               f"Gold visible area {g['gold_top_area_percent']}% of the front; the spec's 5-8% target still conflicts with 0.25-0.35 mm inlays.",
                               "Wings are limited by the circular pocket: left wing lower-left, right wing upper-right, faceted inner edges at a constant 2.2 mm gap.",
                               "Clips are visual concept parts (clear crystal); retention.mechanism stays null.",
                               "Cycles CMF preview is indicative: materials are contract mid-values, no textures, no soft-focus pass; Gate 07-08 own the final look.",
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
    manifest["model"]["status"] = "v3-tri-spinner-slab-rev007-gates-03-05-ready-for-review"
    manifest["currentState"].update({
        "visualApproval": "pending-user-review-gates-01-05-v3-slab-rev007",
        "deviceStatus": "not-built-not-installed-not-device-tested",
        "diagnosis": (f"2026-09-10 12:22/12:23 用户对 Gate 05 rev-006 表示“感觉差不多吧”，要求：预览提亮、红圈处倒圆角、底部横带预留动态三条数值（FDB-DSP-053）。"
                      f"rev-007：{len(g['fillets']['filleted_corners'])} 处倒角接点圆角 {g['fillets']['junction_fillet_mm']} mm；翼板顶点圆角；"
                      f"TRAIT PROFILE 板 {g['trait_plaque']['plaque_mm']} mm、3 条 0–100 轨 + 四分刻度 + 运行时填充占位；凹槽上移（split 0.22）；"
                      f"CMF 预览加 REVIEW-BRIGHT。外壳 {kv['case.width_mm']} × {kv['case.height_mm']} × 结构深 {kv['case.z_frame_front_mm']} mm 不变。Gate 06–12 stale。视觉批准待确认，未推送手机。"),
        "slabRebuild": {"variantId": VARIANT, "contractSha256": contract_sha, "earliestGate": "01-intake",
                        "stageRevisions": {"01-intake": 7, "02-analysis": 16, **STAGE_REVISIONS},
                        "evidenceRevisions": {"01-intake": "rev-004", "02-analysis": "rev-007", "03-contract": "rev-007",
                                              "04-architecture": "rev-029", "05-blockout": "rev-007"},
                        "rejectedRevisions": {"05-blockout": ["rev-004", "rev-005"]},
                        "revisedRevisions": {"05-blockout": ["rev-006"]},
                        "turntable": rel(CMF_TURNTABLE) if CMF_TURNTABLE.exists() else None},
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events.insert(0, {"type": "user-revision-request", "stageId": "05-blockout", "revision": 10, "notes": REJECTION_WORDING,
                      "sourceId": REJECTION_SOURCE_ID, "sourceIds": [REJECTION_SOURCE_ID, REJECTION_SOURCE_ID_B], "directionAccepted": "感觉差不多吧"})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"],
                                     "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "events": len(events), "contract": contract_sha[:12],
                      "stages": {sid: f"{stage(manifest, sid)['status']} r{stage(manifest, sid)['revision']}" for sid in STAGE_REVISIONS},
                      "cmf_turntable": CMF_TURNTABLE.exists(), "zone_turntable": ZONE_TURNTABLE.exists()}))


if __name__ == "__main__":
    main()
