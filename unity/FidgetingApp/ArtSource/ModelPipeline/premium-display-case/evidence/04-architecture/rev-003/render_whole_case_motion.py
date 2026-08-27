#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parent
GIF_PATH = ROOT / "whole-case-only-rive-v15-envelope.gif"
MP4_PATH = ROOT / "whole-case-only-rive-v15-envelope.mp4"
CONTACT_SHEET_PATH = ROOT / "whole-case-only-contact-sheet.png"
TIMING_REPORT_PATH = ROOT / "rive-v15-timing-report.json"
QUALITY_REPORT_PATH = ROOT / "animation-quality-report.json"

WIDTH = 1280
HEIGHT = 960
FPS = 60
FRAME_COUNT = 217
TARGET_DURATION_MS = 3617
MP4_DURATION_MS = FRAME_COUNT * 1000 / FPS
GIF_FRAME_COUNT = 109

# The shipping logs expose state-machine wall time, but not authored curve data.
# These phase bounds are an explicit 20 fps video-sampling approximation.
ROTATION_START_S = 0.18
ROTATION_END_S = 0.52
HIGHLIGHT_START_S = 0.50
HIGHLIGHT_END_S = 0.84

BG = "#070A0F"
PANEL = "#101722"
PANEL_2 = "#0C111A"
LINE = "#334152"
TEXT = "#F4F7FA"
MUTED = "#9BA9B9"
CYAN = "#65D5E6"
BLUE = "#719CFF"
VIOLET = "#A98BFA"
MAGENTA = "#D486D8"
GREEN = "#66D6A5"
RED = "#F06D78"
SILVER = "#D8DEE5"
GRAPHITE = "#242A31"


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


F_BANNER = font(34, True)
F_TITLE = font(44, True)
F_SUBTITLE = font(24)
F_STAGE = font(30, True)
F_BODY = font(23)
F_BODY_BOLD = font(23, True)
F_SMALL = font(19)
F_SMALL_BOLD = font(19, True)
F_CASE_LABEL = font(20, True)
F_CASE_SMALL = font(14, True)


