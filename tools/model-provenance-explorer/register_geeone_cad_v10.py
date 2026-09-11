"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
09:36 feedback: (1) SECTION C-C v9 was unreadable -> v10 keys every section to
cut lines A/C/F on the plan and adds a reading guide; (2) the user's blue/red/
green outlines (template-matched to f0132 at (336,524)+181x168, NCC 0.92) sit
on the CAP edge: crown + two skirt rows form a three-tier transition from the
disc plane to the vertical side, each tier steeper. Registers CAD v10, the two
evidence boards, Gate 01 key frames 128/136/140, the user's screenshots + exact
wording, one claim and one supersession. No approvals, no gate crossing, no
workbench refresh.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_cad_v6 as v6reg
import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()
ASSETS_IN = Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets")
USER_TEXT = "这个我看不懂，然后第二张图里面，红蓝绿色好像是通过三层过度完成了从平面到垂直面的变化"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s01 = base.stage(manifest, "01-intake")
    s02 = base.stage(manifest, "02-analysis")
    assert s01["revision"] == 3 and s02["revision"] == 6 and s02["status"] == "ready_for_review"
    v6reg.NEW_FRAMES = [128, 136, 140]
    v6reg.add_key_frames(manifest, s01)

    shot_cc = A02 / "user-screenshot-2026-09-07-0936-section-cc-unclear.png"
    if not shot_cc.exists():
        shutil.copy2(ASSETS_IN / "image-e6380b64-fc07-4957-bcee-21a288716131.png", shot_cc)
    shot_tiers = A02 / "user-screenshot-2026-09-07-0936-cap-edge-three-tiers.png"
    if not shot_tiers.exists():
        shutil.copy2(ASSETS_IN / "image-59743c56-fe3a-4320-bce4-2f0a064d5207.png", shot_tiers)
    instr = A02 / "user-instructions-2026-09-07-0936.md"
    instr.write_text(
        "# 用户指令 2026-09-07 09:36（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图 1：CAD v9 SECTION C—C 截图（“这个我看不懂”）。\n"
        "附图 2：源视频局部放大，用户用蓝/红/绿三色圈出三块相邻的四边形面。\n\n"
        "定位：附图 2 以归一化互相关模板匹配到 f0132（t=13.2 s）(336,524)+181×168，NCC 0.92；该区域是**盖**的边缘（盘缘 → 冠环 → 裙 → 竖壁），不是叶片边缘。\n\n"
        "解读（Gate 02 rev-006 v10）：\n"
        "- C—C 难读的原因是顶视图上没有剖切线、切面里的上下两坑让截面像“哑铃”、各面无标注。v10 在顶视右下叶标出 A—A / C—C / F—F 剖切线，切面逐面标注，并附 section-cc-reading-guide.png。\n"
        "- 绿 = 冠环楔（贴盘缘，最缓），红 = 盖裙上排鳞，蓝 = 盖裙下排鳞（最陡，近竖直）：盖从盘面到竖壁由三层逐层变陡的刻面完成过渡，之后是一小段竖直 14 边形侧壁到暗缝。"
        "取代 tri-r6e-cap-crown-14 中“冠环外顶点在盖圆、裙为竖直两排”的表述；14 等分不变。各层径向宽与斜度（0.10/0.06/0.02×盖径，20°/45°/75°）为占位。\n"
        "- 叶片边缘（D05）不改：三层假设曾短暂写入 D05 后撤回，因为用户圈出的面不在叶边。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-section-cc-unclear", shot_cc, "analysis-board", "user-input", "user-screenshot-cad-v9-section-cc", "user-provided", "user", ["tri-r6-reference-cad-v9"], "用户 09-07 09:36：看不懂"),
        ("tri-r6-user-screenshot-cap-edge-tiers", shot_tiers, "analysis-board", "user-input", "user-outline-blue-red-green-on-f0132", "user-provided", "user", ["tri-r6-frame-0132"], "用户 09-07 09:36：三层过渡"),
        ("tri-r6-user-instructions-0936", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-0936", "user-provided", "user", [], "原话 + 定位 + 解读"),
        ("tri-r6-cad-v10-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v10.py", "analysis-board", "process", "reference-cad-v10-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0936"], ""),
        ("tri-r6-reference-cad-v10", A02 / "reference-cad-from-video-v10.png", "structural-cad", "analysis", "reference-cad-v10-cap-edge-three-tiers-cut-lines", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0936", "tri-r6-user-screenshot-cap-edge-tiers"], "v10 is the current reference CAD; v1-v9 history"),
        ("tri-r6-reference-cad-v10-pdf", A02 / "reference-cad-from-video-v10.pdf", "structural-cad", "analysis", "reference-cad-v10-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0936"], "v10 vector"),
        ("tri-r6-cap-edge-three-tier-evidence", A02 / "cap-edge-three-tier-evidence.png", "analysis-board", "analysis", "user-outline-located-on-f0132-plus-cad-v10-details", "repository-generated", "repository", ["tri-r6-frame-0132", "tri-r6-user-screenshot-cap-edge-tiers", "tri-r6-reference-cad-v10"], "template match NCC 0.92"),
        ("tri-r6-section-cc-reading-guide", A02 / "section-cc-reading-guide.png", "analysis-board", "analysis", "how-to-read-section-cc", "repository-generated", "repository", ["tri-r6-reference-cad-v10", "tri-r6-frame-0132"], "answers 09:36 “这个我看不懂”"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839", "tri-r6-user-instructions-0936"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 Y ridge, D02/D03 cap-edge three tiers"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v9", "tri-r6-reference-cad-v9-pdf", "tri-r6-cad-v9-script"):
            a["provenance"]["note"] = "v9 — superseded by tri-r6-reference-cad-v10 (cap edge three tiers; cut lines A/C/F; legible sections); kept as history"

    claims = {c["id"]: c for c in manifest["claims"]}
    new_claim = {
        "id": "tri-r6f-cap-edge-three-tiers", "stageId": "02-analysis", "category": "geometry", "confidence": "medium-high (three tiers, ordering) / low (per-tier widths and slopes)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "盖缘从盘面到竖壁由三层逐层变陡的平面刻面完成过渡：第 1 层 = 冠环 14 楔（28 三角，贴 14 边形盘缘，最缓，向外向下，占位 20°，径向 0.10×盖径到 ≈0.92×盖）；第 2 层 = 盖裙上排 14 鳞（占位 45°，径向 0.06×盖径）；第 3 层 = 盖裙下排 14 鳞（占位 75°，近竖直，径向 0.02×盖径到盖圆）；其下为一小段竖直 14 边形侧壁（≈0.05 R，侧高 0.14 R 低置信）接暗缝。三者共用一套 14 等分。依据：用户 2026-09-07 09:36 在 f0132 局部圈出蓝/红/绿三块相邻四边形面并说“通过三层过渡完成了从平面到垂直面的变化”（模板匹配 (336,524)+181×168，NCC 0.92，位于盖缘而非叶边）；f0128–f0140 8× 放大盘缘外依次为亮排、纹理中排、暗陡排。取代 tri-r6e-cap-crown-14 中“冠环外顶点在盖圆、裙为竖直两排”的表述，14 等分与盘 0.82×盖不变。叶边 D05 不受此影响。",
        "sourceAssetIds": ["tri-r6-frame-0132", "tri-r6-frame-0128", "tri-r6-frame-0136", "tri-r6-frame-0140", "tri-r6-user-screenshot-cap-edge-tiers", "tri-r6-user-instructions-0936", "tri-r6-cap-edge-three-tier-evidence"],
    }
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    supersessions = {"tri-r6e-cap-crown-14": "tri-r6f-cap-edge-three-tiers"}
    for old, new in supersessions.items():
        c = claims[old]
        if c.get("state") != "superseded":
            c["state"] = "superseded"
            c["supersededBy"] = new
            c["supersededAt"] = NOW

    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    doc["supersessions"].update(supersessions)
    if new_claim["id"] not in {c["id"] for c in doc["claims"]}:
        doc["claims"].append(new_claim)
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] not in ("cap-facet-count", "cap-edge-tiers", "sections-keyed-to-plan")] + [
        {"id": "cap-facet-count", "status": "pass", "detail": "盘 14 扇区 / 冠环 14 楔 / 裙两排各 14，共用 14 等分；FFT 谐波 12–15；用户 08:25 原话“14 片，均分”"},
        {"id": "cap-edge-tiers", "status": "pass", "detail": "盖缘三层逐层变陡（冠 → 裙上 → 裙下）后接竖壁；用户 09:36 圈图定位 f0132 (336,524) NCC 0.92；各层宽/斜度占位 20°/45°/75°"},
        {"id": "sections-keyed-to-plan", "status": "pass", "detail": "CAD v10 顶视标出 A—A / C—C / F—F 剖切线；C—C 各面标注；section-cc-reading-guide.png"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 09:36 v10:")[0]
        + " | 09-07 09:36 v10: 用户看不懂 C—C → 顶视加剖切线、切面逐面标注 + 读图指南；用户蓝/红/绿三层圈图定位到 f0132 盖缘 → 盖缘 = 冠环 + 裙两排三层逐层变陡到竖壁（D02/D03，宽/斜度占位）；叶边 D05 不变。CAD v10。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v10 — plan cut lines A/C/F, legible C-C + reading guide; cap edge = three tiers plane->vertical (crown 20° / skirt 45° / skirt 75°, provisional) located on f0132 by template match; claim tri-r6f-cap-edge-three-tiers supersedes tri-r6e-cap-crown-14; blade-edge D05 unchanged (three-row hypothesis withdrawn); Gate 01 rev-003 +3 key frames (128/136/140). User 2026-09-07 09:36 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
