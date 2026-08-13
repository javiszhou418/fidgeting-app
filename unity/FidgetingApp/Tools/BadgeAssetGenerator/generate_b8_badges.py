#!/usr/bin/env python3
"""Generate the approved B8 diffuse-chrome production glyph catalog.

The artwork is deliberately text-free. The shipping SwiftUI badge component owns
the two permitted text baselines: milestone token and short semantic name.
"""

from __future__ import annotations

from dataclasses import dataclass
import base64
from html import escape
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "Assets" / "Plugins" / "iOS" / "BadgeArtwork"
ARTIFACTS = ROOT / "Artifacts" / "BadgeSpecial" / "ProductionB8"


@dataclass(frozen=True)
class BadgeArt:
    asset_id: str
    category: str
    grade: str
    token: str
    short_name: str
    markup: str

    @property
    def asset_name(self) -> str:
        return f"badge-b8-{self.asset_id.replace('_', '-')}"


def tube(path: str, transform: str = "") -> str:
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'''<g{transform_attr}>
      <path class="tubeBloom" d="{path}"/>
      <path class="tubeDark" d="{path}"/>
      <path class="tubeBody" d="{path}"/>
      <path class="tubeShade" d="{path}"/>
      <path class="tubeLight" d="{path}"/>
    </g>'''


def plate(path: str, transform: str = "") -> str:
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'''<g{transform_attr}>
      <path class="plateBloom" d="{path}"/>
      <path class="plateShadow" d="{path}"/>
      <path class="plateDepth" d="{path}"/>
      <path class="plateBody" d="{path}"/>
      <path class="plateEdge" d="{path}"/>
    </g>'''


def symmetric_plate(path: str) -> str:
    """A chrome plate whose lighting is invariant across the y=80 mirror."""
    return f'''<g>
      <path class="plateBloom" d="{path}"/>
      <path d="{path}" fill="#151a1e" stroke="#151a1e" stroke-width="3.2" stroke-linejoin="round"/>
      <path d="{path}" fill="url(#chromeSymmetric)" stroke="#727a7f" stroke-width=".75" stroke-linejoin="round"/>
      <path d="{path}" fill="none" stroke="#ffffff" stroke-width=".72" stroke-linejoin="round" opacity=".58"/>
    </g>'''


def orb(cx: int, cy: int, radius: int) -> str:
    return f'''<g>
      <circle class="orbBloom" cx="{cx}" cy="{cy}" r="{radius + 4}"/>
      <circle class="orbBody" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="orbGlint" cx="{cx - radius * .28:.1f}" cy="{cy - radius * .32:.1f}" r="{max(2, radius * .22):.1f}"/>
    </g>'''


def ring(cx: int, cy: int, radius: int) -> str:
    """A true circular chrome tube; never substitute an ellipse."""
    return f'''<g>
      <circle class="tubeBloom" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeDark" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeBody" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeShade" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeLight" cx="{cx}" cy="{cy}" r="{radius}"/>
    </g>'''


def fins(count: int, orbit: bool = False) -> str:
    paths = [
        "M31 94C50 72 69 59 96 47C91 60 82 70 70 79C91 76 111 70 132 61C117 83 91 99 58 108Z",
        "M39 70C58 54 78 43 106 34C100 46 91 56 80 64C99 61 116 56 132 50C119 68 96 80 69 88Z",
        "M48 116C66 94 88 82 123 74C113 89 101 99 86 106C101 105 115 102 128 98C111 116 84 127 57 129Z",
    ]
    result = "".join(plate(path) for path in paths[:count])
    if orbit:
        result += tube("M42 116C22 91 26 57 51 38C72 22 105 24 126 43")
        result += plate("M119 34L136 43L120 52Z")
    return result


def rotor(blades: int, core: bool = False) -> str:
    base = "M80 27C96 34 101 49 91 63C84 72 75 70 73 61C71 51 74 39 80 27Z"
    result = "".join(
        plate(base, f"rotate({360 * index / blades:.3f} 80 80)")
        for index in range(blades)
    )
    if core:
        result += orb(80, 80, 10)
    return result


