"""User 2026-09-07 22:51 on lookdev rev-003 (arrow at the cap edge in the top view):
"就这个 bevel 可以再厚一点。就是这两片龙鳞的这个高度可以再高，然后中间的那个内凹的效果感觉还是不够明显。"

Bookkeeping for the spec v20 amendment (D01 dish 8° + disc 0.80 cap; D02/D03 skirt rows taller/wider, cap side 0.16 R; D09 seam
height follows):
  * Gate 02 rev-006 stays approved; spec hash refreshed, user wording + screenshot registered. Gate 03 / 05 stay approved with a
    warn that the cap block changed again (the user asked for no new white model).
  * Gate 06 -> rev-007 (caps + hub seats rebuilt from the v20 contract, manifold, 11 checks) ready_for_review.
  * Gate 07/08/09 -> rev-004 (same materials / lights / environment as rev-003, re-rendered on geometry rev-007) ready_for_review.
Nothing downstream is approved; no export, Unity, build, install.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

EV = base.EV
REPO = base.REPO
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "就这个 bevel 可以再厚一点。就是这两片龙鳞的这个高度可以再高，然后中间的那个内凹的效果感觉还是不够明显。"
AMEND = "user 2026-09-07 22:51 spec v20 amendment (D01 dish 5°→8°, disc 0.82→0.80 cap; D02 crown 0.09@18°; D03 rows 0.07@50° / 0.04@72°, cap side 0.14→0.16 R; D09 hub seat 0.057→0.0456 R)"


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


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}

    # ---- Gate 02: user wording + screenshot, spec v20 hash refresh
    A02 = EV / "02-analysis/rev-006"
    base.upsert(manifest, base.asset("tri-r6-user-instructions-2251", "02-analysis", "analysis-board", A02 / "user-instructions-2026-09-07-2251.md", "user-input", "user-instruction-exact-wording-2026-09-07-2251", "user-provided", "user", ["tri-r6j-lookdev-top-ortho"], USER_TEXT))
    base.upsert(manifest, base.asset("tri-r6-user-markup-2251", "02-analysis", "analysis-board", A02 / "user-markup-2026-09-07-2251-cap-bevel.png", "user-input", "user-screenshot-rev-003-top-view-arrow-cap-edge", "user-provided", "user", ["tri-r6j-lookdev-top-ortho"], "红箭头指盘外盖缘带（bevel）"))
    for aid in ("tri-r6-user-instructions-2251", "tri-r6-user-markup-2251"):
        if aid not in st["02-analysis"]["artifactIds"]:
            st["02-analysis"]["artifactIds"].append(aid)
    refresh(manifest, "tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", ["tri-r6-user-instructions-2251"], "; v20 (user 22:51) D01 dish 8° + disc 0.80 cap, D02/D03 taller skirt rows + cap side 0.16 R, D09 seam height 0.0456 R — all provisional")
    refresh(manifest, "tri-r6g-contract-exporter", REPO / "tools/model-provenance-explorer/export_geeone_gate02_geometry.py", (), " · --out <dir> added 2026-09-07 22:51 (writes the contract into the target Gate 06 revision)")
    set_validation(st["02-analysis"], "cap-amended-2251", "warn", f"{AMEND}; provisional visibility/proportion amendment of the approved cap definition, authorised by the user's wording; reference-cad-from-video-v17.png still shows the v18 tier values (drawing not regenerated); Gate 02 approval kept")
    set_validation(st["03-contract"], "cap-block-amended-2251", "warn", "contract cap block regenerated in 06-geometry/rev-007 with spec v20; 03-contract/rev-005 copy is the approved history (dish 3°, rows 0.06@45°/0.02@75°, side 0.14 R)")
    set_validation(st["05-blockout"], "cap-amended-2251", "warn", "white model rev-007 caps/hub seats are the approved 3° / 0.14 R geometry; Gate 06 rev-007 rebuilds caps and hub seats from the v20 contract; user asked for no new white model")

    # ---- Gate 06 rev-007
    s06 = st["06-geometry"]
    new_revision(s06, 7, "user 2026-09-07 22:51: skirt rows taller/thicker, dish more concave -> caps + hub seats rebuilt from spec v20")
    s06["status"] = "ready_for_review"
    A06 = EV / "06-geometry/rev-007"
    checks = json.loads((A06 / "gate06-checks.json").read_text(encoding="utf-8"))
    cap = checks["cap"]
    assets06 = [
        ("tri-r6k-g06-contract", A06 / "geeone-gate02-geometry-contract.json", "geometry-source", "contract", "gate02-geometry-contract-r-units", ["tri-r6-surface-detail-spec", "tri-r6j-g06-contract"], "spec v20 hash-linked; cap tableToCap 0.80, dish 8°, tiers 0.09@18° / 0.07@50° / 0.04@72°, side 0.16 R, hub seat 0.0456 R"),
        ("tri-r6k-g06-script", A06 / "finalize_geeone_geometry.py", "geometry-source", "process", "bpy-geometry-finalizer", ["tri-r6h-blend", "tri-r6k-g06-contract", "tri-r6j-g06-script"], "rev-007: + rebuild_hub_seat (cylinder r 0.455 R, TOP -> lip) so the seat follows the taller skirt; caps rebuilt as rev-006"),
        ("tri-r6k-g06-blend", A06 / "geeone-geometry-r007.blend", "geometry-source", "source-model", "geometry-blend-r007", ["tri-r6k-g06-script"], f"Rotor_Body {checks['rotor_final']['verts']} verts / {checks['rotor_final']['faces']} faces / 0 non-manifold; caps 57/99/0; dish {cap['dish_slope_deg']}° = {cap['dish_depth_mm']} mm, skirt rows {cap['skirt_rows_drop_mm']} mm, hub seat {cap['hub_seat_height_mm']} mm (all provisional)"),
        ("tri-r6k-g06-checks", A06 / "gate06-checks.json", "geometry-validation", "process", "gate06-numeric-checks", ["tri-r6k-g06-blend"], json.dumps(checks["gate06Check_results"], ensure_ascii=False)),
    ]
    for name in ("top-ortho", "hero", "pocket-macro", "edge-macro", "notch-macro", "low"):
        assets06.append((f"tri-r6k-g06-check-{name}", A06 / "checks" / f"{name}.png", "geometry-preview", "analysis", f"workbench-{name}", ["tri-r6k-g06-blend"], ""))
    for aid, path, slot, role, cls, srcs, note in assets06:
        base.upsert(manifest, base.asset(aid, "06-geometry", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s06["artifactIds"].append(aid)
    s06["validations"] = [{"id": k.replace(" ", "-").replace("/", "-").replace(",", "").replace("<", "lt").replace("(", "").replace(")", "").replace(">=", "ge").replace("<=", "le"), "status": "pass" if v else "fail", "detail": k} for k, v in checks["gate06Check_results"].items()] + [
        {"id": "surface-detail-coverage", "status": "pass", "detail": "builder rev-007 10/10 + finalizer tags D01–D05, D08–D10"},
        {"id": "mouth-fillet-edges", "status": "pass", "detail": f"{checks['pocket_mouth_fillet']['tagged_edges']} 条坑口边打权重，R {checks['pocket_mouth_fillet']['radius_mm']} mm × 6 段"},
        {"id": "cap-values-provisional", "status": "warn", "detail": f"dish 8°, disc 0.80 cap, rows 0.07@50°/0.04@72°, side 0.16 R, hub seat {cap['hub_seat_height_R']} R: user-driven provisional values; video gives only dish ≤2° bound and side 0.14 R ±20 %"},
    ]

    # ---- Gate 07 / 08 / 09 rev-004
    A07 = EV / "07-material/rev-004"
    for sid in ("07-material", "08-lighting", "09-environment"):
        new_revision(st[sid], 4, "user 2026-09-07 22:51: cap edge rows taller + dish deeper -> re-rendered on geometry rev-007 (materials / lights / environment unchanged)")
        st[sid]["status"] = "ready_for_review"
    common = [
        ("tri-r6k-lookdev-script", A07 / "lookdev_geeone.py", "material-source", "process", "bpy-lookdev-materials-lights-environment", ["tri-r6k-g06-blend", "tri-r6j-lookdev-script"], "identical materials / lights / floor to rev-003; blend name r004"),
        ("tri-r6k-lookdev-blend", A07 / "geeone-lookdev-r004.blend", "material-source", "source-model", "lookdev-blend-r004", ["tri-r6k-lookdev-script"], ""),
        ("tri-r6k-lookdev-board", A07 / "renders" / "lookdev-review-board.png", "material-preview", "analysis", "lookdev-review-board", ["tri-r6k-lookdev-blend"], "七视图评审板"),
        ("tri-r6k-cap-tiers-board", A07 / "renders" / "cap-tiers-before-after-board.png", "material-preview", "analysis", "cap-tiers-before-after-rev-003-vs-rev-004", ["tri-r6k-lookdev-blend", "tri-r6j-lookdev-blend"], "顶视盖局部 / cap-macro / disc-macro / low：rev-003 vs rev-004"),
        ("tri-r6k-cap-section", A07 / "renders" / "cap-section-v19-vs-v20.png", "material-preview", "analysis", "cap-section-from-contract-v19-vs-v20", ["tri-r6j-g06-contract", "tri-r6k-g06-contract"], "盖 A–A 剖面（合同直接生成）：凹深 1.48→2.32 mm、两排鳞 2.78→4.26 mm、盖侧 5.95→6.8 mm、毂座 2.42→1.94 mm，均 provisional"),
        ("tri-r6k-lookdev-turntable-mp4", A07 / "turntable" / "geeone-lookdev-turntable.mp4", "material-preview", "analysis", "turntable-recording-36-frames", ["tri-r6k-lookdev-blend"], "36 帧 / 12 fps 转台（Gate 07–09 交互替代证据）"),
        ("tri-r6k-lookdev-turntable-gif", A07 / "turntable" / "geeone-lookdev-turntable.gif", "material-preview", "analysis", "turntable-gif", ["tri-r6k-lookdev-turntable-mp4"], ""),
    ]
    for name in ("hero", "top-ortho", "low", "blade-macro-f0132", "cap-macro", "disc-macro", "edge-macro"):
        common.append((f"tri-r6k-lookdev-{name}", A07 / "renders" / f"{name}.png", "material-preview", "analysis", f"cycles-{name}", ["tri-r6k-lookdev-blend"], "Cycles 96 spp 1400 px"))
    for aid, path, slot, role, cls, srcs, note in common:
        base.upsert(manifest, base.asset(aid, "07-material", slot, path, role, cls, "repository-generated", "repository", srcs, note))
    for sid in ("07-material", "08-lighting", "09-environment"):
        for aid, *_ in common:
            if aid not in st[sid]["artifactIds"]:
                st[sid]["artifactIds"].append(aid)
    st["07-material"]["validations"] = [
        {"id": "satin-not-mirror", "status": "pass", "detail": "M_Steel_Satin roughness 0.36 metallic 1（用户 09-05：satin 0.3–0.4；用户 09-07 19:42：质感挺漂亮的）"},
        {"id": "anisotropy-disc-only", "status": "pass", "detail": "M_Disc_Turned anisotropic 0.4 径向 + 0.12 mm 同心 bump（0.12 强度）仅在 14 扇区盘面；楔/鳞靠几何法线"},
        {"id": "d01-slices-read", "status": "pass", "detail": "disc-macro / cap-macro：14 个平面扇区有明暗台阶、硬折边；盘凹 8° 梯度比 rev-003 更强"},
        {"id": "hub-seat-dark", "status": "pass", "detail": "M_Hub_Dark 0.06 金属；暗缝 = 外悬下阴影（毂座 1.94 mm）"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认，未推送手机"},
    ]
    st["08-lighting"]["validations"] = [
        {"id": "three-light-studio", "status": "pass", "detail": "Key 2.4×1.6 R 暖白 / Fill 冷白 / Rim 细条（刻面星芒）；功率 ×250（mm 场景）；渐变天空 0.035→0.30；rev-004 未改"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]
    st["09-environment"]["validations"] = [
        {"id": "matte-floor-contact-shadow", "status": "pass", "detail": "哑光深灰地面，产品悬 2 mm，软接触阴影；无 HDRI 贴图；rev-004 未改"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]

    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 22:51 cap-tiers:")[0]
        + " | 09-07 22:51 cap-tiers: 用户“bevel 可以再厚一点…这两片龙鳞的高度可以再高…内凹的效果还是不够明显”→ spec v20（盘 8° / 0.80 盖；裙两排 0.07@50° / 0.04@72°，高 2.8→4.3 mm；盖侧 0.16 R；毂座 0.0456 R）；Gate 06 rev-007 盖 + 毂座重建（11 项检查全过）ready_for_review；Gate 07/08/09 rev-004（材质/灯光/环境不变，几何 rev-007 重渲 + 转台 + 剖面对照）ready_for_review；Gate 02/03/05 保持 approved 并标 warn。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        events = [
            {"type": "stage-note", "stageId": "02-analysis", "notes": f"user 2026-09-07 22:51 (exact wording: {USER_TEXT}) -> surface-detail-spec v20: {AMEND}; Gate 02 approval kept (user-driven provisional amendment)"},
            {"type": "stage-revised", "stageId": "06-geometry", "notes": "06-geometry rev-007 ready_for_review: caps (dish 8° = 2.32 mm, disc 0.80 cap, rows 0.07@50°/0.04@72° = 4.26 mm) and hub seats (1.94 mm) rebuilt from the v20 contract; gate06 checks: " + json.dumps(checks["gate06Check_results"], ensure_ascii=False)},
            {"type": "stage-revised", "stageId": "07-material", "notes": "07-material rev-004 ready_for_review: unchanged materials re-rendered on geometry rev-007; boards: lookdev-review-board, cap-tiers-before-after-board, cap-section-v19-vs-v20; 36-frame turntable"},
            {"type": "stage-revised", "stageId": "08-lighting", "notes": "08-lighting rev-004 ready_for_review: unchanged three-area-light studio + gradient sky, re-rendered on geometry rev-007"},
            {"type": "stage-revised", "stageId": "09-environment", "notes": "09-environment rev-004 ready_for_review: unchanged matte floor + contact shadow, re-rendered on geometry rev-007"},
        ]
        for ev in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
