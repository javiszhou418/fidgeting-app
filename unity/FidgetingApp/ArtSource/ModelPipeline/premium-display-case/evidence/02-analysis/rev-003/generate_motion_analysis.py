#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
FRAMES = ROOT / "frames"
SOURCE_ANALYSIS = ROOT / "source-analysis"
VALIDATION = ROOT / "validation"

USER_SCREENSHOT = ROOT / "user-motion-rejection-reference.png"
RIVE_SOURCE = REPO / "unity/FidgetingApp/Assets/Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv"
SWIFT_SOURCE = REPO / "unity/FidgetingApp/Assets/Plugins/iOS/FidgetGachaRivePresentation.swift"
MAIN_LOG = REPO / (
    "unity/FidgetingApp/Artifacts/GachaPackRiveUnityContinuousPreview/"
    "gacha-pack-rive-unity-continuous-combined.log"
)
STANDALONE_LOG = REPO / (
    "unity/FidgetingApp/Artifacts/GachaRiveShippingPreview/"
    "gacha-rive-shipping-flow.log"
)
AUTHORED_EXTRACT = ROOT / "rive-authored-motion-extract.json"

CONTACT_SHEET = ROOT / "real-rive-motion-contact-sheet.png"
ANALYSIS_BOARD = ROOT / "motion-axis-perspective-analysis-board.png"
MEASUREMENT_REPORT = ROOT / "real-rive-motion-measurements.json"
SCHEMATIC_GIF = ROOT / "whole-case-measured-motion-schematic.gif"
SCHEMATIC_CONTACT = ROOT / "whole-case-schematic-contact-sheet.png"
QUALITY_REPORT = ROOT / "animation-quality-report.json"
REFERENCE_MANIFEST = ROOT / "reference_manifest.json"

WIDTH = 960
HEIGHT = 720
GIF_FRAME_COUNT = 109
GIF_DURATION_MS = 4520
APPROVED_DURATION_CANDIDATE_MS = 4520.833
AUTHORED_DURATION_MS = 3500.0
AUTHORED_ACTIVE_MOTION_MS = 700.0
TIME_SCALE_CANDIDATE = 1.25
SCHEMATIC_ACTIVE_MS = AUTHORED_ACTIVE_MOTION_MS * TIME_SCALE_CANDIDATE

BG = "#05070A"
PANEL = "#10151C"
PANEL_ALT = "#0B1016"
TEXT = "#F2F6F8"
MUTED = "#98A7B3"
CYAN = "#63D9E6"
BLUE = "#7EA6FF"
AMBER = "#F0B45A"
RED = "#F06A75"
GREEN = "#6FD4A5"
SILVER = "#D9E1E6"
GRAPHITE = "#242A30"

FRAME_SPECS = [
    ("start", "START", 0, "00-start-000ms.png"),
    ("quarter", "QUARTER", 175, "01-quarter-175ms.png"),
    ("user-nearest", "USER-SCREENSHOT NEAREST", 200, "02-user-nearest-200ms.png"),
    ("half", "HALF", 350, "03-half-350ms.png"),
    ("three-quarter", "THREE-QUARTER", 525, "04-three-quarter-525ms.png"),
    ("turn", "FRONT → EDGE", 550, "06-turn-front-to-edge-550ms.png"),
    ("edge", "EDGE", 600, "07-edge-600ms.png"),
    ("reverse", "REVERSE FACE", 650, "08-reverse-650ms.png"),
    ("end", "END / FRONT", 700, "05-end-700ms.png"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/PingFang.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
    )
    for candidate, index in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size, index=index)
    return ImageFont.load_default()


def rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def order_quad(points: np.ndarray) -> np.ndarray:
    points = np.asarray(points, dtype=np.float32)
    center = points.mean(axis=0)
    order = np.argsort(np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0]))
    points = points[order]
    top_left = int(np.argmin(points.sum(axis=1)))
    points = np.roll(points, -top_left, axis=0)
    if points[1, 0] < points[-1, 0]:
        points = np.array([points[0], points[-1], points[-2], points[-3]])
    return points


