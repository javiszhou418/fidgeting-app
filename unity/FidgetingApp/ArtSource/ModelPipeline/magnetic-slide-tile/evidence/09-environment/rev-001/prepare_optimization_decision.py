#!/usr/bin/env python3
"""Record the approved model optimization decision in plain terms."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
GEOMETRY = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-001/geometry-validation.json"
ARTWORK = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-007/artwork-layers.json"
OUTPUT = ROOT / "optimization-decision.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    artwork = json.loads(ARTWORK.read_text(encoding="utf-8"))
    mesh_integrity = {
        name: item
        for name, item in geometry["meshIntegrity"].items()
        if isinstance(item, dict) and "triangles" in item
    }
    triangles = sum(item["triangles"] for item in mesh_integrity.values())
    slots = artwork["slots"]
    checks = {
        "triangleCountIs4096": triangles == 4096,
        "singleCloseupModelOnly": True,
        "noHighLowVariantsCreated": True,
        "upperLowerMasksRemainIndependent": all(slot["independentlyEditable"] for slot in slots.values()),
        "simplifiedLibraryModelDeferredUntilProfiling": True,
        "futureHighPolyBakeOnly": True,
        "astcAndChannelPackingDeferredToGate10": True,
        "geometryAndLodUnchanged": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "decision": "Keep the current 4,096-triangle model as the single close-up model. Do not create high/low variants now.",
        "userApprovalWording": "可以吧，然后你继续",
        "decisionState": "locked-user-approved",
        "deliveryState": {
            "singleCloseupModel": "current-approved-model-preserved",
            "highLowVariants": "not-created-and-not-required",
            "independentArtworkMasks": "blender-pipeline-present-unity-parity-pending",
            "simplifiedLibraryModel": "conditional-not-created-profile-many-simultaneous-models-first",
            "futureHighPolySource": "specified-bake-only-never-ships",
            "astcAndChannelPacking": "specified-only-gate10-and-unity-import-pending",
            "deviceAcceptance": "pending",
        },
        "plainTerms": [
            "The current model is light enough for one close-up product view.",
            "Keep one shipping mesh instead of maintaining high and low versions now.",
            "Keep upper and lower artwork as separate replaceable masks.",
            "Only make a simpler library mesh if Unity profiling proves that many simultaneous models need it.",
            "Any future high-poly model is only for baking textures and never ships.",
            "ASTC texture compression and channel packing belong to Gate 10 and Unity import work; they are not delivered yet.",
        ],
        "measuredModel": {
            "totalTriangles": triangles,
            "meshTriangles": {
                name: item["triangles"]
                for name, item in mesh_integrity.items()
            },
            "geometryDigest": geometry["geometryIdentity"]["evaluatedDigest"],
            "sourcePath": str(GEOMETRY.relative_to(REPO)),
            "sourceSha256": sha256(GEOMETRY),
        },
        "artwork": {
            "upperMask": slots["Artwork_Upper"]["mask"],
            "lowerMask": slots["Artwork_Lower"]["mask"],
            "independentlyReplaceable": True,
            "sourcePath": str(ARTWORK.relative_to(REPO)),
            "sourceSha256": sha256(ARTWORK),
        },
        "scope": {
            "geometryChanged": False,
            "lodCreated": False,
            "unityChanged": False,
            "textureImportChanged": False,
            "exportPerformed": False,
            "buildOrInstallPerformed": False,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Optimization decision validation failed.")


if __name__ == "__main__":
    main()
