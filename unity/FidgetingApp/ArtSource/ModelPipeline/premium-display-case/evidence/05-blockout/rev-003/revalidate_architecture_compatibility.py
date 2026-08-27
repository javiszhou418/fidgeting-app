#!/usr/bin/env python3
"""Revalidate the approved Gate 05 white model against Gate 04 rev 7."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
REV2 = ROOT.parent / "rev-002"
SOURCE_BLEND = REV2 / "premium-display-case-blockout.blend"
SOURCE_VALIDATOR = REV2 / "validate_blockout.py"
OUTPUT_BLEND = ROOT / "premium-display-case-blockout-r003.blend"
OUTPUT_REPORT = ROOT / "architecture-compatibility-audit.json"
HERO = ROOT / "white-model-hero.png"
FRONT = ROOT / "white-model-front.png"

EXPECTED_SOURCE_BLEND_SHA256 = "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31"
EXPECTED_GEOMETRY_DIGEST = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_HIERARCHY = {
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
FORBIDDEN_NAME_FRAGMENTS = ("halo", "vfx", "particle", "proxy", "explode", "split")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate05_rev2_validator",
        SOURCE_VALIDATOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SOURCE_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def geometry_digest(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in sorted(objects, key=lambda item: item.name):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            digest.update(obj.name.encode())
            for row in obj.matrix_world:
                for value in row:
                    digest.update(f"{value:.12f}".encode())
            for vertex in mesh.vertices:
                digest.update(
                    f"{vertex.co.x:.12f},{vertex.co.y:.12f},{vertex.co.z:.12f};".encode()
                )
            for polygon in mesh.polygons:
                digest.update(
                    (",".join(str(index) for index in polygon.vertices) + ";").encode()
                )
        finally:
            evaluated.to_mesh_clear()
    return digest.hexdigest()


def render(camera_name: str, output: Path, size: tuple[int, int]) -> None:
    scene = bpy.context.scene
    scene.camera = bpy.data.objects[camera_name]
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(output)
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)


def main() -> None:
    if sha256(SOURCE_BLEND) != EXPECTED_SOURCE_BLEND_SHA256:
        raise RuntimeError("The immutable Gate 05 rev 2 source blend hash changed.")

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    validator = load_validator()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    digest_before = geometry_digest(subjects)
    structural = validator.validate_scene()
    root = bpy.data.objects["PresentationRoot"]

    removed_stale_runtime_properties = []
    for property_name in (
        "motion_owner",
        "locked_total_duration_seconds",
    ):
        if property_name in root:
            del root[property_name]
            removed_stale_runtime_properties.append(property_name)
    root["blender_ownership"] = "geometry-pivot-uv-material-zones"
    root["unity_runtime_owner"] = "GachaRevealDirector"
    root["runtime_motion_baked"] = False
    root["runtime_light_baked"] = False
    root["gate04_architecture_evidence_revision"] = 7

    actual_hierarchy = {
        name: (bpy.data.objects[name].parent.name if bpy.data.objects[name].parent else None)
        for name in EXPECTED_HIERARCHY
    }
    animated_subjects = [
        obj.name
        for obj in (root, bpy.data.objects["CaseAssembly"], *subjects)
        if obj.animation_data is not None
    ]
    content_slot = bpy.data.objects["ContentSlot"]
    content_slot_children = [child.name for child in content_slot.children]
    forbidden_objects = [
        obj.name
        for obj in bpy.context.scene.objects
        if any(fragment in obj.name.casefold() for fragment in FORBIDDEN_NAME_FRAGMENTS)
    ]
    forbidden_materials = [
        material.name
        for material in bpy.data.materials
        if any(fragment in material.name.casefold() for fragment in FORBIDDEN_NAME_FRAGMENTS)
    ]

    digest_after_metadata = geometry_digest(subjects)
    checks = {
        "sourceBlendHashMatches": sha256(SOURCE_BLEND) == EXPECTED_SOURCE_BLEND_SHA256,
        "sourceValidationPassed": structural["status"] == "pass",
        "boundsUnchanged": structural["dimensionsMm"]["measured"] == {
            "width": 228.0,
            "height": 304.0,
            "depth": 59.0,
        },
        "portraitRatioUnchanged": structural["portrait"]["widthHeightRatio"] == 0.75,
        "labelCenterYUnchanged": structural["labelPosition"]["candidateCenterYmm"] == 99.0,
        "concentricCentersUnchanged": structural["cornerCenterFamilies"]["maximumDriftMm"] == 0.0,
        "singleClosedTube": (
            structural["closedTube"]["meshObjectCount"] == 1
            and structural["closedTube"]["topology"]["connectedMaterialBodyCount"] == 1
            and structural["closedTube"]["pathClosed"] is True
        ),
        "tubeManifold": (
            structural["closedTube"]["topology"]["openBoundaryEdgeCount"] == 0
            and structural["closedTube"]["topology"]["nonManifoldEdgeCount"] == 0
        ),
        "channelFloodFillComplete": (
            structural["closedTube"]["channelFloodFill"]["visitedSamples"] == 384
            and structural["closedTube"]["channelFloodFill"]["sampleCount"] == 384
        ),
        "allSubjectSurfacesManifold": (
            structural["subjectTopology"]["allOpenBoundaryEdgeCount"] == 0
            and structural["subjectTopology"]["allNonManifoldEdgeCount"] == 0
        ),
        "hierarchyUnchanged": actual_hierarchy == EXPECTED_HIERARCHY,
        "contentSlotPreservedEmpty": (
            content_slot.type == "EMPTY"
            and content_slot.parent.name == "RearPolycarbonateShell"
            and not content_slot_children
        ),
        "presentationPivotPreserved": (
            root.parent is None
            and tuple(round(value, 9) for value in root.location) == (0.0, 0.0, 0.0)
            and tuple(round(value, 9) for value in root.rotation_euler) == (0.0, 0.0, 0.0)
            and tuple(round(value, 9) for value in root.scale) == (1.0, 1.0, 1.0)
        ),
        "geometryDigestUnchanged": (
            digest_before == EXPECTED_GEOMETRY_DIGEST
            and digest_after_metadata == EXPECTED_GEOMETRY_DIGEST
        ),
        "noBakedRuntimeAnimation": not animated_subjects,
        "noHaloVfxProxyGeometry": not forbidden_objects and not forbidden_materials,
        "noToyGeometry": not content_slot_children,
        "staleRuntimeMetadataRemoved": set(removed_stale_runtime_properties) == {
            "motion_owner",
            "locked_total_duration_seconds",
        },
        "blenderOwnershipBounded": (
            root["blender_ownership"] == "geometry-pivot-uv-material-zones"
            and root["unity_runtime_owner"] == "GachaRevealDirector"
            and root["runtime_motion_baked"] is False
            and root["runtime_light_baked"] is False
        ),
    }
    if not all(checks.values()):
        raise RuntimeError(json.dumps(checks, indent=2))

    render("Gate05HeroCamera", HERO, (1800, 1400))
    render("Gate05FrontCamera", FRONT, (1200, 1600))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)
    digest_after_save = geometry_digest(subjects)
    checks["geometryDigestAfterSaveUnchanged"] = digest_after_save == EXPECTED_GEOMETRY_DIGEST

    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 3,
        "sourceBlockoutRevision": 2,
        "sourceGate04EvidenceRevision": 7,
        "status": "pass" if all(checks.values()) else "fail",
        "compatibilityConclusion": "geometry-unchanged-metadata-rebound-to-unity-runtime",
        "source": {
            "blend": str(SOURCE_BLEND.relative_to(ROOT.parents[7])),
            "sha256": sha256(SOURCE_BLEND),
            "geometryDigest": digest_before,
        },
        "output": {
            "blend": str(OUTPUT_BLEND.relative_to(ROOT.parents[7])),
            "sha256": sha256(OUTPUT_BLEND),
            "geometryDigest": digest_after_save,
        },
        "dimensionsMm": structural["dimensionsMm"]["measured"],
        "portraitWidthHeightRatio": structural["portrait"]["widthHeightRatio"],
        "labelCenterYmm": structural["labelPosition"]["candidateCenterYmm"],
        "maximumCornerCenterDriftMm": structural["cornerCenterFamilies"]["maximumDriftMm"],
        "closedTube": {
            "object": structural["closedTube"]["object"],
            "connectedMaterialBodyCount": structural["closedTube"]["topology"]["connectedMaterialBodyCount"],
            "openBoundaryEdgeCount": structural["closedTube"]["topology"]["openBoundaryEdgeCount"],
            "nonManifoldEdgeCount": structural["closedTube"]["topology"]["nonManifoldEdgeCount"],
            "channelSamplesVisited": structural["closedTube"]["channelFloodFill"]["visitedSamples"],
            "channelSampleCount": structural["closedTube"]["channelFloodFill"]["sampleCount"],
        },
        "subjectTopology": {
            "openBoundaryEdgeCount": structural["subjectTopology"]["allOpenBoundaryEdgeCount"],
            "nonManifoldEdgeCount": structural["subjectTopology"]["allNonManifoldEdgeCount"],
        },
        "hierarchy": actual_hierarchy,
        "pivot": {
            "object": "PresentationRoot",
            "locationMm": list(root.location),
            "rotationEulerRadians": list(root.rotation_euler),
            "scale": list(root.scale),
        },
        "contentSlot": {
            "objectType": content_slot.type,
            "parent": content_slot.parent.name,
            "childCount": len(content_slot_children),
            "callerOwned": True,
        },
        "ownership": {
            "Blender": ["geometry", "pivot", "UV", "material zones"],
            "Unity": [
                "runtime timing",
                "easing",
                "entry Z travel",
                "local-Y rotation",
                "mesh-clipped light",
            ],
        },
        "bakedRuntimeAnimation": False,
        "forbiddenGeometry": {
            "halo": False,
            "vfx": False,
            "particle": False,
            "proxy": False,
            "explode": False,
            "toy": False,
        },
        "removedStaleRuntimeProperties": removed_stale_runtime_properties,
        "checks": checks,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "gate06Status": "blocked",
    }
    OUTPUT_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, indent=2))
    print(json.dumps({
        "status": report["status"],
        "geometryDigest": digest_after_save,
        "outputBlend": str(OUTPUT_BLEND),
        "hero": str(HERO),
        "front": str(FRONT),
    }, indent=2))


if __name__ == "__main__":
    main()
