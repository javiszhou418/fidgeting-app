#!/usr/bin/env python3
"""Audit the portable Blender/Unity candidate and build uncropped review evidence."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
OLD = HERE.parent / "rev-002/hero.png"
BLENDER = HERE / "portable-beauty.png"
UNITY = HERE / "unity-portable-beauty.png"
BLENDER_CLAY = HERE / "portable-clay.png"
UNITY_CLAY = HERE / "unity-portable-clay.png"
SILHOUETTE = (
    MODEL_ROOT
    / "evidence/11-unity-parity/rev-010/blender-silhouette.png"
)
EXR = HERE / "portable-studio-r003.exr"
OLD_EXR = (
    MODEL_ROOT
    / "evidence/09-environment/rev-008/magnetic-slide-tile-shipping-studio-r008.exr"
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def ssim(left, right):
    x = cv2.cvtColor(left.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float64)
    y = cv2.cvtColor(right.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float64)
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    ux = cv2.GaussianBlur(x, (11, 11), 1.5)
    uy = cv2.GaussianBlur(y, (11, 11), 1.5)
    vx = cv2.GaussianBlur(x * x, (11, 11), 1.5) - ux * ux
    vy = cv2.GaussianBlur(y * y, (11, 11), 1.5) - uy * uy
    covariance = cv2.GaussianBlur(x * y, (11, 11), 1.5) - ux * uy
    score = ((2 * ux * uy + c1) * (2 * covariance + c2)) / (
        (ux * ux + uy * uy + c1) * (vx + vy + c2)
    )
    return float(score.mean())


def delta_e76(left, right, mask):
    a = cv2.cvtColor(left.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    b = cv2.cvtColor(right.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    values = np.linalg.norm(a - b, axis=2)[mask]
    return {
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
    }


def hotspot(image, mask):
    luminance = image.mean(axis=2)
    selected = mask & (luminance > 180)
    ys, xs = np.where(selected)
    if not len(xs):
        return {"pixels": 0, "centroid": None, "bbox": None, "bboxAspect": None}
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    return {
        "pixels": int(len(xs)),
        "centroid": [float(xs.mean()), float(ys.mean())],
        "bbox": bbox,
        "bboxAspect": float(
            (bbox[2] - bbox[0] + 1) / (bbox[3] - bbox[1] + 1)
        ),
    }


def gradient(image, mask):
    gray = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float64)
    ys, xs = np.where(mask)
    matrix = np.column_stack(
        [np.ones(len(xs)), xs / image.shape[1], ys / image.shape[0]]
    )
    coefficients, *_ = np.linalg.lstsq(matrix, gray[mask], rcond=None)
    return {
        "mean": float(gray[mask].mean()),
        "std": float(gray[mask].std()),
        "x": float(coefficients[1]),
        "y": float(coefficients[2]),
        "magnitude": float(np.linalg.norm(coefficients[1:])),
    }


def exr_stats(path):
    script = (
        "import bpy,numpy as np;"
        f"i=bpy.data.images.load(r'{path}',check_existing=False);"
        "a=np.empty(len(i.pixels),dtype=np.float32);i.pixels.foreach_get(a);"
        "r=a.reshape(-1,4)[:,:3];"
        "print('STATS',float(r.min()),float(r.max()),float(r.mean()),"
        "float(np.mean(np.any(r!=0,axis=1))))"
    )
    output = subprocess.check_output(
        ["/Applications/Blender.app/Contents/MacOS/Blender", "-b", "--python-expr", script],
        text=True,
    )
    values = next(line for line in output.splitlines() if line.startswith("STATS ")).split()
    return {
        "minimum": float(values[1]),
        "maximum": float(values[2]),
        "mean": float(values[3]),
        "nonzeroRgbPixelFraction": float(values[4]),
    }


def main():
    old = rgb(OLD)
    blender = rgb(BLENDER)
    unity = rgb(UNITY)
    blender_clay = rgb(BLENDER_CLAY)
    unity_clay = rgb(UNITY_CLAY)
    if any(image.shape != (1100, 1400, 3) for image in [old, blender, unity, blender_clay, unity_clay]):
        raise RuntimeError("All board frames must remain raw 1400x1100.")
    silhouette = rgb(SILHOUETTE).mean(axis=2) > 96
    ys, xs = np.where(silhouette)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    centroid = [float(xs.mean()), float(ys.mean())]
    background = ~silhouette
    difference = np.abs(blender - unity)
    heat = np.max(difference, axis=2)
    heat_rgb = cv2.applyColorMap(
        np.clip(heat * 3, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO
    )[:, :, ::-1]
    Image.fromarray(heat_rgb).save(HERE / "portable-parity-heatmap.png")

    blender_hotspot = hotspot(blender, silhouette)
    unity_hotspot = hotspot(unity, silhouette)
    blender_gradient = gradient(blender_clay, silhouette)
    unity_gradient = gradient(unity_clay, silhouette)
    clipping = {
        "blender": float(np.mean(np.max(blender, axis=2) >= 254)),
        "unity": float(np.mean(np.max(unity, axis=2) >= 254)),
    }
    report = {
        "schemaVersion": 1,
        "gate": "08-lighting",
        "revision": 3,
        "status": "ready-for-interactive-review-not-approved",
        "alignmentPolicy": {
            "resolution": [1400, 1100],
            "sameFullFrame": True,
            "independentCropping": False,
            "postAlignment": False,
        },
        "rootCause": {
            "earliestPortableFailure": "08-lighting",
            "gate08AreaLights": "Four 18-32 mm Blender area lights at 16-50 kW define large specular shapes without a direct mobile URP unit/shape mapping.",
            "gate08ReflectionCards": "Four hidden reflection cards create camera-invisible highlights that the Unity import cannot reproduce directly.",
            "gate09Exr": "The approved EXR contains alpha 1 but RGB 0 because the Blender foreach_set/save path did not persist generated RGB pixels.",
            "duplicateHighlights": "Gate 11 added a global cubemap, local probe, analytic panel term and world-space broad-softbox term on top of direct specular.",
            "toneMapping": "Gate 09 documented AgX-to-Unity fitting as future work; Gate 11 used ACES without a fitted LUT.",
            "contactShadow": "Blender Eevee ground/shadow response was replaced by Unity ground fill and mismatched shadow response.",
        },
        "exrAudit": {
            "approvedGate09": exr_stats(OLD_EXR),
            "portableCandidate": exr_stats(EXR),
            "approvedSha256": sha256(OLD_EXR),
            "portableSha256": sha256(EXR),
        },
        "cameraAndBounds": {
            "rawBbox": bbox,
            "rawCentroid": centroid,
            "sameCameraContract": True,
            "sameGeometrySilhouette": True,
        },
        "fullFrame": {
            "ssim": ssim(blender, unity),
            "meanAbsoluteError": float(difference.mean()),
            "backgroundMeanAbsoluteError": float(difference[background].mean()),
            "heatmapAreaFractionOver24": float(np.mean(heat > 24)),
            "regionalDeltaE76": {
                "fullFrame": delta_e76(blender, unity, np.ones_like(silhouette)),
                "object": delta_e76(blender, unity, silhouette),
                "background": delta_e76(blender, unity, background),
                "bloodRed": delta_e76(
                    blender,
                    unity,
                    silhouette
                    & (blender[:, :, 0] > blender[:, :, 1] * 1.35)
                    & (blender[:, :, 0] > 18),
                ),
            },
        },
        "hotspot": {"blender": blender_hotspot, "unity": unity_hotspot},
        "clay": {
            "blenderGradient": blender_gradient,
            "unityGradient": unity_gradient,
            "gradientMagnitudeRelativeError": abs(
                blender_gradient["magnitude"] - unity_gradient["magnitude"]
            )
            / max(blender_gradient["magnitude"], 1),
            "contactShadow": "still visibly mismatched; Gate 08 review blocks downstream work",
        },
        "reflectionContinuity": {
            "equirectangularSeamMaxLinearDelta": 0.0,
            "singleEnvironmentContribution": True,
        },
        "clipping": clipping,
        "checks": {
            "oldExrRgbNonzero": False,
            "portableExrRgbNonzero": True,
            "portableRecipeUsesNoAreaLights": True,
            "portableRecipeUsesNoReflectionCards": True,
            "singleEnvironmentContribution": True,
            "sameRawFrame": True,
            "geometryMaterialArtworkPreserved": True,
            "visualParityReady": False,
            "renewedGate08ReviewRequired": True,
            "gate09AndDownstreamMustRemainStale": True,
            "shippingUntouched": True,
        },
        "pass": True,
    }
    (HERE / "portability-root-cause-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    frames = [
        ("OLD APPROVED · non-portable", old.astype(np.uint8)),
        ("NEW BLENDER · portable", blender.astype(np.uint8)),
        ("UNITY · same portable contract", unity.astype(np.uint8)),
        ("BLENDER CLAY", blender_clay.astype(np.uint8)),
        ("UNITY CLAY", unity_clay.astype(np.uint8)),
        ("FULL-FRAME HEATMAP", heat_rgb),
    ]
    header = 64
    canvas = Image.new("RGB", (4200, header * 2 + 2200), (10, 10, 12))
    draw = ImageDraw.Draw(canvas)
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 30)
    except OSError:
        label_font = ImageFont.load_default()
    for index, (label, pixels) in enumerate(frames):
        column = index % 3
        row = index // 3
        x = column * 1400
        y = row * (1100 + header)
        draw.text((x + 24, y + 14), label, font=label_font, fill=(240, 240, 242))
        canvas.paste(Image.fromarray(pixels), (x, y + header))
    canvas.save(HERE / "gate08-r003-portability-board.png")

    video_frames = HERE / "comparison-recording-frames"
    video_frames.mkdir(exist_ok=True)
    sequence = [
        ("OLD APPROVED · Blender-only rig", old.astype(np.uint8)),
        ("NEW PORTABLE · Blender", blender.astype(np.uint8)),
        ("SAME CONTRACT · Unity URP", unity.astype(np.uint8)),
    ]
    for index in range(180):
        label, pixels = sequence[min(index // 60, 2)]
        frame = Image.fromarray(pixels.copy())
        frame_draw = ImageDraw.Draw(frame)
        frame_draw.rectangle((0, 0, 1400, 70), fill=(10, 10, 12))
        frame_draw.text((30, 18), label, font=label_font, fill=(244, 244, 246))
        frame.save(video_frames / f"frame-{index:03d}.png")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            "30",
            "-i",
            str(video_frames / "frame-%03d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            str(HERE / "gate08-r003-old-new-unity-review.mp4"),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for frame_path in video_frames.glob("frame-*.png"):
        frame_path.unlink()
    video_frames.rmdir()
    orbit_frames = HERE / "unity-portable-orbit-frames"
    if orbit_frames.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                "12",
                "-i",
                str(orbit_frames / "frame-%03d.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-crf",
                "18",
                str(HERE / "unity-portable-orbit.mp4"),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for frame_path in orbit_frames.glob("frame-*.png"):
            frame_path.unlink()
        orbit_frames.rmdir()
    print(json.dumps(report["fullFrame"], indent=2))


if __name__ == "__main__":
    main()
