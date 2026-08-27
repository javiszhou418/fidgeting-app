"""Grade, add controlled FX, and typeset the three high-roller styleframes."""

from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
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


def allowed_particle(rng: random.Random) -> tuple[int, int]:
    zones = (
        (180, 500, 28, 122),
        (210, 520, 270, 620),
        (1080, 1170, 40, 600),
        (395, 535, 255, 455),
    )
    x0, x1, y0, y1 = rng.choice(zones)
    return rng.randint(x0, x1), rng.randint(y0, y1)


def add_fx(image: Image.Image, density: int, seed: int) -> Image.Image:
    rng = random.Random(seed)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for index in range(density):
        x, y = allowed_particle(rng)
        radius = rng.choice((1, 1, 2, 2, 3))
        alpha = rng.randint(95, 220)
        color = (
            rng.randint(218, 255),
            rng.randint(137, 194),
            rng.randint(38, 78),
            alpha,
        )
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=color,
        )
        if index % 7 == 0:
            size = rng.randint(3, 7)
            draw.polygon(
                ((x, y - size), (x + size, y), (x, y + size), (x - size, y)),
                fill=(238, 168, 63, max(70, alpha - 55)),
            )

    blur = Image.new("RGBA", image.size, (0, 0, 0, 0))
    blur_draw = ImageDraw.Draw(blur)
    for _ in range(max(2, density // 14)):
        x, y = allowed_particle(rng)
        radius = rng.randint(8, 18)
        blur_draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(255, 151, 45, rng.randint(25, 60)),
        )
    blur = blur.filter(ImageFilter.GaussianBlur(9))
    result = Image.alpha_composite(image.convert("RGBA"), blur)
    return Image.alpha_composite(result, layer)


def add_copy(image: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (64, 145, 168, 174),
        radius=5,
        fill=(190, 151, 75, 255),
    )
    tracked_text(
        draw,
        (77, 152),
        "FEATURED",
        font(COMPACT, 12, "Semibold"),
        (28, 21, 13, 255),
        1,
    )
    draw.text(
        (64, 191),
        "MAGNETIC FAN CARD",
        font=font(FONT, 35, "Semibold"),
        fill=(239, 227, 205, 255),
        stroke_width=1,
        stroke_fill=(52, 28, 18, 115),
    )
    return Image.alpha_composite(image.convert("RGBA"), layer)


def compose(source: str, output: str, density: int, seed: int) -> None:
    image = Image.open(HERE / source).convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.13)
    image = ImageEnhance.Color(image).enhance(1.09)
    image = ImageEnhance.Brightness(image).enhance(0.94)
    if density:
        image = add_fx(image, density, seed)
    image = add_copy(image)
    image.convert("RGB").save(HERE / output, quality=100)


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (13, 12, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def contact_sheet() -> None:
    width, height = 2130, 570
    canvas = Image.new("RGB", (width, height), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (28, 20),
        "ELECTRONIC HIGH-ROLLER · CONTROLLED ENERGY",
        font=font(FONT, 32, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (28, 60),
        "Same product, lens, table, and copy. Only foreground / FX density changes.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    items = (
        ("C1-grounded-luxury-banner.png", "C1 · GROUNDED", "one foreground chip · lowest FX"),
        ("C2-electronic-stage-banner.png", "C2 · BALANCED", "two chips · circuits · controlled gold dust"),
        ("C3-high-energy-banner.png", "C3 · HIGH ENERGY", "maximum bounded particles and props"),
    )
    for index, (path, title, subtitle) in enumerate(items):
        x = 20 + index * 700
        y = 98
        draw.rounded_rectangle(
            (x, y, x + 680, y + 448),
            radius=18,
            fill=(22, 20, 18),
            outline=(95, 72, 40),
            width=2,
        )
        canvas.paste(fit(HERE / path, (652, 362)), (x + 14, y + 14))
        draw.text(
            (x + 22, y + 385),
            title,
            font=font(FONT, 20, "Bold"),
            fill=(226, 178, 82),
        )
        draw.text(
            (x + 22, y + 416),
            subtitle,
            font=font(FONT, 15, "Regular"),
            fill=(188, 178, 164),
        )
    canvas.save(HERE / "electronic-high-roller-styleframe-contact-sheet.png")


def main() -> None:
    compose(
        "C1-grounded-luxury.png",
        "C1-grounded-luxury-banner.png",
        0,
        101,
    )
    compose(
        "C2-electronic-stage.png",
        "C2-electronic-stage-banner.png",
        30,
        202,
    )
    compose(
        "C3-high-energy.png",
        "C3-high-energy-banner.png",
        68,
        303,
    )
    contact_sheet()
    (HERE / "styleframe-composite-report.json").write_text(
        json.dumps({
            "productPixels": "deterministic grade only; no generative repaint",
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "goldOutline": False,
            "variants": {
                "C1": {"compositeParticleCount": 0},
                "C2": {"compositeParticleCount": 30},
                "C3": {"compositeParticleCount": 68},
            },
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
