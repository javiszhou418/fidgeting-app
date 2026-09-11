#!/usr/bin/env python3
"""Create the compact Gate 10 export review summary."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
MODEL = HERE.parent.parent.parent
SOURCE = MODEL / "evidence/09-environment/rev-008/shipping-closed-hero.png"
OUTPUT = HERE / "export-review-summary.png"
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def font(size, index=0):
    return ImageFont.truetype(FONT, size=size, index=index)


def main():
    build = json.loads((HERE / "export-build-report.json").read_text())
    reimport = json.loads((HERE / "reimport-validation.json").read_text())
    image = Image.new("RGB", (1600, 900), (14, 14, 17))
    source = Image.open(SOURCE).convert("RGB")
    source.thumbnail((900, 720), Image.Resampling.LANCZOS)
    image.paste(source, (55, 120))
    draw = ImageDraw.Draw(image)
    draw.text((55, 35), "Gate 10 · Unity 前的真实导出检查", fill=(246, 244, 242), font=font(42))
    draw.text((1010, 135), "请先操作真实 GLB", fill=(255, 196, 70), font=font(32))
    draw.text((1010, 190), "拖动旋转 · 滚轮缩放", fill=(226, 225, 229), font=font(24))
    rows = [
        ("尺寸", "31 × 50 × 12 mm"),
        ("层级", "20 nodes · 8 meshes"),
        ("材质", "7 slots · 4 embedded images"),
        ("法线", "FBX FACE · GLB tangent"),
        ("碰撞", "独立 FBX · 不参与渲染"),
        ("动画", "0 clips · 0 self-motion"),
        ("状态", "尚未导入 Unity"),
    ]
    y = 285
    for label, value in rows:
        draw.rounded_rectangle((995, y - 8, 1540, y + 53), radius=12, fill=(27, 27, 32))
        draw.text((1020, y + 4), label, fill=(154, 151, 161), font=font(21))
        draw.text((1160, y + 4), value, fill=(238, 236, 242), font=font(21))
        y += 72
    draw.text((55, 840), "静态图仅作摘要；Gate 10 以工作台中的真实导出 GLB 为批准依据。", fill=(168, 165, 173), font=font(20))
    image.save(OUTPUT)
    report = {
        "pass": build["pass"] and reimport["pass"],
        "sourceSha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "outputSha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        "outputResolutionPx": list(image.size),
        "claims": {
            "boundsMeters": reimport["results"]["glb"]["boundsMeters"]["size"],
            "nodes": reimport["results"]["glbStructure"]["counts"]["nodes"],
            "meshes": reimport["results"]["glbStructure"]["counts"]["meshes"],
            "materials": reimport["results"]["glbStructure"]["counts"]["materials"],
            "animations": reimport["results"]["glbStructure"]["counts"]["animations"],
        },
    }
    (HERE / "export-summary-validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

