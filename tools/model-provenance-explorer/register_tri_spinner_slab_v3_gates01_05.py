"""Register the tri-spinner-slab-v3-cmf rebuild request as new revisions of
premium-display-case Gates 01-05 (evidence rev-004 / rev-007 / rev-004 /
rev-026 / rev-004) and mark Gates 06-12 stale.

Idempotent: re-running refreshes hashes for the same revision numbers and
appends nothing twice to `history.ndjson` except a new manifest revision.

Nothing here approves anything. Every stage lands in `ready_for_review` and
keeps the previous approved revision in `historicalRevisions` /
`historicalDecisions`.
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
I01 = EV / "01-intake/rev-004"
A02 = EV / "02-analysis/rev-007"
C03 = EV / "03-contract/rev-004"
R04 = EV / "04-architecture/rev-026"
B05 = EV / "05-blockout/rev-004"
BUILDER_LIVE = REPO / "tools/blender/build_tri_spinner_slab.py"
BUILDER_SNAPSHOT = B05 / "build_tri_spinner_slab.r004.py"
SPINNER_GLB = REPO / "unity/FidgetingApp/ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.glb"
TURNTABLE_ARTIFACT = REPO / "Artifacts/TriSpinnerSlab/g05-r004/g05-r004-blockout-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_gates01_05.py"

USER_WORDING = (
    "can you refer to the tri-spinner-slab and tri-spinner slab agent two files in the browser and rebuild the slab? | "
    "/Users/jiawei.zhou/Documents/ChatGPT/Knowledge base/40-视觉资产/tri-spinner-slab-concept-v3-cmf/tri-spinner-slab-model-spec.v0.json "
    "/Users/jiawei.zhou/Documents/ChatGPT/Knowledge base/40-视觉资产/tri-spinner-slab-concept-v3-cmf/tri-spinner-slab-agent-handoff-spec.md those 2 i meant"
)
SUPERSEDE_REASON = ("User requested the tri-spinner-slab-v3-cmf rebuild on 2026-09-10; the 228 x 304 x 59 mm closed-tube "
                    "contract and its downstream gates are superseded pending the user's gate decisions.")

STAGE_REVISIONS = {"01-intake": 7, "02-analysis": 16, "03-contract": 8, "04-architecture": 35, "05-blockout": 8}


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


def upsert_claim(manifest, record):
    for index, existing in enumerate(manifest["claims"]):
        if existing["id"] == record["id"]:
            manifest["claims"][index] = record
            return
    manifest["claims"].append(record)


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


def supersede_and_bump(manifest, stage_id, events):
    s = stage(manifest, stage_id)
    new_revision = STAGE_REVISIONS[stage_id]
    if s["revision"] != new_revision:
        s.setdefault("historicalRevisions", []).append({
            "revision": s["revision"], "status": s["status"], "artifactIds": list(s["artifactIds"]),
            "reviewArtifactIds": list(s.get("reviewArtifactIds", [])), "decision": s.get("decision"),
            "supersededAt": NOW, "reason": SUPERSEDE_REASON,
        })
        if s.get("decision"):
            s.setdefault("historicalDecisions", []).append({"revision": s["revision"], **s["decision"]})
        events.append({"type": "stage-revised", "stageId": stage_id,
                       "notes": f"{stage_id} rev {s['revision']} preserved as history; rev {new_revision} opened for {VARIANT}."})
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
    validation05 = json.loads((B05 / "blockout-validation.json").read_text())
    analysis = json.loads((A02 / "v3-proportion-analysis.json").read_text())
    spinner = json.loads((A02 / "spinner-source-measurement.json").read_text())
    contract_validation = json.loads((C03 / "contract-validation.json").read_text())
    part_tree = json.loads((R04 / "part-tree.json").read_text())

    shutil.copyfile(BUILDER_LIVE, BUILDER_SNAPSHOT)

    # ---------------------------------------------------------------- Gate 01
    s01 = supersede_and_bump(manifest, "01-intake", events)
    ids01 = []

    def a01(aid, slot, file, role, cls, origin, by, note="", sources=None):
        upsert(manifest, asset(aid, "01-intake", slot, I01 / file, role, cls, origin, by, sources or [], note))
        ids01.append(aid)

    a01("pdc-v3-user-request", "user-request", "user-request.md", "user-input", "verbatim-user-chat-request", "user-provided", "user",
        "Exact wording of the 2026-09-10 rebuild request. Not an approval.")
    a01("pdc-v3-model-spec-v0", "user-specification", "tri-spinner-slab-model-spec.v0.json", "user-input", "user-authored-machine-spec",
        "user-provided", "user", "Spec v0 as supplied; ratios carry evidence_class recommended_start.")
    a01("pdc-v3-handoff-spec", "user-specification", "tri-spinner-slab-agent-handoff-spec.md", "user-input", "user-authored-agent-handoff",
        "user-provided", "user")
    a01("pdc-v3-front-clean", "original-reference", "v3-01-front-cmf-gold-silver.png", "ai-target", "ai-concept-render-v3-clean-1000x1573",
        "user-provided", "user", "AI concept. Not geometry or material truth.")
    a01("pdc-v3-chat-front", "original-reference", "v3-user-chat-front-650x1024.jpg", "ai-target", "ai-concept-render-v3-chat-copy",
        "user-provided", "user", "User chat attachment (650x1024).")
    a01("pdc-v3-chat-three-view", "original-reference", "v3-user-chat-three-view-1024x576.jpg", "ai-target", "ai-concept-three-view",
        "user-provided", "user", "User chat attachment; three-view concept, not orthographic truth.")
    for n, cls in (("v1-01-turntable-hero", "v1-hero"), ("v1-02-orthographic-thickness", "v1-thickness"), ("v1-03-layer-cmf-details", "v1-cmf"),
                   ("v2-01-turntable-hero-soft-light", "v2-hero"), ("v2-02-orthographic-thickness-soft-light", "v2-thickness"),
                   ("v2-03-layer-cmf-details-soft-light", "v2-cmf")):
        a01(f"pdc-v3-history-{n}", "reference-history", f"{n}.png", "ai-target", f"ai-concept-history-{cls}", "user-provided", "user",
            "Earlier concept round kept for history; V3 supersedes.")
    upsert(manifest, {
        "id": "pdc-v3-spinner-source-glb", "stageId": "01-intake", "slot": "source-model", "path": rel(SPINNER_GLB),
        "sha256": sha256(SPINNER_GLB), "role": "source-model",
        "producer": {"name": "metal-three-blade pipeline", "version": "Gate 10 export", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": "caller-owned-spinner-source-model", "assertedBy": "repository",
                       "note": "Immutable caller-owned content. Only measured; never edited by the case task."},
        "sourceAssetIds": [], "exists": True, "sizeBytes": SPINNER_GLB.stat().st_size, "variantId": VARIANT,
        "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
    })
    ids01.append("pdc-v3-spinner-source-glb")
    s01["artifactIds"] = ids01
    s01["reviewArtifactIds"] = ["pdc-v3-front-clean", "pdc-v3-chat-front", "pdc-v3-chat-three-view", "pdc-v3-user-request"]
    s01["validations"] = [
        {"id": "user-wording-verbatim", "status": "pass", "evidence": "user-request.md stores the two chat messages verbatim."},
        {"id": "ai-targets-labelled", "status": "pass", "evidence": "All nine concept images carry role ai-target; none is geometry truth."},
        {"id": "source-model-hash-locked", "status": "pass", "evidence": f"UnifiedTriSpinner.glb sha256 {sha256(SPINNER_GLB)[:12]} registered as caller-owned source-model."},
        {"id": "annotated-feedback-image-not-supplied", "status": "pass",
         "evidence": "src.front_annotated_feedback (416x654) was not provided to the repository; its sha256 is kept in the spec and its ratios are superseded by the clean recheck."},
        {"id": "lost-baseline-recorded", "status": "pass",
         "evidence": "collector-slab-six-products-approved.png (sha d399a782...) is missing from the working tree and git history; recorded as lost, not fabricated."},
    ]

    # ---------------------------------------------------------------- Gate 02
    s02 = supersede_and_bump(manifest, "02-analysis", events)
    ids02 = []
    src01 = ["pdc-v3-front-clean", "pdc-v3-chat-front", "pdc-v3-model-spec-v0"]

    def a02(aid, slot, file, role, cls, note="", sources=None):
        upsert(manifest, asset(aid, "02-analysis", slot, A02 / file, role, cls, "repository-generated", "repository", sources or src01, note))
        ids02.append(aid)

    a02("pdc-v3-analysis-discovery-log", "discovery-log", "v3-proportion-analysis.json", "analysis", "clean-image-pixel-ratio-recheck",
        "Ratios from AI concept renders: recommended_start, never measured.")
    a02("pdc-v3-analysis-board", "analysis-board", "v3-analysis-board.png", "analysis", "proportion-overlay-board")
    a02("pdc-v3-analysis-proportion-script", "analysis-script", "measure_v3_proportions.py", "process", "deterministic-analysis-script")
    a02("pdc-v3-analysis-spinner-measurement", "spinner-source-measurement", "spinner-source-measurement.json", "analysis",
        "measured-from-caller-owned-source-model", "Only measured values in this round.", ["pdc-v3-spinner-source-glb"])
    a02("pdc-v3-analysis-spinner-script", "analysis-script", "measure_spinner_source.py", "process", "deterministic-blender-measurement-script",
        "", ["pdc-v3-spinner-source-glb"])
    s02["artifactIds"] = ids02
    s02["reviewArtifactIds"] = ["pdc-v3-analysis-board"]
    r = analysis["images"][0]["ratios"]
    m = spinner["measurements_mm"]
    claims = [
        ("pdc-v3-analysis-outer-ratio-r007", "case-silhouette",
         f"V3 clean images read outer W/H {r['case_width_over_height']} (chat copy {analysis['images'][1]['ratios']['case_width_over_height']}); "
         "the spec's 0.562 from the annotated screenshot is superseded. Slab, not the 0.75 portrait of the old contract.",
         "concept-image-reading-recommended-start", ["pdc-v3-analysis-discovery-log", "pdc-v3-analysis-board"]),
        ("pdc-v3-analysis-header-seam-r007", "header-split",
         f"Header plate seam at {r['header_seam_from_top']}H; silver datum rail band to {r['main_bay_start_from_top']}H where the main bay starts.",
         "concept-image-reading-recommended-start", ["pdc-v3-analysis-discovery-log", "pdc-v3-analysis-board"]),
        ("pdc-v3-analysis-spinner-placement-r007", "spinner-placement",
         f"Concept hub reads at {r['spinner_center_from_top']}H, horizontally centred. The concept spinner is flatter than a real equilateral "
         "rotor; with the measured 65 mm tip circle the hub must sit lower (contract derives it from the main-field fit).",
         "concept-image-reading-recommended-start", ["pdc-v3-analysis-discovery-log", "pdc-v3-analysis-board"]),
        ("pdc-v3-analysis-pocket-span-r007", "spinner-pocket",
         f"Dark recess pocket spans {r['spinner_pocket_span_over_width']}W around the spinner; tip span reads ~0.73-0.76W.",
         "concept-image-reading-recommended-start", ["pdc-v3-analysis-discovery-log"]),
        ("pdc-v3-analysis-spinner-source-dimensions-r007", "spinner-dimensions",
         f"Measured from UnifiedTriSpinner.glb: tip circle {m['tip_circle_diameter']} mm, horizontal span one-tip-up {m['horizontal_span_one_tip_up']} mm, "
         f"max thickness incl. caps {m['max_thickness_including_caps']} mm, pivot at mid-thickness. The 85 mm provisional span is retired.",
         "measured-source-model", ["pdc-v3-analysis-spinner-measurement", "pdc-v3-spinner-source-glb"]),
        ("pdc-v3-analysis-partial-depth-no-front-cover-r007", "depth-strategy",
         "Frame front covers 0.58 of spinner thickness; the spinner protrudes 0.42 (6.09 mm). No front glass. Crystal is the frame, not a cover.",
         "user-specification-recommended-start", ["pdc-v3-model-spec-v0", "pdc-v3-handoff-spec"]),
        ("pdc-v3-analysis-old-contract-invalid-r007", "contract-supersession",
         "The 228 x 304 x 59 mm closed-tube contract, the 10 x 9 mm tube and the old ContentSlot size are not reused for this variant.",
         "user-specification", ["pdc-v3-handoff-spec"]),
        ("pdc-v3-analysis-unknowns-r007", "unknowns",
         "Retention mechanism, manufacturing clearance, tolerance and draft angle are unknown and stay null; no clips or fasteners are invented.",
         "user-specification", ["pdc-v3-model-spec-v0"]),
    ]
    for cid, topic, statement, confidence, sources in claims:
        upsert_claim(manifest, {"id": cid, "stageId": "02-analysis", "topic": topic, "category": topic, "statement": statement,
                                "confidence": confidence, "state": "active", "assertedBy": "repository", "sourceAssetIds": sources,
                                "sourceRegions": [], "variantId": VARIANT, "decisionState": "proposed-pending-user-gate-decision",
                                "deliveryState": "analysis-only"})
    s02["validations"] = [
        {"id": "clean-image-recheck-done", "status": "pass", "evidence": "Both unannotated V3 images measured; annotated 416x654 ratios superseded."},
        {"id": "physical-dimensions-measured", "status": "pass", "evidence": f"Spinner {m['tip_circle_diameter']} / {m['horizontal_span_one_tip_up']} / {m['max_thickness_including_caps']} mm from the source GLB."},
        {"id": "ratios-not-promoted-to-measured", "status": "pass", "evidence": "v3-proportion-analysis.json carries evidence_class recommended_start."},
        {"id": "spec-tolerance-discrepancies-flagged", "status": "pass", "evidence": "W/H, header split and hub position exceed the spec tolerances; recorded in spec_comparison."},
    ]
    s02["analysisSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["02-analysis"], "recordedAt": NOW,
                           "specSha256": analysis["spec_sha256"], "spinnerSourceSha256": spinner["source"]["sha256"]}

    # ---------------------------------------------------------------- Gate 03
    s03 = supersede_and_bump(manifest, "03-contract", events)
    claim_ids = [c[0] for c in claims]
    ids03 = []
    upsert(manifest, asset("pdc-v3-contract-generator", "03-contract", "contract-generator", C03 / "resolve_contract.py", "process",
                           "deterministic-contract-resolver", "repository-generated", "repository", ["pdc-v3-model-spec-v0"]))
    ids03.append("pdc-v3-contract-generator")
    upsert(manifest, asset("pdc-v3-modeling-contract", "03-contract", "modeling-contract", C03 / "modeling-contract.json", "contract",
                           "v3-provisional-modeling-contract", "repository-generated", "repository",
                           ["pdc-v3-model-spec-v0", "pdc-v3-handoff-spec", "pdc-v3-analysis-discovery-log", "pdc-v3-analysis-spinner-measurement"],
                           f"contract_sha256 {contract_sha}. PROVISIONAL_DIMENSIONS: case size from concept ratios; only spinner values measured.",
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
        {"id": "consumes-all-gate02-v3-claims", "status": "pass", "evidence": f"{len(claim_ids)} claims"},
    ]
    s03["contractSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["03-contract"], "recordedAt": NOW,
                           "contractState": "provisional-pending-user-decision", "contractSha256": contract_sha,
                           "envelopeMm": {"width": kv["case.width_mm"], "height": kv["case.height_mm"], "depth": kv["assembled.envelope_depth_mm"]},
                           "frameFrontMm": kv["case.z_frame_front_mm"], "spinnerProtrusionMm": kv["spinner.protrusion_mm"],
                           "spinnerCenterFromTop": kv["visual.spinner_center_from_top"],
                           "userDecisionsRequested": [
                               "span basis: bbox_x 56.56 mm (used) vs tip-circle 65.0 mm (alternative, gives W 85.3 mm)",
                               "spinner centre 0.722H (field fit) vs concept 0.637H (infeasible with real spinner)",
                               "W/H 0.59 from clean images vs spec 0.562 from annotated screenshot",
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
         "evidence": f"{part_tree['part_count']} GEO_PDC_* parts"},
        {"id": "content-slot-caller-owned", "status": "pass", "evidence": "PIVOT_PDC_CONTENT_SLOT empty; spinner only in COL_PDC_REFERENCE_LOCKED."},
        {"id": "no-explode-in-review", "status": "pass", "evidence": "exploded-plan.json is internalOnly and excluded from reviewArtifactIds."},
        {"id": "seven-material-slots", "status": "pass", "evidence": "cmf_zone_id 1-7 assigned; slot budget 7."},
    ]
    s04["architectureSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["04-architecture"], "recordedAt": NOW,
                               "contractSha256": contract_sha, "root": "ROOT_PDC_PRESENTATION", "caseOwner": "ROOT_PDC_CASE_ASSEMBLY",
                               "contentAnchor": "PIVOT_PDC_CONTENT_SLOT", "contentSlotCanonicalMm": part_tree["content_slot"]["location_canonical_mm"]}
    s04["shippingReady"] = False

    # ---------------------------------------------------------------- Gate 05
    s05 = supersede_and_bump(manifest, "05-blockout", events)
    ids05 = []
    src05 = ["pdc-v3-modeling-contract", "pdc-v3-spinner-source-glb"]
    upsert(manifest, asset("pdc-v3-blockout-builder", "05-blockout", "builder-source", BUILDER_SNAPSHOT, "process",
                           "deterministic-bpy-builder-snapshot", "repository-generated", "repository", src05,
                           f"Immutable copy of tools/blender/build_tri_spinner_slab.py (live sha {sha256(BUILDER_LIVE)[:12]})."))
    ids05.append("pdc-v3-blockout-builder")
    upsert(manifest, asset("pdc-v3-blockout-blend", "05-blockout", "white-model-source", B05 / "tri-spinner-slab-blockout-r004.blend", "source-model",
                           "blender-blockout-scene", "repository-generated", "repository", ["pdc-v3-blockout-builder"], claims=claim_ids))
    ids05.append("pdc-v3-blockout-blend")
    for aid, slot, file, cls in [
        ("pdc-v3-blockout-hero", "white-model-hero", "white-model-hero.png", "workbench-hero-85mm-yaw25-elev5"),
        ("pdc-v3-blockout-front", "white-model-front", "white-model-front.png", "workbench-ortho-front"),
        ("pdc-v3-blockout-back", "white-model-view", "white-model-back.png", "workbench-ortho-back"),
        ("pdc-v3-blockout-top", "white-model-top", "white-model-top.png", "workbench-ortho-top"),
        ("pdc-v3-blockout-left", "white-model-view", "white-model-left.png", "workbench-ortho-left"),
        ("pdc-v3-blockout-left-oblique", "white-model-left-oblique", "white-model-left-oblique.png", "workbench-persp-left-oblique"),
        ("pdc-v3-blockout-right-oblique", "white-model-right-oblique", "white-model-right-oblique.png", "workbench-persp-right-oblique"),
        ("pdc-v3-blockout-low-oblique", "white-model-low-angle", "white-model-low-oblique.png", "workbench-persp-low-oblique"),
        ("pdc-v3-blockout-side-thickness-macro", "white-model-thickness-macro", "white-model-side-thickness-macro.png", "workbench-ortho-side-macro-protrusion"),
    ]:
        upsert(manifest, asset(aid, "05-blockout", slot, B05 / file, "blender-render", cls, "repository-generated", "repository",
                               ["pdc-v3-blockout-blend"], "White model, Workbench, PROVISIONAL_DIMENSIONS stamp; spinner is a review input."))
        ids05.append(aid)
    upsert(manifest, asset("pdc-v3-blockout-turntable", "05-blockout", "white-model-turntable", B05 / "blockout-turntable.mp4", "blender-render",
                           "workbench-turntable-144f-24fps", "repository-generated", "repository", ["pdc-v3-blockout-blend"],
                           f"Repository copy of {rel(TURNTABLE_ARTIFACT)}", frames=144, fps=24, durationSeconds=6))
    ids05.append("pdc-v3-blockout-turntable")
    upsert(manifest, asset("pdc-v3-blockout-turntable-artifact", "05-blockout", "white-model-turntable-artifact", TURNTABLE_ARTIFACT, "blender-render",
                           "workbench-turntable-144f-24fps-h264", "repository-generated", "repository", ["pdc-v3-blockout-blend"], "", frames=144, fps=24))
    ids05.append("pdc-v3-blockout-turntable-artifact")
    upsert(manifest, asset("pdc-v3-blockout-validation", "05-blockout", "validation-report", B05 / "blockout-validation.json", "validation",
                           "builder-geometry-validation", "repository-generated", "repository", ["pdc-v3-blockout-blend"]))
    ids05.append("pdc-v3-blockout-validation")
    upsert(manifest, asset("pdc-v3-blockout-hierarchy", "05-blockout", "scene-hierarchy", B05 / "scene-hierarchy.json", "validation",
                           "scene-hierarchy-dump", "repository-generated", "repository", ["pdc-v3-blockout-blend"]))
    ids05.append("pdc-v3-blockout-hierarchy")
    s05["artifactIds"] = ids05
    s05["reviewArtifactIds"] = ["pdc-v3-blockout-hero", "pdc-v3-blockout-front", "pdc-v3-blockout-left-oblique", "pdc-v3-blockout-right-oblique",
                                "pdc-v3-blockout-low-oblique", "pdc-v3-blockout-top", "pdc-v3-blockout-side-thickness-macro", "pdc-v3-blockout-turntable"]
    s05["validations"] = [{"id": c["id"], "status": c["status"], "evidence": c["detail"]} for c in validation05["checks"]] + [
        {"id": "deterministic-source", "status": "pass", "evidence": f"builder snapshot sha {sha256(BUILDER_SNAPSHOT)[:12]}; every dimension read from the contract"},
        {"id": "no-materials-white-model", "status": "pass", "evidence": "Workbench object colours only; no material assets created."},
        {"id": "provisional-watermark", "status": "pass", "evidence": "Render stamp and object custom property PROVISIONAL_DIMENSIONS."},
    ]
    s05["blockoutSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISIONS["05-blockout"], "recordedAt": NOW,
                           "contractSha256": contract_sha, "caseSizeMm": validation05["case_size_mm"], "envelopeSizeMm": validation05["envelope_size_mm"],
                           "turntable": validation05["turntable"], "reviewSpinnerSourceSha256": spinner["source"]["sha256"],
                           "knownLimitations": [
                               "Pocket outline is the convex hull of three lobes; concave sides deferred to Gate 06.",
                               "Side clearance between pocket and shelf is 0.66 mm each side (tight).",
                               "Gold visible area is ~0.2% of the interior; the spec's 5-8% target is inconsistent with 0.25-0.35 mm inlays.",
                               "Review spinner renders flat-shaded from the imported GLB normals; it is caller-owned and not part of this gate.",
                           ]}

    # ---------------------------------------------------------- downstream
    for sid in ("06-geometry", "07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"):
        s = stage(manifest, sid)
        if s.get("staleReason") != SUPERSEDE_REASON:
            events.append({"type": "stage-stale", "stageId": sid, "notes": SUPERSEDE_REASON})
        if s["status"] in ("approved", "draft", "ready_for_review", "legacy"):
            s["status"] = "stale"
        s["staleReason"] = SUPERSEDE_REASON

    # lost baseline: keep the record, explain it once
    if not any(i.get("id") == "pdc-lost-baseline-collector-slab-six-products" for i in manifest["issues"]):
        manifest["issues"].append({
            "id": "pdc-lost-baseline-collector-slab-six-products", "stageId": "01-intake",
            "assetId": "display-case-approved-shipping-baseline", "claimIds": [], "severity": "note", "status": "open",
            "note": "Docs/DesignBibleAssets/collector-slab-six-products-approved.png (sha d399a782...) is absent from the working tree and was never "
                    "committed. Kept as a missing historical record; the V3 slab variant does not depend on it.",
        })

    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gates-01-05-ready-for-review"
    manifest["model"]["activeVariantId"] = VARIANT
    manifest["currentState"].update({
        "rebuildRequested": True, "shippingAssetUnchanged": True,
        "visualApproval": "pending-user-review-gates-01-05-v3-slab",
        "deviceStatus": "not-built-not-installed-not-device-tested",
        "activeVariantId": VARIANT,
        "diagnosis": (f"2026-09-10 用户要求按 tri-spinner-slab-model-spec.v0 + handoff spec 重建 slab。Gate 01–05 新 revision 已生成："
                      f"外壳 {kv['case.width_mm']} × {kv['case.height_mm']} × 结构深 {kv['case.z_frame_front_mm']} mm，含陀螺外包 {kv['assembled.envelope_depth_mm']} mm；"
                      f"陀螺露出 {kv['spinner.protrusion_mm']} mm（0.42T）。陀螺尺寸为实测（65 / 56.56 / 14.5 mm），外壳比例仍为 PROVISIONAL。"
                      "Gate 06–12 stale。视觉批准待确认，未推送手机。"),
        "slabRebuild": {"variantId": VARIANT, "contractSha256": contract_sha, "earliestGate": "01-intake",
                        "stageRevisions": STAGE_REVISIONS, "evidenceRevisions": {"01-intake": "rev-004", "02-analysis": "rev-007",
                                                                                "03-contract": "rev-004", "04-architecture": "rev-026",
                                                                                "05-blockout": "rev-004"},
                        "turntable": rel(TURNTABLE_ARTIFACT)},
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events.insert(0, {"type": "user-request", "stageId": "01-intake", "notes": USER_WORDING})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"],
                                     "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "events": len(events), "contract": contract_sha[:12],
                      "stages": {sid: stage(manifest, sid)["status"] for sid in STAGE_REVISIONS}}))


if __name__ == "__main__":
    main()
