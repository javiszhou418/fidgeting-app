"""Gate 05 blockout rev-006 for metal-three-blade: built from the Gate 02 rev-006 geometry contract (CAD v16 / spec v17).

User 2026-09-07 17:50: "我觉得不对，还是按照你之前的那一版来做吧" -> the external-script blockout rev-005 is REJECTED
(exact wording persisted) and the blockout is rebuilt from the repository's own Gate 02 analysis. Gate 01/02 stay
ready_for_review (the wording chooses the direction; it is not a Gate approval). Gate 05 rev-006 -> ready_for_review.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A05 = base.EV / "05-blockout/rev-006"
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "我觉得不对，还是按照你之前的那一版来做吧。"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s05 = base.stage(manifest, "05-blockout")
    assert s05["revision"] == 5
    # rev-005 (external script + rev-006 root pocket) rejected by the user
    s05.setdefault("historicalRevisions", []).append({"revision": 5, "artifactIds": list(s05["artifactIds"]), "status": "rejected", "reason": "用户 2026-09-07 17:50 原话：" + USER_TEXT + " —— 外部 rev-005 脚本（65 mm 圆角三角整体机身、45° 平切带、直壁打穿坑）方向作废，改按仓库 Gate 02 rev-006 分析重建"})
    s05.setdefault("historicalDecisions", []).append({"revision": 5, "decision": "rejected", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": USER_TEXT, "replacement": "rev-006 built from evidence/05-blockout/rev-006/geeone-gate02-geometry-contract.json"})
    s05["revision"] = 6
    s05["artifactIds"] = []
    s05["status"] = "ready_for_review"
    s05["decision"] = None

    instr = A05 / "user-instructions-2026-09-07-1750.md"
    instr.write_text(
        "# 用户指令 2026-09-07 17:50（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "解读：rev-005（外部脚本 + rev-006 执行说明）白模方向不对，按“你之前的那一版”= 仓库 Gate 02 rev-006 的分析（CAD v16 / spec v17 / 阴影图 v17）来做 Blender 白模。"
        "Gate 05 rev-005 记为 rejected，rev-006 由 `geeone-gate02-geometry-contract.json`（从 CAD v16 导出）驱动的 `build_geeone_gate02_blockout.py` 生成。\n\n"
        "状态：Gate 01/02 仍 ready_for_review（本句是方向选择，不是 Gate 批准）；Gate 05 rev-006 ready_for_review；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    assets = [
        ("tri-r6g-user-instructions-1750", instr, "white-model-source", "user-input", "user-instruction-exact-wording-2026-09-07-1750", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6g-geometry-contract", A05 / "geeone-gate02-geometry-contract.json", "white-model-source", "contract", "gate02-geometry-contract-r-units", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v16", "tri-r6-cad-v16-script"], "R 单位；轮廓/阶层为 r(θ) 表；六平面；坑口/底多边形（真圆角）；盖参数；85 mm 仅 provisional"),
        ("tri-r6g-contract-exporter", REPO / "tools/model-provenance-explorer/export_geeone_gate02_geometry.py", "white-model-source", "process", "gate02-geometry-contract-exporter", "repository-generated", "repository", ["tri-r6-cad-v16-script", "tri-r6-shaded-relief-v17-script"], "EDT 等距轮廓 → r(θ)；平面/坑/盖直接取自 CAD v16 模块"),
        ("tri-r6g-builder", A05 / "build_geeone_gate02_blockout.py", "white-model-source", "process", "bpy-deterministic-blockout-builder", "repository-generated", "repository", ["tri-r6g-geometry-contract"], "D01–D10 全部 `# detail:` 标记（coverage 10/10）；平面刻面精确裁剪；三环拉链缝合鸢形/Λ；漏斗坑 MANIFOLD Boolean；盖 14 扇/14 楔/14×2 鳞/14 边竖壁；上下镜像；无 Subdivision/Smooth"),
        ("tri-r6g-blend", A05 / "geeone-blockout-r006.blend", "white-model-source", "source-model", "blockout-blend-r006", "repository-generated", "repository", ["tri-r6g-builder", "tri-r6g-geometry-contract"], "Rotor_Body（求值 2125 顶点 / 2012 面 / 0 非流形）、Cap_Top/Cap_Bottom、Seam_Dark、刀体线框"),
    ]
    for name in ("top-ortho", "bottom-ortho", "hero", "left-oblique", "right-oblique", "low", "blade-macro-f0132", "edge-macro", "cap-macro", "notch-macro"):
        assets.append((f"tri-r6g-check-{name}", A05 / "checks" / f"{name}.png", "white-model-preview", "analysis", f"workbench-white-{name}", "repository-generated", "repository", ["tri-r6g-blend"], "Workbench STUDIO 单色 + cavity；白模评审视图"))
    for name in ("top", "hero", "left-oblique", "right-oblique", "low", "front", "back", "left", "right", "bottom"):
        assets.append((f"tri-r6g-view-{name}", A05 / "fixed-views" / f"{name}.png", "white-model-preview", "analysis", f"fixed-camera-pack-{name}", "repository-generated", "repository", ["tri-r6g-blend"], "capture_standard_views.py（EEVEE，场景材质）"))
    assets.append(("tri-r6g-fixed-views-report", A05 / "fixed-views" / "capture-wrapper-report.json", "white-model-preview", "process", "fixed-camera-pack-report", "repository-generated", "repository", ["tri-r6g-blend"], ""))
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in assets:
        base.upsert(manifest, base.asset(aid, "05-blockout", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"].startswith("tri-r5b-"):
            a["provenance"]["note"] = (a["provenance"].get("note", "") + " · rev-005 rejected 2026-09-07 17:50 (user: 按你之前的那一版来做)").strip(" ·")

    s05["validations"] = [
        {"id": "upstream-gates-pending", "status": "warn", "detail": "Gate 01 rev-003 / Gate 02 rev-006 仍 ready_for_review；用户 17:50“按照你之前的那一版来做”是方向选择，不是 Gate 批准；五项冲突（盖侧高 0.14 R、坑深、盖比例 0.485、平盘 0.82、盖顶 E1）按 Gate 02 现值建模，均为占位"},
        {"id": "surface-detail-coverage", "status": "pass", "detail": "check_surface_detail_coverage.py build_geeone_gate02_blockout.py → 10/10（D01–D10）"},
        {"id": "deterministic-source", "status": "pass", "detail": "bpy 构建器 + 几何合同 JSON（哈希链到 spec v17 / CAD v16）；无随机；重跑即重现"},
        {"id": "no-subdivision-no-smooth", "status": "pass", "detail": "所有面 flat；顶面为精确平面裁剪的 n-gon；鳞面为三角/五边扇；无 Subdivision、无 Shade Smooth"},
        {"id": "manifold-and-booleans", "status": "pass", "detail": "基础面片 0 非流形；盖座 + 6 个漏斗坑 MANIFOLD Boolean 后求值 2125 顶点 / 2012 面 / 0 非流形；zmax 0.1185 R（坑尖脊 0.11 R）"},
        {"id": "pocket-form", "status": "pass", "detail": "D08 v17：口沿外扩 0.03 / 平底内收 0.03 R、深 38% t、顶视真圆角（口 R0.05 / 底 R0.03）、底边凹圆角 R0.03（4 段弧）、开口进盖座；口沿凸圆角 R0.03 待 Gate 06 边倒角（warn 见下）"},
        {"id": "mouth-fillet-deferred", "status": "warn", "detail": "口沿凸圆角 R0.03（顶面→斜壁）在白模中为硬边，Gate 06 用 Boolean 生成边的倒角实现"},
        {"id": "edge-transition", "status": "pass", "detail": "D05 v17：0.14 R 过渡 = A 层 0.07 R@22°（大面）+ 鸢形 38° / Λ 53° 咬合（尖 25%/85%，节距 0.18 R → 33 片/圈，每边 4–5）到中面；D06 无竖壁"},
        {"id": "planform-and-notch", "status": "pass", "detail": "D07/D09：凸弧叶边 R1.37 R、尖叶尖、根部内收弧止于盖圈 52°、缺口露盖 ≈16°（外轮廓 r(θ) 来自 CAD v16 planform v7）"},
        {"id": "cap", "status": "pass", "detail": "D01–D03：盘 0.82×盖 14 扇区凹 3°（占位）、冠环 14 楔 28 三角 20°、裙 14×2（45°/75°）、竖壁 0.057 R、盖侧高 0.14 R（占位）；上下盖镜像 D10"},
        {"id": "scale-provisional", "status": "warn", "detail": "2R = 85 mm user-authorized-provisional（总控 09-05 23:14）；所有 mm 非 measured"},
        {"id": "materials-lighting-not-in-scope", "status": "warn", "detail": "白模阶段：Workbench 单色；固定相机包为 EEVEE 场景材质（satin 钢 + 暗缝）仅供轮廓核对；Gate 07/08 另议"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 17:50 blockout r006:")[0]
        + " | 09-07 17:50 blockout r006: 用户“我觉得不对，还是按照你之前的那一版来做吧”→ rev-005 外部方向 rejected；从 CAD v16 导出几何合同 JSON，bpy 构建器生成白模（凸弧三叶 + 缺口露盖、T/F/C 硬切顶、A 层 + 鸢形/Λ 过渡到中面、漏斗坑真圆角、14 扇盘 + 14 楔冠环 + 14×2 裙 + 竖壁盖、上下镜像），coverage 10/10，Boolean 后 0 非流形，Workbench 十视图 + 固定相机包。Gate 05 rev-006 ready_for_review；Gate 01/02 仍 ready_for_review；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for ev in (
            {"type": "stage-rejected", "stageId": "05-blockout", "notes": "05-blockout rev-005 (external spinner_rev005.py + rev-006 root-pocket instructions) rejected by the user. Exact wording 2026-09-07 17:50: " + USER_TEXT},
            {"type": "stage-revised", "stageId": "05-blockout", "notes": "05-blockout rev-006 ready_for_review: white model built from the Gate 02 rev-006 geometry contract (CAD v16 / spec v17) by build_geeone_gate02_blockout.py — coverage D01–D10 10/10, 0 non-manifold after MANIFOLD booleans, Workbench review views + fixed camera pack. No approval; Gate 01/02 still ready_for_review; 85 mm provisional."},
        ):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "stage05": s05["revision"], "assets": len(added)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
