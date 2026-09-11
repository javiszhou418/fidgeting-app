#!/usr/bin/env python3
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent / "unity-playmode-preview"
FRAME_COUNT = 450
FPS = 30
WIDTH = 1920
HEIGHT = 1080
VIDEO = ROOT / "gate08-r004-unity-playmode-runtime.mp4"
POSTER = ROOT / "gate08-r004-unity-playmode-runtime-poster.png"
REPORT = ROOT / "gate08-r004-unity-playmode-validation.json"
CAPTURE_REPORT = ROOT / "unity-playmode-capture-report.json"
ALLOWED_CUTS = {135, 195, 225, 270, 315, 375, 420}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> str:
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout


def probe_video() -> dict:
    output = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-count_frames",
            "-show_entries",
            "stream=codec_name,profile,width,height,pix_fmt,r_frame_rate,nb_read_frames:format=duration",
            "-of",
            "json",
            str(VIDEO),
        ]
    )
    return json.loads(output)


def frame_metrics(paths: list[Path]) -> dict:
    previous = None
    adjacent = []
    centroids = []
    for index, path in enumerate(paths):
        image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
        if image.shape != (HEIGHT, WIDTH, 3):
            raise RuntimeError(f"Unexpected frame dimensions at {index}: {image.shape}.")
        corner = np.median(
            np.concatenate(
                [
                    image[:64, :64].reshape(-1, 3),
                    image[:64, -64:].reshape(-1, 3),
                    image[-64:, :64].reshape(-1, 3),
                    image[-64:, -64:].reshape(-1, 3),
                ]
            ),
            axis=0,
        )
        mask = np.max(np.abs(image - corner), axis=2) > 18
        mask[:150] = False
        ys, xs = np.where(mask)
        if len(xs) < 500:
            raise RuntimeError(f"Object mask is empty at frame {index}.")
        centroids.append([float(xs.mean()), float(ys.mean())])
        if previous is not None:
            adjacent.append(float(np.mean(np.abs(image - previous))))
        previous = image
    moving = [
        value
        for frame, value in enumerate(adjacent, start=1)
        if frame not in ALLOWED_CUTS
    ]
    centroid_y = [item[1] for item in centroids]
    return {
        "maximumAdjacentFrameMaeExcludingCuts": max(moving),
        "meanAdjacentFrameMaeExcludingCuts": float(np.mean(moving)),
        "maximumCutMae": max(
            adjacent[frame - 1] for frame in ALLOWED_CUTS
        ),
        "objectCentroidYRangePixels": max(centroid_y) - min(centroid_y),
        "objectCentroidYMinimum": min(centroid_y),
        "objectCentroidYMaximum": max(centroid_y),
    }


def main() -> None:
    capture = json.loads(CAPTURE_REPORT.read_text())
    if not capture["pass"]:
        raise RuntimeError("Unity PlayMode capture report failed.")
    if capture["evidenceLevel"] != "Unity Editor PlayMode":
        raise RuntimeError("Capture is not Editor PlayMode.")
    if capture["onScreenDisclosure"] != "Unity URP PlayMode · 不是 iPhone Build":
        raise RuntimeError("Required runtime disclosure is missing.")
    if capture["frameCount"] != FRAME_COUNT:
        raise RuntimeError("Capture frame count mismatch.")
    if capture["blenderFrameCount"] != 0 or capture["offlineCompositeCount"] != 0:
        raise RuntimeError("Non-Unity imagery contaminated the capture.")
    if not capture["perFrameTransformValidation"]:
        raise RuntimeError("Per-frame transform validation did not pass.")
    if capture["iPhoneBuild"] or capture["shippingSceneModified"]:
        raise RuntimeError("Capture changed shipping or claimed an iPhone build.")
    if any(
        not frame["fixedTransforms"]
        or not frame["positiveScale"]
        or abs(frame["cameraRollDegrees"]) > 0.0001
        for frame in capture["frames"]
    ):
        raise RuntimeError("A frame failed its motion invariant.")

    paths = sorted(ROOT.glob("frame-*.png"))
    if len(paths) != FRAME_COUNT:
        raise RuntimeError(f"Expected {FRAME_COUNT} frames, found {len(paths)}.")
    if any("blender" in path.name.lower() for path in paths):
        raise RuntimeError("A source frame name references Blender.")

    Image.open(paths[0]).save(POSTER, optimize=True)
    metrics = frame_metrics(paths)
    if metrics["maximumAdjacentFrameMaeExcludingCuts"] > 20:
        raise RuntimeError("Frame continuity exceeds the non-cut threshold.")

    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(ROOT / "frame-%04d.png"),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-profile:v",
            "high",
            "-level",
            "4.2",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(VIDEO),
        ]
    )
    probe = probe_video()
    stream = probe["streams"][0]
    duration = float(probe["format"]["duration"])
    if (
        stream["codec_name"] != "h264"
        or stream["width"] != WIDTH
        or stream["height"] != HEIGHT
        or stream["pix_fmt"] != "yuv420p"
        or stream["r_frame_rate"] != "30/1"
        or int(stream["nb_read_frames"]) != FRAME_COUNT
        or abs(duration - 15.0) > 0.02
    ):
        raise RuntimeError(f"Encoded video failed specification: {probe}.")

    validation = {
        "pass": True,
        "source": "Unity URP Editor PlayMode Camera render target",
        "sourceFrameCount": FRAME_COUNT,
        "blenderFrameCount": 0,
        "splitScreen": False,
        "offlineComposite": False,
        "fakePostProcessing": False,
        "ffprobe": probe,
        "continuity": metrics,
        "video": {
            "path": str(VIDEO.relative_to(Path(__file__).resolve().parents[6])),
            "sha256": sha256(VIDEO),
            "bytes": VIDEO.stat().st_size,
        },
        "poster": {
            "path": str(POSTER.relative_to(Path(__file__).resolve().parents[6])),
            "sha256": sha256(POSTER),
            "bytes": POSTER.stat().st_size,
        },
        "captureReportSha256": sha256(CAPTURE_REPORT),
    }
    REPORT.write_text(json.dumps(validation, indent=2) + "\n")
    for path in paths:
        path.unlink()
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
