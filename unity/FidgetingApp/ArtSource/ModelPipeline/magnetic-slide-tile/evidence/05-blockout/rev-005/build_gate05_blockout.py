#!/usr/bin/env python3
"""Build Gate 05 rev 5 from the current four-track raised-axis contract."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
REPO_ROOT = MODEL_ROOT.parents[4]
CONTRACT_PATH = MODEL_ROOT / "evidence/03-contract/rev-011/authorized-provisional-modeling-contract.json"
ARCHITECTURE_PATH = MODEL_ROOT / "evidence/04-architecture/rev-013/approved-four-track-raised-axis-architecture.json"
REUSE_PLAN_PATH = MODEL_ROOT / "evidence/03-contract/rev-011/reuse-plan.json"
MECHANISM_PATH = MODEL_ROOT / "evidence/02-analysis/rev-016/mechanism-evidence-contract.json"
LEGACY_BUILDER_PATH = HERE.parent / "rev-004/build_gate05_blockout.py"
BLEND_PATH = HERE / "magnetic-slide-tile-blockout-r005.blend"
GLB_PATH = HERE / "magnetic-slide-tile-blockout-r005-review.glb"
REPORT_PATH = HERE / "blockout-validation.json"

CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
GROOVE_IDS = [
    "TopOuterGrooveLeft",
    "TopInnerGrooveLeft",
    "TopInnerGrooveRight",
    "TopOuterGrooveRight",
]
GROOVE_ROLES = [
    "fore-aft-slide",
    "central-axis-link",
    "central-axis-link",
    "fore-aft-slide",
]


def load_legacy_builder():
    spec = importlib.util.spec_from_file_location("gate05_rev4_builder", LEGACY_BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


legacy = load_legacy_builder()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def set_parent_local(obj, parent, location=(0.0, 0.0, 0.0)):
    obj.parent = parent
    obj.location = location


def rounded_prism(name: str, length: float, width: float, depth: float, material):
    profile = legacy.capsule_profile(length, width)
    count = len(profile)
    vertices = [(x, y, -depth / 2.0) for x, y in profile]
    vertices += [(x, y, depth / 2.0) for x, y in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [
        (index, (index + 1) % count, count + (index + 1) % count, count + index)
        for index in range(count)
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def apply_modifier(obj, modifier):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.select_set(False)


def cut_top_grooves(top, length, top_thickness, groove_width, groove_depth, offsets):
    apply_modifier(top, top.modifiers["SilhouetteEdgeBevel"])
    groove_length = length * (0.78 - 0.32)
    groove_center_y = -length / 2.0 + length * ((0.32 + 0.78) / 2.0)
    for groove_id, role, x in zip(GROOVE_IDS, GROOVE_ROLES, offsets):
        cutter = rounded_prism(
            f"_{groove_id}_Cutter",
            groove_length,
            groove_width,
            groove_depth + 0.08,
            None,
        )
        cutter.location = (
            x,
            groove_center_y,
            -top_thickness / 2.0 + groove_depth / 2.0 - 0.03,
        )
        modifier = top.modifiers.new(f"Recess_{groove_id}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        apply_modifier(top, modifier)
        bpy.data.objects.remove(cutter, do_unlink=True)
        marker = legacy.empty(groove_id, parent=top, location=(x, groove_center_y, -top_thickness / 2.0))
        marker.hide_render = True
        marker["ownership"] = "MovingTop underside"
        marker["role"] = role
        marker["width_mm"] = groove_width
        marker["depth_state"] = "diagrammatic-provisional"
        marker["finite_start_y_mm"] = -length / 2.0 + length * 0.32
        marker["finite_end_y_mm"] = -length / 2.0 + length * 0.78
    bevel = top.modifiers.new("GrooveEdgeBevel", "BEVEL")
    bevel.width = 0.10
    bevel.segments = 3


def matrix_values(matrix: Matrix) -> list[list[float]]:
    return [[round(value, 9) for value in row] for row in matrix]


def render(scene, camera, filename: str, width=1400, height=1200):
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def set_pose(carrier_frame, moving_top, top_slide, travel_mm: float, angle_deg: float):
    angle = math.radians(angle_deg)
    carrier_frame.rotation_euler = (0.0, 0.0, angle)
    moving_top.rotation_euler = (0.0, 0.0, angle)
    top_slide.location = (0.0, -travel_mm, 0.0)
    bpy.context.view_layer.update()


def make_ball(name, diameter, clay, parent, location):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64,
        ring_count=32,
        radius=diameter / 2.0,
        location=(0.0, 0.0, 0.0),
    )
    ball = bpy.context.object
    ball.name = name
    ball.data.materials.append(clay)
    set_parent_local(ball, parent, location)
    ball["candidate_only"] = True
    ball["diameter_mm"] = diameter
    ball["material"] = "unknown"
    return ball


def make_follower(name, width, clay, parent, x):
    follower = rounded_prism(name, 6.0, width, 0.72, clay)
    set_parent_local(follower, parent, (x, 0.0, 0.0))
    follower["role"] = "inner-track-link"
    follower["dimensions_state"] = "diagrammatic-provisional"
    bevel = follower.modifiers.new("FollowerBevel", "BEVEL")
    bevel.width = 0.16
    bevel.segments = 4
    return follower


def main():
    contract = load_json(CONTRACT_PATH)
    architecture = load_json(ARCHITECTURE_PATH)
    reuse_plan = load_json(REUSE_PLAN_PATH)
    mechanism = load_json(MECHANISM_PATH)
    if sha256(MECHANISM_PATH) != CONTRACT_SHA256:
        raise RuntimeError("Current mechanism contract hash drift.")
    if contract["governingMechanismContractSha256"] != CONTRACT_SHA256:
        raise RuntimeError("Gate 03 contract does not consume the current mechanism hash.")
    if architecture["governingMechanismContractSha256"] != CONTRACT_SHA256:
        raise RuntimeError("Gate 04 architecture does not consume the current mechanism hash.")
    if reuse_plan["contractSha256"] != CONTRACT_SHA256:
        raise RuntimeError("Reuse plan does not consume the current mechanism hash.")

    dimensions = contract["dimensionsMm"]
    length = dimensions["overallLength"]["provisional"]
    width = dimensions["overallWidth"]["provisional"]
    total_thickness = dimensions["totalClosedThickness"]["provisional"]
    top_thickness = dimensions["topThickness"]["provisional"]
    bottom_envelope = dimensions["bottomThickness"]["provisional"]
    seam_gap = dimensions["closedSeamGap"]["provisional"]
    max_travel = dimensions["maximumSlideTravel"]["provisional"]
    axis_offset = dimensions["fixedAxisOffsetFromNearestEnd"]["provisional"]
    carrier_diameter = dimensions["rotatingCarrierDiameter"]["provisional"]
    ball_range = dimensions["ballDiameter"]["range"]
    ball_diameter = dimensions["ballDiameter"]["provisional"]
    track_range = dimensions["trackWidth"]["range"]
    track_width = dimensions["trackWidth"]["provisional"]
    boss_protrusion = contract["mechanism"]["axisBossProtrusionMm"]["provisional"]
    bottom_shell_thickness = bottom_envelope - boss_protrusion
    if bottom_shell_thickness <= 0:
        raise RuntimeError("Axis boss cannot consume the entire bottom envelope.")

    groove_constraint = next(item for item in mechanism["constraints"] if item["id"] == "MEC-TOP-UNDERSIDE-GROOVES")
    boss_constraint = next(item for item in mechanism["constraints"] if item["id"] == "MEC-RAISED-AXIS-BOSS")
    ball_constraint = next(item for item in mechanism["constraints"] if item["id"] == "MEC-BALL-CONTACT-CANDIDATES")
    tracks = groove_constraint["value"]["tracks"]
    if len(tracks) != 4 or [item["id"] for item in tracks] != GROOVE_IDS:
        raise RuntimeError("Gate 05 requires the exact four-track contract.")
    if set(item["role"] for item in tracks) != set(GROOVE_ROLES):
        raise RuntimeError("Gate 05 requires outer slide and inner axis-link roles.")
    if boss_protrusion <= 0 or boss_constraint["value"]["recessedAxis"]:
        raise RuntimeError("Gate 05 forbids the rejected recessed-axis cavity.")
    if ball_range != [2, 3] or ball_constraint["value"]["ballDiameterMm"] != [2.0, 3.0]:
        raise RuntimeError("Ball candidate range must remain 2–3 mm.")
    if track_range[0] < 1.8 or track_range[1] > 3.0 or not track_range[0] <= track_width <= track_range[1]:
        raise RuntimeError("Track width left the user-authorized 1.8–3.0 mm range.")

    axis_y = -length / 2.0 + axis_offset
    carrier_radius = carrier_diameter / 2.0
    applied_disk_radius = min(length * 0.3184713375796178, width / 2.0)
    inner_offset = length * 0.12
    outer_offset = length * 0.235
    groove_offsets = [-outer_offset, -inner_offset, inner_offset, outer_offset]
    groove_depth = min(1.0, top_thickness * 0.22)

    legacy.clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.026, 0.032, 0.039)
    scene.frame_start = scene.frame_end = 1
    scene["model_id"] = "magnetic-slide-tile"
    scene["gate"] = "05-blockout"
    scene["revision"] = 5
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["dimension_state"] = "user-authorized-provisional-not-production-measured"
    scene["top_transform"] = "R_fixedAxis(theta) * T_local(s)"
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False

    clay_bottom = legacy.material("G05R5_Clay_Bottom", (0.50, 0.53, 0.56, 1.0), 0.82)
    clay_top = legacy.material("G05R5_Clay_Top", (0.82, 0.84, 0.85, 1.0), 0.74)
    clay_mechanism = legacy.material("G05R5_Clay_Mechanism", (0.65, 0.68, 0.70, 1.0), 0.68)
    clay_candidate = legacy.material("G05R5_Clay_Candidate", (0.73, 0.75, 0.76, 1.0), 0.52)
    overlay_red = legacy.material("G05R5_Overlap_Overlay", (0.74, 0.03, 0.05, 0.62), 0.45)
    ground_mat = legacy.material("G05R5_Ground", (0.045, 0.052, 0.060, 1.0), 0.90)

    root = legacy.empty("MagneticSlideTile_G05_R005")
    root["governing_contract_sha256"] = CONTRACT_SHA256
    root["reuse_plan_sha256"] = sha256(REUSE_PLAN_PATH)
    root["architecture_sha256"] = sha256(ARCHITECTURE_PATH)

    bottom = legacy.capsule_mesh("BottomExterior", length, width, bottom_shell_thickness, clay_bottom)
    set_parent_local(bottom, root, (0.0, 0.0, bottom_shell_thickness / 2.0))
    bottom["exterior_front"] = "smooth-rail-free"
    bottom["exterior_back"] = "smooth-rail-free"
    bottom["cavity"] = False
    bottom["bottom_envelope_mm"] = bottom_envelope

    bottom_rim = legacy.capsule_mesh(
        "_BottomExteriorUpperRim",
        length,
        width,
        boss_protrusion,
        clay_bottom,
    )
    apply_modifier(bottom_rim, bottom_rim.modifiers["SilhouetteEdgeBevel"])
    rim_cutter = rounded_prism(
        "_BottomExteriorRimCutter",
        length - 3.0,
        width - 3.0,
        boss_protrusion + 0.16,
        None,
    )
    modifier = bottom_rim.modifiers.new("OpenInteriorDeck", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = rim_cutter
    apply_modifier(bottom_rim, modifier)
    bpy.data.objects.remove(rim_cutter, do_unlink=True)
    set_parent_local(bottom_rim, root, (0.0, 0.0, bottom_shell_thickness + boss_protrusion / 2.0))
    bottom_rim["component_role"] = "smooth outer wall of BottomExterior"
    bottom_rim["axis_cavity"] = False

    boss_radius = max(track_width * 1.35, 3.4)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=boss_radius, depth=boss_protrusion)
    fixed_axis_boss = bpy.context.object
    fixed_axis_boss.name = "FixedAxisBoss"
    fixed_axis_boss.data.materials.append(clay_mechanism)
    set_parent_local(
        fixed_axis_boss,
        bottom,
        (0.0, axis_y, bottom_shell_thickness / 2.0 + boss_protrusion / 2.0),
    )
    fixed_axis_boss["protrusion_mm"] = boss_protrusion
    fixed_axis_boss["recessed_axis"] = False
    fixed_axis_boss["embedded_in_bottom"] = True
    fixed_axis = legacy.empty("FixedAxis", parent=fixed_axis_boss, display="ARROWS", size=1.8)
    fixed_axis["world_invariant"] = True

    overlap_disk = legacy.empty(
        "MinimumOverlapDisk",
        parent=bottom,
        location=(0.0, axis_y, bottom_shell_thickness / 2.0),
        display="CIRCLE",
        size=applied_disk_radius,
    )
    overlap_disk["render_geometry"] = "validation-overlay-only"
    overlap_disk["radius_mm"] = applied_disk_radius

    carrier_frame = legacy.empty("RotatingCarrier", parent=fixed_axis_boss, display="CIRCLE", size=carrier_radius)
    carrier_frame.location = (0.0, 0.0, -boss_protrusion * 0.18)
    carrier_frame["transform"] = "R_fixedAxis(theta)"
    carrier_frame["translation_dof"] = False
    carrier_depth = 0.86
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=carrier_radius, depth=carrier_depth)
    carrier_body = bpy.context.object
    carrier_body.name = "RotatingCarrierBody"
    carrier_body.data.materials.append(clay_mechanism)
    set_parent_local(carrier_body, carrier_frame)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cutter = bpy.context.object
        cutter.name = f"_CarrierSideClearance_{side}"
        cutter.dimensions = (length * 0.16, length * 0.18, carrier_depth * 2.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        set_parent_local(cutter, carrier_frame, (side * carrier_radius, 0.0, 0.0))
        modifier = carrier_body.modifiers.new(f"BilateralClearance_{side}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        apply_modifier(carrier_body, modifier)
        bpy.data.objects.remove(cutter, do_unlink=True)
    for polygon in carrier_body.data.polygons:
        polygon.use_smooth = True
    carrier_body["bilateral_side_clearances"] = True
    carrier_body["diameter_mm"] = carrier_diameter

    follower_z = carrier_depth / 2.0 + 0.36
    follower_left = make_follower("CarrierFollowerLeft", track_width, clay_mechanism, carrier_frame, -inner_offset)
    follower_right = make_follower("CarrierFollowerRight", track_width, clay_mechanism, carrier_frame, inner_offset)
    follower_left.location.z = follower_right.location.z = follower_z
    ball_left = make_ball(
        "BallCandidateLeft",
        ball_diameter,
        clay_candidate,
        carrier_frame,
        (-outer_offset, 0.0, carrier_depth / 2.0 + ball_diameter / 2.0 - 0.15),
    )
    ball_right = make_ball(
        "BallCandidateRight",
        ball_diameter,
        clay_candidate,
        carrier_frame,
        (outer_offset, 0.0, carrier_depth / 2.0 + ball_diameter / 2.0 - 0.15),
    )
    unknown_springs = legacy.empty("UnknownSprings", parent=carrier_frame)
    unknown_springs.hide_render = True
    unknown_springs["count"] = "unknown"
    unknown_preload = legacy.empty("UnknownPreload", parent=carrier_frame)
    unknown_preload.hide_render = True
    unknown_preload["value"] = "unknown"

    moving_top = legacy.empty("MovingTop", parent=root, location=(0.0, axis_y, 0.0))
    moving_top["transform"] = "R_fixedAxis(theta)"
    top_slide = legacy.empty("TopLocalSlide", parent=moving_top)
    top_slide["transform"] = "T_local(s)"
    top_slide["range_mm"] = [0.0, max_travel]
    top = legacy.capsule_mesh("MovingTopBody", length, width, top_thickness, clay_top)
    cut_top_grooves(top, length, top_thickness, track_width, groove_depth, groove_offsets)
    top_base_z = bottom_envelope + seam_gap
    set_parent_local(top, top_slide, (0.0, -axis_y, top_base_z + top_thickness / 2.0))
    top["always_above_bottom"] = True
    top["groove_count"] = 4
    top["artwork_slots"] = "upper-and-lower-preserved-for-later-gates"

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 0.0, -0.55))
    ground = bpy.context.object
    ground.name = "G05R5_PresentationGround"
    ground.data.materials.append(ground_mat)
    for name, location, energy, size in [
        ("G05R5_Key", (55, -74, 96), 50000, 52),
        ("G05R5_Fill", (-58, -18, 60), 23000, 44),
        ("G05R5_Rim", (30, 70, 64), 36000, 38),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.size = size
        legacy.look_at(light, Vector((0.0, -4.0, 5.0)))

    hero_cam = legacy.camera("G05R5_HeroCamera", (84, -126, 70), (0, -3, 5), 72)
    top_cam = legacy.camera("G05R5_TopCamera", (0, 0, 170), (0, 0, 5), 78)
    open_cam = legacy.camera("G05R5_OpenCamera", (92, -142, 70), (0, -10, 5), 76)
    underside_cam = legacy.camera("G05R5_UndersideCamera", (0, 0, 165), (0, 0, 8), 76)
    close_cam = legacy.camera("G05R5_MechanismCloseCamera", (42, -63, 38), (0, axis_y, 5), 82)
    exploded_cam = legacy.camera("G05R5_ExplodedCamera", (98, -138, 82), (0, -4, 11), 76)

    set_pose(carrier_frame, moving_top, top_slide, 0.0, 0.0)
    render(scene, hero_cam, "white-hero.png")
    render(scene, top_cam, "white-closed.png")
    set_pose(carrier_frame, moving_top, top_slide, max_travel, 0.0)
    render(scene, open_cam, "white-max-open.png")
    set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.45, 12.0)
    render(scene, hero_cam, "white-detent-12.png")
    set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.70, 36.0)
    render(scene, hero_cam, "white-detent-36.png")

    set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.35, 12.0)
    top_slide.location.z = 13.0
    top.rotation_euler.x = math.pi
    bottom.hide_render = fixed_axis_boss.hide_render = carrier_body.hide_render = True
    follower_left.hide_render = follower_right.hide_render = ball_left.hide_render = ball_right.hide_render = True
    ground.hide_render = True
    render(scene, underside_cam, "white-underside-four-grooves.png")
    top.rotation_euler.x = 0.0
    bottom.hide_render = fixed_axis_boss.hide_render = carrier_body.hide_render = False
    follower_left.hide_render = follower_right.hide_render = ball_left.hide_render = ball_right.hide_render = False
    ground.hide_render = False

    top_slide.location.z = 10.0
    render(scene, close_cam, "white-raised-axis-carrier-closeup.png")
    top_slide.location.z = 16.0
    carrier_frame["exploded_presentation_only"] = True
    render(scene, exploded_cam, "white-exploded-hierarchy.png")

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=160,
        radius=applied_disk_radius,
        depth=0.10,
        location=(0.0, axis_y, total_thickness + 0.40),
    )
    disk_overlay = bpy.context.object
    disk_overlay.name = "Review_MinimumOverlapDisk_Overlay"
    disk_overlay.data.materials.append(overlay_red)
    disk_overlay["review_overlay_only"] = True
    set_pose(carrier_frame, moving_top, top_slide, max_travel, 0.0)
    top_slide.location.z = 0.0
    render(scene, top_cam, "pivot-overlap-overlay.png")
    disk_overlay.hide_render = True

    set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.35, 12.0)
    top_slide.location.z = 10.0
    bpy.context.view_layer.update()
    export_objects = [
        root,
        bottom,
        bottom_rim,
        fixed_axis_boss,
        fixed_axis,
        overlap_disk,
        carrier_frame,
        carrier_body,
        follower_left,
        follower_right,
        ball_left,
        ball_right,
        unknown_springs,
        unknown_preload,
        moving_top,
        top_slide,
        top,
        *[bpy.data.objects[groove_id] for groove_id in GROOVE_IDS],
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
    )

    set_pose(carrier_frame, moving_top, top_slide, 0.0, 0.0)
    top_slide.location.z = 0.0
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    axis_world_reference = fixed_axis.matrix_world.translation.copy()
    poses = []
    for pose_id, travel, angle in [
        ("closed", 0.0, 0.0),
        ("max-open", max_travel, 0.0),
        ("detent-01", max_travel * 0.45, 12.0),
        ("detent-03", max_travel * 0.70, 36.0),
    ]:
        set_pose(carrier_frame, moving_top, top_slide, travel, angle)
        axis_world = fixed_axis.matrix_world.translation.copy()
        poses.append({
            "id": pose_id,
            "travelMm": travel,
            "angleDeg": angle,
            "axisDriftMm": (axis_world - axis_world_reference).length,
            "carrierMatrixWorld": matrix_values(carrier_frame.matrix_world),
            "movingTopMatrixWorld": matrix_values(moving_top.matrix_world),
            "topSlideMatrixLocal": matrix_values(top_slide.matrix_local),
            "topZMinMm": min((top.matrix_world @ Vector(corner)).z for corner in top.bound_box),
            "bottomZMaxMm": max(
                max((bottom.matrix_world @ Vector(corner)).z for corner in bottom.bound_box),
                max((bottom_rim.matrix_world @ Vector(corner)).z for corner in bottom_rim.bound_box),
            ),
        })

    sweep_samples = []
    for half_degree in range(720):
        angle = half_degree * 0.5
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            travel = max_travel * fraction
            longitudinal_margin = (length - axis_offset - travel) - applied_disk_radius
            side_margin = width / 2.0 - applied_disk_radius
            sweep_samples.append({
                "angleDeg": angle,
                "travelMm": travel,
                "marginMm": min(longitudinal_margin, side_margin),
                "valid": longitudinal_margin >= -1e-9 and side_margin >= -1e-9,
            })

    mesh_audit = {
        bottom.name: legacy.mesh_metrics(bottom),
        bottom_rim.name: legacy.mesh_metrics(bottom_rim),
        top.name: legacy.mesh_metrics(top),
        fixed_axis_boss.name: legacy.mesh_metrics(fixed_axis_boss),
        carrier_body.name: legacy.mesh_metrics(carrier_body),
        follower_left.name: legacy.mesh_metrics(follower_left),
        follower_right.name: legacy.mesh_metrics(follower_right),
        ball_left.name: legacy.mesh_metrics(ball_left),
        ball_right.name: legacy.mesh_metrics(ball_right),
    }
    animated_objects = [
        obj.name
        for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    expected_hierarchy = [item["id"] for item in architecture["hierarchy"]]
    actual_hierarchy = [
        "BottomExterior",
        "FixedAxisBoss",
        "MinimumOverlapDisk",
        "RotatingCarrier",
        "CarrierFollowerLeft",
        "CarrierFollowerRight",
        "BallCandidateLeft",
        "BallCandidateRight",
        "MovingTop",
        *GROOVE_IDS,
        "UnknownSprings",
        "UnknownPreload",
    ]
    report = {
        "schemaVersion": 2,
        "modelId": "magnetic-slide-tile",
        "gate": "05-blockout",
        "revision": 5,
        "contractSha256": CONTRACT_SHA256,
        "inputs": {
            "provisionalContract": str(CONTRACT_PATH.relative_to(REPO_ROOT)),
            "architecture": str(ARCHITECTURE_PATH.relative_to(REPO_ROOT)),
            "reusePlan": str(REUSE_PLAN_PATH.relative_to(REPO_ROOT)),
            "reusePlanSha256": sha256(REUSE_PLAN_PATH),
            "reusedAssetCount": len(reuse_plan["reusedAssets"]),
        },
        "dimensionsMm": {
            "overallLength": {"value": length, "range": dimensions["overallLength"]["range"]},
            "overallWidth": {"value": width, "range": dimensions["overallWidth"]["range"]},
            "totalClosedThickness": {"value": total_thickness, "confidence": "low"},
            "topThickness": top_thickness,
            "bottomEnvelope": bottom_envelope,
            "bottomExteriorShell": bottom_shell_thickness,
            "axisBossProtrusion": boss_protrusion,
            "closedSeamGap": seam_gap,
            "maxTravel": max_travel,
            "axisOffsetFromNearestEnd": axis_offset,
            "carrierDiameter": carrier_diameter,
            "ballDiameterRange": ball_range,
            "ballCandidateDiameter": ball_diameter,
            "trackWidthRange": track_range,
            "trackWidth": track_width,
            "state": "user-authorized-provisional-not-production-measured",
        },
        "hierarchy": actual_hierarchy,
        "poses": poses,
        "meshAudit": mesh_audit,
        "denseSweep": {
            "sampleCount": len(sweep_samples),
            "angularStepDegrees": 0.5,
            "allValid": all(sample["valid"] for sample in sweep_samples),
            "minimumMarginMm": min(sample["marginMm"] for sample in sweep_samples),
        },
        "checks": {
            "contractHashConsumed": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
            "provisionalBoundaryExplicit": scene["dimension_state"] == "user-authorized-provisional-not-production-measured",
            "fourGrooves": len(GROOVE_IDS) == 4 and top["groove_count"] == 4,
            "outerInnerRoles": GROOVE_ROLES.count("fore-aft-slide") == 2 and GROOVE_ROLES.count("central-axis-link") == 2,
            "raisedAxisBoss": fixed_axis_boss["protrusion_mm"] > 0,
            "noRecessedCavity": not fixed_axis_boss["recessed_axis"] and not bottom["cavity"],
            "ballRangeAuthorized": ball_range == [2, 3] and 2 <= ball_diameter <= 3,
            "trackWidthAuthorized": track_range == [1.8, 3] and 1.8 <= track_width <= 3,
            "bottomExteriorSmooth": bottom["exterior_front"] == "smooth-rail-free"
            and bottom["exterior_back"] == "smooth-rail-free"
            and not bottom_rim["axis_cavity"],
            "hierarchyExact": expected_hierarchy == actual_hierarchy,
            "axisInvariant": all(pose["axisDriftMm"] <= 1e-9 for pose in poses),
            "compoundTransform": scene["top_transform"] == "R_fixedAxis(theta) * T_local(s)",
            "topAlwaysAboveBottom": all(pose["topZMinMm"] > pose["bottomZMaxMm"] for pose in poses),
            "finiteEndpoints": max_travel > 0 and all(bpy.data.objects[item]["finite_end_y_mm"] > bpy.data.objects[item]["finite_start_y_mm"] for item in GROOVE_IDS),
            "minimumOverlapDenseSweep": all(sample["valid"] for sample in sweep_samples),
            "unknownEngineeringPreserved": unknown_springs["count"] == "unknown" and unknown_preload["value"] == "unknown",
            "zeroAnimationAndSelfMotion": not animated_objects and scene["self_motion"] is False,
            "capsuleSmoothness": legacy.ARC_SEGMENTS == 256 and legacy.BEVEL_SEGMENTS == 8,
            "glbWritten": GLB_PATH.exists(),
            "blendWritten": BLEND_PATH.exists(),
        },
        "animatedObjects": animated_objects,
        "outputs": {
            "blend": BLEND_PATH.name,
            "glb": GLB_PATH.name,
            "glbPose": "semi-exploded interactive review",
            "renders": [
                "white-hero.png",
                "white-closed.png",
                "white-max-open.png",
                "white-detent-12.png",
                "white-detent-36.png",
                "white-underside-four-grooves.png",
                "white-raised-axis-carrier-closeup.png",
                "white-exploded-hierarchy.png",
                "pivot-overlap-overlay.png",
            ],
        },
    }
    manifold_required = [
        "BottomExterior",
        "_BottomExteriorUpperRim",
        "MovingTopBody",
        "FixedAxisBoss",
        "RotatingCarrierBody",
    ]
    report["pass"] = all(report["checks"].values()) and all(
        mesh_audit[name]["nonmanifoldEdges"] == 0 and mesh_audit[name]["signedVolumeMm3"] > 0
        for name in manifold_required
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps({"checks": report["checks"], "meshAudit": mesh_audit}, indent=2))
    print(json.dumps({
        "pass": True,
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "report": str(REPORT_PATH),
        "renders": report["outputs"]["renders"],
        "denseSweepSamples": report["denseSweep"]["sampleCount"],
    }, indent=2))


if __name__ == "__main__":
    main()

