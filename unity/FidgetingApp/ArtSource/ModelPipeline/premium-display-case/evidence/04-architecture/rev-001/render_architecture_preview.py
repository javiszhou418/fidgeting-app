#!/usr/bin/env python3

import html
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PART_TREE_PATH = ROOT / "part-tree.svg"
EXPLODED_PLAN_PATH = ROOT / "exploded-plan.svg"
PREVIEW_PATH = ROOT / "architecture-preview.png"

WIDTH = 2800
HEIGHT = 3400
MINIMUM_BODY_FONT_PIXELS = 34

BG = "#0A0D12"
PANEL = "#141922"
PANEL_ALT = "#10151D"
LINE = "#323B49"
TEXT = "#F4F7FA"
MUTED = "#A7B1BF"
BLUE = "#74A8FF"
CYAN = "#73D5D0"
GREEN = "#69D4A9"
AMBER = "#F0BC66"
RED = "#F1777E"
PURPLE = "#B99AF4"

SOURCE_CLAIM_IDS = [
    "display-case-analysis-closed-loop-r002",
    "display-case-analysis-manifold-r002",
    "display-case-analysis-background-r002",
    "display-case-analysis-label-r002",
    "display-case-analysis-portrait-r002",
    "display-case-analysis-flow-r002",
    "display-case-analysis-environment-r002",
]

PART_TREE = [
    (0, "PresentationRoot", "transform root · MOTION OWNER", BLUE),
    (1, "CaseAssembly", "nonphysical group · always assembled", CYAN),
    (2, "RearPolycarbonateShell", "physical part", GREEN),
    (3, "TactileBackgroundInsert", "physical part · matte friction grain", GREEN),
    (3, "ContentSlot", "runtime anchor", AMBER),
    (4, "PrizeContent", "real runtime content · independent ω = 0", AMBER),
    (2, "FrontPolycarbonateShell", "physical part", GREEN),
    (3, "ContinuousTubePerimeter", "ONE connected physical part · never four bars", RED),
    (3, "PhysicalLabel", "physical part", PURPLE),
    (4, "LogoZone", "print zone · existing official identity", PURPLE),
    (4, "AchievementZone", "print zone · existing artwork", PURPLE),
    (4, "NarrowFoil", "material zone · non-emissive", PURPLE),
    (3, "TransparentCover", "physical part", GREEN),
]

EXPLODED_LAYERS = [
    ("TransparentCover", "physical front cover", "#B5D4E8"),
    ("PhysicalLabel", "logo + achievement + narrow foil zones", "#D8C7A4"),
    ("ContinuousTubePerimeter", "single connected closed tube", "#E4EEF4"),
    ("FrontPolycarbonateShell", "front physical shell", "#9DBCCB"),
    ("PrizeContent", "runtime child of ContentSlot · ω = 0", "#D8B67D"),
    ("TactileBackgroundInsert", "continuous matte friction surface", "#575C65"),
    ("RearPolycarbonateShell", "rear physical shell", "#8298A6"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
    return ImageFont.load_default()


F_TITLE = font(72, True)
F_H1 = font(48, True)
F_H2 = font(40, True)
F_BODY = font(38)
F_BODY_BOLD = font(38, True)
F_SMALL = font(MINIMUM_BODY_FONT_PIXELS)
F_SMALL_BOLD = font(MINIMUM_BODY_FONT_PIXELS, True)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = PANEL) -> None:
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=LINE, width=3)


def text_width(draw: ImageDraw.ImageDraw, value: str, typeface: ImageFont.ImageFont) -> int:
    return draw.textbbox((0, 0), value, font=typeface)[2]


def wrapped_lines(
    draw: ImageDraw.ImageDraw,
    value: str,
    typeface: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    current = ""
    for token in value.split(" "):
        candidate = token if not current else f"{current} {token}"
        if text_width(draw, candidate, typeface) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = token
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    typeface: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_height: int,
) -> int:
    x, y = xy
    for line in wrapped_lines(draw, value, typeface, max_width):
        draw.text((x, y), line, font=typeface, fill=fill)
        y += line_height
    return y


