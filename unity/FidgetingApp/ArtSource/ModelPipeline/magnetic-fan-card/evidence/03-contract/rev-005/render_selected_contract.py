"""Render the user-selected combined geometry contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
SWEEP_SCRIPT = (
    SCRIPT.parents[1] / "rev-004/model_change_sweep.py"
)
spec = importlib.util.spec_from_file_location(
    "fan_card_model_change_sweep", SWEEP_SCRIPT)
sweep = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = sweep
spec.loader.exec_module(sweep)
sweep.OUTPUT = SCRIPT.parent
original_add_bearing = sweep.source.add_bearing


def add_chrome_bearing(_material) -> None:
    chrome = sweep.source.material(
        "MAT_ChromeCap",
        (0.72, 0.78, 0.86, 1.0),
        1.0,
        0.12,
        920.0,
    )
    original_add_bearing(chrome)


sweep.source.add_bearing = add_chrome_bearing
sweep.setup_and_render(
    sweep.Variant(
        thickness_mm=3.5,
        radius_mm=9.5,
        black_border_mm=1.0,
        gold_trim_mm=0.8,
        trim_bevel_mm=0.38,
    ),
    "selected-geometry-contract.png",
)
