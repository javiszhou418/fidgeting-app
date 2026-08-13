"""Build the reusable premium acrylic display case for Unity.

The FBX intentionally contains case and packaging geometry only.  Prize content
is injected at runtime under Unity's contentSlot anchor.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy


ROOT_NAME = "PremiumDisplayCase_Model"
EXPECTED_LAYERS = (
    "Layer_01_FrontPlate",
    "Layer_02_Fasteners",
    "Layer_03_SpacerFrame",
    "Layer_04_Capsule",
    "Layer_05_VelvetInsert",
    "Layer_06_RearPlate",
    "Layer_07_OuterTray",
    "Layer_08_BoxLid",
)


def millimeters(value: float) -> float:
    return value / 1000.0


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def material(name: str, color: tuple[float, float, float, float], metallic: float,
             roughness: float) -> bpy.types.Material:
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.diffuse_color = color
    result.metallic = metallic
    result.roughness = roughness
    return result


def empty(name: str, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    result = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(result)
    result.parent = parent
    result.empty_display_type = "PLAIN_AXES"
    result.empty_display_size = millimeters(8)
    return result


def finish_mesh(obj: bpy.types.Object, mat: bpy.types.Material,
                bevel_mm: float = 0.0, bevel_segments: int = 4) -> bpy.types.Object:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel_mm > 0:
        bevel = obj.modifiers.new("Precision edge radius", "BEVEL")
        bevel.width = millimeters(bevel_mm)
        bevel.segments = bevel_segments
        bevel.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = bevel_mm > 0
    obj.select_set(False)
    return obj


def rounded_box(name: str, dimensions_mm: tuple[float, float, float],
                location_mm: tuple[float, float, float], bevel_mm: float,
                mat: bpy.types.Material, parent: bpy.types.Object) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(
        location=tuple(millimeters(v) for v in location_mm))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = tuple(millimeters(v) for v in dimensions_mm)
    obj.parent = parent
    return finish_mesh(obj, mat, bevel_mm, 6)


def cylinder(name: str, diameter_mm: float, depth_mm: float,
             location_mm: tuple[float, float, float], mat: bpy.types.Material,
             parent: bpy.types.Object, vertices: int = 64,
             bevel_mm: float = 0.7) -> bpy.types.Object:
    # Blender's cylinder axis is Z. Rotate it onto Y so FBX import presents the
    # case depth along Unity Z after the standard -Z/Y axis conversion.
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=millimeters(diameter_mm * 0.5),
        depth=millimeters(depth_mm),
        location=tuple(millimeters(v) for v in location_mm),
        rotation=(math.pi * 0.5, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.parent = parent
    return finish_mesh(obj, mat, bevel_mm, 4)


def torus(name: str, outer_mm: float, inner_mm: float, depth_scale: float,
          location_mm: tuple[float, float, float], mat: bpy.types.Material,
          parent: bpy.types.Object) -> bpy.types.Object:
    major_radius = millimeters((outer_mm + inner_mm) * 0.25)
    minor_radius = millimeters((outer_mm - inner_mm) * 0.25)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=96,
        minor_segments=16,
        location=tuple(millimeters(v) for v in location_mm),
        rotation=(math.pi * 0.5, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    # The torus is authored in local XY with local Z as its thickness axis.
    # Scale local Z before the +90-degree X rotation carries that thickness
    # onto the case's Blender-Y / Unity-Z depth axis. Scaling local Y would
    # distort the neutral circular opening into an ellipse.
    obj.scale.z = depth_scale
    obj.parent = parent
    return finish_mesh(obj, mat)


def graphite_insert_with_aperture(parent: bpy.types.Object,
                                  graphite: bpy.types.Material) -> bpy.types.Object:
    insert = rounded_box(
        "Graphite_Insert", (160, 8, 208), (0, 2, 0), 10,
        graphite, parent)
    cutter = cylinder(
        "__CapsuleApertureCutter", 84, 18, (0, 2, 0),
        graphite, parent, vertices=96, bevel_mm=0)
    boolean = insert.modifiers.new("Neutral circular aperture", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.solver = "EXACT"
    boolean.object = cutter
    bpy.context.view_layer.objects.active = insert
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return insert


def build_model() -> tuple[bpy.types.Object, dict[str, object]]:
    reset_scene()
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    acrylic = material("MAT_Acrylic_Clear", (0.70, 0.82, 0.90, 0.12), 0.0, 0.05)
    acrylic.diffuse_color = (0.70, 0.82, 0.90, 0.12)
    metal = material("MAT_BrushedMetal", (0.58, 0.62, 0.68, 1.0), 0.98, 0.18)
    graphite = material("MAT_NeutralGraphite", (0.055, 0.067, 0.082, 1.0), 0.46, 0.34)
    velvet = material("MAT_BlackVelvet", (0.012, 0.016, 0.022, 1.0), 0.0, 0.84)
    matte = material("MAT_MatteBlackBox", (0.003, 0.004, 0.006, 1.0), 0.10, 0.22)

    root = empty(ROOT_NAME)
    root["content_contract"] = "runtime-only"
    root["capsule_shape"] = "neutral-circular"
    root["style"] = "clear-acrylic-four-fastener"
    root["has_opaque_outer_box"] = False
    root["units"] = "meters"
    layers = {name: empty(name, root) for name in EXPECTED_LAYERS}

    rounded_box("Acrylic_FrontPlate", (188, 5, 240), (0, -18, 0), 12,
                acrylic, layers["Layer_01_FrontPlate"])

    fastener_positions = {
        "Fastener_TL": (-78, -23, 104),
        "Fastener_TR": (78, -23, 104),
        "Fastener_BL": (-78, -23, -104),
        "Fastener_BR": (78, -23, -104),
    }
    for name, position in fastener_positions.items():
        cylinder(name, 16, 12, position, matte,
                 layers["Layer_02_Fasteners"], vertices=64, bevel_mm=1.2)
        collar_name = name.replace("Fastener_", "ChromeCollar_")
        cylinder(collar_name, 20, 4, (position[0], -17, position[2]), metal,
                 layers["Layer_02_Fasteners"], vertices=64, bevel_mm=0.8)

    spacer = layers["Layer_03_SpacerFrame"]
    rounded_box("Acrylic_SpacerFrame_Top", (180, 10, 10), (0, -11, 110), 4,
                acrylic, spacer)
    rounded_box("Acrylic_SpacerFrame_Bottom", (180, 10, 10), (0, -11, -110), 4,
                acrylic, spacer)
    rounded_box("Acrylic_SpacerFrame_Left", (10, 10, 210), (-84, -11, 0), 4,
                acrylic, spacer)
    rounded_box("Acrylic_SpacerFrame_Right", (10, 10, 210), (84, -11, 0), 4,
                acrylic, spacer)

    capsule = layers["Layer_04_Capsule"]
    torus("Capsule_CircularRing", 96, 84, 1.6, (0, -7, 0),
          acrylic, capsule)
    cylinder("Capsule_ClearBack", 84, 3, (0, -1, 0), acrylic,
             capsule, vertices=96, bevel_mm=0.8)
    torus("Capsule_EdgeHighlight", 90, 86, 0.45, (0, -12, 0),
          metal, capsule)

    graphite_insert_with_aperture(layers["Layer_05_VelvetInsert"], graphite)

    rounded_box("Acrylic_RearPlate", (188, 4, 240), (0, 10, 0), 12,
                acrylic, layers["Layer_06_RearPlate"])

    tray = layers["Layer_07_OuterTray"]
    rounded_box("Graphite_InnerTray", (160, 8, 208), (0, 16, 0), 10,
                graphite, tray)

    lid = layers["Layer_08_BoxLid"]
    rounded_box("Acrylic_BackFrame_Top", (188, 6, 8), (0, 23, 116), 3,
                acrylic, lid)
    rounded_box("Acrylic_BackFrame_Bottom", (188, 6, 8), (0, 23, -116), 3,
                acrylic, lid)
    rounded_box("Acrylic_BackFrame_Left", (8, 6, 224), (-90, 23, 0), 3,
                acrylic, lid)
    rounded_box("Acrylic_BackFrame_Right", (8, 6, 224), (90, 23, 0), 3,
                acrylic, lid)

    # A stable locator included for DCC inspection only. Unity creates the
    # actual runtime contentSlot hierarchy so prize ownership stays external.
    content_anchor = empty("ContentSlot_Anchor", root)
    content_anchor.location = (0.0, millimeters(-7), 0.0)
    content_anchor["runtime_content_only"] = True

    bpy.context.view_layer.objects.active = root
    root.select_set(True)

    manifest = {
        "schemaVersion": 1,
        "root": ROOT_NAME,
        "unit": "meter",
        "style": "clear-acrylic-four-fastener",
        "caseDimensionsMm": {"width": 188, "height": 240, "depth": 53},
        "outerBoxDimensionsMm": {"width": 188, "height": 240, "depth": 53},
        "capsule": {"shape": "circular", "diameterMm": 84, "depthMm": 26},
        "layers": list(EXPECTED_LAYERS),
        "fasteners": list(fastener_positions),
        "fastenerStyle": "black-cap-with-chrome-collar",
        "contentSlot": "ContentSlot_Anchor",
        "hasOpaqueOuterBox": False,
        "containsPrizeGeometry": False,
    }
    return root, manifest


def save_outputs(root: bpy.types.Object, manifest: dict[str, object]) -> None:
    source_dir = Path(__file__).resolve().parent
    unity_root = source_dir.parent.parent
    model_dir = unity_root / "Assets" / "_DisplayCase" / "Models"
    model_dir.mkdir(parents=True, exist_ok=True)
    blend_path = source_dir / "PremiumDisplayCase.blend"
    fbx_path = model_dir / "PremiumDisplayCase.fbx"
    manifest_path = source_dir / "premium_display_case_manifest.json"

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.object.select_all(action="DESELECT")
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.fbx(
        filepath=str(fbx_path),
        use_selection=True,
        object_types={"EMPTY", "MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        bake_anim=False,
        add_leaf_bones=False,
        mesh_smooth_type="FACE",
        path_mode="AUTO",
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(f"DISPLAY_CASE_BLEND={blend_path}")
    print(f"DISPLAY_CASE_FBX={fbx_path}")
    print(f"DISPLAY_CASE_MANIFEST={manifest_path}")


if __name__ == "__main__":
    model_root, model_manifest = build_model()
    save_outputs(model_root, model_manifest)
