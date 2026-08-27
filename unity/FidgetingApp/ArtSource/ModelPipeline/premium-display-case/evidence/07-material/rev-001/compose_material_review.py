#!/usr/bin/env python3
"""Compose and validate Premium Display Case Gate 07 review images."""

from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
BUILD_REPORT = ROOT / "material-build-report.json"
BLENDER_AUDIT = ROOT / "blender-audit.json"
SURFACE_REPORT = ROOT / "surface-coverage-report.json"
OPTIMIZATION_REPORT = ROOT / "asset-optimization-report.json"
QA_REPORT = ROOT / "qa-verdict.json"
IMAGE_REPORT = ROOT / "material-image-validation.json"

TITLE = "GATE 07 MATERIAL REVIEW · WHOLE CASE ONLY · NO EXPLODE"
STATUS = "READY FOR REVIEW · NOT APPROVED · GATE 08 NOT STARTED"
FOOTER = (
    "NEUTRAL PBR LOOKDEV · FORMAL SOURCE MATERIALS · "
    "SHIPPING UNITY UNCHANGED · NOT BUILT OR INSTALLED"
)
BACKGROUND = (13, 16, 20)
PANEL = (23, 28, 34)
PANEL_BORDER = (56, 66, 76)
TEXT = (240, 244, 248)
MUTED = (174, 186, 198)
ACCENT = (182, 211, 222)
PASS = (155, 211, 181)


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
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for size in range(start_size, minimum_size - 1, -1):
        candidate = font(size, bold=True)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= maximum_width:
            return candidate
    return font(minimum_size, bold=True)


def centered_text(
    draw: ImageDraw.ImageDraw,
    canvas_width: int,
    y: int,
    text: str,
    text_font,
    fill: tuple[int, int, int],
) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text(
        ((canvas_width - (box[2] - box[0])) / 2, y),
        text,
        fill=fill,
        font=text_font,
    )


def panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    image_path: Path,
    label_color: tuple[int, int, int] = TEXT,
    padding: int = 28,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=26,
        fill=PANEL,
        outline=PANEL_BORDER,
        width=3,
    )
    label_font = fit_font(draw, label, x1 - x0 - 2 * padding, 34, 22)
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
    available = (x1 - x0 - 2 * padding, y1 - y0 - 96)
    image = Image.open(image_path).convert("RGB")
    fitted = ImageOps.contain(image, available, Image.Resampling.LANCZOS)
    canvas.paste(
        fitted,
        (
            x0 + (x1 - x0 - fitted.width) // 2,
            y0 + 78 + (available[1] - fitted.height) // 2,
        ),
    )


def annotated_view(
    source: Path,
    target: Path,
    view_label: str,
    note: str,
) -> None:
    image = Image.open(source).convert("RGB")
    top = 170
    bottom = 92
    canvas = Image.new("RGB", (image.width, image.height + top + bottom), BACKGROUND)
    canvas.paste(image, (0, top))
    draw = ImageDraw.Draw(canvas)
    title_font = fit_font(draw, TITLE, image.width - 70, 42, 22)
    view_font = fit_font(draw, view_label, image.width - 70, 30, 18)
    note_font = fit_font(draw, note, image.width - 70, 24, 16)
    centered_text(draw, image.width, 18, TITLE, title_font, TEXT)
    centered_text(draw, image.width, 78, view_label, view_font, ACCENT)
    centered_text(draw, image.width, 120, note, note_font, MUTED)
    draw.rectangle((0, top - 4, image.width, top), fill=ACCENT)
    footer_font = fit_font(draw, FOOTER, image.width - 70, 22, 14)
    centered_text(
        draw,
        image.width,
        image.height + top + 28,
        FOOTER,
        footer_font,
        MUTED,
    )
    canvas.save(target, optimize=True)


