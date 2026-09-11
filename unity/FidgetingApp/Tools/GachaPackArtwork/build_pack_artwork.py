#!/usr/bin/env python3
"""Build the six sealed-Pack rasters (body, flap, foil mask) procedurally.

History (user review, 2026-09-08):
- 12:16 / 12:23  six grey bags → per-tier colour grading; abstract emblem →
  Premium Display Case silhouette (188 × 240, label plate + circular well).
- 12:55  `outline` emblem chosen; lower saturation.
- 13:20  precious-metal foil on the upper tiers.
- 13:33  "特别糊": output 2× (768 × 1024) so the 244 pt stage Pack is not
  upscaled on a 3× iPhone.
- 13:51  "所有字和图案都看不清，需要重新做 … pack 再扁平一些，更加贴合 slab 的
  形状": emblem and type are drawn here at full resolution; the pouch is
  narrowed to 280 × 375 (canvas px) so its face is close to the slab's
  188:240 proportion.
- 14:55  "完全没有厚度了 … 上下边缘加一点锯齿": volume cues and serrated
  tear edges.
- 15:03  "铝箔纸这种高级感完全没有了，就像是一个破纸片": the fully
  procedural matte surface is dropped. The foil comes back from the neutral
  photographic source (`ArtSource/GachaPacks/Neutral/`, upscaled 2× and
  re-sharpened, old emblem and baked print inpainted, columns squeezed
  336 → 280), with the procedural pillow/content/crease relief layered on
  top and the crisp vector emblem, metal foil and DIN type stamped last.
- 17:10 / 18:33  "中间这个图案还是不太好看，有没有陀螺相关的，极简一点的，有漂亮的
  曲率和粗细线条的对比" → six candidates; user approved A (tri-lobe spinner
  outline) and C (gyroscope rings). STANDARD–SIGNATURE carry the spinner,
  CHASE–1 OF 1 the gyroscope. Emblems are signed-distance strokes on a local
  8 px/unit raster so a filleted union can carry one thick contour while
  the inner rings stay thin.

Canvas is still 384 × 512 (authored units, ×S for pixels) so
`GachaPackOpeningRules` fractions keep working: fin rows 45–92 (flap raster
45–101 with the body's top rows duplicated), body rows 92–467, pouch columns
52–332. Those constants are mirrored in `GachaPackOpeningRules` and the
Gate 12 harness; change both together.

Deterministic; rerunning writes identical files. Usage:

    build_pack_artwork.py [--out DIR] [--sheet PNG]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve()
APP = HERE.parents[2]
SHIPPING = APP / "Assets" / "Plugins" / "iOS" / "GachaPacks"
SOURCE = APP / "ArtSource" / "GachaPacks" / "Neutral"
# Photo source pouch: columns 24–360, fin rows 45–101, body rows 92–466.
SOURCE_X = (24, 360)
# Baked print and old emblem to inpaint (y0, y1, x0, x1; source columns).
INPAINT_REGIONS = [(188, 380, 94, 294), (120, 176, 70, 244), (386, 422, 68, 304)]
GRAIN_BANK_ROWS = (104, 120)     # plain foil below the fin (ends 101), above the print (124)
UNSHARP = (2.0, 0.6)
# How much of the photo's own light/shade survives under the relief (1 = all).
# R051r (user 22:43 "褶皱再弱，金属/硬挺再强"): the photo's fine wrinkles are
# smoothed (σ PHOTO_SMOOTH px) and weighted down; contrast comes from the
# stretched light field and the specular streak instead.
# R051t (user 09-09 08:28 "表面更平整，不然破破烂烂"): relief 0.60 → 0.35,
# smoothing 1.4 → 2.6 px; only the broad folds survive.
# R051w (user 09-09 08:48 "褶皱太强，大幅降低这个 dent"): the upper-left
# diagonal was the specular streak riding on the photo fold. 0.35 → 0.15.
PHOTO_RELIEF = 0.15
PHOTO_SMOOTH = 2.6

TIERS = ["standard", "refined", "signature", "chase", "grail", "one-of-one"]
TIER_TITLES = {
    "standard": "STANDARD", "refined": "REFINED", "signature": "SIGNATURE",
    "chase": "CHASE", "grail": "GRAIL", "one-of-one": "1 OF 1",
}

# ---------------------------------------------------------------- canvas ----
S = 2                       # output pixels per authored canvas unit
CANVAS = (384, 512)         # authored units; Swift uses fractions of this
SUPER = 4                   # vector supersampling for masks and type

# Pouch layout in authored units. Mirrored by GachaPackOpeningRules:
#   authoredPackTopYFraction 45/512, authoredSeamYFraction 92/512,
#   authoredFlapSpanFraction 52/384…332/384, openingInsetFraction 0.125.
POUCH_X = (52, 332)
FIN_TOP = 45
SEAM = 92
FLAP_BOTTOM = 101           # flap raster duplicates body rows 92–101
BOTTOM_SEAL_TOP = 427
POUCH_BOTTOM = 467
SIDE_SEAL = 7
CORNER = 5
# Serrated tear edges on the top fin and bottom seal (user 14:55 "上下边缘加
# 一点锯齿，来暗示这个是可撕开的包装"). Teeth cut into the pouch, so the
# outer extents (rows 45 / 467) that Swift reads are unchanged.
TOOTH_PITCH = 8.0
TOOTH_DEPTH = 4.5

# The case inside the sachet (188 × 240 mm) still shapes the raised panel the
# foil drapes over; the printed emblem no longer draws the case itself.
SLAB_ASPECT = 188 / 240
SLAB_TOP, SLAB_HEIGHT = 186, 188   # inside the photo's embossed panel (y 184–378)

# Emblem, R051n (user 18:48 reference sheet: sharp four-point stars with
# concave flanks, tapered swoosh strokes). Drawn on a local raster covering
# EMBLEM_BOX; centre and radii in authored units.
# R052c: raised 8 units so the tier title clears the deepest emblem
# (1 OF 1 star bottom) inside the tighter inner frame.
EMBLEM_BOX = (92, 172, 292, 372)
EMBLEM_CX, EMBLEM_CY = 192.0, 272.0
# One emblem per tier (user 20:01 "每个 pack 有一个自己的图标"), ordered from
# a plain spinner up to the gyroscope star.
EMBLEMS = {
    "standard": "triple_swoosh",   # K
    "refined": "solid_star_cut",   # J
    "signature": "orbit_swoosh",   # G
    "chase": "cross_swoosh",       # I
    "grail": "twin_orbit",         # L
    "one-of-one": "star_gyro",     # H
}
STROKE_THIN = 0.9
# Four-point star as a superellipse (|x|/r)^n + (|y|/r)^n ≤ 1; n < 1 gives
# concave flanks and truly sharp tips.
STAR_EXPONENT = 0.55
# K: three tapered crescents chasing round a star.
SPINNER_ARC_START_ANGLES = (-90, 30, 150)
SPINNER_ARC_SPAN_DEGREES, SPINNER_ARC_RADIUS = 100, 70
SPINNER_ARC_WIDTH, SPINNER_ARC_PEAK = 9.0, 0.28   # max width, peak position 0–1
SPINNER_STAR_RADIUS, SPINNER_STAR_ROTATION = 30, 15
# J: solid tri-lobe spinner, star cut from the hub, hairline lobe rings.
SOLID_LOBE_ANGLES, SOLID_LOBE_DISTANCE = (-90, 30, 150), 44
SOLID_HUB_RADIUS, SOLID_LOBE_RADIUS, SOLID_FILLET = 36, 31, 8
SOLID_STAR_RADIUS, SOLID_LOBE_RING_RADIUS = 30, 14
# G: one tilted orbit, thick sweeping front thinning to a hairline; star hub.
ORBIT_AXES, ORBIT_TILT_DEGREES = (76, 30), -22
ORBIT_WIDTH_MAX, ORBIT_WIDTH_MIN, ORBIT_THICK_PHASE_DEGREES, ORBIT_TAPER = 10.0, 0.55, 110, 2.4
ORBIT_STAR_RADIUS = 34
# I: two opposed crescents form an open ring; a long diagonal star pierces it.
CROSS_AXES, CROSS_TILT_DEGREES = (60, 38), 35
CROSS_ARC_WIDTH, CROSS_ARC_PEAK = 5.0, 0.38
CROSS_STAR = (16, 96)             # (half-width, half-height), rotated with the tilt
# L: two hairline orbits at ±28° each with a thick front crescent; star hub.
TWIN_AXES, TWIN_TILT_DEGREES = (72, 24), 28
TWIN_ARC_WIDTH, TWIN_ARC_PEAK, TWIN_STAR_RADIUS = 6.5, 0.5, 30
# H: thin wide orbit, tall star axis, short cross star.
GYRO_ORBIT_AXES = (78, 27)
GYRO_AXIS_STAR = (22, 86)         # (half-width, half-height)
GYRO_CROSS_STAR = (52, 10)

# Type: DIN Condensed Bold (macOS Supplemental) with Arial Narrow fallback.
FONTS = [
    "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf",
]
TEXT_X = 91                 # R052c: 10 units inside the inner hairline
# R052c (user 09-09 15:02): inner frame pulled in to 18; type follows.
HEADLINE = [("FIDGET ARCHIVE", 131, 14), ("SERIES 01", 149, 14)]  # (text, top, size)
TITLE_TOP, TITLE_SIZE = 369, 22
TRACKING = 0.06             # em

# -------------------------------------------------------------- colour ------
# Duotone ramps (shadow, mid, highlight), matching GachaPackArcBackdropRules.
GRADES = {
    "standard": ((0.09, 0.09, 0.10), (0.56, 0.57, 0.60), (0.98, 0.98, 1.00)),
    "refined": ((0.04, 0.06, 0.12), (0.22, 0.32, 0.46), (0.80, 0.88, 0.96)),
    "signature": ((0.14, 0.06, 0.06), (0.52, 0.32, 0.30), (0.96, 0.86, 0.82)),
    "chase": ((0.12, 0.09, 0.03), (0.58, 0.47, 0.24), (0.98, 0.94, 0.82)),
    "grail": ((0.07, 0.03, 0.12), (0.34, 0.24, 0.44), (0.92, 0.88, 0.96)),
    "one-of-one": ((0.01, 0.01, 0.02), (0.13, 0.12, 0.15), (0.92, 0.92, 0.95)),
}
# R051p (user 2026-09-08 22:21 "饱和度过高，像零食"): mid-tones are authored
# muted (steel, dusty copper, antique brass, aubergine); the grey pull stays
# as a second, smaller step.
# User 12:55 "饱和度可以降低一点": mid-tones pulled part-way to grey.
# R051v (user 09-09 08:39 "饱和度还是太高，大幅度降低"): 0.45 → 0.72.
DESATURATE = {
    "standard": 0.0, "refined": 0.72, "signature": 0.72,
    "chase": 0.70, "grail": 0.74, "one-of-one": 0.0,
}
# Flat accent ink for tiers without metal.
ACCENTS = {
    "standard": (0.90, 0.92, 0.96),
    "refined": (0.35, 0.80, 1.00),
    "signature": (1.00, 0.62, 0.62),
    "chase": (1.00, 0.86, 0.36),
    "grail": (0.72, 0.52, 1.00),
    "one-of-one": (1.00, 0.72, 0.92),
}
# Precious-metal foil (dark, base, highlight). User 13:20.
METALS = {
    "standard": None,
    "refined": ((0.42, 0.46, 0.54), (0.80, 0.84, 0.92), (1.00, 1.00, 1.00)),   # silver
    "signature": ((0.48, 0.28, 0.24), (0.80, 0.58, 0.50), (0.98, 0.90, 0.84)),  # dusty rose gold
    "chase": ((0.48, 0.36, 0.12), (0.86, 0.72, 0.40), (0.98, 0.95, 0.80)),      # antique gold
    "grail": ((0.50, 0.38, 0.14), (0.88, 0.74, 0.42), (0.98, 0.95, 0.80)),      # gold on aubergine
    "one-of-one": ((0.55, 0.56, 0.60), (0.90, 0.91, 0.94), (1.00, 1.00, 1.00)), # platinum
}
STROKE_SCALE = {
    "standard": 1.0, "refined": 1.0, "signature": 1.1,
    "chase": 1.2, "grail": 1.2, "one-of-one": 1.3,
}
IRIDESCENCE_STRENGTH = 0.16
IRIDESCENCE_SATURATION = 0.62

# Surface. User 14:55 "完全没有厚度了": a broad pillow bulge, a soft raised
# slab where the case sits inside, and gathered creases at both seals give
# the sachet volume again without the old photo's puffiness.
# R051q (user 22:31 "硬挺感、金属感"): flatter pillow, sharper creases, a
# narrow specular streak on top of the soft sheen, and the whole light
# field stretched about 1.0 so folds read as metal, not fabric.
PILLOW_GAIN = 0.03
# R051x (user 09-09 08:54 "白色羽化模糊的背景去掉"): the raised-panel light
# and its drop shadow are off; the case footprint no longer shows through.
CONTENT_BULGE = 0.0
CONTENT_SHADOW = 0.0
# R051z (user 09-09 09:58 "四边缘能显出里面 slab 的轮廓，不然像装了几张纸"):
# the case edge shows as a narrow ridge with a soft shadow just outside and a
# tiny plateau lift — thickness, not the rejected bright plate.
# R052b: softer edge ("外边缘不这么尖锐"): wider ridge, wider shadow.
SLAB_RIDGE_GAIN, SLAB_RIDGE_WIDTH = 0.08, 3.2
SLAB_SHADOW_GAIN, SLAB_SHADOW_OFFSET, SLAB_SHADOW_WIDTH = 0.06, 5.0, 7.0
SLAB_PLATEAU_GAIN = 0.02
# R051z: metallic rim around the pouch outline so a specular has a surface
# to land on (user: "边缘增加一圈有金属光感的材质"). Authored units.
RIM_WIDTH, RIM_INSET = 3.2, 0.8
CREASE_GAIN = 0.03
SPECULAR_GAIN, SPECULAR_WIDTH = 0.08, 0.10   # R051w: 0.30/0.05 read as a crease
METAL_CONTRAST = 1.55
# R051y (user 09-09 09:06, after holo-card): the print (emblem, type, panel
# rim) ships as its own layer so the runtime can parallax it against the
# foil with device tilt. FRAME_* is the thin stamped rim around the embossed
# panel, holo-card's concentric card rim adapted to the sachet.
# R052a (user 09-09 10:15 "金边加到蓝框位置，把内容都框进来，加点修饰花纹"):
# the rim now frames the whole face — header, emblem and tier title — with
# chamfered corners, a tucked four-point star in each corner, an inner
# hairline and small diamonds on the edge midpoints. Authored units.
FRAME_BOX = (POUCH_X[0] + SIDE_SEAL + 4, 104, POUCH_X[1] - SIDE_SEAL - 4, 421)
FRAME_STROKE = 0.9
# R052b (user 09-09 10:54 "slab 边缘和内细线合成同一个框；倒角缓和；文字内移"):
# the inner hairline IS the case outline. INNER_BOX drives both the printed
# hairline and the embossed slab relief, with rounded (not chamfered) corners.
# R052c (user 09-09 15:02 "内圈还是太近，再向内收"): 11 → 18.
FRAME_INNER_INSET, INNER_RADIUS = 18.0, 9.0
INNER_BOX = (FRAME_BOX[0] + FRAME_INNER_INSET, FRAME_BOX[1] + FRAME_INNER_INSET,
             FRAME_BOX[2] - FRAME_INNER_INSET, FRAME_BOX[3] - FRAME_INNER_INSET)
FRAME_HAIRLINE = 0.45
# R052g (user 09-09 17:53 "这个能用圆角过渡吗"): outer frame corners are
# quarter arcs of FRAME_ARC_R, not 45° chamfers.
FRAME_CORNER, FRAME_ARC_R = 14.0, 8.0
FRAME_STAR_R, FRAME_STAR_INSET = 3.0, 6.2
FRAME_DIAMOND, FRAME_DIAMOND_GAP = 2.4, 4.0
# Share of the holographic sweep the plain foil takes (emblem/text = 1.0).
# R051v (user 09-09 08:39): the R051s panel film was rejected.
BODY_FOIL_ALPHA = 0.16   # R051z: the body is matte; metal (print + rim) carries the sweep
# R051v: precious-metal inks pulled toward grey so the stamps stay metal
# but stop reading as coloured print.
INK_DESATURATE = 0.30
PHOTO_GAMMA = 1.0
GRAIN_FINE = 0.002          # ± luminance, σ 0.6 px
GRAIN_MOTTLE = 0.0        # ± luminance, σ 3 px
EDGE_DARKEN = 0.20          # at the pouch edge, e-folding 7 px
SHEEN_GAIN = 0.05
RIDGE_PITCH = 3.0           # px, crimp ridges in the seal bands
RIDGE_GAIN = 0.05


# ------------------------------------------------------------- helpers ------
def px(v: float) -> float:
    return v * S


def luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def save_rgba(array: np.ndarray, path: Path) -> None:
    out = np.clip(array * 255 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(path, optimize=True)


def load_photo() -> np.ndarray:
    """Sealed neutral photo (body + fin), 2×, re-sharpened, old emblem and
    baked print inpainted, pouch columns squeezed to POUCH_X. Returns RGBA."""
    body = Image.open(SOURCE / "gacha-pack-standard-body.png").convert("RGBA")
    flap = Image.open(SOURCE / "gacha-pack-standard-flap.png").convert("RGBA")
    sealed = Image.new("RGBA", body.size, (0, 0, 0, 0))
    sealed.alpha_composite(body)
    sealed.alpha_composite(flap)
    sealed = sealed.resize((body.width * S, body.height * S), Image.LANCZOS)
    rgb = sealed.convert("RGB").filter(ImageFilter.UnsharpMask(
        radius=UNSHARP[0], percent=int(UNSHARP[1] * 100), threshold=2))
    sealed = Image.merge("RGBA", (*rgb.split(), sealed.split()[3]))
    rgba = np.asarray(sealed).astype(float) / 255.0
    rgba = inpaint(rgba)
    # Squeeze the pouch columns 24–360 → 52–332 (rows unchanged).
    h, w = rgba.shape[:2]
    sx0, sx1 = (int(px(v)) for v in SOURCE_X)
    dx0, dx1 = (int(px(v)) for v in POUCH_X)
    strip = Image.fromarray(np.clip(rgba[:, sx0:sx1] * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
    strip = strip.resize((dx1 - dx0, h), Image.LANCZOS)
    out = np.zeros_like(rgba)
    out[:, dx0:dx1] = np.asarray(strip).astype(float) / 255.0
    return out


def inpaint(rgba: np.ndarray) -> np.ndarray:
    """Fill the old emblem and baked print: low frequency from the nearest
    untouched pixels, micro-grain tiled from plain foil above the print."""
    rgb = rgba[..., :3]
    hole = np.zeros(rgba.shape[:2], bool)
    for y0, y1, x0, x1 in INPAINT_REGIONS:
        hole[int(px(y0)):int(px(y1)), int(px(x0)):int(px(x1))] = True
    hole = ndimage.binary_dilation(hole, iterations=2 * S)
    _, (iy, ix) = ndimage.distance_transform_edt(hole, return_indices=True)
    low = ndimage.gaussian_filter(rgb[iy, ix], (14 * S, 14 * S, 0))
    texture = rgb - ndimage.gaussian_filter(rgb, (3 * S, 3 * S, 0))
    b0, b1 = (int(px(v)) for v in GRAIN_BANK_ROWS)
    # Columns 60–324 only: the side-seal edges have strong high-pass that
    # would tile into the panel as periodic marks.
    bank = texture[b0:b1, int(px(60)):int(px(324))]
    rng = np.random.default_rng(7)
    grain = np.zeros_like(texture)
    y = 0
    flip = False
    while y < grain.shape[0]:
        strip = bank[::-1] if flip else bank
        strip = np.roll(strip, int(rng.integers(0, bank.shape[1])), axis=1)
        n = min(strip.shape[0], grain.shape[0] - y)
        grain[y:y + n, int(px(60)):int(px(324))] = strip[:n]
        y += n
        flip = not flip
    filled = low + np.clip(grain, -0.05, 0.05) * 0.85
    blend = ndimage.gaussian_filter(hole.astype(float), 2.0 * S)[..., None]
    out = rgba.copy()
    out[..., :3] = rgb * (1 - blend) + filled * blend
    return out


def _canvas_L():
    return Image.new("L", (CANVAS[0] * S * SUPER, CANVAS[1] * S * SUPER), 0)


def _down(img: Image.Image) -> np.ndarray:
    return np.asarray(img.resize((CANVAS[0] * S, CANVAS[1] * S), Image.LANCZOS)).astype(float) / 255


def _box(box):
    return tuple(v * S * SUPER for v in box)


def rounded_rect(box, radius, width=0) -> np.ndarray:
    """Filled (width=0) or stroked rounded rectangle mask. Units: authored."""
    img = _canvas_L()
    draw = ImageDraw.Draw(img)
    if width:
        draw.rounded_rectangle(_box(box), radius=radius * S * SUPER, outline=255, width=max(1, round(width * S * SUPER)))
    else:
        draw.rounded_rectangle(_box(box), radius=radius * S * SUPER, fill=255)
    return _down(img)


def ellipse(box, width=0) -> np.ndarray:
    img = _canvas_L()
    draw = ImageDraw.Draw(img)
    if width:
        draw.ellipse(_box(box), outline=255, width=max(1, round(width * S * SUPER)))
    else:
        draw.ellipse(_box(box), fill=255)
    return _down(img)


def load_font(size_units: float) -> ImageFont.FreeTypeFont:
    for path in FONTS:
        if Path(path).exists():
            return ImageFont.truetype(path, int(round(size_units * S * SUPER)))
    raise SystemExit("no usable font: " + ", ".join(FONTS))


def text_mask(text: str, left: float, top: float, size: float) -> np.ndarray:
    """Tracked caps drawn at SUPER×, returned as a soft mask."""
    img = _canvas_L()
    draw = ImageDraw.Draw(img)
    font = load_font(size)
    x = left * S * SUPER
    y = top * S * SUPER
    track = TRACKING * size * S * SUPER
    for ch in text:
        draw.text((x, y), ch, font=font, fill=255)
        x += draw.textlength(ch, font=font) + track
    return _down(img)


def shift(mask: np.ndarray, dx: float, dy: float) -> np.ndarray:
    return ndimage.shift(mask, (dy * S, dx * S), order=1, mode="constant", cval=0)


def metal_ink(shape, tier: str, anchor, size) -> np.ndarray:
    """Per-pixel foil colour: flat accent, or a precious-metal ramp with a
    diagonal highlight band so strokes read as stamped foil."""
    if METALS[tier] is None:
        return np.broadcast_to(np.array(ACCENTS[tier]), shape + (3,)).copy()
    dark, base, high = (np.array(c) for c in METALS[tier])
    dark, base, high = (c + (luminance(c[None, None])[0, 0] - c) * INK_DESATURATE for c in (dark, base, high))
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    ax, ay = (px(v) for v in anchor)
    w, h = (px(v) for v in size)
    diag = ((xx - ax) / w) * 0.6 + ((yy - ay) / h) * 0.8
    band = np.exp(-((diag - 0.55) / 0.22) ** 2)
    shade = np.clip(0.40 + 0.45 * (1.0 - diag / 1.4), 0, 1)
    rgb = dark + (base - dark) * shade[..., None]
    return rgb + (high - rgb) * (band * 0.85)[..., None]


def _over(out: np.ndarray, colour: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Source-over composite of a flat colour with per-pixel alpha onto RGBA."""
    a_old = out[..., 3:4]
    a = alpha[..., None]
    a_new = a + a_old * (1 - a)
    rgb = (colour * a + out[..., :3] * a_old * (1 - a)) / np.maximum(a_new, 1e-6)
    return np.concatenate([rgb, a_new], axis=-1)


