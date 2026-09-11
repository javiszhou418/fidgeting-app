#!/usr/bin/env python3
"""Archive the third R013 Unity capture before transform correction."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "iterations" / "iteration-03-root-rotation"
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
        "schema": "premium-display-case-gate04-r013-iteration-03-self-rejection.v1",
        "decision": "self-rejected",
        "reason": (
            "A +90 degree root rotation made the already Unity-axis-correct FBX "
            "rig render edge-on. The Pack remained an invalid frame-like silhouette."
        ),
        "correctiveScope": (
            "Remove the root rotation. The Unity importer already converts this "
            "FBX into X/Y/Z Pack coordinates."
        ),
        "movedArtifacts": moved,
        "shippingReady": False,
        "physicalPhoneInstalled": False,
        "approvalRequestAllowed": False,
        "statusText": "视觉批准待确认，未推送手机",
    }
    (TARGET / "self-rejection.json").write_text(
        json.dumps(record, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
