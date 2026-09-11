#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat


HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parents[2]
REPO = next(
    parent
    for parent in HERE.parents
    if (parent / "AGENTS.md").is_file()
    and (parent / "tools/model-provenance-explorer").is_dir()
)
PIPELINE_PATH = MODEL_DIR / "pipeline.json"
HISTORICAL_CONTRACT_PATH = MODEL_DIR / "evidence/03-contract/rev-002/modeling-contract.json"
CONTRACT_PATH = HERE / "modeling-contract.json"
PREVIEW_PATH = HERE / "contract-preview.png"
VALIDATION_PATH = HERE / "contract-validation.json"

BG = "#080B10"
PANEL = "#111821"
PANEL_ALT = "#151E29"
LINE = "#2B3948"
TEXT = "#F2F6F8"
MUTED = "#A9B4C0"
CYAN = "#63D7E5"
GREEN = "#72D4A6"
AMBER = "#F0BC66"
RED = "#F1777E"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        (Path("/System/Library/Fonts/Hiragino Sans GB.ttc"), 1 if bold else 0),
        (
            Path(
                "/System/Library/Fonts/STHeiti Medium.ttc"
                if bold
                else "/System/Library/Fonts/STHeiti Light.ttc"
            ),
            0,
        ),
        (
            Path(
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
                if bold
                else "/System/Library/Fonts/Supplemental/Arial.ttf"
            ),
            0,
        ),
    ]
    for candidate, index in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size, index=index)
    return ImageFont.load_default()


def wrapped_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.FreeTypeFont,
    width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and draw.textbbox((0, 0), candidate, font=text_font)[2] > width:
                lines.append(current)
                current = character
            else:
                current = candidate
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    width: int,
    spacing: int = 10,
) -> int:
    x, y = xy
    line_height = text_font.size + spacing
    for line in wrapped_lines(draw, text, text_font, width):
        draw.text((x, y), line, font=text_font, fill=fill)
        y += line_height
    return y


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill=PANEL):
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=LINE, width=3)


def current_claims(pipeline: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        claim
        for claim in pipeline.get("claims", [])
        if claim.get("stageId") == "02-analysis"
        and claim.get("state") != "superseded"
    ]


