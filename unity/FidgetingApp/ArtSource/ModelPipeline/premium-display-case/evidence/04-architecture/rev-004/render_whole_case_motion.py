#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
REV3_SCRIPT = ROOT.parent / "rev-003" / "render_whole_case_motion.py"
SPEC = importlib.util.spec_from_file_location("premium_display_case_rev3", REV3_SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {REV3_SCRIPT}")
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

BASELINE_DURATION_MS = 3617
TIME_SCALE = 1.25
TARGET_DURATION_MS = BASELINE_DURATION_MS * TIME_SCALE
PLAYBACK_FPS = 48
TRUTH_LABEL = "WHOLE CASE ONLY · 1.25× SLOWER · NO EXPLODE"

BASE.GIF_PATH = ROOT / "whole-case-only-1.25x-slower.gif"
BASE.MP4_PATH = ROOT / "whole-case-only-1.25x-slower.mp4"
BASE.CONTACT_SHEET_PATH = ROOT / "whole-case-only-1.25x-slower-contact-sheet.png"
BASE.TIMING_REPORT_PATH = ROOT / "whole-case-only-1.25x-slower-timing-report.json"
BASE.QUALITY_REPORT_PATH = ROOT / "animation-quality-report.json"
BASE.TARGET_DURATION_MS = TARGET_DURATION_MS
BASE.MP4_DURATION_MS = BASE.FRAME_COUNT * 1000 / PLAYBACK_FPS

SOURCE_RENDER_FRAME = BASE.render_frame
SOURCE_BUILD_CONTACT_SHEET = BASE.build_contact_sheet
SOURCE_BUILD_TIMING_REPORT = BASE.build_timing_report
SOURCE_BUILD_QUALITY_REPORT = BASE.build_quality_report


def motion_sequence_sha256() -> str:
    sequence = [
        {
            "angleDegrees": round(float(state["angleDegrees"]), 9),
            "highlightProgress": round(float(state["highlightProgress"]), 9),
            "highlightActive": bool(state["highlightActive"]),
        }
        for state in BASE.STATES
    ]
    encoded = json.dumps(sequence, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


MOTION_SEQUENCE_SHA256 = motion_sequence_sha256()


def draw_panel_rev4(draw: ImageDraw.ImageDraw, state: dict[str, float | str | bool]) -> None:
    x0, y0, x1, y1 = 720, 194, 1236, 824
    draw.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=28,
        fill=BASE.PANEL,
        outline=BASE.LINE,
        width=3,
    )
    draw.text((x0 + 30, y0 + 25), "SPEED-ONLY REVISION", font=BASE.F_STAGE, fill=BASE.TEXT)

    cards = (
        ("MEASURED MAIN APP BASELINE", "3.617 s", BASE.GREEN),
        ("USER-REQUESTED TIME SCALE", "1.25×", BASE.CYAN),
        ("TARGET ENVELOPE", "4.521 s", BASE.BLUE),
    )
    y = y0 + 82
    for label, value, color in cards:
        draw.rounded_rectangle(
            (x0 + 26, y, x1 - 26, y + 79),
            radius=17,
            fill=BASE.PANEL_2,
            outline=BASE.rgba(color, 125),
            width=2,
        )
        draw.text((x0 + 47, y + 14), label, font=BASE.F_SMALL_BOLD, fill=BASE.MUTED)
        draw.text((x1 - 48, y + 45), value, font=BASE.F_BODY_BOLD, fill=color, anchor="rm")
        y += 84

    draw.text((x0 + 30, y + 3), "UNCHANGED ORDER", font=BASE.F_SMALL_BOLD, fill=BASE.MUTED)
    draw.text(
        (x0 + 30, y + 37),
        "FULL TURN  >  HIGHLIGHT  >  HOLD",
        font=BASE.F_BODY_BOLD,
        fill=BASE.TEXT,
    )
    draw.text(
        (x0 + 30, y + 76),
        "Same 217 visual samples; playback is 48 fps.",
        font=BASE.F_SMALL,
        fill=BASE.RED,
    )
    draw.text(
        (x0 + 30, y + 105),
        "No pause added. No second highlight.",
        font=BASE.F_SMALL,
        fill=BASE.MUTED,
    )
    y += 140

    draw.text((x0 + 30, y), "TRUTH BOUNDARY", font=BASE.F_SMALL_BOLD, fill=BASE.MUTED)
    truths = (
        "Authored easing: UNKNOWN",
        "Rive Y-axis sign: UNKNOWN",
        "Preview mapping: +Y smootherstep",
        "Only playback rate changed",
    )
    for index, line in enumerate(truths):
        color = BASE.TEXT if index < 2 else BASE.CYAN
        draw.text((x0 + 30, y + 34 + index * 28), line, font=BASE.F_SMALL_BOLD, fill=color)

    phase = str(state["phase"])
    draw.text(
        (x1 - 28, y0 + 67),
        f"PHASE · {phase}",
        font=BASE.font(14, True),
        fill=BASE.CYAN,
        anchor="rm",
    )


def render_frame_rev4(state: dict[str, float | str | bool]) -> tuple[Image.Image, int]:
    image, prize_width = SOURCE_RENDER_FRAME(state)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, BASE.WIDTH, 64), fill=BASE.CYAN)
    draw.text(
        (BASE.WIDTH // 2, 31),
        TRUTH_LABEL,
        font=BASE.font(30, True),
        fill=BASE.BG,
        anchor="mm",
    )
    draw.rectangle((0, 70, BASE.WIDTH, 178), fill=BASE.BG)
    draw.text(
        (42, 89),
        "GATE 04 · PREMIUM DISPLAY CASE · EVIDENCE REV 4",
        font=BASE.F_TITLE,
        fill=BASE.TEXT,
    )
    draw.text(
        (42, 145),
        "SAME 217-FRAME SEQUENCE · ONE Y 360° · ONE HIGHLIGHT · NO PART MOTION",
        font=BASE.F_SUBTITLE,
        fill=BASE.MUTED,
    )

    draw.rounded_rectangle(
        (38, 852, BASE.WIDTH - 38, 935),
        radius=20,
        fill="#121A24",
        outline=BASE.CYAN,
        width=3,
    )
    draw.text(
        (62, 869),
        "TIME-SCALE ONLY · 3.617 s × 1.25 = 4.521 s TARGET · SAME FRAME ORDER",
        font=BASE.F_BODY_BOLD,
        fill=BASE.TEXT,
    )
    draw.text(
        (62, 904),
        "NO NEW PAUSE · ONE HIGHLIGHT · NO OBJECT SWAP · NO PRIZE HIDE · SETTLED VISIBLE",
        font=BASE.F_SMALL_BOLD,
        fill=BASE.RED,
    )
    return image, prize_width


def build_contact_sheet_rev4(frames: dict[int, Image.Image]) -> None:
    SOURCE_BUILD_CONTACT_SHEET(frames)
    with Image.open(BASE.CONTACT_SHEET_PATH) as source:
        sheet = source.convert("RGB")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, 2000, 215), fill=BASE.BG)
    draw.rectangle((0, 0, 2000, 90), fill=BASE.CYAN)
    draw.text(
        (1000, 44),
        TRUTH_LABEL,
        font=BASE.font(42, True),
        fill=BASE.BG,
        anchor="mm",
    )
    draw.text(
        (54, 119),
        "GATE 04 · EVIDENCE REV 4 · START / 0 / 90 / 180 / 270 / 360 / HIGHLIGHT / SETTLED",
        font=BASE.font(32, True),
        fill=BASE.TEXT,
    )
    draw.text(
        (54, 167),
        "Speed-only supersession: identical normalized motion samples at 1.25× duration; no pause or second highlight.",
        font=BASE.font(24),
        fill=BASE.RED,
    )
    sheet.save(BASE.CONTACT_SHEET_PATH, format="PNG", optimize=True)


