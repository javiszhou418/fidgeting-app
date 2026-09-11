"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
07:53 feedback on CAD v6 (red arrow at the notch): adjacent blades are separated
by a gap and must not connect. Root traces show each edge ends on the cap circle
at polar 51-53°, so the cap is exposed ≈16° per notch. Registers CAD v7, the
re-rendered traces/overlay, the user's screenshot + exact wording, a new claim
and two supersessions. No approvals, no gate crossing, no workbench refresh.
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
USER_TEXT = "这个部分是有些间隔的，不需要连接在一起"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review", (s02["revision"], s02["status"])

    shot = A02 / "user-screenshot-2026-09-07-0753-notch-gap.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-0f85d30c-c38e-4604-a187-dd3d260d36d3.png", shot)
    instr = A02 / "user-instructions-2026-09-07-0753.md"
    instr.write_text(
        "# 用户指令 2026-09-07 07:53（原话，针对 CAD v6 缺口处红箭头截图）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：CAD v6 顶视局部，红箭头指向相邻两叶凸弧在角平分线相交成 V 的位置。\n\n"
        "解读（Gate 02 rev-006 v7）：相邻叶片之间有间隔，不相接。逐叶描迹复核：4 条干净叶边都在 x≈0.31 R 处到达盖圈（极角 51–53°），"
        "随后剪影沿盖圈延伸到 ≥62°，即每个缺口露盖约 16°。v7 把叶边改为：大凸弧（R≈1.37 R）→ 根部内收圆弧（R≈0.15 R，起于极角 ≈44°）→ 止于盖圈极角 52°；"
        "v6 的“相邻弧相交成 V”作废。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-notch-gap", shot, "analysis-board", "user-input", "user-screenshot-cad-v6-notch-red-arrow", "user-provided", "user", ["tri-r6-reference-cad-v6"], "用户 09-07 07:53：“这个部分是有些间隔的，不需要连接在一起”"),
        ("tri-r6-user-instructions-0753", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-0753", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-cad-v7-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v7.py", "analysis-board", "process", "reference-cad-v7-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0753"], ""),
        ("tri-r6-reference-cad-v7", A02 / "reference-cad-from-video-v7.png", "structural-cad", "analysis", "reference-cad-v7-arc-sides-ending-on-cap-with-notch-gap", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0753", "tri-r6-user-screenshot-notch-gap"], "v7 is the current reference CAD; v1-v6 history"),
        ("tri-r6-reference-cad-v7-pdf", A02 / "reference-cad-from-video-v7.pdf", "structural-cad", "analysis", "reference-cad-v7-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0753"], "v7 vector"),
        # scripts that moved / changed
        ("tri-r6-overlay-v6-script", REPO / "tools/model-provenance-explorer/overlay_geeone_planform.py", "analysis-board", "process", "planform-overlay-on-frames-script", "repository-generated", "repository", ["tri-r6-frame-measurements"], "renamed from overlay_geeone_planform_v6.py; draws current (v7) + previous (v6) outlines"),
        ("tri-r6-trace-script", REPO / "tools/model-provenance-explorer/trace_geeone_blade_root.py", "analysis-board", "process", "per-blade-root-trace-script", "repository-generated", "repository", ["tri-r6-frame-measurements"], "rectified per-blade outline traces vs CAD planforms (v6 vs v7)"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform (arcs + root blend ending on the cap, 16° exposed cap per notch)"),
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
        if a["id"] in ("tri-r6-reference-cad-v6", "tri-r6-reference-cad-v6-pdf", "tri-r6-cad-v6-script"):
            a["provenance"]["note"] = "v6 — superseded by tri-r6-reference-cad-v7 (blades end on the cap circle, 16° exposed cap per notch, no V); kept as history"
        if a["id"] == "tri-r6-zoom-planform-v6-on-frames":
            a["provenance"]["note"] = "v6 overlay — history; see planform-v7-on-frames.png"

    claims = {c["id"]: c for c in manifest["claims"]}
    new_claim = {
        "id": "tri-r6f-blade-planform-gap", "stageId": "02-analysis", "category": "geometry", "confidence": "high", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片平面形（修正 tri-r6e）：每条叶边是凸圆弧（R≈1.37 R，圆心在叶轴垂线上距盖心 0.92 R），从 x≈0.40 R（极角 ≈44°）起以 R≈0.15 R 的内收圆弧接入盖圈、止于极角 ≈52°（4 条干净边实测 51–53°）；相邻两叶**不相接**——每个缺口在极角 52°→68° 之间露出盖冠环与裙，约 16°（14–18°）。叶边与盖圈切线夹 ≈60°（锐角）。叶尖两弧夹 ≈90° + 0.03 R 圆角；无直边、无肩角。依据：用户 2026-09-07 07:53 红箭头截图“这个部分是有些间隔的，不需要连接在一起”；blade-root-traces 根部表：4 边均在 x≈0.31 到达 r=1.00 盖并沿盖圈延伸到 ≥62°。取代 tri-r6e-blade-planform-arcs 与 tri-r6e-notch-exposure 中“相邻弧相交于盖圈外 0.005 R”的表述。",
        "sourceAssetIds": ["tri-r6-frame-0077", "tri-r6-frame-0078", "tri-r6-frame-0148", "tri-r6-frame-0134", "tri-r6-user-screenshot-notch-gap", "tri-r6-user-instructions-0753", "tri-r6-zoom-blade-root-traces", "tri-r6-zoom-planform-v7-on-frames"],
    }
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    supersessions = {"tri-r6e-blade-planform-arcs": "tri-r6f-blade-planform-gap", "tri-r6e-notch-exposure": "tri-r6f-blade-planform-gap"}
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

    s02["validations"] = [v for v in s02["validations"] if v["id"] != "planform-profile-measured"] + [
        {"id": "planform-profile-measured", "status": "pass", "detail": "凸弧模型：4 条干净边圆弧拟合 rms ≤0.0010 R（直线 0.011–0.015 R）；R_s 1.367 R、圆心距 0.92 R；根部内收弧 R 0.15 R 止于盖圈极角 52°（实测 51–53°），缺口露盖 16°，相邻叶不相接；CAD v7 由模型绘出并反投影叠加 f0077/f0078（planform-v7-on-frames.png）"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 07:53 v7:")[0]
        + " | 09-07 07:53 v7: 用户指出相邻叶片有间隔、不相接；根部描迹证实叶边在极角 51–53° 止于盖圈、缺口露盖 ≈16°；CAD v7 以 R≈0.15 R 内收弧接入盖圈，v6 的 V 交点作废。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v7 — blade edges blend (R≈0.15 R) into the cap circle at polar 52°, adjacent blades separated by a ≈16° exposed-cap gap; v6 V-apex superseded (claim tri-r6f-blade-planform-gap). User 2026-09-07 07:53 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