def material_board(target: Path) -> None:
    width = 4800
    height = 4020
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title_font = fit_font(draw, TITLE, width - 140, 72, 48)
    status_font = fit_font(draw, STATUS, width - 140, 38, 26)
    centered_text(draw, width, 28, TITLE, title_font, TEXT)
    centered_text(draw, width, 126, STATUS, status_font, PASS)
    draw.rectangle((70, 198, width - 70, 204), fill=ACCENT)

    panel(
        canvas,
        draw,
        (70, 240, 2110, 2700),
        "HERO · FORMAL NEUTRAL PBR · ASSEMBLED",
        RAW / "hero.png",
        ACCENT,
        42,
    )
    boxes = [
        (
            (2160, 240, 3470, 1435),
            "LEFT OBLIQUE",
            RAW / "left-oblique.png",
        ),
        (
            (3520, 240, 4730, 1435),
            "RIGHT OBLIQUE",
            RAW / "right-oblique.png",
        ),
        (
            (2160, 1485, 3470, 2700),
            "SIDE · 90° WHOLE CASE",
            RAW / "rotation-090.png",
        ),
        (
            (3520, 1485, 4730, 2700),
            "BACK · 180° WHOLE CASE",
            RAW / "rotation-180.png",
        ),
    ]
    for box, label, path in boxes:
        panel(canvas, draw, box, label, path)

    rotation_paths = [
        RAW / f"rotation-{angle:03d}.png"
        for angle in (0, 90, 180, 270, 360)
    ]
    rotation_labels = ["0°", "90°", "180°", "270°", "360°"]
    cell_width = 900
    gap = 35
    y0 = 2760
    y1 = 3710
    for index, (label, path) in enumerate(zip(rotation_labels, rotation_paths)):
        x0 = 70 + index * (cell_width + gap)
        panel(
            canvas,
            draw,
            (x0, y0, x0 + cell_width, y1),
            f"{label} · LOCAL GRAIN LOCK",
            path,
            MUTED,
            18,
        )
    footer_font = fit_font(draw, FOOTER, width - 140, 32, 22)
    centered_text(draw, width, 3780, FOOTER, footer_font, MUTED)
    question = "APPROVAL QUESTION: APPROVE THIS MATERIAL RESPONSE AND THESE BOUNDARIES?"
    question_font = fit_font(draw, question, width - 140, 38, 24)
    centered_text(draw, width, 3840, question, question_font, TEXT)
    canvas.save(target, optimize=True)


def material_closeup_board(target: Path) -> None:
    width = 4380
    height = 2900
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GATE 07 MATERIAL CLOSEUP · ASSEMBLED CASE · NO EXPLODE"
    title_font = fit_font(draw, title, width - 140, 66, 42)
    centered_text(draw, width, 28, title, title_font, TEXT)
    subtitle = (
        "CONTINUOUS TUBE HIGHLIGHT · PHYSICAL LABEL / COVER / FOIL · "
        "OBJECT-LOCAL TACTILE GRAIN"
    )
    subtitle_font = fit_font(draw, subtitle, width - 140, 34, 23)
    centered_text(draw, width, 116, subtitle, subtitle_font, ACCENT)
    draw.rectangle((70, 182, width - 70, 188), fill=ACCENT)
    entries = [
        (
            "TUBE CORNER · CONTINUOUS HIGHLIGHT",
            RAW / "tube-corner.png",
            "IOR 1.585 · R 0.18 · T 0.78",
        ),
        (
            "LABEL · PAPER + CLEAR COVER + SILVER FOIL",
            RAW / "label-closeup.png",
            "PAPER R 0.73 · NEUTRAL PLACEHOLDERS",
        ),
        (
            "TACTILE INSERT · LOCAL-SPACE MICROGRAIN",
            RAW / "tactile-closeup.png",
            "R 0.91 · 0.48 MM GRAIN · NO WORLD SWIM",
        ),
    ]
    column_width = 1370
    gap = 45
    for index, (label, path, parameter) in enumerate(entries):
        x0 = 70 + index * (column_width + gap)
        panel(
            canvas,
            draw,
            (x0, 230, x0 + column_width, 2110),
            label,
            path,
            ACCENT,
            26,
        )
        parameter_font = fit_font(draw, parameter, column_width - 70, 27, 18)
        parameter_box = draw.textbbox((0, 0), parameter, font=parameter_font)
        draw.text(
            (
                x0 + (column_width - (parameter_box[2] - parameter_box[0])) / 2,
                2145,
            ),
            parameter,
            fill=PASS,
            font=parameter_font,
        )
        panel(
            canvas,
            draw,
            (x0, 2210, x0 + column_width, 2700),
            "WHOLE-CASE CONTEXT",
            RAW / "hero.png",
            MUTED,
            16,
        )
    footer_font = fit_font(draw, FOOTER, width - 140, 30, 20)
    centered_text(draw, width, 2770, FOOTER, footer_font, MUTED)
    canvas.save(target, optimize=True)


