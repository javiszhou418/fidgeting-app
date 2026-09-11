"""Run inside Blender to render fixed orthographic and perspective views without saving the .blend."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import bpy
from mathutils import Matrix, Vector


def arguments() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    return parser.parse_args(values)


EXCLUDED_NAME_TOKENS = ("renderonly", "studio", "ground", "floor", "backdrop", "cyclorama")


def capture_objects(objects):
    visible = [obj for obj in objects if obj.type == "MESH" and not obj.hide_render]
    filtered = [
        obj for obj in visible
        if not obj.get("model_pipeline_exclude", False)
        and not any(
            obj.name.lower() == token
            or obj.name.lower().startswith(token)
            or obj.name.lower().endswith(token)
            for token in EXCLUDED_NAME_TOKENS
        )
    ]
    return filtered or visible


def world_bounds(objects):
    corners = []
    for obj in objects:
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not corners:
        raise RuntimeError("No visible mesh objects were found.")
    minimum = Vector((min(point.x for point in corners), min(point.y for point in corners), min(point.z for point in corners)))
    maximum = Vector((max(point.x for point in corners), max(point.y for point in corners), max(point.z for point in corners)))
    return minimum, maximum


def look_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def orient_camera(camera, target, world_up):
    backward = (camera.location - target).normalized()
    if abs(backward.dot(world_up)) > 0.999:
        world_up = Vector((0, 0, 1)) if abs(backward.z) < 0.999 else Vector((0, 1, 0))
    right = world_up.cross(backward).normalized()
    up = backward.cross(right).normalized()
    rotation = Matrix((right, up, backward)).transposed().to_4x4()
    camera.matrix_world = Matrix.Translation(camera.location) @ rotation


def main():
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    model_objects = capture_objects(bpy.context.scene.objects)
    minimum, maximum = world_bounds(model_objects)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    radius = max(size.length * 0.5, 0.001)
    camera_data = bpy.data.cameras.new("PipelineCaptureCamera")
    camera = bpy.data.objects.new("PipelineCaptureCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    scene = bpy.context.scene
    scene.camera = camera
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except (TypeError, ValueError):
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("PipelineCaptureWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.035, 0.04, 0.05, 1.0)
        background.inputs["Strength"].default_value = 0.18
    for existing_light in [obj for obj in scene.objects if obj.type == "LIGHT"]:
        existing_light.hide_render = True
    energy_scale = max(1.0, (radius / 5.0) ** 2)
    for name, energy, size_factor, offset in [
        ("PipelineKey", 900, 3.0, (2.2, 2.8, 3.4)),
        ("PipelineFill", 450, 2.5, (-2.8, 0.8, 1.8)),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy * energy_scale
        data.shape = "DISK"
        data.size = radius * size_factor
        light = bpy.data.objects.new(name, data)
        light.location = center + Vector(offset) * radius
        scene.collection.objects.link(light)
        look_at(light, center)
    if scene.get("model_pipeline_up_axis") == "Y" and scene.get("model_pipeline_front_axis") == "+Z":
        views = {
            "front": ((0, 0, 1), True), "back": ((0, 0, -1), True), "top": ((0, 1, 0), True),
            "bottom": ((0, -1, 0), True), "left": ((-1, 0, 0), True), "right": ((1, 0, 0), True),
            "hero": ((1.25, 0.8, 1.6), False), "left-oblique": ((-1.35, 0.6, 1.6), False),
            "right-oblique": ((1.35, 0.6, 1.6), False), "low": ((1.0, -0.18, 1.5), False),
        }
        axis_contract = "X-width/Y-height/Z-front"
        camera_world_up = Vector((0, 1, 0))
    else:
        views = {
            "front": ((0, -1, 0), True), "back": ((0, 1, 0), True), "top": ((0, 0, 1), True),
            "bottom": ((0, 0, -1), True), "left": ((-1, 0, 0), True), "right": ((1, 0, 0), True),
            "hero": ((1.25, -1.6, 1.15), False), "left-oblique": ((-1.35, -1.6, 0.8), False),
            "right-oblique": ((1.35, -1.6, 0.8), False), "low": ((1.0, -1.5, 0.18), False),
        }
        axis_contract = "Blender-default-Z-up/front-negative-Y"
        camera_world_up = Vector((0, 0, 1))
    report = {
        "run_id": args.run_id,
        "bounds": {"min": list(minimum), "max": list(maximum)},
        "included_objects": [obj.name for obj in model_objects],
        "excluded_visible_meshes": [obj.name for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.hide_render and obj not in model_objects],
        "axis_contract": axis_contract,
        "views": [],
    }
    for view_id, (direction_values, orthographic) in views.items():
        direction = Vector(direction_values).normalized()
        camera.location = center + direction * radius * 3.4
        orient_camera(camera, center, camera_world_up)
        camera.data.type = "ORTHO" if orthographic else "PERSP"
        camera.data.ortho_scale = radius * 2.35
        camera.data.lens = 58
        camera.data.clip_end = max(1000.0, radius * 10.0)
        output = args.output / f"{view_id}.png"
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        report["views"].append({"id": view_id, "path": str(output), "camera_location": list(camera.location), "camera_rotation_radians": list(camera.rotation_euler), "projection": "orthographic" if orthographic else "perspective", "lens_mm": camera.data.lens, "ortho_scale": camera.data.ortho_scale})
    (args.output / "capture-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
