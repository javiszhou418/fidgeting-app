"""Concept lookdev for the Premium Display Case back plate (R053 slab concepts).

Concept-only. Renders a thin, flat collector slab (no rear bulge) with a CNC
pocket instead of the sunburst disc, an English label plate, and four back
plate material candidates. Nothing here is promoted to Unity; the user picks a
direction first, then the real pipeline revision follows.

Run:
    blender -b --python render_slab_material_concepts.py -- <output-dir> [candidates]
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
UNITY_ROOT = HERE.parent.parent
GEEONE_FBX = UNITY_ROOT / "Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner.fbx"
OXANIUM = UNITY_ROOT / "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf"

MM = 0.001
SLAB_W, SLAB_H = 188.0, 240.0
FRONT_T, BACK_T = 3.0, 11.0          # total 14 mm: a slab, not a box
CORNER_R = 12.0
POCKET_D, POCKET_DEPTH, POCKET_CHAMFER = 84.0, 8.0, 1.2
LABEL_W, LABEL_H, LABEL_T = 156.0, 42.0, 1.4
LABEL_Z = SLAB_H * 0.5 - 18.0 - LABEL_H * 0.5
POCKET_Z = -18.0
SCREW_INSET = 11.0

CANDIDATES = {
    "a-walnut": "A · 胡桃木背板 + 铂金标签",
    "b-anodised": "B · 黑色阳极氧化铝 + 拉丝",
    "c-forged-carbon": "C · 锻造碳纤维 + 树脂罩光",
    "d-frosted": "D · 磨砂白亚克力内衬（评级卡风）",
}


def mm(v: float) -> float:
    return v * MM


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def reset() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def new_material(name: str) -> tuple[bpy.types.Material, bpy.types.ShaderNode]:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    return mat, bsdf


def set_input(node: bpy.types.ShaderNode, name: str, value) -> None:
    if name in node.inputs:
        node.inputs[name].default_value = value


def rounded_plate(name: str, w: float, h: float, t: float, y_center: float,
                  radius: float, mat: bpy.types.Material, z_center: float = 0.0) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=(0.0, mm(y_center), mm(z_center)))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (mm(w), mm(t), mm(h))
    bpy.ops.object.transform_apply(scale=True)
    bevel = obj.modifiers.new("corner", "BEVEL")
    bevel.width = mm(radius)
    bevel.segments = 16
    bevel.limit_method = "ANGLE"
    bevel.affect = "EDGES"
    # Only round the four Y-parallel edges: restrict with a vertex group on edges along Y.
    obj.vertex_groups.new(name="corners")
    edge_bevel_weights(obj, axis=1)
    bevel.limit_method = "WEIGHT"
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    face_bevel = obj.modifiers.new("edge", "BEVEL")
    face_bevel.width = mm(0.6)
    face_bevel.segments = 3
    face_bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=face_bevel.name)
    obj.data.materials.append(mat)
    smooth_plate(obj)
    return obj


def smooth_plate(obj: bpy.types.Object) -> None:
    """Smooth the rounded corners without letting big n-gons read as pyramids."""
    # Flat: the 16-segment corner radius is invisible at review scale, while
    # smoothing a booleaned n-gon reads as an X-shaped crease.
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()


def edge_bevel_weights(obj: bpy.types.Object, axis: int) -> None:
    import bmesh
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    layer = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    for edge in bm.edges:
        d = edge.verts[0].co - edge.verts[1].co
        along = abs(d[axis]) > 0.9 * d.length
        edge[layer] = 1.0 if along else 0.0
    bm.to_mesh(mesh)
    bm.free()


def cylinder(name: str, d: float, depth: float, location, mat=None, rot_x=math.pi * 0.5,
             r_top: float | None = None) -> bpy.types.Object:
    if r_top is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=mm(d * 0.5), depth=mm(depth),
                                            location=tuple(mm(v) for v in location),
                                            rotation=(rot_x, 0.0, 0.0))
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=128, radius1=mm(d * 0.5), radius2=mm(r_top * 2 * 0.5),
                                        depth=mm(depth), location=tuple(mm(v) for v in location),
                                        rotation=(rot_x, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    if mat is not None:
        obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj


def boolean_cut(target: bpy.types.Object, cutter: bpy.types.Object) -> None:
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# ---------------------------------------------------------------- materials

def acrylic() -> bpy.types.Material:
    mat, b = new_material("MAT_Acrylic_Clear")
    set_input(b, "Base Color", (0.96, 0.98, 1.0, 1.0))
    set_input(b, "Roughness", 0.02)
    set_input(b, "IOR", 1.49)
    set_input(b, "Transmission Weight", 1.0)
    return mat


def keep_front_face_only(plate: bpy.types.Object) -> None:
    """Concept-only: a closed 3 mm glass slab draws an X of internal light
    transport across the back plate in Cycles. A single rounded glass face
    keeps the reflections and refraction we want to judge without it."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(plate.data)
    doomed = [f for f in bm.faces if f.normal.y > -0.9]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(plate.data)
    bm.free()


