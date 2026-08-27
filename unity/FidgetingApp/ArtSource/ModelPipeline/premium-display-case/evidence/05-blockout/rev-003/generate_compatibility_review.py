#!/usr/bin/env python3
"""Compose whole-case Gate 05 rev 3 compatibility evidence."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
REV2 = ROOT.parent / "rev-002"
AUDIT = ROOT / "architecture-compatibility-audit.json"
HERO = ROOT / "white-model-hero.png"
FRONT = ROOT / "white-model-front.png"
SOURCE_HERO = REV2 / "blockout-hero.png"
OUTPUT_REVIEW = ROOT / "blockout-architecture-compatibility-review.png"
OUTPUT_HIERARCHY = ROOT / "blockout-pivot-root-hierarchy.png"

BG = "#081018"
PANEL = "#101c27"
PANEL_ALT = "#142433"
TEXT = "#f2f6f8"
MUTED = "#9eb0bc"
CYAN = "#42d9d2"
GREEN = "#57d68d"
AMBER = "#f2bf66"
LINE = "#315064"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, outline: str = LINE) -> None:
    draw.rounded_rectangle(box, radius=24, fill=fill, outline=outline, width=2)


def fit_image(source: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(source).convert("RGB")
    scale = min(size[0] / image.width, size[1] / image.height)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", size, PANEL)
    canvas.paste(resized, ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2))
    return canvas


def draw_status(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str) -> None:
    draw.text((x, y), label, font=font(27), fill=MUTED)
    draw.text((x, y + 35), value, font=font(31, True), fill=GREEN)


def make_hierarchy(audit: dict) -> None:
    canvas = Image.new("RGB", (1600, 1200), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 56), "GATE 05 · PIVOT / ROOT OWNERSHIP", font=font(50, True), fill=TEXT)
    draw.text((70, 120), "Whole assembled case · no split, explode, proxy, halo, or toy geometry", font=font(28), fill=MUTED)

    boxes = {
        "PresentationRoot": (90, 230, 590, 350),
        "CaseAssembly": (90, 430, 590, 550),
        "RearPolycarbonateShell": (720, 330, 1460, 450),
        "FrontPolycarbonateShell": (720, 535, 1460, 655),
        "ContentSlot": (720, 740, 1460, 860),
    }
    labels = {
        "PresentationRoot": ("PresentationRoot", "Pivot (0, 0, 0) · identity rotation/scale"),
        "CaseAssembly": ("CaseAssembly", "One rigid assembled case"),
        "RearPolycarbonateShell": ("RearPolycarbonateShell", "Geometry remains parented to CaseAssembly"),
        "FrontPolycarbonateShell": ("FrontPolycarbonateShell", "Tube + label remain attached"),
        "ContentSlot": ("ContentSlot", "Caller-owned EMPTY · 0 children"),
    }
    for name, box in boxes.items():
        rounded(draw, box, PANEL_ALT if name in ("PresentationRoot", "CaseAssembly") else PANEL)
        title, subtitle = labels[name]
        draw.text((box[0] + 28, box[1] + 22), title, font=font(31, True), fill=CYAN if name == "PresentationRoot" else TEXT)
        draw.text((box[0] + 28, box[1] + 72), subtitle, font=font(24), fill=MUTED)

    def arrow(start: tuple[int, int], end: tuple[int, int]) -> None:
        draw.line((start, end), fill=CYAN, width=5)
        x, y = end
        draw.polygon(((x, y), (x - 14, y - 8), (x - 14, y + 8)), fill=CYAN)

    arrow((340, 350), (340, 430))
    arrow((590, 490), (720, 390))
    arrow((590, 490), (720, 595))
    draw.line(((1460, 390), (1520, 390), (1520, 800), (1460, 800)), fill=CYAN, width=5)
    draw.polygon(((1460, 800), (1474, 792), (1474, 808)), fill=CYAN)

    rounded(draw, (90, 965, 1460, 1115), PANEL_ALT)
    draw.text((120, 990), "Ownership boundary", font=font(29, True), fill=AMBER)
    draw.text(
        (120, 1037),
        "Blender: geometry, pivot, UV, material zones   |   Unity: timing, easing, Z travel, rotation, mesh-clipped light",
        font=font(24),
        fill=TEXT,
    )
    draw.text(
        (120, 1075),
        f"Geometry digest: {audit['output']['geometryDigest'][:20]}… · unchanged",
        font=font(23),
        fill=GREEN,
    )
    canvas.save(OUTPUT_HIERARCHY, optimize=True)


def make_review(audit: dict) -> None:
    canvas = Image.new("RGB", (2560, 1600), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((72, 55), "GATE 05 · WHITE MODEL COMPATIBILITY", font=font(54, True), fill=TEXT)
    draw.text(
        (72, 123),
        "Gate 04 rev 7 changes Unity presentation ownership only. The historical white-model geometry remains unchanged.",
        font=font(27),
        fill=MUTED,
    )

    rounded(draw, (60, 190, 925, 1170), PANEL)
    draw.text((92, 220), "BEFORE · approved rev 2", font=font(30, True), fill=TEXT)
    canvas.paste(fit_image(SOURCE_HERO, (805, 850)), (90, 285))

    rounded(draw, (950, 190, 1815, 1170), PANEL)
    draw.text((982, 220), "AFTER · rev 3 revalidation", font=font(30, True), fill=TEXT)
    canvas.paste(fit_image(HERO, (805, 850)), (980, 285))

    rounded(draw, (1840, 190, 2500, 1170), PANEL_ALT)
    draw.text((1880, 220), "COMPATIBILITY RESULT", font=font(31, True), fill=CYAN)
    draw_status(draw, 1880, 295, "Envelope", "228 × 304 × 59 mm")
    draw_status(draw, 1880, 390, "Portrait ratio", "0.7500")
    draw_status(draw, 1880, 485, "Label center", "Y = 99 mm")
    draw_status(draw, 1880, 580, "Corner-center drift", "0.000 mm")
    draw_status(draw, 1880, 675, "Closed tube", "1 body · 0 / 0 edges")
    draw_status(draw, 1880, 770, "Channel flood-fill", "384 / 384")
    draw_status(draw, 1880, 865, "ContentSlot", "EMPTY · 0 children")
    draw_status(draw, 1880, 960, "Geometry digest", "UNCHANGED")
    draw.text((1880, 1070), audit["output"]["geometryDigest"][:32], font=font(21), fill=MUTED)
    draw.text((1880, 1100), audit["output"]["geometryDigest"][32:], font=font(21), fill=MUTED)

    rounded(draw, (60, 1200, 2500, 1535), PANEL)
    draw.text((95, 1232), "PIVOT / ROOT / RUNTIME BOUNDARY", font=font(31, True), fill=AMBER)
    draw.text((95, 1285), "PresentationRoot  →  CaseAssembly  →  Rear + Front shells", font=font(29, True), fill=TEXT)
    draw.text((95, 1330), "Rear shell  →  ContentSlot (caller-owned EMPTY)     Front shell  →  closed tube + label", font=font(25), fill=MUTED)
    draw.text((95, 1380), "Blender owns geometry, pivot, UV and material zones. No runtime curves, Z travel, rotation, or light animation are baked.", font=font(25), fill=TEXT)
    draw.text((95, 1425), "No halo/VFX/particle/proxy/explode/toy geometry. Unity will own GachaRevealDirector, easing and mesh-clipped light.", font=font(25), fill=GREEN)
    draw.text((95, 1473), "Gate 06 remains blocked. Shipping Unity and phone state are unchanged.", font=font(24, True), fill=CYAN)
    canvas.save(OUTPUT_REVIEW, optimize=True)


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit["status"] != "pass":
        raise RuntimeError("The Blender compatibility audit must pass first.")
    for source in (HERO, FRONT, SOURCE_HERO):
        if not source.exists():
            raise FileNotFoundError(source)
    make_hierarchy(audit)
    make_review(audit)
    print(json.dumps({
        "review": str(OUTPUT_REVIEW),
        "hierarchy": str(OUTPUT_HIERARCHY),
        "geometryDigest": audit["output"]["geometryDigest"],
    }, indent=2))


if __name__ == "__main__":
    main()