def print_layer(shape, marks, ink: np.ndarray) -> np.ndarray:
    """Stand-alone RGBA print: for each (mask, depth) the stamp's dark shadow
    down-right, light lip up-left and the ink itself, over transparency."""
    out = np.zeros(shape + (4,))
    black = np.zeros(shape + (3,))
    white = np.ones(shape + (3,))
    for mask, depth in marks:
        shadow = np.clip(shift(mask, 0.9 * depth, 0.9 * depth) - mask, 0, 1) * 0.55
        lip = np.clip(shift(mask, -0.6 * depth, -0.6 * depth) - mask, 0, 1) * 0.18
        out = _over(out, black, shadow)
        out = _over(out, white, lip)
        out = _over(out, ink, mask)
    return out


def rim_mask(pouch: np.ndarray) -> np.ndarray:
    """Metallic band along the pouch outline (R051z), inset so the
    anti-aliased edge stays foil."""
    dist = ndimage.distance_transform_edt(pouch > 0.5)
    inner_edge = np.clip((px(RIM_INSET + RIM_WIDTH) - dist) / px(0.8), 0, 1)
    outer_edge = np.clip((dist - px(RIM_INSET)) / px(0.8), 0, 1)
    return inner_edge * outer_edge * (pouch > 0.5)


def _star_polygon(cx, cy, r, samples=96):
    """Four-point star outline, same superellipse family as the emblems."""
    pts = []
    for i in range(samples):
        t = 2 * np.pi * i / samples
        c, sn = np.cos(t), np.sin(t)
        pts.append((cx + r * np.sign(c) * abs(c) ** (2 / STAR_EXPONENT),
                    cy + r * np.sign(sn) * abs(sn) ** (2 / STAR_EXPONENT)))
    return pts


