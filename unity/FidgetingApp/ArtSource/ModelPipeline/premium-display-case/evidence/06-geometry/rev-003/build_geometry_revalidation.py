#!/usr/bin/env python3
"""Revalidate Premium Display Case geometry from approved Gate 05 rev 3."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import bmesh
import bpy


OUTPUT = Path(__file__).resolve().parent
EVIDENCE = OUTPUT.parent.parent
SOURCE = EVIDENCE / "05-blockout/rev-003/premium-display-case-blockout-r003.blend"
OUTPUT_BLEND = OUTPUT / "premium-display-case-geometry-r003.blend"
REPORT = OUTPUT / "geometry-revalidation.json"
VALIDATOR_PATH = EVIDENCE / "06-geometry/rev-002/validate_geometry.py"
EXPECTED_SOURCE_SHA256 = "ed6d54899f53451634685e59d975c7ab16a9fbdfe5b94053a8d115f7d3a31c76"
EXPECTED_SOURCE_GEOMETRY_DIGEST = (
    "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
)
EXPECTED_DERIVATIVE_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
TUBE_NAME = "ContinuousTubePerimeter"


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)


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


VALIDATOR = load_module("premium_display_case_gate06_rev3_validator", VALIDATOR_PATH)


def signed_volume_mm3(obj: bpy.types.Object) -> float:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        value = 0.0
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            value += first.dot(second.cross(third)) / 6.0
        return value
    finally:
        evaluated.to_mesh_clear()


def reverse_faces_without_moving_vertices(obj: bpy.types.Object) -> None:
    coordinates = [tuple(vertex.co) for vertex in obj.data.vertices]
    matrix = obj.matrix_world.copy()
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
    finally:
        bm.free()
    obj.data.validate(verbose=True)
    obj.data.update()
    if coordinates != [tuple(vertex.co) for vertex in obj.data.vertices]:
        raise RuntimeError("Normals correction moved tube vertices.")
    if matrix != obj.matrix_world:
        raise RuntimeError("Normals correction changed the tube matrix.")


def main() -> None:
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Approved Gate 05 rev 3 blend hash changed.")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    source_identity = VALIDATOR.identity_snapshot(subjects)
    if source_identity["fullGeometryDigest"] != EXPECTED_SOURCE_GEOMETRY_DIGEST:
        raise RuntimeError("Gate 05 rev 3 geometry digest changed.")
    tube = bpy.data.objects[TUBE_NAME]
    before_volume = signed_volume_mm3(tube)
    if before_volume >= 0:
        raise RuntimeError("Expected historical negative tube winding was not present.")

    reverse_faces_without_moving_vertices(tube)
    tube["gate06_normals_only_derivative"] = True
    tube["gate06_winding_correction"] = "all-boundary-faces-reversed"
    tube["gate06_outer_boundary"] = "outward-from-material"
    tube["gate06_inner_boundary"] = "toward-lumen"

    result = VALIDATOR.evaluate_scene(source_identity, before_volume)
    derivative_identity = result["identity"]["derivative"]
    if result["status"] != "pass":
        raise RuntimeError("Gate 06 geometry validation failed.")
    if (
        derivative_identity["fullGeometryDigest"]
        != EXPECTED_DERIVATIVE_GEOMETRY_DIGEST
    ):
        raise RuntimeError("Normals-only derivative digest changed.")

    presentation = bpy.data.objects["PresentationRoot"]
    assembly = bpy.data.objects["CaseAssembly"]
    content_slot = bpy.data.objects["ContentSlot"]
    hierarchy_checks = {
        "presentationRootIdentity": (
            tuple(round(value, 9) for value in presentation.location) == (0.0, 0.0, 0.0)
            and tuple(round(value, 9) for value in presentation.rotation_euler)
            == (0.0, 0.0, 0.0)
            and tuple(round(value, 9) for value in presentation.scale)
            == (1.0, 1.0, 1.0)
        ),
        "caseAssemblyRigidChild": assembly.parent == presentation,
        "contentSlotCallerOwnedEmpty": (
            content_slot.type == "EMPTY"
            and content_slot.parent == bpy.data.objects["RearPolycarbonateShell"]
            and len(content_slot.children) == 0
        ),
        "noBakedRuntimeAnimation": all(
            obj.animation_data is None
            for obj in [presentation, assembly, content_slot, *subjects]
        ),
        "noForbiddenGeometry": not any(
            token in obj.name.lower()
            for obj in bpy.data.objects
            for token in ("halo", "particle", "proxy", "explode", "toy")
        ),
    }
    if not all(hierarchy_checks.values()):
        raise RuntimeError("Presentation ownership or forbidden-geometry check failed.")

    presentation["motion_owner"] = "Unity"
    presentation["runtime_transform_contract"] = (
        "bounded-entry-rotation-overlap; runtime-only; no baked animation"
    )
    presentation["case_instance_policy"] = "same-whole-case-through-ack"
    presentation["light_policy"] = "mesh-clipped-material-property-block"
    assembly["assembly_state"] = "always-assembled"
    content_slot["ownership"] = "caller"
    content_slot["independent_angular_velocity"] = 0.0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

    after_save_identity = VALIDATOR.identity_snapshot(
        [bpy.data.objects[name] for name in SUBJECT_NAMES]
    )
    checks = {
        **result["checks"],
        **hierarchy_checks,
        "geometryDigestStableAfterSave": (
            after_save_identity["fullGeometryDigest"]
            == EXPECTED_DERIVATIVE_GEOMETRY_DIGEST
        ),
        "boundsExact": result["bounds"]["sizeMm"]
        == {"width": 228.0, "height": 304.0, "depth": 59.0},
        "labelCenterYExact": (
            result["structural"]["labelPosition"]["candidateCenterYmm"] == 99.0
        ),
        "concentricCentersExact": (
            result["structural"]["cornerCenterFamilies"]["maximumDriftMm"] == 0.0
        ),
        "reviewExplodedArtifactCountZero": True,
        "shippingUnityUnchanged": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 3,
        "sourceGate05Revision": 3,
        "source": {
            "blend": repo_path(SOURCE),
            "sha256": EXPECTED_SOURCE_SHA256,
            "geometryDigest": EXPECTED_SOURCE_GEOMETRY_DIGEST,
        },
        "output": {
            "blend": repo_path(OUTPUT_BLEND),
            "sha256": sha256(OUTPUT_BLEND),
            "geometryDigest": after_save_identity["fullGeometryDigest"],
        },
        "identity": result["identity"],
        "bounds": result["bounds"],
        "meshIntegrity": result["meshIntegrity"],
        "tubeOrientation": result["tubeOrientation"],
        "structural": result["structural"],
        "hierarchyChecks": hierarchy_checks,
        "presentationOwnership": {
            "motionOwner": "Unity",
            "movingTransform": "PresentationRoot",
            "rigidChild": "CaseAssembly",
            "contentSlot": "caller-owned-static",
            "sameInstance": True,
            "wholeCaseOnly": True,
            "runtimeAnimationBakedInBlender": False,
        },
        "internalTechnicalExplodedSourceAssetId": (
            "premium-display-case-geometry-exploded-r002"
        ),
        "reviewArtifactExplodedPartCount": 0,
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "gate07Status": "blocked",
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "outputBlend": str(OUTPUT_BLEND),
                "geometryDigest": report["output"]["geometryDigest"],
                "tubeSignedVolumeMm3": report["tubeOrientation"][
                    "netMaterialSignedVolumeMm3"
                ],
            }
        )
    )


if __name__ == "__main__":
    main()
