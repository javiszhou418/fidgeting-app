#!/usr/bin/env python3
"""Archive the second R013 Unity capture before axis correction."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "iterations" / "iteration-02-axis-import"
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
        "schema": "premium-display-case-gate04-r013-iteration-02-self-rejection.v1",
        "decision": "self-rejected",
        "reason": (
            "The first visible Pack import treated Blender Y as Unity depth and "
            "Blender Z as Unity height. The Pack rig rendered edge-on and revealed "
            "the case before tear."
        ),
        "correctiveScope": (
            "Apply the Pack-only FBX root's required +90 degree X import "
            "orientation. Do not alter the live case or source artwork."
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
