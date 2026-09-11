"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
10:40 feedback on the shaded relief: (1) the blade edge must go from the top
face to the vertical wall through several rows of dragon-scale facets, like the
cap edge; (2) the striped "groove" on the band was a distance-field artefact.
Registers CAD v11 (D05 multi-row, Detail H), shaded relief v11 (explicit planar
scale rows, KD-tree distances), the user's screenshot + exact wording, one claim.
No approvals, no gate crossing, no workbench refresh.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()
ASSETS_IN = Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets")
USER_TEXT = "这个地方的过渡不对，首先页面从平面过渡到垂直面需要有多层龙鳞纹过渡，然后从你的截图里面有个不明的凹痕"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review"

    shot = A02 / "user-screenshot-2026-09-07-1040-blade-edge-rows.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-60fdee86-767f-4d08-a295-46b640505184.png", shot)
    instr = A02 / "user-instructions-2026-09-07-1040.md"
    instr.write_text(
        "# 用户指令 2026-09-07 10:40（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：shaded-relief-v10.png ⑥ 右下叶放大的局部（叶边鳞面带处）。\n\n"
        "解读（Gate 02 rev-006 v11）：\n"
        "- “叶面从平面过渡到垂直面需要有多层龙鳞纹过渡”：叶边 D05 由单排倒角带改为**多排龙鳞刻面**（排数 3 占位，≥2 排可见），逐排变陡到竖壁，错半鳞、相邻一亮一暗，与盖缘三层同一构造；D06 竖壁按此降到 ≈0.30×厚（占位）。"
        "09:36 时曾把三层写到叶边后撤回，本条按用户明确指令重新登记。\n"
        "- “不明的凹痕”：v10 阴影图叶边带上的条纹来自栅格距离场（EDT）对数字化边界的 ≈0.0002 R 周期误差，被 3× 夸张 + 低角度侧光放大成条纹，不是几何。v11 改用 2400 点样条边界 + KD-tree 精确距离/弧长，并把鳞面做成显式平面刻面，条纹消失。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-blade-edge-rows", shot, "analysis-board", "user-input", "user-screenshot-shaded-relief-v10-blade-edge", "user-provided", "user", ["tri-r6-shaded-relief-v10"], "用户 09-07 10:40：多层龙鳞过渡 + 不明凹痕"),
        ("tri-r6-user-instructions-1040", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-1040", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-cad-v11-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v11.py", "analysis-board", "process", "reference-cad-v11-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1040"], ""),
        ("tri-r6-reference-cad-v11", A02 / "reference-cad-from-video-v11.png", "structural-cad", "analysis", "reference-cad-v11-blade-edge-multi-row-scales", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1040", "tri-r6-user-screenshot-blade-edge-rows"], "v11 is the current reference CAD; v1-v10 history"),
        ("tri-r6-reference-cad-v11-pdf", A02 / "reference-cad-from-video-v11.pdf", "structural-cad", "analysis", "reference-cad-v11-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1040"], "v11 vector"),
        ("tri-r6-shaded-relief-v11", A02 / "shaded-relief-v11.png", "analysis-board", "analysis", "shaded-relief-height-field-illustration", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v11", "tri-r6-user-instructions-1040"], "2.5D hillshade + relative-height map; blade band = explicit planar scale rows; KD-tree distances (no EDT ripple); not a blockout, not a render; heights provisional"),
        ("tri-r6-shaded-relief-v11-script", REPO / "tools/model-provenance-explorer/shade_geeone_reference_v11.py", "analysis-board", "analysis", "shaded-relief-script", "repository-generated", "repository", ["tri-r6-cad-v11-script"], ""),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839", "tri-r6-user-instructions-0936", "tri-r6-user-instructions-1040"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 Y ridge, D02/D03 cap-edge three tiers, D05 multi-row blade-edge scales"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v10", "tri-r6-reference-cad-v10-pdf", "tri-r6-cad-v10-script"):
            a["provenance"]["note"] = "v10 — superseded by tri-r6-reference-cad-v11 (blade edge multi-row scales); kept as history"
        if a["id"] in ("tri-r6-shaded-relief-v10", "tri-r6-shaded-relief-v10-script"):
            a["provenance"]["note"] = "v10 — superseded by tri-r6-shaded-relief-v11 (explicit scale rows; the striped band was an EDT artefact); kept as history"

    claims = {c["id"]: c for c in manifest["claims"]}
    new_claim = {
        "id": "tri-r6f-blade-edge-scale-rows", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (multi-row structure: user statement + f0128-f0140) / low (row count 3, per-row widths/slopes)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片边缘从顶面到竖壁不是一条单排倒角带，而是多排平面龙鳞刻面逐排变陡的过渡（与盖缘 D02/D03 三层同一构造）：排数 3 为占位（f0128–f0140 5× 至少可见 2 排），每排每边 6±1 鳞，排间错半鳞、相邻一亮一暗；三排总宽 ≈0.07 R，占位 0.030/0.022/0.018 R、15°/38°/62°；其下竖壁 D06 ≈0.30×厚（占位，原 0.45）。依据：用户 2026-09-07 10:40 原话“叶面从平面过渡到垂直面需要有多层龙鳞纹过渡”。同条指令指出的“不明凹痕”经查为 v10 阴影图的距离场栅格条纹，不是几何，v11 已消除。细化 tri-r6-surface-detail-spec 中 D05“每边 5–7 平面”的单带表述。",
        "sourceAssetIds": ["tri-r6-user-screenshot-blade-edge-rows", "tri-r6-user-instructions-1040", "tri-r6-frame-0132", "tri-r6-frame-0128", "tri-r6-frame-0136", "tri-r6-frame-0140", "tri-r6-reference-cad-v11", "tri-r6-shaded-relief-v11"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    if new_claim["id"] not in {c["id"] for c in doc["claims"]}:
        doc["claims"].append(new_claim)
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] not in ("blade-edge-scale-rows",)] + [
        {"id": "blade-edge-scale-rows", "status": "pass", "detail": "D05 = 多排龙鳞刻面（3 排占位，≥2 排可见）逐排变陡到竖壁，与盖缘同构造；用户 10:40 原话；CAD v11 Detail H + C-C/F-F；阴影图 v11 显式刻面，v10 条纹为 EDT 伪影已消除"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 10:40 v11:")[0]
        + " | 09-07 10:40 v11: 用户指出叶边需多层龙鳞过渡、阴影图有不明凹痕 → D05 改多排鳞（3 排占位）逐排变陡到竖壁，D06 0.30×厚占位；凹痕为 v10 距离场栅格条纹（非几何），v11 用样条边界 + KD-tree 精确距离与显式平面鳞排消除。CAD v11 + 阴影图 v11。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v11 — blade edge D05 = multi-row dragon-scale transition (3 rows provisional, 15/38/62°, wall 0.30t), Detail H; shaded relief v11 with explicit planar scale rows and KD-tree distances (the v10 striped 'groove' was an EDT artefact); claim tri-r6f-blade-edge-scale-rows. User 2026-09-07 10:40 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
