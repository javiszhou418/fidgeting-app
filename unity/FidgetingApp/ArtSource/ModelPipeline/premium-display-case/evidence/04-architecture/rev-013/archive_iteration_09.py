#!/usr/bin/env python3
"""Archive the ninth R013 Unity capture before rim gain correction."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "iterations" / "iteration-09-rim-gain-self-rejection"
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
        "schema": "premium-display-case-gate04-r013-iteration-09-self-rejection.v1",
        "decision": "self-rejected",
        "reason": (
            "The physical Pack and same-case occlusion pass visual inspection, "
            "but the direct CC0 sphere-mask rim and flare output are too dim to "
            "remain recognizable at shipping scale."
        ),
        "correctiveScope": (
            "Correct additive-premultiplication in only the CC0-derived rim and "
            "flare ports. Keep the narrow torn contour, warm-neutral palette, and "
            "all geometry unchanged."
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
