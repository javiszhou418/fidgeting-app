#!/usr/bin/env python3
"""Build Gate 07 neutral material evidence from approved Gate 06 geometry."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE_BLEND = OUTPUT.parent.parent / "06-geometry/rev-001/magnetic-slide-tile-geometry-r001.blend"
SOURCE_GEOMETRY_REPORT = OUTPUT.parent.parent / "06-geometry/rev-001/geometry-validation.json"
OUTPUT_BLEND = OUTPUT / "magnetic-slide-tile-material-r001.blend"
MATERIAL_REPORT = OUTPUT / "material-validation.json"

EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
AXIS_POINT_MM = [0.0, -9.5, 0.0]

MATERIAL_ZONES = {
    "lower-polished-silver-alloy": {
        "object": "LowerBody_Fixed_CleanPlane",
        "faces": "all",
        "material": "M07_Lower_PolishedSilver_Approx",
        "baseColor": [0.58, 0.63, 0.70, 1.0],
        "metallic": 0.96,
        "roughness": 0.17,
        "ior": 1.50,
        "coatWeight": 0.24,
        "coatRoughness": 0.10,
        "transmissionWeight": 0.0,
        "support": "Current approved bright-silver material language and exact-product reflective outer rim.",
        "certainty": "visual-approximation",
        "uncertainty": "Exact alloy, plating stack, brushed direction, oxidation resistance, and production roughness are unknown.",
    },
    "upper-dark-coated-frame": {
        "object": "UpperCapsule_Moving",
        "faces": "side-and-bottom",
        "material": "M07_Upper_DarkCoatedMetal_Approx",
        "baseColor": [0.040, 0.050, 0.065, 1.0],
        "metallic": 0.90,
        "roughness": 0.20,
        "ior": 1.50,
        "coatWeight": 0.34,
        "coatRoughness": 0.12,
        "transmissionWeight": 0.0,
        "support": "HALOOPLAYER and NXEDC images show a dark reflective frame inside the bright perimeter.",
        "certainty": "visual-approximation",
        "uncertainty": "Exact substrate, black coating chemistry, thickness, and gloss tolerance are unknown.",
    },
    "upper-smoked-clear-face": {
        "object": "UpperCapsule_Moving",
        "faces": "top-cap-only",
        "material": "M07_Upper_SmokedClearFace_Approx",
        "baseColor": [0.075, 0.095, 0.130, 1.0],
        "metallic": 0.0,
        "roughness": 0.13,
        "ior": 1.48,
        "coatWeight": 0.62,
        "coatRoughness": 0.08,
        "transmissionWeight": 0.12,
        "support": "Exact-product images show a transparent or semitransparent jewel-like decorative face above dark structure.",
        "certainty": "visual-approximation",
        "uncertainty": "Exact resin/glass identity, absorption, tint, transmission, thickness, birefringence, coating, and pearlescent stack are unknown.",
    },
}

SOURCE_LINKS = [
    {
        "assetId": "slider-intake-haloo-official-01",
        "role": "official hero; bright reflective perimeter, dark inner frame, jewel-like face",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/01.png",
    },
    {
        "assetId": "slider-intake-haloo-official-02",
        "role": "official dual-sided exterior; consistent silver rim and dark face boundary",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/02.png",
    },
    {
        "assetId": "slider-intake-nxedc-ref-02",
        "role": "reseller exact-product exterior; reflective frame and translucent decorative layer",
        "path": "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/external-nxedc/reference-02.jpg",
    },
]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evaluated_geometry_digest(objects: list[bpy.types.Object]) -> str:
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


def look_at(obj: bpy.types.Object, target: Vector, up: str = "Y") -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", up).to_euler()


def set_input(shader: bpy.types.Node, name: str, value) -> None:
    socket = shader.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def create_pbr_material(zone: dict) -> bpy.types.Material:
    result = bpy.data.materials.new(zone["material"])
    result.use_nodes = True
    result.diffuse_color = tuple(zone["baseColor"])
    result["gate07_zone"] = True
    result["certainty"] = zone["certainty"]
    result["uncertainty"] = zone["uncertainty"]
    shader = result.node_tree.nodes.get("Principled BSDF")
    set_input(shader, "Base Color", tuple(zone["baseColor"]))
    set_input(shader, "Metallic", zone["metallic"])
    set_input(shader, "Roughness", zone["roughness"])
    set_input(shader, "IOR", zone["ior"])
    set_input(shader, "Coat Weight", zone["coatWeight"])
    set_input(shader, "Coat Roughness", zone["coatRoughness"])
    set_input(shader, "Transmission Weight", zone["transmissionWeight"])
    return result


def assign_material_zones(lower: bpy.types.Object, upper: bpy.types.Object) -> dict[str, bpy.types.Material]:
    materials = {zone_id: create_pbr_material(zone) for zone_id, zone in MATERIAL_ZONES.items()}
    lower.data.materials.clear()
    lower.data.materials.append(materials["lower-polished-silver-alloy"])
    for polygon in lower.data.polygons:
        polygon.material_index = 0

    upper.data.materials.clear()
    upper.data.materials.append(materials["upper-dark-coated-frame"])
    upper.data.materials.append(materials["upper-smoked-clear-face"])
    top_cap_count = 0
    for polygon in upper.data.polygons:
        if polygon.normal.z > 0.999:
            polygon.material_index = 1
            top_cap_count += 1
        else:
            polygon.material_index = 0
    if top_cap_count != 1:
        raise RuntimeError(f"Expected one source top-cap face, got {top_cap_count}.")
    return materials


def create_area_light(name: str, location: tuple[float, float, float], energy: float, size: float, target: Vector) -> bpy.types.Object:
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


def create_camera(name: str, location: tuple[float, float, float], target: Vector, lens: float, camera_id: str, recipe: str) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["camera_id"] = camera_id
    obj["recipe"] = recipe
    return obj


def create_sample_sphere(
    collection: bpy.types.Collection,
    name: str,
    location: tuple[float, float, float],
    assigned: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=6.5, location=location)
    obj = bpy.context.object
    obj.name = name
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.append(assigned)
    obj["gate07_review_sample"] = True
    return obj


def create_text(
    collection: bpy.types.Collection,
    name: str,
    body: str,
    location: tuple[float, float, float],
    camera: bpy.types.Object,
    size: float,
    assigned: bpy.types.Material,
) -> bpy.types.Object:
    data = bpy.data.curves.new(f"{name}_Curve", "FONT")
    data.body = body
    data.align_x = "CENTER"
    data.align_y = "CENTER"
    data.size = size
    data.extrude = 0.012
    obj = bpy.data.objects.new(name, data)
    collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = camera.rotation_euler
    obj.data.materials.append(assigned)
    obj["gate07_review_annotation"] = True
    return obj


def render(scene: bpy.types.Scene, camera: bpy.types.Object, output_name: str, width: int, height: int) -> None:
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(OUTPUT / output_name)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def material_parameters(assigned: bpy.types.Material) -> dict:
    shader = assigned.node_tree.nodes.get("Principled BSDF")
    def value(name: str, fallback=None):
        socket = shader.inputs.get(name)
        return socket.default_value if socket is not None else fallback
    return {
        "baseColor": list(value("Base Color")),
        "metallic": value("Metallic"),
        "roughness": value("Roughness"),
        "ior": value("IOR"),
        "coatWeight": value("Coat Weight"),
        "coatRoughness": value("Coat Roughness"),
        "transmissionWeight": value("Transmission Weight"),
    }


def main() -> None:
    source_hash_before = file_sha256(SOURCE_BLEND)
    geometry_report = json.loads(SOURCE_GEOMETRY_REPORT.read_text(encoding="utf-8"))
    if geometry_report["geometryIdentity"]["evaluatedDigest"] != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Approved Gate 06 geometry digest mismatch.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "07-material"
    scene["material_revision"] = 1
    scene["source_gate06_sha256"] = source_hash_before
    scene["mechanism_rotation_range_degrees"] = 360
    scene["mechanism_detent_step_degrees"] = 12
    scene["mechanism_detent_count"] = 30
    scene["mechanism_delivery_state"] = "specified-only-runtime-and-hardware-pending"

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

    geometry_before = evaluated_geometry_digest(model_objects)
    if geometry_before != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Gate 07 input does not match approved Gate 06 geometry.")
    lower_matrix = [list(row) for row in lower.matrix_world]
    upper_matrix = [list(row) for row in upper.matrix_world]
    envelope_matrix = [list(row) for row in envelope.matrix_world]
    materials = assign_material_zones(lower, upper)
    geometry_after_materials = evaluated_geometry_digest(model_objects)

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
    neutral_lights = [
        create_area_light("M07_Key_Softbox", (62.0, -72.0, 78.0), 48000.0, 52.0, Vector((0, 0, 0))),
        create_area_light("M07_Fill_Softbox", (-58.0, -18.0, 42.0), 26000.0, 46.0, Vector((0, 0, 1))),
        create_area_light("M07_Rim_Strip", (12.0, 74.0, 54.0), 42000.0, 34.0, Vector((0, 2, 0))),
    ]
    world = scene.world or bpy.data.worlds.new("M07_NeutralWorld")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.065, 0.080, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.72

    ground = bpy.data.objects.get("PresentationGround")
    if ground:
        ground.hide_render = False
        ground_mat = bpy.data.materials.new("M07_NeutralGround")
        ground_mat.use_nodes = True
        shader = ground_mat.node_tree.nodes["Principled BSDF"]
        set_input(shader, "Base Color", (0.025, 0.030, 0.038, 1.0))
        set_input(shader, "Metallic", 0.0)
        set_input(shader, "Roughness", 0.46)
        ground.data.materials.clear()
        ground.data.materials.append(ground_mat)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"

    board_camera = create_camera(
        "M07_MaterialBoardCamera",
        (138.0, -158.0, 108.0),
        Vector((15.0, 2.0, 5.0)),
        58.0,
        "material-board",
        "neutral-reveal-three-zone-board",
    )
    closeup_camera = create_camera(
        "M07_MaterialCloseupCamera",
        (76.0, -84.0, 48.0),
        Vector((0.0, -2.0, 0.5)),
        72.0,
        "material-closeup",
        "neutral-reveal-seam-and-face-closeup",
    )

    review_collection = bpy.data.collections.new("Gate07_MaterialBoardSamples")
    scene.collection.children.link(review_collection)
    sample_locations = {
        "lower-polished-silver-alloy": (37.0, -15.0, 7.0),
        "upper-dark-coated-frame": (39.0, 3.0, 10.0),
        "upper-smoked-clear-face": (38.0, 21.0, 13.0),
    }
    samples = [
        create_sample_sphere(review_collection, f"M07_Sample_{zone_id}", sample_locations[zone_id], materials[zone_id])
        for zone_id in MATERIAL_ZONES
    ]
    label_material = bpy.data.materials.new("M07_Label")
    label_material.use_nodes = True
    label_shader = label_material.node_tree.nodes["Principled BSDF"]
    set_input(label_shader, "Base Color", (0.90, 0.94, 1.0, 1.0))
    set_input(label_shader, "Roughness", 0.35)
    set_input(label_shader, "Emission Color", (0.90, 0.94, 1.0, 1.0))
    set_input(label_shader, "Emission Strength", 2.0)
    labels = [
        create_text(review_collection, "M07_Label_Silver", "POLISHED SILVER\nvisual approximation", (37.0, -15.0, 18.0), board_camera, 1.05, label_material),
        create_text(review_collection, "M07_Label_Dark", "DARK COATED METAL\nvisual approximation", (39.0, 3.0, 21.0), board_camera, 1.05, label_material),
        create_text(review_collection, "M07_Label_Clear", "SMOKED CLEAR FACE\nvisual approximation", (38.0, 21.0, 24.0), board_camera, 1.05, label_material),
    ]
    render(scene, board_camera, "neutral-pbr-material-board.png", 1200, 900)
    for obj in samples + labels:
        obj.hide_render = True
    render(scene, closeup_camera, "neutral-pbr-material-closeup.png", 1000, 1000)

    geometry_final = evaluated_geometry_digest(model_objects)
    source_hash_after = file_sha256(SOURCE_BLEND)
    material_slots = {
        lower.name: [slot.material.name for slot in lower.material_slots],
        upper.name: [slot.material.name for slot in upper.material_slots],
    }
    upper_face_assignments = {
        "topCapFaceCount": sum(1 for polygon in upper.data.polygons if polygon.material_index == 1),
        "frameFaceCount": sum(1 for polygon in upper.data.polygons if polygon.material_index == 0),
    }
    visible_model_meshes = [obj.name for obj in root.children_recursive if obj.type == "MESH" and not obj.hide_render]
    hidden_mechanism_mesh_count = sum(
        1 for obj in root.children_recursive if obj.type == "MESH" and "mechanism" in obj.name.lower()
    )
    animated = [obj.name for obj in root.children_recursive if obj.animation_data or obj.constraints]
    geometry_unchanged = geometry_before == geometry_after_materials == geometry_final == EXPECTED_GEOMETRY_DIGEST
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 1,
        "sourceGate06": {
            "geometryRevision": 1,
            "blendPath": str(SOURCE_BLEND.relative_to(OUTPUT.parents[7])),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "evaluatedGeometryDigest": EXPECTED_GEOMETRY_DIGEST,
        },
        "geometryPreservation": {
            "digestBefore": geometry_before,
            "digestAfterMaterialAssignment": geometry_after_materials,
            "digestAfterRenders": geometry_final,
            "unchanged": geometry_unchanged,
            "boundsMm": [50.0, 31.0, 12.0],
            "axisPointWorldMm": AXIS_POINT_MM,
            "lowerMatrixUnchanged": [list(row) for row in lower.matrix_world] == lower_matrix,
            "upperMatrixUnchanged": [list(row) for row in upper.matrix_world] == upper_matrix,
            "envelopeMatrixUnchanged": [list(row) for row in envelope.matrix_world] == envelope_matrix,
            "envelopeType": envelope.type,
            "envelopeHideRender": envelope.hide_render,
            "envelopeGeometry": envelope["geometry"],
            "smoothProfileSegmentsPerSemicircle": upper["arc_segments_per_semicircle"],
            "visibleModelMeshes": visible_model_meshes,
            "hiddenMechanismMeshCount": hidden_mechanism_mesh_count,
            "artworkOrnamentGeometryCount": 0,
            "animatedOrConstrainedObjects": animated,
            "pass": (
                geometry_unchanged
                and [list(row) for row in lower.matrix_world] == lower_matrix
                and [list(row) for row in upper.matrix_world] == upper_matrix
                and [list(row) for row in envelope.matrix_world] == envelope_matrix
                and envelope.type == "EMPTY"
                and envelope.hide_render
                and envelope["geometry"] == "none"
                and upper["arc_segments_per_semicircle"] == 256
                and set(visible_model_meshes) == {"LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"}
                and hidden_mechanism_mesh_count == 0
                and not animated
            ),
        },
        "materialZones": {
            zone_id: {
                **zone,
                "actualPbr": material_parameters(materials[zone_id]),
            }
            for zone_id, zone in MATERIAL_ZONES.items()
        },
        "materialAssignments": {
            "slots": material_slots,
            "upperFaces": upper_face_assignments,
            "zoneCount": len(MATERIAL_ZONES),
            "pass": (
                material_slots[lower.name] == ["M07_Lower_PolishedSilver_Approx"]
                and material_slots[upper.name] == [
                    "M07_Upper_DarkCoatedMetal_Approx",
                    "M07_Upper_SmokedClearFace_Approx",
                ]
                and upper_face_assignments == {"topCapFaceCount": 1, "frameFaceCount": 514}
            ),
        },
        "sourceLinks": SOURCE_LINKS,
        "sourceClaimIds": ["slider-analysis-claim-material-language"],
        "uncertaintyPolicy": {
            "pbrValuesAreProductionSpecifications": False,
            "artworkOrnamentApproved": False,
            "hiddenRatchetConstructionKnown": False,
            "unknownInternalParts": ["teeth", "pawls", "balls", "coupling", "coating-stack", "transparent-layer-thickness"],
            "note": "PBR values are neutral lookdev approximations. They cannot establish alloy, coating, resin/glass, or internal mechanism production specifications.",
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
            "worldStrength": 0.72,
            "finalLightingOrEnvironment": False,
            "materialBoard": "neutral-pbr-material-board.png",
            "materialCloseup": "neutral-pbr-material-closeup.png",
        },
        "scope": {
            "geometryChanged": False,
            "artworkAdded": False,
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
        report["uncertaintyPolicy"]["pbrValuesAreProductionSpecifications"] is False,
        report["uncertaintyPolicy"]["hiddenRatchetConstructionKnown"] is False,
        report["mechanismDecisionMetadata"]["detentCount"] == 30,
        report["mechanismDecisionMetadata"]["physicalAndHapticConsumeSameSetting"] is True,
        report["mechanismDecisionMetadata"]["runtimeChanged"] is False,
        report["neutralReveal"]["finalLightingOrEnvironment"] is False,
        not any(report["scope"].values()),
    ]
    MATERIAL_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not all(required):
        raise RuntimeError(json.dumps(report, indent=2))

    for obj in samples + labels:
        obj.hide_render = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
