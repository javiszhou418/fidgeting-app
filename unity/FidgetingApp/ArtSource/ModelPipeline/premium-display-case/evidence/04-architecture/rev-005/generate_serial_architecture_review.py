#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
CONTRACT_PATH = (
    REPO
    / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
    / "evidence/03-contract/rev-003/modeling-contract.json"
)

ARCHITECTURE_PATH = ROOT / "architecture.json"
PART_TREE_PATH = ROOT / "part-tree-internal.svg"
EXPLODED_PATH = ROOT / "exploded-plan-internal.svg"
REVIEW_PATH = ROOT / "whole-case-architecture-review.png"
VALIDATION_PATH = ROOT / "architecture-validation.json"

WIDTH = 3200
HEIGHT = 3900


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


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wrap(draw, text, width, face):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=face) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def contract_architecture(contract):
    light_cues = [
        {
            "id": "pack-seam-light",
            "owner": "RestrainedLightController",
            "renderOwner": "NativePackOwner",
            "trigger": "tear/opening during ENTRY",
            "finite": True,
        },
        {
            "id": "arrival-rim",
            "owner": "RestrainedLightController",
            "renderOwner": "CaseAssembly",
            "trigger": "case clears Pack threshold",
            "finite": True,
        },
        {
            "id": "rotation-surface-rim",
            "owner": "RestrainedLightController",
            "renderOwner": "CaseAssembly",
            "trigger": "turning surface orientation during SHOWCASE",
            "finite": True,
        },
        {
            "id": "final-sheen-short-halo",
            "owner": "RestrainedLightController",
            "renderOwner": "CaseAssembly",
            "trigger": "SHOWCASE completion",
            "finite": True,
            "contains": ["final-diagonal-sheen", "settle-halo-then-zero"],
        },
    ]
    nodes = [
        {
            "id": "native-pack-owner",
            "parentId": None,
            "kind": "external-native-owner",
            "physical": False,
            "reviewVisible": True,
            "responsibilities": [
                "Pack foreground",
                "tear progress",
                "authoritative handoff trigger",
            ],
        },
        {
            "id": "presentation-root",
            "parentId": None,
            "kind": "transform-root",
            "physical": False,
            "reviewVisible": True,
            "responsibilities": [
                "serial phase ownership",
                "Y+Z entry",
                "local-Y 360 showcase",
            ],
        },
        {
            "id": "reveal-sequence-controller",
            "parentId": "presentation-root",
            "kind": "logic-controller",
            "physical": False,
            "reviewVisible": True,
            "responsibilities": [
                "ENTRY",
                "SETTLE",
                "SHOWCASE",
                "FINAL_LIGHT",
                "HOLD",
            ],
        },
        {
            "id": "restrained-light-controller",
            "parentId": "presentation-root",
            "kind": "logic-controller",
            "physical": False,
            "reviewVisible": True,
            "responsibilities": [cue["id"] for cue in light_cues],
        },
        {
            "id": "case-assembly",
            "parentId": "presentation-root",
            "kind": "rigid-transform-group",
            "physical": False,
            "reviewVisible": True,
            "responsibilities": [
                "one assembled instance",
                "same identity through ACK",
            ],
        },
        {
            "id": "rear-polycarbonate-shell",
            "parentId": "case-assembly",
            "kind": "physical-part",
            "physical": True,
            "reviewVisible": False,
        },
        {
            "id": "tactile-background-insert",
            "parentId": "case-assembly",
            "kind": "physical-part",
            "physical": True,
            "reviewVisible": False,
        },
        {
            "id": "content-slot",
            "parentId": "case-assembly",
            "kind": "caller-anchor",
            "physical": False,
            "reviewVisible": True,
        },
        {
            "id": "toy-content",
            "parentId": "content-slot",
            "kind": "external-caller-owned-content",
            "physical": True,
            "reviewVisible": True,
            "independentAngularVelocity": 0,
        },
        {
            "id": "front-polycarbonate-shell",
            "parentId": "case-assembly",
            "kind": "physical-part",
            "physical": True,
            "reviewVisible": False,
        },
        {
            "id": "continuous-tube-perimeter",
            "parentId": "case-assembly",
            "kind": "one-connected-physical-part",
            "physical": True,
            "reviewVisible": False,
        },
        {
            "id": "physical-label",
            "parentId": "case-assembly",
            "kind": "physical-part",
            "physical": True,
            "reviewVisible": False,
        },
        {
            "id": "transparent-cover",
            "parentId": "case-assembly",
            "kind": "physical-part",
            "physical": True,
            "reviewVisible": False,
        },
    ]
    return {
        "schema": "premium-display-case-gate04-serial-architecture.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 2,
        "evidenceRevision": 5,
        "status": "ready_for_review",
        "sourceContract": {
            "path": str(CONTRACT_PATH.relative_to(REPO)),
            "sha256": sha256(CONTRACT_PATH),
            "contractRevision": contract["contractRevision"],
            "sourceAnalysisRevision": contract["sourceAnalysisRevision"],
            "sourceClaimIds": contract["sourceClaimIds"],
        },
        "ownership": {
            "pack": "external/native NativePackOwner",
            "presentation": "PresentationRoot",
            "case": "one rigid CaseAssembly instance",
            "toy": "caller-owned ContentSlot child",
            "light": "RestrainedLightController",
        },
        "nodes": nodes,
        "phaseArchitecture": [
            {
                "id": "prepare",
                "owner": "NativePackOwner + RevealSequenceController",
                "visible": "Pack only",
                "completion": "receipt + same request + case/prize/camera stable for 2 frames",
            },
            {
                "id": "entry",
                "owner": "PresentationRoot",
                "motion": ["screen-y", "camera-depth-z"],
                "rotation": [0, 0, 0],
                "concurrentPackAction": "Pack retreats for 0.28 s",
                "lightCue": "pack-seam-light",
            },
            {
                "id": "settle",
                "owner": "RevealSequenceController",
                "completion": "translation velocity 0; rotation velocity 0",
                "lightCue": "arrival-rim",
            },
            {
                "id": "showcase",
                "owner": "PresentationRoot",
                "motion": "one local-Y 360",
                "translation": "locked",
                "lightCue": "rotation-surface-rim",
            },
            {
                "id": "final-light",
                "owner": "RestrainedLightController",
                "motion": "none",
                "lightCue": "final-sheen-short-halo",
            },
            {
                "id": "hold",
                "owner": "RevealSequenceController",
                "motion": "none",
                "light": "all cues zero",
                "completion": "user ACK",
            },
        ],
        "lightCues": light_cues,
        "invariants": {
            "oneCaseInstance": True,
            "wholeCaseOnly": True,
            "packProxyAllowed": False,
            "entryRotationDegrees": [0, 0, 0],
            "showcaseDegrees": 360,
            "entryAndShowcaseOverlap": False,
            "toyIndependentAngularVelocity": 0,
            "particleEmitterCount": 0,
            "persistentLightLoop": False,
            "explodeEligible": False,
        },
        "tunableRuntimeParameters": contract["tunableRuntimeParameters"],
        "internalEvidence": {
            "partTree": "part-tree-internal.svg",
            "explodedPlan": "exploded-plan-internal.svg",
            "reviewEligible": False,
            "productAnimationEligible": False,
        },
        "userReview": {
            "board": "whole-case-architecture-review.png",
            "assembledOnly": True,
            "explodedVisible": False,
        },
        "route": {
            "gate05Status": "blocked",
            "shippingUnityEdit": False,
            "buildInstallPhonePush": False,
            "nextGatePolicy": "Do not enter Gate 05 before explicit Gate 04 approval.",
        },
    }


