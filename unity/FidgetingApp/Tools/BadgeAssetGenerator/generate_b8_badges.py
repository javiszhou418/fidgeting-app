#!/usr/bin/env python3
"""Generate the recessed satin-metal production glyph catalog.

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
      <path class="tubeShadow" d="{path}"/>
      <path class="tubeDepth" d="{path}"/>
      <path class="tubeBevel" d="{path}"/>
      <path class="tubeBody" d="{path}"/>
      <path class="tubeSheen" d="{path}"/>
      <path class="tubeLight" d="{path}"/>
    </g>'''


def plate(path: str, transform: str = "") -> str:
    transform_attr = f' transform="{transform}"' if transform else ""
    return f'''<g{transform_attr}>
      <path class="plateBloom" d="{path}"/>
      <path class="plateShadow" d="{path}"/>
      <path class="plateDepth" d="{path}"/>
      <path class="plateBevel" d="{path}"/>
      <path class="plateBody" d="{path}"/>
      <path class="plateSheen" d="{path}"/>
      <path class="plateEdge" d="{path}"/>
    </g>'''


def symmetric_plate(path: str) -> str:
    """A satin plate whose lighting is invariant across the y=80 mirror."""
    return f'''<g>
      <path class="plateBloom" d="{path}"/>
      <path class="plateShadow" d="{path}"/>
      <path class="plateDepth" d="{path}"/>
      <path d="{path}" fill="url(#iconBevelSymmetric)" fill-rule="evenodd" stroke="#615d6d" stroke-width="9.0" stroke-linejoin="round"/>
      <path d="{path}" fill="url(#iconFaceSymmetric)" fill-rule="evenodd" stroke="#d9d8e0" stroke-width="1.35" stroke-linejoin="round" transform="translate(-.8px,-1.0px)"/>
      <path d="{path}" fill="url(#iconSheenSymmetric)" fill-rule="evenodd" stroke="none" opacity=".58" transform="translate(-.8px,-1.0px)"/>
      <path d="{path}" fill="none" stroke="#ffffff" stroke-width="1.15" stroke-linejoin="round" opacity=".78" transform="translate(-1.25px,-1.45px)"/>
    </g>'''


def orb(cx: int, cy: int, radius: int) -> str:
    return f'''<g>
      <circle class="orbBloom" cx="{cx}" cy="{cy}" r="{radius + 4}"/>
      <circle class="orbShadow" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="orbDepth" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="orbBevel" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="orbBody" cx="{cx}" cy="{cy}" r="{max(1, radius - 2)}"/>
      <circle class="orbGlint" cx="{cx - radius * .28:.1f}" cy="{cy - radius * .32:.1f}" r="{max(2, radius * .22):.1f}"/>
    </g>'''


def ring(cx: int, cy: int, radius: int) -> str:
    """A true circular chrome tube; never substitute an ellipse."""
    return f'''<g>
      <circle class="tubeBloom" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeShadow" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeDepth" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeBevel" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeBody" cx="{cx}" cy="{cy}" r="{radius}"/>
      <circle class="tubeSheen" cx="{cx}" cy="{cy}" r="{radius}"/>
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


def speed_slash() -> str:
    """Reference-matched redline: two rotational arcs and one rounded slash."""
    first_arc = tube("M53 109C35 92 35 63 53 47C57 43 61 40 66 38")
    second_arc = tube(
        "M53 109C35 92 35 63 53 47C57 43 61 40 66 38",
        "rotate(180 80 80)")
    slash = tube("M57 117L103 43")
    return first_arc + second_arc + slash


def rotor_mark(blades: int) -> str:
    """One coherent three-blade rotor; milestone values remain outside."""
    del blades
    blade = (
        "M80 31C95 33 106 43 106 55C106 67 96 76 78 83"
        "C83 70 85 59 84 48C84 41 82 35 80 31Z"
    )
    return "".join(
        plate(blade, f"rotate({120 * index:.3f} 80 80)")
        for index in range(3)
    ) + orb(80, 80, 9)


def chain_links() -> str:
    """Two identical closed obround links on one 45-degree construction axis."""
    link = (
        "M64 72C71 72 76 77 76 84V108C76 115 71 120 64 120"
        "C57 120 52 115 52 108V84C52 77 57 72 64 72Z"
    )
    return (
        tube(link, "rotate(45 64 96)")
        + tube(link, "translate(32 -32) rotate(45 64 96)")
    )


def hourglass_mark() -> str:
    """A single cast hourglass frame; the openings reveal the leather."""
    return plate(
        "M52 31C52 27 55 24 59 24H101C105 24 108 27 108 31"
        "C106 51 98 67 88 80C98 93 106 109 108 129"
        "C108 133 105 136 101 136H59C55 136 52 133 52 129"
        "C54 109 62 93 72 80C62 67 54 51 52 31Z"
        "M64 39H96C93 53 88 65 80 75C72 65 67 53 64 39Z"
        "M80 85C88 95 93 107 96 121H64C67 107 72 95 80 85Z"
    )


def triangle_core() -> str:
    """One symmetric rounded triangular casting, matching the master sheet."""
    return plate(
        "M80 29C87 29 91 34 95 42L125 106C131 118 123 130 110 130"
        "H50C37 130 29 118 35 106L65 42C69 34 73 29 80 29Z")


def cycle_arrows() -> str:
    arc = tube("M42 79C42 56 59 40 82 40C99 40 112 48 120 61")
    arrow = plate("M111 49C111 47 113 46 115 47L135 62C138 64 137 68 134 69L110 75C108 76 106 74 107 72Z")
    return arc + arrow + f'<g transform="rotate(180 80 80)">{arc}{arrow}</g>'


def shield_mark() -> str:
    return (
        plate("M80 28C98 28 113 33 124 42V79C124 104 107 123 80 135C53 123 36 104 36 79V42C47 33 62 28 80 28Z")
        + tube("M80 43V117")
    )


def vault_wheel(spokes: int) -> str:
    result = ring(80, 80, 45)
    for index in range(spokes):
        result += tube("M80 80V43", f"rotate({360 * index / spokes:.3f} 80 80)")
    return result + orb(80, 80, 12)


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
    del nodes
    # Every tier uses the same true circular orbit. Three equal inlaid pearls
    # sit exactly 120 degrees apart, so no milestone looks stretched or loose.
    return (
        ring(80, 80, 41)
        + orb(80, 39, 7)
        + orb(115, 101, 7)
        + orb(45, 101, 7)
        + glint(80, 80, .45)
    )


def mastery(level: int) -> str:
    del level
    # A compact centered medallion replaces the previous loose blade piles.
    return ring(80, 80, 42) + star()


def aperture(blades: int) -> str:
    base = "M80 28C96 28 109 33 121 43L103 66C98 72 90 73 87 65Z"
    result = "".join(
        plate(base, f"rotate({360 * index / blades:.3f} 80 80)")
        for index in range(blades)
    )
    return result


def star() -> str:
    return plate(
        "M80 25C84 48 88 65 98 72C106 77 119 78 135 80"
        "C119 82 106 83 98 88C88 95 84 112 80 135"
        "C76 112 72 95 62 88C54 83 41 82 25 80"
        "C41 78 54 77 62 72C72 65 76 48 80 25Z")


def endurance() -> str:
    return ring(80, 80, 48) + glint(80, 80, 1.04)


def clean() -> str:
    return tube("M38 82L64 107L121 48")


def power_burst() -> str:
    return plate(
        "M88 24C91 24 93 27 92 31L84 62H112C117 62 119 68 116 72"
        "L72 135C70 138 65 135 66 131L75 94H48C43 94 41 88 44 84L88 24Z")


def challenge_redline() -> str:
    return speed_slash()


def challenge_cycle() -> str:
    return cycle_arrows()


def founder() -> str:
    return shield_mark()


BADGES = [
    BadgeArt("toy_power_ignition", "power", "ignition", "1.0", "POWER", speed_slash()),
    BadgeArt("toy_power_overdrive", "power", "overdrive", "2.0", "POWER", speed_slash()),
    BadgeArt("toy_power_apex", "power", "apex", "3.5", "REDLINE", speed_slash()),
    BadgeArt("toy_power_singularity", "power", "singularity", "4.5", "REDLINE", speed_slash()),
    BadgeArt("toy_pulse_100", "pulse", "ignition", "100", "PULSE", rotor_mark(3)),
    BadgeArt("toy_pulse_1k", "pulse", "overdrive", "1K", "PULSE", rotor_mark(3)),
    BadgeArt("toy_pulse_10k", "pulse", "apex", "10K", "PULSE", rotor_mark(3)),
    BadgeArt("toy_pulse_100k", "pulse", "singularity", "100K", "PULSE", rotor_mark(3)),
    BadgeArt("toy_technique_clean", "technique", "ignition", "CLEAN", "CONTROL", clean()),
    BadgeArt("toy_technique_power", "technique", "overdrive", "POWER", "CONTROL", power_burst()),
    BadgeArt("toy_technique_speed", "technique", "apex", "SPEED", "CONTROL", speed_slash()),
    BadgeArt("toy_technique_endurance", "technique", "apex", "ENDURE", "CONTROL", hourglass_mark()),
    BadgeArt("toy_technique_perfect", "technique", "singularity", "PERFECT", "CONTROL", star()),
    BadgeArt("toy_combo_5", "combo", "ignition", "×5", "CHAIN", chain_links()),
    BadgeArt("toy_combo_10", "combo", "overdrive", "×10", "CHAIN", chain_links()),
    BadgeArt("toy_combo_20", "combo", "apex", "×20", "CHAIN", chain_links()),
    BadgeArt("toy_combo_50", "combo", "singularity", "×50", "CHAIN", chain_links()),
    BadgeArt("toy_focus_5m", "focus", "ignition", "5M", "FOCUS", hourglass_mark()),
    BadgeArt("toy_focus_30m", "focus", "overdrive", "30M", "FOCUS", hourglass_mark()),
    BadgeArt("toy_focus_2h", "focus", "apex", "2H", "FOCUS", hourglass_mark()),
    BadgeArt("toy_focus_10h", "focus", "singularity", "10H", "FOCUS", hourglass_mark()),
    BadgeArt("collector_rhythm_1w", "rhythm", "ignition", "1W", "RHYTHM", rhythm(6)),
    BadgeArt("collector_rhythm_4w", "rhythm", "overdrive", "4W", "RHYTHM", rhythm(6)),
    BadgeArt("collector_rhythm_12w", "rhythm", "apex", "12W", "RHYTHM", rhythm(6)),
    BadgeArt("collector_explore_2", "explore", "ignition", "2", "EXPLORE", constellation(2)),
    BadgeArt("collector_explore_3", "explore", "overdrive", "3", "EXPLORE", constellation(3)),
    BadgeArt("collector_explore_5", "explore", "apex", "5", "EXPLORE", constellation(5)),
    BadgeArt("collector_mastery_1_lv20", "mastery", "ignition", "LV 20", "MASTERY", mastery(1)),
    BadgeArt("collector_mastery_3_lv20", "mastery", "overdrive", "3×20", "MASTERY", mastery(2)),
    BadgeArt("collector_mastery_1_lv100", "mastery", "apex", "LV 100", "MASTERY", mastery(3)),
    BadgeArt("collector_mastery_3_lv100", "mastery", "singularity", "3×100", "MASTERY", mastery(4)),
    BadgeArt("collector_collection_5", "collection", "ignition", "5", "VAULT", vault_wheel(5)),
    BadgeArt("collector_collection_10", "collection", "overdrive", "10", "VAULT", vault_wheel(5)),
    BadgeArt("collector_collection_25", "collection", "singularity", "25", "VAULT", vault_wheel(5)),
    BadgeArt("challenge_redline", "challenge", "apex", "3×", "REDLINE", challenge_redline()),
    BadgeArt("challenge_chain_reactor", "challenge", "apex", "2×20", "CHAIN", chain_links()),
    BadgeArt("challenge_perfect_protocol", "challenge", "singularity", "3×", "PERFECT", star()),
    BadgeArt("challenge_three_core_raid", "challenge", "singularity", "3 CORE", "RAID", triangle_core()),
    BadgeArt("challenge_cycle_total", "challenge", "singularity", "4/4", "CYCLE", challenge_cycle()),
    BadgeArt("legacy_founder", "legacy", "singularity", "LEGACY", "FOUNDER", founder()),
]


def definitions() -> str:
    return '''
  <defs>
    <linearGradient id="iconFace" gradientUnits="userSpaceOnUse" x1="34" y1="25" x2="126" y2="138">
      <stop offset="0" stop-color="#f8f6fb"/><stop offset=".32" stop-color="#e8e5ed"/>
      <stop offset=".62" stop-color="#cbc7d3"/><stop offset=".82" stop-color="#ddd7e7"/>
      <stop offset="1" stop-color="#aaa4b5"/>
    </linearGradient>
    <linearGradient id="iconBevel" gradientUnits="userSpaceOnUse" x1="29" y1="28" x2="133" y2="135">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".34" stop-color="#d9d6df"/>
      <stop offset=".70" stop-color="#a6a1b0"/><stop offset="1" stop-color="#777181"/>
    </linearGradient>
    <linearGradient id="iconSheen" gradientUnits="userSpaceOnUse" x1="48" y1="33" x2="116" y2="128">
      <stop offset="0" stop-color="#ffffff" stop-opacity=".72"/>
      <stop offset=".44" stop-color="#ffffff" stop-opacity=".08"/>
      <stop offset="1" stop-color="#cbb9e5" stop-opacity=".30"/>
    </linearGradient>
    <linearGradient id="iconFaceSymmetric" gradientUnits="userSpaceOnUse" x1="22" y1="80" x2="138" y2="80">
      <stop offset="0" stop-color="#b9b5c2"/><stop offset=".28" stop-color="#f3f1f7"/>
      <stop offset=".60" stop-color="#ddd9e3"/><stop offset="1" stop-color="#aaa5b5"/>
    </linearGradient>
    <linearGradient id="iconBevelSymmetric" gradientUnits="userSpaceOnUse" x1="22" y1="80" x2="138" y2="80">
      <stop offset="0" stop-color="#797482"/><stop offset=".30" stop-color="#e1dee6"/>
      <stop offset=".70" stop-color="#beb9c6"/><stop offset="1" stop-color="#77717f"/>
    </linearGradient>
    <linearGradient id="iconSheenSymmetric" gradientUnits="userSpaceOnUse" x1="22" y1="80" x2="138" y2="80">
      <stop offset="0" stop-color="#cab8eb" stop-opacity=".20"/>
      <stop offset=".40" stop-color="#ffffff" stop-opacity=".10"/>
      <stop offset=".62" stop-color="#ffffff" stop-opacity=".62"/>
      <stop offset="1" stop-color="#9a84c7" stop-opacity=".24"/>
    </linearGradient>
    <radialGradient id="orbFace" cx="31%" cy="24%" r="78%">
      <stop offset="0" stop-color="#ffffff"/><stop offset=".28" stop-color="#f2f1f6"/>
      <stop offset=".58" stop-color="#c4c2cd"/><stop offset=".82" stop-color="#8a8797"/>
      <stop offset="1" stop-color="#666373"/>
    </radialGradient>
    <filter id="softGlow" x="-38%" y="-38%" width="176%" height="176%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>
    <filter id="iconShadow" x="-35%" y="-35%" width="180%" height="190%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>
  </defs>
  <style>
    .tubeBloom { fill:none; stroke:#e6def2; stroke-width:22; stroke-linecap:round; stroke-linejoin:round; opacity:.07; filter:url(#softGlow); }
    .tubeShadow { fill:none; stroke:#0b0910; stroke-width:21; stroke-linecap:round; stroke-linejoin:round; opacity:.54; transform:translate(3.2px,3.8px); filter:url(#iconShadow); }
    .tubeDepth { fill:none; stroke:#5b5564; stroke-width:19.5; stroke-linecap:round; stroke-linejoin:round; transform:translate(2.5px,3.0px); }
    .tubeBevel { fill:none; stroke:url(#iconBevel); stroke-width:18; stroke-linecap:round; stroke-linejoin:round; }
    .tubeBody { fill:none; stroke:url(#iconFace); stroke-width:12.8; stroke-linecap:round; stroke-linejoin:round; transform:translate(-.35px,-.48px); }
    .tubeSheen { fill:none; stroke:url(#iconSheen); stroke-width:9.2; stroke-linecap:round; stroke-linejoin:round; opacity:.48; transform:translate(-.5px,-.65px); }
    .tubeLight { fill:none; stroke:#ffffff; stroke-width:1.2; stroke-linecap:round; stroke-linejoin:round; opacity:.34; transform:translate(-.8px,-1px); }
    .plateBloom { fill:#e9e0f7; fill-rule:evenodd; stroke:none; opacity:.07; filter:url(#softGlow); }
    .plateShadow { fill:#0b0910; fill-rule:evenodd; stroke:#0b0910; stroke-width:2.4; transform:translate(3.2px,3.8px); opacity:.54; filter:url(#iconShadow); }
    .plateDepth { fill:#5b5564; fill-rule:evenodd; stroke:#45404e; stroke-width:3.2; stroke-linejoin:round; transform:translate(2.5px,3.0px); }
    .plateBevel { fill:url(#iconBevel); fill-rule:evenodd; stroke:#7f7987; stroke-width:7.2; stroke-linejoin:round; }
    .plateBody { fill:url(#iconFace); fill-rule:evenodd; stroke:#dedbe4; stroke-width:1.0; stroke-linejoin:round; transform:translate(-.45px,-.58px); }
    .plateSheen { fill:url(#iconSheen); fill-rule:evenodd; stroke:none; opacity:.46; transform:translate(-.45px,-.58px); }
    .plateEdge { fill:none; stroke:#ffffff; stroke-width:.82; stroke-linejoin:round; opacity:.30; transform:translate(-.75px,-.92px); }
    .orbBloom { fill:#e6def4; opacity:.10; filter:url(#softGlow); }
    .orbShadow { fill:#0b0910; transform:translate(3.2px,3.8px); opacity:.54; filter:url(#iconShadow); }
    .orbDepth { fill:#5b5564; stroke:#45404e; stroke-width:2.8; transform:translate(2.5px,3.0px); }
    .orbBevel { fill:url(#iconBevel); stroke:#d6d2dc; stroke-width:2.0; }
    .orbBody { fill:url(#orbFace); stroke:#f2eff5; stroke-width:.8; transform:translate(-.4px,-.5px); }
    .orbGlint { fill:#ffffff; opacity:.58; }
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
        (x + width * .90, y + height * .27),
        (x + width * .90, y + height * .73),
        (x + width * .50, y + height * .96),
        (x + width * .10, y + height * .73),
        (x + width * .10, y + height * .27),
    ]
    corner_fraction = .25

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
        well_inset = badge_width * .115
        panel_inset = badge_width * .135
        well_shape = shape_for_grade(
            badge.grade,
            x + well_inset,
            y + well_inset,
            badge_width - well_inset * 2,
            badge_height - well_inset * 2)
        panel_shape = shape_for_grade(
            badge.grade,
            x + panel_inset,
            y + panel_inset,
            badge_width - panel_inset * 2,
            badge_height - panel_inset * 2)
        art_size = badge_width * .48
        art_x = x + (badge_width - art_size) / 2
        art_y = y + (badge_height - art_size) / 2
        label_y = y + badge_height + 12
        items.append(f'''<g>
  <defs><clipPath id="clip-{index}">{panel_shape}</clipPath></defs>
  <g class="badgeShadow">
    <g class="shellDepth" transform="translate(0 {badge_width * .025:.2f})">{shape}</g>
    <g class="shell">{shape}</g>
    <g class="well">{well_shape}</g>
    <g class="panel">{panel_shape}</g>
  </g>
  <g clip-path="url(#clip-{index})">
    <image href="{embedded_png_href(badge)}" x="{art_x:.2f}" y="{art_y:.2f}" width="{art_size:.2f}" height="{art_size:.2f}"/>
  </g>
  <text x="{x + badge_width/2:.2f}" y="{label_y:.2f}" class="label">{escape(badge.short_name)} {escape(badge.token)}</text>
</g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1254" height="1254" viewBox="0 0 1254 1254">
  <defs>
    <style>
      @font-face {{ font-family: Oxanium; src: url('../../Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf'); }}
      .heading,.label {{ font-family:Oxanium,-apple-system,sans-serif;text-anchor:middle;fill:#f3f5f6; }}
      .heading {{ font-size:18px;font-weight:700; }}
      .label {{ font-size:7px;font-weight:620;letter-spacing:.5px;fill:#8d8b96; }}
      .shellDepth {{ fill:#34313e;stroke:#1c1a24;stroke-width:1.5; }}
      .shell {{ fill:url(#rim);stroke:#f4f3f8;stroke-width:1.1; }}
      .well {{ fill:url(#well);stroke:#8f8d99;stroke-width:1.7; }}
      .panel {{ fill:url(#panel);stroke:#111019;stroke-width:1.1; }}
      .badgeShadow {{ filter:url(#shadow); }}
    </style>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#07090b"/><stop offset="1" stop-color="#11151a"/></linearGradient>
    <pattern id="leather" width="37" height="31" patternUnits="userSpaceOnUse"><rect width="37" height="31" fill="#0b1012"/><path d="M3 7C7 3 12 5 16 10M23 3C27 7 31 8 35 5M7 21C12 18 16 19 20 24M27 18C31 15 35 17 39 20" fill="none" stroke="#454c4f" stroke-width=".48" opacity=".22"/><path d="M3.5 7.8C7.5 3.8 12.5 5.8 16.5 10.8M7.5 21.8C12.5 18.8 16.5 19.8 20.5 24.8" fill="none" stroke="#000" stroke-width=".8" opacity=".34"/><circle cx="5" cy="15" r=".55" fill="#60676a" opacity=".22"/><circle cx="20" cy="13" r=".48" fill="#000" opacity=".68"/><circle cx="31" cy="27" r=".5" fill="#555c5f" opacity=".18"/></pattern>
    <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e8f4f1"/><stop offset=".23" stop-color="#ffffff"/><stop offset=".48" stop-color="#aaa8b5"/><stop offset=".72" stop-color="#d8d0e7"/><stop offset="1" stop-color="#6b6877"/></linearGradient>
    <linearGradient id="well" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#777481"/><stop offset=".34" stop-color="#24222e"/><stop offset="1" stop-color="#08070d"/></linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#242231"/><stop offset=".48" stop-color="#100f18"/><stop offset="1" stop-color="#08070d"/></linearGradient>
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
        "visualLanguage": "b9.2-reference-proportioned-satin-relief",
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
        "iconMaterial": {
            "face": "satin-pearl-silver",
            "depth": "soft-dark-lavender-sidewall",
            "bevel": "continuous-rounded-manufactured-edge",
            "lighting": "top-left-softbox",
        },
        "runtimeTypography": {
            "maximumLines": 2,
            "placement": "outside-badge",
            "line": ["shortName", "displayToken"],
        },
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
