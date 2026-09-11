#!/usr/bin/env python3
"""Self-reject Gate 04 rev-011 iteration 09 after full-size frame inspection.

Full-size inspection of frames/frame-0114.png and frames/frame-0136.png shows
the audited Make It Shine discard edge sweep is not readable during the tear
phase, the freed foil reads as a rigid chrome blade, and the source flare still
contributes magenta sparkle glyphs. Criteria 2, 4 and 5 fail, so the stage must
not sit at ready_for_review asking the user to approve it.
"""

import hashlib
import json
import pathlib
import uuid
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[4]
PIPELINE = ROOT / "pipeline.json"
HISTORY = ROOT / "history.ndjson"

EVIDENCE_REL = (
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/"
    "evidence/04-architecture/rev-011"
)
SELF_REJECTION_REL = f"{EVIDENCE_REL}/iteration-09-self-rejection.json"

NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(rel: str) -> str:
    digest = hashlib.sha256()
    with (REPO / rel).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


pipeline = json.loads(PIPELINE.read_text())
stage = next(s for s in pipeline["stages"] if s["id"] == "04-architecture")

reasons = [
    "Criterion 4 fails: the audited Make It Shine discard edge sweep is not "
    "readable during the tear phase. packDissolve is 0.00 for frames 54-96, so "
    "the source identity contributes nothing while the tear is the subject.",
    "Criterion 2 fails: the freed foil reads as a rigid chrome blade with a "
    "smooth silhouette, not curling foil with underside, thickness and an "
    "irregular torn edge.",
    "Criterion 5 fails: the aperture still carries four-point cyan sparkle "
    "glyphs and a residual magenta smudge, because the source lifetime gradient "
    "still passes through magenta and the symmetric star atlas frame dominates.",
    "Criterion 5 fails at mid dissolve: the widened warm edge band degenerates "
    "into two flat cream horizontal rectangles uncorrelated with the torn "
    "contour, visible at frame 0136.",
    "The shaped cavity still reads as a thin dark band rather than an occluding "
    "interior volume at 0.25x.",
]

# 1. Register the self-rejection record as a validation asset.
self_rejection_asset_id = "premium-display-case-gate04-r011-iteration09-self-rejection"
if not any(a["id"] == self_rejection_asset_id for a in pipeline["assets"]):
    pipeline["assets"].append(
        {
            "id": self_rejection_asset_id,
            "stageId": "04-architecture",
            "slot": "architecture-implementation-evidence",
            "path": SELF_REJECTION_REL,
            "sha256": sha256(SELF_REJECTION_REL),
            "exists": True,
            "sizeBytes": (REPO / SELF_REJECTION_REL).stat().st_size,
            "role": "validation",
            "sourceAssetIds": [],
            "sourceClaimIds": [],
            "producer": {
                "name": "agent full-size frame inspection of the iteration-09 Unity capture",
                "version": "iteration-09",
                "recipe": "gate04-rev011-iteration09-self-rejection",
            },
            "provenance": {
                "origin": "assistant-generated",
                "contentClass": "architecture-implementation-evidence",
                "assertedBy": "assistant",
                "note": (
                    "Iteration 09 self-rejection after full-size frame "
                    "inspection. Iteration 09 artifacts are preserved unchanged "
                    "as labeled self-rejected history and were never shown to "
                    "the user for visual approval."
                ),
            },
            "wholeAssembledCaseOnly": True,
            "explodeEligible": False,
            "toyPrizeBundled": False,
            "shippingEligible": False,
            "reviewState": "supporting-evidence",
        }
    )
if self_rejection_asset_id not in stage["artifactIds"]:
    stage["artifactIds"].append(self_rejection_asset_id)
    stage["artifactIds"].sort()

# 2. Preserve the short-lived ready_for_review state as history.
stage.setdefault("historicalDecisions", []).append(
    {
        "revision": stage["revision"],
        "status": "ready_for_review",
        "evidenceRevision": 11,
        "evidenceIteration": 9,
        **stage["decision"],
    }
)
stage.setdefault("historicalRevisions", []).append(
    {
        "revision": stage["revision"],
        "status": "ready_for_review",
        "evidenceRevision": 11,
        "evidenceIteration": 9,
        "inputDigest": stage["inputDigest"],
        "outputDigest": stage["outputDigest"],
        "note": (
            "Iteration 09 briefly reached ready_for_review, then was self-rejected "
            "on full-size frame inspection before any user approval request. "
            "Never shown to the user for approval."
        ),
    }
)

# 3. Self-reject: the stage may not ask for approval.
stage["revision"] = stage["revision"] + 1
stage["status"] = "draft"
stage["decision"] = {
    "action": "self-reject",
    "notes": (
        "Gate 04 rev 011 iteration 09 is self-rejected on full-size frame "
        "inspection. Continuity and exposure genuinely improved over iteration "
        "08, but the audited source effect identity is absent during the tear "
        "phase, the freed foil reads as a chrome blade, and residual magenta "
        "sparkle glyphs remain. Iteration 10 is required before any approval "
        "request. Iteration 09 artifacts stay immutable labeled history."
    ),
    "decidedBy": "agent-full-size-frame-inspection",
    "decidedAt": NOW,
    "rejectionReasons": reasons,
    "approvalRequestAllowed": False,
    "finalAuthority": "latest-explicit-chat-instruction",
    "selfRejectionRecord": SELF_REJECTION_REL,
}

