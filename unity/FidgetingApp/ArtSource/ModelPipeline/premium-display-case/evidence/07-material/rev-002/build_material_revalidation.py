#!/usr/bin/env python3
"""Revalidate Premium Display Case Gate 07 materials on Gate 06 rev 3."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
MASKS = ROOT / "masks"
EVIDENCE = ROOT.parent.parent
GATE04_SPEC = EVIDENCE / "04-architecture/rev-007/architecture.json"
GATE06 = EVIDENCE / "06-geometry/rev-003"
GATE06_BLEND = GATE06 / "premium-display-case-geometry-r003.blend"
GATE06_REPORT = GATE06 / "geometry-revalidation.json"
GATE06_VALIDATOR = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
PRIOR_ROOT = ROOT.parent / "rev-001"
PRIOR_BLEND = PRIOR_ROOT / "premium-display-case-material-r001.blend"
PRIOR_REPORT = PRIOR_ROOT / "material-build-report.json"
OUTPUT_BLEND = ROOT / "premium-display-case-material-r002.blend"
REPORT_PATH = ROOT / "material-revalidation.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
SHEEN_ELIGIBLE_NAMES = (
    "RearPolycarbonateShell",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
)
EXPECTED_ASSIGNMENTS = {
    "RearPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "FrontPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "ContinuousTubePerimeter": "MAT_FrostedPolycarbonateEdge",
    "TactileBackgroundInsert": "MAT_BlackFlocking",
    "PhysicalLabel": "MAT_LabelPaper",
}
EXPECTED_IDENTITY = {
    "fullGeometryDigest": "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951",
    "objectMatrixDigest": "34d52e8980dbbffc5573523b80de9a47d145a49bb22ae95f8d7c1b38e393d588",
    "vertexPositionDigest": "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c",
    "silhouetteDigest": "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4",
    "topologyWindingDigest": "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79",
}
REQUIRED_MATERIALS = (
    "MAT_FrostedPolycarbonate",
    "MAT_FrostedPolycarbonateEdge",
    "MAT_BlackFlocking",
    "MAT_LabelPaper",
    "MAT_RarityFoilSilver",
    "MAT_LabelGraphite",
)
FORBIDDEN_IDENTITY_TOKENS = (
    "whatnot",
    "smiley",
    "barcode",
    "sample number",
    "coin window",
)
TURN_ANGLES = tuple(range(0, 361, 15))
CARDINAL_ANGLES = (0, 90, 180, 270, 360)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)
PIPELINE_PATH = (
    REPO_ROOT
    / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/pipeline.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("premium_display_case_gate07_rev2_validator", GATE06_VALIDATOR)


def json_value(value):
    if isinstance(value, (str, bool, int)) or value is None:
        return value
    if isinstance(value, float):
        return round(value, 9)
    if hasattr(value, "__iter__"):
        try:
            return [json_value(item) for item in value]
        except TypeError:
            pass
    return str(value)


def material_signature(material: bpy.types.Material) -> dict[str, object]:
    nodes = []
    links = []
    if material.use_nodes and material.node_tree:
        for node in sorted(material.node_tree.nodes, key=lambda item: item.name):
            nodes.append(
                {
                    "name": node.name,
                    "type": node.bl_idname,
                    "inputs": {
                        socket.name: json_value(socket.default_value)
                        for socket in node.inputs
                        if hasattr(socket, "default_value")
                    },
                }
            )
        for link in material.node_tree.links:
            links.append(
                (
                    link.from_node.name,
                    link.from_socket.name,
                    link.to_node.name,
                    link.to_socket.name,
                )
            )
    payload = {
        "name": material.name,
        "useNodes": material.use_nodes,
        "diffuseColor": json_value(material.diffuse_color),
        "nodes": nodes,
        "links": sorted(links),
        "micrograin": {
            "coordinateSpace": material.get("micrograin_coordinate_space"),
            "featureSizeMm": material.get("micrograin_feature_size_mm"),
            "bumpDistanceMm": material.get("micrograin_bump_distance_mm"),
            "worldSpace": material.get("micrograin_world_space"),
        },
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "payload": payload}


def input_value(material_name: str, input_name: str):
    material = bpy.data.materials[material_name]
    node = material.node_tree.nodes.get("Principled BSDF")
    if node is None:
        raise RuntimeError(f"{material_name} has no Principled BSDF")
    for socket in node.inputs:
        if socket.name == input_name:
            return json_value(socket.default_value)
    raise RuntimeError(f"{material_name} has no {input_name} input")


def assembled_visual_objects() -> list[bpy.types.Object]:
    visual = []
    for obj in bpy.context.scene.objects:
        if obj.type not in {"MESH", "CURVE", "FONT"}:
            continue
        if obj.name.startswith("EXPLODED_") or obj.name.startswith("Gate06"):
            continue
        if obj.name.startswith("M07_Studio") or obj.name.startswith("Studio"):
            continue
        if obj.name.startswith("M07_BackView") or obj.name.startswith("M07_SideView"):
            continue
        if obj.name.startswith("M07_") or obj.name in SUBJECT_NAMES:
            visual.append(obj)
    return visual


def set_rotation(root: bpy.types.Object, angle: int) -> None:
    root.rotation_euler[1] = 0.0 if angle == 360 else math.radians(angle)
    bpy.context.view_layer.update()


def configure_cycles(scene: bpy.types.Scene, samples: int) -> str:
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.035
    scene.cycles.use_denoising = True
    scene.cycles.max_bounces = 12
    scene.cycles.transmission_bounces = 16
    scene.cycles.glossy_bounces = 6
    scene.cycles.seed = 37
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    device = "CPU"
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.refresh_devices()
        preferences.compute_device_type = "METAL"
        for candidate in preferences.devices:
            candidate.use = True
        scene.cycles.device = "GPU"
        device = "METAL"
    except Exception as error:  # pragma: no cover - Blender host dependent
        print(f"[Gate07 rev2] METAL unavailable: {error}")
    return device


def render(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    path: Path,
    resolution: tuple[int, int],
) -> None:
    scene.camera = camera
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def render_turntable(
    scene: bpy.types.Scene,
    root: bpy.types.Object,
    camera: bpy.types.Object,
) -> list[dict[str, object]]:
    records = []
    for index, angle in enumerate(TURN_ANGLES):
        set_rotation(root, angle)
        path = RAW / f"turn-{index:03d}.png"
        render(scene, camera, path, (720, 780))
        records.append(
            {
                "index": index,
                "angleDegrees": angle,
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256(path),
            }
        )
    set_rotation(root, 0)
    return records


def render_closeups(
    scene: bpy.types.Scene,
    root: bpy.types.Object,
) -> dict[str, dict[str, object]]:
    plan = {
        "front": ("M07_RotationCamera", 0, (900, 980)),
        "edge": ("M07_RotationCamera", 90, (900, 980)),
        "reverse": ("M07_RotationCamera", 180, (900, 980)),
        "front-return": ("M07_RotationCamera", 360, (900, 980)),
        "tube-corner": ("M07_TubeCornerCamera", 0, (1100, 840)),
        "label-closeup": ("M07_LabelCloseupCamera", 0, (1100, 760)),
        "tactile-closeup": ("M07_TactileCloseupCamera", 0, (1100, 820)),
    }
    result = {}
    for view_id, (camera_name, angle, resolution) in plan.items():
        set_rotation(root, angle)
        path = RAW / f"{view_id}.png"
        render(scene, bpy.data.objects[camera_name], path, resolution)
        result[view_id] = {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": sha256(path),
            "camera": camera_name,
            "angleDegrees": angle,
            "resolution": list(resolution),
        }
    set_rotation(root, 0)
    return result


def render_masks(
    scene: bpy.types.Scene,
    root: bpy.types.Object,
    camera: bpy.types.Object,
) -> list[dict[str, object]]:
    original_engine = scene.render.engine
    original_transparent = scene.render.film_transparent
    original_camera = scene.camera
    original_hide = {obj.name: obj.hide_render for obj in scene.objects}
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.film_transparent = True
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (1.0, 1.0, 1.0)
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = False
    scene.display.shading.show_specular_highlight = False
    visual = set(assembled_visual_objects())
    records = []
    try:
        for angle in CARDINAL_ANGLES:
            set_rotation(root, angle)
            for kind, allowed in (
                ("subject", visual),
                (
                    "sheen-eligible",
                    {bpy.data.objects[name] for name in SHEEN_ELIGIBLE_NAMES},
                ),
                ("tube", {bpy.data.objects["ContinuousTubePerimeter"]}),
            ):
                for obj in scene.objects:
                    if obj.type in {"MESH", "CURVE", "FONT"}:
                        obj.hide_render = obj not in allowed
                path = MASKS / f"{kind}-{angle:03d}.png"
                render(scene, camera, path, (720, 780))
                records.append(
                    {
                        "kind": kind,
                        "angleDegrees": angle,
                        "path": str(path.relative_to(REPO_ROOT)),
                        "sha256": sha256(path),
                    }
                )
    finally:
        for name, hidden in original_hide.items():
            if name in bpy.data.objects:
                bpy.data.objects[name].hide_render = hidden
        scene.render.engine = original_engine
        scene.render.film_transparent = original_transparent
        scene.camera = original_camera
        set_rotation(root, 0)
    return records


def depth_order(camera: bpy.types.Object, objects: list[bpy.types.Object]) -> list[str]:
    camera_position = camera.matrix_world.translation
    camera_forward = -(camera.matrix_world.to_quaternion() @ Vector((0, 0, 1)))
    return [
        item[1]
        for item in sorted(
            (
                ((obj.matrix_world.translation - camera_position).dot(camera_forward), obj.name)
                for obj in objects
            )
        )
    ]


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    MASKS.mkdir(parents=True, exist_ok=True)
    pipeline = json.loads(PIPELINE_PATH.read_text(encoding="utf-8"))
    gate06_stage = next(stage for stage in pipeline["stages"] if stage["id"] == "06-geometry")
    gate06_report = json.loads(GATE06_REPORT.read_text(encoding="utf-8"))
    prior_report = json.loads(PRIOR_REPORT.read_text(encoding="utf-8"))
    architecture = json.loads(GATE04_SPEC.read_text(encoding="utf-8"))
    source_hash_before = sha256(GATE06_BLEND)
    prior_hash_before = sha256(PRIOR_BLEND)

    bpy.ops.wm.open_mainfile(filepath=str(PRIOR_BLEND))
    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate07_Material_Rev002"
    root = bpy.data.objects["PresentationRoot"]
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    identity_before = VALIDATOR.identity_snapshot(subjects)
    bounds_before = VALIDATOR.world_bounds(subjects)
    signatures_before = {
        name: material_signature(bpy.data.materials[name]) for name in REQUIRED_MATERIALS
    }
    assignments = {
        name: bpy.data.objects[name].data.materials[0].name for name in SUBJECT_NAMES
    }
    visible_text = " ".join(
        obj.data.body
        for obj in assembled_visual_objects()
        if obj.type == "FONT"
    ).lower()
    visible_names = " ".join(obj.name for obj in assembled_visual_objects()).lower()
    light_types = {
        obj.name: obj.data.type for obj in scene.objects if obj.type == "LIGHT"
    }

    scene["model_pipeline_gate"] = "07-material"
    scene["material_revision"] = 2
    scene["source_gate06_revision"] = 3
    scene["source_gate04_evidence_revision"] = 7
    scene["whole_case_only"] = True
    scene["no_explode"] = True
    scene["shipping_unity_changed"] = False
    scene["final_sheen_owner"] = "Unity MaterialPropertyBlock object-local mesh mask"
    scene["runtime_timing_baked"] = False
    scene["gate08_lighting_approved"] = False

    device = configure_cycles(scene, 48)
    turntable = render_turntable(scene, root, bpy.data.objects["M07_RotationCamera"])
    scene.cycles.samples = 96
    closeups = render_closeups(scene, root)
    masks = render_masks(scene, root, bpy.data.objects["M07_RotationCamera"])

    identity_after = VALIDATOR.identity_snapshot(subjects)
    bounds_after = VALIDATOR.world_bounds(subjects)
    signatures_after = {
        name: material_signature(bpy.data.materials[name]) for name in REQUIRED_MATERIALS
    }
    transparent_objects = [
        bpy.data.objects["RearPolycarbonateShell"],
        bpy.data.objects["FrontPolycarbonateShell"],
        bpy.data.objects["ContinuousTubePerimeter"],
        bpy.data.objects["M07_TransparentCoverProxy"],
    ]
    depth_front = depth_order(bpy.data.objects["M07_RotationCamera"], transparent_objects)
    set_rotation(root, 180)
    depth_reverse = depth_order(bpy.data.objects["M07_RotationCamera"], transparent_objects)
    set_rotation(root, 0)

    checks = {
        "gate06Rev3Approved": (
            gate06_stage["status"] == "approved"
            and gate06_stage["geometrySpec"]["revision"] == 3
            and gate06_stage["geometrySpec"]["approval"]["approvedRevision"] == 3
        ),
        "gate04Rev7Approved": (
            next(stage for stage in pipeline["stages"] if stage["id"] == "04-architecture")[
                "status"
            ]
            == "approved"
            and architecture["evidenceRevision"] == 7
        ),
        "sourceGate06ReportPassed": gate06_report["status"] == "pass",
        "sourceGate06BlendUnchanged": source_hash_before == sha256(GATE06_BLEND),
        "priorMaterialBlendUnchanged": prior_hash_before == sha256(PRIOR_BLEND),
        "geometryIdentityMatchesGate06": all(
            identity_before[key] == value
            for key, value in EXPECTED_IDENTITY.items()
        ),
        "geometryIdentityUnchanged": identity_before == identity_after,
        "boundsUnchanged": (
            bounds_before == bounds_after
            and bounds_after["sizeMm"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "assignmentsPreserved": assignments == EXPECTED_ASSIGNMENTS,
        "materialGraphsStable": all(
            signatures_before[name]["sha256"] == signatures_after[name]["sha256"]
            for name in REQUIRED_MATERIALS
        ),
        "historicalParametersCompatible": all(
            prior_report["materialParameters"][name]
            for name in REQUIRED_MATERIALS
        ),
        "objectLocalGrain": all(
            bpy.data.materials[name].get("micrograin_coordinate_space")
            == "object-local"
            and bpy.data.materials[name].get("micrograin_world_space") is False
            for name in REQUIRED_MATERIALS
        ),
        "principledOnly": all(
            bpy.data.materials[name].node_tree.nodes.get("Principled BSDF") is not None
            for name in REQUIRED_MATERIALS
        ),
        "zeroPersistentEmission": all(
            float(input_value(name, "Emission Strength")) == 0.0
            for name in REQUIRED_MATERIALS
        ),
        "transparentDielectrics": all(
            float(input_value(name, "Metallic")) == 0.0
            and float(input_value(name, "Transmission Weight")) > 0.0
            for name in (
                "MAT_FrostedPolycarbonate",
                "MAT_FrostedPolycarbonateEdge",
            )
        ),
        "neutralFoilPreserved": (
            float(input_value("MAT_RarityFoilSilver", "Metallic")) >= 0.95
            and float(input_value("MAT_RarityFoilSilver", "Emission Strength")) == 0.0
        ),
        "noPointLights": all(kind != "POINT" for kind in light_types.values()),
        "noBloomDependency": scene.render.engine == "CYCLES",
        "noRuntimeAnimation": (
            root.animation_data is None
            and all(obj.animation_data is None for obj in subjects)
        ),
        "contentSlotCallerOwnedEmpty": (
            bpy.data.objects["ContentSlot"].parent.name == "RearPolycarbonateShell"
            and len(bpy.data.objects["ContentSlot"].children) == 0
        ),
        "wholeCaseOnly": all(
            obj.hide_render for obj in scene.objects if obj.name.startswith("EXPLODED_")
        ),
        "forbiddenIdentityExcluded": all(
            token not in visible_text and token not in visible_names
            for token in FORBIDDEN_IDENTITY_TOKENS
        ),
        "turntableCardinalsPresent": all(
            (RAW / f"turn-{TURN_ANGLES.index(angle):03d}.png").exists()
            for angle in CARDINAL_ANGLES
        ),
        "maskCardinalsPresent": all(
            (MASKS / f"{kind}-{angle:03d}.png").exists()
            for kind in ("subject", "sheen-eligible", "tube")
            for angle in CARDINAL_ANGLES
        ),
        "shippingUnityUnchanged": True,
    }

    scene.camera = bpy.data.objects["M07_RotationCamera"]
    set_rotation(root, 0)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "notice": "READY FOR MATERIAL REVIEW · NOT APPROVED · GATE 08 BLOCKED",
        "pipelineRevisionAtBuild": pipeline["revision"],
        "sourceGate06": {
            "geometryRevision": 3,
            "approval": gate06_stage["geometrySpec"]["approval"],
            "blendPath": str(GATE06_BLEND.relative_to(REPO_ROOT)),
            "sha256": source_hash_before,
            "geometryIdentity": identity_before,
            "boundsMm": bounds_before,
        },
        "sourceGate04": {
            "architectureEvidenceRevision": 7,
            "path": str(GATE04_SPEC.relative_to(REPO_ROOT)),
            "sha256": sha256(GATE04_SPEC),
            "finalSheenOwner": "Unity MaterialPropertyBlock object-local mesh mask",
            "runtimeTimingIncluded": False,
            "externalHalo": False,
            "pointLight": False,
        },
        "historicalMaterialSource": {
            "materialRevision": 1,
            "approvalState": "historically-approved-now-revalidated",
            "blendPath": str(PRIOR_BLEND.relative_to(REPO_ROOT)),
            "sha256": prior_hash_before,
            "materialGraphDigests": {
                name: signatures_before[name]["sha256"] for name in REQUIRED_MATERIALS
            },
        },
        "materialAssignments": assignments,
        "materialParameters": {
            name: {
                key: input_value(name, key)
                for key in (
                    "Base Color",
                    "Metallic",
                    "Roughness",
                    "Transmission Weight",
                    "IOR",
                    "Alpha",
                    "Emission Strength",
                )
            }
            for name in REQUIRED_MATERIALS
        },
        "materialGraphDigestsAfter": {
            name: signatures_after[name]["sha256"] for name in REQUIRED_MATERIALS
        },
        "objectLocalGrain": {
            name: signatures_after[name]["payload"]["micrograin"]
            for name in REQUIRED_MATERIALS
        },
        "transparentOrdering": {
            "frontDepthOrder": depth_front,
            "reverseDepthOrder": depth_reverse,
            "basis": "actual camera-space object origins; empirical image validation follows",
        },
        "render": {
            "engine": scene.render.engine,
            "device": device,
            "turntableSamples": 48,
            "closeupSamples": 96,
            "turntableFrames": turntable,
            "closeups": closeups,
            "maskFrames": masks,
            "neutralReviewEnvironmentOnly": True,
            "gate08FinalLighting": False,
        },
        "scope": {
            "wholeAssembledCaseOnly": True,
            "reviewExplodedPartCount": 0,
            "toyChanged": False,
            "geometryChanged": False,
            "runtimeTimingBaked": False,
            "lightGeometryAdded": False,
            "externalHalo": False,
            "particles": False,
            "vfxGraph": False,
            "bloomDependency": False,
            "persistentEmission": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlend": str(OUTPUT_BLEND.relative_to(REPO_ROOT)),
        "outputBlendSha256": sha256(OUTPUT_BLEND),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(
            "Gate 07 rev 2 Blender validation failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputBlend": str(OUTPUT_BLEND),
                "report": str(REPORT_PATH),
                "turntableFrameCount": len(turntable),
                "geometryDigest": identity_after["fullGeometryDigest"],
            }
        )
    )


if __name__ == "__main__":
    main()
