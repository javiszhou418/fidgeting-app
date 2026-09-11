"""Export the Gate 02 rev-006 geometry (CAD v16 / spec v17) as a machine-readable contract for the Blender blockout.

Everything is in R units (R = outer radius). The Blender builder scales by the provisional 85 mm.
Loops are stored as radius-vs-polar-angle tables (the rotor planform and its inward offsets are star-shaped),
so the builder can zip loops vertex-to-vertex by angle.

    python3 export_geeone_gate02_geometry.py  ->  evidence/05-blockout/rev-006/geeone-gate02-geometry-contract.json
"""

from __future__ import annotations

import hashlib
import json
import sys
import math
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

import draw_geeone_reference_cad_v17 as cad
import shade_geeone_reference_v17 as sh

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/06-geometry/rev-006"
SPEC = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/02-analysis/rev-006/surface-detail-spec.json"
BLADE_ANGLES = (90, 210, 330)
N_THETA = 1440  # angle samples per loop (0.25°)


def rotp(pts, deg):
    a = math.radians(deg)
    return [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in pts]


def rotor_mask_and_offsets():
    """Rasterise the full rotor planform (3 blades + hub disc) and pull inward-offset contours from the EDT."""
    half = cad.planform_half()
    full = half + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    full = sh.resample_smooth(full)
    N = sh.N
    mask = np.zeros((N, N), dtype=bool)
    for ang in BLADE_ANGLES:
        mask |= sh.mask_poly(rotp(full, ang))
    r = np.hypot(sh.X, sh.Y)
    mask |= r < cad.CAP  # hub under the cap
    d_in = ndimage.distance_transform_edt(mask) * sh.PX
    return mask, d_in


def contour_radius_table(field: np.ndarray, level: float, n_theta: int = N_THETA):
    """Iso-contour of `field` at `level` -> r(theta) table (star-shaped loop, longest closed path)."""
    fig = plt.figure()
    cs = plt.contour(sh.X, sh.Y, field, levels=[level])
    paths = []
    for coll in cs.allsegs[0]:
        if len(coll) > 50:
            paths.append(np.asarray(coll))
    plt.close(fig)
    best = max(paths, key=lambda p: len(p))
    th = np.arctan2(best[:, 1], best[:, 0]) % (2 * math.pi)
    rr = np.hypot(best[:, 0], best[:, 1])
    order = np.argsort(th)
    th, rr = th[order], rr[order]
    # de-duplicate angles, then periodic interpolation onto a uniform grid
    th_u, idx = np.unique(np.round(th, 6), return_index=True)
    rr_u = rr[idx]
    grid = np.linspace(0, 2 * math.pi, n_theta, endpoint=False)
    th_ext = np.concatenate([th_u - 2 * math.pi, th_u, th_u + 2 * math.pi])
    rr_ext = np.concatenate([rr_u, rr_u, rr_u])
    return np.interp(grid, th_ext, rr_ext).tolist()


