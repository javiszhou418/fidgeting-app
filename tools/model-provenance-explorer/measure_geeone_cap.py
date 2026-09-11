"""Overlay measurement guides on the GEEONE reference photos.

Run with candidate coordinates, look at the output, adjust, repeat. The accepted
numbers become Gate 02 source-linked claims.
"""

from __future__ import annotations

import json
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

# name -> guides
GUIDES = {
    "geeone-01": {
        "cap_center": (300, 505),
        "cap_radius": 95,
        "body_center": (300, 495),
        "body_radius": 178,
    },
    "geeone-02": {
        "cap_center": (338, 396),
        "cap_radius": 108,
        "body_center": (338, 425),
        "body_radius": 205,
    },
}


def annotate(name: str, guide: dict) -> dict:
    source = INTAKE / f"{name}.jpg"
    with Image.open(source) as raw:
        frame = raw.convert("RGB")
    scale = 2
    frame = frame.resize((frame.width * scale, frame.height * scale), Image.LANCZOS)
    draw = ImageDraw.Draw(frame)

    def circle(center, radius, color, width):
        cx, cy = center[0] * scale, center[1] * scale
        r = radius * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
        draw.line([cx - 8, cy, cx + 8, cy], fill=color, width=width)
        draw.line([cx, cy - 8, cx, cy + 8], fill=color, width=width)

    circle(guide["body_center"], guide["body_radius"], (255, 90, 40), 4)
    circle(guide["cap_center"], guide["cap_radius"], (60, 220, 255), 4)

    out = OUT / f"{name}-guides.png"
    frame.save(out)
    return {
        "image": name,
        "capDiameterPx": guide["cap_radius"] * 2,
        "bodyDiameterPx": guide["body_radius"] * 2,
        "capToBodyRatio": round(guide["cap_radius"] / guide["body_radius"], 4),
        "overlay": str(out),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(GUIDES)
    print(json.dumps([annotate(n, GUIDES[n]) for n in names], indent=2))


if __name__ == "__main__":
    main()
