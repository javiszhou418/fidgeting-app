"""Compose the approved Surreal Levitation scene with 72-segment geometry."""

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


HERE = Path(__file__).resolve().parent
REV5 = HERE.parent / "rev-005"
LEGACY_COMPOSE = REV5 / "compose_surreal_levitation_preview.py"
RAW = HERE / "surreal-levitation-72-preview.png"
OUTPUT = HERE / "surreal-levitation-72-banner.png"
BOARD = HERE / "surreal-12-vs-72-comparison.png"
FONT = "/System/Library/Fonts/SFNS.ttf"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


legacy = load_module("fan_card_surreal_compose_72", LEGACY_COMPOSE)


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
    result = Image.new("RGB", size, (13, 12, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    image = Image.open(RAW).convert("RGB")
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Color(image).enhance(1.16)
    image = ImageEnhance.Brightness(image).enhance(0.88)
    image = legacy.add_copy(image)
    image.convert("RGB").save(OUTPUT, quality=100)

    canvas = Image.new("RGB", (1880, 700), (9, 9, 9))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (34, 24),
        "SURREAL LEVITATION · LEGACY 12 → SELECTED 72",
        font=font(34, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (34, 67),
        "Same environment, camera, 14 mm lift, particles, materials, text and color grade. Only visible corner tessellation changes.",
        font=font(17, "Regular"),
        fill=(158, 149, 137),
    )
    panels = (
        (REV5 / "surreal-levitation-banner.png", "LEGACY BLENDER · 12 / QUADRANT"),
        (OUTPUT, "REBUILT BLENDER · 72 / QUADRANT"),
    )
    for index, (path, title) in enumerate(panels):
        x = 24 + index * 925
        y = 108
        draw.rounded_rectangle(
            (x, y, x + 900, y + 560),
            radius=20,
            fill=(22, 20, 18),
            outline=(98, 74, 39),
            width=2,
        )
        canvas.paste(fit(path, (872, 484)), (x + 14, y + 14))
        draw.text(
            (x + 22, y + 510),
            title,
            font=font(19, "Bold"),
            fill=(226, 178, 82),
        )
    canvas.save(BOARD)

    render_report = json.loads(
        (HERE / "surreal-levitation-report.json").read_text(encoding="utf-8"))
    (HERE / "surreal-levitation-composite-report.json").write_text(
        json.dumps({
            "source": RAW.name,
            "output": OUTPUT.name,
            "visibleCornerSegmentsPerQuadrant": 72,
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "screenSpaceParticles": 0,
            "render": render_report,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
