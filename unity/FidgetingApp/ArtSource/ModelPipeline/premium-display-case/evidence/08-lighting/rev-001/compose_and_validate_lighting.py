#!/usr/bin/env python3
"""Compose and validate Premium Display Case Gate 08 review evidence."""

from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
BUILD_REPORT = ROOT / "lighting-build-report.json"
IMAGE_REPORT = ROOT / "lighting-image-validation.json"

BACKGROUND = (12, 15, 19)
PANEL = (23, 28, 34)
BORDER = (61, 72, 84)
TEXT = (242, 246, 250)
MUTED = (178, 190, 202)
ACCENT = (184, 215, 226)
PASS = (157, 214, 181)
WARNING = (237, 202, 126)
TITLE = "GATE 08 LIGHTING REVIEW · WHOLE CASE ONLY · NO EXPLODE"
STATUS = "READY FOR REVIEW · NOT APPROVED · GATE 09 NOT STARTED"
FOOTER = (
    "APPROVED GATE 06 GEOMETRY + GATE 07 MATERIALS UNCHANGED · "
    "BLENDER LOOKDEV ONLY · SHIPPING UNITY UNCHANGED"
)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(
    size: int,
    bold: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Helvetica.ttf"
        ),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    maximum_width: int,
    start_size: int,
    minimum_size: int,
):
    for size in range(start_size, minimum_size - 1, -1):
        candidate = font(size, bold=True)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= maximum_width:
            return candidate
    return font(minimum_size, bold=True)


def centered_text(
    draw: ImageDraw.ImageDraw,
    width: int,
    y: int,
    text: str,
    text_font,
    fill: tuple[int, int, int],
) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text(
        ((width - (box[2] - box[0])) / 2, y),
        text,
        font=text_font,
        fill=fill,
    )


def panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    path: Path,
    label_color: tuple[int, int, int] = TEXT,
    padding: int = 28,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=26,
        fill=PANEL,
        outline=BORDER,
        width=3,
    )
    label_font = fit_font(draw, label, x1 - x0 - 2 * padding, 38, 22)
    label_box = draw.textbbox((0, 0), label, font=label_font)
    draw.text(
        (
            x0 + (x1 - x0 - (label_box[2] - label_box[0])) / 2,
            y0 + 20,
        ),
        label,
        fill=label_color,
        font=label_font,
    )
    available = (x1 - x0 - 2 * padding, y1 - y0 - 102)
    image = Image.open(path).convert("RGB")
    fitted = ImageOps.contain(image, available, Image.Resampling.LANCZOS)
    canvas.paste(
        fitted,
        (
            x0 + (x1 - x0 - fitted.width) // 2,
            y0 + 82 + (available[1] - fitted.height) // 2,
        ),
    )


