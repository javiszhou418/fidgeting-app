#!/usr/bin/env python3
"""Independent reopen audit for Gate 08 rev 2."""

import hashlib
import json
import struct
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "blender-lighting-audit.json"
GLB_PATH = HERE / "magnetic-slide-tile-lighting-r002-lookdev.glb"
GEOMETRY_DIGEST = "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe"
SOURCE_SHA256 = "fdf6e96206b6d048aa88fbd049a8af1a4d7a391d65ed74791c3acaca2767d274"
CONTRACT_SHA256 = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
CORE = [
    "BottomExterior", "FixedAxisBoss", "RotatingCarrierBody",
    "CarrierFollowerLeft", "CarrierFollowerRight",
    "BallCandidateLeft", "BallCandidateRight", "MovingTopBody",
]
MATERIALS = [
    "M07R11_Crystal_Upper", "M07R11_Crystal_LowerDistinct",
    "M07R11_PolishedSilver", "M07R11_InternalSilverReference",
    "M07R11_DarkExteriorSide", "M07R11_NeutralTechnical",
    "M07R11_BallCandidate_UnknownMaterial",
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
    missing_materials = [name for name in MATERIALS if bpy.data.materials.get(name) is None]
    emission = {}
    for name in MATERIALS:
        material = bpy.data.materials.get(name)
        if not material:
            continue
        bsdf = next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
        emission[name] = float(bsdf.inputs["Emission Strength"].default_value)
    lights = {
        obj.get("lightingRole"): {
            "name": obj.name,
            "type": obj.data.type,
            "powerW": obj.data.energy,
            "sizeMm": obj.data.size,
            "cctK": obj.get("cctK"),
        }
        for obj in bpy.data.objects if obj.type == "LIGHT" and obj.name.startswith("M08R2_")
    }
    cameras = [obj.name for obj in bpy.data.objects if obj.type == "CAMERA" and obj.name.startswith("M08R2_")]
    cards = [obj for obj in bpy.data.objects if obj.get("reflectionOnly")]
    pass_materials = [material for material in bpy.data.materials if material.get("technicalPassOnly")]
    animated = [
        obj.name for obj in bpy.data.objects
        if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
    ]
    gltf = glb_json(GLB_PATH)
    glb_materials = [material.get("name") for material in gltf.get("materials", [])]
    glb_images = gltf.get("images", [])
    required_files = [
        "hero.png", "left-oblique.png", "right-oblique.png", "low-angle.png",
        "pass-beauty.png", "pass-clay.png", "pass-normal.png", "pass-depth.png", "pass-roughness.png",
        "lighting-neutral.png", "lighting-studio.png", "lighting-daylight.png",
        "state-closed.png", "state-max-open.png", "state-detent-12.png", "state-detent-36.png",
        "flat-plane-raised-axis-lit.png", "underside-grooves-lit.png", "carrier-clearance-lit.png",
    ]
    checks = {
        "sceneIdentity": scene.get("gate") == "08-lighting" and scene.get("lighting_revision") == 2,
        "sourceHash": scene.get("gate07_source_sha256") == SOURCE_SHA256,
        "contractHash": scene.get("mechanism_contract_sha256") == CONTRACT_SHA256,
        "geometryDigest": digest == GEOMETRY_DIGEST,
        "materialDigestRecorded": bool(scene.get("approved_material_digest")),
        "approvedMaterialsPresent": not missing_materials,
        "approvedEmissionZero": all(value == 0 for value in emission.values()),
        "technicalPassIsolation": len(pass_materials) >= 5 and all(material.get("technicalPassOnly") for material in pass_materials),
        "fourDocumentedLights": set(lights) == {"key", "fill", "rim", "under"}
        and all(item["type"] == "AREA" and item["powerW"] > 0 and item["sizeMm"] > 0 for item in lights.values()),
        "requiredCameras": all(
            name in cameras for name in (
                "M08R2_Hero", "M08R2_LeftOblique", "M08R2_RightOblique",
                "M08R2_Low", "M08R2_TopReveal", "M08R2_Underside", "M08R2_Mechanism",
            )
        ),
        "reflectionCards": len(cards) == 4 and all(card.get("cameraVisible") is False for card in cards),
        "uniformWorldNoHdri": scene.world.get("hdri") == "none",
        "colorManagement": scene.view_settings.view_transform == "AgX"
        and scene.view_settings.look == "AgX - Medium High Contrast"
        and abs(scene.view_settings.exposure + 0.35) < 1e-6,
        "requiredFiles": all((HERE / name).exists() for name in required_files),
        "turntableFrames": len(list((HERE / "turntable").glob("frame-*.png"))) == 24,
        "glbMaterials": all(name in glb_materials for name in MATERIALS),
        "glbEmbeddedImages": len(glb_images) >= 4 and all("bufferView" in image for image in glb_images),
        "zeroSelfMotion": not animated and scene.get("self_motion") is False,
        "oldShippingUntouched": scene.get("shipping_unity_changed") is False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 2,
        "blenderVersion": bpy.app.version_string,
        "geometryDigest": digest,
        "materialDigest": scene.get("approved_material_digest"),
        "missingMaterials": missing_materials,
        "emission": emission,
        "lights": lights,
        "cameras": cameras,
        "reflectionCards": [card.name for card in cards],
        "animatedObjects": animated,
        "glb": {
            "materials": glb_materials,
            "images": len(glb_images),
            "meshes": len(gltf.get("meshes", [])),
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 Blender audit failed.")


if __name__ == "__main__":
    main()