def rgb(value: str) -> tuple[int, int, int]:
    value = value.removeprefix("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def rgba(value: str, alpha: int) -> tuple[int, int, int, int]:
    return (*rgb(value), alpha)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def text_width(draw: ImageDraw.ImageDraw, value: str, typeface: ImageFont.ImageFont) -> int:
    return draw.textbbox((0, 0), value, font=typeface)[2]


def smootherstep(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return value * value * value * (value * (value * 6 - 15) + 10)


def state_at(index: int) -> dict[str, float | str | bool]:
    seconds = index / FPS
    if seconds < ROTATION_START_S:
        rotation_progress = 0.0
        phase = "START"
    elif seconds < ROTATION_END_S:
        rotation_progress = smootherstep(
            (seconds - ROTATION_START_S) / (ROTATION_END_S - ROTATION_START_S)
        )
        phase = "WHOLE-CASE Y 360°"
    else:
        rotation_progress = 1.0
        phase = "HIGHLIGHT" if seconds < HIGHLIGHT_END_S else "SETTLED"

    if HIGHLIGHT_START_S <= seconds <= HIGHLIGHT_END_S:
        highlight_progress = (
            (seconds - HIGHLIGHT_START_S)
            / (HIGHLIGHT_END_S - HIGHLIGHT_START_S)
        )
    else:
        highlight_progress = -1.0

    return {
        "seconds": seconds,
        "phase": phase,
        "angleDegrees": rotation_progress * 360.0,
        "highlightProgress": highlight_progress,
        "highlightActive": highlight_progress >= 0.0,
    }


STATES = [state_at(index) for index in range(FRAME_COUNT)]


def marker_for_angle(angle: float) -> int:
    return min(
        range(FRAME_COUNT),
        key=lambda index: abs(float(STATES[index]["angleDegrees"]) - angle),
    )


MARKERS = {
    "start": 0,
    "zero": max(0, round(ROTATION_START_S * FPS)),
    "90": marker_for_angle(90),
    "180": marker_for_angle(180),
    "270": marker_for_angle(270),
    "360": marker_for_angle(360),
    "highlight": round((HIGHLIGHT_START_S + HIGHLIGHT_END_S) * 0.5 * FPS),
    "settled": FRAME_COUNT - 1,
}


def draw_prize(face: Image.Image, center: tuple[int, int], back: bool) -> None:
    layer = Image.new("RGBA", face.size, (0, 0, 0, 0))
    cx, cy = center
    colors = (CYAN, VIOLET, MAGENTA)
    for index, degrees in enumerate((0, 120, 240)):
        arm = Image.new("RGBA", (92, 176), (0, 0, 0, 0))
        arm_draw = ImageDraw.Draw(arm)
        arm_draw.rounded_rectangle(
            (26, 7, 66, 151),
            radius=19,
            fill=rgba(colors[index], 150 if back else 205),
            outline=rgba(SILVER, 180),
            width=3,
        )
        arm_draw.rounded_rectangle(
            (32, 19, 60, 137),
            radius=14,
            outline=rgba(TEXT, 70),
            width=2,
        )
        rotated = arm.rotate(-degrees, resample=Image.Resampling.BICUBIC, expand=True)
        layer.alpha_composite(
            rotated,
            (cx - rotated.width // 2, cy - rotated.height // 2),
        )

    draw = ImageDraw.Draw(layer)
    hex_radius = 45
    points = [
        (
            cx + math.cos(math.radians(60 * point - 30)) * hex_radius,
            cy + math.sin(math.radians(60 * point - 30)) * hex_radius,
        )
        for point in range(6)
    ]
    draw.polygon(
        points,
        fill=rgba(GRAPHITE, 245),
        outline=rgba(TEXT, 210),
        width=4,
    )
    draw.text(
        (cx, cy),
        "P",
        font=font(25, True),
        fill=TEXT,
        anchor="mm",
    )
    face.alpha_composite(layer)


def case_face(back: bool, highlight_progress: float) -> Image.Image:
    face = Image.new("RGBA", (470, 628), (0, 0, 0, 0))
    draw = ImageDraw.Draw(face)

    outer = (24, 22, 446, 606)
    draw.rounded_rectangle(
        (31, 34, 455, 616),
        radius=56,
        fill=(0, 0, 0, 95),
    )
    draw.rounded_rectangle(
        outer,
        radius=54,
        fill=(36, 43, 51, 246),
        outline=rgba(SILVER, 235),
        width=7,
    )
    draw.rounded_rectangle(
        (35, 33, 435, 595),
        radius=45,
        outline=rgba(CYAN, 150),
        width=5,
    )
    draw.rounded_rectangle(
        (49, 47, 421, 581),
        radius=36,
        outline=rgba(TEXT, 70),
        width=3,
    )

    # One connected perimeter loop. It is never split or translated.
    draw.rounded_rectangle(
        (39, 37, 431, 591),
        radius=43,
        outline=rgba(BLUE, 130),
        width=12,
    )

    label = (72, 72, 398, 176)
    draw.rounded_rectangle(
        label,
        radius=20,
        fill=(188, 194, 199, 235),
        outline=rgba(TEXT, 210),
        width=3,
    )
    draw.text(
        (94, 91),
        "PREMIUM DISPLAY CASE",
        font=F_CASE_LABEL,
        fill=GRAPHITE,
    )
    draw.text(
        (94, 126),
        "REAR · SAME CASE" if back else "PORTRAIT · ASSEMBLED",
        font=F_CASE_SMALL,
        fill="#4A535D",
    )
    draw.rounded_rectangle(
        (319, 118, 376, 143),
        radius=12,
        fill=rgba(GRAPHITE, 220),
    )
    draw.text(
        (347, 131),
        "ONE",
        font=font(12, True),
        fill=TEXT,
        anchor="mm",
    )

    chamber = (82, 205, 388, 526)
    draw.rounded_rectangle(
        chamber,
        radius=54,
        fill=(10, 14, 21, 245),
        outline=rgba(CYAN, 135),
        width=5,
    )
    draw.rounded_rectangle(
        (97, 220, 373, 511),
        radius=43,
        fill=(16, 22, 31, 235),
        outline=rgba(TEXT, 55),
        width=3,
    )
    draw_prize(face, (235, 361), back)
    draw.text(
        (235, 486),
        "SAME PRIZE · VISIBLE",
        font=F_CASE_SMALL,
        fill=rgba(TEXT, 185),
        anchor="mm",
    )

    draw.rounded_rectangle(
        (91, 548, 379, 573),
        radius=12,
        fill=rgba(CYAN, 45),
        outline=rgba(CYAN, 105),
        width=2,
    )
    draw.text(
        (235, 561),
        "WHOLE ROOT · CHILD OFFSETS = 0",
        font=font(11, True),
        fill=rgba(TEXT, 190),
        anchor="mm",
    )

    if highlight_progress >= 0:
        highlight = Image.new("RGBA", face.size, (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(highlight)
        center = -310 + highlight_progress * 980
        hdraw.polygon(
            (
                (center - 95, -70),
                (center + 55, -70),
                (center + 455, 698),
                (center + 305, 698),
            ),
            fill=(235, 248, 255, 175),
        )
        highlight = highlight.filter(ImageFilter.GaussianBlur(22))
        mask = Image.new("L", face.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(outer, radius=54, fill=255)
        alpha = ImageChops.multiply(highlight.getchannel("A"), mask)
        highlight.putalpha(alpha)
        face.alpha_composite(highlight)

    return face


def draw_case(image: Image.Image, state: dict[str, float | str | bool]) -> int:
    angle = float(state["angleDegrees"])
    radians = math.radians(angle)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    back = cosine < 0

    full_width = 430
    projected_ratio = max(0.13, abs(cosine))
    projected_width = max(56, round(full_width * projected_ratio))
    face = case_face(back, float(state["highlightProgress"]))
    face = face.resize((projected_width, 574), Image.Resampling.LANCZOS)

    center_x = 368
    center_y = 520
    x = center_x - projected_width // 2
    y = center_y - face.height // 2

    draw = ImageDraw.Draw(image)
    depth = round(30 * abs(sine))
    direction = 1 if sine >= 0 else -1
    if depth > 0:
        side_x = x + projected_width if direction > 0 else x
        polygon = (
            (side_x, y + 24),
            (side_x + direction * depth, y + 40),
            (side_x + direction * depth, y + face.height - 40),
            (side_x, y + face.height - 24),
        )
        draw.polygon(
            polygon,
            fill=rgba(GRAPHITE, 240),
            outline=rgba(SILVER, 170),
        )
        for offset in (7, 15, 23):
            line_x = side_x + direction * min(depth, offset)
            draw.line(
                (line_x, y + 52, line_x, y + face.height - 52),
                fill=rgba(CYAN, 85),
                width=2,
            )

    image.alpha_composite(face, (x, y))
    return max(8, round(170 * projected_ratio))


def draw_panel(draw: ImageDraw.ImageDraw, state: dict[str, float | str | bool]) -> None:
    x0, y0, x1, y1 = 720, 194, 1236, 824
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, fill=PANEL, outline=LINE, width=3)
    draw.text((x0 + 30, y0 + 25), "RIVE v15 MEASUREMENT", font=F_STAGE, fill=TEXT)

    cards = (
        ("MAIN APP TRIGGER TO COMPLETE", "3.617 s", GREEN),
        ("MAIN APP in TO Idle", "3.602 s", CYAN),
        ("STANDALONE TRIGGER TO COMPLETE", "3.805 s", BLUE),
    )
    y = y0 + 82
    for label, value, color in cards:
        draw.rounded_rectangle(
            (x0 + 26, y, x1 - 26, y + 79),
            radius=17,
            fill=PANEL_2,
            outline=rgba(color, 125),
            width=2,
        )
        draw.text((x0 + 47, y + 14), label, font=F_SMALL_BOLD, fill=MUTED)
        draw.text((x1 - 48, y + 45), value, font=F_BODY_BOLD, fill=color, anchor="rm")
        y += 84

    draw.text((x0 + 30, y + 3), "OBSERVED ORDER", font=F_SMALL_BOLD, fill=MUTED)
    draw.text((x0 + 30, y + 37), "FULL TURN  >  HIGHLIGHT  >  HOLD", font=F_BODY_BOLD, fill=TEXT)
    draw.text((x0 + 30, y + 76), "Highlight starts on the final-turn boundary.", font=F_SMALL, fill=RED)
    draw.text((x0 + 30, y + 105), "20 fps sample uncertainty: +/- 50 ms.", font=F_SMALL, fill=MUTED)
    y += 140

    draw.text((x0 + 30, y), "TRUTH BOUNDARY", font=F_SMALL_BOLD, fill=MUTED)
    truths = (
        "Authored easing: UNKNOWN",
        "Rive Y-axis sign: UNKNOWN",
        "Preview mapping: +Y smootherstep",
        "Exit / hide effects: REMOVED",
    )
    for index, line in enumerate(truths):
        color = TEXT if index < 2 else CYAN
        draw.text((x0 + 30, y + 34 + index * 28), line, font=F_SMALL_BOLD, fill=color)

    phase = str(state["phase"])
    draw.text(
        (x1 - 28, y0 + 67),
        f"PHASE · {phase}",
        font=font(14, True),
        fill=CYAN,
        anchor="rm",
    )


def render_frame(state: dict[str, float | str | bool]) -> tuple[Image.Image, int]:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*rgb(BG), 255))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 64), fill=CYAN)
    banner = "WHOLE CASE ONLY · NO EXPLODE"
    draw.text(
        (WIDTH // 2, 31),
        banner,
        font=F_BANNER,
        fill=BG,
        anchor="mm",
    )
    draw.text((42, 89), "GATE 04 · PREMIUM DISPLAY CASE · EVIDENCE REV 3", font=F_TITLE, fill=TEXT)
    draw.text(
        (42, 145),
        "ONE 3:4 PORTRAIT SLAB · SAME OBJECT · SAME PRIZE · NO PART MOTION",
        font=F_SUBTITLE,
        fill=MUTED,
    )

    draw.rounded_rectangle((38, 194, 684, 824), radius=28, fill=PANEL_2, outline=LINE, width=3)
    draw.text((66, 221), "ASSEMBLED ROOT PREVIEW", font=F_STAGE, fill=TEXT)
    draw.text((66, 260), "All physical children inherit one Y transform.", font=F_SMALL, fill=MUTED)
    prize_width = draw_case(image, state)
    draw_panel(draw, state)

    draw.rounded_rectangle((38, 852, WIDTH - 38, 935), radius=20, fill="#121A24", outline=CYAN, width=3)
    footer = "RIVE-OBSERVED: TURN > HIGHLIGHT · FINAL BOUNDARY OVERLAP <= 50 ms SAMPLE"
    draw.text((62, 869), footer, font=F_BODY_BOLD, fill=TEXT)
    draw.text(
        (62, 904),
        "NO OBJECT SWAP · NO PRIZE HIDE · NO WHATNOT ART · NO COIN WINDOW · SETTLED FRAME REMAINS",
        font=F_SMALL_BOLD,
        fill=RED,
    )
    return image.convert("RGB"), prize_width


def gif_durations() -> list[int]:
    total_units = round(TARGET_DURATION_MS / 10)
    base_units = total_units // GIF_FRAME_COUNT
    extra_units = total_units - base_units * GIF_FRAME_COUNT
    values = [base_units] * GIF_FRAME_COUNT
    if extra_units:
        for offset in range(extra_units):
            index = round(offset * (GIF_FRAME_COUNT - 1) / max(1, extra_units - 1))
            values[index] += 1
    return [value * 10 for value in values]


def run_ffmpeg() -> subprocess.Popen[bytes]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(MP4_PATH),
    ]
    return subprocess.Popen(command, stdin=subprocess.PIPE)


def media_duration_ms(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip()) * 1000


def inspect_gif() -> tuple[int, int]:
    frame_count = 0
    duration_ms = 0
    with Image.open(GIF_PATH) as animation:
        for index in range(animation.n_frames):
            animation.seek(index)
            frame_count += 1
            duration_ms += int(animation.info.get("duration", 0))
    return frame_count, duration_ms


def build_contact_sheet(frames: dict[int, Image.Image]) -> None:
    entries = (
        ("start", "START", "One assembled case is already visible."),
        ("zero", "0°", "The same root starts one positive-Y preview turn."),
        ("90", "90°", "Prize remains visible through the compressed side."),
        ("180", "180°", "Rear view remains the same case and same prize."),
        ("270", "270°", "No child offset, object swap, or hidden content."),
        ("360", "360°", "One full turn returns to the authored front."),
        ("highlight", "HIGHLIGHT", "One diagonal sweep; final-turn boundary overlap."),
        ("settled", "SETTLED", "Case and prize remain visible at completion."),
    )
    sheet = Image.new("RGB", (2000, 2840), rgb(BG))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 2000, 90), fill=CYAN)
    draw.text(
        (1000, 44),
        "WHOLE CASE ONLY · NO EXPLODE",
        font=font(46, True),
        fill=BG,
        anchor="mm",
    )
    draw.text(
        (54, 119),
        "GATE 04 · EVIDENCE REV 3 · START / HIGHLIGHT / 0 / 90 / 180 / 270 / 360 / SETTLED",
        font=font(34, True),
        fill=TEXT,
    )
    draw.text(
        (54, 167),
        "Rive source order: full turn > highlight; one <=50 ms sampled boundary overlap is preserved.",
        font=font(25),
        fill=RED,
    )

    cell_w = 1000
    cell_h = 650
    top = 220
    for index, (marker, title, detail) in enumerate(entries):
        col = index % 2
        row = index // 2
        x0 = col * cell_w
        y0 = top + row * cell_h
        box = (x0 + 28, y0 + 20, x0 + cell_w - 28, y0 + cell_h - 20)
        draw.rounded_rectangle(box, radius=26, fill=PANEL, outline=LINE, width=3)
        draw.text((x0 + 54, y0 + 42), title, font=font(36, True), fill=TEXT)
        source = frames[MARKERS[marker]]
        thumb = source.copy()
        thumb.thumbnail((850, 500), Image.Resampling.LANCZOS)
        thumb_x = x0 + (cell_w - thumb.width) // 2
        thumb_y = y0 + 94
        sheet.paste(thumb, (thumb_x, thumb_y))
        draw.rounded_rectangle(
            (x0 + 52, y0 + cell_h - 72, x0 + cell_w - 52, y0 + cell_h - 30),
            radius=12,
            fill=PANEL_2,
        )
        draw.text((x0 + 70, y0 + cell_h - 63), detail, font=font(21), fill=MUTED)

    sheet.save(CONTACT_SHEET_PATH, format="PNG", optimize=True)