def svg_text(x: int, y: int, value: str, size: int, fill: str, weight: int = 400) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}" font-family="Arial, PingFang SC, sans-serif">'
        f"{html.escape(value)}</text>"
    )


def write_part_tree_svg() -> None:
    width = 1800
    height = 2200
    rows: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        svg_text(80, 105, "GATE 04 · PART TREE", 62, TEXT, 700),
        svg_text(80, 160, "Approved Gate 03 → architecture review only", 32, MUTED),
        f'<rect x="80" y="200" width="1640" height="76" rx="18" fill="{RED}"/>',
        svg_text(120, 252, "SHIPPING REVEAL NEVER EXPLODES", 36, BG, 700),
    ]
    y = 345
    for depth, name, note, color in PART_TREE:
        x = 105 + depth * 105
        if depth:
            rows.append(
                f'<path d="M {x - 62} {y - 45} V {y + 6} H {x - 14}" '
                f'stroke="{LINE}" stroke-width="4" fill="none"/>'
            )
        rows.append(f'<rect x="{x}" y="{y - 33}" width="34" height="34" rx="8" fill="{color}"/>')
        rows.append(svg_text(x + 55, y - 2, name, 34, TEXT, 700))
        rows.append(svg_text(x + 55, y + 39, note, 27, MUTED))
        y += 125
    rows.extend([
        f'<rect x="80" y="1990" width="1640" height="120" rx="22" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>',
        svg_text(120, 2040, "No invented fasteners · no hidden fluid hardware · no extra layers", 30, AMBER, 700),
        svg_text(120, 2085, "PresentationRoot and CaseAssembly are transform containers, not physical parts.", 27, MUTED),
        "</svg>",
    ])
    PART_TREE_PATH.write_text("\n".join(rows), encoding="utf-8")


def write_exploded_plan_svg() -> None:
    width = 1800
    height = 2200
    rows: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        svg_text(80, 105, "GATE 04 · INTERNAL EXPLODED PLAN", 58, TEXT, 700),
        svg_text(80, 160, "Production / website structure evidence only", 32, AMBER, 700),
        f'<rect x="80" y="200" width="1640" height="76" rx="18" fill="{RED}"/>',
        svg_text(120, 252, "NOT A GACHA OR COLLECTION ANIMATION", 36, BG, 700),
        svg_text(110, 345, "FRONT +Z", 30, BLUE, 700),
        svg_text(1460, 345, "REAR −Z", 30, BLUE, 700),
        f'<path d="M 270 325 H 1390" stroke="{BLUE}" stroke-width="5"/>',
        f'<path d="M 1390 325 l -28 -15 v 30 z" fill="{BLUE}"/>',
    ]
    y = 430
    for index, (name, note, color) in enumerate(EXPLODED_LAYERS):
        x = 120 + index * 70
        rows.append(
            f'<rect x="{x}" y="{y}" width="820" height="155" rx="30" '
            f'fill="{color}" fill-opacity="0.18" stroke="{color}" stroke-width="6"/>'
        )
        rows.append(svg_text(x + 35, y + 64, name, 34, TEXT, 700))
        rows.append(svg_text(x + 35, y + 112, note, 27, MUTED))
        if index < len(EXPLODED_LAYERS) - 1:
            rows.append(
                f'<path d="M {x + 860} {y + 77} H {x + 912}" '
                f'stroke="{LINE}" stroke-width="5"/>'
            )
            rows.append(
                f'<path d="M {x + 912} {y + 77} l -20 -11 v 22 z" fill="{LINE}"/>'
            )
        y += 205
    rows.extend([
        f'<rect x="80" y="1925" width="1640" height="190" rx="24" fill="{PANEL}" stroke="{LINE}" stroke-width="3"/>',
        svg_text(120, 1980, "Motion ownership", 34, BLUE, 700),
        svg_text(120, 2030, "PresentationRoot: assembled Y 0→360°, one highlight, hover.", 29, TEXT),
        svg_text(120, 2075, "PrizeContent: inherited root transform only; independent angular velocity = 0.", 29, TEXT),
        "</svg>",
    ])
    EXPLODED_PLAN_PATH.write_text("\n".join(rows), encoding="utf-8")


