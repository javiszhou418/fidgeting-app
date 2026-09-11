#!/usr/bin/env python3
"""Validate and compose real shipping-scene Gate 12 previews."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "gate12-shipping-report.json"
VALIDATION = ROOT / "gate12-image-validation.json"
BOARD = ROOT / "gate12-shipping-board.png"
MOTION = ROOT / "gate12-motion-board.png"
VIEWS = [
    ("library", "模型库"),
    ("hero", "主视角"),
    ("top", "顶部"),
    ("left-oblique", "左斜视"),
    ("right-oblique", "右斜视"),
    ("low", "低角度"),
    ("phone", "手机构图"),
    ("slide-open", "滑开 21 mm"),
    ("ratchet-60deg", "旋转 60°"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size,
        index=1 if bold else 0,
    )


def metrics(path: Path) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    maximum = image.max(axis=2)
    mask = maximum > 24
    ys, xs = np.nonzero(mask)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    bbox_width = bbox[2] - bbox[0]
    bbox_height = bbox[3] - bbox[1]
    pixels = image[mask].astype(np.float32) / 255.0
    red = (pixels[:, 0] > pixels[:, 1] * 1.28) & (pixels[:, 0] > pixels[:, 2] * 1.18)
    silver = (
        (np.max(pixels, axis=1) - np.min(pixels, axis=1) < 0.12)
        & (pixels.mean(axis=1) > 0.34)
    )
    silver_luma = pixels[silver].mean(axis=1) if silver.any() else np.array([0.0])
    return {
        "resolution": [int(image.shape[1]), int(image.shape[0])],
        "boundingBox": bbox,
        "widthFraction": round(bbox_width / image.shape[1], 6),
        "heightFraction": round(bbox_height / image.shape[0], 6),
        "redArtworkPixels": int(red.sum()),
        "silverPixels": int(silver.sum()),
        "silverMedianLuma": round(float(np.median(silver_luma)), 6),
        "clippedPixelFraction": round(float((image >= 250).all(axis=2).mean()), 8),
    }


def card(image_path: Path, label: str, size: tuple[int, int]) -> Image.Image:
    cell = Image.new("RGB", size, (13, 15, 17))
    image = Image.open(image_path).convert("RGB")
    fitted = ImageOps.contain(image, (size[0] - 36, size[1] - 88), Image.Resampling.LANCZOS)
    cell.paste(fitted, ((size[0] - fitted.width) // 2, 58))
    draw = ImageDraw.Draw(cell)
    draw.text((18, 14), label, fill=(242, 241, 236), font=font(30, True))
    return cell


def make_board() -> None:
    canvas = Image.new("RGB", (2700, 1940), (8, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 42), "真实正式场景 · 候选模型视觉检查", fill=(246, 244, 237), font=font(58, True))
    draw.text(
        (62, 118),
        "当前正式模型仍默认启用；这些图片只在受控预览开关中显示候选模型。",
        fill=(177, 182, 181),
        font=font(32),
    )
    cell_size = (860, 540)
    for index, (view, label) in enumerate(VIEWS):
        item = card(ROOT / f"{view}.png", label, cell_size)
        x = 60 + (index % 3) * 880
        y = 190 + (index // 3) * 560
        canvas.paste(item, (x, y))
    draw.text(
        (62, 1870),
        "等待视觉批准，未替换默认模型，未构建或推送手机。",
        fill=(255, 172, 112),
        font=font(34, True),
    )
    canvas.save(BOARD)


def make_motion_board() -> None:
    canvas = Image.new("RGB", (2400, 1050), (8, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 34), "两个姿态只用于本轮检查", fill=(246, 244, 237), font=font(52, True))
    draw.text(
        (62, 100),
        "滑开与旋转各自独立；静止与重置速度都为零。",
        fill=(177, 182, 181),
        font=font(30),
    )
    for index, (view, label) in enumerate([
        ("slide-open", "滑开 21 mm：下片图案可见"),
        ("ratchet-60deg", "旋转 60°：5 × 12°"),
    ]):
        item = card(ROOT / f"{view}.png", label, (1120, 820))
        canvas.paste(item, (60 + index * 1180, 160))
    canvas.save(MOTION)


def main() -> None:
    report = json.loads(REPORT.read_text())
    view_metrics = {view: metrics(ROOT / f"{view}.png") for view, _ in VIEWS}
    checks = {
        "unityShippingReportPassed": report["pass"],
        "realShippingScene": report["shippingScenePath"] == "Assets/_EDC/Scenes/MeshyEDC.unity",
        "candidateDefaultDisabled": not report["candidateDefaultActive"],
        "currentShippingModelDefaultActive": report["currentShippingModelDefaultActive"],
        "requiredViewsPresent": all((ROOT / f"{view}.png").exists() for view, _ in VIEWS),
        "candidateVisibleInAllViews": all(
            values["widthFraction"] > (0.12 if view == "library" else 0.22)
            for view, values in view_metrics.items()
        ),
        "phonePortrait": view_metrics["phone"]["resolution"] == [1290, 2796],
        "deepRedArtworkVisible": all(
            view_metrics[view]["redArtworkPixels"] > 7000
            for view in ("hero", "top", "left-oblique", "right-oblique", "phone")
        ),
        "lowerArtworkVisibleWhenOpen": (
            view_metrics["slide-open"]["redArtworkPixels"]
            > view_metrics["hero"]["redArtworkPixels"] * 1.05
        ),
        "brightSilverReadable": all(
            view_metrics[view]["silverMedianLuma"] > 0.42
            for view in ("hero", "left-oblique", "right-oblique", "low", "phone")
        ),
        "highlightsNotClipped": max(
            values["clippedPixelFraction"] for values in view_metrics.values()
        ) < 0.01,
        "geometryUnchanged": report["triangles"] == 4096,
        "sharedDetentSetting": report["detentCount"] == 30
        and report["detentStepDegrees"] == 12.0,
        "noSelfMotion": report["zeroInitialAndResetVelocity"],
        "runtimeAndHapticsHonest": not report["runtimeInputIntegrated"]
        and not report["hapticsIntegrated"],
        "artworkIndependent": report["upperLowerArtworkIndependent"],
    }
    validation = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "12-shipping",
        "revision": 1,
        "views": view_metrics,
        "checks": checks,
        "pass": all(checks.values()),
    }
    make_board()
    make_motion_board()
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))
    if not validation["pass"]:
        raise RuntimeError("Gate 12 shipping image checks failed.")


if __name__ == "__main__":
    main()
