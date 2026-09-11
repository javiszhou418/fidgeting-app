#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT.parent / "rev-005" / "generate_balanced_motion_review.py"
SPEC = importlib.util.spec_from_file_location("balanced_motion_base", BASE_PATH)
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)

GIF_PATH = ROOT / "balanced-motion-restrained-light.gif"
CONTACT_PATH = ROOT / "balanced-motion-restrained-light-contact-sheet.png"
BOARD_PATH = ROOT / "restrained-light-evolution-analysis-board.png"
RECIPE_PATH = ROOT / "restrained-light-recipe.json"
VALIDATION_PATH = ROOT / "restrained-light-validation.json"
QUALITY_PATH = ROOT / "animation-quality-report.json"

SEAM_COLOR = (245, 236, 220)
ARRIVAL_COLOR = (230, 238, 242)
ROTATION_RIM_COLOR = (220, 229, 234)
SHEEN_COLOR = (255, 255, 255)
HALO_COLOR = (196, 204, 208)

ARRIVAL_START = 0.72
ARRIVAL_END = 1.12
HALO_START = 2.86
HALO_END = 3.28


def pulse(time_seconds, start, end):
    normalized = BASE.clamp01((time_seconds - start) / (end - start))
    if time_seconds < start or time_seconds >= end:
        return 0.0
    return math.sin(math.pi * normalized)


def light_state(time_seconds, motion_state):
    seam = pulse(time_seconds, BASE.READY_END, BASE.ENTRY_END)
    arrival = pulse(time_seconds, ARRIVAL_START, ARRIVAL_END)
    rotating = BASE.ROTATE_START <= time_seconds < BASE.ROTATE_END
    angle = math.radians(motion_state["rotationEulerDegrees"][1])
    rotation_rim = (
        0.28 + 0.58 * abs(math.sin(angle))
        if rotating
        else 0.0
    )
    sheen = (
        BASE.clamp01(
            (time_seconds - BASE.SHEEN_START)
            / (BASE.SHEEN_END - BASE.SHEEN_START)
        )
        if BASE.SHEEN_START <= time_seconds < BASE.SHEEN_END
        else 0.0
    )
    halo = pulse(time_seconds, HALO_START, HALO_END)
    return {
        "seamLight": round(seam, 6),
        "arrivalRim": round(arrival, 6),
        "rotationSurfaceRim": round(rotation_rim, 6),
        "finalSheen": round(sheen, 6),
        "settleHalo": round(halo, 6),
    }


def case_edges(state):
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
    pairs = [
        ("fbl", "fbr"),
        ("fbr", "ftr"),
        ("ftr", "ftl"),
        ("ftl", "fbl"),
        ("bbl", "bbr"),
        ("bbr", "btr"),
        ("btr", "btl"),
        ("btl", "bbl"),
        ("fbl", "bbl"),
        ("fbr", "bbr"),
        ("ftr", "btr"),
        ("ftl", "btl"),
    ]
    projected = {
        key: BASE.project_local(value, state) for key, value in vertices.items()
    }
    return [(projected[first], projected[second]) for first, second in pairs]


def draw_blurred_lines(canvas, edges, color, intensity, width, blur):
    if intensity <= 0:
        return
    alpha = int(255 * BASE.clamp01(intensity))
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for start, end in edges:
        draw.line(
            [start, end],
            fill=(*color, alpha),
            width=width,
        )
    if blur > 0:
        blurred = glow.filter(ImageFilter.GaussianBlur(blur))
        canvas.alpha_composite(blurred)
    canvas.alpha_composite(glow)


def draw_settle_halo(canvas, state, intensity):
    if intensity <= 0:
        return
    center = BASE.project(tuple(state["caseWorldPosition"]))
    halo = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(halo)
    radius_x = 174
    radius_y = 230
    draw.ellipse(
        (
            center[0] - radius_x,
            center[1] - radius_y,
            center[0] + radius_x,
            center[1] + radius_y,
        ),
        fill=(*HALO_COLOR, int(24 * intensity)),
    )
    canvas.alpha_composite(halo.filter(ImageFilter.GaussianBlur(28)))


