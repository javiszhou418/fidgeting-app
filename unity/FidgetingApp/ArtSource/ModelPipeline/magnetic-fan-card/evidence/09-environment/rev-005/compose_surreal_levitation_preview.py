"""Grade and typeset the surreal levitation preview without 2D particles."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


HERE = Path(__file__).resolve().parent
REV4 = HERE.parent / "rev-004"
RAW = HERE / "surreal-levitation-preview.png"
OUTPUT = HERE / "surreal-levitation-banner.png"
BOARD = HERE / "card-rain-vs-surreal-levitation.png"
FONT = "/System/Library/Fonts/SFNS.ttf"
COMPACT = "/System/Library/Fonts/SFCompact.ttf"


def font(path: str, size: int, variation: str):
    value = ImageFont.truetype(path, size)
    try:
        value.set_variation_by_name(variation)
    except OSError:
        pass
    return value


def tracked_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    value: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    tracking: int,
) -> None:
    x, y = position
    for character in text:
        draw.text((x, y), character, font=value, fill=fill)
        x += round(draw.textlength(character, font=value)) + tracking


def add_copy(image: Image.Image) -> Image.Image:
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = shade.load()
    for x in range(min(image.width, 470)):
        alpha = round(68 * max(0.0, 1.0 - x / 470) ** 1.65)
        for y in range(image.height):
            pixels[x, y] = (12, 5, 2, alpha)
    image = Image.alpha_composite(image.convert("RGBA"), shade)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (50, 122, 142, 148),
        radius=5,
        fill=(192, 151, 72, 255),
    )
    tracked_text(
        draw,
        (61, 128),
        "FEATURED",
        font(COMPACT, 11, "Semibold"),
        (28, 21, 13, 255),
        1,
    )
    draw.text(
        (50, 168),
        "MAGNETIC FAN CARD",
        font=font(FONT, 35, "Semibold"),
        fill=(242, 229, 204, 255),
        stroke_width=1,
        stroke_fill=(47, 24, 15, 120),
    )
    return Image.alpha_composite(image, layer)


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (13, 12, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    image = Image.open(RAW).convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Color(image).enhance(1.16)
    image = ImageEnhance.Brightness(image).enhance(0.88)
    image = add_copy(image)
    image.convert("RGB").save(OUTPUT, quality=100)

    canvas = Image.new("RGB", (1880, 700), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (34, 24),
        "APPROVED CARD RAIN → SURREAL LEVITATION",
        font=font(FONT, 34, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (34, 67),
        "Same locked product. Rev 5 adds a 14 mm lift, physical shadow, underlight, open 3D ribbons, and denser depth particles.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    panels = (
        (
            REV4 / "card-rain-final-banner.png",
            "APPROVED BASE · GROUNDED CARD RAIN",
        ),
        (OUTPUT, "REV 5 · SURREAL LEVITATION"),
    )
    for index, (path, title) in enumerate(panels):
        x = 24 + index * 925
        y = 108
        draw.rounded_rectangle(
            (x, y, x + 900, y + 560),
            radius=20,
            fill=(22, 20, 18),
            outline=(98, 74, 39),
            width=2,
        )
        canvas.paste(fit(path, (872, 484)), (x + 14, y + 14))
        draw.text(
            (x + 22, y + 510),
            title,
            font=font(FONT, 19, "Bold"),
            fill=(226, 178, 82),
        )
    canvas.save(BOARD)

    render_report = json.loads(
        (HERE / "surreal-levitation-report.json").read_text(encoding="utf-8"))
    (HERE / "surreal-levitation-composite-report.json").write_text(
        json.dumps({
            "source": RAW.name,
            "output": OUTPUT.name,
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "screenSpaceParticles": 0,
            "render": render_report,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
