#!/usr/bin/env python3

"""Trim and center one black-on-white sticker mask deterministically."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


TRACE_SIZE = 256
ARTWORK_SPAN = 208
PNG_SIZE = 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--trace-mask", required=True, type=Path)
    parser.add_argument("--png", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Image.open(args.source).convert("L")
    foreground = ImageOps.invert(source)
    bbox = foreground.getbbox()
    if bbox is None:
        raise ValueError(f"Sticker mask has no foreground: {args.source}")

    cropped = foreground.crop(bbox)
    scale = ARTWORK_SPAN / max(cropped.size)
    # Even dimensions share the half-pixel center of the even-sized canvas.
    # This keeps both the raster and potraced vector geometrically centered.
    resized_size = tuple(
        max(2, 2 * round(dimension * scale / 2)) for dimension in cropped.size
    )
    resized = cropped.resize(resized_size, Image.Resampling.LANCZOS)

    centered_foreground = Image.new("L", (TRACE_SIZE, TRACE_SIZE), 0)
    paste_position = tuple(
        (TRACE_SIZE - dimension) // 2 for dimension in resized.size
    )
    centered_foreground.paste(resized, paste_position)

    args.trace_mask.parent.mkdir(parents=True, exist_ok=True)
    args.png.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.invert(centered_foreground).save(args.trace_mask)

    alpha = centered_foreground.resize(
        (PNG_SIZE, PNG_SIZE),
        Image.Resampling.LANCZOS,
    )
    white = Image.new("L", alpha.size, 255)
    transparent_white = Image.merge("RGBA", (white, white, white, alpha))
    transparent_white.save(args.png, optimize=True)


if __name__ == "__main__":
    main()
