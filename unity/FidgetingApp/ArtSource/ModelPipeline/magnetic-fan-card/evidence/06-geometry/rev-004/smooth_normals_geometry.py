"""Apply smooth side/bevel normals while preserving hard planar caps."""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
SOURCE_BLEND = (
    HERE.parent / "rev-003/fan-card-72-segment-geometry.blend")
OUTPUT_BLEND = HERE / "fan-card-72-smooth-normal-geometry.blend"
VISUAL_TOKENS = ("GunmetalFrame", "GoldTrim", "WarmSilverFace")


def vertex_hash(objects: list[bpy.types.Object]) -> str:
    digest = hashlib.sha256()
    for obj in sorted(objects, key=lambda item: item.name):
        digest.update(obj.name.encode("utf-8"))
        for vertex in obj.data.vertices:
            digest.update(struct.pack(
                "<fff",
                vertex.co.x,
                vertex.co.y,
                vertex.co.z,
            ))
    return digest.hexdigest()


def aim(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat(
        "-Z", "Y").to_euler()


def visual_meshes() -> list[bpy.types.Object]:
    return [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and any(token in obj.name for token in VISUAL_TOKENS)
    ]


def configure_closeup(output: Path) -> None:
    scene = bpy.context.scene
    root = bpy.data.objects["TopCard"]
    center_local = Vector((-0.02225, -0.03495, 0.0035))
    corner_local = center_local + Vector((0.03175, 0.04445, 0.0))
    target = root.matrix_world @ corner_local
    camera_data = bpy.data.cameras.new("CAM_NormalCloseup")
    camera_data.lens = 108.0
    camera_data.sensor_width = 36.0
    camera_data.clip_start = 0.001
    camera_data.clip_end = 10.0
    camera = bpy.data.objects.new("CAM_NormalCloseup", camera_data)
    scene.collection.objects.link(camera)
    camera.location = target + Vector((0.034, -0.043, 0.024))
    aim(camera, target)
    scene.camera = camera
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "rim.sl"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.012, 0.014, 0.018)
    scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    meshes = visual_meshes()
    before_hash = vertex_hash(meshes)
    configure_closeup(HERE / "normal-before.png")

    smooth_counts = {}
    for obj in meshes:
        smooth = 0
        flat = 0
        for polygon in obj.data.polygons:
            side_or_bevel = abs(polygon.normal.z) < 0.92
            polygon.use_smooth = side_or_bevel
            if side_or_bevel:
                smooth += 1
            else:
                flat += 1
        obj.data.update()
        smooth_counts[obj.name] = {
            "smoothSideOrBevelPolygons": smooth,
            "hardCapPolygons": flat,
        }
    bpy.context.view_layer.update()
    after_hash = vertex_hash(meshes)
    configure_closeup(HERE / "normal-after.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    report = {
        "modelId": "magnetic-fan-card",
        "visibleCornerSegmentsPerQuadrant": 72,
        "vertexPositionHashBefore": before_hash,
        "vertexPositionHashAfter": after_hash,
        "vertexPositionsChanged": before_hash != after_hash,
        "normalPolicy": {
            "sideAndBevel": "smooth",
            "planarCaps": "hard",
            "export": "FBX split normals"
        },
        "objects": smooth_counts,
        "pass": before_hash == after_hash
            and all(
                item["smoothSideOrBevelPolygons"] > 0
                and item["hardCapPolygons"] > 0
                for item in smooth_counts.values()
            ),
    }
    (HERE / "smooth-normal-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