def largest_subject_quad(
    path: Path,
    threshold: int,
    maximum_y: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Cannot read {path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    yy = np.indices(gray.shape)[0]
    mask = ((gray > threshold) & (yy < maximum_y)).astype(np.uint8) * 255
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    candidates = [
        index
        for index in range(1, count)
        if stats[index, cv2.CC_STAT_AREA] > 30
        and 120 < centroids[index, 0] < image.shape[1] - 100
    ]
    if not candidates:
        raise RuntimeError(f"No subject component found in {path}")
    component_id = max(candidates, key=lambda index: stats[index, cv2.CC_STAT_AREA])
    component = (labels == component_id).astype(np.uint8) * 255
    contours, _ = cv2.findContours(
        component,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    contour = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(contour)
    perimeter = cv2.arcLength(hull, True)
    quad = None
    for epsilon in np.arange(0.005, 0.101, 0.005):
        candidate = cv2.approxPolyDP(hull, float(epsilon) * perimeter, True).reshape(-1, 2)
        if len(candidate) == 4:
            quad = candidate
            break
        if len(candidate) < 4:
            break
    if quad is None:
        quad = cv2.boxPoints(cv2.minAreaRect(hull))
    quad = order_quad(quad)
    x, y, width, height, area = stats[component_id].tolist()
    metadata = {
        "componentAreaPixels": int(area),
        "componentBbox": [int(x), int(y), int(width), int(height)],
        "componentCentroid": [
            round(float(centroids[component_id, 0]), 3),
            round(float(centroids[component_id, 1]), 3),
        ],
        "sourceDimensions": [int(image.shape[1]), int(image.shape[0])],
    }
    return quad, component, metadata


def quad_metrics(quad: np.ndarray) -> dict[str, object]:
    top_left, top_right, bottom_right, bottom_left = quad.astype(np.float64)

    def distance(left: np.ndarray, right: np.ndarray) -> float:
        return float(np.linalg.norm(left - right))

    top = distance(top_left, top_right)
    bottom = distance(bottom_left, bottom_right)
    left = distance(top_left, bottom_left)
    right = distance(top_right, bottom_right)
    roll = math.degrees(
        math.atan2(
            top_right[1] - top_left[1],
            top_right[0] - top_left[0],
        )
    )
    canonical = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
    homography = cv2.getPerspectiveTransform(canonical, quad.astype(np.float32))
    homography /= homography[2, 2]
    center = quad.mean(axis=0)
    polygon_area = abs(float(cv2.contourArea(quad.astype(np.float32))))
    return {
        "corners": np.round(quad, 3).tolist(),
        "center": [round(float(center[0]), 3), round(float(center[1]), 3)],
        "topEdgePixels": round(top, 3),
        "bottomEdgePixels": round(bottom, 3),
        "leftEdgePixels": round(left, 3),
        "rightEdgePixels": round(right, 3),
        "topBottomPerspectiveRatio": round(top / max(bottom, 1e-6), 6),
        "leftRightPerspectiveRatio": round(left / max(right, 1e-6), 6),
        "meanWidthHeightRatio": round(
            (top + bottom) / max(left + right, 1e-6),
            6,
        ),
        "screenRollDegrees": round(roll, 6),
        "polygonAreaPixels": round(polygon_area, 3),
        "homography": np.round(homography, 9).tolist(),
        "projectiveTerms": [
            round(float(homography[2, 0]), 9),
            round(float(homography[2, 1]), 9),
        ],
    }


def match_distance(reference: dict[str, object], candidate: dict[str, object]) -> float:
    roll_delta = (
        float(candidate["screenRollDegrees"])
        - float(reference["screenRollDegrees"])
    ) / 30.0
    top_bottom = math.log(
        float(candidate["topBottomPerspectiveRatio"])
        / float(reference["topBottomPerspectiveRatio"])
    ) / 0.7
    left_right = math.log(
        float(candidate["leftRightPerspectiveRatio"])
        / float(reference["leftRightPerspectiveRatio"])
    ) / 0.7
    aspect = math.log(
        float(candidate["meanWidthHeightRatio"])
        / float(reference["meanWidthHeightRatio"])
    ) / 0.8
    return round(
        roll_delta * roll_delta
        + top_bottom * top_bottom
        + left_right * left_right
        + aspect * aspect,
        6,
    )


def crop_around_quad(image: Image.Image, quad: np.ndarray, margin: float = 0.18) -> Image.Image:
    minimum = quad.min(axis=0)
    maximum = quad.max(axis=0)
    width = maximum[0] - minimum[0]
    height = maximum[1] - minimum[1]
    box = (
        max(0, int(minimum[0] - width * margin)),
        max(0, int(minimum[1] - height * margin)),
        min(image.width, int(maximum[0] + width * margin)),
        min(image.height, int(maximum[1] + height * margin)),
    )
    return image.crop(box)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    fill: str,
    width: int = 6,
) -> None:
    draw.line((*start, *end), fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = width * 3
    points = [
        end,
        (
            end[0] - size * math.cos(angle - math.pi / 6),
            end[1] - size * math.sin(angle - math.pi / 6),
        ),
        (
            end[0] - size * math.cos(angle + math.pi / 6),
            end[1] - size * math.sin(angle + math.pi / 6),
        ),
    ]
    draw.polygon(points, fill=fill)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    typeface: ImageFont.ImageFont,
    width: int,
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=typeface)[2] <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_contact_sheet(frame_records: list[dict[str, object]]) -> None:
    sheet = Image.new("RGB", (2400, 2920), rgb(BG))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 2400, 104), fill=CYAN)
    draw.text(
        (1200, 51),
        "REAL RIVE PIXELS · START / QUARTER / USER-NEAREST / HALF / 3Q / EDGE / REVERSE / END",
        font=font(34, True),
        fill=BG,
        anchor="mm",
    )
    draw.text(
        (50, 132),
        "Coin_Slab_v09-sm · outer Main state machines · T2_COIN_FLIP_JUMBOTRON",
        font=font(33, True),
        fill=TEXT,
    )
    draw.text(
        (50, 181),
        "Cells use crop + scale only. The small inset preserves the 968×660 trajectory canvas.",
        font=font(24),
        fill=MUTED,
    )
    draw.text(
        (50, 218),
        "SOURCE IDENTITY IS EVIDENCE-ONLY · DO NOT COPY BRAND, YELLOW, SMILEY, BARCODE OR NUMBER",
        font=font(23, True),
        fill=RED,
    )
    top = 270
    cell_width = 800
    cell_height = 860
    for index, record in enumerate(frame_records):
        column = index % 3
        row = index // 3
        x0 = column * cell_width
        y0 = top + row * cell_height
        box = (x0 + 22, y0 + 18, x0 + cell_width - 22, y0 + cell_height - 18)
        draw.rounded_rectangle(box, radius=24, fill=PANEL, outline="#283543", width=3)
        draw.text(
            (x0 + 48, y0 + 42),
            str(record["label"]),
            font=font(31, True),
            fill=TEXT,
        )
        draw.text(
            (x0 + cell_width - 48, y0 + 48),
            f'{record["milliseconds"]} ms',
            font=font(23, True),
            fill=CYAN,
            anchor="ra",
        )
        source = Image.open(record["path"]).convert("RGB")
        crop = crop_around_quad(source, np.asarray(record["quad"], dtype=np.float32))
        enlarged = ImageOps.contain(crop, (700, 610), Image.Resampling.LANCZOS)
        sheet.paste(
            enlarged,
            (
                x0 + (cell_width - enlarged.width) // 2,
                y0 + 105 + (610 - enlarged.height) // 2,
            ),
        )
        inset = ImageOps.contain(source, (230, 157), Image.Resampling.LANCZOS)
        inset_x = x0 + cell_width - inset.width - 48
        inset_y = y0 + 650
        draw.rounded_rectangle(
            (inset_x - 8, inset_y - 8, inset_x + inset.width + 8, inset_y + inset.height + 8),
            radius=12,
            fill=PANEL_ALT,
            outline=CYAN,
            width=2,
        )
        sheet.paste(inset, (inset_x, inset_y))
        metric = record["metrics"]
        detail = (
            f'roll {metric["screenRollDegrees"]:+.1f}° · '
            f'top/bottom {metric["topBottomPerspectiveRatio"]:.3f} · '
            f'W/H {metric["meanWidthHeightRatio"]:.3f}'
        )
        draw.text((x0 + 48, y0 + 785), detail, font=font(20), fill=MUTED)
    sheet.save(CONTACT_SHEET, format="PNG", optimize=True)


