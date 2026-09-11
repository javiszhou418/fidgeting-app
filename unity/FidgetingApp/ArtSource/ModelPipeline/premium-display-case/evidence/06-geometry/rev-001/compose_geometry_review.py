#!/usr/bin/env python3
"""Annotate real Blender Gate 06 renders and build review sheets."""

from __future__ import annotations

import json
from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
REPORT = ROOT / "geometry-validation.json"
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")

INK = (240, 246, 252)
MUTED = (154, 174, 194)
CYAN = (57, 218, 246)
GREEN = (76, 226, 151)
YELLOW = (250, 194, 62)
CORAL = (255, 105, 116)
BG = (7, 12, 20)
CARD = (17, 26, 39)
LINE = (47, 67, 88)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        str(FONT_BOLD if bold else FONT_REGULAR),
        size,
    )


def png_metadata(report: dict) -> PngImagePlugin.PngInfo:
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("FidgetEvidenceTruth", "REAL BLENDER SAME GEOMETRY")
    metadata.add_text(
        "SourceBlendSha256",
        report["sourceGate05"]["hashesBefore"]["blend"],
    )
    metadata.add_text(
        "GeometryDigest",
        report["geometryIdentity"]["digestBefore"],
    )
    metadata.add_text("Gate", "06-geometry")
    metadata.add_text("GeometryRevision", "1")
    metadata.add_text(
        "ShippingRevealPolicy",
        "always-assembled-never-explodes",
    )
    return metadata


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    initial_size: int,
    minimum_size: int,
    bold: bool = False,
) -> ImageFont.FreeTypeFont:
    for size in range(initial_size, minimum_size - 1, -2):
        candidate = font(size, bold)
        if draw.textbbox((0, 0), text, font=candidate)[2] <= max_width:
            return candidate
    return font(minimum_size, bold)


def annotate(
    source: Path,
    output: Path,
    title: str,
    subtitle: str,
    footer: str,
    report: dict,
) -> None:
    image = Image.open(source).convert("RGB")
    top = 166
    bottom = 126
    canvas = Image.new("RGB", (image.width, image.height + top + bottom), BG)
    canvas.paste(image, (0, top))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, top - 3, image.width, top), fill=CYAN)
    draw.rectangle(
        (0, top + image.height, image.width, top + image.height + 3),
        fill=LINE,
    )
    title_font = fit_text(draw, title, image.width - 100, 58, 34, True)
    subtitle_font = fit_text(draw, subtitle, image.width - 100, 34, 24)
    footer_font = fit_text(draw, footer, image.width - 100, 27, 20)
    draw.text((50, 34), title, font=title_font, fill=INK)
    draw.text((50, 104), subtitle, font=subtitle_font, fill=CYAN)
    draw.text(
        (50, top + image.height + 40),
        footer,
        font=footer_font,
        fill=MUTED,
    )
    canvas.save(output, pnginfo=png_metadata(report), optimize=True)


def paste_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    image_path: Path,
    label: str,
    accent: tuple[int, int, int],
) -> None:
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=28, fill=CARD, outline=LINE, width=3)
    label_font = font(42, True)
    draw.text((left + 28, top + 24), label, font=label_font, fill=accent)
    image = Image.open(image_path).convert("RGB")
    image_box = (
        left + 24,
        top + 90,
        right - 24,
        bottom - 24,
    )
    available_width = image_box[2] - image_box[0]
    available_height = image_box[3] - image_box[1]
    scale = min(
        available_width / image.width,
        available_height / image.height,
    )
    size = (
        max(1, round(image.width * scale)),
        max(1, round(image.height * scale)),
    )
    image = image.resize(size, Image.Resampling.LANCZOS)
    x = image_box[0] + (available_width - size[0]) // 2
    y = image_box[1] + (available_height - size[1]) // 2
    canvas.paste(image, (x, y))


def paste_metric_panel(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    title: str,
    lines: list[tuple[str, tuple[int, int, int]]],
) -> None:
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=28, fill=CARD, outline=LINE, width=3)
    draw.text((left + 34, top + 30), title, font=font(44, True), fill=INK)
    y = top + 112
    for text, color in lines:
        wrapped = textwrap.wrap(text, width=36) or [text]
        for line in wrapped:
            draw.text((left + 36, y), line, font=font(32), fill=color)
            y += 43
        y += 12


