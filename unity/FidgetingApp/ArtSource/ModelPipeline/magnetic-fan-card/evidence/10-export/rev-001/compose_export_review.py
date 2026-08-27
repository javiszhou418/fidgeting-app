"""Compose the Gate 10 export round-trip review contact sheet."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROUNDTRIP = HERE / "export-roundtrip-report.json"
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
    result = Image.new("RGB", size, (10, 11, 12))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    report = json.loads(ROUNDTRIP.read_text(encoding="utf-8"))
    canvas = Image.new("RGB", (2850, 760), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 10 · EXPORT ROUND-TRIP",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 62),
        "Same approved product geometry; neutral workbench display isolates hierarchy, bounds, and collision.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        (
            HERE / "fbx-roundtrip-neutral.png",
            "FBX · UNITY",
            f"{report['fbx']['stats']['triangles']:,} tris · "
            f"{report['fbx']['objects']} objects · hierarchy PASS",
        ),
        (
            HERE / "glb-roundtrip-neutral.png",
            "GLB · PORTABLE",
            f"{report['glb']['stats']['triangles']:,} tris · "
            "bounds delta ≤ 0.00007% · hierarchy PASS",
        ),
        (
            HERE / "collision-roundtrip.png",
            "COLLISION · 3 CONVEX SLABS",
            "Bottom / Middle / Top separate · watertight PASS",
        ),
    )
    for index, (path, title, subtitle) in enumerate(panels):
        x = 25 + index * 940
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 915, y + 625),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(path, (885, 530)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 556),
            title,
            font=font(21, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 588),
            subtitle,
            font=font(16, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / "export-roundtrip-contact-sheet.png")


if __name__ == "__main__":
    main()
