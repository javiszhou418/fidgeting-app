"""Audit the saved 72-segment geometry scene."""

import json
import math
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
BLEND = HERE / "fan-card-72-segment-geometry.blend"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    roots = [bpy.data.objects[name] for name in (
        "BottomCard", "MiddleCard", "TopCard")]
    bodies = [
        bpy.data.objects[f"{root.name}_GunmetalFrame"]
        for root in roots
    ]
    body_stats = {}
    for body in bodies:
        body_stats[body.name] = {
            "vertices": len(body.data.vertices),
            "triangles": sum(
                len(polygon.vertices) - 2
                for polygon in body.data.polygons),
            "dimensionsMm": [
                round(value * 1000, 6)
                for value in body.dimensions
            ],
        }
    tracks = [
        obj.parent.name for obj in meshes
        if "Track_Grille" in obj.name
    ]
    followers = [
        obj.parent.name for obj in meshes
        if "FollowerBearing" in obj.name
    ]
    report = {
        "modelId": "magnetic-fan-card",
        "visibleCornerSegmentsPerQuadrant": 72,
        "meshObjects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "triangles": sum(
            len(polygon.vertices) - 2
            for obj in meshes
            for polygon in obj.data.polygons),
        "bodyStats": body_stats,
        "layerZMillimetres": [
            round(root.location.z * 1000, 6) for root in roots
        ],
        "layerAnglesDegrees": [
            round(math.degrees(root.rotation_euler.z), 6)
            for root in roots
        ],
        "trackParents": sorted(tracks),
        "followerParents": sorted(followers),
        "checks": {
            "bodyTopologyIncreased": all(
                item["vertices"] >= 2500 for item in body_stats.values()),
            "layerPitchPreserved": [
                round(root.location.z * 1000, 6) for root in roots
            ] == [0.0, 4.5, 9.0],
            "anglesPreserved": [
                round(math.degrees(root.rotation_euler.z))
                for root in roots
            ] == [0, 45, 90],
            "tracksPreserved": sorted(tracks)
            == ["MiddleCard", "TopCard"],
            "followersPreserved": sorted(followers)
            == ["BottomCard", "MiddleCard"],
        },
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "geometry-audit.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
