#!/usr/bin/env python3
"""Build Gate 09 rev 2 slide-open environment evidence at +21 mm."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
SOURCE_BLEND = ROOT.parents[0] / "rev-001/magnetic-slide-tile-environment-r001.blend"
SOURCE_REPORT = ROOT.parents[0] / "rev-001/environment-validation.json"
OUTPUT_BLEND = ROOT / "magnetic-slide-tile-environment-open-r002.blend"
REPORT = ROOT / "open-environment-validation.json"
OPEN_TRAVEL_MM = 21.0
EXPECTED_CLOSED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
SHIPPING_MATERIALS = [
    "M07R7_DaylightNeutralPolishedSilver",
    "M07R7_BloodRedCrystal_WideBorder_Upper",
    "M07R7_BloodRedCrystal_WideBorder_Lower",
]
MODEL_OBJECTS = ["LowerBody_Fixed_CleanPlane", "UpperCapsule_Moving"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serializable(value):
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    try:
        return [round(float(component), 9) for component in value]
    except (TypeError, ValueError):
        return str(value)


def local_mesh_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        mesh = obj.data
        digest.update(obj.name.encode())
        for vertex in mesh.vertices:
            digest.update(f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode())
        for polygon in mesh.polygons:
            digest.update((",".join(str(index) for index in polygon.vertices) + ";").encode())
    return digest.hexdigest()


def material_signature(material: bpy.types.Material) -> str:
    nodes = []
    for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
        entry = {
            "name": node.name,
            "type": node.bl_idname,
            "inputs": {
                socket.name: serializable(socket.default_value)
                for socket in node.inputs
                if hasattr(socket, "default_value")
            },
        }
        if node.bl_idname == "ShaderNodeTexImage" and node.image:
            entry["image"] = {
                "filepath": bpy.path.abspath(node.image.filepath),
                "interpolation": node.interpolation,
            }
        nodes.append(entry)
    links = sorted(
        (
            link.from_node.name,
            link.from_socket.name,
            link.to_node.name,
            link.to_socket.name,
        )
        for link in material.node_tree.links
    )
    payload = json.dumps({"nodes": nodes, "links": links}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def world_signature(world: bpy.types.World) -> str:
    nodes = []
    for node in sorted(world.node_tree.nodes, key=lambda item: item.name):
        nodes.append({
            "name": node.name,
            "type": node.bl_idname,
            "inputs": {
                socket.name: serializable(socket.default_value)
                for socket in node.inputs
                if hasattr(socket, "default_value")
            },
        })
    links = sorted(
        (
            link.from_node.name,
            link.from_socket.name,
            link.to_node.name,
            link.to_socket.name,
        )
        for link in world.node_tree.links
    )
    payload = json.dumps({"nodes": nodes, "links": links}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def matrix(obj: bpy.types.Object) -> list[list[float]]:
    return [[round(float(value), 9) for value in row] for row in obj.matrix_world]


def camera_signature(obj: bpy.types.Object) -> dict:
    return {
        "name": obj.name,
        "matrixWorld": matrix(obj),
        "lensMm": float(obj.data.lens),
        "sensorWidthMm": float(obj.data.sensor_width),
    }


def light_signature(obj: bpy.types.Object) -> dict:
    return {
        "name": obj.name,
        "matrixWorld": matrix(obj),
        "type": obj.data.type,
        "energy": float(obj.data.energy),
        "size": float(obj.data.size),
        "color": [float(component) for component in obj.data.color],
        "kelvin": int(obj["color_temperature_kelvin"]),
        "hideRender": bool(obj.hide_render),
    }


def point_camera(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    point_camera(obj, target)
    obj["gate09_open_camera"] = True
    return obj


def neutral_world() -> bpy.types.World:
    world = bpy.data.worlds.new("M09R2_NeutralControlWorld")
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.name = "Background"
    background.inputs["Color"].default_value = (0.24, 0.24, 0.24, 1.0)
    background.inputs["Strength"].default_value = 0.85
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
    return world


def neutral_ground_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M09R2_NeutralControlGround")
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (0.08, 0.08, 0.08, 1.0)
    shader.inputs["Metallic"].default_value = 0.0
    shader.inputs["Roughness"].default_value = 0.46
    shader.inputs["Emission Strength"].default_value = 0.0
    return material


def set_pose(translation: bpy.types.Object, travel_mm: float) -> None:
    translation.location = (0.0, travel_mm, 0.0)
    translation.rotation_euler = (0.0, 0.0, 0.0)
    translation.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()


def render(scene: bpy.types.Scene, camera_obj: bpy.types.Object, filename: str, width: int, height: int) -> None:
    scene.camera = camera_obj
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(ROOT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def main() -> None:
    source_hash_before = sha256(SOURCE_BLEND)
    source_report = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    if not source_report["pass"] or source_report["environmentRevision"] != 1:
        raise RuntimeError("Gate 09 rev 1 source is invalid.")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "09-environment"
    scene["environment_revision"] = 2
    scene["source_gate09_rev1_status"] = "rejected-incomplete-no-open-view"
    scene["open_travel_mm"] = OPEN_TRAVEL_MM
    scene["open_axis"] = "+Y"
    scene["open_rotation_degrees"] = 0.0
    scene["unity_change_authorized"] = False
    scene["gate10_authorized"] = False

    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    model_objects = [lower, upper]
    ground = bpy.data.objects["PresentationGround"]
    shipping_world = scene.world
    shipping_world.name = "M09R2_ShippingAdaptiveWorld"
    shipping_ground = ground.data.materials[0]
    neutral_control_world = neutral_world()
    neutral_ground = neutral_ground_material()

    local_mesh_before = local_mesh_hash(model_objects)
    material_before = {
        name: material_signature(bpy.data.materials[name])
        for name in SHIPPING_MATERIALS
    }
    material_assignments_before = {
        obj.name: [slot.material.name for slot in obj.material_slots]
        for obj in model_objects
    }
    lower_matrix_before = matrix(lower)
    translation_matrix_closed = matrix(translation)
    shipping_world_before = world_signature(shipping_world)
    shipping_ground_signature = material_signature(shipping_ground)
    lights = sorted(
        [
            obj for obj in bpy.data.objects
            if obj.type == "LIGHT" and obj.get("gate08_controlled_lighting")
        ],
        key=lambda item: item.name,
    )
    light_before = {obj.name: light_signature(obj) for obj in lights}
    reflection_cards_before = {
        obj.name: matrix(obj)
        for obj in bpy.data.objects
        if obj.get("gate08_reflection_card")
    }
    artwork_images = {
        "upper": bpy.data.node_groups["Artwork_Upper"].nodes["Artwork_Upper_ExternalMask"].image,
        "lower": bpy.data.node_groups["Artwork_Lower"].nodes["Artwork_Lower_ExternalMask"].image,
    }
    artwork = {
        key: {
            "filepath": str(Path(bpy.path.abspath(image.filepath)).relative_to(REPO)),
            "sha256": sha256(Path(bpy.path.abspath(image.filepath))),
            "nodeGroup": f"Artwork_{key.title()}",
        }
        for key, image in artwork_images.items()
    }

    target = (0.0, 10.5, 2.0)
    open_hero = camera("M09R2_OpenHeroCamera", (92.0, -154.0, 76.0), target, 78.0)
    open_oblique = camera("M09R2_OpenObliqueCamera", (-112.0, -132.0, 68.0), target, 76.0)
    open_top = camera("M09R2_OpenTopCamera", (48.0, -42.0, 195.0), (0.0, 10.5, 0.0), 76.0)
    open_layer = camera("M09R2_OpenLayerCamera", (104.0, -138.0, 43.0), (0.0, 7.0, 0.0), 86.0)
    bpy.context.view_layer.update()
    camera_signatures = {
        obj.name: camera_signature(obj)
        for obj in [open_hero, open_oblique, open_top, open_layer]
    }

    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.exposure = 0.0
    scene.view_settings.look = "AgX - Medium High Contrast"
    set_pose(translation, OPEN_TRAVEL_MM)
    open_translation_matrix = matrix(translation)
    open_upper_matrix = matrix(upper)

    scene.world = neutral_control_world
    ground.data.materials[0] = neutral_ground
    render(scene, open_hero, "open-neutral-hero.png", 1600, 1200)
    render(scene, open_layer, "open-neutral-layer-closeup.png", 1600, 1100)

    scene.world = shipping_world
    ground.data.materials[0] = shipping_ground
    render(scene, open_hero, "open-shipping-hero.png", 1600, 1200)
    render(scene, open_oblique, "open-shipping-oblique.png", 1600, 1200)
    render(scene, open_top, "open-shipping-top.png", 1500, 1500)
    render(scene, open_layer, "open-shipping-layer-closeup.png", 1600, 1100)

    sequence = []
    for index, travel in enumerate([0.0, 7.0, 14.0, 21.0]):
        set_pose(translation, travel)
        filename = f"sequence-{index:02d}-{int(travel):02d}mm.png"
        render(scene, open_hero, filename, 1200, 900)
        sequence.append({
            "frame": index,
            "travelMm": travel,
            "path": filename,
            "translation": list(translation.location),
            "rotationDegrees": [0.0, 0.0, 0.0],
            "lowerMatrix": matrix(lower),
        })
    set_pose(translation, OPEN_TRAVEL_MM)

    local_mesh_after = local_mesh_hash(model_objects)
    material_after = {
        name: material_signature(bpy.data.materials[name])
        for name in SHIPPING_MATERIALS
    }
    material_assignments_after = {
        obj.name: [slot.material.name for slot in obj.material_slots]
        for obj in model_objects
    }
    light_after = {obj.name: light_signature(obj) for obj in lights}
    reflection_cards_after = {
        obj.name: matrix(obj)
        for obj in bpy.data.objects
        if obj.get("gate08_reflection_card")
    }
    shipping_world_after = world_signature(shipping_world)
    source_hash_after = sha256(SOURCE_BLEND)
    emission = {}
    for name in SHIPPING_MATERIALS:
        shader = next(
            node for node in bpy.data.materials[name].node_tree.nodes
            if node.bl_idname == "ShaderNodeBsdfPrincipled"
        )
        emission[name] = float(shader.inputs["Emission Strength"].default_value)

    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 2,
        "sourceRevision": {
            "revision": 1,
            "status": "rejected-incomplete",
            "reason": "Gate 09 rev 1 never showed the slide-open appearance.",
            "blendPath": str(SOURCE_BLEND.relative_to(REPO)),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
        },
        "approvedContracts": {
            "dimensionsMm": [50.0, 31.0, 12.0],
            "closedGeometryDigest": EXPECTED_CLOSED_GEOMETRY_DIGEST,
            "openTravelMm": OPEN_TRAVEL_MM,
            "openAxis": "+Y",
            "openRotationDegrees": 0.0,
            "fixedLowerPlane": True,
            "concealedMechanism": True,
            "pointAxisWorldMm": [0.0, -9.5, 0.0],
        },
        "pose": {
            "translationMatrixClosed": translation_matrix_closed,
            "translationMatrixOpen": open_translation_matrix,
            "upperMatrixOpen": open_upper_matrix,
            "translationLocationMm": list(translation.location),
            "translationRotationRadians": list(translation.rotation_euler),
            "translationScale": list(translation.scale),
            "lowerMatrixBefore": lower_matrix_before,
            "lowerMatrixAfter": matrix(lower),
            "pivotWorldMm": list(pivot.matrix_world.translation),
            "sequence": sequence,
        },
        "invariants": {
            "localMeshHashBefore": local_mesh_before,
            "localMeshHashAfter": local_mesh_after,
            "localMeshUnchanged": local_mesh_before == local_mesh_after,
            "materialHashesBefore": material_before,
            "materialHashesAfter": material_after,
            "materialsUnchanged": material_before == material_after,
            "materialAssignmentsBefore": material_assignments_before,
            "materialAssignmentsAfter": material_assignments_after,
            "materialAssignmentsUnchanged": material_assignments_before == material_assignments_after,
            "lightRigBefore": light_before,
            "lightRigAfter": light_after,
            "lightRigUnchanged": light_before == light_after,
            "reflectionCardsBefore": reflection_cards_before,
            "reflectionCardsAfter": reflection_cards_after,
            "reflectionCardsUnchanged": reflection_cards_before == reflection_cards_after,
            "shippingWorldHashBefore": shipping_world_before,
            "shippingWorldHashAfter": shipping_world_after,
            "shippingWorldUnchanged": shipping_world_before == shipping_world_after,
            "shippingGroundHash": shipping_ground_signature,
            "shippingEmissionStrengths": emission,
            "shippingEmissionZero": all(value == 0.0 for value in emission.values()),
            "artwork": artwork,
            "independentArtworkSlots": artwork["upper"]["nodeGroup"] != artwork["lower"]["nodeGroup"],
            "hiddenEnvelope": {
                "type": envelope.type,
                "hideRender": envelope.hide_render,
                "geometry": envelope["geometry"],
            },
        },
        "comparison": {
            "neutralShippingCamera": camera_signatures["M09R2_OpenHeroCamera"],
            "neutralShippingPose": {
                "travelMm": OPEN_TRAVEL_MM,
                "rotationDegrees": 0.0,
            },
            "neutralWorld": {
                "linearRgb": [0.24, 0.24, 0.24],
                "strength": 0.85,
                "groundMaterial": neutral_ground.name,
            },
            "shippingWorld": source_report["shippingLikeEnvironment"],
            "sameLightRig": True,
            "sameExposureEv": 0.0,
            "sameWhiteBalanceKelvin": 6504,
            "sameWhiteBalanceTint": 10,
        },
        "cameras": camera_signatures,
        "outputs": {
            "neutralOpenHero": "open-neutral-hero.png",
            "shippingOpenHero": "open-shipping-hero.png",
            "shippingOpenOblique": "open-shipping-oblique.png",
            "shippingOpenTop": "open-shipping-top.png",
            "neutralLayerCloseup": "open-neutral-layer-closeup.png",
            "shippingLayerCloseup": "open-shipping-layer-closeup.png",
            "sequence": [item["path"] for item in sequence],
        },
        "scope": {
            "gate10Entered": False,
            "exportPerformed": False,
            "geometryChanged": False,
            "lodCreated": False,
            "unityChanged": False,
            "runtimeOrHapticsChanged": False,
            "buildInstallOrPhonePush": False,
        },
    }
    checks = {
        "sourceRevisionImmutable": report["sourceRevision"]["unchanged"],
        "exactOpenTravel": list(translation.location) == [0.0, 21.0, 0.0],
        "zeroRotation": all(abs(value) < 1e-9 for value in translation.rotation_euler),
        "fixedLowerMatrix": report["pose"]["lowerMatrixBefore"] == report["pose"]["lowerMatrixAfter"],
        "geometryUnchanged": report["invariants"]["localMeshUnchanged"],
        "materialsUnchanged": report["invariants"]["materialsUnchanged"]
        and report["invariants"]["materialAssignmentsUnchanged"],
        "approvedLightingUnchanged": report["invariants"]["lightRigUnchanged"],
        "approvedEnvironmentUnchanged": report["invariants"]["shippingWorldUnchanged"],
        "reflectionCardsUnchanged": report["invariants"]["reflectionCardsUnchanged"],
        "independentArtworkSlots": report["invariants"]["independentArtworkSlots"]
        and report["invariants"]["artwork"]["upper"]["sha256"] == report["invariants"]["artwork"]["lower"]["sha256"],
        "mechanismConcealed": report["invariants"]["hiddenEnvelope"] == {
            "type": "EMPTY",
            "hideRender": True,
            "geometry": "none",
        },
        "shippingEmissionZero": report["invariants"]["shippingEmissionZero"],
        "sequenceEndsAtExactOpenPose": sequence[0]["travelMm"] == 0.0
        and sequence[-1]["travelMm"] == 21.0
        and all(item["rotationDegrees"] == [0.0, 0.0, 0.0] for item in sequence),
        "requiredOutputs": all(
            (ROOT / filename).exists()
            for filename in [
                "open-neutral-hero.png",
                "open-shipping-hero.png",
                "open-shipping-oblique.png",
                "open-shipping-top.png",
                "open-neutral-layer-closeup.png",
                "open-shipping-layer-closeup.png",
                *[item["path"] for item in sequence],
            ]
        ),
        "gate09Only": not any(report["scope"].values()),
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    scene.camera = open_hero
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
