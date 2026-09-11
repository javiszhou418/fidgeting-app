"""GEEONE 龙鳞三叶 · Gate 12 rev-007 (detail-lighting fix) → approved 18:36 "推到手机上吧" → Build 47 → user device acceptance.

Back-fills three events that happened after the last manifest revision (65):

1. 2026-09-08 15:45 user: "感觉挺好的，但是为什么光照感觉特别暗，特别黑？" → Gate 12 rev-007: SpinnerImageBasedLightingController
   GEEONE detail boost + ThreeBladeSceneBuilder HDR/ACES/exposure, seven shipping views re-captured. rev-006 (approved 15:11)
   is preserved as a superseded revision, not rejected: geometry / materials / export / parity did not change.
2. 2026-09-08 18:36 user: "推到手机上吧" → chat visual approval of rev-007 and the device push. Build 47
   (geeone-tri-spinner-build47-20260908T103620Z-snapshot): EditMode 152/152, installed + launched (pid 45090).
3. 2026-09-08 (this thread) user: "GEEONE 龙鳞三叶（metal-three-blade）12 Gate 已完成，Build 47 已装到手机，用户真机验收通过。"
   → device acceptance recorded separately from the Gate 12 visual approval (AGENTS.md: they are different gates).

Idempotent guard: refuses to run twice (stage 12 must still be at rev-006).
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

EV = base.EV
REPO = base.REPO
UNITY = REPO / "unity/FidgetingApp"
NOW = datetime.now(timezone.utc).isoformat()

APPROVAL_AT = "2026-09-08T10:36:00+00:00"  # 18:36 Asia/Shanghai; snapshot 20260908T103620Z started 20 s later
APPROVAL_TEXT = "推到手机上吧"
LIGHTING_FEEDBACK_TEXT = "感觉挺好的，但是为什么光照感觉特别暗，特别黑？"
ACCEPTANCE_TEXT = "GEEONE 龙鳞三叶（metal-three-blade）12 Gate 已完成，Build 47 已装到手机，用户真机验收通过。"
APPROVAL_EVIDENCE = (
    "chat approval of the seven re-captured rev-007 shipping views (phone / hero / top / left / right / low / library, "
    "ThreeBladeMetalOriginal.unity, GEEONE detail lighting boost); no interactive Unity runtime session — static shipping renders + "
    "the device build that followed"
)

A12 = EV / "12-shipping/rev-007"
DELIVERY = A12 / "device-delivery/geeone-tri-spinner-build47-20260908T103620Z-snapshot"
PRECHECK = A12 / "device-delivery/geeone-tri-spinner-build47-20260908T103426Z-snapshot"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}
    s12 = st["12-shipping"]
    assert s12["revision"] == 6 and s12["status"] == "approved", "expected Gate 12 rev-006 approved (manifest rev 65)"
    assert all(st[k]["status"] == "approved" for k in st), "Gates 01–11 must all be approved"

    delivery = json.loads((DELIVERY / "delivery-result.json").read_text(encoding="utf-8"))
    assert delivery["buildNumber"] == "47" and delivery["installed"] and delivery["launched"]

    acceptance = base.write_json(
        DELIVERY / "device-acceptance.json",
        {
            "schemaVersion": 1,
            "modelId": base.MODEL_ID,
            "stageId": "12-shipping",
            "stageRevision": 7,
            "jobId": delivery["jobId"],
            "buildNumber": delivery["buildNumber"],
            "bundleIdentifier": delivery["bundleIdentifier"],
            "version": delivery["version"],
            "deviceUdid": delivery["deviceUdid"],
            "deliveryResultSha256": base.sha256(DELIVERY / "delivery-result.json"),
            "visualApproval": {"channel": "chat", "exactWording": APPROVAL_TEXT, "decidedAt": APPROVAL_AT},
            "deviceAcceptance": {"status": "accepted", "channel": "chat", "exactWording": ACCEPTANCE_TEXT, "decidedBy": "user", "recordedAt": NOW},
            "note": "delivery-result.json is an immutable snapshot (deviceAcceptance=pending-user-validation at build time); this file records the later user decision.",
        },
    )

    # ---- rev-006 → history (superseded by the lighting fix, approval preserved)
    s12.setdefault("historicalRevisions", []).append(
        {
            "revision": 6,
            "artifactIds": list(s12["artifactIds"]),
            "status": "superseded",
            "reason": f"user 2026-09-08 15:45 “{LIGHTING_FEEDBACK_TEXT}” → rev-007 detail lighting boost re-captured the shipping views; rev-006 approval (15:11 “继续吧”) kept as history; geometry / materials / export / parity unchanged",
        }
    )
    s12["revision"] = 7
    s12["artifactIds"] = []
    s12.pop("staleReason", None)

    rows = [
        ("tri-r6n-g12-scene", UNITY / "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity", "shipping-scene", "source-model", "shipping-scene-metal-three-blade", ["tri-r6m-g11-builder-source", "tri-r6m-g11-unity-asset"], "rebuilt 2026-09-08 15:45 by ThreeBladeSceneBuilder.BuildOriginalMetalPresentation (batchmode): HDR + ACES, postExposure +0.75, contrast 4, stronger scene lights"),
        ("tri-r6n-g12-lighting-source", UNITY / "Assets/Scripts/Product/SpinnerImageBasedLightingController.cs", "shipping-source", "process", "runtime-detail-lighting-geeone-boost", [], "GEEONE detail presentation boost: direct ×3.10 / reflection ×2.55 / ambient ×3.40, visibility fill 0.85, ambient floor colours; library canyon card keeps the soft-metal policy"),
        ("tri-r6n-g12-builder-source", UNITY / "Assets/_Fidgeting/Editor/ThreeBladeSceneBuilder.cs", "shipping-source", "process", "unity-scene-builder-install-geeone-visuals", ["tri-r6m-g10-fbx"], "InstallGeeoneVisuals + rev-007 lighting: HDR/ACES volume, exposure, scene lights"),
        ("tri-r6n-g12-capture-source", UNITY / "Assets/Editor/GeeoneShippingPreviewCapture.cs", "shipping-source", "process", "unity-editor-shipping-capture", ["tri-r6n-g12-scene"], "PortraitProjection (ResetProjectionMatrix + aspect) + forced detail lighting recipe before capture"),
        ("tri-r6n-g12-tests-source", UNITY / "Assets/_Fidgeting/Tests/Editor/GeeoneTriSpinnerAssetTests.cs", "shipping-source", "process", "geeone-asset-and-scene-editmode-tests", ["tri-r6n-g12-scene"], ""),
        ("tri-r6n-g12-thumbnail", UNITY / "Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png", "shipping-library", "shipping-render", "swiftui-library-thumbnail-512", ["tri-r6n-g12-scene"], "same bytes as rev-007 shipping-library.png; shipped in Build 47"),
        ("tri-r6n-g12-sheet", A12 / "shipping-review-contact-sheet.png", "contact-sheet", "process", "shipping-review-contact-sheet", ["tri-r6n-g12-scene"], "assembled from the seven rev-007 views (build_geeone_shipping_contact_sheet.py); layout only"),
        ("tri-r6n-g12-delivery-result", DELIVERY / "delivery-result.json", "device-delivery", "validation", "device-delivery-result-build47", ["tri-r6n-g12-scene"], "Build 47, Unity 6000.5.6f1, export + xcodebuild + sign + install + launch (pid 45090); sourceCommit 62d8bcd + 94 dirty tracked files"),
        ("tri-r6n-g12-delivery-tests", DELIVERY / "unity-editmode-results.xml", "test-report", "validation", "unity-editmode-results", ["tri-r6n-g12-scene"], "delivery pre-check 152/152 passed"),
        ("tri-r6n-g12-delivery-install", DELIVERY / "install.json", "device-delivery", "validation", "devicectl-install", ["tri-r6n-g12-delivery-result"], ""),
        ("tri-r6n-g12-delivery-launch", DELIVERY / "launch.json", "device-delivery", "validation", "devicectl-launch", ["tri-r6n-g12-delivery-result"], "outcome success"),
        ("tri-r6n-g12-delivery-source-hashes", DELIVERY / "source-hashes-after-export.txt", "device-delivery", "validation", "source-hashes-after-export", ["tri-r6n-g12-delivery-result"], ""),
        ("tri-r6n-g12-delivery-precheck-tests", PRECHECK / "unity-editmode-results.xml", "test-report", "validation", "unity-editmode-results", [], "first 18:34 job stopped after the EditMode pre-check (no export); kept as history"),
        ("tri-r6n-g12-device-acceptance", acceptance, "device-acceptance", "user-input", "user-device-acceptance-record", ["tri-r6n-g12-delivery-result"], ACCEPTANCE_TEXT),
    ]
    for slot, name in (("shipping-library", "shipping-library.png"), ("shipping-hero", "shipping-hero.png"), ("shipping-top", "shipping-top.png"), ("shipping-left-oblique", "shipping-left-oblique.png"), ("shipping-right-oblique", "shipping-right-oblique.png"), ("shipping-low", "shipping-low.png"), ("shipping-phone", "shipping-phone.png")):
        rows.append((f"tri-r6n-g12-{slot}", A12 / name, slot, "shipping-render", f"unity-shipping-{slot}", ["tri-r6n-g12-scene", "tri-r6n-g12-capture-source"], "720×1280 (library 512²), shipping environment + GEEONE detail lighting, ThreeBladeMetalOriginal.unity"))
    for aid, path, slot, role, cls, srcs, note in rows:
        origin, asserted = ("user-provided", "user") if role == "user-input" else ("repository-generated", "repository")
        base.upsert(manifest, base.asset(aid, "12-shipping", slot, path, role, cls, origin, asserted, srcs, note))
        s12["artifactIds"].append(aid)

    s12["status"] = "approved"
    s12["decision"] = {
        "action": "approve",
        "notes": "用户 18:36“推到手机上吧”（在 15:45 光照提亮 rev-007 七视图之后）。批准 rev-007 出货预览并授权真机推送；Build 47 随即安装启动。真机验收另计（见 device-acceptance）。",
        "decidedBy": "user",
        "decidedAt": APPROVAL_AT,
        "recordedAt": NOW,
        "channel": "chat",
        "exactWording": APPROVAL_TEXT,
        "evidenceMode": APPROVAL_EVIDENCE,
    }
    s12.setdefault("historicalDecisions", []).extend(
        [
            {"revision": 6, "decision": "superseded", "decidedAt": "2026-09-08T07:45:00+00:00", "decidedBy": "user", "channel": "chat", "exactWording": LIGHTING_FEEDBACK_TEXT, "notes": "15:45 光照反馈 → rev-007 详情提亮；不是几何/材质驳回"},
            {"revision": 7, "decision": "approved", "decidedAt": APPROVAL_AT, "recordedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": APPROVAL_TEXT, "evidenceMode": APPROVAL_EVIDENCE, "notes": "批准 rev-007 出货预览 + 授权推送手机 → Build 47"},
            {"revision": 7, "decision": "device-accepted", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": ACCEPTANCE_TEXT, "notes": "Build 47 真机验收通过（与 Gate 12 视觉批准分开记录）"},
        ]
    )
    s12["validations"] = [
        {"id": "shipping-scene-rebuilt", "status": "pass", "detail": "ThreeBladeMetalOriginal.unity: RotorDynamic/Rotor_Root/Rotor_Body 转；HubStatic/TopCap/Cap_Top、BottomCap/Cap_Bottom、Hub_Core 静；procedural + BearingBalls 隐藏；HDR + ACES、postExposure +0.75"},
        {"id": "shipping-preview-set", "status": "pass", "detail": "phone / hero / top / left / right / low / library 来自真实出货场景 + 出货环境 + GEEONE 详情灯光配方"},
        {"id": "preview-aspect", "status": "pass", "detail": "PortraitProjection: ResetProjectionMatrix + aspect 每帧；14:56 拉伸问题已修"},
        {"id": "detail-lighting", "status": "pass", "detail": "user 15:45 “光照特别暗，特别黑” → GEEONE 详情提亮：hero 中心区 mean 0.199→0.246、P90 0.317→0.762（rev-006 vs rev-007）"},
        {"id": "editmode-tests", "status": "pass", "detail": "device delivery pre-check 152/152 passed (Build 47 snapshot)"},
        {"id": "approval-evidence-mode", "status": "warn", "detail": APPROVAL_EVIDENCE},
        {"id": "device-build", "status": "pass", "detail": "Build 47 com.jiaweizhou.fidgetspinner.codex 0.1.0: unityExportSucceeded / xcodeBuildSucceeded / signed / installed / launched (pid 45090)"},
        {"id": "device-acceptance", "status": "pass", "detail": f"user chat (this thread, recorded {NOW}): “{ACCEPTANCE_TEXT}”"},
    ]

    manifest["model"]["status"] = "shipping-current-geeone-device-accepted"
    manifest["model"]["scenePath"] = "unity/FidgetingApp/Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity"
    cs = manifest["currentState"]
    cs["rebuildRequested"] = False
    cs["shippingAssetUnchanged"] = False
    cs["visualApproval"] = "gate12-shipping-preview-rev007-approved-2026-09-08-1836"
    cs["deviceStatus"] = "build-47-installed-launched-user-device-accepted-2026-09-08"
    cs["diagnosis"] = (
        cs["diagnosis"].split(" | 09-08 15:45 lighting:")[0]
        + f" | 09-08 15:45 lighting: 用户“{LIGHTING_FEEDBACK_TEXT}”→ Gate 12 rev-007：SpinnerImageBasedLightingController GEEONE 详情提亮 + 场景 HDR/ACES/曝光，七视图重拍（hero mean 0.199→0.246、P90 0.317→0.762）；rev-006 记 superseded。"
        + f" | 09-08 18:36 push: 用户“{APPROVAL_TEXT}”→ Gate 12 rev-007 approved（chat）+ Build 47 安装启动（EditMode 152/152，pid 45090）。"
        + f" | 09-08 device-accepted: 用户“{ACCEPTANCE_TEXT}”→ 12/12 approved + 真机验收通过。下一步：FDB-PREF-032 catalog 收敛（gold-four-wing / pointed-three-blade）待用户决定。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events = [
        ("stage-revised", f"12-shipping rev-006 → rev-007 after the user's 2026-09-08 15:45 lighting feedback (exact wording: {LIGHTING_FEEDBACK_TEXT}); GEEONE detail lighting boost, seven shipping views re-captured; rev-006 superseded, its 15:11 approval kept as history"),
        ("stage-approved", f"12-shipping rev-007 approved by the user's explicit chat instruction 2026-09-08 18:36 (exact wording: {APPROVAL_TEXT}); evidence mode: {APPROVAL_EVIDENCE}; recorded retroactively {NOW}"),
        ("stage-note", "12-shipping rev-007 device delivery: Build 47 geeone-tri-spinner-build47-20260908T103620Z-snapshot — EditMode 152/152, Unity export + Xcode build + sign + install + launch succeeded (pid 45090); deviceAcceptance pending at build time"),
        ("stage-note", f"12-shipping rev-007 device accepted by the user's explicit chat instruction (exact wording: {ACCEPTANCE_TEXT}); recorded in device-acceptance.json; 12/12 approved; model status shipping-current-geeone-device-accepted"),
    ]
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for kind, note in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": kind, "stageId": "12-shipping", "notes": note}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "stage12": {"revision": s12["revision"], "status": s12["status"], "artifacts": len(s12["artifactIds"])}, "deviceStatus": cs["deviceStatus"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
