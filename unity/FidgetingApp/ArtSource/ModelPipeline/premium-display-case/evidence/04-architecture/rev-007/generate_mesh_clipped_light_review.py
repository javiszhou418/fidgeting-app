#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
EVIDENCE_ROOT = ROOT.parents[1]
OVERLAP_SOURCE_PATH = (
    EVIDENCE_ROOT
    / "04-architecture/rev-006/generate_overlap_architecture_review.py"
)
REV6_ARCHITECTURE_PATH = (
    EVIDENCE_ROOT / "04-architecture/rev-006/architecture.json"
)

GIF_PATH = ROOT / "whole-case-mesh-clipped-light-motion.gif"
CONTACT_PATH = ROOT / "whole-case-mesh-clipped-light-contact-sheet.png"
BOARD_PATH = ROOT / "mesh-clipped-light-architecture-review.png"
ARCHITECTURE_PATH = ROOT / "architecture.json"
VALIDATION_PATH = ROOT / "architecture-validation.json"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OVERLAP = load_module(OVERLAP_SOURCE_PATH, "overlap_source")
SOURCE = OVERLAP.SOURCE
FPS = OVERLAP.FPS
DURATION_SECONDS = OVERLAP.DURATION_SECONDS
FRAME_COUNT = OVERLAP.FRAME_COUNT


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cue_strengths(state):
    entry = state["entryProgress"]
    rotation = state["showcaseProgress"]
    time_seconds = state["timeSeconds"]
    seam = max(0.0, 1.0 - abs(entry - 0.48) / 0.48)
    arrival = (
        max(0.0, 1.0 - abs(entry - 0.88) / 0.22)
        if 0.68 <= time_seconds < 1.12
        else 0.0
    )
    rotation_rim = (
        0.38 + 0.32 * abs(__import__("math").sin(rotation * __import__("math").pi * 2))
        if OVERLAP.ROTATION_START_CANDIDATE <= time_seconds < OVERLAP.ROTATION_END
        else 0.0
    )
    final_sheen = SOURCE.clamp01(
        (time_seconds - OVERLAP.SHEEN_START)
        / (OVERLAP.SHEEN_END - OVERLAP.SHEEN_START)
    )
    if not (OVERLAP.SHEEN_START <= time_seconds < OVERLAP.SHEEN_END):
        final_sheen = 0.0
    return {
        "packSeam": round(seam, 6),
        "arrivalRim": round(arrival, 6),
        "rotationRim": round(rotation_rim, 6),
        "finalSheen": round(final_sheen, 6),
    }


def bbox_from_mask(mask):
    return mask.getbbox() or (0, 0, 0, 0)


def add_inside_light(canvas, case_mask, state):
    cues = cue_strengths(state)
    case_light_alpha = Image.new("L", case_mask.size, 0)

    eroded = case_mask.filter(ImageFilter.MinFilter(13))
    inner_rim = ImageChops.subtract(case_mask, eroded)
    rim_strength = max(cues["arrivalRim"], cues["rotationRim"])
    if rim_strength > 0:
        rim_alpha = inner_rim.point(
            lambda value: round(value * min(0.46, 0.10 + 0.36 * rim_strength))
        )
        case_light_alpha = ImageChops.lighter(case_light_alpha, rim_alpha)

    if cues["finalSheen"] > 0:
        left, top, right, bottom = bbox_from_mask(case_mask)
        width = max(1, right - left)
        sweep_x = int(left - width * 0.40 + cues["finalSheen"] * width * 1.8)
        stripe = Image.new("L", case_mask.size, 0)
        stripe_draw = ImageDraw.Draw(stripe)
        stripe_draw.polygon(
            [
                (sweep_x - 20, top - 24),
                (sweep_x + 8, top - 24),
                (sweep_x + 86, bottom + 24),
                (sweep_x + 58, bottom + 24),
            ],
            fill=116,
        )
        clipped_stripe = ImageChops.multiply(stripe, case_mask)
        case_light_alpha = ImageChops.lighter(
            case_light_alpha,
            clipped_stripe,
        )

    light = Image.new("RGBA", canvas.size, (238, 244, 246, 0))
    light.putalpha(case_light_alpha)
    canvas.alpha_composite(light)

    inverted_mask = ImageChops.invert(case_mask)
    outside = ImageChops.multiply(case_light_alpha, inverted_mask)
    outside_pixels = sum(1 for value in outside.getdata() if value)
    return cues, case_light_alpha, outside_pixels


