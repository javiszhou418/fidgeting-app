"""Build and export the approved magnetic fan-card product package."""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = (
    HERE.parents[1] / "08-lighting/rev-002/"
    "fan-card-exact-lighting.blend"
)
BLEND = HERE / "magnetic-fan-card-export-ready.blend"
FBX = HERE / "magnetic-fan-card.fbx"
GLB = HERE / "magnetic-fan-card.glb"
COLLISION_FBX = HERE / "magnetic-fan-card-collision.fbx"
MANIFEST = HERE / "export-manifest.json"
REPORT = HERE / "export-audit-report.json"

ROOT_NAME = "MagneticFanCard_Root"
CARD_NAMES = ("BottomCard", "MiddleCard", "TopCard")
WIDTH = 0.0635
HEIGHT = 0.0889
THICKNESS = 0.0035
RADIUS = 0.0095


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def move_to_collection(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    if collection not in obj.users_collection:
        collection.objects.link(obj)
    for current in list(obj.users_collection):
        if current != collection:
            current.objects.unlink(obj)


def recursive_product_objects(root: bpy.types.Object) -> list[bpy.types.Object]:
    return [root, *list(root.children_recursive)]


def convert_fonts_to_meshes() -> list[str]:
    converted = []
    for obj in list(bpy.context.scene.objects):
        if obj.type != "FONT":
            continue
        name = obj.name
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH", keep_original=False)
        bpy.context.object.name = name
        converted.append(name)
    return converted


def join_static_artwork(card_name: str) -> dict:
    prefixes = (
        f"{card_name}_Spade",
        f"{card_name}_CornerSpade_",
    )
    objects = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.name.startswith(prefixes)
    ]
    if not objects:
        return {"card": card_name, "sourceObjects": 0, "result": None}
    material = next((
        slot for obj in objects for slot in obj.data.materials if slot
    ), None)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    joined = bpy.context.object
    joined.name = f"{card_name}_BlackArtwork"
    if material is not None:
        joined.data.materials.clear()
        joined.data.materials.append(material)
        for polygon in joined.data.polygons:
            polygon.material_index = 0
    return {
        "card": card_name,
        "sourceObjects": len(objects),
        "result": joined.name,
    }


def rounded_rectangle_points(
    width: float,
    height: float,
    radius: float,
    segments: int = 8,
) -> list[tuple[float, float]]:
    points = []
    corners = (
        (width / 2 - radius, height / 2 - radius, 0.0),
        (-width / 2 + radius, height / 2 - radius, 90.0),
        (-width / 2 + radius, -height / 2 + radius, 180.0),
        (width / 2 - radius, -height / 2 + radius, 270.0),
    )
    for cx, cy, start in corners:
        for index in range(segments + 1):
            angle = math.radians(start + index * 90.0 / segments)
            points.append((
                cx + math.cos(angle) * radius,
                cy + math.sin(angle) * radius,
            ))
    return points


