"""Amend Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
14:25 "你是不会用圆角吗": the v17 pocket used chamfer-style corner cuts; now every
pocket corner and edge is a true circular fillet (plan arcs R0.05 / R0.03,
section fillets R0.03 convex at the mouth edge and concave at the floor edge).
Re-hashes CAD v16, relief v17, the evidence board and the spec; amends the pocket
claim. No approvals, no gate crossing, no workbench refresh.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "你是不会用圆角吗"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review"
    instr = A02 / "user-instructions-2026-09-07-1425.md"
    instr.write_text(
        "# 用户指令 2026-09-07 14:25（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "解读：v17 首版的凹坑“圆角”只是切角（直线倒角），不是圆弧。改为真圆角：顶视口沿/平底角为相切圆弧（R0.05 / R0.03 占位），"
        "剖面口沿为凸圆角 R0.03（顶面→斜壁）、平底边为凹圆角 R0.03（斜壁→平底）。CAD v16、阴影图 v17、证据板与 spec D08 同步重做。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    ids = {a["id"]: a for a in manifest["assets"]}
    base.upsert(manifest, base.asset("tri-r6-user-instructions-1425", "02-analysis", "analysis-board", instr, "user-input", "user-instruction-exact-wording-2026-09-07-1425", "user-provided", "user", [], "原话 + 解读"))
    if "tri-r6-user-instructions-1425" not in s02["artifactIds"]:
        s02["artifactIds"].append("tri-r6-user-instructions-1425")
    for aid, path in [
        ("tri-r6-cad-v16-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v16.py"),
        ("tri-r6-reference-cad-v16", A02 / "reference-cad-from-video-v16.png"),
        ("tri-r6-reference-cad-v16-pdf", A02 / "reference-cad-from-video-v16.pdf"),
        ("tri-r6-shaded-relief-v17", A02 / "shaded-relief-v17.png"),
        ("tri-r6-shaded-relief-v17-script", REPO / "tools/model-provenance-explorer/shade_geeone_reference_v17.py"),
        ("tri-r6-edge-gradient-pocket-evidence", A02 / "edge-gradient-pocket-funnel-user-1401-vs-v17.png"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json"),
    ]:
        old = ids[aid]
        srcs = list(old.get("sourceAssetIds", []))
        if aid != "tri-r6-cad-v16-script" and "tri-r6-user-instructions-1425" not in srcs and aid in ("tri-r6-reference-cad-v16", "tri-r6-shaded-relief-v17", "tri-r6-edge-gradient-pocket-evidence", "tri-r6-surface-detail-spec"):
            srcs.append("tri-r6-user-instructions-1425")
        prov = old["provenance"]
        base.upsert(manifest, base.asset(aid, old["stageId"], old["slot"], path, old["role"], prov["contentClass"], prov["origin"], prov["assertedBy"], srcs, prov.get("note", "") + (" · 14:25 true fillets" if "true fillets" not in prov.get("note", "") else "")))
    for c in manifest["claims"]:
        if c["id"] == "tri-r6f-pocket-funnel-step-rounded":
            c["statement"] = c["statement"].replace("口/底所有角圆角（≈0.04 / 0.025 R 占位）", "口/底所有角为**真圆角**（相切圆弧：顶视口 R≈0.05、底 R≈0.03；剖面口沿凸圆角 R≈0.03、底边凹圆角 R≈0.03，均占位；不是切角）")
            c["amendedAt"] = NOW
            c["amendment"] = "user 2026-09-07 14:25 '你是不会用圆角吗' — chamfer-style corner cuts replaced by tangent circular fillets in plan and section"
            if "tri-r6-user-instructions-1425" not in c["sourceAssetIds"]:
                c["sourceAssetIds"].append("tri-r6-user-instructions-1425")
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    for c in doc["claims"]:
        if c["id"] == "tri-r6f-pocket-funnel-step-rounded":
            src = [x for x in manifest["claims"] if x["id"] == c["id"]][0]
            c.update({k: src[k] for k in ("statement", "amendedAt", "amendment", "sourceAssetIds")})
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))
    for v in s02["validations"]:
        if v["id"] == "root-pocket-form":
            v["detail"] = v["detail"].replace("+ 口/底圆角", "+ 口/底真圆角（顶视相切圆弧 R0.05/0.03，剖面口沿凸 R0.03、底凹 R0.03）")
    manifest["currentState"]["diagnosis"] = manifest["currentState"]["diagnosis"].split(" | 09-07 14:25:")[0] + " | 09-07 14:25: 用户“你是不会用圆角吗”→ 凹坑切角改为真圆角（顶视圆弧 + 剖面凸/凹圆角），CAD v16 / 阴影图 v17 / 证据板重做。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 amended (still ready_for_review): pocket corners/edges are now true circular fillets (plan arcs R0.05 mouth / R0.03 floor; section convex R0.03 at the mouth edge, concave R0.03 at the floor edge, all provisional) in CAD v16, shaded relief v17, spec D08 and claim tri-r6f-pocket-funnel-step-rounded. User 2026-09-07 14:25 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
