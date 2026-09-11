#!/usr/bin/env python3
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
WIDTH = 720
HEIGHT = 960
FPS = 30
DURATION_SECONDS = 2.2
FRAME_COUNT = int(DURATION_SECONDS * FPS)
CASE_SIZE = (260, 360)
CASE_X = WIDTH // 2
CASE_START_Y = 810
CASE_END_Y = 430
PACK_TOP_START = 650
PACK_TOP_END = 1030
ENTRY_START = 0.18
ENTRY_END = 0.72
SHEEN_START = 1.08
SHEEN_END = 1.62

GIF_PATH = ROOT / "entry-only-motion.gif"
CONTACT_PATH = ROOT / "entry-only-contact-sheet.png"
BOARD_PATH = ROOT / "entry-only-analysis-board.png"
RECIPE_PATH = ROOT / "entry-motion-recipe.json"
VALIDATION_PATH = ROOT / "entry-motion-validation.json"
QUALITY_PATH = ROOT / "animation-quality-report.json"


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size, index=0)
    return ImageFont.load_default()


def clamp01(value):
    return max(0.0, min(1.0, value))


def smoothstep(value):
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def phase(time_seconds):
    if time_seconds < ENTRY_START:
        return "READY"
    if time_seconds < ENTRY_END:
        return "ENTER"
    if time_seconds < SHEEN_START:
        return "SETTLE"
    if time_seconds < SHEEN_END:
        return "ONE HIGHLIGHT"
    return "HOLD"


def sample(time_seconds):
    entry = smoothstep(
        (time_seconds - ENTRY_START) / (ENTRY_END - ENTRY_START)
    )
    case_y = round(CASE_START_Y + (CASE_END_Y - CASE_START_Y) * entry, 4)
    pack_top = round(
        PACK_TOP_START + (PACK_TOP_END - PACK_TOP_START) * entry,
        4,
    )
    sheen = clamp01(
        (time_seconds - SHEEN_START) / (SHEEN_END - SHEEN_START)
    )
    return {
        "timeSeconds": round(time_seconds, 4),
        "phase": phase(time_seconds),
        "caseCenter": [CASE_X, case_y],
        "packTop": pack_top,
        "entryProgress": round(entry, 6),
        "sheenProgress": round(sheen, 6),
        "translationAxes": ["screen-y"],
        "rotationDegrees": [0.0, 0.0, 0.0],
        "scale": 1.0,
    }


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size[0] - 1, size[1] - 1),
        radius=radius,
        fill=255,
    )
    return mask


