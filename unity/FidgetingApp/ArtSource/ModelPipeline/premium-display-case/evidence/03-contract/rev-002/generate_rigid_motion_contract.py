#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageStat


HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE.parents[2]
REPO = next(
    parent
    for parent in HERE.parents
    if (parent / "AGENTS.md").is_file() and (parent / "tools/model-provenance-explorer").is_dir()
)
REV3 = MODEL_DIR / "evidence/02-analysis/rev-003"
PIPELINE_PATH = MODEL_DIR / "pipeline.json"
MEASUREMENTS_PATH = REV3 / "real-rive-motion-measurements.json"
EXTRACT_PATH = REV3 / "rive-authored-motion-extract.json"
REFERENCE_MANIFEST_PATH = REV3 / "reference_manifest.json"
APPROVAL_PATH = REV3 / "user-measured-motion-approval.md"
BLOCKOUT_VALIDATION_PATH = MODEL_DIR / "evidence/05-blockout/rev-002/blockout-validation.json"
HISTORICAL_CONTRACT_PATH = MODEL_DIR / "evidence/03-contract/rev-001/modeling-contract.json"

FIT_PATH = HERE / "rigid-motion-fit.json"
VALIDATION_PATH = HERE / "rigid-motion-fit-validation.json"
CONTRACT_PATH = HERE / "modeling-contract.json"
PREVIEW_PATH = HERE / "contract-preview.png"
POSE_SHEET_PATH = HERE / "rigid-pose-contact-sheet.png"
CURVE_PATH = HERE / "rigid-motion-curves.png"

FRAME_FILES = {
    "START": "00-start-000ms.png",
    "QUARTER": "01-quarter-175ms.png",
    "USER-SCREENSHOT NEAREST": "02-user-nearest-200ms.png",
    "HALF": "03-half-350ms.png",
    "THREE-QUARTER": "04-three-quarter-525ms.png",
    "FRONT → EDGE": "06-turn-front-to-edge-550ms.png",
    "EDGE": "07-edge-600ms.png",
    "REVERSE FACE": "08-reverse-650ms.png",
    "END / FRONT": "05-end-700ms.png",
}

WIDTH_MM = 228.0
HEIGHT_MM = 304.0
DEPTH_MM = 59.0
SOURCE_WIDTH = 968
SOURCE_HEIGHT = 660
SOURCE_DURATION_MS = 3500.0
TARGET_DURATION_MS = 4520.833
TIME_SCALE = TARGET_DURATION_MS / SOURCE_DURATION_MS

BG = "#080B10"
PANEL = "#111821"
PANEL_ALT = "#151E29"
LINE = "#2B3948"
TEXT = "#F2F6F8"
MUTED = "#A9B4C0"
CYAN = "#63D7E5"
MAGENTA = "#FF78C8"
GREEN = "#72D4A6"
AMBER = "#F0BC66"
RED = "#F1777E"
BLUE = "#74A8FF"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        (Path("/System/Library/Fonts/Hiragino Sans GB.ttc"), 1 if bold else 0),
        (Path("/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc"), 0),
        (Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"), 0),
        (Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"), 0),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), 0),
    ]
    for candidate, index in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size, index=index)
    return ImageFont.load_default()


def wrapped_lines(draw: ImageDraw.ImageDraw, text: str, text_font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for character in paragraph:
            candidate = current + character
            if current and draw.textbbox((0, 0), candidate, font=text_font)[2] > width:
                lines.append(current)
                current = character
            else:
                current = candidate
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    width: int,
    spacing: int = 10,
) -> int:
    x, y = xy
    line_height = text_font.size + spacing
    for line in wrapped_lines(draw, text, text_font, width):
        draw.text((x, y), line, font=text_font, fill=fill)
        y += line_height
    return y


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = PANEL) -> None:
    draw.rounded_rectangle(box, radius=26, fill=fill, outline=LINE, width=3)


def polygon_area(points: np.ndarray) -> float:
    x = points[:, 0]
    y = points[:, 1]
    return float(abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) * 0.5)


def edge_roll_degrees(points: np.ndarray) -> float:
    delta = points[1] - points[0]
    return math.degrees(math.atan2(float(delta[1]), float(delta[0])))


def rotation_matrix_to_quaternion_wxyz(matrix: np.ndarray) -> np.ndarray:
    trace = float(np.trace(matrix))
    if trace > 0:
        scale = math.sqrt(trace + 1.0) * 2.0
        quaternion = np.array([
            0.25 * scale,
            (matrix[2, 1] - matrix[1, 2]) / scale,
            (matrix[0, 2] - matrix[2, 0]) / scale,
            (matrix[1, 0] - matrix[0, 1]) / scale,
        ])
    else:
        diagonal = np.diag(matrix)
        index = int(np.argmax(diagonal))
        if index == 0:
            scale = math.sqrt(1.0 + matrix[0, 0] - matrix[1, 1] - matrix[2, 2]) * 2.0
            quaternion = np.array([
                (matrix[2, 1] - matrix[1, 2]) / scale,
                0.25 * scale,
                (matrix[0, 1] + matrix[1, 0]) / scale,
                (matrix[0, 2] + matrix[2, 0]) / scale,
            ])
        elif index == 1:
            scale = math.sqrt(1.0 + matrix[1, 1] - matrix[0, 0] - matrix[2, 2]) * 2.0
            quaternion = np.array([
                (matrix[0, 2] - matrix[2, 0]) / scale,
                (matrix[0, 1] + matrix[1, 0]) / scale,
                0.25 * scale,
                (matrix[1, 2] + matrix[2, 1]) / scale,
            ])
        else:
            scale = math.sqrt(1.0 + matrix[2, 2] - matrix[0, 0] - matrix[1, 1]) * 2.0
            quaternion = np.array([
                (matrix[1, 0] - matrix[0, 1]) / scale,
                (matrix[0, 2] + matrix[2, 0]) / scale,
                (matrix[1, 2] + matrix[2, 1]) / scale,
                0.25 * scale,
            ])
    return quaternion / np.linalg.norm(quaternion)


def rotation_matrix_to_xyz_degrees(matrix: np.ndarray) -> list[float]:
    horizontal = math.sqrt(float(matrix[0, 0] ** 2 + matrix[1, 0] ** 2))
    if horizontal > 1e-7:
        x_angle = math.atan2(float(matrix[2, 1]), float(matrix[2, 2]))
        y_angle = math.atan2(float(-matrix[2, 0]), horizontal)
        z_angle = math.atan2(float(matrix[1, 0]), float(matrix[0, 0]))
    else:
        x_angle = math.atan2(float(-matrix[1, 2]), float(matrix[1, 1]))
        y_angle = math.atan2(float(-matrix[2, 0]), horizontal)
        z_angle = 0.0
    return [math.degrees(x_angle), math.degrees(y_angle), math.degrees(z_angle)]


def object_face_points(face: str) -> np.ndarray:
    half_w = WIDTH_MM / 2.0
    half_h = HEIGHT_MM / 2.0
    half_d = DEPTH_MM / 2.0
    if face == "front":
        return np.array([
            [-half_w, -half_h, -half_d],
            [half_w, -half_h, -half_d],
            [half_w, half_h, -half_d],
            [-half_w, half_h, -half_d],
        ], dtype=np.float64)
    if face == "right-side":
        return np.array([
            [half_w, -half_h, -half_d],
            [half_w, -half_h, half_d],
            [half_w, half_h, half_d],
            [half_w, half_h, -half_d],
        ], dtype=np.float64)
    if face == "back":
        return np.array([
            [half_w, -half_h, half_d],
            [-half_w, -half_h, half_d],
            [-half_w, half_h, half_d],
            [half_w, half_h, half_d],
        ], dtype=np.float64)
    raise ValueError(face)


