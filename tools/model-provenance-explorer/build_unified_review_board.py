"""Review board for the unified tri-spinner Gate 05/06 checkpoint.

Usage: python3 build_unified_review_board.py [rev-004]
Writes /tmp/dragon-scale-gate02/20-unified-review-<rev>.png plus single views,
and copies the board into the Gate 06 evidence folder as review-board.png.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
EV = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence"
REV = sys.argv[1] if len(sys.argv) > 1 else "rev-004"
G06 = EV / f"06-geometry/{REV}"
G05 = EV / f"05-blockout/{REV}"
VAR = EV / f"06-geometry/{REV}-variant-table-0797"
REF = EV / "01-intake/rev-002/obsidian-geeone-product"
OUT = Path("/tmp/dragon-scale-gate02")

PANELS = [
    (G06 / "geometry-hero.png", "Hero · Cycles 金属"),
    (G06 / "geometry-top.png", "Top · 正交（机身不可见）"),
    (G06 / "geometry-cap-macro.png", "帽体微距 · 圆台 + 48 三角楔"),
    (G06 / "geometry-cap-profile.png", "帽体侧仰 · 平盘最高、楔面下斜"),
    (G06 / "geometry-notch-macro.png", "叶片缺口 · 竖直侧壁 + 屋脊"),
    (G06 / "geometry-low.png", "Low · 低角"),
    (G06 / "geometry-workbench.png", "Workbench · 无材质真几何"),
    (G05 / "blockout-hero.png", "Gate 05 白模"),
]
REFERENCE = [
    (REF / "geeone-01.jpg", (40, 300, 700, 900), "参考 geeone-01"),
    (REF / "geeone-02.jpg", (40, 250, 700, 850), "参考 geeone-02"),
]
VARIANTS = [
    (G06 / "geometry-cap-profile.png", "台面 0.70（用户指示，本版）"),
    (VAR / "geometry-cap-profile.png", "台面 0.797（照片量得，仅对比）"),
    (G06 / "geometry-hero.png", "0.70 · 楔环宽 5.2 mm，外沿低于叶面 0.94 mm"),
    (VAR / "geometry-hero.png", "0.797 · 楔环宽 3.5 mm，外沿与叶面齐平"),
]


def font(size: int):
    for candidate in ("/System/Library/Fonts/STHeiti Medium.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/PingFang.ttc"):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def paste_fit(board: Image.Image, path: Path, box: tuple[int, int, int, int], crop=None) -> None:
    x, y, w, h = box
    with Image.open(path) as raw:
        img = raw.convert("RGB")
        if crop:
            img = img.crop(crop)
        img.thumbnail((w, h), Image.LANCZOS)
        board.paste(img, (x + (w - img.width) // 2, y + (h - img.height) // 2))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cell, pad, cap = 470, 16, 44
    cols, rows = 4, 2
    small_h = 330
    width = cols * cell + (cols + 1) * pad
    section2 = 70 + small_h + cap + pad
    section3 = 70 + small_h + cap + pad
    height = 96 + rows * (cell + cap + pad) + section2 + section3
    board = Image.new("RGB", (width, height), (13, 13, 15))
    draw = ImageDraw.Draw(board)
    draw.text((pad, 22), f"统一三叶陀螺 {REV} · Gate 05/06 评审（Blender Cycles 真实渲染，未进 Unity）", fill=(245, 245, 245), font=font(38))
    draw.text((pad, 66), "65 mm provisional · 盖 0.536 · 平盘 0.70 为最高点 · 楔环 25° 圆锥 + 锯齿沿 48 三角 · 盖高出叶面 1.5 mm · 暗缝 0.8 mm · 叶片 11.5 mm 厚、泪滴轮廓、60° 缺口、R12 外弧、屋脊 + 端面斜切 · 0.5 mm 倒角", fill=(170, 175, 185), font=font(20))

    for index, (path, label) in enumerate(PANELS):
        c, r = index % cols, index // cols
        x = pad + c * (cell + pad)
        y = 96 + r * (cell + cap + pad)
        paste_fit(board, path, (x, y, cell, cell))
        draw.rectangle([x, y + cell, x + cell, y + cell + cap], fill=(22, 22, 26))
        draw.text((x + 10, y + cell + 8), label, fill=(90, 220, 255), font=font(24))

    y0 = 96 + rows * (cell + cap + pad) + 20
    draw.text((pad, y0), "参考实拍（Gate 01 归档）对照 rev 渲染同机位", fill=(255, 200, 90), font=font(26))
    y0 += 46
    ref_w = 360
    x = pad
    for path, crop, label in REFERENCE:
        paste_fit(board, path, (x, y0, ref_w, small_h), crop)
        draw.rectangle([x, y0 + small_h, x + ref_w, y0 + small_h + cap], fill=(22, 22, 26))
        draw.text((x + 10, y0 + small_h + 8), label, fill=(255, 200, 90), font=font(22))
        x += ref_w + pad
    for path, label in ((G06 / "geometry-hero.png", "rev hero"), (G06 / "geometry-right-oblique.png", "rev right-oblique")):
        paste_fit(board, path, (x, y0, small_h, small_h))
        draw.rectangle([x, y0 + small_h, x + small_h, y0 + small_h + cap], fill=(22, 22, 26))
        draw.text((x + 10, y0 + small_h + 8), label, fill=(255, 200, 90), font=font(22))
        x += small_h + pad

    y0 += small_h + cap + pad + 20
    draw.text((pad, y0), "Gate 02 待裁决：台面占比 0.70（用户）vs 0.797（照片）。两者只差楔环宽度，直接决定暗缝看起来多深", fill=(255, 140, 90), font=font(26))
    y0 += 46
    var_w = (width - 5 * pad) // 4
    for index, (path, label) in enumerate(VARIANTS):
        x = pad + index * (var_w + pad)
        paste_fit(board, path, (x, y0, var_w, small_h))
        draw.rectangle([x, y0 + small_h, x + var_w, y0 + small_h + cap], fill=(22, 22, 26))
        draw.text((x + 10, y0 + small_h + 8), label, fill=(255, 140, 90), font=font(21))

    out = OUT / f"20-unified-review-{REV.replace('-', '')}.png"
    board.save(out)
    shutil.copy2(out, G06 / "review-board.png")
    for path, _ in PANELS[:6]:
        shutil.copy2(path, OUT / f"21-{path.name}")
    print(out)


if __name__ == "__main__":
    main()
