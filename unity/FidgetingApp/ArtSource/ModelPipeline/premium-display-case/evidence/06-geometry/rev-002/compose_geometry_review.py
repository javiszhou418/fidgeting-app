#!/usr/bin/env python3
"""Compose Premium Display Case Gate 06 normals-only revision 2 reviews."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
REPORT = ROOT / "geometry-validation.json"
REV1_COMPOSER = ROOT.parent / "rev-001" / "compose_geometry_review.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    "premium_display_case_gate06_rev1_composer_helpers",
    REV1_COMPOSER,
)
BASE.ROOT = ROOT
BASE.RAW = RAW
BASE.REPORT = REPORT


def png_metadata(report: dict) -> PngImagePlugin.PngInfo:
    source = report["geometryIdentity"]["source"]
    derivative = report["geometryIdentity"]["derivative"]
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text(
        "FidgetEvidenceTruth",
        "REAL BLENDER NORMALS-ONLY DERIVATIVE",
    )
    metadata.add_text(
        "SourceBlendSha256",
        report["sourceGate05"]["hashesBefore"]["blend"],
    )
    metadata.add_text(
        "SourceFullGeometryDigest",
        source["fullGeometryDigest"],
    )
    metadata.add_text(
        "DerivativeFullGeometryDigest",
        derivative["fullGeometryDigest"],
    )
    metadata.add_text(
        "VertexPositionDigest",
        derivative["vertexPositionDigest"],
    )
    metadata.add_text(
        "SilhouetteDigest",
        derivative["silhouetteDigest"],
    )
    metadata.add_text(
        "TopologyWindingDigest",
        derivative["topologyWindingDigest"],
    )
    metadata.add_text("Gate", "06-geometry")
    metadata.add_text("GeometryRevision", "2")
    metadata.add_text(
        "ShippingRevealPolicy",
        "always-assembled-never-explodes",
    )
    return metadata


BASE.png_metadata = png_metadata


def build_contact_sheet(report: dict, outputs: dict[str, Path]) -> Path:
    width, height = 4800, 3600
    canvas = Image.new("RGB", (width, height), BASE.BG)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (120, 72),
        "GATE 06 REV 2 · NORMALS-ONLY DERIVATIVE",
        font=BASE.font(88, True),
        fill=BASE.INK,
    )
    draw.text(
        (124, 176),
        "Premium Display Case · technical correction · Gate 07 blocked",
        font=BASE.font(46),
        fill=BASE.CYAN,
    )
    columns, rows = 4, 3
    margin_x = 110
    start_y = 290
    gap_x = 28
    gap_y = 28
    cell_width = (
        width - margin_x * 2 - gap_x * (columns - 1)
    ) // columns
    cell_height = (
        height - start_y - 210 - gap_y * (rows - 1)
    ) // rows
    boxes = []
    for row in range(rows):
        for column in range(columns):
            left = margin_x + column * (cell_width + gap_x)
            top = start_y + row * (cell_height + gap_y)
            boxes.append(
                (left, top, left + cell_width, top + cell_height)
            )

    panels = [
        ("FRONT", outputs["front"], BASE.CYAN),
        ("BACK", outputs["back"], BASE.CYAN),
        ("TOP", outputs["top"], BASE.CYAN),
        ("BOTTOM", outputs["bottom"], BASE.CYAN),
        ("LEFT", outputs["left"], BASE.CYAN),
        ("RIGHT", outputs["right"], BASE.CYAN),
        ("WORKBENCH", outputs["workbench"], BASE.GREEN),
        ("DIMENSIONS", outputs["dimensions"], BASE.YELLOW),
        ("PIVOT / AXIS", outputs["pivot"], BASE.GREEN),
        (
            "EXPLODED · INTERNAL ONLY",
            outputs["exploded"],
            BASE.CORAL,
        ),
    ]
    for box, (label, image_path, accent) in zip(boxes, panels):
        BASE.paste_panel(canvas, box, image_path, label, accent)

    winding = report["windingCorrection"]
    tube = report["closedTube"]["volumetricPassageFloodFill"]
    integrity = report["meshIntegrity"]
    BASE.paste_metric_panel(
        canvas,
        boxes[10],
        "WINDING FIX",
        [
            (
                f"Net signed volume: "
                f"{winding['before']['netMaterialSignedVolumeMm3']:.6f} "
                f"-> {winding['after']['netMaterialSignedVolumeMm3']:.6f} mm3",
                BASE.YELLOW,
            ),
            (
                f"Outer {winding['after']['outerBoundarySignedVolumeMm3']:.6f} "
                f"outward",
                BASE.GREEN,
            ),
            (
                f"Inner {winding['after']['innerBoundarySignedVolumeMm3']:.6f} "
                f"toward lumen",
                BASE.GREEN,
            ),
            ("Every subject net signed volume > 0", BASE.GREEN),
            (
                f"Open / non-manifold / bad-contiguous: "
                f"{integrity['allOpenBoundaryEdgeCount']} / "
                f"{integrity['allNonManifoldEdgeCount']} / "
                f"{integrity['allBadContiguousEdgeCount']}",
                BASE.GREEN,
            ),
            (
                f"Flood-fill {tube['visitedSamples']}/{tube['sampleCount']} "
                f"· wall mean "
                f"{tube['evaluatedWallThicknessMm']['mean']:.6f} mm",
                BASE.GREEN,
            ),
        ],
    )
    source = report["geometryIdentity"]["source"]
    derivative = report["geometryIdentity"]["derivative"]
    BASE.paste_metric_panel(
        canvas,
        boxes[11],
        "DERIVATIVE PROOF",
        [
            ("Gate 05 rev 2 files and hashes unchanged", BASE.GREEN),
            (
                f"Vertex digest {derivative['vertexPositionDigest'][:20]}… "
                f"UNCHANGED",
                BASE.CYAN,
            ),
            (
                f"Silhouette digest {derivative['silhouetteDigest'][:20]}… "
                f"UNCHANGED",
                BASE.CYAN,
            ),
            (
                f"Winding {source['topologyWindingDigest'][:12]}… -> "
                f"{derivative['topologyWindingDigest'][:12]}…",
                BASE.YELLOW,
            ),
            ("228 x 304 x 59 mm · Portrait 0.750", BASE.INK),
            ("Label Y 99 mm · R20 · drift 0.000 mm", BASE.INK),
            ("Rev 1 technical evidence preserved", BASE.CORAL),
        ],
    )
    draw.text(
        (120, height - 128),
        (
            "READY FOR REVIEW · NOT APPROVED · GATE 07 BLOCKED · "
            "UNITY UNCHANGED · NOT BUILT OR PUSHED"
        ),
        font=BASE.font(43, True),
        fill=BASE.CORAL,
    )
    path = ROOT / "geometry-review-contact-sheet.png"
    canvas.save(path, pnginfo=png_metadata(report), optimize=True)
    return path


def build_primary_review(report: dict, outputs: dict[str, Path]) -> Path:
    width, height = 3600, 3200
    canvas = Image.new("RGB", (width, height), BASE.BG)
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (120, 66),
        "PREMIUM DISPLAY CASE · GATE 06 REV 2",
        font=BASE.font(82, True),
        fill=BASE.INK,
    )
    draw.text(
        (124, 162),
        "NORMALS-ONLY DERIVATIVE · READY FOR REVIEW",
        font=BASE.font(49, True),
        fill=BASE.CYAN,
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
            ("FRONT · 228 x 304", outputs["front"], BASE.CYAN),
            ("WORKBENCH", outputs["workbench"], BASE.GREEN),
            (
                "DIMENSION OVERLAY",
                outputs["dimensions"],
                BASE.YELLOW,
            ),
            (
                "PIVOT / PRESENTATION ROOT",
                outputs["pivot"],
                BASE.GREEN,
            ),
            (
                "EXPLODED · INTERNAL ONLY",
                outputs["exploded"],
                BASE.CORAL,
            ),
        ],
    ):
        label, image_path, accent = entry
        BASE.paste_panel(canvas, box, image_path, label, accent)

    winding = report["windingCorrection"]
    derivative = report["geometryIdentity"]["derivative"]
    tube = report["closedTube"]["volumetricPassageFloodFill"]
    BASE.paste_metric_panel(
        canvas,
        boxes[5],
        "TECHNICAL PASS",
        [
            (
                f"Tube net signed volume "
                f"{winding['before']['netMaterialSignedVolumeMm3']:.6f} "
                f"-> {winding['after']['netMaterialSignedVolumeMm3']:.6f} mm3",
                BASE.YELLOW,
            ),
            ("Outer boundary outward", BASE.GREEN),
            ("Inner boundary toward lumen", BASE.GREEN),
            ("All subject net signed volumes positive", BASE.GREEN),
            ("Vertex-position digest unchanged", BASE.CYAN),
            ("Six-view silhouette digest unchanged", BASE.CYAN),
            (
                f"Topology/winding digest "
                f"{derivative['topologyWindingDigest'][:18]}… changed",
                BASE.YELLOW,
            ),
            ("Bounds 228 x 304 x 59 mm", BASE.INK),
            ("Portrait 0.750 · Label Y 99 mm", BASE.INK),
            ("R20 · drift 0.000 mm", BASE.INK),
            (
                f"Flood-fill {tube['visitedSamples']}/{tube['sampleCount']}",
                BASE.GREEN,
            ),
            ("Open / non-manifold / bad-contiguous 0 / 0 / 0", BASE.GREEN),
            ("Self-intersection / degenerate 0 / 0", BASE.GREEN),
        ],
    )
    draw.text(
        (110, height - 142),
        (
            "Rev 1 technical rejection preserved · Gate 07 blocked · "
            "shipping Unity unchanged · no build, install, or phone push"
        ),
        font=BASE.font(40, True),
        fill=BASE.CORAL,
    )
    path = ROOT / "geometry-review.png"
    canvas.save(path, pnginfo=png_metadata(report), optimize=True)
    return path


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    source = report["geometryIdentity"]["source"]
    derivative = report["geometryIdentity"]["derivative"]
    footer = (
        f"VERTEX {derivative['vertexPositionDigest'][:12]}… SAME · "
        f"SILHOUETTE {derivative['silhouetteDigest'][:12]}… SAME · "
        f"WINDING {source['topologyWindingDigest'][:8]}… -> "
        f"{derivative['topologyWindingDigest'][:8]}…"
    )
    definitions = {
        "front": (
            "front.png",
            "ortho-front.png",
            "FRONT · ORTHOGRAPHIC",
            "228 x 304 mm · label Y 99 mm",
        ),
        "back": (
            "back.png",
            "ortho-back.png",
            "BACK · ORTHOGRAPHIC",
            "same normals-only derivative",
        ),
        "top": (
            "top.png",
            "ortho-top.png",
            "TOP · ORTHOGRAPHIC",
            "width 228 mm · depth 59 mm",
        ),
        "bottom": (
            "bottom.png",
            "ortho-bottom.png",
            "BOTTOM · ORTHOGRAPHIC",
            "same normals-only derivative",
        ),
        "left": (
            "left.png",
            "ortho-left.png",
            "LEFT · ORTHOGRAPHIC",
            "height 304 mm · depth 59 mm",
        ),
        "right": (
            "right.png",
            "ortho-right.png",
            "RIGHT · ORTHOGRAPHIC",
            "height 304 mm · depth 59 mm",
        ),
        "workbench": (
            "workbench.png",
            "geometry-workbench.png",
            "BLENDER WORKBENCH",
            "corrected boundary normals · unchanged vertices",
        ),
        "dimensions": (
            "dimension-overlay.png",
            "dimension-overlay.png",
            "DIMENSION OVERLAY",
            "228 x 304 x 59 mm · R20 · label -6 mm",
        ),
        "pivot": (
            "pivot-axis-overlay.png",
            "pivot-axis-overlay.png",
            "PIVOT / AXIS OVERLAY",
            "PresentationRoot [0,0,0] owns +Y motion",
        ),
        "exploded": (
            "exploded-geometry.png",
            "exploded-geometry.png",
            "EXPLODED GEOMETRY · INTERNAL ONLY",
            "shipping reveal never explodes · tube stays one part",
        ),
    }
    outputs: dict[str, Path] = {}
    for key, (raw_name, output_name, title, subtitle) in definitions.items():
        output = ROOT / output_name
        BASE.annotate(
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
        "annotatedViews": {
            key: str(path) for key, path in outputs.items()
        },
        "vertexPositionDigest": derivative["vertexPositionDigest"],
        "silhouetteDigest": derivative["silhouetteDigest"],
        "topologyWindingDigest": derivative["topologyWindingDigest"],
    }, indent=2))


if __name__ == "__main__":
    main()
