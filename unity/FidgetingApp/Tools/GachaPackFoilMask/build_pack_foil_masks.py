#!/usr/bin/env python3
"""Build the holographic-foil masks for the six sealed Pack bodies.

FDB-GAC-036 (user review 2026-09-07 17:22): the laser sheen must sit only on
the centre emblem and the text, not the whole bag. The Pack layers are
raster-only (exported from the approved contact sheet), so the mask is derived
from `gacha-pack-<tier>-body.png` (384 x 512):

1. emblem: the outer contour is convex, so the convex hull of the embossed
   outline segments (high-pass luminance > 14 inside the panel) is the
   silhouette. Derived once from STANDARD; the template is shared by all tiers.
2. tier label row ("STANDARD", "1 OF 1", ...): high-pass > 22 in the label
   band, specks < 5 px removed, dilated 1 px.
3. series text ("FIDGET ARCHIVE / SERIES 01") is printed darker than the
   foil: high-pass < -9 in its block, specks < 6 px removed, dilated 1 px.

Output: `gacha-pack-<tier>-foil.png`, white RGB with the mask in alpha,
0.8 px soft edge. Deterministic; re-running overwrites identical files.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from scipy.spatial import ConvexHull

TIERS = ["standard", "refined", "signature", "chase", "grail", "one-of-one"]
EMBLEM_REGION = (194, 374, 98, 292)  # y0, y1, x0, x1 inside the panel border
LABEL_REGION = (390, 418, 72, 300)  # below the panel rule at y ~386
SERIES_REGION = (124, 172, 74, 240)
BACKGROUND_BLUR = 9
EMBLEM_THRESHOLD = 14
EMBLEM_MIN_SEGMENT = 20
LABEL_THRESHOLD = 22
SERIES_THRESHOLD = -9  # negative: dark print on lighter foil
SOFT_EDGE_SIGMA = 0.8


def high_pass(body: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    rgb = np.asarray(body.convert("RGBA")).astype(float)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    blurred = Image.fromarray(lum.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(BACKGROUND_BLUR))
    return lum - np.asarray(blurred).astype(float), rgb[..., 3] / 255.0


def emblem_hull(hp: np.ndarray) -> list[tuple[float, float]]:
    y0, y1, x0, x1 = EMBLEM_REGION
    edges = np.zeros(hp.shape, bool)
    edges[y0:y1, x0:x1] = hp[y0:y1, x0:x1] > EMBLEM_THRESHOLD
    labels, count = ndimage.label(edges, structure=np.ones((3, 3)))
    sizes = ndimage.sum(edges, labels, range(1, count + 1))
    keep = np.isin(labels, [i + 1 for i, s in enumerate(sizes) if s >= EMBLEM_MIN_SEGMENT])
    ys, xs = np.nonzero(keep)
    points = np.stack([xs, ys], 1)
    hull = ConvexHull(points)
    return [tuple(map(float, points[v])) for v in hull.vertices]


def text_mask(hp: np.ndarray, region, threshold: float, min_size: int) -> np.ndarray:
    """Positive threshold keeps print lighter than the foil, negative keeps darker."""
    y0, y1, x0, x1 = region
    mask = np.zeros(hp.shape, bool)
    block = hp[y0:y1, x0:x1]
    mask[y0:y1, x0:x1] = block > threshold if threshold >= 0 else block < threshold
    mask = ndimage.binary_opening(mask, structure=np.ones((2, 2)))
    labels, count = ndimage.label(mask)
    if count:
        sizes = ndimage.sum(mask, labels, range(1, count + 1))
        for index, size in enumerate(sizes):
            if size < min_size:
                mask[labels == index + 1] = False
    return ndimage.binary_dilation(mask, iterations=1)


def build(pack_dir: Path, out_dir: Path) -> None:
    standard = Image.open(pack_dir / "gacha-pack-standard-body.png")
    hp_standard, _ = high_pass(standard)
    hull = emblem_hull(hp_standard)
    emblem = Image.new("L", standard.size, 0)
    ImageDraw.Draw(emblem).polygon(hull, fill=255)
    emblem_mask = ndimage.binary_erosion(np.asarray(emblem) > 127, iterations=1)

    for tier in TIERS:
        body = Image.open(pack_dir / f"gacha-pack-{tier}-body.png")
        hp, alpha = high_pass(body)
        mask = emblem_mask.copy()
        mask |= text_mask(hp, LABEL_REGION, LABEL_THRESHOLD, 5)
        mask |= text_mask(hp, SERIES_REGION, SERIES_THRESHOLD, 6)
        mask &= alpha > 0.5
        soft = ndimage.gaussian_filter(mask.astype(float), SOFT_EDGE_SIGMA)
        out = np.zeros(mask.shape + (4,), np.uint8)
        out[..., :3] = 255
        out[..., 3] = np.clip(soft * 255, 0, 255).astype(np.uint8)
        target = out_dir / f"gacha-pack-{tier}-foil.png"
        Image.fromarray(out).save(target, optimize=True)
        print(f"{target.name}: emblem {int(emblem_mask.sum())} px, total {int(mask.sum())} px")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2] / "Assets" / "Plugins" / "iOS" / "GachaPacks"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else root
    out.mkdir(parents=True, exist_ok=True)
    build(root, out)
