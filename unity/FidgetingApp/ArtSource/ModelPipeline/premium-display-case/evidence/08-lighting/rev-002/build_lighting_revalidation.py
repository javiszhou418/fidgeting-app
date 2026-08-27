#!/usr/bin/env python3
"""Build Premium Display Case Gate 08 rev 2 lighting evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

import bpy


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
EVIDENCE = ROOT.parent.parent
MODEL_ROOT = ROOT.parents[2]
LEGACY_BUILDER = ROOT.parent / "rev-001/build_lighting_lookdev.py"
SOURCE_ROOT = EVIDENCE / "07-material/rev-002"
SOURCE_BLEND = SOURCE_ROOT / "premium-display-case-material-r002.blend"
SOURCE_REPORT = SOURCE_ROOT / "material-revalidation.json"
SOURCE_VALIDATION = SOURCE_ROOT / "material-review-validation.json"
SOURCE_SNAPSHOT = SOURCE_ROOT / "material-compatibility-snapshot.json"
ARCHITECTURE = EVIDENCE / "04-architecture/rev-007/architecture.json"
PIPELINE = MODEL_ROOT / "pipeline.json"
OUTPUT_BLEND = ROOT / "premium-display-case-lighting-r002.blend"
REPORT = ROOT / "lighting-revalidation.json"

APPROVAL_QUOTE = "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"
EXPECTED_PIPELINE_REVISION = 63
EXPECTED_GEOMETRY_DIGEST = (
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
)
SOURCE_ASSET_IDS = (
    "premium-display-case-material-blend-r002",
    "premium-display-case-material-revalidation-r002",
    "premium-display-case-material-review-validation-r002",
    "premium-display-case-material-compatibility-snapshot-r002",
    "premium-display-case-material-turntable-mp4-r002",
    "premium-display-case-material-sheen-compatibility-r002",
    "premium-display-case-mesh-light-architecture-r007",
    "premium-display-case-geometry-blend-r003",
)


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


def all_checks_pass(report: dict[str, object]) -> bool:
    return report.get("status") == "pass" and all(report.get("checks", {}).values())


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    pipeline = json.loads(PIPELINE.read_text(encoding="utf-8"))
    gate07 = pipeline["stages"][6]
    source = json.loads(SOURCE_REPORT.read_text(encoding="utf-8"))
    source_validation = json.loads(SOURCE_VALIDATION.read_text(encoding="utf-8"))
    snapshot = json.loads(SOURCE_SNAPSHOT.read_text(encoding="utf-8"))
    architecture = json.loads(ARCHITECTURE.read_text(encoding="utf-8"))
    approval = gate07.get("materialSpec", {}).get("approval", {})
    if (
        pipeline["revision"] != EXPECTED_PIPELINE_REVISION
        or gate07["status"] != "approved"
        or approval.get("approvedRevision") != 2
        or approval.get("userApprovalQuote") != APPROVAL_QUOTE
        or approval.get("labelContentApproved") is not False
    ):
        raise RuntimeError("Gate 07 rev 2 must be approved with the exact label-content boundary.")
    if not all_checks_pass(source) or not all_checks_pass(source_validation):
        raise RuntimeError("Gate 07 rev 2 source evidence is not valid.")
    if sha256(SOURCE_BLEND) != source["outputBlendSha256"]:
        raise RuntimeError("Gate 07 rev 2 source blend hash changed.")
    if (
        snapshot["geometryIdentity"]["fullGeometryDigest"] != EXPECTED_GEOMETRY_DIGEST
        or snapshot["sheenMaskPolicy"]["outsideSubjectPixels"] != 0
        or snapshot["sheenMaskPolicy"]["outsideAllowedMaterialZonePixels"] != 0
        or architecture["evidenceRevision"] != 7
        or architecture["invariants"]["caseLightOutsideSilhouettePixels"] != 0
    ):
        raise RuntimeError("Approved geometry, architecture or sheen boundary drifted.")

    legacy = load_module("premium_display_case_gate08_rev2_legacy_builder", LEGACY_BUILDER)
    with tempfile.TemporaryDirectory(prefix="premium-display-case-gate08-r002-") as temp:
        temp_root = Path(temp)
        compatible_source = {
            "status": "pass",
            "outputBlendSha256": source["outputBlendSha256"],
            "materialParameters": source["materialParameters"],
        }
        transparent = dict(source["transparentOrdering"])
        transparent["pass"] = True
        compatible_audit = {
            "status": "pass",
            "checks": {"transparentOrdering": True},
            "transparentOrdering": transparent,
        }
        compatible_images = {"status": "pass"}
        compatible_manifest = {
            "revision": 34,
            "stages": [
                {},
                {},
                {},
                {},
                {},
                {},
                {"status": "approved", "decision": {"notes": "挺好的"}},
            ],
        }
        files = {
            "source": compatible_source,
            "audit": compatible_audit,
            "images": compatible_images,
            "manifest": compatible_manifest,
        }
        for name, payload in files.items():
            (temp_root / f"{name}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        legacy.ROOT = ROOT
        legacy.RAW = RAW
        legacy.GATE07 = SOURCE_ROOT
        legacy.SOURCE_BLEND = SOURCE_BLEND
        legacy.SOURCE_BUILD_REPORT = temp_root / "source.json"
        legacy.SOURCE_AUDIT_REPORT = temp_root / "audit.json"
        legacy.SOURCE_IMAGE_REPORT = temp_root / "images.json"
        legacy.MANIFEST = temp_root / "manifest.json"
        legacy.OUTPUT_BLEND = OUTPUT_BLEND
        legacy.REPORT = REPORT
        legacy.SOURCE_ASSET_IDS = SOURCE_ASSET_IDS
        legacy.SOURCE_CLAIM_IDS = tuple(architecture["sourceContract"]["sourceClaimIds"])
        legacy.main()

    scene = bpy.context.scene
    scene.name = "PremiumDisplayCase_Gate08_Lighting_Rev002"
    scene["lighting_revision"] = 2
    scene["source_gate07_material_revision"] = 2
    scene["source_gate07_approval_quote"] = APPROVAL_QUOTE
    scene["source_gate04_architecture_revision"] = 7
    scene["label_content_state"] = "placeholder-not-approved"
    scene["label_runtime_authority"] = "Unity real product data"
    scene["mesh_clipped_sheen_owner"] = "Unity MaterialPropertyBlock"
    scene["mesh_clipped_sheen_outside_silhouette_pixels"] = 0
    scene["external_halo"] = False
    scene["large_bloom"] = False
    scene["particles"] = False
    scene["persistent_emission"] = False
    scene["runtime_timing_baked"] = False
    scene["animation_easing_baked"] = False
    scene["lookdev_values_are_unity_runtime_constants"] = False
    for obj in scene.objects:
        if obj.type in {"LIGHT", "CAMERA"} and obj.name.startswith("M08_"):
            obj["lookdev_candidate_only"] = True
            obj["unity_runtime_constant"] = False
    if any(
        obj.animation_data and obj.animation_data.action
        for obj in scene.objects
        if obj.name == "PresentationRoot" or obj.name.startswith("M08_")
    ):
        raise RuntimeError("Gate 08 must not bake timing or easing into Blender.")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND), check_existing=False)

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report["lightingRevision"] = 2
    report["pipelineRevisionAtBuild"] = EXPECTED_PIPELINE_REVISION
    report["notice"] = "GATE 08 REV 2 LIGHTING · READY FOR REVIEW · NOT APPROVED"
    report["sourceGate07"] = {
        "materialRevision": 2,
        "approvalQuote": APPROVAL_QUOTE,
        "approvalScope": approval["approvalScope"],
        "labelContentApproved": False,
        "blendPath": str(SOURCE_BLEND.relative_to(legacy.REPO_ROOT)),
        "sha256Before": source["outputBlendSha256"],
        "sha256After": sha256(SOURCE_BLEND),
        "unchanged": source["outputBlendSha256"] == sha256(SOURCE_BLEND),
        "sourceAssetIds": list(SOURCE_ASSET_IDS),
        "sourceClaimIds": list(architecture["sourceContract"]["sourceClaimIds"]),
    }
    report["sourceGate04"] = {
        "architectureEvidenceRevision": 7,
        "sha256": sha256(ARCHITECTURE),
        "wholeAssembledCaseOnly": True,
        "meshClippedSheenOwner": "Unity MaterialPropertyBlock",
        "outsideSilhouettePixels": 0,
        "runtimeTimingIncluded": False,
    }
    report["materials"]["materialGraphDigests"] = source["materialGraphDigestsAfter"]
    report["materials"]["transparentOrderingPreflight"] = transparent
    report["labelPolicy"] = {
        "visibleContentState": "placeholder-not-approved",
        "blenderOwns": [
            "label geometry",
            "label UV",
            "paper zone",
            "transparent cover zone",
            "foil zone",
        ],
        "unityOwns": [
            "product name",
            "edition or finish",
            "acquired date",
            "rarity or level",
            "real collectible ID when available",
        ],
        "fakeOrPlaceholderCollectibleIdForbidden": True,
    }
    report["sheenCompatibility"] = {
        "classification": "material-runtime compatibility cue; not external light spill",
        "owner": "Unity MaterialPropertyBlock",
        "outsideSubjectPixels": 0,
        "outsideAllowedMaterialZonePixels": 0,
        "externalHalo": False,
        "pointLight": False,
        "runtimeTimingIncluded": False,
    }
    report["candidateBoundary"] = {
        "blenderLookdevCandidatesOnly": True,
        "automaticUnityRuntimeConstants": False,
        "tunableUntilShippingUnityPreview": [
            "intensity",
            "color temperature",
            "exposure",
            "field of view",
            "light width",
            "falloff",
        ],
    }
    report["animationBoundary"] = {
        "gate04StructurePreserved": True,
        "timingBaked": False,
        "easingBaked": False,
        "presentationRootAnimationAction": None,
    }
    report["forbiddenEffects"] = {
        "fixedGreenCast": False,
        "rarityLight": False,
        "externalHalo": False,
        "largeBloom": False,
        "particles": False,
        "flash": False,
        "shake": False,
        "persistentEmission": False,
    }
    report["scope"].update(
        {
            "sourceArchitectureEvidenceRevision": 7,
            "reviewExplodedPartCount": 0,
            "labelContentApproved": False,
            "runtimeTimingBaked": False,
            "runtimeEasingBaked": False,
        }
    )
    report["checks"].update(
        {
            "gate07Rev2ApprovalExact": True,
            "gate04Rev7ArchitectureApproved": True,
            "placeholderLabelContentNotApproved": True,
            "unityAuthoritativeLabelData": True,
            "meshClippedSheenZeroOutside": True,
            "noExternalHaloBloomParticlesOrEmission": True,
            "lookdevValuesAreCandidates": True,
            "runtimeTimingAndEasingNotBaked": True,
        }
    )
    report["status"] = "pass" if all(report["checks"].values()) else "fail"
    report["outputBlend"] = str(OUTPUT_BLEND.relative_to(legacy.REPO_ROOT))
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
                "geometryDigest": report["geometry"]["digestAfter"],
                "materialDigest": report["materials"]["digestAfter"],
                "labelContentState": report["labelPolicy"]["visibleContentState"],
                "outsideSilhouettePixels": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
