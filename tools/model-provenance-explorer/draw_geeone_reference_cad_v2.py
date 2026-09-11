"""Reference CAD v2 for the GEEONE dragon-scale tri-spinner: v1 outline plus the
surface details D01-D10 from surface-detail-spec.json (Gate 02 rev-006).

Plan view: cap table / crown zigzag / faceted skirt polygon, blade plateau,
edge scale bands (6 facets per edge), tip ridge, root pockets with chamfer.
Sections: A-A along a blade (plateau, ridge, pocket, cap two-row side),
C-C across a blade (plateau, alternating scale facets, wall).
Details: developed scale band, developed cap side (crown + skirt).
Ratios of R; millimetres only as the 85 mm user-authorized-provisional label.
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
from matplotlib.patches import Polygon  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_unified_tri_spinner_cad import ALT, CENTER, DIM, FONT, HIDDEN, INK, angle_dim, centerlines, circle, dim, leader, poly, setup  # noqa: E402
import draw_geeone_reference_cad as v1  # noqa: E402

REPO = v1.REPO
A02 = v1.A02
SPEC = json.loads((A02 / "surface-detail-spec.json").read_text(encoding="utf-8"))
D = {d["id"]: d for d in SPEC["details"]}
S = v1.S
R, CAP, TABLE = v1.R, v1.CAP, v1.TABLE
TIP_ANGLE, TIP_FILLET = v1.TIP_ANGLE, v1.TIP_FILLET
BEVEL_W = D["UTS-D05"]["params"]["bandWidthToR"]
FACETS_PER_EDGE = D["UTS-D05"]["params"]["facetsPerEdge"]
N_WEDGE = D["UTS-D02"]["params"]["wedges"]
N_SKIRT = D["UTS-D03"]["params"]["facets"]
POCKET_APEX = D["UTS-D08"]["params"]["apexRadiusToR"]
POCKET_HALF = D["UTS-D08"]["params"]["halfAngleAtCapDeg"]
BODY_T = v1.BODY_T
WALL_H = D["UTS-D06"]["params"]["wallToThickness"]
CAP_SIDE_H = D["UTS-D03"]["params"]["sideHeightToR"]
PHI = math.radians(TIP_ANGLE / 2)
VT = R + TIP_FILLET * (1 / math.sin(PHI) - 1)  # virtual sharp tip


def sc(x, y):
    return (S * x, S * y)


def rot(pts, deg):
    return v1.rot(pts, deg)


def edge_point(t):
    """Upper straight edge, t = distance inward from the virtual tip."""
    return (VT - t * math.cos(PHI), t * math.sin(PHI))


def plateau_edge_point(t):
    nx, ny = math.sin(PHI), math.cos(PHI)
    x, y = edge_point(t)
    return (x - BEVEL_W * nx, y - BEVEL_W * ny)


def plan(ax):
    setup(ax, "REFERENCE PLAN v2  顶视 + 表面细节 D01–D10（比例单位 R；括号内 mm 为 85 provisional 换算）", (-1.5 * S, 1.5 * S), (-1.42 * S, 1.36 * S))
    centerlines(ax, 1.2 * S)
    circle(ax, R * S, lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))
    half = v1.blade_outline_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    t_tan = TIP_FILLET / math.tan(PHI)
    t_shoulder = None
    for t in [k * 0.005 for k in range(int(t_tan / 0.005) + 1, 400)]:
        x, y = edge_point(t)
        if math.hypot(x, y) <= v1.SHOULDER_R:
            t_shoulder = t
            break
    corner_t = BEVEL_W / math.sin(PHI)  # plateau corner distance from the virtual tip along the axis, expressed as edge t
    for ang in (90, 210, 330):
        poly(ax, rot(full, ang), lw=1.3, close=False)  # outline (D07 tip, straight edges, root fillets)
        # D04 plateau edge parallel to the straight edge; D05 facet boundaries across the band
        plateau_pts = [plateau_edge_point(t) for t in (corner_t, t_shoulder)]
        for s_ in (1, -1):
            seg = [(x, s_ * y) for x, y in plateau_pts]
            poly(ax, rot(seg, ang), lw=0.7, color=HIDDEN, close=False)
            for k in range(FACETS_PER_EDGE + 1):
                t = corner_t + (t_shoulder - corner_t) * k / FACETS_PER_EDGE
                a_, b_ = edge_point(t), plateau_edge_point(t)
                # alternate the boundary skew slightly so facets read as scales
                skew = 0.012 * (1 if k % 2 == 0 else -1)
                b_ = (b_[0] + skew * math.cos(PHI), b_[1] - skew * math.sin(PHI))
                poly(ax, rot([(a_[0], s_ * a_[1]), (b_[0], s_ * b_[1])], ang), lw=0.5, color=INK, close=False)
        # plateau corner -> tip ridge (D07)
        pc = (VT - corner_t * math.cos(PHI), 0.0)
        poly(ax, rot([pc, (R - TIP_FILLET * 0.3, 0.0)], ang), lw=0.6, color=HIDDEN, close=False)
        # root fillet zone: plateau flanks run to the cap (D08 flanks)
        fl = plateau_edge_point(t_shoulder)
        root_pt = (CAP * math.cos(math.radians(v1.ROOT_HALF_SPAN - 4)), CAP * math.sin(math.radians(v1.ROOT_HALF_SPAN - 4)))
        for s_ in (1, -1):
            poly(ax, rot([(fl[0], s_ * fl[1]), (root_pt[0], s_ * root_pt[1])], ang), lw=0.7, color=HIDDEN, close=False)
        # D08 pocket: outer triangle + inner chamfer triangle
        pk = [(POCKET_APEX, 0.0), (CAP * math.cos(math.radians(POCKET_HALF)), CAP * math.sin(math.radians(POCKET_HALF))), (CAP * math.cos(math.radians(POCKET_HALF)), -CAP * math.sin(math.radians(POCKET_HALF)))]
        ax.add_patch(Polygon(rot(pk, ang), closed=True, fill=True, fc="#e6e6e6", ec=INK, lw=0.9, zorder=2))
        inner = [(POCKET_APEX - 0.035, 0.0), (CAP * math.cos(math.radians(POCKET_HALF - 3)) + 0.01, (CAP + 0.01) * math.sin(math.radians(POCKET_HALF - 3))), (CAP * math.cos(math.radians(POCKET_HALF - 3)) + 0.01, -(CAP + 0.01) * math.sin(math.radians(POCKET_HALF - 3)))]
        ax.add_patch(Polygon(rot(inner, ang), closed=True, fill=True, fc="#9a9a9a", ec=INK, lw=0.6, hatch="....", zorder=3))
    # cap: D03 skirt polygon (outer), D02 crown zigzag, D01 table
    skirt = [(CAP * math.cos(2 * math.pi * (j + 0.5) / N_SKIRT), CAP * math.sin(2 * math.pi * (j + 0.5) / N_SKIRT)) for j in range(N_SKIRT)]
    poly(ax, [sc(*p) for p in skirt], lw=1.3)
    for j in range(N_WEDGE):
        a_in = 2 * math.pi * j / N_WEDGE
        a_out = 2 * math.pi * (j + 0.5) / N_WEDGE
        i0 = sc(CAP * TABLE * math.cos(a_in), CAP * TABLE * math.sin(a_in))
        i1 = sc(CAP * TABLE * math.cos(a_in + 2 * math.pi / N_WEDGE), CAP * TABLE * math.sin(a_in + 2 * math.pi / N_WEDGE))
        o = sc(CAP * math.cos(a_out), CAP * math.sin(a_out))
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=0.45, zorder=4)
    circle(ax, CAP * TABLE * S, lw=0.9)
    # 85 mm provisional label
    dim(ax, (-R * S, -1.27 * S), (R * S, -1.27 * S), 0.0, "2R = 85 mm  user-authorized-provisional（非 measured；仅供未来 Gate 03–05）", ext=False)
    for xx in (-R * S, R * S):
        ax.plot([xx, xx], [-1.27 * S, -0.35 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    # callouts
    leader(ax, sc(0.0, CAP * TABLE * 0.55), "D01 平盘 0.80×盖，同心车削纹", sc(-1.47, 0.95))
    leader(ax, sc(CAP * 0.9 * math.cos(math.radians(150)), CAP * 0.9 * math.sin(math.radians(150))), f"D02 冠环 {N_WEDGE}±2 三角楔（尖端里外交替）", sc(-1.47, 0.62))
    leader(ax, sc(CAP * math.cos(math.radians(195)), CAP * math.sin(math.radians(195))), f"D03 盖裙 {N_SKIRT}±4 平面（多边形，非圆柱）", sc(-1.47, 0.30))
    leader(ax, rot([(0.72, 0.02)], 330)[0], "D04 平台（平面）", sc(0.95, -0.42))
    leader(ax, rot([(0.78, 0.115)], 330)[0], f"D05 倒角鳞面带 ≈{BEVEL_W:.2f} R，每边 {FACETS_PER_EDGE}±1 平面，倾角交替", sc(0.62, -0.95))
    leader(ax, rot([(R, 0.0)], 330)[0], f"D07 叶尖 {TIP_ANGLE:.0f}°±3，圆角 ≈{TIP_FILLET:.3f} R（≈{TIP_FILLET * S:.1f} mm）", sc(0.62, -1.15))
    leader(ax, rot([(POCKET_APEX - 0.05, 0.0)], 210)[0], f"D08 叶根三角凹坑：开口朝盖，外壁陡斜切；尖端 r≈{POCKET_APEX:.2f} R；深度未知", sc(-1.47, -1.05))
    leader(ax, sc(CAP * 1.02 * math.cos(math.radians(30)), CAP * 1.02 * math.sin(math.radians(30))), f"D09 缺口露盖弧 ≈{D['UTS-D09']['params']['exposedCapArcPerNotchDeg']}°，暗缝宽未知", sc(0.62, 1.20))
    leader(ax, rot([(v1.SHOULDER_R, 0.30)], 90)[0], f"肩部 r≈{v1.SHOULDER_R:.2f} R：直边转为凹收贴盖圈", sc(-1.47, 1.24))
    ax.text(-1.47 * S, -1.38 * S, "细线 = 平台边界 / 鳞面分界；灰三角 = 凹坑（内三角 = 斜切外壁）；D06 竖壁与 D10 底面见剖面", fontsize=6.5, color=HIDDEN)


def section_aa(ax):
    setup(ax, "SECTION A—A v2  过叶片轴（右叶片，左缺口）", (-1.25 * S, 1.3 * S), (-0.44 * S, 0.48 * S))
    ax.plot([-1.25 * S, 1.3 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    corner_x = VT - BEVEL_W / math.sin(PHI)
    ridge_tip_z = wall / 2 * 0.6
    body = [sc(CAP, t / 2), sc(POCKET_APEX, t / 2), sc(corner_x, t / 2), sc(R - 0.01, ridge_tip_z), sc(R, ridge_tip_z * 0.8), sc(R, -ridge_tip_z * 0.8), sc(R - 0.01, -ridge_tip_z), sc(corner_x, -t / 2), sc(POCKET_APEX, -t / 2), sc(CAP, -t / 2)]
    poly(ax, body, lw=1.2, hatch="////")
    # pocket recess (depth unknown -> dashed, drawn at 35% thickness as a placeholder)
    pd = 0.35 * t
    for sgn in (1, -1):
        rec = [sc(CAP, sgn * t / 2), sc(CAP, sgn * (t / 2 - pd)), sc(POCKET_APEX - 0.04, sgn * (t / 2 - pd)), sc(POCKET_APEX, sgn * t / 2)]
        ax.add_patch(Polygon(rec, closed=True, fill=True, fc="white", ec=ALT, lw=0.9, ls=(0, (4, 2)), zorder=4))
    poly(ax, [sc(-CAP, t / 2 * 0.55), sc(-CAP * 1.05, t / 2 * 0.55), sc(-CAP * 1.05, -t / 2 * 0.55), sc(-CAP, -t / 2 * 0.55)], lw=1.0, hatch="////")
    # caps: table + crown slope + vertical faceted skirt
    for sgn in (1, -1):
        top = t / 2 + CAP_SIDE_H
        crown_h = 0.55 * CAP_SIDE_H
        cap_pts = [sc(-CAP * TABLE, sgn * top), sc(CAP * TABLE, sgn * top), sc(CAP, sgn * (top - crown_h)), sc(CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (top - crown_h))]
        poly(ax, cap_pts, lw=1.2, hatch="\\\\\\\\")
        # skirt facet ticks
        for xx in (CAP, -CAP):
            ax.plot([xx * S, xx * S], [sgn * (t / 2 + 0.005) * S, sgn * (top - crown_h) * S], color=DIM, lw=2.0, zorder=6)
    dim(ax, sc(corner_x - 0.05, -t / 2), sc(corner_x - 0.05, t / 2), -0.62 * S, f"厚 ≈{BODY_T:.2f} R")
    dim(ax, sc(CAP * 0.5, t / 2), sc(CAP * 0.5, t / 2 + CAP_SIDE_H), -0.95 * S, f"D03 盖侧 ≈{CAP_SIDE_H:.2f} R")
    dim(ax, sc(R, -ridge_tip_z * 0.8), sc(R, ridge_tip_z * 0.8), -0.10 * S, "D06/D07 叶尖")
    leader(ax, sc(POCKET_APEX - 0.02, t / 2 - pd), "D08 凹坑深度未知（虚线为占位，非量得）", sc(-1.22, -0.40), color=ALT)
    leader(ax, sc((corner_x + R) / 2, t / 2 - (t / 2 - ridge_tip_z) * 0.5), "D07 脊：平台角→叶尖，两侧鳞面带在此交汇", sc(-1.22, 0.42))
    leader(ax, sc(CAP, t / 2 + 0.03), "D03 盖裙竖直刻面 + D02 冠环斜面（两排）", sc(0.30, 0.44))


def section_cc(ax):
    setup(ax, "SECTION C—C v2  叶片横向剖面（中段）", (-0.55 * S, 0.55 * S), (-0.22 * S, 0.26 * S))
    ax.plot([-0.55 * S, 0.55 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    # half width at mid blade (x ~ 0.72 R)
    hw = (VT - 0.72) * math.tan(PHI)
    pw = hw - BEVEL_W / math.cos(PHI)
    # two alternating facets across the band (schematic: split the bevel into two planes with different slopes)
    mid_w = (hw + pw) / 2
    mid_z = (t / 2 + wall / 2) / 2 + 0.012
    sec = [sc(-hw, -wall / 2), sc(hw, -wall / 2), sc(hw, wall / 2), sc(mid_w, mid_z), sc(pw, t / 2), sc(-pw, t / 2), sc(-mid_w, mid_z - 0.02), sc(-hw, wall / 2)]
    sec_bottom = [sc(hw, -wall / 2), sc(mid_w, -mid_z + 0.02), sc(pw, -t / 2), sc(-pw, -t / 2), sc(-mid_w, -mid_z), sc(-hw, -wall / 2)]
    poly(ax, sec[1:] + sec_bottom[1:-1], lw=1.2, hatch="////")
    dim(ax, sc(-hw, -wall / 2), sc(hw, -wall / 2), -0.05 * S, f"宽 ≈{2 * hw:.2f} R（x=0.72R）")
    dim(ax, sc(hw, -wall / 2), sc(hw, wall / 2), -0.06 * S, f"D06 竖壁 ≈{WALL_H:.2f}×厚")
    dim(ax, sc(pw, t / 2), sc(hw, wall / 2), 0.05 * S, f"D05 带宽 ≈{BEVEL_W:.2f} R")
    leader(ax, sc(mid_w, mid_z), "D05 相邻鳞面倾角交替（示意两面）", sc(0.05, 0.24))
    leader(ax, sc(0.0, t / 2), "D04 平台", sc(-0.52, 0.24))
    leader(ax, sc(0.0, -t / 2), "D10 底面镜像", sc(-0.52, -0.20))


def detail_scales(ax):
    setup(ax, "DETAIL D  叶边鳞面带展开（每边 6±1 平面，倾角交替）", (-0.02 * S, 0.62 * S), (-0.02 * S, 0.14 * S))
    L = 0.55
    band = BEVEL_W
    n = FACETS_PER_EDGE
    for k in range(n):
        x0, x1 = L * k / n, L * (k + 1) / n
        skew = 0.012 * (1 if k % 2 == 0 else -1)
        quad = [sc(x0, 0.0), sc(x1, 0.0), sc(x1 + skew, band), sc(x0 - skew * (1 if k > 0 else 0), band)]
        ax.add_patch(Polygon(quad, closed=True, fill=True, fc="#dddddd" if k % 2 == 0 else "#bfbfbf", ec=INK, lw=0.8))
    ax.plot([0, L * S], [0, 0], color=INK, lw=1.4)
    ax.plot([0, L * S], [band * S, band * S], color=INK, lw=1.0)
    ax.text(0.0, -0.018 * S, "竖壁上沿（D06）", fontsize=7, color=HIDDEN)
    ax.text(0.0, (band + 0.012) * S, "平台边（D04）", fontsize=7, color=HIDDEN)
    dim(ax, sc(L, 0.0), sc(L, band), -0.03 * S, f"{band:.2f} R")
    dim(ax, sc(0.0, band), sc(L / n, band), 0.03 * S, f"{L / n:.3f} R/面")
    ax.text(0.30 * S, 0.11 * S, "明暗交替 = 相邻面绕带中线 ±5–10°（估计）", fontsize=7, color=ALT)


def detail_cap_side(ax):
    setup(ax, "DETAIL E  盖侧两排刻面展开（D02 冠环 + D03 盖裙）", (-0.02 * S, 0.62 * S), (-0.02 * S, 0.20 * S))
    n = 6
    pitch = 2 * math.pi * CAP / N_WEDGE  # arc pitch at the rim
    crown_h = 0.55 * CAP_SIDE_H
    skirt_h = CAP_SIDE_H - crown_h
    for k in range(n):
        x0, x1 = pitch * k, pitch * (k + 1)
        # skirt quad
        ax.add_patch(Polygon([sc(x0, 0), sc(x1, 0), sc(x1, skirt_h), sc(x0, skirt_h)], closed=True, fill=True, fc="#d8d8d8", ec=INK, lw=0.8))
        # crown triangles: outward tip at (x0+x1)/2 on the rim line, inward at table line alternating
        apex_up = ((x0 + x1) / 2, skirt_h + crown_h)
        ax.add_patch(Polygon([sc(x0, skirt_h), sc(x1, skirt_h), sc(*apex_up)], closed=True, fill=True, fc="#c4c4c4", ec=INK, lw=0.8))
        if k < n - 1:
            ax.add_patch(Polygon([sc(x1, skirt_h), sc(*apex_up), sc(x1 + pitch / 2, skirt_h + crown_h)], closed=True, fill=True, fc="#ececec", ec=INK, lw=0.8))
    ax.plot([0, pitch * n * S], [(skirt_h + crown_h) * S] * 2, color=INK, lw=1.2)
    ax.text(0.0, (skirt_h + crown_h + 0.012) * S, "平盘边（D01）", fontsize=7, color=HIDDEN)
    ax.text(0.0, -0.018 * S, "盖底 / 暗缝（D09）", fontsize=7, color=HIDDEN)
    dim(ax, sc(pitch * n, 0), sc(pitch * n, skirt_h), -0.03 * S, "裙")
    dim(ax, sc(pitch * n, skirt_h), sc(pitch * n, skirt_h + crown_h), -0.03 * S, "冠")
    dim(ax, sc(0, 0), sc(pitch, 0), -0.03 * S, f"{360 / N_WEDGE:.0f}°")
    ax.text(0.25 * S, 0.18 * S, "冠环/裙高度比 ≈55/45（估计，f0176/f0148）", fontsize=7, color=ALT)


def main() -> None:
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.10, 0.54, 0.86])
    ax_aa = fig.add_axes([0.57, 0.60, 0.42, 0.36])
    ax_cc = fig.add_axes([0.57, 0.36, 0.42, 0.22])
    ax_d = fig.add_axes([0.57, 0.09, 0.20, 0.24])
    ax_e = fig.add_axes([0.79, 0.09, 0.20, 0.24])
    plan(ax_plan)
    section_aa(ax_aa)
    section_cc(ax_cc)
    detail_scales(ax_d)
    detail_cap_side(ax_e)
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD v2 (surface details D01–D10) · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, "UNITS: R（叶尖半径）比例；mm 仅 85 mm user-authorized-provisional 标签 · 所有数值为视频帧估计（置信度见 surface-detail-spec.json）· 凹坑深度、缝宽、倒角各面角度未知 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE surface-detail-spec.json + frame-measurements.json → draw_geeone_reference_cad_v2.py · {date.today().isoformat()} · v1 保留为历史", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video-v2.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video-v2.png")


if __name__ == "__main__":
    main()
