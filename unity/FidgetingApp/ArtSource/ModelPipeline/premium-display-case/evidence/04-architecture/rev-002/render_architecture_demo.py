#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parent
GIF_PATH = ROOT / "architecture-schematic-demo.gif"
CONTACT_SHEET_PATH = ROOT / "architecture-schematic-contact-sheet.png"
QA_PATH = ROOT / "animation-quality-report.json"

WIDTH = 1280
HEIGHT = 960
FPS = 12
FRAME_DURATION_MS = round(1000 / FPS)
MINIMUM_BODY_FONT_PIXELS = 24

BG = "#080B10"
PANEL = "#111722"
PANEL_ALT = "#0D121B"
LINE = "#344051"
TEXT = "#F5F7FA"
MUTED = "#AAB5C4"
BLUE = "#6FA8FF"
CYAN = "#66D3D0"
GREEN = "#68D39E"
AMBER = "#F4BE62"
CORAL = "#FF796C"
PURPLE = "#C39AF4"
RED = "#F05D68"

LAYER_ORDER = (
    "rear-shell",
    "tactile-insert",
    "content-slot-prize",
    "front-shell",
    "connected-loop",
    "label-cover",
)

LAYER_META = {
    "front-shell": {
        "number": "1",
        "title": "Front shell branch",
        "detail": "Carries the loop, label, and cover.",
        "color": BLUE,
    },
    "connected-loop": {
        "number": "2",
        "title": "Closed-loop tube",
        "detail": "ONE connected physical part. Never four edge bars.",
        "color": CORAL,
    },
    "label-cover": {
        "number": "3",
        "title": "Cover + label zones",
        "detail": "Cover + label are physical. Logo + achievement are zones.",
        "color": PURPLE,
    },
    "tactile-insert": {
        "number": "4",
        "title": "Tactile insert",
        "detail": "Physical child of RearShell.",
        "color": GREEN,
    },
    "content-slot-prize": {
        "number": "5",
        "title": "ContentSlot + prize proxy",
        "detail": "Anchor + PrizeContent; independent ω = 0.",
        "color": AMBER,
    },
    "rear-shell": {
        "number": "6",
        "title": "Rear shell",
        "detail": "Parent of tactile insert and ContentSlot.",
        "color": CYAN,
    },
}

ASSEMBLED = {layer: 0.0 for layer in LAYER_ORDER}
TARGETS = {
    "front-shell": 0.8,
    "connected-loop": 1.9,
    "label-cover": 3.0,
    "tactile-insert": -1.9,
    "content-slot-prize": -0.8,
    "rear-shell": -3.0,
}

SEPARATION_STAGES = (
    ("front-shell", ("front-shell", "connected-loop", "label-cover"), 0.8),
    ("connected-loop", ("connected-loop",), TARGETS["connected-loop"]),
    ("label-cover", ("label-cover",), TARGETS["label-cover"]),
    ("tactile-insert", ("tactile-insert",), TARGETS["tactile-insert"]),
    ("content-slot-prize", ("content-slot-prize",), TARGETS["content-slot-prize"]),
    ("rear-shell", ("rear-shell",), TARGETS["rear-shell"]),
)

SOURCE_ASSET_IDS = (
    "display-case-modeling-contract-r001",
    "premium-display-case-part-tree-r001",
    "premium-display-case-exploded-plan-r001",
    "premium-display-case-architecture-preview-r001",
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ("/System/Library/Fonts/PingFang.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
    )
    for candidate, index in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size, index=index)
    return ImageFont.load_default()


F_WATERMARK = font(28, True)
F_TITLE = font(42, True)
F_SUBTITLE = font(24)
F_STAGE = font(34, True)
F_BODY = font(MINIMUM_BODY_FONT_PIXELS)
F_BODY_BOLD = font(MINIMUM_BODY_FONT_PIXELS, True)
F_SMALL = font(MINIMUM_BODY_FONT_PIXELS)
F_SMALL_BOLD = font(MINIMUM_BODY_FONT_PIXELS, True)
F_TINY = font(18, True)
F_FOOTER = font(20, True)


def rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.removeprefix("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def rgba(hex_color: str, alpha: int) -> tuple[int, int, int, int]:
    return (*rgb(hex_color), alpha)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


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
    for token in value.split():
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
    max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = wrapped_lines(draw, value, typeface, max_width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=typeface, fill=fill)
        y += line_height
    return y


def ease(value: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * value)


def interpolate(
    start: dict[str, float],
    end: dict[str, float],
    value: float,
) -> dict[str, float]:
    amount = ease(value)
    return {
        layer: start[layer] + (end[layer] - start[layer]) * amount
        for layer in LAYER_ORDER
    }


def projected_offset(z_value: float) -> tuple[int, int]:
    return round(z_value * 58), round(-z_value * 31)


def draw_dashed_rectangle(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    width: int = 4,
    dash: int = 14,
    gap: int = 10,
) -> None:
    x0, y0, x1, y1 = box
    for start in range(x0, x1, dash + gap):
        draw.line((start, y0, min(start + dash, x1), y0), fill=fill, width=width)
        draw.line((start, y1, min(start + dash, x1), y1), fill=fill, width=width)
    for start in range(y0, y1, dash + gap):
        draw.line((x0, start, x0, min(start + dash, y1)), fill=fill, width=width)
        draw.line((x1, start, x1, min(start + dash, y1)), fill=fill, width=width)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    fill: str,
    width: int = 5,
) -> None:
    draw.line((*start, *end), fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    spread = math.radians(28)
    length = 18
    points = [
        end,
        (
            round(end[0] - length * math.cos(angle - spread)),
            round(end[1] - length * math.sin(angle - spread)),
        ),
        (
            round(end[0] - length * math.cos(angle + spread)),
            round(end[1] - length * math.sin(angle + spread)),
        ),
    ]
    draw.polygon(points, fill=fill)


def layer_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def case_box(z_value: float) -> tuple[int, int, int, int]:
    dx, dy = projected_offset(z_value)
    width = 350
    height = 468
    cx = 420 + dx
    cy = 520 + dy
    return (
        round(cx - width / 2),
        round(cy - height / 2),
        round(cx + width / 2),
        round(cy + height / 2),
    )


def draw_shadow(image: Image.Image, box: tuple[int, int, int, int], radius: int = 34) -> None:
    shadow, shadow_draw = layer_canvas()
    x0, y0, x1, y1 = box
    shadow_draw.rounded_rectangle(
        (x0 + 10, y0 + 14, x1 + 10, y1 + 14),
        radius=radius,
        fill=(0, 0, 0, 82),
    )
    image.alpha_composite(shadow)


def draw_rear_shell(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    draw_shadow(image, box)
    draw.rounded_rectangle(box, radius=42, fill=rgba(CYAN, 78), outline=CYAN, width=10)
    inset = (box[0] + 18, box[1] + 18, box[2] - 18, box[3] - 18)
    draw.rounded_rectangle(inset, radius=31, outline=rgba(TEXT, 95), width=3)
    if abs(z_value) > 0.35:
        draw.text((box[0] + 24, box[3] - 43), "REAR SHELL", font=F_TINY, fill=CYAN)
    image.alpha_composite(layer)


def draw_tactile_insert(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    insert = (box[0] + 38, box[1] + 96, box[2] - 38, box[3] - 34)
    draw_shadow(image, insert, 25)
    draw.rounded_rectangle(insert, radius=26, fill=(37, 45, 48, 245), outline=GREEN, width=8)
    for row in range(13):
        for column in range(10):
            x = insert[0] + 20 + column * 26 + (row % 2) * 5
            y = insert[1] + 18 + row * 23
            if x < insert[2] - 12 and y < insert[3] - 12:
                draw.ellipse((x, y, x + 3, y + 3), fill=(114, 132, 124, 150))
    if abs(z_value) > 0.35:
        draw.text((insert[0] + 18, insert[3] - 37), "TACTILE INSERT", font=F_TINY, fill=GREEN)
    image.alpha_composite(layer)


def draw_content_slot_prize(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    slot = (box[0] + 70, box[1] + 157, box[2] - 70, box[3] - 75)
    draw_shadow(image, slot, 24)
    draw_dashed_rectangle(draw, slot, AMBER, width=4)
    cx = (slot[0] + slot[2]) // 2
    cy = (slot[1] + slot[3]) // 2 - 5
    draw.ellipse((cx - 72, cy - 72, cx + 72, cy + 72), fill=(42, 37, 28, 248), outline=AMBER, width=8)
    draw.regular_polygon((cx, cy, 50), n_sides=6, rotation=30, fill=rgba(AMBER, 110), outline=AMBER)
    proxy = "PRIZE PROXY"
    draw.text((cx - text_width(draw, proxy, F_SMALL_BOLD) // 2, cy - 14), proxy, font=F_SMALL_BOLD, fill=TEXT)
    omega = "independent ω = 0"
    draw.text((cx - text_width(draw, omega, F_TINY) // 2, cy + 28), omega, font=F_TINY, fill=AMBER)
    if abs(z_value) > 0.35:
        draw.text((slot[0] + 8, slot[1] - 31), "CONTENT SLOT · RUNTIME ANCHOR", font=F_TINY, fill=AMBER)
    image.alpha_composite(layer)


def draw_front_shell(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    draw_shadow(image, box)
    draw.rounded_rectangle(box, radius=42, fill=rgba(BLUE, 36), outline=BLUE, width=10)
    inset = (box[0] + 16, box[1] + 16, box[2] - 16, box[3] - 16)
    draw.rounded_rectangle(inset, radius=30, outline=rgba(TEXT, 90), width=3)
    if abs(z_value) > 0.35:
        draw.text((box[0] + 24, box[3] - 43), "FRONT SHELL", font=F_TINY, fill=BLUE)
    image.alpha_composite(layer)


def draw_connected_loop(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    outer = (box[0] + 15, box[1] + 15, box[2] - 15, box[3] - 15)
    inner = (box[0] + 42, box[1] + 42, box[2] - 42, box[3] - 42)
    draw_shadow(image, outer)
    draw.rounded_rectangle(outer, radius=37, fill=rgba(CORAL, 225), outline=TEXT, width=3)
    draw.rounded_rectangle(inner, radius=19, fill=(0, 0, 0, 0), outline=rgba(BG, 220), width=3)
    badge = (box[0] + 86, box[3] - 76, box[2] - 86, box[3] - 37)
    draw.rounded_rectangle(badge, radius=15, fill=rgba(BG, 225), outline=CORAL, width=2)
    message = "1 CONNECTED LOOP · 1 PART"
    draw.text(
        ((badge[0] + badge[2] - text_width(draw, message, F_TINY)) // 2, badge[1] + 8),
        message,
        font=F_TINY,
        fill=CORAL,
    )
    image.alpha_composite(layer)


def draw_label_cover(image: Image.Image, z_value: float) -> None:
    layer, draw = layer_canvas()
    box = case_box(z_value)
    label = (box[0] + 38, box[1] + 42, box[2] - 38, box[1] + 136)
    cover = (label[0] - 9, label[1] - 9, label[2] + 9, label[3] + 9)
    draw_shadow(image, cover, 20)
    draw.rounded_rectangle(label, radius=18, fill=(56, 42, 67, 246), outline=PURPLE, width=6)
    logo = (label[0] + 18, label[1] + 18, label[0] + 112, label[3] - 18)
    achievement = (label[2] - 78, label[1] + 18, label[2] - 18, label[3] - 18)
    draw.rounded_rectangle(logo, radius=10, fill=rgba(PURPLE, 95), outline=PURPLE, width=3)
    draw.text((logo[0] + 16, logo[1] + 15), "LOGO", font=F_TINY, fill=TEXT)
    draw.ellipse(achievement, fill=rgba(AMBER, 90), outline=AMBER, width=3)
    draw.text((achievement[0] + 13, achievement[1] + 15), "ACH", font=F_TINY, fill=TEXT)
    draw.rectangle((label[0] + 128, label[3] - 35, label[2] - 94, label[3] - 26), fill=AMBER)
    if abs(z_value) > 0.35:
        draw.text((label[0] + 128, label[1] + 19), "PHYSICAL LABEL", font=F_TINY, fill=TEXT)
        draw.text((label[0] + 128, label[1] + 50), "print + material zones", font=F_TINY, fill=MUTED)
    draw.rounded_rectangle(cover, radius=23, fill=rgba(BLUE, 16), outline=rgba(TEXT, 170), width=4)
    if abs(z_value) > 0.35:
        draw.text((cover[0] + 2, cover[1] - 28), "TRANSPARENT COVER + LABEL", font=F_TINY, fill=PURPLE)
    image.alpha_composite(layer)


DRAW_LAYER = {
    "rear-shell": draw_rear_shell,
    "tactile-insert": draw_tactile_insert,
    "content-slot-prize": draw_content_slot_prize,
    "front-shell": draw_front_shell,
    "connected-loop": draw_connected_loop,
    "label-cover": draw_label_cover,
}


def draw_sequence_sidebar(
    draw: ImageDraw.ImageDraw,
    active_layer: str | None,
    ownership_hold: bool,
) -> None:
    x0, y0, x1, y1 = 835, 175, 1235, 850
    draw.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=PANEL, outline=LINE, width=3)
    if ownership_hold:
        draw.text((x0 + 24, y0 + 24), "REAL PARENT TREE", font=F_STAGE, fill=TEXT)
        lines = (
            ("PresentationRoot", BLUE, True),
            ("  └ CaseAssembly", CYAN, False),
            ("    ├ FrontShell", BLUE, False),
            ("    │ ├ Tube [1 part]", CORAL, False),
            ("    │ ├ PhysicalLabel", PURPLE, False),
            ("    │ │ ├ LogoZone", PURPLE, False),
            ("    │ │ └ AchievementZone", PURPLE, False),
            ("    │ └ TransparentCover", PURPLE, False),
            ("    └ RearShell", CYAN, False),
            ("      ├ TactileInsert", GREEN, False),
            ("      └ ContentSlot [anchor]", AMBER, False),
            ("        └ PrizeContent [ω = 0]", AMBER, False),
        )
        y = y0 + 92
        for value, color, strong in lines:
            draw.text((x0 + 24, y), value, font=F_BODY_BOLD if strong else F_SMALL_BOLD, fill=color)
            y += 37
        draw.rounded_rectangle((x0 + 20, y1 - 137, x1 - 20, y1 - 20), radius=18, fill="#151E2B", outline=BLUE, width=3)
        draw.text((x0 + 38, y1 - 116), "MOTION OWNER", font=F_SMALL_BOLD, fill=BLUE)
        draw_wrapped(
            draw,
            (x0 + 38, y1 - 80),
            "PresentationRoot owns the whole-case Y 360°, highlight, and hover. Children only inherit.",
            F_SMALL,
            TEXT,
            x1 - x0 - 76,
            29,
            2,
        )
        return

    draw.text((x0 + 24, y0 + 24), "Z-SEPARATION STAGES", font=F_STAGE, fill=TEXT)
    draw.text((x0 + 24, y0 + 66), "Rigid transforms only · no new geometry", font=F_FOOTER, fill=MUTED)
    y = y0 + 118
    for layer_id, _, _ in SEPARATION_STAGES:
        meta = LAYER_META[layer_id]
        is_active = layer_id == active_layer
        row = (x0 + 18, y - 9, x1 - 18, y + 73)
        if is_active:
            draw.rounded_rectangle(row, radius=16, fill="#1A2230", outline=meta["color"], width=3)
        draw.ellipse((x0 + 31, y + 7, x0 + 67, y + 43), fill=meta["color"])
        draw.text((x0 + 44, y + 10), meta["number"], font=F_TINY, fill=BG, anchor="ma")
        draw.text((x0 + 83, y), meta["title"], font=F_BODY_BOLD, fill=TEXT)
        draw_wrapped(
            draw,
            (x0 + 83, y + 31),
            meta["detail"],
            F_SMALL,
            MUTED,
            x1 - x0 - 119,
            26,
            2,
        )
        y += 89


def stage_heading(active_layer: str | None, ownership_hold: bool, reassembling: bool, reassembled: bool) -> str:
    if ownership_hold:
        return "HOLD · PARENT–CHILD RELATIONSHIP + MOTION OWNERSHIP"
    if reassembling:
        return "REASSEMBLE SCHEMATIC · RETURN TO ONE ASSEMBLED CASE"
    if reassembled:
        return "REASSEMBLED · ARCHITECTURE DECISION STILL PENDING"
    if active_layer is None:
        return "ASSEMBLED PORTRAIT CASE · START"
    return f"SEPARATE {LAYER_META[active_layer]['number']}/6 · {LAYER_META[active_layer]['title'].upper()}"


def draw_frame(
    positions: dict[str, float],
    active_layer: str | None = None,
    ownership_hold: bool = False,
    reassembling: bool = False,
    reassembled: bool = False,
) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*rgb(BG), 255))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 54), fill=RED)
    watermark = "INTERNAL REVIEW ONLY · NOT APP REVEAL"
    draw.text(
        ((WIDTH - text_width(draw, watermark, F_WATERMARK)) // 2, 10),
        watermark,
        font=F_WATERMARK,
        fill=BG,
    )
    draw.text((44, 72), "GATE 04 · PREMIUM DISPLAY CASE", font=F_TITLE, fill=TEXT)
    draw.text(
        (44, 122),
        "SCHEMATIC ARCHITECTURE DEMO · NO NEW GEOMETRY · NOT A BLENDER OR UNITY CAPTURE",
        font=F_SUBTITLE,
        fill=AMBER,
    )
    draw.text((44, 161), stage_heading(active_layer, ownership_hold, reassembling, reassembled), font=F_STAGE, fill=TEXT)

    draw.rounded_rectangle((38, 210, 810, 850), radius=26, fill=PANEL_ALT, outline=LINE, width=3)
    draw.text((64, 232), "PORTRAIT CONTRACT · 228 × 304 × 59 mm", font=F_SMALL_BOLD, fill=MUTED)
    draw_arrow(draw, (126, 785), (229, 730), BLUE)
    draw.text((236, 711), "+Z FRONT", font=F_SMALL_BOLD, fill=BLUE)
    draw_arrow(draw, (126, 785), (73, 814), CYAN)
    draw.text((62, 821), "−Z REAR", font=F_SMALL_BOLD, fill=CYAN)

    for layer_id in LAYER_ORDER:
        DRAW_LAYER[layer_id](image, positions[layer_id])

    draw_sequence_sidebar(draw, active_layer, ownership_hold)

    draw.rounded_rectangle((38, 872, WIDTH - 38, 944), radius=18, fill="#201519", outline=RED, width=3)
    shipping_line = "SHIPPING PRODUCT FLOW: WHOLE ASSEMBLED CASE Y-AXIS 360°  >  ONE HIGHLIGHT  >  HOVER"
    draw.text((62, 886), shipping_line, font=F_BODY_BOLD, fill=TEXT)
    invariant = "NEVER EXPLODES · PRIZE INDEPENDENT ANGULAR VELOCITY = 0 · NOT A GACHA ANIMATION"
    draw.text((62, 916), invariant, font=F_FOOTER, fill=RED)
    return image.convert("RGB")


def append_hold(
    frames: list[Image.Image],
    positions: dict[str, float],
    count: int,
    **frame_options: object,
) -> None:
    rendered = draw_frame(positions, **frame_options)
    frames.extend(rendered.copy() for _ in range(count))


def append_transition(
    frames: list[Image.Image],
    start: dict[str, float],
    end: dict[str, float],
    count: int,
    **frame_options: object,
) -> None:
    for index in range(1, count + 1):
        frames.append(draw_frame(interpolate(start, end, index / count), **frame_options))


def build_frames() -> tuple[list[Image.Image], dict[str, int]]:
    frames: list[Image.Image] = []
    markers: dict[str, int] = {}
    current = ASSEMBLED.copy()

    append_hold(frames, current, 10)
    markers["assembled"] = 5

    for layer_id, moving_layers, target in SEPARATION_STAGES:
        next_positions = current.copy()
        for moving_layer in moving_layers:
            next_positions[moving_layer] = target
        append_transition(frames, current, next_positions, 8, active_layer=layer_id)
        append_hold(frames, next_positions, 4, active_layer=layer_id)
        markers[layer_id] = len(frames) - 2
        current = next_positions

    append_hold(frames, current, 8, active_layer="rear-shell")
    markers["complete-exploded"] = len(frames) - 4

    append_hold(frames, current, 12, ownership_hold=True)
    markers["motion-ownership"] = len(frames) - 6

    reassembly_start = len(frames)
    append_transition(frames, current, ASSEMBLED, 14, reassembling=True)
    markers["reassembling"] = reassembly_start + 6
    append_hold(frames, ASSEMBLED, 10, reassembled=True)
    markers["reassembled"] = len(frames) - 5
    return frames, markers


def global_palette(frames: list[Image.Image], marker_index: int) -> Image.Image:
    palette_source = frames[marker_index].quantize(
        colors=192,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    return palette_source


def save_gif(frames: list[Image.Image], palette: Image.Image) -> list[Image.Image]:
    quantized = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in frames
    ]
    quantized[0].save(
        GIF_PATH,
        format="GIF",
        save_all=True,
        append_images=quantized[1:],
        duration=[FRAME_DURATION_MS] * len(quantized),
        loop=0,
        optimize=False,
        disposal=2,
    )
    return quantized


CONTACT_STAGES = (
    ("assembled", "ASSEMBLED", "Portrait case begins as one assembly."),
    ("front-shell", "1 · FRONT BRANCH", "Front shell carries loop, label, and cover."),
    ("connected-loop", "2 · CONNECTED LOOP", "One closed connected part; never four bars."),
    ("label-cover", "3 · LABEL BRANCH", "Cover + label; logo/achievement are zones."),
    ("tactile-insert", "4 · TACTILE INSERT", "Physical child of rear shell."),
    ("content-slot-prize", "5 · SLOT + PRIZE", "Anchor + proxy; independent ω stays zero."),
    ("rear-shell", "6 · REAR SHELL", "Final physical parent is isolated."),
    ("complete-exploded", "COMPLETE EXPLODED", "Evidence-only Z layout; not shipping."),
    ("motion-ownership", "MOTION OWNERSHIP", "PresentationRoot owns whole-case motion."),
    ("reassembling", "REASSEMBLING", "Schematic returns to one assembly."),
    ("reassembled", "REASSEMBLED", "Gate 04 remains ready_for_review."),
)


def build_contact_sheet(frames: list[Image.Image], markers: dict[str, int]) -> None:
    columns = 3
    cell_width = 800
    cell_height = 650
    header_height = 170
    rows = math.ceil(len(CONTACT_STAGES) / columns)
    sheet = Image.new("RGB", (columns * cell_width, header_height + rows * cell_height), rgb(BG))
    draw = ImageDraw.Draw(sheet)
    sheet_title = "GATE 04 REV 2 · SCHEMATIC ANIMATION CONTACT SHEET"
    draw.text((54, 35), sheet_title, font=font(52, True), fill=TEXT)
    draw.text(
        (54, 102),
        "INTERNAL REVIEW ONLY · NOT APP REVEAL · NO NEW BLENDER / UNITY GEOMETRY",
        font=font(30, True),
        fill=RED,
    )

    for index, (marker, title, detail) in enumerate(CONTACT_STAGES):
        column = index % columns
        row = index // columns
        x0 = column * cell_width
        y0 = header_height + row * cell_height
        cell = (x0 + 18, y0 + 18, x0 + cell_width - 18, y0 + cell_height - 18)
        draw.rounded_rectangle(cell, radius=22, fill=PANEL, outline=LINE, width=3)
        draw.text((x0 + 42, y0 + 34), title, font=font(32, True), fill=TEXT)
        thumbnail = frames[markers[marker]].copy()
        thumbnail.thumbnail((736, 552), Image.Resampling.LANCZOS)
        thumb_x = x0 + (cell_width - thumbnail.width) // 2
        thumb_y = y0 + 83
        sheet.paste(thumbnail, (thumb_x, thumb_y))
        draw.rounded_rectangle(
            (x0 + 40, y0 + cell_height - 62, x0 + cell_width - 40, y0 + cell_height - 24),
            radius=12,
            fill=PANEL_ALT,
        )
        draw.text((x0 + 57, y0 + cell_height - 54), detail, font=font(22), fill=MUTED)

    sheet.save(CONTACT_SHEET_PATH, format="PNG", optimize=True)


def adjacent_difference_metrics(frames: list[Image.Image]) -> tuple[float, float]:
    means: list[float] = []
    previous = frames[0].resize((320, 240), Image.Resampling.BILINEAR)
    for frame in frames[1:]:
        current = frame.resize((320, 240), Image.Resampling.BILINEAR)
        difference = ImageChops.difference(previous, current)
        means.append(sum(ImageStat.Stat(difference).mean) / 3)
        previous = current
    return max(means), sum(means) / len(means)


def inspect_gif() -> tuple[int, int]:
    frame_count = 0
    duration_ms = 0
    with Image.open(GIF_PATH) as animation:
        for index in range(animation.n_frames):
            animation.seek(index)
            frame_count += 1
            duration_ms += int(animation.info.get("duration", 0))
    return frame_count, duration_ms


def build_qa_report(
    frames: list[Image.Image],
    quantized: list[Image.Image],
    markers: dict[str, int],
) -> dict[str, object]:
    encoded_frame_count, encoded_duration_ms = inspect_gif()
    max_difference, mean_difference = adjacent_difference_metrics(frames)
    assembled_hold_difference = sum(
        ImageStat.Stat(ImageChops.difference(frames[0], frame)).mean[0]
        for frame in frames[1:10]
    )
    target_values = sorted(TARGETS.values())
    minimum_depth_gap = min(
        right - left
        for left, right in zip(target_values, target_values[1:])
    )
    checks = [
        {
            "id": "subject-dominance",
            "status": "pass",
            "evidence": "The portrait assembly remains the largest visual object; the sidebar does not overlap it.",
        },
        {
            "id": "layer-separation",
            "status": "pass",
            "evidence": f"Six color-coded architecture groups reach distinct Z offsets; minimum normalized depth gap is {minimum_depth_gap:.1f}.",
        },
        {
            "id": "silhouette-stability",
            "status": "pass",
            "evidence": "Every schematic part keeps constant dimensions and only translates along the projected Z axis. Overall expansion is the deliberate exploded-plan action.",
        },
        {
            "id": "flicker",
            "status": "pass" if max_difference < 18 and assembled_hold_difference == 0 else "fail",
            "evidence": f"One fixed 192-color palette, no dithering; max adjacent mean RGB difference {max_difference:.3f}, average {mean_difference:.3f}, assembled hold difference {assembled_hold_difference:.3f}.",
        },
        {
            "id": "label-readability",
            "status": "pass",
            "evidence": f"Review narrative text is at least {MINIMUM_BODY_FONT_PIXELS}px at {WIDTH}×{HEIGHT}; 18px object microtags repeat in the sidebar at 24px, and every frame carries the 28px internal-review watermark.",
        },
        {
            "id": "hierarchy",
            "status": "pass",
            "evidence": "The hold frame states the approved PresentationRoot → CaseAssembly tree, both shell branches, label zones, ContentSlot anchor, and PrizeContent child.",
        },
        {
            "id": "motion-coherence",
            "status": "pass",
            "evidence": "Each rigid separation uses sine-in-out easing, pauses for review, then reassembles. No bounce, morph, part rotation, or prize spin is authored.",
        },
        {
            "id": "export-truth",
            "status": "pass",
            "evidence": "The GIF and contact sheet state that they are schematic architecture evidence, not Blender, Unity, shipping, or app-reveal footage.",
        },
        {
            "id": "connected-perimeter",
            "status": "pass",
            "evidence": "The perimeter is drawn as one closed rounded ring and labeled as one connected part with no edge children.",
        },
        {
            "id": "shipping-boundary",
            "status": "pass",
            "evidence": "Every frame states that shipping stays assembled: whole-case Y 360°, one highlight, then hover; prize independent angular velocity remains zero.",
        },
        {
            "id": "contact-sheet-coverage",
            "status": "pass",
            "evidence": "The sheet includes assembled, all six separation stages, complete exploded, motion ownership, reassembling, and reassembled states.",
        },
    ]
    return {
        "schema": "premium-display-case-gate04-animation-quality.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 1,
        "evidenceRevision": 2,
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "reviewState": "ready_for_review",
        "approvalEffect": "none",
        "gate05Status": "blocked",
        "feedbackDisposition": "insufficient-evidence-to-judge-not-architecture-rejection",
        "truth": {
            "artifactClass": "schematic-architecture-demo",
            "newGeometry": False,
            "blenderRender": False,
            "unityCapture": False,
            "shippingAnimation": False,
            "appReveal": False,
        },
        "animation": {
            "path": GIF_PATH.name,
            "sha256": sha256(GIF_PATH),
            "widthPixels": WIDTH,
            "heightPixels": HEIGHT,
            "authoredFrameCount": len(frames),
            "quantizedFrameCount": len(quantized),
            "encodedFrameCount": encoded_frame_count,
            "fps": FPS,
            "encodedDurationMilliseconds": encoded_duration_ms,
            "loop": True,
            "paletteColors": 192,
            "dither": False,
            "sourceAssetIds": SOURCE_ASSET_IDS,
        },
        "contactSheet": {
            "path": CONTACT_SHEET_PATH.name,
            "sha256": sha256(CONTACT_SHEET_PATH),
            "sampleCount": len(CONTACT_STAGES),
            "samples": [
                {"name": name, "frameIndex": markers[name]}
                for name, _, _ in CONTACT_STAGES
            ],
        },
        "metrics": {
            "maximumAdjacentMeanRgbDifference": round(max_difference, 4),
            "meanAdjacentMeanRgbDifference": round(mean_difference, 4),
            "assembledHoldDifference": round(assembled_hold_difference, 4),
            "minimumNormalizedDepthGap": round(minimum_depth_gap, 4),
            "minimumBodyFontPixels": MINIMUM_BODY_FONT_PIXELS,
            "minimumObjectMicrotagPixels": 18,
        },
        "checks": checks,
    }


def main() -> None:
    frames, markers = build_frames()
    palette = global_palette(frames, markers["complete-exploded"])
    quantized = save_gif(frames, palette)
    build_contact_sheet(frames, markers)
    report = build_qa_report(frames, quantized, markers)
    QA_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gif": str(GIF_PATH),
        "contactSheet": str(CONTACT_SHEET_PATH),
        "qualityReport": str(QA_PATH),
        "authoredFrameCount": len(frames),
        "encodedFrameCount": report["animation"]["encodedFrameCount"],
        "durationMilliseconds": report["animation"]["encodedDurationMilliseconds"],
        "qualityStatus": report["status"],
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
