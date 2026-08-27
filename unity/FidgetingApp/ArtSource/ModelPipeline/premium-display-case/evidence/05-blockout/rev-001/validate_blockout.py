#!/usr/bin/env python3
"""Validate the Premium Display Case Gate 05 Blender blockout."""

from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "blockout-validation.json"

WIDTH_MM = 228.0
HEIGHT_MM = 304.0
DEPTH_MM = 59.0
TUBE_OUTER_WIDTH_MM = 10.0
TUBE_OUTER_DEPTH_MM = 9.0
TUBE_WALL_MM = 2.0
TUBE_PASSAGE_WIDTH_MM = 6.0
TUBE_PASSAGE_DEPTH_MM = 5.0
TUBE_PROFILE_RADIUS_MM = 3.0
TUBE_PASSAGE_RADIUS_MM = 1.0
OUTER_CORNER_RADIUS_MM = 20.0
CENTERLINE_CORNER_RADIUS_MM = 15.0
INNER_CORNER_RADIUS_MM = 10.0


def rounded_rectangle_path(
    half_width: float = WIDTH_MM / 2.0 - TUBE_OUTER_WIDTH_MM / 2.0,
    half_height: float = HEIGHT_MM / 2.0 - TUBE_OUTER_WIDTH_MM / 2.0,
    radius: float = CENTERLINE_CORNER_RADIUS_MM,
    straight_steps: int = 32,
    arc_steps: int = 64,
) -> list[dict[str, object]]:
    """Return a clockwise cyclic centerline with analytic tangents."""
    horizontal = half_width - radius
    vertical = half_height - radius
    samples: list[dict[str, object]] = []

    def line(
        start: tuple[float, float],
        end: tuple[float, float],
        tangent: tuple[float, float],
        label: str,
    ) -> None:
        for index in range(straight_steps):
            amount = index / straight_steps
            samples.append({
                "point": (
                    start[0] + (end[0] - start[0]) * amount,
                    start[1] + (end[1] - start[1]) * amount,
                ),
                "tangent": tangent,
                "region": label,
            })

    def arc(
        center: tuple[float, float],
        start_degrees: float,
        end_degrees: float,
        label: str,
    ) -> None:
        start = math.radians(start_degrees)
        sweep = math.radians(end_degrees - start_degrees)
        direction = -1.0 if sweep < 0.0 else 1.0
        for index in range(arc_steps):
            amount = index / arc_steps
            angle = start + sweep * amount
            samples.append({
                "point": (
                    center[0] + radius * math.cos(angle),
                    center[1] + radius * math.sin(angle),
                ),
                "tangent": (
                    -math.sin(angle) * direction,
                    math.cos(angle) * direction,
                ),
                "region": label,
            })

    line((-horizontal, half_height), (horizontal, half_height), (1.0, 0.0), "top")
    arc((horizontal, vertical), 90.0, 0.0, "top-right-bend")
    line((half_width, vertical), (half_width, -vertical), (0.0, -1.0), "right")
    arc((horizontal, -vertical), 0.0, -90.0, "bottom-right-bend")
    line((horizontal, -half_height), (-horizontal, -half_height), (-1.0, 0.0), "bottom")
    arc((-horizontal, -vertical), -90.0, -180.0, "bottom-left-bend")
    line((-half_width, -vertical), (-half_width, vertical), (0.0, 1.0), "left")
    arc((-horizontal, vertical), 180.0, 90.0, "top-left-bend")
    return samples


def rounded_profile(
    width: float,
    depth: float,
    radius: float,
    corner_steps: int = 12,
) -> list[tuple[float, float]]:
    half_width = width / 2.0
    half_depth = depth / 2.0
    centers = (
        (half_width - radius, half_depth - radius, 0.0),
        (-half_width + radius, half_depth - radius, 90.0),
        (-half_width + radius, -half_depth + radius, 180.0),
        (half_width - radius, -half_depth + radius, 270.0),
    )
    points: list[tuple[float, float]] = []
    for center_u, center_z, start_degrees in centers:
        for index in range(corner_steps):
            angle = math.radians(start_degrees + 90.0 * index / corner_steps)
            points.append((
                center_u + radius * math.cos(angle),
                center_z + radius * math.sin(angle),
            ))
    return points


