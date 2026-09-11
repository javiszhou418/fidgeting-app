#!/usr/bin/env python3
"""Compose deterministic Gate 07 textures from approved artwork lineage."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


HERE = Path(__file__).resolve().parent
MATERIAL_ROOT = HERE.parent
UPPER_MASK = MATERIAL_ROOT / "rev-007/artwork-upper-mask.png"
LOWER_MASK = MATERIAL_ROOT / "rev-010/artwork-lower-mask-r010.png"
LOWER_DIRECT = MATERIAL_ROOT / "rev-010/artwork-lower-direct-mask-r010.png"
LOWER_RECONSTRUCTED = MATERIAL_ROOT / "rev-010/artwork-lower-reconstructed-mask-r010.png"
LOWER_PROVENANCE = MATERIAL_ROOT / "rev-010/lower-artwork-provenance.json"
BORDER_MASK = MATERIAL_ROOT / "rev-007/artwork-top-perimeter-border-mask.png"
RECIPE = MATERIAL_ROOT / "rev-010/material-recipe-r010.json"
EXPECTED = {
    UPPER_MASK: "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36",
    LOWER_MASK: "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2",
    BORDER_MASK: "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_mask(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0


def smooth_noise(rng, size, coarse):
    width, height = size
    source = Image.fromarray(rng.integers(0, 256, (coarse, max(2, round(coarse * width / height))), dtype=np.uint8))
    return np.asarray(source.resize(size, Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(2.2)), dtype=np.float32) / 255.0


def compose(name, motif, border, seed):
    height, width = motif.shape
    rng = np.random.default_rng(seed)
    macro = smooth_noise(rng, (width, height), 32)
    detail = smooth_noise(rng, (width, height), 140)
    grain = np.clip(0.68 * macro + 0.32 * detail, 0, 1)
    base = np.zeros((height, width, 3), dtype=np.float32)
    base[..., 0] = 22 + grain * 116
    base[..., 1] = 1.0 + np.maximum(grain - 0.62, 0) * 24
    base[..., 2] = 4.0 + np.maximum(grain - 0.48, 0) * 32
    cool = detail > 0.84
    base[cool, 0] *= 0.55
    base[cool, 1] += 13
    base[cool, 2] += 30
    occupied = np.maximum(motif, border) > 0.43
    base[occupied] = np.array([3.0, 2.0, 3.0])
    flakes = (rng.random((height, width)) > 0.994) & ~occupied
    base[flakes] = np.array([238.0, 48.0, 68.0])
    albedo = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    albedo_path = HERE / f"{name}-albedo.png"
    albedo.save(albedo_path, optimize=True)
    roughness = np.clip(34 + (1.0 - grain) * 42, 22, 110)
    roughness[occupied] = 64
    roughness_path = HERE / f"{name}-roughness.png"
    Image.fromarray(roughness.astype(np.uint8), "L").save(roughness_path, optimize=True)
    return {
        "albedo": albedo_path.name,
        "albedoSha256": sha256(albedo_path),
        "roughness": roughness_path.name,
        "roughnessSha256": sha256(roughness_path),
        "resolutionPx": [width, height],
        "redMean": float(base[..., 0].mean()),
        "redStd": float(base[..., 0].std()),
        "blackFraction": float(occupied.mean()),
        "microflakePixels": int(flakes.sum()),
    }


def main():
    for path, expected in EXPECTED.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Approved texture hash drift: {path} {actual}")
    provenance = json.loads(LOWER_PROVENANCE.read_text(encoding="utf-8"))
    if not provenance["pass"] or not provenance["mask"]["hashesDistinct"]:
        raise RuntimeError("Lower direct/reconstructed provenance is invalid.")
    recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    upper = load_mask(UPPER_MASK)
    lower = load_mask(LOWER_MASK)
    border = load_mask(BORDER_MASK)
    if upper.shape != lower.shape or upper.shape != border.shape:
        raise RuntimeError("Artwork masks must share one resolution.")
    outputs = {
        "upper": compose("upper", upper, border, 70011),
        "lower": compose("lower", lower, border, 70012),
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 11,
        "appearanceAuthority": "original-user-blood-red-product-imagery-only",
        "sourceMasks": {
            "upper": {"path": str(UPPER_MASK), "sha256": sha256(UPPER_MASK), "lineage": "clean motif r002→r007"},
            "lower": {
                "path": str(LOWER_MASK),
                "sha256": sha256(LOWER_MASK),
                "directMaskSha256": sha256(LOWER_DIRECT),
                "reconstructedMaskSha256": sha256(LOWER_RECONSTRUCTED),
                "lineage": "direct user frames plus labeled reconstructed occlusion",
            },
            "border": {"path": str(BORDER_MASK), "sha256": sha256(BORDER_MASK), "widthPx": 64},
        },
        "outputs": outputs,
        "independentlyReplaceable": outputs["upper"]["albedoSha256"] != outputs["lower"]["albedoSha256"],
        "lowerDirectPixels": provenance["directTrace"]["pixelCount"],
        "lowerReconstructedPixels": provenance["reconstruction"]["pixelCount"],
        "materialValues": recipe,
        "emission": 0,
        "productionChemistryClaim": "unknown; visual approximation only",
    }
    report["pass"] = (
        report["independentlyReplaceable"]
        and all(output["resolutionPx"] == [620, 1000] for output in outputs.values())
        and all(output["redStd"] > 25 for output in outputs.values())
        and all(output["microflakePixels"] > 1000 for output in outputs.values())
        and report["emission"] == 0
    )
    (HERE / "texture-lineage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