def glint(cx: int, cy: int, scale: float = 1.0) -> str:
    return plate(
        "M80 65C81.5 75 85 78.5 95 80C85 81.5 81.5 85 80 95"
        "C78.5 85 75 81.5 65 80C75 78.5 78.5 75 80 65Z",
        f"translate({cx - 80} {cy - 80}) scale({scale:.3f}) translate({80 * (1 / scale - 1):.3f} {80 * (1 / scale - 1):.3f})")


def pulse(level: int) -> str:
    if level == 1:
        return glint(80, 80, 1.45)
    if level == 3:
        return glint(62, 70, 1.42) + glint(105, 91, .98)
    if level == 4:
        return (
            glint(80, 55, 1.30)
            + glint(55, 100, .92)
            + glint(108, 104, .76)
        )

    blades = 3
    base = (
        "M80 27C100 31 111 45 104 60C99 72 87 79 70 84"
        "C80 70 87 58 87 48C87 39 84 31 80 27Z"
    )
    result = "".join(
        plate(base, f"rotate({360 * index / blades:.3f} 80 80)")
        for index in range(blades)
    )
    return result + glint(80, 80, .42)


def interlocking_rings() -> str:
    # Both links are mathematically circular. Drawing the right link second
    # creates a clean physical overlap without welded-on connector fragments.
    return ring(60, 80, 31) + ring(100, 80, 31)


def chain_orbit() -> str:
    result = ring(80, 80, 45) + glint(80, 80, .88)
    for x, y in ((80, 35), (123, 66), (107, 116), (53, 116), (37, 66)):
        result += orb(x, y, 6)
    return result


def links(level: int) -> str:
    if level >= 4:
        return chain_orbit()
    result = interlocking_rings()
    if level >= 2:
        result += glint(80, 80, .26)
    if level >= 3:
        result += glint(124, 49, .20)
    return result


def speed_comet() -> str:
    # Author one set of Bézier controls and calculate both final paths from it.
    # Expanding the reflection into coordinates avoids renderer-specific SVG
    # transform behavior while keeping every lower point equal to y = 160 - y.
    segments: list[tuple[str, tuple[tuple[int, int], ...]]] = [
        ("M", ((22, 74),)),
        ("C", ((43, 52), (74, 39), (138, 40))),
        ("C", ((111, 52), (96, 64), (84, 76))),
        ("C", ((61, 70), (40, 70), (22, 74))),
    ]

    def wing_path(mirrored: bool) -> str:
        path = ""
        for command, points in segments:
            path += command
            path += " ".join(
                f"{x} {160 - y if mirrored else y}" for x, y in points)
        return path + "Z"

    upper_wing = wing_path(mirrored=False)
    lower_wing = wing_path(mirrored=True)
    sparkle = (
        "M80 64C82 74 86 78 96 80C86 82 82 86 80 96"
        "C78 86 74 82 64 80C74 78 78 74 80 64Z"
    )
    return (
        symmetric_plate(upper_wing)
        + symmetric_plate(lower_wing)
        + f'''<g>
      <path d="{sparkle}" fill="#0b1013"/>
      <path d="{sparkle}" fill="none" stroke="#f7f9fa" stroke-width=".72" opacity=".58"/>
    </g>'''
    )


def focus_eye() -> str:
    return (
        tube("M23 80C39 55 57 43 80 43C103 43 121 55 137 80C121 105 103 117 80 117C57 117 39 105 23 80Z")
        + orb(80, 80, 17)
    )


def focus_crescent(extra_glint: bool = False) -> str:
    crescent = (
        "M119 26C80 30 53 52 53 81C53 111 80 132 119 134"
        "C95 118 84 100 84 80C84 59 96 41 119 26Z"
    )
    result = plate(crescent) + glint(82, 80, 1.04)
    if extra_glint:
        result += glint(119, 44, .24)
    return result


def focus(level: int) -> str:
    if level == 1:
        return ring(80, 80, 39) + glint(80, 80, .72)
    if level == 2:
        return focus_eye()
    if level == 3:
        return focus_crescent()
    if level == 4:
        return focus_crescent(extra_glint=True)
    raise ValueError(f"unsupported focus level: {level}")


