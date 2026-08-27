"""Compose the 12-versus-48 corner tessellation review."""

import json
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
    report = json.loads(
        (HERE / "tessellation-report.json").read_text(encoding="utf-8"))
    low, high = report["comparison"]
    canvas = Image.new("RGB", (2000, 790), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "VISIBLE CORNER TESSELLATION",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "Cyan markers show real contour vertices. Dimensions, 9.5 mm radius, pivot, bevel, and collision stay unchanged.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        (
            HERE / "corner-12.png",
            "CURRENT · 12 / QUADRANT",
            f"corner error {low['maximumCornerChordErrorMm']:.5f} mm · "
            f"{low['totalSceneTriangles']:,} tris",
        ),
        (
            HERE / "corner-48.png",
            "PROPOSED · 48 / QUADRANT",
            f"corner error {high['maximumCornerChordErrorMm']:.5f} mm · "
            f"{high['totalSceneTriangles']:,} tris",
        ),
    )
    for index, (path, title, subtitle) in enumerate(panels):
        x = 20 + index * 990
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 970, y + 650),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        image = Image.open(path).convert("RGB")
        image.thumbnail((940, 550), Image.Resampling.LANCZOS)
        canvas.paste(image, (x + 15, y + 15))
        draw.text(
            (x + 24, y + 574),
            title,
            font=font(21, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 608),
            subtitle,
            font=font(16, "Regular"),
            fill=(184, 184, 180),
        )
    draw.text(
        (30, 765),
        "Collision proxy remains 8 segments per quadrant; only visible body, gold trim, and silver face increase.",
        font=font(15, "Regular"),
        fill=(143, 146, 150),
    )
    canvas.save(HERE / "tessellation-comparison.png")


if __name__ == "__main__":
    main()
