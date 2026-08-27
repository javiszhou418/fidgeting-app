#!/usr/bin/env python3
"""Build Gate 07 rev 9 from original appearance references."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
REPO = OUTPUT.parents[7]
SOURCE_BLEND = OUTPUT.parent / "rev-007/magnetic-slide-tile-material-r007.blend"
OUTPUT_BLEND = OUTPUT / "magnetic-slide-tile-material-r009.blend"
UPPER_MASK = OUTPUT.parent / "rev-007/artwork-upper-mask.png"
LOWER_MASK = OUTPUT.parent / "rev-007/artwork-lower-mask.png"
BORDER_MASK = OUTPUT.parent / "rev-007/artwork-top-perimeter-border-mask.png"
EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
SOURCE_ASSETS = [
    "slider-intake-obs-frame-01",
    "slider-intake-obs-frame-05",
    "slider-intake-obs-frame-10",
    "slider-intake-haloo-official-03",
    "slider-intake-haloo-official-04",
    "slider-intake-haloo-official-06",
    "slider-intake-haloo-official-08",
]
RECIPE = {
    "silver": {
        "baseColorLinear": [0.78, 0.77, 0.74, 1.0],
        "metallic": 1.0,
        "roughness": 0.075,
        "anisotropy": 0.16,
        "anisotropyRotation": 0.08,
        "coatWeight": 0.08,
        "coatRoughness": 0.018,
        "microScratchScale": 520.0,
        "microScratchStrength": 0.012,
        "emission": 0.0,
    },
    "crystal": {
        "deepBloodRedLinear": [0.18, 0.003, 0.008, 1.0],
        "darkRubyLinear": [0.018, 0.00025, 0.0008, 1.0],
        "highlightRubyLinear": [0.72, 0.025, 0.045, 1.0],
        "roughnessMinMax": [0.028, 0.085],
        "ior": 1.52,
        "coatWeight": 0.35,
        "coatRoughness": 0.05,
        "transmissionMinMax": [0.07, 0.24],
        "thinFilmIor": 1.38,
        "thinFilmThicknessNm": [365.0, 455.0],
        "mosaicScale": 18.0,
        "mosaicDetailScale": 74.0,
        "mosaicBumpStrength": 0.18,
        "mosaicBumpDistanceMm": 0.018,
        "motifBumpStrength": 0.16,
        "motifDepthMm": 0.045,
        "iridescenceMix": 0.10,
        "emission": 0.0,
    },
    "motif": {
        "baseColorLinear": [0.004, 0.0015, 0.0018, 1.0],
        "metallic": 0.42,
        "roughness": 0.16,
        "coatWeight": 0.35,
    },
    "perimeter": {
        "baseColorLinear": [0.018, 0.020, 0.024, 1.0],
        "metallic": 0.24,
        "roughness": 0.18,
        "coatWeight": 0.55,
        "borderMaskWidthPx": 64,
        "outerInsetPx": 0,
    },
    "colorManagement": {
        "viewTransform": "AgX",
        "look": "AgX - Medium High Contrast",
        "exposureEv": 0.0,
        "gamma": 1.0,
        "whiteBalanceKelvin": 6504,
        "whiteBalanceTint": 10,
    },
    "chemistryClaim": "unknown; visual approximation only",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def set_input(node, name, value):
    for socket in node.inputs:
        if socket.name == name:
            socket.default_value = value
            return socket
    return None


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


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def clear_previous_presentation(keep):
    for obj in list(bpy.data.objects):
        if obj in keep:
            continue
        if obj.type in {"LIGHT", "CAMERA", "FONT"} or obj.get("gate07_review_sample") or obj.get("gate07_calibrated_reflection_card"):
            bpy.data.objects.remove(obj, do_unlink=True)


def image_node(nodes, path, name):
    node = nodes.new("ShaderNodeTexImage")
    node.name = name
    node.image = bpy.data.images.load(str(path), check_existing=True)
    node.image.colorspace_settings.name = "Non-Color"
    node.interpolation = "Closest"
    node.extension = "CLIP"
    return node


def silver_material():
    mat = bpy.data.materials.new("M07R9_OriginalAuthority_PolishedSilver")
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    values = RECIPE["silver"]
    set_input(bsdf, "Base Color", values["baseColorLinear"])
    set_input(bsdf, "Metallic", values["metallic"])
    set_input(bsdf, "Roughness", values["roughness"])
    set_input(bsdf, "Anisotropic", values["anisotropy"])
    set_input(bsdf, "Anisotropic Rotation", values["anisotropyRotation"])
    set_input(bsdf, "Coat Weight", values["coatWeight"])
    set_input(bsdf, "Coat Roughness", values["coatRoughness"])
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    tex = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 64.0, 1.0)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = values["microScratchScale"]
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = values["microScratchStrength"]
    bump.inputs["Distance"].default_value = 0.003
    links.new(tex.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    mat["gate07_revision"] = 9
    mat["appearanceAuthority"] = "original-user-and-exact-product-references"
    mat["emissionEnabled"] = False
    return mat


def crystal_material(name, slot_name, motif_path):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = "DITHERED"
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    tex = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    links.new(tex.outputs["Generated"], mapping.inputs["Vector"])

    motif = image_node(nodes, motif_path, f"{slot_name}_MotifMask")
    border = image_node(nodes, BORDER_MASK, f"{slot_name}_PerimeterMask")
    links.new(mapping.outputs["Vector"], motif.inputs["Vector"])
    links.new(mapping.outputs["Vector"], border.inputs["Vector"])

    voronoi = nodes.new("ShaderNodeTexVoronoi")
    voronoi.voronoi_dimensions = "3D"
    voronoi.feature = "DISTANCE_TO_EDGE"
    voronoi.distance = "EUCLIDEAN"
    voronoi.inputs["Scale"].default_value = RECIPE["crystal"]["mosaicScale"]
    links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])
    edge_ramp = nodes.new("ShaderNodeValToRGB")
    edge_ramp.color_ramp.elements[0].position = 0.012
    edge_ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.02, 1)
    edge_ramp.color_ramp.elements[1].position = 0.095
    edge_ramp.color_ramp.elements[1].color = (0.94, 0.94, 0.94, 1)
    links.new(voronoi.outputs["Distance"], edge_ramp.inputs["Fac"])

    macro = nodes.new("ShaderNodeTexNoise")
    macro.noise_dimensions = "3D"
    macro.inputs["Scale"].default_value = 3.6
    macro.inputs["Detail"].default_value = 5.5
    macro.inputs["Roughness"].default_value = 0.72
    macro.inputs["Distortion"].default_value = 0.28
    links.new(mapping.outputs["Vector"], macro.inputs["Vector"])
    detail = nodes.new("ShaderNodeTexNoise")
    detail.inputs["Scale"].default_value = RECIPE["crystal"]["mosaicDetailScale"]
    detail.inputs["Detail"].default_value = 3.2
    detail.inputs["Roughness"].default_value = 0.58
    links.new(mapping.outputs["Vector"], detail.inputs["Vector"])
    multiply = nodes.new("ShaderNodeMath")
    multiply.operation = "MULTIPLY"
    links.new(macro.outputs["Fac"], multiply.inputs[0])
    links.new(edge_ramp.outputs["Color"], multiply.inputs[1])

    color = nodes.new("ShaderNodeValToRGB")
    color.color_ramp.elements.remove(color.color_ramp.elements[1])
    stops = [
        (0.00, RECIPE["crystal"]["darkRubyLinear"]),
        (0.22, (0.055, 0.0008, 0.003, 1)),
        (0.43, RECIPE["crystal"]["deepBloodRedLinear"]),
        (0.62, (0.38, 0.008, 0.016, 1)),
        (0.78, RECIPE["crystal"]["highlightRubyLinear"]),
        (0.91, (0.065, 0.012, 0.080, 1)),
        (1.00, (0.015, 0.050, 0.095, 1)),
    ]
    first = color.color_ramp.elements[0]
    first.position, first.color = stops[0]
    for pos, rgba in stops[1:]:
        item = color.color_ramp.elements.new(pos)
        item.color = rgba
    links.new(multiply.outputs[0], color.inputs["Fac"])

    layer = nodes.new("ShaderNodeLayerWeight")
    iridescent = nodes.new("ShaderNodeValToRGB")
    iridescent.color_ramp.elements.remove(iridescent.color_ramp.elements[1])
    iridescent_stops = [
        (0.0, (0.17, 0.008, 0.018, 1)),
        (0.32, (0.015, 0.035, 0.13, 1)),
        (0.56, (0.008, 0.11, 0.055, 1)),
        (0.78, (0.30, 0.012, 0.022, 1)),
        (1.0, (0.08, 0.012, 0.10, 1)),
    ]
    first = iridescent.color_ramp.elements[0]
    first.position, first.color = iridescent_stops[0]
    for pos, rgba in iridescent_stops[1:]:
        item = iridescent.color_ramp.elements.new(pos)
        item.color = rgba
    links.new(layer.outputs["Facing"], iridescent.inputs["Fac"])
    iri_mix = nodes.new("ShaderNodeMixRGB")
    iri_mix.blend_type = "SCREEN"
    iri_mix.inputs[0].default_value = RECIPE["crystal"]["iridescenceMix"]
    links.new(color.outputs["Color"], iri_mix.inputs[1])
    links.new(iridescent.outputs["Color"], iri_mix.inputs[2])

    motif_mix = nodes.new("ShaderNodeMixRGB")
    motif_mix.blend_type = "MIX"
    links.new(motif.outputs["Color"], motif_mix.inputs[0])
    links.new(iri_mix.outputs["Color"], motif_mix.inputs[1])
    motif_mix.inputs[2].default_value = RECIPE["motif"]["baseColorLinear"]
    perimeter_mix = nodes.new("ShaderNodeMixRGB")
    perimeter_mix.blend_type = "MIX"
    links.new(border.outputs["Color"], perimeter_mix.inputs[0])
    links.new(motif_mix.outputs["Color"], perimeter_mix.inputs[1])
    perimeter_mix.inputs[2].default_value = RECIPE["perimeter"]["baseColorLinear"]
    links.new(perimeter_mix.outputs["Color"], bsdf.inputs["Base Color"])

    max_mask = nodes.new("ShaderNodeMath")
    max_mask.operation = "MAXIMUM"
    links.new(motif.outputs["Color"], max_mask.inputs[0])
    links.new(border.outputs["Color"], max_mask.inputs[1])
    metallic = nodes.new("ShaderNodeMapRange")
    metallic.inputs["From Min"].default_value = 0.0
    metallic.inputs["From Max"].default_value = 1.0
    metallic.inputs["To Min"].default_value = 0.0
    metallic.inputs["To Max"].default_value = RECIPE["perimeter"]["metallic"]
    links.new(max_mask.outputs[0], metallic.inputs["Value"])
    links.new(metallic.outputs["Result"], bsdf.inputs["Metallic"])
    rough = nodes.new("ShaderNodeMapRange")
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = RECIPE["crystal"]["roughnessMinMax"][0]
    rough.inputs["To Max"].default_value = RECIPE["perimeter"]["roughness"]
    links.new(max_mask.outputs[0], rough.inputs["Value"])
    links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])
    transmission = nodes.new("ShaderNodeMapRange")
    transmission.inputs["From Min"].default_value = 0.0
    transmission.inputs["From Max"].default_value = 1.0
    transmission.inputs["To Min"].default_value = RECIPE["crystal"]["transmissionMinMax"][0]
    transmission.inputs["To Max"].default_value = RECIPE["crystal"]["transmissionMinMax"][1]
    links.new(multiply.outputs[0], transmission.inputs["Value"])
    links.new(transmission.outputs["Result"], bsdf.inputs["Transmission Weight"])

    set_input(bsdf, "IOR", RECIPE["crystal"]["ior"])
    set_input(bsdf, "Coat Weight", RECIPE["crystal"]["coatWeight"])
    set_input(bsdf, "Coat Roughness", RECIPE["crystal"]["coatRoughness"])
    set_input(bsdf, "Specular IOR Level", 0.62)
    set_input(bsdf, "Thin Film IOR", RECIPE["crystal"]["thinFilmIor"])
    thickness = nodes.new("ShaderNodeMapRange")
    thickness.inputs["From Min"].default_value = 0.0
    thickness.inputs["From Max"].default_value = 1.0
    thickness.inputs["To Min"].default_value = RECIPE["crystal"]["thinFilmThicknessNm"][0]
    thickness.inputs["To Max"].default_value = RECIPE["crystal"]["thinFilmThicknessNm"][1]
    links.new(layer.outputs["Facing"], thickness.inputs["Value"])
    links.new(thickness.outputs["Result"], bsdf.inputs["Thin Film Thickness"])
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)

    mosaic_bump = nodes.new("ShaderNodeBump")
    mosaic_bump.inputs["Strength"].default_value = RECIPE["crystal"]["mosaicBumpStrength"]
    mosaic_bump.inputs["Distance"].default_value = RECIPE["crystal"]["mosaicBumpDistanceMm"]
    links.new(multiply.outputs[0], mosaic_bump.inputs["Height"])
    motif_bump = nodes.new("ShaderNodeBump")
    motif_bump.inputs["Strength"].default_value = RECIPE["crystal"]["motifBumpStrength"]
    motif_bump.inputs["Distance"].default_value = RECIPE["crystal"]["motifDepthMm"]
    motif_bump.invert = True
    links.new(max_mask.outputs[0], motif_bump.inputs["Height"])
    links.new(mosaic_bump.outputs["Normal"], motif_bump.inputs["Normal"])
    links.new(motif_bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    mat["gate07_revision"] = 9
    mat["artworkSlot"] = slot_name
    mat["motifMaskSha256"] = sha256(motif_path)
    mat["borderMaskSha256"] = sha256(BORDER_MASK)
    mat["swapWithoutGeometryRebuild"] = True
    mat["appearanceAuthority"] = "original-user-frames-primary-official-exact-product-corroboration"
    mat["productionChemistry"] = "unknown"
    mat["emissionEnabled"] = False
    return mat


def assign_materials(lower, upper, silver, lower_surface, upper_surface):
    counts = {}
    for obj, surface in ((lower, lower_surface), (upper, upper_surface)):
        obj.data.materials.clear()
        obj.data.materials.append(silver)
        obj.data.materials.append(surface)
        top = 0
        for polygon in obj.data.polygons:
            polygon.material_index = 1 if polygon.normal.z > 0.999 else 0
            top += int(polygon.material_index == 1)
        if top != 1:
            raise RuntimeError(f"{obj.name} expected one top cap, got {top}")
        counts[obj.name] = {"topCapFaces": top, "sideAndBottomFaces": len(obj.data.polygons) - top}
    return counts


def area(name, location, energy, size, target, color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate07_rev9_neutral_reveal"] = True
    return obj


def reflection_card(name, location, rotation, scale, value):
    bpy.ops.mesh.primitive_plane_add(size=2, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    mat = bpy.data.materials.new(f"{name}_Mat")
    mat.diffuse_color = (value, value, value, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    set_input(bsdf, "Base Color", (value, value, value, 1))
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Roughness", 0.28)
    obj.data.materials.append(mat)
    obj.visible_camera = False
    obj["gate07_rev9_reflection_card"] = True
    return obj


def camera(name, location, target, lens, camera_id):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["camera_id"] = camera_id
    obj["recipe"] = "Gate07Rev9-neutral-material-reveal"
    return obj


def render(scene, cam, filename, width=1400, height=1050):
    scene.camera = cam
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUTPUT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def configure_scene(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_depth = "16"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.world.color = (0.018, 0.018, 0.018)
    if scene.world:
        scene.world.use_nodes = True
        nodes = scene.world.node_tree.nodes
        links = scene.world.node_tree.links
        nodes.clear()
        output = nodes.new("ShaderNodeOutputWorld")
        camera_background = nodes.new("ShaderNodeBackground")
        camera_background.inputs["Color"].default_value = (0.055, 0.062, 0.072, 1)
        camera_background.inputs["Strength"].default_value = 0.55
        environment_background = nodes.new("ShaderNodeBackground")
        environment_background.inputs["Strength"].default_value = 1.0
        texcoord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Rotation"].default_value = (0.28, -0.12, 0.42)
        gradient = nodes.new("ShaderNodeTexGradient")
        gradient.gradient_type = "LINEAR"
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
        studio_bands = [
            (0.00, (0.006, 0.007, 0.009, 1)),
            (0.12, (0.035, 0.040, 0.050, 1)),
            (0.25, (1.30, 1.34, 1.40, 1)),
            (0.34, (0.15, 0.17, 0.20, 1)),
            (0.49, (0.010, 0.012, 0.016, 1)),
            (0.61, (0.34, 0.36, 0.40, 1)),
            (0.73, (1.60, 1.55, 1.42, 1)),
            (0.82, (0.055, 0.060, 0.070, 1)),
            (0.94, (0.008, 0.010, 0.014, 1)),
            (1.00, (0.18, 0.20, 0.24, 1)),
        ]
        first = ramp.color_ramp.elements[0]
        first.position, first.color = studio_bands[0]
        for pos, rgba in studio_bands[1:]:
            item = ramp.color_ramp.elements.new(pos)
            item.color = rgba
        light_path = nodes.new("ShaderNodeLightPath")
        mix = nodes.new("ShaderNodeMixShader")
        links.new(texcoord.outputs["Normal"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
        links.new(gradient.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], environment_background.inputs["Color"])
        links.new(environment_background.outputs["Background"], mix.inputs[1])
        links.new(camera_background.outputs["Background"], mix.inputs[2])
        links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
        links.new(mix.outputs["Shader"], output.inputs["Surface"])


def main():
    for path in (SOURCE_BLEND, UPPER_MASK, LOWER_MASK, BORDER_MASK):
        if not path.exists():
            raise FileNotFoundError(path)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    configure_scene(scene)
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    model = [lower, upper]
    before = geometry_digest(model)
    if before != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError(f"Geometry digest changed before material rebuild: {before}")
    original_matrices = {obj.name: [list(row) for row in obj.matrix_world] for obj in model}
    clear_previous_presentation(set(model))

    silver = silver_material()
    upper_surface = crystal_material("M07R9_OriginalAuthority_Crystal_Upper", "Artwork_Upper", UPPER_MASK)
    lower_surface = crystal_material("M07R9_OriginalAuthority_Crystal_Lower", "Artwork_Lower", LOWER_MASK)
    assignments = assign_materials(lower, upper, silver, lower_surface, upper_surface)

    target = (0, 0, 2.5)
    area("R9_Key_Softbox", (55, -70, 95), 72000, 46, target)
    area("R9_Fill_Softbox", (-60, -20, 58), 30000, 54, target, (0.97, 0.99, 1.0))
    area("R9_Rim_Strip", (35, 72, 68), 61000, 25, target, (1.0, 0.985, 0.95))
    area("R9_Face_Reveal", (-8, -28, 115), 38000, 28, (0, 0, 4.8))
    reflection_card("R9_WhiteCard_Left", (-62, 0, 32), (math.radians(90), 0, math.radians(90)), (20, 28, 1), 0.78)
    reflection_card("R9_BlackCard_Right", (63, 4, 28), (math.radians(90), 0, math.radians(90)), (18, 24, 1), 0.006)
    reflection_card("R9_WhiteStrip_Back", (0, 58, 42), (math.radians(90), 0, 0), (32, 8, 1), 0.62)

    ground_mat = bpy.data.materials.new("M07R9_NeutralGround")
    ground_mat.use_nodes = True
    ground_bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
    set_input(ground_bsdf, "Base Color", (0.016, 0.018, 0.022, 1))
    set_input(ground_bsdf, "Roughness", 0.34)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, -6.15))
    ground = bpy.context.object
    ground.name = "R9_NeutralGround"
    ground.data.materials.append(ground_mat)

    cameras = {
        "front": camera("R9_Front", (0, -88, 128), target, 88, "front-source-oriented"),
        "oblique": camera("R9_Oblique", (74, -102, 72), target, 82, "hero"),
        "side": camera("R9_Side", (108, -58, 28), (0, 0, 0), 92, "right-oblique"),
        "open": camera("R9_Open", (0, -112, 116), (0, 8, 2.5), 86, "open-front"),
        "crystal": camera("R9_CrystalMacro", (24, -71, 78), (0, 0, 5.7), 118, "material-crystal-macro"),
        "silver": camera("R9_SilverMacro", (72, -96, 38), (10, -4, 0), 118, "material-silver-macro"),
        "perimeter": camera("R9_PerimeterMacro", (36, -70, 74), (0, 0, 5.5), 135, "material-perimeter-macro"),
    }
    render(scene, cameras["front"], "corrected-front.png")
    render(scene, cameras["oblique"], "corrected-oblique.png")
    render(scene, cameras["side"], "corrected-side.png")
    render(scene, cameras["crystal"], "crystal-macro.png", 1500, 1050)
    render(scene, cameras["silver"], "silver-reflection-closeup.png", 1500, 1000)
    render(scene, cameras["perimeter"], "black-perimeter-closeup.png", 1500, 1000)

    upper_location = upper.location.copy()
    upper.location.y += 21.0
    render(scene, cameras["open"], "corrected-open.png", 1400, 1200)
    upper.location = upper_location
    bpy.context.view_layer.update()

    after = geometry_digest(model)
    if after != before:
        raise RuntimeError(f"Geometry digest changed after material rebuild: {after}")
    matrices_after = {obj.name: [list(row) for row in obj.matrix_world] for obj in model}
    if matrices_after != original_matrices:
        raise RuntimeError("Model matrices changed during material rebuild.")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))

    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 9,
        "userQuote": "退回，我们要优先保证模型的质量",
        "sourceBlend": str(SOURCE_BLEND.relative_to(REPO)),
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO)),
        "sourceAssetIds": SOURCE_ASSETS,
        "authorityPolicy": {
            "primary": ["slider-intake-obs-frame-01", "slider-intake-obs-frame-05", "slider-intake-obs-frame-10"],
            "corroboration": [
                "slider-intake-haloo-official-03",
                "slider-intake-haloo-official-04",
                "slider-intake-haloo-official-06",
                "slider-intake-haloo-official-08",
            ],
            "unknownProductionChemistryClaimed": False,
        },
        "geometry": {
            "digestBefore": before,
            "digestAfter": after,
            "expectedDigest": EXPECTED_GEOMETRY_DIGEST,
            "unchanged": before == after == EXPECTED_GEOMETRY_DIGEST,
            "matricesUnchanged": matrices_after == original_matrices,
            "triangles": sum(len(obj.data.loop_triangles) for obj in model),
            "objects": [obj.name for obj in model],
            "assignments": assignments,
        },
        "artwork": {
            "upperMaskSha256": sha256(UPPER_MASK),
            "lowerMaskSha256": sha256(LOWER_MASK),
            "borderMaskSha256": sha256(BORDER_MASK),
            "independentlyReplaceable": True,
            "acceptedPlacementChanged": False,
        },
        "recipe": RECIPE,
        "render": {
            "engine": scene.render.engine,
            "resolution": "1400×1050 base; 1500×1000/1050 macros; 1400×1200 open",
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposure": scene.view_settings.exposure,
            "bloom": False,
            "emission": 0.0,
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
    (OUTPUT / "blender-material-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "material-recipe.json").write_text(
        json.dumps(RECIPE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
