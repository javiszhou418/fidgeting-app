#!/usr/bin/env python3
"""Validate R022's segmented physical Pack mouth from saved Blender geometry."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


ART_V_BOTTOM = 0.020
ART_V_TOP = 0.815
SEGMENT_COUNT = 48
SEGMENT_WIDTH_METERS = 0.255 / SEGMENT_COUNT
MAX_FACE_SPAN_METERS = SEGMENT_WIDTH_METERS * 1.05
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
        "minX": min(point.co.x for point in points),
        "maxX": max(point.co.x for point in points),
        "minY": min(point.co.y for point in points),
        "maxY": max(point.co.y for point in points),
        "minZ": min(point.co.z for point in points),
        "maxZ": max(point.co.z for point in points),
    }


def is_collapsed(points) -> bool:
    anchor = points[0].co
    return all((point.co - anchor).length <= 1e-7 for point in points[1:])


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
    return max(
        max(points[index].co.x for index in polygon.vertices)
        - min(points[index].co.x for index in polygon.vertices)
        for polygon in object_.data.polygons
    )


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
    rig = bpy.data.objects["PackOpeningGate04R022_PACK_ONLY_RIG"]
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
    )
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
        "formedOpenedOnlyComponentsHonorLocalOpen": all(
            form_components[name]["activeSegments"] == expected_formed_open
            for name in opened_only
        ),
        "containedOpenedOnlyComponentsHonorLocalOpen": all(
            contained_components[name]["activeSegments"] == expected_contained_open
            for name in opened_only
        ),
        "formedTopSealHonorsSealedSegments": (
            form_components["Pack_TopSealRemaining"]["activeSegments"]
            == list(range(POSE_FRONT_INDEX["Pose_FormedMouth"] + 1, SEGMENT_COUNT))
        ),
        "containedTopSealHonorsSealedSegments": (
            contained_components["Pack_TopSealRemaining"]["activeSegments"]
            == list(
                range(POSE_FRONT_INDEX["Pose_CaseContained"] + 1, SEGMENT_COUNT)
            )
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
            == "48 independent physical segments; no shared mouth roof"
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
    }
    report = {
        "schema": "premium-display-case-gate04-r022-blender-segmented-mouth-probe.v1",
        "source": "actual Blender saved R022 Pack-only rig",
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
            "sharedMouthRoof": False,
            "topSealUvOrAlphaClip": False,
        },
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
        raise RuntimeError("R022 segmented Blender geometry probe failed.")


if __name__ == "__main__":
    main()
