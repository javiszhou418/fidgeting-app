#!/usr/bin/env python3
"""Audit Gate 05 rev 2 supplementary material-diagnostic Blender evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
REV2 = ROOT.parent
BLEND = ROOT / "premium-display-case-gate05-r2-material-diagnostic.blend"
BUILD_REPORT = ROOT / "material-diagnostic-build-report.json"
AUDIT_REPORT = ROOT / "material-diagnostic-blender-audit.json"
VALIDATOR_PATH = REV2 / "validate_blockout.py"
NOTICE = "DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 APPROVAL"
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_MATERIALS = {
    "MAT_FrostedPolycarbonate": {
        "Base Color": (0.61, 0.65, 0.68, 0.10),
        "Metallic": 0.0,
        "Roughness": 0.22,
        "Transmission Weight": 0.92,
        "IOR": 1.585,
        "Alpha": 0.10,
    },
    "MAT_FrostedPolycarbonateEdge": {
        "Base Color": (0.72, 0.75, 0.77, 0.21),
        "Metallic": 0.0,
        "Roughness": 0.18,
        "Transmission Weight": 0.78,
        "IOR": 1.585,
        "Alpha": 0.21,
    },
    "MAT_BlackFlocking": {
        "Base Color": (0.009, 0.011, 0.014, 1.0),
        "Metallic": 0.0,
        "Roughness": 0.91,
        "Transmission Weight": 0.0,
    },
    "MAT_RarityFoilSilver": {
        "Base Color": (0.58, 0.62, 0.66, 1.0),
        "Metallic": 0.96,
        "Roughness": 0.30,
        "Transmission Weight": 0.0,
    },
    "MAT_LabelPaper": {
        "Base Color": (0.74, 0.72, 0.68, 1.0),
        "Metallic": 0.0,
        "Roughness": 0.73,
        "Transmission Weight": 0.0,
    },
    "MAT_LabelGraphite": {
        "Base Color": (0.055, 0.060, 0.066, 1.0),
        "Metallic": 0.22,
        "Roughness": 0.52,
        "Transmission Weight": 0.0,
    },
}
EXPECTED_ASSIGNMENTS = {
    "RearPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "FrontPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "ContinuousTubePerimeter": "MAT_FrostedPolycarbonateEdge",
    "TactileBackgroundInsert": "MAT_BlackFlocking",
    "PhysicalLabel": "MAT_LabelPaper",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "premium_display_case_gate05_rev2_audit_validator",
        VALIDATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {VALIDATOR_PATH}")
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


def socket_value(material: bpy.types.Material, name: str):
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is None:
        return None
    socket = next((item for item in shader.inputs if item.name == name), None)
    if socket is None:
        return None
    value = socket.default_value
    if hasattr(value, "__len__"):
        return tuple(float(component) for component in value)
    return float(value)


def near(actual, expected, tolerance: float = 1e-5) -> bool:
    if isinstance(expected, tuple):
        return actual is not None and len(actual) == len(expected) and all(
            abs(value - target) <= tolerance
            for value, target in zip(actual, expected)
        )
    return actual is not None and abs(actual - expected) <= tolerance


def object_world_z(obj: bpy.types.Object) -> tuple[float, float]:
    if obj.type == "FONT":
        points = [obj.matrix_world @ point.co for spline in obj.data.splines for point in spline.bezier_points]
    else:
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return min(point.z for point in points), max(point.z for point in points)


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    validator = load_validator()
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    digest = geometry_digest(subjects)
    structural = validator.validate_scene()

    actual_assignments = {
        name: bpy.data.objects[name].material_slots[0].material.name
        for name in EXPECTED_ASSIGNMENTS
    }
    material_values = {
        name: {
            socket: socket_value(bpy.data.materials[name], socket)
            for socket in (*values.keys(), "Emission Strength")
        }
        for name, values in EXPECTED_MATERIALS.items()
    }
    material_value_pass = all(
        near(material_values[name][socket], expected)
        for name, values in EXPECTED_MATERIALS.items()
        for socket, expected in values.items()
    )
    no_emission = all(
        near(material_values[name]["Emission Strength"], 0.0)
        for name in EXPECTED_MATERIALS
    )
    material_image_nodes = {
        name: [
            node.name for node in bpy.data.materials[name].node_tree.nodes
            if node.bl_idname == "ShaderNodeTexImage"
        ]
        for name in EXPECTED_MATERIALS
    }

    proxy_objects = [
        obj for obj in scene.objects
        if bool(obj.get("supplementary_material_diagnostic", False))
    ]
    proxy_meshes = [obj for obj in proxy_objects if obj.type == "MESH"]
    cover_proxy = bpy.data.objects["DIAGNOSTIC_TransparentCoverProxy"]
    foil_proxy = bpy.data.objects["DIAGNOSTIC_NarrowFoilProxy"]
    print_proxy = bpy.data.objects["DIAGNOSTIC_NeutralPrintBarPrimary"]
    label = bpy.data.objects["PhysicalLabel"]
    cover_z = object_world_z(cover_proxy)
    foil_z = object_world_z(foil_proxy)
    print_z = object_world_z(print_proxy)
    label_z = object_world_z(label)
    transparent_ordering = {
        "labelZmm": label_z,
        "foilZmm": foil_z,
        "printZmm": print_z,
        "coverZmm": cover_z,
        "pass": (
            cover_z[0] > print_z[1]
            and cover_z[0] > foil_z[1]
            and print_z[0] > label_z[1]
        ),
    }

    light_objects = [
        obj for obj in scene.objects
        if obj.type == "LIGHT" and obj.name.startswith("DIAGNOSTIC_")
    ]
    lights = {
        obj["studio_role"]: {
            "name": obj.name,
            "energy": obj.data.energy,
            "color": list(obj.data.color),
            "chroma": max(obj.data.color) - min(obj.data.color),
            "rarityLight": bool(obj["rarity_light"]),
        }
        for obj in light_objects
    }
    world_nodes = list(scene.world.node_tree.nodes)
    world_image_nodes = [
        node.name for node in world_nodes if node.bl_idname == "ShaderNodeTexImage"
    ]
    world_emission_nodes = [
        node.name for node in world_nodes if node.bl_idname == "ShaderNodeEmission"
    ]
    text_content = "\n".join(
        obj.data.body for obj in proxy_objects if obj.type == "FONT"
    ).lower()
    forbidden_tokens = ("whatnot", "barcode", "smiley", "sample number", "yellow label")
    forbidden_hits = [token for token in forbidden_tokens if token in text_content]
    raw_paths = {
        name: ROOT / "raw" / f"{name}.png"
        for name in (
            "hero",
            "left-oblique",
            "right-oblique",
            "low",
            "side",
            "label-closeup",
            "concentric-closeup",
            "clay-hero-same-camera",
        )
    }
    source_files_unchanged = all(
        item["sha256Before"] == item["sha256After"]
        for item in build["sourceFiles"].values()
    )
    checks = {
        "buildReportPassed": build["status"] == "pass",
        "diagnosticNoticeExact": scene["diagnostic_notice"] == NOTICE,
        "geometryDigestUnchanged": (
            digest
            == build["geometryPreservation"]["digestBefore"]
            == build["geometryPreservation"]["digestAfterMaterialAssignment"]
            == build["geometryPreservation"]["digestAfterRenders"]
        ),
        "boundsUnchanged": (
            structural["dimensionsMm"]["measured"]
            == {"width": 228.0, "height": 304.0, "depth": 59.0}
        ),
        "labelCenterYUnchanged": (
            structural["labelPosition"]["candidateCenterYmm"] == 99.0
        ),
        "concentricErrorUnchanged": (
            structural["cornerCenterFamilies"]["maximumDriftMm"] == 0.0
        ),
        "allSubjectSurfacesManifold": structural["subjectTopology"]["pass"],
        "tubeManifold": structural["closedTube"]["topology"]["manifoldPreflightPass"],
        "tubeFloodFill": (
            structural["closedTube"]["channelFloodFill"]["pass"]
            and structural["closedTube"]["channelFloodFill"]["visitedSamples"] == 384
        ),
        "formalMaterialAssignmentsExact": actual_assignments == EXPECTED_ASSIGNMENTS,
        "formalPbrValuesExact": material_value_pass,
        "formalMaterialsNoEmission": no_emission,
        "formalMaterialsContainNoImageTextures": all(
            not nodes for nodes in material_image_nodes.values()
        ),
        "transparentLayerOrdering": transparent_ordering["pass"],
        "transparentCoverSourceNodeStillEmpty": (
            bpy.data.objects["TransparentCover"].type == "EMPTY"
            and bpy.data.objects["TransparentCover"]["gate05_geometry_status"]
            == "contour-only-thickness-deferred"
        ),
        "proxySurfacesExcludedFromGate05Digest": all(
            not bool(obj["gate05_subject_geometry"])
            and not bool(obj["gate07_approval_eligible"])
            for obj in proxy_objects
        ),
        "zeroThicknessCoverAndFoil": (
            cover_proxy["proxy_thickness_mm"] == 0.0
            and foil_proxy["proxy_thickness_mm"] == 0.0
        ),
        "neutralKeyFillRimOnly": (
            set(lights) == {"key", "fill", "rim"}
            and all(not light["rarityLight"] for light in lights.values())
            and all(light["chroma"] <= 0.071 for light in lights.values())
        ),
        "keyFillRimRatiosInContract": (
            2.0 <= lights["key"]["energy"] / lights["fill"]["energy"] <= 3.0
            and lights["rim"]["energy"] / lights["key"]["energy"] <= 0.35
        ),
        "continuousMatteWorldNoLocalMasks": (
            scene.world["local_noise_masks"] == 0
            and scene.world["image_texture_count"] == 0
            and any(
                node.bl_idname == "ShaderNodeTexNoise" for node in world_nodes
            )
            and not world_image_nodes
            and not world_emission_nodes
        ),
        "noForbiddenReferenceIdentity": not forbidden_hits,
        "neutralIdentityPlaceholdersOnly": all(
            not bool(obj["formal_logo_redrawn"])
            and not bool(obj["formal_achievement_redrawn"])
            for obj in proxy_objects
        ),
        "sourceFilesUnchanged": source_files_unchanged,
        "rawViewsPresent": all(
            path.exists() and path.stat().st_size > 50_000 for path in raw_paths.values()
        ),
        "gate05StatusPreserved": scene["gate05_status"] == "ready_for_review",
        "gate06And07RemainBlocked": (
            not scene["gate06_entered"]
            and not scene["gate07_entered"]
            and scene["gate07_approval_effect"] == "none"
        ),
        "shippingUnityUnchanged": not scene["shipping_unity_changed"],
        "noBuildInstallPhonePush": not scene["build_install_phone_push"],
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 2,
        "evidenceClass": "supplementary-material-diagnostic",
        "status": "pass" if all(checks.values()) else "fail",
        "notice": NOTICE,
        "approvalEffect": "none-not-gate07-material-approval",
        "geometryDigest": digest,
        "boundsMm": structural["dimensionsMm"]["measured"],
        "labelCenterYmm": structural["labelPosition"]["candidateCenterYmm"],
        "maximumCornerCenterDriftMm": structural[
            "cornerCenterFamilies"
        ]["maximumDriftMm"],
        "openBoundaryEdgeCount": structural[
            "subjectTopology"
        ]["allOpenBoundaryEdgeCount"],
        "nonManifoldEdgeCount": structural[
            "subjectTopology"
        ]["allNonManifoldEdgeCount"],
        "floodFill": structural["closedTube"]["channelFloodFill"],
        "materialAssignments": actual_assignments,
        "materialValues": material_values,
        "materialImageTextureNodes": material_image_nodes,
        "transparentOrdering": transparent_ordering,
        "proxyObjects": [
            {
                "name": obj.name,
                "type": obj.type,
                "kind": obj["proxy_kind"],
                "gate05SubjectGeometry": obj["gate05_subject_geometry"],
                "gate07ApprovalEligible": obj["gate07_approval_eligible"],
            }
            for obj in proxy_objects
        ],
        "proxyMeshCount": len(proxy_meshes),
        "lights": lights,
        "world": {
            "backgroundContract": scene.world["background_contract"],
            "nodeTypes": sorted(node.bl_idname for node in world_nodes),
            "imageTextureNodes": world_image_nodes,
            "emissionNodes": world_emission_nodes,
        },
        "forbiddenIdentityHits": forbidden_hits,
        "sourceFiles": build["sourceFiles"],
        "rawViews": {
            name: {
                "path": str(path),
                "sha256": sha256(path),
                "sizeBytes": path.stat().st_size,
            }
            for name, path in raw_paths.items()
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "sourceBlend": str(BLEND),
        "sourceBlendSha256": sha256(BLEND),
    }
    AUDIT_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "geometryDigest": digest,
        "boundsMm": report["boundsMm"],
        "labelCenterYmm": report["labelCenterYmm"],
        "maximumCornerCenterDriftMm": report["maximumCornerCenterDriftMm"],
        "openBoundaryEdgeCount": report["openBoundaryEdgeCount"],
        "nonManifoldEdgeCount": report["nonManifoldEdgeCount"],
        "floodFill": (
            f"{report['floodFill']['visitedSamples']}/"
            f"{report['floodFill']['sampleCount']}"
        ),
        "auditReport": str(AUDIT_REPORT),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