def draw_pack_and_seam(canvas, state, seam_strength):
    SOURCE.draw_pack(canvas, state)
    if seam_strength <= 0:
        return
    top = int(state["packTop"])
    left = 106
    right = SOURCE.WIDTH - 106
    seam = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(seam)
    alpha = round(110 * seam_strength)
    draw.rounded_rectangle(
        (left + 38, top + 75, right - 38, top + 91),
        radius=8,
        fill=(242, 238, 225, alpha),
    )
    canvas.alpha_composite(seam)


def render_frame(time_seconds, labels=True):
    state = OVERLAP.sample(time_seconds)
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

    case_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    case_state = dict(state)
    case_state["timeSeconds"] = -1.0
    case_state["sheenProgress"] = 0.0
    SOURCE.draw_case(case_layer, case_state)
    case_mask = case_layer.getchannel("A")
    frame.alpha_composite(case_layer)

    cues, case_light_alpha, outside_pixels = add_inside_light(
        frame,
        case_mask,
        state,
    )
    draw_pack_and_seam(frame, state, cues["packSeam"])

    if labels:
        draw = ImageDraw.Draw(frame)
        draw.rectangle(
            (0, 0, SOURCE.WIDTH, 72),
            fill=(90, 205, 218, 255),
        )
        draw.text(
            (SOURCE.WIDTH // 2, 36),
            "MESH-CLIPPED LIGHT · UNITY AUTHORED",
            font=SOURCE.font(26, True),
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
            font=SOURCE.font(20, True),
            fill=(235, 238, 240, 255),
            anchor="lm",
        )
        draw.text(
            (SOURCE.WIDTH - 48, SOURCE.HEIGHT - 54),
            "NO HALO OUTSIDE CASE",
            font=SOURCE.font(16, True),
            fill=(94, 216, 160, 255),
            anchor="rm",
        )
    return frame.convert("RGB"), {
        **state,
        "lightCues": cues,
        "caseLightOutsideMaskPixels": outside_pixels,
        "caseLightPixelCount": sum(
            1 for value in case_light_alpha.getdata() if value
        ),
    }


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
    times = [0.45, 0.83, 0.92, 1.36, 1.90, 2.68, 2.92, 3.25]
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
        "CASE LIGHT STAYS INSIDE THE CASE · PACK LIGHT STAYS IN THE SEAM",
        font=SOURCE.font(27, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    for index, time_seconds in enumerate(times):
        frame, state = render_frame(time_seconds, labels=False)
        frame = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
        x = (index % 4) * tile_w
        y = 72 + (index // 4) * tile_h
        sheet.paste(frame, (x, y))
        draw.rectangle((x + 10, y + 10, x + 276, y + 45), fill=(18, 23, 28))
        draw.text(
            (x + 20, y + 27),
            f"{state['phase']} · outside={state['caseLightOutsideMaskPixels']} px",
            font=SOURCE.font(13, True),
            fill=(238, 240, 242),
            anchor="lm",
        )
    sheet.save(CONTACT_PATH, optimize=True)


def create_review_board():
    board = Image.new("RGB", (1800, 1480), (7, 9, 11))
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, board.width, 88), fill=(90, 205, 218))
    draw.text(
        (board.width // 2, 44),
        "GATE 04 REV 7 · MESH-CLIPPED LIGHT + UNITY RUNTIME OWNERSHIP",
        font=SOURCE.font(36, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (36, 124),
        "Motion relationship stays. External halo is removed. Exact runtime timing and light values stay tunable.",
        font=SOURCE.font(22),
        fill=(170, 180, 187),
    )

    panels = [
        ("1 · PACK SEAM", 0.45),
        ("2 · ARRIVAL / OVERLAP", 0.92),
        ("3 · OBJECT-BOUND RIM", 1.60),
        ("4 · CLIPPED SHEEN / HOLD", 2.86),
    ]
    panel_y = 168
    panel_w = 415
    panel_h = 580
    for index, (label, time_seconds) in enumerate(panels):
        x = 18 + index * 442
        draw.rounded_rectangle(
            (x, panel_y, x + panel_w, panel_y + panel_h),
            radius=18,
            fill=(12, 16, 20),
            outline=(54, 66, 76),
            width=3,
        )
        frame, state = render_frame(time_seconds, labels=False)
        frame.thumbnail((375, 460), Image.Resampling.LANCZOS)
        board.paste(frame, (x + 20, panel_y + 64))
        draw.text(
            (x + 18, panel_y + 28),
            label,
            font=SOURCE.font(22, True),
            fill=(239, 241, 242),
        )
        draw.text(
            (x + 18, panel_y + 542),
            f"outside case light = {state['caseLightOutsideMaskPixels']} px",
            font=SOURCE.font(15, True),
            fill=(94, 216, 160),
        )

    ownership_y = 800
    ownership = [
        ("BLENDER", "geometry · pivot · UV · material zones"),
        ("UNITY", "runtime motion · curves · mesh-clipped light · camera · performance"),
        ("SWIFTUI / RIVE", "Pack selection · tear · foreground handoff"),
        ("REACT", "review tooling only · never shipping animation"),
    ]
    for index, (title, body) in enumerate(ownership):
        x = 30 + (index % 2) * 885
        y = ownership_y + (index // 2) * 126
        draw.rounded_rectangle(
            (x, y, x + 850, y + 104),
            radius=16,
            fill=(13, 18, 22),
            outline=(55, 68, 78),
            width=2,
        )
        draw.text(
            (x + 18, y + 23),
            title,
            font=SOURCE.font(22, True),
            fill=(94, 216, 160) if title == "UNITY" else (229, 185, 84),
        )
        draw.text(
            (x + 18, y + 62),
            body,
            font=SOURCE.font(18),
            fill=(208, 214, 218),
        )

    runtime_y = 1070
    draw.rounded_rectangle(
        (30, runtime_y, 1770, 1435),
        radius=18,
        fill=(12, 16, 20),
        outline=(54, 66, 76),
        width=3,
    )
    draw.text(
        (52, runtime_y + 30),
        "UNITY RUNTIME CONTRACT",
        font=SOURCE.font(24, True),
        fill=(94, 216, 160),
    )
    runtime_lines = [
        "GachaRevealDirector = receipt / two-frame ready / interruption recovery / phase authority",
        "RevealMotionProfile ScriptableObject + AnimationCurve = tunable duration, easing, overlap and Z travel",
        "Case shader + MaterialPropertyBlock = object-local rim and one finite _SheenProgress sweep",
        "Timeline = editor preview and scrub only; never transaction-state authority",
        "No external Point Light for final sheen · no VFX Graph · no particles · no persistent light loop",
    ]
    for index, line in enumerate(runtime_lines):
        draw.text(
            (66, runtime_y + 82 + index * 51),
            f"• {line}",
            font=SOURCE.font(19),
            fill=(208, 214, 218),
        )
    board.save(BOARD_PATH, optimize=True)


def build_architecture():
    architecture = json.loads(REV6_ARCHITECTURE_PATH.read_text(encoding="utf-8"))
    architecture["schema"] = "premium-display-case-gate04-mesh-clipped-light-architecture.v1"
    architecture["evidenceRevision"] = 7
    architecture["status"] = "ready_for_review"
    architecture["ownership"]["light"] = "MeshClippedLightController"
    for node in architecture["nodes"]:
        if node["id"] == "restrained-light-controller":
            node["id"] = "mesh-clipped-light-controller"
            node["responsibilities"] = [
                "pack-seam-light-owned-by-NativePackOwner",
                "arrival-rim-inside-case-mask",
                "rotation-rim-inside-case-mask",
                "final-mesh-clipped-sheen",
            ]
    for phase in architecture["phaseArchitecture"]:
        if phase["id"] == "entry-showcase-overlap":
            phase["lightCue"] = "arrival-rim-inside-case-mask transitions to rotation-rim-inside-case-mask"
        elif phase["id"] == "showcase":
            phase["lightCue"] = "rotation-rim-inside-case-mask"
        elif phase["id"] == "final-light":
            phase["owner"] = "MeshClippedLightController"
            phase["lightCue"] = "final-mesh-clipped-sheen"
    architecture["lightCues"] = [
        {
            "id": "pack-seam-light",
            "owner": "NativePackOwner",
            "renderOwner": "Pack shader",
            "mask": "Pack opening seam only",
            "finite": True,
        },
        {
            "id": "arrival-rim-inside-case-mask",
            "owner": "MeshClippedLightController",
            "renderOwner": "Case shader",
            "mask": "object-local inner silhouette edge",
            "finite": True,
        },
        {
            "id": "rotation-rim-inside-case-mask",
            "owner": "MeshClippedLightController",
            "renderOwner": "Case shader",
            "mask": "object-local surface orientation clipped to case",
            "finite": True,
        },
        {
            "id": "final-mesh-clipped-sheen",
            "owner": "MeshClippedLightController",
            "renderOwner": "Case shader",
            "mask": "UV or object-space case silhouette",
            "driver": "MaterialPropertyBlock _SheenProgress 0..1 once",
            "finite": True,
        },
    ]
    architecture["invariants"].update(
        {
            "caseLightOutsideSilhouettePixels": 0,
            "externalSettleHalo": False,
            "externalPointLightFinalSheen": False,
            "vfxGraphDependency": False,
            "bloomDependency": False,
            "particleEmitterCount": 0,
            "persistentLightLoop": False,
        }
    )
    tunable = architecture["tunableRuntimeParameters"]
    tunable.pop("settleHaloRadius", None)
    tunable.pop("settleHaloDuration", None)
    tunable["finalSheenMaskSpace"] = "object-local-or-uv-candidate"
    tunable["finalSheenDriver"] = "MaterialPropertyBlock"
    tunable["finalSheenShaderProperty"] = "_SheenProgress"
    architecture["toolOwnership"] = {
        "Blender": [
            "geometry",
            "pivot",
            "UV",
            "material zones",
        ],
        "Unity": [
            "runtime motion",
            "timing and easing",
            "entry Z travel",
            "360 showcase",
            "mesh-clipped light",
            "camera",
            "performance",
        ],
        "SwiftUI/Rive": [
            "Pack selection",
            "tear",
            "foreground retreat",
            "ready/handoff bridge",
        ],
        "React": [
            "pipeline review tooling only",
        ],
    }
    architecture["unityRuntimeArchitecture"] = {
        "stateAuthority": "GachaRevealDirector",
        "profile": "RevealMotionProfile ScriptableObject",
        "curves": "AnimationCurve per phase and cue",
        "materialDriver": "MaterialPropertyBlock",
        "timelineRole": "editor-preview-and-scrub-only",
        "timelineTransactionAuthority": False,
        "shippingRuntimeParameterApproval": "pending",
    }
    architecture["userReview"] = {
        "board": BOARD_PATH.name,
        "gif": GIF_PATH.name,
        "contactSheet": CONTACT_PATH.name,
        "assembledOnly": True,
        "explodedVisible": False,
        "externalHaloVisible": False,
    }
    architecture["sourceFeedback"] = {
        "quote": "尤其是你的过光，不应该超过这个物体本身。",
        "accepted": [
            "same-case-identity",
            "bounded-entry-rotation-overlap",
            "Unity-runtime-authoring",
        ],
        "rejected": [
            "external-settle-halo",
            "light-outside-case-silhouette",
            "external-point-light-final-sheen",
        ],
    }
    architecture["route"]["gate05Status"] = "blocked"
    architecture["route"]["shippingUnityEdit"] = False
    architecture["route"]["buildInstallPhonePush"] = False
    ARCHITECTURE_PATH.write_text(
        json.dumps(architecture, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return architecture


def create_validation(architecture, states):
    max_outside = max(
        state["caseLightOutsideMaskPixels"] for state in states
    )
    cue_counts = {
        "pack-seam-light": sum(
            1 for state in states if state["lightCues"]["packSeam"] > 0
        ),
        "arrival-rim-inside-case-mask": sum(
            1 for state in states if state["lightCues"]["arrivalRim"] > 0
        ),
        "rotation-rim-inside-case-mask": sum(
            1 for state in states if state["lightCues"]["rotationRim"] > 0
        ),
        "final-mesh-clipped-sheen": sum(
            1 for state in states if state["lightCues"]["finalSheen"] > 0
        ),
    }
    final_cues = states[-1]["lightCues"]
    checks = {
        "sourceContractRevision3": architecture["sourceContract"]["contractRevision"] == 3,
        "sameCaseAndBoundedOverlap": (
            architecture["invariants"]["oneCaseInstance"]
            and architecture["invariants"]["overlapWindowCount"] == 1
            and architecture["invariants"]["overlapBounded"]
        ),
        "caseLightClipped": max_outside == 0,
        "externalHaloRemoved": architecture["invariants"]["externalSettleHalo"] is False,
        "externalPointLightRejected": (
            architecture["invariants"]["externalPointLightFinalSheen"] is False
        ),
        "materialPropertyBlockDriver": (
            architecture["unityRuntimeArchitecture"]["materialDriver"]
            == "MaterialPropertyBlock"
        ),
        "timelinePreviewOnly": (
            architecture["unityRuntimeArchitecture"]["timelineRole"]
            == "editor-preview-and-scrub-only"
            and architecture["unityRuntimeArchitecture"]["timelineTransactionAuthority"]
            is False
        ),
        "toolOwnershipExplicit": set(architecture["toolOwnership"]) == {
            "Blender",
            "Unity",
            "SwiftUI/Rive",
            "React",
        },
        "fourFiniteCues": (
            len(architecture["lightCues"]) == 4
            and all(cue["finite"] for cue in architecture["lightCues"])
            and all(count > 0 for count in cue_counts.values())
            and all(value == 0 for value in final_cues.values())
        ),
        "noParticleVfxBloomLoop": (
            architecture["invariants"]["particleEmitterCount"] == 0
            and architecture["invariants"]["vfxGraphDependency"] is False
            and architecture["invariants"]["bloomDependency"] is False
            and architecture["invariants"]["persistentLightLoop"] is False
        ),
        "toyStatic": architecture["invariants"]["toyIndependentAngularVelocity"] == 0,
        "wholeCaseNoExplode": (
            architecture["invariants"]["wholeCaseOnly"]
            and architecture["invariants"]["explodeEligible"] is False
        ),
        "timingStillTunable": (
            architecture["tunableRuntimeParameters"]["shippingTotalDurationSeconds"]
            is None
            and architecture["tunableRuntimeParameters"]["overlapDurationSeconds"]
            is None
        ),
        "gate05Blocked": architecture["route"]["gate05Status"] == "blocked",
        "shippingBoundary": (
            architecture["route"]["shippingUnityEdit"] is False
            and architecture["route"]["buildInstallPhonePush"] is False
        ),
    }
    validation = {
        "schema": "premium-display-case-gate04-mesh-clipped-light-validation.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 2,
        "evidenceRevision": 7,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "caseLightOutsideSilhouetteMaxPixels": max_outside,
            "finiteLightCueCount": len(architecture["lightCues"]),
            "lightCueActiveFrameCounts": cue_counts,
            "particleEmitterCount": 0,
            "externalPointLightCount": 0,
            "persistentLightLoopCount": 0,
            "finalFrameActiveLightCueCount": sum(
                1 for value in final_cues.values() if value > 0
            ),
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
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
    }
    VALIDATION_PATH.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return validation


def main():
    states = create_gif()
    create_contact_sheet()
    create_review_board()
    architecture = build_architecture()
    validation = create_validation(architecture, states)
    if validation["status"] != "pass":
        raise SystemExit("Gate 04 rev 7 validation failed")
    print(
        json.dumps(
            {
                "architecture": str(ARCHITECTURE_PATH),
                "gif": str(GIF_PATH),
                "contact": str(CONTACT_PATH),
                "review": str(BOARD_PATH),
                "validation": str(VALIDATION_PATH),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
