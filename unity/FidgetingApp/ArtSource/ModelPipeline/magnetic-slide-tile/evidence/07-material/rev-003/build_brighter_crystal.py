#!/usr/bin/env python3
"""Build Gate 07 rev 2 silver, etched-motif, crystal-iridescent evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE_BLEND = OUTPUT.parents[1] / "06-geometry/rev-001/magnetic-slide-tile-geometry-r001.blend"
SOURCE_GEOMETRY_REPORT = OUTPUT.parents[1] / "06-geometry/rev-001/geometry-validation.json"
MOTIF_MASK = OUTPUT.parent / "rev-002/source-derived-motif-visual-trace.png"
MOTIF_PROVENANCE = OUTPUT.parent / "rev-002/motif-trace-provenance.json"
REV2_CLOSEUP = OUTPUT.parent / "rev-002/neutral-pbr-material-closeup.png"
OUTPUT_BLEND = OUTPUT / "magnetic-slide-tile-material-r003.blend"
MATERIAL_REPORT = OUTPUT / "material-validation.json"

EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
AXIS_POINT_MM = [0.0, -9.5, 0.0]
SILVER = {
    "material": "M07R3_MirrorSilver_Unchanged",
    "baseColor": [0.72, 0.78, 0.86, 1.0],
    "metallic": 1.0,
    "roughness": 0.095,
    "ior": 1.5,
    "coatWeight": 0.32,
    "coatRoughness": 0.055,
    "transmissionWeight": 0.0,
}
HYBRID = {
    "material": "M07R3_BrighterCrystal_NoEmission_Recommended",
    "baseColor": [0.42, 0.20, 0.72, 1.0],
    "metallic": 0.0,
    "roughness": 0.028,
    "ior": 1.52,
    "specularIorLevel": 0.58,
    "coatWeight": 1.0,
    "coatRoughness": 0.010,
    "transmissionWeight": 0.15,
    "thinFilmIor": 1.42,
    "thinFilmThicknessNm": 545.0,
    "etchBumpStrength": 0.24,
    "etchDepthIllusionMm": 0.06,
    "motifDarkColor": [0.006, 0.008, 0.014, 1.0],
    "motifMixFactor": 0.98,
    "microfacetSparkleScale": 130.0,
    "microfacetSparkleStrength": 0.035,
    "microfacetSparkleDistanceMm": 0.012,
    "substrateSaturation": 1.30,
    "substrateValue": 1.15,
}
VARIANTS = {
    "A": {
        "label": "A  MIRROR SILVER + MONO ETCH",
        "material": "M07R2_VariantA_MonochromeEtch",
        "transmissionWeight": 0.0,
        "roughness": 0.12,
        "thinFilmThicknessNm": 0.0,
        "motifMixFactor": 0.82,
    },
    "B": {
        "label": "B  DARK ETCH + CRYSTAL IRIDESCENCE\nRECOMMENDED / SOURCE-FAITHFUL",
        "material": HYBRID["material"],
        "transmissionWeight": HYBRID["transmissionWeight"],
        "roughness": HYBRID["roughness"],
        "thinFilmThicknessNm": HYBRID["thinFilmThicknessNm"],
        "motifMixFactor": HYBRID["motifMixFactor"],
    },
    "C": {
        "label": "C  CLEARER CRYSTAL-HEAVY",
        "material": "M07R2_VariantC_ClearCrystal",
        "transmissionWeight": 0.62,
        "roughness": 0.045,
        "thinFilmThicknessNm": 610.0,
        "motifMixFactor": 0.68,
    },
}
SOURCE_LINKS = [
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
    shader = material.node_tree.nodes["Principled BSDF"]
    set_input(shader, "Base Color", tuple(values["baseColor"]))
    set_input(shader, "Metallic", values["metallic"])
    set_input(shader, "Roughness", values["roughness"])
    set_input(shader, "IOR", values["ior"])
    set_input(shader, "Coat Weight", values["coatWeight"])
    set_input(shader, "Coat Roughness", values["coatRoughness"])
    set_input(shader, "Transmission Weight", values["transmissionWeight"])
    set_input(shader, "Emission Color", (0.0, 0.0, 0.0, 1.0))
    set_input(shader, "Emission Strength", 0.0)
    material["gate07_revision"] = 3
    material["certainty"] = "visual-approximation"
    return material


def hybrid_material(name: str, variant: dict, monochrome: bool = False) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", variant["roughness"])
    set_input(shader, "IOR", HYBRID["ior"])
    set_input(shader, "Specular IOR Level", HYBRID["specularIorLevel"])
    set_input(shader, "Coat Weight", HYBRID["coatWeight"])
    set_input(shader, "Coat Roughness", HYBRID["coatRoughness"])
    set_input(shader, "Transmission Weight", variant["transmissionWeight"])
    set_input(shader, "Emission Color", (0.0, 0.0, 0.0, 1.0))
    set_input(shader, "Emission Strength", 0.0)
    set_input(shader, "Thin Film IOR", HYBRID["thinFilmIor"])
    set_input(shader, "Thin Film Thickness", variant["thinFilmThicknessNm"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    mask = nodes.new("ShaderNodeTexImage")
    mask.image = bpy.data.images.load(str(MOTIF_MASK), check_existing=True)
    mask.image.colorspace_settings.name = "Non-Color"
    mask.interpolation = "Linear"
    mask.extension = "CLIP"
    links.new(texcoord.outputs["Generated"], mask.inputs["Vector"])

    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.4
    noise.inputs["Detail"].default_value = 3.2
    noise.inputs["Roughness"].default_value = 0.68
    noise.inputs["Distortion"].default_value = 0.26
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])

    color = nodes.new("ShaderNodeValToRGB")
    color.color_ramp.elements.remove(color.color_ramp.elements[1])
    stops = [
        (0.0, (0.02, 0.58, 1.0, 1.0)),
        (0.32, (0.06, 0.16, 1.0, 1.0)),
        (0.46, (0.82, 0.03, 1.0, 1.0)),
        (0.58, (1.0, 0.12, 0.78, 1.0)),
        (0.70, (0.01, 1.0, 0.88, 1.0)),
        (1.0, (0.02, 1.0, 0.30, 1.0)),
    ]
    first = color.color_ramp.elements[0]
    first.position, first.color = stops[0]
    for position, rgba in stops[1:]:
        element = color.color_ramp.elements.new(position)
        element.color = rgba
    links.new(noise.outputs["Fac"], color.inputs["Fac"])
    saturation = nodes.new("ShaderNodeHueSaturation")
    saturation.inputs["Saturation"].default_value = HYBRID["substrateSaturation"]
    saturation.inputs["Value"].default_value = HYBRID["substrateValue"]
    links.new(color.outputs["Color"], saturation.inputs["Color"])

    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    mix.inputs[1].default_value = (0.62, 0.66, 0.72, 1.0) if monochrome else (0.10, 0.03, 0.28, 1.0)
    links.new(saturation.outputs["Color"], mix.inputs[1])
    mix.inputs[2].default_value = tuple(HYBRID["motifDarkColor"])

    factor = nodes.new("ShaderNodeMath")
    factor.operation = "MULTIPLY"
    factor.inputs[1].default_value = variant["motifMixFactor"]
    links.new(mask.outputs["Color"], factor.inputs[0])
    links.new(factor.outputs[0], mix.inputs[0])
    links.new(mix.outputs["Color"], shader.inputs["Base Color"])

    sparkle_noise = nodes.new("ShaderNodeTexNoise")
    sparkle_noise.inputs["Scale"].default_value = HYBRID["microfacetSparkleScale"]
    sparkle_noise.inputs["Detail"].default_value = 2.2
    sparkle_noise.inputs["Roughness"].default_value = 0.62
    links.new(texcoord.outputs["Generated"], sparkle_noise.inputs["Vector"])
    sparkle_ramp = nodes.new("ShaderNodeValToRGB")
    sparkle_ramp.color_ramp.elements[0].position = 0.69
    sparkle_ramp.color_ramp.elements[1].position = 0.78
    sparkle_bump = nodes.new("ShaderNodeBump")
    sparkle_bump.inputs["Strength"].default_value = HYBRID["microfacetSparkleStrength"]
    sparkle_bump.inputs["Distance"].default_value = HYBRID["microfacetSparkleDistanceMm"]
    links.new(sparkle_noise.outputs["Fac"], sparkle_ramp.inputs["Fac"])
    links.new(sparkle_ramp.outputs["Color"], sparkle_bump.inputs["Height"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = HYBRID["etchBumpStrength"]
    bump.inputs["Distance"].default_value = HYBRID["etchDepthIllusionMm"]
    bump.invert = True
    links.new(mask.outputs["Color"], bump.inputs["Height"])
    links.new(sparkle_bump.outputs["Normal"], bump.inputs["Normal"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])

    material["gate07_revision"] = 3
    material["motifKind"] = "source-derived-raster-visual-trace-not-production-vector"
    material["motifMaskSha256"] = sha256(MOTIF_MASK)
    material["etchBumpStrength"] = HYBRID["etchBumpStrength"]
    material["etchDepthIllusionMm"] = HYBRID["etchDepthIllusionMm"]
    material["thinFilmIor"] = HYBRID["thinFilmIor"]
    material["thinFilmThicknessNm"] = variant["thinFilmThicknessNm"]
    material["emissionEnabled"] = False
    material["microfacetSparkleScale"] = HYBRID["microfacetSparkleScale"]
    material["microfacetSparkleStrength"] = HYBRID["microfacetSparkleStrength"]
    material["substrateSaturation"] = HYBRID["substrateSaturation"]
    material["substrateValue"] = HYBRID["substrateValue"]
    material["certainty"] = "visual-approximation"
    return material


def assign_model_materials(lower: bpy.types.Object, upper: bpy.types.Object, silver: bpy.types.Material, hybrid: bpy.types.Material) -> dict:
    lower.data.materials.clear()
    lower.data.materials.append(silver)
    for polygon in lower.data.polygons:
        polygon.material_index = 0
    upper.data.materials.clear()
    upper.data.materials.append(silver)
    upper.data.materials.append(hybrid)
    top_count = 0
    for polygon in upper.data.polygons:
        polygon.material_index = 1 if polygon.normal.z > 0.999 else 0
        top_count += int(polygon.material_index == 1)
    if top_count != 1:
        raise RuntimeError(f"Expected one approved top cap, got {top_count}.")
    return {"topCapFaceCount": top_count, "frameFaceCount": len(upper.data.polygons) - top_count}


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


def pbr_values(material: bpy.types.Material) -> dict:
    shader = material.node_tree.nodes.get("Principled BSDF")
    return {
        "metallic": shader.inputs["Metallic"].default_value,
        "roughness": shader.inputs["Roughness"].default_value,
        "ior": shader.inputs["IOR"].default_value,
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
    motif_report = json.loads(MOTIF_PROVENANCE.read_text(encoding="utf-8"))
    if geometry_report["geometryIdentity"]["evaluatedDigest"] != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Approved Gate 06 geometry digest mismatch.")
    if not motif_report["pass"] or motif_report["outputSha256"] != sha256(MOTIF_MASK):
        raise RuntimeError("Motif trace provenance mismatch.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "07-material"
    scene["material_revision"] = 3
    scene["source_gate06_sha256"] = source_hash_before
    scene["geometry_change_authorized"] = False
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
    recommended = hybrid_material(HYBRID["material"], HYBRID)
    assignments = assign_model_materials(lower, upper, silver, recommended)
    after_assignment = geometry_digest(model_objects)

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
    lights = [
        area_light("M07R3_Key_Softbox", (48, -62, 88), 62000, 48, Vector((0, 0, 1))),
        area_light("M07R3_Fill_Softbox", (-54, -14, 52), 36000, 42, Vector((0, 0, 1))),
        area_light("M07R3_Rim_Strip", (18, 68, 58), 52000, 30, Vector((0, 2, 1))),
        area_light("M07R3_Face_Reveal", (-6, -34, 104), 34000, 26, Vector((0, 0, 3))),
    ]
    world = scene.world or bpy.data.worlds.new("M07R3_NeutralWorld")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.09, 0.105, 0.13, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    ground = bpy.data.objects.get("PresentationGround")
    if ground:
        ground.hide_render = False
        ground_values = {**SILVER, "baseColor": [0.035, 0.042, 0.055, 1.0], "metallic": 0.0, "roughness": 0.42, "coatWeight": 0.0}
        ground_material = principled_material("M07R3_NeutralGround", ground_values)
        ground.data.materials.clear()
        ground.data.materials.append(ground_material)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    board_camera = camera("M07R3_MaterialBoardCamera", (128, -148, 108), Vector((12, 4, 4)), 60, "material-board", "neutral-reveal-brighter-crystal-and-value-deltas")
    closeup_camera = camera("M07R3_MaterialCloseupCamera", (58, -72, 58), Vector((0, -1, 3.2)), 78, "material-closeup", "neutral-reveal-brighter-crystal-same-as-rev2")

    review = bpy.data.collections.new("Gate07R3_ReviewAnnotations")
    scene.collection.children.link(review)
    label_values = {**SILVER, "baseColor": [0.92, 0.95, 1.0, 1.0], "metallic": 0.0, "roughness": 0.3, "coatWeight": 0.0}
    label_material = principled_material("M07R3_Label_NoEmission", label_values)
    layer_labels = [
        text_object(review, "M07R3_Recommended", "BRIGHTER CRYSTAL R3 · NO EMISSION", (39, -12, 24), board_camera, 1.25, label_material),
        text_object(review, "M07R3_Deltas", "ROUGHNESS  .075 → .028\nSUBSTRATE TRANSMISSION  .48 → .15\nCLEAR CAP LOBE  .88/.035 → 1.00/.010\nIOR  1.46 → 1.52\nTHIN FILM  1.38/520 → 1.42/545 nm\nLIGHTS + CAMERA UNCHANGED", (42, 3, 12), board_camera, 0.86, label_material),
    ]
    render(scene, board_camera, "neutral-pbr-material-board.png", 1400, 1000)
    for obj in layer_labels:
        obj.hide_render = True
    render(scene, closeup_camera, "neutral-pbr-material-closeup.png", 1200, 1200)

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
        "schemaVersion": 3,
        "gate": "07-material",
        "materialRevision": 3,
        "supersedesMaterialRevision": 2,
        "userRequest": "再 crystal 一点，就是更亮一些.",
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
            "mirror-silver-exterior-body": {
                **SILVER,
                "objects": ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving side-and-bottom"],
                "support": "Official exact product page confirms Steel. Images support a bright mirror-silver response; alloy and finishing process remain unknown.",
                "certainty": "confirmed-steel-visual-finish-provisional",
                "actualPbr": pbr_values(silver),
            },
            "source-derived-dark-etched-motif": {
                "material": HYBRID["material"],
                "faces": "UpperCapsule_Moving top-cap shader only",
                "method": "image-mask-to-base-color-and-inverted-bump; no mesh displacement",
                "motifKind": motif_report["kind"],
                "motifMaskSha256": motif_report["outputSha256"],
                "motifMixFactor": HYBRID["motifMixFactor"],
                "etchBumpStrength": HYBRID["etchBumpStrength"],
                "etchDepthIllusionMm": HYBRID["etchDepthIllusionMm"],
                "certainty": "source-derived-visual-trace-production-process-unknown",
            },
            "crystal-iridescent-face": {
                **HYBRID,
                "faces": "UpperCapsule_Moving top-cap shader only",
                "method": "clear-coat/transmission over procedural purple-blue-green interference with Principled thin film",
                "support": "Exact-product images show bright specular highlights, depth/parallax cues, and purple-blue-green angle-dependent color.",
                "certainty": "visual-approximation",
                "actualPbr": pbr_values(recommended),
            },
        },
        "materialAssignments": {
            "slots": slots,
            "upperFaces": assignments,
            "zoneCount": 3,
            "pass": slots[lower.name] == [SILVER["material"]] and slots[upper.name] == [SILVER["material"], HYBRID["material"]] and assignments == {"topCapFaceCount": 1, "frameFaceCount": 514},
        },
        "motifProvenance": {**motif_report, "registeredAs": "visual-trace-not-production-vector"},
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
                "The opaque dark motif keeps crisp edges over changing purple-blue-green fields.",
                "Oblique closeups show highlight separation and apparent depth between motif, color field, and perimeter.",
                "Color shifts and patchy organic cells fit nacre/abalone; smooth angle-dependent bands also fit dichroic film or interference pigment.",
            ],
            "recommendedProvisionalStack": [
                {"layer": "mirror-polished steel frame/body", "confidence": "medium", "alternatives": ["polished steel with clear protective finish", "steel substrate with bright plating"]},
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
        "revisionComparison": {
            "baselineRevision": 2,
            "baselineCloseupPath": str(REV2_CLOSEUP.relative_to(OUTPUT.parents[7])),
            "baselineCloseupSha256": sha256(REV2_CLOSEUP),
            "sameNeutralLights": True,
            "sameBoardCamera": {
                "location": [128, -148, 108],
                "target": [12, 4, 4],
                "lensMm": 60,
            },
            "sameCloseupCamera": {
                "location": [58, -72, 58],
                "target": [0, -1, 3.2],
                "lensMm": 78,
            },
            "baselinePbr": {
                "roughness": 0.075,
                "ior": 1.46,
                "specularIorLevel": 0.5,
                "transmissionWeight": 0.48,
                "coatWeight": 0.88,
                "coatRoughness": 0.035,
                "thinFilmIor": 1.38,
                "thinFilmThicknessNm": 520.0,
                "motifMixFactor": 0.94,
                "emissionStrength": 0.22,
            },
            "candidatePbr": {
                "roughness": HYBRID["roughness"],
                "ior": HYBRID["ior"],
                "specularIorLevel": HYBRID["specularIorLevel"],
                "transmissionWeight": HYBRID["transmissionWeight"],
                "coatWeight": HYBRID["coatWeight"],
                "coatRoughness": HYBRID["coatRoughness"],
                "thinFilmIor": HYBRID["thinFilmIor"],
                "thinFilmThicknessNm": HYBRID["thinFilmThicknessNm"],
                "motifMixFactor": HYBRID["motifMixFactor"],
                "emissionStrength": 0.0,
                "microfacetSparkleScale": HYBRID["microfacetSparkleScale"],
                "microfacetSparkleStrength": HYBRID["microfacetSparkleStrength"],
                "microfacetSparkleDistanceMm": HYBRID["microfacetSparkleDistanceMm"],
            },
            "opticalStackRationale": "The clear cap is represented by the full-weight low-roughness Coat lobe. The underlying iridescent substrate transmission is reduced so Eevee does not lose substrate energy through a one-surface approximation; stronger optical separation comes from IOR, coat, thin film, and microfacet response without emission.",
            "deltas": {
                "roughness": -0.047,
                "ior": 0.06,
                "specularIorLevel": 0.08,
                "transmissionWeight": -0.33,
                "coatWeight": 0.12,
                "coatRoughness": -0.025,
                "thinFilmIor": 0.04,
                "thinFilmThicknessNm": 25.0,
                "motifMixFactor": 0.04,
                "emissionStrength": -0.22,
            },
        },
        "uncertaintyPolicy": {
            "pbrValuesAreProductionSpecifications": False,
            "motifIsExactProductionVector": False,
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
            "lights": [light.name for light in lights],
            "lightSignature": [
                {"location": [48, -62, 88], "energy": 62000, "size": 48, "target": [0, 0, 1]},
                {"location": [-54, -14, 52], "energy": 36000, "size": 42, "target": [0, 0, 1]},
                {"location": [18, 68, 58], "energy": 52000, "size": 30, "target": [0, 2, 1]},
                {"location": [-6, -34, 104], "energy": 34000, "size": 26, "target": [0, 0, 3]},
            ],
            "worldStrength": 0.9,
            "finalLightingOrEnvironment": False,
            "materialBoard": "neutral-pbr-material-board.png",
            "materialCloseup": "neutral-pbr-material-closeup.png",
        },
        "forbiddenLightingAndShaderTricks": {
            "emissionStrength": pbr_values(recommended)["emissionStrength"],
            "bloomEnabled": False,
            "overexposureUsed": False,
            "gate08LightingUsed": False,
            "pass": pbr_values(recommended)["emissionStrength"] == 0.0,
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
        report["motifProvenance"]["pass"],
        report["motifProvenance"]["registeredAs"] == "visual-trace-not-production-vector",
        report["manufacturingAnalysis"]["productionSpecificationEstablished"] is False,
        report["forbiddenLightingAndShaderTricks"]["pass"],
        report["mechanismDecisionMetadata"]["detentCount"] == 30,
        report["neutralReveal"]["finalLightingOrEnvironment"] is False,
        not any(report["scope"].values()),
    ]
    MATERIAL_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not all(required):
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    for obj in layer_labels:
        obj.hide_render = True
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