def camera_matrix(vertical_fov_degrees: float) -> np.ndarray:
    focal = SOURCE_HEIGHT / (2.0 * math.tan(math.radians(vertical_fov_degrees) / 2.0))
    return np.array([
        [focal, 0.0, SOURCE_WIDTH / 2.0],
        [0.0, focal, SOURCE_HEIGHT / 2.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float64)


def solve_pose(points_2d: np.ndarray, face: str, intrinsics: np.ndarray) -> dict[str, Any]:
    points_3d = object_face_points(face)
    distortion = np.zeros(5, dtype=np.float64)
    success, rotation_vectors, translations, _ = cv2.solvePnPGeneric(
        points_3d,
        points_2d,
        intrinsics,
        distortion,
        flags=cv2.SOLVEPNP_IPPE,
    )
    candidates: list[dict[str, Any]] = []
    if success:
        for rotation_vector, translation in zip(rotation_vectors, translations):
            if float(translation[2, 0]) <= 0:
                continue
            rotation_vector, translation = cv2.solvePnPRefineLM(
                points_3d,
                points_2d,
                intrinsics,
                distortion,
                rotation_vector,
                translation,
            )
            projected, _ = cv2.projectPoints(
                points_3d,
                rotation_vector,
                translation,
                intrinsics,
                distortion,
            )
            projected = projected.reshape(-1, 2)
            errors = np.linalg.norm(projected - points_2d, axis=1)
            candidates.append({
                "rotationVector": rotation_vector.reshape(3),
                "translation": translation.reshape(3),
                "projected": projected,
                "errors": errors,
                "squaredError": float(np.sum(errors ** 2)),
            })
    if not candidates:
        success, rotation_vector, translation = cv2.solvePnP(
            points_3d,
            points_2d,
            intrinsics,
            distortion,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not success or float(translation[2, 0]) <= 0:
            raise RuntimeError("No positive-depth pose solution")
        projected, _ = cv2.projectPoints(points_3d, rotation_vector, translation, intrinsics, distortion)
        projected = projected.reshape(-1, 2)
        errors = np.linalg.norm(projected - points_2d, axis=1)
        candidates.append({
            "rotationVector": rotation_vector.reshape(3),
            "translation": translation.reshape(3),
            "projected": projected,
            "errors": errors,
            "squaredError": float(np.sum(errors ** 2)),
        })
    return min(candidates, key=lambda candidate: candidate["squaredError"])


def face_for_label(label: str) -> str:
    if label == "EDGE":
        return "right-side"
    if label == "REVERSE FACE":
        return "back"
    return "front"


def phase_for_milliseconds(milliseconds: float) -> str:
    if milliseconds < 483.333333:
        return "entry-convergence"
    if milliseconds < 600.0:
        return "front-to-edge"
    if milliseconds < 650.0:
        return "edge-to-reverse"
    if milliseconds < 700.0:
        return "reverse-to-front"
    return "front-settle"


def optimize_camera(records: list[dict[str, Any]]) -> tuple[float, np.ndarray]:
    best: tuple[float, float, np.ndarray] | None = None
    for index in range(261):
        vertical_fov = 20.0 + index * 0.25
        intrinsics = camera_matrix(vertical_fov)
        squared_error = 0.0
        for record in records:
            pose = solve_pose(record["cornersArray"], record["visibleFace"], intrinsics)
            squared_error += float(pose["squaredError"])
        candidate = (squared_error, vertical_fov, intrinsics)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise RuntimeError("Camera optimization failed")
    return best[1], best[2]


def fit_motion() -> dict[str, Any]:
    measurements = load_json(MEASUREMENTS_PATH)
    authored = load_json(EXTRACT_PATH)
    reference_manifest = load_json(REFERENCE_MANIFEST_PATH)
    source_records: list[dict[str, Any]] = []
    for frame in measurements["landmarks"]["frames"]:
        source_records.append({
            "label": frame["label"],
            "sourceMilliseconds": float(frame["milliseconds"]),
            "cornersArray": np.array(frame["corners"], dtype=np.float64),
            "sourceCenter": [float(value) for value in frame["center"]],
            "sourceScreenRollDegrees": float(frame["screenRollDegrees"]),
            "sourcePolygonAreaPixels": float(frame["polygonAreaPixels"]),
            "visibleFace": face_for_label(frame["label"]),
            "sourceClipped": any(
                point[1] <= 0 or point[1] >= SOURCE_HEIGHT - 1
                for point in frame["corners"]
            ),
        })

    vertical_fov, intrinsics = optimize_camera(source_records)
    solved: list[dict[str, Any]] = []
    all_errors: list[float] = []
    for record in source_records:
        pose = solve_pose(record["cornersArray"], record["visibleFace"], intrinsics)
        rotation_matrix, _ = cv2.Rodrigues(pose["rotationVector"])
        projected = pose["projected"]
        fitted_center = projected.mean(axis=0)
        errors = pose["errors"]
        all_errors.extend(float(value) for value in errors)
        solved.append({
            **record,
            "rotationMatrix": rotation_matrix,
            "rotationVector": pose["rotationVector"],
            "translation": pose["translation"],
            "projected": projected,
            "errors": errors,
            "fittedCenter": fitted_center,
        })

    end_rotation = solved[-1]["rotationMatrix"]
    end_translation = solved[-1]["translation"]
    end_depth = float(end_translation[2])
    end_area = float(solved[-1]["sourcePolygonAreaPixels"])
    previous_quaternion: np.ndarray | None = None
    samples: list[dict[str, Any]] = []
    for solved_record in solved:
        relative_rotation = end_rotation.T @ solved_record["rotationMatrix"]
        presentation_quaternion = rotation_matrix_to_quaternion_wxyz(relative_rotation)
        if previous_quaternion is not None and float(np.dot(previous_quaternion, presentation_quaternion)) < 0:
            presentation_quaternion = -presentation_quaternion
        previous_quaternion = presentation_quaternion
        absolute_quaternion = rotation_matrix_to_quaternion_wxyz(solved_record["rotationMatrix"])
        translation = solved_record["translation"]
        relative_translation = translation - end_translation
        errors = solved_record["errors"]
        source_ms = float(solved_record["sourceMilliseconds"])
        samples.append({
            "label": solved_record["label"],
            "phase": phase_for_milliseconds(source_ms),
            "sourceMilliseconds": round(source_ms, 6),
            "contractMilliseconds": round(source_ms * TIME_SCALE, 6),
            "visibleFaceEvidence": solved_record["visibleFace"],
            "sourceCornersPixels": np.round(solved_record["cornersArray"], 6).tolist(),
            "fittedCornersPixels": np.round(solved_record["projected"], 6).tolist(),
            "sourceCenterPixels": np.round(solved_record["sourceCenter"], 6).tolist(),
            "fittedCenterPixels": np.round(solved_record["fittedCenter"], 6).tolist(),
            "centerResidualPixels": round(float(np.linalg.norm(
                solved_record["fittedCenter"] - np.array(solved_record["sourceCenter"])
            )), 6),
            "sourceScreenRollDegrees": round(float(solved_record["sourceScreenRollDegrees"]), 6),
            "fittedScreenRollDegrees": round(edge_roll_degrees(solved_record["projected"]), 6),
            "presentationQuaternionWxyz": np.round(presentation_quaternion, 9).tolist(),
            "diagnosticObjectToCameraQuaternionWxyz": np.round(absolute_quaternion, 9).tolist(),
            "diagnosticTranslationCameraMm": np.round(translation, 6).tolist(),
            "translationRelativeToSettledCameraMm": np.round(relative_translation, 6).tolist(),
            "presentationEulerDecompositionDegrees": {
                key: round(value, 6)
                for key, value in zip(
                    ["pitchX", "yawY", "rollZ"],
                    rotation_matrix_to_xyz_degrees(relative_rotation),
                )
            },
            "uniformScale": 1.0,
            "cameraFramingScaleRelativeToSettled": round(end_depth / float(translation[2]), 9),
            "measuredAreaScaleRelativeToSettled": round(
                math.sqrt(max(float(solved_record["sourcePolygonAreaPixels"]), 1.0) / end_area),
                9,
            ),
            "sourceClipped": bool(solved_record["sourceClipped"]),
            "reprojectionResidualPixels": {
                "perCorner": np.round(errors, 6).tolist(),
                "mean": round(float(np.mean(errors)), 6),
                "rmse": round(float(math.sqrt(np.mean(errors ** 2))), 6),
                "maximum": round(float(np.max(errors)), 6),
            },
        })

    user_points = np.array(measurements["landmarks"]["userScreenshot"]["corners"], dtype=np.float64)
    user_pose = solve_pose(user_points, "front", intrinsics)
    user_errors = user_pose["errors"]
    all_error_array = np.array(all_errors, dtype=np.float64)
    unclipped_errors = np.concatenate([
        solved_record["errors"]
        for solved_record in solved
        if not solved_record["sourceClipped"]
    ])
    focal_pixels = float(intrinsics[0, 0])
    fit = {
        "schema": "premium-display-case-gate03-rigid-motion-fit.v1",
        "modelId": "premium-display-case",
        "gate": "03-contract",
        "contractRevision": 2,
        "status": "pass-with-measured-residuals",
        "sourceTaskId": "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3",
        "sourceFiles": [
            {"path": repo_path(MEASUREMENTS_PATH), "sha256": sha256(MEASUREMENTS_PATH)},
            {"path": repo_path(EXTRACT_PATH), "sha256": sha256(EXTRACT_PATH)},
            {"path": repo_path(REFERENCE_MANIFEST_PATH), "sha256": sha256(REFERENCE_MANIFEST_PATH)},
            {"path": repo_path(APPROVAL_PATH), "sha256": sha256(APPROVAL_PATH)},
        ],
        "box": {
            "dimensionsMm": {"width": WIDTH_MM, "height": HEIGHT_MM, "depth": DEPTH_MM},
            "portraitWidthHeightRatio": 0.75,
            "rigid": True,
            "uniformScaleOnly": True,
            "deformationChannels": 0,
            "motionOwner": "PresentationRoot",
        },
        "cameraAssumptions": {
            "purpose": "diagnostic Rive-quad fit only; not a shipping camera",
            "model": "fixed pinhole",
            "imageSizePixels": [SOURCE_WIDTH, SOURCE_HEIGHT],
            "principalPointPixels": [SOURCE_WIDTH / 2.0, SOURCE_HEIGHT / 2.0],
            "squarePixels": True,
            "skew": 0.0,
            "distortionCoefficients": [0.0, 0.0, 0.0, 0.0, 0.0],
            "verticalFovDegrees": round(vertical_fov, 6),
            "focalLengthPixels": round(focal_pixels, 6),
            "selection": "0.25-degree grid search from 20 to 85 degrees minimizing all-sample corner squared error",
            "shippingCameraRangePreservedForLaterValidationDegrees": [27.0, 31.0],
        },
        "method": {
            "solver": "OpenCV SOLVEPNP_IPPE per visible cuboid face, then solvePnPRefineLM",
            "cameraOptimization": "global least-squares vertical-FOV search",
            "faceEvidence": {
                "front": "START through FRONT → EDGE, plus END / FRONT",
                "right-side": "EDGE",
                "back": "REVERSE FACE",
            },
            "quaternionPolicy": "relative to settled END / FRONT, normalized WXYZ, adjacent sign continuity",
            "translationPolicy": "same rigid cuboid origin in fixed diagnostic camera coordinates",
            "scalePolicy": "physical scale remains 1.0; depth supplies camera framing",
            "exactFitClaimed": False,
            "residualPolicy": "report every corner; clipped source quads remain labeled and are not hidden",
        },
        "timeline": {
            "source": {
                "rootFrames": int(authored["verifiedConclusions"]["rootInFrames"]),
                "fps": int(authored["verifiedConclusions"]["rootFps"]),
                "durationMilliseconds": float(authored["verifiedConclusions"]["rootInDurationMilliseconds"]),
                "entryFrames": [0, 29],
                "visibleFlipFrames": [29, 42],
                "childTimelineFrames": [0, 60],
            },
            "contract": {
                "durationMilliseconds": TARGET_DURATION_MS,
                "durationSeconds": TARGET_DURATION_MS / 1000.0,
                "uniformTimeScale": round(TIME_SCALE, 12),
                "policy": "time-scale measured path only",
                "segments": [
                    {
                        "id": "entry",
                        "sourceFrames": [0, 29],
                        "sourceMilliseconds": [0.0, 483.333333],
                        "contractMilliseconds": [0.0, round(483.333333 * TIME_SCALE, 6)],
                        "sourceBasis": "root transform convergence",
                    },
                    {
                        "id": "front-to-edge",
                        "sourceFrames": [29, 36],
                        "sourceMilliseconds": [483.333333, 600.0],
                        "contractMilliseconds": [
                            round(483.333333 * TIME_SCALE, 6),
                            round(600.0 * TIME_SCALE, 6),
                        ],
                        "sourceBasis": "verified Rive frame landmarks",
                    },
                    {
                        "id": "edge-to-reverse",
                        "sourceFrames": [36, 39],
                        "sourceMilliseconds": [600.0, 650.0],
                        "contractMilliseconds": [
                            round(600.0 * TIME_SCALE, 6),
                            round(650.0 * TIME_SCALE, 6),
                        ],
                        "sourceBasis": "verified Rive frame landmarks",
                    },
                    {
                        "id": "reverse-to-front",
                        "sourceFrames": [39, 42],
                        "sourceMilliseconds": [650.0, 700.0],
                        "contractMilliseconds": [
                            round(650.0 * TIME_SCALE, 6),
                            round(700.0 * TIME_SCALE, 6),
                        ],
                        "sourceBasis": "verified Rive frame landmarks",
                    },
                    {
                        "id": "single-highlight-window",
                        "sourceFrames": [42, 60],
                        "sourceMilliseconds": [700.0, 1000.0],
                        "contractMilliseconds": [
                            round(700.0 * TIME_SCALE, 6),
                            round(1000.0 * TIME_SCALE, 6),
                        ],
                        "sourceBasis": "remaining canonical one-shot child timeline",
                        "implementationState": "deferred-downstream-validation",
                    },
                    {
                        "id": "settled-hold",
                        "sourceFrames": [60, 210],
                        "sourceMilliseconds": [1000.0, 3500.0],
                        "contractMilliseconds": [
                            round(1000.0 * TIME_SCALE, 6),
                            TARGET_DURATION_MS,
                        ],
                        "sourceBasis": "root timeline remainder",
                    },
                ],
            },
            "hover": {
                "implementationState": "deferred-downstream-validation",
                "insideLockedDuration": False,
                "startsOnlyAfterPresentationCompletion": True,
                "independentPrizeAngularVelocity": 0.0,
            },
        },
        "samples": samples,
        "residualSummaryPixels": {
            "sampleCount": len(samples),
            "cornerCount": int(all_error_array.size),
            "mean": round(float(np.mean(all_error_array)), 6),
            "rmse": round(float(math.sqrt(np.mean(all_error_array ** 2))), 6),
            "maximum": round(float(np.max(all_error_array)), 6),
            "maximumSampleLabel": max(
                samples,
                key=lambda sample: sample["reprojectionResidualPixels"]["maximum"],
            )["label"],
            "clippedSampleLabels": [
                sample["label"]
                for sample in samples
                if sample["sourceClipped"]
            ],
            "unclippedMean": round(float(np.mean(unclipped_errors)), 6),
            "unclippedRmse": round(float(math.sqrt(np.mean(unclipped_errors ** 2))), 6),
            "unclippedMaximum": round(float(np.max(unclipped_errors)), 6),
            "exact": False,
        },
        "userScreenshotReferenceFit": {
            "role": "separate rejection screenshot; not a path keyframe",
            "sourceCornersPixels": np.round(user_points, 6).tolist(),
            "fittedCornersPixels": np.round(user_pose["projected"], 6).tolist(),
            "visibleFaceEvidence": "front",
            "reprojectionResidualPixels": {
                "perCorner": np.round(user_errors, 6).tolist(),
                "mean": round(float(np.mean(user_errors)), 6),
                "rmse": round(float(math.sqrt(np.mean(user_errors ** 2))), 6),
                "maximum": round(float(np.max(user_errors)), 6),
            },
            "exact": False,
        },
        "sourceBoundaries": {
            "riveMeshDeformationPresentInSource": bool(
                authored["verifiedConclusions"]["coinSlabUses2DMeshDeformation"]
            ),
            "riveMeshDeformationUsedAsTarget": False,
            "physicalAxisClaim": None,
            "pureYAxisClaim": False,
            "pureXAxisClaim": False,
            "singleAxisClaim": False,
            "wholeCaseOnly": True,
            "explode": False,
            "referenceManifestWholeCaseCount": int(
                reference_manifest["validationThresholds"]["wholeCaseComponentCountExact"]
            ),
        },
    }
    return fit


def transform_points(points: list[list[float]], source_box: tuple[int, int, int, int]) -> list[tuple[float, float]]:
    x0, y0, x1, y1 = source_box
    scale = min((x1 - x0) / SOURCE_WIDTH, (y1 - y0) / SOURCE_HEIGHT)
    width = SOURCE_WIDTH * scale
    height = SOURCE_HEIGHT * scale
    offset_x = x0 + ((x1 - x0) - width) / 2.0
    offset_y = y0 + ((y1 - y0) - height) / 2.0
    return [
        (offset_x + point[0] * scale, offset_y + point[1] * scale)
        for point in points
    ]


def unit_homography(points: list[tuple[float, float]]) -> np.ndarray:
    source = np.float32([[0, 0], [1, 0], [1, 1], [0, 1]])
    target = np.float32(points)
    return cv2.getPerspectiveTransform(source, target)


def mapped_rect(homography: np.ndarray, rect: tuple[float, float, float, float]) -> list[tuple[float, float]]:
    left, top, right, bottom = rect
    points = np.float32([[[left, top], [right, top], [right, bottom], [left, bottom]]])
    transformed = cv2.perspectiveTransform(points, homography)[0]
    return [(float(point[0]), float(point[1])) for point in transformed]


def draw_case_overlay(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    sample: dict[str, Any],
) -> None:
    measured = transform_points(sample["sourceCornersPixels"], box)
    fitted = transform_points(sample["fittedCornersPixels"], box)
    draw.rounded_rectangle(box, radius=18, fill="#070A0E", outline=LINE, width=2)
    face_fill = "#27313B" if sample["visibleFaceEvidence"] != "back" else "#1A222B"
    draw.polygon(fitted, fill=face_fill)
    homography = unit_homography(fitted)
    if sample["visibleFaceEvidence"] == "front":
        inner = mapped_rect(homography, (0.11, 0.10, 0.89, 0.72))
        label = mapped_rect(homography, (0.10, 0.76, 0.90, 0.93))
        draw.polygon(inner, fill="#0E141A", outline="#687480")
        draw.polygon(label, fill="#D2C7B4", outline="#F2E9D9")
    elif sample["visibleFaceEvidence"] == "back":
        inner = mapped_rect(homography, (0.10, 0.08, 0.90, 0.92))
        draw.polygon(inner, fill="#10161D", outline="#596572")
    else:
        seam = mapped_rect(homography, (0.42, 0.06, 0.58, 0.94))
        draw.polygon(seam, fill="#111820")
    draw.line(fitted + [fitted[0]], fill=MAGENTA, width=5, joint="curve")
    draw.line(measured + [measured[0]], fill=CYAN, width=4, joint="curve")
    for source, target in zip(measured, fitted):
        draw.line((source, target), fill=AMBER, width=2)
        draw.ellipse((source[0] - 5, source[1] - 5, source[0] + 5, source[1] + 5), fill=CYAN)
        draw.ellipse((target[0] - 5, target[1] - 5, target[0] + 5, target[1] + 5), fill=MAGENTA)


def render_pose_sheet(fit: dict[str, Any]) -> None:
    canvas = Image.new("RGB", (3000, 4050), BG)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 3000, 150), fill=CYAN)
    draw.text((70, 40), "GATE 03 REV 2 · RIVE QUAD VS RIGID CUBOID FIT", font=font(60, True), fill=BG)
    draw.text(
        (70, 175),
        "Technical evidence · cyan = measured quad · magenta = rigid fit · source pixels remain reference-only",
        font=font(32),
        fill=MUTED,
    )

    panels: list[dict[str, Any]] = [{
        "label": "USER REJECTION SCREENSHOT",
        "sourcePath": REV3 / "user-motion-rejection-reference.png",
        "sourceCornersPixels": fit["userScreenshotReferenceFit"]["sourceCornersPixels"],
        "fittedCornersPixels": fit["userScreenshotReferenceFit"]["fittedCornersPixels"],
        "residual": fit["userScreenshotReferenceFit"]["reprojectionResidualPixels"],
        "visibleFaceEvidence": "front",
        "sourceClipped": False,
        "sourceMilliseconds": None,
    }]
    for sample in fit["samples"]:
        panels.append({
            "label": sample["label"],
            "sourcePath": REV3 / "frames" / FRAME_FILES[sample["label"]],
            "sourceCornersPixels": sample["sourceCornersPixels"],
            "fittedCornersPixels": sample["fittedCornersPixels"],
            "residual": sample["reprojectionResidualPixels"],
            "visibleFaceEvidence": sample["visibleFaceEvidence"],
            "sourceClipped": sample["sourceClipped"],
            "sourceMilliseconds": sample["sourceMilliseconds"],
        })

    panel_width = 1410
    panel_height = 700
    for index, panel in enumerate(panels):
        column = index % 2
        row = index // 2
        x0 = 60 + column * 1470
        y0 = 245 + row * 745
        rounded_panel(draw, (x0, y0, x0 + panel_width, y0 + panel_height))
        source = Image.open(panel["sourcePath"]).convert("RGB")
        source = ImageEnhance.Brightness(source).enhance(0.42)
        image_box = (x0 + 24, y0 + 92, x0 + 944, y0 + 660)
        scale = min((image_box[2] - image_box[0]) / source.width, (image_box[3] - image_box[1]) / source.height)
        rendered = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
        paste_x = image_box[0] + ((image_box[2] - image_box[0]) - rendered.width) // 2
        paste_y = image_box[1] + ((image_box[3] - image_box[1]) - rendered.height) // 2
        canvas.paste(rendered, (paste_x, paste_y))
        actual_box = (paste_x, paste_y, paste_x + rendered.width, paste_y + rendered.height)
        source_points = transform_points(panel["sourceCornersPixels"], actual_box)
        fitted_points = transform_points(panel["fittedCornersPixels"], actual_box)
        draw.line(source_points + [source_points[0]], fill=CYAN, width=5, joint="curve")
        draw.line(fitted_points + [fitted_points[0]], fill=MAGENTA, width=5, joint="curve")
        for source_point, fitted_point in zip(source_points, fitted_points):
            draw.line((source_point, fitted_point), fill=AMBER, width=2)
        draw.text((x0 + 28, y0 + 24), panel["label"], font=font(32, True), fill=TEXT)
        if panel["sourceMilliseconds"] is not None:
            draw.text(
                (x0 + 910, y0 + 28),
                f'{panel["sourceMilliseconds"]:.0f} ms',
                font=font(26, True),
                fill=CYAN,
                anchor="ra",
            )
        details_x = x0 + 975
        draw.text((details_x, y0 + 118), f'FACE · {panel["visibleFaceEvidence"]}', font=font(25, True), fill=GREEN)
        draw.text((details_x, y0 + 168), f'MEAN · {panel["residual"]["mean"]:.3f} px', font=font(25), fill=TEXT)
        draw.text((details_x, y0 + 213), f'RMSE · {panel["residual"]["rmse"]:.3f} px', font=font(25), fill=TEXT)
        draw.text((details_x, y0 + 258), f'MAX · {panel["residual"]["maximum"]:.3f} px', font=font(25), fill=TEXT)
        if panel["sourceClipped"]:
            draw_wrapped(
                draw,
                (details_x, y0 + 322),
                "SOURCE QUAD CLIPPED AT FRAME EDGE. Residual is reported, not hidden.",
                font(24, True),
                RED,
                390,
            )
        else:
            draw_wrapped(
                draw,
                (details_x, y0 + 322),
                "Best-fit only. Cyan and magenta need not coincide.",
                font(24),
                MUTED,
                390,
            )
    canvas.save(POSE_SHEET_PATH)


def plot_lines(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    x_values: list[float],
    series: list[tuple[str, list[float], str]],
    title: str,
    unit: str,
) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box)
    draw.text((x0 + 34, y0 + 24), title, font=font(34, True), fill=TEXT)
    plot_box = (x0 + 92, y0 + 98, x1 - 42, y1 - 74)
    px0, py0, px1, py1 = plot_box
    all_values = [value for _, values, _ in series for value in values]
    minimum = min(all_values)
    maximum = max(all_values)
    if math.isclose(minimum, maximum):
        minimum -= 1.0
        maximum += 1.0
    margin = (maximum - minimum) * 0.1
    minimum -= margin
    maximum += margin
    draw.line((px0, py1, px1, py1), fill=LINE, width=3)
    draw.line((px0, py0, px0, py1), fill=LINE, width=3)
    for step in range(5):
        ratio = step / 4.0
        y = py1 - ratio * (py1 - py0)
        value = minimum + ratio * (maximum - minimum)
        draw.line((px0, y, px1, y), fill="#1D2834", width=2)
        draw.text((px0 - 14, y), f"{value:.1f}", font=font(20), fill=MUTED, anchor="rm")
    min_x = min(x_values)
    max_x = max(x_values)
    for label, values, color in series:
        points = []
        for x_value, value in zip(x_values, values):
            x = px0 + (x_value - min_x) / max(max_x - min_x, 1e-9) * (px1 - px0)
            y = py1 - (value - minimum) / (maximum - minimum) * (py1 - py0)
            points.append((x, y))
        draw.line(points, fill=color, width=5, joint="curve")
        for point in points:
            draw.ellipse((point[0] - 5, point[1] - 5, point[0] + 5, point[1] + 5), fill=color)
    legend_x = px0
    for label, _, color in series:
        draw.rectangle((legend_x, y1 - 48, legend_x + 24, y1 - 24), fill=color)
        draw.text((legend_x + 34, y1 - 53), label, font=font(21, True), fill=MUTED)
        legend_x += 220
    draw.text((x1 - 34, y0 + 32), unit, font=font(22, True), fill=CYAN, anchor="ra")


