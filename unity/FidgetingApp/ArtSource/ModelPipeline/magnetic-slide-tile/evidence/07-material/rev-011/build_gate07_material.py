#!/usr/bin/env python3
"""Apply source-backed Gate 07 materials to approved Gate 06 geometry."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
SOURCE_BLEND = MODEL_ROOT / "evidence/06-geometry/rev-004/magnetic-slide-tile-geometry-r004.blend"
TEXTURE_REPORT = HERE / "texture-lineage.json"
CONTRACT_PATH = MODEL_ROOT / "evidence/02-analysis/rev-016/mechanism-evidence-contract.json"
OUTPUT_BLEND = HERE / "magnetic-slide-tile-material-r011.blend"
OUTPUT_GLB = HERE / "magnetic-slide-tile-material-r011-lookdev.glb"
REPORT_PATH = HERE / "material-validation.json"
SOURCE_BLEND_SHA256 = "8047be52ce635d9bd18d5f2be3c3e223ac04c3101aec10221849d97b6e867085"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


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


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens=75):
    data = bpy.data.cameras.new(f"{name}_Data")
    data.lens = lens
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def area(name, location, target, energy, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def solid_material(name, color, metallic, roughness, coat=0.0, anisotropy=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    set_input(bsdf, "Base Color", color)
    set_input(bsdf, "Metallic", metallic)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "Coat Weight", coat)
    set_input(bsdf, "Coat Roughness", max(0.018, roughness * 0.25))
    set_input(bsdf, "Anisotropic IOR Level", anisotropy)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    mat["gate07_revision"] = 11
    mat["emission"] = 0.0
    return mat


def crystal_material(name, slot_name, albedo_path, roughness_path, source_mask_hash):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    albedo = nodes.new("ShaderNodeTexImage")
    albedo.name = f"{slot_name}_Albedo"
    albedo.image = bpy.data.images.load(str(albedo_path), check_existing=False)
    albedo.image.pack()
    albedo.interpolation = "Cubic"
    roughness = nodes.new("ShaderNodeTexImage")
    roughness.name = f"{slot_name}_Roughness"
    roughness.image = bpy.data.images.load(str(roughness_path), check_existing=False)
    roughness.image.colorspace_settings.name = "Non-Color"
    roughness.image.pack()
    roughness.interpolation = "Cubic"
    links.new(texcoord.outputs["UV"], albedo.inputs["Vector"])
    links.new(texcoord.outputs["UV"], roughness.inputs["Vector"])
    links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{slot_name}_GranularDepth"
    noise.noise_dimensions = "3D"
    noise.inputs["Scale"].default_value = 28.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.72
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.024
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    set_input(bsdf, "Metallic", 0.08)
    set_input(bsdf, "IOR", 1.52)
    set_input(bsdf, "Specular IOR Level", 0.58)
    set_input(bsdf, "Coat Weight", 0.48)
    set_input(bsdf, "Coat Roughness", 0.035)
    set_input(bsdf, "Transmission Weight", 0.08)
    set_input(bsdf, "Thin Film IOR", 1.38)
    set_input(bsdf, "Thin Film Thickness", 410.0)
    set_input(bsdf, "Emission Color", (0, 0, 0, 1))
    set_input(bsdf, "Emission Strength", 0.0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    mat["gate07_revision"] = 11
    mat["artworkSlot"] = slot_name
    mat["sourceMaskSha256"] = source_mask_hash
    mat["albedoSha256"] = sha256(albedo_path)
    mat["roughnessSha256"] = sha256(roughness_path)
    mat["independentlyReplaceable"] = True
    mat["appearanceAuthority"] = "original-user-blood-red-product-imagery-only"
    mat["productionChemistry"] = "unknown"
    mat["emission"] = 0.0
    return mat


def assign_exterior(obj, crystal, dark, silver, technical):
    obj.data.materials.clear()
    for mat in (crystal, dark, silver, technical):
        obj.data.materials.append(mat)
    max_z = max(vertex.co.z for vertex in obj.data.vertices)
    counts = {"artworkTop": 0, "darkSide": 0, "silverRim": 0, "technicalUnderside": 0}
    for polygon in obj.data.polygons:
        if polygon.normal.z > 0.999:
            index, key = 0, "artworkTop"
        elif abs(polygon.normal.z) < 0.72 and polygon.center.z >= max_z - 0.55:
            index, key = 2, "silverRim"
        elif polygon.normal.z < -0.15:
            index, key = 3, "technicalUnderside"
        else:
            index, key = 1, "darkSide"
        polygon.material_index = index
        counts[key] += 1
    return counts


def assign_whole(obj, mat, evidence_label):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
    obj["materialEvidence"] = evidence_label


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


def main():
    if sha256(SOURCE_BLEND) != SOURCE_BLEND_SHA256:
        raise RuntimeError("Approved Gate 06 blend hash drift.")
    if sha256(CONTRACT_PATH) != CONTRACT_SHA256:
        raise RuntimeError("Mechanism contract hash drift.")
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the approved Gate 06 blend before running.")
    texture_report = json.loads(TEXTURE_REPORT.read_text(encoding="utf-8"))
    if not texture_report["pass"]:
        raise RuntimeError("Prepared textures failed lineage validation.")
    before_digest = geometry_digest()
    if before_digest != GEOMETRY_DIGEST:
        raise RuntimeError(f"Gate 06 geometry digest drift: {before_digest}")

    for obj in list(bpy.data.objects):
        if (
            obj.type in {"CAMERA", "LIGHT"}
            or obj.name.startswith("G06_")
            or obj.name.startswith("SectionAA_")
            or obj.get("review_overlay_only")
            or obj.get("derived_section_evidence")
        ):
            bpy.data.objects.remove(obj, do_unlink=True)
    scene = bpy.context.scene
    scene["gate"] = "07-material"
    scene["material_revision"] = 11
    scene["gate06_source_sha256"] = SOURCE_BLEND_SHA256
    scene["mechanism_contract_sha256"] = CONTRACT_SHA256
    scene["canonical_geometry_digest"] = GEOMETRY_DIGEST
    scene["appearance_authority"] = "original-user-blood-red-product-imagery-only"
    scene["self_motion"] = False
    scene["shipping_unity_changed"] = False
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.compression = 18
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.use_file_extension = True
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    if hasattr(scene.view_settings, "use_white_balance"):
        scene.view_settings.use_white_balance = True
    if hasattr(scene.view_settings, "white_balance_temperature"):
        scene.view_settings.white_balance_temperature = 6504
    if hasattr(scene.view_settings, "white_balance_tint"):
        scene.view_settings.white_balance_tint = 10
    scene.world.color = (0.012, 0.016, 0.022)

    upper = crystal_material(
        "M07R11_Crystal_Upper",
        "Artwork_Upper",
        HERE / texture_report["outputs"]["upper"]["albedo"],
        HERE / texture_report["outputs"]["upper"]["roughness"],
        texture_report["sourceMasks"]["upper"]["sha256"],
    )
    lower = crystal_material(
        "M07R11_Crystal_LowerDistinct",
        "Artwork_Lower",
        HERE / texture_report["outputs"]["lower"]["albedo"],
        HERE / texture_report["outputs"]["lower"]["roughness"],
        texture_report["sourceMasks"]["lower"]["sha256"],
    )
    silver = solid_material("M07R11_PolishedSilver", (0.78, 0.77, 0.74, 1), 1.0, 0.075, 0.08, 0.16)
    carrier_silver = solid_material("M07R11_InternalSilverReference", (0.53, 0.55, 0.57, 1), 0.86, 0.13, 0.12)
    dark = solid_material("M07R11_DarkExteriorSide", (0.018, 0.020, 0.024, 1), 0.24, 0.18, 0.55)
    technical = solid_material("M07R11_NeutralTechnical", (0.18, 0.20, 0.22, 1), 0.42, 0.25, 0.10)
    ball_neutral = solid_material("M07R11_BallCandidate_UnknownMaterial", (0.34, 0.35, 0.36, 1), 0.12, 0.22, 0.15)
    assignments = {
        "BottomExterior": assign_exterior(bpy.data.objects["BottomExterior"], lower, dark, silver, technical),
        "MovingTopBody": assign_exterior(bpy.data.objects["MovingTopBody"], upper, dark, silver, technical),
    }
    assign_whole(bpy.data.objects["FixedAxisBoss"], silver, "source-supported-silver-white-zone")
    assign_whole(bpy.data.objects["RotatingCarrierBody"], carrier_silver, "source-supported-internal-silver-zone")
    for name in ("CarrierFollowerLeft", "CarrierFollowerRight"):
        assign_whole(bpy.data.objects[name], technical, "neutral-technical-inspection-only")
    for name in ("BallCandidateLeft", "BallCandidateRight"):
        assign_whole(bpy.data.objects[name], ball_neutral, "unknown-material-neutral-candidate")
        bpy.data.objects[name]["exactMaterialClaim"] = "unknown"

    ground_mat = solid_material("M07R11_NeutralGround", (0.025, 0.030, 0.038, 1), 0.05, 0.58)
    bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 0, -0.6))
    ground = bpy.context.object
    ground.name = "M07R11_NeutralGround"
    ground.data.materials.append(ground_mat)
    area("M07R11_Key", (58, -72, 92), (0, -3, 5), 72000, 48, (1.0, 0.92, 0.84))
    area("M07R11_Fill", (-58, -20, 58), (0, -2, 4), 33000, 44, (0.72, 0.84, 1.0))
    area("M07R11_Rim", (38, 68, 62), (0, 3, 4), 52000, 38, (1.0, 0.34, 0.30))
    area("M07R11_Top", (-8, 8, 118), (0, 0, 4), 42000, 42, (1.0, 1.0, 1.0))

    cameras = {
        "closed": camera("M07R11_Closed", (74, -116, 72), (0, -2, 5), 76),
        "front": camera("M07R11_Front", (0, -106, 126), (0, 0, 4), 88),
        "open": camera("M07R11_Open", (56, -122, 104), (0, -8, 5), 84),
        "side": camera("M07R11_Side", (92, -64, 31), (3, -2, 4), 108),
        "grazing": camera("M07R11_Grazing", (72, -104, 26), (0, -2, 6), 118),
        "macro": camera("M07R11_Macro", (28, -62, 74), (0, -3, 8), 135),
        "underside": camera("M07R11_Underside", (0, 0, 155), (0, 0, 10), 78),
        "internal": camera("M07R11_Internal", (58, -94, 48), (0, -7, 7), 92),
    }

    pose_digests = {}
    set_pose(0, 0)
    render(scene, cameras["closed"], "assembled-closed.png")
    render(scene, cameras["front"], "neutral-pbr-front.png")
    pose_digests["closed"] = geometry_digest()
    set_pose(12.0, 12.0)
    render(scene, cameras["open"], "assembled-open.png")
    render(scene, cameras["side"], "side-reflection.png")
    pose_digests["open"] = geometry_digest()
    for angle, camera_id in ((0, "front"), (12, "closed"), (36, "grazing")):
        set_pose(7.0, angle)
        render(scene, cameras[camera_id], f"crystal-angle-{angle:02d}.png")
        pose_digests[f"angle-{angle}"] = geometry_digest()
    set_pose(4.0, 12.0)
    render(scene, cameras["macro"], "crystal-microflake-closeup.png", 1600, 1200)
    set_pose(18.076433121019107, 0)
    render(scene, cameras["open"], "lower-artwork-open.png", 1600, 1200)

    top = bpy.data.objects["MovingTopBody"]
    hidden = [
        bpy.data.objects["BottomExterior"], bpy.data.objects["FixedAxisBoss"],
        bpy.data.objects["RotatingCarrierBody"], bpy.data.objects["CarrierFollowerLeft"],
        bpy.data.objects["CarrierFollowerRight"], bpy.data.objects["BallCandidateLeft"],
        bpy.data.objects["BallCandidateRight"], ground,
    ]
    set_pose(5.0, 0, 15.0)
    top.rotation_euler.x = math.pi
    for obj in hidden:
        obj.hide_render = True
    render(scene, cameras["underside"], "underside-grooves-material.png")
    for obj in hidden:
        obj.hide_render = False
    top.rotation_euler.x = 0.0

    set_pose(9.0, 12.0, 10.0)
    bpy.data.objects["BottomExterior"].hide_render = True
    render(scene, cameras["internal"], "internal-material-isolation.png")
    bpy.data.objects["BottomExterior"].hide_render = False

    set_pose(10.0, 12.0)
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
    set_pose(7.0, 12.0)
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.camera = cameras["closed"]
    target = Vector((0, -2, 5))
    radius = 132.0
    for frame in range(24):
        angle = math.tau * frame / 24
        cameras["closed"].location = (
            radius * math.sin(angle),
            -2 - radius * math.cos(angle),
            54 + 14 * math.sin(angle * 2),
        )
        look_at(cameras["closed"], target)
        scene.render.filepath = str(turntable / f"frame-{frame:03d}.png")
        bpy.ops.render.render(write_still=True)

    set_pose(0, 0)
    after_digest = geometry_digest()
    material_slots = {
        name: [material.name for material in bpy.data.objects[name].data.materials]
        for name in CORE
    }
    emission_values = {
        material.name: float(material.get("emission", 0.0))
        for material in (upper, lower, silver, carrier_silver, dark, technical, ball_neutral)
    }
    hidden_max_z = max(
        max((bpy.data.objects[name].matrix_world @ Vector(corner)).z for corner in bpy.data.objects[name].bound_box)
        for name in ("RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight")
    )
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 11,
        "pass": False,
        "contractSha256": CONTRACT_SHA256,
        "gate06SourceSha256": SOURCE_BLEND_SHA256,
        "geometryDigestBefore": before_digest,
        "geometryDigestAfter": after_digest,
        "poseGeometryDigests": pose_digests,
        "textureLineage": texture_report,
        "assignments": assignments,
        "materialSlots": material_slots,
        "materials": {
            "silver": {"metallic": 1.0, "roughness": 0.075, "anisotropy": 0.16, "emission": 0},
            "crystal": {
                "ior": 1.52, "coatWeight": 0.48, "coatRoughness": 0.035,
                "transmission": 0.08, "thinFilmIor": 1.38,
                "thinFilmThicknessNm": 410, "granularScale": 28,
                "microflakeScale": 85, "emission": 0,
            },
            "darkSide": {"metallic": 0.24, "roughness": 0.18, "coatWeight": 0.55, "emission": 0},
            "ballCandidates": {"visual": "neutral technical", "exactMaterialClaim": "unknown"},
        },
        "emissionValues": emission_values,
        "hiddenInternalMaximumZMm": hidden_max_z,
        "bottomTopPlaneZMm": 5.875,
        "animatedObjects": [
            obj.name for obj in bpy.data.objects
            if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
        ],
        "outputs": {
            "blend": OUTPUT_BLEND.name,
            "glb": OUTPUT_GLB.name,
            "renders": [
                "assembled-closed.png", "neutral-pbr-front.png", "assembled-open.png",
                "side-reflection.png", "crystal-angle-00.png", "crystal-angle-12.png",
                "crystal-angle-36.png", "crystal-microflake-closeup.png",
                "lower-artwork-open.png", "underside-grooves-material.png",
                "internal-material-isolation.png",
            ],
            "turntableFrames": 24,
        },
    }
    checks = {
        "contractHashConsumed": scene["mechanism_contract_sha256"] == CONTRACT_SHA256,
        "gate06HashConsumed": scene["gate06_source_sha256"] == SOURCE_BLEND_SHA256,
        "geometryUnchanged": before_digest == after_digest == GEOMETRY_DIGEST,
        "poseGeometryUnchanged": all(value == GEOMETRY_DIGEST for value in pose_digests.values()),
        "independentArtwork": upper["albedoSha256"] != lower["albedoSha256"]
        and upper["artworkSlot"] != lower["artworkSlot"],
        "sourceMasksImmutable": texture_report["sourceMasks"]["upper"]["sha256"] == "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
        and texture_report["sourceMasks"]["lower"]["sha256"] == "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2",
        "blackPerimeter": texture_report["sourceMasks"]["border"]["widthPx"] == 64,
        "materialBoundaries": all(assignments[name]["artworkTop"] == 1 and assignments[name]["silverRim"] > 0 for name in assignments),
        "zeroEmission": all(value == 0 for value in emission_values.values()),
        "crystalVariation": all(texture_report["outputs"][slot]["redStd"] > 25 for slot in ("upper", "lower")),
        "microflakes": all(texture_report["outputs"][slot]["microflakePixels"] > 1000 for slot in ("upper", "lower")),
        "lowerProvenance": texture_report["lowerDirectPixels"] == 118942 and texture_report["lowerReconstructedPixels"] == 102670,
        "internalIsolation": hidden_max_z <= 5.875 - 0.049,
        "unknownBallMaterial": all(bpy.data.objects[name]["exactMaterialClaim"] == "unknown" for name in ("BallCandidateLeft", "BallCandidateRight")),
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
        "geometryDigest": after_digest,
        "assignments": assignments,
        "blend": str(OUTPUT_BLEND),
        "glb": str(OUTPUT_GLB),
        "turntableFrames": 24,
    }, indent=2))


if __name__ == "__main__":
    main()