def rhythm(nodes: int) -> str:
    path = (
        "M80 34C89 34 90 47 98 50C106 53 114 44 121 51"
        "C128 58 119 66 122 74C125 82 138 83 138 92"
        "C138 101 125 102 122 110C119 118 128 126 121 133"
        "C114 140 106 131 98 134C90 137 89 150 80 150"
        "C71 150 70 137 62 134C54 131 46 140 39 133"
        "C32 126 41 118 38 110C35 102 22 101 22 92"
        "C22 83 35 82 38 74C41 66 32 58 39 51"
        "C46 44 54 53 62 50C70 47 71 34 80 34Z"
    )
    scale = {4: .78, 6: .88}.get(nodes, .96)
    return tube(path, f"translate({80 * (1 - scale):.2f} {92 * (1 - scale):.2f}) scale({scale:.2f})")


def constellation(nodes: int) -> str:
    positions = {
        2: [(49, 80), (111, 80)],
        3: [(80, 38), (42, 108), (118, 108)],
        5: [(80, 30), (128, 65), (110, 123), (50, 123), (32, 65)],
    }[nodes]
    if nodes == 2:
        result = tube("M61 80H99")
    elif nodes == 3:
        result = tube("M74 50L49 96M86 50L111 96M56 108H104")
    else:
        result = tube("M80 42L116 68L102 111H58L44 68Z")
    return result + "".join(orb(x, y, 9 if nodes < 5 else 7) for x, y in positions)


def mastery(level: int) -> str:
    blades = [5, 5, 6, 6][level - 1]
    base = (
        "M80 29C98 32 108 44 104 58C101 69 90 77 74 83"
        "C82 70 88 59 88 49C88 40 85 33 80 29Z"
    )
    result = "".join(
        plate(base, f"rotate({360 * index / blades:.3f} 80 80)")
        for index in range(blades)
    )
    if level >= 2:
        result += orb(80, 80, 7)
    if level >= 3:
        result += glint(80, 80, .25)
    if level >= 4:
        result += glint(113, 49, .20)
    return result


def aperture(blades: int) -> str:
    base = "M80 28C96 28 109 33 121 43L103 66C98 72 90 73 87 65Z"
    result = "".join(
        plate(base, f"rotate({360 * index / blades:.3f} 80 80)")
        for index in range(blades)
    )
    return result


def star() -> str:
    return plate("M80 23C84 56 88 72 125 80C88 88 84 104 80 137C76 104 72 88 35 80C72 72 76 56 80 23Z")


def endurance() -> str:
    return ring(80, 80, 48) + glint(80, 80, 1.04)


def clean() -> str:
    return tube("M37 84L64 108L120 47") + tube("M37 48C57 33 87 29 117 43")


def power_burst() -> str:
    return plate("M80 20L92 59L131 72L98 94L105 136L80 105L55 136L62 94L29 72L68 59Z")


def challenge_redline() -> str:
    return fins(3, True) + tube("M35 126H128")


def challenge_cycle() -> str:
    result = tube("M80 27C109 27 133 51 133 80C133 109 109 133 80 133C51 133 27 109 27 80C27 51 51 27 80 27Z")
    for rotation in (0, 90, 180, 270):
        result += plate("M80 18L86 31L99 37L86 43L80 56L74 43L61 37L74 31Z", f"rotate({rotation} 80 80)")
    return result


def founder() -> str:
    return plate("M80 22C101 22 118 30 129 42V82C129 109 109 128 80 140C51 128 31 109 31 82V42C42 30 59 22 80 22Z") + star()


