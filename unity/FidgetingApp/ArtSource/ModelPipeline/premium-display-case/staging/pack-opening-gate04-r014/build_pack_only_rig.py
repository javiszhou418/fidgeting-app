#!/usr/bin/env python3
"""Build the R014 Pack-only tear rig from seven authored foil poses."""

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


PACK_WIDTH = 0.255
PACK_HEIGHT = 0.340
PACK_HALF_WIDTH = PACK_WIDTH * 0.5
PACK_BOTTOM = -PACK_HEIGHT * 0.5
PACK_TOP = PACK_HEIGHT * 0.5 - 0.013
TOP_CRIMP_HEIGHT = 0.022
FOIL_THICKNESS = 0.00075
MOUTH_DEPTH = 0.070
BODY_ROWS = 9
MOUTH_ROWS = 4
LIP_SIDES = 6
STRIP_HALF_WIDTH = 0.0105
STRIP_SECTIONS = 6

# These stations and per-pose drop values are intentionally authored rather
# than synthesized. Their uneven progression prevents a symmetric scallop.
GUIDE_X = (
    -1.00, -0.90, -0.80, -0.70, -0.60, -0.50, -0.40, -0.30, -0.20, -0.10,
    0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00,
)


@dataclass(frozen=True)
class Pose:
    key: str
    progress: float
    drops: tuple[float, ...]
    tear_start: int
    tab_lift: tuple[float, float, float]
    strip_spine: tuple[tuple[float, float, float, float], ...]


def strip_points(*points: tuple[float, float, float, float]) -> tuple[
    tuple[float, float, float, float], ...
]:
    if len(points) != STRIP_SECTIONS:
        raise ValueError("Each authored strip pose needs six spine stations.")
    return points


