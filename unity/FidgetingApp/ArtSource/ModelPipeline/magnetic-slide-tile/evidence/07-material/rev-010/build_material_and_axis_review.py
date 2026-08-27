#!/usr/bin/env python3
"""Build Gate 07 rev 10 material and detent-aligned axis evidence."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


OUT = Path(__file__).resolve().parent
REPO = OUT.parents[7]
REV9 = OUT.parent / "rev-009"
REV7 = OUT.parent / "rev-007"
SOURCE_BLEND = REV9 / "magnetic-slide-tile-material-r009.blend"
REV9_BUILDER = REV9 / "build_original_authority_material.py"
UPPER_MASK = REV7 / "artwork-upper-mask.png"
LOWER_MASK = OUT / "artwork-lower-mask-r010.png"
BORDER_MASK = REV7 / "artwork-top-perimeter-border-mask.png"
LOWER_REPORT = OUT / "lower-artwork-provenance.json"
OUTPUT_BLEND = OUT / "magnetic-slide-tile-material-r010.blend"
EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
AXIS_WORLD_MM = Vector((0.0, -9.5, 0.0))
SPIN_ANGLES = [0, 12, 36]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_rev9_builder():
    spec = importlib.util.spec_from_file_location("gate07_rev9_builder", REV9_BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUTPUT = OUT
    module.UPPER_MASK = UPPER_MASK
    module.LOWER_MASK = LOWER_MASK
    module.BORDER_MASK = BORDER_MASK
    module.RECIPE = copy.deepcopy(module.RECIPE)
    module.RECIPE["crystal"].update({
        "roughnessMinMax": [0.022, 0.11],
        "coatWeight": 0.48,
        "coatRoughness": 0.035,
        "transmissionMinMax": [0.05, 0.30],
        "mosaicScale": 24.0,
        "mosaicDetailScale": 120.0,
        "mosaicBumpStrength": 0.22,
        "mosaicBumpDistanceMm": 0.024,
        "iridescenceMix": 0.08,
        "microflakeScale": 85.0,
        "microflakeThreshold": [0.72, 0.79],
        "microflakeColorLinear": [1.0, 0.22, 0.28, 1.0],
        "microflakeMix": 0.70,
        "microflakeBumpStrength": 0.11,
        "microflakeBumpDistanceMm": 0.006,
        "granularVariationScale": 28.0,
        "granularVariationMix": 0.68,
    })
    return module


def geometry_digest(objects):
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(obj.name.encode())
        for row in obj.matrix_world:
            for value in row:
                digest.update(f"{value:.12f}".encode())
        for vertex in mesh.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in mesh.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def set_input(node, name, value):
    for socket in node.inputs:
        if socket.name == name:
            socket.default_value = value
            return socket
    return None


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens, camera_id):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["camera_id"] = camera_id
    obj["recipe"] = "Gate07Rev10-neutral-material-axis-review"
    return obj


def enhance_crystal(material, slot_name):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
    texcoord = next(node for node in nodes if node.type == "TEX_COORD")
    generated = texcoord.outputs["Generated"]
    existing_color_link = next(link for link in links if link.to_node == bsdf and link.to_socket.name == "Base Color")
    existing_color = existing_color_link.from_socket
    links.remove(existing_color_link)

    granular = nodes.new("ShaderNodeTexNoise")
    granular.name = f"R10_{slot_name}_GranularRuby"
    granular.noise_dimensions = "3D"
    granular.inputs["Scale"].default_value = 28.0
    granular.inputs["Detail"].default_value = 6.0
    granular.inputs["Roughness"].default_value = 0.72
    granular.inputs["Distortion"].default_value = 0.33
    links.new(generated, granular.inputs["Vector"])
    granular_color = nodes.new("ShaderNodeValToRGB")
    granular_color.name = f"R10_{slot_name}_GranularRubyRamp"
    granular_color.color_ramp.elements.remove(granular_color.color_ramp.elements[1])
    granular_stops = [
        (0.0, (0.004, 0.00005, 0.0002, 1)),
        (0.26, (0.035, 0.0005, 0.002, 1)),
        (0.48, (0.20, 0.003, 0.010, 1)),
        (0.68, (0.92, 0.028, 0.045, 1)),
        (0.84, (0.075, 0.008, 0.040, 1)),
        (1.0, (0.018, 0.085, 0.12, 1)),
    ]
    first = granular_color.color_ramp.elements[0]
    first.position, first.color = granular_stops[0]
    for position, color in granular_stops[1:]:
        item = granular_color.color_ramp.elements.new(position)
        item.color = color
    links.new(granular.outputs["Fac"], granular_color.inputs["Fac"])
    granular_mix = nodes.new("ShaderNodeMixRGB")
    granular_mix.name = f"R10_{slot_name}_GranularMix"
    granular_mix.blend_type = "SOFT_LIGHT"
    granular_mix.inputs[0].default_value = 0.68
    links.new(existing_color, granular_mix.inputs[1])
    links.new(granular_color.outputs["Color"], granular_mix.inputs[2])

    flake_noise = nodes.new("ShaderNodeTexNoise")
    flake_noise.name = f"R10_{slot_name}_MicroflakeNoise"
    flake_noise.noise_dimensions = "3D"
    flake_noise.inputs["Scale"].default_value = 85.0
    flake_noise.inputs["Detail"].default_value = 2.0
    flake_noise.inputs["Roughness"].default_value = 0.46
    links.new(generated, flake_noise.inputs["Vector"])
    flake_ramp = nodes.new("ShaderNodeValToRGB")
    flake_ramp.name = f"R10_{slot_name}_MicroflakeDistribution"
    flake_ramp.color_ramp.elements[0].position = 0.72
    flake_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    flake_ramp.color_ramp.elements[1].position = 0.79
    flake_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(flake_noise.outputs["Fac"], flake_ramp.inputs["Fac"])

    motif_node = nodes.get(f"{slot_name}_MotifMask")
    border_node = nodes.get(f"{slot_name}_PerimeterMask")
    occupied = nodes.new("ShaderNodeMath")
    occupied.name = f"R10_{slot_name}_MotifPerimeterMaximum"
    occupied.operation = "MAXIMUM"
    links.new(motif_node.outputs["Color"], occupied.inputs[0])
    links.new(border_node.outputs["Color"], occupied.inputs[1])
    clear_region = nodes.new("ShaderNodeMath")
    clear_region.name = f"R10_{slot_name}_ClearCrystalRegion"
    clear_region.operation = "SUBTRACT"
    clear_region.inputs[0].default_value = 1.0
    links.new(occupied.outputs[0], clear_region.inputs[1])
    flake_factor = nodes.new("ShaderNodeMath")
    flake_factor.name = f"R10_{slot_name}_MicroflakeClearFactor"
    flake_factor.operation = "MULTIPLY"
    links.new(flake_ramp.outputs["Color"], flake_factor.inputs[0])
    links.new(clear_region.outputs[0], flake_factor.inputs[1])
    flake_strength = nodes.new("ShaderNodeMath")
    flake_strength.operation = "MULTIPLY"
    flake_strength.inputs[1].default_value = 0.70
    links.new(flake_factor.outputs[0], flake_strength.inputs[0])

    flake_mix = nodes.new("ShaderNodeMixRGB")
    flake_mix.name = f"R10_{slot_name}_ReflectiveMicroflakes"
    flake_mix.blend_type = "SCREEN"
    links.new(flake_strength.outputs[0], flake_mix.inputs[0])
    links.new(granular_mix.outputs["Color"], flake_mix.inputs[1])
    flake_mix.inputs[2].default_value = (1.0, 0.22, 0.28, 1)
    links.new(flake_mix.outputs["Color"], bsdf.inputs["Base Color"])

    existing_roughness_link = next(link for link in links if link.to_node == bsdf and link.to_socket.name == "Roughness")
    existing_roughness = existing_roughness_link.from_socket
    links.remove(existing_roughness_link)
    rough_variation = nodes.new("ShaderNodeMapRange")
    rough_variation.name = f"R10_{slot_name}_RoughnessVariation"
    rough_variation.inputs["From Min"].default_value = 0.0
    rough_variation.inputs["From Max"].default_value = 1.0
    rough_variation.inputs["To Min"].default_value = 0.022
    rough_variation.inputs["To Max"].default_value = 0.11
    links.new(granular.outputs["Fac"], rough_variation.inputs["Value"])
    rough_mix = nodes.new("ShaderNodeMix")
    rough_mix.name = f"R10_{slot_name}_LayeredRoughness"
    rough_mix.data_type = "FLOAT"
    rough_mix.inputs["Factor"].default_value = 0.52
    links.new(existing_roughness, rough_mix.inputs[2])
    links.new(rough_variation.outputs["Result"], rough_mix.inputs[3])
    flake_roughness = nodes.new("ShaderNodeMix")
    flake_roughness.name = f"R10_{slot_name}_MicroflakeRoughness"
    flake_roughness.data_type = "FLOAT"
    links.new(flake_factor.outputs[0], flake_roughness.inputs["Factor"])
    links.new(rough_mix.outputs["Result"], flake_roughness.inputs[2])
    flake_roughness.inputs[3].default_value = 0.005
    links.new(flake_roughness.outputs["Result"], bsdf.inputs["Roughness"])

    existing_normal_link = next(link for link in links if link.to_node == bsdf and link.to_socket.name == "Normal")
    existing_normal = existing_normal_link.from_socket
    links.remove(existing_normal_link)
    flake_bump = nodes.new("ShaderNodeBump")
    flake_bump.name = f"R10_{slot_name}_MicroflakeBump"
    flake_bump.inputs["Strength"].default_value = 0.11
    flake_bump.inputs["Distance"].default_value = 0.006
    links.new(flake_factor.outputs[0], flake_bump.inputs["Height"])
    links.new(existing_normal, flake_bump.inputs["Normal"])
    links.new(flake_bump.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, "Coat Weight", 0.48)
    set_input(bsdf, "Coat Roughness", 0.035)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    material["gate07_revision"] = 10
    material["microflakeScale"] = 85.0
    material["microflakeThreshold"] = [0.72, 0.79]
    material["microflakeMix"] = 0.70
    material["granularVariationScale"] = 28.0
    material["granularVariationMix"] = 0.68
    material["emissionEnabled"] = False


def render(scene, cam, filename, width=1600, height=1200):
    scene.camera = cam
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def projected_pixel(scene, camera_obj, point, width, height):
    ndc = world_to_camera_view(scene, camera_obj, Vector(point))
    return [round(float(ndc.x * width), 3), round(float((1.0 - ndc.y) * height), 3)]


def main():
    for path in [SOURCE_BLEND, REV9_BUILDER, UPPER_MASK, LOWER_MASK, BORDER_MASK, LOWER_REPORT]:
        if not path.exists():
            raise FileNotFoundError(path)
    lower_provenance = json.loads(LOWER_REPORT.read_text(encoding="utf-8"))
    if not lower_provenance["pass"] or not lower_provenance["mask"]["hashesDistinct"]:
        raise RuntimeError("Lower artwork provenance is not valid.")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    rev9 = load_rev9_builder()
    scene = bpy.context.scene
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    translation = bpy.data.objects["UpperTranslation"]
    model = [lower, upper]
    before = geometry_digest(model)
    if before != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError(f"Unexpected geometry digest {before}")
    base_matrices = {obj.name: [list(row) for row in obj.matrix_world] for obj in model}

    upper_surface = rev9.crystal_material(
        "M07R10_OriginalAuthority_Crystal_Upper", "Artwork_Upper", UPPER_MASK)
    lower_surface = rev9.crystal_material(
        "M07R10_OriginalAuthority_Crystal_LowerDistinct", "Artwork_Lower", LOWER_MASK)
    enhance_crystal(upper_surface, "Artwork_Upper")
    enhance_crystal(lower_surface, "Artwork_Lower")
    silver = bpy.data.materials["M07R9_OriginalAuthority_PolishedSilver"]
    assignments = rev9.assign_materials(lower, upper, silver, lower_surface, upper_surface)

    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 6504
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 10

    cameras = {
        "front": camera("R10_Front", (0, -88, 128), (0, 0, 2.5), 88, "front-source-oriented"),
        "oblique": camera("R10_Oblique", (68, -94, 66), (0, 0, 4.0), 94, "material-oblique"),
        "side": camera("R10_SideRim", (82, -84, 30), (7, 0, 0), 112, "side-rim"),
        "open": camera("R10_Open", (0, -112, 116), (0, 8, 2.5), 86, "open-front"),
        "lower": camera("R10_LowerMacro", (4, -104, 82), (0, -11, 3.0), 106, "lower-artwork-macro"),
        "microflake": camera("R10_MicroflakeMacro", (20, -63, 70), (0, 0, 5.8), 132, "crystal-microflake-macro"),
        "spin": camera("R10_SpinEvidence", (0, -102, 126), (0, 0, 2.5), 92, "point-axis-spin"),
    }

    render(scene, cameras["front"], "upper-front.png")
    render(scene, cameras["oblique"], "oblique-crystal.png")
    render(scene, cameras["side"], "side-rim.png")
    render(scene, cameras["microflake"], "crystal-microflake-macro.png", 1800, 1300)

    translation.location = (0, 0, 0)
    pivot.rotation_euler = (0, 0, 0)
    pivot_world_reference = pivot.matrix_world.translation.copy()
    spin_records = []
    for angle in SPIN_ANGLES:
        pivot.rotation_euler.z = math.radians(angle)
        bpy.context.view_layer.update()
        pivot_world = pivot.matrix_world.translation.copy()
        translation_world = translation.matrix_world.translation.copy()
        drift = (pivot_world - pivot_world_reference).length
        if drift > 1e-9 or translation_world.length > 1e-9:
            raise RuntimeError(f"Spin {angle}° drifted: pivot={drift}, translation={translation_world[:]}")
        filename = f"spin-{angle:02d}deg.png"
        render(scene, cameras["spin"], filename)
        spin_records.append({
            "angleDeg": angle,
            "detentIndex": angle // 12,
            "pivotWorldMm": list(pivot_world),
            "pivotDriftMm": drift,
            "translationWorldMm": list(translation_world),
            "translationMagnitudeMm": translation_world.length,
            "axisDirection": "+Z",
            "axisPixel": projected_pixel(scene, cameras["spin"], pivot_world, 1600, 1200),
            "render": filename,
        })

    pivot.rotation_euler = (0, 0, 0)
    translation.location = (0, 21, 0)
    bpy.context.view_layer.update()
    render(scene, cameras["open"], "slide-open-21mm-0deg.png", 1600, 1300)
    render(scene, cameras["lower"], "lower-open-macro.png", 1800, 1300)
    slide_record = {
        "translationLocalMm": list(translation.location),
        "rotationDeg": 0,
        "pivotWorldMm": list(pivot.matrix_world.translation),
        "upperRotationDeg": math.degrees(pivot.rotation_euler.z),
        "render": "slide-open-21mm-0deg.png",
    }

    translation.location = (0, 0, 0)
    pivot.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()
    after = geometry_digest(model)
    matrices_after = {obj.name: [list(row) for row in obj.matrix_world] for obj in model}
    if after != before or matrices_after != base_matrices:
        raise RuntimeError("Base-pose geometry or matrices changed.")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    recipe = copy.deepcopy(rev9.RECIPE)
    recipe["lowerArtwork"] = {
        "upperMaskSha256": sha256(UPPER_MASK),
        "lowerMaskSha256": sha256(LOWER_MASK),
        "hashesDistinct": sha256(UPPER_MASK) != sha256(LOWER_MASK),
        "directTraceRegionY": lower_provenance["directTrace"]["targetRegionY"],
        "reconstructedRegionY": lower_provenance["reconstruction"]["targetRegionY"],
        "reconstructionClaim": lower_provenance["reconstruction"]["claim"],
    }
    recipe["motionEvidence"] = {
        "axisPointWorldMm": list(AXIS_WORLD_MM),
        "axisDirection": "+Z",
        "spinAnglesDeg": SPIN_ANGLES,
        "detentIndices": [0, 1, 3],
        "detentEquation": "360° / 12° = 30",
        "slidePose": {"translationMm": [0, 21, 0], "rotationDeg": 0},
        "primaryAngleDeg": 12,
        "fortyFiveDegreePrimaryPoseUsed": False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 10,
        "sourceBlend": str(SOURCE_BLEND.relative_to(REPO)),
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO)),
        "sourceAssetIds": [
            "slider-intake-obs-frame-01",
            "slider-intake-obs-frame-03",
            "slider-intake-obs-frame-05",
            "slider-intake-obs-frame-10",
            "slider-intake-haloo-official-08",
        ],
        "geometry": {
            "digestBefore": before,
            "digestAfter": after,
            "expectedDigest": EXPECTED_GEOMETRY_DIGEST,
            "unchanged": before == after == EXPECTED_GEOMETRY_DIGEST,
            "matricesUnchanged": matrices_after == base_matrices,
            "assignments": assignments,
        },
        "artwork": lower_provenance,
        "motionEvidence": {
            "axisPointWorldMm": list(AXIS_WORLD_MM),
            "axisDirection": "+Z",
            "spin": spin_records,
            "slide": slide_record,
            "detentEquation": "360° / 12° = 30",
            "allSpinAnglesDetentAligned": all(record["angleDeg"] % 12 == 0 for record in spin_records),
            "allSpinTranslationsZero": all(record["translationMagnitudeMm"] == 0 for record in spin_records),
            "allPivotDriftZero": all(record["pivotDriftMm"] == 0 for record in spin_records),
            "fortyFiveDegreePrimaryPoseUsed": False,
        },
        "recipe": recipe,
        "render": {
            "engine": scene.render.engine,
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": scene.view_settings.exposure,
            "whiteBalanceKelvin": getattr(scene.view_settings, "white_balance_temperature", 6504),
            "whiteBalanceTint": getattr(scene.view_settings, "white_balance_tint", 10),
            "emission": 0.0,
            "bloom": False,
            "cameras": {
                key: {
                    "location": list(cam.location),
                    "rotationEuler": list(cam.rotation_euler),
                    "lensMm": cam.data.lens,
                    "cameraId": cam["camera_id"],
                    "recipe": cam["recipe"],
                } for key, cam in cameras.items()
            },
        },
        "pass": True,
    }
    (OUT / "material-axis-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "material-recipe-r010.json").write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
