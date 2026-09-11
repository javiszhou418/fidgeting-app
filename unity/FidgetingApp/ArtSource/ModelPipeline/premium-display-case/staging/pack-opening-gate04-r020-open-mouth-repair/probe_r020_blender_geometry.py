#!/usr/bin/env python3
"""Record R020 Pack-mouth coordinates from the saved Blender scene."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


ART_V_BOTTOM = 0.020
ART_V_TOP = 0.815


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


def object_y_bounds(object_: bpy.types.Object, key: str) -> dict[str, float]:
    points = object_.data.shape_keys.key_blocks[key].data
    return {
        "minY": min(point.co.y for point in points),
        "maxY": max(point.co.y for point in points),
    }


def y_at_x(points, target_x: float) -> float:
    nearest = min(abs(point.co.x - target_x) for point in points)
    values = [
        point.co.y
        for point in points
        if abs(point.co.x - target_x) <= nearest + 1e-6
    ]
    return sum(values) / len(values)


def main() -> None:
    output_path = Path(parse_args().output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    front = bpy.data.objects["Pack_FrontPrintedFoil"]
    mesh = front.data
    vertex_uvs = uv_by_vertex(mesh)
    basis = mesh.shape_keys.key_blocks["Basis"].data
    formed = mesh.shape_keys.key_blocks["Pose_FormedMouth"].data
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
    right_origin_drop = y_at_x(basis, right_physical_x) - y_at_x(
        formed, right_physical_x
    )
    left_far_drop = y_at_x(basis, left_physical_x) - y_at_x(
        formed, left_physical_x
    )
    component_names = (
        "Pack_TopSealRemaining",
        "Pack_InnerFoilMouth",
        "Pack_InnerBackFoilRim",
        "Pack_RolledCrimpLip",
        "Pack_TornContourSweepCarrier",
        "Pack_TearFrontSidewall",
        "Pack_TabSidewall",
        "Pack_ReleasedSealStrip",
        "Pack_TopRightPullTab",
    )
    components = {
        name: object_y_bounds(bpy.data.objects[name], "Pose_FormedMouth")
        for name in component_names
    }
    strip = bpy.data.objects["Pack_ReleasedSealStrip"]
    strip_formed = strip.data.shape_keys.key_blocks["Pose_FormedMouth"].data
    strip_root = strip_formed[0].co
    seal_formed = bpy.data.objects["Pack_TopSealRemaining"].data.shape_keys.key_blocks[
        "Pose_FormedMouth"
    ].data
    crimp_right_open_height = abs(seal_formed[1].co.y - seal_formed[0].co.y)
    crimp_left_sealed_height = abs(
        seal_formed[-1].co.y - seal_formed[-2].co.y
    )
    cavity_formed = bpy.data.objects["Pack_RearInnerFoil"].data.shape_keys.key_blocks[
        "Pose_FormedMouth"
    ].data
    cavity_back_thickness = abs(cavity_formed[3].co.z - cavity_formed[0].co.z)
    report = {
        "schema": "premium-display-case-gate04-r020-blender-coordinate-probe.v1",
        "source": "actual Blender saved R020 rig",
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
            "basisBottomY": y_at_artwork_v(basis, vertex_uvs, ART_V_BOTTOM),
            "basisTopY": front_top_basis_y,
            "formedTopY": front_top_formed_y,
            "topDropMeters": front_top_basis_y - front_top_formed_y,
            "meanNormalZ": sum(polygon.normal.z for polygon in mesh.polygons)
            / len(mesh.polygons),
            "leftPhysicalXSourceU": left_u,
            "rightPhysicalXSourceU": right_u,
            "rightOriginDropMeters": right_origin_drop,
            "leftFarDropMeters": left_far_drop,
        },
        "formedMouthComponents": components,
        "releasedStrip": {
            "rootX": strip_root.x,
            "rootY": strip_root.y,
            "rootZ": strip_root.z,
            "unityMirrorCompensation":
                "negative Blender X projects to rendered screen-right"
        },
        "sealRepair": {
            "tearOriginPhysicalU": 0.0,
            "tearOriginUnityScreen": "right",
            "openedSide": "physical-u less than or equal to tear front",
            "rightOpenedCrimpHeightMeters": crimp_right_open_height,
            "leftSealedCrimpHeightMeters": crimp_left_sealed_height,
        },
        "cavityRepair": {
            "backWallThicknessMeters": cavity_back_thickness,
            "backWallFiniteDepth": cavity_back_thickness >= 0.004,
        },
    }
    checks = {
        "tearSeamMatchesPrintedTop": tear_seam_y == printed_top_y,
        "topCrimpSitsAbovePrintedTop": top_crimp_base_y > printed_top_y,
        "archiveBandWillMapAboveStandardBand": y_at_artwork_v(
            basis, vertex_uvs, 0.735
        )
        > y_at_artwork_v(basis, vertex_uvs, 0.215),
        "frontTopMovesDownward": report["front"]["topDropMeters"] >= 0.005,
        "frontWindingFacesNegativeZCamera": report["front"]["meanNormalZ"] <= -0.90,
        "tearStartsAtUnityScreenRight": (
            right_origin_drop >= 0.005
            and right_origin_drop > left_far_drop + 0.005
            and left_u >= 0.99
            and right_u <= 0.01
        ),
        "openedCrimpCollapsesIntoFineLip": (
            crimp_right_open_height <= 0.0001
            and crimp_left_sealed_height >= 0.004
        ),
        "cavityBackWallHasFiniteDepth": cavity_back_thickness >= 0.004,
        "allMouthPartsAttachInUpperThird": all(
            bounds["minY"] >= upper_third_start_y
            for bounds in components.values()
        ),
        "stripRootIsReflectedForUnityScreenRight": strip_root.x < 0.0,
        "uCompensationIsExplicit": left_u >= 0.99 and right_u <= 0.01,
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("R020 Blender coordinate probe failed.")


if __name__ == "__main__":
    main()