POSES = (
    Pose(
        "Pose_TabCatch",
        0.12,
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.001),
        20,
        (0.001, 0.005, -0.006),
        strip_points(
            (0.086, PACK_TOP, -0.007, 0.00), (0.094, PACK_TOP, -0.007, 0.04),
            (0.102, PACK_TOP, -0.008, 0.08), (0.110, PACK_TOP, -0.009, 0.12),
            (0.118, PACK_TOP + 0.001, -0.010, 0.18), (0.125, PACK_TOP + 0.002, -0.011, 0.24),
        ),
    ),
    Pose(
        "Pose_NarrowPeel",
        0.28,
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.001, 0.004, 0.007, 0.009, 0.006),
        16,
        (0.004, 0.010, -0.018),
        strip_points(
            (0.074, PACK_TOP - 0.001, -0.010, 0.00), (0.084, PACK_TOP + 0.001, -0.013, 0.18),
            (0.094, PACK_TOP + 0.005, -0.018, 0.52), (0.105, PACK_TOP + 0.007, -0.021, 0.94),
            (0.116, PACK_TOP + 0.004, -0.017, 1.36), (0.125, PACK_TOP + 0.001, -0.013, 1.76),
        ),
    ),
    Pose(
        "Pose_TearAdvance",
        0.48,
        (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.002, 0.005, 0.010, 0.014, 0.019, 0.022, 0.021, 0.025, 0.024, 0.028, 0.027),
        10,
        (0.007, 0.012, -0.024),
        strip_points(
            (0.043, PACK_TOP - 0.002, -0.011, 0.00), (0.057, PACK_TOP + 0.002, -0.015, 0.24),
            (0.071, PACK_TOP + 0.008, -0.022, 0.64), (0.086, PACK_TOP + 0.011, -0.025, 1.08),
            (0.104, PACK_TOP + 0.006, -0.019, 1.54), (0.122, PACK_TOP + 0.001, -0.013, 1.96),
        ),
    ),
    Pose(
        "Pose_FormedMouth",
        0.68,
        (0, 0, 0, 0, 0, 0, 0, 0.002, 0.005, 0.011, 0.017, 0.023, 0.025, 0.028, 0.031, 0.033, 0.036, 0.038, 0.040, 0.043, 0.044),
        7,
        (0.008, 0.014, -0.026),
        strip_points(
            (0.038, PACK_TOP - 0.003, -0.011, 0.00), (0.054, PACK_TOP + 0.002, -0.016, 0.28),
            (0.070, PACK_TOP + 0.010, -0.024, 0.76), (0.086, PACK_TOP + 0.012, -0.026, 1.24),
            (0.105, PACK_TOP + 0.006, -0.019, 1.70), (0.123, PACK_TOP, -0.013, 2.08),
        ),
    ),
    Pose(
        "Pose_CaseContained",
        0.84,
        (0, 0, 0, 0.002, 0.005, 0.010, 0.014, 0.018, 0.021, 0.024, 0.027, 0.029, 0.032, 0.034, 0.037, 0.039, 0.042, 0.044, 0.047, 0.049, 0.052),
        3,
        (0.009, 0.015, -0.028),
        strip_points(
            (0.036, PACK_TOP - 0.004, -0.012, 0.00), (0.052, PACK_TOP + 0.002, -0.017, 0.34),
            (0.069, PACK_TOP + 0.010, -0.025, 0.86), (0.087, PACK_TOP + 0.013, -0.028, 1.38),
            (0.106, PACK_TOP + 0.006, -0.019, 1.88), (0.123, PACK_TOP - 0.001, -0.013, 2.22),
        ),
    ),
    Pose(
        "Pose_ContinuousRise",
        1.00,
        (0.012, 0.013, 0.014, 0.016, 0.017, 0.019, 0.020, 0.022, 0.023, 0.025, 0.026, 0.028, 0.029, 0.031, 0.032, 0.034, 0.035, 0.037, 0.038, 0.040, 0.041),
        0,
        (0.010, 0.013, -0.024),
        strip_points(
            (0.048, PACK_TOP - 0.005, -0.012, 0.00), (0.062, PACK_TOP + 0.001, -0.017, 0.32),
            (0.077, PACK_TOP + 0.008, -0.024, 0.82), (0.092, PACK_TOP + 0.009, -0.025, 1.28),
            (0.108, PACK_TOP + 0.004, -0.018, 1.72), (0.122, PACK_TOP - 0.002, -0.013, 2.08),
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


def guide_x(index: int) -> float:
    return GUIDE_X[index] * PACK_HALF_WIDTH


def pose_open(pose: Pose, index: int) -> float:
    return clamp01(pose.drops[index] / 0.042)


def front_edge(pose: Pose, index: int) -> tuple[float, float, float]:
    return guide_x(index), PACK_TOP - pose.drops[index], -0.009


def interior_back(pose: Pose, index: int) -> tuple[float, float, float]:
    openness = pose_open(pose, index)
    _, front_y, _ = front_edge(pose, index)
    return (
        guide_x(index),
        PACK_TOP + 0.0035 + openness * 0.004,
        -0.009 + openness * MOUTH_DEPTH,
    )


def material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    image: Path | None = None,
) -> bpy.types.Material:
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    result.diffuse_color = color
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
    face_materials: list[int],
    uvs: list[tuple[float, float]],
    materials: list[bpy.types.Material],
    pose_vertices,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    for item in materials:
        mesh.materials.append(item)
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        polygon.material_index = face_materials[polygon.index]
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = uvs[vertex_index]

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


def front_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = 1.0 - column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        for row in range(BODY_ROWS + 1):
            v = row / BODY_ROWS
            y = PACK_BOTTOM + (PACK_TOP - PACK_BOTTOM) * v
            pillow = -0.0055 * math.sin(u * math.pi) * math.sin(v * math.pi)
            vertices.append(Vector((x, y, -0.009 + pillow)))
            uvs.append((u, v))
    return vertices, uvs


def front_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        _, edge_y, _ = front_edge(pose, column)
        for row in range(BODY_ROWS + 1):
            v = row / BODY_ROWS
            y = PACK_BOTTOM + (edge_y - PACK_BOTTOM) * v
            pillow = -0.0055 * math.sin(u * math.pi) * math.sin(v * math.pi)
            z = -0.009 + pillow - pose_open(pose, column) * v**4 * 0.003
            vertices.append(Vector((x, y, z)))
    return vertices


def crimp_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = 1.0 - column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        for row in range(2):
            vertices.append(Vector((x, PACK_TOP + TOP_CRIMP_HEIGHT * row, -0.010)))
            uvs.append((u, 0.84 + row * 0.14))
    return vertices, uvs


def crimp_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        x, edge_y, _ = front_edge(pose, column)
        openness = pose_open(pose, column)
        for row in range(2):
            vertices.append(
                Vector((
                    x,
                    edge_y + row * TOP_CRIMP_HEIGHT * (1.0 - openness),
                    -0.010 - openness * 0.001,
                ))
            )
    return vertices


def mouth_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        for row in range(MOUTH_ROWS + 1):
            vertices.append(Vector((x, PACK_TOP, -0.009)))
            uvs.append((u, row / MOUTH_ROWS))
    return vertices, uvs


def mouth_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        x, front_y, front_z = front_edge(pose, column)
        _, back_y, back_z = interior_back(pose, column)
        openness = pose_open(pose, column)
        for row in range(MOUTH_ROWS + 1):
            t = row / MOUTH_ROWS
            y = front_y * (1.0 - t) + back_y * t - math.sin(t * math.pi) * openness * 0.004
            z = front_z * (1.0 - t) + back_z * t
            vertices.append(Vector((x, y, z)))
    return vertices


def back_rim_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        vertices.extend((
            Vector((x, PACK_TOP, -0.009)),
            Vector((x, PACK_TOP + 0.0001, -0.009)),
        ))
        uvs.extend(((u, 0.0), (u, 1.0)))
    return vertices, uvs


def back_rim_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        x, back_y, back_z = interior_back(pose, column)
        openness = pose_open(pose, column)
        width = 0.001 + openness * 0.0025
        vertices.extend((
            Vector((x, back_y - width, back_z)),
            Vector((x, back_y + width, back_z)),
        ))
    return vertices


def lip_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        x = guide_x(column)
        for side in range(LIP_SIDES):
            angle = side / LIP_SIDES * math.tau
            vertices.append(Vector((x, PACK_TOP + math.sin(angle) * 0.0001, -0.009)))
            uvs.append((u, side / LIP_SIDES))
    return vertices, uvs


def lip_faces() -> list[tuple[int, int, int, int]]:
    faces: list[tuple[int, int, int, int]] = []
    for column in range(len(GUIDE_X) - 1):
        for side in range(LIP_SIDES):
            following = (side + 1) % LIP_SIDES
            a = column * LIP_SIDES + side
            b = column * LIP_SIDES + following
            c = (column + 1) * LIP_SIDES + following
            d = (column + 1) * LIP_SIDES + side
            faces.append((a, b, c, d))
    return faces


def lip_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        x, edge_y, edge_z = front_edge(pose, column)
        openness = pose_open(pose, column)
        radius = 0.0003 + openness * 0.00165
        for side in range(LIP_SIDES):
            angle = side / LIP_SIDES * math.tau
            vertices.append(Vector((
                x,
                edge_y + math.sin(angle) * radius,
                edge_z - math.cos(angle) * radius,
            )))
    return vertices


def rim_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(len(GUIDE_X)):
        u = column / (len(GUIDE_X) - 1)
        vertices.extend((
            Vector((guide_x(column), PACK_TOP, -0.012)),
            Vector((guide_x(column), PACK_TOP - 0.0001, -0.012)),
        ))
        uvs.extend(((u, 0.0), (u, 1.0)))
    return vertices, uvs


def rim_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(len(GUIDE_X)):
        x, edge_y, edge_z = front_edge(pose, column)
        openness = pose_open(pose, column)
        width = 0.00035 + openness * 0.0012
        vertices.extend((
            Vector((x, edge_y + width, edge_z - 0.0014)),
            Vector((x, edge_y - width, edge_z - 0.0014)),
        ))
    return vertices


def sidewall_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices = [Vector((PACK_HALF_WIDTH, PACK_TOP, -0.009)) for _ in range(8)]
    uvs = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)] * 2
    return vertices, uvs


