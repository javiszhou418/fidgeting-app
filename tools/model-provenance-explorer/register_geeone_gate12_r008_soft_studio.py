#!/usr/bin/env python3
"""GEEONE 龙鳞三叶 · Gate 12 rev-008: lighting-only revision (Soft Studio) → ready_for_review.

2026-09-09 18:07 user: "我感觉柔光棚好看一点" (on the mobile-HDR simulator comparison
sheet, FDB-PREF-036). GeeoneLightingPresetCatalog.Shipping becomes SoftStudio; the
Build 47 recipe is kept as `StudioBright` for A/B only.

Gate 12 rev-007 (approved 18:36 "推到手机上吧", Build 47 device accepted) is preserved
as a superseded revision: geometry / materials / export / parity are unchanged; only
the runtime lighting recipe and the Mobile HDR pipeline (FDB-PREF-038) differ.

rev-008 evidence is the real iOS Simulator runtime (r007 library→mid→detail), not the
editor multi-view capture: GeeoneLightingOptionsPreviewCapture renders identically
under LDR/HDR grading and cannot show the HDR result. Visual approval of the r007
sheet is pending; nothing is pushed to the phone.

Idempotent guard: stage 12 must still be at rev-007.
"""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

EV = base.EV
REPO = base.REPO
UNITY = REPO / "unity/FidgetingApp"
NOW = datetime.now(timezone.utc).isoformat()

CHOICE_AT = "2026-09-09T10:07:00+00:00"  # 18:07 Asia/Shanghai
CHOICE_TEXT = "我感觉柔光棚好看一点"
SIM = REPO / "Artifacts/LibraryDetailConsistency/r007"
HDR_SHEET = REPO / "Artifacts/GeeoneLighting/r004-hdr/r004-hdr-geeone-lighting-options-simulator.png"
A12 = EV / "12-shipping/rev-008"


