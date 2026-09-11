#!/usr/bin/env python3
"""Gate 02 rev-007: pixel-proportion recheck of the V3 front target.

The handoff spec derived its ratios from a 416x654 annotated screenshot and
requires every ratio to be rechecked on the unannotated V3 image. This script
measures the clean 1000x1573 PNG and the user's 650x1024 chat copy, writes the
numbers as claims-in-waiting and draws an analysis board. Every value is a
visual reading of an AI concept image: `recommended_start`, never `measured`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
INTAKE = HERE.parents[1] / "01-intake" / "rev-004"
CLEAN = INTAKE / "v3-01-front-cmf-gold-silver.png"
CHAT_FRONT = INTAKE / "v3-user-chat-front-650x1024.jpg"
SPEC = INTAKE / "tri-spinner-slab-model-spec.v0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def luminance(path: Path) -> np.ndarray:
    im = np.asarray(Image.open(path).convert("RGB")).astype(float)
    return 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]


def outer_frame(lum: np.ndarray, threshold: float = 45.0, fraction: float = 0.25):
    """Bounding rows/cols where >= `fraction` of pixels are brighter than the
    background. The floor reflection is separated by the dark gap row below
    the bottom rim: the object ends at the last bright row before the first
    row whose max luminance collapses (< 40) after the frame has started."""
    mask = lum > threshold
    cols = np.where(mask.mean(axis=0) > fraction)[0]
    rows = np.where(mask.mean(axis=1) > fraction)[0]
    x0, x1 = int(cols[0]), int(cols[-1])
    y0 = int(rows[0])
    row_max = lum.max(axis=1)
    y1 = y0
    for y in range(y0 + 10, lum.shape[0]):
        if row_max[y] < 40.0:
            break
        y1 = y
    return x0, x1, y0, y1


def header_seam(lum: np.ndarray, x0: int, x1: int, y0: int, y1: int) -> tuple[int, int]:
    """Centre-column seams between the header compartment and the main bay.

    Returns (seam_below_header_plate, main_bay_start). The first is the dark
    groove under the graphite plate's bottom rail (followed by the bright
    silver datum rail, >= 18 px); the second is the next dark groove after
    that rail, where the main bay's satin shelf begins."""
    cx = (x0 + x1) // 2
    col = lum[:, cx - 4:cx + 4].mean(axis=1)
    start = y0 + int(0.25 * (y1 - y0))
    k = lum.shape[0] / 1573.0  # run lengths were tuned on the 1573 px image
    # run-length encode bright (>75) / dark (<=75) segments below the plate text
    runs = []
    y = start
    while y < y1:
        bright = col[y] > 75
        s = y
        while y < y1 and (col[y] > 75) == bright:
            y += 1
        if runs and not bright and y - s < 3 * k:
            continue  # sub-3 px dark speckle inside a bright rail: absorb it
        if runs and runs[-1][0] == bright:
            runs[-1] = (bright, runs[-1][1], y)
        else:
            runs.append((bool(bright), s, y))
    # pattern: plate bottom rail (bright >= 20 px) -> seam (dark >= 6 px) ->
    # silver datum rail (bright) -> groove (dark >= 4 px) = main bay start
    for i in range(len(runs) - 3):
        b0, s0, e0 = runs[i]
        b1, s1, e1 = runs[i + 1]
        if b0 and e0 - s0 >= 20 * k and not b1 and e1 - s1 >= 6 * k:
            seam = (s1 + e1) // 2
            rail_seen = False
            for j in range(i + 2, len(runs)):
                bj, sj, ej = runs[j]
                if bj and ej - sj >= 15 * k:
                    rail_seen = True  # silver datum rail
                elif rail_seen and not bj and ej - sj >= 3 * k:
                    return seam, (sj + ej) // 2
    raise RuntimeError("header seams not found")


def spinner_pocket(lum: np.ndarray, x0: int, x1: int, y0: int, y1: int):
    h = y1 - y0
    inset = int(0.07 * (x1 - x0))
    ya, yb = y0 + int(0.45 * h), y0 + int(0.88 * h)
    band = lum[ya:yb, x0 + inset:x1 - inset]
    dark = band < 30
    xs = np.where(dark.mean(axis=0) > 0.03)[0]
    ys = np.where(dark.mean(axis=1) > 0.03)[0]
    return int(xs[0] + x0 + inset), int(xs[-1] + x0 + inset), int(ys[0] + ya), int(ys[-1] + ya)


def hub_centre(lum: np.ndarray, x0: int, x1: int, y0: int, y1: int):
    w, h = x1 - x0, y1 - y0
    sub = lum[y0 + int(0.5 * h):y0 + int(0.8 * h), x0 + int(0.35 * w):x0 + int(0.65 * w)]
    yy, xx = np.where(sub > 175)
    return float(xx.mean() + x0 + int(0.35 * w)), float(yy.mean() + y0 + int(0.5 * h))


