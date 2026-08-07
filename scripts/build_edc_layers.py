#!/usr/bin/env python3
"""Simplify the manually height-cut EDC layers while preserving Meshy UVs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import fast_simplification
import numpy as np


TOTAL_TARGET_TRIANGLES = 1_994_857
SIMPLIFICATION_AGGRESSION = 0
LAYER_MINIMUM_Y = {
    "L1_TopFrame": 0.0064,
    "L2_UpperShell": 0.0010,
    "L3_Gasket": 0.0000,
    "L6_InnerFrame": -0.0030,
    "L7_BottomShell": float("-inf"),
}


def count_records(path: Path) -> tuple[int, int, int, int]:
    vertices = uvs = normals = faces = 0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.startswith("v "):
                vertices += 1
            elif line.startswith("vt "):
                uvs += 1
            elif line.startswith("vn "):
                normals += 1
            elif line.startswith("f "):
                faces += 1
    return vertices, uvs, normals, faces


def load_obj(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    vertex_count, uv_count, normal_count, face_count = count_records(path)
    if vertex_count == 0 or face_count == 0:
        raise ValueError(f"No triangular mesh found in {path}")
    if uv_count != vertex_count:
        raise ValueError(
            f"Expected one UV per vertex; got {vertex_count} vertices and {uv_count} UVs"
        )
    if normal_count != vertex_count:
        raise ValueError(
            f"Expected one normal per vertex; got {vertex_count} vertices and "
            f"{normal_count} normals"
        )

    vertices = np.empty((vertex_count, 3), dtype=np.float64)
    uvs = np.empty((uv_count, 2), dtype=np.float64)
    normals = np.empty((normal_count, 3), dtype=np.float64)
    faces = np.empty((face_count, 3), dtype=np.int32)
    vertex_index = uv_index = normal_index = face_index = 0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.startswith("v "):
                vertices[vertex_index] = np.fromstring(line[2:], sep=" ", count=3)
                vertex_index += 1
            elif line.startswith("vt "):
                uvs[uv_index] = np.fromstring(line[3:], sep=" ", count=2)
                uv_index += 1
            elif line.startswith("vn "):
                normals[normal_index] = np.fromstring(line[3:], sep=" ", count=3)
                normal_index += 1
            elif line.startswith("f "):
                tokens = line.split()[1:4]
                faces[face_index] = [int(token.split("/", 1)[0]) - 1 for token in tokens]
                face_index += 1
    return vertices, uvs, normals, faces


def transfer_vertex_data(
    source_vertices: np.ndarray,
    source_data: np.ndarray,
    runtime_vertices: np.ndarray,
    source_to_runtime: np.ndarray,
) -> np.ndarray:
    mapped_positions = runtime_vertices[source_to_runtime]
    distances = np.einsum(
        "ij,ij->i",
        source_vertices - mapped_positions,
        source_vertices - mapped_positions,
    )
    order = np.lexsort((distances, source_to_runtime))
    sorted_mapping = source_to_runtime[order]
    runtime_indices, first_positions = np.unique(sorted_mapping, return_index=True)
    representatives = order[first_positions]

    runtime_data = np.zeros(
        (runtime_vertices.shape[0], source_data.shape[1]),
        dtype=np.float64,
    )
    runtime_data[runtime_indices] = source_data[representatives]
    if runtime_indices.size != runtime_vertices.shape[0]:
        missing = runtime_vertices.shape[0] - runtime_indices.size
        raise ValueError(f"UV transfer left {missing} runtime vertices unmapped")
    return runtime_data


def simplify_with_uvs(
    vertices: np.ndarray,
    uvs: np.ndarray,
    normals: np.ndarray,
    faces: np.ndarray,
    target: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if faces.shape[0] <= target:
        return vertices, uvs, normals, faces

    _, runtime_faces, collapses = fast_simplification.simplify(
        vertices,
        faces,
        target_count=target,
        agg=SIMPLIFICATION_AGGRESSION,
        return_collapses=True,
    )
    runtime_vertices, replay_faces, source_to_runtime = (
        fast_simplification.replay_simplification(
            vertices.astype(np.float32),
            faces,
            collapses,
        )
    )
    if replay_faces.shape != runtime_faces.shape:
        raise ValueError(
            f"Simplification replay changed face count: {runtime_faces.shape} -> {replay_faces.shape}"
        )
    runtime_uvs = transfer_vertex_data(
        vertices,
        uvs,
        runtime_vertices,
        source_to_runtime,
    )
    runtime_normals = transfer_vertex_data(
        vertices,
        normals,
        runtime_vertices,
        source_to_runtime,
    )
    normal_lengths = np.linalg.norm(runtime_normals, axis=1)
    nonzero = normal_lengths > 1e-12
    runtime_normals[nonzero] /= normal_lengths[nonzero, None]
    return runtime_vertices, runtime_uvs, runtime_normals, replay_faces


def write_obj(
    path: Path,
    object_name: str,
    vertices: np.ndarray,
    uvs: np.ndarray,
    normals: np.ndarray,
    faces: np.ndarray,
) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write("# Mobile EDC layer preserving Meshy UVs\n")
        output.write(f"o {object_name}\n")
        for x, y, z in vertices:
            output.write(f"v {x:.9g} {y:.9g} {z:.9g}\n")
        for u, v in uvs:
            output.write(f"vt {u:.9g} {v:.9g}\n")
        for x, y, z in normals:
            output.write(f"vn {x:.9g} {y:.9g} {z:.9g}\n")
        for a, b, c in faces + 1:
            output.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}\n")


def resolve_layer_indices(vertices: np.ndarray, faces: np.ndarray) -> dict[str, np.ndarray]:
    centroid_y = vertices[faces].mean(axis=1)[:, 1]
    remaining = np.ones(faces.shape[0], dtype=bool)
    selections: dict[str, np.ndarray] = {}
    for name, minimum_y in LAYER_MINIMUM_Y.items():
        selected = remaining & (centroid_y >= minimum_y)
        selections[name] = np.flatnonzero(selected)
        remaining[selected] = False
    if remaining.any():
        raise ValueError(f"{remaining.sum()} faces were not assigned to a manual layer")
    return selections


def extract_layer(
    vertices: np.ndarray,
    uvs: np.ndarray,
    normals: np.ndarray,
    faces: np.ndarray,
    face_indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    selected_faces = faces[face_indices]
    referenced, inverse = np.unique(selected_faces.reshape(-1), return_inverse=True)
    return (
        vertices[referenced],
        uvs[referenced],
        normals[referenced],
        inverse.reshape((-1, 3)).astype(np.int32),
    )


def process_layer(
    destination: Path,
    name: str,
    source_vertices: np.ndarray,
    source_normals: np.ndarray,
    source_faces: np.ndarray,
    runtime_vertices: np.ndarray,
    runtime_uvs: np.ndarray,
    runtime_normals: np.ndarray,
    runtime_faces: np.ndarray,
    source_face_indices: np.ndarray,
    runtime_face_indices: np.ndarray,
) -> dict:
    source_layer_vertices, _, _, source_layer_faces = extract_layer(
        source_vertices,
        np.zeros((source_vertices.shape[0], 2), dtype=np.float64),
        source_normals,
        source_faces,
        source_face_indices,
    )
    vertices, uvs, normals, faces = extract_layer(
        runtime_vertices,
        runtime_uvs,
        runtime_normals,
        runtime_faces,
        runtime_face_indices,
    )
    minimum = vertices.min(axis=0)
    maximum = vertices.max(axis=0)
    center = (minimum + maximum) * 0.5
    source_size = source_layer_vertices.max(axis=0) - source_layer_vertices.min(axis=0)
    centered_vertices = vertices - center
    write_obj(destination, name, centered_vertices, uvs, normals, faces)
    return {
        "name": name,
        "assetPath": f"Assets/_EDC/Generated/Meshes/{destination.name}",
        "pivotPosition": [float(value) for value in center],
        "sourceBoundsSize": [float(value) for value in source_size],
        "sourceVertices": int(source_layer_vertices.shape[0]),
        "sourceTriangles": int(source_layer_faces.shape[0]),
        "runtimeVertices": int(vertices.shape[0]),
        "runtimeTriangles": int(faces.shape[0]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_folder", type=Path)
    parser.add_argument("destination_folder", type=Path)
    args = parser.parse_args()
    args.destination_folder.mkdir(parents=True, exist_ok=True)

    full_source = args.source_folder / "EDC_Full_Source.obj"
    source_vertices, source_uvs, source_normals, source_faces = load_obj(full_source)
    runtime_vertices, runtime_uvs, runtime_normals, runtime_faces = simplify_with_uvs(
        source_vertices,
        source_uvs,
        source_normals,
        source_faces,
        TOTAL_TARGET_TRIANGLES,
    )
    source_selections = resolve_layer_indices(source_vertices, source_faces)
    runtime_selections = resolve_layer_indices(runtime_vertices, runtime_faces)

    manifest = {
        "targetLongestDimensionMeters": 0.08,
        "totalRuntimeTriangles": 0,
        "layers": [],
    }
    for name in LAYER_MINIMUM_Y:
        destination = args.destination_folder / f"{name}_Runtime.obj"
        entry = process_layer(
            destination,
            name,
            source_vertices,
            source_normals,
            source_faces,
            runtime_vertices,
            runtime_uvs,
            runtime_normals,
            runtime_faces,
            source_selections[name],
            runtime_selections[name],
        )
        manifest["layers"].append(entry)
        manifest["totalRuntimeTriangles"] += entry["runtimeTriangles"]
        print(
            f"{name}: {entry['sourceTriangles']} -> {entry['runtimeTriangles']} triangles; "
            f"pivot={entry['pivotPosition']}"
        )

    manifest_path = args.destination_folder / "layer-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"total_runtime_triangles={manifest['totalRuntimeTriangles']} "
        f"manifest={manifest_path}"
    )


if __name__ == "__main__":
    main()
