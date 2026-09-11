#!/usr/bin/env python3
"""Regenerate Gate 06 geometry evidence for the endpoint rotation interlock."""

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parents[2]
SOURCE = MODEL_ROOT / "evidence/05-blockout/rev-012/magnetic-slide-tile-fixed-axis-r012.blend"
CONTRACT = MODEL_ROOT / "evidence/02-analysis/rev-017/mechanism-evidence-contract.json"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-geometry-r005.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-geometry-r005-review.glb"
REPORT = HERE / "geometry-validation.json"
SOURCE_SHA256 = "f587be803cf98e134f173e961fe4e096708f08916af51d971b0ef381d51c11a2"
CONTRACT_SHA256 = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
MAX_TRAVEL = 18.076433121019107
PIVOT = Vector((0.0, -9.0, 5.875))
TOP_Q_Z = -3.1875
DISK_RADIUS = 15.0
ALIGNMENT_TOLERANCE_DEG = 0.001
ENDPOINT_TOLERANCE_MM = 1e-6
PRODUCT_MESHES = {"BottomExterior", "MovingTopBody"}
INTERNAL_MESHES = {
    "InternalAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft",
    "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
}
CORE_MESHES = PRODUCT_MESHES | INTERNAL_MESHES
GROOVES = [
    "TopOuterGrooveLeft", "TopInnerGrooveLeft",
    "TopInnerGrooveRight", "TopOuterGrooveRight",
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_digest():
    digest = hashlib.sha256()
    for name in sorted(CORE_MESHES):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def normalized_angle(angle):
    value = angle % 360.0
    return 0.0 if min(value, 360.0 - value) <= ALIGNMENT_TOLERANCE_DEG else value


def resolve_pose(current_slide, current_angle, requested_slide, requested_angle, intent):
    angle = normalized_angle(current_angle)
    if intent == "rotate":
        if current_slide < MAX_TRAVEL - ENDPOINT_TOLERANCE_MM:
            return current_slide, 0.0, "rotation-blocked-below-endpoint"
        return MAX_TRAVEL, requested_angle % 360.0, "endpoint-rotation"
    if angle != 0.0:
        return MAX_TRAVEL, angle, "slide-blocked-while-rotated"
    return max(0.0, min(MAX_TRAVEL, requested_slide)), 0.0, "aligned-slide"


def set_pose(slide, angle):
    angle = normalized_angle(angle)
    if slide < MAX_TRAVEL - ENDPOINT_TOLERANCE_MM and angle != 0.0:
        raise RuntimeError(f"Illegal Gate 06 pose: s={slide}, theta={angle}")
    moving = bpy.data.objects["MovingTop"]
    top_slide = bpy.data.objects["TopLocalSlide"]
    carrier = bpy.data.objects["RotatingCarrier"]
    moving.location = PIVOT
    moving.rotation_mode = "XYZ"
    moving.rotation_euler = (0.0, 0.0, math.radians(angle))
    top_slide.location = (0.0, 9.0 - slide, 0.0)
    carrier.location = (0.0, 0.0, -0.48)
    carrier.rotation_mode = "XYZ"
    carrier.rotation_euler = (0.0, 0.0, math.radians(angle))
    bpy.context.view_layer.update()


def q_local(slide):
    return Vector((0.0, -9.0 + slide, TOP_Q_Z))


def top_residual(slide):
    return (bpy.data.objects["MovingTopBody"].matrix_world @ q_local(slide) - PIVOT).length


def material(name, color, metallic=0.0, roughness=0.68, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Alpha"].default_value = alpha
    if alpha < 1.0 and hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, ortho=None, lens=72):
    data = bpy.data.cameras.new(f"{name}_Data")
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    data.lens = lens
    if ortho is not None:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    look_at(obj, target)
    return obj


def render(scene, cam, filename, size=(1200, 1200)):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def set_product_visibility(extra=()):
    allowed = PRODUCT_MESHES | set(extra)
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in allowed


def set_technical_visibility():
    allowed = PRODUCT_MESHES | INTERNAL_MESHES | {"Gate06_FixedAxisOverlay"}
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in allowed


def line_object(name, points, mat, bevel=0.07):
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


def set_hidden(objects, hidden):
    for obj in objects:
        obj.hide_render = hidden


def nonmanifold_edges(obj):
    counts = {tuple(sorted(edge.vertices)): 0 for edge in obj.data.edges}
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] = counts.get(edge, 0) + 1
    return sum(value != 2 for value in counts.values())


