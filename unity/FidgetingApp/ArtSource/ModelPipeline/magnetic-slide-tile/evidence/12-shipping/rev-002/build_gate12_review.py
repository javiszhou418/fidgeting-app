#!/usr/bin/env python3
"""Validate and compose Gate 12 rev 2 shipping-scene evidence."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
VIEWS = [
    ("library", "模型库"),
    ("hero", "正式主视角"),
    ("top", "顶部"),
    ("left-oblique", "左斜视"),
    ("right-oblique", "右斜视"),
    ("low", "低角度"),
    ("phone", "手机构图"),
    ("max-open", "最大滑开"),
    ("endpoint-12deg", "端点 12°"),
    ("endpoint-36deg", "端点 36°"),
    ("endpoint-360deg", "完整 360°"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size,
        index=1 if bold else 0,
    )


def metrics(path: Path) -> dict:
    image = np.asarray(Image.open(path).convert("RGB"))
    pixels = image.astype(np.float32) / 255.0
    red = (
        (pixels[:, :, 0] > pixels[:, :, 1] * 1.24)
        & (pixels[:, :, 0] > pixels[:, :, 2] * 1.12)
        & (pixels[:, :, 0] > 0.10)
    )
    silver = (
        (pixels.max(axis=2) - pixels.min(axis=2) < 0.14)
        & (pixels.mean(axis=2) > 0.34)
    )
    luma = pixels[silver].mean(axis=1) if silver.any() else np.array([0.0])
    return {
        "resolution": [int(image.shape[1]), int(image.shape[0])],
        "redArtworkPixels": int(red.sum()),
        "silverPixels": int(silver.sum()),
        "silverMedianLuma": round(float(np.median(luma)), 6),
        "clippedFraction": round(float((image >= 250).all(axis=2).mean()), 8),
    }


def card(path: Path, label: str, size: tuple[int, int]) -> Image.Image:
    cell = Image.new("RGB", size, (13, 15, 17))
    image = Image.open(path).convert("RGB")
    fitted = ImageOps.contain(
        image, (size[0] - 28, size[1] - 72), Image.Resampling.LANCZOS)
    cell.paste(fitted, ((size[0] - fitted.width) // 2, 54))
    ImageDraw.Draw(cell).text(
        (16, 12), label, fill=(242, 241, 236), font=font(26, True))
    return cell


def make_board() -> None:
    canvas = Image.new("RGB", (2700, 2520), (8, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 38), "Gate 12 rev 2 · 真实正式场景",
        fill=(246, 244, 237), font=font(56, True))
    draw.text(
        (62, 108),
        "候选仅在证据捕获时启用；默认仍显示旧正式模型。",
        fill=(177, 182, 181), font=font(30))
    for index, (view, label) in enumerate(VIEWS):
        item = card(ROOT / f"{view}.png", label, (860, 540))
        canvas.paste(item, (60 + index % 3 * 880, 170 + index // 3 * 560))
    draw.text(
        (62, 2438),
        "视觉批准待确认，未构建、未安装、未推送手机。",
        fill=(255, 172, 112), font=font(34, True))
    canvas.save(ROOT / "gate12-shipping-board.png")


def make_motion_board() -> None:
    canvas = Image.new("RGB", (2400, 1120), (8, 10, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (60, 36), "端点互锁与下片图案",
        fill=(246, 244, 237), font=font(50, True))
    for index, (view, label) in enumerate([
        ("max-open", "sMax：下片图案可见"),
        ("endpoint-36deg", "sMax：3 × 12°"),
    ]):
        canvas.paste(
            card(ROOT / f"{view}.png", label, (1120, 850)),
            (60 + index * 1180, 150))
    draw.text(
        (62, 1040),
        "完整 30 档与非法回推见 Unity PlayMode 录屏。",
        fill=(177, 182, 181), font=font(30))
    canvas.save(ROOT / "gate12-motion-board.png")


def main() -> None:
    report = json.loads((ROOT / "gate12-shipping-report.json").read_text())
    capture = json.loads(
        (ROOT / "unity-playmode-frames/capture-report.json").read_text())
    probe = json.loads((ROOT / "video-probe.json").read_text())
    values = {view: metrics(ROOT / f"{view}.png") for view, _ in VIEWS}
    stream = probe["streams"][0]
    transitions = capture["transitions"]
    checks = {
        "realShippingScene": report["shippingScenePath"]
        == "Assets/_EDC/Scenes/MeshyEDC.unity",
        "sceneHashRecorded": len(report["shippingSceneSha256"]) == 64,
        "candidateDefaultDisabled": not report["candidateDefaultActive"],
        "oldShippingDefaultActive": report["oldShippingModelDefaultActive"],
        "approvedGate11Source": report["sourceGate11GlbSha256"]
        == "e9f90e9e77756b33857726f95a01194996469f16101dbad91fdb7024b679c2ca",
        "geometryUnchanged": report["triangles"] == 99280,
        "sharedSettings": report["detentCount"] == 30
        and report["detentStepDegrees"] == 12.0,
        "runtimeAndHapticsWired": report["runtimeInputIntegrated"]
        and report["hapticsIntegrated"],
        "requiredViewsPresent": all(
            (ROOT / f"{view}.png").exists() for view, _ in VIEWS),
        "phonePortrait": values["phone"]["resolution"] == [1290, 2796],
        "redArtworkVisible": all(
            values[view]["redArtworkPixels"] > 1000
            for view in ("hero", "top", "right-oblique")),
        "lowerArtworkVisibleOpen":
            values["max-open"]["redArtworkPixels"] > 1000,
        "highlightsNotClipped": max(
            item["clippedFraction"] for item in values.values()) < 0.01,
        "unityOnlyVideo": capture["unityOnly"]
        and capture["candidateExplicitlyEnabled"],
        "fullThirtyDetents": "endpoint-detent-29" in transitions
        and transitions.count("angle-aligned-slide-unlocked") >= 1,
        "endpointInterlock": "rotation-locked-until-maximum-travel" in transitions
        and "slide-locked-until-angle-aligns" in transitions,
        "zeroMotion": capture["zeroInitialAndResetVelocity"],
        "noFlip": capture["wholeProductPitchRollDegrees"] == 0,
        "videoEncoding": stream["codec_name"] == "h264"
        and stream["width"] == 640
        and stream["height"] == 360
        and stream["avg_frame_rate"] == "30/1"
        and stream["nb_read_frames"] == "240",
    }
    validation = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "12-shipping",
        "revision": 2,
        "views": values,
        "checks": checks,
        "pass": all(checks.values()),
    }
    make_board()
    make_motion_board()
    (ROOT / "gate12-image-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))
    if not validation["pass"]:
        raise RuntimeError("Gate 12 rev 2 validation failed.")


if __name__ == "__main__":
    main()