def render_curves(fit: dict[str, Any]) -> None:
    canvas = Image.new("RGB", (2600, 2100), BG)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 2600, 140), fill=CYAN)
    draw.text((62, 34), "GATE 03 REV 2 · RIGID MOTION CURVES", font=font(56, True), fill=BG)
    draw.text(
        (62, 162),
        "Euler curves are a readable decomposition of quaternion samples, not physical single-axis claims.",
        font=font(30),
        fill=MUTED,
    )
    samples = fit["samples"]
    x_values = [float(sample["contractMilliseconds"]) for sample in samples]
    plot_lines(
        draw,
        (50, 230, 2550, 810),
        x_values,
        [
            ("pitch X", [sample["presentationEulerDecompositionDegrees"]["pitchX"] for sample in samples], CYAN),
            ("yaw Y", [sample["presentationEulerDecompositionDegrees"]["yawY"] for sample in samples], MAGENTA),
            ("roll Z", [sample["presentationEulerDecompositionDegrees"]["rollZ"] for sample in samples], AMBER),
        ],
        "Quaternion decomposition",
        "degrees",
    )
    plot_lines(
        draw,
        (50, 850, 2550, 1430),
        x_values,
        [
            ("center X", [sample["fittedCenterPixels"][0] for sample in samples], BLUE),
            ("center Y", [sample["fittedCenterPixels"][1] for sample in samples], GREEN),
            ("framing", [sample["cameraFramingScaleRelativeToSettled"] * 100.0 for sample in samples], AMBER),
        ],
        "Translation and camera framing",
        "pixels / %",
    )
    plot_lines(
        draw,
        (50, 1470, 2550, 2040),
        x_values,
        [
            ("mean", [sample["reprojectionResidualPixels"]["mean"] for sample in samples], CYAN),
            ("maximum", [sample["reprojectionResidualPixels"]["maximum"] for sample in samples], RED),
        ],
        "Reprojection residual",
        "pixels",
    )
    canvas.save(CURVE_PATH)