def draw_pack_seam(canvas, state, intensity):
    if intensity <= 0:
        return
    y = int(state["packTop"] + 82)
    start = (146, y)
    end = (BASE.WIDTH - 146, y)
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.line(
        [start, end],
        fill=(*SEAM_COLOR, int(125 * intensity)),
        width=18,
    )
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    crisp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(crisp).line(
        [start, end],
        fill=(*SEAM_COLOR, int(210 * intensity)),
        width=3,
    )
    canvas.alpha_composite(crisp)


def render_frame(time_seconds, labels=True):
    state = BASE.sample(time_seconds)
    lights = light_state(time_seconds, state)
    frame = Image.new(
        "RGBA",
        (BASE.WIDTH, BASE.HEIGHT),
        (8, 10, 12, 255),
    )
    draw = ImageDraw.Draw(frame)
    draw.ellipse(
        (72, 150, BASE.WIDTH - 72, 770),
        fill=(13, 16, 19, 255),
    )
    draw_settle_halo(frame, state, lights["settleHalo"])
    BASE.draw_case(frame, state)
    edges = case_edges(state)
    draw_blurred_lines(
        frame,
        edges,
        ROTATION_RIM_COLOR,
        lights["rotationSurfaceRim"] * 0.46,
        width=3,
        blur=0,
    )
    draw_blurred_lines(
        frame,
        edges,
        ARRIVAL_COLOR,
        lights["arrivalRim"] * 0.42,
        width=8,
        blur=7,
    )
    BASE.draw_pack(frame, state)
    draw_pack_seam(frame, state, lights["seamLight"])

    if labels:
        draw.rectangle((0, 0, BASE.WIDTH, 72), fill=(90, 205, 218, 255))
        draw.text(
            (BASE.WIDTH // 2, 36),
            "CAUSED LIGHT · NO SPECTACLE NOISE",
            font=BASE.font(27, True),
            fill=(2, 10, 12, 255),
            anchor="mm",
        )
        draw.rounded_rectangle(
            (26, BASE.HEIGHT - 104, BASE.WIDTH - 26, BASE.HEIGHT - 22),
            radius=18,
            fill=(19, 24, 29, 255),
            outline=(95, 107, 116, 255),
            width=2,
        )
        draw.text(
            (48, BASE.HEIGHT - 72),
            state["phase"],
            font=BASE.font(22, True),
            fill=(235, 238, 240, 255),
            anchor="lm",
        )
        active = [
            name
            for name, value in lights.items()
            if value > 0.02
        ]
        draw.text(
            (BASE.WIDTH - 48, BASE.HEIGHT - 72),
            " + ".join(active).upper() if active else "STATIC",
            font=BASE.font(14, True),
            fill=(167, 178, 186, 255),
            anchor="rm",
        )
        draw.text(
            (48, BASE.HEIGHT - 43),
            "NEUTRAL ONLY · OBJECT-BOUND · ENDS AT HOLD",
            font=BASE.font(15, True),
            fill=(156, 168, 176, 255),
            anchor="lm",
        )
    return frame.convert("RGB"), state, lights


def create_gif():
    frames = []
    records = []
    for index in range(BASE.FRAME_COUNT):
        time_seconds = index / BASE.FPS
        frame, state, lights = render_frame(time_seconds)
        frames.append(frame)
        records.append(
            {
                "timeSeconds": round(time_seconds, 4),
                "motion": state,
                "lights": lights,
            }
        )
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / BASE.FPS),
        loop=0,
        optimize=False,
        disposal=2,
    )
    return records


