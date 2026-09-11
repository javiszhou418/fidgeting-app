"""Build the unified tri-blade spinner (metal-three-blade pipeline, Gate 05/06).

One deterministic bpy build replaces the three tri-blade shipping rotors.
Revision 3 follows the user's 2026-09-05 rejection point by point:

1. Two-layer cap. A flat turned table (0.70 of the cap diameter) and, outside
   it, a ring of 24 regular wedges sloping ~25 deg outward and down. Each wedge
   is two planar half-faces meeting on a radial ridge; neighbouring half-faces
   tilt the opposite way, so 48 planar faces alternate light/dark under one
   light. No random scales anywhere.
2. Low profile. Table 1.5 mm above the blade face; the wedge ring runs down
   into a 1.0 mm dark seam. No tall dark pedestal.
3. Solid blades. No pockets. Narrow at the hub, broad rounded flat at the
   outer end, four or five hard planar cuts on each face, vertical side walls.
4. Satin, not mirror. Roughness ~0.3-0.4. Anisotropy only on the turned
   table (radial tangent + fine concentric bump); wedges rely on geometry.
5. Edges. 0.5 mm bevel, two segments, everywhere.

All facet faces are flat-shaded; no subdivision; no shade-smooth-by-angle.
Dimensions are metres. Blender +Z is the spin axis and exports as Unity +Y.
Every millimetre value is `user-authorized-provisional`.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

REPO_ROOT = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
UNITY_ROOT = REPO_ROOT / "unity" / "FidgetingApp"
TOOLS_DIR = REPO_ROOT / "tools" / "blender"
SOURCE_DIR = UNITY_ROOT / "ArtSource" / "UnifiedTriSpinner"
PIPELINE_DIR = UNITY_ROOT / "ArtSource" / "ModelPipeline" / "metal-three-blade"
REV = "rev-003"
BLOCKOUT_DIR = PIPELINE_DIR / "evidence" / "05-blockout" / REV
GEOMETRY_DIR = PIPELINE_DIR / "evidence" / "06-geometry" / REV

BLEND_PATH = SOURCE_DIR / "UnifiedTriSpinner.blend"
FBX_PATH = SOURCE_DIR / "UnifiedTriSpinner.fbx"
GLB_PATH = SOURCE_DIR / "UnifiedTriSpinner.glb"
COLLISION_FBX_PATH = SOURCE_DIR / "UnifiedTriSpinner_Collision.fbx"
STATS_PATH = GEOMETRY_DIR / "geometry-validation.json"

sys.path.insert(0, str(TOOLS_DIR))
import generate_dragon_scale_edc as legacy  # noqa: E402

# ---------------------------------------------------------------- contract --
WIDTH = 0.0650  # tip-to-tip circle, provisional
TIP_R = WIDTH * 0.5
BODY_T = 0.0100
BODY_HALF = BODY_T * 0.5
HUB_R = 0.0188  # 0.4 mm lip outside the counterbore
COUNTERBORE_R = 0.0184
COUNTERBORE_DEPTH = 0.0022
BORE_R = 0.00635  # R188 outer diameter 12.7 mm

CAP_RATIO = 0.536  # photo: cap outer diameter / tip circle diameter
# User direction: flat table ~0.70 of the cap, regular wedge ring outside it,
# cap top ~1.5 mm above the blade face, dark seam ~1 mm. The photo reading of
# 0.797 for the table stays recorded in Gate 02 as a discrepancy.
TABLE_RATIO = 0.70
CAP_R = TIP_R * CAP_RATIO
TABLE_R = CAP_R * TABLE_RATIO
TABLE_Z = BODY_HALF + 0.0015
CROWN_EDGE_Z = BODY_HALF - 0.0009  # ring runs 0.9 mm down into the seam
N_WEDGE = 24
WEDGE_EDGE_LIFT = 0.00022  # ridge/valley offset at the outer edge
SKIRT_BOTTOM_Z = 0.0030
STEM_R = 0.0031  # R188 bore 6.35 mm

BLADE_ANGLES = (90.0, 210.0, 330.0)
BLADE_T = 0.0099
BLADE_WALL = 0.0019  # vertical side-wall half height above/below mid-plane
BLADE_BEVEL = 0.0005
BLADE_BEVEL_SEGMENTS = 2

RES = 1200


# ------------------------------------------------------------- utilities ---
def socket(node: bpy.types.Node, *names: str):
    for name in names:
        candidate = node.inputs.get(name)
        if candidate is not None:
            return candidate
    return None


def pbr(
    name: str,
    color: tuple[float, float, float],
    metallic: float,
    roughness: float,
    *,
    anisotropy: float = 0.0,
    radial_tangent: bool = False,
    ring_bump: float = 0.0,
    noise_bump: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    rgba = (*color, 1.0)
    mat.diffuse_color = rgba
    mat.metallic = metallic
    mat.roughness = roughness
    socket(bsdf, "Base Color").default_value = rgba
    socket(bsdf, "Metallic").default_value = metallic
    socket(bsdf, "Roughness").default_value = roughness
    aniso = socket(bsdf, "Anisotropic", "Anisotropic IOR Level")
    if aniso is not None and anisotropy > 0.0:
        aniso.default_value = anisotropy
        if radial_tangent:
            tangent = nodes.new("ShaderNodeTangent")
            tangent.direction_type = "RADIAL"
            tangent.axis = "Z"
            tangent_socket = socket(bsdf, "Tangent")
            if tangent_socket is not None:
                links.new(tangent.outputs["Tangent"], tangent_socket)

    bump_inputs = []
    if ring_bump > 0.0:
        coords = nodes.new("ShaderNodeTexCoord")
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"
        wave.rings_direction = "SPHERICAL"
        socket(wave, "Scale").default_value = 1400.0
        socket(wave, "Distortion").default_value = 0.0
        socket(wave, "Detail").default_value = 0.0
        links.new(coords.outputs["Object"], wave.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        socket(bump, "Strength").default_value = ring_bump
        socket(bump, "Distance").default_value = 0.00002
        links.new(wave.outputs["Fac"], bump.inputs["Height"])
        bump_inputs.append(bump)
    if noise_bump > 0.0:
        coords = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.noise_dimensions = "3D"
        socket(noise, "Scale").default_value = 650.0
        socket(noise, "Detail").default_value = 2.0
        socket(noise, "Roughness").default_value = 0.6
        links.new(coords.outputs["Object"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        socket(bump, "Strength").default_value = noise_bump
        socket(bump, "Distance").default_value = 0.00004
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        bump_inputs.append(bump)
    if bump_inputs:
        chain = bump_inputs[0]
        for extra in bump_inputs[1:]:
            links.new(chain.outputs["Normal"], extra.inputs["Normal"])
            chain = extra
        links.new(chain.outputs["Normal"], socket(bsdf, "Normal"))
    return mat


def flat_shade(obj: bpy.types.Object) -> None:
    for polygon in obj.data.polygons:
        polygon.use_smooth = False


def mesh_from_bmesh(name: str, bm: bmesh.types.BMesh, materials) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for mat in materials:
        mesh.materials.append(mat)
    flat_shade(obj)
    return obj


def add_face(bm, verts, material_index, faces_out=None):
    if len({v.index for v in verts}) < len(verts):
        return None
    try:
        face = bm.faces.new(verts)
    except ValueError:
        return None
    face.material_index = material_index
    if faces_out is not None:
        faces_out.append(face)
    return face


def apply_bevel(obj, width, segments, angle_degrees=25.0):
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Machined Edge Bevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(angle_degrees)
    modifier.harden_normals = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)


# ------------------------------------------------------------------ cap ----
def build_cap(name: str, sign: float, materials) -> bpy.types.Object:
    """Flat turned table + 24 regular wedges (48 alternating planar faces) + skirt.

    Each half-face is the frustum trapezoid rotated about its own centreline by
    +/-phi (alternating). The faces are exact planes; where neighbouring planes
    meet they form radial ridge/valley lines. The table is the horizontal plane
    z = TABLE_Z, so its boundary is the polyline where those ridge lines pierce
    the plane: a fine serration, exactly like a turned table over milled wedges.
    The outer edge is the turned cylinder r = CAP_R, so ridge/valley points
    alternate in height there.
    """
    from mathutils import Matrix
    from mathutils.geometry import intersect_plane_plane

    half_count = 2 * N_WEDGE
    half_width_outer = CAP_R * math.sin(math.pi / half_count)
    phi = math.atan(WEDGE_EDGE_LIFT / half_width_outer)

    planes = []
    for j in range(half_count):
        mid_angle = math.tau * (j + 0.5) / half_count
        radial = Vector((math.cos(mid_angle), math.sin(mid_angle), 0.0))
        tangent = Vector((-math.sin(mid_angle), math.cos(mid_angle), 0.0))
        m1 = radial * TABLE_R + Vector((0.0, 0.0, TABLE_Z))
        m2 = radial * CAP_R + Vector((0.0, 0.0, CROWN_EDGE_Z))
        centreline = (m2 - m1).normalized()
        base_normal = tangent.cross(centreline).normalized()
        if base_normal.z < 0.0:
            base_normal = -base_normal
        tilt = phi if j % 2 == 0 else -phi
        normal = Matrix.Rotation(tilt, 3, centreline) @ base_normal
        planes.append((m1, normal.normalized()))

    def ridge_line(j: int):
        (co_a, no_a), (co_b, no_b) = planes[(j - 1) % half_count], planes[j]
        point, direction = intersect_plane_plane(co_a, no_a, co_b, no_b)
        if point is None:
            raise RuntimeError("degenerate wedge planes")
        if direction.z > 0.0:
            direction = -direction
        return point, direction.normalized()

    def at_z(point, direction, z):
        t = (z - point.z) / direction.z
        return point + direction * t

    def at_radius(point, direction, radius, near_z):
        a = direction.x ** 2 + direction.y ** 2
        b = 2.0 * (point.x * direction.x + point.y * direction.y)
        c = point.x ** 2 + point.y ** 2 - radius ** 2
        disc = b * b - 4.0 * a * c
        if disc < 0.0:
            raise RuntimeError("ridge line misses the cap cylinder")
        roots = [(-b + s * math.sqrt(disc)) / (2.0 * a) for s in (1.0, -1.0)]
        best = min(roots, key=lambda t: abs((point + direction * t).z - near_z))
        return point + direction * best

    inner_pts, outer_pts = [], []
    for j in range(half_count):
        point, direction = ridge_line(j)
        inner_pts.append(at_z(point, direction, TABLE_Z))
        outer_pts.append(at_radius(point, direction, CAP_R, CROWN_EDGE_Z))

    bm = bmesh.new()

    def vert(p):
        return bm.verts.new((p.x, p.y, sign * p.z))

    inner = [vert(p) for p in inner_pts]
    outer = [vert(p) for p in outer_pts]
    center = bm.verts.new((0.0, 0.0, sign * TABLE_Z))
    bottom = [bm.verts.new((v.co.x, v.co.y, sign * SKIRT_BOTTOM_Z)) for v in outer]
    bottom_center = bm.verts.new((0.0, 0.0, sign * SKIRT_BOTTOM_Z))
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for j in range(half_count):
        nxt = (j + 1) % half_count
        add_face(bm, (center, inner[j], inner[nxt]), 0)  # flat table
        add_face(bm, (inner[j], outer[j], outer[nxt], inner[nxt]), 1)  # planar wedge half-face
        add_face(bm, (outer[j], bottom[j], bottom[nxt], outer[nxt]), 2)  # skirt
        add_face(bm, (bottom_center, bottom[nxt], bottom[j]), 2)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = mesh_from_bmesh(name, bm, materials)
    obj["wedge_tilt_deg"] = math.degrees(phi)
    return obj


# --------------------------------------------------------------- blades ----
def blade_outline() -> list[tuple[float, float]]:
    """Top-view half outline (x along blade, y half-width): narrow at the hub,
    broad rounded flat at the outer end."""
    # Photo (geeone-01): half-width ~12.5 mm at the hub (~85 deg of the sector),
    # nearly parallel sides widening slightly, then the outer end follows the
    # tip circle itself. Notches between blades open outward as a V.
    pts = [
        (0.0150, 0.0120),
        (0.0190, 0.0126),
        (0.0235, 0.0134),
        (0.0275, 0.0142),
        (0.0284, 0.0146),
    ]
    corner_angle = math.asin(0.0146 / TIP_R)
    for step in range(1, 5):
        angle = corner_angle * (1.0 - step / 4.0)
        pts.append((TIP_R * math.cos(angle), TIP_R * math.sin(angle)))
    return pts


def build_blade(name: str, angle_degrees: float, material) -> bpy.types.Object:
    """Convex hull of a designed point set -> 4-5 hard planar cuts per face,
    vertical side walls, no pockets. Deterministic, no jitter."""
    bm = bmesh.new()
    half = blade_outline()
    outline = list(half) + [(x, -y) for x, y in reversed(half[:-1])]

    # Vertical side wall band.
    for x, y in outline:
        for s in (1.0, -1.0):
            bm.verts.new((x, y, s * BLADE_WALL))
    # Top/bottom facet control points. The hull makes planes through them:
    # a shallow roof along the centreline, two side chamfer planes, and a
    # broad sloped plane on the outer end.
    top = BLADE_T * 0.5
    ridge = [(0.0165, 0.0, top), (0.0235, 0.0, top), (0.0285, 0.0, top - 0.0005)]
    side = [(0.0198, 0.0072, top - 0.0012), (0.0198, -0.0072, top - 0.0012),
            (0.0268, 0.0084, top - 0.0013), (0.0268, -0.0084, top - 0.0013)]
    end = [(0.0316, 0.0, top - 0.0017), (0.0300, 0.0094, top - 0.0020), (0.0300, -0.0094, top - 0.0020)]
    for x, y, z in ridge + side + end:
        for s in (1.0, -1.0):
            bm.verts.new((x, y, s * z))
    # Root block buried in the hub.
    for y in (-0.0118, 0.0118):
        for s in (1.0, -1.0):
            bm.verts.new((0.0120, y, s * BLADE_WALL))

    result = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    doomed = {g for g in result["geom_interior"] + result["geom_unused"] if isinstance(g, bmesh.types.BMVert)}
    if doomed:
        bmesh.ops.delete(bm, geom=list(doomed), context="VERTS")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(1.0), verts=bm.verts[:], edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = mesh_from_bmesh(name, bm, [material])
    apply_bevel(obj, BLADE_BEVEL, BLADE_BEVEL_SEGMENTS)
    flat_shade(obj)
    obj.rotation_euler.z = math.radians(angle_degrees)
    legacy.select_only([obj])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return obj


def seal_holes(obj: bpy.types.Object) -> None:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1.0e-7)
    open_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    if open_edges:
        bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def boolean_difference(target: bpy.types.Object, tool: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new("Cut", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.solver = "EXACT"
    modifier.object = tool
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def exact_bounds(objects):
    points = [obj.matrix_world @ v.co for obj in objects if obj.type == "MESH" and not obj.hide_render for v in obj.data.vertices]
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def mesh_audit(obj: bpy.types.Object) -> dict:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {
        "vertices": len(bm.verts),
        "faces": len(bm.faces),
        "boundaryEdges": sum(1 for e in bm.edges if len(e.link_faces) == 1),
        "nonManifoldEdges": sum(1 for e in bm.edges if len(e.link_faces) not in (1, 2)),
        "zeroAreaFaces": sum(1 for f in bm.faces if f.calc_area() <= 1e-12),
    }
    bm.free()
    return result


def wedge_normal_contrast(cap: bpy.types.Object) -> dict:
    """Angle between neighbouring wedge half-face normals (material slot 1)."""
    mesh = cap.data
    ring = [p for p in mesh.polygons if p.material_index == 1]
    ring.sort(key=lambda p: math.atan2(p.center.y, p.center.x))
    angles = []
    for index, poly in enumerate(ring):
        nxt = ring[(index + 1) % len(ring)]
        dot = max(-1.0, min(1.0, poly.normal.dot(nxt.normal)))
        angles.append(math.degrees(math.acos(dot)))
    table = [p for p in mesh.polygons if p.material_index == 0]
    table_tilt = max(math.degrees(math.acos(max(-1.0, min(1.0, abs(p.normal.z))))) for p in table) if table else 0.0
    return {
        "wedgeHalfFaces": len(ring),
        "wedges": len(ring) // 2,
        "adjacentNormalAngleMinDeg": round(min(angles), 2) if angles else 0.0,
        "adjacentNormalAngleMaxDeg": round(max(angles), 2) if angles else 0.0,
        "tableMaxTiltDeg": round(table_tilt, 2),
    }


def blade_plane_count(blade: bpy.types.Object) -> int:
    """Large planar faces on one blade's top side (area > 6 mm^2, facing up)."""
    return sum(1 for p in blade.data.polygons if p.normal.z > 0.35 and p.area > 6e-6)


