"""Build the unified tri-blade spinner (metal-three-blade pipeline, Gate 05/06).

One deterministic bpy build replaces the three tri-blade shipping rotors.
Revision 4 follows the user's second 2026-09-05 rejection ("形状对但几何方向错"):

1. Wedge ring is a cone segment, not a wall. The flat turned table is the
   highest point; the ring slopes outward and down at 25 deg. The rim vertices
   alternate up/down, so the ring is 48 triangles whose tips point alternately
   inward and outward and whose ridge line zigzags around the circumference.
2. Blades are rounded-triangle petals. Outer end is an R12 arc, the sides
   meet the neighbouring blade in a 60 deg V notch whose apex sits on the dark
   seam, so the union of the three blades hides the hub in the top view.
3. Blades are 11.5 mm thick with a roof ridge: two roof planes fall from the
   centreline to near-vertical side walls, and one large slanted plane cuts
   the outer arc end. Three large planes per face, 0.5 mm two-segment bevels.

Secondary: seam 0.8 mm, table anisotropy (radial tangent) + fine concentric
bump, 24 wedges kept. All facet faces are flat-shaded; no subdivision.
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
REV = "rev-004"


def _arg(flag: str, default: str | None) -> str | None:
    argv = sys.argv
    return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else default


# `--variant NAME` renders a labelled comparison into <rev>-variant-NAME and
# never touches the shipping blend/fbx/glb. `--table-ratio` is the only
# parameter a variant may override (Gate 02 discrepancy: photo 0.797 vs user 0.70).
VARIANT = _arg("--variant", None)
REV_DIR = REV if VARIANT is None else f"{REV}-variant-{VARIANT}"
BLOCKOUT_DIR = PIPELINE_DIR / "evidence" / "05-blockout" / REV_DIR
GEOMETRY_DIR = PIPELINE_DIR / "evidence" / "06-geometry" / REV_DIR

BLEND_PATH = SOURCE_DIR / "UnifiedTriSpinner.blend" if VARIANT is None else Path("/tmp") / f"UnifiedTriSpinner-{VARIANT}.blend"
FBX_PATH = SOURCE_DIR / "UnifiedTriSpinner.fbx"
GLB_PATH = SOURCE_DIR / "UnifiedTriSpinner.glb"
COLLISION_FBX_PATH = SOURCE_DIR / "UnifiedTriSpinner_Collision.fbx"
STATS_PATH = GEOMETRY_DIR / "geometry-validation.json"

sys.path.insert(0, str(TOOLS_DIR))
import generate_dragon_scale_edc as legacy  # noqa: E402

# ---------------------------------------------------------------- contract --
WIDTH = 0.0650  # tip-to-tip circle, provisional
TIP_R = WIDTH * 0.5
BLADE_T = 0.0115  # user: 11-12 mm, cap table only 1.5 mm higher
BODY_HALF = BLADE_T * 0.5
BORE_R = 0.00635  # R188 outer diameter 12.7 mm
STEM_R = 0.0031  # R188 bore 6.35 mm

CAP_RATIO = 0.536  # photo: cap outer diameter / tip circle diameter
TABLE_RATIO = float(_arg("--table-ratio", "0.70"))  # user direction; photo reading 0.797 stays in Gate 02 as a discrepancy
CAP_R = TIP_R * CAP_RATIO
TABLE_R = CAP_R * TABLE_RATIO
SEAM_W = 0.0008  # user: tighten 1.0 -> 0.8 mm
SEAM_R = CAP_R + SEAM_W  # counterbore wall = blade root wall
TABLE_LIFT = 0.0015
TABLE_Z = BODY_HALF + TABLE_LIFT
WEDGE_SLOPE_DEG = 25.0  # user: 25-35; 25 keeps the most ring above the blade face
RIM_Z = TABLE_Z - (CAP_R - TABLE_R) * math.tan(math.radians(WEDGE_SLOPE_DEG))
ZIGZAG = 0.00055  # rim vertices alternate +/- this (drives the 48-face light/dark contrast)
N_WEDGE = 24
SKIRT_BOTTOM_Z = 0.0025
CORE_HALF = 0.0022  # counterbore floor height; core between the two floors

BLADE_ANGLES = (90.0, 210.0, 330.0)
ROOT_OVERLAP_DEG = 0.6  # roots overlap so the three petals union into one solid
NOTCH_HALF_DEG = 30.0  # 60 deg V between neighbouring petals
TIP_ARC_R = 0.0120
TIP_ARC_C = TIP_R - TIP_ARC_R
TIP_ARC_JOIN_DEG = 60.0  # the R12 arc spans +/-60 deg of the outer end
SIDE_SEGMENTS = 7
ROOF_SLOPE = 0.18  # z drop per metre of |y|: ~10 deg roof planes
END_PLANE_X = 0.0265
END_PLANE_SLOPE = math.tan(math.radians(32.0))
BLADE_BEVEL = 0.0005
BLADE_BEVEL_SEGMENTS = 2

RES = 1100
SAMPLES = 96
GEOMETRY_ONLY = "--geometry-only" in sys.argv  # smoke run: build, export, stats; skip renders


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
        socket(wave, "Scale").default_value = 2600.0
        socket(wave, "Distortion").default_value = 0.0
        socket(wave, "Detail").default_value = 0.0
        links.new(coords.outputs["Object"], wave.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        socket(bump, "Strength").default_value = ring_bump
        socket(bump, "Distance").default_value = 0.00003
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


def add_face(bm, verts, material_index):
    if len({v.index for v in verts}) < len(verts):
        return None
    try:
        face = bm.faces.new(verts)
    except ValueError:
        return None
    face.material_index = material_index
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


def boolean(target: bpy.types.Object, tool: bpy.types.Object, operation: str) -> None:
    bpy.context.view_layer.objects.active = target
    modifier = target.modifiers.new(operation.title(), "BOOLEAN")
    modifier.operation = operation
    modifier.solver = "EXACT"
    modifier.object = tool
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool, do_unlink=True)


# ------------------------------------------------------------------ cap ----
def build_cap(name: str, sign: float, materials) -> bpy.types.Object:
    """Flat table (highest point) + conical zigzag wedge ring + dark skirt.

    Inner ring: N_WEDGE vertices on the table edge at z = TABLE_Z.
    Outer ring: N_WEDGE vertices half a step later on the rim r = CAP_R, at
    RIM_Z +/- ZIGZAG alternately. Each (inner j, inner j+1, outer j) triangle
    points outward, each (outer j, inner j+1, outer j+1) triangle points inward:
    48 planar triangles with alternating normals around a 25 deg cone.
    """
    bm = bmesh.new()

    def vert(x, y, z):
        return bm.verts.new((x, y, sign * z))

    center = vert(0.0, 0.0, TABLE_Z)
    inner, outer, bottom = [], [], []
    for j in range(N_WEDGE):
        a_in = math.tau * j / N_WEDGE
        a_out = math.tau * (j + 0.5) / N_WEDGE
        inner.append(vert(TABLE_R * math.cos(a_in), TABLE_R * math.sin(a_in), TABLE_Z))
        rim_z = RIM_Z + (ZIGZAG if j % 2 == 0 else -ZIGZAG)
        outer.append(vert(CAP_R * math.cos(a_out), CAP_R * math.sin(a_out), rim_z))
        bottom.append(vert(CAP_R * math.cos(a_out), CAP_R * math.sin(a_out), SKIRT_BOTTOM_Z))
    bottom_center = vert(0.0, 0.0, SKIRT_BOTTOM_Z)
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    for j in range(N_WEDGE):
        nxt = (j + 1) % N_WEDGE
        add_face(bm, (center, inner[j], inner[nxt]), 0)  # flat turned table
        add_face(bm, (inner[j], outer[j], inner[nxt]), 1)  # tip points outward
        add_face(bm, (outer[j], outer[nxt], inner[nxt]), 1)  # tip points inward
        add_face(bm, (outer[j], bottom[j], outer[nxt]), 2)  # skirt (dark)
        add_face(bm, (bottom[j], bottom[nxt], outer[nxt]), 2)
        add_face(bm, (bottom_center, bottom[nxt], bottom[j]), 2)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return mesh_from_bmesh(name, bm, materials)


# --------------------------------------------------------------- blades ----
def blade_outline() -> list[tuple[float, float]]:
    """Top-view half outline (x along the blade, y >= 0), root to tip.

    Root sits on the seam circle at 60 deg (+ overlap) off the blade axis so
    neighbouring petals meet there. The side leaves the notch apex at 30 deg
    to the axis (60 deg V), bulges convexly, then joins the R12 tip arc at its
    tangent point. Convex by construction (directions decrease monotonically).
    """
    root_angle = math.radians(60.0 + ROOT_OVERLAP_DEG)
    inner_root = (0.0150 * math.cos(root_angle), 0.0150 * math.sin(root_angle))
    notch = math.radians(NOTCH_HALF_DEG)
    # The side line starts 0.6 mm inside the seam circle so the counterbore
    # cutter crosses the wall transversally instead of through a vertex.
    p0 = (
        SEAM_R * math.cos(root_angle) - 0.0006 * math.cos(notch),
        SEAM_R * math.sin(root_angle) - 0.0006 * math.sin(notch),
    )
    # Side: convex cubic Bezier from the notch (tangent 30 deg) to the tip arc
    # join at TIP_ARC_JOIN_DEG (tangent = join - 90 deg). The control polygon
    # turns one way only, so the curve is convex and the blade is widest
    # around mid-length, like the photo's rounded-triangle petals.
    join = math.radians(TIP_ARC_JOIN_DEG)
    p3 = (TIP_ARC_C + TIP_ARC_R * math.cos(join), TIP_ARC_R * math.sin(join))
    end_dir = join - math.pi / 2.0
    p1 = (p0[0] + 0.0050 * math.cos(notch), p0[1] + 0.0050 * math.sin(notch))
    p2 = (p3[0] - 0.0090 * math.cos(end_dir), p3[1] - 0.0090 * math.sin(end_dir))
    pts = [inner_root, p0]
    for step in range(1, SIDE_SEGMENTS):
        t = step / SIDE_SEGMENTS
        u = 1.0 - t
        pts.append((
            u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
        ))
    steps = max(4, int(round(TIP_ARC_JOIN_DEG / 5.0)))
    for step in range(steps + 1):
        a = join * (1.0 - step / steps)
        pts.append((TIP_ARC_C + TIP_ARC_R * math.cos(a), TIP_ARC_R * math.sin(a)))
    return pts


def roof_height(x: float, y: float) -> float:
    roof = BODY_HALF - ROOF_SLOPE * abs(y)
    end = BODY_HALF - END_PLANE_SLOPE * max(0.0, x - END_PLANE_X)
    return min(roof, end)


def with_plane_intersections(half: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Insert outline points where the roof plane and end plane meet, so the
    hull gets a clean crease instead of sliver triangles."""
    def diff(p):
        return (BODY_HALF - ROOF_SLOPE * abs(p[1])) - (BODY_HALF - END_PLANE_SLOPE * max(0.0, p[0] - END_PLANE_X))

    tagged = [(half[0], False)]
    for a, b in zip(half, half[1:]):
        da, db = diff(a), diff(b)
        if da * db < 0.0:
            t = da / (da - db)
            tagged.append(((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), True))
        tagged.append((b, False))
    # Drop plain points that sit within 0.25 mm of a crease point; near-
    # coincident hull vertices produce sliver faces that break the booleans.
    out = []
    for index, (point, is_crease) in enumerate(tagged):
        if not is_crease:
            neighbours = [tagged[k][0] for k in (index - 1, index + 1) if 0 <= k < len(tagged) and tagged[k][1]]
            if any(math.dist(point, n) < 0.00025 for n in neighbours):
                continue
        out.append(point)
    return out