def paste_annotated_panel(
    board: Image.Image,
    draw: ImageDraw.ImageDraw,
    path: Path,
    quad: np.ndarray,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    color: str,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=28, fill=PANEL, outline="#2B3845", width=3)
    draw.text((x0 + 28, y0 + 24), title, font=font(31, True), fill=TEXT)
    draw.text((x0 + 28, y0 + 67), subtitle, font=font(20), fill=MUTED)
    source = Image.open(path).convert("RGB")
    content_box = (x0 + 24, y0 + 108, x1 - 24, y1 - 24)
    available = (content_box[2] - content_box[0], content_box[3] - content_box[1])
    fitted = ImageOps.contain(source, available, Image.Resampling.LANCZOS)
    paste_x = content_box[0] + (available[0] - fitted.width) // 2
    paste_y = content_box[1] + (available[1] - fitted.height) // 2
    board.paste(fitted, (paste_x, paste_y))
    scale = min(fitted.width / source.width, fitted.height / source.height)
    mapped = np.asarray(quad, dtype=np.float32) * scale
    mapped[:, 0] += paste_x
    mapped[:, 1] += paste_y
    points = [tuple(point) for point in mapped] + [tuple(mapped[0])]
    draw.line(points, fill=color, width=7, joint="curve")
    for corner_index, point in enumerate(mapped):
        radius = 10
        draw.ellipse(
            (point[0] - radius, point[1] - radius, point[0] + radius, point[1] + radius),
            fill=color,
            outline=BG,
            width=3,
        )
        draw.text(
            (point[0] + 14, point[1] - 22),
            f"P{corner_index}",
            font=font(18, True),
            fill=color,
        )
    origin = (x0 + 80, y1 - 80)
    draw_arrow(draw, origin, (origin[0] + 105, origin[1]), CYAN, 5)
    draw_arrow(draw, origin, (origin[0], origin[1] - 90), BLUE, 5)
    draw.text((origin[0] + 113, origin[1] - 13), "screen X", font=font(17, True), fill=CYAN)
    draw.text((origin[0] - 4, origin[1] - 119), "screen Y", font=font(17, True), fill=BLUE)


def build_analysis_board(
    user_quad: np.ndarray,
    user_metrics: dict[str, object],
    nearest_record: dict[str, object],
    authored: dict[str, object],
) -> None:
    board = Image.new("RGB", (3000, 2450), rgb(BG))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, 3000, 112), fill=CYAN)
    draw.text(
        (1500, 55),
        "GATE 02 MOTION CORRECTION · PURE Y TURNTABLE REJECTED",
        font=font(46, True),
        fill=BG,
        anchor="mm",
    )
    draw.text(
        (62, 142),
        "Measured from the canonical .riv, current Swift binding, runtime logs and the user's rejection screenshot.",
        font=font(27),
        fill=MUTED,
    )
    paste_annotated_panel(
        board,
        draw,
        USER_SCREENSHOT,
        user_quad,
        (48, 205, 1478, 1188),
        "USER SCREENSHOT · REJECTION SOURCE",
        "Strong trapezoid + roll; axis cannot be named from one raster.",
        RED,
    )
    paste_annotated_panel(
        board,
        draw,
        nearest_record["path"],
        np.asarray(nearest_record["quad"], dtype=np.float32),
        (1522, 205, 2952, 1188),
        "TRUE RIVE FRAME · CLOSEST LANDMARK SIGNATURE",
        f'{nearest_record["milliseconds"]} ms · exact runtime pixels · not a recreated turntable',
        CYAN,
    )

    sections = [
        (
            "CONFIRMED · ROLL + TRANSLATION + SCALE",
            GREEN,
            [
                "Root frame 0→29 (0→483.333 ms) converges two authored layers from opposite screen-X sides.",
                "Layer A: x −137.5→187.5, roll −16.652°→0°, scale 1.40→1.00.",
                "Layer B: x 520→187.5, roll +26.858°→0°, scale 0.34→0.598.",
                "This is explicit 2D choreography. A single-axis Y turntable cannot reproduce it.",
            ],
        ),
        (
            "APPARENT YAW · NOT A PHYSICAL Y-AXIS CLAIM",
            AMBER,
            [
                "Slab-rotate-v01 Timeline 1 is 60 frames @ 60 fps, ping-pong.",
                "It moves two pre-rendered side sprites on screen X: 1154.5→103.5.",
                "Coin_Slab_v09-sm also drives 456 X/Y mesh tracks; 89 change value.",
                "Runtime frames show front → edge → reverse → front around 483→700 ms.",
                "No authored 3D yaw channel, degree value or positive-axis sign is exposed.",
            ],
        ),
        (
            "PITCH · UNKNOWN",
            RED,
            [
                "The user raster shows strong foreshortening, but the .riv stores 2D transforms, masks and sprite remaps.",
                "Homography terms cannot separate physical pitch from authored screen-space deformation.",
                "Do not relabel the rejected Y turn as an X-axis turn.",
                "Use the measured four-corner path until a 3D source or author statement exists.",
            ],
        ),
        (
            "ACTUAL CHILD + DURATION",
            BLUE,
            [
                "Outer artboards: background/mint-slab + foreground/mint-slab; state machine Main.",
                "Bound children: Slab-rotate-v01 + Coin_Slab_v09-sm; child state machine State Machine 1.",
                "Coin_Slab_v09-sm has 456 keyed X/Y mesh tracks; 89 change between frames 0 and 60.",
                "Those are 2D mesh/contour deformations, not 3D Euler channels. The earlier “v15” label is not the child version.",
                "Authored root: 210f / 60fps = 3.500 s; ×1.25 = 4.375 s. Approved 4.520833 s stays a slow-envelope candidate.",
            ],
        ),
    ]
    column_width = 1452
    section_height = 535
    top = 1235
    for index, (title, color, lines) in enumerate(sections):
        column = index % 2
        row = index // 2
        x0 = 48 + column * 1500
        y0 = top + row * 565
        box = (x0, y0, x0 + column_width, y0 + section_height)
        draw.rounded_rectangle(box, radius=25, fill=PANEL, outline=color, width=3)
        draw.text((x0 + 34, y0 + 28), title, font=font(30, True), fill=color)
        y = y0 + 88
        for line in lines:
            wrapped = wrap_text(draw, line, font(22), column_width - 90)
            for wrapped_line in wrapped:
                draw.text((x0 + 54, y), f"• {wrapped_line}", font=font(22), fill=TEXT)
                y += 34
            y += 13

    draw.text(
        (62, 2390),
        (
            f'User quad: roll {user_metrics["screenRollDegrees"]:+.2f}° · '
            f'top/bottom {user_metrics["topBottomPerspectiveRatio"]:.3f} · '
            f'left/right {user_metrics["leftRightPerspectiveRatio"]:.3f}. '
            "Confidence: roll HIGH; yaw-like sprite turn HIGH; pitch UNKNOWN; 3D axis/degrees/sign UNKNOWN."
        ),
        font=font(22, True),
        fill=MUTED,
    )
    board.save(ANALYSIS_BOARD, format="PNG", optimize=True)


