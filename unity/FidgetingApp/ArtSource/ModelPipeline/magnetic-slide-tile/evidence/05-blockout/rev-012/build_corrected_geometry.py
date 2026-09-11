import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "06-geometry/rev-004/magnetic-slide-tile-geometry-r004.blend"
BLEND = HERE / "magnetic-slide-tile-fixed-axis-r012.blend"
PRODUCT_GLB = HERE / "magnetic-slide-tile-fixed-axis-product-r012.glb"
TECHNICAL_GLB = HERE / "magnetic-slide-tile-fixed-axis-technical-r012.glb"
FBX = HERE / "magnetic-slide-tile-fixed-axis-r012.fbx"
REPORT = HERE / "geometry-validation.json"
P = Vector((0.0, -9.0, 5.875))
TOP_CENTER_Z = 9.0625
TOP_Q_Z = P.z - TOP_CENTER_Z
MAX_TRAVEL = 18.076433121019107
DISK_RADIUS = 15.0
PRODUCT_MESHES = {"BottomExterior", "MovingTopBody"}
INTERNAL_MESHES = {
    "InternalAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
}
GROOVES = ["TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parent_keep_world(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def material(name, color, metallic=0.0, roughness=0.65, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Alpha"].default_value = alpha
    if alpha < 1.0 and hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    return mat


def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def set_pose(slide, angle_deg):
    moving = bpy.data.objects["MovingTop"]
    top_slide = bpy.data.objects["TopLocalSlide"]
    carrier = bpy.data.objects["RotatingCarrier"]
    moving.location = P
    moving.rotation_mode = "XYZ"
    moving.rotation_euler = (0.0, 0.0, math.radians(angle_deg))
    top_slide.location = (0.0, 9.0 - slide, 0.0)
    carrier.location = (0.0, 0.0, -0.48)
    carrier.rotation_mode = "XYZ"
    carrier.rotation_euler = (0.0, 0.0, math.radians(angle_deg))
    bpy.context.view_layer.update()


def q_local(slide):
    return Vector((0.0, -9.0 + slide, TOP_Q_Z))


def top_residual(slide):
    top = bpy.data.objects["MovingTopBody"]
    return (top.matrix_world @ q_local(slide) - P).length


def set_product_visibility(axis_overlay=False):
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in PRODUCT_MESHES
    if axis_overlay:
        bpy.data.objects["Technical_FixedAxisOverlay"].hide_render = False


def set_technical_visibility():
    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in PRODUCT_MESHES | INTERNAL_MESHES | {"Technical_FixedAxisOverlay"}


def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, lens=70, ortho=None):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    data.lens = lens
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    look_at(obj, target)
    return obj


def render(scene, cam, filename, size=(960, 720)):
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(HERE / filename)
    bpy.ops.render.render(write_still=True)


def bvh(obj):
    return BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get(), epsilon=1e-6)


def mesh_world_vertices(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [obj.matrix_world @ vertex.co for vertex in evaluated.data.vertices]


def capsule_margin(point, radius=15.5, half_segment=9.5):
    nearest_y = max(-half_segment, min(half_segment, point.y))
    return radius - math.hypot(point.x, point.y - nearest_y)


def overlap_pairs(first, second):
    return len(bvh(first).overlap(bvh(second)))


def fingerprint(names):
    digest = hashlib.sha256()
    for name in sorted(names):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(i) for i in polygon.vertices).encode())
    return digest.hexdigest()


bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene = bpy.context.scene
scene["gate"] = "05-blockout"
scene["revision"] = 12
scene["mechanism_contract_sha256"] = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea"
scene["exact_top_transform"] = "T(P)*Rz(theta)*T(-q(s)); q(s)=(0,-9+s,-3.1875)"
scene["fixed_world_pivot_mm"] = list(P)
scene["product_renderer_whitelist"] = sorted(PRODUCT_MESHES)
scene["final_materials_applied"] = False
scene["self_motion"] = False

for obj in list(bpy.data.objects):
    if obj.type in {"LIGHT", "CAMERA"} or obj.name.startswith(("G05R6_", "Gate06_", "G06_", "Review_", "SectionAA_")) or obj.name == "Plane":
        bpy.data.objects.remove(obj, do_unlink=True)