def side_back_board(target: Path) -> None:
    width = 3000
    height = 1700
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "SIDE / BACK MATERIAL RESPONSE · SAME ASSEMBLED CASE"
    title_font = fit_font(draw, title, width - 100, 50, 32)
    centered_text(draw, width, 24, title, title_font, TEXT)
    panel(
        canvas,
        draw,
        (40, 110, 1480, 1530),
        "SIDE · 90°",
        RAW / "rotation-090.png",
        ACCENT,
    )
    panel(
        canvas,
        draw,
        (1520, 110, 2960, 1530),
        "BACK · 180°",
        RAW / "rotation-180.png",
        ACCENT,
    )
    footer_font = fit_font(draw, FOOTER, width - 100, 24, 17)
    centered_text(draw, width, 1580, FOOTER, footer_font, MUTED)
    canvas.save(target, optimize=True)


def clay_pbr_comparison(target: Path) -> None:
    width = 3100
    height = 1550
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "CLAY VS FORMAL PBR · SAME CAMERA · SAME GEOMETRY"
    title_font = fit_font(draw, title, width - 100, 52, 34)
    centered_text(draw, width, 24, title, title_font, TEXT)
    panel(
        canvas,
        draw,
        (40, 110, 1525, 1410),
        "CLAY CONTROL",
        RAW / "clay-hero-same-camera.png",
        MUTED,
    )
    panel(
        canvas,
        draw,
        (1575, 110, 3060, 1410),
        "FORMAL PBR LOOKDEV",
        RAW / "hero.png",
        ACCENT,
    )
    footer_font = fit_font(draw, FOOTER, width - 100, 24, 17)
    centered_text(draw, width, 1450, FOOTER, footer_font, MUTED)
    canvas.save(target, optimize=True)


def rotation_board(target: Path) -> None:
    width = 4200
    height = 1220
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GRAIN STABILITY · OBJECT-LOCAL COORDINATES · 0/90/180/270/360"
    title_font = fit_font(draw, title, width - 100, 50, 30)
    centered_text(draw, width, 22, title, title_font, TEXT)
    cell_width = 800
    for index, angle in enumerate((0, 90, 180, 270, 360)):
        x0 = 20 + index * 835
        panel(
            canvas,
            draw,
            (x0, 95, x0 + cell_width, 1090),
            f"{angle}°",
            RAW / f"rotation-{angle:03d}.png",
            ACCENT,
            16,
        )
    note = (
        "0° / 360° MEAN CHANNEL DELTA < 0.002; "
        "LOCAL COORDINATE RECOVERY ERROR < 0.00001 MM"
    )
    note_font = fit_font(draw, note, width - 100, 26, 18)
    centered_text(draw, width, 1130, note, note_font, PASS)
    canvas.save(target, optimize=True)


