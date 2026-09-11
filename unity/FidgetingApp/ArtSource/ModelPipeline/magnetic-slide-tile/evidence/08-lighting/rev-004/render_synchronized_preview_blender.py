#!/usr/bin/env python3
"""Render Blender frames for the Gate 08 rev 4 synchronized preview."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "supplemental-preview" / "blender"
FRAME_COUNT = 180
SOURCE_FPS = 15
TRAVEL_MM = 18.076433
TARGET = Vector((0.0, -2.0, 5.0))
BASE_CAMERA = Vector((74.0, -116.0, 72.0))
CLAY_RANGE = range(135, 150)
ROTATING_OBJECTS = ("RotatingCarrier", "MovingTop")
FIXED_OBJECTS = ("MagneticSlideTile_G05_R006", "BottomExterior", "FixedAxisBoss")


def frame_state(frame: int) -> dict:
    if frame <= 22:
        return {
            "state": "closed-hero",
            "mode": "hold",
            "yaw": 0.0,
            "angle": 0.0,
            "travel": 0.0,
        }
    if frame <= 74:
        phase = (frame - 23) / (74 - 23)
        return {
            "state": "closed-camera-orbit",
            "mode": "camera-orbit",
            "yaw": 35.0 * math.sin(phase * math.tau),
            "angle": 0.0,
            "travel": 0.0,
        }
    if frame <= 89:
        return {
            "state": "detent-12",
            "mode": "top-z-rotation",
            "yaw": 0.0,
            "angle": 12.0,
            "travel": 0.0,
        }
    if frame <= 104:
        return {
            "state": "detent-36",
            "mode": "top-z-rotation",
            "yaw": 0.0,
            "angle": 36.0,
            "travel": 0.0,
        }
    if frame <= 119:
        return {
            "state": "max-open",
            "mode": "top-slide",
            "yaw": 0.0,
            "angle": 0.0,
            "travel": TRAVEL_MM,
        }
    if frame <= 134:
        return {
            "state": "combined-legal",
            "mode": "top-slide-and-z-rotation",
            "yaw": 0.0,
            "angle": 12.0,
            "travel": TRAVEL_MM * 0.5,
        }
    if frame <= 149:
        return {
            "state": "clay",
            "mode": "diagnostic",
            "yaw": 0.0,
            "angle": 0.0,
            "travel": 0.0,
        }
    return {
        "state": "end-closed",
        "mode": "hold",
        "yaw": 0.0,
        "angle": 0.0,
        "travel": 0.0,
    }


def look_at(camera, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def set_pose(state: dict) -> None:
    angle = math.radians(state["angle"])
    for name in ROTATING_OBJECTS:
        bpy.data.objects[name].rotation_euler = (0.0, 0.0, angle)
    bpy.data.objects["TopLocalSlide"].location = (0.0, -state["travel"], 0.0)


def set_camera(camera, yaw_degrees: float) -> None:
    offset = BASE_CAMERA - TARGET
    angle = math.radians(yaw_degrees)
    camera.location = TARGET + Vector(
        (
            math.cos(angle) * offset.x - math.sin(angle) * offset.y,
            math.sin(angle) * offset.x + math.cos(angle) * offset.y,
            offset.z,
        )
    )
    look_at(camera, TARGET)


def validate_frame(camera, state: dict) -> dict:
    tolerance = 1e-5
    for name in FIXED_OBJECTS:
        rotation = bpy.data.objects[name].matrix_world.to_euler()
        if abs(rotation.x) > tolerance or abs(rotation.y) > tolerance:
            raise RuntimeError(f"{name} pitch/roll changed.")
    expected = math.radians(state["angle"])
    for name in ROTATING_OBJECTS:
        rotation = bpy.data.objects[name].rotation_euler
        if (
            abs(rotation.x) > tolerance
            or abs(rotation.y) > tolerance
            or abs(rotation.z - expected) > tolerance
        ):
            raise RuntimeError(f"{name} left its +Z-only rotation contract.")
    slide = bpy.data.objects["TopLocalSlide"]
    if (
        abs(slide.location.x) > tolerance
        or abs(slide.location.z) > tolerance
        or not -TRAVEL_MM - tolerance <= slide.location.y <= tolerance
    ):
        raise RuntimeError("TopLocalSlide left its approved local groove axis.")
    for obj in bpy.data.objects:
        if min(obj.scale) <= 0.0 or obj.matrix_world.to_3x3().determinant() <= 0.0:
            raise RuntimeError(f"{obj.name} has a negative scale or inversion.")
    offset = camera.location - TARGET
    right = camera.matrix_world.to_quaternion() @ Vector((1.0, 0.0, 0.0))
    up = camera.matrix_world.to_quaternion() @ Vector((0.0, 1.0, 0.0))
    elevation = math.degrees(
        math.atan2(offset.z, math.hypot(offset.x, offset.y))
    )
    base_offset = BASE_CAMERA - TARGET
    base_elevation = math.degrees(
        math.atan2(
            base_offset.z,
            math.hypot(base_offset.x, base_offset.y),
        )
    )
    if (
        abs(elevation - base_elevation) > tolerance
        or abs(right.z) > tolerance
        or up.z <= 0.0
    ):
        raise RuntimeError("Camera roll/elevation invariant failed.")
    return {
        "fixedPitchRollZero": True,
        "topPitchRollZero": True,
        "topYawDegrees": state["angle"],
        "travelMm": state["travel"],
        "positiveScale": True,
        "cameraRollDegrees": 0.0,
        "cameraElevationDegrees": elevation,
    }


def main() -> None:
    scene = bpy.context.scene
    if scene.get("lighting_revision") != 4:
        raise RuntimeError("Expected the Gate 08 rev 4 Blender candidate.")
    camera = bpy.data.objects["M08R4_Hero"]
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.image_settings.exr_codec = "ZIP"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Raw"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame_filter = os.environ.get("PREVIEW_FRAME_RANGE")
    selected = set(range(FRAME_COUNT))
    if frame_filter:
        start, end = (int(value) for value in frame_filter.split(":", 1))
        selected = set(range(start, end + 1))

    frames = []
    for frame in range(FRAME_COUNT):
        state = frame_state(frame)
        frames.append({"frame": frame, "time": frame / SOURCE_FPS, **state})
        set_pose(state)
        set_camera(camera, state["yaw"])
        frames[-1]["validation"] = validate_frame(camera, state)
        if frame in CLAY_RANGE or frame not in selected:
            continue
        scene.render.filepath = str(OUTPUT / f"frame-{frame:04d}-linear.exr")
        bpy.ops.render.render(write_still=True)

    (OUTPUT.parent / "blender-frame-metadata.json").write_text(
        json.dumps(
            {
                "engine": "Blender 5.2 Eevee",
                "frameCount": FRAME_COUNT,
                "sourceFps": SOURCE_FPS,
                "resolution": [1400, 1100],
                "cameraTargetMm": list(TARGET),
                "baseCameraMm": list(BASE_CAMERA),
                "frames": frames,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
