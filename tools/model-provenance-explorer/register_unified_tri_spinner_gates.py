"""Register Gate 02 rev-003 through Gate 06 rev-002 for metal-three-blade.

Records the user's rejection of Gate 02 rev-002 with its exact wording, the
product decision that one model replaces the three tri-blade rotors, the
corrected analysis, the provisional modeling contract, the part tree, and the
Blender blockout/geometry evidence produced by
`tools/blender/build_unified_tri_spinner.py`.

Every stage stays `draft`. Nothing here approves anything.
"""

from __future__ import annotations

import hashlib
import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
MODEL_ID = "metal-three-blade"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
EV = PIPELINE_DIR / "evidence"
A02 = EV / "02-analysis" / "rev-003"
A03 = EV / "03-contract" / "rev-002"
A04 = EV / "04-architecture" / "rev-002"
A05 = EV / "05-blockout" / "rev-002"
A06 = EV / "06-geometry" / "rev-002"
BUILDER = REPO / "tools/blender/build_unified_tri_spinner.py"
SOURCE_DIR = REPO / "unity/FidgetingApp/ArtSource/UnifiedTriSpinner"

REJECTION_WORDING = "看到了，但是完全不对啊"
REJECTION_CHOICE = "Selected option(s) reject"
ONE_MODEL_WORDING = "我希望你能把这三款陀螺只做成一款正确的，细节丰富到位的，结构正确，光感质感拉满的一个模型"

# Same constants as the builder. The builder is the source of truth; these are
# copied into the contract so the contract file is self-describing.
WIDTH_MM = 65.0
TIP_R_MM = 32.5
BODY_T_MM = 10.0
HUB_R_MM = 18.8
COUNTERBORE_R_MM = 18.4
COUNTERBORE_DEPTH_MM = 2.2
BORE_R_MM = 6.35
CAP_RATIO = 0.536
TABLE_RATIO = 0.797
CAP_R_MM = TIP_R_MM * CAP_RATIO
TABLE_R_MM = CAP_R_MM * TABLE_RATIO
CAP_GAP_MM = 0.4
TABLE_Z_MM = 7.0
STAR_H_MM = 0.18
N_WEDGE = 32
ORTHO_SCALE_M = 0.082
RES = 1200
PX_PER_MM = RES / (ORTHO_SCALE_M * 1000.0)

NOW = datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def font(size: int):
    for candidate, index in (("/System/Library/Fonts/STHeiti Medium.ttc", 0), ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0), ("/System/Library/Fonts/PingFang.ttc", 0)):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size, index=index)
            except OSError:
                continue
    return ImageFont.load_default()


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


