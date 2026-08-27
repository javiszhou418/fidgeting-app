"""Compose the selected high-resolution C2 Banner and comparison board."""

from __future__ import annotations

import colorsys
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageStat


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
RAW = HERE / "C2-final-raw-2x.png"
BASELINE = (
    REPO / "Artifacts/FanCardBannerConcept/"
    "fan-card-banner-blender-charcoal-preview.png"
)
FINAL_2X = HERE / "electronic-high-roller-C2-final-2x.png"
FINAL = HERE / "electronic-high-roller-C2-final-preview.png"
BOARD = HERE / "electronic-high-roller-final-comparison.png"
FONT = "/System/Library/Fonts/SFNS.ttf"
COMPACT = "/System/Library/Fonts/SFCompact.ttf"
SCALE = 2


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


def particle_position(rng: random.Random) -> tuple[int, int]:
    zones = (
        (180, 500, 28, 122),
        (210, 520, 270, 620),
        (1080, 1170, 40, 600),
        (395, 535, 255, 455),
    )
    x0, x1, y0, y1 = rng.choice(zones)
    return rng.randint(x0, x1) * SCALE, rng.randint(y0, y1) * SCALE


def add_particles(image: Image.Image) -> Image.Image:
    rng = random.Random(2026082502)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for index in range(30):
        x, y = particle_position(rng)
        radius = rng.choice((2, 2, 3, 4, 5))
        alpha = rng.randint(95, 210)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(
                rng.randint(220, 255),
                rng.randint(135, 190),
                rng.randint(35, 75),
                alpha,
            ),
        )
        if index % 7 == 0:
            size = rng.randint(6, 12)
            draw.polygon(
                ((x, y - size), (x + size, y), (x, y + size), (x - size, y)),
                fill=(238, 168, 63, max(70, alpha - 55)),
            )
    glow = layer.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(
        Image.alpha_composite(image.convert("RGBA"), glow), layer)


def add_copy(image: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (64 * SCALE, 145 * SCALE, 168 * SCALE, 174 * SCALE),
        radius=10,
        fill=(190, 151, 75, 255),
    )
    tracked_text(
        draw,
        (77 * SCALE, 152 * SCALE),
        "FEATURED",
        font(COMPACT, 24, "Semibold"),
        (28, 21, 13, 255),
        2,
    )
    draw.text(
        (64 * SCALE, 191 * SCALE),
        "MAGNETIC FAN CARD",
        font=font(FONT, 70, "Semibold"),
        fill=(239, 227, 205, 255),
        stroke_width=2,
        stroke_fill=(52, 28, 18, 115),
    )
    return Image.alpha_composite(image.convert("RGBA"), layer)


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (13, 12, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def image_metrics(path: Path) -> dict:
    image = Image.open(path).convert("RGB").resize((256, 256))
    pixels = list(image.getdata())
    hsv = [
        colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        for r, g, b in pixels
    ]
    values = sorted(value for _, _, value in hsv)
    return {
        "meanRgb": [round(value, 2) for value in ImageStat.Stat(image).mean],
        "meanValue": round(sum(value for _, _, value in hsv) / len(hsv), 4),
        "meanSaturation": round(
            sum(saturation for _, saturation, _ in hsv) / len(hsv), 4),
        "valueP95": round(values[int(len(values) * 0.95)], 4),
    }


def main() -> None:
    image = Image.open(RAW).convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Color(image).enhance(1.08)
    image = ImageEnhance.Brightness(image).enhance(0.97)
    image = add_particles(image)
    image = add_copy(image)
    image.convert("RGB").save(FINAL_2X, quality=100)
    image.resize((1179, 654), Image.Resampling.LANCZOS).convert(
        "RGB").save(FINAL, quality=100)

    canvas = Image.new("RGB", (1880, 700), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (34, 24),
        "CALM BASELINE → ELECTRONIC HIGH-ROLLER C2",
        font=font(FONT, 34, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (34, 67),
        "The product and lens stay fixed. Scene hierarchy, table story, foreground, and gold FX change.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    for index, (path, title) in enumerate((
            (BASELINE, "SUPERSEDED · PRODUCT + SUPPORT"),
            (FINAL, "SELECTED C2 · FINAL REFINEMENT"))):
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

    (HERE / "C2-final-composite-report.json").write_text(
        json.dumps({
            "source": RAW.name,
            "selectedStyleframe": "C2-electronic-stage",
            "output2x": FINAL_2X.name,
            "output": FINAL.name,
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "compositeParticleCount": 30,
            "productPixels": "deterministic grade only; no generative repaint",
            "metrics": {
                "referenceCasino": image_metrics(
                    HERE / "references/pinterest-casino-party-black-gold.jpg"),
                "referenceCardVortex": image_metrics(
                    HERE / "references/pinterest-card-magic-gold.jpg"),
                "selectedFinal": image_metrics(FINAL),
            },
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
