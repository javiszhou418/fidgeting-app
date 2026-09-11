#!/usr/bin/env python3
"""Preserve the first R013 Blender rig before contour refinement."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "iterations" / "iteration-05-geometry-self-rejection" / "blender-source"
PROJECT = ROOT.parents[5]
RIG = PROJECT / "Assets/_DisplayCase/Candidates/PackOpeningGate04R013/Imported/PackOpeningGate04R013PackOnlyRig.fbx"
ITEMS = (
    ROOT / "pack-opening-gate04-r013.blend",
    RIG,
    ROOT / "blender-rig-build-report.json",
    ROOT / "blender-rig-closed.png",
    ROOT / "blender-rig-open-075.png",
)


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=False)
    copied: list[str] = []
    for source in ITEMS:
        if source.exists():
            shutil.copy2(source, TARGET / source.name)
            copied.append(source.name)
    (TARGET / "archive.json").write_text(
        json.dumps(
            {
                "reason": "Pre-refinement Pack-only Blender rig.",
                "copiedArtifacts": copied,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"copiedArtifacts": copied}, indent=2))


if __name__ == "__main__":
    main()
