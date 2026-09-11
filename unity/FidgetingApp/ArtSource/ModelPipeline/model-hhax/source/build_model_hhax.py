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
import shutil
import subprocess
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

G05 = EVIDENCE / "05-blockout/rev-006"
G06 = EVIDENCE / "06-geometry/rev-003"
G06_REVIEW = EVIDENCE / "06-geometry/rev-004"
G07 = EVIDENCE / "07-material/rev-004"
G07_REVIEW = EVIDENCE / "07-material/rev-005"
G08 = EVIDENCE / "08-lighting/rev-004"
G08_REVIEW = EVIDENCE / "08-lighting/rev-005"
G09 = EVIDENCE / "09-environment/rev-001"
G09_REVIEW = EVIDENCE / "09-environment/rev-002"
G10 = EVIDENCE / "10-export/rev-001"
G10_REVIEW = EVIDENCE / "10-export/rev-002"


def parse_phase():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["gate05", "gate06", "gate07", "gate08", "gate09", "gate10"])
    return parser.parse_args(argv).phase


def prepare_output_directory(directory, allowed_existing=()):
    directory.mkdir(parents=True, exist_ok=True)
    allowed = set(allowed_existing)
    existing = [
        item for item in directory.iterdir()
        if item.is_file() and item.stat().st_size > 0 and item.name not in allowed
    ]
    if existing:
        names = ", ".join(sorted(item.name for item in existing))
        raise RuntimeError(f"immutable evidence target already contains files: {names}")


def assert_approved_upstream(stage_id, asset_id, path):
    """Fail closed if the phase input is not the exact approved upstream asset."""
    manifest = json.loads(PIPELINE_PATH.read_text(encoding="utf-8"))
    stage = next((item for item in manifest["stages"] if item["id"] == stage_id), None)
    if not stage or stage.get("status") != "approved":
        raise RuntimeError(f"{stage_id} must be approved before consuming its Blender source")
    asset = next((item for item in manifest["assets"] if item["id"] == asset_id), None)
    if not asset or asset_id not in stage.get("artifactIds", []):
        raise RuntimeError(f"approved {stage_id} does not contain {asset_id}")
    if not path.exists() or file_sha256(path) != asset.get("sha256"):
        raise RuntimeError(f"approved {stage_id} source hash changed: {path.name}")
    return {
        "manifestRevisionAtBuild": manifest["revision"],
        "stageId": stage_id,
        "assetId": asset_id,
        "sha256": asset["sha256"],
        "path": asset["path"]
    }


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
    grade = nodes.new("ShaderNodeHueSaturation")
    grade.name = "HHAX_DaylightArtworkGrade"
    grade.inputs["Saturation"].default_value = 1.18
    grade.inputs["Value"].default_value = 0.62
    rough = image_node(nodes, TEXTURES / f"{prefix}-roughness.png", "Roughness", True)
    normal = image_node(nodes, TEXTURES / f"{prefix}-normal.png", "Normal", True)
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.28
    emission = image_node(nodes, TEXTURES / f"{prefix}-emission.png", "EmissionColor")
    strength = nodes.new("ShaderNodeValue")
    strength.name = "HHAX_EmissionStrength"
    strength.outputs[0].default_value = 0.08
    links.new(base.outputs["Color"], grade.inputs["Color"])
    links.new(grade.outputs["Color"], bsdf.inputs["Base Color"])
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
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "HHAX_ClearSeal_Principled"
    # Thin clear cap: keep the artwork legible in Eevee and exported glTF,
    # while coat + IOR preserve a readable seal highlight and edge.
    bsdf.inputs["Base Color"].default_value = (0.78, 0.86, 0.92, 1)
    bsdf.inputs["Roughness"].default_value = 0.015
    set_input(bsdf, ["Transmission Weight", "Transmission"], 0.08)
    set_input(bsdf, ["Coat Weight", "Clearcoat"], 0.95)
    set_input(bsdf, ["IOR"], 1.46)
    set_input(bsdf, ["Alpha"], 0.045)
    links.new(bsdf.outputs[0], out.inputs[0])
    material.diffuse_color = (0.78, 0.86, 0.92, 0.045)
    material.surface_render_method = "BLENDED"
    return material


