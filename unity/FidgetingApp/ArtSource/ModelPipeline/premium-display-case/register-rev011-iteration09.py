#!/usr/bin/env python3
"""Register Gate 04 rev 11 iteration-09 shipping-scene evidence.

Adds assets and appends history only. The Gate 04 decision stays not-approved:
registration is evidence delivery, never approval.
"""
import hashlib
import json
import os
import time
import uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", "..", "..", "..", ".."))
EV = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011"
TASK = "gate04-rev011-iteration09-cc0-reuse-retarget"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

ARTIFACTS = [
    ("normal-speed-sequence.mp4", "architecture-shipping-preview",
     "Real Unity 6000.5.6f1 PlayMode capture, 1206x2622, 60 fps, full 3.45 s sequence.", True),
    ("tear-quarter-speed-closeup.mp4", "architecture-shipping-preview",
     "0.25x tear close-up from the same shipping scene, 0.80-1.62 s window.", True),
    ("impact-reveal-quarter-speed.mp4", "architecture-shipping-preview",
     "0.25x impact and reveal from the same shipping scene, 1.56-2.34 s window.", True),
    ("tear-contact-sheet.png", "architecture-shipping-preview",
     "Tear silhouette contact sheet.", True),
    ("source-impact-contact-sheet.png", "architecture-shipping-preview",
     "Impact continuity contact sheet.", True),
    ("continuity-contact-sheet.png", "architecture-shipping-preview",
     "Single-instance case continuity contact sheet.", True),
    ("source-target-side-by-side.png", "architecture-source-comparison",
     "Make It Shine source versus retarget at matched effect timestamps.", False),
    ("matched-timestamps.json", "architecture-source-comparison",
     "Source-to-target timestamp pairing for the side-by-side.", False),
    ("source-to-canonical-mapping.json", "architecture-provenance",
     "CC0 source to canonical asset mapping with direct-copy, adapted and rejected decisions.", False),
    ("unity-capture-report.json", "architecture-implementation-evidence",
     "Automated capture gate report for iteration-09.", False),
    ("iterations/iteration-08/self-rejection.json", "architecture-implementation-evidence",
     "Iteration-08 visual self-rejection: exposure, foil detachment, pack slide, lavender blob, reuse balance.", False),
    ("iterations/iteration-02/EVIDENCE-LOSS.json", "architecture-implementation-evidence",
     "Declared loss of iteration-02 pixel artifacts during takeover; rejection record intact.", False),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    pipeline_path = os.path.join(ROOT, "pipeline.json")
    with open(pipeline_path, encoding="utf-8") as handle:
        data = json.load(handle)

    existing = {a["id"] for a in data["assets"]}
    added, review_ids = [], []

    for name, slot, note, is_review in ARTIFACTS:
        rel = f"{EV}/{name}"
        absolute = os.path.join(REPO, rel)
        if not os.path.exists(absolute):
            print(f"MISSING {rel}")
            continue
        stem = os.path.basename(name).rsplit(".", 1)[0]
        asset_id = f"premium-display-case-gate04-r011-i09-{stem}"
        if asset_id in existing:
            print(f"skip existing {asset_id}")
            continue
        data["assets"].append({
            "id": asset_id,
            "stageId": "04-architecture",
            "slot": slot,
            "path": rel,
            "sha256": sha256(absolute),
            "exists": True,
            "sizeBytes": os.path.getsize(absolute),
            "role": "shipping-render" if is_review else "validation",
            "sourceAssetIds": [],
            "sourceClaimIds": [],
            "producer": {
                "name": "Unity 6000.5.6f1 batchmode PackOpeningGate04R011Builder.BuildAndRunCapture",
                "version": "capture-r14",
                "recipe": TASK,
            },
            "provenance": {
                "origin": "assistant-generated",
                "contentClass": slot,
                "assertedBy": "assistant",
                "note": note,
            },
            "wholeAssembledCaseOnly": True,
            "explodeEligible": False,
            "toyPrizeBundled": False,
            "shippingEligible": False,
            "reviewState": "awaiting-user-visual-approval" if is_review else "supporting-evidence",
        })
        added.append(asset_id)
        if is_review:
            review_ids.append(asset_id)

    stage = next(s for s in data["stages"] if s["id"] == "04-architecture")
    stage["revision"] = stage.get("revision", 0) + 1
    stage["artifactIds"] = sorted(set(stage.get("artifactIds", []) + added))
    stage["reviewArtifactIds"] = review_ids
    stage["evidenceReview"] = {
        "iteration": 9,
        "capturedAt": NOW,
        "source": "actual Unity PlayMode shipping scene",
        "selfRejectedIterations": list(range(1, 9)),
        "residualGaps": [
            "The shaped cavity still reads as a thin dark band at 0.25x close-up rather than an occluding interior volume.",
            "The retarget palette stays cooler than the source because the source's warm dominance comes from rarity card emissive, which must not appear before the authoritative receipt.",
        ],
        "shippingRuntimeWired": False,
        "shippingReady": False,
        "physicalPhoneInstalled": False,
        "visualApproval": "pending",
    }

    data["revision"] = data.get("revision", 0) + 1
    data["updatedAt"] = NOW

    with open(pipeline_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(os.path.join(ROOT, "history.ndjson"), "a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "id": str(uuid.uuid4()),
            "type": "stage-ready-for-review",
            "modelId": "premium-display-case",
            "manifestRevision": data["revision"],
            "timestamp": NOW,
            "stageId": "04-architecture",
            "architectureRevision": 6,
            "evidenceRevision": 11,
            "evidenceIteration": 9,
            "reviewAuthority": "agent-self-inspection-pending-user-approval",
            "sourceTask": TASK,
            "addedAssetIds": added,
            "reviewArtifactIds": review_ids,
            "selfRejectedIterations": list(range(1, 9)),
            "approvalRequestAllowed": True,
            "disposition": "awaiting-user-visual-approval",
            "nextState": "user-visual-approval-required-before-any-build-or-install",
            "staleGateIds": [
                "05-blockout", "06-geometry", "07-material", "08-lighting",
                "09-environment", "10-export", "11-unity-parity", "12-shipping",
            ],
            "shippingRuntimeWired": False,
            "nativeUiWired": False,
            "shippingReady": False,
            "physicalPhoneInstalled": False,
            "deviceAccepted": False,
            "statusText": "视觉批准待确认，未推送手机",
        }, ensure_ascii=False) + "\n")

    print(f"pipeline revision {data['revision']}, stage revision {stage['revision']}")
    print(f"added {len(added)} assets, {len(review_ids)} review artifacts")


if __name__ == "__main__":
    main()