def render_contract_preview(contract: dict[str, Any], fit: dict[str, Any]) -> None:
    width = 3200
    height = 4300
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, 170), fill=CYAN)
    draw.text((76, 42), "GATE 03 CONTRACT · REV 2", font=font(72, True), fill=BG)
    draw.text((width - 76, 62), "READY FOR REVIEW · 2/12", font=font(39, True), fill=BG, anchor="ra")
    draw.text((76, 205), "WHOLE CASE ONLY · RIGID BEST-FIT · NO EXPLODE", font=font(46, True), fill=TEXT)
    draw.text(
        (76, 268),
        "Motion-only correction. Historical static approvals stay locked; Gate 04 is not entered.",
        font=font(32),
        fill=MUTED,
    )

    selection_y = 330
    selections = [
        ("USER SCOPE", "只纠正动画；静态结构保留", GREEN),
        ("TARGET", "整盒刚性；用 pitch/yaw/roll 复合翻转", MAGENTA),
        ("QUOTE", "继续", CYAN),
    ]
    selection_widths = [950, 1460, 520]
    x = 76
    for (label, value, color), item_width in zip(selections, selection_widths):
        draw.rounded_rectangle((x, selection_y, x + item_width, selection_y + 128), radius=22, fill=PANEL_ALT, outline=color, width=3)
        draw.text((x + 24, selection_y + 20), label, font=font(24, True), fill=color)
        draw.text((x + 24, selection_y + 64), value, font=font(31, True), fill=TEXT)
        x += item_width + 20

    rounded_panel(draw, (76, 500, 1555, 1115))
    draw.text((116, 535), "STATIC VALUES PRESERVED", font=font(42, True), fill=GREEN)
    static_lines = [
        "Envelope 228 × 304 × 59 mm · Portrait 0.75",
        "Closed tube 10 × 9 · passage 6 × 5 · wall 2 · R20",
        "Label 184 × 58 mm @ Y=99 mm",
        "ContentSlot 180 × 198 × 48 mm",
        "Analytic concentric corner families · drift 0.000 mm",
        "Current material zones and PBR ranges remain unchanged",
        "Toy/prize remains caller-owned content and is out of scope",
    ]
    y = 610
    for line in static_lines:
        draw.ellipse((118, y + 12, 132, y + 26), fill=GREEN)
        y = draw_wrapped(draw, (154, y), line, font(31), TEXT, 1320, 8) + 11

    rounded_panel(draw, (1595, 500, 3124, 1115))
    draw.text((1635, 535), "MOTION CONTRACT", font=font(42, True), fill=MAGENTA)
    motion_lines = [
        "One rigid assembled Portrait cuboid; PresentationRoot owns pose",
        "Per sample: quaternion + translation + uniform scale 1.0",
        "Fixed diagnostic camera framing; no geometry deformation",
        "Pure Y, pure X and every single-axis physical claim forbidden",
        "Rive mesh deformation is source evidence only",
        "Single highlight and hover stay deferred validation segments",
        "Prize independent angular velocity = 0 · explode forbidden",
    ]
    y = 610
    for line in motion_lines:
        draw.ellipse((1638, y + 12, 1652, y + 26), fill=MAGENTA)
        y = draw_wrapped(draw, (1674, y), line, font(31), TEXT, 1395, 8) + 11

    rounded_panel(draw, (76, 1155, 3124, 1495))
    draw.text((116, 1190), "TIME", font=font(40, True), fill=AMBER)
    timeline = fit["timeline"]["contract"]
    draw.text(
        (315, 1190),
        f'3.500000 s Rive root × {timeline["uniformTimeScale"]:.9f} = 4.520833 s',
        font=font(36, True),
        fill=TEXT,
    )
    segments = timeline["segments"]
    bar_left = 116
    bar_right = 3084
    bar_top = 1290
    bar_bottom = 1372
    segment_colors = [GREEN, CYAN, MAGENTA, BLUE, AMBER, "#4B5663"]
    total = TARGET_DURATION_MS
    for segment, color in zip(segments, segment_colors):
        start = float(segment["contractMilliseconds"][0])
        end = float(segment["contractMilliseconds"][1])
        left = bar_left + (start / total) * (bar_right - bar_left)
        right = bar_left + (end / total) * (bar_right - bar_left)
        draw.rectangle((left, bar_top, right, bar_bottom), fill=color)
        if right - left > 180:
            draw.text(((left + right) / 2, (bar_top + bar_bottom) / 2), segment["id"], font=font(20, True), fill=BG, anchor="mm")
    draw.text(
        (116, 1405),
        "Entry / flip / reverse / highlight window / hold keep canonical order and relative timing. No added pause.",
        font=font(28),
        fill=MUTED,
    )

    draw.text((76, 1545), "MEASURED QUAD VS RIGID FIT", font=font(43, True), fill=TEXT)
    draw.text(
        (3124, 1552),
        "CYAN = RIVE · MAGENTA = RIGID",
        font=font(27, True),
        fill=MUTED,
        anchor="ra",
    )
    sample_labels = ["START", "USER-SCREENSHOT NEAREST", "HALF", "EDGE", "REVERSE FACE", "END / FRONT"]
    sample_by_label = {sample["label"]: sample for sample in fit["samples"]}
    for index, label in enumerate(sample_labels):
        column = index % 3
        row = index // 3
        x0 = 76 + column * 1020
        y0 = 1610 + row * 780
        rounded_panel(draw, (x0, y0, x0 + 980, y0 + 730))
        sample = sample_by_label[label]
        draw.text((x0 + 28, y0 + 24), label, font=font(30, True), fill=TEXT)
        draw.text(
            (x0 + 948, y0 + 28),
            f'{sample["contractMilliseconds"]:.1f} ms',
            font=font(23, True),
            fill=CYAN,
            anchor="ra",
        )
        draw_case_overlay(draw, (x0 + 24, y0 + 88, x0 + 956, y0 + 575), sample)
        residual = sample["reprojectionResidualPixels"]
        draw.text(
            (x0 + 28, y0 + 606),
            f'FACE {sample["visibleFaceEvidence"]} · MEAN {residual["mean"]:.3f} px · MAX {residual["maximum"]:.3f} px',
            font=font(23, True),
            fill=RED if sample["sourceClipped"] else GREEN,
        )
        draw.text(
            (x0 + 28, y0 + 652),
            "clipped source quad · residual retained" if sample["sourceClipped"] else "best-fit residual · not exact",
            font=font(23),
            fill=MUTED,
        )

    residual = fit["residualSummaryPixels"]
    rounded_panel(draw, (76, 3215, 1555, 3705))
    draw.text((116, 3250), "FIT TRUTH", font=font(40, True), fill=RED)
    fit_lines = [
        f'All Rive corners · mean {residual["mean"]:.6f} px',
        f'All Rive corners · RMSE {residual["rmse"]:.6f} px',
        f'All Rive corners · maximum {residual["maximum"]:.6f} px',
        f'Maximum sample · {residual["maximumSampleLabel"]}',
        f'Clipped source samples · {", ".join(residual["clippedSampleLabels"])}',
        "The quad set is not claimed as an exact rigid-camera projection.",
    ]
    y = 3320
    for line in fit_lines:
        y = draw_wrapped(draw, (116, y), line, font(29), TEXT, 1385, 8) + 7

    rounded_panel(draw, (1595, 3215, 3124, 3705))
    draw.text((1635, 3250), "CAMERA ASSUMPTIONS", font=font(40, True), fill=BLUE)
    camera = fit["cameraAssumptions"]
    camera_lines = [
        f'Fixed pinhole · {camera["imageSizePixels"][0]} × {camera["imageSizePixels"][1]} px',
        f'Principal point · {camera["principalPointPixels"][0]:.1f}, {camera["principalPointPixels"][1]:.1f}',
        f'Diagnostic vFOV · {camera["verticalFovDegrees"]:.2f}°',
        f'Focal length · {camera["focalLengthPixels"]:.3f} px',
        "Square pixels · zero skew · zero lens distortion",
        "Diagnostic fit only. Shipping camera remains a later gate.",
    ]
    y = 3320
    for line in camera_lines:
        y = draw_wrapped(draw, (1635, y), line, font(29), TEXT, 1405, 8) + 7

    rounded_panel(draw, (76, 3750, 3124, 4205), PANEL_ALT)
    draw.text((116, 3790), "SINGLE APPROVAL QUESTION", font=font(38, True), fill=CYAN)
    draw_wrapped(
        draw,
        (116, 3860),
        contract["approvalQuestion"],
        font(40, True),
        TEXT,
        2920,
        14,
    )
    draw.text(
        (116, 4145),
        "Gate 03 remains READY FOR REVIEW. No automatic approval. Gate 04 remains stale.",
        font=font(29, True),
        fill=RED,
    )
    canvas.save(PREVIEW_PATH)


