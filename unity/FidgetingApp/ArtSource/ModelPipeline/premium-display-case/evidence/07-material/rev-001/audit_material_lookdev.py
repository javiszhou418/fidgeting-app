#!/usr/bin/env python3
"""Audit Premium Display Case Gate 07 material lookdev in Blender."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parent.parent
GATE06 = EVIDENCE / "06-geometry/rev-002"
BLEND = ROOT / "premium-display-case-material-r001.blend"
BUILD_REPORT = ROOT / "material-build-report.json"
AUDIT_REPORT = ROOT / "blender-audit.json"
SURFACE_REPORT = ROOT / "surface-coverage-report.json"
OPTIMIZATION_REPORT = ROOT / "asset-optimization-report.json"
QA_REPORT = ROOT / "qa-verdict.json"
GATE06_VALIDATOR = GATE06 / "validate_geometry.py"
SOURCE_BLEND = GATE06 / "premium-display-case-geometry-r002.blend"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_ASSIGNMENTS = {
    "RearPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "FrontPolycarbonateShell": "MAT_FrostedPolycarbonate",
    "ContinuousTubePerimeter": "MAT_FrostedPolycarbonateEdge",
    "TactileBackgroundInsert": "MAT_BlackFlocking",
    "PhysicalLabel": "MAT_LabelPaper",
}
EXPECTED_VALUES = {
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
        "Metallic": 0.0,
        "Roughness": 0.52,
        "Transmission Weight": 0.0,
    },
}
EXPECTED_IDENTITY = {
    "fullGeometryDigest": (
        "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    ),
    "objectMatrixDigest": (
        "34d52e8980dbbffc5573523b80de9a47d145a49bb22ae95f8d7c1b38e393d588"
    ),
    "vertexPositionDigest": (
        "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
    ),
    "silhouetteDigest": (
        "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4"
    ),
    "topologyWindingDigest": (
        "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
    ),
}


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("premium_display_case_gate07_audit_validator", GATE06_VALIDATOR)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
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


def object_local_grain(material: bpy.types.Material) -> dict[str, object]:
    nodes = material.node_tree.nodes
    noise_nodes = [
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeTexNoise" and node.name.startswith("M07_")
    ]
    mapping_nodes = [
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeMapping" and node.name.startswith("M07_")
    ]
    texture_coordinate_nodes = [
        node
        for node in nodes
        if node.bl_idname == "ShaderNodeTexCoord" and node.name.startswith("M07_")
    ]
    mapping_sources = []
    for mapping in mapping_nodes:
        vector = mapping.inputs.get("Vector")
        mapping_sources.extend(
            {
                "node": link.from_node.name,
                "socket": link.from_socket.name,
            }
            for link in vector.links
        )
    world_space_nodes = [
        node.name
        for node in nodes
        if node.bl_idname in {
            "ShaderNodeTexEnvironment",
            "ShaderNodeTexImage",
        }
    ]
    return {
        "noiseNodes": [node.name for node in noise_nodes],
        "mappingNodes": [node.name for node in mapping_nodes],
        "textureCoordinateNodes": [
            node.name for node in texture_coordinate_nodes
        ],
        "mappingSources": mapping_sources,
        "worldSpaceOrImageNodes": world_space_nodes,
        "declaredCoordinateSpace": material.get("micrograin_coordinate_space"),
        "featureSizeMm": material.get("micrograin_feature_size_mm"),
        "bumpDistanceMm": material.get("micrograin_bump_distance_mm"),
        "pass": (
            bool(noise_nodes)
            and bool(mapping_nodes)
            and bool(texture_coordinate_nodes)
            and all(source["socket"] == "Object" for source in mapping_sources)
            and not world_space_nodes
            and material.get("micrograin_coordinate_space") == "object-local"
        ),
    }


def object_world_z(obj: bpy.types.Object) -> tuple[float, float]:
    if obj.type == "FONT":
        points = [
            obj.matrix_world @ point.co
            for spline in obj.data.splines
            for point in spline.bezier_points
        ]
    else:
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return min(point.z for point in points), max(point.z for point in points)


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    identity = VALIDATOR.identity_snapshot(subjects)
    bounds = VALIDATOR.world_bounds(subjects)
    integrity = {
        obj.name: VALIDATOR.mesh_integrity(obj) for obj in subjects
    }
    gate05_validator = VALIDATOR.load_gate05_validator()
    tube_orientation = VALIDATOR.hollow_tube_orientation(
        bpy.data.objects["ContinuousTubePerimeter"],
        gate05_validator,
    )
    assignments = {
        name: bpy.data.objects[name].material_slots[0].material.name
        for name in EXPECTED_ASSIGNMENTS
    }
    material_values = {
        material_name: {
            socket_name: socket_value(
                bpy.data.materials[material_name],
                socket_name,
            )
            for socket_name in (*expected.keys(), "Emission Strength")
        }
        for material_name, expected in EXPECTED_VALUES.items()
    }
    pbr_values_pass = all(
        near(material_values[material_name][socket_name], expected)
        for material_name, expected_values in EXPECTED_VALUES.items()
        for socket_name, expected in expected_values.items()
    )
    no_emission = all(
        near(material_values[material_name]["Emission Strength"], 0.0)
        for material_name in EXPECTED_VALUES
    )
    material_names = [
        *EXPECTED_VALUES.keys(),
        "MAT_M07_ContinuousNeutralFriction",
    ]
    grain = {
        name: object_local_grain(bpy.data.materials[name])
        for name in material_names
    }
    image_texture_nodes = {
        name: [
            node.name
            for node in bpy.data.materials[name].node_tree.nodes
            if node.bl_idname == "ShaderNodeTexImage"
        ]
        for name in material_names
    }
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    cover = bpy.data.objects["M07_TransparentCoverProxy"]
    foil = bpy.data.objects["M07_NarrowFoilProxy"]
    print_bar = bpy.data.objects["M07_NeutralPrintBarPrimary"]
    label = bpy.data.objects["PhysicalLabel"]
    ordering = {
        "labelZmm": object_world_z(label),
        "foilZmm": object_world_z(foil),
        "printZmm": object_world_z(print_bar),
        "coverZmm": object_world_z(cover),
    }
    ordering["pass"] = (
        ordering["coverZmm"][0] > ordering["printZmm"][1]
        and ordering["coverZmm"][0] > ordering["foilZmm"][1]
        and ordering["printZmm"][0] > ordering["labelZmm"][1]
    )
    lights = [
        obj
        for obj in scene.objects
        if obj.type == "LIGHT" and bool(obj.get("neutral_gate07_light", False))
    ]
    light_roles = {obj["studio_role"]: obj for obj in lights}
    exploded = [obj for obj in scene.objects if obj.name.startswith("EXPLODED_")]
    raw_paths = [
        ROOT / "raw" / filename
        for filename in (
            "hero.png",
            "left-oblique.png",
            "right-oblique.png",
            "side.png",
            "back.png",
            "tube-corner.png",
            "label-closeup.png",
            "tactile-closeup.png",
            "rotation-000.png",
            "rotation-090.png",
            "rotation-180.png",
            "rotation-270.png",
            "rotation-360.png",
            "clay-hero-same-camera.png",
        )
    ]
    checks = {
        "buildReportPassed": build["status"] == "pass",
        "sourceGate06BlendUnchanged": (
            build["sourceGate06"]["sha256Before"]
            == build["sourceGate06"]["sha256After"]
            == sha256(SOURCE_BLEND)
        ),
        "geometryIdentityExact": all(
            identity[key] == expected
            for key, expected in EXPECTED_IDENTITY.items()
        ),
        "geometryIdentityMatchesBuild": (
            identity
            == build["geometryPreservation"]["identityBefore"]
            == build["geometryPreservation"]["identityAfterMaterialAssignment"]
            == build["geometryPreservation"]["identityAfterRenders"]
        ),
        "boundsExact": bounds["sizeMm"]
        == {"width": 228.0, "height": 304.0, "depth": 59.0},
        "labelCenterYExact": float(label.get("center_y_mm", 99.0)) == 99.0,
        "concentricDriftExact": (
            build["geometryPreservation"]["maximumCornerCenterDriftMm"] == 0.0
        ),
        "closedAndManifold": all(
            item["openBoundaryEdgeCount"] == 0
            and item["nonManifoldEdgeCount"] == 0
            and item["pass"]
            for item in integrity.values()
        ),
        "tubeWindingExact": (
            tube_orientation["netMaterialSignedVolumeMm3"] == 52932.982745
            and tube_orientation["outerBoundary"]["outward"]
            and tube_orientation["innerBoundary"]["inwardTowardLumen"]
            and tube_orientation["pass"]
        ),
        "floodFillExact": (
            build["geometryPreservation"]["floodFill"]["visitedSamples"] == 384
            and build["geometryPreservation"]["floodFill"]["sampleCount"] == 384
            and build["geometryPreservation"]["floodFill"]["pass"]
        ),
        "materialAssignmentsExact": assignments == EXPECTED_ASSIGNMENTS,
        "pbrValuesExact": pbr_values_pass,
        "materialsNoEmission": no_emission,
        "allMicrograinObjectLocal": all(item["pass"] for item in grain.values()),
        "grainStabilityFiveAngles": build["grainStability"]["pass"],
        "noImageTextures": all(not nodes for nodes in image_texture_nodes.values()),
        "transparentOrdering": ordering["pass"],
        "neutralThreeLightRig": set(light_roles) == {"key", "fill", "rim"},
        "finalLightingNotApproved": all(
            not bool(obj["final_lighting_approval"]) for obj in lights
        ),
        "wholeCaseOnlyNoExplode": (
            bool(scene["whole_case_only"])
            and bool(scene["no_explode"])
            and bool(exploded)
            and all(obj.hide_render for obj in exploded)
            and all(not bool(obj["explode_eligible"]) for obj in proxies)
        ),
        "neutralIdentityPlaceholdersOnly": all(
            not bool(obj["formal_logo_redrawn"])
            and not bool(obj["formal_achievement_redrawn"])
            and not bool(obj["copied_reference_branding"])
            for obj in proxies
        ),
        "allRawEvidencePresent": all(
            path.exists() and path.stat().st_size > 50_000 for path in raw_paths
        ),
        "gate07ReadyNotApproved": (
            scene["gate07_status"] == "ready_for_review"
            and not bool(scene["gate07_approved"])
        ),
        "gate08NotEntered": not bool(scene["gate08_entered"]),
        "shippingUnityUnchanged": not bool(scene["shipping_unity_changed"]),
        "noBuildInstallPhonePush": not bool(scene["build_install_phone_push"]),
    }

    audit = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceBlend": str(SOURCE_BLEND.relative_to(REPO_ROOT)),
        "sourceBlendSha256": sha256(SOURCE_BLEND),
        "lookdevBlend": str(BLEND.relative_to(REPO_ROOT)),
        "lookdevBlendSha256": sha256(BLEND),
        "geometryIdentity": identity,
        "boundsMm": bounds,
        "meshIntegrity": integrity,
        "tubeOrientation": tube_orientation,
        "labelCenterYmm": float(label.get("center_y_mm", 99.0)),
        "maximumCornerCenterDriftMm": build["geometryPreservation"][
            "maximumCornerCenterDriftMm"
        ],
        "floodFill": build["geometryPreservation"]["floodFill"],
        "materialAssignments": assignments,
        "materialValues": material_values,
        "micrograin": grain,
        "imageTextureNodes": image_texture_nodes,
        "transparentOrdering": ordering,
        "lights": {
            role: {
                "name": obj.name,
                "energy": obj.data.energy,
                "color": list(obj.data.color),
                "finalLightingApproval": bool(obj["final_lighting_approval"]),
            }
            for role, obj in light_roles.items()
        },
        "proxies": [
            {
                "name": obj.name,
                "type": obj.type,
                "kind": obj["proxy_kind"],
                "thicknessMm": obj.get("proxy_thickness_mm"),
                "geometryContractRole": obj["geometry_contract_role"],
                "wholeCaseOnly": bool(obj["whole_case_only"]),
                "explodeEligible": bool(obj["explode_eligible"]),
            }
            for obj in proxies
        ],
        "checks": checks,
        "blender": bpy.app.version_string,
    }
    AUDIT_REPORT.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    surface_checks = {
        name: {
            "closedSurface": integrity[name]["openBoundaryEdgeCount"] == 0,
            "frontCap": "assigned-formal-principled-material",
            "backCap": "assigned-formal-principled-material",
            "sidewall": "assigned-formal-principled-material",
            "materialSlots": len(bpy.data.objects[name].material_slots),
            "polygonMaterialIndices": sorted(
                {polygon.material_index for polygon in bpy.data.objects[name].data.polygons}
            ),
            "coordinatePolicy": (
                bpy.data.objects[name].material_slots[0].material.get(
                    "micrograin_coordinate_space"
                )
                or "uniform-principled"
            ),
        }
        for name in SUBJECT_NAMES
    }
    surface_pass = all(
        item["closedSurface"]
        and item["materialSlots"] == 1
        and item["polygonMaterialIndices"] == [0]
        for item in surface_checks.values()
    )
    surface_report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "status": "pass" if surface_pass else "fail",
        "surfaceTaxonomy": surface_checks,
        "labelCoverZone": {
            "type": cover.type,
            "thicknessMm": cover.get("proxy_thickness_mm"),
            "policy": "existing transparent material zone; no Gate 06 subject geometry change",
        },
        "narrowFoilZone": {
            "type": foil.type,
            "thicknessMm": foil.get("proxy_thickness_mm"),
            "policy": "existing narrow foil material zone; no Gate 06 subject geometry change",
        },
        "overlayContextExcluded": True,
        "imageTextureCoverageRequired": False,
        "turntableViews": [0, 90, 180, 270, 360],
        "pass": surface_pass,
    }
    SURFACE_REPORT.write_text(
        json.dumps(surface_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    triangle_count = sum(item["triangles"] for item in integrity.values())
    subject_material_slots = sum(
        len(bpy.data.objects[name].material_slots) for name in SUBJECT_NAMES
    )
    scales_applied = all(
        all(abs(component - 1.0) <= 1e-9 for component in obj.scale)
        for obj in subjects
    )
    optimization_checks = {
        "triangleBudget": triangle_count <= 120_000,
        "materialSlotBudget": subject_material_slots <= 8,
        "closedAndManifold": checks["closedAndManifold"],
        "appliedSubjectScales": scales_applied,
        "noUnusedSubjectSlots": all(
            len(bpy.data.objects[name].material_slots) == 1
            for name in SUBJECT_NAMES
        ),
        "proceduralCoverageNoUvPackingRequired": checks["noImageTextures"],
        "approvedGeometryNotOptimizedOrDecimated": (
            identity["fullGeometryDigest"] == EXPECTED_IDENTITY["fullGeometryDigest"]
        ),
    }
    optimization_report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "status": "pass" if all(optimization_checks.values()) else "fail",
        "subjectTriangles": triangle_count,
        "triangleBudget": 120_000,
        "subjectMaterialSlots": subject_material_slots,
        "materialSlotBudget": 8,
        "subjectObjects": len(subjects),
        "renderOnlyMaterialZoneProxies": len(proxies),
        "lodGenerated": False,
        "lodReason": "Gate 07 preserves the approved source; export and LOD decisions remain downstream.",
        "checks": optimization_checks,
    }
    OPTIMIZATION_REPORT.write_text(
        json.dumps(optimization_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    qa_pass = (
        audit["status"] == "pass"
        and surface_report["status"] == "pass"
        and optimization_report["status"] == "pass"
    )
    qa_report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "result": (
            "READY_FOR_MATERIAL_REVIEW_NOT_SHIPPING"
            if qa_pass
            else "NO_SHIP"
        ),
        "status": "pass" if qa_pass else "fail",
        "blockers": [] if qa_pass else ["One or more Gate 07 audits failed."],
        "majors": [],
        "minors": [],
        "expectedPending": [
            "User material approval",
            "Gate 08 final lighting review",
            "Gate 12 shipping-source visual approval",
            "iPhone acceptance after permitted installation",
        ],
        "wholeCaseOnly": True,
        "explode": False,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "evidence": {
            "blenderAudit": str(AUDIT_REPORT.relative_to(REPO_ROOT)),
            "surfaceCoverage": str(SURFACE_REPORT.relative_to(REPO_ROOT)),
            "assetOptimization": str(OPTIMIZATION_REPORT.relative_to(REPO_ROOT)),
        },
    }
    QA_REPORT.write_text(
        json.dumps(qa_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": audit["status"],
                "qa": qa_report["result"],
                "fullGeometryDigest": identity["fullGeometryDigest"],
                "vertexPositionDigest": identity["vertexPositionDigest"],
                "topologyWindingDigest": identity["topologyWindingDigest"],
                "boundsMm": bounds["sizeMm"],
                "labelCenterYmm": audit["labelCenterYmm"],
                "floodFill": (
                    f"{audit['floodFill']['visitedSamples']}/"
                    f"{audit['floodFill']['sampleCount']}"
                ),
                "subjectTriangles": triangle_count,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not qa_pass:
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
