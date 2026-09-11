import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
FRAMES = HERE / "unity-preview/frames-full-360"
VIDEO = HERE / "unity-preview/gate05-r012-unity-full-360-motion.mp4"
UNITY_REPORT_PATH = HERE / "unity-preview/unity-full-rotation-validation.json"
UNITY_REPORT = json.loads(UNITY_REPORT_PATH.read_text())
PIPELINE = json.loads((HERE.parents[2] / "pipeline.json").read_text())
files = sorted(FRAMES.glob("frame-*.png"))
centroids = []
dimensions = set()
first_pixels = None
last_pixels = None
for index, path in enumerate(files):
    pixels = np.asarray(Image.open(path).convert("RGB"))
    dimensions.add((pixels.shape[1], pixels.shape[0]))
    red = (pixels[:, :, 0] > 180) & (pixels[:, :, 1] < 70) & (pixels[:, :, 2] < 50)
    y, x = np.nonzero(red)
    if not len(x):
        raise RuntimeError(f"Missing fixed-axis overlay in {path.name}")
    centroids.append((float(x.mean()), float(y.mean())))
    if index == 0:
        first_pixels = pixels.copy()
    if index == len(files) - 1:
        last_pixels = pixels.copy()

probe = json.loads(subprocess.check_output([
    "ffprobe",
    "-v",
    "error",
    "-count_frames",
    "-show_streams",
    "-show_format",
    "-of",
    "json",
    str(VIDEO),
]))
stream = next(item for item in probe["streams"] if item["codec_type"] == "video")
quicktime = json.loads(subprocess.check_output([
    "swift",
    str(HERE / "validate_quicktime_playback.swift"),
    str(VIDEO),
]))
axis_range = {
    "x": max(x for x, _ in centroids) - min(x for x, _ in centroids),
    "y": max(y for _, y in centroids) - min(y for _, y in centroids),
}
model_roi = (slice(250, 850), slice(650, 1450))
closure_pixel_max_delta = int(np.abs(
    first_pixels[model_roi].astype(np.int16) - last_pixels[model_roi].astype(np.int16)
).max())
fbx = HERE / "magnetic-slide-tile-fixed-axis-r012.fbx"
fbx_sha = hashlib.sha256(fbx.read_bytes()).hexdigest()
registered_fbx_sha = next(
    asset["sha256"] for asset in PIPELINE["assets"]
    if asset["id"] == "magnetic-slide-g05-r012-fbx"
)
duration = float(probe["format"]["duration"])
checks = {
    "realUnityFrames": UNITY_REPORT["unityVersion"] == "6000.5.6f1" and len(files) == 570,
    "h264High1920x1080": stream["codec_name"] == "h264"
    and stream.get("profile") == "High"
    and stream["pix_fmt"] == "yuv420p"
    and stream["width"] == 1920
    and stream["height"] == 1080,
    "thirtyFpsNineteenSeconds": stream["avg_frame_rate"] == "30/1"
    and abs(duration - 19.0) <= 0.02
    and int(stream.get("nb_read_frames", stream.get("nb_frames", 0))) == 570,
    "quickTimePlayable": quicktime["isPlayable"]
    and quicktime["videoSampleCount"] == 570
    and quicktime["width"] == 1920
    and quicktime["height"] == 1080
    and abs(quicktime["durationSeconds"] - 19.0) <= 0.02,
    "allFrameDimensionsExact": dimensions == {(1920, 1080)},
    "fixedWorldAxisOverlay": axis_range["x"] <= 0.01 and axis_range["y"] <= 0.01,
    "singleFixedPivot": UNITY_REPORT["maxPivotVarianceMeters"] == 0,
    "slotPointLockedEveryFrame": UNITY_REPORT["maxConstraintResidualMeters"] <= 1e-7,
    "bottomStaticHorizontal": UNITY_REPORT["maxBottomPositionVarianceMeters"] == 0
    and UNITY_REPORT["maxBottomRotationVarianceDegrees"] == 0,
    "productStaticHorizontal": UNITY_REPORT["maxProductPositionVarianceMeters"] == 0
    and UNITY_REPORT["maxProductRotationVarianceDegrees"] == 0
    and UNITY_REPORT["maxPitchRollDegrees"] == 0,
    "partialFullRevolution": UNITY_REPORT["partialRevolution"]["startUnwrappedDegrees"] == 0
    and UNITY_REPORT["partialRevolution"]["endUnwrappedDegrees"] == 360
    and UNITY_REPORT["partialRevolution"]["orientationClosureDegrees"] <= 0.0001,
    "maximumFullRevolution": UNITY_REPORT["maximumRevolution"]["startUnwrappedDegrees"] == 0
    and UNITY_REPORT["maximumRevolution"]["endUnwrappedDegrees"] == 360
    and UNITY_REPORT["maximumRevolution"]["orientationClosureDegrees"] <= 0.0001,
    "allThirtyDetentsVisited": UNITY_REPORT["visitedDetentIndices"] == list(range(30)),
    "finalOrientationClosure": UNITY_REPORT["finalOrientationClosureDegrees"] <= 0.0001
    and closure_pixel_max_delta <= 1,
    "legalSlideOnly": UNITY_REPORT["illegalSlideFrames"] == 0
    and 0 < UNITY_REPORT["partialSlideMeters"] < UNITY_REPORT["maximumSlideMeters"],
    "minimumDiskContained": UNITY_REPORT["containmentRayMisses"] == 0,
    "topAboveBottom": UNITY_REPORT["minimumVerticalGapMeters"] > 0,
    "rendererWhitelistExact": UNITY_REPORT["rendererWhitelist"] == ["BottomExterior", "MovingTopBody"],
    "fixedCamera": UNITY_REPORT["cameraMotionFrames"] == 0,
    "geometryUnchanged": fbx_sha == registered_fbx_sha,
    "priorRecordingSupersededOnlyForFullRotation": UNITY_REPORT["priorRecordingStatus"]
    == "valid-partial-evidence-superseded-for-full-rotation-approval",
    "noBuildInstallPhone": not UNITY_REPORT["build"]
    and not UNITY_REPORT["install"]
    and not UNITY_REPORT["phone"],
}
report = {
    "schemaVersion": 1,
    "gate": "05-blockout",
    "revision": 12,
    "source": "real Unity 6000.5.6f1 Camera frames",
    "recipe": {
        "camera": "fixed",
        "material": "white-clay-only",
        "frames": 570,
        "fps": 30,
        "phases": [
            "closed/open transition",
            "0-360 degrees at 50% legal slide",
            "open to maximum legal slide",
            "0-360 degrees at maximum legal slide",
            "compound slide and rotation",
            "return to closed at 360 degrees",
        ],
        "detents": "30 unique positions at 12-degree intervals",
        "fixedAxisOverlay": "red world-up line through FixedAxis",
    },
    "frameCount": len(files),
    "axisOverlayCentroidRangePx": axis_range,
    "closureModelRoiMaxPixelDelta": closure_pixel_max_delta,
    "sourceGeometry": {
        "path": str(fbx.relative_to(HERE.parents[7])),
        "sha256": fbx_sha,
        "registeredSha256": registered_fbx_sha,
    },
    "unityTransformValidation": UNITY_REPORT,
    "video": {
        "path": VIDEO.name,
        "sha256": hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
        "sizeBytes": VIDEO.stat().st_size,
        "codec": stream["codec_name"],
        "profile": stream.get("profile"),
        "pixelFormat": stream["pix_fmt"],
        "width": stream["width"],
        "height": stream["height"],
        "frameRate": stream["avg_frame_rate"],
        "frames": int(stream.get("nb_read_frames", stream.get("nb_frames", 0))),
        "durationSeconds": duration,
        "fastStart": True,
    },
    "quickTime": quicktime,
    "checks": checks,
}
report["pass"] = all(checks.values())
(HERE / "unity-preview/full-rotation-video-validation.json").write_text(json.dumps(report, indent=2))
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps({
    "pass": report["pass"],
    "video": report["video"],
    "axisOverlayCentroidRangePx": axis_range,
    "closureModelRoiMaxPixelDelta": closure_pixel_max_delta,
    "quickTime": quicktime,
}, indent=2))
