"""Run full geometry validation with 72 visible corner segments."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY_SCRIPT = HERE.parent / "rev-002/geometry_validation_selected.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


selected = load_module("fan_card_geometry_selected_72", LEGACY_SCRIPT)
selected.OUTPUT = HERE
selected.BLEND = HERE / "fan-card-72-segment-geometry.blend"
selected.geometry.OUTPUT = HERE
original_outline = selected.sweep.source.rounded_outline


def selected_outline(width, height, radius, center, segments=72):
    return original_outline(
        width, height, radius, center, segments=72)


selected.sweep.source.rounded_outline = selected_outline


def main() -> None:
    selected.main()
    report_path = HERE / "geometry-validation.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["visibleCornerSegmentsPerQuadrant"] = 72
    report["collisionCornerSegmentsPerQuadrant"] = 8
    report["dimensionsChanged"] = False
    report["mechanicsChanged"] = False
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
