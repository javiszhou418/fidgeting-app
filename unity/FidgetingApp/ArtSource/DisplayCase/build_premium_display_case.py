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
             roughness: float, transmission: float = 0.0,
             ior: float = 1.5) -> bpy.types.Material:
    result = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    result.diffuse_color = color
    result.metallic = metallic
    result.roughness = roughness
    result.use_nodes = True
    principled = result.node_tree.nodes.get("Principled BSDF")
    if principled is not None:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        if "IOR" in principled.inputs:
            principled.inputs["IOR"].default_value = ior
        if "Transmission Weight" in principled.inputs:
            principled.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in principled.inputs:
            principled.inputs["Transmission"].default_value = transmission
        if "Alpha" in principled.inputs:
            principled.inputs["Alpha"].default_value = color[3]
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


def rounded_frame(name_prefix: str, width_mm: float, height_mm: float,
                  bar_mm: float, depth_mm: float,
                  location_mm: tuple[float, float, float], bevel_mm: float,
                  mat: bpy.types.Material, parent: bpy.types.Object) -> list[bpy.types.Object]:
    x, y, z = location_mm
    horizontal_width = max(bar_mm, width_mm - bar_mm)
    vertical_height = max(bar_mm, height_mm - bar_mm)
    return [
        rounded_box(f"{name_prefix}_Top", (horizontal_width, depth_mm, bar_mm),
                    (x, y, z + (height_mm - bar_mm) * 0.5), bevel_mm, mat, parent),
        rounded_box(f"{name_prefix}_Bottom", (horizontal_width, depth_mm, bar_mm),
                    (x, y, z - (height_mm - bar_mm) * 0.5), bevel_mm, mat, parent),
        rounded_box(f"{name_prefix}_Left", (bar_mm, depth_mm, vertical_height),
                    (x - (width_mm - bar_mm) * 0.5, y, z), bevel_mm, mat, parent),
        rounded_box(f"{name_prefix}_Right", (bar_mm, depth_mm, vertical_height),
                    (x + (width_mm - bar_mm) * 0.5, y, z), bevel_mm, mat, parent),
    ]


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

    acrylic = material(
        "MAT_FrostedPolycarbonate", (0.61, 0.65, 0.68, 0.10),
        0.0, 0.22, transmission=0.92, ior=1.585)
    acrylic_edge = material(
        "MAT_FrostedPolycarbonateEdge", (0.72, 0.75, 0.77, 0.21),
        0.0, 0.18, transmission=0.78, ior=1.585)
    metal = material(
        "MAT_RarityFoilSilver", (0.58, 0.62, 0.66, 1.0), 0.96, 0.30)
    graphite = material(
        "MAT_LabelGraphite", (0.055, 0.060, 0.066, 1.0), 0.22, 0.52)
    velvet = material(
        "MAT_BlackFlocking", (0.009, 0.011, 0.014, 1.0), 0.0, 0.91)
    label_paper = material(
        "MAT_LabelPaper", (0.74, 0.72, 0.68, 1.0), 0.0, 0.73)

    root = empty(ROOT_NAME)
    root["content_contract"] = "runtime-only"
    root["capsule_shape"] = "collector-slab-large-chamber"
    root["style"] = "frosted-polycarbonate-collector-slab"
    root["has_opaque_outer_box"] = False
    root["units"] = "meters"
    layers = {name: empty(name, root) for name in EXPECTED_LAYERS}

    rounded_box("Polycarbonate_FrontShell", (212, 6, 300), (0, -22, 0), 13,
                acrylic, layers["Layer_01_FrontPlate"])

    label_layer = layers["Layer_02_Fasteners"]
    rounded_box("Collector_LabelPaper", (184, 3.0, 58), (0, -26, 105), 4.0,
                label_paper, label_layer)
    rounded_frame("Collector_LabelFoil", 188, 62, 2.2, 1.6,
                  (0, -28, 105), 0.65, metal, label_layer)

    spacer = layers["Layer_03_SpacerFrame"]
    rounded_frame("Polycarbonate_SpacerFrame", 202, 288, 8, 12,
                  (0, -12, 0), 3.4, acrylic_edge, spacer)

    capsule = layers["Layer_04_Capsule"]
    rounded_frame("Collector_ChamberRim", 190, 210, 5.5, 8,
                  (0, -16, -42), 2.4, acrylic_edge, capsule)
    rounded_box("Collector_RarityFoilBand", (170, 1.8, 2.4),
                (0, -27.5, 69), 0.8, metal, capsule)

    rounded_box("Collector_BlackFlocking", (182, 9, 202), (0, -2, -42), 10,
                velvet, layers["Layer_05_VelvetInsert"])

    rounded_box("Polycarbonate_RearShell", (212, 7, 300), (0, 16, 0), 13,
                acrylic, layers["Layer_06_RearPlate"])

    tray = layers["Layer_07_OuterTray"]
    rounded_frame("Polycarbonate_RearStep", 216, 304, 6, 9,
                  (0, 23, 0), 2.6, acrylic_edge, tray)

    lid = layers["Layer_08_BoxLid"]
    rounded_frame("Polycarbonate_FrontStep", 216, 304, 6, 9,
                  (0, -27, 0), 2.6, acrylic_edge, lid)

    # A stable locator included for DCC inspection only. Unity creates the
    # actual runtime contentSlot hierarchy so prize ownership stays external.
    content_anchor = empty("ContentSlot_Anchor", root)
    content_anchor.location = (0.0, millimeters(-18), millimeters(-42))
    content_anchor["runtime_content_only"] = True

    bpy.context.view_layer.objects.active = root
    root.select_set(True)

    manifest = {
        "schemaVersion": 2,
        "root": ROOT_NAME,
        "unit": "meter",
        "style": "frosted-polycarbonate-collector-slab",
        "caseDimensionsMm": {"width": 216, "height": 304, "depth": 50},
        "outerBoxDimensionsMm": {"width": 216, "height": 304, "depth": 50},
        "label": {"widthMm": 184, "heightMm": 58, "centerYmm": 105},
        "capsule": {"shape": "rounded-rectangle", "widthMm": 180,
                    "heightMm": 198, "depthMm": 48, "centerYmm": -42},
        "layers": list(EXPECTED_LAYERS),
        "fasteners": [],
        "fastenerStyle": "none",
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
