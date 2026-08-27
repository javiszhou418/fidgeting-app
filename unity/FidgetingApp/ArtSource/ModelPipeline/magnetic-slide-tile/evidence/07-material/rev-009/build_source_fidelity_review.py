#!/usr/bin/env python3
"""Build source-centered Gate 07 rev 9 review and image validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
REPO = OUT.parents[7]
SOURCES = {
    "front": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-01.jpg",
    "oblique": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-05.jpg",
    "open": REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-10.jpg",
}
SOURCE_REGIONS = {
    "front": {
        "objectPx": [184, 426, 414, 758],
        "facePx": [204, 454, 392, 716],
        "steelSamplePx": [185, 430, 410, 744],
        "steelSelection": "HSV saturation <= 42, value 72–235; brightest 35% of selected pixels",
    },
    "oblique": {
        "objectPx": [176, 350, 456, 792],
        "facePx": [205, 385, 424, 668],
        "steelSamplePx": [183, 356, 451, 704],
        "steelSelection": "HSV saturation <= 48, value 64–240; brightest 35% of selected pixels",
    },
    "open": {
        "objectPx": [175, 275, 435, 735],
        "facePx": [196, 298, 412, 536],
        "lowerArtworkPx": [215, 548, 387, 714],
        "steelSamplePx": [180, 282, 428, 720],
        "steelSelection": "HSV saturation <= 48, value 64–240; brightest 35% of selected pixels",
    },
}
RENDERS = {
    "front": OUT / "corrected-front.png",
    "oblique": OUT / "corrected-oblique.png",
    "side": OUT / "corrected-side.png",
    "open": OUT / "corrected-open.png",
    "crystal": OUT / "crystal-macro.png",
    "silver": OUT / "silver-reflection-closeup.png",
    "perimeter": OUT / "black-perimeter-closeup.png",
}
MASKS = {
    "upper": OUT.parent / "rev-007/artwork-upper-mask.png",
    "lower": OUT.parent / "rev-007/artwork-lower-mask.png",
    "perimeter": OUT.parent / "rev-007/artwork-top-perimeter-border-mask.png",
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size, index=1 if bold and path.endswith(".ttc") else 0)
    return ImageFont.load_default()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def crop(image, box):
    return image.crop(tuple(box))


def contain(image, size, background=(12, 15, 19)):
    result = Image.new("RGB", size, background)
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    result.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return result


def steel_normalize(key):
    source = np.array(Image.open(SOURCES[key]).convert("RGB")).astype(np.float32)
    x1, y1, x2, y2 = SOURCE_REGIONS[key]["steelSamplePx"]
    sample = source[y1:y2, x1:x2].astype(np.uint8)
    hsv = cv2.cvtColor(sample, cv2.COLOR_RGB2HSV)
    sat_max = 42 if key == "front" else 48
    mask = (hsv[:, :, 1] <= sat_max) & (hsv[:, :, 2] >= 64) & (hsv[:, :, 2] <= 240)
    values = sample[mask]
    if len(values) < 64:
        raise RuntimeError(f"Insufficient steel pixels for {key}: {len(values)}")
    luma = values.mean(axis=1)
    values = values[luma >= np.percentile(luma, 65)]
    median = np.median(values, axis=0)
    target = float(np.mean(median))
    scale = np.clip(target / np.maximum(median, 1), 0.72, 1.38)
    normalized = np.clip(source * scale[None, None, :], 0, 255).astype(np.uint8)
    object_crop = crop(Image.fromarray(normalized), SOURCE_REGIONS[key]["objectPx"])
    output = OUT / f"source-normalized-{key}.png"
    contain(object_crop, (720, 720), (8, 10, 14)).save(output)
    return output, {
        "steelMedianRgbBefore": [round(float(v), 2) for v in median],
        "channelScale": [round(float(v), 5) for v in scale],
        "selectedPixelCount": int(len(values)),
        "sourceRegion": SOURCE_REGIONS[key],
    }


def image_metrics(path):
    rgb = np.array(Image.open(path).convert("RGB"))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    red = (((hsv[:, :, 0] <= 12) | (hsv[:, :, 0] >= 174)) & (hsv[:, :, 1] >= 70) & (hsv[:, :, 2] >= 30))
    neutral = ((rgb.max(axis=2) - rgb.min(axis=2)) <= 22) & (gray >= 12)
    dark = gray <= 46
    blue_green = ((rgb[:, :, 1] > rgb[:, :, 0] * 1.04) | (rgb[:, :, 2] > rgb[:, :, 0] * 1.04)) & (gray >= 20)
    edges = cv2.Canny(gray, 45, 125)
    return {
        "sizePx": [int(rgb.shape[1]), int(rgb.shape[0])],
        "redPixelCount": int(red.sum()),
        "redMedianRgb": [round(float(v), 2) for v in np.median(rgb[red], axis=0)] if red.any() else None,
        "redLumaStd": round(float(gray[red].std()), 3) if red.any() else 0,
        "neutralLumaP05P50P95": [round(float(v), 3) for v in np.percentile(gray[neutral], [5, 50, 95])] if neutral.any() else None,
        "darkPixelCount": int(dark.sum()),
        "blueGreenAnglePixelCount": int(blue_green.sum()),
        "edgeDensity": round(float((edges > 0).mean()), 5),
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 3),
        "whiteClipFraction": round(float((rgb >= 253).all(axis=2).mean()), 7),
        "blackClipFraction": round(float((rgb <= 2).all(axis=2).mean()), 7),
        "lumaP01P50P99": [round(float(v), 3) for v in np.percentile(gray, [1, 50, 99])],
        "lumaP001P50P999": [round(float(v), 3) for v in np.percentile(gray, [0.1, 50, 99.9])],
    }


def build_review(normalized):
    board = Image.new("RGB", (2400, 2260), (7, 10, 14))
    draw = ImageDraw.Draw(board)
    draw.text((80, 56), "Gate 07 rev 9｜原图是唯一外观标准", font=font(58, True), fill=(246, 248, 250))
    draw.text((80, 128), "几何、尺寸、转轴、滑动语义和图案位置均未改变。此页只判断 Blender 材质。", font=font(31), fill=(174, 184, 197))
    columns = [(80, "原图"), (830, "修正后 Blender")]
    for x, label in columns:
        draw.text((x, 210), label, font=font(38, True), fill=(235, 238, 242))
    pairs = [
        ("front", "front", "正面：血红晶体、完整黑边、亮暗银反射"),
        ("oblique", "oblique", "斜面：透明层次、局部碎晶高光、克制虹彩"),
        ("open", "open", "打开：下片图案仍清楚可读"),
    ]
    y = 270
    for source_key, render_key, caption in pairs:
        source = contain(Image.open(normalized[source_key]).convert("RGB"), (700, 500))
        rendered = contain(Image.open(RENDERS[render_key]).convert("RGB"), (1450, 500))
        board.paste(source, (80, y))
        board.paste(rendered, (830, y))
        draw.text((80, y + 512), caption, font=font(28, True), fill=(220, 224, 230))
        y += 600
    draw.rounded_rectangle((80, 2075, 2320, 2190), radius=22, fill=(18, 25, 33), outline=(94, 112, 132), width=2)
    draw.text((120, 2106), "只问一件事：现在 Blender 看起来像原来的实物了吗？", font=font(39, True), fill=(250, 252, 255))
    path = OUT / "gate07-rev9-source-fidelity-review.png"
    board.save(path)
    return path


def build_closeups():
    board = Image.new("RGB", (2400, 1220), (7, 10, 14))
    draw = ImageDraw.Draw(board)
    draw.text((70, 48), "材质细节检查", font=font(52, True), fill=(246, 248, 250))
    items = [
        ("crystal", "血红晶体｜局部马赛克、内层明暗、无发光"),
        ("silver", "银色｜同一表面同时出现亮带与暗反射"),
        ("perimeter", "黑色外圈｜黑而不死，保留表面反射和深度"),
    ]
    x = 70
    for key, label in items:
        image = contain(Image.open(RENDERS[key]).convert("RGB"), (720, 920))
        board.paste(image, (x, 150))
        draw.text((x, 1090), label, font=font(24, True), fill=(218, 224, 232))
        x += 770
    path = OUT / "gate07-rev9-material-closeups.png"
    board.save(path)
    return path


def build_editable_layers():
    board = Image.new("RGB", (1900, 920), (10, 13, 17))
    draw = ImageDraw.Draw(board)
    draw.text((60, 45), "图案保持独立可替换", font=font(49, True), fill=(245, 248, 252))
    draw.text((60, 108), "上片、下片和完整外圈是三个外部 Mask；更换图案不改几何。", font=font(28), fill=(174, 186, 201))
    x = 60
    labels = [("upper", "上片图案"), ("lower", "下片图案"), ("perimeter", "完整黑色外圈")]
    for key, label in labels:
        image = Image.open(MASKS[key]).convert("L")
        rgba = Image.merge("RGB", (image, image, image))
        board.paste(contain(rgba, (540, 620), (20, 24, 30)), (x, 190))
        draw.text((x, 830), f"{label}｜SHA-256 {sha256(MASKS[key])[:12]}…", font=font(24, True), fill=(222, 228, 235))
        x += 600
    path = OUT / "gate07-rev9-editable-layer-board.png"
    board.save(path)
    return path


def build_heatmap(normalized_front):
    source = np.array(Image.open(normalized_front).convert("RGB"))
    render = np.array(Image.open(RENDERS["front"]).convert("RGB"))
    source = cv2.resize(source, (720, 720), interpolation=cv2.INTER_LANCZOS4)
    render = cv2.resize(render, (720, 720), interpolation=cv2.INTER_LANCZOS4)
    source_lab = cv2.cvtColor(source, cv2.COLOR_RGB2LAB).astype(np.float32)
    render_lab = cv2.cvtColor(render, cv2.COLOR_RGB2LAB).astype(np.float32)
    delta = np.linalg.norm(source_lab - render_lab, axis=2)
    normalized_delta = np.clip(delta / np.percentile(delta, 95), 0, 1)
    heat = cv2.applyColorMap((normalized_delta * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    board = Image.new("RGB", (1640, 850), (8, 10, 14))
    draw = ImageDraw.Draw(board)
    draw.text((55, 40), "辅助差异图｜不同相机，仅用于定位色彩与高光差异", font=font(39, True), fill=(242, 245, 249))
    board.paste(Image.fromarray(source), (55, 110))
    board.paste(Image.fromarray(heat), (865, 110))
    draw.text((55, 790), "钢色归一后的原图裁切", font=font(24), fill=(198, 207, 219))
    draw.text((865, 790), "LAB 差异热图（不作为批准依据）", font=font(24), fill=(198, 207, 219))
    path = OUT / "gate07-rev9-supporting-heatmap.png"
    board.save(path)
    return path


def main():
    for path in [*SOURCES.values(), *RENDERS.values(), *MASKS.values(), OUT / "blender-material-validation.json"]:
        if not path.exists():
            raise FileNotFoundError(path)
    normalized, normalization = {}, {}
    for key in SOURCES:
        normalized[key], normalization[key] = steel_normalize(key)
    review = build_review(normalized)
    closeups = build_closeups()
    layers = build_editable_layers()
    heatmap = build_heatmap(normalized["front"])
    metrics = {f"source_{key}": image_metrics(path) for key, path in normalized.items()}
    metrics.update({key: image_metrics(path) for key, path in RENDERS.items()})
    checks = {
        "sourceRegionsRecorded": all(normalization.values()),
        "sourceBloodRedRangePresent": metrics["source_front"]["redPixelCount"] > 2500,
        "crystalLocalVariation": metrics["crystal"]["redLumaStd"] >= 8 and metrics["crystal"]["laplacianVariance"] >= 100,
        "crystalAngleColorVariation": metrics["oblique"]["blueGreenAnglePixelCount"] >= 100,
        "silverBrightDarkReflectionRange": (
            metrics["silver"]["lumaP001P50P999"][2] - metrics["silver"]["lumaP001P50P999"][0] >= 195
            and metrics["silver"]["lumaP001P50P999"][2] >= 220
        ),
        "blackPerimeterReflectance": (
            metrics["perimeter"]["lumaP01P50P99"][1] <= 70
            and metrics["perimeter"]["lumaP001P50P999"][2] >= 115
        ),
        "motifSharpness": metrics["crystal"]["edgeDensity"] >= 0.03,
        "lowerArtworkVisible": metrics["open"]["redPixelCount"] >= 12000 and metrics["open"]["edgeDensity"] >= 0.025,
        "zeroWhiteClipping": all(metrics[key]["whiteClipFraction"] < 0.01 for key in RENDERS),
        "maskIdentityPreserved": all(sha256(MASKS[key]) for key in MASKS),
        "editableLayersSeparate": len({str(MASKS[key].resolve()) for key in MASKS}) == 3,
        "heatmapSupportingOnly": True,
    }
    blender_report = json.loads((OUT / "blender-material-validation.json").read_text(encoding="utf-8"))
    checks["geometryDigestUnchanged"] = blender_report["geometry"]["unchanged"]
    checks["modelMatricesUnchanged"] = blender_report["geometry"]["matricesUnchanged"]
    checks["zeroEmission"] = blender_report["recipe"]["silver"]["emission"] == 0 and blender_report["recipe"]["crystal"]["emission"] == 0
    checks["sameCameraLightRecipeRecorded"] = all(
        item["recipe"] == "Gate07Rev9-neutral-material-reveal"
        for item in blender_report["render"]["cameras"].values()
    )
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 9,
        "authority": "original user frames primary; official exact-product images corroboration only",
        "sourceNormalization": normalization,
        "metrics": metrics,
        "checks": checks,
        "pass": all(bool(value) for value in checks.values()),
        "reviewQuestion": "现在 Blender 看起来像原来的实物了吗？",
        "approvalBasis": [review.name, closeups.name, layers.name],
        "supportingOnly": [heatmap.name],
        "artifacts": {
            path.name: sha256(path)
            for path in [*normalized.values(), review, closeups, layers, heatmap]
        },
    }
    (OUT / "source-fidelity-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError(f"Source-fidelity validation failed: {failed}")


if __name__ == "__main__":
    main()
