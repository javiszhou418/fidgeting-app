"""Reference CAD v6: blade sides are convex circular arcs (R≈1.37 R, centre on
the blade's perpendicular through the cap centre at 0.92 R). Adjacent arcs meet
on the bisector ≈0.2 mm outside the cap circle, so the notch bottom hugs the cap
and each arc crosses the cap circle at an acute ≈18°. No straight side, no
shoulder. Tip: ≈90° included angle with a 0.03 R fillet. Cap: 14-wedge crown
ring (28 triangles) sloping outward-down from the disc rim (crest), 14-scale
skirt in two rows, turned disc that is a shallow concave thumb dish (user-stated).

Reads surface-detail-spec.json (planformProfile.parametric, D01-D10). Ratios of
R; millimetres only as the 85 mm user-authorized-provisional label.
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
from matplotlib.patches import Arc, Polygon  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_unified_tri_spinner_cad import ALT, CENTER, DIM, FONT, HIDDEN, INK, centerlines, circle, dim, leader, poly, setup  # noqa: E402

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
A02 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006"
SPEC = json.loads((A02 / "surface-detail-spec.json").read_text(encoding="utf-8"))
D = {d["id"]: d for d in SPEC["details"]}
PF = SPEC["planformProfile"]
PM = PF["parametric"]
S = 42.5  # 1 R = 42.5 provisional mm (85 mm width label)
CAP = PF["rootAtCap"]["capRadiusToR"]
TABLE = D["UTS-D01"]["params"]["tableToCap"]
RS = PM["sideArcRadiusToR"]
CY = -PM["sideArcCentreToR"][1]
RT = PM["tipFilletRadiusToR"]
XC = PM["tipFilletCentreToR"][0]
BEVEL_W = D["UTS-D05"]["params"]["bandWidthToR"]
FACETS = D["UTS-D05"]["params"]["facetsPerEdge"]
N_WEDGE = D["UTS-D02"]["params"]["wedges"]
N_SKIRT = D["UTS-D03"]["params"]["facets"]
PK = D["UTS-D08"]["params"]
BODY_T = 0.17
WALL_H = D["UTS-D06"]["params"]["wallToThickness"]
CAP_SIDE_H = D["UTS-D03"]["params"]["sideHeightToR"]
DISH_SLOPE_DEG = 6.0  # provisional midpoint of the 4-8° range; depth unknown
ENV = PF["sideEnvelope"]
CLEAN_SIDES = [0, 2, 3, 5]  # blade@80 upper (f77,f78), blade@207 lower (f77,f78)


def sc(x, y):
    return (S * x, S * y)


def rot(pts, deg):
    a = math.radians(deg)
    return [(S * (x * math.cos(a) - y * math.sin(a)), S * (x * math.sin(a) + y * math.cos(a))) for x, y in pts]


def side_y(x: float) -> float:
    """Upper side arc: circle centre (0, -CY), radius RS."""
    return math.sqrt(max(0.0, RS * RS - x * x)) - CY


def notch_apex() -> tuple[float, float]:
    """Intersection of the upper side arc with the 60° bisector."""
    b = 2.0 * math.sqrt(3.0) * CY
    c = CY * CY - RS * RS
    x = (-b + math.sqrt(b * b - 16.0 * c)) / 8.0
    return (x, math.sqrt(3.0) * x)


def fillet_tangent() -> tuple[float, float]:
    L = math.hypot(XC, CY)
    return (XC / L * RS, -CY + CY / L * RS)


def planform_half() -> list[tuple[float, float]]:
    """Upper half outline, root (notch apex on the bisector) -> tip (1, 0)."""
    ax_, ay_ = notch_apex()
    tx, ty = fillet_tangent()
    a0 = math.atan2(ay_ + CY, ax_)
    a1 = math.atan2(ty + CY, tx)
    pts = []
    n = 40
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        pts.append((RS * math.cos(a), RS * math.sin(a) - CY))
    f0 = math.atan2(ty, tx - XC)
    for k in range(1, 7):
        a = f0 * (1 - k / 6)
        pts.append((XC + RT * math.cos(a), RT * math.sin(a)))
    return pts


def half_width(x: float) -> float:
    tx, _ = fillet_tangent()
    if x >= tx:
        return math.sqrt(max(0.0, RT * RT - (x - XC) ** 2))
    return side_y(x)


def offset_inward(half: list[tuple[float, float]], w: float) -> list[tuple[float, float]]:
    out = []
    n = len(half)
    for i in range(1, n - 1):
        (x0, y0), (x1, y1), (x2, y2) = half[i - 1], half[i], half[i + 1]
        tx, ty = x2 - x0, y2 - y0
        L = math.hypot(tx, ty) or 1.0
        nx, ny = ty / L, -tx / L
        if nx * x1 + ny * y1 < 0:
            nx, ny = -nx, -ny
        out.append((x1 - w * nx, y1 - w * ny))
    return out


def v5_half() -> list[tuple[float, float]]:
    """Superseded v4/v5 outline (rounded triangle + radial notch + 0.09 R shoulder fillet), for contrast only."""
    old = PM["superseded"]["v4v5"]
    xv = old["virtualVertexRadiusToR"]
    side = math.radians(old["sideAngleToBladeAxisDeg"])
    tip_r = old["cornerArcRadiusToR"]
    root_polar = math.radians(39.0)
    fil = old.get("shoulderFilletRadiusToR", 0.09)
    root = (CAP * math.cos(root_polar), CAP * math.sin(root_polar))
    xs_ = xv * math.tan(side) / (math.tan(root_polar) + math.tan(side))
    vertex = (xs_, xs_ * math.tan(root_polar))
    d1 = (math.cos(root_polar), math.sin(root_polar))
    d2 = (math.cos(-side), math.sin(-side))
    turn = math.acos(d1[0] * d2[0] + d1[1] * d2[1])
    tlen = fil * math.tan(turn / 2)
    t1 = (vertex[0] - d1[0] * tlen, vertex[1] - d1[1] * tlen)
    t2 = (vertex[0] + d2[0] * tlen, vertex[1] + d2[1] * tlen)
    n1 = (d1[1], -d1[0])
    centre = (t1[0] + n1[0] * fil, t1[1] + n1[1] * fil)
    a1 = math.atan2(t1[1] - centre[1], t1[0] - centre[0])
    a2 = math.atan2(t2[1] - centre[1], t2[0] - centre[0])
    while a2 > a1:
        a2 -= 2 * math.pi
    pts = [root, t1]
    for k in range(1, 8):
        a = a1 + (a2 - a1) * k / 8
        pts.append((centre[0] + fil * math.cos(a), centre[1] + fil * math.sin(a)))
    t_tan = tip_r / math.tan(side)
    tangent = (xv - t_tan * math.cos(side), t_tan * math.sin(side))
    pts.append(t2)
    pts.append(tangent)
    cx = 1.0 - tip_r
    a0 = math.pi / 2 - side
    for k in range(1, 13):
        a = a0 * (1 - k / 12)
        pts.append((cx + tip_r * math.cos(a), tip_r * math.sin(a)))
    return pts


def draw_cap_plan(ax, scale=S, lw=1.3):
    skirt = [(CAP * math.cos(2 * math.pi * (j + 0.5) / N_SKIRT), CAP * math.sin(2 * math.pi * (j + 0.5) / N_SKIRT)) for j in range(N_SKIRT)]
    poly(ax, [(scale * x, scale * y) for x, y in skirt], lw=lw)
    for j in range(N_WEDGE):
        a_in = 2 * math.pi * j / N_WEDGE
        a_out = 2 * math.pi * (j + 0.5) / N_WEDGE
        i0 = (scale * CAP * TABLE * math.cos(a_in), scale * CAP * TABLE * math.sin(a_in))
        i1 = (scale * CAP * TABLE * math.cos(a_in + 2 * math.pi / N_WEDGE), scale * CAP * TABLE * math.sin(a_in + 2 * math.pi / N_WEDGE))
        o = (scale * CAP * math.cos(a_out), scale * CAP * math.sin(a_out))
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=0.45)
    circle(ax, CAP * TABLE * scale, lw=0.9)
    for f in (0.25, 0.5, 0.75):
        circle(ax, CAP * TABLE * scale * f, lw=0.25, color=HIDDEN)


def plan(ax):
    setup(ax, "REFERENCE PLAN v6  顶视 — 叶边为凸圆弧（R≈1.37 R），相邻弧在角平分线处相交、几乎贴盖圈；无直边、无肩角；叶尖 ≈90°+0.03 R 圆角", (-1.5 * S, 1.5 * S), (-1.42 * S, 1.36 * S))
    centerlines(ax, 1.2 * S)
    circle(ax, S, lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))
    half = planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    plateau_all = offset_inward(half, BEVEL_W)
    plateau_u = [p for p in plateau_all if math.hypot(*p) > CAP * 1.03]  # clip under the cap
    apex = notch_apex()
    for ang in (90, 210, 330):
        poly(ax, rot(full, ang), lw=1.3, close=False)
        for s_ in (1, -1):
            poly(ax, rot([(x, s_ * y) for x, y in plateau_u], ang), lw=0.7, color=HIDDEN, close=False)
        edge_pts = [p for p in half[2:-6] if math.hypot(*p) > CAP * 1.08]
        idxs = np.linspace(0, len(edge_pts) - 1, FACETS + 2).astype(int)
        for k, i in enumerate(idxs):
            ex, ey = edge_pts[i]
            j = min(range(len(plateau_u)), key=lambda jj: (plateau_u[jj][0] - ex) ** 2 + (plateau_u[jj][1] - ey) ** 2)
            px, py = plateau_u[j]
            skew = 0.010 * (1 if k % 2 == 0 else -1)
            for s_ in (1, -1):
                poly(ax, rot([(ex, s_ * ey), (px + skew, s_ * py)], ang), lw=0.5, color=INK, close=False)
        corner_x = plateau_u[-1][0]
        poly(ax, rot([(corner_x, 0.0), (1.0 - RT * 1.5, 0.0)], ang), lw=0.6, color=HIDDEN, close=False)
        # pocket (D08)
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
            seq = []
            for i in range(n):
                seq.append(out[2 * i + 1])
                seq.append(out[2 * ((i + 1) % n)])
            return seq

        pr = rounded(pocket, rc)
        ax.add_patch(Polygon(rot(pr, ang), closed=True, fill=True, fc="#e3e3e3", ec=INK, lw=0.9, zorder=2))
        inner = [(x * 0.965 + 0.02 * (1 if i == 0 else 0), y * 0.82) for i, (x, y) in enumerate(pr)]
        ax.add_patch(Polygon(rot(inner, ang), closed=True, fill=True, fc="#a8a8a8", ec=INK, lw=0.5, hatch="....", zorder=3))
    draw_cap_plan(ax)
    # side-arc construction for the 330° blade (upper side): centre marker + radius line
    c_local = (0.0, -CY)
    cpt = rot([c_local], 330)[0]
    mid = rot([(0.62, side_y(0.62))], 330)[0]
    ax.plot([cpt[0], mid[0]], [cpt[1], mid[1]], color=ALT, lw=0.5, ls=(0, (4, 2)))
    ax.plot([cpt[0]], [cpt[1]], marker="+", color=ALT, ms=7, mew=0.8)
    leader(ax, ((cpt[0] + mid[0]) / 2, (cpt[1] + mid[1]) / 2), f"叶边凸弧 R≈{RS:.2f} R（≈{RS * S:.0f} mm @85）\n圆心在叶轴垂线上，距盖心 {CY:.2f} R", sc(0.55, -0.62), color=ALT)
    # dimensions / callouts
    dim(ax, (-S, -1.27 * S), (S, -1.27 * S), 0.0, "2R = 85 mm  user-authorized-provisional（非 measured；仅供未来 Gate 03–05）", ext=False)
    for xx in (-S, S):
        ax.plot([xx, xx], [-1.27 * S, -0.3 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    a_pt = rot([apex], 90)[0]
    a_pt2 = rot([(apex[0], -apex[1])], 90)[0]
    dim(ax, a_pt2, a_pt, -0.86 * S, f"叶根宽 ≈{2 * apex[1]:.2f} R（≈{2 * apex[1] / (2 * CAP):.2f}×盖径）— 最宽处即叶根")
    leader(ax, rot([apex], 210)[0], f"缺口底 = 相邻两弧交点，r≈{math.hypot(*apex):.3f} R，距盖圈仅 ≈{(math.hypot(*apex) - CAP) * S:.1f} mm @85（几乎贴近）；弧与盖圈相切角 ≈{PM['arcToCapCrossingAngleDeg']:.0f}°（锐角）", sc(-1.47, -0.80))
    leader(ax, rot([(1.0, 0.0)], 330)[0], f"D07 叶尖：两弧夹角 ≈{PM['tipIncludedAngleDeg']:.0f}°\n圆角 R≈{RT:.2f} R（≈{RT * S:.1f} mm @85）", sc(0.60, -1.12))
    leader(ax, rot([(PK['apexRadiusToR'] - 0.03, 0.0)], 210)[0], f"D08 铣削三角凹坑：平底、圆角 ≈{PK['cornerRadiusToR']:.3f} R；尖端 r≈{PK['apexRadiusToR']:.2f} R，底边半宽 ≈{PK['baseHalfWidthToR']:.3f} R；深度未知", sc(-1.47, -1.05))
    leader(ax, rot([(0.60, side_y(0.60) - BEVEL_W * 0.5)], 330)[0], f"D05 鳞面带 ≈{BEVEL_W:.2f} R\n每边 {FACETS}±1 平面，沿弧排布", sc(0.60, -0.90))
    leader(ax, rot([(0.72, 0.02)], 330)[0], "D04 平台（平面）", sc(0.95, -0.45))
    leader(ax, sc(CAP * math.cos(math.radians(195)), CAP * math.sin(math.radians(195))), f"D03 盖裙 {N_SKIRT}±1 鳞面 ×2 排 · D02 冠环 {N_WEDGE}±1 楔 = {2 * N_WEDGE} 三角", sc(-1.47, 0.62))
    leader(ax, sc(CAP * TABLE * math.cos(math.radians(160)), CAP * TABLE * math.sin(math.radians(160))), f"D01 车削盘 {TABLE:.2f}×盖：盘缘最高，盘内凹面拇指位（用户口述，深度未知）", sc(-1.47, 0.20))
    leader(ax, rot([(0.30, side_y(0.30))], 90)[0], "D09 缺口：仅新月缝内露出冠环+裙\n无宽扇形露盖；暗缝宽未知", sc(0.55, 1.20))
    ax.text(-1.47 * S, -1.38 * S, "细线 = 平台边界 / 鳞面分界 / 叶尖脊；灰 = 凹坑（点状 = 平底）；v4/v5 的直边+径向缺口+肩角已作废（见 Detail D 对比）。", fontsize=6.5, color=HIDDEN)


def section_aa(ax):
    setup(ax, "SECTION A—A v6  过叶轴（右）与对侧缺口（左）· 盖：盘缘最高，冠环向外向下，盘内凹（用户口述，6° 占位）", (-1.25 * S, 1.3 * S), (-0.46 * S, 0.50 * S))
    ax.plot([-1.25 * S, 1.3 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    apex_r = math.hypot(*notch_apex())
    corner_x = 1.0 - RT - BEVEL_W * 1.2
    body = [sc(CAP, t / 2), sc(corner_x, t / 2), sc(1.0 - RT * 0.5, wall / 2), sc(1.0, wall / 2 * 0.5), sc(1.0, -wall / 2 * 0.5), sc(1.0 - RT * 0.5, -wall / 2), sc(corner_x, -t / 2), sc(CAP, -t / 2)]
    poly(ax, body, lw=1.2, hatch="////")
    pd = 0.35 * t
    for sgn in (1, -1):
        rec = [sc(CAP, sgn * t / 2), sc(CAP, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"] - 0.03, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"], sgn * t / 2)]
        ax.add_patch(Polygon(rec, closed=True, fill=True, fc="white", ec=ALT, lw=0.9, ls=(0, (4, 2)), zorder=4))
    # opposite notch: body sliver only up to the notch apex radius
    poly(ax, [sc(-CAP, t / 2 * 0.55), sc(-apex_r, t / 2 * 0.55), sc(-apex_r, -t / 2 * 0.55), sc(-CAP, -t / 2 * 0.55)], lw=1.0, hatch="////")
    top = t / 2 + CAP_SIDE_H
    crown_h = 0.45 * CAP_SIDE_H
    dish_d = CAP * TABLE * math.tan(math.radians(DISH_SLOPE_DEG))
    for sgn in (1, -1):
        cap_pts = [sc(-CAP * TABLE, sgn * top), sc(0.0, sgn * (top - dish_d)), sc(CAP * TABLE, sgn * top), sc(CAP, sgn * (top - crown_h)), sc(CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (top - crown_h))]
        poly(ax, cap_pts, lw=1.2, hatch="\\\\\\\\")
        # skirt row boundary
        ax.plot([sc(-CAP, 0)[0], sc(CAP, 0)[0]], [sc(0, sgn * (t / 2 + 0.5 * (top - crown_h - t / 2)))[1]] * 2, color=INK, lw=0.4)
    dim(ax, sc(corner_x - 0.05, -t / 2), sc(corner_x - 0.05, t / 2), -0.62 * S, f"厚 ≈{BODY_T:.2f} R（占位）")
    dim(ax, sc(CAP * 0.5, t / 2), sc(CAP * 0.5, top), -0.95 * S, f"D03 盖侧 ≈{CAP_SIDE_H:.2f} R")
    dim(ax, sc(0.0, top - dish_d), sc(0.0, top), 0.78 * S, f"凹深 ≈{dish_d:.3f} R（6° 占位）", color=ALT)
    leader(ax, sc(CAP * TABLE, top), "盘缘 = 盖最高点（f0077 远侧冠环被压缩 → 冠环面背向相机 → 向外向下）", sc(0.30, 0.44), fs=6)
    leader(ax, sc(PK["apexRadiusToR"] - 0.02, t / 2 - pd), "D08 平底凹坑，深度未知（虚线占位）", sc(-1.22, -0.40), color=ALT, fs=6)
    leader(ax, sc(-apex_r, t / 2 * 0.55), f"缺口底 r≈{apex_r:.3f} R，贴盖圈", sc(-1.22, 0.30), fs=6)


def detail_notch(ax):
    """Detail D: notch between the 90° and 210° blades, bisector rotated to +y. 3x scale."""
    k = 3.0
    setup(ax, "DETAIL D (3:1) 缺口过渡：两凸弧相交、贴盖圈\n虚线 = 作废的 v5 径向缺口 + 肩角", (-0.42 * S * k, 0.42 * S * k), (0.28 * S * k, 0.92 * S * k))
    # local frame: bisector along +y. Blade A axis at -60° from +y, blade B at +60°.
    def to_local(pts, blade_rot_deg):
        out = []
        for x, y in pts:
            a = math.radians(blade_rot_deg)
            xr, yr = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
            out.append((xr * S * k, yr * S * k))
        return out
    half = planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    v5 = v5_half()
    v5full = v5 + [(x, -y) for x, y in reversed(v5) if y > 1e-9]
    for blade_rot in (30, 150):  # blade axes at ±60° around the +y bisector (90° ± 60°)
        poly(ax, to_local(full, blade_rot), lw=1.4, close=False)
        poly(ax, to_local(v5full, blade_rot), lw=0.7, color=ALT, ls=(0, (4, 2)), close=False)
    # cap
    circle(ax, CAP * S * k, lw=1.2)
    circle(ax, CAP * TABLE * S * k, lw=0.8)
    skirt = [(CAP * math.cos(2 * math.pi * (j + 0.5) / N_SKIRT + math.pi / 2), CAP * math.sin(2 * math.pi * (j + 0.5) / N_SKIRT + math.pi / 2)) for j in range(N_SKIRT)]
    poly(ax, [(x * S * k, y * S * k) for x, y in skirt], lw=0.6, color=HIDDEN)
    for j in range(N_WEDGE):
        a_in = 2 * math.pi * j / N_WEDGE + math.pi / 2
        a_out = 2 * math.pi * (j + 0.5) / N_WEDGE + math.pi / 2
        i0 = (S * k * CAP * TABLE * math.cos(a_in), S * k * CAP * TABLE * math.sin(a_in))
        i1 = (S * k * CAP * TABLE * math.cos(a_in + 2 * math.pi / N_WEDGE), S * k * CAP * TABLE * math.sin(a_in + 2 * math.pi / N_WEDGE))
        o = (S * k * CAP * math.cos(a_out), S * k * CAP * math.sin(a_out))
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=0.4)
    apex = notch_apex()
    ar = math.hypot(*apex)
    apt = (0.0, ar * S * k)
    ax.plot([apt[0]], [apt[1]], marker="o", ms=3, color=INK)
    # crossing point of the blade-A upper arc with the cap circle (polar 62° in blade frame -> local)
    th = math.radians(PM["arcMeetsCapAtPolarDeg"])
    cross_blade = (CAP * math.cos(th), CAP * math.sin(th))
    cross = to_local([cross_blade], 30)[0]
    ax.plot([cross[0]], [cross[1]], marker="o", ms=3, color=ALT)
    leader(ax, apt, f"两弧交点 r≈{ar:.3f} R，距盖圈 ≈{(ar - CAP) * S:.1f} mm @85\nV 内角 ≈{PM['notchVInteriorAngleDeg']:.0f}°", (-0.41 * S * k, 0.86 * S * k), fs=6)
    leader(ax, cross, f"弧穿过盖圈处夹角 ≈{PM['arcToCapCrossingAngleDeg']:.0f}°（锐角新月尖）\n= f0148/f0134 红圈处的过渡", (0.06 * S * k, 0.86 * S * k), color=ALT, fs=6)
    # v5 radial side annotation
    v5root = to_local([(CAP * math.cos(math.radians(39)), CAP * math.sin(math.radians(39)))], 30)[0]
    leader(ax, v5root, "v5：径向缺口边与盖圈成 90°（读作钝角）— 作废", (-0.41 * S * k, 0.31 * S * k), color=ALT, fs=6)
    leader(ax, (0.0, CAP * TABLE * S * k), f"D01 盘缘 {TABLE:.2f}×盖 · D02 冠环 {N_WEDGE} 楔", (0.10 * S * k, 0.31 * S * k), fs=6)


def detail_cap(ax):
    """Detail E: half section of the cap top, adopted (E1) and alternative (E2) readings."""
    k = 3.0
    setup(ax, "DETAIL E (3:1) 盖顶半剖 — 请二选一\nE1 实线：盘缘最高、冠环外低、盘内凹  E2 虚线：整顶内凹、冠环向内向下", (-0.02 * S * k, 0.62 * S * k), (-0.06 * S * k, 0.26 * S * k))
    base = 0.0
    top = CAP_SIDE_H
    crown_h = 0.45 * CAP_SIDE_H
    dish_d = CAP * TABLE * math.tan(math.radians(DISH_SLOPE_DEG))
    e1 = [(0.0, base), (CAP, base), (CAP, top - crown_h), (CAP * TABLE, top), (0.0, top - dish_d)]
    poly(ax, [(x * S * k, y * S * k) for x, y in e1], lw=1.3, hatch="\\\\\\\\")
    # skirt rows
    ax.plot([0, CAP * S * k], [(top - crown_h) * 0.5 * S * k] * 2, color=INK, lw=0.4)
    # E2 alternative: ring slopes inward-down from the rim to the disc, disc flat/dished lower
    e2 = [(CAP, top), (CAP * TABLE, top - crown_h * 0.8), (0.0, top - crown_h * 0.8 - dish_d)]
    ax.plot([x * S * k for x, _ in e2], [y * S * k for _, y in e2], color=ALT, lw=1.0, ls=(0, (4, 2)))
    ax.plot([CAP * S * k] * 2, [(top - crown_h) * S * k, top * S * k], color=ALT, lw=1.0, ls=(0, (4, 2)))
    # concentric turning marks on the dish
    for f in (0.3, 0.55, 0.8):
        x = CAP * TABLE * f
        y = top - dish_d * (1 - f)
        ax.plot([x * S * k], [y * S * k], marker="|", color=HIDDEN, ms=4, mew=0.6)
    dim(ax, (CAP * TABLE * S * k, top * S * k), (CAP * S * k, top * S * k), 0.02 * S * k, f"冠环宽 {CAP * (1 - TABLE):.3f} R", fs=6)
    dim(ax, (CAP * S * k, (top - crown_h) * S * k), (CAP * S * k, top * S * k), -0.04 * S * k, f"落差 ≈{crown_h:.3f} R（占位）", fs=6)
    dim(ax, (0.0, (top - dish_d) * S * k), (0.0, top * S * k), 0.10 * S * k, f"凹深 ≈{dish_d:.3f} R（6° 占位）", color=ALT, fs=6)
    leader(ax, (CAP * TABLE * S * k, top * S * k), "E1 盘缘 = 最高点（f0077 远侧冠环被压缩\n⇒ 冠环面背向相机 ⇒ 向外向下）", (0.02 * S * k, 0.235 * S * k), fs=6)
    leader(ax, (CAP * TABLE * S * k, (top - crown_h * 0.8) * S * k), "E2 备选：冠环 14 楔向内向下，整个顶面成碟形\n（若“14 片有内凹效果”指的是冠环）", (0.06 * S * k, -0.04 * S * k), color=ALT, fs=6)
    leader(ax, (0.0, (top - dish_d) * S * k), "D01 车削凹盘（拇指位，用户口述 20:46）\n锥面/球面、深度未知", (0.02 * S * k, 0.06 * S * k), color=ALT, fs=6)


def profile_table(ax):
    setup(ax, "实测叶边半宽（4 条干净边，单位=该叶尖半径）vs v6 凸弧模型", (0, 10), (0, 10))
    xs = ENV["x"]
    per = ENV["perSide"]
    rows = [("x/R", "实测均值", "v6 模型", "差", "v5 直边模型")]
    old = PM["superseded"]["v4v5"]
    xv = old["virtualVertexRadiusToR"]
    for i, x in enumerate(xs):
        vals = [per[j][i] for j in CLEAN_SIDES if per[j][i] is not None]
        m = sum(vals) / len(vals)
        mod = half_width(x)
        v5m = (xv - x) * math.tan(math.radians(30.0))
        if x > xv - old["cornerArcRadiusToR"] / math.tan(math.radians(30.0)) * math.cos(math.radians(30.0)):
            cx = 1.0 - old["cornerArcRadiusToR"]
            v5m = math.sqrt(max(0.0, old["cornerArcRadiusToR"] ** 2 - (x - cx) ** 2))
        rows.append((f"{x:.2f}", f"{m:.3f}", f"{mod:.3f}", f"{mod - m:+.3f}", f"{v5m:.3f}"))
    for i, r in enumerate(rows):
        y = 9.5 - i * 0.60
        col = INK if i else DIM
        for j, txt in enumerate(r):
            ax.text(0.3 + j * 2.0, y, txt, fontsize=7, color=col, family=FONT)
    ax.text(0.3, 0.35, f"弧拟合 rms 0.0006–0.0010 R，直线拟合 rms 0.011–0.015 R（f0077/f0078）。模型：R_s={RS:.3f} R，圆心 (0, −{CY:.2f} R)，叶尖圆角 {RT:.2f} R。", fontsize=6.5, color=ALT, family=FONT)


def main() -> None:
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.10, 0.50, 0.86])
    ax_aa = fig.add_axes([0.53, 0.70, 0.46, 0.25])
    ax_dd = fig.add_axes([0.53, 0.37, 0.225, 0.31])
    ax_ee = fig.add_axes([0.765, 0.37, 0.225, 0.31])
    ax_tb = fig.add_axes([0.53, 0.09, 0.46, 0.26])
    plan(ax_plan)
    section_aa(ax_aa)
    detail_notch(ax_dd)
    detail_cap(ax_ee)
    profile_table(ax_tb)
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD v6 (convex-arc blade sides hugging the cap + 14-wedge crown / 14-scale skirt / concave turned thumb dish) · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, f"UNITS: R 比例；mm 仅 85 mm user-authorized-provisional · 叶边凸弧 R {RS:.2f} R、圆心距 {CY:.2f} R、相邻弧交于 r {math.hypot(*notch_apex()):.3f} R（贴盖圈）· 叶尖 90°+{RT:.2f} R · 冠环 {N_WEDGE} 楔 · 盘 {TABLE:.2f}×盖、凹面深度未知 · 凹坑深/缝宽未知 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE surface-detail-spec.json (planformProfile.parametric v6) ← blade-root-traces / side-envelope arc fits ← f0077 f0078 → draw_geeone_reference_cad_v6.py · {date.today().isoformat()} · v1–v5 保留为历史", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video-v6.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video-v6.png")


if __name__ == "__main__":
    main()
