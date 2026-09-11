"""Persist the user's chat approval of tri-spinner-slab-v3-cmf Gates 03-05 at rev-011.

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
C03 = PIPELINE_DIR / "evidence/03-contract/rev-011"
NOW = datetime.now(timezone.utc).isoformat()
WORDING = "这版通过了"
DECIDED_AT = "2026-09-10T21:17:00+08:00"
SOURCE_ID = "src.user_gate03_05_rev011_approval_20260910"
SOURCE_ID_0102 = "src.user_gate01_02_approval_20260910"
WORDING_0102 = "一并通过，开 Gate 06（推荐）"          # AskQuestion option chosen 2026-09-10 21:2x after "这版通过了"
DECIDED_AT_0102 = "2026-09-10T21:25:00+08:00"
INCLUDE_01_02 = "--include-gates-01-02" in sys.argv
GATES = (["01-intake", "02-analysis"] if INCLUDE_01_02 else []) + ["03-contract", "04-architecture", "05-blockout"]
CHECKLIST = {
    "01-intake": ["spec + handoff files read back to the user", "intake source hashes recorded"],
    "02-analysis": ["spinner source GLB measured (65 mm tip circle)", "V3 concept proportions measured on the clean image", "analysis board viewed"],
    "03-contract": ["30/30 assertions pass", "key values reviewed (case 101.29 x 171.79 mm, pocket centre -20.69 mm)", "soft_focus / lighting / palette decisions recorded with wording"],
    "04-architecture": ["architecture board viewed", "34 core parts match the contract", "no explode view in review artifacts"],
    "05-blockout": ["CMF turntable recording (72 f) viewed in the IDE", "workbench turntable recording (72 f) available", "hero / front / obliques / macros viewed",
                    "muted four-tier sheet viewed", "reference-vs-hero sheet viewed", "clean / soft pair viewed (soft = Gate 08 only)"],
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
            "sourceId": SOURCE_ID_0102 if early else SOURCE_ID, "requestedAs": "follow-up question after 21:17 (AskQuestion)" if early else "批准 Gate 03/04/05（assistant 18:15 reply）",
            "interactionMode": "complete-recording-and-stills-viewed-in-ide" if sid == "05-blockout" else "documents-and-boards-viewed-in-chat",
            "openArtifactAtApproval": "Artifacts/TriSpinnerSlab/gate05-r011/gate05-r011-cmf-preview-turntable-clear.mp4",
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
        s6 = next(x for x in manifest["stages"] if x["id"] == "06-geometry")
        s6["status"] = "draft"; s6["variantId"] = VARIANT; s6.pop("staleReason", None)
        s6["nextStep"] = "refine geometry from the approved rev-011 blockout: bevel/fillet fidelity, thin-film COLOR0.g edge mask bake, brushing UV2, watertight export prep"
        manifest["currentState"]["activeStageId"] = "06-geometry"; manifest["currentState"]["activeStageStatus"] = "draft"
        events.append({"type": "stage-opened", "stageId": "06-geometry", "notes": "Gates 01-05 approved; Gate 06 opened as draft."})
    update_stage_digests(manifest)
    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = ("v3-tri-spinner-slab-gates-01-05-approved-gate-06-draft" if all_upstream_approved
                                   else "v3-tri-spinner-slab-gates-03-05-approved-gates-01-02-pending")
    manifest["currentState"]["visualApproval"] = ("gates-01-05-approved-rev011-blockout-level; shipping preview not yet produced" if all_upstream_approved
                                                  else "gates-03-05-approved-rev011-blockout-level; gates-01-02 awaiting user confirmation")
    manifest["currentState"]["contractApproval"] = {"stageId": "03-contract", "contractRevision": contract["contractRevision"], "evidenceRevision": "rev-011",
                                                    "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT, "contractSha256": contract_sha}
    manifest["currentState"]["architectureApproval"] = {"stageId": "04-architecture", "evidenceRevision": "rev-033", "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT}
    manifest["currentState"]["blockoutApproval"] = {"stageId": "05-blockout", "evidenceRevision": "rev-011", "userApprovalQuote": WORDING, "approvedAt": DECIDED_AT,
                                                    "openArtifact": "Artifacts/TriSpinnerSlab/gate05-r011/gate05-r011-cmf-preview-turntable-clear.mp4"}
    manifest["currentState"]["diagnosis"] += (f" 21:17 用户「{WORDING}」：Gate {'01–05' if all_upstream_approved else '03–05'} rev-011 批准（blockout 级，非 shipping 预览批准）；"
                                              + ("Gate 06 开为 draft。" if all_upstream_approved else "Gate 01–02 待用户确认。") + "未构建、未推送手机。")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps({"id": str(uuid.uuid4()), "modelId": MODEL_ID, "manifestRevision": manifest["revision"], "timestamp": NOW,
                                     "variantId": VARIANT, **event}, ensure_ascii=False) + "\n")
    print(json.dumps({"revision": manifest["revision"], "approved": GATES, "gate06": "draft" if all_upstream_approved else "stale",
                      "stages": {s["id"]: s["status"] for s in manifest["stages"]}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