def build_contract(fit: dict[str, Any]) -> dict[str, Any]:
    pipeline = load_json(PIPELINE_PATH)
    blockout = load_json(BLOCKOUT_VALIDATION_PATH)
    historical_contract = load_json(HISTORICAL_CONTRACT_PATH)
    gate02 = pipeline["stages"][1]
    gate07 = pipeline["stages"][6]
    active_claim_ids = [
        claim["id"]
        for claim in pipeline["claims"]
        if claim["stageId"] == "02-analysis" and claim.get("state") != "superseded"
    ]
    if (
        pipeline["revision"] != 41
        or gate02["status"] != "approved"
        or gate02["analysisSpec"]["revision"] != 3
        or gate02["analysisSpec"]["approval"]["userApprovalQuote"] != "继续"
        or len(active_claim_ids) != 11
        or any(not claim_id.endswith("-r003") for claim_id in active_claim_ids)
    ):
        raise RuntimeError("Gate 02 rev 3 must be API-approved before generating Gate 03 rev 2")
    if blockout["dimensionsMm"]["measured"] != {"width": 228.0, "height": 304.0, "depth": 59.0}:
        raise RuntimeError("Historical static bounds changed")

    pbr_values = gate07["materialSpec"]["pbrValues"]
    background = gate07["materialSpec"]["background"]
    contract = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "contractRevision": 2,
        "createdDate": "2026-08-26",
        "stageStatus": "ready_for_review",
        "approvalEffect": "none-until-explicit-gate-03-user-approval",
        "sourceTaskId": "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3",
        "sourceClaimIds": active_claim_ids,
        "sourceAssetIds": gate02["artifactIds"],
        "userSelections": {
            "scope": "只纠正动画；静态结构保留",
            "targetMotion": "整盒刚性；用 pitch/yaw/roll 复合翻转",
            "continueQuote": "继续",
        },
        "units": {
            "geometry": "millimeters",
            "angles": "degrees",
            "time": "seconds",
            "imageResidual": "pixels",
        },
        "coordinateSystem": {
            "authoring": "x width-right, y height-up, z depth-front",
            "origin": "assembled outer-envelope center",
            "motionOwner": "PresentationRoot",
            "fitCamera": "OpenCV x-right, y-down, z-forward diagnostic camera",
            "poseAuthority": "presentationQuaternionWxyz plus camera-space translation; Euler values are decomposition only",
        },
        "staticPreservation": {
            "decisionState": "locked-historical-values-preserved-by-user-motion-only-selection",
            "geometryMutationAllowed": False,
            "materialMutationAllowed": False,
            "portraitEnvelope": {
                "widthMm": 228.0,
                "heightMm": 304.0,
                "depthMm": 59.0,
                "widthHeightRatio": 0.75,
            },
            "closedTube": {
                "outerSectionMm": {"width": 10.0, "depth": 9.0},
                "passageSectionMm": {"width": 6.0, "depth": 5.0},
                "wallThicknessMm": 2.0,
                "profileCornerRadiusMm": 3.0,
                "passageCornerRadiusMm": 1.0,
                "outerCornerRadiusMm": 20.0,
                "centerlineCornerRadiusMm": 15.0,
                "innerCornerRadiusMm": 10.0,
                "connectivity": "one connected manifold",
                "openBoundaryEdgeCount": 0,
                "channelFloodFill": "384/384",
            },
            "physicalLabel": {
                "widthMm": 184.0,
                "heightMm": 58.0,
                "centerYmm": 99.0,
            },
            "contentSlot": {
                "widthMm": 180.0,
                "heightMm": 198.0,
                "depthMm": 48.0,
                "owner": "caller",
            },
            "concentricCornerFamilies": {
                "maximumDriftMm": 0.0,
                "toleranceMm": 0.01,
                "caseTubeShellCentersMm": [[-94, -132], [-94, 132], [94, -132], [94, 132]],
                "mainDisplayChamberCentersMm": [[-75, -127], [-75, 43], [75, -127], [75, 43]],
                "physicalLabelCentersMm": [[-86, 76], [-86, 122], [86, 76], [86, 122]],
            },
            "materialRanges": {
                "decisionState": "historical-approved-retained-no-material-edit",
                "zones": historical_contract["materialZones"]["zoneTopology"]["zones"],
                "pbrValues": pbr_values,
                "background": background,
            },
            "toyScope": {
                "status": "out-of-scope-caller-owned-content",
                "attachment": "ContentSlot",
                "geometryChanged": False,
                "materialsChanged": False,
                "artworkChanged": False,
                "pivotChanged": False,
                "physicsChanged": False,
                "hapticsChanged": False,
                "mechanismChanged": False,
            },
        },
        "closedTubeFrame": {
            "topology": {
                "connectivity": "one connected manifold",
                "path": "one cyclic perimeter through four tangent-continuous bends",
                "openBoundaryEdges": 0,
            }
        },
        "motionContract": {
            "decisionState": "gate03-rev2-pending-user-approval",
            "target": "one rigid assembled Portrait cuboid",
            "motionOwner": "PresentationRoot",
            "poseSamplesAsset": repo_path(FIT_PATH),
            "poseRepresentation": "normalized WXYZ quaternion, camera-space translation, uniform scale 1.0, diagnostic framing scale",
            "interpolation": "piecewise quaternion slerp with adjacent sign continuity; translation and framing follow measured sample times",
            "physicalAxisClaim": None,
            "eulerUse": "readable decomposition only",
            "prohibited": [
                "pure Y turntable",
                "pure X rotation replacement",
                "single-axis physical claim",
                "non-rigid Rive mesh deformation",
                "independent foreground/background layer deformation",
                "non-uniform scale",
                "explode",
                "part separation",
                "assembly",
                "reassembly",
            ],
            "timeline": fit["timeline"],
            "singleHighlight": {
                "count": 1,
                "implementationState": "deferred-downstream-validation",
                "poseEffect": "none",
            },
            "hover": fit["timeline"]["hover"],
            "prize": {
                "inheritsPresentationRoot": True,
                "independentAngularVelocity": 0.0,
                "mechanismStateChanged": False,
            },
            "fitTruth": {
                "exactFitClaimed": False,
                "residualSummaryPixels": fit["residualSummaryPixels"],
                "cameraAssumptions": fit["cameraAssumptions"],
            },
        },
        "revealMotion": {
            "sequence": {
                "events": [
                    "entry",
                    "front-to-edge",
                    "edge-to-reverse",
                    "reverse-to-front",
                    "single-highlight-window-deferred-validation",
                    "settled-hold",
                ],
                "prizeAngularVelocity": 0,
                "wholeCaseOnly": True,
                "explode": False,
            }
        },
        "camera": {
            "diagnosticFit": fit["cameraAssumptions"],
            "shippingCamera": {
                "decisionState": "historical-range-preserved-pending-downstream-revalidation",
                "verticalFovDegrees": [27.0, 31.0],
                "depthOfField": "off",
                "note": "The diagnostic fit FOV is not a shipping camera choice.",
            },
        },
        "claimDisposition": {
            claim_id: (
                "preserve-historical-static-values"
                if claim_id == "premium-display-case-analysis-static-preservation-r003"
                else "lock-rigid-quaternion-best-fit-with-no-axis-overclaim"
                if claim_id in {
                    "premium-display-case-analysis-motion-r003",
                    "premium-display-case-analysis-rigid-target-r003",
                }
                else "lock-4.520833-second-uniform-time-scaled-path"
                if claim_id == "premium-display-case-analysis-duration-lock-r003"
                else "consume-without-expanding-approved-scope"
            )
            for claim_id in active_claim_ids
        },
        "route": {
            "primary": "deterministic Python/OpenCV contract fit; Blender geometry remains unchanged",
            "blenderGeometryEdit": False,
            "materialEdit": False,
            "shippingUnityEdit": False,
            "buildInstallPhonePush": False,
            "nextGatePolicy": "Do not enter Gate 04 before explicit Gate 03 approval.",
        },
        "historyBoundary": {
            "gate03Rev1": "preserved-stale",
            "gate04Through08": "preserved-stale",
            "staticArtifactsDeleted": False,
        },
        "completeness": {
            "complete": True,
            "activeGate02ClaimCount": len(active_claim_ids),
            "allActiveGate02ClaimsConsumed": True,
        },
        "approvalQuestion": "是否批准 Gate 03 rev 2：保留既有静态盒体与材质范围，并以图中有明确重投影残差的刚性 quaternion 复合翻转合同进入 Gate 04？",
    }
    return contract