def frame_mask(shell=None) -> np.ndarray:
    """Ornate face frame (R052a). Straight rules with chamfered corners, a
    small star tucked inside each corner, an inner hairline that stops short
    of the corners, and a diamond on each edge midpoint."""
    x0, y0, x1, y1 = FRAME_BOX
    k = S * SUPER
    img = _canvas_L()
    draw = ImageDraw.Draw(img)
    w = max(1, round(FRAME_STROKE * k))
    ch = FRAME_ARC_R
    g, d = FRAME_DIAMOND_GAP, FRAME_DIAMOND
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2

    def line(a, b):
        draw.line([(a[0] * k, a[1] * k), (b[0] * k, b[1] * k)], fill=255, width=w)

    # Edges, broken at the midpoint diamonds.
    line((x0 + ch, y0), (xm - g, y0)); line((xm + g, y0), (x1 - ch, y0))
    line((x0 + ch, y1), (xm - g, y1)); line((xm + g, y1), (x1 - ch, y1))
    line((x0, y0 + ch), (x0, ym - g)); line((x0, ym + g), (x0, y1 - ch))
    line((x1, y0 + ch), (x1, ym - g)); line((x1, ym + g), (x1, y1 - ch))
    # Rounded corners: quarter arcs tangent to the edges.
    def arc(cx, cy, start, end):
        draw.arc([((cx - ch) * k, (cy - ch) * k), ((cx + ch) * k, (cy + ch) * k)],
                 start, end, fill=255, width=w)
    arc(x0 + ch, y0 + ch, 180, 270); arc(x1 - ch, y0 + ch, 270, 360)
    arc(x1 - ch, y1 - ch, 0, 90); arc(x0 + ch, y1 - ch, 90, 180)
    # Midpoint diamonds.
    for (mx, my) in ((xm, y0), (xm, y1), (x0, ym), (x1, ym)):
        draw.polygon([((mx) * k, (my - d) * k), ((mx + d) * k, my * k),
                      (mx * k, (my + d) * k), ((mx - d) * k, my * k)], fill=255)
    # Inner hairline: the case outline itself (rounded corners), continuous.
    draw.rounded_rectangle(_box(INNER_BOX), radius=INNER_RADIUS * k, outline=255,
                           width=max(1, round(FRAME_HAIRLINE * k)))
    # Corner stars, tucked inside the rounded corner.
    si = FRAME_STAR_INSET
    for (cx, cy) in ((x0 + si, y0 + si), (x1 - si, y0 + si), (x0 + si, y1 - si), (x1 - si, y1 - si)):
        draw.polygon([(px_ * k, py_ * k) for px_, py_ in _star_polygon(cx, cy, FRAME_STAR_R)], fill=255)
    return _down(img)


