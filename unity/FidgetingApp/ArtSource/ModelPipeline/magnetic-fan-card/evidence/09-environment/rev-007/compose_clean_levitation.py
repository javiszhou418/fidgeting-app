"""Compose the cleaned 20 mm levitation Banner and comparison."""

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


HERE = Path(__file__).resolve().parent
REV6 = HERE.parent / "rev-006"
LEGACY_COMPOSE = (
    HERE.parent / "rev-005/compose_surreal_levitation_preview.py")
RAW = HERE / "surreal-clean-20mm-preview.png"
OUTPUT = HERE / "surreal-clean-20mm-banner.png"
BOARD = HERE / "cluttered-14mm-vs-clean-20mm.png"
FONT = "/System/Library/Fonts/SFNS.ttf"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


legacy = load_module("fan_card_clean_levitation_compose", LEGACY_COMPOSE)


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
        "REMOVE AMBIGUOUS PROPS · 14 MM → CLEAN 20 MM",
        font=font(34, "Bold"),
        fill=(241, 224, 189),
    )
    draw.text(
        (34, 67),
        "The red chip and every decorative Card Rain prop entering the hero safe zone are removed. Product geometry remains unchanged.",
        font=font(17, "Regular"),
        fill=(158, 149, 137),
    )
    panels = (
        (
            REV6 / "surreal-levitation-72-banner.png",
            "REJECTED · AMBIGUOUS CARD / RED CHIP · 14 MM",
        ),
        (OUTPUT, "REV 7 · CLEAN HERO SAFE ZONE · 20 MM"),
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
        (HERE / "clean-levitation-report.json").read_text(encoding="utf-8"))
    (HERE / "clean-levitation-composite-report.json").write_text(
        json.dumps({
            "source": RAW.name,
            "output": OUTPUT.name,
            "copy": ["FEATURED", "MAGNETIC FAN CARD"],
            "screenSpaceParticles": 0,
            "render": render_report,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
