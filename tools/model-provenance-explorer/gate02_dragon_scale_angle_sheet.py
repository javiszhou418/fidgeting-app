"""Gate 02 rev-002 supporting evidence: the multi-angle GEEONE reference sheet.

The top view alone cannot show the crown profile or how the facets behave under
grazing light. This board collects the remaining archived photographs with the
reading each one supports.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
MODEL_ID = "metal-three-blade"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
PRODUCT = PIPELINE_DIR / "evidence/01-intake/rev-002/obsidian-geeone-product"
OUT = PIPELINE_DIR / "evidence/02-analysis/rev-002"

# name, crop box on the 720x1280 original, view label, reading
PANELS = [
    (
        "geeone-01",
        (150, 400, 640, 890),
        "顶视（近正交）",
        [
            "帽体 = 台面放射楔 + 冠部鳞片刻面",
            "冠部与机身之间只有一道暗缝，无亮环",
        ],
    ),
    (
        "geeone-02",
        (170, 260, 660, 750),
        "顶视偏斜 · 强光",
        [
            "即使强光下，放射楔仍明暗交替",
            "高光被打散成星芒，不聚成一片亮盘",
        ],
    ),
    (
        "geeone-07",
        (140, 380, 630, 870),
        "约 30° 斜视",
        [
            "冠部是不规则多边形鳞片（「龙鳞」由来）",
            "非规则梯形，鳞片大小不一",
        ],
    ),
    (
        "geeone-03",
        (170, 330, 560, 720),
        "掠射 · 暗环境",
        [
            "暗环境下帽体整体压暗，只剩刻面棱线亮",
            "光滑镜面在同样环境会保持大片亮",
        ],
    ),
    (
        "geeone-04",
        (30, 350, 520, 840),
        "侧低角",
        [
            "冠部是浅锥，高出叶面不多",
            "叶片侧面同样带大块平切刻面",
        ],
    ),
    (
        "geeone-06",
        (120, 400, 610, 890),
        "旋转中（动态模糊）",
        [
            "转动时叶片糊成盘，帽体仍是视觉焦点",
            "帽体刻面在转动中形成闪烁，而非恒亮圆环",
        ],
    ),
]


def font(size: int):
    for candidate, index in (
        ("/System/Library/Fonts/PingFang.ttc", 4),
        ("/System/Library/Fonts/PingFang.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size, index=index)
            except OSError:
                continue
    return ImageFont.load_default()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build() -> Path:
    cell = 520
    caption = 128
    pad = 18
    header = 96
    columns = 3
    rows = (len(PANELS) + columns - 1) // columns

    width = columns * cell + (columns + 1) * pad
    height = header + rows * (cell + caption) + (rows + 1) * pad
    board = Image.new("RGB", (width, height), (13, 13, 15))
    draw = ImageDraw.Draw(board)
    title = font(40)
    label = font(28)
    note = font(23)

    draw.text(
        (pad + 6, 26),
        "GEEONE 龙鳞 — Gate 02 多角度实拍证据（metal-three-blade）",
        fill=(245, 245, 245),
        font=title,
    )

    for index, (name, box, view, notes) in enumerate(PANELS):
        column = index % columns
        row = index // columns
        x = pad + column * (cell + pad)
        y = header + pad + row * (cell + caption + pad)

        with Image.open(PRODUCT / f"{name}.jpg") as raw:
            frame = raw.convert("RGB").crop(box).resize((cell, cell), Image.LANCZOS)
        board.paste(frame, (x, y))
        draw.rectangle([x, y, x + cell, y + cell], outline=(60, 60, 68), width=2)

        draw.rectangle([x, y + cell, x + cell, y + cell + caption], fill=(22, 22, 26))
        draw.text((x + 12, y + cell + 8), f"{view}  ·  {name}", fill=(90, 220, 255), font=label)
        ny = y + cell + 46
        for line in notes:
            draw.text((x + 12, ny), f"· {line}", fill=(228, 228, 232), font=note)
            ny += 32

    out = OUT / "reference-angle-sheet.png"
    OUT.mkdir(parents=True, exist_ok=True)
    board.save(out)
    return out


def register(sheet: Path) -> int:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    asset_id = "tri-r2-analysis-angle-sheet"
    reference_ids = [f"tri-r2-product-{index:02d}" for index in range(1, 8)]

    record = {
        "id": asset_id,
        "stageId": "02-analysis",
        "slot": "analysis-board",
        "path": str(sheet.relative_to(REPO)),
        "sha256": sha256(sheet),
        "role": "analysis",
        "producer": {
            "name": "gate02_dragon_scale_angle_sheet.py",
            "version": "rev-002",
        },
        "provenance": {
            "origin": "repository-generated",
            "contentClass": "multi-angle-crops-of-real-photographs-with-readings",
            "assertedBy": "repository",
            "note": "Crops only. No retouching, no generated imagery.",
        },
        "sourceAssetIds": reference_ids,
        "exists": True,
        "sizeBytes": sheet.stat().st_size,
    }

    existing = next((a for a in manifest["assets"] if a["id"] == asset_id), None)
    if existing:
        existing.update(record)
    else:
        manifest["assets"].append(record)

    analysis = next(s for s in manifest["stages"] if s["id"] == "02-analysis")
    if asset_id not in analysis["artifactIds"]:
        analysis["artifactIds"].append(asset_id)

    # Refine the facet claim: the crown is irregular scales, not uniform trapezoids.
    for claim in manifest.get("claims", []):
        if claim["id"] == "tri-r2-facet-counts":
            claim["statement"] = (
                "冠部为不规则多边形鳞片刻面（「龙鳞」命名由来），沿周向约 30±6 片、"
                "大小不一，不是规则梯形阵列；台面为规则放射楔约 20±4 楔。"
                "数值读自照片，需在白模阶段复核。"
            )
        if claim["id"] == "tri-r2-cap-is-brilliant-cut":
            claim["statement"] = (
                "中心指盖为刻面结构：顶面是收敛于中心的规则放射楔面，冠部是一圈不规则多边形鳞片刻面。"
                "它不是光滑球冠。用户反馈的「金属圆环」正是光滑镜面帽把环境光聚成一整片亮盘所致；"
                "掠射与暗环境实拍显示刻面帽会整体压暗、只留棱线高光。"
            )

    manifest["claims"].append(
        {
            "id": "tri-r2-body-facets-too",
            "stageId": "02-analysis",
            "category": "geometry",
            "statement": (
                "刻面不止在帽体：三叶侧面与尖端同样带大块平切刻面，整机是一个连续的刻面实体。"
                "当前模型的光滑圆钝叶片与实物不符。"
            ),
            "confidence": "high",
            "sourceAssetIds": reference_ids,
            "sourceRegions": [],
        }
    )

    analysis["validations"].append(
        {
            "id": "multi-angle-evidence-present",
            "status": "pass",
            "detail": "顶视/斜视/掠射/侧低角/旋转共 6 个角度的实拍裁切已归档。",
        }
    )

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    event = {
        "id": str(uuid.uuid4()),
        "type": "stage-revised",
        "modelId": MODEL_ID,
        "stageId": "02-analysis",
        "manifestRevision": manifest["revision"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Gate 02 rev-002: added the six-angle reference sheet; refined the crown "
            "facet claim to irregular polygonal scales; added tri-r2-body-facets-too."
        ),
        "changedAssets": [asset_id],
        "changedStageIds": ["02-analysis"],
    }
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    return manifest["revision"]


def main() -> None:
    sheet = build()
    revision = register(sheet)
    print(json.dumps({"sheet": str(sheet), "revision": revision}, indent=2))


if __name__ == "__main__":
    main()