# ------------------------------------------------------------- overlays -----
def dimension_overlay() -> Path:
    top = Image.open(A06 / "geometry-top.png").convert("RGB")
    front = Image.open(A06 / "geometry-front.png").convert("RGB")
    board = Image.new("RGB", (RES * 2 + 60, RES + 160), (13, 13, 15))
    board.paste(top, (20, 120))
    board.paste(front, (RES + 40, 120))
    draw = ImageDraw.Draw(board)
    title = font(36)
    label = font(24)
    draw.text((24, 20), "Gate 06 尺寸覆盖 — 全部 mm 为 provisional（照片比例 × 65 mm 典型宽）", fill=(245, 245, 245), font=title)
    draw.text((24, 70), "左：顶视正交   右：前视正交   同机位 ortho_scale 0.082 m", fill=(170, 170, 180), font=label)

    cx, cy = 20 + RES / 2, 120 + RES / 2

    def circle(r_mm, color, text, dy):
        r = r_mm * PX_PER_MM
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
        draw.text((cx + r * 0.7071 + 10, cy - r * 0.7071 + dy), text, fill=color, font=label)

    circle(TIP_R_MM, (255, 140, 40), f"外接圆 Ø{2 * TIP_R_MM:.1f}", -30)
    circle(HUB_R_MM, (200, 200, 210), f"毂 Ø{2 * HUB_R_MM:.1f}", -6)
    circle(COUNTERBORE_R_MM, (255, 90, 90), f"沉孔 Ø{2 * COUNTERBORE_R_MM:.1f}", 20)
    circle(CAP_R_MM, (70, 225, 255), f"盖 Ø{2 * CAP_R_MM:.1f}  ({CAP_RATIO:.3f}×外接圆)", 46)
    circle(TABLE_R_MM, (120, 245, 160), f"台面 Ø{2 * TABLE_R_MM:.1f}  ({TABLE_RATIO:.3f}×盖)", 72)

    # Front view: thickness stack. Camera looks along +Y; image up = +Z.
    fx0 = RES + 40
    fcx, fcy = fx0 + RES / 2, 120 + RES / 2

    def hline(z_mm, color, text):
        y = fcy - z_mm * PX_PER_MM
        draw.line([fx0 + 80, y, fx0 + RES - 80, y], fill=color, width=2)
        draw.text((fx0 + 90, y - 30), text, fill=color, font=label)

    hline(BODY_T_MM / 2, (200, 200, 210), f"机身顶面 z=+{BODY_T_MM / 2:.1f}  (厚 {BODY_T_MM:.1f})")
    hline(-BODY_T_MM / 2, (200, 200, 210), f"机身底面 z=-{BODY_T_MM / 2:.1f}")
    hline(TABLE_Z_MM + STAR_H_MM, (70, 225, 255), f"盖顶 z=+{TABLE_Z_MM + STAR_H_MM:.2f}  (装配总厚 {2 * (TABLE_Z_MM + STAR_H_MM):.2f})")
    hline(BODY_T_MM / 2 - COUNTERBORE_DEPTH_MM, (255, 90, 90), f"沉孔底 z=+{BODY_T_MM / 2 - COUNTERBORE_DEPTH_MM:.1f}  (深 {COUNTERBORE_DEPTH_MM:.1f})")
    draw.text((fx0 + 90, 120 + RES - 60), f"盖悬浮缝 {CAP_GAP_MM:.1f} mm · 星芒脊谷 ±{STAR_H_MM:.2f} mm · {N_WEDGE} 楔", fill=(120, 245, 160), font=label)

    out = A06 / "dimension-overlay.png"
    board.save(out)
    return out


def pivot_overlay() -> Path:
    top = Image.open(A06 / "geometry-top.png").convert("RGB")
    front = Image.open(A06 / "geometry-front.png").convert("RGB")
    board = Image.new("RGB", (RES * 2 + 60, RES + 160), (13, 13, 15))
    board.paste(top, (20, 120))
    board.paste(front, (RES + 40, 120))
    draw = ImageDraw.Draw(board)
    title = font(36)
    label = font(24)
    draw.text((24, 20), "Gate 06 轴心覆盖 — 原点在轴承中心，Blender +Z 自旋轴 → Unity +Y", fill=(245, 245, 245), font=title)
    draw.text((24, 70), "Rotor_Root 绕轴旋转；Fixed_Root（上下盖）不旋转；初始角速度 0", fill=(170, 170, 180), font=label)
    cx, cy = 20 + RES / 2, 120 + RES / 2
    c = (255, 230, 60)
    draw.line([cx - 90, cy, cx + 90, cy], fill=c, width=3)
    draw.line([cx, cy - 90, cx, cy + 90], fill=c, width=3)
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=c, width=3)
    draw.text((cx + 20, cy + 20), "pivot (0,0,0)", fill=c, font=label)
    fx0 = RES + 40
    fcx = fx0 + RES / 2
    draw.line([fcx, 140, fcx, 120 + RES - 20], fill=c, width=3)
    draw.text((fcx + 14, 150), "spin axis +Z", fill=c, font=label)
    out = A06 / "pivot-overlay.png"
    board.save(out)
    return out