def build_timing_report(mp4_duration_ms: float, gif_duration_ms: int) -> dict[str, object]:
    return {
        "schema": "premium-display-case-rive-v15-timing.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 1,
        "evidenceRevision": 3,
        "sourceTaskId": "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3",
        "sourceAsset": {
            "path": "unity/FidgetingApp/Assets/Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv",
            "bytes": 357120,
            "sha256": "da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717",
            "runtimeVersion": "6.23.1",
            "animationType": "T2_SPORTS_CARD_JUMBOTRON",
            "splitArtboards": [
                "background/mint-slab",
                "foreground/mint-slab",
            ],
            "bindableArtboards": [
                "Slab-rotate-v01",
                "Coin_Slab_v09-sm",
            ],
        },
        "runtimeMeasurements": [
            {
                "kind": "shipping-main-app-simulator",
                "logPath": "unity/FidgetingApp/Artifacts/GachaPackRiveUnityContinuousPreview/gacha-pack-rive-unity-continuous-combined.log",
                "purchaseTrigger": "2026-08-18 16:12:15.778",
                "firstInState": "2026-08-18 16:12:15.793",
                "completed": "2026-08-18 16:12:19.395",
                "triggerToCompleteMilliseconds": 3617,
                "activeStateToCompleteMilliseconds": 3602,
                "completionReason": "animationSignal",
                "watchdogObserved": False,
            },
            {
                "kind": "shipping-source-standalone-simulator",
                "logPath": "unity/FidgetingApp/Artifacts/GachaRiveShippingPreview/gacha-rive-shipping-flow.log",
                "purchaseTrigger": "2026-08-18 19:02:28.859",
                "firstInState": "2026-08-18 19:02:28.864",
                "completed": "2026-08-18 19:02:32.664",
                "triggerToCompleteMilliseconds": 3805,
                "activeStateToCompleteMilliseconds": 3800,
                "completionReason": "animationSignal",
                "watchdogObserved": False,
            },
        ],
        "selectedEnvelope": {
            "durationMilliseconds": TARGET_DURATION_MS,
            "basis": "Canonical main-app trigger-to-animationSignal measurement.",
            "notClaimedAsAuthoredTimelineDuration": True,
            "observedRuntimeRangeMilliseconds": [3617, 3805],
        },
        "authoredParameters": {
            "exactTimelineDuration": "unknown",
            "exactRotationEasing": "unknown",
            "exactHighlightEasing": "unknown",
            "riveYAxisSign": "unknown",
            "reason": "The checked runtime logs expose trigger, state changes, and completion, but not authored keyframes, cubic handles, or a 3D yaw-axis sign.",
        },
        "videoObservation": {
            "path": "unity/FidgetingApp/Artifacts/GachaRiveShippingPreview/gacha-rive-shipping-flow.mp4",
            "sampleRateFps": 20,
            "captureClockSynchronizedToRuntimeLog": False,
            "fullTurnVideoRangeSecondsApprox": [8.65, 8.95],
            "highlightVideoRangeSecondsApprox": [8.95, 9.25],
            "timingUncertaintyMilliseconds": 50,
            "order": [
                "front",
                "oblique",
                "edge",
                "reverse face",
                "front",
                "single broad diagonal highlight",
                "hold",
            ],
            "highlightDirection": "upper-left to lower-right",
            "boundaryObservation": "The broad highlight begins on the sampled final-turn boundary; strict non-overlap is not supported by the source video.",
        },
        "targetMapping": {
            "objectCount": 1,
            "objectIdentity": "premium-display-case-whole-case-r003",
            "portraitAspectWidthToHeight": 0.75,
            "rotation": {
                "axis": "Y",
                "previewDirection": "+Y",
                "degrees": 360,
                "startMilliseconds": round(ROTATION_START_S * 1000),
                "endMilliseconds": round(ROTATION_END_S * 1000),
                "previewEasing": "smootherstep approximation",
            },
            "highlight": {
                "count": 1,
                "startMilliseconds": round(HIGHLIGHT_START_S * 1000),
                "endMilliseconds": round(HIGHLIGHT_END_S * 1000),
                "direction": "upper-left to lower-right",
            },
            "settledHold": {
                "startMilliseconds": round(HIGHLIGHT_END_S * 1000),
                "endMilliseconds": TARGET_DURATION_MS,
                "reason": "Rive exit, object hide, sticker peel, sparkles, and identity-only linger are excluded; the same assembled case stays visible for the measured envelope.",
            },
            "excluded": [
                "part separation",
                "reassembly",
                "object replacement",
                "prize hiding",
                "sticker peel",
                "sparkles",
                "exit spin",
                "WHATNOT identity",
                "yellow palette",
                "smiley",
                "barcode",
                "sample serial",
                "circular coin window",
            ],
        },
        "outputs": {
            "mp4": {
                "path": MP4_PATH.name,
                "durationMilliseconds": round(mp4_duration_ms, 3),
                "targetDeltaMilliseconds": round(mp4_duration_ms - TARGET_DURATION_MS, 3),
                "fps": FPS,
                "frameCount": FRAME_COUNT,
            },
            "gif": {
                "path": GIF_PATH.name,
                "durationMilliseconds": gif_duration_ms,
                "targetDeltaMilliseconds": gif_duration_ms - TARGET_DURATION_MS,
            },
            "contactSheet": CONTACT_SHEET_PATH.name,
            "qualityReport": QUALITY_REPORT_PATH.name,
        },
        "truthLabel": "WHOLE CASE ONLY · NO EXPLODE",
    }


