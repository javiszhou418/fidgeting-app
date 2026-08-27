"""Grade and typeset the three full-scene redesign directions."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


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


def compose(name: str) -> Path:
    image = Image.open(HERE / f"{name}.png").convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.15)
    image = ImageEnhance.Color(image).enhance(1.12)
    image = ImageEnhance.Brightness(image).enhance(0.92)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (58, 142, 162, 171),
        radius=5,
        fill=(192, 151, 72, 255),
    )
    tracked_text(
        draw,
        (71, 149),
        "FEATURED",
        font(COMPACT, 12, "Semibold"),
        (28, 21, 13, 255),
        1,
    )
    draw.text(
        (58, 188),
        "MAGNETIC FAN CARD",
        font=font(FONT, 35, "Semibold"),
        fill=(242, 229, 204, 255),
        stroke_width=1,
        stroke_fill=(47, 24, 15, 120),
    )
    output = HERE / f"{name}-banner.png"
    Image.alpha_composite(
        image.convert("RGBA"), layer).convert("RGB").save(output, quality=100)
    return output


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
    names = (
        "A-golden-lounge",
        "B-card-rain",
        "C-high-stakes-vortex",
    )
    outputs = [compose(name) for name in names]
    canvas = Image.new("RGB", (2130, 590), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (28, 20),
        "FULL-SCENE RESET · THREE COMPLETE DIRECTIONS",
        font=font(FONT, 32, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (28, 60),
        "Product geometry stays fixed. Hero scale, foreground, backdrop, light, particles, and palette are rebuilt together.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    labels = (
        ("A · GOLDEN LOUNGE", "architecture + restrained floating cards / droplets"),
        ("B · CARD RAIN", "visible card depth + stronger volume and particles"),
        ("C · HIGH-STAKES VORTEX", "chip framing + denser game-event energy"),
    )
    for index, (path, (title, subtitle)) in enumerate(zip(outputs, labels)):
        x = 20 + index * 700
        y = 98
        draw.rounded_rectangle(
            (x, y, x + 680, y + 468),
            radius=18,
            fill=(22, 20, 18),
            outline=(100, 75, 38),
            width=2,
        )
        canvas.paste(fit(path, (652, 382)), (x + 14, y + 14))
        draw.text(
            (x + 22, y + 405),
            title,
            font=font(FONT, 20, "Bold"),
            fill=(228, 179, 79),
        )
        draw.text(
            (x + 22, y + 436),
            subtitle,
            font=font(FONT, 15, "Regular"),
            fill=(188, 178, 164),
        )
    canvas.save(HERE / "full-scene-redesign-contact-sheet.png")


if __name__ == "__main__":
    main()