stage["validations"] = [
    {
        "id": "rev8-and-rev9-artifacts-preserved",
        "status": "pass",
        "evidence": (
            "Gate 04 rev 8 and rev 9 snapshots remain in historicalRevisions and "
            "historicalDecisions as immutable rejected history."
        ),
    },
    {
        "id": "iterations-01-to-09-preserved-as-self-rejected-history",
        "status": "pass",
        "evidence": f"{EVIDENCE_REL}/iterations/iteration-01 .. iteration-08 plus {SELF_REJECTION_REL}",
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
        "id": "single-case-instance-continuity-verified",
        "status": "pass",
        "evidence": (
            "One distinct caseRootId across 207 frames; projected height 0.4369 to "
            "0.5545 with maximum consecutive step 0.0038; packVisible flips false "
            "only after packDissolve reaches 1.0."
        ),
    },
    {
        "id": "source-effect-identity-readable-during-tear",
        "status": "fail",
        "evidence": (
            f"{EVIDENCE_REL}/frames/frame-0114.png shows an opaque Pack with no "
            "emissive discard edge sweep; packDissolve is 0.00 for frames 54-96."
        ),
    },
    {
        "id": "freed-foil-reads-as-curling-foil",
        "status": "fail",
        "evidence": (
            f"{EVIDENCE_REL}/frames/frame-0114.png shows a rigid chrome blade "
            "silhouette without underside, thickness or irregular torn edge."
        ),
    },
    {
        "id": "no-decorative-sparkle-or-magenta-in-aperture",
        "status": "fail",
        "evidence": (
            f"{EVIDENCE_REL}/continuity-contact-sheet.png top row and frame-0114.png "
            "show four-point cyan sparkle glyphs plus a residual magenta smudge."
        ),
    },
    {
        "id": "shipping-ready-remains-false",
        "status": "pass",
        "evidence": (
            "shippingRuntimeWired=false, shippingReady=false, "
            "physicalPhoneInstalled=false."
        ),
    },
]

stage["evidenceReview"] = {
    **stage.get("evidenceReview", {}),
    "iteration": 9,
    "disposition": "self-rejected",
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "selfRejectionRecord": SELF_REJECTION_REL,
    "shownToUserForApproval": False,
    "visualApproval": "not-requested-self-rejected",
}

# The stage must not advertise review artifacts while self-rejected.
stage["reviewArtifactIds"] = []

state = pipeline["currentState"]
state["visualApproval"] = "gate04-rev011-iteration09-self-rejected-iteration10-required"
state["diagnosis"] = (
    "Gate 04 rev 8 and rev 9 stay immutable rejected history. Rev 011 follows the "
    "user's explicit correction to retarget the audited CC0 Make It Shine example "
    "rather than redraw the transition. Iteration 09 fixed exposure, foil "
    "detachment, excessive twist and pack retreat, and proved real single-instance "
    "continuity, but is self-rejected because the audited discard edge sweep is not "
    "readable during the tear phase, the freed foil reads as a chrome blade, and "
    "residual magenta sparkle glyphs remain. Iterations 01-09 are self-rejected "
    "history. No approval was requested and nothing was built or installed."
)
state["motionCorrection"] = {
    **state.get("motionCorrection", {}),
    "gate04Status": "rev011-iteration09-self-rejected-iteration10-required",
    "currentEvidenceIteration": 9,
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8, 9],
}
state["architectureApproval"] = {
    "stageId": "04-architecture",
    "architectureRevision": 6,
    "evidenceRevision": 11,
    "evidenceIteration": 9,
    "userApprovalQuote": None,
    "decisionState": "self-rejected-iteration10-required",
    "approvalRequestAllowed": False,
    "gate05Status": "stale",
}

pipeline["revision"] = pipeline["revision"] + 1
pipeline["updatedAt"] = NOW

PIPELINE.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False) + "\n")

record = {
    "id": str(uuid.uuid4()),
    "type": "iteration-self-rejected",
    "modelId": "premium-display-case",
    "manifestRevision": pipeline["revision"],
    "timestamp": NOW,
    "stageId": "04-architecture",
    "stageRevision": stage["revision"],
    "previousStageRevision": stage["revision"] - 1,
    "previousStageStatus": "ready_for_review",
    "stageStatus": "draft",
    "architectureRevision": 6,
    "evidenceRevision": 11,
    "evidenceIteration": 9,
    "decidedBy": "agent-full-size-frame-inspection",
    "reviewedAtFullSize": [
        f"{EVIDENCE_REL}/frames/frame-0114.png",
        f"{EVIDENCE_REL}/frames/frame-0136.png",
        f"{EVIDENCE_REL}/tear-contact-sheet.png",
        f"{EVIDENCE_REL}/continuity-contact-sheet.png",
    ],
    "rejectionReasons": reasons,
    "selfRejectionRecord": SELF_REJECTION_REL,
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "shownToUserForApproval": False,
    "approvalRequestAllowed": False,
    "disposition": "iteration-10-required",
    "staleGateIds": [
        "05-blockout",
        "06-geometry",
        "07-material",
        "08-lighting",
        "09-environment",
        "10-export",
        "11-unity-parity",
        "12-shipping",
    ],
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
