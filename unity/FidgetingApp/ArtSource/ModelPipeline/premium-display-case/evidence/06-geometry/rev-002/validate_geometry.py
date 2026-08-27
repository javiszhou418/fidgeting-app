#!/usr/bin/env python3
"""Validate Premium Display Case Gate 06 normals-only geometry revision 2."""

from __future__ import annotations

from collections import Counter, deque
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path(__file__).resolve().parent
GATE05 = ROOT.parent.parent / "05-blockout/rev-002"
SOURCE_VALIDATOR = GATE05 / "validate_blockout.py"
EVIDENCE_BLEND = ROOT / "premium-display-case-geometry-r002.blend"
REPORT_PATH = ROOT / "geometry-validation.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
TUBE_NAME = "ContinuousTubePerimeter"
EXPECTED_SOURCE_FULL_GEOMETRY_DIGEST = (
    "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
)
SIGNED_VOLUME_EPSILON_MM3 = 1e-6


def load_gate05_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate05_validator_for_gate06_r2",
        SOURCE_VALIDATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SOURCE_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hash_records(records: list[str]) -> str:
    digest = hashlib.sha256()
    for record in records:
        digest.update(record.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def _evaluated_mesh(obj: bpy.types.Object):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    return evaluated, evaluated.to_mesh()


def object_matrix_digest(objects: list[bpy.types.Object]) -> str:
    records = []
    for obj in sorted(objects, key=lambda item: item.name):
        records.append(obj.name)
        records.extend(
            ",".join(f"{value:.12f}" for value in row)
            for row in obj.matrix_world
        )
    return _hash_records(records)


def vertex_position_digest(objects: list[bpy.types.Object]) -> str:
    records = []
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            records.append(obj.name)
            records.extend(
                f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f}"
                for vertex in mesh.vertices
            )
        finally:
            evaluated.to_mesh_clear()
    return _hash_records(records)


def topology_winding_digest(objects: list[bpy.types.Object]) -> str:
    records = []
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            records.append(obj.name)
            records.extend(
                ",".join(str(index) for index in polygon.vertices)
                for polygon in mesh.polygons
            )
        finally:
            evaluated.to_mesh_clear()
    return _hash_records(records)


def full_geometry_digest(objects: list[bpy.types.Object]) -> str:
    """Retain the rev 1 digest recipe for an exact before/after comparison."""
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            digest.update(obj.name.encode())
            for row in obj.matrix_world:
                for value in row:
                    digest.update(f"{value:.12f}".encode())
            for vertex in mesh.vertices:
                digest.update(
                    f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode()
                )
            for polygon in mesh.polygons:
                digest.update(
                    (",".join(str(index) for index in polygon.vertices) + ";").encode()
                )
        finally:
            evaluated.to_mesh_clear()
    return digest.hexdigest()


def _project(point: Vector, view_id: str) -> tuple[float, float]:
    if view_id == "front":
        return point.x, point.y
    if view_id == "back":
        return -point.x, point.y
    if view_id == "top":
        return point.x, -point.z
    if view_id == "bottom":
        return point.x, point.z
    if view_id == "left":
        return point.z, point.y
    if view_id == "right":
        return -point.z, point.y
    raise ValueError(view_id)


def silhouette_digest(objects: list[bpy.types.Object]) -> str:
    """Hash six projected face point sets without preserving winding order."""
    records = []
    for view_id in ("front", "back", "top", "bottom", "left", "right"):
        records.append(view_id)
        for obj in sorted(objects, key=lambda item: item.name):
            evaluated, mesh = _evaluated_mesh(obj)
            try:
                projected_faces = []
                for polygon in mesh.polygons:
                    points = sorted(
                        (
                            round(_project(obj.matrix_world @ mesh.vertices[index].co, view_id)[0], 9),
                            round(_project(obj.matrix_world @ mesh.vertices[index].co, view_id)[1], 9),
                        )
                        for index in polygon.vertices
                    )
                    projected_faces.append(
                        ";".join(f"{first:.9f},{second:.9f}" for first, second in points)
                    )
                records.append(obj.name)
                records.extend(sorted(projected_faces))
            finally:
                evaluated.to_mesh_clear()
    return _hash_records(records)


