"""Export the unified tri-spinner 2D CAD geometry as JSON.

Runs inside Blender so it can import the builder and reuse its outline and
roof functions; nothing is re-derived here. Output feeds
`tools/model-provenance-explorer/draw_unified_tri_spinner_cad.py`.

    Blender --background --python tools/blender/export_unified_tri_spinner_cad.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS_DIR))
import build_unified_tri_spinner as B  # noqa: E402

MM = 1000.0


def rotate(points, degrees):
    a = math.radians(degrees)
    return [(x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)) for x, y in points]


def notch_apex(half):
    """Intersection of this petal's upper side with the neighbour's lower side
    (the neighbour is this petal rotated +120 deg). Both are the first side
    segment leaving p0, so the apex is where those two lines cross."""
    p0, p1 = half[1], half[2]
    q0, q1 = rotate([(p0[0], -p0[1]), (p1[0], -p1[1])], 120.0)
    # solve p0 + t (p1 - p0) = q0 + u (q1 - q0)
    dx1, dy1 = p1[0] - p0[0], p1[1] - p0[1]
    dx2, dy2 = q1[0] - q0[0], q1[1] - q0[1]
    det = dx1 * dy2 - dy1 * dx2
    t = ((q0[0] - p0[0]) * dy2 - (q0[1] - p0[1]) * dx2) / det
    return (p0[0] + t * dx1, p0[1] + t * dy1)


def main() -> None:
    half = B.with_plane_intersections(B.blade_outline())
    apex = notch_apex(half)
    # Visible plan outline of one petal: apex -> side (points with r > apex r) -> arc -> mirrored side -> apex
    upper = [apex] + [p for p in half[2:] if math.hypot(*p) > math.hypot(*apex)]
    lower = [(x, -y) for x, y in reversed(upper) if y > 1e-9]
    petal_plan = upper + lower
    union_plan = []
    for angle in B.BLADE_ANGLES:
        union_plan.extend(rotate(petal_plan, angle))

    # Cap profile in the axial half-plane (r, z), nominal cone line + rim envelope
    rim_hi = B.RIM_Z + B.ZIGZAG
    rim_lo = B.RIM_Z - B.ZIGZAG
    cap_profile = [(0.0, B.TABLE_Z), (B.TABLE_R, B.TABLE_Z), (B.CAP_R, B.RIM_Z), (B.CAP_R, B.SKIRT_BOTTOM_Z), (B.STEM_R, B.SKIRT_BOTTOM_Z), (B.STEM_R, 0.0005)]

    # Blade axial section (x along the blade, z): ridge then end plane
    axial_top = [(B.SEAM_R, B.BODY_HALF), (B.END_PLANE_X, B.BODY_HALF), (B.TIP_R, B.roof_height(B.TIP_R, 0.0))]
    widest = max(half, key=lambda p: p[1])
    transverse = [(y, B.roof_height(widest[0], y)) for y in (-widest[1], 0.0, widest[1])]

    wedge_ring = []
    for j in range(B.N_WEDGE):
        a_in = math.tau * j / B.N_WEDGE
        a_out = math.tau * (j + 0.5) / B.N_WEDGE
        wedge_ring.append({
            "inner": [B.TABLE_R * math.cos(a_in) * MM, B.TABLE_R * math.sin(a_in) * MM, B.TABLE_Z * MM],
            "outer": [B.CAP_R * math.cos(a_out) * MM, B.CAP_R * math.sin(a_out) * MM, (rim_hi if j % 2 == 0 else rim_lo) * MM],
        })

    data = {
        "revision": B.REV,
        "units": "mm",
        "provisional": True,
        "constants": {
            "tipR": B.TIP_R * MM, "capR": B.CAP_R * MM, "tableR": B.TABLE_R * MM, "seamR": B.SEAM_R * MM,
            "capRatio": B.CAP_RATIO, "tableRatio": B.TABLE_RATIO, "seamW": B.SEAM_W * MM,
            "tableZ": B.TABLE_Z * MM, "rimZ": B.RIM_Z * MM, "rimHiZ": rim_hi * MM, "rimLoZ": rim_lo * MM, "zigzag": B.ZIGZAG * MM,
            "slopeDeg": B.WEDGE_SLOPE_DEG, "skirtBottomZ": B.SKIRT_BOTTOM_Z * MM, "coreHalf": B.CORE_HALF * MM,
            "coreR": (B.SEAM_R - 0.0003) * MM, "boreR": B.BORE_R * MM, "stemR": B.STEM_R * MM,
            "bladeT": B.BLADE_T * MM, "bodyHalf": B.BODY_HALF * MM,
            "roofSlope": B.ROOF_SLOPE, "roofSlopeDeg": math.degrees(math.atan(B.ROOF_SLOPE)),
            "endPlaneX": B.END_PLANE_X * MM, "endPlaneSlopeDeg": math.degrees(math.atan(B.END_PLANE_SLOPE)),
            "tipArcR": B.TIP_ARC_R * MM, "tipArcC": B.TIP_ARC_C * MM, "tipArcJoinDeg": B.TIP_ARC_JOIN_DEG,
            "notchVDeg": 2.0 * B.NOTCH_HALF_DEG, "nWedge": B.N_WEDGE, "bevel": B.BLADE_BEVEL * MM, "bevelSegments": B.BLADE_BEVEL_SEGMENTS,
            "bearing": {"od": 12.7, "id": 6.35, "width": 4.76},
            "bladeAnglesDeg": list(B.BLADE_ANGLES),
        },
        "bladeHalfOutline": [[x * MM, y * MM, B.roof_height(x, y) * MM] for x, y in half],
        "notchApex": [apex[0] * MM, apex[1] * MM, math.hypot(*apex) * MM],
        "petalPlan": [[x * MM, y * MM] for x, y in petal_plan],
        "unionPlan": [[x * MM, y * MM] for x, y in union_plan],
        "bladeWidest": {"x": widest[0] * MM, "halfWidth": widest[1] * MM, "wallTopZ": B.roof_height(*widest) * MM},
        "capProfile": [[r * MM, z * MM] for r, z in cap_profile],
        "axialTop": [[x * MM, z * MM] for x, z in axial_top],
        "transverseTop": [[y * MM, z * MM] for y, z in transverse],
        "wedgeRing": wedge_ring,
    }
    out = B.GEOMETRY_DIR / "cad-geometry.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("CAD_GEOMETRY " + str(out))


if __name__ == "__main__":
    main()
