"""Gate 02 frame measurements for the GEEONE dragon-scale tri-spinner video.

Input: 10 fps frames extracted from the Gate 01 source video
(`/tmp/dragon-scale-gate02/video/frames10/f_NNNN.jpg`, ffmpeg fps=10).
Only frames with the spinner lying on the black table are used for silhouette
measurements; the black background makes the outline unambiguous.

Method (all in pixels, then ratios; no millimetres are produced here):
1. Threshold the frame, keep the largest bright component = spinner silhouette.
2. Boundary points in polar form around the silhouette centroid. The three
   radial minima lie on the cap crown (the cap protrudes into every notch), so
   an ellipse fitted to the notch-bottom points is the cap outline under the
   oblique camera. Mapping that ellipse to a circle rectifies the view.
3. In the rectified plane: cap radius, tip-circle radius (three maxima),
   polar angle where each blade edge leaves the cap (exposed cap arc per
   notch), straight-edge directions (tip included angle), tip fillet radius
   (circle fit on the tip points), and the table/crown boundary (radius where
   the angular intensity variance of the cap jumps).
Every output is tagged with the frame id, timestamp and the crop used.
"""

from __future__ import annotations

import json
import math
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
FRAMES = Path("/tmp/dragon-scale-gate02/video/frames10")
OUT = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006"
FPS = 10.0
TABLE_FRAMES = [74, 75, 76, 77, 78, 79]  # spinner flat on the black table, t = 7.3-7.8 s
CROP = (40, 280, 700, 940)  # x0, y0, x1, y1 in the 720x1280 frame


def font(size: int):
    for candidate in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Menlo.ttc"):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def largest_component(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = None
    for sy in range(h):
        for sx in range(w):
            if mask[sy, sx] and not seen[sy, sx]:
                comp = []
                dq = deque([(sy, sx)])
                seen[sy, sx] = True
                while dq:
                    y, x = dq.popleft()
                    comp.append((y, x))
                    for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            dq.append((ny, nx))
                if best is None or len(comp) > len(best):
                    best = comp
    out = np.zeros_like(mask, dtype=bool)
    ys, xs = zip(*best)
    out[list(ys), list(xs)] = True
    return out