def write_internal_part_tree(architecture):
    rows = [
        ("NativePackOwner", "external/native · Pack foreground + tear + handoff"),
        ("PresentationRoot", "motion owner · serial phases"),
        ("  RevealSequenceController", "ENTRY → SETTLE → SHOWCASE → FINAL_LIGHT → HOLD"),
        ("  RestrainedLightController", "4 finite cues · no particles · no loop"),
        ("  CaseAssembly", "one rigid assembled instance"),
        ("    RearPolycarbonateShell", "physical"),
        ("    TactileBackgroundInsert", "physical"),
        ("    ContentSlot", "caller anchor"),
        ("      ToyContent", "caller-owned · static · ω=0"),
        ("    FrontPolycarbonateShell", "physical"),
        ("    ContinuousTubePerimeter", "one connected physical part"),
        ("    PhysicalLabel", "physical"),
        ("    TransparentCover", "physical"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2300" viewBox="0 0 1800 2300">',
        '<rect width="1800" height="2300" fill="#090D12"/>',
        '<text x="80" y="105" fill="#F4F7FA" font-size="58" font-weight="700" font-family="Arial, PingFang SC, sans-serif">GATE 04 REV 5 · INTERNAL PART / OWNER TREE</text>',
        '<text x="80" y="165" fill="#F0BC66" font-size="30" font-weight="700" font-family="Arial, PingFang SC, sans-serif">INTERNAL TECHNICAL EVIDENCE · NOT A USER REVIEW ARTIFACT</text>',
        '<rect x="80" y="205" width="1640" height="72" rx="18" fill="#F1777E"/>',
        '<text x="120" y="253" fill="#0A0D12" font-size="34" font-weight="700" font-family="Arial, PingFang SC, sans-serif">SHIPPING REVEAL ALWAYS SHOWS ONE ASSEMBLED CASE</text>',
    ]
    y = 340
    for index, (title, detail) in enumerate(rows):
        indent = len(title) - len(title.lstrip())
        x = 105 + indent * 45
        title = title.strip()
        color = "#74A8FF" if title in {"NativePackOwner", "PresentationRoot"} else "#73D5D0"
        if title == "CaseAssembly":
            color = "#69D4A9"
        if title in {"ContentSlot", "ToyContent"}:
            color = "#F0BC66"
        out.append(f'<rect x="{x}" y="{y-26}" width="30" height="30" rx="7" fill="{color}"/>')
        out.append(f'<text x="{x+50}" y="{y}" fill="#F4F7FA" font-size="31" font-weight="700" font-family="Arial, PingFang SC, sans-serif">{title}</text>')
        out.append(f'<text x="{x+50}" y="{y+38}" fill="#A7B1BF" font-size="24" font-family="Arial, PingFang SC, sans-serif">{detail}</text>')
        y += 138
    out.extend([
        '<rect x="80" y="2140" width="1640" height="100" rx="22" fill="#141922" stroke="#323B49" stroke-width="3"/>',
        '<text x="120" y="2202" fill="#F0BC66" font-size="27" font-weight="700" font-family="Arial, PingFang SC, sans-serif">No invented fasteners · no proxy case · no toy ownership transfer · no persistent light emitter</text>',
        '</svg>',
    ])
    PART_TREE_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_internal_exploded_plan():
    parts = [
        ("TransparentCover", "#B5D4E8"),
        ("PhysicalLabel", "#D8C7A4"),
        ("ContinuousTubePerimeter", "#E4EEF4"),
        ("FrontPolycarbonateShell", "#9DBCCB"),
        ("ContentSlot + caller Toy", "#D8B67D"),
        ("TactileBackgroundInsert", "#575C65"),
        ("RearPolycarbonateShell", "#8298A6"),
    ]
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2300" viewBox="0 0 1800 2300">',
        '<rect width="1800" height="2300" fill="#090D12"/>',
        '<text x="80" y="105" fill="#F4F7FA" font-size="58" font-weight="700" font-family="Arial, PingFang SC, sans-serif">GATE 04 REV 5 · INTERNAL EXPLODED PLAN</text>',
        '<text x="80" y="165" fill="#F0BC66" font-size="30" font-weight="700" font-family="Arial, PingFang SC, sans-serif">TECHNICAL PIPELINE EVIDENCE ONLY · productAnimationEligible=false</text>',
        '<rect x="80" y="205" width="1640" height="72" rx="18" fill="#F1777E"/>',
        '<text x="120" y="253" fill="#0A0D12" font-size="34" font-weight="700" font-family="Arial, PingFang SC, sans-serif">NEVER DISPLAY THIS SEPARATION IN GACHA, NATIVE UI, UNITY PRESENTATION OR USER REVIEW</text>',
    ]
    y = 360
    for index, (name, color) in enumerate(parts):
        x = 120 + index * 75
        out.append(f'<rect x="{x}" y="{y}" width="920" height="150" rx="30" fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="6"/>')
        out.append(f'<text x="{x+35}" y="{y+62}" fill="#F4F7FA" font-size="33" font-weight="700" font-family="Arial, PingFang SC, sans-serif">{name}</text>')
        detail = "caller-owned; not modified" if "Toy" in name else "preserved historical physical zone"
        out.append(f'<text x="{x+35}" y="{y+110}" fill="#A7B1BF" font-size="25" font-family="Arial, PingFang SC, sans-serif">{detail}</text>')
        y += 215
    out.extend([
        '<rect x="80" y="2020" width="1640" height="170" rx="24" fill="#141922" stroke="#323B49" stroke-width="3"/>',
        '<text x="120" y="2080" fill="#74A8FF" font-size="30" font-weight="700" font-family="Arial, PingFang SC, sans-serif">Runtime ownership</text>',
        '<text x="120" y="2130" fill="#F4F7FA" font-size="27" font-family="Arial, PingFang SC, sans-serif">PresentationRoot moves the fully assembled CaseAssembly only. ContentSlot inherits root motion; Toy independent ω=0.</text>',
        '<text x="120" y="2172" fill="#F4F7FA" font-size="27" font-family="Arial, PingFang SC, sans-serif">RestrainedLightController is finite and logical; it does not create an extra physical layer.</text>',
        '</svg>',
    ])
    EXPLODED_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")


