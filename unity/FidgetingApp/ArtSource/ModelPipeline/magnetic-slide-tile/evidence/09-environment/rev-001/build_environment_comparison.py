#!/usr/bin/env python3
"""Build Gate 09 matched-camera neutral and shipping-like environments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
SOURCE_BLEND = ROOT.parents[1] / "08-lighting/rev-001/magnetic-slide-tile-lighting-r001.blend"
LIGHTING_REPORT = ROOT.parents[1] / "08-lighting/rev-001/lighting-validation.json"
OPTIMIZATION = ROOT / "optimization-decision.json"
OUTPUT_BLEND = ROOT / "magnetic-slide-tile-environment-r001.blend"
REPORT = ROOT / "environment-validation.json"
EXPECTED_GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
SHIPPING_MATERIALS = [
    "M07R7_DaylightNeutralPolishedSilver",
    "M07R7_BloodRedCrystal_WideBorder_Upper",
    "M07R7_BloodRedCrystal_WideBorder_Lower",
]


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


def serializable(value):
    if isinstance(value, (int, float, str, bool)) or value is None:
        return value
    try:
        return [round(float(component), 9) for component in value]
    except (TypeError, ValueError):
        return str(value)


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


def object_matrix(obj: bpy.types.Object) -> list[list[float]]:
    return [[round(float(value), 9) for value in row] for row in obj.matrix_world]


def camera_signature(obj: bpy.types.Object) -> dict:
    return {
        "name": obj.name,
        "matrixWorld": object_matrix(obj),
        "lensMm": float(obj.data.lens),
        "sensorWidthMm": float(obj.data.sensor_width),
        "shiftX": float(obj.data.shift_x),
        "shiftY": float(obj.data.shift_y),
    }


def light_signature(obj: bpy.types.Object) -> dict:
    return {
        "name": obj.name,
        "matrixWorld": object_matrix(obj),
        "type": obj.data.type,
        "energy": float(obj.data.energy),
        "size": float(obj.data.size),
        "color": [float(component) for component in obj.data.color],
        "hideRender": bool(obj.hide_render),
        "kelvin": int(obj["color_temperature_kelvin"]),
    }


def set_input(shader: bpy.types.Node, name: str, value) -> None:
    socket = shader.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def shipping_ground_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M09R1_ShippingAdaptiveGround")
    material.use_nodes = True
    shader = material.node_tree.nodes["Principled BSDF"]
    set_input(shader, "Base Color", (0.018, 0.024, 0.032, 1.0))
    set_input(shader, "Metallic", 0.0)
    set_input(shader, "Roughness", 0.48)
    set_input(shader, "Emission Strength", 0.0)
    material["gate09_environment_only"] = True
    return material


def configure_shipping_world(world: bpy.types.World) -> dict:
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    output.name = "M09R1_WorldOutput"
    background = nodes.new("ShaderNodeBackground")
    background.name = "M09R1_AdaptiveBackground"
    background.inputs["Strength"].default_value = 0.85
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = "M09R1_EnvironmentDirection"
    separate = nodes.new("ShaderNodeSeparateXYZ")
    separate.name = "M09R1_VerticalDirection"
    mapping = nodes.new("ShaderNodeMapRange")
    mapping.name = "M09R1_NormalizeVertical"
    mapping.inputs["From Min"].default_value = -1.0
    mapping.inputs["From Max"].default_value = 1.0
    mapping.inputs["To Min"].default_value = 0.0
    mapping.inputs["To Max"].default_value = 1.0
    mapping.clamp = True
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = "M09R1_TopDownAdaptiveField"
    ramp.color_ramp.interpolation = "EASE"
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    stops = [
        (0.0, (0.008, 0.012, 0.018, 1.0)),
        (0.46, (0.022, 0.030, 0.039, 1.0)),
        (0.76, (0.34, 0.36, 0.37, 1.0)),
        (1.0, (0.085, 0.100, 0.108, 1.0)),
    ]
    first = ramp.color_ramp.elements[0]
    first.position = stops[0][0]
    first.color = stops[0][1]
    for position, color in stops[1:]:
        element = ramp.color_ramp.elements.new(position)
        element.color = color
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = "M09R1_StaticFineGrain"
    noise.inputs["Scale"].default_value = 120.0
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.42
    grain_ramp = nodes.new("ShaderNodeValToRGB")
    grain_ramp.name = "M09R1_GrainAmplitude0012"
    grain_ramp.color_ramp.elements[0].color = (0.988, 0.988, 0.988, 1.0)
    grain_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.name = "M09R1_EnvironmentReflectionContent"
    multiply.blend_type = "MULTIPLY"
    multiply.inputs["Fac"].default_value = 1.0
    links.new(texcoord.outputs["Normal"], separate.inputs["Vector"])
    links.new(separate.outputs["Z"], mapping.inputs["Value"])
    links.new(mapping.outputs["Result"], ramp.inputs["Fac"])
    links.new(texcoord.outputs["Normal"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], grain_ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], multiply.inputs[1])
    links.new(grain_ramp.outputs["Color"], multiply.inputs[2])
    links.new(multiply.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    return {
        "authority": [
            "FDB-SCN-001 top-down low-saturation adaptive field",
            "FDB-SCN-002 ground, lighting, IBL, and shadow share one space",
            "MeshyEDC.unity camera background 0.012/0.016/0.023",
        ],
        "type": "procedural-directional-skybox-preview",
        "hdri": None,
        "strength": 0.85,
        "verticalStops": [
            {"position": position, "linearRgb": list(color[:3])}
            for position, color in stops
        ],
        "staticFineGrain": {
            "strength": 0.012,
            "scale": 120.0,
            "detail": 2.0,
            "animated": False,
        },
        "reflectionContent": "Directional top field, neutral horizon, dark lower hemisphere, and static fine grain are visible to the polished silver through Blender world reflections.",
        "unityClaim": "Blender preview only; no Unity skybox or Reflection Probe integration.",
    }


def render(scene: bpy.types.Scene, camera: bpy.types.Object, filename: str, width: int, height: int) -> None:
    scene.camera = camera
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(ROOT / filename)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def main() -> None:
    source_hash_before = sha256(SOURCE_BLEND)
    lighting_report = json.loads(LIGHTING_REPORT.read_text(encoding="utf-8"))
    optimization = json.loads(OPTIMIZATION.read_text(encoding="utf-8"))
    if not lighting_report["pass"] or lighting_report["lightingRevision"] != 1:
        raise RuntimeError("Approved Gate 08 source is invalid.")
    if not optimization["pass"] or optimization["measuredModel"]["totalTriangles"] != 4096:
        raise RuntimeError("Optimization decision is invalid.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    lower = bpy.data.objects["LowerBody_Fixed_CleanPlane"]
    upper = bpy.data.objects["UpperCapsule_Moving"]
    translation = bpy.data.objects["UpperTranslation"]
    pivot = bpy.data.objects["CentralAxisPivot_Point"]
    envelope = bpy.data.objects["ConcealedCircularEnvelope_Metadata"]
    model_objects = [lower, upper]
    beauty_camera = bpy.data.objects["M08R1_BeautyCamera"]
    side_camera = bpy.data.objects["M08R1_Right_ObliqueCamera"]
    lights = sorted(
        [
            obj for obj in bpy.data.objects
            if obj.type == "LIGHT" and obj.get("gate08_controlled_lighting")
        ],
        key=lambda item: item.name,
    )
    ground = bpy.data.objects["PresentationGround"]
    world = scene.world
    scene["gate"] = "09-environment"
    scene["environment_revision"] = 1
    scene["source_gate08_approval_wording"] = "可以吧，然后你继续"
    scene["geometry_change_authorized"] = False
    scene["lod_creation_authorized"] = False
    scene["unity_change_authorized"] = False
    scene["blender_environment_is_unity_integration"] = False

    geometry_before = geometry_digest(model_objects)
    matrices_before = {
        obj.name: object_matrix(obj)
        for obj in [lower, upper, envelope, translation, pivot]
    }
    camera_before = {
        "beauty": camera_signature(beauty_camera),
        "side": camera_signature(side_camera),
    }
    light_before = {
        obj.name: light_signature(obj)
        for obj in lights
    }
    material_before = {
        name: material_signature(bpy.data.materials[name])
        for name in SHIPPING_MATERIALS
    }
    material_assignments_before = {
        obj.name: [slot.material.name for slot in obj.material_slots]
        for obj in model_objects
    }
    shipping_emission = {}
    for name in SHIPPING_MATERIALS:
        material = bpy.data.materials[name]
        shader = next(node for node in material.node_tree.nodes if node.bl_idname == "ShaderNodeBsdfPrincipled")
        shipping_emission[name] = float(shader.inputs["Emission Strength"].default_value)
    if any(value != 0.0 for value in shipping_emission.values()):
        raise RuntimeError("Shipping material emission must remain zero.")

    neutral_world_recipe = {
        "type": "uniform-neutral",
        "linearRgb": list(world.node_tree.nodes["Background"].inputs["Color"].default_value[:3]),
        "strength": float(world.node_tree.nodes["Background"].inputs["Strength"].default_value),
        "hdri": None,
    }
    neutral_ground_material = ground.data.materials[0]
    neutral_ground_shader = neutral_ground_material.node_tree.nodes["Principled BSDF"]
    neutral_ground_recipe = {
        "material": neutral_ground_material.name,
        "baseColor": list(neutral_ground_shader.inputs["Base Color"].default_value),
        "roughness": float(neutral_ground_shader.inputs["Roughness"].default_value),
    }
    reflection_cards = [
        obj for obj in bpy.data.objects
        if obj.get("gate08_reflection_card")
    ]
    reflection_card_recipe = {
        obj.name: {
            "matrixWorld": object_matrix(obj),
            "cameraVisible": bool(obj.visible_camera),
            "renderVisible": not obj.hide_render,
            "material": obj.data.materials[0].name,
        }
        for obj in sorted(reflection_cards, key=lambda item: item.name)
    }

    scene.render.engine = "BLENDER_EEVEE"
    scene.view_settings.exposure = 0.0
    scene.view_settings.look = "AgX - Medium High Contrast"
    render(scene, beauty_camera, "neutral-environment.png", 1600, 1200)
    render(scene, side_camera, "neutral-side-reflection.png", 1400, 1000)

    shipping_world_recipe = configure_shipping_world(world)
    shipping_ground = shipping_ground_material()
    ground.data.materials[0] = shipping_ground
    render(scene, beauty_camera, "shipping-environment.png", 1600, 1200)
    render(scene, side_camera, "shipping-side-reflection.png", 1400, 1000)

    geometry_after = geometry_digest(model_objects)
    matrices_after = {
        obj.name: object_matrix(obj)
        for obj in [lower, upper, envelope, translation, pivot]
    }
    camera_after = {
        "beauty": camera_signature(beauty_camera),
        "side": camera_signature(side_camera),
    }
    light_after = {
        obj.name: light_signature(obj)
        for obj in lights
    }
    material_after = {
        name: material_signature(bpy.data.materials[name])
        for name in SHIPPING_MATERIALS
    }
    material_assignments_after = {
        obj.name: [slot.material.name for slot in obj.material_slots]
        for obj in model_objects
    }
    source_hash_after = sha256(SOURCE_BLEND)

    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "09-environment",
        "environmentRevision": 1,
        "sourceGate08": {
            "lightingRevision": 1,
            "blendPath": str(SOURCE_BLEND.relative_to(REPO)),
            "sha256Before": source_hash_before,
            "sha256After": source_hash_after,
            "unchanged": source_hash_before == source_hash_after,
            "approvalWording": "可以吧，然后你继续",
        },
        "invariants": {
            "geometryDigestBefore": geometry_before,
            "geometryDigestAfter": geometry_after,
            "expectedGeometryDigest": EXPECTED_GEOMETRY_DIGEST,
            "geometryUnchanged": geometry_before == geometry_after == EXPECTED_GEOMETRY_DIGEST,
            "matricesBefore": matrices_before,
            "matricesAfter": matrices_after,
            "matricesUnchanged": matrices_before == matrices_after,
            "cameraBefore": camera_before,
            "cameraAfter": camera_after,
            "camerasUnchanged": camera_before == camera_after,
            "lightBefore": light_before,
            "lightAfter": light_after,
            "lightsUnchanged": light_before == light_after,
            "materialHashesBefore": material_before,
            "materialHashesAfter": material_after,
            "materialsUnchanged": material_before == material_after,
            "materialAssignmentsBefore": material_assignments_before,
            "materialAssignmentsAfter": material_assignments_after,
            "materialAssignmentsUnchanged": material_assignments_before == material_assignments_after,
            "poseClosed": tuple(translation.location) == (0.0, 0.0, 0.0),
            "pointAxisWorldMm": list(pivot.location),
            "hiddenEnvelopeUnchanged": envelope.type == "EMPTY" and envelope.hide_render and envelope["geometry"] == "none",
            "shippingEmissionStrengths": shipping_emission,
            "shippingEmissionZero": all(value == 0.0 for value in shipping_emission.values()),
        },
        "matchedComparison": {
            "camera": camera_before["beauty"],
            "sideCamera": camera_before["side"],
            "lightRig": light_before,
            "exposureEv": 0.0,
            "whiteBalanceKelvin": 6504,
            "whiteBalanceTint": 10,
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "renderer": scene.render.engine,
            "blender": bpy.app.version_string,
        },
        "neutralEnvironment": {
            "world": neutral_world_recipe,
            "ground": neutral_ground_recipe,
            "reflectionCards": reflection_card_recipe,
            "outputs": {
                "matchedCamera": "neutral-environment.png",
                "sideReflection": "neutral-side-reflection.png",
            },
        },
        "shippingLikeEnvironment": {
            "world": shipping_world_recipe,
            "ground": {
                "material": shipping_ground.name,
                "baseColor": [0.018, 0.024, 0.032, 1.0],
                "roughness": 0.48,
            },
            "reflectionCards": reflection_card_recipe,
            "outputs": {
                "matchedCamera": "shipping-environment.png",
                "sideReflection": "shipping-side-reflection.png",
            },
            "classification": "Blender preview of the canonical adaptive shipping environment; not Unity integration.",
        },
        "isolatedDifferences": [
            "World color changed from uniform neutral to the canonical top-down low-saturation adaptive field.",
            "Ground changed from neutral gray to the canonical near-black blue-neutral app ground.",
            "Directional world reflection content and fixed 0.012 grain changed what polished silver samples.",
            "Camera, geometry, materials, pose, light rig, exposure, white balance, and reflection-card transforms did not change.",
        ],
        "optimizationDecision": {
            "path": str(OPTIMIZATION.relative_to(REPO)),
            "sha256": sha256(OPTIMIZATION),
            "decisionState": optimization["decisionState"],
            "deliveryState": optimization["deliveryState"],
            "triangles": optimization["measuredModel"]["totalTriangles"],
        },
        "scope": {
            "gate10Entered": False,
            "exportPerformed": False,
            "geometryChanged": False,
            "lodCreated": False,
            "unityChanged": False,
            "reflectionProbesImplemented": False,
            "runtimeOrHapticsChanged": False,
            "buildInstallOrPhonePush": False,
        },
    }
    checks = {
        "sourceGate08Unchanged": report["sourceGate08"]["unchanged"],
        "geometryUnchanged": report["invariants"]["geometryUnchanged"],
        "cameraMatch": report["invariants"]["camerasUnchanged"],
        "lightRigMatch": report["invariants"]["lightsUnchanged"],
        "materialHashesMatch": report["invariants"]["materialsUnchanged"],
        "materialAssignmentsMatch": report["invariants"]["materialAssignmentsUnchanged"],
        "poseAndPointAxisPreserved": report["invariants"]["poseClosed"]
        and report["invariants"]["pointAxisWorldMm"] == [0.0, -9.5, 0.0],
        "hiddenMechanismPreserved": report["invariants"]["hiddenEnvelopeUnchanged"],
        "shippingEmissionZero": report["invariants"]["shippingEmissionZero"],
        "requiredEnvironmentOutputs": all(
            (ROOT / filename).exists()
            for filename in [
                "neutral-environment.png",
                "shipping-environment.png",
                "neutral-side-reflection.png",
                "shipping-side-reflection.png",
            ]
        ),
        "optimizationDecisionRecorded": optimization["pass"],
        "gate09Only": not any(report["scope"].values()),
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    scene.camera = beauty_camera
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
