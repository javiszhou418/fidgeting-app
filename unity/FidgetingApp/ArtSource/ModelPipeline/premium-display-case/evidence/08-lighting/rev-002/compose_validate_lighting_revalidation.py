#!/usr/bin/env python3
"""Compose and validate Gate 08 rev 2 lighting review evidence."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
LEGACY_COMPOSER = ROOT.parent / "rev-001/compose_and_validate_lighting.py"
BUILD_REPORT = ROOT / "lighting-revalidation.json"
IMAGE_REPORT = ROOT / "lighting-image-validation.json"
SNAPSHOT = ROOT / "lighting-compatibility-snapshot.json"
TURNTABLE_REPORT = ROOT / "lighting-turntable-report.json"
GATE07 = ROOT.parent.parent / "07-material/rev-002"
LABEL_BOARD = ROOT / "label-placeholder-review.png"
SHEEN_BOARD = ROOT / "mesh-clipped-sheen-compatibility.png"
APPROVAL_QUOTE = "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False):
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        (
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Helvetica.ttf"
        ),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def centered(draw: ImageDraw.ImageDraw, width: int, y: int, text: str, size: int, color):
    text_font = font(size, bold=True)
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text(
        ((width - (box[2] - box[0])) / 2, y),
        text,
        font=text_font,
        fill=color,
    )


def warning_review(source: Path, target: Path) -> None:
    image = Image.open(source).convert("RGB")
    width = max(1800, image.width)
    header = 240
    footer = 210
    canvas = Image.new("RGB", (width, image.height + header + footer), (13, 16, 20))
    draw = ImageDraw.Draw(canvas)
    centered(
        draw,
        width,
        30,
        "LABEL CONTENT: PLACEHOLDER · NOT APPROVED",
        58,
        (247, 202, 117),
    )
    centered(
        draw,
        width,
        112,
        "UNITY WILL SUPPLY REAL PRODUCT NAME · EDITION / FINISH · DATE · RARITY / LEVEL",
        30,
        (235, 239, 244),
    )
    centered(
        draw,
        width,
        164,
        "COLLECTIBLE ID APPEARS ONLY WHEN A REAL ID EXISTS",
        28,
        (182, 197, 210),
    )
    fitted = ImageOps.contain(image, (width, image.height), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((width - fitted.width) // 2, header))
    centered(
        draw,
        width,
        header + image.height + 34,
        "BLENDER APPROVAL: LABEL GEOMETRY / UV / PAPER / COVER / FOIL ZONES ONLY",
        30,
        (161, 217, 188),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, optimize=True)


def sheen_review(target: Path) -> dict[str, int]:
    active_path = GATE07 / "masks/clipped-sheen-000.png"
    overlay_path = GATE07 / "masks/clipped-sheen-overlay-000.png"
    subject_path = GATE07 / "masks/subject-000.png"
    eligible_path = GATE07 / "masks/sheen-eligible-000.png"
    active = np.asarray(Image.open(active_path).convert("RGBA"))[:, :, 3] > 16
    subject = np.asarray(Image.open(subject_path).convert("RGBA"))[:, :, 3] > 16
    eligible = np.asarray(Image.open(eligible_path).convert("RGBA"))[:, :, 3] > 16
    outside_subject = int(np.count_nonzero(active & ~subject))
    outside_eligible = int(np.count_nonzero(active & ~eligible))
    overlay = Image.open(overlay_path).convert("RGB")
    width = max(2200, overlay.width)
    canvas = Image.new("RGB", (width, overlay.height + 430), (13, 16, 20))
    draw = ImageDraw.Draw(canvas)
    centered(
        draw,
        width,
        28,
        "MESH-CLIPPED SHEEN · COMPATIBILITY FRAME",
        54,
        (235, 239, 244),
    )
    centered(
        draw,
        width,
        108,
        "MATERIAL / RUNTIME CUE · NOT AN EXTERNAL LIGHT OR HALO",
        32,
        (175, 216, 230),
    )
    fitted = ImageOps.contain(overlay, (width, overlay.height), Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((width - fitted.width) // 2, 180))
    result = (
        f"EFFECT PIXELS OUTSIDE CASE: {outside_subject}   ·   "
        f"OUTSIDE ALLOWED MATERIAL ZONES: {outside_eligible}"
    )
    centered(
        draw,
        width,
        overlay.height + 222,
        result,
        34,
        (160, 218, 185) if outside_subject == 0 and outside_eligible == 0
        else (244, 133, 128),
    )
    centered(
        draw,
        width,
        overlay.height + 286,
        "NO EXTERNAL HALO · NO POINT LIGHT · NO BLOOM DEPENDENCY",
        28,
        (190, 199, 210),
    )
    canvas.save(target, optimize=True)
    return {
        "outsideSubjectPixels": outside_subject,
        "outsideAllowedMaterialZonePixels": outside_eligible,
    }


def append_label_boundary(board: Path) -> None:
    image = Image.open(board).convert("RGB")
    band = 170
    canvas = Image.new("RGB", (image.width, image.height + band), (13, 16, 20))
    canvas.paste(image, (0, 0))
    draw = ImageDraw.Draw(canvas)
    centered(
        draw,
        image.width,
        image.height + 24,
        "LABEL IS PLACEHOLDER / NOT APPROVED · AUTHORITATIVE CONTENT COMES FROM UNITY REAL DATA",
        34,
        (247, 202, 117),
    )
    centered(
        draw,
        image.width,
        image.height + 88,
        "ALL CAMERA / LIGHT / EXPOSURE VALUES ARE LOOKDEV CANDIDATES, NOT UNITY CONSTANTS",
        28,
        (177, 207, 221),
    )
    canvas.save(board, optimize=True)


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    turntable = json.loads(TURNTABLE_REPORT.read_text(encoding="utf-8"))
    if build["status"] != "pass" or build["lightingRevision"] != 2:
        raise RuntimeError("Gate 08 rev 2 build report did not pass.")
    if turntable["status"] != "pass" or turntable["frameCount"] != 13:
        raise RuntimeError("Gate 08 rev 2 real lighting turntable did not pass.")
    legacy = load_module("premium_display_case_gate08_rev2_legacy_composer", LEGACY_COMPOSER)
    legacy.ROOT = ROOT
    legacy.RAW = RAW
    legacy.BUILD_REPORT = BUILD_REPORT
    legacy.IMAGE_REPORT = IMAGE_REPORT
    legacy.TITLE = "GATE 08 REV 2 LIGHTING REVIEW · WHOLE CASE ONLY"
    legacy.STATUS = "READY FOR REVIEW · NOT APPROVED · GATE 09 NOT STARTED"
    legacy.FOOTER = (
        "APPROVED GATE 07 REV 2 MATERIALS · LABEL CONTENT PLACEHOLDER · "
        "BLENDER VALUES ARE LOOKDEV CANDIDATES"
    )
    legacy.main()

    warning_review(RAW / "label-closeup.png", LABEL_BOARD)
    sheen = sheen_review(SHEEN_BOARD)
    append_label_boundary(ROOT / "lighting-review.png")
    append_label_boundary(ROOT / "lighting-details-contact-sheet.png")

    report = json.loads(IMAGE_REPORT.read_text(encoding="utf-8"))
    report["lightingRevision"] = 2
    report["notice"] = "GATE 08 REV 2 LIGHTING · READY FOR REVIEW · NOT APPROVED"
    maximum_clip = max(
        item["highlightClipFraction"] for item in report["rawMetrics"].values()
    )
    black_panel = report["blackPanelMetrics"]
    report["labelPolicy"] = {
        "visibleMarker": "placeholder-not-approved",
        "authoritativeRuntimeOwner": "Unity",
        "approvalQuote": APPROVAL_QUOTE,
        "reviewArtifact": str(LABEL_BOARD.relative_to(legacy.REPO_ROOT)),
    }
    report["sheenCompatibility"] = {
        **sheen,
        "classification": "material-runtime compatibility frame",
        "externalLightSpill": False,
        "reviewArtifact": str(SHEEN_BOARD.relative_to(legacy.REPO_ROOT)),
    }
    report["checks"].update(
        {
            "requiredHeroLeftRightLowPresent": all(
                (RAW / f"{name}.png").exists()
                for name in ("hero", "left-oblique", "right-oblique", "low")
            ),
            "requiredBeautyClayNormalDepthRoughnessPresent": all(
                (RAW / f"pass-{name}.png").exists()
                for name in ("beauty", "clay", "normal", "depth", "roughness")
            ),
            "whitesNotClipped": maximum_clip <= 0.005,
            "blackInsertNotCrushed": (
                black_panel["medianLuma"] >= 8.0
                and black_panel["crushedBelow4Fraction"] <= 0.30
            ),
            "placeholderLabelMarkedNotApproved": LABEL_BOARD.exists(),
            "meshClippedSheenOutsideSubjectZero": sheen["outsideSubjectPixels"] == 0,
            "meshClippedSheenOutsideAllowedZonesZero": (
                sheen["outsideAllowedMaterialZonePixels"] == 0
            ),
            "noExternalHaloBloomParticlesOrPersistentEmission": all(
                value is False for value in build["forbiddenEffects"].values()
            ),
            "lookdevValuesRemainCandidates": (
                build["candidateBoundary"]["blenderLookdevCandidatesOnly"]
                and not build["candidateBoundary"]["automaticUnityRuntimeConstants"]
            ),
            "runtimeTimingAndEasingNotBaked": (
                not build["animationBoundary"]["timingBaked"]
                and not build["animationBoundary"]["easingBaked"]
            ),
            "realLightingTurntablePassed": all(turntable["checks"].values()),
        }
    )
    artifacts = {
        "lighting-review": ROOT / "lighting-review.png",
        "lighting-details": ROOT / "lighting-details-contact-sheet.png",
        "lighting-passes": ROOT / "lighting-passes-contact-sheet.png",
        "lighting-parameters": ROOT / "lighting-parameters-board.png",
        "label-placeholder": LABEL_BOARD,
        "mesh-clipped-sheen": SHEEN_BOARD,
        "lighting-turntable": ROOT / "lighting-turntable.mp4",
        "lighting-turntable-contact": ROOT / "lighting-turntable-contact-sheet.png",
    }
    report["artifacts"] = {
        name: {
            "path": str(path.relative_to(legacy.REPO_ROOT)),
            "sha256": sha256(path),
            "sizeBytes": path.stat().st_size,
        }
        for name, path in artifacts.items()
    }
    report["status"] = "pass" if all(report["checks"].values()) else "fail"
    IMAGE_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    build["outputs"].update(
        {
            "labelPlaceholderReview": str(LABEL_BOARD.relative_to(legacy.REPO_ROOT)),
            "meshClippedSheenCompatibility": str(
                SHEEN_BOARD.relative_to(legacy.REPO_ROOT)
            ),
            "lightingReview": str(
                (ROOT / "lighting-review.png").relative_to(legacy.REPO_ROOT)
            ),
        }
    )
    BUILD_REPORT.write_text(
        json.dumps(build, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    snapshot = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 2,
        "sourceMaterialRevision": 2,
        "sourceArchitectureEvidenceRevision": 7,
        "geometryDigest": build["geometry"]["digestAfter"],
        "materialDigest": build["materials"]["digestAfter"],
        "wholeAssembledCaseOnly": True,
        "reviewExplodedPartCount": 0,
        "labelContentApproved": False,
        "labelRuntimeAuthority": "Unity real product data",
        "meshClippedSheen": build["sheenCompatibility"],
        "candidateBoundary": build["candidateBoundary"],
        "animationBoundary": build["animationBoundary"],
        "forbiddenEffects": build["forbiddenEffects"],
        "lightingCandidates": build["lighting"],
        "cameraCandidates": build["cameras"],
        "renderCandidates": build["render"],
        "realLightingTurntable": {
            "frameCount": turntable["frameCount"],
            "angleStepDegrees": turntable["angleStepDegrees"],
            "durationSeconds": turntable["durationSeconds"],
            "videoSha256": turntable["videoSha256"],
            "contactSheetSha256": turntable["contactSheetSha256"],
            "assemblyState": turntable["assemblyState"],
            "runtimeTimingBaked": turntable["runtimeTimingBaked"],
        },
        "approvalChecklist": [
            "inspect-hero-left-right-low",
            "inspect-beauty-clay-normal-depth-roughness",
            "inspect-frosted-shell-closed-tube-black-insert-label-zones",
            "confirm-no-clipped-whites-or-crushed-darks",
            "confirm-neutral-no-green-rarity-halo-bloom-particles",
            "confirm-placeholder-label-not-approved",
            "confirm-mesh-clipped-sheen-zero-outside-silhouette",
            "confirm-lookdev-values-remain-candidates",
            "confirm-no-blender-timing-or-easing-bake",
        ],
        "gate08Status": "ready_for_review",
        "gate09Status": "blocked",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    SNAPSHOT.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report["checks"], ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "status": report["status"],
                "maximumClipFraction": maximum_clip,
                "blackPanelMedianLuma": black_panel["medianLuma"],
                "outsideSubjectPixels": sheen["outsideSubjectPixels"],
                "review": str(ROOT / "lighting-review.png"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