SIDEWALL_FACES = (
    (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
    (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3),
)


def sidewall_state(pose: Pose, leading: bool) -> list[Vector]:
    index = pose.tear_start if leading else len(GUIDE_X) - 1
    x, front_y, front_z = front_edge(pose, index)
    _, back_y, back_z = interior_back(pose, index)
    openness = pose_open(pose, index)
    half_width = 0.00025 + openness * 0.0022
    lower_front = front_y - (0.001 + openness * 0.006)
    lower_back = back_y - (0.001 + openness * 0.004)
    return [
        Vector((x - half_width, lower_front, front_z)),
        Vector((x + half_width, lower_front, front_z)),
        Vector((x - half_width, front_y, front_z)),
        Vector((x + half_width, front_y, front_z)),
        Vector((x - half_width, lower_back, back_z)),
        Vector((x + half_width, lower_back, back_z)),
        Vector((x - half_width, back_y, back_z)),
        Vector((x + half_width, back_y, back_z)),
    ]


def strip_template() -> tuple[
    list[Vector], list[tuple[int, int, int, int]], list[int], list[tuple[float, float]]
]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for section in range(STRIP_SECTIONS):
        x = 0.080 + section * 0.009
        for _ in range(4):
            vertices.append(Vector((x, PACK_TOP, -0.010)))
        u = section / (STRIP_SECTIONS - 1)
        uvs.extend(((u, 0.0), (u, 1.0), (u, 0.0), (u, 1.0)))
    faces: list[tuple[int, int, int, int]] = []
    face_materials: list[int] = []
    for section in range(STRIP_SECTIONS - 1):
        a = section * 4
        b = (section + 1) * 4
        faces.extend(((a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2)))
        face_materials.extend((0, 1))
        faces.extend(((a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)))
        face_materials.extend((2, 2))
    return vertices, faces, face_materials, uvs


def strip_state(pose: Pose) -> list[Vector]:
    vertices: list[Vector] = []
    for x, y, z, roll in pose.strip_spine:
        cross = Vector((0.0, math.cos(roll) * STRIP_HALF_WIDTH, math.sin(roll) * STRIP_HALF_WIDTH))
        normal = Vector((0.0, -math.sin(roll), math.cos(roll))) * (FOIL_THICKNESS * 0.5)
        center = Vector((x, y, z))
        vertices.extend((
            center - cross - normal,
            center + cross - normal,
            center - cross + normal,
            center + cross + normal,
        ))
    return vertices


def pull_tab_template() -> tuple[
    list[Vector], list[tuple[int, ...]], list[int], list[tuple[float, float]]
]:
    front = [
        Vector((0.104, PACK_TOP - 0.003, -0.011)),
        Vector((0.128, PACK_TOP - 0.003, -0.011)),
        Vector((0.130, PACK_TOP + 0.006, -0.011)),
        Vector((0.122, PACK_TOP + 0.013, -0.011)),
        Vector((0.105, PACK_TOP + 0.007, -0.011)),
    ]
    vertices = front + [point + Vector((0.0, 0.0, FOIL_THICKNESS)) for point in front]
    faces: list[tuple[int, ...]] = [(0, 1, 2, 4), (4, 2, 3), (9, 7, 6, 5), (9, 8, 7)]
    face_materials = [0, 0, 1, 1]
    for index in range(5):
        following = (index + 1) % 5
        faces.append((index, 5 + index, 5 + following, following))
        face_materials.append(2)
    uvs = [(0, 0), (1, 0), (1, 1), (0.5, 1), (0, 1)] * 2
    return vertices, faces, face_materials, uvs


def pull_tab_state(pose: Pose) -> list[Vector]:
    base, _, _, _ = pull_tab_template()
    dx, dy, dz = pose.tab_lift
    pivot = Vector((0.104, PACK_TOP - 0.003, -0.011))
    result: list[Vector] = []
    for point in base:
        local = point - pivot
        result.append(pivot + Vector((
            local.x + dx,
            local.y + dy * (0.7 + max(0.0, local.y) * 14.0),
            local.z + dz * (0.7 + max(0.0, local.y) * 14.0),
        )))
    return result


def set_pose(objects: list[bpy.types.Object], pose: Pose | None) -> None:
    for object_ in objects:
        keys = object_.data.shape_keys.key_blocks
        for key in keys:
            if key.name != "Basis":
                key.value = 1.0 if pose and key.name == pose.key else 0.0
    bpy.context.view_layer.update()


def create_camera_and_lights() -> None:
    bpy.context.scene.world.color = (0.008, 0.010, 0.013)
    camera_data = bpy.data.cameras.new("R014_PackOnlyReviewCamera")
    camera = bpy.data.objects.new("R014_PackOnlyReviewCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, 0.0, -1.08)
    camera.data.lens = 68.0
    camera.rotation_euler = (Vector((0.0, -0.006, 0.020)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = camera
    for name, location, energy, color, size in (
        ("R014_Key", (-0.30, 0.36, -0.46), 750.0, (1.0, 0.89, 0.75), 1.4),
        ("R014_Fill", (0.30, 0.10, -0.30), 250.0, (0.70, 0.75, 0.80), 1.2),
        ("R014_Rim", (0.06, 0.28, 0.42), 450.0, (0.96, 0.84, 0.68), 0.9),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (Vector((0.0, 0.0, 0.015)) - light.location).to_track_quat("-Z", "Y").to_euler()


def render(path: Path, objects: list[bpy.types.Object], pose: Pose | None) -> None:
    set_pose(objects, pose)
    strip = bpy.data.objects.get("Pack_TornSealStrip")
    if strip:
        strip.hide_render = pose is None or pose.key == "Pose_TabCatch"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if strip:
        strip.hide_render = False


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

    body_path = project_root / "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png"
    flap_path = project_root / "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png"
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

    pack_art = material("MI_R014_ActualPackArtwork", (0.74, 0.74, 0.72, 1), 0.18, 0.52, body_path)
    crimp_art = material("MI_R014_ActualTopSeal", (0.65, 0.63, 0.58, 1), 0.18, 0.48, flap_path)
    inner = material("MI_R014_InnerFoil", (0.018, 0.014, 0.011, 1), 0.04, 0.62)
    back = material("MI_R014_BackFoilRim", (0.035, 0.027, 0.021, 1), 0.08, 0.54)
    lip = material("MI_R014_CrimpedLip", (0.14, 0.105, 0.070, 1), 0.22, 0.48)
    strip_front = material("MI_R014_TearStripFront", (0.26, 0.22, 0.17, 1), 0.12, 0.58, flap_path)
    strip_under = material("MI_R014_TearStripUnderside", (0.010, 0.008, 0.006, 1), 0.04, 0.70)
    cut_edge = material("MI_R014_FibrousCutEdge", (0.20, 0.14, 0.09, 1), 0.10, 0.76)
    rim = material("MI_R014_ContourCarrier", (0.34, 0.26, 0.17, 1), 0.04, 0.66)

    front_vertices, front_uvs = front_template()
    front = create_mesh(
        "Pack_FrontFoil",
        front_vertices,
        grid_faces(len(GUIDE_X) - 1, BODY_ROWS),
        [0] * ((len(GUIDE_X) - 1) * BODY_ROWS),
        front_uvs,
        [pack_art],
        front_state,
    )
    crimp_vertices, crimp_uvs = crimp_template()
    crimp = create_mesh(
        "Pack_TopSealRemaining",
        crimp_vertices,
        grid_faces(len(GUIDE_X) - 1, 1),
        [0] * (len(GUIDE_X) - 1),
        crimp_uvs,
        [crimp_art],
        crimp_state,
    )
    mouth_vertices, mouth_uvs = mouth_template()
    mouth = create_mesh(
        "Pack_InnerFoilMouth",
        mouth_vertices,
        grid_faces(len(GUIDE_X) - 1, MOUTH_ROWS),
        [0] * ((len(GUIDE_X) - 1) * MOUTH_ROWS),
        mouth_uvs,
        [inner],
        mouth_state,
    )
    back_vertices, back_uvs = back_rim_template()
    back_rim = create_mesh(
        "Pack_InnerBackFoilRim",
        back_vertices,
        grid_faces(len(GUIDE_X) - 1, 1),
        [0] * (len(GUIDE_X) - 1),
        back_uvs,
        [back],
        back_rim_state,
    )
    lip_vertices, lip_uvs = lip_template()
    rolled_lip = create_mesh(
        "Pack_RolledCrimpLip",
        lip_vertices,
        lip_faces(),
        [0] * len(lip_faces()),
        lip_uvs,
        [lip],
        lip_state,
    )
    rim_vertices, rim_uvs = rim_template()
    contour = create_mesh(
        "Pack_TornContourRim",
        rim_vertices,
        grid_faces(len(GUIDE_X) - 1, 1),
        [0] * (len(GUIDE_X) - 1),
        rim_uvs,
        [rim],
        rim_state,
    )
    side_vertices, side_uvs = sidewall_template()
    leading = create_mesh(
        "Pack_TearLeadingSidewall",
        side_vertices,
        list(SIDEWALL_FACES),
        [0] * len(SIDEWALL_FACES),
        side_uvs,
        [inner],
        lambda pose: sidewall_state(pose, True),
    )
    tab_wall = create_mesh(
        "Pack_TabSidewall",
        side_vertices,
        list(SIDEWALL_FACES),
        [0] * len(SIDEWALL_FACES),
        side_uvs,
        [inner],
        lambda pose: sidewall_state(pose, False),
    )
    strip_vertices, strip_faces, strip_mats, strip_uvs = strip_template()
    strip = create_mesh(
        "Pack_TornSealStrip",
        strip_vertices,
        strip_faces,
        strip_mats,
        strip_uvs,
        [strip_front, strip_under, cut_edge],
        strip_state,
    )
    tab_vertices, tab_faces, tab_mats, tab_uvs = pull_tab_template()
    pull_tab = create_mesh(
        "Pack_TopRightPullTab",
        tab_vertices,
        tab_faces,
        tab_mats,
        tab_uvs,
        [strip_front, strip_under, cut_edge],
        pull_tab_state,
    )

    rig = bpy.data.objects.new("PackOpeningGate04R014_PACK_ONLY_RIG", None)
    bpy.context.collection.objects.link(rig)
    rig.empty_display_type = "SINGLE_ARROW"
    rig["representation"] = "seven-authored-blend-shape-foil-poses"
    rig["pose_count"] = 7
    rig["actual_pack_canvas"] = "384x512"
    rig["case_geometry_included"] = False
    rig["case_rendered_or_baked"] = False
    objects = [front, crimp, mouth, back_rim, rolled_lip, contour, leading, tab_wall, strip, pull_tab]
    for object_ in objects:
        object_.parent = rig
        object_["pack_only"] = True
        object_["artwork_aspect"] = "384x512"

    front["role"] = "front foil carrying the actual authored Pack artwork"
    crimp["role"] = "remaining sealed 5.9 percent top seam"
    mouth["role"] = "dark finite-depth inner foil cavity"
    back_rim["role"] = "separate rear foil layer, never a rectangular back wall"
    rolled_lip["role"] = "thin crimped front lip at the torn contour"
    contour["role"] = "local CC0 contour-sweep carrier"
    leading["role"] = "moving irregular tear-front sidewall"
    tab_wall["role"] = "top-right tab sidewall"
    strip["role"] = "short double-sided curled 6.2 percent seal strip"
    pull_tab["role"] = "top-right pull tab only"

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
        "schema": "premium-display-case-gate04-r014-pack-only-rig.v1",
        "producer": {"blender": bpy.app.version_string, "route": "deterministic-bpy"},
        "representation": "seven hand-authored Pack-only FBX relative blend-shape poses",
        "poses": [
            {
                "key": "Basis" if index == 0 else pose.key,
                "progress": 0.0 if index == 0 else pose.progress,
                "description": description,
            }
            for index, (pose, description) in enumerate((
                (None, "sealed foil Pack"),
                (POSES[0], "top-right pull tab catches"),
                (POSES[1], "narrow top-seal peel; most Pack remains sealed"),
                (POSES[2], "irregular tear advances with a short curled strip"),
                (POSES[3], "formed deep mouth with thin crimp lip"),
                (POSES[4], "same live case can be contained behind the mouth"),
                (POSES[5], "case rises while Pack retreats from torn contour"),
            ))
        ],
        "actualPackArtwork": {
            "bodyPath": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
            "bodySha256": sha256(body_path),
            "flapPath": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
            "flapSha256": sha256(flap_path),
            "canvas": [384, 512],
            "geometryAspect": [0.255, 0.340],
        },
        "topSealHeightFraction": TOP_CRIMP_HEIGHT / PACK_HEIGHT,
        "mouthDepthMeters": MOUTH_DEPTH,
        "foilThicknessMeters": FOIL_THICKNESS,
        "authoredGuideStations": len(GUIDE_X),
        "caseGeometryIncluded": False,
        "caseRenderedOrBaked": False,
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