def stamp(rgb: np.ndarray, mask: np.ndarray, ink: np.ndarray, depth: float) -> np.ndarray:
    """Foil-stamp `mask` onto `rgb`: crisp dark shadow down-right, faint
    light lip up-left, then the ink itself."""
    shadow = np.clip(shift(mask, 0.9 * depth, 0.9 * depth) - mask, 0, 1)
    lip = np.clip(shift(mask, -0.6 * depth, -0.6 * depth) - mask, 0, 1)
    out = rgb * (1 - shadow[..., None] * 0.55)
    out = out + lip[..., None] * 0.18
    return out * (1 - mask[..., None]) + ink * mask[..., None]


# ------------------------------------------------------------- surface ------
def base_colour(tier: str) -> np.ndarray:
    _, mid, _ = (np.array(c) for c in GRADES[tier])
    grey = luminance(mid[None, None])[0, 0]
    return mid + (grey - mid) * DESATURATE[tier]


def tone(rgb_base: np.ndarray, light: np.ndarray, tier: str) -> np.ndarray:
    """Map a light field (1 = base) through the tier's duotone so highlights
    and shadows keep the metal's own hue, not just brighter/darker base."""
    shadow, _, high = (np.array(c) for c in GRADES[tier])
    grey = luminance(shadow[None, None])[0, 0]
    shadow = shadow + (grey - shadow) * DESATURATE[tier]
    grey = luminance(high[None, None])[0, 0]
    high = high + (grey - high) * DESATURATE[tier] * 0.5
    t = light[..., None]
    lower = shadow + (rgb_base - shadow) * np.clip(t, 0, 1)
    upper = rgb_base + (high - rgb_base) * np.clip((t - 1) / 0.8, 0, 1)
    return np.where(t < 1, lower, upper)