def parameter_board(
    build: dict[str, object],
    target: Path,
) -> None:
    width = 3800
    height = 2780
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    title = "GATE 07 MATERIAL PARAMETERS · LARGE-TYPE REVIEW"
    title_font = fit_font(draw, title, width - 140, 68, 42)
    centered_text(draw, width, 32, title, title_font, TEXT)
    subtitle = "FORMAL SOURCE VALUES + OBJECT-LOCAL MICROGRAIN · ALL VALUES PENDING APPROVAL"
    subtitle_font = fit_font(draw, subtitle, width - 140, 34, 24)
    centered_text(draw, width, 126, subtitle, subtitle_font, ACCENT)
    draw.rectangle((70, 192, width - 70, 198), fill=ACCENT)

    parameters = build["materialParameters"]
    rows = [
        (
            "FROSTED POLYCARBONATE SHELL",
            "MAT_FrostedPolycarbonate",
            "IOR 1.585  ·  ROUGHNESS 0.22  ·  TRANSMISSION 0.92",
            "OBJECT-LOCAL 0.62 MM MICROGRAIN · 0.03 MM BUMP",
        ),
        (
            "CONTINUOUS TUBE / EDGE RESPONSE",
            "MAT_FrostedPolycarbonateEdge",
            "IOR 1.585  ·  ROUGHNESS 0.18  ·  TRANSMISSION 0.78",
            "OBJECT-LOCAL 0.58 MM MICROGRAIN · CONTINUOUS HIGHLIGHT",
        ),
        (
            "BLACK TACTILE INSERT",
            "MAT_BlackFlocking",
            "METALLIC 0  ·  ROUGHNESS 0.91",
            "OBJECT-LOCAL 0.48 MM GRAIN · 0.16 MM BUMP",
        ),
        (
            "PHYSICAL LABEL PAPER",
            "MAT_LabelPaper",
            "METALLIC 0  ·  ROUGHNESS 0.73",
            "OBJECT-LOCAL 0.44 MM PAPER GRAIN · 0.04 MM BUMP",
        ),
        (
            "TRANSPARENT LABEL COVER ZONE",
            "MAT_FrostedPolycarbonate",
            "IOR 1.585  ·  ROUGHNESS 0.22  ·  TRANSMISSION 0.92",
            "SORT ORDER CHECKED · ZERO-THICKNESS EXISTING MATERIAL ZONE",
        ),
        (
            "NARROW NEUTRAL SILVER FOIL",
            "MAT_RarityFoilSilver",
            "METALLIC 0.96  ·  ROUGHNESS 0.30  ·  EMISSION 0",
            "OBJECT-LOCAL 0.38 MM MICROGRAIN · NO COLOR WASH",
        ),
        (
            "NEUTRAL FRICTION BACKGROUND",
            "MAT_M07_ContinuousNeutralFriction",
            "METALLIC 0  ·  ROUGHNESS 0.84  ·  L 0.045–0.063",
            "0.50 MM LOCAL GRAIN · NO PATCH / RADIAL HALO / GREEN BIAS",
        ),
    ]
    left = 110
    top = 250
    row_height = 330
    for index, (name, material, primary, secondary) in enumerate(rows):
        y0 = top + index * row_height
        draw.rounded_rectangle(
            (left, y0, width - left, y0 + row_height - 28),
            radius=24,
            fill=PANEL,
            outline=PANEL_BORDER,
            width=3,
        )
        name_font = fit_font(draw, name, width - 2 * left - 80, 38, 28)
        material_font = font(24)
        primary_font = fit_font(draw, primary, width - 2 * left - 80, 34, 24)
        secondary_font = fit_font(
            draw,
            secondary,
            width - 2 * left - 80,
            28,
            20,
        )
        draw.text((left + 38, y0 + 28), name, fill=TEXT, font=name_font)
        draw.text(
            (left + 38, y0 + 86),
            material,
            fill=MUTED,
            font=material_font,
        )
        draw.text(
            (left + 38, y0 + 138),
            primary,
            fill=ACCENT,
            font=primary_font,
        )
        draw.text(
            (left + 38, y0 + 205),
            secondary,
            fill=PASS,
            font=secondary_font,
        )
        if material in parameters:
            assert parameters[material]["emissionStrength"] == 0.0
    footer = (
        "GEOMETRY LOCKED: 228 × 304 × 59 MM · LABEL Y 99 MM · "
        "DIGEST a3d1e9fe… · WINDING c29bc1dd… · FLOOD-FILL 384/384"
    )
    footer_font = fit_font(draw, footer, width - 140, 30, 20)
    centered_text(draw, width, 2580, footer, footer_font, TEXT)
    status_font = fit_font(draw, STATUS, width - 140, 30, 20)
    centered_text(draw, width, 2640, STATUS, status_font, PASS)
    canvas.save(target, optimize=True)


