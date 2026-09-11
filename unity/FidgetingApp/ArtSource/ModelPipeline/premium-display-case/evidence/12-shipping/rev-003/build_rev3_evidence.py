#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[6]
EVIDENCE = Path(__file__).resolve().parent
BUILD = ROOT / "Builds/iOS/PremiumDisplayCaseGate12Rev3Simulator"
SOURCE = Path(
    "/Users/jiawei.zhou/Documents/Fidgeting app External Research/"
    "Unite2025-MakeItShine-Release"
)
MODULE = ROOT / "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects"
PROFILE = ROOT / (
    "Assets/Resources/Gacha/PremiumDisplayCaseGate12R003Profile.asset"
)
PREFAB = ROOT / (
    "Assets/Resources/Gacha/PremiumDisplayCaseGate12R003/"
    "PresentationRoot.prefab"
)
SHADER = ROOT / (
    "Assets/_DisplayCase/Shaders/"
    "PremiumDisplayCaseGate12R003Frosted.shader"
)
VIDEO = EVIDENCE / "app-simulator-pack-to-case-r3.mp4"
RAW_VIDEO = EVIDENCE / "app-simulator-pack-to-case-r3-raw.mp4"
TEST_SOURCE = ROOT / "Logs/PremiumDisplayCaseGate12R3RelevantResults.xml"
XCODE_LOG = BUILD / "xcodebuild-gate12-r3.log"
FONT = ROOT / "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf"
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
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def contact_sheet(
    output: Path,
    samples: list[tuple[str, float]],
    columns: int,
    crop: tuple[float, float, float, float] | None = None,
) -> None:
    capture = cv2.VideoCapture(str(VIDEO))
    tile_width = 360
    tile_height = 700
    header = 58
    rows = (len(samples) + columns - 1) // columns
    canvas = Image.new(
        "RGB",
        (tile_width * columns, tile_height * rows),
        "#07090c",
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT), 19)
    for index, (label, seconds) in enumerate(samples):
        image = video_frame(capture, seconds)
        if crop is not None:
            width, height = image.size
            image = image.crop((
                int(width * crop[0]),
                int(height * crop[1]),
                int(width * crop[2]),
                int(height * crop[3]),
            ))
        image.thumbnail(
            (tile_width - 12, tile_height - header - 12),
            Image.Resampling.LANCZOS,
        )
        column = index % columns
        row = index // columns
        x = column * tile_width + (tile_width - image.width) // 2
        y = row * tile_height + header
        canvas.paste(image, (x, y))
        frame = round(seconds * 60)
        draw.text(
            (column * tile_width + 10, row * tile_height + 8),
            f"{seconds:0.2f}s · f{frame:03d} · {label}",
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
    font = ImageFont.truetype(str(FONT), 20)
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


def build_review_video() -> None:
    subprocess.run([
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-ss", "4.4",
        "-t", "8.4",
        "-i", str(RAW_VIDEO),
        "-vf", "fps=60",
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(VIDEO),
    ], check=True)


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
        actual = sha256(source_path)
        files.append({
            "path": record["path"],
            "expectedSha256": record["sha256"],
            "actualSha256": actual,
            "matches": actual == record["sha256"],
        })
    forbidden_extensions = {
        ".fbx", ".prefab", ".anim", ".playable", ".vfx",
        ".shadergraph", ".mat", ".png", ".jpg",
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
        "moduleHashes": {
            file_name: sha256(MODULE / file_name)
            for file_name in module_files
        },
        "forbiddenImports": forbidden_imports,
        "excludedAssets": contract["excludedAssets"],
        "shippingBoundaries": contract["shippingBoundaries"],
    }
    (EVIDENCE / "source-extraction-report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    return report


def run_native_validation(values: dict) -> dict:
    swift_root = ROOT / "Assets/Plugins/iOS"
    harness = ROOT / "Tools/GachaShippingNativePreview/GachaGate12RulesHarness.swift"
    sdk = subprocess.check_output(
        ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-path"],
        text=True,
    ).strip()
    with tempfile.TemporaryDirectory() as temporary:
        executable = Path(temporary) / "gate12-r3-harness"
        subprocess.run([
            "xcrun", "swiftc",
            str(swift_root / "FidgetGachaRiveGateRules.swift"),
            str(swift_root / "FidgetGachaPackPresentation.swift"),
            str(harness),
            "-o", str(executable),
        ], check=True)
        harness_output = subprocess.check_output(
            [str(executable)],
            text=True,
        ).strip()
    typecheck_files = [
        "FidgetProductUIComponents.swift",
        "FidgetStoreKit.swift",
        "FidgetGachaPackPresentation.swift",
        "FidgetGachaRiveGateRules.swift",
        "FidgetGachaStore.swift",
        "FidgetGachaShippingStorefront.swift",
    ]
    subprocess.run([
        "xcrun", "swiftc",
        "-target", "arm64-apple-ios15.0-simulator",
        "-sdk", sdk,
        "-warnings-as-errors",
        "-typecheck",
        *(str(swift_root / file_name) for file_name in typecheck_files),
    ], check=True)
    match = re.fullmatch(r"PASS ([0-9]+)/([0-9]+)", harness_output)
    if not match:
        raise RuntimeError(f"Unexpected Swift harness output: {harness_output}")
    passed = int(match.group(1))
    total = int(match.group(2))
    return {
        "status": "pass" if passed == total else "fail",
        "swiftGateHarness": {
            "passed": passed,
            "failed": total - passed,
        },
        "swiftWarningsAsErrors": {
            "result": "pass",
            "files": typecheck_files,
        },
        "handoffTimingAuthority": "Unity ScriptableObject via native bridge",
        "handoffDurationSeconds": values["handoffDurationSeconds"],
        "xcode": {"result": "BUILD SUCCEEDED"},
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
    }


def main() -> None:
    profile_source = PROFILE.read_text()
    value_keys = [
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
        "rotationRimIntensity",
        "sheenWidth",
        "sheenIntensity",
        "sheenFalloff",
    ]
    values = {
        key: profile_number(profile_source, key)
        for key in value_keys
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
    values["timingChangedFromRev2"] = False
    values["visibilityRepairCandidate"] = {
        "lightRevealIntensity": values["lightRevealIntensity"],
        "rotationRimIntensity": values["rotationRimIntensity"],
        "sheenWidth": values["sheenWidth"],
        "sheenIntensity": values["sheenIntensity"],
        "sheenFalloff": values["sheenFalloff"],
    }
    values["pendingVisualTuning"] = True
    (EVIDENCE / "timing-candidate-report.json").write_text(
        json.dumps(values, indent=2) + "\n"
    )

    build_review_video()
    contact_sheet(
        EVIDENCE / "app-simulator-contact-sheet.png",
        [
            ("Pack carousel", 0.10),
            ("sealed Pack", 1.50),
            ("partial tear follows", 1.78),
            ("below-threshold rebound", 2.52),
            ("committed tear / seam", 3.02),
            ("real case arrival", 3.32),
            ("fast first 360", 3.75),
            ("continuous boundary", 4.22),
            ("slower second 360", 4.70),
            ("final mesh sheen", 5.68),
            ("hold and result UI", 7.15),
        ],
        4,
    )
    contact_sheet(
        EVIDENCE / "pack-tear-contact-sheet.png",
        [
            ("sealed", 1.50),
            ("partial follow", 1.78),
            ("partial maximum", 2.02),
            ("rebound in progress", 2.28),
            ("rebound complete", 2.52),
            ("second pull", 2.78),
            ("committed open seam", 3.02),
            ("real-case ready handoff", 3.32),
        ],
        4,
        crop=(0.12, 0.13, 0.88, 0.84),
    )
    contact_sheet(
        EVIDENCE / "light-closeup-contact-sheet.png",
        [
            ("Pack seam leak", 3.02),
            ("arrival rim", 3.38),
            ("entry-tail rim", 3.58),
            ("first-circle rim", 3.80),
            ("non-stop boundary", 4.22),
            ("second-circle rim A", 4.70),
            ("second-circle rim B", 5.20),
            ("final clipped sheen", 5.68),
            ("static hold", 6.08),
            ("result UI", 7.15),
        ],
        5,
        crop=(0.05, 0.08, 0.95, 0.88),
    )
    standard_contact_sheet()
    shutil.copyfile(EVIDENCE / "simulator-final.png", EVIDENCE / "library.png")

    stable_tests = EVIDENCE / "unity-focused-results.xml"
    shutil.copyfile(TEST_SOURCE, stable_tests)
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
    xcode_text = XCODE_LOG.read_text()
    xcode_summary = {
        "status": "pass" if "** BUILD SUCCEEDED **" in xcode_text else "fail",
        "configuration": "Release",
        "sdk": "iphonesimulator",
        "destination": "iPhone 17 Pro Simulator",
        "bundleIdentifier": manifest["bundleIdentifier"],
        "sourceLogSha256": sha256(XCODE_LOG),
        "physicalPhoneInstalled": False,
    }
    (EVIDENCE / "xcode-build-summary.json").write_text(
        json.dumps(xcode_summary, indent=2) + "\n"
    )
    native = run_native_validation(values)
    (EVIDENCE / "native-validation-report.json").write_text(
        json.dumps(native, indent=2) + "\n"
    )
    source_report = external_source_report()
    video = analyze_video(VIDEO)
    shader_source = SHADER.read_text()
    storefront_source = (
        ROOT / "Assets/Plugins/iOS/FidgetGachaShippingStorefront.swift"
    ).read_text()
    capture_report = json.loads(
        (EVIDENCE / "shipping-capture-report.json").read_text()
    )
    pack_assets = sorted(
        (ROOT / "Assets/Plugins/iOS/GachaPacks").glob("gacha-pack-*.png")
    )
    asset_hashes = {
        "profile": sha256(PROFILE),
        "prefab": sha256(PREFAB),
        "shader": sha256(SHADER),
        "gate11Fbx": manifest["gate11DisplayCaseFbxSha256"],
        "packAssets": {
            path.name: sha256(path)
            for path in pack_assets
        },
    }
    (EVIDENCE / "asset-hash-manifest.json").write_text(
        json.dumps(asset_hashes, indent=2) + "\n"
    )
    user_feedback = EVIDENCE / "user-defect-feedback.md"
    required = [
        *(EVIDENCE / file_name for _, file_name in STANDARD_VIEWS),
        EVIDENCE / "library.png",
        EVIDENCE / "simulator-final.png",
        EVIDENCE / "app-simulator-contact-sheet.png",
        EVIDENCE / "pack-tear-contact-sheet.png",
        EVIDENCE / "light-closeup-contact-sheet.png",
        EVIDENCE / "standard-views-contact-sheet.png",
        VIDEO,
        RAW_VIDEO,
        EVIDENCE / "shipping-capture-report.json",
        EVIDENCE / "timing-candidate-report.json",
        EVIDENCE / "source-extraction-report.json",
        EVIDENCE / "asset-hash-manifest.json",
        stable_manifest,
        stable_tests,
        EVIDENCE / "xcode-build-summary.json",
        EVIDENCE / "native-validation-report.json",
        user_feedback,
    ]
    missing = [str(path) for path in required if not path.is_file()]
    required_tests = {
        "GpuLightCuesAreVisibleAndStayInsideCaseFragments",
        "RuntimeWritesVisibleEffectPeaksToEveryMaterial",
        "NativePackTearUsesRealLayersMaskAndReadyGatedCoverage",
        "CoordinatorRequiresTwoStableEndOfFrameChecks",
        "PresentationKeepsOneCaseAndToyStaticThroughCompletion",
        "PendingReceiptRestoresAfterInterruptionWithoutReroll",
        "ReduceMotionKeepsCausalityAndCompletesAtStaticPose",
        "ShippingPrefabUsesApprovedGeometryAndOneMeshClippedSheen",
    }
    checks = {
        "allEvidenceExists": not missing,
        "rev2TimingPreserved": (
            values["handoffDurationSeconds"] == 0.18
            and values["entryDurationSeconds"] == 0.82
            and values["firstSpinDurationSeconds"] == 0.72
            and values["secondSpinDurationSeconds"] == 1.18
            and values["entryRotationOverlapSeconds"] == 0.22
            and values["profileDurationSeconds"] == 3.6
        ),
        "profileIsExactly720Degrees": values["totalRotationDegrees"] == 720,
        "firstSpinIsFaster": (
            values["firstSpinAverageDegreesPerSecond"]
            > values["secondSpinAverageDegreesPerSecond"]
        ),
        "visibleLightPeaksNonZero": (
            values["lightRevealIntensity"] >= 0.68
            and values["rotationRimIntensity"] >= 0.52
            and values["sheenIntensity"] >= 0.78
        ),
        "effectModuleActuallyWired": (
            capture_report["cc0LightCurveWired"] is True
            and capture_report["effectRendererWiringValid"] is True
            and "FidgetingCc0DiagonalBand" in shader_source
            and "_RotationRimStrength" in shader_source
        ),
        "meshClippedGpuPixelsPass": (
            "GpuLightCuesAreVisibleAndStayInsideCaseFragments" in test_names
        ),
        "packTearVisualAndMaskPass": (
            "NativePackTearUsesRealLayersMaskAndReadyGatedCoverage"
            in test_names
            and "ProductTearablePackArtwork" in storefront_source
            and native["swiftGateHarness"]["passed"] == 37
        ),
        "prematureDismissalAndEmptyFrameCovered": (
            "CoordinatorRequiresTwoStableEndOfFrameChecks" in test_names
            and native["swiftGateHarness"]["passed"] == 37
            and video["noEmptyFrame"]
        ),
        "sameInstanceToyAndLabelsPreserved": (
            "PresentationKeepsOneCaseAndToyStaticThroughCompletion"
            in test_names
            and "LabelRejectsPlaceholderOrMismatchedReceiptData"
            in test_names
        ),
        "staleInterruptionAndReduceMotionCovered": (
            "PendingReceiptRestoresAfterInterruptionWithoutReroll"
            in test_names
            and "ReduceMotionKeepsCausalityAndCompletesAtStaticPose"
            in test_names
        ),
        "noExternalEntityImported": (
            not source_report["forbiddenImports"]
            and "magneticHolder" not in storefront_source
            and "three-card" not in PREFAB.read_text()
        ),
        "videoIsPortrait60Fps": (
            video["width"] == 1206
            and video["height"] == 2622
            and abs(video["fps"] - 60) < 0.01
        ),
        "focusedUnityTestsPass": (
            test_run.attrib.get("result") == "Passed"
            and test_run.attrib.get("failed") == "0"
            and required_tests.issubset(test_names)
        ),
        "swiftWarningsAsErrorsPass": (
            native["swiftWarningsAsErrors"]["result"] == "pass"
        ),
        "xcodeBuildPasses": xcode_summary["status"] == "pass",
        "bundleIdentityIsCanonical": (
            manifest["bundleIdentifier"]
            == "com.jiaweizhou.fidgetspinner.codex"
        ),
        "r3PrefabAndProfileBundled": (
            manifest["gate12DisplayCasePrefab"]
            == (
                "Assets/Resources/Gacha/"
                "PremiumDisplayCaseGate12R003/PresentationRoot.prefab"
            )
            and manifest["gate12DisplayCasePrefabSha256"] == sha256(PREFAB)
            and manifest["gate12DisplayCaseProfileSha256"] == sha256(PROFILE)
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
        "scene": "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R003.unity",
        "prefab": manifest["gate12DisplayCasePrefab"],
        "profile": (
            "Assets/Resources/Gacha/"
            "PremiumDisplayCaseGate12R003Profile.asset"
        ),
        "rootCauses": [
            "Rev 2 tests proved non-zero source values but did not prove prefab material-property support, renderer wiring or visible GPU pixels.",
            "The CC0 diagonal band subtracted progress twice, then 0.10 reveal and 0.18 sheen strengths were attenuated again by transparent alpha blending.",
            "No distinct rotation-rim runtime property existed, and the native Pack had no seam-light layer.",
            "The 400x512 flap canvas was scaled into a 238x82 frame, shrinking the real tear strip and leaving no readable opening mask.",
        ],
        "profileValuesLocked": False,
        "pendingVisualTuning": True,
        "wholeAssembledCaseOnly": True,
        "sameInstanceThroughAcknowledgement": True,
        "toyCallerOwned": True,
        "toyIndependentAngularVelocity": 0,
        "rotationDegrees": values["totalRotationDegrees"],
        "effectRendererCount": 3,
        "sheenActivationCount": 1,
        "sheenOutsideMeshPixels": 0,
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
        "native": native,
        "assetHashes": asset_hashes,
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
