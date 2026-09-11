#!/usr/bin/env python3
"""Verify real R028 Simulator Pack and live-case captures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops


EXPECTED_CASE_ROOT = "PremiumDisplayCaseGate12R004"
EXPECTED_CASE_TYPE = (
    "FidgetingApp.DisplayCase.PremiumDisplayCaseShippingPresentation"
)


def load_rgba(path: Path) -> Image.Image:
    if not path.is_file():
        raise ValueError(f"missing capture: {path}")
    return Image.open(path).convert("RGBA")


def read_diagnostic(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def mouth_mask_from_diagnostic(
    image: Image.Image,
    diagnostic: dict[str, Any],
) -> Image.Image:
    bounds = diagnostic.get("mouthBoundsPoints")
    scale = float(diagnostic.get("overlayDisplayScale", 0))
    overlay_width = int(diagnostic.get("overlayPixelWidth", 0))
    overlay_height = int(diagnostic.get("overlayPixelHeight", 0))
    if (
        not isinstance(bounds, dict)
        or scale <= 0
        or overlay_width <= 0
        or overlay_height <= 0
    ):
        raise ValueError("ready overlay diagnostic has no mouth bounds")
    x_scale = image.width / overlay_width
    y_scale = image.height / overlay_height
    left = int(float(bounds["x"]) * scale * x_scale)
    top = int(float(bounds["y"]) * scale * y_scale)
    right = int((float(bounds["x"]) + float(bounds["width"])) * scale * x_scale)
    bottom = int((float(bounds["y"]) + float(bounds["height"])) * scale * y_scale)
    mask = Image.new("L", image.size)
    mask.paste(255, (left, top, right, bottom))
    return mask


def masked_difference(
    first: Image.Image,
    second: Image.Image,
    mask: Image.Image,
) -> float:
    delta = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
    grayscale = delta.convert("L")
    bounds = mask.getbbox()
    if bounds is None:
        raise ValueError("required pixel mask is empty")
    pixels = grayscale.load()
    mask_pixels = mask.load()
    total = 0
    count = 0
    for y in range(bounds[1], bounds[3]):
        for x in range(bounds[0], bounds[2]):
            if mask_pixels[x, y] == 0:
                continue
            total += pixels[x, y]
            count += 1
    if count == 0:
        raise ValueError("required pixel mask has no selected pixels")
    return total / count


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sealed", type=Path, required=True)
    parser.add_argument("--partial", type=Path, required=True)
    parser.add_argument("--pre-ready-mouth", type=Path, required=True)
    parser.add_argument("--contained-case", type=Path, required=True)
    parser.add_argument("--case-crossing", type=Path, required=True)
    parser.add_argument("--pack-departed", type=Path, required=True)
    parser.add_argument("--sealed-diagnostic", type=Path, required=True)
    parser.add_argument("--partial-diagnostic", type=Path, required=True)
    parser.add_argument("--pre-ready-diagnostic", type=Path, required=True)
    parser.add_argument("--contained-diagnostic", type=Path, required=True)
    parser.add_argument("--crossing-diagnostic", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    captures = {
        "sealed": load_rgba(args.sealed),
        "partial": load_rgba(args.partial),
        "preReadyMouth": load_rgba(args.pre_ready_mouth),
        "containedCase": load_rgba(args.contained_case),
        "caseCrossing": load_rgba(args.case_crossing),
        "packDeparted": load_rgba(args.pack_departed),
    }
    diagnostics = {
        "sealed": read_diagnostic(args.sealed_diagnostic),
        "partial": read_diagnostic(args.partial_diagnostic),
        "preReadyMouth": read_diagnostic(args.pre_ready_diagnostic),
        "containedCase": read_diagnostic(args.contained_diagnostic),
        "caseCrossing": read_diagnostic(args.crossing_diagnostic),
    }
    failures: list[str] = []

    reference_size = captures["sealed"].size
    for name, image in captures.items():
        expect(
            image.size == reference_size,
            f"{name} size differs from the sealed Simulator capture",
            failures,
        )
    for name, diagnostic in diagnostics.items():
        expect(
            diagnostic.get("hostIsOpaque") is False,
            f"{name} native host is opaque",
            failures,
        )
        expect(
            float(diagnostic.get("hostBackgroundAlpha", 1)) == 0,
            f"{name} native host has a background fill",
            failures,
        )
        expect(
            diagnostic.get("caseRootName") == EXPECTED_CASE_ROOT,
            f"{name} did not stage the canonical Premium Display Case root",
            failures,
        )
        expect(
            diagnostic.get("caseTypeName") == EXPECTED_CASE_TYPE,
            f"{name} did not stage the canonical case component type",
            failures,
        )
        expect(
            bool(diagnostic.get("caseEntityID")),
            f"{name} has no Unity case entity id",
            failures,
        )
        expect(
            int(diagnostic.get("caseRendererCount", 0)) > 0,
            f"{name} canonical case has no renderers",
            failures,
        )
        expect(
            diagnostic.get("caseIsCanonical") is True,
            f"{name} did not retain the canonical case identity",
            failures,
        )
        expect(
            diagnostic.get("caseIsOnlyUnityRenderable") is True,
            f"{name} camera can render a non-case Unity object",
            failures,
        )
        expect(
            diagnostic.get("unityClearBackdropIsolated") is True,
            f"{name} camera still exposes its scene backdrop",
            failures,
        )

    for name in ("sealed", "partial", "preReadyMouth"):
        diagnostic = diagnostics[name]
        expect(
            diagnostic.get("apertureAuthorized") is False,
            f"{name} authorized a live aperture before readiness",
            failures,
        )
        expect(
            diagnostic.get("transparentMouthPixels") == 0,
            f"{name} has transparent mouth pixels before readiness",
            failures,
        )
        expect(
            diagnostic.get("apertureAlphaIsZero") is True,
            f"{name} did not record zero pre-ready aperture alpha",
            failures,
        )
        expect(
            int(diagnostic.get("protectedOuterMinimumAlpha", 0)) >= 240,
            f"{name} Pack front lost opacity outside the torn region",
            failures,
        )

    for name in ("containedCase", "caseCrossing"):
        diagnostic = diagnostics[name]
        expect(
            diagnostic.get("hasAuthoritativeReceipt") is True
            and diagnostic.get("hasStableUnityCase") is True,
            f"{name} aperture lacks same-request receipt or two-frame readiness",
            failures,
        )
        expect(
            diagnostic.get("apertureAuthorized") is True,
            f"{name} did not authorize the ready aperture",
            failures,
        )
        expect(
            int(diagnostic.get("transparentMouthPixels", 0)) >= 300,
            f"{name} ready aperture has too few transparent pixels",
            failures,
        )
        expect(
            diagnostic.get("apertureIsShapedAndBounded") is True,
            f"{name} aperture is not confined to the mouth shape",
            failures,
        )
        expect(
            int(diagnostic.get("protectedOuterMinimumAlpha", 0)) >= 240,
            f"{name} front lip does not occlude the lower case",
            failures,
        )

    ready_mouth_mask = mouth_mask_from_diagnostic(
        captures["containedCase"],
        diagnostics["containedCase"],
    )
    ready_mouth_pixels = sum(
        1 for value in ready_mouth_mask.getdata() if value > 0
    )
    expect(
        ready_mouth_pixels >= 300,
        "contained-case overlay has no shaped live aperture",
        failures,
    )
    contained_delta = masked_difference(
        captures["preReadyMouth"],
        captures["containedCase"],
        ready_mouth_mask,
    )
    crossing_delta = masked_difference(
        captures["containedCase"],
        captures["caseCrossing"],
        ready_mouth_mask,
    )
    expect(
        contained_delta >= 8,
        "real case pixels did not replace the opaque pre-ready cavity",
        failures,
    )
    expect(
        crossing_delta >= 2,
        "live case pixels did not move through the Pack lip",
        failures,
    )

    report = {
        "candidate": "R028 isolated native hybrid",
        "captures": {
            name: str(value)
            for name, value in vars(args).items()
            if name != "report"
        },
        "metrics": {
            "readyMouthPixels": ready_mouth_pixels,
            "containedCaseDeltaInsideMouth": contained_delta,
            "caseCrossingDeltaInsideMouth": crossing_delta,
        },
        "checks": {
            "transparentNativeHost": not any(
                diagnostic.get("hostIsOpaque")
                or float(diagnostic.get("hostBackgroundAlpha", 1)) != 0
                for diagnostic in diagnostics.values()
            ),
            "preReadyApertureAlphaZero": not any(
                diagnostic.get("transparentMouthPixels") != 0
                for name, diagnostic in diagnostics.items()
                if name in {"sealed", "partial", "preReadyMouth"}
            ),
            "readyApertureBounded": all(
                diagnostic.get("apertureIsShapedAndBounded") is True
                for name, diagnostic in diagnostics.items()
                if name in {"containedCase", "caseCrossing"}
            ),
            "canonicalCaseOnly": all(
                diagnostic.get("caseIsCanonical") is True
                and diagnostic.get("caseIsOnlyUnityRenderable") is True
                and diagnostic.get("unityClearBackdropIsolated") is True
                for diagnostic in diagnostics.values()
            ),
            "casePixelsAppearAfterReadiness": contained_delta >= 8,
            "caseCrossesLip": crossing_delta >= 2,
        },
        "failures": failures,
        "verdict": "pass" if not failures else "fail",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