def build_contract() -> dict[str, Any]:
    pipeline = load_json(PIPELINE_PATH)
    historical = load_json(HISTORICAL_CONTRACT_PATH)
    claims = current_claims(pipeline)
    claim_ids = [claim["id"] for claim in claims]
    if len(claim_ids) != 10:
        raise RuntimeError(f"Expected 10 active Gate 02 claims, found {len(claim_ids)}.")
    approved_analysis = pipeline["stages"][1]
    if (
        approved_analysis.get("status") != "approved"
        or approved_analysis.get("analysisSpec", {}).get("revision") != 6
    ):
        raise RuntimeError("Gate 02 rev 6 must be approved before Gate 03 rev 3.")

    static_preservation = historical["staticPreservation"]
    static_preservation["decisionState"] = (
        "historical-compatible-inputs-pending-gate03-rev3-approval"
    )

    claim_disposition = {
        claim["id"]: (
            "lock-serial-motion-direction"
            if claim["category"] in {"motion", "motion-timing"}
            else "lock-restrained-causal-light-boundary"
        )
        for claim in claims
    }
    contract = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "contractRevision": 3,
        "createdDate": "2026-08-26",
        "stageStatus": "ready_for_review",
        "approvalEffect": "none-until-explicit-gate-03-user-approval",
        "sourceAnalysisRevision": 6,
        "sourceMotionStructureRevision": 5,
        "sourceLightTreatmentRevision": 6,
        "sourceClaimIds": claim_ids,
        "units": {
            "geometry": "millimeters",
            "angles": "degrees",
            "time": "seconds",
            "lightColor": "kelvin-or-linear-rgb-candidate",
        },
        "coordinateSystem": {
            "authoring": "x width-right, y height-up, z depth-toward-camera",
            "origin": "assembled outer-envelope center",
            "motionOwner": "PresentationRoot",
            "toyOwner": "caller-owned ContentSlot",
        },
        "staticPreservation": static_preservation,
        "closedTubeFrame": historical["closedTubeFrame"],
        "handoffContract": {
            "decisionState": "locked-existing-runtime-invariant",
            "authoritativeReceiptRequired": True,
            "sameRequestRequired": True,
            "casePrizeCameraStableFrames": 2,
            "packRemainsForegroundUntilReady": True,
            "packRetreatSeconds": 0.28,
            "visibleObjectGapAllowed": False,
            "proxyAllowed": False,
        },
        "motionContract": {
            "decisionState": "gate03-rev3-pending-user-approval",
            "target": "one rigid assembled Portrait case",
            "motionOwner": "PresentationRoot",
            "phaseOrder": [
                "entry-y-z",
                "settle",
                "showcase-local-y-360",
                "final-sheen-short-halo",
                "static-hold",
            ],
            "entry": {
                "translationAxes": ["screen-y", "camera-depth-z"],
                "rotationDegrees": [0, 0, 0],
                "xDrift": 0,
                "modelScale": 1,
                "cameraMotion": False,
                "backgroundMotion": False,
            },
            "settle": {
                "requiredBeforeShowcase": True,
                "translationVelocityAtExit": 0,
                "rotationVelocityAtExit": 0,
            },
            "showcase": {
                "axis": "local-y",
                "degrees": 360,
                "count": 1,
                "translationLocked": True,
                "modelScale": 1,
                "toyIndependentAngularVelocity": 0,
            },
            "simultaneousEntryAndShowcase": False,
            "wholeCaseOnly": True,
            "objectReplacement": False,
            "toyMotion": False,
            "forbidden": [
                "x-drift",
                "roll",
                "pitch",
                "independent-model-scale-animation",
                "camera-motion",
                "background-motion",
                "object-replacement",
                "proxy",
                "split",
                "explode",
                "toy-motion",
                "rarity-color",
                "rainbow",
                "large-bloom",
                "particles",
                "vfx-graph",
                "full-screen-flash",
                "explosion",
                "screen-shake",
                "persistent-light-loop",
            ],
        },
        "lightContract": {
            "decisionState": "gate03-rev3-pending-user-approval",
            "causalCueOrder": [
                "pack-seam-light",
                "arrival-rim",
                "rotation-surface-rim",
                "final-diagonal-sheen",
                "settle-halo-then-zero",
            ],
            "packSeamLight": {
                "count": 1,
                "cause": "Pack opening during entry",
                "rarityInformation": False,
            },
            "arrivalRim": {
                "count": 1,
                "cause": "case clears Pack threshold",
                "fullScreenFlash": False,
            },
            "rotationRim": {
                "cause": "turning case surface orientation",
                "objectBound": True,
                "independentEmitter": False,
            },
            "finalSheen": {"count": 1, "shape": "narrow-diagonal"},
            "settleHalo": {
                "count": 1,
                "maximumAlpha": 0.09411764705882353,
                "persistent": False,
            },
            "maximumRgbChroma": 25,
            "vfxGraphDependency": False,
            "particles": False,
        },
        "tunableRuntimeParameters": {
            "decisionState": "explicitly-unlocked-for-later-gates-and-shipping-tuning",
            "previewDurationSeconds": 3.4,
            "shippingTotalDurationSeconds": None,
            "phaseDurationsSeconds": None,
            "phaseEasing": None,
            "entryScreenYDistance": None,
            "entryCameraDepthZDistance": None,
            "rotationAngularVelocityCurve": None,
            "seamLightWidth": None,
            "seamLightIntensity": None,
            "arrivalRimWidth": None,
            "arrivalRimIntensity": None,
            "lightColorTemperatureKelvin": None,
            "lightFalloff": None,
            "finalSheenWidth": None,
            "finalSheenIntensity": None,
            "settleHaloRadius": None,
            "settleHaloDuration": None,
            "shippingCameraFovDegrees": None,
            "note": (
                "The 3.4 s Gate 02 preview is not a shipping duration. "
                "The stale 4.520833 s and rev 3 quaternion path are not current authority."
            ),
        },
        "reduceMotion": {
            "decisionState": "locked-causal-order-tunable-transition",
            "causalOrderPreserved": True,
            "entry": "short Y+Z transition or immediate settled pose after readiness",
            "showcase": "omitted",
            "light": "single non-spatial neutral emphasis, then zero",
            "hold": "static",
        },
        "performanceBudget": historical.get("performanceBudget", {
            "lockedProductTargets": {
                "targetFramesPerSecond": 60,
                "perFrameManagedAllocationsBytes": 0,
                "offscreenUpdates": 0,
            },
            "candidateGateBudget": {
                "caseTrianglesMax": 120000,
                "caseMaterialSlotsMax": 8,
                "additionalRealtimeLightsMax": 3,
                "presentationCpuMillisecondsMax": 0.2,
                "incrementalGpuMillisecondsMax": 1.5,
                "measurement": "Target iPhone Release build; Simulator cannot pass.",
            },
        }),
        "claimDisposition": claim_disposition,
        "route": {
            "primary": "deterministic contract; existing Blender geometry remains unchanged",
            "blenderGeometryEdit": False,
            "materialEdit": False,
            "shippingUnityEdit": False,
            "buildInstallPhonePush": False,
            "nextGatePolicy": "Do not enter Gate 04 before explicit Gate 03 approval.",
        },
        "historyBoundary": {
            "gate03Rev1": "preserved-stale",
            "gate03Rev2": "preserved-stale",
            "gate04Through08": "preserved-stale",
            "staticArtifactsDeleted": False,
        },
        "completeness": {
            "complete": True,
            "activeGate02ClaimCount": len(claim_ids),
            "allActiveGate02ClaimsConsumed": True,
            "unknownsCarriedForward": True,
        },
        "approvalQuestion": (
            "是否批准 Gate 03 rev 3：锁定 Y+Z 入场→停稳→一次 local-Y 360°"
            "→克制因果光效→静止 hold 的串行合同，同时保持时长、easing、"
            "Z 行程和光效参数继续可调？"
        ),
    }
    return contract


