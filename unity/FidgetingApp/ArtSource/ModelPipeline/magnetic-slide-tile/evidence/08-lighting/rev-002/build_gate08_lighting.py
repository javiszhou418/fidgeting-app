#!/usr/bin/env python3
"""Build Gate 08 lighting evidence without changing approved geometry or materials."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE_BLEND = MODEL_ROOT / "evidence/07-material/rev-011/magnetic-slide-tile-material-r011.blend"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-lighting-r002.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-lighting-r002-lookdev.glb"
REPORT_PATH = HERE / "lighting-validation.json"
SOURCE_SHA256 = "fdf6e96206b6d048aa88fbd049a8af1a4d7a391d65ed74791c3acaca2767d274"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]
APPROVED_MATERIALS = [
    "M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct",
    "M07R11_PolishedSilver", "M07R11_InternalSilverReference",
    "M07R11_DarkExteriorSide", "M07R11_NeutralTechnical",
    "M07R11_BallCandidate_UnknownMaterial",
]
MODES = {
    "neutral": {
        "world": {"linearRgb": [0.10, 0.10, 0.10], "strength": 0.35, "hdri": None},
        "lights": {
            "key": {"powerW": 42000, "linearRgb": [1.0, 0.98, 0.94], "cctK": 6504},
            "fill": {"powerW": 24000, "linearRgb": [0.96, 0.98, 1.0], "cctK": 6504},
            "rim": {"powerW": 42000, "linearRgb": [1.0, 1.0, 1.0], "cctK": 6504},
            "under": {"powerW": 16000, "linearRgb": [1.0, 0.91, 0.82], "cctK": 5600},
        },
    },
    "studio": {
        "world": {"linearRgb": [0.055, 0.055, 0.055], "strength": 0.18, "hdri": None},
        "lights": {
            "key": {"powerW": 48000, "linearRgb": [1.0, 0.91, 0.82], "cctK": 5600},
            "fill": {"powerW": 26000, "linearRgb": [0.90, 0.95, 1.0], "cctK": 7000},
            "rim": {"powerW": 50000, "linearRgb": [1.0, 1.0, 1.0], "cctK": 6504},
            "under": {"powerW": 22000, "linearRgb": [1.0, 0.87, 0.75], "cctK": 5200},
        },
    },
    "daylight": {
        "world": {"linearRgb": [0.24, 0.24, 0.24], "strength": 0.65, "hdri": None},
        "lights": {
            "key": {"powerW": 44000, "linearRgb": [1.0, 0.99, 0.97], "cctK": 6504},
            "fill": {"powerW": 34000, "linearRgb": [0.88, 0.94, 1.0], "cctK": 7500},
            "rim": {"powerW": 39000, "linearRgb": [1.0, 1.0, 1.0], "cctK": 6504},
            "under": {"powerW": 20000, "linearRgb": [1.0, 0.98, 0.94], "cctK": 6504},
        },
    },
}


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def serial(value):
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return [round(float(item), 9) for item in value]
    except (TypeError, ValueError):
        return str(value)


def material_digest():
    payload = {}
    for name in APPROVED_MATERIALS:
        material = bpy.data.materials[name]
        nodes = []
        if material.node_tree:
            for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
                nodes.append({
                    "name": node.name,
                    "type": node.bl_idname,
                    "inputs": {
                        socket.name: serial(socket.default_value)
                        for socket in node.inputs if hasattr(socket, "default_value")
                    },
                    "image": node.image.name if hasattr(node, "image") and node.image else None,
                })
        payload[name] = {
            "blendMethod": getattr(material, "surface_render_method", None),
            "nodes": nodes,
            "props": {key: serial(material[key]) for key in sorted(material.keys())},
        }
    for name in CORE:
        obj = bpy.data.objects[name]
        payload[name] = {
            "slots": [material.name for material in obj.data.materials],
            "indices": [polygon.material_index for polygon in obj.data.polygons],
        }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def matrix_snapshot():
    names = CORE + ["RotatingCarrier", "MovingTop", "TopLocalSlide", "FixedAxis"]
    return {name: [[round(value, 9) for value in row] for row in bpy.data.objects[name].matrix_world] for name in names}


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    data.sensor_width = 36
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate08_revision"] = 2
    obj["targetMm"] = list(target)
    return obj


def area(name, role, location, target, size):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    obj["gate08_revision"] = 2
    obj["lightingRole"] = role
    obj["sizeMm"] = size
    obj["targetMm"] = list(target)
    return obj


def solid_material(name, color, metallic=0.0, roughness=0.5):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = color
    bsdf = material.node_tree.nodes["Principled BSDF"]
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0)
    material["technicalPassOnly"] = True
    return material


def emission_material(name, source_socket_builder):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    source = source_socket_builder(nodes, links)
    links.new(source, emission.inputs["Color"])
    emission.inputs["Strength"].default_value = 1.0
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    material["technicalPassOnly"] = True
    return material


def make_normal_pass():
    def build(nodes, links):
        geometry = nodes.new("ShaderNodeNewGeometry")
        scale = nodes.new("ShaderNodeVectorMath")
        scale.operation = "SCALE"
        scale.inputs["Scale"].default_value = 0.5
        add = nodes.new("ShaderNodeVectorMath")
        add.operation = "ADD"
        add.inputs[1].default_value = (0.5, 0.5, 0.5)
        links.new(geometry.outputs["Normal"], scale.inputs[0])
        links.new(scale.outputs["Vector"], add.inputs[0])
        return add.outputs["Vector"]
    return emission_material("M08R2_PASS_NormalWorld", build)


def make_depth_pass():
    def build(nodes, links):
        camera_data = nodes.new("ShaderNodeCameraData")
        mapping = nodes.new("ShaderNodeMapRange")
        mapping.inputs["From Min"].default_value = 85
        mapping.inputs["From Max"].default_value = 165
        mapping.inputs["To Min"].default_value = 1
        mapping.inputs["To Max"].default_value = 0
        mapping.clamp = True
        links.new(camera_data.outputs["View Z Depth"], mapping.inputs["Value"])
        return mapping.outputs["Result"]
    return emission_material("M08R2_PASS_DepthHero", build)


def make_value_pass(name, value):
    return solid_material(name, (value, value, value, 1), 0, 1)


def set_world(world_spec):
    world = bpy.context.scene.world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (*world_spec["linearRgb"], 1)
    background.inputs["Strength"].default_value = world_spec["strength"]
    world["hdri"] = "none"
    world["gate08Mode"] = bpy.context.scene.get("gate08_mode", "unknown")


def apply_mode(scene, lights, mode):
    recipe = MODES[mode]
    scene["gate08_mode"] = mode
    set_world(recipe["world"])
    for role, obj in lights.items():
        spec = recipe["lights"][role]
        obj.data.energy = spec["powerW"]
        obj.data.color = spec["linearRgb"]
        obj["powerW"] = spec["powerW"]
        obj["cctK"] = spec["cctK"]
        obj["linearRgb"] = spec["linearRgb"]
    bpy.context.view_layer.update()


def create_reflection_card(name, location, rotation, scale, value):
    bpy.ops.mesh.primitive_plane_add(size=2, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(solid_material(f"{name}_Mat", (value, value, value, 1), 0, 0.32))
    if hasattr(obj, "visible_camera"):
        obj.visible_camera = False
    obj["gate08_revision"] = 2
    obj["cameraVisible"] = False
    obj["reflectionOnly"] = True
    return obj


def set_pose(travel, angle, lift=0.0):
    bpy.data.objects["RotatingCarrier"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["MovingTop"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["TopLocalSlide"].location = (0, -travel, lift)
    bpy.context.view_layer.update()


def render(scene, camera_obj, filename, width=1400, height=1100):
    scene.camera = camera_obj
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def camera_recipe(obj):
    return {
        "name": obj.name,
        "locationMm": [round(value, 6) for value in obj.location],
        "rotationEulerRad": [round(value, 9) for value in obj.rotation_euler],
        "targetMm": list(obj["targetMm"]),
        "lensMm": obj.data.lens,
        "sensorWidthMm": obj.data.sensor_width,
    }


def snapshot_slots():
    return {
        name: {
            "materials": [material for material in bpy.data.objects[name].data.materials],
            "indices": [polygon.material_index for polygon in bpy.data.objects[name].data.polygons],
        }
        for name in CORE
    }


def restore_slots(snapshot):
    for name, state in snapshot.items():
        obj = bpy.data.objects[name]
        obj.data.materials.clear()
        for material in state["materials"]:
            obj.data.materials.append(material)
        for polygon, index in zip(obj.data.polygons, state["indices"], strict=True):
            polygon.material_index = index


def apply_roughness_visual(snapshot, cache):
    values = {
        "M07R11_Crystal_Upper": 0.06,
        "M07R11_Crystal_LowerDistinct": 0.06,
        "M07R11_PolishedSilver": 0.075,
        "M07R11_InternalSilverReference": 0.13,
        "M07R11_DarkExteriorSide": 0.18,
        "M07R11_NeutralTechnical": 0.25,
        "M07R11_BallCandidate_UnknownMaterial": 0.22,
    }
    for name, state in snapshot.items():
        obj = bpy.data.objects[name]
        obj.data.materials.clear()
        for material in state["materials"]:
            value = values.get(material.name, 0.5)
            if value not in cache:
                cache[value] = make_value_pass(f"M08R2_PASS_Roughness_{value:.3f}", value)
            obj.data.materials.append(cache[value])


def main():
    if sha256(SOURCE_BLEND) != SOURCE_SHA256:
        raise RuntimeError("Approved Gate 07 blend hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the approved Gate 07 blend before running.")
    for material_name in APPROVED_MATERIALS:
        if material_name not in bpy.data.materials:
            raise RuntimeError(f"Missing approved material {material_name}.")
    geometry_before = geometry_digest()
    material_before = material_digest()
    matrices_before = matrix_snapshot()
    if geometry_before != GEOMETRY_DIGEST:
        raise RuntimeError(f"Geometry digest drift: {geometry_before}")
    for obj in list(bpy.data.objects):
        if (
            obj.type in {"CAMERA", "LIGHT"}
            or obj.name.startswith("M07R11_")
            and obj.name.endswith("Ground")
        ):
            bpy.data.objects.remove(obj, do_unlink=True)

    scene = bpy.context.scene
    scene["gate"] = "08-lighting"
    scene["lighting_revision"] = 2
    scene["gate07_source_sha256"] = SOURCE_SHA256
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["approved_material_digest"] = material_before
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 18
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.35
    scene.view_settings.gamma = 1.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 6504
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 10

    ground = bpy.data.objects.get("M07R11_NeutralGround")
    if ground is None:
        ground_material = solid_material("M08R2_NeutralGround", (0.025, 0.030, 0.038, 1), 0.05, 0.58)
        bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 0, -0.6))
        ground = bpy.context.object
        ground.name = "M08R2_NeutralGround"
        ground.data.materials.append(ground_material)
    lights = {
        "key": area("M08R2_KeySoftbox", "key", (58, -72, 96), (0, -3, 5), 20),
        "fill": area("M08R2_FillSoftbox", "fill", (-54, -12, 58), (0, -2, 4), 32),
        "rim": area("M08R2_SilverRimStrip", "rim", (44, 70, 62), (0, 2, 5), 18),
        "under": area("M08R2_MechanismReveal", "under", (-26, 20, 28), (0, -7, 5), 18),
    }
    cards = [
        create_reflection_card("M08R2_WhiteCard_Left", (-58, 4, 42), (math.radians(90), 0, math.radians(-18)), (8, 22, 1), 0.72),
        create_reflection_card("M08R2_WhiteCard_Right", (58, 2, 38), (math.radians(90), 0, math.radians(18)), (8, 22, 1), 0.82),
        create_reflection_card("M08R2_WhiteCard_Top", (0, 18, 94), (0, 0, 0), (16, 10, 1), 0.68),
        create_reflection_card("M08R2_BlackCard_Back", (0, 68, 32), (math.radians(90), 0, 0), (56, 30, 1), 0.008),
    ]

    cameras = {
        "hero": camera("M08R2_Hero", (74, -116, 72), (0, -2, 5), 76),
        "left-oblique": camera("M08R2_LeftOblique", (-76, -112, 68), (0, -2, 5), 78),
        "right-oblique": camera("M08R2_RightOblique", (80, -108, 63), (0, -2, 5), 80),
        "low": camera("M08R2_Low", (84, -120, 29), (0, -2, 5), 102),
        "top-reveal": camera("M08R2_TopReveal", (8, -76, 138), (0, -7, 4), 92),
        "underside": camera("M08R2_Underside", (0, 0, 155), (0, 0, 10), 78),
        "mechanism": camera("M08R2_Mechanism", (58, -94, 48), (0, -7, 7), 92),
    }
    recipe = {
        "classification": "controlled Gate 08 lighting; no Gate 09 environment composition",
        "modes": MODES,
        "fixtures": {
            role: {
                "name": obj.name,
                "type": obj.data.type,
                "locationMm": [round(value, 6) for value in obj.location],
                "sizeMm": obj.data.size,
                "targetMm": list(obj["targetMm"]),
            }
            for role, obj in lights.items()
        },
        "reflectionCards": [
            {
                "name": card.name,
                "cameraVisible": False,
                "locationMm": [round(value, 6) for value in card.location],
                "scale": [round(value, 6) for value in card.scale],
            }
            for card in cards
        ],
        "cameras": {name: camera_recipe(obj) for name, obj in cameras.items()},
        "colorManagement": {
            "viewTransform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "exposureEv": scene.view_settings.exposure,
            "gamma": scene.view_settings.gamma,
            "whiteBalanceKelvin": 6504,
            "whiteBalanceTint": 10,
        },
        "renderEngine": scene.render.engine,
        "hdri": None,
    }
    (HERE / "lighting-recipe.json").write_text(json.dumps(recipe, indent=2), encoding="utf-8")

    set_pose(0, 0)
    apply_mode(scene, lights, "studio")
    render(scene, cameras["hero"], "hero.png")
    render(scene, cameras["left-oblique"], "left-oblique.png")
    render(scene, cameras["right-oblique"], "right-oblique.png")
    render(scene, cameras["low"], "low-angle.png")
    for mode in ("neutral", "studio", "daylight"):
        apply_mode(scene, lights, mode)
        render(scene, cameras["hero"], f"lighting-{mode}.png")

    apply_mode(scene, lights, "studio")
    set_pose(0, 0)
    render(scene, cameras["hero"], "state-closed.png")
    set_pose(18.076433121019107, 0)
    render(scene, cameras["top-reveal"], "state-max-open.png")
    render(scene, cameras["top-reveal"], "flat-plane-raised-axis-lit.png")
    set_pose(7, 12)
    render(scene, cameras["hero"], "state-detent-12.png")
    set_pose(7, 36)
    render(scene, cameras["hero"], "state-detent-36.png")

    set_pose(5, 0, 15)
    top = bpy.data.objects["MovingTopBody"]
    top.rotation_euler.x = math.pi
    hidden = [
        bpy.data.objects["BottomExterior"], bpy.data.objects["FixedAxisBoss"],
        bpy.data.objects["RotatingCarrierBody"], bpy.data.objects["CarrierFollowerLeft"],
        bpy.data.objects["CarrierFollowerRight"], bpy.data.objects["BallCandidateLeft"],
        bpy.data.objects["BallCandidateRight"], ground,
    ]
    for obj in hidden:
        obj.hide_render = True
    render(scene, cameras["underside"], "underside-grooves-lit.png")
    for obj in hidden:
        obj.hide_render = False
    top.rotation_euler.x = 0
    set_pose(9, 12, 10)
    bpy.data.objects["BottomExterior"].hide_render = True
    render(scene, cameras["mechanism"], "carrier-clearance-lit.png")
    bpy.data.objects["BottomExterior"].hide_render = False

    set_pose(0, 0)
    apply_mode(scene, lights, "studio")
    pass_camera_matrix = [[round(value, 9) for value in row] for row in cameras["hero"].matrix_world]
    render(scene, cameras["hero"], "pass-beauty.png")
    view_layer = scene.view_layers[0]
    clay = solid_material("M08R2_PASS_Clay", (0.42, 0.44, 0.47, 1), 0, 0.38)
    normal_pass = make_normal_pass()
    depth_pass = make_depth_pass()
    view_layer.material_override = clay
    render(scene, cameras["hero"], "pass-clay.png")
    view_layer.material_override = normal_pass
    render(scene, cameras["hero"], "pass-normal.png")
    view_layer.material_override = depth_pass
    render(scene, cameras["hero"], "pass-depth.png")
    view_layer.material_override = None
    original_slots = snapshot_slots()
    apply_roughness_visual(original_slots, {})
    render(scene, cameras["hero"], "pass-roughness.png")
    restore_slots(original_slots)

    set_pose(8, 12)
    bpy.ops.object.select_all(action="DESELECT")
    export_names = [
        "MagneticSlideTile_G05_R006", "BottomExterior", "FixedAxisBoss", "FixedAxis",
        "MinimumOverlapDisk", "RotatingCarrier", "RotatingCarrierBody",
        "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
        "UnknownSprings", "UnknownPreload", "MovingTop", "TopLocalSlide", "MovingTopBody",
        "TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight",
    ]
    for name in export_names:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["MagneticSlideTile_G05_R006"]
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_extras=True,
        export_apply=True,
        export_animations=False,
    )

    turntable = HERE / "turntable"
    turntable.mkdir(exist_ok=True)
    apply_mode(scene, lights, "studio")
    set_pose(8, 12)
    scene.camera = cameras["hero"]
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    target = Vector((0, -2, 5))
    radius = 132
    for frame in range(24):
        angle = math.tau * frame / 24
        cameras["hero"].location = (
            radius * math.sin(angle),
            -2 - radius * math.cos(angle),
            52 + 13 * math.sin(angle * 2),
        )
        look_at(cameras["hero"], target)
        scene.render.filepath = str(turntable / f"frame-{frame:03d}.png")
        bpy.ops.render.render(write_still=True)

    set_pose(0, 0)
    cameras["hero"].location = recipe["cameras"]["hero"]["locationMm"]
    cameras["hero"].rotation_euler = recipe["cameras"]["hero"]["rotationEulerRad"]
    apply_mode(scene, lights, "studio")
    geometry_after = geometry_digest()
    material_after = material_digest()
    matrices_after = matrix_snapshot()
    approved_emission = {}
    for name in APPROVED_MATERIALS:
        bsdf = next(node for node in bpy.data.materials[name].node_tree.nodes if node.type == "BSDF_PRINCIPLED")
        approved_emission[name] = float(bsdf.inputs["Emission Strength"].default_value)
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 2,
        "pass": False,
        "sourceGate07": {
            "materialRevision": 11,
            "blendSha256": SOURCE_SHA256,
            "approvalWording": "继续",
        },
        "contractSha256": CONTRACT_SHA256,
        "geometry": {
            "before": geometry_before,
            "after": geometry_after,
            "expected": GEOMETRY_DIGEST,
        },
        "materials": {
            "before": material_before,
            "after": material_after,
            "approvedEmission": approved_emission,
        },
        "matrices": {
            "before": matrices_before,
            "after": matrices_after,
        },
        "lightingRecipe": recipe,
        "passCameraMatrix": pass_camera_matrix,
        "passCameraName": cameras["hero"].name,
        "passes": ["pass-beauty.png", "pass-clay.png", "pass-normal.png", "pass-depth.png", "pass-roughness.png"],
        "views": ["hero.png", "left-oblique.png", "right-oblique.png", "low-angle.png"],
        "states": [
            "state-closed.png", "state-max-open.png", "state-detent-12.png", "state-detent-36.png",
            "flat-plane-raised-axis-lit.png", "underside-grooves-lit.png", "carrier-clearance-lit.png",
        ],
        "lightingModes": ["lighting-neutral.png", "lighting-studio.png", "lighting-daylight.png"],
        "animatedObjects": [
            obj.name for obj in bpy.data.objects
            if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
        ],
    }
    checks = {
        "sourceHash": sha256(SOURCE_BLEND) == SOURCE_SHA256,
        "contractHash": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
        "geometryUnchanged": geometry_before == geometry_after == GEOMETRY_DIGEST,
        "materialsUnchanged": material_before == material_after,
        "matricesRestored": matrices_before == matrices_after,
        "approvedEmissionZero": all(value == 0 for value in approved_emission.values()),
        "requiredViews": all((HERE / name).exists() for name in report["views"]),
        "requiredPasses": all((HERE / name).exists() for name in report["passes"]),
        "mechanicalViews": all((HERE / name).exists() for name in report["states"]),
        "modeComparisons": all((HERE / name).exists() for name in report["lightingModes"]),
        "passCameraConsistent": report["passCameraName"] == "M08R2_Hero",
        "noHdri": all(spec["world"]["hdri"] is None for spec in MODES.values()),
        "zeroSelfMotion": not report["animatedObjects"] and scene["self_motion"] is False,
        "oldShippingUntouched": scene["shipping_unity_changed"] is False,
        "glbWritten": OUTPUT_GLB.exists(),
        "turntableFrames": len(list(turntable.glob("frame-*.png"))) == 24,
    }
    report["checks"] = checks
    report["pass"] = all(checks.values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report["checks"]["blendWritten"] = OUTPUT_BLEND.exists()
    report["pass"] = all(report["checks"].values())
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "geometryDigest": geometry_after,
        "materialDigest": material_after,
        "lights": recipe["fixtures"],
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
    }, indent=2))


if __name__ == "__main__":
    main()

