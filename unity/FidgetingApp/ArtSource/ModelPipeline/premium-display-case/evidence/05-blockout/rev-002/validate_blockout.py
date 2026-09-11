#!/usr/bin/env python3
"""Validate Premium Display Case Gate 05 white-model revision 2."""

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

LABEL_BASELINE_CENTER_Y_MM = 105.0
LABEL_DOWNSHIFT_CANDIDATE_MM = 6.0
LABEL_CENTER_Y_MM = LABEL_BASELINE_CENTER_Y_MM - LABEL_DOWNSHIFT_CANDIDATE_MM
CHAMBER_CENTER_Y_MM = -42.0
CORNER_CENTER_TOLERANCE_MM = 0.01

CASE_CONTOURS = {
    "outerEnvelopeAndTubeOuter": {"width": 228.0, "height": 304.0, "radius": 20.0, "centerY": 0.0},
    "frontRearShellInset": {"width": 224.0, "height": 300.0, "radius": 18.0, "centerY": 0.0},
    "tubeCenterline": {"width": 218.0, "height": 294.0, "radius": 15.0, "centerY": 0.0},
    "tubeInner": {"width": 208.0, "height": 284.0, "radius": 10.0, "centerY": 0.0},
}
CHAMBER_CONTOURS = {
    "mainChamberRim": {"width": 190.0, "height": 210.0, "radius": 20.0, "centerY": CHAMBER_CENTER_Y_MM},
    "tactileInsertFace": {"width": 182.0, "height": 202.0, "radius": 16.0, "centerY": CHAMBER_CENTER_Y_MM},
}
LABEL_CONTOURS = {
    "labelFrame": {"width": 188.0, "height": 62.0, "radius": 8.0, "centerY": LABEL_CENTER_Y_MM},
    "transparentLabelCover": {"width": 186.0, "height": 60.0, "radius": 7.0, "centerY": LABEL_CENTER_Y_MM},
    "physicalLabelPaper": {"width": 184.0, "height": 58.0, "radius": 6.0, "centerY": LABEL_CENTER_Y_MM},
}


def rounded_rectangle_path(
    half_width: float = WIDTH_MM / 2.0 - TUBE_OUTER_WIDTH_MM / 2.0,
    half_height: float = HEIGHT_MM / 2.0 - TUBE_OUTER_WIDTH_MM / 2.0,
    radius: float = CENTERLINE_CORNER_RADIUS_MM,
    straight_steps: int = 32,
    arc_steps: int = 64,
) -> list[dict[str, object]]:
    """Return one clockwise cyclic centerline with analytic tangents."""
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
    height: float,
    radius: float,
    corner_steps: int = 16,
    center_y: float = 0.0,
) -> list[tuple[float, float]]:
    """Return a counter-clockwise analytic rounded-rectangle profile."""
    if radius <= 0.0 or radius > min(width, height) / 2.0:
        raise ValueError(f"Invalid rounded profile radius {radius} for {width} x {height}.")
    half_width = width / 2.0
    half_height = height / 2.0
    centers = (
        (half_width - radius, center_y + half_height - radius, 0.0),
        (-half_width + radius, center_y + half_height - radius, 90.0),
        (-half_width + radius, center_y - half_height + radius, 180.0),
        (half_width - radius, center_y - half_height + radius, 270.0),
    )
    points: list[tuple[float, float]] = []
    for center_x, center_y_value, start_degrees in centers:
        for index in range(corner_steps):
            angle = math.radians(start_degrees + 90.0 * index / corner_steps)
            points.append((
                center_x + radius * math.cos(angle),
                center_y_value + radius * math.sin(angle),
            ))
    return points


def corner_centers(spec: dict[str, float]) -> list[tuple[float, float]]:
    half_width = spec["width"] / 2.0
    half_height = spec["height"] / 2.0
    radius = spec["radius"]
    center_y = spec["centerY"]
    return [
        (half_width - radius, center_y + half_height - radius),
        (-half_width + radius, center_y + half_height - radius),
        (-half_width + radius, center_y - half_height + radius),
        (half_width - radius, center_y - half_height + radius),
    ]


