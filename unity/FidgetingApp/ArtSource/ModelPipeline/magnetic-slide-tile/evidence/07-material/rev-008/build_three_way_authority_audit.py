#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[8]
OUT = Path(__file__).resolve().parent
SOURCES = {
    "original_user": ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-01.jpg",
    "original_open": ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/obsidian-frames/frame-10.jpg",
    "official_red": ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/03.png",
    "blender": ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003/blender-neutral.png",
    "unity": ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-004/unity-final-object.png",
}
REGIONS = {
    "original_user": {
        "object": [180, 420, 405, 760],
        "face": [198, 445, 383, 714],
        "silver": [188, 438, 405, 735],
    },
    "original_open": {
        "object": [175, 275, 435, 735],
        "lower_artwork": [215, 548, 387, 714],
    },
    "official_red": {
        "object": [430, 385, 684, 790],
        "face": [452, 420, 669, 732],
        "silver": [430, 385, 684, 790],
    },
    "blender": {
        "object": [150, 70, 875, 545],
        "face": [215, 82, 852, 335],
        "silver": [160, 250, 870, 535],
    },
    "unity": {
        "object": [145, 55, 885, 550],
        "face": [205, 72, 852, 328],
        "silver": [165, 240, 870, 545],
    },
}


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crop(source, rect):
    return Image.open(source).convert("RGB").crop(tuple(rect))


def contain(image, size, background=(8, 11, 15)):
    result = Image.new("RGB", size, background)
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return result


def save_normalized(name, source_key):
    image = contain(crop(SOURCES[source_key], REGIONS[source_key]["object"]), (640, 560))
    path = OUT / name
    image.save(path, quality=96)
    return path


def region_metrics(source_key, region_key):
    image = np.array(crop(SOURCES[source_key], REGIONS[source_key][region_key]))
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    red = (((hsv[:, :, 0] <= 12) | (hsv[:, :, 0] >= 170))
           & (hsv[:, :, 1] >= 70) & (hsv[:, :, 2] >= 30))
    neutral = (np.max(image, axis=2) - np.min(image, axis=2) <= 18) & (hsv[:, :, 2] >= 45)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return {
        "sizePx": [int(image.shape[1]), int(image.shape[0])],
        "redPixelCount": int(red.sum()),
        "redMedianRgb": [round(float(v), 2) for v in np.median(image[red], axis=0)] if red.any() else None,
        "redLumaStd": round(float(gray[red].std()), 3) if red.any() else None,
        "neutralPixelCount": int(neutral.sum()),
        "neutralMedianLStar": round(float(np.median(lab[:, :, 0][neutral]) * 100 / 255), 3) if neutral.any() else None,
        "laplacianVariance": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 3),
    }


def mark(draw, box, number, color):
    draw.rounded_rectangle(box, radius=12, outline=color, width=5)
    x, y = box[0], box[1]
    draw.ellipse((x - 2, y - 2, x + 42, y + 42), fill=color)
    draw.text((x + 11, y + 3), str(number), font=font(25, True), fill=(7, 9, 12))


