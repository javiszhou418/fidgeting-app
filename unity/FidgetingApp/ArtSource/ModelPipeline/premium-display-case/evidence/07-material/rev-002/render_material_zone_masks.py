#!/usr/bin/env python3
"""Render temporary flat masks for Gate 07 material-zone diagnostics."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "premium-display-case-material-r002.blend"
MASKS = ROOT / "masks"
REPORT = ROOT / "material-zone-mask-report.json"
ANGLES = (0, 90, 180, 270, 360)
ZONE_OBJECTS = {
    "label-zone": (
        "PhysicalLabel",
        "M07_NarrowFoilProxy",
        "M07_IdentityPlaceholder",
        "M07_AchievementPlaceholder",
        "M07_LabelPrimary",
        "M07_LabelSecondary",
        "M07_NeutralPrintBarPrimary",
        "M07_NeutralPrintBarSecondary",
        "M07_NeutralPrintBarMetadata",
        "M07_IdentityAreaText",
        "M07_AchievementAreaText",
    ),
    "insert-zone": ("TactileBackgroundInsert",),
    "foil-zone": ("M07_NarrowFoilProxy",),
}


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    root = bpy.data.objects["PresentationRoot"]
    camera = bpy.data.objects["M07_RotationCamera"]
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 780
    scene.render.resolution_percentage = 100
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (1.0, 1.0, 1.0)
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.show_specular_highlight = False
    paths = []
    for angle in ANGLES:
        root.rotation_euler[1] = 0.0 if angle == 360 else math.radians(angle)
        bpy.context.view_layer.update()
        for zone, names in ZONE_OBJECTS.items():
            allowed = {bpy.data.objects[name] for name in names}
            for obj in scene.objects:
                if obj.type in {"MESH", "CURVE", "FONT"}:
                    obj.hide_render = obj not in allowed
            path = MASKS / f"{zone}-{angle:03d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            paths.append(
                {
                    "zone": zone,
                    "angleDegrees": angle,
                    "path": str(path.relative_to(REPO_ROOT)),
                    "sha256": sha256(path),
                }
            )
    root.rotation_euler[1] = 0.0
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 2,
        "purpose": "temporary-flat-material-zone-mask-diagnostic",
        "persistentMaterialMutation": False,
        "persistentEmission": False,
        "geometryAdded": False,
        "paths": paths,
        "status": "pass",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "pass", "maskCount": len(paths)}))


if __name__ == "__main__":
    main()