def run_ffmpeg_rev4() -> subprocess.Popen[bytes]:
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
        f"{BASE.WIDTH}x{BASE.HEIGHT}",
        "-r",
        str(PLAYBACK_FPS),
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
        str(BASE.MP4_PATH),
    ]
    return subprocess.Popen(command, stdin=subprocess.PIPE)


def scaled_milliseconds(value: int | float) -> float:
    return round(float(value) * TIME_SCALE, 3)


def build_timing_report_rev4(mp4_duration_ms: float, gif_duration_ms: int) -> dict[str, object]:
    report = SOURCE_BUILD_TIMING_REPORT(mp4_duration_ms, gif_duration_ms)
    report["schema"] = "premium-display-case-whole-case-slowdown-timing.v2"
    report["evidenceRevision"] = 4
    report["userFeedback"] = {
        "rejectedEvidenceRevision": 3,
        "quote": "速度有点太快了",
        "scope": "speed-only",
        "preserved": [
            "one whole assembled case",
            "portrait framing",
            "one unwrapped Y-axis 360-degree turn",
            "one upper-left to lower-right highlight",
            "same frame order",
            "no part separation",
            "no object replacement",
        ],
    }
    report["selectedEnvelope"] = {
        "baselineDurationMilliseconds": BASELINE_DURATION_MS,
        "timeScale": TIME_SCALE,
        "targetDurationMilliseconds": TARGET_DURATION_MS,
        "basis": "Canonical 3617 ms main-app envelope multiplied by the user-requested 1.25 time scale.",
        "notClaimedAsAuthoredTimelineDuration": True,
        "noNewPause": True,
        "noSecondHighlight": True,
    }
    report["frameSequence"] = {
        "sourceEvidenceRevision": 3,
        "frameCount": BASE.FRAME_COUNT,
        "sourceSamplingFps": BASE.FPS,
        "playbackFps": PLAYBACK_FPS,
        "framesAdded": 0,
        "framesRemoved": 0,
        "framesReordered": 0,
        "motionSequenceSha256": MOTION_SEQUENCE_SHA256,
    }

    mapping = report["targetMapping"]
    mapping["objectIdentity"] = "premium-display-case-whole-case-r004"
    rotation = mapping["rotation"]
    rotation["startMilliseconds"] = scaled_milliseconds(rotation["startMilliseconds"])
    rotation["endMilliseconds"] = scaled_milliseconds(rotation["endMilliseconds"])
    highlight = mapping["highlight"]
    highlight["startMilliseconds"] = scaled_milliseconds(highlight["startMilliseconds"])
    highlight["endMilliseconds"] = scaled_milliseconds(highlight["endMilliseconds"])
    settled = mapping["settledHold"]
    settled["startMilliseconds"] = scaled_milliseconds(settled["startMilliseconds"])
    settled["endMilliseconds"] = TARGET_DURATION_MS
    settled["reason"] = (
        "The rev 3 hold is time-scaled with every other sample. No new pause, exit, hide, sticker peel, "
        "sparkle, or identity-only linger was added."
    )

    report["outputs"]["mp4"] = {
        "path": BASE.MP4_PATH.name,
        "durationMilliseconds": round(mp4_duration_ms, 3),
        "targetDeltaMilliseconds": round(mp4_duration_ms - TARGET_DURATION_MS, 3),
        "targetDeltaPercent": round((mp4_duration_ms - TARGET_DURATION_MS) / TARGET_DURATION_MS * 100, 6),
        "fps": PLAYBACK_FPS,
        "frameCount": BASE.FRAME_COUNT,
        "durationProbe": "ffprobe format.duration",
    }
    report["outputs"]["gif"] = {
        "path": BASE.GIF_PATH.name,
        "durationMilliseconds": gif_duration_ms,
        "targetDeltaMilliseconds": round(gif_duration_ms - TARGET_DURATION_MS, 3),
        "targetDeltaPercent": round((gif_duration_ms - TARGET_DURATION_MS) / TARGET_DURATION_MS * 100, 6),
        "durationProbe": "Pillow GIF frame metadata",
    }
    report["outputs"]["contactSheet"] = BASE.CONTACT_SHEET_PATH.name
    report["outputs"]["qualityReport"] = BASE.QUALITY_REPORT_PATH.name
    report["truthLabel"] = TRUTH_LABEL
    return report


