#!/usr/bin/env python3
"""Quantify the real top-render capsule silhouette."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
IMAGE_PATH = ROOT / "silhouette-top.png"
REPORT_PATH = ROOT / "blockout-validation.json"
ALPHA_THRESHOLD = 16
REVERSAL_TOLERANCE_PX = 2


def row_edges(alpha: Image.Image, box: tuple[int, int, int, int]) -> list[tuple[int, int, int]]:
    left, top, right, bottom = box
    pixels = alpha.load()
    rows = []
    for y in range(top, bottom):
        opaque = [x for x in range(left, right) if pixels[x, y] >= ALPHA_THRESHOLD]
        if not opaque:
            continue
        start = opaque[0]
        end = opaque[-1]
        gaps = sum(1 for x in range(start, end + 1) if pixels[x, y] < ALPHA_THRESHOLD)
        rows.append((start, end, gaps))
    return rows


def monotonic_violations(values: list[int], direction: str) -> tuple[int, int]:
    violations = []
    for previous, current in zip(values, values[1:]):
        error = current - previous if direction == "nonincreasing" else previous - current
        if error > REVERSAL_TOLERANCE_PX:
            violations.append(error)
    return len(violations), max(violations, default=0)


def main() -> None:
    with Image.open(IMAGE_PATH) as image:
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        box = alpha.point(lambda value: 255 if value >= ALPHA_THRESHOLD else 0).getbbox()
        if not box:
            raise RuntimeError("Rendered silhouette is empty.")
        rows = row_edges(alpha, box)
        width = box[2] - box[0]
        height = box[3] - box[1]
        cap_rows = round(height * 15.5 / 50.0)
        top_rows = rows[:cap_rows]
        bottom_rows = rows[-cap_rows:]

        checks = [
            monotonic_violations([row[0] for row in top_rows], "nonincreasing"),
            monotonic_violations([row[1] for row in top_rows], "nondecreasing"),
            monotonic_violations([row[0] for row in bottom_rows], "nondecreasing"),
            monotonic_violations([row[1] for row in bottom_rows], "nonincreasing"),
        ]
        violation_count = sum(check[0] for check in checks)
        maximum_reversal = max(check[1] for check in checks)
        rows_with_gaps = sum(1 for row in rows if row[2] > 0)
        aspect_ratio = height / width
        target_aspect_ratio = 50.0 / 31.0
        aspect_error = abs(aspect_ratio - target_aspect_ratio) / target_aspect_ratio
        passed = (
            rgba.size == (2048, 2048)
            and rows_with_gaps == 0
            and violation_count == 0
            and maximum_reversal == 0
            and aspect_error <= 0.005
            and width >= 1000
            and height >= 1600
        )

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    report["renderedSilhouette"] = {
        "source": IMAGE_PATH.name,
        "renderSizePx": [2048, 2048],
        "alphaThreshold": ALPHA_THRESHOLD,
        "boundingBoxPx": list(box),
        "silhouetteWidthPx": width,
        "silhouetteHeightPx": height,
        "measuredAspectRatio": aspect_ratio,
        "targetAspectRatio": target_aspect_ratio,
        "relativeAspectError": aspect_error,
        "rowsWithInteriorAlphaGaps": rows_with_gaps,
        "monotonicCapReversalTolerancePx": REVERSAL_TOLERANCE_PX,
        "monotonicCapViolationCount": violation_count,
        "maximumContourReversalPx": maximum_reversal,
        "pass": passed,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not passed:
        raise RuntimeError(json.dumps(report["renderedSilhouette"], indent=2))


if __name__ == "__main__":
    main()