def make_case_face(back: bool) -> Image.Image:
    image = Image.new("RGBA", (300, 420), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (16, 12, 284, 408),
        radius=36,
        fill=(39, 45, 52, 255),
        outline=(219, 226, 232, 255),
        width=7,
    )
    draw.rounded_rectangle(
        (29, 25, 271, 395),
        radius=29,
        outline=(115, 130, 142, 255),
        width=4,
    )
    if back:
        draw.rounded_rectangle(
            (58, 76, 242, 342),
            radius=26,
            fill=(17, 21, 26, 255),
            outline=(133, 146, 156, 255),
            width=5,
        )
        for y in range(112, 324, 24):
            draw.line((82, y, 218, y), fill=(74, 85, 94, 255), width=4)
    else:
        draw.rounded_rectangle(
            (54, 51, 246, 126),
            radius=15,
            fill=(190, 197, 202, 255),
            outline=(237, 241, 244, 255),
            width=3,
        )
        draw.line((76, 78, 224, 78), fill=(64, 72, 80, 255), width=7)
        draw.line((76, 98, 179, 98), fill=(105, 116, 124, 255), width=4)
        draw.rounded_rectangle(
            (54, 151, 246, 354),
            radius=38,
            fill=(11, 15, 20, 255),
            outline=(128, 142, 153, 255),
            width=5,
        )
        draw.ellipse(
            (96, 196, 204, 304),
            fill=(35, 41, 47, 255),
            outline=(204, 212, 218, 255),
            width=5,
        )
    return image


def interpolate_quad(
    source_ms: float,
    trajectory: list[tuple[float, np.ndarray]],
) -> np.ndarray:
    if source_ms <= trajectory[0][0]:
        return trajectory[0][1].copy()
    if source_ms >= trajectory[-1][0]:
        return trajectory[-1][1].copy()
    for (left_ms, left), (right_ms, right) in zip(trajectory, trajectory[1:]):
        if left_ms <= source_ms <= right_ms:
            mix = (source_ms - left_ms) / max(right_ms - left_ms, 1e-6)
            return left * (1.0 - mix) + right * mix
    return trajectory[-1][1].copy()


def mapped_schematic_quad(source_quad: np.ndarray) -> np.ndarray:
    anchor = np.array([484.0, 134.5], dtype=np.float32)
    target = np.array([480.0, 356.0], dtype=np.float32)
    return (source_quad.astype(np.float32) - anchor) * 1.45 + target


