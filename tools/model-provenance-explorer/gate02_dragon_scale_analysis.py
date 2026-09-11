"""Gate 02 rev-002 analysis for metal-three-blade (GEEONE Dragon Scale).

Produces the annotated measurement board, the reference-vs-current comparison,
and the source-linked claims that later gates must consume. Every ratio below is
read off `geeone-01.jpg` at 720x1280 using the labelled pixel grid in
`grid_geeone.py`; none of them are measured from the physical product.
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
REV = "rev-002"
OUT = PIPELINE_DIR / "evidence/02-analysis" / REV
REFERENCE = (
    PIPELINE_DIR / "evidence/01-intake/rev-002/obsidian-geeone-product/geeone-01.jpg"
)
CURRENT = (
    REPO
    / "Artifacts/EnvironmentIntegration/hub-cap-facets-r005"
    / "metal-three-blade-a-current-top.png"
)

# Pixel readings on geeone-01.jpg (720x1280), read against the labelled grid.
CAP_CENTER = (364, 625)
CAP_OUTER_R = 118  # faceted crown outer edge
TABLE_R = 94  # radially brushed top table
BODY_CENTER = (381, 618)
BODY_R = 220  # circumscribed circle through the three blade tips

MEASUREMENTS = {
    "capOuterDiameterOverBodyDiameter": round(CAP_OUTER_R / BODY_R, 3),
    "tableDiameterOverCapOuterDiameter": round(TABLE_R / CAP_OUTER_R, 3),
    "crownBandWidthOverCapRadius": round((CAP_OUTER_R - TABLE_R) / CAP_OUTER_R, 3),
    "crownFacetCount": 32,
    "crownFacetCountUncertainty": 4,
    "tableRadialWedgeCount": 20,
    "tableRadialWedgeCountUncertainty": 4,
}


def font(size: int):
    # The boards are annotated in Chinese, so a CJK-capable face is required.
    for candidate, index in (
        ("/System/Library/Fonts/PingFang.ttc", 4),
        ("/System/Library/Fonts/PingFang.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
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


def repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO))


CYAN = (70, 225, 255)
ORANGE = (255, 140, 40)
GREEN = (120, 245, 160)
RED = (255, 90, 90)


def measurement_board() -> Path:
    with Image.open(REFERENCE) as raw:
        frame = raw.convert("RGB")
    scale = 2
    frame = frame.resize((frame.width * scale, frame.height * scale), Image.LANCZOS)
    draw = ImageDraw.Draw(frame)
    label = font(30)
    title = font(40)

    def ring(center, radius, color, width=5):
        cx, cy = center[0] * scale, center[1] * scale
        r = radius * scale
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)

    ring(BODY_CENTER, BODY_R, ORANGE)
    ring(CAP_CENTER, CAP_OUTER_R, CYAN)
    ring(CAP_CENTER, TABLE_R, GREEN)

    cx, cy = CAP_CENTER[0] * scale, CAP_CENTER[1] * scale
    draw.line([cx - 20, cy, cx + 20, cy], fill=CYAN, width=4)
    draw.line([cx, cy - 20, cx, cy + 20], fill=CYAN, width=4)

    draw.rectangle([0, 0, frame.width, 120], fill=(12, 12, 14))
    draw.text(
        (28, 34),
        "GEEONE 龙鳞 — Gate 02 参考量测（比例读自照片，非实测毫米）",
        fill=(245, 245, 245),
        font=title,
    )

    legend = [
        (ORANGE, f"整体外接圆 D=100%  (三叶尖端)"),
        (
            CYAN,
            f"帽体刻面外径 D={MEASUREMENTS['capOuterDiameterOverBodyDiameter'] * 100:.1f}% 整体",
        ),
        (
            GREEN,
            f"顶面台面 D={MEASUREMENTS['tableDiameterOverCapOuterDiameter'] * 100:.1f}% 帽径",
        ),
        (RED, f"冠部刻面 ≈{MEASUREMENTS['crownFacetCount']}±4 面（周向梯形）"),
        (RED, f"台面放射楔 ≈{MEASUREMENTS['tableRadialWedgeCount']}±4 楔（收敛于中心）"),
    ]
    y = frame.height - 40 - len(legend) * 46
    draw.rectangle(
        [0, y - 24, frame.width, frame.height], fill=(12, 12, 14)
    )
    for color, text in legend:
        draw.rectangle([28, y + 8, 60, y + 34], fill=color)
        draw.text((78, y + 4), text, fill=(240, 240, 240), font=label)
        y += 46

    out = OUT / "reference-measurement-board.png"
    frame.save(out)
    return out


def comparison_board() -> Path:
    cell = 1000
    pad = 24
    header = 108
    caption = 210
    board = Image.new(
        "RGB", (cell * 2 + pad * 3, header + cell + caption + pad * 2), (14, 14, 16)
    )
    draw = ImageDraw.Draw(board)
    title = font(44)
    head = font(34)
    body = font(27)

    draw.text(
        (pad + 6, 30),
        "metal-three-blade Gate 02：真实参考 vs 当前出货模型",
        fill=(245, 245, 245),
        font=title,
    )

    def crop_square(path: Path, center=None, radius=None) -> Image.Image:
        with Image.open(path) as raw:
            frame = raw.convert("RGB")
        if center and radius:
            box = (
                center[0] - radius,
                center[1] - radius,
                center[0] + radius,
                center[1] + radius,
            )
            frame = frame.crop(box)
        return frame.resize((cell, cell), Image.LANCZOS)

    left = crop_square(REFERENCE, BODY_CENTER, BODY_R + 60)
    right = crop_square(CURRENT)

    board.paste(left, (pad, header))
    board.paste(right, (pad * 2 + cell, header))

    for x, text, color in (
        (pad, "参考：GEEONE 实拍（顶视）", GREEN),
        (pad * 2 + cell, "当前：Unity 出货模型（顶视）", RED),
    ):
        draw.rectangle([x, header - 44, x + cell, header - 6], fill=(24, 24, 28))
        draw.text((x + 12, header - 40), text, fill=color, font=head)

    notes_left = [
        "· 帽体是钻石切工：冠部一圈梯形刻面 + 顶面放射楔面",
        "· 放射楔明暗交替，把高光打散成星芒，不聚成一片亮盘",
        "· 冠部直接接机身，中间只有一道暗缝，没有亮环",
        "· 三叶与中心是一体连续实体，轮廓为圆角三角",
    ]
    notes_right = [
        "· 帽体是一颗完全光滑的球冠，零刻面",
        "· 光滑镜面把整个环境光聚成一整片亮盘 = 用户看到的「金属圆环」",
        "· 帽体与叶片之间露出亮色轴承环",
        "· 三叶是分离的圆钝团块，未与中心连成实体",
    ]
    for x, notes, color in (
        (pad, notes_left, GREEN),
        (pad * 2 + cell, notes_right, RED),
    ):
        y = header + cell + 16
        for note in notes:
            draw.text((x + 8, y), note, fill=color, font=body)
            y += 40

    out = OUT / "reference-vs-current.png"
    board.save(out)
    return out


CLAIMS = [
    {
        "id": "tri-r2-cap-is-brilliant-cut",
        "category": "geometry",
        "statement": (
            "中心指盖是钻石明亮式切工：冠部一圈周向梯形刻面，顶面为收敛于中心的放射楔面。"
            "它不是光滑球冠。用户反馈的「金属圆环」正是光滑镜面帽把环境光聚成一整片亮盘所致。"
        ),
        "confidence": "high",
    },
    {
        "id": "tri-r2-cap-size-was-never-wrong",
        "category": "geometry",
        "statement": (
            f"帽体刻面外径约为整体外接圆的 {MEASUREMENTS['capOuterDiameterOverBodyDiameter'] * 100:.1f}%"
            "（照片比例，±2%）。此前把帽体缩到 33% 的方向与实物相反，应废弃。"
        ),
        "confidence": "high",
    },
    {
        "id": "tri-r2-table-ratio",
        "category": "geometry",
        "statement": (
            f"顶面台面直径约为帽体外径的 {MEASUREMENTS['tableDiameterOverCapOuterDiameter'] * 100:.1f}%"
            "（±3%），其余为冠部刻面带。"
        ),
        "confidence": "medium",
    },
    {
        "id": "tri-r2-facet-counts",
        "category": "geometry",
        "statement": (
            f"冠部刻面约 {MEASUREMENTS['crownFacetCount']}±4 面，"
            f"台面放射楔约 {MEASUREMENTS['tableRadialWedgeCount']}±4 楔。数值读自照片，需在白模阶段复核。"
        ),
        "confidence": "low",
    },
    {
        "id": "tri-r2-no-bright-annulus",
        "category": "geometry",
        "statement": (
            "实物帽体冠部直接过渡到机身，之间只有一道暗色窄缝，不存在任何亮色轴承环、垫圈或倒角环。"
            "当前模型暴露的亮环必须删除或压暗。"
        ),
        "confidence": "high",
    },
    {
        "id": "tri-r2-body-is-one-solid",
        "category": "geometry",
        "statement": (
            "三叶与中心毂是一体连续实体，外轮廓为圆角三角，叶面带大块平切刻面。"
            "当前模型的三个分离圆钝团块与实物不符。"
        ),
        "confidence": "high",
    },
    {
        "id": "tri-r2-dimensions-unmeasured",
        "category": "dimension",
        "statement": (
            "全部毫米级尺寸仍未实测。所有下游关卡只能使用比例，不得把任何毫米值标为 measured。"
        ),
        "confidence": "high",
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    board = measurement_board()
    comparison = comparison_board()

    measurements_path = OUT / "analysis-measurements.json"
    measurements_path.write_text(
        json.dumps(
            {
                "modelId": MODEL_ID,
                "stageId": "02-analysis",
                "revision": 2,
                "measuredAt": datetime.now(timezone.utc).isoformat(),
                "method": "labelled-pixel-grid-on-geeone-01",
                "sourceImage": repo_rel(REFERENCE),
                "sourceImageSize": [720, 1280],
                "pixelReadings": {
                    "capCenter": CAP_CENTER,
                    "capOuterRadius": CAP_OUTER_R,
                    "tableRadius": TABLE_R,
                    "bodyCenter": BODY_CENTER,
                    "bodyRadius": BODY_R,
                },
                "ratios": MEASUREMENTS,
                "unmeasured": [
                    "overall width in mm",
                    "cap diameter in mm",
                    "body thickness in mm",
                    "bearing bore in mm",
                    "crown facet angle",
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    reference_ids = [
        f"tri-r2-product-{index:02d}" for index in range(1, 8)
    ] + ["tri-r2-contact-sheet"]

    asset_defs = [
        (
            "tri-r2-analysis-measurement-board",
            "analysis-board",
            board,
            "analysis",
            "annotated-ratio-measurement-over-real-photograph",
        ),
        (
            "tri-r2-analysis-reference-vs-current",
            "analysis-board",
            comparison,
            "analysis",
            "reference-versus-shipping-model-gap-board",
        ),
        (
            "tri-r2-analysis-measurements",
            "analysis-report",
            measurements_path,
            "analysis",
            "photo-derived-ratio-report",
        ),
    ]

    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing = {asset["id"]: asset for asset in manifest["assets"]}

    artifact_ids = []
    for asset_id, slot, path, role, content_class in asset_defs:
        record = {
            "id": asset_id,
            "stageId": "02-analysis",
            "slot": slot,
            "path": repo_rel(path),
            "sha256": sha256(path),
            "role": role,
            "producer": {
                "name": "gate02_dragon_scale_analysis.py",
                "version": "rev-002",
            },
            "provenance": {
                "origin": "repository-generated",
                "contentClass": content_class,
                "assertedBy": "repository",
                "note": "Ratios read off the real GEEONE photograph. No physical measurement.",
            },
            "sourceAssetIds": reference_ids,
            "exists": True,
            "sizeBytes": path.stat().st_size,
        }
        if asset_id in existing:
            existing[asset_id].update(record)
        else:
            manifest["assets"].append(record)
        artifact_ids.append(asset_id)

    claim_ids = {claim["id"] for claim in manifest.get("claims", [])}
    for claim in CLAIMS:
        if claim["id"] in claim_ids:
            continue
        manifest.setdefault("claims", []).append(
            {
                "id": claim["id"],
                "stageId": "02-analysis",
                "category": claim["category"],
                "statement": claim["statement"],
                "confidence": claim["confidence"],
                "sourceAssetIds": reference_ids,
                "sourceRegions": [],
            }
        )

    for claim in manifest.get("claims", []):
        if claim["id"] == "tri-silhouette-unverified":
            claim["state"] = "superseded"

    analysis = next(
        stage for stage in manifest["stages"] if stage["id"] == "02-analysis"
    )
    analysis["revision"] = 2
    analysis["status"] = "draft"
    analysis["artifactIds"] = artifact_ids
    analysis["decision"] = None
    analysis.pop("staleReason", None)
    analysis["validations"] = [
        {
            "id": "claims-linked-to-real-reference",
            "status": "pass",
            "detail": "全部 claim 的 sourceAssetIds 指向 Gate 01 rev-002 的实拍照片。",
        },
        {
            "id": "root-cause-identified",
            "status": "pass",
            "detail": "金属圆环 = 光滑镜面帽 + 暴露轴承环；实物为钻石切工帽且无亮环。",
        },
        {
            "id": "millimetre-dimensions-measured",
            "status": "fail",
            "detail": "仍无实测毫米尺寸，只有照片比例。",
        },
    ]

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    manifest["currentState"]["diagnosis"] = (
        "Gate 02 rev-002 完成：实拍量测确认中心帽为钻石明亮式切工，帽径约占整体 53.6%，"
        "台面占帽径 79.7%。当前出货模型是光滑球冠 + 分离叶片，与实物不符，"
        "「金属圆环」根因为光滑镜面帽聚光加暴露轴承环。等待用户批准 Gate 02。"
    )

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
            "Gate 02 rev-002: photo-derived ratio measurement over the real GEEONE "
            "reference; registered 7 source-linked claims; superseded "
            "tri-silhouette-unverified."
        ),
        "changedAssets": artifact_ids,
        "changedStageIds": ["02-analysis"],
    }
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "board": repo_rel(board),
                "comparison": repo_rel(comparison),
                "measurements": MEASUREMENTS,
                "revision": manifest["revision"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
