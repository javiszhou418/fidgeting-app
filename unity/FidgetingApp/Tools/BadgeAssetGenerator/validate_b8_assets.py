#!/usr/bin/env python3
"""Deterministic shipping checks for the B8 Badge artwork bundle."""

from __future__ import annotations

import json
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
ARTWORK = ROOT / "Assets" / "Plugins" / "iOS" / "BadgeArtwork"
MANIFEST = ARTWORK / "badge-b8-manifest.json"
EXPECTED_COUNT = 40
VISIBLE_FRACTION = 0.74
ALPHA_THRESHOLD = 16


def png_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("invalid PNG signature")
    chunks: list[tuple[bytes, bytes]] = []
    offset = 8
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        chunks.append((chunk_type, payload))
        offset += length + 12
        if chunk_type == b"IEND":
            break
    return chunks


def validate() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == 2
    assert manifest["visualLanguage"] == "b9.2-reference-proportioned-satin-relief"
    assert manifest["canvas"] == {
        "width": 1024,
        "height": 1024,
        "colorSpace": "sRGB",
        "transparent": True,
    }
    assert manifest["frameShapes"] == ["verticalPointRoundedHexagon"]
    assert manifest["iconLayout"] == {
        "slot": "square",
        "fit": "longest-side-aspect-fit",
        "visibleFraction": VISIBLE_FRACTION,
        "alphaThreshold": ALPHA_THRESHOLD,
        "preserveAspectRatio": True,
        "circlePrimitive": "equal-diameter",
    }
    assert manifest["runtimeTypography"]["maximumLines"] == 2
    assert manifest["runtimeTypography"]["placement"] == "outside-badge"
    assert manifest["runtimeTypography"]["line"] == [
        "shortName", "displayToken"]
    assert manifest["iconMaterial"] == {
        "face": "satin-pearl-silver",
        "depth": "soft-dark-lavender-sidewall",
        "bevel": "continuous-rounded-manufactured-edge",
        "lighting": "top-left-softbox",
    }

    assets = manifest["assets"]
    assert len(assets) == EXPECTED_COUNT
    assert len({item["id"] for item in assets}) == EXPECTED_COUNT
    assert len({item["assetName"] for item in assets}) == EXPECTED_COUNT

    expected_pngs = {item["png"] for item in assets}
    expected_svgs = {item["svg"] for item in assets}
    actual_pngs = {path.name for path in ARTWORK.glob("badge-b8-*.png")}
    actual_svgs = {path.name for path in ARTWORK.glob("badge-b8-*.svg")}
    assert actual_pngs == expected_pngs
    assert actual_svgs == expected_svgs

    speed_svg = (
        ARTWORK / "badge-b8-toy-technique-speed.svg"
    ).read_text(encoding="utf-8")
    assert "M53 109C35 92 35 63 53 47" in speed_svg, (
        "SPEED reference-matched rounded arc is missing"
    )
    assert "rotate(180 80 80)" in speed_svg, (
        "SPEED paired arcs must remain exactly rotationally symmetric"
    )
    assert "M57 117L103 43" in speed_svg, (
        "SPEED central diagonal slash is missing"
    )

    for item in assets:
        assert item["displayToken"].strip()
        assert item["shortName"].strip()

        svg_path = ARTWORK / item["svg"]
        svg_text = svg_path.read_text(encoding="utf-8")
        root = ET.fromstring(svg_text)
        assert root.tag.endswith("svg")
        assert root.attrib.get("viewBox") == "0 0 160 160"
        assert not any(element.tag.endswith("text") for element in root.iter()), (
            f"runtime typography must not be baked into {svg_path.name}"
        )
        assert not any(element.tag.endswith("ellipse") for element in root.iter()), (
            f"circular primitives must use one equal diameter in {svg_path.name}"
        )
        assert ".plateDepth" in svg_text, (
            f"3D plate depth material definition is missing: {svg_path.name}"
        )
        assert ".plateBevel" in svg_text and ".plateSheen" in svg_text, (
            f"satin plate bevel material is missing: {svg_path.name}"
        )
        assert all(marker in svg_text for marker in (
            ".tubeDepth", ".tubeBevel", ".tubeSheen")), (
            f"3D tube depth and bevel material is missing: {svg_path.name}"
        )
        assert "stroke-width:22" in svg_text and "opacity:.07" in svg_text, (
            f"restrained diffuse tube bloom definition is missing: {svg_path.name}"
        )
        assert "translate(3.2px,3.8px)" in svg_text, (
            f"visible manufactured icon extrusion is missing: {svg_path.name}"
        )
        assert "filter:url(#iconShadow)" in svg_text, (
            f"soft cast shadow definition is missing: {svg_path.name}"
        )

        png_path = ARTWORK / item["png"]
        chunks = png_chunks(png_path.read_bytes())
        chunk_types = [chunk_type for chunk_type, _ in chunks]
        assert b"sRGB" in chunk_types, f"missing sRGB chunk: {png_path.name}"
        ihdr = next(payload for chunk_type, payload in chunks if chunk_type == b"IHDR")
        width, height, bit_depth, color_type = struct.unpack(">IIBB", ihdr[:10])
        assert (width, height) == (1024, 1024)
        assert bit_depth == 8
        assert color_type in (4, 6), f"missing alpha channel: {png_path.name}"

        image = Image.open(png_path).convert("RGBA")
        alpha = image.getchannel("A")
        mask = alpha.point(
            lambda value: 255 if value >= ALPHA_THRESHOLD else 0)
        bounds = mask.getbbox()
        assert bounds is not None, f"empty artwork: {png_path.name}"
        left, top, right, bottom = bounds
        visible_width = right - left
        visible_height = bottom - top
        target = round(1024 * VISIBLE_FRACTION)
        assert abs(max(visible_width, visible_height) - target) <= 4, (
            f"longest side is not normalized: {png_path.name} "
            f"{visible_width}×{visible_height}"
        )
        assert abs((left + right) * 0.5 - 512) <= 2, (
            f"artwork is not horizontally centered: {png_path.name}"
        )
        assert abs((top + bottom) * 0.5 - 512) <= 2, (
            f"artwork is not vertically centered: {png_path.name}"
        )

    print(
        f"Validated {EXPECTED_COUNT} B8 SVG/PNG pairs: "
        "1024×1024, transparent, sRGB, text-free, "
        "longest-side aspect-fit artwork."
    )


if __name__ == "__main__":
    validate()
