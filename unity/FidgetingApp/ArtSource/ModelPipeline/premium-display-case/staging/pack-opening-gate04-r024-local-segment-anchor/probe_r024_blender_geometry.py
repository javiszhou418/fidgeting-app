#!/usr/bin/env python3
"""Validate R024's segmented physical Pack mouth from saved Blender geometry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ART_V_BOTTOM = 0.020
ART_V_TOP = 0.815
SEGMENT_COUNT = 48
PACK_WIDTH_METERS = 0.255
SEGMENT_WIDTH_METERS = PACK_WIDTH_METERS / SEGMENT_COUNT
MAX_FACE_SPAN_METERS = SEGMENT_WIDTH_METERS * 1.05
PACK_MIN_X = -PACK_WIDTH_METERS * 0.5
PACK_MAX_X = PACK_WIDTH_METERS * 0.5
COLLAPSE_EPSILON = 1e-7
AREA_EPSILON = 1e-12
POSE_KEYS = (
    "Pose_TabCatch",
    "Pose_Resistance",
    "Pose_TearAdvance",
    "Pose_FormedMouth",
    "Pose_CaseContained",
    "Pose_ContinuousRise",
)
POSE_PROGRESS = (0.11, 0.28, 0.50, 0.70, 0.86, 1.0)
STATIC_SAMPLE_SECONDS = (0.50, 0.70, 0.90)
POSE_FRONT_INDEX = {
    "Pose_TabCatch": 0,
    "Pose_Resistance": 6,
    "Pose_TearAdvance": 18,
    "Pose_FormedMouth": 33,
    "Pose_CaseContained": 44,
    "Pose_ContinuousRise": 48,
}
VERTICES_PER_SEGMENT = {
    "Pack_RearInnerFoil": 8,
    "Pack_TopSealRemaining": 4,
    "Pack_InnerFoilMouth": 8,
    "Pack_InnerBackFoilRim": 4,
    "Pack_RolledCrimpLip": 16,
    "Pack_TornContourSweepCarrier": 4,
}
COMPONENT_ANCHOR_Y = {
    "Pack_RearInnerFoil": 0.1271 - 0.032 * 0.5,
    "Pack_TopSealRemaining": 0.1316 + 0.0055 * 0.5,
    "Pack_InnerFoilMouth": 0.1271 - 0.0048 * 0.5,
    "Pack_InnerBackFoilRim": 0.1271 + 0.0022 * 0.5,
    "Pack_RolledCrimpLip": 0.1271 - 0.00065,
    "Pack_TornContourSweepCarrier": 0.1271,
}
HIDDEN_ANCHOR_Z = 0.095 + 0.006 + 0.014


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def uv_by_vertex(mesh: bpy.types.Mesh) -> dict[int, list[tuple[float, float]]]:
    layer = mesh.uv_layers["UVMap"].data
    output: dict[int, list[tuple[float, float]]] = {}
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            output.setdefault(vertex_index, []).append(
                (layer[loop_index].uv.x, layer[loop_index].uv.y)
            )
    return output


def y_at_artwork_v(
    points, vertex_uvs: dict[int, list[tuple[float, float]]], target: float
) -> float:
    nearest = min(
        abs(uv[1] - target)
        for values in vertex_uvs.values()
        for uv in values
    )
    values = [
        points[index].co.y
        for index, uv_values in vertex_uvs.items()
        if min(abs(uv[1] - target) for uv in uv_values) <= nearest + 1e-5
    ]
    return sum(values) / len(values)


def point_bounds(points) -> dict[str, float]:
    return {
        "minX": min(coordinate(point).x for point in points),
        "maxX": max(coordinate(point).x for point in points),
        "minY": min(coordinate(point).y for point in points),
        "maxY": max(coordinate(point).y for point in points),
        "minZ": min(coordinate(point).z for point in points),
        "maxZ": max(coordinate(point).z for point in points),
    }


def coordinate(point) -> Vector:
    return point.co.copy() if hasattr(point, "co") else point.copy()


def is_collapsed(points) -> bool:
    anchor = coordinate(points[0])
    return all(
        (coordinate(point) - anchor).length <= COLLAPSE_EPSILON
        for point in points[1:]
    )


def active_segments(
    object_: bpy.types.Object, pose_key: str, vertices_per_segment: int
) -> list[int]:
    points = object_.data.shape_keys.key_blocks[pose_key].data
    return [
        segment
        for segment in range(SEGMENT_COUNT)
        if not is_collapsed(
            points[
                segment * vertices_per_segment : (segment + 1)
                * vertices_per_segment
            ]
        )
    ]


def max_face_x_span(object_: bpy.types.Object, pose_key: str) -> float:
    points = object_.data.shape_keys.key_blocks[pose_key].data
    return max_face_x_span_for_points(object_, points)


def max_face_x_span_for_points(
    object_: bpy.types.Object, points
) -> float:
    return max(
        max(coordinate(points[index]).x for index in polygon.vertices)
        - min(coordinate(points[index]).x for index in polygon.vertices)
        for polygon in object_.data.polygons
    )


def face_area(points, indices) -> float:
    coordinates = [coordinate(points[index]) for index in indices]
    if len(coordinates) < 3:
        return 0.0
    origin = coordinates[0]
    return sum(
        (coordinates[index] - origin)
        .cross(coordinates[index + 1] - origin)
        .length
        * 0.5
        for index in range(1, len(coordinates) - 1)
    )


def segment_polygons(
    object_: bpy.types.Object, segment: int, vertices_per_segment: int
):
    start = segment * vertices_per_segment
    end = start + vertices_per_segment
    return [
        polygon
        for polygon in object_.data.polygons
        if all(start <= index < end for index in polygon.vertices)
    ]


def segment_max_face_area(
    object_: bpy.types.Object, points, segment: int, vertices_per_segment: int
) -> float:
    polygons = segment_polygons(object_, segment, vertices_per_segment)
    if not polygons:
        return float("inf")
    return max(face_area(points, polygon.vertices) for polygon in polygons)


def guide_x(index: int) -> float:
    return PACK_MIN_X + index * SEGMENT_WIDTH_METERS


def segment_midpoint_x(segment: int) -> float:
    return (guide_x(segment) + guide_x(segment + 1)) * 0.5


def smooth01(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def timeline_tear_progress(seconds: float) -> float:
    if seconds < 0.14:
        return 0.0
    if seconds < 0.32:
        return 0.11 * smooth01((seconds - 0.14) / 0.18)
    if seconds < 0.50:
        return 0.11 + 0.17 * smooth01((seconds - 0.32) / 0.18)
    if seconds < 0.76:
        return 0.28 + 0.42 * smooth01((seconds - 0.50) / 0.26)
    if seconds < 1.03:
        return 0.70 + 0.16 * smooth01((seconds - 0.76) / 0.27)
    return 0.86 + 0.14 * smooth01((seconds - 1.03) / 0.25)


def blend_weights(progress: float) -> dict[str, float]:
    weights = {key: 0.0 for key in POSE_KEYS}
    progress = max(0.0, min(1.0, progress))
    if progress >= POSE_PROGRESS[-1]:
        weights[POSE_KEYS[-1]] = 1.0
        return weights
    if progress <= 0.0:
        return weights
    upper = next(
        index for index, sample in enumerate(POSE_PROGRESS)
        if progress <= sample
    )
    lower_progress = 0.0 if upper == 0 else POSE_PROGRESS[upper - 1]
    blend = (progress - lower_progress) / (
        POSE_PROGRESS[upper] - lower_progress
    )
    if upper > 0:
        weights[POSE_KEYS[upper - 1]] = 1.0 - blend
    weights[POSE_KEYS[upper]] = blend
    return weights


def blended_points(object_: bpy.types.Object, progress: float) -> list[Vector]:
    keys = object_.data.shape_keys.key_blocks
    basis = keys["Basis"].data
    weights = blend_weights(progress)
    output = [point.co.copy() for point in basis]
    for key_name, weight in weights.items():
        if weight <= 0.0:
            continue
        key = keys[key_name]
        relative = key.relative_key.data
        for index, point in enumerate(key.data):
            output[index] += (point.co - relative[index].co) * weight
    return output


def collapsed_segment_diagnostics(
    object_: bpy.types.Object,
    points,
    vertices_per_segment: int,
) -> dict[str, object]:
    anchors = []
    invalid_segments = []
    for segment in range(SEGMENT_COUNT):
        start = segment * vertices_per_segment
        segment_points = points[start : start + vertices_per_segment]
        if not is_collapsed(segment_points):
            continue
        anchor = coordinate(segment_points[0])
        area = segment_max_face_area(
            object_, points, segment, vertices_per_segment
        )
        nearest_station_distance = min(
            abs(anchor.x - guide_x(index))
            for index in range(SEGMENT_COUNT + 1)
        )
        local = (
            abs(anchor.x - segment_midpoint_x(segment)) <= COLLAPSE_EPSILON
            and abs(anchor.y - COMPONENT_ANCHOR_Y[object_.name])
            <= COLLAPSE_EPSILON
            and abs(anchor.z - HIDDEN_ANCHOR_Z) <= COLLAPSE_EPSILON
        )
        zero_area = area <= AREA_EPSILON
        no_global_station_anchor = (
            nearest_station_distance > SEGMENT_WIDTH_METERS * 0.20
        )
        anchors.append(
            {
                "segment": segment,
                "anchor": [anchor.x, anchor.y, anchor.z],
                "bounds": point_bounds(segment_points),
                "maxFaceArea": area,
                "localMidpointAnchor": local,
                "zeroArea": zero_area,
                "notAtGlobalGuideStation": no_global_station_anchor,
            }
        )
        if not local or not zero_area or not no_global_station_anchor:
            invalid_segments.append(segment)
    unique_coordinates = {
        tuple(round(value, 8) for value in anchor["anchor"])
        for anchor in anchors
    }
    return {
        "collapsedSegmentCount": len(anchors),
        "anchors": anchors,
        "sharedAnchorCount": len(anchors) - len(unique_coordinates),
        "globalSharedAnchorDetected": len(anchors) != len(unique_coordinates),
        "invalidSegments": invalid_segments,
        "passed": not invalid_segments
        and len(anchors) == len(unique_coordinates),
    }


def authored_anchor_diagnostics() -> dict[str, object]:
    result: dict[str, object] = {}
    for name, vertices_per_segment in VERTICES_PER_SEGMENT.items():
        object_ = bpy.data.objects[name]
        keys = object_.data.shape_keys.key_blocks
        poses = {
            key: collapsed_segment_diagnostics(
                object_, keys[key].data, vertices_per_segment
            )
            for key in ("Basis", *POSE_KEYS)
        }
        result[name] = {
            "poses": poses,
            "passed": all(item["passed"] for item in poses.values()),
        }
    return result


def static_blend_diagnostics() -> dict[str, object]:
    result: dict[str, object] = {}
    for seconds in STATIC_SAMPLE_SECONDS:
        progress = timeline_tear_progress(seconds)
        sample = {
            "seconds": seconds,
            "tearProgress": progress,
            "components": {},
        }
        for name, vertices_per_segment in VERTICES_PER_SEGMENT.items():
            object_ = bpy.data.objects[name]
            points = blended_points(object_, progress)
            bounds = point_bounds(points)
            collapsed = collapsed_segment_diagnostics(
                object_, points, vertices_per_segment
            )
            max_span = max_face_x_span_for_points(object_, points)
            sample["components"][name] = {
                "bounds": bounds,
                "maximumFaceXSpanMeters": max_span,
                "collapsedSegments": collapsed,
                "boundsStayInsidePack": (
                    bounds["minX"] >= PACK_MIN_X - COLLAPSE_EPSILON
                    and bounds["maxX"] <= PACK_MAX_X + COLLAPSE_EPSILON
                ),
                "facesStayWithinOneSegment": (
                    max_span <= MAX_FACE_SPAN_METERS + COLLAPSE_EPSILON
                ),
                "passed": (
                    collapsed["passed"]
                    and bounds["minX"] >= PACK_MIN_X - COLLAPSE_EPSILON
                    and bounds["maxX"] <= PACK_MAX_X + COLLAPSE_EPSILON
                    and max_span <= MAX_FACE_SPAN_METERS + COLLAPSE_EPSILON
                ),
            }
        sample["passed"] = all(
            item["passed"] for item in sample["components"].values()
        )
        result[f"{seconds:.2f}"] = sample
    return result


def progression_diagnostics() -> dict[str, object]:
    opened_only = (
        "Pack_RearInnerFoil",
        "Pack_InnerFoilMouth",
        "Pack_InnerBackFoilRim",
        "Pack_RolledCrimpLip",
        "Pack_TornContourSweepCarrier",
    )
    result: dict[str, object] = {}
    for pose_key, front in POSE_FRONT_INDEX.items():
        expected_open = list(range(min(SEGMENT_COUNT, front + 1)))
        expected_seal = list(range(min(SEGMENT_COUNT, front + 1), SEGMENT_COUNT))
        opened = {
            name: active_segments(
                bpy.data.objects[name],
                pose_key,
                VERTICES_PER_SEGMENT[name],
            )
            for name in opened_only
        }
        seal = active_segments(
            bpy.data.objects["Pack_TopSealRemaining"],
            pose_key,
            VERTICES_PER_SEGMENT["Pack_TopSealRemaining"],
        )
        result[pose_key] = {
            "openedSegments": opened,
            "sealedSegments": seal,
            "expectedOpenedSegments": expected_open,
            "expectedSealedSegments": expected_seal,
            "screenRightOrigin": True,
            "passed": (
                all(values == expected_open for values in opened.values())
                and seal == expected_seal
            ),
        }
    return result


def front_top_by_x(front: bpy.types.Object, pose_key: str) -> dict[float, float]:
    points = front.data.shape_keys.key_blocks[pose_key].data
    values: dict[float, tuple[float, float]] = {}
    for point in points:
        key = round(point.co.x, 7)
        current = values.get(key)
        if current is None or point.co.y > current[0]:
            values[key] = (point.co.y, point.co.z)
    return {key: value[1] for key, value in values.items()}


def maximum_depth_from_front(
    object_: bpy.types.Object,
    pose_key: str,
    vertices_per_segment: int,
    front_z_by_x: dict[float, float],
) -> float:
    depths = []
    points = object_.data.shape_keys.key_blocks[pose_key].data
    for segment in active_segments(object_, pose_key, vertices_per_segment):
        start = segment * vertices_per_segment
        for point in points[start : start + vertices_per_segment]:
            front_z = front_z_by_x[round(point.co.x, 7)]
            depths.append(point.co.z - front_z)
    return max(depths) if depths else 0.0


def minimum_depth_from_front(
    object_: bpy.types.Object,
    pose_key: str,
    vertices_per_segment: int,
    front_z_by_x: dict[float, float],
) -> float:
    depths = []
    points = object_.data.shape_keys.key_blocks[pose_key].data
    for segment in active_segments(object_, pose_key, vertices_per_segment):
        start = segment * vertices_per_segment
        for point in points[start : start + vertices_per_segment]:
            front_z = front_z_by_x[round(point.co.x, 7)]
            depths.append(point.co.z - front_z)
    return min(depths) if depths else 0.0


def cavity_thicknesses(object_: bpy.types.Object, pose_key: str) -> list[float]:
    points = object_.data.shape_keys.key_blocks[pose_key].data
    return [
        abs(points[segment * 8 + 4].co.z - points[segment * 8].co.z)
        for segment in active_segments(object_, pose_key, 8)
    ]


def expected_open_segments(pose_key: str) -> list[int]:
    return list(range(min(SEGMENT_COUNT, POSE_FRONT_INDEX[pose_key] + 1)))


def component_diagnostics(pose_key: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, vertices_per_segment in VERTICES_PER_SEGMENT.items():
        object_ = bpy.data.objects[name]
        active = active_segments(object_, pose_key, vertices_per_segment)
        result[name] = {
            "activeSegments": active,
            "activeSegmentCount": len(active),
            "collapsedSegmentCount": SEGMENT_COUNT - len(active),
            "maximumFaceXSpanMeters": max_face_x_span(object_, pose_key),
            "polygonCount": len(object_.data.polygons),
        }
    return result


def main() -> None:
    output_path = Path(parse_args().output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    front = bpy.data.objects["Pack_FrontPrintedFoil"]
    rig = bpy.data.objects["PackOpeningGate04R024_PACK_ONLY_RIG"]
    mesh = front.data
    vertex_uvs = uv_by_vertex(mesh)
    basis = mesh.shape_keys.key_blocks["Basis"].data
    formed = mesh.shape_keys.key_blocks["Pose_FormedMouth"].data
    contained = mesh.shape_keys.key_blocks["Pose_CaseContained"].data
    pack_bottom_y = float(front["physical_y_bottom"])
    printed_top_y = float(front["printed_y_top"])
    pack_top_y = float(front["outer_pack_top_y"])
    top_crimp_base_y = float(front["top_crimp_base_y"])
    tear_seam_y = float(front["tear_seam_y"])
    upper_third_start_y = pack_bottom_y + (pack_top_y - pack_bottom_y) * 2 / 3
    front_top_basis_y = y_at_artwork_v(basis, vertex_uvs, ART_V_TOP)
    front_top_formed_y = y_at_artwork_v(formed, vertex_uvs, ART_V_TOP)
    left_index = min(range(len(basis)), key=lambda index: basis[index].co.x)
    right_index = max(range(len(basis)), key=lambda index: basis[index].co.x)
    left_u = max(uv[0] for uv in vertex_uvs[left_index])
    right_u = min(uv[0] for uv in vertex_uvs[right_index])
    right_physical_x = min(point.co.x for point in basis)
    left_physical_x = max(point.co.x for point in basis)

    form_components = component_diagnostics("Pose_FormedMouth")
    contained_components = component_diagnostics("Pose_CaseContained")
    expected_formed_open = expected_open_segments("Pose_FormedMouth")
    expected_contained_open = expected_open_segments("Pose_CaseContained")
    component_names = tuple(VERTICES_PER_SEGMENT)
    formed_y_bounds = {
        name: point_bounds(
            bpy.data.objects[name].data.shape_keys.key_blocks["Pose_FormedMouth"].data
        )
        for name in component_names
    }
    liner = bpy.data.objects["Pack_InnerFoilMouth"]
    cavity = bpy.data.objects["Pack_RearInnerFoil"]
    formed_front_z = front_top_by_x(front, "Pose_FormedMouth")
    contained_front_z = front_top_by_x(front, "Pose_CaseContained")
    liner_formed_depth = maximum_depth_from_front(
        liner, "Pose_FormedMouth", 8, formed_front_z
    )
    liner_contained_depth = maximum_depth_from_front(
        liner, "Pose_CaseContained", 8, contained_front_z
    )
    cavity_formed_depth = minimum_depth_from_front(
        cavity, "Pose_FormedMouth", 8, formed_front_z
    )
    cavity_contained_depth = minimum_depth_from_front(
        cavity, "Pose_CaseContained", 8, contained_front_z
    )
    formed_cavity_thickness = cavity_thicknesses(cavity, "Pose_FormedMouth")
    contained_cavity_thickness = cavity_thicknesses(
        cavity, "Pose_CaseContained"
    )

    opened_only = (
        "Pack_RearInnerFoil",
        "Pack_InnerFoilMouth",
        "Pack_InnerBackFoilRim",
        "Pack_RolledCrimpLip",
    )
    no_bridge_components = (
        "Pack_RearInnerFoil",
        "Pack_TopSealRemaining",
        "Pack_InnerFoilMouth",
        "Pack_InnerBackFoilRim",
        "Pack_RolledCrimpLip",
        "Pack_TornContourSweepCarrier",
    )
    anchors = authored_anchor_diagnostics()
    blends = static_blend_diagnostics()
    progression = progression_diagnostics()
    checks = {
        "tearSeamMatchesPrintedTop": tear_seam_y == printed_top_y,
        "topCrimpSitsAbovePrintedTop": top_crimp_base_y > printed_top_y,
        "archiveBandWillMapAboveStandardBand": y_at_artwork_v(
            basis, vertex_uvs, 0.735
        )
        > y_at_artwork_v(basis, vertex_uvs, 0.215),
        "frontTopMovesDownward": front_top_basis_y - front_top_formed_y >= 0.005,
        "frontWindingFacesNegativeZCamera": sum(
            polygon.normal.z for polygon in mesh.polygons
        )
        / len(mesh.polygons)
        <= -0.90,
        "tearStartsAtUnityScreenRight": (
            y_at_artwork_v(basis, vertex_uvs, ART_V_TOP)
            - y_at_artwork_v(formed, vertex_uvs, ART_V_TOP)
            > 0.005
            and left_u >= 0.99
            and right_u <= 0.01
        ),
        "openedSegmentsProgressFromUnityScreenRight": all(
            item["passed"] and item["screenRightOrigin"]
            for item in progression.values()
        ),
        "noMouthComponentContainsFullWidthFaces": all(
            form_components[name]["maximumFaceXSpanMeters"]
            <= MAX_FACE_SPAN_METERS
            and contained_components[name]["maximumFaceXSpanMeters"]
            <= MAX_FACE_SPAN_METERS
            for name in no_bridge_components
        ),
        "foldedLinerDepthIsThreeToSixMillimeters": (
            0.003 <= liner_formed_depth <= 0.006
            and 0.003 <= liner_contained_depth <= 0.006
        ),
        "cavityBackWallStaysFarBehindFrontLip": (
            cavity_formed_depth >= 0.090 and cavity_contained_depth >= 0.090
        ),
        "cavityBackWallHasFiniteDepth": (
            formed_cavity_thickness
            and contained_cavity_thickness
            and min(formed_cavity_thickness) >= 0.004
            and min(contained_cavity_thickness) >= 0.004
        ),
        "segmentedTopologyIsExplicit": (
            rig.get("mouth_topology")
            == "48 independent physical segments; per-segment stable local collapse anchors; no shared mouth roof"
            and all(
                bpy.data.objects[name].get("independent_segment_count")
                == SEGMENT_COUNT
                for name in no_bridge_components
            )
        ),
        "topSealHasNoUvOrAlphaMask": "UV-clipped"
        not in bpy.data.objects["Pack_TopSealRemaining"].get(
            "opened_surface_behavior", ""
        ),
        "formedMouthPartsStayUpperThird": all(
            bounds["minY"] >= upper_third_start_y
            for bounds in formed_y_bounds.values()
        ),
        "authoredCollapsedSegmentsUseLocalAnchorsAndZeroArea": all(
            item["passed"] for item in anchors.values()
        ),
        "staticBlendsRetainLocalCollapsedSegments": all(
            component["collapsedSegments"]["passed"]
            for sample in blends.values()
            for component in sample["components"].values()
        ),
        "staticBlendsStayInsidePackAndOneSegmentWide": all(
            component["boundsStayInsidePack"]
            and component["facesStayWithinOneSegment"]
            for sample in blends.values()
            for component in sample["components"].values()
        ),
    }
    report = {
        "schema": "premium-display-case-gate04-r024-blender-segmented-mouth-probe.v1",
        "source": "actual Blender saved R024 Pack-only rig",
        "coordinates": {
            "packBottomY": pack_bottom_y,
            "printedTopY": printed_top_y,
            "packTopY": pack_top_y,
            "topCrimpBaseY": top_crimp_base_y,
            "tearSeamY": tear_seam_y,
            "upperThirdStartY": upper_third_start_y,
        },
        "front": {
            "rows": front["front_rows"],
            "winding": front["front_winding"],
            "uMapping": front["front_u_mapping"],
            "basisTopY": front_top_basis_y,
            "formedTopY": front_top_formed_y,
            "topDropMeters": front_top_basis_y - front_top_formed_y,
            "leftPhysicalXSourceU": left_u,
            "rightPhysicalXSourceU": right_u,
            "rightOriginDropMeters": y_at_artwork_v(
                basis, vertex_uvs, ART_V_TOP
            )
            - y_at_artwork_v(formed, vertex_uvs, ART_V_TOP),
        },
        "segmentTopology": {
            "stationCount": SEGMENT_COUNT + 1,
            "independentSegmentCount": SEGMENT_COUNT,
            "maximumAllowedFaceXSpanMeters": MAX_FACE_SPAN_METERS,
            "collapsedAnchor": {
                "perSegmentMidpoint": True,
                "stableBehindCavityZ": HIDDEN_ANCHOR_Z,
                "componentLocalY": COMPONENT_ANCHOR_Y,
                "globalTearFrontAnchor": False,
            },
            "sharedMouthRoof": False,
            "topSealUvOrAlphaClip": False,
        },
        "authoredCollapsedSegmentAnchors": anchors,
        "staticBlendPoints": blends,
        "openedAndSealedProgression": progression,
        "formedMouth": {
            "expectedOpenedSegments": expected_formed_open,
            "components": form_components,
            "componentYBounds": formed_y_bounds,
            "linerMaximumDepthFromFrontLipMeters": liner_formed_depth,
            "cavityMinimumDepthFromFrontLipMeters": cavity_formed_depth,
            "cavityBackThicknessMeters": min(formed_cavity_thickness),
        },
        "containedMouth": {
            "expectedOpenedSegments": expected_contained_open,
            "components": contained_components,
            "linerMaximumDepthFromFrontLipMeters": liner_contained_depth,
            "cavityMinimumDepthFromFrontLipMeters": cavity_contained_depth,
            "cavityBackThicknessMeters": min(contained_cavity_thickness),
        },
        "checks": checks,
    }
    report["passed"] = all(checks.values())
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("R024 segmented Blender geometry probe failed.")


if __name__ == "__main__":
    main()
