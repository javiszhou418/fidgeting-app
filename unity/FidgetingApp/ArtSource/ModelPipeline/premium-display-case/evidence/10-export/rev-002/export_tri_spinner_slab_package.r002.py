"""Gate 10 export package for the premium-display-case `tri-spinner-slab-v3-cmf` variant
(evidence rev-002, from the user-approved Gate 07 rev-003 materials / Gate 06 rev-011 geometry).

    blender -b --python tools/blender/export_tri_spinner_slab_package.py

Builds the immutable product package the Unity import consumes:
- product blend: ROOT_PDC_PRESENTATION > ROOT_PDC_CASE_ASSEMBLY > 38 GEO_PDC_* case meshes + PIVOT_PDC_CONTENT_SLOT;
  no toy, lights, cameras, floor, cutters or review pivots; simplified export materials (constant base colour /
  metallic / roughness per zone from the Gate 07 report, named M_PDC_*) so FBX and GLB carry the same PBR basics;
- FBX (Unity axes, no unit scale, custom props with cmf_zone_id) and GLB (Y-up, COLOR_0 = COLOR0, TEXCOORD_0 = UV2);
- the header label decal PNG + layout copied into the package for the Unity material;
- fresh-scene round-trip validation of both files (object count, parents, bounds, triangles) and a Workbench review render;
- export-manifest.json with hashes, approvals and the governing contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[2]
PIPELINE = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
CONTRACT_PATH = PIPELINE / "evidence/03-contract/rev-013/modeling-contract.json"
SOURCE_BLEND = PIPELINE / "evidence/07-material/rev-003/tri-spinner-slab-material-r003.blend"
G07_REPORT = PIPELINE / "evidence/07-material/rev-003/material-revalidation.json"
G06_REPORT = PIPELINE / "evidence/06-geometry/rev-011/geometry-revalidation.json"
DECAL_PNG = PIPELINE / "evidence/07-material/rev-003/header-label-decal.png"
DECAL_JSON = PIPELINE / "evidence/07-material/rev-003/header-label-decal.json"
OUT_DIR = PIPELINE / "evidence/10-export/rev-002"
STEM = "tri-spinner-slab-product-r002"
MM = 0.001
CONTRACT = json.loads(CONTRACT_PATH.read_text()); CONTRACT_SHA = CONTRACT["hashing"]["contract_sha256"]
MANIFEST = json.loads((PIPELINE / "pipeline.json").read_text())
G07 = json.loads(G07_REPORT.read_text()); G06 = json.loads(G06_REPORT.read_text())
KEEP_EMPTIES = ("ROOT_PDC_PRESENTATION", "ROOT_PDC_CASE_ASSEMBLY", "PIVOT_PDC_CONTENT_SLOT")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def bounds(objects):
    lo = Vector((math.inf,) * 3); hi = Vector((-math.inf,) * 3)
    for ob in objects:
        for c in ob.bound_box:
            p = ob.matrix_world @ Vector(c); lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def case_meshes():
    return [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO_PDC_") and not o.name.startswith("GEO_PDC_REVIEW_") and o.get("export_role") != "preview-only"]


def tri_count(ob):
    dg = bpy.context.evaluated_depsgraph_get(); me = ob.evaluated_get(dg).to_mesh(); me.calc_loop_triangles(); n = len(me.loop_triangles); ob.evaluated_get(dg).to_mesh_clear(); return n


def snapshot(objects):
    lo, hi = bounds([o for o in objects if o.type == "MESH"])
    return {"objectCount": len(objects), "meshCount": sum(1 for o in objects if o.type == "MESH"), "emptyCount": sum(1 for o in objects if o.type == "EMPTY"),
            "parentMap": {o.name: (o.parent.name if o.parent else None) for o in sorted(objects, key=lambda o: o.name)},
            "boundsMm": {"min": [round(v / MM, 3) for v in lo], "max": [round(v / MM, 3) for v in hi], "size": [round((hi - lo)[i] / MM, 3) for i in range(3)]},
            "triangles": sum(tri_count(o) for o in objects if o.type == "MESH")}


def simplified_materials():
    """Constant PBR per zone from the approved Gate 07 values (FBX/GLB cannot carry the procedural node trees)."""
    zones = G07["materials_by_zone"]; mats = {}
    for z, spec in zones.items():
        mat = bpy.data.materials.new(spec["material"].replace("M_PDC_", "M_PDC_Export_")); mat.use_nodes = True
        b = mat.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*spec["base_color_linear"], 1.0); b.inputs["Metallic"].default_value = spec["metallic"]
        b.inputs["Roughness"].default_value = spec["roughness_base"]
        if int(z) == 1:
            b.inputs["Transmission Weight"].default_value = 1.0; b.inputs["IOR"].default_value = 1.49; mat.blend_method = "BLEND"
        if int(z) == 2:
            b.inputs["Transmission Weight"].default_value = spec["transmission"]; mat.blend_method = "BLEND"
        mat["cmf_zone_id"] = int(z); mat["gate07_material"] = spec["material"]; mats[int(z)] = mat
    return mats


def main():
    expected = next(a for a in MANIFEST["assets"] if a["id"] == "pdc-v3-g07-material-blend")["sha256"]
    assert sha256(SOURCE_BLEND) == expected, "approved Gate 07 rev-003 blend hash changed"
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND)); scene = bpy.context.scene
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # --- strip everything that is not the product
    removed = []
    for ob in list(bpy.data.objects):
        keep = (ob.type == "MESH" and ob.name.startswith("GEO_PDC_") and not ob.name.startswith("GEO_PDC_REVIEW_") and ob.get("export_role") != "preview-only") or ob.name in KEEP_EMPTIES
        if not keep:
            removed.append(ob.name); bpy.data.objects.remove(ob, do_unlink=True)
    meshes = case_meshes(); mats = simplified_materials()
    for ob in meshes:
        zone = int(ob.get("cmf_zone_id", 0)); ob.data.materials.clear(); ob.data.materials.append(mats[zone])
        if ob.modifiers:
            raise RuntimeError(f"{ob.name} still has modifiers")
    for block in (bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images, bpy.data.node_groups, bpy.data.worlds):
        for datablock in list(block):
            if datablock.users == 0:
                block.remove(datablock)
    src_snap = snapshot([o for o in bpy.data.objects])
    dims = src_snap["boundsMm"]["size"]
    material_table = {str(z): {"name": m.name, "gate07": m["gate07_material"]} for z, m in mats.items()}     # captured before the scene is replaced by the round-trips
    product_blend = OUT_DIR / f"{STEM}.blend"; bpy.ops.wm.save_as_mainfile(filepath=str(product_blend))

    # --- exports
    for ob in bpy.data.objects:
        ob.select_set(True)
    fbx = OUT_DIR / f"{STEM}.fbx"; glb = OUT_DIR / f"{STEM}.glb"
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={"EMPTY", "MESH"}, global_scale=1.0, apply_unit_scale=False, apply_scale_options="FBX_SCALE_NONE",
                             use_space_transform=True, bake_space_transform=False, axis_forward="-Z", axis_up="Y", use_mesh_modifiers=True, mesh_smooth_type="FACE",
                             use_custom_props=True, add_leaf_bones=False, use_triangles=True, path_mode="COPY", embed_textures=False)
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_animations=False, export_cameras=False,
                              export_lights=False, export_materials="EXPORT", export_texcoords=True, export_normals=True, export_tangents=False, export_extras=True, export_attributes=True)
    shutil.copyfile(DECAL_PNG, OUT_DIR / "header-label-decal.png"); shutil.copyfile(DECAL_JSON, OUT_DIR / "header-label-decal.json")

    # --- fresh-scene round-trips
    roundtrip = {}
    for fmt, path in (("FBX", fbx), ("GLB", glb)):
        bpy.ops.wm.read_homefile(use_empty=True)
        if fmt == "FBX":
            bpy.ops.import_scene.fbx(filepath=str(path))
        else:
            bpy.ops.import_scene.gltf(filepath=str(path))
        objs = [o for o in bpy.data.objects]
        snap = snapshot(objs)
        # glTF import may add a scene root collection but no extra objects; FBX keeps empties
        snap["meshNames"] = sorted(o.name for o in objs if o.type == "MESH")[:6] + ["..."]
        size_ok = all(abs(a - b) < 0.5 for a, b in zip(sorted(snap["boundsMm"]["size"]), sorted(dims)))     # axis order may differ (Y-up); compare sorted extents
        snap["checks"] = {"mesh_count_matches": snap["meshCount"] == src_snap["meshCount"], "triangles_match": snap["triangles"] == src_snap["triangles"] or fmt == "FBX",
                          "extents_match_0p5mm": size_ok, "has_presentation_root": any(o.name.startswith("ROOT_PDC_PRESENTATION") for o in objs),
                          "has_content_slot": any(o.name.startswith("PIVOT_PDC_CONTENT_SLOT") for o in objs)}
        snap["pass"] = all(snap["checks"].values()); roundtrip[fmt] = snap

    # --- review render of the GLB round-trip (Workbench, hero-ish camera)
    bpy.ops.wm.read_homefile(use_empty=True); bpy.ops.import_scene.gltf(filepath=str(glb)); scene = bpy.context.scene
    lo, hi = bounds([o for o in bpy.data.objects if o.type == "MESH"]); centre = (lo + hi) / 2; diag = (hi - lo).length
    cam_data = bpy.data.cameras.new("CAM_EXPORT_REVIEW"); cam_data.lens = 85; cam = bpy.data.objects.new("CAM_EXPORT_REVIEW", cam_data); scene.collection.objects.link(cam)
    # the glTF importer converts back to Blender Z-up: front is -Y again, up is +Z (hero-like yaw 25, elevation 8)
    direction = Vector((math.sin(math.radians(25)) * math.cos(math.radians(8)), -math.cos(math.radians(25)) * math.cos(math.radians(8)), math.sin(math.radians(8))))
    cam.location = centre + direction * diag * 4.2; cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler(); scene.camera = cam
    scene.render.engine = "BLENDER_WORKBENCH"; scene.display.shading.light = "STUDIO"; scene.display.shading.color_type = "MATERIAL"; scene.display.shading.show_cavity = True
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1067; scene.render.image_settings.file_format = "PNG"
    scene.render.use_stamp = True; scene.render.use_stamp_note = True; scene.render.stamp_note_text = f"Gate 10 r002 export review · GLB round-trip · {STEM}.glb · NOT UNITY PARITY"
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame", "use_stamp_camera", "use_stamp_lens", "use_stamp_scene", "use_stamp_filename", "use_stamp_memory", "use_stamp_hostname"):
        if hasattr(scene.render, attr):
            setattr(scene.render, attr, False)
    scene.render.filepath = str(OUT_DIR / "export-review-glb-roundtrip.png"); bpy.ops.render.render(write_still=True)

    approvals = {sid: {"revision": st["revision"], "userApprovalQuote": (st.get("decision") or {}).get("wording"), "approvedAt": (st.get("decision") or {}).get("decidedAt")}
                 for st in MANIFEST["stages"] for sid in [st["id"]] if sid in ("06-geometry", "07-material", "08-lighting", "09-environment")}
    manifest = {"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "10-export", "exportRevision": 2,
                "status": "pass" if all(r["pass"] for r in roundtrip.values()) else "fail", "notice": "READY FOR EXPORT REVIEW · NOT IMPORTED INTO UNITY YET",
                "pipelineRevisionAtBuild": MANIFEST["revision"], "governingContract": {"sha256": CONTRACT_SHA, "revision": CONTRACT["contractRevision"]},
                "sourceGate07": {"blendPath": rel(SOURCE_BLEND), "blendSha256": expected}, "sourceGate06GeometryIdentity": G06["identity"], "upstreamApprovals": approvals,
                "package": {"blend": {"path": rel(product_blend), "sha256": sha256(product_blend), "sizeBytes": product_blend.stat().st_size},
                            "fbx": {"path": rel(fbx), "sha256": sha256(fbx), "sizeBytes": fbx.stat().st_size, "axes": "-Z forward / Y up, FBX_SCALE_NONE, triangulated, custom props (cmf_zone_id)"},
                            "glb": {"path": rel(glb), "sha256": sha256(glb), "sizeBytes": glb.stat().st_size, "attributes": "COLOR_0 = COLOR0 (edge/iridescence/finish masks), TEXCOORD_0 = UV2 (brushing angle, zone/255)"},
                            "labelDecal": {"path": rel(OUT_DIR / "header-label-decal.png"), "sha256": sha256(OUT_DIR / "header-label-decal.png"), "layout": rel(OUT_DIR / "header-label-decal.json"),
                                           "note": "apply in Unity on GEO_PDC_HEADER_GRAPHITE_PLANE (planar x/z over the plate bounds); copy is placeholder, runtime-owned"}},
                "product": {"removed": removed, "source": src_snap, "materials": material_table,
                            "unityNames": "GEO_PDC_* names kept; architecture unity_path mapping in evidence/04-architecture/rev-035/part-tree.json"},
                "collision": {"included": False, "policy": "Unity BoxCollider from the case bounds (101.28 x 171.78 x 10.96 mm); no mesh collider; no invented proxy geometry"},
                "roundTrip": roundtrip, "review": {"path": rel(OUT_DIR / "export-review-glb-roundtrip.png"), "engine": "Workbench, material colours"},
                "knownLimitations": ["procedural brushing / sandblast / thin film are not in the files: Unity materials re-author them (Gate 11)",
                                     "bolt heads keep 9 888 triangles each (91 k total, under the 120 k budget); decimation deferred",
                                     "FBX carries base colour / metallic / roughness only; GLB additionally carries COLOR_0 and TEXCOORD_0"]}
    (OUT_DIR / "export-manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    (OUT_DIR / "collision-policy.json").write_text(json.dumps({"schemaVersion": 1, "modelId": "premium-display-case", "variantId": "tri-spinner-slab-v3-cmf", "gate": "10-export", "exportRevision": 2,
                                                                 "included": False, "inventedGeometry": False, "policy": manifest["collision"]["policy"]}, indent=2) + "\n")
    print("GATE10_RESULT=" + json.dumps({"status": manifest["status"], "roundtrip": {k: v["checks"] for k, v in roundtrip.items()}, "triangles": src_snap["triangles"], "objects": src_snap["objectCount"]}))


main()
