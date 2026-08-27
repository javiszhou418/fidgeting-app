"""Compose the approved Blender environment into the minimal Banner layout."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
SOURCE = (
    REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/"
    "magnetic-fan-card/evidence/09-environment/rev-001/"
    "environment-B-charcoal-hard-case.png"
)
OUTPUT = SCRIPT.parent / "fan-card-banner-blender-charcoal-preview.png"
REPORT = SCRIPT.parent / "fan-card-banner-blender-charcoal-report.json"
FONT = Path("/System/Library/Fonts/SFNS.ttf")
COMPACT_FONT = Path("/System/Library/Fonts/SFCompact.ttf")


def font(path: Path, size: int, variation: str):
    value = ImageFont.truetype(str(path), size)
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
    fill: tuple[int, int, int],
    tracking: int,
) -> None:
    x, y = position
    for character in text:
        draw.text((x, y), character, font=value, fill=fill)
        width = draw.textlength(character, font=value)
        x += round(width) + tracking


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    draw = ImageDraw.Draw(image)

    label_box = (72, 150, 174, 178)
    draw.rounded_rectangle(
        label_box,
        radius=5,
        fill=(184, 151, 82),
    )
    tracked_text(
        draw,
        (84, 156),
        "FEATURED",
        font(COMPACT_FONT, 12, "Semibold"),
        (24, 22, 18),
        1,
    )
    draw.text(
        (72, 195),
        "MAGNETIC FAN CARD",
        font=font(FONT, 36, "Semibold"),
        fill=(235, 232, 225),
    )

    image.save(OUTPUT, quality=100)
    REPORT.write_text(
        json.dumps({
            "source": str(SOURCE.relative_to(REPO)),
            "output": str(OUTPUT.relative_to(REPO)),
            "textGroups": ["FEATURED", "MAGNETIC FAN CARD"],
            "goldOutline": False,
            "productPixels": "unchanged from selected Blender Cycles render",
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