def draw_case(draw, box, sheen=False):
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=42, fill=(43, 49, 54), outline=(192, 202, 210), width=8)
    draw.rounded_rectangle(
        (left + 24, top + 24, right - 24, bottom - 24),
        radius=31,
        outline=(104, 115, 123),
        width=4,
    )
    label_bottom = top + int((bottom - top) * 0.28)
    draw.rounded_rectangle(
        (left + 44, top + 48, right - 44, label_bottom),
        radius=18,
        fill=(210, 215, 218),
    )
    draw.rounded_rectangle(
        (left + 42, label_bottom + 34, right - 42, bottom - 48),
        radius=25,
        fill=(21, 25, 28),
        outline=(105, 115, 122),
        width=4,
    )
    if sheen:
        draw.polygon(
            [
                (left + 160, top + 15),
                (left + 205, top + 15),
                (right - 120, bottom - 15),
                (right - 165, bottom - 15),
            ],
            fill=(230, 235, 238),
        )


def draw_review_board(architecture):
    image = Image.new("RGB", (WIDTH, HEIGHT), (7, 10, 13))
    draw = ImageDraw.Draw(image)
    cyan = (90, 205, 218)
    white = (239, 242, 244)
    muted = (168, 179, 188)
    green = (94, 216, 160)
    amber = (236, 188, 82)
    panel = (13, 18, 23)
    stroke = (56, 69, 80)

    draw.rectangle((0, 0, WIDTH, 122), fill=cyan)
    draw.text(
        (WIDTH // 2, 61),
        "GATE 04 REV 5 · WHOLE-CASE OWNERSHIP + SERIAL PHASE ARCHITECTURE",
        font=font(47, True),
        fill=(2, 10, 12),
        anchor="mm",
    )
    draw.text(
        (55, 170),
        "USER REVIEW · assembled case only · internal part separation is excluded",
        font=font(29, True),
        fill=white,
    )

    draw.rounded_rectangle((55, 215, 3145, 1000), radius=28, fill=panel, outline=stroke, width=4)
    draw.text((95, 280), "ONE IDENTITY / ONE OWNER", font=font(34, True), fill=green)
    draw_case(draw, (1120, 335, 2080, 930))
    draw.text((1600, 965), "CaseAssembly · same rigid instance from first visible frame through ACK", font=font(27, True), fill=white, anchor="mm")
    draw.text((500, 510), "Native Pack", font=font(32, True), fill=cyan, anchor="mm")
    draw.text((500, 560), "external / native owner", font=font(24), fill=muted, anchor="mm")
    draw.line((720, 565, 1080, 565), fill=cyan, width=8)
    draw.polygon([(1050, 540), (1050, 590), (1090, 565)], fill=cyan)
    draw.text((2700, 510), "ContentSlot / Toy", font=font(32, True), fill=amber, anchor="mm")
    draw.text((2700, 560), "caller-owned · inherited root motion · independent ω=0", font=font(22), fill=muted, anchor="mm")
    draw.line((2120, 565, 2480, 565), fill=amber, width=8)
    draw.polygon([(2450, 540), (2450, 590), (2490, 565)], fill=amber)

    draw.rounded_rectangle((55, 1040, 3145, 1950), radius=28, fill=panel, outline=stroke, width=4)
    draw.text((95, 1105), "SERIAL PHASES · NEVER SIMULTANEOUS", font=font(34, True), fill=green)
    phases = [
        ("PREPARE", "Pack visible\nreceipt + 2 stable frames"),
        ("ENTRY", "Y + camera Z\nrotation 0"),
        ("SETTLE", "translation velocity 0\nrotation velocity 0"),
        ("SHOWCASE", "one local-Y 360°\ntranslation locked"),
        ("FINAL LIGHT", "one sheen + short halo\nthen all light = 0"),
        ("HOLD", "static case + toy\nawait ACK"),
    ]
    start_x = 95
    gap = 28
    phase_w = 480
    for index, (title, body) in enumerate(phases):
        x = start_x + index * (phase_w + gap)
        box = (x, 1180, x + phase_w, 1815)
        draw.rounded_rectangle(box, radius=22, fill=(18, 24, 30), outline=(75, 91, 104), width=3)
        draw.text((x + 28, 1232), f"{index + 1:02d} · {title}", font=font(25, True), fill=cyan if index < 2 else white)
        mini = (x + 135, 1315, x + 345, 1610)
        draw_case(draw, mini, sheen=title == "FINAL LIGHT")
        for line_index, line in enumerate(body.split("\n")):
            draw.text((x + phase_w // 2, 1660 + line_index * 38), line, font=font(21), fill=muted, anchor="mm")
        if index < len(phases) - 1:
            arrow_x = x + phase_w + 5
            draw.line((arrow_x, 1495, arrow_x + 18, 1495), fill=green, width=6)
            draw.polygon([(arrow_x + 12, 1483), (arrow_x + 12, 1507), (arrow_x + 28, 1495)], fill=green)

    draw.rounded_rectangle((55, 1990, 3145, 2860), radius=28, fill=panel, outline=stroke, width=4)
    draw.text((95, 2055), "FOUR FINITE LIGHT CUES · PHYSICALLY CAUSED", font=font(34, True), fill=green)
    cues = [
        ("1 · PACK SEAM", "Native Pack owner", "tear/opening"),
        ("2 · ARRIVAL RIM", "CaseAssembly", "clears Pack threshold"),
        ("3 · ROTATION RIM", "Case surface", "turning orientation"),
        ("4 · FINAL SHEEN + HALO", "CaseAssembly", "showcase completes"),
    ]
    for index, (title, owner, cause) in enumerate(cues):
        x = 95 + (index % 2) * 1525
        y = 2150 + (index // 2) * 310
        draw.rounded_rectangle((x, y, x + 1440, y + 245), radius=20, fill=(18, 24, 30), outline=(75, 91, 104), width=3)
        draw.text((x + 32, y + 55), title, font=font(27, True), fill=cyan)
        draw.text((x + 32, y + 112), f"Render owner: {owner}", font=font(22), fill=white)
        draw.text((x + 32, y + 163), f"Cause: {cause}", font=font(22), fill=muted)
        draw.text((x + 32, y + 211), "finite · no particle emitter · no persistent loop", font=font(20, True), fill=amber)

    draw.rounded_rectangle((55, 2900, 3145, 3760), radius=28, fill=panel, outline=stroke, width=4)
    draw.text((95, 2965), "LOCKED ARCHITECTURE", font=font(34, True), fill=green)
    locked = [
        "PresentationRoot owns all case motion.",
        "CaseAssembly remains one assembled rigid identity through ACK.",
        "Entry completes before the 360° showcase begins.",
        "ContentSlot and Toy remain caller-owned and static.",
        "Native Pack stays external; no case proxy replaces it.",
        "No split, explode, particles, VFX Graph, camera/background motion or persistent light.",
    ]
    for index, text in enumerate(locked):
        draw.text((110, 3040 + index * 66), f"• {text}", font=font(23), fill=white)
    draw.text((1700, 2965), "EXPLICITLY TUNABLE / UNKNOWN", font=font(34, True), fill=amber)
    tunable = [
        "shipping total duration and phase durations",
        "phase easing and rotation angular-velocity curve",
        "Y/Z travel distances",
        "seam/rim/sheen/halo width, intensity, color and falloff",
        "settle halo radius/duration",
        "shipping camera FOV",
    ]
    for index, text in enumerate(tunable):
        draw.text((1715, 3040 + index * 66), f"• {text}", font=font(23), fill=white)
    draw.rounded_rectangle((1700, 3470, 3080, 3700), radius=20, fill=(35, 26, 14), outline=amber, width=3)
    for line_index, line in enumerate(wrap(
        draw,
        "3.4 s is analysis-preview rhythm only. No shipping duration, easing, distance or light parameter is approved.",
        1280,
        font(25, True),
    )):
        draw.text((1740, 3525 + line_index * 46), line, font=font(25, True), fill=amber)

    image.save(REVIEW_PATH, optimize=True)


def validate(architecture):
    nodes = {node["id"]: node for node in architecture["nodes"]}
    cues = architecture["lightCues"]
    phases = architecture["phaseArchitecture"]
    tunable = architecture["tunableRuntimeParameters"]
    checks = {
        "sourceContractRevision3": architecture["sourceContract"]["contractRevision"] == 3,
        "tenSourceClaims": len(architecture["sourceContract"]["sourceClaimIds"]) == 10,
        "presentationRootMotionOwner": architecture["ownership"]["presentation"] == "PresentationRoot",
        "oneRigidCaseInstance": architecture["invariants"]["oneCaseInstance"] is True,
        "wholeCaseOnly": architecture["invariants"]["wholeCaseOnly"] is True,
        "nativePackExternal": nodes["native-pack-owner"]["kind"] == "external-native-owner",
        "toyCallerOwned": nodes["toy-content"]["kind"] == "external-caller-owned-content",
        "toyAngularVelocityZero": nodes["toy-content"]["independentAngularVelocity"] == 0,
        "phaseOrder": [phase["id"] for phase in phases] == [
            "prepare", "entry", "settle", "showcase", "final-light", "hold"
        ],
        "entryRotationZero": phases[1]["rotation"] == [0, 0, 0],
        "showcaseAfterSettle": phases[3]["motion"] == "one local-Y 360",
        "showcaseTranslationLocked": phases[3]["translation"] == "locked",
        "fourFiniteLightCues": len(cues) == 4 and all(cue["finite"] for cue in cues),
        "noParticleEmitter": architecture["invariants"]["particleEmitterCount"] == 0,
        "noPersistentLight": architecture["invariants"]["persistentLightLoop"] is False,
        "noProxy": architecture["invariants"]["packProxyAllowed"] is False,
        "noExplode": architecture["invariants"]["explodeEligible"] is False,
        "shippingDurationUnknown": tunable["shippingTotalDurationSeconds"] is None,
        "phaseTimingUnknown": tunable["phaseDurationsSeconds"] is None,
        "easingUnknown": tunable["phaseEasing"] is None,
        "zDistanceUnknown": tunable["entryCameraDepthZDistance"] is None,
        "lightTuningUnknown": tunable["seamLightIntensity"] is None,
        "internalExplodedNotReview": architecture["internalEvidence"]["reviewEligible"] is False,
        "userReviewAssembledOnly": architecture["userReview"]["assembledOnly"] is True,
        "gate05Blocked": architecture["route"]["gate05Status"] == "blocked",
        "shippingBoundary": architecture["route"]["shippingUnityEdit"] is False
        and architecture["route"]["buildInstallPhonePush"] is False,
    }
    with Image.open(REVIEW_PATH) as image:
        image_report = {
            "path": str(REVIEW_PATH.relative_to(REPO)),
            "width": image.width,
            "height": image.height,
            "nonBlank": image.getbbox() is not None,
        }
    report = {
        "schema": "premium-display-case-gate04-serial-architecture-validation.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 2,
        "evidenceRevision": 5,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "nodeCount": len(nodes),
            "phaseCount": len(phases),
            "finiteLightCueCount": len(cues),
            "reviewArtifactExplodedPartCount": 0,
            "tunableRuntimeParameterCount": 17,
        },
        "imageReport": image_report,
        "truth": {
            "architectureOnly": True,
            "internalExplodedPlanOnly": True,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
        "artifactHashes": {
            "architecture": sha256(ARCHITECTURE_PATH),
            "partTree": sha256(PART_TREE_PATH),
            "explodedPlan": sha256(EXPLODED_PATH),
            "review": sha256(REVIEW_PATH),
        },
    }
    VALIDATION_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise SystemExit("Gate 04 architecture validation failed")


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    architecture = contract_architecture(contract)
    ARCHITECTURE_PATH.write_text(
        json.dumps(architecture, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_internal_part_tree(architecture)
    write_internal_exploded_plan()
    draw_review_board(architecture)
    validate(architecture)
    print(json.dumps({
        "architecture": str(ARCHITECTURE_PATH),
        "partTree": str(PART_TREE_PATH),
        "explodedPlan": str(EXPLODED_PATH),
        "review": str(REVIEW_PATH),
        "validation": str(VALIDATION_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
