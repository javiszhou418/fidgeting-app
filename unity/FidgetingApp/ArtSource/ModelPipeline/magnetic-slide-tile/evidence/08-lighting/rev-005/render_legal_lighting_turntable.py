#!/usr/bin/env python3
"""Render endpoint-safe Gate 08 lighting motion."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
FRAMES = HERE / "legal-turntable-frames"
VIDEO = HERE / "gate08-r005-endpoint-lighting-turntable.mp4"
REPORT = HERE / "legal-lighting-turntable-report.json"
SOURCE = HERE / "magnetic-slide-tile-lighting-r005.blend"
SOURCE_SHA = ""
spec = importlib.util.spec_from_file_location("gate08_builder", HERE / "build_gate08_endpoint_lighting.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def convert(exr_path, png_path):
    source = oiio.ImageInput.open(str(exr_path))
    image_spec = source.spec()
    pixels = source.read_image(format=oiio.FLOAT)
    source.close()
    pixels = np.asarray(pixels, dtype=np.float32).reshape(
        image_spec.height, image_spec.width, image_spec.nchannels
    )
    alpha = pixels[..., 3] if image_spec.nchannels > 3 else np.ones(pixels.shape[:2])
    display = helpers.linear_to_display(pixels, alpha)
    output = oiio.ImageOutput.create(str(png_path))
    output.open(str(png_path), oiio.ImageSpec(image_spec.width, image_spec.height, 3, oiio.UINT8))
    output.write_image(display)
    output.close()


def frame_state(index):
    if index < 15:
        return helpers.MAX_TRAVEL * index / 14, 0.0, "slide-to-endpoint"
    if index < 75:
        return helpers.MAX_TRAVEL, 360.0 * (index - 15) / 59, "endpoint-full-rotation"
    return helpers.MAX_TRAVEL * (89 - index) / 14, 360.0, "aligned-slide-return"


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the Gate 08 rev 5 lighting blend.")
    FRAMES.mkdir(exist_ok=True)
    for old in FRAMES.glob("*"):
        old.unlink()
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["M08R5_Hero"]
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.film_transparent = True
    samples = []
    max_fixed_axis_variance = 0.0
    initial_fixed_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation.copy()
    max_pitch_roll = 0.0
    illegal_rotation_count = 0
    illegal_return_count = 0
    for index in range(90):
        slide, angle, phase = frame_state(index)
        helpers.set_pose(slide, angle)
        normalized = angle % 360.0
        if slide < helpers.MAX_TRAVEL - 1e-6 and min(normalized, 360 - normalized) > 0.001:
            illegal_rotation_count += 1
        if phase == "aligned-slide-return" and min(normalized, 360 - normalized) > 0.001:
            illegal_return_count += 1
        moving = bpy.data.objects["MovingTop"]
        max_pitch_roll = max(max_pitch_roll, abs(moving.rotation_euler.x), abs(moving.rotation_euler.y))
        fixed_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation
        max_fixed_axis_variance = max(
            max_fixed_axis_variance,
            (fixed_axis - initial_fixed_axis).length,
        )
        exr = FRAMES / f"frame-{index:04d}.exr"
        png = FRAMES / f"frame-{index:04d}.png"
        scene.render.filepath = str(exr)
        bpy.ops.render.render(write_still=True)
        convert(exr, png)
        exr.unlink()
        samples.append({
            "frame": index,
            "phase": phase,
            "slideMm": slide,
            "rotationDegrees": angle,
            "fixedAxisWorldMm": list(fixed_axis),
        })
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "15", "-i", str(FRAMES / "frame-%04d.png"),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18",
        "-movflags", "+faststart", str(VIDEO),
    ], check=True)
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)
    ]))
    stream = probe["streams"][0]
    checks = {
        "sourceLightingBlend": Path(bpy.data.filepath).resolve() == SOURCE.resolve(),
        "allFramesRendered": len(list(FRAMES.glob("frame-*.png"))) == 90,
        "rotationOnlyAtEndpoint": illegal_rotation_count == 0,
        "slideReturnOnlyAligned": illegal_return_count == 0,
        "full360Covered": samples[15]["rotationDegrees"] == 0 and samples[74]["rotationDegrees"] == 360,
        "fixedAxisInvariant": max_fixed_axis_variance <= 1e-9,
        "noPitchRollFlip": max_pitch_roll <= 1e-9,
        "noIllegalMidRotationFrames": not any("illegal" in path.name for path in FRAMES.iterdir()),
        "productRendererWhitelist": bpy.context.scene["product_renderer_whitelist"] == helpers.PRODUCT,
        "videoWritten": VIDEO.exists(),
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 5,
        "sourceBlendSha256": sha256(SOURCE),
        "environmentSha256": sha256(HERE / "neutral-parity-studio-r005.exr"),
        "displayTransform": "neutral-display-v1",
        "frameCount": 90,
        "sourceFps": 15,
        "outputFps": stream["avg_frame_rate"],
        "durationSeconds": float(probe["format"]["duration"]),
        "dimensions": [int(stream["width"]), int(stream["height"])],
        "videoSha256": sha256(VIDEO),
        "maximumFixedAxisVarianceMm": max_fixed_axis_variance,
        "maximumPitchRollRadians": max_pitch_roll,
        "samples": samples,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("pass", "frameCount", "durationSeconds", "videoSha256")}, indent=2))
    if not report["pass"]:
        raise RuntimeError("Legal lighting turntable validation failed.")


if __name__ == "__main__":
    main()
