#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
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
BUILD = ROOT / "Builds/iOS/PremiumDisplayCaseGate12Rev4Simulator"
SOURCE = Path(
    "/Users/jiawei.zhou/Documents/Fidgeting app External Research/"
    "Unite2025-MakeItShine-Release"
)
MODULE = ROOT / "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects"
PROFILE = ROOT / (
    "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset"
)
PREFAB = ROOT / (
    "Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/"
    "PresentationRoot.prefab"
)
SHADER = ROOT / (
    "Assets/_DisplayCase/Shaders/"
    "PremiumDisplayCaseGate12R004Frosted.shader"
)
VIDEO = EVIDENCE / "app-simulator-pack-to-case-r4.mp4"
RAW_VIDEO = EVIDENCE / "app-simulator-pack-to-case-r4-raw.mp4"
UNITY_RESULTS = EVIDENCE / "unity-focused-results.xml"
XCODE_LOG = BUILD / "xcodebuild-gate12-r4.log"
FONT = ROOT / "Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf"
TRIM_START_SECONDS = 6.10
TRIM_DURATION_SECONDS = 5.65
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


def read_frame(
    capture: cv2.VideoCapture,
    seconds: float,
) -> np.ndarray:
    capture.set(cv2.CAP_PROP_POS_MSEC, seconds * 1000)
    ok, frame = capture.read()
    if not ok:
        raise RuntimeError(f"Could not read video at {seconds:.3f}s")
    return frame


def image_frame(
    capture: cv2.VideoCapture,
    seconds: float,
) -> Image.Image:
    frame = read_frame(capture, seconds)
    return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


def build_review_video() -> None:
    subprocess.run([
        "ffmpeg",
        "-y",
        "-loglevel", "error",
        "-i", str(RAW_VIDEO),
        "-ss", f"{TRIM_START_SECONDS:.3f}",
        "-t", f"{TRIM_DURATION_SECONDS:.3f}",
        "-vf", "fps=60",
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(VIDEO),
    ], check=True)


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
    rows = math.ceil(len(samples) / columns)
    canvas = Image.new(
        "RGB",
        (tile_width * columns, tile_height * rows),
        "#07090c",
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(str(FONT), 19)
    for index, (label, seconds) in enumerate(samples):
        image = image_frame(capture, seconds)
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
        frame_number = round(seconds * 60)
        draw.text(
            (column * tile_width + 10, row * tile_height + 8),
            f"{seconds:0.2f}s · f{frame_number:03d} · {label}",
            fill="white",
            font=font,
        )
    capture.release()
    canvas.save(output)


def build_contact_sheets() -> list[Path]:
    outputs = [
        EVIDENCE / "app-simulator-contact-sheet.png",
        EVIDENCE / "pack-tear-rebound-contact-sheet.png",
        EVIDENCE / "pack-seam-release-contact-sheet.png",
        EVIDENCE / "case-cue-contact-sheet.png",
    ]
    contact_sheet(
        outputs[0],
        [
            ("Pack carousel", 0.10),
            ("sealed Pack", 1.40),
            ("partial tear + seam", 1.70),
            ("rebound sealed", 2.00),
            ("opened before case", 2.55),
            ("release pulse", 2.60),
            ("arrival rim", 2.75),
            ("fast first 360", 3.15),
            ("continuous 360 boundary", 3.45),
            ("slower second 360", 3.85),
            ("second-circle late pass", 4.35),
            ("final crossing sheen", 4.75),
            ("static hold", 5.15),
            ("result UI", 5.58),
        ],
        4,
    )
    contact_sheet(
        outputs[1],
        [
            ("sealed", 1.40),
            ("first pull begins", 1.60),
            ("partial follow", 1.70),
            ("partial maximum", 1.80),
            ("rebound in progress", 1.90),
            ("rebound sealed", 2.00),
            ("second pull", 2.30),
            ("committed opening before case", 2.55),
        ],
        4,
        crop=(0.12, 0.20, 0.88, 0.76),
    )
    contact_sheet(
        outputs[2],
        [
            ("sealed seam", 1.50),
            ("seam ramp begins", 1.60),
            ("seam ramp readable", 1.70),
            ("seam near threshold", 1.80),
            ("open before pulse", 2.55),
            ("release pulse rise", 2.583),
            ("release pulse peak", 2.60),
            ("release pulse decay", 2.65),
        ],
        4,
        crop=(0.18, 0.28, 0.82, 0.51),
    )
    contact_sheet(
        outputs[3],
        [
            ("opened Pack before case", 2.55),
            ("arrival rim", 2.75),
            ("first-circle rim A", 3.05),
            ("first-circle rim B", 3.25),
            ("continuous boundary", 3.45),
            ("second-circle rim A", 3.75),
            ("second-circle rim B", 4.15),
            ("slower second-circle end", 4.50),
            ("final crossing sheen", 4.75),
            ("static hold / no light", 5.15),
        ],
        5,
        crop=(0.05, 0.08, 0.95, 0.88),
    )
    return outputs


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


def video_report(path: Path) -> dict:
    capture = cv2.VideoCapture(str(path))
    fps = float(capture.get(cv2.CAP_PROP_FPS))
    count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    occupancy = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        gray = cv2.cvtColor(
            frame[
                int(height * 0.22):int(height * 0.84),
                int(width * 0.16):int(width * 0.84),
            ],
            cv2.COLOR_BGR2GRAY,
        )
        occupancy.append(float(np.mean(gray > 10)))
    capture.release()
    return {
        "codecContainer": "H.264 MP4",
        "width": width,
        "height": height,
        "fps": fps,
        "frameCount": count,
        "durationSeconds": count / fps if fps else 0,
        "minimumCentralVisibleFraction": min(occupancy) if occupancy else 0,
        "noEmptyFrame": bool(occupancy and min(occupancy) > 0.10),
    }


def pack_components(frame: np.ndarray) -> list[dict]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[700:1850, 150:1050]
    mask = (roi > 15).astype(np.uint8)
    count, _, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        8,
    )
    components = []
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if area < 10000:
            continue
        components.append({
            "areaPixels": area,
            "x": int(stats[index, cv2.CC_STAT_LEFT]) + 150,
            "y": int(stats[index, cv2.CC_STAT_TOP]) + 700,
            "width": int(stats[index, cv2.CC_STAT_WIDTH]),
            "height": int(stats[index, cv2.CC_STAT_HEIGHT]),
            "centerX": float(centroids[index, 0]) + 150,
            "centerY": float(centroids[index, 1]) + 700,
        })
    return sorted(
        components,
        key=lambda component: component["areaPixels"],
        reverse=True,
    )


