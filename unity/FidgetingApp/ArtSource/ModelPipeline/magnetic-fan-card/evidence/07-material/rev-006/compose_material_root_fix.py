"""Compose material/normal root-fix evidence."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "rev-005"
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
    result = Image.new("RGB", size, (9, 10, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    canvas = Image.new("RGB", (2100, 800), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 07 · MATERIAL / NORMAL ROOT FIX",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "Same material recipe and vertices. New Blender source carries smooth side/bevel normals; Unity fake object-space light bands are removed.",
        font=font(17, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        (OLD / "exact-material-closeup.png", "OLD · FLAT SIDE NORMALS"),
        (HERE / "exact-material-closeup.png", "NEW · SMOOTH NORMALS / PHYSICAL LIGHT CONTRACT"),
    )
    for index, (path, title) in enumerate(panels):
        x = 20 + index * 1030
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 1010, y + 660),
            radius=20,
            fill=(20, 21, 23),
            outline=(223, 174, 78) if index else (93, 74, 43),
            width=3 if index else 2,
        )
        canvas.paste(fit(path, (980, 565)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 596),
            title,
            font=font(19, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 628),
            "72 segments · medium bead-blast · dimensions unchanged",
            font=font(15, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(HERE / "material-root-fix-comparison.png")


if __name__ == "__main__":
    main()