def build_board(normalized):
    board = Image.new("RGB", (2100, 1680), (7, 10, 14))
    draw = ImageDraw.Draw(board)
    draw.text((70, 42), "外观权威链复核", font=font(54, True), fill=(245, 247, 250))
    draw.text((70, 112), "先看原图，不再把 Blender 当最终标准", font=font(30), fill=(174, 184, 197))

    headers = ["原图标准", "Blender 当前", "Unity 当前"]
    x_positions = [55, 735, 1415]
    keys = ["original", "blender", "unity"]
    for x, header, key in zip(x_positions, headers, keys):
        draw.rounded_rectangle((x, 185, x + 630, 870), radius=28, fill=(18, 23, 31))
        draw.text((x + 24, 205), header, font=font(38, True), fill=(244, 246, 249))
        board.paste(Image.open(normalized[key]), (x - 5, 275))

    mark(draw, (205, 352, 525, 745), 1, (224, 62, 73))
    mark(draw, (170, 325, 578, 785), 2, (225, 230, 236))
    mark(draw, (786, 365, 1320, 620), 1, (224, 62, 73))
    mark(draw, (760, 520, 1350, 785), 2, (225, 230, 236))
    mark(draw, (1465, 360, 1995, 620), 1, (224, 62, 73))
    mark(draw, (1448, 520, 2020, 790), 2, (225, 230, 236))

    draw.text((75, 900), "1  血红晶体与图案", font=font(32, True), fill=(238, 91, 100))
    draw.text((75, 950), "原图有碎裂亮暗、透明层次和局部虹彩。Blender 已变成均匀平涂；Unity 只是继续追随这个错误目标。",
              font=font(27), fill=(224, 229, 236))
    draw.text((75, 1020), "2  银色与黑色外圈", font=font(32, True), fill=(232, 236, 242))
    draw.text((75, 1070), "原图银边有明暗环境反射；黑边完整但仍能分出材质层。Blender 银面偏平灰，Unity 又进一步变暗像塑料。",
              font=font(27), fill=(224, 229, 236))

    draw.rounded_rectangle((55, 1150, 2045, 1530), radius=28, fill=(22, 28, 37))
    draw.text((90, 1184), "结论：最早出错的是第 7 关材质", font=font(43, True), fill=(255, 205, 96))
    draw.text((90, 1255), "保持不动：外形、面数、轴心、滑动方式、上下图案位置与可替换能力。",
              font=font(30), fill=(236, 239, 244))
    draw.text((90, 1315), "要重做：先按原图重建血红晶体、亮银反射和黑边材质；之后第 8–11 关全部重新验证。",
              font=font(30), fill=(236, 239, 244))
    draw.text((90, 1375), "现在不继续调 Unity，也不进入第 12 关，不构建、不安装、不推送手机。",
              font=font(30), fill=(236, 239, 244))
    draw.text((90, 1460), "请确认：是否同意退回第 7 关，以原图为标准重做 Blender 材质？",
              font=font(34, True), fill=(255, 224, 143))
    draw.text((70, 1595), "原图用于材质判断；Blender 与 Unity 使用同机位判断导入差异。不同镜头不做轮廓像素结论。",
              font=font(24), fill=(147, 159, 174))
    path = OUT / "gate07-rev8-three-way-authority-audit.png"
    board.save(path, quality=96)
    return path


def main():
    for source in SOURCES.values():
        if not source.exists():
            raise FileNotFoundError(source)
    normalized = {
        "original": save_normalized("normalized-original-authority.png", "original_user"),
        "blender": save_normalized("normalized-blender-current.png", "blender"),
        "unity": save_normalized("normalized-unity-current.png", "unity"),
    }
    board = build_board(normalized)
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 8,
        "auditType": "three-way-source-of-truth",
        "authorityOrder": [
            "original user/exact-product appearance references",
            "Blender implementation",
            "Unity implementation",
        ],
        "sourceAssetIds": [
            "slider-intake-obs-frame-01",
            "slider-intake-obs-frame-10",
            "slider-intake-haloo-official-03",
            "magnetic-slide-tile-unity-parity-rev3-blender-target-r003",
            "magnetic-slide-tile-unity-parity-rev4-unity-final-r004",
        ],
        "regions": REGIONS,
        "metrics": {
            "originalFace": region_metrics("original_user", "face"),
            "officialFaceCrossCheck": region_metrics("official_red", "face"),
            "blenderFace": region_metrics("blender", "face"),
            "unityFace": region_metrics("unity", "face"),
            "blenderSilver": region_metrics("blender", "silver"),
            "unitySilver": region_metrics("unity", "silver"),
        },
        "diagnosis": {
            "geometry": "hold-constant",
            "artworkPlacement": "hold-constant",
            "earliestDivergenceGate": "07-material",
            "bloodRedCrystal": "Blender already lacks the source's fractured highlight variation, apparent transparent depth and restrained iridescence.",
            "silver": "Blender already reduces the source's layered polished reflection to broad flat gray; Unity darkens it further.",
            "border": "The full perimeter decision remains locked, but reflectance and separation must be rebuilt at Gate 07.",
            "lightingColorManagement": "Gate 08-09 metrics validated Blender against its own numeric target, not against normalized original-reference regions.",
            "unity": "Gate 11 is downstream evidence, not the root correction gate.",
        },
        "lockedDecisionsPreserved": [
            "deep blood red, not pink",
            "bright polished silver-white",
            "crisp clean prior motif mask",
            "full black top perimeter with silver side wall",
            "crystalline brightness/depth",
            "independently replaceable upper/lower artwork",
            "exact geometry/pivot/slide semantics",
        ],
        "stageAction": {
            "gate07": "ready_for_review-authority-correction",
            "gates08To11": "stale",
            "gate12": "blocked-rejected-preserved",
            "buildInstallPhone": "not-started",
        },
        "reviewQuestion": "是否同意退回第 7 关，以原图为标准重做 Blender 材质？",
        "normalizedCropPolicy": "Original references provide material cues. Blender and Unity share a camera for parity. Different cameras are not used for silhouette pixel metrics.",
        "artifacts": {path.name: sha256(path) for path in [*normalized.values(), board]},
        "pass": True,
    }
    (OUT / "three-way-authority-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
