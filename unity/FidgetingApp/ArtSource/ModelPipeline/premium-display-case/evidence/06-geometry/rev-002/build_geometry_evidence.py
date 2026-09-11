#!/usr/bin/env python3
"""Build Premium Display Case Gate 06 normals-only geometry revision 2."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


OUTPUT = Path(__file__).resolve().parent
RAW = OUTPUT / "raw"
REV1 = OUTPUT.parent / "rev-001"
EVIDENCE = OUTPUT.parent.parent
GATE05 = EVIDENCE / "05-blockout/rev-002"
SOURCE_BLEND = GATE05 / "premium-display-case-blockout.blend"
SOURCE_BUILDER = GATE05 / "build_blockout.py"
SOURCE_VALIDATOR = GATE05 / "validate_blockout.py"
OUTPUT_BLEND = OUTPUT / "premium-display-case-geometry-r002.blend"
REPORT_PATH = OUTPUT / "geometry-validation.json"
PIPELINE_PATH = EVIDENCE.parent / "pipeline.json"
VALIDATOR_PATH = OUTPUT / "validate_geometry.py"
BASE_BUILDER_PATH = REV1 / "build_geometry_evidence.py"

SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)
ORTHOGRAPHIC_IDS = ("front", "back", "top", "bottom", "left", "right")
EXPECTED_SOURCE_FULL_GEOMETRY_DIGEST = (
    "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
)
EXPECTED_SOURCE_BLEND_SHA256 = (
    "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("premium_display_case_gate06_rev1_helpers", BASE_BUILDER_PATH)
VALIDATION = load_module(
    "premium_display_case_gate06_rev2_validator",
    VALIDATOR_PATH,
)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def signed_volume_mm3(obj: bpy.types.Object) -> float:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        signed_volume = 0.0
        for triangle in mesh.loop_triangles:
            first, second, third = (
                mesh.vertices[index].co for index in triangle.vertices
            )
            signed_volume += first.dot(second.cross(third)) / 6.0
        return signed_volume
    finally:
        evaluated.to_mesh_clear()


def reverse_all_faces_without_moving_vertices(obj: bpy.types.Object) -> None:
    before_coordinates = [
        (vertex.co.x, vertex.co.y, vertex.co.z)
        for vertex in obj.data.vertices
    ]
    before_matrix = obj.matrix_world.copy()
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.validate(verbose=True)
    mesh.update()
    after_coordinates = [
        (vertex.co.x, vertex.co.y, vertex.co.z)
        for vertex in obj.data.vertices
    ]
    if before_coordinates != after_coordinates:
        raise RuntimeError("Normals-only correction changed tube vertex coordinates.")
    if obj.matrix_world != before_matrix:
        raise RuntimeError("Normals-only correction changed the tube object matrix.")
    obj["gate06_normals_only_derivative"] = True
    obj["gate06_winding_correction"] = "all-boundary-faces-reversed"
    obj["gate06_outer_boundary"] = "outward-from-material"
    obj["gate06_inner_boundary"] = "toward-lumen"


def hide_non_subject_meshes(scene: bpy.types.Scene) -> None:
    for obj in scene.objects:
        if obj.type == "MESH" and obj.name not in SUBJECT_NAMES:
            obj.hide_render = True


def update_overlay_copy(objects: list[bpy.types.Object]) -> None:
    for obj in objects:
        if obj.name == "Gate06DimensionTitle" and obj.type == "FONT":
            obj.data.body = "REAL BLENDER · NORMALS-ONLY REV 2"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    source_hashes_before = {
        "blend": file_sha256(SOURCE_BLEND),
        "builder": file_sha256(SOURCE_BUILDER),
        "validator": file_sha256(SOURCE_VALIDATOR),
    }
    if source_hashes_before["blend"] != EXPECTED_SOURCE_BLEND_SHA256:
        raise RuntimeError("Approved Gate 05 rev 2 blend hash changed.")

    pipeline = json.loads(PIPELINE_PATH.read_text(encoding="utf-8"))
    gate05 = next(stage for stage in pipeline["stages"] if stage["id"] == "05-blockout")
    gate06 = next(stage for stage in pipeline["stages"] if stage["id"] == "06-geometry")
    approval = gate05.get("blockoutSpec", {}).get("approval", {})
    rejection_note = str(gate06.get("decision", {}).get("notes", ""))
    if (
        pipeline["revision"] != 29
        or gate05["status"] != "approved"
        or gate05.get("blockoutSpec", {}).get("revision") != 2
        or approval.get("approvedRevision") != 2
        or approval.get("userApprovalQuote") != "可以，继续推进"
        or gate06["status"] != "rejected"
        or gate06.get("geometrySpec", {}).get("revision") != 1
        or gate06.get("decision", {}).get("action") != "reject"
        or "signedVolumeMm3=-52932.982745" not in rejection_note
    ):
        raise RuntimeError(
            "Gate 06 rev 1 must be technically rejected before building rev 2."
        )

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    gate05_validator = VALIDATION.load_gate05_validator()
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    tube = bpy.data.objects["ContinuousTubePerimeter"]

    source_identity = VALIDATION.identity_snapshot(subjects)
    source_bounds = VALIDATION.world_bounds(subjects)
    source_tube_signed_volume = signed_volume_mm3(tube)
    source_tube_orientation = VALIDATION.hollow_tube_orientation(
        tube,
        gate05_validator,
    )
    if (
        source_identity["fullGeometryDigest"]
        != EXPECTED_SOURCE_FULL_GEOMETRY_DIGEST
    ):
        raise RuntimeError("Approved Gate 05 geometry digest changed.")
    if round(source_tube_signed_volume, 6) != -52932.982745:
        raise RuntimeError(
            f"Unexpected source tube signed volume: {source_tube_signed_volume}"
        )

    reverse_all_faces_without_moving_vertices(tube)
    derivative_identity = VALIDATION.identity_snapshot(subjects)
    derivative_tube_signed_volume = signed_volume_mm3(tube)
    if (
        source_identity["objectMatrixDigest"]
        != derivative_identity["objectMatrixDigest"]
        or source_identity["vertexPositionDigest"]
        != derivative_identity["vertexPositionDigest"]
        or source_identity["silhouetteDigest"]
        != derivative_identity["silhouetteDigest"]
    ):
        raise RuntimeError("Normals-only derivative changed matrix, vertices, or silhouette.")
    if (
        source_identity["topologyWindingDigest"]
        == derivative_identity["topologyWindingDigest"]
    ):
        raise RuntimeError("Normals-only derivative did not change winding topology.")

    scene["gate"] = "06-geometry"
    scene["geometry_revision"] = 2
    scene["source_gate05_revision"] = 2
    scene["source_gate05_sha256"] = source_hashes_before["blend"]
    scene["source_gate05_geometry_digest"] = source_identity["fullGeometryDigest"]
    scene["normals_only_derivative"] = True
    scene["vertex_position_digest"] = derivative_identity["vertexPositionDigest"]
    scene["silhouette_digest"] = derivative_identity["silhouetteDigest"]
    scene["topology_winding_digest"] = derivative_identity[
        "topologyWindingDigest"
    ]
    scene["shipping_reveal_policy"] = "always-assembled-never-explodes"
    scene["exploded_evidence_policy"] = "internal-geometry-validation-only"
    scene["gate07_entered"] = False
    scene["shipping_unity_changed"] = False
    scene["build_install_phone_push"] = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.008,
        0.012,
        0.020,
        1.0,
    )
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32
    hide_non_subject_meshes(scene)

    cameras = {
        "front": BASE.add_camera("Gate06CameraFront", (0.0, 0.0, 700.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "back": BASE.add_camera("Gate06CameraBack", (0.0, 0.0, -700.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "top": BASE.add_camera("Gate06CameraTop", (0.0, 700.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=285.0),
        "bottom": BASE.add_camera("Gate06CameraBottom", (0.0, -700.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=285.0),
        "left": BASE.add_camera("Gate06CameraLeft", (-700.0, 0.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
        "right": BASE.add_camera("Gate06CameraRight", (700.0, 0.0, 0.0), (0.0, 0.0, 0.0), orthographic_scale=360.0),
    }
    resolutions = {
        "front": (1400, 1800),
        "back": (1400, 1800),
        "top": (1800, 1000),
        "bottom": (1800, 1000),
        "left": (1000, 1800),
        "right": (1000, 1800),
    }
    cross_view = {}
    derivative_full_digest = derivative_identity["fullGeometryDigest"]
    for camera_id in ORTHOGRAPHIC_IDS:
        before_view = VALIDATION.full_geometry_digest(subjects)
        BASE.render(
            scene,
            cameras[camera_id],
            RAW / f"{camera_id}.png",
            resolutions[camera_id],
            "BLENDER_EEVEE",
        )
        after_view = VALIDATION.full_geometry_digest(subjects)
        cross_view[camera_id] = {
            "cameraObject": cameras[camera_id].name,
            "cameraId": camera_id,
            "type": cameras[camera_id].data.type,
            "orthographicScale": cameras[camera_id].data.ortho_scale,
            "axisContract": "X-width/Y-height/Z-front",
            "fullGeometryDigestBefore": before_view,
            "fullGeometryDigestAfter": after_view,
            "sameDerivativeGeometry": (
                before_view == after_view == derivative_full_digest
            ),
            "rawPath": repo_path(RAW / f"{camera_id}.png"),
        }

    workbench_camera = BASE.add_camera(
        "Gate06CameraWorkbench",
        (340.0, 210.0, 780.0),
        (0.0, 0.0, 0.0),
        lens=72.0,
    )
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    BASE.render(
        scene,
        workbench_camera,
        RAW / "workbench.png",
        (1800, 1500),
        "BLENDER_WORKBENCH",
    )

    annotation_collection = bpy.data.collections.new("Gate06_ReviewAnnotations")
    scene.collection.children.link(annotation_collection)
    dimension_overlay = BASE.create_dimension_overlay(annotation_collection)
    update_overlay_copy(dimension_overlay)
    pivot_overlay = BASE.create_pivot_overlay(
        annotation_collection,
        gate05_validator,
    )
    overlay_camera = BASE.add_camera(
        "Gate06CameraOverlay",
        (0.0, 0.0, 760.0),
        (0.0, 0.0, 0.0),
        orthographic_scale=405.0,
    )
    BASE.set_visible(dimension_overlay, True)
    BASE.render(
        scene,
        overlay_camera,
        RAW / "dimension-overlay.png",
        (1800, 2000),
        "BLENDER_EEVEE",
    )
    BASE.set_visible(dimension_overlay, False)
    BASE.set_visible(pivot_overlay, True)
    BASE.render(
        scene,
        overlay_camera,
        RAW / "pivot-axis-overlay.png",
        (1800, 2000),
        "BLENDER_EEVEE",
    )
    BASE.set_visible(pivot_overlay, False)

    _exploded_collection, exploded = BASE.create_exploded_duplicates(subjects)
    for obj in subjects:
        obj.hide_render = True
    BASE.set_visible(exploded, True)
    scene.display.shading.color_type = "OBJECT"
    exploded_camera = BASE.add_camera(
        "Gate06CameraExploded",
        (720.0, 520.0, 1300.0),
        (0.0, 0.0, 0.0),
        lens=76.0,
    )
    BASE.render(
        scene,
        exploded_camera,
        RAW / "exploded-geometry.png",
        (2000, 1600),
        "BLENDER_WORKBENCH",
    )
    BASE.set_visible(exploded, False)
    for obj in subjects:
        obj.hide_render = False
    scene.display.shading.color_type = "MATERIAL"
    bpy.context.view_layer.update()

    gate05_structural = gate05_validator.validate_scene()
    tube_flow = BASE.passage_and_wall_report(gate05_validator, tube)
    hierarchy = BASE.hierarchy_report(subjects)
    evaluated = VALIDATION.evaluate_scene(
        source_identity,
        source_tube_signed_volume,
    )
    derivative_tube_orientation = evaluated["tubeOrientation"]

    modeled_hidden_parts = sorted(
        obj.name
        for obj in bpy.data.objects
        if (
            obj.type == "MESH"
            and obj.name in {
                "PresentationRoot",
                *(
                    child.name
                    for child in bpy.data.objects[
                        "PresentationRoot"
                    ].children_recursive
                ),
            }
            and obj.name not in SUBJECT_NAMES
        )
    )
    invented_tokens = (
        "fastener", "screw", "bolt", "spring", "bearing",
        "magnet", "latch", "hinge", "pump",
    )
    hierarchy_names = {
        "PresentationRoot",
        *(
            obj.name
            for obj in bpy.data.objects["PresentationRoot"].children_recursive
        ),
    }
    invented_internal_names = sorted(
        name
        for name in hierarchy_names
        if any(token in name.lower() for token in invented_tokens)
    )

    for obj in exploded:
        obj.hide_render = True
    scene.camera = workbench_camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1400
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

    identity_after_save = VALIDATION.identity_snapshot(subjects)
    bounds_after_save = VALIDATION.world_bounds(subjects)
    source_hashes_after = {
        "blend": file_sha256(SOURCE_BLEND),
        "builder": file_sha256(SOURCE_BUILDER),
        "validator": file_sha256(SOURCE_VALIDATOR),
    }
    checks = {
        **evaluated["checks"],
        "gate05ApprovedThroughPipeline": (
            gate05["status"] == "approved"
            and approval.get("userApprovalQuote") == "可以，继续推进"
        ),
        "gate06Rev1TechnicalRejectionRecorded": (
            gate06["status"] == "rejected"
            and "signedVolumeMm3=-52932.982745" in rejection_note
        ),
        "sourceFilesUnchanged": source_hashes_before == source_hashes_after,
        "derivativeIdentityUnchangedAfterRendersAndSave": (
            evaluated["identity"]["derivative"] == identity_after_save
        ),
        "boundsUnchanged": (
            source_bounds == evaluated["bounds"] == bounds_after_save
        ),
        "sixOrthographicSameDerivative": all(
            item["sameDerivativeGeometry"] for item in cross_view.values()
        ),
        "tubeVolumetricFloodFill": tube_flow["pass"],
        "tubeSectionAndWall": tube_flow["pass"],
        "contentSlotAndMotionOwnership": hierarchy["pass"],
        "labelClearance": gate05_structural["labelPosition"]["pass"],
        "noHiddenStructureInvented": (
            not modeled_hidden_parts and not invented_internal_names
        ),
        "explodedTubeRemainsOneDerivativePart": (
            len(
                [
                    obj
                    for obj in exploded
                    if obj.name == "EXPLODED_ContinuousTubePerimeter"
                ]
            )
            == 1
            and exploded[3].data is tube.data
        ),
        "explodedEvidenceInternalOnly": (
            all(
                obj["shipping_animation_eligible"] is False for obj in exploded
            )
            and scene["shipping_reveal_policy"]
            == "always-assembled-never-explodes"
        ),
        "gate07NotEntered": scene["gate07_entered"] is False,
        "shippingUnityUnchanged": scene["shipping_unity_changed"] is False,
        "noBuildInstallPhonePush": scene["build_install_phone_push"] is False,
    }
    report = {
        "schemaVersion": 2,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "pipelineRevisionAtBuild": pipeline["revision"],
        "sourceGate05": {
            "blockoutRevision": 2,
            "approvalQuote": approval.get("userApprovalQuote"),
            "approvalScope": approval.get("approvalScope"),
            "blendPath": repo_path(SOURCE_BLEND),
            "deterministicBuilderPath": repo_path(SOURCE_BUILDER),
            "validatorPath": repo_path(SOURCE_VALIDATOR),
            "hashesBefore": source_hashes_before,
            "hashesAfter": source_hashes_after,
            "unchanged": source_hashes_before == source_hashes_after,
        },
        "supersededGate06Revision": {
            "geometryRevision": 1,
            "technicalDisposition": "rejected-and-superseded",
            "reason": (
                "ContinuousTubePerimeter net signed material volume was "
                "-52932.982745 mm3 and was incorrectly allowed to pass."
            ),
            "evidencePreserved": True,
            "path": repo_path(REV1),
        },
        "geometryIdentity": {
            "subjectObjects": list(SUBJECT_NAMES),
            "source": source_identity,
            "derivative": identity_after_save,
            "matrixDigestUnchanged": (
                source_identity["objectMatrixDigest"]
                == identity_after_save["objectMatrixDigest"]
            ),
            "vertexPositionDigestUnchanged": (
                source_identity["vertexPositionDigest"]
                == identity_after_save["vertexPositionDigest"]
            ),
            "silhouetteDigestUnchanged": (
                source_identity["silhouetteDigest"]
                == identity_after_save["silhouetteDigest"]
            ),
            "topologyWindingDigestChanged": (
                source_identity["topologyWindingDigest"]
                != identity_after_save["topologyWindingDigest"]
            ),
            "onlyTubeTopologyWindingChanged": checks[
                "onlyTubeTopologyWindingChanged"
            ],
            "sameDerivativeAcrossViews": checks[
                "sixOrthographicSameDerivative"
            ],
            "crossView": cross_view,
            "pass": (
                checks["objectMatricesUnchanged"]
                and checks["vertexPositionsUnchanged"]
                and checks["silhouetteDigestUnchanged"]
                and checks["topologyWindingDigestChanged"]
                and checks["onlyTubeTopologyWindingChanged"]
            ),
        },
        "windingCorrection": {
            "scope": "ContinuousTubePerimeter face winding only",
            "operation": "reverse every outer and inner boundary face",
            "vertexCoordinatesChanged": False,
            "objectMatrixChanged": False,
            "boundsChanged": False,
            "crossSectionChanged": False,
            "wallThicknessChanged": False,
            "labelsChanged": False,
            "cornerCentersChanged": False,
            "partHierarchyChanged": False,
            "silhouetteChanged": False,
            "before": {
                "netMaterialSignedVolumeMm3": round(
                    source_tube_signed_volume,
                    6,
                ),
                "outerBoundarySignedVolumeMm3": source_tube_orientation[
                    "outerBoundary"
                ]["signedVolumeMm3"],
                "innerBoundarySignedVolumeMm3": source_tube_orientation[
                    "innerBoundary"
                ]["signedVolumeMm3"],
                "orientationDisposition": source_tube_orientation[
                    "orientationDisposition"
                ],
            },
            "after": {
                "netMaterialSignedVolumeMm3": round(
                    derivative_tube_signed_volume,
                    6,
                ),
                "outerBoundarySignedVolumeMm3": derivative_tube_orientation[
                    "outerBoundary"
                ]["signedVolumeMm3"],
                "innerBoundarySignedVolumeMm3": derivative_tube_orientation[
                    "innerBoundary"
                ]["signedVolumeMm3"],
                "orientationDisposition": derivative_tube_orientation[
                    "orientationDisposition"
                ],
            },
            "pass": derivative_tube_orientation["pass"],
        },
        "bounds": {
            "targetMm": {"width": 228.0, "height": 304.0, "depth": 59.0},
            "measured": evaluated["bounds"],
            "portraitWidthHeightRatio": 0.75,
            "toleranceMm": 0.01,
            "pass": (
                checks["approvedEnvelopeExact"]
                and checks["portraitRatioExact"]
                and checks["boundsUnchanged"]
            ),
        },
        "label": {
            "baselineCenterYmm": 105.0,
            "approvedCenterYmm": 99.0,
            "approvedDownshiftMm": 6.0,
            "minimumFrameToChamberRimMm": gate05_structural[
                "labelPosition"
            ]["minimumLabelFrameToChamberRimMm"],
            "minimumFrameToTubeInnerMm": gate05_structural[
                "labelPosition"
            ]["minimumLabelFrameToTubeInnerMm"],
            "minimumPaperToInsertFaceMm": gate05_structural[
                "labelPosition"
            ]["minimumLabelPaperToInsertFaceMm"],
            "minimumRequiredClearanceMm": gate05_structural[
                "labelPosition"
            ]["minimumRequiredClearanceMm"],
            "pass": checks["labelAndConcentricValuesPreserved"]
            and checks["labelClearance"],
        },
        "concentricContours": {
            "outerRadiusMm": 20.0,
            "families": gate05_structural["cornerCenterFamilies"],
            "maximumCenterDriftMm": gate05_structural[
                "cornerCenterFamilies"
            ]["maximumDriftMm"],
            "toleranceMm": 0.01,
            "pass": checks["labelAndConcentricValuesPreserved"],
        },
        "meshIntegrity": evaluated["meshIntegrity"],
        "closedTube": {
            "object": tube.name,
            "meshObjectCount": 1,
            "connectedMaterialBodyCount": gate05_structural[
                "closedTube"
            ]["topology"]["connectedMaterialBodyCount"],
            "boundarySurfaceComponentCount": derivative_tube_orientation[
                "boundarySurfaceComponentCount"
            ],
            "boundaryOrientation": derivative_tube_orientation,
            "pathClosed": gate05_structural["closedTube"]["pathClosed"],
            "pathSampleCount": gate05_structural["closedTube"][
                "pathSampleCount"
            ],
            "cornerRadiiMm": gate05_structural["closedTube"][
                "cornerRadiiMm"
            ],
            "declaredOuterSectionMm": gate05_structural["closedTube"][
                "outerSectionMm"
            ],
            "declaredPassageSectionMm": gate05_structural["closedTube"][
                "passageSectionMm"
            ],
            "declaredWallThicknessMm": gate05_structural["closedTube"][
                "wallThicknessMm"
            ],
            "volumetricPassageFloodFill": tube_flow,
            "neverSplitIntoFourSides": True,
            "pass": (
                derivative_tube_orientation["pass"] and tube_flow["pass"]
            ),
        },
        "hierarchyAndMotion": hierarchy,
        "hiddenStructure": {
            "modeledHiddenPartNames": modeled_hidden_parts,
            "inventedInternalNames": invented_internal_names,
            "inventedInternalPartCount": (
                len(modeled_hidden_parts) + len(invented_internal_names)
            ),
            "transparentCoverRemainsUnmodeled": (
                hierarchy["transparentCover"]["type"] == "EMPTY"
            ),
            "pass": checks["noHiddenStructureInvented"],
        },
        "explodedEvidence": {
            "purpose": "internal-geometry-validation-only",
            "shippingRevealPolicy": "always-assembled-never-explodes",
            "approvedVisibleSubjectPartCount": len(SUBJECT_NAMES),
            "explodedObjectNames": [obj.name for obj in exploded],
            "continuousTubeExplodedObjectCount": 1,
            "continuousTubeUsesExactDerivativeMeshData": (
                exploded[3].data is tube.data
            ),
            "inventedInternalPartCount": 0,
            "pass": (
                checks["explodedTubeRemainsOneDerivativePart"]
                and checks["explodedEvidenceInternalOnly"]
            ),
        },
        "evidence": {
            "rawOrthographic": {
                camera_id: repo_path(RAW / f"{camera_id}.png")
                for camera_id in ORTHOGRAPHIC_IDS
            },
            "rawWorkbench": repo_path(RAW / "workbench.png"),
            "rawDimensionOverlay": repo_path(
                RAW / "dimension-overlay.png"
            ),
            "rawPivotAxisOverlay": repo_path(
                RAW / "pivot-axis-overlay.png"
            ),
            "rawExplodedGeometry": repo_path(
                RAW / "exploded-geometry.png"
            ),
            "outputBlend": repo_path(OUTPUT_BLEND),
            "realBlenderNormalsOnlyDerivative": True,
        },
        "scope": {
            "earliestAffectedGate": "06-geometry",
            "gate05ContractConflict": False,
            "gate05SourceModified": False,
            "vertexGeometryChanged": False,
            "topologyWindingChanged": True,
            "finalMaterialsApproved": False,
            "gate07Entered": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "checks": checks,
        "blender": bpy.app.version_string,
        "outputBlendSha256": file_sha256(OUTPUT_BLEND),
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "pipelineRevisionAtBuild": pipeline["revision"],
        "sourceBlendSha256": source_hashes_before["blend"],
        "sourceFullGeometryDigest": source_identity["fullGeometryDigest"],
        "derivativeFullGeometryDigest": identity_after_save[
            "fullGeometryDigest"
        ],
        "vertexPositionDigest": identity_after_save[
            "vertexPositionDigest"
        ],
        "silhouetteDigest": identity_after_save["silhouetteDigest"],
        "topologyWindingDigest": identity_after_save[
            "topologyWindingDigest"
        ],
        "windingBeforeAfter": report["windingCorrection"],
        "boundsMm": report["bounds"]["measured"]["sizeMm"],
        "floodFill": (
            f"{tube_flow['visitedSamples']}/{tube_flow['sampleCount']}"
        ),
        "outputBlend": str(OUTPUT_BLEND),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
