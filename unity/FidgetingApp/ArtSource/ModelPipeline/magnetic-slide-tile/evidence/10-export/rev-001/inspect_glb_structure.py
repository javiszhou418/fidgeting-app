#!/usr/bin/env python3
"""Inspect the Gate 10 GLB container and accessor contract."""

from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GLB = ROOT / "magnetic-slide-tile.glb"
OUTPUT = ROOT / "glb-structure-validation.json"


def main() -> None:
    data = GLB.read_bytes()
    magic, version, total_length = struct.unpack_from("<4sII", data, 0)
    offset = 12
    chunks = []
    document = None
    while offset < total_length:
        length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        payload = data[offset:offset + length]
        offset += length
        chunks.append({"type": chunk_type, "bytes": length})
        if chunk_type == 0x4E4F534A:
            document = json.loads(payload.rstrip(b"\x00 \t\r\n").decode("utf-8"))
    if document is None:
        raise RuntimeError("GLB JSON chunk missing.")
    primitives = [
        primitive
        for mesh in document.get("meshes", [])
        for primitive in mesh.get("primitives", [])
    ]
    attributes = [set(primitive.get("attributes", {})) for primitive in primitives]
    nodes = {node.get("name"): node for node in document.get("nodes", [])}
    images = document.get("images", [])
    checks = {
        "header": magic == b"glTF" and version == 2 and total_length == len(data),
        "jsonAndBinaryChunks": len(chunks) == 2
        and chunks[0]["type"] == 0x4E4F534A
        and chunks[1]["type"] == 0x004E4942,
        "twoMeshesFourPrimitives": len(document.get("meshes", [])) == 2 and len(primitives) == 4,
        "normalsPresent": all("NORMAL" in item for item in attributes),
        "tangentsPresent": all("TANGENT" in item for item in attributes),
        "uvsPresent": all("TEXCOORD_0" in item for item in attributes),
        "positionsPresent": all("POSITION" in item for item in attributes),
        "indicesPresent": all("indices" in primitive for primitive in primitives),
        "threeMaterials": len(document.get("materials", [])) == 3,
        "twoEmbeddedImages": len(images) == 2 and all("bufferView" in image for image in images),
        "noAnimations": "animations" not in document or len(document["animations"]) == 0,
        "noCameras": "cameras" not in document or len(document["cameras"]) == 0,
        "noLightsExtension": "KHR_lights_punctual" not in document.get("extensions", {}),
        "closedDefault": nodes["UpperTranslation"].get("translation", [0, 0, 0]) == [0, 0, 0],
        "millimeterToMeterRootScale": all(
            abs(value - 0.001) <= 1e-9
            for value in nodes["MagneticSlideTile_Blockout_R003"].get("scale", [])
        ),
        "hiddenEnvelopeMetadataOnly": "ConcealedCircularEnvelope_Metadata" in nodes
        and all("mesh" not in nodes["ConcealedCircularEnvelope_Metadata"] for _ in [0]),
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 1,
        "header": {
            "magic": magic.decode("ascii"),
            "version": version,
            "totalLength": total_length,
        },
        "chunks": chunks,
        "asset": document.get("asset"),
        "sceneCount": len(document.get("scenes", [])),
        "nodeNames": sorted(name for name in nodes if name),
        "meshNames": [mesh.get("name") for mesh in document.get("meshes", [])],
        "materialNames": [material.get("name") for material in document.get("materials", [])],
        "imageRecords": images,
        "primitiveAttributes": [sorted(item) for item in attributes],
        "animations": document.get("animations", []),
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("GLB structure validation failed.")


if __name__ == "__main__":
    main()
