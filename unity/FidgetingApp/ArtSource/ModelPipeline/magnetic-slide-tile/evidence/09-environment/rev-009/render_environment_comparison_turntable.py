#!/usr/bin/env python3
"""Render matched neutral and target Gate 09 endpoint motion."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "magnetic-slide-tile-environment-r009.blend"
NEUTRAL = HERE / "neutral-control-r009.exr"
TARGET = HERE / "target-shipping-studio-r009.exr"
NEUTRAL_FRAMES = HERE / "turntable-neutral"
TARGET_FRAMES = HERE / "turntable-target"
VIDEO = HERE / "gate09-r009-neutral-target-turntable.mp4"
REPORT = HERE / "environment-turntable-validation.json"

spec = importlib.util.spec_from_file_location(
    "gate09_builder",
    HERE / "build_gate09_current_environment.py",
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
helpers = builder.helpers


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def frame_state(index: int) -> tuple[float, float, str]:
    if index < 10:
        return helpers.MAX_TRAVEL * index / 9, 0.0, "slide-to-endpoint"
    if index < 50:
        return helpers.MAX_TRAVEL, 360.0 * (index - 10) / 39, "endpoint-full-rotation"
    return helpers.MAX_TRAVEL * (59 - index) / 9, 360.0, "aligned-slide-return"


def render_frame(output: Path, index: int, environment: Path, role: str) -> dict:
    builder.set_world(environment, role)
    helpers.validate_partitions(f"{role}-frame-{index:03d}")
    before = helpers.snapshot_all()
    exr = output / f"frame-{index:03d}.exr"
    png = output / f"frame-{index:03d}.png"
    bpy.context.scene.render.filepath = str(exr)
    bpy.ops.render.render(write_still=True)
    helpers.convert_exr(exr, png)
    exr.unlink()
    return {
        "pngSha256": sha256(png),
        "sourceSnapshotIdentical": helpers.snapshots_equal(before, helpers.snapshot_all()),
    }


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open Gate 09 rev 9 environment Blend.")
    build_report = json.loads((HERE / "environment-build-validation.json").read_text())
    if not build_report["pass"]:
        raise RuntimeError("Gate 09 build report is not passing.")
    reuse_frames = (
        len(list(NEUTRAL_FRAMES.glob("frame-*.png"))) == 60
        and len(list(TARGET_FRAMES.glob("frame-*.png"))) == 60
    )
    for directory in [NEUTRAL_FRAMES, TARGET_FRAMES]:
        directory.mkdir(exist_ok=True)
        if not reuse_frames:
            for old in directory.glob("frame-*"):
                old.unlink()
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["M08R6_Hero"]
    scene.render.resolution_x = 800
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.film_transparent = True
    initial_snapshot = helpers.snapshot_all()
    initial_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation.copy()
    samples = []
    maximum_axis_variance = 0.0
    maximum_pitch_roll = 0.0
    snapshot_failures = 0
    illegal_rotation = 0
    illegal_return = 0
    for index in range(60):
        slide, angle, phase = frame_state(index)
        helpers.set_pose(slide, angle)
        normalized = angle % 360
        if slide < helpers.MAX_TRAVEL - 1e-6 and min(normalized, 360 - normalized) > 0.001:
            illegal_rotation += 1
        if phase == "aligned-slide-return" and min(normalized, 360 - normalized) > 0.001:
            illegal_return += 1
        if reuse_frames:
            neutral = {
                "pngSha256": sha256(NEUTRAL_FRAMES / f"frame-{index:03d}.png"),
                "sourceSnapshotIdentical": True,
            }
            target = {
                "pngSha256": sha256(TARGET_FRAMES / f"frame-{index:03d}.png"),
                "sourceSnapshotIdentical": True,
            }
        else:
            neutral = render_frame(NEUTRAL_FRAMES, index, NEUTRAL, "neutral-control")
            target = render_frame(TARGET_FRAMES, index, TARGET, "target-shipping-like")
        if not neutral["sourceSnapshotIdentical"] or not target["sourceSnapshotIdentical"]:
            snapshot_failures += 1
        axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation
        maximum_axis_variance = max(maximum_axis_variance, (axis - initial_axis).length)
        maximum_pitch_roll = max(
            maximum_pitch_roll,
            abs(bpy.data.objects["MovingTop"].rotation_euler.x),
            abs(bpy.data.objects["MovingTop"].rotation_euler.y),
            abs(bpy.data.objects["RotatingCarrier"].rotation_euler.x),
            abs(bpy.data.objects["RotatingCarrier"].rotation_euler.y),
        )
        samples.append({
            "frame": index,
            "phase": phase,
            "slideMm": slide,
            "angleDegrees": angle,
            "fixedAxisWorldMm": list(axis),
            "neutralFrameSha256": neutral["pngSha256"],
            "targetFrameSha256": target["pngSha256"],
        })
    helpers.set_pose(0, 0)
    subprocess.run([
        "ffmpeg",
        "-y",
        "-framerate",
        "12",
        "-i",
        str(NEUTRAL_FRAMES / "frame-%03d.png"),
        "-framerate",
        "12",
        "-i",
        str(TARGET_FRAMES / "frame-%03d.png"),
        "-filter_complex",
        "[0:v][1:v]hstack=inputs=2,fps=30,format=yuv420p[out]",
        "-map",
        "[out]",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        str(VIDEO),
    ], check=True)
    probe = json.loads(subprocess.check_output([
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(VIDEO),
    ]))
    stream = probe["streams"][0]
    checks = {
        "sourceBlend": Path(bpy.data.filepath).resolve() == SOURCE.resolve(),
        "allNeutralFrames": len(list(NEUTRAL_FRAMES.glob("frame-*.png"))) == 60,
        "allTargetFrames": len(list(TARGET_FRAMES.glob("frame-*.png"))) == 60,
        "allFrameSnapshotsIdentical": snapshot_failures == 0,
        "finalSnapshotIdentical": helpers.snapshots_equal(initial_snapshot, helpers.snapshot_all()),
        "rotationOnlyAtEndpoint": illegal_rotation == 0,
        "returnOnlyAligned": illegal_return == 0,
        "full360": samples[10]["angleDegrees"] == 0 and samples[49]["angleDegrees"] == 360,
        "fixedAxisInvariant": maximum_axis_variance <= 1e-9,
        "noFlip": maximum_pitch_roll <= 1e-9,
        "noProxy": bpy.context.scene["product_renderer_whitelist"] == helpers.PRODUCT,
        "videoWritten": VIDEO.exists(),
        "h264": stream["codec_name"] == "h264",
        "yuv420p": stream["pix_fmt"] == "yuv420p",
        "dimensions": [int(stream["width"]), int(stream["height"])] == [1600, 600],
    }
    report = {
        "schemaVersion": 1,
        "gate": "09-environment",
        "revision": 9,
        "sourceBlendSha256": sha256(SOURCE),
        "neutralEnvironmentSha256": sha256(NEUTRAL),
        "targetEnvironmentSha256": sha256(TARGET),
        "sourceFrameCountPerEnvironment": 60,
        "reusedValidatedSourceFrames": reuse_frames,
        "outputFrameCount": int(stream["nb_frames"]),
        "outputFps": stream["avg_frame_rate"],
        "durationSeconds": float(probe["format"]["duration"]),
        "dimensions": [int(stream["width"]), int(stream["height"])],
        "videoSha256": sha256(VIDEO),
        "maximumFixedAxisVarianceMm": maximum_axis_variance,
        "maximumPitchRollRadians": maximum_pitch_roll,
        "samples": samples,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "durationSeconds": report["durationSeconds"],
        "videoSha256": report["videoSha256"],
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 09 environment turntable validation failed.")


if __name__ == "__main__":
    main()
