"""User 2026-09-07 19:42 on lookdev rev-002: "质感挺漂亮的，但是中间你那个切分的细节又丢了。就是从圆心，大概就是像切披萨一样切成了14片，
这个细节又没有了，而且它是应该是向内凹一点的。"

Bookkeeping for the D01 visibility amendment:
  * Gate 02 rev-006 stays approved; surface-detail-spec D01 v19 (dish 5°, ±0.5° alternate sector tilt, crease bevel 0) is
    registered as a user-requested amendment with the exact wording. Gate 03 / 05 stay approved with a warn that the cap
    block of the contract was regenerated in 06-geometry/rev-006 (dish 3° -> 5°); the user asked for no new white model.
  * Gate 06 -> rev-006 (caps rebuilt from the amended contract, manifold, 9 checks) ready_for_review.
  * Gate 07/08/09 -> rev-003 (disc anisotropy 0.7 -> 0.4, softer turning bump, new disc-macro view, turntable) ready_for_review.
Nothing downstream is approved; no export, Unity, build, install.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import register_geeone_video_intake_rev6 as base

EV = base.EV
NOW = datetime.now(timezone.utc).isoformat()
USER_TEXT = "质感挺漂亮的，但是中间你那个切分的细节又丢了。就是从圆心，大概就是像切披萨一样切成了14片，这个细节又没有了，而且它是应该是向内凹一点的。"
AMEND = "user 2026-09-07 19:42 D01 amendment (dish 3°→5°, alternate sector tilt ±0.5° provisional, crease bevel 0)"


def new_revision(stage, rev, reason):
    if stage["revision"] != rev:
        stage.setdefault("historicalRevisions", []).append({"revision": stage["revision"], "artifactIds": list(stage["artifactIds"]), "status": stage["status"], "reason": reason})
        stage["revision"] = rev
        stage["artifactIds"] = []
        stage.pop("staleReason", None)
    stage["decision"] = None


def set_validation(stage, vid, status, detail):
    stage["validations"] = [v for v in stage.get("validations", []) if v["id"] != vid] + [{"id": vid, "status": status, "detail": detail}]


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    st = {s["id"]: s for s in manifest["stages"]}

    # ---- Gate 02: D01 v19 amendment (spec hash refresh + user wording)
    A02 = EV / "02-analysis/rev-006"
    spec_asset = next(a for a in manifest["assets"] if a["id"] == "tri-r6-surface-detail-spec")
    base.upsert(manifest, base.asset("tri-r6-surface-detail-spec", "02-analysis", spec_asset["slot"], A02 / "surface-detail-spec.json", spec_asset["role"], spec_asset["provenance"]["contentClass"], "repository-generated", "repository", spec_asset.get("sourceAssetIds", []) + ["tri-r6-user-instructions-1942"], spec_asset["provenance"]["note"] + "; v19 D01 dish 5° provisional + sectorAltTiltDeg 0.5 provisional + crease bevel 0 (user 19:42)"))
    base.upsert(manifest, base.asset("tri-r6-user-instructions-1942", "02-analysis", "analysis-board", A02 / "user-instructions-2026-09-07-1942.md", "user-input", "user-instruction-exact-wording-2026-09-07-1942", "user-provided", "user", ["tri-r6i-lookdev-board"], USER_TEXT))
    for aid in ("tri-r6-user-instructions-1942",):
        if aid not in st["02-analysis"]["artifactIds"]:
            st["02-analysis"]["artifactIds"].append(aid)
    set_validation(st["02-analysis"], "d01-amended-1942", "warn", f"{AMEND}; visibility fix of the already-approved 14-sector concave dish, authorised by the user's wording; Gate 02 approval kept, no re-approval requested")
    set_validation(st["03-contract"], "cap-block-amended-1942", "warn", "contract cap block regenerated in 06-geometry/rev-006 with spec v19 (dishSlopeDeg 5, sectorAltTiltDeg 0.5, sectorCreaseHighlightBevelMm 0); 03-contract/rev-005 copy is the approved history (dish 3°)")
    set_validation(st["05-blockout"], "cap-dish-amended-1942", "warn", "white model rev-007 caps are the approved 3° dish; Gate 06 rev-006 rebuilds the caps from the amended contract (5°, ±0.5°); user asked for no new white model")

    # ---- Gate 06 rev-006
    s06 = st["06-geometry"]
    new_revision(s06, 6, "user 2026-09-07 19:42: 14 pizza slices not readable, dish not concave enough -> caps rebuilt")
    s06["status"] = "ready_for_review"
    A06 = EV / "06-geometry/rev-006"
    checks = json.loads((A06 / "gate06-checks.json").read_text(encoding="utf-8"))
    cap = checks["cap"]
    assets06 = [
        ("tri-r6j-g06-contract", A06 / "geeone-gate02-geometry-contract.json", "geometry-source", "contract", "gate02-geometry-contract-r-units", ["tri-r6-surface-detail-spec", "tri-r6h-geometry-contract"], "spec v19 hash-linked; cap dishSlopeDeg 5 / sectorAltTiltDeg 0.5 / crease bevel 0"),
        ("tri-r6j-g06-script", A06 / "finalize_geeone_geometry.py", "geometry-source", "process", "bpy-geometry-finalizer", ["tri-r6h-blend", "tri-r6j-g06-contract"], "apply booleans → 坑口沿凸圆角 → 0.15 mm 微倒角 → caps rebuilt: 14 planar sectors from a lowered apex, zigzag rim ±0.033 mm (±0.5° tilt), tiers grown from the rim (manifold)"),
        ("tri-r6j-g06-blend", A06 / "geeone-geometry-r006.blend", "geometry-source", "source-model", "geometry-blend-r006", ["tri-r6j-g06-script"], f"Rotor_Body {checks['rotor_final']['verts']} verts / {checks['rotor_final']['faces']} faces / 0 non-manifold; Cap_Top/Bottom 57 verts / 99 faces / 0 non-manifold; dish {cap['dish_slope_deg']}° = {cap['dish_depth_mm']} mm provisional"),
        ("tri-r6j-g06-checks", A06 / "gate06-checks.json", "geometry-validation", "process", "gate06-numeric-checks", ["tri-r6j-g06-blend"], json.dumps(checks["gate06Check_results"], ensure_ascii=False)),
    ]
    for name in ("top-ortho", "hero", "pocket-macro", "edge-macro", "notch-macro", "low"):
        assets06.append((f"tri-r6j-g06-check-{name}", A06 / "checks" / f"{name}.png", "geometry-preview", "analysis", f"workbench-{name}", ["tri-r6j-g06-blend"], ""))
    for aid, path, slot, role, cls, srcs, note in assets06:
        base.upsert(manifest, base.asset(aid, "06-geometry", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        s06["artifactIds"].append(aid)
    s06["validations"] = [{"id": k.replace(" ", "-").replace("/", "-").replace(",", "").replace("<", "lt").replace("(", "").replace(")", "").replace(">=", "ge"), "status": "pass" if v else "fail", "detail": k} for k, v in checks["gate06Check_results"].items()] + [
        {"id": "surface-detail-coverage", "status": "pass", "detail": "builder rev-007 10/10 + finalizer tags D01–D05, D08, D10"},
        {"id": "mouth-fillet-edges", "status": "pass", "detail": f"{checks['pocket_mouth_fillet']['tagged_edges']} 条坑口边打权重，R {checks['pocket_mouth_fillet']['radius_mm']} mm × 6 段"},
        {"id": "d01-slices-visible", "status": "pass", "detail": "14 sectors read in Cycles disc-macro / cap-macro (lookdev rev-003: tonal steps + hard creases + visible dish); dish 5° and ±0.5° alternate tilt stay provisional/unmeasured — visual approval tracked at Gate 07"},
    ]

    # ---- Gate 07 / 08 / 09 rev-003
    A07 = EV / "07-material/rev-003"
    for sid in ("07-material", "08-lighting", "09-environment"):
        new_revision(st[sid], 3, "user 2026-09-07 19:42: material direction accepted ('质感挺漂亮的'), disc slices not readable -> disc material re-tuned on geometry rev-006")
        st[sid]["status"] = "ready_for_review"
    common = [
        ("tri-r6j-lookdev-script", A07 / "lookdev_geeone.py", "material-source", "process", "bpy-lookdev-materials-lights-environment", ["tri-r6j-g06-blend", "tri-r6i-lookdev-script"], "disc anisotropic 0.7→0.4, ring bump 0.25→0.12 (no distortion); lights / world / floor unchanged from rev-002; new disc-macro view"),
        ("tri-r6j-lookdev-blend", A07 / "geeone-lookdev-r003.blend", "material-source", "source-model", "lookdev-blend-r003", ["tri-r6j-lookdev-script"], ""),
        ("tri-r6j-lookdev-board", A07 / "renders" / "lookdev-review-board.png", "material-preview", "analysis", "lookdev-review-board", ["tri-r6j-lookdev-blend"], "七视图评审板（含 disc-macro）"),
        ("tri-r6j-cap14-board", A07 / "renders" / "cap-14-slices-review-board.png", "material-preview", "analysis", "cap-14-slices-before-after-reference", ["tri-r6j-lookdev-blend", "tri-r6-user-screenshot-disc-14", "tri-r6i-lookdev-cap-macro"], "参考截图 vs rev-002 vs rev-003 盘"),
        ("tri-r6j-lookdev-turntable-mp4", A07 / "turntable" / "geeone-lookdev-turntable.mp4", "material-preview", "analysis", "turntable-recording-36-frames", ["tri-r6j-lookdev-blend"], "36 帧 / 12 fps 转台（Gate 07–09 交互替代证据）"),
        ("tri-r6j-lookdev-turntable-gif", A07 / "turntable" / "geeone-lookdev-turntable.gif", "material-preview", "analysis", "turntable-gif", ["tri-r6j-lookdev-turntable-mp4"], ""),
    ]
    for name in ("hero", "top-ortho", "low", "blade-macro-f0132", "cap-macro", "disc-macro", "edge-macro"):
        common.append((f"tri-r6j-lookdev-{name}", A07 / "renders" / f"{name}.png", "material-preview", "analysis", f"cycles-{name}", ["tri-r6j-lookdev-blend"], "Cycles 96 spp 1400 px"))
    for aid, path, slot, role, cls, srcs, note in common:
        base.upsert(manifest, base.asset(aid, "07-material", slot, path, role, cls, "repository-generated", "repository", srcs, note))
    for sid in ("07-material", "08-lighting", "09-environment"):
        for aid, *_ in common:
            if aid not in st[sid]["artifactIds"]:
                st[sid]["artifactIds"].append(aid)
    st["07-material"]["validations"] = [
        {"id": "satin-not-mirror", "status": "pass", "detail": "M_Steel_Satin roughness 0.36 metallic 1（用户 09-05：satin 0.3–0.4；用户 09-07 19:42：质感挺漂亮的）"},
        {"id": "anisotropy-disc-only", "status": "pass", "detail": "M_Disc_Turned anisotropic 0.4 径向 + 0.12 mm 同心 bump（0.12 强度）仅在 14 扇区盘面；楔/鳞靠几何法线"},
        {"id": "d01-slices-read", "status": "pass", "detail": "disc-macro / cap-macro：14 个平面扇区有明暗台阶、硬折边、盘凹可见"},
        {"id": "hub-seat-dark", "status": "pass", "detail": "M_Hub_Dark 0.06 金属；暗缝 = 外悬下阴影"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认，未推送手机"},
    ]
    st["08-lighting"]["validations"] = [
        {"id": "three-light-studio", "status": "pass", "detail": "Key 2.4×1.6 R 暖白 / Fill 冷白 / Rim 细条（刻面星芒）；功率 ×250（mm 场景）；渐变天空 0.035→0.30；rev-003 未改"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]
    st["09-environment"]["validations"] = [
        {"id": "matte-floor-contact-shadow", "status": "pass", "detail": "哑光深灰地面，产品悬 2 mm，软接触阴影；无 HDRI 贴图；rev-003 未改"},
        {"id": "visual-approval-pending", "status": "warn", "detail": "视觉批准待确认"},
    ]

    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 19:42 cap-14:")[0]
        + " | 09-07 19:42 cap-14: 用户“质感挺漂亮的，但是中间你那个切分的细节又丢了…像切披萨一样切成了14片…应该是向内凹一点的”→ spec D01 v19（盘凹 3°→5°、相邻扇区 ±0.5° 交替倾角 provisional、折边不倒角）；Gate 06 rev-006 盖重建（流形，9 项检查全过）ready_for_review；Gate 07/08/09 rev-003（盘各向异性 0.7→0.4、同心 bump 减弱、新增 disc-macro 参考角视图 + 36 帧转台）ready_for_review；Gate 02/03/05 保持 approved 并标 warn（D01 修订）。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        events = [
            {"type": "stage-note", "stageId": "02-analysis", "notes": f"user 2026-09-07 19:42 (exact wording: {USER_TEXT}) -> surface-detail-spec D01 v19: dishSlopeDegProvisional 5, sectorAltTiltDegProvisional 0.5, sectorCreaseHighlightBevelMm 0; Gate 02 approval kept (visibility amendment of the approved 14-sector concave dish)"},
            {"type": "stage-revised", "stageId": "06-geometry", "notes": "06-geometry rev-006 ready_for_review: caps rebuilt from the amended contract (dish 5° = 1.48 mm provisional, alternate sectors ±0.5°, sharp creases), Cap_Top/Bottom manifold; gate06 checks: " + json.dumps(checks["gate06Check_results"], ensure_ascii=False)},
            {"type": "stage-revised", "stageId": "07-material", "notes": "07-material rev-003 ready_for_review: disc anisotropy 0.7->0.4, turning bump 0.25->0.12, 14 sectors read in disc-macro/cap-macro; Cycles renders + 36-frame turntable on geometry rev-006"},
            {"type": "stage-revised", "stageId": "08-lighting", "notes": "08-lighting rev-003 ready_for_review: unchanged three-area-light studio + gradient sky, re-rendered on geometry rev-006"},
            {"type": "stage-revised", "stageId": "09-environment", "notes": "09-environment rev-003 ready_for_review: unchanged matte floor + contact shadow, re-rendered on geometry rev-006"},
        ]
        for ev in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, **ev}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "statuses": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
