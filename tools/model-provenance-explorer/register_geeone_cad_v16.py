"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
14:01 mark-up of shaded relief v16: (red) pocket corners rounded, (blue) the
pocket has sloped walls that flare outward and a deeper stepped floor, (yellow)
the plane -> vertical transition is a wide stack of different gradients, not a
thin carved band. Registers CAD v16, shaded relief v17, the evidence board
(user mark-up + f0124 6x + relief), the user's drawing + exact wording, two
superseding claims. No approvals, no gate crossing, no workbench refresh.
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
USER_TEXT = "红色部分要用圆角过渡。然后，里面的内凹的那个部分的台阶要更深一些。蓝色部分，它是有一个斜面过渡的。你现在只是向内收了，应该向外扩展，它的深度也要更深。图片的这个黄色部分，它本身是用不同的梯度来进行平面和垂直面的过渡。你现在只是轻轻地在上面做了一层雕刻，所以这个和原图是不对的。"


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review"

    # Gate 01: store key frames f0116 / f0124 (cited by D05/D08 v17), hashed into the intake record
    s01 = base.stage(manifest, "01-intake")
    rec_path = base.A01 / "intake-record.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    fe = rec["frameExtraction"]
    for n in (116, 124):
        frame = base.A01 / "frames10-key" / f"f_{n:04d}.jpg"
        if not frame.exists():
            shutil.copy2(Path(f"/tmp/dragon-scale-gate02/video/frames10/f_{n:04d}.jpg"), frame)
        if n not in fe["storedKeyFrames"]:
            fe["storedKeyFrames"] = sorted(set(fe["storedKeyFrames"]) | {n})
        fe["storedKeyFrameSha256"][f"f_{n:04d}.jpg"] = base.sha256(frame)
        aid = f"tri-r6-frame-{n:04d}"
        base.upsert(manifest, base.asset(aid, "01-intake", "original-reference", frame, "external-reference", f"video-frame-extract-t{(n - 1) / 10:.1f}s", "external", "repository", ["tri-r6-video-source"], "ffmpeg fps=10 frame, unmodified"))
        if aid not in s01["artifactIds"]:
            s01["artifactIds"].append(aid)
    rec_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-intake-record", "01-intake", "source-metadata", rec_path, "process", "intake-record-with-hashes-and-frame-command", "repository-generated", "repository", ["tri-r6-video-source"]))

    shot = A02 / "user-markup-2026-09-07-1401-relief-v16-red-blue-yellow.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-601279fe-4d06-4126-934a-b054a14f16b5.png", shot)
    instr = A02 / "user-instructions-2026-09-07-1401.md"
    instr.write_text(
        "# 用户指令 2026-09-07 14:01（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：在 `blade-top-facets-user-1327-vs-v16.png` 右图（阴影图 v16 上叶）上标红圈 / 蓝线 / 黄线。\n\n"
        "解读（Gate 02 rev-006 v17）：\n"
        "- 红（凹坑四角）→ D08 口沿与平底所有角都圆角过渡（口 0.04 R、底 0.025 R 占位）。\n"
        "- “内凹的台阶要更深”→ D08 平底深度由 25% 厚/侧改 38% 厚/侧（占位，仍 unknown）。\n"
        "- 蓝（坑两侧）→ D08 坑壁是**斜面漏斗**：口沿在顶视描迹线外 0.03 R、平底在内 0.03 R，壁 ≈47°；v16 的直壁 + 内收窄缝作废。f0116/f0120/f0124/f0128 6× 可见圆角尖、亮口沿斜带、暗深腔。\n"
        "- 黄（叶尖面左侧的梯级）→ D05 平面→竖直面的过渡是**多梯度宽过渡**，不是 0.07 R 的一层浅雕：T/F/C ≈15° → A 层大斜面 0.07 R@22°（每边 3 片错位）→ 鸢形 38° / Λ 53° 到中面，整段 ≈0.14 R；f0116/f0124 3× 叶顶大刻面。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-markup-1401", shot, "analysis-board", "user-input", "user-markup-on-relief-v16-pocket-and-gradients", "user-provided", "user", ["tri-r6-shaded-relief-v16", "tri-r6-blade-top-facets-evidence"], "用户 09-07 14:01：红圆角 / 蓝斜面外扩更深 / 黄多梯度"),
        ("tri-r6-user-instructions-1401", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-1401", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-edge-gradient-pocket-evidence", A02 / "edge-gradient-pocket-funnel-user-1401-vs-v17.png", "analysis-board", "analysis", "evidence-user-markup-vs-f0124-6x-vs-relief-v17", "repository-generated", "repository", ["tri-r6-frame-0124", "tri-r6-frame-0116", "tri-r6-user-markup-1401", "tri-r6-user-instructions-1401"], "用户标注 + f0124 6× 漏斗坑 + 阴影图 v17"),
        ("tri-r6-cad-v16-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v16.py", "analysis-board", "process", "reference-cad-v16-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1401"], ""),
        ("tri-r6-reference-cad-v16", A02 / "reference-cad-from-video-v16.png", "structural-cad", "analysis", "reference-cad-v16-wide-gradient-edge-funnel-pocket", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1401", "tri-r6-user-markup-1401", "tri-r6-edge-gradient-pocket-evidence"], "v16 is the current reference CAD; v1-v15 history"),
        ("tri-r6-reference-cad-v16-pdf", A02 / "reference-cad-from-video-v16.pdf", "structural-cad", "analysis", "reference-cad-v16-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1401"], "v16 vector"),
        ("tri-r6-shaded-relief-v17", A02 / "shaded-relief-v17.png", "analysis-board", "analysis", "shaded-relief-height-field-illustration", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v16", "tri-r6-user-instructions-1401"], "2.5D hillshade + relative-height map; edge = tier A + kite/Λ (0.14 R); pocket = sloped funnel + deeper stepped floor, rounded corners; not a blockout, not a render; heights provisional"),
        ("tri-r6-shaded-relief-v17-script", REPO / "tools/model-provenance-explorer/shade_geeone_reference_v17.py", "analysis-board", "analysis", "shaded-relief-script", "repository-generated", "repository", ["tri-r6-cad-v16-script"], ""),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839", "tri-r6-user-instructions-0936", "tri-r6-user-instructions-1040", "tri-r6-user-instructions-1055", "tri-r6-user-instructions-1110", "tri-r6-user-instructions-1147", "tri-r6-user-instructions-1327", "tri-r6-user-instructions-1401"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 v16 hard-cut top facets, D02/D03 cap-edge three tiers, D05 v17 wide multi-gradient edge (tier A + kite/Λ), D08 v17 funnel pocket"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v15", "tri-r6-reference-cad-v15-pdf", "tri-r6-cad-v15-script"):
            a["provenance"]["note"] = "v15 — superseded by tri-r6-reference-cad-v16 (wide multi-gradient edge, funnel pocket); kept as history"
        if a["id"] in ("tri-r6-shaded-relief-v16", "tri-r6-shaded-relief-v16-script"):
            a["provenance"]["note"] = "v16 — superseded by tri-r6-shaded-relief-v17 (user 14:01 mark-up); kept as history"

    edge = {
        "id": "tri-r6f-blade-edge-wide-gradient-transition", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (wide multi-gradient stack, kite/Λ interlock: user 14:01 + f0116/f0124 3× + f0148/f0150/f0152 10×) / low (tier widths, slopes, facet lengths)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片从顶面到竖直面的过渡是一段**宽的多梯度刻面叠层**，不是 0.07 R 的一层浅雕：顶面 T/F/C（≈15°）→ A 层大斜面（≈0.07 R 宽、≈22°、每边 3 片 ≈0.25 R 长、与鸢形错半片）→ 亮鸢形（≈38°）与暗 Λ（≈53°）一道深锯齿咬合到中面（0.07 R），整段径向 ≈0.14 R，叶尖 x>0.85 R 处整个顶面都是过渡刻面；每片独立平面、硬折边，下半镜像。依据：用户 2026-09-07 14:01 黄线“本身是用不同的梯度来进行平面和垂直面的过渡，你现在只是轻轻地在上面做了一层雕刻”；f0116/f0124 3× 叶顶大刻面；f0148/f0150/f0152 10× 鸢形/Λ（保留）。角度/宽度/长度均占位，斜度按到中面归一。取代 tri-r6f-blade-side-kite-lambda-interlock（其鸢形/Λ 读法保留为最后两级）。",
        "sourceAssetIds": ["tri-r6-user-markup-1401", "tri-r6-user-instructions-1401", "tri-r6-frame-0116", "tri-r6-frame-0124", "tri-r6-frame-0148", "tri-r6-frame-0150", "tri-r6-frame-0152", "tri-r6-edge-gradient-pocket-evidence", "tri-r6-reference-cad-v16", "tri-r6-shaded-relief-v17"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    pocket = {
        "id": "tri-r6f-pocket-funnel-step-rounded", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (funnel walls, deeper step, rounded corners: f0116/f0120/f0124/f0128 6× + user 14:01) / low (offsets 0.03 R, depth 0.38 t, slope ≈47°)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶根凹坑不是直壁 + 内收窄缝的坑，而是**斜面漏斗 + 深台阶 + 圆角**：口沿在顶视描迹线（尖 0.70 R、底半宽 0.135 R）外 ≈0.03 R，平底在内 ≈0.03 R，壁 ≈47°（占位）；平底为更深的台阶（≈0.38 厚/侧占位，原 0.25）；口/底所有角圆角（≈0.04 / 0.025 R 占位）；朝盖缝开口；下半镜像。f0116/f0120/f0124/f0128 6×：圆角尖、受光的斜口沿亮带、暗深腔、开口通向暗缝。依据：用户 2026-09-07 14:01“红色部分要用圆角过渡…内凹的台阶要更深…蓝色部分有一个斜面过渡，你现在只是向内收了，应该向外扩展，深度也要更深”。取代 tri-r6-root-pocket 的“外壁为斜切面、底部暗、深度未知”描述中的形态部分（深度仍 unknown）。",
        "sourceAssetIds": ["tri-r6-user-markup-1401", "tri-r6-user-instructions-1401", "tri-r6-frame-0116", "tri-r6-frame-0124", "tri-r6-frame-0132", "tri-r6-edge-gradient-pocket-evidence", "tri-r6-reference-cad-v16", "tri-r6-shaded-relief-v17"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    supersede(manifest, "tri-r6f-blade-side-kite-lambda-interlock", edge)
    supersede(manifest, "tri-r6-root-pocket", pocket)
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    have = {c["id"] for c in doc["claims"]}
    for c in (edge, pocket):
        if c["id"] not in have:
            doc["claims"].append(c)
    for c in doc["claims"]:
        if c["id"] == "tri-r6f-blade-side-kite-lambda-interlock":
            c.update({"state": "superseded", "supersededBy": edge["id"], "supersededAt": NOW})
        if c["id"] == "tri-r6-root-pocket":
            c.update({"state": "superseded", "supersededBy": pocket["id"], "supersededAt": NOW})
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] not in ("blade-edge-scale-rows", "root-pocket-form")] + [
        {"id": "blade-edge-scale-rows", "status": "pass", "detail": "D05 v17 = 宽多梯度过渡 0.14 R：T/F/C ≈15° → A 层 0.07 R@22°（3 片/边错位）→ 鸢形 38°/Λ 53° 到中面；用户 14:01 黄线 + f0116/f0124；CAD v16 三层剖面 + Detail H；阴影图 v17；claim tri-r6f-blade-edge-wide-gradient-transition"},
        {"id": "root-pocket-form", "status": "pass", "detail": "D08 v17 = 斜面漏斗（口外扩 0.03 / 底内收 0.03 R，≈47°）+ 深平底台阶 0.38 t/侧 + 口/底圆角；用户 14:01 红/蓝 + f0116–f0128 6×；CAD v16 顶视双轮廓 + A-A/C-C 漏斗剖面；claim tri-r6f-pocket-funnel-step-rounded；深度仍 unknown"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 14:01 v17:")[0]
        + " | 09-07 14:01 v17: 用户在阴影图 v16 上标红/蓝/黄 → D08 改斜面漏斗（口外扩、底内收 0.03 R）+ 更深平底台阶（0.38 t/侧占位）+ 圆角；D05 改宽多梯度过渡 0.14 R（T/F/C → A 层大斜面 22° → 鸢形/Λ）；CAD v16 + 阴影图 v17 + 证据板；Gate 01 补入 f0116/f0124。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v16 + shaded relief v17 — D05 = wide multi-gradient edge transition 0.14 R (T/F/C ≈15° -> tier A 0.07 R @22° staggered quads -> kite 38° / Λ 53° to the mid-plane); D08 = sloped funnel pocket (mouth +0.03 R, floor -0.03 R, ≈47°) with a deeper stepped floor (0.38 t per side, provisional) and rounded corners; claims tri-r6f-blade-edge-wide-gradient-transition and tri-r6f-pocket-funnel-step-rounded supersede kite-lambda-interlock and tri-r6-root-pocket; Gate 01 +f0116/f0124. User 2026-09-07 14:01 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