def grayscale(capture: cv2.VideoCapture, seconds: float) -> np.ndarray:
    return cv2.cvtColor(read_frame(capture, seconds), cv2.COLOR_BGR2GRAY)


def case_side_fraction(gray: np.ndarray) -> float:
    side = np.concatenate([
        gray[1200:2300, 0:200].ravel(),
        gray[1200:2300, 1006:1206].ravel(),
    ])
    return float(np.mean(side > 12))


def visual_regression_report() -> dict:
    capture = cv2.VideoCapture(str(VIDEO))
    sealed_time = 1.40
    partial_time = 1.70
    rebound_time = 2.00
    open_time = 2.55
    release_time = 2.60
    case_first_visible_time = 2.583
    sheen_time = 4.75
    hold_time = 5.30

    sealed = read_frame(capture, sealed_time)
    partial = read_frame(capture, partial_time)
    rebound = read_frame(capture, rebound_time)
    opened = read_frame(capture, open_time)
    release = read_frame(capture, release_time)
    sheen = grayscale(capture, sheen_time)
    hold = grayscale(capture, hold_time)

    partial_components = pack_components(partial)
    open_components = pack_components(opened)
    if len(partial_components) < 2 or len(open_components) < 2:
        raise RuntimeError("Could not separate the authored Pack body and flap.")
    partial_body, partial_flap = partial_components[:2]
    open_body, open_flap = open_components[:2]

    flap_horizontal_travel = abs(
        partial_flap["centerX"] - partial_body["centerX"]
    )
    partial_opening_gap = (
        partial_body["y"]
        - partial_flap["y"]
        - partial_flap["height"]
    )
    committed_opening_gap = (
        open_body["y"] - open_flap["y"] - open_flap["height"]
    )
    flap_width_fraction = (
        partial_flap["width"] / partial_body["width"]
    )
    rebound_roi = np.s_[850:1800, 250:960]
    rebound_mad = float(np.mean(np.abs(
        rebound[rebound_roi].astype(np.int16)
        - sealed[rebound_roi].astype(np.int16)
    )))

    partial_gray = cv2.cvtColor(partial, cv2.COLOR_BGR2GRAY)
    seam_band = partial_gray[
        partial_body["y"] - 15:partial_body["y"] + 15,
        partial_body["x"]:partial_body["x"] + partial_body["width"],
    ]
    seam_median = float(np.median(seam_band))
    seam_p95 = float(np.percentile(seam_band, 95))
    seam_fraction_above_40 = float(np.mean(seam_band > 40))

    open_gray = cv2.cvtColor(opened, cv2.COLOR_BGR2GRAY)
    release_gray = cv2.cvtColor(release, cv2.COLOR_BGR2GRAY)
    release_slice = np.s_[
        open_body["y"] - 53:open_body["y"] - 13,
        open_body["x"]:open_body["x"] + open_body["width"],
    ]
    release_mean_delta = float(
        release_gray[release_slice].mean()
        - open_gray[release_slice].mean()
    )
    release_p95_delta = float(
        np.percentile(release_gray[release_slice], 95)
        - np.percentile(open_gray[release_slice], 95)
    )

    early_case_fractions = []
    for seconds in [1.40, 1.70, 2.00, 2.30, 2.55]:
        early_case_fractions.append(
            case_side_fraction(grayscale(capture, seconds))
        )
    case_visible_fraction = case_side_fraction(
        grayscale(capture, case_first_visible_time)
    )

    transition_occupancy = []
    for index in range(25):
        gray = grayscale(capture, 2.50 + index / 60)
        transition_occupancy.append(float(np.mean(
            gray[700:2200, 200:1006] > 10
        )))

    case_roi = np.s_[650:2150, 120:1086]
    sheen_delta = (
        sheen[case_roi].astype(np.float32)
        - hold[case_roi].astype(np.float32)
    )
    sheen_signed_delta = float(sheen_delta.mean())
    sheen_absolute_delta = float(np.abs(sheen_delta).mean())
    sheen_p95_delta = float(np.percentile(np.abs(sheen_delta), 95))
    sheen_positive_fraction = float(np.mean(sheen_delta > 10))

    late_hold = grayscale(capture, 5.20)[case_roi].astype(np.float32)
    final_hold = hold[case_roi].astype(np.float32)
    persistent_delta = np.abs(late_hold - final_hold)
    capture.release()

    test_run = ET.parse(UNITY_RESULTS).getroot()
    gpu_case = next(
        case
        for case in test_run.iter("test-case")
        if case.attrib.get("name")
        == "GpuLightCuesAreVisibleAndStayInsideCaseFragments"
    )
    output = gpu_case.findtext("output") or ""
    cue_pattern = re.compile(
        r"(?P<name>arrival|first-rotation-rim|second-rotation-rim|final-sheen): "
        r"changed=(?P<changed>[0-9]+), "
        r"fraction=(?P<fraction>[0-9.]+), "
        r"meanLuma=(?P<mean>[0-9.]+), "
        r"p95Luma=(?P<p95>[0-9.]+), "
        r"maxLuma=(?P<maximum>[0-9.]+), "
        r"external=(?P<external>[0-9]+)"
    )
    cues = {}
    for match in cue_pattern.finditer(output):
        cues[match.group("name")] = {
            "changedPixels": int(match.group("changed")),
            "changedFraction": float(match.group("fraction")),
            "meanLumaDelta": float(match.group("mean")),
            "meanLumaDelta255": float(match.group("mean")) * 255,
            "p95LumaDelta": float(match.group("p95")),
            "p95LumaDelta255": float(match.group("p95")) * 255,
            "maximumLumaDelta": float(match.group("maximum")),
            "maximumLumaDelta255": float(match.group("maximum")) * 255,
            "externalPixels": int(match.group("external")),
        }
    required_cues = {
        "arrival",
        "first-rotation-rim",
        "second-rotation-rim",
        "final-sheen",
    }
    if set(cues) != required_cues:
        raise RuntimeError(f"Missing isolated GPU cue metrics: {cues.keys()}")

    checks = {
        "fullWidthAuthoredFlap": flap_width_fraction > 0.82,
        "flapMotionNotTooSmall": flap_horizontal_travel > 75,
        "partialTearOpeningVisible": partial_opening_gap >= 8,
        "committedTearOpeningVisible": committed_opening_gap >= 35,
        "belowThresholdReboundsToSealed": rebound_mad < 2,
        "caseDoesNotAppearBeforeOpening": max(early_case_fractions) < 0.01,
        "caseAppearsAfterOpening": case_visible_fraction > 0.25,
        "transitionNeverEmpty": min(transition_occupancy) > 0.25,
        "seamContrastReadable": (
            seam_p95 - seam_median > 80
            and seam_fraction_above_40 > 0.20
        ),
        "releasePulseContrastReadable": (
            release_mean_delta > 60
            and release_p95_delta > 80
        ),
        "everyCaseCueHasMeasuredContrast": all(
            cue["changedFraction"] > 0.04
            and cue["meanLumaDelta"] > 0.012
            and cue["p95LumaDelta"] > 0.05
            and cue["maximumLumaDelta"] > 0.10
            for cue in cues.values()
        ),
        "finalSheenCrossingVisible": (
            sheen_signed_delta > 15
            and sheen_absolute_delta > 20
            and sheen_p95_delta > 100
            and sheen_positive_fraction > 0.20
        ),
        "allCaseLightStaysMeshClipped": all(
            cue["externalPixels"] == 0
            for cue in cues.values()
        ),
        "noPersistentLight": (
            float(persistent_delta.mean()) < 2
            and float(np.percentile(persistent_delta, 95)) < 6
        ),
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "sampleTimesVideoSeconds": {
            "sealed": sealed_time,
            "partial": partial_time,
            "rebound": rebound_time,
            "committedOpenBeforeCase": open_time,
            "releasePulse": release_time,
            "caseFirstVisible": case_first_visible_time,
            "finalSheen": sheen_time,
            "hold": hold_time,
        },
        "pack": {
            "authoredAspect": "384:512",
            "flapAnchor": "topTrailing",
            "flapWidthVersusBodyFraction": flap_width_fraction,
            "flapHorizontalTravelPixels": flap_horizontal_travel,
            "partialOpeningGapPixels": partial_opening_gap,
            "committedOpeningGapPixels": committed_opening_gap,
            "reboundMeanAbsoluteDelta": rebound_mad,
            "seamP95MinusMedianLuma255": seam_p95 - seam_median,
            "seamFractionAbove40": seam_fraction_above_40,
            "releaseMeanLumaDelta255": release_mean_delta,
            "releaseP95LumaDelta255": release_p95_delta,
            "maximumCaseFractionBeforeOpening": max(early_case_fractions),
            "caseFractionFirstVisible": case_visible_fraction,
            "minimumTransitionForegroundFraction": min(transition_occupancy),
        },
        "caseCuesIsolatedGpu": cues,
        "finalSheenVersusHold": {
            "meanSignedLumaDelta255": sheen_signed_delta,
            "meanAbsoluteLumaDelta255": sheen_absolute_delta,
            "p95AbsoluteLumaDelta255": sheen_p95_delta,
            "fractionPositiveDeltaAbove10": sheen_positive_fraction,
        },
        "persistentLightAfterSheen": {
            "meanAbsoluteLumaDelta255": float(persistent_delta.mean()),
            "p95AbsoluteLumaDelta255": float(
                np.percentile(persistent_delta, 95)
            ),
        },
        "checks": checks,
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
    boundaries = contract["shippingBoundaries"]
    status = (
        current_commit == contract["source"]["commit"]
        and not source_status
        and all(record["matches"] for record in files)
        and not forbidden_imports
        and boundaries["externalModelsImported"] is False
        and boundaries["externalPrefabsImported"] is False
        and boundaries["particlesEnabled"] is False
        and boundaries["vfxGraphDependency"] is False
    )
    return {
        "status": "pass" if status else "fail",
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
        "shippingBoundaries": boundaries,
    }


def run_native_validation(handoff_seconds: float) -> dict:
    swift_root = ROOT / "Assets/Plugins/iOS"
    harness = (
        ROOT / "Tools/GachaShippingNativePreview/GachaGate12RulesHarness.swift"
    )
    sdk = subprocess.check_output(
        ["xcrun", "--sdk", "iphonesimulator", "--show-sdk-path"],
        text=True,
    ).strip()
    with tempfile.TemporaryDirectory() as temporary:
        executable = Path(temporary) / "gate12-r4-harness"
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
        "handoffDurationSeconds": handoff_seconds,
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
    }


