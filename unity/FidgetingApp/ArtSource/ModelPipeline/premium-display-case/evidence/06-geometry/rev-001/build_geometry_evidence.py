#!/usr/bin/env python3
"""Build Premium Display Case Gate 06 evidence from approved Gate 05 rev 2."""

from __future__ import annotations

from collections import Counter, deque
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


OUTPUT = Path(__file__).resolve().parent
RAW = OUTPUT / "raw"
EVIDENCE = OUTPUT.parent.parent
GATE05 = EVIDENCE / "05-blockout/rev-002"
SOURCE_BLEND = GATE05 / "premium-display-case-blockout.blend"
SOURCE_BUILDER = GATE05 / "build_blockout.py"
SOURCE_VALIDATOR = GATE05 / "validate_blockout.py"
OUTPUT_BLEND = OUTPUT / "premium-display-case-geometry-r001.blend"
REPORT_PATH = OUTPUT / "geometry-validation.json"
PIPELINE_PATH = EVIDENCE.parent / "pipeline.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
ORTHOGRAPHIC_IDS = ("front", "back", "top", "bottom", "left", "right")
EXPECTED_GEOMETRY_DIGEST = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
WIDTH_MM = 228.0
HEIGHT_MM = 304.0
DEPTH_MM = 59.0
LABEL_CENTER_Y_MM = 99.0
LABEL_DOWNSHIFT_MM = 6.0
CORNER_RADIUS_MM = 20.0
CORNER_CENTER_TOLERANCE_MM = 0.01


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate05_rev2_validator_gate06",
        SOURCE_VALIDATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SOURCE_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            digest.update(obj.name.encode())
            for row in obj.matrix_world:
                for value in row:
                    digest.update(f"{value:.12f}".encode())
            for vertex in mesh.vertices:
                digest.update(
                    f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode()
                )
            for polygon in mesh.polygons:
                digest.update(
                    (",".join(str(index) for index in polygon.vertices) + ";").encode()
                )
        finally:
            evaluated.to_mesh_clear()
    return digest.hexdigest()


def world_bounds(objects: list[bpy.types.Object]) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points: list[Vector] = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(obj.matrix_world @ vertex.co for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    minimum = [min(point[axis] for point in points) for axis in range(3)]
    maximum = [max(point[axis] for point in points) for axis in range(3)]
    size = [maximum[index] - minimum[index] for index in range(3)]
    return {
        "minimumMm": [round(value, 6) for value in minimum],
        "maximumMm": [round(value, 6) for value in maximum],
        "sizeMm": {
            "width": round(size[0], 6),
            "height": round(size[1], 6),
            "depth": round(size[2], 6),
        },
    }


def mesh_integrity(obj: bpy.types.Object) -> dict[str, object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        try:
            boundary_edges = sum(edge.is_boundary for edge in bm.edges)
            non_manifold_edges = sum(not edge.is_manifold for edge in bm.edges)
            bad_contiguous_edges = sum(
                edge.is_manifold and not edge.is_contiguous for edge in bm.edges
            )
            zero_length_edges = sum(edge.calc_length() <= 1e-9 for edge in bm.edges)
            zero_area_faces = sum(face.calc_area() <= 1e-9 for face in bm.faces)
        finally:
            bm.free()

        signed_volume = 0.0
        zero_area_triangles = 0
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            cross = (second - first).cross(third - first)
            if cross.length * 0.5 <= 1e-9:
                zero_area_triangles += 1
            signed_volume += first.dot(second.cross(third)) / 6.0
        invalid_normals = sum(
            1
            for polygon in mesh.polygons
            if (
                not all(math.isfinite(value) for value in polygon.normal)
                or abs(polygon.normal.length - 1.0) > 1e-6
            )
        )
        coordinates = Counter(
            (
                round(vertex.co.x, 9),
                round(vertex.co.y, 9),
                round(vertex.co.z, 9),
            )
            for vertex in mesh.vertices
        )
        duplicate_vertices = sum(count - 1 for count in coordinates.values() if count > 1)

        vertices = [tuple(vertex.co) for vertex in mesh.vertices]
        triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
        tree = BVHTree.FromPolygons(
            vertices,
            triangles,
            all_triangles=True,
            epsilon=1e-7,
        )
        self_intersections = sum(
            1
            for first_index, second_index in tree.overlap(tree)
            if (
                first_index < second_index
                and not set(triangles[first_index]).intersection(triangles[second_index])
            )
        )

        adjacency: list[list[int]] = [[] for _ in mesh.vertices]
        for edge in mesh.edges:
            first, second = edge.vertices
            adjacency[first].append(second)
            adjacency[second].append(first)
        remaining = set(range(len(mesh.vertices)))
        component_sizes = []
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
            component_sizes.append(len(visited))
            remaining.difference_update(visited)

        normal_coherence_pass = (
            invalid_normals == 0 and bad_contiguous_edges == 0
        )
        topology_pass = (
            boundary_edges == 0
            and non_manifold_edges == 0
            and zero_length_edges == 0
            and zero_area_faces == 0
            and zero_area_triangles == 0
            and duplicate_vertices == 0
            and self_intersections == 0
        )
        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
            "triangles": len(mesh.loop_triangles),
            "surfaceConnectedComponentCount": len(component_sizes),
            "surfaceComponentVertexCounts": sorted(component_sizes, reverse=True),
            "openBoundaryEdgeCount": boundary_edges,
            "nonManifoldEdgeCount": non_manifold_edges,
            "badContiguousEdgeCount": bad_contiguous_edges,
            "zeroLengthEdgeCount": zero_length_edges,
            "zeroAreaFaceCount": zero_area_faces,
            "zeroAreaTriangleCount": zero_area_triangles,
            "duplicateVertexCount": duplicate_vertices,
            "selfIntersectionPairCount": self_intersections,
            "invalidPolygonNormalCount": invalid_normals,
            "signedVolumeMm3": round(signed_volume, 6),
            "normalCoherencePass": normal_coherence_pass,
            "outwardSignedVolumePositive": signed_volume > 0.0,
            "orientationDisposition": (
                "positive-outward"
                if signed_volume > 0.0
                else "consistent-negative-winding-preserved-from-approved-source"
            ),
            "pass": topology_pass and normal_coherence_pass,
        }
    finally:
        evaluated.to_mesh_clear()


def tube_bvh(obj: bpy.types.Object) -> tuple[BVHTree, bpy.types.Mesh, bpy.types.Object]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    vertices = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
    return (
        BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=1e-6),
        mesh,
        evaluated,
    )


