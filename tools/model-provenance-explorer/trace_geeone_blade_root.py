#!/usr/bin/env python3
"""Gate 02 evidence: per-blade outline traces of the GEEONE tri-spinner in the
blade frame (axis = +x, units of the tip-circle radius R), for the flat table
frames. Overlays the current reference-CAD planform so the root / notch shape
can be compared point by point instead of by eye on a tilted photo.

Reads the ellipse + tip data written by measure_geeone_video_frames.py
(frame-measurements.json), re-extracts the silhouette boundary, rectifies it
with the same cap-ellipse -> circle map, and plots each blade separately.
Ratios only; no millimetres.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_geeone_video_frames as M  # noqa: E402

A02 = M.OUT
MEAS = json.loads((A02 / "frame-measurements.json").read_text(encoding="utf-8"))
OUT = A02 / "frame-zooms" / "blade-root-traces.png"


def frame_boundary(index: int, thr: float) -> np.ndarray:
    frame = Image.open(M.FRAMES / f"f_{index:04d}.jpg").convert("RGB").crop(M.CROP)
    gray = np.asarray(frame.convert("L"), dtype=float)
    mask = M.fill_holes(M.largest_component(gray > thr))
    return M.boundary_points(mask)


def load_planform(version: str):
    import draw_geeone_reference_cad_v7 as cur

    half = cur.planform_half() if version == "v7" else cur.v6_half()
    lower = [(x, -y) for x, y in reversed(half)]
    return half + lower


def main() -> None:
    frames = [f for f in MEAS["frames"] if "error" not in f]
    planforms = {}
    for v in ("v6", "v7"):
        planforms[v] = load_planform(v)
    fig, axes = plt.subplots(len(frames), 3, figsize=(15, 5 * len(frames)), facecolor="#101012")
    for row, fr in enumerate(frames):
        idx = fr["frame"]
        ell = fr["capEllipsePx"]
        centre = np.array(ell["centre"])
        ax_len = np.array(ell["axes"])
        ang = math.radians(ell["angleDeg"])
        bpts = frame_boundary(idx, fr["usedThreshold"])
        rect = M.rectify(bpts, centre, ax_len, ang)
        r_tip = fr["tipRadiusPx"]
        cap = fr["capRadiusPx"] / r_tip
        pts = np.stack([rect[:, 0], -rect[:, 1]], axis=1) / r_tip  # y up, units of R
        for col, tip_deg in enumerate(fr["tipPolarDeg"]):
            a = -math.radians(tip_deg)
            c, s = math.cos(a), math.sin(a)
            q = np.stack([c * pts[:, 0] - s * pts[:, 1], s * pts[:, 0] + c * pts[:, 1]], axis=1)
            ax = axes[row][col]
            ax.set_facecolor("#101012")
            sel = (q[:, 0] > 0.15) & (np.abs(q[:, 1]) < 0.75)
            ax.scatter(q[sel, 0], q[sel, 1], s=2, c="#f2f2f2", label="frame silhouette")
            th = np.linspace(0, 2 * math.pi, 361)
            ax.plot(cap * np.cos(th), cap * np.sin(th), color="#38b6ff", lw=1.0, label=f"cap circle {cap:.3f} R")
            ax.plot(np.cos(th), np.sin(th), color="#ff8c00", lw=0.6, ls="--")
            for sgn in (1, -1):
                ax.plot([0, 1.2 * math.cos(math.radians(60))], [0, sgn * 1.2 * math.sin(math.radians(60))],
                        color="#666", lw=0.6, ls=":")
            colors = {"v6": "#ff5d5d", "v7": "#7CFC00"}
            for v, pf in planforms.items():
                xs = [p[0] for p in pf] + [pf[0][0]]
                ys = [p[1] for p in pf] + [pf[0][1]]
                ax.plot(xs, ys, color=colors[v], lw=1.2, label=f"CAD {v} planform")
                for rot_deg in (120, -120):
                    ra = math.radians(rot_deg)
                    xr = [x * math.cos(ra) - y * math.sin(ra) for x, y in pf]
                    yr = [x * math.sin(ra) + y * math.cos(ra) for x, y in pf]
                    ax.plot(xr + [xr[0]], yr + [yr[0]], color=colors[v], lw=0.7, alpha=0.5)
            ax.set_xlim(0.15, 1.1)
            ax.set_ylim(-0.75, 0.75)
            ax.set_aspect("equal")
            ax.grid(True, color="#333", lw=0.4)
            ax.tick_params(colors="#bbb", labelsize=7)
            for sp in ax.spines.values():
                sp.set_color("#555")
            ax.set_title(f"#{idx:03d} t={fr['timestampS']:.1f}s  blade @ {tip_deg:.0f}°  (blade frame, units of R)",
                         color="#eee", fontsize=9)
            if row == 0 and col == 0:
                ax.legend(loc="lower left", fontsize=7, facecolor="#1a1a1e", labelcolor="#eee", edgecolor="#444")
    fig.suptitle("GEEONE table frames — per-blade root traces vs reference CAD planform (rectified, R = tip radius)",
                 color="#eee", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=110, facecolor=fig.get_facecolor())
    print("TRACES", OUT)


if __name__ == "__main__":
    main()
