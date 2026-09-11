"""Shaded-relief illustration of the Gate 02 rev-006 reference geometry (CAD v13).

v15: blade side = interlocking pentagon facets, dragon-scale layout read from f0148/f0150/f0152 at 10x: light "kites" hang from
the top-face edge (shallower plane, V tip near the mid-plane) and dark "Λ" facets rise from the mid-plane (steeper plane, tip near
the top edge); every facet is its own plane, hard creases, small ridges where the zigzag leaves the plane intersection.
Blade top = raised mesa (flat crest region with straight-sloped skirts) instead of a tent with valleys between the Y lines.

v11: the blade edge band is built as explicit rows of planar dragon-scale facets (D05 multi-row), which also
removes the distance-field ripple ("凹痕") of v10.

Builds a height field from the same spec the CAD is drawn from (planform v7,
D01 14-sector concave disc, D02/D03 cap-edge three tiers, D04 Y ridge, D05 band,
D06 wall, D08 pocket) and renders it with one key light so concave / convex
reads from light and shadow. Also emits a signed-curvature map (red = convex,
blue = concave). This is a 2.5-D analysis illustration, not a Blender blockout
and not a shipping render; crest / dish / pocket / tier heights are placeholders.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import LightSource
from matplotlib.path import Path as MPath
from scipy import ndimage

import draw_geeone_reference_cad_v13 as cad

A02 = cad.A02
N = 1500
EXT = 1.08
SEAM_W = 0.008
POCKET_RIM = 0.012
SCALE_LEN = cad.D["UTS-D05"]["params"]["scaleLengthToR"]  # ≈0.18 R, 4-5 per edge (f0148/f0154)
KITE_SLOPE_DEG = 42.0  # light kites hanging from the top-face edge (provisional)
LAMBDA_SLOPE_DEG = 56.0  # dark Λ facets rising from the mid-plane (provisional)
ZIG_TOP = 0.25  # Λ tips reach up to 25 % of the band width below the top edge (provisional)
ZIG_BOT = 0.85  # kite tips reach down to 85 % of the band width (provisional)
FACET_TWIST_DEG = 3.0  # alternate twist along the edge inside each family (provisional)
MESA_SKIRT = 0.09  # top face: raised crest region, skirts fall to the top-face edge / pocket rim over this distance (R, provisional)  # corrugation amplitude that makes neighbouring scales face ±s (light/dark), provisional


def resample_smooth(pts, n_out=2400, smooth=2e-5):
    """Periodic smoothing spline through a closed polygon, resampled densely so the distance field has no vertex-kink ripple."""
    from scipy import interpolate

    arr = np.array(pts + [pts[0]])
    seg = np.hypot(np.diff(arr[:, 0]), np.diff(arr[:, 1]))
    u = np.concatenate([[0.0], np.cumsum(seg)])
    u /= u[-1]
    tck, _ = interpolate.splprep([arr[:, 0], arr[:, 1]], u=u, s=smooth, per=True)
    uu = np.linspace(0, 1, n_out, endpoint=False)
    xx, yy = interpolate.splev(uu, tck)
    return list(zip(xx.tolist(), yy.tolist()))


def arclength_raster(pts) -> np.ndarray:
    """Rasterise a closed polygon, storing the cumulative arc length (R) on its pixels; NaN elsewhere."""
    img = np.full(X.shape, np.nan)
    s = 0.0
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        seg = math.hypot(x1 - x0, y1 - y0)
        m = max(2, int(seg / PX * 2))
        xx = np.linspace(x0, x1, m)
        yy = np.linspace(y0, y1, m)
        ss = s + np.linspace(0, seg, m)
        ii = np.clip(np.round((yy + EXT) / PX).astype(int), 0, N - 1)
        jj = np.clip(np.round((xx + EXT) / PX).astype(int), 0, N - 1)
        img[ii, jj] = ss
        s += seg
    return img
DISH_DEG = 3.0
FONT = cad.FONT if hasattr(cad, "FONT") else None
for cand in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/PingFang.ttc"):
    if Path(cand).exists():
        font_manager.fontManager.addfont(cand)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=cand).get_name()
        break

xs = np.linspace(-EXT, EXT, N)
X, Y = np.meshgrid(xs, xs)
PX = xs[1] - xs[0]
R = np.hypot(X, Y)
T = cad.BODY_T
TOP = T / 2
WALL_TOP = cad.WALL_H * T / 2
CAP = cad.CAP
CAP_TOP = T / 2 + cad.CAP_SIDE_H
R_RIM = cad.TABLE * CAP
GROUND = -0.10
SEAM_Z = TOP - 0.09


def rotp(pts, deg):
    a = math.radians(deg)
    return [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in pts]


def mask_poly(pts) -> np.ndarray:
    return MPath(pts).contains_points(np.c_[X.ravel(), Y.ravel()]).reshape(X.shape)


def raster_polyline(pts) -> np.ndarray:
    m = np.zeros(X.shape, dtype=bool)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / PX * 2))
        xx = np.linspace(x0, x1, n)
        yy = np.linspace(y0, y1, n)
        i = np.clip(np.round((yy + EXT) / PX).astype(int), 0, N - 1)
        j = np.clip(np.round((xx + EXT) / PX).astype(int), 0, N - 1)
        m[i, j] = True
    return m


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


def pocket_polygon():
    pk = cad.PK
    bx = CAP * math.cos(math.asin(pk["baseHalfWidthToR"] / CAP))
    tri = [(pk["apexRadiusToR"], 0.0), (bx, pk["baseHalfWidthToR"]), (bx, -pk["baseHalfWidthToR"])]
    return rounded(tri, pk["cornerRadiusToR"])


def polygon_radius(normal_angle_offset: float) -> np.ndarray:
    """'Vertex radius' of the regular 14-gon through each point, for a polygon whose edge normals sit at
    angles (j + offset)·2π/14. Inside the polygon of vertex radius r  <=>  value <= r."""
    best = np.full(X.shape, -np.inf)
    for j in range(cad.N_SECTOR):
        a = 2 * math.pi * (j + normal_angle_offset) / cad.N_SECTOR
        best = np.maximum(best, X * math.cos(a) + Y * math.sin(a))
    return best / math.cos(math.pi / cad.N_SECTOR)


def tri_plane_z(p0, p1, p2, pts_mask):
    """Plane z through three (x, y, z) points, evaluated where pts_mask; returns (inside_mask, z)."""
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = p0, p1, p2
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    xx, yy = X[pts_mask], Y[pts_mask]
    l1 = ((xx - x0) * (y2 - y0) - (x2 - x0) * (yy - y0)) / det
    l2 = ((x1 - x0) * (yy - y0) - (xx - x0) * (y1 - y0)) / det
    l0 = 1 - l1 - l2
    inside = (l0 >= -1e-9) & (l1 >= -1e-9) & (l2 >= -1e-9)
    z = l0 * z0 + l1 * z1 + l2 * z2
    return inside, z


def band_mask(m_full, m_plate):
    return m_full & ~m_plate


def build_height_field():
    Z = np.full(X.shape, GROUND)
    body = np.zeros(X.shape, dtype=bool)
    half = cad.planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    plate_half = cad.offset_inward(half, cad.BEVEL_W)
    plate = plate_half + [(x, -y) for x, y in reversed(plate_half) if y > 1e-9]
    pocket = pocket_polygon()
    arm = cad.y_crest_arm()
    crest_lines = [cad.y_crest_stem(), arm, [(x, -y) for x, y in arm]]
    depth = cad.POCKET_DEPTH_FRACTION * T
    tiers = cad.EDGE_TIERS
    edges = np.cumsum([0.0] + [tr["widthToR"] for tr in tiers])
    row_top = [TOP]
    for tr in tiers:
        row_top.append(row_top[-1] - tr["widthToR"] * math.tan(math.radians(tr["slopeDeg"])))
    plate = resample_smooth(plate)
    for ang in (90, 210, 330):
        m_full = mask_poly(rotp(full, ang))
        plate_r = rotp(plate, ang)
        m_plate = mask_poly(plate_r) & m_full
        m_pocket = mask_poly(rotp(pocket, ang)) & m_plate
        crest = np.zeros(X.shape, dtype=bool)
        for line in crest_lines:
            crest |= raster_polyline(rotp(line, ang))
        sm = lambda a: ndimage.gaussian_filter(a, 1.5)  # take the stair-step ripple out of rasterised distance fields
        sm5 = lambda a: ndimage.gaussian_filter(a, 5.0)  # offset polygon vertices leave fan ripples in the EDT; smooth them out
        d_crest = sm5(ndimage.distance_transform_edt(~crest) * PX)
        d_plate_out = sm(ndimage.distance_transform_edt(~m_plate) * PX)  # >0 outside the plateau
        d_low = sm5(ndimage.distance_transform_edt(m_plate & ~m_pocket) * PX)  # distance to plateau edge or pocket rim
        d_in_pocket = sm(ndimage.distance_transform_edt(m_pocket) * PX)
        band = band_mask(m_full, m_plate)
        z = np.zeros(X.shape)
        # --- multi-row dragon-scale band: rows by distance from the top face, scales by arc length along it ---
        # exact distance / arc length to the dense smooth boundary (KD-tree on 2400 points): no digital-EDT ripple
        from scipy.spatial import cKDTree

        verts = np.array(plate_r)
        seg = np.hypot(np.diff(verts[:, 0], append=verts[0, 0]), np.diff(verts[:, 1], append=verts[0, 1]))
        s_vert = np.concatenate([[0.0], np.cumsum(seg)[:-1]])
        tree = cKDTree(verts)
        d = np.zeros(X.shape)
        s_all = np.zeros(X.shape)
        qd, qi = tree.query(np.c_[X[band], Y[band]], k=1)
        d[band] = qd
        s_all[band] = s_vert[qi]
        zb = np.full(X.shape, WALL_TOP)
        L = SCALE_LEN
        W = cad.BEVEL_W
        k1 = math.tan(math.radians(KITE_SLOPE_DEG))
        k2 = math.tan(math.radians(LAMBDA_SLOPE_DEG))
        tw = math.tan(math.radians(FACET_TWIST_DEG))
        sq, dq = s_all[band], d[band]
        f = (sq / L) % 1.0  # kite-local coordinate: kite c spans f in [0, 1), Λ tips at f = 0
        d_zig = W * (ZIG_TOP + (ZIG_BOT - ZIG_TOP) * (1 - 2 * np.abs(f - 0.5)))  # V tip at f = 0.5, Λ tips at f = 0 / 1
        c_k = np.floor(sq / L).astype(int)
        c_l = np.floor(sq / L + 0.5).astype(int)  # Λ facet centred on s = c_l L
        sg_k = np.where(c_k % 2 == 0, 1.0, -1.0)
        sg_l = np.where(c_l % 2 == 0, 1.0, -1.0)
        z_kite = TOP - k1 * dq + tw * sg_k * (sq - (c_k + 0.5) * L)
        z_lam = k2 * (W - dq) + tw * sg_l * (sq - c_l * L)
        zb[band] = np.where(dq < d_zig, z_kite, np.maximum(z_lam, WALL_TOP))
        z[band] = zb[band]
        plateau = m_plate & ~m_pocket
        z[plateau] = TOP + cad.CREST * np.clip(d_low[plateau] / MESA_SKIRT, 0, 1)  # mesa: flat crest region, straight skirts, no valleys
        z[m_pocket] = TOP - depth * np.clip(d_in_pocket[m_pocket] / POCKET_RIM, 0, 1)
        Z[m_full] = z[m_full]
        body |= m_full
    # cap + seam
    s_disc = polygon_radius(0.5)  # disc 14-gon: vertices at j, edge normals at j+0.5
    s_outer = polygon_radius(0.0)  # crown outer / skirt polygons: vertices at j+0.5, edge normals at j
    tiers = cad.CAP_TIERS
    r1 = R_RIM + tiers[0]["radialToCap"] * CAP
    r2 = r1 + tiers[1]["radialToCap"] * CAP
    drops = [tr["radialToCap"] * CAP * math.tan(math.radians(tr["slopeDeg"])) for tr in tiers]
    z1 = CAP_TOP - drops[0]
    z2 = z1 - drops[1]
    z3 = z2 - drops[2]
    dish_d = R_RIM * math.tan(math.radians(DISH_DEG))
    cap = s_outer <= CAP
    seam = (R < CAP + SEAM_W) & ~cap
    Z[seam & (body | (R >= CAP * 0.97))] = SEAM_Z
    Z[body & (R < CAP + SEAM_W) & ~cap] = SEAM_Z
    disc = s_disc <= R_RIM
    Z[disc] = CAP_TOP - dish_d * (1 - s_disc[disc] / R_RIM)
    crown = cap & ~disc & (s_outer <= r1)
    n = cad.N_SECTOR
    inner = [(R_RIM * math.cos(2 * math.pi * j / n), R_RIM * math.sin(2 * math.pi * j / n), CAP_TOP) for j in range(n)]
    outer = [(r1 * math.cos(2 * math.pi * (j + 0.5) / n), r1 * math.sin(2 * math.pi * (j + 0.5) / n), z1) for j in range(n)]
    zc = np.full(crown.sum(), np.nan)
    for j in range(n):
        for tri in ((inner[j], inner[(j + 1) % n], outer[j]), (outer[j - 1], outer[j], inner[j])):
            inside, zt = tri_plane_z(*tri, crown)
            zc[inside] = zt[inside]
    zc = np.where(np.isnan(zc), z1, zc)
    Z[crown] = zc
    t2 = cap & (s_outer > r1) & (s_outer <= r2)
    Z[t2] = z1 - drops[1] * (s_outer[t2] - r1) / (r2 - r1)
    t3 = cap & (s_outer > r2)
    Z[t3] = z2 - drops[2] * (s_outer[t3] - r2) / (CAP - r2)
    region = np.zeros(X.shape, dtype=np.uint8)  # 0 ground, 1 blade, 2 seam, 3 cap
    region[body] = 1
    region[(Z == SEAM_Z)] = 2
    region[cap] = 3
    return Z, region, dict(r1=r1, r2=r2, z1=z1, z2=z2, z3=z3, dish_d=dish_d)


VERT_EXAG = 3.0


def relative_height(Z, region, clip=0.02):
    """Height relative to each part's nominal top face (blade plateau = t/2, cap = disc rim), clipped to ±clip."""
    nominal = np.where(region == 3, CAP_TOP, TOP)
    rel = np.where(region > 0, Z - nominal, 0.0)
    rel = np.where(region == 2, -clip, rel)
    return np.clip(rel / clip, -1, 1)