def fill_holes(mask: np.ndarray) -> np.ndarray:
    """Flood the background from the border; everything not reached is object."""
    h, w = mask.shape
    reach = np.zeros_like(mask, dtype=bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not mask[y, x] and not reach[y, x]:
                reach[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not mask[y, x] and not reach[y, x]:
                reach[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and not reach[ny, nx]:
                reach[ny, nx] = True
                dq.append((ny, nx))
    return ~reach


def boundary_points(mask: np.ndarray) -> np.ndarray:
    m = mask
    inner = m[1:-1, 1:-1] & m[:-2, 1:-1] & m[2:, 1:-1] & m[1:-1, :-2] & m[1:-1, 2:]
    edge = m[1:-1, 1:-1] & ~inner
    ys, xs = np.nonzero(edge)
    return np.stack([xs + 1, ys + 1], axis=1).astype(float)


def fit_ellipse(pts: np.ndarray):
    """Direct least-squares conic fit -> centre, semi-axes, rotation (radians)."""
    x, y = pts[:, 0], pts[:, 1]
    d = np.stack([x * x, x * y, y * y, x, y, np.ones_like(x)], axis=1)
    _, _, vt = np.linalg.svd(d, full_matrices=False)
    a, b, c, dd, e, f = vt[-1]
    m = np.array([[a, b / 2], [b / 2, c]])
    centre = np.linalg.solve(-2 * m, np.array([dd, e]))
    k = -(f + 0.5 * (dd * centre[0] + e * centre[1]))
    evals, evecs = np.linalg.eigh(m / k)
    axes = 1.0 / np.sqrt(np.abs(evals))
    angle = math.atan2(evecs[1, 0], evecs[0, 0])
    return centre, axes, angle


def rectify(pts: np.ndarray, centre, axes, angle) -> np.ndarray:
    """Map the fitted ellipse onto a circle of radius max(axes): rotate into the
    ellipse frame, stretch the minor axis, rotate back."""
    c, s = math.cos(-angle), math.sin(-angle)
    p = pts - centre
    q = np.stack([c * p[:, 0] - s * p[:, 1], s * p[:, 0] + c * p[:, 1]], axis=1)
    scale = axes.max() / axes
    q = q * scale
    c2, s2 = math.cos(angle), math.sin(angle)
    return np.stack([c2 * q[:, 0] - s2 * q[:, 1], s2 * q[:, 0] + c2 * q[:, 1]], axis=1)


def fit_circle(pts: np.ndarray):
    x, y = pts[:, 0], pts[:, 1]
    a = np.stack([x, y, np.ones_like(x)], axis=1)
    b = x * x + y * y
    sol, *_ = np.linalg.lstsq(a, b, rcond=None)
    cx, cy = sol[0] / 2, sol[1] / 2
    r = math.sqrt(sol[2] + cx * cx + cy * cy)
    return (cx, cy), r


def fit_line(pts: np.ndarray):
    mean = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - mean)
    direction = vt[0]
    return mean, direction / np.linalg.norm(direction)


def analyse_frame(index: int) -> dict:
    path = FRAMES / f"f_{index:04d}.jpg"
    frame = Image.open(path).convert("RGB")
    crop = frame.crop(CROP)
    gray = np.asarray(crop.convert("L"), dtype=float)
    # Otsu threshold
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    total = gray.size
    best_t, best_v = 0, -1.0
    sum_all = (hist * np.arange(256)).sum()
    w0 = 0.0
    s0 = 0.0
    for t in range(256):
        w0 += hist[t]
        if w0 == 0 or w0 == total:
            continue
        s0 += t * hist[t]
        m0 = s0 / w0
        m1 = (sum_all - s0) / (total - w0)
        v = w0 * (total - w0) * (m0 - m1) ** 2
        if v > best_v:
            best_v, best_t = v, t
    thr = 0.55 * best_t  # crown facets are darker than the plateau; the cloth is near black
    mask = gray > thr
    mask = fill_holes(largest_component(mask))
    ys, xs = np.nonzero(mask)
    centroid = np.array([xs.mean(), ys.mean()])
    bpts = boundary_points(mask)
    rel = bpts - centroid
    ang = np.degrees(np.arctan2(-rel[:, 1], rel[:, 0])) % 360.0  # image y is down
    rad = np.hypot(rel[:, 0], rel[:, 1])
    order = np.argsort(ang)
    ang, rad, bpts = ang[order], rad[order], bpts[order]

    # smooth radius over angle and find three minima / three maxima
    bins = 360
    prof = np.full(bins, np.nan)
    for k in range(bins):
        sel = (ang >= k) & (ang < k + 1)
        if sel.any():
            prof[k] = rad[sel].mean()
    prof = np.where(np.isnan(prof), np.nanmean(prof), prof)
    kernel = np.ones(7) / 7.0
    sm = np.convolve(np.concatenate([prof[-3:], prof, prof[:3]]), kernel, mode="valid")

    def extrema(sign: float):
        found = []
        for k in range(bins):
            window = [sm[(k + d) % bins] for d in range(-40, 41)]
            if sign * sm[k] >= sign * max(window) if sign > 0 else sm[k] <= min(window):
                found.append(k)
        # merge neighbours
        merged = []
        for k in found:
            if not merged or (k - merged[-1][-1]) % bins > 5:
                merged.append([k])
            else:
                merged[-1].append(k)
        return [int(np.mean(g)) for g in merged]

    maxima = extrema(1.0)
    minima = extrema(-1.0)
    if len(maxima) != 3 or len(minima) != 3:
        return {"frame": index, "error": f"expected 3 maxima/minima, got {maxima} / {minima}"}

    # notch-bottom points: within +/-6 deg of each minimum and within 3% of the minimum radius
    notch_pts = []
    for k in minima:
        sel = (np.abs(((ang - k + 180) % 360) - 180) <= 8.0) & (rad <= sm[k] * 1.04)
        notch_pts.append(bpts[sel])
    notch_all = np.concatenate(notch_pts)
    centre, axes, angle = fit_ellipse(notch_all)
    tilt_deg = math.degrees(math.acos(min(1.0, axes.min() / axes.max())))
    rect = rectify(bpts, centre, axes, angle)  # rectified boundary, origin at cap centre
    r_cap = float(axes.max())
    rang = np.degrees(np.arctan2(-rect[:, 1], rect[:, 0])) % 360.0
    rrad = np.hypot(rect[:, 0], rect[:, 1])

    # tips in rectified space
    tips = []
    for k in maxima:
        sel = np.abs(((rang - k + 180) % 360) - 180) <= 12.0
        j = np.argmax(np.where(sel, rrad, -1))
        tips.append((float(rang[j]), float(rrad[j])))
    r_tip = float(np.mean([t[1] for t in tips]))
    tip_spacing = sorted(((tips[(i + 1) % 3][0] - tips[i][0]) % 360) for i in range(3))

    # for each notch: where does the boundary leave the cap circle (r > 1.04 r_cap)?
    exposed = []
    for k in minima:
        kk = (k - math.degrees(angle) * 0)  # minima angles are in original space; recompute in rectified
        sel = np.abs(((rang - k + 180) % 360) - 180) <= 40.0
        a_sel, r_sel = rang[sel], rrad[sel]
        rel_a = ((a_sel - k + 180) % 360) - 180
        on_cap = r_sel <= r_cap * 1.04
        left = rel_a[on_cap & (rel_a < 0)]
        right = rel_a[on_cap & (rel_a > 0)]
        if len(left) and len(right):
            exposed.append(float(right.max() - left.min()))

    # straight edge directions and tip included angle: points between 55% and 90% of the tip radius on each side of a tip
    tip_angles, tip_radii, edge_dirs = [], [], []
    for a_tip, r_t in tips:
        rel_a = ((rang - a_tip + 180) % 360) - 180
        sides = []
        for sgn in (-1, 1):
            sel = (np.sign(rel_a) == sgn) & (rrad > 0.60 * r_t) & (rrad < 0.90 * r_t) & (np.abs(rel_a) < 40)
            if sel.sum() < 8:
                sides.append(None)
                continue
            mean, d = fit_line(rect[sel])
            sides.append((mean, d))
        if all(s is not None for s in sides):
            d0, d1 = sides[0][1], sides[1][1]
            cosang = abs(float(np.dot(d0, d1)))
            tip_angles.append(math.degrees(math.acos(min(1.0, cosang))))
            edge_dirs.append([float(v) for v in d0] + [float(v) for v in d1])
        sel_tip = (np.abs(rel_a) < 9.0) & (rrad > 0.93 * r_t)
        if sel_tip.sum() >= 6:
            _, rr = fit_circle(rect[sel_tip])
            tip_radii.append(float(rr))

    # blade half-width profile in the rectified plane: for each tip direction,
    # rotate boundary points into the blade frame (x along the tip) and take the
    # max |y| per x-bin. Ratios of the tip radius. Convexity = how far the edge
    # bulges outside the straight chord from tip to root.
    profiles = []
    for a_tip, r_t in tips:
        ca, sa = math.cos(math.radians(a_tip)), math.sin(math.radians(a_tip))
        bx = rect[:, 0] * ca + (-rect[:, 1]) * sa  # image y is down -> flip
        by = -rect[:, 0] * sa + (-rect[:, 1]) * ca
        prof_w = {}
        for frac in np.arange(0.50, 1.001, 0.05):
            sel = np.abs(bx / r_t - frac) < 0.025
            if sel.sum() >= 2:
                prof_w[f"{frac:.2f}"] = float(np.max(np.abs(by[sel])) / r_t)
        profiles.append(prof_w)
    mean_profile = {}
    for key in sorted({k for pr in profiles for k in pr}):
        vals = [pr[key] for pr in profiles if key in pr]
        mean_profile[key] = {"mean": float(np.mean(vals)), "min": float(np.min(vals)), "max": float(np.max(vals)), "n": len(vals)}

    # table/crown boundary: intensity variance around the cap centre vs radius (rectified sampling)
    gray_img = gray
    table_ratio = None
    prof_var = []
    inv_scale = axes / axes.max()
    for frac in np.linspace(0.40, 0.98, 59):
        vals = []
        for th in np.linspace(0, 2 * math.pi, 144, endpoint=False):
            # point on the rectified circle -> back to image: inverse of rectify
            px, py = frac * r_cap * math.cos(th), frac * r_cap * math.sin(th)
            c, s = math.cos(-angle), math.sin(-angle)
            qx, qy = c * px - s * py, s * px + c * py
            qx, qy = qx * inv_scale[0], qy * inv_scale[1]
            c2, s2 = math.cos(angle), math.sin(angle)
            ix, iy = c2 * qx - s2 * qy + centre[0], s2 * qx + c2 * qy + centre[1]
            if 0 <= int(iy) < gray_img.shape[0] and 0 <= int(ix) < gray_img.shape[1]:
                vals.append(gray_img[int(iy), int(ix)])
        prof_var.append((float(frac), float(np.var(vals)) if vals else 0.0))
    # the crown ring has alternating bright/dark triangles -> variance jumps; take first frac where var > 3x the inner median
    inner = [v for f_, v in prof_var if 0.45 <= f_ < 0.62]
    base = float(np.median(inner)) if inner else 0.0
    for f_, v in prof_var:
        if f_ > 0.62 and v > max(2.5 * base, 60.0):
            table_ratio = f_
            break

    # overlay
    over = crop.copy()
    d = ImageDraw.Draw(over)
    ex, ey = centre
    d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(255, 230, 0))
    # ellipse (cap) drawn via parametric points
    pts_e = []
    for th in np.linspace(0, 2 * math.pi, 200):
        px, py = axes[0] * math.cos(th), axes[1] * math.sin(th)
        c2, s2 = math.cos(angle), math.sin(angle)
        pts_e.append((c2 * px - s2 * py + ex, s2 * px + c2 * py + ey))
    d.line(pts_e + [pts_e[0]], fill=(90, 220, 255), width=2)
    for p in notch_all:
        d.point((p[0], p[1]), fill=(255, 90, 90))
    for a_tip, r_t in tips:
        # back-project tip
        px, py = r_t * math.cos(math.radians(a_tip)), -r_t * math.sin(math.radians(a_tip))
        c, s = math.cos(-angle), math.sin(-angle)
        qx, qy = c * px - s * py, s * px + c * py
        qx, qy = qx * inv_scale[0], qy * inv_scale[1]
        c2, s2 = math.cos(angle), math.sin(angle)
        ix, iy = c2 * qx - s2 * qy + ex, s2 * qx + c2 * qy + ey
        d.ellipse([ix - 5, iy - 5, ix + 5, iy + 5], outline=(255, 160, 40), width=2)
    if table_ratio:
        pts_t = []
        for th in np.linspace(0, 2 * math.pi, 200):
            px, py = table_ratio * axes[0] * math.cos(th), table_ratio * axes[1] * math.sin(th)
            c2, s2 = math.cos(angle), math.sin(angle)
            pts_t.append((c2 * px - s2 * py + ex, s2 * px + c2 * py + ey))
        d.line(pts_t + [pts_t[0]], fill=(120, 245, 160), width=2)
    label = font(18)
    d.text((8, 8), f"#{index:03d} t={(index - 1) / FPS:.1f}s  cap ellipse {axes[0]:.0f}x{axes[1]:.0f}px tilt~{tilt_deg:.0f}deg", fill=(255, 255, 255), font=label)
    d.text((8, 30), f"cap/tip={r_cap / r_tip:.3f}  table/cap={table_ratio if table_ratio else float('nan'):.2f}  tip angle {np.mean(tip_angles) if tip_angles else float('nan'):.0f}deg", fill=(255, 255, 255), font=label)
    over_path = OUT / f"measure-overlay-f{index:04d}.png"
    over.save(over_path)

    # rectified silhouette plot (normalised to cap radius = 1)
    canvas = Image.new("RGB", (900, 900), (12, 12, 14))
    dc = ImageDraw.Draw(canvas)
    sc = 380.0 / r_tip
    for p in rect:
        dc.point((450 + p[0] * sc, 450 + p[1] * sc), fill=(230, 230, 230))
    dc.ellipse([450 - r_cap * sc, 450 - r_cap * sc, 450 + r_cap * sc, 450 + r_cap * sc], outline=(90, 220, 255), width=2)
    if table_ratio:
        rt = table_ratio * r_cap * sc
        dc.ellipse([450 - rt, 450 - rt, 450 + rt, 450 + rt], outline=(120, 245, 160), width=1)
    dc.ellipse([450 - r_tip * sc, 450 - r_tip * sc, 450 + r_tip * sc, 450 + r_tip * sc], outline=(255, 160, 40), width=1)
    dc.text((10, 10), f"#{index:03d} rectified silhouette (cap ellipse -> circle). cap/tip {r_cap / r_tip:.3f}", fill=(255, 255, 255), font=label)
    dc.text((10, 32), f"exposed cap arc per notch: {[round(e, 1) for e in exposed]} deg  tip angle {[round(t, 1) for t in tip_angles]} deg  tip fillet/cap {[round(t / r_cap, 3) for t in tip_radii]}", fill=(255, 255, 255), font=font(15))
    rect_path = OUT / f"measure-rectified-f{index:04d}.png"
    canvas.save(rect_path)

    return {
        "frame": index, "timestampS": round((index - 1) / FPS, 2), "crop": list(CROP), "otsuThreshold": int(best_t), "usedThreshold": float(thr),
        "capEllipsePx": {"centre": [float(ex), float(ey)], "axes": [float(axes[0]), float(axes[1])], "angleDeg": math.degrees(angle), "tiltDeg": tilt_deg},
        "capRadiusPx": r_cap, "tipRadiusPx": r_tip, "capToTipRatio": r_cap / r_tip,
        "tipPolarDeg": [t[0] for t in tips], "tipSpacingDeg": tip_spacing,
        "exposedCapArcPerNotchDeg": exposed,
        "tipIncludedAngleDeg": tip_angles, "tipFilletToCap": [t / r_cap for t in tip_radii], "tipFilletToTip": [t / r_tip for t in tip_radii],
        "tableToCap": table_ratio, "varianceProfile": prof_var[::6],
        "bladeHalfWidthProfile": mean_profile, "bladeHalfWidthPerTip": profiles,
        "overlay": str(over_path.relative_to(REPO)), "rectified": str(rect_path.relative_to(REPO)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = [analyse_frame(i) for i in TABLE_FRAMES]
    ok = [r for r in results if "error" not in r]
    summary = {}
    if ok:
        def agg(key, sub=None):
            vals = []
            for r in ok:
                v = r[key]
                if isinstance(v, list):
                    vals.extend(v)
                elif v is not None:
                    vals.append(v)
            return {"mean": float(np.mean(vals)), "std": float(np.std(vals)), "n": len(vals)} if vals else None
        width_keys = sorted({k for r in ok for k in r["bladeHalfWidthProfile"]})
        width_profile = {k: float(np.mean([r["bladeHalfWidthProfile"][k]["mean"] for r in ok if k in r["bladeHalfWidthProfile"]])) for k in width_keys}
        summary = {
            "bladeHalfWidthProfileOfTipRadius": width_profile,
            "capToTipRatio": agg("capToTipRatio"), "tableToCap": agg("tableToCap"),
            "exposedCapArcPerNotchDeg": agg("exposedCapArcPerNotchDeg"), "tipIncludedAngleDeg": agg("tipIncludedAngleDeg"),
            "tipFilletToTip": agg("tipFilletToTip"), "tiltDeg": {"values": [r["capEllipsePx"]["tiltDeg"] for r in ok]},
        }
    payload = {"source": "Gate 01 video frames10 (ffmpeg fps=10)", "frames": results, "summary": summary,
               "units": "pixels and ratios only; no millimetres", "method": __doc__}
    (OUT / "frame-measurements.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    for r in results:
        if "error" in r:
            print("frame", r["frame"], r["error"])


if __name__ == "__main__":
    main()
