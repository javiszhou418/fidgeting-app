#!/usr/bin/env python3
"""Compose and validate Premium Display Case Gate 07 rev 2 review evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
MASKS = ROOT / "masks"
BUILD_REPORT = ROOT / "material-revalidation.json"
ZONE_REPORT = ROOT / "material-zone-mask-report.json"
MP4 = ROOT / "material-turntable.mp4"
GIF = ROOT / "material-turntable.gif"
BOARD = ROOT / "material-board.png"
CLOSEUPS = ROOT / "material-closeups.png"
CONTACT = ROOT / "material-turntable-contact-sheet.png"
MASK_BOARD = ROOT / "mesh-clipped-sheen-compatibility.png"
MASK_DIAGNOSTIC = ROOT / "mesh-clipped-sheen-mask.png"
VALIDATION = ROOT / "material-review-validation.json"
SNAPSHOT = ROOT / "material-compatibility-snapshot.json"

BACKGROUND = (12, 15, 19)
PANEL = (23, 28, 34)
BORDER = (57, 68, 79)
TEXT = (241, 245, 248)
MUTED = (171, 184, 197)
ACCENT = (142, 214, 225)
PASS = (150, 211, 178)
CARDINAL_TO_INDEX = {0: 0, 90: 6, 180: 12, 270: 18, 360: 24}
CHECKLIST = (
    "watch-full-turntable",
    "inspect-front-edge-reverse-front",
    "inspect-tube-corner-continuity",
    "inspect-label-tactile-foil",
    "confirm-sheen-mask-zero-outside-subject",
    "confirm-no-branding-toy-or-exploded-content",
)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(ROOT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False):
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    maximum_width: int,
    start_size: int,
    minimum_size: int,
    bold: bool = False,
):
    for size in range(start_size, minimum_size - 1, -1):
        candidate = font(size, bold=bold)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= maximum_width:
            return candidate
    return font(minimum_size, bold=bold)


def centered(
    draw: ImageDraw.ImageDraw,
    width: int,
    y: int,
    text: str,
    text_font,
    fill: tuple[int, int, int],
) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text(((width - (box[2] - box[0])) / 2, y), text, font=text_font, fill=fill)


def panel(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    image: Image.Image,
    note: str = "",
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=24, fill=PANEL, outline=BORDER, width=3)
    label_font = fit_font(draw, label, x1 - x0 - 40, 34, 21, bold=True)
    label_box = draw.textbbox((0, 0), label, font=label_font)
    draw.text(
        (x0 + (x1 - x0 - (label_box[2] - label_box[0])) / 2, y0 + 18),
        label,
        font=label_font,
        fill=TEXT,
    )
    note_height = 42 if note else 0
    available = (x1 - x0 - 36, y1 - y0 - 96 - note_height)
    if image.mode == "RGBA":
        image = Image.alpha_composite(
            Image.new("RGBA", image.size, (*BACKGROUND, 255)),
            image,
        ).convert("RGB")
    else:
        image = image.convert("RGB")
    fitted = ImageOps.contain(image, available, Image.Resampling.LANCZOS)
    canvas.paste(
        fitted,
        (
            x0 + (x1 - x0 - fitted.width) // 2,
            y0 + 72 + (available[1] - fitted.height) // 2,
        ),
    )
    if note:
        note_font = fit_font(draw, note, x1 - x0 - 40, 24, 16)
        note_box = draw.textbbox((0, 0), note, font=note_font)
        draw.text(
            (
                x0 + (x1 - x0 - (note_box[2] - note_box[0])) / 2,
                y1 - 43,
            ),
            note,
            font=note_font,
            fill=MUTED,
        )


def header(
    canvas: Image.Image,
    title: str,
    subtitle: str,
    status: str,
) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(canvas)
    centered(draw, canvas.width, 34, title, font(49, bold=True), TEXT)
    centered(draw, canvas.width, 100, subtitle, font(27), MUTED)
    centered(draw, canvas.width, 140, status, font(25, bold=True), PASS)
    return draw


def alpha_mask(path: Path) -> np.ndarray:
    image = np.asarray(Image.open(path).convert("RGBA"), dtype=np.uint8)
    return image[:, :, 3] > 16


def luma(image: np.ndarray) -> np.ndarray:
    rgb = image[:, :, :3].astype(np.float32)
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def image_metrics(image_path: Path, subject_path: Path, tube_path: Path) -> dict[str, object]:
    image = np.asarray(Image.open(image_path).convert("RGBA"), dtype=np.uint8)
    subject = alpha_mask(subject_path)
    tube = alpha_mask(tube_path)
    values = luma(image)
    subject_values = values[subject]
    tube_values = values[tube]
    rgb = image[:, :, :3]
    yellow = (
        (rgb[:, :, 0] > 150)
        & (rgb[:, :, 1] > 105)
        & (rgb[:, :, 2] < 90)
        & subject
    )
    return {
        "subjectPixelCount": int(np.count_nonzero(subject)),
        "meanSubjectLuma": round(float(np.mean(subject_values)), 6),
        "p01SubjectLuma": round(float(np.percentile(subject_values, 1)), 6),
        "p99SubjectLuma": round(float(np.percentile(subject_values, 99)), 6),
        "subjectHighClipFraction": round(
            float(np.count_nonzero(subject_values >= 253) / subject_values.size), 9
        ),
        "yellowIdentityFraction": round(
            float(np.count_nonzero(yellow) / np.count_nonzero(subject)), 9
        ),
        "tubePixelCount": int(np.count_nonzero(tube)),
        "tubeP10Luma": round(float(np.percentile(tube_values, 10)), 6),
        "tubeP90Luma": round(float(np.percentile(tube_values, 90)), 6),
        "tubeHighlightContrast": round(
            float(np.percentile(tube_values, 90) - np.percentile(tube_values, 10)),
            6,
        ),
    }


def generate_sheen_diagnostics() -> dict[str, object]:
    orientation_reports = {}
    overlays = {}
    for angle, index in CARDINAL_TO_INDEX.items():
        subject = alpha_mask(MASKS / f"subject-{angle:03d}.png")
        eligible = alpha_mask(MASKS / f"sheen-eligible-{angle:03d}.png")
        label = alpha_mask(MASKS / f"label-zone-{angle:03d}.png")
        insert = alpha_mask(MASKS / f"insert-zone-{angle:03d}.png")
        allowed = eligible & ~label & ~insert
        height, width = allowed.shape
        yy, xx = np.mgrid[0:height, 0:width]
        center = 0.40 * width + 0.22 * height
        distance = np.abs(xx + 0.22 * yy - center)
        band = np.exp(-((distance / max(12.0, width * 0.035)) ** 2))
        clipped = np.where(allowed, band, 0.0)
        active = clipped > 0.05
        outside_subject = int(np.count_nonzero(active & ~subject))
        outside_allowed = int(np.count_nonzero(active & ~allowed))
        eligible_outside_subject = int(np.count_nonzero(eligible & ~subject))
        mask_rgb = np.zeros((height, width, 4), dtype=np.uint8)
        mask_rgb[:, :, :3] = 255
        mask_rgb[:, :, 3] = np.clip(clipped * 255.0, 0, 255).astype(np.uint8)
        mask_path = MASKS / f"clipped-sheen-{angle:03d}.png"
        Image.fromarray(mask_rgb, mode="RGBA").save(mask_path)

        base = Image.open(RAW / f"turn-{index:03d}.png").convert("RGBA")
        cyan = Image.new("RGBA", base.size, (*ACCENT, 0))
        cyan.putalpha(Image.open(mask_path).getchannel("A").point(lambda value: value // 2))
        overlay = Image.alpha_composite(base, cyan)
        overlay_path = MASKS / f"clipped-sheen-overlay-{angle:03d}.png"
        overlay.save(overlay_path)
        overlays[angle] = overlay
        orientation_reports[str(angle)] = {
            "subjectPixels": int(np.count_nonzero(subject)),
            "eligiblePixels": int(np.count_nonzero(eligible)),
            "allowedMaterialZonePixels": int(np.count_nonzero(allowed)),
            "activeSheenPixels": int(np.count_nonzero(active)),
            "eligibleOutsideSubjectPixels": eligible_outside_subject,
            "activeOutsideSubjectPixels": outside_subject,
            "activeOutsideAllowedMaterialZonePixels": outside_allowed,
            "maskPath": str(mask_path.relative_to(REPO_ROOT)),
            "maskSha256": sha256(mask_path),
            "overlayPath": str(overlay_path.relative_to(REPO_ROOT)),
            "overlaySha256": sha256(overlay_path),
        }

    Image.open(MASKS / "clipped-sheen-000.png").save(MASK_DIAGNOSTIC)
    return {
        "orientations": orientation_reports,
        "overlays": overlays,
        "maximumOutsideSubjectPixels": max(
            report["activeOutsideSubjectPixels"]
            for report in orientation_reports.values()
        ),
        "maximumOutsideAllowedMaterialZonePixels": max(
            report["activeOutsideAllowedMaterialZonePixels"]
            for report in orientation_reports.values()
        ),
        "maximumEligibleOutsideSubjectPixels": max(
            report["eligibleOutsideSubjectPixels"]
            for report in orientation_reports.values()
        ),
    }


def compose_boards(diagnostics: dict[str, object]) -> None:
    board = Image.new("RGB", (2400, 1750), BACKGROUND)
    draw = header(
        board,
        "GATE 07 · MATERIAL REVALIDATION",
        "FRONT · EDGE · REVERSE · FRONT RETURN · ONE RIGID ASSEMBLED CASE",
        "READY FOR REVIEW · NOT APPROVED · GATE 08 BLOCKED",
    )
    panel(
        board,
        draw,
        (60, 205, 1170, 930),
        "FRONT · 0°",
        Image.open(RAW / "front.png"),
        "Frosted shell · neutral paper · black tactile insert",
    )
    panel(
        board,
        draw,
        (1230, 205, 2340, 930),
        "EDGE · 90°",
        Image.open(RAW / "edge.png"),
        "Transparent ordering · edge response",
    )
    panel(
        board,
        draw,
        (60, 975, 1170, 1665),
        "REVERSE · 180°",
        Image.open(RAW / "reverse.png"),
        "Same materials and geometry from reverse",
    )
    panel(
        board,
        draw,
        (1230, 975, 2340, 1665),
        "FRONT RETURN · 360°",
        Image.open(RAW / "front-return.png"),
        "Object-local grain returns without drift",
    )
    board.save(BOARD)

    closeups = Image.new("RGB", (2400, 1560), BACKGROUND)
    draw = header(
        closeups,
        "MATERIAL BOUNDARIES · USEFUL CLOSEUPS",
        "REAL CYCLES RENDERS · NEUTRAL REVIEW ENVIRONMENT",
        "NO EXPLODE · NO TOY · NO SHIPPING LIGHTING",
    )
    panel(
        closeups,
        draw,
        (60, 205, 1180, 855),
        "TUBE CORNER",
        Image.open(RAW / "tube-corner.png"),
        "Continuous highlight through the rounded corner",
    )
    panel(
        closeups,
        draw,
        (1220, 205, 2340, 855),
        "LABEL + RESTRAINED FOIL",
        Image.open(RAW / "label-closeup.png"),
        "Neutral identity placeholders; excluded brand cues",
    )
    panel(
        closeups,
        draw,
        (350, 900, 2050, 1480),
        "BLACK TACTILE INSERT",
        Image.open(RAW / "tactile-closeup.png"),
        "Object-local micrograin; no world-space swim",
    )
    closeups.save(CLOSEUPS)

    contact = Image.new("RGB", (2400, 1520), BACKGROUND)
    draw = header(
        contact,
        "REAL 360° MATERIAL TURNTABLE · CONTACT SHEET",
        "SAMPLED FROM 25 CYCLES FRAMES · 0° → 360°",
        "MATERIAL RESPONSE ONLY · RUNTIME TIMING NOT BAKED",
    )
    sample_indices = (0, 3, 6, 9, 12, 15, 18, 21)
    for position, index in enumerate(sample_indices):
        row, column = divmod(position, 4)
        x0 = 50 + column * 590
        y0 = 200 + row * 630
        panel(
            contact,
            draw,
            (x0, y0, x0 + 540, y0 + 585),
            f"{index * 15}°",
            Image.open(RAW / f"turn-{index:03d}.png"),
        )
    contact.save(CONTACT)

    mask_board = Image.new("RGB", (2400, 1410), BACKGROUND)
    draw = header(
        mask_board,
        "UNITY SHEEN MASK · MATERIAL COMPATIBILITY",
        "DIAGNOSTIC ONLY · OBJECT-LOCAL · MESH-CLIPPED",
        "0 LIGHT PIXELS OUTSIDE SUBJECT · NO HALO · NO LIGHT GEOMETRY",
    )
    panel(
        mask_board,
        draw,
        (60, 210, 810, 1120),
        "FRONT MATERIAL",
        Image.open(RAW / "turn-000.png"),
    )
    panel(
        mask_board,
        draw,
        (825, 210, 1575, 1120),
        "CLIPPED MASK",
        Image.open(MASK_DIAGNOSTIC),
        "Shell/tube zones; label and insert excluded",
    )
    panel(
        mask_board,
        draw,
        (1590, 210, 2340, 1120),
        "DIAGNOSTIC OVERLAY",
        diagnostics["overlays"][0],
        "Not runtime timing; no external halo",
    )
    metric_font = font(28)
    metric_lines = (
        f"Outside subject: {diagnostics['maximumOutsideSubjectPixels']} px",
        "Outside allowed material zones: "
        f"{diagnostics['maximumOutsideAllowedMaterialZonePixels']} px",
        f"Eligible mask outside subject: {diagnostics['maximumEligibleOutsideSubjectPixels']} px",
        "Final sheen owner: Unity MaterialPropertyBlock · object-local mesh mask",
    )
    for index, line in enumerate(metric_lines):
        centered(draw, mask_board.width, 1190 + index * 43, line, metric_font, ACCENT)
    mask_board.save(MASK_BOARD)


def ffprobe() -> dict[str, object]:
    output = subprocess.run(
        (
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height,avg_frame_rate,nb_frames",
            "-of",
            "json",
            str(MP4),
        ),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(output.stdout)


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    zone = json.loads(ZONE_REPORT.read_text(encoding="utf-8"))
    diagnostics = generate_sheen_diagnostics()
    orientation_metrics = {}
    for angle, index in CARDINAL_TO_INDEX.items():
        orientation_metrics[str(angle)] = image_metrics(
            RAW / f"turn-{index:03d}.png",
            MASKS / f"subject-{angle:03d}.png",
            MASKS / f"tube-{angle:03d}.png",
        )
    frames = [
        np.asarray(Image.open(RAW / f"turn-{index:03d}.png").convert("RGB"))
        for index in range(25)
    ]
    frame_mean_luma = [float(np.mean(luma(frame))) for frame in frames]
    maximum_adjacent_mean_delta = max(
        abs(current - previous)
        for previous, current in zip(frame_mean_luma, frame_mean_luma[1:])
    )
    front_return_mae = float(
        np.mean(np.abs(frames[0].astype(np.float32) - frames[-1].astype(np.float32)))
    )
    tube_contrasts = [
        metrics["tubeHighlightContrast"] for metrics in orientation_metrics.values()
    ]
    compose_boards(diagnostics)
    video_probe = ffprobe()

    checks = {
        "blenderRevalidationPassed": build["status"] == "pass",
        "materialZoneMaskRenderPassed": zone["status"] == "pass",
        "realTurntableHas25Frames": int(video_probe["streams"][0]["nb_frames"]) == 25,
        "frontReturnStable": front_return_mae <= 1.5,
        "turntableNoAbruptMeanFlicker": maximum_adjacent_mean_delta <= 14.0,
        "transparentOrderingReadable": all(
            metrics["meanSubjectLuma"] >= 14.0
            and metrics["p99SubjectLuma"] <= 250.0
            and metrics["subjectHighClipFraction"] <= 0.001
            for metrics in orientation_metrics.values()
        ),
        "continuousTubeHighlights": min(tube_contrasts) >= 5.0,
        "yellowIdentityExcluded": max(
            metrics["yellowIdentityFraction"] for metrics in orientation_metrics.values()
        )
        <= 0.001,
        "eligibleMaskConfinedToSubject": (
            diagnostics["maximumEligibleOutsideSubjectPixels"] == 0
        ),
        "sheenConfinedToSubject": diagnostics["maximumOutsideSubjectPixels"] == 0,
        "sheenConfinedToMaterialZones": (
            diagnostics["maximumOutsideAllowedMaterialZonePixels"] == 0
        ),
        "materialBoardPresent": BOARD.exists(),
        "closeupsPresent": CLOSEUPS.exists(),
        "contactSheetPresent": CONTACT.exists(),
        "maskBoardPresent": MASK_BOARD.exists(),
        "wholeCaseOnly": build["scope"]["wholeAssembledCaseOnly"],
        "reviewExplodedPartCountZero": build["scope"]["reviewExplodedPartCount"] == 0,
        "noRuntimeTimingOrFinalLighting": (
            not build["sourceGate04"]["runtimeTimingIncluded"]
            and build["render"]["neutralReviewEnvironmentOnly"]
            and not build["render"]["gate08FinalLighting"]
        ),
        "forbiddenEffectsAbsent": all(
            not build["scope"][key]
            for key in (
                "lightGeometryAdded",
                "externalHalo",
                "particles",
                "vfxGraph",
                "bloomDependency",
                "persistentEmission",
            )
        ),
        "shippingUnityUnchanged": not build["scope"]["shippingUnityChanged"],
        "buildInstallPhonePushFalse": not build["scope"]["buildInstallPhonePush"],
    }
    snapshot = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 2,
        "sourceGate06Approval": build["sourceGate06"]["approval"],
        "sourceGate04": build["sourceGate04"],
        "geometryIdentity": build["sourceGate06"]["geometryIdentity"],
        "boundsMm": build["sourceGate06"]["boundsMm"],
        "materialAssignments": build["materialAssignments"],
        "materialParameters": build["materialParameters"],
        "materialGraphDigests": build["materialGraphDigestsAfter"],
        "objectLocalGrain": build["objectLocalGrain"],
        "sheenMaskPolicy": {
            "owner": "Unity MaterialPropertyBlock",
            "coordinateSpace": "object-local",
            "eligibleMaterialZones": [
                "frosted polycarbonate shells",
                "continuous tube edge",
            ],
            "excludedMaterialZones": [
                "label paper",
                "black tactile insert",
                "caller-owned toy",
            ],
            "outsideSubjectPixels": diagnostics["maximumOutsideSubjectPixels"],
            "outsideAllowedMaterialZonePixels": diagnostics[
                "maximumOutsideAllowedMaterialZonePixels"
            ],
            "runtimeTimingIncluded": False,
            "geometryAdded": False,
        },
        "approvalChecklist": list(CHECKLIST),
        "gate08Status": "blocked",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "07-material",
        "materialRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "notice": "READY FOR MATERIAL REVIEW · NOT APPROVED · GATE 08 BLOCKED",
        "orientationMetrics": orientation_metrics,
        "turntableMetrics": {
            "frameCount": 25,
            "frontReturnMeanAbsoluteChannelDelta": round(front_return_mae, 9),
            "maximumAdjacentMeanLumaDelta": round(maximum_adjacent_mean_delta, 9),
            "minimumCardinalTubeHighlightContrast": round(min(tube_contrasts), 6),
        },
        "sheenMaskCompatibility": {
            key: value
            for key, value in diagnostics.items()
            if key != "overlays"
        },
        "videoProbe": video_probe,
        "artifacts": {
            path.name: {"sha256": sha256(path), "sizeBytes": path.stat().st_size}
            for path in (
                MP4,
                GIF,
                BOARD,
                CLOSEUPS,
                CONTACT,
                MASK_BOARD,
                MASK_DIAGNOSTIC,
                SNAPSHOT,
            )
        },
        "approvalChecklist": list(CHECKLIST),
        "checks": checks,
        "scope": {
            "wholeAssembledCaseOnly": True,
            "reviewExplodedPartCount": 0,
            "neutralMaterialEnvironmentOnly": True,
            "finalLightingApproved": False,
            "runtimeTimingIncluded": False,
            "shippingUnityChanged": False,
            "buildInstallPhonePush": False,
        },
    }
    VALIDATION.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(
            "Gate 07 rev 2 image validation failed: "
            + ", ".join(name for name, passed in checks.items() if not passed)
        )
    print(
        json.dumps(
            {
                "status": report["status"],
                "board": str(BOARD),
                "turntable": str(MP4),
                "maskOutsidePixels": diagnostics["maximumOutsideSubjectPixels"],
            }
        )
    )


if __name__ == "__main__":
    main()
