import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image


HERE = Path(__file__).resolve().parent
FRAMES = HERE / "unity-preview/frames"
VIDEO = HERE / "unity-preview/gate05-r012-unity-fixed-axis-motion.mp4"
UNITY_REPORT = json.loads((HERE / "unity-preview/unity-motion-validation.json").read_text())
files = sorted(FRAMES.glob("frame-*.png"))
centroids = []
for path in files:
    image = Image.open(path).convert("RGB")
    pixels = image.load()
    points = [
        (x, y)
        for y in range(image.height)
        for x in range(image.width)
        if pixels[x, y][0] > 180 and pixels[x, y][1] < 70 and pixels[x, y][2] < 50
    ]
    if not points:
        raise RuntimeError(f"Missing fixed-axis overlay in {path.name}")
    centroids.append((sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points)))

probe = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(VIDEO)
]))
stream = probe["streams"][0]
report = {
    "schemaVersion": 1,
    "gate": "05-blockout",
    "revision": 12,
    "source": "real Unity 6000.5.6f1 Camera frames",
    "frameCount": len(files),
    "axisOverlayCentroidRangePx": {
        "x": max(x for x, _ in centroids) - min(x for x, _ in centroids),
        "y": max(y for _, y in centroids) - min(y for _, y in centroids),
    },
    "unityTransformValidation": {
        "fixedPivotVarianceMeters": UNITY_REPORT["maxPivotVarianceMeters"],
        "constraintResidualMeters": UNITY_REPORT["maxConstraintResidualMeters"],
        "pitchRollDegrees": UNITY_REPORT["maxPitchRollDegrees"],
        "rendererWhitelist": UNITY_REPORT["rendererWhitelist"],
    },
    "video": {
        "path": VIDEO.name,
        "sha256": hashlib.sha256(VIDEO.read_bytes()).hexdigest(),
        "codec": stream["codec_name"],
        "pixelFormat": stream["pix_fmt"],
        "width": stream["width"],
        "height": stream["height"],
        "frameRate": stream["avg_frame_rate"],
        "durationSeconds": float(probe["format"]["duration"]),
    },
    "checks": {
        "allFramesPresent": len(files) == 300,
        "fixedWorldAxisOverlay": max(x for x, _ in centroids) - min(x for x, _ in centroids) <= 0.01 and max(y for _, y in centroids) - min(y for _, y in centroids) <= 0.01,
        "pivotVarianceZero": UNITY_REPORT["maxPivotVarianceMeters"] == 0,
        "slotPointLocked": UNITY_REPORT["maxConstraintResidualMeters"] <= 1e-7,
        "noPitchRoll": UNITY_REPORT["maxPitchRollDegrees"] <= 0.0001,
        "productWhitelistExact": UNITY_REPORT["rendererWhitelist"] == ["BottomExterior", "MovingTopBody"],
        "videoTenSeconds": abs(float(probe["format"]["duration"]) - 10.0) <= 0.05,
    },
}
report["pass"] = all(report["checks"].values())
(HERE / "unity-preview/motion-video-validation.json").write_text(json.dumps(report, indent=2))
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