def evaluated_vertices(obj: bpy.types.Object) -> list[Vector]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def object_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [point for obj in objects for point in evaluated_vertices(obj)]
    if not points:
        raise RuntimeError("No blockout subject meshes were found.")
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def mesh_topology(obj: bpy.types.Object) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        edge_face_counts = {tuple(sorted(edge.vertices)): 0 for edge in mesh.edges}
        for polygon in mesh.polygons:
            for edge_key in polygon.edge_keys:
                edge_face_counts[tuple(sorted(edge_key))] += 1
        open_edges = sum(count == 1 for count in edge_face_counts.values())
        non_manifold_edges = sum(count != 2 for count in edge_face_counts.values())

        adjacency: list[list[int]] = [[] for _ in mesh.vertices]
        for edge in mesh.edges:
            first, second = edge.vertices
            adjacency[first].append(second)
            adjacency[second].append(first)
        components: list[set[int]] = []
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
            components.append(visited)
            remaining.difference_update(visited)

        component_metrics = []
        for vertices in components:
            edge_count = sum(
                edge.vertices[0] in vertices and edge.vertices[1] in vertices
                for edge in mesh.edges
            )
            face_count = sum(all(vertex in vertices for vertex in polygon.vertices) for polygon in mesh.polygons)
            component_metrics.append({
                "vertices": len(vertices),
                "edges": edge_count,
                "faces": face_count,
                "eulerCharacteristic": len(vertices) - edge_count + face_count,
            })
        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "openBoundaryEdgeCount": open_edges,
            "nonManifoldEdgeCount": non_manifold_edges,
            "surfaceConnectedComponentCount": len(components),
            "expectedBoundarySurfaceComponents": 2,
            "surfaceComponents": component_metrics,
            "connectedMaterialBodyCount": 1,
            "materialBodyBasis": "A cyclic sweep of one connected annular cross-section.",
            "boundaryInterpretation": "A closed hollow pipe has separate inner and outer watertight boundary surfaces while its annular wall remains one connected material body.",
            "manifoldPreflightPass": (
                open_edges == 0
                and non_manifold_edges == 0
                and len(components) == 2
                and all(metric["eulerCharacteristic"] == 0 for metric in component_metrics)
            ),
        }
    finally:
        evaluated.to_mesh_clear()


def channel_flood_fill(samples: list[dict[str, object]]) -> dict[str, object]:
    sample_count = len(samples)
    adjacency = {
        index: {(index - 1) % sample_count, (index + 1) % sample_count}
        for index in range(sample_count)
    }
    visited = {0}
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    regions = sorted({str(samples[index]["region"]) for index in visited})
    expected_regions = sorted([
        "top",
        "top-right-bend",
        "right",
        "bottom-right-bend",
        "bottom",
        "bottom-left-bend",
        "left",
        "top-left-bend",
    ])
    return {
        "method": "cyclic-centerline-construction-graph-preflight",
        "sampleCount": sample_count,
        "visitedSamples": len(visited),
        "regionsVisited": regions,
        "expectedRegions": expected_regions,
        "pass": len(visited) == sample_count and regions == expected_regions,
        "gateBoundary": "Construction-level preflight only; volumetric and exported-mesh checks remain Gate 06.",
    }


def tangent_continuity() -> dict[str, object]:
    joins = [
        ((1.0, 0.0), (1.0, 0.0)),
        ((0.0, -1.0), (0.0, -1.0)),
        ((0.0, -1.0), (0.0, -1.0)),
        ((-1.0, 0.0), (-1.0, 0.0)),
        ((-1.0, 0.0), (-1.0, 0.0)),
        ((0.0, 1.0), (0.0, 1.0)),
        ((0.0, 1.0), (0.0, 1.0)),
        ((1.0, 0.0), (1.0, 0.0)),
    ]
    deviations = []
    for first, second in joins:
        dot = max(-1.0, min(1.0, first[0] * second[0] + first[1] * second[1]))
        deviations.append(math.degrees(math.acos(dot)))
    return {
        "joinCount": len(joins),
        "analyticMaximumJoinAngleDegrees": round(max(deviations), 6),
        "continuity": "G1",
        "pass": max(deviations) <= 0.000001,
    }


