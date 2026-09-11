#!/usr/bin/env python3
"""Assemble Gate 08 rev 6 lighting and partition review boards."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPORT = HERE / "review-board-report.json"
FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
SMALL = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 21)


def board(filename: str, title: str, entries, columns: int, cell=(560, 440)) -> dict:
    rows = (len(entries) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * cell[0], 84 + rows * cell[1]), (16, 16, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((28, 22), title, fill=(240, 240, 240), font=FONT)
    for index, (label, image_name) in enumerate(entries):
        image = Image.open(HERE / image_name).convert("RGB")
        image.thumbnail((cell[0] - 24, cell[1] - 58), Image.Resampling.LANCZOS)
        column = index % columns
        row = index // columns
        x = column * cell[0] + (cell[0] - image.width) // 2
        y = 84 + row * cell[1] + 42
        canvas.paste(image, (x, y))
        draw.text(
            (column * cell[0] + 18, 84 + row * cell[1] + 10),
            label,
            fill=(220, 220, 225),
            font=SMALL,
        )
    output = HERE / filename
    canvas.save(output, quality=95)
    return {"path": output.name, "dimensions": list(canvas.size), "entries": len(entries)}


def main() -> None:
    outputs = [
        board(
            "gate08-r006-lighting-review-board.png",
            "Gate 08 rev 6 · portable shared-HDR lighting",
            [
                ("Hero", "hero.png"),
                ("Left oblique", "left-oblique.png"),
                ("Right oblique", "right-oblique.png"),
                ("Low", "low.png"),
                ("Beauty", "pass-beauty.png"),
                ("Clay · duplicate scene", "pass-clay.png"),
                ("Normal · duplicate scene", "pass-normal.png"),
                ("Depth · duplicate scene", "pass-depth.png"),
                ("Roughness · duplicate scene", "pass-roughness.png"),
            ],
            3,
        ),
        board(
            "gate08-r006-partition-closeups.png",
            "Corrected material partitions · cap artwork / dark side / silver rim",
            [
                ("Top cap artwork", "closeup-top.png"),
                ("Dark side walls · artwork 0", "closeup-side.png"),
                ("Polished silver rim", "closeup-rim.png"),
                ("Legal mid-slide · 0°", "legal-mid-slide-0.png"),
                ("Max-open · 0°", "legal-max-open-0.png"),
                ("Max-open · 12°", "legal-max-open-12.png"),
                ("Max-open · 36°", "legal-max-open-36.png"),
                ("Max-open · 360°", "legal-max-open-360.png"),
            ],
            2,
            cell=(700, 530),
        ),
    ]
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 6,
        "outputs": outputs,
        "pass": all((HERE / item["path"]).exists() for item in outputs),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
