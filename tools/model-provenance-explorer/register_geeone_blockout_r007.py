"""Gate 05 blockout rev-007: cap rim overhangs a recessed rotating hub seat (user 2026-09-07 18:33 mark-up on r006).

Also registers CAD v17 (A-A / Detail G show the overhang + hub seat) and spec v18 (D03/D09) under Gate 02 rev-006,
and marks blockout rev-006 rejected with the user's exact wording. No approvals.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A02 = base.A02
A05 = base.EV / "05-blockout/rev-007"
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "不知道你能不能理解啊？就是黄色的部分，它的圆圈的半径应该是大于内部的这个轴心的转动的承托的。所以我用颜色标示了一下：绿色的应该是往内收。它的这个圆环是要往内收，然后上下内凹的这个圆盘要稍微盖住中间的一点点。"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    s05 = base.stage(manifest, "05-blockout")
    assert s05["revision"] == 6

    instr = A05 / "user-instructions-2026-09-07-1833.md"
    instr.write_text(
        "# 用户指令 2026-09-07 18:33（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：在 Gate 05 rev-006 白模（缺口特写）上，黄弧 = 盖缘（盘 + 冠环 + 裙）与箭头，绿框 = 盖缘下的竖直环并箭头指向内。\n\n"
        "解读（spec v18 D03/D09，CAD v17，白模 rev-007）：盖缘半径 > 内部“轴心转动的承托”（毂座）。盖缘下面不是与盖同径的竖壁，而是**内收的毂座圆柱**"
        "（R = 盖 − 0.03 R 占位，高 ≈0.057 R），上下两片内凹圆盘的盖缘略微盖住毂座；暗缝 = 外悬下的阴影。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；Gate 05 rev-007 ready_for_review；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    # ---- Gate 02: CAD v17 + spec v18 (same revision, refined)
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-markup-1833", A05 / "user-markup-2026-09-07-1833-cap-overhang.png", "analysis-board", "user-input", "user-markup-on-blockout-r006-cap-overhang", "user-provided", "user", ["tri-r6g-check-notch-macro"], "用户 18:33：黄 = 盖缘半径 > 毂座；绿 = 环往内收"),
        ("tri-r6-user-instructions-1833", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-1833", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-cad-v17-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v17.py", "analysis-board", "process", "reference-cad-v17-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1833"], "A-A / Detail G：盖缘外悬 + 内收毂座"),
        ("tri-r6-reference-cad-v17", A02 / "reference-cad-from-video-v17.png", "structural-cad", "analysis", "reference-cad-v17-cap-overhang-hub-seat", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1833", "tri-r6-user-markup-1833"], "v17 is the current reference CAD; v1-v16 history"),
        ("tri-r6-reference-cad-v17-pdf", A02 / "reference-cad-from-video-v17.pdf", "structural-cad", "analysis", "reference-cad-v17-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1833"], "v17 vector"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    ids = {a["id"]: a for a in manifest["assets"]}
    spec_old = ids["tri-r6-surface-detail-spec"]
    srcs = list(spec_old["sourceAssetIds"]) + ["tri-r6-user-instructions-1833"]
    base.upsert(manifest, base.asset("tri-r6-surface-detail-spec", "02-analysis", spec_old["slot"], A02 / "surface-detail-spec.json", spec_old["role"], spec_old["provenance"]["contentClass"], spec_old["provenance"]["origin"], spec_old["provenance"]["assertedBy"], srcs, spec_old["provenance"].get("note", "") + "; v18 D03/D09 cap overhang + recessed hub seat"))
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v16", "tri-r6-reference-cad-v16-pdf", "tri-r6-cad-v16-script"):
            a["provenance"]["note"] = "v16 — superseded by tri-r6-reference-cad-v17 (cap overhang + hub seat); kept as history"
    cap_claim = {
        "id": "tri-r6f-cap-overhang-hub-seat", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (structure: user 18:33 statement + f0132/f0116 dark undercut under the rim) / low (overhang 0.03 R, hub seat 0.455 R, height 0.057 R)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "盖缘（盘 + 冠环 + 裙）的半径大于其下方“轴心转动的承托”（毂座）：盖裙底边就是盖的下缘，其下是一段**内收的毂座圆柱**（R ≈ 盖 − 0.03 R、高 ≈0.057 R，均占位）把盖接到转子上；上下两片内凹圆盘的盖缘都略微盖住毂座；缺口处看到的暗缝就是外悬下的阴影，不是与盖同径的竖壁。依据：用户 2026-09-07 18:33 原话“黄色的部分，它的圆圈的半径应该是大于内部的这个轴心的转动的承托的…绿色的应该是往内收…上下内凹的这个圆盘要稍微盖住中间的一点点”。修正 tri-r6f-cap-edge-three-tiers 中“再接一小段竖直 14 边形侧壁到暗缝”的表述。",
        "sourceAssetIds": ["tri-r6-user-markup-1833", "tri-r6-user-instructions-1833", "tri-r6-frame-0132", "tri-r6-frame-0116", "tri-r6-reference-cad-v17"],
        "refines": ["tri-r6f-cap-edge-three-tiers", "tri-r6-surface-detail-spec"],
    }
    if cap_claim["id"] not in {c["id"] for c in manifest["claims"]}:
        manifest["claims"].append(cap_claim)
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    if cap_claim["id"] not in {c["id"] for c in doc["claims"]}:
        doc["claims"].append(cap_claim)
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))
    s02["validations"] = [v for v in s02["validations"] if v["id"] != "cap-overhang-hub-seat"] + [
        {"id": "cap-overhang-hub-seat", "status": "pass", "detail": "D03/D09 v18：盖缘外悬 0.03 R（占位）于内收毂座 R0.455、高 0.057 R；用户 18:33 原话；CAD v17 A-A/Detail G；claim tri-r6f-cap-overhang-hub-seat"},
    ]

    # ---- Gate 05: rev-006 rejected -> rev-007
    s05.setdefault("historicalRevisions", []).append({"revision": 6, "artifactIds": list(s05["artifactIds"]), "status": "rejected", "reason": "用户 2026-09-07 18:33：盖缘半径应大于毂座，环往内收，上下圆盘略盖住中间（原话见 user-instructions-2026-09-07-1833.md）"})
    s05.setdefault("historicalDecisions", []).append({"revision": 6, "decision": "rejected", "decidedAt": NOW, "decidedBy": "user", "channel": "chat", "exactWording": USER_TEXT, "replacement": "rev-007: cap overhang + recessed hub seat"})
    s05["revision"] = 7
    s05["artifactIds"] = []
    s05["status"] = "ready_for_review"
    s05["decision"] = None
    assets = [
        ("tri-r6h-user-instructions-1833", instr, "white-model-source", "user-input", "user-instruction-exact-wording-2026-09-07-1833", "user-provided", "user", [], "原话 + 解读（同 Gate 02 登记）"),
        ("tri-r6h-user-markup-1833", A05 / "user-markup-2026-09-07-1833-cap-overhang.png", "white-model-source", "user-input", "user-markup-on-blockout-r006", "user-provided", "user", ["tri-r6g-check-notch-macro"], ""),
        ("tri-r6h-geometry-contract", A05 / "geeone-gate02-geometry-contract.json", "white-model-source", "contract", "gate02-geometry-contract-r-units", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v17", "tri-r6-cad-v17-script"], "v18 spec / CAD v17：+capOverhangToR、hubSeatRadiusToR、hubSeatHeightToR；verticalSideToR 0"),
        ("tri-r6h-builder", A05 / "build_geeone_gate02_blockout.py", "white-model-source", "process", "bpy-deterministic-blockout-builder", "repository-generated", "repository", ["tri-r6h-geometry-contract"], "rev-007：盖无竖壁、盖底为唇；Hub_Seat_Top/Bottom 圆柱（暗材质）；其余同 rev-006；coverage 10/10"),
        ("tri-r6h-blend", A05 / "geeone-blockout-r007.blend", "white-model-source", "source-model", "blockout-blend-r007", "repository-generated", "repository", ["tri-r6h-builder", "tri-r6h-geometry-contract"], "Rotor_Body 2125 顶点 / 2012 面 / 0 非流形；Cap_Top/Bottom；Hub_Seat_Top/Bottom"),
    ]
    for name in ("top-ortho", "bottom-ortho", "hero", "left-oblique", "right-oblique", "low", "blade-macro-f0132", "edge-macro", "cap-macro", "notch-macro", "review-board"):
        assets.append((f"tri-r6h-check-{name}", A05 / "checks" / f"{name}.png", "white-model-preview", "analysis", f"workbench-white-{name}", "repository-generated", "repository", ["tri-r6h-blend"], "Workbench STUDIO 单色 + cavity"))
    for name in ("top", "hero", "left-oblique", "right-oblique", "low", "front", "back", "left", "right", "bottom"):
        assets.append((f"tri-r6h-view-{name}", A05 / "fixed-views" / f"{name}.png", "white-model-preview", "analysis", f"fixed-camera-pack-{name}", "repository-generated", "repository", ["tri-r6h-blend"], "capture_standard_views.py（EEVEE）"))
    assets.append(("tri-r6h-fixed-views-report", A05 / "fixed-views" / "capture-wrapper-report.json", "white-model-preview", "process", "fixed-camera-pack-report", "repository-generated", "repository", ["tri-r6h-blend"], ""))
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in assets:
        base.upsert(manifest, base.asset(aid, "05-blockout", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s05["artifactIds"]:
            s05["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"].startswith("tri-r6g-"):
            a["provenance"]["note"] = (a["provenance"].get("note", "") + " · rev-006 rejected 2026-09-07 18:33 (cap overhang)").strip(" ·")
    prev_val = {v["id"]: v for v in s05["validations"]}
    s05["validations"] = [v for v in s05["validations"] if v["id"] not in ("cap", "upstream-gates-pending")] + [
        {"id": "upstream-gates-pending", "status": "warn", "detail": prev_val.get("upstream-gates-pending", {}).get("detail", "Gate 01/02 仍 ready_for_review")},
        {"id": "cap", "status": "pass", "detail": "D01–D03 v18：盘 0.82×盖 14 扇区凹 3°、冠环 14 楔、裙 14×2；盖缘 R0.485 外悬毂座 R0.455（0.03 R 占位），毂座高 0.057 R；盖无竖壁，底为唇；上下镜像"},
        {"id": "cap-overhang-user-1833", "status": "pass", "detail": "用户 18:33 修正已落地：环往内收（毂座）、上下内凹圆盘略盖住中间；checks/notch-macro.png、low.png"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 18:33 blockout r007:")[0]
        + " | 09-07 18:33 blockout r007: 用户指出盖缘半径应大于内部轴心承托、环往内收、上下圆盘略盖住中间 → spec D03/D09 v18 + CAD v17（A-A/Detail G 外悬 + 毂座）+ 合同/构建器 rev-007（盖无竖壁，Hub_Seat R0.455 高 0.057）；rev-006 rejected。Gate 05 rev-007 ready_for_review；Gate 01/02 仍 ready_for_review；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for ev in (
            {"type": "stage-note", "stageId": "02-analysis", "notes": "rev-006 refined: spec D03/D09 v18 + CAD v17 — cap rim overhangs a recessed rotating hub seat (overhang 0.03 R, seat R0.455, height 0.057 R, provisional); claim tri-r6f-cap-overhang-hub-seat. User 2026-09-07 18:33 exact wording: " + USER_TEXT},
            {"type": "stage-rejected", "stageId": "05-blockout", "notes": "05-blockout rev-006 rejected by the user (cap side wall flush with the rim). Exact wording: " + USER_TEXT},
            {"type": "stage-revised", "stageId": "05-blockout", "notes": "05-blockout rev-007 ready_for_review: cap without wall, Hub_Seat_Top/Bottom recessed cylinders under the overhanging lip; coverage 10/10; 0 non-manifold; Workbench views + fixed camera pack. No approval."},
        ):
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "stage05": s05["revision"], "assets": len(added)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