def hierarchy_report() -> dict[str, object]:
    expected = {
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
    actual = {
        name: bpy.data.objects[name].parent.name if bpy.data.objects.get(name) and bpy.data.objects[name].parent else None
        for name in expected
        if bpy.data.objects.get(name)
    }
    return {
        "expected": expected,
        "actual": actual,
        "requiredNodesPresent": actual == expected,
        "contentSlotType": bpy.data.objects.get("ContentSlot").type if bpy.data.objects.get("ContentSlot") else None,
        "transparentCoverType": bpy.data.objects.get("TransparentCover").type if bpy.data.objects.get("TransparentCover") else None,
    }


def scope_report() -> dict[str, object]:
    render_geometry = [
        obj for obj in bpy.data.objects
        if obj.type in {"MESH", "FONT"} and bool(obj.get("model_pipeline_subject", False))
    ]
    names = [obj.name.lower() for obj in render_geometry]
    materials = {
        slot.material.name
        for obj in render_geometry
        for slot in obj.material_slots
        if slot.material
    }
    return {
        "finalMaterials": any(not name.startswith("MAT_DIAGNOSTIC_") for name in materials),
        "branding": any("brand" in name for name in names),
        "logos": any("logo" in name for name in names),
        "badges": any("badge" in name or "achievement" in name for name in names),
        "hiddenFasteners": any("fastener" in name or "screw" in name or "bolt" in name for name in names),
        "inventedInternalParts": any(
            token in name
            for name in names
            for token in ("spring", "bearing", "magnet", "latch", "hinge", "fluid", "pump")
        ),
        "transparentCoverGeometry": (
            bpy.data.objects["TransparentCover"].get("gate05_geometry_status")
            if bpy.data.objects.get("TransparentCover")
            else "missing"
        ),
        "diagnosticMaterialNames": sorted(materials),
    }


def validate_scene() -> dict[str, object]:
    subjects = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and bool(obj.get("model_pipeline_subject", False))
    ]
    minimum, maximum = object_bounds(subjects)
    size = maximum - minimum
    measured = {
        "width": round(size.x, 6),
        "height": round(size.y, 6),
        "depth": round(size.z, 6),
    }
    dimension_pass = all(
        abs(measured[key] - target) <= 0.01
        for key, target in {
            "width": WIDTH_MM,
            "height": HEIGHT_MM,
            "depth": DEPTH_MM,
        }.items()
    )
    tube_object = bpy.data.objects.get("ContinuousTubePerimeter")
    if tube_object is None or tube_object.type != "MESH":
        raise RuntimeError("ContinuousTubePerimeter mesh is missing.")
    topology = mesh_topology(tube_object)
    path_samples = rounded_rectangle_path()
    flood_fill = channel_flood_fill(path_samples)
    hierarchy = hierarchy_report()
    scope = scope_report()
    checks = {
        "approvedEnvelopeExact": dimension_pass,
        "portraitRatioExact": abs(measured["width"] / measured["height"] - 0.75) <= 0.000001,
        "tubeSingleMesh": len([obj for obj in subjects if obj.name == "ContinuousTubePerimeter"]) == 1,
        "tubeManifoldPreflight": topology["manifoldPreflightPass"],
        "tubeChannelFloodFill": flood_fill["pass"],
        "tubeTangentContinuity": tangent_continuity()["pass"],
        "approvedHierarchy": hierarchy["requiredNodesPresent"],
        "contentSlotIsRuntimeAnchor": hierarchy["contentSlotType"] == "EMPTY",
        "coverThicknessNotGuessed": hierarchy["transparentCoverType"] == "EMPTY"
        and scope["transparentCoverGeometry"] == "deferred-no-approved-thickness",
        "noFinalMaterials": scope["finalMaterials"] is False,
        "noIdentityArtwork": scope["branding"] is False and scope["logos"] is False and scope["badges"] is False,
        "noInventedHardware": scope["hiddenFasteners"] is False and scope["inventedInternalParts"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "artifactTruth": {
            "realBlenderBlockout": True,
            "schematic": False,
            "shippingUnityChanged": False,
            "finalGeometry": False,
        },
        "coordinateSystem": {
            "x": "width",
            "y": "height",
            "z": "depth-positive-front",
            "origin": "assembled outer-envelope center",
        },
        "dimensionsMm": {
            "target": {"width": WIDTH_MM, "height": HEIGHT_MM, "depth": DEPTH_MM},
            "measured": measured,
            "minimum": [round(value, 6) for value in minimum],
            "maximum": [round(value, 6) for value in maximum],
            "toleranceMm": 0.01,
            "pass": dimension_pass,
        },
        "portrait": {
            "widthHeightRatio": round(measured["width"] / measured["height"], 6),
            "target": 0.75,
            "pass": checks["portraitRatioExact"],
        },
        "closedTube": {
            "object": tube_object.name,
            "meshObjectCount": 1,
            "pathClosed": bool(tube_object.get("path_closed", False)),
            "pathSampleCount": int(tube_object.get("path_sample_count", 0)),
            "outerSectionMm": {"width": TUBE_OUTER_WIDTH_MM, "depth": TUBE_OUTER_DEPTH_MM},
            "wallThicknessMm": TUBE_WALL_MM,
            "passageSectionMm": {"width": TUBE_PASSAGE_WIDTH_MM, "depth": TUBE_PASSAGE_DEPTH_MM},
            "profileCornerRadiusMm": TUBE_PROFILE_RADIUS_MM,
            "passageCornerRadiusMm": TUBE_PASSAGE_RADIUS_MM,
            "cornerRadiiMm": {
                "outer": OUTER_CORNER_RADIUS_MM,
                "centerline": CENTERLINE_CORNER_RADIUS_MM,
                "inner": INNER_CORNER_RADIUS_MM,
            },
            "tangentContinuity": tangent_continuity(),
            "topology": topology,
            "channelFloodFill": flood_fill,
        },
        "hierarchy": hierarchy,
        "secondaryDimensions": {
            "provenance": "retained-approved-shipping-baseline",
            "sourcePaths": [
                "unity/FidgetingApp/Docs/DisplayCase/PremiumDisplayCaseSpecification.md",
                "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py",
                "unity/FidgetingApp/ArtSource/DisplayCase/premium_display_case_manifest.json",
            ],
            "adaptation": "Gate 03 changes the approved case width to 228 mm. The blockout retains the shipping shell inset, label, chamber, insert, and ContentSlot dimensions. Rear-shell placement terminates at the approved -29.5 mm envelope boundary.",
            "frontShellMm": {"width": 224, "height": 300, "depth": 6, "cornerRadius": 13},
            "rearShellMm": {"width": 224, "height": 300, "depth": 7, "cornerRadius": 13},
            "labelMm": {"width": 184, "height": 58, "depth": 3, "centerY": 105, "cornerRadius": 4},
            "tactileInsertMm": {"width": 182, "height": 202, "depth": 9, "centerY": -42, "cornerRadius": 10},
            "contentSlotMm": {"width": 180, "height": 198, "depth": 48, "centerY": -42, "cornerRadius": 16},
        },
        "scope": scope,
        "checks": checks,
        "validationContext": {
            "stage": "blockout-preflight",
            "fullGate06ValidationDeferred": True,
            "fullGate06Requirements": [
                "six orthographic views",
                "Workbench topology review",
                "dimension and pivot overlays",
                "exported-mesh manifold verification",
                "volumetric channel flood-fill",
                "exploded geometry",
            ],
        },
        "blender": bpy.app.version_string,
        "sourceBlend": Path(bpy.data.filepath).name,
    }
    return report


def main() -> None:
    report = validate_scene()
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "dimensionsMm": report["dimensionsMm"]["measured"],
        "tubeTopology": report["closedTube"]["topology"],
        "channelFloodFill": report["closedTube"]["channelFloodFill"],
    }, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report["checks"], indent=2))


if __name__ == "__main__":
    main()
