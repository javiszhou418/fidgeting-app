#!/usr/bin/env python3
"""Assemble Gate 07 evidence boards and audit rendered images."""

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
USER_FRAME = MODEL_ROOT / "evidence/01-intake/rev-001/obsidian-frames/frame-10.jpg"
NORMALIZED_AUTHORITY = HERE.parent / "rev-009/source-normalized-front.png"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def panel(image_path, size, label):
    image = Image.open(image_path).convert("RGB")
    fitted = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(fitted)
    draw.rectangle((0, 0, size[0], 48), fill=(7, 9, 13))
    draw.text((16, 11), label, font=font(23), fill=(238, 240, 244))
    return fitted


def board(filename, title, items, columns):
    panel_w, panel_h = 560, 430
    rows = (len(items) + columns - 1) // columns
    canvas = Image.new("RGB", (columns * panel_w, 78 + rows * panel_h), (7, 9, 13))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 20), title, font=font(34), fill=(246, 247, 249))
    for index, (path, label) in enumerate(items):
        x = (index % columns) * panel_w
        y = 78 + (index // columns) * panel_h
        canvas.paste(panel(path, (panel_w, panel_h), label), (x, y))
    output = HERE / filename
    canvas.save(output, optimize=True)
    return output


def metrics(path):
    pixels = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    red_dominant = (pixels[..., 0] > pixels[..., 1] * 1.35) & (pixels[..., 0] > pixels[..., 2] * 1.16) & (pixels[..., 0] > 28)
    dark = pixels.mean(axis=2) < 24
    clipped = (pixels >= 254).any(axis=2)
    red_values = pixels[..., 0][red_dominant]
    return {
        "sha256": sha256(path),
        "sizePx": [pixels.shape[1], pixels.shape[0]],
        "redDominantFraction": float(red_dominant.mean()),
        "redStandardDeviation": float(red_values.std()) if red_values.size else 0.0,
        "darkFraction": float(dark.mean()),
        "clippedFraction": float(clipped.mean()),
    }


def main():
    material_board = board(
        "neutral-pbr-material-board.png",
        "GATE 07 REV 11 — NEUTRAL PBR MATERIAL BOARD",
        [
            (HERE / "assembled-closed.png", "Assembled closed"),
            (HERE / "assembled-open.png", "Assembled open — lower artwork visible"),
            (HERE / "side-reflection.png", "Dark side + polished silver rim"),
            (HERE / "crystal-angle-12.png", "Angle-dependent crystal — 12°"),
        ],
        2,
    )
    closeup_board = board(
        "material-closeups-board.png",
        "SOURCE-BACKED SURFACE AND INTERNAL MATERIAL CLOSEUPS",
        [
            (HERE / "crystal-microflake-closeup.png", "Granular blood-red crystal + microflake"),
            (HERE / "lower-artwork-open.png", "Distinct lower direct/reconstructed artwork"),
            (HERE / "underside-grooves-material.png", "Four grooves — neutral technical material"),
            (HERE / "internal-material-isolation.png", "Internal inspection — neutral candidate materials"),
        ],
        2,
    )
    source_board = board(
        "source-comparison.png",
        "ORIGINAL USER IMAGE REMAINS THE SOLE APPEARANCE AUTHORITY",
        [
            (USER_FRAME, "Original user frame 10"),
            (NORMALIZED_AUTHORITY, "Prior source-normalized crop"),
            (HERE / "assembled-closed.png", "Rev 11 corrected geometry — closed"),
            (HERE / "lower-artwork-open.png", "Rev 11 corrected geometry — lower artwork"),
        ],
        2,
    )
    render_names = [
        "assembled-closed.png", "assembled-open.png", "side-reflection.png",
        "crystal-angle-00.png", "crystal-angle-12.png", "crystal-angle-36.png",
        "crystal-microflake-closeup.png", "lower-artwork-open.png",
        "underside-grooves-material.png", "internal-material-isolation.png",
    ]
    render_metrics = {name: metrics(HERE / name) for name in render_names}
    upper = np.asarray(Image.open(HERE / "upper-albedo.png").convert("RGB"))
    lower = np.asarray(Image.open(HERE / "lower-albedo.png").convert("RGB"))
    border = np.asarray(Image.open(HERE.parent / "rev-007/artwork-top-perimeter-border-mask.png").convert("L")) > 96
    upper_border_black = float((upper[border].mean(axis=1) < 12).mean())
    lower_border_black = float((lower[border].mean(axis=1) < 12).mean())
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 11,
        "renders": render_metrics,
        "boards": {
            material_board.name: sha256(material_board),
            closeup_board.name: sha256(closeup_board),
            source_board.name: sha256(source_board),
        },
        "sourceColorContrast": {
            "appearanceAuthority": "original user frame 10",
            "closedRedVariation": render_metrics["assembled-closed.png"]["redStandardDeviation"],
            "openRedVariation": render_metrics["assembled-open.png"]["redStandardDeviation"],
            "closedDarkFraction": render_metrics["assembled-closed.png"]["darkFraction"],
        },
        "fullBlackPerimeter": {
            "upperBlackFractionWithinBorderMask": upper_border_black,
            "lowerBlackFractionWithinBorderMask": lower_border_black,
        },
        "maximumClippedFraction": max(item["clippedFraction"] for item in render_metrics.values()),
        "angleViews": ["crystal-angle-00.png", "crystal-angle-12.png", "crystal-angle-36.png"],
    }
    report["checks"] = {
        "sourceBoardWritten": source_board.exists(),
        "neutralPbrBoardWritten": material_board.exists(),
        "closeupsWritten": closeup_board.exists(),
        "bloodRedVariation": report["sourceColorContrast"]["closedRedVariation"] > 15
        and report["sourceColorContrast"]["openRedVariation"] > 15,
        "blackPerimeter": upper_border_black > 0.995 and lower_border_black > 0.995,
        "lowerArtworkVisible": render_metrics["lower-artwork-open.png"]["redDominantFraction"] > 0.015,
        "silverDarkResponse": render_metrics["side-reflection.png"]["darkFraction"] > 0.25
        and render_metrics["side-reflection.png"]["clippedFraction"] < 0.001,
        "angleDependentEvidence": all((HERE / name).exists() for name in report["angleViews"]),
        "noClipping": report["maximumClippedFraction"] < 0.001,
    }
    report["pass"] = all(report["checks"].values())
    (HERE / "image-material-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