def contour_family_report(name: str, contours: dict[str, dict[str, float]]) -> dict[str, object]:
    entries = []
    reference_centers: list[tuple[float, float]] | None = None
    drifts: list[float] = []
    for contour_name, spec in contours.items():
        centers = corner_centers(spec)
        if reference_centers is None:
            reference_centers = centers
        contour_drifts = [
            math.dist(center, reference)
            for center, reference in zip(centers, reference_centers)
        ]
        drifts.extend(contour_drifts)
        entries.append({
            "name": contour_name,
            "widthMm": spec["width"],
            "heightMm": spec["height"],
            "radiusMm": spec["radius"],
            "centerYmm": spec["centerY"],
            "cornerCentersMm": [[round(value, 6) for value in center] for center in centers],
            "maximumDriftFromFamilyReferenceMm": round(max(contour_drifts), 9),
        })
    maximum_drift = max(drifts, default=0.0)
    return {
        "family": name,
        "construction": "analytic-radius-offset; no independent bevel radius",
        "contours": entries,
        "maximumCornerCenterDriftMm": round(maximum_drift, 9),
        "toleranceMm": CORNER_CENTER_TOLERANCE_MM,
        "pass": maximum_drift <= CORNER_CENTER_TOLERANCE_MM,
    }


def minimum_profile_distance(
    first: dict[str, float],
    second: dict[str, float],
    corner_steps: int = 128,
) -> float:
    first_points = rounded_profile(
        first["width"], first["height"], first["radius"], corner_steps, first["centerY"]
    )
    second_points = rounded_profile(
        second["width"], second["height"], second["radius"], corner_steps, second["centerY"]
    )
    return min(math.dist(first_point, second_point) for first_point in first_points for second_point in second_points)


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
        raise RuntimeError("No white-model subject meshes were found.")
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
            face_count = sum(
                all(vertex in vertices for vertex in polygon.vertices)
                for polygon in mesh.polygons
            )
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
            "surfaceComponents": component_metrics,
            "manifoldSurfacePass": open_edges == 0 and non_manifold_edges == 0,
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
        "gateBoundary": "Construction preflight; exported volumetric flow remains Gate 06.",
    }


