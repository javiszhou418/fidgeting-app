"""Compose six-view and structural review boards for 72 segments."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
CORNER = HERE.parents[1] / "03-contract/rev-007/corner-72-selected.png"
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


def panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    box: tuple[int, int, int, int],
    label: str,
) -> None:
    x, y, width, height = box
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=18,
        fill=(20, 21, 23),
        outline=(93, 74, 43),
        width=2,
    )
    canvas.paste(fit(path, (width - 30, height - 68)), (x + 15, y + 15))
    draw.text(
        (x + 22, y + height - 42),
        label,
        font=font(18, "Bold"),
        fill=(223, 174, 78),
    )


def main() -> None:
    six = Image.new("RGB", (2400, 1500), (8, 9, 10))
    draw = ImageDraw.Draw(six)
    draw.text(
        (30, 20),
        "GATE 06 · 72-SEGMENT SIX-VIEW GEOMETRY",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 64),
        "One geometry source. Dimensions, pivot, tracks, layers, ranks, and 1 mm air gaps remain locked.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    views = (
        ("view-front.png", "FRONT"),
        ("view-back.png", "BACK"),
        ("view-top.png", "TOP"),
        ("view-bottom.png", "BOTTOM"),
        ("view-left.png", "LEFT"),
        ("view-right.png", "RIGHT"),
    )
    for index, (name, label) in enumerate(views):
        panel(
            six,
            draw,
            HERE / name,
            (
                20 + (index % 3) * 795,
                105 + (index // 3) * 680,
                775,
                650,
            ),
            label,
        )
    six.save(HERE / "six-view-contact-sheet.png")

    base = Image.open(HERE / "workbench.png").convert("RGB")
    dimension = Image.new("RGB", (1600, 980), (8, 9, 10))
    dim_draw = ImageDraw.Draw(dimension)
    dim_draw.text(
        (30, 20),
        "LOCKED GEOMETRY · 72 VISIBLE SEGMENTS / QUADRANT",
        font=font(30, "Bold"),
        fill=(237, 224, 199),
    )
    dimension.paste(fit(HERE / "workbench.png", (1050, 850)), (20, 100))
    dim_draw.rounded_rectangle(
        (1090, 110, 1575, 900),
        radius=20,
        fill=(20, 21, 23),
        outline=(93, 74, 43),
        width=2,
    )
    specs = (
        "CARD  63.5 × 88.9 × 3.5 mm",
        "CORNER  R 9.5 mm",
        "VISIBLE ARC  72 / 90°",
        "AIR GAP  1.0 mm × 2",
        "BLACK EDGE  1.0 mm",
        "GOLD TRIM  0.8 mm",
        "BEVEL  0.38 mm",
        "TRACK CLEARANCE  7.590 mm",
        "COLLISION ARC  8 / 90°",
        "PIVOT / MOTION  UNCHANGED",
    )
    for index, text in enumerate(specs):
        dim_draw.text(
            (1120, 150 + index * 66),
            text,
            font=font(18, "Bold" if index < 3 else "Regular"),
            fill=(225, 188, 112) if index < 3 else (190, 190, 185),
        )
    dimension.save(HERE / "dimension-overlay.png")

    structural = Image.new("RGB", (2400, 1400), (8, 9, 10))
    structural_draw = ImageDraw.Draw(structural)
    structural_draw.text(
        (30, 20),
        "GATE 06 · STRUCTURAL VALIDATION",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    structural_panels = (
        (HERE / "workbench.png", "WORKBENCH"),
        (HERE / "dimension-overlay.png", "DIMENSIONS"),
        (HERE / "pivot-overlay.png", "PIVOT"),
        (HERE / "exploded-geometry.png", "EXPLODED · INTERNAL"),
        (CORNER, "72-SEGMENT CORNER"),
    )
    sizes = (
        (20, 105, 775, 590),
        (815, 105, 775, 590),
        (1610, 105, 770, 590),
        (20, 720, 1165, 650),
        (1205, 720, 1175, 650),
    )
    for (path, label), box in zip(structural_panels, sizes):
        panel(structural, structural_draw, path, box, label)
    structural.save(HERE / "structural-contact-sheet.png")


if __name__ == "__main__":
    main()
