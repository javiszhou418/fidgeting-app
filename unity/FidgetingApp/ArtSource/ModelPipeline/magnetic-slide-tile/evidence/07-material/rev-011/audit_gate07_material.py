#!/usr/bin/env python3
"""Independent Blender and GLB audit for Gate 07 rev 11."""

import hashlib
import json
import struct
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "blender-material-audit.json"
GLB_PATH = HERE / "magnetic-slide-tile-material-r011-lookdev.glb"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
SOURCE_SHA256 = "8047be52ce635d9bd18d5f2be3c3e223ac04c3101aec10221849d97b6e867085"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]


def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()


def glb_json(path):
    with path.open("rb") as handle:
        magic, version, length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF" or version != 2 or length != path.stat().st_size:
            raise RuntimeError("Invalid GLB header.")
        chunk_length, chunk_type = struct.unpack("<II", handle.read(8))
        if chunk_type != 0x4E4F534A:
            raise RuntimeError("GLB first chunk is not JSON.")
        return json.loads(handle.read(chunk_length).decode("utf-8"))


def main():
    scene = bpy.context.scene
    digest = geometry_digest()
    required_materials = [
        "M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct",
        "M07R11_PolishedSilver", "M07R11_DarkExteriorSide",
        "M07R11_NeutralTechnical", "M07R11_BallCandidate_UnknownMaterial",
    ]
    materials = {name: bpy.data.materials.get(name) for name in required_materials}
    missing = [name for name, material in materials.items() if material is None]
    emission = {}
    texture_nodes = {}
    for name, material in materials.items():
        if material is None:
            continue
        bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        emission[name] = float(bsdf.inputs["Emission Strength"].default_value) if bsdf and bsdf.inputs.get("Emission Strength") else 0.0
        texture_nodes[name] = [
            {
                "node": node.name,
                "image": node.image.name if node.image else None,
                "sizePx": list(node.image.size) if node.image else None,
                "packed": bool(node.image and node.image.packed_file),
            }
            for node in material.node_tree.nodes if node.type == "TEX_IMAGE"
        ]
    boundary_counts = {}
    for object_name in ("BottomExterior", "MovingTopBody"):
        obj = bpy.data.objects[object_name]
        counts = {material.name: 0 for material in obj.data.materials}
        for polygon in obj.data.polygons:
            counts[obj.data.materials[polygon.material_index].name] += 1
        boundary_counts[object_name] = counts
    gltf = glb_json(GLB_PATH)
    glb_materials = [material.get("name") for material in gltf.get("materials", [])]
    glb_images = gltf.get("images", [])
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    checks = {
        "sceneGate": scene.get("gate") == "07-material" and scene.get("material_revision") == 11,
        "sourceHash": scene.get("gate06_source_sha256") == SOURCE_SHA256,
        "contractHash": scene.get("mechanism_contract_sha256") == CONTRACT_SHA256,
        "geometryDigest": digest == GEOMETRY_DIGEST,
        "materialsPresent": not missing,
        "independentMasks": materials["M07R11_Crystal_Upper"].get("sourceMaskSha256")
        != materials["M07R11_Crystal_LowerDistinct"].get("sourceMaskSha256"),
        "packedTextures": all(
            item["packed"] and item["sizePx"] == [620, 1000]
            for name in ("M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct")
            for item in texture_nodes[name]
        ),
        "zeroEmission": all(value == 0 for value in emission.values()),
        "slotBoundaries": all(
            counts.get("M07R11_PolishedSilver", 0) > 0
            and counts.get("M07R11_DarkExteriorSide", 0) > 0
            for counts in boundary_counts.values()
        ),
        "upperLowerArtwork": boundary_counts["MovingTopBody"].get("M07R11_Crystal_Upper") == 1
        and boundary_counts["BottomExterior"].get("M07R11_Crystal_LowerDistinct") == 1,
        "unknownBallMaterial": all(
            bpy.data.objects[name].get("exactMaterialClaim") == "unknown"
            for name in ("BallCandidateLeft", "BallCandidateRight")
        ),
        "zeroSelfMotion": not animated and scene.get("self_motion") is False,
        "glbMaterials": all(name in glb_materials for name in required_materials),
        "glbEmbeddedImages": len(glb_images) >= 4 and all("bufferView" in image for image in glb_images),
        "oldShippingUntouched": scene.get("shipping_unity_changed") is False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 11,
        "blenderVersion": bpy.app.version_string,
        "geometryDigest": digest,
        "missingMaterials": missing,
        "emission": emission,
        "textureNodes": texture_nodes,
        "boundaryCounts": boundary_counts,
        "animatedObjects": animated,
        "glb": {
            "materials": glb_materials,
            "imageCount": len(glb_images),
            "textureCount": len(gltf.get("textures", [])),
            "meshCount": len(gltf.get("meshes", [])),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

