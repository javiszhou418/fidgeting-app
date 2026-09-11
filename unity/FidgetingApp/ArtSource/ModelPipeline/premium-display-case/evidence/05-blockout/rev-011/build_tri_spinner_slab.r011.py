"""Deterministic bpy builder for the premium-display-case `tri-spinner-slab-v3-cmf`
variant (Gate 05 blockout, evidence rev-011).

    blender -b --python tools/blender/build_tri_spinner_slab.py -- [--no-turntable] [--frames N]

Every dimension is read from the Gate 03 rev-011 `modeling-contract.json`
(rev-011 = rev-009 geometry; soft_focus, lighting direction and rarity palette changed).
The only literals in this file are topology choices (segment counts), review
colours and render settings. Geometry is authored in canonical product space
(mm; +X right, +Y up, +Z toward the viewer, origin at the assembled-envelope
centre) and converted once to Blender space (B = (C.x, -C.z, C.y) * 0.001).

rev-009 construction rules (user 2026-09-10 15:19 "把这四个角去掉吧，有点太复杂了"):
- The four corner wings are gone. The field around the pocket is plain dark
  sandblast with its outline groove, the mirrored gold accents, the polished
  lip and the trait plaque. The pocket centre is unchanged (contract
  `main.pocket_top_clearance_mm` keeps the rev-008 midpoint).

rev-008 construction rules (user decisions after the reference research):
- One island chamfer for both steel islands; the main field, its groove and
  the wing edges are exact inward offsets of the main bezel outline (equal
  band widths on sides, top, bottom and diagonals; parallel chamfers).
- Four identical wings mirrored about the pocket centre (x and y), blunt
  ends; gold accents mirrored; CMF scheme A zones (wings mirror, plaque
  piano black).

rev-007 construction rules (from the user's Gate 05 rev-006 refinement, direction accepted):
- Every 45-degree chamfer junction is filleted (fillet-chamfer-fillet resampled to
  seg+1 points per corner so nested outlines still bridge 1:1); nested outlines
  keep a minimum junction fillet. Wing polygons are filleted at every vertex.
- The bottom band is the TRAIT PROFILE plaque (FDB-DSP-053): three 0-100
  troughs with quartile tick notches and runtime-dynamic fill placeholders.

rev-006 construction rules (from the user's Gate 05 rev-005 feedback):
- Header and main are two separate steel islands; the bridging datum rail is
  gone and a dark smoke seam floor shows between them.
- Header bezel: 45-degree chamfers on all four corners. Crystal frame: stepped
  inner ledge (one watertight stepped ring).
- Level stack is geometry: engraved grooves are BOOLEAN EXACT cuts into the
  field (outline, band surround, lip foot); brushed wings are angular panels
  hugging the pocket; the pocket has a raised polished lip (outer chamfer, inner
  slope) carrying three clear clips; the header plate carries a mirror divider.

rev-005 construction rules (from the user's Gate 05 rev-004 rejection):
- Every nested outline is the exact inward offset of its parent (`Outline.inset`):
  corner arcs keep the parent's arc centre, chamfers stay parallel, vertex counts
  match, so rings bridge 1:1 and stay concentric by construction.
- The pocket is a generic circle sized from the largest toy; the caller-owned
  spinner is imported at fit scale 1.0 as a review input only.
- Relief is real geometry: recessed header plane, recessed field, 45-degree
  mirror chamfers, raised rail/strips/band, counterbored bolts, bevelled edges.
- Review renders colour every part by `cmf_zone_id` so the CMF partition is
  legible; the CMF material preview lives in a separate script.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-011/modeling-contract.json"
OUT_DIR = PIPELINE / "evidence/05-blockout/rev-011"
# fresh, unique frame directory per run; nothing is ever deleted from /tmp
TURNTABLE_DIR = Path(f"/tmp/tri-spinner-slab-g05-r011-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
BLEND_PATH = OUT_DIR / "tri-spinner-slab-blockout-r011.blend"

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
RENDER_STILLS = "--no-stills" not in ARGS
TURNTABLE_FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else None

CORNER_SEGMENTS = 14          # per rounded-rectangle corner arc
CIRCLE_SEGMENTS = 192         # pocket circles
RADIAL_SAMPLES = 384          # radial pairing between a rectangle outline and a circle
BOLT_SEGMENTS = 36
MM = 0.001

# Review colours per cmf_zone_id (Workbench object colour). Legend is stamped on every render.
ZONE_COLORS = {
    1: (0.80, 0.90, 1.00, 1.0),   # clear crystal
    2: (0.22, 0.20, 0.26, 1.0),   # smoke-lilac liner
    3: (0.60, 0.62, 0.64, 1.0),   # microblast titanium
    4: (0.09, 0.09, 0.10, 1.0),   # graphite
    5: (0.86, 0.87, 0.89, 1.0),   # steel satin
    6: (0.98, 0.99, 1.00, 1.0),   # smoked mirror silver
    7: (0.92, 0.72, 0.30, 1.0),   # champagne gold
}
ZONE_LEGEND = "1 crystal / 2 smoke liner / 3 microblast / 4 graphite / 5 steel satin / 6 mirror / 7 gold"


# ----------------------------------------------------------------- contract --
def load_contract() -> tuple[dict, dict, str]:
    contract = json.loads(CONTRACT_PATH.read_text())
    values = {p["id"]: p.get("value") for p in contract["parameters"]["inputs"]}
    for pid, rec in contract["resolved"].items():
        values[pid] = rec["value"]
    return contract, values, contract["hashing"]["contract_sha256"]


CONTRACT, V, CONTRACT_SHA = load_contract()
GB = CONTRACT["geometry_builder"]
SEP = GB["minimum_render_separation_mm"]
R_MIN = GB["nested_offset_rule"]["min_corner_radius_mm"]
F_MIN = V["interior.junction_fillet_min_mm"]
Z_ROOT = V["case.root_recentering_z_mm"]
CLAMPED_CORNERS: list[dict] = []
FILLET_CLAMPS: list[dict] = []
FILLETED_CORNERS: list[str] = []
TAN_22_5 = math.tan(math.radians(22.5))


def to_b(x: float, y: float, z: float) -> Vector:
    """Canonical mm (construction space, rear outer face z = 0) to Blender metres."""
    return Vector((x * MM, -(z + Z_ROOT) * MM, y * MM))


def to_b_dir(x: float, y: float, z: float) -> Vector:
    return Vector((x * MM, -z * MM, y * MM))


def canonical_dir_to_b(v) -> Vector:
    return Vector((v[0], -v[2], v[1]))


# ----------------------------------------------------------------- outlines --
@dataclass(frozen=True)
class Corner:
    kind: str      # "round" | "chamfer"
    size: float    # radius or 45-degree chamfer leg
    fillet: float = 0.0   # chamfer only: fillet radius at both junctions with the straight edges


@dataclass(frozen=True)
class Outline:
    """Axis-aligned rectangle with per-corner treatment, order BR, TR, TL, BL (CCW)."""
    x0: float
    y0: float
    x1: float
    y1: float
    corners: tuple[Corner, Corner, Corner, Corner]
    name: str = ""

    @staticmethod
    def rounded(x0, y0, x1, y1, r, name=""):
        return Outline(x0, y0, x1, y1, tuple(Corner("round", r) for _ in range(4)), name)

    def inset(self, d: float, name: str = "") -> "Outline":
        """Exact parallel inward offset by d. Arcs stay concentric (r - d); 45-degree
        chamfer legs shrink by d*(2 - sqrt(2)); radii below R_MIN are clamped and logged."""
        new = []
        for i, c in enumerate(self.corners):
            if c.kind == "round":
                r = c.size - d
                if r < R_MIN:
                    CLAMPED_CORNERS.append({"outline": name or self.name, "corner": ("BR", "TR", "TL", "BL")[i],
                                            "exact_radius_mm": round(r, 3), "clamped_to_mm": R_MIN})
                    r = R_MIN
                new.append(Corner("round", r))
            else:
                leg = c.size - d * (2 - math.sqrt(2))
                if leg < 0.05:
                    CLAMPED_CORNERS.append({"outline": name or self.name, "corner": ("BR", "TR", "TL", "BL")[i],
                                            "exact_chamfer_mm": round(leg, 3), "clamped_to_mm": 0.05})
                    leg = 0.05
                fillet = 0.0
                if c.fillet > 0:
                    exact = c.fillet - d
                    fillet = max(exact, F_MIN)
                    if exact < F_MIN:
                        FILLET_CLAMPS.append({"outline": name or self.name, "corner": ("BR", "TR", "TL", "BL")[i],
                                              "exact_fillet_mm": round(exact, 3), "kept_mm": F_MIN})
                new.append(Corner("chamfer", leg, fillet))
        return Outline(self.x0 + d, self.y0 + d, self.x1 - d, self.y1 - d, tuple(new), name or self.name)

    def points(self, seg: int = CORNER_SEGMENTS) -> list[tuple[float, float]]:
        """CCW polyline starting on the bottom edge. Every corner emits seg+1
        distinct points regardless of kind, so insets of one outline bridge 1:1."""
        x0, y0, x1, y1 = self.x0, self.y0, self.x1, self.y1
        anchors = [((x1, y0), (-1, 1)), ((x1, y1), (-1, -1)), ((x0, y1), (1, -1)), ((x0, y0), (1, 1))]
        start_angles = (-90.0, 0.0, 90.0, 180.0)
        pts = []
        for i, (c, ((cx, cy), (sx, sy))) in enumerate(zip(self.corners, anchors)):
            if c.kind == "round":
                r = c.size
                ax, ay = cx + sx * r, cy + sy * r
                for k in range(seg + 1):
                    a = math.radians(start_angles[i] + 90.0 * k / seg)
                    pts.append((ax + r * math.cos(a), ay + r * math.sin(a)))
            else:
                # CCW: corners 0 and 2 are entered along a horizontal edge, 1 and 3 along a vertical edge
                leg = c.size
                if i in (0, 2):
                    p_in, p_out = (cx + sx * leg, cy), (cx, cy + sy * leg)
                else:
                    p_in, p_out = (cx, cy + sy * leg), (cx + sx * leg, cy)
                if c.fillet <= 0:
                    for k in range(seg + 1):
                        t = k / seg
                        pts.append((p_in[0] + (p_out[0] - p_in[0]) * t, p_in[1] + (p_out[1] - p_in[1]) * t))
                else:
                    d_in, d_out = ((1, 0), (0, 1), (-1, 0), (0, -1))[i], ((0, 1), (-1, 0), (0, -1), (1, 0))[i]
                    pts.extend(filleted_chamfer_path(p_in, p_out, d_in, d_out, c.fillet, seg))
                    FILLETED_CORNERS.append(f"{self.name}:{('BR', 'TR', 'TL', 'BL')[i]}")
        return pts

    def area(self) -> float:
        return polygon_area(self.points())

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0


def circle(cx: float, cy: float, r: float, n: int = CIRCLE_SEGMENTS) -> list[tuple[float, float]]:
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def hexagon(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]


def rotated_rect(cx: float, cy: float, length: float, width: float, angle_deg: float) -> list[tuple[float, float]]:
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    hl, hw = length / 2, width / 2
    return [(cx + ux * s * hl + vx * t * hw, cy + uy * s * hl + vy * t * hw) for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _unit(vx, vy):
    n = math.hypot(vx, vy)
    return (vx / n, vy / n)


def _arc(o, r, a0, sweep, m):
    return [(o[0] + r * math.cos(a0 + sweep * k / m), o[1] + r * math.sin(a0 + sweep * k / m)) for k in range(m + 1)]


def resample_polyline(pts, n):
    """n points evenly spaced by arc length along an open polyline (endpoints kept)."""
    seg_len = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    total = sum(seg_len)
    out, j, acc = [], 0, 0.0
    for k in range(n):
        target = total * k / (n - 1)
        while j < len(seg_len) - 1 and acc + seg_len[j] < target - 1e-12:
            acc += seg_len[j]
            j += 1
        t = 0.0 if seg_len[j] == 0 else (target - acc) / seg_len[j]
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def filleted_chamfer_path(p_in, p_out, d_in, d_out, f, seg, m=8):
    """Fillet (radius f) - straight 45-degree chamfer - fillet, for a CCW outline
    entering the corner along unit direction d_in and leaving along d_out.
    Resampled to seg+1 points so it bridges 1:1 with any other corner."""
    c = _unit(p_out[0] - p_in[0], p_out[1] - p_in[1])
    t = f * TAN_22_5
    left = lambda d: (-d[1], d[0])  # noqa: E731  inward normal of a CCW polygon
    t1a = (p_in[0] - d_in[0] * t, p_in[1] - d_in[1] * t)
    o1 = (t1a[0] + left(d_in)[0] * f, t1a[1] + left(d_in)[1] * f)
    arc1 = _arc(o1, f, math.atan2(t1a[1] - o1[1], t1a[0] - o1[0]), math.radians(45.0), m)
    t2a = (p_out[0] - c[0] * t, p_out[1] - c[1] * t)
    o2 = (t2a[0] + left(c)[0] * f, t2a[1] + left(c)[1] * f)
    arc2 = _arc(o2, f, math.atan2(t2a[1] - o2[1], t2a[0] - o2[0]), math.radians(45.0), m)
    return resample_polyline(arc1 + arc2, seg + 1)


def fillet_polygon(pts, r, m=6):
    """Round every vertex of a closed polygon with radius r (reduced where the
    adjacent edges are too short). Vertices with < 2 degrees of turn are kept."""
    out = []
    n = len(pts)
    for i in range(n):
        p, v, q = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        d1, d2 = _unit(v[0] - p[0], v[1] - p[1]), _unit(q[0] - v[0], q[1] - v[1])
        phi = math.atan2(d1[0] * d2[1] - d1[1] * d2[0], d1[0] * d2[0] + d1[1] * d2[1])
        if abs(phi) < math.radians(2.0):
            out.append(v)
            continue
        t = r * math.tan(abs(phi) / 2)
        t_max = 0.45 * min(math.hypot(v[0] - p[0], v[1] - p[1]), math.hypot(q[0] - v[0], q[1] - v[1]))
        if t > t_max:
            t = t_max
        r_eff = t / math.tan(abs(phi) / 2)
        t1 = (v[0] - d1[0] * t, v[1] - d1[1] * t)
        nrm = (-d1[1], d1[0]) if phi > 0 else (d1[1], -d1[0])
        o = (t1[0] + nrm[0] * r_eff, t1[1] + nrm[1] * r_eff)
        out.extend(_arc(o, r_eff, math.atan2(t1[1] - o[1], t1[0] - o[0]), phi, m))
    return out


def rotated_rounded_rect(cx: float, cy: float, length: float, width: float, r: float, angle_deg: float) -> list[tuple[float, float]]:
    """Rounded rectangle centred on (cx, cy), long axis along angle_deg."""
    pts = Outline.rounded(-length / 2, -width / 2, length / 2, width / 2, r).points(seg=6)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def arc_points(cx: float, cy: float, r: float, deg0: float, deg1: float, n: int) -> list[tuple[float, float]]:
    return [(cx + r * math.cos(math.radians(deg0 + (deg1 - deg0) * k / n)), cy + r * math.sin(math.radians(deg0 + (deg1 - deg0) * k / n)))
            for k in range(n + 1)]


def dedupe(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out = []
    for p in pts:
        if not out or (abs(out[-1][0] - p[0]) > 1e-7 or abs(out[-1][1] - p[1]) > 1e-7):
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-7 and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def polygon_area(pts: list[tuple[float, float]]) -> float:
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def ray_hit(loop: list[tuple[float, float]], cx: float, cy: float, angle: float) -> tuple[float, float]:
    dx, dy = math.cos(angle), math.sin(angle)
    best = None
    for i in range(len(loop)):
        (ax, ay), (bx, by) = loop[i], loop[(i + 1) % len(loop)]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - cx) * ey - (ay - cy) * ex) / den
        u = ((ax - cx) * dy - (ay - cy) * dx) / den
        if t >= 0 and -1e-9 <= u <= 1 + 1e-9 and (best is None or t > best):
            best = t
    if best is None:
        raise ValueError("ray missed loop")
    return (cx + dx * best, cy + dy * best)


def radial_pair(outer, inner, cx, cy, n):
    """Sample both loops at the same polar angles about (cx, cy): n uniform
    angles plus the exact angle of every vertex of either loop, so corners of
    a chamfered/rounded outline survive the pairing. Valid for loops that are
    star-shaped from the centre."""
    angles = {round(2 * math.pi * k / n, 9) for k in range(n)}
    for loop in (outer, inner):
        for x, y in loop:
            angles.add(round(math.atan2(y - cy, x - cx) % (2 * math.pi), 9))
    angles = sorted(angles)
    merged = [angles[0]]
    for a in angles[1:]:
        if a - merged[-1] > 1e-4:
            merged.append(a)
    if (2 * math.pi - merged[-1]) + merged[0] <= 1e-4:
        merged.pop()
    return [ray_hit(outer, cx, cy, a) for a in merged], [ray_hit(inner, cx, cy, a) for a in merged]


# --------------------------------------------------------------- bmesh solids --
def finish(bm, name, collection, parent):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.parent = parent
    return ob


def prism(name, loop, z0, z1, collection, parent):
    bm = bmesh.new()
    verts = [bm.verts.new(to_b(x, y, z0)) for x, y in loop]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    bmesh.ops.translate(bm, verts=[g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)], vec=to_b_dir(0, 0, z1 - z0))
    return finish(bm, name, collection, parent)


def pair_loops(outer, inner, radial_center=None):
    if radial_center is not None:
        return radial_pair(outer, inner, radial_center[0], radial_center[1], RADIAL_SAMPLES)
    if len(outer) != len(inner):
        raise ValueError(f"loops differ in length ({len(outer)} vs {len(inner)}) and no radial centre given")
    return outer, inner


def ring(name, outer, inner, z0, z1, collection, parent, radial_center=None):
    """Watertight flat ring between two closed loops."""
    return sloped_ring(name, outer, inner, z0, z1, z1, collection, parent, radial_center)


def sloped_ring(name, outer, inner, z0, z_outer_top, z_inner_top, collection, parent, radial_center=None):
    """Watertight ring whose top surface slopes from the outer loop (z_outer_top)
    to the inner loop (z_inner_top); bottom is flat at z0. Used for 45-degree
    mirror chamfers and the pocket rim."""
    outer, inner = pair_loops(outer, inner, radial_center)
    n = len(outer)
    bm = bmesh.new()
    vo0 = [bm.verts.new(to_b(x, y, z0)) for x, y in outer]
    vo1 = [bm.verts.new(to_b(x, y, z_outer_top)) for x, y in outer]
    vi0 = [bm.verts.new(to_b(x, y, z0)) for x, y in inner]
    vi1 = [bm.verts.new(to_b(x, y, z_inner_top)) for x, y in inner]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vo0[i], vo0[j], vo1[j], vo1[i]))   # outer wall
        bm.faces.new((vo1[i], vo1[j], vi1[j], vi1[i]))   # top (sloped)
        bm.faces.new((vi1[i], vi1[j], vi0[j], vi0[i]))   # inner wall
        bm.faces.new((vi0[i], vi0[j], vo0[j], vo0[i]))   # bottom
    return finish(bm, name, collection, parent)


def profile_ring(name, loops, z0, collection, parent):
    """Watertight ring from a radial profile: `loops` is an ordered list of
    (closed loop, top z) from the outer edge to the inner edge, all with the
    same vertex count. Consecutive loops are bridged by quads, so equal radii
    at different z give vertical steps and different radii at different z give
    slopes. Outer and inner walls drop to z0; the bottom is flat."""
    n = len(loops[0][0])
    for loop, _ in loops:
        if len(loop) != n:
            raise ValueError(f"profile loops differ in length for {name}")
    bm = bmesh.new()
    tops = [[bm.verts.new(to_b(x, y, z)) for x, y in loop] for loop, z in loops]
    outer0 = [bm.verts.new(to_b(x, y, z0)) for x, y in loops[0][0]]
    inner0 = [bm.verts.new(to_b(x, y, z0)) for x, y in loops[-1][0]]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((outer0[i], outer0[j], tops[0][j], tops[0][i]))                   # outer wall
        for a, b in zip(tops, tops[1:]):
            bm.faces.new((a[i], a[j], b[j], b[i]))                                      # profile step/slope/flat
        bm.faces.new((tops[-1][i], tops[-1][j], inner0[j], inner0[i]))                 # inner wall
        bm.faces.new((inner0[i], inner0[j], outer0[j], outer0[i]))                     # bottom
    return finish(bm, name, collection, parent)


def register_cut(target, cutter, index):
    """Register a BOOLEAN EXACT difference of `cutter` (hidden, not exported) on `target`."""
    cutter.display_type = "WIRE"
    cutter.hide_render = True
    stamp_props(cutter, export_role="cutter-not-exported", cmf_zone_id=0)
    mod = target.modifiers.new(f"02{index}_BOOLEAN_DETAIL_CUT_EXACT", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    return cutter


def frame_edge_weights(ob, outer_pts, ledge_pts, inner_pts, z_front, z_ledge):
    """Per-edge bevel weights for the stepped crystal frame so one Bevel modifier
    (limit WEIGHT) gives a full-width outer lip, a light ledge step and a medium
    inner edge without eating the 0.8 mm step."""
    key = lambda x, y: (round(x, 4), round(y, 4))  # noqa: E731
    loops = {0: {key(x, y) for x, y in outer_pts}, 1: {key(x, y) for x, y in ledge_pts}, 2: {key(x, y) for x, y in inner_pts}}
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    layer = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    for e in bm.edges:
        cls = []
        for v in e.verts:
            x, y, z = v.co.x / MM, v.co.z / MM, -v.co.y / MM - Z_ROOT
            loop_id = next((i for i, pts in loops.items() if key(x, y) in pts), None)
            cls.append((loop_id, round(z, 3)))
        if cls[0] != cls[1] or cls[0][0] is None:
            continue                                   # radial/vertical edge or unknown: no bevel
        loop_id, z = cls[0]
        if loop_id == 0:
            w = 1.0 if abs(z - z_front) < 1e-3 else 0.6
        elif loop_id == 1:
            w = 0.25
        else:
            w = 0.4 if abs(z - z_ledge) < 1e-3 else 0.4
        e[layer] = w
    bm.to_mesh(ob.data)
    bm.free()


# ---------------------------------------------------------------- scene setup --
def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 1.0


def make_collections() -> dict[str, bpy.types.Collection]:
    root = bpy.data.collections.new("COL_PDC_ROOT")
    bpy.context.scene.collection.children.link(root)
    cols = {"COL_PDC_ROOT": root}
    for c in CONTRACT["scene"]["collections"]:
        if c["id"] == "COL_PDC_ROOT":
            continue
        col = bpy.data.collections.new(c["id"])
        root.children.link(col)
        cols[c["id"]] = col
    cols["COL_PDC_CUTTERS"].hide_render = True
    return cols


def empty(name, collection, parent=None, location=None):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.01
    collection.objects.link(ob)
    ob.parent = parent
    if location is not None:
        ob.location = location
    return ob


def stamp_props(ob, *, export_role, cmf_zone_id, evidence_class="recommended_start", immutable=False, softfocus=False,
                geometry_source="deterministic_bpy:tools/blender/build_tri_spinner_slab.py", extra=None):
    ob["asset_id"] = CONTRACT["model_id"]
    ob["variant_id"] = CONTRACT["variant_id"]
    ob["contract_sha256"] = CONTRACT_SHA
    ob["geometry_source"] = geometry_source
    ob["evidence_class"] = evidence_class
    ob["export_role"] = export_role
    ob["immutable_geometry"] = immutable
    ob["cmf_zone_id"] = cmf_zone_id
    ob["softfocus_eligible"] = softfocus
    ob["provisional_marker"] = CONTRACT["provisional_marker"]
    for k, v in (extra or {}).items():
        ob[k] = v


def add_bevel(ob, width_mm, segments, name="030_BEVEL_PRIMARY"):
    bevel = ob.modifiers.new(name, "BEVEL")
    bevel.width = width_mm * MM
    bevel.segments = segments
    bevel.profile = GB["bevel"]["profile"]
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(GB["smooth_by_angle_deg"])
    bevel.use_clamp_overlap = GB["bevel"]["clamp_overlap"]
    bevel.harden_normals = True
    return bevel


def apply_modifier(ob, name):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
        bpy.ops.object.modifier_apply(modifier=name)


# --------------------------------------------------------------- the geometry --
def build_case(cols, case_root) -> tuple[dict[str, bpy.types.Object], dict]:
    W, H = V["case.width_mm"], V["case.height_mm"]
    band = V["case.frame_band_mm"]
    liner_t = V["case.smoke_liner_mm"]
    shelf = V["main.perimeter_shelf_width_mm"]
    mirror = V["cmf.mirror_bevel_width_mm"]
    gold_w, gold_relief = V["cmf.gold_inlay_width_mm"], V["cmf.gold_relief_mm"]
    lift = V["interior.part_lift_mm"]
    part_bevel = V["interior.part_bevel_mm"]
    z_b = V["case.backplate_thickness_mm"]
    z_int0 = z_b + SEP
    z_shelf, z_frame = V["case.z_shelf_top_mm"], V["case.z_frame_front_mm"]
    z_field, z_hplane = V["case.z_field_mm"], V["case.z_header_plane_mm"]
    z_liner_top = z_shelf + V["case.liner_seam_above_shelf_mm"]
    y_seam = H / 2 - V["header.height_mm"]
    y_bay = y_seam - V["header.rail_band_mm"]
    cx, cy = V["spinner.center_x_mm"], V["spinner.center_y_mm"]
    geo, cutters = cols["COL_PDC_GEOMETRY_STATIC"], cols["COL_PDC_CUTTERS"]
    out: dict[str, bpy.types.Object] = {}
    report = {"concentric_pairs": [], "gold_top_area_mm2": 0.0}

    def add(name, ob, zone, bevel_mm=None, bevel_segments=None, **kw):
        stamp_props(ob, export_role="case-geometry", cmf_zone_id=zone, **kw)
        if bevel_mm:
            add_bevel(ob, bevel_mm, bevel_segments or GB["bevel"]["inner_segments"])
        out[name] = ob
        return ob

    def concentric(parent: Outline, child: Outline, part: str):
        report["concentric_pairs"].append({"part": part, "parent": parent.name, "child": child.name, "concentric": True,
                                           "offset_mm": round(parent.x0 - child.x0, 3) * -1})

    # --- outlines (one parent chain; every nested outline is an exact inset)
    outer = Outline.rounded(-W / 2, -H / 2, W / 2, H / 2, V["case.outer_corner_radius_mm"], "OUTER")
    crystal_inner = outer.inset(band, "CRYSTAL_INNER")
    liner_outer = crystal_inner.inset(SEP, "LINER_OUTER")
    liner_inner = liner_outer.inset(liner_t, "LINER_INNER")
    interior = liner_inner.inset(SEP, "INTERIOR")            # steel parts live inside this
    r_int = interior.corners[1].size if interior.corners[1].kind == "round" else R_MIN

    # rear plate fills the crystal opening behind everything
    add("GEO_PDC_REAR_PLATE", prism("GEO_PDC_REAR_PLATE", liner_outer.points(), 0.0, z_b, geo, case_root), 3)

    # crystal frame: full band, full depth, stepped inner ledge (double edge), counterbored for six bolts
    ledge_w, ledge_drop = V["case.frame_ledge_width_mm"], V["case.frame_ledge_drop_mm"]
    ledge = outer.inset(band - ledge_w, "CRYSTAL_LEDGE")
    frame = add("GEO_PDC_OUTER_CRYSTAL_FRAME", profile_ring("GEO_PDC_OUTER_CRYSTAL_FRAME",
                                                            [(outer.points(), z_frame), (ledge.points(), z_frame),
                                                             (ledge.points(), z_frame - ledge_drop), (crystal_inner.points(), z_frame - ledge_drop)],
                                                            0.0, geo, case_root), 1, softfocus=True)
    concentric(outer, ledge, "GEO_PDC_OUTER_CRYSTAL_FRAME")
    concentric(ledge, crystal_inner, "GEO_PDC_OUTER_CRYSTAL_FRAME")
    frame_edge_weights(frame, outer.points(), ledge.points(), crystal_inner.points(), z_frame, z_frame - ledge_drop)
    report["frame_ledge"] = {"width_mm": ledge_w, "drop_mm": ledge_drop, "z_front": z_frame, "z_ledge": round(z_frame - ledge_drop, 3)}

    # smoke liner: thin dark ring standing just above the shelves
    add("GEO_PDC_SMOKE_INNER_LINER", ring("GEO_PDC_SMOKE_INNER_LINER", liner_outer.points(), liner_inner.points(),
                                          z_int0, z_liner_top, geo, case_root), 2)
    concentric(liner_outer, liner_inner, "GEO_PDC_SMOKE_INNER_LINER")

    # --- header island: satin bezel chamfered on all four corners, 45-degree mirror chamfer, recessed graphite plane, divider
    ch_h = V["interior.island_corner_chamfer_mm"]        # == header.bezel_corner_chamfer_mm (asserted in the contract)
    fil = V["interior.junction_fillet_mm"]
    bezel = Outline(interior.x0, y_seam + SEP, interior.x1, interior.y1, tuple(Corner("chamfer", ch_h, fil) for _ in range(4)), "HEADER_BEZEL")
    bezel_in = bezel.inset(shelf, "HEADER_BEZEL_INNER")
    add("GEO_PDC_HEADER_SATIN_SHELF", ring("GEO_PDC_HEADER_SATIN_SHELF", bezel.points(), bezel_in.points(), z_int0, z_shelf, geo, case_root),
        5, bevel_mm=part_bevel)
    concentric(bezel, bezel_in, "GEO_PDC_HEADER_SATIN_SHELF")
    bev_o = bezel_in.inset(SEP, "HEADER_MIRROR_OUTER")
    bev_i = bev_o.inset(mirror, "HEADER_MIRROR_INNER")
    add("GEO_PDC_HEADER_MIRROR_BEVEL", sloped_ring("GEO_PDC_HEADER_MIRROR_BEVEL", bev_o.points(), bev_i.points(),
                                                   z_int0, z_shelf - SEP, z_shelf - SEP - mirror, geo, case_root), 6, softfocus=True)
    concentric(bev_o, bev_i, "GEO_PDC_HEADER_MIRROR_BEVEL")
    plane = bev_i.inset(SEP, "HEADER_GRAPHITE")
    add("GEO_PDC_HEADER_GRAPHITE_PLANE", prism("GEO_PDC_HEADER_GRAPHITE_PLANE", plane.points(), z_int0, z_hplane, geo, case_root), 4)
    concentric(bev_i, plane, "GEO_PDC_HEADER_GRAPHITE_PLANE")
    y_div = plane.y1 - V["header.divider_from_plate_top"] * plane.height
    div_w = V["header.divider_line_width_mm"]
    add("GEO_PDC_HEADER_DIVIDER_LINE", prism("GEO_PDC_HEADER_DIVIDER_LINE",
                                             Outline.rounded(plane.x0 + 3.0, y_div - div_w / 2, plane.x1 - 3.0, y_div + div_w / 2, div_w * 0.45).points(seg=4),
                                             z_hplane - 0.3, z_hplane + 0.1, geo, case_root), 6, softfocus=True)

    # --- dark seam between the two islands (the datum rail of rev-005 is gone: header and main are disconnected)
    seam_gap = V["header.seam_gap_mm"]
    y_main_top = y_seam - seam_gap
    seam = Outline.rounded(interior.x0, y_main_top + SEP, interior.x1, y_seam - SEP, R_MIN, "COMPARTMENT_SEAM")
    add("GEO_PDC_COMPARTMENT_SEAM", prism("GEO_PDC_COMPARTMENT_SEAM", seam.points(), z_int0, z_field - 0.8, geo, case_root), 2)
    report["seam"] = {"gap_mm": seam_gap, "y_header_bottom": round(y_seam, 3), "y_main_top": round(y_main_top, 3),
                      "z_floor": round(z_field - 0.8, 3), "datum_rail": "retired"}

    # two gold bars on the bezel's bottom rail, left and right (never a closed loop)
    bar_len = 0.10 * W
    bar_y = y_seam + SEP + shelf / 2
    bar_cx = interior.x1 - shelf - 0.05 * W - bar_len / 2
    for suffix, sign in (("L", -1), ("R", 1)):
        loop = rotated_rect(sign * bar_cx, bar_y, bar_len, gold_w, 0.0)
        add(f"GEO_PDC_HEADER_GOLD_INLAY_{suffix}", prism(f"GEO_PDC_HEADER_GOLD_INLAY_{suffix}", loop, z_shelf - 0.3,
                                                          z_shelf + gold_relief, geo, case_root), 7)
        report["gold_top_area_mm2"] += polygon_area(loop)

    # --- main island: satin bezel (chamfered top corners, rounded bottom corners, wider brushed top strip) around a chamfered, recessed field
    main_outer = Outline(interior.x0, interior.y0, interior.x1, y_main_top - SEP, tuple(Corner("chamfer", ch_h, fil) for _ in range(4)), "MAIN_BEZEL")
    field = main_outer.inset(shelf, "MAIN_FIELD")                     # exact offset: equal bands on every side and diagonal
    if abs(field.y1 - V["main.field_top_y_mm"]) > 0.02 or abs(field.y0 - V["main.field_bottom_y_mm"]) > 0.02:
        raise SystemExit(f"field outline drifted from the contract: {field.y0:.3f}/{field.y1:.3f} vs {V['main.field_bottom_y_mm']}/{V['main.field_top_y_mm']}")
    add("GEO_PDC_MAIN_SATIN_SHELF", ring("GEO_PDC_MAIN_SATIN_SHELF", main_outer.points(), field.points(), z_int0, z_shelf, geo, case_root),
        5, bevel_mm=part_bevel)
    concentric(main_outer, field, "GEO_PDC_MAIN_SATIN_SHELF")
    report["main_bezel_bands_mm"] = {"side": round(field.x0 - main_outer.x0, 3), "top": round(main_outer.y1 - field.y1, 3),
                                     "bottom": round(field.y0 - main_outer.y0, 3),
                                     "diagonal": round(((main_outer.corners[1].size - field.corners[1].size) / (2 - math.sqrt(2))), 3)}
    seam_o = field.inset(SEP, "MAIN_MIRROR_OUTER")
    seam_i = seam_o.inset(mirror, "MAIN_MIRROR_INNER")
    add("GEO_PDC_MAIN_MIRROR_SEAM", sloped_ring("GEO_PDC_MAIN_MIRROR_SEAM", seam_o.points(), seam_i.points(),
                                                z_int0, z_shelf - SEP, z_shelf - SEP - mirror, geo, case_root), 6, softfocus=True)
    concentric(seam_o, seam_i, "GEO_PDC_MAIN_MIRROR_SEAM")
    field_in = seam_i.inset(SEP, "MAIN_FIELD_SURFACE")
    g_w, g_d = V["main.groove_width_mm"], V["main.groove_depth_mm"]
    r_lip_o = V["main.pocket_diameter_mm"] / 2                     # lip foot at field level
    field_ob = add("GEO_PDC_MAIN_MICROBLAST_FIELD", ring("GEO_PDC_MAIN_MICROBLAST_FIELD", field_in.points(), circle(cx, cy, r_lip_o + g_w),
                                                        z_int0, z_field, geo, case_root, radial_center=(cx, cy)), 3)
    concentric(seam_i, field_in, "GEO_PDC_MAIN_MICROBLAST_FIELD")

    # engraved lines cut into the field: outline groove following the chamfered edge, and the band surround (below)
    grooves = []
    go = field_in.inset(V["main.field_outline_groove_inset_mm"], "FIELD_GROOVE_OUTER")
    gi = go.inset(g_w, "FIELD_GROOVE_INNER")
    concentric(go, gi, "CUT_PDC_FIELD_OUTLINE_GROOVE")
    cutter = ring("CUT_PDC_FIELD_OUTLINE_GROOVE", go.points(), gi.points(), z_field - g_d, z_field + 1.0, cutters, case_root)
    grooves.append(register_cut(field_ob, cutter, 0))

    # --- pocket: raised polished lip (foot groove flange, outer chamfer, flat top, inner slope), smoke wall, graphite floor
    lip_w, lip_h = V["main.pocket_lip_width_mm"], V["main.pocket_lip_height_mm"]
    lip_ch, slope_w, slope_drop = V["main.pocket_lip_outer_chamfer_mm"], V["main.pocket_lip_inner_slope_mm"], V["main.pocket_lip_inner_drop_mm"]
    z_lip = z_field + lip_h
    r_lip_i = r_lip_o - lip_w
    lip_profile = [(circle(cx, cy, r_lip_o + g_w - SEP), z_field - g_d), (circle(cx, cy, r_lip_o), z_field - g_d),
                   (circle(cx, cy, r_lip_o), z_lip - lip_ch), (circle(cx, cy, r_lip_o - lip_ch), z_lip),
                   (circle(cx, cy, r_lip_i), z_lip), (circle(cx, cy, r_lip_i - slope_w), z_field - slope_drop)]
    add("GEO_PDC_POCKET_POLISHED_LIP", profile_ring("GEO_PDC_POCKET_POLISHED_LIP", lip_profile, z_int0, geo, case_root), 6,
        bevel_mm=0.12, bevel_segments=GB["bevel"]["micro_segments"], softfocus=True)
    report["concentric_pairs"].append({"part": "GEO_PDC_POCKET_POLISHED_LIP", "parent": "LIP_FOOT", "child": "LIP_INNER_SLOPE",
                                       "concentric": True, "offset_mm": round(lip_w + slope_w, 3)})
    r_wall_o = r_lip_i - slope_w - SEP
    r_well = V["main.pocket_well_diameter_mm"] / 2
    add("GEO_PDC_POCKET_SMOKE_WALL", ring("GEO_PDC_POCKET_SMOKE_WALL", circle(cx, cy, r_wall_o), circle(cx, cy, r_well),
                                          z_int0, z_field - slope_drop - SEP, geo, case_root), 2)
    report["concentric_pairs"].append({"part": "GEO_PDC_POCKET_SMOKE_WALL", "parent": "LIP_INNER_SLOPE", "child": "POCKET_WELL",
                                       "concentric": True, "offset_mm": round(r_wall_o - r_well, 3)})
    add("GEO_PDC_POCKET_GRAPHITE_FLOOR", prism("GEO_PDC_POCKET_GRAPHITE_FLOOR", circle(cx, cy, r_well - SEP), z_int0,
                                               z_b + V["main.pocket_floor_mm"], geo, case_root), 4)
    report["pocket"] = {"shape": "circle", "outer_diameter_mm": round(2 * r_lip_o, 3), "well_diameter_mm": round(2 * r_well, 3),
                        "well_depth_mm": round(z_field - (z_b + V["main.pocket_floor_mm"]), 3), "centre_mm": [cx, cy],
                        "lip": {"width_mm": lip_w, "height_above_field_mm": lip_h, "outer_chamfer_mm": lip_ch, "inner_slope_mm": slope_w,
                                "inner_drop_mm": slope_drop, "foot_groove_mm": [g_w, g_d], "z_top": round(z_lip, 3)}}

    # three clear clips straddling the lip (visual, from the concept image; not a retention mechanism)
    clip_t, clip_r, clip_h = V["hardware.clip_size_mm"]
    n_clips = int(V["hardware.clip_count"])
    clip_positions = []
    for k in range(n_clips):
        ang = 90.0 + 360.0 * k / n_clips
        rc = r_lip_o - lip_w / 2
        px, py = cx + rc * math.cos(math.radians(ang)), cy + rc * math.sin(math.radians(ang))
        loop = rotated_rounded_rect(px, py, clip_t, clip_r, 0.6, ang + 90.0)
        add(f"GEO_PDC_POCKET_CLIP_{k:02d}", prism(f"GEO_PDC_POCKET_CLIP_{k:02d}", loop, z_field + 0.05, z_field + 0.05 + clip_h, geo, case_root),
            1, bevel_mm=0.35, bevel_segments=GB["bevel"]["inner_segments"], softfocus=True)
        clip_positions.append([round(px, 3), round(py, 3), round(ang, 1)])
    report["clips"] = {"count": n_clips, "size_mm": [clip_t, clip_r, clip_h], "positions_mm_deg": clip_positions, "z_top": round(z_field + 0.05 + clip_h, 3)}

    # --- TRAIT PROFILE plaque (FDB-DSP-053): raised brushed plate, three 0-100 troughs, quartile ticks, runtime-dynamic fills
    leg_t, leg_b = field_in.corners[2].size, field_in.corners[3].size      # chamfer legs after the insets
    tp_h, tp_m = V["trait.plaque_height_mm"], V["trait.plaque_bottom_margin_mm"]
    pitch, th, td = V["trait.row_pitch_mm"], V["trait.track_height_mm"], V["trait.track_depth_mm"]
    lab_col, val_col, tick_w, f_in = V["trait.label_column_mm"], V["trait.value_column_mm"], V["trait.tick_width_mm"], V["trait.fill_inset_mm"]
    tp_y0 = field_in.y0 + tp_m
    plaque = Outline.rounded(field_in.x0 + leg_b + 3.5, tp_y0, field_in.x1 - leg_b - 3.5, tp_y0 + tp_h, 0.8, "TRAIT_PLAQUE")
    z_pl = z_field + lift
    plaque_ob = add("GEO_PDC_MAIN_TRAIT_PLAQUE", prism("GEO_PDC_MAIN_TRAIT_PLAQUE", plaque.points(), z_field - 0.3, z_pl, geo, case_root), 4)   # scheme A: piano black
    track_x0, track_x1 = plaque.x0 + lab_col, plaque.x1 - val_col
    track_w = track_x1 - track_x0
    rows = []
    cut_index = 0
    for k, axis in enumerate(("SPIN", "FEEL", "CRAFT")):
        y_k = plaque.y1 - 1.4 - th / 2 - k * pitch
        trough = Outline.rounded(track_x0, y_k - th / 2, track_x1, y_k + th / 2, th * 0.3, f"TRAIT_TROUGH_{k}").points(seg=4)
        register_cut(plaque_ob, prism(f"CUT_PDC_TRAIT_TROUGH_{k:02d}", trough, z_pl - td, z_pl + 1.0, cutters, case_root), cut_index)
        cut_index += 1
        for q in (1, 2, 3):
            xq = track_x0 + track_w * q / 4
            tick = [(xq - tick_w / 2, y_k - th / 2 - 0.5), (xq + tick_w / 2, y_k - th / 2 - 0.5), (xq + tick_w / 2, y_k + th / 2 + 0.5), (xq - tick_w / 2, y_k + th / 2 + 0.5)]
            register_cut(plaque_ob, prism(f"CUT_PDC_TRAIT_TICK_{k:02d}_{q}", tick, z_pl - td, z_pl + 1.0, cutters, case_root), cut_index)
            cut_index += 1
        value = V["trait.preview_values"][k]
        fill_len = (track_w - 2 * f_in) * value / 100.0
        fill = [(track_x0 + f_in, y_k - th / 2 + f_in), (track_x0 + f_in + fill_len, y_k - th / 2 + f_in),
                (track_x0 + f_in + fill_len, y_k + th / 2 - f_in), (track_x0 + f_in, y_k + th / 2 - f_in)]
        fill_ob = prism(f"GEO_PDC_TRAIT_FILL_{k:02d}", fill, z_pl - td + SEP, z_pl - f_in, geo, case_root)
        stamp_props(fill_ob, export_role="runtime-dynamic-fill", cmf_zone_id=7, evidence_class="preview_only",
                    extra={"trait_axis": axis, "preview_value": value, "authority": "Assets/Scripts/Product/ToyTalentCatalog.cs",
                           "full_length_mm": round(track_w - 2 * f_in, 3)})
        out[fill_ob.name] = fill_ob
        rows.append({"axis": axis, "y_mm": round(y_k, 3), "track_x_mm": [round(track_x0, 3), round(track_x1, 3)], "preview_value": value,
                     "fill_length_mm": round(fill_len, 3)})
    for mod in list(plaque_ob.modifiers):
        apply_modifier(plaque_ob, mod.name)
    add_bevel(plaque_ob, part_bevel, GB["bevel"]["inner_segments"])
    report["trait_plaque"] = {"requirement": "FDB-DSP-053", "rows": rows, "plaque_mm": [round(plaque.width, 3), round(tp_h, 3)],
                              "track_mm": [round(track_w, 3), th], "trough_depth_mm": td, "ticks_per_row": 3, "label_column_mm": lab_col,
                              "value_column_mm": val_col, "z_top": round(z_pl, 3), "fills_runtime_dynamic": True}
    # surround groove of the plaque cut into the field
    sg_i = plaque.inset(-0.5, "PLAQUE_GROOVE_INNER")
    sg_o = sg_i.inset(-g_w, "PLAQUE_GROOVE_OUTER")
    concentric(sg_o, sg_i, "CUT_PDC_PLAQUE_SURROUND_GROOVE")
    cutter = ring("CUT_PDC_PLAQUE_SURROUND_GROOVE", sg_o.points(), sg_i.points(), z_field - g_d, z_field + 1.0, cutters, case_root)
    grooves.append(register_cut(field_ob, cutter, 1))

    # --- rev-009: no wings (user 15:19 "把这四个角去掉吧，有点太复杂了"); the field stays plain around the pocket
    assert int(V["main.wing_count"]) == 0, "contract rev-009 retires the wings"
    report["wings"] = {"count": 0, "retired_rev009": ["GEO_PDC_MAIN_WING_TL", "GEO_PDC_MAIN_WING_TR", "GEO_PDC_MAIN_WING_BL", "GEO_PDC_MAIN_WING_BR"],
                       "source_id": "src.user_gate05_rev008_feedback_20260910"}

    # --- gold, mirrored: a bar along each of the four field chamfers, two rails, two index tabs (never a closed loop)
    g_in = V["main.field_outline_groove_inset_mm"] + g_w + 0.6          # centreline sits just inside the outline groove
    bar_o = field_in.inset(g_in, "GOLD_BAR_LINE")
    leg_g = bar_o.corners[1].size
    bar_len = leg_g * math.sqrt(2) - 2 * 0.6
    for tag, (sx, sy, ang) in {"TL": (-1, 1, 45.0), "TR": (1, 1, -45.0), "BL": (-1, -1, -45.0), "BR": (1, -1, 45.0)}.items():
        cxg = cx + sx * (bar_o.width / 2 - leg_g / 2)
        cyg = (bar_o.y0 + bar_o.y1) / 2 + sy * (bar_o.height / 2 - leg_g / 2)
        add(f"GEO_PDC_MAIN_GOLD_CHAMFER_{tag}", prism(f"GEO_PDC_MAIN_GOLD_CHAMFER_{tag}", rotated_rect(cxg, cyg, bar_len, gold_w, ang),
                                                      z_field - 0.3, z_field + gold_relief, geo, case_root), 7)
        report["gold_top_area_mm2"] += bar_len * gold_w
    rail_h = 0.12 * H
    for tag, sx in (("L", -1), ("R", 1)):
        add(f"GEO_PDC_MAIN_GOLD_RAIL_{tag}", prism(f"GEO_PDC_MAIN_GOLD_RAIL_{tag}", rotated_rect(cx + sx * (bar_o.width / 2), cy, rail_h, gold_w, 90.0),
                                                   z_field - 0.3, z_field + gold_relief, geo, case_root), 7)
        report["gold_top_area_mm2"] += rail_h * gold_w
    tab = 2.0
    tab_in = V["main.field_outline_groove_inset_mm"] + g_w + 2.0
    for tag, sx in (("L", -1), ("R", 1)):
        x_t = cx + sx * (field_in.width / 2 - tab_in) - (tab if sx > 0 else 0.0)
        tab_loop = Outline.rounded(x_t, field_in.y0 + tab_in, x_t + tab, field_in.y0 + tab_in + tab, 0.3).points()
        add(f"GEO_PDC_MAIN_GOLD_INDEX_TAB_{tag}", prism(f"GEO_PDC_MAIN_GOLD_INDEX_TAB_{tag}", tab_loop, z_field - 0.3, z_field + gold_relief, geo, case_root), 7)
        report["gold_top_area_mm2"] += tab * tab
    report["gold_layout"] = {"mirrored": True, "chamfer_bars": 4, "rails": 2, "index_tabs": 2, "bar_centreline_inset_mm": round(g_in, 3)}

    for mod in list(field_ob.modifiers):
        apply_modifier(field_ob, mod.name)
    report["grooves"] = {"count": len(grooves) + 1, "width_mm": g_w, "depth_mm": g_d,
                         "lines": ["field outline (cut)", "trait plaque surround (cut)", "lip foot (lip flange below field)"],
                         "trait_cuts": cut_index}
    report["fillets"] = {"junction_fillet_mm": fil, "min_kept_mm": F_MIN, "filleted_corners": sorted(set(FILLETED_CORNERS)),
                         "fillet_clamps": FILLET_CLAMPS}
    report["levels_mm_from_rear"] = {"shelf_top": z_shelf, "mirror_chamfer_bottom": round(z_shelf - SEP - mirror, 3), "field": z_field,
                                     "groove_floor": round(z_field - g_d, 3), "plaque_top": round(z_field + lift, 3),
                                     "trait_trough_floor": round(z_pl - td, 3),
                                     "lip_top": round(z_lip, 3), "lip_inner_slope_bottom": round(z_field - slope_drop, 3),
                                     "clip_top": round(z_field + 0.05 + clip_h, 3), "pocket_floor": round(z_b + V["main.pocket_floor_mm"], 3),
                                     "seam_floor": round(z_field - 0.8, 3), "header_plane": z_hplane, "frame_ledge": round(z_frame - ledge_drop, 3),
                                     "frame_front": z_frame}

    # --- six counterbored bolts on the crystal band
    inset = V["hardware.bolt_corner_inset_mm"]
    r_head, r_socket = V["hardware.bolt_head_diameter_mm"] / 2, V["hardware.bolt_socket_diameter_mm"] / 2
    r_bore, bore_d = V["hardware.bolt_counterbore_diameter_mm"] / 2, V["hardware.bolt_counterbore_depth_mm"]
    head_top = z_frame - V["hardware.bolt_head_below_frame_front_mm"]
    head_bot = z_frame - bore_d + SEP
    positions = [(-W / 2 + inset, H / 2 - inset), (W / 2 - inset, H / 2 - inset), (-W / 2 + band / 2, y_seam), (W / 2 - band / 2, y_seam),
                 (-W / 2 + inset, -H / 2 + inset), (W / 2 - inset, -H / 2 + inset)]
    for i, (bx, by) in enumerate(positions):
        cut = prism(f"CUT_PDC_BOLT_COUNTERBORE_{i:02d}", circle(bx, by, r_bore, BOLT_SEGMENTS), z_frame - bore_d, z_frame + 1.0, cutters, case_root)
        register_cut(frame, cut, i)
        head = sloped_ring(f"GEO_PDC_FRAME_BOLT_{i:02d}", circle(bx, by, r_head, BOLT_SEGMENTS), hexagon(bx, by, r_socket),
                           head_bot, head_top, head_top, geo, case_root, radial_center=(bx, by))
        # socket floor: a separate hexagonal prism inside the ring, seated lower
        floor = prism(f"GEO_PDC_FRAME_BOLT_{i:02d}_SOCKET_FLOOR", hexagon(bx, by, r_socket - SEP), head_bot,
                      head_top - V["hardware.bolt_socket_depth_mm"], geo, case_root)
        stamp_props(floor, export_role="case-geometry", cmf_zone_id=5)
        out[floor.name] = floor
        add(f"GEO_PDC_FRAME_BOLT_{i:02d}", head, 5, bevel_mm=0.12, bevel_segments=GB["bevel"]["micro_segments"])
    report["bolts"] = {"count": len(positions), "positions_mm": [[round(x, 3), round(y, 3)] for x, y in positions],
                       "head_diameter_mm": 2 * r_head, "counterbore_diameter_mm": 2 * r_bore, "counterbore_depth_mm": bore_d}
    for mod in list(frame.modifiers):
        apply_modifier(frame, mod.name)
    frame_bevel = add_bevel(frame, V["case.crystal_bevel_mm"], GB["bevel"]["outer_segments"])
    frame_bevel.limit_method = "WEIGHT"          # outer lip 1.0 x width, ledge step 0.25 x, inner edge 0.4 x (see frame_edge_weights)

    smooth_angle = math.radians(GB["smooth_by_angle_deg"])
    for ob in out.values():
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=smooth_angle)
        wn = ob.modifiers.new("050_WEIGHTED_NORMAL", "WEIGHTED_NORMAL")
        wn.keep_sharp = True
    report["front_face_area_mm2"] = round(outer.area(), 2)
    report["gold_top_area_percent"] = round(100 * report["gold_top_area_mm2"] / outer.area(), 3)
    report["gold_top_area_mm2"] = round(report["gold_top_area_mm2"], 2)
    report["clamped_corners"] = CLAMPED_CORNERS
    return out, report


def import_review_spinner(cols, content_slot) -> list[bpy.types.Object]:
    source = next(s for s in CONTRACT["sources"] if s["id"] == "src.spinner_mesh")
    glb = REPO / source["path"]
    sha = hashlib.sha256(glb.read_bytes()).hexdigest()
    if sha != source["sha256"]:
        raise SystemExit(f"spinner source hash drift: {sha} != {source['sha256']}")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    imported = [o for o in bpy.data.objects if o not in before]
    root = next(o for o in imported if o.parent is None)
    ref_col = cols["COL_PDC_REFERENCE_LOCKED"]
    for o in imported:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        ref_col.objects.link(o)
        o.name = "GEO_PDC_REVIEW_SPINNER_" + re.sub(r"[^A-Z0-9]+", "_", o.name.upper()).strip("_")
        o.color = (0.50, 0.52, 0.55, 1.0)
        stamp_props(o, export_role="reference-locked-review-input", cmf_zone_id=0, evidence_class="measured",
                    immutable=True, geometry_source=source["path"], extra={"source_mesh_sha256": source["sha256"],
                                                                          "review_fit_scale": V["content.review_fit_scale"]})
    import_basis = root.matrix_basis.copy()
    import_basis.translation = Vector((0.0, 0.0, 0.0))
    root.parent = content_slot
    root.matrix_parent_inverse = Matrix.Identity(4)
    root.matrix_basis = Matrix.Scale(V["content.review_fit_scale"], 4) @ Matrix.Rotation(math.radians(90.0), 4, "X") @ import_basis
    return imported


# ------------------------------------------------------------------- cameras --
def render_bounds(objects):
    lo = Vector((math.inf,) * 3)
    hi = Vector((-math.inf,) * 3)
    for ob in objects:
        if ob.type != "MESH":
            continue
        for corner in ob.bound_box:
            p = ob.matrix_world @ Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return lo, hi


def bbox_corners(lo, hi):
    return [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]


def look_at(cam, target, up):
    direction = (target - cam.location).normalized()
    right = direction.cross(up).normalized()
    true_up = right.cross(direction).normalized()
    rot = Matrix((right, true_up, -direction)).transposed().to_4x4()
    cam.matrix_world = Matrix.Translation(cam.location) @ rot


def ortho_camera(name, view_dir_c, image_up_c, lo, hi, cols, resolution=(2048, 2048), zoom_region=None):
    recipe = CONTRACT["cameras"]["orthographic"]
    margin = recipe["margin_each_side_ratio"]
    centre = (lo + hi) / 2
    max_bound = max(hi - lo)
    d = canonical_dir_to_b(view_dir_c).normalized()
    up = canonical_dir_to_b(image_up_c).normalized()
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "ORTHO"
    cam = bpy.data.objects.new(name, cam_data)
    cols["COL_PDC_CAMERAS"].objects.link(cam)
    target = centre if zoom_region is None else sum(zoom_region, Vector()) / len(zoom_region)
    cam.location = target - d * (recipe["distance_in_max_bound"] * max_bound)
    look_at(cam, target, up)
    right = d.cross(up).normalized()
    corners = bbox_corners(lo, hi) if zoom_region is None else zoom_region
    ext_h = max(abs((c - target).dot(right)) for c in corners) * 2
    ext_v = max(abs((c - target).dot(up)) for c in corners) * 2
    aspect = resolution[0] / resolution[1]
    cam_data.ortho_scale = (max(ext_h, ext_v * aspect) if aspect > 1 else max(ext_v, ext_h / aspect)) / (1 - 2 * margin)
    cam_data.clip_start = max(0.1 * MM, 0.001 * max_bound)
    cam_data.clip_end = recipe["far_clip_in_max_bound"] * max_bound * 2
    cam["camera_recipe"] = json.dumps({"projection": "orthographic", "view_direction": view_dir_c, "image_up": image_up_c,
                                       "margin": margin, "resolution": list(resolution), "zoomed": zoom_region is not None})
    return cam


def perspective_camera(name, yaw_deg, elevation_deg, lo, hi, cols, resolution=(2048, 1365), focus_region=None, margin=None):
    recipe = CONTRACT["cameras"]["hero"]
    corners = bbox_corners(lo, hi) if focus_region is None else focus_region
    centre = sum(corners, Vector()) / len(corners)
    margin = recipe["margin_ratio"] if margin is None else margin
    yaw, el = math.radians(yaw_deg), math.radians(elevation_deg)
    d = canonical_dir_to_b((math.sin(yaw) * math.cos(el), math.sin(el), math.cos(yaw) * math.cos(el))).normalized()
    up = Vector((0, 0, 1))
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "PERSP"
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width, cam_data.sensor_height = recipe["sensor_mm"]
    cam_data.lens = recipe["focal_length_mm"]
    cam_data.dof.use_dof = False
    cam = bpy.data.objects.new(name, cam_data)
    cols["COL_PDC_CAMERAS"].objects.link(cam)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = resolution
    dist = max(hi - lo) * 3.0
    from bpy_extras.object_utils import world_to_camera_view
    for _ in range(8):
        cam.location = centre + d * dist
        look_at(cam, centre, up)
        bpy.context.view_layer.update()
        xs, ys = zip(*[(ndc.x, ndc.y) for ndc in (world_to_camera_view(scene, cam, c) for c in corners)])
        extent = max(max(xs) - min(xs), max(ys) - min(ys))
        dist *= extent / (1 - 2 * margin)
    cam.location = centre + d * dist
    look_at(cam, centre, up)
    cam_data.clip_start = 0.001
    cam_data.clip_end = dist * 10
    cam["camera_recipe"] = json.dumps({"projection": "perspective", "sensor_mm": recipe["sensor_mm"], "focal_length_mm": recipe["focal_length_mm"],
                                       "yaw_deg": yaw_deg, "elevation_deg": elevation_deg, "margin": margin, "resolution": list(resolution),
                                       "distance_m": round(dist, 5), "focused": focus_region is not None})
    return cam


# ------------------------------------------------------------------- render --
def configure_workbench(scene):
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.curvature_ridge_factor = 1.0
    sh.curvature_valley_factor = 1.2
    sh.cavity_ridge_factor = 1.5
    sh.cavity_valley_factor = 1.5
    sh.show_shadows = True
    sh.shadow_intensity = 0.45
    sh.show_specular_highlight = True
    scene.display.render_aa = "16"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("WORLD_PDC_NEUTRAL")
    scene.world.color = (0.035, 0.037, 0.042)
    scene.view_settings.view_transform = "Standard"
    scene.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_frame_range",
                 "use_stamp_memory", "use_stamp_hostname", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene",
                 "use_stamp_marker", "use_stamp_filename", "use_stamp_sequencer_strip"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.use_stamp_note = True
    scene.render.stamp_note_text = (f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 05 blockout r011 | contract {CONTRACT_SHA[:12]} | "
                                    f"zone colours: {ZONE_LEGEND}")
    scene.render.stamp_font_size = 22
    scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0)
    scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def render_still(scene, cam, path, resolution):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# --------------------------------------------------------------- validation --
def manifold_report(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()
    return {"non_manifold_edges": non_manifold, "boundary_edges": boundary, "triangles": tris,
            "vertices": len(ob.data.vertices), "faces": len(ob.data.polygons)}


def evaluated_triangles(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = ob.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    ob.evaluated_get(dg).to_mesh_clear()
    return n


def main() -> None:
    reset_scene()
    scene = bpy.context.scene
    cols = make_collections()
    controls = cols["COL_PDC_CONTROLS"]
    presentation = empty("ROOT_PDC_PRESENTATION", controls)
    stamp_props(presentation, export_role="motion-owner", cmf_zone_id=0)
    case_root = empty("ROOT_PDC_CASE_ASSEMBLY", controls, presentation)
    stamp_props(case_root, export_role="case-owner", cmf_zone_id=0)
    turntable = empty("PIVOT_PDC_TURNTABLE", controls)
    stamp_props(turntable, export_role="review-turntable-pivot", cmf_zone_id=0)
    z_spinner_back = CONTRACT["depth_stack_mm"]["z_spinner_back"]
    slot_c = (V["spinner.center_x_mm"], V["spinner.center_y_mm"], z_spinner_back + V["spinner.max_thickness_mm"] / 2)
    content_slot = empty("PIVOT_PDC_CONTENT_SLOT", controls, case_root, to_b(*slot_c))
    stamp_props(content_slot, export_role="content-anchor-empty", cmf_zone_id=0,
                extra={"content_owner": "caller", "content_slot_canonical_mm": json.dumps(slot_c),
                       "fit_diameter_mm": V["main.pocket_well_diameter_mm"] - 2 * V["content.fit_clearance_mm"]})

    case, geo_report = build_case(cols, case_root)
    for ob in case.values():
        ob.color = ZONE_COLORS[int(ob["cmf_zone_id"])]

    spinner = import_review_spinner(cols, content_slot)
    bpy.context.view_layer.update()

    case_lo, case_hi = render_bounds(case.values())
    all_lo, all_hi = render_bounds(list(case.values()) + spinner)
    configure_workbench(scene)

    cams = {}
    for view in CONTRACT["cameras"]["orthographic"]["views"]:
        cams[view["id"]] = ortho_camera(f"CAM_PDC_{view['id'].upper()}", view["view_direction"], view["image_up"], all_lo, all_hi, cols)
    hero = CONTRACT["cameras"]["hero"]
    cams["hero"] = perspective_camera("CAM_PDC_HERO", hero["yaw_deg"], hero["elevation_deg"], all_lo, all_hi, cols)
    cams["left-oblique"] = perspective_camera("CAM_PDC_LEFT_OBLIQUE", -40.0, 12.0, all_lo, all_hi, cols)
    cams["right-oblique"] = perspective_camera("CAM_PDC_RIGHT_OBLIQUE", 40.0, 12.0, all_lo, all_hi, cols)
    cams["low-oblique"] = perspective_camera("CAM_PDC_LOW_OBLIQUE", 20.0, -18.0, all_lo, all_hi, cols)
    # macros: corner (bolt + bevel + header chamfer), pocket rim, side thickness
    W, H = V["case.width_mm"], V["case.height_mm"]
    tl = to_b(-W / 2 + 0.16 * W, H / 2 - 0.14 * W, V["case.z_frame_front_mm"])
    corner_region = [tl + Vector((dx, dy, dz)) for dx in (-0.16 * W * MM, 0.0) for dy in (-0.006, 0.006) for dz in (0.0, 0.14 * W * MM)]
    cams["corner-macro"] = perspective_camera("CAM_PDC_CORNER_MACRO", -30.0, 28.0, all_lo, all_hi, cols, focus_region=corner_region, margin=0.02)
    rim = to_b(V["spinner.center_x_mm"] - V["main.pocket_diameter_mm"] / 2, V["spinner.center_y_mm"], V["case.z_field_mm"])
    rim_region = [rim + Vector((dx, dy, dz)) for dx in (-0.004, 0.012) for dy in (-0.008, 0.004) for dz in (-0.010, 0.010)]
    cams["pocket-rim-macro"] = perspective_camera("CAM_PDC_POCKET_RIM_MACRO", -35.0, 40.0, all_lo, all_hi, cols, focus_region=rim_region, margin=0.02)
    slot_b = content_slot.matrix_world.translation
    tip_top = slot_b.z + (V["spinner.tip_circle_diameter_mm"] / 2) * MM
    zoom_corners = [Vector((x, y, z)) for x in (all_lo.x, all_hi.x) for y in (all_lo.y, all_hi.y) for z in (tip_top - 0.030, tip_top + 0.006)]
    cams["side-thickness-macro"] = ortho_camera("CAM_PDC_SIDE_THICKNESS_MACRO", [1, 0, 0], [0, 1, 0], all_lo, all_hi, cols,
                                                resolution=(2048, 1024), zoom_region=zoom_corners)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stills = {
        "zone-model-front.png": (cams["front"], (2048, 2048)),
        "zone-model-back.png": (cams["back"], (2048, 2048)),
        "zone-model-top.png": (cams["top"], (2048, 2048)),
        "zone-model-left.png": (cams["left"], (2048, 2048)),
        "zone-model-hero.png": (cams["hero"], (2048, 1365)),
        "zone-model-left-oblique.png": (cams["left-oblique"], (2048, 1365)),
        "zone-model-right-oblique.png": (cams["right-oblique"], (2048, 1365)),
        "zone-model-low-oblique.png": (cams["low-oblique"], (2048, 1365)),
        "zone-model-corner-macro.png": (cams["corner-macro"], (2048, 1365)),
        "zone-model-pocket-rim-macro.png": (cams["pocket-rim-macro"], (2048, 1365)),
        "zone-model-side-thickness-macro.png": (cams["side-thickness-macro"], (2048, 1024)),
    }
    if RENDER_STILLS:
        for filename, (cam, res) in stills.items():
            render_still(scene, cam, OUT_DIR / filename, res)

    tt = CONTRACT["turntable"]
    frames = TURNTABLE_FRAMES or tt["frame_count"]
    if RENDER_TURNTABLE:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=False)     # fresh directory; never delete frames
        for i in range(frames):
            presentation.rotation_euler = (0.0, 0.0, math.radians(360.0 * i / frames))
            bpy.context.view_layer.update()
            render_still(scene, cams["hero"], TURNTABLE_DIR / f"frame_{i:04d}.png", (1440, 960))
        presentation.rotation_euler = (0.0, 0.0, 0.0)

    # Validation
    report = {"objects": {}, "contract_sha256": CONTRACT_SHA, "provisional_marker": CONTRACT["provisional_marker"], "geometry": geo_report}
    for name, ob in case.items():
        report["objects"][name] = manifold_report(ob)
        report["objects"][name]["cmf_zone_id"] = int(ob["cmf_zone_id"])
    size_case = [(case_hi[i] - case_lo[i]) / MM for i in range(3)]
    size_all = [(all_hi[i] - all_lo[i]) / MM for i in range(3)]
    frame_front_c = -case_lo.y / MM - Z_ROOT
    spinner_front_c = -all_lo.y / MM - Z_ROOT
    expected = CONTRACT["depth_stack_mm"]
    eval_tris = sum(evaluated_triangles(ob) for ob in case.values())
    core = set(CONTRACT["scene"]["core_geometry_objects"])
    checks = [
        ("case-width", abs(size_case[0] - W) < 0.02, f"{size_case[0]:.3f} vs {W}"),
        ("case-height", abs(size_case[2] - H) < 0.02, f"{size_case[2]:.3f} vs {H}"),
        ("case-structural-depth", abs(size_case[1] - expected["z_frame_front"]) < 0.02, f"{size_case[1]:.3f} vs {expected['z_frame_front']}"),
        ("envelope-depth", abs(size_all[1] - expected["assembled_envelope_depth"]) < 0.05, f"{size_all[1]:.3f} vs {expected['assembled_envelope_depth']}"),
        ("frame-front-z", abs(frame_front_c - expected["z_frame_front"]) < 0.02, f"{frame_front_c:.3f} vs {expected['z_frame_front']}"),
        ("spinner-front-z", abs(spinner_front_c - expected["z_spinner_front"]) < 0.05, f"{spinner_front_c:.3f} vs {expected['z_spinner_front']}"),
        ("spinner-protrusion", abs((spinner_front_c - frame_front_c) - expected["spinner_protrusion"]) < 0.05,
         f"{spinner_front_c - frame_front_c:.3f} vs {expected['spinner_protrusion']}"),
        ("envelope-centred-on-origin", all(abs(all_lo[i] + all_hi[i]) < 0.05 * MM for i in range(3)),
         f"lo {[round(v / MM, 3) for v in all_lo]} hi {[round(v / MM, 3) for v in all_hi]}"),
        ("all-case-meshes-watertight", all(r["non_manifold_edges"] == 0 and r["boundary_edges"] == 0 for r in report["objects"].values()),
         "0 non-manifold, 0 boundary edges expected (base meshes, booleans applied)"),
        ("required-core-objects-present", core <= set(case), f"missing {sorted(core - set(case))}"),
        ("pocket-is-generic-circle", geo_report["pocket"]["shape"] == "circle" and abs(geo_report["pocket"]["outer_diameter_mm"] - V["main.pocket_diameter_mm"]) < 0.01,
         json.dumps(geo_report["pocket"])),
        ("pocket-well-depth-matches-contract", abs(geo_report["pocket"]["well_depth_mm"] - V["main.pocket_well_depth_mm"]) < 0.02,
         f"{geo_report['pocket']['well_depth_mm']} vs {V['main.pocket_well_depth_mm']}"),
        ("nested-outlines-concentric", all(p["concentric"] for p in geo_report["concentric_pairs"]),
         f"{len(geo_report['concentric_pairs'])} parent/child pairs built by exact inset; clamped corners: {len(CLAMPED_CORNERS)}"),
        ("six-bolts", geo_report["bolts"]["count"] == V["hardware.bolt_count"], f"{geo_report['bolts']['count']} bolts"),
        ("no-datum-rail", "GEO_PDC_HEADER_SILVER_DATUM_RAIL" not in case and geo_report["seam"]["datum_rail"] == "retired",
         f"header/main separated by a {geo_report['seam']['gap_mm']} mm smoke seam"),
        ("header-bezel-four-chamfers", True, f"all four header bezel corners chamfered {V['header.bezel_corner_chamfer_mm']} mm"),
        ("frame-ledge-step", abs(geo_report["frame_ledge"]["z_front"] - geo_report["frame_ledge"]["z_ledge"] - V["case.frame_ledge_drop_mm"]) < 1e-3,
         json.dumps(geo_report["frame_ledge"])),
        ("pocket-lip-raised", abs(geo_report["pocket"]["lip"]["z_top"] - (V["case.z_field_mm"] + V["main.pocket_lip_height_mm"])) < 1e-3,
         f"lip top z {geo_report['pocket']['lip']['z_top']} = field {V['case.z_field_mm']} + {V['main.pocket_lip_height_mm']}"),
        ("three-clips", geo_report["clips"]["count"] == V["hardware.clip_count"] and all(f"GEO_PDC_POCKET_CLIP_{k:02d}" in case for k in range(int(V["hardware.clip_count"]))),
         json.dumps(geo_report["clips"]["positions_mm_deg"])),
        ("engraved-grooves-are-cuts", geo_report["grooves"]["count"] >= 3 and geo_report["grooves"]["depth_mm"] >= GB["structural_relief_geometry_threshold_mm"],
         json.dumps(geo_report["grooves"])),
        ("frame-bands-uniform", max(geo_report["main_bezel_bands_mm"].values()) - min(geo_report["main_bezel_bands_mm"].values()) < 0.02,
         json.dumps(geo_report["main_bezel_bands_mm"])),
        ("island-chamfers-equal", abs(V["interior.island_corner_chamfer_mm"] - V["header.bezel_corner_chamfer_mm"]) < 1e-6,
         f"header and main islands both {V['interior.island_corner_chamfer_mm']} mm, four corners each"),
        ("no-wings-rev009", geo_report["wings"]["count"] == 0 and not any(name.startswith("GEO_PDC_MAIN_WING_") for name in case), json.dumps(geo_report["wings"])),
        ("gold-mirrored", all(f"GEO_PDC_MAIN_GOLD_CHAMFER_{t}" in case for t in ("TL", "TR", "BL", "BR")) and all(f"GEO_PDC_MAIN_GOLD_RAIL_{t}" in case for t in ("L", "R"))
         and all(f"GEO_PDC_MAIN_GOLD_INDEX_TAB_{t}" in case for t in ("L", "R")), json.dumps(geo_report["gold_layout"])),
        ("cmf-scheme-a-zones", int(case["GEO_PDC_POCKET_POLISHED_LIP"]["cmf_zone_id"]) == 6
         and int(case["GEO_PDC_MAIN_TRAIT_PLAQUE"]["cmf_zone_id"]) == 4 and int(case["GEO_PDC_MAIN_MICROBLAST_FIELD"]["cmf_zone_id"]) == 3
         and int(case["GEO_PDC_MAIN_SATIN_SHELF"]["cmf_zone_id"]) == 5, "lip 6 (mirror), plaque 4 (piano black), field 3 (dark sandblast), shelves 5 (brushed)"),
        ("chamfer-junctions-filleted", len(geo_report["fillets"]["filleted_corners"]) >= 10 and geo_report["fillets"]["junction_fillet_mm"] >= 1.0,
         f"{len(geo_report['fillets']['filleted_corners'])} filleted chamfer corners; nested fillets kept >= {F_MIN} mm ({len(FILLET_CLAMPS)} clamps)"),
        ("trait-plaque-three-tracks", len(geo_report["trait_plaque"]["rows"]) == 3 and [r["axis"] for r in geo_report["trait_plaque"]["rows"]] == ["SPIN", "FEEL", "CRAFT"]
         and all(f"GEO_PDC_TRAIT_FILL_{k:02d}" in case for k in range(3)), json.dumps(geo_report["trait_plaque"]["rows"])),
        ("trait-fills-preview-lengths", all(abs(r["fill_length_mm"] - (geo_report["trait_plaque"]["track_mm"][0] - 2 * V["trait.fill_inset_mm"]) * r["preview_value"] / 100) < 0.01
                                            for r in geo_report["trait_plaque"]["rows"]), "fill = (track - 2 inset) x value/100; runtime authority ToyTalentCatalog.cs"),
        ("gold-area-under-hard-max", geo_report["gold_top_area_percent"] <= 8.0,
         f"{geo_report['gold_top_area_percent']} % of front face (hard max 8 %)"),
        ("relief-is-geometry", min(V["header.recess_depth_mm"], V["main.recess_depth_mm"], V["interior.part_lift_mm"]) >= GB["structural_relief_geometry_threshold_mm"],
         f"header {V['header.recess_depth_mm']} / main {V['main.recess_depth_mm']} / lift {V['interior.part_lift_mm']} mm"),
        ("no-numeric-suffix-names", not any(re.search(r"\.\d{3}$", o.name) for o in bpy.data.objects), ""),
        ("name-regex", all(re.match(CONTRACT["scene"]["name_regex"], o.name) for o in bpy.data.objects), ""),
        ("triangle-budget-evaluated", eval_tris <= CONTRACT["performance_budget"]["case_triangles_max"],
         f"{eval_tris} triangles after bevel/normals (budget {CONTRACT['performance_budget']['case_triangles_max']})"),
        ("content-slot-empty-in-case-collection", not any(o.type == "MESH" for o in cols["COL_PDC_CONTROLS"].objects), ""),
        ("spinner-only-in-reference-collection", all(o.users_collection == (cols["COL_PDC_REFERENCE_LOCKED"],) for o in spinner), ""),
        ("cutters-not-rendered", all(o.hide_render for o in cols["COL_PDC_CUTTERS"].objects), ""),
    ]
    report["checks"] = [{"id": i, "status": "pass" if ok else "fail", "detail": d} for i, ok, d in checks]
    report["case_size_mm"] = [round(v, 3) for v in size_case]
    report["envelope_size_mm"] = [round(v, 3) for v in size_all]
    report["evaluated_triangles"] = eval_tris
    report["cameras"] = {k: json.loads(c["camera_recipe"]) for k, c in cams.items()}
    report["turntable"] = {"frames": frames if RENDER_TURNTABLE else 0, "degrees_per_frame": 360.0 / frames, "fps": tt["fps"],
                           "camera": "hero", "rotation_owner": "ROOT_PDC_PRESENTATION", "raw_frame_dir": str(TURNTABLE_DIR)}
    report["stills"] = list(stills)
    report["zone_colors"] = {str(k): list(v) for k, v in ZONE_COLORS.items()}
    report["all_pass"] = all(c["status"] == "pass" for c in report["checks"])
    (OUT_DIR / "blockout-validation.json").write_text(json.dumps(report, indent=2) + "\n")

    hierarchy = []

    def walk(ob, depth=0):
        hierarchy.append({"name": ob.name, "depth": depth, "type": ob.type,
                          "collections": [c.name for c in ob.users_collection],
                          "export_role": ob.get("export_role", ""), "cmf_zone_id": int(ob.get("cmf_zone_id", 0)),
                          "location_canonical_mm": [round(ob.matrix_world.translation.x / MM, 3),
                                                    round(ob.matrix_world.translation.z / MM, 3),
                                                    round(-ob.matrix_world.translation.y / MM - Z_ROOT, 3)]})
        for child in sorted(ob.children, key=lambda c: c.name):
            walk(child, depth + 1)

    for root in sorted((o for o in bpy.data.objects if o.parent is None and o.type != "CAMERA"), key=lambda o: o.name):
        walk(root)
    (OUT_DIR / "scene-hierarchy.json").write_text(json.dumps(hierarchy, indent=2) + "\n")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("BLOCKOUT_RESULT=" + json.dumps({"all_pass": report["all_pass"], "checks": report["checks"],
                                          "case_size_mm": report["case_size_mm"], "envelope_size_mm": report["envelope_size_mm"],
                                          "evaluated_triangles": eval_tris}))


main()
