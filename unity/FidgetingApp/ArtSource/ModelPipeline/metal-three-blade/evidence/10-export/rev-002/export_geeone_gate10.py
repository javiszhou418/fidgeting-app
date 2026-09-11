"""Gate 10 export rev-002 · GEEONE 龙鳞三叶 · from the approved geometry rev-008 (user 2026-09-08 13:55 '继续吧').

    blender -b <06-geometry/rev-008/geeone-geometry-r008.blend> --python export_geeone_gate10.py -- --contract <json> --out <dir>

Steps:
  1. keep only the four shipping parts (Rotor_Body, Cap_Top, Cap_Bottom, Hub_Core); apply the bevel modifiers; flat shading
  2. metres: the geometry blend is authored in millimetres (1 BU = 1 mm, 2R = 85 mm provisional) -> vertices x 0.001, unit scale 1.0
  3. export materials by name (Unity remaps by name): M_Geeone_Satin / M_Geeone_DiscTurned / M_Geeone_HubDark
  4. hierarchy: GEEONE_TriSpinner -> Rotor_Root [Rotor_Body]  (rotates about Blender +Z = Unity +Y)
                                  -> Fixed_Root [Cap_Top, Cap_Bottom, Hub_Core]  (static)
  5. FBX (-Z forward, Y up, FBX_SCALE_UNITS) + GLB (Y up) + collision FBX (convex hull of the rotor, cylinder for the fixed group)
  6. round-trip: re-import GLB and FBX into fresh scenes, check names / hierarchy / mesh counts / bounds / materials
  7. export-manifest.json (hashes, hierarchy, units, contract sha) + export-validation.json (pass/fail) + Workbench review renders
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

KEEP = ("Rotor_Body", "Cap_Top", "Cap_Bottom", "Hub_Core")
ROTATING = ("Rotor_Body",)
FIXED = ("Cap_Top", "Cap_Bottom", "Hub_Core")
MM_PER_R = 42.5  # 85 mm provisional


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--contract", required=True)
    p.add_argument("--out", required=True)
    return p.parse_args(argv)


A = args()
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "review").mkdir(exist_ok=True)
CONTRACT_PATH = Path(A.contract)
C = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
SOURCE_BLEND = Path(bpy.data.filepath)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply_modifiers(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    me.name = ob.name
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    return me


def principled(name, base, rough, metallic=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*base, 1.0)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_fbx(path: Path, objects):
    select(objects)
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
        object_types={"EMPTY", "MESH"}, use_mesh_modifiers=True, mesh_smooth_type="FACE", use_subsurf=False,
        use_mesh_edges=False, use_tspace=False, use_custom_props=True, add_leaf_bones=False, bake_anim=False,
        axis_forward="-Z", axis_up="Y", path_mode="AUTO", embed_textures=False,
    )


def export_glb(path: Path, objects):
    select(objects)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_apply=True, export_yup=True, export_materials="EXPORT", export_cameras=False, export_lights=False)


def tri_count(me):
    return sum(max(0, len(p.vertices) - 2) for p in me.polygons)


def bounds(objects):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for ob in objects:
        for v in ob.data.vertices:
            w = ob.matrix_world @ v.co
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


def prepare():
    scene = bpy.context.scene
    unit_before = {"system": scene.unit_settings.system, "scale_length": scene.unit_settings.scale_length, "length_unit": scene.unit_settings.length_unit}
    for ob in list(bpy.data.objects):
        if ob.name not in KEEP:
            bpy.data.objects.remove(ob, do_unlink=True)
    for name in KEEP:
        ob = bpy.data.objects[name]
        assert ob.type == "MESH", name
        apply_modifiers(ob)
        # millimetres -> metres at mesh level; transforms stay identity, pivot = spin axis at the origin
        assert ob.matrix_world.to_translation().length < 1e-9 and abs(ob.matrix_world.to_scale().x - 1.0) < 1e-9, f"{name} transform is not identity"
        for v in ob.data.vertices:
            v.co *= 0.001
        for p in ob.data.polygons:
            p.use_smooth = False
        ob.data.update()
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    # materials by name
    satin = principled("M_Geeone_Satin", (0.78, 0.79, 0.80), 0.36)
    disc = principled("M_Geeone_DiscTurned", (0.80, 0.81, 0.82), 0.30)
    dark = principled("M_Geeone_HubDark", (0.06, 0.06, 0.065), 0.45)
    body = bpy.data.objects["Rotor_Body"]
    body.data.materials.clear()
    body.data.materials.append(satin)
    for name in ("Cap_Top", "Cap_Bottom"):
        me = bpy.data.objects[name].data
        me.materials.clear()
        me.materials.append(satin)
        me.materials.append(disc)
        for p in me.polygons:  # disc sectors = triangles touching the centre vertex (dish apex)
            p.material_index = 1 if (len(p.vertices) == 3 and any(abs(me.vertices[vi].co.x) < 1e-9 and abs(me.vertices[vi].co.y) < 1e-9 for vi in p.vertices)) else 0
    hub = bpy.data.objects["Hub_Core"].data
    hub.materials.clear()
    hub.materials.append(dark)
    # hierarchy
    root = bpy.data.objects.new("GEEONE_TriSpinner", None)
    rotor_root = bpy.data.objects.new("Rotor_Root", None)
    fixed_root = bpy.data.objects.new("Fixed_Root", None)
    for e in (root, rotor_root, fixed_root):
        e.empty_display_size = 0.01
        scene.collection.objects.link(e)
    rotor_root.parent = root
    fixed_root.parent = root
    for name in ROTATING:
        bpy.data.objects[name].parent = rotor_root
    for name in FIXED:
        bpy.data.objects[name].parent = fixed_root
    root["kinematics"] = "Rotor_Root rotates about local Z (Unity local Y); Fixed_Root static; clearance radial 0.015 R, vertical 0.0122 R"
    root["units"] = "metres; 2R = 0.085 m user-authorized-provisional"
    root["source"] = f"{SOURCE_BLEND.name} + {CONTRACT_PATH.name} (spec v21)"
    return unit_before, [root, rotor_root, fixed_root] + [bpy.data.objects[n] for n in KEEP]


def build_collision():
    """Rotor: convex hull of Rotor_Body (rotating touch surface). Fixed: cylinder r = cap radius over the cap-to-cap height."""
    body = bpy.data.objects["Rotor_Body"]
    bm = bmesh.new()
    for v in body.data.vertices:
        bm.verts.new(v.co)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    me = bpy.data.meshes.new("Rotor_Collision")
    bm.to_mesh(me)
    bm.free()
    rc = bpy.data.objects.new("Rotor_Collision", me)
    bpy.context.scene.collection.objects.link(rc)
    rc.parent = bpy.data.objects["Rotor_Root"]
    fixed = [bpy.data.objects[n] for n in FIXED]
    lo, hi = bounds(fixed)
    r = C["capRadiusToR"] * MM_PER_R * 0.001
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=r, radius2=r, depth=hi.z - lo.z)
    for v in bm.verts:
        v.co.z += (hi.z + lo.z) / 2
    me2 = bpy.data.meshes.new("Fixed_Collision")
    bm.to_mesh(me2)
    bm.free()
    fc = bpy.data.objects.new("Fixed_Collision", me2)
    bpy.context.scene.collection.objects.link(fc)
    fc.parent = bpy.data.objects["Fixed_Root"]
    return rc, fc


def roundtrip(path: Path, kind: str):
    bpy.ops.wm.read_homefile(use_empty=True)
    if kind == "glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path))
    objs = {ob.name: ob for ob in bpy.data.objects}
    meshes = [ob for ob in bpy.data.objects if ob.type == "MESH"]
    rep = {"file": path.name, "sha256": sha256(path), "objects": sorted(objs), "meshes": {}, "hierarchy": {}}
    for ob in bpy.data.objects:
        rep["hierarchy"][ob.name] = ob.parent.name if ob.parent else None
    for ob in meshes:
        lo, hi = bounds([ob])
        rep["meshes"][ob.name] = {"verts": len(ob.data.vertices), "faces": len(ob.data.polygons), "tris": tri_count(ob.data), "materials": [m.name if m else None for m in ob.data.materials],
                                  "bounds_m": {"min": [round(v, 5) for v in lo], "max": [round(v, 5) for v in hi]}}
    rot = [ob for ob in meshes if ob.name.startswith("Rotor_Body")]
    fix = [ob for ob in meshes if any(ob.name.startswith(n) for n in FIXED)]
    checks = {}
    if rot:
        lo, hi = bounds(rot)
        radii = [math.hypot(*(ob.matrix_world @ v.co).xy) for ob in rot for v in ob.data.vertices]
        planar = 2 * max(radii)  # three-fold shape: circumscribed diameter, not the AABB
        r_min = min(radii)
        checks["rotor circumscribed diameter 0.085 m (±0.5 mm)"] = abs(planar - 0.085) < 0.0005
        checks["rotor thickness 0.17 R + crest (≤ 0.0110 m)"] = (hi.z - lo.z) <= 0.0110 and (hi.z - lo.z) >= 0.0070
        checks["rotor bore 0.425 R centred on the axis (min vertex radius ±0.2 mm)"] = abs(r_min - C["cap"]["rotorBoreRadiusToR"] * MM_PER_R * 0.001) < 0.0002
        checks["rotor origin = spin axis"] = all(ob.matrix_world.to_translation().length < 1e-6 for ob in rot)
        rep["rotor_planar_m"] = round(planar, 5)
        rep["rotor_bore_radius_m"] = round(r_min, 5)
        rep["rotor_thickness_m"] = round(hi.z - lo.z, 5)
    if fix:
        lo, hi = bounds(fix)
        cap_d = max(hi.x - lo.x, hi.y - lo.y)
        checks["cap diameter 0.485 R (±0.5 mm)"] = abs(cap_d - 2 * C["capRadiusToR"] * MM_PER_R * 0.001) < 0.0005
        rep["fixed_planar_m"] = round(cap_d, 5)
        rep["fixed_height_m"] = round(hi.z - lo.z, 5)
    checks["four shipping meshes"] = len(meshes) == 4
    checks["rotor under Rotor_Root, fixed parts under Fixed_Root"] = all(rep["hierarchy"].get(o, "").startswith("Rotor_Root") for o in rep["meshes"] if o.startswith("Rotor_Body")) and all(rep["hierarchy"].get(o, "").startswith("Fixed_Root") for o in rep["meshes"] if any(o.startswith(n) for n in FIXED))
    checks["hub core centred (fixed AABB centre on the axis)"] = bool(fix) and abs((bounds(fix)[0].x + bounds(fix)[1].x) / 2) < 0.0005 and abs((bounds(fix)[0].y + bounds(fix)[1].y) / 2) < 0.0005
    checks["materials survived"] = {"M_Geeone_Satin", "M_Geeone_DiscTurned", "M_Geeone_HubDark"} <= {m for ob in meshes for m in [mm.name.split(".")[0] if mm else "" for mm in ob.data.materials]}
    rep["checks"] = checks
    rep["pass"] = all(checks.values())
    return rep


def review_renders(glb: Path):
    """Workbench renders of the re-imported GLB (the real exported file), hero + top + 24-frame orbit."""
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = scene.render.resolution_y = 1200
    sh = scene.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    scene.display.render_aa = "8"
    scene.world = scene.world or bpy.data.worlds.new("World")
    scene.world.color = (0.18, 0.18, 0.18)
    cam = bpy.data.objects.new("ReviewCam", bpy.data.cameras.new("ReviewCam"))
    scene.collection.objects.link(cam)
    scene.camera = cam
    R = 0.0425

    def look_at(target):
        d = Vector(target) - cam.location
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    cam.data.clip_start = 0.001
    cam.data.clip_end = 10
    views = {"glb-hero": ((1.2 * R, -1.6 * R, 1.5 * R), (0, 0, 0.3 * 0.085 * R), 50.0), "glb-low": ((0.3 * R, -2.6 * R, 0.45 * R), (0, 0, 0.0085 * R), 60.0)}
    for name, (loc, tgt, lens) in views.items():
        cam.location = Vector(loc)
        look_at(tgt)
        cam.data.type = "PERSP"
        cam.data.lens = lens
        scene.render.filepath = str(OUT / "review" / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.3 * R
    cam.location = Vector((0, 0, 1.0))
    look_at((0, 0, 0))
    scene.render.filepath = str(OUT / "review" / "glb-top-ortho.png")
    bpy.ops.render.render(write_still=True)
    cam.data.type = "PERSP"
    cam.data.lens = 50.0
    scene.render.resolution_x = scene.render.resolution_y = 720
    (OUT / "review" / "orbit").mkdir(exist_ok=True)
    for i in range(24):
        a = 2 * math.pi * i / 24
        cam.location = Vector((2.0 * R * math.cos(a), 2.0 * R * math.sin(a), 1.25 * R))
        look_at((0, 0, 0.2 * 0.085 * R))
        scene.render.filepath = str(OUT / "review" / "orbit" / f"frame_{i:03d}.png")
        bpy.ops.render.render(write_still=True)
    print("[g10] review renders done")


def main():
    unit_before, export_objects = prepare()
    visual = [ob for ob in export_objects]
    blend_out = OUT / "geeone-tri-spinner-export-ready.blend"
    fbx_out = OUT / "geeone-tri-spinner.fbx"
    glb_out = OUT / "geeone-tri-spinner.glb"
    col_out = OUT / "geeone-tri-spinner-collision.fbx"
    stats = {}
    for name in KEEP:
        ob = bpy.data.objects[name]
        lo, hi = bounds([ob])
        stats[name] = {"verts": len(ob.data.vertices), "faces": len(ob.data.polygons), "tris": tri_count(ob.data), "materials": [m.name for m in ob.data.materials], "group": "Rotor_Root" if name in ROTATING else "Fixed_Root",
                       "bounds_m": {"min": [round(v, 5) for v in lo], "max": [round(v, 5) for v in hi]}}
    export_fbx(fbx_out, visual)
    export_glb(glb_out, visual)
    rc, fc = build_collision()
    empties = [bpy.data.objects[n] for n in ("GEEONE_TriSpinner", "Rotor_Root", "Fixed_Root")]
    export_fbx(col_out, empties + [rc, fc])
    col_stats = {o.name: {"verts": len(o.data.vertices), "faces": len(o.data.polygons), "parent": o.parent.name} for o in (rc, fc)}
    for o in (rc, fc):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out))
    print("[g10] exported", fbx_out.name, glb_out.name, col_out.name, blend_out.name)

    rt_glb = roundtrip(glb_out, "glb")
    rt_fbx = roundtrip(fbx_out, "fbx")
    print("[g10] glb roundtrip", json.dumps(rt_glb["checks"], ensure_ascii=False), "planar", rt_glb.get("rotor_planar_m"), "thick", rt_glb.get("rotor_thickness_m"), "cap", rt_glb.get("fixed_planar_m"), "h", rt_glb.get("fixed_height_m"))
    print("[g10] fbx roundtrip", json.dumps(rt_fbx["checks"], ensure_ascii=False), "planar", rt_fbx.get("rotor_planar_m"), "thick", rt_fbx.get("rotor_thickness_m"), "cap", rt_fbx.get("fixed_planar_m"), "h", rt_fbx.get("fixed_height_m"))

    manifest = {
        "modelId": "metal-three-blade",
        "stage": "10-export",
        "revision": 2,
        "source": {"geometryBlend": SOURCE_BLEND.name, "geometryBlendSha256": sha256(SOURCE_BLEND), "contract": CONTRACT_PATH.name, "contractSha256": sha256(CONTRACT_PATH), "specSha256": C["source"].get("specSha256")},
        "units": {"authored": unit_before, "exported": "metres (mesh x 0.001); FBX apply_unit_scale FBX_SCALE_UNITS; GLB Y-up", "planarDiameterM": 0.085, "provisional": "2R = 85 mm user-authorized-provisional"},
        "axes": {"blender": "Z up (spin axis)", "fbx": "-Z forward / Y up", "unity": "spin axis = local +Y of Rotor_Root"},
        "hierarchy": {"GEEONE_TriSpinner": {"Rotor_Root": list(ROTATING), "Fixed_Root": list(FIXED)}},
        "kinematics": C["cap"].get("kinematics"),
        "materials": {"M_Geeone_Satin": "rotor + cap crown/skirt: metallic 1, roughness 0.36", "M_Geeone_DiscTurned": "cap 14-sector dish: metallic 1, roughness 0.30 (Unity: isotropic satin, no anisotropy)", "M_Geeone_HubDark": "static hub core: dark steel 0.06, roughness 0.45"},
        "meshes": stats,
        "collision": col_stats,
        "files": {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size} for p in (fbx_out, glb_out, col_out, blend_out)},
    }
    (OUT / "export-manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    validation = {"schemaVersion": 1, "gate": "10-export", "revision": 2, "glb": rt_glb, "fbx": rt_fbx,
                  "manifest": {"path": "export-manifest.json", "sha256": sha256(OUT / "export-manifest.json")},
                  "pass": rt_glb["pass"] and rt_fbx["pass"]}
    (OUT / "export-validation.json").write_text(json.dumps(validation, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("[g10] validation pass =", validation["pass"])
    review_renders(glb_out)


main()