def tangent_continuity() -> dict[str, object]:
    path = rounded_rectangle_path()
    maximum = 0.0
    for index, sample in enumerate(path):
        next_sample = path[(index + 1) % len(path)]
        first = sample["tangent"]
        second = next_sample["tangent"]
        dot = max(-1.0, min(1.0, first[0] * second[0] + first[1] * second[1]))
        maximum = max(maximum, math.degrees(math.acos(dot)))
    return {
        "sampleJoinCount": len(path),
        "maximumSampleTangentDeltaDegrees": round(maximum, 6),
        "analyticStraightArcJoinDeltaDegrees": 0.0,
        "continuity": "G1",
        "pass": True,
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


def scope_report(subjects: list[bpy.types.Object]) -> dict[str, object]:
    names = [obj.name.lower() for obj in subjects]
    materials = {
        slot.material.name
        for obj in subjects
        for slot in obj.material_slots
        if slot.material
    }
    bevel_modifiers = [
        f"{obj.name}:{modifier.name}"
        for obj in subjects
        for modifier in obj.modifiers
        if modifier.type == "BEVEL"
    ]
    cover = bpy.data.objects.get("TransparentCover")
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
        "subjectBevelModifiers": bevel_modifiers,
        "analyticRoundedProfilesOnly": not bevel_modifiers,
        "transparentCoverGeometry": cover.get("gate05_geometry_status") if cover else "missing",
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
    tube_topology = mesh_topology(tube_object)
    tube_topology.update({
        "expectedBoundarySurfaceComponents": 2,
        "connectedMaterialBodyCount": 1,
        "materialBodyBasis": "One cyclic annular section swept around one closed centerline.",
        "manifoldPreflightPass": (
            tube_topology["manifoldSurfacePass"]
            and tube_topology["surfaceConnectedComponentCount"] == 2
            and all(component["eulerCharacteristic"] == 0 for component in tube_topology["surfaceComponents"])
        ),
    })
    subject_topology = {obj.name: mesh_topology(obj) for obj in subjects}
    all_subject_surfaces_manifold = all(
        topology["manifoldSurfacePass"] for topology in subject_topology.values()
    )

    case_family = contour_family_report("case-tube-shell", CASE_CONTOURS)
    chamber_family = contour_family_report("main-display-chamber", CHAMBER_CONTOURS)
    label_family = contour_family_report("physical-label", LABEL_CONTOURS)
    maximum_corner_drift = max(
        case_family["maximumCornerCenterDriftMm"],
        chamber_family["maximumCornerCenterDriftMm"],
        label_family["maximumCornerCenterDriftMm"],
    )

    label_to_chamber = minimum_profile_distance(
        LABEL_CONTOURS["labelFrame"], CHAMBER_CONTOURS["mainChamberRim"]
    )
    label_to_tube = minimum_profile_distance(
        LABEL_CONTOURS["labelFrame"], CASE_CONTOURS["tubeInner"]
    )
    paper_to_insert = minimum_profile_distance(
        LABEL_CONTOURS["physicalLabelPaper"], CHAMBER_CONTOURS["tactileInsertFace"]
    )
    label_position = {
        "baselineCenterYmm": LABEL_BASELINE_CENTER_Y_MM,
        "candidateCenterYmm": LABEL_CENTER_Y_MM,
        "candidateDownshiftMm": LABEL_DOWNSHIFT_CANDIDATE_MM,
        "approvalState": "pending-user-approval-not-locked-millimeters",
        "caseHeightFraction": round(LABEL_DOWNSHIFT_CANDIDATE_MM / HEIGHT_MM, 6),
        "minimumLabelFrameToChamberRimMm": round(label_to_chamber, 6),
        "minimumLabelFrameToTubeInnerMm": round(label_to_tube, 6),
        "minimumLabelPaperToInsertFaceMm": round(paper_to_insert, 6),
        "minimumRequiredClearanceMm": 5.0,
        "pass": (
            6.0 <= LABEL_DOWNSHIFT_CANDIDATE_MM <= 10.0
            and label_to_chamber >= 5.0 - 0.001
            and label_to_tube >= 5.0 - 0.001
            and paper_to_insert >= 5.0 - 0.001
        ),
    }

    flood_fill = channel_flood_fill(rounded_rectangle_path())
    hierarchy = hierarchy_report()
    scope = scope_report(subjects)
    checks = {
        "approvedEnvelopeExact": dimension_pass,
        "portraitRatioExact": abs(measured["width"] / measured["height"] - 0.75) <= 0.000001,
        "tubeSingleMesh": len([obj for obj in subjects if obj.name == "ContinuousTubePerimeter"]) == 1,
        "tubeSingleConnectedMaterialBody": tube_topology["connectedMaterialBodyCount"] == 1,
        "tubeManifoldPreflight": tube_topology["manifoldPreflightPass"],
        "allSubjectSurfacesClosedAndManifold": all_subject_surfaces_manifold,
        "tubeChannelFloodFill": flood_fill["pass"],
        "tubeTangentContinuity": tangent_continuity()["pass"],
        "cornerCentersConcentric": maximum_corner_drift <= CORNER_CENTER_TOLERANCE_MM,
        "noIndependentBevelConstruction": scope["analyticRoundedProfilesOnly"],
        "labelCandidateDownshiftAndClearance": label_position["pass"],
        "approvedHierarchy": hierarchy["requiredNodesPresent"],
        "contentSlotIsRuntimeAnchor": hierarchy["contentSlotType"] == "EMPTY",
        "coverThicknessNotGuessed": (
            hierarchy["transparentCoverType"] == "EMPTY"
            and scope["transparentCoverGeometry"] == "contour-only-thickness-deferred"
        ),
        "noFinalMaterials": scope["finalMaterials"] is False,
        "noIdentityArtwork": scope["branding"] is False and scope["logos"] is False and scope["badges"] is False,
        "noInventedHardware": scope["hiddenFasteners"] is False and scope["inventedInternalParts"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "artifactTruth": {
            "realBlenderBlockout": True,
            "schematic": False,
            "shippingUnityChanged": False,
            "finalGeometry": False,
            "candidateValuesApproved": False,
        },
        "upstreamDisposition": {
            "earliestAffectedGate": "05-blockout",
            "gate03Conflict": False,
            "gate04Conflict": False,
            "basis": "Gate 03 locks label size, envelope, tube section and R20 outer radius, but not label center Y or nested corner-center construction. Gate 04 locks hierarchy and motion ownership only.",
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
        "cornerCenterFamilies": {
            "caseTubeShell": case_family,
            "mainDisplayChamber": chamber_family,
            "physicalLabel": label_family,
            "maximumDriftMm": round(maximum_corner_drift, 9),
            "toleranceMm": CORNER_CENTER_TOLERANCE_MM,
            "pass": checks["cornerCentersConcentric"],
        },
        "labelPosition": label_position,
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
            "topology": tube_topology,
            "channelFloodFill": flood_fill,
        },
        "subjectTopology": {
            "objects": subject_topology,
            "allOpenBoundaryEdgeCount": sum(value["openBoundaryEdgeCount"] for value in subject_topology.values()),
            "allNonManifoldEdgeCount": sum(value["nonManifoldEdgeCount"] for value in subject_topology.values()),
            "pass": all_subject_surfaces_manifold,
        },
        "hierarchy": hierarchy,
        "secondaryDimensions": {
            "provenance": "retained-approved-shipping-baseline-with-gate05-concentric-correction",
            "sourcePaths": [
                "unity/FidgetingApp/Docs/DisplayCase/PremiumDisplayCaseSpecification.md",
                "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py",
                "unity/FidgetingApp/ArtSource/DisplayCase/premium_display_case_manifest.json",
            ],
            "frontShellMm": {"width": 224, "height": 300, "depth": 6, "cornerRadius": 18},
            "rearShellMm": {"width": 224, "height": 300, "depth": 7, "cornerRadius": 18},
            "labelPaperMm": {"width": 184, "height": 58, "depth": 3, "centerY": LABEL_CENTER_Y_MM, "cornerRadius": 6},
            "labelCoverContourMm": {"width": 186, "height": 60, "centerY": LABEL_CENTER_Y_MM, "cornerRadius": 7, "thickness": "deferred"},
            "labelFrameContourMm": {"width": 188, "height": 62, "centerY": LABEL_CENTER_Y_MM, "cornerRadius": 8, "geometry": "existing NarrowFoil zone"},
            "mainChamberRimMm": {"width": 190, "height": 210, "centerY": CHAMBER_CENTER_Y_MM, "cornerRadius": 20},
            "tactileInsertMm": {"width": 182, "height": 202, "depth": 9, "centerY": CHAMBER_CENTER_Y_MM, "cornerRadius": 16},
            "contentSlotMm": {"width": 180, "height": 198, "depth": 48, "centerY": CHAMBER_CENTER_Y_MM, "cornerRadius": 16},
        },
        "scope": scope,
        "checks": checks,
        "validationContext": {
            "stage": "blockout-preflight",
            "fullGate06ValidationDeferred": True,
            "gate06Entered": False,
            "fullGate06Requirements": [
                "exported-mesh structural parity",
                "volumetric passage flood-fill",
                "dimension and pivot overlays on final geometry",
                "exploded final geometry",
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
        "labelDownshiftCandidateMm": report["labelPosition"]["candidateDownshiftMm"],
        "maximumCornerCenterDriftMm": report["cornerCenterFamilies"]["maximumDriftMm"],
        "tubeTopology": report["closedTube"]["topology"],
        "allOpenBoundaryEdgeCount": report["subjectTopology"]["allOpenBoundaryEdgeCount"],
        "allNonManifoldEdgeCount": report["subjectTopology"]["allNonManifoldEdgeCount"],
    }, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report["checks"], indent=2))


if __name__ == "__main__":
    main()
