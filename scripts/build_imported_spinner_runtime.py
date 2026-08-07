#!/usr/bin/env python3
"""Build the mobile spinner mesh while preserving the FBX's original UV atlas."""

from __future__ import annotations

import argparse
from pathlib import Path

import fast_simplification
import numpy as np
from PIL import Image, ImageOps


def count_records(path: Path) -> tuple[int, int, int]:
    vertices = uvs = faces = 0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.startswith("v "):
                vertices += 1
            elif line.startswith("vt "):
                uvs += 1
            elif line.startswith("f "):
                faces += 1
    return vertices, uvs, faces


def load_obj(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertex_count, uv_count, face_count = count_records(path)
    if vertex_count == 0 or face_count == 0:
        raise ValueError(f"No triangular mesh found in {path}")
    if uv_count != vertex_count:
        raise ValueError(
            f"The source must have one UV per vertex; got {vertex_count} vertices and {uv_count} UVs"
        )

    vertices = np.empty((vertex_count, 3), dtype=np.float64)
    uvs = np.empty((uv_count, 2), dtype=np.float64)
    faces = np.empty((face_count, 3), dtype=np.int32)
    vertex_index = uv_index = face_index = 0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.startswith("v "):
                vertices[vertex_index] = np.fromstring(line[2:], sep=" ", count=3)
                vertex_index += 1
            elif line.startswith("vt "):
                uvs[uv_index] = np.fromstring(line[3:], sep=" ", count=2)
                uv_index += 1
            elif line.startswith("f "):
                tokens = line.split()[1:4]
                faces[face_index] = [int(token.split("/", 1)[0]) - 1 for token in tokens]
                face_index += 1
    return vertices, uvs, faces


def transfer_uvs(
    source_vertices: np.ndarray,
    source_uvs: np.ndarray,
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

    runtime_uvs = np.zeros((runtime_vertices.shape[0], 2), dtype=np.float64)
    runtime_uvs[runtime_indices] = source_uvs[representatives]
    if runtime_indices.size != runtime_vertices.shape[0]:
        missing = runtime_vertices.shape[0] - runtime_indices.size
        raise ValueError(f"UV transfer left {missing} runtime vertices unmapped")
    return runtime_uvs


def write_obj(
    path: Path,
    vertices: np.ndarray,
    uvs: np.ndarray | None,
    faces: np.ndarray,
) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write("# Mobile runtime mesh preserving the supplied FBX UV atlas\n")
        output.write("o ImportedSpinner_Runtime\n")
        for x, y, z in vertices:
            output.write(f"v {x:.9g} {y:.9g} {z:.9g}\n")
        if uvs is not None:
            for u, v in uvs:
                output.write(f"vt {u:.9g} {v:.9g}\n")
        for a, b, c in faces + 1:
            if uvs is None:
                output.write(f"f {a} {b} {c}\n")
            else:
                output.write(f"f {a}/{a} {b}/{b} {c}/{c}\n")


def pack_metallic_smoothness(metallic_path: Path, roughness_path: Path, output_path: Path) -> None:
    metallic = Image.open(metallic_path).convert("L")
    roughness = Image.open(roughness_path).convert("L")
    if metallic.size != roughness.size:
        raise ValueError(
            f"Metallic and roughness dimensions differ: {metallic.size} vs {roughness.size}"
        )
    black = Image.new("L", metallic.size, 0)
    smoothness = ImageOps.invert(roughness)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.merge("RGBA", (metallic, black, black, smoothness)).save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--triangles", type=int, default=180_000)
    parser.add_argument("--metallic", type=Path)
    parser.add_argument("--roughness", type=Path)
    parser.add_argument("--packed-metallic-smoothness", type=Path)
    parser.add_argument(
        "--uniform-smooth",
        action="store_true",
        help="Weld texture seams and remove high-frequency geometric noise for a uniform material",
    )
    parser.add_argument("--smoothing-iterations", type=int, default=8)
    args = parser.parse_args()

    source_vertices, source_uvs, source_faces = load_obj(args.source)
    if args.uniform_smooth:
        import trimesh

        welded = trimesh.Trimesh(
            vertices=source_vertices,
            faces=source_faces,
            process=True,
        )
        runtime_vertices, runtime_faces = fast_simplification.simplify(
            np.asarray(welded.vertices),
            np.asarray(welded.faces),
            target_count=args.triangles,
            agg=7,
        )
        smoothed = trimesh.Trimesh(
            vertices=runtime_vertices,
            faces=runtime_faces,
            process=True,
        )
        trimesh.smoothing.filter_humphrey(
            smoothed,
            alpha=0.1,
            beta=0.45,
            iterations=args.smoothing_iterations,
        )
        replay_vertices = np.asarray(smoothed.vertices)
        replay_faces = np.asarray(smoothed.faces)
        runtime_uvs = None
    else:
        runtime_vertices, runtime_faces, collapses = fast_simplification.simplify(
            source_vertices,
            source_faces,
            target_count=args.triangles,
            agg=7,
            return_collapses=True,
        )
        replay_vertices, replay_faces, source_to_runtime = (
            fast_simplification.replay_simplification(
                source_vertices.astype(np.float32),
                source_faces,
                collapses,
            )
        )
        if replay_faces.shape != runtime_faces.shape:
            raise ValueError(
                f"Simplification replay changed face count: {runtime_faces.shape} -> {replay_faces.shape}"
            )
        runtime_uvs = transfer_uvs(
            source_vertices,
            source_uvs,
            replay_vertices,
            source_to_runtime,
        )

    args.destination.parent.mkdir(parents=True, exist_ok=True)
    write_obj(args.destination, replay_vertices, runtime_uvs, replay_faces)
    packed_inputs = (args.metallic, args.roughness, args.packed_metallic_smoothness)
    if any(packed_inputs) and not all(packed_inputs):
        raise ValueError(
            "--metallic, --roughness and --packed-metallic-smoothness must be supplied together"
        )
    if all(packed_inputs):
        pack_metallic_smoothness(
            args.metallic,
            args.roughness,
            args.packed_metallic_smoothness,
        )
    print(
        f"source_vertices={source_vertices.shape[0]} "
        f"source_triangles={source_faces.shape[0]} "
        f"runtime_vertices={replay_vertices.shape[0]} "
        f"runtime_triangles={replay_faces.shape[0]} "
        f"uvs={0 if runtime_uvs is None else runtime_uvs.shape[0]}"
    )


if __name__ == "__main__":
    main()