def polygon(points) -> np.ndarray:
    img = _canvas_L()
    ImageDraw.Draw(img).polygon([(x * S * SUPER, y * S * SUPER) for x, y in points], fill=255)
    return _down(img)


def serrated_band(edge_y: float, inward: int) -> np.ndarray:
    """Half-plane whose boundary is a zigzag along `edge_y`; `inward` +1 keeps
    what lies below the teeth (top edge), -1 what lies above (bottom edge)."""
    x0, x1 = POUCH_X
    n = int(round((x1 - x0) / TOOTH_PITCH))
    pitch = (x1 - x0) / n
    pts = []
    for i in range(n + 1):
        x = x0 + i * pitch
        pts.append((x, edge_y))                                     # tip
        if i < n:
            pts.append((x + pitch / 2, edge_y + inward * TOOTH_DEPTH))  # valley
    far = CANVAS[1] if inward > 0 else 0
    return polygon(pts + [(x1, far), (x0, far)])


def pouch_masks():
    # R052f: the body's top corners are square at the seam (the fin above is
    # square too), so the pouch outline has no notch there and the body's
    # top rim meets the side rims in a clean T after the tear.
    body = rounded_rect((POUCH_X[0], SEAM - CORNER, POUCH_X[1], POUCH_BOTTOM + CORNER), CORNER)
    body = body * serrated_band(POUCH_BOTTOM, -1)
    body = body * rounded_rect((0, SEAM, CANVAS[0], CANVAS[1]), 0)
    fin = rounded_rect((POUCH_X[0], FIN_TOP - CORNER, POUCH_X[1], SEAM + CORNER), CORNER)
    fin = fin * serrated_band(FIN_TOP, +1)
    fin = fin * (1 - rounded_rect((0, SEAM, CANVAS[0], CANVAS[1]), 0))
    pouch = np.clip(body + fin, 0, 1)
    return pouch, body, fin


def light_field(pouch: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    h, w = pouch.shape
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx - px(POUCH_X[0])) / px(POUCH_X[1] - POUCH_X[0])
    v = (yy - px(FIN_TOP)) / px(POUCH_BOTTOM - FIN_TOP)

    light = 1.0 + 0.08 * (0.5 - (u * 0.55 + v * 0.45))         # key from top-left
    diag = u * 0.6 + v * 0.8
    light += SHEEN_GAIN * np.exp(-((diag - 0.42) / 0.16) ** 2)  # one soft sheen band
    light += SPECULAR_GAIN * np.exp(-((diag - 0.40) / SPECULAR_WIDTH) ** 2)  # crisp metal streak

    # Volume: pillow bulge across the face between the two seals.
    fv = (yy - px(SEAM)) / px(BOTTOM_SEAL_TOP - SEAM)
    bulge = np.sqrt(np.clip(1 - (2 * u - 1) ** 2, 0, 1)) * np.sqrt(np.clip(1 - (2 * fv - 1) ** 2, 0, 1))
    light += PILLOW_GAIN * (bulge - 0.55)
    # The case inside presses a soft raised rectangle into the foil. R052b:
    # its outline is INNER_BOX, the same rectangle the printed hairline traces.
    inner = rounded_rect(INNER_BOX, INNER_RADIUS)
    raised = ndimage.gaussian_filter(inner, px(9))
    light += CONTENT_BULGE * raised
    light -= CONTENT_SHADOW * np.clip(ndimage.gaussian_filter(shift(inner, 5, 7), px(7)) - raised, 0, 1)
    # R051z slab edge: signed distance to the case outline (px, + outside).
    signed = ndimage.distance_transform_edt(inner <= 0.5) - ndimage.distance_transform_edt(inner > 0.5)
    light += SLAB_RIDGE_GAIN * np.exp(-((signed + px(1.0)) / px(SLAB_RIDGE_WIDTH)) ** 2)
    light -= SLAB_SHADOW_GAIN * np.exp(-((signed - px(SLAB_SHADOW_OFFSET)) / px(SLAB_SHADOW_WIDTH)) ** 2) * (signed > 0)
    light += SLAB_PLATEAU_GAIN * ndimage.gaussian_filter(inner, px(4))
    # Gathered creases where the face meets each seal.
    for edge, sign in ((SEAM, 1), (BOTTOM_SEAL_TOP, -1)):
        d = (yy - px(edge)) * sign
        light -= CREASE_GAIN * np.exp(-((d - px(3)) / px(2.2)) ** 2) * (0.7 + 0.3 * np.cos(xx / px(11)))
        light += CREASE_GAIN * 0.6 * np.exp(-((d - px(8)) / px(3)) ** 2)

    dist = ndimage.distance_transform_edt(pouch > 0.5)
    light -= EDGE_DARKEN * np.exp(-dist / px(7))                # rolled edge

    # Side seals: slightly darker with a light inner rule.
    for x_edge, sign in ((POUCH_X[0], 1), (POUCH_X[1], -1)):
        dx = (xx - px(x_edge)) * sign
        seal = (dx >= 0) & (dx < px(SIDE_SEAL))
        light -= 0.06 * seal
        light += 0.05 * np.exp(-((dx - px(SIDE_SEAL)) / px(0.7)) ** 2)

    # Crimp ridges in the top fin and bottom seal.
    ridge = 0.5 + 0.5 * np.sin(2 * np.pi * yy / px(RIDGE_PITCH) + 0.6 * np.sin(xx / px(9)))
    in_fin = (yy >= px(FIN_TOP)) & (yy < px(SEAM))
    in_bottom = (yy >= px(BOTTOM_SEAL_TOP)) & (yy < px(POUCH_BOTTOM))
    band = in_fin | in_bottom
    light += band * (RIDGE_GAIN * (ridge - 0.5) - 0.04)
    seam_line = np.exp(-((yy - px(SEAM)) / px(0.8)) ** 2) + np.exp(-((yy - px(BOTTOM_SEAL_TOP)) / px(0.8)) ** 2)
    light -= 0.10 * seam_line

    fine = ndimage.gaussian_filter(rng.standard_normal((h, w)), 0.6 * S)
    fine /= fine.std() + 1e-6
    mottle = ndimage.gaussian_filter(rng.standard_normal((h, w)), 3 * S)
    mottle /= mottle.std() + 1e-6
    light += GRAIN_FINE * fine + GRAIN_MOTTLE * mottle
    return light


