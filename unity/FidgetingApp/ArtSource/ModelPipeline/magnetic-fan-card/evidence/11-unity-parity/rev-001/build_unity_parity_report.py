"""Compare Blender and Unity neutral captures for Gate 11 parity."""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
BLENDER = HERE / "blender-neutral.png"
UNITY = HERE / "unity-neutral.png"
BLENDER_REPORT = HERE / "blender-neutral-report.json"
UNITY_REPORT = HERE / "unity-neutral-report.json"
REPORT = HERE / "parity-report.json"
OVERLAY = HERE / "silhouette-overlay.png"
CONTACT = HERE / "unity-parity-contact-sheet.png"
FONT = "/System/Library/Fonts/SFNS.ttf"


def font(size: int, variation: str):
    value = ImageFont.truetype(FONT, size)
    try:
        value.set_variation_by_name(variation)
    except OSError:
        pass
    return value


def mask(image: Image.Image) -> list[bool]:
    pixels = image.convert("RGB").getdata()
    return [
        max(red, green, blue) >= 28
        for red, green, blue in pixels
    ]


def mask_stats(
    values: list[bool],
    width: int,
    height: int,
) -> dict:
    indices = [index for index, value in enumerate(values) if value]
    xs = [index % width for index in indices]
    ys = [index // width for index in indices]
    return {
        "areaPixels": len(indices),
        "areaFraction": len(indices) / (width * height),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "centroid": [
            sum(xs) / len(xs),
            sum(ys) / len(ys),
        ],
    }


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (9, 10, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def main() -> None:
    blender_image = Image.open(BLENDER).convert("RGB")
    unity_image = Image.open(UNITY).convert("RGB")
    if blender_image.size != unity_image.size:
        raise ValueError("Neutral captures have different dimensions.")
    width, height = blender_image.size
    blender_mask = mask(blender_image)
    unity_mask = mask(unity_image)
    intersection = sum(
        left and right
        for left, right in zip(blender_mask, unity_mask)
    )
    union = sum(
        left or right
        for left, right in zip(blender_mask, unity_mask)
    )
    iou = intersection / union
    blender_stats = mask_stats(blender_mask, width, height)
    unity_stats = mask_stats(unity_mask, width, height)
    bbox_error = max(
        abs(left - right) / axis
        for left, right, axis in zip(
            blender_stats["bbox"],
            unity_stats["bbox"],
            (width, height, width, height),
        )
    )
    centroid_error = math.dist(
        blender_stats["centroid"],
        unity_stats["centroid"],
    ) / math.hypot(width, height)
    area_ratio = (
        unity_stats["areaPixels"] / blender_stats["areaPixels"])

    overlay = Image.new("RGB", (width, height), (0, 0, 0))
    overlay.putdata([
        (236, 232, 218)
        if left and right
        else (44, 196, 209)
        if left
        else (221, 67, 153)
        if right
        else (0, 0, 0)
        for left, right in zip(blender_mask, unity_mask)
    ])
    overlay.save(OVERLAY)

    blender_report = json.loads(BLENDER_REPORT.read_text(encoding="utf-8"))
    unity_report = json.loads(UNITY_REPORT.read_text(encoding="utf-8"))
    image_checks = {
        "silhouetteIouAtLeast085": iou >= 0.85,
        "bboxEdgeErrorAtMost5Percent": bbox_error <= 0.05,
        "centroidErrorAtMost3Percent": centroid_error <= 0.03,
        "areaRatioWithin10Percent": 0.90 <= area_ratio <= 1.10,
    }
    numeric_checks = {
        "unityImporterPass": unity_report["pass"],
        "triangleCountPreserved": (
            blender_report["triangles"] == unity_report["triangles"] == 34284),
        "meshObjectCountPreserved": (
            blender_report["meshObjects"] == unity_report["meshObjects"] == 32),
        "boundsWithinOnePercent": (
            unity_report["boundsRelativeError"] <= 0.01),
        "rankMeshesPreserved": unity_report["rankMeshes"] == 6,
        "trackDistributionPreserved": (
            unity_report["bottomTrackObjects"] == 0
            and unity_report["middleTopTrackObjects"] == 4),
        "collisionMeshesPreserved": unity_report["collisionMeshes"] == 3,
    }
    passed = all(image_checks.values()) and all(numeric_checks.values())
    report = {
        "modelId": "magnetic-fan-card",
        "gate": "11-unity-parity",
        "viewId": "hero",
        "cameraRecipe": "neutral-camera-recipe.json",
        "imageComparison": {
            "resolution": [width, height],
            "threshold": 28,
            "silhouetteIou": round(iou, 7),
            "bboxEdgeError": round(bbox_error, 7),
            "centroidError": round(centroid_error, 7),
            "areaRatioUnityOverBlender": round(area_ratio, 7),
            "blender": blender_stats,
            "unity": unity_stats,
            "checks": image_checks,
        },
        "numericChecks": numeric_checks,
        "blenderReport": blender_report,
        "unityReport": unity_report,
        "pass": passed,
        "shippingIntegrated": False,
        "deviceValidated": False,
    }
    REPORT.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")

    canvas = Image.new("RGB", (2850, 780), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (30, 20),
        "GATE 11 · BLENDER ↔ UNITY PARITY",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (30, 62),
        "Same exported FBX and hero camera. White = overlap; cyan = Blender only; magenta = Unity only.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        (
            BLENDER,
            "BLENDER NEUTRAL",
            f"{blender_report['triangles']:,} tris · "
            f"{blender_report['meshObjects']} meshes",
        ),
        (
            UNITY,
            "UNITY 6000.5.6f1",
            f"bounds error {unity_report['boundsRelativeError']:.8%} · "
            "hierarchy PASS",
        ),
        (
            OVERLAY,
            "SILHOUETTE OVERLAY",
            f"IoU {iou:.4f} · bbox {bbox_error:.2%} · "
            f"centroid {centroid_error:.2%}",
        ),
    )
    for index, (path, title, subtitle) in enumerate(panels):
        x = 25 + index * 940
        y = 105
        draw.rounded_rectangle(
            (x, y, x + 915, y + 645),
            radius=20,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(path, (885, 540)), (x + 15, y + 15))
        draw.text(
            (x + 24, y + 567),
            title,
            font=font(21, "Bold"),
            fill=(223, 174, 78),
        )
        draw.text(
            (x + 24, y + 601),
            subtitle,
            font=font(16, "Regular"),
            fill=(184, 184, 180),
        )
    canvas.save(CONTACT)
    if not passed:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
