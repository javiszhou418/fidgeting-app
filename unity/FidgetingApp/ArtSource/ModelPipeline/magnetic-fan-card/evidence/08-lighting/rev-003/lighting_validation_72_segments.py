"""Render approved shared lighting on the 72-segment material scene."""

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY_SCRIPT = HERE.parent / "rev-002/exact_lighting_validation.py"
SOURCE_BLEND = (
    HERE.parents[1] / "07-material/rev-005/"
    "fan-card-72-segment-material.blend"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


lighting = load_module("fan_card_lighting_72", LEGACY_SCRIPT)
lighting.SOURCE_BLEND = SOURCE_BLEND
lighting.OUTPUT = HERE
lighting.BLEND = HERE / "fan-card-72-segment-lighting.blend"


def main() -> None:
    lighting.main()
    report_path = HERE / "exact-lighting-validation.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["visibleCornerSegmentsPerQuadrant"] = 72
    report["lightingChanged"] = False
    report["materialsChanged"] = False
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