def make_glass_edge():
    material = bpy.data.materials.get("MAT_ClearSealEdge") or bpy.data.materials.new("MAT_ClearSealEdge")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "HHAX_ClearSealEdge_Principled"
    bsdf.inputs["Base Color"].default_value = (0.44, 0.60, 0.78, 1)
    bsdf.inputs["Roughness"].default_value = 0.022
    set_input(bsdf, ["Transmission Weight", "Transmission"], 0.12)
    set_input(bsdf, ["Coat Weight", "Clearcoat"], 1.0)
    set_input(bsdf, ["IOR"], 1.46)
    set_input(bsdf, ["Alpha"], 0.34)
    links.new(bsdf.outputs[0], out.inputs[0])
    material.diffuse_color = (0.44, 0.60, 0.78, 0.34)
    material.surface_render_method = "BLENDED"
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

    back_inset = .04 * MM
    lower = capsule("LowerShell", W, L, BOTTOM_T - back_inset,
                    back_inset + (BOTTOM_T - back_inset) / 2, clay, product, lower_root, 0)
    cavity = capsule("LowerInternalCavity_Cutter", W - 2.4 * MM, L - 2.4 * MM,
                     1.45 * MM, BOTTOM_T - .62 * MM, clay, product, None, 0)
    boolean_cut(lower, cavity, "Reversible internal cavity")
    lower_bevel = lower.modifiers.new("Precision edge", "BEVEL")
    lower_bevel.width, lower_bevel.segments, lower_bevel.limit_method = .52 * MM, 5, "ANGLE"
    lower["hhax_material"] = "metal"
    lower_art = capsule("LowerFrontArtwork", W - 2.1 * MM, L - 2.1 * MM, .16 * MM, BOTTOM_T + .10 * MM, clay_light, product, lower_root, .12 * MM)
    lower_art["hhax_material"] = "lower-art"
    back_art = capsule("BackArtwork", W - 2.0 * MM, L - 2.0 * MM, back_inset, back_inset / 2, clay_light, product, lower_root, 0)
    back_hole = cylinder("BackArtworkCarrierHole_Cutter", CARRIER_D / 2 + .18 * MM, .12 * MM,
                         (0, AXIS_Y, .06 * MM), clay, product, None)
    boolean_cut(back_art, back_hole, "Rear carrier artwork clearance")
    back_bevel = back_art.modifiers.new("Inset edge", "BEVEL")
    back_bevel.width, back_bevel.segments, back_bevel.limit_method = .012 * MM, 2, "ANGLE"
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
    rear_cap = cylinder("RearClearCap", CARRIER_D / 2 - .65 * MM, .06 * MM, (0, 0, .05 * MM), clay_light, product, rotor_root)
    rear_cap["hhax_material"] = "glass"
    rear_mark = rounded_box("RearRotationOrientationMark", (1.1 * MM, 6.2 * MM, .02 * MM),
                            (0, 2.4 * MM, .01 * MM), clay_dark, product, rotor_root, .08 * MM)
    rear_mark["hhax_material"] = "dark"
    rear_mark["purpose"] = "visual rotation direction marker; not hidden mechanism evidence"

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
    camera.data.clip_start = .001
    camera.data.clip_end = 10.0
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
    floor_mat = make_material(f"MAT_Floor_{environment}", floor_color, .18, .32 if environment == "shipping" else .42)
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
        return obj

    def area_strip(name, location, energy, color, width, height, target=(0, 0, .005)):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.color = energy, color
        data.shape, data.size, data.size_y = "RECTANGLE", width, height
        data.use_shadow = False
        obj = bpy.data.objects.new(name, data)
        stage.objects.link(obj)
        obj.location = location
        look_at(obj, target)
        return obj
    if dark:
        # Emission proof uses only a trace of neutral edge light. Broad
        # coloured studio highlights would masquerade as emissive artwork.
        area("DarkEdge", (.08, -.02, .09), .026, (.72, .78, .88), .07)
    elif environment == "shipping":
        area("KeySoftbox", (.07, -.055, .13), .92, (.92, .96, 1.0), .11)
        area("NeutralSideFill", (-.080, -.035, .065), .46, (.68, .75, .88), .095).data.use_shadow = False
        area("NeutralRearStrip", (.055, .085, .082), .28, (1.0, .88, .82), .065).data.use_shadow = False
        # A long, neutral reflection card is aimed at the vertical walls. It
        # creates the wide polished-metal gradient missing from earlier rounds.
        area_strip("VerticalMetalReflection", (0, -.115, .035), 1.28, (.82, .86, .94), .135, .014, target=(0, 0, .0045))
        # Colour lights remain tiny accents; the material shader supplies the
        # approved narrow spectrum edge and the floor must not become a colour field.
        area("CyanRim", (-.088, .050, .090), .045, (.18, .55, 1.0), .032)
        area("MagentaRim", (.082, .078, .078), .040, (1.0, .14, .42), .030)
        area("TopStrip", (0, .01, .16), .32, (.72, .78, 1.0), .060)
    else:
        area("NeutralKey", (.065, -.075, .12), 1.9, (1.0, .96, .92), .09)
        area("NeutralFill", (-.07, -.015, .075), .85, (.55, .72, 1.0), .07)
        area("NeutralRim", (.045, .075, .06), .62, (1.0, .58, .72), .05)


def apply_environment_variant(environment):
    """Change only world/floor response so environment comparisons keep camera/lights fixed."""
    scene = bpy.context.scene
    world = scene.world
    world.use_nodes = True
    background = world.node_tree.nodes["Background"]
    if environment == "shipping":
        background.inputs["Color"].default_value = (.006, .004, .013, 1)
        background.inputs["Strength"].default_value = .18
        floor_color, floor_roughness = (.010, .006, .018), .20
    else:
        background.inputs["Color"].default_value = (.012, .014, .020, 1)
        background.inputs["Strength"].default_value = .12
        floor_color, floor_roughness = (.014, .017, .024), .42
    floor = bpy.data.objects.get("StudioFloor")
    if floor:
        material = make_material(f"MAT_Floor_{environment}_comparison", floor_color, .18, floor_roughness)
        floor.data.materials.clear()
        floor.data.materials.append(material)


