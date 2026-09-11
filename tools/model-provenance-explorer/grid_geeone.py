"""Draw a labelled pixel grid over a reference photo so coordinates can be read
off the image directly, independent of any viewer scaling."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
INTAKE = (
    REPO
    / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade"
    / "evidence/01-intake/rev-002/obsidian-geeone-product"
)
OUT = Path("/tmp/geeone-measure")


def main() -> None:
    name = sys.argv[1]
    step = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    box = [int(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else None

    with Image.open(INTAKE / f"{name}.jpg") as raw:
        frame = raw.convert("RGB")

    offset_x, offset_y = 0, 0
    if box:
        frame = frame.crop(box)
        offset_x, offset_y = box[0], box[1]

    scale = max(1, 1400 // max(frame.width, 1))
    frame = frame.resize((frame.width * scale, frame.height * scale), Image.LANCZOS)
    draw = ImageDraw.Draw(frame, "RGBA")

    x = ((offset_x + step - 1) // step) * step
    while (x - offset_x) * scale < frame.width:
        px = (x - offset_x) * scale
        major = x % (step * 2) == 0
        draw.line([px, 0, px, frame.height], fill=(0, 255, 255, 150 if major else 70), width=2 if major else 1)
        if major:
            draw.text((px + 4, 6), str(x), fill=(0, 255, 255, 255))
        x += step

    y = ((offset_y + step - 1) // step) * step
    while (y - offset_y) * scale < frame.height:
        py = (y - offset_y) * scale
        major = y % (step * 2) == 0
        draw.line([0, py, frame.width, py], fill=(255, 120, 0, 150 if major else 70), width=2 if major else 1)
        if major:
            draw.text((6, py + 4), str(y), fill=(255, 160, 0, 255))
        y += step

    out = OUT / f"{name}-grid.png"
    OUT.mkdir(parents=True, exist_ok=True)
    frame.save(out)
    print(out)


if __name__ == "__main__":
    main()
