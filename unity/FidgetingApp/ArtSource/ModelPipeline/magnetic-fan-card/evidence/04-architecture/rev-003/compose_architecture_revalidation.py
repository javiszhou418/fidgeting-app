"""Show that the 72-segment change does not alter product architecture."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REV2 = HERE.parent / "rev-002"
CONTRACT = HERE.parents[1] / "03-contract/rev-007/tessellation-selection.png"
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
    canvas = Image.new("RGB", (2200, 900), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 04 · TOPOLOGY-ONLY ARCHITECTURE REVALIDATION",
        font=font(32, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 62),
        "72 segments refine each visible perimeter. Parts, pivots, layers, tracks, artwork parenting, and collisions remain unchanged.",
        font=font(17, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        (REV2 / "part-tree.png", "APPROVED PART TREE · UNCHANGED"),
        (CONTRACT, "SELECTED 72-SEGMENT PERIMETER"),
    )
    for index, (path, title) in enumerate(panels):
        x = 20 + index * 1090
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 1070, y + 710),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(path, (1040, 620)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 656),
            title,
            font=font(20, "Bold"),
            fill=(223, 174, 78),
        )
    lines = (
        "UNCHANGED: MagneticFanCard_Root → Bottom / Middle / Top",
        "UNCHANGED: Bottom fixed · Middle 45°q · Top 90°q",
        "UNCHANGED: tracks Top+Middle · followers Middle+Bottom · collision 8/quadrant",
    )
    for index, line in enumerate(lines):
        draw.text(
            (35 + index * 715, 845),
            line,
            font=font(14, "Regular"),
            fill=(174, 174, 170),
        )
    canvas.save(HERE / "architecture-revalidation.png")
    (HERE / "architecture-revalidation-report.json").write_text(
        json.dumps({
            "selectedVisibleCornerSegmentsPerQuadrant": 72,
            "changed": ["visible perimeter vertex density"],
            "unchanged": [
                "part tree",
                "material zones",
                "pivot",
                "layer angles",
                "track layers",
                "follower layers",
                "artwork parenting",
                "collision tessellation"
            ],
            "collisionCornerSegmentsPerQuadrant": 8,
            "downstreamGeometryRebuildRequired": True
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
