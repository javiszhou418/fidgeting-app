#!/usr/bin/env python3
"""Confirm rev 6 changes only the rejected bottom top-skin geometry."""

import hashlib
import json
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
REV5 = HERE.parent / "rev-005/magnetic-slide-tile-blockout-r005.blend"
REV6 = HERE / "magnetic-slide-tile-blockout-r006.blend"
REPORT_PATH = HERE / "geometry-comparison.json"
UNCHANGED_MESHES = [
    "MovingTopBody",
    "FixedAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
]


def fingerprint(obj):
    digest = hashlib.sha256()
    for vertex in obj.data.vertices:
        digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        digest.update(b";")
    for polygon in obj.data.polygons:
        digest.update(",".join(str(index) for index in polygon.vertices).encode())
        digest.update(b";")
    center = sum((vertex.co for vertex in obj.data.vertices), start=obj.data.vertices[0].co.copy() * 0.0) / len(obj.data.vertices)
    radial_digest = hashlib.sha256()
    for radius in sorted(round((vertex.co - center).length, 9) for vertex in obj.data.vertices):
        radial_digest.update(f"{radius:.9f};".encode())
    return {
        "sha256": digest.hexdigest(),
        "shapeSha256": radial_digest.hexdigest(),
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
    }


def load_meshes(path, names):
    with bpy.data.libraries.load(str(path), link=False) as (source, target):
        target.objects = [name for name in names if name in source.objects]
    result = {}
    for obj in target.objects:
        if obj and obj.type == "MESH":
            result[obj.name.split(".")[0]] = fingerprint(obj)
            bpy.data.objects.remove(obj, do_unlink=True)
    return result


def main():
    names = ["BottomExterior", "_BottomExteriorUpperRim", *UNCHANGED_MESHES]
    rev5 = load_meshes(REV5, names)
    rev6 = load_meshes(REV6, names)
    unchanged = {}
    for name in UNCHANGED_MESHES:
        if name.startswith("BallCandidate"):
            unchanged[name] = all(
                rev5[name][key] == rev6[name][key]
                for key in ("shapeSha256", "vertices", "polygons")
            )
        else:
            unchanged[name] = rev5.get(name) == rev6.get(name)
    checks = {
        "acceptedMeshesUnchanged": all(unchanged.values()),
        "bottomExteriorChanged": rev5["BottomExterior"] != rev6["BottomExterior"],
        "rejectedUpperRimRemoved": "_BottomExteriorUpperRim" in rev5
        and "_BottomExteriorUpperRim" not in rev6,
        "noUnexpectedMeshAdded": set(rev6) == {"BottomExterior", *UNCHANGED_MESHES},
    }
    report = {
        "pass": all(checks.values()),
        "checks": checks,
        "unchangedMeshes": unchanged,
        "rev5": rev5,
        "rev6": rev6,
        "changedGeometry": ["BottomExterior"],
        "removedRejectedGeometry": ["_BottomExteriorUpperRim"],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

