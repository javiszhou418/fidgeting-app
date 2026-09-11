"""Persist the user's chat approval of tri-spinner-slab-v3-cmf Gates 03-05 at rev-012.

User 2026-09-11 08:5x, asked whether "继续" meant approving Gates 03-06, chose the option
"批准 03–05（设计），06 精模我还要再看". Gates 03 r16 / 04 r43 / 05 r16 become approved; Gate 06
r10 stays ready_for_review.

(Original rev-011 docstring follows.)

User 2026-09-10 21:17 (UTC+8), with gate05-r011-cmf-preview-turntable-clear.mp4 open in the
IDE: "这版通过了". The assistant had asked for "批准 Gate 03/04/05" after presenting rev-011, so
the wording is applied to 03-contract r15, 04-architecture r42 and 05-blockout r15. Gates
01-02 are left ready_for_review until the user answers the follow-up question; Gate 06 opens
as draft only after that.

Each approval records the reviewed artifacts with SHA-256, the governing contract SHA-256,
the parameter snapshot, the viewing checklist, the interaction mode and the chat timestamp.
Blockout approval is not a shipping-preview approval: nothing is copied into DesignBibleAssets
and nothing is built or installed.

Usage: python3 register_tri_spinner_slab_v3_rev011_approval.py [--include-gates-01-02]
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODEL_ID = "premium-display-case"
VARIANT = "tri-spinner-slab-v3-cmf"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
C03 = PIPELINE_DIR / "evidence/03-contract/rev-012"
NOW = datetime.now(timezone.utc).isoformat()
WORDING = "批准 03–05（设计），06 精模我还要再看"
PRECEDING_WORDING = "继续"
DECIDED_AT = "2026-09-11T08:58:00+08:00"
SOURCE_ID = "src.user_gate03_05_rev012_approval_20260911"
SOURCE_ID_0102 = "src.user_gate01_02_approval_20260910"
WORDING_0102 = "一并通过，开 Gate 06（推荐）"          # AskQuestion option chosen 2026-09-10 21:2x after "这版通过了"
DECIDED_AT_0102 = "2026-09-10T21:25:00+08:00"
INCLUDE_01_02 = False
GATES = ["03-contract", "04-architecture", "05-blockout"]
CHECKLIST = {
    "01-intake": ["spec + handoff files read back to the user", "intake source hashes recorded"],
    "02-analysis": ["spinner source GLB measured (65 mm tip circle)", "V3 concept proportions measured on the clean image", "analysis board viewed"],
    "03-contract": ["35/35 assertions pass", "key values reviewed (case 101.28 x 171.78 mm kept, bands 2.80 mm, chamfers 3.5 mm, pocket centre -20.68 mm)",
                    "07:57 refinements + magnitude choices recorded with wording"],
    "04-architecture": ["architecture board viewed", "33 core parts match the contract", "divider / trait fills retired; no explode view in review artifacts"],
    "05-blockout": ["CMF turntable recording (72 f) open in the IDE at approval time", "workbench turntable recording (72 f) available",
                    "rev-011 vs rev-012 front/hero comparison viewed", "muted four-tier sheet viewed", "clean / soft pair rendered (soft = Gate 08 only)"],
}


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


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = {a["id"]: a for a in manifest["assets"]}
    contract = json.loads((C03 / "modeling-contract.json").read_text())
    contract_sha = contract["hashing"]["contract_sha256"]
    snapshot = json.loads((C03 / "contract-validation.json").read_text())["resolved_key_values_mm"]
    events = []
    for sid in GATES:
        s = next(x for x in manifest["stages"] if x["id"] == sid)
        if s["status"] == "approved" and (s.get("decision") or {}).get("sourceId") in (SOURCE_ID, SOURCE_ID_0102):
            continue                                   # idempotent re-run
        assert s["status"] == "ready_for_review" and s.get("variantId") == VARIANT, (sid, s["status"])
        reviewed = []
        for aid in s.get("reviewArtifactIds", []):
            a = assets.get(aid)
            if a:
                reviewed.append({"id": aid, "path": a["path"], "sha256": a["sha256"]})
        early = sid in ("01-intake", "02-analysis")
        s["decision"] = {
            "state": "approved", "action": "approve", "decidedBy": "user", "decidedAt": DECIDED_AT_0102 if early else DECIDED_AT, "channel": "chat",
            "wording": WORDING_0102 if early else WORDING, "precedingWording": WORDING if early else None,
            "sourceId": SOURCE_ID_0102 if early else SOURCE_ID, "requestedAs": "AskQuestion after the user's 08:56 “继续” (option chosen; Gate 06 explicitly withheld)",
            "precedingUserMessage": PRECEDING_WORDING, "withheld": "06-geometry rev-010 (“06 精模我还要再看”)",
            "interactionMode": "complete-recording-and-stills-viewed-in-ide" if sid == "05-blockout" else "documents-and-boards-viewed-in-chat",
            "openArtifactAtApproval": "Artifacts/TriSpinnerSlab/gate05-r012/gate05-r012-cmf-preview-turntable-clear.mp4",
            "reviewedArtifacts": reviewed, "governingContractSha256": contract_sha, "contractRevision": contract["contractRevision"],
            "parameterSnapshotMm": snapshot, "checklist": CHECKLIST[sid], "checklistComplete": True,
            "scope": "blockout-level approval of geometry, CMF zones, lighting direction, soft-focus level and muted rarity palette; not a shipping-preview approval; "
                     "nothing built or installed",
        }
        s["status"] = "approved"
        s["approvedAt"] = NOW
        events.append({"type": "user-approval", "stageId": sid, "revision": s["revision"], "notes": WORDING_0102 if early else WORDING, "sourceId": SOURCE_ID_0102 if early else SOURCE_ID,
                       "reviewedArtifactSha256": [r["sha256"] for r in reviewed], "governingContractSha256": contract_sha})
    all_upstream_approved = all(next(x for x in manifest["stages"] if x["id"] == sid)["status"] == "approved"
                                for sid in ("01-intake", "02-analysis", "03-contract", "04-architecture", "05-blockout"))
    if all_upstream_approved:
        manifest["currentState"]["activeStageId"] = "06-geometry"; manifest["currentState"]["activeStageStatus"] = "ready_for_review"
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = "v3-tri-spinner-slab-gates-01-05-approved-rev012-gate-06-rev010-pending"
    manifest["currentState"]["visualApproval"] = "gates-01-05 approved (rev-012 design level); gate-06 rev-010 awaiting the user's own review; shipping preview not yet produced"
    manifest["currentState"]["contractApproval"] = {"stageId": "03-contract", "contractRevision": contract["contractRevision"], "evidenceRevision": "rev-012",
                                                    "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT, "contractSha256": contract_sha}
    manifest["currentState"]["architectureApproval"] = {"stageId": "04-architecture", "evidenceRevision": "rev-034", "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT}
    manifest["currentState"]["blockoutApproval"] = {"stageId": "05-blockout", "evidenceRevision": "rev-012", "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT,
                                                    "openArtifact": "Artifacts/TriSpinnerSlab/gate05-r012/gate05-r012-cmf-preview-turntable-clear.mp4"}
    manifest["currentState"]["diagnosis"] += (f" 09-11 08:5x 用户「{WORDING}」（前一句「{PRECEDING_WORDING}」）：Gate 03–05 rev-012 批准（设计级）；Gate 06 rev-010 用户保留再看，仍 ready_for_review。未构建、未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                     "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "approved": GATES, "gate06": "draft" if all_upstream_approved else "stale",
                      "stages": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
