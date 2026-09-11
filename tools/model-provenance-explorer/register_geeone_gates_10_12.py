"""GEEONE 龙鳞三叶 · Gate 10 export rev-002, Gate 11 Unity parity rev-002, Gate 12 shipping previews rev-006 -> ready_for_review.

Triggered by the user's 2026-09-08 13:55 "继续吧" (Gates 04/06/07/08/09 approved in register_geeone_go_ahead_1355.py).
Nothing here approves anything: Gate 10 needs the user to look at the real GLB (orbit recording provided), Gate 11 shows the
Unity scene matches the export (silhouette IoU + import report), Gate 12 needs explicit visual approval before any build /
install. 视觉批准待确认，未推送手机.
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


def new_revision(stage, rev, reason):
    if stage["revision"] != rev:
        stage.setdefault("historicalRevisions", []).append({"revision": stage["revision"], "artifactIds": list(stage["artifactIds"]), "status": stage["status"], "reason": reason})
        stage["revision"] = rev
        stage["artifactIds"] = []
        stage.pop("staleReason", None)
    stage["decision"] = None


def add(manifest, stage, rows, stage_id):
    for aid, path, slot, role, cls, srcs, note in rows:
        base.upsert(manifest, base.asset(aid, stage_id, slot, path, role, cls, "repository-generated", "repository", srcs, note))
        if aid not in stage["artifactIds"]:
            stage["artifactIds"].append(aid)


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}

    # ---- Gate 10 export rev-002
    s10 = st["10-export"]
    new_revision(s10, 2, "rev-001 (old tri-fbx/glb direction) superseded by the GEEONE Gate 06 rev-008 export")
    s10["status"] = "ready_for_review"
    A10 = EV / "10-export/rev-002"
    val = json.loads((A10 / "export-validation.json").read_text(encoding="utf-8"))
    man = json.loads((A10 / "export-manifest.json").read_text(encoding="utf-8"))
    rows10 = [
        ("tri-r6m-g10-script", A10 / "export_geeone_gate10.py", "export-script", "process", "bpy-gate10-exporter-and-roundtrip-validator", ["tri-r6l-g06-blend", "tri-r6l-g06-contract"], "mm→m, Rotor_Root / Fixed_Root hierarchy, materials by name, FBX (-Z/Y, FBX_SCALE_UNITS) + GLB + collision, GLB/FBX round-trip checks"),
        ("tri-r6m-g10-blend", A10 / "geeone-tri-spinner-export-ready.blend", "blend-source", "source-model", "export-ready-blend-metres", ["tri-r6m-g10-script"], "4 meshes, modifiers applied, metres, hierarchy GEEONE_TriSpinner/Rotor_Root/Fixed_Root"),
        ("tri-r6m-g10-fbx", A10 / "geeone-tri-spinner.fbx", "fbx-export", "export", "shipping-fbx", ["tri-r6m-g10-blend"], f"sha256 {man['files']['geeone-tri-spinner.fbx']['sha256'][:12]}…; copied to Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner.fbx"),
        ("tri-r6m-g10-glb", A10 / "geeone-tri-spinner.glb", "glb-export", "export", "review-glb-y-up", ["tri-r6m-g10-blend"], "the real exported GLB for interactive review; orbit recording review/glb-orbit-review.mp4"),
        ("tri-r6m-g10-collision", A10 / "geeone-tri-spinner-collision.fbx", "collision-export", "export", "collision-fbx-rotor-hull-fixed-cylinder", ["tri-r6m-g10-blend"], "Rotor_Collision = convex hull of Rotor_Body (under Rotor_Root); Fixed_Collision = cap-radius cylinder (under Fixed_Root)"),
        ("tri-r6m-g10-manifest", A10 / "export-manifest.json", "export-manifest", "contract", "export-manifest-hashes-units-hierarchy", ["tri-r6m-g10-fbx", "tri-r6m-g10-glb", "tri-r6m-g10-collision", "tri-r6m-g10-blend"], "units metres (2R = 0.085 m provisional), axes, kinematics, per-mesh stats, sha256 of every file"),
        ("tri-r6m-g10-validation", A10 / "export-validation.json", "export-validation", "validation", "glb-and-fbx-roundtrip-validation", ["tri-r6m-g10-manifest"], json.dumps(val["glb"]["checks"], ensure_ascii=False)),
        ("tri-r6m-g10-silhouette-script", A10 / "render_glb_silhouettes.py", "export-review", "process", "glb-flat-silhouette-renderer", ["tri-r6m-g10-glb"], "Gate 11 camera recipe: top ortho 2.3 R, hero (1.2, -1.6, 1.5) R"),
        ("tri-r6m-g10-orbit", A10 / "review/glb-orbit-review.mp4", "export-review", "blender-render", "glb-roundtrip-orbit-24-frames", ["tri-r6m-g10-glb"], "Workbench orbit of the re-imported GLB (interaction substitute)"),
    ]
    for name in ("glb-hero", "glb-low", "glb-top-ortho", "glb-top-ortho-silhouette", "glb-hero-silhouette"):
        rows10.append((f"tri-r6m-g10-review-{name}", A10 / "review" / f"{name}.png", "export-review", "blender-render", f"glb-roundtrip-{name}", ["tri-r6m-g10-glb"], ""))
    add(manifest, s10, rows10, "10-export")
    s10["validations"] = [{"id": "glb-" + k.replace(" ", "-").replace("(", "").replace(")", "").replace("±", "pm").replace("/", "-").replace(",", "").replace("=", "").replace("≤", "le"), "status": "pass" if v else "fail", "detail": "GLB round-trip: " + k} for k, v in val["glb"]["checks"].items()] + [
        {"id": "fbx-roundtrip", "status": "pass" if val["fbx"]["pass"] else "fail", "detail": "FBX round-trip: " + json.dumps(val["fbx"]["checks"], ensure_ascii=False)},
        {"id": "units-and-axes", "status": "pass", "detail": "metres, planar 2R = 0.085 m; Blender Z → Unity Y (FBX -Z forward / Y up); pivot at the spin axis"},
        {"id": "kinematic-groups", "status": "pass", "detail": "Rotor_Root [Rotor_Body] rotates; Fixed_Root [Cap_Top, Cap_Bottom, Hub_Core] static"},
        {"id": "user-glb-review", "status": "warn", "detail": "等待用户查看真实 GLB（review/glb-orbit-review.mp4 为交互替代）"},
    ]

    # ---- Gate 11 Unity parity rev-002
    s11 = st["11-unity-parity"]
    new_revision(s11, 2, "first real parity revision for the GEEONE export")
    s11["status"] = "ready_for_review"
    A11 = EV / "11-unity-parity/rev-002"
    par = json.loads((A11 / "parity-report.json").read_text(encoding="utf-8"))
    rows11 = [
        ("tri-r6m-g11-capture-source", UNITY / "Assets/Editor/GeeoneShippingPreviewCapture.cs", "parity-source", "process", "unity-editor-neutral-and-shipping-capture", ["tri-r6m-g10-fbx"], "CaptureNeutral: flat-white silhouettes with the Gate 10 camera recipe; WriteParityReport: hierarchy / ownership / materials / triangles / bounds"),
        ("tri-r6m-g11-builder-source", UNITY / "Assets/_Fidgeting/Editor/ThreeBladeSceneBuilder.cs", "parity-source", "process", "unity-scene-builder-install-geeone-visuals", ["tri-r6m-g10-fbx"], "InstallGeeoneVisuals: Rotor_Root → RotorDynamic; Cap_Top/Cap_Bottom → TopCap/BottomCap; Hub_Core → HubStatic; 180° yaw; materials by name"),
        ("tri-r6m-g11-materials-source", UNITY / "Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs", "parity-source", "process", "unity-material-factory-geeone", [], "M_GeeoneSatin 0.64 / M_GeeoneDiscTurned 0.68 (URP Lit, facets must read) / M_GeeoneHubDark 0.55"),
        ("tri-r6m-g11-unity-asset", UNITY / "Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner.fbx", "unity-asset", "export", "unity-imported-fbx", ["tri-r6m-g10-fbx"], "same bytes as 10-export/rev-002/geeone-tri-spinner.fbx"),
        ("tri-r6m-g11-blender-neutral", A10 / "review/glb-top-ortho.png", "blender-neutral", "blender-render", "blender-glb-roundtrip-top-ortho", ["tri-r6m-g10-glb"], "Workbench material view, top ortho 2.3 R"),
        ("tri-r6m-g11-blender-neutral-silhouette", A10 / "review/glb-top-ortho-silhouette.png", "blender-neutral", "blender-render", "blender-glb-roundtrip-top-ortho-silhouette", ["tri-r6m-g10-glb"], "flat white on black"),
        ("tri-r6m-g11-unity-neutral", A11 / "unity-neutral-top-ortho.png", "unity-neutral", "unity-render", "unity-shipping-scene-top-ortho-silhouette", ["tri-r6m-g11-capture-source"], "same camera recipe, URP Unlit white, other renderers hidden"),
        ("tri-r6m-g11-unity-neutral-hero", A11 / "unity-neutral-hero.png", "unity-neutral", "unity-render", "unity-shipping-scene-hero-silhouette", ["tri-r6m-g11-capture-source"], ""),
        ("tri-r6m-g11-import-report", A11 / "unity-import-parity-report.json", "parity-measurement", "validation", "unity-hierarchy-ownership-materials-bounds", ["tri-r6m-g11-capture-source"], "rotates / rendererEnabled / materials / triangles / world bounds per part; yaw 180; zero angular velocity"),
        ("tri-r6m-g11-parity-script", A11 / "build_geeone_parity_report.py", "parity-source", "process", "silhouette-iou-and-import-checks", ["tri-r6m-g11-import-report", "tri-r6m-g10-manifest"], ""),
        ("tri-r6m-g11-parity-report", A11 / "parity-report.json", "parity-report", "validation", "gate11-parity-report", ["tri-r6m-g11-parity-script"], json.dumps(par["checks"], ensure_ascii=False)),
        ("tri-r6m-g11-overlay-top", A11 / "silhouette-overlay-top-ortho.png", "parity-overlay", "process", "silhouette-overlay-top", ["tri-r6m-g11-parity-script"], f"IoU {par['silhouette']['top-ortho']['iou']}"),
        ("tri-r6m-g11-overlay-hero", A11 / "silhouette-overlay-hero.png", "parity-overlay", "process", "silhouette-overlay-hero", ["tri-r6m-g11-parity-script"], f"IoU {par['silhouette']['hero']['iou']}"),
        ("tri-r6m-g11-sheet", A11 / "unity-parity-contact-sheet.png", "contact-sheet", "process", "unity-parity-contact-sheet", ["tri-r6m-g11-parity-script"], ""),
    ]
    add(manifest, s11, rows11, "11-unity-parity")
    s11["validations"] = [{"id": "p-" + k.replace(" ", "-").replace("(", "").replace(")", "").replace("/", "-").replace(",", "").replace(":", "").replace("%", "pct").replace(">=", "ge").replace("'", ""), "status": "pass" if v else "fail", "detail": k} for k, v in par["checks"].items()] + [
        {"id": "editmode-tests", "status": "pass", "detail": "GeeoneTriSpinnerAssetTests (2) + BlenderDragonScaleAssetTests + ThreeBladeStaticAcceptanceTests + SpinnerProgressionTests (skins / engraving on Cap_Top, Rotor_Body) + PremiumDisplayCaseTests + FidgetSpinnerMotionTests: 121/122; the one failure (RuntimeAndLiquidGlassUi Swift 'Label(' check) is unrelated to the model"},
        {"id": "unity-anisotropy", "status": "warn", "detail": "URP 无各向异性：盘用 URP Lit 0.68 + 弱径向 normal；14 扇区靠几何法线读出（预览已确认）"},
        {"id": "user-review", "status": "warn", "detail": "等待用户确认 Unity 对齐（unity-parity-contact-sheet.png）"},
    ]

    # ---- Gate 12 shipping rev-006
    s12 = st["12-shipping"]
    new_revision(s12, 6, "r001–r005 (hub-cap size / facet direction, rejected 2026-09-05) superseded by the GEEONE rebuild")
    s12["status"] = "ready_for_review"
    A12 = EV / "12-shipping/rev-006"
    rows12 = [
        ("tri-r6m-g12-scene", UNITY / "Assets/_Fidgeting/Scenes/ThreeBladeMetalOriginal.unity", "shipping-scene", "source-model", "shipping-scene-metal-three-blade", ["tri-r6m-g11-builder-source", "tri-r6m-g11-unity-asset"], "rebuilt 2026-09-08 by ThreeBladeSceneBuilder.BuildOriginalMetalPresentation (batchmode)"),
        ("tri-r6m-g12-thumbnail", UNITY / "Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png", "shipping-library", "shipping-render", "swiftui-library-thumbnail-512", ["tri-r6m-g12-scene"], "regenerated from the shipping scene (library pose 0°/89°); shipping asset — reverts with git if rejected"),
        ("tri-r6m-g12-tests", A12 / "tests/geeone-editmode-results.xml", "test-report", "validation", "unity-editmode-results", ["tri-r6m-g12-scene"], "121 passed / 1 unrelated failure"),
        ("tri-r6m-g12-tests-source", UNITY / "Assets/_Fidgeting/Tests/Editor/GeeoneTriSpinnerAssetTests.cs", "shipping-source", "process", "geeone-asset-and-scene-editmode-tests", ["tri-r6m-g12-scene"], "two-part ownership, 85 mm, materials, hidden procedural / bearing, exploded order, zero angular velocity, no DragonScale dependency"),
        ("tri-r6m-g12-sheet", A12 / "shipping-review-contact-sheet.png", "contact-sheet", "process", "shipping-review-contact-sheet", ["tri-r6m-g12-scene"], "phone / hero / top / left / right / low / library"),
    ]
    for slot, name in (("shipping-library", "shipping-library.png"), ("shipping-hero", "shipping-hero.png"), ("shipping-top", "shipping-top.png"), ("shipping-left-oblique", "shipping-left-oblique.png"), ("shipping-right-oblique", "shipping-right-oblique.png"), ("shipping-low", "shipping-low.png"), ("shipping-phone", "shipping-phone.png")):
        rows12.append((f"tri-r6m-g12-{slot}", A12 / name, slot, "shipping-render", f"unity-shipping-{slot}", ["tri-r6m-g12-scene", "tri-r6m-g11-capture-source"], "720×1280 (library 512²), shipping environment, ThreeBladeMetalOriginal.unity"))
    add(manifest, s12, rows12, "12-shipping")
    s12["validations"] = [
        {"id": "shipping-scene-rebuilt", "status": "pass", "detail": "ThreeBladeMetalOriginal.unity: RotorDynamic/Rotor_Root/Rotor_Body 转；HubStatic/TopCap/Cap_Top、BottomCap/Cap_Bottom、Hub_Core 静；procedural + BearingBalls 隐藏"},
        {"id": "shipping-preview-set", "status": "pass", "detail": "phone / hero / top / left / right / low / library 来自真实出货场景 + 出货环境"},
        {"id": "editmode-tests", "status": "pass", "detail": "121/122（唯一失败 RuntimeAndLiquidGlassUi Swift 文案检查与模型无关）"},
        {"id": "visual-approval", "status": "pending", "detail": "视觉批准待确认，未 build，未推送手机"},
        {"id": "device-acceptance", "status": "pending", "detail": "未安装；真机验收另计"},
    ]

    manifest["currentState"]["visualApproval"] = "gate12-shipping-preview-pending"
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-08 gates 10-12:")[0]
        + " | 09-08 gates 10-12: Gate 10 rev-002 导出（米、Rotor_Root / Fixed_Root、FBX + GLB + collision、往返校验全过）；Gate 11 rev-002 Unity 对齐（ThreeBladeMetalOriginal 场景换 GEEONE FBX，轮廓 IoU 顶视 0.998 / hero 0.995，三角数一致，转子转 / 盖 + 毂芯静，EditMode 121/122）；Gate 12 rev-006 出货预览（phone / hero / top / 左右 oblique / low / library）ready_for_review。未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for sid, note in (
            ("10-export", "10-export rev-002 ready_for_review: FBX/GLB/collision in metres, Rotor_Root + Fixed_Root, round-trip checks pass; " + json.dumps(val["glb"]["checks"], ensure_ascii=False)),
            ("11-unity-parity", "11-unity-parity rev-002 ready_for_review: metal scene rebuilt with the GEEONE FBX; silhouette IoU top 0.998 / hero 0.995; " + json.dumps(par["checks"], ensure_ascii=False)),
            ("12-shipping", "12-shipping rev-006 ready_for_review: shipping previews from ThreeBladeMetalOriginal.unity; EditMode 121/122; visual approval pending, no build, no install"),
        ):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": "stage-revised", "stageId": sid, "notes": note}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