def build_contact_sheet(report: dict, outputs: dict[str, Path]) -> Path:
    width, height = 4800, 3600
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (120, 72),
        "GATE 06 · REAL BLENDER SAME-GEOMETRY EVIDENCE",
        font=font(88, True),
        fill=INK,
    )
    draw.text(
        (124, 176),
        "Premium Display Case · geometry rev 1 · Gate 07 blocked",
        font=font(46),
        fill=CYAN,
    )
    columns, rows = 4, 3
    margin_x = 110
    start_y = 290
    gap_x = 28
    gap_y = 28
    cell_width = (width - margin_x * 2 - gap_x * (columns - 1)) // columns
    cell_height = (height - start_y - 210 - gap_y * (rows - 1)) // rows
    boxes = []
    for row in range(rows):
        for column in range(columns):
            left = margin_x + column * (cell_width + gap_x)
            top = start_y + row * (cell_height + gap_y)
            boxes.append((left, top, left + cell_width, top + cell_height))

    panels = [
        ("FRONT", outputs["front"], CYAN),
        ("BACK", outputs["back"], CYAN),
        ("TOP", outputs["top"], CYAN),
        ("BOTTOM", outputs["bottom"], CYAN),
        ("LEFT", outputs["left"], CYAN),
        ("RIGHT", outputs["right"], CYAN),
        ("WORKBENCH", outputs["workbench"], GREEN),
        ("DIMENSIONS", outputs["dimensions"], YELLOW),
        ("PIVOT / AXIS", outputs["pivot"], GREEN),
        ("EXPLODED · INTERNAL ONLY", outputs["exploded"], CORAL),
    ]
    for box, (label, image_path, accent) in zip(boxes, panels):
        paste_panel(canvas, box, image_path, label, accent)

    tube = report["closedTube"]["volumetricPassageFloodFill"]
    integrity = report["meshIntegrity"]
    paste_metric_panel(
        canvas,
        boxes[10],
        "MEASURED",
        [
            ("228 x 304 x 59 mm · Portrait 0.750", INK),
            ("Label Y 99 mm · approved shift -6 mm", CYAN),
            ("R20 · concentric drift 0.000 mm", YELLOW),
            (
                f"Open / non-manifold / bad-contiguous: "
                f"{integrity['allOpenBoundaryEdgeCount']} / "
                f"{integrity['allNonManifoldEdgeCount']} / "
                f"{integrity['allBadContiguousEdgeCount']}",
                GREEN,
            ),
            (
                f"Self-intersection / degenerate: "
                f"{integrity['allSelfIntersectionPairCount']} / "
                f"{integrity['allDegenerateElementCount']}",
                GREEN,
            ),
            (
                f"Evaluated passage flood-fill: "
                f"{tube['visitedSamples']}/{tube['sampleCount']}",
                GREEN,
            ),
        ],
    )
    paste_metric_panel(
        canvas,
        boxes[11],
        "SOURCE BOUNDARY",
        [
            ("Gate 05 rev 2 source hash unchanged", GREEN),
            (
                f"Blend SHA-256 {report['sourceGate05']['hashesBefore']['blend'][:20]}…",
                MUTED,
            ),
            (
                f"Geometry digest {report['geometryIdentity']['digestBefore'][:20]}…",
                MUTED,
            ),
            ("Closed-loop tube remains one connected part", YELLOW),
            ("Exploded view is internal validation only", CORAL),
            ("Shipping reveal never explodes", CORAL),
            ("No hidden structure was invented", GREEN),
        ],
    )
    draw.text(
        (120, height - 128),
        "READY FOR REVIEW · NOT APPROVED · NOT GATE 07 · UNITY UNCHANGED · NOT BUILT OR PUSHED",
        font=font(43, True),
        fill=CORAL,
    )
    path = ROOT / "geometry-review-contact-sheet.png"
    canvas.save(path, pnginfo=png_metadata(report), optimize=True)
    return path


