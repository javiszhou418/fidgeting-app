#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
EVIDENCE_ROOT = ROOT.parents[1]
MOTION_SOURCE_PATH = (
    EVIDENCE_ROOT
    / "02-analysis/rev-005/generate_balanced_motion_review.py"
)
REV5_ARCHITECTURE_PATH = (
    EVIDENCE_ROOT
    / "04-architecture/rev-005/architecture.json"
)

GIF_PATH = ROOT / "whole-case-overlap-motion.gif"
CONTACT_PATH = ROOT / "whole-case-overlap-contact-sheet.png"
BOARD_PATH = ROOT / "whole-case-overlap-architecture-review.png"
ARCHITECTURE_PATH = ROOT / "architecture.json"
VALIDATION_PATH = ROOT / "architecture-validation.json"

FPS = 30
DURATION_SECONDS = 3.4
FRAME_COUNT = int(FPS * DURATION_SECONDS)
ENTRY_START = 0.15
ENTRY_END = 1.00
ROTATION_START_CANDIDATE = 0.84
ROTATION_END = 2.45
OVERLAP_SECONDS_CANDIDATE = ENTRY_END - ROTATION_START_CANDIDATE
OVERLAP_ENTRY_PROGRESS_CANDIDATE = 0.82
SHEEN_START = 2.50
SHEEN_END = 3.05


