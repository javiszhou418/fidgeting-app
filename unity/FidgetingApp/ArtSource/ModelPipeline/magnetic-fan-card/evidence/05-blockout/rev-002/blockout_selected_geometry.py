"""Render A/B/C blockouts for the selected thicker rounded geometry."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
SWEEP_SCRIPT = (
    SCRIPT.parents[2] / "03-contract/rev-004/model_change_sweep.py"
)
spec = importlib.util.spec_from_file_location(
    "fan_card_model_change_sweep", SWEEP_SCRIPT)
sweep = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = sweep
spec.loader.exec_module(sweep)
sweep.OUTPUT = SCRIPT.parent

variant = sweep.Variant(
    thickness_mm=3.5,
    radius_mm=9.5,
    black_border_mm=1.0,
    gold_trim_mm=0.8,
    trim_bevel_mm=0.38,
)
original_material = sweep.source.material
support_colors = {
    "A-dark-walnut": (0.13, 0.055, 0.018, 1.0),
    "B-charcoal-hard-case": (0.012, 0.015, 0.020, 1.0),
    "C-cork-slab": (0.24, 0.12, 0.045, 1.0),
}
outputs = {}

for support_id, support_color in support_colors.items():
    def blockout_material(name, color, metallic, roughness,
                          bump_strength, support_color=support_color):
        if name == "MAT_CharcoalSupport":
            return original_material(
                name, support_color, 0.0, 0.82, 110.0)
        if name == "MAT_GoldTrim":
            return original_material(
                name, (0.52, 0.30, 0.09, 1.0),
                0.0, 0.58, 0.0)
        if name == "MAT_Gunmetal":
            return original_material(
                name, (0.16, 0.18, 0.21, 1.0),
                0.0, 0.72, 0.0)
        return original_material(
            name, (0.62, 0.63, 0.64, 1.0),
            0.0, 0.68, 0.0)

    sweep.source.material = blockout_material
    filename = f"blockout-{support_id}.png"
    sweep.setup_and_render(variant, filename)
    outputs[support_id] = filename

(SCRIPT.parent / "blockout-report.json").write_text(
    json.dumps({
        "geometry": {
            "cardMm": [63.5, 88.9, 3.5],
            "cornerRadiusMm": 9.5,
            "blackBorderMm": 1.0,
            "goldTrimMm": 0.8,
            "goldTrimBevelMm": 0.38
        },
        "outputs": outputs,
        "shippingAssetModified": False
    }, indent=2) + "\n",
    encoding="utf-8")