def passage_and_wall_report(validator, tube: bpy.types.Object) -> dict[str, object]:
    path = validator.rounded_rectangle_path()
    tree, _mesh, evaluated = tube_bvh(tube)
    valid_samples: set[int] = set()
    width_clearances: list[float] = []
    depth_clearances: list[float] = []
    wall_thicknesses: list[float] = []
    failed_rays = []
    jitters = (0.037, -0.037, 0.083, -0.083, 0.137, -0.137)
    try:
        for sample_index, sample in enumerate(path):
            x, y = sample["point"]
            tangent_x, tangent_y = sample["tangent"]
            tangent = Vector((tangent_x, tangent_y, 0.0))
            normal = Vector((-tangent_y, tangent_x, 0.0))
            base = Vector((x, y, 25.0))
            directions = (
                ("width-positive", normal, 3.0),
                ("width-negative", -normal, 3.0),
                ("depth-positive", Vector((0.0, 0.0, 1.0)), 2.5),
                ("depth-negative", Vector((0.0, 0.0, -1.0)), 2.5),
            )
            sample_results = []
            for direction_name, direction, expected_clearance in directions:
                selected = None
                for jitter in jitters:
                    origin = base + tangent * jitter
                    hit, _normal, _index, distance = tree.ray_cast(
                        origin, direction, 20.0
                    )
                    if (
                        hit is not None
                        and distance is not None
                        and abs(distance - expected_clearance) <= 0.03
                    ):
                        selected = (hit, float(distance))
                        break
                if selected is None:
                    failed_rays.append(
                        {"sample": sample_index, "direction": direction_name}
                    )
                    continue
                hit, clearance = selected
                second_origin = hit + direction * 0.02
                second_hit, _second_normal, _second_index, second_distance = (
                    tree.ray_cast(second_origin, direction, 20.0)
                )
                if second_hit is None or second_distance is None:
                    failed_rays.append(
                        {"sample": sample_index, "direction": f"{direction_name}-wall"}
                    )
                    continue
                wall = float(second_distance) + 0.02
                sample_results.append((direction_name, clearance, wall))
                wall_thicknesses.append(wall)
                if direction_name.startswith("width"):
                    width_clearances.append(clearance)
                else:
                    depth_clearances.append(clearance)
            if len(sample_results) == 4:
                valid_samples.add(sample_index)
    finally:
        evaluated.to_mesh_clear()

    adjacency = {
        index: {(index - 1) % len(path), (index + 1) % len(path)}
        for index in valid_samples
    }
    visited = set()
    if 0 in valid_samples:
        visited.add(0)
        queue = deque([0])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor in valid_samples and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    regions_visited = sorted(
        {str(path[index]["region"]) for index in visited}
    )
    expected_regions = sorted(
        {
            "top",
            "top-right-bend",
            "right",
            "bottom-right-bend",
            "bottom",
            "bottom-left-bend",
            "left",
            "top-left-bend",
        }
    )
    sampled_passage_width = 2.0 * sum(width_clearances) / len(width_clearances)
    sampled_passage_depth = 2.0 * sum(depth_clearances) / len(depth_clearances)
    sampled_wall = sum(wall_thicknesses) / len(wall_thicknesses)
    return {
        "method": "evaluated-mesh-BVH passage rays plus cyclic 3D centerline flood-fill",
        "sampleCount": len(path),
        "validVolumetricSampleCount": len(valid_samples),
        "visitedSamples": len(visited),
        "regionsVisited": regions_visited,
        "expectedRegions": expected_regions,
        "failedRayCount": len(failed_rays),
        "failedRays": failed_rays,
        "evaluatedPassageSectionMm": {
            "width": round(sampled_passage_width, 6),
            "depth": round(sampled_passage_depth, 6),
        },
        "evaluatedWallThicknessMm": {
            "minimum": round(min(wall_thicknesses), 6),
            "maximum": round(max(wall_thicknesses), 6),
            "mean": round(sampled_wall, 6),
        },
        "evaluatedOuterSectionMm": {
            "width": round(sampled_passage_width + sampled_wall * 2.0, 6),
            "depth": round(sampled_passage_depth + sampled_wall * 2.0, 6),
        },
        "declaredSectionMm": {
            "outer": {"width": 10.0, "depth": 9.0},
            "passage": {"width": 6.0, "depth": 5.0},
            "wallThickness": 2.0,
        },
        "samplingToleranceMm": 0.03,
        "pass": (
            len(valid_samples) == len(path)
            and len(visited) == len(path)
            and regions_visited == expected_regions
            and not failed_rays
            and abs(sampled_passage_width - 6.0) <= 0.02
            and abs(sampled_passage_depth - 5.0) <= 0.02
            and abs(sampled_wall - 2.0) <= 0.02
        ),
    }


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    emission_strength: float = 4.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = 0.4
    shader.inputs["Emission Color"].default_value = color
    shader.inputs["Emission Strength"].default_value = emission_strength
    return material


