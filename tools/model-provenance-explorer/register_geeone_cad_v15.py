"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
13:27 facet drawing on f0132 ("这个细节图能帮助你理解吗"): the blade top is the
lower envelope of a few large hard-cut planes (per half T tip / F pocket-flank /
C root-corner) meeting at straight creases; the pocket rim is F's upper edge; the
stem crease falls toward the tip. Registers CAD v15, shaded relief v16, the
reading board (user strokes located on f0132 vs relief), the user's drawing +
exact wording, one superseding claim. No approvals, no gate crossing, no
workbench refresh.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_video_intake_rev6 as base
from register_geeone_cad_v14 import supersede

REPO = base.REPO
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()
ASSETS_IN = Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets")
USER_TEXT = "这个细节图能帮助你理解吗"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review"

    shot = A02 / "user-drawing-2026-09-07-1327-blade-top-facets-f0132.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-7184bb25-d5ce-4f0f-b3a7-2c41b64112e3.png", shot)
    instr = A02 / "user-instructions-2026-09-07-1327.md"
    instr.write_text(
        "# 用户指令 2026-09-07 13:27（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：在 `frame-zooms/blade-top-y-ridge-f0108-f0132-f0156.png` 面板 ③（f0132 上叶根部）上手绘绿 / 蓝 / 红线。"
        "归一化互相关定位：f0132 (287,396) 起 223×270 px，缩放 2.4×，NCC 0.92（`blade-top-facets-user-1327-vs-v16.png` 左图）。\n\n"
        "解读（Gate 02 rev-006 v16）：\n"
        "- 绿 = 坑尖以上的主脊折边 + 凹坑右缘：**坑缘就是坑侧面 F 的上边（最高线）**，臂不是独立隆起。\n"
        "- 蓝框 = 叶尖面 T：从主脊到边缘鳞带的一块大平面，下边止于坑尖到 K 的折边。\n"
        "- 红 = 平面之间的直折边：坑角 → K → 上接 T 面角；K → 根部边缘。三面 T / F / C 交于 K。\n"
        "- 右蓝 = 根角面 C / 边缘鳞带。\n"
        "- 因此 D04 由“平顶隆起 + 直斜裙”(v15) 改为**几块大平面硬切的凸包络**（表面 = 各平面最低值），折边为直线、无谷；主脊自坑尖向叶尖下落。"
        "K 位置、各面落差、C 范围均为占位。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-drawing-blade-top-facets", shot, "analysis-board", "user-input", "user-drawing-on-f0132-blade-top-facets", "user-provided", "user", ["tri-r6-frame-0132", "tri-r6-zoom-blade-top-y-ridge-f0108-f0132-f0156"], "用户 09-07 13:27：绿/蓝/红描出叶顶刻面与折边"),
        ("tri-r6-user-instructions-1327", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-1327", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-blade-top-facets-evidence", A02 / "blade-top-facets-user-1327-vs-v16.png", "analysis-board", "analysis", "evidence-user-strokes-located-on-f0132-vs-relief-v16", "repository-generated", "repository", ["tri-r6-frame-0132", "tri-r6-user-drawing-blade-top-facets", "tri-r6-user-instructions-1327"], "用户描线定位到 f0132（NCC 0.92）+ T/F/C 读法 vs 阴影图 v16"),
        ("tri-r6-cad-v15-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v15.py", "analysis-board", "process", "reference-cad-v15-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1327"], ""),
        ("tri-r6-reference-cad-v15", A02 / "reference-cad-from-video-v15.png", "structural-cad", "analysis", "reference-cad-v15-hard-cut-top-facets", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1327", "tri-r6-user-drawing-blade-top-facets", "tri-r6-blade-top-facets-evidence"], "v15 is the current reference CAD; v1-v14 history"),
        ("tri-r6-reference-cad-v15-pdf", A02 / "reference-cad-from-video-v15.pdf", "structural-cad", "analysis", "reference-cad-v15-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1327"], "v15 vector"),
        ("tri-r6-shaded-relief-v16", A02 / "shaded-relief-v16.png", "analysis-board", "analysis", "shaded-relief-height-field-illustration", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v15", "tri-r6-user-instructions-1327"], "2.5D hillshade + relative-height map; blade top = lower envelope of planes T/F/C (straight creases, convex); blade side = kite/Λ facets; not a blockout, not a render; heights provisional"),
        ("tri-r6-shaded-relief-v16-script", REPO / "tools/model-provenance-explorer/shade_geeone_reference_v16.py", "analysis-board", "analysis", "shaded-relief-script", "repository-generated", "repository", ["tri-r6-cad-v15-script"], ""),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839", "tri-r6-user-instructions-0936", "tri-r6-user-instructions-1040", "tri-r6-user-instructions-1055", "tri-r6-user-instructions-1110", "tri-r6-user-instructions-1147", "tri-r6-user-instructions-1327"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 v16 hard-cut top facets T/F/C, D02/D03 cap-edge three tiers, D05 v15 kite/Λ interlocking blade-side facets"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v14", "tri-r6-reference-cad-v14-pdf", "tri-r6-cad-v14-script"):
            a["provenance"]["note"] = "v14 — superseded by tri-r6-reference-cad-v15 (blade top = hard-cut planes T/F/C); kept as history"
        if a["id"] in ("tri-r6-shaded-relief-v15", "tri-r6-shaded-relief-v15-script"):
            a["provenance"]["note"] = "v15 — superseded by tri-r6-shaded-relief-v16 (user 13:27 facet drawing); kept as history"

    facets = {
        "id": "tri-r6f-blade-top-hard-cut-facets", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (facet layout: user drawing 13:27 located on f0132 NCC 0.92 + f0132 5× shading) / low (K position, drops, C extent)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片顶面是几块**大平面硬切**的凸包络（表面 = 各平面的最低值），不是平顶隆起 + 直斜裙（v15）、也不是三条脊线的帐篷（v9–v14）。用户 2026-09-07 13:27 在 f0132 上描线：绿 = 坑尖以上的主脊折边并沿凹坑右缘继续（**坑缘 = 坑侧面 F 的上边 = 最高线**）；蓝框 = 叶尖面 T，一块大平面从主脊到边缘鳞带；红 = 平面之间的直折边，自坑角到 K、再上接 T 面角，另一支自 K 到根部边缘；右蓝 = 根角面 C。每半叶三面：T（含主脊，向叶尖下落 ≈0.025 R 占位、向外落）、F（上边为水平坑缘，向外落）、C（自坑角与 K 落到根部边缘）；折边 T∩T' = 主脊、T∩F 坑尖→K、F∩C 坑角→K、T∩C K→边缘，均为直线；凸包络故无任何谷（用户 11:47）。K ≈ 坑角外 0.07 R×0.07 R、落差 0.015 R，均占位。取代 tri-r6f-blade-top-y-mesa。",
        "sourceAssetIds": ["tri-r6-user-drawing-blade-top-facets", "tri-r6-user-instructions-1327", "tri-r6-blade-top-facets-evidence", "tri-r6-frame-0132", "tri-r6-user-instructions-1147", "tri-r6-reference-cad-v15", "tri-r6-shaded-relief-v16"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    supersede(manifest, "tri-r6f-blade-top-y-mesa", facets)
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    if facets["id"] not in {c["id"] for c in doc["claims"]}:
        doc["claims"].append(facets)
    for c in doc["claims"]:
        if c["id"] == "tri-r6f-blade-top-y-mesa":
            c.update({"state": "superseded", "supersededBy": facets["id"], "supersededAt": NOW})
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] not in ("blade-top-structure",)] + [
        {"id": "blade-top-structure", "status": "pass", "detail": "D04 v16 = 大平面硬切凸包络（每半叶 T/F/C，折边直线，坑缘 = F 上边，主脊向叶尖下落）；用户 13:27 描线定位 f0132 NCC 0.92；CAD v15 折边由平面交线算出；阴影图 v16；claim tri-r6f-blade-top-hard-cut-facets 取代 y-mesa"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 13:27 v16:")[0]
        + " | 09-07 13:27 v16: 用户在 f0132 上描出叶顶刻面（绿主脊+坑缘、蓝叶尖面、红折边交于 K）→ D04 改为几块大平面硬切的凸包络（T/F/C，折边直线，坑缘 = F 上边，主脊向叶尖下落）；CAD v15 + 阴影图 v16 + 读法对照板。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v15 + shaded relief v16 — D04 blade top = lower envelope of hard-cut planes T (tip) / F (pocket flank, upper edge = pocket rim) / C (root corner) per half, straight creases meeting at K (provisional), stem falls toward the tip; from the user's 13:27 facet drawing located on f0132 (NCC 0.92); claim tri-r6f-blade-top-hard-cut-facets supersedes tri-r6f-blade-top-y-mesa. User 2026-09-07 13:27 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
