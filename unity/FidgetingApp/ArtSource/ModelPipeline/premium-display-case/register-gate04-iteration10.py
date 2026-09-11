#!/usr/bin/env python3
"""Register Gate 04 rev 11 iteration 10 and move the stage to ready_for_review.

Iteration 09 stays as immutable self-rejected history. Iteration 10 fixes the
four defects the parent prioritised: no visible aperture, no source edge sweep
during the tear, a blade-like freed strip, and coloured sparkle glyphs.
"""

import datetime
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[4]
PIPELINE = ROOT / "pipeline.json"
HISTORY = ROOT / "history.ndjson"
EV = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011"
NOW = "2026-08-28T12:30:00.000Z"

NEW_ASSETS = [
    (
        "premium-display-case-gate04-r011-iteration10-self-review",
        f"{EV}/iterations/iteration-10/self-review.json",
        "validation",
        "Iteration-10 full-size frame verdict: aperture, tear-driven sweep, "
        "foil and sparkle criteria with root causes and residual defects.",
    ),
    (
        "premium-display-case-gate04-r011-iteration09-evidence-loss",
        f"{EV}/iterations/iteration-09/EVIDENCE-LOSS.json",
        "validation",
        "Iteration-09 pixel evidence was overwritten by the iteration-10 "
        "captures because it had never been archived. Written verdict survives.",
    ),
    (
        "premium-display-case-gate04-r011-iteration09-self-rejection-archived",
        f"{EV}/iterations/iteration-09/self-rejection.json",
        "validation",
        "Archived copy of the iteration-09 self-rejection in its iteration slot.",
    ),
    (
        "premium-display-case-gate04-r011-i10-tear-contact-sheet",
        f"{EV}/iterations/iteration-10/tear-contact-sheet.png",
        "shipping-render",
        "Iteration-10 tear silhouette sheet: progressive right-to-left opening "
        "with occluded interior, from the real Unity shipping scene.",
    ),
    (
        "premium-display-case-gate04-r011-i10-continuity-contact-sheet",
        f"{EV}/iterations/iteration-10/continuity-contact-sheet.png",
        "shipping-render",
        "Iteration-10 impact continuity sheet from the real Unity shipping scene.",
    ),
    (
        "premium-display-case-gate04-r011-i10-source-side-by-side",
        f"{EV}/iterations/iteration-10/source-target-side-by-side.png",
        "shipping-render",
        "Iteration-10 CC0 source versus retarget at matched effect timestamps.",
    ),
    (
        "premium-display-case-gate04-r011-i10-normal-speed",
        f"{EV}/iterations/iteration-10/normal-speed-sequence.mp4",
        "shipping-render",
        "Iteration-10 normal-speed full sequence encoded from the real frames.",
    ),
    (
        "premium-display-case-gate04-r011-i10-tear-quarter-speed",
        f"{EV}/iterations/iteration-10/tear-quarter-speed-closeup.mp4",
        "shipping-render",
        "Iteration-10 0.25x tear close-up encoded from the real frames.",
    ),
    (
        "premium-display-case-gate04-r011-i10-impact-quarter-speed",
        f"{EV}/iterations/iteration-10/impact-reveal-quarter-speed.mp4",
        "shipping-render",
        "Iteration-10 0.25x impact and reveal encoded from the real frames.",
    ),
    (
        "premium-display-case-gate04-r011-i10-capture-report",
        f"{EV}/iterations/iteration-10/unity-capture-report.json",
        "validation",
        "Iteration-10 capture report: 1206x2622 at 60 fps, 207 frames, all 26 "
        "assertions pass.",
    ),
]

