#!/usr/bin/env python3
"""Derive the Gate 07 rev 12 browser check from the stable rev 11 flow."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
source = ROOT / "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07.mjs"
output = ROOT / "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07-r012.mjs"
text = source.read_text(encoding="utf-8")
for old, new in {
    "9226": "9242",
    "rev11": "rev12",
    "rev-011": "rev-012",
    "r011": "r012",
    "Gate 07 rev 11": "Gate 07 rev 12",
}.items():
    text = text.replace(old, new)
text = text.replace(
    'path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate07-rev12-persistent-workbench.png")',
    'path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-persistent-workbench.png")',
)
text = text.replace(
    'path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate07-rev12-workbench-focused.png")',
    'path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-workbench-focused.png")',
)
output.write_text(text, encoding="utf-8")
print(output)