BADGES = [
    BadgeArt("toy_power_ignition", "power", "ignition", "1.0", "POWER", fins(1)),
    BadgeArt("toy_power_overdrive", "power", "overdrive", "2.0", "POWER", fins(2)),
    BadgeArt("toy_power_apex", "power", "apex", "3.5", "REDLINE", fins(3, True)),
    BadgeArt("toy_power_singularity", "power", "singularity", "4.5", "REDLINE", fins(3, True)),
    BadgeArt("toy_pulse_100", "pulse", "ignition", "100", "PULSE", pulse(1)),
    BadgeArt("toy_pulse_1k", "pulse", "overdrive", "1K", "PULSE", pulse(2)),
    BadgeArt("toy_pulse_10k", "pulse", "apex", "10K", "PULSE", pulse(3)),
    BadgeArt("toy_pulse_100k", "pulse", "singularity", "100K", "PULSE", pulse(4)),
    BadgeArt("toy_technique_clean", "technique", "ignition", "CLEAN", "CONTROL", clean()),
    BadgeArt("toy_technique_power", "technique", "overdrive", "POWER", "CONTROL", power_burst()),
    BadgeArt("toy_technique_speed", "technique", "apex", "SPEED", "CONTROL", speed_comet()),
    BadgeArt("toy_technique_endurance", "technique", "apex", "ENDURE", "CONTROL", endurance()),
    BadgeArt("toy_technique_perfect", "technique", "singularity", "PERFECT", "CONTROL", star()),
    BadgeArt("toy_combo_5", "combo", "ignition", "×5", "CHAIN", links(1)),
    BadgeArt("toy_combo_10", "combo", "overdrive", "×10", "CHAIN", links(2)),
    BadgeArt("toy_combo_20", "combo", "apex", "×20", "CHAIN", links(3)),
    BadgeArt("toy_combo_50", "combo", "singularity", "×50", "CHAIN", links(4)),
    BadgeArt("toy_focus_5m", "focus", "ignition", "5M", "FOCUS", focus(1)),
    BadgeArt("toy_focus_30m", "focus", "overdrive", "30M", "FOCUS", focus(2)),
    BadgeArt("toy_focus_2h", "focus", "apex", "2H", "FOCUS", focus(3)),
    BadgeArt("toy_focus_10h", "focus", "singularity", "10H", "FOCUS", focus(4)),
    BadgeArt("collector_rhythm_1w", "rhythm", "ignition", "1W", "RHYTHM", rhythm(4)),
    BadgeArt("collector_rhythm_4w", "rhythm", "overdrive", "4W", "RHYTHM", rhythm(6)),
    BadgeArt("collector_rhythm_12w", "rhythm", "apex", "12W", "RHYTHM", rhythm(8)),
    BadgeArt("collector_explore_2", "explore", "ignition", "2", "EXPLORE", constellation(2)),
    BadgeArt("collector_explore_3", "explore", "overdrive", "3", "EXPLORE", constellation(3)),
    BadgeArt("collector_explore_5", "explore", "apex", "5", "EXPLORE", constellation(5)),
    BadgeArt("collector_mastery_1_lv20", "mastery", "ignition", "LV 20", "MASTERY", mastery(1)),
    BadgeArt("collector_mastery_3_lv20", "mastery", "overdrive", "3×20", "MASTERY", mastery(2)),
    BadgeArt("collector_mastery_1_lv100", "mastery", "apex", "LV 100", "MASTERY", mastery(3)),
    BadgeArt("collector_mastery_3_lv100", "mastery", "singularity", "3×100", "MASTERY", mastery(4)),
    BadgeArt("collector_collection_5", "collection", "ignition", "5", "VAULT", aperture(5)),
    BadgeArt("collector_collection_10", "collection", "overdrive", "10", "VAULT", aperture(6)),
    BadgeArt("collector_collection_25", "collection", "singularity", "25", "VAULT", aperture(7)),
    BadgeArt("challenge_redline", "challenge", "apex", "3×", "REDLINE", challenge_redline()),
    BadgeArt("challenge_chain_reactor", "challenge", "apex", "2×20", "CHAIN", links(4)),
    BadgeArt("challenge_perfect_protocol", "challenge", "singularity", "3×", "PERFECT", star() + tube("M33 80C33 51 51 33 80 33C109 33 127 51 127 80")),
    BadgeArt("challenge_three_core_raid", "challenge", "singularity", "3 CORE", "RAID", constellation(3) + orb(80, 80, 7)),
    BadgeArt("challenge_cycle_total", "challenge", "singularity", "4/4", "CYCLE", challenge_cycle()),
    BadgeArt("legacy_founder", "legacy", "singularity", "LEGACY", "FOUNDER", founder()),
]