def per_object_digests(objects: list[bpy.types.Object]) -> dict[str, dict[str, str]]:
    return {
        obj.name: {
            "objectMatrixDigest": object_matrix_digest([obj]),
            "vertexPositionDigest": vertex_position_digest([obj]),
            "silhouetteDigest": silhouette_digest([obj]),
            "topologyWindingDigest": topology_winding_digest([obj]),
            "fullGeometryDigest": full_geometry_digest([obj]),
        }
        for obj in sorted(objects, key=lambda item: item.name)
    }


def identity_snapshot(objects: list[bpy.types.Object]) -> dict[str, object]:
    return {
        "objectMatrixDigest": object_matrix_digest(objects),
        "vertexPositionDigest": vertex_position_digest(objects),
        "silhouetteDigest": silhouette_digest(objects),
        "silhouetteDigestMethod": (
            "six-orthographic orientation-insensitive projected-face point sets"
        ),
        "topologyWindingDigest": topology_winding_digest(objects),
        "fullGeometryDigest": full_geometry_digest(objects),
        "perObject": per_object_digests(objects),
    }


def world_bounds(objects: list[bpy.types.Object]) -> dict[str, object]:
    points: list[Vector] = []
    for obj in objects:
        evaluated, mesh = _evaluated_mesh(obj)
        try:
            points.extend(obj.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    size = [maximum[index] - minimum[index] for index in range(3)]
    return {
        "minimumMm": [round(value, 6) for value in minimum],
        "maximumMm": [round(value, 6) for value in maximum],
        "sizeMm": {
            "width": round(size[0], 6),
            "height": round(size[1], 6),
            "depth": round(size[2], 6),
        },
    }


def _vertex_components(mesh: bpy.types.Mesh) -> tuple[list[set[int]], list[int]]:
    adjacency: list[list[int]] = [[] for _ in mesh.vertices]
    for edge in mesh.edges:
        first, second = edge.vertices
        adjacency[first].append(second)
        adjacency[second].append(first)
    components: list[set[int]] = []
    component_by_vertex = [-1] * len(mesh.vertices)
    remaining = set(range(len(mesh.vertices)))
    while remaining:
        start = next(iter(remaining))
        visited = {start}
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        component_index = len(components)
        for vertex_index in visited:
            component_by_vertex[vertex_index] = component_index
        components.append(visited)
        remaining.difference_update(visited)
    return components, component_by_vertex


def mesh_integrity(obj: bpy.types.Object) -> dict[str, object]:
    evaluated, mesh = _evaluated_mesh(obj)
    try:
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        try:
            boundary_edges = sum(edge.is_boundary for edge in bm.edges)
            non_manifold_edges = sum(not edge.is_manifold for edge in bm.edges)
            bad_contiguous_edges = sum(
                edge.is_manifold and not edge.is_contiguous for edge in bm.edges
            )
            zero_length_edges = sum(edge.calc_length() <= 1e-9 for edge in bm.edges)
            zero_area_faces = sum(face.calc_area() <= 1e-9 for face in bm.faces)
        finally:
            bm.free()

        components, component_by_vertex = _vertex_components(mesh)
        component_volumes = [0.0] * len(components)
        signed_volume = 0.0
        zero_area_triangles = 0
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            area = (second - first).cross(third - first).length * 0.5
            if area <= 1e-9:
                zero_area_triangles += 1
            volume = first.dot(second.cross(third)) / 6.0
            signed_volume += volume
            component_index = component_by_vertex[triangle.vertices[0]]
            if any(
                component_by_vertex[index] != component_index
                for index in triangle.vertices
            ):
                raise RuntimeError(f"{obj.name} triangle spans disconnected components.")
            component_volumes[component_index] += volume

        invalid_normals = sum(
            1
            for polygon in mesh.polygons
            if (
                not all(math.isfinite(value) for value in polygon.normal)
                or abs(polygon.normal.length - 1.0) > 1e-6
            )
        )
        coordinates = Counter(
            (
                round(vertex.co.x, 9),
                round(vertex.co.y, 9),
                round(vertex.co.z, 9),
            )
            for vertex in mesh.vertices
        )
        duplicate_vertices = sum(
            count - 1 for count in coordinates.values() if count > 1
        )
        vertices = [tuple(vertex.co) for vertex in mesh.vertices]
        triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
        tree = BVHTree.FromPolygons(
            vertices,
            triangles,
            all_triangles=True,
            epsilon=1e-7,
        )
        self_intersections = sum(
            1
            for first_index, second_index in tree.overlap(tree)
            if (
                first_index < second_index
                and not set(triangles[first_index]).intersection(
                    triangles[second_index]
                )
            )
        )
        topology_pass = (
            boundary_edges == 0
            and non_manifold_edges == 0
            and zero_length_edges == 0
            and zero_area_faces == 0
            and zero_area_triangles == 0
            and duplicate_vertices == 0
            and self_intersections == 0
        )
        normal_coherence_pass = (
            invalid_normals == 0 and bad_contiguous_edges == 0
        )
        positive_material_volume = signed_volume > SIGNED_VOLUME_EPSILON_MM3
        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
            "surfaceConnectedComponentCount": len(components),
            "surfaceComponentVertexCounts": sorted(
                (len(component) for component in components),
                reverse=True,
            ),
            "surfaceComponentSignedVolumesMm3": [
                round(value, 6) for value in component_volumes
            ],
            "openBoundaryEdgeCount": boundary_edges,
            "nonManifoldEdgeCount": non_manifold_edges,
            "badContiguousEdgeCount": bad_contiguous_edges,
            "zeroLengthEdgeCount": zero_length_edges,
            "zeroAreaFaceCount": zero_area_faces,
            "zeroAreaTriangleCount": zero_area_triangles,
            "duplicateVertexCount": duplicate_vertices,
            "selfIntersectionPairCount": self_intersections,
            "invalidPolygonNormalCount": invalid_normals,
            "signedVolumeMm3": round(signed_volume, 6),
            "positiveMaterialSignedVolume": positive_material_volume,
            "normalCoherencePass": normal_coherence_pass,
            "orientationDisposition": (
                "positive-material-volume"
                if positive_material_volume
                else "invalid-non-positive-material-volume"
            ),
            "pass": topology_pass and normal_coherence_pass and positive_material_volume,
        }
    finally:
        evaluated.to_mesh_clear()


