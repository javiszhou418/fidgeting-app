#!/usr/bin/env python3
"""Annotate and validate Gate 05 rev 2 material-diagnostic images."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
BUILD_REPORT = ROOT / "material-diagnostic-build-report.json"
BLENDER_AUDIT = ROOT / "material-diagnostic-blender-audit.json"
IMAGE_REPORT = ROOT / "material-diagnostic-image-validation.json"
NOTICE = "DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 APPROVAL"
FOOTER = "GATE 05 REV 2 SUPPLEMENT · GEOMETRY UNCHANGED · GATE 06/07 BLOCKED"
VIEWS = {
    "hero": ("HERO · REAL BLENDER CYCLES PBR", "diagnostic-material-hero.png"),
    "left-oblique": (
        "LEFT OBLIQUE · REAL BLENDER CYCLES PBR",
        "diagnostic-material-left-oblique.png",
    ),
    "right-oblique": (
        "RIGHT OBLIQUE · REAL BLENDER CYCLES PBR",
        "diagnostic-material-right-oblique.png",
    ),
    "low": ("LOW ANGLE · REAL BLENDER CYCLES PBR", "diagnostic-material-low.png"),
    "side": ("SIDE · 59 MM DEPTH", "diagnostic-material-side.png"),
    "label-closeup": (
        "LABEL CLOSEUP · NEUTRAL IDENTITY PLACEHOLDERS",
        "diagnostic-material-label-closeup.png",
    ),
    "concentric-closeup": (
        "CONCENTRIC ROUNDED-CORNER CLOSEUP",
        "diagnostic-material-concentric-closeup.png",
    ),
    "clay-hero-same-camera": (
        "CLAY CONTROL · SAME HERO CAMERA",
        "diagnostic-clay-hero-same-camera.png",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
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


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    maximum_width: int,
    start_size: int,
    minimum_size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for size in range(start_size, minimum_size - 1, -1):
        candidate = font(size, bold=True)
        box = draw.textbbox((0, 0), text, font=candidate)
        if box[2] - box[0] <= maximum_width:
            return candidate
    return font(minimum_size, bold=True)


def annotate(source: Path, target: Path, view_label: str) -> None:
    image = Image.open(source).convert("RGB")
    top = 132
    bottom = 64
    canvas = Image.new("RGB", (image.width, image.height + top + bottom), (14, 17, 21))
    canvas.paste(image, (0, top))
    draw = ImageDraw.Draw(canvas)
    notice_font = fit_font(draw, NOTICE, image.width - 72, 38, 23)
    view_font = fit_font(draw, view_label, image.width - 72, 27, 18)
    footer_font = fit_font(draw, FOOTER, image.width - 72, 24, 16)
    notice_box = draw.textbbox((0, 0), NOTICE, font=notice_font)
    view_box = draw.textbbox((0, 0), view_label, font=view_font)
    footer_box = draw.textbbox((0, 0), FOOTER, font=footer_font)
    draw.text(
        ((image.width - (notice_box[2] - notice_box[0])) / 2, 17),
        NOTICE,
        fill=(244, 247, 250),
        font=notice_font,
    )
    draw.text(
        ((image.width - (view_box[2] - view_box[0])) / 2, 76),
        view_label,
        fill=(170, 204, 215),
        font=view_font,
    )
    draw.rectangle((0, top - 3, image.width, top), fill=(111, 156, 170))
    draw.text(
        (
            (image.width - (footer_box[2] - footer_box[0])) / 2,
            image.height + top + 18,
        ),
        FOOTER,
        fill=(184, 191, 201),
        font=footer_font,
    )
    canvas.save(target, optimize=True)


def same_camera_comparison(clay: Path, pbr: Path, target: Path) -> None:
    clay_image = Image.open(clay).convert("RGB")
    pbr_image = Image.open(pbr).convert("RGB")
    cell = (1420, 1136)
    header = 190
    footer = 72
    canvas = Image.new("RGB", (2960, header + cell[1] + footer), (14, 17, 21))
    draw = ImageDraw.Draw(canvas)
    notice_font = fit_font(draw, NOTICE, 2860, 52, 34)
    label_font = font(34, bold=True)
    footer_font = fit_font(draw, FOOTER, 2860, 28, 20)
    notice_box = draw.textbbox((0, 0), NOTICE, font=notice_font)
    draw.text(
        ((canvas.width - (notice_box[2] - notice_box[0])) / 2, 24),
        NOTICE,
        fill=(244, 247, 250),
        font=notice_font,
    )
    draw.text((90, 115), "CLAY CONTROL", fill=(199, 207, 215), font=label_font)
    draw.text((1600, 115), "FORMAL PBR MATERIALS", fill=(170, 204, 215), font=label_font)
    for image, x in ((clay_image, 40), (pbr_image, 1500)):
        fitted = ImageOps.contain(image, cell, Image.Resampling.LANCZOS)
        canvas.paste(
            fitted,
            (x + (cell[0] - fitted.width) // 2, header + (cell[1] - fitted.height) // 2),
        )
    draw.line((1480, header, 1480, header + cell[1]), fill=(80, 94, 106), width=3)
    footer_box = draw.textbbox((0, 0), FOOTER, font=footer_font)
    draw.text(
        (
            (canvas.width - (footer_box[2] - footer_box[0])) / 2,
            header + cell[1] + 20,
        ),
        FOOTER,
        fill=(184, 191, 201),
        font=footer_font,
    )
    canvas.save(target, optimize=True)


def contact_sheet(entries: list[tuple[str, Path]], target: Path) -> None:
    width = 3300
    header = 210
    footer = 78
    cell_width = 1040
    cell_height = 770
    gap = 35
    height = header + cell_height * 3 + gap * 2 + footer
    canvas = Image.new("RGB", (width, height), (14, 17, 21))
    draw = ImageDraw.Draw(canvas)
    notice_font = fit_font(draw, NOTICE, width - 120, 62, 40)
    subtitle_font = font(30, bold=True)
    label_font = font(24, bold=True)
    footer_font = fit_font(draw, FOOTER, width - 120, 30, 21)
    notice_box = draw.textbbox((0, 0), NOTICE, font=notice_font)
    draw.text(
        ((width - (notice_box[2] - notice_box[0])) / 2, 24),
        NOTICE,
        fill=(244, 247, 250),
        font=notice_font,
    )
    subtitle = "FORMAL MATERIAL SOURCE · 7 PBR VIEWS · 1 CLAY CONTROL · SAME-CAMERA COMPARISON"
    subtitle_box = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    draw.text(
        ((width - (subtitle_box[2] - subtitle_box[0])) / 2, 116),
        subtitle,
        fill=(170, 204, 215),
        font=subtitle_font,
    )
    for index, (label, path) in enumerate(entries):
        row, column = divmod(index, 3)
        x = 20 + column * (cell_width + gap)
        y = header + row * (cell_height + gap)
        draw.rounded_rectangle(
            (x, y, x + cell_width, y + cell_height),
            radius=18,
            fill=(24, 29, 35),
            outline=(54, 65, 76),
            width=2,
        )
        label_box = draw.textbbox((0, 0), label, font=label_font)
        draw.text(
            (x + (cell_width - (label_box[2] - label_box[0])) / 2, y + 18),
            label,
            fill=(211, 218, 225),
            font=label_font,
        )
        image = Image.open(path).convert("RGB")
        fitted = ImageOps.contain(
            image,
            (cell_width - 32, cell_height - 82),
            Image.Resampling.LANCZOS,
        )
        canvas.paste(
            fitted,
            (
                x + (cell_width - fitted.width) // 2,
                y + 66 + (cell_height - 82 - fitted.height) // 2,
            ),
        )
    footer_box = draw.textbbox((0, 0), FOOTER, font=footer_font)
    draw.text(
        (
            (width - (footer_box[2] - footer_box[0])) / 2,
            height - footer + 21,
        ),
        FOOTER,
        fill=(184, 191, 201),
        font=footer_font,
    )
    canvas.save(target, optimize=True)


def image_metrics(path: Path) -> dict[str, object]:
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    return {
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "meanLuma": round(float(luma.mean()), 6),
        "p01Luma": round(float(np.percentile(luma, 1)), 6),
        "p99Luma": round(float(np.percentile(luma, 99)), 6),
        "lowClipFraction": round(float((luma <= 1.0).mean()), 8),
        "highClipFraction": round(float((luma >= 254.0).mean()), 8),
        "meanChannelChroma": round(
            float((rgb.max(axis=2) - rgb.min(axis=2)).mean() / 255.0),
            8,
        ),
    }


def background_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    rgb = np.asarray(image, dtype=np.float32)
    height, width = rgb.shape[:2]
    regions = {
        "topLeft": rgb[0:int(height * 0.24), 0:int(width * 0.18)],
        "topRight": rgb[0:int(height * 0.24), int(width * 0.82):width],
        "midLeft": rgb[int(height * 0.32):int(height * 0.68), 0:int(width * 0.12)],
        "midRight": rgb[int(height * 0.32):int(height * 0.68), int(width * 0.88):width],
    }
    patch_means = {}
    chroma_means = {}
    outlier_fractions = {}
    for name, region in regions.items():
        luma = region[..., 0] * 0.2126 + region[..., 1] * 0.7152 + region[..., 2] * 0.0722
        patch_means[name] = round(float(luma.mean()), 6)
        chroma_means[name] = round(
            float((region.max(axis=2) - region.min(axis=2)).mean() / 255.0),
            8,
        )
        region_image = Image.fromarray(region.astype(np.uint8))
        blurred = np.asarray(
            region_image.filter(ImageFilter.GaussianBlur(radius=5)),
            dtype=np.float32,
        )
        residual = np.abs(region - blurred).max(axis=2)
        outlier_fractions[name] = round(float((residual > 18.0).mean()), 8)
    return {
        "patchMeanLuma": patch_means,
        "patchMeanLumaRange": round(
            max(patch_means.values()) - min(patch_means.values()),
            6,
        ),
        "patchMeanChannelChroma": chroma_means,
        "fineResidualOutlierFractions": outlier_fractions,
        "maximumFineResidualOutlierFraction": max(outlier_fractions.values()),
        "maximumPatchMeanChannelChroma": max(chroma_means.values()),
    }


def label_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    crop = image.crop((
        int(width * 0.07),
        int(height * 0.16),
        int(width * 0.93),
        int(height * 0.67),
    ))
    rgb = np.asarray(crop, dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    edges = np.asarray(crop.convert("L").filter(ImageFilter.FIND_EDGES), dtype=np.float32)
    return {
        "crop": [
            int(width * 0.07),
            int(height * 0.16),
            int(width * 0.93),
            int(height * 0.67),
        ],
        "p10Luma": round(float(np.percentile(luma, 10)), 6),
        "p90Luma": round(float(np.percentile(luma, 90)), 6),
        "p10P90Contrast": round(
            float(np.percentile(luma, 90) - np.percentile(luma, 10)),
            6,
        ),
        "darkPrintFraction": round(float((luma < 70.0).mean()), 8),
        "lightStockFraction": round(float((luma > 120.0).mean()), 8),
        "meanEdgeResponse": round(float(edges.mean()), 6),
        "blackoutFraction": round(float((luma < 5.0).mean()), 8),
    }


def main() -> None:
    build = json.loads(BUILD_REPORT.read_text(encoding="utf-8"))
    audit = json.loads(BLENDER_AUDIT.read_text(encoding="utf-8"))
    annotated: dict[str, Path] = {}
    for view_id, (label, filename) in VIEWS.items():
        source = RAW / f"{view_id}.png"
        target = ROOT / filename
        annotate(source, target, label)
        annotated[view_id] = target

    comparison = ROOT / "diagnostic-clay-vs-pbr-same-camera.png"
    same_camera_comparison(
        RAW / "clay-hero-same-camera.png",
        RAW / "hero.png",
        comparison,
    )
    sheet = ROOT / "diagnostic-material-contact-sheet.png"
    contact_sheet(
        [
            ("HERO", RAW / "hero.png"),
            ("LEFT OBLIQUE", RAW / "left-oblique.png"),
            ("RIGHT OBLIQUE", RAW / "right-oblique.png"),
            ("LOW", RAW / "low.png"),
            ("SIDE", RAW / "side.png"),
            ("LABEL CLOSEUP", RAW / "label-closeup.png"),
            ("CONCENTRIC CORNER", RAW / "concentric-closeup.png"),
            ("CLAY CONTROL", RAW / "clay-hero-same-camera.png"),
            ("SAME CAMERA", comparison),
        ],
        sheet,
    )

    raw_metrics = {
        view_id: image_metrics(RAW / f"{view_id}.png")
        for view_id in VIEWS
    }
    background = background_metrics(RAW / "hero.png")
    label = label_metrics(RAW / "label-closeup.png")
    checks = {
        "buildValidationPassed": build["status"] == "pass",
        "blenderAuditPassed": audit["status"] == "pass",
        "allRawViewsPresent": all(
            (RAW / f"{view_id}.png").exists()
            and (RAW / f"{view_id}.png").stat().st_size > 50_000
            for view_id in VIEWS
        ),
        "allAnnotatedViewsPresent": all(
            path.exists() and path.stat().st_size > 50_000
            for path in annotated.values()
        ),
        "sameCameraComparisonPresent": (
            comparison.exists() and comparison.stat().st_size > 100_000
        ),
        "contactSheetPresent": sheet.exists() and sheet.stat().st_size > 200_000,
        "sameCameraDimensionsMatch": (
            Image.open(RAW / "hero.png").size
            == Image.open(RAW / "clay-hero-same-camera.png").size
        ),
        "noSevereChannelClipping": all(
            values["highClipFraction"] < 0.01
            and values["lowClipFraction"] < 0.25
            for values in raw_metrics.values()
        ),
        "backgroundLowSaturation": (
            background["maximumPatchMeanChannelChroma"] <= 0.12
        ),
        "backgroundNoLocalizedNoiseSpots": (
            background["maximumFineResidualOutlierFraction"] <= 0.01
        ),
        "backgroundContinuousPatchValues": (
            background["patchMeanLumaRange"] <= 18.0
        ),
        "labelContrastVisible": label["p10P90Contrast"] >= 45.0,
        "labelDarkPrintVisible": label["darkPrintFraction"] >= 0.04,
        "labelStockVisible": label["lightStockFraction"] >= 0.30,
        "labelEdgesReadable": label["meanEdgeResponse"] >= 3.0,
        "labelNotBlackedOutByCover": label["blackoutFraction"] <= 0.20,
        "transparentOrderingPreflightPassed": audit["checks"][
            "transparentLayerOrdering"
        ],
        "geometryDigestUnchanged": audit["checks"]["geometryDigestUnchanged"],
        "gate05ReadyForReviewPreserved": audit["checks"]["gate05StatusPreserved"],
        "gate06And07Blocked": audit["checks"]["gate06And07RemainBlocked"],
        "shippingUnityUnchanged": audit["checks"]["shippingUnityUnchanged"],
        "noBuildInstallPhonePush": audit["checks"]["noBuildInstallPhonePush"],
    }
    artifact_paths = {
        **{f"annotated-{name}": path for name, path in annotated.items()},
        "same-camera-comparison": comparison,
        "material-contact-sheet": sheet,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "05-blockout",
        "blockoutRevision": 2,
        "evidenceClass": "supplementary-material-diagnostic",
        "status": "pass" if all(checks.values()) else "fail",
        "notice": NOTICE,
        "approvalEffect": "none-not-gate07-material-approval",
        "rawMetrics": raw_metrics,
        "backgroundMetrics": background,
        "labelReadabilityInitialCheck": {
            **label,
            "scope": (
                "Rendered diagnostic readability only. Shipping phone 17/11 pt "
                "projection remains a later gate."
            ),
        },
        "transparentSortingInitialCheck": {
            "blenderLayerOrdering": audit["transparentOrdering"],
            "labelBlackoutFraction": label["blackoutFraction"],
            "scope": (
                "Cycles diagnostic preflight only. Unity transparency sorting "
                "remains untested and unapproved."
            ),
        },
        "artifacts": {
            name: {
                "path": str(path),
                "sha256": sha256(path),
                "sizeBytes": path.stat().st_size,
                "dimensions": list(Image.open(path).size),
            }
            for name, path in artifact_paths.items()
        },
        "checks": checks,
    }
    IMAGE_REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "contactSheet": str(sheet),
        "sameCameraComparison": str(comparison),
        "backgroundMetrics": background,
        "labelMetrics": label,
        "imageReport": str(IMAGE_REPORT),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
