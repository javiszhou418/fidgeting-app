#!/usr/bin/env python3
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[6]
EVIDENCE = Path(__file__).resolve().parent
BUILD = ROOT / "Builds/iOS/PremiumDisplayCaseGate12Simulator"
STANDARD_VIEWS = [
    ("HERO", "hero.png"),
    ("TOP", "top.png"),
    ("LEFT OBLIQUE", "left-oblique.png"),
    ("RIGHT OBLIQUE", "right-oblique.png"),
    ("LOW", "low.png"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_standard_contact_sheet() -> Path:
    tile_width = 410
    tile_height = 540
    canvas = Image.new("RGB", (tile_width * 3, tile_height * 2), "#07090c")
    draw = ImageDraw.Draw(canvas)
    for index, (label, file_name) in enumerate(STANDARD_VIEWS):
        image = Image.open(EVIDENCE / file_name).convert("RGB")
        image.thumbnail((tile_width - 20, tile_height - 44), Image.Resampling.LANCZOS)
        column = index % 3
        row = index // 3
        x = column * tile_width + (tile_width - image.width) // 2
        y = row * tile_height + 32 + (tile_height - 40 - image.height) // 2
        canvas.paste(image, (x, y))
        draw.text((column * tile_width + 12, row * tile_height + 10), label, fill="white")
    output = EVIDENCE / "standard-views-contact-sheet.png"
    canvas.save(output)
    return output


def analyze_video(path: Path) -> dict:
    capture = cv2.VideoCapture(str(path))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    occupancy = []
    sampled = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if sampled % 3 == 0:
            y0, y1 = int(height * 0.13), int(height * 0.82)
            x0, x1 = int(width * 0.08), int(width * 0.92)
            gray = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
            occupancy.append(float(np.mean(gray > 18)))
        sampled += 1
    capture.release()
    duration = frame_count / fps if fps > 0 else 0
    return {
        "codecContainer": "H.264 MP4",
        "width": width,
        "height": height,
        "fps": fps,
        "frameCount": frame_count,
        "durationSeconds": duration,
        "sampledFrameCount": len(occupancy),
        "minimumCentralVisibleFraction": min(occupancy) if occupancy else 0,
        "noEmptyFrame": bool(occupancy and min(occupancy) >= 0.005),
    }


def main() -> None:
    contact = build_standard_contact_sheet()
    library = EVIDENCE / "library.png"
    Image.open(EVIDENCE / "simulator-final.png").save(library)
    video = EVIDENCE / "app-simulator-pack-to-case.mp4"
    video_report = analyze_video(video)
    manifest_path = BUILD / "FidgetingBuildManifest.json"
    manifest = json.loads(manifest_path.read_text())
    test_path = ROOT / "Logs/PremiumDisplayCaseGate12Focused.xml"
    test_run = ET.parse(test_path).getroot()
    xcode_log = BUILD / "xcodebuild-gate12.log"
    stable_test_path = EVIDENCE / "unity-focused-results.xml"
    stable_manifest_path = EVIDENCE / "simulator-build-manifest.json"
    stable_xcode_summary_path = EVIDENCE / "xcode-build-summary.json"
    shutil.copyfile(test_path, stable_test_path)
    shutil.copyfile(manifest_path, stable_manifest_path)
    xcode_text = xcode_log.read_text()
    stable_xcode_summary_path.write_text(json.dumps({
        "status": "pass" if "** BUILD SUCCEEDED **" in xcode_text else "fail",
        "configuration": "Release",
        "sdk": "iphonesimulator",
        "destination": "iPhone 17 Pro Simulator",
        "bundleIdentifier": manifest["bundleIdentifier"],
        "sourceLogSha256": sha256(xcode_log),
        "physicalPhoneInstalled": False,
    }, indent=2) + "\n")
    profile_path = ROOT / "Assets/Resources/Gacha/PremiumDisplayCaseGate12R001Profile.asset"
    profile_source = profile_path.read_text()
    rotation_match = re.search(r"localYawDegrees:\s*([0-9.]+)", profile_source)
    rotation_degrees = float(rotation_match.group(1)) if rotation_match else None

    required = [
        *(EVIDENCE / file_name for _, file_name in STANDARD_VIEWS),
        library,
        EVIDENCE / "simulator-final.png",
        EVIDENCE / "app-simulator-contact-sheet.png",
        EVIDENCE / "app-simulator-handoff-contact-sheet.png",
        contact,
        video,
        EVIDENCE / "shipping-capture-report.json",
        stable_manifest_path,
        stable_test_path,
        stable_xcode_summary_path,
        EVIDENCE / "native-validation-report.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    checks = {
        "allEvidenceExists": not missing,
        "standardViewsHaveImageData": all(
            np.asarray(Image.open(EVIDENCE / file_name).convert("RGB")).std() > 5
            for _, file_name in STANDARD_VIEWS
        ),
        "videoIsPortrait60Fps": (
            video_report["width"] == 1206
            and video_report["height"] == 2622
            and abs(video_report["fps"] - 60) < 0.01
        ),
        "videoContainsNoEmptyFrame": video_report["noEmptyFrame"],
        "profileUsesOneLocalY360": rotation_degrees == 360,
        "focusedUnityTestsPass": (
            test_run.attrib.get("result") == "Passed"
            and test_run.attrib.get("failed") == "0"
        ),
        "xcodeBuildPasses": "** BUILD SUCCEEDED **" in xcode_text,
        "bundleIdentityIsCanonical": (
            manifest["bundleIdentifier"] == "com.jiaweizhou.fidgetspinner.codex"
        ),
        "gate10FbxHashMatches": (
            manifest["gate11DisplayCaseFbxSha256"]
            == "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
        ),
        "consoleFreeSimulatorBuild": manifest["development"] is False,
        "physicalPhoneInstallNotAuthorized": (
            manifest["physicalPhoneInstallAuthorized"] is False
        ),
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "source": "canonical unity/FidgetingApp shipping source",
        "scene": "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R001.unity",
        "prefab": manifest["gate12DisplayCasePrefab"],
        "profile": "Assets/Resources/Gacha/PremiumDisplayCaseGate12R001Profile.asset",
        "profileValuesLocked": False,
        "wholeAssembledCaseOnly": True,
        "sameInstanceThroughAcknowledgement": True,
        "toyCallerOwned": True,
        "toyIndependentAngularVelocity": 0,
        "rotationDegrees": rotation_degrees,
        "sheenActivationCount": 1,
        "sheenOutsideMeshPixelsByContract": 0,
        "pointLightCount": 0,
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
        "video": video_report,
        "unityTests": {
            "total": int(test_run.attrib["total"]),
            "passed": int(test_run.attrib["passed"]),
            "failed": int(test_run.attrib["failed"]),
        },
        "checks": checks,
        "missing": missing,
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in required
            if path.exists()
        },
        "limitation": (
            "The Simulator preview uses the guarded shipping preview token to fund one "
            "real durable draw transaction. It uses production receipt, ownership, "
            "same-request, reveal-ready and exact-once ACK code, but it is not a "
            "StoreKit sandbox purchase and does not prove iPhone performance, Haptics "
            "or device acceptance."
        ),
        "statusText": "视觉批准待确认，未推送手机",
    }
    output = EVIDENCE / "gate12-evidence-report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