def definitions() -> str:
    return '''
  <defs>
    <linearGradient id="chrome" gradientUnits="userSpaceOnUse" x1="31" y1="25" x2="130" y2="137">
      <stop offset="0" stop-color="#11161a"/><stop offset=".08" stop-color="#566067"/>
      <stop offset=".16" stop-color="#f8fbfc"/><stop offset=".24" stop-color="#879197"/>
      <stop offset=".36" stop-color="#ffffff"/><stop offset=".47" stop-color="#30373c"/>
      <stop offset=".58" stop-color="#cbd2d5"/><stop offset=".69" stop-color="#ffffff"/>
      <stop offset=".79" stop-color="#596269"/><stop offset=".90" stop-color="#e8edef"/>
      <stop offset="1" stop-color="#171c20"/>
    </linearGradient>
    <linearGradient id="chromeSymmetric" gradientUnits="userSpaceOnUse" x1="22" y1="80" x2="138" y2="80">
      <stop offset="0" stop-color="#252c31"/><stop offset=".12" stop-color="#aeb6bb"/>
      <stop offset=".24" stop-color="#ffffff"/><stop offset=".39" stop-color="#737c82"/>
      <stop offset=".52" stop-color="#f7f9fa"/><stop offset=".66" stop-color="#90989d"/>
      <stop offset=".80" stop-color="#e9edef"/><stop offset=".92" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#626a6f"/>
    </linearGradient>
    <radialGradient id="orb" cx="34%" cy="27%" r="74%">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".19" stop-color="#e7ecee"/>
      <stop offset=".42" stop-color="#8d979c"/><stop offset=".68" stop-color="#30383e"/>
      <stop offset="1" stop-color="#0d1114"/>
    </radialGradient>
    <filter id="softGlow" x="-35%" y="-35%" width="170%" height="170%">
      <feGaussianBlur stdDeviation="2.8"/>
    </filter>
  </defs>
  <style>
    .tubeBloom { fill:none; stroke:#edf6fa; stroke-width:21; stroke-linecap:round; stroke-linejoin:round; opacity:.18; filter:url(#softGlow); }
    .tubeDark { fill:none; stroke:#0b1014; stroke-width:18; stroke-linecap:round; stroke-linejoin:round; }
    .tubeBody { fill:none; stroke:url(#chrome); stroke-width:13.8; stroke-linecap:round; stroke-linejoin:round; }
    .tubeShade { fill:none; stroke:#0a0e11; stroke-width:3.2; stroke-linecap:round; stroke-linejoin:round; opacity:.58; transform:translate(1.25px,1.35px); }
    .tubeLight { fill:none; stroke:#ffffff; stroke-width:2.0; stroke-linecap:round; stroke-linejoin:round; opacity:.82; transform:translate(-1.0px,-1.05px); }
    .plateBloom { fill:#edf5f8; stroke:none; opacity:.16; filter:url(#softGlow); }
    .plateShadow { fill:#080c0f; stroke:#080c0f; stroke-width:1.6; transform:translate(2.5px,2.8px); }
    .plateDepth { fill:#161d22; stroke:#080c0f; stroke-width:2.4; stroke-linejoin:round; transform:translate(1.2px,1.4px); }
    .plateBody { fill:url(#chrome); stroke:#929ba0; stroke-width:.9; stroke-linejoin:round; }
    .plateEdge { fill:none; stroke:#ffffff; stroke-width:1.05; stroke-linejoin:round; opacity:.78; transform:translate(-.55px,-.62px); }
    .orbBloom { fill:#eef8fb; opacity:.40; filter:url(#softGlow); }
    .orbBody { fill:url(#orb); stroke:#f2f5f6; stroke-width:2.2; }
    .orbGlint { fill:#ffffff; opacity:.96; }
  </style>'''


def individual_svg(badge: BadgeArt) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 160 160">
{definitions()}
  <g>{badge.markup}</g>
