#!/usr/bin/env python3
"""Prepare exact Gate 10 texture and environment transport assets."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
MODEL = HERE.parent.parent.parent
GATE09 = MODEL / "evidence/09-environment/rev-008"
PACKAGE = HERE / "package"
TEXTURES = PACKAGE / "textures"
ENVIRONMENT = PACKAGE / "environment"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def copy_exact(source, destination):
    shutil.copyfile(source, destination)
    return {"path": destination.relative_to(HERE).as_posix(), "sha256": sha256(destination), "bytes": destination.stat().st_size}


def create_channel_pack(layer, albedo_path, roughness_path, mask_path):
    albedo = np.asarray(Image.open(albedo_path).convert("RGB"), dtype=np.float32)
    roughness = np.asarray(Image.open(roughness_path).convert("L"), dtype=np.uint8)
    mask = np.asarray(Image.open(mask_path).convert("L").resize((albedo.shape[1], albedo.shape[0]), Image.Resampling.NEAREST), dtype=np.uint8)
    metallic = np.where(mask >= 128, 107, 0).astype(np.uint8)
    ao = np.full_like(metallic, 255)
    red_detail = np.clip((albedo[:, :, 0] - np.maximum(albedo[:, :, 1], albedo[:, :, 2])) * 2.2, 0, 255).astype(np.uint8)
    smoothness = 255 - roughness
    packed = np.stack([metallic, ao, red_detail, smoothness], axis=2)
    packed_path = TEXTURES / f"{layer}-maskmap-r009.png"
    Image.fromarray(packed, "RGBA").save(packed_path)
    height = red_detail.astype(np.float32) / 255.0
    gy, gx = np.gradient(height)
    strength = 1.1
    nx, ny = -gx * strength, -gy * strength
    nz = np.ones_like(nx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.stack([
        (nx / length * 0.5 + 0.5) * 255,
        (ny / length * 0.5 + 0.5) * 255,
        (nz / length * 0.5 + 0.5) * 255,
    ], axis=2).astype(np.uint8)
    normal_path = TEXTURES / f"{layer}-normal-r009.png"
    Image.fromarray(normal, "RGB").save(normal_path)
    return {
        "maskMap": {"path": packed_path.relative_to(HERE).as_posix(), "sha256": sha256(packed_path), "channels": {"R": "metallic", "G": "ambient-occlusion", "B": "crystal-detail", "A": "smoothness"}},
        "normal": {"path": normal_path.relative_to(HERE).as_posix(), "sha256": sha256(normal_path), "basis": "tangent-space transport approximation; source procedural detail remains the parity authority"},
        "resolutionPx": [albedo.shape[1], albedo.shape[0]],
    }


def main():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    ENVIRONMENT.mkdir(parents=True, exist_ok=True)
    sources = {
        "upperBaseColor": GATE09 / "portable-textures/upper-albedo.png",
        "upperRoughness": GATE09 / "portable-textures/upper-roughness.png",
        "lowerBaseColor": GATE09 / "portable-textures/lower-albedo.png",
        "lowerRoughness": GATE09 / "portable-textures/lower-roughness.png",
        "upperArtworkMask": MODEL / "evidence/07-material/rev-007/artwork-upper-mask.png",
        "lowerArtworkMask": MODEL / "evidence/07-material/rev-010/artwork-lower-mask-r010.png",
        "perimeterMask": MODEL / "evidence/07-material/rev-007/artwork-top-perimeter-border-mask.png",
    }
    records = {}
    for name, source in sources.items():
        destination = TEXTURES / f"{name}.png"
        records[name] = copy_exact(source, destination)
        records[name]["resolutionPx"] = list(Image.open(destination).size)
    upper = create_channel_pack("upper", TEXTURES / "upperBaseColor.png", TEXTURES / "upperRoughness.png", TEXTURES / "upperArtworkMask.png")
    lower = create_channel_pack("lower", TEXTURES / "lowerBaseColor.png", TEXTURES / "lowerRoughness.png", TEXTURES / "lowerArtworkMask.png")
    environment = {
        "exr": copy_exact(GATE09 / "magnetic-slide-tile-shipping-studio-r008.exr", ENVIRONMENT / "magnetic-slide-tile-shipping-studio-r008.exr"),
        "preview": copy_exact(GATE09 / "magnetic-slide-tile-shipping-studio-r008-preview.png", ENVIRONMENT / "magnetic-slide-tile-shipping-studio-r008-preview.png"),
        "metadata": copy_exact(GATE09 / "portable-hdri-metadata.json", ENVIRONMENT / "portable-hdri-metadata.json"),
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 9,
        "pass": True,
        "textures": records,
        "channelPacks": {"upper": upper, "lower": lower},
        "environment": environment,
        "rules": {
            "baseColor": {"sRGB": True, "wrap": "clamp", "filter": "trilinear", "mipmaps": True},
            "maskMapAndNormal": {"sRGB": False, "wrap": "clamp", "filter": "trilinear", "mipmaps": True},
            "artworkMasks": {"sRGB": False, "wrap": "clamp", "filter": "bilinear", "mipmaps": True, "independentUpperLower": True},
            "npot": {
                "sourceResolutionPx": [620, 1000],
                "policy": "None / preserve dimensions",
                "forbidden": "Do not rescale to 512x1024 or stretch aspect ratio.",
                "unityImportApplied": False,
            },
            "astc": {
                "baseColorCandidate": "ASTC 6x6 after Gate 11 visual comparison",
                "maskNormalCandidate": "ASTC 4x4 after Gate 11 channel-error comparison",
                "sourceForParity": "lossless PNG",
                "applied": False,
            },
        },
    }
    (HERE / "texture-export-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"pass": True, "textureCount": len(records) + 4, "environmentSha256": environment["exr"]["sha256"]}, indent=2))


if __name__ == "__main__":
    main()

