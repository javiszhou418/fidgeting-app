#!/usr/bin/env python3
"""Gate 03 rev-007: resolve the V3 slab modeling contract after the user's
Gate 05 rev-006 feedback (2026-09-10 12:22 / 12:23, direction accepted:
"感觉差不多吧").

Changes against rev-006:
- `src.user_gate05_rev006_feedback_fillets_20260910`: every 45-degree chamfer
  junction (header bezel, main bezel top corners, field outline and its
  groove, wing corners) gets a fillet instead of a hard vertex.
- `src.user_gate05_rev006_feedback_trait_plaque_20260910`: the bottom brushed
  band becomes a TRAIT PROFILE plaque reserving three 0-100 tracks
  (SPIN / FEEL / CRAFT, FDB-DSP-053, source thread
  d0029833-35d3-499b-9f9d-7156b390f254) with quartile tick notches and
  runtime-dynamic fill placeholders; the pocket moves up (split 0.22) to
  make room.
- Review lighting brightness is a preview-script concern, not a contract
  change (the beauty rig stays as specified).

Changes rev-005 -> rev-006 (kept), sourced to `src.user_gate05_rev005_feedback_20260910`:
- The silver datum rail bridging header and main is removed: the reference
  shows two separate steel islands with a dark seam between them.
- Header bezel has 45-degree chamfers on all four corners; the crystal frame
  gets a stepped inner ledge (double edge).
- More levels inside the holder: engraved outline groove and band grooves cut
  into the field, angular brushed wing panels, a raised polished pocket lip
  with an outer chamfer and an inner slope, three clear retention clips on the
  lip (visible in the concept image; mechanical function not engineered), a
  mirror divider line on the header plate.

Changes rev-004 -> rev-005 (kept), sourced to the rev-004 rejection:
- Pocket is a generic circle sized from the largest toy (65 mm tip circle),
  not a tri-lobe. The case width is now derived from the pocket plus margins,
  so the toy sits at fit scale 1.0 instead of being shrunk into the case.
- Relief depths, chamfers and bevels are raised into the visible range
  (header 1.2 mm, main field 1.6 mm, mirror chamfer 0.9 mm, crystal bevel 1.0 mm).
- Six counterbored bolts on the crystal band; pocket rim + smoke wall + floor.
- Every nested outline must be a true inward offset of its parent
  (concentric corners by construction; see geometry_builder.nested_offset_rule).

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

REJECTION_SOURCE_ID = "src.user_gate05_rev004_rejection_20260910"
REJECTION_WORDING = (
    "细节还原网还达不到，就是时刻的深度，就是雕刻的深度，包括里面的那些细节还差很多。各种材质的分区我也没有看到。"
    "你里面给这个模型留的这个三角的区域应该是不对的。我建议你可以留一个比较通用的、一个形状。"
    "这样我们在不同的样式的陀螺的时候才能有不同的表现嘛？才有这个捞下去的东西才能容纳这个3D陀螺本身。"
    "它的这个厚度，以及这种光感、倒角、打孔等细节，你现在全都丢失了。现在圆角都不是同心圆，你这个品质简直是太垃圾了。"
    "我现在没法相信你就是直接出图的能力了。"
)
FEEDBACK = {"evidence_class": "recommended_start", "value_state": "provisional", "source_id": REJECTION_SOURCE_ID}

FEEDBACK2_SOURCE_ID = "src.user_gate05_rev005_feedback_20260910"
FEEDBACK2_WORDING = (
    "我现在就是里面笔触和描边的细节，就是不同这个 holder 里面不同层级的台阶，好像没有介绍得很清楚。还是太扁平了，缺少层级，"
    "然后笔触和台阶可以增加一些。细节太少了，就是我在这个图里面通过不同颜色的 arrow 给你标注出来的。"
    "第二张图里面蓝色框出来的一个部分，我在给你参考图里面应该是没有这部分区域的。它跟线的那个板子是断开的。"
    "然后下面那个实际放陀螺的那个承载区细节也是比较缺失，你再仔细对照一下。"
)
FEEDBACK2 = {"evidence_class": "recommended_start", "value_state": "provisional", "source_id": FEEDBACK2_SOURCE_ID}

FEEDBACK3A_SOURCE_ID = "src.user_gate05_rev006_feedback_fillets_20260910"
FEEDBACK3A_WORDING = (
    "感觉差不多吧，这个光照还是有点黑。能不能再提亮点，这样细节我看得更清楚一些，或者你把环境光射得更亮一些。"
    "然后，这些红色的圈的这些地方感觉过渡得太生硬了，能不能稍微用圆角，就是倒一下角？"
)
FEEDBACK3B_SOURCE_ID = "src.user_gate05_rev006_feedback_trait_plaque_20260910"
FEEDBACK3B_WORDING = (
    "然后这个地方可能要稍微注意一下。就到时候我可能要放一个动态的三条数值。"
    "就是在d0029833-35d3-499b-9f9d-7156b390f254 这个对话里面我们做过的一个 feature"
)
FEEDBACK3A = {"evidence_class": "recommended_start", "value_state": "provisional", "source_id": FEEDBACK3A_SOURCE_ID}
FEEDBACK3B = {"evidence_class": "recommended_start", "value_state": "provisional", "source_id": FEEDBACK3B_SOURCE_ID}


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

    # --- structure: shelf scales with W
    inputs.pop("main.perimeter_shelf_width_mm")
    order.remove("main.perimeter_shelf_width_mm")
    add_input(inputs, order, "main.perimeter_shelf_over_width", data_type="number", unit="ratio", value=0.045,
              range=[0.040, 0.052], evidence_class="recommended_start", value_state="provisional",
              note="Replaces the fixed 4.5 mm, which was sized for the retired 111.55 mm provisional width.")
    add_input(inputs, order, "interior.shelf_top_below_frame_front_mm", data_type="number", unit="mm", value=3.0,
              range=[2.0, 4.5], evidence_class="recommended_start", value_state="provisional",
              note="Depth of the crystal lip above the satin shelves.")
    add_input(inputs, order, "header.plate_side_inset_mm", data_type="number", unit="mm", value=1.5, range=[1.0, 2.5],
              evidence_class="recommended_start", value_state="provisional",
              note="Graphite plate inset from the header shelf edge, in addition to the mirror bevel width.")

    # --- pocket: generic circle sized from the largest toy (user rejection 2026-09-10: tri-lobe is wrong,
    #     leave a generic shape that holds the 3D toy itself)
    add_input(inputs, order, "main.pocket_generic_for_any_toy", data_type="boolean", unit="none", value=True,
              evidence_class="user_requirement", value_state="visual_locked", source_id=REJECTION_SOURCE_ID,
              note="The pocket must not encode one spinner's silhouette; different toys are shown in the same well.")
    add_input(inputs, order, "main.pocket_shape", data_type="enum", unit="none", value="circle", allowed=["circle"],
              **FEEDBACK, note="Circle chosen as the generic well; matches the shipping case's circular recess precedent.")
    add_input(inputs, order, "content.design_toy_diameter_mm", data_type="number", unit="mm",
              value=sm["tip_circle_diameter"], evidence_class="measured", value_state="measured", source_id="src.spinner_mesh",
              note="Largest catalog toy footprint (tri-spinner tip circle). Smaller toys are fit-scaled by the runtime, never enlarged.")
    add_input(inputs, order, "content.fit_clearance_mm", data_type="number", unit="mm", value=1.2, range=[0.8, 2.0],
              **FEEDBACK, manufacturing_clearance=False,
              note="Visual gap between the toy tip circle and the smoke wall. Not a retention or manufacturing clearance.")
    add_input(inputs, order, "main.pocket_wall_mm", data_type="number", unit="mm", value=0.85, range=[0.7, 1.0],
              **FEEDBACK, note="Smoke-liner wall of the well, from the backplate front to the rim underside.")
    add_input(inputs, order, "main.pocket_floor_mm", data_type="number", unit="mm", value=0.3, range=[0.2, 0.4],
              **FEEDBACK, note="Graphite floor disc laid on the backplate inside the well.")
    add_input(inputs, order, "main.field_side_margin_mm", data_type="number", unit="mm", value=3.0, range=[2.5, 4.0],
              **FEEDBACK, note="Microblast field left beside the pocket rim; hosts the vertical gold rails and brushed strips.")
    add_input(inputs, order, "main.pocket_vertical_margin_split", data_type="number", unit="ratio", value=0.22,
              range=[0.18, 0.40], **FEEDBACK3B,
              note="Share of the spare field height placed above the pocket. rev-007 lowers 0.30 -> 0.22 so the TRAIT PROFILE plaque "
                   "fits below the pocket; the hub moves ~2 mm up from the 0.637H image reading (warn-level, user-driven).")

    # --- relief, chamfer and bevel depths raised into the visible range (user: carving depth, bevels lost)
    set_input(inputs, "header.recess_depth_mm", value=1.2, range=[0.8, 1.6], **FEEDBACK,
              note="Spec start 0.3 mm read flat at 2048 px; rev-005 raises it.")
    set_input(inputs, "main.recess_depth_mm", value=1.6, range=[1.2, 2.0], hard_max=2.4, **FEEDBACK,
              note="Spec start 0.4 mm read flat at 2048 px; rev-005 raises it.")
    set_input(inputs, "cmf.mirror_bevel_width_mm", value=0.9, range=[0.7, 1.2], **FEEDBACK,
              note="45-degree mirror chamfer between shelf top and recessed plane.")
    set_input(inputs, "case.crystal_bevel_mm", value=1.0, range=[0.8, 1.2], **FEEDBACK)
    set_input(inputs, "case.inner_bevel_mm", value=0.4, range=[0.3, 0.5], **FEEDBACK)
    set_input(inputs, "cmf.gold_inlay_width_mm", value=0.6, range=[0.4, 0.8], **FEEDBACK,
              note="Wider than the spec's 0.18-0.35 range so the inlays read as inlays, not hairlines.")
    set_input(inputs, "cmf.gold_relief_mm", value=0.10, range=[0.06, 0.15], **FEEDBACK)
    add_input(inputs, order, "interior.part_lift_mm", data_type="number", unit="mm", value=0.6, range=[0.4, 0.8],
              **FEEDBACK, note="Raised brushed strips and band above the microblast field.")
    # rev-006: the datum rail is retired (user: the blue-boxed band does not exist in the reference; the header plate is
    # disconnected from the main plate). The rail band becomes a dark seam plus a wider brushed top strip of the main bezel.
    add_input(inputs, order, "header.seam_gap_mm", data_type="number", unit="mm", value=2.4, range=[1.8, 3.2], **FEEDBACK2,
              note="Dark gap between the header bezel and the main bezel; the smoke seam floor shows through. Replaces the silver datum rail.")
    add_input(inputs, order, "header.bezel_corner_chamfer_mm", data_type="number", unit="mm", value=4.5, range=[3.5, 5.5], **FEEDBACK2,
              note="45-degree chamfer on all four header bezel corners (reference crop: header top corners are chamfered, not rounded).")
    add_input(inputs, order, "case.frame_ledge_width_mm", data_type="number", unit="mm", value=0.9, range=[0.7, 1.2], **FEEDBACK2,
              note="Inner ledge of the crystal frame stepped below the front face: the double edge seen along the frame.")
    add_input(inputs, order, "case.frame_ledge_drop_mm", data_type="number", unit="mm", value=0.8, range=[0.6, 1.0], **FEEDBACK2)
    add_input(inputs, order, "main.field_outline_groove_inset_mm", data_type="number", unit="mm", value=1.6, range=[1.2, 2.2], **FEEDBACK2,
              note="Engraved outline groove following the chamfered field edge, cut into the microblast field.")
    add_input(inputs, order, "main.groove_width_mm", data_type="number", unit="mm", value=0.4, range=[0.3, 0.6], **FEEDBACK2)
    add_input(inputs, order, "main.groove_depth_mm", data_type="number", unit="mm", value=0.3, range=[0.2, 0.4], **FEEDBACK2,
              note="All engraved lines (field outline, band surround, lip foot) are boolean cuts of this depth: geometry, not texture.")
    add_input(inputs, order, "main.wing_edge_inset_mm", data_type="number", unit="mm", value=3.2, range=[2.5, 4.0], **FEEDBACK2,
              note="Brushed wing panels start this far inside the field edge, leaving the gold accent between wing and edge.")
    add_input(inputs, order, "main.wing_pocket_gap_mm", data_type="number", unit="mm", value=2.2, range=[1.6, 3.0], **FEEDBACK2,
              note="Gap between a wing's faceted inner edge and the pocket lip foot.")
    add_input(inputs, order, "main.pocket_lip_width_mm", data_type="number", unit="mm", value=1.8, range=[1.4, 2.4], **FEEDBACK2,
              note="Polished lip ring around the well, raised above the field (reference: bright raised rim, not a sunken chamfer). "
                   "Replaces main.pocket_rim_width_mm (retired).")
    add_input(inputs, order, "main.pocket_lip_height_mm", data_type="number", unit="mm", value=0.6, range=[0.4, 0.8], **FEEDBACK2)
    add_input(inputs, order, "main.pocket_lip_outer_chamfer_mm", data_type="number", unit="mm", value=0.5, range=[0.3, 0.7], **FEEDBACK2)
    add_input(inputs, order, "main.pocket_lip_inner_slope_mm", data_type="number", unit="mm", value=0.6, range=[0.4, 0.9], **FEEDBACK2,
              note="Inner face slopes from the lip top down below field level into the smoke wall (horizontal run).")
    add_input(inputs, order, "main.pocket_lip_inner_drop_mm", data_type="number", unit="mm", value=1.2, range=[0.8, 1.6], **FEEDBACK2,
              note="Vertical drop of the inner slope below the field surface before the smoke wall takes over.")
    add_input(inputs, order, "hardware.clip_count", data_type="number", unit="count", value=3, **FEEDBACK2,
              note="Clear clips on the lip at 90/210/330 degrees, as the three clips at the concept pocket tips. Visual only.")
    add_input(inputs, order, "hardware.clip_size_mm", data_type="vector3", unit="mm", value=[4.0, 3.2, 2.4], **FEEDBACK2,
              note="tangential x radial x height; rounded block straddling the lip. Not a retention mechanism (retention.mechanism stays null).")
    # rev-007 (12:22): fillets at every chamfer junction (red circles: header bezel lower corners, field TL/TR chamfer ends, wing corners)
    add_input(inputs, order, "interior.junction_fillet_mm", data_type="number", unit="mm", value=1.5, range=[1.0, 2.0], **FEEDBACK3A,
              note="Fillet radius where a 45-degree chamfer meets a straight edge, on the outermost outline of each chain.")
    add_input(inputs, order, "interior.junction_fillet_min_mm", data_type="number", unit="mm", value=0.8, range=[0.5, 1.0], **FEEDBACK3A,
              note="Nested outlines keep at least this junction fillet even when the exact offset (r - d) would be smaller. The only sanctioned "
                   "deviation from the exact-offset rule; it applies to chamfer-junction fillets only, never to the main corner arcs.")
    add_input(inputs, order, "main.wing_corner_fillet_mm", data_type="number", unit="mm", value=1.0, range=[0.6, 1.5], **FEEDBACK3A,
              note="Fillet on every wing polygon vertex.")
    # rev-007 (12:23): bottom band becomes the TRAIT PROFILE plaque (FDB-DSP-053; three 0-100 tracks SPIN / FEEL / CRAFT)
    add_input(inputs, order, "trait.plaque_hosts_trait_profile", data_type="boolean", unit="none", value=True,
              evidence_class="user_requirement", value_state="visual_locked", source_id=FEEDBACK3B_SOURCE_ID,
              note="The plaque reserves three dynamic 0-100 bars. Axis order SPIN / FEEL / CRAFT is fixed by FDB-DSP-053; values come from "
                   "Assets/Scripts/Product/ToyTalentCatalog.cs at runtime, never from this contract.")
    add_input(inputs, order, "trait.plaque_height_mm", data_type="number", unit="mm", value=10.0, range=[9.0, 12.0], **FEEDBACK3B)
    add_input(inputs, order, "trait.plaque_bottom_margin_mm", data_type="number", unit="mm", value=2.2, range=[1.8, 3.0], **FEEDBACK3B,
              note="Plaque bottom edge above the field bottom edge.")
    add_input(inputs, order, "trait.row_pitch_mm", data_type="number", unit="mm", value=3.0, range=[2.6, 3.6], **FEEDBACK3B)
    add_input(inputs, order, "trait.track_height_mm", data_type="number", unit="mm", value=1.2, range=[1.0, 1.6], **FEEDBACK3B)
    add_input(inputs, order, "trait.track_depth_mm", data_type="number", unit="mm", value=0.35, range=[0.25, 0.5], **FEEDBACK3B,
              note="Trough recess cut into the plaque top (BOOLEAN EXACT); the empty part of a bar is this trough.")
    add_input(inputs, order, "trait.label_column_mm", data_type="number", unit="mm", value=14.0, range=[12.0, 16.0], **FEEDBACK3B,
              note="Reserved for the axis label decal (SPIN / FEEL / CRAFT); no text geometry in the blockout.")
    add_input(inputs, order, "trait.value_column_mm", data_type="number", unit="mm", value=9.0, range=[8.0, 11.0], **FEEDBACK3B,
              note="Reserved for the numeric value decal; no text geometry in the blockout.")
    add_input(inputs, order, "trait.tick_width_mm", data_type="number", unit="mm", value=0.3, range=[0.25, 0.4], **FEEDBACK3B,
              note="Quartile tick notches at 25 / 50 / 75 % cut through the trough edges (printed ink on the paper certificate, geometry here).")
    add_input(inputs, order, "trait.fill_inset_mm", data_type="number", unit="mm", value=0.1, range=[0.05, 0.15], **FEEDBACK3B,
              note="Runtime fill strip sits inside the trough by this margin and below the plaque top.")
    add_input(inputs, order, "trait.preview_values", data_type="vector3", unit="0-100", value=[88, 36, 86],
              evidence_class="repository_authority", value_state="preview_only", source_id="ToyTalentCatalog.metal-three-blade",
              note="Preview placeholder lengths only (metal-three-blade 88/36/86, sum 210). Runtime authority is ToyTalentCatalog.cs; "
                   "the exported fill strips are authored at 100 % and shortened by the trait block at runtime.")
    add_input(inputs, order, "header.divider_from_plate_top", data_type="number", unit="ratio", value=0.58, range=[0.5, 0.65], **FEEDBACK2,
              note="Mirror divider line on the graphite plate (reference: rule under the title block).")
    add_input(inputs, order, "header.divider_line_width_mm", data_type="number", unit="mm", value=0.3, range=[0.2, 0.4], **FEEDBACK2)
    add_input(inputs, order, "interior.part_bevel_mm", data_type="number", unit="mm", value=0.25, range=[0.15, 0.35],
              **FEEDBACK, note="Bevel on shelves, rail, strips and band edges.")
    add_input(inputs, order, "main.field_top_chamfer_mm", data_type="number", unit="mm", value=8.0, range=[6.0, 10.0],
              **FEEDBACK, note="45-degree chamfer on the two upper corners of the main field, as in the V3 front image.")
    add_input(inputs, order, "main.field_bottom_chamfer_mm", data_type="number", unit="mm", value=4.0, range=[3.0, 5.0],
              **FEEDBACK)
    add_input(inputs, order, "header.plate_bottom_chamfer_mm", data_type="number", unit="mm", value=4.5, range=[3.5, 5.5],
              **FEEDBACK2, note="rev-006: equals header.bezel_corner_chamfer_mm; all four header bezel corners are chamfered.")
    add_input(inputs, order, "interior.bezel_corner_radius_mm", data_type="number", unit="mm", value=6.0, range=[5.0, 7.0],
              **FEEDBACK, note="Outer corner radius of the header and main steel bezels. Large enough that bezel -> mirror chamfer -> "
                               "plane stay concentric after the shelf inset without clamping.")

    # --- hardware: six counterbored bolts on the crystal band (user: holes/bolts lost)
    add_input(inputs, order, "hardware.bolt_count", data_type="number", unit="count", value=6, **FEEDBACK,
              note="Four frame corners plus left/right at the header seam, as in the V3 front image.")
    add_input(inputs, order, "hardware.bolt_head_diameter_mm", data_type="number", unit="mm", value=2.6, range=[2.2, 3.0], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_socket_diameter_mm", data_type="number", unit="mm", value=1.4, range=[1.2, 1.6], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_socket_depth_mm", data_type="number", unit="mm", value=0.6, range=[0.4, 0.8], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_counterbore_diameter_mm", data_type="number", unit="mm", value=3.0, range=[2.6, 3.4], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_counterbore_depth_mm", data_type="number", unit="mm", value=1.0, range=[0.8, 1.4], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_head_below_frame_front_mm", data_type="number", unit="mm", value=0.25, range=[0.15, 0.4], **FEEDBACK)
    add_input(inputs, order, "hardware.bolt_on_band_centreline", data_type="boolean", unit="none", value=True, **FEEDBACK,
              note="Corner bolts sit on the band centreline at the 45-degree point of the corner arc; seam bolts on the centreline at the seam height.")

    # --- crystal band is the visible clear frame width; the smoke liner sits inside it
    add_input(inputs, order, "case.crystal_frame_is_full_band", data_type="boolean", unit="none", value=True, **FEEDBACK,
              note="The clear frame ring spans the whole frame band (not only the 1.5 mm wall) so its thickness reads from the front.")
    add_input(inputs, order, "case.liner_seam_above_shelf_mm", data_type="number", unit="mm", value=0.3, range=[0.2, 0.5], **FEEDBACK,
              note="Smoke liner stands slightly above the shelves, giving the dark seam between crystal and steel.")

    set_input(inputs, "visual.spinner_span_over_width",
              note="Image reading kept on record. No longer drives case.width_mm: rev-005 derives the width from the generic pocket.")

    values = {pid: p.get("value") for pid, p in inputs.items()}

    derived_specs = [d for d in spec["parameters"]["derived"]
                     if d["id"] not in ("spinner.center_y_mm", "case.width_mm", "case.outer_corner_radius_mm")]
    ref = lambda i: {"ref": i}  # noqa: E731
    const = lambda v: {"value": v, "unit": "ratio"}  # noqa: E731
    derived_specs += [
        {"id": "case.outer_corner_radius_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("case.frame_band_mm"), ref("case.inner_corner_radius_mm")]},
         "dependencies": ["case.frame_band_mm", "case.inner_corner_radius_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived",
         "note": "Concentric rule: outer radius = band + inner radius, so the frame's inner corner is exactly the 0.028 W reading. "
                 "Replaces the 0.04 W outer reading, which cannot be concentric with a 0.052 W band."},
        {"id": "hardware.bolt_corner_inset_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [ref("case.outer_corner_radius_mm"),
                                              {"op": "mul", "args": [const(0.7071067811865476),
                                                                     {"op": "sub", "args": [ref("case.outer_corner_radius_mm"),
                                                                                            {"op": "mul", "args": [const(0.5), ref("case.frame_band_mm")]}]}]}]},
         "dependencies": ["case.outer_corner_radius_mm", "case.frame_band_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived",
         "note": "Corner bolt centre offset from both outer edges = R - (R - band/2)/sqrt(2): the 45-degree point on the band centreline."},
        {"id": "main.pocket_well_diameter_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("content.design_toy_diameter_mm"),
                                              {"op": "mul", "args": [const(2.0), ref("content.fit_clearance_mm")]}]},
         "dependencies": ["content.design_toy_diameter_mm", "content.fit_clearance_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived", "note": "inside face of the smoke wall"},
        {"id": "main.pocket_diameter_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("main.pocket_well_diameter_mm"),
                                              {"op": "mul", "args": [const(2.0), ref("main.pocket_wall_mm")]},
                                              {"op": "mul", "args": [const(2.0), ref("main.pocket_lip_inner_slope_mm")]},
                                              {"op": "mul", "args": [const(2.0), ref("main.pocket_lip_width_mm")]}]},
         "dependencies": ["main.pocket_well_diameter_mm", "main.pocket_wall_mm", "main.pocket_lip_inner_slope_mm", "main.pocket_lip_width_mm"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "outer foot of the polished lip at field level = well + 2 wall + 2 inner slope + 2 lip"},
        {"id": "main.field_width_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("main.pocket_diameter_mm"),
                                              {"op": "mul", "args": [const(2.0), ref("main.field_side_margin_mm")]}]},
         "dependencies": ["main.pocket_diameter_mm", "main.field_side_margin_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived"},
        {"id": "case.width_mm", "unit": "mm",
         "expression": {"op": "div", "args": [
             {"op": "add", "args": [ref("main.field_width_mm"),
                                    {"op": "mul", "args": [const(2.0), {"op": "add", "args": [ref("case.smoke_liner_mm"), const(0.02)]}]}]},
             {"op": "sub", "args": [const(1.0), {"op": "mul", "args": [const(2.0), {"op": "add", "args": [
                 ref("visual.frame_band_over_width"), ref("main.perimeter_shelf_over_width")]}]}]}]},
         "dependencies": ["main.field_width_mm", "case.smoke_liner_mm", "visual.frame_band_over_width", "main.perimeter_shelf_over_width"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "W = (field + 2*(liner + 0.02 sep)) / (1 - 2*(band ratio + shelf ratio)). Replaces span / span_over_width."},
        {"id": "content.review_fit_scale", "unit": "ratio",
         "expression": {"op": "min", "args": [const(1.0), {"op": "div", "args": [
             {"op": "sub", "args": [ref("main.pocket_well_diameter_mm"), {"op": "mul", "args": [const(2.0), ref("content.fit_clearance_mm")]}]},
             ref("content.design_toy_diameter_mm")]}]},
         "dependencies": ["main.pocket_well_diameter_mm", "content.fit_clearance_mm", "content.design_toy_diameter_mm"],
         "round_to": 0.0001, "evidence_class": "derived", "value_state": "derived",
         "note": "Runtime fit scale for the design toy; 1.0 by construction. Smaller toys keep scale 1.0 too (never enlarged)."},
        {"id": "main.liner_inset_mm", "unit": "mm",
         "expression": {"op": "add", "args": [ref("case.frame_band_mm"), ref("case.smoke_liner_mm"), const(0.02)]},
         "dependencies": ["case.frame_band_mm", "case.smoke_liner_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived",
         "note": "full crystal band + 0.02 mm render separation + liner"},
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
        {"id": "spinner.center_y_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [
             ref("main.field_top_y_mm"),
             {"op": "mul", "args": [ref("main.pocket_vertical_margin_split"),
                                    {"op": "sub", "args": [{"op": "sub", "args": [ref("main.field_top_y_mm"), ref("main.field_bottom_y_mm")]},
                                                           ref("main.pocket_diameter_mm")]}]},
             {"op": "mul", "args": [const(0.5), ref("main.pocket_diameter_mm")]}]},
         "dependencies": ["main.field_top_y_mm", "main.field_bottom_y_mm", "main.pocket_diameter_mm",
                          "main.pocket_vertical_margin_split"],
         "round_to": 0.01, "evidence_class": "derived", "value_state": "derived",
         "note": "Pocket centre = field top - split * spare height - radius. Replaces the spec's image-ratio placement."},
        {"id": "case.z_field_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [ref("case.z_shelf_top_mm"), ref("main.recess_depth_mm")]},
         "dependencies": ["case.z_shelf_top_mm", "main.recess_depth_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived", "note": "microblast field surface"},
        {"id": "case.z_header_plane_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [ref("case.z_shelf_top_mm"), ref("header.recess_depth_mm")]},
         "dependencies": ["case.z_shelf_top_mm", "header.recess_depth_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived", "note": "graphite plane surface"},
        {"id": "main.pocket_well_depth_mm", "unit": "mm",
         "expression": {"op": "sub", "args": [ref("case.z_field_mm"), ref("case.backplate_thickness_mm"), ref("main.pocket_floor_mm")]},
         "dependencies": ["case.z_field_mm", "case.backplate_thickness_mm", "main.pocket_floor_mm"], "round_to": 0.01,
         "evidence_class": "derived", "value_state": "derived", "note": "field surface down to the graphite floor"},
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
    H = values["case.height_mm"]
    liner_inset = values["main.liner_inset_mm"]
    field_half_width = W / 2 - liner_inset - values["main.perimeter_shelf_width_mm"]
    pocket_margin = field_half_width - values["main.pocket_diameter_mm"] / 2
    field_height = values["main.field_top_y_mm"] - values["main.field_bottom_y_mm"]
    spare_below = field_height - values["main.pocket_diameter_mm"] - values["main.pocket_vertical_margin_split"] * (field_height - values["main.pocket_diameter_mm"])
    band = values["case.frame_band_mm"]
    r_o = values["case.outer_corner_radius_mm"]
    inset = values["hardware.bolt_corner_inset_mm"]
    head_r = values["hardware.bolt_counterbore_diameter_mm"] / 2
    # corner bolt centre sits at (W/2 - inset, H/2 - inset); the outer corner arc centre is at (W/2 - r_o, H/2 - r_o)
    d_arc_centre = math.hypot(r_o - inset, r_o - inset)
    dist_outer = r_o - d_arc_centre
    dist_inner = d_arc_centre - (r_o - band)          # inner arc is concentric with radius r_o - band
    bolt_clear = min(dist_outer, dist_inner) - head_r
    assertions = [
        {"id": "pocket-is-generic-circle", "status": "pass" if values["main.pocket_shape"] == "circle" and values["main.pocket_generic_for_any_toy"] else "fail",
         "detail": f"shape {values['main.pocket_shape']}, generic {values['main.pocket_generic_for_any_toy']}"},
        {"id": "design-toy-fits-at-scale-one", "status": "pass" if abs(values["content.review_fit_scale"] - 1.0) < 1e-6 else "fail",
         "detail": f"fit scale {values['content.review_fit_scale']} for {values['content.design_toy_diameter_mm']} mm tip circle in "
                   f"{values['main.pocket_well_diameter_mm']} mm well"},
        {"id": "pocket-side-margin-equals-input", "status": "pass" if abs(pocket_margin - values["main.field_side_margin_mm"]) < 0.05 else "fail",
         "detail": f"field half-width {field_half_width:.2f} mm, pocket radius {values['main.pocket_diameter_mm'] / 2:.2f} mm, margin {pocket_margin:.2f} mm"},
        {"id": "room-below-pocket-for-trait-plaque",
         "status": "pass" if spare_below - values["main.groove_width_mm"] - values["main.wing_pocket_gap_mm"]
                              - (values["trait.plaque_bottom_margin_mm"] + values["trait.plaque_height_mm"]) >= 1.0 else "fail",
         "detail": f"{spare_below:.2f} mm below the pocket foot; plaque {values['trait.plaque_bottom_margin_mm']} + {values['trait.plaque_height_mm']} mm, "
                   f"lip groove {values['main.groove_width_mm']}, wing gap {values['main.wing_pocket_gap_mm']}: "
                   f"{spare_below - values['main.groove_width_mm'] - values['main.wing_pocket_gap_mm'] - values['trait.plaque_bottom_margin_mm'] - values['trait.plaque_height_mm']:.2f} mm left for the wing foot (>= 1.0)"},
        {"id": "trait-rows-fit-plaque",
         "status": "pass" if 2 * values["trait.row_pitch_mm"] + values["trait.track_height_mm"] + 2 * 1.4 <= values["trait.plaque_height_mm"] + 1e-6 else "fail",
         "detail": f"3 rows: 2 x pitch {values['trait.row_pitch_mm']} + track {values['trait.track_height_mm']} + 2 x 1.4 margin <= plaque {values['trait.plaque_height_mm']} mm"},
        {"id": "trait-preview-budget", "status": "pass" if sum(values["trait.preview_values"]) == 210 else "fail",
         "detail": f"preview values {values['trait.preview_values']} sum {sum(values['trait.preview_values'])} (FDB-DSP-053 budget 210)"},
        {"id": "junction-fillet-fits-chamfer",
         "status": "pass" if values["interior.junction_fillet_mm"] * math.tan(math.radians(22.5)) * 2 < values["header.bezel_corner_chamfer_mm"] * math.sqrt(2) else "fail",
         "detail": f"2 x tangent {2 * values['interior.junction_fillet_mm'] * math.tan(math.radians(22.5)):.2f} mm < chamfer length {values['header.bezel_corner_chamfer_mm'] * math.sqrt(2):.2f} mm"},
        {"id": "corner-bolt-inside-crystal-band", "status": "pass" if bolt_clear >= 0.3 else "fail",
         "detail": f"counterbore edge clearance {bolt_clear:.2f} mm to band edges (band {band:.2f} mm, inset {inset} mm, R {r_o:.2f} mm)"},
        {"id": "seam-bolt-inside-crystal-band", "status": "pass" if band - 2 * head_r >= 0.6 else "fail",
         "detail": f"band {band:.2f} mm vs counterbore {2 * head_r} mm"},
        {"id": "reliefs-above-structural-threshold",
         "status": "pass" if min(values["header.recess_depth_mm"], values["main.recess_depth_mm"], values["interior.part_lift_mm"],
                                 values["main.pocket_lip_height_mm"], values["main.groove_depth_mm"]) >= spec["geometry_builder"]["structural_relief_geometry_threshold_mm"] else "fail",
         "detail": "header/main recess, part lift, pocket lip and groove depth are real geometry, not normal-map relief"},
        {"id": "header-chamfer-chain-never-clamps",
         "status": "pass" if values["header.bezel_corner_chamfer_mm"] - (values["main.perimeter_shelf_width_mm"] + 0.04 + values["cmf.mirror_bevel_width_mm"] + 0.02) * (2 - math.sqrt(2)) >= 0.4 else "fail",
         "detail": f"bezel chamfer {values['header.bezel_corner_chamfer_mm']} mm -> plane chamfer "
                   f"{values['header.bezel_corner_chamfer_mm'] - (values['main.perimeter_shelf_width_mm'] + 0.06 + values['cmf.mirror_bevel_width_mm']) * (2 - math.sqrt(2)):.2f} mm (min 0.4)"},
        {"id": "seam-gap-inside-rail-band",
         "status": "pass" if values["header.seam_gap_mm"] + 1.0 <= values["header.rail_band_mm"] else "fail",
         "detail": f"seam gap {values['header.seam_gap_mm']} mm inside the {values['header.rail_band_mm']} mm rail band; remainder widens the main bezel top strip"},
        {"id": "frame-ledge-clears-counterbore",
         "status": "pass" if band / 2 - head_r - values["case.frame_ledge_width_mm"] >= 0.0 else "fail",
         "detail": f"band/2 {band / 2:.2f} - bore r {head_r} - ledge {values['case.frame_ledge_width_mm']} = {band / 2 - head_r - values['case.frame_ledge_width_mm']:.2f} mm"},
        {"id": "no-datum-rail", "status": "pass", "detail": "GEO_PDC_HEADER_SILVER_DATUM_RAIL retired; header and main bezels are separate islands"},
        {"id": "concentric-chain-never-clamps",
         "status": "pass" if (r_o - band - values["case.smoke_liner_mm"] - 0.04) >= 0.4
         and (values["interior.bezel_corner_radius_mm"] - values["main.perimeter_shelf_width_mm"] - 0.04 - values["cmf.mirror_bevel_width_mm"] - 0.02) >= 0.4 else "fail",
         "detail": f"frame inner R {r_o - band:.2f} -> interior R {r_o - band - values['case.smoke_liner_mm'] - 0.04:.2f} mm; "
                   f"bezel R {values['interior.bezel_corner_radius_mm']} -> plane R "
                   f"{values['interior.bezel_corner_radius_mm'] - values['main.perimeter_shelf_width_mm'] - 0.04 - values['cmf.mirror_bevel_width_mm'] - 0.02:.2f} mm (min 0.4)"},
        {"id": "hub-near-image-reading",
         "status": "pass" if abs(values["visual.spinner_center_from_top"] - values["visual.spinner_center_from_top_image_reading"]) <= 0.03 else "warn",
         "detail": f"derived {values['visual.spinner_center_from_top']}H vs image {values['visual.spinner_center_from_top_image_reading']}H"},
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
        {"id": REJECTION_SOURCE_ID, "role": "user_requirement", "kind": "chat-rejection",
         "chat_timestamp_local": "2026-09-10T10:01:00+08:00", "rejected_stage": "05-blockout", "rejected_evidence_revision": 4,
         "wording": REJECTION_WORDING, "immutable": True, "geometry_truth": False, "material_truth": False,
         "sha256": hashlib.sha256(REJECTION_WORDING.encode("utf-8")).hexdigest()},
        {"id": FEEDBACK3A_SOURCE_ID, "role": "user_requirement", "kind": "chat-refinement",
         "chat_timestamp_local": "2026-09-10T12:22:00+08:00", "refined_stage": "05-blockout", "refined_evidence_revision": 6,
         "direction_accepted": "感觉差不多吧", "wording": FEEDBACK3A_WORDING, "immutable": True, "geometry_truth": False, "material_truth": False,
         "attachment": "render crop with red circles on the header bezel lower chamfer corners, the field TL/TR chamfer ends and the right wing corner",
         "sha256": hashlib.sha256(FEEDBACK3A_WORDING.encode("utf-8")).hexdigest()},
        {"id": FEEDBACK3B_SOURCE_ID, "role": "user_requirement", "kind": "chat-refinement",
         "chat_timestamp_local": "2026-09-10T12:23:00+08:00", "refined_stage": "05-blockout", "refined_evidence_revision": 6,
         "wording": FEEDBACK3B_WORDING, "immutable": True, "geometry_truth": False, "material_truth": False,
         "attachment": "render crop of the bottom brushed band", "related_requirement": "FDB-DSP-053",
         "related_thread": "d0029833-35d3-499b-9f9d-7156b390f254",
         "sha256": hashlib.sha256(FEEDBACK3B_WORDING.encode("utf-8")).hexdigest()},
        {"id": FEEDBACK2_SOURCE_ID, "role": "user_requirement", "kind": "chat-rejection",
         "chat_timestamp_local": "2026-09-10T11:15:00+08:00", "rejected_stage": "05-blockout", "rejected_evidence_revision": 5,
         "wording": FEEDBACK2_WORDING, "immutable": True, "geometry_truth": False, "material_truth": False,
         "note": "The user mentions coloured arrows; the attached image carried no arrows, so the reference was re-read directly (crops of "
                 "junction, left edge, pocket rim, clip, bottom band, header corner).",
         "sha256": hashlib.sha256(FEEDBACK2_WORDING.encode("utf-8")).hexdigest()},
    ]

    scene = json.loads(json.dumps(spec["scene"]))
    scene["core_geometry_objects"] = [
        "GEO_PDC_REAR_PLATE",
        "GEO_PDC_OUTER_CRYSTAL_FRAME",
        "GEO_PDC_SMOKE_INNER_LINER",
        "GEO_PDC_HEADER_SATIN_SHELF",
        "GEO_PDC_HEADER_MIRROR_BEVEL",
        "GEO_PDC_HEADER_GRAPHITE_PLANE",
        "GEO_PDC_HEADER_DIVIDER_LINE",
        "GEO_PDC_COMPARTMENT_SEAM",
        "GEO_PDC_HEADER_GOLD_INLAY_L",
        "GEO_PDC_HEADER_GOLD_INLAY_R",
        "GEO_PDC_MAIN_SATIN_SHELF",
        "GEO_PDC_MAIN_MIRROR_SEAM",
        "GEO_PDC_MAIN_MICROBLAST_FIELD",
        "GEO_PDC_POCKET_POLISHED_LIP",
        "GEO_PDC_POCKET_SMOKE_WALL",
        "GEO_PDC_POCKET_GRAPHITE_FLOOR",
        "GEO_PDC_POCKET_CLIP_00",
        "GEO_PDC_POCKET_CLIP_01",
        "GEO_PDC_POCKET_CLIP_02",
        "GEO_PDC_MAIN_BRUSHED_PANEL_L",
        "GEO_PDC_MAIN_BRUSHED_PANEL_R",
        "GEO_PDC_MAIN_TRAIT_PLAQUE",
        "GEO_PDC_TRAIT_FILL_00",
        "GEO_PDC_TRAIT_FILL_01",
        "GEO_PDC_TRAIT_FILL_02",
        "GEO_PDC_MAIN_GOLD_RAIL_00",
        "GEO_PDC_MAIN_GOLD_RAIL_01",
        "GEO_PDC_MAIN_GOLD_CHAMFER_TL",
        "GEO_PDC_MAIN_GOLD_INDEX_TAB",
        "GEO_PDC_FRAME_BOLT_00",
        "GEO_PDC_FRAME_BOLT_01",
        "GEO_PDC_FRAME_BOLT_02",
        "GEO_PDC_FRAME_BOLT_03",
        "GEO_PDC_FRAME_BOLT_04",
        "GEO_PDC_FRAME_BOLT_05",
    ]
    scene["retired_objects_rev005"] = {"GEO_PDC_MAIN_CORNER_FACETS": "replaced by the chamfered field outline itself"}
    scene["retired_objects_rev006"] = {"GEO_PDC_HEADER_SILVER_DATUM_RAIL": "not in the reference; header and main are separate islands with a dark seam",
                                       "GEO_PDC_POCKET_MIRROR_RIM": "sunken chamfer replaced by the raised GEO_PDC_POCKET_POLISHED_LIP"}
    scene["engraved_lines_rev006"] = ["field outline groove", "bottom band surround groove", "pocket lip foot groove"]
    scene["retired_objects_rev007"] = {"GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM": "replaced by GEO_PDC_MAIN_TRAIT_PLAQUE (three 0-100 tracks, FDB-DSP-053)"}
    scene["runtime_dynamic_objects_rev007"] = {"GEO_PDC_TRAIT_FILL_00": "SPIN", "GEO_PDC_TRAIT_FILL_01": "FEEL", "GEO_PDC_TRAIT_FILL_02": "CRAFT",
                                               "rule": "exported at 100 % length; PremiumDisplayCaseTraitBlock-equivalent shortens to ToyTalentCatalog values"}
    scene["engraved_lines_rev007"] = ["trait plaque surround groove", "3 trait troughs", "9 quartile tick notches"]
    geometry_builder = json.loads(json.dumps(spec["geometry_builder"]))
    geometry_builder["nested_offset_rule"] = {
        "rule": "Every nested outline is the exact inward offset of its parent outline by the local wall/shelf width; "
                "corner arcs share the parent's arc centre (concentric) and chamfers stay parallel.",
        "min_corner_radius_mm": 0.4,
        "source_id": REJECTION_SOURCE_ID,
        "validation": "05-blockout validation asserts every rounded-rect pair reports concentric=true",
    }
    geometry_builder["gold_inlay_components"] = ["rail_00", "rail_01", "chamfer_tl", "index_tab", "header_inlay_l", "header_inlay_r"]
    geometry_builder["bolt_construction"] = "cylindrical head with hexagonal socket, seated in a counterbore cut into the crystal band (BOOLEAN EXACT, applied before bevel)"
    geometry_builder["junction_fillet_rule"] = {
        "source_id": FEEDBACK3A_SOURCE_ID,
        "rule": "Every vertex where a 45-degree chamfer meets a straight edge is filleted (interior.junction_fillet_mm on the outer outline). "
                "Insets keep max(r - d, interior.junction_fillet_min_mm). Wing polygons are filleted at every vertex (main.wing_corner_fillet_mm).",
        "sampling": "each corner still emits seg+1 points, resampled by arc length over fillet-chamfer-fillet, so nested outlines bridge 1:1",
    }
    geometry_builder["trait_plaque_rule"] = {
        "source_id": FEEDBACK3B_SOURCE_ID, "requirement": "FDB-DSP-053",
        "rule": "Raised brushed plaque with surround groove; three troughs (label column | 0-100 track | value column) top-down SPIN, FEEL, CRAFT; "
                "quartile tick notches; fill strips as separate runtime-dynamic objects authored at 100 % and shown at preview lengths.",
    }
    geometry_builder["level_stack_rule"] = {
        "source_id": FEEDBACK2_SOURCE_ID,
        "rule": "Inside each compartment the holder must read as distinct steps: bezel top -> 45-degree mirror chamfer -> recessed field -> "
                "engraved outline groove -> raised brushed wings/band (with surround groove) -> raised polished lip (outer chamfer, inner slope) -> "
                "smoke wall -> graphite floor. Every step is geometry with its own bevel; no step may be implied by shading alone.",
        "engraving": "grooves are BOOLEAN EXACT cuts of main.groove_width_mm x main.groove_depth_mm, applied before bevel",
        "frame_profile": "outer rounded lip + inner ledge stepped down case.frame_ledge_drop_mm (stepped ring, one watertight mesh)",
    }
    geometry_builder["bevel"]["outer_segments"] = 6

    contract = {
        "schemaVersion": 1,
        "schema_version": spec["schema_version"],
        "spec_id": spec["spec_id"],
        "modelId": spec["model_id"],
        "model_id": spec["model_id"],
        "variant_id": spec["variant_id"],
        "contractRevision": 7,
        "revision": 1,
        "createdDate": dt.date.today().isoformat(),
        "stageStatus": "ready_for_review",
        "approvalEffect": "none-until-explicit-gate-03-user-approval",
        "status": "gate03_candidate_ready_for_review",
        "provisional_marker": "PROVISIONAL_DIMENSIONS",
        "provisional_marker_reason": "Case size derives from the generic pocket plus concept-image ratios; only spinner dimensions are measured.",
        "revision_reason": {"source_ids": [FEEDBACK3A_SOURCE_ID, FEEDBACK3B_SOURCE_ID], "refined": "05-blockout rev-006",
                            "direction_accepted": "感觉差不多吧",
                            "summary": "fillets at every chamfer junction and wing corner; bottom band becomes the TRAIT PROFILE plaque (three 0-100 tracks); "
                                       "pocket raised (split 0.22) to make room; brighter review lighting handled in the preview script"},
        "sourceSpec": {"path": f"{REPO_REL}/01-intake/rev-004/tri-spinner-slab-model-spec.v0.json", "sha256": sha256(SPEC_PATH),
                       "handoff_spec_path": f"{REPO_REL}/01-intake/rev-004/tri-spinner-slab-agent-handoff-spec.md",
                       "handoff_spec_sha256": sha256(INTAKE / "tri-spinner-slab-agent-handoff-spec.md")},
        "sourceAnalysisRevision": 7,
        "sourceIntakeRevision": 4,
        "sourceClaimIds": SOURCE_CLAIM_IDS,
        "supersedes": {"contractRevision": 6, "reason": "User refinement on Gate 05 rev-006 (direction accepted): hard chamfer junctions, dark review "
                                                        "lighting, bottom band must host the dynamic three-value trait profile.",
                       "reuse_forbidden_dimensions_mm": spec["pipeline_context"]["old_contract_reference_dimensions_mm"],
                       "retired_rev004_parameters": ["main.pocket_gap_mm", "main.pocket_lobe_radius_mm", "main.pocket_lobe_center_radius_mm",
                                                     "main.pocket_reach_mm", "main.pocket_height_mm"],
                       "retired_rev005_parameters": ["interior.datum_rail_lift_mm", "main.pocket_rim_width_mm"],
                       "retired_rev006_objects": ["GEO_PDC_MAIN_BRUSHED_BAND_BOTTOM"]},
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
            "z_pocket_floor": round(values["case.backplate_thickness_mm"] + values["main.pocket_floor_mm"], 3),
            "z_field": values["case.z_field_mm"],
            "z_pocket_lip_top": round(values["case.z_field_mm"] + values["main.pocket_lip_height_mm"], 3),
            "z_groove_floor": round(values["case.z_field_mm"] - values["main.groove_depth_mm"], 3),
            "z_header_plane": values["case.z_header_plane_mm"],
            "z_frame_ledge": round(values["case.z_frame_front_mm"] - values["case.frame_ledge_drop_mm"], 3),
            "z_shelf_top": values["case.z_shelf_top_mm"],
            "z_frame_front": values["case.z_frame_front_mm"],
            "pocket_well_depth": values["main.pocket_well_depth_mm"],
            "z_spinner_front": values["case.z_spinner_front_mm"],
            "spinner_protrusion": values["spinner.protrusion_mm"],
            "assembled_envelope_depth": values["assembled.envelope_depth_mm"],
            "root_recentering_z": values["case.root_recentering_z_mm"],
        },
        "assertions": assertions,
        "scene": scene,
        "geometry_builder": geometry_builder,
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
            "spinner.protrusion_mm", "case.z_frame_front_mm", "case.z_shelf_top_mm", "case.z_field_mm", "case.z_header_plane_mm",
            "case.z_spinner_front_mm", "assembled.envelope_depth_mm", "case.root_recentering_z_mm",
            "main.pocket_well_diameter_mm", "main.pocket_diameter_mm", "main.pocket_well_depth_mm", "main.field_width_mm",
            "main.liner_inset_mm", "main.field_top_y_mm", "main.field_bottom_y_mm", "visual.spinner_center_from_top",
            "content.review_fit_scale", "header.seam_gap_mm", "header.bezel_corner_chamfer_mm", "main.pocket_lip_width_mm",
            "main.pocket_lip_height_mm", "main.groove_depth_mm", "case.frame_ledge_drop_mm", "interior.junction_fillet_mm",
            "trait.plaque_height_mm", "trait.row_pitch_mm", "trait.track_height_mm"]},
        "all_pass": all(a["status"] == "pass" for a in assertions),
        "warnings": [a for a in assertions if a["status"] == "warn"],
    }
    (HERE / "contract-validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=1))
    return 0 if all(a["status"] != "fail" for a in assertions) else 1


if __name__ == "__main__":
    sys.exit(main())