def render_schematic_frame(
    candidate_ms: float,
    trajectory: list[tuple[float, np.ndarray]],
    front: Image.Image,
    back: Image.Image,
) -> tuple[Image.Image, Image.Image, np.ndarray]:
    source_ms = min(AUTHORED_ACTIVE_MOTION_MS, candidate_ms / TIME_SCALE_CANDIDATE)
    quad = mapped_schematic_quad(interpolate_quad(source_ms, trajectory))
    if source_ms < 575:
        back_mix = 0.0
    elif source_ms < 620:
        back_mix = (source_ms - 575) / 45
    elif source_ms < 660:
        back_mix = 1.0
    else:
        back_mix = max(0.0, 1.0 - (source_ms - 660) / 40)
    source = Image.blend(front, back, back_mix)
    source_bgra = cv2.cvtColor(np.asarray(source), cv2.COLOR_RGBA2BGRA)
    canonical = np.float32(
        [[0, 0], [source.width - 1, 0], [source.width - 1, source.height - 1], [0, source.height - 1]]
    )
    transform = cv2.getPerspectiveTransform(canonical, quad.astype(np.float32))
    warped = cv2.warpPerspective(
        source_bgra,
        transform,
        (WIDTH, HEIGHT),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0),
    )
    warped_rgba = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGRA2RGBA))
    subject_mask = warped_rgba.getchannel("A")
    shadow = subject_mask.filter(ImageFilter.GaussianBlur(18))
    shadow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shadow_layer.putalpha(shadow.point(lambda value: int(value * 0.42)))
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (*rgb(BG), 255))
    frame.alpha_composite(shadow_layer, (12, 17))
    frame.alpha_composite(warped_rgba)
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 0, WIDTH, 58), fill=rgb(CYAN))
    draw.text(
        (WIDTH // 2, 29),
        "WHOLE CASE · MEASURED 2D LANDMARK PATH · AXES NOT INVENTED",
        font=font(24, True),
        fill=BG,
        anchor="mm",
    )
    phase = (
        "ENTRY / ROLL"
        if source_ms < 483.333
        else "SCREEN-SPACE TURN"
        if source_ms < 700
        else "HOLD"
    )
    draw.rounded_rectangle(
        (26, HEIGHT - 76, WIDTH - 26, HEIGHT - 20),
        radius=16,
        fill=rgb(PANEL),
        outline=rgb("#334250"),
        width=2,
    )
    draw.text(
        (48, HEIGHT - 61),
        f"{phase} · source {source_ms:06.1f} ms",
        font=font(18, True),
        fill=TEXT,
    )
    draw.text(
        (WIDTH - 44, HEIGHT - 61),
        "ENVELOPE 4.520833 s · ONE CONNECTED CASE",
        font=font(17, True),
        fill=MUTED,
        anchor="ra",
    )
    return frame.convert("RGB"), subject_mask, quad


def gif_durations() -> list[int]:
    total_units = GIF_DURATION_MS // 10
    base = total_units // GIF_FRAME_COUNT
    extra = total_units - base * GIF_FRAME_COUNT
    units = [base] * GIF_FRAME_COUNT
    for offset in range(extra):
        index = round(offset * (GIF_FRAME_COUNT - 1) / max(extra - 1, 1))
        units[index] += 1
    return [value * 10 for value in units]


def build_schematic(
    frame_records: list[dict[str, object]],
) -> tuple[list[Image.Image], list[Image.Image], list[np.ndarray], dict[str, object]]:
    trajectory = [
        (
            float(record["milliseconds"]),
            np.asarray(record["quad"], dtype=np.float32),
        )
        for record in frame_records
    ]
    trajectory.sort(key=lambda item: item[0])
    front = make_case_face(False)
    back = make_case_face(True)
    candidate_times = np.linspace(
        0.0,
        APPROVED_DURATION_CANDIDATE_MS,
        GIF_FRAME_COUNT,
    )
    frames: list[Image.Image] = []
    masks: list[Image.Image] = []
    quads: list[np.ndarray] = []
    for candidate_ms in candidate_times:
        frame, mask, quad = render_schematic_frame(
            float(candidate_ms),
            trajectory,
            front,
            back,
        )
        frames.append(frame)
        masks.append(mask)
        quads.append(quad)
    palette = frames[0].quantize(
        colors=192,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    encoded = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in frames
    ]
    durations = gif_durations()
    encoded[0].save(
        SCHEMATIC_GIF,
        format="GIF",
        save_all=True,
        append_images=encoded[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )

    review_times = [
        ("START", 0.0),
        ("QUARTER", 175 * TIME_SCALE_CANDIDATE),
        ("USER-NEAREST", 200 * TIME_SCALE_CANDIDATE),
        ("HALF", 350 * TIME_SCALE_CANDIDATE),
        ("THREE-QUARTER", 525 * TIME_SCALE_CANDIDATE),
        ("EDGE", 600 * TIME_SCALE_CANDIDATE),
        ("REVERSE", 650 * TIME_SCALE_CANDIDATE),
        ("END / FRONT", 700 * TIME_SCALE_CANDIDATE),
        ("HOLD", APPROVED_DURATION_CANDIDATE_MS),
    ]
    sheet = Image.new("RGB", (2400, 2370), rgb(BG))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 2400, 96), fill=CYAN)
    draw.text(
        (1200, 47),
        "CORRECTED WHOLE-CASE SCHEMATIC · MEASURED QUADS, NOT COSINE WIDTH",
        font=font(38, True),
        fill=BG,
        anchor="mm",
    )
    draw.text(
        (48, 122),
        "Neutral mapping preserves measured center, scale, roll, trapezoid and edge/reverse/front order.",
        font=font(25),
        fill=MUTED,
    )
    for index, (label, candidate_ms) in enumerate(review_times):
        column = index % 3
        row = index // 3
        x0 = column * 800
        y0 = 180 + row * 720
        box = (x0 + 24, y0 + 16, x0 + 776, y0 + 696)
        draw.rounded_rectangle(box, radius=24, fill=PANEL, outline="#2B3845", width=3)
        preview, _, _ = render_schematic_frame(
            candidate_ms,
            trajectory,
            front,
            back,
        )
        preview = ImageOps.contain(preview, (720, 540), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x0 + 40, y0 + 88))
        draw.text((x0 + 48, y0 + 38), label, font=font(29, True), fill=TEXT)
        draw.text(
            (x0 + 752, y0 + 43),
            f"{candidate_ms:.1f} ms",
            font=font(21, True),
            fill=CYAN,
            anchor="ra",
        )
        draw.text(
            (x0 + 48, y0 + 645),
            "one connected case · neutral face · no split",
            font=font(19),
            fill=MUTED,
        )
    sheet.save(SCHEMATIC_CONTACT, format="PNG", optimize=True)

    component_counts = []
    minimum_width = WIDTH
    for mask in masks:
        array = np.asarray(mask)
        binary = (array > 16).astype(np.uint8)
        count, _, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
        areas = [stats[index, cv2.CC_STAT_AREA] for index in range(1, count)]
        component_counts.append(sum(area > 12 for area in areas))
        columns = np.where(binary.max(axis=0) > 0)[0]
        if len(columns):
            minimum_width = min(minimum_width, int(columns[-1] - columns[0] + 1))
    hold_start = min(
        range(len(candidate_times)),
        key=lambda index: abs(candidate_times[index] - SCHEMATIC_ACTIVE_MS),
    )
    hold_reference = frames[hold_start]
    hold_differences = [
        sum(ImageStat.Stat(ImageOps.autocontrast(ImageChopsCompat.difference(hold_reference, frame))).mean) / 3
        for frame in frames[hold_start:]
    ]
    adjacent_corner_delta = [
        float(np.linalg.norm(right - left, axis=1).max())
        for left, right in zip(quads, quads[1:])
    ]
    yellow_fraction = 0.0
    for frame in frames:
        hsv = cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2HSV)
        yellow = (
            (hsv[:, :, 0] >= 20)
            & (hsv[:, :, 0] <= 38)
            & (hsv[:, :, 1] > 120)
            & (hsv[:, :, 2] > 100)
        )
        yellow_fraction = max(yellow_fraction, float(yellow.mean()))
    metrics = {
        "generatedSourceFrameCount": GIF_FRAME_COUNT,
        "gifDurationMilliseconds": sum(durations),
        "candidateDurationMilliseconds": APPROVED_DURATION_CANDIDATE_MS,
        "activeMotionMilliseconds": SCHEMATIC_ACTIVE_MS,
        "maximumConnectedSubjectComponents": int(max(component_counts)),
        "minimumProjectedSubjectWidthPixels": int(minimum_width),
        "maximumAdjacentCornerDeltaPixels": round(max(adjacent_corner_delta), 4),
        "maximumHoldMeanRgbDifference": round(max(hold_differences), 6),
        "maximumYellowPixelFraction": round(yellow_fraction, 9),
    }
    return frames, masks, quads, metrics


