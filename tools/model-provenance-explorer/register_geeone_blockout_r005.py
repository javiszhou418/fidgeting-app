"""Register Gate 05 blockout rev-005 (user-directed candidate) for metal-three-blade.

User 2026-09-07 17:18 pasted "geeone-02 · rev-006 · 叶根凹坑 + 阶梯过渡 + 刀纹 —— agent 执行说明" and asked for it to be run
on the external rev-005 Blender script (~/Downloads/spinner_rev005.py, 2026-09-05 23:05). The referenced
spinner_rev006_rootpocket.py did not exist anywhere on disk, so it was written from the A/B/C tables and both were
run headless (Blender 5.2, Workbench checks + fixed camera pack).

Gate 01/02 are still ready_for_review and Gates 03/04 have no rev-005 contract: this blockout is registered as
`draft`, upstream-pending, with the spec's conflicts against Gate 02 listed as validations. No approvals.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A05 = base.EV / "05-blockout/rev-005"
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT_HEAD = "# geeone-02 · rev-006 · 叶根凹坑 + 阶梯过渡 + 刀纹 —— agent 执行说明（用户 2026-09-07 17:18 粘贴，全文存 rev006-agent-instructions-user-2026-09-07-1718.md）"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s05 = base.stage(manifest, "05-blockout")
    if s05["revision"] != 5:
        s05.setdefault("historicalRevisions", []).append({"revision": s05["revision"], "artifactIds": list(s05["artifactIds"]), "status": s05["status"], "reason": s05.get("staleReason", "superseded by rev-005 (user-directed external-script blockout)")})
        s05["revision"] = 5
        s05["artifactIds"] = []
        s05.pop("staleReason", None)
    s05["status"] = "draft"
    s05["decision"] = None

    spec = A05 / "rev006-agent-instructions-user-2026-09-07-1718.md"
    assert spec.exists(), "save the user's pasted instructions first"
    assets = [
        ("tri-r5b-user-rev006-instructions", spec, "white-model-source", "user-input", "user-agent-instructions-rev006-rootpocket-steps-lay", "user-provided", "user", ["tri-r6-frame-0132"], "用户粘贴的执行说明（A 凹坑 / B 阶梯 / C 刀纹 / D 验收 / E 调参 / F 禁止 / G 置信度）"),
        ("tri-r5b-external-rev005-prompt", A05 / "rev005-agent-prompt-external.md", "white-model-source", "user-input", "external-agent-prompt-rev005-2026-09-05", "user-provided", "user", [], "~/Downloads/rev005_agent_prompt.md（外部 agent，65 mm，圆角三角整体机身）"),
        ("tri-r5b-external-rev005-preview", A05 / "rev005-script-preview-external.png", "white-model-source", "user-input", "external-agent-preview-rev005", "user-provided", "user", [], "~/Downloads/rev005_script_preview.png"),
        ("tri-r5b-rev005-script", A05 / "spinner_rev005.py", "white-model-source", "external-reference", "external-bpy-builder-rev005", "user-provided", "user", ["tri-r5b-external-rev005-prompt"], "~/Downloads/spinner_rev005.py 原样复制；机身 = 圆角等边三角整体（R 32.5、角 R9、边凹 1.5）、盖孔 R18.22、轴承孔 R6.4、旧凹槽（尖朝圆心）、盖 24 楔 0.797 平盘"),
        ("tri-r5b-rev006-script", A05 / "spinner_rev006_rootpocket.py", "white-model-source", "process", "bpy-script-rev006-rootpocket-steps-lay", "repository-generated", "repository", ["tri-r5b-user-rev006-instructions", "tri-r5b-rev005-script"], "按说明书 A/B/C 实现；说明书引用的脚本磁盘上不存在。偏差：Boolean 用 MANIFOLD（EXACT 在 Bevel A 之后留下刀体顶面 + 29 非流形边）；移除 rev-005 反向凹槽与旧角度倒角"),
        ("tri-r5b-headless-driver", A05 / "run_rev005_rev006_headless.py", "white-model-source", "process", "blender-headless-driver-and-workbench-checks", "repository-generated", "repository", ["tri-r5b-rev005-script", "tri-r5b-rev006-script"], "blender -b --factory-startup：rev005 → 存 → rev006 → 存 → Workbench 六视图"),
        ("tri-r5b-blend-rev005", A05 / "geeone-blockout-r005.blend", "white-model-source", "source-model", "blend-after-rev005-script", "repository-generated", "repository", ["tri-r5b-rev005-script"], "SP_Body / SP_Cap，rev-005 原样"),
        ("tri-r5b-blend-rev006", A05 / "geeone-blockout-r005-rev006-rootpocket.blend", "white-model-source", "source-model", "blend-after-rev006-rootpocket", "repository-generated", "repository", ["tri-r5b-blend-rev005", "tri-r5b-rev006-script"], "修改器：Bool_bore → Bool_bearing → R6_StepA_45chamfer → R6_Pocket_0/1/2 (MANIFOLD, TRANSFER) → R6_StepB_break；材质 SP_Steel_ArmLay / SP_Steel_PocketLay"),
    ]
    for name in ("top-ortho", "oblique-f0132-like", "pocket-closeup", "edge-steps-low", "side-ortho", "bottom-ortho"):
        assets.append((f"tri-r5b-check-{name}", A05 / "checks" / f"{name}.png", "white-model-preview", "analysis", f"workbench-check-{name}", "repository-generated", "repository", ["tri-r5b-blend-rev006"], "Workbench STUDIO 单色，说明书 D 验收视图"))
    for name in ("top", "hero", "left-oblique", "right-oblique", "low", "front", "back", "left", "right", "bottom"):
        assets.append((f"tri-r5b-view-{name}", A05 / "fixed-views" / f"{name}.png", "white-model-preview", "analysis", f"fixed-camera-pack-{name}", "repository-generated", "repository", ["tri-r5b-blend-rev006"], "capture_standard_views.py（EEVEE，场景材质）"))
    assets.append(("tri-r5b-fixed-views-report", A05 / "fixed-views" / "capture-wrapper-report.json", "white-model-preview", "process", "fixed-camera-pack-report", "repository-generated", "repository", ["tri-r5b-blend-rev006"], ""))
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in assets:
        base.upsert(manifest, base.asset(aid, "05-blockout", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)

    s05["validations"] = [
        {"id": "upstream-gates-pending", "status": "warn", "detail": "Gate 01 rev-003 / Gate 02 rev-006 仍 ready_for_review，Gate 03/04 无 rev-005 合同；本白模为用户 17:18 明确指令下的候选，不构成任何 Gate 批准"},
        {"id": "d1-pocket-plan-shape", "status": "pass", "detail": "顶视三坑为圆顶等腰三角、尖朝叶尖、底开口进盖孔；坑口顶角 52°（PK_HALF_ANGLE 26）；checks/top-ortho.png"},
        {"id": "d2-apex-to-tip", "status": "pass", "detail": "坑尖最远点 27.50，叶尖 32.50 → 5.00 mm（要求 4.5–5.5）"},
        {"id": "d3-planar-walls", "status": "pass", "detail": "刀体两层轮廓桥接，壁为平面、顶弧为锥面，无 Subdivision/Smooth；Workbench 斜视均匀单色；checks/oblique-f0132-like.png、pocket-closeup.png"},
        {"id": "d4-see-through-to-bore", "status": "fail", "detail": "坑底 z 8.80 高于 rev-005 盖座 7.50（BODY_H 12.0 − 3.2），且 SP_Cap 填在盖孔内：透过坑看到的是盖侧壁而非黑腔。说明书写的“坑底 z = 9.8 低于盖体下沿”与 rev-005 数值不自洽（其隐含 Z_TOP 13.0）。需用户裁决：加深 PK_DEPTH ≥ 4.6 / 抬高盖座 / 接受"},
        {"id": "d5-two-step-edge", "status": "pass", "detail": "外轮廓两条折线：顶面/45° 带（1.20×1，weight 84 条边）、45° 带/竖壁；B 0.20×2 @35°；checks/edge-steps-low.png、side-ortho.png"},
        {"id": "d6-console-values", "status": "pass", "detail": "[rev006] 四行：tip-most 27.50 / clearance 5.00 / floor 8.80 / inset 1.70 / floor apex R 0.80 / open u 14.42 / A 1.20×1 / B 0.20×2@35 / lay radial 0.20"},
        {"id": "boolean-solver-deviation", "status": "warn", "detail": "说明书要求 Exact；Blender 5.2 EXACT 在 Bevel A 之后失败（刀体顶面残留、29 非流形边，见 spinner_rev006_rootpocket.py 注释），改 MANIFOLD 后 selfcheck 0 非流形、足迹 z 8.80..12.00"},
        {"id": "rev005-legacy-removed", "status": "warn", "detail": "说明书未提及：rev-005 的三个反向凹槽 Bool_SP_cut_pocket_* 与旧角度 Bevel 已移除，否则与 rev-006 坑重叠、倒角重复"},
        {"id": "conflict-scale-65-vs-85", "status": "warn", "detail": "脚本 D_TOTAL 65 mm；管线 85 mm 为 user-authorized-provisional（总控 09-05 23:14）。本白模按脚本 65 mm 执行，比例可换算"},
        {"id": "conflict-body-concept", "status": "warn", "detail": "rev-005 机身 = 圆角等边三角整体、盖沉在中心孔、缺口处有 1.03 mm 连续薄壁；Gate 02 claim tri-r6f-blade-planform-gap（用户 07:53“有些间隔，不需要连接在一起”，露盖 ≈16°/缺口）与之冲突"},
        {"id": "conflict-edge-transition", "status": "warn", "detail": "说明书 B = 45°×1.2 平切带 + 竖壁两级；Gate 02 D05 v17 = 宽多梯度过渡 0.14 R（A 层 22° + 鸢形/Λ 龙鳞，用户 10:40/10:55/11:10/11:47/14:01）。本白模按说明书执行，龙鳞未建"},
        {"id": "conflict-pocket-form", "status": "warn", "detail": "说明书 A = 平面直壁 62° + 锥顶弧 R2.5 + 打穿到盖孔；Gate 02 D08 v17 = 47° 漏斗 + 深平底台阶 + 真圆角。拓扑相近（尖朝叶尖、开口朝盖），角度/深度/圆角不同"},
        {"id": "materials-not-rendered", "status": "warn", "detail": "C 刀纹材质已建（Wave→Bump，radial/tangential 可切），按说明书 D 只出 Workbench，未开 Cycles"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 17:18 blockout r005:")[0]
        + " | 09-07 17:18 blockout r005: 用户粘贴 rev-006 执行说明 → 在外部 rev-005 脚本（65 mm 圆角三角机身）上实现 A 凹坑 / B 两级阶梯 / C 刀纹，Blender 5.2 headless，Workbench 六视图 + 固定相机包；D4（透过坑见黑腔）不成立（坑底 8.80 > 盖座 7.50）；EXACT→MANIFOLD；与 Gate 02 的 65/85、机身整体、龙鳞过渡、坑形四项冲突已列为 warn。Gate 05 rev-005 draft；Gate 01/02 仍 ready_for_review；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-revised", "stageId": "05-blockout",
            "notes": "05-blockout rev-005 draft (user-directed): external spinner_rev005.py (65 mm rounded-triangle body) + spinner_rev006_rootpocket.py written from the user's 17:18 A/B/C tables; Blender 5.2 headless; Workbench D-checklist: D1 D2 D3 D5 D6 pass, D4 fail (floor 8.80 above cap seat 7.50), EXACT boolean replaced by MANIFOLD; conflicts with Gate 02 (65 vs 85 mm, one-piece body vs blade gaps, 45° step vs dragon-scale multi-gradient, pocket form) recorded as warnings. No approval. " + USER_TEXT_HEAD,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "stage05": s05["revision"], "assets": len(added)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