def platinum_label() -> bpy.types.Material:
    mat, b = new_material("MAT_Label_Platinum")
    set_input(b, "Base Color", (0.34, 0.34, 0.33, 1.0))
    set_input(b, "Metallic", 0.9)
    set_input(b, "Roughness", 0.52)
    return mat


def ink() -> bpy.types.Material:
    mat, b = new_material("MAT_Label_Ink")
    set_input(b, "Base Color", (0.04, 0.04, 0.045, 1.0))
    set_input(b, "Roughness", 0.55)
    return mat


def screw_black() -> bpy.types.Material:
    mat, b = new_material("MAT_Screw")
    set_input(b, "Base Color", (0.05, 0.05, 0.055, 1.0))
    set_input(b, "Metallic", 1.0)
    set_input(b, "Roughness", 0.35)
    return mat


def steel(name: str, base, rough: float, aniso: float = 0.0) -> bpy.types.Material:
    mat, b = new_material(name)
    set_input(b, "Base Color", (*base, 1.0))
    set_input(b, "Metallic", 1.0)
    set_input(b, "Roughness", rough)
    set_input(b, "Anisotropic", aniso)
    return mat


def walnut() -> bpy.types.Material:
    mat, b = new_material("MAT_Back_Walnut")
    nt = mat.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 0.09)   # grain runs along height
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 9.0
    noise.inputs["Detail"].default_value = 9.0
    noise.inputs["Roughness"].default_value = 0.62
    noise.inputs["Distortion"].default_value = 0.9
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 3.2
    wave.inputs["Distortion"].default_value = 5.0
    wave.inputs["Detail"].default_value = 4.0
    wave.inputs["Detail Scale"].default_value = 1.5
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.055, 0.030, 0.018, 1.0)
    ramp.color_ramp.elements[1].color = (0.20, 0.11, 0.06, 1.0)
    mid = ramp.color_ramp.elements.new(0.55)
    mid.color = (0.13, 0.072, 0.040, 1.0)
    rough_ramp = nt.nodes.new("ShaderNodeValToRGB")
    rough_ramp.color_ramp.elements[0].color = (0.42,) * 3 + (1.0,)
    rough_ramp.color_ramp.elements[1].color = (0.30,) * 3 + (1.0,)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Color"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(wave.outputs["Fac"], rough_ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(rough_ramp.outputs["Color"], b.inputs["Roughness"])
    set_input(b, "Coat Weight", 0.35)
    set_input(b, "Coat Roughness", 0.18)
    return mat


def anodised() -> bpy.types.Material:
    mat, b = new_material("MAT_Back_Anodised")
    nt = mat.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (2.0, 2.0, 400.0)  # hairline grain along height
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 60.0
    noise.inputs["Detail"].default_value = 4.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.030, 0.031, 0.034, 1.0)
    ramp.color_ramp.elements[1].color = (0.075, 0.077, 0.082, 1.0)
    rough = nt.nodes.new("ShaderNodeMath")
    rough.operation = "MULTIPLY_ADD"
    rough.inputs[1].default_value = 0.10
    rough.inputs[2].default_value = 0.30
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(noise.outputs["Fac"], rough.inputs[0])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(rough.outputs["Value"], b.inputs["Roughness"])
    set_input(b, "Metallic", 1.0)
    return mat


