#!/usr/bin/env python3
"""Assemble the hash-locked Gate 10 Unity export manifest."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
MODEL = HERE.parent.parent.parent
PACKAGE = HERE / "package"
GATE09 = MODEL / "evidence/09-environment/rev-008"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).relative_to(REPO).as_posix()


def main():
    build = json.loads((HERE / "export-build-report.json").read_text())
    reimport = json.loads((HERE / "reimport-validation.json").read_text())
    textures = json.loads((HERE / "texture-export-manifest.json").read_text())
    prior = json.loads((GATE09 / "unity-portability-contract.json").read_text())
    contract_copy = PACKAGE / "unity-portability-contract-gate09-r008.json"
    shutil.copyfile(GATE09 / "unity-portability-contract.json", contract_copy)
    hierarchy_path = PACKAGE / "hierarchy-motion-metadata-r009.json"
    hierarchy = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 9,
        "contractSha256": build["contractSha256"],
        "geometryDigest": build["approved"]["geometryDigest"],
        "uvDigest": prior["geometry"]["uvDigest"],
        "closedBoundsMm": prior["geometry"]["closedBoundsMm"],
        "measurementState": prior["geometry"]["measurementState"],
        "flatBottomExteriorTopZMm": prior["geometry"]["flatBottomExteriorTopZMm"],
        "fixedAxisBossProtrusionMm": prior["geometry"]["fixedAxisBossProtrusionMm"],
        "hierarchy": build["before"]["hierarchy"],
        "motion": prior["motion"],
        "defaultState": {
            "pose": "closed",
            "angularVelocity": 0,
            "linearVelocity": 0,
            "animationClips": 0,
            "selfMotion": False,
        },
        "parts": {
            "fixed": ["BottomExterior", "FixedAxis", "FixedAxisBoss", "MinimumOverlapDisk"],
            "carrier": ["RotatingCarrier", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight"],
            "movingTop": ["MovingTop", "TopLocalSlide", "MovingTopBody"],
            "fourTopUndersideGrooves": ["TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"],
            "unknowns": ["UnknownSprings", "UnknownPreload"],
        },
    }
    hierarchy_path.write_text(json.dumps(hierarchy, indent=2), encoding="utf-8")
    files = []
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file():
            files.append({"path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "revision": 9,
        "status": "ready-for-review-not-unity-imported",
        "sourceApproval": {
            "gate": "09-environment",
            "revision": 8,
            "exactUserWording": "你给我看一下最终在 Unity 里边的呈现吧。",
            "sourceBlend": build["source"],
        },
        "immutablePackageFiles": files,
        "formatHashes": build["formats"],
        "geometry": {
            "canonicalDigest": build["approved"]["geometryDigest"],
            "triangulatedTransportDigest": build["before"]["triangleDigest"],
            "uvDigest": prior["geometry"]["uvDigest"],
            "closedBoundsMm": [50, 31, 12],
            "measurementState": "user-authorized-provisional; not production measured",
            "renderMeshCount": 8,
            "glbPrimitiveAttributes": ["POSITION", "NORMAL", "TANGENT", "TEXCOORD_0"],
            "renderModelPolicy": "single approved render model; no unapproved LOD/high-poly pair",
        },
        "coordinateSystem": {
            "authoringUnits": "millimeters",
            "FBX": {"units": "meters", "forward": "-Z", "up": "+Y", "scaleApplied": 0.001},
            "GLB": {"units": "meters per glTF 2.0", "rightHanded": True, "up": "+Y", "rootExportScale": 0.001},
            "UnityTarget": {"units": "meters", "coordinateConversion": "importer-owned at Gate 11; preserve named hierarchy and local transforms"},
            "pivot": prior["motion"]["coordinateMapping"],
        },
        "motion": prior["motion"],
        "textures": {
            "manifest": relative(HERE / "texture-export-manifest.json"),
            "upperLowerArtworkIndependent": True,
            "npotPolicy": textures["rules"]["npot"],
            "astcPlan": textures["rules"]["astc"],
            "colorSpaceAndFiltering": {
                "baseColor": textures["rules"]["baseColor"],
                "maskMapAndNormal": textures["rules"]["maskMapAndNormal"],
                "artworkMasks": textures["rules"]["artworkMasks"],
            },
            "channelPacking": {"upper": textures["channelPacks"]["upper"], "lower": textures["channelPacks"]["lower"]},
        },
        "materials": {
            "approvedSemanticDigest": build["approved"]["materialDigest"],
            "shaderMapping": prior["unityUrpShaderTargets"],
            "proceduralGraphTransfer": "not byte-identical; Gate 11 measures visual parity",
        },
        "environment": prior["environmentAndReflections"],
        "colorManagement": prior["colorManagement"],
        "parityTolerances": prior["acceptanceTolerances"],
        "collision": {
            "file": relative(PACKAGE / "magnetic-slide-tile-collision-r009.fbx"),
            "sha256": sha256(PACKAGE / "magnetic-slide-tile-collision-r009.fbx"),
            "rendering": False,
            "objects": ["COL_BottomExterior", "COL_MovingTop"],
            "displayRule": "Show only as labeled wireframe technical evidence; never beside render model as product shading.",
        },
        "validation": {
            "buildPassed": build["pass"],
            "independentReimportPassed": reimport["pass"],
            "fbxBoundsMeters": reimport["results"]["fbx"]["boundsMeters"],
            "glbBoundsMeters": reimport["results"]["glb"]["boundsMeters"],
            "glbCounts": reimport["results"]["glbStructure"]["counts"],
            "noAnimations": True,
            "noMeshSmoothTypeOff": True,
            "noReflectionBandEnvironment": True,
            "noStaleTwoShellCavity": True,
            "unityImportApplied": False,
            "buildInstallDevice": False,
        },
        "deferred": {
            "Gate11": ["Unity import settings", "URP materials", "reflection probe", "matched-camera parity"],
            "Gate12": ["shipping Unity scene review", "real shipping visual approval"],
            "afterGate12Approval": ["iPhone build", "install", "device acceptance"],
        },
    }
    output = HERE / "unity-export-manifest.json"
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    validation = {
        "pass": all([
            build["pass"], reimport["pass"], textures["pass"],
            sha256(contract_copy) == "fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134",
            sha256(PACKAGE / "environment/magnetic-slide-tile-shipping-studio-r008.exr") == "7f1c9fded84c453efbc5300a6a71fe2948534055d3f4ae5052696909f30be6ab",
        ]),
        "manifestSha256": sha256(output),
        "packageFileCount": len(files),
        "packageBytes": sum(item["bytes"] for item in files),
        "checks": {
            "geometryHashLocked": manifest["geometry"]["canonicalDigest"] == "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
            "materialHashLocked": manifest["materials"]["approvedSemanticDigest"] == "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8",
            "exactMasks": textures["textures"]["upperArtworkMask"]["sha256"] == "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36" and textures["textures"]["lowerArtworkMask"]["sha256"] == "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2",
            "npotPreserved": textures["rules"]["npot"]["sourceResolutionPx"] == [620, 1000] and textures["rules"]["npot"]["policy"].startswith("None"),
            "noUnityMutation": not manifest["validation"]["unityImportApplied"],
        },
    }
    validation["pass"] = validation["pass"] and all(validation["checks"].values())
    (HERE / "portability-manifest-validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    if not validation["pass"]:
        raise RuntimeError(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

