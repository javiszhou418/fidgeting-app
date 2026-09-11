"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
08:39 red-Y drawing: each blade top is a Y-shaped raised ridge (stem to the tip,
two bulging arms flanking the root pocket), not a flat plateau. Registers CAD
v9, the blade-top evidence panel, three extra Gate 01 key frames (108/132/156),
the user's drawing + exact wording, a new claim and one supersession.
No approvals, no gate crossing, no workbench refresh.
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
USER_TEXT = "就是有一个这样的凸起的弧度，然后中间红色的部分就是它的隆起。"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s01 = base.stage(manifest, "01-intake")
    s02 = base.stage(manifest, "02-analysis")
    assert s01["revision"] == 3 and s02["revision"] == 6 and s02["status"] == "ready_for_review"
    v6reg.NEW_FRAMES = [108, 132, 156]
    v6reg.add_key_frames(manifest, s01)

    shot = A02 / "user-screenshot-2026-09-07-0839-blade-top-y.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-fdb83bba-0fd8-408c-8933-f8b2d5668be8.png", shot)
    instr = A02 / "user-instructions-2026-09-07-0839.md"
    instr.write_text(
        "# 用户指令 2026-09-07 08:39（原话，针对 CAD v8 顶视图上手绘的红色 Y）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：CAD v8 顶视局部，右叶片上红色 Y：柄沿叶轴指向叶尖，两臂绕过叶根凹坑两侧到盖圈。\n\n"
        "解读（Gate 02 rev-006 v9）：叶片顶面不是平台，而是沿 Y 形脊线隆起的顶面——主脊沿叶轴从叶尖到 x≈0.72 R（凹坑尖端外），"
        "两臂沿凹坑两侧外凸弧线（“叉臂”）到盖圈极角 ±38°；顶面从脊线向外落到鳞面带、向内落到凹坑边。f0108/f0132 主脊与两臂的亮带、f0156 斜视的大斜面软脊与此一致。"
        "脊高未测（CAD 以 0.025 R 占位）。取代“D04 平台为平面”。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-blade-top-y", shot, "analysis-board", "user-input", "user-drawing-red-y-on-cad-v8", "user-provided", "user", ["tri-r6-reference-cad-v8"], "用户 09-07 08:39：红色 Y = 叶顶隆起"),
        ("tri-r6-user-instructions-0839", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-0839", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-cad-v9-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v9.py", "analysis-board", "process", "reference-cad-v9-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0839"], ""),
        ("tri-r6-reference-cad-v9", A02 / "reference-cad-from-video-v9.png", "structural-cad", "analysis", "reference-cad-v9-y-ridge-blade-top", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0839", "tri-r6-user-screenshot-blade-top-y"], "v9 is the current reference CAD; v1-v8 history"),
        ("tri-r6-reference-cad-v9-pdf", A02 / "reference-cad-from-video-v9.pdf", "structural-cad", "analysis", "reference-cad-v9-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0839"], "v9 vector"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 Y ridge"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    existing = {a["id"]: a for a in manifest["assets"]}
    for p in sorted((A02 / "frame-zooms").glob("*.png")):
        if p.name.startswith("_"):
            continue
        aid = "tri-r6-zoom-" + p.stem
        if aid not in existing or existing[aid]["sha256"] != base.sha256(p):
            base.upsert(manifest, base.asset(aid, "02-analysis", "analysis-board", p, "analysis", "frame-zoom-crop-or-trace", "repository-generated", "repository", ["tri-r6-video-source", "tri-r6-frame-measurements"]))
            added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v8", "tri-r6-reference-cad-v8-pdf", "tri-r6-cad-v8-script"):
            a["provenance"]["note"] = "v8 — superseded by tri-r6-reference-cad-v9 (Y-shaped raised ridge on the blade tops); kept as history"

    claims = {c["id"]: c for c in manifest["claims"]}
    new_claim = {
        "id": "tri-r6f-blade-top-y-ridge", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (Y layout) / unknown (rise)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片顶面不是平面平台，而是沿 Y 形脊线隆起：主脊沿叶轴从叶尖圆角到 x≈0.72 R（凹坑尖端 0.70 R 之外），两臂从该点沿凹坑两侧以外凸弧线（“叉臂”）延伸到盖圈极角 ±38°；顶面自脊线向外落到 D05 鳞面带、向内（叉内）落到 D08 凹坑边，读作几个大斜面交出的软脊。依据：用户 2026-09-07 08:39 在 CAD v8 上手绘红色 Y 并说明“有一个这样的凸起的弧度，中间红色的部分就是它的隆起”；f0108/f0132 上叶主脊与两臂的亮带环抱凹坑，f0156 斜视顶面为大斜面软脊。脊高未测（CAD 以 0.025 R 占位），脊线圆润度未知。取代 tri-r6-blade-top-structure 中“中央平台为平面”。",
        "sourceAssetIds": ["tri-r6-frame-0108", "tri-r6-frame-0132", "tri-r6-frame-0156", "tri-r6-frame-0148", "tri-r6-user-screenshot-blade-top-y", "tri-r6-user-instructions-0839", "tri-r6-zoom-blade-top-y-ridge-f0108-f0132-f0156"],
    }
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    supersessions = {"tri-r6-blade-top-structure": "tri-r6f-blade-top-y-ridge"}
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

    s02["validations"] = [v for v in s02["validations"] if v["id"] != "blade-top-structure"] + [
        {"id": "blade-top-structure", "status": "pass", "detail": "D04 = Y 形隆起脊线（主脊到 x 0.72 R，两臂沿凹坑两侧到盖圈 ±38°），脊高未测（0.025 R 占位）；“平台为平面”作废；CAD v9 剖面 C-C/F-F 示意"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 08:39 v9:")[0]
        + " | 09-07 08:39 v9: 用户手绘红色 Y 指出叶顶为 Y 形隆起（柄到叶尖、两臂绕凹坑到盖）；D04 由“平台为平面”改为 Y 形隆起脊线，脊高未测（0.025 R 占位）。CAD v9。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v9 — blade top = Y-shaped raised ridge (stem to the tip, arms flanking the pocket to the cap at ±38°); claim tri-r6f-blade-top-y-ridge supersedes tri-r6-blade-top-structure; Gate 01 rev-003 +3 key frames (108/132/156). User 2026-09-07 08:39 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
