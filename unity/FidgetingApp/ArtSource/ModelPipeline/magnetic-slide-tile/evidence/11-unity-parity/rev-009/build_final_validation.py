#!/usr/bin/env python3
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


REPO = Path(__file__).resolve().parents[8]
EVIDENCE = Path(__file__).resolve().parent
CANDIDATE = REPO / "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R009"
IMPORTED = CANDIDATE / "Imported"


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    unity_report = json.loads((EVIDENCE / "unity-import-parity-report.json").read_text())
    parity_report = json.loads((EVIDENCE / "parity-report.json").read_text())
    results_path = EVIDENCE / "editmode-results.xml"
    test_summary = {
        "exists": results_path.exists(),
        "total": 0,
        "passed": 0,
        "failed": 0,
    }
    if results_path.exists():
        root = ET.parse(results_path).getroot()
        test_summary.update(
            total=int(root.attrib.get("total", 0)),
            passed=int(root.attrib.get("passed", 0)),
            failed=int(root.attrib.get("failed", 0)),
        )

    hashes = {
        "renderFbx": (
            IMPORTED / "magnetic-slide-tile-render-r009.fbx",
            "d15e5c944e10ac61d466668309a2ae3f1069870d3c690b67bfd5595af5e32179",
        ),
        "collisionFbx": (
            IMPORTED / "magnetic-slide-tile-collision-r009.fbx",
            "b14ea11d8d08d6ff6d5583ccee0a29c6a219247ed7f7bc16182b1f7e0970851b",
        ),
        "environmentExr": (
            IMPORTED / "Environment/magnetic-slide-tile-shipping-studio-r008.exr",
            "7f1c9fded84c453efbc5300a6a71fe2948534055d3f4ae5052696909f30be6ab",
        ),
        "upperArtworkMask": (
            IMPORTED / "Textures/upperArtworkMask.png",
            "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36",
        ),
        "lowerArtworkMask": (
            IMPORTED / "Textures/lowerArtworkMask.png",
            "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2",
        ),
        "perimeterMask": (
            IMPORTED / "Textures/perimeterMask.png",
            "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc",
        ),
    }
    hash_results = {
        name: {
            "path": str(path.relative_to(REPO)),
            "expected": expected,
            "actual": sha256(path),
            "pass": sha256(path) == expected,
        }
        for name, (path, expected) in hashes.items()
    }

    texture_paths = sorted((IMPORTED / "Textures").glob("*.png"))
    texture_dimensions = {
        path.name: list(Image.open(path).size) for path in texture_paths
    }
    crystal_shader = (CANDIDATE / "Shaders/MagneticSlideTileCrystal.shader").read_text()
    silver_shader = (CANDIDATE / "Shaders/MagneticSlideTileSilver.shader").read_text()
    video = EVIDENCE / "unity-gate11-r009-interactive-review.mp4"
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration,size",
                "-show_entries",
                "stream=width,height,nb_frames",
                "-of",
                "json",
                str(video),
            ],
            text=True,
        )
    )

    expected_names = sorted(
        [
            "BottomExterior",
            "FixedAxisBoss",
            "RotatingCarrierBody",
            "CarrierFollowerLeft",
            "CarrierFollowerRight",
            "BallCandidateLeft",
            "BallCandidateRight",
            "MovingTopBody",
        ]
    )
    checks = {
        "unityImportReport": unity_report["pass"],
        "bounds": all(
            abs(actual - expected) <= 0.00001
            for actual, expected in zip(
                unity_report["sortedBoundsMeters"], [0.012, 0.031, 0.050]
            )
        ),
        "renderCounts": unity_report["renderMeshCount"] == 8
        and unity_report["renderTriangleCount"] == 99280
        and unity_report["renderVertexCount"] == 80102,
        "renderHierarchy": unity_report["renderMeshNames"] == expected_names,
        "collision": unity_report["collisionMeshCount"] == 2
        and unity_report["collisionTriangleCounts"] == [108, 108],
        "mechanismNames": unity_report["fixedAxisFound"]
        and unity_report["fourGroovesFound"],
        "motionMetadata": unity_report["detentCount"] == 30
        and unity_report["detentStepDegrees"] == 12
        and abs(unity_report["maximumTravelMeters"] - 0.018076433) < 1e-8,
        "provisionalDimensions": unity_report["provisionalDimensions"],
        "shippingSceneUnchanged": not unity_report["shippingSceneModified"]
        and unity_report["shippingSceneHashBefore"]
        == unity_report["shippingSceneHashAfter"],
        "sourceHashes": all(item["pass"] for item in hash_results.values()),
        "npotPreserved": len(texture_dimensions) == 11
        and all(size == [620, 1000] for size in texture_dimensions.values()),
        "crystalShader": "GlossyEnvironmentReflection" in crystal_shader
        and "_ArtworkMask" in crystal_shader
        and "_PerimeterMask" in crystal_shader
        and "_Iridescence" in crystal_shader
        and "_CoatStrength" in crystal_shader
        and "_Emission" not in crystal_shader,
        "silverShader": "GlossyEnvironmentReflection" in silver_shader
        and "_Emission" not in silver_shader,
        "materials": len(list((CANDIDATE / "Materials").glob("M_G11R009_*.mat"))) >= 8,
        "parity": parity_report["pass"],
        "interactiveRecording": video.exists()
        and probe["streams"][0]["nb_frames"] == "72"
        and abs(float(probe["format"]["duration"]) - 6.0) < 0.001,
        "focusedTests": test_summary["exists"]
        and test_summary["total"] >= 6
        and test_summary["failed"] == 0,
        "noBuildInstallDevice": not unity_report["buildInstallDevice"],
    }
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 9,
        "hashes": hash_results,
        "textureDimensions": texture_dimensions,
        "video": probe,
        "tests": test_summary,
        "checks": checks,
        "pass": all(checks.values()),
    }
    (EVIDENCE / "final-validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