def lighting_review(build: dict[str, object], target: Path) -> None:
    width = 4800
    height = 4020
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    centered_text(
        draw,
        width,
        28,
        TITLE,
        fit_font(draw, TITLE, width - 140, 76, 48),
        TEXT,
    )
    centered_text(
        draw,
        width,
        126,
        STATUS,
        fit_font(draw, STATUS, width - 140, 40, 26),
        PASS,
    )
    draw.rectangle((70, 198, width - 70, 204), fill=ACCENT)
    panel(
        canvas,
        draw,
        (70, 240, 2640, 3370),
        "AUTHORED HERO · ASSEMBLED PORTRAIT CASE",
        RAW / "hero.png",
        ACCENT,
        46,
    )
    entries = [
        ("LEFT OBLIQUE · THICKNESS READ", RAW / "left-oblique.png"),
        ("RIGHT OBLIQUE · THICKNESS READ", RAW / "right-oblique.png"),
        ("LOW ANGLE · UNCROPPED SILHOUETTE", RAW / "low.png"),
    ]
    for index, (label, path) in enumerate(entries):
        y0 = 240 + index * 1040
        panel(
            canvas,
            draw,
            (2690, y0, 4730, y0 + 990),
            label,
            path,
            MUTED,
            34,
        )
    ratios = build["lighting"]["ratios"]
    parameter = (
        f"KEY {ratios['key']:.2f}  ·  FILL {ratios['fill']:.2f}  ·  "
        f"RIM {ratios['rim']:.2f}  ·  60 MM / "
        f"{build['cameras']['hero']['verticalFovDegrees']:.2f}° vFOV  ·  "
        f"AGX {build['render']['exposureEv']:+.2f} EV"
    )
    centered_text(
        draw,
        width,
        3440,
        parameter,
        fit_font(draw, parameter, width - 160, 42, 26),
        ACCENT,
    )
    centered_text(
        draw,
        width,
        3515,
        (
            "NEUTRAL PRODUCT LIGHT · NO TEAL RARITY WASH · "
            "NO FIXED GREEN BIAS · NO FULL-FRAME OVEREXPOSURE"
        ),
        fit_font(
            draw,
            (
                "NEUTRAL PRODUCT LIGHT · NO TEAL RARITY WASH · "
                "NO FIXED GREEN BIAS · NO FULL-FRAME OVEREXPOSURE"
            ),
            width - 160,
            34,
            22,
        ),
        PASS,
    )
    centered_text(
        draw,
        width,
        3610,
        FOOTER,
        fit_font(draw, FOOTER, width - 160, 30, 20),
        MUTED,
    )
    question = "APPROVAL QUESTION: APPROVE THIS GATE 08 LIGHTING?"
    centered_text(
        draw,
        width,
        3700,
        question,
        fit_font(draw, question, width - 160, 42, 28),
        TEXT,
    )
    canvas.save(target, optimize=True)


def details_board(target: Path) -> None:
    width = 4500
    height = 2350
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GATE 08 LIGHTING DETAILS · SAME ASSEMBLED CASE"
    centered_text(
        draw,
        width,
        28,
        title,
        fit_font(draw, title, width - 140, 68, 42),
        TEXT,
    )
    subtitle = (
        "LABEL CONTRAST · CONTINUOUS TUBE-CORNER HIGHLIGHT · "
        "BLACK FLOCKING SHADOW DETAIL"
    )
    centered_text(
        draw,
        width,
        120,
        subtitle,
        fit_font(draw, subtitle, width - 140, 34, 22),
        ACCENT,
    )
    draw.rectangle((70, 186, width - 70, 192), fill=ACCENT)
    entries = [
        (
            "LABEL / COVER / FOIL · READABLE",
            RAW / "label-closeup.png",
            "PAPER + GRAPHITE + NARROW SILVER FOIL",
        ),
        (
            "CLOSED TUBE CORNER · CONTINUOUS HIGHLIGHT",
            RAW / "tube-corner.png",
            "ONE CONNECTED LOOP · TANGENT CORNER RESPONSE",
        ),
        (
            "BLACK FLOCKING · SHADOW DETAIL PRESERVED",
            RAW / "black-panel.png",
            "DARK, NOT CRUSHED · BOUNDARY REMAINS VISIBLE",
        ),
    ]
    column_width = 1420
    for index, (label, path, note) in enumerate(entries):
        x0 = 70 + index * 1470
        panel(
            canvas,
            draw,
            (x0, 235, x0 + column_width, 2050),
            label,
            path,
            ACCENT,
            26,
        )
        centered_text(
            draw,
            column_width,
            0,
            "",
            font(12),
            TEXT,
        )
        note_font = fit_font(draw, note, column_width - 40, 28, 18)
        note_box = draw.textbbox((0, 0), note, font=note_font)
        draw.text(
            (
                x0 + (column_width - (note_box[2] - note_box[0])) / 2,
                2080,
            ),
            note,
            fill=PASS,
            font=note_font,
        )
    centered_text(
        draw,
        width,
        2220,
        FOOTER,
        fit_font(draw, FOOTER, width - 140, 28, 18),
        MUTED,
    )
    canvas.save(target, optimize=True)