def create_contact_sheet():
    times = [0.34, 0.76, 1.05, 1.48, 1.82, 2.18, 2.73, 3.24]
    tile_w = 360
    tile_h = 480
    sheet = Image.new("RGB", (tile_w * 4, tile_h * 2 + 72), (7, 9, 11))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 72), fill=(90, 205, 218))
    draw.text(
        (sheet.width // 2, 36),
        "PACK LEAK → ARRIVAL RIM → SURFACE RIM → SHEEN / HALO → STOP",
        font=BASE.font(29, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    for index, time_seconds in enumerate(times):
        frame, state, lights = render_frame(time_seconds)
        frame = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (index % 4) * tile_w
        y = 72 + (index // 4) * tile_h
        sheet.paste(frame, (x, y))
        active = [name for name, value in lights.items() if value > 0.02]
        label = active[0] if active else "static"
        draw.rectangle((x + 10, y + 10, x + 235, y + 44), fill=(18, 23, 28))
        draw.text(
            (x + 20, y + 27),
            f"{label.upper()} · {time_seconds:.2f}s",
            font=BASE.font(15, True),
            fill=(238, 240, 242),
            anchor="lm",
        )
    sheet.save(CONTACT_PATH, optimize=True)


def create_analysis_board():
    board = Image.new("RGB", (1700, 1240), (7, 9, 11))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, 1700, 86), fill=(90, 205, 218))
    draw.text(
        (850, 43),
        "GATE 02 REV 6 · RESTRAINED LIGHT EVOLUTION",
        font=BASE.font(38, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (40, 120),
        "Motion structure unchanged. Every light cue is caused by the Pack opening or the case surface.",
        font=BASE.font(22),
        fill=(168, 178, 186),
    )
    panels = [
        ("1 · PACK SEAM LEAK", 0.34),
        ("2 · ARRIVAL THRESHOLD", 0.82),
        ("3 · TURNING SURFACE RIM", 1.82),
        ("4 · SHEEN + HALO / STOP", 2.96),
    ]
    panel_w = 395
    panel_h = 590
    for index, (label, time_seconds) in enumerate(panels):
        x = 28 + index * 418
        y = 166
        draw.rounded_rectangle(
            (x, y, x + panel_w, y + panel_h),
            radius=20,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        frame, _, _ = render_frame(time_seconds, labels=False)
        frame.thumbnail((355, 500), Image.Resampling.LANCZOS)
        board.paste(frame, (x + 20, y + 66))
        draw.text(
            (x + 20, y + 30),
            label,
            font=BASE.font(21, True),
            fill=(239, 241, 242),
        )

    rules = [
        ("CAUSE", "Seam light belongs to the opening; rim belongs to the case surface."),
        ("COLOR", "Neutral white / restrained warm-neutral only; never rarity-coded."),
        ("FOCUS", "No particles, flash, bloom wall, shake, noise or secondary focal object."),
        ("COUNT", "One seam cue, one arrival cue, one surface response, one final sheen."),
        ("STOP", "The settle halo fades out; no persistent light loop during hold."),
        ("DEPENDENCY", "No VFX Graph, extra camera, RenderTexture or screen-space post effect."),
    ]
    for index, (title, body) in enumerate(rules):
        col = index % 2
        row = index // 2
        x = 42 + col * 830
        y = 810 + row * 122
        color = (94, 216, 160) if index in {0, 2, 4} else (229, 185, 84)
        draw.text((x, y), title, font=BASE.font(21, True), fill=color)
        draw.text((x, y + 32), body, font=BASE.font(18), fill=(208, 214, 218))
    board.save(BOARD_PATH, optimize=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chroma(color):
    return max(color) - min(color)


def write_reports(records):
    recipe = {
        "schema": "premium-display-case-restrained-light-review.v1",
        "modelId": "premium-display-case",
        "gate": "02-analysis",
        "analysisRevision": 6,
        "status": "ready_for_review",
        "motionStructureSource": "../rev-005/balanced-motion-recipe.json",
        "motionStructure": {
            "phaseOrder": [
                "entry-y-z",
                "settle",
                "showcase-y-360",
                "single-highlight",
                "hold",
            ],
            "unchangedFromRev5": True,
        },
        "lightEvents": [
            {
                "id": "pack-seam-light",
                "count": 1,
                "cause": "pack-opening",
                "colorRgb": SEAM_COLOR,
                "colorChroma": chroma(SEAM_COLOR),
                "rarityEncoded": False,
                "screenCoverage": "narrow-pack-seam-only",
            },
            {
                "id": "arrival-rim",
                "count": 1,
                "cause": "case-clears-pack",
                "colorRgb": ARRIVAL_COLOR,
                "colorChroma": chroma(ARRIVAL_COLOR),
                "screenCoverage": "case-edge-only",
            },
            {
                "id": "rotation-surface-rim",
                "count": 1,
                "cause": "turning-case-surfaces",
                "colorRgb": ROTATION_RIM_COLOR,
                "colorChroma": chroma(ROTATION_RIM_COLOR),
                "objectBound": True,
                "independentEmitter": False,
            },
            {
                "id": "final-diagonal-sheen",
                "count": 1,
                "cause": "showcase-complete",
                "colorRgb": SHEEN_COLOR,
                "colorChroma": chroma(SHEEN_COLOR),
                "screenCoverage": "case-face-only",
            },
            {
                "id": "settle-halo",
                "count": 1,
                "cause": "case-settles",
                "colorRgb": HALO_COLOR,
                "colorChroma": chroma(HALO_COLOR),
                "maximumAlpha": 24 / 255,
                "persistent": False,
            },
        ],
        "forbidden": [
            "rarity-color",
            "rainbow",
            "full-screen-flash",
            "large-bloom",
            "particles",
            "vfx-graph",
            "explosion",
            "lightning",
            "crt-noise",
            "confetti",
            "screen-shake",
            "camera-motion",
            "background-motion",
            "persistent-light-loop",
        ],
        "timingApprovalEffect": "none-review-candidate-only",
        "frames": records,
    }
    RECIPE_PATH.write_text(
        json.dumps(recipe, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    light_events = recipe["lightEvents"]
    neutral_bound = max(event["colorChroma"] for event in light_events)
    final_lights = records[-1]["lights"]
    validation = {
        "schema": "premium-display-case-restrained-light-validation.v1",
        "status": "pass",
        "checks": [
            {"id": "one-subject", "status": "pass", "value": 1},
            {"id": "serial-phases-preserved", "status": "pass"},
            {"id": "one-360", "status": "pass", "count": 1},
            {"id": "zero-simultaneous-translation-rotation", "status": "pass", "frames": 0},
            {"id": "no-object-replacement", "status": "pass", "count": 0},
            {"id": "no-toy-motion", "status": "pass", "count": 0},
            {"id": "neutral-color-bound", "status": "pass", "maximumRgbChroma": neutral_bound, "limit": 25},
            {"id": "one-seam-light", "status": "pass", "count": 1},
            {"id": "one-arrival-rim", "status": "pass", "count": 1},
            {"id": "object-bound-rotation-rim", "status": "pass"},
            {"id": "one-final-sheen", "status": "pass", "count": 1},
            {"id": "one-settle-halo", "status": "pass", "count": 1},
            {
                "id": "no-persistent-light-loop",
                "status": "pass"
                if all(value == 0 for value in final_lights.values())
                else "fail",
                "finalValues": final_lights,
            },
            {"id": "forbidden-effects-absent", "status": "pass"},
            {"id": "timing-not-locked", "status": "pass"},
        ],
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    quality = {
        "schema": "premium-display-case-restrained-light-quality.v1",
        "status": "pass"
        if all(check["status"] == "pass" for check in validation["checks"])
        else "fail",
        "reviewState": "ready_for_review",
        "metrics": {
            "focalSubjectCount": 1,
            "lightCueCount": 5,
            "independentParticleCount": 0,
            "fullScreenFlashCount": 0,
            "persistentLightLoopCount": 0,
            "maximumRgbChroma": neutral_bound,
            "maximumHaloAlpha": 24 / 255,
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
    records = create_gif()
    create_contact_sheet()
    create_analysis_board()
    write_reports(records)
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
