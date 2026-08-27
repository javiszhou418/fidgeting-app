#!/usr/bin/env python3
"""Compose review sheets from the real Unity Collector Slab captures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / "Artifacts" / "PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview"
PRODUCTS = (
    ("pointed-three-blade", "EDGE TRIAD"),
    ("metal-three-blade", "MAGNETIC TRINITY"),
    ("gold-four-wing", "MIRROR QUAD"),
    ("graphite-two-lobe", "GRAPHITE DUO"),
    ("magnetic-slide-tile", "MAGNETIC SLIDE"),
    ("magnetic-fan-card", "MAGNETIC FAN"),
)


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def compose(
    filename: str,
    products: tuple[tuple[str, str], ...],
    views: tuple[str, ...],
    rows: int,
) -> None:
    cell_width, image_height, label_height = 420, 560, 42
    columns = 3
    canvas = Image.new(
        "RGB",
        (columns * cell_width, rows * (image_height + label_height)),
        (18, 18, 20),
    )
    draw = ImageDraw.Draw(canvas)
    label_font = font(21)
    for index, (product_id, display_name) in enumerate(products):
        for view_index, view in enumerate(views):
            slot = view_index * len(products) + index
            row, column = divmod(slot, columns)
            source = Image.open(PREVIEW / product_id / view).convert("RGB")
            source.thumbnail((cell_width, image_height), Image.Resampling.LANCZOS)
            x = column * cell_width + (cell_width - source.width) // 2
            y = row * (image_height + label_height)
            canvas.paste(source, (x, y))
            suffix = "HERO" if view == "01_hero.png" else "LEFT OBLIQUE"
            text = f"{display_name} · {suffix}"
            box = draw.textbbox((0, 0), text, font=label_font)
            text_width = box[2] - box[0]
            draw.text(
                (column * cell_width + (cell_width - text_width) / 2,
                 y + image_height + 8),
                text,
                fill=(220, 220, 216),
                font=label_font,
            )
    output = PREVIEW / filename
    canvas.save(output, optimize=True)
    print(output)


def main() -> None:
    compose(
        "collector-slab-all-products-shipping-final.png",
        PRODUCTS,
        ("01_hero.png",),
        2,
    )
    compose(
        "collector-slab-material-shipping-final.png",
        PRODUCTS[1:4],
        ("01_hero.png", "03_left_oblique.png"),
        2,
    )


if __name__ == "__main__":
    main()
