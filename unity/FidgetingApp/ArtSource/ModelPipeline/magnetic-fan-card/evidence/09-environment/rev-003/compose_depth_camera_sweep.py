"""Typeset the true-depth camera sweep without adding screen-space particles."""

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


def compose(elevation: int) -> Path:
    image = Image.open(HERE / f"depth-camera-{elevation:02d}.png").convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Color(image).enhance(1.06)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (62, 150, 166, 179),
        radius=5,
        fill=(190, 151, 75, 255),
    )
    tracked_text(
        draw,
        (75, 157),
        "FEATURED",
        font(COMPACT, 12, "Semibold"),
        (28, 21, 13, 255),
        1,
    )
    draw.text(
        (62, 196),
        "MAGNETIC FAN CARD",
        font=font(FONT, 35, "Semibold"),
        fill=(239, 227, 205, 255),
        stroke_width=1,
        stroke_fill=(52, 28, 18, 115),
    )
    output = HERE / f"depth-camera-{elevation:02d}-banner.png"
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
    outputs = [compose(elevation) for elevation in (32, 27, 22)]
    canvas = Image.new("RGB", (2130, 570), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (28, 20),
        "TRUE 3D DEPTH · SAME 80 MM LENS",
        font=font(FONT, 32, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (28, 60),
        "Foreground props, mid sparks, background cards / arches, and local volume are rendered in depth. Only elevation changes.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    labels = (
        ("32°", "original product angle · least background"),
        ("27°", "balanced product and casino depth"),
        ("22°", "strongest background scale · lowest angle"),
    )
    for index, (path, (title, subtitle)) in enumerate(zip(outputs, labels)):
        x = 20 + index * 700
        y = 98
        draw.rounded_rectangle(
            (x, y, x + 680, y + 448),
            radius=18,
            fill=(22, 20, 18),
            outline=(95, 72, 40),
            width=2,
        )
        canvas.paste(fit(path, (652, 362)), (x + 14, y + 14))
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
    canvas.save(HERE / "depth-camera-sweep-contact-sheet.png")


if __name__ == "__main__":
    main()
