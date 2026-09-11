#!/usr/bin/env python3
"""Gate 03 rev-004: resolve the V3 slab modeling contract.

Inputs
- Gate 01 rev-004 copy of `tri-spinner-slab-model-spec.v0.json` (user document).
- Gate 02 rev-007 `v3-proportion-analysis.json` (clean-image ratio recheck).
- Gate 02 rev-007 `spinner-source-measurement.json` (caller-owned source model).

Output
- `modeling-contract.json`: every parameter with `evidence_class` and
  `value_state`; derived values evaluated from the typed formula AST (no
  eval); depth stack; assertions; RFC 8785-style contract SHA-256.
- `contract-validation.json`: assertion results.

Rules honoured: unknown stays null; provisional values never become
measured; measured values come only from the source model; the old
228 x 304 x 59 mm contract is not reused.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parents[1]
INTAKE = EVIDENCE / "01-intake" / "rev-004"
ANALYSIS = EVIDENCE / "02-analysis" / "rev-007"
SPEC_PATH = INTAKE / "tri-spinner-slab-model-spec.v0.json"
PROPORTIONS_PATH = ANALYSIS / "v3-proportion-analysis.json"
SPINNER_PATH = ANALYSIS / "spinner-source-measurement.json"
REPO_REL = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence"

SOURCE_CLAIM_IDS = [
    "pdc-v3-analysis-outer-ratio-r007",
    "pdc-v3-analysis-header-seam-r007",
    "pdc-v3-analysis-spinner-placement-r007",
    "pdc-v3-analysis-pocket-span-r007",
    "pdc-v3-analysis-spinner-source-dimensions-r007",
    "pdc-v3-analysis-partial-depth-no-front-cover-r007",
    "pdc-v3-analysis-old-contract-invalid-r007",
    "pdc-v3-analysis-unknowns-r007",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value) -> str:
    """RFC 8785-style canonicalisation for the value shapes used here:
    sorted keys, no whitespace, integral floats printed as integers."""
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(k, ensure_ascii=False)}:{canonical_json(value[k])}" for k in sorted(value)) + "}"
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(v) for v in value) + "]"
    if isinstance(value, bool) or value is None:
        return json.dumps(value)
    if isinstance(value, float):
        if math.isfinite(value) and value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return repr(value)
    if isinstance(value, int):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def contract_hash(contract: dict) -> str:
    clone = json.loads(json.dumps(contract))
    clone["hashing"]["contract_sha256"] = None
    return hashlib.sha256(canonical_json(clone).encode("utf-8")).hexdigest()


class Unresolved(Exception):
    pass


def evaluate(node, values: dict, stack: tuple = ()):
    if "ref" in node:
        ref = node["ref"]
        if ref in stack:
            raise ValueError(f"cycle: {' -> '.join(stack + (ref,))}")
        if ref not in values:
            raise KeyError(ref)
        value = values[ref]
        if value is None:
            raise Unresolved(ref)
        return value
    if "value" in node:
        return node["value"]
    op = node["op"]
    args = [evaluate(a, values, stack) for a in node["args"]]
    if op == "add":
        return sum(args)
    if op == "sub":
        return args[0] - sum(args[1:])
    if op == "mul":
        out = 1.0
        for a in args:
            out *= a
        return out
    if op == "div":
        return args[0] / args[1]
    if op == "min":
        return min(args)
    if op == "max":
        return max(args)
    if op == "neg":
        return -args[0]
    raise ValueError(f"unknown op {op}")


def set_input(inputs: dict, pid: str, **fields) -> None:
    if pid not in inputs:
        raise KeyError(pid)
    inputs[pid].update(fields)


def add_input(inputs: dict, order: list, pid: str, **fields) -> None:
    if pid in inputs:
        raise KeyError(f"duplicate {pid}")
    inputs[pid] = {"id": pid, **fields}
    order.append(pid)


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text())
    proportions = json.loads(PROPORTIONS_PATH.read_text())
    spinner = json.loads(SPINNER_PATH.read_text())
    ratios_clean = proportions["images"][0]["ratios"]
    ratios_chat = proportions["images"][1]["ratios"]
    mean = lambda k: round((ratios_clean[k] + ratios_chat[k]) / 2, 4)  # noqa: E731
    sm = spinner["measurements_mm"]
    spinner_source = spinner["source"]

    inputs = {p["id"]: dict(p) for p in spec["parameters"]["inputs"]}
    order = [p["id"] for p in spec["parameters"]["inputs"]]
    recheck = {"source_id": "src.v3_clean_recheck_r007", "supersedes": "annotated 416x654 reading"}

    # --- visual ratios rechecked on the clean V3 images (still concept readings)
    set_input(inputs, "visual.case_width_over_height", value=mean("case_width_over_height"), **recheck,
              note="Spec 0.562 came from the annotated screenshot; both clean images read 0.589-0.590.")
    set_input(inputs, "visual.header_split_from_top", value=mean("header_seam_from_top"), **recheck,
              note="Dark seam under the header plate rail. The silver datum rail band runs from this seam to main_bay_start.")
    add_input(inputs, order, "visual.main_bay_start_from_top", data_type="number", unit="ratio",
              value=mean("main_bay_start_from_top"), evidence_class="recommended_start", value_state="provisional",
              tolerance=0.006, **recheck)
    set_input(inputs, "visual.spinner_center_x_from_left", value=0.5,
              note="Highlight-biased centroid read 0.484; horizontal centring is the design intent and is kept at 0.500.")
    # The concept spinner is flatter than the real equilateral rotor: with the
    # measured 65 mm tip circle a hub at 0.637H would push the top tip into the
    # header rail. Keep the image reading on record and derive the centre from
    # the main-field fit instead (see derived `spinner.center_y_mm`).
    image_center = inputs.pop("visual.spinner_center_from_top")
    order.remove("visual.spinner_center_from_top")
    add_input(inputs, order, "visual.spinner_center_from_top_image_reading", data_type="number", unit="ratio",
              value=mean("spinner_center_from_top"), evidence_class="recommended_start", value_state="provisional",
              tolerance=image_center.get("tolerance", 0.008), **recheck,
              note="Not used for placement: infeasible with the measured spinner. Superseded by derived spinner.center_y_mm.")
    add_input(inputs, order, "main.pocket_vertical_margin_split", data_type="number", unit="ratio", value=0.5,
              evidence_class="recommended_start", value_state="provisional",
              note="Share of the spare field height placed above the pocket (0.5 = pocket centred vertically in the field).")
    add_input(inputs, order, "visual.spinner_pocket_span_over_width", data_type="number", unit="ratio",
              value=mean("spinner_pocket_span_over_width"), evidence_class="recommended_start",
              value_state="provisional", tolerance=0.01, **recheck,
              note="Dark recess outline around the spinner, not the tip span.")

    # --- spinner: measured from the caller-owned source model
    set_input(inputs, "spinner.max_span_mm", value=sm["horizontal_span_one_tip_up"], provisional_value=None,
              evidence_class="measured", value_state="measured", source_id="src.spinner_mesh",
              measurement="bbox X of UnifiedTriSpinner.glb in the one-tip-up pose",
              span_basis="bbox_x_one_tip_up",
              alternative_tip_circle_diameter_mm=sm["tip_circle_diameter"],
              note="The 85 mm provisional value is retired. Tip-circle 65.0 mm is recorded as the alternative basis for the user's Gate 03 decision.")
    for key in ("provisional_use", "blocks_manufacturing_claims"):
        inputs["spinner.max_span_mm"].pop(key, None)
    set_input(inputs, "spinner.max_thickness_mm", value=sm["max_thickness_including_caps"], provisional_value=None,
              evidence_class="measured", value_state="measured", source_id="src.spinner_mesh",
              measurement="assembly bbox Z including both finger caps")
    inputs["spinner.max_thickness_mm"].pop("blocks_gates_from", None)
    add_input(inputs, order, "spinner.tip_circle_diameter_mm", data_type="number", unit="mm",
              value=sm["tip_circle_diameter"], evidence_class="measured", value_state="measured",
              source_id="src.spinner_mesh")
    add_input(inputs, order, "spinner.rotor_body_thickness_mm", data_type="number", unit="mm",
              value=sm["rotor_body_thickness"], evidence_class="measured", value_state="measured",
              source_id="src.spinner_mesh")
    add_input(inputs, order, "spinner.pivot_at_mid_thickness", data_type="boolean", unit="none",
              value=bool(sm["pivot_z_is_mid_thickness"]), evidence_class="measured", value_state="measured",
              source_id="src.spinner_mesh")

    # --- structure: shelf scales with W; pocket and interior depth are new blockout starts
    inputs.pop("main.perimeter_shelf_width_mm")
    order.remove("main.perimeter_shelf_width_mm")
    add_input(inputs, order, "main.perimeter_shelf_over_width", data_type="number", unit="ratio", value=0.045,
              range=[0.040, 0.052], evidence_class="recommended_start", value_state="provisional",
              note="Replaces the fixed 4.5 mm, which was sized for the retired 111.55 mm provisional width.")
    add_input(inputs, order, "main.pocket_gap_mm", data_type="number", unit="mm", value=2.0, range=[1.5, 3.5],
              evidence_class="recommended_start", value_state="provisional", manufacturing_clearance=False,
              note="Visual gap between spinner tip and dark pocket wall. Not a retention or manufacturing clearance.")
    add_input(inputs, order, "main.pocket_lobe_radius_mm", data_type="number", unit="mm", value=4.0, range=[3.0, 6.0],
              evidence_class="recommended_start", value_state="provisional",
              note="Pocket outline = convex hull of three lobes on the tip circle; concave sides deferred to Gate 06.")
    add_input(inputs, order, "interior.shelf_top_below_frame_front_mm", data_type="number", unit="mm", value=3.0,
              range=[2.0, 4.5], evidence_class="recommended_start", value_state="provisional",
              note="Depth of the crystal lip above the satin shelves. Sets pocket depth = shelf top - backplate front.")
    add_input(inputs, order, "interior.part_lift_mm", data_type="number", unit="mm", value=0.2, range=[0.15, 0.3],
              evidence_class="recommended_start", value_state="provisional",
              note="Raised brushed panels/band above the microblast field; also the render separation for interior parts.")
    add_input(inputs, order, "interior.datum_rail_lift_mm", data_type="number", unit="mm", value=0.2,
              range=[0.1, 0.4], evidence_class="recommended_start", value_state="provisional")
    add_input(inputs, order, "header.plate_side_inset_mm", data_type="number", unit="mm", value=1.5, range=[1.0, 2.5],
              evidence_class="recommended_start", value_state="provisional",
              note="Graphite plate inset from the header shelf edge, in addition to the mirror bevel width.")
    set_input(inputs, "cmf.gold_inlay_width_mm", value=0.35,
              note="Blockout uses the range maximum so the inlays read at 2048 px; the clean image reads ~0.4-0.5 mm.")

    values = {pid: p.get("value") for pid, p in inputs.items()}

    derived_specs = [d for d in spec["parameters"]["derived"] if d["id"] != "spinner.center_y_mm"]
    ref = lambda i: {"ref": i}  # noqa: E731
    const = lambda v: {"value": v, "unit": "ratio"}  # noqa: E731
    derived_specs += [
        {"id": "main.liner_inset_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("case.crystal_wall_mm"), ref("case.smoke_liner_mm"),
                                              const(0.02)]},
         "dependencies": ["case.crystal_wall_mm", "case.smoke_liner_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived",
         "note": "crystal wall + 0.02 mm render separation + liner"},
        {"id": "main.field_top_y_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [
             {"op": "mul", "args": [ref("case.height_mm"), {"op": "sub", "args": [const(0.5), ref("visual.main_bay_start_from_top")]}]},
             ref("main.perimeter_shelf_width_mm")]},
         "dependencies": ["case.height_mm", "visual.main_bay_start_from_top", "main.perimeter_shelf_width_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "main.field_bottom_y_mm", "unit": "mm",
         "expression": {"op": "add", "args": [{"op": "mul", "args": [const(-0.5), ref("case.height_mm")]},
                                              ref("main.liner_inset_mm"), ref("main.perimeter_shelf_width_mm")]},
         "dependencies": ["case.height_mm", "main.liner_inset_mm", "main.perimeter_shelf_width_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "main.pocket_reach_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("main.pocket_lobe_center_radius_mm"), ref("main.pocket_lobe_radius_mm")]},
         "dependencies": ["main.pocket_lobe_center_radius_mm", "main.pocket_lobe_radius_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "centre to top of the upper lobe"},
        {"id": "main.pocket_height_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("main.pocket_reach_mm"),
                                              {"op": "mul", "args": [ref("main.pocket_lobe_center_radius_mm"), const(0.5)]},
                                              ref("main.pocket_lobe_radius_mm")]},
         "dependencies": ["main.pocket_reach_mm", "main.pocket_lobe_center_radius_mm", "main.pocket_lobe_radius_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "lower lobes sit at sin(30 deg) = 0.5 of the lobe-centre radius below the hub"},
        {"id": "spinner.center_y_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [
             ref("main.field_top_y_mm"),
             {"op": "mul", "args": [ref("main.pocket_vertical_margin_split"),
                                    {"op": "sub", "args": [{"op": "sub", "args": [ref("main.field_top_y_mm"), ref("main.field_bottom_y_mm")]},
                                                           ref("main.pocket_height_mm")]}]},
             ref("main.pocket_reach_mm")]},
         "dependencies": ["main.field_top_y_mm", "main.field_bottom_y_mm", "main.pocket_height_mm", "main.pocket_reach_mm",
                          "main.pocket_vertical_margin_split"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "Replaces the spec's image-ratio placement; centres the pocket in the main field."},
        {"id": "visual.spinner_center_from_top", "unit": "ratio",
         "expression": {"op": "sub", "args": [const(0.5), {"op": "div", "args": [ref("spinner.center_y_mm"), ref("case.height_mm")]}]},
         "dependencies": ["spinner.center_y_mm", "case.height_mm"], "round_to": 0.0001,
         "evidence_class": "derived", "value_state": "derived"},
        {"id": "main.perimeter_shelf_width_mm", "unit": "mm",
         "expression": {"op": "mul", "args": [{"ref": "case.width_mm"}, {"ref": "main.perimeter_shelf_over_width"}]},
         "dependencies": ["case.width_mm", "main.perimeter_shelf_over_width"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived"},
        {"id": "header.rail_band_mm", "unit": "mm",
         "expression": {"op": "mul", "args": [{"ref": "case.height_mm"}, {"op": "sub", "args": [
             {"ref": "visual.main_bay_start_from_top"}, {"ref": "visual.header_split_from_top"}]}]},
         "dependencies": ["case.height_mm", "visual.main_bay_start_from_top", "visual.header_split_from_top"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "main.pocket_lobe_center_radius_mm", "unit": "mm",
         "expression": {"op": "add", "args": [
             {"op": "div", "args": [{"ref": "spinner.tip_circle_diameter_mm"}, {"value": 2.0, "unit": "ratio"}]},
             {"ref": "main.pocket_gap_mm"}, {"op": "neg", "args": [{"ref": "main.pocket_lobe_radius_mm"}]}]},
         "dependencies": ["spinner.tip_circle_diameter_mm", "main.pocket_gap_mm", "main.pocket_lobe_radius_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "case.z_frame_front_mm", "unit": "mm",
         "expression": {"op": "add", "args": [{"ref": "case.backplate_thickness_mm"}, {"ref": "content.review_rear_gap_mm"},
                                              {"ref": "case.frame_front_height_from_spinner_back_mm"}]},
         "dependencies": ["case.backplate_thickness_mm", "content.review_rear_gap_mm",
                          "case.frame_front_height_from_spinner_back_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "case.z_spinner_front_mm", "unit": "mm",
         "expression": {"op": "add", "args": [{"ref": "case.backplate_thickness_mm"}, {"ref": "content.review_rear_gap_mm"},
                                              {"ref": "spinner.max_thickness_mm"}]},
         "dependencies": ["case.backplate_thickness_mm", "content.review_rear_gap_mm", "spinner.max_thickness_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "case.z_shelf_top_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [{"ref": "case.z_frame_front_mm"}, {"ref": "interior.shelf_top_below_frame_front_mm"}]},
         "dependencies": ["case.z_frame_front_mm", "interior.shelf_top_below_frame_front_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived"},
        {"id": "case.root_recentering_z_mm", "unit": "mm",
         "expression": {"op": "mul", "args": [{"value": -0.5, "unit": "ratio"}, {"ref": "assembled.envelope_depth_mm"}]},
         "dependencies": ["assembled.envelope_depth_mm"], "round_to": 0.001, "evidence_class": "derived", "value_state": "derived"},
    ]
    resolved = {}
    pending = list(derived_specs)
    progress = True
    while pending and progress:
        progress = False
        for d in list(pending):
            try:
                value = evaluate(d["expression"], values)
            except KeyError:
                continue
            except Unresolved as exc:
                resolved[d["id"]] = {"value": None, "unit": d["unit"], "value_state": "unresolved", "blocked_by": str(exc)}
                values[d["id"]] = None
                pending.remove(d)
                progress = True
                continue
            step = d.get("round_to", 0.01)
            value = round(round(value / step) * step, 6)
            values[d["id"]] = value
            resolved[d["id"]] = {"value": value, "unit": d["unit"], "value_state": "derived",
                                 "dependencies": d["dependencies"]}
            pending.remove(d)
            progress = True
    if pending:
        raise SystemExit(f"unresolvable derived values: {[d['id'] for d in pending]}")

    # assertions from the spec §5.3 plus blockout fit checks
    T = values["spinner.max_thickness_mm"]
    coverage = values["case.frame_coverage_of_spinner_thickness"]
    protrusion_ratio = values["spinner.protrusion_ratio"]
    W = values["case.width_mm"]
    liner_inset = values["case.crystal_wall_mm"] + values["case.smoke_liner_mm"]
    field_half_width = W / 2 - liner_inset - values["main.perimeter_shelf_width_mm"]
    pocket_half_span = values["main.pocket_lobe_center_radius_mm"] * math.sin(math.radians(60)) + values["main.pocket_lobe_radius_mm"]
    pocket_margin = field_half_width - values["cmf.mirror_bevel_width_mm"] - pocket_half_span
    assertions = [
        {"id": "coverage-plus-protrusion-equals-one", "status": "pass" if abs(coverage + protrusion_ratio - 1.0) <= 0.001 else "fail",
         "detail": f"{coverage} + {protrusion_ratio} = {coverage + protrusion_ratio:.4f}"},
        {"id": "frame-height-plus-protrusion-equals-thickness",
         "status": "pass" if abs(values["case.frame_front_height_from_spinner_back_mm"] + values["spinner.protrusion_mm"] - T) <= 0.01 else "fail",
         "detail": f"{values['case.frame_front_height_from_spinner_back_mm']} + {values['spinner.protrusion_mm']} vs {T}"},
        {"id": "protrusion-ratio-in-range", "status": "pass" if 0.35 <= protrusion_ratio <= 0.45 else "fail",
         "detail": f"protrusion_ratio {protrusion_ratio}"},
        {"id": "no-old-contract-dimensions", "status": "pass" if not any(abs(values[k] - v) < 0.5 for k, v in
                                                                            [("case.width_mm", 228.0), ("case.height_mm", 304.0),
                                                                             ("assembled.envelope_depth_mm", 59.0)]) else "fail",
         "detail": f"W {W} H {values['case.height_mm']} D {values['assembled.envelope_depth_mm']} vs 228x304x59"},
        {"id": "spinner-pocket-fits-inside-field", "status": "pass" if pocket_margin > 0.5 else ("warn" if pocket_margin > 0 else "fail"),
         "detail": f"field half-width {field_half_width:.2f} mm, pocket half-span {pocket_half_span:.2f} mm, margin {pocket_margin:.2f} mm each side"},
        {"id": "spinner-pocket-fits-vertically",
         "status": "pass" if (values["main.field_top_y_mm"] - values["main.field_bottom_y_mm"] - values["main.pocket_height_mm"]) / 2 > 2.0 else "fail",
         "detail": f"field height {values['main.field_top_y_mm'] - values['main.field_bottom_y_mm']:.2f} mm, pocket height "
                   f"{values['main.pocket_height_mm']:.2f} mm, spinner centre {values['spinner.center_y_mm']} mm "
                   f"({values['visual.spinner_center_from_top']}H; image read {values['visual.spinner_center_from_top_image_reading']}H)"},
        {"id": "unknowns-preserved", "status": "pass" if all(values[k] is None for k in
                                                              ["retention.mechanism", "manufacturing.clearance_mm",
                                                               "manufacturing.tolerance_mm", "manufacturing.draft_angle_deg"]) else "fail",
         "detail": "retention and manufacturing fields stay null"},
        {"id": "no-provisional-promoted-to-measured",
         "status": "pass" if all(p["evidence_class"] != "measured" or p.get("source_id") == "src.spinner_mesh"
                                 for p in inputs.values()) else "fail",
         "detail": "every measured input cites src.spinner_mesh"},
    ]

    sources = []
    for s in spec["sources"]:
        s = dict(s)
        if s["id"] == "src.front_cmf_clean_v3":
            s["path"] = f"{REPO_REL}/01-intake/rev-004/v3-01-front-cmf-gold-silver.png"
        if s["id"] == "src.spinner_mesh":
            s["path"] = spinner_source["path"]
            s["sha256"] = spinner_source["sha256"]
            s["blend_path"] = spinner_source["blend_path"]
            s["blend_sha256"] = spinner_source["blend_sha256"]
            s["owner_pipeline"] = spinner_source["owner_pipeline"]
            s.pop("blocks_gate", None)
        if s["id"] == "src.front_annotated_feedback":
            s["note"] = "Not supplied to the repository. SHA-256 kept from the spec; its ratios are superseded by the clean recheck."
        sources.append(s)
    sources += [
        {"id": "src.v3_user_chat_front", "role": "ai-target/concept-only",
         "path": f"{REPO_REL}/01-intake/rev-004/v3-user-chat-front-650x1024.jpg",
         "sha256": sha256(INTAKE / "v3-user-chat-front-650x1024.jpg"), "pixel_size": [650, 1024], "immutable": True,
         "geometry_truth": False, "material_truth": False},
        {"id": "src.v3_user_chat_three_view", "role": "ai-target/concept-only",
         "path": f"{REPO_REL}/01-intake/rev-004/v3-user-chat-three-view-1024x576.jpg",
         "sha256": sha256(INTAKE / "v3-user-chat-three-view-1024x576.jpg"), "pixel_size": [1024, 576], "immutable": True,
         "geometry_truth": False, "material_truth": False},
        {"id": "src.v3_clean_recheck_r007", "role": "analysis",
         "path": f"{REPO_REL}/02-analysis/rev-007/v3-proportion-analysis.json", "sha256": sha256(PROPORTIONS_PATH),
         "immutable": True, "geometry_truth": False, "material_truth": False},
        {"id": "src.spinner_measurement_r007", "role": "analysis",
         "path": f"{REPO_REL}/02-analysis/rev-007/spinner-source-measurement.json", "sha256": sha256(SPINNER_PATH),
         "immutable": True, "geometry_truth": True, "material_truth": False},
    ]

    contract = {
        "schemaVersion": 1,
        "schema_version": spec["schema_version"],
        "spec_id": spec["spec_id"],
        "modelId": spec["model_id"],
        "model_id": spec["model_id"],
        "variant_id": spec["variant_id"],
        "contractRevision": 4,
        "revision": 1,
        "createdDate": dt.date.today().isoformat(),
        "stageStatus": "ready_for_review",
        "approvalEffect": "none-until-explicit-gate-03-user-approval",
        "status": "gate03_candidate_ready_for_review",
        "provisional_marker": "PROVISIONAL_DIMENSIONS",
        "provisional_marker_reason": "Case size derives from concept-image ratios; only spinner dimensions are measured.",
        "sourceSpec": {"path": f"{REPO_REL}/01-intake/rev-004/tri-spinner-slab-model-spec.v0.json", "sha256": sha256(SPEC_PATH),
                       "handoff_spec_path": f"{REPO_REL}/01-intake/rev-004/tri-spinner-slab-agent-handoff-spec.md",
                       "handoff_spec_sha256": sha256(INTAKE / "tri-spinner-slab-agent-handoff-spec.md")},
        "sourceAnalysisRevision": 7,
        "sourceIntakeRevision": 4,
        "sourceClaimIds": SOURCE_CLAIM_IDS,
        "supersedes": {"contractRevision": 3, "reason": "Old 228x304x59 mm closed-tube contract does not apply to the V3 slab concept.",
                       "reuse_forbidden_dimensions_mm": spec["pipeline_context"]["old_contract_reference_dimensions_mm"]},
        "software": spec["software"],
        "evidence_taxonomy": spec["evidence_taxonomy"],
        "sources": sources,
        "units": spec["units"],
        "coordinate_system": spec["coordinate_system"],
        "integration_contract": spec["integration_contract"],
        "formula_language": spec["formula_language"],
        "parameters": {"inputs": [inputs[pid] for pid in order], "derived": derived_specs},
        "resolved": resolved,
        "depth_stack_mm": {
            "z_rear_outer": 0.0,
            "z_backplate_front": values["case.backplate_thickness_mm"],
            "z_spinner_back": round(values["case.backplate_thickness_mm"] + values["content.review_rear_gap_mm"], 3),
            "z_shelf_top": values["case.z_shelf_top_mm"],
            "z_frame_front": values["case.z_frame_front_mm"],
            "z_spinner_front": values["case.z_spinner_front_mm"],
            "spinner_protrusion": values["spinner.protrusion_mm"],
            "assembled_envelope_depth": values["assembled.envelope_depth_mm"],
            "root_recentering_z": values["case.root_recentering_z_mm"],
        },
        "assertions": assertions,
        "scene": spec["scene"],
        "geometry_builder": spec["geometry_builder"],
        "vertex_channels": spec["vertex_channels"],
        "materials": spec["materials"],
        "cameras": spec["cameras"],
        "lighting": spec["lighting"],
        "blender_render": spec["blender_render"],
        "soft_focus": spec["soft_focus"],
        "turntable": spec["turntable"],
        "unity_urp": spec["unity_urp"],
        "performance_budget": spec["performance_budget"],
        "acceptance": spec["acceptance"],
        "required_artifacts": spec["required_artifacts"],
        "validation_rules": spec["validation_rules"],
        "hashing": {"algorithm": "sha256",
                    "canonical_json": "RFC8785-style: sorted keys, no whitespace, integral floats as integers (see resolve_contract.py)",
                    "contract_sha256": None,
                    "invalidation": spec["hashing"]["invalidation"]},
    }
    contract["hashing"]["contract_sha256"] = contract_hash(contract)
    (HERE / "modeling-contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n")
    validation = {
        "contract_sha256": contract["hashing"]["contract_sha256"],
        "assertions": assertions,
        "resolved_key_values_mm": {k: values[k] for k in [
            "case.width_mm", "case.height_mm", "header.height_mm", "header.rail_band_mm", "case.frame_band_mm",
            "case.outer_corner_radius_mm", "case.inner_corner_radius_mm", "main.perimeter_shelf_width_mm",
            "spinner.center_x_mm", "spinner.center_y_mm", "case.frame_front_height_from_spinner_back_mm",
            "spinner.protrusion_mm", "case.z_frame_front_mm", "case.z_shelf_top_mm", "case.z_spinner_front_mm",
            "assembled.envelope_depth_mm", "case.root_recentering_z_mm", "main.pocket_lobe_center_radius_mm",
            "main.field_top_y_mm", "main.field_bottom_y_mm", "main.pocket_height_mm", "visual.spinner_center_from_top"]},
        "all_pass": all(a["status"] == "pass" for a in assertions),
        "warnings": [a for a in assertions if a["status"] == "warn"],
    }
    (HERE / "contract-validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=1))
    return 0 if all(a["status"] != "fail" for a in assertions) else 1


if __name__ == "__main__":
    sys.exit(main())