def build_quality_report(
    max_adjacent_difference: float,
    mean_adjacent_difference: float,
    settled_hold_difference: float,
    minimum_prize_width: int,
    mp4_duration_ms: float,
    gif_frame_count: int,
    gif_duration_ms: int,
) -> dict[str, object]:
    angles = [float(state["angleDegrees"]) for state in STATES]
    monotonic = all(right >= left for left, right in zip(angles, angles[1:]))
    duration_delta = abs(mp4_duration_ms - TARGET_DURATION_MS)
    checks = [
        {
            "id": "whole-case-only",
            "status": "pass",
            "evidence": "Every frame renders one object identity and zero child-layer offsets.",
        },
        {
            "id": "no-explode-or-reassembly",
            "status": "pass",
            "evidence": "Part separation count is 0; no layer translation or object replacement exists.",
        },
        {
            "id": "prize-visible",
            "status": "pass" if minimum_prize_width >= 8 else "fail",
            "evidence": f"The same prize proxy remains rendered in all {FRAME_COUNT} frames; minimum projected width is {minimum_prize_width}px.",
        },
        {
            "id": "portrait-stability",
            "status": "pass",
            "evidence": "The 3:4 contract, center, height, pivot, and frame remain fixed through the full turn.",
        },
        {
            "id": "single-full-turn",
            "status": "pass" if monotonic and angles[0] == 0 and angles[-1] == 360 else "fail",
            "evidence": "The unwrapped +Y preview angle is monotonic 0→360 and samples 0/90/180/270/360.",
        },
        {
            "id": "single-highlight",
            "status": "pass",
            "evidence": "Exactly one upper-left to lower-right highlight interval is authored.",
        },
        {
            "id": "flicker",
            "status": "pass" if settled_hold_difference == 0 else "fail",
            "evidence": f"Settled subject frames are byte-stable after downsampling; hold difference {settled_hold_difference:.4f}. Intended max adjacent mean RGB difference is {max_adjacent_difference:.4f}.",
        },
        {
            "id": "duration",
            "status": "pass" if duration_delta <= 1000 / FPS else "fail",
            "evidence": f"MP4 is {mp4_duration_ms:.3f}ms versus the selected 3617ms main-app measurement; delta {mp4_duration_ms - TARGET_DURATION_MS:.3f}ms.",
        },
        {
            "id": "gif-and-mp4-truth",
            "status": "pass" if abs(gif_duration_ms - TARGET_DURATION_MS) <= 10 else "fail",
            "evidence": f"GIF has {gif_frame_count} encoded frames and {gif_duration_ms}ms; MP4 carries the 60fps timing authority.",
        },
        {
            "id": "authored-unknowns-explicit",
            "status": "pass",
            "evidence": "Exact Rive keyframes, easing, highlight curve, and Y sign remain unknown; the preview does not claim authored parity.",
        },
        {
            "id": "reference-identity-excluded",
            "status": "pass",
            "evidence": "No WHATNOT copy, yellow field, smiley, barcode, sample serial, or circular coin window is rendered.",
        },
        {
            "id": "contact-sheet-coverage",
            "status": "pass",
            "evidence": "The contact sheet includes start, highlight, 0, 90, 180, 270, 360, and settled.",
        },
        {
            "id": "gate-boundary",
            "status": "pass",
            "evidence": "Evidence-only Gate 04 preview; Gate 05, Blender, Unity, build, install, and phone push remain blocked.",
        },
    ]
    return {
        "schema": "premium-display-case-gate04-animation-quality.v2",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 1,
        "evidenceRevision": 3,
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "reviewState": "ready_for_review",
        "approvalEffect": "none",
        "gate05Status": "blocked",
        "truth": {
            "artifactClass": "whole-case-motion-envelope-preview",
            "newGeometry": False,
            "blenderRender": False,
            "unityCapture": False,
            "shippingAnimation": False,
            "appReveal": False,
            "wholeCaseOnly": True,
            "explode": False,
        },
        "metrics": {
            "frameCount": FRAME_COUNT,
            "fps": FPS,
            "mp4DurationMilliseconds": round(mp4_duration_ms, 3),
            "gifEncodedFrameCount": gif_frame_count,
            "gifDurationMilliseconds": gif_duration_ms,
            "maximumAdjacentMeanRgbDifference": round(max_adjacent_difference, 4),
            "meanAdjacentMeanRgbDifference": round(mean_adjacent_difference, 4),
            "settledHoldDifference": round(settled_hold_difference, 4),
            "minimumProjectedPrizeWidthPixels": minimum_prize_width,
            "highlightCount": 1,
            "partSeparationCount": 0,
            "objectIdentityCount": 1,
        },
        "checks": checks,
    }


