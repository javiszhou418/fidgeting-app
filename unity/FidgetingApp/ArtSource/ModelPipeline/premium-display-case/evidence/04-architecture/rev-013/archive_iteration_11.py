#!/usr/bin/env python3
"""Archive R013's full-size rejected Unity capture without deleting evidence."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "iterations" / "iteration-11-full-size-self-rejection"
ITEMS = (
    "frames",
    "frames-tear-quarter",
    "frames-impact-quarter",
    "primary-contact-sheet.png",
    "continuity-contact-sheet.png",
    "technical-continuity-sheet.svg",
    "source-target-side-by-side.png",
    "matched-timestamps.json",
    "runtime-footprint-editor-estimate.json",
    "unity-capture-report.json",
    "unity-source-manifest.json",
    "source-to-canonical-mapping.json",
)


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=False)
    moved: list[str] = []
    for name in ITEMS:
        source = ROOT / name
        if source.exists():
            shutil.move(str(source), str(TARGET / name))
            moved.append(name)

    record = {
        "schema": "premium-display-case-gate04-r013-iteration-11-self-rejection.v1",
        "decision": "self-rejected",
        "reviewedSource": "actual Unity PlayMode Camera PNG capture at 1206x2622/60 fps",
        "fullSizeFramesReviewed": [
            "frames/frame-0000.png",
            "frames/frame-0039.png",
            "frames/frame-0055.png",
            "frames/frame-0065.png",
            "frames/frame-0083.png",
            "frames/frame-0100.png",
            "frames/frame-0121.png",
            "frames/frame-0169.png",
            "frames-tear-quarter/frame-0060.png",
            "frames-impact-quarter/frame-0060.png",
        ],
        "passedTechnicalChecks": [
            "One pre-instantiated assembled case retains its entity ID and scale.",
            "The case stays contained before it crosses the physical mouth.",
            "No early case travel, black frame, white frame, identity swap, or bounds jump was detected.",
            "The Blender Pack-only FBX imported with 96 tear columns and six relative blend-shape samples.",
            "The Pack remains a candidate and is not wired into shipping runtime or native UI.",
        ],
        "rejectionReasons": [
            "The released strip and lip form a rigid blue U-shaped rail. They do not read as a narrow double-sided, creased foil strip with a local curl near the pull tab.",
            "The mouth silhouette is a broad symmetric scallop with dark hard-edged end pieces. It does not read as a credible foil pouch with an irregular torn edge and rolled contact lip.",
            "The CC0-derived Shuriken output appears as stacked red rectangular streaks, not a restrained warm-neutral torn-contour sweep. The direct source identity is not visually preserved at portrait scale.",
        ],
        "missingRequiredDeliverables": [
            "Normal-speed and 0.25x MP4 encodes could not be written because the volume had only 119 MiB available. The original Unity PNG sequences remain preserved.",
            "Focused Unity EditMode re-run was not started because the same volume is full and a Unity reimport/log write could corrupt the project.",
        ],
        "correctiveScope": (
            "Do not advance Gate 04. A future revision must redesign the physical lip/strip "
            "and source-port particle layout from real Pack foil behavior, then re-capture "
            "only after durable storage is available."
        ),
        "movedArtifacts": moved,
        "approvalRequestAllowed": False,
        "shippingReady": False,
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
        "statusText": "视觉批准待确认，未推送手机",
    }
    (TARGET / "self-rejection.json").write_text(
        json.dumps(record, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
