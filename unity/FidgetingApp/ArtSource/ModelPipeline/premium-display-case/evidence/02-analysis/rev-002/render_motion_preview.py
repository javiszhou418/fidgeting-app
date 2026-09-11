#!/usr/bin/env python3
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
WIDTH = 720
HEIGHT = 900
FRAME_COUNT = 72
FPS = 30


def smoothstep(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def matte_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), (24, 26, 29))
    draw = ImageDraw.Draw(image)
    random_source = random.Random(24)
    for _ in range(7600):
        x = random_source.randrange(WIDTH)
        y = random_source.randrange(HEIGHT)
        delta = random_source.choice((-5, -4, -3, 3, 4, 5))
        base = 28 + delta
        draw.point((x, y), fill=(base, base + 1, base + 2))
    return image


def draw_case(frame_index: int) -> Image.Image:
    image = matte_background()
    draw = ImageDraw.Draw(image, "RGBA")
    center_x = WIDTH // 2
    center_y = 430
    full_width = 324
    full_height = 432
    depth_width = 34

    if frame_index < 9:
        appear = 0.18 + 0.82 * smoothstep(frame_index / 8)
        angle = 0.0
        scale = 0.92 + 0.08 * appear
        alpha = int(255 * appear)
    else:
        scale = 1.0
        alpha = 255
        turn_progress = smoothstep(min(1.0, (frame_index - 9) / 47))
        angle = turn_progress * math.tau

    cosine = math.cos(angle)
    visible_width = max(depth_width, int(full_width * abs(cosine)))
    left = center_x - visible_width // 2
    right = center_x + visible_width // 2
    top = center_y - int(full_height * scale) // 2
    bottom = center_y + int(full_height * scale) // 2
    radius = min(42, max(10, visible_width // 6))
    front_facing = cosine >= 0

    if visible_width <= depth_width + 8:
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=radius,
            fill=(154, 160, 166, alpha),
            outline=(232, 236, 239, alpha),
            width=5,
        )
        draw.line(
            (center_x, top + 18, center_x, bottom - 18),
            fill=(90, 98, 106, alpha),
            width=4,
        )
    else:
        shell_fill = (96, 103, 111, alpha) if front_facing else (70, 76, 84, alpha)
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=radius,
            fill=shell_fill,
            outline=(229, 233, 237, alpha),
            width=16,
        )
        inner_inset = max(18, int(visible_width * 0.095))
        inner_left = min(center_x - 4, left + inner_inset)
        inner_right = max(center_x + 4, right - inner_inset)
        draw.rounded_rectangle(
            (inner_left, top + 70, inner_right, bottom - 24),
            radius=max(8, radius - 12),
            fill=(28, 31, 35, alpha),
            outline=(124, 132, 140, alpha),
            width=3,
        )

        if front_facing and visible_width > 150:
            label_left = left + inner_inset
            label_right = right - inner_inset
            label_bottom = top + 64
            draw.rounded_rectangle(
                (label_left, top + 18, label_right, label_bottom),
                radius=8,
                fill=(178, 182, 185, alpha),
            )
            line_width = max(20, label_right - label_left - 28)
            draw.line(
                (label_left + 14, top + 34, label_left + 14 + line_width, top + 34),
                fill=(39, 42, 46, alpha),
                width=5,
            )
            draw.line(
                (label_left + 14, top + 48, label_left + 14 + int(line_width * 0.62), top + 48),
                fill=(68, 72, 77, alpha),
                width=3,
            )

    if frame_index >= 57:
        sweep = smoothstep((frame_index - 57) / 14)
        sweep_x = int((center_x - full_width) + sweep * full_width * 2)
        draw.polygon(
            [
                (sweep_x - 34, top + 10),
                (sweep_x - 6, top + 10),
                (sweep_x + 74, bottom - 10),
                (sweep_x + 46, bottom - 10),
            ],
            fill=(255, 255, 255, 76),
        )

    shadow_width = 176 + int(46 * abs(cosine))
    draw.ellipse(
        (
            center_x - shadow_width,
            bottom + 34,
            center_x + shadow_width,
            bottom + 72,
        ),
        fill=(0, 0, 0, 96),
    )

    font = ImageFont.load_default(size=24)
    phase = "APPEAR" if frame_index < 9 else (
        "Y-AXIS 360" if frame_index < 57 else "SINGLE HIGHLIGHT"
    )
    draw.text((30, 28), phase, fill=(238, 240, 242, 255), font=font)
    draw.text((30, 62), "PORTRAIT 3:4 ANALYSIS PROPORTION", fill=(170, 177, 184, 255), font=font)
    draw.point((WIDTH - 1, HEIGHT - 1), fill=(frame_index + 1, 0, 0, 255))
    return image


def contact_sheet(frames: list[Image.Image]) -> Image.Image:
    indexes = [9, 21, 33, 45, 56, 66]
    labels = ["0° FRONT", "90° EDGE", "180° BACK", "270° EDGE", "360° FRONT", "HIGHLIGHT"]
    thumb_width = 300
    thumb_height = 375
    sheet = Image.new("RGB", (thumb_width * 3, (thumb_height + 48) * 2), (10, 11, 13))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=21)
    for position, (index, label) in enumerate(zip(indexes, labels)):
        thumb = frames[index].resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = (position % 3) * thumb_width
        y = (position // 3) * (thumb_height + 48)
        sheet.paste(thumb, (x, y))
        draw.text((x + 12, y + thumb_height + 10), label, fill=(224, 228, 232), font=font)
    return sheet


def main() -> None:
    frames = [draw_case(index) for index in range(FRAME_COUNT)]
    frames[0].save(
        ROOT / "portrait-y-turn-preview.gif",
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        disposal=2,
        optimize=False,
    )
    contact_sheet(frames).save(ROOT / "portrait-y-turn-contact-sheet.png")


if __name__ == "__main__":
    main()
