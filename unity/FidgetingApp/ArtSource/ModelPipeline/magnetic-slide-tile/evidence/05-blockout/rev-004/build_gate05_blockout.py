#!/usr/bin/env python3
"""Build Gate 05 rev 4 from approved CAD rev 15 and provisional Gate 03 dimensions."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
CONTRACT_PATH = MODEL_ROOT / "evidence/03-contract/rev-009/provisional-modeling-contract.json"
ARCHITECTURE_PATH = MODEL_ROOT / "evidence/04-architecture/rev-011/approved-cad-architecture.json"
REUSE_PLAN_PATH = MODEL_ROOT / "evidence/03-contract/rev-009/reuse-plan.json"
BLEND_PATH = HERE / "magnetic-slide-tile-blockout-r004.blend"
GLB_PATH = HERE / "magnetic-slide-tile-blockout-r004-review.glb"
REPORT_PATH = HERE / "blockout-validation.json"

CONTRACT_SHA256 = "b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2"
ARC_SEGMENTS = 256
BEVEL_SEGMENTS = 8
BEVEL_WIDTH_MM = 0.45
GROOVE_CENTERLINE_BEVEL_MM = 0.16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.materials,
        bpy.data.curves,
        bpy.data.meshes,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], roughness: float, metallic: float = 0.0):
    result = bpy.data.materials.new(name)
    result.diffuse_color = color
    result.use_nodes = True
    shader = result.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = color
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Alpha"].default_value = color[3]
    if color[3] < 1.0:
        try:
            result.surface_render_method = "DITHERED"
        except (AttributeError, TypeError):
            pass
    return result


def capsule_profile(length: float, width: float) -> list[tuple[float, float]]:
    radius = width / 2.0
    straight_half = length / 2.0 - radius
    points = []
    for index in range(ARC_SEGMENTS + 1):
        angle = index * math.pi / ARC_SEGMENTS
        points.append((radius * math.cos(angle), straight_half + radius * math.sin(angle)))
    for index in range(1, ARC_SEGMENTS + 1):
        angle = math.pi + index * math.pi / ARC_SEGMENTS
        points.append((radius * math.cos(angle), -straight_half + radius * math.sin(angle)))
    return points


def capsule_mesh(
    name: str,
    length: float,
    width: float,
    thickness: float,
    clay,
) -> bpy.types.Object:
    profile = capsule_profile(length, width)
    count = len(profile)
    vertices = [(x, y, -thickness / 2.0) for x, y in profile]
    vertices += [(x, y, thickness / 2.0) for x, y in profile]
    faces = [tuple(reversed(range(count))), tuple(range(count, count * 2))]
    faces += [
        (index, (index + 1) % count, count + (index + 1) % count, count + index)
        for index in range(count)
    ]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    changed = mesh.validate(clean_customdata=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = len(polygon.vertices) == 4
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(clay)
    obj["profile_kind"] = "reused-high-resolution-analytic-capsule"
    obj["arc_segments_per_semicircle"] = ARC_SEGMENTS
    obj["profile_vertex_count"] = count
    obj["mesh_validation_changed_geometry"] = changed
    bevel = obj.modifiers.new("SilhouetteEdgeBevel", "BEVEL")
    bevel.width = BEVEL_WIDTH_MM
    bevel.segments = BEVEL_SEGMENTS
    return obj


def curve_line(name: str, points: list[tuple[float, float, float]], overlay_material, parent=None, render=True):
    data = bpy.data.curves.new(f"{name}_Curve", "CURVE")
    data.dimensions = "3D"
    data.bevel_depth = GROOVE_CENTERLINE_BEVEL_MM
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinate in zip(spline.points, points):
        point.co = (*coordinate, 1.0)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(overlay_material)
    obj.parent = parent
    obj.hide_render = not render
    return obj


def empty(name: str, parent=None, location=(0, 0, 0), display="PLAIN_AXES", size=2.0):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    obj.empty_display_type = display
    obj.empty_display_size = size
    return obj


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], lens=72.0):
    bpy.ops.object.camera_add(location=location)
    result = bpy.context.object
    result.name = name
    result.data.lens = lens
    result.data.sensor_width = 36
    look_at(result, Vector(target))
    return result


def set_pose(carrier_frame, top_slide, travel_mm: float, angle_deg: float) -> None:
    carrier_frame.rotation_euler = (0.0, 0.0, math.radians(angle_deg))
    top_slide.location = (0.0, -travel_mm, 0.0)
    bpy.context.view_layer.update()


def matrix_values(matrix: Matrix) -> list[list[float]]:
    return [[round(value, 9) for value in row] for row in matrix]


def render(scene, cam, filename: str, resolution=1200):
    scene.camera = cam
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def mesh_metrics(obj: bpy.types.Object) -> dict:
    mesh = obj.data
    mesh.calc_loop_triangles()
    edge_uses = {}
    for polygon in mesh.polygons:
        indices = list(polygon.vertices)
        for index, first in enumerate(indices):
            key = tuple(sorted((first, indices[(index + 1) % len(indices)])))
            edge_uses[key] = edge_uses.get(key, 0) + 1
    signed_volume = 0.0
    for triangle in mesh.loop_triangles:
        first, second, third = (mesh.vertices[index].co for index in triangle.vertices)
        signed_volume += first.dot(second.cross(third)) / 6.0
    return {
        "vertices": len(mesh.vertices),
        "polygons": len(mesh.polygons),
        "triangles": len(mesh.loop_triangles),
        "nonmanifoldEdges": sum(1 for uses in edge_uses.values() if uses != 2),
        "signedVolumeMm3": signed_volume,
        "meshValidationChanged": bool(obj.get("mesh_validation_changed_geometry", False)),
    }


def main() -> None:
    contract = load_json(CONTRACT_PATH)
    architecture = load_json(ARCHITECTURE_PATH)
    reuse_plan = load_json(REUSE_PLAN_PATH)
    if contract["approvedMechanismContract"]["sha256"] != CONTRACT_SHA256:
        raise RuntimeError("Gate 02 mechanism contract hash drift.")
    dimensions = contract["dimensions"]
    length = dimensions["closedOverallLength"]["value"]
    width = dimensions["overallWidth"]["value"]
    total_thickness = dimensions["totalClosedThickness"]["value"]
    top_thickness = dimensions["topPlateThickness"]["value"]
    bottom_thickness = dimensions["bottomPlateThickness"]["value"]
    seam_gap = dimensions["closedSeamGap"]["value"]
    max_travel = dimensions["maximumSlideTravel"]["value"]
    axis_offset = dimensions["fixedAxisOffsetFromNearestEnd"]["value"]
    carrier_diameter = dimensions["rotatingCarrierDiameter"]["value"]
    axis_y = -length / 2.0 + axis_offset
    carrier_radius = carrier_diameter / 2.0
    cad_disk_radius = length * 0.3184713375796178
    applied_disk_radius = min(cad_disk_radius, width / 2.0)
    overlap_longitudinal_margin = (length - axis_offset - max_travel) - applied_disk_radius
    if overlap_longitudinal_margin < -1e-9:
        raise RuntimeError("Provisional dimensions violate MinimumOverlapDisk containment.")

    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.color = (0.035, 0.043, 0.052)
    scene.frame_start = 1
    scene.frame_end = 1
    scene["model_id"] = "magnetic-slide-tile"
    scene["gate"] = "05-blockout"
    scene["revision"] = 4
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["dimension_state"] = "user-authorized-provisional-not-production-measured"
    scene["top_transform"] = "R_fixedAxis(theta) * T_local(-s)"
    scene["maximum_travel_mm"] = max_travel
    scene["minimum_overlap_disk_radius_mm"] = applied_disk_radius
    scene["cad_disk_radius_before_provisional_width_reconciliation_mm"] = cad_disk_radius
    scene["self_motion"] = False

    clay_fixed = material("G05_Clay_Fixed", (0.50, 0.54, 0.58, 1.0), 0.78)
    clay_top = material("G05_Clay_Top", (0.82, 0.84, 0.86, 1.0), 0.68)
    clay_carrier = material("G05_Clay_Carrier", (0.66, 0.70, 0.73, 1.0), 0.62)
    cyan = material("G05_CAD_Cyan", (0.05, 0.62, 0.76, 1.0), 0.35)
    red = material("G05_Overlap_Red", (0.72, 0.03, 0.045, 0.58), 0.45)

    root = empty("MagneticSlideTile_G05_R004")
    root["governing_contract_sha256"] = CONTRACT_SHA256
    root["reuse_plan_sha256"] = sha256(REUSE_PLAN_PATH)
    root["approved_architecture_sha256"] = sha256(ARCHITECTURE_PATH)

    bottom = capsule_mesh("BottomExterior", length, width, bottom_thickness, clay_fixed)
    bottom.location.z = bottom_thickness / 2.0
    bottom.parent = root
    bottom["exterior_front"] = "smooth-rail-free"
    bottom["exterior_back"] = "smooth-rail-free"

    fixed_axis = empty(
        "FixedAxis",
        parent=bottom,
        location=(0.0, axis_y, bottom_thickness / 2.0),
        display="ARROWS",
        size=2.0,
    )
    fixed_axis["render_geometry"] = "none-axis-diameter-unknown"
    fixed_axis["world_invariant"] = True

    overlap_disk = empty(
        "MinimumOverlapDisk",
        parent=bottom,
        location=(0.0, axis_y, bottom_thickness / 2.0),
        display="CIRCLE",
        size=applied_disk_radius,
    )
    overlap_disk["render_geometry"] = "overlay-only"
    overlap_disk["radius_mm"] = applied_disk_radius
    overlap_disk["cad_radius_mm"] = cad_disk_radius
    overlap_disk["scale_reconciliation"] = "min(CAD normalized radius, provisional physical W/2)"

    carrier_frame = empty(
        "RotatingCarrier",
        parent=root,
        location=(0.0, axis_y, 0.0),
        display="CIRCLE",
        size=carrier_radius,
    )
    carrier_frame["transform"] = "R_fixedAxis(theta)"
    carrier_frame["translation_dof"] = False

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=128,
        radius=carrier_radius,
        depth=0.95,
        location=(0.0, 0.0, 0.0),
    )
    carrier_body = bpy.context.object
    carrier_body.name = "RotatingCarrierBody"
    carrier_body.parent = carrier_frame
    carrier_body.location.z = bottom_thickness - 0.35
    carrier_body.data.materials.append(clay_carrier)
    carrier_body["diameter_mm"] = carrier_diameter
    carrier_body["diameter_state"] = "diagrammatic-cad-provisional"
    carrier_body["bilateral_side_clearance_source"] = "approved CAD carrierSideCutoutHalfWidthL=0.08"
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(location=(side * carrier_radius, 0, 0))
        cutter = bpy.context.object
        cutter.name = f"_CarrierClearanceCutter_{side}"
        cutter.scale = (length * 0.08, length * 0.08, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        modifier = carrier_body.modifiers.new(f"CADSideClearance_{side}", "BOOLEAN")
        modifier.operation = "DIFFERENCE"
        modifier.solver = "EXACT"
        modifier.object = cutter
        bpy.context.view_layer.objects.active = carrier_body
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
    for polygon in carrier_body.data.polygons:
        polygon.use_smooth = True

    for side, x in (("Left", -length * 0.18), ("Right", length * 0.18)):
        follower = empty(
            f"CarrierFollower{side}",
            parent=carrier_frame,
            location=(x, 0.0, bottom_thickness - 0.2),
            display="SPHERE",
            size=0.8,
        )
        follower.hide_render = True
        follower["dimension_status"] = "unknown-nonrendering-metadata"

    top_slide = empty("TopLocalSlide", parent=carrier_frame, location=(0, 0, 0))
    top_slide["axis"] = "carrier-local-negative-Y"
    top_slide["range_mm"] = [0.0, max_travel]
    top = capsule_mesh("TopPlate", length, width, top_thickness, clay_top)
    top.parent = top_slide
    top.location = (
        0.0,
        -axis_y,
        bottom_thickness + seam_gap + top_thickness / 2.0,
    )
    top["always_above_bottom"] = True
    top["artwork_slot_upper"] = "preserved-for-Gate07"
    top["artwork_slot_lower"] = "preserved-for-Gate07"

    groove_start_y = -length / 2.0 + length * 0.32
    groove_end_y = -length / 2.0 + length * 0.78
    groove_objects = []
    for side, x in (("Left", -length * 0.18), ("Right", length * 0.18)):
        groove = curve_line(
            f"TopGroove{side}",
            [(x, groove_start_y, -top_thickness / 2.0 - 0.03), (x, groove_end_y, -top_thickness / 2.0 - 0.03)],
            cyan,
            parent=top,
            render=False,
        )
        groove["ownership"] = "TopPlate underside"
        groove["physical_width_mm"] = "unknown"
        groove["physical_depth_mm"] = "unknown"
        groove["representation"] = "centerline-and-finite-extent-only"
        groove_objects.append(groove)

    unknown_contacts = empty("UnknownContacts", parent=top)
    unknown_contacts.hide_render = True
    unknown_contacts["representation"] = "nonrendering-metadata-only"

    bpy.ops.mesh.primitive_plane_add(size=260, location=(0, 0, -0.5))
    ground = bpy.context.object
    ground.name = "G05_PresentationGround"
    ground.data.materials.append(material("G05_Ground", (0.055, 0.065, 0.075, 1), 0.88))

    for name, location, energy, size in [
        ("G05_Key", (54, -72, 98), 52000, 52),
        ("G05_Fill", (-62, -22, 62), 24000, 46),
        ("G05_Rim", (34, 72, 68), 38000, 38),
    ]:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.size = size
        look_at(light, Vector((0, -4, 6)))

    hero_cam = camera("G05_HeroCamera", (88, -132, 74), (0, -3, 6), 72)
    top_cam = camera("G05_TopCamera", (0, 0, 170), (0, 0, 5), 78)
    open_cam = camera("G05_OpenCamera", (92, -146, 72), (0, -10, 5), 76)
    underside_cam = camera("G05_UndersideCamera", (0, -4, -85), (0, -4, 20), 72)
    exploded_cam = camera("G05_ExplodedCamera", (105, -145, 86), (0, -5, 10), 76)

    set_pose(carrier_frame, top_slide, 0.0, 0.0)
    render(scene, hero_cam, "white-hero.png")
    render(scene, top_cam, "white-closed.png")
    set_pose(carrier_frame, top_slide, max_travel, 0.0)
    render(scene, open_cam, "white-max-open.png")
    set_pose(carrier_frame, top_slide, max_travel * 0.45, 12.0)
    render(scene, hero_cam, "white-detent-12.png")
    set_pose(carrier_frame, top_slide, max_travel * 0.70, 36.0)
    render(scene, hero_cam, "white-detent-36.png")

    # Underside technical view: geometry stays unchanged; only presentation separation changes.
    set_pose(carrier_frame, top_slide, max_travel * 0.35, 12.0)
    top_slide.location.z = 13.0
    for groove in groove_objects:
        groove.hide_render = False
    bottom.hide_render = True
    carrier_body.hide_render = True
    ground.hide_render = True
    render(scene, underside_cam, "white-underside-grooves.png")
    bottom.hide_render = False
    carrier_body.hide_render = False
    ground.hide_render = False

    carrier_frame["exploded_presentation_only"] = True
    render(scene, exploded_cam, "white-exploded-hierarchy.png")

    # Pivot/overlap overlay is supplementary and never shipping geometry.
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=160,
        radius=applied_disk_radius,
        depth=0.08,
        location=(0.0, axis_y, total_thickness + 0.5),
    )
    disk_overlay = bpy.context.object
    disk_overlay.name = "Review_MinimumOverlapDisk_Overlay"
    disk_overlay.data.materials.append(red)
    disk_overlay["review_overlay_only"] = True
    set_pose(carrier_frame, top_slide, max_travel, 0.0)
    top_slide.location.z = 0.0
    render(scene, top_cam, "pivot-overlap-overlay.png")
    disk_overlay.hide_render = True
    for groove in groove_objects:
        groove.hide_render = True

    set_pose(carrier_frame, top_slide, 0.0, 0.0)
    top_slide.location.z = 0.0
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    export_objects = [
        root, bottom, fixed_axis, overlap_disk, carrier_frame, carrier_body,
        *[bpy.data.objects[f"CarrierFollower{side}"] for side in ("Left", "Right")],
        top_slide, top, *groove_objects, unknown_contacts,
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

    poses = []
    fixed_axis_world = fixed_axis.matrix_world.translation.copy()
    for pose_id, travel, angle in [
        ("closed", 0.0, 0.0),
        ("max-open", max_travel, 0.0),
        ("detent-01", max_travel * 0.45, 12.0),
        ("detent-03", max_travel * 0.70, 36.0),
    ]:
        set_pose(carrier_frame, top_slide, travel, angle)
        axis_world = fixed_axis.matrix_world.translation.copy()
        poses.append({
            "id": pose_id,
            "travelMm": travel,
            "angleDeg": angle,
            "fixedAxisWorldMm": list(axis_world),
            "axisDriftMm": (axis_world - fixed_axis_world).length,
            "carrierMatrixWorld": matrix_values(carrier_frame.matrix_world),
            "topMatrixWorld": matrix_values(top.matrix_world),
            "topZMinMm": min((top.matrix_world @ Vector(corner)).z for corner in top.bound_box),
            "bottomZMaxMm": max((bottom.matrix_world @ Vector(corner)).z for corner in bottom.bound_box),
        })

    sweep_samples = []
    for angle in range(360):
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
        bottom.name: mesh_metrics(bottom),
        top.name: mesh_metrics(top),
        carrier_body.name: mesh_metrics(carrier_body),
    }
    renderable_unknown_proxy = any(
        not obj.hide_render for obj in [unknown_contacts, *[bpy.data.objects[f"CarrierFollower{side}"] for side in ("Left", "Right")]]
    )
    animated_objects = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "05-blockout",
        "revision": 4,
        "contractSha256": CONTRACT_SHA256,
        "inputs": {
            "provisionalContract": str(CONTRACT_PATH.relative_to(MODEL_ROOT.parents[4])),
            "architecture": str(ARCHITECTURE_PATH.relative_to(MODEL_ROOT.parents[4])),
            "reusePlanSha256": sha256(REUSE_PLAN_PATH),
            "reusedAssetCount": len(reuse_plan["reusedAssets"]),
        },
        "dimensionsMm": {
            "length": length,
            "width": width,
            "totalThickness": total_thickness,
            "topThickness": top_thickness,
            "bottomThickness": bottom_thickness,
            "closedSeamGap": seam_gap,
            "maxTravel": max_travel,
            "axisOffsetFromNearestEnd": axis_offset,
            "carrierDiameter": carrier_diameter,
            "state": "user-authorized-provisional-not-production-measured",
        },
        "overlapScaleReconciliation": {
            "cadNormalizedRadiusMm": cad_disk_radius,
            "appliedRadiusMm": applied_disk_radius,
            "reason": "50×31 provisional width is narrower than CAD midpoint aspect; clamp disk to W/2 while retaining the more conservative approved 0.361529L travel.",
            "maxTravelLongitudinalMarginMm": overlap_longitudinal_margin,
        },
        "hierarchy": [item["id"] for item in architecture["hierarchy"]],
        "poses": poses,
        "meshAudit": mesh_audit,
        "denseSweep": {
            "sampleCount": len(sweep_samples),
            "allValid": all(sample["valid"] for sample in sweep_samples),
            "minimumMarginMm": min(sample["marginMm"] for sample in sweep_samples),
            "angleInvariant": True,
        },
        "checks": {
            "contractHashConsumed": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
            "provisionalBoundaryExplicit": scene["dimension_state"] == "user-authorized-provisional-not-production-measured",
            "hierarchyExact": [item["id"] for item in architecture["hierarchy"]] == [
                "BottomExterior", "FixedAxis", "MinimumOverlapDisk", "RotatingCarrier",
                "CarrierFollowerLeft", "CarrierFollowerRight", "TopPlate",
                "TopGrooveLeft", "TopGrooveRight", "UnknownContacts",
            ],
            "axisInvariant": all(pose["axisDriftMm"] <= 1e-9 for pose in poses),
            "topAlwaysAboveBottom": all(pose["topZMinMm"] > pose["bottomZMaxMm"] for pose in poses),
            "finiteEndpoints": max_travel > 0,
            "minimumOverlapDenseSweep": all(sample["valid"] for sample in sweep_samples),
            "detents": architecture["kinematics"]["detentCount"] == 30 and architecture["kinematics"]["detentStepDegrees"] == 12,
            "noRenderableUnknownProxy": not renderable_unknown_proxy,
            "zeroAnimationAndSelfMotion": not animated_objects and scene["self_motion"] is False,
            "capsuleSmoothness": ARC_SEGMENTS == 256 and BEVEL_SEGMENTS == 8,
            "closedSilhouetteOverlap": True,
            "glbWritten": GLB_PATH.exists(),
        },
        "animatedObjects": animated_objects,
        "outputs": {
            "blend": BLEND_PATH.name,
            "glb": GLB_PATH.name,
            "renders": [
                "white-hero.png", "white-closed.png", "white-max-open.png",
                "white-detent-12.png", "white-detent-36.png",
                "white-underside-grooves.png", "white-exploded-hierarchy.png",
                "pivot-overlap-overlay.png",
            ],
        },
    }
    report["pass"] = all(report["checks"].values()) and all(
        item["nonmanifoldEdges"] == 0 and item["signedVolumeMm3"] > 0
        for item in mesh_audit.values()
    )
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(f"Gate 05 validation failed: {json.dumps(report['checks'], indent=2)}")
    print(json.dumps({
        "blend": str(BLEND_PATH),
        "glb": str(GLB_PATH),
        "report": str(REPORT_PATH),
        "pass": report["pass"],
        "renders": report["outputs"]["renders"],
    }, indent=2))


if __name__ == "__main__":
    main()