def forged_carbon() -> bpy.types.Material:
    mat, b = new_material("MAT_Back_ForgedCarbon")
    nt = mat.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    voronoi = nt.nodes.new("ShaderNodeTexVoronoi")
    voronoi.feature = "F1"
    voronoi.inputs["Scale"].default_value = 110.0
    voronoi.inputs["Randomness"].default_value = 1.0
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 0.25)    # stretched flakes
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.012, 0.012, 0.014, 1.0)
    ramp.color_ramp.elements[1].color = (0.11, 0.115, 0.125, 1.0)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])
    nt.links.new(voronoi.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    set_input(b, "Metallic", 0.6)
    set_input(b, "Roughness", 0.42)
    set_input(b, "Coat Weight", 1.0)
    set_input(b, "Coat Roughness", 0.06)
    return mat


def frosted() -> bpy.types.Material:
    mat, b = new_material("MAT_Back_Frosted")
    set_input(b, "Base Color", (0.93, 0.94, 0.95, 1.0))
    set_input(b, "Roughness", 0.55)
    set_input(b, "Transmission Weight", 0.35)
    set_input(b, "IOR", 1.49)
    set_input(b, "Subsurface Weight", 0.4)
    set_input(b, "Subsurface Radius", (0.004, 0.004, 0.004))
    return mat


BACK_MATERIALS = {
    "a-walnut": walnut,
    "b-anodised": anodised,
    "c-forged-carbon": forged_carbon,
    "d-frosted": frosted,
}


# ------------------------------------------------------------------ build

def build_slab(back_mat: bpy.types.Material) -> None:
    clear = acrylic()
    front = rounded_plate("Front_Acrylic", SLAB_W, SLAB_H, FRONT_T, -(BACK_T * 0.5 + FRONT_T * 0.5),
                          CORNER_R, clear)
    keep_front_face_only(front)

    back = rounded_plate("Back_Plate", SLAB_W, SLAB_H, BACK_T, 0.0, CORNER_R, back_mat)
    front_face_y = -BACK_T * 0.5
    # CNC pocket: straight bore + 1.2 mm chamfer at the mouth.
    bore = cylinder("__bore", POCKET_D, POCKET_DEPTH * 2, (0, front_face_y, POCKET_Z))
    boolean_cut(back, bore)
    chamfer = cylinder("__chamfer", POCKET_D + POCKET_CHAMFER * 2, POCKET_CHAMFER * 2,
                       (0, front_face_y, POCKET_Z), r_top=POCKET_D * 0.5 - POCKET_CHAMFER)
    boolean_cut(back, chamfer)
    # Label recess.
    bpy.ops.mesh.primitive_cube_add(location=(0, mm(front_face_y), mm(LABEL_Z)))
    recess = bpy.context.object
    recess.dimensions = (mm(LABEL_W + 0.6), mm(LABEL_T * 2), mm(LABEL_H + 0.6))
    bpy.ops.object.transform_apply(scale=True)
    boolean_cut(back, recess)
    smooth_plate(back)

    label = rounded_plate("Label_Plate", LABEL_W, LABEL_H, LABEL_T, front_face_y + LABEL_T * 0.5 - 0.05,
                          3.0, platinum_label(), z_center=LABEL_Z)
    label_text(front_face_y - 0.14)

    screw = screw_black()
    for sx in (-1, 1):
        for sz in (-1, 1):
            x = sx * (SLAB_W * 0.5 - SCREW_INSET)
            z = sz * (SLAB_H * 0.5 - SCREW_INSET)
            head = cylinder(f"Screw_{sx}_{sz}", 5.0, 1.2, (x, front_face_y - FRONT_T - 0.4, z), screw)
            slot = cylinder("__slot", 2.2, 1.0, (x, front_face_y - FRONT_T - 1.0, z))
            boolean_cut(head, slot)

    place_geeone(front_face_y)


def label_text(surface_y: float) -> None:
    ink_mat = ink()
    font = bpy.data.fonts.load(str(OXANIUM)) if OXANIUM.is_file() else None

    def text(body: str, size_mm: float, x: float, z: float, align: str = "LEFT") -> None:
        bpy.ops.object.text_add(location=(mm(x), mm(surface_y), mm(z)), rotation=(math.pi * 0.5, 0, 0))
        obj = bpy.context.object
        obj.data.body = body
        obj.data.size = mm(size_mm)
        obj.data.align_x = align
        obj.data.extrude = mm(0.05)
        if font is not None:
            obj.data.font = font
        obj.data.materials.append(ink_mat)

    left = -LABEL_W * 0.5 + 7
    text("FIDGET ARCHIVE  ·  SERIES 01", 4.2, left, LABEL_Z + 12)
    text("GEEONE TRI-SPINNER", 9.5, left, LABEL_Z + 0.5)
    text("SATIN STEEL  ·  DRAGON SCALE", 4.2, left, LABEL_Z - 9)
    text("No. 000128", 4.6, left, LABEL_Z - 17)
    # Grade block, right side.
    text("10", 17, LABEL_W * 0.5 - 9, LABEL_Z - 5, align="RIGHT")
    text("GEM MINT", 3.8, LABEL_W * 0.5 - 9, LABEL_Z - 17, align="RIGHT")


def place_geeone(front_face_y: float) -> None:
    if not GEEONE_FBX.is_file():
        return
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(GEEONE_FBX))
    imported = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in imported if o.parent is None or o.parent not in imported]
    root = bpy.data.objects.new("Geeone_Root", None)
    bpy.context.collection.objects.link(root)
    for obj in roots:
        obj.parent = root
    satin = steel("M_Geeone_Satin", (0.30, 0.31, 0.32), 0.55)
    disc = steel("M_Geeone_Disc", (0.44, 0.45, 0.46), 0.34, 0.8)
    hub = steel("M_Geeone_Hub", (0.06, 0.06, 0.065), 0.38)
    for obj in imported:
        if obj.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(32))
        for slot in obj.material_slots:
            name = slot.material.name if slot.material else ""
            slot.material = disc if "DiscTurned" in name else hub if "HubDark" in name else satin
        obj.data.materials.clear() if not obj.material_slots else None
        if not obj.material_slots:
            obj.data.materials.append(satin)
    # Measure and fit inside the pocket: spin axis -> -Y (faces the viewer).
    bpy.context.view_layer.update()
    xs, ys, zs = [], [], []
    for obj in imported:
        if obj.type == "MESH":
            for corner in obj.bound_box:
                w = obj.matrix_world @ Vector(corner)
                xs.append(w.x); ys.append(w.y); zs.append(w.z)
    if not xs:
        return
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    span_z = max(zs) - min(zs)
    # Imported spin axis is the shortest extent.
    extents = {"x": span_x, "y": span_y, "z": span_z}
    axis = min(extents, key=extents.get)
    footprint = max(v for k, v in extents.items() if k != axis)
    scale = mm(POCKET_D - 6.0) / footprint if footprint > 0 else 1.0
    root.scale = (scale,) * 3
    if axis == "z":
        root.rotation_euler = (math.pi * 0.5, 0.0, 0.0)
    elif axis == "x":
        root.rotation_euler = (0.0, 0.0, math.pi * 0.5)
    center = Vector(((max(xs) + min(xs)) * 0.5, (max(ys) + min(ys)) * 0.5, (max(zs) + min(zs)) * 0.5)) * scale
    thickness = extents[axis] * scale
    root.location = (0.0, mm(front_face_y + POCKET_DEPTH) - thickness * 0.5, mm(POCKET_Z))
    bpy.context.view_layer.update()
    # Recentre in XZ after rotation.
    xs, zs = [], []
    for obj in imported:
        if obj.type == "MESH":
            for corner in obj.bound_box:
                w = obj.matrix_world @ Vector(corner)
                xs.append(w.x); zs.append(w.z)
    root.location.x -= (max(xs) + min(xs)) * 0.5
    root.location.z += mm(POCKET_Z) - (max(zs) + min(zs)) * 0.5
    root.rotation_euler.rotate_axis("Y", math.radians(12))


