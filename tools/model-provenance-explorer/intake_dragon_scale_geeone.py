"""Archive the real GEEONE Dragon Scale references into Gate 01 rev-002.

The existing Gate 01 record cites assistant-generated orthographic targets. The
user's Obsidian vault holds the actual saved product clipping, so this run
files the photographs as external reference and demotes the generated sheets to
`ai-target` so later gates cannot treat them as measurements.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
VAULT = Path("/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手")
MODEL_ID = "metal-three-blade"
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline" / MODEL_ID
REV = "rev-002"
INTAKE = PIPELINE_DIR / "evidence/01-intake" / REV

# Real product screenshots saved by the user from the 指玩屋 clipping.
PRODUCT_SHOTS = [
    "aaf44360187ff917e1f13259930dc262_MD5.jpg",
    "793f36060c9f6116b2d1617e8da37682_MD5.jpg",
    "920db3ce3e1f3fdae7d0dc4f13c29f76_MD5.jpg",
    "c1e10711a9d8ea4451ceac6ed92203ee_MD5.jpg",
    "f886cf1c5947e3e26210a932412ce29e_MD5.jpg",
    "a366848a0415f56902be9c1b0bba1633_MD5.jpg",
    "f3dcb63080bed245a9cf8df76e92599f_MD5.jpg",
]

# Assistant-generated boards. Evidence of prior intent, never a measurement.
DERIVED_SHEETS = [
    "generated/龙鳞EDC-分镜/龙鳞EDC_02_三视图与爆炸图_标注版.png",
    "generated/龙鳞EDC-分镜/龙鳞EDC_03_材质灯光参数卡.png",
    "generated/龙鳞EDC-分镜/龙鳞EDC_01_动作分镜_底图.png",
]

NOTES = [
    ("2026-08-01/可以玩一整天的小玩意？！.md", "source-clipping.md"),
    ("2026-08-01/龙鳞（NOVO EDC）分镜与3D生成规范.md", "assistant-spec.md"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def contact_sheet(images: list[Path], out: Path, columns: int = 4) -> None:
    cell = 420
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new(
        "RGB", (columns * cell, rows * cell), (16, 16, 18)
    )
    for index, source in enumerate(images):
        with Image.open(source) as raw:
            frame = raw.convert("RGB")
            frame.thumbnail((cell - 12, cell - 12))
            x = (index % columns) * cell + (cell - frame.width) // 2
            y = (index // columns) * cell + (cell - frame.height) // 2
            sheet.paste(frame, (x, y))
    sheet.save(out, quality=92)


def main() -> None:
    product_dir = INTAKE / "obsidian-geeone-product"
    derived_dir = INTAKE / "assistant-derived-not-reference"
    for folder in (product_dir, derived_dir):
        folder.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    copied_products: list[Path] = []

    for index, name in enumerate(PRODUCT_SHOTS, start=1):
        source = VAULT / "images" / name
        if not source.exists():
            raise FileNotFoundError(source)
        target = product_dir / f"geeone-{index:02d}{source.suffix}"
        shutil.copy2(source, target)
        copied_products.append(target)
        records.append(
            {
                "id": f"tri-r2-product-{index:02d}",
                "slot": "original-reference",
                "path": repo_rel(target),
                "role": "external-reference",
                "vaultSource": str(source),
                "contentClass": "real-product-photograph",
            }
        )

    for index, rel in enumerate(DERIVED_SHEETS, start=1):
        source = VAULT / "images" / rel
        if not source.exists():
            print(f"skip missing derived sheet: {source}")
            continue
        target = derived_dir / f"assistant-board-{index:02d}{source.suffix}"
        shutil.copy2(source, target)
        records.append(
            {
                "id": f"tri-r2-derived-{index:02d}",
                "slot": "ai-target",
                "path": repo_rel(target),
                "role": "ai-target",
                "vaultSource": str(source),
                "contentClass": "assistant-generated-board",
            }
        )

    for rel, out_name in NOTES:
        source = VAULT / rel
        if not source.exists():
            print(f"skip missing note: {source}")
            continue
        target = INTAKE / out_name
        shutil.copy2(source, target)
        records.append(
            {
                "id": f"tri-r2-note-{out_name.split('.')[0]}",
                "slot": "source-note",
                "path": repo_rel(target),
                "role": (
                    "ai-target"
                    if "spec" in out_name
                    else "external-reference"
                ),
                "vaultSource": str(source),
                "contentClass": (
                    "assistant-generated-spec"
                    if "spec" in out_name
                    else "user-saved-clipping"
                ),
            }
        )

    sheet_path = INTAKE / "geeone-contact-sheet.jpg"
    contact_sheet(copied_products, sheet_path)
    records.append(
        {
            "id": "tri-r2-contact-sheet",
            "slot": "contact-sheet",
            "path": repo_rel(sheet_path),
            "role": "derived-index",
            "vaultSource": "",
            "contentClass": "generated-index-of-real-photographs",
        }
    )

    for record in records:
        absolute = REPO / record["path"]
        record["sha256"] = sha256(absolute)
        record["sizeBytes"] = absolute.stat().st_size

    metadata = {
        "modelId": MODEL_ID,
        "stageId": "01-intake",
        "revision": 2,
        "capturedAt": datetime.now(timezone.utc).isoformat(),
        "originVault": str(VAULT),
        "productIdentified": "GEEONE 龙鳞 / NOVO EDC three-blade faceted spinner",
        "classification": {
            "external-reference": "Real product photographs the user saved. Valid basis for Gate 02 claims.",
            "ai-target": "Assistant-generated boards and specs. Intent only; never a measurement source.",
            "derived-index": "Generated contact sheet over the real photographs.",
        },
        "knownGaps": [
            "No caliper measurement, no orthographic product shot, no teardown.",
            "Overall width, cap diameter, and thickness remain unknown until measured or user-authorized.",
            "Prior 0.52 cap ratio traces to the assistant spec board, not to a measurement.",
        ],
        "assets": records,
    }
    (INTAKE / "source-metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    existing = {asset["id"] for asset in manifest["assets"]}
    for record in records:
        if record["id"] in existing:
            continue
        manifest["assets"].append(
            {
                "id": record["id"],
                "stageId": "01-intake",
                "slot": record["slot"],
                "path": record["path"],
                "sha256": record["sha256"],
                "role": record["role"],
                "producer": {
                    "name": "obsidian-vault-intake",
                    "version": "rev-002",
                },
                "provenance": {
                    "origin": "user-obsidian-vault",
                    "contentClass": record["contentClass"],
                    "assertedBy": "gate01-rev002-intake",
                    "note": record["vaultSource"],
                },
                "sourceAssetIds": [],
                "exists": True,
                "sizeBytes": record["sizeBytes"],
            }
        )

    # Demote the legacy generated orthographic/exploded targets.
    for asset in manifest["assets"]:
        if asset["id"] in {"tri-input-orthographic", "tri-input-exploded"}:
            asset["role"] = "ai-target"
            asset["slot"] = "ai-target"
            asset["provenance"]["note"] = (
                "Superseded by Gate 01 rev-002. Assistant-generated target, "
                "not a product reference."
            )

    stages = {stage["id"]: stage for stage in manifest["stages"]}
    intake = stages["01-intake"]
    intake["revision"] = 2
    intake["status"] = "draft"
    intake["artifactIds"] = [record["id"] for record in records]
    intake["decision"] = None
    intake["validations"] = [
        {
            "id": "real-product-reference-present",
            "status": "pass",
            "detail": f"{len(copied_products)} GEEONE product photographs archived.",
        },
        {
            "id": "generated-targets-demoted",
            "status": "pass",
            "detail": "Assistant boards carry role ai-target and cannot back a claim.",
        },
        {
            "id": "physical-dimensions-measured",
            "status": "fail",
            "detail": "No measured width, cap diameter, or thickness yet.",
        },
    ]

    for stage_id, stage in stages.items():
        if stage_id == "01-intake":
            continue
        if stage["status"] in {"approved", "draft"}:
            stage["status"] = "stale"
        stage["staleReason"] = "Gate 01 rev-002 replaced the reference basis."

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    manifest["currentState"] = {
        "rebuildRequested": True,
        "shippingAssetUnchanged": True,
        "visualApproval": "pending",
        "deviceStatus": "not-approved",
        "diagnosis": (
            "用户要求从参考重做完整 12 关。Gate 01 rev-002 归档了 Obsidian 中 "
            "GEEONE 龙鳞实拍作为真实外部参考，并将助手生成的三视图/参数卡降级为 "
            "ai-target。物理尺寸仍未实测。"
        ),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    event = {
        "id": str(uuid.uuid4()),
        "type": "stage-revised",
        "modelId": MODEL_ID,
        "stageId": "01-intake",
        "manifestRevision": manifest["revision"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Gate 01 rev-002: archived GEEONE product photographs from the user's "
            "Obsidian vault as external-reference; demoted assistant-generated "
            "orthographic/exploded boards to ai-target; marked downstream stale."
        ),
        "changedAssets": [record["id"] for record in records],
        "changedStageIds": list(stages.keys()),
    }
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(json.dumps({"intake": repo_rel(INTAKE), "assets": len(records)}, indent=2))


if __name__ == "__main__":
    main()
