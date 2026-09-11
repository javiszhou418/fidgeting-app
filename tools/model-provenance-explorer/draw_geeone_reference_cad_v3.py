"""Reference CAD v3: blade planform taken directly from the measured half-width
profile (convex edges, radial notch sides, shoulder at r≈0.64 R, tip corner
≈0.085 R) plus the blade-face interior (plateau, scale bands, milled pocket
with flat floor / rounded corners / chamfered rim, tip ridge).

Reads surface-detail-spec.json (planformProfile, D01-D10). Ratios of R;
millimetres only as the 85 mm user-authorized-provisional label.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_unified_tri_spinner_cad import ALT, CENTER, DIM, FONT, HIDDEN, INK, angle_dim, centerlines, circle, dim, leader, poly, setup  # noqa: E402

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
A02 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006"
SPEC = json.loads((A02 / "surface-detail-spec.json").read_text(encoding="utf-8"))
D = {d["id"]: d for d in SPEC["details"]}
PF = SPEC["planformProfile"]
S = 42.5  # 1 R = 42.5 provisional mm (85 mm width label)
CAP = PF["rootAtCap"]["capRadiusToR"]
TABLE = D["UTS-D01"]["params"]["tableToCap"]
ROOT_POLAR = math.radians(PF["rootAtCap"]["edgeMeetsCapAtPolarDeg"])
SHOULDER_R = PF["shoulder"]["radiusToR"]
TIP_R = PF["tipCornerRadiusToR"]
BEVEL_W = D["UTS-D05"]["params"]["bandWidthToR"]
FACETS = D["UTS-D05"]["params"]["facetsPerEdge"]
N_WEDGE = D["UTS-D02"]["params"]["wedges"]
N_SKIRT = D["UTS-D03"]["params"]["facets"]
PK = D["UTS-D08"]["params"]
BODY_T = 0.17
WALL_H = D["UTS-D06"]["params"]["wallToThickness"]
CAP_SIDE_H = D["UTS-D03"]["params"]["sideHeightToR"]


def sc(x, y):
    return (S * x, S * y)


def rot(pts, deg):
    a = math.radians(deg)
    return [(S * (x * math.cos(a) - y * math.sin(a)), S * (x * math.sin(a) + y * math.cos(a))) for x, y in pts]


def half_width(x: float) -> float:
    """Measured half-width profile (x/R -> y/R), smooth interpolation, tip pinned to 0."""
    xs = np.array([float(k) for k in PF["halfWidth"]] + [1.0 + TIP_R * 0.0001])
    ys = np.array([PF["halfWidth"][k] for k in PF["halfWidth"]] + [0.0])
    ys[-2] = min(ys[-2], 0.031)
    return float(np.interp(x, xs, ys))


def planform_half() -> list[tuple[float, float]]:
    """Upper half outline root -> tip: radial notch side from the cap to the
    shoulder, then the measured convex edge, then a rounded tip."""
    root = (CAP * math.cos(ROOT_POLAR), CAP * math.sin(ROOT_POLAR))
    shoulder = (SHOULDER_R * math.cos(ROOT_POLAR), SHOULDER_R * math.sin(ROOT_POLAR))
    pts = [root, shoulder]
    # convex edge sampled from the profile, from the shoulder x to the tip fillet start
    x0 = shoulder[0]
    x_fillet = 1.0 - TIP_R * (1 - math.cos(math.radians(50)))
    for x in np.linspace(x0 + 0.02, 0.93, 22):
        pts.append((float(x), half_width(float(x))))
    # rounded tip: circle centre (1-TIP_R, 0), from the tangent angle down to 0
    a0 = math.radians(52.0)
    for k in range(9):
        a = a0 * (1 - k / 8)
        pts.append((1.0 - TIP_R + TIP_R * math.cos(a), TIP_R * math.sin(a)))
    return pts


def offset_inward(half: list[tuple[float, float]], w: float) -> list[tuple[float, float]]:
    """Plateau boundary: outline offset inward by w along local normals (upper half only)."""
    out = []
    n = len(half)
    for i in range(1, n - 1):
        (x0, y0), (x1, y1), (x2, y2) = half[i - 1], half[i], half[i + 1]
        tx, ty = x2 - x0, y2 - y0
        L = math.hypot(tx, ty) or 1.0
        nx, ny = ty / L, -tx / L  # right-hand normal points outward for a CCW upper edge -> flip
        if nx * x1 + ny * y1 < 0:
            nx, ny = -nx, -ny
        out.append((x1 - w * nx, y1 - w * ny))
    return out


def plan(ax):
    setup(ax, "REFERENCE PLAN v3  顶视 — 叶片平面形来自实测半宽曲线；叶面内部细节（平台、鳞面带、凹坑、脊）", (-1.5 * S, 1.5 * S), (-1.42 * S, 1.36 * S))
    centerlines(ax, 1.2 * S)
    circle(ax, S, lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))
    half = planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    plateau_u = offset_inward(half[1:], BEVEL_W)  # skip the root point (edge under the cap)
    for ang in (90, 210, 330):
        poly(ax, rot(full, ang), lw=1.3, close=False)  # outline
        # plateau boundary (D04) both sides
        for s_ in (1, -1):
            poly(ax, rot([(x, s_ * y) for x, y in plateau_u], ang), lw=0.7, color=HIDDEN, close=False)
        # scale-band facet boundaries (D05): FACETS per side between shoulder and tip start
        edge_pts = [p for p in half[2:-9]]
        idxs = np.linspace(0, len(edge_pts) - 1, FACETS + 1).astype(int)
        for k, i in enumerate(idxs):
            ex, ey = edge_pts[i]
            # nearest plateau point
            j = min(range(len(plateau_u)), key=lambda jj: (plateau_u[jj][0] - ex) ** 2 + (plateau_u[jj][1] - ey) ** 2)
            px, py = plateau_u[j]
            skew = 0.010 * (1 if k % 2 == 0 else -1)
            for s_ in (1, -1):
                poly(ax, rot([(ex, s_ * ey), (px + skew, s_ * (py))], ang), lw=0.5, color=INK, close=False)
        # tip ridge (D07): from plateau corner to tip
        corner_x = plateau_u[-1][0]
        poly(ax, rot([(corner_x, 0.0), (1.0 - TIP_R * 0.35, 0.0)], ang), lw=0.6, color=HIDDEN, close=False)
        # pocket (D08): rounded triangle open toward the cap, plus chamfer rim
        bx = CAP * math.cos(math.asin(PK["baseHalfWidthToR"] / CAP))
        pocket = [(PK["apexRadiusToR"], 0.0), (bx, PK["baseHalfWidthToR"]), (bx, -PK["baseHalfWidthToR"])]
        rc = PK["cornerRadiusToR"]
        def rounded(tri, r):
            out = []
            n = len(tri)
            for i in range(n):
                p0, p1, p2 = tri[i - 1], tri[i], tri[(i + 1) % n]
                for q in (p0, p2):
                    dx, dy = q[0] - p1[0], q[1] - p1[1]
                    L = math.hypot(dx, dy)
                    out.append((p1[0] + dx / L * r * 2.2, p1[1] + dy / L * r * 2.2))
            # order: for each vertex two points (toward prev, toward next); reorder to go around
            seq = []
            for i in range(n):
                seq.append(out[2 * i + 1])  # toward next
                seq.append(out[2 * ((i + 1) % n)])  # next vertex toward prev
            return seq
        pr = rounded(pocket, rc)
        ax.add_patch(Polygon(rot(pr, ang), closed=True, fill=True, fc="#e3e3e3", ec=INK, lw=0.9, zorder=2))
        inner = [(x * 0.965 + 0.02 * (1 if i == 0 else 0), y * 0.82) for i, (x, y) in enumerate(pr)]
        ax.add_patch(Polygon(rot(inner, ang), closed=True, fill=True, fc="#a8a8a8", ec=INK, lw=0.5, hatch="....", zorder=3))
        # notch side bevels: short ticks along the radial sides (D05 continues)
        for s_ in (1, -1):
            for f in (0.35, 0.7):
                r_ = CAP + (SHOULDER_R - CAP) * f
                p_out = (r_ * math.cos(ROOT_POLAR), s_ * r_ * math.sin(ROOT_POLAR))
                p_in = ((r_) * math.cos(ROOT_POLAR) + BEVEL_W * 0.8 * math.sin(ROOT_POLAR), s_ * (r_ * math.sin(ROOT_POLAR) - BEVEL_W * 0.8 * math.cos(ROOT_POLAR)))
                poly(ax, rot([p_out, p_in], ang), lw=0.5, color=INK, close=False)
    # cap: skirt polygon, crown zigzag, table
    skirt = [(CAP * math.cos(2 * math.pi * (j + 0.5) / N_SKIRT), CAP * math.sin(2 * math.pi * (j + 0.5) / N_SKIRT)) for j in range(N_SKIRT)]
    poly(ax, [sc(*p) for p in skirt], lw=1.3)
    for j in range(N_WEDGE):
        a_in = 2 * math.pi * j / N_WEDGE
        a_out = 2 * math.pi * (j + 0.5) / N_WEDGE
        i0 = sc(CAP * TABLE * math.cos(a_in), CAP * TABLE * math.sin(a_in))
        i1 = sc(CAP * TABLE * math.cos(a_in + 2 * math.pi / N_WEDGE), CAP * TABLE * math.sin(a_in + 2 * math.pi / N_WEDGE))
        o = sc(CAP * math.cos(a_out), CAP * math.sin(a_out))
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=0.45)
    circle(ax, CAP * TABLE * S, lw=0.9)
    # dimensions / callouts
    dim(ax, (-S, -1.27 * S), (S, -1.27 * S), 0.0, "2R = 85 mm  user-authorized-provisional（非 measured；仅供未来 Gate 03–05）", ext=False)
    for xx in (-S, S):
        ax.plot([xx, xx], [-1.27 * S, -0.3 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    sh = rot([(SHOULDER_R * math.cos(ROOT_POLAR), SHOULDER_R * math.sin(ROOT_POLAR))], 90)[0]
    sh2 = rot([(SHOULDER_R * math.cos(ROOT_POLAR), -SHOULDER_R * math.sin(ROOT_POLAR))], 90)[0]
    dim(ax, sh2, sh, 0.16 * S, f"最宽 ≈{2 * PF['shoulder']['halfWidthToR']:.2f} R（≈{2 * PF['shoulder']['halfWidthToR'] / (2 * CAP):.2f}×盖径）r≈{SHOULDER_R:.2f} R")
    leader(ax, rot([(0.75, half_width(0.75))], 330)[0], "边缘为凸弧（实测半宽曲线，非直线）", sc(0.60, -0.70))
    leader(ax, rot([(1.0, 0.0)], 330)[0], f"D07 叶尖圆角 ≈{TIP_R:.3f} R（≈{TIP_R * S:.1f} mm）", sc(0.60, -1.12))
    root = rot([(CAP * math.cos(ROOT_POLAR), CAP * math.sin(ROOT_POLAR))], 90)[0]
    leader(ax, root, f"叶根接盖于极角 ±{PF['rootAtCap']['edgeMeetsCapAtPolarDeg']}°；缺口两侧为径向直边，露盖弧 ≈{PF['rootAtCap']['exposedCapArcPerNotchDeg']}°", sc(-1.47, 1.26))
    leader(ax, rot([(PK['apexRadiusToR'] - 0.03, 0.0)], 210)[0], f"D08 铣削三角凹坑：平底、圆角 ≈{PK['cornerRadiusToR']:.3f} R、边沿倒角；尖端 r≈{PK['apexRadiusToR']:.2f} R，底边半宽 ≈{PK['baseHalfWidthToR']:.3f} R；深度未知", sc(-1.47, -1.05))
    leader(ax, rot([(0.60, half_width(0.60) - BEVEL_W * 0.5)], 330)[0], f"D05 鳞面带 ≈{BEVEL_W:.2f} R，每边 {FACETS}±1 平面", sc(0.60, -0.90))
    leader(ax, rot([(0.72, 0.02)], 330)[0], "D04 平台（平面）", sc(0.95, -0.45))
    leader(ax, sc(CAP * math.cos(math.radians(195)), CAP * math.sin(math.radians(195))), f"D03 盖裙 {N_SKIRT}±4 面 · D02 冠环 {N_WEDGE}±2 楔 · D01 平盘 0.80×盖", sc(-1.47, 0.40))
    leader(ax, sc(CAP * 1.02 * math.cos(math.radians(30)), CAP * 1.02 * math.sin(math.radians(30))), "D09 缺口：盖冠环+裙外露，暗缝宽未知", sc(0.60, 1.20))
    ax.text(-1.47 * S, -1.38 * S, "细线 = 平台边界 / 鳞面分界 / 叶尖脊；灰 = 凹坑（点状 = 平底）；半宽曲线见右下表。", fontsize=6.5, color=HIDDEN)


def section_aa(ax):
    setup(ax, "SECTION A—A v3  过叶片轴（右叶片，左缺口）", (-1.25 * S, 1.3 * S), (-0.44 * S, 0.48 * S))
    ax.plot([-1.25 * S, 1.3 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    corner_x = 1.0 - TIP_R - BEVEL_W * 1.2
    body = [sc(CAP, t / 2), sc(corner_x, t / 2), sc(1.0 - TIP_R * 0.3, wall / 2), sc(1.0, wall / 2 * 0.7), sc(1.0, -wall / 2 * 0.7), sc(1.0 - TIP_R * 0.3, -wall / 2), sc(corner_x, -t / 2), sc(CAP, -t / 2)]
    poly(ax, body, lw=1.2, hatch="////")
    pd = 0.35 * t
    for sgn in (1, -1):
        rec = [sc(CAP, sgn * t / 2), sc(CAP, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"] - 0.03, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"], sgn * t / 2)]
        ax.add_patch(Polygon(rec, closed=True, fill=True, fc="white", ec=ALT, lw=0.9, ls=(0, (4, 2)), zorder=4))
    poly(ax, [sc(-CAP, t / 2 * 0.55), sc(-CAP * 1.05, t / 2 * 0.55), sc(-CAP * 1.05, -t / 2 * 0.55), sc(-CAP, -t / 2 * 0.55)], lw=1.0, hatch="////")
    for sgn in (1, -1):
        top = t / 2 + CAP_SIDE_H
        crown_h = 0.55 * CAP_SIDE_H
        cap_pts = [sc(-CAP * TABLE, sgn * top), sc(CAP * TABLE, sgn * top), sc(CAP, sgn * (top - crown_h)), sc(CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (top - crown_h))]
        poly(ax, cap_pts, lw=1.2, hatch="\\\\\\\\")
    dim(ax, sc(corner_x - 0.05, -t / 2), sc(corner_x - 0.05, t / 2), -0.62 * S, f"厚 ≈{BODY_T:.2f} R")
    dim(ax, sc(CAP * 0.5, t / 2), sc(CAP * 0.5, t / 2 + CAP_SIDE_H), -0.95 * S, f"D03 盖侧 ≈{CAP_SIDE_H:.2f} R")
    leader(ax, sc(PK["apexRadiusToR"] - 0.02, t / 2 - pd), "D08 平底凹坑，深度未知（虚线占位）", sc(-1.22, -0.40), color=ALT)
    leader(ax, sc((corner_x + 1.0) / 2, t / 2 - 0.02), "D07 脊 + 圆角叶尖", sc(-1.22, 0.42))


def section_cc(ax):
    setup(ax, f"SECTION C—C v3  过凹坑横剖（x≈0.58 R）", (-0.55 * S, 0.55 * S), (-0.22 * S, 0.26 * S))
    ax.plot([-0.55 * S, 0.55 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    hw = half_width(0.58)
    pw = hw - BEVEL_W
    pk_hw = PK["baseHalfWidthToR"] * 0.85
    pd = 0.35 * t
    outer = [sc(-hw, -wall / 2), sc(hw, -wall / 2), sc(hw, wall / 2), sc(pw, t / 2), sc(pk_hw, t / 2), sc(pk_hw - 0.01, t / 2 - pd), sc(-pk_hw + 0.01, t / 2 - pd), sc(-pk_hw, t / 2), sc(-pw, t / 2), sc(-hw, wall / 2)]
    bottom = [sc(-pw, -t / 2), sc(-pk_hw, -t / 2), sc(-pk_hw + 0.01, -t / 2 + pd), sc(pk_hw - 0.01, -t / 2 + pd), sc(pk_hw, -t / 2), sc(pw, -t / 2)]
    poly(ax, outer[1:] + [sc(-hw, -wall / 2)] + bottom, lw=1.2, hatch="////")
    dim(ax, sc(-hw, -wall / 2), sc(hw, -wall / 2), -0.05 * S, f"宽 ≈{2 * hw:.2f} R")
    dim(ax, sc(-pk_hw, t / 2), sc(pk_hw, t / 2), 0.045 * S, f"D08 坑宽 ≈{2 * pk_hw:.2f} R")
    dim(ax, sc(hw, -wall / 2), sc(hw, wall / 2), -0.05 * S, f"D06 ≈{WALL_H:.2f}×厚")
    leader(ax, sc((pw + hw) / 2, (t / 2 + wall / 2) / 2), "D05 鳞面带", sc(0.30, 0.24))
    leader(ax, sc(0.0, t / 2 - pd), "凹坑平底（深度未知，占位 35%）", sc(-0.52, -0.20), color=ALT)


def profile_table(ax):
    setup(ax, "实测半宽曲线（f0077/f0078 校正剪影，3 叶平均）", (0, 10), (0, 10))
    rows = [("x/R", "半宽/R", "全宽/R")] + [(k, f"{v:.3f}", f"{2 * v:.3f}") for k, v in PF["halfWidth"].items()]
    for i, (a, b, c) in enumerate(rows):
        y = 9.4 - i * 0.72
        ax.text(0.4, y, a, fontsize=7.5, color=INK if i else DIM, family=FONT)
        ax.text(3.6, y, b, fontsize=7.5, color=INK if i else DIM, family=FONT)
        ax.text(6.6, y, c, fontsize=7.5, color=INK if i else DIM, family=FONT)
    ax.text(0.4, 0.5, f"叶根接盖 ±{PF['rootAtCap']['edgeMeetsCapAtPolarDeg']}° · 肩 r≈{SHOULDER_R} · 叶尖圆角 {TIP_R} R · ±0.02 R", fontsize=7, color=ALT, family=FONT)


def main() -> None:
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.10, 0.54, 0.86])
    ax_aa = fig.add_axes([0.57, 0.60, 0.42, 0.36])
    ax_cc = fig.add_axes([0.57, 0.33, 0.42, 0.25])
    ax_tb = fig.add_axes([0.57, 0.09, 0.42, 0.22])
    plan(ax_plan)
    section_aa(ax_aa)
    section_cc(ax_cc)
    profile_table(ax_tb)
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD v3 (measured planform + blade-face interior) · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, "UNITS: R 比例；mm 仅 85 mm user-authorized-provisional · 平面形来自实测半宽曲线（凸弧边、径向缺口边、肩 0.64 R、叶尖圆角 0.085 R）· 凹坑深度/缝宽未知 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE surface-detail-spec.json (planformProfile) ← frame-measurements.json → draw_geeone_reference_cad_v3.py · {date.today().isoformat()} · v1/v2 保留为历史", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video-v3.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video-v3.png")


if __name__ == "__main__":
    main()
