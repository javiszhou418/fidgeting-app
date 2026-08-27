#!/usr/bin/env python3
"""Generate tight exact-source crops for the corrected Gate 04 review."""

from pathlib import Path

from PIL import Image


REVISION = Path(__file__).resolve().parent
PREVIOUS_CROPS = REVISION.parent / "rev-008" / "source-crops"
OUTPUT = REVISION / "source-crops"


def crop(source_name: str, output_name: str, box: tuple[int, int, int, int], width: int = 760) -> None:
    with Image.open(PREVIOUS_CROPS / source_name) as image:
        region = image.crop(box)
        height = round(region.height * width / region.width)
        region.resize((width, height), Image.Resampling.LANCZOS).save(OUTPUT / output_name)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    crop("rotate-66.50.png", "visible-flat-lower.png", (165, 430, 650, 855))
    crop("slide-42.00.png", "circular-slide-overlap.png", (70, 0, 595, 455))
    crop("official-fixed-carrier.png", "official-concealed-interface.png", (65, 20, 650, 515))
    crop("rotate-67.25.png", "upper-rotates-over-lower.png", (165, 120, 650, 820))


if __name__ == "__main__":
    main()
