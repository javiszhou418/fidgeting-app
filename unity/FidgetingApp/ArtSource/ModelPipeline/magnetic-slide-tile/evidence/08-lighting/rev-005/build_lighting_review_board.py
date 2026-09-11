#!/usr/bin/env python3
"""Assemble Gate 08 rev 5 supplementary review boards."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ENTRIES = [
    ("hero.png", "Hero · closed 0°"),
    ("left-oblique.png", "Left oblique"),
    ("right-oblique.png", "Right oblique"),
    ("low.png", "Low angle"),
    ("pass-beauty.png", "Beauty"),
    ("pass-clay.png", "Clay"),
    ("pass-normal.png", "Camera normal"),
    ("pass-depth.png", "Camera depth"),
    ("pass-roughness.png", "Roughness"),
    ("legal-mid-slide-0.png", "Intermediate slide · 0° only"),
    ("blender-full-model-display.png", "Blender · shared HDR"),
    ("unity-full-model-display.png", "Unity · shared HDR"),
]
CELL = (700, 550)
LABEL = 58
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)


def main():
    board = Image.new("RGB", (CELL[0] * 3, (CELL[1] + LABEL) * 4), (24, 24, 24))
    for index, (name, title) in enumerate(ENTRIES):
        source = Image.open(HERE / name).convert("RGB")
        source.thumbnail(CELL, Image.Resampling.LANCZOS)
        panel = Image.new("RGB", (CELL[0], CELL[1] + LABEL), (24, 24, 24))
        panel.paste(source, ((CELL[0] - source.width) // 2, LABEL + (CELL[1] - source.height) // 2))
        ImageDraw.Draw(panel).text((20, 14), title, font=FONT, fill=(238, 238, 238))
        board.paste(panel, ((index % 3) * CELL[0], (index // 3) * (CELL[1] + LABEL)))
    board.save(HERE / "gate08-r005-lighting-review-board.png")
    comparison = Image.new("RGB", (1400 * 2, 1100 + LABEL), (24, 24, 24))
    for index, (name, title) in enumerate([
        ("blender-full-model-display.png", "Blender · shared HDR · neutral-display-v1"),
        ("unity-full-model-display.png", "Unity URP · same HDR · neutral-display-v1"),
    ]):
        comparison.paste(Image.open(HERE / name).convert("RGB"), (index * 1400, LABEL))
        ImageDraw.Draw(comparison).text((index * 1400 + 24, 14), title, font=FONT, fill=(238, 238, 238))
    comparison.save(HERE / "gate08-r005-blender-unity-comparison.png")
    print(HERE / "gate08-r005-lighting-review-board.png")
    print(HERE / "gate08-r005-blender-unity-comparison.png")


if __name__ == "__main__":
    main()