def iridesce(rgb: np.ndarray, light: np.ndarray) -> np.ndarray:
    h, w = light.shape
    yy, xx = np.mgrid[0:h, 0:w]
    hue = ((xx / w) * 0.9 + (yy / h) * 0.6) % 1.0
    k = (hue * 6.0)[..., None] + np.array([0.0, 4.0, 2.0])
    spectrum = 1 - IRIDESCENCE_SATURATION * np.clip(np.abs((k % 6.0) - 3.0) - 1.0, 0, 1)
    gain = (np.clip(light - 0.9, 0, None) ** 1.6)[..., None] * IRIDESCENCE_STRENGTH * 4
    return rgb + spectrum * gain


# -------------------------------------------------------------- emblem ------
def slab_geometry():
    """Footprint of the case inside the sachet (drives the raised panel)."""
    cx = (POUCH_X[0] + POUCH_X[1]) / 2
    height = SLAB_HEIGHT
    width = height * SLAB_ASPECT
    shell = (cx - width / 2, SLAB_TOP, cx + width / 2, SLAB_TOP + height)
    return shell, width, height


class _EmblemRaster:
    """Local raster over EMBLEM_BOX at S × SUPER px per authored unit. Shapes
    are boolean fields; strokes come from a signed distance field so any
    union carries a clean outline of exact width."""

    def __init__(self):
        self.ss = S * SUPER
        x0, y0, x1, y1 = EMBLEM_BOX
        h, w = int((y1 - y0) * self.ss), int((x1 - x0) * self.ss)
        yy, xx = np.mgrid[0:h, 0:w]
        self.ux = xx / self.ss + x0
        self.uy = yy / self.ss + y0
        self.shape = (h, w)

    def disk(self, cx, cy, r):
        return (self.ux - cx) ** 2 + (self.uy - cy) ** 2 <= r * r

    def ellipse(self, cx, cy, a, b, degrees):
        t = np.deg2rad(degrees)
        x, y = self.ux - cx, self.uy - cy
        xr = x * np.cos(t) + y * np.sin(t)
        yr = -x * np.sin(t) + y * np.cos(t)
        return (xr / a) ** 2 + (yr / b) ** 2 <= 1

    def fillet(self, mask, radius_units):
        """Round concave joins by blur + threshold."""
        return ndimage.gaussian_filter(mask.astype(float), radius_units * self.ss) > 0.5

    def sdf(self, mask):
        return ndimage.distance_transform_edt(~mask) - ndimage.distance_transform_edt(mask)

    def outline(self, mask, width_units):
        half = width_units * self.ss / 2
        return np.clip(half - np.abs(self.sdf(mask)) + 0.5, 0, 1)

    def fill(self, mask):
        return np.clip(-self.sdf(mask) + 0.5, 0, 1)

    def swept(self, curve, width_fn, n=160):
        """Variable-width stroke along curve(t) → (x, y), t ∈ [0, 1]."""
        ts = np.linspace(0, 1, n)
        pts = np.array([curve(t) for t in ts])
        d = np.gradient(pts, axis=0)
        nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
        half = np.array([width_fn(t) for t in ts])[:, None] / 2
        ring = np.concatenate([pts + nrm * half, (pts - nrm * half)[::-1]])
        img = Image.new("L", (self.shape[1], self.shape[0]), 0)
        ImageDraw.Draw(img).polygon(
            [((x - EMBLEM_BOX[0]) * self.ss, (y - EMBLEM_BOX[1]) * self.ss) for x, y in ring], fill=255)
        return np.asarray(img) > 127

    def star4(self, cx, cy, rx, ry, degrees=0.0):
        """Four-point star: (|x|/rx)^n + (|y|/ry)^n ≤ 1 with n = STAR_EXPONENT."""
        t = np.deg2rad(degrees)
        x, y = self.ux - cx, self.uy - cy
        xr = x * np.cos(t) + y * np.sin(t)
        yr = -x * np.sin(t) + y * np.cos(t)
        n = STAR_EXPONENT
        return (np.abs(xr) / rx) ** n + (np.abs(yr) / ry) ** n <= 1

    def crescent(self, cx, cy, a, b, tilt_degrees, start_degrees, end_degrees, width, peak):
        """Elliptical arc whose width rises from a point to `width` (at
        fraction `peak` of the arc) and falls back to a point."""
        t = np.deg2rad(tilt_degrees)
        a0, a1 = np.deg2rad(start_degrees), np.deg2rad(end_degrees)
        exponent = np.log(0.5) / np.log(peak)

        def curve(s):
            ang = a0 + (a1 - a0) * s
            x, y = a * np.cos(ang), b * np.sin(ang)
            return (cx + x * np.cos(t) - y * np.sin(t), cy + x * np.sin(t) + y * np.cos(t))

        def width_fn(s):
            return max(width * np.sin(np.pi * s ** exponent) ** 0.9, 0.15)

        return self.swept(curve, width_fn, n=220)

    def tapered_ring(self, cx, cy, a, b, tilt_degrees, width_max, width_min, phase_degrees, taper):
        """Closed ellipse whose stroke swells once around (thickest at
        `phase_degrees`). Outer and inner loops are separate polygons; the
        band is their XOR."""
        t = np.deg2rad(tilt_degrees)
        ph = np.deg2rad(phase_degrees)
        ts = np.linspace(0, 1, 360, endpoint=False)
        ang = 2 * np.pi * ts
        x, y = a * np.cos(ang), b * np.sin(ang)
        pts = np.stack([cx + x * np.cos(t) - y * np.sin(t), cy + x * np.sin(t) + y * np.cos(t)], axis=1)
        d = np.gradient(np.vstack([pts[-1:], pts, pts[:1]]), axis=0)[1:-1]
        nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
        c = 0.5 + 0.5 * np.cos(ang - ph)
        half = (width_min + (width_max - width_min) * c ** taper)[:, None] / 2
        return self._poly(pts + nrm * half) ^ self._poly(pts - nrm * half)

    def _poly(self, ring):
        img = Image.new("L", (self.shape[1], self.shape[0]), 0)
        ImageDraw.Draw(img).polygon(
            [((x - EMBLEM_BOX[0]) * self.ss, (y - EMBLEM_BOX[1]) * self.ss) for x, y in ring], fill=255)
        return np.asarray(img) > 127

    def to_canvas(self, local):
        h, w = local.shape
        down = local.reshape(h // SUPER, SUPER, w // SUPER, SUPER).mean(axis=(1, 3))
        full = np.zeros((CANVAS[1] * S, CANVAS[0] * S))
        y0, x0 = EMBLEM_BOX[1] * S, EMBLEM_BOX[0] * S
        full[y0:y0 + down.shape[0], x0:x0 + down.shape[1]] = down
        return np.clip(full, 0, 1)


def triple_swoosh_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """K: three tapered crescents (sharp tip → wide → sharp tip) chasing
    round a four-point star."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    m = np.zeros(r.shape)
    for a0 in SPINNER_ARC_START_ANGLES:
        m = np.maximum(m, r.fill(r.crescent(
            cx, cy, SPINNER_ARC_RADIUS, SPINNER_ARC_RADIUS, 0,
            a0, a0 + SPINNER_ARC_SPAN_DEGREES, SPINNER_ARC_WIDTH * k, SPINNER_ARC_PEAK)))
    return np.maximum(m, r.fill(r.star4(
        cx, cy, SPINNER_STAR_RADIUS, SPINNER_STAR_RADIUS, SPINNER_STAR_ROTATION)))


def solid_star_cut_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """J: solid tri-lobe spinner silhouette with a star cut from the hub and
    hairline rings on the lobes."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    lobes = [(cx + SOLID_LOBE_DISTANCE * np.cos(np.deg2rad(a)),
              cy + SOLID_LOBE_DISTANCE * np.sin(np.deg2rad(a))) for a in SOLID_LOBE_ANGLES]
    body = r.disk(cx, cy, SOLID_HUB_RADIUS)
    for lx, ly in lobes:
        body |= r.disk(lx, ly, SOLID_LOBE_RADIUS)
    m = r.fill(r.fillet(body, SOLID_FILLET))
    cut = r.fill(r.star4(cx, cy, SOLID_STAR_RADIUS, SOLID_STAR_RADIUS))
    for lx, ly in lobes:
        cut = np.maximum(cut, r.outline(r.disk(lx, ly, SOLID_LOBE_RING_RADIUS), STROKE_THIN * k))
    return np.clip(m - cut, 0, 1)