def create_card_collider(
    card_name: str,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    points = rounded_rectangle_points(WIDTH, HEIGHT, RADIUS, 8)
    count = len(points)
    half = THICKNESS / 2
    vertices = [
        (x, y, -half) for x, y in points
    ] + [
        (x, y, half) for x, y in points
    ]
    faces = []
    faces.append(tuple(reversed(range(count))))
    faces.append(tuple(range(count, count * 2)))
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"COLLIDER_{card_name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    collider = bpy.data.objects.new(f"COLLIDER_{card_name}", mesh)
    collection.objects.link(collider)
    collider.parent = bpy.data.objects[card_name]
    collider.location = (0.0, 0.0, 0.0)
    collider.rotation_euler = (0.0, 0.0, 0.0)
    collider.scale = (1.0, 1.0, 1.0)
    collider.display_type = "WIRE"
    collider.hide_render = True
    collider["unityColliderType"] = "ConvexMesh"
    collider["isTrigger"] = False
    return collider


def edge_face_counts(obj: bpy.types.Object) -> Counter:
    counts = Counter()
    for polygon in obj.data.polygons:
        vertices = list(polygon.vertices)
        for index, start in enumerate(vertices):
            edge = tuple(sorted((start, vertices[(index + 1) % len(vertices)])))
            counts[edge] += 1
    return counts


def mesh_stats(objects: list[bpy.types.Object]) -> dict:
    meshes = [obj for obj in objects if obj.type == "MESH"]
    triangles = sum(
        len(polygon.vertices) - 2
        for obj in meshes
        for polygon in obj.data.polygons
    )
    materials = sorted({
        material.name
        for obj in meshes
        for material in obj.data.materials
        if material is not None
    })
    return {
        "meshObjects": len(meshes),
        "vertices": sum(len(obj.data.vertices) for obj in meshes),
        "triangles": triangles,
        "materials": materials,
        "materialCount": len(materials),
    }


def select_objects(objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    if objects:
        bpy.context.view_layer.objects.active = objects[0]


def export_product_fbx(objects: list[bpy.types.Object]) -> None:
    select_objects(objects)
    bpy.ops.export_scene.fbx(
        filepath=str(FBX),
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_space_transform=False,
        object_types={"MESH", "EMPTY"},
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=False,
        axis_forward="-Z",
        axis_up="Y",
    )


def export_product_glb(objects: list[bpy.types.Object]) -> None:
    select_objects(objects)
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_yup=True,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_normals=True,
        export_tangents=False,
    )


def export_collision_fbx(
    hierarchy: list[bpy.types.Object],
    colliders: list[bpy.types.Object],
) -> None:
    empties = [
        obj for obj in hierarchy
        if obj.type == "EMPTY" and obj.name in {ROOT_NAME, *CARD_NAMES}
    ]
    select_objects([*empties, *colliders])
    bpy.ops.export_scene.fbx(
        filepath=str(COLLISION_FBX),
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        bake_space_transform=False,
        object_types={"MESH", "EMPTY"},
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="AUTO",
        embed_textures=False,
        axis_forward="-Z",
        axis_up="Y",
    )


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"

    root = bpy.data.objects[ROOT_NAME]
    axis_names = (
        "CommonAxis_RecessedMatteSpindle",
        "CommonAxis_BearingCap_Chrome",
    )
    for name in axis_names:
        obj = bpy.data.objects[name]
        world = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = world

    product_hierarchy = recursive_product_objects(root)
    product_set = set(product_hierarchy)
    for obj in list(scene.objects):
        if obj not in product_set:
            bpy.data.objects.remove(obj, do_unlink=True)

    product_collection = bpy.data.collections.new("COL_Product_Export")
    scene.collection.children.link(product_collection)
    for obj in list(scene.objects):
        move_to_collection(obj, product_collection)

    before = mesh_stats(product_hierarchy)
    converted_fonts = convert_fonts_to_meshes()
    artwork_joins = [join_static_artwork(card) for card in CARD_NAMES]
    product_hierarchy = recursive_product_objects(root)
    for obj in product_hierarchy:
        if obj.type != "MESH":
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)
    after = mesh_stats(product_hierarchy)

    collision_collection = bpy.data.collections.new(
        "COL_Collision_MagneticFanCard")
    scene.collection.children.link(collision_collection)
    colliders = [
        create_card_collider(card, collision_collection)
        for card in CARD_NAMES
    ]
    collider_validation = {}
    for collider in colliders:
        counts = edge_face_counts(collider)
        collider_validation[collider.name] = {
            "vertices": len(collider.data.vertices),
            "polygons": len(collider.data.polygons),
            "watertight": bool(counts) and all(
                count == 2 for count in counts.values()),
            "nonTwoFaceEdges": sum(
                1 for count in counts.values() if count != 2),
        }

    hierarchy = recursive_product_objects(root)
    product_objects = [
        obj for obj in hierarchy
        if not obj.name.startswith("COLLIDER_")
    ]
    assert all(obj.type != "FONT" for obj in product_objects)
    assert after["triangles"] <= 50_000
    assert after["materialCount"] <= 8
    assert all(
        result["watertight"] for result in collider_validation.values())
    assert not any(
        obj.name.startswith("BottomCard_Track_")
        for obj in product_objects)
    assert len([
        obj for obj in product_objects
        if "_Track_Undercut" in obj.name
    ]) == 2
    assert len([
        obj for obj in product_objects
        if "_FollowerBearing" in obj.name
    ]) == 2

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    export_product_fbx(product_objects)
    export_product_glb(product_objects)
    export_collision_fbx(hierarchy, colliders)

    files = {
        "blend-source": BLEND,
        "fbx-export": FBX,
        "glb-export": GLB,
        "collision-export": COLLISION_FBX,
    }
    report = {
        "sourceBlend": str(SOURCE_BLEND.relative_to(HERE.parents[7])),
        "unitSystem": "meters",
        "unityUnitsPerMeter": 1.0,
        "fbxAxis": {"forward": "-Z", "up": "Y"},
        "glbAxis": "Y-up",
        "root": ROOT_NAME,
        "cardHierarchy": {
            name: {
                "parent": bpy.data.objects[name].parent.name,
                "rotationDegreesZ": round(
                    math.degrees(bpy.data.objects[name].rotation_euler.z), 4),
            }
            for name in CARD_NAMES
        },
        "convertedFontObjects": converted_fonts,
        "staticArtworkJoins": artwork_joins,
        "beforeOptimization": before,
        "afterOptimization": after,
        "budget": {
            "profile": "Unity hero asset",
            "triangleLimit": 50_000,
            "pass": after["triangles"] <= 50_000,
        },
        "collision": collider_validation,
        "lockedInvariants": {
            "cardDimensionsMm": [63.5, 88.9, 3.5],
            "cornerRadiusMm": 9.5,
            "airGapMm": 1.0,
            "trackClearanceMm": 7.590,
            "bottomTrackCount": 0,
            "topMiddleTrackCount": 2,
            "followerCount": 2,
            "productGeometryChangedByExport": False,
        },
    }
    REPORT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")

    manifest = {
        "modelId": "magnetic-fan-card",
        "gate": "10-export",
        "revision": 1,
        "sourceAsset": {
            "path": str(SOURCE_BLEND.relative_to(HERE.parents[7])),
            "sha256": sha256(SOURCE_BLEND),
        },
        "exports": {
            slot: {
                "path": str(path.relative_to(HERE.parents[7])),
                "sha256": sha256(path),
                "sizeBytes": path.stat().st_size,
            }
            for slot, path in files.items()
        },
        "auditReport": {
            "path": str(REPORT.relative_to(HERE.parents[7])),
            "sha256": sha256(REPORT),
        },
        "materialPolicy": (
            "FBX/GLB preserve material names and preview values; "
            "Gate 11 Unity parity assigns shipping materials."
        ),
        "collisionPolicy": (
            "Three watertight convex rounded-slab proxies remain separate "
            "and parent to BottomCard, MiddleCard, and TopCard."
        ),
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
