#!/usr/bin/env python3
"""Audit Premium Display Case Gate 08 Blender evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT.parent.parent
BLEND = ROOT / "premium-display-case-lighting-r001.blend"
BUILD_REPORT = ROOT / "lighting-build-report.json"
IMAGE_REPORT = ROOT / "lighting-image-validation.json"
GATE06_VALIDATOR = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
BUILDER = ROOT / "build_lighting_lookdev.py"
AUDIT_REPORT = ROOT / "blender-lighting-audit.json"
QA_REPORT = ROOT / "qa-verdict.json"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
EXPECTED_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)


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


VALIDATOR = load_module("premium_display_case_gate08_audit_validator", GATE06_VALIDATOR)
BUILD = load_module("premium_display_case_gate08_build_helpers", BUILDER)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def world_z(obj: bpy.types.Object) -> tuple[float, float]:
    if obj.type in {"FONT", "CURVE"}:
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
        evaluated.to_mesh_clear()
    else:
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    return min(point.z for point in points), max(point.z for point in points)


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    images = json.loads(IMAGE_REPORT.read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    proxies = [
        obj
        for obj in scene.objects
        if bool(obj.get("gate07_material_zone_proxy", False))
    ]
    studio = [
        obj
        for name in ("M07_StudioCyclorama", "M07_BackViewWall", "M07_SideViewWall")
        if (obj := bpy.data.objects.get(name)) is not None
    ]
    identity = VALIDATOR.identity_snapshot(subjects)
    material_digest, material_payload = BUILD.approved_material_digest(
        build["materials"]["approvedMaterialNames"],
        subjects + proxies + studio,
    )
    lights = {
        obj["studio_role"]: {
            "name": obj.name,
            "type": obj.data.type,
            "shape": obj.data.shape,
            "energy": float(obj.data.energy),
            "ratioToKey": float(obj.data.energy) / BUILD.KEY_ENERGY,
            "sizeMm": float(obj.data.size),
            "sizeYmm": float(obj.data.size_y),
            "linearRgb": [float(value) for value in obj.data.color],
            "colorTemperatureKelvin": int(obj["color_temperature_kelvin"]),
            "locationMm": [float(value) for value in obj.location],
            "targetMm": list(obj["target_mm"]),
            "rarityLight": bool(obj["rarity_light"]),
        }
        for obj in scene.objects
        if obj.type == "LIGHT" and bool(obj.get("gate08_controlled_light", False))
    }
    cameras = {
        obj["camera_id"]: {
            "name": obj.name,
            "locationMm": [float(value) for value in obj.location],
            "targetMm": list(obj["target_mm"]),
            "lensMm": float(obj.data.lens),
            "sensorWidthMm": float(obj.data.sensor_width),
            "sensorHeightMm": float(obj.data.sensor_height),
            "sensorFit": obj.data.sensor_fit,
            "depthOfField": bool(obj.data.dof.use_dof),
            "assemblyState": obj["whole_case_assembly_state"],
        }
        for obj in scene.objects
        if obj.type == "CAMERA" and bool(obj.get("gate08_authored_camera", False))
    }
    ordering = {
        "labelZmm": world_z(bpy.data.objects["PhysicalLabel"]),
        "foilZmm": world_z(bpy.data.objects["M07_NarrowFoilProxy"]),
        "printZmm": world_z(bpy.data.objects["M07_NeutralPrintBarPrimary"]),
        "coverZmm": world_z(bpy.data.objects["M07_TransparentCoverProxy"]),
    }
    ordering["pass"] = (
        ordering["coverZmm"][0] > ordering["printZmm"][1]
        and ordering["coverZmm"][0] > ordering["foilZmm"][1]
        and ordering["printZmm"][0] > ordering["labelZmm"][1]
    )
    technical_materials = sorted(
        material.name
        for material in bpy.data.materials
        if bool(material.get("gate08_technical_pass_only", False))
    )
    required_outputs = [
        "raw/hero.png",
        "raw/left-oblique.png",
        "raw/right-oblique.png",
        "raw/low.png",
        "raw/pass-beauty.png",
        "raw/pass-clay.png",
        "raw/pass-normal.png",
        "raw/pass-depth.png",
        "raw/pass-roughness.png",
        "raw/label-closeup.png",
        "raw/tube-corner.png",
        "raw/black-panel.png",
        "lighting-review.png",
        "lighting-details-contact-sheet.png",
        "lighting-passes-contact-sheet.png",
        "lighting-parameters-board.png",
    ]
    checks = {
        "buildPassed": build["status"] == "pass",
        "imageValidationPassed": images["status"] == "pass",
        "geometryDigestExact": (
            identity["fullGeometryDigest"] == EXPECTED_GEOMETRY_DIGEST
            == build["geometry"]["digestBefore"]
            == build["geometry"]["digestAfter"]
        ),
        "materialDigestExact": (
            material_digest
            == build["materials"]["digestBefore"]
            == build["materials"]["digestAfter"]
        ),
        "approvedAssignmentsRestored": (
            material_payload["assignments"]
            == BUILD.approved_material_digest(
                build["materials"]["approvedMaterialNames"],
                subjects + proxies + studio,
            )[1]["assignments"]
            and build["materials"]["assignmentsRestored"]
        ),
        "requiredLights": set(lights) == {"key", "fill", "rim"},
        "requestedRatios": (
            abs(lights["key"]["ratioToKey"] - 1.0) <= 1e-9
            and 0.25 <= lights["fill"]["ratioToKey"] <= 0.35
            and 0.30 <= lights["rim"]["ratioToKey"] <= 0.45
            and abs(lights["fill"]["ratioToKey"] - 0.30) <= 1e-9
            and abs(lights["rim"]["ratioToKey"] - 0.40) <= 1e-9
        ),
        "neutralNoRarityLights": all(
            not item["rarityLight"]
            and item["colorTemperatureKelvin"] in {5000, 5600, 6200}
            and item["linearRgb"][1]
            <= max(item["linearRgb"][0], item["linearRgb"][2]) + 0.025
            for item in lights.values()
        ),
        "requiredCameras": {
            "hero",
            "left-oblique",
            "right-oblique",
            "low",
            "label-closeup",
            "tube-corner",
            "black-panel",
        }.issubset(cameras),
        "portraitCameraContract": (
            cameras["hero"]["lensMm"] == 60.0
            and cameras["hero"]["sensorFit"] == "VERTICAL"
            and not cameras["hero"]["depthOfField"]
            and 27.0
            <= build["cameras"]["hero"]["verticalFovDegrees"]
            <= 31.0
        ),
        "mainViewsUncropped": all(
            item["notCropped"] and item["comfortableMargin"]
            for item in build["framing"].values()
        ),
        "agxExposureRecorded": (
            scene.view_settings.view_transform == "AgX"
            and scene.view_settings.look == "AgX - Medium High Contrast"
            and abs(scene.view_settings.exposure - 0.55) <= 1e-6
            and build["render"]["shutterSeconds"] is None
            and build["render"]["iso"] is None
        ),
        "transparentOrdering": ordering["pass"],
        "grainStableAtFiveAngles": build["grainStability"]["pass"],
        "technicalPassesSeparated": (
            not technical_materials
            and build["technicalPassPolicy"][
                "clayNormalDepthRoughnessUseTemporaryOverrides"
            ]
            and not build["technicalPassPolicy"][
                "temporaryOverridesAreShippingMaterials"
            ]
            and build["technicalPassPolicy"][
                "approvedAssignmentsRestoredBeforeSave"
            ]
        ),
        "requiredOutputsPresent": all(
            (ROOT / relative).exists()
            and (ROOT / relative).stat().st_size > 30_000
            for relative in required_outputs
        ),
        "wholeCaseOnlyNoExplode": (
            bool(scene["whole_case_only"])
            and bool(scene["no_explode"])
            and all(
                obj.hide_render
                for obj in scene.objects
                if obj.name.startswith("EXPLODED_")
            )
            and all(
                camera["assemblyState"] == "assembled"
                for camera in cameras.values()
            )
        ),
        "gate08ReadyNotApproved": (
            scene["gate08_status"] == "ready_for_review"
            and not bool(scene["gate08_approved"])
        ),
        "gate09NotEntered": not bool(scene["gate09_entered"]),
        "shippingUnityUnchanged": not bool(scene["shipping_unity_changed"]),
        "noBuildInstallPhonePush": not bool(scene["build_install_phone_push"]),
    }
    audit = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "blender": bpy.app.version_string,
        "blendPath": str(BLEND.relative_to(REPO_ROOT)),
        "blendSha256": sha256(BLEND),
        "geometryIdentity": identity,
        "materialDigest": material_digest,
        "materialAssignments": material_payload["assignments"],
        "lights": lights,
        "cameras": cameras,
        "transparentOrdering": ordering,
        "technicalPassMaterials": technical_materials,
        "imageChecks": images["checks"],
        "checks": checks,
    }
    AUDIT_REPORT.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    qa_pass = audit["status"] == "pass" and images["status"] == "pass"
    qa = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "result": (
            "READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING"
            if qa_pass
            else "NO_SHIP"
        ),
        "status": "pass" if qa_pass else "fail",
        "blockers": [] if qa_pass else ["Gate 08 audit or image checks failed."],
        "majors": [],
        "minors": [],
        "expectedPending": [
            "User Gate 08 lighting approval",
            "Gate 09 environment review",
            "Gate 12 shipping-source visual approval",
            "iPhone acceptance after a separately authorized installation",
        ],
        "wholeCaseOnly": True,
        "explode": False,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "evidence": {
            "lightingReview": str(
                (ROOT / "lighting-review.png").relative_to(REPO_ROOT)
            ),
            "blenderAudit": str(AUDIT_REPORT.relative_to(REPO_ROOT)),
            "imageValidation": str(IMAGE_REPORT.relative_to(REPO_ROOT)),
        },
    }
    QA_REPORT.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": audit["status"],
                "qa": qa["result"],
                "geometryDigest": identity["fullGeometryDigest"],
                "materialDigest": material_digest,
                "ratios": {
                    role: item["ratioToKey"] for role, item in lights.items()
                },
                "checks": checks,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if not qa_pass:
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