def shade(Z, region, vert_exag=VERT_EXAG, az=315, alt=38, cavity=0.45):
    """Hillshade with one key light plus cavity darkening: recessed areas (below their part's main face)
    get up to `cavity` darker, so 凹 reads darker even where the slope alone would not show it."""
    ls = LightSource(azdeg=az, altdeg=alt)
    # 1.5 px pre-blur: the rasterised distance fields carry ~0.0002 R noise that raking light would turn into stripes
    hs = ls.hillshade(ndimage.gaussian_filter(Z, 0.6), vert_exag=vert_exag, dx=PX, dy=PX)
    albedo = np.select([region == 0, region == 1, region == 2, region == 3], [0.30, 0.90, 0.20, 0.90])
    img = albedo * (0.12 + 1.15 * hs)
    img = np.where(region == 0, 0.30, img)  # flat neutral ground so the silhouette always reads
    kk = relative_height(Z, region)
    img = img * (1 + cavity * np.minimum(kk, 0))
    return np.clip(img, 0, 1)


def relief_overlay(Z, region, base, clip=0.02):
    """Height relative to each part's nominal top face (blade plateau = t/2, cap = disc rim height).
    Red = raised above that face (convex: Y ridge), blue = recessed below it (concave: dish, pocket, band, tiers, seam)."""
    kk = relative_height(Z, region, clip)
    rgb = np.dstack([base, base, base])
    red = np.array([0.85, 0.15, 0.10])
    blue = np.array([0.10, 0.35, 0.90])
    wgt = np.abs(kk) * 0.8
    col = np.where((kk > 0)[..., None], red, blue)
    rgb = rgb * (1 - wgt[..., None]) + col * wgt[..., None]
    rgb[region == 0] = np.dstack([base, base, base])[region == 0]
    return np.clip(rgb, 0, 1)