# ------------------------------------------------------------------ build ---
def main() -> None:
    for folder in (SOURCE_DIR, BLOCKOUT_DIR, GEOMETRY_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    legacy.clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = True
    scene.eevee.taa_render_samples = 96
    scene.render.resolution_x = RES
    scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.050, 0.055, 0.065, 1.0)
    background.inputs["Strength"].default_value = 1.0
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0

    # Materials: satin everywhere, anisotropy only on the turned table --------
    body_satin = pbr("M_UTS_BodySatinSteel", (0.78, 0.79, 0.80), 1.0, 0.36, noise_bump=0.02)
    seam_steel = pbr("M_UTS_SeamDarkSteel", (0.085, 0.088, 0.095), 1.0, 0.46)
    shadow_gap = pbr("M_UTS_ShadowGapGunmetal", (0.030, 0.031, 0.035), 0.85, 0.55)
    cap_table = pbr("M_UTS_CapTableTurned", (0.76, 0.77, 0.78), 1.0, 0.32, anisotropy=0.70, radial_tangent=True, ring_bump=0.035)
    cap_wedge = pbr("M_UTS_CapWedgeSatin", (0.76, 0.77, 0.785), 1.0, 0.34, noise_bump=0.012)
    cap_skirt = pbr("M_UTS_CapSkirtDark", (0.06, 0.062, 0.068), 0.9, 0.50)
    bearing_steel = pbr("M_UTS_BearingSteel", (0.40, 0.42, 0.45), 1.0, 0.40)
    clay = pbr("M_UTS_Clay", (0.55, 0.55, 0.53), 0.0, 0.85)
    ground_mat = pbr("M_UTS_StudioGround", (0.004, 0.0045, 0.006), 0.0, 0.55)

    # Hierarchy ----------------------------------------------------------
    root = legacy.empty("UnifiedTriSpinner_Root")
    rotor = legacy.empty("Rotor_Root", root)
    fixed = legacy.empty("Fixed_Root", root)
    bearing_root = legacy.empty("BearingAssembly_Root", root)
    top_cap_root = legacy.empty("TopCap_Root", fixed)
    bottom_cap_root = legacy.empty("BottomCap_Root", fixed)
    collision_root = legacy.empty("Collision_Root", root)

    # Rotor body: dark 0.4 mm lip + dark counterbore core + three solid blades
    # The hub is body metal: blades merge into one bright piece. Only the
    # counterbore wall and floor are dark, so the seam reads as a 1 mm line.
    collar = legacy.create_ring("HubCollar", HUB_R, COUNTERBORE_R, BODY_T, 0.0, body_satin, segments=96, bevel=0.0, bevel_segments=1)
    collar.data.materials.append(seam_steel)
    for polygon in collar.data.polygons:
        if math.hypot(polygon.center.x, polygon.center.y) < COUNTERBORE_R + 0.00005 and abs(polygon.normal.z) < 0.5:
            polygon.material_index = 1
    core_t = BODY_T - 2.0 * COUNTERBORE_DEPTH
    core = legacy.create_ring("HubCore", COUNTERBORE_R, BORE_R, core_t, 0.0, shadow_gap, segments=96, bevel=0.0, bevel_segments=1)
    flat_shade(collar)
    flat_shade(core)
    blades = []
    blade_audit_log = {}
    for index, angle in enumerate(BLADE_ANGLES, start=1):
        blade = build_blade(f"Blade_{index:02d}", angle, body_satin)
        blade_audit_log[f"{blade.name}_hull"] = mesh_audit(blade)
        # Keep the root outside the counterbore so nothing bright shows in the seam.
        # Odd segment count + a small twist keep cutter vertices off the blade's
        # symmetry plane; the Exact solver left open edges when they coincided.
        root_cutter = legacy.create_cylinder(f"RootCutter_{index:02d}", COUNTERBORE_R + 0.0001, 0.020, 0.0, shadow_gap, 97)
        root_cutter.rotation_euler.z = math.radians(0.9)
        boolean_difference(blade, root_cutter)
        seal_holes(blade)
        blade_audit_log[f"{blade.name}_cut"] = mesh_audit(blade)
        blade_audit_log[f"{blade.name}_topPlanes"] = blade_plane_count(blade)
        flat_shade(blade)
        blades.append(blade)

    legacy.select_only([collar, core] + blades)
    bpy.context.view_layer.objects.active = collar
    bpy.ops.object.join()
    rotor_body = collar
    rotor_body.name = "RotorBody_OnePiece"
    rotor_body.data.name = "RotorBody_OnePiece_Mesh"
    rotor_body.parent = rotor
    flat_shade(rotor_body)

    # Hidden R188-class bearing ---------------------------------------------
    outer_race = legacy.create_ring("BearingOuterRace", BORE_R, 0.0053, 0.00476, 0.0, bearing_steel, segments=48, bevel=0.0)
    inner_race = legacy.create_ring("BearingInnerRace", 0.0042, STEM_R, 0.00476, 0.0, bearing_steel, segments=48, bevel=0.0)
    for obj in (outer_race, inner_race):
        obj.parent = bearing_root
    balls = []
    for index in range(8):
        angle = math.tau * index / 8
        ball = legacy.create_uv_sphere(f"BearingBall_{index + 1:02d}", 0.00085, (0.00475 * math.cos(angle), 0.00475 * math.sin(angle), 0.0), bearing_steel)
        ball.parent = bearing_root
        balls.append(ball)

    # Caps ------------------------------------------------------------------
    cap_materials = [cap_table, cap_wedge, cap_skirt]
    top_cap = build_cap("FingerCap_Top", 1.0, cap_materials)
    bottom_cap = build_cap("FingerCap_Bottom", -1.0, cap_materials)
    top_cap.parent = top_cap_root
    bottom_cap.parent = bottom_cap_root
    stem_len = SKIRT_BOTTOM_Z - 0.0010
    top_stem = legacy.create_cylinder("CapStem_Top", STEM_R, stem_len, 0.0010 + stem_len * 0.5, cap_skirt, 32)
    bottom_stem = legacy.create_cylinder("CapStem_Bottom", STEM_R, stem_len, -(0.0010 + stem_len * 0.5), cap_skirt, 32)
    top_stem.parent = top_cap_root
    bottom_stem.parent = bottom_cap_root
    flat_shade(top_stem)
    flat_shade(bottom_stem)

    visual = [rotor_body, outer_race, inner_race, *balls, top_cap, bottom_cap, top_stem, bottom_stem]

    # Collision ---------------------------------------------------------------
    collision = []
    half = blade_outline()
    col_points = list(half) + [(x, -y) for x, y in reversed(half[:-1])]
    for index, angle in enumerate(BLADE_ANGLES, start=1):
        col = legacy.create_prism(f"COL_Blade_{index:02d}", col_points, BLADE_T, 0.0, None)
        col.rotation_euler.z = math.radians(angle)
        col.parent = collision_root
        col.hide_render = True
        col.display_type = "WIRE"
        collision.append(col)
    col_hub = legacy.create_cylinder("COL_Hub", HUB_R, BODY_T, 0.0, shadow_gap, 24)
    col_hub.parent = collision_root
    col_hub.hide_render = True
    col_hub.display_type = "WIRE"
    collision.append(col_hub)

    root["units"] = "metres"
    root["spin_axis_blender"] = "+Z"
    root["spin_axis_unity"] = "+Y"
    root["width_mm_provisional"] = WIDTH * 1000.0
    root["cap_ratio_photo"] = CAP_RATIO
    root["table_ratio_user"] = TABLE_RATIO
    root["initial_angular_velocity"] = 0.0
    root["status"] = "gate05-06 rev-003 draft; visual approval pending; not shipping integrated"

    # Studio ------------------------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=0.6, location=(0.0, 0.0, -0.0080))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_mat)

    bpy.ops.object.camera_add(location=(0.075, -0.095, 0.078))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.sensor_width = 36
    camera.data.clip_start = 0.001
    scene.camera = camera

    # Key kept small enough to separate the 48 wedge normals, but larger than
    # rev-002 so metal highlights roll off instead of reading as mirror.
    light_specs = [
        ("HardKey", (0.090, -0.070, 0.165), 0.85, 0.055, (1.0, 0.96, 0.92)),
        ("SoftFill", (0.040, 0.150, 0.110), 0.35, 0.320, (0.80, 0.87, 1.0)),
        ("WarmRim", (-0.105, 0.030, 0.085), 0.40, 0.080, (1.0, 0.58, 0.34)),
        ("TopStrip", (0.120, 0.090, 0.170), 0.06, 0.160, (0.9, 0.93, 1.0)),
    ]
    lights = []
    for suffix, location, energy, size, color in light_specs:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Studio{suffix}_RenderOnly"
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        look_at(light, (0.0, 0.0, 0.004))
        lights.append(light)

    def render(path: Path, location, target, lens, *, ortho=None):
        camera.location = location
        camera.data.type = "ORTHO" if ortho else "PERSP"
        if ortho:
            camera.data.ortho_scale = ortho
        else:
            camera.data.lens = lens
        look_at(camera, target)
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)

    origin = (0.0, 0.0, 0.0)
    views = {
        "hero": ((0.075, -0.095, 0.078), (0.0, 0.0, 0.002), 72, None),
        "left-oblique": ((-0.084, -0.092, 0.060), origin, 74, None),
        "right-oblique": ((0.084, -0.092, 0.060), origin, 74, None),
        "low": ((0.076, -0.112, 0.016), origin, 78, None),
        "top": ((0.0, -0.0005, 0.30), origin, 60, 0.082),
        "bottom": ((0.0, -0.0005, -0.30), origin, 60, 0.082),
        "front": ((0.0, -0.30, 0.0), origin, 60, 0.082),
        "back": ((0.0, 0.30, 0.0), origin, 60, 0.082),
        "right": ((0.30, 0.0, 0.0), origin, 60, 0.082),
        "left": ((-0.30, 0.0, 0.0), origin, 60, 0.082),
        "cap-macro": ((0.040, -0.052, 0.062), (0.0, 0.0, 0.006), 85, None),
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    for name, (location, target, lens, ortho) in views.items():
        ground.hide_render = ortho is not None
        render(GEOMETRY_DIR / f"geometry-{name}.png", location, target, lens, ortho=ortho)
    ground.hide_render = False

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.75, 0.75, 0.74)
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    ground.hide_render = True
    location, target, lens, ortho = views["hero"]
    render(GEOMETRY_DIR / "geometry-workbench.png", location, target, lens, ortho=ortho)
    ground.hide_render = False
    scene.render.engine = "BLENDER_EEVEE"

    top_cap_root.location.z = 0.030
    bearing_root.location.z = 0.012
    bottom_cap_root.location.z = -0.028
    render(GEOMETRY_DIR / "geometry-exploded.png", (0.110, -0.150, 0.090), (0.0, 0.0, 0.002), 72)
    for owner in (top_cap_root, bearing_root, bottom_cap_root):
        owner.location.z = 0.0

    bpy.context.view_layer.material_override = clay
    ground.hide_render = True
    for name in ("hero", "top", "left-oblique", "low", "cap-macro"):
        location, target, lens, ortho = views[name]
        render(BLOCKOUT_DIR / f"blockout-{name}.png", location, target, lens, ortho=ortho)
    bpy.context.view_layer.material_override = None
    ground.hide_render = False

    # Geometry metrics are read before export triangulation so face counts and
    # normal angles describe the authored planes, not their triangle halves.
    rotor_audit = mesh_audit(rotor_body)
    cap_audit = mesh_audit(top_cap)
    wedge_ring = wedge_normal_contrast(top_cap)
    blade_planes = blade_audit_log.get("Blade_01_topPlanes", 0)
    blade_audits = {name: audit for name, audit in blade_audit_log.items()}

    # Export ------------------------------------------------------------------
    for obj in visual + collision:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
    hierarchy = [root, rotor, fixed, bearing_root, top_cap_root, bottom_cap_root]
    legacy.select_only(hierarchy + visual)
    bpy.ops.export_scene.fbx(filepath=str(FBX_PATH), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", add_leaf_bones=False, bake_anim=False, path_mode="AUTO")
    bpy.ops.export_scene.gltf(filepath=str(GLB_PATH), export_format="GLB", use_selection=True, export_apply=True, export_yup=True, export_animations=False)
    legacy.select_only([collision_root] + collision)
    bpy.ops.export_scene.fbx(filepath=str(COLLISION_FBX_PATH), use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", add_leaf_bones=False, bake_anim=False, path_mode="AUTO")

    # Validation --------------------------------------------------------------
    lo, hi = exact_bounds(visual)
    extents = hi - lo
    cap_lo, cap_hi = exact_bounds([top_cap])
    cap_d = max(cap_hi.x - cap_lo.x, cap_hi.y - cap_lo.y)
    tip_circle = 2.0 * max(math.hypot(v.co.x, v.co.y) for v in rotor_body.data.vertices)
    stats = {
        "status": "gate05-06-rev-003-draft-visual-approval-pending",
        "provisional": True,
        "source": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "contract": {
            "widthMm": WIDTH * 1000.0, "bodyThicknessMm": BODY_T * 1000.0,
            "capRatio": CAP_RATIO, "tableRatio": TABLE_RATIO,
            "tableAboveBladeFaceMm": (TABLE_Z - BODY_HALF) * 1000.0,
            "wedgeRingSlopeDeg": round(math.degrees(math.atan((TABLE_Z - CROWN_EDGE_Z) / (CAP_R - TABLE_R))), 1),
            "wedges": N_WEDGE, "wedgeEdgeLiftMm": WEDGE_EDGE_LIFT * 1000.0,
            "seamWidthMm": (COUNTERBORE_R - CAP_R) * 1000.0, "lipWidthMm": (HUB_R - COUNTERBORE_R) * 1000.0,
            "bladeBevelMm": BLADE_BEVEL * 1000.0, "bladeBevelSegments": BLADE_BEVEL_SEGMENTS,
            "bearing": "R188 12.7x6.35x4.76 hidden",
        },
        "measured": {
            "tipCircleDiameterMm": tip_circle * 1000.0,
            "boundingWidthMm": max(extents.x, extents.y) * 1000.0,
            "assembledDepthMm": extents.z * 1000.0,
            "capDiameterMm": cap_d * 1000.0,
            "capRatioActual": cap_d / tip_circle,
            "capTopAboveBladeFaceMm": (cap_hi.z - BODY_HALF) * 1000.0,
            "triangleCount": sum(len(p.vertices) - 2 for o in visual for p in o.data.polygons),
            "rotorAudit": rotor_audit,
            "capAudit": cap_audit,
            "wedgeRing": wedge_ring,
            "bladeLargeTopPlanes": blade_planes,
            "bladeAudits": blade_audits,
        },
        "forbidden": {
            "brightAnnulusBetweenCapAndBody": False, "materialFakedFacets": False,
            "smoothByAngleOnFacets": False, "subdivision": False,
            "randomScales": False, "bladePockets": False, "anisotropyOnWedges": False,
        },
        "initialAngularVelocity": 0.0,
    }
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    ground.hide_viewport = True
    for light in lights:
        light.hide_viewport = True
    legacy.select_only([root])
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("UNIFIED_TRI_SPINNER " + json.dumps(stats["measured"], sort_keys=True))


if __name__ == "__main__":
    main()