def draw_part_tree(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box)
    draw.text((x0 + 42, y0 + 34), "PART TREE · REAL PARENTING", font=F_H1, fill=TEXT)
    draw.text((x0 + 42, y0 + 98), "Containers are labeled; material zones are not extra parts.", font=F_SMALL, fill=MUTED)
    y = y0 + 175
    row_height = 133
    for depth, name, note, color in PART_TREE:
        x = x0 + 56 + depth * 76
        if depth:
            draw.line((x - 46, y - 56, x - 46, y + 11), fill=LINE, width=4)
            draw.line((x - 46, y + 11, x - 12, y + 11), fill=LINE, width=4)
        draw.rounded_rectangle((x, y - 10, x + 34, y + 24), radius=8, fill=color)
        draw.text((x + 52, y - 19), name, font=F_SMALL_BOLD, fill=TEXT)
        draw.text((x + 52, y + 27), note, font=F_SMALL, fill=MUTED)
        y += row_height
    draw.rounded_rectangle((x0 + 42, y1 - 120, x1 - 42, y1 - 38), radius=18, fill="#241D17")
    draw.text(
        (x0 + 72, y1 - 98),
        "Perimeter = 1 connected part. No four-edge children.",
        font=F_SMALL_BOLD,
        fill=AMBER,
    )


def draw_exploded_plan(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box, PANEL_ALT)
    draw.text((x0 + 42, y0 + 34), "INTERNAL EXPLODED PLAN", font=F_H1, fill=TEXT)
    draw.text((x0 + 42, y0 + 98), "Production / website structure evidence only.", font=F_SMALL_BOLD, fill=AMBER)
    draw.text((x0 + 42, y0 + 148), "FRONT +Z", font=F_SMALL_BOLD, fill=BLUE)
    draw.line((x0 + 240, y0 + 169, x1 - 95, y0 + 169), fill=BLUE, width=5)
    draw.polygon(
        [(x1 - 95, y0 + 169), (x1 - 125, y0 + 152), (x1 - 125, y0 + 186)],
        fill=BLUE,
    )
    draw.text((x1 - 220, y0 + 115), "REAR −Z", font=F_SMALL_BOLD, fill=BLUE)
    y = y0 + 245
    for index, (name, note, color) in enumerate(EXPLODED_LAYERS):
        x = x0 + 58 + index * 38
        layer_box = (x, y, x1 - 90 + index * 8, y + 160)
        draw.rounded_rectangle(layer_box, radius=28, fill="#18202A", outline=color, width=6)
        draw.text((x + 30, y + 28), name, font=F_SMALL_BOLD, fill=TEXT)
        draw_wrapped(draw, (x + 30, y + 78), note, F_SMALL, MUTED, layer_box[2] - x - 60, 43)
        if index < len(EXPLODED_LAYERS) - 1:
            draw.line((x1 - 60, y + 80, x1 - 35, y + 80), fill=LINE, width=5)
        y += 218
    draw.rounded_rectangle((x0 + 42, y1 - 260, x1 - 42, y1 - 38), radius=22, fill="#21171A", outline=RED, width=3)
    draw.text((x0 + 72, y1 - 232), "SHIPPING RED LINE", font=F_SMALL_BOLD, fill=RED)
    draw.text((x0 + 72, y1 - 178), "The real reveal stays assembled.", font=F_BODY_BOLD, fill=TEXT)
    draw.text((x0 + 72, y1 - 124), "No explode · no reassembly · no part animation.", font=F_SMALL, fill=MUTED)


