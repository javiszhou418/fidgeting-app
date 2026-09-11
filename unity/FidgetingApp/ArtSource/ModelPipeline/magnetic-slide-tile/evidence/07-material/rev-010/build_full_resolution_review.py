#!/usr/bin/env python3
"""Compose full-resolution Gate 07 rev 10 review boards."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
REV9 = OUT.parent / "rev-009"
REPORT = OUT / "material-axis-validation.json"


def font(size, bold=False):
    path = "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc"
    return ImageFont.truetype(path, size=size)


def contain(path, size):
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (7, 10, 14))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def axis_overlay(path, record, size=(1500, 1050)):
    image = Image.open(path).convert("RGB")
    sx = image.width / 1600
    sy = image.height / 1200
    px = record["axisPixel"][0] * sx
    py = record["axisPixel"][1] * sy
    draw = ImageDraw.Draw(image)
    cyan = (44, 224, 239)
    radius = 30
    draw.ellipse((px - radius, py - radius, px + radius, py + radius), outline=cyan, width=5)
    draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=cyan)
    draw.line((px - 48, py, px - 15, py), fill=cyan, width=5)
    draw.line((px + 15, py, px + 48, py), fill=cyan, width=5)
    draw.line((px, py - 48, px, py - 15), fill=cyan, width=5)
    draw.line((px, py + 15, px, py + 48), fill=cyan, width=5)
    label = f"[0,-9.5,0] mm  +Z ⊙  {record['angleDeg']}° / detent {record['detentIndex']}"
    label_box = draw.textbbox((0, 0), label, font=font(30, True))
    label_w = label_box[2] - label_box[0]
    lx = min(max(px + 44, 22), image.width - label_w - 32)
    ly = min(max(py - 66, 22), image.height - 58)
    draw.rounded_rectangle((lx - 12, ly - 8, lx + label_w + 12, ly + 45), radius=10, fill=(4, 14, 20, 220))
    draw.text((lx, ly), label, font=font(30, True), fill=cyan)
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (7, 10, 14))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def build_axis_board(report):
    board = Image.new("RGB", (3200, 2550), (6, 9, 13))
    draw = ImageDraw.Draw(board)
    draw.text((80, 55), "轴心与棘轮角度证据｜材质仍是本关评审对象", font=font(60, True), fill=(246, 248, 251))
    draw.text((80, 130), "世界轴点 [0,-9.5,0] mm｜+Z｜360° / 12° = 30 detents｜青色十字不遮挡主要材质。", font=font(31), fill=(181, 195, 210))
    draw.text((80, 178), "每个旋转姿态：UpperTranslation = [0,0,0] mm；pivot drift = 0 mm。45° 不作为主姿态。", font=font(31), fill=(181, 195, 210))
    records = report["motionEvidence"]["spin"]
    positions = [(80, 250), (1650, 250), (80, 1370)]
    for record, position in zip(records, positions):
        image = axis_overlay(OUT / record["render"], record)
        board.paste(image, position)
        caption = f"{record['angleDeg']}°｜detent {record['detentIndex']}｜平移 0 mm｜轴漂移 0 mm"
        draw.text((position[0], position[1] + 1070), caption, font=font(34, True), fill=(44, 224, 239))
    slide = contain(OUT / report["motionEvidence"]["slide"]["render"], (1450, 1050))
    board.paste(slide, (1650, 1370))
    draw.text((1650, 2440), "独立滑开姿态｜+21 mm｜0° 旋转", font=font(34, True), fill=(245, 181, 67))
    path = OUT / "axis-angle-evidence-board.png"
    board.save(path)
    return path


def source_crop(path, crop=None, size=(760, 700)):
    image = Image.open(path).convert("RGB")
    if crop:
        image = image.crop(crop)
    scale = min(size[0] / image.width, size[1] / image.height)
    image = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGB", size, (7, 10, 14))
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def build_source_board():
    board = Image.new("RGB", (3240, 2520), (6, 9, 13))
    draw = ImageDraw.Draw(board)
    draw.text((80, 55), "原图 → Blender｜Gate 07 rev 10 材质与下片图案", font=font(60, True), fill=(246, 248, 251))
    draw.text((80, 132), "大图逐项比较；原图是外观唯一权威。下片绿色区为实拍直见，遮挡区为明确标注的重建。", font=font(31), fill=(181, 195, 210))
    comparisons = [
        (
            source_crop(REV9 / "source-normalized-front.png", (300, 300, 480, 540)),
            contain(OUT / "upper-front.png", (760, 700)),
            "上片正面｜深血红、亮暗红晶片、黑色锐利图案",
        ),
        (
            source_crop(OUT / "lower-rectified-user-frame-10.png", (0, 350, 620, 1000)),
            contain(OUT / "lower-open-macro.png", (760, 700)),
            "下片展开｜独立图案，不再复制上片",
        ),
        (
            source_crop(REV9 / "source-normalized-oblique.png", (310, 225, 505, 590)),
            contain(OUT / "oblique-crystal.png", (760, 700)),
            "斜视晶体｜颗粒箔片、局部亮暗、透明盖层",
        ),
        (
            source_crop(REV9 / "source-normalized-front.png", (305, 300, 360, 540)),
            contain(OUT / "side-rim.png", (760, 700)),
            "边框与侧身｜细亮银边、暗黑侧面、窄反射线",
        ),
    ]
    positions = [(80, 230), (1640, 230), (80, 1360), (1640, 1360)]
    for (source, render, caption), (x, y) in zip(comparisons, positions):
        board.paste(source, (x, y))
        board.paste(render, (x + 780, y))
        draw.text((x, y - 42), "原图", font=font(30, True), fill=(194, 204, 216))
        draw.text((x + 780, y - 42), "Blender", font=font(30, True), fill=(194, 204, 216))
        draw.text((x, y + 718), caption, font=font(29, True), fill=(236, 240, 245))
    path = OUT / "source-fidelity-review-board.png"
    board.save(path)
    return path


def build_closeup_board():
    board = Image.new("RGB", (3200, 1900), (6, 9, 13))
    draw = ImageDraw.Draw(board)
    draw.text((80, 55), "材质全分辨率近照｜零自发光、零 Bloom", font=font(60, True), fill=(246, 248, 251))
    panels = [
        ("晶体颗粒／微闪／盖层", "crystal-microflake-macro.png"),
        ("斜视红晶与角度色", "oblique-crystal.png"),
        ("银边与暗侧身反射", "side-rim.png"),
        ("下片独立图案", "lower-open-macro.png"),
    ]
    for index, (label, filename) in enumerate(panels):
        x = 80 + (index % 2) * 1560
        y = 180 + (index // 2) * 830
        board.paste(contain(OUT / filename, (1480, 730)), (x, y))
        draw.text((x, y + 745), label, font=font(32, True), fill=(231, 236, 242))
    path = OUT / "material-closeups-board.png"
    board.save(path)
    return path


def main():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    required = [
        "upper-front.png", "oblique-crystal.png", "side-rim.png",
        "crystal-microflake-macro.png", "lower-open-macro.png",
        "spin-00deg.png", "spin-12deg.png", "spin-36deg.png",
        "slide-open-21mm-0deg.png",
    ]
    for filename in required:
        if not (OUT / filename).exists():
            raise FileNotFoundError(OUT / filename)
    paths = [build_source_board(), build_closeup_board(), build_axis_board(report)]
    result = {
        "schemaVersion": 1,
        "gate": "07-material",
        "revision": 10,
        "reviewQuestion": "现在这个 Blender 材质和下片图案像原来的实物吗？",
        "technicalDetailsCollapsed": True,
        "boards": [path.name for path in paths],
        "axisEvidence": report["motionEvidence"],
    }
    (OUT / "review-board-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
