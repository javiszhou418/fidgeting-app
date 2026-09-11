"""Gate 05 blockout rev-006 · GEEONE 龙鳞三叶 · built from the Gate 02 rev-006 geometry contract (CAD v16 / spec v17).

    blender -b --factory-startup --python build_geeone_gate02_blockout.py -- --contract <json> --out <dir>

Deterministic bpy builder. Every mustBeGeometry detail of the surface-detail spec is tagged `# detail: UTS-Dxx`
so check_surface_detail_coverage.py can gate it. Units: mm, 2R = 85 mm user-authorized-provisional.
No Subdivision, no Shade Smooth: every facet is its own plane / triangle with hard creases.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Vector


# ============================================================ args / contract
def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-render", action="store_true")
    return p.parse_args(argv)


A = args()
C = json.loads(Path(A.contract).read_text(encoding="utf-8"))
S = C["scale"]["diameterMmProvisional"] / 2.0  # mm per R
T = C["body"]["thicknessToR"]
TOP = T / 2
CREST = C["body"]["crestRiseToR"]
CAP = C["capRadiusToR"]
BLADES = C["bladeAnglesDeg"]
LOOPS = C["loops"]
NTH = LOOPS["nTheta"]
ET = C["edgeTransition"]
PK = C["pocket"]
CP = C["cap"]
TWO_PI = 2 * math.pi


def r_of(table, theta):
    """Periodic linear interpolation of an r(theta) table."""
    t = np.asarray(theta) % TWO_PI
    idx = t / TWO_PI * NTH
    i0 = np.floor(idx).astype(int) % NTH
    i1 = (i0 + 1) % NTH
    f = idx - np.floor(idx)
    tb = np.asarray(table)
    return tb[i0] * (1 - f) + tb[i1] * f


def sector_of(theta):
    """Blade whose ±60° sector contains theta -> (blade angle deg)."""
    best, bd = None, 9.0
    for a in BLADES:
        d = abs((theta - math.radians(a) + math.pi) % TWO_PI - math.pi)
        if d < bd:
            bd, best = d, a
    return best


def to_local(x, y, blade_deg):
    a = math.radians(blade_deg)
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def top_z_R(x, y):
    """Blade-top height (R units) at world (x, y): min over the six planes of the containing blade's frame."""  # detail: UTS-D04
    theta = math.atan2(y, x)
    bl = sector_of(theta)
    lx, ly = to_local(x, y, bl)
    return min(p["a"] * lx + p["b"] * ly + p["c"] for p in C["topPlanes"]["planes"])


# ============================================================ facet angle grid along the outline
def outline_arclength_angles():
    """Angles of kite corners (pitch kitePitchToR along the outline) and their half-step midpoints."""
    th = np.linspace(0, TWO_PI, NTH, endpoint=False)
    r = np.asarray(LOOPS["outline"])
    x, y = r * np.cos(th), r * np.sin(th)
    seg = np.hypot(np.diff(x, append=x[0]), np.diff(y, append=y[0]))
    s = np.concatenate([[0.0], np.cumsum(seg)])  # length NTH+1
    L = ET["kitePitchToR"]
    n = int(round(s[-1] / L))
    L_eff = s[-1] / n  # closes the loop exactly
    corners = np.interp(np.arange(n) * L_eff, s, np.append(th, TWO_PI))
    mids = np.interp((np.arange(n) + 0.5) * L_eff, s, np.append(th, TWO_PI))
    return corners % TWO_PI, mids % TWO_PI