</svg>
'''


def shape_for_grade(grade: str, x: float, y: float, width: float, height: float) -> str:
    del grade
    vertices = [
        (x + width * .50, y + height * .04),
        (x + width * .92, y + height * .27),
        (x + width * .92, y + height * .73),
        (x + width * .50, y + height * .96),
        (x + width * .08, y + height * .73),
        (x + width * .08, y + height * .27),
    ]
    corner_fraction = .16

    def toward(point: tuple[float, float], neighbor: tuple[float, float]) -> tuple[float, float]:
        return (
            point[0] + (neighbor[0] - point[0]) * corner_fraction,
            point[1] + (neighbor[1] - point[1]) * corner_fraction,
        )

    first = toward(vertices[0], vertices[-1])
    commands = [f"M{first[0]:.2f} {first[1]:.2f}"]
    for index, current in enumerate(vertices):
        previous = vertices[(index - 1) % len(vertices)]
        next_point = vertices[(index + 1) % len(vertices)]
        before = toward(current, previous)
        after = toward(current, next_point)
        if index > 0:
            commands.append(f"L{before[0]:.2f} {before[1]:.2f}")
        commands.append(
            f"Q{current[0]:.2f} {current[1]:.2f} {after[0]:.2f} {after[1]:.2f}")
    commands.append("Z")
    return f'<path d="{"".join(commands)}"/>'


def embedded_png_href(badge: BadgeArt) -> str:
    path = OUTPUT / f"{badge.asset_name}.png"
    if not path.exists():
        return f"../../../Assets/Plugins/iOS/BadgeArtwork/{badge.asset_name}.png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def sheet_svg(title: str, badges: list[BadgeArt], columns: int) -> str:
    width = height = 1254
    margin = 24
    gap = 10
    top = 72
    bottom = 24
    rows = (len(badges) + columns - 1) // columns
    cell_width = (width - margin * 2 - gap * (columns - 1)) / columns
    cell_height = (height - top - bottom - gap * (rows - 1)) / rows
    items: list[str] = []
    for index, badge in enumerate(badges):
        row, column = divmod(index, columns)
        cell_x = margin + column * (cell_width + gap)
        cell_y = top + row * (cell_height + gap)
        badge_width = min(cell_width - 18, 136)
        badge_height = min(cell_height - 12, badge_width)
        x = cell_x + (cell_width - badge_width) / 2
        y = cell_y + (cell_height - badge_height) / 2
        shape = shape_for_grade(badge.grade, x, y, badge_width, badge_height)
        rim_inset = badge_width * .054
        inner_shape = shape_for_grade(
            badge.grade,
            x + rim_inset,
            y + rim_inset,
            badge_width - rim_inset * 2,
            badge_height - rim_inset * 2)
        art_size = badge_width * .46
        art_x = x + (badge_width - art_size) / 2
        art_y = y + badge_height * .08
        token_y = y + badge_height * .72
        label_y = y + badge_height * .84
        items.append(f'''<g>
  <defs><clipPath id="clip-{index}">{shape}</clipPath></defs>
  <g class="badgeShadow"><g class="shell">{shape}</g></g>
  <g class="innerRim">{inner_shape}</g>
  <g clip-path="url(#clip-{index})">
    <image href="{embedded_png_href(badge)}" x="{art_x:.2f}" y="{art_y:.2f}" width="{art_size:.2f}" height="{art_size:.2f}"/>
    <text x="{x + badge_width/2:.2f}" y="{token_y:.2f}" class="token">{escape(badge.token)}</text>
    <text x="{x + badge_width/2:.2f}" y="{label_y:.2f}" class="label">{escape(badge.short_name)}</text>
  </g>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254" viewBox="0 0 1254 1254">
  <defs>
    <style>
      @font-face {{ font-family: Oxanium; src: url('../../Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf'); }}
      .heading,.token,.label {{ font-family:Oxanium,-apple-system,sans-serif;text-anchor:middle;fill:#f3f5f6; }}
      .heading {{ font-size:18px;font-weight:700; }} .token {{ font-size:18px;font-weight:720; }}
      .label {{ font-size:7px;font-weight:680;letter-spacing:.8px;fill:#c5cbd0; }}
      .shell {{ fill:url(#leather);stroke:url(#rim);stroke-width:3.5; }}
      .innerRim {{ fill:none;stroke:#71787b;stroke-width:.75;opacity:.62; }}
      .badgeShadow {{ filter:url(#shadow); }}
    </style>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#07090b"/><stop offset="1" stop-color="#11151a"/></linearGradient>
    <pattern id="leather" width="37" height="31" patternUnits="userSpaceOnUse"><rect width="37" height="31" fill="#0b1012"/><path d="M3 7C7 3 12 5 16 10M23 3C27 7 31 8 35 5M7 21C12 18 16 19 20 24M27 18C31 15 35 17 39 20" fill="none" stroke="#454c4f" stroke-width=".48" opacity=".22"/><path d="M3.5 7.8C7.5 3.8 12.5 5.8 16.5 10.8M7.5 21.8C12.5 18.8 16.5 19.8 20.5 24.8" fill="none" stroke="#000" stroke-width=".8" opacity=".34"/><circle cx="5" cy="15" r=".55" fill="#60676a" opacity=".22"/><circle cx="20" cy="13" r=".48" fill="#000" opacity=".68"/><circle cx="31" cy="27" r=".5" fill="#555c5f" opacity=".18"/></pattern>
    <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f0f4f5"/><stop offset=".32" stop-color="#abb1b3"/><stop offset=".68" stop-color="#5b6265"/><stop offset="1" stop-color="#303638"/></linearGradient>
    <filter id="shadow" x="-30%" y="-25%" width="160%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="7" flood-color="#000" flood-opacity=".72"/></filter>
  </defs>
  <rect width="1254" height="1254" fill="url(#bg)"/>
  <text x="627" y="38" class="heading">{escape(title)}</text>
  {''.join(items)}
</svg>
'''


def main() -> None:
    if len(BADGES) != 40 or len({badge.asset_id for badge in BADGES}) != 40:
        raise RuntimeError("The B8 catalog must contain exactly 40 unique badge assets")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for badge in BADGES:
        (OUTPUT / f"{badge.asset_name}.svg").write_text(
            individual_svg(badge), encoding="utf-8")

    manifest = {
        "version": 2,
        "visualLanguage": "b8.10-vertical-point-hex-safe-area",
        "canvas": {"width": 1024, "height": 1024, "colorSpace": "sRGB", "transparent": True},
        "frameShapes": ["verticalPointRoundedHexagon"],
        "iconLayout": {
            "slot": "square",
            "fit": "longest-side-aspect-fit",
            "visibleFraction": 0.74,
            "alphaThreshold": 16,
            "preserveAspectRatio": True,
            "circlePrimitive": "equal-diameter",
        },
        "runtimeTypography": {"maximumLines": 2, "lines": ["displayToken", "shortName"]},
        "assets": [
            {
                "id": badge.asset_id,
                "assetName": badge.asset_name,
                "category": badge.category,
                "grade": badge.grade,
                "displayToken": badge.token,
                "shortName": badge.short_name,
                "svg": f"{badge.asset_name}.svg",
                "png": f"{badge.asset_name}.png",
            }
            for badge in BADGES
        ],
    }
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    (OUTPUT / "badge-b8-manifest.json").write_text(manifest_text, encoding="utf-8")
    (ARTIFACTS / "badge-b8-manifest.json").write_text(manifest_text, encoding="utf-8")

    toy = [badge for badge in BADGES if badge.asset_id.startswith("toy_")]
    collector = [badge for badge in BADGES if badge.asset_id.startswith("collector_")]
    special = [badge for badge in BADGES if badge.asset_id.startswith(("challenge_", "legacy_"))]
    (ARTIFACTS / "badge-b8-catalog-toy.svg").write_text(
        sheet_svg("21 TOY BADGES", toy, 7), encoding="utf-8")
    (ARTIFACTS / "badge-b8-catalog-collector.svg").write_text(
        sheet_svg("13 COLLECTOR BADGES", collector, 5), encoding="utf-8")
    (ARTIFACTS / "badge-b8-catalog-challenge.svg").write_text(
        sheet_svg("CHALLENGE + LEGACY", special, 3), encoding="utf-8")
    print(f"generated_b8_badges={len(BADGES)} output={OUTPUT}")


if __name__ == "__main__":
    main()