def timing_report() -> dict:
    source = PROFILE.read_text()
    keys = [
        "handoffDurationSeconds",
        "entryDurationSeconds",
        "firstSpinDurationSeconds",
        "secondSpinDurationSeconds",
        "entryRotationOverlapSeconds",
        "arrivalRimDurationSeconds",
        "sheenDurationSeconds",
        "holdDurationSeconds",
        "entryYOffsetMeters",
        "entryCameraDepthZMeters",
        "firstSpinDegrees",
        "secondSpinDegrees",
        "lightRevealWidth",
        "lightRevealIntensity",
        "firstRotationRimIntensity",
        "secondRotationRimIntensity",
        "sheenWidth",
        "sheenIntensity",
        "sheenFalloff",
    ]
    values = {key: profile_number(source, key) for key in keys}
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
    values["firstToSecondAverageSpeedRatio"] = (
        values["firstSpinAverageDegreesPerSecond"]
        / values["secondSpinAverageDegreesPerSecond"]
    )
    values["profileValuesLocked"] = False
    values["pendingVisualTuning"] = True
    return values


def test_names(test_run: ET.Element) -> set[str]:
    return {
        case.attrib["name"]
        for case in test_run.iter("test-case")
        if case.attrib.get("result") == "Passed"
    }


def main() -> None:
    required_inputs = [
        RAW_VIDEO,
        UNITY_RESULTS,
        XCODE_LOG,
        BUILD / "FidgetingBuildManifest.json",
        EVIDENCE / "shipping-capture-report.json",
        EVIDENCE / "simulator-final.png",
        EVIDENCE / "diagnosis/rev3-frame-diagnosis.json",
        EVIDENCE / "user-rejection.md",
        PROFILE,
        PREFAB,
        SHADER,
    ]
    missing_inputs = [str(path) for path in required_inputs if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(f"Missing rev 4 inputs: {missing_inputs}")

    timing = timing_report()
    (EVIDENCE / "timing-candidate-report.json").write_text(
        json.dumps(timing, indent=2) + "\n"
    )
    build_review_video()
    contacts = build_contact_sheets()
    standard = standard_contact_sheet()
    shutil.copyfile(EVIDENCE / "simulator-final.png", EVIDENCE / "library.png")

    visual = visual_regression_report()
    (EVIDENCE / "visual-regression-report.json").write_text(
        json.dumps(visual, indent=2) + "\n"
    )
    if visual["status"] != "pass":
        raise RuntimeError(f"Visual regression failed: {visual['checks']}")

    source_report = external_source_report()
    (EVIDENCE / "source-extraction-report.json").write_text(
        json.dumps(source_report, indent=2) + "\n"
    )
    if source_report["status"] != "pass":
        raise RuntimeError("Pinned CC0 source or exclusion contract failed.")

    native = run_native_validation(timing["handoffDurationSeconds"])
    (EVIDENCE / "native-validation-report.json").write_text(
        json.dumps(native, indent=2) + "\n"
    )
    if native["status"] != "pass":
        raise RuntimeError("Native gate validation failed.")

    manifest_source = BUILD / "FidgetingBuildManifest.json"
    stable_manifest = EVIDENCE / "simulator-build-manifest.json"
    shutil.copyfile(manifest_source, stable_manifest)
    manifest = json.loads(stable_manifest.read_text())
    xcode_text = XCODE_LOG.read_text()
    xcode = {
        "status": "pass"
        if "** BUILD SUCCEEDED **" in xcode_text
        else "fail",
        "configuration": "Release",
        "sdk": "iphonesimulator",
        "destination": "iPhone 17 Pro Simulator",
        "touchedSourceWarningsAsErrors": {
            "swiftStandaloneTypecheck": (
                native["swiftWarningsAsErrors"]["result"]
            ),
            "generatedUnityHeadersEscalated": False,
            "reason": (
                "Unity 6000.5 generated umbrella headers emit four "
                "non-modular warnings under global -Werror. Product Swift "
                "is checked separately with -warnings-as-errors."
            ),
        },
        "bundleIdentifier": manifest["bundleIdentifier"],
        "sourceLogSha256": sha256(XCODE_LOG),
        "physicalPhoneInstalled": False,
    }
    (EVIDENCE / "xcode-build-summary.json").write_text(
        json.dumps(xcode, indent=2) + "\n"
    )
    if xcode["status"] != "pass":
        raise RuntimeError("Release Simulator Xcode build failed.")

    capture = json.loads(
        (EVIDENCE / "shipping-capture-report.json").read_text()
    )
    video = video_report(VIDEO)
    test_run = ET.parse(UNITY_RESULTS).getroot()
    passed_tests = test_names(test_run)
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
    pack_assets = sorted(
        (ROOT / "Assets/Plugins/iOS/GachaPacks").glob("gacha-pack-*.png")
    )
    hashes = {
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
        json.dumps(hashes, indent=2) + "\n"
    )

    source_files = [
        ROOT / "Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12Builder.cs",
        ROOT / "Assets/_DisplayCase/Runtime/PremiumDisplayCaseRevealProfile.cs",
        ROOT / (
            "Assets/_DisplayCase/Runtime/"
            "PremiumDisplayCaseShippingPresentation.cs"
        ),
        ROOT / (
            "Assets/_DisplayCase/Runtime/"
            "PremiumDisplayCaseShippingFactory.cs"
        ),
        ROOT / (
            "Assets/Scripts/Product/Gacha/"
            "GachaShippingRevealDirector.cs"
        ),
        ROOT / "Assets/Scripts/Product/FidgetAppCoordinator.cs",
        ROOT / "Assets/Plugins/iOS/FidgetGachaPackPresentation.swift",
        ROOT / "Assets/Plugins/iOS/FidgetProductUIComponents.swift",
        ROOT / "Assets/Plugins/iOS/FidgetGachaShippingStorefront.swift",
        SHADER,
    ]
    required_artifacts = [
        *(EVIDENCE / name for _, name in STANDARD_VIEWS),
        EVIDENCE / "library.png",
        EVIDENCE / "simulator-final.png",
        VIDEO,
        RAW_VIDEO,
        *contacts,
        standard,
        EVIDENCE / "shipping-capture-report.json",
        EVIDENCE / "timing-candidate-report.json",
        EVIDENCE / "visual-regression-report.json",
        EVIDENCE / "source-extraction-report.json",
        EVIDENCE / "asset-hash-manifest.json",
        EVIDENCE / "native-validation-report.json",
        EVIDENCE / "simulator-build-manifest.json",
        EVIDENCE / "xcode-build-summary.json",
        UNITY_RESULTS,
        EVIDENCE / "diagnosis/rev3-frame-diagnosis.json",
        EVIDENCE / "user-rejection.md",
        EVIDENCE / "build_rev4_evidence.py",
        *source_files,
    ]
    missing = [
        str(path)
        for path in required_artifacts
        if not path.is_file()
    ]
    checks = {
        "allEvidenceExists": not missing,
        "rev3RejectionPersistedExactly": (
            "撕包仍然有问题"
            in (EVIDENCE / "user-rejection.md").read_text()
            and "仍然太弱"
            in (EVIDENCE / "user-rejection.md").read_text()
            and "仍需加强蓄力与冲击"
            in (EVIDENCE / "user-rejection.md").read_text()
        ),
        "visualRegressionPasses": (
            visual["status"] == "pass"
            and all(visual["checks"].values())
        ),
        "profileIsExactly720Degrees": (
            timing["totalRotationDegrees"] == 720
        ),
        "firstSpinIsClearlyFaster": (
            timing["firstToSecondAverageSpeedRatio"] >= 2
        ),
        "spinBoundaryHasNoStop": (
            "SpinBoundaryPreservesPositiveAngularVelocity"
            in passed_tests
        ),
        "eventCountsAreExact": (
            "PresentationKeepsOneCaseAndToyStaticThroughCompletion"
            in passed_tests
        ),
        "effectModuleActuallyWired": (
            capture["cc0LightCurveWired"] is True
            and capture["effectRendererWiringValid"] is True
        ),
        "sameInstanceToyAndLabelsPreserved": (
            "PresentationKeepsOneCaseAndToyStaticThroughCompletion"
            in passed_tests
            and "LabelRejectsPlaceholderOrMismatchedReceiptData"
            in passed_tests
        ),
        "staleInterruptionAndReduceMotionCovered": (
            "PendingReceiptRestoresAfterInterruptionWithoutReroll"
            in passed_tests
            and "ReduceMotionKeepsCausalityAndCompletesAtStaticPose"
            in passed_tests
        ),
        "focusedUnityTestsPass": (
            test_run.attrib.get("result") == "Passed"
            and test_run.attrib.get("failed") == "0"
            and required_tests.issubset(passed_tests)
        ),
        "swiftWarningsAsErrorsPass": (
            native["swiftWarningsAsErrors"]["result"] == "pass"
        ),
        "pinnedCc0SourceAndExclusionsPass": (
            source_report["status"] == "pass"
        ),
        "releaseSimulatorBuildPasses": xcode["status"] == "pass",
        "videoIsPortrait60Fps": (
            video["width"] == 1206
            and video["height"] == 2622
            and abs(video["fps"] - 60) < 0.01
        ),
        "videoHasNoEmptyFrame": video["noEmptyFrame"],
        "canonicalBundleIdentity": (
            manifest["bundleIdentifier"]
            == "com.jiaweizhou.fidgetspinner.codex"
        ),
        "rev4PrefabAndProfileBundled": (
            manifest["gate12DisplayCasePrefab"]
            == (
                "Assets/Resources/Gacha/"
                "PremiumDisplayCaseGate12R004/PresentationRoot.prefab"
            )
            and manifest["gate12DisplayCasePrefabSha256"] == sha256(PREFAB)
            and manifest["gate12DisplayCaseProfileSha256"] == sha256(PROFILE)
        ),
        "approvedGate10FbxPreserved": (
            manifest["gate11DisplayCaseFbxSha256"]
            == (
                "21c9db68723f0006d7c6bfec5280cafe"
                "55c16cf5392ff97c365c966e91f847ae"
            )
        ),
        "physicalPhoneUntouched": (
            manifest["physicalPhoneInstallAuthorized"] is False
        ),
    }
    report = {
        "status": "pass" if all(checks.values()) else "fail",
        "source": "canonical unity/FidgetingApp shipping source",
        "scene": "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R004.unity",
        "prefab": manifest["gate12DisplayCasePrefab"],
        "profile": (
            "Assets/Resources/Gacha/"
            "PremiumDisplayCaseGate12R004Profile.asset"
        ),
        "rejectedRevision": 3,
        "rejectionSelections": {
            "packTear": "撕包仍然有问题",
            "light": "仍然太弱",
            "gachaEnergy": "仍需加强蓄力与冲击",
        },
        "rootCauses": json.loads(
            (
                EVIDENCE
                / "diagnosis/rev3-frame-diagnosis.json"
            ).read_text()
        ),
        "profileValuesLocked": False,
        "pendingVisualTuning": True,
        "shippingReady": False,
        "wholeAssembledCaseOnly": True,
        "sameInstanceThroughAcknowledgement": True,
        "toyCallerOwned": True,
        "toyIndependentAngularVelocity": 0,
        "eventCounts": {
            "seam": 1,
            "releasePulse": 1,
            "arrivalRim": 1,
            "rotationRimPasses": 2,
            "finalSheen": 1,
            "persistentLight": 0,
        },
        "pointLightCount": 0,
        "particlesEnabled": False,
        "physicalPhoneInstalled": False,
        "deviceAccepted": False,
        "timing": timing,
        "visualRegression": visual,
        "video": video,
        "unityTests": {
            "total": int(test_run.attrib["total"]),
            "passed": int(test_run.attrib["passed"]),
            "failed": int(test_run.attrib["failed"]),
        },
        "native": native,
        "sourceExtraction": source_report,
        "assetHashes": hashes,
        "checks": checks,
        "missing": missing,
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in required_artifacts
            if path.is_file()
        },
        "statusText": "视觉批准待确认，未推送手机",
    }
    (EVIDENCE / "gate12-evidence-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps({
        "status": report["status"],
        "video": video,
        "visualChecks": visual["checks"],
        "checks": checks,
    }, indent=2))
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
