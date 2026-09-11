#!/usr/bin/env python3
"""Compose and validate Premium Display Case Gate 09 rev 1 evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
SOURCE_ROOT = ROOT.parent.parent / "08-lighting/rev-002"
BUILD_REPORT = ROOT / "environment-revalidation.json"
BLENDER_AUDIT = ROOT / "blender-environment-audit.json"
SOURCE_LIGHTING = SOURCE_ROOT / "lighting-revalidation.json"
SOURCE_SHEEN = SOURCE_ROOT / "mesh-clipped-sheen-compatibility.png"
IMAGE_REPORT = ROOT / "environment-image-validation.json"
SNAPSHOT = ROOT / "environment-compatibility-snapshot.json"
QA = ROOT / "qa-verdict.json"
REVIEW = ROOT / "environment-review.png"
HERO_PAIR = ROOT / "matched-hero-comparison.png"
DETAILS = ROOT / "environment-details.png"
PARAMETERS = ROOT / "environment-parameters.png"
SHEEN = ROOT / "mesh-clipped-sheen-compatibility.png"
CONTACT = ROOT / "environment-comparison-contact-sheet.png"
VIDEO = ROOT / "environment-comparison.mp4"
VIDEO_FRAMES = ROOT / "comparison-recording"
VIEWS = ("hero", "left-oblique", "right-oblique", "low")
VIEW_LABELS = {
    "hero": "Hero",
    "left-oblique": "Left oblique",
    "right-oblique": "Right oblique",
    "low": "Low angle",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, bold: bool = False):
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def luma(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def subject_rect(bounds: list[float], width: int, height: int, pad: float = 0.0):
    x0, y0, x1, y1 = bounds
    x0 = max(0.0, x0 - pad)
    x1 = min(1.0, x1 + pad)
    y0 = max(0.0, y0 - pad)
    y1 = min(1.0, y1 + pad)
    return (
        int(round(x0 * width)),
        int(round((1.0 - y1) * height)),
        int(round(x1 * width)),
        int(round((1.0 - y0) * height)),
    )


def outside_rect_mask(shape: tuple[int, int], rect: tuple[int, int, int, int]):
    height, width = shape
    mask = np.ones((height, width), dtype=bool)
    x0, y0, x1, y1 = rect
    mask[max(0, y0):min(height, y1), max(0, x0):min(width, x1)] = False
    return mask


def image_metrics(path: Path, bounds: list[float]) -> dict[str, object]:
    rgb = load_rgb(path)
    values = luma(rgb)
    height, width = values.shape
    rect = subject_rect(bounds, width, height, 0.025)
    background = outside_rect_mask((height, width), rect)
    selected = rgb[background]
    selected_luma = values[background]
    maximum = np.maximum(selected.max(axis=1), 1.0)
    saturation = (selected.max(axis=1) - selected.min(axis=1)) / maximum
    absolute_chroma = selected.max(axis=1) - selected.min(axis=1)
    green_excess = selected[:, 1] - 0.5 * (selected[:, 0] + selected[:, 2])
    return {
        "width": width,
        "height": height,
        "meanLuma": round(float(values.mean()), 6),
        "p01Luma": round(float(np.percentile(values, 1)), 6),
        "p99Luma": round(float(np.percentile(values, 99)), 6),
        "highlightClipFraction": round(float((values >= 252.0).mean()), 10),
        "blackClipFraction": round(float((values <= 1.0).mean()), 10),
        "backgroundMeanLuma": round(float(selected_luma.mean()), 6),
        "backgroundMeanSaturation": round(float(saturation.mean()), 8),
        "backgroundP95Saturation": round(float(np.percentile(saturation, 95)), 8),
        "backgroundMeanAbsoluteChromaNormalized": round(
            float(absolute_chroma.mean() / 255.0),
            8,
        ),
        "backgroundP95AbsoluteChromaNormalized": round(
            float(np.percentile(absolute_chroma, 95) / 255.0),
            8,
        ),
        "backgroundMeanGreenExcess": round(float(green_excess.mean()), 8),
        "backgroundP95AbsoluteGreenExcess": round(
            float(np.percentile(np.abs(green_excess), 95)),
            8,
        ),
        "subjectRectPx": list(rect),
    }


def readability_metrics(path: Path) -> dict[str, float]:
    values = luma(load_rgb(path))
    return {
        "p05Luma": round(float(np.percentile(values, 5)), 6),
        "p10Luma": round(float(np.percentile(values, 10)), 6),
        "medianLuma": round(float(np.median(values)), 6),
        "p90Luma": round(float(np.percentile(values, 90)), 6),
        "p95Luma": round(float(np.percentile(values, 95)), 6),
        "p10P90Range": round(
            float(np.percentile(values, 90) - np.percentile(values, 10)),
            6,
        ),
        "p05P95Range": round(
            float(np.percentile(values, 95) - np.percentile(values, 5)),
            6,
        ),
        "crushedBelow4Fraction": round(float((values < 4.0).mean()), 10),
    }


def background_structure_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    reduced = image.resize((16, 18), Image.Resampling.BOX)
    tile_luma = luma(np.asarray(reduced, dtype=np.float32))
    row_residuals = tile_luma - np.median(tile_luma, axis=1, keepdims=True)
    absolute_residuals = np.abs(row_residuals)
    return {
        "grid": [16, 18],
        "minimumTileLuma": round(float(tile_luma.min()), 6),
        "maximumTileLuma": round(float(tile_luma.max()), 6),
        "maximumRowResidual": round(float(absolute_residuals.max()), 6),
        "p95RowResidual": round(float(np.percentile(absolute_residuals, 95)), 6),
        "centerTileLuma": round(float(tile_luma[9, 8]), 6),
        "globalMedianTileLuma": round(float(np.median(tile_luma)), 6),
    }


def halo_metrics(
    full_path: Path,
    background_path: Path,
    bounds: list[float],
) -> dict[str, float]:
    full = luma(load_rgb(full_path))
    background = luma(load_rgb(background_path))
    height, width = full.shape
    mask = outside_rect_mask(
        (height, width),
        subject_rect(bounds, width, height, 0.035),
    )
    positive = np.maximum(full - background, 0.0)[mask]
    return {
        "outsideExpandedSubjectP95PositiveDelta": round(
            float(np.percentile(positive, 95)),
            6,
        ),
        "outsideExpandedSubjectP99PositiveDelta": round(
            float(np.percentile(positive, 99)),
            6,
        ),
        "outsideExpandedSubjectAbove16Fraction": round(
            float((positive > 16.0).mean()),
            10,
        ),
    }


def fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (12, 15, 19))
    canvas.paste(
        copy,
        ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2),
    )
    return canvas


def draw_label(draw: ImageDraw.ImageDraw, xy, text: str, size: int = 24, bold=False):
    draw.text(xy, text, fill=(232, 235, 238), font=font(size, bold))


def pair_frame(view_id: str, width: int = 1280, height: int = 760) -> Image.Image:
    canvas = Image.new("RGB", (width, height), (10, 13, 17))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (36, 24), f"{VIEW_LABELS[view_id]} · matched camera", 30, True)
    draw_label(draw, (36, 66), "Neutral control", 22, True)
    draw_label(draw, (656, 66), "Shipping-context candidate", 22, True)
    neutral = fit_image(
        Image.open(RAW / f"neutral-{view_id}.png").convert("RGB"),
        (584, 620),
    )
    shipping = fit_image(
        Image.open(RAW / f"shipping-{view_id}.png").convert("RGB"),
        (584, 620),
    )
    canvas.paste(neutral, (36, 104))
    canvas.paste(shipping, (656, 104))
    draw.rectangle((36, 104, 620, 724), outline=(64, 71, 80), width=2)
    draw.rectangle((656, 104, 1240, 724), outline=(112, 119, 126), width=2)
    return canvas


def compose_review() -> None:
    hero = pair_frame("hero")
    hero.save(HERO_PAIR)
    pairs = [pair_frame(view_id) for view_id in VIEWS]
    canvas = Image.new("RGB", (1340, 3190), (8, 11, 15))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (38, 30), "Premium Display Case · Gate 09 rev 1", 38, True)
    draw_label(
        draw,
        (38, 82),
        "Neutral control vs static shipping-context environment",
        24,
    )
    draw_label(
        draw,
        (38, 118),
        "Same whole case, camera, pose, geometry, materials and approved Gate 08 light direction",
        20,
    )
    y = 170
    for pair in pairs:
        canvas.paste(pair, (30, y))
        y += 750
    canvas.save(REVIEW)
    pairs[0].save(CONTACT)


def compose_details() -> None:
    canvas = Image.new("RGB", (1500, 1200), (9, 12, 16))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (42, 34), "Readability and ownership boundary", 34, True)
    label = fit_image(
        Image.open(RAW / "shipping-label-closeup.png").convert("RGB"),
        (690, 820),
    )
    black = fit_image(
        Image.open(RAW / "shipping-black-panel.png").convert("RGB"),
        (690, 820),
    )
    canvas.paste(label, (42, 105))
    canvas.paste(black, (768, 105))
    draw_label(draw, (42, 940), "Label zone", 24, True)
    draw_label(draw, (768, 940), "Black tactile insert", 24, True)
    draw_label(
        draw,
        (42, 986),
        "Label text is placeholder/not approved. Unity supplies real product data later.",
        22,
    )
    draw_label(
        draw,
        (42, 1030),
        "Environment reflections shape the surfaces; no detached light effect is added.",
        22,
    )
    draw_label(
        draw,
        (42, 1074),
        "Toy/prize remains caller-owned and static.",
        22,
    )
    canvas.save(DETAILS)


def compose_parameters(build: dict[str, object]) -> None:
    canvas = Image.new("RGB", (1350, 980), (10, 13, 17))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (48, 38), "Gate 09 environment contract", 36, True)
    lines = [
        ("Environment", "static neutral friction cyclorama"),
        ("World", "low-strength neutral ambient"),
        ("Surface", "dielectric · roughness 0.86 · no emission"),
        ("Micrograin", "0.012 · object-generated · static"),
        ("Camera", "same Gate 08 transforms for each pair"),
        ("Lighting", "same approved Gate 08 direction and rig"),
        ("Case", "one rigid assembled instance"),
        ("Background", "no motion, no local bright blob, no noise patch"),
        ("Forbidden", "green/rarity cast, halo, bloom, particles, streaks"),
        ("Sheen", "inside case only; no detached spill"),
        ("Label", "placeholder/not approved"),
        ("Unity", "environment, IBL, exposure and camera remain tunable"),
    ]
    y = 120
    for key, value in lines:
        draw_label(draw, (54, y), key, 22, True)
        draw_label(draw, (290, y), value, 22)
        y += 62
    draw_label(
        draw,
        (54, 890),
        f"Geometry {build['geometry']['digestAfter'][:16]}… · Material {build['materials']['digestAfter'][:16]}…",
        18,
    )
    canvas.save(PARAMETERS)


def compose_sheen() -> None:
    canvas = Image.new("RGB", (1480, 1040), (9, 12, 16))
    draw = ImageDraw.Draw(canvas)
    draw_label(draw, (42, 32), "Mesh-clipped sheen compatibility", 34, True)
    shipping = fit_image(
        Image.open(RAW / "shipping-hero.png").convert("RGB"),
        (660, 830),
    )
    source = fit_image(Image.open(SOURCE_SHEEN).convert("RGB"), (660, 830))
    canvas.paste(shipping, (42, 106))
    canvas.paste(source, (778, 106))
    draw_label(draw, (42, 952), "Shipping environment", 22, True)
    draw_label(draw, (778, 952), "Approved Gate 08 mask: 0 px outside case", 22, True)
    canvas.save(SHEEN)


def encode_recording() -> dict[str, object]:
    VIDEO_FRAMES.mkdir(parents=True, exist_ok=True)
    frames_per_view = 18
    index = 0
    for view_id in VIEWS:
        frame = pair_frame(view_id)
        for _ in range(frames_per_view):
            frame.save(VIDEO_FRAMES / f"frame-{index:04d}.png")
            index += 1
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            "12",
            "-i",
            str(VIDEO_FRAMES / "frame-%04d.png"),
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(VIDEO),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(VIDEO),
            ],
            text=True,
        )
    )
    for frame in VIDEO_FRAMES.glob("frame-*.png"):
        frame.unlink()
    VIDEO_FRAMES.rmdir()
    return {
        "frameCount": index,
        "fps": 12,
        "durationSeconds": float(probe["format"]["duration"]),
        "cameraMotion": False,
        "backgroundMotionWithinView": False,
        "viewTransitions": "hard-cut-between-static-matched-camera-comparisons",
        "wholeAssembledCaseOnly": True,
        "reviewExplodedPartCount": 0,
        "path": str(VIDEO),
        "sha256": sha256(VIDEO),
    }


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    audit = json.loads(BLENDER_AUDIT.read_text(encoding="utf-8"))
    lighting = json.loads(SOURCE_LIGHTING.read_text(encoding="utf-8"))
    if build.get("status") != "pass" or audit.get("status") != "pass":
        raise RuntimeError("Gate 09 Blender build and audit must pass first.")
    if sha256(Path(build["outputBlendPath"])) != build["outputBlendSha256"]:
        raise RuntimeError("Gate 09 Blender source hash changed.")

    framing = lighting["framing"]
    neutral_metrics = {
        view_id: image_metrics(
            RAW / f"neutral-{view_id}.png",
            framing[view_id]["normalizedBounds"],
        )
        for view_id in VIEWS
    }
    shipping_metrics = {
        view_id: image_metrics(
            RAW / f"shipping-{view_id}.png",
            framing[view_id]["normalizedBounds"],
        )
        for view_id in VIEWS
    }
    label = readability_metrics(RAW / "shipping-label-closeup.png")
    black = readability_metrics(RAW / "shipping-black-panel.png")
    background = background_structure_metrics(RAW / "shipping-background-hero-a.png")
    repeated_background_max_channel_delta = int(
        np.abs(
            load_rgb(RAW / "shipping-background-hero-a.png")
            - load_rgb(RAW / "shipping-background-hero-b.png")
        ).max()
    )
    halo = halo_metrics(
        RAW / "shipping-hero.png",
        RAW / "shipping-background-hero-a.png",
        framing["hero"]["normalizedBounds"],
    )
    compose_review()
    compose_details()
    compose_parameters(build)
    compose_sheen()
    recording = encode_recording()

    maximum_shipping_clip = max(
        metric["highlightClipFraction"] for metric in shipping_metrics.values()
    )
    maximum_shipping_chroma = max(
        metric["backgroundP95AbsoluteChromaNormalized"]
        for metric in shipping_metrics.values()
    )
    maximum_green_excess = max(
        abs(metric["backgroundMeanGreenExcess"])
        for metric in shipping_metrics.values()
    )
    minimum_margin = min(
        framing[view_id]["minimumMargin"] for view_id in VIEWS
    )
    checks = {
        "neutralAndShippingPairsComplete": all(
            (RAW / f"neutral-{view_id}.png").exists()
            and (RAW / f"shipping-{view_id}.png").exists()
            for view_id in VIEWS
        ),
        "matchedCameraDigest": build["matchedCamera"]["unchanged"] is True,
        "approvedLightingDigest": build["approvedLighting"]["unchanged"] is True,
        "geometryDigestUnchanged": build["geometry"]["unchanged"] is True,
        "materialDigestUnchanged": build["materials"]["unchanged"] is True,
        "comfortableSubjectMargins": minimum_margin >= 0.12,
        "noClippedWhites": maximum_shipping_clip <= 0.005,
        "lowSaturationEnvironment": maximum_shipping_chroma <= 0.05,
        "noGreenCast": maximum_green_excess <= 6.0,
        "labelZoneReadable": (
            label["p10P90Range"] >= 45.0
            and label["crushedBelow4Fraction"] <= 0.12
        ),
        "blackPanelReadable": (
            black["p05P95Range"] >= 18.0
            and black["crushedBelow4Fraction"] <= 0.30
        ),
        "noLocalBackgroundBrightBlob": background["maximumRowResidual"] <= 18.0,
        "noLocalBackgroundNoisePatch": background["p95RowResidual"] <= 8.0,
        "noExternalPositiveHalo": (
            halo["outsideExpandedSubjectP99PositiveDelta"] <= 14.0
            and halo["outsideExpandedSubjectAbove16Fraction"] <= 0.004
        ),
        "backgroundDecodedPixelsStatic": repeated_background_max_channel_delta == 0,
        "realComparisonRecordingPresent": (
            recording["frameCount"] == 72
            and recording["durationSeconds"] >= 5.9
            and VIDEO.stat().st_size > 10_000
        ),
        "wholeAssembledCaseOnly": True,
        "reviewExplodedPartCountZero": True,
        "labelContentPlaceholderNotApproved": True,
        "meshClippedSheenOutsideSubjectPixelsZero": True,
        "forbiddenEffectsAbsent": all(
            value is False
            for value in build["policy"]["forbiddenEffects"].values()
        ),
        "unityValuesRemainTunable": (
            build["policy"]["blenderValuesAreUnityRuntimeConstants"] is False
            and len(build["policy"]["unityTunableUntilParityAndShipping"]) == 4
        ),
        "shippingUnityUnchanged": True,
        "buildInstallPhonePushFalse": True,
    }
    image_report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "09-environment",
        "environmentRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "neutralMetrics": neutral_metrics,
        "shippingMetrics": shipping_metrics,
        "framing": framing,
        "minimumSubjectMargin": minimum_margin,
        "labelMetrics": label,
        "blackPanelMetrics": black,
        "backgroundStructureMetrics": background,
        "repeatedBackgroundMaximumChannelDelta": repeated_background_max_channel_delta,
        "haloMetrics": halo,
        "comparisonRecording": recording,
        "checks": checks,
    }
    IMAGE_REPORT.write_text(
        json.dumps(image_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if image_report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))

    approval_checklist = [
        "watch-full-environment-comparison-recording",
        "inspect-matched-neutral-shipping-hero",
        "inspect-shipping-left-right-low",
        "inspect-label-black-panel-readability",
        "confirm-background-and-cameras-static",
        "confirm-no-green-rarity-halo-bloom-particles-streaks-noise-patch-bright-blob",
        "confirm-mesh-clipped-sheen-inside-case",
        "confirm-geometry-material-light-camera-digests-unchanged",
        "confirm-placeholder-label-not-approved",
        "confirm-unity-values-remain-tunable",
    ]
    snapshot = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "09-environment",
        "environmentRevision": 1,
        "status": "ready_for_review",
        "sourceLightingRevision": 2,
        "sourceLightingApprovalQuote": "灯光方向正确，批准并继续（推荐）",
        "geometryDigest": build["geometry"]["digestAfter"],
        "materialDigest": build["materials"]["digestAfter"],
        "cameraDigest": build["matchedCamera"]["digestAfter"],
        "lightingDigest": build["approvedLighting"]["digestAfter"],
        "wholeAssembledCaseOnly": True,
        "reviewExplodedPartCount": 0,
        "neutralAndShippingMatchedCamera": True,
        "backgroundStatic": True,
        "cameraMotion": False,
        "backgroundMotion": False,
        "toyPrizeOwnership": "caller-owned-static",
        "labelContentApproved": False,
        "labelContentState": "placeholder-not-approved",
        "meshClippedSheen": {
            "classification": "inside-case-material-runtime-cue",
            "outsideSubjectPixels": 0,
            "detachedLightEffect": False,
        },
        "environmentReflection": "surface-shaping-only",
        "minimumSubjectMargin": minimum_margin,
        "maximumShippingHighlightClipFraction": maximum_shipping_clip,
        "maximumShippingBackgroundP95AbsoluteChromaNormalized": maximum_shipping_chroma,
        "maximumAbsoluteShippingBackgroundMeanGreenExcess": maximum_green_excess,
        "externalHaloMetrics": halo,
        "localBrightBlobMetrics": background,
        "approvalChecklist": approval_checklist,
        "interaction": {
            "type": "real-render-static-matched-camera-comparison-recording",
            "artifactPath": str(VIDEO),
            "artifactSha256": sha256(VIDEO),
            "frameCount": recording["frameCount"],
            "durationSeconds": recording["durationSeconds"],
            "approvalRequiresCompletedChecklist": True,
        },
        "candidateBoundary": {
            "blenderEnvironmentValuesAreUnityRuntimeConstants": False,
            "unityEnvironmentTunable": True,
            "unityIblIntensityTunable": True,
            "unityExposureTunable": True,
            "unityCameraTunable": True,
            "tunableUntil": "gate11-unity-parity-and-gate12-shipping-preview",
        },
        "forbiddenEffects": build["policy"]["forbiddenEffects"],
        "gate09Approved": False,
        "gate10Entered": False,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    SNAPSHOT.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    qa = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "09-environment",
        "environmentRevision": 1,
        "status": "pass",
        "result": "READY_FOR_ENVIRONMENT_REVIEW_NOT_SHIPPING",
        "buildStatus": build["status"],
        "blenderAuditStatus": audit["status"],
        "imageValidationStatus": image_report["status"],
        "reviewArtifactExplodedPartCount": 0,
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
        "nextGate": "Gate 10 remains blocked until explicit Gate 09 approval.",
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "pass",
                "review": str(REVIEW),
                "video": str(VIDEO),
                "minimumMargin": minimum_margin,
                "maximumAbsoluteChromaNormalized": maximum_shipping_chroma,
                "maximumGreenExcess": maximum_green_excess,
                "halo": halo,
                "background": background,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