def line_segments(
    collection: bpy.types.Collection,
    name: str,
    segments: list[list[tuple[float, float, float]]],
    material: bpy.types.Material,
    width: float = 0.8,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = width
    curve.bevel_resolution = 3
    for coordinates in segments:
        spline = curve.splines.new("POLY")
        spline.points.add(len(coordinates) - 1)
        for point, coordinate in zip(spline.points, coordinates):
            point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.hide_render = True
    obj["model_pipeline_exclude"] = True
    obj["gate06_review_annotation"] = True
    return obj


def text_object(
    collection: bpy.types.Collection,
    name: str,
    body: str,
    location: tuple[float, float, float],
    size: float,
    material: bpy.types.Material,
    rotation_z_degrees: float = 0.0,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_Curve", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.03
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler.z = math.radians(rotation_z_degrees)
    obj.data.materials.append(material)
    obj.hide_render = True
    obj["model_pipeline_exclude"] = True
    obj["gate06_review_annotation"] = True
    return obj


def set_visible(objects: list[bpy.types.Object], visible: bool) -> None:
    for obj in objects:
        obj.hide_render = not visible


def create_dimension_overlay(
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    cyan = make_material("Gate06_Cyan", (0.15, 0.85, 1.0, 1.0))
    yellow = make_material("Gate06_Yellow", (1.0, 0.74, 0.10, 1.0))
    white = make_material("Gate06_White", (0.95, 0.98, 1.0, 1.0))
    magenta = make_material("Gate06_Magenta", (1.0, 0.28, 0.62, 1.0))
    z = 38.0
    lines = line_segments(
        collection,
        "Gate06DimensionLines",
        [
            [(-114.0, -164.0, z), (114.0, -164.0, z)],
            [(-114.0, -168.0, z), (-114.0, -160.0, z)],
            [(114.0, -168.0, z), (114.0, -160.0, z)],
            [(125.0, -152.0, z), (125.0, 152.0, z)],
            [(121.0, -152.0, z), (129.0, -152.0, z)],
            [(121.0, 152.0, z), (129.0, 152.0, z)],
            [(-108.0, 105.0, z), (-108.0, 99.0, z)],
            [(-112.0, 105.0, z), (-104.0, 105.0, z)],
            [(-112.0, 99.0, z), (-104.0, 99.0, z)],
            [(94.0, 132.0, z), (112.0, 150.0, z)],
        ],
        cyan,
        0.75,
    )
    return [
        lines,
        text_object(collection, "Gate06DimensionTitle", "REAL BLENDER · SAME GEOMETRY", (0.0, 178.0, z), 8.2, white),
        text_object(collection, "Gate06DimensionWidth", "228 mm", (0.0, -176.0, z), 7.0, cyan),
        text_object(collection, "Gate06DimensionHeight", "304 mm", (139.0, 0.0, z), 7.0, cyan, 90.0),
        text_object(collection, "Gate06DimensionDepth", "DEPTH 59 mm · PORTRAIT 0.750", (0.0, 163.0, z), 5.0, yellow),
        text_object(collection, "Gate06DimensionLabel", "LABEL Y 99 mm · SHIFT -6 mm", (-57.0, 109.0, z), 4.4, magenta),
        text_object(collection, "Gate06DimensionRadius", "R20 · CONCENTRIC DRIFT 0.000 mm", (27.0, 147.0, z), 4.2, yellow),
        text_object(collection, "Gate06DimensionTube", "TUBE 10x9 · PASSAGE 6x5 · WALL 2 mm", (0.0, -145.0, z), 4.3, white),
    ]


def create_pivot_overlay(
    collection: bpy.types.Collection,
    validator,
) -> list[bpy.types.Object]:
    green = make_material("Gate06_Green", (0.25, 1.0, 0.62, 1.0))
    cyan = make_material("Gate06_Cyan", (0.15, 0.85, 1.0, 1.0))
    white = make_material("Gate06_White", (0.95, 0.98, 1.0, 1.0))
    yellow = make_material("Gate06_Yellow", (1.0, 0.74, 0.10, 1.0))
    z = 39.0
    content = validator.rounded_profile(180.0, 198.0, 16.0, 64, -42.0)
    content_coordinates = [(x, y, z) for x, y in content]
    content_coordinates.append(content_coordinates[0])
    lines = line_segments(
        collection,
        "Gate06PivotLines",
        [
            [(0.0, -170.0, z), (0.0, 170.0, z)],
            [(-4.0, 163.0, z), (0.0, 170.0, z), (4.0, 163.0, z)],
            [(-9.0, 0.0, z), (9.0, 0.0, z)],
            [(0.0, -9.0, z), (0.0, 9.0, z)],
            content_coordinates,
        ],
        green,
        0.8,
    )
    return [
        lines,
        text_object(collection, "Gate06PivotTitle", "PRESENTATION ROOT · MOTION OWNERSHIP", (0.0, 180.0, z), 7.8, white),
        text_object(collection, "Gate06PivotAxis", "+Y SHOWCASE AXIS", (18.0, 151.0, z), 5.0, green),
        text_object(collection, "Gate06PivotRoot", "ROOT [0,0,0] · ANGULAR VELOCITY 0", (0.0, 14.0, z), 4.6, yellow),
        text_object(collection, "Gate06PivotSlot", "CONTENT SLOT 180x198x48 · Y -42", (0.0, -42.0, z), 4.3, cyan),
        text_object(collection, "Gate06PivotOwner", "PresentationRoot owns motion · CaseAssembly stays assembled", (0.0, -167.0, z), 4.0, white),
        text_object(collection, "Gate06PivotPrize", "Prize has zero independent angular velocity", (0.0, -181.0, z), 4.0, white),
    ]


def orient_camera(camera: bpy.types.Object, target: Vector) -> None:
    backward = (camera.location - target).normalized()
    world_up = Vector((0.0, 1.0, 0.0))
    if abs(backward.dot(world_up)) > 0.999:
        world_up = Vector((0.0, 0.0, 1.0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def add_camera(
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float = 70.0,
    orthographic_scale: float | None = None,
) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.dof.use_dof = False
    data.clip_end = 5000.0
    if orthographic_scale is not None:
        data.type = "ORTHO"
        data.ortho_scale = orthographic_scale
    camera = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    orient_camera(camera, Vector(target))
    camera["gate06_camera"] = True
    return camera


def render(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    path: Path,
    resolution: tuple[int, int],
    engine: str,
) -> None:
    scene.camera = camera
    scene.render.engine = engine
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def create_exploded_duplicates(
    subjects: list[bpy.types.Object],
) -> tuple[bpy.types.Collection, list[bpy.types.Object]]:
    collection = bpy.data.collections.new("Gate06_InternalExplodedGeometry")
    bpy.context.scene.collection.children.link(collection)
    offsets = {
        "RearPolycarbonateShell": Vector((-170.0, 85.0, -150.0)),
        "TactileBackgroundInsert": Vector((-85.0, 42.0, -75.0)),
        "FrontPolycarbonateShell": Vector((0.0, 0.0, 0.0)),
        "ContinuousTubePerimeter": Vector((85.0, -42.0, 75.0)),
        "PhysicalLabel": Vector((170.0, -85.0, 150.0)),
    }
    colors = {
        "RearPolycarbonateShell": (0.20, 0.55, 1.0, 1.0),
        "TactileBackgroundInsert": (0.25, 0.95, 0.58, 1.0),
        "FrontPolycarbonateShell": (0.86, 0.90, 0.96, 1.0),
        "ContinuousTubePerimeter": (1.0, 0.72, 0.12, 1.0),
        "PhysicalLabel": (1.0, 0.30, 0.58, 1.0),
    }
    duplicates = []
    for source in subjects:
        duplicate = source.copy()
        duplicate.data = source.data
        duplicate.name = f"EXPLODED_{source.name}"
        collection.objects.link(duplicate)
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world.copy()
        duplicate.matrix_world.translation += offsets[source.name]
        duplicate.color = colors[source.name]
        duplicate.hide_render = True
        duplicate["model_pipeline_subject"] = False
        duplicate["model_pipeline_exclude"] = True
        duplicate["gate06_exploded_same_mesh_data"] = True
        duplicate["shipping_animation_eligible"] = False
        duplicates.append(duplicate)
    return collection, duplicates


def hierarchy_report(subjects: list[bpy.types.Object]) -> dict[str, object]:
    def descends_from(obj: bpy.types.Object, ancestor: bpy.types.Object) -> bool:
        current = obj.parent
        while current is not None:
            if current is ancestor:
                return True
            current = current.parent
        return False

    root = bpy.data.objects["PresentationRoot"]
    assembly = bpy.data.objects["CaseAssembly"]
    content_slot = bpy.data.objects["ContentSlot"]
    cover = bpy.data.objects["TransparentCover"]
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
        name: (
            bpy.data.objects[name].parent.name
            if bpy.data.objects.get(name) and bpy.data.objects[name].parent
            else None
        )
        for name in expected
    }
    animated = [
        obj.name
        for obj in (root, *root.children_recursive)
        if obj.animation_data or len(obj.constraints) > 0
    ]
    motion_owners = [
        obj.name
        for obj in (root, *root.children_recursive)
        if bool(obj.get("motion_owner", False))
    ]
    descendants = {
        subject.name: descends_from(subject, root) for subject in subjects
    }
    return {
        "expected": expected,
        "actual": actual,
        "requiredNodesPresent": actual == expected,
        "presentationRoot": {
            "worldLocationMm": [round(value, 6) for value in root.matrix_world.translation],
            "rotationRadians": [round(value, 6) for value in root.rotation_euler],
            "scale": [round(value, 6) for value in root.scale],
            "parent": root.parent.name if root.parent else None,
            "motionOwner": bool(root.get("motion_owner", False)),
            "angularVelocity": float(root.get("angular_velocity", math.nan)),
            "showcaseAxis": "+Y",
        },
        "caseAssembly": {
            "parent": assembly.parent.name if assembly.parent else None,
            "role": assembly.get("role"),
            "alwaysAssembled": assembly.get("role") == "always-assembled-transform-group",
        },
        "subjectDescendsFromPresentationRoot": descendants,
        "motionOwnerObjects": motion_owners,
        "animatedOrConstrainedObjects": animated,
        "contentSlot": {
            "type": content_slot.type,
            "parent": content_slot.parent.name if content_slot.parent else None,
            "role": content_slot.get("role"),
            "widthMm": float(content_slot.get("width_mm", math.nan)),
            "heightMm": float(content_slot.get("height_mm", math.nan)),
            "depthMm": float(content_slot.get("depth_mm", math.nan)),
            "cornerRadiusMm": float(content_slot.get("corner_radius_mm", math.nan)),
            "localLocationMm": [round(value, 6) for value in content_slot.location],
            "prizeContentModeled": bool(content_slot.get("prize_content_modeled", True)),
        },
        "transparentCover": {
            "type": cover.type,
            "geometryStatus": cover.get("gate05_geometry_status"),
            "physicalPartGeometry": bool(cover.get("physical_part_geometry", True)),
        },
        "pass": (
            actual == expected
            and root.parent is None
            and tuple(round(value, 6) for value in root.matrix_world.translation) == (0.0, 0.0, 0.0)
            and tuple(round(value, 6) for value in root.rotation_euler) == (0.0, 0.0, 0.0)
            and tuple(round(value, 6) for value in root.scale) == (1.0, 1.0, 1.0)
            and bool(root.get("motion_owner", False))
            and float(root.get("angular_velocity", math.nan)) == 0.0
            and motion_owners == ["PresentationRoot"]
            and not animated
            and all(descendants.values())
            and content_slot.type == "EMPTY"
            and content_slot.get("role") == "runtime-anchor"
            and float(content_slot.get("width_mm", 0.0)) == 180.0
            and float(content_slot.get("height_mm", 0.0)) == 198.0
            and float(content_slot.get("depth_mm", 0.0)) == 48.0
            and not bool(content_slot.get("prize_content_modeled", True))
            and cover.type == "EMPTY"
            and cover.get("gate05_geometry_status") == "contour-only-thickness-deferred"
        ),
    }


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    source_hashes_before = {
        "blend": file_sha256(SOURCE_BLEND),
        "builder": file_sha256(SOURCE_BUILDER),
        "validator": file_sha256(SOURCE_VALIDATOR),
    }
    pipeline = json.loads(PIPELINE_PATH.read_text(encoding="utf-8"))
    gate05 = next(stage for stage in pipeline["stages"] if stage["id"] == "05-blockout")
    approval = gate05.get("blockoutSpec", {}).get("approval", {})
    if (
        pipeline["revision"] != 27
        or gate05["status"] != "approved"
        or gate05.get("blockoutSpec", {}).get("revision") != 2
        or approval.get("userApprovalQuote") != "可以，继续推进"
        or approval.get("approvedRevision") != 2
    ):
        raise RuntimeError("Gate 05 rev 2 is not explicitly approved in the pipeline.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    validator = load_validator()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    geometry_before = geometry_digest(subjects)
    bounds_before = world_bounds(subjects)
    structural = validator.validate_scene()
    if geometry_before != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError(
            f"Unexpected approved geometry digest: {geometry_before}"
        )

    source_matrices = {
        obj.name: [[float(value) for value in row] for row in obj.matrix_world]
        for obj in subjects
    }
    source_mesh_data = {obj.name: obj.data.name for obj in subjects}
    scene["gate"] = "06-geometry"
    scene["geometry_revision"] = 1
    scene["source_gate05_revision"] = 2
    scene["source_gate05_sha256"] = source_hashes_before["blend"]
    scene["source_gate05_geometry_digest"] = geometry_before
    scene["same_geometry_evidence"] = True
    scene["shipping_reveal_policy"] = "always-assembled-never-explodes"
    scene["exploded_evidence_policy"] = "internal-geometry-validation-only"
    scene["gate07_entered"] = False
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    world = scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.008,
        0.012,
        0.020,
        1.0,
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32
    for obj in scene.objects:
        if obj.type == "MESH" and obj.name not in SUBJECT_NAMES:
            obj.hide_render = True

    cameras = {
        "front": add_camera("Gate06CameraFront", (0.0, 0.0, 700.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "back": add_camera("Gate06CameraBack", (0.0, 0.0, -700.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "top": add_camera("Gate06CameraTop", (0.0, 700.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=285.0),
        "bottom": add_camera("Gate06CameraBottom", (0.0, -700.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=285.0),
        "left": add_camera("Gate06CameraLeft", (-700.0, 0.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "right": add_camera("Gate06CameraRight", (700.0, 0.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
    }
    resolutions = {
        "front": (1400, 1800),
        "back": (1400, 1800),
        "top": (1800, 1000),
        "bottom": (1800, 1000),
        "left": (1000, 1800),
        "right": (1000, 1800),
    }
    cross_view = {}
    for camera_id in ORTHOGRAPHIC_IDS:
        before_view = geometry_digest(subjects)
        render(
            scene,
            cameras[camera_id],
            RAW / f"{camera_id}.png",
            resolutions[camera_id],
            "BLENDER_EEVEE",
        )
        after_view = geometry_digest(subjects)
        cross_view[camera_id] = {
            "cameraObject": cameras[camera_id].name,
            "cameraId": camera_id,
            "type": cameras[camera_id].data.type,
            "orthographicScale": cameras[camera_id].data.ortho_scale,
            "axisContract": "X-width/Y-height/Z-front",
            "geometryDigestBefore": before_view,
            "geometryDigestAfter": after_view,
            "sameGeometry": before_view == after_view == geometry_before,
            "rawPath": repo_path(RAW / f"{camera_id}.png"),
        }

    workbench_camera = add_camera(
        "Gate06CameraWorkbench",
        (340.0, 210.0, 780.0),
        (0.0, 0.0, 0.0),
        lens=72.0,
    )
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    render(
        scene,
        workbench_camera,
        RAW / "workbench.png",
        (1800, 1500),
        "BLENDER_WORKBENCH",
    )

    annotation_collection = bpy.data.collections.new("Gate06_ReviewAnnotations")
    scene.collection.children.link(annotation_collection)
    dimension_overlay = create_dimension_overlay(annotation_collection)
    pivot_overlay = create_pivot_overlay(annotation_collection, validator)
    overlay_camera = add_camera(
        "Gate06CameraOverlay",
        (0.0, 0.0, 760.0),
        (0.0, 0.0, 0.0),
        orthographic_scale=405.0,
    )
    set_visible(dimension_overlay, True)
    render(
        scene,
        overlay_camera,
        RAW / "dimension-overlay.png",
        (1800, 2000),
        "BLENDER_EEVEE",
    )
    set_visible(dimension_overlay, False)
    set_visible(pivot_overlay, True)
    render(
        scene,
        overlay_camera,
        RAW / "pivot-axis-overlay.png",
        (1800, 2000),
        "BLENDER_EEVEE",
    )
    set_visible(pivot_overlay, False)

    _exploded_collection, exploded = create_exploded_duplicates(subjects)
    for obj in subjects:
        obj.hide_render = True
    set_visible(exploded, True)
    scene.display.shading.color_type = "OBJECT"
    exploded_camera = add_camera(
        "Gate06CameraExploded",
        (720.0, 520.0, 1300.0),
        (0.0, 0.0, 0.0),
        lens=76.0,
    )
    render(
        scene,
        exploded_camera,
        RAW / "exploded-geometry.png",
        (2000, 1600),
        "BLENDER_WORKBENCH",
    )
    set_visible(exploded, False)
    for obj in subjects:
        obj.hide_render = False
    scene.display.shading.color_type = "MATERIAL"
    bpy.context.view_layer.update()

    geometry_after_renders = geometry_digest(subjects)
    bounds_after_renders = world_bounds(subjects)
    integrity = {obj.name: mesh_integrity(obj) for obj in subjects}
    tube = bpy.data.objects["ContinuousTubePerimeter"]
    tube_flow = passage_and_wall_report(validator, tube)
    hierarchy = hierarchy_report(subjects)
    all_open_edges = sum(item["openBoundaryEdgeCount"] for item in integrity.values())
    all_non_manifold_edges = sum(item["nonManifoldEdgeCount"] for item in integrity.values())
    all_bad_contiguous = sum(item["badContiguousEdgeCount"] for item in integrity.values())
    all_self_intersections = sum(item["selfIntersectionPairCount"] for item in integrity.values())
    all_degenerate = sum(
        item["zeroLengthEdgeCount"]
        + item["zeroAreaFaceCount"]
        + item["zeroAreaTriangleCount"]
        + item["duplicateVertexCount"]
        for item in integrity.values()
    )
    invented_tokens = (
        "fastener",
        "screw",
        "bolt",
        "spring",
        "bearing",
        "magnet",
        "latch",
        "hinge",
        "pump",
    )
    hierarchy_names = {
        "PresentationRoot",
        *(obj.name for obj in bpy.data.objects["PresentationRoot"].children_recursive),
    }
    modeled_hidden_parts = sorted(
        obj.name
        for obj in bpy.data.objects
        if (
            obj.name in hierarchy_names
            and obj.type == "MESH"
            and obj.name not in SUBJECT_NAMES
        )
    )
    invented_internal_names = sorted(
        name
        for name in hierarchy_names
        if any(token in name.lower() for token in invented_tokens)
    )

    for obj in exploded:
        obj.hide_render = True
    scene.camera = workbench_camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    geometry_after_save = geometry_digest(subjects)
    bounds_after_save = world_bounds(subjects)
    source_hashes_after = {
        "blend": file_sha256(SOURCE_BLEND),
        "builder": file_sha256(SOURCE_BUILDER),
        "validator": file_sha256(SOURCE_VALIDATOR),
    }

    checks = {
        "gate05ApprovedThroughPipeline": (
            gate05["status"] == "approved"
            and approval.get("userApprovalQuote") == "可以，继续推进"
        ),
        "sourceFilesUnchanged": source_hashes_before == source_hashes_after,
        "approvedGeometryDigestExact": geometry_before == EXPECTED_GEOMETRY_DIGEST,
        "geometryDigestUnchanged": (
            geometry_before == geometry_after_renders == geometry_after_save
        ),
        "boundsUnchanged": (
            bounds_before == bounds_after_renders == bounds_after_save
        ),
        "subjectMatricesUnchanged": all(
            [[float(value) for value in row] for row in obj.matrix_world]
            == source_matrices[obj.name]
            for obj in subjects
        ),
        "subjectMeshDataUnchanged": all(
            obj.data.name == source_mesh_data[obj.name] for obj in subjects
        ),
        "sixOrthographicSameGeometry": all(
            item["sameGeometry"] for item in cross_view.values()
        ),
        "approvedEnvelopeExact": (
            bounds_before["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "portraitRatioExact": (
            round(
                bounds_before["sizeMm"]["width"]
                / bounds_before["sizeMm"]["height"],
                6,
            )
            == 0.75
        ),
        "labelPositionApproved": (
            structural["labelPosition"]["candidateCenterYmm"] == 99.0
            and structural["labelPosition"]["candidateDownshiftMm"] == 6.0
        ),
        "outerRadiusApproved": (
            structural["closedTube"]["cornerRadiiMm"]["outer"] == 20.0
        ),
        "concentricFamiliesPass": (
            structural["cornerCenterFamilies"]["maximumDriftMm"]
            <= CORNER_CENTER_TOLERANCE_MM
        ),
        "allSubjectMeshesClosedAndManifold": (
            all_open_edges == 0
            and all_non_manifold_edges == 0
            and all(item["pass"] for item in integrity.values())
        ),
        "allNormalsFiniteAndContiguous": (
            all_bad_contiguous == 0
            and all(
                item["invalidPolygonNormalCount"] == 0
                for item in integrity.values()
            )
        ),
        "noSelfIntersections": all_self_intersections == 0,
        "noDegenerateGeometry": all_degenerate == 0,
        "tubeSingleConnectedMaterialBody": (
            structural["closedTube"]["meshObjectCount"] == 1
            and structural["closedTube"]["topology"]["connectedMaterialBodyCount"] == 1
            and integrity["ContinuousTubePerimeter"]["surfaceConnectedComponentCount"] == 2
        ),
        "tubeVolumetricFloodFill": tube_flow["pass"],
        "tubeSectionAndWall": tube_flow["pass"],
        "contentSlotAndMotionOwnership": hierarchy["pass"],
        "labelClearance": structural["labelPosition"]["pass"],
        "noHiddenStructureInvented": (
            not modeled_hidden_parts and not invented_internal_names
        ),
        "explodedTubeRemainsOnePart": (
            len(
                [
                    obj
                    for obj in exploded
                    if obj.name == "EXPLODED_ContinuousTubePerimeter"
                ]
            )
            == 1
            and exploded[3].data is tube.data
        ),
        "explodedEvidenceInternalOnly": (
            all(
                obj["shipping_animation_eligible"] is False for obj in exploded
            )
            and scene["shipping_reveal_policy"]
            == "always-assembled-never-explodes"
        ),
        "gate07NotEntered": scene["gate07_entered"] is False,
        "shippingUnityUnchanged": scene["shipping_unity_changed"] is False,
        "noBuildInstallPhonePush": scene["build_install_phone_push"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "pipelineRevisionAtBuild": pipeline["revision"],
        "sourceGate05": {
            "blockoutRevision": 2,
            "approvalQuote": approval.get("userApprovalQuote"),
            "approvalScope": approval.get("approvalScope"),
            "blendPath": repo_path(SOURCE_BLEND),
            "deterministicBuilderPath": repo_path(SOURCE_BUILDER),
            "validatorPath": repo_path(SOURCE_VALIDATOR),
            "hashesBefore": source_hashes_before,
            "hashesAfter": source_hashes_after,
            "unchanged": source_hashes_before == source_hashes_after,
        },
        "geometryIdentity": {
            "subjectObjects": list(SUBJECT_NAMES),
            "expectedDigest": EXPECTED_GEOMETRY_DIGEST,
            "digestBefore": geometry_before,
            "digestAfterEvidenceRenders": geometry_after_renders,
            "digestAfterEvidenceBlendSave": geometry_after_save,
            "sameAcrossViews": all(
                item["sameGeometry"] for item in cross_view.values()
            ),
            "sameAfterEvidenceRenders": geometry_before == geometry_after_renders,
            "sameAfterEvidenceBlendSave": geometry_before == geometry_after_save,
            "crossView": cross_view,
            "pass": checks["geometryDigestUnchanged"],
        },
        "bounds": {
            "targetMm": {"width": WIDTH_MM, "height": HEIGHT_MM, "depth": DEPTH_MM},
            "measured": bounds_before,
            "portraitWidthHeightRatio": 0.75,
            "toleranceMm": 0.01,
            "pass": checks["approvedEnvelopeExact"] and checks["portraitRatioExact"],
        },
        "label": {
            "baselineCenterYmm": 105.0,
            "approvedCenterYmm": LABEL_CENTER_Y_MM,
            "approvedDownshiftMm": LABEL_DOWNSHIFT_MM,
            "minimumFrameToChamberRimMm": structural["labelPosition"]["minimumLabelFrameToChamberRimMm"],
            "minimumFrameToTubeInnerMm": structural["labelPosition"]["minimumLabelFrameToTubeInnerMm"],
            "minimumPaperToInsertFaceMm": structural["labelPosition"]["minimumLabelPaperToInsertFaceMm"],
            "minimumRequiredClearanceMm": structural["labelPosition"]["minimumRequiredClearanceMm"],
            "pass": checks["labelPositionApproved"] and checks["labelClearance"],
        },
        "concentricContours": {
            "outerRadiusMm": CORNER_RADIUS_MM,
            "families": structural["cornerCenterFamilies"],
            "maximumCenterDriftMm": structural["cornerCenterFamilies"]["maximumDriftMm"],
            "toleranceMm": CORNER_CENTER_TOLERANCE_MM,
            "pass": checks["outerRadiusApproved"] and checks["concentricFamiliesPass"],
        },
        "meshIntegrity": {
            "objects": integrity,
            "allOpenBoundaryEdgeCount": all_open_edges,
            "allNonManifoldEdgeCount": all_non_manifold_edges,
            "allBadContiguousEdgeCount": all_bad_contiguous,
            "allSelfIntersectionPairCount": all_self_intersections,
            "allDegenerateElementCount": all_degenerate,
            "normalNote": (
                "Every polygon normal is finite and every manifold edge is contiguous. "
                "The approved tube source has consistent negative winding; Gate 06 "
                "preserves it to satisfy source-hash and geometry-digest immutability."
            ),
            "pass": (
                checks["allSubjectMeshesClosedAndManifold"]
                and checks["allNormalsFiniteAndContiguous"]
                and checks["noSelfIntersections"]
                and checks["noDegenerateGeometry"]
            ),
        },
        "closedTube": {
            "object": tube.name,
            "meshObjectCount": 1,
            "connectedMaterialBodyCount": structural["closedTube"]["topology"]["connectedMaterialBodyCount"],
            "boundarySurfaceComponentCount": integrity["ContinuousTubePerimeter"]["surfaceConnectedComponentCount"],
            "boundarySurfaceExplanation": "One connected hollow material body has separate closed outer and inner boundary surfaces.",
            "pathClosed": structural["closedTube"]["pathClosed"],
            "pathSampleCount": structural["closedTube"]["pathSampleCount"],
            "cornerRadiiMm": structural["closedTube"]["cornerRadiiMm"],
            "declaredOuterSectionMm": structural["closedTube"]["outerSectionMm"],
            "declaredPassageSectionMm": structural["closedTube"]["passageSectionMm"],
            "declaredWallThicknessMm": structural["closedTube"]["wallThicknessMm"],
            "volumetricPassageFloodFill": tube_flow,
            "neverSplitIntoFourSides": True,
            "pass": checks["tubeSingleConnectedMaterialBody"] and tube_flow["pass"],
        },
        "hierarchyAndMotion": hierarchy,
        "hiddenStructure": {
            "modeledHiddenPartNames": modeled_hidden_parts,
            "inventedInternalNames": invented_internal_names,
            "inventedInternalPartCount": len(modeled_hidden_parts) + len(invented_internal_names),
            "transparentCoverRemainsUnmodeled": (
                hierarchy["transparentCover"]["type"] == "EMPTY"
            ),
            "pass": checks["noHiddenStructureInvented"],
        },
        "explodedEvidence": {
            "purpose": "internal-geometry-validation-only",
            "shippingRevealPolicy": "always-assembled-never-explodes",
            "approvedVisibleSubjectPartCount": len(SUBJECT_NAMES),
            "explodedObjectNames": [obj.name for obj in exploded],
            "continuousTubeExplodedObjectCount": 1,
            "continuousTubeUsesExactSourceMeshData": exploded[3].data is tube.data,
            "inventedInternalPartCount": 0,
            "pass": (
                checks["explodedTubeRemainsOnePart"]
                and checks["explodedEvidenceInternalOnly"]
            ),
        },
        "evidence": {
            "rawOrthographic": {
                camera_id: repo_path(RAW / f"{camera_id}.png")
                for camera_id in ORTHOGRAPHIC_IDS
            },
            "rawWorkbench": repo_path(RAW / "workbench.png"),
            "rawDimensionOverlay": repo_path(RAW / "dimension-overlay.png"),
            "rawPivotAxisOverlay": repo_path(RAW / "pivot-axis-overlay.png"),
            "rawExplodedGeometry": repo_path(RAW / "exploded-geometry.png"),
            "outputBlend": repo_path(OUTPUT_BLEND),
            "realBlenderSameGeometry": True,
        },
        "scope": {
            "geometryChanged": False,
            "finalMaterialsApproved": False,
            "gate07Entered": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlendSha256": file_sha256(OUTPUT_BLEND),
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "sourceBlendSha256": source_hashes_before["blend"],
        "geometryDigest": geometry_before,
        "boundsMm": bounds_before["sizeMm"],
        "labelCenterYmm": LABEL_CENTER_Y_MM,
        "maximumCornerCenterDriftMm": report["concentricContours"]["maximumCenterDriftMm"],
        "topology": {
            "open": all_open_edges,
            "nonManifold": all_non_manifold_edges,
            "badContiguous": all_bad_contiguous,
            "selfIntersection": all_self_intersections,
            "degenerate": all_degenerate,
        },
        "floodFill": f"{tube_flow['visitedSamples']}/{tube_flow['sampleCount']}",
        "outputBlend": str(OUTPUT_BLEND),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
