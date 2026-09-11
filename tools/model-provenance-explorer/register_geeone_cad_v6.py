"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-06
20:46 feedback on CAD v5 (two screenshots): blade sides are convex arcs hugging
the cap (no shoulder, acute crescent), cap crown has 14 wedges, disc is a
concave thumb dish (user-stated). Registers CAD v6, the per-blade traces, the
frame overlays, the cap evidence panel, three extra Gate 01 key frames, the
user's screenshots + exact wording, new claims and supersessions.

No approvals, no gate crossing, no workbench refresh; digests recomputed here.
"""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A01 = base.A01
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()
ASSETS_IN = Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets")
USER_TEXT = (
    "第一个问题就是它的这个过渡应该更像这个图片里面红圈圈出来的。它还是有点像一个毛形状的，就是它下面这个斜切线不是有一个弧度，"
    "你好像做了一个拐角嘛。下面这层拐角应该几乎是锐角，中间的圆心几乎是贴近的状态。它的角角的角度应该是个锐角，你现在好像是个钝角。"
    "然后第二张图里面，明显是中间有一个凹下去的。中间这个圆被切分成了大概14片，有一个内凹的效果，是为了放拇指。"
)
NEW_FRAMES = [192, 200, 208]


def add_key_frames(manifest, s01):
    frames_dir = A01 / "frames10-key"
    record_path = A01 / "intake-record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    stored = list(record["frameExtraction"]["storedKeyFrames"])
    for idx in NEW_FRAMES:
        dst = frames_dir / f"f_{idx:04d}.jpg"
        if not dst.exists():
            shutil.copy2(base.FRAMES_SRC / f"f_{idx:04d}.jpg", dst)
        aid = f"tri-r6-frame-{idx:04d}"
        base.upsert(manifest, base.asset(aid, "01-intake", "original-reference", dst, "external-reference", f"video-frame-extract-t{(idx - 1) / 10:.1f}s", "external", "repository", ["tri-r6-video-source"], "ffmpeg fps=10 frame, unmodified"))
        if aid not in s01["artifactIds"]:
            s01["artifactIds"].append(aid)
        if idx not in stored:
            stored.append(idx)
        record["frameExtraction"]["storedKeyFrameSha256"][f"f_{idx:04d}.jpg"] = base.sha256(dst)
    record["frameExtraction"]["storedKeyFrames"] = sorted(stored)
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-intake-record", "01-intake", "source-metadata", record_path, "process", "intake-record-with-hashes-and-frame-command", "repository-generated", "repository", ["tri-r6-video-source"]))


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s01 = base.stage(manifest, "01-intake")
    s02 = base.stage(manifest, "02-analysis")
    assert s01["revision"] == 3 and s01["status"] == "ready_for_review", (s01["revision"], s01["status"])
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review", (s02["revision"], s02["status"])
    add_key_frames(manifest, s01)

    # ---- user inputs (exact wording + screenshots) ----
    shot_notch = A02 / "user-screenshot-2026-09-06-2046-notch-redcircles.png"
    shot_cap = A02 / "user-screenshot-2026-09-06-2046-cap-concave.png"
    for src, dst in ((ASSETS_IN / "image-bebc061d-f200-4fdd-b06f-47b1f76faabc.png", shot_notch), (ASSETS_IN / "image-1cd0b5c7-340e-4bff-844a-e9de2d0d3beb.png", shot_cap)):
        if not dst.exists():
            shutil.copy2(src, dst)
    instr = A02 / "user-instructions-2026-09-06-2046.md"
    instr.write_text(
        "# 用户指令 2026-09-06 20:46（原话，针对 CAD v5 + 两张截图）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图 1：surface-detail-atlas 裁切（f0148 / f0134），四个红圈标出叶边接盖处的过渡。\n"
        "附图 2：f0077 盖部裁切（D08/D09 标注），用户指中间凹下去、被切分成约 14 片、为放拇指。\n\n"
        "解读（Gate 02 rev-006 v6）：\n"
        "1. 叶边是凸圆弧，直接扫到盖圈，无肩角；相邻两弧在角平分线相交于盖圈外 ≈0.005 R，弧与盖圈交角 ≈18°（锐角新月尖）。\n"
        "2. 冠环 14 楔（28 三角），盖裙 14 鳞 ×2 排；盘 0.82×盖，车削，盘内为凹面拇指位（用户口述；凹深未测）。\n"
        "   冠环斜向（向外向下）来自 f0077 透视；若用户指的是整顶内凹（冠环向内向下），见 CAD v6 Detail E2。\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-notch-redcircles", shot_notch, "analysis-board", "user-input", "user-screenshot-atlas-f0148-f0134-red-circles", "user-provided", "user", ["tri-r6-frame-0148", "tri-r6-frame-0134"], "用户 20:46 附图 1：红圈 = 叶边接盖处的过渡"),
        ("tri-r6-user-screenshot-cap-concave", shot_cap, "analysis-board", "user-input", "user-screenshot-f0077-cap", "user-provided", "user", ["tri-r6-frame-0077"], "用户 20:46 附图 2：“中间有一个凹下去的…切分成大概14片…放拇指”"),
        ("tri-r6-user-instructions-2046", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-06-2046", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-trace-script", REPO / "tools/model-provenance-explorer/trace_geeone_blade_root.py", "analysis-board", "process", "per-blade-root-trace-script", "repository-generated", "repository", ["tri-r6-frame-measurements"], "rectified per-blade outline traces vs CAD planforms"),
        ("tri-r6-overlay-v6-script", REPO / "tools/model-provenance-explorer/overlay_geeone_planform_v6.py", "analysis-board", "process", "planform-overlay-on-frames-script", "repository-generated", "repository", ["tri-r6-frame-measurements"], "inverse-rectified planform overlay on original frames"),
        ("tri-r6-cad-v6-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v6.py", "analysis-board", "process", "reference-cad-v6-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-2046"], ""),
        ("tri-r6-reference-cad-v6", A02 / "reference-cad-from-video-v6.png", "structural-cad", "analysis", "reference-cad-v6-convex-arc-sides-14-wedge-cap", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-2046", "tri-r6-user-screenshot-notch-redcircles", "tri-r6-user-screenshot-cap-concave"], "v6 is the current reference CAD; v1-v5 history"),
        ("tri-r6-reference-cad-v6-pdf", A02 / "reference-cad-from-video-v6.pdf", "structural-cad", "analysis", "reference-cad-v6-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-2046"], "v6 vector"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for p in sorted((A02 / "frame-zooms").glob("*.png")):
        if p.name.startswith("_"):
            continue
        aid = "tri-r6-zoom-" + p.stem
        existing = {a["id"]: a for a in manifest["assets"]}
        if aid not in existing or existing[aid]["sha256"] != base.sha256(p):
            base.upsert(manifest, base.asset(aid, "02-analysis", "analysis-board", p, "analysis", "frame-zoom-crop-or-trace", "repository-generated", "repository", ["tri-r6-video-source", "tri-r6-frame-measurements"]))
            added.append(aid)
    # re-hash changed contract/doc assets
    base.upsert(manifest, base.asset("tri-r6-surface-detail-spec", "02-analysis", "analysis-measurements", A02 / "surface-detail-spec.json", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v6 planform arcs, 14-wedge cap, concave dish (user-stated)"))
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    # mark v5 as history
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v5", "tri-r6-reference-cad-v5-pdf", "tri-r6-cad-v5-script"):
            a["provenance"]["note"] = "v5 — superseded by tri-r6-reference-cad-v6 (convex-arc sides, no shoulder; 14-wedge cap); kept as history"

    # ---- claims ----
    claims = {c["id"]: c for c in manifest["claims"]}
    new_claims = [
        {
            "id": "tri-r6e-blade-planform-arcs", "category": "geometry", "confidence": "high",
            "statement": "叶片平面形：每条叶边是一条凸圆弧，半径 ≈1.37 R，圆心在该叶轴的垂线上、距盖心 0.92 R；两条弧在叶尖以 ≈90° 相交并以 ≈0.03 R 圆角软化；相邻两叶的弧在角平分线上相交于 r≈0.49 R，仅比盖圈（0.485 R）外 ≈0.005 R（≈0.2 mm @85 provisional），即缺口底几乎贴盖；每条弧穿过盖圈处夹角 ≈18°（锐角新月尖）。没有直边、没有肩角、没有径向缺口。依据：f0077/f0078 校正剪影逐叶描迹（blade-root-traces.png），4 条干净边圆弧拟合 rms 0.0006–0.0010 R，直线拟合 rms 0.011–0.015 R；用户 20:46 红圈截图与原话（过渡贴圆心、锐角、斜切线有弧度）。取代 tri-r6c-blade-planform-triangle 与 tri-r6d-shoulder-fillet。",
            "sourceAssetIds": ["tri-r6-frame-0077", "tri-r6-frame-0078", "tri-r6-frame-0148", "tri-r6-frame-0134", "tri-r6-user-screenshot-notch-redcircles", "tri-r6-user-instructions-2046", "tri-r6-zoom-blade-root-traces", "tri-r6-zoom-planform-v6-on-frames"],
        },
        {
            "id": "tri-r6e-notch-exposure", "category": "geometry", "confidence": "medium-high",
            "statement": "缺口处露盖：相邻两弧交点距盖圈 ≈0.005 R，剪影沿盖圈最多 ±5°；冠环与裙只透过新月形缝隙外露，不存在 36–71° 的宽扇形露盖（旧读数为暗色倒角低于剪影阈值所致）。暗缝仍为暗色，无亮色轴承环；缝宽未知。取代 tri-r6-seam 中“三个缺口处盖冠环与暗缝完整外露”的表述。",
            "sourceAssetIds": ["tri-r6-frame-0077", "tri-r6-frame-0078", "tri-r6-frame-0148", "tri-r6-zoom-notch-5x-f0077-f0075-f0038", "tri-r6-zoom-planform-v6-on-frames"],
        },
        {
            "id": "tri-r6e-cap-crown-14", "category": "geometry", "confidence": "medium-high",
            "statement": "盖 = 车削盘（0.82×盖径，范围 0.80–0.85）+ 冠环 14±1 楔 = 28 三角（尖端里外交替；f0077/f0078 校正展开图每 180° 约 14 齿，FFT 谐波 12–15、无 24）+ 盖裙两排各 14 片大鳞面（f0200/f0208 近侧约 7 片/180°）。冠环由盘缘向外向下倾斜：f0077 30° 倾斜俯视中远侧冠环被压缩到侧向宽度的 ≈1/3，说明冠环面背向相机；盘缘为盖的最高圈。取代 tri-r6-cap-crown（24±2）与 tri-r6-table-ratio（0.80）。",
            "sourceAssetIds": ["tri-r6-frame-0077", "tri-r6-frame-0078", "tri-r6-frame-0200", "tri-r6-frame-0208", "tri-r6-user-screenshot-cap-concave", "tri-r6-user-instructions-2046", "tri-r6-zoom-cap-ring-unwrap-f0077-hires", "tri-r6-zoom-cap-evidence-v6"],
        },
        {
            "id": "tri-r6e-cap-dish-user-stated", "category": "geometry", "confidence": "user-stated",
            "statement": "盘内为凹面拇指位：用户 2026-09-06 20:46 原话“明显是中间有一个凹下去的……有一个内凹的效果，是为了放拇指”。视频证据：f0204/f0208 盘面呈锥形/放射扇区明暗 + 同心车纹，说明是车削浅锥或浅碟，但凹/凸方向、斜度与深度无法由视频判定；按用户口述取“凹”，凹深 unknown（CAD v6 以 6° 占位 ≈0.04 R）。冠环斜向仍按 f0077 透视取“向外向下”（E1）；若用户所指“14 片有内凹效果”为冠环向内向下（E2），需用户在 CAD v6 Detail E 二选一。",
            "sourceAssetIds": ["tri-r6-user-instructions-2046", "tri-r6-user-screenshot-cap-concave", "tri-r6-frame-0077", "tri-r6-frame-0192", "tri-r6-frame-0200", "tri-r6-frame-0208", "tri-r6-zoom-cap-evidence-v6"],
        },
        {
            "id": "tri-r6e-unknowns", "category": "unknown", "confidence": "high",
            "statement": "未知项（无证据，不填数）：所有绝对 mm（除 85 mm provisional 标签）；盘凹面的锥/球形式、斜度与深度；凹坑深度/是否通孔；倒角带各平面角度；冠环楔面斜度；缝宽；轴承型号与尺寸；材质牌号；重量。取代 tri-r6-unknowns（其“冠环楔数 24±2”已由 tri-r6e-cap-crown-14 定为 14±1）。",
            "sourceAssetIds": ["tri-r6-user-instructions-2046", "tri-r6-frame-0077", "tri-r6-frame-0226"],
        },
    ]
    for c in new_claims:
        if c["id"] not in claims:
            manifest["claims"].append({**c, "stageId": "02-analysis", "sourceRegions": [], "recordedAt": NOW})
    supersessions = {
        "tri-r6c-blade-planform-triangle": "tri-r6e-blade-planform-arcs",
        "tri-r6d-shoulder-fillet": "tri-r6e-blade-planform-arcs",
        "tri-r6-seam": "tri-r6e-notch-exposure",
        "tri-r6-cap-crown": "tri-r6e-cap-crown-14",
        "tri-r6-table-ratio": "tri-r6e-cap-crown-14",
        "tri-r6-unknowns": "tri-r6e-unknowns",
    }
    for old, new in supersessions.items():
        c = claims[old]
        if c.get("state") != "superseded":
            c["state"] = "superseded"
            c["supersededBy"] = new
            c["supersededAt"] = NOW

    # claims doc
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    doc["supersessions"].update(supersessions)
    have = {c["id"] for c in doc["claims"]}
    for c in new_claims:
        if c["id"] not in have:
            doc["claims"].append({**c, "stageId": "02-analysis", "sourceRegions": [], "recordedAt": NOW})
    doc["openConflictsForUser"] = [x for x in doc["openConflictsForUser"] if x.get("topic") != "平盘/盖"] + [
        {"topic": "平盘/盖", "video": "0.82（0.80–0.85）", "priorInstruction": "0.70"},
        {"topic": "盖顶凹凸", "adopted": "E1 盘缘最高、冠环向外向下、盘内凹（用户口述）", "alternative": "E2 整顶内凹、冠环向内向下", "evidence": "f0077 远侧冠环被压缩 → E1；用户原话可读作 E1 或 E2"},
    ]
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    # ---- validations / state ----
    keep = {"planform-profile-measured", "open-conflicts-flagged", "claims-source-linked", "cap-facet-count"}
    s02["validations"] = [v for v in s02["validations"] if v["id"] not in keep] + [
        {"id": "claims-source-linked", "status": "pass", "detail": "rev-6 有效 claim 全部引用 Gate 01 关键帧或用户指令资产；本轮新增 5 条（e 系列），6 条旧 claim superseded（三角/肩角/冠环 24/平盘 0.80/缝/未知项）"},
        {"id": "planform-profile-measured", "status": "pass", "detail": "凸弧模型：4 条干净边圆弧拟合 rms ≤0.0010 R（直线 0.011–0.015 R）；R_s 1.367 R、圆心距 0.92 R；相邻弧交于盖圈外 0.005 R；CAD v6 由模型绘出并反投影叠加 f0077/f0078（planform-v6-on-frames.png）"},
        {"id": "cap-facet-count", "status": "pass", "detail": "冠环 14±1 楔（展开图计数 + FFT 谐波 12–15，无 24）；盖裙 14 鳞 ×2 排（f0200/f0208）"},
        {"id": "open-conflicts-flagged", "status": "pass", "detail": "待用户裁决：盖侧高、叶根凹坑、盖比例、平盘比例 0.82 vs 0.70、盖顶 E1/E2（盘内凹 vs 整顶内凹）"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 20:46 v6:")[0]
        + " | 20:46 v6: 用户红圈截图指出叶边接盖过渡应贴圆心且为锐角、斜切线有弧度；逐叶描迹证实叶边是 R≈1.37 R 的凸圆弧、直接扫到盖圈（无肩角），相邻弧交于盖圈外 0.2 mm；冠环 14 楔（24 作废）、盖裙 14 鳞 ×2 排；盘 0.82×盖，盘内凹面拇指位按用户口述登记（凹深未知，E1/E2 待裁决）。CAD v6 + 原帧叠加已出。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v6 — convex-arc blade sides hugging the cap (no shoulder), 14-wedge crown, 14-scale skirt, concave turned thumb dish (user-stated). Claims tri-r6e-* added; tri-r6c/tri-r6d/cap-crown/table-ratio/seam/unknowns superseded. Gate 01 rev-003 +3 key frames (192/200/208). User 2026-09-06 20:46 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added, "superseded": list(supersessions)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
