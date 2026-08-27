#!/usr/bin/env python3
"""Validate same-camera crystal gains and build a labeled comparison."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


OUTPUT = Path(__file__).resolve().parent
BASELINE = OUTPUT.parent / "rev-002/neutral-pbr-material-closeup.png"
CANDIDATE = OUTPUT / "neutral-pbr-material-closeup.png"
COMPARISON = OUTPUT / "same-camera-crystal-comparison.png"
REPORT = OUTPUT / "image-validation.json"
ROI = (30, 180, 1180, 1170)
FACE_ROI = (70, 220, 1130, 780)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[int], fraction: float) -> int:
    values.sort()
    return values[min(len(values) - 1, round((len(values) - 1) * fraction))]


def metrics(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    roi = rgb.crop(ROI)
    luma = roi.convert("L")
    luma_values = list(luma.getdata())
    pixels = list(roi.getdata())
    face_luma = list(rgb.crop(FACE_ROI).convert("L").getdata())
    pixel_count = len(luma_values)
    return {
        "sizePx": list(rgb.size),
        "roi": list(ROI),
        "meanLuma": round(ImageStat.Stat(luma).mean[0], 4),
        "stddevLuma": round(ImageStat.Stat(luma).stddev[0], 4),
        "highlightFractionAbove200": round(sum(value >= 200 for value in luma_values) / pixel_count, 6),
        "highlightFractionAbove230": round(sum(value >= 230 for value in luma_values) / pixel_count, 6),
        "clippedFractionAbove250": round(sum(value >= 250 for value in luma_values) / pixel_count, 6),
        "hardClipFraction255": round(sum(value == 255 for value in luma_values) / pixel_count, 6),
        "meanRgbChroma": round(sum(max(pixel) - min(pixel) for pixel in pixels) / pixel_count, 4),
        "faceContrastP90MinusP10": percentile(face_luma, 0.90) - percentile(face_luma, 0.10),
    }


def main() -> None:
    baseline = Image.open(BASELINE).convert("RGB")
    candidate = Image.open(CANDIDATE).convert("RGB")
    if baseline.size != candidate.size:
        raise RuntimeError("Same-camera comparison requires equal render sizes.")
    baseline_metrics = metrics(baseline)
    candidate_metrics = metrics(candidate)
    deltas = {
        key: round(candidate_metrics[key] - baseline_metrics[key], 6)
        for key in [
            "meanLuma",
            "stddevLuma",
            "highlightFractionAbove200",
            "highlightFractionAbove230",
            "clippedFractionAbove250",
            "hardClipFraction255",
            "meanRgbChroma",
            "faceContrastP90MinusP10",
        ]
    }
    deltas["highlightAbove230RelativeGain"] = round(
        candidate_metrics["highlightFractionAbove230"] / baseline_metrics["highlightFractionAbove230"] - 1.0,
        6,
    )
    checks = {
        "sameCameraResolution": baseline.size == candidate.size == (1200, 1200),
        "brightnessGain": candidate_metrics["meanLuma"] >= baseline_metrics["meanLuma"]
        and deltas["highlightAbove230RelativeGain"] >= 0.15,
        "highlightGain": candidate_metrics["highlightFractionAbove200"] > baseline_metrics["highlightFractionAbove200"],
        "colorSeparationGain": candidate_metrics["meanRgbChroma"] > baseline_metrics["meanRgbChroma"],
        "noMeaningfulClipping": candidate_metrics["clippedFractionAbove250"] < 0.01
        and candidate_metrics["hardClipFraction255"] < 0.002,
        "motifContrastMaintained": candidate_metrics["faceContrastP90MinusP10"]
        >= baseline_metrics["faceContrastP90MinusP10"] * 0.90,
    }

    header = 72
    canvas = Image.new("RGB", (baseline.width * 2, baseline.height + header), (12, 16, 22))
    canvas.paste(baseline, (0, header))
    canvas.paste(candidate, (baseline.width, header))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=22)
    draw.text((32, 24), "GATE 07 REV 2 · VARIANT B BASELINE", fill=(210, 220, 235), font=font)
    draw.text((baseline.width + 32, 24), "GATE 07 REV 3 · BRIGHTER CRYSTAL · NO EMISSION", fill=(245, 248, 255), font=font)
    canvas.save(COMPARISON)

    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 3,
        "comparisonMode": "same-camera-same-neutral-light",
        "baseline": {
            "path": str(BASELINE.relative_to(OUTPUT.parents[7])),
            "sha256": sha256(BASELINE),
            "metrics": baseline_metrics,
        },
        "candidate": {
            "path": CANDIDATE.name,
            "sha256": sha256(CANDIDATE),
            "metrics": candidate_metrics,
        },
        "deltas": deltas,
        "checks": checks,
        "comparisonPath": COMPARISON.name,
        "comparisonSha256": sha256(COMPARISON),
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Crystal comparison failed one or more image gates.")


if __name__ == "__main__":
    main()
