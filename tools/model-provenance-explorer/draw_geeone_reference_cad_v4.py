"""Reference CAD v4: planform = rounded equilateral triangle (straight sides at
30° to each blade axis, corner arcs of 0.21 R spanning 120° with the apex on
the tip circle) cut by three radial notch sectors (42°) down to the cap. Fitted
to the measured half-width profile within ±0.02 R (x 0.50-0.85). Blade-face
interior as v3 (plateau, scale bands wrapping the arc, milled pocket, ridge).

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
PM = PF["parametric"]
TIP_R = PM["cornerArcRadiusToR"]
XV = PM["virtualVertexRadiusToR"]
SIDE_ANG = math.radians(PM["sideAngleToBladeAxisDeg"])
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
    """Parametric half-width: straight side until the arc tangent point, then the corner arc."""
    t_tan = TIP_R / math.tan(SIDE_ANG)
    x_tan = XV - t_tan * math.cos(SIDE_ANG)
    if x <= x_tan:
        return (XV - x) * math.tan(SIDE_ANG)
    cx = 1.0 - TIP_R
    return math.sqrt(max(0.0, TIP_R ** 2 - (x - cx) ** 2))


def planform_half() -> list[tuple[float, float]]:
    """Upper half outline root -> tip: radial notch side from the cap to the
    shoulder, straight triangle side at 30° to the axis, then the 120° corner arc."""
    root = (CAP * math.cos(ROOT_POLAR), CAP * math.sin(ROOT_POLAR))
    # shoulder = radial line at ROOT_POLAR meets the side line y = (XV - x) tan30
    xs_ = XV * math.tan(SIDE_ANG) / (math.tan(ROOT_POLAR) + math.tan(SIDE_ANG))
    shoulder = (xs_, xs_ * math.tan(ROOT_POLAR))
    t_tan = TIP_R / math.tan(SIDE_ANG)  # vertex -> tangent point along the side
    tangent = (XV - t_tan * math.cos(SIDE_ANG), t_tan * math.sin(SIDE_ANG))
    pts = [root, shoulder]
    for k in range(1, 9):
        f = k / 8
        pts.append((shoulder[0] + (tangent[0] - shoulder[0]) * f, shoulder[1] + (tangent[1] - shoulder[1]) * f))
    cx = 1.0 - TIP_R
    a0 = math.pi / 2 - SIDE_ANG  # 60 deg
    for k in range(1, 13):
        a = a0 * (1 - k / 12)
        pts.append((cx + TIP_R * math.cos(a), TIP_R * math.sin(a)))
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
    setup(ax, "REFERENCE PLAN v4  顶视 — 圆角等边三角 + 三个径向缺口（拟合实测半宽 ±0.02 R）；叶面内部细节", (-1.5 * S, 1.5 * S), (-1.42 * S, 1.36 * S))
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
        edge_pts = [p for p in half[2:-1]]
        idxs = np.linspace(0, len(edge_pts) - 1, FACETS + 2).astype(int)
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
    dim(ax, sh2, sh, 0.16 * S, f"肩宽 ≈{2 * shoulder_hw():.2f} R（≈{2 * shoulder_hw() / (2 * CAP):.2f}×盖径）r≈{SHOULDER_R:.2f} R")
    leader(ax, rot([(0.75, half_width(0.75))], 330)[0], f"直边：与叶轴成 {PM['sideAngleToBladeAxisDeg']:.0f}°，即等边三角的边；相邻两叶的底边共线", sc(0.60, -0.70))
    leader(ax, rot([(1.0, 0.0)], 330)[0], f"D07 叶尖大圆弧 R≈{TIP_R:.2f} R（≈{TIP_R * S:.0f} mm @85），跨 120°，顶点在外接圆上", sc(0.60, -1.12))
    # triangle base line through the two lower tips (collinear bottom edges)
    base_y = -XV * math.sin(SIDE_ANG) * S
    ax.plot([-1.1 * S, 1.1 * S], [base_y, base_y], color=ALT, lw=0.6, ls=(0, (6, 3)))
    ax.text(0.72 * S, base_y - 0.05 * S, f"等边三角底边（距中心 {PM['sideDistanceFromCentreToR']:.3f} R）：两下叶底边近似共线", fontsize=6.5, color=ALT)
    root = rot([(CAP * math.cos(ROOT_POLAR), CAP * math.sin(ROOT_POLAR))], 90)[0]
    leader(ax, root, f"叶根接盖于极角 ±{PF['rootAtCap']['edgeMeetsCapAtPolarDeg']}°；缺口两侧为径向直边，露盖弧 ≈{PF['rootAtCap']['exposedCapArcPerNotchDeg']}°", sc(-1.47, 1.26))
    leader(ax, rot([(PK['apexRadiusToR'] - 0.03, 0.0)], 210)[0], f"D08 铣削三角凹坑：平底、圆角 ≈{PK['cornerRadiusToR']:.3f} R、边沿倒角；尖端 r≈{PK['apexRadiusToR']:.2f} R，底边半宽 ≈{PK['baseHalfWidthToR']:.3f} R；深度未知", sc(-1.47, -1.05))
    leader(ax, rot([(0.60, half_width(0.60) - BEVEL_W * 0.5)], 330)[0], f"D05 鳞面带 ≈{BEVEL_W:.2f} R，每边 {FACETS}±1 平面", sc(0.60, -0.90))
    leader(ax, rot([(0.72, 0.02)], 330)[0], "D04 平台（平面）", sc(0.95, -0.45))
    leader(ax, sc(CAP * math.cos(math.radians(195)), CAP * math.sin(math.radians(195))), f"D03 盖裙 {N_SKIRT}±4 面 · D02 冠环 {N_WEDGE}±2 楔 · D01 平盘 0.80×盖", sc(-1.47, 0.40))
    leader(ax, sc(CAP * 1.02 * math.cos(math.radians(30)), CAP * 1.02 * math.sin(math.radians(30))), "D09 缺口：盖冠环+裙外露，暗缝宽未知", sc(0.60, 1.20))
    ax.text(-1.47 * S, -1.38 * S, "细线 = 平台边界 / 鳞面分界 / 叶尖脊；灰 = 凹坑（点状 = 平底）；半宽曲线见右下表。", fontsize=6.5, color=HIDDEN)


def section_aa(ax):
    setup(ax, "SECTION A—A v4  过叶片轴（右叶片，左缺口）", (-1.25 * S, 1.3 * S), (-0.44 * S, 0.48 * S))
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
    setup(ax, f"SECTION C—C v4  过凹坑横剖（x≈0.58 R）", (-0.55 * S, 0.55 * S), (-0.22 * S, 0.26 * S))
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


def shoulder_hw() -> float:
    xs_ = XV * math.tan(SIDE_ANG) / (math.tan(ROOT_POLAR) + math.tan(SIDE_ANG))
    return xs_ * math.tan(ROOT_POLAR)


def profile_table(ax):
    setup(ax, "实测半宽（f0077/f0078）vs 圆角三角模型", (0, 10), (0, 10))
    rows = [("x/R", "实测", "模型", "差")]
    for k, v in PF["halfWidth"].items():
        m = half_width(float(k))
        rows.append((k, f"{v:.3f}", f"{m:.3f}", f"{m - v:+.3f}"))
    for i, (a, b, c, d) in enumerate(rows):
        y = 9.4 - i * 0.72
        col = INK if i else DIM
        if i and float(a) >= 0.90:
            col = HIDDEN
        ax.text(0.3, y, a, fontsize=7.5, color=col, family=FONT)
        ax.text(2.6, y, b, fontsize=7.5, color=col, family=FONT)
        ax.text(5.0, y, c, fontsize=7.5, color=col, family=FONT)
        ax.text(7.4, y, d, fontsize=7.5, color=col, family=FONT)
    ax.text(0.3, 0.5, f"x≥0.90 实测偏窄：叶尖暗色倒角面低于剪影阈值（灰）。模型：顶点 {XV:.3f} R、边距 {PM['sideDistanceFromCentreToR']:.3f} R、圆弧 {TIP_R:.3f} R", fontsize=6.5, color=ALT, family=FONT)


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
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD v4 (rounded-triangle planform + radial notches + blade-face interior) · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, "UNITS: R 比例；mm 仅 85 mm user-authorized-provisional · 平面形 = 圆角等边三角（边距 0.606 R，圆弧 0.212 R）+ 三个 42° 径向缺口到盖圈 · 凹坑深度/缝宽未知 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE surface-detail-spec.json (planformProfile) ← frame-measurements.json → draw_geeone_reference_cad_v4.py · {date.today().isoformat()} · v1–v3 保留为历史", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video-v4.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video-v4.png")


if __name__ == "__main__":
    main()
