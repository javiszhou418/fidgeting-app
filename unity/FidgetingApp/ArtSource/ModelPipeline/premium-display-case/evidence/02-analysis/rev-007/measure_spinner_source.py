"""Gate 02 rev-007: measure the caller-owned spinner source model.

Run inside Blender:
    blender -b --python measure_spinner_source.py

Reads the shipping `UnifiedTriSpinner.glb` (metal-three-blade Gate 10 export),
and writes `spinner-source-measurement.json` next to this script. These are
`measured` values: they come from the real source geometry, not from an image.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
GLB = REPO / "unity/FidgetingApp/ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.glb"
BLEND = REPO / "unity/FidgetingApp/ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.blend"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    mins = Vector((math.inf,) * 3)
    maxs = Vector((-math.inf,) * 3)
    rotor_tip_radius = 0.0
    parts = []
    for o in meshes:
        world = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector((min(p.x for p in world), min(p.y for p in world), min(p.z for p in world)))
        mx = Vector((max(p.x for p in world), max(p.y for p in world), max(p.z for p in world)))
        for i in range(3):
            mins[i] = min(mins[i], mn[i])
            maxs[i] = max(maxs[i], mx[i])
        rmax = max(((o.matrix_world @ v.co).xy.length for v in o.data.vertices), default=0.0)
        if o.name.startswith("RotorBody"):
            rotor_tip_radius = max(rotor_tip_radius, rmax)
        parts.append({
            "name": o.name,
            "parent": o.parent.name if o.parent else None,
            "bbox_min_mm": [round(v * 1000, 3) for v in mn],
            "bbox_max_mm": [round(v * 1000, 3) for v in mx],
            "max_radius_from_axis_mm": round(rmax * 1000, 3),
            "triangles": sum(len(p.vertices) - 2 for p in o.data.polygons),
            "materials": [m.name for m in o.data.materials],
        })
    size = [(maxs[i] - mins[i]) * 1000 for i in range(3)]
    # glTF import: spin axis = Blender +Z; the front-view plane is Blender XY,
    # +Y is one tip pointing up. Canonical mapping for the slab review pose:
    # canonical +X = Blender +X, canonical +Y = Blender +Y, canonical +Z = Blender +Z.
    result = {
        "schema": "premium-display-case.gate02.spinner-source-measurement/1",
        "evidence_class": "measured",
        "value_state": "measured",
        "source": {
            "path": "unity/FidgetingApp/ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.glb",
            "sha256": sha256(GLB),
            "blend_path": "unity/FidgetingApp/ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.blend",
            "blend_sha256": sha256(BLEND),
            "owner_pipeline": "metal-three-blade",
            "role": "caller-owned/immutable-geometry",
        },
        "blender_version": bpy.app.version_string,
        "pose": "as imported: spin axis +Z, one tip toward +Y",
        "measurements_mm": {
            "tip_circle_diameter": round(rotor_tip_radius * 2000, 3),
            "horizontal_span_one_tip_up": round(size[0], 3),
            "vertical_span_one_tip_up": round(size[1], 3),
            "max_thickness_including_caps": round(size[2], 3),
            "rotor_body_thickness": round(next(p for p in parts if p["name"] == "RotorBody_OnePiece")["bbox_max_mm"][2]
                                          - next(p for p in parts if p["name"] == "RotorBody_OnePiece")["bbox_min_mm"][2], 3),
            "assembly_bbox_min": [round(v * 1000, 3) for v in mins],
            "assembly_bbox_max": [round(v * 1000, 3) for v in maxs],
            "pivot_in_source_units": [0.0, 0.0, 0.0],
            "pivot_z_is_mid_thickness": abs(mins.z + maxs.z) < 1e-6,
        },
        "span_basis_options": {
            "bbox_x_one_tip_up": round(size[0], 3),
            "tip_circle_diameter": round(rotor_tip_radius * 2000, 3),
            "note": "The spec's `spinner.max_span_mm` says 'bounds'; the V3 image ratio 0.762W was read tip-to-tip in the "
                    "one-tip-up pose, so the contract uses bbox_x. The tip-circle alternative is recorded for the user.",
        },
        "parts": parts,
    }
    (HERE / "spinner-source-measurement.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["measurements_mm"], indent=1))


main()
