#!/usr/bin/env python3
"""Build lossless full-frame Gate 08 rev 4 review assets."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
NAMES = [
    ("reflection-only", "Reflection-only sphere + strip"),
    ("clay", "Flat clay, no ground"),
    ("silver", "Approved silver response"),
    ("crystal", "Approved blood-red crystal"),
    ("full-model", "Full model"),
]
WIDTH = 1400
HEIGHT = 1100
LABEL = 80
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)


def labeled(path, title):
    source = Image.open(path).convert("RGB")
    if source.size != (WIDTH, HEIGHT):
        raise RuntimeError(f"Unexpected frame size: {path}")
    result = Image.new("RGB", (WIDTH, HEIGHT + LABEL), (24, 24, 24))
    ImageDraw.Draw(result).text((28, 21), title, font=FONT, fill=(238, 238, 238))
    result.paste(source, (0, LABEL))
    return result


def main():
    board = Image.new(
        "RGB", (WIDTH * 2, (HEIGHT + LABEL) * len(NAMES)), (24, 24, 24)
    )
    sequence = []
    for row, (name, title) in enumerate(NAMES):
        blender = labeled(
            HERE / f"blender-{name}-display.png", f"Blender · {title}"
        )
        unity = labeled(HERE / f"unity-{name}-display.png", f"Unity URP · {title}")
        heatmap = labeled(HERE / f"{name}-heatmap.png", f"Difference · {title}")
        board.paste(blender, (0, row * (HEIGHT + LABEL)))
        board.paste(unity, (WIDTH, row * (HEIGHT + LABEL)))
        for engine, image in [
            ("blender", blender),
            ("unity", unity),
            ("difference", heatmap),
        ]:
            path = HERE / f"review-{row:02d}-{engine}.png"
            image.save(path)
            sequence.append(path)
    board.save(HERE / "gate08-r004-neutral-parity-board.png")

    concat = HERE / "review-sequence.txt"
    lines = []
    for path in sequence:
        lines.append(f"file '{path.name}'")
        lines.append("duration 2")
    lines.append(f"file '{sequence[-1].name}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-movflags",
            "+faststart",
            str(HERE / "gate08-r004-neutral-parity-review.mp4"),
        ],
        cwd=HERE,
        check=True,
    )
    print(HERE / "gate08-r004-neutral-parity-board.png")
    print(HERE / "gate08-r004-neutral-parity-review.mp4")


if __name__ == "__main__":
    main()
