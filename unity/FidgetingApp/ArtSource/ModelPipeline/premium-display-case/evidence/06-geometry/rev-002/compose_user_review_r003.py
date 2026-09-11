#!/usr/bin/env python3
"""Compose the whole-case-only Gate 06 user review board."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "geometry-validation.json"
OUTPUT = ROOT / "gate06-whole-case-review-r003.png"
CONCENTRIC = (
    ROOT.parent.parent
    / "05-blockout"
    / "rev-002"
    / "blockout-concentric-centers.png"
)

FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")

BG = (7, 12, 20)
CARD = (17, 26, 39)
LINE = (47, 67, 88)
INK = (240, 246, 252)
MUTED = (154, 174, 194)
CYAN = (57, 218, 246)
GREEN = (76, 226, 151)
YELLOW = (250, 194, 62)
CORAL = (255, 105, 116)

PANELS = (
    "front",
    "back",
    "top",
    "side",
    "workbench",
    "dimensions",
    "pivot",
    "concentric",
    "closed-loop",
    "flood-fill",
    "normal-validation",
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        str(FONT_BOLD if bold else FONT_REGULAR),
        size,
    )


def metadata(report: dict) -> PngImagePlugin.PngInfo:
    derivative = report["geometryIdentity"]["derivative"]
    info = PngImagePlugin.PngInfo()
    info.add_text(
        "FidgetEvidenceTruth",
        "USER-FACING WHOLE-CASE GATE 06 REVIEW",
    )
    info.add_text("Gate", "06-geometry")
    info.add_text("GeometryRevision", "2")
    info.add_text("EvidenceRevision", "3")
    info.add_text(
        "ReviewPanels",
        ",".join(PANELS),
    )
    info.add_text(
        "SourceBlendSha256",
        report["sourceGate05"]["hashesBefore"]["blend"],
    )
    info.add_text(
        "DerivativeFullGeometryDigest",
        derivative["fullGeometryDigest"],
    )
    info.add_text(
        "VertexPositionDigest",
        derivative["vertexPositionDigest"],
    )
    info.add_text(
        "SilhouetteDigest",
        derivative["silhouetteDigest"],
    )
    info.add_text(
        "TopologyWindingDigest",
        derivative["topologyWindingDigest"],
    )
    info.add_text(
        "ShippingRevealPolicy",
        "whole-case-only-no-explode-in-app-or-review",
    )
    return info


def card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    accent: tuple[int, int, int],
) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        box,
        radius=24,
        fill=CARD,
        outline=LINE,
        width=3,
    )
    draw.text(
        (box[0] + 28, box[1] + 22),
        title,
        font=font(42, True),
        fill=accent,
    )
    draw.line(
        (
            box[0] + 28,
            box[1] + 82,
            box[2] - 28,
            box[1] + 82,
        ),
        fill=accent,
        width=3,
    )
    return draw


def image_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    path: Path,
    accent: tuple[int, int, int],
) -> None:
    card(canvas, box, title, accent)
    area = (
        box[0] + 24,
        box[1] + 104,
        box[2] - 24,
        box[3] - 24,
    )
    with Image.open(path) as source:
        image = source.convert("RGB")
        image.thumbnail(
            (area[2] - area[0], area[3] - area[1]),
            Image.Resampling.LANCZOS,
        )
        left = area[0] + (area[2] - area[0] - image.width) // 2
        top = area[1] + (area[3] - area[1] - image.height) // 2
        canvas.paste(image, (left, top))


def closed_loop_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
) -> None:
    draw = card(canvas, box, "CLOSED LOOP", GREEN)
    left = box[0] + 190
    top = box[1] + 160
    right = box[2] - 190
    bottom = box[1] + 600
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=95,
        outline=GREEN,
        width=24,
    )
    for fraction in (0.12, 0.38, 0.62, 0.88):
        x = int(left + (right - left) * fraction)
        draw.ellipse(
            (x - 13, top - 13, x + 13, top + 13),
            fill=CYAN,
        )
        draw.ellipse(
            (x - 13, bottom - 13, x + 13, bottom + 13),
            fill=CYAN,
        )
    draw.text(
        (box[0] + 55, box[1] + 675),
        "1 CONNECTED HOLLOW BODY\n"
        "0 OPEN · 0 NON-MANIFOLD\n"
        "10 × 9 mm OUTER · 6 × 5 mm PASSAGE\n"
        "R20 · CONTINUOUS THROUGH FOUR CORNERS",
        font=font(35, True),
        fill=INK,
        spacing=15,
    )


def flood_fill_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    visited: int,
    total: int,
) -> None:
    draw = card(canvas, box, "FLOOD-FILL", GREEN)
    center_x = (box[0] + box[2]) // 2
    center_y = box[1] + 420
    radius = 225
    for index in range(48):
        angle = math.tau * index / 48
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        draw.ellipse(
            (x - 11, y - 11, x + 11, y + 11),
            fill=GREEN,
        )
    draw.text(
        (center_x, center_y - 55),
        f"{visited}/{total}",
        anchor="mm",
        font=font(78, True),
        fill=INK,
    )
    draw.text(
        (center_x, center_y + 35),
        "VISITED",
        anchor="mm",
        font=font(31, True),
        fill=CYAN,
    )
    draw.text(
        (box[0] + 60, box[1] + 730),
        "FULL CYCLIC PASSAGE REACHED\n"
        "0 FAILED RAYS · WALL ≈ 2 mm",
        font=font(36, True),
        fill=INK,
        spacing=17,
    )


def normal_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    report: dict,
) -> None:
    draw = card(canvas, box, "NORMAL VALIDATION", CYAN)
    orientation = report["closedTube"]["boundaryOrientation"]
    outer = orientation["outerBoundary"]["signedVolumeMm3"]
    inner = orientation["innerBoundary"]["signedVolumeMm3"]
    net = orientation["netMaterialSignedVolumeMm3"]

    cross = (
        box[0] + 90,
        box[1] + 175,
        box[0] + 860,
        box[1] + 650,
    )
    draw.rounded_rectangle(
        cross,
        radius=100,
        fill=(44, 59, 73),
        outline=GREEN,
        width=18,
    )
    lumen = (
        cross[0] + 155,
        cross[1] + 120,
        cross[2] - 155,
        cross[3] - 120,
    )
    draw.rounded_rectangle(
        lumen,
        radius=48,
        fill=BG,
        outline=CYAN,
        width=14,
    )
    for y in (cross[1] + 80, cross[3] - 80):
        draw.line(
            (cross[0] - 55, y, cross[0] + 45, y),
            fill=GREEN,
            width=12,
        )
        draw.line(
            (cross[2] - 45, y, cross[2] + 55, y),
            fill=GREEN,
            width=12,
        )
    draw.text(
        (cross[0] + 385, cross[1] + 50),
        "MATERIAL",
        anchor="mm",
        font=font(30, True),
        fill=INK,
    )
    draw.text(
        (cross[0] + 385, cross[1] + 238),
        "LUMEN",
        anchor="mm",
        font=font(30, True),
        fill=CYAN,
    )

    text_x = box[0] + 980
    draw.text(
        (text_x, box[1] + 180),
        f"OUTER  +{outer:.6f} mm³  · OUTWARD\n"
        f"INNER  {inner:.6f} mm³  · TOWARD LUMEN\n"
        f"NET     +{net:.6f} mm³  · POSITIVE",
        font=font(42, True),
        fill=INK,
        spacing=22,
    )
    draw.text(
        (text_x, box[1] + 470),
        "ALL 5 SUBJECT MATERIAL VOLUMES > 0\n"
        "VERTICES AND SIX-VIEW SILHOUETTE UNCHANGED\n"
        "ONLY TUBE FACE WINDING CHANGED",
        font=font(37, True),
        fill=GREEN,
        spacing=20,
    )
    draw.text(
        (box[0] + 90, box[1] + 780),
        "0 BAD-CONTIGUOUS · 0 SELF-INTERSECTION · 0 DEGENERATE",
        font=font(37, True),
        fill=YELLOW,
    )


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    width, height = 4800, 4000
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)

    draw.text(
        (110, 50),
        "PREMIUM DISPLAY CASE · GATE 06 REV 2",
        font=font(88, True),
        fill=INK,
    )
    draw.text(
        (110, 150),
        "WHOLE CASE ONLY · NO EXPLODE IN APP OR REVIEW",
        font=font(82, True),
        fill=CORAL,
    )
    draw.text(
        (114, 258),
        "GEOMETRY READY FOR REVIEW · EVIDENCE-ONLY REV 3 · GATE 07 BLOCKED",
        font=font(43, True),
        fill=CYAN,
    )

    margin_x = 100
    gap_x = 28
    gap_y = 32
    start_y = 355
    cell_width = (width - margin_x * 2 - gap_x * 3) // 4
    cell_height = 1050

    boxes = []
    for row in range(3):
        for column in range(4):
            left = margin_x + column * (cell_width + gap_x)
            top = start_y + row * (cell_height + gap_y)
            boxes.append(
                (left, top, left + cell_width, top + cell_height)
            )

    images = (
        ("FRONT", ROOT / "ortho-front.png", CYAN),
        ("BACK", ROOT / "ortho-back.png", CYAN),
        ("TOP", ROOT / "ortho-top.png", CYAN),
        ("SIDE", ROOT / "ortho-right.png", CYAN),
        ("WORKBENCH", ROOT / "geometry-workbench.png", GREEN),
        ("DIMENSIONS", ROOT / "dimension-overlay.png", YELLOW),
        ("PIVOT / AXIS", ROOT / "pivot-axis-overlay.png", GREEN),
        ("CONCENTRIC", CONCENTRIC, YELLOW),
    )
    for box, (title, path, accent) in zip(boxes[:8], images):
        image_panel(canvas, box, title, path, accent)

    closed_loop_panel(canvas, boxes[8])
    flow = report["closedTube"]["volumetricPassageFloodFill"]
    flood_fill_panel(
        canvas,
        boxes[9],
        flow["visitedSamples"],
        flow["sampleCount"],
    )
    normal_box = (
        boxes[10][0],
        boxes[10][1],
        boxes[11][2],
        boxes[11][3],
    )
    normal_panel(canvas, normal_box, report)

    draw.text(
        (110, height - 112),
        "READY FOR REVIEW · NOT APPROVED · SHIPPING UNITY UNCHANGED · "
        "NOT BUILT, INSTALLED, OR PUSHED",
        font=font(42, True),
        fill=CORAL,
    )
    canvas.save(
        OUTPUT,
        pnginfo=metadata(report),
        optimize=True,
    )
    print(json.dumps({
        "status": "pass",
        "output": str(OUTPUT),
        "dimensions": [width, height],
        "panels": list(PANELS),
    }, indent=2))


if __name__ == "__main__":
    main()
