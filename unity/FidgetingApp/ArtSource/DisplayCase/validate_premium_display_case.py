"""Fail-fast validation for PremiumDisplayCase.blend and its Unity FBX."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


EXPECTED_LAYERS = [f"Layer_{index:02d}_{suffix}" for index, suffix in (
    (1, "FrontPlate"),
    (2, "Fasteners"),
    (3, "SpacerFrame"),
    (4, "Capsule"),
    (5, "VelvetInsert"),
    (6, "RearPlate"),
    (7, "OuterTray"),
    (8, "BoxLid"),
)]
EXPECTED_FASTENERS = {"Fastener_TL", "Fastener_TR", "Fastener_BL", "Fastener_BR"}
EXPECTED_COLLARS = {
    "ChromeCollar_TL",
    "ChromeCollar_TR",
    "ChromeCollar_BL",
    "ChromeCollar_BR",
}
FORBIDDEN_PRIZE_WORDS = ("trinity", "tri-blade", "spinner", "prize", "reward")
FORBIDDEN_OPAQUE_SHELLS = {"MatteBlack_OuterTray", "MatteBlack_BoxLid"}


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector(tuple(min(point[axis] for point in points) for axis in range(3))),
        Vector(tuple(max(point[axis] for point in points) for axis in range(3))),
    )


def main() -> None:
    source_dir = Path(bpy.data.filepath).resolve().parent
    unity_root = source_dir.parent.parent
    fbx_path = unity_root / "Assets" / "_DisplayCase" / "Models" / "PremiumDisplayCase.fbx"
    output_dir = unity_root / "Artifacts" / "PremiumDisplayCaseValidation"
    output_dir.mkdir(parents=True, exist_ok=True)

    names = set(bpy.data.objects.keys())
    missing_layers = [name for name in EXPECTED_LAYERS if name not in names]
    fasteners = {name for name in names if name.startswith("Fastener_")}
    collars = {name for name in names if name.startswith("ChromeCollar_")}
    forbidden = sorted(
        name for name in names
        if any(word in name.lower() for word in FORBIDDEN_PRIZE_WORDS))
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    minimum, maximum = world_bounds(mesh_objects)
    dimensions_mm = tuple(round((maximum[i] - minimum[i]) * 1000, 3) for i in range(3))

    errors: list[str] = []
    if "PremiumDisplayCase_Model" not in names:
        errors.append("missing PremiumDisplayCase_Model root")
    if missing_layers:
        errors.append(f"missing layers: {missing_layers}")
    if fasteners != EXPECTED_FASTENERS:
        errors.append(f"fasteners differ: {sorted(fasteners)}")
    if collars != EXPECTED_COLLARS:
        errors.append(f"fastener collars differ: {sorted(collars)}")
    opaque_shells = sorted(names.intersection(FORBIDDEN_OPAQUE_SHELLS))
    if opaque_shells:
        errors.append(f"reference style forbids opaque outer shells: {opaque_shells}")
    if forbidden:
        errors.append(f"prize-specific names found: {forbidden}")
    if "ContentSlot_Anchor" not in names:
        errors.append("missing ContentSlot_Anchor")
    if not fbx_path.exists() or fbx_path.stat().st_size < 100_000:
        errors.append("Unity FBX missing or unexpectedly small")
    # Blender axes are X width, Y depth, Z height.
    if not (0.180 <= dimensions_mm[0] / 1000 <= 0.195):
        errors.append(f"unexpected width: {dimensions_mm[0]} mm")
    # The reference model is a slim clear-acrylic stack. Full depth includes
    # the projecting black fastener heads and the rear acrylic reinforcement.
    if not (0.050 <= dimensions_mm[1] / 1000 <= 0.060):
        errors.append(f"unexpected depth: {dimensions_mm[1]} mm")
    if not (0.235 <= dimensions_mm[2] / 1000 <= 0.245):
        errors.append(f"unexpected height: {dimensions_mm[2]} mm")

    capsule = bpy.data.objects.get("Capsule_CircularRing")
    if capsule is None:
        errors.append("missing clear central capsule ring")
    else:
        capsule_width_mm = round(capsule.dimensions.x * 1000, 3)
        if not (95.0 <= capsule_width_mm <= 97.0):
            errors.append(f"unexpected capsule outer diameter: {capsule_width_mm} mm")

    for fastener_name in EXPECTED_FASTENERS:
        fastener = bpy.data.objects.get(fastener_name)
        materials = [] if fastener is None else list(fastener.data.materials)
        if not materials or materials[0].name != "MAT_MatteBlackBox":
            errors.append(f"{fastener_name} is not a black cap")

    report = {
        "passed": not errors,
        "blend": str(Path(bpy.data.filepath).resolve()),
        "fbx": str(fbx_path),
        "meshObjectCount": len(mesh_objects),
        "layerCount": len([name for name in EXPECTED_LAYERS if name in names]),
        "fasteners": sorted(fasteners),
        "fastenerCollars": sorted(collars),
        "style": "clear-acrylic-four-fastener",
        "hasOpaqueOuterBox": bool(opaque_shells),
        "worldDimensionsMm": {
            "widthX": dimensions_mm[0],
            "depthY": dimensions_mm[1],
            "heightZ": dimensions_mm[2],
        },
        "containsPrizeGeometry": bool(forbidden),
        "errors": errors,
    }
    report_path = output_dir / "blender_validation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
