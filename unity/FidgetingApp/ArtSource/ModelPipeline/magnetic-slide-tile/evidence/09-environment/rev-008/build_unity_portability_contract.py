#!/usr/bin/env python3
"""Write the hash-locked Gate 09 Unity portability contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
MODEL = HERE.parent.parent.parent
GATE07 = MODEL / "evidence/07-material/rev-011"
GATE08 = MODEL / "evidence/08-lighting/rev-002"
GATE06 = MODEL / "evidence/06-geometry/rev-004"
MECHANISM = MODEL / "evidence/02-analysis/rev-016/mechanism-evidence-contract.json"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path, role, color_space=None):
    path = Path(path)
    item = {
        "path": path.relative_to(REPO).as_posix(),
        "sha256": sha256(path),
        "role": role,
    }
    if color_space:
        item["colorSpace"] = color_space
    return item


def main():
    environment = json.loads((HERE / "environment-validation.json").read_text(encoding="utf-8"))
    materials = json.loads((GATE07 / "material-validation.json").read_text(encoding="utf-8"))
    extracted = json.loads((HERE / "portable-texture-extraction.json").read_text(encoding="utf-8"))
    hdri = json.loads((HERE / "portable-hdri-metadata.json").read_text(encoding="utf-8"))
    material_values = materials["textureLineage"]["materialValues"]
    assets = {
        "mechanismContract": record(MECHANISM, "approved-mechanism-contract"),
        "gate06GeometryValidation": record(GATE06 / "geometry-validation.json", "geometry-motion-authority"),
        "gate08LightingValidation": record(GATE08 / "lighting-validation.json", "approved-light-camera-authority"),
        "gate08SourceBlend": record(GATE08 / "magnetic-slide-tile-lighting-r002.blend", "approved-source-blend"),
        "gate09Blend": record(HERE / "magnetic-slide-tile-environment-r008.blend", "environment-source-blend"),
        "gate09ReviewGlb": record(HERE / "magnetic-slide-tile-environment-r008-lookdev.glb", "interactive-review-only-not-export-approved"),
        "shippingEnvironment": record(HERE / hdri["asset"], "portable-equirectangular-environment", "scene-linear Rec.709/D65"),
        "upperAlbedo": record(HERE / extracted["textures"]["upper-albedo.png"]["path"], "upper-editable-base-color", "sRGB"),
        "upperRoughness": record(HERE / extracted["textures"]["upper-roughness.png"]["path"], "upper-roughness-source", "linear"),
        "lowerAlbedo": record(HERE / extracted["textures"]["lower-albedo.png"]["path"], "lower-editable-base-color", "sRGB"),
        "lowerRoughness": record(HERE / extracted["textures"]["lower-roughness.png"]["path"], "lower-roughness-source", "linear"),
        "upperArtworkMask": record(MODEL / "evidence/07-material/rev-007/artwork-upper-mask.png", "upper-independent-artwork-mask", "linear"),
        "lowerArtworkMask": record(MODEL / "evidence/07-material/rev-010/artwork-lower-mask-r010.png", "lower-independent-artwork-mask", "linear"),
        "perimeterMask": record(MODEL / "evidence/07-material/rev-007/artwork-top-perimeter-border-mask.png", "full-black-perimeter-mask", "linear"),
    }
    if assets["mechanismContract"]["sha256"] != environment["contractSha256"]:
        raise RuntimeError("Mechanism contract hash mismatch.")
    contract = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "modelId": "magnetic-slide-tile",
        "status": "portable-input-contract-not-unity-import-settings",
        "finalGoal": {
            "exactUserGoal": "transfer to Unity with no avoidable loss and run on iPhone",
            "iphonePerformanceAndDeviceAcceptance": "future work after Gate 12 visual approval",
        },
        "losslessDefinition": {
            "exactDeterministicPreservation": [
                "geometry vertex/index digest",
                "hierarchy and parent ownership",
                "fixed-axis pivot and local transforms",
                "UV coordinates",
                "upper/lower/perimeter artwork mask bytes",
            ],
            "measuredVisualParity": [
                "blood-red crystal response",
                "silver and black material response",
                "thin-film/iridescence approximation",
                "lighting response",
                "AgX-to-Unity tone-mapped output",
            ],
            "notPossible": "Blender procedural shader nodes cannot transfer one-to-one into Unity URP or remain byte-identical.",
            "portableDocumentedInputs": [
                "equirectangular OpenEXR",
                "PBR source textures and packing plan",
                "reflection probe and card expectations",
                "color-management calibration plan",
            ],
        },
        "assets": assets,
        "geometry": {
            "digestAlgorithm": "Gate 06 deterministic SHA-256 over ordered core object names, local vertex coordinates and polygon indices",
            "digest": environment["geometry"]["expected"],
            "closedBoundsMm": [50, 31, 12],
            "measurementState": "user-authorized-provisional; not a production measurement",
            "flatBottomExteriorTopZMm": 5.875,
            "fixedAxisBossProtrusionMm": 0.2,
            "uvDigest": environment["uv"]["after"],
            "hierarchy": environment["hierarchy"]["after"],
            "blenderFixedAxisObjectMatrix": environment["hierarchy"]["after"]["FixedAxis"]["matrixWorld"],
            "requiredNamedRoots": {
                "fixed": ["BottomExterior", "FixedAxis", "FixedAxisBoss", "MinimumOverlapDisk"],
                "carrier": ["RotatingCarrier", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight"],
                "top": ["MovingTop", "TopLocalSlide", "MovingTopBody", "TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"],
            },
        },
        "motion": {
            "axisPointWorldMm": [0, -9.5, 0],
            "axisDirection": "+Z",
            "coordinateMapping": {
                "mechanismContractSpace": "2D interaction plane with Z=0",
                "blenderFixedAxisObjectOriginMm": [0, -9, 5.074999809],
                "rule": "Gate 10 must preserve the Blender object matrix exactly and retain the mechanism-space axis metadata; do not silently equate the two coordinate spaces.",
            },
            "fixedObjects": ["BottomExterior", "FixedAxis", "FixedAxisBoss", "MinimumOverlapDisk"],
            "carrierTransform": "R_fixedAxis(theta)",
            "topTransform": "R_fixedAxis(theta) * T_local(slide)",
            "detentStepDegrees": 12,
            "detentCount": 30,
            "reviewAnglesDegrees": [0, 12, 36],
            "maximumTravelMm": environment["motionContainment"]["maxTravelMm"],
            "minimumOverlapContainment": {
                "source": assets["gate06GeometryValidation"],
                "denseSweepSamples": environment["motionContainment"]["denseSweepSamples"],
                "angularStepDegrees": environment["motionContainment"]["angularStepDegrees"],
                "allValid": True,
            },
            "selfMotion": "forbidden; angular velocity starts and resets at zero",
        },
        "artworkAndTextures": {
            "upperAndLowerIndependentlyReplaceable": True,
            "upperMask": assets["upperArtworkMask"],
            "lowerMask": assets["lowerArtworkMask"],
            "perimeterMask": assets["perimeterMask"],
            "rules": {
                "baseColor": {"sRGB": True, "filter": "trilinear", "wrap": "clamp", "mipmaps": True},
                "roughnessMaskAO": {"sRGB": False, "filter": "trilinear", "wrap": "clamp", "mipmaps": True},
                "artworkMasks": {"sRGB": False, "filter": "bilinear", "wrap": "clamp", "mipmaps": True, "alphaIsTransparency": False},
                "normal": {"textureType": "normal-map", "sRGB": False, "filter": "trilinear", "wrap": "clamp", "mipmaps": True},
                "compressionDecision": "Gate 10 must compare lossless source against iPhone ASTC candidates; no compression is authorized at Gate 09.",
            },
        },
        "pbrBakeAndPackingPlan": {
            "preserveSourceFiles": ["upperAlbedo", "lowerAlbedo", "upperRoughness", "lowerRoughness", "upperArtworkMask", "lowerArtworkMask", "perimeterMask"],
            "perArtworkLayer": {
                "BaseMap": "RGBA sRGB; approved albedo in RGB; alpha reserved and must not merge upper/lower masks",
                "MaskMap": "RGBA linear: R metallic, G ambient occlusion, B crystal/detail mask, A smoothness=1-roughness",
                "NormalMap": "tangent-space linear normal; bake crystal mosaic/microflake normal response at Gate 10",
                "ArtworkMask": "separate single-channel linear asset; upper and lower remain independent",
            },
            "bakeRequirements": {
                "minimumResolutionPx": [1024, 1024],
                "supersampling": "4x before downsample",
                "paddingPxAtFinalResolution": 16,
                "tangentBasis": "MikkTSpace",
                "ambientOcclusion": "model-only neutral AO; environment excluded",
                "proceduralSource": "approved Gate 07 rev 11 Blender nodes",
                "hashManifest": "Gate 10 records every source and baked output SHA-256",
            },
        },
        "unityUrpShaderTargets": {
            "silver": material_values["silver"],
            "bloodRedCrystal": {
                **material_values["crystal"],
                "implementation": "URP Lit-compatible custom shader; baked crystal detail plus view-dependent Fresnel/thin-film approximation",
                "fresnelF0FromIor": round(((material_values["crystal"]["ior"] - 1) / (material_values["crystal"]["ior"] + 1)) ** 2, 8),
            },
            "blackMotif": material_values["motif"],
            "blackPerimeterAndSide": material_values["perimeter"],
            "iridescenceApproximation": {
                "thinFilmIor": material_values["crystal"]["thinFilmIor"],
                "thicknessNm": material_values["crystal"]["thinFilmThicknessNm"],
                "mix": material_values["crystal"]["iridescenceMix"],
                "viewTerm": "Schlick Fresnel using crystal IOR 1.52",
                "lookup": "bake a 1D spectral-response LUT at Gate 10; do not claim graph identity",
            },
            "emission": 0,
        },
        "environmentAndReflections": {
            "environment": {
                **hdri,
                "worldStrength": 0.65,
                "rotationDegrees": 0,
            },
            "background": "same EXR, directly visible; no Blender-only procedural world nodes",
            "ground": environment["environment"]["targetShipping"]["ground"],
            "approvedLightsDigest": environment["lighting"]["after"],
            "approvedSourceCamerasDigest": environment["cameras"]["after"],
            "reflectionCards": {
                "source": "approved Gate 08 rev 2 light rig",
                "count": 4,
                "rule": "preserve card transforms and visibility roles; cards may affect reflections but stay hidden from product camera",
            },
            "unityProbeExpectation": {
                "type": "local box-projected Reflection Probe",
                "centerWorldMm": [0, -3, 12],
                "sizeMm": [140, 140, 90],
                "blendDistanceMm": 20,
                "hdr": True,
                "resolutionCandidatePx": 512,
                "refresh": "baked",
                "sourceCubemap": "derive from the hash-locked equirectangular EXR",
                "probePriority": 1,
                "performanceAcceptance": "benchmark resolution and ASTC/HDR format on iPhone only after Gate 12 approval",
            },
        },
        "colorManagement": {
            "blenderReference": {
                "viewTransform": "AgX",
                "look": "AgX - Medium High Contrast",
                "exposureEv": -0.35,
                "gamma": 1,
                "whitePoint": "D65",
            },
            "unityStartingPoint": {
                "renderPipeline": "URP linear HDR",
                "toneMapper": "ACES",
                "whiteBalanceKelvin": 6504,
                "whiteBalanceTint": 10,
                "postExposureEv": 0,
            },
            "mappingPlan": [
                "Gate 11 captures matched-camera linear EXR before tone mapping in Blender and Unity.",
                "Gate 11 captures the same 24 color patches, silver highlight, blood-red crystal and black motif under the hash-locked environment.",
                "Use Unity ACES directly when DeltaE and clipping tolerances pass.",
                "Only if ACES fails, fit and hash a 32x32x32 .cube LUT against Blender AgX reference, then re-run every parity metric.",
            ],
            "claim": "AgX and Unity ACES/Neutral are not identical transforms; acceptance is measured parity.",
        },
        "acceptanceTolerances": {
            "closedBoundsMaxAbsoluteErrorMm": 0.001,
            "vertexIndexDigest": "exact SHA-256 match",
            "hierarchyParentAndNames": "exact match",
            "pivotAxisPointMaxAbsoluteErrorMm": 0.001,
            "uvMaxAbsoluteCoordinateError": 1e-6,
            "artworkMaskBytes": "exact SHA-256 match",
            "silhouette": {"minimumSSIM": 0.995, "maximumEdgeDistancePxAt1400x1100": 1},
            "colorDeltaE2000Median": {"silver": 3, "bloodRed": 4, "black": 2.5},
            "colorDeltaE2000P95Maximum": 6,
            "reflectionContinuity": {
                "hdriSeamMaxAbsoluteLinearDelta": 1e-6,
                "highlightCentroidMaxErrorPxAt1400x1100": 2,
                "highlightMeanLuminanceRelativeError": 0.05,
            },
            "clipping": {"maximumPixelFraction": 0.001, "maximumAbsoluteDifferenceFromBlender": 0.0005},
            "emission": 0,
            "containment": "all 3600 dense-sweep samples valid",
        },
        "deferred": {
            "unityImportSettingsApplied": False,
            "unitySceneChanged": False,
            "shippingModelChanged": False,
            "build": False,
            "install": False,
            "iphoneRun": False,
            "iphonePerformanceAndAcceptance": "after Gate 12 visual approval",
        },
    }
    output = HERE / "unity-portability-contract.json"
    output.write_text(json.dumps(contract, indent=2), encoding="utf-8")
    verification = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "pass": True,
        "contractPath": output.relative_to(REPO).as_posix(),
        "contractSha256": sha256(output),
        "assetCount": len(assets),
        "allAssetHashesVerified": all(sha256(REPO / item["path"]) == item["sha256"] for item in assets.values()),
        "exactGeometryDigest": contract["geometry"]["digest"] == environment["geometry"]["expected"],
        "exactUvDigestRecorded": bool(contract["geometry"]["uvDigest"]),
        "independentArtworkMasks": contract["artworkAndTextures"]["upperMask"]["sha256"] != contract["artworkAndTextures"]["lowerMask"]["sha256"],
        "portableHdriSeam": hdri["seamMaxAbsoluteLinearDelta"] <= 1e-6,
        "portableHdriDynamicRange": hdri["dynamicRangeStopsP01ToP99"] >= 4,
        "measuredNotGraphIdentical": "cannot transfer one-to-one" in contract["losslessDefinition"]["notPossible"],
        "noUnityImportSettings": contract["deferred"]["unityImportSettingsApplied"] is False,
        "iphoneDeferred": contract["deferred"]["iphoneRun"] is False,
    }
    verification["pass"] = all(value for key, value in verification.items() if isinstance(value, bool))
    (HERE / "portability-validation.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    if not verification["pass"]:
        raise RuntimeError(json.dumps(verification, indent=2))
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()

