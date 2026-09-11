#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
VARIANTS = {
    "rev12": ROOT / "A-rev12-detail",
    "rev13": ROOT / "B-rev13-depth",
    "hybrid": ROOT / "C-rev14-hybrid",
}
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
SMALL = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (10, 13, 17))
    canvas.paste(image, ((size[0] - image.width) // 2,
                         (size[1] - image.height) // 2))
    return canvas


def make_board(path, title, entries, columns):
    cell = (640, 440)
    rows = (len(entries) + columns - 1) // columns
    board = Image.new(
        "RGB", (cell[0] * columns, 72 + rows * 480), (13, 16, 21))
    draw = ImageDraw.Draw(board)
    draw.text((24, 20), title, font=FONT, fill=(238, 241, 246))
    for index, (label, source) in enumerate(entries):
        x = index % columns * cell[0]
        y = 72 + index // columns * 480
        board.paste(fit(source, cell), (x, y))
        draw.text((x + 18, y + 446), label, font=SMALL,
                  fill=(218, 224, 232))
    board.save(path)


def image_and_red_mask(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    red = (
        (rgb[..., 0] > 0.10)
        & (rgb[..., 0] > rgb[..., 1] * 1.35)
        & (rgb[..., 0] > rgb[..., 2] * 1.18)
    )
    return rgb, red


def detail_metrics(path, comparison_mask=None):
    rgb, red = image_and_red_mask(path)
    gray = (
        rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    )
    measurement_mask = red if comparison_mask is None else comparison_mask
    lap = np.zeros_like(gray)
    lap[1:-1, 1:-1] = (
        4.0 * gray[1:-1, 1:-1]
        - gray[:-2, 1:-1]
        - gray[2:, 1:-1]
        - gray[1:-1, :-2]
        - gray[1:-1, 2:]
    )
    detail = np.abs(lap[measurement_mask])
    horizontal = np.abs(gray[:, 1:] - gray[:, :-1])
    vertical = np.abs(gray[1:, :] - gray[:-1, :])
    horizontal = horizontal[
        measurement_mask[:, 1:] & measurement_mask[:, :-1]]
    vertical = vertical[
        measurement_mask[1:, :] & measurement_mask[:-1, :]]
    local = np.concatenate([horizontal, vertical])
    return {
        "redPixelFraction": float(np.mean(red)),
        "comparisonPixelFraction": float(np.mean(measurement_mask)),
        "laplacianMean": float(np.mean(detail)),
        "laplacianP90": float(np.percentile(detail, 90)),
        "localVariance": float(np.var(local)),
        "localDifferenceP90": float(np.percentile(local, 90)),
        "edgeDensity": float(np.mean(detail > 0.025)),
        "clippedFraction": float(np.mean(np.max(rgb, axis=2) >= 0.995)),
    }


def compose_motion():
    output = ROOT / "triptych-motion-frames"
    output.mkdir(exist_ok=True)
    labels = ["rev 12 detail", "rev 13 depth", "rev 14 hybrid"]
    dirs = [
        ROOT / "A-rev12-detail-motion-frames",
        ROOT / "B-rev13-depth-motion-frames",
        ROOT / "C-rev14-hybrid-motion-frames",
    ]
    for frame in range(150):
        canvas = Image.new("RGB", (1920, 400), (9, 12, 16))
        draw = ImageDraw.Draw(canvas)
        for index, (label, directory) in enumerate(zip(labels, dirs)):
            image = fit(directory / f"frame-{frame:04d}.png", (640, 360))
            canvas.paste(image, (index * 640, 0))
            draw.text((index * 640 + 18, 366), label, font=SMALL,
                      fill=(230, 234, 240))
        canvas.save(output / f"frame-{frame:04d}.png")


def main():
    report = json.loads((ROOT / "unity-hybrid-report.json").read_text())
    unity_project = next(
        parent for parent in ROOT.parents if parent.name == "FidgetingApp")
    assets = unity_project / "Assets" / "_EDC" / "Candidates"
    shader_paths = {
        "rev12OnePass":
            assets / "MagneticSlideTileGate11R012" / "Shaders"
            / "MagneticSlideTileLayeredOpticsR012.shader",
        "rev13Substrate":
            assets / "MagneticSlideTileGate11R013" / "Shaders"
            / "MagneticSlideTrueSubstrateR013.shader",
        "rev13Motif":
            assets / "MagneticSlideTileGate11R013" / "Shaders"
            / "MagneticSlideTrueMotifR013.shader",
        "rev13Crystal":
            assets / "MagneticSlideTileGate11R013" / "Shaders"
            / "MagneticSlideTrueCrystalCapR013.shader",
        "rev14Substrate":
            assets / "MagneticSlideTileGate11R014" / "Shaders"
            / "MagneticSlideHybridSubstrateR014.shader",
        "rev14Motif":
            assets / "MagneticSlideTileGate11R014" / "Shaders"
            / "MagneticSlideHybridMotifR014.shader",
        "rev14Crystal":
            assets / "MagneticSlideTileGate11R014" / "Shaders"
            / "MagneticSlideHybridCrystalR014.shader",
    }
    lineage = {
        "schemaVersion": 1,
        "shaderSha256": {
            name: sha256(path) for name, path in shader_paths.items()
        },
        "reusedTextureSha256": {
            "upperAlbedo": report["upperAlbedoSha256"],
            "lowerAlbedo": report["lowerAlbedoSha256"],
            "upperRoughness": report["upperRoughnessSha256"],
            "lowerRoughness": report["lowerRoughnessSha256"],
            "upperNormal": report["upperNormalSha256"],
            "lowerNormal": report["lowerNormalSha256"],
            "upperMotifMask": report["upperMotifMaskSha256"],
            "lowerMotifMask": report["lowerMotifMaskSha256"],
            "perimeterMask": report["perimeterMaskSha256"],
        },
        "rev13Loss": {
            "droppedMaps":
                "No substrate files were removed, but authored albedo RGB "
                "was collapsed to luminance. Motif stopped sampling the "
                "roughness and normal maps.",
            "proceduralChanges":
                "Mica 28->26, microflake 85/0.16->92/0.19 with a narrower "
                "sparkle threshold, roughness 0.022-0.11->0.035-0.13, "
                "normal 0.32->0.36, iridescence 0.12->0.10.",
            "filtering":
                "Texture importer stayed bilinear with mipmaps. Rev13 "
                "crystal additionally sampled scene color at 2.8 px "
                "distortion, which hid high-frequency substrate detail.",
        },
        "rev14Restoration":
            "Same texture asset paths and hashes as rev12; authored RGB "
            "and rev12 tuning restored. Motif masks sample LOD0. Crystal "
            "transmission is 0.985 with 0.35 px refraction.",
    }
    (ROOT / "source-shader-lineage.json").write_text(
        json.dumps(lineage, indent=2) + "\n")
    _, rev12_red = image_and_red_mask(VARIANTS["rev12"] / "macro.png")
    _, hybrid_red = image_and_red_mask(VARIANTS["hybrid"] / "macro.png")
    shared_red = rev12_red & hybrid_red
    metrics = {
        name: detail_metrics(directory / "macro.png", shared_red)
        for name, directory in VARIANTS.items()
    }
    baseline = metrics["rev12"]
    hybrid = metrics["hybrid"]
    phone_metrics = detail_metrics(
        VARIANTS["hybrid"] / "phone.png")
    ratios = {
        key: hybrid[key] / max(baseline[key], 1e-8)
        for key in [
            "laplacianMean",
            "laplacianP90",
            "localVariance",
            "localDifferenceP90",
            "edgeDensity",
        ]
    }
    checks = {
        "laplacianAtLeastRev12": ratios["laplacianMean"] >= 0.95,
        "localVarianceAtLeastRev12": ratios["localVariance"] >= 0.95,
        "edgeDensityAtLeastRev12": ratios["edgeDensity"] >= 0.95,
        "microflakeDetailVisible": hybrid["localDifferenceP90"] >= 0.01,
        "phoneDistanceMicroflakeVisible":
            phone_metrics["localDifferenceP90"] >= 0.006,
        "noWashout": hybrid["clippedFraction"] < 0.005,
        "parallaxAtLeastRev13Target":
            report["measuredParallaxPixelsAt15Degrees"] >= 2.1,
        "boundsUnchanged":
            report["boundsCenterDeltaMeters"] < 1e-6
            and report["boundsSizeDeltaMeters"] < 1e-6,
        "collidersAndRuntimeUnchanged":
            report["collidersUnchanged"]
            and report["protectedRuntimeUnchanged"],
        "sideAndUndersideArtworkZero":
            report["sideArtworkTriangles"] == 0
            and report["undersideArtworkTriangles"] == 0,
        "build44Blocked": not report["build44InstallAuthorized"],
    }
    result = {
        "schemaVersion": 1,
        "source": "same-camera real MeshyEDC.unity macro renders",
        "comparisonMask":
            "pixel-aligned intersection of rev12 and rev14 red regions",
        "tolerance": "hybrid/rev12 >= 0.95 for primary detail metrics",
        "metrics": metrics,
        "hybridPhoneMetrics": phone_metrics,
        "hybridToRev12Ratios": ratios,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (ROOT / "hybrid-detail-metrics.json").write_text(
        json.dumps(result, indent=2) + "\n")

    make_board(
        ROOT / "gate11-r014-three-way-macro.png",
        "Same Unity camera · detail and physical depth",
        [
            ("rev 12 · one-pass detail", VARIANTS["rev12"] / "macro.png"),
            ("rev 13 · physical depth, detail loss", VARIANTS["rev13"] / "macro.png"),
            ("rev 14 · rev12 detail + rev13 depth", VARIANTS["hybrid"] / "macro.png"),
        ],
        3,
    )
    make_board(
        ROOT / "gate11-r014-hybrid-angle-board.png",
        "Hybrid physical layers · Unity views",
        [
            ("Macro", VARIANTS["hybrid"] / "macro.png"),
            ("Grazing 15°", VARIANTS["hybrid"] / "grazing-15.png"),
            ("Grazing 30°", VARIANTS["hybrid"] / "grazing-30.png"),
            ("Grazing 60°", VARIANTS["hybrid"] / "grazing-60.png"),
        ],
        2,
    )
    make_board(
        ROOT / "gate11-r014-hybrid-shipping-board.png",
        "Hybrid shipping composition",
        [
            ("Closed hero", VARIANTS["hybrid"] / "hero-closed.png"),
            ("Maximum open", VARIANTS["hybrid"] / "max-open.png"),
            ("Phone composition", VARIANTS["hybrid"] / "phone.png"),
        ],
        3,
    )
    compose_motion()
    if not result["pass"]:
        raise SystemExit("Hybrid detail metrics failed.")


if __name__ == "__main__":
    main()
