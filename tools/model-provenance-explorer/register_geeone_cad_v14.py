"""Refine Gate 02 rev-006 (still ready_for_review) after the user's 2026-09-07
11:47 feedback on shaded relief v14: (1) two spots beside the Y junction on the
blade top read as recessed -> the tent-of-crest-lines top is replaced by a
Y-shaped mesa with straight skirts (D04 v15); (2) the scale detail is still
wrong -> f0148/f0150/f0152 re-read at 10x: one band of interlocking light kite /
dark Λ pentagon facets with a deep zigzag, not two stacked rows (D05 v15).
Registers CAD v14, shaded relief v15, the shape comparison board, the user's
screenshot + exact wording, two superseding claims. No approvals, no gate
crossing, no workbench refresh.
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
USER_TEXT = "这两个地方凹下去了。然后鳞片的细节还是不对，你再仔细对照图片看一下。"


def supersede(manifest: dict, old_id: str, new_claim: dict) -> None:
    claims = {c["id"]: c for c in manifest["claims"]}
    if new_claim["id"] not in claims:
        manifest["claims"].append(new_claim)
    old = claims.get(old_id)
    if old is not None and old.get("supersededBy") != new_claim["id"]:
        old["state"] = "superseded"
        old["supersededBy"] = new_claim["id"]
        old["supersededAt"] = NOW


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review"

    # Gate 01: store key frame f0152 (cited by D05 v15) next to f0148/f0150, hash it into the intake record.
    s01 = base.stage(manifest, "01-intake")
    key_dir = base.A01 / "frames10-key"
    frame = key_dir / "f_0152.jpg"
    if not frame.exists():
        shutil.copy2(Path("/tmp/dragon-scale-gate02/video/frames10/f_0152.jpg"), frame)
    rec_path = base.A01 / "intake-record.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    fe = rec["frameExtraction"]
    if 152 not in fe["storedKeyFrames"]:
        fe["storedKeyFrames"] = sorted(set(fe["storedKeyFrames"]) | {152})
    fe["storedKeyFrameSha256"]["f_0152.jpg"] = base.sha256(frame)
    rec_path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-frame-0152", "01-intake", "original-reference", frame, "external-reference", "video-frame-extract-t15.1s", "external", "repository", ["tri-r6-video-source"], "ffmpeg fps=10 frame, unmodified"))
    base.upsert(manifest, base.asset("tri-r6-intake-record", "01-intake", "source-metadata", rec_path, "process", "intake-record-with-hashes-and-frame-command", "repository-generated", "repository", ["tri-r6-video-source"]))
    if "tri-r6-frame-0152" not in s01["artifactIds"]:
        s01["artifactIds"].append("tri-r6-frame-0152")

    shot = A02 / "user-screenshot-2026-09-07-1147-two-dents-scale-detail.png"
    if not shot.exists():
        shutil.copy2(ASSETS_IN / "image-fe40358c-43a6-425a-a72e-7ea21b3201ac.png", shot)
    instr = A02 / "user-instructions-2026-09-07-1147.md"
    instr.write_text(
        "# 用户指令 2026-09-07 11:47（原话）\n\n"
        f"> {USER_TEXT}\n\n"
        "附图：shaded-relief-v14.png ⑥ 右下叶放大的局部，两个红圈分别在 Y 形交点两侧（柄与上臂之间、柄与下臂之间）。\n\n"
        "解读（Gate 02 rev-006 v15）：\n"
        "- “这两个地方凹下去了”：v9–v14 把叶顶做成三条脊线的帐篷面（z = 脊高·d_low/(d_low+d_crest)），柄与两臂之间形成谷。"
        "改为 **Y 形平顶隆起**：顶区平、四周直斜裙（≈0.09 R 占位）落到鳞带边和坑边，柄臂之间保持高位、无谷（D04 v15）。\n"
        "- “鳞片的细节还是不对”：f0148/f0150/f0152 10× 复核——叶侧不是两排叠放的浅锯齿，而是**一道深锯齿咬合**：亮“鸢形”自顶面边下垂（较缓，≈42° 占位，V 尖到带宽 ≈85%），"
        "暗“Λ 形”自中面上升（较陡，≈56° 占位，尖到 ≈25%），每边 4–5 片鸢形、节距 ≈0.18 R，每片独立平面、硬折边（D05 v15）。\n\n"
        "状态：Gate 01/02 仍 ready_for_review；无任何批准；视觉批准待确认，未推送手机。\n",
        encoding="utf-8",
    )
    added = []
    for aid, path, slot, role, cls, origin, by, srcs, note in [
        ("tri-r6-user-screenshot-two-dents", shot, "analysis-board", "user-input", "user-screenshot-shaded-relief-v14-blade-top-dents", "user-provided", "user", ["tri-r6-shaded-relief-v14"], "用户 09-07 11:47：Y 交点两侧两处凹下去 + 鳞片细节不对"),
        ("tri-r6-user-instructions-1147", instr, "analysis-board", "user-input", "user-instruction-exact-wording-2026-09-07-1147", "user-provided", "user", [], "原话 + 解读"),
        ("tri-r6-blade-scale-shape-evidence", A02 / "blade-scale-shape-v14-vs-v15.png", "analysis-board", "analysis", "evidence-blade-side-kite-lambda-f0148-10x-vs-v14-vs-v15", "repository-generated", "repository", ["tri-r6-frame-0148", "tri-r6-shaded-relief-v14", "tri-r6-user-instructions-1147"], "f0148 10× 鳞片形状 vs v14 vs v15"),
        ("tri-r6-cad-v14-script", REPO / "tools/model-provenance-explorer/draw_geeone_reference_cad_v14.py", "analysis-board", "process", "reference-cad-v14-script", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1147"], ""),
        ("tri-r6-reference-cad-v14", A02 / "reference-cad-from-video-v14.png", "structural-cad", "analysis", "reference-cad-v14-kite-lambda-scales-y-mesa", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1147", "tri-r6-user-screenshot-two-dents", "tri-r6-blade-scale-shape-evidence"], "v14 is the current reference CAD; v1-v13 history"),
        ("tri-r6-reference-cad-v14-pdf", A02 / "reference-cad-from-video-v14.pdf", "structural-cad", "analysis", "reference-cad-v14-vector", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-user-instructions-1147"], "v14 vector"),
        ("tri-r6-shaded-relief-v15", A02 / "shaded-relief-v15.png", "analysis-board", "analysis", "shaded-relief-height-field-illustration", "repository-generated", "repository", ["tri-r6-surface-detail-spec", "tri-r6-reference-cad-v14", "tri-r6-user-instructions-1147"], "2.5D hillshade + relative-height map; blade side = interlocking kite/Λ planar facets, one deep zigzag; blade top = Y mesa with straight skirts (no valleys); not a blockout, not a render; heights provisional"),
        ("tri-r6-shaded-relief-v15-script", REPO / "tools/model-provenance-explorer/shade_geeone_reference_v15.py", "analysis-board", "analysis", "shaded-relief-script", "repository-generated", "repository", ["tri-r6-cad-v14-script"], ""),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", "repository-generated", "repository", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements", "tri-r6-user-instructions-2046", "tri-r6-user-instructions-0753", "tri-r6-user-instructions-0825", "tri-r6-user-instructions-0839", "tri-r6-user-instructions-0936", "tri-r6-user-instructions-1040", "tri-r6-user-instructions-1055", "tri-r6-user-instructions-1110", "tri-r6-user-instructions-1147"], "carry-over list for future Gate 03-06; mustBeGeometry ids; v7 planform, D01 14-sector dish, D04 v15 Y mesa, D02/D03 cap-edge three tiers, D05 v15 kite/Λ interlocking blade-side facets"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, origin, by, srcs, note))
        added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    for a in manifest["assets"]:
        if a["id"] in ("tri-r6-reference-cad-v13", "tri-r6-reference-cad-v13-pdf", "tri-r6-cad-v13-script"):
            a["provenance"]["note"] = "v13 — superseded by tri-r6-reference-cad-v14 (kite/Λ interlocking blade-side facets, Y mesa top); kept as history"
        if a["id"] in ("tri-r6-shaded-relief-v14", "tri-r6-shaded-relief-v14-script"):
            a["provenance"]["note"] = "v14 — superseded by tri-r6-shaded-relief-v15 (user 11:47: two dents beside the Y junction; scale detail); kept as history"

    mesa = {
        "id": "tri-r6f-blade-top-y-mesa", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (Y layout + no valleys: user drawing 08:39, user 11:47, f0108/f0132) / unknown (rise, skirt width)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片顶面是 Y 形**平顶隆起**，不是三条脊线的帐篷面：顶区平，四周以直斜裙（宽 ≈0.09 R 占位）落到 D05 鳞带边与 D08 坑边；因凹坑在叉内，顶区在顶视上呈 Y 形（柄沿叶轴、近叶尖收成一条脊；两臂在坑侧与叶边之间）。柄与两臂之间保持高位，**没有谷/鞍**——用户 2026-09-07 11:47 在阴影图 v14 的 Y 交点两侧圈出两处“凹下去了”，即 v9–v14 帐篷模型（z = 脊高·d_low/(d_low+d_crest)）在脊线之间产生的谷。脊高 ≈0.025 R 仍为占位。取代 tri-r6f-blade-top-y-ridge。",
        "sourceAssetIds": ["tri-r6-user-screenshot-two-dents", "tri-r6-user-instructions-1147", "tri-r6-user-screenshot-blade-top-y", "tri-r6-user-instructions-0839", "tri-r6-frame-0108", "tri-r6-frame-0132", "tri-r6-reference-cad-v14", "tri-r6-shaded-relief-v15"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    kite = {
        "id": "tri-r6f-blade-side-kite-lambda-interlock", "stageId": "02-analysis", "category": "geometry", "confidence": "medium (kite/Λ interlock, 4-5 per edge, no wall: f0148/f0150/f0152 10× + user) / low (slopes 42°/56°, tip depths 25%/85%, twist)", "recordedAt": NOW, "sourceRegions": [],
        "statement": "叶片侧面从顶面到中面是**一道**互相咬合的平面五边形刻面带（下半镜像 D10），不是两排叠放的浅锯齿：f0148/f0150/f0152 10× 显示亮“鸢形”自顶面边下垂（顶边宽、两侧短竖边、V 尖朝下到带宽 ≈85%，较缓 ≈42° 占位，顶光下亮）与暗“Λ 形”自中面上升（底边在中面、尖朝上到带宽 ≈25%，较陡 ≈56° 占位，暗）沿叶边交替、共用斜折边，形成一道几乎贯穿侧面高度的深锯齿；每边 4–5 片鸢形、节距 ≈0.18 R；每片独立平面、硬折边、锯齿偏离两面交线处成细棱；带径向宽 ≈0.07 R（f0077）；无独立竖壁（D06≈0）。用户 2026-09-07 11:47：“鳞片的细节还是不对，你再仔细对照图片看一下”。取代 tri-r6f-blade-side-two-rows-to-midplane（其“2 排”即鸢形与 Λ 两族被当成了两排）。",
        "sourceAssetIds": ["tri-r6-frame-0148", "tri-r6-frame-0150", "tri-r6-frame-0152", "tri-r6-blade-scale-shape-evidence", "tri-r6-user-instructions-1147", "tri-r6-user-instructions-1110", "tri-r6-reference-cad-v14", "tri-r6-shaded-relief-v15"],
        "refines": ["tri-r6-surface-detail-spec"],
    }
    supersede(manifest, "tri-r6f-blade-top-y-ridge", mesa)
    supersede(manifest, "tri-r6f-blade-side-two-rows-to-midplane", kite)
    doc_path = A02 / "claims-rev6.json"
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    have = {c["id"] for c in doc["claims"]}
    for c in (mesa, kite):
        if c["id"] not in have:
            doc["claims"].append(c)
    for c in doc["claims"]:
        if c["id"] == "tri-r6f-blade-top-y-ridge":
            c.update({"state": "superseded", "supersededBy": mesa["id"], "supersededAt": NOW})
        if c["id"] == "tri-r6f-blade-side-two-rows-to-midplane":
            c.update({"state": "superseded", "supersededBy": kite["id"], "supersededAt": NOW})
    doc["recordedAt"] = NOW
    doc_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.upsert(manifest, base.asset("tri-r6-claims-doc", "02-analysis", "analysis-board", doc_path, "analysis", "claims-with-supersessions-and-open-conflicts", "repository-generated", "repository", ["tri-r6-frame-measurements", "tri-r6-surface-detail-spec"]))

    s02["validations"] = [v for v in s02["validations"] if v["id"] not in ("blade-top-structure", "blade-edge-scale-rows", "blade-scale-facet-style")] + [
        {"id": "blade-top-structure", "status": "pass", "detail": "D04 v15 = Y 形平顶隆起（顶平 + 直斜裙 0.09 R 占位），柄臂之间无谷；用户 11:47 两处凹陷已消除（阴影图 v15）；claim tri-r6f-blade-top-y-mesa 取代 y-ridge"},
        {"id": "blade-edge-scale-rows", "status": "pass", "detail": "D05 v15 = 亮鸢形（自顶面边下垂 42° 占位）与暗 Λ（自中面上升 56° 占位）一道深锯齿咬合，每边 4–5 片鸢形 0.18 R 节距；f0148/f0150/f0152 10×；CAD v14 Detail H；claim tri-r6f-blade-side-kite-lambda-interlock"},
        {"id": "blade-scale-facet-style", "status": "pass", "detail": "每片鸢形/Λ 独立平面、硬折边（用户 11:10 硬朗）；阴影图 v15；spec D05 facetStyle planar+hardCreases；Gate 06 check 已改为鸢形/Λ 判据"},
    ]
    manifest["currentState"]["diagnosis"] = (
        manifest["currentState"]["diagnosis"].split(" | 09-07 11:47 v15:")[0]
        + " | 09-07 11:47 v15: 用户圈出 Y 交点两侧两处凹陷 + 鳞片细节不对 → D04 改 Y 形平顶隆起（无谷）；D05 改亮鸢形/暗 Λ 一道深锯齿咬合（f0148/f0150/f0152 10×）；CAD v14 + 阴影图 v15 + 形状对照板。Gate 01/02 ready_for_review；视觉批准待确认，未推送手机；等待用户 Gate 审批。"
    )
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
            "type": "stage-note", "stageId": "02-analysis",
            "notes": "rev-006 refined (still ready_for_review): CAD v14 + shaded relief v15 — D04 blade top = Y mesa with straight skirts (no valleys beside the junction); D05 blade side = interlocking light kite / dark Λ planar facets with one deep zigzag (42°/56°, tips 85%/25% of band, 4-5 kites per edge, all provisional) from f0148/f0150/f0152 at 10x; claims tri-r6f-blade-top-y-mesa and tri-r6f-blade-side-kite-lambda-interlock supersede y-ridge and two-rows-to-midplane. User 2026-09-07 11:47 exact wording: " + USER_TEXT,
        }, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}, ensure_ascii=False))


if __name__ == "__main__":
    main()
