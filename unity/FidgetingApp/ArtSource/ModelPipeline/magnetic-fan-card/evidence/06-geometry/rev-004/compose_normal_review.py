"""Compose the flat-versus-smooth normal review."""

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


def main() -> None:
    canvas = Image.new("RGB", (2000, 790), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 06 · NORMAL POLICY ROOT FIX",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "Same 72-segment vertices. Side and bevel normals become smooth; planar caps stay hard. Vertex hash is identical.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        ("normal-before.png", "REJECTED · FLAT SIDE NORMALS"),
        ("normal-after.png", "PROPOSED · SMOOTH SIDE / HARD CAP"),
    )
    for index, (name, label) in enumerate(panels):
        x = 20 + index * 990
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 970, y + 650),
            radius=20,
            fill=(20, 21, 23),
            outline=(223, 174, 78) if index else (93, 74, 43),
            width=3 if index else 2,
        )
        image = Image.open(HERE / name).convert("RGB")
        canvas.paste(image, (x + 5, y + 5))
        draw.text(
            (x + 24, y + 600),
            label,
            font=font(20, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 630),
            "72 segments / quadrant · geometry positions unchanged",
            font=font(15, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / "normal-policy-comparison.png")


if __name__ == "__main__":
    main()
