"""Assemble the seven Gate 12 shipping views of one revision into a single contact sheet.

Usage: python3 build_geeone_shipping_contact_sheet.py <rev-dir> [<title>]

Reads shipping-phone / hero / top / left-oblique / right-oblique / low / library PNGs written by
GeeoneShippingPreviewCapture and writes shipping-review-contact-sheet.png next to them. Pure layout; no
re-rendering, no colour changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

VIEWS = ["phone", "hero", "top", "left-oblique", "right-oblique", "low", "library"]
TILE_W = 400
PAD = 16
LABEL_H = 40


def main() -> None:
    rev_dir = Path(sys.argv[1]).resolve()
    title = sys.argv[2] if len(sys.argv) > 2 else rev_dir.name
    tiles = []
    for view in VIEWS:
        image = Image.open(rev_dir / f"shipping-{view}.png").convert("RGB")
        scale = TILE_W / image.width
        tiles.append((view, image.resize((TILE_W, round(image.height * scale)), Image.LANCZOS)))
    tile_h = max(t.height for _, t in tiles)
    sheet = Image.new("RGB", (PAD + len(tiles) * (TILE_W + PAD), PAD + LABEL_H + tile_h + PAD + LABEL_H), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    draw.text((PAD, PAD + 8), title, fill=(230, 230, 230))
    for index, (view, tile) in enumerate(tiles):
        x = PAD + index * (TILE_W + PAD)
        y = PAD + LABEL_H + (tile_h - tile.height) // 2
        sheet.paste(tile, (x, y))
        draw.text((x, PAD + LABEL_H + tile_h + PAD + 8), view, fill=(200, 200, 200))
    out = rev_dir / "shipping-review-contact-sheet.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
