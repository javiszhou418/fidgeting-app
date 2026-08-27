#!/usr/bin/env python3
"""Re-render the unchanged Blender control into immutable Gate 11 rev 2."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REV1 = ROOT.parent / "rev-001" / "render_blender_neutral.py"
spec = importlib.util.spec_from_file_location("gate11_rev1_renderer", REV1)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ROOT = ROOT
module.RECIPE = module.json.loads((ROOT / "neutral-camera-recipe.json").read_text())
module.OUTPUT = ROOT / "blender-neutral.png"
module.SILHOUETTE = ROOT / "blender-neutral-silhouette.png"
module.REPORT = ROOT / "blender-neutral-report.json"
module.main()
report = module.json.loads(module.REPORT.read_text())
report["revision"] = 2
report["sourceGeometryChanged"] = False
report["sourceMaterialChanged"] = False
report["sourceCameraChanged"] = False
report["sourceRevision"] = "../rev-001"
module.REPORT.write_text(module.json.dumps(report, indent=2) + "\n")