def hollow_tube_orientation(
    obj: bpy.types.Object,
    gate05_validator,
) -> dict[str, object]:
    evaluated, mesh = _evaluated_mesh(obj)
    try:
        mesh.calc_loop_triangles()
        components, component_by_vertex = _vertex_components(mesh)
        if len(components) != 2:
            return {
                "boundarySurfaceComponentCount": len(components),
                "pass": False,
                "reason": "Expected exactly two closed boundary surfaces.",
            }

        component_volumes = [0.0, 0.0]
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            component_index = component_by_vertex[triangle.vertices[0]]
            component_volumes[component_index] += (
                first.dot(second.cross(third)) / 6.0
            )
        outer_index = max(
            range(2),
            key=lambda index: abs(component_volumes[index]),
        )
        inner_index = 1 - outer_index

        path = gate05_validator.rounded_rectangle_path()
        outer_count = int(obj.get("outer_profile_count", 0))
        inner_count = int(obj.get("inner_profile_count", 0))
        ring_stride = outer_count + inner_count
        if ring_stride <= 0:
            raise RuntimeError("Tube profile counts are missing.")

        dot_values = {0: [], 1: []}
        mismatch_counts = {0: 0, 1: 0}
        for polygon in mesh.polygons:
            component_index = component_by_vertex[polygon.vertices[0]]
            ring_index = int(polygon.vertices[0]) // ring_stride
            sample = path[ring_index % len(path)]
            centerline = Vector(
                (sample["point"][0], sample["point"][1], 25.0)
            )
            center = sum(
                (mesh.vertices[index].co for index in polygon.vertices),
                Vector(),
            ) / len(polygon.vertices)
            dot = float(polygon.normal.dot(center - centerline))
            dot_values[component_index].append(dot)
            expected_positive = component_index == outer_index
            if (dot > 1e-8) != expected_positive:
                mismatch_counts[component_index] += 1

        outer_volume = component_volumes[outer_index]
        inner_volume = component_volumes[inner_index]
        net_volume = outer_volume + inner_volume
        outer_dots = dot_values[outer_index]
        inner_dots = dot_values[inner_index]
        outer_outward = (
            bool(outer_dots)
            and mismatch_counts[outer_index] == 0
            and min(outer_dots) > 1e-8
        )
        inner_toward_lumen = (
            bool(inner_dots)
            and mismatch_counts[inner_index] == 0
            and max(inner_dots) < -1e-8
        )
        pass_value = (
            outer_volume > SIGNED_VOLUME_EPSILON_MM3
            and inner_volume < -SIGNED_VOLUME_EPSILON_MM3
            and net_volume > SIGNED_VOLUME_EPSILON_MM3
            and outer_outward
            and inner_toward_lumen
        )
        return {
            "boundarySurfaceComponentCount": 2,
            "classificationMethod": (
                "larger absolute enclosed volume is outer boundary; "
                "face-normal dot against swept-section radial vector verifies direction"
            ),
            "outerBoundary": {
                "componentIndex": outer_index,
                "signedVolumeMm3": round(outer_volume, 6),
                "normalDirection": "outward-from-material",
                "minimumRadialNormalDot": round(min(outer_dots), 9),
                "maximumRadialNormalDot": round(max(outer_dots), 9),
                "orientationMismatchFaceCount": mismatch_counts[outer_index],
                "outward": outer_outward,
            },
            "innerBoundary": {
                "componentIndex": inner_index,
                "signedVolumeMm3": round(inner_volume, 6),
                "normalDirection": "toward-lumen",
                "minimumRadialNormalDot": round(min(inner_dots), 9),
                "maximumRadialNormalDot": round(max(inner_dots), 9),
                "orientationMismatchFaceCount": mismatch_counts[inner_index],
                "inwardTowardLumen": inner_toward_lumen,
            },
            "netMaterialSignedVolumeMm3": round(net_volume, 6),
            "netMaterialVolumePositive": net_volume > SIGNED_VOLUME_EPSILON_MM3,
            "orientationDisposition": (
                "outer-outward-inner-toward-lumen-net-positive"
                if pass_value
                else "invalid-hollow-boundary-orientation"
            ),
            "pass": pass_value,
        }
    finally:
        evaluated.to_mesh_clear()


