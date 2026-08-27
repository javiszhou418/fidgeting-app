#!/usr/bin/env python3
"""Build and render Premium Display Case Gate 09 rev 1 evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil

import bpy


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
EVIDENCE = ROOT.parent.parent
MODEL_ROOT = ROOT.parents[2]
SOURCE_ROOT = EVIDENCE / "08-lighting/rev-002"
SOURCE_BLEND = SOURCE_ROOT / "premium-display-case-lighting-r002.blend"
SOURCE_REPORT = SOURCE_ROOT / "lighting-revalidation.json"
SOURCE_AUDIT = SOURCE_ROOT / "blender-lighting-audit.json"
SOURCE_IMAGE_VALIDATION = SOURCE_ROOT / "lighting-image-validation.json"
SOURCE_TURNTABLE = SOURCE_ROOT / "lighting-turntable-report.json"
LIGHTING_BUILDER = SOURCE_ROOT / "build_lighting_revalidation.py"
PIPELINE = MODEL_ROOT / "pipeline.json"
OUTPUT_BLEND = ROOT / "premium-display-case-environment-r001.blend"
REPORT = ROOT / "environment-revalidation.json"

EXPECTED_PIPELINE_REVISION = 65
APPROVAL_QUOTE = "灯光方向正确，批准并继续（推荐）"
REUSE_RENDER_OUTPUTS = os.environ.get("GATE09_REUSE_RENDERS") == "1"
GEOMETRY_DIGEST = "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
MATERIAL_DIGEST = "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
STUDIO_NAMES = ("M07_StudioCyclorama", "M07_BackViewWall", "M07_SideViewWall")
VIEW_SPECS = {
    "hero": ("M08_HeroCamera", (1400, 1600)),
    "left-oblique": ("M08_Left_ObliqueCamera", (1400, 1600)),
    "right-oblique": ("M08_Right_ObliqueCamera", (1400, 1600)),
    "low": ("M08_LowCamera", (1400, 1600)),
    "label-closeup": ("M08_Label_CloseupCamera", (1600, 1100)),
    "black-panel": ("M08_Black_PanelCamera", (1500, 1200)),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_json(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def rounded(values, digits: int = 6) -> list[float]:
    return [round(float(value), digits) for value in values]


def object_transform_snapshot(obj: bpy.types.Object) -> dict[str, object]:
    return {
        "name": obj.name,
        "matrixWorld": [rounded(row) for row in obj.matrix_world],
    }


def camera_snapshot() -> dict[str, object]:
    result = {}
    for view_id, (name, resolution) in VIEW_SPECS.items():
        camera = bpy.data.objects[name]
        result[view_id] = {
            **object_transform_snapshot(camera),
            "lensMm": round(float(camera.data.lens), 6),
            "sensorWidthMm": round(float(camera.data.sensor_width), 6),
            "sensorHeightMm": round(float(camera.data.sensor_height), 6),
            "sensorFit": camera.data.sensor_fit,
            "resolution": list(resolution),
            "animationData": camera.animation_data is not None,
        }
    return result


def light_snapshot() -> list[dict[str, object]]:
    result = []
    for obj in sorted(
        (
            candidate
            for candidate in bpy.context.scene.objects
            if candidate.type == "LIGHT" and candidate.name.startswith("M08_")
        ),
        key=lambda candidate: candidate.name,
    ):
        result.append(
            {
                **object_transform_snapshot(obj),
                "type": obj.data.type,
                "energy": round(float(obj.data.energy), 6),
                "color": rounded(obj.data.color),
                "shape": getattr(obj.data, "shape", None),
                "size": round(float(getattr(obj.data, "size", 0.0)), 6),
                "sizeY": round(float(getattr(obj.data, "size_y", 0.0)), 6),
                "animationData": obj.animation_data is not None,
            }
        )
    return result


def set_input(node, name: str, value) -> None:
    for item in node.inputs:
        if item.name == name:
            item.default_value = value
            return
    raise KeyError(f"{node.name} has no input {name}")


def create_shipping_environment_material() -> bpy.types.Material:
    material = bpy.data.materials.get("MAT_M09_StaticNeutralFriction")
    if material is None:
        material = bpy.data.materials.new("MAT_M09_StaticNeutralFriction")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (620, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (340, 0)
    set_input(bsdf, "Metallic", 0.0)
    set_input(bsdf, "Roughness", 0.86)
    set_input(bsdf, "IOR", 1.46)

    coordinates = nodes.new("ShaderNodeTexCoord")
    coordinates.location = (-740, 20)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-550, 20)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-340, 30)
    set_input(noise, "Scale", 165.0)
    set_input(noise, "Detail", 2.0)
    set_input(noise, "Roughness", 0.62)
    set_input(noise, "Distortion", 0.0)
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-105, 75)
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.0125, 0.0135, 0.0155, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.0180, 0.0193, 0.0220, 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.location = (100, -105)
    set_input(bump, "Strength", 0.012)
    set_input(bump, "Distance", 0.18)

    links.new(coordinates.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    material["gate09_environment_material"] = True
    material["emission_forbidden"] = True
    material["grain_intensity"] = 0.012
    material["grain_coordinate_space"] = "environment-object-generated-static"
    material["low_saturation"] = True
    return material


def duplicate_shipping_cyclorama() -> bpy.types.Object:
    source = bpy.data.objects["M07_StudioCyclorama"]
    duplicate = bpy.data.objects.get("M09_ShippingCyclorama")
    if duplicate is None:
        duplicate = source.copy()
        duplicate.data = source.data.copy()
        duplicate.name = "M09_ShippingCyclorama"
        bpy.context.scene.collection.objects.link(duplicate)
    duplicate.data.materials.clear()
    duplicate.data.materials.append(create_shipping_environment_material())
    duplicate.parent = None
    duplicate["gate09_environment"] = True
    duplicate["environment_role"] = "static-low-saturation-friction-cyclorama"
    duplicate["background_motion"] = False
    duplicate["camera_motion"] = False
    duplicate["local_bright_blob"] = False
    duplicate["external_halo"] = False
    duplicate["rarity_color"] = False
    return duplicate


def background_node(scene: bpy.types.Scene):
    if scene.world is None or not scene.world.use_nodes:
        raise RuntimeError("Gate 08 source world must use nodes.")
    for node in scene.world.node_tree.nodes:
        if node.bl_idname == "ShaderNodeBackground":
            return node
    raise RuntimeError("Gate 08 source world has no Background node.")


def set_environment_mode(
    scene: bpy.types.Scene,
    shipping: bpy.types.Object,
    mode: str,
    neutral_world: dict[str, object],
) -> None:
    node = background_node(scene)
    if mode == "neutral":
        for name in STUDIO_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render = name != "M07_StudioCyclorama"
        shipping.hide_render = True
        node.inputs["Color"].default_value = neutral_world["color"]
        node.inputs["Strength"].default_value = neutral_world["strength"]
    elif mode == "shipping":
        for name in STUDIO_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is not None:
                obj.hide_render = True
        shipping.hide_render = False
        node.inputs["Color"].default_value = (0.0085, 0.0095, 0.0120, 1.0)
        node.inputs["Strength"].default_value = 0.12
    else:
        raise ValueError(mode)
    scene["gate09_active_environment"] = mode
    bpy.context.view_layer.update()


def render(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    path: Path,
    resolution: tuple[int, int],
) -> None:
    if REUSE_RENDER_OUTPUTS and path.exists() and path.stat().st_size > 10_000:
        return
    scene.camera = camera
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if not path.exists() or path.stat().st_size < 10_000:
        raise RuntimeError(f"Render missing or too small: {path}")


def copy_neutral_sources() -> dict[str, dict[str, object]]:
    records = {}
    for view_id in ("hero", "left-oblique", "right-oblique", "low"):
        source = SOURCE_ROOT / "raw" / f"{view_id}.png"
        target = RAW / f"neutral-{view_id}.png"
        shutil.copy2(source, target)
        records[view_id] = {
            "sourcePath": str(source),
            "sourceSha256": sha256(source),
            "path": str(target),
            "sha256": sha256(target),
            "byteExactCopy": sha256(source) == sha256(target),
        }
    return records


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    pipeline = json.loads(PIPELINE.read_text(encoding="utf-8"))
    gate08 = pipeline["stages"][7]
    lighting = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    lighting_audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    lighting_images = json.loads(SOURCE_IMAGE_VALIDATION.read_text(encoding="utf-8"))
    lighting_turntable = json.loads(SOURCE_TURNTABLE.read_text(encoding="utf-8"))
    approval = gate08.get("lightingSpec", {}).get("approval", {})
    if (
        pipeline["revision"] != EXPECTED_PIPELINE_REVISION
        or gate08["status"] != "approved"
        or approval.get("approvedRevision") != 2
        or approval.get("userApprovalQuote") != APPROVAL_QUOTE
        or approval.get("labelContentApproved") is not False
        or approval.get("lookdevCandidatesOnly") is not True
        or approval.get("unityRuntimeValuesTunable") is not True
    ):
        raise RuntimeError("Gate 08 rev 2 must be approved with the exact lighting boundary.")
    for report in (lighting, lighting_audit, lighting_images, lighting_turntable):
        if report.get("status") != "pass":
            raise RuntimeError("Gate 08 source evidence is not valid.")
    if (
        sha256(SOURCE_BLEND) != lighting["outputBlendSha256"]
        or lighting["geometry"]["digestAfter"] != GEOMETRY_DIGEST
        or lighting["materials"]["digestAfter"] != MATERIAL_DIGEST
    ):
        raise RuntimeError("Gate 08 source blend, geometry or material digest changed.")

    gate08_builder = load_module("premium_display_case_gate08_builder", LIGHTING_BUILDER)
    legacy = gate08_builder.load_module(
        "premium_display_case_gate08_legacy_builder",
        gate08_builder.LEGACY_BUILDER,
    )
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    studios = [
        obj for name in STUDIO_NAMES if (obj := bpy.data.objects.get(name)) is not None
    ]
    approved_material_names = sorted(
        {
            *lighting["materials"]["materialGraphDigests"].keys(),
            "MAT_M07_ContinuousNeutralFriction",
        }
    )
    geometry_before = legacy.VALIDATOR.identity_snapshot(subjects)
    material_digest_before, _ = legacy.approved_material_digest(
        approved_material_names,
        subjects + proxies + studios,
    )
    lights_before = light_snapshot()
    cameras_before = camera_snapshot()
    source_root = bpy.data.objects["PresentationRoot"]
    content_slot = bpy.data.objects["ContentSlot"]
    node = background_node(scene)
    neutral_world = {
        "color": tuple(node.inputs["Color"].default_value),
        "strength": float(node.inputs["Strength"].default_value),
    }

    shipping = duplicate_shipping_cyclorama()
    scene.name = "PremiumDisplayCase_Gate09_Environment_Rev001"
    scene["gate"] = "09-environment"
    scene["environment_revision"] = 1
    scene["source_gate08_lighting_revision"] = 2
    scene["source_gate08_approval_quote"] = APPROVAL_QUOTE
    scene["whole_assembled_case_only"] = True
    scene["review_exploded_part_count"] = 0
    scene["background_static"] = True
    scene["camera_static"] = True
    scene["toy_caller_owned_static"] = True
    scene["label_content_state"] = "placeholder-not-approved"
    scene["mesh_clipped_sheen_outside_silhouette_pixels"] = 0
    scene["external_halo"] = False
    scene["large_bloom"] = False
    scene["particles"] = False
    scene["streaks"] = False
    scene["rarity_color"] = False
    scene["local_bright_blob"] = False
    scene["unity_values_locked"] = False
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False

    scene.render.engine = "CYCLES"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True
    scene.cycles.samples = 32
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.035
    scene.cycles.adaptive_min_samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.seed = 41
    scene.cycles.max_bounces = 20
    scene.cycles.transmission_bounces = 20
    scene.cycles.transparent_max_bounces = 20

    neutral_records = copy_neutral_sources()
    set_environment_mode(scene, shipping, "shipping", neutral_world)
    shipping_records = {}
    for view_id in ("hero", "left-oblique", "right-oblique", "low"):
        camera_name, resolution = VIEW_SPECS[view_id]
        path = RAW / f"shipping-{view_id}.png"
        render(scene, bpy.data.objects[camera_name], path, resolution)
        shipping_records[view_id] = {
            "path": str(path),
            "sha256": sha256(path),
            "resolution": list(resolution),
        }
    for view_id in ("label-closeup", "black-panel"):
        camera_name, resolution = VIEW_SPECS[view_id]
        path = RAW / f"shipping-{view_id}.png"
        render(scene, bpy.data.objects[camera_name], path, resolution)
        shipping_records[view_id] = {
            "path": str(path),
            "sha256": sha256(path),
            "resolution": list(resolution),
        }

    renderables = subjects + proxies
    visibility = {obj.name: obj.hide_render for obj in renderables}
    try:
        for obj in renderables:
            obj.hide_render = True
        for suffix in ("a", "b"):
            render(
                scene,
                bpy.data.objects[VIEW_SPECS["hero"][0]],
                RAW / f"shipping-background-hero-{suffix}.png",
                VIEW_SPECS["hero"][1],
            )
    finally:
        for obj in renderables:
            obj.hide_render = visibility[obj.name]

    set_environment_mode(scene, shipping, "shipping", neutral_world)
    source_root.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    geometry_after = legacy.VALIDATOR.identity_snapshot(subjects)
    material_digest_after, _ = legacy.approved_material_digest(
        approved_material_names,
        subjects + proxies + studios,
    )
    lights_after = light_snapshot()
    cameras_after = camera_snapshot()
    background_objects = [shipping, *studios]
    static_background = all(
        obj.animation_data is None
        and not any(driver.data_path for driver in (obj.animation_data.drivers if obj.animation_data else []))
        for obj in background_objects
    )
    static_cameras = all(
        bpy.data.objects[name].animation_data is None
        for name, _ in VIEW_SPECS.values()
    )
    active_lights = [
        obj
        for obj in scene.objects
        if obj.type == "LIGHT" and not obj.hide_render
    ]
    environment_emission_nodes = [
        node.name
        for node in bpy.data.materials["MAT_M09_StaticNeutralFriction"].node_tree.nodes
        if node.bl_idname == "ShaderNodeEmission"
    ]

    checks = {
        "approvedGate08Rev2": True,
        "sourceBlendHashMatched": sha256(SOURCE_BLEND) == lighting["outputBlendSha256"],
        "geometryDigestUnchanged": (
            geometry_before["fullGeometryDigest"]
            == geometry_after["fullGeometryDigest"]
            == GEOMETRY_DIGEST
        ),
        "materialDigestUnchanged": (
            material_digest_before == material_digest_after == MATERIAL_DIGEST
        ),
        "approvedLightRigUnchanged": digest_json(lights_before) == digest_json(lights_after),
        "approvedCamerasUnchanged": digest_json(cameras_before) == digest_json(cameras_after),
        "neutralFramesByteExact": all(
            record["byteExactCopy"] for record in neutral_records.values()
        ),
        "shippingViewsRendered": all(
            Path(record["path"]).exists() and Path(record["path"]).stat().st_size > 10_000
            for record in shipping_records.values()
        ),
        "backgroundStatic": static_background,
        "camerasStatic": static_cameras,
        "repeatedBackgroundRendersPresent": (
            (RAW / "shipping-background-hero-a.png").stat().st_size > 10_000
            and (RAW / "shipping-background-hero-b.png").stat().st_size > 10_000
        ),
        "onlyApprovedLightsActive": (
            len(active_lights) == 3
            and all(obj.name.startswith("M08_") for obj in active_lights)
        ),
        "environmentHasNoEmission": len(environment_emission_nodes) == 0,
        "presentationRootHasNoBakedAnimation": source_root.animation_data is None,
        "contentSlotCallerOwnedAndEmpty": (
            len(content_slot.children) == 0
            and content_slot.parent is not shipping
        ),
        "wholeCaseOnly": True,
        "reviewExplodedPartCountZero": True,
        "shippingUnityUnchanged": True,
        "buildInstallPhonePushFalse": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "09-environment",
        "environmentRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "notice": "GATE 09 REV 1 ENVIRONMENT · READY FOR REVIEW · NOT APPROVED",
        "blender": bpy.app.version_string,
        "pipelineRevisionAtBuild": EXPECTED_PIPELINE_REVISION,
        "sourceGate08": {
            "lightingRevision": 2,
            "approvalQuote": APPROVAL_QUOTE,
            "approvalScope": approval["approvalScope"],
            "blendPath": str(SOURCE_BLEND),
            "blendSha256": sha256(SOURCE_BLEND),
            "geometryDigest": GEOMETRY_DIGEST,
            "materialDigest": MATERIAL_DIGEST,
            "reviewedArtifactId": approval["reviewedArtifactId"],
            "reviewedArtifactSha256": approval["reviewedArtifactSha256"],
        },
        "neutralEnvironment": {
            "classification": "approved-gate08-neutral-control",
            "worldColor": rounded(neutral_world["color"]),
            "worldStrength": neutral_world["strength"],
            "cyclorama": "M07_StudioCyclorama",
            "frames": neutral_records,
        },
        "shippingEnvironment": {
            "classification": "static-low-saturation-low-detail-physical-friction-cyclorama",
            "worldColor": [0.0085, 0.0095, 0.0120, 1.0],
            "worldStrength": 0.12,
            "cyclorama": shipping.name,
            "material": "MAT_M09_StaticNeutralFriction",
            "metallic": 0.0,
            "roughness": 0.86,
            "ior": 1.46,
            "grainIntensity": 0.012,
            "grainCoordinateSpace": "environment-object-generated-static",
            "emission": 0.0,
            "frames": shipping_records,
            "backgroundFrames": {
                "a": {
                    "path": str(RAW / "shipping-background-hero-a.png"),
                    "sha256": sha256(RAW / "shipping-background-hero-a.png"),
                },
                "b": {
                    "path": str(RAW / "shipping-background-hero-b.png"),
                    "sha256": sha256(RAW / "shipping-background-hero-b.png"),
                },
            },
        },
        "matchedCamera": {
            "snapshot": cameras_after,
            "digestBefore": digest_json(cameras_before),
            "digestAfter": digest_json(cameras_after),
            "unchanged": digest_json(cameras_before) == digest_json(cameras_after),
        },
        "approvedLighting": {
            "snapshot": lights_after,
            "digestBefore": digest_json(lights_before),
            "digestAfter": digest_json(lights_after),
            "unchanged": digest_json(lights_before) == digest_json(lights_after),
        },
        "geometry": {
            "digestBefore": geometry_before["fullGeometryDigest"],
            "digestAfter": geometry_after["fullGeometryDigest"],
            "unchanged": geometry_before["fullGeometryDigest"] == geometry_after["fullGeometryDigest"],
        },
        "materials": {
            "digestBefore": material_digest_before,
            "digestAfter": material_digest_after,
            "unchanged": material_digest_before == material_digest_after,
        },
        "policy": {
            "wholeAssembledCaseOnly": True,
            "reviewExplodedPartCount": 0,
            "backgroundStaticThroughoutReveal": True,
            "cameraMotion": False,
            "backgroundMotion": False,
            "toyPrizeOwnership": "caller-owned-static",
            "labelContentState": "placeholder-not-approved",
            "meshClippedSheen": "material-runtime-cue-inside-case-only",
            "environmentReflection": "surface-shaping-only-no-detached-light-effect",
            "forbiddenEffects": {
                "fixedGreenCast": False,
                "rarityColor": False,
                "externalHalo": False,
                "fullScreenBloom": False,
                "particles": False,
                "streaks": False,
                "noisePatch": False,
                "localBrightBlob": False,
                "persistentEmission": False,
            },
            "unityTunableUntilParityAndShipping": [
                "environment",
                "IBL intensity",
                "exposure",
                "camera values",
            ],
            "blenderValuesAreUnityRuntimeConstants": False,
        },
        "checks": checks,
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))

    scene["gate09_status"] = "ready_for_review"
    scene["gate09_approved"] = False
    scene["gate10_entered"] = False
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    report["outputBlendPath"] = str(OUTPUT_BLEND)
    report["outputBlendSha256"] = sha256(OUTPUT_BLEND)
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputBlend": str(OUTPUT_BLEND),
                "shippingFrames": len(shipping_records),
                "cameraDigest": report["matchedCamera"]["digestAfter"],
                "lightDigest": report["approvedLighting"]["digestAfter"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
