#!/usr/bin/env python3
"""Write Gate 09 rev 9 Unity portability contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[8]
CONTRACT = HERE / "unity-portability-contract-r009.json"
VALIDATION = HERE / "portability-validation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def asset(path: Path, role: str, color_space=None) -> dict:
    record = {
        "path": path.relative_to(REPO).as_posix(),
        "sha256": sha256(path),
        "role": role,
    }
    if color_space:
        record["colorSpace"] = color_space
    return record


def main() -> None:
    build = json.loads((HERE / "environment-build-validation.json").read_text())
    blender = json.loads((HERE / "blender-environment-audit.json").read_text())
    images = json.loads((HERE / "image-environment-audit.json").read_text())
    turntable = json.loads((HERE / "environment-turntable-validation.json").read_text())
    if not all(report["pass"] for report in [build, blender, images, turntable]):
        raise RuntimeError("Gate 09 evidence must pass before portability registration.")
    gate08 = HERE.parent.parent / "08-lighting/rev-006"
    gate07 = HERE.parent.parent / "07-material/rev-013"
    assets = {
        "gate07MaterialBlend": asset(
            gate07 / "magnetic-slide-tile-material-r013.blend",
            "approved-corrected-material-source",
        ),
        "gate08LightingBlend": asset(
            gate08 / "magnetic-slide-tile-lighting-r006.blend",
            "approved-portable-lighting-source",
        ),
        "gate09EnvironmentBlend": asset(
            HERE / "magnetic-slide-tile-environment-r009.blend",
            "current-environment-source",
        ),
        "interactiveReviewGlb": asset(
            HERE / "magnetic-slide-tile-environment-r009-lookdev.glb",
            "interactive-review-model-not-export-approved",
        ),
        "neutralControl": asset(
            HERE / "neutral-control-r009.exr",
            "revalidated-current-lighting-control",
            "scene-linear Rec.709/D65",
        ),
        "targetEquirectangular": asset(
            HERE / "target-shipping-studio-r009.exr",
            "portable-target-environment",
            "scene-linear Rec.709/D65",
        ),
        "cubemapContract": asset(
            HERE / "cubemap-r009/cubemap-contract.json",
            "unity-cubemap-orientation-contract",
        ),
        "comparisonTurntable": asset(
            HERE / "gate09-r009-neutral-target-turntable.mp4",
            "matched-real-render-comparison",
        ),
    }
    cubemap_assets = {
        face: asset(HERE / record["path"], f"unity-cubemap-{face}", "scene-linear Rec.709/D65")
        for face, record in build["cubemap"]["faces"].items()
    }
    contract = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "modelId": "magnetic-slide-tile",
        "status": "portable-input-contract-not-unity-import-settings",
        "approvalAuthority": {
            "gate08ExactUserWording": "你开始吧",
            "decisionSource": "latest-explicit-chat",
        },
        "currentInputs": {
            "geometryDigest": build["source"]["geometryDigest"],
            "materialSourceSha256": build["source"]["materialSha256"],
            "lightingSourceSha256": build["source"]["sha256"],
            "mechanismContractSha256": build["source"]["mechanismContractSha256"],
            "oldGate09AssetsCurrent": False,
            "oldGate09Policy": "immutable history only; no stale environment asset is a current input",
        },
        "assets": assets,
        "cubemapFaces": cubemap_assets,
        "exactPreservation": {
            "geometry": "ordered vertex/index digest exact",
            "hierarchyAndPivot": "exact names, parents, and fixed-axis transform",
            "materialPartitions": build["materialPartitions"]["objects"],
            "materialSlotOrder": "exact",
            "polygonMaterialIndices": "exact",
            "artworkUvs": "exact; cap within 0..1; non-cap sentinel remains -1,-1",
            "artworkMasks": "upper and lower remain independent",
            "sideArtworkTriangles": 0,
            "undersideArtworkTriangles": 0,
            "emission": 0,
        },
        "environmentComparison": {
            "identical": [
                "camera matrix and lens",
                "model transforms",
                "mesh and UV data",
                "material slots and polygon indices",
                "light count and settings",
                "Raw scene-linear render",
                "neutral-display-v1 mapping",
                "exposure and background composite",
            ],
            "onlyChanged": "environment texture input",
            "neutral": build["neutral"],
            "target": build["target"],
            "matchedPairState": {
                key: value["stateIdentical"] for key, value in build["pairs"].items()
            },
        },
        "unityEnvironmentImport": {
            "preferredSource": assets["targetEquirectangular"],
            "projection": "latitude-longitude equirectangular",
            "textureShape": "Cube",
            "sRGB": False,
            "alphaSource": "None",
            "generateMipmaps": True,
            "wrapMode": "Clamp",
            "filterMode": "Trilinear",
            "hdrFormat": "RGBAHalf or BC6H after measured iPhone comparison",
            "compressionAtGate09": "None",
            "worldStrength": 0.85,
            "rotationDegrees": 0,
            "fallbackFaces": cubemap_assets,
            "coordinateMapping": build["cubemap"]["coordinateMapping"],
            "orientationConvention": build["cubemap"]["faceConvention"],
            "orientationValidation": {
                "brightestDirectionUnity": build["cubemap"]["brightestDirectionUnity"],
                "angularErrorDegrees": build["cubemap"]["brightestDirectionAngularErrorDegrees"],
                "maximumAllowedDegrees": 1,
            },
        },
        "materialTransport": {
            "shaderTarget": "URP Lit-compatible custom material at Gate 10/11",
            "zones": {
                "topArtwork": "blood-red crystal plus independent black artwork",
                "solidDarkSide": "zero texture sampling",
                "polishedSilverRim": "bright neutral metal reflection response",
                "neutralUnderside": "zero artwork sampling",
            },
            "sampling": {
                "artwork": "Clamp; linear mask; no wrap",
                "baseColor": "sRGB",
                "roughnessMetallicAo": "linear",
                "normal": "linear tangent-space MikkTSpace",
            },
            "gate10Requirement": "Bake and hash portable BaseMap, MaskMap, Normal, and independent artwork masks without merging material zones.",
        },
        "displayMapping": {
            "reference": "neutral-display-v1",
            "blenderRender": "Raw scene-linear HDR EXR",
            "mapping": "rgb=max(rgb,0); rgb=rgb/(1+0.18*rgb); IEC 61966-2-1 sRGB encode",
            "unityStartingPoint": "URP linear HDR; apply the same mapping in parity capture",
            "fallback": "If runtime display differs, Gate 11 must fit and hash a LUT from linear matched frames.",
        },
        "motion": {
            "fixed": ["BottomExterior", "InternalAxisBoss"],
            "rotationOnlyAt": "sMax",
            "fullRotationDegrees": 360,
            "slideReturnOnlyAtDegrees": [0, 360],
            "reviewStates": [
                "closed-0",
                "max-open-0",
                "max-open-12",
                "max-open-36",
                "max-open-360",
            ],
            "noPitchRollFlip": True,
            "noPenetration": True,
            "noDebugProxy": True,
            "recording": assets["comparisonTurntable"],
        },
        "acceptanceTolerances": {
            "environmentRgbNonzeroFraction": 1,
            "equirectangularSeamMaxLinearDelta": 1e-6,
            "cubemapOrientationMaxDegrees": 1,
            "geometryDigest": "exact",
            "materialSlotAndIndexDigest": "exact",
            "uvDigest": "exact",
            "sideAndUndersideArtworkTriangles": 0,
            "standardViewClippingMaxFraction": 0.001,
            "reflectionCloseupClippingMaxFraction": 0.002,
            "fixedAxisVarianceMm": 1e-9,
            "pitchRollRadians": 1e-9,
            "emission": 0,
        },
        "deferred": {
            "gate10Export": True,
            "unityImport": True,
            "unityParity": True,
            "shippingScene": True,
            "buildInstallPhone": True,
            "deviceAcceptance": True,
        },
    }
    CONTRACT.write_text(json.dumps(contract, indent=2) + "\n")
    contract_sha = sha256(CONTRACT)
    checks = {
        "allEvidencePassed": all(report["pass"] for report in [build, blender, images, turntable]),
        "sourceHashesCurrent": assets["gate08LightingBlend"]["sha256"] == build["source"]["sha256"]
        and assets["gate07MaterialBlend"]["sha256"] == build["source"]["materialSha256"],
        "neutralRevalidated": assets["neutralControl"]["sha256"] == build["neutral"]["sha256"],
        "targetHash": assets["targetEquirectangular"]["sha256"] == build["target"]["sha256"],
        "cubemapFaceHashes": all(
            cubemap_assets[face]["sha256"] == record["sha256"]
            for face, record in build["cubemap"]["faces"].items()
        ),
        "materialPartitions": blender["checks"]["glbPartitions"],
        "displayMapping": contract["displayMapping"]["reference"] == "neutral-display-v1",
        "motion": turntable["checks"]["rotationOnlyAtEndpoint"]
        and turntable["checks"]["returnOnlyAligned"],
        "scope": all(contract["deferred"].values()),
    }
    validation = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "contract": CONTRACT.name,
        "contractSha256": contract_sha,
        "checks": checks,
        "pass": all(checks.values()),
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps({
        "pass": validation["pass"],
        "contractSha256": contract_sha,
        "targetEnvironmentSha256": build["target"]["sha256"],
    }, indent=2))
    if not validation["pass"]:
        raise RuntimeError("Gate 09 portability contract validation failed.")


if __name__ == "__main__":
    main()