def outline_radius_table(mask: np.ndarray, n_theta: int = N_THETA):
    """r(theta) of the rotor outline itself (level 0.5 of the mask)."""
    return contour_radius_table(mask.astype(float), 0.5, n_theta)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    by = {d["id"]: d for d in spec["details"]}
    mask, d_in = rotor_mask_and_offsets()
    r_out = outline_radius_table(mask)
    r_a = contour_radius_table(d_in, cad.BAND_W)  # kite/Λ band inner edge = tier-A outer edge
    r_p = contour_radius_table(d_in, cad.BEVEL_W)  # plateau boundary (top facets)
    # sanity: star-shaped and nested
    r_out_a, r_a_a, r_p_a = np.array(r_out), np.array(r_a), np.array(r_p)
    assert np.all(r_a_a < r_out_a + 1e-6) and np.all(r_p_a < r_a_a + 1e-6), "offset loops are not nested"

    tiers = by["UTS-D05"]["params"]["tiers"]
    fam = by["UTS-D05"]["params"]["facetFamilies"]
    d8 = by["UTS-D08"]["params"]
    contract = {
        "modelId": "metal-three-blade",
        "source": {"stage": "02-analysis", "revision": 6, "spec": "evidence/02-analysis/rev-006/surface-detail-spec.json", "specSha256": hashlib.sha256(SPEC.read_bytes()).hexdigest(), "cad": "tools/model-provenance-explorer/draw_geeone_reference_cad_v17.py", "generatedOn": date.today().isoformat()},
        "units": "R (outer radius). mm scale is user-authorized-provisional: 2R = 85 mm (controller 2026-09-05 23:14); all mm are not measured",
        "scale": {"diameterMmProvisional": 85.0},
        "bladeAnglesDeg": list(BLADE_ANGLES),
        "body": {"thicknessToR": cad.BODY_T, "crestRiseToR": cad.CREST, "mirrorBottom": True},
        "loops": {"nTheta": N_THETA, "thetaStartDeg": 0.0, "outline": r_out, "tierA": r_a, "plateau": r_p,
                  "note": "r(theta) tables; outline = blade edges + hub arcs (r=cap) in the notches; tierA = inward offset bandWidth; plateau = inward offset transitionWidth"},
        "capRadiusToR": cad.CAP,
        "topPlanes": {"frame": "blade-local (x along the blade axis outward, y across); z = a x + b y + c; surface = min over the six planes; hub (r < capRadius) is flattened by the cap-seat boolean",
                      "planes": [{"name": n, "a": a, "b": b, "c": c} for n, a, b, c in cad.TOP_PLANES]},
        "edgeTransition": {"transitionWidthToR": cad.BEVEL_W, "tierAWidthToR": cad.TIER_A_W, "bandWidthToR": cad.BAND_W,
                           "tierASlopeDeg": tiers[0]["slopeDeg"], "tierAFacetLengthToR": tiers[0].get("facetLengthToR", 0.25),
                           "kiteSlopeDeg": fam["kite"]["slopeDeg"], "lambdaSlopeDeg": fam["lambda"]["slopeDeg"],
                           "kiteTipBandFraction": fam["kite"]["tipAtBandFraction"], "lambdaTipBandFraction": fam["lambda"]["tipAtBandFraction"],
                           "kitePitchToR": by["UTS-D05"]["params"]["scaleLengthToR"], "normalise": "slopes scaled so the Λ facets end on the mid-plane"},
        "pocket": {"mouth": cad.mouth_polygon(), "floor": cad.floor_polygon(), "depthFractionOfThicknessPerSide": d8["depthFractionOfThicknessPerSide"],
                   "edgeFilletTopToR": cad.POCKET_FILLET_TOP, "edgeFilletFloorToR": cad.POCKET_FILLET_FLOOR, "mouthOffsetToR": cad.MOUTH_OFF, "floorOffsetToR": cad.FLOOR_OFF,
                   "frame": "blade-local, open toward the cap (mouth base beyond the cap circle is inside the cap-seat cut)"},
        "cap": {"radiusToR": cad.CAP, "tableToCap": cad.TABLE, "sectors": cad.N_SECTOR, "dishSlopeDeg": cad.DISH_SLOPE_DEG, "sideHeightToR": cad.CAP_SIDE_H,
                "sectorAltTiltDeg": by["UTS-D01"]["params"].get("sectorAltTiltDegProvisional", 0.0), "sectorCreaseHighlightBevelMm": by["UTS-D01"]["params"].get("sectorCreaseHighlightBevelMm", 0.0),
                "tiers": cad.CAP_TIERS, "wedges": cad.N_WEDGE, "skirtFacets": cad.N_SKIRT,
                "verticalSideToR": 0.0, "capOverhangToR": cad.CAP_OVERHANG, "hubSeatRadiusToR": cad.HUB_SEAT_R, "hubSeatHeightToR": cad.HUB_SEAT_H,
                "hubCoreRadiusToR": by["UTS-D03"]["params"].get("hubCoreRadiusToR", cad.HUB_SEAT_R), "hubCoreStatic": by["UTS-D03"]["params"].get("hubCoreStatic", False),
                "rotorBoreRadiusToR": by["UTS-D03"]["params"].get("rotorBoreRadiusToR", 0.0), "bearingGapToR": by["UTS-D03"]["params"].get("bearingGapToR", 0.0),
                "kinematics": {"fixed": ["Cap_Top", "Cap_Bottom", "Hub_Core"], "rotating": ["Rotor_Body"], "axis": "Z", "note": by["UTS-D03"]["params"].get("kinematicNote", "")},
                "seamNote": "user 2026-09-07 18:33: the cap rim overhangs a recessed hub seat; the dark seam is the shadow under the lip (overhang provisional)"},
        "notch": by["UTS-D09"]["params"],
    }
    out = OUT_DIR / "geeone-gate02-geometry-contract.json"
    out.write_text(json.dumps(contract, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out, "planes", len(cad.TOP_PLANES), "r_out[0..3]", [round(v, 3) for v in r_out[:3]], "min/max r_p", round(min(r_p), 3), round(max(r_p), 3))


if __name__ == "__main__":
    main()
