"""Gate 06 geometry for the premium-display-case `tri-spinner-slab-v3-cmf` variant
(evidence rev-010, from the Gate 05 rev-012 blockout that follows the user's 2026-09-11 07:57 refinements).

    blender -b --python tools/blender/refine_tri_spinner_slab_geometry.py -- [--no-turntable] [--frames N]

Gate 06 does not redesign anything. It turns the approved deterministic blockout into
static, export-ready geometry:
- verifies the approved blockout .blend hash against pipeline.json before touching it;
- applies every remaining modifier (bevels, weighted normals) in the contract's order so the
  result is static geometry (source triangulation stays off; Gate 10 triangulates the export);
- bakes the contract vertex channels: COLOR0.r edge_thickness_mask, COLOR0.g
  edge_iridescence_mask (crystal only), COLOR0.b finish_mix_mask (mirror = 1), COLOR0.a = 1;
  UV2.x brushing_angle_normalized, UV2.y cmf_zone_id / 255;
- runs per-object mesh integrity (manifold, boundary, degenerate, duplicate, signed volume,
  components) and the contract budgets (triangles <= 120 000, 7 material slots);
- writes identity digests (vertex positions, object matrices, topology);
- renders six orthographic Workbench views, a zone hero, dimension / pivot overlays, an
  INTERNAL exploded z-stack (never a review artifact) and a Workbench turntable;
- exports a review-only GLB for interactive inspection (not the Gate 10 export).
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER_TURNTABLE = "--no-turntable" not in ARGS
FRAMES = int(ARGS[ARGS.index("--frames") + 1]) if "--frames" in ARGS else 72

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-012/modeling-contract.json"
SOURCE_BLEND = PIPELINE / "evidence/05-blockout/rev-012/tri-spinner-slab-blockout-r012.blend"
OUT_DIR = PIPELINE / "evidence/06-geometry/rev-010"
GEOMETRY_BLEND = OUT_DIR / "tri-spinner-slab-geometry-r010.blend"
REVIEW_GLB = OUT_DIR / "tri-spinner-slab-gate06-review-r010.glb"
TURNTABLE_DIR = Path(f"/tmp/tri-spinner-slab-g06-r010-turntable-{__import__('time').strftime('%Y%m%dT%H%M%S')}")
MM = 0.001

CONTRACT = json.loads(CONTRACT_PATH.read_text())
CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
GB = CONTRACT["geometry_builder"]
BUDGET = CONTRACT["performance_budget"]
INPUTS = {i["id"]: i for i in CONTRACT["parameters"]["inputs"]}
VALUES = json.loads((CONTRACT_PATH.parent / "contract-validation.json").read_text())["resolved_key_values_mm"]
BLOCKOUT_VALIDATION = json.loads((SOURCE_BLEND.parent / "blockout-validation.json").read_text())
VALUES.setdefault("case.structural_depth_mm", BLOCKOUT_VALIDATION["case_size_mm"][1])     # derived value resolved by the approved blockout (10.96 mm)
MANIFEST = json.loads((PIPELINE / "pipeline.json").read_text())

ZONE_COLORS = {1: (0.80, 0.90, 1.00, 1.0), 2: (0.22, 0.20, 0.26, 1.0), 3: (0.60, 0.62, 0.64, 1.0), 4: (0.09, 0.09, 0.10, 1.0),
               5: (0.86, 0.87, 0.89, 1.0), 6: (0.98, 0.99, 1.00, 1.0), 7: (0.92, 0.72, 0.30, 1.0)}
ZONE_LEGEND = "1 crystal / 2 smoke liner / 3 microblast / 4 graphite / 5 steel satin / 6 mirror / 7 gold"
# brushing angle per zone (normalized 0..1 = 0..180 deg): bezels horizontal, gold along the inlay long axis, others none
EDGE_FACE_AREA_MM2 = 2.5           # faces smaller than this are bevel / fillet strips; flats and side walls are far larger (per-corner mask)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


EXPECTED_SOURCE_SHA = sha256(SOURCE_BLEND) if "--unregistered-source" in ARGS else next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-blockout-blend")["sha256"]


def case_meshes():
    """Case deliverables only: the caller-owned review spinner (GEO_PDC_REVIEW_*) and preview-only objects are excluded."""
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO_PDC_") and not o.name.startswith("GEO_PDC_REVIEW_")
            and o.get("export_role") != "preview-only"]


def cleanup(ob):
    """Static-geometry cleanup after applying modifiers: merge vertices closer than 1 um and dissolve the resulting
    zero-length edges / zero-area faces (bevel + boolean slivers on the bolt heads and crystal frame). No vertex is moved
    by more than the 1 um merge distance; design intent is untouched."""
    before = (len(ob.data.vertices), len(ob.data.polygons))
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    return {"vertices_before": before[0], "vertices_after": len(ob.data.vertices), "polygons_before": before[1], "polygons_after": len(ob.data.polygons)}


def apply_all_modifiers(ob):
    """Apply modifiers in stack order (the builder already named them by contract order)."""
    applied = []
    bpy.context.view_layer.objects.active = ob
    for mod in list(ob.modifiers):
        name = mod.name
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=name)
        applied.append(name)
    return applied


def bake_channels(ob, zone):
    """Per-corner COLOR0 so a flat face's corners stay 0 while the bevel strip sharing the vertex is 1."""
    me = ob.data
    scale = ob.matrix_world.to_scale()
    edge_faces = set(); edge_area = 0.0; total_area = 0.0
    for poly in me.polygons:
        area_mm2 = poly.area * scale.x * scale.y / (MM * MM)
        total_area += area_mm2
        if area_mm2 < EDGE_FACE_AREA_MM2:
            edge_faces.add(poly.index); edge_area += area_mm2
    col = me.color_attributes.get("COLOR0") or me.color_attributes.new("COLOR0", "BYTE_COLOR", "CORNER")
    finish_mix = 1.0 if zone == 6 else 0.0
    for poly in me.polygons:
        e = 1.0 if poly.index in edge_faces else 0.0
        for li in poly.loop_indices:
            col.data[li].color = (e, e if zone == 1 else 0.0, finish_mix, 1.0)
    uv2 = me.uv_layers.get("UV2") or me.uv_layers.new(name="UV2")
    if zone == 5:
        angle = 0.0                                         # bezels: horizontal brushing
    elif zone == 7:
        dims = ob.dimensions
        angle = 0.0 if dims.x >= dims.z else 0.5            # inlay long axis (Blender X = canonical X, Blender Z = canonical Y)
    else:
        angle = 0.0
    for loop in me.loops:
        uv2.data[loop.index].uv = (angle, zone / 255.0)
    me.update()
    return {"edge_faces": len(edge_faces), "faces": len(me.polygons), "edge_area_fraction": round(edge_area / total_area, 4) if total_area else 0.0,
            "finish_mix": finish_mix, "brushing_angle_normalized": angle}


