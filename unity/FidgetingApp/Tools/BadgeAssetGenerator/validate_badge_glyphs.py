#!/usr/bin/env python3
"""Validate the production Badge glyph source and raster export contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "Artifacts" / "BadgeSpecial" / "VectorGlyphs"
MANIFEST = ASSET_DIR / "badge-glyph-manifest.json"
EXPECTED_ASSET_COUNT = 40


def fail(message: str) -> None:
    raise AssertionError(message)


def sips_properties(path: Path) -> dict[str, str]:
    result = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "hasAlpha", "-g", "profile", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    properties: dict[str, str] = {}
    for line in result.stdout.splitlines():
        match = re.match(r"\s+(pixelWidth|pixelHeight|hasAlpha|profile):\s+(.+)$", line)
        if match:
            properties[match.group(1)] = match.group(2)
    return properties


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assets = manifest.get("assets", [])
    if len(assets) != EXPECTED_ASSET_COUNT:
        fail(f"Expected {EXPECTED_ASSET_COUNT} manifest entries, found {len(assets)}")

    ids = [item["id"] for item in assets]
    if len(set(ids)) != EXPECTED_ASSET_COUNT:
        fail("Badge glyph IDs are not unique")

    svg_hashes: set[str] = set()
    for item in assets:
        svg_path = ASSET_DIR / item["svg"]
        png_path = ASSET_DIR / item["png"]
        if not svg_path.is_file() or not png_path.is_file():
            fail(f"Missing asset pair for {item['id']}")

        root = ET.parse(svg_path).getroot()
        if root.attrib.get("width") != "1024" or root.attrib.get("height") != "1024":
            fail(f"{svg_path.name} is not a 1024 square source")
        if root.attrib.get("viewBox") != "0 0 160 160":
            fail(f"{svg_path.name} uses the wrong viewBox")
        source = svg_path.read_bytes()
        if b'stroke-width="10"' not in source or b'stroke-linecap="round"' not in source or b'stroke-linejoin="round"' not in source:
            fail(f"{svg_path.name} violates the rounded-monoline geometry contract")
        svg_hashes.add(hashlib.sha256(source).hexdigest())

        properties = sips_properties(png_path)
        if properties.get("pixelWidth") != "1024" or properties.get("pixelHeight") != "1024":
            fail(f"{png_path.name} is not 1024 × 1024")
        if properties.get("hasAlpha") != "yes":
            fail(f"{png_path.name} has no alpha channel")
        if not properties.get("profile", "").startswith("sRGB"):
            fail(f"{png_path.name} is not tagged sRGB")

    if len(svg_hashes) != EXPECTED_ASSET_COUNT:
        fail("At least two production glyph SVG files are exact duplicates")

    print(
        f"badge_glyph_validation=pass assets={EXPECTED_ASSET_COUNT} "
        "svg=unique/rounded-monoline png=1024x1024/alpha/sRGB"
    )


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ET.ParseError, subprocess.CalledProcessError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"badge_glyph_validation=fail {error}", file=sys.stderr)
        raise SystemExit(1)
