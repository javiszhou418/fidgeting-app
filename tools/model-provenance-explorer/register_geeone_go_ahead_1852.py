"""User 2026-09-07 18:52 "可以，继续推进吧" on blockout rev-007.

Persists the exact wording as the approval of Gate 05 rev-007 and, because the white model embodies the Gate 01/02 analysis
and the contract/architecture derived from it, as the chat approval of Gate 01 rev-003, Gate 02 rev-006, Gate 03 rev-005
(modeling contract, all mm provisional) and Gate 04 rev-005 (parts/pivot architecture). Evidence for those approvals is
static Workbench views + the fixed camera pack (no interactive viewer) — recorded as such.
Then registers Gate 06 rev-005 (finalised geometry, self-checked) and Gate 07/08/09 rev-002 (Cycles lookdev + turntable)
as ready_for_review. Nothing downstream is approved; no export, Unity, build, install.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
EV = base.EV
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "可以，继续推进吧"
EVIDENCE_MODE = "chat approval after static Workbench review views + fixed camera pack (capture_standard_views.py); no interactive 3D viewer was used"


def approve(stage, notes):
    stage["status"] = "approved"
    stage["decision"] = {"action": "approve", "notes": notes, "decidedBy": "user", "decidedAt": NOW, "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": EVIDENCE_MODE}
    stage.setdefault("historicalDecisions", []).append({"revision": stage["revision"], "decision": "approved", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": USER_TEXT, "evidenceMode": EVIDENCE_MODE, "notes": notes})


def new_revision(stage, rev, reason):
    if stage["revision"] != rev:
        stage.setdefault("historicalRevisions", []).append({"revision": stage["revision"], "artifactIds": list(stage["artifactIds"]), "status": stage["status"], "reason": stage.get("staleReason", reason)})
        stage["revision"] = rev
        stage["artifactIds"] = []
        stage.pop("staleReason", None)
    stage["decision"] = None


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}

    # ---- Gate 01 / 02 approvals
    approve(st["01-intake"], "用户 18:52 对按 Gate 01/02 分析建成的白模 rev-007 说“可以，继续推进吧”。批准范围：GEEONE 源视频 intake（哈希、fps=10 关键帧）作为唯一参考来源。")
    approve(st["02-analysis"], "用户 18:52“可以，继续推进吧”。批准 Gate 02 rev-006 现行分析（surface-detail-spec v18、reference-cad-from-video-v17、claims tri-r6f-*）作为建模依据。此前五项冲突按现值收口且全部 provisional：盖侧高 0.14 R、叶根漏斗坑存在、盖/外接圆 0.485、平盘 0.82、盖顶 E1（盘缘最高 + 14 扇区内凹拇指位）。2R = 85 mm user-authorized-provisional，无 measured mm。")

    # ---- Gate 03 contract rev-005
    s03 = st["03-contract"]
    new_revision(s03, 5, "rev-004 draft (old direction) superseded by the Gate 02 rev-006 contract")
    A03 = EV / "03-contract/rev-005"
    for aid, path, slot, role, cls, srcs, note in [
        ("tri-r6i-contract-json", A03 / "geeone-gate02-geometry-contract.json", "modeling-contract", "contract", "gate02-geometry-contract-r-units", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v17"], "same file as 05-blockout/rev-007"),
        ("tri-r6i-contract-md", A03 / "modeling-contract.md", "modeling-contract", "contract", "modeling-contract-table-provisional-mm", ["tri-r6i-contract-json", "tri-r6-user-instructions-1833"], "所有 mm 均 user-authorized-provisional；未列尺寸 unknown"),
    ]:
        base.upsert(manifest, base.asset(aid, "03-contract", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s03["artifactIds"].append(aid)
    s03["validations"] = [
        {"id": "no-measured-mm", "status": "pass", "detail": "合同全部 R 比例；mm 仅 85 provisional 换算；未知工程尺寸保持 unknown"},
        {"id": "approval-evidence-mode", "status": "warn", "detail": EVIDENCE_MODE},
    ]
    approve(s03, "用户 18:52“可以，继续推进吧”。批准 rev-005 建模合同（R 比例 + 85 mm provisional）。仅授权 Gate 04–10 的 Blender 工作与 Gate 11 Unity 对齐准备；不授权 shipping build、install、手机。")

    # ---- Gate 04 architecture rev-005
    s04 = st["04-architecture"]
    new_revision(s04, 5, "rev-004 draft (old direction) superseded")
    A04 = EV / "04-architecture/rev-005"
    base.upsert(manifest, base.asset("tri-r6i-architecture-md", "04-architecture", "interaction-architecture", A04 / "architecture.md", "contract", "parts-ownership-pivot-hierarchy", "repository-generated", "repository", ["tri-r6i-contract-json"], "Rotor_Body 旋转 / Cap+Hub_Seat 静止；Unity Fixed_Root / Rotor 挂点"))
    s04["artifactIds"].append("tri-r6i-architecture-md")
    s04["validations"] = [
        {"id": "kinematics-only", "status": "pass", "detail": "仅绕 Z 自由旋转；无阻尼/力感/Haptics 内容"},
        {"id": "approval-evidence-mode", "status": "warn", "detail": EVIDENCE_MODE},
    ]
    approve(s04, "用户 18:52“可以，继续推进吧”。批准 rev-005 零件架构：Rotor_Body 旋转、Cap_Top/Bottom + Hub_Seat_Top/Bottom 静止；Unity 挂点 Fixed_Root / Rotor。")

    # ---- Gate 05 rev-007 approved
    s05 = st["05-blockout"]
    assert s05["revision"] == 7
    s05["validations"] = [v for v in s05["validations"] if v["id"] != "upstream-gates-pending"] + [{"id": "approval-evidence-mode", "status": "warn", "detail": EVIDENCE_MODE}]
    approve(s05, "用户 18:52“可以，继续推进吧”（在看过 rev-007 评审板：盖缘外悬毂座后）。批准白模 rev-007。占位值（外悬 0.03 R、盖侧高 0.14 R、坑深 38% t、鳞角度、85 mm）随批准进入下游，仍标 provisional。")

    # ---- Gate 06 geometry rev-005 ready_for_review
    s06 = st["06-geometry"]
    new_revision(s06, 5, "rev-004 draft (old direction) superseded")
    s06["status"] = "ready_for_review"
    A06 = EV / "06-geometry/rev-005"
    checks = json.loads((A06 / "gate06-checks.json").read_text(encoding="utf-8"))
    assets06 = [
        ("tri-r6i-g06-script", A06 / "finalize_geeone_geometry.py", "geometry-source", "process", "bpy-geometry-finalizer", ["tri-r6h-blend", "tri-r6h-geometry-contract"], "apply booleans → 坑口沿凸圆角（weight bevel R0.03·S，6 段）→ 0.15 mm 微倒角（>40°）→ gate06 检查"),
        ("tri-r6i-g06-contract", A06 / "geeone-gate02-geometry-contract.json", "geometry-source", "contract", "gate02-geometry-contract-r-units", ["tri-r6h-geometry-contract"], ""),
        ("tri-r6i-g06-blend", A06 / "geeone-geometry-r005.blend", "geometry-source", "source-model", "geometry-blend-r005", ["tri-r6i-g06-script"], "Rotor_Body 3393 顶点 / 3208 面 / 0 非流形（含倒角）"),
        ("tri-r6i-g06-checks", A06 / "gate06-checks.json", "geometry-validation", "process", "gate06-numeric-checks", ["tri-r6i-g06-blend"], json.dumps(checks["gate06Check_results"], ensure_ascii=False)),
    ]
    for name in ("top-ortho", "hero", "pocket-macro", "edge-macro", "notch-macro", "low"):
        assets06.append((f"tri-r6i-g06-check-{name}", A06 / "checks" / f"{name}.png", "geometry-preview", "analysis", f"workbench-{name}", ["tri-r6i-g06-blend"], ""))
    for aid, path, slot, role, cls, srcs, note in assets06:
        base.upsert(manifest, base.asset(aid, "06-geometry", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s06["artifactIds"].append(aid)
    s06["validations"] = [{"id": k.replace(" ", "-").replace("/", "-").replace(",", "").replace("<", "lt").replace("(", "").replace(")", ""), "status": "pass" if v else "fail", "detail": k} for k, v in checks["gate06Check_results"].items()] + [
        {"id": "surface-detail-coverage", "status": "pass", "detail": "builder rev-007 10/10 + finalizer tags D01–D05, D08"},
        {"id": "mouth-fillet-edges", "status": "pass", "detail": f"{checks['pocket_mouth_fillet']['tagged_edges']} 条坑口边打权重，R {checks['pocket_mouth_fillet']['radius_mm']} mm × 6 段"},
    ]

    # ---- Gate 07 / 08 / 09 rev-002 ready_for_review (one lookdev blend)
    A07 = EV / "07-material/rev-002"
    for sid, rev_reason in (("07-material", "rev-001 placeholder"), ("08-lighting", "rev-001 placeholder"), ("09-environment", "rev-001 placeholder")):
        new_revision(st[sid], 2, rev_reason)
        st[sid]["status"] = "ready_for_review"
    common = [
        ("tri-r6i-lookdev-script", A07 / "lookdev_geeone.py", "material-source", "process", "bpy-lookdev-materials-lights-environment", ["tri-r6i-g06-blend"], "Gate 07 材质 / 08 灯光 / 09 环境 同一脚本；Cycles AgX"),
        ("tri-r6i-lookdev-blend", A07 / "geeone-lookdev-r002.blend", "material-source", "source-model", "lookdev-blend-r002", ["tri-r6i-lookdev-script"], ""),
        ("tri-r6i-lookdev-board", A07 / "renders" / "lookdev-review-board.png", "material-preview", "analysis", "lookdev-review-board", ["tri-r6i-lookdev-blend"], "六视图评审板"),
        ("tri-r6i-lookdev-turntable-mp4", A07 / "turntable" / "geeone-lookdev-turntable.mp4", "material-preview", "analysis", "turntable-recording-36-frames", ["tri-r6i-lookdev-blend"], "36 帧 / 12 fps 转台（Gate 07–09 交互替代证据）"),
        ("tri-r6i-lookdev-turntable-gif", A07 / "turntable" / "geeone-lookdev-turntable.gif", "material-preview", "analysis", "turntable-gif", ["tri-r6i-lookdev-turntable-mp4"], ""),
    ]
    for name in ("hero", "top-ortho", "low", "blade-macro-f0132", "cap-macro", "edge-macro"):
        common.append((f"tri-r6i-lookdev-{name}", A07 / "renders" / f"{name}.png", "material-preview", "analysis", f"cycles-{name}", ["tri-r6i-lookdev-blend"], "Cycles 96 spp 1400 px"))
    for aid, path, slot, role, cls, srcs, note in common:
        base.upsert(manifest, base.asset(aid, "07-material", slot, path, role, cls, "repository-generated", "repository", srcs, note))
    for sid in ("07-material", "08-lighting", "09-environment"):
        for aid, *_ in common:
            if aid not in st[sid]["artifactIds"]:
                st[sid]["artifactIds"].append(aid)
    st["07-material"]["validations"] = [
        {"id": "satin-not-mirror", "status": "pass", "detail": "M_Steel_Satin roughness 0.36 metallic 1（用户 09-05：satin 0.3–0.4）"},
        {"id": "anisotropy-disc-only", "status": "pass", "detail": "M_Disc_Turned anisotropic 0.7 径向 + 0.12 mm 同心 bump 仅在 14 扇区盘面；楔/鳞靠几何法线"},
        {"id": "hub-seat-dark", "status": "pass", "detail": "M_Hub_Dark 0.06 金属；暗缝 = 外悬下阴影"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认，未推送手机"},
    ]
    st["08-lighting"]["validations"] = [
        {"id": "three-light-studio", "status": "pass", "detail": "Key 2.4×1.6 R 暖白 / Fill 冷白 / Rim 细条（刻面星芒）；功率 ×250（mm 场景）；渐变天空 0.035→0.30"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]
    st["09-environment"]["validations"] = [
        {"id": "matte-floor-contact-shadow", "status": "pass", "detail": "哑光深灰地面，产品悬 2 mm，软接触阴影；无 HDRI 贴图"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]

    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 18:52 go-ahead:")[0]
        + " | 09-07 18:52 go-ahead: 用户“可以，继续推进吧”→ Gate 01 rev-003 / 02 rev-006 / 03 rev-005（合同）/ 04 rev-005（架构）/ 05 rev-007 记 approved（chat，静态视图证据）；Gate 06 rev-005 几何定稿（apply Boolean、坑口凸圆角、0.15 mm 微倒角，7 项 gate06 检查全过）ready_for_review；Gate 07/08/09 rev-002 Cycles lookdev（satin + 盘各向异性 + 暗毂座；三灯 + 渐变天空；哑光地面）+ 36 帧转台 ready_for_review。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        events = [
            {"type": "stage-approved", "stageId": sid, "notes": f"{sid} approved by the user's explicit chat instruction 2026-09-07 18:52 (exact wording: {USER_TEXT}); evidence mode: {EVIDENCE_MODE}"}
            for sid in ("01-intake", "02-analysis", "03-contract", "04-architecture", "05-blockout")
        ] + [
            {"type": "stage-revised", "stageId": "06-geometry", "notes": "06-geometry rev-005 ready_for_review: booleans applied, pocket mouth convex fillet R0.03 R (30 edges), 0.15 mm edge break; gate06 checks: " + json.dumps(checks["gate06Check_results"], ensure_ascii=False)},
            {"type": "stage-revised", "stageId": "07-material", "notes": "07-material rev-002 ready_for_review: satin steel 0.36, disc anisotropic radial 0.7 + concentric bump, dark hub seat; Cycles renders + 36-frame turntable"},
            {"type": "stage-revised", "stageId": "08-lighting", "notes": "08-lighting rev-002 ready_for_review: three-area-light studio + gradient sky (same lookdev blend)"},
            {"type": "stage-revised", "stageId": "09-environment", "notes": "09-environment rev-002 ready_for_review: matte dark floor, contact shadow (same lookdev blend)"},
        ]
        for ev in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
