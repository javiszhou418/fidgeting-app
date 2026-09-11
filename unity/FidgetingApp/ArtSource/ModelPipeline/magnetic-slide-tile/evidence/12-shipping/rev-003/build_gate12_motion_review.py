#!/usr/bin/env python3
"""Validate Gate 12 rev 3 connected-product motion evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "rev-002"
ACCEPTED = [
    "library", "hero", "top", "left-oblique",
    "right-oblique", "low", "phone",
]
MOTION = [
    ("max-open", "最大滑开 · sMax / 0°"),
    ("endpoint-12deg", "端点 · 12°"),
    ("endpoint-36deg", "端点 · 36°"),
    ("endpoint-360deg", "端点 · 360°"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        size,
        index=1 if bold else 0,
    )


def image_metrics(path: Path) -> dict:
    pixels = np.asarray(Image.open(path).convert("RGB"))
    foreground = np.any(pixels > 28, axis=2) & np.any(pixels < 238, axis=2)
    red = (
        (pixels[:, :, 0] > pixels[:, :, 1] * 1.20)
        & (pixels[:, :, 0] > pixels[:, :, 2] * 1.08)
        & (pixels[:, :, 0] > 24)
    )
    return {
        "resolution": [int(pixels.shape[1]), int(pixels.shape[0])],
        "foregroundPixels": int(foreground.sum()),
        "redArtworkPixels": int(red.sum()),
        "clippedFraction": round(
            float(np.all(pixels >= 250, axis=2).mean()), 8),
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


def make_boards() -> None:
    motion = Image.new("RGB", (2400, 1280), (8, 10, 13))
    draw = ImageDraw.Draw(motion)
    draw.text(
        (60, 36), "Gate 12 rev 3 · 连体平面运动修正",
        fill=(246, 244, 237), font=font(50, True))
    draw.text(
        (62, 102),
        "顶片高度恒定；只沿平面滑动，并绕固定轴作 30 × 12° 旋转。",
        fill=(177, 182, 181), font=font(28))
    for index, (name, label) in enumerate(MOTION):
        motion.paste(
            card(ROOT / f"{name}.png", label, (1120, 500)),
            (60 + index % 2 * 1180, 170 + index // 2 * 520))
    draw.text(
        (62, 1222), "视觉批准待确认，未构建、未安装、未推送手机。",
        fill=(255, 172, 112), font=font(30, True))
    motion.save(ROOT / "gate12-motion-board-r003.png")

    shipping = Image.new("RGB", (2700, 2520), (8, 10, 13))
    draw = ImageDraw.Draw(shipping)
    draw.text(
        (60, 38), "Gate 12 rev 3 · 真实正式场景",
        fill=(246, 244, 237), font=font(56, True))
    views = [(name, name) for name in ACCEPTED] + MOTION
    for index, (name, label) in enumerate(views):
        shipping.paste(
            card(ROOT / f"{name}.png", label, (860, 540)),
            (60 + index % 3 * 880, 150 + index // 3 * 560))
    draw.text(
        (62, 2438), "七个已接受视图逐字节保留；本轮只替换运动证据。",
        fill=(177, 182, 181), font=font(30))
    shipping.save(ROOT / "gate12-shipping-board-r003.png")


def main() -> None:
    feedback = json.loads((ROOT / "user-feedback.json").read_text())
    report = json.loads((ROOT / "gate12-motion-fix-report.json").read_text())
    capture = json.loads(
        (ROOT / "unity-playmode-frames/capture-report.json").read_text())
    probe = json.loads((ROOT / "video-probe.json").read_text())
    metrics = {
        name: image_metrics(ROOT / f"{name}.png")
        for name, _ in MOTION
    }
    accepted_hashes = {
        name: {
            "rev2": sha256(PRIOR / f"{name}.png"),
            "rev3": sha256(ROOT / f"{name}.png"),
        }
        for name in ACCEPTED
    }
    checks = {
        "feedbackArchived":
            feedback["screenshotSha256"]
            == "d36fb987ee46313fe401337a61552d6e80c3310f9ccdb9852938edee4191015b",
        "acceptedViewsByteIdentical": all(
            value["rev2"] == value["rev3"]
            for value in accepted_hashes.values()),
        "motionImagesVisible": all(
            value["foregroundPixels"] > 100000
            and value["redArtworkPixels"] > 1000
            and value["clippedFraction"] < 0.01
            for value in metrics.values()),
        "correctedAxes":
            report["correctedSlideAxis"] == "TopLocalSlide local -Y"
            and report["correctedRotationAxis"]
            == "MovingTop/RotatingCarrier local +Z",
        "topStackConstant":
            capture["maximumTopStackResidualMeters"] <= 5e-9,
        "noOutOfPlaneSlide":
            capture["maximumOutOfPlaneSlideResidualMeters"] <= 1e-9,
        "fixedAxisInvariant":
            capture["maximumFixedAxisConstraintResidual"] <= 1e-9,
        "renderersAttached": capture["renderersAttachedEveryFrame"],
        "detentsAtMaximumTravel": capture["detentsStayedAtMaximumTravel"],
        "allThirtyDetents": capture["observedDetentMask"] == 1073741823,
        "endpointInterlock":
            "rotation-locked-until-maximum-travel" in capture["transitions"]
            and "slide-locked-until-angle-aligns" in capture["transitions"]
            and "angle-aligned-slide-unlocked" in capture["transitions"],
        "noPitchRollFlip":
            capture["wholeProductPitchRollDegrees"] == 0,
        "unityOnlyVideo":
            capture["unityOnly"]
            and probe["streams"][0]["codec_name"] == "h264"
            and probe["streams"][0]["nb_read_frames"] == "240",
        "noBuildInstallPhone":
            not report["buildInstallPhone"],
    }
    validation = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "12-shipping",
        "evidenceRevision": 3,
        "acceptedViewHashes": accepted_hashes,
        "motionImageMetrics": metrics,
        "transformMetrics": {
            "maximumTopStackResidualMeters":
                capture["maximumTopStackResidualMeters"],
            "maximumOutOfPlaneSlideResidualMeters":
                capture["maximumOutOfPlaneSlideResidualMeters"],
            "maximumFixedAxisConstraintResidual":
                capture["maximumFixedAxisConstraintResidual"],
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    make_boards()
    (ROOT / "gate12-motion-validation.json").write_text(
        json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))
    if not validation["pass"]:
        raise RuntimeError("Gate 12 rev 3 motion validation failed.")


if __name__ == "__main__":
    main()