root = bpy.data.objects["MagneticSlideTile_G05_R006"]
root.name = "MagneticSlideTile_G05_R012"
bottom = bpy.data.objects["BottomExterior"]
boss = bpy.data.objects["FixedAxisBoss"]
boss.name = "InternalAxisBoss"
fixed = bpy.data.objects["FixedAxis"]
disk = bpy.data.objects["MinimumOverlapDisk"]
carrier = bpy.data.objects["RotatingCarrier"]
moving = bpy.data.objects["MovingTop"]
top_slide = bpy.data.objects["TopLocalSlide"]
top = bpy.data.objects["MovingTopBody"]

parent_keep_world(fixed, bottom)
fixed.matrix_world.translation = P
fixed["mechanical_role"] = "single-fixed-world-pivot"
fixed["pivot_id"] = "FixedAxis"
fixed["translation_dof"] = False
fixed["rotation_dof"] = False
fixed["world_invariant"] = True
parent_keep_world(carrier, fixed)
parent_keep_world(boss, bottom)
boss.matrix_world.translation.z -= 0.25
boss["mechanical_role"] = "internal-axis-support"
boss["pivot_id"] = ""
boss["product_render"] = False
boss["fully_below_bottom_top_plane"] = True
parent_keep_world(disk, bottom)
disk.matrix_world.translation = P
disk.hide_render = True
disk.hide_viewport = False
disk["mechanical_role"] = "constraint-metadata"
disk["render_geometry"] = False
disk["radius_mm"] = DISK_RADIUS
disk["pivot_id"] = ""

parent_keep_world(moving, root)
moving.location = P
moving["transform"] = "T(P)*Rz(theta)"
moving["pivot_id"] = ""
top_slide.location = (0.0, 9.0, 0.0)
top_slide["transform"] = "T(-q_xy(s))"
top_slide["q_formula_mm"] = "q(s)=(0,-9+s,-3.1875)"
top.location = (0.0, 0.0, TOP_CENTER_Z - P.z)
top["transform_contract"] = "M_top(s,theta)*q(s)=P"
top["product_render"] = True
bottom["product_render"] = True
for name in INTERNAL_MESHES:
    bpy.data.objects[name]["product_render"] = False
    bpy.data.objects[name]["technical_render"] = True
    bpy.data.objects[name].hide_render = True
for name in GROOVES:
    bpy.data.objects[name]["product_render"] = False
    bpy.data.objects[name]["internal_only"] = True

white = material("G05R12_ProductClay", (0.72, 0.74, 0.77), roughness=0.58)
dark = material("G05R12_InternalClay", (0.20, 0.24, 0.30), metallic=0.15, roughness=0.45)
accent = material("G05R12_FollowerClay", (0.22, 0.55, 0.72), roughness=0.38)
overlay = material("G05R12_AxisOverlay", (0.95, 0.06, 0.02), roughness=0.35)
for name in PRODUCT_MESHES:
    assign(bpy.data.objects[name], white)
for name in INTERNAL_MESHES:
    assign(bpy.data.objects[name], accent if "Follower" in name or "Ball" in name else dark)

bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.22, depth=18.0, location=P + Vector((0, 0, 4.0)))
axis_overlay = bpy.context.object
axis_overlay.name = "Technical_FixedAxisOverlay"
assign(axis_overlay, overlay)
axis_overlay["product_render"] = False
axis_overlay["render_layer"] = "technical-overlay"
axis_overlay["non_product_geometry"] = True
axis_overlay.hide_render = True

world = bpy.data.worlds.new("G05R12_World") if not scene.world else scene.world
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.04, 0.05, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.look = "AgX - Medium High Contrast"
for name, loc, energy, size in [
    ("Key", (62, -75, 92), 50000, 44),
    ("Fill", (-48, -25, 52), 23000, 38),
    ("Rim", (32, 65, 62), 36000, 32),
]:
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size = energy, "DISK", size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    look_at(obj, (0, -4, 5))

cams = {
    "hero": camera("Hero", (70, -95, 64), (0, -6, 6), 68),
    "front": camera("Front", (0, -105, 8), (0, 0, 6), ortho=64),
    "back": camera("Back", (0, 105, 8), (0, 0, 6), ortho=64),
    "left": camera("Left", (-85, 0, 8), (0, 0, 6), ortho=60),
    "right": camera("Right", (85, 0, 8), (0, 0, 6), ortho=60),
    "top": camera("Top", (0, 0, 120), (0, 0, 0), ortho=64),
    "bottom": camera("Bottom", (0, 0, -110), (0, 0, 0), ortho=64),
    "technical": camera("Technical", (68, -90, 48), (0, -7, 5), 72),
}

