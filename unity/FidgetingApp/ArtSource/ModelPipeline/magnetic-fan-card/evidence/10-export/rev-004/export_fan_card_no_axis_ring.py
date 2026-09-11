"""Remove forbidden front-axis hardware and rebuild the Fan Card export."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


SCRIPT_PATH = Path(__file__).resolve()
REVISION_DIR = SCRIPT_PATH.parent
SOURCE_BLEND = REVISION_DIR.parent / "rev-003/magnetic-fan-card-export-ready.blend1"
OUTPUT_BLEND = REVISION_DIR / "magnetic-fan-card-no-axis-ring.blend"
OUTPUT_FBX = REVISION_DIR / "magnetic-fan-card-no-axis-ring.fbx"
OUTPUT_GLB = REVISION_DIR / "magnetic-fan-card-no-axis-ring.glb"
COLLISION_FBX = REVISION_DIR / "magnetic-fan-card-collision.fbx"
REPORT_PATH = REVISION_DIR / "no-axis-ring-export-report.json"

FORBIDDEN_AXIS_TOKENS = (
    "bearingcap",
    "ring",
    "washer",
    "axisseat",
    "coverdisc",
    "chromeball",
    "ballseat",
)
ALLOWED_VISIBLE_AXIS_OBJECT = "CommonAxis_RecessedMatteSpindle"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def triangle_count(obj: bpy.types.Object) -> int:
    return sum(max(0, len(polygon.vertices) - 2) for polygon in obj.data.polygons)


def select(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_fbx(path: Path, objects: list[bpy.types.Object]) -> None:
    select(objects)
    bpy.ops.export_scene.fbx(
        filepath=str(path),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        object_types={"EMPTY", "MESH"},
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        mesh_smooth_type="FACE",
        use_subsurf=False,
        use_mesh_edges=False,
        use_tspace=True,
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        axis_forward="-Z",
        axis_up="Y",
    )


def main() -> None:
    if not SOURCE_BLEND.exists():
        raise FileNotFoundError(SOURCE_BLEND)

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    source_meshes = {
        obj.name: triangle_count(obj)
        for obj in bpy.data.objects
        if obj.type == "MESH"
    }
    cap = bpy.data.objects.get("CommonAxis_BearingCap_Chrome")
    if cap is None or cap.type != "MESH":
        raise RuntimeError("Expected the rejected chrome bearing cap in rev-003.")
    removed_cap_triangles = triangle_count(cap)
    bpy.data.objects.remove(cap, do_unlink=True)

    root = bpy.data.objects.get("MagneticFanCard_Root")
    spindle = bpy.data.objects.get(ALLOWED_VISIBLE_AXIS_OBJECT)
    if root is None or spindle is None or spindle.type != "MESH":
        raise RuntimeError("The root or recessed matte spindle is missing.")
    root["front_visible_axis_hardware"] = "recessed_matte_spindle_only"
    root["forbidden_axis_ring_rule"] = (
        "No cap, chrome disc, annular ring, washer, axis seat, cover disc, or ball"
    )

    forbidden_objects = [
        obj.name
        for obj in bpy.data.objects
        if "axis" in obj.name.lower()
        and any(token in obj.name.lower() for token in FORBIDDEN_AXIS_TOKENS)
    ]
    if forbidden_objects:
        raise RuntimeError(f"Forbidden axis objects remain: {forbidden_objects}")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    export_objects = [
        obj
        for obj in bpy.data.objects
        if obj.type in {"EMPTY", "MESH"}
    ]
    export_fbx(OUTPUT_FBX, export_objects)

    select(export_objects)
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT_GLB),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_extras=True,
    )

    collision_meshes = [
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name.startswith("COLLIDER_")
    ]
    collision_parents = list({
        obj.parent
        for obj in collision_meshes
        if obj.parent is not None
    })
    if root not in collision_parents:
        collision_parents.append(root)
    export_fbx(COLLISION_FBX, [*collision_parents, *collision_meshes])

    output_meshes = {
        obj.name: triangle_count(obj)
        for obj in bpy.data.objects
        if obj.type == "MESH"
    }
    unchanged_meshes = {
        name: triangles
        for name, triangles in source_meshes.items()
        if name != "CommonAxis_BearingCap_Chrome"
    }
    if output_meshes != unchanged_meshes:
        raise RuntimeError("Removing the cap changed unrelated mesh topology.")

    report = {
        "source_blend": str(SOURCE_BLEND),
        "source_sha256": sha256(SOURCE_BLEND),
        "output_blend": str(OUTPUT_BLEND),
        "output_fbx": str(OUTPUT_FBX),
        "output_glb": str(OUTPUT_GLB),
        "collision_fbx": str(COLLISION_FBX),
        "removed_object": "CommonAxis_BearingCap_Chrome",
        "removed_cap_triangles": removed_cap_triangles,
        "allowed_visible_axis_object": ALLOWED_VISIBLE_AXIS_OBJECT,
        "forbidden_axis_tokens": list(FORBIDDEN_AXIS_TOKENS),
        "remaining_object_count": len(bpy.data.objects),
        "remaining_mesh_count": len(output_meshes),
        "remaining_triangle_count": sum(output_meshes.values()),
        "unrelated_mesh_topology_unchanged": True,
        "outputs": {
            path.name: {
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in (OUTPUT_BLEND, OUTPUT_FBX, OUTPUT_GLB, COLLISION_FBX)
        },
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
