#!/usr/bin/env python3
"""Normalize visible Badge artwork into one square, aspect-fit safe frame."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, PngImagePlugin


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIRECTORY = ROOT / "Assets" / "Plugins" / "iOS" / "BadgeArtwork"
CANVAS_SIZE = 1024
DEFAULT_VISIBLE_FRACTION = 0.74
DEFAULT_ALPHA_THRESHOLD = 16


def visible_bounds(image: Image.Image, threshold: int) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value >= threshold else 0)
    bounds = mask.getbbox()
    if bounds is None:
        raise ValueError("artwork has no visible pixels")
    return bounds


def normalize(path: Path, visible_fraction: float, threshold: int) -> tuple[int, int]:
    source = Image.open(path).convert("RGBA")
    if source.size != (CANVAS_SIZE, CANVAS_SIZE):
        raise ValueError(f"{path.name} must be {CANVAS_SIZE}×{CANVAS_SIZE}")

    left, top, right, bottom = visible_bounds(source, threshold)
    visible_width = right - left
    visible_height = bottom - top
    longest_side = max(visible_width, visible_height)
    target = round(CANVAS_SIZE * visible_fraction)
    center_x = (left + right) * 0.5
    center_y = (top + bottom) * 0.5
    if (
        abs(longest_side - target) <= 4
        and abs(center_x - CANVAS_SIZE * 0.5) <= 2
        and abs(center_y - CANVAS_SIZE * 0.5) <= 2
    ):
        return visible_width, visible_height
    scale = target / longest_side

    # One uniform scale preserves the source aspect ratio and therefore cannot
    # turn a circle into an ellipse. The visible center, not the raw transparent
    # canvas center, is mapped to the center of the shared 1:1 slot.
    resized_size = max(1, round(CANVAS_SIZE * scale))
    resized = source.resize(
        (resized_size, resized_size),
        resample=Image.Resampling.LANCZOS)
    visible_center_x = (left + right) * 0.5 * scale
    visible_center_y = (top + bottom) * 0.5 * scale
    destination_x = round(CANVAS_SIZE * 0.5 - visible_center_x)
    destination_y = round(CANVAS_SIZE * 0.5 - visible_center_y)

    normalized = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    normalized.alpha_composite(resized, dest=(destination_x, destination_y))

    png_info = PngImagePlugin.PngInfo()
    png_info.add(b"sRGB", b"\x00")
    temporary = path.with_name(path.stem + ".normalized.tmp.png")
    normalized.save(temporary, format="PNG", pnginfo=png_info, optimize=True)
    temporary.replace(path)

    new_left, new_top, new_right, new_bottom = visible_bounds(normalized, threshold)
    return new_right - new_left, new_bottom - new_top


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=DEFAULT_DIRECTORY)
    parser.add_argument(
        "--visible-fraction",
        type=float,
        default=DEFAULT_VISIBLE_FRACTION)
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=DEFAULT_ALPHA_THRESHOLD)
    args = parser.parse_args()

    if not 0 < args.visible_fraction <= 1:
        raise ValueError("visible fraction must be in (0, 1]")
    if not 1 <= args.alpha_threshold <= 255:
        raise ValueError("alpha threshold must be in [1, 255]")

    paths = sorted(args.directory.glob("badge-b8-*.png"))
    if not paths:
        raise FileNotFoundError(f"no Badge PNGs found in {args.directory}")

    for path in paths:
        width, height = normalize(
            path,
            args.visible_fraction,
            args.alpha_threshold)
        print(f"{path.name}: visible={width}×{height}")

    print(
        f"normalized_badges={len(paths)} canvas={CANVAS_SIZE} "
        f"visible_fraction={args.visible_fraction:.2f} "
        f"fit=longest-side-aspect-fit")


if __name__ == "__main__":
    main()