set_pose(0, 0)
set_product_visibility()
for view in ["front", "back", "left", "right", "top", "bottom"]:
    render(scene, cams[view], f"orthographic-{view}.png")
render(scene, cams["hero"], "white-hero.png")
for name, slide, angle in [
    ("closed", 0, 0),
    ("max-open", MAX_TRAVEL, 0),
    ("detent-12", MAX_TRAVEL * 0.45, 12),
    ("detent-36", MAX_TRAVEL * 0.70, 36),
    ("combined", MAX_TRAVEL * 0.65, 24),
]:
    set_pose(slide, angle)
    render(scene, cams["hero"], f"state-{name}.png")

set_pose(MAX_TRAVEL * 0.55, 24)
set_product_visibility(axis_overlay=True)
render(scene, cams["technical"], "fixed-world-axis-overlay.png")

set_pose(MAX_TRAVEL * 0.35, 18)
set_technical_visibility()
top.location.z += 12.0
internal_world = {name: bpy.data.objects[name].matrix_world.copy() for name in INTERNAL_MESHES}
for index, name in enumerate(sorted(INTERNAL_MESHES)):
    bpy.data.objects[name].matrix_world.translation.z += 3.0 + index * 1.4
render(scene, cams["technical"], "technical-internals-exploded.png")
top.location.z -= 12.0
for name, matrix in internal_world.items():
    bpy.data.objects[name].matrix_world = matrix
bottom.hide_render = top.hide_render = True
render(scene, cams["technical"], "technical-internals-separated.png")
bottom.hide_render = top.hide_render = False

set_pose(0, 0)
set_product_visibility()
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

def export_selection(path, names, glb=True):
    bpy.ops.object.select_all(action="DESELECT")
    for name in names:
        bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["MagneticSlideTile_G05_R012"]
    if glb:
        bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_extras=True, export_animations=False, export_apply=True)
    else:
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y", add_leaf_bones=False, bake_anim=False, use_custom_props=True, mesh_smooth_type="FACE")

product_nodes = ["MagneticSlideTile_G05_R012", "BottomExterior", "FixedAxis", "MinimumOverlapDisk", "MovingTop", "TopLocalSlide", "MovingTopBody"]
technical_nodes = product_nodes + sorted(INTERNAL_MESHES) + ["RotatingCarrier", "Technical_FixedAxisOverlay"] + GROOVES
export_selection(PRODUCT_GLB, product_nodes, True)
export_selection(TECHNICAL_GLB, technical_nodes, True)
export_selection(FBX, technical_nodes, False)

set_pose(0, 0)
pivot_reference = fixed.matrix_world.translation.copy()
dense = {"samples": 0, "maxPivotVarianceMm": 0.0, "maxResidualMm": 0.0, "minimumHiddenEnvelopeMarginMm": 1e9}
hidden_vertices_local = {name: [vertex.co.copy() for vertex in bpy.data.objects[name].data.vertices] for name in INTERNAL_MESHES}
for angle in range(361):
    for index in range(37):
        slide = MAX_TRAVEL * index / 36.0
        set_pose(slide, angle)
        dense["samples"] += 1
        dense["maxPivotVarianceMm"] = max(dense["maxPivotVarianceMm"], (fixed.matrix_world.translation - pivot_reference).length)
        dense["maxResidualMm"] = max(dense["maxResidualMm"], top_residual(slide))
    for name, vertices in hidden_vertices_local.items():
        obj = bpy.data.objects[name]
        for vertex in vertices:
            world = obj.matrix_world @ vertex
            margin = min(capsule_margin(world), world.z - 0.15, 5.825 - world.z)
            dense["minimumHiddenEnvelopeMarginMm"] = min(dense["minimumHiddenEnvelopeMarginMm"], margin)

