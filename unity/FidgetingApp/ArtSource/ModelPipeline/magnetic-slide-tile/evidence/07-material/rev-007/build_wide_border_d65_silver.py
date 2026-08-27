#!/usr/bin/env python3
"""Build Gate 07 rev 7 full black perimeter and D65 silver diagnostics."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE_BLEND = OUTPUT.parents[1] / "06-geometry/rev-001/magnetic-slide-tile-geometry-r001.blend"
SOURCE_GEOMETRY_REPORT = OUTPUT.parents[1] / "06-geometry/rev-001/geometry-validation.json"
ARTWORK_CONFIG = OUTPUT / "artwork-layers.json"
ARTWORK_LINEAGE = OUTPUT / "artwork-lineage.json"
BORDER_SETTINGS = OUTPUT / "border-settings.json"
UPPER_MASK = OUTPUT / "artwork-upper-mask.png"
LOWER_MASK = OUTPUT / "artwork-lower-mask.png"
BORDER_MASK = OUTPUT / "artwork-top-perimeter-border-mask.png"
COLOR_REPORT = OUTPUT / "blood-red-source-analysis.json"
OUTPUT_BLEND = OUTPUT / "magnetic-slide-tile-material-r007.blend"
MATERIAL_REPORT = OUTPUT / "material-validation.json"

EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
AXIS_POINT_MM = [0.0, -9.5, 0.0]
SILVER = {
    "material": "M07R7_DaylightNeutralPolishedSilver",
    "baseColor": [0.97, 0.965, 0.94, 1.0],
    "metallic": 1.0,
    "roughness": 0.03,
    "ior": 1.45,
    "specularIorLevel": 0.5,
    "anisotropy": 0.14,
    "anisotropyRotation": 0.08,
    "coatWeight": 0.06,
    "coatRoughness": 0.02,
    "transmissionWeight": 0.0,
    "microScratchScale": 420.0,
    "microScratchStrength": 0.022,
    "microScratchDistanceMm": 0.004,
    "appearanceAuthority": "user-authorized-polished-pure-silver-visual-target",
    "productionMaterialClaim": False,
}
REV6_SILVER = {
    "material": "M07R7_Rev6SilverComparison",
    "baseColor": [0.94, 0.94, 0.92, 1.0],
    "metallic": 1.0,
    "roughness": 0.045,
    "ior": 1.45,
    "specularIorLevel": 0.5,
    "anisotropy": 0.22,
    "anisotropyRotation": 0.08,
    "coatWeight": 0.12,
    "coatRoughness": 0.025,
    "transmissionWeight": 0.0,
    "microScratchScale": 380.0,
    "microScratchStrength": 0.032,
    "microScratchDistanceMm": 0.006,
}
CRYSTAL = {
    "baseColor": [0.22, 0.008, 0.018, 1.0],
    "metallic": 0.0,
    "roughness": 0.035,
    "ior": 1.52,
    "specularIorLevel": 0.58,
    "coatWeight": 1.0,
    "coatRoughness": 0.012,
    "transmissionWeight": 0.12,
    "thinFilmIor": 1.38,
    "thinFilmThicknessNm": 430.0,
    "etchBumpStrength": 0.20,
    "etchDepthIllusionMm": 0.06,
    "motifDarkColor": [0.003, 0.0015, 0.002, 1.0],
    "motifMixFactor": 0.98,
    "roughnessDelta": 0.055,
    "microfacetSparkleScale": 145.0,
    "microfacetSparkleStrength": 0.028,
    "microfacetSparkleDistanceMm": 0.012,
    "substrateSaturation": 1.08,
    "substrateValue": 1.02,
}
SOURCE_LINKS = [
    {
        "assetId": "slider-intake-obs-frame-01",
        "role": "authoritative deep blood-red upper face and full upper motif",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-01.jpg",
    },
    {
        "assetId": "slider-intake-obs-frame-05",
        "role": "authoritative oblique blood-red crystal response",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-05.jpg",
    },
    {
        "assetId": "slider-intake-obs-frame-10",
        "role": "authoritative open pose and source-visible lower pattern end",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-10.jpg",
    },
    {
        "assetId": "slider-intake-haloo-official-03",
        "role": "official three-color face lineup; silver perimeter, opaque motif, bright angle-varying face",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/03.png",
    },
    {
        "assetId": "slider-intake-haloo-official-04",
        "role": "official high-resolution purple face closeup; motif boundaries and face highlights",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/04.png",
    },
    {
        "assetId": "slider-intake-haloo-official-06",
        "role": "official oblique open view; edge stacking and purple-blue interference",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/06.png",
    },
    {
        "assetId": "slider-intake-haloo-official-08",
        "role": "official front/open view; bright crystalline highlight breakup",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/08.png",
    },
    {
        "assetId": "slider-intake-nxedc-ref-01",
        "role": "exact-product front closeup used for deterministic motif visual trace",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/external-nxedc/reference-01.jpg",
    },
    {
        "assetId": "slider-intake-nxedc-ref-05",
        "role": "exact-product macro oblique closeup; parallax, edge stack, green-blue-pink response",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/external-nxedc/reference-05.jpg",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geometry_digest(objects: list[bpy.types.Object]) -> str:
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


def set_input(shader: bpy.types.Node, name: str, value) -> None:
    socket = shader.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def principled_material(name: str, values: dict) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    set_input(shader, "Base Color", tuple(values["baseColor"]))
    set_input(shader, "Metallic", values["metallic"])
    set_input(shader, "Roughness", values["roughness"])
    set_input(shader, "IOR", values["ior"])
    set_input(shader, "Specular IOR Level", values.get("specularIorLevel", 0.5))
    set_input(shader, "Anisotropic", values.get("anisotropy", 0.0))
    set_input(shader, "Anisotropic Rotation", values.get("anisotropyRotation", 0.0))
    set_input(shader, "Coat Weight", values["coatWeight"])
    set_input(shader, "Coat Roughness", values["coatRoughness"])
    set_input(shader, "Transmission Weight", values["transmissionWeight"])
    set_input(shader, "Emission Color", (0.0, 0.0, 0.0, 1.0))
    set_input(shader, "Emission Strength", 0.0)
    if values.get("microScratchScale"):
        texcoord = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = values["microScratchScale"]
        noise.inputs["Detail"].default_value = 1.8
        noise.inputs["Roughness"].default_value = 0.42
        mapping.inputs["Scale"].default_value = (1.0, 42.0, 1.0)
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = values["microScratchStrength"]
        bump.inputs["Distance"].default_value = values["microScratchDistanceMm"]
        links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    material["gate07_revision"] = 7
    material["certainty"] = "visual-approximation"
    return material


def artwork_group(slot_name: str, mask_path: Path, border_path: Path | None) -> bpy.types.NodeTree:
    group = bpy.data.node_groups.new(slot_name, "ShaderNodeTree")
    group.interface.new_socket(name="Vector", in_out="INPUT", socket_type="NodeSocketVector")
    group.interface.new_socket(name="Mask", in_out="OUTPUT", socket_type="NodeSocketFloat")
    input_node = group.nodes.new("NodeGroupInput")
    output_node = group.nodes.new("NodeGroupOutput")
    mask = group.nodes.new("ShaderNodeTexImage")
    mask.name = f"{slot_name}_ExternalMask"
    mask.label = mask_path.name
    mask.image = bpy.data.images.load(str(mask_path), check_existing=True)
    mask.image.colorspace_settings.name = "Non-Color"
    mask.interpolation = "Closest"
    mask.extension = "CLIP"
    group.links.new(input_node.outputs["Vector"], mask.inputs["Vector"])
    mask_output = mask.outputs["Color"]
    if border_path is not None:
        border = group.nodes.new("ShaderNodeTexImage")
        border.name = f"{slot_name}_TopPerimeterBorderMask"
        border.label = border_path.name
        border.image = bpy.data.images.load(str(border_path), check_existing=True)
        border.image.colorspace_settings.name = "Non-Color"
        border.interpolation = "Closest"
        border.extension = "CLIP"
        maximum = group.nodes.new("ShaderNodeMath")
        maximum.name = f"{slot_name}_MotifPlusBorder"
        maximum.operation = "MAXIMUM"
        group.links.new(input_node.outputs["Vector"], border.inputs["Vector"])
        group.links.new(mask_output, maximum.inputs[0])
        group.links.new(border.outputs["Color"], maximum.inputs[1])
        mask_output = maximum.outputs[0]
        group["borderMaskRepositoryRelative"] = str(border_path.relative_to(OUTPUT.parents[7]))
        group["borderMaskSha256"] = sha256(border_path)
        group["borderCompositionOperation"] = "MAXIMUM"
    group.links.new(mask_output, output_node.inputs["Mask"])
    group["slotName"] = slot_name
    group["externalMaskRepositoryRelative"] = str(mask_path.relative_to(OUTPUT.parents[7]))
    group["externalMaskSha256"] = sha256(mask_path)
    group["borderOverlayEnabled"] = border_path is not None
    group["swapWithoutGeometryRebuild"] = True
    return group


def artwork_material(name: str, slot_name: str, mask_path: Path, border_path: Path | None = BORDER_MASK) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", CRYSTAL["roughness"])
    set_input(shader, "IOR", CRYSTAL["ior"])
    set_input(shader, "Specular IOR Level", CRYSTAL["specularIorLevel"])
    set_input(shader, "Coat Weight", CRYSTAL["coatWeight"])
    set_input(shader, "Coat Roughness", CRYSTAL["coatRoughness"])
    set_input(shader, "Transmission Weight", CRYSTAL["transmissionWeight"])
    set_input(shader, "Emission Color", (0.0, 0.0, 0.0, 1.0))
    set_input(shader, "Emission Strength", 0.0)
    set_input(shader, "Thin Film IOR", CRYSTAL["thinFilmIor"])
    set_input(shader, "Thin Film Thickness", CRYSTAL["thinFilmThicknessNm"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    slot = nodes.new("ShaderNodeGroup")
    slot.name = slot_name
    slot.label = f"{slot_name} · external motif + editable perimeter border"
    slot.node_tree = artwork_group(slot_name, mask_path, border_path)
    links.new(texcoord.outputs["Generated"], slot.inputs["Vector"])

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.8
    noise.inputs["Detail"].default_value = 3.2
    noise.inputs["Roughness"].default_value = 0.61
    noise.inputs["Distortion"].default_value = 0.18
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])

    color = nodes.new("ShaderNodeValToRGB")
    color.color_ramp.elements.remove(color.color_ramp.elements[1])
    stops = [
        (0.0, (0.018, 0.0005, 0.0015, 1.0)),
        (0.28, (0.075, 0.0015, 0.004, 1.0)),
        (0.49, (0.22, 0.008, 0.018, 1.0)),
        (0.68, (0.40, 0.012, 0.022, 1.0)),
        (0.86, (0.12, 0.006, 0.018, 1.0)),
        (1.0, (0.018, 0.035, 0.14, 1.0)),
    ]
    first = color.color_ramp.elements[0]
    first.position, first.color = stops[0]
    for position, rgba in stops[1:]:
        element = color.color_ramp.elements.new(position)
        element.color = rgba
    links.new(noise.outputs["Fac"], color.inputs["Fac"])
    saturation = nodes.new("ShaderNodeHueSaturation")
    saturation.inputs["Saturation"].default_value = CRYSTAL["substrateSaturation"]
    saturation.inputs["Value"].default_value = CRYSTAL["substrateValue"]
    links.new(color.outputs["Color"], saturation.inputs["Color"])

    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    links.new(saturation.outputs["Color"], mix.inputs[1])
    mix.inputs[2].default_value = tuple(CRYSTAL["motifDarkColor"])

    factor = nodes.new("ShaderNodeMath")
    factor.operation = "MULTIPLY"
    factor.inputs[1].default_value = CRYSTAL["motifMixFactor"]
    links.new(slot.outputs["Mask"], factor.inputs[0])
    links.new(factor.outputs[0], mix.inputs[0])
    links.new(mix.outputs["Color"], shader.inputs["Base Color"])

    rough_mix = nodes.new("ShaderNodeMapRange")
    rough_mix.inputs["From Min"].default_value = 0.0
    rough_mix.inputs["From Max"].default_value = 1.0
    rough_mix.inputs["To Min"].default_value = CRYSTAL["roughness"]
    rough_mix.inputs["To Max"].default_value = CRYSTAL["roughness"] + CRYSTAL["roughnessDelta"]
    links.new(slot.outputs["Mask"], rough_mix.inputs["Value"])
    links.new(rough_mix.outputs["Result"], shader.inputs["Roughness"])

    sparkle_noise = nodes.new("ShaderNodeTexNoise")
    sparkle_noise.inputs["Scale"].default_value = CRYSTAL["microfacetSparkleScale"]
    sparkle_noise.inputs["Detail"].default_value = 2.2
    sparkle_noise.inputs["Roughness"].default_value = 0.62
    links.new(texcoord.outputs["Generated"], sparkle_noise.inputs["Vector"])
    sparkle_ramp = nodes.new("ShaderNodeValToRGB")
    sparkle_ramp.color_ramp.elements[0].position = 0.69
    sparkle_ramp.color_ramp.elements[1].position = 0.78
    sparkle_bump = nodes.new("ShaderNodeBump")
    sparkle_bump.inputs["Strength"].default_value = CRYSTAL["microfacetSparkleStrength"]
    sparkle_bump.inputs["Distance"].default_value = CRYSTAL["microfacetSparkleDistanceMm"]
    links.new(sparkle_noise.outputs["Fac"], sparkle_ramp.inputs["Fac"])
    links.new(sparkle_ramp.outputs["Color"], sparkle_bump.inputs["Height"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = CRYSTAL["etchBumpStrength"]
    bump.inputs["Distance"].default_value = CRYSTAL["etchDepthIllusionMm"]
    bump.invert = True
    links.new(slot.outputs["Mask"], bump.inputs["Height"])
    links.new(sparkle_bump.outputs["Normal"], bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    material["gate07_revision"] = 7
    material["artworkSlot"] = slot_name
    material["externalMaskRepositoryRelative"] = str(mask_path.relative_to(OUTPUT.parents[7]))
    material["externalMaskSha256"] = sha256(mask_path)
    material["swapWithoutGeometryRebuild"] = True
    material["motifKind"] = "user-authorized-prior-material-design-reuse-not-new-exact-trace"
    material["motifMaskSha256"] = sha256(mask_path)
    material["borderOverlayEnabled"] = border_path is not None
    if border_path is not None:
        material["borderMaskRepositoryRelative"] = str(border_path.relative_to(OUTPUT.parents[7]))
        material["borderMaskSha256"] = sha256(border_path)
    material["etchBumpStrength"] = CRYSTAL["etchBumpStrength"]
    material["etchDepthIllusionMm"] = CRYSTAL["etchDepthIllusionMm"]
    material["roughnessDelta"] = CRYSTAL["roughnessDelta"]
    material["thinFilmIor"] = CRYSTAL["thinFilmIor"]
    material["thinFilmThicknessNm"] = CRYSTAL["thinFilmThicknessNm"]
    material["emissionEnabled"] = False
    material["microfacetSparkleScale"] = CRYSTAL["microfacetSparkleScale"]
    material["microfacetSparkleStrength"] = CRYSTAL["microfacetSparkleStrength"]
    material["substrateSaturation"] = CRYSTAL["substrateSaturation"]
    material["substrateValue"] = CRYSTAL["substrateValue"]
    material["certainty"] = "visual-approximation"
    return material


def assign_model_materials(lower: bpy.types.Object, upper: bpy.types.Object, silver: bpy.types.Material, upper_artwork: bpy.types.Material, lower_artwork: bpy.types.Material) -> dict:
    lower.data.materials.clear()
    lower.data.materials.append(silver)
    lower.data.materials.append(lower_artwork)
    lower_top_count = 0
    for polygon in lower.data.polygons:
        polygon.material_index = 1 if polygon.normal.z > 0.999 else 0
        lower_top_count += int(polygon.material_index == 1)
    upper.data.materials.clear()
    upper.data.materials.append(silver)
    upper.data.materials.append(upper_artwork)
    upper_top_count = 0
    for polygon in upper.data.polygons:
        polygon.material_index = 1 if polygon.normal.z > 0.999 else 0
        upper_top_count += int(polygon.material_index == 1)
    if upper_top_count != 1 or lower_top_count != 1:
        raise RuntimeError(f"Expected one top cap per body, got upper={upper_top_count}, lower={lower_top_count}.")
    return {
        "upperTopCapFaceCount": upper_top_count,
        "lowerTopCapFaceCount": lower_top_count,
        "upperFrameFaceCount": len(upper.data.polygons) - upper_top_count,
        "lowerFrameFaceCount": len(lower.data.polygons) - lower_top_count,
    }


def area_light(name: str, location: tuple[float, float, float], energy: float, size: float, target: Vector) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate07_neutral_reveal_light"] = True
    return obj


def sun_light(name: str, location: tuple[float, float, float], energy: float, angle_degrees: float, color: tuple[float, float, float], target: Vector) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "SUN")
    data.energy = energy
    data.angle = angle_degrees * 3.141592653589793 / 180
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate07_d65_daylight_diagnostic"] = True
    obj["correlated_color_temperature_kelvin"] = 6504
    return obj


def camera(name: str, location: tuple[float, float, float], target: Vector, lens: float, camera_id: str, recipe: str) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["camera_id"] = camera_id
    obj["recipe"] = recipe
    return obj


def text_object(collection: bpy.types.Collection, name: str, body: str, location: tuple[float, float, float], target_camera: bpy.types.Object, size: float, material: bpy.types.Material) -> bpy.types.Object:
    curve = bpy.data.curves.new(f"{name}_Curve", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.008
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = target_camera.rotation_euler
    obj.data.materials.append(material)
    obj["gate07_review_annotation"] = True
    return obj


def variant_sample(collection: bpy.types.Collection, source: bpy.types.Object, name: str, location: tuple[float, float, float], surface: bpy.types.Material, silver: bpy.types.Material) -> bpy.types.Object:
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = name
    obj.parent = None
    obj.matrix_world = Matrix.Identity(4)
    obj.location = location
    obj.scale = (0.58, 0.58, 0.58)
    obj.data.materials.clear()
    obj.data.materials.append(silver)
    obj.data.materials.append(surface)
    for polygon in obj.data.polygons:
        polygon.material_index = 1 if polygon.normal.z > 0.999 else 0
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj["gate07_review_sample"] = True
    return obj


def render(scene: bpy.types.Scene, target_camera: bpy.types.Object, filename: str, width: int, height: int) -> None:
    scene.camera = target_camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUTPUT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def reflection_card(collection: bpy.types.Collection, name: str, location: tuple[float, float, float], rotation: tuple[float, float, float], scale: tuple[float, float, float], color: tuple[float, float, float, float]) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=2, location=location, rotation=rotation)
    card = bpy.context.object
    card.name = name
    card.scale = scale
    for owner in list(card.users_collection):
        owner.objects.unlink(card)
    collection.objects.link(card)
    values = {
        **REV6_SILVER,
        "baseColor": list(color),
        "metallic": 0.0,
        "roughness": 0.32,
        "coatWeight": 0.0,
        "coatRoughness": 0.0,
    }
    card.data.materials.append(principled_material(f"{name}_Diffuse", values))
    card["gate07_calibrated_reflection_card"] = True
    return card


def pbr_values(material: bpy.types.Material) -> dict:
    shader = material.node_tree.nodes.get("Principled BSDF")
    return {
        "baseColor": list(shader.inputs["Base Color"].default_value),
        "metallic": shader.inputs["Metallic"].default_value,
        "roughness": shader.inputs["Roughness"].default_value,
        "ior": shader.inputs["IOR"].default_value,
        "anisotropy": shader.inputs["Anisotropic"].default_value,
        "anisotropyRotation": shader.inputs["Anisotropic Rotation"].default_value,
        "coatWeight": shader.inputs["Coat Weight"].default_value,
        "coatRoughness": shader.inputs["Coat Roughness"].default_value,
        "transmissionWeight": shader.inputs["Transmission Weight"].default_value,
        "thinFilmIor": shader.inputs["Thin Film IOR"].default_value,
        "thinFilmThicknessNm": shader.inputs["Thin Film Thickness"].default_value,
        "specularIorLevel": shader.inputs["Specular IOR Level"].default_value,
        "emissionStrength": shader.inputs["Emission Strength"].default_value,
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_BLEND)
    geometry_report = json.loads(SOURCE_GEOMETRY_REPORT.read_text(encoding="utf-8"))
    artwork_config = json.loads(ARTWORK_CONFIG.read_text(encoding="utf-8"))
    artwork_lineage = json.loads(ARTWORK_LINEAGE.read_text(encoding="utf-8"))
    border_settings = json.loads(BORDER_SETTINGS.read_text(encoding="utf-8"))
    color_report = json.loads(COLOR_REPORT.read_text(encoding="utf-8"))
    if geometry_report["geometryIdentity"]["evaluatedDigest"] != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Approved Gate 06 geometry digest mismatch.")
    if artwork_config["geometryDigest"] != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Artwork config geometry contract mismatch.")
    if artwork_config["slots"]["Artwork_Upper"]["maskSha256"] != sha256(UPPER_MASK):
        raise RuntimeError("Upper artwork hash mismatch.")
    if artwork_config["slots"]["Artwork_Lower"]["maskSha256"] != sha256(LOWER_MASK):
        raise RuntimeError("Lower artwork hash mismatch.")
    if artwork_lineage["sourceSha256"] != sha256(UPPER_MASK) or artwork_lineage["sourceSha256"] != sha256(LOWER_MASK):
        raise RuntimeError("Clean motif lineage hash mismatch.")
    if not artwork_lineage["notNewExactTraceClaim"]:
        raise RuntimeError("Historical design reuse must not become a new exact-trace claim.")
    if border_settings["outerPerimeterInsetPx"] != 0 or border_settings["borderWidthPx"] != 64:
        raise RuntimeError("Editable top-perimeter border setting mismatch.")
    if artwork_config["topPerimeterBorder"]["maskSha256"] != sha256(BORDER_MASK):
        raise RuntimeError("External top-perimeter border mask hash mismatch.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "07-material"
    scene["material_revision"] = 7
    scene["source_gate06_sha256"] = source_hash_before
    scene["geometry_change_authorized"] = False
    scene["diagnostic_lights_only_not_gate08"] = True
    scene["artwork_config_repository_relative"] = str(ARTWORK_CONFIG.relative_to(OUTPUT.parents[7]))
    scene["artwork_lineage_repository_relative"] = str(ARTWORK_LINEAGE.relative_to(OUTPUT.parents[7]))
    scene["border_settings_repository_relative"] = str(BORDER_SETTINGS.relative_to(OUTPUT.parents[7]))
    scene["top_face_black_border_width_px"] = border_settings["borderWidthPx"]
    scene["top_face_black_border_outer_inset_px"] = border_settings["outerPerimeterInsetPx"]
    scene["silver_visual_target_not_production_material_claim"] = True
    scene["daylight_diagnostic_cct_kelvin"] = 6504
    scene["daylight_diagnostic_fixed_exposure_ev"] = 0.0
    scene["mechanism_rotation_range_degrees"] = 360
    scene["mechanism_detent_step_degrees"] = 12
    scene["mechanism_detent_count"] = 30
    scene["mechanism_delivery_state"] = "specified-only-runtime-and-hardware-validation-pending"

    root = bpy.data.objects["MagneticSlideTile_Blockout_R003"]
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    model_objects = [lower, upper]
    if tuple(translation.location) != (0.0, 0.0, 0.0) or tuple(pivot.location) != tuple(AXIS_POINT_MM):
        raise RuntimeError("Approved closed pose or point axis changed.")
    if envelope.type != "EMPTY" or not envelope.hide_render or envelope["geometry"] != "none":
        raise RuntimeError("Concealed mechanism metadata changed.")

    before = geometry_digest(model_objects)
    matrices = {obj.name: [list(row) for row in obj.matrix_world] for obj in [lower, upper, envelope]}
    silver = principled_material(SILVER["material"], SILVER)
    rev6_silver = principled_material(REV6_SILVER["material"], REV6_SILVER)
    upper_artwork = artwork_material("M07R7_BloodRedCrystal_WideBorder_Upper", "Artwork_Upper", UPPER_MASK)
    lower_artwork = artwork_material("M07R7_BloodRedCrystal_WideBorder_Lower", "Artwork_Lower", LOWER_MASK)
    rev6_border_baseline = artwork_material(
        "M07R7_BloodRedCrystal_Rev6BorderBaseline",
        "Comparison_Rev6Border",
        UPPER_MASK,
        None,
    )
    assignments = assign_model_materials(lower, upper, silver, upper_artwork, lower_artwork)
    after_assignment = geometry_digest(model_objects)

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
    neutral_lights = [
        area_light("M07R7_Neutral_Key_Softbox", (48, -62, 88), 62000, 48, Vector((0, 0, 1))),
        area_light("M07R7_Neutral_Fill_Softbox", (-54, -14, 52), 36000, 42, Vector((0, 0, 1))),
        area_light("M07R7_Neutral_Rim_Strip", (18, 68, 58), 52000, 30, Vector((0, 2, 1))),
        area_light("M07R7_Neutral_Face_Reveal", (-6, -34, 104), 34000, 26, Vector((0, 0, 3))),
    ]

    world = scene.world or bpy.data.worlds.new("M07R7_NeutralWorld")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.105, 0.105, 0.105, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    ground = bpy.data.objects.get("PresentationGround")
    if ground:
        ground.hide_render = False
        ground_values = {**SILVER, "baseColor": [0.055, 0.055, 0.055, 1.0], "metallic": 0.0, "roughness": 0.42, "coatWeight": 0.0}
        ground_material = principled_material("M07R7_NeutralGround", ground_values)
        ground.data.materials.clear()
        ground.data.materials.append(ground_material)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0

    board_camera = camera("M07R7_MaterialBoardCamera", (128, -148, 108), Vector((12, 4, 4)), 60, "material-board", "neutral-wide-black-border-daylight-neutral-silver")
    closeup_camera = camera("M07R7_MaterialCloseupCamera", (58, -72, 58), Vector((0, -1, 3.2)), 78, "material-closeup", "neutral-blood-red-wide-border-silver")
    front_camera = camera("M07R7_NeutralFrontCamera", (0, -112, 64), Vector((0, 0, 3.5)), 82, "front", "same-camera-border-and-silver-comparisons")
    open_camera = camera("M07R7_OpenArtworkCamera", (65, -106, 88), Vector((0, 7, 3.5)), 72, "right-oblique", "open-wide-border-clean-lower-artwork")
    daylight_hero_camera = camera("M07R7_D65HeroCamera", (88, -126, 72), Vector((0, 0, 4)), 72, "hero", "d65-daylight-with-neutral-reference-card")
    daylight_side_camera = camera("M07R7_D65SideCamera", (118, -8, 28), Vector((0, 0, 4)), 82, "right", "silver-side-direct-d65-daylight")

    cards = bpy.data.collections.new("Gate07R7_ReflectionAndReferenceCards")
    scene.collection.children.link(cards)
    camera_white_card = reflection_card(cards, "M07R7_Studio_WhiteReflector", (-24, -180, 48), (1.570796, 0, 0), (34, 38, 1), (0.80, 0.80, 0.80, 1.0))
    camera_black_card = reflection_card(cards, "M07R7_Studio_BlackReflector", (46, -180, 48), (1.570796, 0, 0), (18, 38, 1), (0.008, 0.008, 0.008, 1.0))
    daylight_reference_cards = [
        reflection_card(cards, "M07R7_D65Reference_White80", (-46, 15, 9), (1.570796, 0, 0), (5, 7, 1), (0.80, 0.80, 0.80, 1.0)),
        reflection_card(cards, "M07R7_D65Reference_Gray18", (-34, 15, 9), (1.570796, 0, 0), (5, 7, 1), (0.18, 0.18, 0.18, 1.0)),
        reflection_card(cards, "M07R7_D65Reference_Black", (-22, 15, 9), (1.570796, 0, 0), (5, 7, 1), (0.008, 0.008, 0.008, 1.0)),
    ]
    for card in daylight_reference_cards:
        card.hide_render = True
    camera_white_card["gate07_off_camera_reflection_card"] = True
    camera_black_card["gate07_off_camera_reflection_card"] = True

    review = bpy.data.collections.new("Gate07R7_ReviewAnnotations")
    scene.collection.children.link(review)
    label_values = {**SILVER, "baseColor": [0.94, 0.94, 0.94, 1.0], "metallic": 0.0, "roughness": 0.3, "coatWeight": 0.0}
    label_material = principled_material("M07R7_Label_NoEmission", label_values)
    layer_labels = [
        text_object(review, "M07R7_Title", "BLOOD RED · FULL BLACK TOP PERIMETER · DAYLIGHT-NEUTRAL SILVER", (39, -12, 24), board_camera, 0.84, label_material),
        text_object(review, "M07R7_Values", "TOP BORDER 64 px / 10.32% / ≈3.2 mm · OUTER INSET 0 px\nREV 2/3 CLEAN MOTIF SHA 8250df70d228… PRESERVED\nSILVER .970/.965/.940 · METAL 1 · ROUGH .030 · ANISO .14\nD65 6504 K DIAGNOSTIC · FIXED EV 0 · NO EMISSION · GATE 08 BLOCKED", (42, 3, 12), board_camera, 0.54, label_material),
    ]
    render(scene, board_camera, "neutral-pbr-material-board.png", 1400, 1000)
    for obj in layer_labels:
        obj.hide_render = True
    render(scene, closeup_camera, "neutral-pbr-material-closeup.png", 1200, 1200)
    render(scene, closeup_camera, "blood-red-closeup.png", 1200, 1200)

    upper.material_slots[1].material = rev6_border_baseline
    render(scene, front_camera, "rev6-border-same-camera.png", 1100, 1300)
    upper.material_slots[1].material = upper_artwork
    render(scene, front_camera, "wide-border-same-camera.png", 1100, 1300)

    lower.material_slots[0].material = rev6_silver
    upper.material_slots[0].material = rev6_silver
    render(scene, front_camera, "rev6-silver-neutral-studio-same-camera.png", 1100, 1300)
    lower.material_slots[0].material = silver
    upper.material_slots[0].material = silver
    render(scene, front_camera, "daylight-neutral-silver-neutral-studio-same-camera.png", 1100, 1300)

    translation.location.y = 21.0
    bpy.context.view_layer.update()
    render(scene, open_camera, "open-slide-lower-artwork.png", 1200, 1400)
    process_labels = [
        text_object(review, "M07R7_ProcessTitle", "EDITABLE MOTIF + EXTERNAL FULL-PERIMETER BORDER", (40, -8, 24), board_camera, 0.72, label_material),
        text_object(review, "M07R7_ProcessSlots", "Artwork_Upper → separate clean motif file / node group\nArtwork_Lower → separate clean motif file / node group\nTopFaceBlackPerimeterBorder → shared initial external mask\nWIDTH 64 px · OUTER INSET 0 px · MAXIMUM COMPOSITE\nSILVER STRUCTURAL SIDE WALL IS OUTSIDE THIS TOP-FACE MASK", (42, 7, 12), board_camera, 0.50, label_material),
    ]
    render(scene, board_camera, "editable-artwork-layer-board.png", 1500, 1100)
    for obj in process_labels:
        obj.hide_render = True
    translation.location.y = 0.0
    bpy.context.view_layer.update()

    for light in neutral_lights:
        light.hide_render = True
    camera_white_card.hide_render = True
    camera_black_card.hide_render = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.72, 0.72, 0.72, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.75
    if ground:
        daylight_ground_values = {**SILVER, "baseColor": [0.55, 0.55, 0.55, 1.0], "metallic": 0.0, "roughness": 0.52, "coatWeight": 0.0}
        daylight_ground = principled_material("M07R7_D65_NeutralGroundBounce", daylight_ground_values)
        ground.data.materials.clear()
        ground.data.materials.append(daylight_ground)
    d65_sun = sun_light(
        "M07R7_D65_6504K_Sun",
        (72, -58, 118),
        3.2,
        0.53,
        (1.0, 0.994, 0.97),
        Vector((0, 0, 3)),
    )
    d65_sky_fill = area_light(
        "M07R7_D65_NeutralOvercastFill",
        (-76, -22, 108),
        28000,
        60,
        Vector((0, 0, 3)),
    )
    d65_sky_fill["gate07_neutral_reveal_light"] = False
    d65_sky_fill["gate07_d65_daylight_diagnostic"] = True
    d65_sky_fill.data.color = (1.0, 0.998, 0.985)
    for card in daylight_reference_cards:
        card.hide_render = False
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 6504
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 10
    scene.view_settings.exposure = 0.0
    render(scene, daylight_hero_camera, "outdoor-d65-hero-neutral-card.png", 1500, 1100)
    for card in daylight_reference_cards:
        card.hide_render = True
    render(scene, daylight_side_camera, "outdoor-d65-silver-side-direct.png", 1500, 1000)

    final = geometry_digest(model_objects)
    source_hash_after = sha256(SOURCE_BLEND)
    slots = {
        lower.name: [slot.material.name for slot in lower.material_slots],
        upper.name: [slot.material.name for slot in upper.material_slots],
    }
    visible_model_meshes = [obj.name for obj in root.children_recursive if obj.type == "MESH" and not obj.hide_render]
    hidden_mechanism_meshes = [obj.name for obj in root.children_recursive if obj.type == "MESH" and "mechanism" in obj.name.lower()]
    animated = [obj.name for obj in root.children_recursive if obj.animation_data or obj.constraints]
    unchanged = before == after_assignment == final == EXPECTED_GEOMETRY_DIGEST
    report = {
        "schemaVersion": 7,
        "gate": "07-material",
        "materialRevision": 7,
        "supersedesMaterialRevision": 6,
        "userRequest": "widen the black top-face border to the full outer perimeter and make polished silver read bright neutral under D65 daylight",
        "sourceGate06": {
            "geometryRevision": 1,
            "blendPath": str(SOURCE_BLEND.relative_to(OUTPUT.parents[7])),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "evaluatedGeometryDigest": EXPECTED_GEOMETRY_DIGEST,
        },
        "geometryPreservation": {
            "digestBefore": before,
            "digestAfterMaterialAssignment": after_assignment,
            "digestAfterRenders": final,
            "unchanged": unchanged,
            "boundsMm": [50.0, 31.0, 12.0],
            "axisPointWorldMm": AXIS_POINT_MM,
            "matricesUnchanged": all([list(row) for row in obj.matrix_world] == matrices[obj.name] for obj in [lower, upper, envelope]),
            "envelopeType": envelope.type,
            "envelopeHideRender": envelope.hide_render,
            "envelopeGeometry": envelope["geometry"],
            "smoothProfileSegmentsPerSemicircle": upper["arc_segments_per_semicircle"],
            "visibleModelMeshes": visible_model_meshes,
            "hiddenMechanismMeshes": hidden_mechanism_meshes,
            "artworkOrnamentGeometryCount": 0,
            "animatedOrConstrainedObjects": animated,
            "pass": unchanged and source_hash_before == source_hash_after and not hidden_mechanism_meshes and not animated and set(visible_model_meshes) == {"LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"},
        },
        "materialZones": {
            "polished-pure-silver-visual-target-exterior": {
                **SILVER,
                "objects": ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving side-and-bottom"],
                "support": "The exact product page confirms Steel. The user separately authorizes a polished pure-silver visual target; this does not claim silver production material.",
                "certainty": "confirmed-steel-user-authorized-pure-silver-appearance-only",
                "actualPbr": pbr_values(silver),
                "rev6SilverComparisonPbr": pbr_values(rev6_silver),
            },
            "deep-blood-red-crystal-face": {
                **CRYSTAL,
                "faces": "Upper and lower top caps through independent artwork materials",
                "method": "clear-coat/transmission over controlled dark-red substrate with restrained ruby/blue accents; crisp dark-fill motif uses nearest-neighbor mask sampling",
                "support": "User-authoritative blood-red correction plus user-authorized lossless reuse of the prior clean motif design.",
                "certainty": "visual-approximation",
                "actualPbrUpper": pbr_values(upper_artwork),
                "actualPbrLower": pbr_values(lower_artwork),
            },
        },
        "materialAssignments": {
            "slots": slots,
            "topCapFaces": assignments,
            "zoneCount": 3,
            "pass": slots[lower.name] == [SILVER["material"], lower_artwork.name]
            and slots[upper.name] == [SILVER["material"], upper_artwork.name]
            and assignments["upperTopCapFaceCount"] == 1
            and assignments["lowerTopCapFaceCount"] == 1,
        },
        "artworkLayers": {
            "configPath": str(ARTWORK_CONFIG.relative_to(OUTPUT.parents[7])),
            "configSha256": sha256(ARTWORK_CONFIG),
            "slots": artwork_config["slots"],
            "nodeGroups": {
                "Artwork_Upper": bpy.data.node_groups["Artwork_Upper"]["externalMaskRepositoryRelative"],
                "Artwork_Lower": bpy.data.node_groups["Artwork_Lower"]["externalMaskRepositoryRelative"],
            },
            "independentSwap": UPPER_MASK != LOWER_MASK
            and artwork_config["slots"]["Artwork_Upper"]["independentlyEditable"]
            and artwork_config["slots"]["Artwork_Lower"]["independentlyEditable"],
            "initialHashesIntentionallyEqual": sha256(UPPER_MASK) == sha256(LOWER_MASK),
            "geometryRebuildRequired": False,
            "lineage": {
                "path": str(ARTWORK_LINEAGE.relative_to(OUTPUT.parents[7])),
                "sha256": sha256(ARTWORK_LINEAGE),
                "reuseClass": artwork_lineage["reuseClass"],
                "sourceAssetId": artwork_lineage["sourceAssetId"],
                "sourceSha256": artwork_lineage["sourceSha256"],
                "notNewExactTraceClaim": artwork_lineage["notNewExactTraceClaim"],
            },
            "topPerimeterBorder": {
                **artwork_config["topPerimeterBorder"],
                "settingsPath": str(BORDER_SETTINGS.relative_to(OUTPUT.parents[7])),
                "settingsSha256": sha256(BORDER_SETTINGS),
                "widthPx": border_settings["borderWidthPx"],
                "widthFractionMinorAxis": border_settings["borderWidthFractionMinorAxis"],
                "approxVisualWidthMm": border_settings["approxVisualWidthMm"],
                "outerPerimeterInsetPx": border_settings["outerPerimeterInsetPx"],
                "blackZone": border_settings["topologyBoundary"]["black"],
                "silverZone": border_settings["topologyBoundary"]["silver"],
            },
            "pass": all(name in bpy.data.node_groups for name in ("Artwork_Upper", "Artwork_Lower"))
            and UPPER_MASK != LOWER_MASK
            and sha256(UPPER_MASK) == sha256(LOWER_MASK) == artwork_lineage["sourceSha256"]
            and all(bpy.data.node_groups[name]["borderOverlayEnabled"] for name in ("Artwork_Upper", "Artwork_Lower"))
            and border_settings["outerPerimeterInsetPx"] == 0
            and artwork_lineage["notNewExactTraceClaim"],
        },
        "colorTarget": color_report,
        "sourceLinks": SOURCE_LINKS,
        "sourceClaimIds": ["slider-analysis-claim-material-language"],
        "manufacturingAnalysis": {
            "confirmed": [
                {
                    "claim": "The exact HALOOPLAYER product page lists Material: Steel.",
                    "confidence": "high",
                    "url": "https://www.halooplayer.com/halo-heart-rhythm-haloo-player-edc-push-slider--high-tech-stress-relief-toy-fingertip-gyro--hand-fidget-gadget-p6875695.html",
                }
            ],
            "visualCues": [
                "Narrow white mirror highlights and a bright perimeter support polished metal, but do not identify alloy or plating.",
                "The opaque dark motif keeps crisp edges over changing red fields.",
                "Oblique closeups show highlight separation and apparent depth between motif, color field, and perimeter.",
                "Patchy red response can fit nacre/abalone, dichroic film, or interference pigment; pixels do not establish chemistry.",
            ],
            "recommendedProvisionalStack": [
                {"layer": "polished pure-silver appearance target over confirmed-steel product context", "confidence": "user-authorized-visual-target", "alternatives": ["polished steel with silver-like response", "steel substrate with bright silver-colored plating"], "productionMaterialClaim": False},
                {"layer": "opaque dark motif", "confidence": "medium", "alternatives": ["blackened/annealed steel mark", "etched and dark-filled recess", "laser-cut black overlay"]},
                {"layer": "iridescent substrate", "confidence": "medium-low", "alternatives": ["mother-of-pearl/abalone inlay", "dichroic multilayer film", "interference-pigment layer"]},
                {"layer": "clear protective cap", "confidence": "medium-low", "alternatives": ["clear resin", "clear polymer lens", "glass/crystal cover"]},
            ],
            "researchLinks": [
                "https://doi.org/10.1038/s41598-021-99327-4",
                "https://www.antalis.fr/mediashare/g4media/pdf/TS_EN_3M_GLASS_FINISHES_DICHROIC_TECH_DATASHEET_00_11022026.pdf",
                "https://www.troteclaser.com/en/helpcenter/materials/application-techniques/laser-marking-steel-through-annealing-process",
            ],
            "productionSpecificationEstablished": False,
        },
        "uncertaintyPolicy": {
            "pbrValuesAreProductionSpecifications": False,
            "motifIsExactProductionVector": False,
            "motifReuseIsNewExactTraceClaim": False,
            "pureSilverIsProductionMaterialClaim": False,
            "exactProductMaterialConfirmed": "steel",
            "alloyKnown": False,
            "coatingKnown": False,
            "clearLayerMaterialKnown": False,
            "iridescentSubstrateKnown": False,
            "hiddenRatchetConstructionKnown": False,
        },
        "mechanismDecisionMetadata": {
            "decisionState": "locked-user-authoritative",
            "deliveryState": "specified-only-runtime-and-hardware-validation-pending",
            "rotationRangeDegrees": 360,
            "detentStepDegrees": 12,
            "detentCount": 30,
            "semantics": "ratchet",
            "physicalAndHapticConsumeSameSetting": True,
            "runtimeChanged": False,
            "hapticsChanged": False,
            "unityChanged": False,
            "hiddenConstruction": "unknown",
        },
        "neutralReveal": {
            "lights": [light.name for light in neutral_lights],
            "lightSignature": [
                {"location": [48, -62, 88], "energy": 62000, "size": 48, "target": [0, 0, 1]},
                {"location": [-54, -14, 52], "energy": 36000, "size": 42, "target": [0, 0, 1]},
                {"location": [18, 68, 58], "energy": 52000, "size": 30, "target": [0, 2, 1]},
                {"location": [-6, -34, 104], "energy": 34000, "size": 26, "target": [0, 0, 3]},
            ],
            "worldColorLinear": [0.105, 0.105, 0.105],
            "worldStrength": 0.9,
            "finalLightingOrEnvironment": False,
            "materialBoard": "neutral-pbr-material-board.png",
            "materialCloseup": "neutral-pbr-material-closeup.png",
        },
        "diagnosticLighting": {
            "classification": "Gate 07 material tests only; not approved Gate 08 lighting",
            "exposureEv": 0.0,
            "sameCameraComparisons": {
                "camera": {"location": [0, -112, 64], "target": [0, 0, 3.5], "lensMm": 82},
                "rev6Border": "rev6-border-same-camera.png",
                "wideBorder": "wide-border-same-camera.png",
                "rev6SilverNeutralStudio": "rev6-silver-neutral-studio-same-camera.png",
                "daylightNeutralSilverNeutralStudio": "daylight-neutral-silver-neutral-studio-same-camera.png",
            },
            "d65Daylight": {
                "classification": "controlled outdoor/daylight material diagnostic; not final Gate 08 lighting",
                "heroImage": "outdoor-d65-hero-neutral-card.png",
                "sideImage": "outdoor-d65-silver-side-direct.png",
                "correlatedColorTemperatureKelvin": 6504,
                "sun": {
                    "name": d65_sun.name,
                    "energy": 3.2,
                    "angleDegrees": 0.53,
                    "linearRgb": [1.0, 0.994, 0.97],
                    "location": [72, -58, 118],
                    "target": [0, 0, 3],
                },
                "neutralOvercastFill": {
                    "name": d65_sky_fill.name,
                    "energyW": 28000,
                    "size": 60,
                    "linearRgb": [1.0, 0.998, 0.985],
                },
                "worldLinearRgb": [0.72, 0.72, 0.72],
                "worldStrength": 0.75,
                "groundLinearRgb": [0.55, 0.55, 0.55],
                "whiteBalanceKelvin": 6504,
                "whiteBalanceTint": 10,
                "viewTransform": scene.view_settings.view_transform,
                "look": scene.view_settings.look,
                "exposureEv": 0.0,
                "referenceCards": [
                    {"name": "white80", "linearRgb": [0.8, 0.8, 0.8]},
                    {"name": "gray18", "linearRgb": [0.18, 0.18, 0.18]},
                    {"name": "black", "linearRgb": [0.008, 0.008, 0.008]},
                ],
                "emission": 0,
            },
            "offCameraStudioReflectionCards": {
                "cards": [
                    {"name": "white", "linearRgb": [0.8, 0.8, 0.8]},
                    {"name": "black", "linearRgb": [0.008, 0.008, 0.008]},
                ],
                "emission": 0,
            },
            "finalLightingOrEnvironment": False,
        },
        "forbiddenLightingAndShaderTricks": {
            "upperEmissionStrength": pbr_values(upper_artwork)["emissionStrength"],
            "lowerEmissionStrength": pbr_values(lower_artwork)["emissionStrength"],
            "silverEmissionStrength": pbr_values(silver)["emissionStrength"],
            "bloomEnabled": False,
            "overexposureUsed": False,
            "gate08LightingUsed": False,
            "pass": pbr_values(upper_artwork)["emissionStrength"] == 0.0
            and pbr_values(lower_artwork)["emissionStrength"] == 0.0
            and pbr_values(silver)["emissionStrength"] == 0.0,
        },
        "scope": {
            "geometryChanged": False,
            "artworkGeometryAdded": False,
            "hiddenMechanismAdded": False,
            "runtimeChanged": False,
            "hapticsChanged": False,
            "unityAssetChanged": False,
            "gate08Entered": False,
        },
        "blender": bpy.app.version_string,
    }
    required = [
        report["sourceGate06"]["unchanged"],
        report["geometryPreservation"]["pass"],
        report["materialAssignments"]["pass"],
        report["artworkLayers"]["pass"],
        report["colorTarget"]["chemistryClaimed"] is False,
        report["manufacturingAnalysis"]["productionSpecificationEstablished"] is False,
        report["uncertaintyPolicy"]["pureSilverIsProductionMaterialClaim"] is False,
        report["uncertaintyPolicy"]["motifReuseIsNewExactTraceClaim"] is False,
        report["forbiddenLightingAndShaderTricks"]["pass"],
        report["mechanismDecisionMetadata"]["detentCount"] == 30,
        report["neutralReveal"]["finalLightingOrEnvironment"] is False,
        not any(report["scope"].values()),
    ]
    report["pass"] = all(required)
    MATERIAL_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    for obj in [*layer_labels, *process_labels]:
        obj.hide_render = True
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
