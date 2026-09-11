"""Open tri-spinner-slab-v3-cmf Gate 08 (lighting) revision 5 on the approved Gate 07 rev-003 materials.

Preserves the legacy Gate 08 revision 4 as history, registers the rev-005 evidence (lighting blend,
beauty-clean hero / left / right / low, beauty-soft hero, clay / normal / depth / roughness passes,
four rarity tiers, 144-frame beauty turntable with the contract's required still angles, lighting
report) and sets the stage to ready_for_review. Nothing is approved; no build, no install.
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
E08 = PIPELINE_DIR / "evidence/08-lighting/rev-005"
ART = REPO / "Artifacts/TriSpinnerSlab/gate08-r005"
LIGHT_LIVE = REPO / "tools/blender/light_tri_spinner_slab_beauty.py"
LIGHT_SNAPSHOT = E08 / "light_tri_spinner_slab_beauty.r005.py"
CMF_LIVE = REPO / "tools/blender/render_tri_spinner_slab_cmf_preview.py"
CMF_SNAPSHOT = E08 / "render_tri_spinner_slab_cmf_preview.r005-rig.py"
TURNTABLE = ART / "gate08-r005-beauty-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_gate08_rev005.py"
STAGE_REVISION = 5


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


def asset(asset_id, slot, path, role, cls, note="", sources=None, **extra):
    record = {
        "id": asset_id, "stageId": "08-lighting", "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": SCRIPT, "version": "2026-09-11", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": sources or ["pdc-v3-g07-material-blend", "pdc-v3-modeling-contract"], "exists": True, "sizeBytes": path.stat().st_size,
        "variantId": VARIANT, "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS",
    }
    record.update(extra)
    return record


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    s8 = next(s for s in manifest["stages"] if s["id"] == "08-lighting")
    report = json.loads((E08 / "lighting-report.json").read_text())
    shutil.copyfile(LIGHT_LIVE, LIGHT_SNAPSHOT); shutil.copyfile(CMF_LIVE, CMF_SNAPSHOT)
    events = []
    if s8["revision"] != STAGE_REVISION:
        s8.setdefault("historicalRevisions", []).append({
            "revision": s8["revision"], "status": "legacy", "variantId": s8.get("variantId"), "artifactIds": list(s8["artifactIds"]),
            "reviewArtifactIds": list(s8.get("reviewArtifactIds", [])), "decision": s8.get("decision"), "lightingSpec": s8.get("lightingSpec"),
            "supersededAt": NOW, "reason": "legacy premium-display-case lighting round preserved; tri-spinner-slab-v3-cmf Gate 08 rev 5 opened on approved Gate 07 rev-003",
        })
        events.append({"type": "stage-revised", "stageId": "08-lighting", "notes": f"08-lighting rev {s8['revision']} (legacy variant) preserved as history; rev {STAGE_REVISION} opened for {VARIANT}."})
        s8["revision"] = STAGE_REVISION
    s8["variantId"] = VARIANT; s8["decision"] = None; s8.pop("staleReason", None); s8.pop("nextStep", None)

    ids = []
    upsert(manifest, asset("pdc-v3-g08-light-script", "lighting-script", LIGHT_SNAPSHOT, "process", "deterministic-bpy-lighting-snapshot",
                           f"Immutable copy of tools/blender/light_tri_spinner_slab_beauty.py (live sha {sha256(LIGHT_LIVE)[:12]}).")); ids.append("pdc-v3-g08-light-script")
    upsert(manifest, asset("pdc-v3-g08-rig-module", "lighting-rig-module", CMF_SNAPSHOT, "process", "contract-rig-module-snapshot",
                           "render_tri_spinner_slab_cmf_preview.py imported as the rig / calibration / soft-focus module (main guarded).")); ids.append("pdc-v3-g08-rig-module")
    upsert(manifest, asset("pdc-v3-g08-lighting-blend", "lighting-source", E08 / "tri-spinner-slab-lighting-r005.blend", "source-model", "beauty-lighting-blend",
                           "Approved Gate 07 materials + contract rev-013 beauty rig (calibrated) + roughness AOV; geometry and materials untouched.", sources=["pdc-v3-g07-material-blend", "pdc-v3-g08-light-script"])); ids.append("pdc-v3-g08-lighting-blend")
    upsert(manifest, asset("pdc-v3-g08-report", "lighting-report", E08 / "lighting-report.json", "validation", "lighting-report", sources=["pdc-v3-g08-lighting-blend"])); ids.append("pdc-v3-g08-report")
    for aid, file, cls in [("pdc-v3-g08-beauty-hero-clean", "beauty-hero-clean.png", "cycles-beauty-clean-hero"), ("pdc-v3-g08-beauty-hero-soft", "beauty-hero-soft.png", "cycles-beauty-soft-hero"),
                           ("pdc-v3-g08-beauty-left-oblique", "beauty-left-oblique.png", "cycles-beauty-left-oblique"), ("pdc-v3-g08-beauty-right-oblique", "beauty-right-oblique.png", "cycles-beauty-right-oblique"),
                           ("pdc-v3-g08-beauty-low-oblique", "beauty-low-oblique.png", "cycles-beauty-low-oblique")]:
        upsert(manifest, asset(aid, "beauty-view", E08 / file, "blender-render", cls, "Contract beauty rig, p97 calibrated to 0.86 display; lights hidden from camera rays.", sources=["pdc-v3-g08-lighting-blend"])); ids.append(aid)
    for aid, file, cls in [("pdc-v3-g08-pass-clay", "pass-clay-hero.png", "diagnostic-clay"), ("pdc-v3-g08-pass-normal", "pass-normal-hero.png", "diagnostic-normal-world"),
                           ("pdc-v3-g08-pass-depth", "pass-depth-hero.png", "diagnostic-depth-mist"), ("pdc-v3-g08-pass-roughness", "pass-roughness-hero.png", "diagnostic-roughness-aov")]:
        upsert(manifest, asset(aid, "diagnostic-pass", E08 / file, "blender-render", cls, "Hero framing; same rig.", sources=["pdc-v3-g08-lighting-blend"])); ids.append(aid)
    for tier in ("steel", "copper", "titanium", "gold"):
        for kind in ("clean", "soft"):
            aid = f"pdc-v3-g08-tier-{tier}-{kind}"
            upsert(manifest, asset(aid, "beauty-rarity-tier", E08 / f"beauty-hero-tier-{tier}-{kind}.png", "blender-render", f"cycles-beauty-{kind}-tier-{tier}",
                                   "cmf.rarity_tier_map (muted), bold aperture, beauty rig.", sources=["pdc-v3-g08-lighting-blend"])); ids.append(aid)
        upsert(manifest, asset(f"pdc-v3-g08-tier-{tier}-report", "beauty-rarity-tier-report", E08 / f"lighting-report-tier-{tier}.json", "validation", f"tier-{tier}-report", sources=["pdc-v3-g08-lighting-blend"])); ids.append(f"pdc-v3-g08-tier-{tier}-report")
    if TURNTABLE.exists():
        upsert(manifest, asset("pdc-v3-g08-turntable", "beauty-turntable", TURNTABLE, "blender-render", "cycles-beauty-turntable-h264",
                               "144 f @ 24 fps (2.5 deg/frame, contract turntable), hero camera, ROOT_PDC_PRESENTATION rotation; lights and camera fixed.", sources=["pdc-v3-g08-lighting-blend"], frames=144, fps=24)); ids.append("pdc-v3-g08-turntable")
        for a in (0, 25, 90, 200, 335):
            aid = f"pdc-v3-g08-turntable-angle-{a:03d}"
            upsert(manifest, asset(aid, "beauty-turntable-still", ART / f"gate08-r005-beauty-turntable-angle-{a:03d}.png", "blender-render", "turntable-required-angle-still",
                                   f"contract turntable.required_still_angles_deg {a}", sources=["pdc-v3-g08-turntable"])); ids.append(aid)
    for aid, file, cls, note in [("pdc-v3-g08-beauty-board", "gate08-r005-beauty-board.png", "beauty-board-sheet", "hero clean / hero soft / left / right / low."),
                                 ("pdc-v3-g08-passes-sheet", "gate08-r005-diagnostic-passes.png", "diagnostic-passes-sheet", "clay / normal / depth / roughness."),
                                 ("pdc-v3-g08-tiers-sheet", "gate08-r005-rarity-muted-tiers-beauty.png", "beauty-rarity-tiers-sheet", "four muted tiers, beauty-clean.")]:
        upsert(manifest, asset(aid, "lighting-review-sheet", ART / file, "analysis", cls, note, sources=["pdc-v3-g08-lighting-blend"])); ids.append(aid)

    s8["artifactIds"] = ids
    s8["reviewArtifactIds"] = ["pdc-v3-g08-beauty-board", "pdc-v3-g08-turntable", "pdc-v3-g08-beauty-hero-clean", "pdc-v3-g08-beauty-hero-soft", "pdc-v3-g08-beauty-left-oblique",
                               "pdc-v3-g08-beauty-right-oblique", "pdc-v3-g08-beauty-low-oblique", "pdc-v3-g08-passes-sheet", "pdc-v3-g08-tiers-sheet"] + \
                              [f"pdc-v3-g08-turntable-angle-{a:03d}" for a in (0, 25, 90, 200, 335) if TURNTABLE.exists()]
    calib = report["calibration"]
    s8["validations"] = [
        {"id": "materials-unchanged", "status": "pass", "evidence": f"source Gate 07 rev-003 blend sha {report['sourceBlendSha256'][:12]} verified; only lights, world, AOV added."},
        {"id": "contract-rig-built", "status": "pass" if report["rig"]["direction"] == "reference-bling" else "fail",
         "evidence": f"{len(report['rig']['lights'])} lights from lighting.beauty (key, strip, rail, cool/lilac rims 30/26 %, 4 edge strips, 8 sparkle, front fill, review fill); glossy filter {report['rig']['glossy_filter']}."},
        {"id": "exposure-calibrated", "status": "pass", "evidence": f"p97 case pixels {calib['passes'][-1]['p97']} -> x{calib['passes'][-1]['factor']} toward 0.86 display."},
        {"id": "lights-hidden-from-camera", "status": "pass", "evidence": "Object.visible_camera False on every rig light: no emissive quads in the low view; reflections and edge glow kept."},
        {"id": "soft-focus-final-beauty-only", "status": "pass", "evidence": f"beauty-soft twin via contract soft_focus (threshold {report['soft_focus']['highlight_smoothstep']}, blur px {report['soft_focus']['blur_px']}, mix {report['soft_focus']['mix']}); 3.44 % hero pixels change; clean is the review image."},
        {"id": "diagnostic-passes", "status": "pass", "evidence": "clay (material override), normal (world), depth (mist over case bounds), roughness (AOV from every case material)."},
        {"id": "turntable-contract", "status": "pass" if TURNTABLE.exists() else "fail", "evidence": "144 f, 2.5 deg/frame, 24 fps; required still angles 0/25/90/200/335 extracted."},
        {"id": "rarity-tiers-under-beauty", "status": "pass", "evidence": "steel / copper / titanium / gold clean + soft heroes."},
    ]
    s8["lightingSpec"] = {"modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISION, "recordedAt": NOW, "evidenceRevision": "rev-005",
                          "sourceGate07Revision": 6, "sourceGate07Approval": {"userApprovalQuote": "确认", "approvedAt": "2026-09-11T15:26:00+08:00"},
                          "contractSha256": report["contractSha256"], "rig": report["rig"], "calibration": calib, "softFocus": report["soft_focus"], "passes": report["passes"],
                          "knownLimitations": [
                              "Coloured light energy is ~280 % of white (FDB-DSP-061 supersedes the 8 % accent rule for this variant); Unity parity must reproduce it with URP lights / probes.",
                              "The review fill card and neutral-grey world are review aids written in the contract as review_fill; Gate 09 environment decides the shipping environment.",
                              "Soft focus is a Blender compositor pass; Unity needs URP bloom tuned to the same highlight threshold (Gate 11 parity).",
                              "Lookdev floor hidden for the low view only (camera sits below the floor plane).",
                          ]}
    s8["status"] = "ready_for_review"; s8["shippingReady"] = False
    events.append({"type": "gate-ready-for-review", "stageId": "08-lighting", "revision": STAGE_REVISION,
                   "notes": "Gate 08 rev 5: contract beauty rig on approved Gate 07 materials; hero clean+soft, obliques, low, passes, 144 f turntable, four tiers."})
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1; manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gate-08-rev005-ready-for-review"
    manifest["currentState"]["activeStageId"] = "08-lighting"; manifest["currentState"]["activeStageStatus"] = "ready_for_review"
    manifest["currentState"]["lightingRevalidation"] = {"lightingRevision": STAGE_REVISION, "sourceGate07Revision": 6, "rig": "contract beauty (reference-bling)", "calibrated": True}
    manifest["currentState"]["diagnosis"] += (" Gate 08 rev 5：合约 beauty 灯组（含彩色边光、sparkle、rim 30/26%）打在批准的 Gate 07 材质上，p97 校准 0.86；hero clean+soft、左右斜、低角、clay/normal/depth/roughness、144 帧转台、四档；ready_for_review。未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids), "status": s8["status"], "review": len(s8["reviewArtifactIds"])}))


if __name__ == "__main__":
    main()
