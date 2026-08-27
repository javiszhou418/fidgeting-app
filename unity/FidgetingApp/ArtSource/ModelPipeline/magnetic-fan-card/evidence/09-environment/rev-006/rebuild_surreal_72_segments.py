"""Rebuild Card Rain and Surreal Levitation with 72-segment geometry."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
REV4 = HERE.parent / "rev-004"
REV5 = HERE.parent / "rev-005"
LIGHTING_BLEND = (
    HERE.parents[1] / "08-lighting/rev-003/"
    "fan-card-72-segment-lighting.blend"
)
CARD_RAIN_STAGE = HERE / "fan-card-72-card-rain-stage.blend"
CARD_RAIN_BASE = HERE / "fan-card-72-card-rain-base.blend"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    stage = load_module(
        "fan_card_full_scene_72",
        REV4 / "full_scene_redesign.py",
    )
    stage.HERE = HERE
    stage.SOURCE_BLEND = LIGHTING_BLEND
    stage.OUTPUT_BLEND = CARD_RAIN_STAGE
    stage.main()

    selector = load_module(
        "fan_card_card_rain_selector_72",
        REV4 / "render_selected_card_rain_final.py",
    )
    bpy.ops.wm.open_mainfile(filepath=str(CARD_RAIN_STAGE))
    scene = bpy.context.scene
    camera = bpy.data.objects["CAM_Hero_Selected"]
    selector.configure_selected_direction(scene, camera)
    bpy.data.objects["LGT_STAGE_GoldRim"].data.energy = 3.4
    bpy.data.objects["LGT_STAGE_TableGold"].data.energy = 0.56
    bpy.ops.wm.save_as_mainfile(filepath=str(CARD_RAIN_BASE))

    surreal = load_module(
        "fan_card_surreal_72",
        REV5 / "surreal_levitation_scene.py",
    )
    surreal.HERE = HERE
    surreal.SOURCE_BLEND = CARD_RAIN_BASE
    surreal.OUTPUT_BLEND = HERE / "fan-card-72-surreal-levitation.blend"
    surreal.OUTPUT_IMAGE = HERE / "surreal-levitation-72-preview.png"
    surreal.main()

    report_path = HERE / "surreal-levitation-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["visibleCornerSegmentsPerQuadrant"] = 72
    report["collisionCornerSegmentsPerQuadrant"] = 8
    report["dimensionsChanged"] = False
    report["environmentChanged"] = False
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
