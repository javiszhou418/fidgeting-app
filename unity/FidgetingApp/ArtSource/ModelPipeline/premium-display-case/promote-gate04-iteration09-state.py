#!/usr/bin/env python3
"""Promote Gate 04 stage state from the rev-9 technical rejection to the
rev-011 iteration-09 ready_for_review candidate.

The register step already added the iteration-09 artifacts, reviewArtifactIds
and evidenceReview, but left stage status/decision/validations and the
pipeline currentState describing rev 9. That inconsistency makes the stage
claim "rejected" while carrying ready-for-review evidence.
"""

import json
import pathlib
import uuid
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
PIPELINE = ROOT / "pipeline.json"
HISTORY = ROOT / "history.ndjson"

EVIDENCE_REL = (
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/"
    "evidence/04-architecture/rev-011"
)

NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

pipeline = json.loads(PIPELINE.read_text())

stage = next(s for s in pipeline["stages"] if s["id"] == "04-architecture")

# 1. Preserve the rev-9 rejection as immutable labeled history.
rejected_decision = stage["decision"]
stage.setdefault("historicalDecisions", []).append(
    {
        "revision": stage["revision"],
        "status": "rejected",
        "evidenceRevision": 9,
        "architectureRevision": 5,
        **rejected_decision,
    }
)
stage.setdefault("historicalRevisions", []).append(
    {
        "revision": stage["revision"],
        "status": "rejected",
        "evidenceRevision": 9,
        "architectureRevision": 5,
        "inputDigest": stage["inputDigest"],
        "outputDigest": stage["outputDigest"],
        "note": (
            "Gate 04 rev 9 technical rejection. Immutable history; never restore "
            "as a current requirement or show for approval."
        ),
    }
)

# 2. Promote the stage to the iteration-09 candidate.
stage["revision"] = stage["revision"] + 1
stage["status"] = "ready_for_review"
stage["decision"] = {
    "action": "ready-for-review",
    "notes": (
        "Gate 04 rev 011 iteration 09 retargets the audited CC0 Make It Shine "
        "transition instead of redrawing it, per the user's explicit correction. "
        "Real Unity PlayMode capture at 1206x2622 / 60 fps: 207 normal-speed "
        "frames plus 0.25x tear (197) and 0.25x impact/reveal (187) passes. "
        "Iterations 01-08 remain immutable self-rejected history. Awaiting user "
        "visual approval; no build, no install."
    ),
    "decidedBy": "agent-self-inspection-pending-user-approval",
    "decidedAt": NOW,
    "approvalRequestAllowed": True,
    "finalAuthority": "latest-explicit-chat-instruction",
    "supersedes": {
        "revision": stage["revision"] - 1,
        "evidenceRevision": 9,
        "reason": "rev-9-technical-rejection-superseded-by-cc0-reuse-retarget",
    },
}

stage["validations"] = [
    {
        "id": "rev8-and-rev9-artifacts-preserved",
        "status": "pass",
        "evidence": (
            "Gate 04 rev 8 and rev 9 stage snapshots remain in historicalRevisions "
            "and historicalDecisions; all rev 9 artifacts stay technical-rejected "
            "history."
        ),
    },
    {
        "id": "iterations-01-to-08-preserved-as-self-rejected-history",
        "status": "pass",
        "evidence": f"{EVIDENCE_REL}/iterations/iteration-01 .. iteration-08",
    },
    {
        "id": "capture-is-real-unity-playmode-output",
        "status": "pass",
        "evidence": f"{EVIDENCE_REL}/unity-capture-report.json",
    },
    {
        "id": "cc0-source-to-canonical-mapping-recorded",
        "status": "pass",
        "evidence": f"{EVIDENCE_REL}/source-to-canonical-mapping.json",
    },
    {
        "id": "focused-unity-tests-pass",
        "status": "pass",
        "evidence": "unity/FidgetingApp/Logs/PackOpeningGate04R011Results-r11.xml (29/29)",
    },
    {
        "id": "shipping-ready-remains-false",
        "status": "pass",
        "evidence": (
            "shippingRuntimeWired=false, shippingReady=false, "
            "physicalPhoneInstalled=false in the capture report and stage "
            "evidenceReview."
        ),
    },
]