VALIDATIONS = [
    ("rev8-and-rev9-artifacts-preserved", "pass",
     "Gate 04 rev 8 and rev 9 snapshots remain in historicalRevisions and "
     "historicalDecisions as immutable rejected history."),
    ("iterations-01-to-09-preserved-as-self-rejected-history", "pass",
     f"{EV}/iterations/iteration-01 .. iteration-09. Iteration-09 pixel "
     f"artifacts were lost to overwrite; the loss and the surviving written "
     f"verdict are recorded in {EV}/iterations/iteration-09/EVIDENCE-LOSS.json."),
    ("capture-is-real-unity-playmode-output", "pass",
     f"{EV}/iterations/iteration-10/unity-capture-report.json, all 26 "
     f"assertions pass at 1206x2622 and 60 fps."),
    ("cc0-source-to-canonical-mapping-recorded", "pass",
     f"{EV}/iterations/iteration-10/source-to-canonical-mapping.json"),
    ("focused-unity-tests-pass", "pass",
     "34/34 EditMode tests in PackOpeningGate04R011Tests, including the four "
     "new iteration-10 regressions for aperture exposure, tear-driven sweep, "
     "torn-edge irregularity and the dissolve visibility invariant."),
    ("single-case-instance-continuity-verified", "pass",
     "One caseRootId across 207 frames. Case projected height 0.4369 to 0.5545 "
     "with maximum consecutive step 0.00384. packVisible becomes false only at "
     "packDissolve 1.0 exactly, now gated on the discard curve rather than the "
     "retreat settle."),
    ("pack-visibly-opens-with-occluded-interior", "pass",
     f"{EV}/iterations/iteration-10/tear-contact-sheet.png and frames 0060 and "
     f"0084. The bag now has a back wall behind the concealed case, a tear-front "
     f"cross wall, a released-end side wall, a torn-edge lip and a separate "
     f"near-black occlusion band behind the lip."),
    ("source-effect-identity-readable-during-tear", "pass",
     "The audited discard edge sweep is evaluated in torn-contour space from uv2 "
     "and driven by TearSweepStrength(tearProgress), so it is lit at frames 0060 "
     "and 0084 while packDissolve is still 0.00, and cannot degenerate into a "
     "full-width horizontal band."),
    ("freed-foil-reads-as-curling-foil", "pass",
     "Band width 0.026 to 0.045 m, front metallic 0.72 to 0.28, smoothness 0.58 "
     "to 0.24, darker underside, curl turning over inside the Pack width, and "
     "per-column micro-offsets on both the free edge and the torn contour. "
     "Residual: the curled tip still reads as a hard dark wedge."),
    ("no-decorative-sparkle-or-magenta-in-aperture", "pass",
     "The purple and saturated cyan keys are excluded from the flare lifetime "
     "gradient, every flare port addresses a single atlas cell, rotation is "
     "limited to the radial glow port, and the flare billboard is flattened so "
     "the source glyph reads as a horizontal streak."),
    ("no-rarity-leak-before-authoritative-receipt", "pass",
     "noReceiptRarityLeak passes. The palette stays cooler than the source and "
     "was not warmed by leaking rarity."),
    ("shipping-ready-remains-false", "pass",
     "shippingReady false, physicalPhoneInstalled false, deviceAccepted false."),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


pipeline = json.loads(PIPELINE.read_text())
stage = next(s for s in pipeline["stages"] if s["id"] == "04-architecture")

# Preserve the iteration-09 self-rejected state as immutable history.
stage.setdefault("historicalDecisions", []).append({
    "supersededAt": NOW,
    "supersededBy": "gate04-rev011-iteration-10",
    "revision": stage["revision"],
    "status": stage["status"],
    "decision": stage["decision"],
    "validations": stage["validations"],
    "evidenceReview": stage.get("evidenceReview"),
})

existing = {a["id"] for a in pipeline["assets"]}
added = []
for asset_id, rel, role, note in NEW_ASSETS:
    if asset_id in existing:
        raise SystemExit(f"asset already registered: {asset_id}")
    absolute = REPO / rel
    if not absolute.is_file():
        raise SystemExit(f"missing artifact: {rel}")
    pipeline["assets"].append({
        "id": asset_id,
        "stageId": "04-architecture",
        "slot": "architecture-implementation-evidence",
        "path": rel,
        "sha256": sha256(absolute),
        "exists": True,
        "sizeBytes": absolute.stat().st_size,
        "role": role,
        "sourceAssetIds": [],
        "sourceClaimIds": [],
        "producer": {
            "name": "Unity 6000.5.6f1 batchmode "
                    "PackOpeningGate04R011Builder.BuildAndRunCapture",
            "version": "capture-r26",
            "recipe": "gate04-rev011-iteration10-cc0-reuse-retarget",
        },
        "provenance": {
            "origin": "assistant-generated",
            "contentClass": "architecture-implementation-evidence",
            "assertedBy": "assistant",
            "note": note,
        },
        "wholeAssembledCaseOnly": True,
        "explodeEligible": False,
        "toyPrizeBundled": False,
        "shippingEligible": False,
        "reviewState": "awaiting-user-visual-approval"
            if role == "shipping-render" else "supporting-evidence",
    })
    added.append(asset_id)
    if asset_id not in stage["artifactIds"]:
        stage["artifactIds"].append(asset_id)

stage["reviewArtifactIds"] = [
    "premium-display-case-gate04-r011-i10-tear-contact-sheet",
    "premium-display-case-gate04-r011-i10-continuity-contact-sheet",
    "premium-display-case-gate04-r011-i10-source-side-by-side",
    "premium-display-case-gate04-r011-i10-normal-speed",
    "premium-display-case-gate04-r011-i10-tear-quarter-speed",
    "premium-display-case-gate04-r011-i10-impact-quarter-speed",
]

stage["status"] = "ready_for_review"
stage["revision"] = stage["revision"] + 1
stage["validations"] = [
    {"id": i, "status": s, "evidence": e} for i, s, e in VALIDATIONS
]
stage["decision"] = {
    "action": "request-user-visual-approval",
    "notes": (
        "Gate 04 rev 011 iteration 10. The iteration-09 blocking defects are "
        "addressed at their root causes rather than by repeating a failed "
        "tweak. The Pack now visibly opens: the bag has a real interior with a "
        "back wall behind the concealed case, a tear-front cross wall, a "
        "released-end side wall, a torn-edge lip and a separate occlusion band, "
        "so the receding front face uncovers a cavity instead of shortening the "
        "silhouette. The audited discard edge sweep is evaluated in torn-contour "
        "space and driven by tearProgress, so it is visible while the Pack is "
        "still opaque and can never become a full-width horizontal rectangle. "
        "The freed strip is wider, rougher, darker underneath and curls over "
        "itself. The magenta and saturated cyan gradient segments are excluded "
        "and the flare ports render horizontal streaks instead of four-point "
        "glyphs. Continuity is unchanged except that packVisible now can only "
        "become false at packDissolve 1.0 exactly. Four polish-level residual "
        "defects are disclosed in the self-review. Awaiting explicit user "
        "visual approval; nothing installed on a device."
    ),
    "decidedAt": NOW,
    "decidedBy": "assistant",
}
stage["evidenceReview"] = {
    "iteration": 10,
    "capturedAt": NOW,
    "source": "actual Unity PlayMode shipping scene",
    "selfRejectedIterations": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "residualGaps": [
        "The interior rim reads as a near-straight horizontal line rather than "
        "a crimped seal contour, so the opening looks slightly rectangular.",
        "The released-end side wall shows as a thin sliver just outside the "
        "front face silhouette.",
        "The curled foil tip reads as a hard dark wedge.",
        "The retarget palette stays cooler than the source, because the "
        "source's warm dominance comes from rarity card emissive which must not "
        "appear before the authoritative receipt.",
    ],
    "evidenceLoss": f"{EV}/iterations/iteration-09/EVIDENCE-LOSS.json",
    "shippingRuntimeWired": False,
    "userVisualApprovalObtained": False,
    "physicalPhoneInstalled": False,
    "deviceAccepted": False,
    "statusText": "视觉批准待确认，未推送手机",
}

pipeline["currentState"] = dict(pipeline.get("currentState", {}))
pipeline["currentState"].update({
    "activeStageId": "04-architecture",
    "activeStageStatus": "ready_for_review",
    "activeIteration": 10,
    "summary": (
        "Gate 04 rev 011 iteration 10 awaits user visual approval. Iterations "
        "01-09 remain self-rejected history."
    ),
    "statusText": "视觉批准待确认，未推送手机",
})
pipeline["revision"] = pipeline["revision"] + 1
pipeline["updatedAt"] = NOW

PIPELINE.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False) + "\n")

with HISTORY.open("a") as handle:
    handle.write(json.dumps({
        "event": "stage-ready-for-review",
        "at": NOW,
        "modelId": "premium-display-case",
        "pipelineRevision": pipeline["revision"],
        "stageId": "04-architecture",
        "stageRevision": stage["revision"],
        "iteration": 10,
        "actor": "assistant",
        "summary": (
            "Gate 04 rev 011 iteration 10: real bag interior so the Pack "
            "visibly opens, contour-space source edge sweep driven by "
            "tearProgress, foil-like freed strip, streak-only flares with the "
            "magenta segment excluded. 34/34 focused tests, 26/26 capture "
            "assertions. Iteration-09 evidence loss recorded."
        ),
        "assetIds": added,
        "statusText": "视觉批准待确认，未推送手机",
    }, ensure_ascii=False) + "\n")

print(f"pipeline revision -> {pipeline['revision']}")
print(f"stage revision -> {stage['revision']} status {stage['status']}")
print(f"registered {len(added)} assets")
