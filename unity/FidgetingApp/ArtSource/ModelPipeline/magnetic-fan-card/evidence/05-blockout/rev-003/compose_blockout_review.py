"""Compose the selected 72-segment white-model review."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
CONTRACT = HERE.parents[1] / "03-contract/rev-007/corner-72-selected.png"
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
    canvas = Image.new("RGB", (2600, 790), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 05 · 72-SEGMENT WHITE MODEL",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "Same 3.5 mm / 9.5 mm / 1.0 mm / 0.8 mm stack and 80 mm / 32° composition; only visible corner density changes.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        ("blockout-A-dark-walnut.png", "A · DARK WALNUT ID"),
        ("blockout-B-charcoal-hard-case.png", "B · CHARCOAL ID"),
        ("blockout-C-cork-slab.png", "C · CORK ID"),
    )
    for index, (name, label) in enumerate(panels):
        x = 20 + index * 650
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 630, y + 650),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(HERE / name, (600, 550)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 588),
            label,
            font=font(19, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 620),
            "72 visible segments / quadrant",
            font=font(15, "Regular"),
            fill=(184, 184, 180),
        )
    inset_x = 1980
    draw.rounded_rectangle(
        (inset_x, 105, inset_x + 595, 755),
        radius=20,
        fill=(20, 21, 23),
        outline=(223, 174, 78),
        width=3,
    )
    canvas.paste(fit(CONTRACT, (565, 550)), (inset_x + 15, 120))
    draw.text(
        (inset_x + 24, 693),
        "SELECTED CORNER CLOSEUP",
        font=font(19, "Bold"),
        fill=(223, 174, 78),
    )
    draw.text(
        (inset_x + 24, 725),
        "collision remains 8 / quadrant",
        font=font(15, "Regular"),
        fill=(184, 184, 180),
    )
    canvas.save(HERE / "blockout-contact-sheet.png")


if __name__ == "__main__":
    main()
