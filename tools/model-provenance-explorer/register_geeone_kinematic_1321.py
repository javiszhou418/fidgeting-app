"""User 2026-09-08 07:13 "OK还有一点就是这个陀螺的三个页面是可以转的，你确保在结构上是正确的，没问题的话你可以推进下一步"
and 13:21 "这个不是一体的，叶片是分开转的" (low-angle turntable frame attached).

Bookkeeping:
  * 07:13 "OK" = chat approval of the lookdev appearance: Gate 07/08/09 rev-004 -> approved (static boards + 36-frame turntable
    recording; the mp4 was open in the user's IDE). It is NOT an approval of Gate 06 rev-007: the same message demands a
    structural check, and 13:21 rejects the one-piece hub/rotor structure of rev-007.
  * Gate 06 rev-007 -> rejected (exact wording 13:21), rev-008 (rotor through-bore + static Hub_Core, kinematic checks)
    ready_for_review. Gate 04 -> rev-006 (kinematic split architecture) ready_for_review; rev-005 approval kept as history.
  * Gate 07/08/09 -> rev-005 (same materials / lights / floor, re-rendered on rev-008 + Cycles section views + rotor-only spin)
    ready_for_review. Gate 02 spec v21 hash refresh; Gate 02/03/05 keep their approvals with a warn.
Nothing exported, no Unity, no build, no install.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

EV = base.EV
REPO = base.REPO
NOW = datetime.now(timezone.utc).isoformat()
OK_TEXT = "OK还有一点就是这个陀螺的三个页面是可以转的，你确保在结构上是正确的，没问题的话你可以推进下一步"
REJ_TEXT = "这个不是一体的，叶片是分开转的"
OK_EVIDENCE = "chat approval after the rev-004 review boards and the 36-frame Cycles turntable recording (turntable mp4 open in the user's IDE); no interactive 3D viewer"


def new_revision(stage, rev, reason):
    if stage["revision"] != rev:
        stage.setdefault("historicalRevisions", []).append({"revision": stage["revision"], "artifactIds": list(stage["artifactIds"]), "status": stage["status"], "reason": reason})
        stage["revision"] = rev
        stage["artifactIds"] = []
        stage.pop("staleReason", None)
    stage["decision"] = None


def set_validation(stage, vid, status, detail):
    stage["validations"] = [v for v in stage.get("validations", []) if v["id"] != vid] + [{"id": vid, "status": status, "detail": detail}]


def refresh(manifest, asset_id, path, extra_sources=(), note_suffix=""):
    a = next(a for a in manifest["assets"] if a["id"] == asset_id)
    base.upsert(manifest, base.asset(asset_id, a["stageId"], a["slot"], path, a["role"], a["provenance"]["contentClass"], a["provenance"]["origin"], a["provenance"]["assertedBy"], list(dict.fromkeys(a.get("sourceAssetIds", []) + list(extra_sources))), a["provenance"]["note"] + note_suffix))


def decide(stage, action, wording, notes, evidence):
    rec = {"revision": stage["revision"], "decision": "approved" if action == "approve" else "rejected", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": wording, "evidenceMode": evidence, "notes": notes}
    stage.setdefault("historicalDecisions", []).append(rec)
    stage["decision"] = {"action": action, "notes": notes, "decidedBy": "user", "decidedAt": NOW, "channel": "chat", "exactWording": wording, "evidenceMode": evidence}


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}
    A02 = EV / "02-analysis/rev-006"

    # ---- Gate 02: user wording + screenshot, spec v21
    base.upsert(manifest, base.asset("tri-r6-user-instructions-0713-1321", "02-analysis", "analysis-board", A02 / "user-instructions-2026-09-08-0713-1321.md", "user-input", "user-instruction-exact-wording-2026-09-08-0713-1321", "user-provided", "user", ["tri-r6k-lookdev-board", "tri-r6k-lookdev-turntable-mp4"], OK_TEXT + " | " + REJ_TEXT))
    base.upsert(manifest, base.asset("tri-r6-user-markup-1321", "02-analysis", "analysis-board", A02 / "user-markup-2026-09-08-1321-one-piece.png", "user-input", "user-screenshot-rev-004-turntable-low-angle", "user-provided", "user", ["tri-r6k-lookdev-turntable-mp4"], "低角度转台帧：毂座 + 转子 + 盖读成一体"))
    for aid in ("tri-r6-user-instructions-0713-1321", "tri-r6-user-markup-1321"):
        if aid not in st["02-analysis"]["artifactIds"]:
            st["02-analysis"]["artifactIds"].append(aid)
    refresh(manifest, "tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", ["tri-r6-user-instructions-0713-1321"], "; v21 (user 13:21) kinematic split: static Hub_Core r 0.41 R through a rotor bore r 0.425 R, gap 0.015 R, cap overhang 0.075 R — provisional")
    refresh(manifest, "tri-r6g-contract-exporter", REPO / "tools/model-provenance-explorer/export_geeone_gate02_geometry.py", (), " · v21 cap.kinematics / rotorBoreRadiusToR / hubCoreRadiusToR")
    set_validation(st["02-analysis"], "kinematic-amended-1321", "warn", f"user 13:21 (exact wording: {REJ_TEXT}) -> spec v21 D03/D09: hub is a static core through a rotor bore; radii provisional; Gate 02 approval kept")
    set_validation(st["03-contract"], "cap-block-amended-1321", "warn", "contract regenerated in 06-geometry/rev-008 with spec v21 (rotor bore 0.425 R, hub core 0.41 R static, overhang 0.075 R); 03-contract/rev-005 copy stays the approved history")
    set_validation(st["05-blockout"], "kinematic-amended-1321", "warn", "white model rev-007 has a solid rotor + Hub_Seat_Top/Bottom; Gate 06 rev-008 cuts the bore and builds the static Hub_Core from the v21 contract; user asked for no new white model")

    # ---- Gate 04 rev-006 (kinematic split) ready_for_review; rev-005 approval preserved
    s04 = st["04-architecture"]
    new_revision(s04, 6, "user 2026-09-08 13:21: rotor must be a separate part spinning around the static cap + hub assembly")
    s04["status"] = "ready_for_review"
    base.upsert(manifest, base.asset("tri-r6l-architecture-md", "04-architecture", "interaction-architecture", EV / "04-architecture/rev-006/architecture.md", "contract", "parts-ownership-pivot-hierarchy-kinematic-split", "repository-generated", "repository", ["tri-r6l-g06-contract", "tri-r6-user-instructions-0713-1321"], "Fixed_Root = Cap_Top + Cap_Bottom + Hub_Core；Rotor_Root = Rotor_Body（通孔 R0.425，绕 Z）；间隙 0.64 / 0.52 mm；连接环 2.97 mm"))
    s04["artifactIds"].append("tri-r6l-architecture-md")
    s04["validations"] = [
        {"id": "kinematics-only", "status": "pass", "detail": "仅绕 Z 自由旋转；无阻尼/力感/Haptics 内容"},
        {"id": "two-part-structure", "status": "pass", "detail": "转子与盖 + 毂芯是两件：径向间隙 0.015 R、竖向 0.52 mm、连接环 ≥ 0.05 R（Gate 06 rev-008 kinematics 8/8）"},
        {"id": "user-confirmation-pending", "status": "warn", "detail": "等待用户确认拆分方式（毂芯静止 vs 转子）与盖缘外悬 0.075 R"},
    ]

    # ---- Gate 06: rev-007 rejected (13:21), rev-008 ready_for_review
    s06 = st["06-geometry"]
    assert s06["revision"] == 7
    decide(s06, "reject", REJ_TEXT, "rev-007: Hub_Seat_Top/Bottom sat on a solid rotor; cap + hub + blades read as one piece. Replaced by rev-008 (rotor through-bore + static Hub_Core).", "low-angle turntable frame (user screenshot) + rev-004 turntable recording")
    new_revision(s06, 8, "rejected 2026-09-08 13:21: one-piece structure; rev-008 = kinematic split")
    s06["status"] = "ready_for_review"
    A06 = EV / "06-geometry/rev-008"
    checks = json.loads((A06 / "gate06-checks.json").read_text(encoding="utf-8"))
    kin = checks["kinematics"]
    assets06 = [
        ("tri-r6l-g06-contract", A06 / "geeone-gate02-geometry-contract.json", "geometry-source", "contract", "gate02-geometry-contract-r-units", ["tri-r6-surface-detail-spec", "tri-r6k-g06-contract"], "spec v21 hash-linked; cap.kinematics fixed = caps + Hub_Core, rotating = Rotor_Body; bore 0.425 R, hub 0.41 R"),
        ("tri-r6l-g06-script", A06 / "finalize_geeone_geometry.py", "geometry-source", "process", "bpy-geometry-finalizer", ["tri-r6h-blend", "tri-r6l-g06-contract", "tri-r6k-g06-script"], "rev-008: + cut_rotor_bore (EXACT, 192 seg) + rebuild_hub_core (cap-to-cap static cylinder) + kinematic_checks (clearances, ring width by ray-cast, centroid, inertia) + half-section renders"),
        ("tri-r6l-g06-blend", A06 / "geeone-geometry-r008.blend", "geometry-source", "source-model", "geometry-blend-r008", ["tri-r6l-g06-script"], f"Rotor_Body {checks['rotor_final']['verts']} verts / {checks['rotor_final']['faces']} faces / 0 non-manifold, bore {checks['rotor_bore']['radius_mm']} mm; Hub_Core r {kin['hub_core_R']} R static; clearance {kin['radial_clearance_mm']} mm radial / {kin['vertical_clearance_mm']} mm vertical"),
        ("tri-r6l-g06-checks", A06 / "gate06-checks.json", "geometry-validation", "process", "gate06-numeric-checks", ["tri-r6l-g06-blend"], json.dumps(checks["gate06Check_results"], ensure_ascii=False)),
    ]
    for name in ("top-ortho", "hero", "pocket-macro", "edge-macro", "notch-macro", "low", "kinematic-section", "kinematic-section-macro", "kinematic-junction-macro"):
        assets06.append((f"tri-r6l-g06-check-{name}", A06 / "checks" / f"{name}.png", "geometry-preview", "analysis", f"workbench-{name}", ["tri-r6l-g06-blend"], "静止件蓝 / 转子灰" if name.startswith("kinematic") else ""))
    for aid, path, slot, role, cls, srcs, note in assets06:
        base.upsert(manifest, base.asset(aid, "06-geometry", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s06["artifactIds"].append(aid)
    s06["validations"] = [{"id": k.replace(" ", "-").replace("/", "-").replace(",", "").replace("<", "lt").replace("(", "").replace(")", "").replace(">=", "ge").replace("<=", "le").replace("|", "").replace("=", ""), "status": "pass" if v else "fail", "detail": k} for k, v in checks["gate06Check_results"].items()] + [
        {"id": "surface-detail-coverage", "status": "pass", "detail": "builder rev-007 10/10 + finalizer tags D01–D05, D08–D10"},
        {"id": "mouth-fillet-edges", "status": "pass", "detail": f"{checks['pocket_mouth_fillet']['tagged_edges']} 条坑口边打权重，R {checks['pocket_mouth_fillet']['radius_mm']} mm × 6 段"},
        {"id": "kinematic-values-provisional", "status": "warn", "detail": f"bore {kin['rotor_bore_R']} R / hub {kin['hub_core_R']} R / gap {kin['radial_clearance_R']} R / cap overhang 0.075 R are user-driven provisional values (video cannot resolve the bearing); ring at notches {kin['ring_width_at_notch_min_mm']} mm"},
    ]

    # ---- Gate 07 / 08 / 09: rev-004 approved (07:13 OK), rev-005 ready_for_review
    A07 = EV / "07-material/rev-005"
    for sid, note in (("07-material", "satin steel 0.36 / disc anisotropic 0.4 + turning bump / dark hub"), ("08-lighting", "three-area-light studio + gradient sky"), ("09-environment", "matte floor + contact shadow")):
        s = st[sid]
        assert s["revision"] == 4
        s["validations"] = [v for v in s["validations"] if v["id"] != "visual-approval-pending"] + [{"id": "approval-evidence-mode", "status": "warn", "detail": OK_EVIDENCE}]
        decide(s, "approve", OK_TEXT, f"用户 07:13 “OK…” 对 rev-004 评审板 + 转台：认可 {note}。附带的结构条件在 Gate 04/06 处理。", OK_EVIDENCE)
        s["status"] = "approved"
        new_revision(s, 5, "re-rendered on geometry rev-008 (kinematic split); materials / lights / floor unchanged from the approved rev-004")
        s["status"] = "ready_for_review"
    common = [
        ("tri-r6l-lookdev-script", A07 / "lookdev_geeone.py", "material-source", "process", "bpy-lookdev-materials-lights-environment", ["tri-r6l-g06-blend", "tri-r6k-lookdev-script"], "same materials as rev-004; Hub_Core = M_Hub_Dark; + Cycles half-section (static tinted) + junction macro + --spin (Rotor_Body only)"),
        ("tri-r6l-lookdev-blend", A07 / "geeone-lookdev-r005.blend", "material-source", "source-model", "lookdev-blend-r005", ["tri-r6l-lookdev-script"], ""),
        ("tri-r6l-lookdev-board", A07 / "renders" / "lookdev-review-board.png", "material-preview", "analysis", "lookdev-review-board", ["tri-r6l-lookdev-blend"], "八视图评审板"),
        ("tri-r6l-kinematic-board", A07 / "renders" / "kinematic-review-board.png", "material-preview", "analysis", "kinematic-split-review-board", ["tri-r6l-lookdev-blend", "tri-r6l-g06-check-kinematic-section", "tri-r6k-lookdev-low"], "半剖 / 交界 / spin 帧 / rev-004 对照"),
        ("tri-r6l-rotor-spin-mp4", A07 / "spin" / "geeone-rotor-spin.mp4", "material-preview", "analysis", "rotor-only-spin-recording-24-frames", ["tri-r6l-lookdev-blend"], "只有 Rotor_Body 转 120°（24 帧 / 12 fps），盖 + 毂芯静止 —— 运动学证据"),
        ("tri-r6l-rotor-spin-gif", A07 / "spin" / "geeone-rotor-spin.gif", "material-preview", "analysis", "rotor-only-spin-gif", ["tri-r6l-rotor-spin-mp4"], ""),
        ("tri-r6l-lookdev-turntable-mp4", A07 / "turntable" / "geeone-lookdev-turntable.mp4", "material-preview", "analysis", "turntable-recording-36-frames", ["tri-r6l-lookdev-blend"], "36 帧 / 12 fps 转台"),
        ("tri-r6l-lookdev-turntable-gif", A07 / "turntable" / "geeone-lookdev-turntable.gif", "material-preview", "analysis", "turntable-gif", ["tri-r6l-lookdev-turntable-mp4"], ""),
    ]
    for name in ("hero", "top-ortho", "low", "blade-macro-f0132", "cap-macro", "disc-macro", "edge-macro", "kinematic-section", "kinematic-section-macro", "kinematic-junction-macro"):
        common.append((f"tri-r6l-lookdev-{name}", A07 / "renders" / f"{name}.png", "material-preview", "analysis", f"cycles-{name}", ["tri-r6l-lookdev-blend"], "Cycles 96 spp 1400 px"))
    for aid, path, slot, role, cls, srcs, note in common:
        base.upsert(manifest, base.asset(aid, "07-material", slot, path, role, cls, "repository-generated", "repository", srcs, note))
    for sid in ("07-material", "08-lighting", "09-environment"):
        for aid, *_ in common:
            if aid not in st[sid]["artifactIds"]:
                st[sid]["artifactIds"].append(aid)
    st["07-material"]["validations"] = [
        {"id": "satin-not-mirror", "status": "pass", "detail": "M_Steel_Satin roughness 0.36 metallic 1（用户 07:13 OK）"},
        {"id": "anisotropy-disc-only", "status": "pass", "detail": "M_Disc_Turned anisotropic 0.4 径向 + 0.12 mm 同心 bump 仅在 14 扇区盘面"},
        {"id": "hub-core-dark", "status": "pass", "detail": "Hub_Core = M_Hub_Dark（静止暗柱）"},
        {"id": "materials-unchanged-from-approved", "status": "pass", "detail": "rev-005 材质 / 灯光 / 地面与已批准的 rev-004 完全一致，只换几何 rev-008"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "结构拆分后的外观待确认；未推送手机"},
    ]
    st["08-lighting"]["validations"] = [{"id": "three-light-studio", "status": "pass", "detail": "同 rev-004（已批准）"}, {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"}]
    st["09-environment"]["validations"] = [{"id": "matte-floor-contact-shadow", "status": "pass", "detail": "同 rev-004（已批准）"}, {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"}]

    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-08 07:13/13:21 kinematic:")[0]
        + " | 09-08 07:13/13:21 kinematic: 用户 07:13“OK…三个页面是可以转的，你确保在结构上是正确的”→ Gate 07/08/09 rev-004 approved（chat，静态板 + 转台录像）；13:21“这个不是一体的，叶片是分开转的”→ Gate 06 rev-007 rejected；spec v21 运动学拆分：转子通孔 R0.425 + 静止毂芯 R0.41 贯穿两盖（径向间隙 0.64 mm、竖向 0.52 mm、连接环 2.97 mm；质心在轴、Z 主轴）；Gate 04 rev-006、Gate 06 rev-008、Gate 07/08/09 rev-005（含半剖 + 转子单独旋转 24 帧）ready_for_review。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        events = [
            {"type": "stage-approved", "stageId": sid, "notes": f"{sid} rev-004 approved by the user's explicit chat instruction 2026-09-08 07:13 (exact wording: {OK_TEXT}); evidence mode: {OK_EVIDENCE}"}
            for sid in ("07-material", "08-lighting", "09-environment")
        ] + [
            {"type": "stage-rejected", "stageId": "06-geometry", "notes": f"06-geometry rev-007 rejected 2026-09-08 13:21 (exact wording: {REJ_TEXT}): hub seats on a solid rotor read as one piece"},
            {"type": "stage-note", "stageId": "02-analysis", "notes": "surface-detail-spec v21: D03/D09 kinematic split — static Hub_Core r 0.41 R through rotor bore r 0.425 R, gap 0.015 R, cap overhang 0.075 R (provisional)"},
            {"type": "stage-revised", "stageId": "04-architecture", "notes": "04-architecture rev-006 ready_for_review: Fixed_Root = Cap_Top + Cap_Bottom + Hub_Core; Rotor_Root = Rotor_Body (through-bore); clearances 0.64 mm radial / 0.52 mm vertical; ring 2.97 mm; rev-005 approval kept as history"},
            {"type": "stage-revised", "stageId": "06-geometry", "notes": "06-geometry rev-008 ready_for_review: rotor bore + static Hub_Core; checks: " + json.dumps(checks["gate06Check_results"], ensure_ascii=False)},
            {"type": "stage-revised", "stageId": "07-material", "notes": "07-material rev-005 ready_for_review: materials unchanged from approved rev-004, re-rendered on rev-008; kinematic section views + rotor-only spin 24 frames + turntable 36 frames"},
            {"type": "stage-revised", "stageId": "08-lighting", "notes": "08-lighting rev-005 ready_for_review: unchanged lights re-rendered on rev-008"},
            {"type": "stage-revised", "stageId": "09-environment", "notes": "09-environment rev-005 ready_for_review: unchanged floor re-rendered on rev-008"},
        ]
        for ev in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
