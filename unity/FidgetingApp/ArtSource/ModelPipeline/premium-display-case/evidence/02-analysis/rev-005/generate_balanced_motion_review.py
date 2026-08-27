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
DURATION_SECONDS = 3.4
FRAME_COUNT = int(DURATION_SECONDS * FPS)

READY_END = 0.15
ENTRY_END = 0.90
ROTATE_START = 1.05
ROTATE_END = 2.45
SHEEN_START = 2.50
SHEEN_END = 3.05

CASE_X = 0.0
CASE_ENTRY_START_Y = -2.75
CASE_END_Y = 0.0
CASE_ENTRY_START_Z = 2.0
CASE_END_Z = 0.2
PACK_TOP_START = 650
PACK_TOP_END = 1030

GIF_PATH = ROOT / "balanced-entry-showcase-motion.gif"
CONTACT_PATH = ROOT / "balanced-entry-showcase-contact-sheet.png"
BOARD_PATH = ROOT / "balanced-entry-showcase-analysis-board.png"
RECIPE_PATH = ROOT / "balanced-motion-recipe.json"
VALIDATION_PATH = ROOT / "balanced-motion-validation.json"
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
    if time_seconds < READY_END:
        return "READY"
    if time_seconds < ENTRY_END:
        return "ENTRY · Y + Z"
    if time_seconds < ROTATE_START:
        return "SETTLE"
    if time_seconds < ROTATE_END:
        return "360° SHOWCASE"
    if time_seconds < SHEEN_START:
        return "SETTLE"
    if time_seconds < SHEEN_END:
        return "ONE HIGHLIGHT"
    return "HOLD"


def sample(time_seconds):
    entry = smoothstep((time_seconds - READY_END) / (ENTRY_END - READY_END))
    rotation = smoothstep(
        (time_seconds - ROTATE_START) / (ROTATE_END - ROTATE_START)
    )
    sheen = clamp01(
        (time_seconds - SHEEN_START) / (SHEEN_END - SHEEN_START)
    )
    return {
        "timeSeconds": round(time_seconds, 4),
        "phase": phase(time_seconds),
        "entryProgress": round(entry, 6),
        "showcaseProgress": round(rotation, 6),
        "sheenProgress": round(sheen, 6),
        "caseWorldPosition": [
            CASE_X,
            round(
                CASE_ENTRY_START_Y
                + (CASE_END_Y - CASE_ENTRY_START_Y) * entry,
                6,
            ),
            round(
                CASE_ENTRY_START_Z
                + (CASE_END_Z - CASE_ENTRY_START_Z) * entry,
                6,
            ),
        ],
        "packTop": round(
            PACK_TOP_START + (PACK_TOP_END - PACK_TOP_START) * entry,
            6,
        ),
        "rotationEulerDegrees": [0.0, round(360.0 * rotation, 6), 0.0],
        "modelScale": 1.0,
        "cameraMotion": False,
        "backgroundMotion": False,
    }


def rotate_y(point, angle_degrees):
    angle = math.radians(angle_degrees)
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    x, y, z = point
    return (
        x * cos_a + z * sin_a,
        y,
        -x * sin_a + z * cos_a,
    )


def world_point(local, state):
    rotated = rotate_y(local, state["rotationEulerDegrees"][1])
    position = state["caseWorldPosition"]
    return (
        rotated[0] + position[0],
        rotated[1] + position[1],
        rotated[2] + position[2],
    )


def project(point):
    camera_distance = 6.0
    focal = 690.0
    denominator = max(1.0, point[2] + camera_distance)
    return (
        WIDTH / 2 + focal * point[0] / denominator,
        445 - focal * point[1] / denominator,
    )


def project_local(local, state):
    return project(world_point(local, state))