# 3. Realign pipeline currentState with the iteration-09 candidate.
state = pipeline["currentState"]
state["visualApproval"] = (
    "gate04-rev011-iteration09-ready-for-review-pending-user-visual-approval"
)
state["diagnosis"] = (
    "Gate 04 rev 8 and rev 9 stay immutable rejected history and must not be "
    "shown for approval. Rev 011 iteration 09 follows the user's explicit "
    "correction to retarget the audited CC0 Make It Shine example rather than "
    "redraw the transition: source Timeline beat structure, the normalized "
    "discard curve, the SG_BoosterPack dissolve/emissive edge math and the "
    "Sphere Mask sweep are reused, with minimum adapters for URP 17.5, portrait "
    "composition, real object bindings and the VFX Graph to Shuriken port. "
    "Iterations 01-08 are self-rejected history. Awaiting user visual approval "
    "before any build or install."
)
state["motionCorrection"] = {
    "earliestGate": "04-architecture",
    "gate04Status": "rev011-iteration09-ready-for-review",
    "rejectedArchitectureRevision": 5,
    "rejectedEvidenceRevision": 9,
    "rejectedEvidenceRevisions": [8, 9],
    "rejectionEventId": "794facd7-3c15-4c6c-bc32-4617cf4de882",
    "currentArchitectureRevision": 6,
    "currentEvidenceRevision": 11,
    "currentEvidenceIteration": 9,
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8],
    "downstreamStaleGates": [
        "05-blockout",
        "06-geometry",
        "07-material",
        "08-lighting",
        "09-environment",
        "10-export",
        "11-unity-parity",
        "12-shipping",
    ],
    "shippingPreviewApproved": False,
    "deviceAccepted": False,
}
state["architectureApproval"] = {
    "stageId": "04-architecture",
    "architectureRevision": 6,
    "evidenceRevision": 11,
    "evidenceIteration": 9,
    "userApprovalQuote": None,
    "decisionState": "ready-for-review-pending-user-visual-approval",
    "approvalRequestAllowed": True,
    "gate05Status": "stale",
}

pipeline["revision"] = pipeline["revision"] + 1
pipeline["updatedAt"] = NOW

PIPELINE.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False) + "\n")

record = {
    "id": str(uuid.uuid4()),
    "type": "stage-state-realignment",
    "modelId": "premium-display-case",
    "manifestRevision": pipeline["revision"],
    "timestamp": NOW,
    "stageId": "04-architecture",
    "stageRevision": stage["revision"],
    "previousStageRevision": stage["revision"] - 1,
    "previousStageStatus": "rejected",
    "stageStatus": "ready_for_review",
    "architectureRevision": 6,
    "evidenceRevision": 11,
    "evidenceIteration": 9,
    "reason": (
        "The iteration-09 registration added artifacts, reviewArtifactIds and "
        "evidenceReview but left stage status, decision, validations and "
        "currentState describing the rev-9 technical rejection. This realigns "
        "them and preserves the rev-9 rejection in historicalDecisions and "
        "historicalRevisions."
    ),
    "reviewAuthority": "agent-self-inspection-pending-user-approval",
    "approvalRequestAllowed": True,
    "disposition": "awaiting-user-visual-approval",
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8],
    "shippingRuntimeWired": False,
    "nativeUiWired": False,
    "shippingReady": False,
    "physicalPhoneInstalled": False,
    "deviceAccepted": False,
    "statusText": "视觉批准待确认，未推送手机",
}

with HISTORY.open("a") as handle:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"pipeline revision -> {pipeline['revision']}")
print(f"stage 04-architecture revision -> {stage['revision']} status -> {stage['status']}")
print(f"history event -> {record['id']}")