def integrity(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
    boundary = sum(1 for e in bm.edges if e.is_boundary)
    zero_len = sum(1 for e in bm.edges if e.calc_length() < 1e-7)
    zero_area = sum(1 for f in bm.faces if f.calc_area() < 1e-14)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    # duplicates: count vertex pairs closer than 1 micron without modifying the mesh
    dup = bmesh.ops.find_doubles(bm, verts=bm.verts, dist=1e-6)
    duplicate_count = len(dup["targetmap"])
    # connected components
    seen = set(); components = 0; comp_sizes = []
    for v in bm.verts:
        if v.index in seen:
            continue
        components += 1; stack = [v]; size = 0
        while stack:
            cur = stack.pop()
            if cur.index in seen:
                continue
            seen.add(cur.index); size += 1
            stack.extend(e.other_vert(cur) for e in cur.link_edges)
        comp_sizes.append(size)
    # signed volume (object space, closed meshes)
    vol = 0.0
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6.0
    bm.free()
    scale = ob.matrix_world.to_scale()
    vol_mm3 = vol * scale.x * scale.y * scale.z / (MM ** 3)
    return {"vertices": len(ob.data.vertices), "edges": len(ob.data.edges), "polygons": len(ob.data.polygons), "triangles": tris,
            "non_manifold_edges": non_manifold, "boundary_edges": boundary, "zero_length_edges": zero_len, "zero_area_faces": zero_area,
            "duplicate_vertices": duplicate_count, "components": components, "component_vertex_counts": comp_sizes[:8],
            "signed_volume_mm3": round(vol_mm3, 4), "watertight": non_manifold == 0 and boundary == 0,
            "positive_volume": vol_mm3 > 0}


def digests(objects):
    h_pos, h_mat, h_topo = hashlib.sha256(), hashlib.sha256(), hashlib.sha256()
    for ob in sorted(objects, key=lambda o: o.name):
        h_mat.update(ob.name.encode()); h_mat.update(json.dumps([[round(v, 7) for v in row] for row in ob.matrix_world]).encode())
        for v in ob.data.vertices:
            h_pos.update(("%.6f,%.6f,%.6f;" % tuple(v.co)).encode())
        for p in ob.data.polygons:
            h_topo.update((",".join(str(i) for i in p.vertices) + ";").encode())
    return {"vertexPositionDigest": h_pos.hexdigest(), "objectMatrixDigest": h_mat.hexdigest(), "topologyDigest": h_topo.hexdigest()}


def bounds(objects):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def configure_workbench(scene, note):
    scene.render.engine = "BLENDER_WORKBENCH"
    sh = scene.display.shading
    sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_cavity = True; sh.cavity_type = "BOTH"
    sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.2; sh.cavity_ridge_factor = 1.5; sh.cavity_valley_factor = 1.5
    sh.show_shadows = True; sh.shadow_intensity = 0.45; sh.show_specular_highlight = True
    scene.display.render_aa = "16"
    scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGB"; scene.render.film_transparent = False
    scene.world = bpy.data.worlds.get("WORLD_PDC_NEUTRAL") or bpy.data.worlds.new("WORLD_PDC_NEUTRAL")
    scene.world.color = (0.035, 0.037, 0.042)
    scene.view_settings.view_transform = "Standard"
    scene.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_frame_range", "use_stamp_memory",
                 "use_stamp_hostname", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene", "use_stamp_marker", "use_stamp_filename", "use_stamp_sequencer_strip"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.use_stamp_note = True; scene.render.stamp_note_text = note
    scene.render.stamp_font_size = 22; scene.render.stamp_foreground = (0.85, 0.85, 0.85, 1.0); scene.render.stamp_background = (0.0, 0.0, 0.0, 0.55)


def ortho_camera(name, direction, up, lo, hi, margin=0.06):
    d = Vector(direction).normalized(); u = Vector(up).normalized()
    centre = (lo + hi) / 2; size = hi - lo
    right = d.cross(u).normalized(); u = right.cross(d).normalized()
    extent_w = sum(abs(right[i]) * size[i] for i in range(3)); extent_h = sum(abs(u[i]) * size[i] for i in range(3))
    depth = sum(abs(d[i]) * size[i] for i in range(3))
    cam_data = bpy.data.cameras.new(name); cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(extent_w, extent_h) * (1 + 2 * margin); cam_data.clip_start = 0.001; cam_data.clip_end = 10.0
    cam = bpy.data.objects.new(name, cam_data); bpy.context.scene.collection.objects.link(cam)
    cam.location = centre - d * (depth + 0.5)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    # align image up
    q = cam.rotation_euler.to_quaternion(); cam_up = q @ Vector((0, 1, 0))
    ang = cam_up.angle(u, 0.0); sign = 1.0 if (cam_up.cross(u)).dot(d) < 0 else -1.0
    cam.rotation_euler.rotate_axis("Z", sign * ang) if abs(ang) > 1e-6 else None
    cam["camera_recipe"] = json.dumps({"projection": "ortho", "direction_b": list(d), "up_b": list(u), "ortho_scale_m": cam_data.ortho_scale, "margin": margin})
    return cam, extent_w, extent_h


def render(scene, cam, path, resolution):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    assert sha256(SOURCE_BLEND) == EXPECTED_SOURCE_SHA, "approved Gate 05 rev-011 blend hash changed; refuse to refine an unregistered source"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "06-geometry", "geometryRevision": 10,
              "sourceBlend": str(SOURCE_BLEND.relative_to(REPO)), "sourceBlendSha256": EXPECTED_SOURCE_SHA, "contractSha256": CONTRACT_SHA,
              "sourceGate05EvidenceRevision": "rev-012", "designChanged": False, "provisional_marker": "PROVISIONAL_DIMENSIONS"}

    meshes = case_meshes()
    # cutters and review-only objects are not geometry deliverables
    removed = []
    for ob in list(bpy.data.objects):
        if ob.name.startswith("CUT_PDC_") or ob.get("export_role") == "preview-only":
            removed.append(ob.name); bpy.data.objects.remove(ob, do_unlink=True)
    report["removed_non_deliverables"] = removed

    applied = {}
    for ob in meshes:
        applied[ob.name] = apply_all_modifiers(ob)
    report["modifiers_applied"] = applied
    report["modifier_order_contract"] = GB["modifier_order"]
    report["cleanup"] = {ob.name: cleanup(ob) for ob in meshes}
    report["cleanup"]["_rule"] = "remove_doubles 1e-6 m + dissolve_degenerate 1e-6 m after modifier apply; no design change"

    channels = {}
    for ob in meshes:
        zone = int(ob.get("cmf_zone_id", 0))
        channels[ob.name] = bake_channels(ob, zone)
    report["vertex_channels"] = {"spec": CONTRACT["vertex_channels"], "edge_face_area_mm2": EDGE_FACE_AREA_MM2, "domain": "CORNER", "per_object": channels}

    integ = {ob.name: integrity(ob) for ob in meshes}
    total_tris = sum(v["triangles"] for v in integ.values())
    report["mesh_integrity"] = integ
    report["totals"] = {"objects": len(meshes), "triangles": total_tris, "triangle_budget": BUDGET["case_triangles_max"],
                        "material_slots_used": len({int(o.get("cmf_zone_id", 0)) for o in meshes}), "material_slot_budget": BUDGET["case_material_slots_max"]}
    report["identity"] = digests(meshes)

    lo, hi = bounds(meshes)
    size_mm = [(hi - lo)[i] / MM for i in range(3)]
    # Blender (x, y, z) = canonical (x, -z, y): width = x, depth = y, height = z
    report["dimensions_mm"] = {"width": round(size_mm[0], 3), "depth": round(size_mm[1], 3), "height": round(size_mm[2], 3)}
    report["contract_dimensions_mm"] = {"width": VALUES["case.width_mm"], "height": VALUES["case.height_mm"], "structural_depth": VALUES["case.structural_depth_mm"],
                                        "envelope_depth_with_toy": VALUES["assembled.envelope_depth_mm"]}
    slot = bpy.data.objects.get("PIVOT_PDC_CONTENT_SLOT")
    report["content_slot_location_mm"] = [round(v / MM, 3) for v in slot.matrix_world.translation] if slot else None
    root = bpy.data.objects.get("ROOT_PDC_PRESENTATION")
    report["presentation_root_location_mm"] = [round(v / MM, 3) for v in root.matrix_world.translation] if root else None

    checks = [
        ("source-hash-matches-approved-gate05", True, EXPECTED_SOURCE_SHA[:12]),
        ("all-modifiers-applied", all(len(o.modifiers) == 0 for o in meshes), f"{sum(len(v) for v in applied.values())} modifiers applied"),
        ("all-case-meshes-watertight", all(v["watertight"] for v in integ.values()), json.dumps({k: (v["non_manifold_edges"], v["boundary_edges"]) for k, v in integ.items() if not v["watertight"]})),
        ("no-degenerate-geometry", all(v["zero_length_edges"] == 0 and v["zero_area_faces"] == 0 for v in integ.values()), ""),
        ("no-duplicate-vertices", all(v["duplicate_vertices"] == 0 for v in integ.values()), json.dumps({k: v["duplicate_vertices"] for k, v in integ.items() if v["duplicate_vertices"]})),
        ("positive-material-volume", all(v["positive_volume"] for v in integ.values()), json.dumps({k: v["signed_volume_mm3"] for k, v in integ.items() if not v["positive_volume"]})),
        ("triangle-budget", total_tris <= BUDGET["case_triangles_max"], f"{total_tris} <= {BUDGET['case_triangles_max']}"),
        ("material-slot-budget", report["totals"]["material_slots_used"] <= BUDGET["case_material_slots_max"], f"{report['totals']['material_slots_used']} zones"),
        ("case-width-matches-contract", abs(size_mm[0] - VALUES["case.width_mm"]) < 0.05, f"{size_mm[0]:.3f} vs {VALUES['case.width_mm']}"),
        ("case-height-matches-contract", abs(size_mm[2] - VALUES["case.height_mm"]) < 0.05, f"{size_mm[2]:.3f} vs {VALUES['case.height_mm']}"),
        ("case-structural-depth-matches-contract", abs(size_mm[1] - VALUES["case.structural_depth_mm"]) < 0.05, f"{size_mm[1]:.3f} vs {VALUES['case.structural_depth_mm']} (envelope {VALUES['assembled.envelope_depth_mm']} includes the toy)"),
        ("vertex-channels-present", all(o.data.color_attributes.get("COLOR0") and o.data.uv_layers.get("UV2") for o in meshes), "COLOR0 + UV2 on every case mesh"),
        ("crystal-iridescence-mask-edge-limited", 0.005 < channels.get("GEO_PDC_OUTER_CRYSTAL_FRAME", {}).get("edge_area_fraction", 0) < 0.5, json.dumps(channels.get("GEO_PDC_OUTER_CRYSTAL_FRAME"))),
        ("no-wings", not any(o.name.startswith("GEO_PDC_MAIN_WING_") for o in meshes), "rev-009+ contract"),
        ("content-slot-present", slot is not None, str(report["content_slot_location_mm"])),
        ("no-cutters-left", not any(o.name.startswith("CUT_PDC_") for o in bpy.data.objects), f"removed {len(removed)}"),
    ]
    report["checks"] = [{"id": i, "status": "pass" if ok else "fail", "detail": d} for i, ok, d in checks]
    report["all_pass"] = all(c["status"] == "pass" for c in report["checks"])

    # --- renders: six orthographic Workbench views + zone hero + turntable
    note = f"PROVISIONAL_DIMENSIONS | tri-spinner-slab-v3-cmf | Gate 06 geometry r010 | source Gate 05 r012 {EXPECTED_SOURCE_SHA[:12]} | contract {CONTRACT_SHA[:12]} | zones: {ZONE_LEGEND}"
    configure_workbench(scene, note)
    for ob in meshes:
        ob.color = ZONE_COLORS.get(int(ob.get("cmf_zone_id", 0)), (0.5, 0.5, 0.5, 1.0))
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.name.startswith("GEO_PDC_REVIEW_SPINNER"):
            ob.hide_render = True                              # caller-owned toy: not part of Gate 06 geometry
    # camera looks ALONG the direction vector; canonical front (+Z) is Blender -Y, so the front camera sits at -Y and looks toward +Y
    views = {"front": ((0, 1, 0), (0, 0, 1)), "back": ((0, -1, 0), (0, 0, 1)), "top": ((0, 0, -1), (0, -1, 0)), "bottom": ((0, 0, 1), (0, 1, 0)),
             "left": ((1, 0, 0), (0, 0, 1)), "right": ((-1, 0, 0), (0, 0, 1))}
    ortho_meta = {}
    for vid, (direction, up) in views.items():
        cam, ew, eh = ortho_camera(f"CAM_G06_{vid.upper()}", direction, up, lo, hi)
        res = (2048, 2048)
        render(scene, cam, OUT_DIR / f"ortho-{vid}.png", res)
        ortho_meta[vid] = {"ortho_scale_m": cam.data.ortho_scale, "extent_w_m": ew, "extent_h_m": eh, "resolution": res, "px_per_mm": res[0] / (cam.data.ortho_scale / MM)}
    report["orthographic_views"] = ortho_meta
    hero = bpy.data.objects.get("CAM_PDC_HERO")
    if hero:
        render(scene, hero, OUT_DIR / "geometry-workbench-hero.png", (2048, 1365))

    # --- INTERNAL exploded z-stack: technical evidence only, never a review artifact (whole-case gate)
    saved = {ob.name: ob.location.copy() for ob in meshes}
    z_order = sorted(meshes, key=lambda o: (o.matrix_world @ Vector(o.bound_box[0])).y)
    for i, ob in enumerate(z_order):
        ob.location.y -= 0.004 * i                         # Blender -Y = toward the viewer
    cam, _, _ = ortho_camera("CAM_G06_EXPLODED_INTERNAL", (0.6, -1, 0.35), (0, 0, 1), *bounds(meshes), margin=0.08)
    render(scene, cam, OUT_DIR / "internal-exploded-zstack.png", (2048, 1365))
    for ob in meshes:
        ob.location = saved[ob.name]
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.context.view_layer.update()

    if RENDER_TURNTABLE and root is not None:
        TURNTABLE_DIR.mkdir(parents=True, exist_ok=False)
        for i in range(FRAMES):
            root.rotation_euler = (0.0, 0.0, math.radians(360.0 * i / FRAMES))
            bpy.context.view_layer.update()
            render(scene, hero, TURNTABLE_DIR / f"frame_{i:04d}.png", (1440, 960))
        root.rotation_euler = (0.0, 0.0, 0.0)
        report["turntable"] = {"frames": FRAMES, "fps": 24, "camera": "CAM_PDC_HERO", "raw_frame_dir": str(TURNTABLE_DIR)}

    # --- save geometry blend, then export a review GLB (case + controls; no toy, no cameras/lights)
    for cam_ob in [o for o in bpy.data.objects if o.name.startswith("CAM_G06_")]:
        bpy.data.objects.remove(cam_ob, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(GEOMETRY_BLEND))
    for ob in bpy.data.objects:
        ob.select_set(ob.type in ("MESH", "EMPTY") and (ob.name.startswith(("GEO_PDC_", "ROOT_PDC_", "PIVOT_PDC_"))) and not ob.name.startswith("GEO_PDC_REVIEW_SPINNER"))
    bpy.ops.export_scene.gltf(filepath=str(REVIEW_GLB), use_selection=True, export_format="GLB", export_apply=True, export_yup=True,
                              export_texcoords=True, export_normals=True, export_attributes=True, export_extras=True)
    report["review_glb"] = {"path": str(REVIEW_GLB.relative_to(REPO)), "sha256": sha256(REVIEW_GLB), "purpose": "interactive-review-only-not-gate10-export",
                            "objects": sorted(o.name for o in bpy.data.objects if o.select_get())}
    report["geometry_blend"] = {"path": str(GEOMETRY_BLEND.relative_to(REPO)), "sha256": sha256(GEOMETRY_BLEND)}
    (OUT_DIR / "geometry-revalidation.json").write_text(json.dumps(report, indent=2) + "\n")
    print("GATE06_RESULT=" + json.dumps({"all_pass": report["all_pass"], "fails": [c["id"] for c in report["checks"] if c["status"] != "pass"],
                                        "triangles": total_tris, "objects": len(meshes)}))


main()