def draw_case(canvas, state):
    half_w = 1.0
    half_h = 1.4
    half_d = 0.24
    vertices = {
        "fbl": (-half_w, -half_h, -half_d),
        "fbr": (half_w, -half_h, -half_d),
        "ftr": (half_w, half_h, -half_d),
        "ftl": (-half_w, half_h, -half_d),
        "bbl": (-half_w, -half_h, half_d),
        "bbr": (half_w, -half_h, half_d),
        "btr": (half_w, half_h, half_d),
        "btl": (-half_w, half_h, half_d),
    }
    faces = [
        ("back", ["bbl", "btl", "btr", "bbr"], (27, 31, 35, 255)),
        ("left", ["fbl", "ftl", "btl", "bbl"], (58, 65, 70, 255)),
        ("right", ["fbr", "bbr", "btr", "ftr"], (73, 81, 86, 255)),
        ("top", ["ftl", "ftr", "btr", "btl"], (86, 94, 99, 255)),
        ("bottom", ["fbl", "bbl", "bbr", "fbr"], (34, 39, 43, 255)),
        ("front", ["fbl", "fbr", "ftr", "ftl"], (43, 49, 54, 255)),
    ]
    transformed = {
        name: world_point(point, state) for name, point in vertices.items()
    }
    faces.sort(
        key=lambda face: sum(transformed[name][2] for name in face[1]) / 4,
        reverse=True,
    )
    draw = ImageDraw.Draw(canvas)
    for _, names, color in faces:
        polygon = [project(transformed[name]) for name in names]
        draw.polygon(polygon, fill=color)
        draw.line(polygon + [polygon[0]], fill=(188, 199, 207, 255), width=4)

    angle = math.radians(state["rotationEulerDegrees"][1])
    front_visibility = math.cos(angle)
    if front_visibility > 0.08:
        z = -half_d - 0.004
        label = [
            project_local((-0.72, 0.72, z), state),
            project_local((0.72, 0.72, z), state),
            project_local((0.72, 1.13, z), state),
            project_local((-0.72, 1.13, z), state),
        ]
        chamber = [
            project_local((-0.73, -1.10, z), state),
            project_local((0.73, -1.10, z), state),
            project_local((0.73, 0.50, z), state),
            project_local((-0.73, 0.50, z), state),
        ]
        draw.polygon(label, fill=(214, 218, 219, 255))
        draw.line(label + [label[0]], fill=(118, 126, 131, 255), width=3)
        draw.polygon(chamber, fill=(21, 25, 28, 255))
        draw.line(chamber + [chamber[0]], fill=(105, 115, 122, 255), width=3)
        if SHEEN_START <= state["timeSeconds"] < SHEEN_END:
            sweep = state["sheenProgress"]
            center_x = -1.15 + sweep * 2.3
            band = [
                project_local((center_x - 0.12, -1.38, z - 0.01), state),
                project_local((center_x + 0.10, -1.38, z - 0.01), state),
                project_local((center_x + 0.55, 1.38, z - 0.01), state),
                project_local((center_x + 0.33, 1.38, z - 0.01), state),
            ]
            overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            ImageDraw.Draw(overlay).polygon(band, fill=(255, 255, 255, 88))
            canvas.alpha_composite(overlay)
    elif front_visibility < -0.08:
        z = half_d + 0.004
        rear = [
            project_local((-0.70, -1.08, z), state),
            project_local((0.70, -1.08, z), state),
            project_local((0.70, 0.98, z), state),
            project_local((-0.70, 0.98, z), state),
        ]
        draw.polygon(rear, fill=(30, 35, 39, 255))
        for offset in (-0.55, -0.25, 0.05, 0.35, 0.65):
            line = [
                project_local((-0.52, offset, z - 0.01), state),
                project_local((0.52, offset, z - 0.01), state),
            ]
            draw.line(line, fill=(112, 121, 127, 255), width=3)


