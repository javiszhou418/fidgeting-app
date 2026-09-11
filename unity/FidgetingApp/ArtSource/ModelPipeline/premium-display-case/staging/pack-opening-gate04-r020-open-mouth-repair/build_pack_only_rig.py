#!/usr/bin/env python3
"""Build the R020 Pack-only foil-pouch rig from seven authored tear poses."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Vector


CANVAS_WIDTH = 0.255
CANVAS_HEIGHT = 0.340
CANVAS_BOTTOM_Y = -0.150
ART_V_BOTTOM = 0.020
ART_V_TOP = 0.815
PACK_BOTTOM_Y = CANVAS_BOTTOM_Y + CANVAS_HEIGHT * ART_V_BOTTOM
PRINTED_TOP_Y = CANVAS_BOTTOM_Y + CANVAS_HEIGHT * ART_V_TOP
TEAR_SEAM_Y = PRINTED_TOP_Y
CRIMP_CLEARANCE = 0.0045
CRIMP_BASE_Y = TEAR_SEAM_Y + CRIMP_CLEARANCE
TOP_SEAL_HEIGHT = 0.0055
PACK_TOP_Y = CRIMP_BASE_Y + TOP_SEAL_HEIGHT
FRONT_Z = -0.012
BACK_Z = 0.095
MOUTH_DEPTH = BACK_Z - FRONT_Z
FOIL_THICKNESS = 0.00075
CAVITY_HEIGHT = 0.024
CAVITY_BACK_THICKNESS = 0.006
BODY_ROWS = 16
GUIDE_X = tuple(-1.0 + index * 2.0 / 48.0 for index in range(49))
LIP_SIDES = 8
STRIP_HALF_WIDTH = 0.0065

# These are authored local offsets, not a periodic or tooth-like displacement.
# They break an even tear silhouette while preserving a fine continuous contour.
IRREGULARITY = (
    -0.18, 0.11, -0.07, 0.23, -0.12, 0.04, 0.19, -0.21, 0.08, -0.04,
    0.15, -0.15, 0.02, 0.20, -0.09, 0.07, -0.17, 0.12, -0.02, 0.16,
    -0.11, 0.05, -0.20, 0.10, -0.06, 0.22, -0.14, 0.03, 0.18, -0.08,
    0.09, -0.19, 0.06, -0.05, 0.17, -0.13, 0.01, 0.14, -0.16, 0.08,
    -0.03, 0.20, -0.10, 0.04, -0.18, 0.12, -0.07, 0.16, -0.05,
)


@dataclass(frozen=True)
class Pose:
    key: str
    progress: float
    tear_start: int
    max_front_drop: float
    inner_lag: float
    tab_lift: tuple[float, float, float]
    strip_spine: tuple[tuple[float, float, float, float], ...]


POSES = (
    Pose(
        "Pose_TabCatch",
        0.11,
        48,
        0.003,
        0.16,
        (-0.001, 0.003, -0.004),
        (
            (-0.086, TEAR_SEAM_Y + 0.003, -0.015, 0.05),
            (-0.092, TEAR_SEAM_Y + 0.005, -0.018, 0.18),
            (-0.099, TEAR_SEAM_Y + 0.007, -0.020, 0.32),
            (-0.106, TEAR_SEAM_Y + 0.006, -0.018, 0.46),
            (-0.111, TEAR_SEAM_Y + 0.004, -0.016, 0.58),
        ),
    ),
    Pose(
        "Pose_Resistance",
        0.28,
        42,
        0.014,
        0.22,
        (-0.003, 0.007, -0.011),
        (
            (-0.086, TEAR_SEAM_Y + 0.002, -0.017, 0.10),
            (-0.094, TEAR_SEAM_Y + 0.006, -0.024, 0.38),
            (-0.102, TEAR_SEAM_Y + 0.010, -0.030, 0.82),
            (-0.109, TEAR_SEAM_Y + 0.008, -0.026, 1.20),
            (-0.114, TEAR_SEAM_Y + 0.004, -0.020, 1.42),
        ),
    ),
    Pose(
        "Pose_TearAdvance",
        0.50,
        30,
        0.040,
        0.29,
        (-0.005, 0.010, -0.017),
        (
            (-0.086, TEAR_SEAM_Y + 0.001, -0.020, 0.12),
            (-0.095, TEAR_SEAM_Y + 0.006, -0.032, 0.52),
            (-0.104, TEAR_SEAM_Y + 0.011, -0.039, 1.05),
            (-0.111, TEAR_SEAM_Y + 0.007, -0.030, 1.46),
            (-0.116, TEAR_SEAM_Y + 0.002, -0.021, 1.74),
        ),
    ),
    Pose(
        "Pose_FormedMouth",
        0.70,
        15,
        0.068,
        0.34,
        (-0.006, 0.011, -0.020),
        (
            (-0.086, TEAR_SEAM_Y, -0.021, 0.18),
            (-0.096, TEAR_SEAM_Y + 0.006, -0.035, 0.64),
            (-0.105, TEAR_SEAM_Y + 0.012, -0.044, 1.17),
            (-0.113, TEAR_SEAM_Y + 0.008, -0.034, 1.58),
            (-0.118, TEAR_SEAM_Y + 0.002, -0.022, 1.92),
        ),
    ),
    Pose(
        "Pose_CaseContained",
        0.86,
        4,
        0.077,
        0.38,
        (-0.007, 0.011, -0.020),
        (
            (-0.086, TEAR_SEAM_Y - 0.001, -0.021, 0.22),
            (-0.096, TEAR_SEAM_Y + 0.006, -0.036, 0.72),
            (-0.106, TEAR_SEAM_Y + 0.013, -0.045, 1.25),
            (-0.114, TEAR_SEAM_Y + 0.008, -0.034, 1.66),
            (-0.119, TEAR_SEAM_Y + 0.001, -0.022, 1.98),
        ),
    ),
    Pose(
        "Pose_ContinuousRise",
        1.00,
        0,
        0.072,
        0.40,
        (-0.006, 0.009, -0.017),
        (
            (-0.086, TEAR_SEAM_Y - 0.001, -0.020, 0.18),
            (-0.096, TEAR_SEAM_Y + 0.005, -0.034, 0.64),
            (-0.106, TEAR_SEAM_Y + 0.010, -0.041, 1.10),
            (-0.114, TEAR_SEAM_Y + 0.006, -0.031, 1.48),
            (-0.119, TEAR_SEAM_Y, -0.021, 1.78),
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--fbx", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--preview-closed", required=True)
    parser.add_argument("--preview-mouth", required=True)
    parser.add_argument("--preview-rise", required=True)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def smooth01(value: float) -> float:
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def guide_x(index: int) -> float:
    return GUIDE_X[index] * CANVAS_WIDTH * 0.5


def tear_front_index(pose: Pose) -> int:
    """Map the authored seam index to the screen-right pull origin."""
    return len(GUIDE_X) - 1 - pose.tear_start


def local_open(pose: Pose | None, index: int) -> float:
    if pose is None:
        return 0.0
    front = tear_front_index(pose)
    if index > front:
        return 0.0
    span = max(1, front)
    distance = (front - index) / span
    irregular = 1.0 + smoothed_irregularity(index) * 0.08
    return clamp01((0.25 + 0.75 * smooth01(distance)) * irregular)


def opened_surface_factor(opening: float) -> float:
    """Collapse every opened station into the separate fine torn lip."""
    return smooth01(opening * 4.0)


def smoothed_irregularity(index: int) -> float:
    previous = IRREGULARITY[max(0, index - 1)]
    current = IRREGULARITY[index]
    following = IRREGULARITY[min(len(IRREGULARITY) - 1, index + 1)]
    return previous * 0.18 + current * 0.64 + following * 0.18


def front_drop(pose: Pose | None, index: int) -> float:
    if pose is None:
        return 0.0
    return pose.max_front_drop * local_open(pose, index)


def front_edge(pose: Pose | None, index: int) -> Vector:
    opening = local_open(pose, index)
    return Vector(
        (
            guide_x(index),
            TEAR_SEAM_Y - front_drop(pose, index),
            FRONT_Z - opening * 0.0025,
        )
    )


def rear_edge(pose: Pose | None, index: int) -> Vector:
    opening = local_open(pose, index)
    lag = pose.inner_lag if pose else 0.0
    return Vector(
        (
            guide_x(index),
            TEAR_SEAM_Y - front_drop(pose, index) * lag,
            BACK_Z + opening * 0.002,
        )
    )


def create_material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    image: Path | None = None,
) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    nodes = result.node_tree.nodes
    links = result.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Alpha"].default_value = color[3]
    if image:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = bpy.data.images.load(str(image), check_existing=True)
        texture.interpolation = "Linear"
        links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
        result.surface_render_method = "DITHERED"
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return result


def grid_faces(columns: int, rows: int) -> list[tuple[int, int, int, int]]:
    return [
        (
            column * (rows + 1) + row,
            column * (rows + 1) + row + 1,
            (column + 1) * (rows + 1) + row + 1,
            (column + 1) * (rows + 1) + row,
        )
        for column in range(columns)
        for row in range(rows)
    ]


def create_mesh(
    name: str,
    vertices: list[Vector],
    faces: list[tuple[int, ...]],
    material_indices: list[int],
    uv_sets: dict[str, list[tuple[float, float]]],
    materials: list[bpy.types.Material],
    pose_vertices,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    for item in materials:
        mesh.materials.append(item)
    mesh.update()
    for name_, coordinates in uv_sets.items():
        if len(coordinates) != len(vertices):
            raise ValueError(f"{name_} UV count does not match {name}.")
        layer = mesh.uv_layers.new(name=name_)
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex_index = mesh.loops[loop_index].vertex_index
                layer.data[loop_index].uv = coordinates[vertex_index]
    for polygon in mesh.polygons:
        polygon.material_index = material_indices[polygon.index]
    result = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(result)
    basis = result.shape_key_add(name="Basis", from_mix=False)
    basis.interpolation = "KEY_LINEAR"
    for pose in POSES:
        key = result.shape_key_add(name=pose.key, from_mix=False)
        key.interpolation = "KEY_LINEAR"
        for index, point in enumerate(pose_vertices(pose)):
            key.data[index].co = point
    result["representation"] = "seven-authored-relative-foil-poses"
    result["pose_keys"] = [pose.key for pose in POSES]
    return result


def front_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    artwork_uvs: list[tuple[float, float]] = []
    contour_uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        x = guide_x(column)
        physical_u = column / (len(GUIDE_X) - 1)
        artwork_u = 1.0 - physical_u
        for row in range(BODY_ROWS + 1):
            t = row / BODY_ROWS
            v = ART_V_BOTTOM + t * (ART_V_TOP - ART_V_BOTTOM)
            pillow = -0.0045 * math.sin(t * math.pi) * (
                1.0 - (2.0 * physical_u - 1.0) ** 2
            )
            vertices.append(
                Vector(
                    (
                        x,
                        PACK_BOTTOM_Y + (PRINTED_TOP_Y - PACK_BOTTOM_Y) * t,
                        FRONT_Z + pillow,
                    )
                )
            )
            artwork_uvs.append((artwork_u, v))
            contour_uvs.append((1.0 - t, physical_u))
    return vertices, {"UVMap": artwork_uvs, "TearContour": contour_uvs}


def front_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        edge = front_edge(pose, column)
        physical_u = column / (len(GUIDE_X) - 1)
        for row in range(BODY_ROWS + 1):
            t = row / BODY_ROWS
            pillow = -0.0045 * math.sin(t * math.pi) * (
                1.0 - (2.0 * physical_u - 1.0) ** 2
            )
            vertices.append(
                Vector(
                    (
                        edge.x,
                        PACK_BOTTOM_Y + (edge.y - PACK_BOTTOM_Y) * t,
                        FRONT_Z + pillow - local_open(pose, column) * t**4 * 0.002,
                    )
                )
            )
    return vertices


def back_vertex_index(column: int, layer: int, row: int) -> int:
    return column * 6 + layer * 3 + row


def back_faces() -> list[tuple[int, int, int, int]]:
    faces: list[tuple[int, int, int, int]] = []
    last_column = len(GUIDE_X) - 1
    for column in range(last_column):
        next_column = column + 1
        for row in range(2):
            faces.extend(
                (
                    (
                        back_vertex_index(column, 0, row),
                        back_vertex_index(next_column, 0, row),
                        back_vertex_index(next_column, 0, row + 1),
                        back_vertex_index(column, 0, row + 1),
                    ),
                    (
                        back_vertex_index(column, 1, row + 1),
                        back_vertex_index(next_column, 1, row + 1),
                        back_vertex_index(next_column, 1, row),
                        back_vertex_index(column, 1, row),
                    ),
                )
            )
        for row in (0, 2):
            faces.append(
                (
                    back_vertex_index(column, 0, row),
                    back_vertex_index(column, 1, row),
                    back_vertex_index(next_column, 1, row),
                    back_vertex_index(next_column, 0, row),
                )
            )
    for column in (0, last_column):
        for row in range(2):
            faces.append(
                (
                    back_vertex_index(column, 0, row),
                    back_vertex_index(column, 0, row + 1),
                    back_vertex_index(column, 1, row + 1),
                    back_vertex_index(column, 1, row),
                )
            )
    return faces


def back_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        x = guide_x(column)
        u = column / (len(GUIDE_X) - 1)
        for layer in range(2):
            for row in range(3):
                t = row * 0.5
                vertices.append(
                    Vector(
                        (
                            x,
                            TEAR_SEAM_Y - CAVITY_HEIGHT + t * CAVITY_HEIGHT,
                            BACK_Z + layer * CAVITY_BACK_THICKNESS,
                        )
                    )
                )
                uvs.append((u, t))
    return vertices, {"UVMap": uvs}


def back_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        front = front_edge(pose, column)
        rear = rear_edge(pose, column)
        opening = local_open(pose, column)
        factor = opened_surface_factor(opening)
        collapsed = front + Vector((0.0, -0.0007, 0.006))
        targets = (
            rear + Vector((0.0, -CAVITY_HEIGHT - opening * 0.004, 0.0)),
            rear + Vector((0.0, -0.012 - opening * 0.002, 0.0018)),
            rear + Vector((0.0, -0.0012, 0.0)),
        )
        for layer in range(2):
            for target in targets:
                near = collapsed + (target - collapsed) * factor
                vertices.append(
                    near + Vector((0.0, 0.0, layer * CAVITY_BACK_THICKNESS * factor))
                )
    return vertices


def seal_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        vertices.extend(
            (
                Vector((x, CRIMP_BASE_Y, FRONT_Z - 0.0005)),
                Vector((x, PACK_TOP_Y, FRONT_Z - 0.0005)),
            )
        )
        uvs.extend(((u, 0.765), (u, 0.925)))
    return vertices, {"UVMap": uvs}


def seal_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        edge = front_edge(pose, column)
        opening = local_open(pose, column)
        base = edge + Vector((0.0, CRIMP_CLEARANCE, -0.0005))
        retained = 1.0 - opened_surface_factor(opening)
        height = TOP_SEAL_HEIGHT * retained
        vertices.extend(
            (
                base,
                base + Vector((0.0, height, 0.0)),
            )
        )
    return vertices


def mouth_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        for row in range(3):
            vertices.append(Vector((guide_x(column), TEAR_SEAM_Y, FRONT_Z)))
            uvs.append((u, row * 0.5))
    return vertices, {"UVMap": uvs}


def mouth_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        front = front_edge(pose, column)
        opening = local_open(pose, column)
        factor = opened_surface_factor(opening)
        collapsed = front + Vector((0.0, -0.0007, 0.0035))
        targets = (
            front + Vector((0.0, -0.0009, 0.0045)),
            front + Vector((0.0, -0.0058, 0.027)),
            front + Vector((0.0, -0.0102, 0.050)),
        )
        vertices.extend(
            collapsed + (target - collapsed) * factor for target in targets
        )
    return vertices


def back_rim_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        vertices.extend(
            (
                Vector((guide_x(column), TEAR_SEAM_Y, BACK_Z)),
                Vector((guide_x(column), TEAR_SEAM_Y + 0.004, BACK_Z)),
            )
        )
        uvs.extend(((u, 0.0), (u, 1.0)))
    return vertices, {"UVMap": uvs}


def back_rim_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        front = front_edge(pose, column)
        rear = rear_edge(pose, column)
        opening = local_open(pose, column)
        factor = opened_surface_factor(opening)
        center = front + (rear - front) * factor
        width = (0.0012 + opening * 0.0012) * factor
        vertices.extend(
            (
                center + Vector((0.0, -width, 0.0)),
                center + Vector((0.0, width, 0.0)),
            )
        )
    return vertices


def lip_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        for side in range(LIP_SIDES):
            vertices.append(Vector((guide_x(column), TEAR_SEAM_Y, FRONT_Z)))
            uvs.append((u, side / LIP_SIDES))
    return vertices, {"UVMap": uvs}


def lip_faces() -> list[tuple[int, int, int, int]]:
    faces: list[tuple[int, int, int, int]] = []
    for column in range(len(GUIDE_X) - 1):
        for side in range(LIP_SIDES):
            next_side = (side + 1) % LIP_SIDES
            a = column * LIP_SIDES + side
            b = column * LIP_SIDES + next_side
            c = (column + 1) * LIP_SIDES + next_side
            d = (column + 1) * LIP_SIDES + side
            faces.append((a, b, c, d))
    return faces


def lip_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        edge = front_edge(pose, column)
        opening = local_open(pose, column)
        center = edge + Vector((0.0, -0.00055 - opening * 0.0008, 0.0))
        radius = 0.00035 + opening * 0.00135
        for side in range(LIP_SIDES):
            angle = side / LIP_SIDES * math.tau
            vertices.append(
                center
                + Vector((0.0, math.sin(angle) * radius, -math.cos(angle) * radius))
            )
    return vertices


def contour_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        vertices.extend(
            (
                Vector((guide_x(column), TEAR_SEAM_Y, FRONT_Z - 0.0016)),
                Vector((guide_x(column), TEAR_SEAM_Y + 0.0001, FRONT_Z - 0.0016)),
            )
        )
        uvs.extend(((u, 0.0), (u, 1.0)))
    return vertices, {"UVMap": uvs}


def contour_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        edge = front_edge(pose, column)
        opening = local_open(pose, column)
        width = 0.00018 + opening * 0.00065
        vertices.extend((edge + Vector((0.0, -width, -0.0016)), edge + Vector((0.0, width, -0.0016))))
    return vertices


SIDEWALL_FACES = (
    (0, 1, 3, 2),
    (4, 6, 7, 5),
    (0, 4, 5, 1),
    (2, 3, 7, 6),
    (0, 2, 6, 4),
    (1, 5, 7, 3),
)


def sidewall_template() -> tuple[list[Vector], dict[str, list[tuple[float, float]]]]:
    return [Vector((0.0, TEAR_SEAM_Y, FRONT_Z)) for _ in range(8)], {
        "UVMap": [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)] * 2
    }


def sidewall_state(pose: Pose, leading: bool) -> list[Vector]:
    index = tear_front_index(pose) if leading else 0
    front = front_edge(pose, index)
    rear = rear_edge(pose, index)
    opening = local_open(pose, index)
    half_width = 0.0004 + opening * 0.0015
    lower_front = front - Vector((0.0, 0.003 + opening * 0.002, 0.0))
    lower_rear = rear - Vector((0.0, 0.002 + opening * 0.0015, 0.0))
    return [
        lower_front + Vector((-half_width, 0.0, 0.0)),
        lower_front + Vector((half_width, 0.0, 0.0)),
        front + Vector((-half_width, 0.0, 0.0)),
        front + Vector((half_width, 0.0, 0.0)),
        lower_rear + Vector((-half_width, 0.0, 0.0)),
        lower_rear + Vector((half_width, 0.0, 0.0)),
        rear + Vector((-half_width, 0.0, 0.0)),
        rear + Vector((half_width, 0.0, 0.0)),
    ]


def strip_template() -> tuple[
    list[Vector], list[tuple[int, ...]], list[int], dict[str, list[tuple[float, float]]]
]:
    sections = len(POSES[0].strip_spine)
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for section in range(sections):
        for _ in range(4):
            vertices.append(Vector((-0.086, TEAR_SEAM_Y, FRONT_Z)))
        u = section / max(1, sections - 1)
        uvs.extend(((u, 0.765), (u, 0.925), (u, 0.765), (u, 0.925)))
    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    for section in range(sections - 1):
        a = section * 4
        b = (section + 1) * 4
        faces.extend(((a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2)))
        material_indices.extend((0, 1))
        faces.extend(((a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)))
        material_indices.extend((2, 2))
    return vertices, faces, material_indices, {"UVMap": uvs}


def strip_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for x, y, z, roll in pose.strip_spine:
        cross = Vector((0.0, math.cos(roll) * STRIP_HALF_WIDTH, math.sin(roll) * STRIP_HALF_WIDTH))
        normal = Vector((0.0, -math.sin(roll), math.cos(roll))) * (FOIL_THICKNESS * 0.5)
        center = Vector((x, y, z))
        vertices.extend((center - cross - normal, center + cross - normal, center - cross + normal, center + cross + normal))
    return vertices


def tab_template() -> tuple[
    list[Vector], list[tuple[int, ...]], list[int], dict[str, list[tuple[float, float]]]
]:
    front = [
        Vector((-0.086, TEAR_SEAM_Y + 0.002, FRONT_Z - 0.002)),
        Vector((-0.116, TEAR_SEAM_Y + 0.002, FRONT_Z - 0.002)),
        Vector((-0.116, TEAR_SEAM_Y + 0.011, FRONT_Z - 0.002)),
        Vector((-0.107, TEAR_SEAM_Y + 0.016, FRONT_Z - 0.002)),
        Vector((-0.090, TEAR_SEAM_Y + 0.006, FRONT_Z - 0.002)),
    ]
    vertices = front + [point + Vector((0.0, 0.0, FOIL_THICKNESS)) for point in front]
    faces: list[tuple[int, ...]] = [(0, 1, 2, 4), (4, 2, 3), (9, 7, 6, 5), (9, 8, 7)]
    material_indices = [0, 0, 1, 1]
    for index in range(5):
        next_index = (index + 1) % 5
        faces.append((index, 5 + index, 5 + next_index, next_index))
        material_indices.append(2)
    return vertices, faces, material_indices, {"UVMap": [(0, 0), (1, 0), (1, 1), (0.5, 1), (0, 1)] * 2}


def tab_state(pose: Pose) -> list[Vector]:
    basis, _, _, _ = tab_template()
    dx, dy, dz = pose.tab_lift
    pivot = basis[0]
    return [
        pivot
        + Vector(
            (
                (point - pivot).x + dx,
                (point - pivot).y + dy * (0.65 + max(0.0, (point - pivot).y) * 18.0),
                (point - pivot).z + dz * (0.65 + max(0.0, (point - pivot).y) * 18.0),
            )
        )
        for point in basis
    ]


def set_pose(objects: list[bpy.types.Object], pose: Pose | None) -> None:
    for object_ in objects:
        keys = object_.data.shape_keys.key_blocks
        for key in keys:
            if key.name != "Basis":
                key.value = 1.0 if pose and key.name == pose.key else 0.0
        object_.hide_render = False
    if pose is None:
        for name in (
            "Pack_RearInnerFoil",
            "Pack_InnerFoilMouth",
            "Pack_InnerBackFoilRim",
            "Pack_RolledCrimpLip",
            "Pack_TornContourSweepCarrier",
            "Pack_TearFrontSidewall",
            "Pack_TabSidewall",
            "Pack_ReleasedSealStrip",
            "Pack_TopRightPullTab",
        ):
            bpy.data.objects[name].hide_render = True
    elif pose.key == "Pose_TabCatch":
        bpy.data.objects["Pack_ReleasedSealStrip"].hide_render = True
    bpy.context.view_layer.update()


def create_camera_and_lights() -> None:
    bpy.context.scene.world.color = (0.010, 0.012, 0.014)
    camera_data = bpy.data.cameras.new("R020_PackOnlyReviewCamera")
    camera = bpy.data.objects.new("R020_PackOnlyReviewCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, -0.010, -1.12)
    camera.data.lens = 70.0
    camera.rotation_euler = (Vector((0.0, -0.010, 0.030)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera
    for name, location, energy, color, size in (
        ("R020_Key", (-0.26, 0.24, -0.42), 68.0, (1.0, 0.90, 0.78), 1.1),
        ("R020_Fill", (0.26, 0.04, -0.26), 24.0, (0.70, 0.75, 0.80), 1.0),
        ("R020_Rim", (0.04, 0.18, 0.30), 34.0, (0.98, 0.85, 0.66), 0.7),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (Vector((0.0, -0.010, 0.020)) - light.location).to_track_quat("-Z", "Y").to_euler()


def render(path: Path, objects: list[bpy.types.Object], pose: Pose | None) -> None:
    set_pose(objects, pose)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for material_ in list(bpy.data.materials):
        bpy.data.materials.remove(material_)


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    blend_path = Path(args.blend).resolve()
    fbx_path = Path(args.fbx).resolve()
    report_path = Path(args.report).resolve()
    previews = (
        Path(args.preview_closed).resolve(),
        Path(args.preview_mouth).resolve(),
        Path(args.preview_rise).resolve(),
    )
    for path in (blend_path, fbx_path, report_path, *previews):
        path.parent.mkdir(parents=True, exist_ok=True)

    body_path = project_root / "Assets/Source/Pack/gacha-pack-standard-body.png"
    flap_path = project_root / "Assets/Source/Pack/gacha-pack-standard-flap.png"
    if not body_path.is_file() or not flap_path.is_file():
        raise RuntimeError("The authored 384x512 Pack artwork is missing.")

    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.look = "AgX - Medium High Contrast"

    front_material = create_material("MI_R020_ActualPackArtwork", (0.70, 0.70, 0.68, 1.0), 0.22, 0.48, body_path)
    crimp_material = create_material("MI_R020_ActualTopCrimp", (0.58, 0.57, 0.54, 1.0), 0.30, 0.44, flap_path)
    inner_material = create_material("MI_R020_InnerReflectiveFoil", (0.38, 0.40, 0.42, 1.0), 0.76, 0.38)
    back_material = create_material("MI_R020_RecessedCavity", (0.023, 0.027, 0.032, 1.0), 0.05, 0.78)
    lip_material = create_material("MI_R020_CrimpLip", (0.16, 0.13, 0.095, 1.0), 0.34, 0.44)
    strip_front = create_material("MI_R020_ReleasedSealFront", (0.42, 0.38, 0.31, 1.0), 0.20, 0.54, flap_path)
    strip_under = create_material("MI_R020_ReleasedSealUnderside", (0.016, 0.014, 0.012, 1.0), 0.10, 0.68)
    cut_edge = create_material("MI_R020_FibrousTornEdge", (0.22, 0.16, 0.10, 1.0), 0.10, 0.77)
    contour_material = create_material("MI_R020_ContourCarrier", (0.30, 0.23, 0.15, 1.0), 0.12, 0.62)

    front_vertices, front_uvs = front_template()
    front = create_mesh("Pack_FrontPrintedFoil", front_vertices, grid_faces(len(GUIDE_X) - 1, BODY_ROWS), [0] * ((len(GUIDE_X) - 1) * BODY_ROWS), front_uvs, [front_material], front_state)
    if not all(polygon.normal.z < -0.95 for polygon in front.data.polygons):
        raise RuntimeError("Front rows must retain camera-facing negative-Z winding.")
    back_vertices, back_uvs = back_template()
    back_faces_ = back_faces()
    back = create_mesh("Pack_RearInnerFoil", back_vertices, back_faces_, [0] * len(back_faces_), back_uvs, [back_material], back_state)
    seal_vertices, seal_uvs = seal_template()
    seal = create_mesh("Pack_TopSealRemaining", seal_vertices, grid_faces(len(GUIDE_X) - 1, 1), [0] * (len(GUIDE_X) - 1), seal_uvs, [crimp_material], seal_state)
    mouth_vertices, mouth_uvs = mouth_template()
    mouth = create_mesh("Pack_InnerFoilMouth", mouth_vertices, grid_faces(len(GUIDE_X) - 1, 2), [0] * ((len(GUIDE_X) - 1) * 2), mouth_uvs, [inner_material], mouth_state)
    back_rim_vertices, back_rim_uvs = back_rim_template()
    back_rim = create_mesh("Pack_InnerBackFoilRim", back_rim_vertices, grid_faces(len(GUIDE_X) - 1, 1), [0] * (len(GUIDE_X) - 1), back_rim_uvs, [inner_material], back_rim_state)
    lip_vertices, lip_uvs = lip_template()
    lip = create_mesh("Pack_RolledCrimpLip", lip_vertices, lip_faces(), [0] * len(lip_faces()), lip_uvs, [lip_material], lip_state)
    contour_vertices, contour_uvs = contour_template()
    contour = create_mesh("Pack_TornContourSweepCarrier", contour_vertices, grid_faces(len(GUIDE_X) - 1, 1), [0] * (len(GUIDE_X) - 1), contour_uvs, [contour_material], contour_state)
    side_vertices, side_uvs = sidewall_template()
    leading = create_mesh("Pack_TearFrontSidewall", side_vertices, list(SIDEWALL_FACES), [0] * len(SIDEWALL_FACES), side_uvs, [inner_material], lambda pose: sidewall_state(pose, True))
    tab_wall = create_mesh("Pack_TabSidewall", side_vertices, list(SIDEWALL_FACES), [0] * len(SIDEWALL_FACES), side_uvs, [inner_material], lambda pose: sidewall_state(pose, False))
    strip_vertices, strip_faces, strip_indices, strip_uvs = strip_template()
    strip = create_mesh("Pack_ReleasedSealStrip", strip_vertices, strip_faces, strip_indices, strip_uvs, [strip_front, strip_under, cut_edge], strip_state)
    tab_vertices, tab_faces, tab_indices, tab_uvs = tab_template()
    pull_tab = create_mesh("Pack_TopRightPullTab", tab_vertices, tab_faces, tab_indices, tab_uvs, [strip_front, strip_under, cut_edge], tab_state)

    rig = bpy.data.objects.new("PackOpeningGate04R020_PACK_ONLY_RIG", None)
    bpy.context.collection.objects.link(rig)
    rig.empty_display_type = "SINGLE_ARROW"
    rig["representation"] = "seven-authored-pack-only-foil-pouch-poses"
    rig["actual_pack_canvas"] = "384x512"
    rig["unity_root_rotation_euler"] = [0.0, 0.0, 0.0]
    rig["case_geometry_included"] = False
    rig["case_rendered_or_baked"] = False
    front["physical_y_bottom"] = PACK_BOTTOM_Y
    front["printed_y_top"] = PRINTED_TOP_Y
    front["outer_pack_top_y"] = PACK_TOP_Y
    front["top_crimp_base_y"] = CRIMP_BASE_Y
    front["tear_seam_y"] = TEAR_SEAM_Y
    front["tear_origin_physical_u"] = 0.0
    front["tear_origin_unity_screen"] = "right"
    front["front_rows"] = "bottom-to-top"
    front["front_winding"] = "negative-z-camera-facing"
    front["front_u_mapping"] = (
        "physical-left-to-right maps to source-u 1-to-0 to correct "
        "the observed Unity FBX horizontal mirror"
    )
    seal["opened_side"] = "physical-u-0-to-tear-front; Unity screen-right"
    seal["opened_surface_behavior"] = "collapsed into separate fine torn lip"
    back["finite_back_wall_thickness_meters"] = CAVITY_BACK_THICKNESS
    objects = [front, back, seal, mouth, back_rim, lip, contour, leading, tab_wall, strip, pull_tab]
    roles = {
        "Pack_FrontPrintedFoil": "outer printed foil carrying unmodified 384x512 Pack art",
        "Pack_RearInnerFoil": "finite-depth matte-charcoal cavity back wall behind the live case and liner",
        "Pack_TopSealRemaining": "UV-clipped attached crimp retained only ahead of the right-to-left tear front",
        "Pack_InnerFoilMouth": "short collapsed-outside-opening silver-gray inner liner",
        "Pack_InnerBackFoilRim": "rear foil rim behind the contained case",
        "Pack_RolledCrimpLip": "fine irregular torn front lip",
        "Pack_TornContourSweepCarrier": "local warm-neutral CC0 sweep carrier",
        "Pack_TearFrontSidewall": "moving lateral tear-front cavity wall",
        "Pack_TabSidewall": "fixed upper-right cavity wall",
        "Pack_ReleasedSealStrip": "short two-sided curled foil strip rooted at rendered top-right",
        "Pack_TopRightPullTab": "small rendered top-right tab only",
    }
    for object_ in objects:
        object_.parent = rig
        object_["pack_only"] = True
        object_["artwork_aspect"] = "384x512"
        object_["role"] = roles[object_.name]

    create_camera_and_lights()
    render(previews[0], objects, None)
    render(previews[1], objects, POSES[3])
    render(previews[2], objects, POSES[5])
    set_pose(objects, None)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    for object_ in objects:
        object_.select_set(True)
    bpy.ops.export_scene.fbx(
        filepath=str(fbx_path),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        use_mesh_modifiers=False,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="RELATIVE",
        apply_scale_options="FBX_SCALE_ALL",
    )

    report = {
        "schema": "premium-display-case-gate04-r020-pack-only-rig.v1",
        "producer": {"blender": bpy.app.version_string, "route": "deterministic-bpy"},
        "representation": "seven hand-authored Pack-only foil-pouch FBX relative blend-shape poses",
        "actualPackArtwork": {
            "bodyPath": "Assets/Source/Pack/gacha-pack-standard-body.png",
            "bodySha256": sha256(body_path),
            "flapPath": "Assets/Source/Pack/gacha-pack-standard-flap.png",
            "flapSha256": sha256(flap_path),
            "canvas": [384, 512],
            "canvasAspect": 384 / 512,
            "visualArtworkUvWindow": [0.0, ART_V_BOTTOM, 1.0, ART_V_TOP],
            "aspectTreatment": "transparent canvas margins omitted without resampling; sampled printed pixels retain authored aspect",
        },
        "physicalCoordinates": {
            "packBottomY": PACK_BOTTOM_Y,
            "printedTopY": PRINTED_TOP_Y,
            "packTopY": PACK_TOP_Y,
            "topCrimpBaseY": CRIMP_BASE_Y,
            "tearSeamY": TEAR_SEAM_Y,
            "frontOpensTowardNegativeY": True,
        },
        "frontOrientation": {
            "rows": "bottom-to-top",
            "basisNormalZ": sum(polygon.normal.z for polygon in front.data.polygons)
            / len(front.data.polygons),
            "physicalUToSourceU": "1-to-0",
        },
        "attachedCrimpHeightFraction": TOP_SEAL_HEIGHT / abs(PACK_TOP_Y - PACK_BOTTOM_Y),
        "releasedSealStripHeightFraction": (STRIP_HALF_WIDTH * 2.0)
        / abs(PACK_TOP_Y - PACK_BOTTOM_Y),
        "recessedCavityHeightMeters": CAVITY_HEIGHT,
        "recessedCavityBackThicknessMeters": CAVITY_BACK_THICKNESS,
        "mouthDepthMeters": MOUTH_DEPTH,
        "foilThicknessMeters": FOIL_THICKNESS,
        "authoredGuideStations": len(GUIDE_X),
        "tearFront": {
            "input": "continuous normalized physical-u front",
            "originPhysicalU": 0.0,
            "originUnityScreen": "right",
            "openedSide": "physical-u less than or equal to tear front",
        },
        "unityRootRotationEuler": [0.0, 0.0, 0.0],
        "caseGeometryIncluded": False,
        "caseRenderedOrBaked": False,
        "poses": [
            {
                "key": "Basis" if pose is None else pose.key,
                "progress": 0.0 if pose is None else pose.progress,
                "description": description,
            }
            for pose, description in (
                (None, "sealed foil pouch; front and rear meet at an attached crimp seam"),
                (POSES[0], "small upper-right tab catch and local compression"),
                (POSES[1], "outer printed foil peels first while inner liner lags"),
                (POSES[2], "narrow lateral tear front advances across the seam"),
                (POSES[3], "formed physical mouth with a fine lip and sidewalls"),
                (POSES[4], "deep mouth holds one live case behind the front lip"),
                (POSES[5], "same mouth permits vertical case extraction"),
            )
        ],
        "objects": [
            {
                "name": object_.name,
                "vertices": len(object_.data.vertices),
                "polygons": len(object_.data.polygons),
                "blendShapeCount": len(object_.data.shape_keys.key_blocks) - 1,
                "role": object_.get("role"),
            }
            for object_ in objects
        ],
        "blend": str(blend_path),
        "blendSha256": sha256(blend_path),
        "fbx": str(fbx_path),
        "fbxSha256": sha256(fbx_path),
        "previews": [str(path) for path in previews],
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
