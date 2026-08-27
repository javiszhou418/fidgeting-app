"""Build the Gate 09 luxury-scene reference analysis board."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
BASELINE = (
    REPO / "Artifacts/FanCardBannerConcept/"
    "fan-card-banner-blender-charcoal-preview.png"
)
REF_A = HERE / "references/pinterest-casino-party-black-gold.jpg"
REF_B = HERE / "references/pinterest-card-magic-gold.jpg"
OUTPUT = HERE / "luxury-reference-analysis-board.png"
FONT = "/System/Library/Fonts/SFNS.ttf"


def font(size: int, bold: bool = False):
    value = ImageFont.truetype(FONT, size)
    if bold:
        try:
            value.set_variation_by_name("Bold")
        except OSError:
            pass
    return value


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    source = Image.open(path).convert("RGB")
    source.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (17, 16, 15))
    result.paste(
        source,
        ((size[0] - source.width) // 2, (size[1] - source.height) // 2),
    )
    return result


def panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    image: Path,
    title: str,
    notes: list[str],
    accent: tuple[int, int, int],
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box, radius=22, fill=(24, 22, 20), outline=(74, 65, 54), width=2)
    canvas.paste(fit(image, (x1 - x0 - 28, 455)), (x0 + 14, y0 + 14))
    draw.text((x0 + 22, y0 + 486), title, font=font(24, True), fill=accent)
    for index, note in enumerate(notes):
        draw.text(
            (x0 + 22, y0 + 530 + index * 31),
            "• " + note,
            font=font(17),
            fill=(211, 202, 188),
        )


def main() -> None:
    width, height = 2200, 1450
    canvas = Image.new("RGB", (width, height), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (48, 30),
        "FROM LOOKDEV TO ELECTRONIC HIGH-ROLLER BANNER",
        font=font(42, True),
        fill=(242, 225, 189),
    )
    draw.text(
        (48, 82),
        "Keep the approved product. Rebuild only the scene hierarchy, light, and FX.",
        font=font(20),
        fill=(160, 150, 137),
    )

    panel(
        canvas, draw, (35, 125, 730, 760), BASELINE,
        "CURRENT BASELINE",
        ["exact model and camera work", "only subject + support", "no scale, depth, or game energy"],
        (176, 185, 198),
    )
    panel(
        canvas, draw, (752, 125, 1447, 760), REF_A,
        "REFERENCE A · CASINO LOUNGE",
        ["foreground table rail", "floating cards and gold droplets", "warm architectural bokeh"],
        (221, 167, 73),
    )
    panel(
        canvas, draw, (1469, 125, 2164, 760), REF_B,
        "REFERENCE B · CARD VORTEX",
        ["cropped chips create foreground", "black void protects the focal point", "diagonal motion and focus depth"],
        (194, 79, 63),
    )

    draw.rounded_rectangle(
        (35, 790, 1540, 1408),
        radius=24,
        fill=(19, 18, 17),
        outline=(87, 72, 48),
        width=2,
    )
    draw.text(
        (65, 820),
        "RECOMMENDED SYNTHESIS · ELECTRONIC HIGH-ROLLER TABLE",
        font=font(28, True),
        fill=(231, 188, 97),
    )
    layers = [
        (
            "BACKGROUND",
            "black-gold casino architecture · horizontal light bands · soft bokeh",
            (42, 34, 25),
        ),
        (
            "MIDGROUND",
            "approved Fan Card · velvet table · brass rail · electronic suit circuitry",
            (55, 25, 25),
        ),
        (
            "FOREGROUND",
            "one or two cropped chips · suit shards · strong shallow-depth blur",
            (36, 28, 21),
        ),
        (
            "LIGHT / FX",
            "motivated warm key · gold rim · one light shaft · bounded diagonal particles",
            (54, 42, 18),
        ),
    ]
    for index, (name, description, color) in enumerate(layers):
        y = 884 + index * 116
        draw.rounded_rectangle(
            (65, y, 1510, y + 92),
            radius=16,
            fill=color,
            outline=(112, 89, 51),
            width=1,
        )
        draw.text((91, y + 16), name, font=font(20, True), fill=(232, 188, 94))
        draw.text(
            (315, y + 18),
            description,
            font=font(18),
            fill=(224, 215, 198),
        )

    draw.rounded_rectangle(
        (1570, 790, 2164, 1408),
        radius=24,
        fill=(19, 18, 17),
        outline=(87, 72, 48),
        width=2,
    )
    draw.text((1600, 820), "STYLEFRAME ROUTES", font=font(26, True), fill=(238, 222, 188))
    routes = [
        ("A", "CASINO LOUNGE", "grounded / fewer FX"),
        ("B", "BLACK VORTEX", "game-heavy / less grounded"),
        ("C", "ELECTRONIC HIGH-ROLLER", "balanced synthesis · recommended"),
    ]
    for index, (letter, title, subtitle) in enumerate(routes):
        y = 885 + index * 126
        selected = letter == "C"
        draw.rounded_rectangle(
            (1600, y, 2134, y + 98),
            radius=15,
            fill=(64, 42, 17) if selected else (31, 29, 27),
            outline=(219, 169, 70) if selected else (76, 70, 63),
            width=2 if selected else 1,
        )
        draw.text((1622, y + 18), letter, font=font(25, True), fill=(231, 180, 76))
        draw.text((1670, y + 14), title, font=font(19, True), fill=(239, 231, 215))
        draw.text((1670, y + 49), subtitle, font=font(16), fill=(171, 161, 148))

    draw.text((1600, 1280), "LOCKED", font=font(20, True), fill=(180, 186, 195))
    draw.text(
        (1600, 1317),
        "product · 80 mm lens · material · two text groups",
        font=font(16),
        fill=(186, 177, 164),
    )
    canvas.save(OUTPUT)


if __name__ == "__main__":
    main()