def orbit_swoosh_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """G: one tilted orbit whose stroke swells once (thick sweeping front,
    hairline back) round a star hub."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    a, b = ORBIT_AXES
    ring = r.tapered_ring(
        cx, cy, a, b, ORBIT_TILT_DEGREES,
        ORBIT_WIDTH_MAX * k, ORBIT_WIDTH_MIN * k, ORBIT_THICK_PHASE_DEGREES, ORBIT_TAPER)
    return np.maximum(r.fill(ring), r.fill(r.star4(cx, cy, ORBIT_STAR_RADIUS, ORBIT_STAR_RADIUS)))


def cross_swoosh_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """I: two opposed crescents form an open ring; a long diagonal star
    pierces it along the tilt."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    a, b = CROSS_AXES
    m = np.zeros(r.shape)
    for a0, a1 in ((25, 205), (205, 385)):
        m = np.maximum(m, r.fill(r.crescent(
            cx, cy, a, b, CROSS_TILT_DEGREES, a0, a1, CROSS_ARC_WIDTH * k, CROSS_ARC_PEAK)))
    return np.maximum(m, r.fill(r.star4(cx, cy, *CROSS_STAR, CROSS_TILT_DEGREES)))


def twin_orbit_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """L: two hairline orbits crossing at ±tilt, each with one thick front
    crescent; star hub."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    a, b = TWIN_AXES
    m = np.zeros(r.shape)
    for tilt in (-TWIN_TILT_DEGREES, TWIN_TILT_DEGREES):
        m = np.maximum(m, r.outline(r.ellipse(cx, cy, a, b, tilt), 0.9 * STROKE_THIN * k))
        m = np.maximum(m, r.fill(r.crescent(
            cx, cy, a, b, tilt, 15, 165, TWIN_ARC_WIDTH * k, TWIN_ARC_PEAK)))
    return np.maximum(m, r.fill(r.star4(cx, cy, TWIN_STAR_RADIUS, TWIN_STAR_RADIUS)))


def star_gyro_emblem(r: _EmblemRaster, k: float) -> np.ndarray:
    """H: one wide hairline orbit; the axis is a tall star whose tips fade to
    points, crossed by a short star at the hub."""
    cx, cy = EMBLEM_CX, EMBLEM_CY
    a, b = GYRO_ORBIT_AXES
    m = r.outline(r.ellipse(cx, cy, a, b, 0), 1.2 * STROKE_THIN * k)
    m = np.maximum(m, r.fill(r.star4(cx, cy, *GYRO_AXIS_STAR)))
    return np.maximum(m, r.fill(r.star4(cx, cy, *GYRO_CROSS_STAR)))


EMBLEM_DRAWERS = {
    "triple_swoosh": triple_swoosh_emblem,
    "solid_star_cut": solid_star_cut_emblem,
    "orbit_swoosh": orbit_swoosh_emblem,
    "cross_swoosh": cross_swoosh_emblem,
    "twin_orbit": twin_orbit_emblem,
    "star_gyro": star_gyro_emblem,
}


def emblem_mask(tier: str) -> np.ndarray:
    r = _EmblemRaster()
    return r.to_canvas(EMBLEM_DRAWERS[EMBLEMS[tier]](r, STROKE_SCALE[tier]))


def type_mask() -> tuple[np.ndarray, np.ndarray]:
    head = np.zeros((CANVAS[1] * S, CANVAS[0] * S))
    for text, top, size in HEADLINE:
        head = np.maximum(head, text_mask(text, TEXT_X, top, size))
    return head


# --------------------------------------------------------------- build ------
def build_tier(tier: str, out_dir: Path) -> np.ndarray:
    h, w = CANVAS[1] * S, CANVAS[0] * S
    rng = np.random.default_rng(20260908)
    pouch, body, fin = pouch_masks()

    photo = load_photo()
    photo_lum = np.clip(luminance(photo[..., :3]), 0, 1)
    photo_lum = ndimage.gaussian_filter(photo_lum, PHOTO_SMOOTH * S)
    # Photo folds carry the foil; the procedural relief (pillow, content
    # bulge, creases, serrated rolled edge) rides on top. Photo mean ≈ 0.42.
    relief = light_field(pouch, rng)
    # R051u (user 09-09 08:32 "把这个熨平"): the photo's brightness used to
    # multiply in at full strength whatever PHOTO_RELIEF said, so the bright
    # top-left fold survived every smoothing pass. Blend it toward flat.
    photo_term = 1 + ((photo_lum / 0.42) ** PHOTO_GAMMA - 1) * PHOTO_RELIEF
    light = photo_term * relief
    light = 1 + (light - 1) * METAL_CONTRAST
    rgb = tone(base_colour(tier), light, tier)
    if tier == "one-of-one":
        # Spectrum follows the broad sheen, not the grain (no colour speckle).
        rgb = iridesce(rgb, ndimage.gaussian_filter(light, 4 * S))

    shell, *_ = slab_geometry()
    ink = metal_ink((h, w), tier, (POUCH_X[0], FIN_TOP), (POUCH_X[1] - POUCH_X[0], POUCH_BOTTOM - FIN_TOP))
    emblem = emblem_mask(tier)
    head = type_mask()
    title = text_mask(TIER_TITLES[tier], TEXT_X, TITLE_TOP, TITLE_SIZE)
    frame = frame_mask(shell)
    # R052e (user 09-09 16:25 "撕开的边缘好像比卡包靠后"): the body's rim is
    # computed on the body alone, so it closes along the top edge at the seam.
    # Once the lid is off, the mouth is a rimmed foil edge on the Pack's own
    # plane instead of a bare cut with a dark hole behind it.
    # R052f (user 09-09 17:09 "线是断的"): the body is square at the seam, so
    # the top rim meets the side rims in a T and the fin's rim runs straight
    # through the seam.
    rim = rim_mask(body)
    fin_rim = rim_mask(pouch)
    depth = 1.0 * STROKE_SCALE[tier]
    type_marks = np.clip(head + title, 0, 1)
    surface = np.clip(rgb, 0, 1)
    printed = print_layer(
        (h, w),
        [(rim, depth * 0.35), (frame, depth * 0.5), (emblem, depth), (type_marks, depth * 0.7)],
        ink)
    printed[..., 3] *= pouch > 0.5
    # R052d (user 09-09 15:23 "撕开之后锯齿的银色描边依然存在"): the runtime
    # print overlay never tears, so it may only cover the body rows. The fin's
    # share of the rim is baked into the flap raster and leaves with the lid.
    seam_row = int(px(SEAM))
    fin_print = print_layer((h, w), [(fin_rim, depth * 0.35)], ink)
    fin_print[seam_row:, :, 3] = 0
    printed[:seam_row, :, 3] = 0

    # Body/flap carry the bare foil; the print composites on top at runtime.
    sealed = np.zeros((h, w, 4))
    sealed[..., :3] = surface
    sealed[..., 3] = pouch
    # Contact sheets and downstream tools still see the sealed Pack whole.
    composite = _over(sealed.copy(), printed[..., :3], printed[..., 3])
    composite = _over(composite, fin_print[..., :3], fin_print[..., 3])

    body_png = sealed.copy()
    body_png[..., 3] *= body
    body_png[:seam_row, :, 3] = 0

    flap_png = _over(sealed.copy(), fin_print[..., :3], fin_print[..., 3])
    flap_png[int(px(FLAP_BOTTOM)):, :, 3] = 0
    flap_png[: int(px(FIN_TOP)), :, 3] = 0

    foil = np.zeros((h, w, 4))
    foil[..., :3] = 1.0
    # R051v (user 09-09 08:39): the panel film is gone; instead the whole
    # pouch takes the laser sweep at BODY_FOIL_ALPHA and the emblem/text at 1.
    foil[..., 3] = np.clip(np.maximum(np.maximum(np.maximum(emblem, type_marks), frame), rim), 0, 1)
    # R052d: the sheen mask does not tear either, so it stops at the seam:
    # otherwise a ghost band (and the rim's bright serration) lingers where
    # the fin was. The sealed fin keeps only its baked foil.
    foil[..., 3] = np.maximum(foil[..., 3], BODY_FOIL_ALPHA * pouch) * (pouch > 0.5)
    foil[:seam_row, :, 3] = 0

    # Reversed-out emblem for the storefront heading (user 22:31): white on
    # transparent, cropped to EMBLEM_BOX (400 × 400 at 2×).
    x0, y0, x1, y1 = (int(px(v)) for v in EMBLEM_BOX)
    logo = np.zeros((y1 - y0, x1 - x0, 4))
    logo[..., :3] = 1.0
    logo[..., 3] = emblem[y0:y1, x0:x1]

    save_rgba(body_png, out_dir / f"gacha-pack-{tier}-body.png")
    save_rgba(flap_png, out_dir / f"gacha-pack-{tier}-flap.png")
    save_rgba(foil, out_dir / f"gacha-pack-{tier}-foil.png")
    save_rgba(logo, out_dir / f"gacha-pack-{tier}-emblem.png")
    save_rgba(printed, out_dir / f"gacha-pack-{tier}-print.png")
    return composite


def contact_sheet(bodies: list[np.ndarray], path: Path) -> None:
    h, w = bodies[0].shape[:2]
    margin = 12
    sheet = Image.new("RGBA", (margin + len(TIERS) * (w + margin), h + 2 * margin), (16, 16, 20, 255))
    for c, body in enumerate(bodies):
        tile = Image.fromarray(np.clip(body * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
        sheet.alpha_composite(tile, (margin + c * (w + margin), margin))
    sheet.save(path, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=SHIPPING)
    parser.add_argument("--sheet", type=Path, help="write a six-tier contact sheet")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sealed = [build_tier(tier, args.out) for tier in TIERS]
    print(f"wrote {len(TIERS) * 5} files ({CANVAS[0] * S}x{CANVAS[1] * S}) to {args.out}")
    if args.sheet:
        contact_sheet(sealed, args.sheet)
        print(f"contact sheet: {args.sheet}")


if __name__ == "__main__":
    main()