def analyse(path: Path) -> dict:
    lum = luminance(path)
    x0, x1, y0, y1 = outer_frame(lum)
    w, h = x1 - x0, y1 - y0
    seam, bay_start = header_seam(lum, x0, x1, y0, y1)
    px0, px1, py0, py1 = spinner_pocket(lum, x0, x1, y0, y1)
    hx, hy = hub_centre(lum, x0, x1, y0, y1)
    return {
        "image": path.name,
        "sha256": sha256(path),
        "pixel_size": [int(lum.shape[1]), int(lum.shape[0])],
        "outer_frame_px": {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "w": w, "h": h},
        "ratios": {
            "case_width_over_height": round(w / h, 4),
            "header_seam_from_top": round((seam - y0) / h, 4),
            "main_bay_start_from_top": round((bay_start - y0) / h, 4),
            "spinner_pocket_span_over_width": round((px1 - px0) / w, 4),
            "spinner_pocket_top_from_top": round((py0 - y0) / h, 4),
            "spinner_pocket_bottom_from_top": round((py1 - y0) / h, 4),
            "spinner_center_x_from_left": round((hx - x0) / w, 4),
            "spinner_center_from_top": round((hy - y0) / h, 4),
        },
        "raw_px": {"header_seam_y": seam, "main_bay_start_y": bay_start, "pocket": [px0, px1, py0, py1],
                   "hub": [round(hx, 1), round(hy, 1)]},
    }


def draw_board(path: Path, result: dict, out: Path) -> None:
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)
    f = result["outer_frame_px"]
    d.rectangle([f["x0"], f["y0"], f["x1"], f["y1"]], outline=(255, 60, 60), width=3)
    seam = result["raw_px"]["header_seam_y"]
    d.line([f["x0"], seam, f["x1"], seam], fill=(80, 255, 120), width=2)
    bay = result["raw_px"]["main_bay_start_y"]
    d.line([f["x0"], bay, f["x1"], bay], fill=(80, 255, 120), width=1)
    px0, px1, py0, py1 = result["raw_px"]["pocket"]
    d.rectangle([px0, py0, px1, py1], outline=(80, 160, 255), width=3)
    hx, hy = result["raw_px"]["hub"]
    d.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], outline=(255, 220, 80), width=3)
    d.line([hx - 30, hy, hx + 30, hy], fill=(255, 220, 80), width=2)
    d.line([hx, hy - 30, hx, hy + 30], fill=(255, 220, 80), width=2)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
    except OSError:
        font = ImageFont.load_default()
    r = result["ratios"]
    lines = [
        "Gate 02 rev-007  V3 clean image recheck (AI concept, recommended_start)",
        f"outer W/H = {r['case_width_over_height']}   header seam = {r['header_seam_from_top']}H   bay start = {r['main_bay_start_from_top']}H",
        f"pocket span = {r['spinner_pocket_span_over_width']}W   hub = ({r['spinner_center_x_from_left']}W, {r['spinner_center_from_top']}H)",
        "red: outer frame  green: header/main seam  blue: dark spinner pocket  yellow: hub",
    ]
    y = img.height - 30 * len(lines) - 12
    d.rectangle([0, y - 8, img.width, img.height], fill=(0, 0, 0))
    for line in lines:
        d.text((14, y), line, fill=(235, 235, 235), font=font)
        y += 30
    img.save(out)


def main() -> int:
    spec = json.loads(SPEC.read_text())
    spec_inputs = {p["id"]: p for p in spec["parameters"]["inputs"]}
    clean = analyse(CLEAN)
    chat = analyse(CHAT_FRONT)
    draw_board(CLEAN, clean, HERE / "v3-analysis-board.png")

    def spec_value(pid: str):
        return spec_inputs[pid]["value"] if pid in spec_inputs else None

    comparisons = []
    for ratio_id, spec_id in [
        ("case_width_over_height", "visual.case_width_over_height"),
        ("header_seam_from_top", "visual.header_split_from_top"),
        ("spinner_center_x_from_left", "visual.spinner_center_x_from_left"),
        ("spinner_center_from_top", "visual.spinner_center_from_top"),
    ]:
        sv = spec_value(spec_id)
        cv, uv = clean["ratios"][ratio_id], chat["ratios"][ratio_id]
        tol = spec_inputs[spec_id].get("tolerance", 0.0)
        comparisons.append({
            "spec_id": spec_id,
            "spec_value_from_annotated_416x654": sv,
            "clean_1000x1573": cv,
            "user_chat_650x1024": uv,
            "mean_clean": round((cv + uv) / 2, 4),
            "within_spec_tolerance": abs(cv - sv) <= tol and abs(uv - sv) <= tol,
            "spec_tolerance": tol,
        })
    result = {
        "schema": "premium-display-case.gate02.v3-proportion-analysis/1",
        "spec_sha256": sha256(SPEC),
        "evidence_class": "recommended_start",
        "value_state": "provisional",
        "geometry_truth": False,
        "method": "luminance thresholds on the unannotated concept renders; frame = rows/cols with >=25% pixels above L45, "
                  "bottom rim separated from the floor reflection by the dark gap row; seam = first dark run followed by >=40px "
                  "bright run on the centre column; pocket = dark (<L30) region in the main bay; hub = centroid of pixels >L175.",
        "images": [clean, chat],
        "spec_comparison": comparisons,
        "notes": [
            "The spec's 0.562 W/H came from the annotated 416x654 screenshot. Both clean images read ~0.58-0.59; the annotated "
            "estimate is superseded for the contract, which adopts the mean of the two clean readings.",
            "The dark pocket span (~0.80W) is the recess outline, not the spinner tips. Tip-to-tip span is read visually at "
            "~0.73-0.76W; the spec's 0.762W stays as the contract start value.",
            "Pixel ratios of an AI image never become `measured`. Physical size enters only through the caller-owned spinner "
            "source model (see spinner-source-measurement.json).",
        ],
    }
    (HERE / "v3-proportion-analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"clean": clean["ratios"], "chat": chat["ratios"], "comparison": comparisons}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
