#!/usr/bin/env python3
"""Prepare hash-locked Gate 10 textures, environment, and Unity import plan."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
MODEL = HERE.parent.parent.parent
MATERIAL = MODEL / "evidence/07-material/rev-013"
ENVIRONMENT = MODEL / "evidence/09-environment/rev-009"
PACKAGE = HERE / "package"
TEXTURES = PACKAGE / "textures"
ENV_OUT = PACKAGE / "environment"
CUBE_OUT = ENV_OUT / "cubemap"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_exact(source: Path, target: Path) -> dict:
    shutil.copy2(source, target)
    if sha256(source) != sha256(target):
        raise RuntimeError(f"Byte copy mismatch: {source}")
    return {
        "path": str(target.relative_to(HERE)),
        "sha256": sha256(target),
        "bytes": target.stat().st_size,
    }


def build_maskmap(roughness_path: Path, target: Path) -> dict:
    roughness = Image.open(roughness_path).convert("L")
    width, height = roughness.size
    output = Image.new("RGBA", roughness.size, (20, 255, 0, 255))
    output.putalpha(roughness.point(lambda value: 255 - value))
    output.save(target, optimize=False)
    return {
        "path": str(target.relative_to(HERE)),
        "sha256": sha256(target),
        "dimensions": [width, height],
        "channels": {
            "R": "metallic=0.08 for top artwork transport baseline",
            "G": "occlusion=1.0",
            "B": "detailMask=0.0",
            "A": "smoothness=1-source roughness",
        },
    }


def build_flat_normal(target: Path) -> dict:
    image = Image.new("RGB", (620, 1000), (128, 128, 255))
    image.save(target, optimize=False)
    return {
        "path": str(target.relative_to(HERE)),
        "sha256": sha256(target),
        "dimensions": [620, 1000],
        "encoding": "OpenGL tangent-space flat normal; textureType NormalMap downstream",
    }


def main() -> None:
    TEXTURES.mkdir(parents=True, exist_ok=True)
    CUBE_OUT.mkdir(parents=True, exist_ok=True)
    copied = {}
    for name in [
        "upper-albedo.png",
        "lower-albedo.png",
        "upper-roughness.png",
        "lower-roughness.png",
        "upper-artwork-mask.png",
        "lower-artwork-mask.png",
        "top-perimeter-mask.png",
    ]:
        copied[name] = copy_exact(MATERIAL / name, TEXTURES / name)

    environment_files = {
        "target-shipping-studio-r009.exr": ENVIRONMENT / "target-shipping-studio-r009.exr",
        "neutral-control-r009.exr": ENVIRONMENT / "neutral-control-r009.exr",
        "target-shipping-studio-r009-preview.png": ENVIRONMENT / "target-shipping-studio-r009-preview.png",
        "unity-portability-contract-r009.json": ENVIRONMENT / "unity-portability-contract-r009.json",
        "cubemap-contract.json": ENVIRONMENT / "cubemap-r009/cubemap-contract.json",
    }
    for target_name, source in environment_files.items():
        target = CUBE_OUT / target_name if target_name == "cubemap-contract.json" else ENV_OUT / target_name
        copied[target_name] = copy_exact(source, target)
    for face in [
        "positive-x.exr",
        "negative-x.exr",
        "positive-y.exr",
        "negative-y.exr",
        "positive-z.exr",
        "negative-z.exr",
    ]:
        copied[face] = copy_exact(ENVIRONMENT / "cubemap-r009" / face, CUBE_OUT / face)

    generated = {
        "upper-maskmap.png": build_maskmap(TEXTURES / "upper-roughness.png", TEXTURES / "upper-maskmap.png"),
        "lower-maskmap.png": build_maskmap(TEXTURES / "lower-roughness.png", TEXTURES / "lower-maskmap.png"),
        "upper-normal.png": build_flat_normal(TEXTURES / "upper-normal.png"),
        "lower-normal.png": build_flat_normal(TEXTURES / "lower-normal.png"),
    }
    import_contract = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "purpose": "Unity Gate 11 import and ASTC comparison plan; not applied in this gate",
        "sourceGate09PortabilityContractSha256": copied["unity-portability-contract-r009.json"]["sha256"],
        "units": {"authoring": "millimeters", "fbxAndGlb": "meters"},
        "modelImport": {
            "preserveHierarchy": True,
            "readWrite": False,
            "importAnimation": False,
            "generateColliders": False,
            "normals": "Import",
            "tangents": "Import",
            "meshCompression": "Off for Gate 11 parity",
            "optimizeMeshPolygons": False,
            "optimizeMeshVertices": False,
            "weldVertices": False,
        },
        "textureImport": {
            "nativeDimensions": [620, 1000],
            "npotScale": "None",
            "wrapMode": "Clamp",
            "mipMaps": True,
            "baseColorSRGB": True,
            "maskMapSRGB": False,
            "normalTextureType": "NormalMap",
            "environmentSRGB": False,
        },
        "astcPlan": {
            "applied": False,
            "gate": "11-unity-parity",
            "baseColorCandidates": ["ASTC_4x4", "ASTC_6x6"],
            "maskAndNormalCandidates": ["ASTC_4x4"],
            "environment": "RGBAHalf cubemap; no ASTC before HDR parity",
            "acceptance": "Compare against uncompressed import at native NPOT dimensions before selecting compression.",
        },
        "materialPartitions": {
            "topArtwork": "upper/lower independent BaseColor + MaskMap; Clamp",
            "sideWall": "solid dark material; no image sampler and exactly zero artwork",
            "rim": "polished bright silver material; no artwork",
            "underside": "neutral technical material; no artwork",
        },
        "environment": {
            "source": copied["target-shipping-studio-r009.exr"],
            "cubemapContract": copied["cubemap-contract.json"],
            "displayMapping": "neutral-display-v1",
        },
        "scope": {
            "unityImportApplied": False,
            "unitySceneModified": False,
            "buildInstallDevice": False,
        },
    }
    contract_path = PACKAGE / "unity-import-contract-r010.json"
    contract_path.write_text(json.dumps(import_contract, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "pass": True,
        "copied": copied,
        "generated": generated,
        "checks": {
            "independentArtworkMasks": copied["upper-artwork-mask.png"]["sha256"] != copied["lower-artwork-mask.png"]["sha256"],
            "nativeNpotPreserved": all(Image.open(TEXTURES / name).size == (620, 1000) for name in copied if name.endswith(".png") and name in {
                "upper-albedo.png", "lower-albedo.png", "upper-roughness.png", "lower-roughness.png",
                "upper-artwork-mask.png", "lower-artwork-mask.png", "top-perimeter-mask.png",
            }),
            "clampSpecified": import_contract["textureImport"]["wrapMode"] == "Clamp",
            "astcNotApplied": not import_contract["astcPlan"]["applied"],
            "environmentCopiedExact": copied["target-shipping-studio-r009.exr"]["sha256"] == sha256(ENVIRONMENT / "target-shipping-studio-r009.exr"),
        },
        "unityImportContract": {
            "path": str(contract_path.relative_to(HERE)),
            "sha256": sha256(contract_path),
        },
    }
    report["pass"] = all(report["checks"].values())
    report_path = HERE / "texture-environment-validation.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({"pass": True, "contractSha256": report["unityImportContract"]["sha256"]}, indent=2))


if __name__ == "__main__":
    main()