# ============================================================ polygon clipping (plateau facets)
def clip_halfplane(poly, a, b, c):
    """Keep the part of polygon `poly` where a x + b y + c >= 0 (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def poly_area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def world_plane(p, blade_deg):
    """Plane z = a lx + b ly + c in the blade frame -> world coefficients (A x + B y + c)."""
    a = math.radians(blade_deg)
    # lx = x cos a + y sin a ; ly = -x sin a + y cos a
    return (p["a"] * math.cos(a) - p["b"] * math.sin(a), p["a"] * math.sin(a) + p["b"] * math.cos(a), p["c"])


# ============================================================ mesh helpers
def new_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def offset_polygon(pts, d):
    """Offset a dense convex-ish polygon by d (positive outward) along vertex bisector normals (CCW input)."""
    out = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        tx, ty = x2 - x0, y2 - y0
        L = math.hypot(tx, ty) or 1.0
        nx, ny = ty / L, -tx / L  # outward normal for CCW
        out.append((x1 + d * nx, y1 + d * ny))
    return out


def ensure_ccw(pts):
    return pts if poly_area(pts) > 0 else list(reversed(pts))


# ============================================================ rotor body
def build_rotor():
    corners, mids = outline_arclength_angles()
    tip_angles = [math.radians(a) for a in BLADES]
    W = ET["bandWidthToR"]
    dropA = ET["tierAWidthToR"] * math.tan(math.radians(ET["tierASlopeDeg"]))
    k1, k2 = math.tan(math.radians(ET["kiteSlopeDeg"])), math.tan(math.radians(ET["lambdaSlopeDeg"]))
    fV, fL = ET["kiteTipBandFraction"], ET["lambdaTipBandFraction"]

    def zP(theta):  # plateau boundary height (world)
        r = float(r_of(LOOPS["plateau"], theta))
        return top_z_R(r * math.cos(theta), r * math.sin(theta))

    def zA(theta):  # tier-A outer edge
        return zP(theta) - dropA  # detail: UTS-D05

    def band_z(theta, f):
        """Two-slope band profile normalised so the Λ plane ends on the mid-plane (kite for f < 0.55, Λ beyond)."""  # detail: UTS-D05
        za = zA(theta)
        kk = za / (W * (k1 * 0.55 + k2 * 0.45))
        return za - kk * k1 * f * W if f < 0.55 else kk * k2 * (1 - f) * W

    # ---- vertex rings (angle-sorted), top half
    def ring(angles, r_fn, z_fn):
        out = []
        for th in sorted(set(float(a) for a in angles)):
            r = r_fn(th)
            out.append((th, r * math.cos(th), r * math.sin(th), z_fn(th)))
        return out

    # outline: Λ base corners at midpoints + exact tip vertices (sharp tips, D07)  # detail: UTS-D07, UTS-D06
    ring_out = ring(list(mids) + tip_angles, lambda th: float(r_of(LOOPS["outline"], th)), lambda th: 0.0)
    corners = np.array(sorted(set(list(map(float, corners)) + tip_angles)))
    # zigzag: Λ tips at corners (fraction fL), V tips at midpoints (fraction fV)
    zig = []
    for th in corners:
        rA, rO = float(r_of(LOOPS["tierA"], th)), float(r_of(LOOPS["outline"], th))
        r = rA + (rO - rA) * fL
        zig.append((float(th), r * math.cos(th), r * math.sin(th), band_z(th, fL)))
    for th in mids:
        rA, rO = float(r_of(LOOPS["tierA"], th)), float(r_of(LOOPS["outline"], th))
        r = rA + (rO - rA) * fV
        zig.append((float(th), r * math.cos(th), r * math.sin(th), band_z(th, fV)))
    zig.sort()
    ring_A = ring(list(corners), lambda th: float(r_of(LOOPS["tierA"], th)), zA)

    # ---- plateau facets: per blade sector, per plane region (exact planar n-gons)  # detail: UTS-D04
    plateau_pts = {}
    base_angles = sorted(set([float(a) for a in mids] + tip_angles))
    base_poly = [(float(r_of(LOOPS["plateau"], th)) * math.cos(th), float(r_of(LOOPS["plateau"], th)) * math.sin(th)) for th in base_angles]
    faces_plateau = []  # list of (poly2d, plane(a,b,c))
    for bl in BLADES:
        a0 = math.radians(bl - 60.0)
        a1 = math.radians(bl + 60.0)
        # sector wedge = half-planes: left of ray a0 rotated... keep points with cross(ray_a0, p) >= 0 and cross(ray_a1, p) <= 0
        sec = clip_halfplane(base_poly, -math.sin(a0), math.cos(a0), 0.0)
        sec = clip_halfplane(sec, math.sin(a1), -math.cos(a1), 0.0)
        planes = [world_plane(p, bl) for p in C["topPlanes"]["planes"]]
        for i, (ai, bi, ci) in enumerate(planes):
            reg = sec
            for j, (aj, bj, cj) in enumerate(planes):
                if j == i:
                    continue
                reg = clip_halfplane(reg, aj - ai, bj - bi, cj - ci)  # keep where plane_i <= plane_j
                if len(reg) < 3:
                    break
            if len(reg) >= 3 and abs(poly_area(reg)) > 1e-7:
                faces_plateau.append((reg, (ai, bi, ci)))
    # heal T-junctions: insert every vertex that lies on another polygon's edge, so shared creases / sector lines match exactly
    all_pts = {}
    for reg, _ in faces_plateau:
        for pt in reg:
            all_pts[(round(pt[0], 7), round(pt[1], 7))] = pt
    all_list = list(all_pts.values())

    def heal(poly):
        out = []
        n = len(poly)
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            out.append(poly[i])
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            if L2 < 1e-14:
                continue
            ins = []
            for px, py in all_list:
                t = ((px - x0) * dx + (py - y0) * dy) / L2
                if 1e-6 < t < 1 - 1e-6 and math.hypot(px - (x0 + t * dx), py - (y0 + t * dy)) < 1e-6:
                    ins.append((t, (px, py)))
            out.extend(pt for _, pt in sorted(ins))
        return out

    faces_plateau = [(heal(reg), pl) for reg, pl in faces_plateau]
    # boundary vertices of the plateau loop actually used by the facets (original samples + inserted crease/sector hits)
    def on_loop(pt):
        """True if pt lies on the plateau base polygon (its chords), i.e. it is a boundary vertex of the plateau region."""
        n = len(base_poly)
        for i in range(n):
            (x0, y0), (x1, y1) = base_poly[i], base_poly[(i + 1) % n]
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy
            t = max(0.0, min(1.0, ((pt[0] - x0) * dx + (pt[1] - y0) * dy) / L2))
            if math.hypot(pt[0] - (x0 + t * dx), pt[1] - (y0 + t * dy)) < 1e-6:
                return True
        return False
    loop_pts = {}
    for reg, pl in faces_plateau:
        for pt in reg:
            if on_loop(pt):
                th = math.atan2(pt[1], pt[0]) % TWO_PI
                loop_pts[round(th, 7)] = (th, pt[0], pt[1], pl[0] * pt[0] + pl[1] * pt[1] + pl[2])
    ring_P = sorted(loop_pts.values())

    # ---- build bmesh (top half), then mirror
    bm = bmesh.new()
    vcache = {}

    def V(x, y, z):
        key = (round(x, 6), round(y, 6), round(z, 6))
        if key not in vcache:
            vcache[key] = bm.verts.new((x * S, y * S, z * S))
        return vcache[key]

    def zipper(inner, outer, flip=False):
        """Stitch two angle-sorted rings (th, x, y, z) into triangles."""
        ni, no = len(inner), len(outer)
        i = j = 0
        # start both at the smallest angle; walk around once
        ci = [(*inner[k],) for k in range(ni)]
        co = [(*outer[k],) for k in range(no)]
        # extend cyclically
        ci.append((ci[0][0] + TWO_PI, *ci[0][1:]))
        co.append((co[0][0] + TWO_PI, *co[0][1:]))
        while i < ni or j < no:
            adv_inner = (j >= no) or (i < ni and ci[i + 1][0] <= co[j + 1][0])
            if adv_inner:
                tri = (ci[i], ci[i + 1], co[j])
                i += 1
            else:
                tri = (co[j], ci[i], co[j + 1])
                j += 1
            vs = [V(p[1], p[2], p[3]) for p in tri]
            if flip:
                vs.reverse()
            try:
                if len({id(v) for v in vs}) == 3:
                    bm.faces.new(vs)
            except ValueError:
                pass

    for sign, flip in ((1.0, False), (-1.0, True)):  # detail: UTS-D10
        def mz(ring_):
            return [(th, x, y, sign * z) for th, x, y, z in ring_]
        zipper(mz(zig), mz(ring_out), flip)  # Λ facets (base on the mid-plane)
        zipper(mz(ring_A), mz(zig), flip)  # kites (base on the tier-A edge)
        zipper(mz(ring_P), mz(ring_A), flip)  # tier A large facets
        n_fail = 0
        for reg, (a, b, c) in faces_plateau:
            vs = []
            for x, y in ensure_ccw(reg):
                v = V(x, y, sign * (a * x + b * y + c))
                if v not in vs:  # drop repeated vertices (healing can insert a point that rounds onto an existing one)
                    vs.append(v)
            if flip:
                vs.reverse()
            if len(vs) < 3:
                continue
            try:
                bm.faces.new(vs)
            except ValueError as exc:
                n_fail += 1
                print("[dbg] plateau face failed:", exc, "nverts", len(vs))
        if n_fail:
            print("[r006] WARNING plateau faces failed:", n_fail, "of", len(faces_plateau))
    nonman_base = sum(1 for e in bm.edges if len(e.link_faces) != 2)
    print("[r006] base surface: verts %d faces %d non-manifold edges %d (plateau facets %d, kites %d)" % (len(bm.verts), len(bm.faces), nonman_base, len(faces_plateau), len(corners)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    body = new_object("Rotor_Body", bm)
    return body


# ============================================================ cutters
def cylinder_cutter(name, r, z0, z1, seg=96):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=(z1 - z0))
    for v in bm.verts:
        v.co.z += (z0 + z1) / 2
    ob = new_object(name, bm)
    ob.display_type = "WIRE"
    ob.hide_render = True
    return ob


def pocket_cutter(name, blade_deg, sign):
    """Funnel pocket: rounded floor -> concave floor fillet (arc loops) -> planar sloped wall (open toward the cap) -> above the top."""  # detail: UTS-D08
    depth = PK["depthFractionOfThicknessPerSide"] * T
    run = PK["mouthOffsetToR"] + PK["floorOffsetToR"]
    r2 = PK["edgeFilletFloorToR"]
    phi = math.atan2(depth, run)
    t2 = r2 * math.tan(phi / 2)
    floor = ensure_ccw([tuple(p) for p in PK["floor"]])
    z_f = TOP - depth
    loops = []  # (offset from floor polygon outward, z)
    for a in np.linspace(0.0, phi, 5):
        u_c, z_c = run + t2, z_f + r2  # fillet centre in (u from mouth, z)
        u = u_c - r2 * math.sin(a)
        z = z_c - r2 * math.cos(a)
        loops.append((run - u, z))  # offset outward from the floor polygon = run - u
    z_top_cut = TOP + CREST + 0.08
    u_top = run - (z_top_cut - z_f) * run / depth
    loops.append((run - u_top, z_top_cut))
    bm = bmesh.new()
    rings = []
    a = math.radians(blade_deg)
    for off, z in loops:
        pts = offset_polygon(floor, off)
        ring_v = []
        for x, y in pts:
            wx, wy = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
            ring_v.append(bm.verts.new((wx * S, wy * S, sign * z * S)))
        rings.append(ring_v)
    n = len(rings[0])
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    for lo, hi in zip(rings[:-1], rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    ob = new_object(name, bm)
    ob.display_type = "WIRE"
    ob.hide_render = True
    return ob


def boolean(target, tool, name):
    m = target.modifiers.new(name, "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = tool
    m.solver = "MANIFOLD"
    return m


# ============================================================ caps
def build_cap(name, sign):
    """Static cap: 14-sector concave dish (D01) -> crown 14 wedges / 28 triangles (D02) -> two skirt rows + vertical 14-gon side (D03) -> seat."""
    N = CP["sectors"]
    Rc = CP["radiusToR"]
    r_table = CP["tableToCap"] * Rc
    z_rim = TOP + CP["sideHeightToR"]
    dish = r_table * math.tan(math.radians(CP["dishSlopeDeg"]))
    bm = bmesh.new()
    centre = bm.verts.new((0.0, 0.0, sign * (z_rim - dish) * S))
    rim = [bm.verts.new((r_table * math.cos(TWO_PI * j / N) * S, r_table * math.sin(TWO_PI * j / N) * S, sign * z_rim * S)) for j in range(N)]
    for j in range(N):  # detail: UTS-D01
        bm.faces.new((centre, rim[j], rim[(j + 1) % N]))
    # tiers: crown (staggered zigzag), skirt row 1 (staggered), skirt row 2 (staggered)
    tiers = CP["tiers"]
    prev_ring, prev_r, prev_z = rim, r_table, z_rim
    prev_phase = 0.0
    for k, tier in enumerate(tiers):  # detail: UTS-D02, UTS-D03
        r_next = prev_r + tier["radialToCap"] * Rc
        z_next = prev_z - tier["radialToCap"] * Rc * math.tan(math.radians(tier["slopeDeg"]))
        phase = prev_phase + 0.5
        ring_next = [bm.verts.new((r_next * math.cos(TWO_PI * (j + phase) / N) * S, r_next * math.sin(TWO_PI * (j + phase) / N) * S, sign * z_next * S)) for j in range(N)]
        for j in range(N):
            j1 = (j + 1) % N
            bm.faces.new((prev_ring[j], prev_ring[j1], ring_next[j]))  # tip pointing outward
            bm.faces.new((prev_ring[j1], ring_next[j1], ring_next[j]))  # tip pointing inward
        prev_ring, prev_r, prev_z, prev_phase = ring_next, r_next, z_next, phase
    # vertical 14-gon side down to the seat  # detail: UTS-D03
    z_seat = prev_z - CP["verticalSideToR"]
    base = [bm.verts.new((prev_r * math.cos(TWO_PI * (j + prev_phase) / N) * S, prev_r * math.sin(TWO_PI * (j + prev_phase) / N) * S, sign * z_seat * S)) for j in range(N)]
    for j in range(N):
        j1 = (j + 1) % N
        bm.faces.new((prev_ring[j], prev_ring[j1], base[j1], base[j]))
    bm.faces.new(list(reversed(base)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sign < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    ob = new_object(name, bm)
    return ob, z_seat


def build_seam(z_seat_top):
    """Dark seam ring between the cap seat and the blade roots, visible in the notches."""  # detail: UTS-D09
    Rc = CP["radiusToR"]
    g = CP["seamGapToR"]
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=(Rc + g) * S, radius2=(Rc + g) * S, depth=T * S * 1.02)
    ob = new_object("Seam_Dark", bm)
    return ob


# ============================================================ materials / render
def mat(name, rgb, rough=0.35, metallic=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    return m


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def render_workbench(out_dir: Path, body_top_mm: float):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = 1600
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "SINGLE"
    sh.single_color = (0.75, 0.75, 0.75)
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_shadows = False
    sh.show_object_outline = True
    scene.display.render_aa = "8"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.18, 0.18, 0.18)
    cam = bpy.data.objects.new("ReviewCam", bpy.data.cameras.new("ReviewCam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    R = S
    views = {
        "top-ortho": ((0, 0, 300), (0, 0, body_top_mm), 2.3 * R, None),
        "bottom-ortho": ((0, 0, -300), (0, 0, -body_top_mm), 2.3 * R, None),
        "hero": ((1.2 * R, -1.6 * R, 1.5 * R), (0, 0, 0.3 * body_top_mm), None, 50.0),
        "left-oblique": ((-1.9 * R, -1.1 * R, 1.1 * R), (0, 0, 0), None, 50.0),
        "right-oblique": ((1.9 * R, -1.1 * R, 1.1 * R), (0, 0, 0), None, 50.0),
        "low": ((0.3 * R, -2.6 * R, 0.45 * R), (0, 0, 0.1 * body_top_mm), None, 60.0),
        "blade-macro-f0132": ((0.0, -0.15 * R, 1.35 * R), (0.0, 0.62 * R, body_top_mm * 0.9), None, 70.0),
        "edge-macro": ((1.3 * R, -0.9 * R, 0.55 * R), (0.55 * R, -0.35 * R, body_top_mm * 0.6), None, 85.0),
        "cap-macro": ((0.75 * R, -1.15 * R, 0.62 * R), (0.12 * R, -0.05 * R, body_top_mm * 1.6), None, 85.0),
        "notch-macro": ((0.9 * R, 0.55 * R, 0.75 * R), (0.42 * R, 0.24 * R, body_top_mm * 0.8), None, 85.0),
    }
    for name, (loc, tgt, ortho, lens) in views.items():
        cam.location = Vector(loc)
        look_at(cam, tgt)
        cam.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            cam.data.ortho_scale = ortho
        else:
            cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 2000
        scene.render.filepath = str(out_dir / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", name)


def main():
    out = Path(A.out)
    out.mkdir(parents=True, exist_ok=True)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001
    scene.unit_settings.length_unit = "MILLIMETERS"

    body = build_rotor()
    # hub flattened to ±T/2 under the caps (cap seat); pockets open into this cut  # detail: UTS-D09
    seat_top = cylinder_cutter("Cut_CapSeat_Top", CAP * S, TOP * S, (TOP + 0.5) * S)
    seat_bot = cylinder_cutter("Cut_CapSeat_Bottom", CAP * S, -(TOP + 0.5) * S, -TOP * S)
    boolean(body, seat_top, "Bool_CapSeat_Top")
    boolean(body, seat_bot, "Bool_CapSeat_Bottom")
    for i, bl in enumerate(BLADES):
        for sign, tag in ((1.0, "T"), (-1.0, "B")):  # detail: UTS-D08, UTS-D10
            cut = pocket_cutter(f"Cut_Pocket_{tag}_{i}", bl, sign)
            boolean(body, cut, f"Bool_Pocket_{tag}_{i}")
    steel = mat("M_Steel_Satin", (0.78, 0.79, 0.80), 0.35)
    dark = mat("M_Seam_Dark", (0.02, 0.02, 0.02), 0.6)
    body.data.materials.append(steel)
    cap_t, z_seat = build_cap("Cap_Top", 1.0)
    cap_b, _ = build_cap("Cap_Bottom", -1.0)  # detail: UTS-D10
    for c in (cap_t, cap_b):
        c.data.materials.append(steel)
    seam = build_seam(z_seat)
    seam.data.materials.append(dark)

    # evaluated self-check
    dg = bpy.context.evaluated_depsgraph_get()
    me = body.evaluated_get(dg).to_mesh()
    bmc = bmesh.new()
    bmc.from_mesh(me)
    nonman = sum(1 for e in bmc.edges if not e.is_manifold)
    zmax = max(v.co.z for v in me.vertices) / S
    n_v, n_f = len(me.vertices), len(me.polygons)
    bmc.free()
    body.evaluated_get(dg).to_mesh_clear()
    print("[r006] scale 2R = %.1f mm (provisional) · body t %.2f R = %.2f mm · crest %.3f R · cap R %.3f R" % (2 * S, T, T * S, CREST, CAP))
    print("[r006] rotor evaluated: verts %d faces %d non-manifold edges %d zmax %.4f R (crest %.4f)" % (n_v, n_f, nonman, zmax, TOP + CREST))
    print("[r006] edge: transition %.2f R = tierA %.2f R @%d° + kite/Λ band %.2f R (%d°/%d°, tips %.0f%%/%.0f%%), pitch %.2f R" % (ET["transitionWidthToR"], ET["tierAWidthToR"], ET["tierASlopeDeg"], ET["bandWidthToR"], ET["kiteSlopeDeg"], ET["lambdaSlopeDeg"], ET["lambdaTipBandFraction"] * 100, ET["kiteTipBandFraction"] * 100, ET["kitePitchToR"]))
    print("[r006] pocket: funnel mouth +%.2f / floor -%.2f R, depth %.0f%% t, floor fillet R%.2f (mouth convex fillet deferred to Gate 06 edge bevel)" % (PK["mouthOffsetToR"], PK["floorOffsetToR"], PK["depthFractionOfThicknessPerSide"] * 100, PK["edgeFilletFloorToR"]))
    print("[r006] cap: table %.2f, %d sectors dish %.0f°, crown %d wedges, skirt %d×2, side %.3f R, seat z %.3f R (body top %.3f)" % (CP["tableToCap"], CP["sectors"], CP["dishSlopeDeg"], CP["wedges"], CP["skirtFacets"], CP["verticalSideToR"], z_seat, TOP))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "geeone-blockout-r006.blend"))
    if not A.no_render:
        render_workbench(out / "checks", TOP * S)
        bpy.ops.wm.save_as_mainfile(filepath=str(out / "geeone-blockout-r006.blend"))


main()
