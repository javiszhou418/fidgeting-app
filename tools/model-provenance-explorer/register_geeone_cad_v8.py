"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
08:25 feedback: the cap disc is divided into 14 equal sectors about its centre.
High-pass unwrap of f0077 confirms per-sector brightness steps every ≈26°, so
D01 becomes a concave 14-gon pyramid (14 planar sectors) whose rim vertices
coincide with the crown's inner vertices. Registers CAD v8, the disc evidence,
the user's screenshot + exact wording, a new claim and one supersession.
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
USER_TEXT = "这个圆应该以圆心为中心，作为中心点，然后被切分成14片。均分。"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review", (s02["revision"], s02["status"])

    shot = A02 / "user-screenshot-2026-09-07-0825-disc-14.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-ce78c372-a9e3-470a-9bc7-a1b6ed0f4730.png", shot)
    instr = A02 / "user-instructions-2026-09-07-0825.md"
    instr.write_text(
        "# 用户指令 2026-09-07 08:25（原话，针对 planform-v7-on-frames 盖部截图）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：f0077 盖部叠加图裁切（蓝圈 = 盖外圈与盘缘）。\n\n"
        "解读（Gate 02 rev-006 v8）：中央盘以圆心为顶点被均分为 14 个平面扇区（凹 14 棱锥拇指位），盘缘为 14 边形（0.82×盖），"
        "其顶点与冠环 14 楔的内顶点重合，盘/冠环/裙共用一套 14 等分。f0077 角向高通展开图在受光半周每 ≈26° 一条扇区亮度阶跃，与 14 等分相符；"
        "凹深仍未知（顶点透视位移 ≤2 px → 视频上限约 2°，占位 3°）。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-disc-14", shot, "analysis-board", "user-input", "user-screenshot-f0077-cap-overlay", "user-provided", "user", ["tri-r6-frame-0077"], "用户 09-07 08:25：“以圆心为中心…被切分成14片。均分”"),
        ("tri-r6-user-instructions-0825", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-0825", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-cad-v8-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v8.py", "analysis-board", "process", "reference-cad-v8-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0825"], ""),
        ("tri-r6-reference-cad-v8", A02 / "reference-cad-from-video-v8.png", "structural-cad", "analysis", "reference-cad-v8-14-sector-concave-disc", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0825", "tri-r6-user-screenshot-disc-14"], "v8 is the current reference CAD; v1-v7 history"),
        ("tri-r6-reference-cad-v8-pdf", A02 / "reference-cad-from-video-v8.pdf", "structural-cad", "analysis", "reference-cad-v8-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-0825"], "v8 vector"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform + D01 = 14-sector concave faceted disc"),
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
        if a["id"] in ("tri-r6-reference-cad-v7", "tri-r6-reference-cad-v7-pdf", "tri-r6-cad-v7-script"):
            a["provenance"]["note"] = "v7 — superseded by tri-r6-reference-cad-v8 (disc = 14 equal planar sectors, concave 14-gon pyramid); blades unchanged; kept as history"

    claims = {c["id"]: c for c in manifest["claims"]}
    new_claim = {
        "id": "tri-r6f-disc-14-sectors", "stageId": "02-analysis", "category": "geometry", "confidence": "high (14 sectors) / user-stated (concave) / unknown (depth)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "中央盘不是光滑车削平盘，而是以圆心为顶点均分的 14 个平面扇区（凹 14 棱锥拇指位）：盘缘为 14 边形（0.82×盖，0.80–0.85），其顶点与冠环 14 楔的内顶点重合，盘、冠环、裙共用一套 14 等分。依据：用户 2026-09-07 08:25 原话“这个圆应该以圆心为中心，作为中心点，然后被切分成14片。均分”；f0077 校正后角向高通展开图（disc-unwrap-f0077-highpass.png）在受光半周每 ≈26° 一条扇区亮度阶跃，6× 高通图（disc-sectors-f0077.png）中 14 辐条（相位 ≈16°）与分界吻合；f0204/f0208 盘面放射扇区明暗。凹向按用户口述（20:46 “凹下去…放拇指”）；深度未知——顶点相对盘缘的透视位移仅 ±2 px（f0077/f0078 符号不一），视频上限约 2° 斜度，CAD 以 3° 占位。扇区内可见细同心刀痕，仅作表面纹理。取代 tri-r6e-cap-dish-user-stated（“车削浅锥/碟”）。",
        "sourceAssetIds": ["tri-r6-frame-0077", "tri-r6-frame-0078", "tri-r6-frame-0204", "tri-r6-frame-0208", "tri-r6-user-screenshot-disc-14", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-2046", "tri-r6-zoom-disc-sectors-f0077", "tri-r6-zoom-disc-unwrap-f0077-highpass"],
    }
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    supersessions = {"tri-r6e-cap-dish-user-stated": "tri-r6f-disc-14-sectors"}
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
    doc["openConflictsForUser"] = [x for x in doc["openConflictsForUser"] if x.get("topic") != "盖顶凹凸"] + [
        {"topic": "盖顶凹凸", "adopted": "E1 盘缘 14 边形最高、冠环向外向下、盘为 14 扇区凹棱锥（用户口述）", "alternative": "E2 整顶内凹、冠环向内向下", "evidence": "f0077 远侧冠环被压缩 → E1；盘凹深视频上限 ≈2°"},
    ]
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] != "cap-facet-count"] + [
        {"id": "cap-facet-count", "status": "pass", "detail": "盘 14 等分平面扇区（高通展开每 ≈26° 一条分界；用户计数）；冠环 14±1 楔（展开计数 + FFT 12–15，无 24）；盖裙 14 鳞 ×2 排（f0200/f0208）；三者共用一套 14 等分"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 08:25 v8:")[0]
        + " | 09-07 08:25 v8: 用户指出盘以圆心为中心均分 14 片；高通展开证实每 ≈26° 一条扇区分界，D01 改为 14 平面扇区凹棱锥（盘缘 14 边形与冠环内顶点重合），凹深未知（3° 占位，视频上限 ≈2°）。CAD v8。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v8 — cap disc = 14 equal planar sectors about the centre (concave 14-gon pyramid, rim 14-gon aligned with the crown); claim tri-r6f-disc-14-sectors supersedes tri-r6e-cap-dish-user-stated. User 2026-09-07 08:25 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