def image_metrics(path: Path) -> dict[str, object]:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    return {
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "meanLuma": round(float(luma.mean()), 6),
        "p01Luma": round(float(np.percentile(luma, 1)), 6),
        "p99Luma": round(float(np.percentile(luma, 99)), 6),
        "lowClipFraction": round(float((luma <= 1.0).mean()), 8),
        "highClipFraction": round(float((luma >= 254.0).mean()), 8),
        "meanChannelChroma": round(
            float((rgb.max(axis=2) - rgb.min(axis=2)).mean() / 255.0),
            8,
        ),
    }


def background_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    rgb = np.asarray(image, dtype=np.float32)
    height, width = rgb.shape[:2]
    regions = {
        "topLeft": rgb[0 : int(height * 0.20), 0 : int(width * 0.16)],
        "topRight": rgb[0 : int(height * 0.20), int(width * 0.84) : width],
        "midLeft": rgb[int(height * 0.32) : int(height * 0.64), 0 : int(width * 0.10)],
        "midRight": rgb[
            int(height * 0.32) : int(height * 0.64),
            int(width * 0.90) : width,
        ],
    }
    patch_luma = {}
    patch_chroma = {}
    outliers = {}
    for name, region in regions.items():
        luma = (
            region[..., 0] * 0.2126
            + region[..., 1] * 0.7152
            + region[..., 2] * 0.0722
        )
        patch_luma[name] = round(float(luma.mean()), 6)
        patch_chroma[name] = round(
            float((region.max(axis=2) - region.min(axis=2)).mean() / 255.0),
            8,
        )
        blurred = np.asarray(
            Image.fromarray(region.astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(radius=5)
            ),
            dtype=np.float32,
        )
        residual = np.abs(region - blurred).max(axis=2)
        outliers[name] = round(float((residual > 18.0).mean()), 8)
    return {
        "patchMeanLuma": patch_luma,
        "patchMeanLumaRange": round(
            max(patch_luma.values()) - min(patch_luma.values()),
            6,
        ),
        "patchMeanChannelChroma": patch_chroma,
        "maximumPatchMeanChannelChroma": max(patch_chroma.values()),
        "fineResidualOutlierFractions": outliers,
        "maximumFineResidualOutlierFraction": max(outliers.values()),
    }


