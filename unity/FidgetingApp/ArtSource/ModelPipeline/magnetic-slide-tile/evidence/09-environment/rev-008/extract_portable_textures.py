#!/usr/bin/env python3
"""Extract approved packed texture bytes without color conversion."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "portable-textures"
EXPECTED = {
    "upper-albedo.png": "c0e9305d475cd2c591efc8a833a0aafb1aef4ccc437d84a3417674e6d1b453a5",
    "upper-roughness.png": "854f1dbc393585ff9b88f808c1a46a35b091088ac8b83894763f502876e3df6a",
    "lower-albedo.png": "968c1e87ca2d5ea7c8fc57106e42bcd09dc95395fac7dd3be569e580ea8850eb",
    "lower-roughness.png": "ca2697560a2e57685a71c423f15f70a72ebb47c93c53cae0e3a8dae0b3248245",
}


def main():
    OUTPUT.mkdir(exist_ok=True)
    records = {}
    for name, expected_sha256 in EXPECTED.items():
        image = bpy.data.images.get(name)
        if image is None or image.packed_file is None:
            raise RuntimeError(f"Missing packed approved texture {name}.")
        output = OUTPUT / name
        output.write_bytes(image.packed_file.data)
        actual = hashlib.sha256(output.read_bytes()).hexdigest()
        if actual != expected_sha256:
            raise RuntimeError(f"{name} hash drift: {actual}")
        records[name] = {
            "path": output.relative_to(HERE).as_posix(),
            "sha256": actual,
            "resolutionPx": list(image.size),
            "packedBytePreservation": True,
        }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 8,
        "pass": True,
        "source": "approved Gate 07 rev 11 packed image bytes carried by Gate 08/09 blend",
        "textures": records,
    }
    (HERE / "portable-texture-extraction.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