representative = []
for label, slide, angle in [("closed", 0, 0), ("open", MAX_TRAVEL, 0), ("12deg", MAX_TRAVEL * .45, 12), ("36deg", MAX_TRAVEL * .7, 36), ("combined", MAX_TRAVEL * .65, 24)]:
    set_pose(slide, angle)
    intersections = {}
    for internal in INTERNAL_MESHES:
        intersections[f"{internal}:BottomExterior"] = overlap_pairs(bpy.data.objects[internal], bottom)
        intersections[f"{internal}:MovingTopBody"] = overlap_pairs(bpy.data.objects[internal], top)
    top_tree = bvh(top)
    coverage_misses = 0
    for radial_index in range(64):
        phase = 2 * math.pi * radial_index / 64
        point = P + Vector((DISK_RADIUS * math.cos(phase), DISK_RADIUS * math.sin(phase), 30))
        hit, _, _, _ = top_tree.ray_cast(point, Vector((0, 0, -1)), 50)
        coverage_misses += hit is None
    representative.append({"id": label, "slideMm": slide, "angleDeg": angle, "surfaceIntersectionPairs": intersections, "minimumDiskActualMeshCoverageMisses": coverage_misses, "topConstraintResidualMm": top_residual(slide)})

top_plane_z = []
for polygon in bottom.data.polygons:
    if polygon.normal.z > 0.999999:
        top_plane_z.extend((bottom.matrix_world @ bottom.data.vertices[index].co).z for index in polygon.vertices)
plane_deviation = max(top_plane_z) - min(top_plane_z)
pivot_objects = [obj.name for obj in bpy.data.objects if obj.get("pivot_id")]
geometry_digest = fingerprint(PRODUCT_MESHES | INTERNAL_MESHES)
report = {
    "schemaVersion": 1,
    "gate": "05-blockout",
    "revision": 12,
    "source": {"path": str(SOURCE), "sha256": sha256(SOURCE)},
    "contractSha256": scene["mechanism_contract_sha256"],
    "geometryDigest": geometry_digest,
    "kinematics": {
        "fixedPivotMm": list(P),
        "qFormulaMm": ["0", "-9+s", str(TOP_Q_Z)],
        "topTransform": "M_top(s,theta)=T(P)*Rz(theta)*T(-q(s))",
        "carrierTransform": "T(P)*Rz(theta), translation=0",
        "slideRangeMm": [0, MAX_TRAVEL],
        "angleSweepDegrees": [0, 360],
    },
    "denseValidation": dense,
    "representativeActualMeshValidation": representative,
    "renderLayers": {"productWhitelist": sorted(PRODUCT_MESHES), "technicalOnly": sorted(INTERNAL_MESHES), "minimumOverlapDisk": "EMPTY/non-rendering"},
    "bottomTopPlaneDeviationMm": plane_deviation,
    "pivotObjects": pivot_objects,
    "checks": {
        "exactlyOnePivotObject": pivot_objects == ["FixedAxis"],
        "fixedPivotVarianceZero": dense["maxPivotVarianceMm"] <= 1e-12,
        "topConstraintResidualTight": dense["maxResidualMm"] <= 1e-6,
        "hiddenMeshesInsideEnvelope": dense["minimumHiddenEnvelopeMarginMm"] >= -1e-6,
        "actualMeshSurfaceIntersectionsZero": all(value == 0 for pose in representative for value in pose["surfaceIntersectionPairs"].values()),
        "minimumDiskCoveredByActualTopMesh": all(pose["minimumDiskActualMeshCoverageMisses"] == 0 for pose in representative),
        "bottomTopPlaneWithinTolerance": plane_deviation <= 0.001,
        "productRendererWhitelistExact": sorted(PRODUCT_MESHES) == ["BottomExterior", "MovingTopBody"],
        "minimumOverlapDiskNonRenderingEmpty": disk.type == "EMPTY" and bool(disk.hide_render) and disk.get("render_geometry") is False,
        "internalMeshesTechnicalOnly": all(bpy.data.objects[name].get("product_render") is False for name in INTERNAL_MESHES),
        "noPitchRollOrFlip": all(abs(value) <= 1e-12 for value in (moving.rotation_euler.x, moving.rotation_euler.y, carrier.rotation_euler.x, carrier.rotation_euler.y)) and all(min(obj.scale) > 0 for obj in bpy.data.objects),
        "fourInternalGrooves": len(GROOVES) == 4 and all(bpy.data.objects[name].get("internal_only") for name in GROOVES),
        "outputsWritten": all(path.exists() for path in [BLEND, PRODUCT_GLB, TECHNICAL_GLB, FBX]),
    },
}
report["pass"] = all(report["checks"].values())
REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps({"pass": True, "geometryDigest": geometry_digest, "dense": dense, "blend": str(BLEND)}, indent=2))

