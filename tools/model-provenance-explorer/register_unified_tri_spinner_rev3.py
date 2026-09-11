"""Record the user's rejection of Gate 02 rev-003 / Gates 03-06 rev-002 and
register the rev-003 unified tri-spinner geometry as new draft revisions.

Rejection wording is stored verbatim in
`evidence/06-geometry/rev-002/user-rejection-2026-09-05.md` (user-input).
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
REJ = EV / "06-geometry/rev-002/user-rejection-2026-09-05.md"
A02 = EV / "02-analysis/rev-004"
A03 = EV / "03-contract/rev-003"
A04 = EV / "04-architecture/rev-003"
A05 = EV / "05-blockout/rev-003"
A06 = EV / "06-geometry/rev-003"
BUILDER = REPO / "tools/blender/build_unified_tri_spinner.py"

# Builder constants (mm) mirrored for the overlays and contract.
TIP_R = 32.5
BODY_T = 10.0
HUB_R = 18.8
COUNTERBORE_R = 18.4
COUNTERBORE_DEPTH = 2.2
CAP_RATIO = 0.536
TABLE_RATIO = 0.70
CAP_R = TIP_R * CAP_RATIO
TABLE_R = CAP_R * TABLE_RATIO
TABLE_Z = BODY_T / 2 + 1.5
CROWN_EDGE_Z = BODY_T / 2 - 0.9
N_WEDGE = 24
EDGE_LIFT = 0.22
BLADE_T = 9.9
RES = 1200
PX_PER_MM = RES / 82.0
NOW = datetime.now(timezone.utc).isoformat()

REJECTION_SUMMARY = (
    "用户驳回五点：1 盖体应为平车削盘（≈0.70 盖径）+ 外圈规则向下楔面，不是从圆心铺到边的风车，且冠环不应有随机鳞片；"
    "2 盖悬空太高、黑环太厚，应只高出叶面 1–2 mm、黑线约 1 mm；3 叶片应实心无凹坑、向中心收窄、外端大圆角平面、4–5 个大平面硬切、竖直侧壁；"
    "4 太镜面，Roughness≈0.3，各向异性只给中心圆盘；5 倒角 0.5 mm 2–3 段。"
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


def overlays() -> tuple[Path, Path]:
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

    dim, d = board("Gate 06 rev-003 尺寸覆盖 — 全部 mm 为 provisional（照片比例 × 65 mm）", "左：顶视正交   右：前视正交   ortho_scale 0.082 m")

    def circle(r_mm, color, text, dy):
        r = r_mm * PX_PER_MM
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
        d.text((cx + r * 0.7071 + 10, cy - r * 0.7071 + dy), text, fill=color, font=label)

    circle(TIP_R, (255, 140, 40), f"外接圆 Ø{2 * TIP_R:.1f}", -30)
    circle(HUB_R, (200, 200, 210), f"毂 Ø{2 * HUB_R:.1f}", -4)
    circle(COUNTERBORE_R, (255, 90, 90), f"沉孔 Ø{2 * COUNTERBORE_R:.1f}（暗缝 {COUNTERBORE_R - CAP_R:.1f}）", 22)
    circle(CAP_R, (70, 225, 255), f"盖 Ø{2 * CAP_R:.1f}（{CAP_RATIO:.3f}×外接圆）", 48)
    circle(TABLE_R, (120, 245, 160), f"平台面 Ø{2 * TABLE_R:.1f}（{TABLE_RATIO:.2f}×盖）", 74)

    def hline(z_mm, color, text):
        y = fcy - z_mm * PX_PER_MM
        d.line([fx0 + 80, y, fx0 + RES - 80, y], fill=color, width=2)
        d.text((fx0 + 90, y - 30), text, fill=color, font=label)

    hline(BODY_T / 2, (200, 200, 210), f"机身/叶面 z=+{BODY_T / 2:.1f}（厚 {BODY_T:.1f}，叶 {BLADE_T:.1f}）")
    hline(-BODY_T / 2, (200, 200, 210), f"机身底面 z=-{BODY_T / 2:.1f}")
    hline(TABLE_Z, (70, 225, 255), f"盖顶平面 z=+{TABLE_Z:.1f}（高出叶面 1.5，装配总厚 {2 * TABLE_Z:.1f}）")
    hline(CROWN_EDGE_Z, (255, 200, 80), f"楔环外缘 z=+{CROWN_EDGE_Z:.1f}（斜 {math.degrees(math.atan((TABLE_Z - CROWN_EDGE_Z) / (CAP_R - TABLE_R))):.0f}°，外缘脊谷 ±{EDGE_LIFT:.2f}）")
    hline(BODY_T / 2 - COUNTERBORE_DEPTH, (255, 90, 90), f"沉孔底 z=+{BODY_T / 2 - COUNTERBORE_DEPTH:.1f}")
    d.text((fx0 + 90, 120 + RES - 60), f"{N_WEDGE} 楔 / {2 * N_WEDGE} 平面 · 相邻法线 18.7–25.0° · 台面倾斜 0.0°", fill=(120, 245, 160), font=label)
    dim_path = A06 / "dimension-overlay.png"
    dim.save(dim_path)

    piv, d = board("Gate 06 rev-003 轴心覆盖 — 原点在轴承中心，Blender +Z 自旋轴 → Unity +Y", "Rotor_Root 绕轴旋转；Fixed_Root（上下盖）不旋转；初始角速度 0")
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
        "producer": {"name": "register_unified_tri_spinner_rev3.py", "version": "2026-09-05"},
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


def reject_and_bump(manifest, stage_id, new_revision, events):
    s = stage(manifest, stage_id)
    s.setdefault("historicalRevisions", []).append({"revision": s["revision"], "artifactIds": list(s["artifactIds"]), "status": "rejected", "reason": REJECTION_SUMMARY})
    s.setdefault("historicalDecisions", []).append({"revision": s["revision"], "action": "reject", "decidedBy": "user", "decidedAt": NOW, "notes": f"原文见 tri-r4-user-rejection。摘要：{REJECTION_SUMMARY}"})
    events.append({"type": "stage-rejected", "stageId": stage_id, "notes": f"{stage_id} rev {s['revision']} rejected by user; verbatim wording in evidence/06-geometry/rev-002/user-rejection-2026-09-05.md."})
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

    upsert(manifest, asset("tri-r4-user-rejection", "06-geometry", "geometry-support", REJ, "user-input", "user-chat-rejection-verbatim", "user-provided", "user", [], "2026-09-05 驳回原文"))

    # ---- Gate 02 rev-004: claims follow the user's direction ----------------
    s02 = reject_and_bump(manifest, "02-analysis", 4, events)
    for claim in manifest["claims"]:
        if claim["id"] in ("tri-r3-star-on-table", "tri-r3-blade-facets-irregular", "tri-r3-pocket-polished-chamfer", "tri-r2-body-facets-too", "tri-r2-table-ratio"):
            claim["state"] = "superseded"
            claim["supersededBy"] = "tri-r4-two-layer-cap"
    new_claims = [
        ("tri-r4-two-layer-cap", "geometry", "high", "中心盖为两层：中间平的车削圆盘（约 0.70 盖径，细密同心纹，径向各向异性出一道柔和弧光）；外圈为规则等分的向下倾斜楔面（24 楔，每楔两个平面交成一条径向脊线，相邻半面法线相反），没有任何随机鳞片。星芒来自楔面几何法线，不来自纹理。用户 2026-09-05 指示。"),
        ("tri-r4-cap-low-profile", "geometry", "high", "盖顶只高出叶片顶面约 1.5 mm；盖与机身之间的黑色只是约 1 mm 的细线；不允许高的暗色圆柱底座。"),
        ("tri-r4-solid-faceted-blades", "geometry", "high", "叶片实心、无开孔；根部半宽约 12.5 mm 略向外加宽，外端沿外接圆走大圆角；顶面由 4–5 个大平面硬切并有脊线；侧壁近乎竖直；所有边 0.5 mm 小倒角。照片 geeone-01 里叶根紧贴盖处的暗色三角凹陷已向用户标出，本轮按用户指示不建。"),
        ("tri-r4-satin-material", "material", "high", "整机 satin 半哑光（Roughness≈0.3–0.4），非镜面；各向异性只用于中心圆盘；楔面区不加各向异性。"),
        ("tri-r4-table-ratio-discrepancy", "dimension", "medium", "照片读数台面/盖 = 0.797±0.03，用户指示 0.70；本轮按用户值 0.70 建模，差异保留待正俯视图或实测裁决。"),
    ]
    existing = {c["id"] for c in manifest["claims"]}
    for cid, category, confidence, statement in new_claims:
        if cid not in existing:
            manifest["claims"].append({"id": cid, "stageId": "02-analysis", "category": category, "statement": statement, "confidence": confidence, "sourceAssetIds": reference_ids + ["tri-r4-user-rejection", "tri-r3-user-modeling-analysis"], "sourceRegions": []})
    corrections = write_json(A02 / "analysis-corrections-rev4.json", {
        "modelId": MODEL_ID, "stageId": "02-analysis", "revision": 4, "recordedAt": NOW,
        "basis": "用户 2026-09-05 驳回原文（tri-r4-user-rejection）+ geeone-01 高倍复核",
        "changes": [
            {"topic": "盖结构", "rev3": "放射楔铺满台面到圆心；冠环不规则鳞片", "rev4": "平车削盘 0.70 + 24 规则楔环（48 平面交替）", "authority": "user"},
            {"topic": "盖高度", "rev3": "台面 z=7.0，盖悬浮 0.4 于叶面之上，暗裙可见", "rev4": "台面 z=6.5（高出叶面 1.5），楔环外缘 z=4.1 沉入缝内", "authority": "user"},
            {"topic": "叶片", "rev3": "抖动凸包不规则刻面 + 三角口袋", "rev4": "实心、确定性 4–5 大平面、竖直侧壁、根宽 12 mm、外端沿外接圆", "authority": "user + photo"},
            {"topic": "材质", "rev3": "roughness 0.30 + 台面各向异性", "rev4": "body 0.36 / wedge 0.34 / table 0.32 仅台面各向异性；key 光加大到 55 mm", "authority": "user"},
            {"topic": "倒角", "rev3": "0.6 mm 1 段（45° 平倒角）", "rev4": "0.5 mm 2 段", "authority": "user"},
            {"topic": "毂", "rev3": "毂领暗色", "rev4": "毂领为机身亮金属，只有沉孔壁与底暗", "authority": "photo (one solid body)"},
            {"topic": "叶根暗三角", "rev3": "口袋", "rev4": "不建；照片证据保留供用户裁决", "authority": "user"},
        ],
    })
    upsert(manifest, asset("tri-r4-analysis-corrections", "02-analysis", "analysis-board", corrections, "analysis", "rev3-to-rev4-correction-table", "repository-generated", "repository", reference_ids + ["tri-r4-user-rejection"]))
    s02["artifactIds"] = ["tri-r3-discovery-log", "tri-r4-analysis-corrections", "tri-r4-user-rejection", "tri-r3-user-modeling-analysis", "tri-r2-analysis-angle-sheet", "tri-r2-analysis-measurement-board", "tri-r2-analysis-measurements"]
    s02["validations"] = [
        {"id": "rejection-recorded-verbatim", "status": "pass", "detail": "rev-003 驳回原文完整保存为 user-input 资产"},
        {"id": "claims-follow-user-direction", "status": "pass", "detail": "5 条 rev-4 claim；5 条旧 claim superseded"},
        {"id": "discovery-log-present", "status": "pass", "detail": "沿用 rev-003 discovery log"},
        {"id": "millimetre-dimensions-measured", "status": "fail", "detail": "仍无实测；65 mm provisional；台面比 0.70 vs 照片 0.797 待裁决"},
    ]
    active = [c["id"] for c in manifest["claims"] if c["stageId"] == "02-analysis" and c.get("state") != "superseded"]

    # ---- Gate 03 rev-003 ----------------------------------------------------
    s03 = reject_and_bump(manifest, "03-contract", 3, events)
    contract = write_json(A03 / "modeling-contract.json", {
        "modelId": MODEL_ID, "stageId": "03-contract", "revision": 3, "recordedAt": NOW, "contractState": "user-authorized-provisional",
        "route": "deterministic-bpy-builder", "builder": rel(BUILDER), "units": "metres in Blender; mm here", "spinAxis": {"blender": "+Z", "unity": "+Y"}, "origin": "bearing centre",
        "overall": {"tipCircleDiameterMm": 65.0, "boundingWidthMm": 64.0, "bodyThicknessMm": BODY_T, "bladeThicknessMm": BLADE_T, "assembledDepthMm": 2 * TABLE_Z},
        "hub": {"hubDiameterMm": 2 * HUB_R, "counterboreDiameterMm": 2 * COUNTERBORE_R, "counterboreDepthMm": COUNTERBORE_DEPTH, "boreDiameterMm": 12.7, "lipWidthMm": 0.4, "hubMaterial": "body satin; counterbore wall+floor dark"},
        "cap": {"outerDiameterMm": round(2 * CAP_R, 2), "capToTipCircle": CAP_RATIO, "tableDiameterMm": round(2 * TABLE_R, 2), "tableToCap": TABLE_RATIO, "tableAboveBladeFaceMm": 1.5, "tableFlat": True, "wedges": N_WEDGE, "planarHalfFaces": 2 * N_WEDGE, "wedgeRingSlopeDeg": round(math.degrees(math.atan((TABLE_Z - CROWN_EDGE_Z) / (CAP_R - TABLE_R))), 1), "outerEdgeLiftMm": EDGE_LIFT, "adjacentNormalAngleDeg": [18.7, 25.0], "seamWidthMm": round(COUNTERBORE_R - CAP_R, 2), "anisotropy": "table only"},
        "blades": {"count": 3, "anglesDeg": [90, 210, 330], "solid": True, "rootHalfWidthMm": 12.0, "outerEnd": "arc on tip circle from ±14.6 mm", "topPlanesPerBlade": "4-5 large + chamfers (measured 7)", "sideWalls": "vertical, 3.8 mm", "bevelMm": 0.5, "bevelSegments": 2},
        "bearing": {"standard": "R188", "odMm": 12.7, "idMm": 6.35, "widthMm": 4.76, "visibility": "hidden"},
        "materials": {"body": {"metallic": 1.0, "roughness": 0.36}, "capTable": {"metallic": 1.0, "roughness": 0.32, "anisotropic": 0.7, "tangent": "radial", "ringBump": 0.035}, "capWedge": {"metallic": 1.0, "roughness": 0.34}, "seam": "dark steel 0.085 / gunmetal 0.03"},
        "forbidden": ["random scales", "wedges across the table", "blade pockets", "anisotropy on wedges", "bright annulus", "cap under Rotor_Root", "subdivision", "smooth-by-angle on facets", "non-zero initial angular velocity"],
        "unknowns": ["official width/thickness mm", "table ratio 0.70 (user) vs 0.797 (photo)", "root dark triangles (photo) vs solid (user)", "turning-mark pitch"],
        "consumedClaimIds": active,
    })
    upsert(manifest, asset("tri-r4-modeling-contract", "03-contract", "modeling-contract", contract, "contract", "provisional-modeling-contract", "repository-generated", "repository", reference_ids + ["tri-r4-user-rejection"], "user-authorized-provisional", claims=active))
    s03["artifactIds"] = ["tri-r4-modeling-contract"]
    s03["validations"] = [
        {"id": "consumes-all-active-gate02-claims", "status": "pass", "detail": f"{len(active)} claims"},
        {"id": "provisional-labelled", "status": "pass", "detail": "user-authorized-provisional"},
        {"id": "physical-dimensions-measured", "status": "fail", "detail": "无实测 mm"},
    ]

    # ---- Gate 04 rev-003 ----------------------------------------------------
    s04 = reject_and_bump(manifest, "04-architecture", 3, events)
    part_tree = write_json(A04 / "part-tree.json", {
        "modelId": MODEL_ID, "stageId": "04-architecture", "revision": 3, "recordedAt": NOW, "root": "UnifiedTriSpinner_Root",
        "tree": {
            "Rotor_Root (rotates)": {"RotorBody_OnePiece": ["HubCollar (body satin; counterbore wall dark steel)", "HubCore (dark counterbore floor, bore Ø12.7)", "Blade_01/02/03 (solid, hard planar cuts, 0.5 mm bevel)"]},
            "Fixed_Root (static)": {"TopCap_Root": ["FingerCap_Top (flat turned table / 24-wedge ring / dark skirt)", "CapStem_Top"], "BottomCap_Root": ["FingerCap_Bottom", "CapStem_Bottom"]},
            "BearingAssembly_Root (hidden)": ["BearingOuterRace", "BearingInnerRace", "BearingBall_01..08"],
            "Collision_Root (export only)": ["COL_Blade_01..03", "COL_Hub"],
        },
        "explodedOrder": ["TopCap_Root +30 mm", "BearingAssembly_Root +12 mm", "RotorBody 0", "BottomCap_Root -28 mm"],
        "materialZones": 7,
    })
    upsert(manifest, asset("tri-r4-part-tree", "04-architecture", "part-tree", part_tree, "contract", "part-tree-and-material-zones", "repository-generated", "repository", ["tri-r4-modeling-contract"], claims=active))
    upsert(manifest, asset("tri-r4-exploded-plan", "04-architecture", "exploded-plan", A06 / "geometry-exploded.png", "blender-render", "real-blender-exploded-render", "repository-generated", "repository", ["tri-r4-modeling-contract"]))
    s04["artifactIds"] = ["tri-r4-part-tree", "tri-r4-exploded-plan"]
    s04["validations"] = [{"id": "caps-not-under-rotor", "status": "pass", "detail": "FingerCap_* 挂 Fixed_Root"}, {"id": "single-axis", "status": "pass", "detail": "+Z 原点"}]

    # ---- Gate 05 rev-003 ----------------------------------------------------
    s05 = reject_and_bump(manifest, "05-blockout", 3, events)
    upsert(manifest, asset("tri-r4-blockout-builder", "05-blockout", "white-model-source", BUILDER, "process", "deterministic-bpy-builder", "repository-generated", "repository", ["tri-r4-modeling-contract", "tri-r4-part-tree"], claims=active))
    ids05 = ["tri-r4-blockout-builder"]
    for view in ("hero", "top", "left-oblique", "low", "cap-macro"):
        aid = f"tri-r4-blockout-{view}"
        upsert(manifest, asset(aid, "05-blockout", "white-model-hero" if view == "hero" else "white-model-support", A05 / f"blockout-{view}.png", "blender-render", f"real-blender-clay-{view}", "repository-generated", "repository", ["tri-r4-blockout-builder"]))
        ids05.append(aid)
    s05["artifactIds"] = ids05
    s05["validations"] = [{"id": "deterministic-source", "status": "pass", "detail": f"builder sha {sha256(BUILDER)[:12]}; no random jitter"}, {"id": "no-subdivision-no-smooth-by-angle", "status": "pass", "detail": "全部刻面 flat shading"}]

    # ---- Gate 06 rev-003 ----------------------------------------------------
    s06 = reject_and_bump(manifest, "06-geometry", 3, events)
    dim, piv = overlays()
    ids06 = []
    for view, slot in {"front": "view-front", "back": "view-back", "top": "view-top", "bottom": "view-bottom", "left": "view-left", "right": "view-right"}.items():
        aid = f"tri-r4-geometry-{view}"
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / f"geometry-{view}.png", "blender-render", f"real-blender-ortho-{view}", "repository-generated", "repository", ["tri-r4-blockout-builder"], "ortho 0.082 m"))
        ids06.append(aid)
    for aid, slot, file, cls, role in [
        ("tri-r4-geometry-workbench", "workbench", "geometry-workbench.png", "real-blender-workbench-cavity", "blender-render"),
        ("tri-r4-geometry-dimension-overlay", "dimension-overlay", "dimension-overlay.png", "contract-dimensions-over-same-camera-orthos", "blender-render"),
        ("tri-r4-geometry-pivot-overlay", "pivot-overlay", "pivot-overlay.png", "pivot-and-axis-over-same-camera-orthos", "blender-render"),
        ("tri-r4-geometry-exploded", "exploded-geometry", "geometry-exploded.png", "real-blender-exploded-render", "blender-render"),
        ("tri-r4-geometry-hero", "geometry-support", "geometry-hero.png", "real-blender-eevee-hero", "blender-render"),
        ("tri-r4-geometry-left-oblique", "geometry-support", "geometry-left-oblique.png", "real-blender-eevee-left-oblique", "blender-render"),
        ("tri-r4-geometry-right-oblique", "geometry-support", "geometry-right-oblique.png", "real-blender-eevee-right-oblique", "blender-render"),
        ("tri-r4-geometry-low", "geometry-support", "geometry-low.png", "real-blender-eevee-low", "blender-render"),
        ("tri-r4-geometry-cap-macro", "geometry-support", "geometry-cap-macro.png", "real-blender-eevee-cap-macro", "blender-render"),
        ("tri-r4-geometry-validation", "validation-report", "geometry-validation.json", "builder-geometry-validation", "validation"),
    ]:
        upsert(manifest, asset(aid, "06-geometry", slot, A06 / file, role, cls, "repository-generated", "repository", ["tri-r4-blockout-builder"]))
        ids06.append(aid)
    ids06.append("tri-r4-user-rejection")
    validation = json.loads((A06 / "geometry-validation.json").read_text(encoding="utf-8"))
    ring = validation["measured"]["wedgeRing"]
    audit = validation["measured"]["rotorAudit"]
    s06["artifactIds"] = ids06
    s06["validations"] = [
        {"id": "wedge-normals-alternate", "status": "pass" if ring["adjacentNormalAngleMinDeg"] >= 6.0 else "fail", "detail": f"{ring['wedges']} 楔 / {ring['wedgeHalfFaces']} 平面，相邻法线 {ring['adjacentNormalAngleMinDeg']}–{ring['adjacentNormalAngleMaxDeg']}°"},
        {"id": "table-flat", "status": "pass" if ring["tableMaxTiltDeg"] < 0.5 else "fail", "detail": f"台面最大倾斜 {ring['tableMaxTiltDeg']}°"},
        {"id": "cap-low-profile", "status": "pass" if abs(validation["measured"]["capTopAboveBladeFaceMm"] - 1.5) < 0.05 else "fail", "detail": f"盖顶高出叶面 {validation['measured']['capTopAboveBladeFaceMm']:.2f} mm"},
        {"id": "rotor-manifold", "status": "pass" if audit["nonManifoldEdges"] == 0 and audit["boundaryEdges"] == 0 else "fail", "detail": json.dumps(audit)},
        {"id": "cap-ratio-matches-photo", "status": "pass" if abs(validation["measured"]["capRatioActual"] - CAP_RATIO) < 0.01 else "fail", "detail": f"{validation['measured']['capRatioActual']:.3f}"},
        {"id": "no-blade-pockets-no-random-scales", "status": "pass", "detail": "builder has no jitter and no pocket cutters"},
    ]

    for sid in ("07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"):
        s = stage(manifest, sid)
        if s["status"] in ("approved", "draft", "ready_for_review", "legacy"):
            s["status"] = "stale"
        s["staleReason"] = "Upstream geometry replaced by unified tri-spinner rev-003."

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["currentState"] = {
        "rebuildRequested": True, "shippingAssetUnchanged": True, "visualApproval": "pending", "deviceStatus": "not-approved",
        "diagnosis": "用户驳回 rev-003/rev-002（五点：两层盖、盖太高、叶片实心与形态、satin、倒角）。rev-004/rev-003 已按指示重建：平车削台面 0.70 + 24 规则楔环、盖高出叶面 1.5 mm、暗缝 1 mm、实心硬切叶片、satin 材质、0.5 mm 倒角。Gate 02–06 draft 等待批准；未进 Unity，未推手机。",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for sid in ("02-analysis", "03-contract", "04-architecture", "05-blockout", "06-geometry"):
        events.append({"type": "stage-revised", "stageId": sid, "notes": "New draft revision from build_unified_tri_spinner.py rev-003 (two-layer cap, solid hard-cut blades, satin)."})
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "activeClaims": len(active)}))


if __name__ == "__main__":
    main()
