"""Gate 06 geometry rev-007 · GEEONE 龙鳞三叶 · finalize the approved blockout rev-007.
rev-006 (user 2026-09-07 19:42 '切分成 14 片的细节丢了…应向内凹一点'): caps rebuilt with dish 5° and alternate sectors tilted ±0.5°
so the 14 pizza slices read in the render; creases stay sharp (crease bevel disabled: it would hide a 2° crease).  # detail: UTS-D01
rev-007 (user 2026-09-07 22:51 'bevel 可以再厚一点…这两片龙鳞的高度可以再高…内凹的效果还是不够明显'): contract v20 — dish 8°, disc 0.80 cap,
skirt rows 0.07 cap @50° / 0.04 cap @72° (crown 0.09 @18°), cap side 0.16 R; the cap lip therefore moves to TOP + 0.0456 R, so the
hub seats are rebuilt from the contract too (Hub_Seat_Top/Bottom: cylinder r = hubSeatRadiusToR, TOP -> lip).  # detail: UTS-D02, UTS-D03, UTS-D09

    blender -b <geeone-blockout-r007.blend> --python finalize_geeone_geometry.py -- --contract <json> --out <dir>

Steps (all deterministic, no Subdivision / Shade Smooth):
  1. apply the boolean stack of Rotor_Body (cap seats + 6 funnel pockets) -> real mesh
  2. pocket mouth convex fillet (deferred from Gate 05): tag the mouth edges by distance to the contract's mouth outline,
     Bevel (weight) R = edgeFilletTopToR, 6 segments  # detail: UTS-D08
  3. micro-bevel on remaining sharp creases (> 40°): 0.15 mm, 2 segments — the thin highlight line on hard edges;
     the facet creases themselves stay planar-to-planar (angle differences < 40° are untouched)  # detail: UTS-D04, UTS-D05
  4. run the spec's gate06Check rules that can be checked numerically -> gate06-checks.json
  5. save geeone-geometry-r007.blend + Workbench check renders
Detail tags for coverage: UTS-D01 UTS-D02 UTS-D03 UTS-D06 UTS-D07 UTS-D09 UTS-D10 are carried by the blockout builder that
produced this .blend (build_geeone_gate02_blockout.py rev-007); this script only finalizes.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


A = args()
C = json.loads(Path(A.contract).read_text(encoding="utf-8"))
S = C["scale"]["diameterMmProvisional"] / 2.0
T = C["body"]["thicknessToR"]
TOP = T / 2
CAP = C["capRadiusToR"]
BLADES = C["bladeAnglesDeg"]
PK = C["pocket"]
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "checks").mkdir(exist_ok=True)


def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    return me


def mouth_outline_world(blade_deg, sign):
    a = math.radians(blade_deg)
    pts = []
    for x, y in PK["mouth"]:
        pts.append(Vector((x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))) * S)
    return pts


def dist_to_polyline(p, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ab = b - a
        L2 = ab.length_squared
        t = max(0.0, min(1.0, (p - a).dot(ab) / L2)) if L2 > 1e-12 else 0.0
        d = (p - (a + ab * t)).length
        if d < best:
            best = d
    return best


def tag_mouth_edges(ob):
    """Edges whose both ends lie on a pocket mouth outline (top or bottom) and above/below the funnel wall get bevel weight 1."""  # detail: UTS-D08
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    layer = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    outlines = [(mouth_outline_world(bl, s), s) for bl in BLADES for s in (1.0, -1.0)]
    tol = 0.004 * S  # 0.17 mm at 85 mm
    tagged = 0
    for e in bm.edges:
        e[layer] = 0.0
        ok = True
        for v in e.verts:
            p = Vector((v.co.x, v.co.y))
            zs = math.copysign(1.0, v.co.z)
            hit = any(dist_to_polyline(p, o) < tol for o, s in outlines if s == zs)
            if not hit or abs(v.co.z) < TOP * S * 0.9:
                ok = False
                break
        if ok:
            e[layer] = 1.0
            tagged += 1
    bm.to_mesh(me)
    bm.free()
    me.update()
    return tagged


def add_bevel(ob, name, width_mm, segments, limit, angle_deg=None, profile=0.5):
    m = ob.modifiers.new(name, "BEVEL")
    m.width = width_mm
    m.segments = segments
    m.limit_method = limit
    m.profile = profile
    if angle_deg is not None:
        m.angle_limit = math.radians(angle_deg)
    m.miter_outer = "MITER_ARC"
    m.harden_normals = False
    return m


# ---------------------------------------------------------------- gate06 checks
def face_planarity(me):
    worst = 0.0
    for p in me.polygons:
        if len(p.vertices) <= 3:
            continue
        n = p.normal
        c = p.center
        for vi in p.vertices:
            d = abs((me.vertices[vi].co - c).dot(n))
            worst = max(worst, d)
    return worst / S  # in R


def local_minima_on_top(me, bm_edges_adj):
    """Vertices on the blade top faces (z > TOP + 1e-4 R) that are lower than all their neighbours (valleys)."""
    cnt = 0
    for v, nbrs in bm_edges_adj.items():
        if v.co.z / S <= TOP + 1e-4:
            continue
        if all(nv.co.z > v.co.z + 1e-6 for nv in nbrs) and len(nbrs) >= 3:
            cnt += 1
    return cnt


def mirror_symmetry(me):
    pts = {}
    for v in me.vertices:
        pts.setdefault((round(v.co.x, 2), round(v.co.y, 2), round(abs(v.co.z), 2)), []).append(math.copysign(1, v.co.z) if abs(v.co.z) > 1e-4 else 0)
    unmatched = sum(1 for k, s in pts.items() if k[2] > 0.01 and (1 not in s or -1 not in s))
    return unmatched, len(pts)


def look_at(cam, target):
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def render_checks(body_top_mm):
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
    cam = bpy.data.objects.get("ReviewCam") or bpy.data.objects.new("ReviewCam", bpy.data.cameras.new("ReviewCam"))
    if cam.name not in scene.collection.objects:
        scene.collection.objects.link(cam)
    scene.camera = cam
    R = S
    views = {
        "top-ortho": ((0, 0, 300), (0, 0, body_top_mm), 2.3 * R, None),
        "hero": ((1.2 * R, -1.6 * R, 1.5 * R), (0, 0, 0.3 * body_top_mm), None, 50.0),
        "pocket-macro": ((0.0, -0.15 * R, 1.35 * R), (0.0, 0.62 * R, body_top_mm * 0.9), None, 70.0),
        "edge-macro": ((1.3 * R, -0.9 * R, 0.55 * R), (0.55 * R, -0.35 * R, body_top_mm * 0.6), None, 85.0),
        "notch-macro": ((0.9 * R, 0.55 * R, 0.75 * R), (0.42 * R, 0.24 * R, body_top_mm * 0.8), None, 85.0),
        "low": ((0.3 * R, -2.6 * R, 0.45 * R), (0, 0, 0.1 * body_top_mm), None, 60.0),
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
        scene.render.filepath = str(OUT / "checks" / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("[render]", name)


def rebuild_cap(name, sign):
    """Cap with a visibly concave 14-slice dish (D01): 14 planar sectors from a lowered centre apex to a 14-gon rim.
    Alternate sectors are tilted ±alt about their bisector: rim vertex j sits at z_rim + sgn_j·d with sgn alternating, so every
    sector has one raised and one lowered rim vertex (tilt = alt) and neighbours tilt the opposite way -> hard creases whose two
    sides differ in normal, visible under a soft key light. Crown / skirt tiers grow straight from that zigzag rim (no separate
    level ring, which is what left the 28-edge hole in the first rev-006 pass). Creases stay sharp: a bevel would spread a 2°
    crease over 0.12 mm and hide it, so sectorCreaseHighlightBevelMm is only honoured when > 0."""  # detail: UTS-D01, UTS-D02, UTS-D03
    CP = C["cap"]
    N = CP["sectors"]
    assert N % 2 == 0, "alternating sector tilt needs an even sector count"
    Rc = CP["radiusToR"]
    r_table = CP["tableToCap"] * Rc
    z_rim = TOP + CP["sideHeightToR"]
    dish = r_table * math.tan(math.radians(CP["dishSlopeDeg"]))
    alt = math.radians(CP.get("sectorAltTiltDeg", 0.0))
    d = r_table * math.sin(math.pi / N) * math.tan(alt)  # rim half-offset that tilts a sector by exactly alt about its bisector
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    bm = bmesh.new()
    TWO_PI = 2 * math.pi
    apex = bm.verts.new((0.0, 0.0, sign * (z_rim - dish) * S))
    rim = []
    for j in range(N):
        sgn = 1.0 if j % 2 == 0 else -1.0
        rim.append(bm.verts.new((r_table * math.cos(TWO_PI * j / N) * S, r_table * math.sin(TWO_PI * j / N) * S, sign * (z_rim + sgn * d) * S)))
    for j in range(N):
        bm.faces.new((apex, rim[j], rim[(j + 1) % N]))
    prev_ring, prev_r, prev_z, prev_phase = rim, r_table, z_rim, 0.0
    for tier in CP["tiers"]:
        r_next = prev_r + tier["radialToCap"] * Rc
        z_next = prev_z - tier["radialToCap"] * Rc * math.tan(math.radians(tier["slopeDeg"]))
        phase = prev_phase + 0.5
        ring_next = [bm.verts.new((r_next * math.cos(TWO_PI * (j + phase) / N) * S, r_next * math.sin(TWO_PI * (j + phase) / N) * S, sign * z_next * S)) for j in range(N)]
        for j in range(N):
            j1 = (j + 1) % N
            bm.faces.new((prev_ring[j], prev_ring[j1], ring_next[j]))
            bm.faces.new((prev_ring[j1], ring_next[j1], ring_next[j]))
        prev_ring, prev_r, prev_z, prev_phase = ring_next, r_next, z_next, phase
    bm.faces.new(list(reversed(prev_ring)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if sign < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    layer = bm.edges.layers.float.new("bevel_weight_edge")
    n_tag = 0
    for e in bm.edges:
        if apex in e.verts:
            e[layer] = 1.0
            n_tag += 1
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    crease_bevel = float(CP.get("sectorCreaseHighlightBevelMm", 0.0) or 0.0)
    if crease_bevel > 0:
        bev = ob.modifiers.new("G6_SectorCreaseHighlight", "BEVEL")
        bev.width = crease_bevel
        bev.segments = 2
        bev.limit_method = "WEIGHT"
    print("[g06] %s: verts %d faces %d non-manifold %d, rim zigzag ±%.4f mm, crease bevel %.2f mm" % (name, len(me.vertices), len(me.polygons), nonman, d * S, crease_bevel))
    return ob, n_tag, dish, nonman


def rebuild_hub_seat(sign):
    """Recessed rotating hub / bearing seat between the rotor top and the overhanging cap lip; height follows the contract
    (sideHeightToR − tiers drop) so it stays consistent with the rebuilt cap."""  # detail: UTS-D09, UTS-D03
    CP = C["cap"]
    name = "Hub_Seat_Top" if sign > 0 else "Hub_Seat_Bottom"
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    r = CP["hubSeatRadiusToR"]
    Rc = CP["radiusToR"]
    drop = sum(t["radialToCap"] * Rc * math.tan(math.radians(t["slopeDeg"])) for t in CP["tiers"])
    z0, z1 = TOP, TOP + CP["sideHeightToR"] - drop
    assert z1 > z0 + 1e-6, "cap lip must stay above the rotor top (tiers drop exceeds the cap side height)"
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=r * S, radius2=r * S, depth=(z1 - z0) * S)
    for v in bm.verts:
        v.co.z += sign * (z0 + z1) / 2 * S
    if sign < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    print("[g06] %s rebuilt: r %.3f R, height %.4f R = %.2f mm (lip at TOP + %.4f R)" % (name, r, z1 - z0, (z1 - z0) * S, z1 - z0))
    return ob, z1 - z0


def main():
    body = bpy.data.objects["Rotor_Body"]
    me = apply_modifiers(body)
    for o in list(bpy.data.objects):
        if o.name.startswith("Cut_"):
            bpy.data.objects.remove(o, do_unlink=True)
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    adj = {v: [e.other_vert(v) for e in v.link_edges] for v in bm.verts}
    minima = local_minima_on_top(me, adj)
    bm.free()
    planarity = face_planarity(me)
    unmatched, n_xyz = mirror_symmetry(me)
    tagged = tag_mouth_edges(body)
    add_bevel(body, "G6_PocketMouthFillet", PK["edgeFilletTopToR"] * S, 6, "WEIGHT")  # detail: UTS-D08
    add_bevel(body, "G6_EdgeBreak", 0.15, 2, "ANGLE", 40.0)  # detail: UTS-D04, UTS-D05
    cap_t, n_tag, dish, cap_nonman_t = rebuild_cap("Cap_Top", 1.0)
    cap_b, _, _, cap_nonman_b = rebuild_cap("Cap_Bottom", -1.0)  # detail: UTS-D10
    _, hub_h = rebuild_hub_seat(1.0)
    rebuild_hub_seat(-1.0)
    Rc = C["cap"]["radiusToR"]
    tier_drops = [round(t["radialToCap"] * Rc * math.tan(math.radians(t["slopeDeg"])), 4) for t in C["cap"]["tiers"]]
    print("[g06] caps rebuilt: dish %.0f° depth %.4f R = %.2f mm, alt tilt ±%.1f°, %d radial creases tagged (%.2f mm highlight bevel)" % (C["cap"]["dishSlopeDeg"], dish, dish * S, C["cap"].get("sectorAltTiltDeg", 0.0), n_tag, C["cap"].get("sectorCreaseHighlightBevelMm", 0.12)))
    for name in ("Cap_Top", "Cap_Bottom", "Hub_Seat_Top", "Hub_Seat_Bottom"):
        ob = bpy.data.objects.get(name)
        if ob is not None:
            add_bevel(ob, "G6_EdgeBreak", 0.15, 2, "ANGLE", 40.0)  # detail: UTS-D01, UTS-D02, UTS-D03
    # evaluated result
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    bm2 = bmesh.new()
    bm2.from_mesh(ev)
    nonman_final = sum(1 for e in bm2.edges if not e.is_manifold)
    bm2.free()
    cap = bpy.data.objects["Cap_Top"].data
    sectors = sum(1 for p in cap.polygons if len(p.vertices) == 3 and any(abs(cap.vertices[vi].co.x) < 1e-6 and abs(cap.vertices[vi].co.y) < 1e-6 for vi in p.vertices) and all(math.hypot(cap.vertices[vi].co.x, cap.vertices[vi].co.y) < C["cap"]["tableToCap"] * CAP * S * 1.01 for vi in p.vertices))
    checks = {
        "source": {"blockout": "05-blockout/rev-007/geeone-blockout-r007.blend", "contract": str(Path(A.contract).name)},
        "rotor_after_booleans": {"verts": len(me.vertices), "faces": len(me.polygons), "non_manifold_edges": nonman, "max_face_planarity_dev_R": round(planarity, 6), "top_local_minima": minima, "mirror_unmatched_xyz_of": [unmatched, n_xyz]},
        "pocket_mouth_fillet": {"tagged_edges": tagged, "radius_R": PK["edgeFilletTopToR"], "radius_mm": round(PK["edgeFilletTopToR"] * S, 3), "segments": 6},
        "edge_break": {"width_mm": 0.15, "segments": 2, "angle_limit_deg": 40},
        "rotor_final": {"verts": len(ev.vertices), "faces": len(ev.polygons), "non_manifold_edges": nonman_final},
        "cap": {"dish_sectors": sectors, "expected": C["cap"]["sectors"], "rim_R": CAP, "hub_seat_R": C["cap"]["hubSeatRadiusToR"], "rim_gt_hub": CAP > C["cap"]["hubSeatRadiusToR"],
                "dish_slope_deg": C["cap"]["dishSlopeDeg"], "dish_depth_mm": round(dish * S, 3), "sector_alt_tilt_deg": C["cap"].get("sectorAltTiltDeg", 0.0),
                "radial_creases": n_tag, "crease_bevel_mm": C["cap"].get("sectorCreaseHighlightBevelMm", 0.0), "non_manifold_edges": [cap_nonman_t, cap_nonman_b],
                "table_to_cap": C["cap"]["tableToCap"], "side_height_R": C["cap"]["sideHeightToR"], "tier_drops_R": tier_drops, "tiers_drop_R": round(sum(tier_drops), 4),
                "skirt_rows_drop_mm": round((tier_drops[1] + tier_drops[2]) * S, 2), "hub_seat_height_R": round(hub_h, 4), "hub_seat_height_mm": round(hub_h * S, 2)},
        "gate06Check_results": {
            "D04 top convex, no valley": minima == 0,
            "D04/D05 planar facets (dev < 1e-4 R)": planarity < 1e-4,
            "D08 mouth fillet applied": tagged > 0,
            "D10 mirror": unmatched == 0,
            "D01 14 sectors": sectors == C["cap"]["sectors"],
            "D01 dish visibly concave (>= 4 deg)": C["cap"]["dishSlopeDeg"] >= 4.0,
            "D03 cap rim > hub seat": CAP > C["cap"]["hubSeatRadiusToR"],
            "manifold after fillets": nonman_final == 0,
            "D01 caps manifold": cap_nonman_t == 0 and cap_nonman_b == 0,
            "D02/D03 each tier steeper than the one above": all(C["cap"]["tiers"][i]["slopeDeg"] < C["cap"]["tiers"][i + 1]["slopeDeg"] for i in range(len(C["cap"]["tiers"]) - 1)),
            "D03 tiers drop <= cap side height (lip above rotor top)": hub_h > 0,
        },
    }
    (OUT / "gate06-checks.json").write_text(json.dumps(checks, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[g06]", json.dumps(checks["gate06Check_results"], ensure_ascii=False))
    print("[g06] rotor", checks["rotor_after_booleans"], "final", checks["rotor_final"], "mouth edges tagged", tagged)
    bpy.data.meshes.remove(ev)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "geeone-geometry-r007.blend"))
    render_checks(TOP * S)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "geeone-geometry-r007.blend"))


main()