# ---------------------------------------------------------------- scene

def studio(target: Vector) -> bpy.types.Object:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 160
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = True
        scene.cycles.device = "GPU"
    except Exception:
        scene.cycles.device = "CPU"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -1.4
    world = bpy.data.worlds.new("Studio")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.013, 0.016, 1.0)
    bg.inputs["Strength"].default_value = 1.0

    def area(name, loc, energy, color, size, shape="RECTANGLE", size_y=None):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.color = color
        data.shape = shape
        data.size = size
        if size_y:
            data.size_y = size_y
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = loc
        look_at(obj, target)
        return obj

    area("Key_Softbox", (-0.55, -0.45, 0.10), 34, (1.0, 0.97, 0.93), 0.8, size_y=1.1)
    area("Fill_Softbox", (0.48, -0.36, 0.05), 16, (0.90, 0.94, 1.0), 0.7)
    area("Rim_Strip", (0.22, 0.30, 0.34), 40, (1.0, 0.98, 0.95), 0.08, size_y=0.8)
    area("Top_Strip", (0.0, -0.10, 0.62), 12, (1.0, 1.0, 1.0), 0.06, size_y=0.6)

    # Backdrop plane far behind, matte near-black.
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0.6, 0), rotation=(math.pi * 0.5, 0, 0))
    plane = bpy.context.object
    mat, b = new_material("MAT_Backdrop")
    set_input(b, "Base Color", (0.006, 0.0065, 0.008, 1.0))
    set_input(b, "Roughness", 1.0)
    plane.data.materials.append(mat)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 70
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    return cam


def render(cam: bpy.types.Object, loc, target, path: Path) -> None:
    cam.location = loc
    look_at(cam, Vector(target))
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[0]) if argv else UNITY_ROOT.parent / "Artifacts/PremiumDisplayCase/slab-material-concepts-r001"
    selected = argv[1:] or list(CANDIDATES)
    out.mkdir(parents=True, exist_ok=True)
    for key in selected:
        reset()
        build_slab(BACK_MATERIALS[key]())
        cam = studio(Vector((0.0, 0.0, -0.005)))
        render(cam, (0.16, -0.62, 0.10), (0.0, 0.0, -0.01), out / f"{key}-hero.png")
        render(cam, (0.0, -0.66, 0.0), (0.0, 0.0, 0.0), out / f"{key}-front.png")
        render(cam, (0.0, -0.36, 0.09), (0.0, 0.0, LABEL_Z * MM - 0.03), out / f"{key}-label-detail.png")
        print(f"CONCEPT_RENDERED={key}")


if __name__ == "__main__":
    main()