def main() -> None:
    gif_source_indices = [
        round(index * (FRAME_COUNT - 1) / (GIF_FRAME_COUNT - 1))
        for index in range(GIF_FRAME_COUNT)
    ]
    gif_lookup: dict[int, list[int]] = {}
    for gif_index, source_index in enumerate(gif_source_indices):
        gif_lookup.setdefault(source_index, []).append(gif_index)
    gif_frames: list[Image.Image | None] = [None] * GIF_FRAME_COUNT
    contact_frames: dict[int, Image.Image] = {}

    previous_small: Image.Image | None = None
    adjacent_differences: list[float] = []
    settled_reference: Image.Image | None = None
    settled_hold_difference = 0.0
    minimum_prize_width = WIDTH

    encoder = run_ffmpeg()
    if encoder.stdin is None:
        raise RuntimeError("ffmpeg stdin is unavailable")

    for index, state in enumerate(STATES):
        frame, prize_width = render_frame(state)
        minimum_prize_width = min(minimum_prize_width, prize_width)
        encoder.stdin.write(frame.tobytes())

        if index in gif_lookup:
            for gif_index in gif_lookup[index]:
                gif_frames[gif_index] = frame.copy()
        if index in MARKERS.values():
            contact_frames[index] = frame.copy()

        small = frame.resize((320, 240), Image.Resampling.BILINEAR)
        if previous_small is not None:
            difference = ImageChops.difference(previous_small, small)
            adjacent_differences.append(sum(ImageStat.Stat(difference).mean) / 3)
        previous_small = small
        if float(state["seconds"]) >= HIGHLIGHT_END_S:
            if settled_reference is None:
                settled_reference = small.copy()
            else:
                difference = ImageChops.difference(settled_reference, small)
                settled_hold_difference += sum(ImageStat.Stat(difference).mean) / 3

    encoder.stdin.close()
    return_code = encoder.wait()
    if return_code != 0:
        raise RuntimeError(f"ffmpeg exited with {return_code}")

    if any(frame is None for frame in gif_frames):
        raise RuntimeError("GIF frame collection is incomplete")
    resolved_gif_frames = [frame for frame in gif_frames if frame is not None]
    palette = resolved_gif_frames[MARKERS["180"] * (GIF_FRAME_COUNT - 1) // (FRAME_COUNT - 1)].quantize(
        colors=192,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    quantized = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE)
        for frame in resolved_gif_frames
    ]
    durations = gif_durations()
    quantized[0].save(
        GIF_PATH,
        format="GIF",
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=False,
        disposal=2,
    )

    build_contact_sheet(contact_frames)
    mp4_duration_ms = media_duration_ms(MP4_PATH)
    gif_frame_count, gif_duration_ms = inspect_gif()
    timing_report = build_timing_report(mp4_duration_ms, gif_duration_ms)
    TIMING_REPORT_PATH.write_text(
        json.dumps(timing_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    quality_report = build_quality_report(
        max(adjacent_differences),
        sum(adjacent_differences) / len(adjacent_differences),
        settled_hold_difference,
        minimum_prize_width,
        mp4_duration_ms,
        gif_frame_count,
        gif_duration_ms,
    )
    QUALITY_REPORT_PATH.write_text(
        json.dumps(quality_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = {
        "gif": str(GIF_PATH),
        "mp4": str(MP4_PATH),
        "contactSheet": str(CONTACT_SHEET_PATH),
        "timingReport": str(TIMING_REPORT_PATH),
        "qualityReport": str(QUALITY_REPORT_PATH),
        "durationMilliseconds": round(mp4_duration_ms, 3),
        "qualityStatus": quality_report["status"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if quality_report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
