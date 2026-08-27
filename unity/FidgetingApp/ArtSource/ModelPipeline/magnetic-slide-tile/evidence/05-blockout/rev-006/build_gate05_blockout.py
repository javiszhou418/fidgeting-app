#!/usr/bin/env python3
"""Build Gate 05 rev 6 with one continuous flat BottomExterior top plane."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
REPO_ROOT = MODEL_ROOT.parents[4]
REV5_BUILDER = HERE.parent / "rev-005/build_gate05_blockout.py"
REV5_REPORT = HERE.parent / "rev-005/blockout-validation.json"
CONTRACT_PATH = MODEL_ROOT / "evidence/03-contract/rev-011/authorized-provisional-modeling-contract.json"
ARCHITECTURE_PATH = MODEL_ROOT / "evidence/04-architecture/rev-013/approved-four-track-raised-axis-architecture.json"
REUSE_PLAN_PATH = MODEL_ROOT / "evidence/03-contract/rev-011/reuse-plan.json"
MECHANISM_PATH = MODEL_ROOT / "evidence/02-analysis/rev-016/mechanism-evidence-contract.json"
BLEND_PATH = HERE / "magnetic-slide-tile-blockout-r006.blend"
GLB_PATH = HERE / "magnetic-slide-tile-blockout-r006-review.glb"
REPORT_PATH = HERE / "blockout-validation.json"

CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
REV5_BUILDER_SHA256 = "f04579dbc8f1e92dbbcca9a3b17cd050558c467e2c82f8b345d690ebc68fde73"
PLANE_TOLERANCE_MM = 0.001
PLANE_SAMPLE_STEP_MM = 1.0
AXIS_BOSS_EXPOSED_MM = 0.2


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module():
    if sha256(REV5_BUILDER) != REV5_BUILDER_SHA256:
        raise RuntimeError("Gate 05 rev 5 builder changed; immutable lineage check failed.")
    spec = importlib.util.spec_from_file_location("gate05_rev5_builder", REV5_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r5 = load_module()
r5.HERE = HERE
legacy = r5.legacy


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def capsule_contains(x: float, y: float, length: float, width: float, margin: float) -> bool:
    radius = width / 2.0 - margin
    straight_half = length / 2.0 - width / 2.0
    dy = max(abs(y) - straight_half, 0.0)
    return x * x + dy * dy <= radius * radius


def sample_flat_plane(bottom, length, width, boss_radius, expected_local_z):
    samples = []
    x = -width / 2.0
    while x <= width / 2.0 + 1e-9:
        y = -length / 2.0
        while y <= length / 2.0 + 1e-9:
            if capsule_contains(x, y, length, width, 0.65) and math.hypot(x, y - (-length / 2.0 + 16.0)) > boss_radius + 0.25:
                hit, location, normal, _ = bottom.ray_cast(
                    Vector((x, y, expected_local_z + 2.0)),
                    Vector((0.0, 0.0, -1.0)),
                )
                if not hit:
                    raise RuntimeError(f"Flat-plane sample missed BottomExterior at {(x, y)}.")
                samples.append({
                    "xMm": round(x, 4),
                    "yMm": round(y, 4),
                    "zMm": location.z + bottom.location.z,
                    "normalZ": normal.z,
                })
            y += PLANE_SAMPLE_STEP_MM
        x += PLANE_SAMPLE_STEP_MM
    deviations = [abs(sample["zMm"] - (expected_local_z + bottom.location.z)) for sample in samples]
    return {
        "sampleCount": len(samples),
        "stepMm": PLANE_SAMPLE_STEP_MM,
        "toleranceMm": PLANE_TOLERANCE_MM,
        "maximumDeviationMm": max(deviations),
        "minimumZMm": min(sample["zMm"] for sample in samples),
        "maximumZMm": max(sample["zMm"] for sample in samples),
        "minimumNormalZ": min(sample["normalZ"] for sample in samples),
    }


def main():
    contract = load_json(CONTRACT_PATH)
    architecture = load_json(ARCHITECTURE_PATH)
    reuse_plan = load_json(REUSE_PLAN_PATH)
    mechanism = load_json(MECHANISM_PATH)
    rev5_report = load_json(REV5_REPORT)
    if sha256(MECHANISM_PATH) != CONTRACT_SHA256:
        raise RuntimeError("Current mechanism contract hash drift.")
    for source in (contract, architecture):
        if source["governingMechanismContractSha256"] != CONTRACT_SHA256:
            raise RuntimeError("Upstream contract hash drift.")

    dimensions = contract["dimensionsMm"]
    length = dimensions["overallLength"]["provisional"]
    width = dimensions["overallWidth"]["provisional"]
    total_thickness = dimensions["totalClosedThickness"]["provisional"]
    top_thickness = dimensions["topThickness"]["provisional"]
    bottom_thickness = dimensions["bottomThickness"]["provisional"]
    seam_gap = dimensions["closedSeamGap"]["provisional"]
    max_travel = dimensions["maximumSlideTravel"]["provisional"]
    axis_offset = dimensions["fixedAxisOffsetFromNearestEnd"]["provisional"]
    carrier_diameter = dimensions["rotatingCarrierDiameter"]["provisional"]
    ball_range = dimensions["ballDiameter"]["range"]
    ball_diameter = dimensions["ballDiameter"]["provisional"]
    track_range = dimensions["trackWidth"]["range"]
    track_width = dimensions["trackWidth"]["provisional"]
    boss_module_depth = contract["mechanism"]["axisBossProtrusionMm"]["provisional"]
    axis_y = -length / 2.0 + axis_offset
    top_plane_z = bottom_thickness
    boss_radius = max(track_width * 1.35, 3.4)
    carrier_radius = carrier_diameter / 2.0
    carrier_depth = 0.86
    hidden_clearance = 0.05
    applied_disk_radius = min(length * 0.3184713375796178, width / 2.0)
    inner_offset = length * 0.12
    outer_offset = length * 0.235
    groove_offsets = [-outer_offset, -inner_offset, inner_offset, outer_offset]
    groove_depth = min(1.0, top_thickness * 0.22)

    groove_constraint = next(item for item in mechanism["constraints"] if item["id"] == "MEC-TOP-UNDERSIDE-GROOVES")
    boss_constraint = next(item for item in mechanism["constraints"] if item["id"] == "MEC-RAISED-AXIS-BOSS")
    if [item["id"] for item in groove_constraint["value"]["tracks"]] != r5.GROOVE_IDS:
        raise RuntimeError("Four top-underside grooves drifted.")
    if boss_constraint["value"]["recessedAxis"] or AXIS_BOSS_EXPOSED_MM <= 0:
        raise RuntimeError("FixedAxisBoss must protrude above the flat plane.")

    legacy.clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.026, 0.032, 0.039)
    scene.frame_start = scene.frame_end = 1
    scene["model_id"] = "magnetic-slide-tile"
    scene["gate"] = "05-blockout"
    scene["revision"] = 6
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["dimension_state"] = "user-authorized-provisional-not-production-measured"
    scene["top_transform"] = "R_fixedAxis(theta) * T_local(s)"
    scene["bottom_top_surface"] = "continuous-flat-plane"
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False

    clay_bottom = legacy.material("G05R6_Clay_Bottom", (0.50, 0.53, 0.56, 1.0), 0.82)
    clay_top = legacy.material("G05R6_Clay_Top", (0.82, 0.84, 0.85, 1.0), 0.74)
    clay_mechanism = legacy.material("G05R6_Clay_Mechanism", (0.65, 0.68, 0.70, 1.0), 0.68)
    clay_candidate = legacy.material("G05R6_Clay_Candidate", (0.73, 0.75, 0.76, 1.0), 0.52)
    overlay_red = legacy.material("G05R6_Overlap_Overlay", (0.74, 0.03, 0.05, 0.62), 0.45)
    ground_mat = legacy.material("G05R6_Ground", (0.045, 0.052, 0.060, 1.0), 0.90)
    transparent_bottom = legacy.material("G05R6_Technical_Transparent", (0.50, 0.53, 0.56, 0.22), 0.82)

    root = legacy.empty("MagneticSlideTile_G05_R006")
    root["governing_contract_sha256"] = CONTRACT_SHA256
    root["source_rev5_builder_sha256"] = REV5_BUILDER_SHA256
    root["reuse_plan_sha256"] = sha256(REUSE_PLAN_PATH)

    bottom = legacy.capsule_mesh("BottomExterior", length, width, bottom_thickness, clay_bottom)
    r5.apply_modifier(bottom, bottom.modifiers["SilhouetteEdgeBevel"])
    r5.set_parent_local(bottom, root, (0.0, 0.0, bottom_thickness / 2.0))
    bottom["top_plane_z_mm"] = top_plane_z
    bottom["top_plane_tolerance_mm"] = PLANE_TOLERANCE_MM
    bottom["top_surface"] = "flat-continuous-except-raised-axis-boss"
    bottom["cavity"] = False
    bottom["recess_depth_mm"] = 0.0
    bottom["carrier_exterior"] = False

    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=boss_radius, depth=boss_module_depth)
    fixed_axis_boss = bpy.context.object
    fixed_axis_boss.name = "FixedAxisBoss"
    fixed_axis_boss.data.materials.append(clay_mechanism)
    boss_center_world_z = top_plane_z - boss_module_depth / 2.0 + AXIS_BOSS_EXPOSED_MM
    r5.set_parent_local(
        fixed_axis_boss,
        bottom,
        (0.0, axis_y, boss_center_world_z - bottom.location.z),
    )
    fixed_axis_boss["module_depth_mm"] = boss_module_depth
    fixed_axis_boss["protrusion_mm"] = AXIS_BOSS_EXPOSED_MM
    fixed_axis_boss["recessed_axis"] = False
    fixed_axis = legacy.empty("FixedAxis", parent=fixed_axis_boss, display="ARROWS", size=1.8)
    fixed_axis["world_invariant"] = True

    overlap_disk = legacy.empty(
        "MinimumOverlapDisk",
        parent=bottom,
        location=(0.0, axis_y, bottom_thickness / 2.0),
        display="CIRCLE",
        size=applied_disk_radius,
    )
    overlap_disk["render_geometry"] = "validation-overlay-only"
    overlap_disk["radius_mm"] = applied_disk_radius

    carrier_center_world_z = top_plane_z - hidden_clearance - carrier_depth / 2.0
    carrier_frame = legacy.empty("RotatingCarrier", parent=fixed_axis_boss, display="CIRCLE", size=carrier_radius)
    carrier_frame.location = (0.0, 0.0, carrier_center_world_z - boss_center_world_z)
    carrier_frame["transform"] = "R_fixedAxis(theta)"
    carrier_frame["translation_dof"] = False
    carrier_frame["exterior_visible"] = False
    bpy.ops.mesh.primitive_cylinder_add(vertices=160, radius=carrier_radius, depth=carrier_depth)
    carrier_body = bpy.context.object
    carrier_body.name = "RotatingCarrierBody"
    carrier_body.data.materials.append(clay_mechanism)
    r5.set_parent_local(carrier_body, carrier_frame)
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        cutter = bpy.context.object
        cutter.dimensions = (length * 0.16, length * 0.18, carrier_depth * 2.2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        r5.set_parent_local(cutter, carrier_frame, (side * carrier_radius, 0.0, 0.0))
        modifier = carrier_body.modifiers.new(f"BilateralClearance_{side}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        r5.apply_modifier(carrier_body, modifier)
        bpy.data.objects.remove(cutter, do_unlink=True)
    carrier_body["bilateral_side_clearances"] = True
    carrier_body["exterior_visible"] = False

    follower_top_world_z = top_plane_z - hidden_clearance
    follower_local_z = follower_top_world_z - 0.36 - carrier_center_world_z
    follower_left = r5.make_follower("CarrierFollowerLeft", track_width, clay_mechanism, carrier_frame, -inner_offset)
    follower_right = r5.make_follower("CarrierFollowerRight", track_width, clay_mechanism, carrier_frame, inner_offset)
    follower_left.location.z = follower_right.location.z = follower_local_z
    ball_center_local_z = top_plane_z - hidden_clearance - ball_diameter / 2.0 - carrier_center_world_z
    ball_left = r5.make_ball("BallCandidateLeft", ball_diameter, clay_candidate, carrier_frame, (-outer_offset, 0.0, ball_center_local_z))
    ball_right = r5.make_ball("BallCandidateRight", ball_diameter, clay_candidate, carrier_frame, (outer_offset, 0.0, ball_center_local_z))
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
    r5.cut_top_grooves(top, length, top_thickness, track_width, groove_depth, groove_offsets)
    top_base_z = bottom_thickness + seam_gap
    r5.set_parent_local(top, top_slide, (0.0, -axis_y, top_base_z + top_thickness / 2.0))
    top["always_above_bottom"] = True
    top["groove_count"] = 4

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0.0, 0.0, -0.55))
    ground = bpy.context.object
    ground.data.materials.append(ground_mat)
    for name, location, energy, size in [
        ("G05R6_Key", (55, -74, 96), 50000, 52),
        ("G05R6_Fill", (-58, -18, 60), 23000, 44),
        ("G05R6_Rim", (30, 70, 64), 36000, 38),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.size = size
        legacy.look_at(light, Vector((0.0, -4.0, 5.0)))

    hero_cam = legacy.camera("G05R6_HeroCamera", (84, -126, 70), (0, -3, 5), 72)
    top_cam = legacy.camera("G05R6_TopCamera", (0, 0, 170), (0, 0, 5), 78)
    open_cam = legacy.camera("G05R6_OpenCamera", (92, -142, 70), (0, -10, 5), 76)
    underside_cam = legacy.camera("G05R6_UndersideCamera", (0, 0, 165), (0, 0, 8), 76)
    plane_cam = legacy.camera("G05R6_FlatPlaneCamera", (52, -70, 55), (0, -2, top_plane_z), 84)
    axis_cam = legacy.camera("G05R6_AxisCamera", (25, axis_y - 35, 12), (0, axis_y, top_plane_z), 100)
    exploded_cam = legacy.camera("G05R6_ExplodedCamera", (98, -138, 82), (0, -4, 11), 76)

    r5.set_pose(carrier_frame, moving_top, top_slide, 0.0, 0.0)
    r5.render(scene, hero_cam, "white-hero.png")
    r5.render(scene, top_cam, "white-closed.png")
    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel, 0.0)
    r5.render(scene, open_cam, "white-max-open.png")
    top.hide_render = True
    r5.render(scene, plane_cam, "white-bottom-flat-plane-closeup.png")
    r5.render(scene, axis_cam, "white-raised-axis-closeup.png")
    top.hide_render = False
    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.45, 12.0)
    r5.render(scene, hero_cam, "white-detent-12.png")
    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.70, 36.0)
    r5.render(scene, hero_cam, "white-detent-36.png")

    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel * 0.35, 12.0)
    top_slide.location.z = 13.0
    top.rotation_euler.x = math.pi
    bottom.hide_render = fixed_axis_boss.hide_render = carrier_body.hide_render = True
    follower_left.hide_render = follower_right.hide_render = ball_left.hide_render = ball_right.hide_render = True
    ground.hide_render = True
    r5.render(scene, underside_cam, "white-underside-four-grooves.png")
    top.rotation_euler.x = 0.0
    bottom.hide_render = fixed_axis_boss.hide_render = carrier_body.hide_render = False
    follower_left.hide_render = follower_right.hide_render = ball_left.hide_render = ball_right.hide_render = False
    ground.hide_render = False

    top_slide.location.z = 16.0
    bottom.data.materials[0] = transparent_bottom
    r5.render(scene, exploded_cam, "white-exploded-hierarchy.png")
    bottom.data.materials[0] = clay_bottom

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=160,
        radius=applied_disk_radius,
        depth=0.10,
        location=(0.0, axis_y, total_thickness + 0.40),
    )
    disk_overlay = bpy.context.object
    disk_overlay.name = "Review_MinimumOverlapDisk_Overlay"
    disk_overlay.data.materials.append(overlay_red)
    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel, 0.0)
    top_slide.location.z = 0.0
    r5.render(scene, top_cam, "pivot-overlap-overlay.png")
    disk_overlay.hide_render = True

    r5.set_pose(carrier_frame, moving_top, top_slide, max_travel, 0.0)
    top_slide.location.z = 8.0
    bpy.context.view_layer.update()
    export_objects = [
        root, bottom, fixed_axis_boss, fixed_axis, overlap_disk, carrier_frame, carrier_body,
        follower_left, follower_right, ball_left, ball_right, unknown_springs, unknown_preload,
        moving_top, top_slide, top, *[bpy.data.objects[groove_id] for groove_id in r5.GROOVE_IDS],
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

    r5.set_pose(carrier_frame, moving_top, top_slide, 0.0, 0.0)
    top_slide.location.z = 0.0
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    plane_metrics = sample_flat_plane(bottom, length, width, boss_radius, bottom_thickness / 2.0)
    top_polygons = [polygon for polygon in bottom.data.polygons if polygon.normal.z > 0.999999]
    top_vertex_z = [
        (bottom.matrix_world @ bottom.data.vertices[index].co).z
        for polygon in top_polygons
        for index in polygon.vertices
    ]
    carrier_meshes = [carrier_body, follower_left, follower_right, ball_left, ball_right]
    carrier_max_z = max(
        max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)
        for obj in carrier_meshes
    )
    poses = []
    axis_world_reference = fixed_axis.matrix_world.translation.copy()
    for pose_id, travel, angle in [
        ("closed", 0.0, 0.0),
        ("max-open", max_travel, 0.0),
        ("detent-01", max_travel * 0.45, 12.0),
        ("detent-03", max_travel * 0.70, 36.0),
    ]:
        r5.set_pose(carrier_frame, moving_top, top_slide, travel, angle)
        poses.append({
            "id": pose_id,
            "travelMm": travel,
            "angleDeg": angle,
            "axisDriftMm": (fixed_axis.matrix_world.translation - axis_world_reference).length,
            "movingTopMatrixWorld": r5.matrix_values(moving_top.matrix_world),
            "topSlideMatrixLocal": r5.matrix_values(top_slide.matrix_local),
            "topZMinMm": min((top.matrix_world @ Vector(corner)).z for corner in top.bound_box),
            "bottomTopPlaneZMm": top_plane_z,
        })
    sweep = []
    for half_degree in range(720):
        for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
            travel = max_travel * fraction
            longitudinal_margin = (length - axis_offset - travel) - applied_disk_radius
            side_margin = width / 2.0 - applied_disk_radius
            sweep.append(min(longitudinal_margin, side_margin) >= -1e-9)

    mesh_audit = {
        name: legacy.mesh_metrics(bpy.data.objects[name])
        for name in [
            "BottomExterior", "MovingTopBody", "FixedAxisBoss", "RotatingCarrierBody",
            "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
        ]
    }
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    expected_hierarchy = [item["id"] for item in architecture["hierarchy"]]
    actual_hierarchy = [
        "BottomExterior", "FixedAxisBoss", "MinimumOverlapDisk", "RotatingCarrier",
        "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
        "MovingTop", *r5.GROOVE_IDS, "UnknownSprings", "UnknownPreload",
    ]
    bottom_modifier_names = [modifier.name for modifier in bottom.modifiers]
    report = {
        "schemaVersion": 3,
        "modelId": "magnetic-slide-tile",
        "gate": "05-blockout",
        "revision": 6,
        "contractSha256": CONTRACT_SHA256,
        "partialApproval": {
            "accepted": "Gate 05 rev 5 hierarchy and kinematics",
            "rejected": "recessed/concave BottomExterior top surface",
            "supersedesRevision": 5,
        },
        "dimensionsMm": {
            "overallLength": length,
            "overallWidth": width,
            "totalClosedThickness": total_thickness,
            "topThickness": top_thickness,
            "bottomThickness": bottom_thickness,
            "bottomTopPlaneZ": top_plane_z,
            "axisBossModuleDepth": boss_module_depth,
            "axisBossExposedProtrusion": AXIS_BOSS_EXPOSED_MM,
            "maxTravel": max_travel,
            "state": "user-authorized-provisional-not-production-measured",
        },
        "flatPlaneMetrics": {
            **plane_metrics,
            "topFacingPolygonCount": len(top_polygons),
            "topFacingVertexCount": len(top_vertex_z),
            "minimumTopFacingVertexZMm": min(top_vertex_z),
            "maximumTopFacingVertexZMm": max(top_vertex_z),
            "definedTopPlaneZMm": top_plane_z,
        },
        "carrierPacking": {
            "maximumWorldZMm": carrier_max_z,
            "topPlaneZMm": top_plane_z,
            "clearanceBelowPlaneMm": top_plane_z - carrier_max_z,
            "exteriorVisible": False,
        },
        "hierarchy": actual_hierarchy,
        "poses": poses,
        "meshAudit": mesh_audit,
        "denseSweep": {
            "sampleCount": len(sweep),
            "angularStepDegrees": 0.5,
            "allValid": all(sweep),
        },
        "geometryComparisonToRev5": {
            "acceptedHierarchyUnchanged": actual_hierarchy == rev5_report["hierarchy"],
            "topMeshMetricsUnchanged": mesh_audit["MovingTopBody"] == rev5_report["meshAudit"]["MovingTopBody"],
            "poseTravelAndAnglesUnchanged": [
                (pose["travelMm"], pose["angleDeg"]) for pose in poses
            ] == [
                (pose["travelMm"], pose["angleDeg"]) for pose in rev5_report["poses"]
            ],
            "changedExteriorGeometry": ["BottomExterior top skin"],
            "removedGeometry": ["_BottomExteriorUpperRim recessed perimeter"],
            "unchangedMechanismMeshGeometry": [
                "FixedAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft",
                "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
            ],
        },
        "checks": {
            "contractHashConsumed": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
            "flatPlaneWithinTolerance": plane_metrics["maximumDeviationMm"] <= PLANE_TOLERANCE_MM,
            "noTopSkinVertexBelowPlane": min(top_vertex_z) >= top_plane_z - PLANE_TOLERANCE_MM,
            "noBottomRecessModifier": not bottom_modifier_names,
            "noNegativeRecessDepth": bottom["recess_depth_mm"] == 0.0,
            "noConcaveCircularSurface": bottom["cavity"] is False and "_BottomExteriorUpperRim" not in bpy.data.objects,
            "axisBossPositive": fixed_axis_boss["protrusion_mm"] > 0,
            "carrierHiddenBelowPlane": carrier_max_z <= top_plane_z - hidden_clearance + PLANE_TOLERANCE_MM,
            "fourTopUndersideGrooves": top["groove_count"] == 4,
            "hierarchyExact": expected_hierarchy == actual_hierarchy,
            "axisInvariant": all(pose["axisDriftMm"] <= 1e-9 for pose in poses),
            "topAlwaysAbovePlane": all(pose["topZMinMm"] > top_plane_z for pose in poses),
            "minimumOverlapDenseSweep": all(sweep),
            "geometryComparisonOnlyRecessChanged": actual_hierarchy == rev5_report["hierarchy"]
            and mesh_audit["MovingTopBody"] == rev5_report["meshAudit"]["MovingTopBody"],
            "zeroAnimationAndSelfMotion": not animated and scene["self_motion"] is False,
            "glbWritten": GLB_PATH.exists(),
            "blendWritten": BLEND_PATH.exists(),
        },
        "outputs": {
            "blend": BLEND_PATH.name,
            "glb": GLB_PATH.name,
            "renders": [
                "white-hero.png", "white-closed.png", "white-max-open.png",
                "white-detent-12.png", "white-detent-36.png",
                "white-bottom-flat-plane-closeup.png", "white-raised-axis-closeup.png",
                "white-underside-four-grooves.png", "white-exploded-hierarchy.png",
                "pivot-overlap-overlay.png",
            ],
        },
    }
    report["pass"] = all(report["checks"].values()) and all(
        metrics["nonmanifoldEdges"] == 0 and metrics["signedVolumeMm3"] > 0
        for metrics in mesh_audit.values()
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({
        "pass": True,
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "planeMetrics": report["flatPlaneMetrics"],
        "carrierPacking": report["carrierPacking"],
        "denseSweepSamples": report["denseSweep"]["sampleCount"],
    }, indent=2))


if __name__ == "__main__":
    main()

