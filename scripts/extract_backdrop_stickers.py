#!/usr/bin/env python3
"""Extract high-resolution white backdrop stickers from IMG_5837.PNG.

The crop rectangles are authored against the 946 x 2048 display-space preview
provided with the task, then scaled to the original source dimensions. Each
result is cleaned into a white-on-alpha, square 1024 px Unity texture. Potrace
is used to create a true vector SVG from the cleaned mask.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


PREVIEW_SIZE = (946, 2048)
OUTPUT_SIZE = 1024
ARTWORK_SPAN = 832


@dataclass(frozen=True)
class Sticker:
    name: str
    title: str
    preview_box: tuple[int, int, int, int]


# Only stickers whose full silhouette is visible in the source photograph.
# The rectangles intentionally leave a little dark-panel padding around each.
STICKERS = (
    Sticker("01-polygon-cube", "Polygon cube", (201, 85, 265, 143)),
    Sticker("02-hw-studio", "HW Studio badge", (576, 62, 657, 143)),
    Sticker("03-top-right-monogram", "Top-right monogram", (844, 86, 920, 154)),
    Sticker("04-rabbit-hand", "Rabbit hand", (244, 196, 309, 277)),
    Sticker("05-wawu-word", "WAWU wordmark", (18, 255, 126, 322)),
    Sticker("06-round-mascot", "Round mascot", (171, 286, 253, 379)),
    Sticker("07-nck-word", "NCK wordmark", (610, 210, 696, 287)),
    Sticker("08-geeone", "GEEONE badge", (326, 225, 608, 365)),
    Sticker("09-tiger-head", "Tiger head", (774, 267, 867, 370)),
    Sticker("10-meteor", "Meteor", (660, 331, 767, 433)),
    Sticker("11-mackie", "Mackie badge", (77, 356, 168, 447)),
    Sticker("12-turci-word", "Turci wordmark", (207, 399, 363, 500)),
    Sticker("13-astronaut", "Astronaut helmet", (804, 404, 902, 502)),
    Sticker("14-target", "Concentric target", (13, 432, 91, 528)),
    Sticker("15-knot", "Angular knot", (129, 472, 220, 565)),
    Sticker("16-flame-leaf", "Flame leaf", (722, 461, 815, 565)),
    Sticker("17-chemy-word", "CHEMY wordmark", (22, 524, 162, 616)),
    Sticker("18-emoji-face", "Emoji face", (287, 524, 382, 629)),
    Sticker("19-box-t", "Boxed T", (187, 578, 270, 685)),
    Sticker("20-warning-triangle", "Warning triangle", (824, 503, 930, 619)),
    Sticker("21-triple-stroke", "Triple stroke", (698, 589, 823, 690)),
    Sticker("22-section-s", "Section S", (835, 644, 925, 758)),
    Sticker("23-fierce-head", "Fierce head", (90, 678, 182, 781)),
    Sticker("24-round-chinese", "Round Chinese seal", (20, 721, 93, 807)),
)


OCCLUDED_OR_CROPPED = (
    "Top-left coil/bed symbol: covered by the phone status bar",
    "Head/brain badge near the top: covered by the app navigation labels",
    "Left organic badge: covered by the app menu and navigation labels",
    "Round double-slot badge: covered by the app navigation labels",
    "Angular box mark above GEEONE: covered by app navigation labels",
    "Upper-right Kego-style wordmark: covered by app navigation labels",
    "Long angular mark below it: covered by app navigation labels",
    "Wordmark behind the woman's hair at center-right",
    "Gift-box badge behind the woman's hair/shoulder",
    "Lower center-right badge behind the woman and foreground display",
    "Ruler fragment at the left frame edge",
    "DS6-style badge behind the foreground display",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--png-dir", type=Path, required=True)
    parser.add_argument("--svg-dir", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--ai-reference", type=Path)
    return parser.parse_args()


def source_box(sticker: Sticker, size: tuple[int, int]) -> tuple[int, int, int, int]:
    sx = size[0] / PREVIEW_SIZE[0]
    sy = size[1] / PREVIEW_SIZE[1]
    x0, y0, x1, y1 = sticker.preview_box
    return tuple(
        int(round(value * (sx if index % 2 == 0 else sy)))
        for index, value in enumerate((x0, y0, x1, y1))
    )


def clean_mask(crop_rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    gray = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2GRAY)
    smooth = cv2.GaussianBlur(gray, (0, 0), 0.75)

    raw = np.where(smooth >= 42, 255, 0).astype(np.uint8)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, 8)
    keep = np.zeros_like(raw)
    height, width = raw.shape
    minimum_area = max(18, int(raw.size * 0.0004))

    for label in range(1, count):
        x, y, w, h, area = stats[label]
        if area < minimum_area:
            continue
        cx, cy = centroids[label]
        central = abs(cx - width / 2) <= width * 0.49 and abs(cy - height / 2) <= height * 0.49
        substantial = area >= raw.size * 0.002
        touches_edge = x <= 1 or y <= 1 or x + w >= width - 1 or y + h >= height - 1
        edge_rule = substantial and central and not (w >= h * 4 and touches_edge)
        if touches_edge and not edge_rule:
            continue
        if central or substantial:
            keep[labels == label] = 255

    if not np.any(keep):
        raise RuntimeError("No sticker pixels survived the cleanup mask")

    support = cv2.dilate(keep, np.ones((5, 5), np.uint8), iterations=1)
    alpha = np.clip((smooth.astype(np.float32) - 24.0) * (255.0 / 116.0), 0, 255)
    alpha = np.where(support > 0, alpha, 0).astype(np.uint8)
    alpha[keep > 0] = np.maximum(alpha[keep > 0], 110)
    peak = float(np.percentile(alpha[keep > 0], 99.0))
    if 0 < peak < 255:
        alpha = np.clip(alpha.astype(np.float32) * (255.0 / peak), 0, 255).astype(np.uint8)
    return alpha, keep


def square_asset(alpha: np.ndarray, binary: np.ndarray) -> tuple[Image.Image, Image.Image]:
    ys, xs = np.where(binary > 0)
    x0, x1 = max(0, xs.min() - 3), min(binary.shape[1], xs.max() + 4)
    y0, y1 = max(0, ys.min() - 3), min(binary.shape[0], ys.max() + 4)

    alpha_crop = Image.fromarray(alpha[y0:y1, x0:x1])
    binary_crop = Image.fromarray(binary[y0:y1, x0:x1])
    scale = ARTWORK_SPAN / max(alpha_crop.size)
    resized = (
        max(1, int(round(alpha_crop.width * scale))),
        max(1, int(round(alpha_crop.height * scale))),
    )
    alpha_crop = alpha_crop.resize(resized, Image.Resampling.LANCZOS)
    binary_crop = binary_crop.resize(resized, Image.Resampling.LANCZOS)

    alpha_square = Image.new("L", (OUTPUT_SIZE, OUTPUT_SIZE), 0)
    binary_square = Image.new("L", (OUTPUT_SIZE, OUTPUT_SIZE), 0)
    offset = ((OUTPUT_SIZE - resized[0]) // 2, (OUTPUT_SIZE - resized[1]) // 2)
    alpha_square.paste(alpha_crop, offset)
    binary_square.paste(binary_crop, offset)

    rgba = Image.new("RGBA", (OUTPUT_SIZE, OUTPUT_SIZE), (255, 255, 255, 0))
    rgba.putalpha(alpha_square)
    traced = binary_square.point(lambda value: 255 if value >= 128 else 0, mode="1")
    return rgba, traced


def trace_svg(binary: Image.Image, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="backdrop-sticker-") as temp_dir:
        pbm = Path(temp_dir) / "mask.pbm"
        # Potrace traces black pixels, so invert the white foreground mask.
        inverted = Image.eval(binary.convert("L"), lambda value: 255 - value).convert("1")
        inverted.save(pbm)
        subprocess.run(
            [
                "potrace",
                "--svg",
                "--flat",
                "--turdsize",
                "6",
                "--alphamax",
                "1.0",
                "--opttolerance",
                "0.2",
                "--width",
                "1024pt",
                "--height",
                "1024pt",
                "--color",
                "#ffffff",
                "--output",
                str(destination),
                str(pbm),
            ],
            check=True,
        )


def make_contact_sheet(entries: list[dict], png_dir: Path, destination: Path) -> None:
    columns, rows = 4, 6
    cell = 360
    header = 52
    sheet = Image.new("RGB", (columns * cell, rows * cell), (12, 12, 14))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=18)
    checker = Image.new("RGB", (cell - 32, cell - header - 18), (34, 34, 38))
    checker_draw = ImageDraw.Draw(checker)
    tile = 24
    for y in range(0, checker.height, tile):
        for x in range(0, checker.width, tile):
            if (x // tile + y // tile) % 2:
                checker_draw.rectangle((x, y, x + tile - 1, y + tile - 1), fill=(43, 43, 48))

    for index, entry in enumerate(entries):
        col, row = index % columns, index // columns
        ox, oy = col * cell, row * cell
        draw.text((ox + 16, oy + 16), entry["title"], fill=(240, 240, 244), font=font)
        sheet.paste(checker, (ox + 16, oy + header))
        asset = Image.open(png_dir / entry["png"]).convert("RGBA")
        asset.thumbnail((checker.width - 20, checker.height - 20), Image.Resampling.LANCZOS)
        px = ox + 16 + (checker.width - asset.width) // 2
        py = oy + header + (checker.height - asset.height) // 2
        sheet.paste(asset, (px, py), asset)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, optimize=True)


def main() -> None:
    args = parse_args()
    args.png_dir.mkdir(parents=True, exist_ok=True)
    args.svg_dir.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    reference_dir = args.artifact_dir / "Reference"
    reference_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(args.source, reference_dir / "IMG_5837-source.PNG")
    if args.ai_reference and args.ai_reference.exists():
        shutil.copy2(args.ai_reference, reference_dir / "IMG_5837-clean-reference-AI.png")

    source = Image.open(args.source).convert("RGB")
    entries: list[dict] = []
    for sticker in STICKERS:
        box = source_box(sticker, source.size)
        crop = np.asarray(source.crop(box))
        try:
            alpha, binary = clean_mask(crop)
        except RuntimeError as error:
            raise RuntimeError(f"{sticker.name}: {error}") from error
        rgba, trace_mask = square_asset(alpha, binary)

        png_name = f"{sticker.name}.png"
        svg_name = f"{sticker.name}.svg"
        rgba.save(args.png_dir / png_name, optimize=True)
        trace_svg(trace_mask, args.svg_dir / svg_name)
        entries.append(
            {
                "id": sticker.name,
                "title": sticker.title,
                "classification": "source-exact-visible",
                "preview_box_946x2048": list(sticker.preview_box),
                "source_box": list(box),
                "png": png_name,
                "svg": svg_name,
                "canvas": [OUTPUT_SIZE, OUTPUT_SIZE],
            }
        )

    contact_name = "backdrop-stickers-contact-sheet.png"
    make_contact_sheet(entries, args.png_dir, args.artifact_dir / contact_name)
    manifest = {
        "generated": date.today().isoformat(),
        "source": str(args.source),
        "source_dimensions": list(source.size),
        "output": {
            "png_directory": str(args.png_dir),
            "svg_directory": str(args.svg_dir),
            "contact_sheet": contact_name,
            "count": len(entries),
            "format": "1024x1024 transparent white RGBA PNG plus traced SVG",
        },
        "method": (
            "Manual source-accurate crops, luminance/connected-component cleanup, "
            "Lanczos alpha upscaling, and Potrace vector tracing."
        ),
        "ai_reference_policy": (
            "The AI-cleaned backdrop is preserved only as a reconstruction reference; "
            "none of its invented or altered marks were used in production assets."
        ),
        "stickers": entries,
        "not_exported_because_occluded_or_cropped": list(OCCLUDED_OR_CROPPED),
    }
    (args.artifact_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"Extracted {len(entries)} stickers")
    print(f"PNG: {args.png_dir}")
    print(f"SVG: {args.svg_dir}")
    print(f"Preview: {args.artifact_dir / contact_name}")


if __name__ == "__main__":
    main()
