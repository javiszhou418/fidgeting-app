"""Open tri-spinner-slab-v3-cmf Gate 07 (material) revision 6 from the approved Gate 06 rev-011 geometry.

Preserves the legacy Gate 07 revision 5 (old premium-display-case variant) as history, registers the
rev-003 evidence (material blend, neutral-rig board: hero / front / header-macro / main-cmf-macro /
crystal-bevel-macro / pocket-rim-macro, material-id maps, four rarity tiers, header label decal + layout,
neutral turntable, revalidation report) and sets the stage to ready_for_review. Nothing is approved and
no material is registered in the MaterialLibrary until the user approves.
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
E07 = PIPELINE_DIR / "evidence/07-material/rev-003"
ART = REPO / "Artifacts/TriSpinnerSlab/gate07-r003"
LOOKDEV_LIVE = REPO / "tools/blender/lookdev_tri_spinner_slab_materials.py"
LOOKDEV_SNAPSHOT = E07 / "lookdev_tri_spinner_slab_materials.r003.py"
DECAL_LIVE = REPO / "tools/blender/make_tri_spinner_slab_label_decal.py"
DECAL_SNAPSHOT = E07 / "make_tri_spinner_slab_label_decal.r003.py"
TURNTABLE = ART / "gate07-r003-material-neutral-turntable-clear.mp4"
NOW = datetime.now(timezone.utc).isoformat()
SCRIPT = "register_tri_spinner_slab_v3_gate07_rev003.py"
STAGE_REVISION = 6


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
        "id": asset_id, "stageId": "07-material", "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": SCRIPT, "version": "2026-09-11", "variant": VARIANT},
        "provenance": {"origin": "repository-generated", "contentClass": cls, "assertedBy": "repository", "note": note},
        "sourceAssetIds": sources or ["pdc-v3-g06-geometry-blend", "pdc-v3-modeling-contract"], "exists": True, "sizeBytes": path.stat().st_size,
        "variantId": VARIANT, "wholeAssembledCaseOnly": True, "explodeEligible": False, "toyPrizeBundled": False, "shippingEligible": False,
        "provisionalMarker": "PROVISIONAL_DIMENSIONS",
    }
    record.update(extra)
    return record


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    s7 = next(s for s in manifest["stages"] if s["id"] == "07-material")
    report = json.loads((E07 / "material-revalidation.json").read_text())
    assert report["calibration"]["within_tolerance"], report["calibration"]
    shutil.copyfile(LOOKDEV_LIVE, LOOKDEV_SNAPSHOT); shutil.copyfile(DECAL_LIVE, DECAL_SNAPSHOT)
    events = []
    if s7["revision"] != STAGE_REVISION:
        s7.setdefault("historicalRevisions", []).append({
            "revision": s7["revision"], "status": "legacy", "variantId": s7.get("variantId"), "artifactIds": list(s7["artifactIds"]),
            "reviewArtifactIds": list(s7.get("reviewArtifactIds", [])), "decision": s7.get("decision"), "materialSpec": s7.get("materialSpec"),
            "supersededAt": NOW, "reason": "legacy premium-display-case material round preserved; tri-spinner-slab-v3-cmf Gate 07 rev 6 opened from approved Gate 06 rev-011",
        })
        events.append({"type": "stage-revised", "stageId": "07-material", "notes": f"07-material rev {s7['revision']} (legacy variant) preserved as history; rev {STAGE_REVISION} opened for {VARIANT}."})
        s7["revision"] = STAGE_REVISION
    s7["variantId"] = VARIANT; s7["decision"] = None; s7.pop("staleReason", None); s7.pop("nextStep", None)

    ids = []
    upsert(manifest, asset("pdc-v3-g07-lookdev-script", "material-lookdev-script", LOOKDEV_SNAPSHOT, "process", "deterministic-bpy-lookdev-snapshot",
                           f"Immutable copy of tools/blender/lookdev_tri_spinner_slab_materials.py (live sha {sha256(LOOKDEV_LIVE)[:12]}).")); ids.append("pdc-v3-g07-lookdev-script")
    upsert(manifest, asset("pdc-v3-g07-decal-script", "label-decal-script", DECAL_SNAPSHOT, "process", "label-decal-generator-snapshot",
                           "Pillow + Oxanium variable font; placeholder copy from the V3 concept; runtime-owned values.")); ids.append("pdc-v3-g07-decal-script")
    upsert(manifest, asset("pdc-v3-g07-label-decal", "header-label-decal", E07 / "header-label-decal.png", "source-model", "header-label-decal-rgba",
                           "TRI-SPINNER / SERIES 01 / TITANIUM / rule / spec grid. Oxanium SemiBold/Medium, native kerning, no tracking (FDB-GAC-009 type rule). PLACEHOLDER copy.",
                           sources=["pdc-v3-g07-decal-script"])); ids.append("pdc-v3-g07-label-decal")
    upsert(manifest, asset("pdc-v3-g07-label-layout", "header-label-layout", E07 / "header-label-decal.json", "validation", "header-label-layout-mm", sources=["pdc-v3-g07-decal-script"])); ids.append("pdc-v3-g07-label-layout")
    upsert(manifest, asset("pdc-v3-g07-material-blend", "material-source", E07 / "tri-spinner-slab-material-r003.blend", "source-model", "lookdev-material-blend",
                           "Approved Gate 06 rev-011 geometry + Gate 07 materials + neutral rig; geometry untouched.", sources=["pdc-v3-g06-geometry-blend", "pdc-v3-g07-lookdev-script", "pdc-v3-g07-label-decal"])); ids.append("pdc-v3-g07-material-blend")
    upsert(manifest, asset("pdc-v3-g07-revalidation", "material-validation", E07 / "material-revalidation.json", "validation", "material-revalidation-report", sources=["pdc-v3-g07-material-blend"])); ids.append("pdc-v3-g07-revalidation")
    for view in ("hero", "front", "header-macro", "main-cmf-macro", "crystal-bevel-macro", "pocket-rim-macro"):
        aid = f"pdc-v3-g07-board-{view}"
        upsert(manifest, asset(aid, f"material-board-{view}", E07 / f"material-{view}.png", "blender-render", f"cycles-neutral-material-{view}",
                               "Contract NEUTRAL rig, 18 % grey card calibrated to 0.18 scene-linear; AgX base contrast.", sources=["pdc-v3-g07-material-blend"], view=view)); ids.append(aid)
    for view in ("hero", "front"):
        aid = f"pdc-v3-g07-material-id-{view}"
        upsert(manifest, asset(aid, f"material-id-{view}", E07 / f"material-id-{view}.png", "blender-render", f"workbench-material-id-{view}",
                               "Flat zone colours for the material-boundary check.", sources=["pdc-v3-g07-material-blend"], view=view)); ids.append(aid)
    for tier in ("steel", "copper", "titanium", "gold"):
        aid = f"pdc-v3-g07-tier-{tier}-hero"
        upsert(manifest, asset(aid, "material-rarity-tier", E07 / f"material-hero-tier-{tier}.png", "blender-render", f"cycles-neutral-tier-{tier}-hero",
                               "cmf.rarity_tier_map (muted) under the neutral rig, bold aperture.", sources=["pdc-v3-g07-material-blend"])); ids.append(aid)
        upsert(manifest, asset(f"pdc-v3-g07-tier-{tier}-report", "material-rarity-tier-report", E07 / f"material-revalidation-tier-{tier}.json", "validation", f"tier-{tier}-report",
                               sources=["pdc-v3-g07-material-blend"])); ids.append(f"pdc-v3-g07-tier-{tier}-report")
    if TURNTABLE.exists():
        upsert(manifest, asset("pdc-v3-g07-turntable", "material-turntable", TURNTABLE, "blender-render", "cycles-neutral-material-turntable-h264",
                               "72 f @ 24 fps, hero camera, neutral rig; complete recording for material review.", sources=["pdc-v3-g07-material-blend"], frames=72, fps=24)); ids.append("pdc-v3-g07-turntable")
        upsert(manifest, asset("pdc-v3-g07-turntable-frame", "material-turntable-frame", ART / "gate07-r003-material-neutral-turntable-frame-036.png", "blender-render", "turntable-frame-extract",
                               sources=["pdc-v3-g07-turntable"])); ids.append("pdc-v3-g07-turntable-frame")
    for aid, file, cls, note in [
        ("pdc-v3-g07-board-sheet", "gate07-r003-material-board.png", "material-board-sheet", "hero + front + four macros."),
        ("pdc-v3-g07-id-vs-render", "gate07-r003-material-id-vs-render.png", "material-id-vs-render-sheet", "zone map next to the material render for the boundary check."),
        ("pdc-v3-g07-tiers-sheet", "gate07-r003-rarity-muted-tiers-neutral.png", "material-rarity-tiers-sheet", "four muted tiers under the neutral rig."),
    ]:
        upsert(manifest, asset(aid, "material-review-sheet", ART / file, "analysis", cls, note, sources=["pdc-v3-g07-material-blend"])); ids.append(aid)

    s7["artifactIds"] = ids
    s7["reviewArtifactIds"] = ["pdc-v3-g07-board-sheet", "pdc-v3-g07-turntable", "pdc-v3-g07-board-hero", "pdc-v3-g07-board-front", "pdc-v3-g07-board-header-macro",
                               "pdc-v3-g07-board-main-cmf-macro", "pdc-v3-g07-board-crystal-bevel-macro", "pdc-v3-g07-board-pocket-rim-macro",
                               "pdc-v3-g07-id-vs-render", "pdc-v3-g07-tiers-sheet", "pdc-v3-g07-label-decal"]
    s7["validations"] = [
        {"id": "geometry-unchanged", "status": "pass", "evidence": f"source Gate 06 rev-011 blend sha {report['sourceBlendSha256'][:12]} verified before lookdev; no mesh edited."},
        {"id": "neutral-rig-calibrated", "status": "pass", "evidence": f"18 % card {report['calibration']['passes'][-1]['card_luminance']} -> factor {report['calibration']['passes'][-1]['factor']}; energies {report['calibration']['energies_w']}."},
        {"id": "seven-zones-materialised", "status": "pass" if len(report["materials_by_zone"]) == 7 else "fail", "evidence": ", ".join(f"{k}:{v['material']}" for k, v in sorted(report["materials_by_zone"].items()))},
        {"id": "surface-detail-present", "status": "pass", "evidence": "brushing (anisotropy 0.8 + streak roughness ±0.015, pitch 0.06 mm), sandblast bump (feature 0.13 mm, 0.0105 mm), whole-crystal thin film 300-650 nm, piano-black coat, gold anisotropy."},
        {"id": "header-label-decal", "status": "pass", "evidence": "Oxanium placeholder label mapped planar on GEO_PDC_HEADER_GRAPHITE_PLANE; copy runtime-owned; rule under the title is print, not geometry."},
        {"id": "trait-plaque-left-flat", "status": "pass", "evidence": "no placeholder UI drawn on the reserved runtime region."},
        {"id": "rarity-tiers-rendered", "status": "pass", "evidence": "steel / copper / titanium / gold heroes under the neutral rig."},
        {"id": "material-id-boundaries", "status": "pass", "evidence": "material-id hero/front rendered from the same camera for the boundary check."},
        {"id": "library-registration-pending-approval", "status": "pass", "evidence": "7 registration proposals listed in material-revalidation.json; nothing written to materials.json before approval."},
    ]
    s7["materialSpec"] = {
        "modelId": MODEL_ID, "variantId": VARIANT, "revision": STAGE_REVISION, "recordedAt": NOW, "evidenceRevision": "rev-003",
        "sourceGate06Revision": 11, "sourceGate06Approval": {"userApprovalQuote": "批准", "approvedAt": "2026-09-11T14:45:00+08:00"},
        "contractSha256": report["contractSha256"], "rig": report["rig"], "calibration": report["calibration"], "materialsByZone": report["materials_by_zone"],
        "schemeAValues": report["scheme_a_values_adopted"], "headerLabel": report["header_label"], "traitPlaque": report["trait_plaque"],
        "libraryRegistrationProposals": report["library_registration_proposals"],
        "knownLimitations": [
            "Label copy (TRI-SPINNER / SERIES 01 / TITANIUM / 42.8 G / 0017 / 01/500) is placeholder from the V3 concept; the App fills real values at runtime.",
            "Brushing and sandblast are procedural object-space textures; Gate 10 must bake or re-author them as URP textures / detail normals.",
            "Neutral board is intentionally moodier than the Gate 05 beauty previews: black world, three 5600 K lights, no colour, no bloom.",
            "Unity parity (Gate 11) must reproduce thin film with a custom shader or an approximation; URP Lit has no thin-film term.",
        ],
    }
    s7["status"] = "ready_for_review"; s7["shippingReady"] = False
    events.append({"type": "gate-ready-for-review", "stageId": "07-material", "revision": STAGE_REVISION,
                   "notes": "Gate 07 rev 6: seven Gate 07 materials + header label decal on approved Gate 06 rev-011; neutral board, id maps, four tiers, neutral turntable."})
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1; manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gate-07-rev003-ready-for-review"
    manifest["currentState"]["activeStageId"] = "07-material"; manifest["currentState"]["activeStageStatus"] = "ready_for_review"
    manifest["currentState"]["materialRevalidation"] = {"materialRevision": STAGE_REVISION, "sourceGate06Revision": 11, "geometryChanged": False, "rig": "neutral", "calibrated": True}
    manifest["currentState"]["diagnosis"] += (" Gate 07 rev 6：在批准的 Gate 06 rev-011 几何上做七区材质（拉丝各向异性 + 细纹、喷砂微凸、整片薄膜、钢琴黑清漆、金饰各向异性）+ Oxanium 占位标签 decal；"
                                              "NEUTRAL 灯组 18% 灰卡校准；材质板 + 分区图 + 四档 + 中性转台；ready_for_review。材质库未写入。未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "assets": len(ids), "status": s7["status"], "review": len(s7["reviewArtifactIds"])}))


if __name__ == "__main__":
    main()
