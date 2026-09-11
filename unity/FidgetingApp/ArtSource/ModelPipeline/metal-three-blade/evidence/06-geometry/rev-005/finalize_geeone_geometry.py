"""Gate 06 geometry rev-005 · GEEONE 龙鳞三叶 · finalize the approved blockout rev-007.

    blender -b <geeone-blockout-r007.blend> --python finalize_geeone_geometry.py -- --contract <json> --out <dir>

Steps (all deterministic, no Subdivision / Shade Smooth):
  1. apply the boolean stack of Rotor_Body (cap seats + 6 funnel pockets) -> real mesh
  2. pocket mouth convex fillet (deferred from Gate 05): tag the mouth edges by distance to the contract's mouth outline,
     Bevel (weight) R = edgeFilletTopToR, 6 segments  # detail: UTS-D08
  3. micro-bevel on remaining sharp creases (> 40°): 0.15 mm, 2 segments — the thin highlight line on hard edges;
     the facet creases themselves stay planar-to-planar (angle differences < 40° are untouched)  # detail: UTS-D04, UTS-D05
  4. run the spec's gate06Check rules that can be checked numerically -> gate06-checks.json
  5. save geeone-geometry-r005.blend + Workbench check renders
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
    sectors = sum(1 for p in cap.polygons if len(p.vertices) == 3 and any(abs(cap.vertices[vi].co.x) < 1e-6 and abs(cap.vertices[vi].co.y) < 1e-6 for vi in p.vertices))
    checks = {
        "source": {"blockout": "05-blockout/rev-007/geeone-blockout-r007.blend", "contract": str(Path(A.contract).name)},
        "rotor_after_booleans": {"verts": len(me.vertices), "faces": len(me.polygons), "non_manifold_edges": nonman, "max_face_planarity_dev_R": round(planarity, 6), "top_local_minima": minima, "mirror_unmatched_xyz_of": [unmatched, n_xyz]},
        "pocket_mouth_fillet": {"tagged_edges": tagged, "radius_R": PK["edgeFilletTopToR"], "radius_mm": round(PK["edgeFilletTopToR"] * S, 3), "segments": 6},
        "edge_break": {"width_mm": 0.15, "segments": 2, "angle_limit_deg": 40},
        "rotor_final": {"verts": len(ev.vertices), "faces": len(ev.polygons), "non_manifold_edges": nonman_final},
        "cap": {"dish_sectors": sectors, "expected": C["cap"]["sectors"], "rim_R": CAP, "hub_seat_R": C["cap"]["hubSeatRadiusToR"], "rim_gt_hub": CAP > C["cap"]["hubSeatRadiusToR"]},
        "gate06Check_results": {
            "D04 top convex, no valley": minima == 0,
            "D04/D05 planar facets (dev < 1e-4 R)": planarity < 1e-4,
            "D08 mouth fillet applied": tagged > 0,
            "D10 mirror": unmatched == 0,
            "D01 14 sectors": sectors == C["cap"]["sectors"],
            "D03 cap rim > hub seat": CAP > C["cap"]["hubSeatRadiusToR"],
            "manifold after fillets": nonman_final == 0,
        },
    }
    (OUT / "gate06-checks.json").write_text(json.dumps(checks, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[g06]", json.dumps(checks["gate06Check_results"], ensure_ascii=False))
    print("[g06] rotor", checks["rotor_after_booleans"], "final", checks["rotor_final"], "mouth edges tagged", tagged)
    bpy.data.meshes.remove(ev)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "geeone-geometry-r005.blend"))
    render_checks(TOP * S)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "geeone-geometry-r005.blend"))


main()
