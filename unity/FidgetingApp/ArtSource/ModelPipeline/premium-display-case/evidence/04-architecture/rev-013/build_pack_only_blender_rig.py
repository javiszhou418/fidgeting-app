#!/usr/bin/env python3
"""Build the Gate 04 R013 Pack-only blend-shape rig in real Blender."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


PACK_WIDTH_METERS = 0.255
PACK_HEIGHT_METERS = 0.340
PACK_HALF_WIDTH = PACK_WIDTH_METERS * 0.5
PACK_BOTTOM_Y = -PACK_HEIGHT_METERS * 0.5
SEALED_RIM_Y = PACK_HEIGHT_METERS * 0.318
TOP_CRIMP_HEIGHT = 0.014
LONGITUDINAL_COLUMNS = 96
BODY_ROWS = 34
MOUTH_ROWS = 4
STRIP_ROWS = 9
TEAR_SAMPLES = (0.0, 0.15, 0.35, 0.55, 0.75, 1.0)
MAX_MOUTH_HEIGHT = 0.088
MOUTH_DEPTH = 0.300
FOIL_THICKNESS = 0.00075
STRIP_WIDTH = 0.0105
SEED = 13013


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--fbx", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--preview-closed", required=True)
    parser.add_argument("--preview-open", required=True)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def smooth01(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def tear_front(progress: float) -> float:
    return PACK_HALF_WIDTH - PACK_WIDTH_METERS * max(0.0, min(1.0, progress))


def release_at(x: float, progress: float) -> float:
    if progress <= 0.0:
        return 0.0
    return smooth01((x - tear_front(progress) + 0.001) / 0.014)


def pouch_mouth_profile(u: float) -> float:
    """Round the open lip so it reads as a pouch mouth, not a rectangular lid."""
    return 0.48 + 0.52 * math.sin(max(0.0, min(1.0, u)) * math.pi) ** 0.72


def seeded_contour(column: int) -> float:
    """Fine, deterministic irregularity without a stepped sawtooth profile."""
    phase = column / LONGITUDINAL_COLUMNS
    generator = random.Random(SEED + column * 7919)
    grain = generator.uniform(-1.0, 1.0)
    low = math.sin(phase * math.tau * 7.0 + 0.41)
    mid = math.sin(phase * math.tau * 19.0 + 1.19)
    fine = math.sin(phase * math.tau * 43.0 + 0.73)
    return (low * 0.00045) + (mid * 0.00024) + (fine * 0.00012) + (grain * 0.00011)


TEAR_CONTOUR = tuple(seeded_contour(index) for index in range(LONGITUDINAL_COLUMNS + 1))


def contour_at(column: int) -> float:
    return TEAR_CONTOUR[max(0, min(LONGITUDINAL_COLUMNS, column))]


def shape_key_name(progress: float) -> str:
    return f"Tear_{round(progress * 100):03d}"


def material_with_nodes(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    image_path: Path | None = None,
    emission: tuple[float, float, float, float] | None = None,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    for node in list(nodes):
        nodes.remove(node)
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (460, 0)
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (170, 0)
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Alpha"].default_value = color[3]
    if emission is not None:
        shader.inputs["Emission Color"].default_value = emission
        shader.inputs["Emission Strength"].default_value = 0.8
    if image_path is not None:
        image = bpy.data.images.load(str(image_path), check_existing=True)
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Linear"
        texture.location = (-180, 0)
        links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
        material.surface_render_method = "DITHERED"
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def create_mesh_object(
    name: str,
    vertices: list[Vector],
    faces: list[tuple[int, ...]],
    face_materials: list[int],
    uvs: list[tuple[float, float]],
    materials: list[bpy.types.Material],
    state_generator,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    for material in materials:
        mesh.materials.append(material)
    mesh.update()

    uv_layer = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        polygon.material_index = face_materials[polygon.index]
        for loop_index in polygon.loop_indices:
            vertex_index = mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = uvs[vertex_index]

    object_ = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(object_)
    basis = object_.shape_key_add(name="Basis", from_mix=False)
    basis.interpolation = "KEY_LINEAR"
    for progress in TEAR_SAMPLES[1:]:
        key = object_.shape_key_add(name=shape_key_name(progress), from_mix=False)
        key.interpolation = "KEY_LINEAR"
        for index, value in enumerate(state_generator(progress)):
            key.data[index].co = value
    object_["tear_samples"] = list(TEAR_SAMPLES)
    object_["representation"] = "relative-blend-shapes"
    return object_


def add_grid_faces(columns: int, rows: int) -> list[tuple[int, int, int, int]]:
    faces: list[tuple[int, int, int, int]] = []
    for column in range(columns):
        for row in range(rows):
            lower = column * (rows + 1) + row
            upper = lower + 1
            next_lower = (column + 1) * (rows + 1) + row
            next_upper = next_lower + 1
            faces.append((lower, upper, next_upper, next_lower))
    return faces


def front_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        for row in range(BODY_ROWS + 1):
            v = row / BODY_ROWS
            y = PACK_BOTTOM_Y + (SEALED_RIM_Y - PACK_BOTTOM_Y) * v
            pillow = -0.006 * math.sin(u * math.pi) ** 0.8 * math.sin(v * math.pi)
            vertices.append(Vector((x, y, pillow)))
            uvs.append((u, v * (1.0 - 90.0 / 512.0)))
    return vertices, uvs


def front_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        contour = contour_at(column) * release
        drop = (
            MAX_MOUTH_HEIGHT
            * release
            * (0.42 + 0.58 * progress)
            * pouch_mouth_profile(u)
        )
        for row in range(BODY_ROWS + 1):
            v = row / BODY_ROWS
            top_influence = v**3.6
            y = (
                PACK_BOTTOM_Y
                + (SEALED_RIM_Y - PACK_BOTTOM_Y) * v
                - drop * top_influence
                + contour * top_influence
            )
            pillow = -0.006 * math.sin(u * math.pi) ** 0.8 * math.sin(v * math.pi)
            z = pillow - 0.0022 * progress - (0.014 * release * top_influence)
            vertices.append(Vector((x, y, z)))
    return vertices


def back_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices, uvs = front_template()
    return [
        Vector(
            (
                point.x,
                point.y,
                FOIL_THICKNESS
                + 0.004
                * math.sin(
                    (point.x + PACK_HALF_WIDTH) / PACK_WIDTH_METERS * math.pi
                )
                ** 0.8,
            )
        )
        for point in vertices
    ], uvs


def back_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        contour = contour_at(column) * release
        rear_rim_y = (
            SEALED_RIM_Y + release * (0.014 + progress * 0.012) + contour * 0.35
        )
        rear_rim_z = FOIL_THICKNESS + release * MOUTH_DEPTH
        for row in range(BODY_ROWS + 1):
            v = row / BODY_ROWS
            top_influence = v**4.1
            sealed_y = PACK_BOTTOM_Y + (SEALED_RIM_Y - PACK_BOTTOM_Y) * v
            base_z = FOIL_THICKNESS + 0.004 * math.sin(u * math.pi) ** 0.8
            # The released back layer must become a narrow rear rim, not an
            # opaque rectangular wall behind the live case.
            rim_band = (v - 0.5) * 0.010
            y = sealed_y * (1.0 - release) + (rear_rim_y + rim_band) * release
            z = base_z * (1.0 - release) + rear_rim_z * release
            vertices.append(Vector((x, y, z)))
    return vertices


def top_crimp_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        for row in range(2):
            v = row
            vertices.append(Vector((x, SEALED_RIM_Y + TOP_CRIMP_HEIGHT * v, -0.003)))
            uvs.append((u, 0.80 + 0.14 * v))
    return vertices, uvs


def top_crimp_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        collapsed_x = tear_front(progress)
        for row in range(2):
            height = TOP_CRIMP_HEIGHT * (1.0 - release)
            y = SEALED_RIM_Y + height * row + contour_at(column) * release * 0.2
            local_x = x * (1.0 - release) + collapsed_x * release
            z = -0.003 - release * 0.0015
            vertices.append(Vector((local_x, y, z)))
    return vertices


def mouth_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        for row in range(MOUTH_ROWS + 1):
            v = row / MOUTH_ROWS
            vertices.append(Vector((x, SEALED_RIM_Y, 0.0)))
            uvs.append((u, v))
    return vertices, uvs


def mouth_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        front_y = (
            SEALED_RIM_Y
            - MAX_MOUTH_HEIGHT
            * release
            * (0.42 + 0.58 * progress)
            * pouch_mouth_profile(u)
            + contour_at(column) * release
        )
        front_z = -0.016 * release
        # The broad, deep volume is carried by the two side gussets below.
        # This central liner stays narrow so it reads as foil lining, not a lid.
        back_y = front_y + release * 0.008
        back_z = front_z + release * 0.018
        for row in range(MOUTH_ROWS + 1):
            v = row / MOUTH_ROWS
            eased = smooth01(v)
            y = front_y * (1.0 - eased) + back_y * eased
            y -= math.sin(v * math.pi) * release * 0.009
            z = front_z * (1.0 - eased) + back_z * eased
            vertices.append(Vector((x, y, z)))
    return vertices


def gusset_template() -> tuple[
    list[Vector], list[tuple[int, int, int, int]], list[tuple[float, float]]
]:
    vertices = [Vector((PACK_HALF_WIDTH, SEALED_RIM_Y, 0.0)) for _ in range(8)]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
    ]
    uvs = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)] * 2
    return vertices, faces, uvs


def gusset_state(progress: float, leading: bool) -> list[Vector]:
    if progress <= 0.0:
        return [Vector((PACK_HALF_WIDTH, SEALED_RIM_Y, 0.0)) for _ in range(8)]
    edge_x = tear_front(progress) if leading else PACK_HALF_WIDTH
    opening = smooth01(progress)
    contour_column = round(
        (edge_x + PACK_HALF_WIDTH) / PACK_WIDTH_METERS * LONGITUDINAL_COLUMNS
    )
    edge_u = (edge_x + PACK_HALF_WIDTH) / PACK_WIDTH_METERS
    front_y = (
        SEALED_RIM_Y
        - MAX_MOUTH_HEIGHT
        * opening
        * (0.42 + 0.58 * progress)
        * pouch_mouth_profile(edge_u)
        + contour_at(contour_column) * opening
    )
    front_z = -0.016 * opening
    back_y = SEALED_RIM_Y + opening * (0.014 + progress * 0.012)
    back_z = opening * MOUTH_DEPTH
    half_width = 0.0019 * opening
    front_lower = front_y - 0.010 * opening
    rear_lower = front_y - 0.007 * opening
    return [
        Vector((edge_x - half_width, front_lower, front_z)),
        Vector((edge_x + half_width, front_lower, front_z)),
        Vector((edge_x - half_width, front_y, front_z)),
        Vector((edge_x + half_width, front_y, front_z)),
        Vector((edge_x - half_width, rear_lower, back_z)),
        Vector((edge_x + half_width, rear_lower, back_z)),
        Vector((edge_x - half_width, back_y, back_z)),
        Vector((edge_x + half_width, back_y, back_z)),
    ]


def lip_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        for row in range(2):
            vertices.append(Vector((x, SEALED_RIM_Y, -0.003)))
            uvs.append((u, row))
    return vertices, uvs


def lip_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        y = (
            SEALED_RIM_Y
            - MAX_MOUTH_HEIGHT
            * release
            * (0.42 + 0.58 * progress)
            * pouch_mouth_profile(u)
            + contour_at(column) * release
        )
        for row in range(2):
            lip_radius = 0.0032 * release
            vertices.append(
                Vector(
                    (
                        x,
                        y - lip_radius * row,
                        -0.016 * release + lip_radius * (row - 0.5),
                    )
                )
            )
    return vertices


def rim_template() -> tuple[list[Vector], list[tuple[float, float]]]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * (column / LONGITUDINAL_COLUMNS)
        for row in range(2):
            vertices.append(Vector((x, SEALED_RIM_Y, -0.005)))
            uvs.append((column / LONGITUDINAL_COLUMNS, row))
    return vertices, uvs


def rim_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * u
        release = release_at(x, progress)
        y = (
            SEALED_RIM_Y
            - MAX_MOUTH_HEIGHT
            * release
            * (0.42 + 0.58 * progress)
            * pouch_mouth_profile(u)
            + contour_at(column) * release
        )
        width = 0.0012 * release
        for row in range(2):
            vertices.append(Vector((x, y - width * row, -0.019 * release)))
    return vertices


def strip_template() -> tuple[
    list[Vector], list[tuple[int, int, int, int]], list[int], list[tuple[float, float]]
]:
    vertices: list[Vector] = []
    uvs: list[tuple[float, float]] = []
    for column in range(LONGITUDINAL_COLUMNS + 1):
        u = column / LONGITUDINAL_COLUMNS
        for side in range(2):
            for row in range(STRIP_ROWS + 1):
                cross = row / STRIP_ROWS - 0.5
                vertices.append(
                    Vector((PACK_HALF_WIDTH, SEALED_RIM_Y + cross * 0.0001, -0.006))
                )
                uvs.append((u, 0.80 + (row / STRIP_ROWS) * 0.14))
    faces: list[tuple[int, int, int, int]] = []
    materials: list[int] = []
    row_count = STRIP_ROWS + 1
    for column in range(LONGITUDINAL_COLUMNS):
        for row in range(STRIP_ROWS):
            a = (column * 2) * row_count + row
            b = ((column + 1) * 2) * row_count + row
            c = b + 1
            d = a + 1
            faces.append((a, b, c, d))
            materials.append(0)
            a += row_count
            b += row_count
            c += row_count
            d += row_count
            faces.append((d, c, b, a))
            materials.append(1)
        front_start = (column * 2) * row_count
        front_next = ((column + 1) * 2) * row_count
        back_start = front_start + row_count
        back_next = front_next + row_count
        faces.append((front_start, front_next, back_next, back_start))
        materials.append(2)
        faces.append(
            (
                front_start + STRIP_ROWS,
                back_start + STRIP_ROWS,
                back_next + STRIP_ROWS,
                front_next + STRIP_ROWS,
            )
        )
        materials.append(2)
    return vertices, faces, materials, uvs


def strip_spine(x: float, progress: float) -> tuple[Vector, Vector, Vector]:
    front = tear_front(progress)
    released_width = max(0.0001, PACK_HALF_WIDTH - front)
    u = max(0.0, min(1.0, (x - front) / released_width))
    curve = math.sin(u * math.pi)
    curl = smooth01((u - 0.68) / 0.32)
    global_u = (x + PACK_HALF_WIDTH) / PACK_WIDTH_METERS
    lip_y = (
        SEALED_RIM_Y
        - MAX_MOUTH_HEIGHT
        * progress
        * (0.42 + 0.58 * progress)
        * pouch_mouth_profile(global_u)
        + seeded_contour(round(global_u * LONGITUDINAL_COLUMNS)) * progress
    )
    # Keep the released seal close to the tear line. Only the pull-tab end
    # folds forward, so the strip cannot become a bow or rigid horizontal lid.
    base_x = x + curve * progress * 0.004 + curl * progress * 0.014
    base_y = lip_y + progress * (0.002 + curl * 0.020)
    base_z = -0.011 - progress * (curve * 0.012 + curl * 0.028)
    tangent = Vector(
        (
            1.0 + math.cos(u * math.pi) * progress * 0.04,
            -math.cos(u * math.pi) * progress * 0.08,
            -math.cos(u * math.pi) * progress * 0.09,
        )
    ).normalized()
    cross = Vector(
        (
            0.0,
            0.55 + 0.08 * math.cos(u * math.pi * 3.0),
            0.84,
        )
    )
    cross = (cross - tangent * cross.dot(tangent)).normalized()
    normal = tangent.cross(cross).normalized()
    return Vector((base_x, base_y, base_z)), cross, normal


def strip_state(progress: float) -> list[Vector]:
    vertices: list[Vector] = []
    front = tear_front(progress)
    for column in range(LONGITUDINAL_COLUMNS + 1):
        x = -PACK_HALF_WIDTH + PACK_WIDTH_METERS * (column / LONGITUDINAL_COLUMNS)
        release = release_at(x, progress)
        spine, cross_axis, normal = strip_spine(x, progress)
        collapsed = Vector((front, SEALED_RIM_Y, -0.006))
        for side in range(2):
            surface = -1.0 if side == 0 else 1.0
            for row in range(STRIP_ROWS + 1):
                cross = row / STRIP_ROWS - 0.5
                crease = (
                    math.sin(row / STRIP_ROWS * math.pi)
                    * math.sin((column / LONGITUDINAL_COLUMNS) * math.pi * 5.0)
                    * (0.0008 + 0.00065 * progress)
                )
                deployed = (
                    spine
                    + cross_axis * (cross * STRIP_WIDTH)
                    + normal * (surface * FOIL_THICKNESS * 0.5 + crease)
                )
                vertices.append(collapsed.lerp(deployed, release))
    return vertices


def pull_tab_template() -> tuple[
    list[Vector], list[tuple[int, int, int, int]], list[int], list[tuple[float, float]]
]:
    front = [
        Vector((0.116, SEALED_RIM_Y - 0.002, -0.006)),
        Vector((0.132, SEALED_RIM_Y - 0.002, -0.006)),
        Vector((0.133, SEALED_RIM_Y + 0.006, -0.006)),
        Vector((0.125, SEALED_RIM_Y + 0.013, -0.006)),
        Vector((0.116, SEALED_RIM_Y + 0.008, -0.006)),
    ]
    vertices = front + [point + Vector((0.0, 0.0, FOIL_THICKNESS)) for point in front]
    faces: list[tuple[int, int, int, int]] = [
        (0, 1, 2, 4),
        (4, 2, 3),
        (9, 7, 6, 5),
        (9, 8, 7),
    ]
    materials = [0, 0, 1, 1]
    for index in range(5):
        next_index = (index + 1) % 5
        faces.append((index, 5 + index, 5 + next_index, next_index))
        materials.append(2)
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.5, 1.0), (0.0, 1.0)] * 2
    return vertices, faces, materials, uvs


def pull_tab_state(progress: float) -> list[Vector]:
    vertices, _, _, _ = pull_tab_template()
    lift = smooth01((progress - 0.02) / 0.35)
    result: list[Vector] = []
    pivot = Vector((0.120, SEALED_RIM_Y - 0.002, -0.006))
    for index, point in enumerate(vertices):
        local = point - pivot
        local.y += lift * (0.014 + max(0.0, local.y) * 0.45)
        local.z -= lift * (0.030 + max(0.0, local.y) * 0.75)
        local.x += lift * 0.006
        result.append(pivot + local)
    return result


def add_review_lights() -> None:
    bpy.context.scene.world.color = (0.008, 0.010, 0.013)
    for name, location, energy, color, size in (
        ("R013_Key", (-0.35, 0.42, -0.48), 820.0, (1.0, 0.88, 0.71), 1.6),
        ("R013_Fill", (0.32, 0.15, -0.30), 380.0, (0.65, 0.73, 0.82), 1.2),
        ("R013_Rim", (0.04, 0.34, 0.44), 600.0, (0.95, 0.86, 0.72), 1.0),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.color = color
        data.shape = "DISK"
        data.size = size
        object_ = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(object_)
        object_.location = location
        object_.rotation_euler = (math.radians(28), 0.0, math.radians(180))


def look_at(object_: bpy.types.Object, target: Vector) -> None:
    object_.rotation_euler = (target - object_.location).to_track_quat("-Z", "Y").to_euler()


def add_review_camera() -> None:
    camera_data = bpy.data.cameras.new("R013_PackRigReviewCamera")
    camera = bpy.data.objects.new("R013_PackRigReviewCamera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, 0.004, -1.18)
    camera.data.lens = 62.0
    look_at(camera, Vector((0.0, -0.008, 0.075)))
    bpy.context.scene.camera = camera


def set_progress(objects: list[bpy.types.Object], progress: float) -> None:
    previous = max((value for value in TEAR_SAMPLES if value <= progress), default=0.0)
    following = min((value for value in TEAR_SAMPLES if value >= progress), default=1.0)
    if previous == following:
        blend = 0.0
    else:
        blend = (progress - previous) / (following - previous)
    for object_ in objects:
        shape_keys = object_.data.shape_keys
        if shape_keys is None:
            continue
        for key in shape_keys.key_blocks:
            if key.name != "Basis":
                key.value = 0.0
        if previous == following and previous > 0.0:
            shape_keys.key_blocks[shape_key_name(previous)].value = 1.0
        elif previous > 0.0:
            shape_keys.key_blocks[shape_key_name(previous)].value = 1.0 - blend
        if previous != following and following > 0.0:
            shape_keys.key_blocks[shape_key_name(following)].value = blend


def render_preview(path: Path, objects: list[bpy.types.Object], progress: float) -> None:
    set_progress(objects, progress)
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def write_contract_text(
    rig: bpy.types.Object,
    pack_body: Path,
    pack_flap: Path,
) -> None:
    contract = {
        "schema": "premium-display-case-gate04-r013-pack-only-rig.v1",
        "representation": "Pack-only Blender relative blend shapes imported through FBX",
        "longitudinalTearColumns": LONGITUDINAL_COLUMNS,
        "tearSamples": list(TEAR_SAMPLES),
        "mouthDepthMeters": MOUTH_DEPTH,
        "foilThicknessMeters": FOIL_THICKNESS,
        "frontArtwork": {
            "path": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
            "sha256": sha256(pack_body),
            "canvas": [384, 512],
        },
        "topCrimpArtwork": {
            "path": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
            "sha256": sha256(pack_flap),
            "canvas": [384, 512],
        },
        "caseGeometryIncluded": False,
        "caseRenderedOrBaked": False,
        "control": {
            "object": rig.name,
            "property": "tear_progress",
            "unityDriver": "normalized drag progress / pairwise blend-shape interpolation",
        },
    }
    text = bpy.data.texts.new("R013_PACK_ONLY_RIG_CONTRACT.json")
    text.write(json.dumps(contract, indent=2))


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    blend_path = Path(args.blend).resolve()
    fbx_path = Path(args.fbx).resolve()
    report_path = Path(args.report).resolve()
    preview_closed = Path(args.preview_closed).resolve()
    preview_open = Path(args.preview_open).resolve()
    for path in (blend_path, fbx_path, report_path, preview_closed, preview_open):
        path.parent.mkdir(parents=True, exist_ok=True)

    pack_body = project_root / "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png"
    pack_flap = project_root / "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png"
    if not pack_body.is_file() or not pack_flap.is_file():
        raise RuntimeError("The audited Pack artwork is missing.")

    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    pack_artwork = material_with_nodes(
        "MI_R013_ActualPackArtwork",
        (0.72, 0.72, 0.70, 1.0),
        0.34,
        0.38,
        pack_body,
    )
    back_foil = material_with_nodes(
        "MI_R013_BackFoil",
        (0.018, 0.016, 0.014, 1.0),
        0.08,
        0.68,
    )
    top_crimp = material_with_nodes(
        "MI_R013_ActualTopCrimp",
        (0.62, 0.60, 0.56, 1.0),
        0.42,
        0.28,
        pack_flap,
    )
    inner_foil = material_with_nodes(
        "MI_R013_InnerFoil",
        (0.010, 0.009, 0.008, 1.0),
        0.08,
        0.72,
    )
    contact_foil = material_with_nodes(
        "MI_R013_ContactOcclusion",
        (0.003, 0.003, 0.002, 1.0),
        0.04,
        0.80,
    )
    strip_front = material_with_nodes(
        "MI_R013_TornSealFront",
        (0.105, 0.093, 0.076, 1.0),
        0.26,
        0.62,
    )
    strip_under = material_with_nodes(
        "MI_R013_TornSealDarkUnderside",
        (0.009, 0.008, 0.007, 1.0),
        0.12,
        0.68,
    )
    cut_edge = material_with_nodes(
        "MI_R013_TornSealCutEdge",
        (0.15, 0.12, 0.09, 1.0),
        0.20,
        0.28,
    )
    warm_rim = material_with_nodes(
        "MI_R013_TornContourRim",
        (0.22, 0.17, 0.11, 1.0),
        0.0,
        0.60,
        emission=(0.30, 0.18, 0.08, 1.0),
    )

    rig = bpy.data.objects.new("PackOpeningGate04R013_PACK_ONLY_RIG", None)
    bpy.context.collection.objects.link(rig)
    rig.empty_display_type = "SINGLE_ARROW"
    rig.empty_display_size = 0.08
    rig["tear_progress"] = 0.0
    rig.id_properties_ui("tear_progress").update(min=0.0, max=1.0)
    rig["representation"] = "relative-blend-shape-pack-only"
    rig["longitudinal_tear_columns"] = LONGITUDINAL_COLUMNS
    rig["case_geometry_included"] = False
    rig["case_rendered_or_baked"] = False

    front_vertices, front_uvs = front_template()
    front = create_mesh_object(
        "Pack_FrontFoil",
        front_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, BODY_ROWS),
        [0] * (LONGITUDINAL_COLUMNS * BODY_ROWS),
        front_uvs,
        [pack_artwork],
        front_state,
    )
    back_vertices, back_uvs = back_template()
    back = create_mesh_object(
        "Pack_BackFoil",
        back_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, BODY_ROWS),
        [0] * (LONGITUDINAL_COLUMNS * BODY_ROWS),
        back_uvs,
        [back_foil],
        back_state,
    )
    crimp_vertices, crimp_uvs = top_crimp_template()
    crimp = create_mesh_object(
        "Pack_TopCrimpRemaining",
        crimp_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, 1),
        [0] * LONGITUDINAL_COLUMNS,
        crimp_uvs,
        [top_crimp],
        top_crimp_state,
    )
    mouth_vertices, mouth_uvs = mouth_template()
    mouth = create_mesh_object(
        "Pack_InnerFoilMouth",
        mouth_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, MOUTH_ROWS),
        [0] * (LONGITUDINAL_COLUMNS * MOUTH_ROWS),
        mouth_uvs,
        [inner_foil],
        mouth_state,
    )
    gusset_vertices, gusset_faces, gusset_uvs = gusset_template()
    leading_gusset = create_mesh_object(
        "Pack_MouthLeadingGusset",
        gusset_vertices,
        gusset_faces,
        [0] * len(gusset_faces),
        gusset_uvs,
        [inner_foil],
        lambda progress: gusset_state(progress, True),
    )
    tab_gusset = create_mesh_object(
        "Pack_MouthTabGusset",
        gusset_vertices,
        gusset_faces,
        [0] * len(gusset_faces),
        gusset_uvs,
        [inner_foil],
        lambda progress: gusset_state(progress, False),
    )
    lip_vertices, lip_uvs = lip_template()
    lip = create_mesh_object(
        "Pack_RolledFrontLip",
        lip_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, 1),
        [0] * LONGITUDINAL_COLUMNS,
        lip_uvs,
        [contact_foil],
        lip_state,
    )
    rim_vertices, rim_uvs = rim_template()
    rim = create_mesh_object(
        "Pack_TornContourRim",
        rim_vertices,
        add_grid_faces(LONGITUDINAL_COLUMNS, 1),
        [0] * LONGITUDINAL_COLUMNS,
        rim_uvs,
        [warm_rim],
        rim_state,
    )
    strip_vertices, strip_faces, strip_materials, strip_uvs = strip_template()
    strip = create_mesh_object(
        "Pack_TornSealStrip",
        strip_vertices,
        strip_faces,
        strip_materials,
        strip_uvs,
        [strip_front, strip_under, cut_edge],
        strip_state,
    )
    tab_vertices, tab_faces, tab_materials, tab_uvs = pull_tab_template()
    tab = create_mesh_object(
        "Pack_TopRightPullTab",
        tab_vertices,
        tab_faces,
        tab_materials,
        tab_uvs,
        [strip_front, strip_under, cut_edge],
        pull_tab_state,
    )

    objects = [
        front,
        back,
        crimp,
        mouth,
        leading_gusset,
        tab_gusset,
        lip,
        rim,
        strip,
        tab,
    ]
    for object_ in objects:
        object_.parent = rig
        object_["longitudinal_tear_columns"] = LONGITUDINAL_COLUMNS
        object_["artwork_aspect"] = "384x512"
        object_["pack_only"] = True

    front["role"] = "front foil layer with the actual shipping Pack artwork"
    back["role"] = "separate back foil layer"
    crimp["role"] = "remaining sealed top crimp"
    mouth["role"] = "narrow central inner foil liner"
    leading_gusset["role"] = "moving leading side gusset with finite mouth depth"
    tab_gusset["role"] = "top-right pull-tab side gusset with finite mouth depth"
    lip["role"] = "front contact-occlusion lip"
    rim["role"] = "narrow torn-contour source-sweep carrier"
    strip["role"] = "double-sided narrow torn top seal with curled spine"
    tab["role"] = "actual top-right pull tab"

    write_contract_text(rig, pack_body, pack_flap)
    add_review_lights()
    add_review_camera()
    render_preview(preview_closed, objects, 0.0)
    render_preview(preview_open, objects, 0.75)
    set_progress(objects, 0.0)
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
        "schema": "premium-display-case-gate04-r013-blender-rig-build.v1",
        "producer": {
            "blender": bpy.app.version_string,
            "engine": "Blender bpy deterministic build",
            "seed": SEED,
        },
        "representation": "Pack-only FBX relative blend shapes",
        "blend": str(blend_path),
        "blendSha256": sha256(blend_path),
        "fbx": str(fbx_path),
        "fbxSha256": sha256(fbx_path),
        "packArtwork": {
            "path": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
            "sha256": sha256(pack_body),
            "canvas": [384, 512],
        },
        "flapArtwork": {
            "path": "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
            "sha256": sha256(pack_flap),
            "canvas": [384, 512],
        },
        "longitudinalTearColumns": LONGITUDINAL_COLUMNS,
        "tearSamples": list(TEAR_SAMPLES),
        "maxMouthHeightMeters": MAX_MOUTH_HEIGHT,
        "mouthDepthMeters": MOUTH_DEPTH,
        "foilThicknessMeters": FOIL_THICKNESS,
        "objects": [
            {
                "name": object_.name,
                "vertexCount": len(object_.data.vertices),
                "polygonCount": len(object_.data.polygons),
                "blendShapeCount": len(object_.data.shape_keys.key_blocks) - 1,
            }
            for object_ in objects
        ],
        "caseGeometryIncluded": False,
        "caseRenderedOrBaked": False,
        "previewClosed": str(preview_closed),
        "previewOpen": str(preview_open),
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