def copy(name: str):
    A12.mkdir(parents=True, exist_ok=True)
    target = A12 / name
    shutil.copy2(SIM / name, target)
    return target


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}
    s12 = st["12-shipping"]
    assert s12["revision"] == 7 and s12["status"] == "approved", "expected Gate 12 rev-007 approved (manifest rev 67)"

    s12.setdefault("historicalRevisions", []).append(
        {
            "revision": 7,
            "artifactIds": list(s12["artifactIds"]),
            "status": "superseded",
            "reason": f"user 2026-09-09 18:07 “{CHOICE_TEXT}” → rev-008 Soft Studio lighting (FDB-PREF-036) under the Mobile HDR pipeline (FDB-PREF-038); rev-007 approval + Build 47 device acceptance kept as history; geometry / materials / export / parity unchanged",
        }
    )
    s12["revision"] = 8
    s12["artifactIds"] = []
    s12.pop("staleReason", None)

    rows = [
        ("tri-r6o-g12-preset-source", UNITY / "Assets/Scripts/Product/GeeoneLightingPresetCatalog.cs", "shipping-source", "process", "runtime-lighting-preset-catalog", [], "ShippingId = SoftStudioId: spots 0.30/0.22/0.18, camera fill 0.26, ambient ×3.20, ambient floor ×0.95, studio softbox 0.42; StudioBright (Build 47 recipe) kept for A/B only"),
        ("tri-r6o-g12-lighting-source", UNITY / "Assets/Scripts/Product/SpinnerImageBasedLightingController.cs", "shipping-source", "process", "runtime-lighting-geeone-recipe", ["tri-r6o-g12-preset-source"], "Geeone* mirror constants follow Shipping; one recipe in library and detail"),
        ("tri-r6o-g12-pipeline-asset", UNITY / "Assets/Settings/Mobile_RPAsset.asset", "shipping-source", "process", "urp-mobile-pipeline-hdr", [], "FDB-PREF-038: SupportsHDR=1 (R11G11B10), ColorGradingMode=HDR"),
        ("tri-r6o-g12-tests-source", UNITY / "Assets/Tests/Editor/SpinnerEnvironmentTests.cs", "shipping-source", "process", "spinner-environment-editmode-tests", ["tri-r6o-g12-preset-source"], "GeeoneLightingPresets_ShipSoftStudioAndKeepStudioBrightOnlyForReview, GeeoneLightsIdenticallyInLibraryAndDetail"),
        ("tri-r6o-g12-hdr-options-sheet", HDR_SHEET, "review-sheet", "process", "simulator-lighting-options-sheet", [], "Mobile HDR real-simulator A×1.0 / A×0.5 / A×0.3 / B / C / D × library card / detail; the sheet the user chose B from"),
        ("tri-r6o-g12-sim-capture", copy("r007-simulator-capture.json"), "device-delivery", "validation", "simulator-capture-manifest", [], "iPhone 17 Pro simulator 5BF378DF, Release-iphonesimulator app sha256 inside"),
        ("tri-r6o-g12-sim-sheet", copy("r007-library-detail-sheet.png"), "contact-sheet", "shipping-render", "simulator-library-detail-sheet", ["tri-r6o-g12-sim-capture"], "four shipping toys × library / mid / detail; GEEONE column is rev-008"),
        ("tri-r6o-g12-sim-video", copy("r007-metal-three-blade-library-to-detail-clear.mp4"), "shipping-video", "shipping-render", "simulator-library-to-detail-recording", ["tri-r6o-g12-sim-capture"], "H.264 re-encode of the real runtime library→detail entrance"),
        ("tri-r6o-g12-shipping-library", copy("r007-metal-three-blade-library.png"), "shipping-library", "shipping-render", "simulator-library-frame", ["tri-r6o-g12-sim-video"], "≥250 white pixels in the model region 10.8% → 6.3% vs rev-007 under HDR"),
        ("tri-r6o-g12-shipping-mid", copy("r007-metal-three-blade-mid.png"), "shipping-transition", "shipping-render", "simulator-transition-frame", ["tri-r6o-g12-sim-video"], ""),
        ("tri-r6o-g12-shipping-phone", copy("r007-metal-three-blade-detail.png"), "shipping-phone", "shipping-render", "simulator-detail-frame", ["tri-r6o-g12-sim-video"], "≥250 white pixels in the model region 10.9% → 4.9% vs rev-007 under HDR"),
    ]
    for aid, path, slot, role, cls, srcs, note in rows:
        base.upsert(manifest, base.asset(aid, "12-shipping", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s12["artifactIds"].append(aid)

    s12["status"] = "ready_for_review"
    s12.setdefault("historicalDecisions", []).append(
        {
            "revision": 8,
            "decision": "preset-chosen",
            "decidedAt": CHOICE_AT,
            "decidedBy": "user",
            "channel": "chat",
            "exactWording": CHOICE_TEXT,
            "notes": "Soft Studio chosen from the HDR comparison sheet; this is a preset choice, not yet the rev-008 shipping visual approval",
        }
    )
    s12["decision"] = None
    s12["validations"] = [v for v in s12.get("validations", []) if v["id"] != "shipping-lighting-recipe"] + [
        {"id": "shipping-lighting-recipe", "status": "pass", "detail": "GeeoneLightingPresetCatalog.Shipping == SoftStudio; EditMode GeeoneLightingPresets_ShipSoftStudioAndKeepStudioBrightOnlyForReview + GeeoneLightsIdenticallyInLibraryAndDetail pass"},
        {"id": "shipping-editor-multiview-capture", "status": "warn", "detail": "GeeoneShippingPreviewCapture / GeeoneLightingOptionsPreviewCapture render identically under LDR and HDR grading; top / hero / oblique / low editor views cannot show the rev-008 HDR result. Real-simulator runtime frames are the review evidence."},
        {"id": "device-fps-budget-hdr", "status": "warn", "detail": "60 fps device budget not re-measured after FDB-PREF-038 HDR switch"},
    ]

    cs = manifest["currentState"]
    cs["visualApproval"] = "gate12-shipping-rev008-soft-studio-pending-user-visual-approval"
    cs["deviceStatus"] = "build-47-rev007-on-device; rev-008 not pushed (visual approval pending)"
    cs["lightingPresetProposal"] = {
        "status": "user-chose-B-soft-studio",
        "exactWording": CHOICE_TEXT,
        "decidedAt": CHOICE_AT,
        "shipping": "B soft-studio",
        "evidence": base.rel(HDR_SHEET),
        "note": "Gate 12 rev-008 lighting-only revision opened; ready_for_review on the r007 simulator sheet",
    }
    cs["diagnosis"] = (
        cs["diagnosis"]
        + f" | 09-09 18:07 preset-chosen: 用户“{CHOICE_TEXT}”→ Shipping = SoftStudio（FDB-PREF-036 Locked），Gate 12 rev-008 仅灯光修订，模拟器 r007 重录 {base.rel(SIM / 'r007-library-detail-sheet.png')}；GEEONE 列表卡 ≥250 白像素 10.8%→6.3%、详情 10.9%→4.9%。视觉批准待确认，未推送手机。"
    )

    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events = [
        ("stage-revised", f"Gate 12 rev-007 → rev-008 (lighting only) after the user's 2026-09-09 18:07 choice (exact wording: {CHOICE_TEXT}); rev-007 approval and Build 47 device acceptance preserved as history"),
        ("stage-note", "GeeoneLightingPresetCatalog.Shipping = SoftStudio (spots 0.30/0.22/0.18, fill 0.26, softbox 0.42); StudioBright kept for A/B only; r007 simulator re-record of all four toys; visual approval pending, not pushed to phone"),
    ]
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for kind, note in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": kind, "stageId": "12-shipping", "notes": note}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "stage12": {"revision": s12["revision"], "status": s12["status"], "artifacts": len(s12["artifactIds"])}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
