#!/usr/bin/env python3
"""Build Gate 08 lighting evidence from approved Gate 07 rev 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
SOURCE_BLEND = ROOT.parents[1] / "07-material/rev-007/magnetic-slide-tile-material-r007.blend"
SOURCE_MATERIAL_REPORT = ROOT.parents[1] / "07-material/rev-007/material-validation.json"
UNITY_PLAN = ROOT / "unity-reflection-plan.json"
OUTPUT_BLEND = ROOT / "magnetic-slide-tile-lighting-r001.blend"
REPORT = ROOT / "lighting-validation.json"
EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
EXPECTED_MOTIF_SHA256 = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def area_light(name: str, location: tuple[float, float, float], energy: float, size: float, color: tuple[float, float, float], kelvin: int, target: Vector) -> bpy.types.Object:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate08_controlled_lighting"] = True
    obj["color_temperature_kelvin"] = kelvin
    obj["target_mm"] = list(target)
    return obj


def camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], lens: float, camera_id: str) -> bpy.types.Object:
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36.0
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, Vector(target))
    obj["camera_id"] = camera_id
    obj["target_mm"] = list(target)
    obj["gate08_authored_camera"] = True
    return obj


def principled_material(name: str, base_color: tuple[float, float, float, float], metallic: float, roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    set_input(shader, "Base Color", base_color)
    set_input(shader, "Metallic", metallic)
    set_input(shader, "Roughness", roughness)
    set_input(shader, "Emission Color", (0.0, 0.0, 0.0, 1.0))
    set_input(shader, "Emission Strength", 0.0)
    material["gate08_technical_override"] = True
    return material


def unlit_material(name: str, color_socket=None, color: tuple[float, float, float, float] | None = None) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_fake_user = True
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    if color_socket is None:
        emission.inputs["Color"].default_value = color or (0.5, 0.5, 0.5, 1.0)
    else:
        links.new(color_socket, emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_aov_only"] = True
    material["not_shipping_material"] = True
    return material


def normal_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M08R1_Pass_Normal")
    material.use_fake_user = True
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    geometry = nodes.new("ShaderNodeNewGeometry")
    multiply = nodes.new("ShaderNodeVectorMath")
    multiply.operation = "SCALE"
    multiply.inputs[3].default_value = 0.5
    add = nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    add.inputs[1].default_value = (0.5, 0.5, 0.5)
    emission = nodes.new("ShaderNodeEmission")
    links.new(geometry.outputs["Normal"], multiply.inputs[0])
    links.new(multiply.outputs["Vector"], add.inputs[0])
    links.new(add.outputs["Vector"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_aov_only"] = True
    material["not_shipping_material"] = True
    return material


def depth_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M08R1_Pass_Depth")
    material.use_fake_user = True
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    camera_data = nodes.new("ShaderNodeCameraData")
    mapping = nodes.new("ShaderNodeMapRange")
    mapping.inputs["From Min"].default_value = 115.0
    mapping.inputs["From Max"].default_value = 210.0
    mapping.inputs["To Min"].default_value = 1.0
    mapping.inputs["To Max"].default_value = 0.06
    mapping.clamp = True
    emission = nodes.new("ShaderNodeEmission")
    links.new(camera_data.outputs["View Z Depth"], mapping.inputs["Value"])
    links.new(mapping.outputs["Result"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_aov_only"] = True
    material["not_shipping_material"] = True
    material["depth_near_mm"] = 115.0
    material["depth_far_mm"] = 210.0
    return material


def roughness_artwork_material(name: str, source: bpy.types.Material) -> bpy.types.Material:
    material = source.copy()
    material.name = name
    material.use_fake_user = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = next(node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
    roughness_source = shader.inputs["Roughness"].links[0].from_socket
    output = nodes.get("Material Output") or next(node for node in nodes if node.bl_idname == "ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    combine = nodes.new("ShaderNodeCombineColor")
    combine.mode = "RGB"
    for channel in ("Red", "Green", "Blue"):
        links.new(roughness_source, combine.inputs[channel])
    links.new(combine.outputs["Color"], emission.inputs["Color"])
    for link in list(output.inputs["Surface"].links):
        links.remove(link)
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["gate08_technical_aov_only"] = True
    material["not_shipping_material"] = True
    return material


def reflection_card(name: str, location: tuple[float, float, float], rotation: tuple[float, float, float], scale: tuple[float, float, float], color: tuple[float, float, float, float]) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=2, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(principled_material(f"{name}_Material", color, 0.0, 0.34))
    obj["gate08_reflection_card"] = True
    obj["visible_to_camera"] = False
    obj.visible_camera = False
    return obj


def render(scene: bpy.types.Scene, target_camera: bpy.types.Object, filename: str, width: int = 1400, height: int = 1000) -> None:
    scene.camera = target_camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(ROOT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def main() -> None:
    source_hash_before = sha256(SOURCE_BLEND)
    source_report = json.loads(SOURCE_MATERIAL_REPORT.read_text(encoding="utf-8"))
    unity_plan = json.loads(UNITY_PLAN.read_text(encoding="utf-8"))
    if not source_report["pass"] or source_report["materialRevision"] != 7:
        raise RuntimeError("Gate 07 rev 7 source material is not valid.")
    if source_report["geometryPreservation"]["digestAfterRenders"] != EXPECTED_GEOMETRY_DIGEST:
        raise RuntimeError("Approved geometry digest mismatch.")
    if source_report["artworkLayers"]["lineage"]["sourceSha256"] != EXPECTED_MOTIF_SHA256:
        raise RuntimeError("Approved motif lineage mismatch.")
    if not unity_plan["pass"] or unity_plan["deliveryState"] != "specified-only-not-integrated":
        raise RuntimeError("Unity reflection specification is invalid.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 1
    scene["source_gate07_material_revision"] = 7
    scene["source_gate07_sha256"] = source_hash_before
    scene["geometry_change_authorized"] = False
    scene["material_change_authorized"] = False
    scene["environment_composition_deferred_to_gate09"] = True
    scene["unity_reflection_delivery_state"] = "specified-only-not-integrated"
    scene["shipping_material_emission"] = 0.0

    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    model_objects = [lower, upper]
    if tuple(translation.location) != (0.0, 0.0, 0.0) or tuple(pivot.location) != (0.0, -9.5, 0.0):
        raise RuntimeError("Closed pose or point-axis semantics changed.")
    before = geometry_digest(model_objects)
    matrices = {obj.name: [list(row) for row in obj.matrix_world] for obj in [lower, upper, envelope]}
    material_slots_before = {
        obj.name: [slot.material for slot in obj.material_slots]
        for obj in model_objects
    }
    shipping_materials = [material for values in material_slots_before.values() for material in values]
    shipping_emissions = {}
    for material in shipping_materials:
        shader = next(node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
        shipping_emissions[material.name] = shader.inputs["Emission Strength"].default_value
    if any(value != 0.0 for value in shipping_emissions.values()):
        raise RuntimeError("Approved shipping materials must keep emission at zero.")

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
        if obj.type == "CAMERA":
            obj.hide_render = True

    world = scene.world or bpy.data.worlds.new("M08R1_NeutralStudioWorld")
    scene.world = world
    world.use_nodes = True
    world_color = (0.24, 0.24, 0.24, 1.0)
    world_strength = 0.85
    world.node_tree.nodes["Background"].inputs["Color"].default_value = world_color
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = world_strength

    light_specs = [
        ("M08R1_Key_D65_Softbox", (54, -72, 98), 62000, 52, (1.0, 0.994, 0.97), 6504, (0, 0, 3)),
        ("M08R1_Fill_Neutral", (-62, -22, 62), 30000, 46, (1.0, 0.965, 0.92), 5600, (0, 0, 3)),
        ("M08R1_Rim_SilverStrip", (34, 72, 68), 48000, 38, (1.0, 0.997, 0.985), 6400, (0, 2, 4)),
        ("M08R1_FaceReveal", (-12, -28, 112), 23000, 30, (1.0, 0.98, 0.94), 5900, (0, 0, 4)),
    ]
    lights = [
        area_light(name, location, power, size, color, kelvin, Vector(target))
        for name, location, power, size, color, kelvin, target in light_specs
    ]
    for light in lights:
        light.hide_render = False

    ground = bpy.data.objects.get("PresentationGround")
    ground_material_before = list(ground.data.materials) if ground else []
    if ground:
        ground.hide_render = False
        ground_material = principled_material("M08R1_NeutralGround", (0.08, 0.08, 0.08, 1.0), 0.0, 0.46)
        ground.data.materials.clear()
        ground.data.materials.append(ground_material)

    cards = [
        reflection_card("M08R1_WhiteCard_Left", (-52, -95, 40), (1.570796, 0, 0.18), (18, 32, 1), (0.80, 0.80, 0.80, 1.0)),
        reflection_card("M08R1_WhiteCard_Right", (58, -88, 34), (1.570796, 0, -0.18), (14, 30, 1), (0.80, 0.80, 0.80, 1.0)),
        reflection_card("M08R1_WhiteCard_Camera", (-18, -180, 46), (1.570796, 0, 0), (34, 38, 1), (0.80, 0.80, 0.80, 1.0)),
        reflection_card("M08R1_BlackCard_NegativeFill", (44, -148, 44), (1.570796, 0, 0), (16, 32, 1), (0.008, 0.008, 0.008, 1.0)),
    ]

    camera_specs = {
        "hero": ((88, -132, 74), (0, 0, 4), 72),
        "left-oblique": ((-96, -122, 66), (0, 0, 4), 74),
        "right-oblique": ((98, -120, 64), (0, 0, 4), 74),
        "low": ((104, -146, 25), (0, 0, 4), 78),
        "beauty": ((76, -138, 58), (0, 0, 4), 82),
        "open-side": ((102, -112, 46), (0, 8, 4), 78),
    }
    cameras = {
        camera_id: camera(f"M08R1_{camera_id.replace('-', '_').title()}Camera", location, target, lens, camera_id)
        for camera_id, (location, target, lens) in camera_specs.items()
    }

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 6504
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 10

    render(scene, cameras["hero"], "hero.png", 1500, 1100)
    render(scene, cameras["left-oblique"], "left-oblique.png")
    render(scene, cameras["right-oblique"], "right-oblique.png")
    render(scene, cameras["low"], "low-angle.png")
    render(scene, cameras["beauty"], "pass-beauty.png", 1600, 1200)

    translation.location.y = 21.0
    bpy.context.view_layer.update()
    render(scene, cameras["open-side"], "open-side-reflection.png", 1500, 1100)
    translation.location.y = 0.0
    bpy.context.view_layer.update()

    view_layer = scene.view_layers[0]
    view_layer.material_override = principled_material("M08R1_Pass_Clay", (0.46, 0.47, 0.49, 1.0), 0.0, 0.88)
    render(scene, cameras["beauty"], "pass-clay.png")
    view_layer.material_override = normal_material()
    render(scene, cameras["beauty"], "pass-normal.png")
    view_layer.material_override = depth_material()
    render(scene, cameras["beauty"], "pass-depth.png")
    view_layer.material_override = None

    rough_silver = unlit_material("M08R1_Pass_RoughnessSilver", color=(0.03, 0.03, 0.03, 1.0))
    rough_upper = roughness_artwork_material("M08R1_Pass_RoughnessUpper", material_slots_before[upper.name][1])
    rough_lower = roughness_artwork_material("M08R1_Pass_RoughnessLower", material_slots_before[lower.name][1])
    lower.material_slots[0].material = rough_silver
    lower.material_slots[1].material = rough_lower
    upper.material_slots[0].material = rough_silver
    upper.material_slots[1].material = rough_upper
    render(scene, cameras["beauty"], "pass-roughness.png")
    for obj in model_objects:
        for index, material in enumerate(material_slots_before[obj.name]):
            obj.material_slots[index].material = material

    after = geometry_digest(model_objects)
    source_hash_after = sha256(SOURCE_BLEND)
    matrices_unchanged = all(
        [list(row) for row in obj.matrix_world] == matrices[obj.name]
        for obj in [lower, upper, envelope]
    )
    material_assignments_restored = all(
        [slot.material for slot in obj.material_slots] == material_slots_before[obj.name]
        for obj in model_objects
    )
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "sourceGate07": {
            "materialRevision": 7,
            "blendPath": str(SOURCE_BLEND.relative_to(REPO)),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "approvalWording": "可以",
        },
        "geometry": {
            "digestBefore": before,
            "digestAfter": after,
            "expectedDigest": EXPECTED_GEOMETRY_DIGEST,
            "unchanged": before == after == EXPECTED_GEOMETRY_DIGEST,
            "matricesUnchanged": matrices_unchanged,
            "closedPoseRestored": tuple(translation.location) == (0.0, 0.0, 0.0),
            "pointAxisWorldMm": [0.0, -9.5, 0.0],
            "hiddenEnvelopeUnchanged": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none",
        },
        "materials": {
            "assignmentsRestored": material_assignments_restored,
            "shippingEmissionStrengths": shipping_emissions,
            "shippingEmissionZero": all(value == 0.0 for value in shipping_emissions.values()),
            "fullBlackPerimeterPreserved": source_report["artworkLayers"]["topPerimeterBorder"]["outerPerimeterInsetPx"] == 0,
            "motifSha256": source_report["artworkLayers"]["lineage"]["sourceSha256"],
            "bloodRedBase": source_report["materialZones"]["deep-blood-red-crystal-face"]["baseColor"],
            "silverPbr": source_report["materialZones"]["polished-pure-silver-visual-target-exterior"]["actualPbr"],
        },
        "lightingRecipe": {
            "classification": "controlled Gate 08 lighting; no Gate 09 environment composition",
            "lights": [
                {
                    "name": name,
                    "type": "AREA",
                    "locationMm": list(location),
                    "powerW": power,
                    "sizeMm": size,
                    "linearRgb": list(color),
                    "colorTemperatureKelvin": kelvin,
                    "targetMm": list(target),
                }
                for name, location, power, size, color, kelvin, target in light_specs
            ],
            "world": {
                "type": "uniform-neutral",
                "linearRgb": list(world_color[:3]),
                "strength": world_strength,
                "hdri": None,
            },
            "reflectionCards": [
                {"name": cards[0].name, "linearRgb": [0.8, 0.8, 0.8], "cameraVisible": False},
                {"name": cards[1].name, "linearRgb": [0.8, 0.8, 0.8], "cameraVisible": False},
                {"name": cards[2].name, "linearRgb": [0.8, 0.8, 0.8], "cameraVisible": False},
                {"name": cards[3].name, "linearRgb": [0.008, 0.008, 0.008], "cameraVisible": False},
            ],
            "exposureEv": 0.0,
            "whiteBalanceKelvin": 6504,
            "whiteBalanceTint": 10,
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "renderer": scene.render.engine,
            "blender": bpy.app.version_string,
        },
        "cameras": {
            camera_id: {
                "name": cameras[camera_id].name,
                "locationMm": list(location),
                "targetMm": list(target),
                "lensMm": lens,
            }
            for camera_id, (location, target, lens) in camera_specs.items()
        },
        "outputs": {
            "hero": "hero.png",
            "leftOblique": "left-oblique.png",
            "rightOblique": "right-oblique.png",
            "low": "low-angle.png",
            "beauty": "pass-beauty.png",
            "clay": "pass-clay.png",
            "normal": "pass-normal.png",
            "depth": "pass-depth.png",
            "roughness": "pass-roughness.png",
            "openSideReflection": "open-side-reflection.png",
        },
        "technicalPassPolicy": {
            "normalDepthRoughnessUseUnlitOverrides": True,
            "technicalOverridesAreShippingMaterials": False,
            "beautyUsesApprovedGate07Materials": True,
        },
        "unityReflectionPlan": {
            "path": str(UNITY_PLAN.relative_to(REPO)),
            "sha256": sha256(UNITY_PLAN),
            "deliveryState": unity_plan["deliveryState"],
            "unityFilesChanged": False,
        },
        "scope": {
            "gate09Entered": False,
            "unityFilesChanged": False,
            "runtimeChanged": False,
            "reflectionProbesImplemented": False,
            "shaderGraphImplemented": False,
            "hapticsChanged": False,
            "buildInstallOrPhonePush": False,
        },
    }
    checks = {
        "sourceGate07Unchanged": report["sourceGate07"]["unchanged"],
        "geometryUnchanged": report["geometry"]["unchanged"] and report["geometry"]["matricesUnchanged"],
        "closedPoseAndPointAxis": report["geometry"]["closedPoseRestored"] and report["geometry"]["pointAxisWorldMm"] == [0.0, -9.5, 0.0],
        "hiddenMechanismUnchanged": report["geometry"]["hiddenEnvelopeUnchanged"],
        "materialsRestored": report["materials"]["assignmentsRestored"],
        "shippingEmissionZero": report["materials"]["shippingEmissionZero"],
        "approvedMaterialLanguagePreserved": report["materials"]["fullBlackPerimeterPreserved"]
        and report["materials"]["motifSha256"] == EXPECTED_MOTIF_SHA256,
        "requiredViewsAndPassesRendered": all((ROOT / filename).exists() for filename in report["outputs"].values()),
        "gate08Only": not any(report["scope"].values()),
        "unityPlanSpecifiedOnly": report["unityReflectionPlan"]["deliveryState"] == "specified-only-not-integrated",
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))

    scene.camera = cameras["hero"]
    view_layer.material_override = None
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
