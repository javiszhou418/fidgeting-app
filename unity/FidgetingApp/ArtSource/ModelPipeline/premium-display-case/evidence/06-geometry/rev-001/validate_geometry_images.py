#!/usr/bin/env python3
"""Validate Premium Display Case Gate 06 image evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
FIXED = ROOT / "fixed-views"
REPORT = ROOT / "geometry-validation.json"
AUDIT = ROOT / "blender-audit.json"
OUTPUT = ROOT / "geometry-image-validation.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_record(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        variance = ImageStat.Stat(rgb.resize((128, 128))).var
        return {
            "path": str(path),
            "sha256": sha256(path),
            "sizeBytes": path.stat().st_size,
            "dimensions": [image.width, image.height],
            "mode": image.mode,
            "channelVariance": [round(value, 6) for value in variance],
            "metadata": {
                key: image.info.get(key)
                for key in (
                    "FidgetEvidenceTruth",
                    "SourceBlendSha256",
                    "GeometryDigest",
                    "Gate",
                    "GeometryRevision",
                    "ShippingRevealPolicy",
                )
                if image.info.get(key) is not None
            },
        }


def main() -> None:
    validation = json.loads(REPORT.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    source_hash = validation["sourceGate05"]["hashesBefore"]["blend"]
    digest = validation["geometryIdentity"]["digestBefore"]
    raw_dimensions = {
        "front": [1400, 1800],
        "back": [1400, 1800],
        "top": [1800, 1000],
        "bottom": [1800, 1000],
        "left": [1000, 1800],
        "right": [1000, 1800],
        "workbench": [1800, 1500],
        "dimensions": [1800, 2000],
        "pivot": [1800, 2000],
        "exploded": [2000, 1600],
    }
    raw_paths = {
        "front": RAW / "front.png",
        "back": RAW / "back.png",
        "top": RAW / "top.png",
        "bottom": RAW / "bottom.png",
        "left": RAW / "left.png",
        "right": RAW / "right.png",
        "workbench": RAW / "workbench.png",
        "dimensions": RAW / "dimension-overlay.png",
        "pivot": RAW / "pivot-axis-overlay.png",
        "exploded": RAW / "exploded-geometry.png",
    }
    annotated_paths = {
        "front": ROOT / "ortho-front.png",
        "back": ROOT / "ortho-back.png",
        "top": ROOT / "ortho-top.png",
        "bottom": ROOT / "ortho-bottom.png",
        "left": ROOT / "ortho-left.png",
        "right": ROOT / "ortho-right.png",
        "workbench": ROOT / "geometry-workbench.png",
        "dimensions": ROOT / "dimension-overlay.png",
        "pivot": ROOT / "pivot-axis-overlay.png",
        "exploded": ROOT / "exploded-geometry.png",
        "review": ROOT / "geometry-review.png",
        "contactSheet": ROOT / "geometry-review-contact-sheet.png",
    }
    missing = [
        str(path)
        for path in (*raw_paths.values(), *annotated_paths.values())
        if not path.exists()
    ]
    if missing:
        raise RuntimeError(f"Missing image evidence: {missing}")
    raw_records = {
        key: image_record(path) for key, path in raw_paths.items()
    }
    annotated_records = {
        key: image_record(path) for key, path in annotated_paths.items()
    }
    standard_view_ids = (
        "front",
        "back",
        "top",
        "bottom",
        "left",
        "right",
        "hero",
        "left-oblique",
        "right-oblique",
        "low",
    )
    standard_paths = {view_id: FIXED / f"{view_id}.png" for view_id in standard_view_ids}
    standard_missing = [
        str(path) for path in standard_paths.values() if not path.exists()
    ]
    if standard_missing:
        raise RuntimeError(f"Missing standard views: {standard_missing}")
    standard_records = {
        key: image_record(path) for key, path in standard_paths.items()
    }
    capture_report = json.loads(
        (FIXED / "capture-report.json").read_text(encoding="utf-8")
    )
    wrapper_report = json.loads(
        (FIXED / "capture-wrapper-report.json").read_text(encoding="utf-8")
    )
    metadata_pass = all(
        record["metadata"] == {
            "FidgetEvidenceTruth": "REAL BLENDER SAME GEOMETRY",
            "SourceBlendSha256": source_hash,
            "GeometryDigest": digest,
            "Gate": "06-geometry",
            "GeometryRevision": "1",
            "ShippingRevealPolicy": "always-assembled-never-explodes",
        }
        for record in annotated_records.values()
    )
    annotated_pairs = {
        key: {
            "rawSha256": raw_records[key]["sha256"],
            "annotatedSha256": annotated_records[key]["sha256"],
            "hashDiffers": raw_records[key]["sha256"] != annotated_records[key]["sha256"],
            "rawDimensions": raw_records[key]["dimensions"],
            "annotatedDimensions": annotated_records[key]["dimensions"],
            "expectedHeightDelta": 292,
            "dimensionDelta": [
                annotated_records[key]["dimensions"][0]
                - raw_records[key]["dimensions"][0],
                annotated_records[key]["dimensions"][1]
                - raw_records[key]["dimensions"][1],
            ],
        }
        for key in raw_paths
    }
    orthographic_hashes = [
        annotated_records[key]["sha256"]
        for key in ("front", "back", "top", "bottom", "left", "right")
    ]
    all_annotated_hashes = [
        record["sha256"] for record in annotated_records.values()
    ]
    checks = {
        "geometryValidationPassed": validation["status"] == "pass",
        "blenderAuditPassed": audit["status"] == "pass",
        "allRawImagesPresent": not missing,
        "allAnnotatedImagesPresent": not missing,
        "rawDimensionsExact": all(
            raw_records[key]["dimensions"] == expected
            for key, expected in raw_dimensions.items()
        ),
        "annotatedDimensionsExpected": all(
            item["dimensionDelta"] == [0, 292]
            for item in annotated_pairs.values()
        ),
        "reviewDimensionsLarge": (
            annotated_records["review"]["dimensions"] == [3600, 3200]
            and annotated_records["contactSheet"]["dimensions"] == [4800, 3600]
        ),
        "rawImagesNonBlank": all(
            max(record["channelVariance"]) > 5.0
            for record in raw_records.values()
        ),
        "annotatedImagesNonBlank": all(
            max(record["channelVariance"]) > 5.0
            for record in annotated_records.values()
        ),
        "rawAndAnnotatedHashesDiffer": all(
            item["hashDiffers"] for item in annotated_pairs.values()
        ),
        "sixOrthographicHashesDistinct": len(set(orthographic_hashes)) == 6,
        "allAnnotatedHashesDistinct": (
            len(set(all_annotated_hashes)) == len(all_annotated_hashes)
        ),
        "embeddedSameGeometryMetadataExact": metadata_pass,
        "standardViewWrapperVerified": (
            wrapper_report["verified_capture"] is True
            and wrapper_report["blender_returncode"] == 0
            and wrapper_report["missing_views"] == []
        ),
        "standardViewsComplete": (
            {view["id"] for view in capture_report["views"]}
            == set(standard_view_ids)
            and not standard_missing
        ),
        "standardCaptureUsesSubjectGeometry": (
            set(capture_report["included_objects"])
            == {
                "RearPolycarbonateShell",
                "TactileBackgroundInsert",
                "FrontPolycarbonateShell",
                "ContinuousTubePerimeter",
                "PhysicalLabel",
            }
        ),
        "sourceHashAndDigestUnchanged": (
            source_hash
            == "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31"
            and digest
            == "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
        ),
        "gate07NotEntered": validation["scope"]["gate07Entered"] is False,
        "shippingUnityUnchanged": validation["scope"]["shippingUnityChanged"] is False,
        "noBuildInstallPhonePush": validation["scope"]["buildInstallPhonePush"] is False,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 1,
        "status": "pass" if all(checks.values()) else "fail",
        "sourceBlendSha256": source_hash,
        "geometryDigest": digest,
        "rawImages": raw_records,
        "annotatedImages": annotated_records,
        "rawAnnotatedComparisons": annotated_pairs,
        "standardViews": standard_records,
        "standardCapture": {
            "runId": capture_report["run_id"],
            "viewIds": [view["id"] for view in capture_report["views"]],
            "wrapperVerified": wrapper_report["verified_capture"],
            "missingViews": wrapper_report["missing_views"],
        },
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": report["status"],
        "review": annotated_records["review"],
        "contactSheet": annotated_records["contactSheet"],
        "orthographicHashesDistinct": len(set(orthographic_hashes)),
        "standardViews": len(standard_records),
    }, ensure_ascii=False, indent=2))
    if report["status"] != "pass":
        raise RuntimeError(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
