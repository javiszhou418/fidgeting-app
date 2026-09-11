#!/usr/bin/env python3
"""Verify pixels from real R027 Simulator captures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops


def load_rgba(path: Path) -> Image.Image:
    if not path.is_file():
        raise ValueError(f"missing capture: {path}")
    return Image.open(path).convert("RGBA")


def transparent_mouth_mask(overlay: Image.Image) -> Image.Image:
    alpha = overlay.transpose(Image.Transpose.FLIP_TOP_BOTTOM).getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("native Pack overlay has no opaque pixels")
    left, top, right, bottom = bounds
    width = right - left
    height = bottom - top
    region = Image.new("L", alpha.size)
    region.paste(
        255,
        (
            int(left + width * 0.12),
            int(top + height * 0.18),
            int(left + width * 0.88),
            int(top + height * 0.36),
        ),
    )
    transparent = alpha.point(lambda value: 255 if value <= 8 else 0)
    return ImageChops.multiply(region, transparent)


def opaque_front_lip_mask(overlay: Image.Image) -> Image.Image:
    alpha = overlay.transpose(Image.Transpose.FLIP_TOP_BOTTOM).getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("native Pack overlay has no opaque pixels")
    left, top, right, bottom = bounds
    width = right - left
    height = bottom - top
    region = Image.new("L", alpha.size)
    region.paste(
        255,
        (
            int(left + width * 0.32),
            int(top + height * 0.30),
            int(left + width * 0.68),
            int(top + height * 0.39),
        ),
    )
    opaque = alpha.point(lambda value: 255 if value >= 180 else 0)
    return ImageChops.multiply(region, opaque)


def masked_mean(image: Image.Image, mask: Image.Image) -> float:
    bounds = mask.getbbox()
    if bounds is None:
        raise ValueError("required pixel mask is empty")
    pixels = image.convert("RGB").load()
    mask_pixels = mask.load()
    total = 0
    count = 0
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            if mask_pixels[x, y] > 0:
                red, green, blue = pixels[x, y]
                total += red + green + blue
                count += 3
    if count == 0:
        raise ValueError("required pixel mask has no selected pixels")
    return total / count


def masked_difference(
    first: Image.Image,
    second: Image.Image,
    mask: Image.Image,
) -> tuple[float, tuple[float, float] | None]:
    delta = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
    grayscale = delta.convert("L")
    bounds = mask.getbbox()
    if bounds is None:
        raise ValueError("required pixel mask is empty")
    pixels = grayscale.load()
    mask_pixels = mask.load()
    difference_total = 0
    count = 0
    moving_total = 0
    x_total = 0
    y_total = 0
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            if mask_pixels[x, y] == 0:
                continue
            value = pixels[x, y]
            difference_total += value
            count += 1
            if value >= 12:
                moving_total += value
                x_total += value * x
                y_total += value * y
    centroid: tuple[float, float] | None = None
    if moving_total > 0:
        centroid = (x_total / moving_total, y_total / moving_total)
    if count == 0:
        raise ValueError("required pixel mask has no selected pixels")
    return difference_total / count, centroid


def read_diagnostic(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sealed", type=Path, required=True)
    parser.add_argument("--partial", type=Path, required=True)
    parser.add_argument("--empty-mouth", type=Path, required=True)
    parser.add_argument("--contained-case", type=Path, required=True)
    parser.add_argument("--case-crossing", type=Path, required=True)
    parser.add_argument("--empty-overlay", type=Path, required=True)
    parser.add_argument("--contained-overlay", type=Path, required=True)
    parser.add_argument("--crossing-overlay", type=Path, required=True)
    parser.add_argument("--empty-diagnostic", type=Path, required=True)
    parser.add_argument("--contained-diagnostic", type=Path, required=True)
    parser.add_argument("--crossing-diagnostic", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    captures = {
        "sealed": load_rgba(args.sealed),
        "partial": load_rgba(args.partial),
        "emptyMouth": load_rgba(args.empty_mouth),
        "containedCase": load_rgba(args.contained_case),
        "caseCrossing": load_rgba(args.case_crossing),
    }
    overlays = {
        "emptyMouth": load_rgba(args.empty_overlay),
        "containedCase": load_rgba(args.contained_overlay),
        "caseCrossing": load_rgba(args.crossing_overlay),
    }
    diagnostics = {
        "emptyMouth": read_diagnostic(args.empty_diagnostic),
        "containedCase": read_diagnostic(args.contained_diagnostic),
        "caseCrossing": read_diagnostic(args.crossing_diagnostic),
    }
    failures: list[str] = []

    for name, image in captures.items():
        expect(
            image.size == captures["emptyMouth"].size,
            f"{name} size differs from the empty-mouth capture",
            failures,
        )
    for name, image in overlays.items():
        expect(
            image.size == captures["emptyMouth"].size,
            f"{name} overlay size differs from Simulator capture",
            failures,
        )
    for name, diagnostic in diagnostics.items():
        expect(
            diagnostic.get("hostIsOpaque") is False,
            f"{name} hosting view is opaque",
            failures,
        )
        expect(
            float(diagnostic.get("hostBackgroundAlpha", 1)) == 0,
            f"{name} hosting view has a background fill",
            failures,
        )
        expect(
            diagnostic.get("stage") in {"empty-mouth", "contained-case", "case-crossing"},
            f"{name} diagnostic has an unexpected static stage",
            failures,
        )
    expect(
        diagnostics["emptyMouth"].get("hasAuthoritativeReceipt") is False
        and diagnostics["emptyMouth"].get("hasStableUnityCase") is False,
        "empty mouth exposed a case before receipt readiness",
        failures,
    )
    for name in ("containedCase", "caseCrossing"):
        expect(
            diagnostics[name].get("hasAuthoritativeReceipt") is True
            and diagnostics[name].get("hasStableUnityCase") is True,
            f"{name} was captured before receipt and two-frame readiness",
            failures,
        )

    mouth_mask = transparent_mouth_mask(overlays["emptyMouth"])
    lip_mask = opaque_front_lip_mask(overlays["containedCase"])
    mouth_pixels = sum(1 for value in mouth_mask.getdata() if value > 0)
    lip_pixels = sum(1 for value in lip_mask.getdata() if value > 0)
    expect(mouth_pixels >= 300, "mouth cutout has too few transparent pixels", failures)
    expect(lip_pixels >= 300, "front lip has too few opaque pixels", failures)

    empty_mouth_luminance = masked_mean(captures["emptyMouth"], mouth_mask)
    contained_delta, contained_centroid = masked_difference(
        captures["emptyMouth"],
        captures["containedCase"],
        mouth_mask,
    )
    crossing_delta, crossing_centroid = masked_difference(
        captures["emptyMouth"],
        captures["caseCrossing"],
        mouth_mask,
    )
    lip_delta, _ = masked_difference(
        captures["emptyMouth"],
        captures["containedCase"],
        lip_mask,
    )
    expect(
        empty_mouth_luminance >= 10,
        "empty mouth reads as an opaque black UI hole",
        failures,
    )
    expect(
        contained_delta >= 8,
        "live case pixels do not appear through the mouth",
        failures,
    )
    expect(
        crossing_delta >= 8,
        "crossing case pixels do not appear through the mouth",
        failures,
    )
    expect(
        lip_delta <= contained_delta * 0.35,
        "case leaks through the opaque Pack front lip",
        failures,
    )
    if contained_centroid is not None and crossing_centroid is not None:
        expect(
            abs(crossing_centroid[1] - contained_centroid[1]) >= 2,
            "case pixels do not move between contained and crossing frames",
            failures,
        )
    else:
        failures.append("could not locate moving case pixels inside the mouth")

    report = {
        "candidate": "R027 isolated native hybrid",
        "captures": {name: str(path) for name, path in vars(args).items()
                     if name not in {"report"}},
        "metrics": {
            "mouthTransparentPixels": mouth_pixels,
            "frontLipOpaquePixels": lip_pixels,
            "emptyMouthLuminance": empty_mouth_luminance,
            "containedCaseDeltaInsideMouth": contained_delta,
            "caseCrossingDeltaInsideMouth": crossing_delta,
            "frontLipDelta": lip_delta,
            "containedCaseCentroid": contained_centroid,
            "caseCrossingCentroid": crossing_centroid,
        },
        "checks": {
            "transparentHost": not any(
                diagnostic.get("hostIsOpaque")
                or float(diagnostic.get("hostBackgroundAlpha", 1)) != 0
                for diagnostic in diagnostics.values()),
            "transparentMouth": mouth_pixels >= 300,
            "emptyMouthShowsUnityPixels": empty_mouth_luminance >= 10,
            "caseAppearsOnlyAfterReadiness": contained_delta >= 8,
            "packLipOccludesCase": lip_delta <= contained_delta * 0.35,
            "caseMovesContinuously": (
                contained_centroid is not None
                and crossing_centroid is not None
                and abs(crossing_centroid[1] - contained_centroid[1]) >= 2),
        },
        "failures": failures,
        "verdict": "pass" if not failures else "fail",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
