"""Rebuild the clean 20 mm environment from smooth-normal lighting."""

import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REV6 = HERE.parent / "rev-006"
REV7 = HERE.parent / "rev-007"
LIGHTING_BLEND = (
    HERE.parents[1] / "08-lighting/rev-004/"
    "fan-card-smooth-normal-lighting.blend"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    rebuild = load_module(
        "fan_card_smooth_environment_rebuild",
        REV6 / "rebuild_surreal_72_segments.py",
    )
    rebuild.HERE = HERE
    rebuild.LIGHTING_BLEND = LIGHTING_BLEND
    rebuild.CARD_RAIN_STAGE = HERE / "fan-card-smooth-card-rain-stage.blend"
    rebuild.CARD_RAIN_BASE = HERE / "fan-card-smooth-card-rain-base.blend"
    rebuild.main()

    clean = load_module(
        "fan_card_smooth_environment_clean",
        REV7 / "clean_levitation_20mm.py",
    )
    clean.HERE = HERE
    clean.SOURCE_BLEND = HERE / "fan-card-72-surreal-levitation.blend"
    clean.OUTPUT_BLEND = HERE / "fan-card-smooth-clean-20mm.blend"
    clean.OUTPUT_IMAGE = HERE / "smooth-clean-20mm-preview.png"
    clean.main()

    report_path = HERE / "clean-levitation-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["normalPolicy"] = {
        "sideAndBevel": "smooth",
        "planarCaps": "hard"
    }
    report["environmentChanged"] = False
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