def build_quality_report_rev4(
    max_adjacent_difference: float,
    mean_adjacent_difference: float,
    settled_hold_difference: float,
    minimum_prize_width: int,
    mp4_duration_ms: float,
    gif_frame_count: int,
    gif_duration_ms: int,
) -> dict[str, object]:
    report = SOURCE_BUILD_QUALITY_REPORT(
        max_adjacent_difference,
        mean_adjacent_difference,
        settled_hold_difference,
        minimum_prize_width,
        mp4_duration_ms,
        gif_frame_count,
        gif_duration_ms,
    )
    report["schema"] = "premium-display-case-gate04-animation-quality.v3"
    report["evidenceRevision"] = 4
    report["truth"].update(
        {
            "speedOnlySupersession": True,
            "frameSequenceChanged": False,
            "newPauseAdded": False,
            "secondHighlightAdded": False,
        }
    )
    report["revisionDisposition"] = {
        "rejectedEvidenceRevision": 3,
        "rejectionScope": "speed-only",
        "wholeCaseDirectionRejected": False,
        "portraitRejected": False,
        "fullTurnRejected": False,
        "singleHighlightRejected": False,
    }
    report["metrics"].update(
        {
            "fps": PLAYBACK_FPS,
            "sourceSamplingFps": BASE.FPS,
            "targetDurationMilliseconds": TARGET_DURATION_MS,
            "baselineDurationMilliseconds": BASELINE_DURATION_MS,
            "timeScale": TIME_SCALE,
            "targetDeltaMilliseconds": round(mp4_duration_ms - TARGET_DURATION_MS, 3),
            "motionSequenceSha256": MOTION_SEQUENCE_SHA256,
        }
    )
    for check in report["checks"]:
        if check["id"] == "duration":
            check["status"] = "pass" if abs(mp4_duration_ms - TARGET_DURATION_MS) <= 1000 / PLAYBACK_FPS else "fail"
            check["evidence"] = (
                f"ffprobe measures {mp4_duration_ms:.3f}ms versus the {TARGET_DURATION_MS:.3f}ms target; "
                f"delta {mp4_duration_ms - TARGET_DURATION_MS:.3f}ms."
            )
        elif check["id"] == "gif-and-mp4-truth":
            check["status"] = "pass" if abs(gif_duration_ms - TARGET_DURATION_MS) <= 10 else "fail"
            check["evidence"] = (
                f"GIF metadata totals {gif_duration_ms}ms across {gif_frame_count} encoded frames; "
                f"MP4 ffprobe metadata carries the {PLAYBACK_FPS}fps timing authority."
            )
        elif check["id"] == "authored-unknowns-explicit":
            check["evidence"] = (
                "Exact authored Rive easing, highlight curve, timeline duration, and Y sign remain unknown."
            )
        elif check["id"] == "gate-boundary":
            check["evidence"] = (
                "Evidence-only Gate 04 rev 4 preview; Gate 05, Blender, Unity, build, install, and phone push remain blocked."
            )
    report["checks"].insert(
        6,
        {
            "id": "time-scale-only",
            "status": "pass",
            "evidence": (
                f"The same {BASE.FRAME_COUNT} ordered motion samples use {PLAYBACK_FPS}fps playback. "
                "No frame, pause, highlight, object, or part event was added."
            ),
        },
    )
    report["status"] = "pass" if all(check["status"] == "pass" for check in report["checks"]) else "fail"
    return report


BASE.draw_panel = draw_panel_rev4
BASE.render_frame = render_frame_rev4
BASE.build_contact_sheet = build_contact_sheet_rev4
BASE.run_ffmpeg = run_ffmpeg_rev4
BASE.build_timing_report = build_timing_report_rev4
BASE.build_quality_report = build_quality_report_rev4


if __name__ == "__main__":
    BASE.main()
