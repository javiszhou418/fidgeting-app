#!/usr/bin/env python3
"""Prepare independent Gate 10 artwork packs and Gate 11 ASTC specifications."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
TEXTURES = ROOT / "textures"
OUTPUT = ROOT / "texture-manifest.json"
EXPECTED_ARTWORK_HASH = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    TEXTURES.mkdir(parents=True, exist_ok=True)
    sources = {
        "artwork-upper-mask.png": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-007/artwork-upper-mask.png",
        "artwork-lower-mask.png": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-007/artwork-lower-mask.png",
        "artwork-top-perimeter-border-mask.png": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-007/artwork-top-perimeter-border-mask.png",
    }
    for name, source in sources.items():
        shutil.copy2(source, TEXTURES / name)
    upper = np.asarray(Image.open(TEXTURES / "artwork-upper-mask.png").convert("L"))
    lower = np.asarray(Image.open(TEXTURES / "artwork-lower-mask.png").convert("L"))
    border = np.asarray(Image.open(TEXTURES / "artwork-top-perimeter-border-mask.png").convert("L"))
    if upper.shape != (1000, 620) or lower.shape != upper.shape or border.shape != upper.shape:
        raise RuntimeError("Approved artwork dimensions changed.")
    for name, motif in [("upper", upper), ("lower", lower)]:
        combined = np.maximum(motif, border)
        pack = np.dstack([motif, border, combined, np.full_like(motif, 255)])
        Image.fromarray(pack, "RGBA").save(TEXTURES / f"artwork-{name}-channel-pack.png")
        factor = combined.astype(np.float32)[..., None] / 255.0
        blood_red = np.array([120.0, 5.0, 16.0], dtype=np.float32)
        blackened = np.array([4.0, 2.0, 3.0], dtype=np.float32)
        base = blood_red * (1.0 - factor * 0.94) + blackened * (factor * 0.94)
        Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").save(
            TEXTURES / f"face-{name}-transport-basecolor.png"
        )
    plans = {
        "artwork-upper-channel-pack.png": {"format": "ASTC_4x4", "block": [4, 4], "sRGB": False, "runtime": True},
        "artwork-lower-channel-pack.png": {"format": "ASTC_4x4", "block": [4, 4], "sRGB": False, "runtime": True},
        "face-upper-transport-basecolor.png": {"format": "ASTC_6x6", "block": [6, 6], "sRGB": True, "runtime": False},
        "face-lower-transport-basecolor.png": {"format": "ASTC_6x6", "block": [6, 6], "sRGB": True, "runtime": False},
        "artwork-upper-mask.png": {"format": "EditorSource", "block": None, "sRGB": False, "runtime": False},
        "artwork-lower-mask.png": {"format": "EditorSource", "block": None, "sRGB": False, "runtime": False},
        "artwork-top-perimeter-border-mask.png": {"format": "EditorSource", "block": None, "sRGB": False, "runtime": False},
    }
    records = {}
    for path in sorted(TEXTURES.glob("*.png")):
        image = Image.open(path)
        width, height = image.size
        plan = plans[path.name]
        compressed = None
        if plan["block"]:
            bw, bh = plan["block"]
            compressed = math.ceil(width / bw) * math.ceil(height / bh) * 16
        records[path.name] = {
            "path": str(path.relative_to(REPO)),
            "sha256": sha256(path),
            "dimensionsPx": [width, height],
            "mode": image.mode,
            "channels": list(image.getbands()),
            "fileBytes": path.stat().st_size,
            "estimatedRgba32MemoryBytes": width * height * 4,
            "plannedAstcMemoryBytes": compressed,
            "gate11ImportPlan": {
                "deliveryState": "specified-only-not-applied",
                "platform": "iPhone",
                "format": plan["format"],
                "maxSize": 1024,
                "mipmaps": plan["runtime"],
                "sRGB": plan["sRGB"],
                "alphaSource": "None" if image.mode != "RGBA" else "InputTextureAlpha",
                "runtime": plan["runtime"],
            },
        }
    runtime_files = [name for name, record in records.items() if record["gate11ImportPlan"]["runtime"]]
    checks = {
        "sourceDimensions": upper.shape == lower.shape == border.shape == (1000, 620),
        "upperLineage": records["artwork-upper-mask.png"]["sha256"] == EXPECTED_ARTWORK_HASH,
        "lowerLineage": records["artwork-lower-mask.png"]["sha256"] == EXPECTED_ARTWORK_HASH,
        "independentRuntimePacks": runtime_files == [
            "artwork-lower-channel-pack.png",
            "artwork-upper-channel-pack.png",
        ],
        "runtimeAstc4x4Specified": all(records[name]["gate11ImportPlan"]["format"] == "ASTC_4x4" for name in runtime_files),
        "astcNotApplied": all(record["gate11ImportPlan"]["deliveryState"] == "specified-only-not-applied" for record in records.values()),
        "noOversizeTexture": all(max(record["dimensionsPx"]) <= 1024 for record in records.values()),
        "texturePayloadBelowFiveMb": sum(record["fileBytes"] for record in records.values()) < 5 * 1024 * 1024,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "10-export",
        "exportRevision": 2,
        "records": records,
        "runtimeTextureFiles": runtime_files,
        "runtimeUncompressedRgba32Bytes": sum(records[name]["estimatedRgba32MemoryBytes"] for name in runtime_files),
        "runtimePlannedAstcBytes": sum(records[name]["plannedAstcMemoryBytes"] for name in runtime_files),
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 10 texture preparation failed.")


if __name__ == "__main__":
    main()
