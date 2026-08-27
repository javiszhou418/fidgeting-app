"""Apply approved materials to the authoritative smooth-normal geometry."""

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY_SCRIPT = HERE.parent / "rev-004/exact_material_lookdev.py"
GEOMETRY_BLEND = (
    HERE.parents[1] / "06-geometry/rev-004/"
    "fan-card-72-smooth-normal-geometry.blend"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


lookdev = load_module("fan_card_material_smooth_normals", LEGACY_SCRIPT)
lookdev.GEOMETRY_BLEND = GEOMETRY_BLEND
lookdev.OUTPUT = HERE
lookdev.BLEND = HERE / "fan-card-smooth-normal-material.blend"


def main() -> None:
    lookdev.main()
    report_path = HERE / "exact-material-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["visibleCornerSegmentsPerQuadrant"] = 72
    report["normalPolicy"] = {
        "sideAndBevel": "smooth",
        "planarCaps": "hard"
    }
    report["unityShaderPolicy"] = {
        "objectSpaceSoftPanel": False,
        "objectSpaceReflectedBand": False,
        "lighting": "main light + spherical harmonics + rough specular"
    }
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
