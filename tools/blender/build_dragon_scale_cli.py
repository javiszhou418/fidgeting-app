"""Build the 85 mm reference-matched Dragon Scale EDC spinner.

This is the high-detail companion to the cli-anything-blender JSON project at
ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI.blend-cli.json.  The
installed CLI intentionally stays the state/manifest layer; exact lofts,
booleans, anisotropic materials, export, and verification renders are executed
by Blender because they are beyond the CLI primitive schema.

All dimensions are metres. Blender +Z is the mechanical spin axis and exports
as Unity +Y.
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
SOURCE_DIR = UNITY_ROOT / "ArtSource" / "DragonScaleEDC" / "CLIAnything"
ARTIFACT_DIR = UNITY_ROOT / "Artifacts" / "DragonScaleEDC_CLIAnything"

BLEND_PATH = SOURCE_DIR / "DragonScaleEDC_CLI_85mm.blend"
FBX_PATH = SOURCE_DIR / "DragonScaleEDC_CLI_85mm.fbx"
GLB_PATH = SOURCE_DIR / "DragonScaleEDC_CLI_85mm.glb"
COLLISION_FBX_PATH = SOURCE_DIR / "DragonScaleEDC_CLI_85mm_Collision.fbx"
STATS_PATH = ARTIFACT_DIR / "dragon-scale-cli-validation.json"

PREVIEW_PATHS = {
    "top": ARTIFACT_DIR / "dragon-scale-cli-top.png",
    "hero": ARTIFACT_DIR / "dragon-scale-cli-hero.png",
    "left_oblique": ARTIFACT_DIR / "dragon-scale-cli-left-oblique.png",
    "right_oblique": ARTIFACT_DIR / "dragon-scale-cli-right-oblique.png",
    "low": ARTIFACT_DIR / "dragon-scale-cli-low.png",
    "side": ARTIFACT_DIR / "dragon-scale-cli-side.png",
    "exploded": ARTIFACT_DIR / "dragon-scale-cli-exploded.png",
}

# Hard dimensions read from the annotated reference.
TARGET_WIDTH = 0.0850
TARGET_CAP_DIAMETER = TARGET_WIDTH * 0.52
TARGET_BODY_DEPTH = TARGET_WIDTH * 0.09
TARGET_ASSEMBLED_DEPTH = TARGET_WIDTH * 0.20
CAP_RADIUS = TARGET_CAP_DIAMETER * 0.5
TIP_RADIUS = TARGET_WIDTH / math.sqrt(3.0) - 0.000588
BEARING_OD = 0.0220
BEARING_ID = 0.0080
BEARING_WIDTH = 0.0070

PRIMARY_SEGMENTS = 96
SECONDARY_SEGMENTS = 72
FACET_SEGMENTS = 24

FORBIDDEN_DECORATIVE_AXIS_RINGS = (
    "RotorCrownTrim",
    "FingerCapTop_PolishedBezel",
    "FingerCapBottom_PolishedBezel",
    "FingerCapTop_ShadowGap",
    "FingerCapBottom_ShadowGap",
)

sys.path.insert(0, str(TOOLS_DIR))
import generate_dragon_scale_edc as legacy  # noqa: E402


def ensure_dirs() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def socket(node: bpy.types.Node, *names: str):
    for name in names:
        candidate = node.inputs.get(name)
        if candidate is not None:
            return candidate
    return None


def machined_material(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
    *,
    anisotropy: float = 0.0,
    micro_strength: float = 0.0,
    micro_scale: float = 520.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.metallic = metallic
    mat.roughness = roughness
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    socket(bsdf, "Base Color").default_value = color
    socket(bsdf, "Metallic").default_value = metallic
    socket(bsdf, "Roughness").default_value = roughness
    anisotropic_input = socket(bsdf, "Anisotropic IOR Level", "Anisotropic")
    if anisotropic_input is not None:
        anisotropic_input.default_value = anisotropy
    ior_input = socket(bsdf, "IOR")
    if ior_input is not None:
        ior_input.default_value = 1.48 if metallic < 0.5 else 2.1

    if micro_strength > 0.0:
        texcoord = nodes.new("ShaderNodeTexCoord")
        noise = nodes.new("ShaderNodeTexNoise")
        noise.noise_dimensions = "3D"
        socket(noise, "Scale").default_value = micro_scale
        socket(noise, "Detail").default_value = 2.2
        socket(noise, "Roughness").default_value = 0.68
        bump = nodes.new("ShaderNodeBump")
        socket(bump, "Strength").default_value = micro_strength
        socket(bump, "Distance").default_value = 0.000055
        links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], socket(bsdf, "Normal"))
    return mat


def create_radial_crown(
    name: str,
    radius: float,
    depth: float,
    face_z: float,
    facing: float,
    materials: tuple[bpy.types.Material, bpy.types.Material, bpy.types.Material],
    sectors: int = FACET_SEGMENTS,
) -> bpy.types.Object:
    """Create a shallow crowned radial face with real alternating sectors."""
    half = depth * 0.5
    back_z = face_z - facing * depth
    center_z = face_z + facing * 0.00018
    vertices = [(0.0, 0.0, back_z)]
    back_start = len(vertices)
    for index in range(sectors):
        angle = math.tau * index / sectors
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), back_z))
    face_center = len(vertices)
    vertices.append((0.0, 0.0, center_z))
    face_start = len(vertices)
    for index in range(sectors):
        angle = math.tau * index / sectors
        vertices.append((radius * math.cos(angle), radius * math.sin(angle), face_z))

    faces: list[tuple[int, ...]] = []
    material_indices: list[int] = []
    for index in range(sectors):
        nxt = (index + 1) % sectors
        faces.append((0, back_start + index, back_start + nxt))
        material_indices.append(2)
        faces.append(
            (
                back_start + index,
                face_start + index,
                face_start + nxt,
                back_start + nxt,
            )
        )
        material_indices.append(2)
        if facing > 0.0:
            faces.append((face_center, face_start + index, face_start + nxt))
        else:
            faces.append((face_center, face_start + nxt, face_start + index))
        material_indices.append(index % 2)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    for mat in materials:
        mesh.materials.append(mat)
    for polygon, material_index in zip(mesh.polygons, material_indices):
        polygon.material_index = material_index
        polygon.use_smooth = False
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    return obj


def make_blade(
    name: str,
    angle_degrees: float,
    titanium: bpy.types.Material,
) -> bpy.types.Object:
    blade = legacy.create_rounded_tapered_blade(
        name,
        inner_x=0.0192,
        outer_x=TIP_RADIUS,
        inner_depth=TARGET_BODY_DEPTH - 0.00092,
        outer_depth=0.00385,
        mat=titanium,
        outer_base_width=0.0209,
        outer_tip_width=0.00205,
        outer_shoulder=0.00175,
    )
    # The authored fold ridge adds 0.92 mm above the shell. Lower the shell by
    # half that amount so the complete raised blade remains inside the exact
    # 7.65 mm annotated body envelope.
    blade.location.z = -0.00046
    # The supplied front view has slightly broader shoulders than the old
    # 84 mm candidate.  Scale only the tangential direction before union.
    blade.scale.y = 1.045
    blade.rotation_euler.z = math.radians(angle_degrees)
    legacy.select_only([blade])
    bpy.context.view_layer.objects.active = blade
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return blade


def parent(obj: bpy.types.Object, owner: bpy.types.Object) -> bpy.types.Object:
    obj.parent = owner
    return obj


def create_facet_cap_body(
    name: str,
    z_center: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    body = legacy.create_cylinder(
        name,
        CAP_RADIUS,
        0.00387,
        z_center,
        material,
        FACET_SEGMENTS,
        bevel=0.00072,
        bevel_segments=2,
    )
    # Keep the 24-sided jewellery-cut band visible. Bevel faces remain smooth
    # enough to avoid razor edges, while the vertical panels stay planar.
    for polygon in body.data.polygons:
        polygon.use_smooth = False
    return body


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def create_studio(
    ground_material: bpy.types.Material,
) -> tuple[bpy.types.Object, bpy.types.Object, list[bpy.types.Object]]:
    bpy.ops.mesh.primitive_plane_add(size=0.52, location=(0.0, 0.0, -0.0092))
    ground = bpy.context.object
    ground.name = "StudioGround_RenderOnly"
    ground.data.materials.append(ground_material)

    bpy.ops.object.camera_add(location=(0.105, -0.135, 0.110))
    camera = bpy.context.object
    camera.name = "StudioCamera_RenderOnly"
    camera.data.lens = 72
    camera.data.sensor_width = 36
    look_at(camera, (0.0, 0.0, 0.0))
    bpy.context.scene.camera = camera

    specifications = [
        ("Key5000K", (0.085, -0.070, 0.130), 3.0, 0.115, 0.075, (1.0, 0.78, 0.62)),
        ("Rim3200K", (-0.095, 0.020, 0.078), 2.2, 0.085, 0.055, (1.0, 0.37, 0.15)),
        ("Fill6500K", (0.030, 0.130, 0.070), 1.15, 0.130, 0.080, (0.56, 0.72, 1.0)),
        ("TopStrip", (-0.025, -0.010, 0.170), 0.72, 0.150, 0.022, (0.86, 0.92, 1.0)),
    ]
    lights: list[bpy.types.Object] = []
    for suffix, location, energy, width, height, color in specifications:
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.name = f"Studio{suffix}_RenderOnly"
        light.data.energy = energy
        light.data.shape = "RECTANGLE"
        light.data.size = width
        light.data.size_y = height
        light.data.color = color
        look_at(light, (0.0, 0.0, 0.0))
        lights.append(light)
    return ground, camera, lights


def render_view(
    camera: bpy.types.Object,
    name: str,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
) -> None:
    camera.location = location
    camera.data.lens = lens
    look_at(camera, target)
    bpy.context.scene.render.filepath = str(PREVIEW_PATHS[name])
    bpy.ops.render.render(write_still=True)


def exact_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [
        obj.matrix_world @ vertex.co
        for obj in objects
        if obj.type == "MESH" and not obj.hide_render
        for vertex in obj.data.vertices
    ]
    return (
        Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))),
        Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points))),
    )


def mesh_audit(obj: bpy.types.Object) -> dict[str, int | float]:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    boundary_edges = sum(1 for edge in bm.edges if len(edge.link_faces) == 1)
    non_manifold_edges = sum(1 for edge in bm.edges if len(edge.link_faces) != 2)
    zero_area_faces = sum(1 for face in bm.faces if face.calc_area() <= 1.0e-12)
    result = {
        "vertices": len(bm.verts),
        "edges": len(bm.edges),
        "faces": len(bm.faces),
        "boundaryEdges": boundary_edges,
        "nonManifoldEdges": non_manifold_edges,
        "zeroAreaFaces": zero_area_faces,
    }
    bm.free()
    return result


def is_descendant(obj: bpy.types.Object, ancestor: bpy.types.Object) -> bool:
    owner = obj.parent
    while owner is not None:
        if owner == ancestor:
            return True
        owner = owner.parent
    return False


def scale_meshes_xy(objects: list[bpy.types.Object], factor: float) -> None:
    """Bake a uniform planar scale into independent mesh datablocks."""
    handled: set[int] = set()
    for obj in objects:
        pointer = obj.data.as_pointer()
        if pointer in handled:
            continue
        handled.add(pointer)
        for vertex in obj.data.vertices:
            vertex.co.x *= factor
            vertex.co.y *= factor
        obj.data.update(calc_edges=True)


def main() -> None:
    ensure_dirs()
    legacy.clear_scene()

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.world.use_nodes = True
    world_background = scene.world.node_tree.nodes.get("Background")
    world_background.inputs["Color"].default_value = (0.0049, 0.0059, 0.0078, 1.0)
    world_background.inputs["Strength"].default_value = 0.022
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.85

    blasted = machined_material(
        "M_CLI_BlastedTitanium",
        (0.260, 0.285, 0.305, 1.0),
        1.0,
        0.28,
        micro_strength=0.12,
        micro_scale=720.0,
    )
    blasted_dark = machined_material(
        "M_CLI_BlastedTitaniumDark",
        (0.105, 0.120, 0.138, 1.0),
        1.0,
        0.31,
        micro_strength=0.08,
        micro_scale=640.0,
    )
    polished = machined_material(
        "M_CLI_PolishedEdge",
        (0.390, 0.430, 0.465, 1.0),
        1.0,
        0.10,
        anisotropy=0.20,
    )
    brushed_a = machined_material(
        "M_CLI_RadialBrushedA",
        (0.105, 0.125, 0.145, 1.0),
        1.0,
        0.16,
        anisotropy=0.55,
        micro_strength=0.035,
        micro_scale=960.0,
    )
    brushed_b = machined_material(
        "M_CLI_RadialBrushedB",
        (0.020, 0.027, 0.036, 1.0),
        1.0,
        0.23,
        anisotropy=0.55,
        micro_strength=0.035,
        micro_scale=960.0,
    )
    recess = machined_material(
        "M_CLI_RecessedGunmetal",
        (0.002, 0.003, 0.005, 1.0),
        0.35,
        0.48,
        micro_strength=0.07,
        micro_scale=540.0,
    )
    bearing_steel = machined_material(
        "M_CLI_BearingSteel",
        (0.19, 0.21, 0.235, 1.0),
        1.0,
        0.16,
        anisotropy=0.18,
    )
    pom = machined_material(
        "M_CLI_BlackPOM",
        (0.006, 0.008, 0.011, 1.0),
        0.0,
        0.42,
    )
    ground_mat = machined_material(
        "M_CLI_StudioGraphite",
        (0.0002, 0.00025, 0.00035, 1.0),
        0.0,
        0.52,
        micro_strength=0.035,
        micro_scale=180.0,
    )

    root = legacy.empty("DragonScaleEDC_CLI_Root")
    rotor = legacy.empty("Rotor_Root", root)
    fixed = legacy.empty("Fixed_Root", root)
    bearing_root = legacy.empty("BearingAssembly_Root", root)
    cage_root = legacy.empty("BearingCage_Root", bearing_root)
    top_cap_root = legacy.empty("TopCap_Root", fixed)
    top_washer_root = legacy.empty("TopWasher_Root", fixed)
    bottom_washer_root = legacy.empty("BottomWasher_Root", fixed)
    bottom_cap_root = legacy.empty("BottomCap_Root", fixed)
    collision_root = legacy.empty("Collision_Root", root)

    rotor_body = legacy.create_ring(
        "RotorBody_OnePiece",
        outer_radius=0.02175,
        inner_radius=0.01135,
        depth=TARGET_BODY_DEPTH,
        z_center=0.0,
        mat=blasted,
        segments=PRIMARY_SEGMENTS,
        bevel=0.00078,
        bevel_segments=3,
    )
    rotor_body.parent = rotor
    blade_solids: list[bpy.types.Object] = []
    for index, angle in enumerate((90.0, 210.0, 330.0), start=1):
        blade = make_blade(f"BladeUnionTool_{index:02d}", angle, blasted)
        blade_solids.append(blade)
    # Blender 5.2's Exact Boolean opens this high-density ring/loft
    # intersection. Join the four individually watertight solids into one
    # mechanical mesh instead; their overlaps live under the cap and preserve
    # the reference silhouette without destructive solver artefacts.
    legacy.select_only([rotor_body] + blade_solids)
    bpy.context.view_layer.objects.active = rotor_body
    bpy.ops.object.join()
    rotor_body.data.name = "RotorBody_OnePiece_Mesh"
    legacy.shade_smooth_by_angle(rotor_body, 43.0)

    visual_objects: list[bpy.types.Object] = [rotor_body]

    # Three recessed scale fields sit inside the raised dragon-wing crowns.
    pocket_outline = [
        (0.0247, -0.00665),
        (0.0430, -0.00055),
        (0.0434, 0.0),
        (0.0430, 0.00055),
        (0.0247, 0.00665),
    ]
    inlay_outline = [
        (0.0254, -0.00575),
        (0.0417, 0.0),
        (0.0254, 0.00575),
    ]
    for index, angle in enumerate((90.0, 210.0, 330.0), start=1):
        floor = legacy.create_prism(
            f"BladePocketFloor_{index:02d}",
            pocket_outline,
            0.00018,
            0.00118,
            recess,
            bevel=0.00034,
        )
        floor.rotation_euler.z = math.radians(angle)
        floor.parent = rotor
        inlay = legacy.create_prism(
            f"BladePocketInlay_{index:02d}",
            inlay_outline,
            0.00012,
            0.00131,
            blasted_dark,
            bevel=0.00024,
        )
        inlay.rotation_euler.z = math.radians(angle)
        inlay.parent = rotor
        visual_objects.extend([floor, inlay])

    # 608-class bearing, POM washers, and fixed axle.
    bearing_outer = parent(
        legacy.create_ring(
            "BearingOuterRace",
            BEARING_OD * 0.5,
            0.00910,
            BEARING_WIDTH,
            0.0,
            bearing_steel,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00022,
            bevel_segments=2,
        ),
        bearing_root,
    )
    bearing_inner = parent(
        legacy.create_ring(
            "BearingInnerRace",
            0.00605,
            BEARING_ID * 0.5,
            BEARING_WIDTH,
            0.0,
            bearing_steel,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00020,
            bevel_segments=2,
        ),
        bearing_root,
    )
    top_shield = parent(
        legacy.create_ring(
            "BearingShield_Top",
            0.01075,
            0.00620,
            0.00028,
            0.00344,
            recess,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00008,
            bevel_segments=1,
        ),
        bearing_root,
    )
    bottom_shield = parent(
        legacy.create_ring(
            "BearingShield_Bottom",
            0.01075,
            0.00620,
            0.00028,
            -0.00344,
            recess,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00008,
            bevel_segments=1,
        ),
        bearing_root,
    )
    axle = parent(
        legacy.create_cylinder(
            "Axle",
            0.00390,
            0.0146,
            0.0,
            bearing_steel,
            SECONDARY_SEGMENTS,
            bevel=0.00024,
            bevel_segments=2,
        ),
        fixed,
    )
    visual_objects.extend([bearing_outer, bearing_inner, top_shield, bottom_shield, axle])

    for index in range(10):
        angle = math.tau * index / 10
        ball = legacy.create_uv_sphere(
            f"BearingBall_{index + 1:02d}",
            0.00144,
            (0.00755 * math.cos(angle), 0.00755 * math.sin(angle), 0.0),
            bearing_steel,
        )
        ball.parent = cage_root
        visual_objects.append(ball)

    top_washer = parent(
        legacy.create_ring(
            "TopWasher",
            0.01115,
            0.00410,
            0.00068,
            0.00402,
            pom,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00013,
            bevel_segments=2,
        ),
        top_washer_root,
    )
    bottom_washer = parent(
        legacy.create_ring(
            "BottomWasher",
            0.01115,
            0.00410,
            0.00068,
            -0.00402,
            pom,
            segments=SECONDARY_SEGMENTS,
            bevel=0.00013,
            bevel_segments=2,
        ),
        bottom_washer_root,
    )
    visual_objects.extend([top_washer, bottom_washer])

    cap_center = (0.00822 + 0.00435) * 0.5
    top_cap = parent(
        create_facet_cap_body("FingerCap_Top", cap_center, blasted),
        top_cap_root,
    )
    bottom_cap = parent(
        create_facet_cap_body("FingerCap_Bottom", -cap_center, blasted),
        bottom_cap_root,
    )
    top_face = parent(
        create_radial_crown(
            "FingerCapTop_RadialFace",
            radius=0.02145,
            depth=0.00026,
            face_z=TARGET_ASSEMBLED_DEPTH * 0.5 - 0.00018,
            facing=1.0,
            materials=(brushed_a, brushed_b, polished),
        ),
        top_cap_root,
    )
    bottom_face = parent(
        create_radial_crown(
            "FingerCapBottom_RadialFace",
            radius=0.02145,
            depth=0.00026,
            face_z=-TARGET_ASSEMBLED_DEPTH * 0.5 + 0.00018,
            facing=-1.0,
            materials=(brushed_a, brushed_b, polished),
        ),
        bottom_cap_root,
    )
    visual_objects.extend(
        [
            top_cap,
            bottom_cap,
            top_face,
            bottom_face,
        ]
    )

    remaining_axis_rings = sorted(
        obj.name
        for obj in visual_objects
        if obj.name in FORBIDDEN_DECORATIVE_AXIS_RINGS
    )
    if remaining_axis_rings:
        raise RuntimeError(
            "Rejected decorative axis rings remain: "
            + ", ".join(remaining_axis_rings)
        )

    # Low-complexity interaction collision exchange asset.
    collision_outline = [
        (0.0187, -0.0204),
        (0.0285, -0.0187),
        (0.0420, -0.0092),
        (TIP_RADIUS, 0.0),
        (0.0420, 0.0092),
        (0.0285, 0.0187),
        (0.0187, 0.0204),
    ]
    collision_objects: list[bpy.types.Object] = []
    for index, angle in enumerate((90.0, 210.0, 330.0), start=1):
        collision = legacy.create_prism(
            f"COL_DragonBlade_{index:02d}",
            collision_outline,
            TARGET_BODY_DEPTH,
            0.0,
            None,
            bevel=0.00020,
        )
        collision.rotation_euler.z = math.radians(angle)
        collision.parent = collision_root
        collision.hide_render = True
        collision.display_type = "WIRE"
        collision_objects.append(collision)
    col_hub = parent(
        legacy.create_cylinder(
            "COL_Hub",
            0.0253,
            TARGET_BODY_DEPTH,
            0.0,
            pom,
            24,
        ),
        collision_root,
    )
    col_hub.hide_render = True
    col_hub.display_type = "WIRE"
    collision_objects.append(col_hub)

    rotor_meshes = [
        obj for obj in visual_objects
        if obj.type == "MESH" and is_descendant(obj, rotor)
    ]
    rotor_min, rotor_max = exact_bounds(rotor_meshes)
    rotor_width = max(rotor_max.x - rotor_min.x, rotor_max.y - rotor_min.y)
    planar_normalization = TARGET_WIDTH / rotor_width
    scale_meshes_xy(rotor_meshes + collision_objects, planar_normalization)

    root["reference_width_mm"] = 85.0
    root["reference_cap_ratio"] = 0.52
    root["reference_body_depth_ratio"] = 0.09
    root["reference_total_depth_ratio"] = 0.20
    root["blade_angles_degrees"] = "90,210,330"
    root["initial_angular_velocity"] = 0.0
    root["units"] = "metres"
    root["spin_axis_blender"] = "+Z"
    root["spin_axis_unity"] = "+Y"
    root["candidate_status"] = "visual approval pending; not shipping integrated"

    export_visual_objects = [obj for obj in visual_objects if obj.type == "MESH"]
    legacy.clean_export_meshes(export_visual_objects + collision_objects)
    for obj in [
        rotor_body,
        bearing_outer,
        bearing_inner,
        top_shield,
        bottom_shield,
        axle,
        top_washer,
        bottom_washer,
        top_cap,
        bottom_cap,
        top_face,
        bottom_face,
    ]:
        legacy.shade_smooth_by_angle(obj, 42.0)
        legacy.apply_weighted_normals(obj)

    ground, camera, lights = create_studio(ground_mat)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    render_view(camera, "top", (0.0, -0.0008, 0.235), (0.0, 0.0, 0.0), 68)
    render_view(camera, "hero", (0.102, -0.130, 0.105), (0.0, 0.0, 0.0), 72)
    render_view(camera, "left_oblique", (-0.112, -0.128, 0.082), (0.0, 0.0, 0.0), 74)
    render_view(camera, "right_oblique", (0.112, -0.128, 0.082), (0.0, 0.0, 0.0), 74)
    render_view(camera, "low", (0.102, -0.148, 0.025), (0.0, 0.0, 0.0), 78)
    render_view(camera, "side", (0.0, -0.220, 0.0010), (0.0, 0.0, 0.0), 84)

    # Axial exploded order taken directly from the annotated reference.
    top_cap_root.location.z = 0.043
    top_washer_root.location.z = 0.024
    bearing_root.location.z = 0.010
    bottom_washer_root.location.z = -0.016
    bottom_cap_root.location.z = -0.036
    render_view(camera, "exploded", (0.150, -0.205, 0.118), (0.0, 0.0, 0.002), 74)
    for component in (
        top_cap_root,
        top_washer_root,
        bearing_root,
        bottom_washer_root,
        bottom_cap_root,
    ):
        component.location.z = 0.0

    legacy.select_only(
        [
            root,
            rotor,
            fixed,
            bearing_root,
            cage_root,
            top_cap_root,
            top_washer_root,
            bottom_washer_root,
            bottom_cap_root,
        ]
        + visual_objects
    )
    bpy.ops.export_scene.fbx(
        filepath=str(FBX_PATH),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
    )
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_animations=False,
    )
    legacy.select_only([collision_root] + collision_objects)
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION_FBX_PATH),
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
    )

    bounds_min, bounds_max = exact_bounds(export_visual_objects)
    extents = bounds_max - bounds_min
    planar_width = max(extents.x, extents.y)
    actual_depth = extents.z
    triangle_count = sum(
        max(1, len(polygon.vertices) - 2)
        for obj in export_visual_objects
        for polygon in obj.data.polygons
    )
    stats = {
        "status": "candidate_visual_approval_pending_not_integrated",
        "source": str(BLEND_PATH.relative_to(REPO_ROOT)),
        "fbx": str(FBX_PATH.relative_to(REPO_ROOT)),
        "glb": str(GLB_PATH.relative_to(REPO_ROOT)),
        "collisionFbx": str(COLLISION_FBX_PATH.relative_to(REPO_ROOT)),
        "previews": {
            key: str(value.relative_to(REPO_ROOT))
            for key, value in PREVIEW_PATHS.items()
        },
        "referenceBasis": {
            "overallWidthMm": TARGET_WIDTH * 1000.0,
            "capDiameterMm": TARGET_CAP_DIAMETER * 1000.0,
            "bodyDepthMm": TARGET_BODY_DEPTH * 1000.0,
            "assembledDepthMm": TARGET_ASSEMBLED_DEPTH * 1000.0,
            "bladeAnglesDegrees": [90.0, 210.0, 330.0],
            "bearingStandardMm": [22.0, 8.0, 7.0],
        },
        "measured": {
            "overallWidthMm": planar_width * 1000.0,
            "assembledDepthMm": actual_depth * 1000.0,
            "capDiameterMm": max(top_cap.dimensions.x, top_cap.dimensions.y) * 1000.0,
            "rotorBodyDepthMm": rotor_body.dimensions.z * 1000.0,
            "bearingOuterDiameterMm": max(bearing_outer.dimensions.x, bearing_outer.dimensions.y) * 1000.0,
            "widthErrorMm": (planar_width - TARGET_WIDTH) * 1000.0,
            "depthErrorMm": (actual_depth - TARGET_ASSEMBLED_DEPTH) * 1000.0,
            "meshCount": len(export_visual_objects),
            "triangleCount": triangle_count,
            "rotorAudit": mesh_audit(rotor_body),
            "rotorPlanarNormalization": planar_normalization,
        },
        "materials": {
            "body": {"metallic": 1.0, "roughness": 0.28, "microNormal": 0.12},
            "cap": {"metallic": 1.0, "roughness": 0.19, "anisotropy": 0.55},
            "polishedEdge": {"metallic": 1.0, "roughness": 0.10},
            "pom": {"metallic": 0.0, "roughness": 0.42, "ior": 1.48},
        },
        "decorativeAxisRingCount": len(remaining_axis_rings),
        "forbiddenDecorativeAxisRings": list(FORBIDDEN_DECORATIVE_AXIS_RINGS),
        "initialAngularVelocity": 0.0,
    }
    STATS_PATH.write_text(json.dumps(stats, indent=2), encoding="utf-8")

    ground.hide_viewport = True
    for light in lights:
        light.hide_viewport = True
    legacy.select_only([root])
    bpy.context.view_layer.objects.active = root
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    print("DRAGON_SCALE_CLI_EXPORT " + json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    main()
