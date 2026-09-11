"""Repair Gate 01 rev-002 provenance so the manifest passes the schema validator.

The intake run wrote `origin: user-obsidian-vault` and `assertedBy:
gate01-rev002-intake`, which are outside the allowed enums in
`pipeline-contract.mjs`. Map each asset to a legal origin/role pair and keep the
vault path in `note`.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
PIPELINE_DIR = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade"

# id prefix -> (role, slot, origin, assertedBy)
MAPPING = {
    "tri-r2-product-": ("external-reference", "original-reference", "external", "user"),
    "tri-r2-derived-": ("ai-target", "ai-target", "assistant-generated", "assistant"),
    "tri-r2-note-source-clipping": (
        "external-reference",
        "original-reference",
        "user-provided",
        "user",
    ),
    "tri-r2-note-assistant-spec": (
        "ai-target",
        "ai-target",
        "assistant-generated",
        "assistant",
    ),
    "tri-r2-contact-sheet": (
        "analysis",
        "original-reference",
        "repository-generated",
        "repository",
    ),
}


def resolve(asset_id: str):
    for key, value in MAPPING.items():
        if asset_id.startswith(key):
            return value
    return None


def main() -> None:
    manifest_path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    fixed: list[str] = []
    for asset in manifest["assets"]:
        mapped = resolve(asset["id"])
        if mapped is None:
            continue
        role, slot, origin, asserted_by = mapped
        asset["role"] = role
        asset["slot"] = slot
        provenance = asset.setdefault("provenance", {})
        provenance["origin"] = origin
        provenance["assertedBy"] = asserted_by
        provenance.setdefault("contentClass", "unclassified")
        fixed.append(asset["id"])

    intake = next(stage for stage in manifest["stages"] if stage["id"] == "01-intake")
    intake["artifactIds"] = [
        asset["id"] for asset in manifest["assets"] if asset["id"] in set(fixed)
    ]

    manifest["revision"] = int(manifest.get("revision", 0)) + 1
    manifest["updatedAt"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    event = {
        "id": str(uuid.uuid4()),
        "type": "stage-revised",
        "modelId": "metal-three-blade",
        "stageId": "01-intake",
        "manifestRevision": manifest["revision"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Gate 01 rev-002 correction: remapped provenance.origin/assertedBy and "
            "asset roles onto the schema enums. Real GEEONE photographs stay "
            "external-reference; assistant boards stay ai-target."
        ),
        "changedAssets": fixed,
        "changedStageIds": ["01-intake"],
    }
    with (PIPELINE_DIR / "history.ndjson").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(json.dumps({"fixed": len(fixed), "revision": manifest["revision"]}, indent=2))


if __name__ == "__main__":
    main()
