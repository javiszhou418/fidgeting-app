#!/usr/bin/env python3
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PARITY = ROOT / "full-frame-parity-report.json"
UNITY = ROOT / "unity-import-parity-report.json"
RESULTS = ROOT / "editmode-results.xml"
VIDEO = ROOT / "unity-gate11-r010-interactive-review.mp4"
BOARD = ROOT / "gate11-r010-full-frame-board.png"
OUTPUT = ROOT / "final-validation.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parity = json.loads(PARITY.read_text())
    unity = json.loads(UNITY.read_text())
    test_run = ET.parse(RESULTS).getroot()
    video = json.loads(subprocess.check_output([
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(VIDEO),
    ]))
    checks = {
        "unityTransportPassed": unity["pass"],
        "shippingSceneUnchanged": not unity["shippingSceneModified"],
        "gate12NotStarted": not unity["gate12Started"],
        "buildInstallDeviceFalse": not unity["buildInstallDevice"],
        "sameFullFrameMeasured": parity["checks"]["sameFullFrame"],
        "cameraAndBboxPassed": parity["checks"]["cameraAndBbox"],
        "visualParityCorrectlyBlocked": not parity["pass"],
        "hotspotFailureRecorded": not parity["checks"]["hotspot"],
        "clayFailureRecorded": not parity["checks"]["clayGradient"],
        "contactShadowFailureRecorded": not parity["checks"]["contactShadow"],
        "focusedUnityTestsPassed": (
            test_run.attrib["result"] == "Passed"
            and test_run.attrib["total"] == "7"
            and test_run.attrib["failed"] == "0"
        ),
        "recordingIsRealSixSecondUnityCapture": (
            video["streams"][0]["codec_name"] == "h264"
            and video["streams"][0]["width"] == 960
            and video["streams"][0]["height"] == 720
            and video["streams"][0]["nb_frames"] == "72"
            and video["format"]["duration"] == "6.000000"
        ),
        "boardExists": BOARD.exists(),
    }
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 10,
        "status": "validated-blocked-not-ready-for-review",
        "checks": checks,
        "tests": {
            "total": int(test_run.attrib["total"]),
            "passed": int(test_run.attrib["passed"]),
            "failed": int(test_run.attrib["failed"]),
        },
        "video": video,
        "fullFrameSummary": {
            "ssim": parity["fullFrame"]["globalSsim"],
            "perceptualProxy": parity["fullFrame"]["perceptualProxy"]["combined"],
            "heatmapAreaFractionOver24": parity["fullFrame"]["heatmapAreaFractionOver24"],
            "backgroundMeanAbsoluteError": parity["fullFrame"]["backgroundMeanAbsoluteError"],
            "hotspotAreaRelativeError": parity["hotspot"]["relativeAreaError"],
            "hotspotCentroidErrorPixels": parity["hotspot"]["centroidErrorPixels"],
            "hotspotAspectRelativeError": parity["hotspot"]["aspectRelativeError"],
            "clayGradientMagnitudeRelativeError": parity["clay"]["gradientMagnitudeRelativeError"],
            "contactShadowRelativeError": parity["clay"]["contactShadowRelativeError"],
        },
        "files": {
            path.name: {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
            for path in [PARITY, UNITY, RESULTS, VIDEO, BOARD]
        },
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
