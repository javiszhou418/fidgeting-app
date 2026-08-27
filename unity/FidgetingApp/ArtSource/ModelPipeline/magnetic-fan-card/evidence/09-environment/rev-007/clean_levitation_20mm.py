"""Raise the 72-segment product to 20 mm and clear ambiguous hero props."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = (
    HERE.parent / "rev-006/fan-card-72-surreal-levitation.blend")
OUTPUT_BLEND = HERE / "fan-card-72-surreal-clean-20mm.blend"
OUTPUT_IMAGE = HERE / "surreal-clean-20mm-preview.png"
ADDITIONAL_LIFT = 0.006


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    return [root, *list(root.children_recursive)]


def hide_hierarchy(root: bpy.types.Object) -> None:
    for obj in descendants(root):
        obj.hide_render = True
        obj.hide_viewport = True


def projected_rect(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    objects: list[bpy.types.Object],
) -> tuple[float, float, float, float] | None:
    points = [
        world_to_camera_view(scene, camera, obj.matrix_world @ Vector(corner))
        for obj in objects
        if obj.type == "MESH"
        for corner in obj.bound_box
    ]
    if not points:
        return None
    return (
        min(point.x for point in points),
        max(point.x for point in points),
        min(point.y for point in points),
        max(point.y for point in points),
    )


def intersects(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> bool:
    return not (
        left[1] < right[0]
        or left[0] > right[1]
        or left[3] < right[2]
        or left[2] > right[3]
    )


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    camera = bpy.data.objects["CAM_Hero_Selected"]
    scene.camera = camera
    for name in (
        "MagneticFanCard_Root",
        "CommonAxis_RecessedMatteSpindle",
        "CommonAxis_BearingCap_Chrome",
        "EMPTY_CamTarget_FullScene",
    ):
        bpy.data.objects[name].location.z += ADDITIONAL_LIFT
    bpy.context.view_layer.update()

    product_collection = bpy.data.collections["COL_Product_Locked"]
    product_rect = projected_rect(
        scene,
        camera,
        [obj for obj in product_collection.all_objects if obj.type == "MESH"],
    )
    assert product_rect is not None
    product_safe_rect = (
        product_rect[0] - 0.025,
        product_rect[1] + 0.025,
        product_rect[2] - 0.025,
        product_rect[3] + 0.025,
    )

    removed = []
    for name in ("PROP_B_RainCard_04", "PROP_B_ForegroundChipRight"):
        root = bpy.data.objects.get(name)
        if root is not None:
            hide_hierarchy(root)
            removed.append(name)
    for root in [
        obj for obj in scene.objects
        if obj.parent is None
        and obj.name.startswith("PROP_B_")
        and not obj.hide_render
    ]:
        rect = projected_rect(scene, camera, descendants(root))
        if rect is not None and intersects(rect, product_safe_rect):
            hide_hierarchy(root)
            removed.append(root.name)

    key = bpy.data.objects["LGT_Key_Broad"].data
    key.size = 0.18
    key.energy = 2.9
    bpy.data.objects["LGT_Fill_Weak"].data.energy = 0.12
    bpy.data.objects["LGT_STAGE_TableGold"].data.energy = 0.58
    bpy.data.objects["LGT_Surreal_UnderGold"].data.energy = 1.45
    bpy.data.objects["LGT_Surreal_VolumeLift"].data.energy = 6.4

    scene.render.engine = "CYCLES"
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.020
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.58
    scene.render.filepath = str(OUTPUT_IMAGE)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    (HERE / "clean-levitation-report.json").write_text(
        json.dumps({
            "source": SOURCE_BLEND.name,
            "visibleCornerSegmentsPerQuadrant": 72,
            "hoverMillimetres": 20,
            "removedAmbiguousProps": sorted(set(removed)),
            "heroPropExclusionMarginNormalized": 0.025,
            "keySizeMillimetres": 180,
            "productGeometryModified": False,
            "productMaterialModified": False,
            "productHierarchyModified": False,
            "screenSpaceParticles": 0,
            "shippingIntegrated": False,
        }, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
