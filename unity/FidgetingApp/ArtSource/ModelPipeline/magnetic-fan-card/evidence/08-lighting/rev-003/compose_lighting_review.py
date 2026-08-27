"""Compose 72-segment Cycles lighting review boards."""

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


def board(
    output: str,
    title: str,
    subtitle: str,
    panels: tuple[tuple[str, str], ...],
) -> None:
    columns = len(panels)
    canvas = Image.new("RGB", (columns * 650 + 40, 760), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20), title, font=font(32, "Bold"), fill=(237, 224, 199))
    draw.text(
        (30, 60), subtitle, font=font(17, "Regular"), fill=(155, 158, 162))
    for index, (name, label) in enumerate(panels):
        x = 20 + index * 650
        y = 100
        draw.rounded_rectangle(
            (x, y, x + 630, y + 630),
            radius=18,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(HERE / name, (600, 540)), (x + 15, y + 15))
        draw.text(
            (x + 22, y + 576),
            label,
            font=font(18, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 22, y + 606),
            "72 visible segments / quadrant",
            font=font(14, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / output)


def main() -> None:
    board(
        "lighting-hero-contact-sheet.png",
        "GATE 08 · 72-SEGMENT SHARED LIGHT",
        "5000 K / 350 mm key, 5:1 key-to-fill, 80 mm / 32° camera; material recipes unchanged.",
        (
            ("hero-A-dark-walnut.png", "DARK WALNUT"),
            ("hero-B-charcoal-hard-case.png", "CHARCOAL"),
            ("hero-C-cork-slab.png", "CORK"),
        ),
    )
    board(
        "lighting-angle-contact-sheet.png",
        "GATE 08 · ANGLE RESPONSE",
        "Grazing highlights verify smoother corners without changing thickness or layer gaps.",
        (
            ("left-oblique.png", "LEFT"),
            ("right-oblique.png", "RIGHT"),
            ("top-oblique.png", "TOP"),
            ("low-angle.png", "LOW"),
        ),
    )
    board(
        "lighting-pass-contact-sheet.png",
        "GATE 08 · DIAGNOSTIC PASSES",
        "Beauty, clay, normal, depth and roughness isolate topology and surface response.",
        (
            ("hero-B-charcoal-hard-case.png", "BEAUTY"),
            ("pass-clay.png", "CLAY"),
            ("pass-normal.png", "NORMAL"),
            ("pass-depth.png", "DEPTH"),
            ("pass-roughness.png", "ROUGHNESS"),
        ),
    )


if __name__ == "__main__":
    main()
