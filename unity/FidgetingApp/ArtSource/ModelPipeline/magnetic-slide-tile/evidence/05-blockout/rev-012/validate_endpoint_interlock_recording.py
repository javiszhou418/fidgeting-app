import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FRAMES = HERE / "unity-preview/frames-endpoint-interlock"
VIDEO = HERE / "unity-preview/gate05-r012-endpoint-interlock-motion.mp4"
UNITY_PATH = HERE / "unity-preview/unity-endpoint-interlock-validation.json"
UNITY = json.loads(UNITY_PATH.read_text())
PIPELINE = json.loads((HERE.parents[2] / "pipeline.json").read_text())
CONTRACT = HERE.parents[2] / "evidence/02-analysis/rev-017/mechanism-evidence-contract.json"
files = sorted(FRAMES.glob("frame-*.png"))
centroids = []
dimensions = set()
first_pixels = last_pixels = None
for index, frame_path in enumerate(files):
    pixels = np.asarray(Image.open(frame_path).convert("RGB"))
    dimensions.add((pixels.shape[1], pixels.shape[0]))
    y, x = np.nonzero(
        (pixels[:, :, 0] > 180) & (pixels[:, :, 1] < 70) & (pixels[:, :, 2] < 50)
    )
    if not len(x):
        raise RuntimeError(f"Missing fixed-axis overlay in {frame_path.name}")
    centroids.append((float(x.mean()), float(y.mean())))
    if index == 0:
        first_pixels = pixels.copy()
    if index == len(files) - 1:
        last_pixels = pixels.copy()