def image_metrics(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGB")
    statistics = ImageStat.Stat(image)
    extrema = image.getextrema()
    return {
        "width": image.width,
        "height": image.height,
        "meanRgb": [round(float(value), 6) for value in statistics.mean],
        "channelRanges": [maximum - minimum for minimum, maximum in extrema],
        "nonBlank": all(maximum > minimum for minimum, maximum in extrema),
    }


def build_validation(fit: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    residual = fit["residualSummaryPixels"]
    samples = fit["samples"]
    checks = {
        "sourceHashesPresent": all(source["sha256"] for source in fit["sourceFiles"]),
        "nineRiveSamplesFit": len(samples) == 9,
        "allPoseValuesFinite": all(
            np.isfinite(
                sample["presentationQuaternionWxyz"]
                + sample["diagnosticTranslationCameraMm"]
                + sample["translationRelativeToSettledCameraMm"]
            ).all()
            for sample in samples
        ),
        "quaternionsNormalized": all(
            abs(float(np.linalg.norm(sample["presentationQuaternionWxyz"])) - 1.0) <= 1e-6
            for sample in samples
        ),
        "uniformScaleLocked": all(sample["uniformScale"] == 1.0 for sample in samples),
        "positiveCameraDepth": all(sample["diagnosticTranslationCameraMm"][2] > 0 for sample in samples),
        "residualsFiniteAndReported": all(
            np.isfinite(list(sample["reprojectionResidualPixels"].values())[1:]).all()
            for sample in samples
        ),
        "nonExactFitDeclared": residual["exact"] is False and fit["method"]["exactFitClaimed"] is False,
        "clippedSamplesDeclared": residual["clippedSampleLabels"] == [
            "QUARTER",
            "USER-SCREENSHOT NEAREST",
            "HALF",
        ],
        "compositeRotationPresent": any(
            sum(
                abs(sample["presentationEulerDecompositionDegrees"][axis]) > 5.0
                for axis in ["pitchX", "yawY", "rollZ"]
            ) >= 2
            for sample in samples
        ),
        "axisOverclaimAbsent": (
            fit["sourceBoundaries"]["physicalAxisClaim"] is None
            and fit["sourceBoundaries"]["pureYAxisClaim"] is False
            and fit["sourceBoundaries"]["pureXAxisClaim"] is False
            and fit["sourceBoundaries"]["singleAxisClaim"] is False
        ),
        "riveDeformationExcludedFromTarget": fit["sourceBoundaries"]["riveMeshDeformationUsedAsTarget"] is False,
        "wholeCaseNoExplode": (
            fit["sourceBoundaries"]["wholeCaseOnly"] is True
            and fit["sourceBoundaries"]["explode"] is False
        ),
        "durationExact": abs(fit["timeline"]["contract"]["durationMilliseconds"] - TARGET_DURATION_MS) <= 1e-9,
        "timeScaleOnly": fit["timeline"]["contract"]["policy"] == "time-scale measured path only",
        "allActiveClaimsConsumed": contract["completeness"]["allActiveGate02ClaimsConsumed"] is True,
        "gate04Blocked": contract["route"]["nextGatePolicy"] == "Do not enter Gate 04 before explicit Gate 03 approval.",
        "toyOutOfScope": contract["staticPreservation"]["toyScope"]["status"] == "out-of-scope-caller-owned-content",
    }
    image_reports = {
        repo_path(path): image_metrics(path)
        for path in [PREVIEW_PATH, POSE_SHEET_PATH, CURVE_PATH]
    }
    checks["largeTypePreview"] = (
        image_reports[repo_path(PREVIEW_PATH)]["width"] >= 3000
        and image_reports[repo_path(PREVIEW_PATH)]["height"] >= 4000
    )
    checks["imagesNonBlank"] = all(report["nonBlank"] for report in image_reports.values())
    return {
        "schema": "premium-display-case-gate03-rigid-motion-fit-validation.v1",
        "modelId": "premium-display-case",
        "gate": "03-contract",
        "contractRevision": 2,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "meanReprojectionResidualPixels": residual["mean"],
            "rmseReprojectionResidualPixels": residual["rmse"],
            "maximumReprojectionResidualPixels": residual["maximum"],
            "unclippedMeanReprojectionResidualPixels": residual["unclippedMean"],
            "unclippedMaximumReprojectionResidualPixels": residual["unclippedMaximum"],
            "diagnosticVerticalFovDegrees": fit["cameraAssumptions"]["verticalFovDegrees"],
            "totalDurationSeconds": TARGET_DURATION_MS / 1000.0,
            "activeGate02ClaimCount": contract["completeness"]["activeGate02ClaimCount"],
        },
        "imageReports": image_reports,
        "truth": {
            "bestFitNotExact": True,
            "wholeCaseOnly": True,
            "explode": False,
            "meshDeformationTarget": False,
            "shippingUnityChanged": False,
            "blenderGeometryOrMaterialChanged": False,
            "buildInstallPhonePush": False,
        },
    }


def build_outputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    fit = fit_motion()
    contract = build_contract(fit)
    write_json(FIT_PATH, fit)
    write_json(CONTRACT_PATH, contract)
    render_pose_sheet(fit)
    render_curves(fit)
    render_contract_preview(contract, fit)
    validation = build_validation(fit, contract)
    write_json(VALIDATION_PATH, validation)
    if validation["status"] != "pass":
        failed = [key for key, value in validation["checks"].items() if not value]
        raise RuntimeError(f"Rigid motion validation failed: {failed}")
    return fit, contract, validation


def validate_existing() -> dict[str, Any]:
    existing_fit = load_json(FIT_PATH)
    existing_contract = load_json(CONTRACT_PATH)
    existing_validation = load_json(VALIDATION_PATH)
    recomputed_fit = fit_motion()
    keys = ["mean", "rmse", "maximum", "unclippedMean", "unclippedMaximum"]
    metric_deltas = {
        key: abs(
            float(existing_fit["residualSummaryPixels"][key])
            - float(recomputed_fit["residualSummaryPixels"][key])
        )
        for key in keys
    }
    checks = {
        "storedValidationPassed": existing_validation["status"] == "pass",
        "contractReadyForReview": existing_contract["stageStatus"] == "ready_for_review",
        "residualsReproduce": max(metric_deltas.values()) <= 1e-6,
        "samplePoseCountReproduces": len(existing_fit["samples"]) == len(recomputed_fit["samples"]) == 9,
        "previewImagePasses": image_metrics(PREVIEW_PATH)["nonBlank"],
        "poseSheetPasses": image_metrics(POSE_SHEET_PATH)["nonBlank"],
        "motionCurvePasses": image_metrics(CURVE_PATH)["nonBlank"],
    }
    result = {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metricDeltas": metric_deltas,
        "residualSummaryPixels": existing_fit["residualSummaryPixels"],
    }
    if result["status"] != "pass":
        raise RuntimeError(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.validate_only:
        print(json.dumps(validate_existing(), indent=2, ensure_ascii=False))
        return
    fit, _, validation = build_outputs()
    print(json.dumps({
        "status": validation["status"],
        "contractRevision": 2,
        "meanReprojectionResidualPixels": fit["residualSummaryPixels"]["mean"],
        "maximumReprojectionResidualPixels": fit["residualSummaryPixels"]["maximum"],
        "preview": str(PREVIEW_PATH),
        "poseSheet": str(POSE_SHEET_PATH),
        "curve": str(CURVE_PATH),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