def draw_motion_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box)
    draw.text((x0 + 42, y0 + 34), "MOTION OWNERSHIP + SCOPE BOUNDARY", font=F_H1, fill=TEXT)
    left = (x0 + 42, y0 + 118, x0 + 835, y1 - 42)
    center = (x0 + 875, y0 + 118, x0 + 1668, y1 - 42)
    right = (x0 + 1708, y0 + 118, x1 - 42, y1 - 42)
    for card_box, color in ((left, BLUE), (center, AMBER), (right, RED)):
        draw.rounded_rectangle(card_box, radius=24, fill=PANEL_ALT, outline=color, width=4)

    draw.text((left[0] + 30, left[1] + 28), "PresentationRoot OWNS", font=F_H2, fill=BLUE)
    draw_wrapped(
        draw,
        (left[0] + 30, left[1] + 95),
        "Whole assembled case: unwrapped Y 0→360° / 1.8 s, one 0.55 s highlight, then ±2 mm / 3.2 s hover.",
        F_SMALL,
        TEXT,
        left[2] - left[0] - 60,
        49,
    )

    draw.text((center[0] + 30, center[1] + 28), "PrizeContent NEVER OWNS", font=F_H2, fill=AMBER)
    draw_wrapped(
        draw,
        (center[0] + 30, center[1] + 95),
        "It remains below ContentSlot, inherits the root transform, keeps independent angular velocity at zero, and leaves mechanism state unchanged.",
        F_SMALL,
        TEXT,
        center[2] - center[0] - 60,
        49,
    )

    draw.text((right[0] + 30, right[1] + 28), "FORBIDDEN", font=F_H2, fill=RED)
    draw_wrapped(
        draw,
        (right[0] + 30, right[1] + 95),
        "Shipping explosion or reassembly; four-bar perimeter; idle prize spin; invented fasteners; hidden fluid hardware; extra layers.",
        F_SMALL,
        TEXT,
        right[2] - right[0] - 60,
        49,
    )


def render_preview() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.text((80, 52), "GATE 04 · PREMIUM DISPLAY CASE", font=F_TITLE, fill=TEXT)
    draw.text(
        (80, 144),
        "Architecture rev 1 · consumes approved Gate 03 rev 1 (‘批准’) · decision pending",
        font=F_BODY,
        fill=MUTED,
    )
    draw.rounded_rectangle((80, 215, WIDTH - 80, 310), radius=24, fill=RED)
    red_line = "SHIPPING REVEAL NEVER EXPLODES · Gate 05 remains blocked"
    red_width = text_width(draw, red_line, F_H1)
    draw.text(((WIDTH - red_width) // 2, 236), red_line, font=F_H1, fill=BG)

    draw_part_tree(draw, (80, 365, 1365, 2470))
    draw_exploded_plan(draw, (1435, 365, WIDTH - 80, 2470))
    draw_motion_panel(draw, (80, 2540, WIDTH - 80, 3260))

    footer = (
        f"3/12 approved · Gate 04 ready_for_review · {len(SOURCE_CLAIM_IDS)} source claims · "
        "shipping asset unchanged · no build / install / phone push"
    )
    draw.text((80, 3310), footer, font=F_SMALL, fill=MUTED)
    image.save(PREVIEW_PATH, format="PNG", optimize=True)


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    write_part_tree_svg()
    write_exploded_plan_svg()
    render_preview()
    print(json.dumps({
        "partTree": str(PART_TREE_PATH),
        "explodedPlan": str(EXPLODED_PLAN_PATH),
        "preview": str(PREVIEW_PATH),
        "previewSize": [WIDTH, HEIGHT],
        "minimumBodyFontPixels": MINIMUM_BODY_FONT_PIXELS,
        "sourceClaimIds": SOURCE_CLAIM_IDS,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
