#!/usr/bin/env python3
"""Gate 04 rev-034: part tree, ownership and depth stack for tri-spinner-slab-v3-cmf.

rev-034 follows contract rev-012 / blockout rev-012: header divider line and trait fill strips retired (printed rule -> decal;
TRAIT PROFILE -> runtime UI on the flat plaque), compartment seam polished (zone 6) and flush with the shelf, bands 2.8 mm,
island chamfers 3.5 mm.

rev-033 follows contract rev-011 / blockout rev-011 (lighting direction + muted palette; geometry = rev-009).

rev-032 follows contract rev-010 / blockout rev-010 (soft_focus ranges only; geometry = rev-009).

rev-031 follows contract rev-009 / blockout rev-009: the four corner wings are
retired (user 2026-09-10 15:19 "把这四个角去掉吧，有点太复杂了"); the MainCompartment
loses its Wings group; everything else is unchanged from rev-030.

rev-030 (kept):

Supersedes rev-029 after the user rejected Gate 05 rev-007 (2026-09-10 13:39) and
decided: uniform offsets / four mirrored wings / CMF scheme A. Wings become
GEO_PDC_MAIN_WING_{TL,TR,BL,BR} (zone 6), gold accents are mirrored, the trait
plaque moves to zone 4.

rev-029 (kept): after the user's Gate 05 rev-006 refinement (2026-09-10 12:22/12:23):
the bottom brushed band becomes the TRAIT PROFILE plaque (FDB-DSP-053) with
three runtime-dynamic fill strips owned by the trait block at runtime.

rev-028 (kept): after the user's Gate 05 rev-005 feedback (2026-09-10 11:15):
retires the silver datum rail, adds the compartment seam, header divider line,
raised polished pocket lip (replaces the sunken mirror rim), three clear clips,
and the stepped crystal-frame ledge.

rev-027 (kept): after the user rejected Gate 05 rev-004 (2026-09-10).
Adds the generic circular pocket (rim / wall / floor), the six counterbored
frame bolts with hexagonal socket floors, the gold chamfer bar, and drops the
retired GEO_PDC_MAIN_CORNER_FACETS.

Reads the Gate 03 rev-005 contract and the Gate 05 rev-005 scene hierarchy
emitted by `tools/blender/build_tri_spinner_slab.py`, and writes:

- part-tree.json        ownership, pivots, export roles, CMF zone ids, z-stack
- exploded-plan.json    INTERNAL technical layer order (never a review artifact;
                        the Premium Display Case whole-case gate forbids explode
                        views in user previews)
- architecture-board.png  hierarchy + depth-stack board for review
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[1]
CONTRACT_PATH = EVIDENCE / "03-contract" / "rev-012" / "modeling-contract.json"
HIERARCHY_PATH = EVIDENCE / "05-blockout" / "rev-012" / "scene-hierarchy.json"

UNITY_NAMES = {
    "GEO_PDC_REAR_PLATE": "RearPlate",
    "GEO_PDC_OUTER_CRYSTAL_FRAME": "OuterCrystalFrame",
    "GEO_PDC_SMOKE_INNER_LINER": "SmokeInnerLiner",
    "GEO_PDC_HEADER_SATIN_SHELF": "HeaderCompartment/HeaderSatinShelf",
    "GEO_PDC_HEADER_GRAPHITE_PLANE": "HeaderCompartment/HeaderGraphitePlane",
    "GEO_PDC_HEADER_MIRROR_BEVEL": "HeaderCompartment/HeaderMirrorBevel",
    "GEO_PDC_COMPARTMENT_SEAM": "CompartmentSeam",
    "GEO_PDC_HEADER_GOLD_INLAY_L": "HeaderCompartment/HeaderGoldInlayL",
    "GEO_PDC_HEADER_GOLD_INLAY_R": "HeaderCompartment/HeaderGoldInlayR",
    "GEO_PDC_MAIN_SATIN_SHELF": "MainCompartment/MainSatinShelf",
    "GEO_PDC_MAIN_MICROBLAST_FIELD": "MainCompartment/MainMicroblastField",
    "GEO_PDC_MAIN_MIRROR_SEAM": "MainCompartment/MainMirrorSeam",
    "GEO_PDC_MAIN_TRAIT_PLAQUE": "MainCompartment/TraitPlaque",
    "GEO_PDC_POCKET_POLISHED_LIP": "MainCompartment/Pocket/PocketPolishedLip",
    "GEO_PDC_POCKET_CLIP_00": "MainCompartment/Pocket/PocketClip00",
    "GEO_PDC_POCKET_CLIP_01": "MainCompartment/Pocket/PocketClip01",
    "GEO_PDC_POCKET_CLIP_02": "MainCompartment/Pocket/PocketClip02",
    "GEO_PDC_POCKET_SMOKE_WALL": "MainCompartment/Pocket/PocketSmokeWall",
    "GEO_PDC_POCKET_GRAPHITE_FLOOR": "MainCompartment/Pocket/PocketGraphiteFloor",
    "GEO_PDC_MAIN_GOLD_RAIL_L": "MainCompartment/Gold/RailL",
    "GEO_PDC_MAIN_GOLD_RAIL_R": "MainCompartment/Gold/RailR",
    "GEO_PDC_MAIN_GOLD_CHAMFER_TL": "MainCompartment/Gold/ChamferTL",
    "GEO_PDC_MAIN_GOLD_CHAMFER_TR": "MainCompartment/Gold/ChamferTR",
    "GEO_PDC_MAIN_GOLD_CHAMFER_BL": "MainCompartment/Gold/ChamferBL",
    "GEO_PDC_MAIN_GOLD_CHAMFER_BR": "MainCompartment/Gold/ChamferBR",
    "GEO_PDC_MAIN_GOLD_INDEX_TAB_L": "MainCompartment/Gold/IndexTabL",
    "GEO_PDC_MAIN_GOLD_INDEX_TAB_R": "MainCompartment/Gold/IndexTabR",
}
for _i in range(6):
    UNITY_NAMES[f"GEO_PDC_FRAME_BOLT_{_i:02d}"] = f"Hardware/FrameBolt{_i:02d}"
    UNITY_NAMES[f"GEO_PDC_FRAME_BOLT_{_i:02d}_SOCKET_FLOOR"] = f"Hardware/FrameBolt{_i:02d}/SocketFloor"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text())
    hierarchy = json.loads(HIERARCHY_PATH.read_text())
    values = {p["id"]: p.get("value") for p in contract["parameters"]["inputs"]}
    values.update({k: v["value"] for k, v in contract["resolved"].items()})
    zones = {m["slot"]: {"name": m["id"], "material": m["id"]} for m in contract["materials"]["materials"]}
    ds = contract["depth_stack_mm"]
    z_field = ds["z_field"]
    z_plate = ds["z_header_plane"]
    z_frame = ds["z_frame_front"]
    lift = values["interior.part_lift_mm"]
    relief = values["cmf.gold_relief_mm"]
    sep = contract["geometry_builder"]["minimum_render_separation_mm"]
    bore_d = values["hardware.bolt_counterbore_depth_mm"]
    head_top = z_frame - values["hardware.bolt_head_below_frame_front_mm"]
    head_bot = z_frame - bore_d + sep
    z_ranges = {
        "GEO_PDC_REAR_PLATE": [0.0, ds["z_backplate_front"]],
        "GEO_PDC_OUTER_CRYSTAL_FRAME": [0.0, ds["z_frame_front"]],   # inner ledge steps to ds["z_frame_ledge"]
        "GEO_PDC_SMOKE_INNER_LINER": [ds["z_backplate_front"] + sep, ds["z_frame_front"] - values["header.recess_depth_mm"]],
        "GEO_PDC_HEADER_SATIN_SHELF": [ds["z_backplate_front"] + sep, ds["z_shelf_top"]],
        "GEO_PDC_HEADER_MIRROR_BEVEL": [ds["z_backplate_front"] + sep, z_plate - values["header.recess_depth_mm"] * 0.5],
        "GEO_PDC_HEADER_GRAPHITE_PLANE": [ds["z_backplate_front"] + sep, z_plate],
        "GEO_PDC_COMPARTMENT_SEAM": [ds["z_backplate_front"] + sep, ds["z_shelf_top"]],      # rev-034: polished band flush with the shelf
        "GEO_PDC_HEADER_GOLD_INLAY_L": [ds["z_shelf_top"] - lift / 2, ds["z_shelf_top"] + relief],
        "GEO_PDC_HEADER_GOLD_INLAY_R": [ds["z_shelf_top"] - lift / 2, ds["z_shelf_top"] + relief],
        "GEO_PDC_MAIN_SATIN_SHELF": [ds["z_backplate_front"] + sep, ds["z_shelf_top"]],
        "GEO_PDC_MAIN_MIRROR_SEAM": [ds["z_backplate_front"] + sep, z_field - values["main.recess_depth_mm"] * 0.25],
        "GEO_PDC_MAIN_MICROBLAST_FIELD": [ds["z_backplate_front"] + sep, z_field],
        "GEO_PDC_MAIN_TRAIT_PLAQUE": [z_field - 0.3, z_field + lift],
        "GEO_PDC_POCKET_POLISHED_LIP": [ds["z_backplate_front"] + sep, ds["z_pocket_lip_top"]],
        "GEO_PDC_POCKET_SMOKE_WALL": [ds["z_backplate_front"] + sep, z_field - values["main.pocket_lip_inner_drop_mm"]],
        "GEO_PDC_POCKET_GRAPHITE_FLOOR": [ds["z_backplate_front"] + sep, ds["z_pocket_floor"]],
        **{f"GEO_PDC_MAIN_GOLD_{n}": [z_field - 0.3, z_field + relief] for n in
           ("RAIL_L", "RAIL_R", "CHAMFER_TL", "CHAMFER_TR", "CHAMFER_BL", "CHAMFER_BR", "INDEX_TAB_L", "INDEX_TAB_R")},
    }
    for i in range(int(values["hardware.clip_count"])):
        z_ranges[f"GEO_PDC_POCKET_CLIP_{i:02d}"] = [z_field + 0.05, z_field + 0.05 + values["hardware.clip_size_mm"][2]]
    for i in range(values["hardware.bolt_count"]):
        z_ranges[f"GEO_PDC_FRAME_BOLT_{i:02d}"] = [head_bot, head_top]
        z_ranges[f"GEO_PDC_FRAME_BOLT_{i:02d}_SOCKET_FLOOR"] = [head_bot, head_top - values["hardware.bolt_socket_depth_mm"]]
    parts = []
    for node in hierarchy:
        name = node["name"]
        if not name.startswith("GEO_PDC_") or name.startswith("GEO_PDC_REVIEW_SPINNER"):
            continue
        parts.append({
            "blender_name": name,
            "unity_path": "PresentationRoot/CaseAssembly/" + UNITY_NAMES[name],
            "owner": "runtime-trait-block" if name.startswith("GEO_PDC_TRAIT_FILL_") else "case",
            "parent_part": (name[: -len("_SOCKET_FLOOR")] if name.endswith("_SOCKET_FLOOR")
                            else "GEO_PDC_MAIN_TRAIT_PLAQUE" if name.startswith("GEO_PDC_TRAIT_FILL_") else None),
            "export_role": node["export_role"],
            "collection": node["collections"][0],
            "z_range_construction_mm": [round(z, 3) for z in z_ranges[name]],
            "z_range_canonical_mm": [round(z + ds["root_recentering_z"], 3) for z in z_ranges[name]],
            "cmf_zone_id": None,
        })
    # zone ids come from the builder's stamped custom property, not a second table
    zone_by_name = {n["name"]: n["cmf_zone_id"] for n in hierarchy if n.get("cmf_zone_id")}
    for p in parts:
        p["cmf_zone_id"] = zone_by_name[p["blender_name"]]
        p["cmf_zone"] = zones[p["cmf_zone_id"]]["name"]
        p["material_slot"] = zones[p["cmf_zone_id"]]["material"]

    controls = [n for n in hierarchy if n["name"].startswith(("ROOT_PDC_", "PIVOT_PDC_"))]
    slot = next(n for n in controls if n["name"] == "PIVOT_PDC_CONTENT_SLOT")
    part_tree = {
        "schema": "premium-display-case.gate04.part-tree/10",
        "modelId": contract["model_id"],
        "variant_id": contract["variant_id"],
        "contract_sha256": contract["hashing"]["contract_sha256"],
        "coordinate_system": contract["coordinate_system"]["canonical_product"],
        "controls": [{
            "name": n["name"], "unity_name": {"ROOT_PDC_PRESENTATION": "PresentationRoot",
                                              "ROOT_PDC_CASE_ASSEMBLY": "CaseAssembly", "PIVOT_PDC_CONTENT_SLOT": "ContentSlot",
                                              "PIVOT_PDC_TURNTABLE": "(review only, not exported)"}[n["name"]],
            "export_role": n["export_role"], "location_canonical_mm": n["location_canonical_mm"],
        } for n in controls],
        "content_slot": {
            "name": "PIVOT_PDC_CONTENT_SLOT",
            "location_canonical_mm": slot["location_canonical_mm"],
            "owner": "caller",
            "rule": "content_owner=caller; case_export_contains_spinner_mesh=false; ContentSlot is an empty at the spinner pivot",
            "review_input": {"source": next(s for s in contract["sources"] if s["id"] == "src.spinner_mesh")["path"],
                             "sha256": next(s for s in contract["sources"] if s["id"] == "src.spinner_mesh")["sha256"],
                             "collection": "COL_PDC_REFERENCE_LOCKED", "exported": False,
                             "pose": "spin axis = canonical +Z, one tip up (+Y), pivot at ContentSlot"},
        },
        "parts": parts,
        "part_count": len(parts),
        "core_part_count": len([p for p in parts if p["parent_part"] is None]),
        "core_object_list_matches_contract": sorted(p["blender_name"] for p in parts
                                                    if p["parent_part"] is None or p["blender_name"].startswith("GEO_PDC_TRAIT_FILL_"))
                                             == sorted(contract["scene"]["core_geometry_objects"]),
        "sub_parts": [p["blender_name"] for p in parts if p["parent_part"] is not None],
        "ownership_rules": [
            "The case export contains only GEO_PDC_* case parts plus ROOT_PDC_CASE_ASSEMBLY and PIVOT_PDC_CONTENT_SLOT.",
            "PIVOT_PDC_CONTENT_SLOT is an empty. The spinner mesh, its materials, pivot, physics and haptics stay caller-owned.",
            "ROOT_PDC_PRESENTATION owns turntable/idle motion; ROOT_PDC_CASE_ASSEMBLY never animates.",
            "No explode, assembly or layer-separation state exists in exported controls.",
            "The pocket is a generic circular well (rim / smoke wall / graphite floor) sized from content.design_toy_diameter_mm + fit clearance; "
            "it is not shaped to any one spinner silhouette.",
            "Frame bolts are case hardware (zone 5 steel); each SocketFloor is a sub-part of its bolt head.",
            "Every nested outline is a concentric inward offset of its parent (nested_offset_rule); no independent corner radii except interior.bezel_corner_radius_mm.",
            "Header and main compartments are separate steel islands; CompartmentSeam is the dark smoke floor between them (no bridging rail).",
            "Pocket clips are visual case parts in the clear-crystal zone; retention.mechanism remains null and no mechanical claim is made.",
            "Engraved grooves are cut into MainMicroblastField and are not separate parts.",
            "TraitPlaque hosts the FDB-DSP-053 TRAIT PROFILE: three troughs SPIN / FEEL / CRAFT top-down with quartile ticks. TraitFill* are exported "
            "at full length and shortened at runtime from ToyTalentCatalog.cs; label/value text are decals, not geometry.",
            "Uniform-offset rule: main bezel -> field -> groove are exact offsets of one chamfered outline; band widths equal everywhere.",
            "rev-031: no wings (retired GEO_PDC_MAIN_WING_{TL,TR,BL,BR}); the field around the pocket is plain; gold accents mirrored L/R and T/B.",
            "CMF scheme A zones: lip/bevels/seam 6 (mirror), trait plaque 4 (piano black, flat runtime-UI region), field 3 (dark sandblast), shelves 5 (brushed).",
            "rev-034: no header divider line (printed rule -> Gate 07 decal); no trait fill strips (TRAIT PROFILE drawn at runtime); seam flush with the shelf top.",
            "Rarity CMF (FDB-DSP-059, contract cmf.rarity_tier_map): zones 5/6/7 + liner tint follow the tier; 1/3/4 constant. Gate 07 sets values.",
        ],
        "depth_stack_mm": ds,
        "inputs": {"contract": str(CONTRACT_PATH.relative_to(EVIDENCE.parents[3])), "contract_sha256_file": sha256(CONTRACT_PATH),
                   "scene_hierarchy": str(HIERARCHY_PATH.relative_to(EVIDENCE.parents[3])), "scene_hierarchy_sha256": sha256(HIERARCHY_PATH)},
    }
    (HERE / "part-tree.json").write_text(json.dumps(part_tree, indent=2) + "\n")

    exploded = {
        "schema": "premium-display-case.gate04.exploded-plan/10",
        "visibility": "INTERNAL_TECHNICAL_ONLY",
        "rule": "Never a review artifact or user preview (Premium Display Case whole-case gate). Layer order is documentation of the "
                "z-stack; no explode animation, control or export state exists.",
        "layers_rear_to_front": sorted(
            [{"blender_name": p["blender_name"], "z_range_construction_mm": p["z_range_construction_mm"]} for p in parts],
            key=lambda p: (p["z_range_construction_mm"][1], p["z_range_construction_mm"][0])),
        "caller_content": {"name": "review spinner", "z_range_construction_mm": [ds["z_spinner_back"], ds["z_spinner_front"]],
                           "protrudes_past_frame_front_mm": ds["spinner_protrusion"]},
    }
    (HERE / "exploded-plan.json").write_text(json.dumps(exploded, indent=2) + "\n")

    # Board
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
        small = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 16)
    except OSError:
        font = small = ImageFont.load_default()
    W_, H_ = 1800, 1400
    img = Image.new("RGB", (W_, H_), (24, 25, 28))
    d = ImageDraw.Draw(img)
    d.text((30, 24), "Gate 04 rev-034  premium-display-case / tri-spinner-slab-v3-cmf  architecture", fill=(235, 235, 235), font=font)
    d.text((30, 52), f"contract {contract['hashing']['contract_sha256'][:16]}  PROVISIONAL_DIMENSIONS  (no explode view: internal z-stack only)",
           fill=(180, 180, 180), font=small)
    y = 100
    for n in hierarchy:
        if n["name"].startswith("GEO_PDC_REVIEW_SPINNER") and n["depth"] > 3:
            continue
        colour = (255, 214, 120) if n["name"].startswith(("ROOT_", "PIVOT_")) else (200, 205, 215)
        if n["name"].startswith("GEO_PDC_REVIEW_SPINNER"):
            colour = (140, 170, 200)
        d.text((30 + 26 * n["depth"], y), n["name"], fill=colour, font=small)
        y += 22
        if y > H_ - 40:
            break
    # depth stack
    x0, x1 = 1000, 1740
    scale = 640 / ds["z_spinner_front"]
    base_y = 1300
    d.text((x0, 100), "depth stack (construction z, mm; rear outer face = 0)", fill=(235, 235, 235), font=small)
    for p in sorted(parts, key=lambda p: p["z_range_construction_mm"][1]):
        z0, z1 = p["z_range_construction_mm"]
        yy0, yy1 = base_y - z1 * scale, base_y - z0 * scale
        d.rectangle([x0 + 40, yy0, x0 + 40 + 60, yy1], outline=(120, 130, 150))
    for label, z in (("backplate front", ds["z_backplate_front"]), ("spinner back", ds["z_spinner_back"]), ("pocket floor", ds["z_pocket_floor"]),
                     ("field", ds["z_field"]), ("lip top", ds["z_pocket_lip_top"]), ("header plane", ds["z_header_plane"]), ("shelf top", ds["z_shelf_top"]),
                     ("frame ledge", ds["z_frame_ledge"]),
                     ("frame front", ds["z_frame_front"]), ("spinner front", ds["z_spinner_front"])):
        yy = base_y - z * scale
        d.line([x0 + 30, yy, x1, yy], fill=(90, 200, 140), width=1)
        d.text((x0 + 120, yy - 18), f"{label}  z={z}", fill=(160, 230, 180), font=small)
    d.text((x0, 1330), f"protrusion {ds['spinner_protrusion']} mm  envelope depth {ds['assembled_envelope_depth']} mm", fill=(235, 235, 235), font=small)
    img.save(HERE / "architecture-board.png")
    print(json.dumps({"parts": len(parts), "core_parts": part_tree["core_part_count"], "core_match": part_tree["core_object_list_matches_contract"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
