#!/usr/bin/env python3
"""Build the immutable Premium Display Case Gate 10 product export package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent.parent
SOURCE = EVIDENCE / "07-material/rev-002/premium-display-case-material-r002.blend"
SOURCE_REPORT = EVIDENCE / "07-material/rev-002/material-revalidation.json"
GEOMETRY_VALIDATOR_PATH = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
PRODUCT_BLEND = HERE / "premium-display-case-product-r001.blend"
FBX_EXPORT = HERE / "premium-display-case-product-r001.fbx"
GLB_EXPORT = HERE / "premium-display-case-product-r001.glb"
BUILD_REPORT = HERE / "export-build-report.json"

EXPECTED_SOURCE_SHA256 = (
    "076f5dd07f8e611ceaaabb7d1a92790659a7fcf9c1dd04dcd8e1fc7e9684dd49"
)
EXPECTED_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)
EXPECTED_MATERIAL_DIGEST = (
    "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
)
EXPECTED_GATE09_QUOTE = "环境正确，批准并继续（推荐）"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
PRODUCT_OBJECTS = (
    "PresentationRoot",
    "CaseAssembly",
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "ContentSlot",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
    "LogoZone",
    "AchievementZone",
    "NarrowFoil",
    "TransparentCover",
)
EXPECTED_PARENTS = {
    "PresentationRoot": None,
    "CaseAssembly": "PresentationRoot",
    "RearPolycarbonateShell": "CaseAssembly",
    "TactileBackgroundInsert": "RearPolycarbonateShell",
    "ContentSlot": "RearPolycarbonateShell",
    "FrontPolycarbonateShell": "CaseAssembly",
    "ContinuousTubePerimeter": "FrontPolycarbonateShell",
    "PhysicalLabel": "FrontPolycarbonateShell",
    "LogoZone": "PhysicalLabel",
    "AchievementZone": "PhysicalLabel",
    "NarrowFoil": "PhysicalLabel",
    "TransparentCover": "FrontPolycarbonateShell",
}
EXPECTED_ASSIGNMENTS = {
    "RearPolycarbonateShell": ["MAT_FrostedPolycarbonate"],
    "TactileBackgroundInsert": ["MAT_BlackFlocking"],
    "FrontPolycarbonateShell": ["MAT_FrostedPolycarbonate"],
    "ContinuousTubePerimeter": ["MAT_FrostedPolycarbonateEdge"],
    "PhysicalLabel": ["MAT_LabelPaper"],
}
PRODUCT_MATERIALS = {
    "MAT_FrostedPolycarbonate",
    "MAT_FrostedPolycarbonateEdge",
    "MAT_BlackFlocking",
    "MAT_LabelPaper",
    "MAT_RarityFoilSilver",
    "MAT_LabelGraphite",
}
FORBIDDEN_NAME_TOKENS = (
    "proxy",
    "placeholder",
    "primary",
    "secondary",
    "metadata",
    "exploded",
    "camera",
    "light",
    "cyclorama",
    "backdrop",
    "studioground",
    "particle",
    "halo",
    "toy",
    "prize",
)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(HERE)
PIPELINE = REPO_ROOT / (
    "unity/FidgetingApp/ArtSource/ModelPipeline/"
    "premium-display-case/pipeline.json"
)
HISTORY = REPO_ROOT / (
    "unity/FidgetingApp/ArtSource/ModelPipeline/"
    "premium-display-case/history.ndjson"
)


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


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


GEOMETRY_VALIDATOR = load_module(
    "premium_display_case_gate10_geometry_validator",
    GEOMETRY_VALIDATOR_PATH,
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def gate09_approval_event(pipeline_revision: int) -> dict:
    events = [
        json.loads(line)
        for line in HISTORY.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matches = [
        event
        for event in events
        if event.get("type") == "stage-approved"
        and event.get("stageId") == "09-environment"
        and event.get("manifestRevision") == pipeline_revision
    ]
    if len(matches) != 1:
        raise RuntimeError("Expected one Gate 09 approval event at the live revision.")
    return matches[0]


def object_depth(obj: bpy.types.Object) -> int:
    depth = 0
    parent = obj.parent
    while parent is not None:
        depth += 1
        parent = parent.parent
    return depth


def normalize_parent_inverses() -> None:
    """Keep world transforms while making exported local transforms explicit."""
    objects = sorted(bpy.context.scene.objects, key=object_depth)
    world_matrices = {obj.name: obj.matrix_world.copy() for obj in objects}
    for obj in objects:
        world = world_matrices[obj.name]
        obj.matrix_parent_inverse = Matrix.Identity(4)
        if obj.parent is None:
            obj.matrix_world = world
        else:
            obj.matrix_basis = obj.parent.matrix_world.inverted() @ world
    bpy.context.view_layer.update()


def add_label_uv() -> None:
    obj = bpy.data.objects["PhysicalLabel"]
    mesh = obj.data
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])
    uv_layer = mesh.uv_layers.new(name="LabelUV")
    minimum_x = min(vertex.co.x for vertex in mesh.vertices)
    maximum_x = max(vertex.co.x for vertex in mesh.vertices)
    minimum_y = min(vertex.co.y for vertex in mesh.vertices)
    maximum_y = max(vertex.co.y for vertex in mesh.vertices)
    width = maximum_x - minimum_x
    height = maximum_y - minimum_y
    if width <= 0 or height <= 0:
        raise RuntimeError("PhysicalLabel cannot receive a planar UV map.")
    for loop in mesh.loops:
        coordinate = mesh.vertices[loop.vertex_index].co
        uv_layer.data[loop.index].uv = (
            (coordinate.x - minimum_x) / width,
            (coordinate.y - minimum_y) / height,
        )
    mesh.update()
    obj["uv_contract"] = "LabelUV planar X/Y; authoritative content supplied by Unity"
    obj["runtime_content_authority"] = "Unity"
    obj["placeholder_text_baked"] = False
    obj["fake_collectible_id_baked"] = False


def strip_to_product() -> None:
    missing = sorted(set(PRODUCT_OBJECTS) - set(bpy.data.objects.keys()))
    if missing:
        raise RuntimeError(f"Approved product objects are missing: {missing}")
    for obj in list(bpy.data.objects):
        if obj.name not in PRODUCT_OBJECTS:
            bpy.data.objects.remove(obj, do_unlink=True)
    normalize_parent_inverses()

    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    for obj in bpy.context.scene.objects:
        obj.animation_data_clear()
        obj.hide_render = False
        obj.hide_viewport = False
        obj["gate10_product_object"] = True

    add_label_uv()

    presentation = bpy.data.objects["PresentationRoot"]
    assembly = bpy.data.objects["CaseAssembly"]
    content_slot = bpy.data.objects["ContentSlot"]
    presentation["runtime_animation_owner"] = "Unity PresentationRoot"
    presentation["runtime_animation_baked"] = False
    presentation["runtime_light_cues_baked"] = False
    presentation["runtime_path_baked"] = False
    assembly["assembly_state"] = "whole-assembled-case"
    content_slot["ownership"] = "caller-owned"
    content_slot["bundled_content_count"] = 0
    content_slot["independent_angular_velocity"] = 0.0

    zone_contracts = {
        "LogoZone": ("runtime-label-anchor", "MAT_LabelGraphite"),
        "AchievementZone": ("runtime-label-anchor", "MAT_LabelGraphite"),
        "NarrowFoil": ("material-zone-contour", "MAT_RarityFoilSilver"),
        "TransparentCover": (
            "material-zone-contour-no-approved-thickness",
            "MAT_FrostedPolycarbonate",
        ),
    }
    for name, (role, material) in zone_contracts.items():
        zone = bpy.data.objects[name]
        zone["gate10_export_role"] = role
        zone["unity_material_hint"] = material
        zone["proxy_geometry_included"] = False

    for material in list(bpy.data.materials):
        if material.name in PRODUCT_MATERIALS:
            material.use_fake_user = True
        else:
            bpy.data.materials.remove(material)
    for collection in list(bpy.data.collections):
        if collection.users == 0:
            bpy.data.collections.remove(collection)

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.camera = None
    scene.render.engine = "BLENDER_EEVEE"
    scene["gate10_product_only"] = True
    scene["authoring_axis_contract"] = "X-width/Y-height/Z-front"
    scene["authoring_units"] = "millimeters"
    scene["runtime_animation_owner"] = "Unity"
    scene["label_content_authority"] = "Unity runtime data"
    scene["collision_policy"] = "none; no approved proxy exists"
    if scene.world is not None:
        scene.world.use_nodes = False
        scene.world.color = (0.0, 0.0, 0.0)


def matrix_is_identity(obj: bpy.types.Object, tolerance: float = 1e-8) -> bool:
    identity = Matrix.Identity(4)
    return all(
        abs(obj.matrix_world[row][column] - identity[row][column]) <= tolerance
        for row in range(4)
        for column in range(4)
    )


def material_assignments() -> dict[str, list[str]]:
    return {
        name: [
            material.name
            for material in bpy.data.objects[name].data.materials
            if material is not None
        ]
        for name in SUBJECT_NAMES
    }


def parent_map() -> dict[str, str | None]:
    return {
        name: (
            bpy.data.objects[name].parent.name
            if bpy.data.objects[name].parent is not None
            else None
        )
        for name in PRODUCT_OBJECTS
    }


def product_scene_checks(identity: dict, bounds: dict) -> dict[str, bool]:
    presentation = bpy.data.objects["PresentationRoot"]
    content_slot = bpy.data.objects["ContentSlot"]
    physical_label = bpy.data.objects["PhysicalLabel"]
    object_names = set(bpy.context.scene.objects.keys())
    return {
        "approvedGate09Live": True,
        "sourceHashExact": sha256(SOURCE) == EXPECTED_SOURCE_SHA256,
        "geometryDigestExact": (
            identity["fullGeometryDigest"] == EXPECTED_GEOMETRY_DIGEST
        ),
        "boundsExact": bounds["sizeMm"] == {
            "width": 228.0,
            "height": 304.0,
            "depth": 59.0,
        },
        "productObjectSetExact": object_names == set(PRODUCT_OBJECTS),
        "hierarchyExact": parent_map() == EXPECTED_PARENTS,
        "presentationRootIdentity": matrix_is_identity(presentation),
        "contentSlotEmpty": len(content_slot.children) == 0,
        "labelCenterYExact": (
            round(physical_label.matrix_world.translation.y, 6) == 99.0
        ),
        "labelUvPresent": (
            [layer.name for layer in physical_label.data.uv_layers] == ["LabelUV"]
        ),
        "materialAssignmentsExact": material_assignments() == EXPECTED_ASSIGNMENTS,
        "fiveRenderMeshes": sum(
            obj.type == "MESH" for obj in bpy.context.scene.objects
        ) == 5,
        "noCamerasLightsOrFonts": not any(
            obj.type in {"CAMERA", "LIGHT", "FONT", "CURVE"}
            for obj in bpy.context.scene.objects
        ),
        "noForbiddenObjects": not any(
            token in name.lower()
            for name in object_names
            for token in FORBIDDEN_NAME_TOKENS
        ),
        "noAnimation": (
            not bpy.data.actions
            and all(obj.animation_data is None for obj in bpy.context.scene.objects)
        ),
        "noBundledToyOrPrize": not any(
            token in name.lower()
            for name in object_names
            for token in ("toy", "prize")
        ),
        "noProxyOrExplodedGeometry": not any(
            token in name.lower()
            for name in object_names
            for token in ("proxy", "exploded")
        ),
        "zoneMetadataPresent": all(
            bpy.data.objects[name].get("gate10_export_role")
            for name in ("LogoZone", "AchievementZone", "NarrowFoil", "TransparentCover")
        ),
        "runtimeContentNotBaked": (
            physical_label.get("placeholder_text_baked") is False
            and physical_label.get("fake_collectible_id_baked") is False
        ),
        "collisionNotInvented": not any(
            token in name.lower()
            for name in object_names
            for token in ("collider", "collision", "ucx_")
        ),
    }


def convert_scene_for_export(basis: Matrix) -> None:
    """Convert explicit local coordinates from authored mm to exported metres."""
    for obj in bpy.context.scene.objects:
        obj.location = basis @ (obj.location * 0.001)
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        if obj.type == "MESH":
            for vertex in obj.data.vertices:
                vertex.co = basis @ (vertex.co * 0.001)
            obj.data.update()
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "METERS"
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.view_layer.update()


def select_product() -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.context.scene.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["PresentationRoot"]


def export_glb() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(PRODUCT_BLEND))
    convert_scene_for_export(Matrix.Identity(3))
    select_product()
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_EXPORT),
        export_format="GLB",
        use_selection=True,
        export_yup=False,
        export_apply=False,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_extras=True,
    )


def export_fbx() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(PRODUCT_BLEND))
    basis = Matrix.Rotation(math.radians(90.0), 3, "X")
    convert_scene_for_export(basis)
    select_product()
    bpy.ops.export_scene.fbx(
        filepath=str(FBX_EXPORT),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        global_scale=1.0,
        apply_unit_scale=False,
        apply_scale_options="FBX_SCALE_NONE",
        use_space_transform=True,
        bake_space_transform=False,
        axis_forward="-Z",
        axis_up="Y",
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        embed_textures=False,
        path_mode="AUTO",
        use_metadata=True,
    )


def main() -> None:
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Approved Gate 07 material source hash changed.")
    pipeline = load_json(PIPELINE)
    if pipeline["revision"] != 67:
        raise RuntimeError(
            f"Expected live pipeline revision 67, got {pipeline['revision']}."
        )
    gate09 = pipeline["stages"][8]
    gate10 = pipeline["stages"][9]
    approval = gate09.get("environmentSpec", {}).get("approval", {})
    if (
        gate09["status"] != "approved"
        or approval.get("approvedRevision") != 1
        or approval.get("userApprovalQuote") != EXPECTED_GATE09_QUOTE
        or gate10["status"] not in {"blocked", "stale"}
        or gate10["artifactIds"]
    ):
        raise RuntimeError("Gate 09 approval or empty Gate 10 live state changed.")
    approval_event = gate09_approval_event(pipeline["revision"])

    source_report = load_json(SOURCE_REPORT)
    if (
        source_report["outputBlendSha256"] != EXPECTED_SOURCE_SHA256
        or source_report["sourceGate06"]["geometryIdentity"]["fullGeometryDigest"]
        != EXPECTED_GEOMETRY_DIGEST
        or source_report["materialGraphDigestsAfter"] is None
    ):
        raise RuntimeError("Approved source report does not match Gate 10 inputs.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    strip_to_product()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    identity = GEOMETRY_VALIDATOR.identity_snapshot(subjects)
    bounds = GEOMETRY_VALIDATOR.world_bounds(subjects)
    checks = product_scene_checks(identity, bounds)
    if not all(checks.values()):
        raise RuntimeError(json.dumps(checks, indent=2))
    bpy.ops.wm.save_as_mainfile(filepath=str(PRODUCT_BLEND), check_existing=False)

    bpy.ops.wm.open_mainfile(filepath=str(PRODUCT_BLEND))
    saved_identity = GEOMETRY_VALIDATOR.identity_snapshot(
        [bpy.data.objects[name] for name in SUBJECT_NAMES]
    )
    saved_bounds = GEOMETRY_VALIDATOR.world_bounds(
        [bpy.data.objects[name] for name in SUBJECT_NAMES]
    )
    if (
        saved_identity["fullGeometryDigest"] != EXPECTED_GEOMETRY_DIGEST
        or saved_bounds != bounds
    ):
        raise RuntimeError("Product-only Blender save changed approved geometry.")

    export_fbx()
    export_glb()
    for path in (PRODUCT_BLEND, FBX_EXPORT, GLB_EXPORT):
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError(f"Export is missing: {path}")

    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "notice": "GATE 10 REV 1 EXPORT · BUILT · ROUND-TRIP VALIDATION REQUIRED",
        "blender": bpy.app.version_string,
        "pipelineRevisionAtBuild": pipeline["revision"],
        "sourceGate09": {
            "environmentRevision": 1,
            "approvalEventId": approval_event["id"],
            "approvalQuote": approval["userApprovalQuote"],
            "approvalScope": approval["approvalScope"],
        },
        "sourceGate07": {
            "blendPath": repo_path(SOURCE),
            "blendSha256": EXPECTED_SOURCE_SHA256,
            "materialDigest": EXPECTED_MATERIAL_DIGEST,
        },
        "geometry": {
            "approvedDigest": EXPECTED_GEOMETRY_DIGEST,
            "productBlendDigest": saved_identity["fullGeometryDigest"],
            "identity": saved_identity,
            "boundsMm": saved_bounds,
            "labelCenterYmm": 99.0,
            "unchanged": True,
        },
        "hierarchy": {
            "parents": EXPECTED_PARENTS,
            "runtimeMotionOwner": "PresentationRoot",
            "rigidAssembly": "CaseAssembly",
            "contentSlot": "caller-owned-empty",
            "sameWholeCase": True,
        },
        "materials": {
            "approvedDigest": EXPECTED_MATERIAL_DIGEST,
            "assignments": EXPECTED_ASSIGNMENTS,
            "retainedMaterialNames": sorted(PRODUCT_MATERIALS),
            "labelZones": {
                "paperGeometry": "PhysicalLabel",
                "uvLayer": "LabelUV",
                "transparentCover": "TransparentCover metadata contour",
                "narrowFoil": "NarrowFoil metadata contour",
                "runtimeAnchors": ["LogoZone", "AchievementZone"],
            },
        },
        "runtimeBoundary": {
            "labelContentAuthority": "Unity runtime data",
            "placeholderTextBaked": False,
            "fakeCollectibleIdBaked": False,
            "animationBaked": False,
            "timingBaked": False,
            "easingBaked": False,
            "entryPathBaked": False,
            "showcaseRotationBaked": False,
            "lightCuesBaked": False,
        },
        "excluded": {
            "toyPrize": True,
            "proxyGeometry": True,
            "explodedGeometry": True,
            "lightGeometry": True,
            "externalHalo": True,
            "particlesVfx": True,
            "cameraBackground": True,
            "collisionGeometry": True,
        },
        "collision": {
            "included": False,
            "reason": "No approved collision or selection proxy exists; Gate 10 invents none.",
        },
        "exports": {
            "blend": {
                "path": repo_path(PRODUCT_BLEND),
                "sha256": sha256(PRODUCT_BLEND),
                "authoringUnits": "millimeters",
                "axisContract": "X-width/Y-height/Z-front",
            },
            "fbx": {
                "path": repo_path(FBX_EXPORT),
                "sha256": sha256(FBX_EXPORT),
                "encodedUnits": "meters",
                "axisContract": "Y-up/-Z-forward for Unity",
                "animations": False,
            },
            "glb": {
                "path": repo_path(GLB_EXPORT),
                "sha256": sha256(GLB_EXPORT),
                "encodedUnits": "meters",
                "axisContract": "Y-up portable GLB",
                "animations": False,
            },
        },
        "checks": checks,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    BUILD_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