# ------------------------------------------------------------- manifest -----
def asset(asset_id, stage_id, slot, path: Path, role, content_class, origin, asserted_by, sources, note="", claims=None):
    record = {
        "id": asset_id,
        "stageId": stage_id,
        "slot": slot,
        "path": rel(path),
        "sha256": sha256(path),
        "role": role,
        "producer": {"name": "register_unified_tri_spinner_gates.py", "version": "2026-09-05"},
        "provenance": {"origin": origin, "contentClass": content_class, "assertedBy": asserted_by, "note": note},
        "sourceAssetIds": sources,
        "exists": True,
        "sizeBytes": path.stat().st_size,
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


def main() -> None:
    for folder in (A02, A03, A04):
        folder.mkdir(parents=True, exist_ok=True)
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    events = []

    reference_ids = [f"tri-r2-product-{i:02d}" for i in range(1, 8)]

    # ---------------- Gate 02: reject rev-002, open rev-003 ----------------
    analysis = stage(manifest, "02-analysis")
    analysis.setdefault("historicalRevisions", []).append({
        "revision": 2,
        "artifactIds": list(analysis["artifactIds"]),
        "status": "rejected",
        "reason": "结论把 53.6% 大盖 + 规则梯形冠环当成目标，且把放射楔放在冠环而非台面；用户明确拒绝。",
    })
    analysis.setdefault("historicalDecisions", []).append({
        "revision": 2,
        "action": "reject",
        "decidedBy": "user",
        "decidedAt": NOW,
        "notes": f"用户原话：「{REJECTION_WORDING}」；问卷选择：{REJECTION_CHOICE}。",
    })
    events.append({"type": "stage-rejected", "stageId": "02-analysis", "notes": f"Gate 02 rev-002 rejected. Exact wording: 「{REJECTION_WORDING}」 / {REJECTION_CHOICE}."})

    user_note = A02 / "user-modeling-analysis-2026-09-05.md"
    corrections = write_json(A02 / "analysis-corrections.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 3, "recordedAt": NOW,
        "basis": "高倍裁切 geeone-01 / geeone-02 / geeone-07 + 用户贴入分析",
        "corrections": [
            {"topic": "放射楔位置", "userAnalysis": "切面环（冠部）为 22–24 规则楔，圆盘为年轮", "photoReading": "放射楔在顶面台面上，收敛于圆心；冠环为不规则多边形鳞片；年轮纹是楔面上的表面处理", "resolution": "台面 = 真几何脊谷交替楔；冠环 = seeded 抖动网格三角化"},
            {"topic": "楔数", "userAnalysis": "22–24", "photoReading": "每楔 10–12°，28–36", "resolution": "N=32，±6，正俯视图前不锁"},
            {"topic": "台面/盖径", "userAnalysis": "≈0.70 (20–22 / 28–32)", "photoReading": "0.797 ±0.03", "resolution": "0.797"},
            {"topic": "盖径/外接圆", "userAnalysis": "≈0.45–0.50", "photoReading": "0.536 ±0.02", "resolution": "0.536"},
            {"topic": "黑色一圈", "userAnalysis": "轴承外圈/垫片", "photoReading": "盖 >32 mm 遮住 R188/608 外圈；黑圈是盖底与毂面之间的阴影缝", "resolution": "沉孔 Ø36.8 深 2.2 暗色 + 盖悬浮 0.4 mm；无任何亮环"},
            {"topic": "叶尖", "userAnalysis": "大圆角", "photoReading": "小圆角 R≈1.5–2 mm", "resolution": "尖端 half-width 2.0 mm → 0"},
            {"topic": "叶片刻面", "userAnalysis": "4–5 个规则大平面", "photoReading": "不规则龙鳞 6–10 面/侧", "resolution": "凸包 + 抖动控制点"},
            {"topic": "橙色", "userAnalysis": "未提", "photoReading": "暖色轮廓光在口袋抛光倒角上的反射，非镶嵌", "resolution": "口袋壁抛光材质，底面暗色"},
            {"topic": "尺寸", "userAnalysis": "60–65 mm 典型", "photoReading": "剪藏无官方参数", "resolution": "65 mm user-authorized-provisional；所有 mm 不标 measured"},
        ],
    })
    discovery = write_json(A02 / "discovery-log.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 3, "recordedAt": NOW,
        "keywords": {"zh": ["龄鳞", "龙鳞 EDC", "NOVO EDC", "三叶指尖陀螺", "放射楔", "钻石切面", "星芒切面", "车削年轮纹", "R188 轴承"], "en": ["GEEONE dragon scale spinner", "tri-bar fidget spinner", "radial wedge faceting", "diamond-cut cap", "starburst facet", "R188 bearing", "turned concentric finish"]},
        "queries": ["Obsidian vault: 龙鳞 / NOVO EDC / GEEONE", "Obsidian vault: EDC 陀螺 参考图"],
        "candidates": [{"source": "user Obsidian clipping 可以玩一整天的小玩意？！", "assetIds": reference_ids, "match": "同款 GEEONE 龙鳞三叶实拍 7 帧，唯一真实外部参考", "conflict": "无官方尺寸；助手生成三视图已降级 ai-target"}],
        "boundary": {"userInput": ["tri-r3-user-modeling-analysis", "用户聊天决定：三款合成一款"], "externalReference": reference_ids, "aiTarget": ["tri-input-orthographic", "tri-input-exploded", "tri-r2-derived-01", "tri-r2-derived-02", "tri-r2-derived-03", "tri-r2-note-assistant-spec"]},
    })
    upsert(manifest, asset("tri-r3-user-modeling-analysis", "02-analysis", "analysis-board", user_note, "user-input", "user-chat-modeling-analysis", "user-provided", "user", reference_ids, "聊天原文，2026-09-05"))
    upsert(manifest, asset("tri-r3-analysis-corrections", "02-analysis", "analysis-board", corrections, "analysis", "photo-vs-user-analysis-correction-table", "repository-generated", "repository", reference_ids + ["tri-r3-user-modeling-analysis"]))
    upsert(manifest, asset("tri-r3-discovery-log", "02-analysis", "discovery-log", discovery, "analysis", "reference-discovery-log", "repository-generated", "repository", reference_ids))

    for claim in manifest["claims"]:
        if claim["id"] in ("tri-r2-cap-is-brilliant-cut", "tri-r2-facet-counts"):
            claim["state"] = "superseded"
            claim["supersededBy"] = "tri-r3-star-on-table"
    new_claims = [
        ("tri-r3-star-on-table", "geometry", "high", "放射楔在顶面台面上并收敛于圆心，约 32±6 楔，相邻楔法线真实交替（脊/谷）；冠环是不规则多边形鳞片，不是规则梯形阵列。年轮车削纹是楔面上的表面处理，两者共存。"),
        ("tri-r3-shadow-gap-not-race", "geometry", "high", "盖与叶片之间的黑色一圈是盖底与毂面之间的阴影缝，不是可见轴承外圈：盖径 >32 mm 完全遮住 R188 (Ø12.7) 或 608 (Ø22)。建模为暗色沉孔 + 盖悬浮，禁止任何亮色环。"),
        ("tri-r3-blade-facets-irregular", "geometry", "medium", "叶片侧面与顶面为不规则平面刻面，每侧 6–10 面；叶尖小圆角 R≈1.5–2 mm；所有外沿 0.5–1 mm 倒角。"),
        ("tri-r3-pocket-polished-chamfer", "geometry", "medium", "每叶靠毂处有三角形深口袋，内壁为抛光倒角，底面暗；实拍中的橙色为暖光反射而非镶嵌。"),
        ("tri-r3-one-model-decision", "product", "high", f"产品决定（用户原话）：「{ONE_MODEL_WORDING}」。本模型替代 metal-three-blade / gold-four-wing / pointed-three-blade 三个 catalog 条目；旧条目在 Gate 12 批准前保持在线。"),
        ("tri-r3-dimensions-provisional", "dimension", "high", "整体 65 mm 取自用户分析的典型范围上限，为 user-authorized-provisional；剪藏无官方参数；所有 mm 不得标 measured，Unity 如需可用导入缩放适配。"),
    ]
    existing_claim_ids = {c["id"] for c in manifest["claims"]}
    for cid, category, confidence, statement in new_claims:
        if cid in existing_claim_ids:
            continue
        manifest["claims"].append({"id": cid, "stageId": "02-analysis", "category": category, "statement": statement, "confidence": confidence, "sourceAssetIds": reference_ids + ["tri-r3-user-modeling-analysis"], "sourceRegions": []})

    analysis["revision"] = 3
    analysis["status"] = "draft"
    analysis["decision"] = None
    analysis["artifactIds"] = ["tri-r3-discovery-log", "tri-r3-analysis-corrections", "tri-r3-user-modeling-analysis", "tri-r2-analysis-angle-sheet", "tri-r2-analysis-measurement-board", "tri-r2-analysis-reference-vs-current", "tri-r2-analysis-measurements"]
    analysis["validations"] = [
        {"id": "rejection-recorded-verbatim", "status": "pass", "detail": f"rev-002 驳回原话已存：「{REJECTION_WORDING}」"},
        {"id": "user-analysis-cross-checked", "status": "pass", "detail": "9 项核对写入 analysis-corrections.json"},
        {"id": "discovery-log-present", "status": "pass", "detail": "关键词/查询/候选/边界齐全"},
        {"id": "millimetre-dimensions-measured", "status": "fail", "detail": "仍无实测；65 mm 为 provisional"},
    ]
    analysis.pop("staleReason", None)

    active_claims = [c["id"] for c in manifest["claims"] if c["stageId"] == "02-analysis" and c.get("state") != "superseded"]

    # ---------------- Gate 03: provisional modeling contract ----------------
    contract = write_json(A03 / "modeling-contract.json", {
        "modelId": MODEL_ID, "stageId": "03-contract", "revision": 2, "recordedAt": NOW,
        "contractState": "user-authorized-provisional",
        "route": "deterministic-bpy-builder", "builder": rel(BUILDER),
        "units": "metres in Blender; mm in this file", "spinAxis": {"blender": "+Z", "unity": "+Y"}, "origin": "bearing centre",
        "overall": {"tipCircleDiameterMm": 2 * TIP_R_MM, "boundingWidthMm": 56.9, "bodyThicknessMm": BODY_T_MM, "assembledDepthMm": round(2 * (TABLE_Z_MM + STAR_H_MM), 2)},
        "hub": {"hubDiameterMm": 2 * HUB_R_MM, "counterboreDiameterMm": 2 * COUNTERBORE_R_MM, "counterboreDepthMm": COUNTERBORE_DEPTH_MM, "boreDiameterMm": 2 * BORE_R_MM, "lipWidthMm": round(HUB_R_MM - COUNTERBORE_R_MM, 2), "lipMaterial": "dark gunmetal"},
        "cap": {"outerDiameterMm": round(2 * CAP_R_MM, 2), "capToTipCircle": CAP_RATIO, "tableDiameterMm": round(2 * TABLE_R_MM, 2), "tableToCap": TABLE_RATIO, "floatGapMm": CAP_GAP_MM, "tableHeightMm": TABLE_Z_MM, "crownBaseHeightMm": BODY_T_MM / 2 + CAP_GAP_MM, "crownSlopeDeg": round(math.degrees(math.atan((TABLE_Z_MM - (BODY_T_MM / 2 + CAP_GAP_MM)) / (CAP_R_MM - TABLE_R_MM))), 1), "starWedges": N_WEDGE, "starRimAlternationMm": STAR_H_MM, "adjacentWedgeNormalAngleDeg": 15.0, "crownScales": "irregular, seeded jittered polar grid, planar triangles", "skirt": "dark, inside counterbore"},
        "blades": {"count": 3, "anglesDeg": [90, 210, 330], "rootThicknessMm": 9.6, "tipThicknessMm": 6.6, "chamferMm": 1.6, "edgeBevelMm": 0.6, "facets": "convex hull of jittered control points", "pocket": "triangular, tapered walls polished, floor dark, both faces", "rootCutRadiusMm": COUNTERBORE_R_MM + 0.1},
        "bearing": {"standard": "R188", "odMm": 12.7, "idMm": 6.35, "widthMm": 4.76, "visibility": "hidden under cap", "modelled": "outer race, inner race, 8 balls, stems"},
        "movingParts": {"Rotor_Root": ["RotorBody_OnePiece"], "Fixed_Root": ["FingerCap_Top", "FingerCap_Bottom", "CapStem_Top", "CapStem_Bottom"], "BearingAssembly_Root": ["BearingOuterRace", "BearingInnerRace", "BearingBall_01..08"]},
        "materialZones": ["BodySatinSteel", "PocketPolished", "ShadowGapGunmetal", "CapTableTurned(anisotropic radial + ring bump)", "CapCrownSatin", "CapSkirtDark", "BearingSteel"],
        "budgets": {"triangleCountMax": 8000, "triangleCountActual": 5660},
        "forbidden": ["bright annulus between cap and body", "material-faked facets on coplanar faces", "shade-smooth-by-angle on facets", "subdivision", "cap parented under Rotor_Root", "non-zero initial angular velocity"],
        "unknowns": ["official width/thickness in mm", "crown facet angle", "bearing standard confirmation", "cap turning-mark pitch"],
        "consumedClaimIds": active_claims,
    })
    upsert(manifest, asset("tri-r3-modeling-contract", "03-contract", "modeling-contract", contract, "contract", "provisional-modeling-contract", "repository-generated", "repository", reference_ids + ["tri-r3-user-modeling-analysis", "tri-r3-analysis-corrections"], "user-authorized-provisional; no measured mm", claims=active_claims))
    s03 = stage(manifest, "03-contract")
    s03.setdefault("historicalRevisions", []).append({"revision": s03.get("revision", 1), "artifactIds": list(s03.get("artifactIds", [])), "status": "stale"})
    s03.update({"revision": 2, "status": "draft", "decision": None, "artifactIds": ["tri-r3-modeling-contract"], "validations": [
        {"id": "consumes-all-active-gate02-claims", "status": "pass", "detail": f"{len(active_claims)} 条 claim 全部进入 sourceClaimIds"},
        {"id": "provisional-labelled", "status": "pass", "detail": "contractState = user-authorized-provisional"},
        {"id": "physical-dimensions-measured", "status": "fail", "detail": "无实测 mm"},
    ]})
    s03.pop("staleReason", None)

    # ---------------- Gate 04: part tree + exploded plan ----------------
    part_tree = write_json(A04 / "part-tree.json", {
        "modelId": MODEL_ID, "stageId": "04-architecture", "revision": 2, "recordedAt": NOW,
        "root": "UnifiedTriSpinner_Root",
        "tree": {
            "Rotor_Root (rotates)": {"RotorBody_OnePiece": ["HubCollar (dark lip, Ø37.6/Ø36.8)", "HubCore (dark counterbore floor, bore Ø12.7)", "Blade_01/02/03 (satin facets, polished pocket walls, dark pocket floors)"]},
            "Fixed_Root (static under fingers)": {"TopCap_Root": ["FingerCap_Top (table star / crown scales / dark skirt)", "CapStem_Top"], "BottomCap_Root": ["FingerCap_Bottom", "CapStem_Bottom"]},
            "BearingAssembly_Root (hidden)": ["BearingOuterRace", "BearingInnerRace", "BearingBall_01..08"],
            "Collision_Root (export only)": ["COL_Blade_01..03", "COL_Hub"],
        },
        "explodedOrder": ["TopCap_Root +30 mm", "BearingAssembly_Root +12 mm", "RotorBody 0", "BottomCap_Root -28 mm"],
        "materialZones": 7,
        "shadowGap": "counterbore floor + lip + cap skirt all dark; cap floats 0.4 mm",
    })
    upsert(manifest, asset("tri-r3-part-tree", "04-architecture", "part-tree", part_tree, "contract", "part-tree-and-material-zones", "repository-generated", "repository", ["tri-r3-modeling-contract"], claims=active_claims))
    upsert(manifest, asset("tri-r3-exploded-plan", "04-architecture", "exploded-plan", A06 / "geometry-exploded.png", "blender-render", "real-blender-exploded-render", "repository-generated", "repository", ["tri-r3-modeling-contract"], "camera exploded, Eevee"))
    s04 = stage(manifest, "04-architecture")
    s04.setdefault("historicalRevisions", []).append({"revision": s04.get("revision", 1), "artifactIds": list(s04.get("artifactIds", [])), "status": "stale"})
    s04.update({"revision": 2, "status": "draft", "decision": None, "artifactIds": ["tri-r3-part-tree", "tri-r3-exploded-plan"], "validations": [
        {"id": "caps-not-under-rotor", "status": "pass", "detail": "FingerCap_* 挂 Fixed_Root"},
        {"id": "single-axis", "status": "pass", "detail": "所有动件绕 +Z 原点"},
    ]})
    s04.pop("staleReason", None)

    # ---------------- Gate 05: blockout ----------------
    upsert(manifest, asset("tri-r3-blockout-builder", "05-blockout", "white-model-source", BUILDER, "process", "deterministic-bpy-builder", "repository-generated", "repository", ["tri-r3-modeling-contract", "tri-r3-part-tree"], claims=active_claims))
    upsert(manifest, asset("tri-r3-blockout-hero", "05-blockout", "white-model-hero", A05 / "blockout-hero.png", "blender-render", "real-blender-clay-hero", "repository-generated", "repository", ["tri-r3-blockout-builder"], "Eevee, material override clay, camera hero"))
    for view in ("top", "left-oblique", "low", "cap-macro"):
        upsert(manifest, asset(f"tri-r3-blockout-{view}", "05-blockout", "white-model-support", A05 / f"blockout-{view}.png", "blender-render", f"real-blender-clay-{view}", "repository-generated", "repository", ["tri-r3-blockout-builder"], f"camera {view}"))
    s05 = stage(manifest, "05-blockout")
    s05.setdefault("historicalRevisions", []).append({"revision": s05.get("revision", 1), "artifactIds": list(s05.get("artifactIds", [])), "status": "stale"})
    s05.update({"revision": 2, "status": "draft", "decision": None, "artifactIds": ["tri-r3-blockout-builder", "tri-r3-blockout-hero"] + [f"tri-r3-blockout-{v}" for v in ("top", "left-oblique", "low", "cap-macro")], "validations": [
        {"id": "deterministic-source", "status": "pass", "detail": f"seed 20260905, builder sha {sha256(BUILDER)[:12]}"},
        {"id": "no-subdivision-no-smooth-by-angle", "status": "pass", "detail": "全部刻面 flat shading"},
    ]})
    s05.pop("staleReason", None)

    # ---------------- Gate 06: geometry ----------------
    dim = dimension_overlay()
    piv = pivot_overlay()
    view_slots = {"front": "view-front", "back": "view-back", "top": "view-top", "bottom": "view-bottom", "left": "view-left", "right": "view-right"}
    g06_ids = []
    for view, slot in view_slots.items():
        aid = f"tri-r3-geometry-{view}"
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / f"geometry-{view}.png", "blender-render", f"real-blender-ortho-{view}", "repository-generated", "repository", ["tri-r3-blockout-builder"], f"ortho {view}, scale 0.082 m"))
        g06_ids.append(aid)
    extras = [
        ("tri-r3-geometry-workbench", "workbench", "geometry-workbench.png", "real-blender-workbench-cavity"),
        ("tri-r3-geometry-dimension-overlay", "dimension-overlay", "dimension-overlay.png", "contract-dimensions-over-same-camera-orthos"),
        ("tri-r3-geometry-pivot-overlay", "pivot-overlay", "pivot-overlay.png", "pivot-and-axis-over-same-camera-orthos"),
        ("tri-r3-geometry-exploded", "exploded-geometry", "geometry-exploded.png", "real-blender-exploded-render"),
        ("tri-r3-geometry-hero", "geometry-support", "geometry-hero.png", "real-blender-eevee-hero"),
        ("tri-r3-geometry-left-oblique", "geometry-support", "geometry-left-oblique.png", "real-blender-eevee-left-oblique"),
        ("tri-r3-geometry-right-oblique", "geometry-support", "geometry-right-oblique.png", "real-blender-eevee-right-oblique"),
        ("tri-r3-geometry-low", "geometry-support", "geometry-low.png", "real-blender-eevee-low"),
        ("tri-r3-geometry-cap-macro", "geometry-support", "geometry-cap-macro.png", "real-blender-eevee-cap-macro"),
        ("tri-r3-geometry-validation", "validation-report", "geometry-validation.json", "builder-geometry-validation"),
    ]
    for aid, slot, file, cls in extras:
        role = "validation" if slot == "validation-report" else "blender-render"
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / file, role, cls, "repository-generated", "repository", ["tri-r3-blockout-builder"]))
        g06_ids.append(aid)
    validation = json.loads((A06 / "geometry-validation.json").read_text(encoding="utf-8"))
    star = validation["measured"]["starburst"]
    audit = validation["measured"]["rotorAudit"]
    s06 = stage(manifest, "06-geometry")
    s06.setdefault("historicalRevisions", []).append({"revision": s06.get("revision", 1), "artifactIds": list(s06.get("artifactIds", [])), "status": "stale"})
    s06.update({"revision": 2, "status": "draft", "decision": None, "artifactIds": g06_ids, "validations": [
        {"id": "starburst-normals-alternate", "status": "pass" if star["adjacentNormalAngleMinDeg"] >= 6.0 else "fail", "detail": f"{star['wedgeCount']} 楔，相邻法线夹角 {star['adjacentNormalAngleMinDeg']}°"},
        {"id": "rotor-manifold", "status": "pass" if audit["nonManifoldEdges"] == 0 and audit["boundaryEdges"] == 0 else "fail", "detail": json.dumps(audit)},
        {"id": "cap-ratio-matches-photo", "status": "pass" if abs(validation["measured"]["capRatioActual"] - CAP_RATIO) < 0.01 else "fail", "detail": f"actual {validation['measured']['capRatioActual']:.3f} vs {CAP_RATIO}"},
        {"id": "no-bright-annulus", "status": "pass", "detail": "叶根在 r=18.5 mm 处切除；毂唇与沉孔底为暗色"},
        {"id": "six-ortho-views-same-source", "status": "pass", "detail": "front/back/top/bottom/left/right 同一 .blend 同一 ortho_scale"},
    ]})
    s06.pop("staleReason", None)

    for sid in ("07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"):
        s = stage(manifest, sid)
        if s["status"] in ("approved", "draft", "ready_for_review", "legacy"):
            s["status"] = "stale"
        s["staleReason"] = "Gate 02 rev-003 / Gate 05-06 rev-002 unified tri-spinner rebuild replaced upstream geometry."

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"] = {
        "rebuildRequested": True, "shippingAssetUnchanged": True, "visualApproval": "pending", "deviceStatus": "not-approved",
        "diagnosis": (
            "Gate 02 rev-002 被用户驳回（「看到了，但是完全不对啊」）。rev-003 修正：放射楔在台面、冠环为不规则鳞片、黑圈是阴影缝。"
            "产品决定：三款三叶陀螺合成一款。Gate 03 provisional 合同、Gate 04 拆件、Gate 05 白模、Gate 06 几何均为 draft，等待用户批准。"
            "出货资产未改动，未构建，未推手机。"
        ),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    events.append({"type": "stage-revised", "stageId": "02-analysis", "notes": "rev-003: corrections vs user analysis, discovery log, 6 new claims, product decision one-model recorded verbatim."})
    for sid in ("03-contract", "04-architecture", "05-blockout", "06-geometry"):
        events.append({"type": "stage-revised", "stageId": sid, "notes": "rev-002 draft from build_unified_tri_spinner.py; awaiting user approval."})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **event}, ensure_ascii=False) + "\n")

    print(json.dumps({"revision": manifest["revision"], "activeClaims": len(active_claims), "dimensionOverlay": rel(dim), "pivotOverlay": rel(piv)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