def passes_board(target: Path) -> None:
    width = 4800
    height = 3280
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GATE 08 LIGHTING PASSES · BEAUTY / CLAY / NORMAL / DEPTH / ROUGHNESS"
    centered_text(
        draw,
        width,
        28,
        title,
        fit_font(draw, title, width - 140, 68, 40),
        TEXT,
    )
    subtitle = (
        "TECHNICAL OVERRIDES ARE REVIEW-ONLY · "
        "APPROVED GATE 07 MATERIAL ASSIGNMENTS RESTORED"
    )
    centered_text(
        draw,
        width,
        120,
        subtitle,
        fit_font(draw, subtitle, width - 140, 34, 22),
        ACCENT,
    )
    draw.rectangle((70, 186, width - 70, 192), fill=ACCENT)
    panel(
        canvas,
        draw,
        (70, 235, 2380, 2940),
        "BEAUTY · APPROVED GATE 07 MATERIALS",
        RAW / "pass-beauty.png",
        ACCENT,
        42,
    )
    cells = [
        ("CLAY", RAW / "pass-clay.png"),
        ("NORMAL", RAW / "pass-normal.png"),
        ("DEPTH", RAW / "pass-depth.png"),
        ("ROUGHNESS", RAW / "pass-roughness.png"),
    ]
    boxes = [
        (2430, 235, 3560, 1560),
        (3610, 235, 4730, 1560),
        (2430, 1610, 3560, 2940),
        (3610, 1610, 4730, 2940),
    ]
    for (label, path), box in zip(cells, boxes):
        panel(canvas, draw, box, label, path, MUTED, 24)
    centered_text(
        draw,
        width,
        3040,
        FOOTER,
        fit_font(draw, FOOTER, width - 140, 28, 18),
        MUTED,
    )
    canvas.save(target, optimize=True)


def parameter_board(build: dict[str, object], target: Path) -> None:
    width = 4000
    height = 2820
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GATE 08 LIGHTING PARAMETERS · LARGE-TYPE REVIEW"
    centered_text(
        draw,
        width,
        30,
        title,
        fit_font(draw, title, width - 140, 70, 44),
        TEXT,
    )
    subtitle = "BLENDER LOOKDEV VALUES · NOT CURRENT UNITY RUNTIME PARAMETERS"
    centered_text(
        draw,
        width,
        126,
        subtitle,
        fit_font(draw, subtitle, width - 140, 38, 24),
        WARNING,
    )
    draw.rectangle((70, 194, width - 70, 200), fill=ACCENT)
    hero = build["cameras"]["hero"]
    rows = [
        (
            "KEY / FILL / RIM",
            "1.00 / 0.30 / 0.40",
            "REQUESTED RANGES: FILL 0.25–0.35 · RIM 0.30–0.45",
        ),
        (
            "LIGHT COLOR TEMPERATURE",
            "KEY 5000 K · FILL 6200 K · RIM 5600 K",
            "LOW-CHROMA NEUTRAL SOURCES · NO TEAL RARITY LIGHT",
        ),
        (
            "HERO CAMERA",
            (
                f"{hero['lensMm']:.0f} MM · {hero['verticalFovDegrees']:.2f}° vFOV · "
                f"SENSOR {hero['sensorWidthMm']:.0f} × {hero['sensorHeightMm']:.0f} MM"
            ),
            "PORTRAIT THICKNESS READ · NO DEPTH OF FIELD · NO WIDE-LENS DISTORTION",
        ),
        (
            "COLOR MANAGEMENT",
            (
                f"{build['render']['viewTransform']} · {build['render']['look']} · "
                f"{build['render']['exposureEv']:+.2f} EV"
            ),
            "SHUTTER / ISO UNSET · NO UNITY RUNTIME MAPPING CLAIMED",
        ),
        (
            "LOCKED INPUT DIGESTS",
            (
                f"GEOMETRY {build['geometry']['digestAfter'][:16]}… · "
                f"MATERIAL {build['materials']['digestAfter'][:16]}…"
            ),
            "IDENTICAL BEFORE / AFTER LIGHTING AND TECHNICAL PASSES",
        ),
        (
            "SCOPE",
            "GATE 08 READY FOR REVIEW · GATE 09 BLOCKED",
            "WHOLE CASE ONLY · SHIPPING UNITY / BUILD / INSTALL / PHONE UNCHANGED",
        ),
    ]
    top = 250
    row_height = 395
    for index, (name, primary, secondary) in enumerate(rows):
        y0 = top + index * row_height
        draw.rounded_rectangle(
            (100, y0, width - 100, y0 + row_height - 30),
            radius=24,
            fill=PANEL,
            outline=BORDER,
            width=3,
        )
        draw.text(
            (145, y0 + 32),
            name,
            font=fit_font(draw, name, width - 290, 40, 28),
            fill=TEXT,
        )
        draw.text(
            (145, y0 + 112),
            primary,
            font=fit_font(draw, primary, width - 290, 38, 24),
            fill=ACCENT,
        )
        draw.text(
            (145, y0 + 205),
            secondary,
            font=fit_font(draw, secondary, width - 290, 30, 19),
            fill=PASS,
        )
    centered_text(
        draw,
        width,
        2660,
        STATUS,
        fit_font(draw, STATUS, width - 140, 34, 22),
        PASS,
    )
    canvas.save(target, optimize=True)


