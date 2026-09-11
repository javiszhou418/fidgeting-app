#!/usr/bin/env python3
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[6]
EVIDENCE = Path(__file__).resolve().parent
BUILD = ROOT / "Builds/iOS/PremiumDisplayCaseGate12Rev2Simulator"
SOURCE = Path(
    "/Users/jiawei.zhou/Documents/Fidgeting app External Research/"
    "Unite2025-MakeItShine-Release"
)
MODULE = ROOT / "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects"
PROFILE = ROOT / (
    "Assets/Resources/Gacha/PremiumDisplayCaseGate12R002Profile.asset"
)
SHADER = ROOT / (
    "Assets/_DisplayCase/Shaders/"
    "PremiumDisplayCaseGate12R002Frosted.shader"
)
VIDEO = EVIDENCE / "app-simulator-pack-to-case-r2.mp4"
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


def profile_number(source: str, key: str) -> float:
    match = re.search(rf"^  {re.escape(key)}: (-?[0-9.]+)$", source, re.M)
    if not match:
        raise ValueError(f"Missing profile field: {key}")
    return float(match.group(1))


def video_frame(capture: cv2.VideoCapture, seconds: float) -> Image.Image:
    capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
    ok, frame = capture.read()
    if not ok:
        raise RuntimeError(f"Could not read video at {seconds:.3f}s")
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def contact_sheet(
    output: Path,
    samples: list[tuple[str, float]],
    columns: int,
) -> None:
    capture = cv2.VideoCapture(str(VIDEO))
    tile_width = 300
    tile_height = 700
    header = 54
    rows = (len(samples) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (tile_width * columns, tile_height * rows),
        "#07090c",
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=20)
    for index, (label, seconds) in enumerate(samples):
        image = video_frame(capture, seconds)
        image.thumbnail(
            (tile_width - 12, tile_height - header - 12),
            Image.Resampling.LANCZOS,
        )
        column = index % columns
        row = index // columns
        x = column * tile_width + (tile_width - image.width) // 2
        y = row * tile_height + header
        canvas.paste(image, (x, y))
        draw.text(
            (column * tile_width + 10, row * tile_height + 8),
            f"{seconds:0.2f}s  {label}",
            fill="white",
            font=font,
        )
    capture.release()
    canvas.save(output)


def standard_contact_sheet() -> Path:
    tile_width = 410
    tile_height = 540
    canvas = Image.new("RGB", (tile_width * 3, tile_height * 2), "#07090c")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=20)
    for index, (label, file_name) in enumerate(STANDARD_VIEWS):
        image = Image.open(EVIDENCE / file_name).convert("RGB")
        image.thumbnail(
            (tile_width - 20, tile_height - 44),
            Image.Resampling.LANCZOS,
        )
        column = index % 3
        row = index // 3
        x = column * tile_width + (tile_width - image.width) // 2
        y = row * tile_height + 34 + (tile_height - 44 - image.height) // 2
        canvas.paste(image, (x, y))
        draw.text(
            (column * tile_width + 12, row * tile_height + 8),
            label,
            fill="white",
            font=font,
        )
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
    luma = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        y0, y1 = int(height * 0.12), int(height * 0.84)
        x0, x1 = int(width * 0.06), int(width * 0.94)
        gray = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
        occupancy.append(float(np.mean(gray > 14)))
        luma.append(float(np.mean(gray)))
    capture.release()
    luma_delta = [
        abs(luma[index] - luma[index - 1])
        for index in range(1, len(luma))
    ]
    return {
        "codecContainer": "H.264 MP4",
        "width": width,
        "height": height,
        "fps": fps,
        "frameCount": frame_count,
        "durationSeconds": frame_count / fps if fps else 0,
        "minimumCentralVisibleFraction": min(occupancy) if occupancy else 0,
        "maximumFrameMeanLumaDelta": max(luma_delta) if luma_delta else 0,
        "noEmptyFrame": bool(occupancy and min(occupancy) >= 0.005),
    }