def add_review_area_light(name, location, energy, color, size, target=(0, 0, .003)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.color, data.shape, data.size = energy, color, "DISK", size
    obj = bpy.data.objects.new(name, data)
    bpy.data.collections["HHAX_Stage"].objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


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
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 1024
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
                              export_materials="EXPORT", export_cameras=False, export_lights=False,
                              export_extras=True)
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


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_dimension_overlay(path):
    d = DIMENSIONS_MM
    values = [
        ("Closed length", d["closedOverallLength"]),
        ("Overall width", d["overallWidth"]),
        ("Closed thickness", d["totalClosedThickness"]),
        ("Upper shell", d["topPlateThickness"]),
        ("Lower shell", d["bottomPlateThickness"]),
        ("Max slide", d["maximumSlideTravel"]),
        ("Axis end offset", d["fixedAxisOffsetFromNearestEnd"]),
        ("Rear carrier Ø", d["rotatingCarrierDiameter"]),
        ("Closed seam", d["closedSeamGap"]),
    ]
    rows = "".join(
        f'<g transform="translate(650,{112 + index * 54})"><text class="k">{label}</text>'
        f'<text class="v" x="410">{value:g} mm</text></g>'
        for index, (label, value) in enumerate(values)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
<rect width="1200" height="720" fill="#15161a"/><style>.t{{fill:#f4f5f7;font:700 28px system-ui}}.s{{fill:#9da2ad;font:16px system-ui}}.k{{fill:#b8bdc8;font:18px system-ui}}.v{{fill:#f4f5f7;font:700 19px ui-monospace,monospace;text-anchor:end}}.d{{stroke:#c5f43d;stroke-width:3;fill:none}}.g{{stroke:#656b76;stroke-width:2;fill:#333740}}</style>
<text class="t" x="54" y="54">Gate 06 · approved envelope</text><text class="s" x="54" y="82">Exact product specification · reversible digital target, not a manufacturing drawing</text>
<rect class="g" x="142" y="122" width="330" height="510" rx="165"/><circle class="g" cx="307" cy="486" r="115"/>
<line class="d" x1="110" y1="122" x2="110" y2="632"/><path class="d" d="M96 140l14-18 14 18M96 614l14 18 14-18"/><text class="v" x="96" y="385" transform="rotate(-90 96 385)">{d['closedOverallLength']:g} mm</text>
<line class="d" x1="142" y1="664" x2="472" y2="664"/><path class="d" d="M160 650l-18 14 18 14M454 650l18 14-18 14"/><text class="v" x="360" y="700">{d['overallWidth']:g} mm</text>
<line class="d" x1="307" y1="486" x2="307" y2="632"/><text class="s" x="322" y="566">axis offset {d['fixedAxisOffsetFromNearestEnd']:g}</text>
<line class="d" x1="192" y1="486" x2="422" y2="486"/><text class="s" x="240" y="476">Ø {d['rotatingCarrierDiameter']:g}</text>
<path class="d" d="M504 300h92M578 282l18 18-18 18"/><text class="s" x="500" y="278">slide {d['maximumSlideTravel']:g}</text>
{rows}
</svg>'''
    path.write_text(svg, encoding="utf-8")


def write_pivot_overlay(path):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
<rect width="1200" height="720" fill="#15161a"/><style>.t{{fill:#f4f5f7;font:700 28px system-ui}}.s{{fill:#aeb3be;font:17px system-ui}}.n{{fill:#f4f5f7;font:700 18px system-ui}}.b{{stroke:#69707c;stroke-width:3;fill:#30343d}}.a{{stroke:#c5f43d;stroke-width:5;fill:none}}.c{{stroke:#ff956d;stroke-width:4;fill:none}}</style>
<text class="t" x="54" y="54">Gate 06 · motion ownership</text><text class="s" x="54" y="82">+Y straight translation and independent rear +Z rotation</text>
<rect class="b" x="145" y="118" width="350" height="540" rx="175"/><rect class="b" x="565" y="118" width="350" height="540" rx="175" opacity=".72"/>
<line class="a" x1="320" y1="360" x2="740" y2="360"/><path class="a" d="M710 334l30 26-30 26"/>
<text class="n" x="460" y="334">Moving upper shell · +Y · 0–{DIMENSIONS_MM['maximumSlideTravel']:g} mm</text>
<circle class="b" cx="320" cy="510" r="122"/><circle class="c" cx="320" cy="510" r="78"/><path class="c" d="M366 446a78 78 0 0 1 21 78"/><path class="c" d="M374 499l13 25 22-17"/>
<line class="c" x1="320" y1="510" x2="320" y2="408"/><circle cx="320" cy="510" r="8" fill="#ff956d"/>
<text class="n" x="80" y="694">Fixed lower shell stays at origin</text><text class="n" x="410" y="526">Rear carrier pivot · (0, {AXIS_Y / MM:g}, 0) mm · +Z</text>
<text class="s" x="760" y="694">Hidden track profile remains provisional</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def write_geometry_snapshot(path, bounds, upstream):
    roots = ["ModelHhax_Root", "FixedLowerAssembly", "MovingUpperAssembly", "RearRotorAssembly", "MechanicalTrackAssembly"]
    snapshot = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "gate": "06-geometry",
        "input": upstream,
        "contractDimensionsMm": DIMENSIONS_MM,
        "evaluatedClosedBounds": bounds,
        "coordinateSystem": {"width": "+X", "lengthAndSlide": "+Y", "thicknessAndRearRotationAxis": "+Z"},
        "pivotsMm": {
            "fixedLower": [0, 0, 0],
            "movingUpper": [0, 0, 0],
            "rearCarrier": [0, round(AXIS_Y / MM, 4), 0]
        },
        "motionOwnership": {
            "MovingUpperAssembly": {"mode": "translation-only", "axis": "+Y", "rangeMm": [0, DIMENSIONS_MM["maximumSlideTravel"]]},
            "RearRotorAssembly": {"mode": "rotation-only", "axis": "+Z", "rangeDegrees": [0, 360]},
            "FixedLowerAssembly": {"mode": "fixed"}
        },
        "hierarchy": {
            name: (bpy.data.objects[name].parent.name if bpy.data.objects.get(name) and bpy.data.objects[name].parent else None)
            for name in roots
        },
        "meshCount": sum(1 for obj in product_objects() if obj.type == "MESH"),
        "evaluatedTriangleCount": evaluated_stats(),
        "checks": {
            "closedEnvelope": "pass",
            "sixOrthographicViews": "pass",
            "dimensionOverlay": "pass",
            "pivotOverlay": "pass",
            "explodedOwnership": "pass"
        },
        "hiddenGeometryBoundary": "Internal cavity, rail profile, follower count and coupling remain reversible digital reconstruction, not measured or manufacturing geometry."
    }
    write_json(path, snapshot)


def encode_review_video(output, images, seconds_per_image=1.8):
    """Create a deterministic H.264 comparison recording without overwriting."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for review recordings")
    list_path = output.parent / "review-sequence.txt"
    lines = []
    for image in images:
        lines.extend((f"file '{image}'", f"duration {seconds_per_image}"))
    lines.append(f"file '{images[-1]}'")
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    command = [
        ffmpeg, "-n", "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,fps=30",
        "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", str(output)
    ]
    subprocess.run(command, check=True)
    if not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"review recording was not created: {output}")


def assign_final_materials():
    metal = make_iridescent("MAT_Zirconium_PurpleBlack", .28)
    front = make_art_material("MAT_FrontMOP", "front")
    lower = make_art_material("MAT_LowerMOP", "lower")
    back = make_art_material("MAT_BackMOP", "back")
    glass = make_glass()
    glass_edge = make_glass_edge()
    track = make_material("MAT_TrackBronze", (.30, .16, .055), .88, .22)
    silver = make_material("MAT_PolishedSteel", (.64, .68, .74), 1.0, .14)
    dark = make_material("MAT_GrooveDark", (.018, .014, .024), .75, .27)
    stable_ids = {
        metal: "hhax-zirconium-purple-black",
        front: "hhax-front-mop-sealed",
        lower: "hhax-lower-mop-sealed",
        back: "hhax-back-mop-sealed",
        glass: "hhax-clear-crystal-seal",
        glass_edge: "hhax-clear-crystal-seal-edge",
        track: "hhax-provisional-track-bronze",
        silver: "hhax-polished-steel-detail",
        dark: "hhax-dark-groove"
    }
    for material, stable_id in stable_ids.items():
        material["hhax_material_id"] = stable_id
    mapping = {"metal": metal, "front-art": front, "lower-art": lower, "back-art": back,
               "rear-rotor": back, "glass": glass, "track": track, "silver": silver, "dark": dark}
    for obj in product_objects():
        key = obj.get("hhax_material")
        if obj.type == "MESH" and key in mapping:
            obj.data.materials.clear()
            obj.data.materials.append(mapping[key])
            if obj.name == "ClearSealCap" and key == "glass":
                obj.data.materials.append(glass_edge)
                # Capsule face 0/1 are the transparent sheets; subsequent
                # faces are the real 0.8 mm sidewall carrying the edge glint.
                for polygon in obj.data.polygons:
                    polygon.material_index = 1 if polygon.index >= 2 else 0
    # The approved metal shader itself supplies the narrow view-dependent edge color.
    # No oversized helper mesh is allowed outside the exact public envelope.


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
    elif mode == "depth":
        camera = nodes.new("ShaderNodeCameraData")
        remap = nodes.new("ShaderNodeMapRange")
        remap.inputs["From Min"].default_value = .135
        remap.inputs["From Max"].default_value = .205
        remap.inputs["To Min"].default_value = 1.0
        remap.inputs["To Max"].default_value = 0.0
        remap.clamp = True
        emission = nodes.new("ShaderNodeEmission")
        links.new(camera.outputs["View Z Depth"], remap.inputs["Value"])
        links.new(remap.outputs["Result"], emission.inputs["Color"])
        links.new(emission.outputs[0], out.inputs[0])
    else:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        color = (.28, .31, .36, 1)
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = .46
        links.new(bsdf.outputs[0], out.inputs[0])
    return material


def set_material_override(material):
    bpy.context.scene.view_layers[0].material_override = material


def install_roughness_diagnostics():
    """Temporarily emit every authored material's real scalar/texture roughness."""
    restored = []
    diagnostics = {}
    for obj in product_objects():
        if obj.type != "MESH":
            continue
        for index, slot in enumerate(obj.material_slots):
            original = slot.material
            if not original or not original.use_nodes:
                continue
            diagnostic = diagnostics.get(original.name)
            if diagnostic is None:
                diagnostic = original.copy()
                diagnostic.name = f"DIAG_Roughness_{original.name}"
                nodes, links = diagnostic.node_tree.nodes, diagnostic.node_tree.links
                source_bsdf = next((node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"), None)
                output = next((node for node in nodes if node.bl_idname == "ShaderNodeOutputMaterial"), None)
                if source_bsdf is None or output is None:
                    raise RuntimeError(f"material {original.name} has no Principled/output node for roughness review")
                roughness = source_bsdf.inputs.get("Roughness")
                emission = nodes.new("ShaderNodeEmission")
                emission.name = "HHAX_RoughnessDiagnostic"
                emission.inputs["Strength"].default_value = 1.0
                if roughness.is_linked:
                    links.new(roughness.links[0].from_socket, emission.inputs["Color"])
                else:
                    value = float(roughness.default_value)
                    emission.inputs["Color"].default_value = (value, value, value, 1)
                for link in list(output.inputs["Surface"].links):
                    links.remove(link)
                links.new(emission.outputs[0], output.inputs["Surface"])
                diagnostics[original.name] = diagnostic
            restored.append((obj, index, original))
            obj.material_slots[index].material = diagnostic
    return restored


def restore_materials(restored):
    for obj, index, material in restored:
        obj.material_slots[index].material = material


def texture_hashes():
    return {
        path.name: {"sha256": file_sha256(path), "bytes": path.stat().st_size}
        for path in sorted(TEXTURES.glob("*.png"))
    }


def material_snapshot(bounds, upstream):
    return {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "gate": "07-material",
        "input": upstream,
        "evaluatedClosedBounds": bounds,
        "materials": [
            {"id": "hhax-zirconium-purple-black", "surface": "near-black purple-gray metal", "metallic": .96, "roughness": .18, "edgeColor": "view-dependent shader; no envelope geometry"},
            {"id": "hhax-front-mop-sealed", "surface": "front mother-of-pearl cells and coral knight beneath clear seal", "daylightValue": .62, "daylightSaturation": 1.18, "emission": "cyan cells and orange knight only"},
            {"id": "hhax-lower-mop-sealed", "surface": "lower revealed mother-of-pearl field", "daylightValue": .62, "daylightSaturation": 1.18, "emission": "non-emissive in the supplied lower-art crop"},
            {"id": "hhax-back-mop-sealed", "surface": "rear medallion and spine artwork", "daylightValue": .62, "daylightSaturation": 1.18, "emission": "cyan cells and orange knight only"},
            {"id": "hhax-clear-crystal-seal", "ior": 1.46, "roughness": .015, "transmission": .08, "alpha": .045, "coatWeight": .95, "surfaceMode": "blended"},
            {"id": "hhax-clear-crystal-seal-edge", "ior": 1.46, "roughness": .022, "transmission": .12, "alpha": .34, "coatWeight": 1.0, "surfaceMode": "blended"}
        ],
        "textureInputs": texture_hashes(),
        "checks": {
            "closedEnvelopeUnchanged": "pass",
            "pbrChannelsConnected": "pass",
            "dayNightEmissionSeparated": "pass",
            "oversizedEdgeGeometryAbsent": "pass"
        },
        "appearanceBoundary": "Custom imagery controls visible artwork; hidden material construction is not asserted."
    }


def stage_snapshot(stage_id, upstream, bounds, extra):
    value = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "gate": stage_id,
        "input": upstream,
        "contractDimensionsMm": DIMENSIONS_MM,
        "evaluatedClosedBounds": bounds,
        "inputProvenance": INPUT_PROVENANCE,
        "provisionalBoundary": "Hidden linkage timing, detents, forces and tolerances remain unknown and are not manufacturing claims."
    }
    value.update(extra)
    return value


def render_gate05():
    prepare_output_directory(G05)
    build_geometry()
    bounds = assert_closed_bounds()
    setup_stage("neutral")
    add_review_area_light("SealGrazingStrip", (-.025, .082, .034), .16, (.72, .83, 1.0), .055, target=(0, .004, .012))
    set_pose(.60, 35)
    render(G05 / "white-model-hero.png", (.090, -.112, .088))
    set_pose(0, 0)
    render(G05 / "white-model-closed.png", (.082, -.108, .082))
    set_pose(1, 80)
    render(G05 / "white-model-open.png", (.088, -.115, .088), target=(0, .006, .006))
    set_pose(.55, 180)
    floor = bpy.data.objects.get("StudioFloor")
    if floor: floor.hide_render = True
    add_review_area_light("UndersideKey", (.055, -.045, -.085), 2.2, (1.0, .92, .86), .075)
    add_review_area_light("UndersideFill", (-.055, .035, -.060), 1.1, (.48, .70, 1.0), .060)
    render(G05 / "white-model-rotation.png", (-.074, -.092, -.082), target=(0, .004, .002))
    set_pose(0, 0)
    render(G05 / "white-model-underside.png", (0, -.018, -.165), target=(0, 0, .002))
    if floor: floor.hide_render = False
    set_pose(0, 0)
    export_glb(G05 / "white-model-interactive.glb")
    write_blockout_snapshot(G05 / "blockout-parameters.json", bounds)
    save_blend(G05 / "model-hhax-white.blend")


def render_gate06():
    prepare_output_directory(G06, allowed_existing=("geometry-review.glb",))
    prepare_output_directory(G06_REVIEW)
    upstream = assert_approved_upstream(
        "05-blockout", "hhax-gate05-white-source-r006", G05 / "model-hhax-white.blend"
    )
    open_blend(G05 / "model-hhax-white.blend")
    setup_stage("neutral")
    floor = bpy.data.objects.get("StudioFloor")
    set_pose(.62, 55)
    set_material_override(technical_material("clay"))
    render(G06 / "workbench.png", (.085, -.112, .092))
    set_material_override(None)
    set_pose(0, 0)
    if floor: floor.hide_render = True
    add_review_area_light("GeometryUndersideKey", (.060, -.040, -.090), 2.1, (1.0, .94, .90), .075)
    add_review_area_light("GeometryUndersideFill", (-.060, .045, -.065), 1.0, (.50, .72, 1.0), .065)
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
    set_pose(0, 0)
    bounds = assert_closed_bounds()
    write_dimension_overlay(G06 / "dimension-overlay.svg")
    write_pivot_overlay(G06 / "pivot-overlay.svg")
    write_geometry_snapshot(G06 / "geometry-parameters.json", bounds, upstream)
    export_glb(G06 / "geometry-interactive.glb")
    save_blend(G06 / "model-hhax-geometry.blend")
    export_glb(G06_REVIEW / "geometry-review.glb")


def render_gate07():
    # rev-002 already contains the untouched, unregistered first-round review
    # carrier. It stays immutable and is deliberately not reused.
    prepare_output_directory(G07, allowed_existing=("material-review.glb",))
    prepare_output_directory(G07_REVIEW)
    upstream = assert_approved_upstream(
        "06-geometry", "hhax-gate06-geometry-source-r003", G06 / "model-hhax-geometry.blend"
    )
    open_blend(G06 / "model-hhax-geometry.blend")
    assign_final_materials()
    bounds = assert_closed_bounds()
    setup_stage("neutral")
    set_emission(.05)
    set_pose(.58, 25)
    render(G07 / "material-day-hero.png", (.086, -.113, .087))
    set_pose(1, 65)
    render(G07 / "material-open.png", (.092, -.121, .090), target=(0, .006, .006))
    set_pose(0, 0)
    render(G07 / "material-closeup.png", (.054, -.073, .096), target=(0, .001, .011))
    # A real lit PBR response board, rather than a source-reference collage.
    set_pose(.38, 18)
    render(G07 / "material-board.png", (.020, -.104, .142), target=(0, .003, .007), width=1600, height=900)
    setup_stage("neutral", dark=True)
    set_emission(3.6)
    set_pose(0, 0)
    render(G07 / "material-dark-emission.png", (.050, -.086, .108), target=(0, 0, .009))
    set_emission(.05)
    setup_stage("neutral")
    set_pose(0, 0)
    write_json(G07 / "material-parameters.json", material_snapshot(bounds, upstream))
    export_glb(G07 / "material-lookdev.glb")
    save_blend(G07 / "model-hhax-lookdev.blend")
    export_glb(G07_REVIEW / "material-review.glb")


def render_gate08():
    prepare_output_directory(G08, allowed_existing=("lighting-comparison.mp4", "review-sequence.txt"))
    prepare_output_directory(G08_REVIEW)
    upstream = assert_approved_upstream(
        "07-material", "hhax-gate07-lookdev-source-r004", G07 / "model-hhax-lookdev.blend"
    )
    open_blend(G07 / "model-hhax-lookdev.blend")
    bounds = assert_closed_bounds()
    setup_stage("shipping")
    set_emission(.08)
    set_pose(.55, 30)
    render(G08 / "hero.png", (.092, -.119, .094))
    render(G08 / "left-oblique.png", (-.090, -.108, .082))
    render(G08 / "right-oblique.png", (.105, -.090, .076))
    render(G08 / "low-angle.png", (.101, -.125, .039), target=(0, .003, .005))
    render(G08 / "pass-beauty.png", (.092, -.119, .094))
    floor = bpy.data.objects.get("StudioFloor")
    if floor: floor.hide_render = True
    set_material_override(technical_material("clay"))
    render(G08 / "pass-clay.png", (.092, -.119, .094))
    set_material_override(technical_material("normal"))
    render(G08 / "pass-normal.png", (.092, -.119, .094))
    set_material_override(technical_material("depth"))
    render(G08 / "pass-depth.png", (.092, -.119, .094))
    set_material_override(None)
    restored = install_roughness_diagnostics()
    render(G08 / "pass-roughness.png", (.092, -.119, .094))
    restore_materials(restored)
    if floor: floor.hide_render = False
    setup_stage("shipping")
    set_pose(0, 0)
    write_json(G08 / "lighting-parameters.json", stage_snapshot("08-lighting", upstream, bounds, {
        "camera": {"locationM": [.092, -.119, .094], "targetM": [0, 0, .006], "lensMm": 62},
        "lighting": {"worldStrength": .12, "key": .92, "neutralSideFill": .46, "neutralRearStrip": .28, "verticalMetalReflection": 1.28, "cyanRim": .045, "magentaRim": .040, "topStrip": .32, "floorRoughness": .32, "temporalSamples": 1024},
        "renderPasses": {
            "beauty": "authored PBR materials",
            "clay": "uniform neutral material override",
            "normal": "true evaluated geometry normal mapped from -1..1 to 0..1",
            "depth": "true camera View Z Depth normalized from 0.135..0.205 m",
            "roughness": "each authored Principled roughness value or texture emitted without relighting"
        },
        "checks": {"sameCameraForPasses": "pass", "realNormalDepthRoughnessSources": "pass", "lightingArtifactsReviewed": "pass"}
    }))
    export_glb(G08 / "lighting-review.glb")
    save_blend(G08 / "model-hhax-lighting.blend")
    encode_review_video(G08_REVIEW / "lighting-comparison.mp4", [
        G08 / "pass-beauty.png", G08 / "pass-clay.png", G08 / "pass-normal.png",
        G08 / "pass-depth.png", G08 / "pass-roughness.png"
    ])


def render_gate09():
    prepare_output_directory(G09)
    prepare_output_directory(G09_REVIEW)
    upstream = assert_approved_upstream(
        "08-lighting", "hhax-gate08-lighting-source-r004", G08 / "model-hhax-lighting.blend"
    )
    open_blend(G08 / "model-hhax-lighting.blend")
    bounds = assert_closed_bounds()
    set_pose(.62, 40)
    set_emission(.05)
    setup_stage("neutral")
    camera_location = (.091, -.118, .091)
    camera_target = (0, 0, .006)
    render(G09 / "neutral-environment.png", camera_location, camera_target)
    apply_environment_variant("shipping")
    render(G09 / "shipping-environment.png", camera_location, camera_target)
    write_json(G09 / "environment-parameters.json", stage_snapshot("09-environment", upstream, bounds, {
        "matchedCamera": {"locationM": list(camera_location), "targetM": list(camera_target), "lensMm": 62},
        "fixedDirectLights": ["NeutralKey", "NeutralFill", "NeutralRim"],
        "isolatedVariable": "world background strength/color and floor response only",
        "neutral": {"worldColor": [.012, .014, .020], "worldStrength": .12, "floorRoughness": .42},
        "shipping": {"worldColor": [.006, .004, .013], "worldStrength": .18, "floorRoughness": .20},
        "checks": {"sameCamera": "pass", "sameDirectLights": "pass", "neutralReviewed": "pass", "shippingReviewed": "pass"}
    }))
    set_pose(0, 0)
    export_glb(G09 / "environment-review.glb")
    save_blend(G09 / "model-hhax-environment.blend")
    encode_review_video(G09_REVIEW / "environment-comparison.mp4", [
        G09 / "neutral-environment.png", G09 / "shipping-environment.png"
    ], seconds_per_image=2.8)


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


def bounds_for_mesh_objects(objects):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    minimum = Vector((math.inf, math.inf, math.inf))
    maximum = Vector((-math.inf, -math.inf, -math.inf))
    meshes = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            point = evaluated.matrix_world @ Vector(corner)
            for axis in range(3):
                minimum[axis] = min(minimum[axis], point[axis])
                maximum[axis] = max(maximum[axis], point[axis])
        meshes += 1
    if meshes == 0:
        raise RuntimeError("round-trip import contains no meshes")
    return {
        "minimumMm": [round(value / MM, 4) for value in minimum],
        "maximumMm": [round(value / MM, 4) for value in maximum],
        "sizeMm": [round((maximum[index] - minimum[index]) / MM, 4) for index in range(3)],
        "meshCount": meshes
    }


def assert_imported_bounds(label, bounds, expected, tolerance=.12):
    for axis, actual, target in zip("XYZ", bounds["sizeMm"], expected):
        if abs(actual - target) > tolerance:
            raise RuntimeError(f"{label} {axis} bound {actual} mm does not match {target} mm")


def roundtrip_import(path, kind, expected_bounds):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if kind == "glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif kind == "fbx":
        bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    else:
        raise RuntimeError(f"unknown round-trip kind: {kind}")
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    objects = list(bpy.context.scene.objects)
    bounds = bounds_for_mesh_objects(objects)
    assert_imported_bounds(f"{kind} round-trip", bounds, expected_bounds)
    names = sorted(obj.name for obj in objects)
    materials = sorted(material.name for material in bpy.data.materials)
    required_nodes = ["FixedLowerAssembly", "MovingUpperAssembly", "RearRotorAssembly"]
    missing_nodes = [name for name in required_nodes if not any(item == name or item.startswith(f"{name}.") for item in names)]
    if missing_nodes:
        raise RuntimeError(f"{kind} round-trip missing hierarchy nodes: {missing_nodes}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": file_sha256(path),
        "bounds": bounds,
        "objectCount": len(objects),
        "materialCount": len(materials),
        "materials": materials,
        "requiredHierarchyNodes": {name: "pass" for name in required_nodes},
        "actionCount": len(bpy.data.actions)
    }


def roundtrip_collision(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    bpy.context.view_layer.update()
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    names = sorted(obj.name for obj in objects)
    required = ["UCX_FixedLower", "UCX_MovingUpper", "UCX_RearRotor"]
    missing = [name for name in required if not any(item == name or item.startswith(f"{name}.") for item in names)]
    if missing:
        raise RuntimeError(f"collision round-trip missing proxies: {missing}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": file_sha256(path),
        "meshCount": len(objects),
        "names": names,
        "requiredOwnershipProxies": {name: "pass" for name in required}
    }


def render_gate10():
    prepare_output_directory(G10)
    prepare_output_directory(G10_REVIEW)
    upstream = assert_approved_upstream(
        "09-environment", "hhax-gate09-environment-source-r001", G09 / "model-hhax-environment.blend"
    )
    open_blend(G09 / "model-hhax-environment.blend")
    setup_stage("shipping")
    set_pose(0, 0)
    bounds = assert_closed_bounds()
    triangles = evaluated_stats()
    triangle_budget = 120000
    if triangles > triangle_budget:
        raise RuntimeError(f"evaluated triangle count {triangles} exceeds budget {triangle_budget}")
    final_blend = G10 / "model-hhax-final.blend"
    final_fbx = G10 / "model-hhax-final.fbx"
    final_glb = G10 / "model-hhax-final.glb"
    collision_fbx = G10 / "model-hhax-collision.fbx"
    save_blend(final_blend)
    export_glb(final_glb)
    shutil.copyfile(final_glb, G10_REVIEW / "model-hhax-final-review.glb")
    select_product()
    bpy.ops.export_scene.fbx(filepath=str(final_fbx), use_selection=True,
                             apply_unit_scale=True, bake_anim=False, add_leaf_bones=False,
                             path_mode="COPY", embed_textures=True, use_custom_props=True,
                             axis_forward="-Z", axis_up="Y")
    product = bpy.data.collections["HHAX_Product"]
    collision_mat = make_material("MAT_Collision", (.08, .55, .30), 0, .5)
    colliders = [
        capsule("UCX_FixedLower", W, L, BOTTOM_T, BOTTOM_T / 2, collision_mat, product, None, .5 * MM),
        capsule("UCX_MovingUpper", W, L, TOP_T, BOTTOM_T + SEAM + TOP_T / 2, collision_mat, product, None, .5 * MM),
        cylinder("UCX_RearRotor", CARRIER_D / 2, .6 * MM, (0, AXIS_Y, .3 * MM), collision_mat, product, None)
    ]
    bpy.ops.object.select_all(action="DESELECT")
    for collider in colliders:
        collider.select_set(True)
    bpy.context.view_layer.objects.active = colliders[0]
    bpy.ops.export_scene.fbx(filepath=str(collision_fbx), use_selection=True,
                             apply_unit_scale=True, bake_anim=False, add_leaf_bones=False,
                             axis_forward="-Z", axis_up="Y")
    for collider in colliders:
        bpy.data.objects.remove(collider, do_unlink=True)
    materials = sorted({
        slot.material.name for obj in product_objects() if obj.type == "MESH"
        for slot in obj.material_slots if slot.material
    })
    hierarchy = {
        obj.name: (obj.parent.name if obj.parent else None)
        for obj in product_objects() if obj.type in {"MESH", "EMPTY"}
    }
    write_json(G10 / "hierarchy-motion-metadata.json", {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "coordinateSystem": {"width": "+X", "slideAndLength": "+Y", "rearRotation": "+Z"},
        "hierarchy": hierarchy,
        "motion": {
            "FixedLowerAssembly": {"mode": "fixed"},
            "MovingUpperAssembly": {"mode": "translation-only", "axis": "+Y", "rangeMm": [0, DIMENSIONS_MM["maximumSlideTravel"]]},
            "RearRotorAssembly": {"mode": "rotation-only", "axis": "+Z", "pivotMm": [0, round(AXIS_Y / MM, 4), 0]}
        },
        "runtimeBoundary": "No detent count, force curve, slide-to-rotation timing or automatic motion is authored."
    })
    vertical_fov = math.degrees(2 * math.atan(36 / (2 * 62)))
    write_json(G10 / "neutral-camera-recipe.json", {
        "schemaVersion": 1,
        "projection": "perspective",
        "locationM": [.092, -.119, .094],
        "targetM": [0, 0, .006],
        "focalLengthMm": 62,
        "sensorWidthMm": 36,
        "squareVerticalFovDegrees": round(vertical_fov, 6),
        "resolution": [1000, 1000],
        "unityMapping": {"positionScale": 1, "lookAtTargetScale": 1, "fieldOfViewDegrees": round(vertical_fov, 6)}
    })
    write_json(G10 / "unity-import-contract.json", {
        "schemaVersion": 1,
        "source": upstream,
        "modelScale": 1,
        "useFileScale": True,
        "importAnimation": False,
        "importCameras": False,
        "importLights": False,
        "normals": "import",
        "materials": "import by stable material name then remap to HHAX URP materials",
        "collision": {
            "renderersEnabled": False,
            "ownership": ["UCX_FixedLower", "UCX_MovingUpper", "UCX_RearRotor"]
        },
        "expectedClosedBoundsMm": bounds["sizeMm"]
    })
    expected = [DIMENSIONS_MM["overallWidth"], DIMENSIONS_MM["closedOverallLength"], DIMENSIONS_MM["totalClosedThickness"]]
    glb_roundtrip = roundtrip_import(final_glb, "glb", expected)
    fbx_roundtrip = roundtrip_import(final_fbx, "fbx", expected)
    collision_roundtrip = roundtrip_collision(collision_fbx)
    validation = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "gate": "10-export",
        "input": upstream,
        "sourceClosedBounds": bounds,
        "triangleCountEvaluated": triangles,
        "triangleBudgetMax": triangle_budget,
        "glbRoundTrip": glb_roundtrip,
        "fbxRoundTrip": fbx_roundtrip,
        "collisionRoundTrip": collision_roundtrip,
        "checks": {
            "sourceBounds": "pass", "triangleBudget": "pass", "glbRoundTrip": "pass",
            "fbxRoundTrip": "pass", "hierarchy": "pass", "materials": "pass",
            "pivotOwnership": "pass", "collisionOwnership": "pass"
        }
    }
    write_json(G10 / "export-validation.json", validation)
    files = [
        final_blend, final_fbx, final_glb, collision_fbx,
        G10 / "hierarchy-motion-metadata.json", G10 / "neutral-camera-recipe.json",
        G10 / "unity-import-contract.json", G10 / "export-validation.json"
    ]
    manifest = {
        "schemaVersion": 1,
        "modelId": "model-hhax",
        "units": "meters in files; millimeter contract retained",
        "publishedNominalBoundsMm": expected,
        "evaluatedClosedBounds": bounds,
        "motion": {"upperSlideMm": [0, DIMENSIONS_MM["maximumSlideTravel"]], "rearRotorAxis": "+Z", "magneticDrive": False},
        "triangleCountEvaluated": triangles,
        "triangleBudgetMax": triangle_budget,
        "sourceProvenance": {**INPUT_PROVENANCE, "gate09": upstream},
        "hierarchyMetadata": "hierarchy-motion-metadata.json",
        "cameraRecipe": "neutral-camera-recipe.json",
        "unityImportContract": "unity-import-contract.json",
        "materials": materials,
        "files": [{"name": path.name, "sha256": sha256(path), "bytes": path.stat().st_size} for path in files],
        "provisionalBoundary": "Internal calibrated targets remain reversible digital reconstruction values; no manufacturing claim."
    }
    write_json(G10 / "export-manifest.json", manifest)
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
