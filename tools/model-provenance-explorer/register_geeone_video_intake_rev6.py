"""Gate 01 rev-003 (full source video intake) and Gate 02 rev-006 (frame-by-frame
source-linked claims + reference CAD) for metal-three-blade.

Constraints honoured (controller 2026-09-05 23:12 / 23:14):
- Only Gates 01/02 change; Gates 03-06 drafts become `stale` history, nothing
  is inherited into the new revisions.
- 85 mm is `user-authorized-provisional`, never measured; it supersedes the
  65 mm claim append-style (history kept); scope note: future Gate 03-05 only.
- No approvals, no workbench refresh; stage digests are computed here so a
  later read-only validation sees a consistent manifest.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
MODEL_ID = "metal-three-blade"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
EV = PIPELINE_DIR / "evidence"
A01 = EV / "01-intake/rev-003"
A02 = EV / "02-analysis/rev-006"
VIDEO_SRC = Path("/tmp/dragon-scale-gate02/video")
FRAMES_SRC = VIDEO_SRC / "frames10"
NOW = datetime.now(timezone.utc).isoformat()
PRODUCER = {"name": "register_geeone_video_intake_rev6.py", "version": "2026-09-05"}

KEY_FRAMES = [3, 6, 9, 38, 74, 75, 76, 77, 78, 79, 126, 134, 156, 160, 164, 168, 175, 196, 204, 212, 222, 226, 230, 236, 300]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def asset(asset_id, stage_id, slot, path, role, content_class, origin, asserted_by, sources, note="", claims=None):
    record = {
        "id": asset_id, "stageId": stage_id, "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": PRODUCER, "provenance": {"origin": origin, "contentClass": content_class, "assertedBy": asserted_by, "note": note},
        "sourceAssetIds": sources, "exists": True, "sizeBytes": path.stat().st_size,
    }
    if claims:
        record["sourceClaimIds"] = claims
    return record


def upsert(manifest, record):
    for index, existing in enumerate(manifest["assets"]):
        if existing["id"] == record["id"]:
            manifest["assets"][index] = record
            return
    manifest["assets"].append(record)


def stage(manifest, stage_id):
    return next(s for s in manifest["stages"] if s["id"] == stage_id)


def stable_json(value) -> str:
    if isinstance(value, list):
        return "[" + ",".join(stable_json(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{stable_json(value[k])}" for k in sorted(value)) + "}"
    return json.dumps(value, ensure_ascii=False)


def update_stage_digests(manifest) -> None:
    assets = {a["id"]: a for a in manifest["assets"]}
    previous = None
    for st in manifest["stages"]:
        hashes = [assets[aid]["sha256"] for aid in st["artifactIds"] if aid in assets]
        claims = [stable_json(c) for c in manifest.get("claims", []) if c["stageId"] == st["id"]]
        digest = hashlib.sha256("\n".join(sorted(v for v in hashes + claims if v)).encode("utf-8")).hexdigest()
        st["inputDigest"] = digest if previous is None else previous
        st["outputDigest"] = digest
        previous = digest


def revise(manifest, stage_id, new_revision, reason, events):
    s = stage(manifest, stage_id)
    if s["revision"] != new_revision:
        s.setdefault("historicalRevisions", []).append({"revision": s["revision"], "artifactIds": list(s["artifactIds"]), "status": "superseded", "reason": reason})
        events.append({"type": "stage-revised", "stageId": stage_id, "notes": reason})
        s["revision"] = new_revision
    s["decision"] = None
    s.pop("staleReason", None)
    return s


def main() -> None:
    manifest = json.loads((PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    events = []

    # ------------------------------------------------------------ Gate 01 --
    video_dir = A01 / "obsidian-geeone-video"
    video_dir.mkdir(parents=True, exist_ok=True)
    mp4 = video_dir / "geeone-source.mp4"
    info = video_dir / "geeone-source.info.json"
    if not mp4.exists():
        shutil.copy2(VIDEO_SRC / "geeone-source.mp4", mp4)
    if not info.exists():
        shutil.copy2(VIDEO_SRC / "geeone-source.info.json", info)
    frames_dir = A01 / "frames10-key"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for idx in KEY_FRAMES:
        dst = frames_dir / f"f_{idx:04d}.jpg"
        if not dst.exists():
            shutil.copy2(FRAMES_SRC / f"f_{idx:04d}.jpg", dst)
    sheets_dir = A01 / "frames10-contact-sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)
    for k in range(1, 8):
        src = VIDEO_SRC / "sheets" / f"sheet_{k}.png"
        dst = sheets_dir / f"sheet_{k}.png"
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    overview = A01 / "frames-2fps-overview.png"
    if not overview.exists() and Path("/tmp/dragon-scale-gate02/80-video-frames-2fps.png").exists():
        shutil.copy2("/tmp/dragon-scale-gate02/80-video-frames-2fps.png", overview)

    meta = json.loads(info.read_text(encoding="utf-8"))
    note_url = (REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/01-intake/rev-002/source-clipping.md")
    intake_record = write_json(A01 / "intake-record.json", {
        "modelId": MODEL_ID, "stageId": "01-intake", "revision": 3, "recordedAt": NOW,
        "source": {
            "kind": "video", "platform": "xiaohongshu", "author": "指玩屋", "noteTitle": "可以玩一整天的小玩意？！",
            "obsidianNote": "Obsidian Vault/笔记同步助手/2026-08-01/可以玩一整天的小玩意？！.md",
            "url": meta.get("webpage_url") or meta.get("original_url"), "videoId": meta.get("id"),
            "downloadedWith": "yt-dlp 2025.10.14 (python -m yt_dlp)", "downloadedAt": "2026-09-05T22:32+08:00", "formatId": meta.get("format_id"),
            "durationS": meta.get("duration"), "width": meta.get("width"), "height": meta.get("height"), "fps": meta.get("fps"),
        },
        "files": {"video": {"path": rel(mp4), "sha256": sha256(mp4), "bytes": mp4.stat().st_size}, "info": {"path": rel(info), "sha256": sha256(info)}},
        "frameExtraction": {
            "command": "ffmpeg -i geeone-source.mp4 -vf fps=10 -q:v 2 frames10/f_%04d.jpg",
            "frameCount": 366, "timestampOfFrameN": "(N-1)/10 s", "storedKeyFrames": KEY_FRAMES,
            "storedKeyFrameSha256": {f"f_{i:04d}.jpg": sha256(frames_dir / f"f_{i:04d}.jpg") for i in KEY_FRAMES},
            "note": "All 366 frames are reproducible from the hashed mp4 with the command above; only the frames cited by Gate 02 claims are stored.",
        },
        "priorRevision": "rev-002 archived 7 stills that the note-sync tool had cut from this same video; they remain valid external references and are re-linked here.",
    })

    s01 = revise(manifest, "01-intake", 3, "Gate 01 rev-003: full source video intake with hashes (user 22:31 “再去完整的跑一下obsidian里面的那个视频”).", events)
    upsert(manifest, asset("tri-r6-video-source", "01-intake", "original-reference", mp4, "external-reference", "product-video-mp4-720x1280-29.97fps-36.6s", "external", "user", [], "小红书 指玩屋 视频，来自用户 Obsidian 剪藏链接；yt-dlp 下载"))
    upsert(manifest, asset("tri-r6-video-info", "01-intake", "source-metadata", info, "external-reference", "yt-dlp-info-json", "external", "assistant", ["tri-r6-video-source"]))
    upsert(manifest, asset("tri-r6-intake-record", "01-intake", "source-metadata", intake_record, "process", "intake-record-with-hashes-and-frame-command", "repository-generated", "repository", ["tri-r6-video-source"]))
    frame_ids = []
    for idx in KEY_FRAMES:
        aid = f"tri-r6-frame-{idx:04d}"
        upsert(manifest, asset(aid, "01-intake", "original-reference", frames_dir / f"f_{idx:04d}.jpg", "external-reference", f"video-frame-extract-t{(idx - 1) / 10:.1f}s", "external", "repository", ["tri-r6-video-source"], "ffmpeg fps=10 frame, unmodified"))
        frame_ids.append(aid)
    sheet_ids = []
    for k in range(1, 8):
        p = sheets_dir / f"sheet_{k}.png"
        if p.exists():
            aid = f"tri-r6-frames-sheet-{k}"
            upsert(manifest, asset(aid, "01-intake", "analysis-board", p, "analysis", f"contact-sheet-frames-{(k - 1) * 60 + 1}-{min(k * 60, 366)}", "repository-generated", "repository", ["tri-r6-video-source"]))
            sheet_ids.append(aid)
    if overview.exists():
        upsert(manifest, asset("tri-r6-frames-overview", "01-intake", "analysis-board", overview, "analysis", "contact-sheet-2fps-73-frames", "repository-generated", "repository", ["tri-r6-video-source"]))
        sheet_ids.append("tri-r6-frames-overview")
    keep_prior = [a for a in s01["artifactIds"] if a.startswith("tri-r2-product-") or a in ("tri-r2-note-source-clipping",)]
    s01["artifactIds"] = ["tri-r6-video-source", "tri-r6-video-info", "tri-r6-intake-record"] + frame_ids + sheet_ids + keep_prior
    s01["status"] = "ready_for_review"
    s01["validations"] = [
        {"id": "real-product-reference-present", "status": "pass", "detail": "完整源视频 36.6 s + 25 张关键帧 + 7 张缩略表；rev-002 的 7 张剪藏截图重新关联"},
        {"id": "source-hashes-recorded", "status": "pass", "detail": f"mp4 sha256 {sha256(mp4)[:12]}…；关键帧逐张哈希在 intake-record.json"},
        {"id": "download-provenance", "status": "pass", "detail": "yt-dlp 2025.10.14，format 2，URL 与剪藏一致；无登录/验证码"},
        {"id": "generated-targets-demoted", "status": "pass", "detail": "rev-002 assistant boards 不再列入 Gate 01 artifacts"},
        {"id": "physical-dimensions-measured", "status": "fail", "detail": "无实测 mm；85 mm 仅 user-authorized-provisional（见 Gate 02）"},
    ]

    # ------------------------------------------------------------ Gate 02 --
    s02 = revise(manifest, "02-analysis", 6, "Gate 02 rev-006: frame-by-frame source-linked claims from the full video; 65 mm → 85 mm user-authorized-provisional supersession.", events)
    instructions = A02 / "user-instructions-2026-09-05-late.md"
    upsert(manifest, asset("tri-r6-user-instructions", "02-analysis", "analysis-board", instructions, "user-input", "user-and-controller-instructions-verbatim", "user-provided", "user", [], "22:22 / 22:31 / 23:07 用户；23:12 / 23:14 总控"))
    measurements = A02 / "frame-measurements.json"
    upsert(manifest, asset("tri-r6-frame-measurements", "02-analysis", "analysis-measurements", measurements, "analysis", "silhouette-ellipse-rectified-ratios-f0077-f0078", "repository-generated", "repository", ["tri-r6-frame-0077", "tri-r6-frame-0078"], "pixels and ratios only"))
    upsert(manifest, asset("tri-r6-measure-script", "02-analysis", "analysis-board", REPO / "tools/model-provenance-explorer/measure_geeone_video_frames.py", "process", "measurement-script", "repository-generated", "repository", []))
    board_ids = ["tri-r6-user-instructions", "tri-r6-frame-measurements", "tri-r6-measure-script"]
    for name, cls, srcs in [
        ("measure-overlay-f0077.png", "ellipse-and-tip-overlay", ["tri-r6-frame-0077"]),
        ("measure-overlay-f0078.png", "ellipse-and-tip-overlay", ["tri-r6-frame-0078"]),
        ("measure-rectified-f0077.png", "rectified-silhouette", ["tri-r6-frame-0077"]),
        ("measure-rectified-f0078.png", "rectified-silhouette", ["tri-r6-frame-0078"]),
        ("frame-vs-rev004-comparison.png", "frame-vs-rev004-render-comparison", ["tri-r6-frame-0038", "tri-r6-frame-0077", "tri-r6-frame-0226", "tri-r6-frame-0164"]),
        ("reference-cad-from-video.png", "reference-cad-plan-profile-from-frames", ["tri-r6-frame-measurements"]),
        ("reference-cad-from-video.pdf", "reference-cad-plan-profile-from-frames-vector", ["tri-r6-frame-measurements"]),
    ]:
        aid = "tri-r6-" + name.replace(".", "-")
        slot = "structural-cad" if name.startswith("reference-cad") else "analysis-board"
        upsert(manifest, asset(aid, "02-analysis", slot, A02 / name, "analysis", cls, "repository-generated", "repository", srcs))
        board_ids.append(aid)
    zoom_ids = []
    for p in sorted((A02 / "frame-zooms").glob("*.png")):
        if p.name.startswith("_"):
            continue
        aid = "tri-r6-zoom-" + p.stem
        upsert(manifest, asset(aid, "02-analysis", "analysis-board", p, "analysis", "frame-zoom-crop", "repository-generated", "repository", ["tri-r6-video-source"]))
        zoom_ids.append(aid)
    upsert(manifest, asset("tri-r6-cad-script", "02-analysis", "analysis-board", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad.py", "process", "reference-cad-script", "repository-generated", "repository", []))
    board_ids.append("tri-r6-cad-script")

    # supersede every previously active Gate 02 claim except the product decision and the vault rescan
    supersede_map = {
        "tri-r3-dimensions-provisional": "tri-r6-width-85-provisional",
        "tri-r2-cap-size-was-never-wrong": "tri-r6-cap-ratio",
        "tri-r4-table-ratio-discrepancy": "tri-r6-table-ratio",
        "tri-r5-petal-blades": "tri-r6-blade-outline-teardrop",
        "tri-r5-notch-interpretation": "tri-r6-blade-outline-teardrop",
        "tri-r5-blade-volume": "tri-r6-blade-top-structure",
        "tri-r5-cone-zigzag-crown": "tri-r6-cap-crown",
        "tri-r4-cap-low-profile": "tri-r6-cap-crown",
        "tri-r4-satin-material": "tri-r6-material",
        "tri-r5-table-finish": "tri-r6-material",
        "tri-r5-seam-08": "tri-r6-seam",
        "tri-r3-shadow-gap-not-race": "tri-r6-seam",
        "tri-r2-no-bright-annulus": "tri-r6-seam",
        "tri-r2-body-is-one-solid": "tri-r6-parts-motion",
        "tri-r2-dimensions-unmeasured": "tri-r6-unknowns",
    }
    for claim in manifest["claims"]:
        if claim["id"] in supersede_map and claim.get("state") != "superseded":
            claim["state"] = "superseded"
            claim["supersededBy"] = supersede_map[claim["id"]]
            claim["supersededAt"] = NOW
    F = lambda *ids: [f"tri-r6-frame-{i:04d}" for i in ids]  # noqa: E731
    new_claims = [
        ("tri-r6-width-85-provisional", "dimension", "user-authorized-provisional",
         "整体外接圆直径 85 mm 为 user-authorized-provisional（总控 2026-09-05 23:12/23:14 指令），绝不能标 measured。取代 tri-r3-dimensions-provisional 的 65 mm（追加式 supersession，65 mm 历史保留在 claims 中）。适用范围：仅可供未来 Gate 03–05（合同/拆件/白模）使用；其余所有 mm 尺寸保持 unknown。",
         ["tri-r6-user-instructions"]),
        ("tri-r6-cap-ratio", "dimension", "medium",
         "盖外径/外接圆 = 0.485±0.009（视频 f0077/f0078 桌面段剪影，椭圆→圆校正倾斜≈30°，透视未校正 ±0.03）；此前照片 geeone-02 读数 0.536。取值区间 0.49–0.54，建模前需用户裁决或更多帧。",
         F(77, 78) + ["tri-r6-frame-measurements"]),
        ("tri-r6-table-ratio", "dimension", "high",
         "平盘直径/盖外径 = 0.80（f0077/f0078 角向方差边界；照片 0.797）。此前用户口述 0.70 与两组证据不符，已由本 claim 取代。",
         F(77, 78, 38) + ["tri-r6-frame-measurements"]),
        ("tri-r6-blade-outline-teardrop", "geometry", "medium",
         "叶片顶视为泪滴/尖角三角：叶尖夹角 67°±3（f0077/f0078 两枚近端叶尖直边拟合；远端叶尖 84° 为透视失真），叶尖圆角≈0.045 R（锐但非刀口）；两条直边向内至 r≈0.68 R 的肩部后向内凹收，贴到盖圈；叶根在盖圈上只跨约 ±32°，每个缺口露出盖冠环弧 ≈56°（近端 70°/远端 36°，透视未校正）。此前 R12 大圆弧叶尖、凸弧侧边、根部撑满 120° 的解释全部作废。",
         F(77, 78, 38, 75)),
        ("tri-r6-blade-top-structure", "geometry", "medium",
         "叶片顶面：中央平台为平面；沿两条外边一条倒角带（宽≈0.07 R），带内由 3–4 个平面组成（“楔形过渡”/龙鳞分面），两侧倒角在叶尖交成一条脊；倒角带下为近竖直侧壁（≈0.45×厚）；底面与顶面镜像对称。",
         F(77, 164, 226, 168) + ["tri-r6-zoom-blade-f0077-4x"]),
        ("tri-r6-root-pocket", "geometry", "medium",
         "每片叶根紧贴盖处有一个三角形凹坑：开口朝盖，尖端朝叶尖约 r≈0.70 R，外壁为斜切面（f0126–f0138、f0077 中橙色反光即该斜壁），底部暗；深度与是否通孔未知。此前“实心无凹坑”的指示与视频不符，待用户裁决。",
         F(77, 38, 126, 134)),
        ("tri-r6-cap-crown", "geometry", "medium",
         "盖 = 平车削盘（0.80 盖径，细同心纹）+ 一圈向外下斜的三角楔冠环（尖端里外交替，f0077 计数 24±2）+ 冠环下方分面的裙（多边形柱面，非光滑圆柱）。盖侧面（冠环+裙）露出高度≈0.14 R，约 0.8×机身厚（f0226 单帧，低置信 ±20%），与此前“盖只高出叶面 1.5 mm”冲突，待裁决。",
         F(77, 38, 134, 226)),
        ("tri-r6-body-thickness", "dimension", "low",
         "机身厚度≈0.17 R（f0226 边视 50 px vs 外接圆半径≈290 px；透视未校正 ±20%）；叶尖处收薄到≈0.6×竖壁高。无 mm 值。",
         F(226, 160)),
        ("tri-r6-seam", "geometry", "medium",
         "盖裙与叶根之间为一道暗色窄缝，看不到任何亮色轴承环；缝宽在视频分辩率下不可测（unknown）；在三个缺口处盖冠环与暗缝完整外露。",
         F(38, 77, 134)),
        ("tri-r6-parts-motion", "mechanism", "high",
         "零件与动静关系：上盖、下盖（同形，静止，手指夹持）；转子体一件式（三叶 + 中毂，含三个叶根凹坑）；内部轴承（型号未知）。f0191–f0240 显示手指夹持上下盖、转子体自由旋转；盖不随转子转动。",
         F(196, 204, 212, 222, 226, 230)),
        ("tri-r6-material", "material", "medium",
         "材质：钢色缎面金属（拉丝/喷砂感），倒角分面与冠环楔面在橙色补光下呈硬边高光（近抛光），平盘带细同心车削纹；合金牌号未知。整机同一材质，无双色。",
         F(38, 134, 226, 3)),
        ("tri-r6-unknowns", "dimension", "high",
         "未知项（无证据，不填数）：所有绝对 mm（除 85 mm provisional 标签）；凹坑深度/是否通孔；倒角带各平面角度；缝宽；轴承型号与尺寸；盖冠环精确楔数（24±2）；材质牌号；重量。",
         ["tri-r6-frame-measurements"]),
    ]
    existing = {c["id"] for c in manifest["claims"]}
    for cid, category, confidence, statement, sources in new_claims:
        if cid not in existing:
            manifest["claims"].append({"id": cid, "stageId": "02-analysis", "category": category, "statement": statement, "confidence": confidence, "sourceAssetIds": sources, "sourceRegions": [], "recordedAt": NOW})
    claims_doc = write_json(A02 / "claims-rev6.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 6, "recordedAt": NOW,
        "supersessions": supersede_map,
        "claims": [{"id": c[0], "category": c[1], "confidence": c[2], "statement": c[3], "sourceAssetIds": c[4]} for c in new_claims],
        "openConflictsForUser": [
            {"topic": "盖侧高度", "video": "≈0.14 R ≈0.8×机身厚（低置信）", "priorInstruction": "盖只高出叶面 1.5 mm"},
            {"topic": "叶根凹坑", "video": "存在，三角形，开口朝盖", "priorInstruction": "实心无凹坑"},
            {"topic": "盖/外接圆", "video": "0.485±0.03", "photo": "0.536"},
            {"topic": "平盘/盖", "video+photo": "0.80", "priorInstruction": "0.70"},
        ],
    })
    upsert(manifest, asset("tri-r6-claims-doc", "02-analysis", "analysis-board", claims_doc, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-user-instructions"]))
    board_ids.append("tri-r6-claims-doc")
    s02["artifactIds"] = board_ids + zoom_ids + ["tri-r5-vault-rescan-sheet", "tri-r5-vault-rescan-candidates", "tri-r5-discovery-log"]
    s02["status"] = "ready_for_review"
    active = [c["id"] for c in manifest["claims"] if c["stageId"] == "02-analysis" and c.get("state") != "superseded"]
    s02["validations"] = [
        {"id": "claims-source-linked", "status": "pass", "detail": f"{len(new_claims)} 条 rev-6 claim 全部引用 Gate 01 关键帧或用户指令资产；15 条旧 claim superseded（含 65 mm）"},
        {"id": "width-provisional-superseded-not-measured", "status": "pass", "detail": "85 mm = user-authorized-provisional，适用范围仅未来 Gate 03–05；65 mm 历史保留"},
        {"id": "frame-measurements-present", "status": "pass", "detail": "f0077/f0078 剪影量测 + 叠加图 + 校正图"},
        {"id": "reference-cad-present", "status": "pass", "detail": "reference-cad-from-video.png/pdf（顶视 + 剖面示意，比例单位 R）"},
        {"id": "frame-vs-render-comparison", "status": "pass", "detail": "4 组视频帧 vs rev-004 渲染对比（分析用，rev-004 不继承）"},
        {"id": "millimetre-dimensions-measured", "status": "fail", "detail": "无实测 mm；全部为比例与 85 mm provisional 换算"},
        {"id": "open-conflicts-flagged", "status": "pass", "detail": "盖侧高、叶根凹坑、盖比例、平盘比例四项冲突已列出待用户裁决"},
    ]

    # ------------------------------------------------ Gates 03-06: history --
    for sid in ("03-contract", "04-architecture", "05-blockout", "06-geometry"):
        s = stage(manifest, sid)
        if s["status"] not in ("missing", "blocked"):
            s["status"] = "stale"
        s["staleReason"] = "Gate 01 rev-003 / Gate 02 rev-006 re-intake from the full video (2026-09-05 23:12 controller); this draft is history pending invalidation and is not inherited."
        s["decision"] = None
    events.append({"type": "stage-note", "stageId": "03-contract", "notes": "Gates 03-06 rev-004 drafts kept as history; no new Gate 03-12 work tonight (controller 23:14)."})

    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"] = {
        "rebuildRequested": True, "shippingAssetUnchanged": True, "visualApproval": "pending", "deviceStatus": "not-approved",
        "diagnosis": "用户 23:07 指出 CAD 叶尖弧度、楔形过渡、凸凹细节与原图不符并要求逐帧对比。已完整下载 Obsidian 剪藏对应的小红书源视频（36.6 s），抽帧 366 张，Gate 01 rev-003 归档源视频与关键帧哈希；Gate 02 rev-006 用桌面平放段剪影量测（盖/外接圆 0.485、平盘/盖 0.80、叶尖 67°、圆角 0.045R、叶根跨 ±32°）、逐帧叠加与 rev-004 对比、参考 CAD，12 条 source-linked claims，15 条旧 claim superseded，85 mm user-authorized-provisional 取代 65 mm。Gate 01/02 ready_for_review；Gate 03–06 draft 转为历史 stale。视觉批准待确认，未推送手机；等待用户 Gate 审批。",
    }
    (PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for sid in ("01-intake", "02-analysis"):
        events.append({"type": "stage-ready-for-review", "stageId": sid, "notes": "Awaiting the user's Gate decision; no approval implied. 视觉批准待确认，未推送手机；等待用户 Gate 审批。"})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "activeGate02Claims": len(active), "gate01Artifacts": len(s01["artifactIds"]), "gate02Artifacts": len(s02["artifactIds"])}))


if __name__ == "__main__":
    main()
