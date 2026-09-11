"""Persist the user's approval of tri-spinner-slab-v3-cmf Gate 07 rev-003 ("确认", 2026-09-11 15:26, with
gate07-r003-material-id-vs-render.png open) and register the approved case materials in the MaterialLibrary
(contract: new_materials_require_library_registration_after_approval). Opens Gate 08 as draft.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_ID = "premium-display-case"
VARIANT = "tri-spinner-slab-v3-cmf"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
E07 = PIPELINE_DIR / "evidence/07-material/rev-003"
LIB_PATH = REPO / "unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json"
NOW = datetime.now(timezone.utc).isoformat()
WORDING = "确认"
DECIDED_AT = "2026-09-11T15:26:00+08:00"
SOURCE_ID = "src.user_gate07_rev003_approval_20260911"
SNAPSHOT = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py"
CONTRACT = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value) -> str:
    if isinstance(value, list):
        return "[" + ",".join(stable_json(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{stable_json(value[k])}" for k in sorted(value)) + "}"
    return json.dumps(value, ensure_ascii=False)


def update_stage_digests(manifest) -> None:
    assets = {a["id"]: a for a in manifest["assets"]}
    previous = None
    for stage_record in manifest["stages"]:
        hashes = [assets[aid]["sha256"] for aid in stage_record["artifactIds"] if aid in assets and assets[aid].get("sha256")]
        claims = [stable_json(c) for c in manifest.get("claims", []) if c["stageId"] == stage_record["id"]]
        digest = hashlib.sha256("\n".join(sorted(hashes + claims)).encode("utf-8")).hexdigest()
        stage_record["inputDigest"] = digest if previous is None else previous
        stage_record["outputDigest"] = digest
        previous = digest


def lin(hex_str):
    h = hex_str.lstrip("#"); out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(round(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4, 4))
    return out


def lin_rgb(rgb):
    return [round(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4, 4) for c in rgb]


def entry(mid, zh, en, family, description, phrases, avoid, material_name, base, metallic, roughness, parts, extra_blender=None):
    blender = {"authority": "blender-lookdev", "materialName": material_name, "baseColor": base, "metallic": metallic, "roughness": roughness}
    blender.update(extra_blender or {})
    return {"id": mid, "name": {"zh": zh, "en": en}, "family": family, "status": "approved-gate07", "description": description,
            "imageGen": {"phrases": phrases, "avoid": avoid}, "blender": blender, "unity": None,
            "usedBy": [{"model": MODEL_ID, "variant": VARIANT, "parts": parts}],
            "sources": [{"path": SNAPSHOT, "note": f"Gate 07 rev-003 lookdev, user approval “{WORDING}” {DECIDED_AT}"},
                        {"path": CONTRACT, "note": "contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map"}]}


NEW_MATERIALS = [
    entry("case-clear-crystal", "透明水晶外壳", "Clear crystal shell", "glass",
          "展示盒最外层的透明聚碳酸酯水晶框：IOR 1.49，极低粗糙度，薄清漆层，整片 300–650 nm 薄膜虹彩让边缘在彩色边光下泛出青/品红。",
          ["clear polycarbonate crystal frame", "thin-film iridescent edge sheen", "sharp glass-like bevels", "IOR 1.49 transmission"],
          ["frosted glass", "tinted acrylic", "rainbow across flat faces under neutral light"],
          "M_PDC_ClearCrystal", lin("#F8FBFF"), 0, 0.035,
          ["GEO_PDC_OUTER_CRYSTAL_FRAME", "GEO_PDC_POCKET_CLIP_*"],
          {"transmission": 1.0, "ior": 1.49, "coatWeight": 0.08, "coatRoughness": 0.03, "thinFilmThicknessNm": [300, 650], "thinFilmIor": 1.355, "thinFilmMask": "whole crystal; COLOR0.g edge boost optional"}),
    entry("case-smoke-lilac-liner", "烟紫内衬", "Smoke-lilac liner", "glass",
          "盒体内圈与凹槽壁的半透明烟紫内衬：透射 0.775，带体积吸收，随稀有度档位微调基色。",
          ["smoked lilac translucent liner", "soft volumetric absorption", "matte-satin translucency"],
          ["clear glass", "opaque plastic", "saturated purple"],
          "M_PDC_SmokeLiner", lin("#EEEAF4"), 0, 0.15,
          ["GEO_PDC_SMOKE_INNER_LINER", "GEO_PDC_POCKET_SMOKE_WALL"],
          {"transmission": 0.775, "ior": 1.49, "volumeAbsorptionColor": [0.55, 0.48, 0.66], "volumeAbsorptionDensity": 180}),
    entry("case-dark-sandblast", "深色喷砂钢", "Dark sandblasted steel", "dark-metal",
          "主舱 field 与后板的深灰喷砂钢面：scheme A 用 #5C6266 取代规格 #AEB3B6，微凸粒度 0.13 mm、高度 0.0105 mm，粗糙度 0.45±0.03。",
          ["dark bead-blasted steel", "fine even micro-grain", "low diffuse sheen", "no directional brushing"],
          ["brushed lines", "mirror", "light silver sandblast"],
          "M_PDC_DarkSandblast", lin("#5C6266"), 1, 0.45,
          ["GEO_PDC_MAIN_MICROBLAST_FIELD", "GEO_PDC_REAR_PLATE"],
          {"roughnessDelta": 0.03, "sandblastFeatureMm": 0.13, "sandblastBumpMm": 0.0105, "supersedesSpecBaseColorHex": "#AEB3B6"}),
    entry("case-piano-black", "钢琴黑板", "Piano-black plate", "dark-metal",
          "header 石墨板、数值板与凹槽底的钢琴黑：深炭底色加满强清漆（coat 1.0 / 0.03），基础粗糙度 0.25；header 板叠印刷标签（油墨粗糙度 0.55）。",
          ["piano black lacquer", "deep gloss clear coat", "crisp reflections", "near-black charcoal base"],
          ["matte black", "plastic sheen", "dust or fingerprints"],
          "M_PDC_PianoBlack", lin("#1C1E22"), 0.05, 0.25,
          ["GEO_PDC_HEADER_GRAPHITE_PLANE (+ label decal)", "GEO_PDC_MAIN_TRAIT_PLAQUE", "GEO_PDC_POCKET_GRAPHITE_FLOOR"],
          {"coatWeight": 1.0, "coatRoughness": 0.03, "labelInkRoughness": 0.55}),
    entry("case-bright-mirror", "亮镜面银", "Bright mirror silver", "steel",
          "斜边、凹槽抛光唇等凸起抛光件的亮镜面：scheme A 以 #C9D0D6、粗糙度 0.04 取代规格烟色镜面 #667078；宽口径下随稀有度换金属。",
          ["bright mirror-polished steel", "razor-sharp reflections", "narrow polished bevels"],
          ["smoked mirror", "brushed", "visible grain"],
          "M_PDC_Mirror", lin("#C9D0D6"), 1, 0.04,
          ["GEO_PDC_HEADER_MIRROR_BEVEL", "GEO_PDC_MAIN_MIRROR_SEAM", "GEO_PDC_POCKET_POLISHED_LIP"],
          {"visibleGrain": False, "supersedesSpecBaseColorHex": "#667078"}),
    entry("case-champagne-gold-inlay", "香槟金饰条", "Champagne gold inlay", "gold",
          "Standard 档的金色饰条、竖轨与索引块：#C8B48B，各向异性 0.15，沿饰条长轴拉丝，永不成闭环。",
          ["champagne gold inlay", "fine directional brushing along the inlay", "restrained warm metal"],
          ["yellow gold", "mirror gold", "closed gold loop"],
          "M_PDC_AccentMetal", lin("#C8B48B"), 1, 0.26,
          ["GEO_PDC_*GOLD*"],
          {"anisotropic": 0.15, "brushingAxis": "inlay long axis (UV2.x)"}),
    entry("case-rose-bronze-tier", "玫瑰青铜档位金属", "Rose-bronze tier metal", "gold",
          "Refined 档（宽口径）：边框、抛光件与饰条整体换为低饱和玫瑰青铜，sRGB 0.70/0.58/0.52，饱和度约为原铜色 40%。",
          ["muted rose bronze", "low-saturation warm metal", "brushed on frames, polished on bevels"],
          ["orange copper", "saturated bronze", "rose gold jewelry pink"],
          "M_PDC_BrushedSteel_copper", lin_rgb([0.70, 0.58, 0.52]), 1, 0.30,
          ["bezels (5)", "polished parts (6)", "accents (7)", "liner tint (2)"],
          {"rarity": "Refined", "requirement": "FDB-DSP-059/061", "linerSrgb": [0.90, 0.86, 0.84]}),
    entry("case-grey-blue-titanium-tier", "灰蓝钛档位金属", "Grey-blue titanium tier metal", "steel",
          "Signature 档（宽口径）：灰蓝钛，sRGB 0.58/0.63/0.70，与 Standard 冷钢的差别只在偏蓝色相。",
          ["grey-blue titanium PVD", "cool desaturated metal", "brushed frames, polished bevels"],
          ["saturated blue", "cobalt", "chrome blue"],
          "M_PDC_BrushedSteel_titanium", lin_rgb([0.58, 0.63, 0.70]), 1, 0.30,
          ["bezels (5)", "polished parts (6)", "accents (7)", "liner tint (2)"],
          {"rarity": "Signature", "requirement": "FDB-DSP-059/061", "linerSrgb": [0.86, 0.88, 0.93]}),
    entry("case-champagne-tier", "香槟档位金属", "Champagne tier metal", "gold",
          "Heirloom 档（宽口径）：香槟色，sRGB 0.80/0.73/0.60，取代饱和黄金。",
          ["pale champagne metal", "warm desaturated gold", "brushed frames, polished bevels"],
          ["yellow gold", "brass", "saturated gold"],
          "M_PDC_BrushedSteel_gold", lin_rgb([0.80, 0.73, 0.60]), 1, 0.30,
          ["bezels (5)", "polished parts (6)", "accents (7)", "liner tint (2)"],
          {"rarity": "Heirloom", "requirement": "FDB-DSP-059/061", "linerSrgb": [0.90, 0.88, 0.90]}),
]


def main() -> None:
    # --- pipeline approval
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = {a["id"]: a for a in manifest["assets"]}
    s7 = next(s for s in manifest["stages"] if s["id"] == "07-material")
    assert s7["status"] == "ready_for_review" and s7["revision"] == 6
    report = json.loads((E07 / "material-revalidation.json").read_text())
    reviewed = [{"id": aid, "path": assets[aid]["path"], "sha256": assets[aid]["sha256"]} for aid in s7["reviewArtifactIds"] if aid in assets]
    s7["decision"] = {
        "state": "approved", "action": "approve", "decidedBy": "user", "decidedAt": DECIDED_AT, "channel": "chat", "wording": WORDING, "sourceId": SOURCE_ID,
        "requestedAs": "assistant 15:0x reply: 待你批准 Gate 07", "openArtifactAtApproval": "Artifacts/TriSpinnerSlab/gate07-r003/gate07-r003-material-id-vs-render.png",
        "interactionMode": "complete-neutral-turntable-recording + material board + id-vs-render sheet viewed in IDE",
        "reviewedArtifacts": reviewed, "governingContractSha256": report["contractSha256"], "contractRevision": 13,
        "parameterSnapshot": report["materials_by_zone"], "checklist": ["material board (hero/front/4 macros) viewed", "material-id vs render boundary sheet open at approval",
                                                                         "neutral turntable 72 f available", "four muted tiers viewed", "label copy acknowledged as placeholder"],
        "checklistComplete": True, "scope": "material language + boundaries approved at lookdev level; not a shipping-preview approval; nothing built or installed",
    }
    s7["status"] = "approved"; s7["approvedAt"] = NOW
    s8 = next(s for s in manifest["stages"] if s["id"] == "08-lighting")
    s8["status"] = "draft"; s8["variantId"] = VARIANT; s8.pop("staleReason", None)
    s8["nextStep"] = "beauty rig from contract rev-013 lighting.beauty on the approved Gate 07 materials: hero / left-right oblique / low, beauty-clean + beauty-soft, clay / normal / depth / roughness passes, calibrated"
    manifest["currentState"]["activeStageId"] = "08-lighting"; manifest["currentState"]["activeStageStatus"] = "draft"
    manifest["currentState"]["materialApproval"] = {"stageId": "07-material", "evidenceRevision": "rev-003", "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT}
    manifest["currentState"]["visualApproval"] = "gates-01-07 approved (lookdev level); Gate 08 lighting draft; shipping preview not yet produced"
    manifest["model"]["status"] = "v3-tri-spinner-slab-gates-01-07-approved-gate-08-draft"
    manifest["currentState"]["diagnosis"] += (f" 09-11 15:26 用户「{WORDING}」：Gate 07 rev-003 批准；9 条材质写入 MaterialLibrary（approved-gate07）；Gate 08 开为 draft。未推送手机。")
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1; manifest["updatedAt"] = NOW
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "variantId": VARIANT,
                                 "type": "user-approval", "stageId": "07-material", "revision": 6, "notes": WORDING, "sourceId": SOURCE_ID,
                                 "reviewedArtifactSha256": [r["sha256"] for r in reviewed], "governingContractSha256": report["contractSha256"]}, ensure_ascii=False) + "\n")
        handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "variantId": VARIANT,
                                 "type": "stage-opened", "stageId": "08-lighting", "notes": "Gate 07 approved; Gate 08 opened as draft."}, ensure_ascii=False) + "\n")

    # --- material library registration (after approval, per contract)
    lib = json.loads(LIB_PATH.read_text(encoding="utf-8"))
    if not any(f["id"] == "glass" for f in lib["families"]):
        lib["families"].append({"id": "glass", "label": "透明 / 半透明", "labelEn": "Glass & translucent"})
    ids = {m["id"] for m in lib["materials"]}
    added = []
    for m in NEW_MATERIALS:
        if m["id"] in ids:
            lib["materials"] = [m if x["id"] == m["id"] else x for x in lib["materials"]]
        else:
            lib["materials"].append(m); added.append(m["id"])
    steel = next(m for m in lib["materials"] if m["id"] == "steel-satin")
    if not any(u.get("variant") == VARIANT for u in steel.get("usedBy", [])):
        steel.setdefault("usedBy", []).append({"model": MODEL_ID, "variant": VARIANT, "parts": ["GEO_PDC_HEADER_SATIN_SHELF", "GEO_PDC_MAIN_SATIN_SHELF", "GEO_PDC_FRAME_BOLT_*"],
                                               "note": "library values verbatim + scheme-A anisotropy 0.8 / brushing along UV2.x (Gate 07 rev-003 approved 2026-09-11)"})
    lib["updatedAt"] = "2026-09-11"
    LIB_PATH.write_text(json.dumps(lib, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifestRevision": manifest["revision"], "gate07": s7["status"], "gate08": s8["status"], "libraryAdded": added, "libraryCount": len(lib["materials"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
