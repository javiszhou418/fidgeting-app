#!/usr/bin/env python3
"""Render six clear orthographic Workbench views for Gate 06."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


OUTPUT = Path(__file__).resolve().parent
SOURCE = OUTPUT / "premium-display-case-geometry-r003.blend"
SUBJECT_NAMES = {
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
}
VIEWS = {
    "front": (0, 0, 1),
    "back": (0, 0, -1),
    "top": (0, 1, 0),
    "bottom": (0, -1, 0),
    "left": (-1, 0, 0),
    "right": (1, 0, 0),
}


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    corners = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    return (
        Vector(tuple(min(point[index] for point in corners) for index in range(3))),
        Vector(tuple(max(point[index] for point in corners) for index in range(3))),
    )


def orient(camera: bpy.types.Object, target: Vector, view_id: str) -> None:
    backward = (camera.location - target).normalized()
    world_up = Vector((0, 0, 1)) if view_id in ("top", "bottom") else Vector((0, 1, 0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    subjects = [bpy.data.objects[name] for name in SUBJECT_NAMES]
    for obj in scene.objects:
        if obj.type == "MESH":
            obj.hide_render = obj.name not in SUBJECT_NAMES
    minimum, maximum = bounds(subjects)
    center = (minimum + maximum) * 0.5
    radius = max((maximum - minimum).length * 0.5, 0.001)
    data = bpy.data.cameras.new("Gate06Rev3OrthoCamera")
    camera = bpy.data.objects.new("Gate06Rev3OrthoCamera", data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    data.type = "ORTHO"
    data.ortho_scale = radius * 2.35
    data.clip_end = max(1000.0, radius * 10.0)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.72, 0.74, 0.78)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.display.shading.background_type = "WORLD"
    scene.display.shading.background_color = (0.025, 0.03, 0.04)
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    records = []
    for view_id, direction_values in VIEWS.items():
        direction = Vector(direction_values).normalized()
        camera.location = center + direction * radius * 3.4
        orient(camera, center, view_id)
        target = OUTPUT / f"ortho-{view_id}.png"
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        records.append(
            {
                "id": view_id,
                "path": str(target.relative_to(REPO_ROOT)),
                "projection": "orthographic",
                "renderEngine": "BLENDER_WORKBENCH",
            }
        )
    (OUTPUT / "orthographic-workbench-report.json").write_text(
        json.dumps({"status": "pass", "views": records}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "pass", "viewCount": len(records)}))


if __name__ == "__main__":
    main()