def build_blade(name: str, angle_degrees: float, material) -> bpy.types.Object:
    """Convex hull: vertical side walls + two roof planes + one end plane
    (mirrored underneath). Deterministic, no jitter, no pockets."""
    bm = bmesh.new()
    half = with_plane_intersections(blade_outline())
    outline = list(half) + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    for x, y in outline:
        z = roof_height(x, y)
        for s in (1.0, -1.0):
            bm.verts.new((x, y, s * z))
    for x in (0.0080, 0.0140, 0.0200, END_PLANE_X):  # roof ridge
        for s in (1.0, -1.0):
            bm.verts.new((x, 0.0, s * BODY_HALF))
    result = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    doomed = {g for g in result["geom_interior"] + result["geom_unused"] if isinstance(g, bmesh.types.BMVert)}
    if doomed:
        bmesh.ops.delete(bm, geom=list(doomed), context="VERTS")
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1.0e-6)
    bmesh.ops.dissolve_degenerate(bm, dist=1.0e-6, edges=bm.edges[:])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts[:], edges=bm.edges[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = mesh_from_bmesh(name, bm, [material])
    # Bevel each convex petal before the union: the modifier is exact on a
    # hull and unreliable on boolean output. Union seams stay sharp on purpose.
    apply_bevel(obj, BLADE_BEVEL, BLADE_BEVEL_SEGMENTS)
    flat_shade(obj)
    obj.rotation_euler.z = math.radians(angle_degrees)
    legacy.select_only([obj])
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return obj


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


def wedge_ring_report(cap: bpy.types.Object) -> dict:
    mesh = cap.data
    ring = [p for p in mesh.polygons if p.material_index == 1]
    ring.sort(key=lambda p: math.atan2(p.center.y, p.center.x))
    angles, slopes = [], []
    for index, poly in enumerate(ring):
        nxt = ring[(index + 1) % len(ring)]
        dot = max(-1.0, min(1.0, poly.normal.dot(nxt.normal)))
        angles.append(math.degrees(math.acos(dot)))
        slopes.append(math.degrees(math.acos(max(-1.0, min(1.0, abs(poly.normal.z))))))
    table = [p for p in mesh.polygons if p.material_index == 0]
    table_tilt = max(math.degrees(math.acos(max(-1.0, min(1.0, abs(p.normal.z))))) for p in table) if table else 0.0
    tips_out = sum(1 for p in ring if sum(1 for v in p.vertices if math.hypot(*mesh.vertices[v].co.xy) > TABLE_R + 1e-6) == 1)
    return {
        "wedgeTriangles": len(ring),
        "wedges": len(ring) // 2,
        "tipsPointingOutward": tips_out,
        "tipsPointingInward": len(ring) - tips_out,
        "adjacentNormalAngleMinDeg": round(min(angles), 2),
        "adjacentNormalAngleMaxDeg": round(max(angles), 2),
        "faceSlopeMinDeg": round(min(slopes), 1),
        "faceSlopeMaxDeg": round(max(slopes), 1),
        "tableMaxTiltDeg": round(table_tilt, 2),
        "tableIsHighestPoint": TABLE_Z > RIM_Z + ZIGZAG,
    }


def blade_top_planes(body: bpy.types.Object) -> dict:
    """Large upward planes on the rotor body (area > 20 mm^2), per blade."""
    big = [p for p in body.data.polygons if p.normal.z > 0.30 and p.area > 20e-6]
    per_blade = {}
    for angle in BLADE_ANGLES:
        direction = Vector((math.cos(math.radians(angle)), math.sin(math.radians(angle)), 0.0))
        per_blade[f"blade@{int(angle)}"] = sum(1 for p in big if Vector((p.center.x, p.center.y, 0.0)).dot(direction) > 0.008)
    return per_blade


def notch_apex_radius(body: bpy.types.Object) -> float:
    """Smallest body radius along the notch bisectors (between blades)."""
    best = float("inf")
    for angle in BLADE_ANGLES:
        bis = math.radians(angle + 60.0)
        d = Vector((math.cos(bis), math.sin(bis)))
        for v in body.data.vertices:
            p = Vector((v.co.x, v.co.y))
            r = p.length
            if r < 1e-6 or r < SEAM_R - 1e-5:
                continue
            if abs(math.atan2(p.cross(d), p.dot(d))) < math.radians(1.0):
                best = min(best, r)
    return best


# ------------------------------------------------------------------ build ---
def configure_cycles(scene) -> str:
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = dev.type != "CPU"
        if any(dev.use for dev in prefs.devices):
            scene.cycles.device = "GPU"
            device = "METAL"
    except Exception:  # noqa: BLE001 - CPU fallback keeps the build deterministic
        scene.cycles.device = "CPU"
    return device


def main() -> None:
    for folder in (SOURCE_DIR, BLOCKOUT_DIR, GEOMETRY_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    legacy.clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    render_device = configure_cycles(scene)
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
    cap_table = pbr("M_UTS_CapTableTurned", (0.76, 0.77, 0.78), 1.0, 0.30, anisotropy=0.85, radial_tangent=True, ring_bump=0.09)
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

    # Rotor body: three bevelled convex petals, each counterbored on its own
    # (convex input keeps the exact solver clean), joined with a bored core
    # ring. Roots overlap inside the counterbore, where nothing is visible; the
    # core ring sits 0.05 mm below the petal floors so no faces are coplanar.
    blades = [build_blade(f"Blade_{index:02d}", angle, body_satin) for index, angle in enumerate(BLADE_ANGLES, start=1)]
    petal_audit = mesh_audit(blades[0])
    petal_planes_up = sum(1 for p in blades[0].data.polygons if p.normal.z > 0.30 and p.area > 20e-6)
    step_audit = {}
    for blade in blades:
        for sign in (1.0, -1.0):
            cutter = legacy.create_cylinder(f"Counterbore_{blade.name}", SEAM_R, 0.030, sign * (CORE_HALF + 0.015), shadow_gap, 96)
            boolean(blade, cutter, "DIFFERENCE")
        step_audit[f"{blade.name}-counterbored"] = mesh_audit(blade)
    core = legacy.create_ring("HubCore", SEAM_R - 0.0003, BORE_R, 2.0 * (CORE_HALF - 0.00005), 0.0, body_satin, segments=96, bevel=0.0, bevel_segments=1)
    flat_shade(core)
    legacy.select_only(blades + [core])
    bpy.context.view_layer.objects.active = blades[0]
    bpy.ops.object.join()
    body = blades[0]
    body.name = "RotorBody_OnePiece"
    body.data.name = "RotorBody_OnePiece_Mesh"
    body.data.materials.append(seam_steel)
    for polygon in body.data.polygons:
        r = math.hypot(polygon.center.x, polygon.center.y)
        z = abs(polygon.center.z)
        is_wall = abs(r - SEAM_R) < 0.00006 and abs(polygon.normal.z) < 0.5
        is_floor = abs(z - CORE_HALF) < 0.0001 and r < SEAM_R
        is_bore = r < BORE_R + 0.0001
        is_core_shell = r < SEAM_R - 0.0002 and z <= CORE_HALF
        if is_wall or is_floor or is_bore or is_core_shell:
            polygon.material_index = 1  # counterbore wall + floor + bore: dark seam steel
    body.parent = rotor
    flat_shade(body)
    # The petal side wall is one continuous curved surface in the photo, so it
    # is shaded smooth across its polyline facets. Roof, end plane, bevels and
    # the notch crease (separate shells) stay hard.
    for polygon in body.data.polygons:
        r = math.hypot(polygon.center.x, polygon.center.y)
        if abs(polygon.normal.z) < 0.15 and r > SEAM_R + 0.0010 and polygon.material_index == 0:
            polygon.use_smooth = True

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
    stem_len = SKIRT_BOTTOM_Z - 0.0005
    top_stem = legacy.create_cylinder("CapStem_Top", STEM_R, stem_len, 0.0005 + stem_len * 0.5, cap_skirt, 32)
    bottom_stem = legacy.create_cylinder("CapStem_Bottom", STEM_R, stem_len, -(0.0005 + stem_len * 0.5), cap_skirt, 32)
    top_stem.parent = top_cap_root
    bottom_stem.parent = bottom_cap_root
    flat_shade(top_stem)
    flat_shade(bottom_stem)

    visual = [body, outer_race, inner_race, *balls, top_cap, bottom_cap, top_stem, bottom_stem]

    # Collision ---------------------------------------------------------------
    collision = []
    half = blade_outline()
    col_points = list(half) + [(x, -y) for x, y in reversed(half) if y > 1e-9]
    for index, angle in enumerate(BLADE_ANGLES, start=1):
        col = legacy.create_prism(f"COL_Blade_{index:02d}", col_points, BLADE_T, 0.0, None)
        col.rotation_euler.z = math.radians(angle)
        col.parent = collision_root
        col.hide_render = True
        col.display_type = "WIRE"
        collision.append(col)
    col_hub = legacy.create_cylinder("COL_Hub", SEAM_R, 2.0 * CORE_HALF, 0.0, shadow_gap, 24)
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
    root["status"] = f"gate05-06 {REV} draft; visual approval pending; not shipping integrated"

    # Studio ------------------------------------------------------------------
    bpy.ops.mesh.primitive_plane_add(size=0.6, location=(0.0, 0.0, -0.0090))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_mat)

    bpy.ops.object.camera_add(location=(0.075, -0.095, 0.078))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.sensor_width = 36
    camera.data.clip_start = 0.001
    scene.camera = camera

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
        if not GEOMETRY_ONLY:
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
        "cap-macro": ((0.040, -0.052, 0.050), (0.0, 0.0, 0.006), 85, None),
        "cap-profile": ((0.055, -0.085, 0.024), (0.0, 0.0, 0.006), 100, None),
        "notch-macro": ((0.020, -0.075, 0.045), (0.016, -0.028, 0.004), 90, None),
    }
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    variant_views = ("hero", "cap-macro", "cap-profile", "top", "low")
    for name, (location, target, lens, ortho) in views.items():
        if VARIANT is not None and name not in variant_views:
            continue
        ground.hide_render = ortho is not None
        render(GEOMETRY_DIR / f"geometry-{name}.png", location, target, lens, ortho=ortho)
    ground.hide_render = False

    if VARIANT is not None:
        stats = {
            "status": f"{REV} labelled comparison variant '{VARIANT}'; not a revision; not exported",
            "tableRatio": TABLE_RATIO,
            "rimMeanBelowBladeFaceMm": round((BODY_HALF - RIM_Z) * 1000.0, 2),
            "wedgeRingWidthMm": round((CAP_R - TABLE_R) * 1000.0, 2),
            "wedgeRing": wedge_ring_report(top_cap),
            "views": list(variant_views),
        }
        STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print("UNIFIED_TRI_SPINNER_VARIANT " + json.dumps(stats, sort_keys=True))
        return

    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.75, 0.75, 0.74)
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    ground.hide_render = True
    location, target, lens, ortho = views["hero"]
    render(GEOMETRY_DIR / "geometry-workbench.png", location, target, lens, ortho=ortho)
    for name in ("hero", "top", "left-oblique", "low", "cap-macro", "cap-profile"):
        location, target, lens, ortho = views[name]
        render(BLOCKOUT_DIR / f"blockout-{name}.png", location, target, lens, ortho=ortho)
    ground.hide_render = False
    scene.render.engine = "CYCLES"

    top_cap_root.location.z = 0.030
    bearing_root.location.z = 0.012
    bottom_cap_root.location.z = -0.028
    render(GEOMETRY_DIR / "geometry-exploded.png", (0.110, -0.150, 0.090), (0.0, 0.0, 0.002), 72)
    for owner in (top_cap_root, bearing_root, bottom_cap_root):
        owner.location.z = 0.0

    # Geometry metrics are read before export triangulation so face counts and
    # normal angles describe the authored planes, not their triangle halves.
    body_audit = mesh_audit(body)
    cap_audit = mesh_audit(top_cap)
    wedge_ring = wedge_ring_report(top_cap)
    top_planes = blade_top_planes(body)
    apex_r = notch_apex_radius(body)

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
    tip_circle = 2.0 * max(math.hypot(v.co.x, v.co.y) for v in body.data.vertices)
    blade_top = max(v.co.z for v in body.data.vertices)
    half_outline = blade_outline()
    stats = {
        "status": f"gate05-06-{REV}-draft-visual-approval-pending",
        "provisional": True,
        "renderEngine": f"CYCLES/{render_device} {SAMPLES}spp denoised; blockout=WORKBENCH",
        "source": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "contract": {
            "widthMm": WIDTH * 1000.0, "bladeThicknessMm": BLADE_T * 1000.0,
            "capRatio": CAP_RATIO, "tableRatio": TABLE_RATIO,
            "tableAboveBladeFaceMm": TABLE_LIFT * 1000.0,
            "wedgeRingSlopeDeg": WEDGE_SLOPE_DEG, "wedges": N_WEDGE, "rimZigzagMm": ZIGZAG * 1000.0,
            "rimMeanBelowBladeFaceMm": round((BODY_HALF - RIM_Z) * 1000.0, 2),
            "seamWidthMm": SEAM_W * 1000.0, "counterboreRadiusMm": SEAM_R * 1000.0,
            "notchVDeg": 2.0 * NOTCH_HALF_DEG, "tipArcRadiusMm": TIP_ARC_R * 1000.0,
            "bladeMaxHalfWidthMm": round(max(y for _, y in half_outline) * 1000.0, 2),
            "roofSlopeDeg": round(math.degrees(math.atan(ROOF_SLOPE)), 1),
            "endPlaneSlopeDeg": round(math.degrees(math.atan(END_PLANE_SLOPE)), 1),
            "sideWallHeightAtWidestMm": round(2.0 * roof_height(0.0167, max(y for _, y in half_outline)) * 1000.0, 2),
            "bladeBevelMm": BLADE_BEVEL * 1000.0, "bladeBevelSegments": BLADE_BEVEL_SEGMENTS,
            "bearing": "R188 12.7x6.35x4.76 hidden",
        },
        "measured": {
            "tipCircleDiameterMm": tip_circle * 1000.0,
            "boundingWidthMm": max(extents.x, extents.y) * 1000.0,
            "assembledDepthMm": extents.z * 1000.0,
            "bladeTopZMm": blade_top * 1000.0,
            "capDiameterMm": cap_d * 1000.0,
            "capRatioActual": cap_d / tip_circle,
            "capTopAboveBladeFaceMm": (cap_hi.z - blade_top) * 1000.0,
            "notchApexRadiusMm": round(apex_r * 1000.0, 2) if apex_r < 1.0 else None,
            "hubVisibleInTopView": bool(apex_r > SEAM_R + 0.0010),
            "triangleCount": sum(len(p.vertices) - 2 for o in visual for p in o.data.polygons),
            "bodyAudit": body_audit,
            "bodyStepAudits": step_audit,
            "petalHullAudit": petal_audit,
            "petalLargeTopPlanesBeforeUnion": petal_planes_up,
            "bodyLargeTopPlanesPerBlade": top_planes,
            "capAudit": cap_audit,
            "wedgeRing": wedge_ring,
        },
        "forbidden": {
            "brightAnnulusBetweenCapAndBody": False, "materialFakedFacets": False,
            "smoothByAngleOnFacets": False, "smoothShadedCurvedSideWallsOnly": True, "subdivision": False,
            "randomScales": False, "bladePockets": False, "anisotropyOnWedges": False,
            "hubCollarOutsideSeam": False,
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
