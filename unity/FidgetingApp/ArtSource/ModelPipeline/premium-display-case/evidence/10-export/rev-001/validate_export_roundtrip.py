#!/usr/bin/env python3
"""Fresh-scene round-trip validation for the Gate 10 FBX and GLB exports."""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Callable

import bpy
from mathutils import Vector
from mathutils import kdtree


HERE = Path(__file__).resolve().parent
PRODUCT_BLEND = HERE / "premium-display-case-product-r001.blend"
FBX_EXPORT = HERE / "premium-display-case-product-r001.fbx"
GLB_EXPORT = HERE / "premium-display-case-product-r001.glb"
BUILD_REPORT = HERE / "export-build-report.json"
ROUNDTRIP_REPORT = HERE / "export-roundtrip-validation.json"
GLB_STRUCTURE_REPORT = HERE / "glb-structure-validation.json"

EXPECTED_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
PRODUCT_OBJECTS = (
    "PresentationRoot",
    "CaseAssembly",
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "ContentSlot",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
    "LogoZone",
    "AchievementZone",
    "NarrowFoil",
    "TransparentCover",
)
EXPECTED_PARENTS = {
    "PresentationRoot": None,
    "CaseAssembly": "PresentationRoot",
    "RearPolycarbonateShell": "CaseAssembly",
    "TactileBackgroundInsert": "RearPolycarbonateShell",
    "ContentSlot": "RearPolycarbonateShell",
    "FrontPolycarbonateShell": "CaseAssembly",
    "ContinuousTubePerimeter": "FrontPolycarbonateShell",
    "PhysicalLabel": "FrontPolycarbonateShell",
    "LogoZone": "PhysicalLabel",
    "AchievementZone": "PhysicalLabel",
    "NarrowFoil": "PhysicalLabel",
    "TransparentCover": "FrontPolycarbonateShell",
}
EXPECTED_ASSIGNMENTS = {
    "RearPolycarbonateShell": ["MAT_FrostedPolycarbonate"],
    "TactileBackgroundInsert": ["MAT_BlackFlocking"],
    "FrontPolycarbonateShell": ["MAT_FrostedPolycarbonate"],
    "ContinuousTubePerimeter": ["MAT_FrostedPolycarbonateEdge"],
    "PhysicalLabel": ["MAT_LabelPaper"],
}
EXPECTED_ANCHORS_MM = {
    "PhysicalLabel": (0.0, 99.0, 24.0),
    "FrontPolycarbonateShell": (0.0, 0.0, 20.0),
    "RearPolycarbonateShell": (0.0, 0.0, -26.0),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material_assignments() -> dict[str, list[str]]:
    return {
        name: [
            material.name
            for material in bpy.data.objects[name].data.materials
            if material is not None
        ]
        for name in SUBJECT_NAMES
    }


def parent_map() -> dict[str, str | None]:
    return {
        name: (
            bpy.data.objects[name].parent.name
            if bpy.data.objects[name].parent is not None
            else None
        )
        for name in PRODUCT_OBJECTS
        if name in bpy.data.objects
    }


def rounded_point(point: Vector, digits: int = 2) -> tuple[float, float, float]:
    threshold = 0.5 * (10 ** -digits)
    return tuple(
        0.0 if abs(float(value)) < threshold else round(float(value), digits)
        for value in point
    )


def source_mapping(point: Vector) -> Vector:
    return Vector((point.x, point.y, point.z))


def imported_mapping(
    signs: tuple[int, int, int],
) -> Callable[[Vector], Vector]:
    first, second, third = signs

    def convert(point: Vector) -> Vector:
        return Vector((
            first * point.x * 1000.0,
            second * point.z * 1000.0,
            third * point.y * 1000.0,
        ))

    return convert


def mapping_determinant(signs: tuple[int, int, int]) -> int:
    # Axis permutation X,Z,Y is odd.
    return -signs[0] * signs[1] * signs[2]


def choose_import_mapping() -> tuple[str, Callable[[Vector], Vector], float]:
    candidates = [
        signs
        for signs in (
            (1, 1, -1),
            (-1, 1, 1),
            (1, -1, 1),
            (-1, -1, -1),
        )
        if mapping_determinant(signs) == 1
    ]
    scored = []
    for signs in candidates:
        convert = imported_mapping(signs)
        error = 0.0
        for name, expected in EXPECTED_ANCHORS_MM.items():
            point = convert(bpy.data.objects[name].matrix_world.translation)
            error += sum((point[index] - expected[index]) ** 2 for index in range(3))
        scored.append((error, signs, convert))
    error, signs, convert = min(scored, key=lambda item: item[0])
    label = f"canonical=(X*{signs[0]},Z*{signs[1]},Y*{signs[2]})*1000"
    return label, convert, math.sqrt(error)


def canonical_triangles(
    convert: Callable[[Vector], Vector],
) -> tuple[list[str], list[str], dict[str, float], int, int]:
    geometry_records: list[str] = []
    winding_records: list[str] = []
    signed_volumes: dict[str, float] = {}
    triangle_count = 0
    degenerate_count = 0
    for name in SUBJECT_NAMES:
        obj = bpy.data.objects[name]
        mesh = obj.data
        mesh.calc_loop_triangles()
        signed_volume = 0.0
        for triangle in mesh.loop_triangles:
            points = [
                convert(obj.matrix_world @ mesh.vertices[index].co)
                for index in triangle.vertices
            ]
            edge_a = points[1] - points[0]
            edge_b = points[2] - points[0]
            if edge_a.cross(edge_b).length <= 1e-8:
                degenerate_count += 1
            signed_volume += points[0].dot(points[1].cross(points[2])) / 6.0
            tuples = [rounded_point(point) for point in points]
            geometry = "|".join(
                ",".join(f"{value:.2f}" for value in point)
                for point in sorted(tuples)
            )
            cyclic = [
                tuples[index:] + tuples[:index]
                for index in range(3)
            ]
            oriented = min(cyclic)
            winding = "|".join(
                ",".join(f"{value:.2f}" for value in point)
                for point in oriented
            )
            geometry_records.append(f"{name}:{geometry}")
            winding_records.append(f"{name}:{winding}")
            triangle_count += 1
        signed_volumes[name] = round(signed_volume, 3)
    return (
        sorted(geometry_records),
        sorted(winding_records),
        signed_volumes,
        triangle_count,
        degenerate_count,
    )


def records_digest(records: list[str]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def canonical_vertex_digest(convert: Callable[[Vector], Vector]) -> str:
    records = []
    for name in SUBJECT_NAMES:
        obj = bpy.data.objects[name]
        points = {
            rounded_point(convert(obj.matrix_world @ vertex.co))
            for vertex in obj.data.vertices
        }
        records.extend(
            f"{name}:{','.join(f'{value:.2f}' for value in point)}"
            for point in sorted(points)
        )
    return records_digest(records)


def canonical_vertex_positions(
    convert: Callable[[Vector], Vector],
) -> dict[str, list[tuple[float, float, float]]]:
    return {
        name: sorted({
            tuple(float(value) for value in convert(
                bpy.data.objects[name].matrix_world @ vertex.co
            ))
            for vertex in bpy.data.objects[name].data.vertices
        })
        for name in SUBJECT_NAMES
    }


def source_position_digest(
    positions: dict[str, list[tuple[float, float, float]]],
) -> str:
    records = [
        f"{name}:{point[0]:.9f},{point[1]:.9f},{point[2]:.9f}"
        for name in SUBJECT_NAMES
        for point in positions[name]
    ]
    return records_digest(records)


def correspondence_audit(
    convert: Callable[[Vector], Vector],
    expected_positions: dict[str, list[tuple[float, float, float]]],
) -> dict:
    actual_positions = canonical_vertex_positions(convert)
    matched_records = []
    per_object = {}
    all_bijective = True
    maximum_error = 0.0
    for name in SUBJECT_NAMES:
        expected = expected_positions[name]
        actual = actual_positions[name]
        tree = kdtree.KDTree(len(expected))
        for index, point in enumerate(expected):
            tree.insert(Vector(point), index)
        tree.balance()
        matched_indices = []
        errors = []
        for point in actual:
            _, index, distance = tree.find(Vector(point))
            matched_indices.append(index)
            errors.append(distance)
        bijective = (
            len(actual) == len(expected)
            and len(set(matched_indices)) == len(expected)
        )
        all_bijective = all_bijective and bijective
        object_maximum = max(errors, default=0.0)
        maximum_error = max(maximum_error, object_maximum)
        matched_records.extend(
            f"{name}:{expected[index][0]:.9f},"
            f"{expected[index][1]:.9f},{expected[index][2]:.9f}"
            for index in sorted(set(matched_indices))
        )
        per_object[name] = {
            "expectedUniquePositions": len(expected),
            "actualUniquePositions": len(actual),
            "bijective": bijective,
            "maximumErrorMm": round(object_maximum, 9),
        }
    return {
        "normalizedDigest": records_digest(matched_records),
        "allObjectsBijective": all_bijective,
        "maximumErrorMm": round(maximum_error, 9),
        "perObject": per_object,
    }


def canonical_vertex_snapshot(convert: Callable[[Vector], Vector]) -> dict:
    snapshot = {}
    for name in SUBJECT_NAMES:
        obj = bpy.data.objects[name]
        points = sorted({
            rounded_point(convert(obj.matrix_world @ vertex.co))
            for vertex in obj.data.vertices
        })
        records = [
            f"{name}:{','.join(f'{value:.2f}' for value in point)}"
            for point in points
        ]
        snapshot[name] = {
            "uniquePositionCount": len(points),
            "digest": records_digest(records),
        }
    return snapshot


def volume_errors(
    actual: dict[str, float],
    expected: dict[str, float],
) -> dict[str, float]:
    return {
        name: round(
            abs(actual[name] - expected[name]) / max(abs(expected[name]), 1e-9),
            9,
        )
        for name in SUBJECT_NAMES
    }


def canonical_bounds(convert: Callable[[Vector], Vector]) -> dict:
    points = [
        convert(bpy.data.objects[name].matrix_world @ Vector(corner))
        for name in SUBJECT_NAMES
        for corner in bpy.data.objects[name].bound_box
    ]
    minimum = Vector((
        min(point.x for point in points),
        min(point.y for point in points),
        min(point.z for point in points),
    ))
    maximum = Vector((
        max(point.x for point in points),
        max(point.y for point in points),
        max(point.z for point in points),
    ))
    extent = maximum - minimum
    return {
        "minimumMm": [round(value, 5) for value in minimum],
        "maximumMm": [round(value, 5) for value in maximum],
        "sizeMm": {
            "width": round(extent.x, 6),
            "height": round(extent.y, 6),
            "depth": round(extent.z, 6),
        },
    }


def bounds_within_tolerance(bounds: dict, tolerance_mm: float = 0.001) -> bool:
    expected = {"width": 228.0, "height": 304.0, "depth": 59.0}
    return all(
        abs(bounds["sizeMm"][key] - value) <= tolerance_mm
        for key, value in expected.items()
    )


def uv_audit() -> dict:
    label = bpy.data.objects["PhysicalLabel"]
    layers = [layer.name for layer in label.data.uv_layers]
    coordinates = [
        tuple(layer.data[loop.index].uv)
        for layer in label.data.uv_layers
        for loop in label.data.loops
    ]
    return {
        "layers": layers,
        "coordinateCount": len(coordinates),
        "minimum": [
            round(min(value[index] for value in coordinates), 6)
            for index in range(2)
        ] if coordinates else None,
        "maximum": [
            round(max(value[index] for value in coordinates), 6)
            for index in range(2)
        ] if coordinates else None,
    }


def raw_bounds() -> list[float]:
    points = [
        bpy.data.objects[name].matrix_world @ Vector(corner)
        for name in SUBJECT_NAMES
        for corner in bpy.data.objects[name].bound_box
    ]
    minimum = [min(point[index] for point in points) for index in range(3)]
    maximum = [max(point[index] for point in points) for index in range(3)]
    return [round(maximum[index] - minimum[index], 7) for index in range(3)]


def audit_loaded_scene(
    format_name: str,
    convert: Callable[[Vector], Vector],
    mapping_label: str,
    mapping_error_mm: float,
    expected_geometry_digest: str,
    expected_signed_volumes: dict[str, float],
    expected_positions: dict[str, list[tuple[float, float, float]]],
) -> dict:
    objects = list(bpy.context.scene.objects)
    object_names = {obj.name for obj in objects}
    triangles, winding, volumes, triangle_count, degenerate_count = (
        canonical_triangles(convert)
    )
    raw_geometry_digest = canonical_vertex_digest(convert)
    correspondence = correspondence_audit(convert, expected_positions)
    geometry_digest = correspondence["normalizedDigest"]
    triangulated_surface_digest = records_digest(triangles)
    winding_digest = records_digest(winding)
    signed_volume_relative_errors = volume_errors(
        volumes,
        expected_signed_volumes,
    )
    bounds = canonical_bounds(convert)
    uv = uv_audit()
    label_center = convert(
        bpy.data.objects["PhysicalLabel"].matrix_world.translation
    )
    root_center = convert(
        bpy.data.objects["PresentationRoot"].matrix_world.translation
    )
    type_counts = {
        object_type: sum(obj.type == object_type for obj in objects)
        for object_type in ("EMPTY", "MESH", "CAMERA", "LIGHT", "FONT", "CURVE")
    }
    checks = {
        "objectSetExact": object_names == set(PRODUCT_OBJECTS),
        "objectCountExact": len(objects) == len(PRODUCT_OBJECTS),
        "fiveMeshesSevenEmpties": (
            type_counts["MESH"] == 5 and type_counts["EMPTY"] == 7
        ),
        "hierarchyExact": parent_map() == EXPECTED_PARENTS,
        "canonicalMappingProperRotation": mapping_error_mm <= 0.001,
        "boundsExact": bounds_within_tolerance(bounds),
        "labelCenterExact": all(
            abs(label_center[index] - (0.0, 99.0, 24.0)[index]) <= 0.001
            for index in range(3)
        ),
        "pivotAtOrigin": root_center.length <= 0.001,
        "materialAssignmentsExact": material_assignments() == EXPECTED_ASSIGNMENTS,
        "labelUvPresent": bool(uv["layers"]),
        "labelUvNormalized": (
            uv["minimum"] is not None
            and min(uv["minimum"]) >= -0.000001
            and max(uv["maximum"]) <= 1.000001
        ),
        "geometryDigestIdentity": geometry_digest == expected_geometry_digest,
        "vertexCorrespondenceWithinPoint001Mm": (
            correspondence["allObjectsBijective"]
            and correspondence["maximumErrorMm"] <= 0.001
        ),
        "windingOrientationPreserved": (
            all(value > 0 for value in volumes.values())
            and max(signed_volume_relative_errors.values()) <= 0.00005
        ),
        "positiveSignedMaterialVolumes": all(
            value > 0 for value in volumes.values()
        ),
        "noDegenerateTriangles": degenerate_count == 0,
        "noAnimation": (
            not bpy.data.actions
            and all(obj.animation_data is None for obj in objects)
        ),
        "noCameraLightOrEnvironmentObjects": all(
            type_counts[kind] == 0
            for kind in ("CAMERA", "LIGHT", "FONT", "CURVE")
        ),
        "contentSlotEmpty": len(bpy.data.objects["ContentSlot"].children) == 0,
        "noToyPrizeProxyExplodedOrCollision": not any(
            token in name.lower()
            for name in object_names
            for token in (
                "toy",
                "prize",
                "proxy",
                "exploded",
                "collider",
                "collision",
                "ucx_",
            )
        ),
        "noPlaceholderTextOrIdObjects": not any(
            token in name.lower()
            for name in object_names
            for token in ("placeholder", "labelprimary", "labelsecondary", "identity")
        ),
    }
    return {
        "format": format_name,
        "objects": sorted(object_names),
        "objectCount": len(objects),
        "typeCounts": type_counts,
        "parentMap": parent_map(),
        "rawImportedBounds": raw_bounds(),
        "canonicalMapping": mapping_label,
        "canonicalMappingAnchorErrorMm": round(mapping_error_mm, 8),
        "canonicalBounds": bounds,
        "labelCenterMm": [round(value, 6) for value in label_center],
        "presentationRootPivotMm": [round(value, 6) for value in root_center],
        "materials": material_assignments(),
        "labelUv": uv,
        "triangleCount": triangle_count,
        "signedVolumesMm3": volumes,
        "signedVolumeRelativeErrors": signed_volume_relative_errors,
        "geometryDigest": geometry_digest,
        "rawQuantizedVertexDigest": raw_geometry_digest,
        "vertexCorrespondence": correspondence,
        "perObjectVertexDigests": canonical_vertex_snapshot(convert),
        "triangulatedSurfaceDigest": triangulated_surface_digest,
        "triangulatedWindingDigest": winding_digest,
        "checks": checks,
        "pass": all(checks.values()),
    }


def validate_source() -> dict:
    bpy.ops.wm.open_mainfile(filepath=str(PRODUCT_BLEND))
    objects = list(bpy.context.scene.objects)
    triangles, winding, volumes, triangle_count, degenerate_count = (
        canonical_triangles(source_mapping)
    )
    geometry_digest = canonical_vertex_digest(source_mapping)
    positions = canonical_vertex_positions(source_mapping)
    geometry_digest = source_position_digest(positions)
    triangulated_surface_digest = records_digest(triangles)
    winding_digest = records_digest(winding)
    bounds = canonical_bounds(source_mapping)
    uv = uv_audit()
    checks = {
        "objectSetExact": {obj.name for obj in objects} == set(PRODUCT_OBJECTS),
        "hierarchyExact": parent_map() == EXPECTED_PARENTS,
        "boundsExact": bounds_within_tolerance(bounds),
        "materialAssignmentsExact": material_assignments() == EXPECTED_ASSIGNMENTS,
        "labelUvExact": uv["layers"] == ["LabelUV"],
        "positiveSignedMaterialVolumes": all(
            value > 0 for value in volumes.values()
        ),
        "noDegenerateTriangles": degenerate_count == 0,
        "noAnimation": (
            not bpy.data.actions
            and all(obj.animation_data is None for obj in objects)
        ),
        "noCameraLightFontOrCurve": not any(
            obj.type in {"CAMERA", "LIGHT", "FONT", "CURVE"} for obj in objects
        ),
        "runtimeContentNotBaked": (
            bpy.data.objects["PhysicalLabel"].get("placeholder_text_baked") is False
            and bpy.data.objects["PhysicalLabel"].get("fake_collectible_id_baked")
            is False
        ),
    }
    return {
        "format": "BLEND",
        "path": PRODUCT_BLEND.name,
        "sha256": sha256(PRODUCT_BLEND),
        "objectCount": len(objects),
        "typeCounts": {
            kind: sum(obj.type == kind for obj in objects)
            for kind in ("EMPTY", "MESH", "CAMERA", "LIGHT", "FONT", "CURVE")
        },
        "parentMap": parent_map(),
        "canonicalBounds": bounds,
        "materials": material_assignments(),
        "labelUv": uv,
        "triangleCount": triangle_count,
        "signedVolumesMm3": volumes,
        "geometryDigest": geometry_digest,
        "rawQuantizedVertexDigest": canonical_vertex_digest(source_mapping),
        "vertexCorrespondence": {
            "normalizedDigest": geometry_digest,
            "allObjectsBijective": True,
            "maximumErrorMm": 0.0,
        },
        "perObjectVertexDigests": canonical_vertex_snapshot(source_mapping),
        "triangulatedSurfaceDigest": triangulated_surface_digest,
        "triangulatedWindingDigest": winding_digest,
        "checks": checks,
        "pass": all(checks.values()),
        "_vertexPositions": positions,
    }


def validate_fbx(
    expected_geometry_digest: str,
    expected_signed_volumes: dict[str, float],
    expected_positions: dict[str, list[tuple[float, float, float]]],
) -> dict:
    reset()
    bpy.ops.import_scene.fbx(
        filepath=str(FBX_EXPORT),
        use_custom_props=True,
        use_image_search=False,
    )
    label, convert, error = choose_import_mapping()
    result = audit_loaded_scene(
        "FBX",
        convert,
        label,
        error,
        expected_geometry_digest,
        expected_signed_volumes,
        expected_positions,
    )
    result["path"] = FBX_EXPORT.name
    result["sha256"] = sha256(FBX_EXPORT)
    return result


def validate_glb(
    expected_geometry_digest: str,
    expected_signed_volumes: dict[str, float],
    expected_positions: dict[str, list[tuple[float, float, float]]],
) -> dict:
    reset()
    bpy.ops.import_scene.gltf(filepath=str(GLB_EXPORT))
    label, convert, error = choose_import_mapping()
    result = audit_loaded_scene(
        "GLB",
        convert,
        label,
        error,
        expected_geometry_digest,
        expected_signed_volumes,
        expected_positions,
    )
    result["path"] = GLB_EXPORT.name
    result["sha256"] = sha256(GLB_EXPORT)
    return result


def parse_glb() -> dict:
    data = GLB_EXPORT.read_bytes()
    if len(data) < 20:
        raise RuntimeError("GLB is too small.")
    magic, version, total_length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total_length != len(data):
        raise RuntimeError("GLB header is invalid.")
    json_length, json_type = struct.unpack_from("<I4s", data, 12)
    if json_type != b"JSON":
        raise RuntimeError("GLB first chunk is not JSON.")
    document = json.loads(data[20:20 + json_length].decode("utf-8").rstrip(" \x00"))
    nodes = document.get("nodes", [])
    node_names = {node.get("name") for node in nodes}
    physical_label = next(
        (node for node in nodes if node.get("name") == "PhysicalLabel"),
        {},
    )
    zone_nodes = {
        name: next((node for node in nodes if node.get("name") == name), {})
        for name in ("LogoZone", "AchievementZone", "NarrowFoil", "TransparentCover")
    }
    extensions_used = set(document.get("extensionsUsed", []))
    checks = {
        "gltf2Binary": magic == b"glTF" and version == 2,
        "fileLengthExact": total_length == len(data),
        "nodeNamesExact": node_names == set(PRODUCT_OBJECTS),
        "twelveNodes": len(nodes) == 12,
        "fiveMeshes": len(document.get("meshes", [])) == 5,
        "fourUsedMaterials": len(document.get("materials", [])) == 4,
        "noAnimations": not document.get("animations"),
        "noCameras": not document.get("cameras"),
        "noLightsExtension": "KHR_lights_punctual" not in extensions_used,
        "noImagesOrTextures": (
            not document.get("images") and not document.get("textures")
        ),
        "labelRuntimeAuthorityExtra": (
            physical_label.get("extras", {}).get("runtime_content_authority")
            == "Unity"
        ),
        "labelPlaceholderFlagsFalse": (
            physical_label.get("extras", {}).get("placeholder_text_baked") is False
            and physical_label.get("extras", {}).get("fake_collectible_id_baked")
            is False
        ),
        "zoneExtrasPresent": all(
            node.get("extras", {}).get("gate10_export_role")
            for node in zone_nodes.values()
        ),
    }
    report = {
        "schemaVersion": 1,
        "path": GLB_EXPORT.name,
        "sha256": sha256(GLB_EXPORT),
        "header": {
            "magic": magic.decode("ascii"),
            "version": version,
            "totalLength": total_length,
        },
        "asset": document.get("asset"),
        "nodeNames": sorted(node_names),
        "nodeCount": len(nodes),
        "meshCount": len(document.get("meshes", [])),
        "materialNames": sorted(
            material.get("name", "") for material in document.get("materials", [])
        ),
        "animations": len(document.get("animations", [])),
        "cameras": len(document.get("cameras", [])),
        "extensionsUsed": sorted(extensions_used),
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
    }
    GLB_STRUCTURE_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    build = load_json(BUILD_REPORT)
    for path in (PRODUCT_BLEND, FBX_EXPORT, GLB_EXPORT):
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Gate 10 export is missing: {path}")
    if (
        build["status"] != "pass"
        or build["geometry"]["approvedDigest"] != EXPECTED_GEOMETRY_DIGEST
        or not all(build["checks"].values())
    ):
        raise RuntimeError("Gate 10 build report is not valid.")

    source = validate_source()
    source_positions = source.pop("_vertexPositions")
    fbx = validate_fbx(
        source["geometryDigest"],
        source["signedVolumesMm3"],
        source_positions,
    )
    glb = validate_glb(
        source["geometryDigest"],
        source["signedVolumesMm3"],
        source_positions,
    )
    glb_structure = parse_glb()
    cross_format = {
        "geometryDigestIdentity": (
            source["geometryDigest"]
            == fbx["geometryDigest"]
            == glb["geometryDigest"]
        ),
        "exportTriangulatedSurfaceDigestIdentity": (
            fbx["triangulatedSurfaceDigest"]
            == glb["triangulatedSurfaceDigest"]
        ),
        "exportTriangulatedWindingDigestIdentity": (
            fbx["triangulatedWindingDigest"]
            == glb["triangulatedWindingDigest"]
        ),
        "sourceAndExportWindingOrientationPositive": all(
            value > 0
            for report in (source, fbx, glb)
            for value in report["signedVolumesMm3"].values()
        ),
        "sourceToExportVolumeErrorWithinPoint005Percent": (
            max(fbx["signedVolumeRelativeErrors"].values()) <= 0.00005
            and max(glb["signedVolumeRelativeErrors"].values()) <= 0.00005
        ),
        "triangleCountIdentity": (
            source["triangleCount"]
            == fbx["triangleCount"]
            == glb["triangleCount"]
        ),
        "boundsIdentity": all(
            abs(candidate["canonicalBounds"]["sizeMm"][axis]
                - source["canonicalBounds"]["sizeMm"][axis]) <= 0.001
            for candidate in (fbx, glb)
            for axis in ("width", "height", "depth")
        ),
        "materialAssignmentsIdentity": (
            source["materials"] == fbx["materials"] == glb["materials"]
        ),
        "hierarchyIdentity": (
            source["parentMap"] == fbx["parentMap"] == glb["parentMap"]
        ),
        "fileHashesMatchBuildReport": (
            build["exports"]["blend"]["sha256"] == sha256(PRODUCT_BLEND)
            and build["exports"]["fbx"]["sha256"] == sha256(FBX_EXPORT)
            and build["exports"]["glb"]["sha256"] == sha256(GLB_EXPORT)
        ),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "notice": "FRESH-SCENE FBX/GLB ROUND-TRIP PASS · NOT UNITY PARITY",
        "source": source,
        "fbx": fbx,
        "glb": glb,
        "glbStructure": {
            "path": GLB_STRUCTURE_REPORT.name,
            "sha256": sha256(GLB_STRUCTURE_REPORT),
            "status": glb_structure["status"],
        },
        "crossFormat": cross_format,
        "checks": {
            "sourcePass": source["pass"],
            "fbxPass": fbx["pass"],
            "glbPass": glb["pass"],
            "glbStructurePass": glb_structure["status"] == "pass",
            "crossFormatPass": all(cross_format.values()),
            "approvedGeometryDigestCarried": (
                build["geometry"]["productBlendDigest"]
                == EXPECTED_GEOMETRY_DIGEST
            ),
            "collisionPolicyExplicitNoApprovedProxy": (
                build["collision"]["included"] is False
                and "no approved" in build["collision"]["reason"].lower()
            ),
            "shippingUnityUnchanged": build["shippingUnityChanged"] is False,
            "buildInstallPhonePushFalse": build["buildInstallPhonePush"] is False,
        },
    }
    report["status"] = (
        "pass" if all(report["checks"].values()) else "fail"
    )
    ROUNDTRIP_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
