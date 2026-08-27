"""Typeset and grade the selected 32° true-depth final without 2D particles."""

from __future__ import annotations

import colorsys
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageStat


HERE = Path(__file__).resolve().parent
REV2 = HERE.parent / "rev-002"
RAW = HERE / "depth32-final-raw-2x.png"
PREVIOUS = REV2 / "electronic-high-roller-C2-final-preview.png"
FINAL_2X = HERE / "depth32-electronic-high-roller-final-2x.png"
FINAL = HERE / "depth32-electronic-high-roller-final-preview.png"
BOARD = HERE / "rev2-vs-true-depth-final-comparison.png"
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


def metrics(path: Path) -> dict:
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
    image = ImageEnhance.Contrast(image).enhance(1.10)
    image = ImageEnhance.Color(image).enhance(1.13)
    image = ImageEnhance.Brightness(image).enhance(0.97)
    image = add_copy(image)
    image.convert("RGB").save(FINAL_2X, quality=100)
    image.resize((1179, 654), Image.Resampling.LANCZOS).convert(
        "RGB").save(FINAL, quality=100)

    canvas = Image.new("RGB", (1880, 700), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (34, 24),
        "SCREEN-SPACE FX → TRUE 3D DEPTH",
        font=font(FONT, 34, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (34, 67),
        "Same product and 80 mm / 32° camera. Rev 3 rebuilds foreground, particles, architecture, and local light volume in Blender.",
        font=font(FONT, 17, "Regular"),
        fill=(158, 149, 137),
    )
    for index, (path, title) in enumerate((
            (PREVIOUS, "SUPERSEDED · SCREEN-SPACE GOLD DUST"),
            (FINAL, "REV 3 · TRUE 3D DEPTH FINAL"))):
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
        (HERE / "depth32-final-render-report.json").read_text(encoding="utf-8"))
    (HERE / "depth32-final-composite-report.json").write_text(
        json.dumps({
            "source": RAW.name,
            "output2x": FINAL_2X.name,
            "output": FINAL.name,
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "screenSpaceParticles": 0,
            "true3dFx": {
                "additionalFinalObjects":
                    render_report["additionalFinal3dFxObjects"],
                "culledProductOverlapObjects":
                    render_report["culledProductOverlapFxObjects"],
            },
            "productPixels": "deterministic color grade only; no generative repaint",
            "metrics": {
                "referenceCasino": metrics(
                    REV2 / "references/pinterest-casino-party-black-gold.jpg"),
                "referenceCardVortex": metrics(
                    REV2 / "references/pinterest-card-magic-gold.jpg"),
                "selectedFinal": metrics(FINAL),
            },
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
