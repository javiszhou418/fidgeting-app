"""Append durable fan-card validation evidence to Gate 12 R010."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
PIPELINE_DIR = (
    REPO
    / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
)
EVIDENCE = PIPELINE_DIR / "evidence/12-shipping/v3-rev-010"
NOW = datetime.now(timezone.utc).isoformat()
FILES = [
    (
        "pdc-v3-g12-r010-fan-guardrails",
        "fan-card-guardrails",
        EVIDENCE / "fan-card-guardrails-full.txt",
        "fan-card-full-guardrails-pass",
    ),
    (
        "pdc-v3-g12-r010-fan-geometry",
        "fan-card-geometry-validation",
        EVIDENCE / "fan-card-geometry-validation.log",
        "fan-card-unity-geometry-pass",
    ),
    (
        "pdc-v3-g12-r010-fan-tests",
        "fan-card-test-results",
        EVIDENCE / "fan-card-acceptance-results.xml",
        "fan-card-editmode-23-of-23",
    ),
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value):
    if isinstance(value, list):
        return "[" + ",".join(stable_json(item) for item in value) + "]"
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(
                f"{json.dumps(key, ensure_ascii=False)}:{stable_json(value[key])}"
                for key in sorted(value)
            )
            + "}"
        )
    return json.dumps(value, ensure_ascii=False)


def main():
    path = PIPELINE_DIR / "pipeline.json"
    manifest = json.loads(path.read_text())
    stage = next(item for item in manifest["stages"] if item["id"] == "12-shipping")
    if stage["revision"] != 10 or stage["status"] != "draft":
        raise ValueError("Gate 12 R010 draft required")
    existing = {item["id"] for item in manifest["assets"]}
    for asset_id, slot, file, content_class in FILES:
        if asset_id in existing:
            raise ValueError(f"asset already registered: {asset_id}")
        manifest["assets"].append(
            {
                "id": asset_id,
                "stageId": "12-shipping",
                "slot": slot,
                "path": str(file.relative_to(REPO)),
                "sha256": sha256(file),
                "role": "validation",
                "producer": {
                    "name": Path(__file__).name,
                    "version": "2026-09-11",
                    "variant": "tri-spinner-slab-v3-cmf",
                },
                "provenance": {
                    "origin": "repository-generated",
                    "contentClass": content_class,
                    "assertedBy": "repository",
                    "note": "Fan-card geometry was not changed by the slab preview.",
                },
                "sourceAssetIds": [
                    "pdc-v3-g12-r010-magnetic-fan-card-pocket-front"
                ],
                "exists": True,
                "sizeBytes": file.stat().st_size,
                "variantId": "tri-spinner-slab-v3-cmf",
                "wholeAssembledCaseOnly": True,
                "explodeEligible": False,
                "toyPrizeBundled": False,
                "shippingEligible": False,
                "visualApproved": False,
            }
        )
        stage["artifactIds"].append(asset_id)

    assets = {item["id"]: item for item in manifest["assets"]}
    previous = None
    for record in manifest["stages"]:
        hashes = [
            assets[asset_id]["sha256"]
            for asset_id in record.get("artifactIds", [])
            if asset_id in assets and assets[asset_id].get("sha256")
        ]
        claims = [
            stable_json(claim)
            for claim in manifest.get("claims", [])
            if claim["stageId"] == record["id"]
        ]
        digest = hashlib.sha256(
            "\n".join(sorted(hashes + claims)).encode()
        ).hexdigest()
        record["inputDigest"] = digest if previous is None else previous
        record["outputDigest"] = digest
        previous = digest

    manifest["revision"] += 1
    manifest["updatedAt"] = NOW
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    event = {
        "id": str(uuid.uuid4()),
        "modelId": "premium-display-case",
        "manifestRevision": manifest["revision"],
        "timestamp": NOW,
        "variantId": "tri-spinner-slab-v3-cmf",
        "type": "stage-draft-validation-updated",
        "stageId": "12-shipping",
        "revision": 10,
        "notes": (
            "Fan-card full source/asset guardrails pass at 7.590 mm; "
            "CardGeometryValidator ALL PASS; FanCardAcceptanceTests 23/23."
        ),
    }
    with (PIPELINE_DIR / "history.ndjson").open("a") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(json.dumps({"manifestRevision": manifest["revision"], "added": 3}))


if __name__ == "__main__":
    main()
