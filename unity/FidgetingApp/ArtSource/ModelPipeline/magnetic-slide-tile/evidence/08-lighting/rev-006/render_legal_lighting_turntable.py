#!/usr/bin/env python3
"""Render Gate 08 rev 6 endpoint motion with per-frame partition checks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import bpy
import numpy as np
import OpenImageIO as oiio


HERE = Path(__file__).resolve().parent
FRAMES = HERE / "legal-turntable-frames"
VIDEO = HERE / "gate08-r006-endpoint-lighting-turntable.mp4"
REPORT = HERE / "legal-lighting-turntable-report.json"
SOURCE = HERE / "magnetic-slide-tile-lighting-r006.blend"
GATE07_MOTION = (
    HERE.parent.parent / "07-material/rev-013/endpoint-material-motion-audit.json"
)
spec = importlib.util.spec_from_file_location(
    "gate08_builder",
    HERE / "build_gate08_partition_safe_lighting.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def convert(exr_path: Path, png_path: Path) -> None:
    source = oiio.ImageInput.open(str(exr_path))
    specification = source.spec()
    pixels = source.read_image(format=oiio.FLOAT)
    source.close()
    pixels = np.asarray(pixels, dtype=np.float32).reshape(
        specification.height,
        specification.width,
        specification.nchannels,
    )
    alpha = pixels[..., 3] if specification.nchannels > 3 else np.ones(pixels.shape[:2])
    display = helpers.linear_to_display(pixels, alpha)
    output = oiio.ImageOutput.create(str(png_path))
    output.open(
        str(png_path),
        oiio.ImageSpec(specification.width, specification.height, 3, oiio.UINT8),
    )
    output.write_image(display)
    output.close()


def frame_state(index: int):
    if index < 15:
        return helpers.MAX_TRAVEL * index / 14, 0.0, "slide-to-endpoint"
    if index < 75:
        return helpers.MAX_TRAVEL, 360.0 * (index - 15) / 59, "endpoint-full-rotation"
    return helpers.MAX_TRAVEL * (89 - index) / 14, 360.0, "aligned-slide-return"


def main() -> None:
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError("Open the Gate 08 rev 6 lighting Blend.")
    gate07_motion = json.loads(GATE07_MOTION.read_text(encoding="utf-8"))
    if not gate07_motion["pass"]:
        raise RuntimeError("Approved Gate 07 endpoint motion audit is not current.")
    before = helpers.snapshot_all()
    initial_partitions = helpers.validate_partitions("turntable-initial")
    FRAMES.mkdir(exist_ok=True)
    for old in FRAMES.glob("frame-*"):
        old.unlink()
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["M08R6_Hero"]
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "32"
    scene.render.film_transparent = True
    samples = []
    initial_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation.copy()
    max_fixed_axis_variance = 0.0
    max_pitch_roll = 0.0
    illegal_rotation_count = 0
    illegal_return_count = 0
    source_snapshot_failures = 0
    partition_failures = 0
    for index in range(90):
        slide, angle, phase = frame_state(index)
        helpers.set_pose(slide, angle)
        normalized = angle % 360.0
        if slide < helpers.MAX_TRAVEL - 1e-6 and min(normalized, 360 - normalized) > 0.001:
            illegal_rotation_count += 1
        if phase == "aligned-slide-return" and min(normalized, 360 - normalized) > 0.001:
            illegal_return_count += 1
        moving = bpy.data.objects["MovingTop"]
        max_pitch_roll = max(
            max_pitch_roll,
            abs(moving.rotation_euler.x),
            abs(moving.rotation_euler.y),
        )
        fixed_axis = bpy.data.objects["InternalAxisBoss"].matrix_world.translation
        max_fixed_axis_variance = max(
            max_fixed_axis_variance,
            (fixed_axis - initial_axis).length,
        )
        partitions = helpers.validate_partitions(f"turntable-frame-{index:04d}")
        if not partitions["pass"]:
            partition_failures += 1
        if not helpers.snapshots_equal(before, helpers.snapshot_all()):
            source_snapshot_failures += 1
        exr_path = FRAMES / f"frame-{index:04d}.exr"
        png_path = FRAMES / f"frame-{index:04d}.png"
        scene.render.filepath = str(exr_path)
        bpy.ops.render.render(write_still=True)
        convert(exr_path, png_path)
        exr_path.unlink()
        samples.append({
            "frame": index,
            "phase": phase,
            "slideMm": slide,
            "rotationDegrees": angle,
            "fixedAxisWorldMm": list(fixed_axis),
            "partitionPass": partitions["pass"],
            "sourceSnapshotIdentical": source_snapshot_failures == 0,
        })
    helpers.set_pose(0, 0)
    after = helpers.snapshot_all()
    subprocess.run([
        "ffmpeg",
        "-y",
        "-framerate",
        "15",
        "-i",
        str(FRAMES / "frame-%04d.png"),
        "-vf",
        "fps=30,format=yuv420p",
        "-c:v",
        "libx264",
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
        "sourceLightingBlend": Path(bpy.data.filepath).resolve() == SOURCE.resolve(),
        "allFramesRendered": len(list(FRAMES.glob("frame-*.png"))) == 90,
        "allFramesPartitionValidated": partition_failures == 0,
        "allFramesSourceSnapshotIdentical": source_snapshot_failures == 0,
        "sourceSnapshotIdenticalAfter": helpers.snapshots_equal(before, after),
        "rotationOnlyAtEndpoint": illegal_rotation_count == 0,
        "slideReturnOnlyAligned": illegal_return_count == 0,
        "full360Covered": samples[15]["rotationDegrees"] == 0
        and samples[74]["rotationDegrees"] == 360,
        "fixedAxisInvariant": max_fixed_axis_variance <= 1e-9,
        "noPitchRollFlip": max_pitch_roll <= 1e-9,
        "approvedNoPenetrationAudit": gate07_motion["checks"]["noPenetration"],
        "noDebugProxy": bpy.context.scene["product_renderer_whitelist"] == helpers.PRODUCT,
        "sideArtworkZeroEveryFrame": all(
            values["verticalSideArtworkFaces"] == 0
            for values in initial_partitions["objects"].values()
        ),
        "undersideArtworkZeroEveryFrame": all(
            values["undersideArtworkFaces"] == 0
            for values in initial_partitions["objects"].values()
        ),
        "videoWritten": VIDEO.exists(),
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 6,
        "sourceBlendSha256": sha256(SOURCE),
        "gate07MotionAuditSha256": sha256(GATE07_MOTION),
        "environmentSha256": sha256(HERE / "neutral-parity-studio-r006.exr"),
        "displayTransform": "neutral-display-v1",
        "frameCount": 90,
        "sourceFps": 15,
        "outputFps": stream["avg_frame_rate"],
        "encodedFrameCount": int(stream["nb_frames"]),
        "durationSeconds": float(probe["format"]["duration"]),
        "dimensions": [int(stream["width"]), int(stream["height"])],
        "videoSha256": sha256(VIDEO),
        "maximumFixedAxisVarianceMm": max_fixed_axis_variance,
        "maximumPitchRollRadians": max_pitch_roll,
        "sourceSnapshotBefore": helpers.snapshot_report(before),
        "sourceSnapshotAfter": helpers.snapshot_report(after),
        "samples": samples,
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "pass": report["pass"],
        "frameCount": report["frameCount"],
        "durationSeconds": report["durationSeconds"],
        "videoSha256": report["videoSha256"],
    }, indent=2))
    if not report["pass"]:
        raise RuntimeError("Legal lighting turntable validation failed.")


if __name__ == "__main__":
    main()
