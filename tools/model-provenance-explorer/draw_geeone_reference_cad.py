"""Gate 02 reference CAD for the GEEONE dragon-scale tri-spinner, drawn from the
frame measurements in `evidence/02-analysis/rev-006/frame-measurements.json`.

Everything is in ratios of the tip-circle radius R. The only millimetre value
is the width label, which is the user-authorized-provisional 85 mm (never
"measured"). Confidence is printed next to every dimension.
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

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
A02 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006"
MEAS = A02 / "frame-measurements.json"
WIDTH_PROVISIONAL_MM = 85.0  # user-authorized-provisional (controller instruction 2026-09-05 23:12); scope: future Gate 03-05 only

# Reference estimates (ratios of R = tip-circle radius). Source frames in brackets.
R = 1.0
CAP = 0.50        # cap outer radius / R      [f0077, f0078 silhouette; photo geeone-02 gave 0.536]
TABLE = 0.80      # table radius / cap radius [f0077, f0078 variance boundary; photo 0.797]
TIP_ANGLE = 67.0  # deg                       [f0077, f0078 straight-edge fit on the two near tips]
TIP_FILLET = 0.045  # / R                     [f0077, f0078 circle fit]
ROOT_HALF_SPAN = 32.0  # deg blade half-span at the cap [exposed cap arc ~56 deg per notch]
SHOULDER_R = 0.68  # / R, where the straight edge starts curving into the root [visual, low confidence]
POCKET_APEX_R = 0.70  # / R                   [f0077 4x zoom, visual]
POCKET_HALF_DEG = 14.0  # half angle of the pocket triangle at the cap [visual]
BEVEL_W = 0.07    # / R bevel band width mid-blade [visual]
BODY_T = 0.17     # body thickness / R        [f0226 profile 50 px vs ~290 px tip radius, low confidence]
CAP_SIDE_H = 0.14  # cap side (skirt+crown) above the blade top / R [f0226, low confidence]
WALL_H = 0.45     # vertical wall / body thickness [f0164, f0226 visual]


def blade_outline_half():
    """Half outline (y >= 0) of one blade in R units, blade axis +x.
    tip fillet -> straight edge -> concave root fillet -> cap circle."""
    phi = math.radians(TIP_ANGLE / 2)
    vt = R + TIP_FILLET * (1 / math.sin(phi) - 1)  # virtual sharp tip
    pts = []
    # tip fillet from the axis up to the tangent point
    cx = R - TIP_FILLET
    a0 = math.pi / 2 - phi
    for k in range(7):
        a = a0 * k / 6
        pts.append((cx + TIP_FILLET * math.cos(a), TIP_FILLET * math.sin(a)))
    # straight edge from the tangent point inward to the shoulder radius
    t_tan = TIP_FILLET / math.tan(phi)
    def edge(t):
        return (vt - t * math.cos(phi), t * math.sin(phi))
    t = t_tan
    while True:
        x, y = edge(t)
        if math.hypot(x, y) <= SHOULDER_R:
            break
        pts.append((x, y))
        t += 0.02
    shoulder = edge(t)
    # concave root fillet: quadratic blend from the shoulder to the cap circle at ROOT_HALF_SPAN
    root = (CAP * math.cos(math.radians(ROOT_HALF_SPAN)), CAP * math.sin(math.radians(ROOT_HALF_SPAN)))
    ctrl = (shoulder[0] - 0.10, shoulder[1] + 0.02)  # pulls the curve inward-first (concave)
    for k in range(1, 9):
        s = k / 8
        u = 1 - s
        pts.append((u * u * shoulder[0] + 2 * u * s * ctrl[0] + s * s * root[0], u * u * shoulder[1] + 2 * u * s * ctrl[1] + s * s * root[1]))
    return pts  # tip -> root


S = WIDTH_PROVISIONAL_MM / 2.0  # drawing scale: 1 R = 42.5 provisional mm


def rot(pts, deg):
    a = math.radians(deg)
    return [(S * (x * math.cos(a) - y * math.sin(a)), S * (x * math.sin(a) + y * math.cos(a))) for x, y in pts]


def sc(x, y):
    return (S * x, S * y)


def plan(ax, meas):
    setup(ax, "REFERENCE PLAN  顶视（由视频帧 f0077/f0078 轮廓与 f0038/f0077 细节读出）  比例单位 R；括号内 mm = 85 mm provisional 换算", (-1.5 * S, 1.5 * S), (-1.4 * S, 1.36 * S))
    centerlines(ax, 1.2 * S)
    circle(ax, R * S, lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))
    half = blade_outline_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    for ang in (90, 210, 330):
        pts = rot(full, ang)
        poly(ax, pts, lw=1.3, close=False)
        # plateau (offset inward by bevel width along the straight edges) — schematic
        phi = math.radians(TIP_ANGLE / 2)
        vt = R + TIP_FILLET * (1 / math.sin(phi) - 1)
        corner = vt - BEVEL_W / math.sin(phi)
        plateau = [(corner, 0.0)]
        for t in (0.15, 0.30, 0.42):
            x, y = vt - t * math.cos(phi), t * math.sin(phi)
            nx, ny = math.sin(phi), math.cos(phi)
            plateau.append((x - BEVEL_W * nx, y - BEVEL_W * ny))
        plateau_full = plateau + [(x, -y) for x, y in reversed(plateau[1:])]
        poly(ax, rot(plateau_full, ang), lw=0.7, color=HIDDEN, close=False)
        # pocket triangle at the root (open toward the cap)
        pocket = [(POCKET_APEX_R, 0.0), (CAP * math.cos(math.radians(POCKET_HALF_DEG)), CAP * math.sin(math.radians(POCKET_HALF_DEG))), (CAP * math.cos(math.radians(POCKET_HALF_DEG)), -CAP * math.sin(math.radians(POCKET_HALF_DEG)))]
        ax.add_patch(Polygon(rot(pocket, ang), closed=True, fill=True, fc="#dddddd", ec=INK, lw=0.8, hatch="....", zorder=2))
    circle(ax, CAP * S, lw=1.3)
    circle(ax, CAP * TABLE * S, lw=0.9)
    # crown zigzag (24, count from f0077 ~ 24 +/- 2)
    for j in range(24):
        a_in = 2 * math.pi * j / 24
        a_out = 2 * math.pi * (j + 0.5) / 24
        ax.plot([S * CAP * TABLE * math.cos(a_in), S * CAP * math.cos(a_out)], [S * CAP * TABLE * math.sin(a_in), S * CAP * math.sin(a_out)], color=INK, lw=0.35)
        ax.plot([S * CAP * math.cos(a_out), S * CAP * TABLE * math.cos(a_in + 2 * math.pi / 24)], [S * CAP * math.sin(a_out), S * CAP * TABLE * math.sin(a_in + 2 * math.pi / 24)], color=INK, lw=0.35)

    s = meas["summary"]
    dim(ax, (-R * S, -1.25 * S), (R * S, -1.25 * S), 0.0, f"2R = {WIDTH_PROVISIONAL_MM:.0f} mm  user-authorized-provisional（非 measured；仅供未来 Gate 03–05）", ext=False)
    ax.plot([-R * S, -R * S], [-1.25 * S, -0.3 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    ax.plot([R * S, R * S], [-1.25 * S, -0.3 * S], color=DIM, lw=0.4, ls=(0, (3, 2)))
    leader(ax, sc(CAP * math.cos(math.radians(200)), CAP * math.sin(math.radians(200))), f"盖外径 {2 * CAP:.2f} R（视频 {s['capToTipRatio']['mean']:.3f}±{s['capToTipRatio']['std']:.3f}，照片 0.536）中置信", sc(-1.47, -0.62))
    leader(ax, sc(CAP * TABLE * math.cos(math.radians(160)), CAP * TABLE * math.sin(math.radians(160))), f"平盘 {TABLE:.2f}×盖（视频 {s['tableToCap']['mean']:.2f}，照片 0.797）高置信", sc(-1.47, 0.66))
    tip = rot([(R, 0.0)], 330)[0]
    angle_dim(ax, rot([(R + TIP_FILLET * (1 / math.sin(math.radians(TIP_ANGLE / 2)) - 1), 0.0)], 330)[0], 0.16 * S, 330 + 180 - TIP_ANGLE / 2, 330 + 180 + TIP_ANGLE / 2, f"{TIP_ANGLE:.0f}°±3（f0077/78 直边拟合）")
    leader(ax, tip, f"叶尖圆角 ≈{TIP_FILLET:.3f} R（≈{TIP_FILLET * S:.1f} mm @85 provisional）中置信", sc(0.62, -1.08))
    root = rot([(CAP * math.cos(math.radians(ROOT_HALF_SPAN)), CAP * math.sin(math.radians(ROOT_HALF_SPAN)))], 90)[0]
    leader(ax, root, f"叶根在盖圈上跨 ±{ROOT_HALF_SPAN:.0f}°；每缺口露盖弧 ≈{s['exposedCapArcPerNotchDeg']['mean']:.0f}°±{s['exposedCapArcPerNotchDeg']['std']:.0f}（透视未校正，低置信）", sc(-1.47, 1.26))
    leader(ax, rot([(SHOULDER_R * 0.98, 0.34)], 90)[0], f"肩部：直边在 r≈{SHOULDER_R:.2f} R 起向内凹收到盖圈（视觉，低置信）", sc(0.34, 1.26))
    leader(ax, rot([(POCKET_APEX_R * 0.9, 0.0)], 210)[0], f"叶根三角凹坑：开口朝盖，外壁斜切；尖端 r≈{POCKET_APEX_R:.2f} R；深度未知（f0077 4×）", sc(-1.47, -1.12))
    leader(ax, rot([(0.75, 0.13)], 330)[0], f"边缘倒角带宽 ≈{BEVEL_W:.2f} R，带内 3–4 个平面（“楔形过渡”，f0077/f0164）", sc(0.34, -0.84))
    ax.text(-1.47 * S, -1.36 * S, "细线 = 平台（plateau）边界示意；点状 = 凹坑；24 楔冠环 = 从 f0077 计数 24±2。", fontsize=6.5, color=HIDDEN)


def profile(ax, meas):
    setup(ax, "REFERENCE PROFILE  过叶片轴剖面示意（f0226 边视 + f0164 底视）  比例单位 R", (-1.25 * S, 1.3 * S), (-0.42 * S, 0.46 * S))
    ax.plot([-1.25 * S, 1.3 * S], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)))
    t = BODY_T
    wall = WALL_H * t
    body = [sc(CAP, t / 2), sc(0.62, t / 2), sc(R - 0.02, wall / 2), sc(R, wall / 2 * 0.6), sc(R, -wall / 2 * 0.6), sc(R - 0.02, -wall / 2), sc(0.62, -t / 2), sc(CAP, -t / 2)]
    poly(ax, body, lw=1.2, hatch="////")
    poly(ax, [sc(-CAP, t / 2 * 0.55), sc(-CAP * 1.05, t / 2 * 0.55), sc(-CAP * 1.05, -t / 2 * 0.55), sc(-CAP, -t / 2 * 0.55)], lw=1.0, hatch="////")
    for sgn in (1, -1):
        cap_pts = [sc(-CAP * TABLE, sgn * (t / 2 + CAP_SIDE_H)), sc(CAP * TABLE, sgn * (t / 2 + CAP_SIDE_H)), sc(CAP, sgn * (t / 2 + CAP_SIDE_H * 0.45)), sc(CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + 0.005)), sc(-CAP, sgn * (t / 2 + CAP_SIDE_H * 0.45))]
        poly(ax, cap_pts, lw=1.2, hatch="\\\\")
    dim(ax, sc(0.62, -t / 2), sc(0.62, t / 2), -0.62 * S, f"厚 ≈{t:.2f} R")
    dim(ax, sc(CAP * 0.5, t / 2), sc(CAP * 0.5, t / 2 + CAP_SIDE_H), -0.95 * S, f"盖侧 ≈{CAP_SIDE_H:.2f} R")
    dim(ax, sc(R, -wall / 2 * 0.6), sc(R, wall / 2 * 0.6), -0.10 * S, f"竖壁 ≈{WALL_H:.2f}×厚")
    leader(ax, sc(0.62, t / 2), "平台→倒角带→竖壁；倒角带内多平面（龙鳞）", sc(-1.22, 0.40))
    leader(ax, sc(-CAP * 1.02, 0.0), "缺口侧：盖圈外无机身", sc(-1.22, -0.30))
    ax.text(-1.22 * S, -0.40 * S, f"示意，±20%：厚≈{t * S:.0f} mm、盖侧≈{CAP_SIDE_H * S:.0f} mm（@85 provisional）；盖侧≈{CAP_SIDE_H / t:.1f}×机身厚，与此前“高出 1.5 mm”冲突，待裁决", fontsize=7, color=ALT)


def main() -> None:
    meas = json.loads(MEAS.read_text(encoding="utf-8"))
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax1 = fig.add_axes([0.02, 0.10, 0.55, 0.86])
    ax2 = fig.add_axes([0.58, 0.45, 0.41, 0.50])
    ax3 = fig.add_axes([0.58, 0.09, 0.41, 0.34])
    plan(ax1, meas)
    profile(ax2, meas)
    ax3.axis("off")
    s = meas["summary"]
    lines = [
        "来源链：Gate 01 rev-003 视频 geeone-source.mp4（小红书 指玩屋 6a5d80be…）→ ffmpeg fps=10 抽帧 → f0074–f0079 桌面平放段（黑底）",
        "方法：Otsu×0.55 阈值取剪影 → 三个缺口底落在盖冠环上 → 拟合椭圆 = 盖外圈 → 椭圆→圆校正倾斜（≈30°）→ 极坐标量测",
        f"结果（n={s['capToTipRatio']['n']} 帧）：盖/外接圆 {s['capToTipRatio']['mean']:.3f}±{s['capToTipRatio']['std']:.3f}；平盘/盖 {s['tableToCap']['mean']:.2f}；叶尖角 {s['tipIncludedAngleDeg']['mean']:.0f}°±{s['tipIncludedAngleDeg']['std']:.0f}（含一枚远端叶尖 84°，透视失真）；",
        f"        叶尖圆角 {s['tipFilletToTip']['mean']:.3f}±{s['tipFilletToTip']['std']:.3f} R；每缺口露盖弧 {s['exposedCapArcPerNotchDeg']['mean']:.0f}°±{s['exposedCapArcPerNotchDeg']['std']:.0f}（近端 70°、远端 36°，透视未校正）。",
        "未知项（无证据，不得填数）：所有 mm 绝对尺寸；凹坑深度与是否通孔；倒角带各平面角度；轴承型号；盖冠环精确楔数（24±2）；材质牌号。",
        f"85 mm = user-authorized-provisional（总控 2026-09-05 23:12），取代此前 65 mm provisional（追加式 supersession，历史保留）；适用范围仅说明可供未来 Gate 03–05。",
        "本图为 Gate 02 参考 CAD，不是建模合同；Gate 03–12 今晚不新增。",
    ]
    ax3.text(0.0, 1.0, "\n".join(lines), fontsize=8.2, va="top", ha="left", color=INK, family=FONT, linespacing=1.6, wrap=True)
    fig.text(0.012, 0.045, "GEEONE 龙鳞三叶 · REFERENCE CAD from video frames · metal-three-blade · Gate 02 rev-006", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, "UNITS: R（叶尖半径）比例；mm 仅 85 mm user-authorized-provisional 标签 · 所有数值为视频帧估计，置信度见标注 · 未推手机", fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE tools/model-provenance-explorer/measure_geeone_video_frames.py → frame-measurements.json → draw_geeone_reference_cad.py · {date.today().isoformat()}", fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))
    for ext in ("png", "pdf"):
        fig.savefig(A02 / f"reference-cad-from-video.{ext}", dpi=220, facecolor="white")
    plt.close(fig)
    print(A02 / "reference-cad-from-video.png")


if __name__ == "__main__":
    main()
