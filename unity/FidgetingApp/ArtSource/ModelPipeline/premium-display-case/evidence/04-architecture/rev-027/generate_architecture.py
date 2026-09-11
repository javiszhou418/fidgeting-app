#!/usr/bin/env python3
"""Gate 04 rev-027: part tree, ownership and depth stack for tri-spinner-slab-v3-cmf.

Supersedes rev-026 after the user rejected Gate 05 rev-004 (2026-09-10).
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
CONTRACT_PATH = EVIDENCE / "03-contract" / "rev-005" / "modeling-contract.json"
HIERARCHY_PATH = EVIDENCE / "05-blockout" / "rev-005" / "scene-hierarchy.json"

UNITY_NAMES = {
    "GEO_PDC_REAR_PLATE": "RearPlate",
    "GEO_PDC_OUTER_CRYSTAL_FRAME": "OuterCrystalFrame",
    "GEO_PDC_SMOKE_INNER_LINER": "SmokeInnerLiner",
    "GEO_PDC_HEADER_SATIN_SHELF": "HeaderCompartment/HeaderSatinShelf",
    "GEO_PDC_HEADER_GRAPHITE_PLANE": "HeaderCompartment/HeaderGraphitePlane",
    "GEO_PDC_HEADER_MIRROR_BEVEL": "HeaderCompartment/HeaderMirrorBevel",
    "GEO_PDC_HEADER_SILVER_DATUM_RAIL": "HeaderCompartment/HeaderSilverDatumRail",
    "GEO_PDC_HEADER_GOLD_INLAY_L": "HeaderCompartment/HeaderGoldInlayL",
    "GEO_PDC_HEADER_GOLD_INLAY_R": "HeaderCompartment/HeaderGoldInlayR",
    "GEO_PDC_MAIN_SATIN_SHELF": "MainCompartment/MainSatinShelf",
    "GEO_PDC_MAIN_MICROBLAST_FIELD": "MainCompartment/MainMicroblastField",
    "GEO_PDC_MAIN_MIRROR_SEAM": "MainCompartment/MainMirrorSeam",
    "GEO_PDC_MAIN_BRUSHED_PANEL_L": "MainCompartment/MainBrushedPanelL",
    "GEO_PDC_MAIN_BRUSHED_PANEL_R": "MainCompartment/MainBrushedPanelR",
    "GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM": "MainCompartment/MainBrushedBandBottom",
    "GEO_PDC_POCKET_MIRROR_RIM": "MainCompartment/Pocket/PocketMirrorRim",
    "GEO_PDC_POCKET_SMOKE_WALL": "MainCompartment/Pocket/PocketSmokeWall",
    "GEO_PDC_POCKET_GRAPHITE_FLOOR": "MainCompartment/Pocket/PocketGraphiteFloor",
    "GEO_PDC_MAIN_GOLD_RAIL_00": "MainCompartment/MainGoldRail00",
    "GEO_PDC_MAIN_GOLD_RAIL_01": "MainCompartment/MainGoldRail01",
    "GEO_PDC_MAIN_GOLD_CHAMFER_TL": "MainCompartment/MainGoldChamferTL",
    "GEO_PDC_MAIN_GOLD_INDEX_TAB": "MainCompartment/MainGoldIndexTab",
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
        "GEO_PDC_OUTER_CRYSTAL_FRAME": [0.0, ds["z_frame_front"]],
        "GEO_PDC_SMOKE_INNER_LINER": [ds["z_backplate_front"] + sep, ds["z_frame_front"] - values["header.recess_depth_mm"]],
        "GEO_PDC_HEADER_SATIN_SHELF": [ds["z_backplate_front"] + sep, ds["z_shelf_top"]],
        "GEO_PDC_HEADER_MIRROR_BEVEL": [ds["z_backplate_front"] + sep, z_plate - values["header.recess_depth_mm"] * 0.5],
        "GEO_PDC_HEADER_GRAPHITE_PLANE": [ds["z_backplate_front"] + sep, z_plate],
        "GEO_PDC_HEADER_SILVER_DATUM_RAIL": [ds["z_backplate_front"] + sep, ds["z_shelf_top"] + values["interior.datum_rail_lift_mm"]],
        "GEO_PDC_HEADER_GOLD_INLAY_L": [ds["z_shelf_top"] - lift / 2, ds["z_shelf_top"] + relief],
        "GEO_PDC_HEADER_GOLD_INLAY_R": [ds["z_shelf_top"] - lift / 2, ds["z_shelf_top"] + relief],
        "GEO_PDC_MAIN_SATIN_SHELF": [ds["z_backplate_front"] + sep, ds["z_shelf_top"]],
        "GEO_PDC_MAIN_MIRROR_SEAM": [ds["z_backplate_front"] + sep, z_field - values["main.recess_depth_mm"] * 0.25],
        "GEO_PDC_MAIN_MICROBLAST_FIELD": [ds["z_backplate_front"] + sep, z_field],
        "GEO_PDC_MAIN_BRUSHED_PANEL_L": [z_field - lift / 2, z_field + lift],
        "GEO_PDC_MAIN_BRUSHED_PANEL_R": [z_field - lift / 2, z_field + lift],
        "GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM": [z_field - lift / 2, z_field + lift],
        "GEO_PDC_POCKET_MIRROR_RIM": [z_field - values["main.recess_depth_mm"] * 0.25, z_field],
        "GEO_PDC_POCKET_SMOKE_WALL": [ds["z_pocket_floor"], z_field],
        "GEO_PDC_POCKET_GRAPHITE_FLOOR": [ds["z_backplate_front"] + sep, ds["z_pocket_floor"]],
        "GEO_PDC_MAIN_GOLD_RAIL_00": [z_field - lift / 2, z_field + relief],
        "GEO_PDC_MAIN_GOLD_RAIL_01": [z_field - lift / 2, z_field + relief],
        "GEO_PDC_MAIN_GOLD_CHAMFER_TL": [z_field - lift / 2, z_field + relief],
        "GEO_PDC_MAIN_GOLD_INDEX_TAB": [z_field - lift / 2, z_field + relief],
    }
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
            "owner": "case",
            "parent_part": name[: -len("_SOCKET_FLOOR")] if name.endswith("_SOCKET_FLOOR") else None,
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
        "schema": "premium-display-case.gate04.part-tree/3",
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
        "core_object_list_matches_contract": sorted(p["blender_name"] for p in parts if p["parent_part"] is None)
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
        ],
        "depth_stack_mm": ds,
        "inputs": {"contract": str(CONTRACT_PATH.relative_to(EVIDENCE.parents[3])), "contract_sha256_file": sha256(CONTRACT_PATH),
                   "scene_hierarchy": str(HIERARCHY_PATH.relative_to(EVIDENCE.parents[3])), "scene_hierarchy_sha256": sha256(HIERARCHY_PATH)},
    }
    (HERE / "part-tree.json").write_text(json.dumps(part_tree, indent=2) + "\n")

    exploded = {
        "schema": "premium-display-case.gate04.exploded-plan/3",
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
    d.text((30, 24), "Gate 04 rev-027  premium-display-case / tri-spinner-slab-v3-cmf  architecture", fill=(235, 235, 235), font=font)
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
                     ("field", ds["z_field"]), ("header plane", ds["z_header_plane"]), ("shelf top", ds["z_shelf_top"]),
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