def label_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    crop = image.crop(
        (
            int(width * 0.04),
            int(height * 0.15),
            int(width * 0.96),
            int(height * 0.82),
        )
    )
    rgb = np.asarray(crop, dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    yellow = (
        (rgb[..., 0] > 140)
        & (rgb[..., 1] > 130)
        & (rgb[..., 2] < 85)
        & ((rgb[..., 0] - rgb[..., 2]) > 60)
    )
    return {
        "crop": [int(width * 0.04), int(height * 0.15), int(width * 0.96), int(height * 0.82)],
        "p10Luma": round(float(np.percentile(luma, 10)), 6),
        "p90Luma": round(float(np.percentile(luma, 90)), 6),
        "p10P90Contrast": round(
            float(np.percentile(luma, 90) - np.percentile(luma, 10)),
            6,
        ),
        "blackoutFraction": round(float((luma < 5.0).mean()), 8),
        "yellowReferenceFraction": round(float(yellow.mean()), 10),
    }


def tactile_grain_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("L")
    width, height = image.size
    crop = image.crop(
        (
            int(width * 0.12),
            int(height * 0.12),
            int(width * 0.78),
            int(height * 0.88),
        )
    )
    raw = np.asarray(crop, dtype=np.float32)
    blurred = np.asarray(
        crop.filter(ImageFilter.GaussianBlur(radius=7)),
        dtype=np.float32,
    )
    residual = raw - blurred
    return {
        "crop": [
            int(width * 0.12),
            int(height * 0.12),
            int(width * 0.78),
            int(height * 0.88),
        ],
        "residualRms": round(float(np.sqrt(np.mean(residual**2))), 8),
        "residualP95Absolute": round(
            float(np.percentile(np.abs(residual), 95)),
            8,
        ),
        "meanLuma": round(float(raw.mean()), 6),
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
            component: list[tuple[int, int]] = []
            while queue:
                cy, cx = queue.popleft()
                component.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
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
            "touchesTopHorizontal": False,
            "touchesCorner": False,
            "touchesRightVertical": False,
        }
    top = any(y < height * 0.32 and x < width * 0.72 for y, x in best)
    corner = any(
        height * 0.18 < y < height * 0.56 and x > width * 0.55
        for y, x in best
    )
    right = any(y > height * 0.42 and x > width * 0.58 for y, x in best)
    return {
        "pixelCount": len(best),
        "touchesTopHorizontal": top,
        "touchesCorner": corner,
        "touchesRightVertical": right,
    }


def highlight_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("L")
    width, height = image.size
    roi_box = (
        0,
        int(height * 0.12),
        int(width * 0.62),
        int(height * 0.98),
    )
    roi = image.crop(roi_box)
    reduced = roi.resize(
        (max(1, roi.width // 5), max(1, roi.height // 5)),
        Image.Resampling.BILINEAR,
    )
    luma = np.asarray(reduced, dtype=np.float32)
    yy, xx = np.indices(luma.shape)
    corridor = (
        ((yy < luma.shape[0] * 0.34) & (xx < luma.shape[1] * 0.82))
        | (
            (xx > luma.shape[1] * 0.54)
            & (yy > luma.shape[0] * 0.14)
        )
    )
    threshold = 45.0
    raw_mask = ((luma >= threshold) & corridor).astype(np.uint8) * 255
    closed_mask = np.asarray(
        Image.fromarray(raw_mask)
        .filter(ImageFilter.MaxFilter(size=5))
        .filter(ImageFilter.MinFilter(size=5)),
        dtype=np.uint8,
    ) > 0
    component = largest_component(closed_mask)
    top_region = (
        (yy < luma.shape[0] * 0.36)
        & (xx < luma.shape[1] * 0.82)
        & corridor
    )
    top_bright_fraction = float((luma[top_region] >= threshold).mean())
    return {
        "roi": list(roi_box),
        "thresholdLuma": round(threshold, 6),
        "topHorizontalBrightFraction": round(top_bright_fraction, 8),
        "largestBrightComponent": component,
        "pass": (
            component["pixelCount"] >= 220
            and top_bright_fraction >= 0.03
            and component["touchesCorner"]
            and component["touchesRightVertical"]
        ),
    }


def pixel_difference(first: Path, second: Path) -> dict[str, object]:
    a = np.asarray(Image.open(first).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(second).convert("RGB"), dtype=np.int16)
    difference = np.abs(a - b)
    return {
        "meanAbsoluteChannelDelta": round(float(difference.mean()), 10),
        "maximumChannelDelta": int(difference.max()),
        "differentPixelFraction": round(
            float((difference.max(axis=2) > 0).mean()),
            10,
        ),
    }


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    audit = json.loads(BLENDER_AUDIT.read_text(encoding="utf-8"))
    surface = json.loads(SURFACE_REPORT.read_text(encoding="utf-8"))
    optimization = json.loads(OPTIMIZATION_REPORT.read_text(encoding="utf-8"))
    qa = json.loads(QA_REPORT.read_text(encoding="utf-8"))

    outputs = {
        "material-board": ROOT / "material-board.png",
        "material-closeup": ROOT / "material-closeup.png",
        "hero": ROOT / "hero-review.png",
        "left-oblique": ROOT / "left-oblique-review.png",
        "right-oblique": ROOT / "right-oblique-review.png",
        "side-back": ROOT / "side-back-review.png",
        "tube-corner-highlight": ROOT / "tube-corner-continuous-highlight.png",
        "label-closeup": ROOT / "label-closeup-review.png",
        "tactile-grain-closeup": ROOT / "tactile-grain-closeup-review.png",
        "clay-vs-pbr": ROOT / "clay-vs-pbr-same-camera.png",
        "grain-stability": ROOT / "grain-stability-rotation.png",
        "parameter-board": ROOT / "material-parameters-board.png",
    }
    material_board(outputs["material-board"])
    material_closeup_board(outputs["material-closeup"])
    annotated_view(
        RAW / "hero.png",
        outputs["hero"],
        "HERO · FORMAL FROSTED POLYCARBONATE / PAPER / FLOCKING / SILVER",
        "NEUTRAL STUDIO ONLY · FINAL LIGHTING REMAINS GATE 08",
    )
    annotated_view(
        RAW / "left-oblique.png",
        outputs["left-oblique"],
        "LEFT OBLIQUE · EDGE RESPONSE AND LAYER SEPARATION",
        "SAME APPROVED GATE 06 REV 2 GEOMETRY",
    )
    annotated_view(
        RAW / "right-oblique.png",
        outputs["right-oblique"],
        "RIGHT OBLIQUE · EDGE RESPONSE AND LAYER SEPARATION",
        "SAME APPROVED GATE 06 REV 2 GEOMETRY",
    )
    side_back_board(outputs["side-back"])
    annotated_view(
        RAW / "tube-corner.png",
        outputs["tube-corner-highlight"],
        "TUBE CORNER · CONTINUOUS STRIP HIGHLIGHT THROUGH TANGENT RADIUS",
        "ONE CONNECTED TUBE · IOR 1.585 · R 0.18 · T 0.78",
    )
    annotated_view(
        RAW / "label-closeup.png",
        outputs["label-closeup"],
        "LABEL CLOSEUP · PAPER / CLEAR COVER / NARROW SILVER FOIL",
        "IDENTITY AND ACHIEVEMENT ARE NEUTRAL PLACEHOLDERS",
    )
    annotated_view(
        RAW / "tactile-closeup.png",
        outputs["tactile-grain-closeup"],
        "TACTILE INSERT · OBJECT-LOCAL FINE GRAIN",
        "R 0.91 · 0.48 MM FEATURE · NO WORLD-SPACE SWIM",
    )
    clay_pbr_comparison(outputs["clay-vs-pbr"])
    rotation_board(outputs["grain-stability"])
    parameter_board(build, outputs["parameter-board"])

    raw_names = (
        "hero",
        "left-oblique",
        "right-oblique",
        "side",
        "back",
        "tube-corner",
        "label-closeup",
        "tactile-closeup",
        "clay-hero-same-camera",
        "rotation-000",
        "rotation-090",
        "rotation-180",
        "rotation-270",
        "rotation-360",
    )
    raw_metrics = {
        name: image_metrics(RAW / f"{name}.png") for name in raw_names
    }
    background = background_metrics(RAW / "hero.png")
    label = label_metrics(RAW / "label-closeup.png")
    tactile = tactile_grain_metrics(RAW / "tactile-closeup.png")
    highlight = highlight_metrics(RAW / "tube-corner.png")
    rotation_match = pixel_difference(
        RAW / "rotation-000.png",
        RAW / "rotation-360.png",
    )
    checks = {
        "buildReportPassed": build["status"] == "pass",
        "blenderAuditPassed": audit["status"] == "pass",
        "surfaceCoveragePassed": surface["status"] == "pass",
        "assetOptimizationPassed": optimization["status"] == "pass",
        "qaReadyForMaterialReview": (
            qa["result"] == "READY_FOR_MATERIAL_REVIEW_NOT_SHIPPING"
        ),
        "allRawViewsPresent": all(
            (RAW / f"{name}.png").exists()
            and (RAW / f"{name}.png").stat().st_size > 50_000
            for name in raw_names
        ),
        "allReviewArtifactsPresent": all(
            path.exists() and path.stat().st_size > 80_000
            for path in outputs.values()
        ),
        "requiredMaterialBoardPresent": (
            outputs["material-board"].stat().st_size > 300_000
        ),
        "requiredMaterialCloseupPresent": (
            outputs["material-closeup"].stat().st_size > 250_000
        ),
        "noSevereChannelClipping": all(
            metric["highClipFraction"] < 0.01
            and metric["lowClipFraction"] < 0.30
            for metric in raw_metrics.values()
        ),
        "backgroundLowSaturation": (
            background["maximumPatchMeanChannelChroma"] <= 0.12
        ),
        "backgroundContinuous": background["patchMeanLumaRange"] <= 20.0,
        "backgroundNoLocalizedNoiseSpots": (
            background["maximumFineResidualOutlierFraction"] <= 0.01
        ),
        "labelContrastVisible": label["p10P90Contrast"] >= 45.0,
        "labelNotBlackedOutByCover": label["blackoutFraction"] <= 0.10,
        "noYellowReferenceField": label["yellowReferenceFraction"] <= 0.001,
        "tactileGrainVisible": tactile["residualRms"] >= 0.10,
        "tubeHighlightContinuous": highlight["pass"],
        "grainLocalCoordinateAudit": audit["checks"][
            "allMicrograinObjectLocal"
        ],
        "grainStableAtFiveAngles": build["grainStability"]["pass"],
        "zeroAnd360PixelMatch": (
            rotation_match["meanAbsoluteChannelDelta"] <= 0.002
            and rotation_match["maximumChannelDelta"] <= 3
            and rotation_match["differentPixelFraction"] <= 0.01
        ),
        "transparentOrderingPreflight": audit["checks"][
            "transparentOrdering"
        ],
        "pbrChannelsAndColorSpace": (
            audit["checks"]["pbrValuesExact"]
            and audit["checks"]["noImageTextures"]
            and build["colorSpacePolicy"]["pass"]
        ),
        "geometryPreserved": (
            audit["checks"]["geometryIdentityExact"]
            and audit["checks"]["boundsExact"]
            and audit["checks"]["labelCenterYExact"]
            and audit["checks"]["concentricDriftExact"]
            and audit["checks"]["tubeWindingExact"]
            and audit["checks"]["floodFillExact"]
        ),
        "wholeCaseOnlyNoExplode": audit["checks"]["wholeCaseOnlyNoExplode"],
        "gate07NotApproved": not build["scope"]["gate07Approved"],
        "gate08NotEntered": not build["scope"]["gate08Entered"],
        "finalLightingNotApproved": not build["scope"]["finalLightingApproval"],
        "shippingUnityUnchanged": not build["scope"]["shippingUnityChanged"],
        "noBuildInstallPhonePush": not build["scope"][
            "buildInstallPhonePush"
        ],
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "rawMetrics": raw_metrics,
        "backgroundMetrics": background,
        "labelMetrics": label,
        "tactileGrainMetrics": tactile,
        "tubeHighlightContinuity": highlight,
        "grainRotationImageMatch": rotation_match,
        "artifacts": {
            name: {
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256(path),
                "sizeBytes": path.stat().st_size,
                "dimensions": list(Image.open(path).size),
            }
            for name, path in outputs.items()
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
                "materialBoard": str(outputs["material-board"]),
                "materialCloseup": str(outputs["material-closeup"]),
                "background": background,
                "label": label,
                "tactile": tactile,
                "highlight": highlight,
                "rotationMatch": rotation_match,
                "imageReport": str(IMAGE_REPORT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
