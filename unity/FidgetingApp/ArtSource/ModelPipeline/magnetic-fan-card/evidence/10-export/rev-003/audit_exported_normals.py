"""Verify FBX preserves smooth side/bevel and hard cap normals."""

import json
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
FBX = HERE / "magnetic-fan-card.fbx"
TOKENS = ("GunmetalFrame", "GoldTrim", "WarmSilverFace")


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX))
    objects = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and any(token in obj.name for token in TOKENS)
    ]
    records = {}
    for obj in objects:
        smooth = sum(polygon.use_smooth for polygon in obj.data.polygons)
        flat = len(obj.data.polygons) - smooth
        records[obj.name] = {
            "vertices": len(obj.data.vertices),
            "triangles": sum(
                len(polygon.vertices) - 2
                for polygon in obj.data.polygons),
            "smoothPolygons": smooth,
            "flatPolygons": flat,
            "pass": smooth > 0 and flat > 0,
        }
    report = {
        "modelId": "magnetic-fan-card",
        "fbx": FBX.name,
        "visualMeshes": len(objects),
        "objects": records,
        "pass": len(objects) == 9
            and all(record["pass"] for record in records.values()),
    }
    (HERE / "exported-normal-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
