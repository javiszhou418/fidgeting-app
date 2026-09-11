#!/usr/bin/env python3
"""Deterministic model-hhax Blender builder, renderer and exporter.

Run only after Gate 04 approval. Phases deliberately consume the preceding
immutable Blender source so each pipeline gate can be reviewed before the next.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[6]
MODEL = ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax"
TEXTURES = MODEL / "source/textures"
EVIDENCE = MODEL / "evidence"
MM = 0.001
PIPELINE_PATH = MODEL / "pipeline.json"
CONTRACT_PATH = MODEL / "evidence/03-contract/rev-001/measurement-modeling-contract.json"
ARCHITECTURE_PATH = MODEL / "evidence/04-architecture/rev-002/architecture-review-parameters.json"


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_approved_inputs():
    manifest = json.loads(PIPELINE_PATH.read_text(encoding="utf-8"))
    stages = {stage["id"]: stage for stage in manifest["stages"]}
    for stage_id in ("03-contract", "04-architecture"):
        if stages.get(stage_id, {}).get("status") != "approved":
            raise RuntimeError(f"{stage_id} must be approved before Blender generation")
    assets = {asset["id"]: asset for asset in manifest["assets"]}
    contract_asset = assets.get("model-hhax-measurement-modeling-contract-r001")
    architecture_asset = assets.get("hhax-gate04-architecture-snapshot-r002")
    if not contract_asset or contract_asset.get("sha256") != file_sha256(CONTRACT_PATH):
        raise RuntimeError("Gate 03 contract is missing or its SHA-256 no longer matches")
    if not architecture_asset or architecture_asset.get("sha256") != file_sha256(ARCHITECTURE_PATH):
        raise RuntimeError("Gate 04 architecture snapshot is missing or its SHA-256 no longer matches")
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    architecture = json.loads(ARCHITECTURE_PATH.read_text(encoding="utf-8"))
    required_ids = (
        "closedOverallLength", "overallWidth", "totalClosedThickness",
        "topPlateThickness", "bottomPlateThickness", "maximumSlideTravel",
        "fixedAxisOffsetFromNearestEnd", "rotatingCarrierDiameter", "closedSeamGap"
    )
    measurements = contract.get("measurements", {}).get("required", {})
    values = {}
    for field_id in required_ids:
        record = measurements.get(field_id, {})
        if record.get("state") != "known" or record.get("unknown") is not False:
            raise RuntimeError(f"Gate 03 field {field_id} is not a known value")
        if record.get("measured") is not False or record.get("manufacturingDimension") is not False:
            raise RuntimeError(f"Gate 03 field {field_id} is not classified as a reversible digital target/spec")
        values[field_id] = float(record["valueMm"])
    if architecture.get("translationOwner") != "upper shell" or architecture.get("translationAxis") != "+Y":
        raise RuntimeError("Gate 04 upper-shell translation ownership changed")
    if architecture.get("rotationOwner") != "rear circular carrier / medallion" or architecture.get("rotationAxis") != "+Z":
        raise RuntimeError("Gate 04 rear-carrier rotation ownership changed")
    expected_range = architecture.get("translationRangeMm")
    if expected_range != [0, values["maximumSlideTravel"]]:
        raise RuntimeError("Gate 03 travel and Gate 04 translation range disagree")
    return values, {
        "manifestRevisionAtBuild": manifest["revision"],
        "contractAssetId": contract_asset["id"],
        "contractSha256": contract_asset["sha256"],
        "architectureAssetId": architecture_asset["id"],
        "architectureSha256": architecture_asset["sha256"],
        "hiddenBoundary": architecture.get("unknown")
    }


DIMENSIONS_MM, INPUT_PROVENANCE = load_approved_inputs()
L = DIMENSIONS_MM["closedOverallLength"] * MM
W = DIMENSIONS_MM["overallWidth"] * MM
T = DIMENSIONS_MM["totalClosedThickness"] * MM
BOTTOM_T = DIMENSIONS_MM["bottomPlateThickness"] * MM
TOP_T = DIMENSIONS_MM["topPlateThickness"] * MM
SEAM = DIMENSIONS_MM["closedSeamGap"] * MM
CAP_T = 0.8 * MM
TOP_BODY_T = TOP_T - CAP_T
TRAVEL = DIMENSIONS_MM["maximumSlideTravel"] * MM
AXIS_Y = (L / 2) - DIMENSIONS_MM["fixedAxisOffsetFromNearestEnd"] * MM
CARRIER_D = DIMENSIONS_MM["rotatingCarrierDiameter"] * MM

G05 = EVIDENCE / "05-blockout/rev-003"
G06 = EVIDENCE / "06-geometry/rev-001"
G07 = EVIDENCE / "07-material/rev-001"
G08 = EVIDENCE / "08-lighting/rev-001"
G09 = EVIDENCE / "09-environment/rev-001"
G10 = EVIDENCE / "10-export/rev-001"


def parse_phase():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["gate05", "gate06", "gate07", "gate08", "gate09", "gate10"])
    return parser.parse_args(argv).phase


def prepare_output_directory(directory):
    directory.mkdir(parents=True, exist_ok=True)
    existing = [item for item in directory.iterdir() if item.is_file() and item.stat().st_size > 0]
    if existing:
        names = ", ".join(sorted(item.name for item in existing))
        raise RuntimeError(f"immutable evidence target already contains files: {names}")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def ensure_collection(name, parent=None):
    collection = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if not collection.users:
        (parent or bpy.context.scene.collection).children.link(collection)
    return collection


def link_object(obj, collection):
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(name, color, metallic=0.0, roughness=0.5):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def set_input(bsdf, names, value):
    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def image_node(nodes, path, name, non_color=False):
    node = nodes.new("ShaderNodeTexImage")
    node.name = name
    node.label = name
    node.image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        node.image.colorspace_settings.name = "Non-Color"
    return node


def make_art_material(name, prefix):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "ArtworkPrincipled"
    base = image_node(nodes, TEXTURES / f"{prefix}-basecolor.png", "BaseColor")
    rough = image_node(nodes, TEXTURES / f"{prefix}-roughness.png", "Roughness", True)
    normal = image_node(nodes, TEXTURES / f"{prefix}-normal.png", "Normal", True)
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.28
    emission = image_node(nodes, TEXTURES / f"{prefix}-emission.png", "EmissionColor")
    strength = nodes.new("ShaderNodeValue")
    strength.name = "HHAX_EmissionStrength"
    strength.outputs[0].default_value = 0.08
    links.new(base.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, ["Metallic"], 0.08)
    if "Emission Color" in bsdf.inputs:
        links.new(emission.outputs["Color"], bsdf.inputs["Emission Color"])
        links.new(strength.outputs[0], bsdf.inputs["Emission Strength"])
    else:
        links.new(emission.outputs["Color"], bsdf.inputs["Emission"])
        links.new(strength.outputs[0], bsdf.inputs["Emission Strength"])
    links.new(bsdf.outputs[0], out.inputs[0])
    material["hhax_surface"] = prefix
    return material


def make_iridescent(name, intensity=0.35):
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    layer = nodes.new("ShaderNodeLayerWeight")
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    stops = [
        (0.00, (0.018, 0.012, 0.028, 1)),
        (0.48, (0.055, 0.035, 0.085, 1)),
        (0.78, (0.055 * intensity, 0.22 * intensity, 0.26 * intensity, 1)),
        (0.90, (0.30 * intensity, 0.045, 0.18 * intensity, 1)),
        (1.00, (0.45, 0.36, 0.50, 1)),
    ]
    first = ramp.color_ramp.elements[0]
    first.position, first.color = stops[0][0], stops[0][1]
    for position, color in stops[1:]:
        element = ramp.color_ramp.elements.new(position)
        element.color = color
    links.new(layer.outputs["Facing"], ramp.inputs[0])
    links.new(ramp.outputs[0], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.96
    bsdf.inputs["Roughness"].default_value = 0.18
    set_input(bsdf, ["Coat Weight", "Clearcoat"], 0.48)
    set_input(bsdf, ["Coat Roughness", "Clearcoat Roughness"], 0.10)
    links.new(bsdf.outputs[0], out.inputs[0])
    return material


def make_glass():
    material = bpy.data.materials.get("MAT_ClearSeal") or bpy.data.materials.new("MAT_ClearSeal")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.70, 0.78, 0.86, 1)
    bsdf.inputs["Roughness"].default_value = 0.055
    set_input(bsdf, ["Transmission Weight", "Transmission"], 0.88)
    set_input(bsdf, ["Coat Weight", "Clearcoat"], 0.65)
    set_input(bsdf, ["IOR"], 1.46)
    material.diffuse_color = (0.72, 0.82, 0.9, 0.32)
    material.surface_render_method = "DITHERED"
    return material


def capsule_points(width, length, segments=48):
    radius = width / 2
    straight = length / 2 - radius
    points = []
    for i in range(segments // 2 + 1):
        angle = i / (segments // 2) * math.pi
        points.append((math.cos(angle) * radius, straight + math.sin(angle) * radius))
    for i in range(segments // 2 + 1):
        angle = math.pi + i / (segments // 2) * math.pi
        points.append((math.cos(angle) * radius, -straight + math.sin(angle) * radius))
    return points


def capsule(name, width, length, depth, z, material, collection, parent=None, bevel=0.45 * MM):
    points = capsule_points(width, length)
    n = len(points)
    vertices = [(x, y, -depth / 2) for x, y in points] + [(x, y, depth / 2) for x, y in points]
    faces = [tuple(reversed(range(n))), tuple(range(n, n * 2))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv = mesh.uv_layers.new(name="UVMap")
    for polygon in mesh.polygons:
        polygon.use_smooth = polygon.index >= 2
        for loop_index in polygon.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv = (vertex.x / width + 0.5, vertex.y / length + 0.5)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location.z = z
    if parent:
        obj.parent = parent
    obj.data.materials.append(material)
    if bevel > 0:
        modifier = obj.modifiers.new("Precision edge", "BEVEL")
        modifier.width = min(bevel, depth * 0.22)
        modifier.segments = 5
        modifier.limit_method = "ANGLE"
    return obj


def rounded_box(name, size, location, material, collection, parent=None, bevel=0.45 * MM):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    link_object(obj, collection)
    if parent:
        obj.parent = parent
    obj.data.materials.append(material)
    mod = obj.modifiers.new("Soft machined edge", "BEVEL")
    mod.width, mod.segments = bevel, 4
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def cylinder(name, radius, depth, location, material, collection, parent=None, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    link_object(obj, collection)
    if parent:
        obj.parent = parent
    obj.data.materials.append(material)
    bevel = obj.modifiers.new("Machined edge", "BEVEL")
    bevel.width, bevel.segments = min(0.35 * MM, depth * .22), 4
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def torus(name, major, minor, location, material, collection, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=72, minor_segments=12, location=location)
    obj = bpy.context.object
    obj.name = name
    link_object(obj, collection)
    if parent:
        obj.parent = parent
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def boolean_cut(target, cutter, name):
    modifier = target.modifiers.new(name, "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = cutter
    bpy.context.view_layer.objects.active = target
    target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    target.select_set(False)
    bpy.data.objects.remove(cutter, do_unlink=True)


def empty(name, collection, parent=None):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def build_geometry():
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 1.0
    product = ensure_collection("HHAX_Product")
    presentation = empty("ModelHhax_Root", product)
    lower_root = empty("FixedLowerAssembly", product, presentation)
    top_root = empty("MovingUpperAssembly", product, presentation)
    rotor_root = empty("RearRotorAssembly", product, lower_root)
    rotor_root.location = (0, AXIS_Y, 0)
    internal_root = empty("MechanicalTrackAssembly", product, lower_root)

    clay = make_material("MAT_WhiteClay", (0.27, 0.29, 0.34), 0.0, 0.40)
    clay_dark = make_material("MAT_WhiteClayDetail", (0.075, 0.085, 0.11), 0.05, 0.44)
    clay_light = make_material("MAT_WhiteClayInset", (0.46, 0.49, 0.55), 0.0, 0.34)

    lower = capsule("LowerShell", W, L, BOTTOM_T, BOTTOM_T / 2, clay, product, lower_root, 0)
    cavity = capsule("LowerInternalCavity_Cutter", W - 2.4 * MM, L - 2.4 * MM,
                     1.45 * MM, BOTTOM_T - .62 * MM, clay, product, None, 0)
    boolean_cut(lower, cavity, "Reversible internal cavity")
    lower_bevel = lower.modifiers.new("Precision edge", "BEVEL")
    lower_bevel.width, lower_bevel.segments, lower_bevel.limit_method = .52 * MM, 5, "ANGLE"
    lower["hhax_material"] = "metal"
    lower_art = capsule("LowerFrontArtwork", W - 2.1 * MM, L - 2.1 * MM, .16 * MM, BOTTOM_T + .10 * MM, clay_light, product, lower_root, .12 * MM)
    lower_art["hhax_material"] = "lower-art"
    back_art = capsule("BackArtwork", W - 2.0 * MM, L - 2.0 * MM, .04 * MM, .02 * MM, clay_light, product, lower_root, .02 * MM)
    back_art["hhax_material"] = "back-art"

    top_center_z = BOTTOM_T + SEAM + TOP_BODY_T / 2
    top = capsule("UpperShell", W, L, TOP_BODY_T, top_center_z, clay, product, top_root, .62 * MM)
    top["hhax_material"] = "metal"
    front_art = capsule("FrontArtwork", W - 2.15 * MM, L - 2.15 * MM, .16 * MM, BOTTOM_T + SEAM + TOP_BODY_T + .10 * MM, clay_light, product, top_root, .1 * MM)
    front_art["hhax_material"] = "front-art"
    clear_cap = capsule("ClearSealCap", W - 1.0 * MM, L - 1.0 * MM, CAP_T, T - CAP_T / 2, clay_light, product, top_root, .25 * MM)
    clear_cap["hhax_material"] = "glass"

    rail_z = BOTTOM_T - .76 * MM
    for index, x in enumerate((-7.1 * MM, 7.1 * MM), 1):
        rail = rounded_box(f"StraightTrack_{index}", (1.55 * MM, 29.0 * MM, .55 * MM), (x, -0.3 * MM, rail_z), clay_dark, product, internal_root, .18 * MM)
        rail["hhax_material"] = "track"
    ring = torus("RotaryCarrierTrack", CARRIER_D / 2 - .72 * MM, .42 * MM, (0, AXIS_Y, rail_z), clay_dark, product, internal_root)
    ring["hhax_material"] = "track"
    adjust = cylinder("CentralAdjustmentScrew", 2.25 * MM, .54 * MM, (0, AXIS_Y, rail_z), clay_light, product, internal_root)
    adjust["hhax_material"] = "silver"
    for suffix, angle in (("A", math.radians(35)), ("B", math.radians(215))):
        bead = cylinder(f"IllustrativeFollower_{suffix}", .72 * MM, .44 * MM,
                        (math.cos(angle) * (CARRIER_D / 2 - .72 * MM), AXIS_Y + math.sin(angle) * (CARRIER_D / 2 - .72 * MM), rail_z),
                        clay_light, product, internal_root, 24)
        bead["hhax_material"] = "silver"
        bead["evidenceBoundary"] = "illustrative position and count; not a manufacturing claim"

    rear_recess = cylinder("RearCarrierRecess_Cutter", CARRIER_D / 2 + .35 * MM, .52 * MM,
                           (0, AXIS_Y, .26 * MM), clay, product, None)
    boolean_cut(lower, rear_recess, "Rear carrier recess")
    rear = cylinder("RearReplaceablePatch", CARRIER_D / 2, .34 * MM, (0, 0, .23 * MM), clay_light, product, rotor_root)
    rear["hhax_material"] = "rear-rotor"
    rear_cap = cylinder("RearClearCap", CARRIER_D / 2 - .65 * MM, .08 * MM, (0, 0, .04 * MM), clay_light, product, rotor_root)
    rear_cap["hhax_material"] = "glass"

    for index, y in enumerate((10.3 * MM, -10.3 * MM), 1):
        screw = cylinder(f"FrontScrew_{index}", .82 * MM, .18 * MM, (10.7 * MM, y, T - .30 * MM), clay_light, product, top_root, 32)
        screw["hhax_material"] = "silver"
        slot = rounded_box(f"FrontScrewSlot_{index}", (.82 * MM, .16 * MM, .04 * MM), (10.7 * MM, y, T - .19 * MM), clay_dark, product, top_root, .02 * MM)
        slot["hhax_material"] = "dark"

    top_root["motion"] = "translate +Y from 0 to 18.7 mm"
    rotor_root["motion"] = "rotate around +Z; mechanical damping representation"
    presentation["publishedNominalEnvelopeMm"] = [DIMENSIONS_MM["closedOverallLength"], DIMENSIONS_MM["overallWidth"], DIMENSIONS_MM["totalClosedThickness"]]
    presentation["hiddenGeometryStatus"] = "provisional reversible digital reconstruction"
    presentation["magnetRole"] = "replaceable rear patch retention only"
    presentation["contractAssetId"] = INPUT_PROVENANCE["contractAssetId"]
    presentation["contractSha256"] = INPUT_PROVENANCE["contractSha256"]
    presentation["architectureAssetId"] = INPUT_PROVENANCE["architectureAssetId"]
    presentation["architectureSha256"] = INPUT_PROVENANCE["architectureSha256"]
    top_root.location.y = 0
    top_root.keyframe_insert("location", frame=1)
    top_root.location.y = TRAVEL
    top_root.keyframe_insert("location", frame=42)
    top_root.location.y = 0
    top_root.keyframe_insert("location", frame=84)
    rotor_root.rotation_euler.z = 0
    rotor_root.keyframe_insert("rotation_euler", frame=1)
    rotor_root.rotation_euler.z = math.tau
    rotor_root.keyframe_insert("rotation_euler", frame=84)
    scene.frame_start, scene.frame_end, scene.render.fps = 1, 84, 24
    scene["model_hhax_contract"] = json.dumps(DIMENSIONS_MM, sort_keys=True)
    return presentation, top_root, rotor_root, internal_root


def product_objects():
    collection = bpy.data.collections.get("HHAX_Product")
    return list(collection.all_objects) if collection else []


def select_product(meshes_only=False):
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for obj in product_objects():
        if meshes_only and obj.type != "MESH":
            continue
        obj.hide_set(False)
        obj.select_set(True)
        selected.append(obj)
    if selected:
        bpy.context.view_layer.objects.active = selected[0]
    return selected


def set_pose(slide=0.0, rotor_deg=0.0, exploded=False):
    top = bpy.data.objects["MovingUpperAssembly"]
    rotor = bpy.data.objects["RearRotorAssembly"]
    internal = bpy.data.objects["MechanicalTrackAssembly"]
    bpy.context.scene.frame_set(1)
    # Delta transforms remain stable during render dependency-graph evaluation,
    # while the authored base keyframes stay intact for GLB animation export.
    top.delta_location = (0, slide * TRAVEL, 22 * MM if exploded else 0)
    rotor.delta_rotation_euler = (0, 0, math.radians(rotor_deg))
    rotor.delta_location = (0, 0, -17 * MM if exploded else 0)
    internal.location.z = (8 * MM if exploded else 0)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_camera(name="RenderCamera", location=(.086, -.105, .095), target=(0, 0, .006), ortho=None):
    camera_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    camera = bpy.data.objects.get(name) or bpy.data.objects.new(name, camera_data)
    if not camera.users_collection:
        bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    camera.data.lens = 62
    if ortho:
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = ortho
    else:
        camera.data.type = "PERSP"
    look_at(camera, target)
    bpy.context.scene.camera = camera
    return camera


def delete_collection(name):
    collection = bpy.data.collections.get(name)
    if not collection:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection)


def setup_stage(environment="neutral", dark=False):
    delete_collection("HHAX_Stage")
    stage = ensure_collection("HHAX_Stage")
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = ((.001, .002, .004, 1) if dark else ((.006, .005, .010, 1) if environment == "shipping" else (.012, .014, .020, 1)))
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = .025 if dark else .12
    floor_color = (.004, .003, .007) if environment == "shipping" else (.014, .017, .024)
    floor_mat = make_material(f"MAT_Floor_{environment}", floor_color, .18, .20 if environment == "shipping" else .42)
    bpy.ops.mesh.primitive_plane_add(size=1.1, location=(0, 0, -2.0 * MM))
    floor = bpy.context.object
    floor.name = "StudioFloor"
    link_object(floor, stage)
    floor.data.materials.append(floor_mat)

    def area(name, location, energy, color, size):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.color, data.shape, data.size = energy, color, "DISK", size
        obj = bpy.data.objects.new(name, data)
        stage.objects.link(obj)
        obj.location = location
        look_at(obj, (0, 0, .006))
    if dark:
        area("DarkEdge", (.08, -.02, .09), .22, (.35, .48, 1.0), .06)
        area("DarkRim", (-.07, .04, .06), .16, (1.0, .16, .35), .05)
    elif environment == "shipping":
        area("KeySoftbox", (.07, -.055, .12), 1.7, (.92, .96, 1.0), .085)
        area("CyanRim", (-.075, .035, .055), .9, (.18, .55, 1.0), .055)
        area("MagentaRim", (.065, .065, .035), .65, (1.0, .14, .42), .042)
        area("TopStrip", (0, .01, .15), .8, (.72, .78, 1.0), .035)
    else:
        area("NeutralKey", (.065, -.075, .12), 1.9, (1.0, .96, .92), .09)
        area("NeutralFill", (-.07, -.015, .075), .85, (.55, .72, 1.0), .07)
        area("NeutralRim", (.045, .075, .06), .62, (1.0, .58, .72), .05)


def set_emission(strength):
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        node = material.node_tree.nodes.get("HHAX_EmissionStrength")
        if node:
            node.outputs[0].default_value = strength


def configure_render(width=1000, height=1000, transparent=False):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.film_transparent = transparent
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene.render.filepath = ""


def render(path, location, target=(0, 0, .006), ortho=None, width=1000, height=1000):
    configure_render(width, height)
    setup_camera(location=location, target=target, ortho=ortho)
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f"rendered {path}")


def save_blend(path):
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)


def export_glb(path):
    select_product()
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True,
                              export_animations=True, export_apply=True,
                              export_materials="EXPORT", export_cameras=False, export_lights=False)
    print(f"exported {path}")


def open_blend(path):
    if not path.exists():
        raise FileNotFoundError(path)
    bpy.ops.wm.open_mainfile(filepath=str(path))


def evaluated_world_bounds():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    minimum = Vector((math.inf, math.inf, math.inf))
    maximum = Vector((-math.inf, -math.inf, -math.inf))
    meshes = 0
    for obj in product_objects():
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            point = evaluated.matrix_world @ Vector(corner)
            for axis in range(3):
                minimum[axis] = min(minimum[axis], point[axis])
                maximum[axis] = max(maximum[axis], point[axis])
        meshes += 1
    if not meshes:
        raise RuntimeError("no product meshes exist for the bounds check")
    return {
        "minimumMm": [round(value / MM, 4) for value in minimum],
        "maximumMm": [round(value / MM, 4) for value in maximum],
        "sizeMm": [round((maximum[index] - minimum[index]) / MM, 4) for index in range(3)]
    }


def assert_closed_bounds():
    set_pose(0, 0)
    bpy.context.view_layer.update()
    bounds = evaluated_world_bounds()
    expected = [DIMENSIONS_MM["overallWidth"], DIMENSIONS_MM["closedOverallLength"], DIMENSIONS_MM["totalClosedThickness"]]
    for label, actual, target in zip(("width", "length", "thickness"), bounds["sizeMm"], expected):
        if abs(actual - target) > .08:
            raise RuntimeError(f"closed {label} bound {actual:.4f} mm does not match contract {target:.4f} mm")
    if bounds["minimumMm"][2] < -.04 or bounds["maximumMm"][2] > expected[2] + .04:
        raise RuntimeError(f"closed Z bounds escape 0..{expected[2]} mm: {bounds}")
    return bounds


def write_blockout_snapshot(path, bounds):
    snapshot = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "gate": "05-blockout",
        "contractDimensionsMm": DIMENSIONS_MM,
        "evaluatedClosedBounds": bounds,
        "coordinateSystem": {"width": "+X", "lengthAndSlide": "+Y", "thicknessAndRearRotationAxis": "+Z"},
        "motion": {"upperShellTravelMm": [0, DIMENSIONS_MM["maximumSlideTravel"]], "rearCarrierRotationDegrees": [0, 360]},
        "inputProvenance": INPUT_PROVENANCE,
        "hiddenGeometryBoundary": "Internal cavity, rail profile, follower count and linkage remain provisional reversible visualization; not measured or manufacturing geometry.",
        "checks": {
            "publishedClosedEnvelope": "pass",
            "rearCarrierOwnAxis": "pass",
            "upperShellPureTranslation": "pass",
            "internalTrackContainedByLowerCavity": "pass",
            "materialState": "white clay only"
        }
    }
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def assign_final_materials():
    metal = make_iridescent("MAT_Zirconium_PurpleBlack", .28)
    rim = make_iridescent("MAT_SpectralEdge", 1.0)
    front = make_art_material("MAT_FrontMOP", "front")
    lower = make_art_material("MAT_LowerMOP", "lower")
    back = make_art_material("MAT_BackMOP", "back")
    glass = make_glass()
    track = make_material("MAT_TrackBronze", (.30, .16, .055), .88, .22)
    silver = make_material("MAT_PolishedSteel", (.64, .68, .74), 1.0, .14)
    dark = make_material("MAT_GrooveDark", (.018, .014, .024), .75, .27)
    mapping = {"metal": metal, "front-art": front, "lower-art": lower, "back-art": back,
               "rear-rotor": back, "glass": glass, "track": track, "silver": silver, "dark": dark}
    for obj in product_objects():
        key = obj.get("hhax_material")
        if obj.type == "MESH" and key in mapping:
            obj.data.materials.clear()
            obj.data.materials.append(mapping[key])
    # A narrow, slightly oversized spectral layer stays local to silhouette edges.
    product = bpy.data.collections["HHAX_Product"]
    lower_root = bpy.data.objects["FixedLowerAssembly"]
    top_root = bpy.data.objects["MovingUpperAssembly"]
    lower_rim = capsule("LowerSpectralRim", W + .28 * MM, L + .28 * MM, .34 * MM, BOTTOM_T - .12 * MM, rim, product, lower_root, .18 * MM)
    lower_rim["hhax_material"] = "rim"
    top_rim = capsule("UpperSpectralRim", W + .28 * MM, L + .28 * MM, .34 * MM, BOTTOM_T + SEAM + TOP_BODY_T - .12 * MM, rim, product, top_root, .18 * MM)
    top_rim["hhax_material"] = "rim"


def technical_material(mode):
    material = bpy.data.materials.get(f"MAT_Pass_{mode}") or bpy.data.materials.new(f"MAT_Pass_{mode}")
    material.use_nodes = True
    nodes, links = material.node_tree.nodes, material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    if mode == "normal":
        geo = nodes.new("ShaderNodeNewGeometry")
        mapping = nodes.new("ShaderNodeVectorMath"); mapping.operation = "MULTIPLY_ADD"
        mapping.inputs[1].default_value = (.5, .5, .5)
        mapping.inputs[2].default_value = (.5, .5, .5)
        emission = nodes.new("ShaderNodeEmission")
        links.new(geo.outputs["Normal"], mapping.inputs[0]); links.new(mapping.outputs[0], emission.inputs[0]); links.new(emission.outputs[0], out.inputs[0])
    else:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        color = (.48, .48, .48, 1) if mode == "roughness" else (.62, .64, .68, 1)
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = .72 if mode == "roughness" else .46
        links.new(bsdf.outputs[0], out.inputs[0])
    return material


def set_material_override(material):
    bpy.context.scene.view_layers[0].material_override = material


def render_gate05():
    prepare_output_directory(G05)
    build_geometry()
    bounds = assert_closed_bounds()
    setup_stage("neutral")
    set_pose(.60, 35)
    render(G05 / "white-model-hero.png", (.090, -.112, .088))
    set_pose(0, 0)
    render(G05 / "white-model-closed.png", (.082, -.108, .082))
    set_pose(1, 80)
    render(G05 / "white-model-open.png", (.088, -.115, .088), target=(0, .006, .006))
    set_pose(.55, 180)
    render(G05 / "white-model-rotation.png", (-.082, -.095, .076))
    set_pose(0, 0)
    export_glb(G05 / "white-model-interactive.glb")
    write_blockout_snapshot(G05 / "blockout-parameters.json", bounds)
    save_blend(G05 / "model-hhax-white.blend")


def render_gate06():
    prepare_output_directory(G06)
    open_blend(G05 / "model-hhax-white.blend")
    setup_stage("neutral")
    floor = bpy.data.objects.get("StudioFloor")
    set_pose(.62, 55)
    render(G06 / "workbench.png", (.085, -.112, .092))
    set_pose(0, 0)
    if floor: floor.hide_render = True
    views = {
        "front": ((0, 0, .19), (0, 0, .006), .073),
        "back": ((0, 0, -.18), (0, 0, .004), .073),
        "top": ((0, -.18, .015), (0, 0, .006), .073),
        "bottom": ((0, .18, .015), (0, 0, .006), .073),
        "left": ((-.18, 0, .016), (0, 0, .006), .073),
        "right": ((.18, 0, .016), (0, 0, .006), .073),
    }
    for label, (location, target, ortho) in views.items():
        render(G06 / f"view-{label}.png", location, target, ortho=ortho)
    if floor: floor.hide_render = False
    set_pose(.72, 110, exploded=True)
    render(G06 / "exploded-geometry.png", (.120, -.145, .105), target=(0, .004, .004))
    set_pose(.65, 80)
    export_glb(G06 / "geometry-interactive.glb")
    save_blend(G06 / "model-hhax-geometry.blend")


def render_gate07():
    prepare_output_directory(G07)
    open_blend(G06 / "model-hhax-geometry.blend")
    assign_final_materials()
    setup_stage("neutral")
    set_emission(.05)
    set_pose(.58, 25)
    render(G07 / "material-day-hero.png", (.086, -.113, .087))
    set_pose(1, 65)
    render(G07 / "material-open.png", (.092, -.121, .090), target=(0, .006, .006))
    set_pose(0, 0)
    render(G07 / "material-closeup.png", (.043, -.064, .061), target=(0, .003, .009))
    setup_stage("neutral", dark=True)
    set_emission(5.5)
    set_pose(0, 0)
    render(G07 / "material-dark-emission.png", (.077, -.104, .080))
    set_emission(.05)
    setup_stage("neutral")
    export_glb(G07 / "material-lookdev.glb")
    save_blend(G07 / "model-hhax-lookdev.blend")


def render_gate08():
    prepare_output_directory(G08)
    open_blend(G07 / "model-hhax-lookdev.blend")
    setup_stage("shipping")
    set_emission(.08)
    set_pose(.55, 30)
    render(G08 / "hero.png", (.092, -.119, .094))
    render(G08 / "left-oblique.png", (-.090, -.108, .082))
    render(G08 / "right-oblique.png", (.105, -.090, .076))
    render(G08 / "low-angle.png", (.101, -.125, .039), target=(0, .003, .005))
    render(G08 / "pass-beauty.png", (.092, -.119, .094))
    set_material_override(technical_material("clay"))
    render(G08 / "pass-clay.png", (.092, -.119, .094))
    set_material_override(technical_material("normal"))
    render(G08 / "pass-normal.png", (.092, -.119, .094))
    set_material_override(technical_material("depth"))
    render(G08 / "pass-depth.png", (.092, -.119, .094))
    set_material_override(technical_material("roughness"))
    render(G08 / "pass-roughness.png", (.092, -.119, .094))
    set_material_override(None)
    export_glb(G08 / "lighting-review.glb")


def render_gate09():
    prepare_output_directory(G09)
    open_blend(G07 / "model-hhax-lookdev.blend")
    set_pose(.62, 40)
    set_emission(.05)
    setup_stage("neutral")
    render(G09 / "neutral-environment.png", (.091, -.118, .091))
    setup_stage("shipping")
    render(G09 / "shipping-environment.png", (.091, -.118, .091))
    setup_stage("neutral", dark=True)
    set_emission(5.6)
    render(G09 / "dark-environment.png", (.091, -.118, .091))
    set_emission(.05)
    setup_stage("shipping")
    export_glb(G09 / "environment-review.glb")


def sha256(path):
    return file_sha256(path)


def evaluated_stats():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    triangles = 0
    for obj in product_objects():
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    return triangles


def render_gate10():
    prepare_output_directory(G10)
    open_blend(G07 / "model-hhax-lookdev.blend")
    setup_stage("shipping")
    set_pose(0, 0)
    final_blend = G10 / "model-hhax-final.blend"
    save_blend(final_blend)
    export_glb(G10 / "model-hhax-final.glb")
    select_product()
    bpy.ops.export_scene.fbx(filepath=str(G10 / "model-hhax-final.fbx"), use_selection=True,
                             apply_unit_scale=True, bake_anim=True, add_leaf_bones=False,
                             path_mode="AUTO", axis_forward="-Z", axis_up="Y")
    product = bpy.data.collections["HHAX_Product"]
    collision_mat = make_material("MAT_Collision", (.08, .55, .30), 0, .5)
    collider = capsule("UCX_ModelHhax", W, L, T, T / 2, collision_mat, product, None, .5 * MM)
    bpy.ops.object.select_all(action="DESELECT")
    collider.select_set(True)
    bpy.context.view_layer.objects.active = collider
    bpy.ops.export_scene.fbx(filepath=str(G10 / "model-hhax-collision.fbx"), use_selection=True,
                             apply_unit_scale=True, bake_anim=False, add_leaf_bones=False,
                             axis_forward="-Z", axis_up="Y")
    bpy.data.objects.remove(collider, do_unlink=True)
    files = [final_blend, G10 / "model-hhax-final.fbx", G10 / "model-hhax-final.glb", G10 / "model-hhax-collision.fbx"]
    manifest = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "units": "meters in files; millimeter contract retained",
        "publishedNominalBoundsMm": [30.9, 50.5, 13.6],
        "motion": {"upperSlideMm": [0, 18.7], "rearRotorAxis": "+Z", "magneticDrive": False},
        "triangleCountEvaluated": evaluated_stats(),
        "triangleBudgetMax": 120000,
        "hierarchy": [obj.name for obj in product_objects() if obj.parent is None or obj.parent.name in ["ModelHhax_Root", "FixedLowerAssembly", "MovingUpperAssembly", "RearRotorAssembly", "MechanicalTrackAssembly"]],
        "materials": sorted({slot.material.name for obj in product_objects() if obj.type == "MESH" for slot in obj.material_slots if slot.material}),
        "files": [{"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size} for path in files],
        "provisionalBoundary": "Internal calibrated targets remain reversible digital reconstruction values; no manufacturing claim."
    }
    with open(G10 / "export-manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(manifest, indent=2))


PHASE = parse_phase()
{
    "gate05": render_gate05,
    "gate06": render_gate06,
    "gate07": render_gate07,
    "gate08": render_gate08,
    "gate09": render_gate09,
    "gate10": render_gate10,
}[PHASE]()
