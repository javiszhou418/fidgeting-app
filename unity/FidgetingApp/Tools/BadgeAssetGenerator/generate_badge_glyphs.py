#!/usr/bin/env python3
"""Generate the approved rounded-monoline Badge glyph catalog.

The output deliberately contains no baked milestone text. Runtime typography owns
displayToken/displayUnit so every numeric badge shares one baseline and font size.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "Artifacts" / "BadgeSpecial" / "VectorGlyphs"
PREVIEWS = ROOT / "Artifacts" / "BadgeSpecial" / "Concepts"


@dataclass(frozen=True)
class Glyph:
    asset_id: str
    title: str
    detail: str
    category: str
    markup: str
    color: str = "violet"


P = lambda d: f'<path d="{d}"/>'
C = lambda cx, cy, r: f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
R = lambda x, y, w, h, rx: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>'
L = lambda x1, y1, x2, y2: f'<path d="M{x1} {y1}L{x2} {y2}"/>'


def arrow(tails: int, orbit: bool = False) -> str:
    parts = [P("M42 80h70M89 57l23 23-23 23")]
    if tails >= 1:
        parts.append(P("M39 50c22-15 54-15 76 0"))
    if tails >= 2:
        parts.append(P("M39 110c22 15 54 15 76 0"))
    if orbit:
        parts.append(P("M53 39a49 49 0 0 1 67 15M107 121a49 49 0 0 1-67-15"))
    return "".join(parts)


def pulse(level: int) -> str:
    if level == 1:
        return P("M42 87c21-22 55-22 76 0")
    if level == 2:
        return P("M47 70c18-17 48-17 66 0M35 96c25-27 65-27 90 0")
    if level == 3:
        return P("M32 88h23l12-25 19 46 17-35 12 14h13")
    return P("M31 80c12-35 28-35 40 0s28 35 40 0 18-35 18 0")


def links(energy: int = 0) -> str:
    base = (
        '<g transform="translate(36 55) rotate(-22 44 25)">'
        + R(0, 0, 60, 40, 20)
        + R(31, 10, 60, 40, 20)
        + "</g>"
    )
    if energy == 1:
        base += P("M48 117c20 12 44 12 64 0")
    elif energy == 2:
        base += P("M38 40c26-16 58-16 84 0M46 121c22 13 46 13 68 0")
    elif energy == 3:
        base += P("M80 29v15M80 116v15M28 80h15M117 80h15")
    return base


def focus(level: int) -> str:
    end = ["M54 45a45 45 0 1 1-8 69", "M45 54a45 45 0 1 1 69 60", "M39 68a45 45 0 1 1 18 54", "M50 43a45 45 0 1 1-8 70"]
    marks = ["M80 80v-24", "M80 80l18-18", "M80 80l22 8", "M80 80l-17 22"]
    return P(end[level - 1]) + C(80, 80, 13) + P(marks[level - 1])


def rhythm(peaks: int) -> str:
    if peaks == 1:
        return P("M28 84h30l18-36 24 72 17-36h15")
    if peaks == 2:
        return P("M24 88h20l13-30 18 51 17-62 19 41h25")
    return P("M23 87h15l10-22 16 43 16-58 16 58 16-43 10 22h15")


def explore(nodes: int) -> str:
    if nodes == 2:
        return C(49, 80, 13) + C(111, 80, 13) + L(62, 80, 98, 80)
    if nodes == 3:
        return C(80, 39, 12) + C(43, 105, 12) + C(117, 105, 12) + P("M73 50L50 94M87 50l23 44M56 105h48")
    return C(80, 34, 10) + C(123, 65, 10) + C(107, 116, 10) + C(53, 116, 10) + C(37, 65, 10) + P("M80 44l33 24-13 38H60L47 68z")


def mastery(cores: int, apex: bool) -> str:
    outer = P("M80 29l42 24v54l-42 24-42-24V53z")
    if cores == 1:
        inner = C(80, 80, 15) if apex else P("M80 55l22 13v25l-22 13-22-13V68z")
    else:
        inner = C(80, 55, 10) + C(60, 93, 10) + C(100, 93, 10)
        if apex:
            inner += P("M80 65L67 83M80 65l13 18M70 93h20")
    return outer + inner


def collection(layers: int) -> str:
    offsets = [(34, 42), (58, 58), (48, 29), (72, 45)][:layers]
    return "".join(R(x, y, 58, 58, 18) for x, y in offsets)


GLYPHS = [
    Glyph("toy_power_ignition", "POWER I", "1.0 / 0.35", "POWER", arrow(0), "cyan"),
    Glyph("toy_power_overdrive", "POWER II", "2.0 / 0.55", "POWER", arrow(1), "cyan"),
    Glyph("toy_power_apex", "POWER III", "3.5 / 0.75", "POWER", arrow(2), "cyan"),
    Glyph("toy_power_singularity", "POWER IV", "4.5 / 0.90", "POWER", arrow(0, True), "cyan"),
    Glyph("toy_pulse_100", "PULSE I", "100", "PULSE", pulse(1)),
    Glyph("toy_pulse_1k", "PULSE II", "1K", "PULSE", pulse(2)),
    Glyph("toy_pulse_10k", "PULSE III", "10K", "PULSE", pulse(3)),
    Glyph("toy_pulse_100k", "PULSE IV", "100K", "PULSE", pulse(4)),
    Glyph("toy_technique_clean", "CLEAN", "TECHNIQUE", "TECHNIQUE", P("M46 84l20 20 49-53") + P("M43 46c22-17 52-17 74 0")),
    Glyph("toy_technique_power", "POWER MOVE", "TECHNIQUE", "TECHNIQUE", P("M80 27l14 35 35 14-35 14-14 35-14-35-35-14 35-14z")),
    Glyph("toy_technique_speed", "SPEED MOVE", "TECHNIQUE", "TECHNIQUE", P("M32 54l31 26-31 26M72 54l31 26-31 26M111 54l18 26-18 26"), "cyan"),
    Glyph("toy_technique_endurance", "ENDURANCE", "TECHNIQUE", "TECHNIQUE", P("M29 80c13-28 34-28 51 0s38 28 51 0-8-28-25-28c-17 0-30 28-51 56-38 28-51 0")),
    Glyph("toy_technique_perfect", "PERFECT", "TECHNIQUE", "TECHNIQUE", P("M80 29l14 37 37 14-37 14-14 37-14-37-37-14 37-14z") + C(80, 80, 13)),
    Glyph("toy_combo_5", "COMBO I", "×5", "COMBO", links(0)),
    Glyph("toy_combo_10", "COMBO II", "×10", "COMBO", links(1)),
    Glyph("toy_combo_20", "COMBO III", "×20", "COMBO", links(2)),
    Glyph("toy_combo_50", "COMBO IV", "×50", "COMBO", links(3)),
    Glyph("toy_focus_5m", "FOCUS I", "5m", "FOCUS", focus(1), "cyan"),
    Glyph("toy_focus_30m", "FOCUS II", "30m", "FOCUS", focus(2), "cyan"),
    Glyph("toy_focus_2h", "FOCUS III", "2h", "FOCUS", focus(3), "cyan"),
    Glyph("toy_focus_10h", "FOCUS IV", "10h", "FOCUS", focus(4), "cyan"),
    Glyph("collector_rhythm_1w", "RHYTHM I", "1W", "RHYTHM", rhythm(1)),
    Glyph("collector_rhythm_4w", "RHYTHM II", "4W", "RHYTHM", rhythm(2)),
    Glyph("collector_rhythm_12w", "RHYTHM III", "12W", "RHYTHM", rhythm(3)),
    Glyph("collector_explore_2", "EXPLORE I", "2 MODELS", "EXPLORE", explore(2), "cyan"),
    Glyph("collector_explore_3", "EXPLORE II", "3 MODELS", "EXPLORE", explore(3), "cyan"),
    Glyph("collector_explore_5", "EXPLORE III", "5 MODELS", "EXPLORE", explore(5), "cyan"),
    Glyph("collector_mastery_1_lv20", "MASTERY I", "1 × LV.20", "MASTERY", mastery(1, False)),
    Glyph("collector_mastery_3_lv20", "MASTERY II", "3 × LV.20", "MASTERY", mastery(3, False)),
    Glyph("collector_mastery_1_lv100", "MASTERY III", "1 × LV.100", "MASTERY", mastery(1, True)),
    Glyph("collector_mastery_3_lv100", "MASTERY IV", "3 × LV.100", "MASTERY", mastery(3, True)),
    Glyph("collector_collection_5", "VAULT I", "5 LOOKS", "COLLECTION", collection(2), "gold"),
    Glyph("collector_collection_10", "VAULT II", "10 LOOKS", "COLLECTION", collection(3), "gold"),
    Glyph("collector_collection_25", "VAULT III", "25 LOOKS", "COLLECTION", collection(4), "gold"),
    Glyph("challenge_redline", "REDLINE", "WEEK 1", "CHALLENGE", P("M35 105l41-60 17 32h34M104 54l23 23-23 23") + L(32, 119, 128, 119), "cyan"),
    Glyph("challenge_chain_reactor", "CHAIN REACTOR", "WEEK 2", "CHALLENGE", links(2) + C(80, 80, 9)),
    Glyph("challenge_perfect_protocol", "PERFECT PROTOCOL", "WEEK 3", "CHALLENGE", P("M80 28l14 38 38 14-38 14-14 38-14-38-38-14 38-14z") + C(80, 80, 14)),
    Glyph("challenge_three_core_raid", "THREE-CORE RAID", "WEEK 4", "CHALLENGE", C(80, 36, 13) + C(43, 105, 13) + C(117, 105, 13) + P("M73 48L51 93M87 48l22 45M56 105h48"), "cyan"),
    Glyph("challenge_cycle_total", "CYCLE COMPLETE", "4 / 4", "CHALLENGE", C(80, 80, 45) + C(80, 35, 9) + C(125, 80, 9) + C(80, 125, 9) + C(35, 80, 9), "gold"),
    Glyph("legacy_founder", "FOUNDER", "LEGACY", "LEGACY", P("M80 29l38 19v37c0 24-15 38-38 48-23-10-38-24-38-48V48z") + P("M58 81l14 14 31-34"), "gold"),
]


def defs() -> str:
    return """
  <defs>
    <linearGradient id="violet" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#8062ff"/><stop offset=".5" stop-color="#c58cff"/><stop offset="1" stop-color="#6b55e8"/></linearGradient>
    <linearGradient id="cyan" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#91f4ff"/><stop offset="1" stop-color="#5087ff"/></linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff2c9"/><stop offset="1" stop-color="#d5a65a"/></linearGradient>
    <radialGradient id="core"><stop stop-color="#8c5cff" stop-opacity=".28"/><stop offset="1" stop-color="#14141f" stop-opacity=".98"/></radialGradient>
    <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity=".55"/></filter>
  </defs>"""


def individual_svg(glyph: Glyph) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 160 160">
{defs()}
  <g fill="none" stroke="url(#{glyph.color})" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">
    {glyph.markup}
  </g>
</svg>
'''


def sheet_svg(title: str, glyphs: list[Glyph], columns: int) -> str:
    width = height = 1254
    margin = 28
    gap = 16
    top = 150
    bottom = 66
    rows = (len(glyphs) + columns - 1) // columns
    cell_w = (width - margin * 2 - gap * (columns - 1)) / columns
    cell_h = (height - top - bottom - gap * (rows - 1)) / rows
    icon_size = min(116, cell_w - 36, cell_h - 112)
    items: list[str] = []
    for index, glyph in enumerate(glyphs):
        row, column = divmod(index, columns)
        x = margin + column * (cell_w + gap)
        y = top + row * (cell_h + gap)
        frame_x = x + (cell_w - icon_size) / 2
        frame_y = y + 22
        scale = icon_size / 160
        title_y = frame_y + icon_size + 39
        detail_y = title_y + 25
        items.append(f'''<g>
  <rect x="{x:.2f}" y="{y:.2f}" width="{cell_w:.2f}" height="{cell_h:.2f}" rx="26" fill="#fff" fill-opacity=".018" stroke="#fff" stroke-opacity=".08"/>
  <g transform="translate({frame_x:.2f} {frame_y:.2f}) scale({scale:.5f})" filter="url(#shadow)">
    <rect width="160" height="160" rx="52" fill="url(#core)" stroke="#b8b3c8" stroke-width="5"/>
    <g fill="none" stroke="url(#{glyph.color})" stroke-width="10" stroke-linecap="round" stroke-linejoin="round">{glyph.markup}</g>
  </g>
  <text x="{x + cell_w / 2:.2f}" y="{title_y:.2f}" class="label" font-size="15">{escape(glyph.title)}</text>
  <text x="{x + cell_w / 2:.2f}" y="{detail_y:.2f}" class="meta" font-size="12">{escape(glyph.detail)}</text>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
{defs()}
  <style>
    @font-face {{ font-family: Oxanium; src: url('../../../Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf'); }}
    .heading, .label {{ font-family: Oxanium, -apple-system, sans-serif; font-weight: 700; text-anchor: middle; fill: #f6f3ff; }}
    .meta {{ font-family: Oxanium, -apple-system, sans-serif; font-weight: 560; text-anchor: middle; fill: #888395; }}
  </style>
  <rect width="1254" height="1254" fill="#0b0c13"/>
  <text x="627" y="64" class="heading" font-size="25">{escape(title)}</text>
  <text x="627" y="96" class="meta" font-size="14">ROUNDED MONOLINE · SEMANTIC GLYPH · NO BAKED MILESTONE TEXT</text>
  {''.join(items)}
</svg>
'''


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    for glyph in GLYPHS:
        (OUTPUT / f"{glyph.asset_id}.svg").write_text(individual_svg(glyph), encoding="utf-8")

    manifest = {
        "version": 1,
        "visualLanguage": "rounded-monoline",
        "canvas": {"width": 1024, "height": 1024, "colorSpace": "sRGB", "transparent": True},
        "geometry": {"viewBox": "0 0 160 160", "strokeWidth": 10, "lineCap": "round", "lineJoin": "round"},
        "milestoneTypography": "Runtime BadgeMilestoneToken; never baked into glyph artwork",
        "assets": [
            {
                "id": glyph.asset_id,
                "title": glyph.title,
                "previewDetail": glyph.detail,
                "category": glyph.category,
                "palette": glyph.color,
                "svg": f"{glyph.asset_id}.svg",
                "png": f"{glyph.asset_id}.png",
            }
            for glyph in GLYPHS
        ],
    }
    (OUTPUT / "badge-glyph-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    toy = [glyph for glyph in GLYPHS if glyph.asset_id.startswith("toy_")]
    collector = [glyph for glyph in GLYPHS if glyph.asset_id.startswith("collector_")]
    special = [glyph for glyph in GLYPHS if glyph.asset_id.startswith(("challenge_", "legacy_"))]
    (PREVIEWS / "badge-glyph-catalog-toy.svg").write_text(sheet_svg("21 TOY ACHIEVEMENTS", toy, 7), encoding="utf-8")
    (PREVIEWS / "badge-glyph-catalog-collector.svg").write_text(sheet_svg("13 COLLECTOR ACHIEVEMENTS", collector, 5), encoding="utf-8")
    (PREVIEWS / "badge-glyph-catalog-challenge.svg").write_text(sheet_svg("CHALLENGE + LEGACY", special, 3), encoding="utf-8")
    print(f"Generated {len(GLYPHS)} SVG glyphs, manifest, and 3 contact sheets in {OUTPUT.parent}")


if __name__ == "__main__":
    main()
