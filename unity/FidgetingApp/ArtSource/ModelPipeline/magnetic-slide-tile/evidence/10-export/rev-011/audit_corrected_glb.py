#!/usr/bin/env python3
"""Audit corrected GLB JSON, embedded images, accessors, hierarchy, and PBR."""

from __future__ import annotations

import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
REJECTED = HERE.parent / "rev-010" / "package" / "magnetic-slide-tile-render-r010.glb"
CORRECTED = PACKAGE / "magnetic-slide-tile-render-r011.glb"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    json_length = struct.unpack_from("<I", raw, 12)[0]
    document = json.loads(raw[20:20 + json_length].decode().rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length = struct.unpack_from("<I", raw, binary_header)[0]
    return document, raw[binary_header + 8:binary_header + 8 + binary_length]


def accessor_payload(document: dict, binary: bytes, index: int) -> bytes:
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    component_size = {
        5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4,
    }[accessor["componentType"]]
    component_count = {
        "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16,
    }[accessor["type"]]
    item_size = component_size * component_count
    stride = view.get("byteStride", item_size)
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    if stride == item_size:
        return binary[start:start + accessor["count"] * item_size]
    return b"".join(
        binary[start + item * stride:start + item * stride + item_size]
        for item in range(accessor["count"])
    )


def mesh_payloads(document: dict, binary: bytes) -> dict:
    records = {}
    for mesh in document["meshes"]:
        for primitive_index, primitive in enumerate(mesh["primitives"]):
            attributes = dict(primitive["attributes"])
            attributes["INDICES"] = primitive["indices"]
            records[f"{mesh.get('name')}:{primitive_index}"] = {
                semantic: sha256_bytes(accessor_payload(document, binary, accessor_index))
                for semantic, accessor_index in sorted(attributes.items())
            }
    return records


def embedded_images(document: dict, binary: bytes) -> dict:
    records = {}
    for image in document.get("images", []):
        view = document["bufferViews"][image["bufferView"]]
        start = view.get("byteOffset", 0)
        payload = binary[start:start + view["byteLength"]]
        decoded = Image.open(io.BytesIO(payload))
        records[image["name"]] = {
            "sha256": sha256_bytes(payload),
            "dimensions": list(decoded.size),
            "mode": decoded.mode,
            "allAlphaOpaque": decoded.convert("RGBA").getchannel("A").getextrema() == (255, 255),
        }
    return records


def main() -> None:
    old_document, old_binary = parse(REJECTED)
    document, binary = parse(CORRECTED)
    material_by_name = {material["name"]: material for material in document["materials"]}
    old_payloads = mesh_payloads(old_document, old_binary)
    payloads = mesh_payloads(document, binary)
    images = embedded_images(document, binary)
    top_names = {"M07R13_UpperTopArtwork", "M07R13_LowerTopArtwork"}
    top_materials = [material_by_name[name] for name in top_names]
    side = material_by_name["M07R13_SolidDarkSide"]
    rim = material_by_name["M07R13_PolishedBrightSilverRim"]
    meshes = {mesh.get("name"): mesh for mesh in document["meshes"]}
    moving_material_names = {
        document["materials"][primitive["material"]]["name"]
        for primitive in meshes["MovingTopBody_Mesh"]["primitives"]
    }
    bottom_material_names = {
        document["materials"][primitive["material"]]["name"]
        for primitive in meshes["BottomExterior_Mesh"]["primitives"]
    }
    node_names = [node.get("name", "") for node in document["nodes"]]
    root = next(node for node in document["nodes"] if node.get("name") == "MagneticSlideTile_G06_R005")
    material_dump = {
        material["name"]: {
            "pbrMetallicRoughness": material.get("pbrMetallicRoughness", {}),
            "extensions": material.get("extensions", {}),
            "normalTexture": material.get("normalTexture"),
            "emissiveFactor": material.get("emissiveFactor"),
            "alphaMode": material.get("alphaMode"),
        }
        for material in document["materials"]
    }
    (HERE / "raw-glb-materials-r011.json").write_text(
        json.dumps(material_dump, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    checks = {
        "geometryAccessorBytesUnchanged": payloads == old_payloads,
        "meshMaterialAssignmentsUnchanged": [
            [primitive.get("material") for primitive in mesh["primitives"]]
            for mesh in document["meshes"]
        ] == [
            [primitive.get("material") for primitive in mesh["primitives"]]
            for mesh in old_document["meshes"]
        ],
        "hierarchyUnchanged": [
            (node.get("name"), node.get("children"), node.get("mesh"), node.get("translation"), node.get("rotation"), node.get("scale"))
            for node in document["nodes"]
        ] == [
            (node.get("name"), node.get("children"), node.get("mesh"), node.get("translation"), node.get("rotation"), node.get("scale"))
            for node in old_document["nodes"]
        ],
        "geometryDigest": root["extras"]["canonicalGeometryDigest"] == GEOMETRY_DIGEST,
        "exactOneFixedAxis": node_names.count("FixedAxis") == 1,
        "fourTopGrooves": len([name for name in node_names if name.startswith("Top") and "Groove" in name]) == 4,
        "minimumOverlapNotMesh": "MinimumOverlapDisk" in node_names
            and next(node for node in document["nodes"] if node.get("name") == "MinimumOverlapDisk").get("mesh") is None,
        "noAnimations": not document.get("animations"),
        "topPartitions": moving_material_names == {
            "M07R13_UpperTopArtwork",
            "M07R13_SolidDarkSide",
            "M07R13_PolishedBrightSilverRim",
            "M07R13_NeutralUnderside",
        } and bottom_material_names == {
            "M07R13_LowerTopArtwork",
            "M07R13_SolidDarkSide",
            "M07R13_PolishedBrightSilverRim",
            "M07R13_NeutralUnderside",
        },
        "sideArtworkCoverageZero": "baseColorTexture" not in side["pbrMetallicRoughness"]
            and "metallicRoughnessTexture" not in side["pbrMetallicRoughness"]
            and side["extras"]["artworkSampling"] is False,
        "topArtworkPresent": all("baseColorTexture" in material["pbrMetallicRoughness"] for material in top_materials),
        "independentTopTextures": len({
            material["pbrMetallicRoughness"]["baseColorTexture"]["index"]
            for material in top_materials
        }) == 2,
        "topUsesCapUv": all(
            material["pbrMetallicRoughness"]["baseColorTexture"]["texCoord"] == 1
            and material["pbrMetallicRoughness"]["metallicRoughnessTexture"]["texCoord"] == 1
            and material["normalTexture"]["texCoord"] == 1
            for material in top_materials
        ),
        "nativeNpot": all(record["dimensions"] == [620, 1000] for record in images.values()),
        "opaqueImages": all(record["allAlphaOpaque"] for record in images.values()),
        "clampSampler": all(
            sampler.get("wrapS") == 33071 and sampler.get("wrapT") == 33071
            for sampler in document["samplers"]
        ),
        "explicitOpaque": all(material.get("alphaMode") == "OPAQUE" for material in document["materials"]),
        "zeroEmission": all(material.get("emissiveFactor") == [0.0, 0.0, 0.0] for material in document["materials"]),
        "noTransmission": all(
            "KHR_materials_transmission" not in material.get("extensions", {})
            for material in document["materials"]
        ),
        "boundedSpecular": all(
            all(0 <= value <= 1 for value in material.get("extensions", {}).get("KHR_materials_specular", {}).get("specularColorFactor", [1, 1, 1]))
            and 0 <= material.get("extensions", {}).get("KHR_materials_specular", {}).get("specularFactor", 1) <= 1
            for material in document["materials"]
        ),
        "deepRedPbr": all(
            material["pbrMetallicRoughness"]["baseColorFactor"] == [1.0, 1.0, 1.0, 1.0]
            and material["pbrMetallicRoughness"]["metallicFactor"] == 0.08
            and material["extensions"]["KHR_materials_specular"]["specularFactor"] == 0.55
            for material in top_materials
        ),
        "darkSidePbr": side["pbrMetallicRoughness"] == {
            "baseColorFactor": [0.014, 0.016, 0.02, 1.0],
            "metallicFactor": 0.2,
            "roughnessFactor": 0.3,
        },
        "silverRimPbr": rim["pbrMetallicRoughness"] == {
            "baseColorFactor": [0.68, 0.66, 0.62, 1.0],
            "roughnessFactor": 0.16,
            "metallicFactor": 1.0,
        },
        "normalMapsTagged": all("normalTexture" in material for material in top_materials),
        "endpointInterlock": root["extras"]["rotationLockedBelowSMax"] is True
            and root["extras"]["slideLockedAtNonzeroAngle"] is True
            and root["extras"]["rotationAtSMaxDegrees"] == 360
            and root["extras"]["returnRule"] == "align theta to 0 then close",
        "closedZeroMotion": root["extras"]["defaultPose"] == "closed-zero-motion"
            and root["extras"]["linearVelocityMmPerSecond"] == 0
            and root["extras"]["angularVelocityDegreesPerSecond"] == 0,
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "pass": all(checks.values()),
        "sourceRejectedGlbSha256": sha256_bytes(REJECTED.read_bytes()),
        "correctedGlbSha256": sha256_bytes(CORRECTED.read_bytes()),
        "geometryAccessorPayloads": payloads,
        "materials": material_dump,
        "embeddedImages": images,
        "checks": checks,
    }
    (HERE / "corrected-glb-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"pass": True, "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
