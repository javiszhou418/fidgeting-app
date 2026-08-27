"""Export the authoritative 72-segment smooth-normal product."""

from pathlib import Path

import bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "rev-001/export_fan_card.py"


def _signed_area(vertices) -> float:
    return 0.5 * sum(
        left.co.x * right.co.y - right.co.x * left.co.y
        for left, right in zip(vertices, vertices[1:] + vertices[:1])
    )


def _order_boundary_loops(edges):
    unused = set(edges)
    loops = []
    while unused:
        first = unused.pop()
        start = first.verts[0]
        current = first.verts[1]
        previous = start
        loop = [start, current]
        while current != start:
            candidates = [
                edge for edge in current.link_edges
                if edge in unused and previous in edge.verts
                    or edge in unused
            ]
            next_edge = next(
                edge for edge in candidates
                if edge.other_vert(current) != previous
                or len(candidates) == 1
            )
            unused.remove(next_edge)
            following = next_edge.other_vert(current)
            if following == start:
                break
            loop.append(following)
            previous, current = current, following
        loops.append(loop)
    return loops


def _triangle_contains_origin(vertices) -> bool:
    point = (0.0, 0.0)
    triangle = [(vertex.co.x, vertex.co.y) for vertex in vertices]

    def cross(p, a, b):
        return ((p[0] - b[0]) * (a[1] - b[1])
                - (a[0] - b[0]) * (p[1] - b[1]))

    values = (
        cross(point, triangle[0], triangle[1]),
        cross(point, triangle[1], triangle[2]),
        cross(point, triangle[2], triangle[0]))
    return not (
        any(value < -0.0000000001 for value in values)
        and any(value > 0.0000000001 for value in values))


def _tessellate_bridged_hole(outer, hole):
    outer = list(outer)
    hole = list(hole)
    if _signed_area(outer) < 0:
        outer.reverse()
    if _signed_area(hole) > 0:
        hole.reverse()
    outer_index, hole_index = min(
        (
            (outer_index, hole_index)
            for outer_index in range(len(outer))
            for hole_index in range(len(hole))
        ),
        key=lambda pair: (
            outer[pair[0]].co - hole[pair[1]].co).length_squared,
    )
    combined = (
        outer[outer_index:]
        + outer[:outer_index + 1]
        + hole[hole_index:]
        + hole[:hole_index + 1]
    )
    triangles = []
    for triangle in tessellate_polygon(
            [[Vector(vertex.co) for vertex in combined]]):
        if isinstance(triangle[0], int):
            vertices = [combined[index] for index in triangle]
        else:
            lookup = {
                (
                    round(vertex.co.x, 9),
                    round(vertex.co.y, 9),
                    round(vertex.co.z, 9),
                ): vertex
                for vertex in combined
            }
            vertices = [
                lookup[(
                    round(point.x, 9),
                    round(point.y, 9),
                    round(point.z, 9),
                )]
                for point in triangle
            ]
        if len(set(vertices)) == 3 and not _triangle_contains_origin(vertices):
            triangles.append(vertices)
    return triangles


def repair_visual_caps(obj) -> None:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    z_values = [vertex.co.z for vertex in bm.verts]
    minimum = min(z_values)
    maximum = max(z_values)
    tolerance = 0.0000001
    cap_faces = [
        face for face in bm.faces
        if all(abs(vertex.co.z - minimum) <= tolerance for vertex in face.verts)
        or all(abs(vertex.co.z - maximum) <= tolerance for vertex in face.verts)
    ]
    bmesh.ops.delete(bm, geom=cap_faces, context="FACES_ONLY")
    bm.edges.ensure_lookup_table()
    for plane, top in ((minimum, False), (maximum, True)):
        boundary = [
            edge for edge in bm.edges
            if len(edge.link_faces) == 1
            and all(
                abs(vertex.co.z - plane) <= tolerance
                for vertex in edge.verts
            )
        ]
        loops = _order_boundary_loops(boundary)
        if len(loops) != 2:
            bm.free()
            raise RuntimeError(
                f"{obj.name} expected outer and axis loops at z={plane}, "
                f"found {len(loops)}")
        outer = max(loops, key=lambda loop: abs(_signed_area(loop)))
        hole = min(loops, key=lambda loop: abs(_signed_area(loop)))
        selected = None
        for reverse_outer in (False, True):
            for reverse_hole in (False, True):
                ordered_outer = list(reversed(outer)) if reverse_outer else list(outer)
                ordered_hole = list(reversed(hole)) if reverse_hole else list(hole)
                flattened = ordered_outer + ordered_hole
                lookup = {
                    (
                        round(vertex.co.x, 9),
                        round(vertex.co.y, 9),
                        round(vertex.co.z, 9),
                    ): vertex
                    for vertex in flattened
                }
                polygons = [
                    [Vector(vertex.co) for vertex in ordered_outer],
                    [Vector(vertex.co) for vertex in ordered_hole],
                ]
                candidate = []
                for triangle in tessellate_polygon(polygons):
                    if isinstance(triangle[0], int):
                        candidate.append([
                            flattened[index] for index in triangle])
                    else:
                        candidate.append([
                            lookup[(
                                round(point.x, 9),
                                round(point.y, 9),
                                round(point.z, 9),
                            )]
                            for point in triangle
                        ])
                if candidate and not any(
                        _triangle_contains_origin(triangle)
                        for triangle in candidate):
                    selected = candidate
                    break
            if selected is not None:
                break
        if selected is None:
            selected = _tessellate_bridged_hole(outer, hole)
        if not selected or any(
                _triangle_contains_origin(triangle)
                for triangle in selected):
            bm.free()
            raise RuntimeError(
                f"{obj.name} cap triangulation still covers the axis at z={plane}")
        for vertices in selected:
            if (_signed_area(vertices) > 0) != top:
                vertices.reverse()
            face = bm.faces.new(vertices)
            face.smooth = False
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def main() -> None:
    source = LEGACY.read_text(encoding="utf-8")
    source = source.replace(
        '"08-lighting/rev-002/"',
        '"08-lighting/rev-004/"',
    ).replace(
        '"fan-card-exact-lighting.blend"',
        '"fan-card-smooth-normal-lighting.blend"',
    ).replace(
        "50_000",
        "100_000",
    )
    marker = "    before = mesh_stats(product_hierarchy)\n"
    triangulation = """    for visual_obj in [
        obj for obj in product_hierarchy
        if obj.type == "MESH"
        and any(token in obj.name for token in (
            "GunmetalFrame", "GoldTrim", "WarmSilverFace"))]:
        bpy.ops.object.select_all(action="DESELECT")
        visual_obj.select_set(True)
        bpy.context.view_layer.objects.active = visual_obj
        modifier = visual_obj.modifiers.new(
            name="ShippingTriangulation",
            type="TRIANGULATE")
        modifier.quad_method = "BEAUTY"
        modifier.ngon_method = "BEAUTY"
        modifier.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        repair_visual_caps(visual_obj)
"""
    if marker not in source:
        raise RuntimeError("The export insertion point changed.")
    source = source.replace(marker, triangulation + marker, 1)
    scope = {
        "__file__": str(HERE / "export_fan_card_smooth_impl.py"),
        "__name__": "fan_card_export_smooth_impl",
        "repair_visual_caps": repair_visual_caps,
    }
    exec(compile(source, scope["__file__"], "exec"), scope)
    scope["main"]()


if __name__ == "__main__":
    main()