def main() -> None:
    Z, region, info = build_height_field()
    img = shade(Z, region)
    curv = relief_overlay(Z, region, img)
    extent = (-EXT, EXT, -EXT, EXT)

    fig = plt.figure(figsize=(18, 13.5), dpi=170)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 3, left=0.02, right=0.98, top=0.83, bottom=0.04, wspace=0.08, hspace=0.20)

    def panel(cell, im, title, cmap=None, xlim=None, ylim=None):
        ax = fig.add_subplot(cell)
        ax.imshow(im, extent=extent, origin="lower", cmap=cmap, vmin=0, vmax=1, interpolation="bilinear")
        ax.set_title(title, fontsize=11, loc="left")
        ax.set_xticks([])
        ax.set_yticks([])
        if xlim:
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
        return ax

    a1 = panel(gs[0, 0], img, f"① 顶视阴影图 · 光从左上、仰角 38°（高度夸张 {VERT_EXAG:.0f}×）+ 凹处加暗（cavity）\n凸起 = 左上亮 / 右下暗；凹陷 = 左上暗 / 右下亮，且整体偏暗", cmap="gray")
    a2 = panel(gs[0, 1], curv, "② 凹凸判读：相对各自主面的高度（±0.02 R 饱和）\n红 = 高于主面（凸：Y 脊）· 蓝 = 低于主面（凹：盘、坑、鳞面带、盖缘、缝）")
    rake = shade(Z, region, az=290, alt=18)
    a3 = panel(gs[0, 2], rake, f"③ 顶视 · 低角度侧光（光从左偏上、仰角 18°，高度夸张 {VERT_EXAG:.0f}×）\n微小起伏被放大：盘 14 扇区、冠环三角、Y 脊、鳞面带都更明显", cmap="gray")
    zoom = 0.56
    a4 = panel(gs[1, 0], rake, "④ 盖放大（低角度侧光）：14 扇区凹盘（中心最低）→ 冠环 28 三角\n（相邻两面倾角 17°/26°，一亮一暗）→ 裙两排逐层变陡 → 暗缝", cmap="gray", xlim=(-zoom, zoom), ylim=(-zoom, zoom))
    a5 = panel(gs[1, 1], curv, "⑤ 盖放大（凹凸）：盘缘 = 主面（白）→ 盘心渐蓝（凹拇指位）\n→ 冠环/裙向外越来越蓝（逐层下落）→ 缝深蓝", xlim=(-zoom, zoom), ylim=(-zoom, zoom))
    bl = rotp([(0.66, 0.0)], 330)[0]
    a6 = panel(gs[1, 2], rake, f"⑥ 右下叶放大（低角度侧光）：Y 形隆起 = 亮脊（凸）· 叶根凹坑 = 暗三角（凹）\n· 叶边龙鳞：亮鸢形（自顶面边下垂）与暗 Λ 形（自中面上升）咬合，硬折边", cmap="gray", xlim=(bl[0] - 0.5, bl[0] + 0.5), ylim=(bl[1] - 0.5, bl[1] + 0.5))

    def note(ax, xy, text, xytext, color="#111"):
        ax.annotate(text, xy=xy, xytext=xytext, fontsize=8, color=color, arrowprops=dict(arrowstyle="->", color=color, lw=0.8), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=0.5, alpha=0.9))

    note(a4, (0.0, 0.0), "盘中心 = 最低点（凹 14 棱锥，3° 占位）", (-0.58, -0.52))
    note(a4, (R_RIM * 0.999, 0.0), "盘缘 14 边形 = 盖最高圈", (0.10, 0.50))
    note(a4, ((R_RIM + info["r1"]) / 2 * math.cos(0.3), (R_RIM + info["r1"]) / 2 * math.sin(0.3)), "冠环：相邻三角法线不同 → 一亮一暗", (0.22, -0.56))
    note(a4, (info["r2"] * math.cos(2.2), info["r2"] * math.sin(2.2)), "裙上排 45° / 下排 75°（占位）", (-0.60, 0.50))
    note(a4, ((CAP + SEAM_W * 0.5) * math.cos(-1.9), (CAP + SEAM_W * 0.5) * math.sin(-1.9)), "暗缝（盖竖壁在缝内，顶视不可见）", (-0.05, -0.60))
    stem_mid = rotp([(0.86, 0.0)], 330)[0]
    arm_mid = rotp([tuple(cad.Y_MID)], 330)[0]
    pocket_c = rotp([(0.56, 0.0)], 330)[0]
    band_pt = rotp([(0.70, cad.half_width(0.70) - cad.BEVEL_W * 0.5)], 330)[0]
    # reference lines from the CAD so the shading can be read against the drawing: Y crest (purple), pocket rim (orange)
    for line in (cad.y_crest_stem(), cad.y_crest_arm(), [(x, -y) for x, y in cad.y_crest_arm()]):
        pts = rotp(line, 330)
        a6.plot([q[0] for q in pts], [q[1] for q in pts], color="#6a3d9a", lw=1.0, ls=(0, (4, 2)), alpha=0.9)
    pk = rotp(pocket_polygon(), 330) + [rotp(pocket_polygon(), 330)[0]]
    a6.plot([q[0] for q in pk], [q[1] for q in pk], color="#d9541e", lw=0.9, ls=(0, (2, 2)), alpha=0.9)
    note(a6, stem_mid, "Y 形平顶隆起（紫虚线 = CAD 脊线）：顶平、裙直斜，无谷", (bl[0] - 0.48, bl[1] + 0.42))
    note(a6, arm_mid, "Y 臂：环抱凹坑的隆起", (bl[0] - 0.48, bl[1] + 0.30))
    note(a6, pocket_c, "叶根凹坑（橙虚线 = CAD 坑边）：平底、上下镜像（深度占位）", (bl[0] - 0.48, bl[1] - 0.42))
    note(a6, band_pt, "叶边龙鳞：亮鸢形 / 暗 Λ 形咬合到中面（尺寸/角度占位）", (bl[0] + 0.02, bl[1] + 0.42))
    fig.text(0.02, 0.965, "GEEONE 龙鳞三叶 · 参考几何阴影示意（CAD v13 同一参数生成的高度图 + 单灯着色 · v15 龙鳞刻面）", fontsize=15, fontweight="bold")
    fig.text(0.02, 0.945, "metal-three-blade · Gate 02 rev-006 · 2.5D 分析插图", fontsize=10, color="#333")
    fig.text(0.02, 0.905, f"用途：用明暗读凹/凸。不是 Blender 白模、不是渲染。占位值：脊高 {cad.CREST:.3f} R、盘凹 {DISH_DEG:.0f}°、凹坑深 {cad.POCKET_DEPTH_FRACTION:.0%}/侧、盖缘三层角度、叶边鳞 42°/56° 与锯齿深度 25%–85%、顶面裙宽 0.09 R。每片鳞独立平面、硬折边。视觉批准待确认，未推送手机。", fontsize=9.5, color="#333")
    # calibration legend: a convex dome and a concave dish under the same two lights
    lx = np.linspace(-1.2, 1.2, 160)
    LX, LY = np.meshgrid(lx, lx)
    LR = np.hypot(LX, LY)
    dome = np.where(LR < 1, 0.35 * np.sqrt(np.clip(1 - LR ** 2, 0, 1)), 0.0)
    for k, (zz, name) in enumerate(((dome, "凸（隆起）"), (-dome, "凹（下陷）"))):
        for m, (az, alt, lname) in enumerate(((315, 38, "主光 左上 38°"), (290, 18, "侧光 左 18°"))):
            hs = LightSource(azdeg=az, altdeg=alt).hillshade(zz, vert_exag=1.0, dx=lx[1] - lx[0], dy=lx[1] - lx[0])
            axl = fig.add_axes([0.70 + (k * 2 + m) * 0.062, 0.875, 0.055, 0.075])
            axl.imshow(np.clip(0.9 * (0.12 + 1.15 * hs), 0, 1), cmap="gray", vmin=0, vmax=1, origin="lower")
            axl.set_xticks([])
            axl.set_yticks([])
            axl.set_title(f"{name}\n{lname}", fontsize=7.5, pad=2)
    fig.text(0.70, 0.985, "读图标定：同一盏灯下，凸起与凹陷的明暗分布相反", fontsize=9.5, va="top")
    out = A02 / "shaded-relief-v15.png"
    fig.savefig(out, facecolor="white")
    print(out)
    np.save("/tmp/dragon-scale-gate02/shaded-relief-v15-height.npy", Z.astype(np.float32))


if __name__ == "__main__":
    main()
