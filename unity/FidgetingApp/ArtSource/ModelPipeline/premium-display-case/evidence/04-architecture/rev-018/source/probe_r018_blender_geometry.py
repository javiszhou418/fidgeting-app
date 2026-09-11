#!/usr/bin/env python3
"""Record R018 physical Pack coordinates from the saved Blender scene."""

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


def main() -> None:
    output_path = Path(parse_args().output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    front = bpy.data.objects["Pack_FrontPrintedFoil"]
    mesh = front.data
    vertex_uvs = uv_by_vertex(mesh)
    basis = mesh.shape_keys.key_blocks["Basis"].data
    formed = mesh.shape_keys.key_blocks["Pose_FormedMouth"].data
    pack_bottom_y = float(front["physical_y_bottom"])
    pack_top_y = float(front["physical_y_top"])
    upper_third_start_y = pack_bottom_y + (pack_top_y - pack_bottom_y) * 2 / 3
    front_top_basis_y = y_at_artwork_v(basis, vertex_uvs, ART_V_TOP)
    front_top_formed_y = y_at_artwork_v(formed, vertex_uvs, ART_V_TOP)
    left_index = min(range(len(basis)), key=lambda index: basis[index].co.x)
    right_index = max(range(len(basis)), key=lambda index: basis[index].co.x)
    left_u = max(uv[0] for uv in vertex_uvs[left_index])
    right_u = min(uv[0] for uv in vertex_uvs[right_index])
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
    report = {
        "schema": "premium-display-case-gate04-r018-blender-coordinate-probe.v1",
        "source": "actual Blender saved R018 rig",
        "coordinates": {
            "packBottomY": pack_bottom_y,
            "packTopY": pack_top_y,
            "tearSeamY": float(front["tear_seam_y"]),
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
        },
        "formedMouthComponents": components,
    }
    checks = {
        "physicalTopMatchesTearSeam": report["coordinates"]["tearSeamY"]
        == pack_top_y,
        "archiveBandWillMapAboveStandardBand": y_at_artwork_v(
            basis, vertex_uvs, 0.735
        )
        > y_at_artwork_v(basis, vertex_uvs, 0.215),
        "frontTopMovesDownward": report["front"]["topDropMeters"] >= 0.005,
        "frontWindingFacesNegativeZCamera": report["front"]["meanNormalZ"] <= -0.90,
        "allMouthPartsAttachInUpperThird": all(
            bounds["minY"] >= upper_third_start_y
            for bounds in components.values()
        ),
        "uCompensationIsExplicit": left_u >= 0.99 and right_u <= 0.01,
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("R018 Blender coordinate probe failed.")


if __name__ == "__main__":
    main()
