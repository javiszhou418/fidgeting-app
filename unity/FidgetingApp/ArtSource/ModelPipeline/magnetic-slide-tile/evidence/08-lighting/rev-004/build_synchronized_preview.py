#!/usr/bin/env python3
"""Build and validate the Gate 08 rev 4 synchronized comparison video."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
SOURCE = HERE / "supplemental-preview"
BLENDER = SOURCE / "blender"
UNITY = SOURCE / "unity"
VIDEO = HERE / "gate08-r004-synchronized-portable-parity.mp4"
POSTER = HERE / "gate08-r004-synchronized-portable-parity-poster.png"
REPORT = HERE / "gate08-r004-synchronized-preview-report.json"
FRAME_COUNT = 180
SOURCE_FPS = 15
OUTPUT_FPS = 30
PANEL_WIDTH = 1400
PANEL_HEIGHT = 1100
LABEL_HEIGHT = 80
OUTPUT_SIZE = (PANEL_WIDTH * 2, PANEL_HEIGHT + LABEL_HEIGHT)
BACKGROUND = np.array([0.035, 0.035, 0.035], dtype=np.float32)
SHOULDER = 0.18
FONT_PATH = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT = ImageFont.truetype(FONT_PATH, 28)
FONT_SMALL = ImageFont.truetype(FONT_PATH, 22)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_from_exr(path: Path) -> tuple[np.ndarray, np.ndarray]:
    rgba = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if rgba is None or rgba.shape != (PANEL_HEIGHT, PANEL_WIDTH, 4):
        raise RuntimeError(f"Invalid preview EXR: {path}")
    rgba = rgba[:, :, [2, 1, 0, 3]].astype(np.float32)
    alpha = np.clip(rgba[:, :, 3], 0.0, 1.0)
    linear = rgba[:, :, :3] * alpha[:, :, None]
    linear += BACKGROUND[None, None, :] * (1.0 - alpha[:, :, None])
    compressed = np.maximum(linear, 0.0) / (
        1.0 + np.maximum(linear, 0.0) * SHOULDER
    )
    srgb = np.where(
        compressed <= 0.0031308,
        compressed * 12.92,
        1.055 * np.power(compressed, 1.0 / 2.4) - 0.055,
    )
    return np.round(np.clip(srgb, 0.0, 1.0) * 255).astype(np.uint8), alpha


def clay_pair() -> tuple[np.ndarray, np.ndarray]:
    blender = np.array(Image.open(HERE / "blender-clay-display.png").convert("RGB"))
    unity = np.array(Image.open(HERE / "unity-clay-display.png").convert("RGB"))
    return blender, unity


def mask_stats(left: np.ndarray, right: np.ndarray) -> dict:
    left_mask = left > 0.5
    right_mask = right > 0.5
    intersection = np.logical_and(left_mask, right_mask).sum()
    union = np.logical_or(left_mask, right_mask).sum()
    left_points = np.argwhere(left_mask)
    right_points = np.argwhere(right_mask)
    left_centroid = left_points.mean(axis=0)
    right_centroid = right_points.mean(axis=0)
    return {
        "iou": float(intersection / union),
        "centroidDeltaPixels": float(np.linalg.norm(left_centroid - right_centroid)),
        "leftCentroidY": float(left_centroid[0]),
        "rightCentroidY": float(right_centroid[0]),
    }


def state_label(state: dict) -> str:
    travel_mm = state["travelMeters"] * 1000.0
    motion = {
        "camera-orbit": "相机环绕（物体固定）",
        "top-z-rotation": "顶片 +Z 旋转（相机固定）",
        "top-slide": "顶片沿槽平移（底座固定）",
        "top-slide-and-z-rotation": "顶片平移 + +Z 旋转（底座固定）",
        "diagnostic": "Clay 对照（物体固定）",
        "hold": "固定姿态",
    }[state["mode"]]
    return (
        f"{motion}  |  {state['state']}  |  camera yaw {state['yaw']:.1f} deg  |  "
        f"top +Z {state['angle']:.0f} deg  |  travel {travel_mm:.2f} mm"
    )


def compose(
    left: np.ndarray,
    right: np.ndarray,
    state: dict,
    frame: int,
) -> np.ndarray:
    canvas = Image.new("RGB", OUTPUT_SIZE, (24, 24, 24))
    canvas.paste(Image.fromarray(left), (0, LABEL_HEIGHT))
    canvas.paste(Image.fromarray(right), (PANEL_WIDTH, LABEL_HEIGHT))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 10), "Blender 5.2 Eevee", font=FONT, fill=(244, 244, 244))
    draw.text(
        (PANEL_WIDTH + 24, 10),
        "Unity 6000.5 URP",
        font=FONT,
        fill=(244, 244, 244),
    )
    metadata = (
        f"{state_label(state)}  |  t={frame / SOURCE_FPS:05.2f}s  "
        f"|  source frame {frame:03d}/{FRAME_COUNT - 1:03d}"
    )
    draw.text((24, 46), metadata, font=FONT_SMALL, fill=(200, 200, 200))
    draw.line(
        (PANEL_WIDTH, 0, PANEL_WIDTH, OUTPUT_SIZE[1]),
        fill=(86, 86, 86),
        width=2,
    )
    return np.asarray(canvas)


def probe_video() -> dict:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=codec_name,profile,width,height,r_frame_rate,"
        "avg_frame_rate,pix_fmt,nb_frames",
        "-of",
        "json",
        str(VIDEO),
    ]
    return json.loads(subprocess.check_output(command, text=True))


def main() -> None:
    blender_metadata = json.loads(
        (SOURCE / "blender-frame-metadata.json").read_text(encoding="utf-8")
    )
    unity_metadata = json.loads(
        (SOURCE / "unity-frame-metadata.json").read_text(encoding="utf-8")
    )
    if blender_metadata["frameCount"] != FRAME_COUNT:
        raise RuntimeError("Blender frame count drift.")
    if unity_metadata["frameCount"] != FRAME_COUNT:
        raise RuntimeError("Unity frame count drift.")

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}",
        "-r",
        str(SOURCE_FPS),
        "-i",
        "-",
        "-an",
        "-vf",
        f"fps={OUTPUT_FPS},format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-profile:v",
        "high",
        "-movflags",
        "+faststart",
        str(VIDEO),
    ]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)
    alignments = []
    clay_left, clay_right = clay_pair()
    poster_frame = None
    for frame in range(FRAME_COUNT):
        blender_state = blender_metadata["frames"][frame]
        unity_state = unity_metadata["frames"][frame]
        if (
            blender_state["state"] != unity_state["state"]
            or blender_state["mode"] != unity_state["mode"]
            or abs(blender_state["yaw"] - unity_state["yaw"]) > 0.001
            or abs(blender_state["angle"] - unity_state["angle"]) > 0.001
            or abs(blender_state["travel"] / 1000.0 - unity_state["travelMeters"])
            > 0.000001
        ):
            raise RuntimeError(f"Pose metadata mismatch at frame {frame}.")
        for metadata in (blender_state, unity_state):
            validation = metadata.get("validation")
            if (
                not validation
                or not validation["fixedPitchRollZero"]
                or not validation["topPitchRollZero"]
                or not validation["positiveScale"]
                or abs(validation["cameraRollDegrees"]) > 0.0001
            ):
                raise RuntimeError(f"Transform validation failed at frame {frame}.")
        if blender_state["state"] == "clay":
            left, right = clay_left, clay_right
        else:
            left, left_alpha = display_from_exr(
                BLENDER / f"frame-{frame:04d}-linear.exr"
            )
            right, right_alpha = display_from_exr(
                UNITY / f"frame-{frame:04d}-linear.exr"
            )
            alignments.append({"frame": frame, **mask_stats(left_alpha, right_alpha)})
        paired = compose(left, right, unity_state, frame)
        if frame == 50:
            poster_frame = paired
        encoder.stdin.write(paired.tobytes())
    encoder.stdin.close()
    if encoder.wait() != 0:
        raise RuntimeError("ffmpeg failed to encode the synchronized preview.")
    Image.fromarray(poster_frame).save(POSTER)

    probe = probe_video()
    stream = probe["streams"][0]
    duration = float(probe["format"]["duration"])
    minimum_iou = min(item["iou"] for item in alignments)
    maximum_centroid = max(item["centroidDeltaPixels"] for item in alignments)
    centroid_y = [
        value
        for item in alignments
        for value in (item["leftCentroidY"], item["rightCentroidY"])
    ]
    if stream["codec_name"] != "h264":
        raise RuntimeError("Preview codec is not H.264.")
    if (stream["width"], stream["height"]) != OUTPUT_SIZE:
        raise RuntimeError("Preview dimensions drift.")
    if stream["avg_frame_rate"] != "30/1" or not 11.9 <= duration <= 12.1:
        raise RuntimeError("Preview timing drift.")
    if minimum_iou < 0.985 or maximum_centroid > 3.0:
        raise RuntimeError(
            "Blender/Unity frame alignment failed: "
            f"minimum IoU={minimum_iou:.6f}, "
            f"maximum centroid delta={maximum_centroid:.6f}px."
        )
    if min(centroid_y) < 200.0 or max(centroid_y) > 900.0:
        raise RuntimeError("Image orientation check detected a vertical flip.")

    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 4,
        "status": "supplemental-recording-ready-not-approved",
        "video": {
            "path": str(VIDEO.relative_to(REPO)),
            "sha256": sha256(VIDEO),
            "durationSeconds": duration,
            "codec": stream["codec_name"],
            "profile": stream["profile"],
            "pixelFormat": stream["pix_fmt"],
            "dimensions": [stream["width"], stream["height"]],
            "fps": stream["avg_frame_rate"],
            "frameCount": int(stream["nb_frames"]),
            "fastStart": True,
        },
        "recipe": {
            "sourceFps": SOURCE_FPS,
            "outputFps": OUTPUT_FPS,
            "sourceResolutionPerEngine": [PANEL_WIDTH, PANEL_HEIGHT],
            "perEngineCrop": False,
            "perEngineScale": False,
            "displayTransform": "neutral-display-v1",
            "transition": "hard cuts and holds only",
            "segments": [
                ["closed-hero", 0, 22],
                ["closed-camera-orbit", 23, 74],
                ["detent-12", 75, 89],
                ["detent-36", 90, 104],
                ["max-open", 105, 119],
                ["combined-legal", 120, 134],
                ["clay", 135, 149],
                ["end-closed", 150, 179],
            ],
        },
        "sourceHashes": {
            "blenderCandidate": sha256(
                HERE / "magnetic-slide-tile-lighting-r004-neutral-parity.blend"
            ),
            "unityCandidate": sha256(
                REPO
                / "unity/FidgetingApp/Assets/_EDC/Candidates/"
                "MagneticSlideTileGate08R004NeutralParity/Scenes/"
                "MagneticSlideTileNeutralParityR004.unity"
            ),
            "sharedEnvironment": sha256(HERE / "neutral-parity-studio-r004.exr"),
            "displayTransform": sha256(HERE / "apply_shared_display.py"),
            "blenderRenderer": sha256(HERE / "render_synchronized_preview_blender.py"),
            "unityRenderer": sha256(
                REPO
                / "unity/FidgetingApp/Assets/_EDC/Candidates/"
                "MagneticSlideTileGate08R004NeutralParity/Editor/"
                "MagneticSlideTileNeutralParityPreviewBuilder.cs"
            ),
            "videoBuilder": sha256(Path(__file__)),
        },
        "alignment": {
            "checkedRenderedFramePairs": len(alignments),
            "minimumSilhouetteIoU": minimum_iou,
            "maximumCentroidDeltaPixels": maximum_centroid,
            "poseMetadataMatchesEveryFrame": True,
            "transformValidatorsPassedEveryFrame": True,
            "cameraMapping": "Blender Rz(yaw) equals Unity Ry(-yaw)",
            "cameraOrbitDegrees": [-35.0, 35.0],
            "constantElevation": True,
            "stableWorldUp": True,
            "imageOrientationCentroidYRange": [min(centroid_y), max(centroid_y)],
        },
        "state": {
            "gate08": "blocked-pending-corrected-visual-review",
            "gate09": "stale",
            "gate11": "stale",
            "gate12": "stale",
            "approved": False,
            "shippingModified": False,
            "buildInstallPhone": False,
        },
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for folder in (BLENDER, UNITY):
        for path in folder.glob("frame-*-linear.exr"):
            path.unlink()
        folder.rmdir()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