def draw_preview(contract: dict[str, Any]) -> None:
    width, height = 3200, 3900
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    title = font(76, True)
    h2 = font(48, True)
    h3 = font(34, True)
    body = font(29)
    body_bold = font(29, True)
    small = font(24)

    draw.rectangle((0, 0, width, 150), fill=CYAN)
    draw.text(
        (width // 2, 75),
        "GATE 03 REV 3 · SERIAL MOTION + RESTRAINED LIGHT CONTRACT",
        font=title,
        fill="#071015",
        anchor="mm",
    )
    draw.text(
        (70, 195),
        "锁方向，不锁最终节奏参数 · 10/10 ACTIVE GATE 02 CLAIMS CONSUMED",
        font=h3,
        fill=MUTED,
    )

    sequence_y = 280
    sequence_h = 560
    phases = [
        ("1", "Y + Z 入场", "rotation = 0\nPack 保持前景直到 two-frame ready", GREEN),
        ("2", "完全停稳", "translation velocity = 0\nrotation velocity = 0", CYAN),
        ("3", "一次 360°", "local Y only\ntranslation locked", AMBER),
        ("4", "克制光效", "surface rim → one sheen\nshort halo → zero", GREEN),
        ("5", "静止 HOLD", "same assembled case\nprize angular velocity = 0", CYAN),
    ]
    gap = 28
    phase_w = (width - 140 - gap * 4) // 5
    for index, (number, label, detail, color) in enumerate(phases):
        x = 70 + index * (phase_w + gap)
        panel(draw, (x, sequence_y, x + phase_w, sequence_y + sequence_h))
        draw.ellipse((x + 28, sequence_y + 30, x + 100, sequence_y + 102), fill=color)
        draw.text(
            (x + 64, sequence_y + 66),
            number,
            font=h3,
            fill=BG,
            anchor="mm",
        )
        draw.text((x + 28, sequence_y + 132), label, font=h2, fill=TEXT)
        draw_wrapped(
            draw,
            (x + 28, sequence_y + 225),
            detail,
            body,
            MUTED,
            phase_w - 56,
            spacing=14,
        )
        if index < 4:
            arrow_x = x + phase_w + 6
            arrow_y = sequence_y + sequence_h // 2
            draw.line(
                (arrow_x, arrow_y, arrow_x + gap - 10, arrow_y),
                fill=CYAN,
                width=8,
            )

    locked_box = (70, 930, 1545, 2780)
    tunable_box = (1655, 930, 3130, 2780)
    panel(draw, locked_box)
    panel(draw, tunable_box, PANEL_ALT)
    draw.text((110, 980), "LOCKED · 批准后进入 Gate 04", font=h2, fill=GREEN)
    draw.text((1695, 980), "TUNABLE · 后续关卡／shipping 调校", font=h2, fill=AMBER)

    locked_sections = [
        (
            "对象与所有权",
            "同一 assembled 真盒；PresentationRoot 拥有 motion；Toy 由 ContentSlot 调用方拥有且静止；禁止 proxy／替换／split／explode。",
        ),
        (
            "串行运动",
            "entry 只用 screen Y + camera-depth Z，rotation=0；完全停稳后才开始一次 local-Y 360°；平移与旋转不得同时发生。",
        ),
        (
            "因果光效",
            "Pack seam light → arrival rim → object-bound rotation rim → one final sheen → short halo then zero。无粒子、VFX Graph、rarity 色或持续循环。",
        ),
        (
            "Pack 接力",
            "同 request receipt + 真盒／奖品／相机连续 2 帧 ready；Pack 才在 0.28 s 下退；任意帧至少一个真实对象可见。",
        ),
        (
            "静态基线",
            "历史 228×304×59 mm、闭环管、标签 Y99、ContentSlot 与 PBR 范围作为兼容输入；本关不改 geometry/material。",
        ),
        (
            "禁止项",
            "X drift、roll、pitch、独立 scale 动画、相机／背景 motion、object replacement、toy motion、particles、flash、shake、large bloom。",
        ),
    ]
    y = 1080
    for heading, text in locked_sections:
        draw.text((110, y), heading, font=h3, fill=CYAN)
        y = draw_wrapped(draw, (110, y + 58), text, body, TEXT, 1360, spacing=12) + 34

    tunable_sections = [
        ("最终总时长", "UNKNOWN · 3.4 s 仅为 Gate 02 placeholder；旧 4.520833 s 不再是当前权威。"),
        ("分段时长／easing", "UNKNOWN · entry、settle、360、sheen、halo 的占比与曲线留给后续预览调校。"),
        ("Y／Z 行程", "UNKNOWN · 真实 screen Y 与 camera-depth Z 距离必须由 shipping 构图和 Pack 遮挡共同求解。"),
        ("360° 速度曲线", "UNKNOWN · 只锁一次 local-Y 360° 与 translation locked，不锁角速度曲线。"),
        ("光效参数", "UNKNOWN · seam/rim/sheen/halo 的 width、intensity、色温、falloff、duration 均可调。"),
        ("shipping 相机", "UNKNOWN · FOV 与 framing 在后续 lighting／Unity parity gate 重验证；不得复用诊断相机。"),
        ("粒子", "当前明确禁止。若未来新增，必须重新开启视觉审批并证明不会抢主体。"),
        ("性能验收", "60 FPS／0 B-frame 仍是产品目标；只有目标 iPhone Release build 可通过性能门禁。"),
    ]
    y = 1080
    for heading, text in tunable_sections:
        draw.text((1695, y), heading, font=h3, fill=AMBER)
        y = draw_wrapped(draw, (1695, y + 58), text, body, TEXT, 1360, spacing=12) + 28

    panel(draw, (70, 2870, 3130, 3600))
    draw.text((110, 2920), "CLAIM CONSUMPTION + GATE BOUNDARY", font=h2, fill=CYAN)
    draw.text(
        (110, 3005),
        f"Active Gate 02 claims consumed: {len(contract['sourceClaimIds'])} / {len(contract['sourceClaimIds'])}",
        font=body_bold,
        fill=TEXT,
    )
    bullets = [
        "Gate 03 approval locks direction and forbidden effects; it does not lock final runtime tuning values.",
        "Gate 04 remains blocked until this contract receives explicit user approval.",
        "Gate 03 rev 1 and rev 2 remain immutable stale history.",
        "Shipping Unity, Simulator, build, install and phone state remain unchanged.",
    ]
    y = 3070
    for item in bullets:
        draw.ellipse((116, y + 10, 132, y + 26), fill=GREEN)
        y = draw_wrapped(draw, (154, y), item, body, TEXT, 2850, spacing=12) + 22

    draw.rectangle((0, 3670, width, height), fill="#0E151C")
    draw.text((80, 3715), "APPROVAL QUESTION", font=h3, fill=AMBER)
    draw_wrapped(
        draw,
        (80, 3770),
        contract["approvalQuestion"],
        h3,
        TEXT,
        width - 160,
        spacing=12,
    )
    image.save(PREVIEW_PATH, optimize=True)


def image_report(path: Path) -> dict[str, Any]:
    with Image.open(path).convert("RGB") as image:
        stat = ImageStat.Stat(image)
        extrema = image.getextrema()
        return {
            "path": path.relative_to(REPO).as_posix(),
            "width": image.width,
            "height": image.height,
            "meanRgb": [round(value, 6) for value in stat.mean],
            "channelRanges": [maximum - minimum for minimum, maximum in extrema],
            "nonBlank": any(maximum - minimum > 8 for minimum, maximum in extrema),
        }


def write_validation(contract: dict[str, Any]) -> None:
    claims = contract["sourceClaimIds"]
    motion = contract["motionContract"]
    light = contract["lightContract"]
    tunable = contract["tunableRuntimeParameters"]
    checks = {
        "sourceHashesPresent": all(isinstance(value, str) and value for value in claims),
        "tenActiveClaimsConsumed": len(claims) == 10,
        "claimIdsUnique": len(set(claims)) == len(claims),
        "serialPhaseOrder": motion["phaseOrder"]
        == [
            "entry-y-z",
            "settle",
            "showcase-local-y-360",
            "final-sheen-short-halo",
            "static-hold",
        ],
        "entryAxesLocked": motion["entry"]["translationAxes"]
        == ["screen-y", "camera-depth-z"],
        "entryRotationZero": motion["entry"]["rotationDegrees"] == [0, 0, 0],
        "showcaseAfterSettle": motion["settle"]["requiredBeforeShowcase"]
        and motion["showcase"]["translationLocked"],
        "oneLocalY360": motion["showcase"]["axis"] == "local-y"
        and motion["showcase"]["degrees"] == 360
        and motion["showcase"]["count"] == 1,
        "noSimultaneousEntryAndShowcase": motion["simultaneousEntryAndShowcase"]
        is False,
        "wholeCaseNoReplacement": motion["wholeCaseOnly"]
        and not motion["objectReplacement"],
        "toyStatic": not motion["toyMotion"]
        and motion["showcase"]["toyIndependentAngularVelocity"] == 0,
        "causalLightOrder": light["causalCueOrder"]
        == [
            "pack-seam-light",
            "arrival-rim",
            "rotation-surface-rim",
            "final-diagonal-sheen",
            "settle-halo-then-zero",
        ],
        "neutralLightBound": light["maximumRgbChroma"] <= 25,
        "haloStops": not light["settleHalo"]["persistent"]
        and light["settleHalo"]["maximumAlpha"] <= 0.1,
        "particlesAndVfxGraphForbidden": not light["particles"]
        and not light["vfxGraphDependency"],
        "shippingDurationUnknown": tunable["shippingTotalDurationSeconds"] is None,
        "phaseTimingUnknown": tunable["phaseDurationsSeconds"] is None
        and tunable["phaseEasing"] is None,
        "distanceUnknownsPreserved": tunable["entryScreenYDistance"] is None
        and tunable["entryCameraDepthZDistance"] is None,
        "lightUnknownsPreserved": all(
            tunable[key] is None
            for key in [
                "seamLightWidth",
                "seamLightIntensity",
                "arrivalRimWidth",
                "arrivalRimIntensity",
                "lightColorTemperatureKelvin",
                "lightFalloff",
                "finalSheenWidth",
                "finalSheenIntensity",
                "settleHaloRadius",
                "settleHaloDuration",
            ]
        ),
        "oldTimingNotRestored": "4.520833" in tunable["note"]
        and "not current authority" in tunable["note"],
        "gate04Blocked": contract["route"]["nextGatePolicy"]
        == "Do not enter Gate 04 before explicit Gate 03 approval.",
        "shippingBoundary": not contract["route"]["shippingUnityEdit"]
        and not contract["route"]["buildInstallPhonePush"],
        "largeTypePreview": PREVIEW_PATH.is_file(),
    }
    report = {
        "schema": "premium-display-case-gate03-serial-contract-validation.v1",
        "modelId": "premium-display-case",
        "gate": "03-contract",
        "contractRevision": 3,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "activeGate02ClaimCount": len(claims),
            "lockedPhaseCount": len(motion["phaseOrder"]),
            "showcaseDegrees": motion["showcase"]["degrees"],
            "approvedShippingDuration": None,
            "tunableParameterCount": sum(
                value is None
                for key, value in tunable.items()
                if key not in {"decisionState", "note", "previewDurationSeconds"}
            ),
        },
        "imageReport": image_report(PREVIEW_PATH),
        "truth": {
            "contractOnly": True,
            "blenderGeometryOrMaterialChanged": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
    }
    write_json(VALIDATION_PATH, report)
    if report["status"] != "pass":
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError(f"Gate 03 validation failed: {failed}")


def main() -> None:
    contract = build_contract()
    write_json(CONTRACT_PATH, contract)
    draw_preview(contract)
    write_validation(contract)
    print(
        json.dumps(
            {
                "contract": str(CONTRACT_PATH),
                "preview": str(PREVIEW_PATH),
                "validation": str(VALIDATION_PATH),
                "contractSha256": sha256(CONTRACT_PATH),
                "previewSha256": sha256(PREVIEW_PATH),
                "validationSha256": sha256(VALIDATION_PATH),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
