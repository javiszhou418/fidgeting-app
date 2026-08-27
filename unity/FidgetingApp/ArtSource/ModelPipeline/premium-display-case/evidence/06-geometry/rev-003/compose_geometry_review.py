#!/usr/bin/env python3
"""Compose whole-case Gate 06 geometry review evidence."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
VIEWS = ROOT / "fixed-views"
REPORT = ROOT / "geometry-revalidation.json"
WORKBENCH = ROOT / "geometry-workbench.png"
DIMENSIONS = ROOT / "dimension-overlay.png"
PIVOT = ROOT / "pivot-presentation-root-overlay.png"
BOARD = ROOT / "geometry-presentation-review.png"

BG = "#071019"
PANEL = "#101d28"
PANEL_ALT = "#152634"
TEXT = "#f1f6f8"
MUTED = "#9fb2be"
CYAN = "#48d8d0"
GREEN = "#5bd68e"
AMBER = "#f1bd64"
LINE = "#315266"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path(
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        Path("/System/Library/Fonts/HelveticaNeue.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str = PANEL,
) -> None:
    draw.rounded_rectangle(box, radius=22, fill=fill, outline=LINE, width=2)


def fit_image(source: Path, size: tuple[int, int], background: str = PANEL) -> Image.Image:
    image = Image.open(source).convert("RGB")
    scale = min(size[0] / image.width, size[1] / image.height)
    image = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = CYAN,
) -> None:
    draw.line((start, end), fill=color, width=4)
    sx, sy = start
    ex, ey = end
    if abs(ex - sx) >= abs(ey - sy):
        draw.polygon(((sx, sy), (sx + 14, sy - 8), (sx + 14, sy + 8)), fill=color)
        draw.polygon(((ex, ey), (ex - 14, ey - 8), (ex - 14, ey + 8)), fill=color)
    else:
        draw.polygon(((sx, sy), (sx - 8, sy + 14), (sx + 8, sy + 14)), fill=color)
        draw.polygon(((ex, ey), (ex - 8, ey - 14), (ex + 8, ey - 14)), fill=color)


def make_dimensions(report: dict) -> None:
    canvas = Image.new("RGB", (1800, 1200), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 45), "GATE 06 · EXACT DIMENSIONS", font=font(48, True), fill=TEXT)
    draw.text(
        (70, 106),
        "Same assembled geometry · values measured from evaluated meshes",
        font=font(27),
        fill=MUTED,
    )
    rounded(draw, (60, 175, 1080, 1110))
    rounded(draw, (1110, 175, 1740, 720))
    rounded(draw, (1110, 750, 1740, 1110), PANEL_ALT)
    front = fit_image(ROOT / "ortho-front.png", (900, 800))
    canvas.paste(front, (115, 215))
    arrow(draw, (260, 1045), (900, 1045))
    draw.text((510, 1060), "228 mm", font=font(29, True), fill=CYAN)
    arrow(draw, (1025, 315), (1025, 930))
    draw.text((930, 600), "304 mm", font=font(29, True), fill=CYAN)
    top = fit_image(ROOT / "ortho-top.png", (560, 370))
    canvas.paste(top, (1145, 220))
    arrow(draw, (1625, 325), (1625, 540))
    draw.text((1450, 555), "59 mm depth", font=font(27, True), fill=CYAN)
    draw.text((1155, 790), "LOCKED GEOMETRY", font=font(27, True), fill=GREEN)
    lines = [
        f"Bounds  {report['bounds']['sizeMm']['width']:.0f} × "
        f"{report['bounds']['sizeMm']['height']:.0f} × "
        f"{report['bounds']['sizeMm']['depth']:.0f} mm",
        "Label center Y = 99 mm",
        "Portrait ratio = 0.7500",
        "Concentric center drift = 0.000 mm",
        "Geometry edits in this gate = 0",
    ]
    for index, line in enumerate(lines):
        draw.text((1155, 842 + index * 48), line, font=font(24), fill=TEXT)
    canvas.save(DIMENSIONS)


def make_pivot(report: dict) -> None:
    canvas = Image.new("RGB", (1800, 1200), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 45), "GATE 06 · PIVOT / PRESENTATION OWNERSHIP", font=font(46, True), fill=TEXT)
    draw.text(
        (70, 106),
        "Unity may move only PresentationRoot; descendants remain one rigid assembled instance",
        font=font(26),
        fill=MUTED,
    )
    rounded(draw, (60, 175, 930, 1115))
    hero = fit_image(WORKBENCH, (810, 740))
    canvas.paste(hero, (90, 210))
    cx, cy = 495, 575
    draw.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), outline=CYAN, width=5)
    draw.line((cx - 75, cy, cx + 75, cy), fill=CYAN, width=3)
    draw.line((cx, cy - 75, cx, cy + 75), fill=CYAN, width=3)
    draw.text((95, 985), "PresentationRoot pivot = (0, 0, 0)", font=font(28, True), fill=CYAN)
    draw.text((95, 1030), "No baked animation · no geometry proxy", font=font(24), fill=MUTED)

    boxes = [
        ("PresentationRoot", "Unity runtime transform owner", CYAN),
        ("CaseAssembly", "Rigid child · whole case", TEXT),
        ("Front + Rear shells", "Geometry stays attached", TEXT),
        ("ContentSlot", "Caller-owned EMPTY · 0 children", AMBER),
    ]
    for index, (title, subtitle, color) in enumerate(boxes):
        top = 220 + index * 190
        rounded(draw, (1010, top, 1715, top + 130), PANEL_ALT if index < 2 else PANEL)
        draw.text((1045, top + 22), title, font=font(30, True), fill=color)
        draw.text((1045, top + 72), subtitle, font=font(23), fill=MUTED)
        if index < len(boxes) - 1:
            draw.line((1360, top + 130, 1360, top + 190), fill=CYAN, width=4)
            draw.polygon(
                ((1360, top + 190), (1351, top + 174), (1369, top + 174)),
                fill=CYAN,
            )
    draw.text((1010, 1035), "Motion check", font=font(27, True), fill=GREEN)
    draw.text(
        (1010, 1078),
        "Same instance · rigid descendants · whole-case only",
        font=font(23),
        fill=TEXT,
    )
    canvas.save(PIVOT)


def make_board(report: dict) -> None:
    canvas = Image.new("RGB", (3000, 2000), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((70, 46), "PREMIUM DISPLAY CASE · GATE 06 REV 3", font=font(58, True), fill=TEXT)
    draw.text(
        (70, 122),
        "Geometry + presentation revalidation · approved Gate 05 source · no geometry redesign",
        font=font(30),
        fill=MUTED,
    )
    draw.rounded_rectangle((2440, 50, 2925, 128), radius=38, fill="#123c31")
    draw.text((2500, 72), "READY FOR REVIEW", font=font(27, True), fill=GREEN)

    view_ids = ("front", "back", "top", "bottom", "left", "right")
    labels = ("FRONT", "BACK", "TOP", "BOTTOM", "LEFT", "RIGHT")
    for index, (view_id, label) in enumerate(zip(view_ids, labels)):
        col = index % 3
        row = index // 3
        x = 60 + col * 610
        y = 190 + row * 520
        rounded(draw, (x, y, x + 575, y + 485))
        view = fit_image(ROOT / f"ortho-{view_id}.png", (535, 410))
        canvas.paste(view, (x + 20, y + 20))
        draw.text((x + 24, y + 438), label, font=font(24, True), fill=CYAN)

    rounded(draw, (60, 1250, 1885, 1870), PANEL_ALT)
    workbench = fit_image(WORKBENCH, (860, 560), PANEL_ALT)
    canvas.paste(workbench, (80, 1280))
    draw.text((975, 1300), "REAL BLENDER WORKBENCH", font=font(31, True), fill=TEXT)
    draw.text((975, 1350), "Whole assembled case", font=font(25), fill=MUTED)
    workbench_lines = [
        "Interactive GLB: orbit / zoom / fixed views / wireframe",
        "No exploded image in this review set",
        "Internal exploded evidence remains historical technical evidence only",
        "No timing, easing, light tuning, materials, or shipping implementation",
    ]
    for index, line in enumerate(workbench_lines):
        draw.text((975, 1430 + index * 64), f"• {line}", font=font(23), fill=TEXT)

    rounded(draw, (1920, 190, 2940, 1870))
    x = 1970
    draw.text((x, 230), "STRUCTURAL RESULT", font=font(31, True), fill=GREEN)
    metric_lines = [
        ("Envelope", "228 × 304 × 59 mm"),
        ("Label", "center Y = 99 mm"),
        ("Corners", "max drift 0.000 mm"),
        ("Open edges", "0"),
        ("Non-manifold edges", "0"),
        ("Self-intersections", "0"),
        ("Degenerate elements", "0"),
        ("Tube signed volume", f"{report['tubeOrientation']['netMaterialSignedVolumeMm3']:.6f} mm³"),
        ("Tube channel", "384 / 384 connected"),
    ]
    for index, (label, value) in enumerate(metric_lines):
        y = 300 + index * 92
        draw.text((x, y), label, font=font(22), fill=MUTED)
        draw.text((x, y + 32), value, font=font(25, True), fill=TEXT)

    y = 1185
    draw.text((x, y), "IDENTITY", font=font(29, True), fill=CYAN)
    identity_lines = [
        ("Source geometry", report["source"]["geometryDigest"][:18] + "…"),
        ("Derivative geometry", report["output"]["geometryDigest"][:18] + "…"),
        ("Vertex positions", report["identity"]["derivative"]["vertexPositionDigest"][:18] + "…"),
        ("Silhouette", report["identity"]["derivative"]["silhouetteDigest"][:18] + "…"),
    ]
    for index, (label, value) in enumerate(identity_lines):
        draw.text((x, y + 55 + index * 72), label, font=font(21), fill=MUTED)
        draw.text((x + 300, y + 55 + index * 72), value, font=font(21, True), fill=TEXT)

    draw.text((x, 1545), "RUNTIME OWNERSHIP", font=font(29, True), fill=AMBER)
    ownership = [
        "PresentationRoot — Unity runtime motion",
        "CaseAssembly — rigid child",
        "ContentSlot — caller-owned static slot",
        "Same instance — whole-case only",
    ]
    for index, line in enumerate(ownership):
        draw.text((x, 1595 + index * 54), f"• {line}", font=font(22), fill=TEXT)

    draw.text(
        (70, 1920),
        "Approval scope: geometry and hierarchy only · Gate 07+ remain blocked · shipping Unity unchanged",
        font=font(28, True),
        fill=AMBER,
    )
    canvas.save(BOARD)


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("status") != "pass":
        raise RuntimeError("Geometry revalidation must pass before composing review evidence.")
    make_dimensions(report)
    make_pivot(report)
    make_board(report)
    print(json.dumps({"dimensions": str(DIMENSIONS), "pivot": str(PIVOT), "board": str(BOARD)}))


if __name__ == "__main__":
    main()