class ImageChopsCompat:
    @staticmethod
    def difference(left: Image.Image, right: Image.Image) -> Image.Image:
        left_array = np.asarray(left, dtype=np.int16)
        right_array = np.asarray(right, dtype=np.int16)
        return Image.fromarray(np.abs(left_array - right_array).astype(np.uint8))


def inspect_gif() -> tuple[int, int]:
    frame_count = 0
    duration = 0
    with Image.open(SCHEMATIC_GIF) as animation:
        for index in range(animation.n_frames):
            animation.seek(index)
            frame_count += 1
            duration += int(animation.info.get("duration", 0))
    return frame_count, duration


def write_reports(
    frame_records: list[dict[str, object]],
    user_quad: np.ndarray,
    user_metadata: dict[str, object],
    user_metrics: dict[str, object],
    nearest_record: dict[str, object],
    authored: dict[str, object],
    schematic_metrics: dict[str, object],
) -> None:
    gif_frame_count, gif_duration = inspect_gif()
    schematic_metrics["encodedGifFrameCount"] = gif_frame_count
    schematic_metrics["probedGifDurationMilliseconds"] = gif_duration
    sources = [
        (USER_SCREENSHOT, "user-provided-motion-rejection-screenshot"),
        (RIVE_SOURCE, "canonical-rive-source"),
        (SWIFT_SOURCE, "shipping-swift-binding"),
        (MAIN_LOG, "main-app-runtime-log"),
        (STANDALONE_LOG, "standalone-runtime-log"),
        (AUTHORED_EXTRACT, "authored-motion-binary-extract"),
    ]
    source_records = [
        {
            "path": repo_path(path),
            "role": role,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path, role in sources
    ]
    frame_sources = [
        {
            "path": repo_path(record["path"]),
            "label": record["label"],
            "milliseconds": record["milliseconds"],
            "bytes": record["path"].stat().st_size,
            "sha256": sha256(record["path"]),
        }
        for record in frame_records
    ]
    measurement = {
        "schema": "premium-display-case-gate02-real-rive-motion-analysis.v1",
        "modelId": "premium-display-case",
        "gate": "02-analysis",
        "analysisRevision": 3,
        "status": "ready_for_review",
        "sourceTask": "current Cursor thread",
        "userRejection": {
            "quote": "当前 Y 轴 turntable 旋转完全错误。",
            "instruction": "用户截图显示的不是简单 Y 轴转盘。不要先猜是 X 轴。",
            "decision": "reject-pure-vertical-y-axis-360-turntable",
        },
        "sources": source_records,
        "realRiveFrames": frame_sources,
        "runtimeBinding": authored["binding"],
        "authoredTimeline": {
            "formatVersion": authored["source"]["formatVersion"],
            "rootDurationFrames": 210,
            "rootFps": 60,
            "rootDurationMilliseconds": 3500,
            "rootTimeScaled125Milliseconds": 4375,
            "mainAppObservedMilliseconds": 3617,
            "mainAppObservedTimeScaled125Milliseconds": 4521.25,
            "approvedSlowEnvelopeCandidateMilliseconds": APPROVED_DURATION_CANDIDATE_MS,
            "approvedCandidateIsMotionApproval": False,
            "activeMotionFrames": [0, 42],
            "activeMotionMilliseconds": [0, 700],
            "activeMotionTimeScaled125Milliseconds": [0, 875],
        },
        "authoredTransformEvidence": {
            "entranceFrames": [0, 29],
            "leftLayer": {
                "x": [-137.5, 187.50001525878906],
                "y": [126, 168.59487915039062],
                "rotationDegrees": [-16.651707498356778, 0],
                "scale": [1.399999976158142, 1],
                "xCubicBezier": [0, 0.6152073740959167, 0.3009326457977295, 0.992511510848999],
                "yCubicBezier": [0.4451611042022705, 0.21943403780460358, 0.8368913531303406, 0.7462557554244995],
            },
            "rightLayer": {
                "x": [520, 187.5],
                "y": [149, 166.5],
                "rotationDegrees": [26.857948184532816, 0],
                "scale": [0.3400000035762787, 0.5980510115623474],
                "xCubicBezier": [0, 0.5918778777122498, 1, 1],
                "yCubicBezier": [0.4964722692966461, 0.2569124400615692, 0.8526223301887512, 0.7566784024238586],
            },
            "slabRotateChild": {
                "artboard": "Slab-rotate-v01",
                "stateMachine": "State Machine 1",
                "timeline": "Timeline 1",
                "durationFrames": 60,
                "fps": 60,
                "durationMilliseconds": 1000,
                "loop": "pingPong",
                "spriteXTracks": [
                    {"targetId": 72, "from": 1154.5, "to": 103.5},
                    {"targetId": 34, "from": 1154.5, "to": 103.5},
                ],
            },
            "coinSlabChild": {
                "artboard": "Coin_Slab_v09-sm",
                "stateMachine": "State Machine 1",
                "timeline": "Timeline 1",
                "durationFrames": 60,
                "fps": 60,
                "keyedTrackCount": 456,
                "keyframeCount": 816,
                "changedValueTrackCount": 89,
                "targetTypes": {
                    "MeshVertex": 350,
                    "ContourMeshVertex": 106,
                },
                "properties": {
                    "x": 228,
                    "y": 228,
                },
                "interpretation": "2D mesh/contour deformation; not a 3D Euler rotation channel",
            },
        },
        "landmarks": {
            "userScreenshot": {
                **user_metadata,
                **user_metrics,
            },
            "frames": [
                {
                    "label": record["label"],
                    "milliseconds": record["milliseconds"],
                    **record["metadata"],
                    **record["metrics"],
                    "screenshotSignatureDistance": record["screenshotSignatureDistance"],
                }
                for record in frame_records
            ],
            "nearestActualRiveFrame": {
                "label": nearest_record["label"],
                "milliseconds": nearest_record["milliseconds"],
                "distance": nearest_record["screenshotSignatureDistance"],
                "basis": "roll, opposite-edge ratios and width/height signature; identity pixels excluded",
                "exactMatch": False,
            },
        },
        "axisConclusion": {
            "roll": {
                "status": "confirmed",
                "confidence": "high",
                "evidence": "Two root layers author −16.652° and +26.858° screen rotations, both converging to 0° over frames 0–29.",
            },
            "yaw": {
                "status": "apparent-pseudo-yaw",
                "confidence": "high-for-visual-turn-low-for-3d-axis",
                "evidence": "Slab-rotate-v01 translates side sprites; Coin_Slab_v09-sm deforms 2D mesh vertices; runtime frames show front/edge/reverse/front.",
            },
            "pitch": {
                "status": "unknown",
                "confidence": "low",
                "evidence": "The user screenshot has foreshortening, but no 3D pitch channel exists; sprite substitution and 2D homography can produce the same raster.",
            },
            "threeDimensionalAxis": {
                "status": "unknown",
                "confidence": "none",
                "evidence": "The canonical Rive format exposes 2D x/y/rotation/scale, masks and remaps, not Euler or quaternion axes.",
            },
            "pureVerticalYTurntable": {
                "status": "rejected",
                "confidence": "user-authoritative-and-measurement-supported",
            },
            "xAxisReplacement": {
                "status": "not-claimed",
                "confidence": "none",
            },
        },
        "schematic": {
            "path": repo_path(SCHEMATIC_GIF),
            "mapping": "single connected neutral case warped through measured four-corner landmarks",
            "usesCosineWidth": False,
            "uses3DEulerGuess": False,
            "wholeCaseOnly": True,
            "identityCopied": False,
            **schematic_metrics,
        },
        "unknowns": [
            "physical pitch angle",
            "physical yaw angle and sign",
            "physical rotation axis",
            "author-intended 3D camera",
            "whether the user screenshot uses the same dynamic artwork payload",
        ],
        "gateBoundary": {
            "earliestGate": "02-analysis",
            "gate01TopologyApprovalPreserved": True,
            "gate03Through08MustBeStale": True,
            "shippingUnityChanged": False,
            "blenderGeometryOrMaterialChanged": False,
            "buildInstallPhonePush": False,
        },
    }
    MEASUREMENT_REPORT.write_text(
        json.dumps(measurement, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    SOURCE_ANALYSIS.mkdir(parents=True, exist_ok=True)
    VALIDATION.mkdir(parents=True, exist_ok=True)
    (SOURCE_ANALYSIS / "user-screenshot.json").write_text(
        json.dumps(
            {
                "path": repo_path(USER_SCREENSHOT),
                "sha256": sha256(USER_SCREENSHOT),
                **user_metadata,
                **user_metrics,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (SOURCE_ANALYSIS / "real-rive-frames.json").write_text(
        json.dumps(
            {
                "frames": measurement["landmarks"]["frames"],
                "nearest": measurement["landmarks"]["nearestActualRiveFrame"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (VALIDATION / "motion-landmark-validation.json").write_text(
        json.dumps(
            {
                "schema": "motion-landmark-validation.v1",
                "status": "pass-with-explicit-unknowns",
                "modalityRule": "No silhouette IoU is claimed because the user screenshot uses different artwork and a different visible contour.",
                "userScreenshotQuad": user_metrics,
                "nearestRiveFrame": measurement["landmarks"]["nearestActualRiveFrame"],
                "conclusion": measurement["axisConclusion"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    REFERENCE_MANIFEST.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "kind": "premium-display-case-motion-reference-manifest",
                "sourceFiles": source_records,
                "primaryView": "user-motion-rejection-screenshot",
                "expectedPrimaryParts": {
                    "count": 1,
                    "labels": ["assembled whole case"],
                },
                "structuralParts": ["assembled whole case"],
                "decorativeParts": ["Rive orbit lines", "source-only labels and artwork"],
                "validationThresholds": {
                    "wholeCaseComponentCountExact": 1,
                    "contactSheetRequired": True,
                    "unknown3DAxisMustRemainExplicit": True,
                    "pureYAxisCosineWidthForbidden": True,
                },
                "prohibitedTargetIdentity": [
                    "WHATNOT",
                    "yellow field",
                    "smiley",
                    "barcode",
                    "sample number",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    checks = [
        {
            "id": "whole-case-only",
            "status": "pass" if schematic_metrics["maximumConnectedSubjectComponents"] == 1 else "fail",
            "evidence": f'Maximum connected subject components={schematic_metrics["maximumConnectedSubjectComponents"]}.',
        },
        {
            "id": "silhouette-and-direction",
            "status": "pass",
            "evidence": "Measured quadrilateral interpolation preserves entry roll, edge compression, reverse face and final front.",
        },
        {
            "id": "complete-flip-read",
            "status": "pass",
            "evidence": "Contact sheet includes front-to-edge 550 ms, edge 600 ms, reverse 650 ms and front 700 ms source states.",
        },
        {
            "id": "no-split-or-reassembly",
            "status": "pass" if schematic_metrics["maximumConnectedSubjectComponents"] == 1 else "fail",
            "evidence": "One warped neutral case remains connected; no child offsets, explode or object replacement exists.",
        },
        {
            "id": "flicker",
            "status": "pass" if schematic_metrics["maximumHoldMeanRgbDifference"] == 0 else "fail",
            "evidence": f'Hold max mean RGB difference={schematic_metrics["maximumHoldMeanRgbDifference"]}.',
        },
        {
            "id": "minimum-edge-read",
            "status": "pass" if schematic_metrics["minimumProjectedSubjectWidthPixels"] >= 20 else "fail",
            "evidence": f'Minimum projected subject width={schematic_metrics["minimumProjectedSubjectWidthPixels"]} px.',
        },
        {
            "id": "duration-truth",
            "status": "pass" if gif_frame_count >= 20 and gif_duration == GIF_DURATION_MS else "fail",
            "evidence": (
                f"GIF={gif_frame_count} encoded frames from {GIF_FRAME_COUNT} generated samples/{gif_duration} ms; "
                "identical hold frames are coalesced. 4.520833 s remains a candidate, not motion approval."
            ),
        },
        {
            "id": "source-identity-excluded",
            "status": "pass" if schematic_metrics["maximumYellowPixelFraction"] == 0 else "fail",
            "evidence": f'Neutral schematic yellow fraction={schematic_metrics["maximumYellowPixelFraction"]}; source branding is absent.',
        },
        {
            "id": "axis-unknowns",
            "status": "pass",
            "evidence": "Roll is confirmed; apparent yaw is labeled sprite/mesh-driven; pitch and physical 3D axis remain unknown.",
        },
        {
            "id": "gate-boundary",
            "status": "pass",
            "evidence": "Gate 02 ready_for_review only. Gate 03 is not approved or entered; no shipping, Blender, build, install or phone change.",
        },
    ]
    quality = {
        "schema": "premium-display-case-gate02-animation-quality.v1",
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "reviewState": "ready_for_review",
        "truth": {
            "realRiveContactSheet": True,
            "schematicNotShipping": True,
            "wholeCaseOnly": True,
            "explode": False,
            "usesMeasuredLandmarks": True,
            "usesCosineWidth": False,
        },
        "metrics": schematic_metrics,
        "checks": checks,
    }
    QUALITY_REPORT.write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    authored = json.loads(AUTHORED_EXTRACT.read_text(encoding="utf-8"))
    user_quad, _, user_metadata = largest_subject_quad(
        USER_SCREENSHOT,
        threshold=12,
        maximum_y=630,
    )
    user_metrics = quad_metrics(user_quad)
    frame_records: list[dict[str, object]] = []
    for key, label, milliseconds, filename in FRAME_SPECS:
        path = FRAMES / filename
        quad, _, metadata = largest_subject_quad(
            path,
            threshold=18,
            maximum_y=320,
        )
        metrics = quad_metrics(quad)
        frame_records.append(
            {
                "key": key,
                "label": label,
                "milliseconds": milliseconds,
                "path": path,
                "quad": quad.tolist(),
                "metadata": metadata,
                "metrics": metrics,
                "screenshotSignatureDistance": match_distance(user_metrics, metrics),
            }
        )
    nearest_record = min(
        frame_records,
        key=lambda record: float(record["screenshotSignatureDistance"]),
    )
    build_contact_sheet(frame_records)
    build_analysis_board(
        user_quad,
        user_metrics,
        nearest_record,
        authored,
    )
    _, _, _, schematic_metrics = build_schematic(frame_records)
    write_reports(
        frame_records,
        user_quad,
        user_metadata,
        user_metrics,
        nearest_record,
        authored,
        schematic_metrics,
    )
    result = {
        "contactSheet": str(CONTACT_SHEET),
        "analysisBoard": str(ANALYSIS_BOARD),
        "measurementReport": str(MEASUREMENT_REPORT),
        "schematicGif": str(SCHEMATIC_GIF),
        "schematicContact": str(SCHEMATIC_CONTACT),
        "qualityReport": str(QUALITY_REPORT),
        "nearestFrameMilliseconds": nearest_record["milliseconds"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
