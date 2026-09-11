#!/usr/bin/env python3
"""Compare Unity-imported vertices with the approved Gate 10 FBX."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector, kdtree


HERE = Path(__file__).resolve().parent
GATE10 = HERE.parent.parent / "10-export/rev-001"
FBX = GATE10 / "premium-display-case-product-r001.fbx"
GATE10_VALIDATOR = GATE10 / "validate_export_roundtrip.py"
GATE10_REPORT = GATE10 / "export-roundtrip-validation.json"
SNAPSHOT = HERE / "unity-vertex-snapshot.csv"
OUTPUT = HERE / "unity-geometry-correspondence.json"
APPROVED_FBX_SHA256 = (
    "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_gate10_validator() -> dict:
    namespace = {
        "__name__": "premium_display_case_gate11_reference",
        "__file__": str(GATE10_VALIDATOR),
    }
    exec(
        compile(
            GATE10_VALIDATOR.read_text(encoding="utf-8"),
            str(GATE10_VALIDATOR),
            "exec",
        ),
        namespace,
    )
    return namespace


def unity_positions(subject_names: tuple[str, ...]) -> dict:
    values = {name: set() for name in subject_names}
    with SNAPSHOT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            name = row["objectName"]
            if name not in values:
                raise RuntimeError(f"Unexpected Unity snapshot object: {name}")
            values[name].add(
                (
                    float(row["xMm"]),
                    float(row["yMm"]),
                    float(row["zMm"]),
                )
            )
    return {name: sorted(points) for name, points in values.items()}


def fbx_positions(namespace: dict) -> tuple[dict, str, float]:
    namespace["reset"]()
    bpy.ops.import_scene.fbx(
        filepath=str(FBX),
        use_custom_props=True,
        use_image_search=False,
    )
    mapping_label, convert, mapping_error = namespace["choose_import_mapping"]()
    positions = {
        name: sorted(
            {
                tuple(
                    float(value)
                    for value in convert(
                        bpy.data.objects[name].matrix_world @ vertex.co
                    )
                )
                for vertex in bpy.data.objects[name].data.vertices
            }
        )
        for name in namespace["SUBJECT_NAMES"]
    }
    return positions, mapping_label, mapping_error


def correspondence(
    expected: dict,
    actual: dict,
    records_digest,
) -> dict:
    maximum_error = 0.0
    all_bijective = True
    per_object = {}
    matched_records = []
    for name, expected_points in expected.items():
        actual_points = actual[name]
        tree = kdtree.KDTree(len(expected_points))
        for index, point in enumerate(expected_points):
            tree.insert(Vector(point), index)
        tree.balance()
        matched_indices = []
        distances = []
        for point in actual_points:
            _, index, distance = tree.find(Vector(point))
            matched_indices.append(index)
            distances.append(distance)
        unique_matches = sorted(set(matched_indices))
        bijective = (
            len(actual_points) == len(expected_points)
            and len(unique_matches) == len(expected_points)
        )
        object_maximum = max(distances, default=0.0)
        maximum_error = max(maximum_error, object_maximum)
        all_bijective = all_bijective and bijective
        matched_records.extend(
            f"{name}:{expected_points[index][0]:.9f},"
            f"{expected_points[index][1]:.9f},"
            f"{expected_points[index][2]:.9f}"
            for index in unique_matches
        )
        per_object[name] = {
            "fbxUniquePositionCount": len(expected_points),
            "unityUniquePositionCount": len(actual_points),
            "bijective": bijective,
            "maximumErrorMm": round(object_maximum, 9),
        }
    authority_records = [
        f"{name}:{point[0]:.9f},{point[1]:.9f},{point[2]:.9f}"
        for name, points in expected.items()
        for point in points
    ]
    return {
        "allObjectsBijective": all_bijective,
        "maximumErrorMm": round(maximum_error, 9),
        "fbxAuthorityDigest": records_digest(authority_records),
        "unityMatchedAuthorityDigest": records_digest(matched_records),
        "perObject": per_object,
    }


def bounds(points: dict) -> dict:
    flattened = [point for values in points.values() for point in values]
    minimum = [min(point[index] for point in flattened) for index in range(3)]
    maximum = [max(point[index] for point in flattened) for index in range(3)]
    return {
        "minimumMm": [round(value, 6) for value in minimum],
        "maximumMm": [round(value, 6) for value in maximum],
        "sizeMm": [
            round(maximum[index] - minimum[index], 6)
            for index in range(3)
        ],
    }


def main() -> None:
    if not SNAPSHOT.exists() or not FBX.exists():
        raise RuntimeError("Gate 11 Unity snapshot or Gate 10 FBX is missing.")
    namespace = load_gate10_validator()
    subject_names = namespace["SUBJECT_NAMES"]
    expected, mapping_label, mapping_error = fbx_positions(namespace)
    actual = unity_positions(subject_names)
    audit = correspondence(expected, actual, namespace["records_digest"])
    expected_bounds = bounds(expected)
    actual_bounds = bounds(actual)
    gate10 = json.loads(GATE10_REPORT.read_text(encoding="utf-8"))
    checks = {
        "approvedFbxHashExact": sha256(FBX) == APPROVED_FBX_SHA256,
        "gate10FbxPassed": gate10["fbx"]["pass"],
        "mappingAnchorWithinPoint001Mm": mapping_error <= 0.001,
        "allObjectsBijective": audit["allObjectsBijective"],
        "maximumErrorWithinPoint001Mm": audit["maximumErrorMm"] <= 0.001,
        "authorityDigestIdentity": (
            audit["fbxAuthorityDigest"]
            == audit["unityMatchedAuthorityDigest"]
        ),
        "boundsWithinPoint001Mm": all(
            abs(expected_bounds["sizeMm"][index] - actual_bounds["sizeMm"][index])
            <= 0.001
            for index in range(3)
        ),
        "expectedObjectCounts": all(
            audit["perObject"][name]["fbxUniquePositionCount"]
            == gate10["fbx"]["perObjectVertexDigests"][name][
                "uniquePositionCount"
            ]
            for name in subject_names
        ),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "11-unity-parity",
        "parityRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceFbxPath": str(FBX),
        "sourceFbxSha256": sha256(FBX),
        "unitySnapshotPath": str(SNAPSHOT),
        "unitySnapshotSha256": sha256(SNAPSHOT),
        "mapping": mapping_label,
        "mappingAnchorErrorMm": round(mapping_error, 9),
        "fbxBounds": expected_bounds,
        "unityBounds": actual_bounds,
        **audit,
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError("Unity-to-FBX geometry correspondence failed.")


if __name__ == "__main__":
    main()
