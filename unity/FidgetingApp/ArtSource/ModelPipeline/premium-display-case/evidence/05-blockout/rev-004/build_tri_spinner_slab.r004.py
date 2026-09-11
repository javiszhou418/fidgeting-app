"""Deterministic bpy builder for the premium-display-case `tri-spinner-slab-v3-cmf`
variant (Gate 05 blockout, evidence rev-004).

    blender -b --python tools/blender/build_tri_spinner_slab.py -- [--no-turntable] [--frames N]

Every dimension is read from the Gate 03 rev-004 `modeling-contract.json`.
There are no geometry constants in this file; the only literals are topology
choices (segment counts) and render settings. Geometry is authored in the
canonical product space (mm; +X right, +Y up, +Z toward the viewer, origin at
the assembled-envelope centre) and converted once to Blender space
(B = (C.x, -C.z, C.y) * 0.001).

The caller-owned spinner is imported into `COL_PDC_REFERENCE_LOCKED` as a
review input under `PIVOT_PDC_CONTENT_SLOT`; it is never part of the case
export. All exported outputs are stamped `PROVISIONAL_DIMENSIONS` because the
case size derives from concept-image ratios.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-004/modeling-contract.json"
OUT_DIR = PIPELINE / "evidence/05-blockout/rev-004"
TURNTABLE_DIR = Path("/tmp/tri-spinner-slab-g05-r004-turntable")
BLEND_PATH = OUT_DIR / "tri-spinner-slab-blockout-r004.blend"

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
TURNTABLE_FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else None

CORNER_SEGMENTS = 12          # per rounded-rectangle corner arc
LOBE_SEGMENTS = 28            # per pocket lobe arc (120 deg each)
RING_SAMPLES = 480                # resample count when bridging dissimilar loops (field <-> pocket)
MM = 0.001


# ----------------------------------------------------------------- contract --
def load_contract() -> tuple[dict, dict, str]:
    contract = json.loads(CONTRACT_PATH.read_text())
    values = {p["id"]: p.get("value") for p in contract["parameters"]["inputs"]}
    for pid, rec in contract["resolved"].items():
        values[pid] = rec["value"]
    return contract, values, contract["hashing"]["contract_sha256"]


CONTRACT, V, CONTRACT_SHA = load_contract()
Z_ROOT = V["case.root_recentering_z_mm"]


def to_b(x: float, y: float, z: float) -> Vector:
    """Canonical mm (already in construction space, rear outer face z = 0) to Blender metres."""
    z = z + Z_ROOT
    return Vector((x * MM, -z * MM, y * MM))


def to_b_dir(x: float, y: float, z: float) -> Vector:
    return Vector((x * MM, -z * MM, y * MM))


def canonical_dir_to_b(v) -> Vector:
    return Vector((v[0], -v[2], v[1]))


# ----------------------------------------------------------------- 2D loops --
def rounded_rect(x0: float, y0: float, x1: float, y1: float, r: float, seg: int = CORNER_SEGMENTS) -> list[tuple[float, float]]:
    """CCW rounded rectangle from (x0,y0) to (x1,y1) with corner radius r."""
    r = max(0.0, min(r, (x1 - x0) / 2 - 1e-6, (y1 - y0) / 2 - 1e-6))
    centres = [(x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)]
    pts = []
    for cx, cy, a0 in centres:
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return dedupe(pts)


def tri_lobe(cx: float, cy: float, d: float, r: float, seg: int = LOBE_SEGMENTS) -> list[tuple[float, float]]:
    """CCW convex hull of three equal circles (radius r) at distance d from
    (cx, cy), one lobe pointing up (+Y)."""
    pts = []
    for lobe in (90.0, 210.0, 330.0):
        lx, ly = cx + d * math.cos(math.radians(lobe)), cy + d * math.sin(math.radians(lobe))
        for i in range(seg + 1):
            a = math.radians(lobe - 60.0 + 120.0 * i / seg)
            pts.append((lx + r * math.cos(a), ly + r * math.sin(a)))
    return dedupe(pts)


def chamfered_rect(x0: float, y0: float, x1: float, y1: float, c: float) -> list[tuple[float, float]]:
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def rotated_rect(cx: float, cy: float, length: float, width: float, angle_deg: float) -> list[tuple[float, float]]:
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    hl, hw = length / 2, width / 2
    return [(cx + ux * s * hl + vx * t * hw, cy + uy * s * hl + vy * t * hw) for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def dedupe(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out = []
    for p in pts:
        if not out or (abs(out[-1][0] - p[0]) > 1e-7 or abs(out[-1][1] - p[1]) > 1e-7):
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-7 and abs(out[0][1] - out[-1][1]) < 1e-7:
        out.pop()
    return out


def resample(loop: list[tuple[float, float]], n: int) -> list[tuple[float, float]]:
    """Equal-arc-length resample of a closed polyline to n points, starting at
    the point with the smallest non-negative polar angle about the centroid so
    that two loops bridged together stay rotationally aligned."""
    cx = sum(p[0] for p in loop) / len(loop)
    cy = sum(p[1] for p in loop) / len(loop)
    start = min(range(len(loop)), key=lambda i: (math.atan2(loop[i][1] - cy, loop[i][0] - cx) % (2 * math.pi)))
    loop = loop[start:] + loop[:start]
    seg_len = []
    for i in range(len(loop)):
        a, b = loop[i], loop[(i + 1) % len(loop)]
        seg_len.append(math.hypot(b[0] - a[0], b[1] - a[1]))
    total = sum(seg_len)
    out = []
    target = 0.0
    i = 0
    acc = 0.0
    for k in range(n):
        target = total * k / n
        while acc + seg_len[i] < target - 1e-12:
            acc += seg_len[i]
            i = (i + 1) % len(loop)
        a, b = loop[i], loop[(i + 1) % len(loop)]
        t = 0.0 if seg_len[i] == 0 else (target - acc) / seg_len[i]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


# --------------------------------------------------------------- bmesh solids --
def finish(bm: bmesh.types.BMesh, name: str, collection: bpy.types.Collection, parent: bpy.types.Object) -> bpy.types.Object:
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    ob.parent = parent
    return ob


def solid_from_loop(name, loop, z0, z1, collection, parent):
    bm = bmesh.new()
    verts = [bm.verts.new(to_b(x, y, z0)) for x, y in loop]
    face = bm.faces.new(verts)
    res = bmesh.ops.extrude_face_region(bm, geom=[face])
    new_verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=to_b_dir(0, 0, z1 - z0))
    return finish(bm, name, collection, parent)


def ray_hit(loop: list[tuple[float, float]], cx: float, cy: float, angle: float) -> tuple[float, float]:
    """Farthest intersection of the ray from (cx, cy) at `angle` with a closed polygon."""
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
    """Sample both loops at the same n polar angles about (cx, cy). Valid when
    both loops are star-shaped from that point; guarantees untwisted quads."""
    angles = [2 * math.pi * k / n for k in range(n)]
    return [ray_hit(outer, cx, cy, a) for a in angles], [ray_hit(inner, cx, cy, a) for a in angles]


def ring_solid(name, outer, inner, z0, z1, collection, parent, samples=None, radial_center=None):
    """Bridge two closed loops into a watertight ring solid. Loops built from
    the same parametrisation (equal length, same start corner) bridge 1:1 so
    corner arcs survive; dissimilar loops are paired radially about
    `radial_center` (or resampled by arc length when no centre is given)."""
    if radial_center is not None:
        samples = samples or RING_SAMPLES
        outer, inner = radial_pair(outer, inner, radial_center[0], radial_center[1], samples)
    elif samples is None and len(outer) == len(inner):
        samples = len(outer)
    else:
        samples = samples or RING_SAMPLES
        outer = resample(outer, samples)
        inner = resample(inner, samples)
    bm = bmesh.new()
    vo = [bm.verts.new(to_b(x, y, z0)) for x, y in outer]
    vi = [bm.verts.new(to_b(x, y, z0)) for x, y in inner]
    faces = []
    for i in range(samples):
        j = (i + 1) % samples
        faces.append(bm.faces.new((vo[i], vo[j], vi[j], vi[i])))
    res = bmesh.ops.extrude_face_region(bm, geom=faces)
    new_verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=new_verts, vec=to_b_dir(0, 0, z1 - z0))
    return finish(bm, name, collection, parent)


def multi_solid(name, loops, z0, z1, collection, parent):
    bm = bmesh.new()
    for loop in loops:
        verts = [bm.verts.new(to_b(x, y, z0)) for x, y in loop]
        face = bm.faces.new(verts)
        res = bmesh.ops.extrude_face_region(bm, geom=[face])
        new_verts = [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=new_verts, vec=to_b_dir(0, 0, z1 - z0))
    return finish(bm, name, collection, parent)


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
    return cols


def empty(name: str, collection, parent=None, location=None) -> bpy.types.Object:
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "PLAIN_AXES"
    ob.empty_display_size = 0.01
    collection.objects.link(ob)
    ob.parent = parent
    if location is not None:
        ob.location = location
    return ob


def stamp_props(ob: bpy.types.Object, *, export_role: str, cmf_zone_id: int, evidence_class: str = "recommended_start",
                immutable: bool = False, softfocus: bool = False, geometry_source: str = "deterministic_bpy:tools/blender/build_tri_spinner_slab.py",
                extra: dict | None = None) -> None:
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


# --------------------------------------------------------------- the geometry --
def build_case(cols, case_root) -> dict[str, bpy.types.Object]:
    W, H = V["case.width_mm"], V["case.height_mm"]
    r_o, r_i = V["case.outer_corner_radius_mm"], V["case.inner_corner_radius_mm"]
    t_c, t_l = V["case.crystal_wall_mm"], V["case.smoke_liner_mm"]
    sep = CONTRACT["geometry_builder"]["minimum_render_separation_mm"]
    shelf = V["main.perimeter_shelf_width_mm"]
    mirror = V["cmf.mirror_bevel_width_mm"]
    gold_w = V["cmf.gold_inlay_width_mm"]
    gold_relief = V["cmf.gold_relief_mm"]
    lift = V["interior.part_lift_mm"]
    z_b = V["case.backplate_thickness_mm"]
    z_int0 = z_b + sep
    z_shelf = V["case.z_shelf_top_mm"]
    z_frame = V["case.z_frame_front_mm"]
    z_liner_top = z_frame - V["header.recess_depth_mm"]
    z_header_plate = z_shelf - V["header.recess_depth_mm"]
    z_field = z_shelf - V["main.recess_depth_mm"]
    liner_inset = V["main.liner_inset_mm"]
    y_seam = H / 2 - V["header.height_mm"]                       # seam under the header plate rail
    y_bay = H / 2 - V["visual.main_bay_start_from_top"] * H     # main bay starts below the datum rail
    hx0, hx1 = -W / 2 + liner_inset, W / 2 - liner_inset
    y_c = V["spinner.center_y_mm"]
    geo = cols["COL_PDC_GEOMETRY_STATIC"]
    out = {}

    def add(name, ob, zone, **kw):
        stamp_props(ob, export_role="case-geometry", cmf_zone_id=zone, **kw)
        out[name] = ob
        return ob

    # Rear plate: inside the crystal frame, separated by the render gap.
    add("GEO_PDC_REAR_PLATE", solid_from_loop(
        "GEO_PDC_REAR_PLATE", rounded_rect(-W / 2 + t_c + sep, -H / 2 + t_c + sep, W / 2 - t_c - sep, H / 2 - t_c - sep, r_o - t_c - sep),
        0.0, z_b, geo, case_root), 3)

    # Outer crystal frame: watertight ring, rear face to frame front.
    frame = add("GEO_PDC_OUTER_CRYSTAL_FRAME", ring_solid(
        "GEO_PDC_OUTER_CRYSTAL_FRAME",
        rounded_rect(-W / 2, -H / 2, W / 2, H / 2, r_o),
        rounded_rect(-W / 2 + t_c, -H / 2 + t_c, W / 2 - t_c, H / 2 - t_c, r_o - t_c),
        0.0, z_frame, geo, case_root), 1, softfocus=True)
    bevel = frame.modifiers.new("030_BEVEL_PRIMARY", "BEVEL")
    bevel.width = V["case.crystal_bevel_mm"] * MM
    bevel.segments = CONTRACT["geometry_builder"]["bevel"]["outer_segments"]
    bevel.profile = CONTRACT["geometry_builder"]["bevel"]["profile"]
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(CONTRACT["geometry_builder"]["smooth_by_angle_deg"])
    bevel.use_clamp_overlap = CONTRACT["geometry_builder"]["bevel"]["clamp_overlap"]

    # Smoke liner: nested ring, separated from crystal and rear plate.
    add("GEO_PDC_SMOKE_INNER_LINER", ring_solid(
        "GEO_PDC_SMOKE_INNER_LINER",
        rounded_rect(-W / 2 + t_c + sep, -H / 2 + t_c + sep, W / 2 - t_c - sep, H / 2 - t_c - sep, r_o - t_c - sep),
        rounded_rect(hx0, -H / 2 + liner_inset, hx1, H / 2 - liner_inset, r_i),
        z_int0, z_liner_top, geo, case_root), 2)

    # --- Header compartment
    header_outer = rounded_rect(hx0, y_seam, hx1, H / 2 - liner_inset, r_i)
    plate_inset_b = V["header.plate_side_inset_mm"]
    px0, px1 = hx0 + shelf, hx1 - shelf
    py0, py1 = y_seam + plate_inset_b, H / 2 - liner_inset - shelf
    pocket = rounded_rect(px0, py0, px1, py1, r_i * 0.6)
    add("GEO_PDC_HEADER_SATIN_SHELF", ring_solid("GEO_PDC_HEADER_SATIN_SHELF", header_outer, pocket, z_int0, z_shelf, geo, case_root), 5)
    add("GEO_PDC_HEADER_MIRROR_BEVEL", ring_solid(
        "GEO_PDC_HEADER_MIRROR_BEVEL", rounded_rect(px0 + sep, py0 + sep, px1 - sep, py1 - sep, r_i * 0.6 - sep),
        rounded_rect(px0 + sep + mirror, py0 + sep + mirror, px1 - sep - mirror, py1 - sep - mirror, max(0.3, r_i * 0.6 - sep - mirror)),
        z_int0, z_header_plate - V["header.recess_depth_mm"] * 0.5, geo, case_root), 6, softfocus=True)
    gi = sep + mirror + sep
    add("GEO_PDC_HEADER_GRAPHITE_PLANE", solid_from_loop(
        "GEO_PDC_HEADER_GRAPHITE_PLANE", rounded_rect(px0 + gi, py0 + gi, px1 - gi, py1 - gi, max(0.3, r_i * 0.6 - gi)),
        z_int0, z_header_plate, geo, case_root), 4)
    rail_lift = V["interior.datum_rail_lift_mm"]
    add("GEO_PDC_HEADER_SILVER_DATUM_RAIL", solid_from_loop(
        "GEO_PDC_HEADER_SILVER_DATUM_RAIL", rounded_rect(hx0, y_bay + sep, hx1, y_seam - sep, 0.4),
        z_int0, z_shelf + rail_lift, geo, case_root), 5)
    # Two short gold bars on the header shelf strip under the plate, left and right.
    bar_len = 0.10 * W
    bar_y = y_seam + plate_inset_b / 2
    bar_cx = W / 2 - liner_inset - shelf - bar_len / 2 - 0.05 * W
    add("GEO_PDC_HEADER_GOLD_INLAY_L", solid_from_loop(
        "GEO_PDC_HEADER_GOLD_INLAY_L", rotated_rect(-bar_cx, bar_y, bar_len, gold_w, 0.0),
        z_shelf - lift / 2, z_shelf + gold_relief, geo, case_root), 7)
    add("GEO_PDC_HEADER_GOLD_INLAY_R", solid_from_loop(
        "GEO_PDC_HEADER_GOLD_INLAY_R", rotated_rect(bar_cx, bar_y, bar_len, gold_w, 0.0),
        z_shelf - lift / 2, z_shelf + gold_relief, geo, case_root), 7)

    # --- Main compartment
    main_outer = rounded_rect(hx0, -H / 2 + liner_inset, hx1, y_bay, r_i)
    fx0, fx1 = hx0 + shelf, hx1 - shelf
    fy0, fy1 = V["main.field_bottom_y_mm"], V["main.field_top_y_mm"]
    field = rounded_rect(fx0, fy0, fx1, fy1, r_i)
    add("GEO_PDC_MAIN_SATIN_SHELF", ring_solid("GEO_PDC_MAIN_SATIN_SHELF", main_outer, field, z_int0, z_shelf, geo, case_root), 5)
    add("GEO_PDC_MAIN_MIRROR_SEAM", ring_solid(
        "GEO_PDC_MAIN_MIRROR_SEAM", rounded_rect(fx0 + sep, fy0 + sep, fx1 - sep, fy1 - sep, r_i - sep),
        rounded_rect(fx0 + sep + mirror, fy0 + sep + mirror, fx1 - sep - mirror, fy1 - sep - mirror, r_i - sep - mirror),
        z_int0, z_field - V["main.recess_depth_mm"] * 0.25, geo, case_root), 6, softfocus=True)
    pocket_loop = tri_lobe(V["spinner.center_x_mm"], y_c, V["main.pocket_lobe_center_radius_mm"], V["main.pocket_lobe_radius_mm"])
    add("GEO_PDC_MAIN_MICROBLAST_FIELD", ring_solid(
        "GEO_PDC_MAIN_MICROBLAST_FIELD",
        rounded_rect(fx0 + gi, fy0 + gi, fx1 - gi, fy1 - gi, r_i - gi), pocket_loop,
        z_int0, z_field, geo, case_root, samples=RING_SAMPLES, radial_center=(V["spinner.center_x_mm"], y_c)), 3)

    # Raised brushed panels either side of the spinner, above hub height so
    # they clear the flared lower lobes of the pocket.
    panel_w, panel_h = 0.088 * W, 0.20 * H
    panel_inner = fx1 - gi - 1.0 - panel_w
    panel_y0 = y_c - 1.0
    for suffix, sign in (("L", -1), ("R", 1)):
        x_lo = sign * panel_inner if sign > 0 else -(panel_inner + panel_w)
        add(f"GEO_PDC_MAIN_BRUSHED_PANEL_{suffix}", solid_from_loop(
            f"GEO_PDC_MAIN_BRUSHED_PANEL_{suffix}", chamfered_rect(x_lo, panel_y0, x_lo + panel_w, panel_y0 + panel_h, 1.5),
            z_field - lift / 2, z_field + lift, geo, case_root), 5)
    band_h = 0.055 * H
    add("GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM", solid_from_loop(
        "GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM", rounded_rect(fx0 + gi + 1.5, fy0 + gi + 1.5, fx1 - gi - 1.5, fy0 + gi + 1.5 + band_h, 0.6),
        z_field - lift / 2, z_field + lift, geo, case_root), 5)
    facet_len, facet_w, facet_in = 0.09 * W, 0.8, 4.5
    facets = [
        rotated_rect(fx0 + facet_in, fy1 - facet_in, facet_len, facet_w, -45.0),
        rotated_rect(fx1 - facet_in, fy1 - facet_in, facet_len, facet_w, 45.0),
        rotated_rect(fx0 + facet_in, fy0 + facet_in, facet_len, facet_w, 45.0),
        rotated_rect(fx1 - facet_in, fy0 + facet_in, facet_len, facet_w, -45.0),
    ]
    add("GEO_PDC_MAIN_CORNER_FACETS", multi_solid("GEO_PDC_MAIN_CORNER_FACETS", facets, z_field - lift / 2, z_field + lift * 0.75, geo, case_root), 5)

    # Gold: two discontinuous rails and one small index tab. Never a closed loop.
    rail00_x = fx1 - gi - 0.6
    add("GEO_PDC_MAIN_GOLD_RAIL_00", solid_from_loop(
        "GEO_PDC_MAIN_GOLD_RAIL_00", rotated_rect(rail00_x, y_c + 0.09 * H, gold_w, 0.14 * H, 0.0),
        z_field - lift / 2, z_field + gold_relief, geo, case_root), 7)
    add("GEO_PDC_MAIN_GOLD_RAIL_01", solid_from_loop(
        "GEO_PDC_MAIN_GOLD_RAIL_01", rotated_rect(fx0 + gi + 1.2 + 0.04 * W, fy1 - gi - 1.2, 0.08 * W, gold_w, 0.0),
        z_field - lift / 2, z_field + gold_relief, geo, case_root), 7)
    tab = 0.02 * W
    add("GEO_PDC_MAIN_GOLD_INDEX_TAB", solid_from_loop(
        "GEO_PDC_MAIN_GOLD_INDEX_TAB", rounded_rect(fx0 + gi + 1.2, fy0 + gi + 1.2, fx0 + gi + 1.2 + tab, fy0 + gi + 1.2 + tab, 0.2),
        z_field - lift / 2, z_field + gold_relief, geo, case_root), 7)

    smooth_angle = math.radians(CONTRACT["geometry_builder"]["smooth_by_angle_deg"])
    for ob in out.values():
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=smooth_angle)
    return out


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
        o.color = (0.42, 0.44, 0.47, 1.0)
        stamp_props(o, export_role="reference-locked-review-input", cmf_zone_id=0, evidence_class="measured",
                    immutable=True, geometry_source=f"{source['path']}", extra={"source_mesh_sha256": source["sha256"]})
    # The glTF importer already carries the Y-up -> Z-up conversion in the
    # root's basis (spin axis lands on Blender +Z, one tip on +Y). Compose a
    # further +90 deg about X so the axis faces the viewer (Blender -Y =
    # canonical +Z) and the tip points up (+Z).
    import_basis = root.matrix_basis.copy()
    import_basis.translation = Vector((0.0, 0.0, 0.0))
    root.parent = content_slot
    root.matrix_parent_inverse = Matrix.Identity(4)
    root.matrix_basis = Matrix.Rotation(math.radians(90.0), 4, "X") @ import_basis
    return imported


# ------------------------------------------------------------------- cameras --
def render_bounds(objects) -> tuple[Vector, Vector]:
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


def bbox_corners(lo: Vector, hi: Vector) -> list[Vector]:
    return [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]


def look_at(cam: bpy.types.Object, target: Vector, up: Vector) -> None:
    direction = (target - cam.location).normalized()
    right = direction.cross(up).normalized()
    true_up = right.cross(direction).normalized()
    rot = Matrix((right, true_up, -direction)).transposed().to_4x4()
    cam.matrix_world = Matrix.Translation(cam.location) @ rot


def ortho_camera(name, view_dir_c, image_up_c, lo, hi, cols, resolution=(2048, 2048), zoom_region=None) -> bpy.types.Object:
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
    cam.location = centre - d * (recipe["distance_in_max_bound"] * max_bound)
    look_at(cam, centre, up)
    right = d.cross(up).normalized()
    corners = bbox_corners(lo, hi) if zoom_region is None else zoom_region
    ext_h = max(abs((c - centre).dot(right)) for c in corners) * 2
    ext_v = max(abs((c - centre).dot(up)) for c in corners) * 2
    aspect = resolution[0] / resolution[1]
    cam_data.ortho_scale = max(ext_v, ext_h / aspect) / (1 - 2 * margin) * (1 if aspect <= 1 else 1)
    if aspect > 1:
        cam_data.ortho_scale = max(ext_h, ext_v * aspect) / (1 - 2 * margin)
    cam_data.clip_start = max(0.1 * MM, 0.001 * max_bound)
    cam_data.clip_end = recipe["far_clip_in_max_bound"] * max_bound * 2
    if zoom_region is not None:
        zc = sum(zoom_region, Vector()) / len(zoom_region)
        cam.location = zc - d * (recipe["distance_in_max_bound"] * max_bound)
        look_at(cam, zc, up)
    cam["camera_recipe"] = json.dumps({"projection": "orthographic", "view_direction": view_dir_c, "image_up": image_up_c,
                                       "margin": margin, "resolution": list(resolution)})
    return cam


def perspective_camera(name, yaw_deg, elevation_deg, lo, hi, cols, resolution=(2048, 1365)) -> bpy.types.Object:
    recipe = CONTRACT["cameras"]["hero"]
    centre = (lo + hi) / 2
    margin = recipe["margin_ratio"]
    yaw, el = math.radians(yaw_deg), math.radians(elevation_deg)
    dir_from_target_c = (math.sin(yaw) * math.cos(el), math.sin(el), math.cos(yaw) * math.cos(el))
    d = canonical_dir_to_b(dir_from_target_c).normalized()
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
    for _ in range(6):
        cam.location = centre + d * dist
        look_at(cam, centre, up)
        bpy.context.view_layer.update()
        from bpy_extras.object_utils import world_to_camera_view
        xs, ys = [], []
        for c in bbox_corners(lo, hi):
            ndc = world_to_camera_view(scene, cam, c)
            xs.append(ndc.x)
            ys.append(ndc.y)
        extent = max(max(xs) - min(xs), max(ys) - min(ys))
        dist *= extent / (1 - 2 * margin)
    cam.location = centre + d * dist
    look_at(cam, centre, up)
    cam_data.clip_start = 0.001
    cam_data.clip_end = dist * 10
    cam["camera_recipe"] = json.dumps({"projection": "perspective", "sensor_mm": recipe["sensor_mm"], "focal_length_mm": recipe["focal_length_mm"],
                                       "yaw_deg": yaw_deg, "elevation_deg": elevation_deg, "margin": margin, "resolution": list(resolution),
                                       "distance_m": round(dist, 5)})
    return cam


# ------------------------------------------------------------------- render --
def configure_workbench(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "OBJECT"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.curvature_ridge_factor = 0.6
    sh.curvature_valley_factor = 0.8
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.show_specular_highlight = True
    scene.display.render_aa = "8"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("WORLD_PDC_NEUTRAL")
    scene.world.color = (0.035, 0.037, 0.042)
    scene.view_settings.view_transform = "Standard"
    # provisional watermark
    scene.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_frame_range",
                 "use_stamp_memory", "use_stamp_hostname", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene",
                 "use_stamp_marker", "use_stamp_filename", "use_stamp_sequencer_strip"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.use_stamp_note = True
    scene.render.stamp_note_text = (f"PROVISIONAL_DIMENSIONS | premium-display-case / tri-spinner-slab-v3-cmf | Gate 05 blockout r004 | "
                                    f"contract {CONTRACT_SHA[:12]} | white model, no materials")
    scene.render.stamp_font_size = 22
    scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0)
    scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def render_still(scene, cam, path: Path, resolution) -> None:
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# --------------------------------------------------------------- validation --
def manifold_report(ob: bpy.types.Object) -> dict:
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()
    return {"non_manifold_edges": non_manifold, "boundary_edges": boundary, "triangles": tris,
            "vertices": len(ob.data.vertices), "faces": len(ob.data.polygons)}


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
                extra={"content_owner": "caller", "content_slot_canonical_mm": json.dumps(slot_c)})

    case = build_case(cols, case_root)
    for ob in case.values():
        ob.color = (0.80, 0.81, 0.83, 1.0)
    case["GEO_PDC_OUTER_CRYSTAL_FRAME"].color = (0.93, 0.95, 0.98, 1.0)
    case["GEO_PDC_SMOKE_INNER_LINER"].color = (0.86, 0.84, 0.90, 1.0)
    case["GEO_PDC_HEADER_GRAPHITE_PLANE"].color = (0.55, 0.56, 0.58, 1.0)
    for n in ("GEO_PDC_MAIN_GOLD_RAIL_00", "GEO_PDC_MAIN_GOLD_RAIL_01", "GEO_PDC_MAIN_GOLD_INDEX_TAB",
              "GEO_PDC_HEADER_GOLD_INLAY_L", "GEO_PDC_HEADER_GOLD_INLAY_R"):
        case[n].color = (0.72, 0.66, 0.52, 1.0)

    spinner = import_review_spinner(cols, content_slot)
    bpy.context.view_layer.update()

    case_lo, case_hi = render_bounds(case.values())
    all_lo, all_hi = render_bounds(list(case.values()) + spinner)
    configure_workbench(scene)

    # Cameras (canonical recipes from the contract)
    ortho = CONTRACT["cameras"]["orthographic"]["views"]
    cams = {}
    for view in ortho:
        cams[view["id"]] = ortho_camera(f"CAM_PDC_{view['id'].upper()}", view["view_direction"], view["image_up"], all_lo, all_hi, cols)
    hero = CONTRACT["cameras"]["hero"]
    cams["hero"] = perspective_camera("CAM_PDC_HERO", hero["yaw_deg"], hero["elevation_deg"], all_lo, all_hi, cols)
    cams["left-oblique"] = perspective_camera("CAM_PDC_LEFT_OBLIQUE", -40.0, 12.0, all_lo, all_hi, cols)
    cams["right-oblique"] = perspective_camera("CAM_PDC_RIGHT_OBLIQUE", 40.0, 12.0, all_lo, all_hi, cols)
    cams["low-oblique"] = perspective_camera("CAM_PDC_LOW_OBLIQUE", 20.0, -18.0, all_lo, all_hi, cols)
    # Side thickness macro: orthographic from the left, zoomed on the upper edge
    # so frame front vs spinner front (protrusion) is legible.
    slot_b = content_slot.matrix_world.translation
    tip_top = slot_b.z + (V["spinner.tip_circle_diameter_mm"] / 2) * MM
    zoom_corners = [Vector((x, y, z)) for x in (all_lo.x, all_hi.x) for y in (all_lo.y, all_hi.y)
                    for z in (tip_top - 0.030, tip_top + 0.006)]
    cams["side-thickness-macro"] = ortho_camera("CAM_PDC_SIDE_THICKNESS_MACRO", [1, 0, 0], [0, 1, 0], all_lo, all_hi, cols,
                                                resolution=(2048, 1024), zoom_region=zoom_corners)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stills = {
        "white-model-front.png": (cams["front"], (2048, 2048)),
        "white-model-back.png": (cams["back"], (2048, 2048)),
        "white-model-top.png": (cams["top"], (2048, 2048)),
        "white-model-left.png": (cams["left"], (2048, 2048)),
        "white-model-hero.png": (cams["hero"], (2048, 1365)),
        "white-model-left-oblique.png": (cams["left-oblique"], (2048, 1365)),
        "white-model-right-oblique.png": (cams["right-oblique"], (2048, 1365)),
        "white-model-low-oblique.png": (cams["low-oblique"], (2048, 1365)),
        "white-model-side-thickness-macro.png": (cams["side-thickness-macro"], (2048, 1024)),
    }
    for filename, (cam, res) in stills.items():
        render_still(scene, cam, OUT_DIR / filename, res)

    # Turntable: fixed hero camera, PresentationRoot rotates about canonical +Y.
    tt = CONTRACT["turntable"]
    frames = TURNTABLE_FRAMES or tt["frame_count"]
    if RENDER_TURNTABLE:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=True)
        for f in TURNTABLE_DIR.glob("*.png"):
            f.unlink()
        step = 360.0 / frames
        for i in range(frames):
            presentation.rotation_euler = (0.0, 0.0, math.radians(step * i))
            bpy.context.view_layer.update()
            render_still(scene, cams["hero"], TURNTABLE_DIR / f"frame_{i:04d}.png", (1440, 960))
        presentation.rotation_euler = (0.0, 0.0, 0.0)

    # Validation
    report = {"objects": {}, "contract_sha256": CONTRACT_SHA, "provisional_marker": CONTRACT["provisional_marker"]}
    for name, ob in case.items():
        report["objects"][name] = manifold_report(ob)
    size_case = [(case_hi[i] - case_lo[i]) / MM for i in range(3)]
    size_all = [(all_hi[i] - all_lo[i]) / MM for i in range(3)]
    frame_front_c = -case_lo.y / MM - Z_ROOT  # Blender -Y is canonical +Z; undo recentering
    spinner_front_c = -all_lo.y / MM - Z_ROOT
    expected = CONTRACT["depth_stack_mm"]
    checks = [
        ("case-width", abs(size_case[0] - V["case.width_mm"]) < 0.02, f"{size_case[0]:.3f} vs {V['case.width_mm']}"),
        ("case-height", abs(size_case[2] - V["case.height_mm"]) < 0.02, f"{size_case[2]:.3f} vs {V['case.height_mm']}"),
        ("case-structural-depth", abs(size_case[1] - expected["z_frame_front"]) < 0.02, f"{size_case[1]:.3f} vs {expected['z_frame_front']}"),
        ("envelope-depth", abs(size_all[1] - expected["assembled_envelope_depth"]) < 0.05, f"{size_all[1]:.3f} vs {expected['assembled_envelope_depth']}"),
        ("frame-front-z", abs(frame_front_c - expected["z_frame_front"]) < 0.02, f"{frame_front_c:.3f} vs {expected['z_frame_front']}"),
        ("spinner-front-z", abs(spinner_front_c - expected["z_spinner_front"]) < 0.05, f"{spinner_front_c:.3f} vs {expected['z_spinner_front']}"),
        ("spinner-protrusion", abs((spinner_front_c - frame_front_c) - expected["spinner_protrusion"]) < 0.05,
         f"{spinner_front_c - frame_front_c:.3f} vs {expected['spinner_protrusion']}"),
        ("envelope-centred-on-origin", all(abs(all_lo[i] + all_hi[i]) < 0.05 * MM for i in (0, 1)) and abs(all_lo.z + all_hi.z) < 0.05 * MM,
         f"lo {[round(v / MM, 3) for v in all_lo]} hi {[round(v / MM, 3) for v in all_hi]}"),
        ("all-case-meshes-watertight", all(r["non_manifold_edges"] == 0 and r["boundary_edges"] == 0 for r in report["objects"].values()),
         "0 non-manifold, 0 boundary edges expected"),
        ("required-core-objects-present", set(CONTRACT["scene"]["core_geometry_objects"]) <= set(case), ""),
        ("no-numeric-suffix-names", not any(re.search(r"\.\d{3}$", o.name) for o in bpy.data.objects), ""),
        ("name-regex", all(re.match(CONTRACT["scene"]["name_regex"], o.name) for o in bpy.data.objects), ""),
        ("triangle-budget", sum(r["triangles"] for r in report["objects"].values()) <= CONTRACT["performance_budget"]["case_triangles_max"],
         f"{sum(r['triangles'] for r in report['objects'].values())} triangles (pre-bevel)"),
        ("content-slot-empty-in-case-collection", not any(o.type == "MESH" for o in cols["COL_PDC_CONTROLS"].objects), ""),
        ("spinner-only-in-reference-collection", all(o.users_collection == (cols["COL_PDC_REFERENCE_LOCKED"],) for o in spinner), ""),
    ]
    report["checks"] = [{"id": i, "status": "pass" if ok else "fail", "detail": d} for i, ok, d in checks]
    report["case_size_mm"] = [round(v, 3) for v in size_case]
    report["envelope_size_mm"] = [round(v, 3) for v in size_all]
    report["cameras"] = {k: json.loads(c["camera_recipe"]) for k, c in cams.items()}
    report["turntable"] = {"frames": frames if RENDER_TURNTABLE else 0, "degrees_per_frame": 360.0 / frames, "fps": tt["fps"],
                           "camera": "hero", "rotation_owner": "ROOT_PDC_PRESENTATION", "raw_frame_dir": str(TURNTABLE_DIR)}
    report["stills"] = list(stills)
    report["all_pass"] = all(c["status"] == "pass" for c in report["checks"])
    (OUT_DIR / "blockout-validation.json").write_text(json.dumps(report, indent=2) + "\n")

    hierarchy = []

    def walk(ob, depth=0):
        hierarchy.append({"name": ob.name, "depth": depth, "type": ob.type,
                          "collections": [c.name for c in ob.users_collection],
                          "export_role": ob.get("export_role", ""),
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
                                          "case_size_mm": report["case_size_mm"], "envelope_size_mm": report["envelope_size_mm"]}))


main()