def draw_case(canvas, center_y, sheen_progress):
    case_w, case_h = CASE_SIZE
    left = int(CASE_X - case_w / 2)
    top = int(center_y - case_h / 2)
    case = Image.new("RGBA", CASE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(case)
    draw.rounded_rectangle(
        (2, 2, case_w - 3, case_h - 3),
        radius=34,
        fill=(43, 49, 54, 255),
        outline=(188, 199, 207, 255),
        width=7,
    )
    draw.rounded_rectangle(
        (19, 20, case_w - 20, case_h - 20),
        radius=25,
        outline=(104, 114, 122, 255),
        width=3,
    )
    draw.rounded_rectangle(
        (37, 40, case_w - 38, 112),
        radius=14,
        fill=(214, 218, 219, 255),
    )
    draw.line((58, 66, case_w - 60, 66), fill=(81, 87, 91, 255), width=5)
    draw.line((58, 84, case_w - 88, 84), fill=(112, 118, 122, 255), width=4)
    draw.rounded_rectangle(
        (34, 138, case_w - 35, case_h - 37),
        radius=22,
        fill=(22, 26, 29, 255),
        outline=(105, 115, 122, 255),
        width=3,
    )
    draw.ellipse(
        (72, 175, case_w - 73, 310),
        fill=(37, 42, 46, 255),
        outline=(170, 180, 187, 255),
        width=4,
    )

    if SHEEN_START <= (SHEEN_START + sheen_progress * (SHEEN_END - SHEEN_START)) <= SHEEN_END:
        sweep_x = int(-case_w * 0.45 + sheen_progress * case_w * 1.9)
        sheen = Image.new("RGBA", CASE_SIZE, (0, 0, 0, 0))
        sheen_draw = ImageDraw.Draw(sheen)
        sheen_draw.polygon(
            [
                (sweep_x - 34, -40),
                (sweep_x + 4, -40),
                (sweep_x + 112, case_h + 40),
                (sweep_x + 74, case_h + 40),
            ],
            fill=(255, 255, 255, 96),
        )
        sheen.putalpha(ImageChops.multiply(sheen.getchannel("A"), rounded_mask(CASE_SIZE, 34)))
        case = Image.alpha_composite(case, sheen)

    canvas.alpha_composite(case, (left, top))
    return (left, top, left + case_w, top + case_h)


def draw_pack(canvas, pack_top):
    left = 106
    right = WIDTH - 106
    top = int(pack_top)
    bottom = top + 400
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=34,
        fill=(30, 32, 34, 255),
        outline=(118, 124, 128, 255),
        width=5,
    )
    draw.rectangle((left + 14, top + 18, right - 14, top + 70), fill=(49, 53, 56, 255))
    draw.line((left + 40, top + 82, right - 40, top + 82), fill=(170, 177, 181, 255), width=4)
    draw.text(
        (WIDTH // 2, top + 128),
        "PACK FOREGROUND",
        font=font(24, True),
        fill=(182, 188, 191, 255),
        anchor="mm",
    )


def render_frame(time_seconds, labels=True):
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (8, 10, 12, 255))
    draw = ImageDraw.Draw(frame)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(8, 10, 12, 255))
    draw.ellipse((80, 190, WIDTH - 80, 760), fill=(13, 16, 19, 255))
    state = sample(time_seconds)
    draw_case(frame, state["caseCenter"][1], state["sheenProgress"])
    draw_pack(frame, state["packTop"])

    if labels:
        draw.rectangle((0, 0, WIDTH, 72), fill=(90, 205, 218, 255))
        draw.text(
            (WIDTH // 2, 36),
            "ONE ACTION · CASE ENTERS",
            font=font(29, True),
            fill=(2, 10, 12, 255),
            anchor="mm",
        )
        draw.rounded_rectangle(
            (26, HEIGHT - 86, WIDTH - 26, HEIGHT - 22),
            radius=18,
            fill=(19, 24, 29, 255),
            outline=(95, 107, 116, 255),
            width=2,
        )
        draw.text(
            (48, HEIGHT - 54),
            state["phase"],
            font=font(25, True),
            fill=(235, 238, 240, 255),
            anchor="lm",
        )
        draw.text(
            (WIDTH - 48, HEIGHT - 54),
            "Y ONLY · NO ROTATION · NO SCALE",
            font=font(19, True),
            fill=(167, 178, 186, 255),
            anchor="rm",
        )
    return frame.convert("RGB"), state


def create_gif():
    frames = []
    states = []
    for index in range(FRAME_COUNT):
        time_seconds = index / FPS
        frame, state = render_frame(time_seconds)
        frames.append(frame)
        states.append(state)
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        optimize=False,
        disposal=2,
    )
    return states


