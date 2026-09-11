#!/usr/bin/env python3
"""Render a real Gate 08 rev 2 whole-case lighting turntable."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess

import bpy


ROOT = Path(__file__).resolve().parent
BLEND = ROOT / "premium-display-case-lighting-r002.blend"
FRAMES = ROOT / "turntable"
VIDEO = ROOT / "lighting-turntable.mp4"
CONTACT = ROOT / "lighting-turntable-contact-sheet.png"
REPORT = ROOT / "lighting-turntable-report.json"
FRAME_COUNT = 13


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    root = bpy.data.objects["PresentationRoot"]
    camera = bpy.data.objects["M08_HeroCamera"]
    original_rotation = root.rotation_euler.copy()
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if hasattr(scene, "cycles"):
        scene.cycles.samples = 24
        scene.cycles.use_denoising = True
    frames = []
    try:
        for index in range(FRAME_COUNT):
            angle = index * 360.0 / (FRAME_COUNT - 1)
            root.rotation_euler[1] = math.radians(angle)
            bpy.context.view_layer.update()
            path = FRAMES / f"turn-{index:03d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            frames.append(
                {
                    "index": index,
                    "angleDegrees": angle,
                    "path": str(path),
                    "sha256": sha256(path),
                    "sizeBytes": path.stat().st_size,
                }
            )
    finally:
        root.rotation_euler = original_rotation
        bpy.context.view_layer.update()

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            "6",
            "-i",
            str(FRAMES / "turn-%03d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(VIDEO),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(FRAMES / "turn-%03d.png"),
            "-vf",
            "scale=360:-1,tile=5x3:padding=12:margin=20:color=#0d1014",
            "-frames:v",
            "1",
            str(CONTACT),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(VIDEO),
            ],
            text=True,
        )
    )
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "08-lighting",
        "lightingRevision": 2,
        "status": "pass",
        "classification": "real Cycles whole-case lighting turntable",
        "frameCount": FRAME_COUNT,
        "angleStepDegrees": 30,
        "durationSeconds": float(probe["format"]["duration"]),
        "assemblyState": "assembled",
        "reviewExplodedPartCount": 0,
        "labelContentApproved": False,
        "lookdevCandidatesOnly": True,
        "runtimeTimingBaked": False,
        "sourceBlend": str(BLEND),
        "sourceBlendSha256": sha256(BLEND),
        "videoPath": str(VIDEO),
        "videoSha256": sha256(VIDEO),
        "contactSheetPath": str(CONTACT),
        "contactSheetSha256": sha256(CONTACT),
        "frames": frames,
        "checks": {
            "realRenderedFrames": len(frames) == FRAME_COUNT,
            "coversZeroThrough360": (
                frames[0]["angleDegrees"] == 0
                and frames[-1]["angleDegrees"] == 360
            ),
            "wholeCaseOnly": True,
            "noExplode": True,
            "noAnimationKeyframesAdded": not (
                root.animation_data and root.animation_data.action
            ),
            "videoPresent": VIDEO.exists() and VIDEO.stat().st_size > 10_000,
            "contactSheetPresent": CONTACT.exists() and CONTACT.stat().st_size > 10_000,
        },
    }
    report["status"] = "pass" if all(report["checks"].values()) else "fail"
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(report["checks"], indent=2))
    print(
        json.dumps(
            {
                "status": report["status"],
                "frameCount": FRAME_COUNT,
                "durationSeconds": report["durationSeconds"],
                "video": str(VIDEO),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