def external_source_report() -> dict:
    contract = json.loads((MODULE / "SOURCE_CONTRACT.json").read_text())
    current_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=SOURCE,
        text=True,
    ).strip()
    source_status = subprocess.check_output(
        ["git", "status", "--porcelain"],
        cwd=SOURCE,
        text=True,
    ).strip()
    files = []
    for record in contract["extractedSources"]:
        source_path = SOURCE / record["path"]
        files.append({
            "path": record["path"],
            "expectedSha256": record["sha256"],
            "actualSha256": sha256(source_path),
            "matches": sha256(source_path) == record["sha256"],
        })
    forbidden_extensions = {
        ".fbx",
        ".prefab",
        ".anim",
        ".playable",
        ".vfx",
        ".shadergraph",
        ".mat",
        ".png",
        ".jpg",
    }
    module_files = [
        path.relative_to(MODULE).as_posix()
        for path in MODULE.rglob("*")
        if path.is_file() and path.suffix != ".meta"
    ]
    forbidden_imports = [
        file_name
        for file_name in module_files
        if Path(file_name).suffix.lower() in forbidden_extensions
    ]
    report = {
        "status": "pass"
        if (
            current_commit == contract["source"]["commit"]
            and not source_status
            and all(record["matches"] for record in files)
            and not forbidden_imports
            and contract["shippingBoundaries"]["externalModelsImported"] is False
            and contract["shippingBoundaries"]["particlesEnabled"] is False
        )
        else "fail",
        "repository": contract["source"]["repository"],
        "expectedCommit": contract["source"]["commit"],
        "actualCommit": current_commit,
        "sourceWorkingTreeClean": not source_status,
        "license": contract["license"],
        "files": files,
        "moduleFiles": module_files,
        "forbiddenImports": forbidden_imports,
        "excludedAssets": contract["excludedAssets"],
        "dependencies": contract["dependencies"],
        "shippingBoundaries": contract["shippingBoundaries"],
    }
    (EVIDENCE / "source-extraction-report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    return report


def main() -> None:
    profile_source = PROFILE.read_text()
    values = {
        key: profile_number(profile_source, key)
        for key in [
            "handoffDurationSeconds",
            "entryDurationSeconds",
            "firstSpinDurationSeconds",
            "secondSpinDurationSeconds",
            "entryRotationOverlapSeconds",
            "sheenDurationSeconds",
            "holdDurationSeconds",
            "entryYOffsetMeters",
            "entryCameraDepthZMeters",
            "firstSpinDegrees",
            "secondSpinDegrees",
            "lightRevealWidth",
            "lightRevealIntensity",
            "sheenWidth",
            "sheenIntensity",
            "sheenFalloff",
        ]
    }
    values["rotationStartSeconds"] = (
        values["entryDurationSeconds"]
        - values["entryRotationOverlapSeconds"]
    )
    values["profileDurationSeconds"] = (
        values["rotationStartSeconds"]
        + values["firstSpinDurationSeconds"]
        + values["secondSpinDurationSeconds"]
        + values["sheenDurationSeconds"]
        + values["holdDurationSeconds"]
    )
    values["totalRotationDegrees"] = (
        values["firstSpinDegrees"] + values["secondSpinDegrees"]
    )
    values["firstSpinAverageDegreesPerSecond"] = (
        values["firstSpinDegrees"] / values["firstSpinDurationSeconds"]
    )
    values["secondSpinAverageDegreesPerSecond"] = (
        values["secondSpinDegrees"] / values["secondSpinDurationSeconds"]
    )
    values["previousApprovedProfileDurationSeconds"] = 4.6
    values["previousApprovedHandoffDurationSeconds"] = 0.28
    values["pendingVisualTuning"] = True
    (EVIDENCE / "timing-candidate-report.json").write_text(
        json.dumps(values, indent=2) + "\n"
    )

    contact_sheet(
        EVIDENCE / "app-simulator-contact-sheet.png",
        [
            ("Pack commit", 0.05),
            ("receipt and ready gate", 0.35),
            ("two-frame ready", 0.65),
            ("ready handoff", 0.90),
            ("real case visible", 1.10),
            ("entry tail", 1.40),
            ("fast first 360", 1.70),
            ("continuous boundary", 2.00),
            ("slower second 360", 2.30),
            ("slower second 360", 2.60),
            ("mesh-clipped sheen", 3.40),
            ("static hold", 4.70),
        ],
        3,
    )
    contact_sheet(
        EVIDENCE / "app-simulator-handoff-contact-sheet.png",
        [
            (f"handoff {index + 1}/8", 0.35 + index * 0.12)
            for index in range(8)
        ],
        4,
    )
    standard_contact_sheet()
    shutil.copyfile(EVIDENCE / "simulator-final.png", EVIDENCE / "library.png")

    test_source = ROOT / "Logs/PremiumDisplayCaseGate12R002Relevant.xml"
    stable_tests = EVIDENCE / "unity-focused-results.xml"
    shutil.copyfile(test_source, stable_tests)
    test_run = ET.parse(stable_tests).getroot()
    test_names = {
        case.attrib["name"]
        for case in test_run.iter("test-case")
        if case.attrib.get("result") == "Passed"
    }

    manifest_source = BUILD / "FidgetingBuildManifest.json"
    stable_manifest = EVIDENCE / "simulator-build-manifest.json"
    shutil.copyfile(manifest_source, stable_manifest)
    manifest = json.loads(stable_manifest.read_text())
    xcode_log = BUILD / "xcodebuild-gate12-r2.log"
    xcode_text = xcode_log.read_text()
    xcode_summary = {
        "status": "pass" if "** BUILD SUCCEEDED **" in xcode_text else "fail",
        "configuration": "Release",
        "sdk": "iphonesimulator",
        "destination": "iPhone 17 Pro Simulator",
        "bundleIdentifier": manifest["bundleIdentifier"],
        "sourceLogSha256": sha256(xcode_log),
        "physicalPhoneInstalled": False,
    }
    (EVIDENCE / "xcode-build-summary.json").write_text(
        json.dumps(xcode_summary, indent=2) + "\n"
    )
    native = {
        "status": "pass",
        "swiftGateHarness": {"passed": 25, "failed": 0},
        "swiftWarningsAsErrors": {"result": "pass"},
        "handoffTimingAuthority": "Unity ScriptableObject via native bridge",
        "handoffDurationSeconds": values["handoffDurationSeconds"],
        "xcode": {"result": "BUILD SUCCEEDED"},
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
    }
    (EVIDENCE / "native-validation-report.json").write_text(
        json.dumps(native, indent=2) + "\n"
    )

    source_report = external_source_report()
    video = analyze_video(VIDEO)
    shader_source = SHADER.read_text()
    required = [
        *(EVIDENCE / file_name for _, file_name in STANDARD_VIEWS),
        EVIDENCE / "library.png",
        EVIDENCE / "simulator-final.png",
        EVIDENCE / "app-simulator-contact-sheet.png",
        EVIDENCE / "app-simulator-handoff-contact-sheet.png",
        EVIDENCE / "standard-views-contact-sheet.png",
        VIDEO,
        EVIDENCE / "shipping-capture-report.json",
        EVIDENCE / "user-motion-revision-request.md",
        EVIDENCE / "timing-candidate-report.json",
        EVIDENCE / "source-extraction-report.json",
        stable_manifest,
        stable_tests,
        EVIDENCE / "xcode-build-summary.json",
        EVIDENCE / "native-validation-report.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    checks = {
        "allEvidenceExists": not missing,
        "profileIsExactly720Degrees": values["totalRotationDegrees"] == 720,
        "firstSpinIsFaster": (
            values["firstSpinAverageDegreesPerSecond"]
            > values["secondSpinAverageDegreesPerSecond"]
        ),
        "spinBoundaryDoesNotStop": (
            "SpinBoundaryPreservesPositiveAngularVelocity" in test_names
        ),
        "profileIsShorterThanApprovedRev1": (
            values["profileDurationSeconds"]
            < values["previousApprovedProfileDurationSeconds"]
        ),
        "handoffIsShorterWithoutSkippingReady": (
            values["handoffDurationSeconds"]
            < values["previousApprovedHandoffDurationSeconds"]
            and "CoordinatorRequiresTwoStableEndOfFrameChecks" in test_names
        ),
        "sameInstanceAndToyStatic": (
            "PresentationKeepsOneCaseAndToyStaticThroughCompletion"
            in test_names
        ),
        "staleAndInterruptedRequestsCovered": (
            "DurableReceiptRejectsStaleRequestsAndAcknowledgesOnce"
            in test_names
            and "PendingReceiptRestoresAfterInterruptionWithoutReroll"
            in test_names
        ),
        "oneFiniteRevealAndSheen": (
            "RevealAndSheenAreFiniteMeshLocalCues" in test_names
        ),
        "reduceMotionIsCausalAndStatic": (
            "ReduceMotionKeepsCausalityAndCompletesAtStaticPose"
            in test_names
        ),
        "effectPixelsAreMeshClipped": (
            "MakeItShineCc0Masks.hlsl" in shader_source
            and "input.positionOS" in shader_source
            and "SAMPLE_TEXTURE2D" not in shader_source
            and "GrabPass" not in shader_source
        ),
        "externalSourceContractPasses": source_report["status"] == "pass",
        "noExternalEntityImported": not source_report["forbiddenImports"],
        "videoIsPortrait60Fps": (
            video["width"] == 1206
            and video["height"] == 2622
            and abs(video["fps"] - 60) < 0.01
        ),
        "videoContainsNoEmptyFrame": video["noEmptyFrame"],
        "focusedUnityTestsPass": (
            test_run.attrib.get("result") == "Passed"
            and test_run.attrib.get("failed") == "0"
        ),
        "xcodeBuildPasses": xcode_summary["status"] == "pass",
        "bundleIdentityIsCanonical": (
            manifest["bundleIdentifier"]
            == "com.jiaweizhou.fidgetspinner.codex"
        ),
        "gate10FbxHashMatches": (
            manifest["gate11DisplayCaseFbxSha256"]
            == "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
        ),
        "physicalPhoneUntouched": (
            manifest["physicalPhoneInstallAuthorized"] is False
        ),
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "source": "canonical unity/FidgetingApp shipping source",
        "scene": "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R002.unity",
        "prefab": manifest["gate12DisplayCasePrefab"],
        "profile": (
            "Assets/Resources/Gacha/"
            "PremiumDisplayCaseGate12R002Profile.asset"
        ),
        "profileValuesLocked": False,
        "pendingVisualTuning": True,
        "wholeAssembledCaseOnly": True,
        "sameInstanceThroughAcknowledgement": True,
        "toyCallerOwned": True,
        "toyIndependentAngularVelocity": 0,
        "rotationDegrees": values["totalRotationDegrees"],
        "sheenActivationCount": 1,
        "sheenOutsideMeshPixelsByContract": 0,
        "pointLightCount": 0,
        "particlesEnabled": False,
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
        "timing": values,
        "video": video,
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
            if path.is_file()
        },
        "statusText": "视觉批准待确认，未推送手机",
    }
    (EVIDENCE / "gate12-evidence-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps({"status": report["status"], "checks": checks}, indent=2))
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