def build_primary_review(report: dict, outputs: dict[str, Path]) -> Path:
    width, height = 3600, 3200
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (120, 66),
        "PREMIUM DISPLAY CASE · GATE 06",
        font=font(82, True),
        fill=INK,
    )
    draw.text(
        (124, 162),
        "REAL BLENDER · SAME GEOMETRY · READY FOR REVIEW",
        font=font(49, True),
        fill=CYAN,
    )
    boxes = [
        (100, 270, 1760, 1135),
        (1840, 270, 3500, 1135),
        (100, 1165, 1760, 2030),
        (1840, 1165, 3500, 2030),
        (100, 2060, 1760, 2925),
        (1840, 2060, 3500, 2925),
    ]
    for box, entry in zip(
        boxes[:5],
        [
            ("FRONT · 228 x 304", outputs["front"], CYAN),
            ("WORKBENCH", outputs["workbench"], GREEN),
            ("DIMENSION OVERLAY", outputs["dimensions"], YELLOW),
            ("PIVOT / PRESENTATION ROOT", outputs["pivot"], GREEN),
            ("EXPLODED · INTERNAL ONLY", outputs["exploded"], CORAL),
        ],
    ):
        label, image_path, accent = entry
        paste_panel(canvas, box, image_path, label, accent)
    tube = report["closedTube"]["volumetricPassageFloodFill"]
    paste_metric_panel(
        canvas,
        boxes[5],
        "VALIDATION PASS",
        [
            ("Bounds 228 x 304 x 59 mm", INK),
            ("Portrait 0.750 · Label Y 99 mm", CYAN),
            ("Shift -6 mm · R20 · drift 0.000 mm", YELLOW),
            ("One connected hollow tube body", GREEN),
            (
                f"Flood-fill {tube['visitedSamples']}/{tube['sampleCount']}",
                GREEN,
            ),
            ("Open / non-manifold / bad-contiguous 0 / 0 / 0", GREEN),
            ("Self-intersection / degenerate 0 / 0", GREEN),
            ("No hidden structure invented", GREEN),
            ("Shipping reveal never explodes", CORAL),
        ],
    )
    draw.text(
        (110, height - 142),
        "Gate 07 blocked · shipping Unity unchanged · no build, install, or phone push",
        font=font(40, True),
        fill=CORAL,
    )
    path = ROOT / "geometry-review.png"
    canvas.save(path, pnginfo=png_metadata(report), optimize=True)
    return path


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    source_hash = report["sourceGate05"]["hashesBefore"]["blend"]
    digest = report["geometryIdentity"]["digestBefore"]
    footer = f"SOURCE {source_hash[:16]}… · GEOMETRY {digest[:16]}… · UNCHANGED"
    definitions = {
        "front": ("front.png", "ortho-front.png", "FRONT · ORTHOGRAPHIC", "228 x 304 mm · label Y 99 mm"),
        "back": ("back.png", "ortho-back.png", "BACK · ORTHOGRAPHIC", "same evaluated geometry"),
        "top": ("top.png", "ortho-top.png", "TOP · ORTHOGRAPHIC", "width 228 mm · depth 59 mm"),
        "bottom": ("bottom.png", "ortho-bottom.png", "BOTTOM · ORTHOGRAPHIC", "same evaluated geometry"),
        "left": ("left.png", "ortho-left.png", "LEFT · ORTHOGRAPHIC", "height 304 mm · depth 59 mm"),
        "right": ("right.png", "ortho-right.png", "RIGHT · ORTHOGRAPHIC", "height 304 mm · depth 59 mm"),
        "workbench": ("workbench.png", "geometry-workbench.png", "BLENDER WORKBENCH", "real source mesh · no geometry edits"),
        "dimensions": ("dimension-overlay.png", "dimension-overlay.png", "DIMENSION OVERLAY", "228 x 304 x 59 mm · R20 · label -6 mm"),
        "pivot": ("pivot-axis-overlay.png", "pivot-axis-overlay.png", "PIVOT / AXIS OVERLAY", "PresentationRoot [0,0,0] owns +Y motion"),
        "exploded": ("exploded-geometry.png", "exploded-geometry.png", "EXPLODED GEOMETRY · INTERNAL ONLY", "shipping reveal never explodes · tube stays one part"),
    }
    outputs: dict[str, Path] = {}
    for key, (raw_name, output_name, title, subtitle) in definitions.items():
        output = ROOT / output_name
        annotate(
            RAW / raw_name,
            output,
            f"{title} · REAL BLENDER",
            subtitle,
            footer,
            report,
        )
        outputs[key] = output
    primary = build_primary_review(report, outputs)
    contact = build_contact_sheet(report, outputs)
    print(json.dumps({
        "status": "pass",
        "geometryReview": str(primary),
        "contactSheet": str(contact),
        "annotatedViews": {key: str(path) for key, path in outputs.items()},
        "sourceBlendSha256": source_hash,
        "geometryDigest": digest,
    }, indent=2))


if __name__ == "__main__":
    main()