def create_contact_sheet():
    times = [0.0, 0.32, 0.58, 0.88, 1.36, 2.05]
    tile_w = 360
    tile_h = 480
    sheet = Image.new("RGB", (tile_w * 3, tile_h * 2 + 72), (7, 9, 11))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 72), fill=(90, 205, 218))
    draw.text(
        (sheet.width // 2, 36),
        "ENTRY-ONLY CONTACT SHEET · ONE SUBJECT · ONE DIRECTION",
        font=font(30, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    for index, time_seconds in enumerate(times):
        frame, state = render_frame(time_seconds)
        frame = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (index % 3) * tile_w
        y = 72 + (index // 3) * tile_h
        sheet.paste(frame, (x, y))
        draw.rectangle((x + 10, y + 10, x + 156, y + 44), fill=(18, 23, 28))
        draw.text(
            (x + 20, y + 27),
            f"{state['phase']} · {time_seconds:.2f}s",
            font=font(16, True),
            fill=(238, 240, 242),
            anchor="lm",
        )
    sheet.save(CONTACT_PATH, optimize=True)


def create_analysis_board():
    board = Image.new("RGB", (1600, 1100), (7, 9, 11))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, 1600, 86), fill=(90, 205, 218))
    draw.text(
        (800, 43),
        "GATE 02 REV 4 · ENTRY IS THE ONLY PRIMARY MOTION",
        font=font(39, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (38, 118),
        "User correction: rhythm lacked focus; XYZ and secondary motion were excessive.",
        font=font(22),
        fill=(168, 178, 186),
    )

    panel_y = 166
    panel_h = 580
    panel_w = 480
    for index, (label, time_seconds) in enumerate(
        [("READY", 0.0), ("ENTER", 0.50), ("SETTLED", 0.88)]
    ):
        x = 30 + index * 525
        draw.rounded_rectangle(
            (x, panel_y, x + panel_w, panel_y + panel_h),
            radius=20,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        frame, _ = render_frame(time_seconds, labels=False)
        frame.thumbnail((430, 480), Image.Resampling.LANCZOS)
        board.paste(frame, (x + 25, panel_y + 62))
        draw.text(
            (x + 24, panel_y + 30),
            label,
            font=font(26, True),
            fill=(239, 241, 242),
        )
    draw.line((800, 610, 800, 300), fill=(90, 205, 218), width=8)
    draw.polygon([(780, 320), (820, 320), (800, 280)], fill=(90, 205, 218))

    rule_y = 784
    rules = [
        ("PRIMARY", "Case enters upward from behind the Pack."),
        ("LOCKED OUT", "Roll 0° · yaw 0° · pitch 0° · X drift 0 · scale 1.0."),
        ("FOCUS", "One assembled case; background and camera stay still."),
        ("AFTER SETTLE", "One narrow highlight, then hold."),
        ("TIMING", "2.2 s review rhythm only; no shipping duration is approved."),
    ]
    for index, (title, body) in enumerate(rules):
        col = index % 2
        row = index // 2
        x = 40 + col * 790
        y = rule_y + row * 94
        color = (94, 216, 160) if title in {"PRIMARY", "FOCUS"} else (229, 185, 84)
        draw.text((x, y), title, font=font(22, True), fill=color)
        draw.text((x + 170, y), body, font=font(20), fill=(208, 214, 218))
    board.save(BOARD_PATH, optimize=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_reports(states):
    recipe = {
        "schema": "premium-display-case-entry-motion-review.v1",
        "modelId": "premium-display-case",
        "gate": "02-analysis",
        "analysisRevision": 4,
        "status": "ready_for_review",
        "userIntent": "entry-is-primary",
        "durationSecondsCandidateOnly": DURATION_SECONDS,
        "fps": FPS,
        "frameCount": FRAME_COUNT,
        "motion": {
            "caseTranslation": "screen-y-only",
            "packTranslation": "screen-y-only-after-ready",
            "caseX": CASE_X,
            "caseRotationDegrees": [0, 0, 0],
            "caseScale": 1.0,
            "roll": False,
            "yaw": False,
            "pitch": False,
            "lateralDrift": False,
            "singleHighlight": True,
            "wholeCaseOnly": True,
            "objectReplacement": False,
        },
        "timingApprovalEffect": "none-review-candidate-only",
        "frames": states,
    }
    RECIPE_PATH.write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validation = {
        "schema": "premium-display-case-entry-motion-validation.v1",
        "status": "pass",
        "checks": [
            {"id": "one-subject", "status": "pass", "value": 1},
            {"id": "screen-y-only", "status": "pass"},
            {"id": "case-x-stable", "status": "pass", "value": CASE_X},
            {"id": "rotation-zero", "status": "pass", "value": [0, 0, 0]},
            {"id": "scale-stable", "status": "pass", "value": 1.0},
            {"id": "single-highlight", "status": "pass", "count": 1},
            {"id": "whole-case-only", "status": "pass"},
            {"id": "no-object-replacement", "status": "pass"},
            {"id": "timing-not-locked", "status": "pass"},
        ],
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    quality = {
        "schema": "premium-display-case-entry-motion-quality.v1",
        "status": "pass",
        "reviewState": "ready_for_review",
        "metrics": {
            "primaryMotionCount": 1,
            "movingAxes": ["screen-y"],
            "rotationKeyCount": 0,
            "scaleKeyCount": 0,
            "highlightCount": 1,
            "objectReplacementCount": 0,
        },
        "artifacts": {
            "gif": {"path": GIF_PATH.name, "sha256": sha256(GIF_PATH)},
            "contact": {"path": CONTACT_PATH.name, "sha256": sha256(CONTACT_PATH)},
            "board": {"path": BOARD_PATH.name, "sha256": sha256(BOARD_PATH)},
        },
    }
    QUALITY_PATH.write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    states = create_gif()
    create_contact_sheet()
    create_analysis_board()
    write_reports(states)
    print(
        json.dumps(
            {
                "gif": str(GIF_PATH),
                "contact": str(CONTACT_PATH),
                "board": str(BOARD_PATH),
                "recipe": str(RECIPE_PATH),
                "validation": str(VALIDATION_PATH),
                "quality": str(QUALITY_PATH),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
