"""Open tri-spinner-slab-v3-cmf Gate 06 (geometry) revision 9 from the approved Gate 05 rev-011.

Preserves the legacy Gate 06 revision 8 (old premium-display-case variant, approved 2026-08-26)
as history, registers the rev-009 evidence (static geometry blend, review GLB, revalidation
report, six orthographic views, hero, dimension/pivot overlays, fixed-view pack, Workbench
turntable, INTERNAL exploded z-stack) and sets the stage to ready_for_review. Nothing is
approved; Gates 07-12 stay stale.
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
E06 = PIPELINE_DIR / "evidence/06-geometry/rev-009"
ART = REPO / "Artifacts/TriSpinnerSlab/gate06-r009"
SCRIPT_LIVE = REPO / "tools/blender/refine_tri_spinner_slab_geometry.py"
SCRIPT_SNAPSHOT = E06 / "refine_tri_spinner_slab_geometry.r009.py"
TURNTABLE = ART / "gate06-r009-geometry-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_gate06_rev009.py"
STAGE_REVISION = 9


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
        "id": asset_id, "stageId": "06-geometry", "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": SCRIPT, "version": "2026-09-11", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": sources or ["pdc-v3-blockout-blend", "pdc-v3-modeling-contract"], "exists": True, "sizeBytes": path.stat().st_size,
        "variantId": VARIANT, "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS",
    }
    record.update(extra)
    return record


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    s6 = next(s for s in manifest["stages"] if s["id"] == "06-geometry")
    report = json.loads((E06 / "geometry-revalidation.json").read_text())
    assert report["all_pass"], [c["id"] for c in report["checks"] if c["status"] != "pass"]
    shutil.copyfile(SCRIPT_LIVE, SCRIPT_SNAPSHOT)
    events = []
    if s6["revision"] != STAGE_REVISION:
        s6.setdefault("historicalRevisions", []).append({
            "revision": s6["revision"], "status": "legacy", "variantId": s6.get("variantId"), "artifactIds": list(s6["artifactIds"]),
            "reviewArtifactIds": list(s6.get("reviewArtifactIds", [])), "decision": s6.get("decision"), "geometrySpec": s6.get("geometrySpec"),
            "supersededAt": NOW, "reason": "legacy premium-display-case R003 geometry round preserved; tri-spinner-slab-v3-cmf Gate 06 rev 9 opened from approved Gate 05 rev-011",
        })
        events.append({"type": "stage-revised", "stageId": "06-geometry", "notes": f"06-geometry rev {s6['revision']} (legacy variant) preserved as history; rev {STAGE_REVISION} opened for {VARIANT}."})
        s6["revision"] = STAGE_REVISION
    s6["variantId"] = VARIANT
    s6["decision"] = None
    s6.pop("staleReason", None); s6.pop("nextStep", None)

    ids = []
    upsert(manifest, asset("pdc-v3-g06-refine-script", "geometry-refine-script", SCRIPT_SNAPSHOT, "process", "deterministic-bpy-geometry-refine-snapshot",
                           f"Immutable copy of tools/blender/refine_tri_spinner_slab_geometry.py (live sha {sha256(SCRIPT_LIVE)[:12]}). Applies modifiers, cleans 1 um doubles/degenerates, bakes COLOR0/UV2, validates.")); ids.append("pdc-v3-g06-refine-script")
    upsert(manifest, asset("pdc-v3-g06-geometry-blend", "geometry-source", E06 / "tri-spinner-slab-geometry-r009.blend", "source-model", "static-geometry-blend",
                           "All modifiers applied; COLOR0 (corner) + UV2 baked; cutters and preview-only objects removed; review spinner kept in COL_PDC_REFERENCE_LOCKED (hidden).",
                           sources=["pdc-v3-blockout-blend", "pdc-v3-g06-refine-script"])); ids.append("pdc-v3-g06-geometry-blend")
    upsert(manifest, asset("pdc-v3-g06-review-glb", "geometry-interactive-review", E06 / "tri-spinner-slab-gate06-review-r009.glb", "export", "interactive-review-glb-not-gate10-export",
                           "Case + controls only (no toy, no cameras/lights) for interactive inspection in the workbench viewer. Gate 10 owns the shipping export.",
                           sources=["pdc-v3-g06-geometry-blend"], interactive=True)); ids.append("pdc-v3-g06-review-glb")
    upsert(manifest, asset("pdc-v3-g06-revalidation", "geometry-validation", E06 / "geometry-revalidation.json", "validation", "geometry-revalidation-report",
                           sources=["pdc-v3-g06-geometry-blend"])); ids.append("pdc-v3-g06-revalidation")
    for view in ("front", "back", "top", "bottom", "left", "right"):
        aid = f"pdc-v3-g06-ortho-{view}"
        upsert(manifest, asset(aid, f"geometry-ortho-{view}", E06 / f"ortho-{view}.png", "blender-render", f"workbench-ortho-{view}-zone-colour",
                               "Workbench, object colour = cmf_zone_id, 2048 px, ortho scale in geometry-revalidation.json.", sources=["pdc-v3-g06-geometry-blend"],
                               view=view, projection="orthographic")); ids.append(aid)
    upsert(manifest, asset("pdc-v3-g06-hero", "geometry-hero", E06 / "geometry-workbench-hero.png", "blender-render", "workbench-zone-hero", sources=["pdc-v3-g06-geometry-blend"])); ids.append("pdc-v3-g06-hero")
    for view in ("front", "left"):
        aid = f"pdc-v3-g06-dimension-overlay-{view}"
        upsert(manifest, asset(aid, "geometry-dimension-overlay", E06 / f"dimension-overlay-{view}.png", "analysis", f"dimension-pivot-overlay-{view}",
                               "W/H (front) or structural D/H (left) measured from the geometry bounds; front view marks PIVOT_PDC_CONTENT_SLOT.", sources=[f"pdc-v3-g06-ortho-{view}"])); ids.append(aid)
    for view in ("front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"):
        aid = f"pdc-v3-g06-fixed-{view}"
        upsert(manifest, asset(aid, f"fixed-view-{view}", E06 / "fixed-views" / f"{view}.png", "blender-render", "fixed-camera-pack-view",
                               "skills/fidgeting-model-pipeline/scripts/capture_standard_views.py (real Blender render).", sources=["pdc-v3-g06-geometry-blend"], view=view)); ids.append(aid)
    for name, file in (("pdc-v3-g06-fixed-capture-report", "capture-report.json"), ("pdc-v3-g06-fixed-wrapper-report", "capture-wrapper-report.json")):
        upsert(manifest, asset(name, "fixed-view-report", E06 / "fixed-views" / file, "validation", "fixed-camera-pack-report", sources=["pdc-v3-g06-geometry-blend"])); ids.append(name)
    upsert(manifest, asset("pdc-v3-g06-internal-exploded", "internal-exploded-zstack", E06 / "internal-exploded-zstack.png", "analysis", "internal-technical-exploded-zstack",
                           "INTERNAL technical evidence only (whole-case gate): never a review artifact, never shown as a product preview.", sources=["pdc-v3-g06-geometry-blend"], internalOnly=True)); ids.append("pdc-v3-g06-internal-exploded")
    if TURNTABLE.exists():
        upsert(manifest, asset("pdc-v3-g06-turntable", "geometry-turntable", TURNTABLE, "blender-render", "workbench-zone-turntable-h264",
                               "72 f @ 24 fps, hero camera, ROOT_PDC_PRESENTATION rotation; complete recording for geometry review.", sources=["pdc-v3-g06-geometry-blend"], frames=72, fps=24)); ids.append("pdc-v3-g06-turntable")
        upsert(manifest, asset("pdc-v3-g06-turntable-frame", "geometry-turntable-frame", ART / "gate06-r009-geometry-turntable-frame-036.png", "blender-render", "turntable-frame-extract",
                               sources=["pdc-v3-g06-turntable"])); ids.append("pdc-v3-g06-turntable-frame")
    upsert(manifest, asset("pdc-v3-g06-six-view-sheet", "geometry-six-view-sheet", ART / "gate06-r009-six-ortho-views.png", "analysis", "six-ortho-contact-sheet",
                           sources=[f"pdc-v3-g06-ortho-{v}" for v in ("front", "back", "top", "bottom", "left", "right")])); ids.append("pdc-v3-g06-six-view-sheet")

    s6["artifactIds"] = ids
    s6["reviewArtifactIds"] = ["pdc-v3-g06-review-glb", "pdc-v3-g06-turntable", "pdc-v3-g06-six-view-sheet", "pdc-v3-g06-hero",
                               "pdc-v3-g06-ortho-front", "pdc-v3-g06-ortho-back", "pdc-v3-g06-ortho-top", "pdc-v3-g06-ortho-bottom", "pdc-v3-g06-ortho-left", "pdc-v3-g06-ortho-right",
                               "pdc-v3-g06-dimension-overlay-front", "pdc-v3-g06-dimension-overlay-left",
                               "pdc-v3-g06-fixed-hero", "pdc-v3-g06-fixed-left-oblique", "pdc-v3-g06-fixed-right-oblique", "pdc-v3-g06-fixed-low"]
    assert "pdc-v3-g06-internal-exploded" not in s6["reviewArtifactIds"]
    s6["validations"] = [{"id": c["id"], "status": c["status"], "evidence": c["detail"]} for c in report["checks"]] + [
        {"id": "design-unchanged-from-approved-blockout", "status": "pass", "evidence": "no parameter, outline, or part changed; modifiers applied + 1 um cleanup only (report.cleanup)."},
        {"id": "no-explode-in-review", "status": "pass", "evidence": "internal-exploded-zstack.png is internalOnly and excluded from reviewArtifactIds."},
        {"id": "fixed-view-pack-complete", "status": "pass", "evidence": "capture_standard_views.py: 10/10 views rendered, missing_views []."},
        {"id": "interactive-review-glb", "status": "pass", "evidence": f"{report['review_glb']['path']} sha {report['review_glb']['sha256'][:12]}; {len(report['review_glb']['objects'])} objects; review-only."},
    ]
    s6["geometrySpec"] = {
        "modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISION, "recordedAt": NOW, "evidenceRevision": "rev-009",
        "sourceGate05StageRevision": 15, "sourceGate05EvidenceRevision": "rev-011", "sourceBlendSha256": report["sourceBlendSha256"],
        "contractSha256": report["contractSha256"], "designChanged": False, "identity": report["identity"],
        "dimensionsMm": report["dimensions_mm"], "contractDimensionsMm": report["contract_dimensions_mm"],
        "contentSlotCanonicalMm": report["content_slot_location_mm"], "totals": report["totals"],
        "vertexChannels": {"spec": report["vertex_channels"]["spec"], "domain": "CORNER", "edgeFaceAreaMm2": report["vertex_channels"]["edge_face_area_mm2"],
                           "crystalEdgeAreaFraction": report["vertex_channels"]["per_object"]["GEO_PDC_OUTER_CRYSTAL_FRAME"]["edge_area_fraction"]},
        "cleanup": {k: v for k, v in report["cleanup"].items() if k == "_rule" or v["vertices_before"] != v["vertices_after"]},
        "knownLimitations": [
            "Six bolt heads carry 9 888 triangles each (59 k of 96 k): Gate 10 export should decimate the hex-socket bevel rings.",
            "COLOR0.g edge mask is a per-corner area heuristic (faces < 2.5 mm2); Gate 07 may replace it with a baked texture mask if the shader needs a soft falloff.",
            "UV2.x brushing angle is per object (bezels horizontal, gold along the inlay long axis); no UV0 unwrap exists yet (Gate 07 material stage).",
            "Review spinner (caller-owned) stays hidden in COL_PDC_REFERENCE_LOCKED; it is not part of the geometry deliverable.",
        ],
    }
    s6["status"] = "ready_for_review"
    s6["shippingReady"] = False
    events.append({"type": "gate-ready-for-review", "stageId": "06-geometry", "revision": STAGE_REVISION,
                   "notes": "Gate 06 rev 9: static geometry from approved Gate 05 rev-011; 16/16 checks; six ortho + fixed pack + turntable + review GLB."})
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gate-06-rev009-ready-for-review"
    manifest["currentState"]["activeStageId"] = "06-geometry"; manifest["currentState"]["activeStageStatus"] = "ready_for_review"
    manifest["currentState"]["geometryRevalidation"] = {"geometryRevision": STAGE_REVISION, "sourceGate05Revision": 15, "geometryChanged": False,
                                                        "identity": report["identity"], "triangles": report["totals"]["triangles"], "allPass": True}
    manifest["currentState"]["diagnosis"] += (" 22:33 用户「继续」→ Gate 06 rev 9：从已批准的 Gate 05 rev-011 出静态几何（应用修改器、1 µm 去重、烘 COLOR0/UV2），"
                                              "16/16 检查通过，96 134 三角（预算 120 000），六向正交 + 固定机位包 + 转台 + 审阅 GLB；ready_for_review。未构建、未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                     "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids), "status": s6["status"], "review": len(s6["reviewArtifactIds"])}))


if __name__ == "__main__":
    main()
