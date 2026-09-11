#!/usr/bin/env python3
"""Assemble Gate 08 boards and audit lighting/pass images."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def font(size):
    paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in paths:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def board(filename, title, panels, columns, cell=(520, 410)):
    rows = (len(panels) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * cell[0], 72 + rows * cell[1]), (12, 14, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 18), title, fill=(242, 242, 240), font=font(26))
    for index, (source, label) in enumerate(panels):
        image = Image.open(HERE / source).convert("RGB")
        image.thumbnail((cell[0] - 24, cell[1] - 60), Image.Resampling.LANCZOS)
        x = (index % columns) * cell[0] + (cell[0] - image.width) // 2
        y = 72 + (index // columns) * cell[1] + 38
        canvas.paste(image, (x, y))
        draw.text(
            ((index % columns) * cell[0] + 16, 72 + (index // columns) * cell[1] + 8),
            label,
            fill=(226, 226, 222),
            font=font(20),
        )
    canvas.save(HERE / filename, optimize=True)


def image_metrics(filename):
    rgb = np.asarray(Image.open(HERE / filename).convert("RGB"), dtype=np.float32)
    maxc = rgb.max(axis=2)
    minc = rgb.min(axis=2)
    red = (rgb[:, :, 0] > 45) & (rgb[:, :, 0] > rgb[:, :, 1] * 1.35) & (rgb[:, :, 0] > rgb[:, :, 2] * 1.22)
    red_pixels = rgb[red]
    if red_pixels.size:
        normalized = red_pixels / 255.0
        mx = normalized.max(axis=1)
        mn = normalized.min(axis=1)
        delta = np.maximum(mx - mn, 1e-6)
        hue = np.where(
            mx == normalized[:, 0],
            ((normalized[:, 1] - normalized[:, 2]) / delta) % 6,
            np.where(
                mx == normalized[:, 1],
                (normalized[:, 2] - normalized[:, 0]) / delta + 2,
                (normalized[:, 0] - normalized[:, 1]) / delta + 4,
            ),
        ) * 60
        hue = np.where(hue > 180, hue - 360, hue)
        red_hue = float(np.median(hue))
        red_variation = float(red_pixels[:, 0].std())
        pink = float(np.mean(hue < -15))
    else:
        red_hue = 999.0
        red_variation = 0.0
        pink = 1.0
    neutral = (maxc - minc < 16) & (maxc > 65) & (maxc < 248)
    neutral_pixels = rgb[neutral]
    blue_gray = float(np.mean((neutral_pixels[:, 2] - neutral_pixels[:, 0]) > 12)) if neutral_pixels.size else 1.0
    neutral_chroma = float(np.median(neutral_pixels.max(axis=1) - neutral_pixels.min(axis=1))) if neutral_pixels.size else 255
    luminance = rgb.mean(axis=2)
    gx = np.abs(np.diff(luminance, axis=1))
    gy = np.abs(np.diff(luminance, axis=0))
    edge_fraction = float((gx > 22).mean() * 0.5 + (gy > 22).mean() * 0.5)
    if red.any():
        ys, xs = np.where(red)
        pad = 8
        crop = luminance[
            max(0, int(ys.min()) - pad):min(luminance.shape[0], int(ys.max()) + pad + 1),
            max(0, int(xs.min()) - pad):min(luminance.shape[1], int(xs.max()) + pad + 1),
        ]
        crop_gx = np.abs(np.diff(crop, axis=1))
        crop_gy = np.abs(np.diff(crop, axis=0))
        motif_edge_fraction = float((crop_gx > 16).mean() * 0.5 + (crop_gy > 16).mean() * 0.5)
    else:
        motif_edge_fraction = 0.0
    return {
        "sizePx": [int(rgb.shape[1]), int(rgb.shape[0])],
        "sha256": sha256(HERE / filename),
        "pixelSha256": hashlib.sha256(rgb.astype(np.uint8).tobytes()).hexdigest(),
        "clippedFraction": float(np.mean((rgb[:, :, 0] >= 254) & (rgb[:, :, 1] >= 254) & (rgb[:, :, 2] >= 254))),
        "redFraction": float(red.mean()),
        "redHueDegrees": red_hue,
        "redVariation": red_variation,
        "pinkFractionWithinRed": pink,
        "neutralFraction": float(neutral.mean()),
        "neutralChroma": neutral_chroma,
        "blueGrayFractionWithinNeutral": blue_gray,
        "edgeFraction": edge_fraction,
        "motifLocalEdgeFraction": motif_edge_fraction,
        "dynamicRange": float(np.percentile(luminance, 99) - np.percentile(luminance, 1)),
        "channelStd": [float(value) for value in rgb.reshape(-1, 3).std(axis=0)],
    }


def pass_metrics(filename):
    rgb = np.asarray(Image.open(HERE / filename).convert("RGB"), dtype=np.uint8)
    saturation = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2).astype(np.int16)
    luminance = rgb.mean(axis=2)
    return {
        "sha256": sha256(HERE / filename),
        "pixelSha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
        "sizePx": [int(rgb.shape[1]), int(rgb.shape[0])],
        "saturationMedian": float(np.median(saturation)),
        "dynamicRange": float(np.percentile(luminance, 99) - np.percentile(luminance, 1)),
        "channelStd": [float(value) for value in rgb.reshape(-1, 3).std(axis=0)],
        "uniqueGrayLevels": int(len(np.unique(rgb[:, :, 0]))),
    }


def main():
    views = ["hero.png", "left-oblique.png", "right-oblique.png", "low-angle.png"]
    modes = ["lighting-neutral.png", "lighting-studio.png", "lighting-daylight.png"]
    mechanical = ["flat-plane-raised-axis-lit.png", "underside-grooves-lit.png", "carrier-clearance-lit.png"]
    passes = ["pass-beauty.png", "pass-clay.png", "pass-normal.png", "pass-depth.png", "pass-roughness.png"]
    board(
        "lighting-view-board.png",
        "Gate 08 rev 2 · Authored lighting views",
        list(zip(views, ["Hero", "Left oblique", "Right oblique", "Low angle"])),
        2,
    )
    board(
        "lighting-mode-comparison.png",
        "Same camera · Neutral / Studio / Daylight",
        list(zip(modes, ["Neutral 6504 K", "Studio 5600 K key", "Daylight 6504 K"])),
        3,
        (500, 420),
    )
    board(
        "lighting-pass-board.png",
        "Same camera and pose · Beauty / Clay / Normal / Depth / Roughness",
        list(zip(passes, ["Beauty", "Clay", "World normal", "View depth", "Roughness"])),
        5,
        (390, 350),
    )
    board(
        "mechanical-lighting-board.png",
        "Lighting reveals hidden mechanical geometry",
        list(zip(mechanical, ["Flat plane + raised axis", "Four underside grooves", "Carrier + follower clearance"])),
        3,
        (500, 420),
    )
    view_reports = {name: image_metrics(name) for name in views + modes}
    mechanical_reports = {name: image_metrics(name) for name in mechanical}
    pass_reports = {name: pass_metrics(name) for name in passes}
    required_size = [1400, 1100]
    max_clip = max(report["clippedFraction"] for report in view_reports.values())
    checks = {
        "requiredViewSize": all(report["sizePx"] == required_size for report in view_reports.values()),
        "allViewHashesDistinct": len({report["sha256"] for report in view_reports.values()}) == len(view_reports),
        "beautyMatchesHero": pass_reports["pass-beauty.png"]["pixelSha256"] == view_reports["hero.png"]["pixelSha256"],
        "allPassesSameSize": all(report["sizePx"] == required_size for report in pass_reports.values()),
        "passesDistinct": len({report["sha256"] for report in pass_reports.values()}) == 5,
        "clippingControlled": max_clip < 0.001,
        "bloodRedHue": all(-20 <= report["redHueDegrees"] <= 20 for report in view_reports.values()),
        "noPinkDrift": all(report["pinkFractionWithinRed"] < 0.08 for report in view_reports.values()),
        "crystalVariation": all(report["redVariation"] > 10 for report in view_reports.values()),
        "neutralSilver": all(report["neutralChroma"] <= 12 for report in view_reports.values()),
        "noBlueGraySilver": all(report["blueGrayFractionWithinNeutral"] < 0.08 for report in view_reports.values()),
        "motifContrast": all(report["motifLocalEdgeFraction"] > 0.0035 for report in view_reports.values()),
        "mechanicalReadable": all(
            report["edgeFraction"] > 0.0015 and report["dynamicRange"] > 60
            for report in mechanical_reports.values()
        ),
        "clayValid": pass_reports["pass-clay.png"]["saturationMedian"] < 16
        and pass_reports["pass-clay.png"]["dynamicRange"] > 70,
        "normalValid": min(pass_reports["pass-normal.png"]["channelStd"]) > 8
        and max(pass_reports["pass-normal.png"]["channelStd"]) > 18,
        "depthValid": pass_reports["pass-depth.png"]["dynamicRange"] > 70,
        "roughnessValid": pass_reports["pass-roughness.png"]["uniqueGrayLevels"] >= 5
        and pass_reports["pass-roughness.png"]["dynamicRange"] > 20,
        "boardsWritten": all(
            (HERE / name).exists()
            for name in (
                "lighting-view-board.png", "lighting-mode-comparison.png",
                "lighting-pass-board.png", "mechanical-lighting-board.png",
            )
        ),
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 2,
        "views": view_reports,
        "mechanical": mechanical_reports,
        "passes": pass_reports,
        "maximumBeautyClippedFraction": max_clip,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (HERE / "image-lighting-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 08 image audit failed.")


if __name__ == "__main__":
    main()