def rgb_and_luma(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    luma = (
        rgb[..., 0] * 0.2126
        + rgb[..., 1] * 0.7152
        + rgb[..., 2] * 0.0722
    )
    return rgb, luma


def image_metrics(path: Path) -> dict[str, object]:
    rgb, luma = rgb_and_luma(path)
    return {
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "meanLuma": round(float(luma.mean()), 6),
        "p01Luma": round(float(np.percentile(luma, 1)), 6),
        "p99Luma": round(float(np.percentile(luma, 99)), 6),
        "highlightClipFraction": round(
            float((rgb.max(axis=2) >= 250.0).mean()),
            10,
        ),
        "blackClipFraction": round(float((luma <= 1.0).mean()), 10),
    }


def green_bias_metrics(path: Path) -> dict[str, object]:
    rgb, luma = rgb_and_luma(path)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    mask = (luma >= 12.0) & (luma <= 245.0) & (chroma <= 30.0)
    selected = rgb[mask]
    if len(selected) == 0:
        return {
            "selectedPixels": 0,
            "meanGreenExcess": None,
            "p95AbsoluteGreenExcess": None,
            "greenExcessAbove8Fraction": None,
        }
    excess = selected[:, 1] - (selected[:, 0] + selected[:, 2]) * 0.5
    return {
        "selectedPixels": int(len(selected)),
        "meanGreenExcess": round(float(excess.mean()), 8),
        "p95AbsoluteGreenExcess": round(
            float(np.percentile(np.abs(excess), 95)),
            8,
        ),
        "greenExcessAbove8Fraction": round(float((excess > 8.0).mean()), 10),
    }


def label_metrics(path: Path) -> dict[str, object]:
    rgb, luma = rgb_and_luma(path)
    height, width = luma.shape
    x0, x1 = int(width * 0.05), int(width * 0.95)
    y0, y1 = int(height * 0.12), int(height * 0.88)
    crop = luma[y0:y1, x0:x1]
    center = luma[
        int(height * 0.28) : int(height * 0.72),
        int(width * 0.18) : int(width * 0.82),
    ]
    border = np.concatenate(
        (
            luma[: int(height * 0.12)].reshape(-1),
            luma[int(height * 0.88) :].reshape(-1),
            luma[:, : int(width * 0.05)].reshape(-1),
            luma[:, int(width * 0.95) :].reshape(-1),
        )
    )
    return {
        "cropPx": [x0, y0, x1, y1],
        "p10Luma": round(float(np.percentile(crop, 10)), 6),
        "p90Luma": round(float(np.percentile(crop, 90)), 6),
        "p10P90Contrast": round(
            float(np.percentile(crop, 90) - np.percentile(crop, 10)),
            6,
        ),
        "centerMeanLuma": round(float(center.mean()), 6),
        "borderMeanLuma": round(float(border.mean()), 6),
        "labelBackgroundMeanContrast": round(
            float(center.mean() - border.mean()),
            6,
        ),
        "blackoutFraction": round(float((crop < 5.0).mean()), 10),
    }


def black_panel_metrics(path: Path) -> dict[str, object]:
    _, luma = rgb_and_luma(path)
    height, width = luma.shape
    crop = luma[
        int(height * 0.12) : int(height * 0.90),
        int(width * 0.12) : int(width * 0.88),
    ]
    p05 = float(np.percentile(crop, 5))
    p50 = float(np.percentile(crop, 50))
    p95 = float(np.percentile(crop, 95))
    return {
        "p05Luma": round(p05, 6),
        "medianLuma": round(p50, 6),
        "p95Luma": round(p95, 6),
        "p05P95Range": round(p95 - p05, 6),
        "crushedBelow4Fraction": round(float((crop <= 4.0).mean()), 10),
    }


def largest_component(mask: np.ndarray) -> dict[str, object]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    best: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            queue = deque([(y, x)])
            visited[y, x] = True
            component = []
            while queue:
                cy, cx = queue.popleft()
                component.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        ny, nx = cy + dy, cx + dx
                        if (
                            0 <= ny < height
                            and 0 <= nx < width
                            and mask[ny, nx]
                            and not visited[ny, nx]
                        ):
                            visited[ny, nx] = True
                            queue.append((ny, nx))
            if len(component) > len(best):
                best = component
    if not best:
        return {
            "pixelCount": 0,
            "boundsPx": [0, 0, 0, 0],
            "widthFraction": 0.0,
            "heightFraction": 0.0,
        }
    ys = [item[0] for item in best]
    xs = [item[1] for item in best]
    return {
        "pixelCount": len(best),
        "boundsPx": [min(xs), min(ys), max(xs), max(ys)],
        "widthFraction": round((max(xs) - min(xs) + 1) / width, 8),
        "heightFraction": round((max(ys) - min(ys) + 1) / height, 8),
    }


def tube_highlight_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("L")
    reduced = image.resize(
        (max(1, image.width // 5), max(1, image.height // 5)),
        Image.Resampling.BILINEAR,
    )
    luma = np.asarray(reduced, dtype=np.float32)
    threshold = max(50.0, float(np.percentile(luma, 76)))
    raw = (luma >= threshold).astype(np.uint8) * 255
    closed = np.asarray(
        Image.fromarray(raw)
        .filter(ImageFilter.MaxFilter(size=5))
        .filter(ImageFilter.MinFilter(size=5)),
        dtype=np.uint8,
    )
    mask = closed > 0
    component = largest_component(mask)
    return {
        "thresholdLuma": round(threshold, 6),
        "brightFraction": round(float(mask.mean()), 10),
        "largestBrightComponent": component,
        "pass": (
            component["pixelCount"] >= 240
            and component["widthFraction"] >= 0.18
            and component["heightFraction"] >= 0.18
        ),
    }


def boundary_metrics(path: Path) -> dict[str, object]:
    _, luma = rgb_and_luma(path)
    height, width = luma.shape
    crop = luma[
        int(height * 0.10) : int(height * 0.92),
        int(width * 0.08) : int(width * 0.92),
    ]
    horizontal = np.abs(np.diff(crop, axis=1))
    vertical = np.abs(np.diff(crop, axis=0))
    gradients = np.concatenate((horizontal.reshape(-1), vertical.reshape(-1)))
    return {
        "p99Gradient": round(float(np.percentile(gradients, 99)), 6),
        "gradientAbove8Fraction": round(float((gradients >= 8.0).mean()), 10),
        "p05P95LumaRange": round(
            float(np.percentile(crop, 95) - np.percentile(crop, 5)),
            6,
        ),
    }


def pass_metrics(path: Path) -> dict[str, object]:
    rgb, luma = rgb_and_luma(path)
    mask = rgb.max(axis=2) >= 7.0
    selected = rgb[mask]
    selected_luma = luma[mask]
    if len(selected) == 0:
        selected = rgb.reshape(-1, 3)
        selected_luma = luma.reshape(-1)
    chroma = selected.max(axis=1) - selected.min(axis=1)
    return {
        "selectedPixels": int(len(selected)),
        "channelStd": [
            round(float(value), 6) for value in selected.std(axis=0)
        ],
        "medianChannelChroma": round(float(np.median(chroma)), 6),
        "p05Luma": round(float(np.percentile(selected_luma, 5)), 6),
        "p95Luma": round(float(np.percentile(selected_luma, 95)), 6),
        "p05P95LumaRange": round(
            float(
                np.percentile(selected_luma, 95)
                - np.percentile(selected_luma, 5)
            ),
            6,
        ),
    }


def image_difference(first: Path, second: Path) -> float:
    a = np.asarray(
        Image.open(first).convert("RGB").resize((320, 360)),
        dtype=np.float32,
    )
    b = np.asarray(
        Image.open(second).convert("RGB").resize((320, 360)),
        dtype=np.float32,
    )
    return round(float(np.abs(a - b).mean()), 6)


def artifact_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sha256": sha256(path),
        "sizeBytes": path.stat().st_size,
        "dimensions": list(Image.open(path).size),
    }


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    if build["status"] != "pass":
        raise RuntimeError("Gate 08 build report did not pass.")
    outputs = {
        "lighting-review": ROOT / "lighting-review.png",
        "lighting-details": ROOT / "lighting-details-contact-sheet.png",
        "lighting-passes": ROOT / "lighting-passes-contact-sheet.png",
        "lighting-parameters": ROOT / "lighting-parameters-board.png",
    }
    lighting_review(build, outputs["lighting-review"])
    details_board(outputs["lighting-details"])
    passes_board(outputs["lighting-passes"])
    parameter_board(build, outputs["lighting-parameters"])

    beauty_paths = {
        "hero": RAW / "hero.png",
        "leftOblique": RAW / "left-oblique.png",
        "rightOblique": RAW / "right-oblique.png",
        "low": RAW / "low.png",
        "beauty": RAW / "pass-beauty.png",
        "labelCloseup": RAW / "label-closeup.png",
        "tubeCorner": RAW / "tube-corner.png",
        "blackPanel": RAW / "black-panel.png",
    }
    raw_metrics = {
        name: image_metrics(path) for name, path in beauty_paths.items()
    }
    green_metrics = {
        name: green_bias_metrics(path)
        for name, path in beauty_paths.items()
        if name
        in {
            "hero",
            "leftOblique",
            "rightOblique",
            "low",
            "beauty",
        }
    }
    label = label_metrics(beauty_paths["labelCloseup"])
    black_panel = black_panel_metrics(beauty_paths["blackPanel"])
    tube = tube_highlight_metrics(beauty_paths["tubeCorner"])
    boundaries = {
        name: boundary_metrics(beauty_paths[name])
        for name in ("hero", "leftOblique", "rightOblique", "low")
    }
    passes = {
        name: pass_metrics(RAW / f"pass-{name}.png")
        for name in ("clay", "normal", "depth", "roughness")
    }
    differences = {
        "leftVsRight": image_difference(
            beauty_paths["leftOblique"],
            beauty_paths["rightOblique"],
        ),
        "heroVsLow": image_difference(
            beauty_paths["hero"],
            beauty_paths["low"],
        ),
    }
    checks = {
        "builderPassed": build["status"] == "pass",
        "requiredViewsAndPassesPresent": all(
            path.exists() and path.stat().st_size > 30_000
            for path in (
                *beauty_paths.values(),
                RAW / "pass-clay.png",
                RAW / "pass-normal.png",
                RAW / "pass-depth.png",
                RAW / "pass-roughness.png",
            )
        ),
        "reviewBoardsPresent": all(
            path.exists() and path.stat().st_size > 150_000
            for path in outputs.values()
        ),
        "highlightClippingBelowHalfPercent": all(
            metric["highlightClipFraction"] < 0.005
            for metric in raw_metrics.values()
        ),
        "labelBackgroundContrast": (
            label["p10P90Contrast"] >= 45.0
            and label["labelBackgroundMeanContrast"] >= 20.0
            and label["blackoutFraction"] <= 0.10
        ),
        "darkSubjectBoundariesVisible": all(
            metric["p99Gradient"] >= 4.0
            and metric["gradientAbove8Fraction"] >= 0.0075
            and metric["p05P95LumaRange"] >= 25.0
            for metric in boundaries.values()
        ),
        "blackFlockingNotCrushed": (
            black_panel["medianLuma"] >= 8.0
            and black_panel["p05P95Range"] >= 12.0
            and black_panel["crushedBelow4Fraction"] <= 0.30
        ),
        "greenBiasControlled": all(
            metric["selectedPixels"] >= 10_000
            and abs(metric["meanGreenExcess"]) <= 4.0
            and metric["greenExcessAbove8Fraction"] <= 0.08
            for metric in green_metrics.values()
        ),
        "tubeCornerHighlightContinuous": tube["pass"],
        "mainViewsUncropped": all(
            item["notCropped"] and item["comfortableMargin"]
            for item in build["framing"].values()
        ),
        "distinctAuthoredViews": (
            differences["leftVsRight"] >= 3.0
            and differences["heroVsLow"] >= 5.0
        ),
        "clayPassValid": (
            passes["clay"]["medianChannelChroma"] <= 8.0
            and passes["clay"]["p05P95LumaRange"] >= 25.0
        ),
        "normalPassValid": (
            min(passes["normal"]["channelStd"]) >= 8.0
            and passes["normal"]["medianChannelChroma"] >= 12.0
        ),
        "depthPassValid": (
            passes["depth"]["medianChannelChroma"] <= 1.0
            and passes["depth"]["p05P95LumaRange"] >= 20.0
        ),
        "roughnessPassValid": (
            passes["roughness"]["medianChannelChroma"] <= 1.0
            and passes["roughness"]["p05P95LumaRange"] >= 8.0
        ),
        "geometryAndMaterialDigestsUnchanged": (
            build["geometry"]["unchanged"]
            and build["materials"]["unchanged"]
            and build["materials"]["assignmentsRestored"]
        ),
        "grainStableAtFiveAngles": build["grainStability"]["pass"],
        "transparentOrderingPreflight": build["materials"][
            "transparentOrderingPreflight"
        ]["pass"],
        "wholeCaseOnlyNoExplode": (
            build["scope"]["wholeCaseOnly"]
            and not build["scope"]["explode"]
        ),
        "gate08ReadyNotApproved": (
            build["scope"]["gate08Status"] == "ready_for_review"
            and not build["scope"]["gate08Approved"]
        ),
        "gate09NotEntered": not build["scope"]["gate09Entered"],
        "shippingUnityUnchanged": not build["scope"]["shippingUnityChanged"],
        "noBuildInstallPhonePush": not build["scope"][
            "buildInstallPhonePush"
        ],
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "rawMetrics": raw_metrics,
        "greenBiasMetrics": green_metrics,
        "labelMetrics": label,
        "blackPanelMetrics": black_panel,
        "tubeHighlightContinuity": tube,
        "boundaryMetrics": boundaries,
        "passMetrics": passes,
        "viewDifferences": differences,
        "framing": build["framing"],
        "artifacts": {
            name: artifact_record(path) for name, path in outputs.items()
        },
        "checks": checks,
    }
    IMAGE_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "lightingReview": str(outputs["lighting-review"]),
                "maximumClipFraction": max(
                    item["highlightClipFraction"]
                    for item in raw_metrics.values()
                ),
                "label": label,
                "blackPanel": black_panel,
                "tube": tube,
                "greenBias": green_metrics,
                "checks": checks,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))
if __name__ == "__main__":
    main()
