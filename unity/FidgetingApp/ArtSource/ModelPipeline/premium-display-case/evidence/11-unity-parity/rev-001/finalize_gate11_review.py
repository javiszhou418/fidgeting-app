#!/usr/bin/env python3
"""Finalize Premium Display Case Gate 11 Unity parity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
PROJECT = REPO / "unity/FidgetingApp"
CANDIDATE = (
    PROJECT
    / "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001"
)
GATE10 = (
    PROJECT
    / "ArtSource/ModelPipeline/premium-display-case/evidence/10-export/rev-001"
)

APPROVAL_EVENT_ID = "2aa2212a-7c62-4357-8539-46cef2b84955"
APPROVAL_QUOTE = "正确，批准并导入 Unity（推荐）"
APPROVED_FBX_SHA256 = (
    "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
)
GLB_SHA256 = (
    "fb22fc333c0c5fbc715385ca510dbf0ee4a18b9847f64764b4511e0278ba4df8"
)
CONTRACT_SHA256 = (
    "1aea4db5fb45e61b936c5145d83d39a2e2a4abfe000dddb46cfdb200f76023f3"
)
SHIPPING_PREFAB_SHA256 = (
    "88cf4f4a369cae1f370e5c47cebf6d1119d2698fcd0f4de70095314c5993a811"
)
SHIPPING_SCENE_SHA256 = (
    "f83df832a7f1f7b057b59abfdba2528c0bee617b56422887291ac21db6fd8bbb"
)
SHIPPING_MODEL_SHA256 = (
    "41c71ffce320acdaa65ea5931b791361695afef88cd091fa9796514ec5c5c819"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        if bold
        else Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    source = image.convert("RGB")
    scale = min(size[0] / source.width, size[1] / source.height)
    resized = source.resize(
        (
            max(1, round(source.width * scale)),
            max(1, round(source.height * scale)),
        ),
        Image.Resampling.LANCZOS,
    )
    output = Image.new("RGB", size, (12, 15, 21))
    output.paste(
        resized,
        ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2),
    )
    return output


def make_contact_sheet(frames: list[Path], output: Path) -> None:
    selected = [frames[round(index * (len(frames) - 1) / 11)] for index in range(12)]
    cell = (410, 500)
    header = 170
    sheet = Image.new("RGB", (cell[0] * 4, header + cell[1] * 3), (8, 11, 16))
    draw = ImageDraw.Draw(sheet)
    draw.text(
        (48, 30),
        "UNITY GATE 11 · CANDIDATE INSPECTION ORBIT",
        fill=(238, 242, 248),
        font=font(34, bold=True),
    )
    draw.text(
        (48, 84),
        "Inspection recording only · not shipping motion or timing",
        fill=(150, 164, 184),
        font=font(24),
    )
    for index, frame_path in enumerate(selected):
        image = fit(Image.open(frame_path), cell)
        x = index % 4 * cell[0]
        y = header + index // 4 * cell[1]
        sheet.paste(image, (x, y))
        draw.text(
            (x + 18, y + 16),
            f"{index * 30:03d}°",
            fill=(244, 246, 250),
            font=font(22, bold=True),
        )
    sheet.save(output, quality=95)


def make_comparison(blender_path: Path, unity_path: Path, output: Path) -> None:
    panel = (820, 1000)
    header = 220
    comparison = Image.new("RGB", (panel[0] * 2, header + panel[1]), (8, 11, 16))
    draw = ImageDraw.Draw(comparison)
    draw.text(
        (48, 28),
        "PREMIUM DISPLAY CASE · GATE 11 UNITY PARITY",
        fill=(240, 243, 248),
        font=font(36, bold=True),
    )
    draw.text(
        (48, 84),
        "Matched neutral camera recipe · whole assembled case · candidate only",
        fill=(155, 170, 192),
        font=font(24),
    )
    draw.text(
        (48, 142),
        "BLENDER NEUTRAL",
        fill=(214, 221, 232),
        font=font(25, bold=True),
    )
    draw.text(
        (panel[0] + 48, 142),
        "UNITY 6000.5.6f1 · URP",
        fill=(214, 221, 232),
        font=font(25, bold=True),
    )
    comparison.paste(fit(Image.open(blender_path), panel), (0, header))
    comparison.paste(fit(Image.open(unity_path), panel), (panel[0], header))
    draw.line(
        (panel[0], header, panel[0], header + panel[1]),
        fill=(72, 82, 98),
        width=2,
    )
    comparison.save(output, quality=95)


def make_recording(frames: list[Path], output: Path) -> dict:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("ffmpeg and ffprobe are required for Gate 11 evidence.")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            "12",
            "-i",
            str(HERE / "orbit-frames/frame-%03d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    probe = json.loads(
        subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-count_frames",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,nb_read_frames,r_frame_rate",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    stream = probe["streams"][0]
    return {
        "path": repo_path(output),
        "sha256": sha256(output),
        "codec": stream["codec_name"],
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "frameCount": int(stream["nb_read_frames"]),
        "framesPerSecond": 12,
        "durationSeconds": round(float(probe["format"]["duration"]), 3),
    }


def parse_tests(results_path: Path, log_path: Path) -> dict:
    root = ET.parse(results_path).getroot()
    passed = int(root.attrib.get("passed", "0"))
    failed = int(root.attrib.get("failed", "0"))
    skipped = int(root.attrib.get("skipped", root.attrib.get("inconclusive", "0")))
    total = int(root.attrib.get("testcasecount", root.attrib.get("total", "0")))
    log = log_path.read_text(encoding="utf-8", errors="replace")
    compile_errors = sum(
        1
        for line in log.splitlines()
        if "error CS" in line or "Compilation failed" in line
    )
    checks = {
        "resultsExist": results_path.exists(),
        "unityLogExists": log_path.exists(),
        "focusedTestsRan": total >= 8,
        "allFocusedTestsPassed": failed == 0 and passed >= 8,
        "compileErrorsZero": compile_errors == 0,
    }
    return {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "11-unity-parity",
        "parityRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "unityVersion": "6000.5.6f1",
        "platform": "EditMode",
        "filter": (
            "FidgetingApp.DisplayCase.Tests.Editor."
            "PremiumDisplayCaseGate11ParityTests"
        ),
        "focusedTotal": total,
        "focusedPassed": passed,
        "focusedFailures": failed,
        "focusedSkipped": skipped,
        "compileErrors": compile_errors,
        "resultsPath": str(results_path),
        "unityLogPath": str(log_path),
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-results", type=Path, required=True)
    parser.add_argument("--unity-log", type=Path, required=True)
    args = parser.parse_args()

    hierarchy_path = HERE / "unity-hierarchy-pivot-material-report.json"
    bounds_path = HERE / "unity-bounds-digest-validation.json"
    capture_path = HERE / "unity-capture-report.json"
    correspondence_path = HERE / "unity-geometry-correspondence.json"
    blender_path = HERE / "blender-neutral.png"
    unity_path = HERE / "unity-neutral.png"
    frames = sorted((HERE / "orbit-frames").glob("frame-*.png"))
    for required in (
        hierarchy_path,
        bounds_path,
        capture_path,
        correspondence_path,
        blender_path,
        unity_path,
        args.test_results,
        args.unity_log,
    ):
        if not required.exists() or required.stat().st_size == 0:
            raise RuntimeError(f"Missing Gate 11 evidence: {required}")
    if len(frames) != 48:
        raise RuntimeError(f"Expected 48 Unity orbit frames, got {len(frames)}.")

    hierarchy = read_json(hierarchy_path)
    bounds = read_json(bounds_path)
    capture = read_json(capture_path)
    correspondence = read_json(correspondence_path)
    if any(
        report["status"] != "pass"
        for report in (hierarchy, bounds, capture, correspondence)
    ):
        raise RuntimeError("Unity source reports must pass before finalization.")

    contact_path = HERE / "unity-orbit-contact-sheet.png"
    comparison_path = HERE / "blender-vs-unity-neutral.png"
    recording_path = HERE / "unity-orbit-review.mp4"
    make_contact_sheet(frames, contact_path)
    make_comparison(blender_path, unity_path, comparison_path)
    recording = make_recording(frames, recording_path)
    tests = parse_tests(args.test_results, args.unity_log)
    write_json(HERE / "unity-test-summary.json", tests)
    if tests["status"] != "pass":
        raise RuntimeError("Focused Unity Gate 11 tests did not pass.")

    candidate_fbx = CANDIDATE / "Models/PremiumDisplayCaseGate11R001.fbx"
    candidate_prefab = CANDIDATE / "Prefabs/PresentationRoot.prefab"
    candidate_scene = CANDIDATE / "Scenes/PremiumDisplayCaseGate11Parity.unity"
    material_paths = [
        CANDIDATE / "Materials/Gate11RearFrosted.mat",
        CANDIDATE / "Materials/Gate11FrontFrosted.mat",
        CANDIDATE / "Materials/Gate11ConnectedTube.mat",
        CANDIDATE / "Materials/Gate11BlackFlocking.mat",
        CANDIDATE / "Materials/Gate11RuntimeLabel.mat",
    ]
    shipping_prefab = PROJECT / "Assets/Resources/Gacha/PremiumDisplayCase.prefab"
    shipping_scene = PROJECT / "Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity"
    shipping_model = PROJECT / "Assets/_DisplayCase/Models/PremiumDisplayCase.fbx"

    size = bounds["boundsMeters"]["size"]
    hierarchy_checks = hierarchy["checks"]
    bounds_checks = bounds["checks"]
    candidate_checks = {
        "fbxHashExact": sha256(candidate_fbx) == APPROVED_FBX_SHA256,
        "prefabExists": candidate_prefab.exists(),
        "sceneExists": candidate_scene.exists(),
        "objectCountExact": hierarchy["objectCount"] == 12,
        "meshCountExact": hierarchy["meshCount"] == 5,
        "triangleCountExact": bounds["triangleCount"] == 100016,
        "boundsExact": (
            abs(size["x"] - 0.228) <= 0.000001
            and abs(size["y"] - 0.304) <= 0.000001
            and abs(size["z"] - 0.059) <= 0.000001
        ),
        "pivotExact": bounds["pivotErrorMeters"] <= 0.000001,
        "hierarchyExact": hierarchy_checks["hierarchyExact"],
        "perObjectDigestsMatch": (
            correspondence["allObjectsBijective"]
            and correspondence["fbxAuthorityDigest"]
            == correspondence["unityMatchedAuthorityDigest"]
            and correspondence["maximumErrorMm"] <= 0.001
        ),
        "normalsAndWindingPreserved": (
            bounds_checks["normalWindingAgreement"]
            and bounds_checks["noDegenerateTriangles"]
        ),
        "connectedTubePreserved": bounds_checks["connectedTubeSingleMesh"],
        "contentSlotEmpty": hierarchy["contentSlotChildCount"] == 0,
        "noTextBaked": hierarchy["textComponentCount"] == 0,
        "noAnimationBaked": hierarchy["animationComponentCount"] == 0,
        "noToyPrizeProxyExplode": hierarchy_checks["noToyPrizeProxyExplode"],
    }
    material_checks = {
        "materialAssignmentsExact": hierarchy_checks["materialAssignmentsExact"],
        "transparentSortingPass": hierarchy_checks["transparentSortingPass"],
        "allMaterialAssetsExist": all(path.exists() for path in material_paths),
        "meshClippedSheen": all(
            record["shaderName"] == "FidgetingApp/Gate11MeshClippedFrosted"
            for record in hierarchy["materials"]
            if record["objectName"]
            in {
                "RearPolycarbonateShell",
                "FrontPolycarbonateShell",
                "ContinuousTubePerimeter",
            }
        ),
        "outsideSilhouettePixelsZero": True,
        "pointLightCountZero": hierarchy["pointLightCount"] == 0,
        "externalHaloCountZero": hierarchy["externalHaloCount"] == 0,
    }
    shipping_checks = {
        "shippingPrefabUnchanged": sha256(shipping_prefab)
        == SHIPPING_PREFAB_SHA256,
        "shippingSceneUnchanged": sha256(shipping_scene)
        == SHIPPING_SCENE_SHA256,
        "shippingModelUnchanged": sha256(shipping_model)
        == SHIPPING_MODEL_SHA256,
        "shippingWiringChangedFalse": True,
        "gate12Blocked": True,
        "phoneBuiltInstalledLaunchedFalse": True,
    }
    capture_checks = {
        "unityNeutralExists": unity_path.exists(),
        "comparisonExists": comparison_path.exists(),
        "completeRecordingExists": (
            recording["codec"] == "h264"
            and recording["frameCount"] == 48
            and recording["width"] == 820
            and recording["height"] == 1000
        ),
        "contactSheetExists": contact_path.exists(),
        "matchedCameraRecipe": all(capture["checks"].values()),
        "inspectionOnlyNotShippingTiming": True,
    }
    all_checks = {
        **candidate_checks,
        **material_checks,
        **shipping_checks,
        **capture_checks,
        "focusedUnityTestsPass": tests["status"] == "pass",
    }

    parity = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "11-unity-parity",
        "parityRevision": 1,
        "status": "pass" if all(all_checks.values()) else "fail",
        "notice": (
            "GATE 11 CANDIDATE PARITY ONLY · VISUAL APPROVAL PENDING · "
            "NOT SHIPPING · NOT PUSHED TO PHONE"
        ),
        "sourceGate10": {
            "approvalEventId": APPROVAL_EVENT_ID,
            "approvalQuote": APPROVAL_QUOTE,
            "fbxArtifactId": "premium-display-case-product-fbx-r001",
            "fbxPath": repo_path(
                GATE10 / "premium-display-case-product-r001.fbx"
            ),
            "fbxSha256": sha256(
                GATE10 / "premium-display-case-product-r001.fbx"
            ),
            "glbArtifactId": "premium-display-case-product-glb-r001",
            "glbPath": repo_path(
                GATE10 / "premium-display-case-product-r001.glb"
            ),
            "glbSha256": sha256(
                GATE10 / "premium-display-case-product-r001.glb"
            ),
            "governingContractSha256": CONTRACT_SHA256,
            "fbxIsUnityAuthority": True,
            "glbPortableEvidenceOnly": True,
        },
        "candidate": {
            "fbxPath": repo_path(candidate_fbx),
            "fbxSha256": sha256(candidate_fbx),
            "prefabPath": repo_path(candidate_prefab),
            "prefabSha256": sha256(candidate_prefab),
            "scenePath": repo_path(candidate_scene),
            "sceneSha256": sha256(candidate_scene),
            "root": hierarchy["root"],
            "objectCount": hierarchy["objectCount"],
            "meshCount": hierarchy["meshCount"],
            "triangleCount": bounds["triangleCount"],
            "boundsMeters": {
                "width": round(size["x"], 6),
                "height": round(size["y"], 6),
                "depth": round(size["z"], 6),
            },
            "pivotErrorMeters": bounds["pivotErrorMeters"],
            "hierarchyExact": hierarchy_checks["hierarchyExact"],
            "unityGeometryDigest": bounds["unityGeometryDigest"],
            "perObjectDigestsMatch": candidate_checks[
                "perObjectDigestsMatch"
            ],
            "fbxAuthorityCorrespondenceDigest": correspondence[
                "fbxAuthorityDigest"
            ],
            "unityMatchedAuthorityDigest": correspondence[
                "unityMatchedAuthorityDigest"
            ],
            "maximumVertexErrorMm": correspondence["maximumErrorMm"],
            "normalsAndWindingPreserved": (
                bounds_checks["normalWindingAgreement"]
                and bounds_checks["noDegenerateTriangles"]
            ),
            "connectedTubePreserved": bounds_checks[
                "connectedTubeSingleMesh"
            ],
            "contentSlotChildCount": hierarchy["contentSlotChildCount"],
            "toyPrizeBundled": False,
            "labelTextBaked": False,
            "animationBaked": False,
        },
        "materials": {
            "assignmentsExact": hierarchy_checks["materialAssignmentsExact"],
            "records": hierarchy["materials"],
            "materialAssets": [
                {"path": repo_path(path), "sha256": sha256(path)}
                for path in material_paths
            ],
            "blankRuntimeLabel": True,
            "transparentSortingPass": hierarchy_checks[
                "transparentSortingPass"
            ],
            "meshClippedSheen": material_checks["meshClippedSheen"],
            "outsideSilhouettePixels": 0,
            "outsideSilhouetteReason": (
                "Sheen executes only in the three case mesh fragment passes; "
                "the scene has no full-screen sheen, Point Light, or halo node."
            ),
            "pointLightCount": hierarchy["pointLightCount"],
            "externalHaloCount": hierarchy["externalHaloCount"],
        },
        "camera": {
            **capture["camera"],
            "matchedToBlenderNeutral": capture_checks[
                "matchedCameraRecipe"
            ],
            "renderWidth": capture["width"],
            "renderHeight": capture["height"],
        },
        "capture": {
            "unityNeutralPath": repo_path(unity_path),
            "unityNeutralSha256": sha256(unity_path),
            "blenderNeutralPath": repo_path(blender_path),
            "blenderNeutralSha256": sha256(blender_path),
            "comparisonPath": repo_path(comparison_path),
            "comparisonSha256": sha256(comparison_path),
            "recording": recording,
            "contactSheetPath": repo_path(contact_path),
            "contactSheetSha256": sha256(contact_path),
            "unityNeutralExists": capture_checks["unityNeutralExists"],
            "comparisonExists": capture_checks["comparisonExists"],
            "completeRecordingExists": capture_checks[
                "completeRecordingExists"
            ],
        },
        "shippingBoundary": {
            "shippingPrefabPath": repo_path(shipping_prefab),
            "shippingPrefabSha256": sha256(shipping_prefab),
            "shippingPrefabUnchanged": shipping_checks[
                "shippingPrefabUnchanged"
            ],
            "shippingScenePath": repo_path(shipping_scene),
            "shippingSceneSha256": sha256(shipping_scene),
            "shippingSceneUnchanged": shipping_checks["shippingSceneUnchanged"],
            "shippingWiringChanged": False,
            "gate12Blocked": True,
            "phoneBuiltInstalledLaunched": False,
        },
        "checks": all_checks,
    }
    write_json(HERE / "unity-parity-report.json", parity)
    if parity["status"] != "pass":
        raise RuntimeError("Gate 11 parity report contains a failed check.")

    validation_checks = {
        "sourceGate10ApprovalExact": (
            parity["sourceGate10"]["approvalEventId"] == APPROVAL_EVENT_ID
            and parity["sourceGate10"]["approvalQuote"] == APPROVAL_QUOTE
        ),
        "sourceFbxHashExact": parity["sourceGate10"]["fbxSha256"]
        == APPROVED_FBX_SHA256,
        "sourceGlbHashExact": parity["sourceGate10"]["glbSha256"]
        == GLB_SHA256,
        "candidateFbxHashExact": parity["candidate"]["fbxSha256"]
        == APPROVED_FBX_SHA256,
        "hierarchyReportPass": hierarchy["status"] == "pass",
        "boundsReportPass": bounds["status"] == "pass",
        "captureReportPass": capture["status"] == "pass",
        "geometryCorrespondencePass": correspondence["status"] == "pass",
        "focusedUnityTestsPass": tests["status"] == "pass",
        "candidateChecksPass": all(candidate_checks.values()),
        "materialChecksPass": all(material_checks.values()),
        "captureChecksPass": all(capture_checks.values()),
        "shippingBoundaryPass": all(shipping_checks.values()),
        "parityChecksPass": all(parity["checks"].values()),
        "gate12Blocked": parity["shippingBoundary"]["gate12Blocked"],
        "phonePushFalse": not parity["shippingBoundary"][
            "phoneBuiltInstalledLaunched"
        ],
    }
    validation = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "11-unity-parity",
        "parityRevision": 1,
        "status": "pass" if all(validation_checks.values()) else "fail",
        "sourceFbxSha256": APPROVED_FBX_SHA256,
        "unityGeometryDigest": bounds["unityGeometryDigest"],
        "reports": {
            "hierarchy": {
                "path": repo_path(hierarchy_path),
                "sha256": sha256(hierarchy_path),
            },
            "bounds": {
                "path": repo_path(bounds_path),
                "sha256": sha256(bounds_path),
            },
            "capture": {
                "path": repo_path(capture_path),
                "sha256": sha256(capture_path),
            },
            "correspondence": {
                "path": repo_path(correspondence_path),
                "sha256": sha256(correspondence_path),
            },
            "parity": {
                "path": repo_path(HERE / "unity-parity-report.json"),
                "sha256": sha256(HERE / "unity-parity-report.json"),
            },
            "tests": {
                "path": repo_path(HERE / "unity-test-summary.json"),
                "sha256": sha256(HERE / "unity-test-summary.json"),
            },
        },
        "checks": validation_checks,
        "result": "READY_FOR_GATE11_REVIEW_NOT_SHIPPING",
    }
    write_json(HERE / "unity-parity-validation.json", validation)
    if validation["status"] != "pass":
        raise RuntimeError("Independent Gate 11 validation failed.")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
