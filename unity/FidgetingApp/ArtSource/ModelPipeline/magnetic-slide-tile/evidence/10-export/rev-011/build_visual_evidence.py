#!/usr/bin/env python3
"""Build display-space comparison boards and objective image metrics."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
CONTROLLED = HERE / "controlled-neutral"
REJECTION = HERE / "user-rejection-washed-out-r010.jpg"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"), dtype=np.float32) / 255.0


def metrics(path: Path, use_alpha: bool = True) -> dict:
    image = load_rgba(path)
    rgb = image[..., :3]
    luminance = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    mask = image[..., 3] > 0.25 if use_alpha else luminance > 0.04
    pixels = rgb[mask]
    values = luminance[mask]
    red = (pixels[:, 0] > pixels[:, 1] * 1.35) & (pixels[:, 0] > pixels[:, 2] * 1.2)
    return {
        "dimensions": [image.shape[1], image.shape[0]],
        "sampledPixels": int(mask.sum()),
        "luminanceP05P50P95": [float(np.percentile(values, p)) for p in [5, 50, 95]],
        "redFraction": float(red.mean()),
        "darkFraction": float((values < 0.12).mean()),
        "controlledSilverFraction": float(((values > 0.58) & (values < 0.95)).mean()),
        "clippedWhiteFraction": float((values > 0.95).mean()),
    }


def image_similarity(left: Path, right: Path) -> dict:
    a = load_rgba(left)
    b = load_rgba(right)
    mask = (a[..., 3] > 0.25) & (b[..., 3] > 0.25)
    delta = np.abs(a[..., :3][mask] - b[..., :3][mask])
    return {
        "intersectionPixels": int(mask.sum()),
        "meanAbsoluteError": float(delta.mean()),
        "p95AbsoluteError": float(np.percentile(delta, 95)),
    }


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (6, 8, 11))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def comparison_board(output: Path) -> None:
    size = (900, 558)
    sources = [
        CONTROLLED / "approved-blender-hero-r011.png",
        CONTROLLED / "glb-reimport-hero-r011.png",
        HERE / "gate10-r011-threejs-neutral-hero.png",
        REJECTION,
    ]
    titles = ["AUTHORITATIVE BLENDER", "CORRECTED GLB REIMPORT", "THREE.JS REAL GLB", "REJECTED REV 10"]
    notes = ["Controlled neutral", "Same camera + environment", "Matched hero camera + neutral HDR", "Uncalibrated near-field evidence"]
    board = Image.new("RGB", (3600, 654), (6, 8, 11))
    draw = ImageDraw.Draw(board)
    title_font = ImageFont.load_default(size=21)
    note_font = ImageFont.load_default(size=16)
    for index, source in enumerate(sources):
        x = index * size[0]
        board.paste(fit(source, size), (x, 96))
        draw.text((x + 20, 17), titles[index], font=title_font, fill=(238, 241, 245))
        draw.text((x + 20, 53), notes[index], font=note_font, fill=(153, 165, 178))
    board.save(output, optimize=False)


def closeup_board(output: Path) -> None:
    cell = (720, 446)
    board = Image.new("RGB", (1440, 1434), (6, 8, 11))
    draw = ImageDraw.Draw(board)
    title_font = ImageFont.load_default(size=19)
    labels = ["TOP / DEEP RED + BLACK", "SIDE / ZERO ARTWORK", "RIM / CONTROLLED SILVER"]
    views = ["top-closeup", "side-closeup", "rim-closeup"]
    for row, (label, view) in enumerate(zip(labels, views)):
        y = row * 478
        draw.text((18, y + 12), f"BLENDER {label}", font=title_font, fill=(225, 231, 238))
        draw.text((738, y + 12), f"GLB {label}", font=title_font, fill=(225, 231, 238))
        board.paste(fit(CONTROLLED / f"approved-blender-{view}-r011.png", cell), (0, y + 32))
        board.paste(fit(CONTROLLED / f"glb-reimport-{view}-r011.png", cell), (720, y + 32))
    board.save(output, optimize=False)


def main() -> None:
    comparison = HERE / "gate10-r011-controlled-comparison.png"
    closeups = HERE / "gate10-r011-material-closeups.png"
    comparison_board(comparison)
    closeup_board(closeups)
    source = metrics(CONTROLLED / "approved-blender-hero-r011.png")
    reimport = metrics(CONTROLLED / "glb-reimport-hero-r011.png")
    rejected = metrics(REJECTION, use_alpha=False)
    similarity = image_similarity(
        CONTROLLED / "approved-blender-hero-r011.png",
        CONTROLLED / "glb-reimport-hero-r011.png",
    )
    top = metrics(CONTROLLED / "glb-reimport-top-closeup-r011.png")
    side = metrics(CONTROLLED / "glb-reimport-side-closeup-r011.png")
    rim = metrics(CONTROLLED / "glb-reimport-rim-closeup-r011.png")
    checks = {
        "sameCameraSimilarity": similarity["meanAbsoluteError"] <= 0.04,
        "deepRedTop": top["redFraction"] >= 0.18 and top["luminanceP05P50P95"][1] <= 0.14,
        "darkSide": side["luminanceP05P50P95"][1] <= 0.12,
        "controlledSilver": 0.002 <= rim["controlledSilverFraction"] <= 0.30,
        "noWhiteAreaExcess": reimport["clippedWhiteFraction"] <= 0.04,
        "rejectionWashedOut": rejected["clippedWhiteFraction"] >= reimport["clippedWhiteFraction"] * 8,
        "reimportDarkerThanRejected": reimport["luminanceP05P50P95"][1] < rejected["luminanceP05P50P95"][1] * 0.45,
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "pass": all(checks.values()),
        "displaySpace": "sRGB PNG",
        "source": source,
        "reimport": reimport,
        "rejected": rejected,
        "topCloseup": top,
        "sideCloseup": side,
        "rimCloseup": rim,
        "sameCameraSimilarity": similarity,
        "checks": checks,
        "artifacts": {
            "comparison": {"path": str(comparison), "sha256": sha256(comparison)},
            "closeups": {"path": str(closeups), "sha256": sha256(closeups)},
        },
    }
    (HERE / "visual-metrics-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
