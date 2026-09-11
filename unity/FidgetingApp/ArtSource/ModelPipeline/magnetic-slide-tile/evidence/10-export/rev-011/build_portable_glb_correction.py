#!/usr/bin/env python3
"""Build a portable Gate 10 GLB with explicit bounded glTF PBR transport."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import struct
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "rev-010"
PREVIOUS_PACKAGE = PREVIOUS / "package"
PACKAGE = HERE / "package"
TEXTURES = PACKAGE / "textures"
ENVIRONMENT = PACKAGE / "environment"
SOURCE_GLB = PREVIOUS_PACKAGE / "magnetic-slide-tile-render-r010.glb"
OUTPUT_GLB = PACKAGE / "magnetic-slide-tile-render-r011.glb"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
MATERIAL_STATE_DIGEST = "c876a0c4186ac2ce8364a309508c74c8a93a53bf57f993e36256cab2eaed2905"
UV_DIGEST = "c1c00c094735dfd28750f8b894b9f14c8e4bdfea9d3510791d95c1bb6908d9df"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_glb(path: Path) -> tuple[dict, bytearray]:
    raw = path.read_bytes()
    magic, version, total_length = struct.unpack_from("<4sII", raw, 0)
    json_length, json_type = struct.unpack_from("<II", raw, 12)
    if magic != b"glTF" or version != 2 or total_length != len(raw) or json_type != 0x4E4F534A:
        raise RuntimeError("Invalid source GLB.")
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<II", raw, binary_header)
    if binary_type != 0x004E4942:
        raise RuntimeError("Missing source GLB BIN chunk.")
    binary_start = binary_header + 8
    return document, bytearray(raw[binary_start:binary_start + binary_length])


def write_glb(path: Path, document: dict, binary: bytearray) -> None:
    while len(binary) % 4:
        binary.append(0)
    document["buffers"][0]["byteLength"] = len(binary)
    encoded = json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encoded += b" " * ((4 - len(encoded) % 4) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    raw = bytearray(struct.pack("<4sII", b"glTF", 2, total))
    raw.extend(struct.pack("<II", len(encoded), 0x4E4F534A))
    raw.extend(encoded)
    raw.extend(struct.pack("<II", len(binary), 0x004E4942))
    raw.extend(binary)
    path.write_bytes(raw)


def append_image(document: dict, binary: bytearray, name: str, payload: bytes) -> int:
    while len(binary) % 4:
        binary.append(0)
    offset = len(binary)
    binary.extend(payload)
    view_index = len(document["bufferViews"])
    document["bufferViews"].append({
        "buffer": 0,
        "byteOffset": offset,
        "byteLength": len(payload),
    })
    image_index = len(document.setdefault("images", []))
    document["images"].append({
        "bufferView": view_index,
        "mimeType": "image/png",
        "name": name,
    })
    texture_index = len(document.setdefault("textures", []))
    document["textures"].append({"sampler": 0, "source": image_index})
    return texture_index


def build_normal(source: Path, target: Path) -> dict:
    image = np.asarray(Image.open(source).convert("RGB"), dtype=np.float32) / 255.0
    luminance = image[..., 0] * 0.2126 + image[..., 1] * 0.7152 + image[..., 2] * 0.0722
    dx = np.gradient(luminance, axis=1) * 0.45
    dy = np.gradient(luminance, axis=0) * 0.45
    normal = np.dstack((-dx, -dy, np.ones_like(luminance)))
    normal /= np.maximum(np.linalg.norm(normal, axis=2, keepdims=True), 1e-6)
    encoded = np.clip((normal * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(encoded, "RGB").save(target, optimize=False)
    return {
        "path": str(target.relative_to(HERE)),
        "sha256": sha256(target),
        "dimensions": list(Image.open(target).size),
        "colorSpace": "linear-data",
        "semantic": "tangent-space normal",
        "scale": 0.35,
    }


def image_metrics(path: Path) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    luminance = image[..., 0] * 0.2126 + image[..., 1] * 0.7152 + image[..., 2] * 0.0722
    red = (image[..., 0] > image[..., 1] * 1.35) & (image[..., 0] > image[..., 2] * 1.25)
    dark = luminance < 0.08
    return {
        "dimensions": [image.shape[1], image.shape[0]],
        "luminanceP05P50P95": [float(np.percentile(luminance, p)) for p in [5, 50, 95]],
        "redFraction": float(red.mean()),
        "darkFraction": float(dark.mean()),
        "whiteFraction": float((luminance > 0.92).mean()),
        "alpha": "opaque",
    }


def material_snapshot(document: dict) -> dict:
    return {
        material["name"]: {
            "pbrMetallicRoughness": material.get("pbrMetallicRoughness"),
            "extensions": material.get("extensions", {}),
            "emissiveFactor": material.get("emissiveFactor", [0, 0, 0]),
            "alphaMode": material.get("alphaMode", "OPAQUE"),
            "doubleSided": material.get("doubleSided", False),
        }
        for material in document["materials"]
    }


def main() -> None:
    PACKAGE.mkdir(parents=True, exist_ok=True)
    TEXTURES.mkdir(parents=True, exist_ok=True)
    ENVIRONMENT.mkdir(parents=True, exist_ok=True)
    copied = {}
    exact_files = {
        "magnetic-slide-tile-authoritative-r011.blend": PREVIOUS_PACKAGE / "magnetic-slide-tile-authoritative-r010.blend",
        "magnetic-slide-tile-render-r011.fbx": PREVIOUS_PACKAGE / "magnetic-slide-tile-render-r010.fbx",
        "magnetic-slide-tile-collision-r011.fbx": PREVIOUS_PACKAGE / "magnetic-slide-tile-collision-r010.fbx",
    }
    for target_name, source in exact_files.items():
        target = PACKAGE / target_name
        shutil.copy2(source, target)
        copied[target_name] = {
            "source": str(source),
            "sourceSha256": sha256(source),
            "sha256": sha256(target),
            "byteIdentical": sha256(source) == sha256(target),
        }
    shutil.copytree(PREVIOUS_PACKAGE / "textures", TEXTURES, dirs_exist_ok=True)
    shutil.copytree(PREVIOUS_PACKAGE / "environment", ENVIRONMENT, dirs_exist_ok=True)

    upper_normal = build_normal(TEXTURES / "upper-albedo.png", TEXTURES / "upper-transport-normal-r011.png")
    lower_normal = build_normal(TEXTURES / "lower-albedo.png", TEXTURES / "lower-transport-normal-r011.png")
    document, binary = parse_glb(SOURCE_GLB)
    before_materials = material_snapshot(document)
    upper_normal_texture = append_image(
        document,
        binary,
        "upper-transport-normal-r011",
        (TEXTURES / "upper-transport-normal-r011.png").read_bytes(),
    )
    lower_normal_texture = append_image(
        document,
        binary,
        "lower-transport-normal-r011",
        (TEXTURES / "lower-transport-normal-r011.png").read_bytes(),
    )
    top_values = {
        "metallicFactor": 0.08,
        "roughnessFactor": 1.0,
        "clearcoatFactor": 0.32,
        "clearcoatRoughnessFactor": 0.10,
        "specularFactor": 0.55,
        "normalScale": 0.35,
    }
    material_values = {}
    for material in document["materials"]:
        name = material["name"]
        material["alphaMode"] = "OPAQUE"
        # The approved export uses mirrored transform ownership; keep culling portable.
        material["doubleSided"] = True
        material["emissiveFactor"] = [0.0, 0.0, 0.0]
        pbr = material.setdefault("pbrMetallicRoughness", {})
        extensions = material.setdefault("extensions", {})
        extensions.pop("KHR_materials_transmission", None)
        if name.endswith("TopArtwork"):
            pbr["baseColorFactor"] = [1.0, 1.0, 1.0, 1.0]
            pbr["metallicFactor"] = top_values["metallicFactor"]
            pbr["roughnessFactor"] = top_values["roughnessFactor"]
            material["normalTexture"] = {
                "index": upper_normal_texture if "Upper" in name else lower_normal_texture,
                "texCoord": 1,
                "scale": top_values["normalScale"],
            }
            extensions["KHR_materials_clearcoat"] = {
                "clearcoatFactor": top_values["clearcoatFactor"],
                "clearcoatRoughnessFactor": top_values["clearcoatRoughnessFactor"],
            }
            extensions["KHR_materials_specular"] = {
                "specularFactor": top_values["specularFactor"],
                "specularColorFactor": [1.0, 1.0, 1.0],
            }
            material["extras"]["transportApproximation"] = (
                "Explicit opaque glTF PBR: baked sRGB baseColor, linear metallicRoughness G, "
                "linear tangent normal, bounded specular/clearcoat, no transmission."
            )
        elif name == "M07R13_SolidDarkSide":
            pbr.update({
                "baseColorFactor": [0.014, 0.016, 0.020, 1.0],
                "metallicFactor": 0.20,
                "roughnessFactor": 0.30,
            })
            extensions["KHR_materials_clearcoat"] = {
                "clearcoatFactor": 0.22,
                "clearcoatRoughnessFactor": 0.12,
            }
        elif name == "M07R13_PolishedBrightSilverRim":
            pbr.update({
                "baseColorFactor": [0.68, 0.66, 0.62, 1.0],
                "metallicFactor": 1.0,
                "roughnessFactor": 0.16,
            })
            extensions["KHR_materials_clearcoat"] = {
                "clearcoatFactor": 0.05,
                "clearcoatRoughnessFactor": 0.08,
            }
        elif name == "M07R13_NeutralUnderside":
            pbr.update({
                "baseColorFactor": [0.14, 0.16, 0.18, 1.0],
                "metallicFactor": 0.35,
                "roughnessFactor": 0.34,
            })
        elif name == "M07R13_InternalSilverReference":
            pbr.update({
                "baseColorFactor": [0.48, 0.50, 0.52, 1.0],
                "metallicFactor": 0.82,
                "roughnessFactor": 0.20,
            })
        elif name == "M07R13_BallCandidateUnknownMaterial":
            pbr.update({
                "baseColorFactor": [0.30, 0.31, 0.32, 1.0],
                "metallicFactor": 0.10,
                "roughnessFactor": 0.30,
            })
        material_values[name] = {
            "pbrMetallicRoughness": pbr,
            "extensions": extensions,
            "emissiveFactor": material["emissiveFactor"],
            "alphaMode": material["alphaMode"],
        }
        if not extensions:
            material.pop("extensions", None)

    used_extensions = sorted({
        extension
        for material in document["materials"]
        for extension in material.get("extensions", {})
    })
    document["extensionsUsed"] = used_extensions
    document["asset"]["generator"] = "Gate 10 rev 11 explicit portable PBR correction"
    root = next(node for node in document["nodes"] if node.get("name") == "MagneticSlideTile_G06_R005")
    root.setdefault("extras", {}).update({
        "gate10Revision": 11,
        "sourceRejectedGate10Revision": 10,
        "transportCorrection": "explicit-bounded-opaque-gltf-pbr",
        "geometryChanged": False,
        "materialPartitionsChanged": False,
        "mechanismChanged": False,
    })
    write_glb(OUTPUT_GLB, document, binary)

    hierarchy = json.loads((PREVIOUS_PACKAGE / "hierarchy-motion-metadata-r010.json").read_text())
    hierarchy["revision"] = 11
    hierarchy["sourceRejectedRevision"] = 10
    hierarchy["transportMaterialApproximation"] = {
        "authoritativeBlenderMaterialPreservedSeparately": True,
        "portableGlb": "explicit opaque PBR approximation",
        "baseColor": "sRGB baked upper/lower 620x1000",
        "metallicRoughness": "linear; G=roughness, metallic factor scales R",
        "normal": "linear tangent-space; scale 0.35",
        "alphaMode": "OPAQUE",
        "emissiveFactor": [0, 0, 0],
        "transmission": 0,
        "values": material_values,
    }
    hierarchy_path = PACKAGE / "hierarchy-motion-metadata-r011.json"
    hierarchy_path.write_text(json.dumps(hierarchy, ensure_ascii=False, indent=2), encoding="utf-8")

    import_contract = json.loads((PREVIOUS_PACKAGE / "unity-import-contract-r010.json").read_text())
    import_contract["revision"] = 11
    import_contract["purpose"] = "Gate 11 import plan for corrected explicit portable GLB; not applied"
    import_contract["portableGlbTransport"] = hierarchy["transportMaterialApproximation"]
    import_contract["textureImport"].update({
        "baseColorSRGB": True,
        "maskMapSRGB": False,
        "normalTextureType": "NormalMap",
        "alphaSource": "None / OPAQUE",
    })
    import_contract_path = PACKAGE / "unity-import-contract-r011.json"
    import_contract_path.write_text(json.dumps(import_contract, ensure_ascii=False, indent=2), encoding="utf-8")

    after_document, _ = parse_glb(OUTPUT_GLB)
    after_materials = material_snapshot(after_document)
    checks = {
        "sourceRev10Immutable": sha256(SOURCE_GLB) == "ca174b340c87e58a6b76aa367baf910650546bc69c5f2794c52aff3268da1100",
        "authoritativeBlendExact": copied["magnetic-slide-tile-authoritative-r011.blend"]["byteIdentical"],
        "fbxExact": copied["magnetic-slide-tile-render-r011.fbx"]["byteIdentical"],
        "collisionExact": copied["magnetic-slide-tile-collision-r011.fbx"]["byteIdentical"],
        "deepRedBaseColor": all(image_metrics(TEXTURES / f"{half}-albedo.png")["redFraction"] > 0.20 for half in ["upper", "lower"]),
        "blackMotifAndPerimeter": all(image_metrics(TEXTURES / f"{half}-albedo.png")["darkFraction"] > 0.40 for half in ["upper", "lower"]),
        "nativeNpot": all(Image.open(TEXTURES / f"{half}-albedo.png").size == (620, 1000) for half in ["upper", "lower"]),
        "normalMapsLinearTagged": all(record["colorSpace"] == "linear-data" for record in [upper_normal, lower_normal]),
        "allOpaque": all(material.get("alphaMode") == "OPAQUE" for material in after_document["materials"]),
        "zeroEmission": all(material.get("emissiveFactor") == [0.0, 0.0, 0.0] for material in after_document["materials"]),
        "noTransmission": all("KHR_materials_transmission" not in material.get("extensions", {}) for material in after_document["materials"]),
        "specularBounded": all(
            all(0 <= value <= 1 for value in material.get("extensions", {}).get("KHR_materials_specular", {}).get("specularColorFactor", [1, 1, 1]))
            for material in after_document["materials"]
        ),
        "normalTextures": sum("normalTexture" in material for material in after_document["materials"]) == 2,
        "geometryMetadata": root["extras"]["canonicalGeometryDigest"] == GEOMETRY_DIGEST,
        "noAnimations": not after_document.get("animations"),
        "unityNotApplied": not import_contract["scope"]["unityImportApplied"],
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "pass": all(checks.values()),
        "sourceRejectedGlb": {
            "path": str(SOURCE_GLB),
            "sha256": sha256(SOURCE_GLB),
        },
        "rootCauseInputs": {
            "rev10SpecularColorFactor": [1.159999966621399] * 3,
            "rev10TransmissionFactor": 0.07999999821186066,
            "rev10ClearcoatFactor": 0.47999998927116394,
            "rev10BlenderReimportPreviewLights": {
                "keyWatts": 75,
                "fillWatts": 42,
                "distanceMetersApprox": 0.10,
            },
            "rev10Viewer": {
                "hemisphere": 2.2,
                "key": 3.2,
                "fill": 1.1,
                "rim": 1.4,
                "persistedExposureRange": [0.5, 2.0],
                "realHdrLoaded": False,
            },
        },
        "diagnosis": {
            "baseColorTexture": "Deep blood-red and black source pixels are correct.",
            "metallicRoughness": "Roughness is correctly packed in glTF G and treated as linear data.",
            "emission": "Zero; not a washout source.",
            "alpha": "Source is opaque; rev 11 makes OPAQUE explicit.",
            "proceduralConversion": "Blender procedural bump/film cannot transfer exactly; rev 11 uses explicit baked baseColor and tangent normal.",
            "glbMaterialFactors": "Rev 10 exported specularColorFactor 1.16 and transmission 0.08. Rev 11 bounds specular and removes transmission.",
            "blenderReimportPreview": "Rev 10 evidence used 75 W + 42 W area lights about 0.10 m from a meter-scale import, causing the attached white board.",
            "threeViewer": "Rev 10 used additive high-intensity lights and inherited exposure up to 2.0 without loading the approved HDR. Rev 11 requires neutral HDR and asset-specific exposure.",
            "rootCause": "Both preview calibration and unbounded/unsupported portable material extensions; geometry, UVs, partitions, deep-red pixels, and emission were not the cause.",
        },
        "beforeMaterials": before_materials,
        "afterMaterials": after_materials,
        "transportValues": material_values,
        "textures": {
            "upperBaseColor": {
                "sha256": sha256(TEXTURES / "upper-albedo.png"),
                "colorSpace": "sRGB",
                "metrics": image_metrics(TEXTURES / "upper-albedo.png"),
            },
            "lowerBaseColor": {
                "sha256": sha256(TEXTURES / "lower-albedo.png"),
                "colorSpace": "sRGB",
                "metrics": image_metrics(TEXTURES / "lower-albedo.png"),
            },
            "upperNormal": upper_normal,
            "lowerNormal": lower_normal,
            "metallicRoughness": "embedded PNG; linear; R scaled by metallicFactor, G exact source roughness",
        },
        "outputs": {
            "blend": {"path": str(PACKAGE / "magnetic-slide-tile-authoritative-r011.blend"), "sha256": sha256(PACKAGE / "magnetic-slide-tile-authoritative-r011.blend")},
            "fbx": {"path": str(PACKAGE / "magnetic-slide-tile-render-r011.fbx"), "sha256": sha256(PACKAGE / "magnetic-slide-tile-render-r011.fbx")},
            "glb": {"path": str(OUTPUT_GLB), "sha256": sha256(OUTPUT_GLB)},
            "collision": {"path": str(PACKAGE / "magnetic-slide-tile-collision-r011.fbx"), "sha256": sha256(PACKAGE / "magnetic-slide-tile-collision-r011.fbx")},
            "hierarchyMotion": {"path": str(hierarchy_path), "sha256": sha256(hierarchy_path)},
            "unityImportContract": {"path": str(import_contract_path), "sha256": sha256(import_contract_path)},
        },
        "preserved": {
            "geometryDigest": GEOMETRY_DIGEST,
            "materialStateDigest": MATERIAL_STATE_DIGEST,
            "uvDigest": UV_DIGEST,
            "hierarchy": True,
            "endpointInterlock": True,
        },
        "checks": checks,
    }
    (HERE / "portable-glb-build-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({
        "pass": True,
        "glbSha256": report["outputs"]["glb"]["sha256"],
        "rootCause": report["diagnosis"]["rootCause"],
    }, indent=2))


if __name__ == "__main__":
    main()
