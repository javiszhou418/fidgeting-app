"""Compose the user-selected 72-segment topology contract board."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REV6 = HERE.parent / "rev-006"
FONT = "/System/Library/Fonts/SFNS.ttf"

METRICS = {
    48: {"triangles": 11040, "error": 0.00127169},
    72: {"triangles": 15840, "error": 0.00056520},
    96: {"triangles": 20640, "error": 0.00031793},
}


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
    selected = Image.open(REV6 / "corner-72.png").convert("RGB")
    selected.save(HERE / "corner-72-selected.png")

    canvas = Image.new("RGB", (2700, 790), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "SELECTED VISIBLE CORNER DENSITY · 72 / QUADRANT",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "72 balances sub-pixel curvature with mobile hero cost. Collision remains 8; dimensions and mechanics do not change.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    for index, segments in enumerate((48, 72, 96)):
        x = 20 + index * 890
        y = 105
        selected_panel = segments == 72
        draw.rounded_rectangle(
            (x, y, x + 870, y + 650),
            radius=20,
            fill=(20, 21, 23),
            outline=(223, 174, 78) if selected_panel else (74, 69, 59),
            width=5 if selected_panel else 2,
        )
        canvas.paste(
            fit(REV6 / f"corner-{segments:02d}.png", (840, 550)),
            (x + 15, y + 15),
        )
        title = (
            f"{segments} / QUADRANT · SELECTED"
            if selected_panel
            else f"{segments} / QUADRANT"
        )
        draw.text(
            (x + 24, y + 574),
            title,
            font=font(21, "Bold"),
            fill=(223, 174, 78) if selected_panel else (185, 181, 172),
        )
        metric = METRICS[segments]
        draw.text(
            (x + 24, y + 608),
            f"{metric['triangles']:,} single-card scene tris · "
            f"{metric['error']:.8f} mm corner error",
            font=font(16, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / "tessellation-selection.png")

    (HERE / "tessellation-selection-report.json").write_text(
        json.dumps({
            "selectedSegmentsPerQuadrant": 72,
            "visibleSurfaces": ["body", "gold-trim", "silver-face"],
            "collisionSegmentsPerQuadrant": 8,
            "singleCardSceneTriangles": 15840,
            "maximumCornerChordErrorMm": 0.00056520,
            "dimensionsChanged": False,
            "mechanicsChanged": False,
            "userSelected": True,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
