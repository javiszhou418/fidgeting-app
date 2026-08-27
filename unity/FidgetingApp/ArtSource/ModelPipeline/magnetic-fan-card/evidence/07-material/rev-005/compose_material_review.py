"""Compose the 72-segment material revalidation board."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/SFNS.ttf"


def font(size: int, variation: str):
    value = ImageFont.truetype(FONT, size)
    try:
        value.set_variation_by_name(variation)
    except OSError:
        pass
    return value


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (9, 10, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    canvas = Image.new("RGB", (2600, 820), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 07 · 72-SEGMENT MATERIAL REVALIDATION",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "Warm silver medium bead-blast, gunmetal, black etching, chrome cap, and warm-gold bevel are unchanged.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        ("exact-A-dark-walnut.png", "DARK WALNUT"),
        ("exact-B-charcoal-hard-case.png", "CHARCOAL HARD CASE"),
        ("exact-C-cork-slab.png", "CORK SLAB"),
        ("exact-material-closeup.png", "72-SEGMENT MATERIAL CLOSEUP"),
    )
    for index, (name, label) in enumerate(panels):
        x = 20 + index * 645
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 625, y + 680),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(HERE / name, (595, 580)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 616),
            label,
            font=font(18, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 648),
            "72 visible segments / quadrant",
            font=font(15, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / "material-contact-sheet.png")


if __name__ == "__main__":
    main()
