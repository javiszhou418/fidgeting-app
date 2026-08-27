#!/usr/bin/env python3
"""Create source-linked anthropometric/video estimates without claiming production measurements."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
SOURCE = HERE / "source-crops"
SCREENSHOTS = [
    Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-7fdf600a-5f50-4c05-b673-3291b6538a63.png"),
    Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-ac92bd48-1d78-4108-ab89-cccf7681d214.png"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def annotate_frame(filename: str, toy: list[list[int]], palm: list[list[int]], state: str) -> dict:
    path = SOURCE / filename
    image = cv2.imread(str(path))
    toy_points = np.float32(toy)
    palm_points = np.float32(palm)
    toy_rect = cv2.minAreaRect(toy_points)
    toy_length_px, toy_width_px = sorted(toy_rect[1], reverse=True)
    palm_breadth_px = float(np.linalg.norm(palm_points[1] - palm_points[0]))
    for points, color in ((toy_points, (20, 220, 255)), (palm_points, (80, 255, 100))):
        for point in points.astype(int):
            cv2.circle(image, tuple(point), 8, color, -1)
    cv2.polylines(image, [cv2.boxPoints(toy_rect).astype(int)], True, (20, 220, 255), 4)
    cv2.line(image, tuple(palm_points[0].astype(int)), tuple(palm_points[1].astype(int)), (80, 255, 100), 4)
    cv2.putText(image, f"{state}: toy/palm same-depth audit", (35, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 3)
    output = SOURCE / filename.replace(".png", "-annotated.png")
    cv2.imwrite(str(output), image)
    hand_breadth_prior = [75.3, 83.8]
    width_ratio = toy_width_px / palm_breadth_px
    length_ratio = toy_length_px / palm_breadth_px
    width_range = [width_ratio * value for value in hand_breadth_prior]
    length_range = [width_range[0] * 1.52, width_range[1] * 1.62]
    return {
        "source": str(path.relative_to(REPO)),
        "annotated": str(output.relative_to(REPO)),
        "state": state,
        "toyLengthPx": round(toy_length_px, 2),
        "toyWidthPx": round(toy_width_px, 2),
        "palmBreadthLandmarkPx": round(palm_breadth_px, 2),
        "lengthToPalmBreadth": round(length_ratio, 4),
        "widthToPalmBreadth": round(width_ratio, 4),
        "estimatedLengthMm": [round(value, 1) for value in length_range],
        "estimatedWidthMm": [round(value, 1) for value in width_range],
        "lengthDerivation": "width estimate × approved perspective-corrected L/W range 1.52–1.62; open pose occludes direct full-length silhouette",
        "errorSources": ["hand-size population prior", "soft-tissue landmark placement", "residual perspective", "toy/palm depth mismatch"],
    }


def main() -> None:
    archived = []
    for index, source in enumerate(SCREENSHOTS, 1):
        target = SOURCE / f"user-rejection-screenshot-{index:02d}.png"
        shutil.copyfile(source, target)
        archived.append({
            "path": str(target.relative_to(REPO)),
            "sha256": sha256(target),
            "interpretation": "Rejected Gate 05 rev 4 evidence: visible circular depression is wrong; required mechanism is a raised independent axis boss.",
        })

    frames = [
        annotate_frame(
            "video-frame-02.png",
            [[412, 116], [550, 18], [688, 218], [541, 350]],
            [[180, 80], [615, 230]],
            "accepted",
        ),
        annotate_frame(
            "video-frame-03.png",
            [[525, 80], [684, 33], [755, 247], [579, 305]],
            [[180, 100], [570, 330]],
            "accepted",
        ),
        annotate_frame(
            "video-frame-01.png",
            [[429, 113], [603, 62], [687, 249], [510, 317]],
            [[146, 40], [726, 395]],
            "rejected-severe-foreshortening-and-motion-blur",
        ),
    ]
    accepted = [frame for frame in frames if frame["state"] == "accepted"]
    length_values = [value for frame in accepted for value in frame["estimatedLengthMm"]]
    width_values = [value for frame in accepted for value in frame["estimatedWidthMm"]]
    report = {
        "schemaVersion": 1,
        "kind": "anthropometric-video-measurement-estimate",
        "modelId": "magnetic-slide-tile",
        "gate": "03-contract",
        "revision": 10,
        "classification": "anthropometric video estimate; not production measured",
        "userAuthorization": {
            "anthropometricAndVideoEstimatesAllowed": True,
            "ballDiameterMm": [2.0, 3.0],
            "trackWidthMm": {"minimum": None, "maximum": 3.0},
        },
        "sources": [
            {
                "title": "AIST Japanese hand anthropometric database",
                "url": "https://www.airc.aist.go.jp/dhrt/hand/index.html",
                "population": "530 healthy Japanese adults, 18–64; 327 male, 203 female",
                "method": "traditional anthropometry; digital calipers except circumference",
            },
            {
                "title": "AIST hand breadth statistics B03",
                "url": "https://www.airc.aist.go.jp/dhrt/hand/data/B.pdf",
                "priorUsedMm": {"P25Combined": 75.3, "P75Combined": 83.8, "meanCombined": 79.8},
            },
            {
                "title": "GB/T 16252-2023 / GB/T 10000-2023 values reproduced in peer-reviewed joystick study",
                "url": "https://doi.org/10.3390/app15063019",
                "crossCheck": "Chinese adult male hand breadth P10/P50/P90 = 82/88/94 mm; not used as the user's sex/percentile is unknown.",
            },
            {
                "title": "Korean hand-shape survey",
                "url": "https://www.sciencedirect.com/science/article/abs/pii/S016981411530041X",
                "population": "321 adults; breadth, palm length and finger length are the three dominant factors",
                "use": "regional shape caution only; no numeric scale imported",
            },
        ],
        "method": {
            "tool": f"OpenCV {cv2.__version__}",
            "landmarks": "manually reviewed palm-breadth endpoints tracked across adjacent frames; toy minAreaRect from four silhouette landmarks",
            "perspective": "accepted only near-open-palm frames where toy and palm share depth; one blurred/foreshortened frame rejected",
            "scale": "toy/palm pixel ratio × AIST combined-sex B03 P25–P75 prior",
            "limitations": "No camera calibration or known-size object shares the toy plane. Results remain range estimates.",
        },
        "frames": frames,
        "exteriorEstimateMm": {
            "overallLength": {"range": [round(min(length_values), 1), round(max(length_values), 1)], "recommendedProvisional": 50.0, "confidence": "medium-low"},
            "overallWidth": {"range": [round(min(width_values), 1), round(max(width_values), 1)], "recommendedProvisional": 31.0, "confidence": "medium-low"},
            "totalThickness": {"range": None, "recommendedProvisional": 12.0, "confidence": "low", "reason": "frontal palm scale cannot constrain thickness"},
        },
        "internalFeatureEstimateMm": {
            "ballDiameter": {"range": [2.0, 3.0], "state": "user-authoritative estimate", "confidence": "medium"},
            "trackWidth": {"range": [1.8, 3.0], "state": "user maximum plus HALOO/NXEDC visible-ratio estimate", "confidence": "low"},
            "trackCenterSpacing": {"range": [5.0, 8.5], "state": "official internal-view pixel ratio", "confidence": "low"},
            "axisOffsetFromNearestEnd": {"range": [14.5, 17.5], "recommendedProvisional": 16.0, "confidence": "low"},
            "carrierDiameter": {"range": [21.0, 26.0], "recommendedProvisional": 23.0, "confidence": "low"},
        },
        "officialInternalPixelRatios": {
            "sourceAssetIds": ["slider-intake-haloo-official-05", "slider-intake-haloo-official-07", "magnetic-slide-tile-official-slider-a-r008", "magnetic-slide-tile-official-slider-b-r008"],
            "ballToOverallWidth": [0.055, 0.082],
            "trackWidthToOverallWidth": [0.058, 0.088],
            "warning": "Perspective, blur and uncertain edge ownership dominate; ratios only support ranges.",
        },
        "remainingUnknowns": [
            "ball material and exact count", "spring count and layout", "groove cross-section and depth",
            "contact preload", "operating clearance", "manufacturing allowance", "manufacturing tolerance",
        ],
        "archivedUserRejectionScreenshots": archived,
    }
    (HERE / "anthropometric-video-measurement-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"acceptedFrames": len(accepted), "lengthMm": report["exteriorEstimateMm"]["overallLength"], "widthMm": report["exteriorEstimateMm"]["overallWidth"]}, indent=2))


if __name__ == "__main__":
    main()
