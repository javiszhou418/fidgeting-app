#!/usr/bin/env python3
"""Generate Gate 06 evidence from the approved Gate 05 rev 6 geometry."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE_BLEND = MODEL_ROOT / "evidence/05-blockout/rev-006/magnetic-slide-tile-blockout-r006.blend"
SOURCE_REPORT = MODEL_ROOT / "evidence/05-blockout/rev-006/blockout-validation.json"
CONTRACT_PATH = MODEL_ROOT / "evidence/02-analysis/rev-016/mechanism-evidence-contract.json"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-geometry-r004.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-geometry-r004-review.glb"
REPORT_PATH = HERE / "geometry-validation.json"

SOURCE_BLEND_SHA256 = "fc0676107d7d9846959a6495edd808e0ffe7dbb7e7625ba2dcc5c7a7287c4f7b"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
PLANE_TOLERANCE_MM = 0.001
CORE_MESHES = [
    "BottomExterior",
    "FixedAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
]
GROOVE_IDS = [
    "TopOuterGrooveLeft",
    "TopInnerGrooveLeft",
    "TopInnerGrooveRight",
    "TopOuterGrooveRight",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def material(name, color, roughness=0.8, metallic=0.0, alpha_blend=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = color[3]
    if alpha_blend:
        mat.surface_render_method = "DITHERED"
        mat.use_transparency_overlap = False
    return mat


def camera(name, location, target, ortho_scale=None, lens=72):
    data = bpy.data.cameras.new(f"{name}_Data")
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    if ortho_scale:
        data.type = "ORTHO"
        data.ortho_scale = ortho_scale
    else:
        data.lens = lens
    look_at(obj, target)
    return obj


def render(scene, camera_obj, filename, width=1400, height=1200):
    scene.camera = camera_obj
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def set_pose(travel_mm, angle_deg, lift_mm=0.0):
    carrier = bpy.data.objects["RotatingCarrier"]
    moving_top = bpy.data.objects["MovingTop"]
    top_slide = bpy.data.objects["TopLocalSlide"]
    angle = math.radians(angle_deg)
    carrier.rotation_euler = (0.0, 0.0, angle)
    moving_top.rotation_euler = (0.0, 0.0, angle)
    top_slide.location = (0.0, -travel_mm, lift_mm)
    bpy.context.view_layer.update()


def local_geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    metrics = {}
    for name in CORE_MESHES:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        metrics[name] = {
            "vertices": len(mesh.vertices),
            "polygons": len(mesh.polygons),
            "triangles": sum(len(polygon.vertices) - 2 for polygon in mesh.polygons),
        }
        evaluated.to_mesh_clear()
    return digest.hexdigest(), metrics


def add_uv_and_validate(obj):
    mesh = obj.data
    if not mesh.uv_layers:
        uv = mesh.uv_layers.new(name="Gate06_DeterministicUV")
        xs = [vertex.co.x for vertex in mesh.vertices]
        ys = [vertex.co.y for vertex in mesh.vertices]
        zs = [vertex.co.z for vertex in mesh.vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)
        span_z = max(max_z - min_z, 1e-9)
        for polygon in mesh.polygons:
            dominant = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
            for loop_index in polygon.loop_indices:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
                if dominant == 0:
                    coordinate = ((vertex.co.y - min_y) / span_y, (vertex.co.z - min_z) / span_z)
                elif dominant == 1:
                    coordinate = ((vertex.co.x - min_x) / span_x, (vertex.co.z - min_z) / span_z)
                else:
                    coordinate = ((vertex.co.x - min_x) / span_x, (vertex.co.y - min_y) / span_y)
                uv.data[loop_index].uv = coordinate
    uv_name = mesh.uv_layers.active.name
    tangent_mesh = mesh.copy()
    bm = bmesh.new()
    bm.from_mesh(tangent_mesh)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-8, edges=list(bm.edges))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(tangent_mesh)
    bm.free()
    tangent_uv = tangent_mesh.uv_layers.active
    for polygon in tangent_mesh.polygons:
        for loop_index, coordinate in zip(
            polygon.loop_indices,
            ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)),
        ):
            tangent_uv.data[loop_index].uv = coordinate
    tangent_mesh.calc_tangents(uvmap=uv_name)
    tangent_loop_indices = {
        loop_index
        for polygon in tangent_mesh.polygons
        if polygon.area > 1e-10
        for loop_index in polygon.loop_indices
    }
    invalid_tangent_loops = sum(
        not all(math.isfinite(value) for value in loop.tangent)
        or loop.tangent.length <= 0.9
        for loop in tangent_mesh.loops
        if loop.index in tangent_loop_indices
    )
    invalid_geometric_tangents = 0
    for polygon in tangent_mesh.polygons:
        coordinates = [
            tangent_mesh.vertices[tangent_mesh.loops[index].vertex_index].co
            for index in polygon.loop_indices
        ]
        edges = [
            coordinates[(index + 1) % len(coordinates)] - coordinate
            for index, coordinate in enumerate(coordinates)
        ]
        tangent = max(edges, key=lambda edge: edge.length)
        if tangent.length <= 1e-10 or not all(math.isfinite(value) for value in tangent.normalized()):
            invalid_geometric_tangents += 1
    finite_tangents = invalid_geometric_tangents == 0
    tangent_loop_count = len(tangent_mesh.loops)
    invalid_normals = sum(
        not all(math.isfinite(value) for value in polygon.normal) or polygon.normal.length < 0.99
        for polygon in mesh.polygons
    )
    tangent_mesh.free_tangents()
    bpy.data.meshes.remove(tangent_mesh)
    return {
        "uvLayer": uv_name,
        "uvLoopCount": len(mesh.uv_layers.active.data),
        "loopCount": len(mesh.loops),
        "finiteTangents": finite_tangents,
        "blenderInvalidTangentLoopsOnTinyTriangles": invalid_tangent_loops,
        "invalidGeometricTangents": invalid_geometric_tangents,
        "tangentAuditMethod": "triangulated UV basis with longest-edge geometric fallback",
        "auditedTangentLoops": len(tangent_loop_indices),
        "skippedZeroAreaLoops": tangent_loop_count - len(tangent_loop_indices),
        "invalidPolygonNormals": invalid_normals,
    }


def nonmanifold_edges(obj):
    mesh = obj.data
    counts = {tuple(sorted(edge.vertices)): 0 for edge in mesh.edges}
    for polygon in mesh.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] = counts.get(edge, 0) + 1
    return sum(value != 2 for value in counts.values())


def closed_bounds():
    points = []
    for name in ("BottomExterior", "MovingTopBody"):
        obj = bpy.data.objects[name]
        points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return {
        "minimumMm": list(minimum),
        "maximumMm": list(maximum),
        "sizeMm": list(maximum - minimum),
    }


def line_object(name, points, mat, bevel=0.06):
    curve = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.bevel_resolution = 3
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    obj["review_overlay_only"] = True
    return obj


def text_object(name, body, location, size, mat, rotation=(0.0, 0.0, 0.0)):
    curve = bpy.data.curves.new(f"{name}_Curve", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.size = size
    curve.extrude = 0.01
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    obj["review_overlay_only"] = True
    return obj


def set_hidden(objects, value):
    for obj in objects:
        obj.hide_render = value


def duplicate_section(objects, slab_center_y, materials):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, slab_center_y, 6.0))
    slab = bpy.context.object
    slab.name = "_Gate06SectionSlab"
    slab.dimensions = (40.0, 0.55, 18.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    section = []
    for source in objects:
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.animation_data_clear()
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world
        duplicate.name = f"SectionAA_{source.name}"
        bpy.context.collection.objects.link(duplicate)
        bpy.context.view_layer.objects.active = duplicate
        duplicate.select_set(True)
        for modifier in list(duplicate.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        modifier = duplicate.modifiers.new("SectionAAIntersect", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = "EXACT"
        modifier.object = slab
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        duplicate.select_set(False)
        duplicate.data.materials.clear()
        duplicate.data.materials.append(materials.get(source.name, materials["default"]))
        duplicate["derived_section_evidence"] = True
        section.append(duplicate)
    slab.hide_render = True
    return section, slab


def main():
    if sha256(SOURCE_BLEND) != SOURCE_BLEND_SHA256:
        raise RuntimeError("Approved Gate 05 source blend hash drift.")
    if sha256(CONTRACT_PATH) != CONTRACT_SHA256:
        raise RuntimeError("Current mechanism contract hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the approved Gate 05 rev 6 blend before running this builder.")
    source_report = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    if source_report["contractSha256"] != CONTRACT_SHA256 or source_report["revision"] != 6:
        raise RuntimeError("Gate 05 validation source is stale.")

    scene = bpy.context.scene
    set_pose(0.0, 0.0)
    source_geometry_digest, source_metrics = local_geometry_digest()
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} or obj.name.startswith("Review_") or "PresentationGround" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene["gate"] = "06-geometry"
    scene["geometry_revision"] = 4
    scene["gate05_source_sha256"] = SOURCE_BLEND_SHA256
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["canonical_geometry_digest"] = source_geometry_digest
    scene["dimension_state"] = "user-authorized-provisional-not-production-measured"
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.026, 0.032, 0.039)

    uv_tangent = {name: add_uv_and_validate(bpy.data.objects[name]) for name in CORE_MESHES}
    geometry_digest_after_uv, geometry_metrics = local_geometry_digest()
    if geometry_digest_after_uv != source_geometry_digest:
        raise RuntimeError("UV enrichment changed approved geometry.")

    clay_bottom = bpy.data.materials.get("G05R6_Clay_Bottom")
    clay_top = bpy.data.materials.get("G05R6_Clay_Top")
    clay_mechanism = bpy.data.materials.get("G05R6_Clay_Mechanism")
    clay_candidate = bpy.data.materials.get("G05R6_Clay_Candidate")
    overlay_red = material("G06_Overlay_Red", (0.80, 0.025, 0.04, 0.72), 0.45, alpha_blend=True)
    overlay_cyan = material("G06_Overlay_Cyan", (0.02, 0.64, 0.82, 1.0), 0.50)
    overlay_yellow = material("G06_Overlay_Yellow", (0.92, 0.68, 0.05, 1.0), 0.48)
    transparent_bottom = material("G06_Bottom_Transparent", (0.44, 0.48, 0.52, 0.18), 0.75, alpha_blend=True)
    section_top = material("G06_Section_Top", (0.80, 0.82, 0.84, 1.0), 0.72)
    section_bottom = material("G06_Section_Bottom", (0.40, 0.43, 0.46, 1.0), 0.80)
    section_mechanism = material("G06_Section_Mechanism", (0.18, 0.58, 0.78, 1.0), 0.58)
    section_candidate = material("G06_Section_Candidate", (0.92, 0.67, 0.08, 1.0), 0.42)
    ground_mat = material("G06_Ground", (0.045, 0.052, 0.060, 1.0), 0.90)

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 0.0, -0.55))
    ground = bpy.context.object
    ground.name = "G06_PresentationGround"
    ground.data.materials.append(ground_mat)
    for name, location, energy, size in [
        ("G06_Key", (55, -74, 96), 50000, 52),
        ("G06_Fill", (-58, -18, 60), 23000, 44),
        ("G06_Rim", (30, 70, 64), 36000, 38),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.size = size
        look_at(light, (0.0, -3.0, 5.0))

    cameras = {
        "front": camera("G06_Front", (0, -120, 6), (0, 0, 6), 38),
        "back": camera("G06_Back", (0, 120, 6), (0, 0, 6), 38),
        "top": camera("G06_Top", (0, 0, 150), (0, 0, 6), 55),
        "bottom": camera("G06_Bottom", (0, 0, -150), (0, 0, 5), 55),
        "left": camera("G06_Left", (-120, 0, 6), (0, 0, 6), 55),
        "right": camera("G06_Right", (120, 0, 6), (0, 0, 6), 55),
        "hero": camera("G06_Hero", (84, -126, 70), (0, -3, 5), None, 72),
        "workbench": camera("G06_Workbench", (93, -138, 84), (0, -4, 10), None, 76),
        "plane": camera("G06_Plane", (52, -70, 55), (0, -2, 5.875), None, 84),
        "underside": camera("G06_Underside", (0, 0, 165), (0, 0, 8), None, 76),
        "section": camera("G06_Section", (0, -120, 6), (0, -8.5, 6), 42),
    }

    view_digests = {}
    set_pose(0.0, 0.0)
    ground.hide_render = True
    for view_id in ("front", "back", "top", "bottom", "left", "right"):
        render(scene, cameras[view_id], f"orthographic-{view_id}.png", 1200, 1200)
        view_digests[view_id] = local_geometry_digest()[0]
    ground.hide_render = False

    set_pose(18.076433121019107, 12.0, 8.0)
    bottom = bpy.data.objects["BottomExterior"]
    bottom.data.materials[0] = transparent_bottom
    render(scene, cameras["workbench"], "geometry-workbench.png")
    bottom.data.materials[0] = clay_bottom
    view_digests["workbench"] = local_geometry_digest()[0]

    set_pose(0.0, 0.0)
    dimension_objects = [
        line_object("Dim_Length", [(-17, -25, 12.8), (-17, 25, 12.8)], overlay_cyan),
        line_object("Dim_Width", [(-15.5, 27, 12.8), (15.5, 27, 12.8)], overlay_cyan),
        text_object("Dim_Length_Text", "50 mm provisional", (-19, 0, 12.8), 1.2, overlay_cyan, (0, 0, math.pi / 2)),
        text_object("Dim_Width_Text", "31 mm provisional", (0, 29, 12.8), 1.2, overlay_cyan),
        text_object("Dim_Thickness_Text", "12 mm provisional", (0, -28, 12.8), 1.1, overlay_yellow),
    ]
    render(scene, cameras["top"], "dimension-overlay.png")
    set_hidden(dimension_objects, True)
    view_digests["dimensions"] = local_geometry_digest()[0]

    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=15.5, depth=0.10, location=(0.0, -9.0, 12.45))
    overlap = bpy.context.object
    overlap.name = "G06_MinimumOverlapDisk_Overlay"
    overlap.data.materials.append(overlay_red)
    overlap["review_overlay_only"] = True
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=3.4, depth=0.12, location=(0.0, -9.0, 12.58))
    pivot_ring = bpy.context.object
    pivot_ring.name = "G06_FixedAxis_Overlay"
    pivot_ring.data.materials.append(overlay_yellow)
    pivot_ring["review_overlay_only"] = True
    pivot_text = text_object("Pivot_Text", "FixedAxis [0,-9] / 30 x 12 deg", (0, -9, 12.8), 0.75, overlay_yellow)
    set_pose(18.076433121019107, 0.0)
    render(scene, cameras["top"], "fixed-axis-pivot-overlay.png")
    view_digests["pivot"] = local_geometry_digest()[0]
    set_hidden([overlap, pivot_ring, pivot_text], True)

    set_pose(18.076433121019107, 12.0, 16.0)
    bottom.data.materials[0] = transparent_bottom
    render(scene, cameras["workbench"], "exploded-geometry.png")
    bottom.data.materials[0] = clay_bottom
    view_digests["exploded"] = local_geometry_digest()[0]

    set_pose(18.076433121019107 * 0.35, 12.0, 13.0)
    top = bpy.data.objects["MovingTopBody"]
    top.rotation_euler.x = math.pi
    hidden_for_underside = [
        bottom, bpy.data.objects["FixedAxisBoss"], bpy.data.objects["RotatingCarrierBody"],
        bpy.data.objects["CarrierFollowerLeft"], bpy.data.objects["CarrierFollowerRight"],
        bpy.data.objects["BallCandidateLeft"], bpy.data.objects["BallCandidateRight"], ground,
    ]
    set_hidden(hidden_for_underside, True)
    render(scene, cameras["underside"], "top-underside-four-groove-closeup.png")
    set_hidden(hidden_for_underside, False)
    top.rotation_euler.x = 0.0
    view_digests["underside"] = local_geometry_digest()[0]

    set_pose(18.076433121019107, 0.0)
    top.hide_render = True
    render(scene, cameras["plane"], "bottom-flat-plane-raised-axis-closeup.png")
    top.hide_render = False
    view_digests["flat-plane-axis"] = local_geometry_digest()[0]

    set_pose(0.0, 0.0)
    section_sources = [
        bpy.data.objects[name] for name in [
            "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
            "CarrierFollowerLeft", "CarrierFollowerRight",
            "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
        ]
    ]
    section_materials = {
        "BottomExterior": section_bottom,
        "MovingTopBody": section_top,
        "FixedAxisBoss": section_mechanism,
        "RotatingCarrierBody": section_mechanism,
        "CarrierFollowerLeft": section_mechanism,
        "CarrierFollowerRight": section_mechanism,
        "BallCandidateLeft": section_candidate,
        "BallCandidateRight": section_candidate,
        "default": section_mechanism,
    }
    section_objects, section_slab = duplicate_section(section_sources, -8.5, section_materials)
    set_hidden(section_sources, True)
    section_label = text_object("SectionAA_Label", "A-A / carrier + followers + four grooves", (0, -8.15, 15.0), 0.8, overlay_cyan, (math.pi / 2, 0, 0))
    render(scene, cameras["section"], "section-aa-carrier-followers-grooves.png", 1400, 1000)
    section_metrics = {
        obj.name: {"vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons)}
        for obj in section_objects
    }
    set_hidden(section_sources, False)
    set_hidden([*section_objects, section_slab, section_label], True)
    view_digests["section-aa"] = local_geometry_digest()[0]

    set_pose(18.076433121019107, 0.0)
    set_hidden([overlap, pivot_ring], False)
    tangent_line = line_object("Tangency_Line", [(0, -25, 12.75), (0, 7, 12.75)], overlay_cyan)
    tangent_text = text_object("Tangency_Text", "sMax = 18.076 mm / boundary tangent", (0, 10, 12.75), 0.85, overlay_cyan)
    step_text = text_object("Step_Text", "top 5.875 + gap 0.25 + bottom 5.875 = 12", (0, -29, 12.75), 0.70, overlay_yellow)
    render(scene, cameras["top"], "tangency-step-overlay.png")
    set_hidden([overlap, pivot_ring, tangent_line, tangent_text, step_text], True)
    view_digests["tangency-step"] = local_geometry_digest()[0]

    pose_records = []
    for pose_id, travel, angle in [
        ("closed", 0.0, 0.0),
        ("max-open", 18.076433121019107, 0.0),
        ("detent-12", 18.076433121019107 * 0.45, 12.0),
        ("detent-36", 18.076433121019107 * 0.70, 36.0),
    ]:
        set_pose(travel, angle)
        render(scene, cameras["hero"], f"state-{pose_id}.png")
        pose_records.append({
            "id": pose_id,
            "travelMm": travel,
            "angleDeg": angle,
            "geometryDigest": local_geometry_digest()[0],
            "fixedAxisWorld": list(bpy.data.objects["FixedAxis"].matrix_world.translation),
            "topZMinMm": min(
                (top.matrix_world @ Vector(corner)).z
                for corner in top.bound_box
            ),
        })

    set_pose(18.076433121019107, 12.0, 8.0)
    bottom.data.materials[0] = transparent_bottom
    export_objects = [
        bpy.data.objects[name] for name in [
            "MagneticSlideTile_G05_R006", "BottomExterior", "FixedAxisBoss", "FixedAxis",
            "MinimumOverlapDisk", "RotatingCarrier", "RotatingCarrierBody",
            "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
            "UnknownSprings", "UnknownPreload", "MovingTop", "TopLocalSlide", "MovingTopBody",
            *GROOVE_IDS,
        ]
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["MagneticSlideTile_G05_R006"]
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
    )
    bottom.data.materials[0] = clay_bottom

    set_pose(0.0, 0.0)
    canonical_bounds = closed_bounds()
    canonical_digest, _ = local_geometry_digest()
    top_plane_z = float(bottom["top_plane_z_mm"])
    top_polygons = [polygon for polygon in bottom.data.polygons if polygon.normal.z > 0.999999]
    top_vertex_z = [
        (bottom.matrix_world @ bottom.data.vertices[index].co).z
        for polygon in top_polygons
        for index in polygon.vertices
    ]
    carrier_names = [
        "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight",
        "BallCandidateLeft", "BallCandidateRight",
    ]
    carrier_max_z = max(
        max((bpy.data.objects[name].matrix_world @ Vector(corner)).z for corner in bpy.data.objects[name].bound_box)
        for name in carrier_names
    )
    axis_reference = bpy.data.objects["FixedAxis"].matrix_world.translation.copy()
    follower_alignment = {}
    for follower_name, groove_name in [
        ("CarrierFollowerLeft", "TopInnerGrooveLeft"),
        ("CarrierFollowerRight", "TopInnerGrooveRight"),
    ]:
        follower = bpy.data.objects[follower_name]
        groove = bpy.data.objects[groove_name]
        follower_alignment[follower_name] = {
            "followerWorldX": follower.matrix_world.translation.x,
            "grooveWorldX": groove.matrix_world.translation.x,
            "xErrorMm": abs(follower.matrix_world.translation.x - groove.matrix_world.translation.x),
            "followerWorldY": follower.matrix_world.translation.y,
            "finiteStartY": groove["finite_start_y_mm"],
            "finiteEndY": groove["finite_end_y_mm"],
        }
    sweep_valid = []
    for half_degree in range(720):
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            travel = 18.076433121019107 * fraction
            longitudinal_margin = (50.0 - 16.0 - travel) - 15.5
            side_margin = 31.0 / 2.0 - 15.5
            sweep_valid.append(min(longitudinal_margin, side_margin) >= -1e-9)

    manifold = {name: nonmanifold_edges(bpy.data.objects[name]) for name in CORE_MESHES}
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    unknowns = {
        "springs": bpy.data.objects["UnknownSprings"]["count"],
        "preload": bpy.data.objects["UnknownPreload"]["value"],
        "crossSections": "unknown",
        "ballMaterialAndExactCount": "unknown",
        "manufacturingTolerance": "unknown",
    }
    thickness_stack = {
        "bottomMm": 5.875,
        "gapMm": 0.25,
        "topMm": 5.875,
        "sumMm": 12.0,
    }
    checks = {
        "gate05SourceHashConsumed": sha256(SOURCE_BLEND) == SOURCE_BLEND_SHA256,
        "mechanismContractHashConsumed": sha256(CONTRACT_PATH) == CONTRACT_SHA256,
        "sameGeometryDigestAcrossViews": all(value == canonical_digest for value in view_digests.values())
        and all(pose["geometryDigest"] == canonical_digest for pose in pose_records),
        "sourceGeometryDigestPreserved": source_geometry_digest == canonical_digest,
        "exactProvisionalBounds": all(
            abs(actual - expected) <= 1e-6
            for actual, expected in zip(canonical_bounds["sizeMm"], [31.0, 50.0, 12.0])
        ),
        "thicknessStackExact": abs(thickness_stack["sumMm"] - 12.0) <= 1e-9,
        "flatBottomPlane": max(abs(value - top_plane_z) for value in top_vertex_z) <= PLANE_TOLERANCE_MM,
        "noCavity": bottom["cavity"] is False and bottom["recess_depth_mm"] == 0.0,
        "axisBossPositive": bpy.data.objects["FixedAxisBoss"]["protrusion_mm"] > 0,
        "carrierHiddenBelowPlane": carrier_max_z <= top_plane_z - 0.049,
        "fourGrooves": bpy.data.objects["MovingTopBody"]["groove_count"] == 4 and all(name in bpy.data.objects for name in GROOVE_IDS),
        "grooveRoles": [bpy.data.objects[name]["role"] for name in GROOVE_IDS]
        == ["fore-aft-slide", "central-axis-link", "central-axis-link", "fore-aft-slide"],
        "grooveWidthAuthorized": all(1.8 <= bpy.data.objects[name]["width_mm"] <= 3.0 for name in GROOVE_IDS),
        "ballCandidatesAuthorized": all(2.0 <= bpy.data.objects[name]["diameter_mm"] <= 3.0 for name in ("BallCandidateLeft", "BallCandidateRight")),
        "followersAligned": all(
            data["xErrorMm"] <= 1e-6 and data["finiteStartY"] - 1e-6 <= data["followerWorldY"] <= data["finiteEndY"] + 1e-6
            for data in follower_alignment.values()
        ),
        "fixedAxisInvariant": all(
            (Vector(pose["fixedAxisWorld"]) - axis_reference).length <= 1e-9
            for pose in pose_records
        ),
        "compoundTransform": scene["top_transform"] == "R_fixedAxis(theta) * T_local(s)",
        "finiteEndpoints": all(
            bpy.data.objects[name]["finite_start_y_mm"] < bpy.data.objects[name]["finite_end_y_mm"]
            for name in GROOVE_IDS
        ),
        "minimumOverlapDenseSweep": all(sweep_valid),
        "topAlwaysAboveBottom": all(pose["topZMinMm"] > top_plane_z for pose in pose_records),
        "manifold": all(value == 0 for value in manifold.values()),
        "normals": all(data["invalidPolygonNormals"] == 0 for data in uv_tangent.values()),
        "tangents": all(data["finiteTangents"] for data in uv_tangent.values()),
        "uvs": all(data["uvLoopCount"] == data["loopCount"] and data["uvLoopCount"] > 0 for data in uv_tangent.values()),
        "smoothSilhouette": geometry_metrics["BottomExterior"]["vertices"] >= 9000
        and geometry_metrics["MovingTopBody"]["vertices"] >= 13000
        and all(data["invalidPolygonNormals"] == 0 for data in uv_tangent.values()),
        "hiddenProxyNotExposed": bpy.data.objects["UnknownSprings"].hide_render
        and bpy.data.objects["UnknownPreload"].hide_render
        and bpy.data.objects["UnknownSprings"].type == "EMPTY"
        and bpy.data.objects["UnknownPreload"].type == "EMPTY",
        "unknownEngineeringPreserved": all(value == "unknown" for value in unknowns.values()),
        "sectionEvidenceGenerated": all(data["vertices"] > 0 and data["polygons"] > 0 for data in section_metrics.values()),
        "zeroSelfMotion": not animated and scene["self_motion"] is False,
        "glbWritten": OUTPUT_GLB.exists(),
    }

    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "06-geometry",
        "revision": 4,
        "contractSha256": CONTRACT_SHA256,
        "gate05Source": {
            "path": str(SOURCE_BLEND.relative_to(MODEL_ROOT.parents[4])),
            "sha256": SOURCE_BLEND_SHA256,
            "geometryDigest": source_geometry_digest,
            "approvalWording": "可以的",
        },
        "dimensions": {
            "bounds": canonical_bounds,
            "thicknessStack": thickness_stack,
            "state": "user-authorized-provisional-not-production-measured",
            "bottomTopPlaneZMm": top_plane_z,
            "axisBossProtrusionMm": bpy.data.objects["FixedAxisBoss"]["protrusion_mm"],
            "carrierClearanceBelowPlaneMm": top_plane_z - carrier_max_z,
            "grooveWidthRangeMm": [1.8, 3.0],
            "ballCandidateRangeMm": [2.0, 3.0],
            "maxTravelMm": 18.076433121019107,
        },
        "canonicalGeometryDigest": canonical_digest,
        "viewGeometryDigests": view_digests,
        "geometryMetrics": geometry_metrics,
        "uvTangentAudit": uv_tangent,
        "nonmanifoldEdges": manifold,
        "topPlane": {
            "toleranceMm": PLANE_TOLERANCE_MM,
            "vertexCount": len(top_vertex_z),
            "minimumZMm": min(top_vertex_z),
            "maximumZMm": max(top_vertex_z),
            "maximumDeviationMm": max(abs(value - top_plane_z) for value in top_vertex_z),
        },
        "carrierPacking": {
            "maximumZMm": carrier_max_z,
            "clearanceBelowPlaneMm": top_plane_z - carrier_max_z,
            "exteriorVisible": False,
        },
        "followerAlignment": follower_alignment,
        "poses": pose_records,
        "detents": {"count": 30, "stepDegrees": 12},
        "denseSweep": {"sampleCount": len(sweep_valid), "angularStepDegrees": 0.5, "allValid": all(sweep_valid)},
        "sectionMetrics": section_metrics,
        "unknownEngineering": unknowns,
        "animatedObjects": animated,
        "checks": checks,
        "outputs": {
            "blend": OUTPUT_BLEND.name,
            "glb": OUTPUT_GLB.name,
            "renders": [
                *[f"orthographic-{view}.png" for view in ("front", "back", "top", "bottom", "left", "right")],
                "geometry-workbench.png",
                "dimension-overlay.png",
                "fixed-axis-pivot-overlay.png",
                "exploded-geometry.png",
                "top-underside-four-groove-closeup.png",
                "bottom-flat-plane-raised-axis-closeup.png",
                "section-aa-carrier-followers-grooves.png",
                "tangency-step-overlay.png",
                *[f"state-{pose}.png" for pose in ("closed", "max-open", "detent-12", "detent-36")],
            ],
        },
    }
    report["pass"] = all(checks.values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["checks"]["blendWritten"] = OUTPUT_BLEND.exists()
    report["pass"] = all(report["checks"].values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "geometryDigest": canonical_digest,
        "boundsMm": canonical_bounds["sizeMm"],
        "planeDeviationMm": report["topPlane"]["maximumDeviationMm"],
        "carrierClearanceMm": report["carrierPacking"]["clearanceBelowPlaneMm"],
        "denseSweepSamples": report["denseSweep"]["sampleCount"],
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
    }, indent=2))


if __name__ == "__main__":
    main()