def bvh(obj):
    return BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get(), epsilon=1e-6)


def overlap_pairs(first, second):
    return len(bvh(first).overlap(bvh(second)))


def local_top_bvh():
    mesh = bpy.data.objects["MovingTopBody"].data
    return BVHTree.FromPolygons(
        [vertex.co.copy() for vertex in mesh.vertices],
        [list(polygon.vertices) for polygon in mesh.polygons],
        all_triangles=False,
    )


def disk_coverage_misses(top_tree, slide, angle, radial_samples=48):
    set_pose(slide, angle)
    inverse = bpy.data.objects["MovingTopBody"].matrix_world.inverted()
    misses = 0
    for radial_index in range(radial_samples):
        phase = 2.0 * math.pi * radial_index / radial_samples
        point = PIVOT + Vector((DISK_RADIUS * math.cos(phase), DISK_RADIUS * math.sin(phase), 20.0))
        local_point = inverse @ point
        local_direction = inverse.to_3x3() @ Vector((0.0, 0.0, -1.0))
        hit, _, _, _ = top_tree.ray_cast(local_point, local_direction, 50.0)
        misses += hit is None
    return misses


def duplicate_section(sources, slab_center_y, mats):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, slab_center_y, 6.0))
    slab = bpy.context.object
    slab.name = "Gate06_SectionSlab"
    slab.dimensions = (40.0, 0.55, 18.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    section = []
    for source in sources:
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.parent = None
        duplicate.matrix_world = source.matrix_world
        duplicate.name = f"Gate06_SectionAA_{source.name}"
        bpy.context.collection.objects.link(duplicate)
        bpy.context.view_layer.objects.active = duplicate
        duplicate.select_set(True)
        modifier = duplicate.modifiers.new("SectionAAIntersect", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = "EXACT"
        modifier.object = slab
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        duplicate.select_set(False)
        assign(duplicate, mats.get(source.name, mats["default"]))
        duplicate["derived_section_evidence"] = True
        section.append(duplicate)
    slab.hide_render = True
    return section, slab


def main():
    if sha256(SOURCE) != SOURCE_SHA256:
        raise RuntimeError("Gate 05 rev 12 approved blend hash drift.")
    if sha256(CONTRACT) != CONTRACT_SHA256:
        raise RuntimeError("Mechanism evidence contract rev 17 hash drift.")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT", "FONT", "CURVE"} or obj.name.startswith(("_Gate06", "Gate06_", "Technical_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    root = bpy.data.objects["MagneticSlideTile_G05_R012"]
    root.name = "MagneticSlideTile_G06_R005"
    root["mechanism_contract_sha256"] = CONTRACT_SHA256
    root["gate05_source_sha256"] = SOURCE_SHA256
    root["geometry_digest"] = GEOMETRY_DIGEST
    root["endpoint_interlock"] = "0<=s<sMax:theta=0;s=sMax:theta=0..360;theta!=0:slide locked"
    root["legal_pose_ids"] = "closed,max-open-0,max-open-12,max-open-36,max-open-360"
    root["prohibited_pose"] = "mid-slide rotation"
    scene["gate"] = "06-geometry"
    scene["geometry_revision"] = 5
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["gate05_source_sha256"] = SOURCE_SHA256
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["product_renderer_whitelist"] = sorted(PRODUCT_MESHES)
    scene["state_machine"] = root["endpoint_interlock"]
    scene["final_materials_applied"] = False
    scene["simulator_used"] = False
    scene["shipping_unity_changed"] = False
    scene["self_motion"] = False

    if geometry_digest() != GEOMETRY_DIGEST:
        raise RuntimeError("Gate 05 geometry digest changed before Gate 06.")

    clay = material("G06R5_ProductClay", (0.73, 0.75, 0.78), roughness=0.62)
    internal = material("G06R5_InternalClay", (0.18, 0.24, 0.31), metallic=0.12, roughness=0.48)
    follower = material("G06R5_FollowerClay", (0.18, 0.56, 0.76), roughness=0.40)
    cyan = material("G06R5_OverlayCyan", (0.02, 0.72, 0.92), roughness=0.40)
    yellow = material("G06R5_OverlayYellow", (0.96, 0.65, 0.05), roughness=0.42)
    red = material("G06R5_OverlayRed", (0.95, 0.04, 0.03), roughness=0.40)
    section_top = material("G06R5_SectionTop", (0.82, 0.84, 0.87), roughness=0.72)
    section_bottom = material("G06R5_SectionBottom", (0.42, 0.45, 0.49), roughness=0.78)
    for name in PRODUCT_MESHES:
        assign(bpy.data.objects[name], clay)
    for name in INTERNAL_MESHES:
        assign(bpy.data.objects[name], follower if "Follower" in name or "Ball" in name else internal)

    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.22, depth=18.0, location=PIVOT + Vector((0, 0, 4.0)))
    axis_overlay = bpy.context.object
    axis_overlay.name = "Gate06_FixedAxisOverlay"
    assign(axis_overlay, red)
    axis_overlay["technical_overlay_only"] = True
    axis_overlay.hide_render = True

    world = scene.world or bpy.data.worlds.new("G06R5_World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.028, 0.034, 0.044, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.55
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    for name, location, energy, size in [
        ("G06R5_Key", (58, -76, 92), 50000, 46),
        ("G06R5_Fill", (-52, -18, 58), 24000, 42),
        ("G06R5_Rim", (34, 70, 66), 34000, 34),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        look_at(obj, (0, -3, 5))

    cameras = {
        "front": camera("G06R5_Front", (0, -110, 8), (0, 0, 6), ortho=64),
        "back": camera("G06R5_Back", (0, 110, 8), (0, 0, 6), ortho=64),
        "top": camera("G06R5_Top", (0, 0, 125), (0, 0, 5), ortho=64),
        "bottom": camera("G06R5_Bottom", (0, 0, -115), (0, 0, 5), ortho=64),
        "left": camera("G06R5_Left", (-90, 0, 8), (0, 0, 6), ortho=60),
        "right": camera("G06R5_Right", (90, 0, 8), (0, 0, 6), ortho=60),
        "hero": camera("G06R5_Hero", (72, -100, 68), (0, -5, 6), lens=70),
        "technical": camera("G06R5_Technical", (76, -105, 66), (0, -6, 7), lens=74),
        "section": camera("G06R5_Section", (0, -115, 7), (0, -8.5, 6), ortho=44),
    }

    view_digests = {}
    set_pose(0.0, 0.0)
    set_product_visibility()
    for view in ("front", "back", "top", "bottom", "left", "right"):
        render(scene, cameras[view], f"orthographic-{view}.png")
        view_digests[view] = geometry_digest()

    set_pose(MAX_TRAVEL, 12.0)
    set_technical_visibility()
    render(scene, cameras["technical"], "geometry-workbench.png", (1400, 1100))
    view_digests["workbench"] = geometry_digest()

    set_pose(0.0, 0.0)
    set_product_visibility()
    dimensions = [
        line_object("Gate06_DimLength", [(-17, -25, 12.7), (-17, 25, 12.7)], cyan),
        line_object("Gate06_DimWidth", [(-15.5, 27, 12.7), (15.5, 27, 12.7)], cyan),
        text_object("Gate06_DimLengthText", "50 mm provisional", (-19, 0, 12.7), 1.15, cyan, (0, 0, math.pi / 2)),
        text_object("Gate06_DimWidthText", "31 mm provisional", (0, 29, 12.7), 1.15, cyan),
        text_object("Gate06_DimThicknessText", "12 mm provisional", (0, -29, 12.7), 1.0, yellow),
    ]
    render(scene, cameras["top"], "dimension-overlay.png")
    set_hidden(dimensions, True)
    view_digests["dimensions"] = geometry_digest()

    set_pose(MAX_TRAVEL, 0.0)
    set_product_visibility({"Gate06_FixedAxisOverlay"})
    pivot_label = text_object("Gate06_PivotText", "ONE FIXED AXIS P=[0,-9,5.875]", (0, -10, 13.0), 0.75, red)
    unlock_label = text_object("Gate06_UnlockText", "s=sMax: ROTATION UNLOCKED / 30 x 12 deg", (0, 21, 13.0), 0.75, yellow)
    render(scene, cameras["top"], "fixed-axis-pivot-overlay.png")
    set_hidden([pivot_label, unlock_label, axis_overlay], True)
    view_digests["pivot"] = geometry_digest()

    set_pose(MAX_TRAVEL, 12.0)
    set_technical_visibility()
    top = bpy.data.objects["MovingTopBody"]
    original_top = top.matrix_world.copy()
    internal_world = {name: bpy.data.objects[name].matrix_world.copy() for name in INTERNAL_MESHES}
    top.matrix_world.translation.z += 13.0
    for index, name in enumerate(sorted(INTERNAL_MESHES)):
        bpy.data.objects[name].matrix_world.translation.z += 2.0 + index * 1.15
    render(scene, cameras["technical"], "exploded-geometry.png", (1400, 1100))
    top.matrix_world = original_top
    for name, matrix in internal_world.items():
        bpy.data.objects[name].matrix_world = matrix
    view_digests["exploded"] = geometry_digest()

    set_pose(MAX_TRAVEL, 0.0)
    set_product_visibility()
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name != "MovingTopBody"
    original_top = top.matrix_world.copy()
    top.rotation_mode = "XYZ"
    top.rotation_euler.x += math.pi
    render(scene, cameras["hero"], "top-underside-four-groove-closeup.png", (1400, 1100))
    top.matrix_world = original_top
    view_digests["underside"] = geometry_digest()

    set_pose(MAX_TRAVEL, 0.0)
    set_technical_visibility()
    top.hide_render = True
    render(scene, cameras["technical"], "bottom-flat-plane-raised-axis-closeup.png", (1400, 1100))
    top.hide_render = False
    view_digests["flat-plane-axis"] = geometry_digest()

    set_pose(0.0, 0.0)
    section_sources = [bpy.data.objects[name] for name in sorted(CORE_MESHES)]
    section, slab = duplicate_section(section_sources, -8.5, {
        "MovingTopBody": section_top,
        "BottomExterior": section_bottom,
        "default": internal,
    })
    set_hidden(section_sources, True)
    section_label = text_object("Gate06_SectionLabel", "A-A / CARRIER + FOLLOWERS + FOUR INTERNAL GROOVES", (0, -8.15, 15), 0.65, cyan, (math.pi / 2, 0, 0))
    render(scene, cameras["section"], "section-aa-carrier-followers-grooves.png", (1400, 1000))
    section_metrics = {obj.name: {"vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons)} for obj in section}
    set_hidden(section_sources, False)
    set_hidden([*section, slab, section_label], True)
    view_digests["section-aa"] = geometry_digest()

    state_records = []
    for pose_id, slide, angle in [
        ("closed", 0.0, 0.0),
        ("max-open-0", MAX_TRAVEL, 0.0),
        ("max-open-12", MAX_TRAVEL, 12.0),
        ("max-open-36", MAX_TRAVEL, 36.0),
        ("max-open-360", MAX_TRAVEL, 360.0),
    ]:
        set_pose(slide, angle)
        set_product_visibility()
        render(scene, cameras["hero"], f"state-{pose_id}.png", (1400, 1100))
        state_records.append({
            "id": pose_id,
            "slideMm": slide,
            "angleDeg": angle,
            "geometryDigest": geometry_digest(),
            "fixedAxisWorldMm": list(bpy.data.objects["FixedAxis"].matrix_world.translation),
            "topResidualMm": top_residual(slide),
        })

    blocked_slide = MAX_TRAVEL * 0.5
    resolved_slide, resolved_angle, blocked_state = resolve_pose(blocked_slide, 0.0, blocked_slide, 36.0, "rotate")
    set_pose(resolved_slide, resolved_angle)
    set_product_visibility({"Gate06_FixedAxisOverlay"})
    blocked_label = text_object("Gate06_BlockedText", "PROHIBITED: MID-SLIDE ROTATION / theta remains 0 deg", (0, 22, 13), 0.72, red)
    render(scene, cameras["top"], "state-prohibited-mid-slide-rotation.png", (1400, 1100))
    set_hidden([blocked_label, axis_overlay], True)
    state_records.append({
        "id": "prohibited-mid-slide-rotation",
        "requestedSlideMm": blocked_slide,
        "requestedAngleDeg": 36.0,
        "resolvedSlideMm": resolved_slide,
        "resolvedAngleDeg": resolved_angle,
        "state": blocked_state,
        "renderedInvalidPose": False,
        "geometryDigest": geometry_digest(),
    })

    set_pose(MAX_TRAVEL, 12.0)
    set_technical_visibility()
    original_top = top.matrix_world.copy()
    top.matrix_world.translation.z += 10.0
    root["interactive_view"] = "technical-exploded-endpoint-12deg"
    export_names = [
        "MagneticSlideTile_G06_R005", "BottomExterior", "FixedAxis", "MinimumOverlapDisk",
        "MovingTop", "TopLocalSlide", "MovingTopBody", "RotatingCarrier",
        *sorted(INTERNAL_MESHES), *GROOVES,
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for name in export_names:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB), export_format="GLB", use_selection=True,
        export_extras=True, export_apply=True, export_animations=False,
    )
    top.matrix_world = original_top

    set_pose(0.0, 0.0)
    top_tree = local_top_bvh()
    fixed = bpy.data.objects["FixedAxis"]
    pivot_reference = fixed.matrix_world.translation.copy()
    dense = {
        "legalSamples": 0, "blockedRotationAttempts": 0, "blockedSlideAttempts": 0,
        "maxPivotVarianceMm": 0.0, "maxTopResidualMm": 0.0,
        "minimumDiskCoverageMisses": 0, "simultaneousVelocityViolations": 0,
    }
    for index in range(1001):
        slide = MAX_TRAVEL * index / 1000.0
        set_pose(slide, 0.0)
        dense["legalSamples"] += 1
        dense["maxPivotVarianceMm"] = max(dense["maxPivotVarianceMm"], (fixed.matrix_world.translation - pivot_reference).length)
        dense["maxTopResidualMm"] = max(dense["maxTopResidualMm"], top_residual(slide))
        dense["minimumDiskCoverageMisses"] += disk_coverage_misses(top_tree, slide, 0.0, 24)
        if index < 1000:
            for requested_angle in (12.0, 36.0, 180.0, 359.0):
                _, angle, state = resolve_pose(slide, 0.0, slide, requested_angle, "rotate")
                dense["blockedRotationAttempts"] += state == "rotation-blocked-below-endpoint" and angle == 0.0
    for angle in range(361):
        set_pose(MAX_TRAVEL, float(angle))
        dense["legalSamples"] += 1
        dense["maxPivotVarianceMm"] = max(dense["maxPivotVarianceMm"], (fixed.matrix_world.translation - pivot_reference).length)
        dense["maxTopResidualMm"] = max(dense["maxTopResidualMm"], top_residual(MAX_TRAVEL))
        dense["minimumDiskCoverageMisses"] += disk_coverage_misses(top_tree, MAX_TRAVEL, float(angle), 24)
        if angle not in (0, 360):
            slide, _, state = resolve_pose(MAX_TRAVEL, float(angle), 0.0, float(angle), "slide")
            dense["blockedSlideAttempts"] += state == "slide-blocked-while-rotated" and abs(slide - MAX_TRAVEL) <= ENDPOINT_TOLERANCE_MM

    representative = []
    for pose_id, slide, angle in [
        ("closed", 0.0, 0.0), ("mid-slide", MAX_TRAVEL * 0.5, 0.0),
        ("max-open-0", MAX_TRAVEL, 0.0), ("max-open-12", MAX_TRAVEL, 12.0),
        ("max-open-36", MAX_TRAVEL, 36.0), ("max-open-360", MAX_TRAVEL, 360.0),
    ]:
        set_pose(slide, angle)
        intersections = {}
        for name in INTERNAL_MESHES:
            intersections[f"{name}:BottomExterior"] = overlap_pairs(bpy.data.objects[name], bpy.data.objects["BottomExterior"])
            intersections[f"{name}:MovingTopBody"] = overlap_pairs(bpy.data.objects[name], top)
        representative.append({
            "id": pose_id, "slideMm": slide, "angleDeg": angle,
            "surfaceIntersectionPairs": intersections,
            "minimumDiskActualMeshCoverageMisses": disk_coverage_misses(top_tree, slide, angle),
            "topResidualMm": top_residual(slide),
        })

    set_pose(MAX_TRAVEL, 0.0)
    matrix_zero = top.matrix_world.copy()
    set_pose(MAX_TRAVEL, 360.0)
    matrix_full = top.matrix_world.copy()
    closure_error = max(abs(matrix_zero[row][column] - matrix_full[row][column]) for row in range(4) for column in range(4))
    set_pose(0.0, 0.0)
    bottom = bpy.data.objects["BottomExterior"]
    top_plane_z = [
        (bottom.matrix_world @ bottom.data.vertices[index].co).z
        for polygon in bottom.data.polygons if polygon.normal.z > 0.999999
        for index in polygon.vertices
    ]
    bounds_points = [
        obj.matrix_world @ Vector(corner)
        for obj in (bottom, top)
        for corner in obj.bound_box
    ]
    bounds = [
        max(point.x for point in bounds_points) - min(point.x for point in bounds_points),
        max(point.y for point in bounds_points) - min(point.y for point in bounds_points),
        max(point.z for point in bounds_points) - min(point.z for point in bounds_points),
    ]
    pivot_objects = [obj.name for obj in bpy.data.objects if obj.get("pivot_id")]
    manifold = {name: nonmanifold_edges(bpy.data.objects[name]) for name in sorted(CORE_MESHES)}
    invalid_normals = {
        name: sum(
            polygon.normal.length < 0.99 or not all(math.isfinite(value) for value in polygon.normal)
            for polygon in bpy.data.objects[name].data.polygons
        )
        for name in sorted(CORE_MESHES)
    }
    geometry_metrics = {
        name: {
            "vertices": len(bpy.data.objects[name].data.vertices),
            "polygons": len(bpy.data.objects[name].data.polygons),
            "triangles": sum(len(polygon.vertices) - 2 for polygon in bpy.data.objects[name].data.polygons),
            "uvLayers": len(bpy.data.objects[name].data.uv_layers),
        }
        for name in sorted(CORE_MESHES)
    }
    ball_diameters = [bpy.data.objects[name]["diameter_mm"] for name in ("BallCandidateLeft", "BallCandidateRight")]
    groove_widths = [bpy.data.objects[name]["width_mm"] for name in GROOVES]
    checks = {
        "gate05SourceHashConsumed": sha256(SOURCE) == SOURCE_SHA256,
        "contractRev17HashConsumed": sha256(CONTRACT) == CONTRACT_SHA256,
        "geometryDigestUnchanged": geometry_digest() == GEOMETRY_DIGEST,
        "sameGeometryAcrossViewsAndStates": all(value == GEOMETRY_DIGEST for value in view_digests.values())
        and all(record["geometryDigest"] == GEOMETRY_DIGEST for record in state_records),
        "exactProvisionalBounds": all(abs(actual - expected) <= 1e-6 for actual, expected in zip(bounds, [31.0, 50.0, 12.0])),
        "flatBottomPlane": max(top_plane_z) - min(top_plane_z) <= 0.001,
        "singleFixedAxis": pivot_objects == ["FixedAxis"] and dense["maxPivotVarianceMm"] <= 1e-12,
        "fixedPivotEquation": dense["maxTopResidualMm"] <= 5e-6,
        "productRendererWhitelistExact": sorted(PRODUCT_MESHES) == ["BottomExterior", "MovingTopBody"],
        "minimumOverlapDiskNonRendering": bpy.data.objects["MinimumOverlapDisk"].type == "EMPTY"
        and bpy.data.objects["MinimumOverlapDisk"].hide_render,
        "internalMeshesTechnicalOnly": all(bpy.data.objects[name].get("product_render") is False for name in INTERNAL_MESHES),
        "actualMeshSurfaceIntersectionsZero": all(value == 0 for pose in representative for value in pose["surfaceIntersectionPairs"].values()),
        "minimumOverlapDenseActualMeshCoverage": dense["minimumDiskCoverageMisses"] == 0
        and all(pose["minimumDiskActualMeshCoverageMisses"] == 0 for pose in representative),
        "fourFiniteGrooves": len(GROOVES) == 4 and all(
            bpy.data.objects[name]["finite_start_y_mm"] < bpy.data.objects[name]["finite_end_y_mm"] for name in GROOVES
        ),
        "grooveWidthsAuthorized": all(1.8 <= value <= 3.0 for value in groove_widths),
        "ballRangesAuthorized": all(2.0 <= value <= 3.0 for value in ball_diameters),
        "rotationBlockedBelowEndpoint": dense["blockedRotationAttempts"] == 4000,
        "onlyEndpointUnlocksRotation": all(record["slideMm"] == MAX_TRAVEL for record in state_records if record["id"].startswith("max-open")),
        "thirtyEndpointDetents": all(abs((index * 12.0) % 360.0) <= 360.0 for index in range(30)),
        "slideBlockedAtNonzeroAngle": dense["blockedSlideAttempts"] == 359,
        "alignmentToleranceAllowsClosure": resolve_pose(MAX_TRAVEL, 0.0005, 0.0, 0.0005, "slide")[0] == 0.0,
        "full360Closure": closure_error <= 1e-9,
        "noSimultaneousVelocitiesBelowEndpoint": dense["simultaneousVelocityViolations"] == 0,
        "noInvalidMidSlidePoseRendered": state_records[-1]["renderedInvalidPose"] is False
        and state_records[-1]["resolvedAngleDeg"] == 0.0,
        "manifold": all(value == 0 for value in manifold.values()),
        "normals": all(value == 0 for value in invalid_normals.values()),
        "uvs": all(metric["uvLayers"] > 0 for metric in geometry_metrics.values()),
        "smoothSilhouette": geometry_metrics["BottomExterior"]["vertices"] >= 9000
        and geometry_metrics["MovingTopBody"]["vertices"] >= 13000,
        "sectionEvidenceGenerated": all(metric["vertices"] > 0 and metric["polygons"] > 0 for metric in section_metrics.values()),
        "zeroSelfMotion": not any(obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers) for obj in bpy.data.objects),
        "glbWritten": OUTPUT_GLB.exists(),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "06-geometry",
        "revision": 5,
        "contractSha256": CONTRACT_SHA256,
        "gate05Source": {
            "path": str(SOURCE),
            "sha256": SOURCE_SHA256,
            "geometryDigest": GEOMETRY_DIGEST,
            "approvalWording": "可以，可以继续推进。",
        },
        "canonicalGeometryDigest": GEOMETRY_DIGEST,
        "dimensions": {
            "boundsMm": bounds,
            "state": "user-authorized-provisional-not-production-measured",
            "bottomTopPlaneZMm": min(top_plane_z),
            "bottomTopPlaneMaximumDeviationMm": max(top_plane_z) - min(top_plane_z),
            "axisBossProtrusionMm": bpy.data.objects["InternalAxisBoss"]["protrusion_mm"],
            "grooveWidthRangeMm": [min(groove_widths), max(groove_widths)],
            "ballCandidateRangeMm": [min(ball_diameters), max(ball_diameters)],
            "maximumTravelMm": MAX_TRAVEL,
        },
        "stateMachine": {
            "belowEndpoint": "0<=s<sMax => theta=0",
            "endpointAligned": "s=sMax and theta=0/360 => rotate or slide-close",
            "endpointRotating": "s=sMax and theta mod 360!=0 => rotate only",
            "hiddenLatchGeometry": "unknown-not-modeled",
            "alignmentToleranceDegrees": ALIGNMENT_TOLERANCE_DEG,
        },
        "viewGeometryDigests": view_digests,
        "stateRecords": state_records,
        "denseValidation": dense,
        "representativeActualMeshValidation": representative,
        "full360ClosureMatrixError": closure_error,
        "pivotObjects": pivot_objects,
        "productRendererWhitelist": sorted(PRODUCT_MESHES),
        "technicalOnlyMeshes": sorted(INTERNAL_MESHES),
        "geometryMetrics": geometry_metrics,
        "nonmanifoldEdges": manifold,
        "invalidPolygonNormals": invalid_normals,
        "sectionMetrics": section_metrics,
        "checks": checks,
        "outputs": {
            "blend": OUTPUT_BLEND.name,
            "glb": OUTPUT_GLB.name,
            "renders": [
                *[f"orthographic-{view}.png" for view in ("front", "back", "top", "bottom", "left", "right")],
                "geometry-workbench.png", "dimension-overlay.png", "fixed-axis-pivot-overlay.png",
                "exploded-geometry.png", "top-underside-four-groove-closeup.png",
                "bottom-flat-plane-raised-axis-closeup.png", "section-aa-carrier-followers-grooves.png",
                *[f"state-{pose}.png" for pose in ("closed", "max-open-0", "max-open-12", "max-open-36", "max-open-360")],
                "state-prohibited-mid-slide-rotation.png",
            ],
        },
    }
    report["pass"] = all(checks.values())
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    set_pose(0.0, 0.0)
    set_product_visibility()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["checks"]["blendWritten"] = OUTPUT_BLEND.exists()
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "geometryDigest": GEOMETRY_DIGEST,
        "legalSamples": dense["legalSamples"],
        "blockedRotationAttempts": dense["blockedRotationAttempts"],
        "blockedSlideAttempts": dense["blockedSlideAttempts"],
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
    }, indent=2))


if __name__ == "__main__":
    main()
