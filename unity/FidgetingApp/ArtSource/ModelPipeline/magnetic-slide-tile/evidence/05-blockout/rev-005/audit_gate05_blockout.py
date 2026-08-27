#!/usr/bin/env python3
"""Independently audit the saved Gate 05 rev 5 blend."""

import json
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "blender-audit.json"
EXPECTED_HASH = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"


def nonmanifold_edges(obj):
    uses = {}
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, first in enumerate(vertices):
            edge = tuple(sorted((first, vertices[(index + 1) % len(vertices)])))
            uses[edge] = uses.get(edge, 0) + 1
    return sum(1 for count in uses.values() if count != 2)


def main():
    scene = bpy.context.scene
    objects = bpy.data.objects
    expected_parents = {
        "BottomExterior": "MagneticSlideTile_G05_R005",
        "FixedAxisBoss": "BottomExterior",
        "FixedAxis": "FixedAxisBoss",
        "MinimumOverlapDisk": "BottomExterior",
        "RotatingCarrier": "FixedAxisBoss",
        "RotatingCarrierBody": "RotatingCarrier",
        "CarrierFollowerLeft": "RotatingCarrier",
        "CarrierFollowerRight": "RotatingCarrier",
        "BallCandidateLeft": "RotatingCarrier",
        "BallCandidateRight": "RotatingCarrier",
        "MovingTop": "MagneticSlideTile_G05_R005",
        "TopLocalSlide": "MovingTop",
        "MovingTopBody": "TopLocalSlide",
        "TopOuterGrooveLeft": "MovingTopBody",
        "TopInnerGrooveLeft": "MovingTopBody",
        "TopInnerGrooveRight": "MovingTopBody",
        "TopOuterGrooveRight": "MovingTopBody",
    }
    missing = [name for name in expected_parents if name not in objects]
    wrong_parents = {
        name: objects[name].parent.name if objects[name].parent else None
        for name, parent in expected_parents.items()
        if name in objects and (objects[name].parent.name if objects[name].parent else None) != parent
    }
    animated = [
        obj.name for obj in objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    meshes = [
        "BottomExterior",
        "_BottomExteriorUpperRim",
        "FixedAxisBoss",
        "RotatingCarrierBody",
        "MovingTopBody",
    ]
    manifold = {name: nonmanifold_edges(objects[name]) for name in meshes}
    checks = {
        "contractHash": scene.get("mechanism_contract_sha256") == EXPECTED_HASH,
        "revision": scene.get("revision") == 5,
        "noMissingObjects": not missing,
        "hierarchy": not wrong_parents,
        "fourGrooves": objects["MovingTopBody"].get("groove_count") == 4,
        "raisedBoss": objects["FixedAxisBoss"].get("protrusion_mm", 0) > 0,
        "noRecessedAxis": objects["FixedAxisBoss"].get("recessed_axis") is False,
        "smoothBottom": objects["BottomExterior"].get("cavity") is False,
        "carrierCutouts": objects["RotatingCarrierBody"].get("bilateral_side_clearances") is True,
        "ballCandidates": all(objects[name].get("candidate_only") is True for name in ["BallCandidateLeft", "BallCandidateRight"]),
        "unknownEngineering": objects["UnknownSprings"].get("count") == "unknown" and objects["UnknownPreload"].get("value") == "unknown",
        "manifold": all(count == 0 for count in manifold.values()),
        "zeroSelfMotion": scene.get("self_motion") is False and not animated,
        "oneFrame": scene.frame_start == 1 and scene.frame_end == 1,
    }
    report = {
        "schemaVersion": 1,
        "pass": all(checks.values()),
        "blenderVersion": bpy.app.version_string,
        "checks": checks,
        "missingObjects": missing,
        "wrongParents": wrong_parents,
        "nonmanifoldEdges": manifold,
        "animatedObjects": animated,
        "objectCount": len(objects),
    }
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