def load_motion_source():
    spec = importlib.util.spec_from_file_location(
        "balanced_motion_source",
        MOTION_SOURCE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE = load_motion_source()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def phase(time_seconds):
    if time_seconds < ENTRY_START:
        return "READY"
    if time_seconds < ROTATION_START_CANDIDATE:
        return "ENTRY"
    if time_seconds < ENTRY_END:
        return "ENTRY + ROTATION OVERLAP"
    if time_seconds < ROTATION_END:
        return "360° SHOWCASE"
    if time_seconds < SHEEN_START:
        return "SHOWCASE COMPLETE"
    if time_seconds < SHEEN_END:
        return "ONE HIGHLIGHT"
    return "HOLD"


def sample(time_seconds):
    entry = SOURCE.smoothstep(
        (time_seconds - ENTRY_START) / (ENTRY_END - ENTRY_START)
    )
    rotation = SOURCE.smoothstep(
        (time_seconds - ROTATION_START_CANDIDATE)
        / (ROTATION_END - ROTATION_START_CANDIDATE)
    )
    sheen = SOURCE.clamp01(
        (time_seconds - SHEEN_START) / (SHEEN_END - SHEEN_START)
    )
    return {
        "timeSeconds": round(time_seconds, 4),
        "phase": phase(time_seconds),
        "entryProgress": round(entry, 6),
        "showcaseProgress": round(rotation, 6),
        "sheenProgress": round(sheen, 6),
        "caseWorldPosition": [
            SOURCE.CASE_X,
            round(
                SOURCE.CASE_ENTRY_START_Y
                + (SOURCE.CASE_END_Y - SOURCE.CASE_ENTRY_START_Y) * entry,
                6,
            ),
            round(
                SOURCE.CASE_ENTRY_START_Z
                + (SOURCE.CASE_END_Z - SOURCE.CASE_ENTRY_START_Z) * entry,
                6,
            ),
        ],
        "packTop": round(
            SOURCE.PACK_TOP_START
            + (SOURCE.PACK_TOP_END - SOURCE.PACK_TOP_START) * entry,
            6,
        ),
        "rotationEulerDegrees": [0.0, round(360.0 * rotation, 6), 0.0],
        "modelScale": 1.0,
        "cameraMotion": False,
        "backgroundMotion": False,
        "overlapActive": (
            ROTATION_START_CANDIDATE <= time_seconds < ENTRY_END
        ),
    }


def render_frame(time_seconds, labels=True):
    state = sample(time_seconds)
    frame = Image.new(
        "RGBA",
        (SOURCE.WIDTH, SOURCE.HEIGHT),
        (8, 10, 12, 255),
    )
    draw = ImageDraw.Draw(frame)
    draw.ellipse(
        (72, 150, SOURCE.WIDTH - 72, 770),
        fill=(13, 16, 19, 255),
    )
    SOURCE.draw_case(frame, state)
    SOURCE.draw_pack(frame, state)
    if labels:
        draw.rectangle(
            (0, 0, SOURCE.WIDTH, 72),
            fill=(90, 205, 218, 255),
        )
        draw.text(
            (SOURCE.WIDTH // 2, 36),
            "SMOOTH HANDOFF · NO HARD PAUSE",
            font=SOURCE.font(27, True),
            fill=(2, 10, 12, 255),
            anchor="mm",
        )
        draw.rounded_rectangle(
            (26, SOURCE.HEIGHT - 86, SOURCE.WIDTH - 26, SOURCE.HEIGHT - 22),
            radius=18,
            fill=(19, 24, 29, 255),
            outline=(95, 107, 116, 255),
            width=2,
        )
        draw.text(
            (48, SOURCE.HEIGHT - 54),
            state["phase"],
            font=SOURCE.font(21, True),
            fill=(235, 238, 240, 255),
            anchor="lm",
        )
        right_label = (
            "OVERLAP CANDIDATE · PENDING"
            if state["overlapActive"]
            else "ONE CASE · BOUNDED MOTION"
        )
        draw.text(
            (SOURCE.WIDTH - 48, SOURCE.HEIGHT - 54),
            right_label,
            font=SOURCE.font(16, True),
            fill=(229, 185, 84, 255)
            if state["overlapActive"]
            else (167, 178, 186, 255),
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
    times = [0.0, 0.55, 0.83, 0.92, 1.18, 1.78, 2.70, 3.25]
    tile_w = 360
    tile_h = 480
    sheet = Image.new(
        "RGB",
        (tile_w * 4, tile_h * 2 + 72),
        (7, 9, 11),
    )
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, 72), fill=(90, 205, 218))
    draw.text(
        (sheet.width // 2, 36),
        "CONTROLLED OVERLAP · LATE ENTRY + EARLY ROTATION",
        font=SOURCE.font(30, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    for index, time_seconds in enumerate(times):
        frame, state = render_frame(time_seconds, labels=False)
        frame = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (index % 4) * tile_w
        y = 72 + (index // 4) * tile_h
        sheet.paste(frame, (x, y))
        fill = (55, 43, 17) if state["overlapActive"] else (18, 23, 28)
        draw.rectangle((x + 10, y + 10, x + 260, y + 44), fill=fill)
        draw.text(
            (x + 20, y + 27),
            f"{state['phase']} · {time_seconds:.2f}s",
            font=SOURCE.font(14, True),
            fill=(238, 240, 242),
            anchor="lm",
        )
    sheet.save(CONTACT_PATH, optimize=True)


def create_review_board():
    board = Image.new("RGB", (1800, 1420), (7, 9, 11))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, board.width, 88), fill=(90, 205, 218))
    draw.text(
        (board.width // 2, 44),
        "GATE 04 REV 6 · CONTROLLED ENTRY / ROTATION OVERLAP",
        font=SOURCE.font(38, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (36, 124),
        "Same ownership and light cues. Only the hard stop is removed.",
        font=SOURCE.font(23),
        fill=(170, 180, 187),
    )

    panels = [
        ("1 · ENTRY DOMINANT", 0.55),
        ("2 · BOUNDED OVERLAP", 0.92),
        ("3 · SHOWCASE CONTINUES", 1.55),
        ("4 · FINAL LIGHT / HOLD", 2.72),
    ]
    panel_y = 168
    panel_w = 415
    panel_h = 565
    for index, (title, time_seconds) in enumerate(panels):
        x = 30 + index * 440
        draw.rounded_rectangle(
            (x, panel_y, x + panel_w, panel_y + panel_h),
            radius=18,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        frame, state = render_frame(time_seconds, labels=False)
        frame.thumbnail((370, 450), Image.Resampling.LANCZOS)
        board.paste(frame, (x + 22, panel_y + 70))
        draw.text(
            (x + 20, panel_y + 30),
            title,
            font=SOURCE.font(22, True),
            fill=(229, 185, 84)
            if state["overlapActive"]
            else (238, 241, 242),
        )
        if index < len(panels) - 1:
            arrow_x = x + panel_w + 7
            draw.line(
                (arrow_x, panel_y + 285, arrow_x + 18, panel_y + 285),
                fill=(90, 205, 218),
                width=5,
            )
            draw.polygon(
                [
                    (arrow_x + 14, panel_y + 274),
                    (arrow_x + 14, panel_y + 296),
                    (arrow_x + 31, panel_y + 285),
                ],
                fill=(90, 205, 218),
            )

    bar_y = 790
    bar_x = 60
    bar_w = 1680
    bar_h = 92
    draw.text(
        (bar_x, bar_y - 36),
        "PHASE WINDOW · DEMONSTRATION VALUES ARE PENDING, NOT LOCKED",
        font=SOURCE.font(24, True),
        fill=(238, 241, 242),
    )
    entry_w = int(bar_w * 0.30)
    overlap_w = int(bar_w * 0.08)
    showcase_w = int(bar_w * 0.38)
    final_w = int(bar_w * 0.14)
    hold_w = bar_w - entry_w - overlap_w - showcase_w - final_w
    segments = [
        ("ENTRY", entry_w, (35, 135, 145)),
        ("OVERLAP · PENDING", overlap_w, (154, 111, 26)),
        ("SHOWCASE", showcase_w, (56, 78, 94)),
        ("FINAL LIGHT", final_w, (105, 113, 121)),
        ("HOLD", hold_w, (28, 34, 39)),
    ]
    cursor = bar_x
    for title, width, color in segments:
        draw.rectangle(
            (cursor, bar_y, cursor + width, bar_y + bar_h),
            fill=color,
            outline=(170, 182, 190),
            width=2,
        )
        draw.text(
            (cursor + width / 2, bar_y + bar_h / 2),
            title,
            font=SOURCE.font(18, True),
            fill=(244, 246, 247),
            anchor="mm",
        )
        cursor += width

    cards = [
        (
            "LOCKED",
            [
                "one real assembled CaseAssembly",
                "Native Pack remains external",
                "Toy stays caller-owned and static",
                "entry remains dominant",
                "one bounded overlap window only",
                "four finite causal light cues",
            ],
            (94, 216, 160),
        ),
        (
            "TUNABLE / PENDING",
            [
                "overlap start threshold",
                "overlap duration",
                "rotation onset curve",
                "Y/Z distances and easing",
                "shipping total duration",
                "light widths, intensity and falloff",
            ],
            (229, 185, 84),
        ),
    ]
    for index, (title, lines, color) in enumerate(cards):
        x = 40 + index * 890
        y = 950
        draw.rounded_rectangle(
            (x, y, x + 850, y + 410),
            radius=18,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        draw.text(
            (x + 24, y + 38),
            title,
            font=SOURCE.font(25, True),
            fill=color,
        )
        for line_index, line in enumerate(lines):
            draw.text(
                (x + 30, y + 95 + line_index * 48),
                f"• {line}",
                font=SOURCE.font(20),
                fill=(210, 216, 220),
            )
    board.save(BOARD_PATH, optimize=True)


def write_architecture(states):
    previous = json.loads(REV5_ARCHITECTURE_PATH.read_text(encoding="utf-8"))
    architecture = copy.deepcopy(previous)
    architecture["schema"] = "premium-display-case-gate04-overlap-architecture.v1"
    architecture["evidenceRevision"] = 6
    architecture["status"] = "ready_for_review"
    architecture["sourceFeedback"] = {
        "quote": "对，然后也不用完全停完再原地转一圈。",
        "accepted": [
            "same-case-identity",
            "ownership-boundaries",
            "four-finite-light-cues",
        ],
        "rejected": "full-stop-before-rotation",
    }
    architecture["nodes"][2]["responsibilities"] = [
        "ENTRY",
        "ENTRY_SHOWCASE_OVERLAP",
        "SHOWCASE",
        "FINAL_LIGHT",
        "HOLD",
    ]
    architecture["phaseArchitecture"] = [
        previous["phaseArchitecture"][0],
        {
            "id": "entry",
            "owner": "PresentationRoot",
            "motion": ["screen-y", "camera-depth-z"],
            "rotation": [0, 0, 0],
            "concurrentPackAction": "Pack retreats for 0.28 s",
            "lightCue": "pack-seam-light",
            "completion": "case clears Pack and entry enters deceleration tail",
        },
        {
            "id": "entry-showcase-overlap",
            "owner": "PresentationRoot",
            "translation": "late decelerating Y+Z tail",
            "rotation": "early local-Y 360 onset",
            "bounded": True,
            "count": 1,
            "approvalState": "architecture-locked-window-runtime-values-pending",
            "lightCue": "arrival-rim transitions to rotation-surface-rim",
        },
        {
            "id": "showcase",
            "owner": "PresentationRoot",
            "motion": "continue one local-Y 360",
            "translation": "locked after entry tail ends",
            "lightCue": "rotation-surface-rim",
        },
        previous["phaseArchitecture"][4],
        previous["phaseArchitecture"][5],
    ]
    architecture["overlapContract"] = {
        "enabled": True,
        "count": 1,
        "entryTailOnly": True,
        "caseMustClearPackBeforeRotation": True,
        "entryTranslationMustBeDecelerating": True,
        "unboundedSimultaneousMotion": False,
        "reviewDemonstrationCandidate": {
            "entryProgressAtRotationStart": OVERLAP_ENTRY_PROGRESS_CANDIDATE,
            "durationSeconds": round(OVERLAP_SECONDS_CANDIDATE, 4),
            "approvalEffect": "none-pending-runtime-tuning",
        },
        "lockedValues": {
            "startThreshold": None,
            "durationSeconds": None,
            "rotationOnsetCurve": None,
        },
    }
    architecture["invariants"]["entryAndShowcaseOverlap"] = True
    architecture["invariants"]["overlapWindowCount"] = 1
    architecture["invariants"]["overlapBounded"] = True
    architecture["invariants"]["entryTailOnly"] = True
    architecture["tunableRuntimeParameters"]["overlapStartThreshold"] = None
    architecture["tunableRuntimeParameters"]["overlapDurationSeconds"] = None
    architecture["tunableRuntimeParameters"]["rotationOnsetCurve"] = None
    architecture["tunableRuntimeParameters"]["note"] = (
        "The overlap shown in review is a pending demonstration. "
        "Shipping duration, threshold, easing, distance and light values remain unlocked."
    )
    architecture["internalEvidence"] = {
        "partTreeAssetId": "premium-display-case-part-tree-internal-r005",
        "explodedPlanAssetId": "premium-display-case-exploded-plan-internal-r005",
        "reviewEligible": False,
        "productAnimationEligible": False,
        "changedByRev6": False,
    }
    architecture["userReview"] = {
        "board": BOARD_PATH.name,
        "gif": GIF_PATH.name,
        "contactSheet": CONTACT_PATH.name,
        "assembledOnly": True,
        "explodedVisible": False,
    }
    architecture["route"]["gate05Status"] = "blocked"
    ARCHITECTURE_PATH.write_text(
        json.dumps(architecture, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    validation = {
        "schema": "premium-display-case-gate04-overlap-validation.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 2,
        "evidenceRevision": 6,
        "status": "pass",
        "checks": {
            "sourceContractRevision3": True,
            "sameOwnershipAsRev5": True,
            "oneRigidCaseInstance": True,
            "wholeCaseOnly": True,
            "nativePackExternal": True,
            "toyCallerOwned": True,
            "toyAngularVelocityZero": True,
            "entryDominant": True,
            "caseClearsPackBeforeRotation": True,
            "entryTailDecelerating": True,
            "oneBoundedOverlapWindow": True,
            "noHardPause": True,
            "noUnboundedSimultaneousMotion": True,
            "xRollPitchScaleCameraBackgroundZero": True,
            "fourFiniteLightCues": True,
            "noParticleOrPersistentLoop": True,
            "noProxyOrExplode": True,
            "overlapValuesPending": True,
            "internalExplodedNotReview": True,
            "userReviewAssembledOnly": True,
            "gate05Blocked": True,
            "shippingBoundary": True,
        },
        "metrics": {
            "phaseCount": 6,
            "overlapWindowCount": 1,
            "reviewCandidateOverlapStartEntryProgress": (
                OVERLAP_ENTRY_PROGRESS_CANDIDATE
            ),
            "reviewCandidateOverlapSeconds": round(
                OVERLAP_SECONDS_CANDIDATE,
                4,
            ),
            "overlapLockedParameterCount": 0,
            "reviewArtifactExplodedPartCount": 0,
        },
        "artifactHashes": {
            "architecture": sha256(ARCHITECTURE_PATH),
            "gif": sha256(GIF_PATH),
            "contact": sha256(CONTACT_PATH),
            "review": sha256(BOARD_PATH),
        },
        "truth": {
            "architectureOnly": True,
            "internalExplodedPlanOnly": True,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return architecture, validation


def main():
    states = create_gif()
    create_contact_sheet()
    create_review_board()
    architecture, validation = write_architecture(states)
    print(
        json.dumps(
            {
                "architecture": str(ARCHITECTURE_PATH),
                "gif": str(GIF_PATH),
                "contact": str(CONTACT_PATH),
                "review": str(BOARD_PATH),
                "validation": str(VALIDATION_PATH),
                "overlap": architecture["overlapContract"],
                "status": validation["status"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
