"""Refine Gate 02 rev-006 (still ready_for_review): add the surface detail atlas,
the machine-readable surface-detail-spec.json, the coverage gate-keeper and its
report against the historical builder. No stage revision change, no approval."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import register_geeone_video_intake_rev6 as base

REPO = base.REPO
A02 = base.A02
NOW = datetime.now(timezone.utc).isoformat()


def main() -> None:
    manifest = json.loads((base.PIPELINE_DIR / "pipeline.json").read_text(encoding="utf-8"))
    s02 = base.stage(manifest, "02-analysis")
    assert s02["revision"] == 6 and s02["status"] == "ready_for_review", (s02["revision"], s02["status"])
    added = []
    for aid, path, slot, role, cls, srcs, note in [
        ("tri-r6-surface-detail-atlas", A02 / "surface-detail-atlas.png", "analysis-board", "analysis", "surface-detail-atlas-D01-D10-from-frames", ["tri-r6-video-source"], "8 frames zoomed 2-4x with D01-D10 callouts"),
        ("tri-r6-surface-detail-spec", A02 / "surface-detail-spec.json", "analysis-measurements", "contract", "surface-detail-spec-machine-readable", ["tri-r6-surface-detail-atlas", "tri-r6-frame-measurements"], "carry-over list for future Gate 03-06; mustBeGeometry ids"),
        ("tri-r6-detail-coverage-checker", REPO / "tools/model-provenance-explorer/check_surface_detail_coverage.py", "analysis-board", "process", "gate05-06-gatekeeper-script", ["tri-r6-surface-detail-spec"], "exit 1 when a builder lacks any `# detail: UTS-Dxx` tag"),
        ("tri-r6-detail-coverage-current-builder", A02 / "detail-coverage-current-builder.json", "analysis-measurements", "validation", "coverage-report-historical-rev005-builder-0-of-10", ["tri-r6-detail-coverage-checker"], "historical builder covers 0/10; proves the gate blocks until rebuilt"),
    ]:
        base.upsert(manifest, base.asset(aid, "02-analysis", slot, path, role, cls, "repository-generated", "repository", srcs, note))
        added.append(aid)
    for p in sorted((A02 / "frame-zooms").glob("*.png")):
        if p.name.startswith("_"):
            continue
        aid = "tri-r6-zoom-" + p.stem
        if aid not in {a["id"] for a in manifest["assets"]}:
            base.upsert(manifest, base.asset(aid, "02-analysis", "analysis-board", p, "analysis", "frame-zoom-crop", "repository-generated", "repository", ["tri-r6-video-source"]))
            added.append(aid)
    for aid in added:
        if aid not in s02["artifactIds"]:
            s02["artifactIds"].append(aid)
    claim_id = "tri-r6-surface-detail-spec"
    if claim_id not in {c["id"] for c in manifest["claims"]}:
        manifest["claims"].append({
            "id": claim_id, "stageId": "02-analysis", "category": "geometry", "confidence": "medium", "recordedAt": NOW,
            "statement": "表面细节 D01–D10（平盘、冠环三角、盖裙第二排刻面、平台、叶边倒角鳞面带每边 5–7 平面、竖壁、叶尖脊、叶根凹坑、暗缝/缺口露盖、底面镜像）全部为真实几何要求，见 surface-detail-spec.json；未来 Blender builder 必须逐项以 `# detail: UTS-Dxx` 标记，check_surface_detail_coverage.py 覆盖率不足即阻断 Gate 05/06 登记。当前历史 builder 覆盖 0/10。",
            "sourceAssetIds": ["tri-r6-surface-detail-atlas", "tri-r6-surface-detail-spec", "tri-r6-frame-0148", "tri-r6-frame-0176", "tri-r6-frame-0077", "tri-r6-frame-0038"], "sourceRegions": [],
        })
    s02["validations"] = [v for v in s02["validations"] if v["id"] != "surface-detail-spec-present"] + [
        {"id": "surface-detail-spec-present", "status": "pass", "detail": "10 项 mustBeGeometry 细节 + gate-keeper 脚本；历史 builder 覆盖 0/10（预期阻断）"},
    ]
    base.update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    (base.PIPELINE_DIR / "pipeline.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (base.PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": base.MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW, "type": "stage-note", "stageId": "02-analysis", "notes": "rev-006 refined (still ready_for_review): surface detail atlas D01-D10, machine-readable spec, coverage gate-keeper (historical builder 0/10). User 2026-09-06 07:27 asked to restore surface details and guarantee carry-over into Blender."}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "added": added}))


if __name__ == "__main__":
    main()