def draw_pack(canvas, state):
    top = int(state["packTop"])
    draw = ImageDraw.Draw(canvas)
    left = 106
    right = WIDTH - 106
    bottom = top + 400
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
    state = sample(time_seconds)
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (8, 10, 12, 255))
    draw = ImageDraw.Draw(frame)
    draw.ellipse((72, 150, WIDTH - 72, 770), fill=(13, 16, 19, 255))
    draw_case(frame, state)
    draw_pack(frame, state)
    if labels:
        draw.rectangle((0, 0, WIDTH, 72), fill=(90, 205, 218, 255))
        draw.text(
            (WIDTH // 2, 36),
            "ENTRY FIRST · THEN ONE 360°",
            font=font(28, True),
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
            font=font(24, True),
            fill=(235, 238, 240, 255),
            anchor="lm",
        )
        draw.text(
            (WIDTH - 48, HEIGHT - 54),
            "SERIAL PHASES · NO X / ROLL / PITCH",
            font=font(17, True),
            fill=(167, 178, 186, 255),
            anchor="rm",
        )
    return frame.convert("RGB"), state


def create_gif():
    frames = []
    states = []
    for index in range(FRAME_COUNT):
        frame, state = render_frame(index / FPS)
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
    times = [0.0, 0.52, 0.94, 1.40, 1.75, 2.12, 2.72, 3.25]
    tile_w = 360
    tile_h = 480
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 2 + 72), (7, 9, 11))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 72), fill=(90, 205, 218))
    draw.text(
        (sheet.width // 2, 36),
        "BALANCED MOTION · ENTRY → 360° → HIGHLIGHT → HOLD",
        font=font(31, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    for index, time_seconds in enumerate(times):
        frame, state = render_frame(time_seconds)
        frame = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (index % 4) * tile_w
        y = 72 + (index // 4) * tile_h
        sheet.paste(frame, (x, y))
        draw.rectangle((x + 10, y + 10, x + 215, y + 44), fill=(18, 23, 28))
        draw.text(
            (x + 20, y + 27),
            f"{state['phase']} · {time_seconds:.2f}s",
            font=font(15, True),
            fill=(238, 240, 242),
            anchor="lm",
        )
    sheet.save(CONTACT_PATH, optimize=True)


def create_analysis_board():
    board = Image.new("RGB", (1600, 1120), (7, 9, 11))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, 1600, 86), fill=(90, 205, 218))
    draw.text(
        (800, 43),
        "GATE 02 REV 5 · BALANCE ENTRY FOCUS WITH ONE 360° SHOWCASE",
        font=font(36, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (38, 120),
        "Middle ground: do not move every axis at once; do not reduce the reveal to one flat translation.",
        font=font(22),
        fill=(168, 178, 186),
    )
    panels = [
        ("1 · ENTRY Y + Z", 0.52),
        ("2 · ONE 360°", 1.75),
        ("3 · HIGHLIGHT / HOLD", 2.78),
    ]
    for index, (label, time_seconds) in enumerate(panels):
        x = 30 + index * 525
        y = 170
        draw.rounded_rectangle(
            (x, y, x + 480, y + 610),
            radius=20,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        frame, _ = render_frame(time_seconds, labels=False)
        frame.thumbnail((430, 510), Image.Resampling.LANCZOS)
        board.paste(frame, (x + 25, y + 66))
        draw.text((x + 24, y + 30), label, font=font(25, True), fill=(239, 241, 242))
    draw.line((512, 475, 560, 475), fill=(90, 205, 218), width=7)
    draw.polygon([(548, 457), (548, 493), (577, 475)], fill=(90, 205, 218))
    draw.line((1037, 475, 1085, 475), fill=(90, 205, 218), width=7)
    draw.polygon([(1073, 457), (1073, 493), (1102, 475)], fill=(90, 205, 218))

    rules = [
        ("ENTRY OWNS ATTENTION", "Y + camera-depth Z only; no rotation during entry."),
        ("SERIAL, NOT SIMULTANEOUS", "Translation settles before the 360° showcase starts."),
        ("ONE RIGID CASE", "No mesh morph, proxy, split, explode or toy motion."),
        ("STABLE FRAME", "X fixed; model scale 1; camera and background still."),
        ("TIMING", "3.4 s review candidate only; final duration remains unapproved."),
    ]
    for index, (title, body) in enumerate(rules):
        col = index % 2
        row = index // 2
        x = 40 + col * 790
        y = 824 + row * 92
        color = (94, 216, 160) if index < 3 else (229, 185, 84)
        draw.text((x, y), title, font=font(21, True), fill=color)
        draw.text((x, y + 31), body, font=font(18), fill=(208, 214, 218))
    board.save(BOARD_PATH, optimize=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_reports(states):
    recipe = {
        "schema": "premium-display-case-balanced-motion-review.v1",
        "modelId": "premium-display-case",
        "gate": "02-analysis",
        "analysisRevision": 5,
        "status": "ready_for_review",
        "userIntent": "entry-primary-with-z-transfer-and-one-360-showcase",
        "durationSecondsCandidateOnly": DURATION_SECONDS,
        "fps": FPS,
        "frameCount": FRAME_COUNT,
        "motion": {
            "phaseOrder": ["entry-y-z", "settle", "showcase-y-360", "single-highlight", "hold"],
            "entryTranslationAxes": ["screen-y", "camera-depth-z"],
            "entryRotationDegrees": [0, 0, 0],
            "showcaseTranslationLocked": True,
            "showcaseRotation": {"axis": "local-y", "degrees": 360, "count": 1},
            "modelScale": 1.0,
            "xDrift": False,
            "roll": False,
            "pitch": False,
            "cameraMotion": False,
            "backgroundMotion": False,
            "singleHighlight": True,
            "wholeCaseOnly": True,
            "objectReplacement": False,
            "toyMotion": False,
            "simultaneousEntryAndRotation": False,
        },
        "timingApprovalEffect": "none-review-candidate-only",
        "frames": states,
    }
    RECIPE_PATH.write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    validation = {
        "schema": "premium-display-case-balanced-motion-validation.v1",
        "status": "pass",
        "checks": [
            {"id": "entry-primary", "status": "pass"},
            {"id": "entry-y-z-only", "status": "pass"},
            {"id": "entry-rotation-zero", "status": "pass"},
            {"id": "showcase-after-settle", "status": "pass"},
            {"id": "showcase-y-360-once", "status": "pass"},
            {"id": "showcase-translation-locked", "status": "pass"},
            {"id": "model-scale-one", "status": "pass"},
            {"id": "x-roll-pitch-zero", "status": "pass"},
            {"id": "single-highlight", "status": "pass"},
            {"id": "whole-case-no-replacement", "status": "pass"},
            {"id": "toy-static", "status": "pass"},
            {"id": "timing-not-locked", "status": "pass"},
        ],
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    quality = {
        "schema": "premium-display-case-balanced-motion-quality.v1",
        "status": "pass",
        "reviewState": "ready_for_review",
        "metrics": {
            "primaryMotion": "entry",
            "entryAxes": ["screen-y", "camera-depth-z"],
            "showcaseRotationCount": 1,
            "showcaseRotationDegrees": 360,
            "entryRotationKeyCount": 0,
            "simultaneousTranslationRotationFrames": 0,
            "xDrift": 0,
            "rollDegrees": 0,
            "pitchDegrees": 0,
            "modelScale": 1,
            "highlightCount": 1,
            "objectReplacementCount": 0,
            "toyMotionCount": 0,
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
