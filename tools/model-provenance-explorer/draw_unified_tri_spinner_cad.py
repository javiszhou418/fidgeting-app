"""Draw 2D CAD sheets for the unified tri-spinner from cad-geometry.json.

Sheet 1: plan view, axial section A-A, transverse section C-C, crown detail B.
Sheet 2: decision overlays (table ratio 0.70 vs 0.797, notch reading 1 vs 2).

    python3 tools/model-provenance-explorer/draw_unified_tri_spinner_cad.py [rev-004]
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Arc, Circle, Polygon  # noqa: E402

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
REV = sys.argv[1] if len(sys.argv) > 1 else "rev-004"
G06 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/06-geometry" / REV
DATA = G06 / "cad-geometry.json"
OUT_TMP = Path("/tmp/dragon-scale-gate02")

for candidate in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc"):
    if Path(candidate).exists():
        font_manager.fontManager.addfont(candidate)
        FONT = font_manager.FontProperties(fname=candidate).get_name()
        break
else:
    FONT = "DejaVu Sans"
plt.rcParams["font.family"] = [FONT, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#111111"
DIM = "#1f4fa3"
HIDDEN = "#555555"
CENTER = "#8a2b2b"
ALT = "#c2410c"
FS = 7.5


# ------------------------------------------------------------ primitives ---
def setup(ax, title, xlim, ylim):
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=10, fontweight="bold", color=INK, pad=4)


def poly(ax, pts, lw=1.1, color=INK, ls="-", close=True, hatch=None, fill=False):
    if close:
        pts = list(pts) + [pts[0]]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_joinstyle="miter", zorder=3)
    if hatch:
        ax.add_patch(Polygon(pts[:-1], closed=True, fill=fill, hatch=hatch, edgecolor=color, lw=0, zorder=2))


def circle(ax, r, lw=1.1, color=INK, ls="-", c=(0.0, 0.0)):
    ax.add_patch(Circle(c, r, fill=False, lw=lw, ec=color, ls=ls, zorder=3))


def centerlines(ax, r, c=(0.0, 0.0)):
    ax.plot([c[0] - r, c[0] + r], [c[1], c[1]], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)
    ax.plot([c[0], c[0]], [c[1] - r, c[1] + r], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)


def dim(ax, p1, p2, offset, text, side="auto", fs=FS, color=DIM, ext=True):
    """Linear dimension between p1 and p2, offset perpendicular by `offset` mm."""
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    a = (x1 + nx * offset, y1 + ny * offset)
    b = (x2 + nx * offset, y2 + ny * offset)
    if ext:
        for p, q in ((p1, a), (p2, b)):
            ax.plot([p[0], q[0] + nx * 0.6 * (1 if offset > 0 else -1)], [p[1], q[1] + ny * 0.6 * (1 if offset > 0 else -1)], color=color, lw=0.5, zorder=4)
    ax.annotate("", xy=a, xytext=b, arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0), zorder=5)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    angle = math.degrees(math.atan2(dy, dx))
    if angle > 90 or angle < -90:
        angle += 180
    ax.text(mx + nx * 0.9, my + ny * 0.9, text, fontsize=fs, color=color, ha="center", va="center", rotation=angle, rotation_mode="anchor", zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))


def leader(ax, target, text, textpos, fs=FS, color=DIM, arrow=True):
    ax.annotate(text, xy=target, xytext=textpos, fontsize=fs, color=color, ha="left", va="center", zorder=6,
                arrowprops=dict(arrowstyle="->" if arrow else "-", color=color, lw=0.7, shrinkA=0, shrinkB=1),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=0.4, alpha=0.9))


def dia(ax, r, angle_deg, text, c=(0.0, 0.0), fs=FS, color=DIM, textshift=2.0):
    a = math.radians(angle_deg)
    p1 = (c[0] - r * math.cos(a), c[1] - r * math.sin(a))
    p2 = (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
    ax.annotate("", xy=p1, xytext=p2, arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0), zorder=5)
    tx = c[0] + (r + textshift) * math.cos(a)
    ty = c[1] + (r + textshift) * math.sin(a)
    ax.text(tx, ty, text, fontsize=fs, color=color, ha="left" if math.cos(a) >= 0 else "right", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))


def angle_dim(ax, vertex, r, a0, a1, text, fs=FS, color=DIM):
    ax.add_patch(Arc(vertex, 2 * r, 2 * r, angle=0, theta1=a0, theta2=a1, color=color, lw=0.7, zorder=5))
    for a in (a0, a1):
        ax.plot([vertex[0], vertex[0] + (r + 1.5) * math.cos(math.radians(a))], [vertex[1], vertex[1] + (r + 1.5) * math.sin(math.radians(a))], color=color, lw=0.5, zorder=4)
    am = math.radians((a0 + a1) / 2)
    ax.text(vertex[0] + (r + 1.6) * math.cos(am), vertex[1] + (r + 1.6) * math.sin(am), text, fontsize=fs, color=color, ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def title_block(fig, data, sheet, total, subtitle):
    c = data["constants"]
    fig.text(0.012, 0.045, f"UNIFIED TRI-SPINNER  ·  metal-three-blade  ·  {data['revision']}  ·  Gate 04/06 draft  ·  {subtitle}", fontsize=11, fontweight="bold", color=INK)
    fig.text(0.012, 0.028, f"UNITS mm  ·  所有尺寸 provisional（user-authorized-provisional，无实测）  ·  外接圆 Ø{2 * c['tipR']:.0f} 由照片比例定  ·  Blender +Z = 自旋轴 → Unity +Y  ·  原点 = 轴承中心",
             fontsize=8, color=INK)
    fig.text(0.012, 0.013, f"SOURCE tools/blender/build_unified_tri_spinner.py → export_unified_tri_spinner_cad.py → cad-geometry.json sha256 {sha(DATA)}  ·  {date.today().isoformat()}  ·  SHEET {sheet}/{total}",
             fontsize=8, color=HIDDEN)
    fig.patches.append(plt.Rectangle((0.005, 0.005), 0.99, 0.055, transform=fig.transFigure, fill=False, ec=INK, lw=0.8))


# ------------------------------------------------------------------ views ---
def plan_view(ax, data, alt=None):
    c = data["constants"]
    petal = [tuple(p) for p in data["petalPlan"]]
    setup(ax, "PLAN  顶视（正交）  SCALE 2:1", (-46, 46), (-42, 44))
    centerlines(ax, 40)
    circle(ax, c["tipR"], lw=0.5, color=CENTER, ls=(0, (8, 2, 1.5, 2)))  # tip circle
    for ang in c["bladeAnglesDeg"]:
        a = math.radians(ang)
        pts = [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in petal]
        poly(ax, pts, lw=1.3, close=False)  # apex -> side -> R12 arc -> side -> apex; closing edge hidden under the cap
    circle(ax, c["seamR"], lw=1.0)
    circle(ax, c["capR"], lw=1.3)
    circle(ax, c["tableR"], lw=0.9)
    # wedge ring radial lines (48 triangle edges) drawn light
    for w in data["wedgeRing"]:
        ix, iy, _ = w["inner"]
        ox, oy, _ = w["outer"]
        ax.plot([ix, ox], [iy, oy], color=INK, lw=0.35, zorder=3)
    for j, w in enumerate(data["wedgeRing"]):
        nxt = data["wedgeRing"][(j + 1) % len(data["wedgeRing"])]
        ax.plot([w["outer"][0], nxt["inner"][0]], [w["outer"][1], nxt["inner"][1]], color=INK, lw=0.35, zorder=3)
    circle(ax, c["coreR"], lw=0.6, color=HIDDEN, ls=(0, (4, 2)))  # hidden core ring
    circle(ax, c["boreR"], lw=0.6, color=HIDDEN, ls=(0, (4, 2)))
    # blade axes
    for ang in c["bladeAnglesDeg"]:
        a = math.radians(ang)
        ax.plot([0, 34 * math.cos(a)], [0, 34 * math.sin(a)], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)

    # dimensions
    dia(ax, c["tipR"], 20, f"Ø{2 * c['tipR']:.1f}  外接圆（叶尖）", textshift=1.5)
    dia(ax, c["capR"], -40, f"Ø{2 * c['capR']:.2f}  盖（{c['capRatio']:.3f}×外接圆）", textshift=12)
    dia(ax, c["tableR"], 200, f"Ø{2 * c['tableR']:.2f}  平盘（{c['tableRatio']:.2f}×盖）", textshift=26)
    dia(ax, c["seamR"], 215, f"Ø{2 * c['seamR']:.2f}  沉孔／叶根壁", textshift=8)
    # R12 arcs: leader to arc mid of blade at 330 deg
    for ang in c["bladeAnglesDeg"][:1]:
        a = math.radians(ang)
        tip = (c["tipR"] * math.cos(a), c["tipR"] * math.sin(a))
        ctr = (c["tipArcC"] * math.cos(a), c["tipArcC"] * math.sin(a))
        ax.plot([ctr[0]], [ctr[1]], marker="+", color=DIM, ms=6, mew=0.7, zorder=6)
        ax.annotate("", xy=tip, xytext=ctr, arrowprops=dict(arrowstyle="->", color=DIM, lw=0.7, shrinkA=0, shrinkB=0), zorder=5)
        ax.text(ctr[0] + 1.2, ctr[1] + 3.5, f"R{c['tipArcR']:.0f}  外端圆弧（占 ±{c['tipArcJoinDeg']:.0f}°）×3", fontsize=FS, color=DIM, zorder=6,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    # notch V at the notch between 90 and 210 deg (bisector 150 deg)
    apex = data["notchApex"]
    ap = (apex[0], apex[1])
    # apex is defined for the blade at 0 deg; rotate to blade 90 deg => bisector 150
    a90 = math.radians(90)
    apex90 = (ap[0] * math.cos(a90) - ap[1] * math.sin(a90), ap[0] * math.sin(a90) + ap[1] * math.cos(a90))
    bis = 150.0
    angle_dim(ax, apex90, 7.0, bis - 30, bis + 30, f"{c['notchVDeg']:.0f}°")
    leader(ax, apex90, f"缺口尖点 r={apex[2]:.2f}（暗缝边 r={c['seamR']:.2f}）", (-44, 30))
    # blade width at widest
    w = data["bladeWidest"]
    a330 = math.radians(330)
    p_a = (w["x"] * math.cos(a330) - w["halfWidth"] * math.sin(a330), w["x"] * math.sin(a330) + w["halfWidth"] * math.cos(a330))
    p_b = (w["x"] * math.cos(a330) + w["halfWidth"] * math.sin(a330), w["x"] * math.sin(a330) - w["halfWidth"] * math.cos(a330))
    dim(ax, p_a, p_b, 14.0, f"{2 * w['halfWidth']:.2f}  叶片最宽（r={w['x']:.1f}）")
    # 120 deg spacing
    angle_dim(ax, (0, 0), 30.5, 210, 330, "120°")
    leader(ax, (c["seamR"] * math.cos(math.radians(30)), c["seamR"] * math.sin(math.radians(30))), f"暗缝 {c['seamW']:.1f}（盖沿→叶根壁）", (24, 36))
    leader(ax, (c["coreR"] * math.cos(math.radians(250)), c["coreR"] * math.sin(math.radians(250))), f"轴承座环 Ø{2 * c['coreR']:.2f}（隐藏，盖下）", (-44, -36), color=HIDDEN)
    a_sec = math.radians(330.0)
    sx, sy = math.cos(a_sec), math.sin(a_sec)
    ax.plot([-42 * sx, 42 * sx], [-42 * sy, 42 * sy], color=INK, lw=0.9, ls=(0, (10, 3)), zorder=2)
    ax.text(43 * sx, 43 * sy - 1.0, "A", fontsize=10, fontweight="bold", color=INK, ha="center")
    ax.text(-43 * sx, -43 * sy + 0.5, "A", fontsize=10, fontweight="bold", color=INK, ha="center")
    ax.text(-45, -40.5, "A—A：沿 330° 叶片轴，穿过对面 150° 缺口；剖面图中右侧 = 叶片，左侧 = 缺口", fontsize=6.5, color=HIDDEN)
    # section C-C marker on blade 330: transverse at x = widest
    cx = w["x"]
    p1 = (cx * math.cos(a330) - 20 * math.sin(a330), cx * math.sin(a330) + 20 * math.cos(a330))
    p2 = (cx * math.cos(a330) + 20 * math.sin(a330), cx * math.sin(a330) - 20 * math.cos(a330))
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INK, lw=0.9, ls=(0, (10, 3)), zorder=2)
    ax.text(p1[0] - 1.5, p1[1] + 0.5, "C", fontsize=10, fontweight="bold", color=INK)
    ax.text(p2[0] + 0.5, p2[1] - 2.5, "C", fontsize=10, fontweight="bold", color=INK)

    if alt:
        circle(ax, alt["tableR"], lw=1.0, color=ALT, ls=(0, (5, 2)))
        dia(ax, alt["tableR"], 150, f"Ø{2 * alt['tableR']:.2f}  平盘 0.797（照片值，方案 A2）", color=ALT, textshift=10)
        for pts in alt["literalPetals"]:
            poly(ax, pts, lw=1.0, color=ALT, ls=(0, (5, 2)), close=False)
        for pts in alt["exposedHub"]:
            ax.add_patch(Polygon(pts, closed=True, fill=True, fc="#f4b6a3", ec="none", alpha=0.7, zorder=0))
        leader(ax, alt["literalPetals"][0][len(alt["literalPetals"][0]) // 4], "解释②：单片泪滴切线夹 60° → 叶片=R12 圆弧被暗缝截断", (14, -40), color=ALT)
        leader(ax, alt["exposedHub"][0][1], f"解释②每个缺口在 r={c['seamR']:.1f} 张开 {alt['gapDeg']:.0f}°：机身外露（粉色）", (-44, -42), color=ALT)


def section_aa(ax, data, alt=None):
    c = data["constants"]
    setup(ax, "SECTION A—A  过叶片轴的轴向剖面（右：叶片；左：对面缺口）  SCALE 2:1", (-40, 45), (-15.5, 15))
    ax.plot([-40, 40], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)
    ax.plot([0, 0], [-12, 12], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)
    face = c["bodyHalf"]
    floor = c["coreHalf"]
    seam = c["seamR"]
    tipz = data["axialTop"][-1][1]
    apex_z = None
    for x, y, z in data["bladeHalfOutline"]:
        pass
    ax_apex = data["notchApex"]
    apex_z = face - c["roofSlope"] * ax_apex[1]
    # body right half (blade) as closed polygon (with bore/core simplified: floor at coreHalf)
    right = [(c["boreR"], floor), (seam, floor), (seam, face), (c["endPlaneX"], face), (c["tipR"], tipz), (c["tipR"], -tipz), (c["endPlaneX"], -face), (seam, -face), (seam, -floor), (c["boreR"], -floor)]
    poly(ax, right, lw=1.2, hatch="////")
    # body left half: core + roots to the notch apex sliver
    left = [(-c["boreR"], floor), (-seam, floor), (-seam, apex_z), (-ax_apex[2], apex_z), (-ax_apex[2], -apex_z), (-seam, -apex_z), (-seam, -floor), (-c["boreR"], -floor)]
    poly(ax, left, lw=1.2, hatch="////")
    # caps
    prof = [tuple(p) for p in data["capProfile"]]
    for sgn in (1, -1):
        pts = [(r, sgn * z) for r, z in prof]
        full = pts + [(-r, sgn * z) for r, z in reversed(prof)]
        poly(ax, full, lw=1.2, hatch="\\\\\\\\")
        # rim envelope ticks
        for s2 in (1, -1):
            ax.plot([s2 * c["capR"], s2 * c["capR"]], [sgn * c["rimLoZ"], sgn * c["rimHiZ"]], color=DIM, lw=1.6, zorder=6)
    # bearing (R188) sectioned
    b = c["bearing"]
    for sgn in (1, -1):
        for r0, r1 in ((b["id"] / 2, 4.2), (5.3, b["od"] / 2)):
            poly(ax, [(sgn * r0, -b["width"] / 2), (sgn * r1, -b["width"] / 2), (sgn * r1, b["width"] / 2), (sgn * r0, b["width"] / 2)], lw=0.7, color=HIDDEN, hatch="xxxx")
        circle(ax, 0.85, lw=0.6, color=HIDDEN, c=(sgn * 4.75, 0.0))
    # dimensions
    # vertical dims: dim() offsets to the left for upward p1->p2, so negative = right of the part
    dim(ax, (c["tipR"], -tipz), (c["tipR"], tipz), -2.5, f"{2 * tipz:.1f}  叶尖端面高")
    dim(ax, (seam, floor), (seam, face), -20.3, f"{face - floor:.2f}  沉孔深")
    dim(ax, (c["endPlaneX"] - 4.0, -face), (c["endPlaneX"] - 4.0, face), -20.0, f"{c['bladeT']:.1f}  叶片厚（脊线处）")
    dim(ax, (-c["capR"] - 8, -c["tableZ"]), (-c["capR"] - 8, c["tableZ"]), 0.0, f"{2 * c['tableZ']:.1f}  装配总厚", ext=False)
    dim(ax, (-c["tableR"] - 1.0, face), (-c["tableR"] - 1.0, c["tableZ"]), 6.5, f"{c['tableZ'] - face:.1f}  盖顶高出叶面")
    dim(ax, (0, -floor), (0, floor), -26.0, f"{2 * floor:.1f}  座环厚", ext=False)
    dim(ax, (c["endPlaneX"], face), (c["tipR"], face), 5.2, f"{c['tipR'] - c['endPlaneX']:.1f}  端面斜切起点→叶尖")
    angle_dim(ax, (c["endPlaneX"], face), 2.6, 360 - c["endPlaneSlopeDeg"], 360, f"{c['endPlaneSlopeDeg']:.0f}°")
    leader(ax, (c["capR"], c["rimZ"]), f"楔环外沿 z={c['rimZ']:.2f}±{c['zigzag']:.2f}（低于叶面 {face - c['rimZ']:.2f}）", (-8, 13.5))
    leader(ax, (c["capR"] + 0.4, (face + floor) / 2), f"暗缝 {c['seamW']:.1f}", (26, -9.5))
    leader(ax, (-seam - 0.04, apex_z), f"缺口尖点处叶片残余 r {seam:.2f}→{ax_apex[2]:.2f}，高 ±{apex_z:.2f}", (-39, 12.5))
    leader(ax, (c["boreR"], 0.9), f"Ø{2 * c['boreR']:.1f} 轴孔 · R188 {b['od']}×{b['id']}×{b['width']}（隐藏）", (2, -12.4), color=HIDDEN)
    leader(ax, (c["stemR"], c["skirtBottomZ"] - 0.6), f"盖轴 Ø{2 * c['stemR']:.1f}，盖底 z={c['skirtBottomZ']:.1f}", (-30, -11.5))
    leader(ax, (c["seamR"] + 3, -face), "所有外露边 0.5 mm 倒角 ×2 段（未画）", (2, -14.6), color=HIDDEN)
    if alt:
        # alternative cone for table 0.797
        r2 = alt["tableR"]
        for sgn in (1, -1):
            ax.plot([-r2, r2], [sgn * c["tableZ"], sgn * c["tableZ"]], color=ALT, lw=1.0, ls=(0, (5, 2)), zorder=6)
            for s2 in (1, -1):
                ax.plot([s2 * r2, s2 * c["capR"]], [sgn * c["tableZ"], sgn * alt["rimZ"]], color=ALT, lw=1.0, ls=(0, (5, 2)), zorder=6)
        leader(ax, (-c["capR"], alt["rimZ"]), f"方案 A2：平盘 0.797 → 外沿 z={alt['rimZ']:.2f}（低于叶面 {face - alt['rimZ']:.2f}）", (-39, -13.5), color=ALT)


def section_cc(ax, data):
    c = data["constants"]
    w = data["bladeWidest"]
    setup(ax, f"SECTION C—C  叶片横向剖面（最宽处 r={w['x']:.1f}）  SCALE 2:1", (-24, 24), (-9, 11))
    ax.plot([-24, 24], [0, 0], color=CENTER, lw=0.5, ls=(0, (8, 2, 1.5, 2)), zorder=1)
    hw, wz, face = w["halfWidth"], w["wallTopZ"], c["bodyHalf"]
    poly(ax, [(-hw, -wz), (0, -face), (hw, -wz), (hw, wz), (0, face), (-hw, wz)], lw=1.2, hatch="////")
    dim(ax, (-hw, -wz), (hw, -wz), -3.5, f"{2 * hw:.2f}")
    dim(ax, (hw, -wz), (hw, wz), -3.0, f"{2 * wz:.2f}  竖直侧壁")
    dim(ax, (0, -face), (0, face), -21.0, f"{c['bladeT']:.1f}  脊线", ext=False)
    angle_dim(ax, (hw, wz), 5.0, 180 - c["roofSlopeDeg"], 180, f"{c['roofSlopeDeg']:.1f}°  屋脊面")
    leader(ax, (0, face), "中脊（两屋脊平面相交）", (3, 9.5))
    leader(ax, (-hw, 0), "竖直侧壁：连续曲面（顶视轮廓拉伸）", (-23, -7.5), color=HIDDEN)


def detail_b(ax, data):
    c = data["constants"]
    setup(ax, "DETAIL B  楔环展开（沿盖沿 r=17.42 展开，显示 6/24 楔）  SCALE 4:1", (-1, 38), (2.0, 9.0))
    ring = data["wedgeRing"]
    n = c["nWedge"]
    pitch_in = 2 * math.pi * c["tableR"] / n  # arc length per wedge on the table edge
    pitch_out = 2 * math.pi * c["capR"] / n
    # developed: use rim arc length as x for outer, table arc for inner (radial faces converge; draw as trapezoid strip)
    xs_in = [j * pitch_out for j in range(7)]
    z_in = c["tableZ"]
    outs = [((j + 0.5) * pitch_out, ring[j % n]["outer"][2]) for j in range(6)]
    for j in range(6):
        i0, i1 = (xs_in[j], z_in), (xs_in[j + 1], z_in)
        o = outs[j]
        ax.plot([i0[0], o[0], i1[0]], [i0[1], o[1], i1[1]], color=INK, lw=1.0, zorder=3)
        if j < 5:
            ax.plot([o[0], outs[j + 1][0]], [o[1], outs[j + 1][1]], color=INK, lw=1.3, zorder=3)  # zigzag rim
    ax.plot([xs_in[0], xs_in[-1]], [z_in, z_in], color=INK, lw=1.3, zorder=3)
    # skirt bottom
    ax.plot([outs[0][0], outs[-1][0]], [c["skirtBottomZ"], c["skirtBottomZ"]], color=HIDDEN, lw=0.8, ls=(0, (4, 2)), zorder=2)
    dim(ax, (xs_in[1], z_in), (xs_in[2], z_in), 0.9, f"{pitch_out:.2f}（{360 / n:.0f}°）  楔距（外沿弧长）")
    dim(ax, (outs[-1][0] + 2.0, c["rimLoZ"]), (outs[-1][0] + 2.0, c["rimHiZ"]), 0.0, f"{2 * c['zigzag']:.2f}  锯齿峭谷", ext=False)
    dim(ax, (outs[-1][0] + 6.0, c["rimZ"]), (outs[-1][0] + 6.0, z_in), 0.0, f"{z_in - c['rimZ']:.2f}  落差", ext=False)
    ax.plot([outs[-1][0], outs[-1][0] + 6.5], [c["rimZ"], c["rimZ"]], color=DIM, lw=0.4, ls=(0, (3, 2)))
    ax.plot([xs_in[-1], outs[-1][0] + 6.5], [z_in, z_in], color=DIM, lw=0.4, ls=(0, (3, 2)))
    leader(ax, (outs[0][0], outs[0][1]), "外沿顶点交替 ±0.55 → 每楔 2 个三角平面，尖端里外交替", (4, 2.6))
    leader(ax, ((xs_in[2] + xs_in[3]) / 2, z_in), "平盘边（最高点）", (16, 8.5))
    ax.text(20, 2.5, f"{n} 楔 / {2 * n} 三角 · 相邻法线夹角 9.3–16.1° · 面斜 19.5–29.3°（均值 ≈{c['slopeDeg']:.0f}°）", fontsize=6.5, color=HIDDEN)


def crown_radial(ax, data):
    c = data["constants"]
    setup(ax, "DETAIL B'  楔环径向剖面  SCALE 4:1", (10, 20.5), (1.5, 9.6))
    pts = [(c["tableR"], c["tableZ"]), (c["capR"], c["rimZ"]), (c["capR"], c["skirtBottomZ"])]
    ax.plot([10.5, c["tableR"]], [c["tableZ"], c["tableZ"]], color=INK, lw=1.3)
    ax.plot(*zip(*pts), color=INK, lw=1.3)
    ax.plot([c["capR"], c["capR"]], [c["rimLoZ"], c["rimHiZ"]], color=DIM, lw=2.2)
    ax.plot([c["seamR"], c["seamR"]], [c["coreHalf"], c["bodyHalf"]], color=INK, lw=1.3)
    ax.plot([c["seamR"], 20.3], [c["bodyHalf"], c["bodyHalf"]], color=INK, lw=1.3)
    ax.plot([10.5, 20.3], [c["coreHalf"], c["coreHalf"]], color=INK, lw=1.0)
    dim(ax, (c["tableR"], c["tableZ"]), (c["capR"], c["tableZ"]), 0.7, f"{c['capR'] - c['tableR']:.2f}  楔环径向宽")
    dim(ax, (c["capR"], c["rimZ"]), (c["seamR"], c["rimZ"]), -1.2, f"{c['seamW']:.1f}")
    dim(ax, (20.0, c["bodyHalf"]), (20.0, c["tableZ"]), 0.0, "1.50", ext=False)
    dim(ax, (20.0, c["rimZ"]), (20.0, c["bodyHalf"]), 0.0, f"{c['bodyHalf'] - c['rimZ']:.2f}", ext=False)
    ax.plot([c["tableR"], 20.3], [c["tableZ"], c["tableZ"]], color=DIM, lw=0.4, ls=(0, (3, 2)))
    ax.plot([c["capR"], 20.3], [c["rimZ"], c["rimZ"]], color=DIM, lw=0.4, ls=(0, (3, 2)))
    angle_dim(ax, (c["tableR"], c["tableZ"]), 2.2, 360 - c["slopeDeg"], 360, f"{c['slopeDeg']:.0f}°")
    leader(ax, (c["capR"], c["rimHiZ"]), "±0.55", (18.5, 8.3))
    ax.text(10.6, 1.8, "平盘 z=7.25 · 外沿 z=4.81 · 叶面 z=5.75 · 沉孔底 z=2.20", fontsize=6.5, color=HIDDEN)


# ---------------------------------------------------------------- sheets ---
def sheet1(data):
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.10, 0.50, 0.86])
    ax_aa = fig.add_axes([0.53, 0.55, 0.46, 0.41])
    ax_cc = fig.add_axes([0.53, 0.30, 0.24, 0.24])
    ax_b = fig.add_axes([0.53, 0.09, 0.30, 0.20])
    ax_b2 = fig.add_axes([0.83, 0.09, 0.16, 0.20])
    plan_view(ax_plan, data)
    section_aa(ax_aa, data)
    section_cc(ax_cc, data)
    detail_b(ax_b, data)
    crown_radial(ax_b2, data)
    title_block(fig, data, 1, 2, "平面图 + 剖面（rev-004 现状）")
    return fig


def alternatives(data):
    c = data["constants"]
    r_alt = c["capR"] * 0.797
    rim_alt = c["tableZ"] - (c["capR"] - r_alt) * math.tan(math.radians(c["slopeDeg"]))
    # literal reading: R12 disc clipped by the seam circle
    R, C, S = c["tipArcR"], c["tipArcC"], c["seamR"]
    xi = (S * S - R * R + C * C) / (2 * C)
    yi = math.sqrt(max(0.0, S * S - xi * xi))
    a_cut = math.degrees(math.atan2(yi, xi - C))
    petals, exposed = [], []
    half_span = math.degrees(math.atan2(yi, xi))
    gap = 120.0 - 2 * half_span
    for ang in c["bladeAnglesDeg"]:
        pts = []
        for k in range(61):
            a = math.radians(a_cut) * (1 - 2 * k / 60)
            pts.append((C + R * math.cos(a), R * math.sin(a)))
        ar = math.radians(ang)
        petals.append([(x * math.cos(ar) - y * math.sin(ar), x * math.sin(ar) + y * math.cos(ar)) for x, y in pts])
        # exposed sector between this blade's edge and the next one's
        a0 = math.radians(ang + half_span)
        a1 = math.radians(ang + 120 - half_span)
        r_hub = 19.6
        sector = [(S * math.cos(a0), S * math.sin(a0))]
        for k in range(11):
            a = a0 + (a1 - a0) * k / 10
            sector.append((r_hub * math.cos(a), r_hub * math.sin(a)))
        sector.append((S * math.cos(a1), S * math.sin(a1)))
        exposed.append(sector)
    return {"tableR": r_alt, "rimZ": rim_alt, "literalPetals": petals, "exposedHub": exposed, "gapDeg": gap}


def sheet2(data):
    alt = alternatives(data)
    fig = plt.figure(figsize=(16.5, 11.7), dpi=220)
    fig.patch.set_facecolor("white")
    ax_plan = fig.add_axes([0.02, 0.10, 0.50, 0.86])
    ax_aa = fig.add_axes([0.53, 0.50, 0.46, 0.46])
    ax_txt = fig.add_axes([0.53, 0.09, 0.46, 0.38])
    plan_view(ax_plan, data, alt=alt)
    section_aa(ax_aa, data, alt=alt)
    ax_txt.axis("off")
    c = data["constants"]
    lines = [
        "裁决叠加（橙色虚线 = 未建的备选；黑色 = rev-004 现状）",
        "",
        f"A  台面占比：A1 = 0.70（现状）Ø{2 * c['tableR']:.2f}，楔环宽 {c['capR'] - c['tableR']:.2f}，25° 落差 {c['tableZ'] - c['rimZ']:.2f} → 外沿低于叶面 {c['bodyHalf'] - c['rimZ']:.2f}",
        f"                A2 = 0.797（照片）Ø{2 * alt['tableR']:.2f}，楔环宽 {c['capR'] - alt['tableR']:.2f}，落差 {c['tableZ'] - alt['rimZ']:.2f} → 外沿低于叶面 {c['bodyHalf'] - alt['rimZ']:.2f}（几乎齐平）",
        "     两者盖径、盖高、斜角、锯齿、暗缝全部相同；差别只在暗缝看起来是槽还是细线。",
        "",
        f"B  “两侧向内收 60°”：①（现状）= 相邻叶片间 V 缺口 60°，尖点 r={data['notchApex'][2]:.2f} 落在暗缝边，机身顶视不可见；",
        f"     ② 字面 = 单片泪滴两侧切线夹 60°：切线在 r<{c['seamR']:.1f} 内，叶片可见轮廓退化为 R12 圆弧，每缺口张开 {alt['gapDeg']:.0f}°，机身必外露（粉色区）。",
        "     ② 若采用，需给机身圆柱一个直径（示意取 Ø39.2），并放弃“机身被完全包住”。",
        "",
        "C  叶根暗三角凹陷：照片有、现状实心。无几何定义，未叠加；若要加，需要给出凹陷的三角尺寸与深度。",
        "",
        "D  其余（R12 外弧、11.5 厚、屋脊 10.2°、端面 32°、0.8 暗缝、24 楔 ±0.55）为 rev-004 现状，见 SHEET 1。",
    ]
    ax_txt.text(0.0, 1.0, "\n".join(lines), fontsize=8.6, va="top", ha="left", color=INK, family=FONT, linespacing=1.55)
    title_block(fig, data, 2, 2, "裁决叠加：台面 0.70/0.797 · 缺口解释 ①/②")
    return fig


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT_TMP.mkdir(parents=True, exist_ok=True)
    for name, fig in (("cad-sheet-1-plan-sections", sheet1(data)), ("cad-sheet-2-decision-overlays", sheet2(data))):
        for folder in (G06, OUT_TMP):
            fig.savefig(folder / f"{name}.png", dpi=220, facecolor="white")
        fig.savefig(G06 / f"{name}.pdf", facecolor="white")
        plt.close(fig)
        print(G06 / f"{name}.png")


if __name__ == "__main__":
    main()
