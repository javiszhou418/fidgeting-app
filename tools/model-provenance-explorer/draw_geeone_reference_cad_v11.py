"""Reference CAD v11 (v10 + multi-row dragon-scale transition on every blade edge, same construction as the cap edge): blade sides are convex circular arcs (R≈1.37 R, centre on
the blade's perpendicular through the cap centre at 0.92 R). Near the root each
arc blends (R≈0.15 R) inward and ENDS on the cap circle at polar ≈52°; adjacent
blades do not touch — the cap crown/skirt is exposed over ≈16° per notch (user
2026-09-07 07:53: “这个部分是有些间隔的，不需要连接在一起”). No straight side,
no shoulder. Tip: ≈90° included angle with a 0.03 R fillet. Cap: the central
disc is a shallow CONCAVE 14-gon pyramid — 14 equal planar sectors from the
centre apex to a 14-gon rim at 0.82 cap (user 2026-09-07 08:25 “以圆心为中心…切分
成14片。均分”); the rim vertices coincide with the 14-wedge crown ring's inner
vertices (28 triangles, sloping outward-down); 14-scale skirt in two rows.

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
FACETS = D["UTS-D05"]["params"]["facetsPerRowPerEdge"]
EDGE_TIERS = D["UTS-D05"]["params"]["tiers"]  # blade edge rows, top face -> wall
EDGE_DROP = sum(t_["widthToR"] * math.tan(math.radians(t_["slopeDeg"])) for t_ in EDGE_TIERS)
CAP_TIERS = D["UTS-D02"]["params"]["capEdgeTiers"]  # crown / upper skirt / lower skirt
TIER_COLORS = ("#7CC144", "#E2452B", "#3B8BEB")  # user's green / red / blue (disc -> vertical side)
ROW_COLORS = ("#2E8B57", "#C0392B", "#2C6FBF")  # blade edge rows 1-3 (top face -> wall)
N_WEDGE = D["UTS-D02"]["params"]["wedges"]
N_SKIRT = D["UTS-D03"]["params"]["facets"]
PK = D["UTS-D08"]["params"]
BODY_T = 0.17
WALL_H = D["UTS-D06"]["params"]["wallToThickness"]
CAP_SIDE_H = D["UTS-D03"]["params"]["sideHeightToR"]
DISH_SLOPE_DEG = float(D["UTS-D01"]["params"]["dishSlopeDegProvisional"])  # provisional; depth unknown
N_SECTOR = D["UTS-D01"]["params"]["sectors"]
YR = D["UTS-D04"]["params"]
Y_JX = YR["junctionX"]
Y_END = math.radians(YR["armEndPolarDeg"])
Y_MID = tuple(YR["armMidpoint"])
CREST = 0.025  # provisional crest rise (R)
POCKET_DEPTH_FRACTION = 0.25  # placeholder per side; depth unknown


def cap_edge_profile(top: float) -> list[tuple[float, float]]:
    """(r, z) from the disc rim outward through the three cap-edge tiers: crown -> upper skirt -> lower skirt."""
    pts = [(CAP * TABLE, top)]
    r, z = pts[0]
    for tier in CAP_TIERS:
        r += tier["radialToCap"] * CAP
        z -= tier["radialToCap"] * CAP * math.tan(math.radians(tier["slopeDeg"]))
        pts.append((r, z))
    return pts


def edge_profile_upper_right(hw: float, t: float) -> list[tuple[float, float]]:
    """(y, z) of the upper-right blade edge: top-face edge -> row 1 -> row 2 -> row 3 -> wall top (D05 multi-row)."""
    pts = [(hw - BEVEL_W, t / 2)]
    y, z = pts[0]
    for tier in EDGE_TIERS:
        y += tier["widthToR"]
        z -= tier["widthToR"] * math.tan(math.radians(tier["slopeDeg"]))
        pts.append((y, z))
    return pts


def wall_half(t: float) -> float:
    return t / 2 - EDGE_DROP


def y_crest_arm() -> list[tuple[float, float]]:
    """Upper arm of the Y crest: quadratic Bezier junction -> (bulging) -> root corner on the cap."""
    p0 = (Y_JX, 0.0)
    p2 = (CAP * math.cos(Y_END), CAP * math.sin(Y_END))
    m = Y_MID
    # control point so the curve passes through the midpoint at t=0.5: c = 2m - (p0+p2)/2
    c = (2 * m[0] - (p0[0] + p2[0]) / 2, 2 * m[1] - (p0[1] + p2[1]) / 2)
    pts = []
    for k in range(17):
        t = k / 16
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def y_crest_stem() -> list[tuple[float, float]]:
    return [(Y_JX, 0.0), (1.0 - RT * 1.5, 0.0)]
RB = PM["rootBlend"]
ROOT_POLAR = math.radians(RB["meetsCapAtPolarDeg"])
XB = RB["startX"]
RB_R = RB["radiusToR"]
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


def root_point() -> tuple[float, float]:
    """Where the blade edge ends on the cap circle (polar ROOT_POLAR)."""
    return (CAP * math.cos(ROOT_POLAR), CAP * math.sin(ROOT_POLAR))


def blend_geometry():
    """Root blend: circle tangent to the big side arc at x=XB and passing through root_point()."""
    yb = side_y(XB)
    nx, ny = XB / RS, (yb + CY) / RS  # outward normal of the big circle at the blend start
    tx, ty = root_point()
    dx, dy = XB - tx, yb - ty
    rb = (dx * dx + dy * dy) / (2.0 * (dx * nx + dy * ny))
    centre = (XB - rb * nx, yb - rb * ny)
    return (XB, yb), centre, rb


def notch_apex() -> tuple[float, float]:
    """Compatibility: the v6 V-apex (adjacent arcs meeting on the bisector) — superseded, drawn dashed only."""
    b = 2.0 * math.sqrt(3.0) * CY
    c = CY * CY - RS * RS
    x = (-b + math.sqrt(b * b - 16.0 * c)) / 8.0
    return (x, math.sqrt(3.0) * x)


def fillet_tangent() -> tuple[float, float]:
    L = math.hypot(XC, CY)
    return (XC / L * RS, -CY + CY / L * RS)


def v6_half() -> list[tuple[float, float]]:
    """Superseded v6 outline (adjacent arcs meeting on the bisector), for contrast only."""
    ax_, ay_ = notch_apex()
    tx, ty = fillet_tangent()
    a0 = math.atan2(ay_ + CY, ax_)
    a1 = math.atan2(ty + CY, tx)
    pts = []
    for k in range(41):
        a = a0 + (a1 - a0) * k / 40
        pts.append((RS * math.cos(a), RS * math.sin(a) - CY))
    f0 = math.atan2(ty, tx - XC)
    for k in range(1, 7):
        a = f0 * (1 - k / 6)
        pts.append((XC + RT * math.cos(a), RT * math.sin(a)))
    return pts


def planform_half() -> list[tuple[float, float]]:
    """Upper half outline, root (on the cap circle, polar ROOT_POLAR) -> blend -> big arc -> tip fillet -> (1, 0)."""
    (xb, yb), cb, rb = blend_geometry()
    rx, ry = root_point()
    b0 = math.atan2(ry - cb[1], rx - cb[0])
    b1 = math.atan2(yb - cb[1], xb - cb[0])
    sweep = (b1 - b0 + math.pi) % (2 * math.pi) - math.pi  # shortest signed sweep
    pts = []
    for k in range(13):
        a = b0 + sweep * k / 12
        pts.append((cb[0] + rb * math.cos(a), cb[1] + rb * math.sin(a)))
    tx, ty = fillet_tangent()
    a0 = math.atan2(yb + CY, xb)
    a1 = math.atan2(ty + CY, tx)
    n = 40
    for k in range(1, n + 1):
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
    if x < XB:
        (_, _), cb, rb = blend_geometry()
        return cb[1] + math.sqrt(max(0.0, rb * rb - (x - cb[0]) ** 2))
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
    r1 = CAP * (TABLE + CAP_TIERS[0]["radialToCap"])  # crown outer radius (tier 1 / tier 2 boundary)
    r2 = r1 + CAP_TIERS[1]["radialToCap"] * CAP  # tier 2 / tier 3 boundary
    for rr, col in ((r1, TIER_COLORS[0]), (r2, TIER_COLORS[1])):
        ring = [(rr * math.cos(2 * math.pi * (j + 0.5) / N_SKIRT), rr * math.sin(2 * math.pi * (j + 0.5) / N_SKIRT)) for j in range(N_SKIRT)]
        poly(ax, [(scale * x, scale * y) for x, y in ring], lw=0.7, color=col)
    for j in range(N_WEDGE):
        a_in = 2 * math.pi * j / N_WEDGE
        a_out = 2 * math.pi * (j + 0.5) / N_WEDGE
        i0 = (scale * CAP * TABLE * math.cos(a_in), scale * CAP * TABLE * math.sin(a_in))
        i1 = (scale * CAP * TABLE * math.cos(a_in + 2 * math.pi / N_WEDGE), scale * CAP * TABLE * math.sin(a_in + 2 * math.pi / N_WEDGE))
        o = (scale * r1 * math.cos(a_out), scale * r1 * math.sin(a_out))
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=0.45)
        # skirt scale side edges (rows 2 and 3) run radially at the wedge tips
        ax.plot([o[0], scale * CAP * math.cos(a_out)], [o[1], scale * CAP * math.sin(a_out)], color=INK, lw=0.35)
    rim = [(CAP * TABLE * math.cos(2 * math.pi * j / N_SECTOR), CAP * TABLE * math.sin(2 * math.pi * j / N_SECTOR)) for j in range(N_SECTOR)]
    poly(ax, [(scale * x, scale * y) for x, y in rim], lw=0.9)
    for x, y in rim:  # sector creases: centre apex -> rim vertices (= crown inner vertices)
        ax.plot([0.0, scale * x], [0.0, scale * y], color=INK, lw=0.35)
    ax.plot([0.0], [0.0], marker="o", ms=2.2, color=INK)


def plan(ax):
    setup(ax, "REFERENCE PLAN v11  顶视 — 凸弧叶边止于盖圈 52° · Y 形脊线（紫）· 叶边多层鳞面 · 盘 14 扇区 · 盖缘三层 · 剖切线 A/C/F", (-1.5 * S, 1.5 * S), (-1.42 * S, 1.36 * S))
    centerlines(ax, 1.2 * S)
    circle(ax, S, lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))
    half = planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    plateau_all = offset_inward(half, BEVEL_W)
    plateau_u = [p for p in plateau_all if math.hypot(*p) > CAP * 1.03]  # clip under the cap
    root = root_point()
    (xb, yb), cb, rb = blend_geometry()
    for ang in (90, 210, 330):
        poly(ax, rot(full, ang), lw=1.3, close=False)
        for s_ in (1, -1):
            poly(ax, rot([(x, s_ * y) for x, y in plateau_u], ang), lw=0.7, color=HIDDEN, close=False)
        cum = 0.0
        for tier, col in zip(EDGE_TIERS[:-1], ROW_COLORS):  # row boundaries inside the band
            cum += tier["widthToR"]
            row = [p for p in offset_inward(half, BEVEL_W - cum) if math.hypot(*p) > CAP * 1.03]
            for s_ in (1, -1):
                poly(ax, rot([(x, s_ * y) for x, y in row], ang), lw=0.5, color=col, close=False)
        edge_pts = [p for p in half[2:-6] if math.hypot(*p) > CAP * 1.08]
        idxs = np.linspace(0, len(edge_pts) - 1, FACETS + 2).astype(int)
        for k, i in enumerate(idxs):
            ex, ey = edge_pts[i]
            j = min(range(len(plateau_u)), key=lambda jj: (plateau_u[jj][0] - ex) ** 2 + (plateau_u[jj][1] - ey) ** 2)
            px, py = plateau_u[j]
            skew = 0.010 * (1 if k % 2 == 0 else -1)
            for s_ in (1, -1):
                poly(ax, rot([(ex, s_ * ey), (px + skew, s_ * py)], ang), lw=0.5, color=INK, close=False)
        # Y-shaped raised crest (D04): stem + two bulging arms flanking the pocket
        crest_style = dict(lw=1.6, color="#6a3d9a", ls=(0, (6, 2, 1, 2)), close=False)
        poly(ax, rot(y_crest_stem(), ang), **crest_style)
        arm = y_crest_arm()
        poly(ax, rot(arm, ang), **crest_style)
        poly(ax, rot([(x, -y) for x, y in arm], ang), **crest_style)
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
    # section cut lines on the 330° blade: A-A along the axis, C-C at x=0.58, F-F at x=0.85
    def cut(p1, p2, letter):
        (x1, y1), (x2, y2) = rot([p1], 330)[0], rot([p2], 330)[0]
        ax.plot([x1, x2], [y1, y2], color=INK, lw=1.2, ls=(0, (10, 3, 2, 3)), zorder=6)
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        for (x, y), sgn in (((x1, y1), -1), ((x2, y2), 1)):
            ax.text(x + ux * sgn * 0.06 * S, y + uy * sgn * 0.06 * S, letter, fontsize=9, fontweight="bold", color=INK, ha="center", va="center", zorder=7,
                    bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=INK, lw=0.6))
    cut((0.28, 0.0), (1.10, 0.0), "A")
    cut((0.58, -0.50), (0.58, 0.50), "C")
    cut((0.85, -0.34), (0.85, 0.34), "F")
    # side-arc construction for the 330° blade (upper side): centre marker + radius line
    c_local = (0.0, -CY)
    cpt = rot([c_local], 330)[0]
    mid = rot([(0.62, side_y(0.62))], 330)[0]
    ax.plot([cpt[0], mid[0]], [cpt[1], mid[1]], color=ALT, lw=0.5, ls=(0, (4, 2)))
    ax.plot([cpt[0]], [cpt[1]], marker="+", color=ALT, ms=7, mew=0.8)
    leader(ax, ((cpt[0] + mid[0]) / 2, (cpt[1] + mid[1]) / 2), f"叶边凸弧 R≈{RS:.2f} R（≈{RS * S:.0f} mm @85）\n圆心距盖心 {CY:.2f} R（叶轴垂线上）", sc(0.96, -0.64), color=ALT)
    # dimensions / callouts
    dim(ax, (-S, -1.27 * S), (S, -1.27 * S), 0.0, "2R = 85 mm  user-authorized-provisional（非 measured；仅供未来 Gate 03–05）", ext=False)
    for xx in (-S, S):
        ax.plot([xx, xx], [-1.27 * S, -0.3 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    a_pt = rot([(xb, yb)], 90)[0]
    a_pt2 = rot([(xb, -yb)], 90)[0]
    dim(ax, a_pt2, a_pt, -0.92 * S, f"最宽处 x≈{xb:.2f} R：宽 ≈{2 * yb:.2f} R（≈{2 * yb / (2 * CAP):.2f}×盖径）；叶根止于盖圈处宽 ≈{2 * root[1]:.2f} R")
    leader(ax, rot([root], 210)[0], f"叶边止于盖圈极角 ±{RB['meetsCapAtPolarDeg']:.0f}°：根部以 R≈{rb:.2f} R 内收圆弧接入盖圈（与盖圈切线夹 ≈{RB['angleToCapTangentDeg']:.0f}°，锐角）；相邻叶片不相接，缺口露盖 ≈{RB['exposedCapArcPerNotchDeg']:.0f}°（用户 09-07：“有些间隔，不需要连接在一起”）", sc(-1.47, -0.80))
    leader(ax, rot([(1.0, 0.0)], 330)[0], f"D07 叶尖：两弧夹角 ≈{PM['tipIncludedAngleDeg']:.0f}°\n圆角 R≈{RT:.2f} R（≈{RT * S:.1f} mm @85）", sc(0.60, -1.12))
    leader(ax, rot([(PK['apexRadiusToR'] - 0.03, 0.0)], 210)[0], f"D08 铣削三角凹坑：平底、圆角 ≈{PK['cornerRadiusToR']:.3f} R；尖端 r≈{PK['apexRadiusToR']:.2f} R，底边半宽 ≈{PK['baseHalfWidthToR']:.3f} R；深度未知", sc(-1.47, -1.05))
    leader(ax, rot([(0.60, side_y(0.60) - BEVEL_W * 0.5)], 330)[0], f"D05 叶边多层龙鳞过渡（顶面→竖壁）≈{BEVEL_W:.2f} R 宽\n{len(EDGE_TIERS)} 排（占位）× 每排每边 {FACETS}±1 鳞，错半鳞；见 Detail H", sc(0.60, -0.90))
    leader(ax, rot([(0.85, 0.0)], 330)[0], f"D04 Y 形隆起脊线（紫点划线 = 最高线）\n主脊沿叶轴到 x≈{Y_JX:.2f} R；两臂沿凹坑两侧\n外凸弧线到盖圈 ±{YR['armEndPolarDeg']}°；脊高 ≈{CREST:.3f} R 占位\n（用户 09-07 08:39 红色 Y）", sc(0.66, -0.40), color="#6a3d9a", fs=6.5)
    leader(ax, sc(CAP * math.cos(math.radians(195)), CAP * math.sin(math.radians(195))), f"D03 盖裙 {N_SKIRT}±1 鳞面 ×2 排 · D02 冠环 {N_WEDGE}±1 楔 = {2 * N_WEDGE} 三角 · 盘/冠环/裙共用一套 14 等分", sc(-1.47, 0.62))
    leader(ax, sc(CAP * TABLE * math.cos(math.radians(160)), CAP * TABLE * math.sin(math.radians(160))), f"D01 盘 = {N_SECTOR} 等分平面扇区（以圆心为中心均分）→ 凹 14 棱锥拇指位\n盘缘 14 边形 {TABLE:.2f}×盖 = 最高圈，顶点与冠环内顶点重合；凹深未知（{DISH_SLOPE_DEG:.0f}° 占位）", sc(-1.47, 0.22))
    leader(ax, rot([(0.30, side_y(0.30))], 90)[0], f"D09 缺口：露盖弧 ≈{RB['exposedCapArcPerNotchDeg']:.0f}°（极角 {RB['meetsCapAtPolarDeg']:.0f}°→{120 - RB['meetsCapAtPolarDeg']:.0f}°）\n冠环+裙在此外露；暗缝宽未知", sc(0.62, 1.06))
    ax.text(-1.47 * S, -1.38 * S, "细线 = 顶面/鳞面带分界 / 鳞面分界；紫点划线 = Y 形隆起脊线（D04，取代“平台为平面”）；灰 = 凹坑（点状 = 平底）；v6 的 V 交点已作废（见 Detail D）。", fontsize=6.5, color=HIDDEN)


def section_aa(ax):
    setup(ax, "SECTION A—A v10  沿右下叶叶轴剖；左为对侧缺口；盖缘三层（绿/红/蓝）逐层变陡→竖壁", (-1.25 * S, 1.3 * S), (-0.46 * S, 0.50 * S))
    ax.plot([-1.25 * S, 1.3 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = 2 * wall_half(t)
    corner_x = 1.0 - RT - BEVEL_W * 1.2
    body = [sc(CAP, t / 2), sc(PK["apexRadiusToR"], t / 2), sc(Y_JX, t / 2 + CREST), sc(corner_x, t / 2 + CREST), sc(1.0 - RT * 0.5, wall / 2), sc(1.0, wall / 2 * 0.5), sc(1.0, -wall / 2 * 0.5), sc(1.0 - RT * 0.5, -wall / 2), sc(corner_x, -t / 2 - CREST), sc(Y_JX, -t / 2 - CREST), sc(PK["apexRadiusToR"], -t / 2), sc(CAP, -t / 2)]
    poly(ax, body, lw=1.2, hatch="////")
    leader(ax, sc((Y_JX + corner_x) / 2, t / 2 + CREST), f"D04 主脊（Y 的柄）高出顶面边 ≈{CREST:.3f} R（占位）", sc(0.55, -0.42), color="#6a3d9a", fs=6)
    pd = 0.35 * t
    for sgn in (1, -1):
        rec = [sc(CAP, sgn * t / 2), sc(CAP, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"] - 0.03, sgn * (t / 2 - pd)), sc(PK["apexRadiusToR"], sgn * t / 2)]
        ax.add_patch(Polygon(rec, closed=True, fill=True, fc="white", ec=ALT, lw=0.9, ls=(0, (4, 2)), zorder=4))
    # opposite notch: body sliver only up to the notch apex radius
    top = t / 2 + CAP_SIDE_H
    crown_h = 0.45 * CAP_SIDE_H
    dish_d = CAP * TABLE * math.tan(math.radians(DISH_SLOPE_DEG))
    for sgn in (1, -1):
        prof = cap_edge_profile(top)
        cap_pts = [sc(-r, sgn * z) for r, z in reversed(prof)] + [sc(0.0, sgn * (top - dish_d))] + [sc(r, sgn * z) for r, z in prof] + [sc(CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + 0.005))]
        poly(ax, cap_pts, lw=1.2, hatch="\\\\\\\\")
        for i in range(3):
            (r0, z0), (r1, z1) = prof[i], prof[i + 1]
            for side in (1, -1):
                ax.plot([S * side * r0, S * side * r1], [S * sgn * z0, S * sgn * z1], color=TIER_COLORS[i], lw=2.4, solid_capstyle="butt", zorder=5)
    dim(ax, sc(corner_x - 0.05, -t / 2), sc(corner_x - 0.05, t / 2), -0.62 * S, f"厚 ≈{BODY_T:.2f} R（占位）")
    dim(ax, sc(CAP * 0.5, t / 2), sc(CAP * 0.5, top), -0.95 * S, f"D03 盖侧 ≈{CAP_SIDE_H:.2f} R")
    dim(ax, sc(0.0, top - dish_d), sc(0.0, top), 0.78 * S, f"凹深 ≈{dish_d:.3f} R（{DISH_SLOPE_DEG:.0f}° 占位；视频上限 ≈2°）", color=ALT)
    leader(ax, sc(CAP * TABLE, top), "盘缘 = 盖最高点（f0077 远侧冠环被压缩 → 冠环面背向相机 → 向外向下）", sc(0.30, 0.44), fs=6)
    leader(ax, sc(PK["apexRadiusToR"] - 0.02, t / 2 - pd), "D08 平底凹坑，深度未知（虚线占位）", sc(-1.22, -0.40), color=ALT, fs=6)
    leader(ax, sc(-CAP, t / 2 * 0.3), f"对侧缺口：机身在此不超出盖圈（露盖 ≈{RB['exposedCapArcPerNotchDeg']:.0f}°），盖裙与暗缝外露", sc(-1.22, 0.30), fs=6)


def section_cc(ax):
    """Transverse section at x≈0.58 R (cut line C-C on the plan): pocket between the two Y arms; three-tier edges."""
    setup(ax, "SECTION C—C v11  沿顶视 C—C 线（x≈0.58 R）横剖，看向叶尖", (-0.56 * S, 0.56 * S), (-0.22 * S, 0.30 * S))
    ax.plot([-0.56 * S, 0.56 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    x0 = 0.58
    hw = half_width(x0)
    arm_y = Y_MID[1]
    pk_hw = PK["baseHalfWidthToR"] * 0.85
    pd = POCKET_DEPTH_FRACTION * t
    tiers_r = edge_profile_upper_right(hw, t)  # (y,z) from top-surface edge to wall top
    pw = tiers_r[0][0]
    wh = wall_half(t)
    upper_right = [sc(y, z) for y, z in tiers_r]  # pw -> hw
    top = ([sc(-y, z) for y, z in reversed(tiers_r)] + [sc(-arm_y, t / 2 + CREST), sc(-pk_hw, t / 2), sc(-pk_hw + 0.012, t / 2 - pd), sc(pk_hw - 0.012, t / 2 - pd), sc(pk_hw, t / 2), sc(arm_y, t / 2 + CREST)] + upper_right)
    bottom = [sc(y, -z) for (y, z) in reversed(tiers_r)] + [sc(arm_y, -t / 2 - CREST), sc(pk_hw, -t / 2), sc(pk_hw - 0.012, -t / 2 + pd), sc(-pk_hw + 0.012, -t / 2 + pd), sc(-pk_hw, -t / 2), sc(-arm_y, -t / 2 - CREST)] + [sc(-y, -z) for y, z in tiers_r]
    poly(ax, top + bottom, lw=1.3, hatch="////")
    for k in range(len(EDGE_TIERS)):
        (y0, z0), (y1, z1) = tiers_r[k], tiers_r[k + 1]
        ax.plot([S * y0, S * y1], [S * z0, S * z1], color=ROW_COLORS[k], lw=3.0, solid_capstyle="butt", zorder=5)
    # labels
    leader(ax, sc(arm_y, t / 2 + CREST), f"Y 臂脊线 = 最高线（高 ≈{CREST:.3f} R 占位）", sc(0.06, 0.285), color="#6a3d9a", fs=6)
    leader(ax, sc((arm_y + pw) / 2, t / 2 + CREST * 0.5), "顶面（Y 臂外侧斜面）", sc(0.30, 0.22), fs=6)
    leader(ax, sc((tiers_r[1][0] + tiers_r[2][0]) / 2, (tiers_r[1][1] + tiers_r[2][1]) / 2), f"D05 多层龙鳞过渡：{len(EDGE_TIERS)} 排逐层变陡（占位）", sc(0.22, 0.13), fs=6)
    leader(ax, sc(hw, 0.0), f"D06 竖壁 ≈{2 * wh / t:.2f}×厚", sc(0.30, -0.14), fs=6)
    leader(ax, sc(0.0, t / 2 - pd), f"D08 叶根凹坑（平底；上下镜像 D10）\n深度未知，占位 {POCKET_DEPTH_FRACTION:.0%}/侧", sc(-0.54, -0.20), color=ALT, fs=6)
    leader(ax, sc(-(pk_hw + arm_y) / 2, t / 2 + CREST * 0.5), "顶面（Y 臂内侧斜面，落向坑边）", sc(-0.54, 0.26), fs=6)
    dim(ax, sc(-hw, -wh), sc(hw, -wh), -0.06 * S, f"叶宽 ≈{2 * hw:.2f} R", fs=6)
    dim(ax, sc(hw + 0.02, -t / 2 - CREST), sc(hw + 0.02, t / 2 + CREST), -0.05 * S, f"总厚 ≈{t + 2 * CREST:.2f} R（占位）", fs=6)


def section_ff(ax):
    """Transverse section at x≈0.85 R (cut line F-F): single crowned ridge, three-tier edges."""
    setup(ax, "SECTION F—F v11  沿 F—F 线（x≈0.85 R）", (-0.36 * S, 0.36 * S), (-0.22 * S, 0.30 * S))
    ax.plot([-0.36 * S, 0.36 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    hw = half_width(0.85)
    tiers_r = edge_profile_upper_right(hw, t)
    wh = wall_half(t)
    top = [sc(-y, z) for y, z in reversed(tiers_r)] + [sc(0.0, t / 2 + CREST)] + [sc(y, z) for y, z in tiers_r]
    bottom = [sc(y, -z) for y, z in reversed(tiers_r)] + [sc(0.0, -t / 2 - CREST)] + [sc(-y, -z) for y, z in tiers_r]
    poly(ax, top + bottom, lw=1.3, hatch="////")
    for k in range(len(EDGE_TIERS)):
        (y0, z0), (y1, z1) = tiers_r[k], tiers_r[k + 1]
        ax.plot([S * y0, S * y1], [S * z0, S * z1], color=ROW_COLORS[k], lw=3.0, solid_capstyle="butt", zorder=5)
    leader(ax, sc(0.0, t / 2 + CREST), f"主脊 = 最高线（≈{CREST:.3f} R 占位）", sc(-0.34, 0.285), color="#6a3d9a", fs=6)
    leader(ax, sc((tiers_r[1][0] + tiers_r[2][0]) / 2, (tiers_r[1][1] + tiers_r[2][1]) / 2), "D05 多层鳞", sc(0.20, 0.20), fs=6)
    dim(ax, sc(-hw, -wh), sc(hw, -wh), -0.06 * S, f"叶宽 ≈{2 * hw:.2f} R", fs=6)


def detail_edge(ax):
    """Detail G: cap edge, half-section through a wedge tip — disc rim -> crown -> upper skirt -> lower skirt -> vertical side -> seam."""
    k = 4.0
    setup(ax, "DETAIL G (4:1) 盖缘三层过渡（盘面→竖壁）", (0.30 * S * k, 0.64 * S * k), (0.05 * S * k, 0.325 * S * k))
    t = BODY_T
    top = t / 2 + CAP_SIDE_H
    prof = cap_edge_profile(top)  # (r, z): disc rim -> t1 -> t2 -> t3
    base = t / 2 + 0.005
    pts = [(CAP * 0.62, top - 0.004)] + prof + [(CAP, base), (CAP * 0.62, base)]
    xs = [x * S * k for x, _ in pts]
    ys = [y * S * k for _, y in pts]
    ax.add_patch(Polygon(list(zip(xs, ys)), closed=True, fill=False, hatch="////", edgecolor=INK, lw=1.3))
    names = ("第 1 层（绿）冠环 D02", "第 2 层（红）裙上排 D03", "第 3 层（蓝）裙下排 D03")
    for i in range(3):
        (r0, z0), (r1, z1) = prof[i], prof[i + 1]
        ax.plot([S * k * r0, S * k * r1], [S * k * z0, S * k * z1], color=TIER_COLORS[i], lw=5, solid_capstyle="butt", zorder=5)
        tier = CAP_TIERS[i]
        ax.annotate(f"{names[i]}  径向 ≈{tier['radialToCap']:.2f}×盖径  斜 ≈{tier['slopeDeg']}°（占位）", xy=(S * k * (r0 + r1) / 2, S * k * (z0 + z1) / 2), xytext=(0.305 * S * k, (0.312 - 0.018 * i) * S * k), fontsize=6, color=TIER_COLORS[i], arrowprops=dict(arrowstyle="->", color=TIER_COLORS[i], lw=0.7), bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=TIER_COLORS[i], lw=0.4))
    ax.annotate(f"盘缘 14 边形 = 盖最高点（{TABLE:.2f}×盖）", xy=(S * k * prof[0][0], S * k * prof[0][1]), xytext=(0.305 * S * k, 0.255 * S * k), fontsize=6, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    ax.annotate(f"竖直 14 边形侧壁 ≈{max(prof[-1][1] - base, 0):.3f} R → 暗缝\n（侧高 {CAP_SIDE_H:.2f} R 低置信）", xy=(S * k * CAP, S * k * (prof[-1][1] + base) / 2), xytext=(0.50 * S * k, 0.10 * S * k), fontsize=6, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    ax.text(0.305 * S * k, 0.235 * S * k, "第 1 层 = 冠环 D02；第 2/3 层 = 盖裙两排 D03", fontsize=6, color=INK)
    ax.plot([S * k * CAP, S * k * CAP * 1.06], [S * k * base] * 2, color=ALT, lw=1.0, ls=(0, (4, 2)))
    ax.text(S * k * CAP * 1.005, S * k * (base + 0.006), "叶根 / 暗缝", fontsize=5.5, color=ALT)
    ax.text(0.305 * S * k, 0.062 * S * k, "视频确认：三层、逐层变陡、最后接竖壁（用户圈图 + f0128–f0140）\n占位：各层径向宽与角度。Gate 06 检查：三行平面、斜度递增", fontsize=5.5, color=HIDDEN)


def detail_blade_edge(ax):
    """Detail H: blade edge, 4:1 — top face -> scale rows -> vertical wall, with the brick layout sketched in plan."""
    k = 4.0
    setup(ax, "DETAIL H (4:1) 叶边多层龙鳞过渡（顶面→竖壁）", (-0.02 * S * k, 0.22 * S * k), (-0.015 * S * k, 0.165 * S * k))
    t = BODY_T
    hw = half_width(0.85)
    tiers_r = edge_profile_upper_right(hw, t)
    wh = wall_half(t)
    pts = [(0.0, t / 2 + CREST), (tiers_r[0][0], t / 2)] + tiers_r[1:] + [(hw, 0.0)]
    xs = [x * S * k for x, _ in pts]
    ys = [y * S * k for _, y in pts]
    ax.add_patch(Polygon(list(zip(xs, ys)) + [(xs[0], 0.0)], closed=True, fill=False, hatch="////", edgecolor=INK, lw=1.3))
    names = ("第 1 排（贴顶面）", "第 2 排", "第 3 排（贴竖壁）")
    for i, tier in enumerate(EDGE_TIERS):
        (y0, z0), (y1, z1) = tiers_r[i], tiers_r[i + 1]
        ax.plot([S * k * y0, S * k * y1], [S * k * z0, S * k * z1], color=ROW_COLORS[i], lw=5, solid_capstyle="butt", zorder=5)
        ax.annotate(f"{names[i]} 宽 ≈{tier['widthToR']:.3f} R · 斜 ≈{tier['slopeDeg']}°（占位）", xy=(S * k * (y0 + y1) / 2, S * k * (z0 + z1) / 2), xytext=(-0.01 * S * k, (0.158 - 0.016 * i) * S * k), fontsize=6, color=ROW_COLORS[i], arrowprops=dict(arrowstyle="->", color=ROW_COLORS[i], lw=0.7), bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=ROW_COLORS[i], lw=0.4))
    ax.annotate("顶面（从 Y 脊落下来的斜面）", xy=(S * k * (tiers_r[0][0] - 0.03), S * k * (t / 2 + CREST * 0.4)), xytext=(0.13 * S * k, 0.115 * S * k), fontsize=6, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    ax.annotate(f"D06 竖壁（≈{2 * wh / t:.2f}×厚，占位）", xy=(S * k * hw, S * k * wh * 0.5), xytext=(0.16 * S * k, 0.03 * S * k), fontsize=6, color=INK, arrowprops=dict(arrowstyle="->", color=INK, lw=0.7))
    # brick layout sketch: three rows of scales offset by half a scale (plan view of the band, unrolled)
    bx0, by0, L, H = 0.115 * S * k, 0.045 * S * k, 0.018 * S * k, 0.011 * S * k
    for r in range(3):
        for c in range(5):
            x = bx0 + (c + (0.5 if r % 2 else 0.0)) * L
            ax.add_patch(Polygon([(x, by0 + r * H), (x + L, by0 + r * H), (x + L, by0 + (r + 1) * H), (x, by0 + (r + 1) * H)], closed=True, fill=True, fc=("#f2f2f2" if (c + r) % 2 else "#d0d0d0"), ec=ROW_COLORS[2 - r], lw=0.6))
    ax.text(bx0, by0 + 3 * H + 0.004 * S * k, "俯视展开：三排鳞错半鳞、相邻一亮一暗（占位）", fontsize=5.5, color=INK)
    ax.text(-0.01 * S * k, -0.012 * S * k, "用户 10:40“多层龙鳞纹过渡”；与盖缘同一构造。排数 3 占位（≥2 排可见）；宽/斜度占位", fontsize=5.5, color=HIDDEN)


def detail_notch(ax):
    """Detail D: notch between the 90° and 210° blades, bisector rotated to +y. 3x scale."""
    k = 3.0
    setup(ax, "DETAIL D (3:1) 缺口：两叶边各自止于盖圈，中间留出露盖间隔\n虚线 = 作废的 v6（相邻弧相交成 V）", (-0.42 * S * k, 0.42 * S * k), (0.28 * S * k, 0.92 * S * k))
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
    v6 = v6_half()
    v6full = v6 + [(x, -y) for x, y in reversed(v6) if y > 1e-9]
    for blade_rot in (30, 150):  # blade axes at ±60° around the +y bisector (90° ± 60°)
        poly(ax, to_local(full, blade_rot), lw=1.4, close=False)
        poly(ax, to_local(v6full, blade_rot), lw=0.7, color=ALT, ls=(0, (4, 2)), close=False)
    # cap
    circle(ax, CAP * S * k, lw=1.2)
    rim = [(CAP * TABLE * math.cos(2 * math.pi * j / N_SECTOR + math.pi / 2), CAP * TABLE * math.sin(2 * math.pi * j / N_SECTOR + math.pi / 2)) for j in range(N_SECTOR)]
    poly(ax, [(x * S * k, y * S * k) for x, y in rim], lw=0.8)
    for x, y in rim:
        ax.plot([0.0, x * S * k], [0.0, y * S * k], color=INK, lw=0.3)
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
    apt = (0.0, math.hypot(*apex) * S * k)
    ax.plot([apt[0]], [apt[1]], marker="x", ms=5, color=ALT)
    rA = to_local([root_point()], 30)[0]
    rB = to_local([root_point()], 150)[0]
    for r_ in (rA, rB):
        ax.plot([r_[0]], [r_[1]], marker="o", ms=3.5, color=INK)
    # exposed cap arc between the two root points
    from matplotlib.patches import Arc as _Arc
    a0 = 90.0 - (60.0 - RB["meetsCapAtPolarDeg"])
    a1 = 90.0 + (60.0 - RB["meetsCapAtPolarDeg"])
    ax.add_patch(_Arc((0, 0), 2 * CAP * S * k * 1.04, 2 * CAP * S * k * 1.04, angle=0, theta1=a0, theta2=a1, color=DIM, lw=0.8))
    ax.text(0.0, CAP * S * k * 1.075, f"露盖 ≈{RB['exposedCapArcPerNotchDeg']:.0f}°", fontsize=6, color=DIM, ha="center")
    (xb, yb), cb, rb = blend_geometry()
    bstart = to_local([(xb, yb)], 30)[0]
    ax.plot([bstart[0]], [bstart[1]], marker="|", ms=6, color=HIDDEN)
    leader(ax, apt, "v6：两弧相交成 V（红箭头处）— 作废", (-0.41 * S * k, 0.88 * S * k), color=ALT, fs=6)
    leader(ax, rA, f"叶边止于盖圈 {RB['meetsCapAtPolarDeg']:.0f}°；根部内收弧 R≈{rb:.2f} R\n（起于 ≈{RB['startPolarDeg']:.0f}°），与盖圈切线夹 ≈{RB['angleToCapTangentDeg']:.0f}°", (0.02 * S * k, 0.88 * S * k), fs=6)
    leader(ax, (0.0, CAP * TABLE * S * k), f"D01 盘缘 {TABLE:.2f}×盖 · D02 冠环 {N_WEDGE} 楔 · D09 缺口内冠环+裙+暗缝外露", (-0.41 * S * k, 0.31 * S * k), fs=6)


def detail_cap(ax):
    """Detail E: half section of the cap top, adopted (E1) and alternative (E2) readings."""
    k = 3.0
    setup(ax, "DETAIL E (3:1) 盖顶半剖（过扇区中线）— 请二选一\nE1 实线：盘缘最高 + 三层外低  E2 虚线：整顶内凹", (-0.02 * S * k, 0.62 * S * k), (-0.06 * S * k, 0.26 * S * k))
    base = 0.0
    top = CAP_SIDE_H
    crown_h = 0.45 * CAP_SIDE_H
    dish_d = CAP * TABLE * math.tan(math.radians(DISH_SLOPE_DEG))
    prof = cap_edge_profile(top)
    e1 = [(0.0, base), (CAP, base)] + [(r, z) for r, z in reversed(prof)] + [(0.0, top - dish_d)]
    poly(ax, [(x * S * k, y * S * k) for x, y in e1], lw=1.3, hatch="\\\\\\\\")
    for i in range(3):
        (r0, z0), (r1, z1) = prof[i], prof[i + 1]
        ax.plot([S * k * r0, S * k * r1], [S * k * z0, S * k * z1], color=TIER_COLORS[i], lw=3.5, solid_capstyle="butt", zorder=5)
    # E2 alternative: ring slopes inward-down from the rim to the disc, disc flat/dished lower
    e2 = [(CAP, top), (CAP * TABLE, top - crown_h * 0.8), (0.0, top - crown_h * 0.8 - dish_d)]
    ax.plot([x * S * k for x, _ in e2], [y * S * k for _, y in e2], color=ALT, lw=1.0, ls=(0, (4, 2)))
    ax.plot([CAP * S * k] * 2, [(top - crown_h) * S * k, top * S * k], color=ALT, lw=1.0, ls=(0, (4, 2)))
    # concentric turning marks on the dish
    dim(ax, (CAP * TABLE * S * k, top * S * k), (CAP * S * k, top * S * k), 0.02 * S * k, f"三层总径向 {CAP * (1 - TABLE):.3f} R", fs=6)
    dim(ax, (CAP * S * k, prof[-1][1] * S * k), (CAP * S * k, top * S * k), -0.10 * S * k, f"三层总落差 ≈{top - prof[-1][1]:.3f} R（占位）", fs=6)
    dim(ax, (0.0, (top - dish_d) * S * k), (0.0, top * S * k), -0.52 * S * k, f"凹深 ≈{dish_d:.3f} R（{DISH_SLOPE_DEG:.0f}° 占位）", color=ALT, fs=6)
    leader(ax, (CAP * TABLE * S * k, top * S * k), "E1 盘缘 = 最高点（f0077 远侧冠环被压缩\n⇒ 冠环面背向相机 ⇒ 向外向下）", (0.02 * S * k, 0.235 * S * k), fs=6)
    leader(ax, (CAP * TABLE * S * k, (top - crown_h * 0.8) * S * k), "E2 备选：冠环 14 楔向内向下，整个顶面成碟形\n（若“14 片有内凹效果”指的是冠环）", (0.06 * S * k, -0.04 * S * k), color=ALT, fs=6)
    leader(ax, (0.0, (top - dish_d) * S * k), f"D01 {N_SECTOR} 等分平面扇区凹棱锥（拇指位）\n各扇区为平面，剖面为直线；深度未知", (0.02 * S * k, 0.06 * S * k), color=ALT, fs=6)


def profile_table(ax):
    setup(ax, "实测叶边半宽（4 条干净边）vs v7+ 凸弧+根部内收模型", (0, 10), (0, 10))
    xs = ENV["x"]
    per = ENV["perSide"]
    rows = [("x/R", "实测均值", "v7 模型", "差", "v5 直边模型")]
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
            ax.text(0.3 + j * 2.0, y, txt, fontsize=5.5, color=col, family=FONT)
    ax.text(0.3, 0.35, f"弧拟合 rms 0.0006–0.0010 R，直线 0.011–0.015 R（f0077/f0078）。R_s={RS:.3f} R，圆心 (0, −{CY:.2f} R)；根部 x<{XB:.2f} 内收弧 R {RB_R:.2f} R 止于盖圈 {RB['meetsCapAtPolarDeg']:.0f}°（4 边实测 51–53°）；叶尖圆角 {RT:.2f} R。", fontsize=6.5, color=ALT, family=FONT)


def main() -> None:
    fig = plt.figure(figsize=(16.5, 14.0), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.09, 0.50, 0.88])
    ax_aa = fig.add_axes([0.53, 0.80, 0.46, 0.17])
    ax_cc = fig.add_axes([0.53, 0.585, 0.29, 0.20])
    ax_ff = fig.add_axes([0.825, 0.585, 0.165, 0.20])
    ax_gg = fig.add_axes([0.53, 0.355, 0.225, 0.215])
    ax_dd = fig.add_axes([0.765, 0.355, 0.225, 0.215])
    ax_ee = fig.add_axes([0.53, 0.13, 0.225, 0.21])
    ax_hh = fig.add_axes([0.765, 0.13, 0.225, 0.21])
    plan(ax_plan)
    section_aa(ax_aa)
    section_cc(ax_cc)
    section_ff(ax_ff)
    detail_edge(ax_gg)
    detail_notch(ax_dd)
    detail_cap(ax_ee)
    detail_blade_edge(ax_hh)
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD v11 (v10 + multi-row dragon-scale transition on every blade edge, same construction as the cap edge; profile table moved to history) · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, f"UNITS: R 比例；mm 仅 85 mm user-authorized-provisional · 叶边凸弧 R {RS:.2f} R、圆心距 {CY:.2f} R；根部内收弧 R {RB_R:.2f} R 止于盖圈 {RB['meetsCapAtPolarDeg']:.0f}°，缺口露盖 {RB['exposedCapArcPerNotchDeg']:.0f}° · 叶尖 90°+{RT:.2f} R · 冠环 {N_WEDGE} 楔 · 盘 {N_SECTOR} 等分扇区凹棱锥、{TABLE:.2f}×盖、凹深未知 · 叶顶 Y 形隆起脊（脊高 {CREST:.3f} R 占位）· 盖缘三层过渡 冠 {CAP_TIERS[0]['slopeDeg']}°/裙 {CAP_TIERS[1]['slopeDeg']}°/{CAP_TIERS[2]['slopeDeg']}°（占位）· 叶边 {len(EDGE_TIERS)} 排鳞 {BEVEL_W:.2f} R 宽（排数/宽/斜度占位）· 竖壁 ≈{2 * wall_half(BODY_T) / BODY_T:.2f}×厚 · 凹坑深/缝宽未知 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE surface-detail-spec.json (planformProfile.parametric v7, D01 v8, D04 v9, D02/D03 v10, D05/D06 v11) ← traces / arc fits / disc unwrap / user drawings ← f0077 f0078 f0108 f0132 → draw_geeone_reference_cad_v11.py · {date.today().isoformat()} · v1–v10 保留为历史", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video-v11.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video-v11.png")


if __name__ == "__main__":
    main()
