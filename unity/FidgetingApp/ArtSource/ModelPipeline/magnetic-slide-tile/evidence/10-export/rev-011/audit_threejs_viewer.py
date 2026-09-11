#!/usr/bin/env python3
"""Validate the real Three.js GLB screenshot and interaction recording."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
SCREENSHOT = HERE / "gate10-r011-threejs-neutral-hero.png"
VIDEO = HERE / "gate10-r011-real-glb-orbit.mp4"
BROWSER = HERE / "browser-viewer-validation.json"
REJECTION = HERE / "user-rejection-washed-out-r010.jpg"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def region_metrics(image: np.ndarray, box: tuple[int, int, int, int]) -> dict:
    left, top, right, bottom = box
    rgb = image[top:bottom, left:right, :3].reshape((-1, 3))
    luminance = rgb[:, 0] * 0.2126 + rgb[:, 1] * 0.7152 + rgb[:, 2] * 0.0722
    object_mask = (rgb.max(axis=1) - rgb.min(axis=1) > 0.035) | (luminance > 0.11)
    pixels = rgb[object_mask]
    values = luminance[object_mask]
    red = (pixels[:, 0] > pixels[:, 1] * 1.32) & (pixels[:, 0] > pixels[:, 2] * 1.20)
    return {
        "sampledPixels": int(object_mask.sum()),
        "redFraction": float(red.mean()),
        "luminanceP05P50P95": [float(np.percentile(values, p)) for p in [5, 50, 95]],
        "clippedWhiteFraction": float((values > 0.95).mean()),
        "controlledSilverFraction": float(((values > 0.58) & (values < 0.95)).mean()),
    }


def main() -> None:
    screenshot = np.asarray(Image.open(SCREENSHOT).convert("RGB"), dtype=np.float32) / 255.0
    rejection = np.asarray(Image.open(REJECTION).convert("RGB"), dtype=np.float32) / 255.0
    browser = json.loads(BROWSER.read_text())
    viewer = region_metrics(screenshot, (170, 190, 820, 565))
    side = region_metrics(screenshot, (210, 390, 780, 565))
    reject_luminance = (
        rejection[..., 0] * 0.2126
        + rejection[..., 1] * 0.7152
        + rejection[..., 2] * 0.0722
    )
    video_probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "stream=width,height,nb_frames,duration:format=duration",
        "-of", "json", str(VIDEO),
    ]))
    stream = video_probe["streams"][0]
    checks = {
        "browserPass": browser["pass"],
        "realGlbLoaded": browser["viewer"]["checklist"]["loaded"],
        "orbitCompleted": browser["viewer"]["checklist"]["orbit"],
        "zoomCompleted": browser["viewer"]["checklist"]["zoom"],
        "neutralHdr": browser["calibration"]["environment"].endswith("neutral-control-r009.exr")
            and browser["calibration"]["environmentIntensity"] == 0.58,
        "colorPipeline": browser["calibration"]["outputColorSpace"] == "SRGBColorSpace"
            and browser["calibration"]["toneMapping"] == "ACESFilmicToneMapping"
            and browser["calibration"]["exposure"] == 0.9,
        "exposureIsolated": browser["calibration"]["exposureControl"] == 0.9
            and browser["calibration"]["exposureMax"] == 1.1,
        "deepBloodRedVisible": viewer["redFraction"] >= 0.20,
        "darkBodyVisible": side["luminanceP05P50P95"][1] <= 0.28,
        "silverControlled": 0.01 <= viewer["controlledSilverFraction"] <= 0.20,
        "noWhiteAreaExcess": viewer["clippedWhiteFraction"] <= 0.03,
        "rejectionWhiteAreaExcess": float((reject_luminance > 0.95).mean()) >= 0.06,
        "videoDimensions": int(stream["width"]) == 1200 and int(stream["height"]) == 900,
        "videoFrames": int(stream.get("nb_frames", 0)) == 24,
        "videoNontrivial": VIDEO.stat().st_size > 100_000,
        "runtimeClean": browser["runtimeExceptionCount"] == 0 and browser["loadingFailureCount"] == 0,
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "pass": all(checks.values()),
        "viewerMetrics": viewer,
        "sideMetrics": side,
        "rejectionWholeImageWhiteFraction": float((reject_luminance > 0.95).mean()),
        "calibration": browser["calibration"],
        "videoProbe": video_probe,
        "artifacts": {
            "viewerScreenshot": {"path": str(SCREENSHOT), "sha256": sha256(SCREENSHOT)},
            "orbitRecording": {"path": str(VIDEO), "sha256": sha256(VIDEO)},
        },
        "checks": checks,
    }
    (HERE / "threejs-viewer-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