def evaluate_scene(
    source_identity: dict[str, object],
    source_tube_signed_volume_mm3: float,
) -> dict[str, object]:
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    derivative_identity = identity_snapshot(subjects)
    bounds = world_bounds(subjects)
    integrity = {obj.name: mesh_integrity(obj) for obj in subjects}
    gate05_validator = load_gate05_validator()
    structural = gate05_validator.validate_scene()
    tube_orientation = hollow_tube_orientation(
        bpy.data.objects[TUBE_NAME],
        gate05_validator,
    )

    all_open = sum(item["openBoundaryEdgeCount"] for item in integrity.values())
    all_non_manifold = sum(
        item["nonManifoldEdgeCount"] for item in integrity.values()
    )
    all_bad_contiguous = sum(
        item["badContiguousEdgeCount"] for item in integrity.values()
    )
    all_self_intersections = sum(
        item["selfIntersectionPairCount"] for item in integrity.values()
    )
    all_degenerate = sum(
        item["zeroLengthEdgeCount"]
        + item["zeroAreaFaceCount"]
        + item["zeroAreaTriangleCount"]
        + item["duplicateVertexCount"]
        for item in integrity.values()
    )

    source_per_object = source_identity["perObject"]
    derivative_per_object = derivative_identity["perObject"]
    non_tube_names = [name for name in SUBJECT_NAMES if name != TUBE_NAME]
    checks = {
        "sourceGate05FullGeometryDigestExact": (
            source_identity["fullGeometryDigest"]
            == EXPECTED_SOURCE_FULL_GEOMETRY_DIGEST
        ),
        "objectMatricesUnchanged": (
            source_identity["objectMatrixDigest"]
            == derivative_identity["objectMatrixDigest"]
        ),
        "vertexPositionsUnchanged": (
            source_identity["vertexPositionDigest"]
            == derivative_identity["vertexPositionDigest"]
        ),
        "silhouetteDigestUnchanged": (
            source_identity["silhouetteDigest"]
            == derivative_identity["silhouetteDigest"]
        ),
        "topologyWindingDigestChanged": (
            source_identity["topologyWindingDigest"]
            != derivative_identity["topologyWindingDigest"]
        ),
        "onlyTubeTopologyWindingChanged": (
            source_per_object[TUBE_NAME]["topologyWindingDigest"]
            != derivative_per_object[TUBE_NAME]["topologyWindingDigest"]
            and all(
                source_per_object[name]["topologyWindingDigest"]
                == derivative_per_object[name]["topologyWindingDigest"]
                for name in non_tube_names
            )
        ),
        "allPerObjectVerticesAndSilhouettesUnchanged": all(
            source_per_object[name]["vertexPositionDigest"]
            == derivative_per_object[name]["vertexPositionDigest"]
            and source_per_object[name]["silhouetteDigest"]
            == derivative_per_object[name]["silhouetteDigest"]
            and source_per_object[name]["objectMatrixDigest"]
            == derivative_per_object[name]["objectMatrixDigest"]
            for name in SUBJECT_NAMES
        ),
        "approvedEnvelopeExact": (
            bounds["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "portraitRatioExact": (
            bounds["sizeMm"]["width"] / bounds["sizeMm"]["height"] == 0.75
        ),
        "allSubjectMeshesClosedAndManifold": (
            all_open == 0
            and all_non_manifold == 0
            and all(item["pass"] for item in integrity.values())
        ),
        "allSubjectMaterialSignedVolumesPositive": all(
            item["signedVolumeMm3"] > SIGNED_VOLUME_EPSILON_MM3
            and item["positiveMaterialSignedVolume"] is True
            for item in integrity.values()
        ),
        "allNormalsFiniteAndContiguous": (
            all_bad_contiguous == 0
            and all(
                item["invalidPolygonNormalCount"] == 0
                for item in integrity.values()
            )
        ),
        "noSelfIntersections": all_self_intersections == 0,
        "noDegenerateGeometry": all_degenerate == 0,
        "sourceTubeWasNegative": (
            source_tube_signed_volume_mm3 < -SIGNED_VOLUME_EPSILON_MM3
        ),
        "tubeNetSignedVolumePositive": (
            tube_orientation["netMaterialSignedVolumeMm3"]
            > SIGNED_VOLUME_EPSILON_MM3
        ),
        "tubeOuterBoundaryOutward": (
            tube_orientation["outerBoundary"]["outward"] is True
            and tube_orientation["outerBoundary"]["signedVolumeMm3"] > 0
        ),
        "tubeInnerBoundaryTowardLumen": (
            tube_orientation["innerBoundary"]["inwardTowardLumen"] is True
            and tube_orientation["innerBoundary"]["signedVolumeMm3"] < 0
        ),
        "tubeHollowOrientationPass": tube_orientation["pass"] is True,
        "labelAndConcentricValuesPreserved": (
            structural["labelPosition"]["candidateCenterYmm"] == 99.0
            and structural["labelPosition"]["candidateDownshiftMm"] == 6.0
            and structural["closedTube"]["cornerRadiiMm"]["outer"] == 20.0
            and structural["cornerCenterFamilies"]["maximumDriftMm"] <= 0.01
        ),
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "identity": {
            "source": source_identity,
            "derivative": derivative_identity,
        },
        "bounds": bounds,
        "meshIntegrity": {
            "objects": integrity,
            "allOpenBoundaryEdgeCount": all_open,
            "allNonManifoldEdgeCount": all_non_manifold,
            "allBadContiguousEdgeCount": all_bad_contiguous,
            "allSelfIntersectionPairCount": all_self_intersections,
            "allDegenerateElementCount": all_degenerate,
            "allSubjectMaterialSignedVolumesPositive": checks[
                "allSubjectMaterialSignedVolumesPositive"
            ],
            "pass": (
                checks["allSubjectMeshesClosedAndManifold"]
                and checks["allSubjectMaterialSignedVolumesPositive"]
                and checks["allNormalsFiniteAndContiguous"]
                and checks["noSelfIntersections"]
                and checks["noDegenerateGeometry"]
            ),
        },
        "tubeOrientation": tube_orientation,
        "structural": structural,
        "checks": checks,
    }


def main() -> None:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    if Path(bpy.data.filepath).resolve() != EVIDENCE_BLEND.resolve():
        bpy.ops.wm.open_mainfile(filepath=str(EVIDENCE_BLEND))
    result = evaluate_scene(
        report["geometryIdentity"]["source"],
        report["windingCorrection"]["before"]["netMaterialSignedVolumeMm3"],
    )
    report["validatorRecheck"] = {
        "status": result["status"],
        "identity": result["identity"]["derivative"],
        "meshIntegrity": result["meshIntegrity"],
        "tubeOrientation": result["tubeOrientation"],
        "checks": result["checks"],
        "blender": bpy.app.version_string,
    }
    report["status"] = (
        "pass"
        if report.get("status") == "pass" and result["status"] == "pass"
        else "fail"
    )
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "vertexPositionDigest": result["identity"]["derivative"][
            "vertexPositionDigest"
        ],
        "silhouetteDigest": result["identity"]["derivative"][
            "silhouetteDigest"
        ],
        "topologyWindingDigest": result["identity"]["derivative"][
            "topologyWindingDigest"
        ],
        "tubeOrientation": result["tubeOrientation"],
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(result["checks"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
