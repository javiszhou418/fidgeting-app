#!/usr/bin/env python3
"""Generate the shared transparent leather grain used by native Badge cards."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


SIZE = 384
OUTPUT = (
    Path(__file__).resolve().parents[1]
    / "Assets/Plugins/iOS/BadgeArtwork/badge-leather-texture.png"
)


def cubic(p0, p1, p2, p3, steps=14):
    points = []
    for index in range(steps + 1):
        t = index / steps
        inverse = 1.0 - t
        points.append(
            (
                inverse**3 * p0[0]
                + 3 * inverse**2 * t * p1[0]
                + 3 * inverse * t**2 * p2[0]
                + t**3 * p3[0],
                inverse**3 * p0[1]
                + 3 * inverse**2 * t * p1[1]
                + 3 * inverse * t**2 * p2[1]
                + t**3 * p3[1],
            )
        )
    return points


def generate() -> None:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")

    for index in range(34):
        seed_a = ((index * 43 + 17) % 97) / 97
        seed_b = ((index * 61 + 31) % 101) / 101
        seed_c = ((index * 79 + 7) % 103) / 103
        start = ((seed_a * 0.92 + 0.01) * SIZE, (seed_c * 0.94 + 0.02) * SIZE)
        length = (0.012 + seed_b * 0.032) * SIZE
        angle = (seed_c - 0.5) * 1.42
        direction = (math.cos(angle), math.sin(angle))
        normal = (-direction[1], direction[0])
        end = (start[0] + direction[0] * length, start[1] + direction[1] * length)
        bend = (seed_a - 0.5) * 6.3
        controls = (
            (
                start[0] + direction[0] * length * 0.31 + normal[0] * bend,
                start[1] + direction[1] * length * 0.31 + normal[1] * bend,
            ),
            (
                start[0] + direction[0] * length * 0.70 - normal[0] * bend * 0.55,
                start[1] + direction[1] * length * 0.70 - normal[1] * bend * 0.55,
            ),
        )
        points = cubic(start, controls[0], controls[1], end)
        shadow = [(x + normal[0] * 2.0, y + normal[1] * 2.0) for x, y in points]
        draw.line(shadow, fill=(0, 0, 0, 62), width=3, joint="curve")
        draw.line(points, fill=(255, 255, 255, 9), width=1, joint="curve")

    for index in range(270):
        seed_a = ((index * 37 + 11) % 101) / 101
        seed_b = ((index * 59 + 23) % 103) / 103
        seed_c = ((index * 83 + 41) % 107) / 107
        center = ((0.025 + seed_a * 0.95) * SIZE, (0.025 + seed_c * 0.95) * SIZE)
        radius_x = 2.2 + seed_b * 4.9
        radius_y = 1.8 + seed_c * 3.8
        skew = (seed_a - 0.5) * radius_x * 0.34
        points = []
        for step in range(16):
            angle = 2 * math.pi * step / 16
            wobble = 1 + 0.12 * math.sin(angle * 3 + seed_b * math.pi)
            points.append(
                (
                    center[0] + math.cos(angle) * radius_x * wobble + skew * math.sin(angle),
                    center[1] + math.sin(angle) * radius_y * wobble,
                )
            )
        draw.polygon(points, fill=(0, 0, 0, 18))
        draw.line(points + [points[0]], fill=(0, 0, 0, 96), width=2, joint="curve")
        highlight = [(x - 0.5, y - 0.5) for x, y in points]
        draw.line(highlight + [highlight[0]], fill=(255, 255, 255, 18), width=1, joint="curve")

    for index in range(420):
        x = ((index * 47 + 13) % 101) / 101 * SIZE
        y = ((index * 71 + 29) % 103) / 103 * SIZE
        radius = (1 + (index * 11) % 3) * 1.1
        draw.ellipse(
            (x - radius * 0.25, y + radius * 0.30, x + radius * 0.75, y + radius * 1.02),
            fill=(0, 0, 0, 76),
        )
        draw.ellipse(
            (x, y, x + radius * 0.58, y + radius * 0.42),
            fill=(255, 255, 255, 24),
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, optimize=True)
    print(OUTPUT)


if __name__ == "__main__":
    generate()