probe = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-count_frames", "-show_streams",
    "-show_format", "-of", "json", str(VIDEO)
]))
stream = next(item for item in probe["streams"] if item["codec_type"] == "video")
quicktime = json.loads(subprocess.check_output([
    "swift", str(HERE / "validate_quicktime_playback.swift"), str(VIDEO)
]))
axis_range = {
    "x": max(x for x, _ in centroids) - min(x for x, _ in centroids),
    "y": max(y for _, y in centroids) - min(y for _, y in centroids),
}
roi = (slice(250, 850), slice(650, 1450))
closure_delta = int(np.abs(
    first_pixels[roi].astype(np.int16) - last_pixels[roi].astype(np.int16)
).max())
fbx = HERE / "magnetic-slide-tile-fixed-axis-r012.fbx"
fbx_sha = hashlib.sha256(fbx.read_bytes()).hexdigest()
registered_fbx_sha = next(
    item["sha256"] for item in PIPELINE["assets"] if item["id"] == "magnetic-slide-g05-r012-fbx"
)
contract_sha = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
records = UNITY["framesData"]
maximum = UNITY["maximumSlideMeters"]
below_maximum = [item for item in records if item["slideMeters"] < maximum - 1e-8]
nonzero = [
    item for item in records
    if min(item["unwrappedAngleDegrees"] % 360, 360 - item["unwrappedAngleDegrees"] % 360) > 1e-4
]
rotation_attempts = [item for item in records if item["rotationAttempt"]]
slide_attempts = [item for item in records if item["slideAttempt"]]
duration = float(probe["format"]["duration"])
checks = {
    "realUnityFrames": UNITY["unityVersion"] == "6000.5.6f1" and len(files) == 450,
    "currentContractConsumed": UNITY["contractSha256"] == contract_sha,
    "h264High1920x1080": stream["codec_name"] == "h264"
    and stream.get("profile") == "High" and stream["pix_fmt"] == "yuv420p"
    and stream["width"] == 1920 and stream["height"] == 1080,
    "thirtyFpsFifteenSeconds": stream["avg_frame_rate"] == "30/1"
    and abs(duration - 15.0) <= 0.02
    and int(stream.get("nb_read_frames", stream.get("nb_frames", 0))) == 450,
    "quickTimePlayable": quicktime["isPlayable"]
    and quicktime["videoSampleCount"] == 450
    and quicktime["width"] == 1920 and quicktime["height"] == 1080,
    "allFrameDimensionsExact": dimensions == {(1920, 1080)},
    "fixedWorldAxisOverlay": axis_range["x"] <= 0.01 and axis_range["y"] <= 0.01,
    "singleFixedPivot": UNITY["maxPivotVarianceMeters"] == 0,
    "slotPointLockedEveryFrame": UNITY["maxConstraintResidualMeters"] <= 1e-7,
    "bottomAndProductStatic": UNITY["maxBottomPositionVarianceMeters"] == 0
    and UNITY["maxBottomRotationVarianceDegrees"] == 0
    and UNITY["maxProductPositionVarianceMeters"] == 0
    and UNITY["maxProductRotationVarianceDegrees"] == 0,
    "noPitchRoll": UNITY["maxPitchRollDegrees"] == 0,
    "rotationBlockedBelowMaximum": UNITY["belowMaxRotationViolations"] == 0
    and all(item["unwrappedAngleDegrees"] % 360 == 0 for item in below_maximum),
    "midTravelAttemptVisibleAndBlocked": len(rotation_attempts) == 30
    and all(item["unwrappedAngleDegrees"] == 0 for item in rotation_attempts),
    "rotationOnlyAtMaximum": UNITY["endpointUnlockViolations"] == 0
    and all(item["atMaximum"] for item in nonzero),
    "allThirtyDetentsAtEndpoint": UNITY["visitedDetentIndices"] == list(range(30)),
    "slideBlockedWhileNonzero": UNITY["rotatedSlideViolations"] == 0
    and len(slide_attempts) == 30
    and all(item["atMaximum"] and item["unwrappedAngleDegrees"] == 180 for item in slide_attempts),
    "alignmentPermitsReturn": all(item["aligned"] for item in records[391:421])
    and records[420]["slideMeters"] == 0,
    "noSimultaneousVelocities": UNITY["simultaneousVelocityViolations"] == 0,
    "full360Closure": UNITY["fullRevolutionClosureDegrees"] <= 0.0001
    and UNITY["finalOrientationClosureDegrees"] <= 0.0001 and closure_delta <= 1,
    "minimumDiskContained": UNITY["containmentRayMisses"] == 0,
    "topAboveBottom": UNITY["minimumVerticalGapMeters"] > 0,
    "rendererWhitelistExact": UNITY["rendererWhitelist"] == ["BottomExterior", "MovingTopBody"],
    "fixedCamera": UNITY["cameraMotionFrames"] == 0,
    "geometryUnchanged": not UNITY["geometryChanged"] and fbx_sha == registered_fbx_sha,
    "priorInvalidEvidenceRejected": "50% travel" in UNITY["rejectedPriorFullRotationEvidence"],
    "noBuildInstallPhone": not UNITY["build"] and not UNITY["install"] and not UNITY["phone"],
}
report = {
    "schemaVersion": 2,
    "gate": "05-blockout",
    "revision": 12,
    "source": "real Unity 6000.5.6f1 Camera frames",
    "contractSha256": contract_sha,
    "stateMachine": UNITY["stateMachine"],
    "recipe": {
        "camera": "fixed",
        "material": "white-clay-only",
        "frames": 450,
        "fps": 30,
        "phases": [
            "closed theta=0",
            "slide to midpoint with rotation locked",
            "visible rejected rotation attempt at midpoint",
            "slide to sMax and unlock",
            "rotate 0-180 through detents",
            "visible rejected slide attempt at 180 degrees",
            "rotate 180-360 through detents",
            "aligned return to closed",
        ],
    },
    "frameCount": len(files),
    "axisOverlayCentroidRangePx": axis_range,
    "closureModelRoiMaxPixelDelta": closure_delta,
    "sourceGeometry": {"sha256": fbx_sha, "registeredSha256": registered_fbx_sha},
    "unityTransformValidation": UNITY,
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
    },
    "quickTime": quicktime,
    "checks": checks,
}
report["pass"] = all(checks.values())
(HERE / "unity-preview/endpoint-interlock-video-validation.json").write_text(
    json.dumps(report, indent=2)
)
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps({
    "pass": True,
    "video": report["video"],
    "axisOverlayCentroidRangePx": axis_range,
    "closureModelRoiMaxPixelDelta": closure_delta,
    "quickTime": quicktime,
}, indent=2))
