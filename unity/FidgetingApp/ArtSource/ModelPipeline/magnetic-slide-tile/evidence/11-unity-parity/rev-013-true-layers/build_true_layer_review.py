#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
A = ROOT / "A-one-pass-r012"
B = ROOT / "B-true-layers-r013"
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
SMALL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)


def load(path, size=(720, 540)):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (12, 15, 19))
    canvas.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return canvas


def board(path, title, items, columns=2):
    width = 720 * columns
    rows = (len(items) + columns - 1) // columns
    image = Image.new("RGB", (width, 76 + rows * 586), (14, 17, 22))
    draw = ImageDraw.Draw(image)
    draw.text((28, 22), title, font=FONT, fill=(238, 241, 246))
    for index, (label, source) in enumerate(items):
        x = (index % columns) * 720
        y = 76 + (index // columns) * 586
        image.paste(load(source), (x, y))
        draw.text((x + 22, y + 548), label, font=SMALL, fill=(222, 226, 232))
    image.save(path)


def image_metrics(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    luminance = (
        rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    )
    object_mask = luminance > 0.03
    red_mask = (
        object_mask
        & (rgb[..., 0] > rgb[..., 1] * 1.35)
        & (rgb[..., 0] > rgb[..., 2] * 1.18)
    )
    red = rgb[red_mask]
    maximum = np.max(red, axis=1)
    minimum = np.min(red, axis=1)
    saturation = (maximum - minimum) / np.maximum(maximum, 1e-6)
    horizontal = np.abs(luminance[:, 1:] - luminance[:, :-1])
    vertical = np.abs(luminance[1:, :] - luminance[:-1, :])
    horizontal = horizontal[red_mask[:, 1:] & red_mask[:, :-1]]
    vertical = vertical[red_mask[1:, :] & red_mask[:-1, :]]
    local = np.concatenate([horizontal, vertical])
    return {
        "objectPixelFraction": float(np.mean(object_mask)),
        "redPixelFraction": float(np.mean(red_mask)),
        "redMedianSaturation": float(np.median(saturation)),
        "localVariationP90": float(np.percentile(local, 90)),
        "clippedFraction": float(np.mean(np.max(rgb, axis=2) >= 0.995)),
    }


def technical_board(report):
    image = Image.new("RGB", (1440, 760), (13, 16, 21))
    draw = ImageDraw.Draw(image)
    draw.text((28, 22), "Gate 11 rev 13 · Actual Unity optical stack", font=FONT,
              fill=(238, 241, 246))
    macro = load(B / "side-macro.png", (850, 640))
    image.paste(macro, (20, 86))
    x0, x1 = 940, 1340
    y_cap, y_motif, y_substrate = 188, 356, 524
    draw.rectangle((x0, y_cap, x1, y_cap + 44), fill=(160, 205, 225))
    draw.rectangle((x0, y_motif, x1, y_motif + 22), fill=(18, 20, 24))
    draw.rectangle((x0, y_substrate, x1, y_substrate + 76), fill=(118, 16, 30))
    draw.text((x0, y_cap - 38), "Transparent crystal cap", font=SMALL,
              fill=(220, 235, 242))
    draw.text((x0, y_motif - 38), "Etched black motif", font=SMALL,
              fill=(220, 225, 232))
    draw.text((x0, y_substrate - 38), "Blood-red substrate", font=SMALL,
              fill=(238, 215, 220))
    draw.line((910, y_cap, 910, y_substrate + 76), fill=(238, 241, 246), width=2)
    values = [
        f"cap surface: existing outer boundary",
        f"cap thickness: {report['crystalCapThicknessMeters'] * 1000:.2f} mm",
        f"cap → motif: {report['capToMotifSeparationMeters'] * 1000:.2f} mm",
        f"motif → substrate: {report['motifToSubstrateSeparationMeters'] * 1000:.2f} mm",
        f"15° macro parallax: {report['measuredScreenParallaxPixelsAt15Degrees']:.2f} px",
        "visual estimates; not production measurements",
    ]
    for index, value in enumerate(values):
        draw.text((900, 624 + index * 22), value, font=SMALL,
                  fill=(205, 211, 220))
    image.save(ROOT / "gate11-r013-true-layer-technical-board.png")


def main():
    report = json.loads((ROOT / "unity-true-layer-report.json").read_text())
    board(
        ROOT / "gate11-r013-r012-true-layer-comparison.png",
        "Same shipping camera · one-pass rev 12 vs true-layer rev 13",
        [
            ("Rev 12 · one opaque surface", A / "hero-closed.png"),
            ("Rev 13 · physical substrate / motif / crystal", B / "hero-closed.png"),
            ("Rev 12 · grazing 15°", A / "grazing-15.png"),
            ("Rev 13 · grazing 15°", B / "grazing-15.png"),
        ],
    )
    board(
        ROOT / "gate11-r013-depth-angle-board.png",
        "True-layer Unity depth views",
        [
            ("Front", B / "front.png"),
            ("Grazing 15°", B / "grazing-15.png"),
            ("Grazing 30°", B / "grazing-30.png"),
            ("Grazing 60°", B / "grazing-60.png"),
        ],
    )
    board(
        ROOT / "gate11-r013-shipping-poses-board.png",
        "True-layer shipping poses",
        [
            ("Closed hero", B / "hero-closed.png"),
            ("Maximum open · upper and lower", B / "hero-max-open.png"),
            ("Lower artwork", B / "lower-artwork-max-open.png"),
            ("Phone composition", B / "phone-closed.png"),
        ],
    )
    technical_board(report)
    metrics = {
        "schemaVersion": 1,
        "source": "real MeshyEDC.unity camera renders",
        "onePassR012": image_metrics(A / "hero-closed.png"),
        "trueLayersR013": image_metrics(B / "hero-closed.png"),
        "grazing15": image_metrics(B / "grazing-15.png"),
        "checks": {},
    }
    revised = metrics["trueLayersR013"]
    metrics["checks"] = {
        "nonBlankShippingRender": revised["objectPixelFraction"] > 0.10,
        "deepRedVisible": revised["redPixelFraction"] > 0.025,
        "redSaturationPresent": revised["redMedianSaturation"] > 0.40,
        "localVariationPresent": metrics["grazing15"]["localVariationP90"] > 0.002,
        "noWhiteWashout": revised["clippedFraction"] < 0.005,
        "measurableParallax": (
            report["measuredScreenParallaxPixelsAt15Degrees"] >= 1.0
        ),
        "boundsUnchanged": report["boundsWithinExistingExterior"],
        "collidersUnchanged": report["colliderIdentitiesUnchanged"],
        "endpointInterlockLegal": report["endpointInterlockLegal"],
        "build44Blocked": not report["build44InstallAuthorized"],
    }
    metrics["pass"] = all(metrics["checks"].values())
    (ROOT / "true-layer-image-metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n"
    )
    if not metrics["pass"]:
        raise SystemExit("True-layer image checks failed.")


if __name__ == "__main__":
    main()
