#!/usr/bin/env python3
"""Gate 02 evidence: project the current reference-CAD planform (v7; and the superseded
v6 outline, dashed) back onto the original GEEONE table frames through the
inverse of the cap-ellipse rectification used by measure_geeone_video_frames.py.
Lets the user check the outline against the photo without any mental un-tilting.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_geeone_video_frames as M  # noqa: E402
import draw_geeone_reference_cad_v7 as V6  # noqa: E402  (current = v7; V6.v6_half() = previous)

A02 = M.OUT
MEAS = json.loads((A02 / "frame-measurements.json").read_text(encoding="utf-8"))
OUT = A02 / "frame-zooms" / "planform-v7-on-frames.png"


def unrectify(pts_r: np.ndarray, centre, axes, angle) -> np.ndarray:
    """Inverse of M.rectify: rectified px (origin at cap centre) -> original crop px."""
    c, s = math.cos(-angle), math.sin(-angle)
    q = np.stack([c * pts_r[:, 0] - s * pts_r[:, 1], s * pts_r[:, 0] + c * pts_r[:, 1]], axis=1)
    q = q / (axes.max() / axes)
    c2, s2 = math.cos(angle), math.sin(angle)
    return np.stack([c2 * q[:, 0] - s2 * q[:, 1], s2 * q[:, 0] + c2 * q[:, 1]], axis=1) + centre


def outline(half, rot_deg):
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    a = math.radians(rot_deg)
    return [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in full]


def main() -> None:
    font = M.font(22)
    frames = [f for f in MEAS["frames"] if "error" not in f]
    tiles = []
    for fr in frames:
        idx = fr["frame"]
        ell = fr["capEllipsePx"]
        centre = np.array(ell["centre"])
        axes = np.array(ell["axes"])
        angle = math.radians(ell["angleDeg"])
        r_tip = fr["tipRadiusPx"]
        img = Image.open(M.FRAMES / f"f_{idx:04d}.jpg").convert("RGB").crop(M.CROP)
        zoom = 2
        img = img.resize((img.width * zoom, img.height * zoom), Image.LANCZOS)
        d = ImageDraw.Draw(img)

        def draw_model(pts_model, color, width, dash=False):
            p = np.array(pts_model) * r_tip
            p = np.stack([p[:, 0], -p[:, 1]], axis=1)  # model y up -> rectified y down
            q = unrectify(p, centre, axes, angle) * zoom
            seq = [tuple(v) for v in q]
            if dash:
                for i in range(0, len(seq) - 1, 2):
                    d.line([seq[i], seq[i + 1]], fill=color, width=width)
            else:
                d.line(seq, fill=color, width=width)  # open: the blade continues under the cap

        for tip_deg in fr["tipPolarDeg"]:
            draw_model(outline(V6.planform_half(), tip_deg), (124, 252, 0), 3)
            draw_model(outline(V6.v6_half(), tip_deg), (255, 93, 93), 2, dash=True)
        th = np.linspace(0, 2 * math.pi, 181)
        cap = fr["capRadiusPx"] / r_tip
        draw_model([(cap * math.cos(t), cap * math.sin(t)) for t in th] + [(cap, 0.0)], (56, 182, 255), 2)
        draw_model([(cap * V6.TABLE * math.cos(t), cap * V6.TABLE * math.sin(t)) for t in th] + [(cap * V6.TABLE, 0.0)], (56, 182, 255), 1)
        d.text((10, 10), f"#{idx:03d} t={fr['timestampS']:.1f}s  green = CAD v7 (arcs end on the cap, gap per notch), red dashed = v6 (arcs meeting in a V), blue = cap / disc", fill=(255, 230, 60), font=font)
        tiles.append(img)
        # notch zoom: around the bisector between the first two tips
        t0, t1 = fr["tipPolarDeg"][0], fr["tipPolarDeg"][1]
        bis = math.radians((t0 + t1) / 2 + (180 if abs(t1 - t0) > 180 else 0))
        pr = np.array([[0.55 * r_tip * math.cos(bis), -0.55 * r_tip * math.sin(bis)]])
        c = unrectify(pr, centre, axes, angle)[0] * zoom
        box = (int(c[0] - 180), int(c[1] - 180), int(c[0] + 180), int(c[1] + 180))
        nz = img.crop(box).resize((720, 720), Image.LANCZOS)
        ImageDraw.Draw(nz).text((8, 8), f"#{idx:03d} notch 4x", fill=(255, 230, 60), font=font)
        tiles.append(nz)
    w = sum(t.width for t in tiles[:2]) + 20
    h = max(t.height for t in tiles) * 1
    rows = len(tiles) // 2
    sheet = Image.new("RGB", (w, rows * (max(t.height for t in tiles[::2]) + 10)), (12, 12, 14))
    y = 0
    for i in range(0, len(tiles), 2):
        sheet.paste(tiles[i], (0, y))
        sheet.paste(tiles[i + 1], (tiles[i].width + 20, y))
        y += tiles[i].height + 10
    sheet.save(OUT)
    print("OVERLAY", OUT)


if __name__ == "__main__":
    main()
