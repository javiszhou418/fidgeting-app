#!/usr/bin/env python3
"""Audit Gate 08 rev 6 lighting, GLB transport, passes, and partitions."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent.parent / "07-material/rev-013/magnetic-slide-tile-material-r013.blend"
SOURCE_SHA = "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c"
GLB = HERE / "magnetic-slide-tile-lighting-lookdev-r006.glb"
REPORT = HERE / "lighting-material-audit.json"
EXPECTED = {
    "BottomExterior": {
        "topArtwork": 511,
        "solidDarkSide": 6156,
        "polishedSilverRim": 4104,
        "neutralUnderside": 7693,
    },
    "MovingTopBody": {
        "topArtwork": 511,
        "solidDarkSide": 10268,
        "polishedSilverRim": 4104,
        "neutralUnderside": 11805,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise RuntimeError("Invalid GLB header.")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RuntimeError("GLB JSON chunk missing.")
    return json.loads(data[20:20 + chunk_length].decode("utf-8").rstrip("\x00 \t\r\n"))


def material_zone(name: str) -> str:
    if "Artwork" in name:
        return "topArtwork"
    if "SolidDarkSide" in name:
        return "solidDarkSide"
    if "PolishedBrightSilverRim" in name:
        return "polishedSilverRim"
    if "NeutralUnderside" in name:
        return "neutralUnderside"
    return "other"


def inspect_imported_object(obj) -> dict:
    counts = {
        "topArtwork": 0,
        "solidDarkSide": 0,
        "polishedSilverRim": 0,
        "neutralUnderside": 0,
        "other": 0,
    }
    side_artwork = 0
    underside_artwork = 0
    artwork_uvs = []
    uv_layer = obj.data.uv_layers.active
    for polygon in obj.data.polygons:
        material = obj.data.materials[polygon.material_index]
        zone = material_zone(material.name)
        counts[zone] += 1
        if zone == "topArtwork":
            if abs(polygon.normal.z) < 0.2:
                side_artwork += 1
            if polygon.normal.z < -0.2:
                underside_artwork += 1
            if uv_layer:
                artwork_uvs.extend(
                    tuple(uv_layer.data[loop_index].uv)
                    for loop_index in polygon.loop_indices
                )
    uv_array = np.asarray(artwork_uvs, dtype=np.float64)
    expected = EXPECTED[obj.name]
    checks = {
        "triangleCountsExact": all(counts[key] == value for key, value in expected.items()),
        "noUnknownMaterial": counts["other"] == 0,
        "sideArtworkZero": side_artwork == 0,
        "undersideArtworkZero": underside_artwork == 0,
        "topArtworkPresent": counts["topArtwork"] > 0,
        "silverRimPresent": counts["polishedSilverRim"] > 0,
        "artworkUvsPresent": uv_array.size > 0,
        "artworkUvsWithinZeroOne": uv_array.size > 0
        and float(uv_array.min()) >= 0
        and float(uv_array.max()) <= 1,
    }
    return {
        "triangleCount": len(obj.data.polygons),
        "materialSlots": [material.name for material in obj.data.materials],
        "zoneTriangleCounts": counts,
        "sideArtworkTriangles": side_artwork,
        "undersideArtworkTriangles": underside_artwork,
        "artworkUvMin": uv_array.min(axis=0).tolist() if uv_array.size else None,
        "artworkUvMax": uv_array.max(axis=0).tolist() if uv_array.size else None,
        "checks": checks,
        "pass": all(checks.values()),
    }


def image_metrics(path: Path) -> dict:
    source = oiio.ImageInput.open(str(path))
    specification = source.spec()
    pixels = source.read_image(format=oiio.UINT8)
    source.close()
    pixels = np.asarray(pixels, dtype=np.uint8).reshape(
        specification.height,
        specification.width,
        specification.nchannels,
    )[:, :, :3]
    foreground = np.max(pixels, axis=2) > 12
    object_pixels = pixels[foreground]
    red = (
        (object_pixels[:, 0] > object_pixels[:, 1] * 1.15)
        & (object_pixels[:, 0] > 45)
    )
    dark = np.max(object_pixels, axis=1) < 85
    bright_neutral = (
        (np.min(object_pixels, axis=1) > 115)
        & ((np.max(object_pixels, axis=1) - np.min(object_pixels, axis=1)) < 35)
    )
    return {
        "dimensions": [pixels.shape[1], pixels.shape[0]],
        "foregroundPixels": int(foreground.sum()),
        "redFraction": float(red.mean()),
        "darkFraction": float(dark.mean()),
        "brightNeutralFraction": float(bright_neutral.mean()),
        "clippedFraction": float(np.mean(np.max(pixels, axis=2) >= 255)),
    }


def main() -> None:
    blender = json.loads((HERE / "blender-lighting-report.json").read_text(encoding="utf-8"))
    motion = json.loads((HERE / "legal-lighting-turntable-report.json").read_text(encoding="utf-8"))
    frame_audit = json.loads((HERE / "frame-partition-audit.json").read_text(encoding="utf-8"))
    document = glb_json(GLB)
    samplers = document.get("samplers", [])
    sampler_clamp = bool(samplers) and all(
        sampler.get("wrapS", 10497) == 33071
        and sampler.get("wrapT", 10497) == 33071
        for sampler in samplers
    )
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    imported = {
        obj.name: inspect_imported_object(obj)
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name in EXPECTED
    }
    required_images = [
        "hero.png",
        "left-oblique.png",
        "right-oblique.png",
        "low.png",
        "pass-beauty.png",
        "pass-clay.png",
        "pass-normal.png",
        "pass-depth.png",
        "pass-roughness.png",
        "closeup-top.png",
        "closeup-side.png",
        "closeup-rim.png",
        "legal-mid-slide-0.png",
        "legal-max-open-0.png",
        "legal-max-open-12.png",
        "legal-max-open-36.png",
        "legal-max-open-360.png",
    ]
    metrics = {
        name: image_metrics(HERE / name)
        for name in required_images
    }
    checks = {
        "builderPassed": blender["pass"],
        "motionPassed": motion["pass"],
        "sourceBlendHash": sha256(SOURCE) == SOURCE_SHA,
        "sourceGeometryCurrent": blender["geometryDigestAfter"] == blender["geometryDigestBefore"],
        "sourceMeshElementIdentical": blender["sourceMeshDataElementIdentical"],
        "allDiagnosticPassesNonDestructive": blender["checks"]["allDiagnosticPassesNonDestructive"],
        "materialSlotsIdentical": blender["checks"]["materialSlotsIdentical"],
        "materialIndicesIdentical": blender["checks"]["polygonMaterialIndicesByteIdentical"],
        "uvsIdentical": blender["checks"]["uvsByteIdentical"],
        "framePartitionAudit": frame_audit["pass"],
        "allRequiredImages": all((HERE / name).exists() for name in required_images),
        "allImportedObjects": set(imported) == set(EXPECTED),
        "glbPartitions": imported
        and all(values["pass"] for values in imported.values()),
        "glbClampNoWrap": sampler_clamp,
        "capArtworkVisible": metrics["closeup-top.png"]["redFraction"] > 0.03,
        "darkSidesVisible": metrics["closeup-side.png"]["darkFraction"] > 0.20,
        "silverRimVisible": metrics["closeup-rim.png"]["brightNeutralFraction"] > 0.001,
        "noMaterialEmission": blender["checks"]["zeroProductEmission"],
        "standardViewsClippingBounded": max(
            metrics[name]["clippedFraction"]
            for name in [
                "hero.png",
                "left-oblique.png",
                "right-oblique.png",
                "low.png",
                "pass-beauty.png",
            ]
        ) < 0.01,
        "closeupSpecularClippingBounded": max(
            metrics[name]["clippedFraction"]
            for name in ["closeup-top.png", "closeup-side.png", "closeup-rim.png"]
        ) < 0.02,
        "cameraClippingValid": all(
            recipe["clipMm"][0] > 0
            and recipe["clipMm"][1] > recipe["clipMm"][0]
            for recipe in blender["cameraRecipes"].values()
        ),
        "sharedHdrCurrent": blender["checks"]["sharedHdrCurrent"],
        "endpointMotionOnly": motion["checks"]["rotationOnlyAtEndpoint"]
        and motion["checks"]["slideReturnOnlyAligned"],
        "fixedAxisNoFlipNoPenetration": motion["checks"]["fixedAxisInvariant"]
        and motion["checks"]["noPitchRollFlip"]
        and motion["checks"]["approvedNoPenetrationAudit"],
        "noSimulatorUnityBuildDevice": not blender["checks"]["shippingUntouched"] is False,
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 6,
        "status": "validated",
        "sourceHashes": {
            "materialBlend": SOURCE_SHA,
            "lightingBlend": sha256(HERE / "magnetic-slide-tile-lighting-r006.blend"),
            "interactiveGlb": sha256(GLB),
            "environment": blender["environment"]["sha256"],
            "contract": blender["contractSha256"],
            "geometryDigest": blender["geometryDigestAfter"],
        },
        "environment": blender["environment"],
        "cameraRecipes": blender["cameraRecipes"],
        "diagnosticPasses": blender["diagnosticPasses"],
        "importedGlb": imported,
        "glbSamplers": samplers,
        "imageMetrics": metrics,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "sourceHashes": report["sourceHashes"],
        "checks": checks,
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 rev 6 lighting/material audit failed.")


if __name__ == "__main__":
    main()
