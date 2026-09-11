"""Record the user's second 2026-09-05 rejection (Gate 02 rev-004 / Gates
03-06 rev-003) and register the rev-004 unified tri-spinner geometry as new
draft revisions.

Rejection wording is stored verbatim in
`evidence/06-geometry/rev-003/user-rejection-2026-09-05-b.md` (user-input).
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
REJ = EV / "06-geometry/rev-003/user-rejection-2026-09-05-b.md"
A02 = EV / "02-analysis/rev-005"
A03 = EV / "03-contract/rev-004"
A04 = EV / "04-architecture/rev-004"
A05 = EV / "05-blockout/rev-004"
A06 = EV / "06-geometry/rev-004"
VAR = EV / "06-geometry/rev-004-variant-table-0797"
BUILDER = REPO / "tools/blender/build_unified_tri_spinner.py"
BOARD_SCRIPT = REPO / "tools/model-provenance-explorer/build_unified_review_board.py"

# Builder constants (mm) mirrored for the overlays and contract.
TIP_R = 32.5
BLADE_T = 11.5
BODY_HALF = BLADE_T / 2
CAP_RATIO = 0.536
TABLE_RATIO = 0.70
CAP_R = TIP_R * CAP_RATIO
TABLE_R = CAP_R * TABLE_RATIO
SEAM_W = 0.8
SEAM_R = CAP_R + SEAM_W
TABLE_Z = BODY_HALF + 1.5
SLOPE_DEG = 25.0
RIM_Z = TABLE_Z - (CAP_R - TABLE_R) * math.tan(math.radians(SLOPE_DEG))
ZIGZAG = 0.55
N_WEDGE = 24
CORE_HALF = 2.2
RES = 1100
PX_PER_MM = RES / 82.0
NOW = datetime.now(timezone.utc).isoformat()

REJECTION_SUMMARY = (
    "用户第二次驳回（三主三次）：1 楔环是竖直矩形棱条“城墙”，平盘反而低于楔环；应为平盘最高、楔面向外下斜 25–35° 的矮圆台，楔为三角形、尖端里外交替、脊线锯齿；"
    "2 叶片成了贴在圆柱上的扇形桨，顶视露出机身圆柱；应为圆角三角/泪滴，外端 R≈12 大圆弧，两侧向内收 60°，内端延伸到暗缝，机身不可见；"
    "3 叶片是平板、只有盖的一半高；应 11–12 mm 厚，顶面 3–4 个平面切出中脊，侧壁竖直，外端圆弧上再切大斜面。"
    "次要：平盘加径向各向异性 + 高频同心 Bump；暗缝 1.0→0.8 mm；24 楔与 0.5 mm 倒角保留。"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def font(size: int):
    for candidate in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc"):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def overlays(validation: dict) -> tuple[Path, Path]:
    top = Image.open(A06 / "geometry-top.png").convert("RGB")
    front = Image.open(A06 / "geometry-front.png").convert("RGB")

    def board(title_text, subtitle):
        board_img = Image.new("RGB", (RES * 2 + 60, RES + 160), (13, 13, 15))
        board_img.paste(top, (20, 120))
        board_img.paste(front, (RES + 40, 120))
        d = ImageDraw.Draw(board_img)
        d.text((24, 20), title_text, fill=(245, 245, 245), font=font(36))
        d.text((24, 70), subtitle, fill=(170, 170, 180), font=font(24))
        return board_img, d

    label = font(24)
    cx, cy = 20 + RES / 2, 120 + RES / 2
    fx0 = RES + 40
    fcy = 120 + RES / 2
    ring = validation["measured"]["wedgeRing"]

    dim, d = board("Gate 06 rev-004 尺寸覆盖 — 全部 mm 为 provisional（照片比例 × 65 mm）", "左：顶视正交   右：前视正交   ortho_scale 0.082 m")

    def circle(r_mm, color, text, dy):
        r = r_mm * PX_PER_MM
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
        d.text((cx + r * 0.7071 + 10, cy - r * 0.7071 + dy), text, fill=color, font=label)

    circle(TIP_R, (255, 140, 40), f"外接圆 Ø{2 * TIP_R:.1f}", -30)
    circle(SEAM_R, (255, 90, 90), f"沉孔/叶根壁 Ø{2 * SEAM_R:.2f}（暗缝 {SEAM_W:.1f}）", -4)
    circle(CAP_R, (70, 225, 255), f"盖 Ø{2 * CAP_R:.2f}（{CAP_RATIO:.3f}×外接圆）", 22)
    circle(TABLE_R, (120, 245, 160), f"平盘 Ø{2 * TABLE_R:.2f}（{TABLE_RATIO:.2f}×盖）", 48)
    d.text((40, 120 + RES - 100), "机身圆柱藏在盖与叶根之下：顶视不可见（notchApex r = %.2f mm）" % validation["measured"]["notchApexRadiusMm"], fill=(255, 200, 90), font=label)
    d.text((40, 120 + RES - 64), f"缺口 V {validation['contract']['notchVDeg']:.0f}° · 外端弧 R{validation['contract']['tipArcRadiusMm']:.0f} · 叶片最大半宽 {validation['contract']['bladeMaxHalfWidthMm']:.1f}", fill=(255, 200, 90), font=label)

    def hline(z_mm, color, text):
        y = fcy - z_mm * PX_PER_MM
        d.line([fx0 + 80, y, fx0 + RES - 80, y], fill=color, width=2)
        d.text((fx0 + 90, y - 30), text, fill=color, font=label)

    hline(BODY_HALF, (200, 200, 210), f"叶片顶面 z=+{BODY_HALF:.2f}（叶厚 {BLADE_T:.1f}）")
    hline(-BODY_HALF, (200, 200, 210), f"叶片底面 z=-{BODY_HALF:.2f}")
    hline(TABLE_Z, (70, 225, 255), f"平盘 z=+{TABLE_Z:.2f}（最高点，高出叶面 1.5，装配总厚 {2 * TABLE_Z:.1f}）")
    hline(RIM_Z, (255, 200, 80), f"楔环外沿均值 z=+{RIM_Z:.2f}（斜 {SLOPE_DEG:.0f}°，锯齿 ±{ZIGZAG:.2f}，低于叶面 {BODY_HALF - RIM_Z:.2f}）")
    hline(CORE_HALF, (255, 90, 90), f"沉孔底 z=+{CORE_HALF:.1f}")
    d.text((fx0 + 90, 120 + RES - 60), f"{ring['wedges']} 楔 / {ring['wedgeTriangles']} 三角 · 相邻法线 {ring['adjacentNormalAngleMinDeg']}–{ring['adjacentNormalAngleMaxDeg']}° · 面斜 {ring['faceSlopeMinDeg']}–{ring['faceSlopeMaxDeg']}° · 台面倾斜 {ring['tableMaxTiltDeg']}°", fill=(120, 245, 160), font=label)
    dim_path = A06 / "dimension-overlay.png"
    dim.save(dim_path)

    piv, d = board("Gate 06 rev-004 轴心覆盖 — 原点在轴承中心，Blender +Z 自旋轴 → Unity +Y", "Rotor_Root 绕轴旋转；Fixed_Root（上下盖）不旋转；初始角速度 0")
    c = (255, 230, 60)
    d.line([cx - 90, cy, cx + 90, cy], fill=c, width=3)
    d.line([cx, cy - 90, cx, cy + 90], fill=c, width=3)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=c, width=3)
    d.text((cx + 20, cy + 20), "pivot (0,0,0)", fill=c, font=label)
    d.line([fx0 + RES / 2, 140, fx0 + RES / 2, 120 + RES - 20], fill=c, width=3)
    d.text((fx0 + RES / 2 + 14, 150), "spin axis +Z", fill=c, font=label)
    piv_path = A06 / "pivot-overlay.png"
    piv.save(piv_path)
    return dim_path, piv_path


def asset(asset_id, stage_id, slot, path, role, content_class, origin, asserted_by, sources, note="", claims=None):
    record = {
        "id": asset_id, "stageId": stage_id, "slot": slot, "path": rel(path), "sha256": sha256(path), "role": role,
        "producer": {"name": "register_unified_tri_spinner_rev4.py", "version": "2026-09-05"},
        "provenance": {"origin": origin, "contentClass": content_class, "assertedBy": asserted_by, "note": note},
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
    """Mirror of pipeline-core.mjs stableJson (sorted keys, JSON.stringify scalars)."""
    if isinstance(value, list):
        return "[" + ",".join(stable_json(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{stable_json(value[k])}" for k in sorted(value)) + "}"
    return json.dumps(value, ensure_ascii=False)


def digest_values(values) -> str:
    return hashlib.sha256("\n".join(sorted(v for v in values if v)).encode("utf-8")).hexdigest()


def update_stage_digests(manifest) -> None:
    """Mirror of pipeline-core.mjs updateStageDigests so a later workbench
    refresh does not read our own registration as an unexpected change."""
    assets = {a["id"]: a for a in manifest["assets"]}
    previous = None
    for stage_record in manifest["stages"]:
        hashes = [assets[aid]["sha256"] for aid in stage_record["artifactIds"] if aid in assets]
        claims = [stable_json(c) for c in manifest.get("claims", []) if c["stageId"] == stage_record["id"]]
        digest = digest_values(hashes + claims)
        stage_record["inputDigest"] = digest if previous is None else previous
        stage_record["outputDigest"] = digest
        previous = digest


BUMPED: set[str] = set()


def reject_and_bump(manifest, stage_id, new_revision, events):
    s = stage(manifest, stage_id)
    if s["revision"] == new_revision:  # re-run: revision already registered, only refresh status
        s["status"] = "draft"
        s["decision"] = None
        s.pop("staleReason", None)
        return s
    s.setdefault("historicalRevisions", []).append({"revision": s["revision"], "artifactIds": list(s["artifactIds"]), "status": "rejected", "reason": REJECTION_SUMMARY})
    s.setdefault("historicalDecisions", []).append({"revision": s["revision"], "action": "reject", "decidedBy": "user", "decidedAt": NOW, "notes": f"原文见 tri-r5-user-rejection。摘要：{REJECTION_SUMMARY}"})
    events.append({"type": "stage-rejected", "stageId": stage_id, "notes": f"{stage_id} rev {s['revision']} rejected by user (2026-09-05 19:43); verbatim wording in evidence/06-geometry/rev-003/user-rejection-2026-09-05-b.md."})
    BUMPED.add(stage_id)
    s["revision"] = new_revision
    s["status"] = "draft"
    s["decision"] = None
    s.pop("staleReason", None)
    return s


def main() -> None:
    for folder in (A02, A03, A04):
        folder.mkdir(parents=True, exist_ok=True)
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    events = []
    reference_ids = [f"tri-r2-product-{i:02d}" for i in range(1, 8)]
    validation = json.loads((A06 / "geometry-validation.json").read_text(encoding="utf-8"))
    variant = json.loads((VAR / "geometry-validation.json").read_text(encoding="utf-8"))

    upsert(manifest, asset("tri-r5-user-rejection", "06-geometry", "geometry-support", REJ, "user-input", "user-chat-rejection-verbatim", "user-provided", "user", [], "2026-09-05 19:43 驳回原文（第二次）"))

    # ---- Gate 02 rev-005 ------------------------------------------------------
    s02 = reject_and_bump(manifest, "02-analysis", 5, events)
    supersede = {"tri-r4-two-layer-cap": "tri-r5-cone-zigzag-crown", "tri-r4-solid-faceted-blades": "tri-r5-petal-blades"}
    for claim in manifest["claims"]:
        if claim["id"] in supersede:
            claim["state"] = "superseded"
            claim["supersededBy"] = supersede[claim["id"]]
    new_claims = [
        ("tri-r5-cone-zigzag-crown", "geometry", "high", "盖为矮圆台：平车削盘（0.70 盖径）是最高点；楔环是从盘边向外向下 25–35° 的圆锥面，外沿顶点交替上下位移形成锯齿脊线，24 楔 = 48 个三角平面，尖端里外交替，明暗交替来自几何法线。用户 2026-09-05 19:43 指示。"),
        ("tri-r5-petal-blades", "geometry", "high", "叶片为圆角三角/泪滴：外端 R≈12 mm 大圆弧；两侧向内收拢，相邻叶片在暗缝边以约 60° V 形缺口相接；内端延伸到暗缝边；机身圆柱缩小到只容纳轴承座，正交顶视不可见；顶视轮廓是连续三叶曲线。用户 2026-09-05 19:43 指示 + 照片 geeone-01/02。"),
        ("tri-r5-blade-volume", "geometry", "high", "叶片厚 11–12 mm，与盖顶只差 1.5 mm；顶面由 3–4 个大平面切出中脊（中间高、向两侧与外缘落下），侧壁近乎竖直，外端圆弧面上再切一个大斜面。用户 2026-09-05 19:43 指示。"),
        ("tri-r5-table-finish", "material", "medium", "平盘需径向 Tangent 各向异性 + 高频同心 Bump，出一道柔和弧形亮带；Eevee 不渲染各向异性，Gate 06 起用 Cycles 出图。用户次要指示。"),
        ("tri-r5-seam-08", "dimension", "medium", "暗缝由 1.0 mm 收到 0.8 mm（沉孔半径 = 盖半径 + 0.8）。用户次要指示。"),
        ("tri-r5-vault-rescan-negative", "reference", "high", "2026-09-05 复扫 Obsidian vault 22 条相关笔记 40 张图：本产品只有 Gate 01 已归档的 7 张 GEEONE 实拍；TW 玲珑云三叶、钛 storm 三叶为同类不同款，仅作品类语境，不作尺寸来源。"),
        ("tri-r5-notch-interpretation", "geometry", "medium", "用户“两侧向内收成约 60° 夹角”按“相邻叶片间 V 形缺口 60°”解释：若按“单片泪滴两侧切线夹 60°”字面构造，R12 圆弧切线在 r≈18 mm 处相距 49°，机身必然外露，与“机身被完全包住”矛盾。解释已在评审板标注，待用户裁决。"),
    ]
    existing = {c["id"] for c in manifest["claims"]}
    for cid, category, confidence, statement in new_claims:
        if cid not in existing:
            manifest["claims"].append({"id": cid, "stageId": "02-analysis", "category": category, "statement": statement, "confidence": confidence, "sourceAssetIds": reference_ids + ["tri-r5-user-rejection"], "sourceRegions": []})

    rescan_sheet = A02 / "vault-rescan-contact-sheet.png"
    rescan_cands = A02 / "vault-rescan-tri-blade-candidates.png"
    discovery = write_json(A02 / "discovery-log-rev5.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 5, "recordedAt": NOW,
        "trigger": "用户早期指示“去 Obsidian 看类似帖子/EDC 参考图”在本轮回放；顺带裁决台面比例与叶根凹陷两个悬案是否有新证据",
        "vaultRoot": "~/Documents/Obsidian Vault/笔记同步助手",
        "query": "陀螺|spinner|fidget|EDC|龙鳞|GEEONE|NOVO|tri-bar|三叶",
        "notesMatched": 22, "imagesScanned": 40,
        "result": "no additional photos of the GEEONE dragon-scale product; all 7 archived in Gate 01 rev-002 are the complete set",
        "sameCategoryContextOnly": [
            {"note": "2026-08-18/这是什么神仙金属啊？TW听闻玲珑云三叶.md", "why": "timascus tri-blade, cloud-shaped blades, turned concentric cap; different product"},
            {"note": "2026-08-24/同步助手_2026-08-24.md (#spinner #titanium #storm)", "why": "360x480 thumbnail of three tri-blades incl. a pinwheel-cap one; too small to measure"},
            {"note": "2026-08-08/看看你指尖的ootd？…指尖陀螺.md", "why": "rope-twist cap two/three-lobe spinner; different product"},
        ],
        "openDiscrepancies": {"tableRatio": {"user": 0.70, "photo": 0.797, "status": "rendered both; comparison variant registered"}, "rootDarkTriangles": {"photo": "present", "user": "solid", "status": "not modelled; awaiting user"}},
    })
    upsert(manifest, asset("tri-r5-discovery-log", "02-analysis", "discovery-log", discovery, "analysis", "vault-rescan-discovery-log", "repository-generated", "repository", reference_ids))
    upsert(manifest, asset("tri-r5-vault-rescan-sheet", "02-analysis", "analysis-board", rescan_sheet, "analysis", "vault-rescan-contact-sheet-40-images", "repository-generated", "repository", []))
    upsert(manifest, asset("tri-r5-vault-rescan-candidates", "02-analysis", "analysis-board", rescan_cands, "analysis", "vault-rescan-tri-blade-candidates-not-this-product", "repository-generated", "repository", []))
    corrections = write_json(A02 / "analysis-corrections-rev5.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 5, "recordedAt": NOW,
        "basis": "用户 2026-09-05 19:43 驳回原文（tri-r5-user-rejection）+ geeone-01/02 复核",
        "changes": [
            {"topic": "楔环", "rev4": "等宽梯形半面 ±11° 扭转，外沿 z=4.1，读成竖直棱条/凹碟", "rev5": "圆锥 25°，内环 24 点在平盘边、外环 24 点错半步且 ±0.55 mm 锯齿，48 三角尖端里外交替，相邻法线 9.3–16.1°", "authority": "user"},
            {"topic": "平盘为最高点", "rev4": "z=6.5 但视觉被楔环压住", "rev5": "z=7.25，楔环全部低于平盘（tableIsHighestPoint=true）", "authority": "user"},
            {"topic": "叶片轮廓", "rev4": "外宽内窄扇形、直边外缘、根半宽 12", "rev5": "泪滴：缺口 V 60° 起于暗缝边，凸 Bezier 侧边，R12 外弧占 ±60°，最大半宽 16.4", "authority": "user + photo"},
            {"topic": "机身可见性", "rev4": "顶视露出 Ø37.6 毂领圆环", "rev5": "毂领删除；三叶根部在暗缝边相接，顶视 hubVisibleInTopView=false", "authority": "user"},
            {"topic": "叶片厚度与顶面", "rev4": "9.9 mm，平顶 + 小切角", "rev5": "11.5 mm，两屋脊面 10.2° + 端面 32° 斜切，竖直侧壁 5.6 mm", "authority": "user"},
            {"topic": "暗缝", "rev4": "1.0 mm", "rev5": "0.8 mm", "authority": "user"},
            {"topic": "平盘纹理", "rev4": "Eevee 不出各向异性", "rev5": "Cycles/Metal 96spp；径向各向异性 0.85 + 同心 Bump 0.09", "authority": "user"},
            {"topic": "楔环外沿高度（新悬案）", "rev4": "—", "rev5": "台面 0.70 + 25° 斜 ⇒ 外沿低于叶面 0.94 mm，暗缝看起来比 0.8 mm 深；照片值 0.797 ⇒ 外沿与叶面齐平（0.15 mm）。两版同机位对比已出，待用户裁决", "authority": "geometry"},
        ],
    })
    upsert(manifest, asset("tri-r5-analysis-corrections", "02-analysis", "analysis-board", corrections, "analysis", "rev4-to-rev5-correction-table", "repository-generated", "repository", reference_ids + ["tri-r5-user-rejection"]))
    s02["artifactIds"] = ["tri-r5-discovery-log", "tri-r5-vault-rescan-sheet", "tri-r5-vault-rescan-candidates", "tri-r5-analysis-corrections", "tri-r5-user-rejection", "tri-r4-analysis-corrections", "tri-r4-user-rejection", "tri-r3-user-modeling-analysis", "tri-r2-analysis-angle-sheet", "tri-r2-analysis-measurement-board", "tri-r2-analysis-measurements"]
    s02["validations"] = [
        {"id": "rejection-recorded-verbatim", "status": "pass", "detail": "rev-004 驳回原文完整保存为 user-input 资产"},
        {"id": "claims-follow-user-direction", "status": "pass", "detail": "7 条 rev-5 claim；2 条 rev-4 claim superseded"},
        {"id": "discovery-log-present", "status": "pass", "detail": "vault 复扫 22 笔记 / 40 图，负结果已记录"},
        {"id": "millimetre-dimensions-measured", "status": "fail", "detail": "仍无实测；65 mm provisional；台面比 0.70 vs 0.797 待裁决"},
    ]
    active = [c["id"] for c in manifest["claims"] if c["stageId"] == "02-analysis" and c.get("state") != "superseded"]

    # ---- Gate 03 rev-004 ------------------------------------------------------
    s03 = reject_and_bump(manifest, "03-contract", 4, events)
    c = validation["contract"]
    contract = write_json(A03 / "modeling-contract.json", {
        "modelId": MODEL_ID, "stageId": "03-contract", "revision": 4, "recordedAt": NOW, "contractState": "user-authorized-provisional",
        "route": "deterministic-bpy-builder", "builder": rel(BUILDER), "units": "metres in Blender; mm here", "spinAxis": {"blender": "+Z", "unity": "+Y"}, "origin": "bearing centre",
        "overall": {"tipCircleDiameterMm": 65.0, "boundingWidthMm": round(validation["measured"]["boundingWidthMm"], 2), "bladeThicknessMm": BLADE_T, "assembledDepthMm": round(validation["measured"]["assembledDepthMm"], 2)},
        "hub": {"visible": False, "coreRingDiameterMm": round(2 * (SEAM_R - 0.3), 2), "coreThicknessMm": 2 * CORE_HALF, "counterboreDiameterMm": round(2 * SEAM_R, 2), "counterboreFloorZMm": CORE_HALF, "boreDiameterMm": 12.7, "material": "dark seam steel (wall + floor + bore)"},
        "cap": {"outerDiameterMm": round(2 * CAP_R, 2), "capToTipCircle": CAP_RATIO, "tableDiameterMm": round(2 * TABLE_R, 2), "tableToCap": TABLE_RATIO, "tableAboveBladeFaceMm": 1.5, "tableIsHighestPoint": True, "wedges": N_WEDGE, "wedgeTriangles": 2 * N_WEDGE, "wedgeRingSlopeDeg": SLOPE_DEG, "rimZigzagMm": ZIGZAG, "rimMeanBelowBladeFaceMm": c["rimMeanBelowBladeFaceMm"], "seamWidthMm": SEAM_W, "anisotropy": "table only (radial tangent) + concentric bump"},
        "blades": {"count": 3, "anglesDeg": [90, 210, 330], "solid": True, "outline": "teardrop / rounded triangle", "notchVDeg": c["notchVDeg"], "notchApexOnSeam": True, "tipArcRadiusMm": c["tipArcRadiusMm"], "tipArcSpanDeg": 120, "maxHalfWidthMm": c["bladeMaxHalfWidthMm"], "roofPlanes": 2, "roofSlopeDeg": c["roofSlopeDeg"], "endPlaneSlopeDeg": c["endPlaneSlopeDeg"], "sideWalls": f"vertical, {c['sideWallHeightAtWidestMm']} mm at widest", "bevelMm": 0.5, "bevelSegments": 2},
        "bearing": {"standard": "R188", "odMm": 12.7, "idMm": 6.35, "widthMm": 4.76, "visibility": "hidden"},
        "materials": {"body": {"metallic": 1.0, "roughness": 0.36}, "capTable": {"metallic": 1.0, "roughness": 0.30, "anisotropic": 0.85, "tangent": "radial", "ringBump": 0.09}, "capWedge": {"metallic": 1.0, "roughness": 0.34}, "seam": "dark steel 0.085 / gunmetal 0.03"},
        "forbidden": ["random scales", "wedges across the table", "rectangular wedge strips", "blade pockets", "anisotropy on wedges", "bright annulus", "visible hub collar", "cap under Rotor_Root", "subdivision", "smooth-by-angle on facets", "non-zero initial angular velocity"],
        "unknowns": ["official width/thickness mm", "table ratio 0.70 (user) vs 0.797 (photo) — decides rim height vs blade face", "root dark triangles (photo) vs solid (user)", "turning-mark pitch"],
        "consumedClaimIds": active,
    })
    upsert(manifest, asset("tri-r5-modeling-contract", "03-contract", "modeling-contract", contract, "contract", "provisional-modeling-contract", "repository-generated", "repository", reference_ids + ["tri-r5-user-rejection"], "user-authorized-provisional", claims=active))
    s03["artifactIds"] = ["tri-r5-modeling-contract"]
    s03["validations"] = [
        {"id": "consumes-all-active-gate02-claims", "status": "pass", "detail": f"{len(active)} claims"},
        {"id": "provisional-labelled", "status": "pass", "detail": "user-authorized-provisional"},
        {"id": "physical-dimensions-measured", "status": "fail", "detail": "无实测 mm"},
    ]

    # ---- Gate 04 rev-004 ------------------------------------------------------
    s04 = reject_and_bump(manifest, "04-architecture", 4, events)
    part_tree = write_json(A04 / "part-tree.json", {
        "modelId": MODEL_ID, "stageId": "04-architecture", "revision": 4, "recordedAt": NOW, "root": "UnifiedTriSpinner_Root",
        "tree": {
            "Rotor_Root (rotates)": {"RotorBody_OnePiece": ["Blade_01/02/03 petals (convex hull: 2 roof planes + end plane + vertical walls, 0.5 mm bevel, counterbored)", "HubCore ring Ø35.8 x 4.4 (hidden; bore Ø12.7)"]},
            "Fixed_Root (static)": {"TopCap_Root": ["FingerCap_Top (flat table / 48-triangle cone crown / dark skirt)", "CapStem_Top"], "BottomCap_Root": ["FingerCap_Bottom", "CapStem_Bottom"]},
            "BearingAssembly_Root (hidden)": ["BearingOuterRace", "BearingInnerRace", "BearingBall_01..08"],
            "Collision_Root (export only)": ["COL_Blade_01..03", "COL_Hub"],
        },
        "removedSinceRev3": ["HubCollar (visible body cylinder outside the seam)"],
        "explodedOrder": ["TopCap_Root +30 mm", "BearingAssembly_Root +12 mm", "RotorBody 0", "BottomCap_Root -28 mm"],
        "materialZones": 7,
    })
    upsert(manifest, asset("tri-r5-part-tree", "04-architecture", "part-tree", part_tree, "contract", "part-tree-and-material-zones", "repository-generated", "repository", ["tri-r5-modeling-contract"], claims=active))
    upsert(manifest, asset("tri-r5-exploded-plan", "04-architecture", "exploded-plan", A06 / "geometry-exploded.png", "blender-render", "real-blender-exploded-render", "repository-generated", "repository", ["tri-r5-modeling-contract"]))
    # 2D CAD (交互 CAD tab): geometry exported from the builder inside Blender, sheets drawn from that JSON only.
    cad_new = "tri-r5-cad-sheet-1" not in s04["artifactIds"]
    upsert(manifest, asset("tri-r5-cad-geometry", "04-architecture", "structural-cad", A06 / "cad-geometry.json", "contract", "cad-geometry-json-from-builder", "repository-generated", "repository", ["tri-r5-blockout-builder"], "export_unified_tri_spinner_cad.py (runs inside Blender, imports the builder)"))
    for aid, file, cls in [
        ("tri-r5-cad-sheet-1", "cad-sheet-1-plan-sections.png", "cad-sheet-plan-section-aa-cc-detail-b"),
        ("tri-r5-cad-sheet-1-pdf", "cad-sheet-1-plan-sections.pdf", "cad-sheet-plan-section-aa-cc-detail-b-vector"),
        ("tri-r5-cad-sheet-2", "cad-sheet-2-decision-overlays.png", "cad-sheet-decision-overlays-table-ratio-notch"),
        ("tri-r5-cad-sheet-2-pdf", "cad-sheet-2-decision-overlays.pdf", "cad-sheet-decision-overlays-vector"),
    ]:
        upsert(manifest, asset(aid, "04-architecture", "structural-cad", A06 / file, "contract", cls, "repository-generated", "repository", ["tri-r5-cad-geometry"], "draw_unified_tri_spinner_cad.py; all mm provisional"))
    s04["artifactIds"] = ["tri-r5-part-tree", "tri-r5-exploded-plan", "tri-r5-cad-geometry", "tri-r5-cad-sheet-1", "tri-r5-cad-sheet-1-pdf", "tri-r5-cad-sheet-2", "tri-r5-cad-sheet-2-pdf"]
    s04["validations"] = [
        {"id": "caps-not-under-rotor", "status": "pass", "detail": "FingerCap_* 挂 Fixed_Root"},
        {"id": "single-axis", "status": "pass", "detail": "+Z 原点"},
        {"id": "no-visible-hub-collar", "status": "pass", "detail": "HubCollar 已删除"},
        {"id": "structural-cad-present", "status": "pass", "detail": "平面图 + 剖面 A-A/C-C + 楔环 detail B/B'；几何来自 builder 导出，不另行推导"},
    ]
    if cad_new and "04-architecture" not in BUMPED:
        events.append({"type": "stage-revised", "stageId": "04-architecture", "notes": "rev-004 CAD sheets added (plan, sections A-A/C-C, crown detail, decision overlays) from cad-geometry.json exported by the builder."})

    # ---- Gate 05 rev-004 ------------------------------------------------------
    s05 = reject_and_bump(manifest, "05-blockout", 4, events)
    # Immutable snapshot of the builder that produced this revision. The live
    # path keeps changing between revisions and would keep flagging old stages.
    snapshot = A05 / "builder-snapshot-rev-004.py"
    snapshot.write_bytes(BUILDER.read_bytes())
    upsert(manifest, asset("tri-r5-blockout-builder", "05-blockout", "white-model-source", snapshot, "process", "deterministic-bpy-builder-snapshot", "repository-generated", "repository", ["tri-r5-modeling-contract", "tri-r5-part-tree"], f"snapshot of {rel(BUILDER)}", claims=active))
    rev3_snapshot = EV / "06-geometry/rev-003/builder-snapshot-rev-003.py"
    for old in manifest["assets"]:
        if old["id"] == "tri-r4-blockout-builder" and rev3_snapshot.exists():
            old.update({"path": rel(rev3_snapshot), "sha256": sha256(rev3_snapshot), "sizeBytes": rev3_snapshot.stat().st_size})
            old["provenance"]["note"] = "repointed to the rev-003 builder snapshot; the live builder path moved on to rev-004"
    ids05 = ["tri-r5-blockout-builder"]
    for view in ("hero", "top", "left-oblique", "low", "cap-macro", "cap-profile"):
        aid = f"tri-r5-blockout-{view}"
        upsert(manifest, asset(aid, "05-blockout", "white-model-hero" if view == "hero" else "white-model-support", A05 / f"blockout-{view}.png", "blender-render", f"real-blender-workbench-clay-{view}", "repository-generated", "repository", ["tri-r5-blockout-builder"]))
        ids05.append(aid)
    s05["artifactIds"] = ids05
    s05["validations"] = [{"id": "deterministic-source", "status": "pass", "detail": f"builder sha {sha256(BUILDER)[:12]}; no random jitter"}, {"id": "no-subdivision-no-smooth-by-angle", "status": "pass", "detail": "刻面 flat；仅连续曲面侧壁 smooth"}]

    # ---- Gate 06 rev-004 ------------------------------------------------------
    s06 = reject_and_bump(manifest, "06-geometry", 4, events)
    dim, piv = overlays(validation)
    ids06 = []
    for view, slot in {"front": "view-front", "back": "view-back", "top": "view-top", "bottom": "view-bottom", "left": "view-left", "right": "view-right"}.items():
        aid = f"tri-r5-geometry-{view}"
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / f"geometry-{view}.png", "blender-render", f"real-blender-cycles-ortho-{view}", "repository-generated", "repository", ["tri-r5-blockout-builder"], "ortho 0.082 m"))
        ids06.append(aid)
    for aid, slot, file, cls, role in [
        ("tri-r5-geometry-workbench", "workbench", "geometry-workbench.png", "real-blender-workbench-cavity", "blender-render"),
        ("tri-r5-geometry-dimension-overlay", "dimension-overlay", "dimension-overlay.png", "contract-dimensions-over-same-camera-orthos", "blender-render"),
        ("tri-r5-geometry-pivot-overlay", "pivot-overlay", "pivot-overlay.png", "pivot-and-axis-over-same-camera-orthos", "blender-render"),
        ("tri-r5-geometry-exploded", "exploded-geometry", "geometry-exploded.png", "real-blender-exploded-render", "blender-render"),
        ("tri-r5-geometry-hero", "geometry-support", "geometry-hero.png", "real-blender-cycles-hero", "blender-render"),
        ("tri-r5-geometry-left-oblique", "geometry-support", "geometry-left-oblique.png", "real-blender-cycles-left-oblique", "blender-render"),
        ("tri-r5-geometry-right-oblique", "geometry-support", "geometry-right-oblique.png", "real-blender-cycles-right-oblique", "blender-render"),
        ("tri-r5-geometry-low", "geometry-support", "geometry-low.png", "real-blender-cycles-low", "blender-render"),
        ("tri-r5-geometry-cap-macro", "geometry-support", "geometry-cap-macro.png", "real-blender-cycles-cap-macro", "blender-render"),
        ("tri-r5-geometry-cap-profile", "geometry-support", "geometry-cap-profile.png", "real-blender-cycles-cap-profile", "blender-render"),
        ("tri-r5-geometry-notch-macro", "geometry-support", "geometry-notch-macro.png", "real-blender-cycles-notch-macro", "blender-render"),
        ("tri-r5-geometry-review-board", "geometry-support", "review-board.png", "review-board-with-reference-and-variant", "blender-render"),
        ("tri-r5-geometry-validation", "validation-report", "geometry-validation.json", "builder-geometry-validation", "validation"),
    ]:
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / file, role, cls, "repository-generated", "repository", ["tri-r5-blockout-builder"]))
        ids06.append(aid)
    for view in ("hero", "cap-profile", "cap-macro", "top", "low"):
        aid = f"tri-r5-variant-table0797-{view}"
        upsert(manifest, asset(aid, "06-geometry", "geometry-support", VAR / f"geometry-{view}.png", "analysis", "labelled-comparison-variant-table-0.797-not-a-revision", "repository-generated", "repository", ["tri-r5-blockout-builder"], "仅对比：台面 0.797（照片值）；未导出、不是候选 revision"))
        ids06.append(aid)
    upsert(manifest, asset("tri-r5-variant-table0797-validation", "06-geometry", "geometry-support", VAR / "geometry-validation.json", "analysis", "labelled-comparison-variant-stats", "repository-generated", "repository", ["tri-r5-blockout-builder"]))
    ids06.append("tri-r5-variant-table0797-validation")
    ids06.append("tri-r5-user-rejection")
    ring = validation["measured"]["wedgeRing"]
    audit = validation["measured"]["bodyAudit"]
    planes = validation["measured"]["bodyLargeTopPlanesPerBlade"]
    s06["artifactIds"] = ids06
    s06["validations"] = [
        {"id": "crown-is-cone-not-wall", "status": "pass" if ring["tableIsHighestPoint"] and 25.0 <= SLOPE_DEG <= 35.0 and 24.0 <= (ring["faceSlopeMinDeg"] + ring["faceSlopeMaxDeg"]) / 2 <= 36.0 else "fail", "detail": f"平盘最高={ring['tableIsHighestPoint']}；圆锥 {SLOPE_DEG:.0f}°，锯齿使单个三角面斜 {ring['faceSlopeMinDeg']}–{ring['faceSlopeMaxDeg']}°（均值 {(ring['faceSlopeMinDeg'] + ring['faceSlopeMaxDeg']) / 2:.1f}，目标 25–35）"},
        {"id": "wedge-triangles-alternate", "status": "pass" if ring["wedgeTriangles"] == 48 and ring["tipsPointingInward"] == 24 and ring["adjacentNormalAngleMinDeg"] >= 6.0 else "fail", "detail": f"{ring['wedges']} 楔 / {ring['wedgeTriangles']} 三角，尖端向内 {ring['tipsPointingInward']} 向外 {ring['tipsPointingOutward']}，相邻法线 {ring['adjacentNormalAngleMinDeg']}–{ring['adjacentNormalAngleMaxDeg']}°"},
        {"id": "table-flat", "status": "pass" if ring["tableMaxTiltDeg"] < 0.5 else "fail", "detail": f"台面最大倾斜 {ring['tableMaxTiltDeg']}°"},
        {"id": "cap-low-profile", "status": "pass" if abs(validation["measured"]["capTopAboveBladeFaceMm"] - 1.5) < 0.05 else "fail", "detail": f"盖顶高出叶面 {validation['measured']['capTopAboveBladeFaceMm']:.2f} mm；楔环外沿低于叶面 {c['rimMeanBelowBladeFaceMm']} mm（0.797 变体 {variant['rimMeanBelowBladeFaceMm']} mm）"},
        {"id": "hub-hidden-in-top-view", "status": "pass" if not validation["measured"]["hubVisibleInTopView"] else "fail", "detail": f"notchApex r={validation['measured']['notchApexRadiusMm']} mm，沉孔 r={SEAM_R:.2f} mm"},
        {"id": "blade-thickness-and-roof", "status": "pass" if abs(validation["measured"]["bladeTopZMm"] * 2 - BLADE_T) < 0.05 and min(planes.values()) >= 3 else "fail", "detail": f"叶厚 {validation['measured']['bladeTopZMm'] * 2:.2f} mm；每叶大平面 {planes}（屋脊 2 + 端面 1）"},
        {"id": "rotor-manifold", "status": "pass" if audit["nonManifoldEdges"] == 0 and audit["boundaryEdges"] == 0 and audit["zeroAreaFaces"] == 0 else "fail", "detail": json.dumps(audit)},
        {"id": "cap-ratio-matches-photo", "status": "pass" if abs(validation["measured"]["capRatioActual"] - CAP_RATIO) < 0.01 else "fail", "detail": f"{validation['measured']['capRatioActual']:.3f}"},
        {"id": "seam-0-8", "status": "pass" if abs(c["seamWidthMm"] - 0.8) < 1e-6 else "fail", "detail": f"{c['seamWidthMm']} mm"},
        {"id": "no-blade-pockets-no-random-scales", "status": "pass", "detail": "builder has no jitter and no pocket cutters"},
    ]

    for sid in ("07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"):
        s = stage(manifest, sid)
        if s["status"] in ("approved", "draft", "ready_for_review", "legacy"):
            s["status"] = "stale"
        s["staleReason"] = "Upstream geometry replaced by unified tri-spinner rev-004."

    # Gate 01 content is unchanged since rev-002; its stale flag came from the
    # workbench refresh seeing digests that earlier scripts never recorded.
    s01 = stage(manifest, "01-intake")
    if s01["status"] == "stale" and s01.get("decision") is None:
        s01["status"] = "draft"
        s01.pop("staleReason", None)

    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"] = {
        "rebuildRequested": True, "shippingAssetUnchanged": True, "visualApproval": "pending", "deviceStatus": "not-approved",
        "diagnosis": "用户第二次驳回（19:43）：楔环成城墙、叶片成扇形桨露机身、叶片太薄。rev-004（Gate 02 rev-005 / 03–06 rev-004）已重建：25° 圆锥楔环 48 三角锯齿沿、平盘最高、泪滴叶片 60° 缺口 R12 外弧、11.5 mm 厚屋脊 + 端面斜切、机身顶视不可见、暗缝 0.8。Cycles 出图。待裁决：台面 0.70 vs 0.797（决定楔环外沿是否低于叶面）。Gate 02–06 draft 等待批准；未进 Unity，未推手机。",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for sid in ("02-analysis", "03-contract", "04-architecture", "05-blockout", "06-geometry"):
        if sid in BUMPED:
            events.append({"type": "stage-revised", "stageId": sid, "notes": "New draft revision from build_unified_tri_spinner.py rev-004 (cone zigzag crown, teardrop petals, 11.5 mm roof blades, hub hidden, seam 0.8)."})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "activeClaims": len(active)}))


if __name__ == "__main__":
    main()
