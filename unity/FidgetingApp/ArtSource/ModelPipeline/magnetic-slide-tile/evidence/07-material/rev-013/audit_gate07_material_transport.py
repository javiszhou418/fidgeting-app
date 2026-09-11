#!/usr/bin/env python3
"""Audit Gate 07 rev 13 material zones in Blend, GLB, and FBX re-imports."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = HERE / "magnetic-slide-tile-material-r013.blend"
GLB_PATH = HERE / "magnetic-slide-tile-material-r013-lookdev.glb"
FBX_PATH = HERE / "magnetic-slide-tile-material-r013.fbx"
REPORT_PATH = HERE / "material-transport-audit.json"
GEOMETRY_DIGEST = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
PRODUCT = ("BottomExterior", "MovingTopBody")
CORE = [
    "BottomExterior",
    "InternalAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def geometry_digest() -> str:
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()


def material_kind(name: str) -> str:
    if "TopArtwork" in name:
        return "topArtwork"
    if "SolidDarkSide" in name:
        return "solidDarkSide"
    if "PolishedBrightSilverRim" in name:
        return "polishedSilverRim"
    if "NeutralUnderside" in name:
        return "neutralUnderside"
    return "other"


def object_by_base_name(name: str):
    exact = bpy.data.objects.get(name)
    if exact is not None:
        return exact
    matches = [
        obj
        for obj in bpy.data.objects
        if obj.name == name or obj.name.startswith(f"{name}.")
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one {name} object, got {[obj.name for obj in matches]}"
        )
    return matches[0]


def inspect_product(label: str) -> dict:
    result = {}
    for requested_name in PRODUCT:
        obj = object_by_base_name(requested_name)
        mesh = obj.data
        uv = mesh.uv_layers.get("ArtworkUV") or mesh.uv_layers.active
        if uv is None:
            raise RuntimeError(f"{label} {obj.name} has no artwork UV.")
        max_z = max(vertex.co.z for vertex in mesh.vertices)
        face_counts = {
            "topArtwork": 0,
            "solidDarkSide": 0,
            "polishedSilverRim": 0,
            "neutralUnderside": 0,
            "other": 0,
        }
        triangle_counts = {key: 0 for key in face_counts}
        side_artwork_faces = 0
        underside_artwork_faces = 0
        non_cap_textured_faces = 0
        cap_uvs = []
        material_indices = {}
        image_extensions = {}
        for slot_index, material in enumerate(mesh.materials):
            if material is None:
                continue
            material_indices[material.name] = slot_index
            image_extensions[material.name] = [
                node.extension
                for node in material.node_tree.nodes
                if material.use_nodes and node.type == "TEX_IMAGE"
            ]
        for polygon in mesh.polygons:
            material = mesh.materials[polygon.material_index]
            kind = material_kind(material.name if material else "")
            face_counts[kind] += 1
            triangle_counts[kind] += max(1, len(polygon.vertices) - 2)
            vertex_z = [mesh.vertices[index].co.z for index in polygon.vertices]
            is_top = (
                polygon.normal.z > 0.999
                and max(abs(value - max_z) for value in vertex_z) <= 1e-4
            )
            is_side = abs(polygon.normal.z) <= 0.72 and not is_top
            is_underside = polygon.normal.z < -0.15
            textured = bool(
                material
                and material.use_nodes
                and any(
                    node.type == "TEX_IMAGE" and node.image
                    for node in material.node_tree.nodes
                )
            )
            if kind == "topArtwork":
                for loop_index in polygon.loop_indices:
                    value = uv.data[loop_index].uv
                    cap_uvs.append([float(value.x), float(value.y)])
                if is_side:
                    side_artwork_faces += 1
                if is_underside:
                    underside_artwork_faces += 1
                if not is_top:
                    non_cap_textured_faces += 1
            elif textured:
                non_cap_textured_faces += 1
        result[requested_name] = {
            "actualObjectName": obj.name,
            "polygonCount": len(mesh.polygons),
            "triangleCount": sum(
                max(1, len(polygon.vertices) - 2)
                for polygon in mesh.polygons
            ),
            "materialSlots": [
                material.name if material else None
                for material in mesh.materials
            ],
            "materialIds": material_indices,
            "faceCounts": face_counts,
            "triangleCounts": triangle_counts,
            "sideWallArtworkFaceCount": side_artwork_faces,
            "sideWallArtworkTriangleCount": 0 if side_artwork_faces == 0 else None,
            "undersideArtworkFaceCount": underside_artwork_faces,
            "nonCapTexturedFaceCount": non_cap_textured_faces,
            "topArtworkPresent": face_counts["topArtwork"] > 0,
            "artworkUvLayer": uv.name,
            "artworkUvMin": [
                min(value[index] for value in cap_uvs)
                for index in (0, 1)
            ],
            "artworkUvMax": [
                max(value[index] for value in cap_uvs)
                for index in (0, 1)
            ],
            "artworkUvsWithinZeroOne": all(
                -1e-5 <= component <= 1 + 1e-5
                for value in cap_uvs
                for component in value
            ),
            "imageNodeExtensions": image_extensions,
        }
    return result


def read_glb_json(path: Path) -> dict:
    with path.open("rb") as handle:
        magic, version, length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF" or version != 2 or length != path.stat().st_size:
            raise RuntimeError("Invalid GLB header.")
        chunk_length, chunk_type = struct.unpack("<II", handle.read(8))
        if chunk_type != 0x4E4F534A:
            raise RuntimeError("GLB JSON chunk missing.")
        return json.loads(handle.read(chunk_length).decode("utf-8"))


def glb_contract() -> dict:
    gltf = read_glb_json(GLB_PATH)
    materials = [
        {
            "id": index,
            "name": material.get("name"),
            "baseColorTexture": (
                material.get("pbrMetallicRoughness", {})
                .get("baseColorTexture", {})
                .get("index")
            ),
            "normalTexture": material.get("normalTexture", {}).get("index"),
        }
        for index, material in enumerate(gltf.get("materials", []))
    ]
    primitives = []
    for mesh_index, mesh in enumerate(gltf.get("meshes", [])):
        for primitive_index, primitive in enumerate(mesh.get("primitives", [])):
            material_id = primitive.get("material")
            material_name = (
                gltf["materials"][material_id].get("name")
                if material_id is not None
                else None
            )
            primitives.append({
                "meshId": mesh_index,
                "meshName": mesh.get("name"),
                "primitiveId": primitive_index,
                "materialId": material_id,
                "materialName": material_name,
                "indexAccessor": primitive.get("indices"),
                "uvAccessor": primitive.get("attributes", {}).get("TEXCOORD_0"),
            })
    samplers = [
        {
            "id": index,
            "wrapS": sampler.get("wrapS", 10497),
            "wrapT": sampler.get("wrapT", 10497),
            "minFilter": sampler.get("minFilter"),
            "magFilter": sampler.get("magFilter"),
        }
        for index, sampler in enumerate(gltf.get("samplers", []))
    ]
    return {
        "assetVersion": gltf.get("asset", {}).get("version"),
        "materials": materials,
        "primitives": primitives,
        "samplers": samplers,
        "meshCount": len(gltf.get("meshes", [])),
        "materialCount": len(gltf.get("materials", [])),
        "imageCount": len(gltf.get("images", [])),
        "allSamplersClampNoWrap": bool(samplers)
        and all(
            sampler["wrapS"] == 33071 and sampler["wrapT"] == 33071
            for sampler in samplers
        ),
        "onlyArtworkMaterialsSampleImages": all(
            material["baseColorTexture"] is None
            or material_kind(material["name"] or "") == "topArtwork"
            for material in materials
        ),
        "fourPrimitivesPerProduct": all(
            len([
                primitive
                for primitive in primitives
                if primitive["meshName"].startswith(name)
            ]) == 4
            for name in PRODUCT
        ),
    }


def inspect_import(kind: str, path: Path) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if kind == "glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif kind == "fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise ValueError(kind)
    bpy.context.view_layer.update()
    return inspect_product(kind)


def format_checks(report: dict) -> dict:
    checks = {}
    for format_name in ("blend", "glbReimport", "fbxReimport"):
        data = report[format_name]
        checks[f"{format_name}ZeroSideArtwork"] = all(
            item["sideWallArtworkFaceCount"] == 0
            for item in data.values()
        )
        checks[f"{format_name}ZeroUndersideArtwork"] = all(
            item["undersideArtworkFaceCount"] == 0
            for item in data.values()
        )
        checks[f"{format_name}TopArtworkPresent"] = all(
            item["topArtworkPresent"]
            for item in data.values()
        )
        checks[f"{format_name}NoNonCapTextureSampling"] = all(
            item["nonCapTexturedFaceCount"] == 0
            for item in data.values()
        )
        checks[f"{format_name}ArtworkUvsBounded"] = all(
            item["artworkUvsWithinZeroOne"]
            for item in data.values()
        )
        checks[f"{format_name}AllZonesPresent"] = all(
            all(item["faceCounts"][zone] > 0 for zone in (
                "topArtwork",
                "solidDarkSide",
                "polishedSilverRim",
                "neutralUnderside",
            ))
            for item in data.values()
        )
    checks["blendGeometryDigest"] = report["geometryDigest"] == GEOMETRY_DIGEST
    checks["glbClampNoWrap"] = report["glbContract"]["allSamplersClampNoWrap"]
    checks["glbOnlyArtworkSamplesImages"] = report["glbContract"]["onlyArtworkMaterialsSampleImages"]
    checks["glbFourPrimitivesPerProduct"] = report["glbContract"]["fourPrimitivesPerProduct"]
    checks["upperLowerArtworkIndependent"] = all(
        report[format_name]["BottomExterior"]["materialSlots"][0]
        != report[format_name]["MovingTopBody"]["materialSlots"][0]
        for format_name in ("blend", "glbReimport", "fbxReimport")
    )
    return checks


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE_BLEND.resolve():
        raise RuntimeError("Open the Gate 07 rev 13 Blend before auditing.")
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "07-material",
        "revision": 13,
        "blenderVersion": bpy.app.version_string,
        "geometryDigest": geometry_digest(),
        "assetHashes": {
            "blend": sha256(SOURCE_BLEND),
            "glb": sha256(GLB_PATH),
            "fbx": sha256(FBX_PATH),
        },
        "blend": inspect_product("blend"),
        "glbContract": glb_contract(),
    }
    report["glbReimport"] = inspect_import("glb", GLB_PATH)
    report["fbxReimport"] = inspect_import("fbx", FBX_PATH)
    report["checks"] = format_checks(report)
    report["pass"] = all(report["checks"].values())
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({
        "pass": report["pass"],
        "blend": {
            name: item["faceCounts"]
            for name, item in report["blend"].items()
        },
        "glbReimport": {
            name: item["triangleCounts"]
            for name, item in report["glbReimport"].items()
        },
        "fbxReimport": {
            name: item["triangleCounts"]
            for name, item in report["fbxReimport"].items()
        },
        "glbSamplerClamp": report["glbContract"]["allSamplersClampNoWrap"],
    }, indent=2))


if __name__ == "__main__":
    main()
