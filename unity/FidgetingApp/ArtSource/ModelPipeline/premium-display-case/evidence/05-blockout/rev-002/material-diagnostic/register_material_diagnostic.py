#!/usr/bin/env python3
"""Register Gate 05 rev 2 supplementary material-diagnostic evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import uuid

import PIL


ROOT = Path(__file__).resolve().parent


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)
PIPELINE = (
    REPO_ROOT
    / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/pipeline.json"
)
HISTORY = (
    REPO_ROOT
    / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/history.ndjson"
)
BUILD_REPORT = ROOT / "material-diagnostic-build-report.json"
BLENDER_AUDIT = ROOT / "material-diagnostic-blender-audit.json"
IMAGE_REPORT = ROOT / "material-diagnostic-image-validation.json"
NOTICE = "DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 APPROVAL"
CLAIM_IDS = [
    "display-case-analysis-closed-loop-r002",
    "display-case-analysis-manifold-r002",
    "display-case-analysis-background-r002",
    "display-case-analysis-label-r002",
    "display-case-analysis-portrait-r002",
    "display-case-analysis-flow-r002",
    "display-case-analysis-environment-r002",
]
BASE_SOURCES = [
    "display-case-modeling-contract-r001",
    "premium-display-case-blockout-builder-r002",
    "premium-display-case-blockout-validator-r002",
    "premium-display-case-blockout-blend-r002",
    "premium-display-case-blockout-validation-r002",
]
MATERIAL_BLEND_ID = "premium-display-case-formal-material-blend-source"
MATERIAL_RECIPE_ID = "premium-display-case-formal-material-recipe-source"
BUILDER_ID = "premium-display-case-material-diagnostic-builder-r002"
AUDITOR_ID = "premium-display-case-material-diagnostic-auditor-r002"
IMAGE_VALIDATOR_ID = "premium-display-case-material-diagnostic-image-validator-r002"
REGISTRAR_ID = "premium-display-case-material-diagnostic-registrar-r002"
BLEND_ID = "premium-display-case-material-diagnostic-blend-r002"
BUILD_REPORT_ID = "premium-display-case-material-diagnostic-build-report-r002"
AUDIT_REPORT_ID = "premium-display-case-material-diagnostic-blender-audit-r002"
IMAGE_REPORT_ID = "premium-display-case-material-diagnostic-image-report-r002"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def asset(
    asset_id: str,
    slot: str,
    path: Path,
    role: str,
    producer_name: str,
    producer_version: str,
    recipe: str,
    content_class: str,
    note: str,
    source_asset_ids: list[str],
    *,
    asserted_by: str = "assistant",
    source_claim_ids: list[str] | None = CLAIM_IDS,
    view: dict[str, object] | None = None,
) -> dict[str, object]:
    if not path.exists():
        raise RuntimeError(f"Missing asset: {path}")
    record: dict[str, object] = {
        "id": asset_id,
        "stageId": "05-blockout",
        "slot": slot,
        "path": relative(path),
        "sha256": sha256(path),
        "exists": True,
        "sizeBytes": path.stat().st_size,
        "role": role,
        "producer": {
            "name": producer_name,
            "version": producer_version,
            "recipe": recipe,
        },
        "provenance": {
            "origin": "repository-generated",
            "contentClass": content_class,
            "assertedBy": asserted_by,
            "note": note,
        },
        "sourceAssetIds": source_asset_ids,
    }
    if source_claim_ids is not None:
        record["sourceClaimIds"] = source_claim_ids
    if view is not None:
        record["view"] = view
    return record


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    audit = json.loads(BLENDER_AUDIT.read_text(encoding="utf-8"))
    images = json.loads(IMAGE_REPORT.read_text(encoding="utf-8"))
    if not all(report["status"] == "pass" for report in (build, audit, images)):
        raise RuntimeError("Diagnostic reports must pass before registration.")
    if any(report["notice"] != NOTICE for report in (build, audit, images)):
        raise RuntimeError("Diagnostic notice mismatch.")

    material_blend = (
        REPO_ROOT / "unity/FidgetingApp/ArtSource/DisplayCase/PremiumDisplayCase.blend"
    )
    material_recipe = (
        REPO_ROOT
        / "unity/FidgetingApp/ArtSource/DisplayCase/build_premium_display_case.py"
    )
    formal_source_note = (
        "Existing formal Premium Display Case material source. It is registered "
        "for provenance only; the file hash is unchanged and this does not approve Gate 07."
    )
    assets = [
        asset(
            MATERIAL_BLEND_ID,
            "supplementary-material-source",
            material_blend,
            "historical",
            "Blender",
            "5.2.0 LTS",
            "Existing editable Premium Display Case material source",
            "formal-premium-display-case-material-source",
            formal_source_note,
            ["display-case-approved-shipping-baseline"],
            asserted_by="repository",
            source_claim_ids=None,
        ),
        asset(
            MATERIAL_RECIPE_ID,
            "supplementary-material-source",
            material_recipe,
            "historical",
            "deterministic-bpy",
            "repository source",
            "Existing Premium Display Case material recipe",
            "formal-premium-display-case-material-recipe",
            formal_source_note,
            ["display-case-approved-shipping-baseline"],
            asserted_by="repository",
            source_claim_ids=None,
        ),
        asset(
            BUILDER_ID,
            "supplementary-diagnostic-source",
            ROOT / "build_material_diagnostic.py",
            "process",
            "deterministic-bpy",
            "Blender 5.2.0 LTS",
            "Append formal materials, map them to Gate 05 rev 2, render Cycles views",
            "gate05-supplementary-material-diagnostic-builder",
            (
                "Builds diagnostic evidence only. Gate 05 rev 2 subject geometry and "
                "status remain unchanged; Gate 06 and Gate 07 remain blocked."
            ),
            [*BASE_SOURCES, MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID],
        ),
        asset(
            AUDITOR_ID,
            "supplementary-diagnostic-source",
            ROOT / "audit_material_diagnostic.py",
            "process",
            "Blender validation",
            "5.2.0 LTS",
            "Independent geometry, material, ordering, lighting, and gate-boundary audit",
            "gate05-supplementary-material-diagnostic-auditor",
            "Audits the diagnostic .blend without changing the Gate 05 source .blend.",
            [BUILDER_ID, "premium-display-case-blockout-validator-r002"],
        ),
        asset(
            IMAGE_VALIDATOR_ID,
            "supplementary-diagnostic-source",
            ROOT / "validate_material_diagnostic.py",
            "process",
            "Python Pillow + NumPy",
            f"Pillow {PIL.__version__}",
            "Add immutable diagnostic notice, assemble sheets, and measure image quality",
            "gate05-supplementary-material-image-validator",
            (
                "Adds only review labels and validates background continuity, label "
                "contrast, clipping, and same-camera comparison."
            ),
            [BUILDER_ID, AUDITOR_ID],
        ),
        asset(
            REGISTRAR_ID,
            "supplementary-diagnostic-source",
            ROOT / "register_material_diagnostic.py",
            "process",
            "fidgeting-model-pipeline",
            "2026-08-25",
            "Register hashed supplementary evidence without changing active Gate 05 output",
            "gate05-supplementary-material-diagnostic-registrar",
            (
                "Registers asset records and history while preserving Gate 05 "
                "ready_for_review, its output digest, and blocked downstream gates."
            ),
            [BUILD_REPORT_ID, AUDIT_REPORT_ID, IMAGE_REPORT_ID],
        ),
        asset(
            BLEND_ID,
            "supplementary-diagnostic-blend",
            ROOT / "premium-display-case-gate05-r2-material-diagnostic.blend",
            "source-model",
            "Blender",
            "5.2.0 LTS",
            relative(ROOT / "build_material_diagnostic.py"),
            "real-blender-gate05-supplementary-material-diagnostic",
            (
                "Diagnostic copy only. It maps formal PBR materials to unchanged Gate 05 "
                "rev 2 subject geometry and adds zero-thickness cover/foil review surfaces."
            ),
            [*BASE_SOURCES, MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID, BUILDER_ID],
        ),
        asset(
            BUILD_REPORT_ID,
            "supplementary-validation-report",
            BUILD_REPORT,
            "validation",
            "deterministic-bpy",
            "Blender 5.2.0 LTS",
            "Build-time geometry, source-hash, material, lighting, and gate-boundary checks",
            "gate05-supplementary-material-diagnostic-build-report",
            (
                "Records unchanged geometry digest, bounds, label Y, concentric error, "
                "manifold edges, flood-fill, and formal material values."
            ),
            [BUILDER_ID, BLEND_ID, MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID],
        ),
        asset(
            AUDIT_REPORT_ID,
            "supplementary-validation-report",
            BLENDER_AUDIT,
            "validation",
            "Blender validation",
            "5.2.0 LTS",
            relative(ROOT / "audit_material_diagnostic.py"),
            "gate05-supplementary-material-diagnostic-blender-audit",
            (
                "Independent audit passed. Transparent cover and foil remain zero-thickness "
                "diagnostic surfaces and do not enter the Gate 05 geometry digest."
            ),
            [AUDITOR_ID, BLEND_ID, BUILD_REPORT_ID],
        ),
        asset(
            IMAGE_REPORT_ID,
            "supplementary-validation-report",
            IMAGE_REPORT,
            "validation",
            "Python Pillow + NumPy",
            f"Pillow {PIL.__version__}",
            relative(ROOT / "validate_material_diagnostic.py"),
            "gate05-supplementary-material-diagnostic-image-report",
            (
                "Image checks pass for continuous low-saturation background, no localized "
                "noise spots, label contrast, transparent ordering preflight, and clipping."
            ),
            [IMAGE_VALIDATOR_ID, AUDIT_REPORT_ID],
        ),
    ]

    raw_views = {
        "hero": ("hero", "DIAGNOSTIC_HeroCamera"),
        "left-oblique": ("left-oblique", "DIAGNOSTIC_LeftObliqueCamera"),
        "right-oblique": ("right-oblique", "DIAGNOSTIC_RightObliqueCamera"),
        "low": ("low", "DIAGNOSTIC_LowCamera"),
        "side": ("right", "DIAGNOSTIC_SideCamera"),
        "label-closeup": ("label-closeup", "DIAGNOSTIC_LabelCloseupCamera"),
        "concentric-closeup": (
            "concentric-corner-closeup",
            "DIAGNOSTIC_ConcentricCornerCamera",
        ),
        "clay-hero-same-camera": ("hero-clay-control", "DIAGNOSTIC_HeroCamera"),
    }
    raw_ids: dict[str, str] = {}
    for name, (view_id, camera) in raw_views.items():
        asset_id = f"premium-display-case-material-diagnostic-raw-{name}-r002"
        raw_ids[name] = asset_id
        assets.append(asset(
            asset_id,
            "supplementary-diagnostic-raw-render",
            ROOT / "raw" / f"{name}.png",
            "blender-render",
            "Blender Cycles",
            "5.2.0 LTS",
            "96 adaptive samples, OpenImageDenoise, AgX Medium High Contrast",
            "real-blender-gate05-supplementary-material-diagnostic-render",
            (
                f"Unannotated real Blender Cycles {name} render. Diagnostic only; "
                "not Gate 07 approval and not shipping evidence."
            ),
            [BLEND_ID, BUILDER_ID, MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID],
            view={
                "id": view_id,
                "camera": camera,
                "renderEngine": "CYCLES",
                "axisContract": "X-width/Y-height/Z-front",
            },
        ))

    annotated_names = {
        "hero": "diagnostic-material-hero.png",
        "left-oblique": "diagnostic-material-left-oblique.png",
        "right-oblique": "diagnostic-material-right-oblique.png",
        "low": "diagnostic-material-low.png",
        "side": "diagnostic-material-side.png",
        "label-closeup": "diagnostic-material-label-closeup.png",
        "concentric-closeup": "diagnostic-material-concentric-closeup.png",
        "clay-hero-same-camera": "diagnostic-clay-hero-same-camera.png",
    }
    annotated_ids: dict[str, str] = {}
    for name, filename in annotated_names.items():
        asset_id = f"premium-display-case-material-diagnostic-{name}-r002"
        annotated_ids[name] = asset_id
        view_id, camera = raw_views[name]
        assets.append(asset(
            asset_id,
            "supplementary-diagnostic-review-render",
            ROOT / filename,
            "process",
            "Python Pillow",
            PIL.__version__,
            "Preserve Blender pixels and add diagnostic approval-boundary header/footer",
            "annotated-real-blender-gate05-material-diagnostic-render",
            (
                f"Annotated {name} review image. Every image states that this is a "
                "diagnostic material proxy and not Gate 07 approval."
            ),
            [raw_ids[name], IMAGE_VALIDATOR_ID],
            view={
                "id": view_id,
                "camera": camera,
                "renderEngine": "CYCLES",
                "annotation": NOTICE,
            },
        ))

    comparison_id = "premium-display-case-material-diagnostic-clay-pbr-comparison-r002"
    contact_id = "premium-display-case-material-diagnostic-contact-sheet-r002"
    assets.extend([
        asset(
            comparison_id,
            "supplementary-diagnostic-comparison",
            ROOT / "diagnostic-clay-vs-pbr-same-camera.png",
            "process",
            "Python Pillow",
            PIL.__version__,
            "Same-camera clay and formal PBR side-by-side comparison",
            "gate05-clay-pbr-same-camera-comparison",
            (
                "Same Gate 05 rev 2 geometry and hero camera. It isolates material "
                "readability and does not approve geometry or Gate 07."
            ),
            [
                raw_ids["clay-hero-same-camera"],
                raw_ids["hero"],
                IMAGE_VALIDATOR_ID,
            ],
            view={
                "id": "hero-clay-pbr-comparison",
                "camera": "DIAGNOSTIC_HeroCamera",
                "renderEngine": "CYCLES",
                "sameCamera": True,
            },
        ),
        asset(
            contact_id,
            "supplementary-diagnostic-contact-sheet",
            ROOT / "diagnostic-material-contact-sheet.png",
            "process",
            "Python Pillow",
            PIL.__version__,
            "Nine-cell formal material diagnostic contact sheet",
            "gate05-supplementary-material-diagnostic-contact-sheet",
            (
                "Hero, obliques, low, side, label, concentric corner, clay control, "
                "and same-camera comparison with explicit non-approval notice."
            ),
            [*raw_ids.values(), comparison_id, IMAGE_VALIDATOR_ID],
            view={
                "id": "material-diagnostic-contact-sheet",
                "camera": "multi-view-contact-sheet",
                "renderEngine": "CYCLES",
                "annotation": NOTICE,
            },
        ),
    ])

    manifest = json.loads(PIPELINE.read_text(encoding="utf-8"))
    existing_ids = {record["id"] for record in manifest["assets"]}
    duplicate_ids = [record["id"] for record in assets if record["id"] in existing_ids]
    if duplicate_ids:
        raise RuntimeError(f"Diagnostic assets are already registered: {duplicate_ids}")
    stage = next(item for item in manifest["stages"] if item["id"] == "05-blockout")
    if stage["status"] != "ready_for_review" or stage["blockoutSpec"]["revision"] != 2:
        raise RuntimeError("Gate 05 rev 2 must remain ready_for_review.")
    downstream = {
        item["id"]: {
            "status": item["status"],
            "revision": item["revision"],
            "inputDigest": item["inputDigest"],
            "outputDigest": item["outputDigest"],
            "artifactIds": list(item["artifactIds"]),
            "decision": item["decision"],
        }
        for item in manifest["stages"]
        if item["id"] in {"06-geometry", "07-material"}
    }
    if downstream["06-geometry"]["status"] != "blocked":
        raise RuntimeError("Gate 06 must remain blocked.")
    if downstream["07-material"]["status"] != "blocked":
        raise RuntimeError("Gate 07 must remain blocked.")
    active_artifact_ids = list(stage["artifactIds"])
    review_artifact_ids = list(stage["reviewArtifactIds"])
    output_digest = stage["outputDigest"]
    revision_before = manifest["revision"]
    now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    manifest["assets"].extend(assets)
    supplementary_ids = [record["id"] for record in assets]
    stage["supplementaryDiagnosticArtifactIds"] = supplementary_ids
    stage["blockoutSpec"]["supplementaryMaterialDiagnostic"] = {
        "evidenceClass": "supplementary-material-diagnostic",
        "status": "pass",
        "notice": NOTICE,
        "approvalEffect": "none-not-gate07-material-approval",
        "formalMaterialSources": [MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID],
        "diagnosticBlendId": BLEND_ID,
        "reviewArtifactIds": [
            annotated_ids["hero"],
            annotated_ids["left-oblique"],
            annotated_ids["right-oblique"],
            annotated_ids["low"],
            annotated_ids["side"],
            annotated_ids["label-closeup"],
            annotated_ids["concentric-closeup"],
            comparison_id,
            contact_id,
        ],
        "geometryDigest": audit["geometryDigest"],
        "boundsMm": audit["boundsMm"],
        "labelCenterYmm": audit["labelCenterYmm"],
        "maximumCornerCenterDriftMm": audit["maximumCornerCenterDriftMm"],
        "openBoundaryEdgeCount": audit["openBoundaryEdgeCount"],
        "nonManifoldEdgeCount": audit["nonManifoldEdgeCount"],
        "floodFillVisited": audit["floodFill"]["visitedSamples"],
        "floodFillTotal": audit["floodFill"]["sampleCount"],
        "transparentSortingInitialCheck": "pass-cycles-only-unity-unapproved",
        "labelReadabilityInitialCheck": "pass-diagnostic-only-phone-projection-deferred",
        "formalSourceImageTextureCount": build["formalSourceImageTextureCount"],
        "sourceTextureTruth": build["formalSourceTextureTruth"],
        "gate05Status": "ready_for_review",
        "gate06Status": "blocked",
        "gate07Status": "blocked",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    validation_ids = {item["id"] for item in stage["validations"]}
    new_validations = [
        {
            "id": "supplementary-material-diagnostic-only",
            "status": "pass",
            "evidence": (
                "All review images state DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 "
                "APPROVAL. Active Gate 05 artifacts, review artifacts and output digest "
                "remain unchanged."
            ),
        },
        {
            "id": "formal-material-source-provenance",
            "status": "pass",
            "evidence": (
                f"PremiumDisplayCase.blend {sha256(material_blend)} and "
                f"build_premium_display_case.py {sha256(material_recipe)} remain unchanged. "
                "Formal source contains no image-texture nodes; no bitmap was invented."
            ),
        },
        {
            "id": "supplementary-material-geometry-preservation",
            "status": "pass",
            "evidence": (
                f"Subject geometry digest {audit['geometryDigest']} is unchanged before "
                "assignment, after assignment and after renders; bounds 228 × 304 × 59 mm, "
                "label Y=99 mm, concentric drift 0 mm, open/non-manifold edges 0/0 and "
                "flood-fill 384/384 remain unchanged."
            ),
        },
        {
            "id": "supplementary-material-image-preflight",
            "status": "pass",
            "evidence": (
                "Cycles transparent ordering and label readability preflight pass. "
                "Background patch luma range is "
                f"{images['backgroundMetrics']['patchMeanLumaRange']} with zero localized "
                "residual outliers; Unity sorting and phone projection remain untested."
            ),
        },
        {
            "id": "supplementary-material-downstream-boundary",
            "status": "pass",
            "evidence": (
                "Gate 05 remains ready_for_review. Gate 06 and Gate 07 remain blocked. "
                "Shipping Unity, build, install and phone state are unchanged."
            ),
        },
    ]
    if validation_ids.intersection(item["id"] for item in new_validations):
        raise RuntimeError("Supplementary validations are already registered.")
    stage["validations"].extend(new_validations)
    manifest["revision"] = revision_before + 1
    manifest["updatedAt"] = now
    manifest["currentState"]["visualApproval"] = "pending"
    manifest["currentState"]["shippingAssetUnchanged"] = True
    manifest["currentState"]["deviceStatus"] = "not-approved"
    manifest["currentState"]["diagnosis"] = (
        "Gate 05 rev 2 remains ready_for_review. Supplementary formal-material diagnostic "
        "evidence was added without changing the active Gate 05 artifact set or output "
        "digest. Geometry digest/bounds/label Y/concentric error/manifold/flood-fill remain "
        "unchanged. Gate 06 and Gate 07 remain blocked; this is not Gate 07 approval. "
        "Shipping Unity, build, install and phone state are unchanged."
    )

    if stage["artifactIds"] != active_artifact_ids:
        raise RuntimeError("Active Gate 05 artifactIds changed.")
    if stage["reviewArtifactIds"] != review_artifact_ids:
        raise RuntimeError("Active Gate 05 reviewArtifactIds changed.")
    if stage["outputDigest"] != output_digest:
        raise RuntimeError("Active Gate 05 output digest changed.")
    for stage_id, snapshot in downstream.items():
        current = next(item for item in manifest["stages"] if item["id"] == stage_id)
        actual = {
            "status": current["status"],
            "revision": current["revision"],
            "inputDigest": current["inputDigest"],
            "outputDigest": current["outputDigest"],
            "artifactIds": list(current["artifactIds"]),
            "decision": current["decision"],
        }
        if actual != snapshot:
            raise RuntimeError(f"{stage_id} changed during supplementary registration.")

    temporary = PIPELINE.with_name(f"{PIPELINE.name}.tmp-{uuid.uuid4()}")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, PIPELINE)
    event = {
        "id": str(uuid.uuid4()),
        "type": "supplementary-diagnostic-evidence-added",
        "modelId": "premium-display-case",
        "manifestRevision": manifest["revision"],
        "timestamp": now,
        "stageId": "05-blockout",
        "blockoutRevision": 2,
        "evidenceClass": "supplementary-material-diagnostic",
        "notice": NOTICE,
        "approvalEffect": "none",
        "stageStatus": "ready_for_review",
        "activeArtifactIdsUnchanged": True,
        "activeReviewArtifactIdsUnchanged": True,
        "outputDigestUnchanged": True,
        "supplementaryArtifactIds": supplementary_ids,
        "formalMaterialSourceIds": [MATERIAL_BLEND_ID, MATERIAL_RECIPE_ID],
        "geometryDigest": audit["geometryDigest"],
        "boundsMm": audit["boundsMm"],
        "labelCenterYmm": audit["labelCenterYmm"],
        "maximumCornerCenterDriftMm": audit["maximumCornerCenterDriftMm"],
        "openBoundaryEdgeCount": audit["openBoundaryEdgeCount"],
        "nonManifoldEdgeCount": audit["nonManifoldEdgeCount"],
        "floodFill": (
            f"{audit['floodFill']['visitedSamples']}/"
            f"{audit['floodFill']['sampleCount']}"
        ),
        "gate06Status": "blocked",
        "gate07Status": "blocked",
        "shippingAssetUnchanged": True,
        "buildInstallPhonePush": False,
    }
    with HISTORY.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps({
        "manifestRevisionBefore": revision_before,
        "manifestRevisionAfter": manifest["revision"],
        "stageStatus": stage["status"],
        "activeArtifactIdsUnchanged": stage["artifactIds"] == active_artifact_ids,
        "outputDigestUnchanged": stage["outputDigest"] == output_digest,
        "supplementaryArtifactCount": len(supplementary_ids),
        "gate06Status": downstream["06-geometry"]["status"],
        "gate07Status": downstream["07-material"]["status"],
        "contactSheet": str(ROOT / "diagnostic-material-contact-sheet.png"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
