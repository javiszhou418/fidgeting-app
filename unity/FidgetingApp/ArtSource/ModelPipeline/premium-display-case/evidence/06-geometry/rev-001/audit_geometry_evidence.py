#!/usr/bin/env python3
"""Audit Premium Display Case Gate 06 evidence in Blender."""

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
EVIDENCE_BLEND = ROOT / "premium-display-case-geometry-r001.blend"
VALIDATION = ROOT / "geometry-validation.json"
AUDIT = ROOT / "blender-audit.json"
GATE05 = ROOT.parent.parent / "05-blockout/rev-002"
SOURCE_BLEND = GATE05 / "premium-display-case-blockout.blend"
SOURCE_BUILDER = GATE05 / "build_blockout.py"
SOURCE_VALIDATOR = GATE05 / "validate_blockout.py"
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_DIGEST = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate06_audit_validator",
        SOURCE_VALIDATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SOURCE_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
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


def bounds(objects: list[bpy.types.Object]) -> dict[str, float]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(obj.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    return {
        "width": round(max(point.x for point in points) - min(point.x for point in points), 6),
        "height": round(max(point.y for point in points) - min(point.y for point in points), 6),
        "depth": round(max(point.z for point in points) - min(point.z for point in points), 6),
    }


def mesh_audit(obj: bpy.types.Object) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        try:
            open_edges = sum(edge.is_boundary for edge in bm.edges)
            non_manifold = sum(not edge.is_manifold for edge in bm.edges)
            bad_contiguous = sum(
                edge.is_manifold and not edge.is_contiguous for edge in bm.edges
            )
            zero_edges = sum(edge.calc_length() <= 1e-9 for edge in bm.edges)
            zero_faces = sum(face.calc_area() <= 1e-9 for face in bm.faces)
        finally:
            bm.free()
        invalid_normals = sum(
            1
            for polygon in mesh.polygons
            if (
                not all(math.isfinite(value) for value in polygon.normal)
                or abs(polygon.normal.length - 1.0) > 1e-6
            )
        )
        zero_triangles = 0
        signed_volume = 0.0
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            if (second - first).cross(third - first).length * 0.5 <= 1e-9:
                zero_triangles += 1
            signed_volume += first.dot(second.cross(third)) / 6.0
        coordinate_counts = Counter(
            (
                round(vertex.co.x, 9),
                round(vertex.co.y, 9),
                round(vertex.co.z, 9),
            )
            for vertex in mesh.vertices
        )
        duplicate_vertices = sum(
            count - 1 for count in coordinate_counts.values() if count > 1
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
            for first, second in tree.overlap(tree)
            if first < second and not set(triangles[first]).intersection(triangles[second])
        )
        result = {
            "openBoundaryEdgeCount": open_edges,
            "nonManifoldEdgeCount": non_manifold,
            "badContiguousEdgeCount": bad_contiguous,
            "invalidPolygonNormalCount": invalid_normals,
            "zeroLengthEdgeCount": zero_edges,
            "zeroAreaFaceCount": zero_faces,
            "zeroAreaTriangleCount": zero_triangles,
            "duplicateVertexCount": duplicate_vertices,
            "selfIntersectionPairCount": self_intersections,
            "signedVolumeMm3": round(signed_volume, 6),
        }
        result["pass"] = all(
            result[key] == 0
            for key in (
                "openBoundaryEdgeCount",
                "nonManifoldEdgeCount",
                "badContiguousEdgeCount",
                "invalidPolygonNormalCount",
                "zeroLengthEdgeCount",
                "zeroAreaFaceCount",
                "zeroAreaTriangleCount",
                "duplicateVertexCount",
                "selfIntersectionPairCount",
            )
        )
        return result
    finally:
        evaluated.to_mesh_clear()


def flood_fill_audit(validator, tube: bpy.types.Object) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = tube.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    vertices = [tube.matrix_world @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(
        vertices,
        triangles,
        all_triangles=True,
        epsilon=1e-6,
    )
    path = validator.rounded_rectangle_path()
    valid = set()
    wall_values = []
    try:
        for sample_index, sample in enumerate(path):
            x, y = sample["point"]
            tangent_x, tangent_y = sample["tangent"]
            tangent = Vector((tangent_x, tangent_y, 0.0))
            normal = Vector((-tangent_y, tangent_x, 0.0))
            base = Vector((x, y, 25.0))
            directions = (
                (normal, 3.0),
                (-normal, 3.0),
                (Vector((0.0, 0.0, 1.0)), 2.5),
                (Vector((0.0, 0.0, -1.0)), 2.5),
            )
            passed = 0
            for direction, expected in directions:
                result = None
                for jitter in (0.037, -0.037, 0.083, -0.083, 0.137, -0.137):
                    origin = base + tangent * jitter
                    hit, _normal, _index, distance = tree.ray_cast(
                        origin,
                        direction,
                        20.0,
                    )
                    if (
                        hit is not None
                        and distance is not None
                        and abs(distance - expected) <= 0.03
                    ):
                        result = hit
                        break
                if result is None:
                    continue
                second_hit, _normal, _index, second_distance = tree.ray_cast(
                    result + direction * 0.02,
                    direction,
                    20.0,
                )
                if second_hit is None or second_distance is None:
                    continue
                wall_values.append(float(second_distance) + 0.02)
                passed += 1
            if passed == 4:
                valid.add(sample_index)
    finally:
        evaluated.to_mesh_clear()

    visited = set()
    if 0 in valid:
        visited.add(0)
        queue = deque([0])
        while queue:
            current = queue.popleft()
            for neighbor in ((current - 1) % len(path), (current + 1) % len(path)):
                if neighbor in valid and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return {
        "method": "independent evaluated-mesh BVH audit",
        "sampleCount": len(path),
        "validVolumetricSampleCount": len(valid),
        "visitedSamples": len(visited),
        "wallThicknessMinimumMm": round(min(wall_values), 6),
        "wallThicknessMaximumMm": round(max(wall_values), 6),
        "pass": (
            len(valid) == len(path)
            and len(visited) == len(path)
            and abs(sum(wall_values) / len(wall_values) - 2.0) <= 0.02
        ),
    }


def main() -> None:
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    if Path(bpy.data.filepath).resolve() != EVIDENCE_BLEND.resolve():
        bpy.ops.wm.open_mainfile(filepath=str(EVIDENCE_BLEND))
    validator = load_validator()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    digest = geometry_digest(subjects)
    measured_bounds = bounds(subjects)
    structural = validator.validate_scene()
    object_audits = {obj.name: mesh_audit(obj) for obj in subjects}
    flood = flood_fill_audit(
        validator,
        bpy.data.objects["ContinuousTubePerimeter"],
    )
    source_hashes = {
        "blend": sha256(SOURCE_BLEND),
        "builder": sha256(SOURCE_BUILDER),
        "validator": sha256(SOURCE_VALIDATOR),
    }
    root = bpy.data.objects["PresentationRoot"]
    assembly = bpy.data.objects["CaseAssembly"]
    content = bpy.data.objects["ContentSlot"]
    exploded_tube = bpy.data.objects.get("EXPLODED_ContinuousTubePerimeter")
    exploded_objects = [
        obj
        for obj in bpy.data.objects
        if obj.name.startswith("EXPLODED_")
    ]
    annotations = [
        obj
        for obj in bpy.data.objects
        if bool(obj.get("gate06_review_annotation", False))
    ]
    checks = {
        "validationReportPassed": validation["status"] == "pass",
        "sourceHashesMatchBuildReport": (
            source_hashes == validation["sourceGate05"]["hashesBefore"]
            == validation["sourceGate05"]["hashesAfter"]
        ),
        "sourceBlendUnchanged": (
            source_hashes["blend"]
            == "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31"
        ),
        "geometryDigestExact": (
            digest == EXPECTED_DIGEST
            == validation["geometryIdentity"]["digestBefore"]
            == validation["geometryIdentity"]["digestAfterEvidenceRenders"]
            == validation["geometryIdentity"]["digestAfterEvidenceBlendSave"]
        ),
        "boundsExact": measured_bounds == {
            "width": 228.0,
            "height": 304.0,
            "depth": 59.0,
        },
        "portraitRatioExact": measured_bounds["width"] / measured_bounds["height"] == 0.75,
        "labelAndConcentricValues": (
            structural["labelPosition"]["candidateCenterYmm"] == 99.0
            and structural["labelPosition"]["candidateDownshiftMm"] == 6.0
            and structural["closedTube"]["cornerRadiiMm"]["outer"] == 20.0
            and structural["cornerCenterFamilies"]["maximumDriftMm"] <= 0.01
        ),
        "allMeshesClean": all(item["pass"] for item in object_audits.values()),
        "tubeOneConnectedMaterialBody": (
            structural["closedTube"]["meshObjectCount"] == 1
            and structural["closedTube"]["topology"]["connectedMaterialBodyCount"] == 1
        ),
        "tubeFloodFillAndWall": flood["pass"],
        "presentationRootOwnsMotion": (
            root.parent is None
            and bool(root.get("motion_owner", False))
            and float(root.get("angular_velocity", math.nan)) == 0.0
            and assembly.parent is root
            and assembly.get("role") == "always-assembled-transform-group"
        ),
        "contentSlotPreserved": (
            content.type == "EMPTY"
            and content.parent.name == "RearPolycarbonateShell"
            and content.get("role") == "runtime-anchor"
            and float(content.get("width_mm", 0.0)) == 180.0
            and float(content.get("height_mm", 0.0)) == 198.0
            and float(content.get("depth_mm", 0.0)) == 48.0
        ),
        "explodedEvidenceUsesExactTubeData": (
            len(exploded_objects) == 5
            and exploded_tube is not None
            and exploded_tube.data is bpy.data.objects["ContinuousTubePerimeter"].data
            and bool(exploded_tube.get("gate06_exploded_same_mesh_data", False))
            and not bool(exploded_tube.get("shipping_animation_eligible", True))
        ),
        "explodedAndAnnotationsHiddenInCanonicalScene": (
            all(obj.hide_render for obj in exploded_objects)
            and all(obj.hide_render for obj in annotations)
        ),
        "noHiddenStructureInvented": (
            validation["hiddenStructure"]["inventedInternalPartCount"] == 0
            and bpy.data.objects["TransparentCover"].type == "EMPTY"
        ),
        "shippingRevealAlwaysAssembled": (
            bpy.context.scene["shipping_reveal_policy"]
            == "always-assembled-never-explodes"
        ),
        "gate07NotEntered": bpy.context.scene["gate07_entered"] is False,
        "shippingUnityUnchanged": bpy.context.scene["shipping_unity_changed"] is False,
        "noBuildInstallPhonePush": bpy.context.scene["build_install_phone_push"] is False,
    }
    audit = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceFiles": {
            "gate05Blend": {
                "path": str(SOURCE_BLEND),
                "sha256": source_hashes["blend"],
            },
            "gate05Builder": {
                "path": str(SOURCE_BUILDER),
                "sha256": source_hashes["builder"],
            },
            "gate05Validator": {
                "path": str(SOURCE_VALIDATOR),
                "sha256": source_hashes["validator"],
            },
        },
        "evidenceBlend": {
            "path": str(EVIDENCE_BLEND),
            "sha256": sha256(EVIDENCE_BLEND),
        },
        "geometryDigest": digest,
        "boundsMm": measured_bounds,
        "portraitWidthHeightRatio": measured_bounds["width"] / measured_bounds["height"],
        "labelCenterYmm": structural["labelPosition"]["candidateCenterYmm"],
        "labelDownshiftMm": structural["labelPosition"]["candidateDownshiftMm"],
        "outerRadiusMm": structural["closedTube"]["cornerRadiiMm"]["outer"],
        "maximumCornerCenterDriftMm": structural["cornerCenterFamilies"]["maximumDriftMm"],
        "meshAudit": object_audits,
        "tubeFloodFill": flood,
        "checks": checks,
        "blender": bpy.app.version_string,
    }
    AUDIT.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": audit["status"],
        "geometryDigest": digest,
        "boundsMm": measured_bounds,
        "tubeFloodFill": f"{flood['visitedSamples']}/{flood['sampleCount']}",
        "meshAudit": object_audits,
    }, ensure_ascii=False, indent=2))
    if audit["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
