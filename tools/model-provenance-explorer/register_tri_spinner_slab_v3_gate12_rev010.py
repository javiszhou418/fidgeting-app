"""Register the R009 rejection and the corrected Gate 12 R010 draft.

R010 is not approval-ready yet. Its real Unity static captures prove content
centering, scale, orientation and rarity CMF, but the Gate 12 complete runtime
recording and the approved soft-focus implementation are still pending.
"""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
UNITY = REPO / "unity/FidgetingApp"
PIPELINE_DIR = UNITY / "ArtSource/ModelPipeline/premium-display-case"
PIPELINE = PIPELINE_DIR / "pipeline.json"
HISTORY = PIPELINE_DIR / "history.ndjson"
E9 = PIPELINE_DIR / "evidence/12-shipping/v3-rev-009"
REJECTED = E9 / "rejected-20260911T222500+0800"
E10 = PIPELINE_DIR / "evidence/12-shipping/v3-rev-010"
ART10 = REPO / "Artifacts/TriSpinnerSlab/gate12-r010"
PREFAB = UNITY / "Assets/Resources/Gacha/PremiumDisplayCaseGate12R010/PresentationRoot.prefab"
SCENE = UNITY / "Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R010.unity"
BUILDER = UNITY / "Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12R010ReviewBuilder.cs"
TESTS = UNITY / "Assets/_DisplayCase/Tests/Editor/PremiumDisplayCaseGate12R010Tests.cs"
POCKET_PROFILES = UNITY / "Assets/_DisplayCase/Runtime/PremiumDisplayCaseV3PocketProfiles.cs"
RARITY_CMF = UNITY / "Assets/_DisplayCase/Runtime/PremiumDisplayCaseV3RarityCmf.cs"
PRESENTATION = UNITY / "Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingPresentation.cs"
COMPOSER = REPO / "tools/model-provenance-explorer/compose_tri_spinner_slab_gate12_r010.py"
CONTRACT_SHA = "e9a6f14a61e823274c716f3b3c26ee63e0bbc8e5879145e7b98c65aa9ea88294"
VARIANT = "tri-spinner-slab-v3-cmf"
SCRIPT = Path(__file__).name
NOW = datetime.now(timezone.utc).isoformat()
REJECTION_TIME = "2026-09-11T22:25:00+08:00"
REJECTION_SOURCE = "src.user_gate12_r009_content_matrix_rejection_20260911"
REJECTION_WORDING = (
    "首先，第一个陀螺的中心点还是不对，没有居中。然后，后面四张图搞得他妈什么乱七八糟的？"
    "你自己看这个他妈什么东西吗？你自己有没有一套审查的流程啊？大小尺寸比例全都不对。"
    "你搞了什么乱七八糟的？你搞这种垃圾东西，我把你炸了"
)
STAMP = "20260911T145551Z"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def stable_json(value) -> str:
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


def update_stage_digests(manifest: dict) -> None:
    assets = {record["id"]: record for record in manifest["assets"]}
    previous = None
    for stage in manifest["stages"]:
        hashes = [
            assets[asset_id]["sha256"]
            for asset_id in stage.get("artifactIds", [])
            if asset_id in assets and assets[asset_id].get("sha256")
        ]
        claims = [
            stable_json(claim)
            for claim in manifest.get("claims", [])
            if claim["stageId"] == stage["id"]
        ]
        digest = hashlib.sha256(
            "\n".join(sorted(hashes + claims)).encode("utf-8")
        ).hexdigest()
        stage["inputDigest"] = digest if previous is None else previous
        stage["outputDigest"] = digest
        previous = digest


def copy_new(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    with source.open("rb") as source_stream, destination.open("xb") as output:
        for chunk in iter(lambda: source_stream.read(1 << 20), b""):
            output.write(chunk)


def upsert(manifest: dict, record: dict) -> None:
    if any(existing["id"] == record["id"] for existing in manifest["assets"]):
        raise ValueError(f"asset id already exists: {record['id']}")
    manifest["assets"].append(record)


def asset(
    asset_id: str,
    slot: str,
    path: Path,
    role: str,
    content_class: str,
    source_ids: list[str],
    note: str = "",
) -> dict:
    return {
        "id": asset_id,
        "stageId": "12-shipping",
        "slot": slot,
        "path": rel(path),
        "sha256": sha256(path),
        "role": role,
        "producer": {
            "name": SCRIPT,
            "version": "2026-09-11",
            "variant": VARIANT,
        },
        "provenance": {
            "origin": "repository-generated",
            "contentClass": content_class,
            "assertedBy": "repository",
            "note": note,
        },
        "sourceAssetIds": source_ids,
        "exists": True,
        "sizeBytes": path.stat().st_size,
        "variantId": VARIANT,
        "wholeAssembledCaseOnly": True,
        "explodeEligible": False,
        "toyPrizeBundled": False,
        "shippingEligible": False,
        "visualApproved": False,
    }


def main() -> None:
    test_results = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if test_results is None or not test_results.exists():
        raise FileNotFoundError("Pass the successful Unity test-results XML path.")

    report = json.loads((E10 / "gate12-r010-review-report.json").read_text())
    audit = json.loads(
        (ART10 / f"gate12-r010-review-audit-{STAMP}.json").read_text()
    )
    if report["status"] != "pass" or report["failures"]:
        raise ValueError("R010 Unity report is not pass.")
    if audit["status"] != "pass" or not all(audit["checks"].values()):
        raise ValueError("R010 image audit is not pass.")

    snapshots = {
        "builder": (BUILDER, E10 / "PremiumDisplayCaseGate12R010ReviewBuilder.r010.cs"),
        "tests": (TESTS, E10 / "PremiumDisplayCaseGate12R010Tests.r010.cs"),
        "pocket-profiles": (
            POCKET_PROFILES,
            E10 / "PremiumDisplayCaseV3PocketProfiles.r010.cs",
        ),
        "rarity-cmf": (
            RARITY_CMF,
            E10 / "PremiumDisplayCaseV3RarityCmf.r010.cs",
        ),
        "presentation": (
            PRESENTATION,
            E10 / "PremiumDisplayCaseShippingPresentation.r010.cs",
        ),
        "composer": (
            COMPOSER,
            E10 / "compose_tri_spinner_slab_gate12_r010.py",
        ),
        "test-results": (test_results, E10 / "unity-editmode-results.xml"),
    }
    for source, destination in snapshots.values():
        copy_new(source, destination)

    manifest = json.loads(PIPELINE.read_text(encoding="utf-8"))
    stage = next(item for item in manifest["stages"] if item["id"] == "12-shipping")
    if stage["revision"] != 9 or stage["status"] != "draft":
        raise ValueError(
            f"expected Gate 12 rev 9 draft, got rev {stage['revision']} {stage['status']}"
        )

    rejected_records = [
        asset(
            "pdc-v3-g12-r009-rejection-record",
            "rejection-record",
            REJECTED / "user-rejection.md",
            "validation",
            "explicit-user-rejection",
            ["pdc-v3-g11-candidate-prefab"],
            "R009 visual evidence is forbidden for approval.",
        ),
        asset(
            "pdc-v3-g12-r009-center-annotation",
            "rejected-user-annotation",
            REJECTED / "user-annotation-spinner-center.png",
            "shipping-render",
            "rejected-spinner-centering-annotation",
            ["pdc-v3-g12-r009-rejection-record"],
        ),
        asset(
            "pdc-v3-g12-r009-matrix-annotation",
            "rejected-user-annotation",
            REJECTED / "user-annotation-content-matrix-defects.png",
            "shipping-render",
            "rejected-content-matrix-annotation",
            ["pdc-v3-g12-r009-rejection-record"],
        ),
        asset(
            "pdc-v3-g12-r009-rejected-center-preview",
            "rejected-preview",
            REPO
            / "Artifacts/TriSpinnerSlab/gate12-r009"
            / "gate12-r009-pocket-macro-centered-20260911T140200Z.png",
            "shipping-render",
            "rejected-oblique-pocket-preview",
            ["pdc-v3-g11-candidate-prefab"],
        ),
        asset(
            "pdc-v3-g12-r009-rejected-content-matrix",
            "rejected-preview",
            REPO
            / "Artifacts/TriSpinnerSlab/gate12-r009"
            / "gate12-r009-content-matrix-pocket-20260911T140800Z.png",
            "shipping-render",
            "rejected-contaminated-content-matrix",
            ["pdc-v3-g11-candidate-prefab"],
        ),
    ]
    for record in rejected_records:
        upsert(manifest, record)

    rejection_decision = {
        "state": "rejected",
        "action": "reject",
        "decidedBy": "user",
        "decidedAt": REJECTION_TIME,
        "channel": "chat",
        "wording": REJECTION_WORDING,
        "sourceId": REJECTION_SOURCE,
        "recordedAt": NOW,
        "governingContractSha256": CONTRACT_SHA,
        "scope": (
            "R009 off-centre pocket macro and four-product content matrix; "
            "no shipping resource or phone installation was approved"
        ),
        "reviewedArtifacts": [
            {
                "id": record["id"],
                "path": record["path"],
                "sha256": record["sha256"],
            }
            for record in rejected_records
        ],
    }
    stage["artifactIds"] = [record["id"] for record in rejected_records]
    stage["reviewArtifactIds"] = []
    stage["validations"] = [
        {
            "id": "direct-user-visual-review",
            "status": "fail",
            "evidence": (
                "Off-centre spinner; duplicate rotations; source-scene "
                "contamination; invalid scale and clipping."
            ),
        }
    ]
    stage["decision"] = rejection_decision
    stage["status"] = "rejected"
    stage.setdefault("historicalRevisions", []).append(
        {
            "revision": 9,
            "status": "rejected",
            "variantId": VARIANT,
            "artifactIds": list(stage["artifactIds"]),
            "reviewArtifactIds": [],
            "decision": rejection_decision,
            "validations": list(stage["validations"]),
            "shippingSpec": stage.get("shippingSpec"),
            "supersededAt": NOW,
            "reason": (
                "User rejected the R009 centering proof and content matrix. "
                "R010 replaces capture isolation, rotations, fit and review gates."
            ),
        }
    )

    ids: list[str] = []

    def add(
        asset_id: str,
        slot: str,
        path: Path,
        role: str,
        content_class: str,
        source_ids: list[str],
        note: str = "",
    ) -> None:
        upsert(
            manifest,
            asset(
                asset_id,
                slot,
                path,
                role,
                content_class,
                source_ids,
                note,
            ),
        )
        ids.append(asset_id)

    add(
        "pdc-v3-g12-r010-candidate-prefab",
        "shipping-candidate-prefab",
        PREFAB,
        "validation",
        "unity-resources-prefab-candidate",
        ["pdc-v3-g11-candidate-prefab"],
        "Candidate only; PremiumDisplayCaseShippingFactory remains R004.",
    )
    add(
        "pdc-v3-g12-r010-review-scene",
        "shipping-candidate-scene",
        SCENE,
        "validation",
        "unity-review-scene",
        ["pdc-v3-g12-r010-candidate-prefab"],
    )
    for key, (_, destination) in snapshots.items():
        add(
            f"pdc-v3-g12-r010-{key}",
            key,
            destination,
            "validation" if key == "test-results" else "process",
            f"r010-{key}-snapshot",
            ["pdc-v3-g12-r010-candidate-prefab"],
        )
    add(
        "pdc-v3-g12-r010-report",
        "unity-report",
        E10 / "gate12-r010-review-report.json",
        "validation",
        "content-fit-rarity-cmf-report",
        ["pdc-v3-g12-r010-candidate-prefab"],
    )

    for product in report["products"]:
        model_id = product["modelId"]
        for suffix, slot, content_class in [
            ("pocket-front", "content-pocket-front", "straight-on-centering-proof"),
            ("phone-front", "content-phone-front", "whole-case-phone-front"),
            ("phone-quarter", "content-phone-quarter", "whole-case-phone-quarter"),
        ]:
            add(
                f"pdc-v3-g12-r010-{model_id}-{suffix}",
                slot,
                E10 / "content" / f"{model_id}-{suffix}.png",
                "unity-render",
                content_class,
                ["pdc-v3-g12-r010-candidate-prefab"],
                (
                    f"Real shipping renderer snapshot; center "
                    f"{max(abs(product['centerOffsetMm'][0]), abs(product['centerOffsetMm'][1])):.5f} mm; "
                    f"occupancy {product['occupancy']:.3f}."
                ),
            )

    for rarity in report["rarities"]:
        tier = rarity["tier"].lower()
        for suffix, slot, content_class in [
            ("phone-front", "rarity-phone-front", "whole-case-rarity-cmf"),
            ("header-front", "rarity-header-front", "header-rarity-cmf-macro"),
        ]:
            add(
                f"pdc-v3-g12-r010-rarity-{tier}-{suffix}",
                slot,
                E10 / "rarity" / f"{tier}-{suffix}.png",
                "unity-render",
                content_class,
                ["pdc-v3-g12-r010-candidate-prefab"],
                f"{rarity['rarityWord']} using locked muted accent/liner plus proposed near-black header.",
            )

    composites = [
        (
            "content-phone-matrix",
            f"gate12-r010-content-phone-matrix-{STAMP}.png",
            "whole-case-content-matrix",
        ),
        (
            "content-center-proof",
            f"gate12-r010-content-center-proof-{STAMP}.png",
            "annotated-content-centering-proof",
        ),
        (
            "content-quarter-matrix",
            f"gate12-r010-content-quarter-matrix-{STAMP}.png",
            "whole-case-quarter-matrix",
        ),
        (
            "rarity-cmf-matrix",
            f"gate12-r010-rarity-cmf-matrix-{STAMP}.png",
            "whole-case-and-header-rarity-matrix",
        ),
    ]
    preview_ids = []
    for suffix, filename, content_class in composites:
        asset_id = f"pdc-v3-g12-r010-{suffix}"
        add(
            asset_id,
            "review-sheet",
            ART10 / filename,
            "shipping-render",
            content_class,
            ["pdc-v3-g12-r010-report"],
        )
        preview_ids.append(asset_id)
    add(
        "pdc-v3-g12-r010-image-audit",
        "image-audit",
        ART10 / f"gate12-r010-review-audit-{STAMP}.json",
        "validation",
        "deterministic-review-image-audit",
        preview_ids,
    )

    stage["revision"] = 10
    stage["variantId"] = VARIANT
    stage["status"] = "draft"
    stage["artifactIds"] = ids
    stage["reviewArtifactIds"] = []
    stage["previewArtifactIds"] = preview_ids
    stage["decision"] = None
    stage["validations"] = [
        {
            "id": "r009-user-rejection-preserved",
            "status": "pass",
            "evidence": rel(REJECTED / "user-rejection.md"),
        },
        {
            "id": "real-shipping-renderers",
            "status": "pass",
            "evidence": "4/4 snapshots captured; source scenes closed before rendering.",
        },
        {
            "id": "center-error",
            "status": "pass",
            "evidence": "max world-plane error <=0.00002 mm; max screen error <=0.0003 px.",
        },
        {
            "id": "exact-circular-fit",
            "status": "pass",
            "evidence": "mesh-vertex occupancy 0.793-1.000; three-blade 0.902; no radial overflow.",
        },
        {
            "id": "orientation-and-complete-frame",
            "status": "pass",
            "evidence": "4 front + 4 quarter whole-case frames; fan-card A artwork faces camera.",
        },
        {
            "id": "rarity-contract",
            "status": "pass",
            "evidence": "FDB-DSP-059/061 muted zone 2/5/6/7 values; proposed near-black header values recorded.",
        },
        {
            "id": "editmode-tests",
            "status": "pass",
            "evidence": "75/75 focused DisplayCase, parity and Gacha tests.",
        },
        {
            "id": "fan-card-guardrails",
            "status": "pass",
            "evidence": "full validator pass; track clearance 7.590 mm; fan geometry unchanged.",
        },
        {
            "id": "shipping-factory-unchanged",
            "status": "pass",
            "evidence": "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot",
        },
    ]
    stage["shippingReady"] = False
    stage["visualApproved"] = False
    stage["shippingSpec"] = {
        "modelId": "premium-display-case",
        "variantId": VARIANT,
        "revision": 10,
        "recordedAt": NOW,
        "governingContractSha256": CONTRACT_SHA,
        "previousRejectedRevision": 9,
        "previousRevisionDisposition": "user-rejected-history-preserved",
        "rejectionSourceId": REJECTION_SOURCE,
        "wholeAssembledCaseOnly": True,
        "toyPrizeOwnership": "caller-owned",
        "contentFit": {
            "fitDiameterMm": 65.4,
            "referenceDepthMm": 14.5,
            "profiles": [
                {
                    "modelId": row["modelId"],
                    "initialEuler": row["initialEuler"],
                    "anchor": row["anchor"],
                    "uniformScale": row["uniformScale"],
                    "radialExtentMm": row["radialExtentMm"],
                    "depthMm": row["depthMm"],
                    "centerOffsetMm": row["centerOffsetMm"],
                    "occupancy": row["occupancy"],
                }
                for row in report["products"]
            ],
        },
        "rarityCmf": {
            "wideApertureZones": [2, 5, 6, 7],
            "constantZones": [1, 3, 4],
            "lockedAccentAndLiner": "FDB-DSP-059/061",
            "headerProposal": "near-black same-hue base tint per tier; visual approval pending",
            "tiers": report["rarities"],
        },
        "knownLimitations": [
            "The approved Gate 08 visible soft-focus renderer feature is not implemented in Unity yet; R010 uses the existing Bloom/Neutral/Vignette profile only.",
            "The fan-card snapshot shows the shipping scene's zero-input closed stack; no mechanism pose or fan geometry was changed.",
            "Graphite two-lobe keeps physical scale 1.0 and depth 18.68 mm; its back plane is aligned and the extra depth protrudes forward.",
            "Static captures are supplementary. A complete real Unity runtime recording is still required before Gate 12 can become ready_for_review.",
        ],
        "factoryResourcesPath": "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot",
        "candidateResourcesPath": "Gacha/PremiumDisplayCaseGate12R010/PresentationRoot",
        "completeRecording": None,
        "visualApproved": False,
        "shippingReady": False,
    }
    stage["nextStep"] = (
        "Show only the audited R010 static preview sheets for direction feedback. "
        "Then implement the approved visible soft-focus and produce a complete "
        "real Unity runtime recording before requesting Gate 12 approval. "
        "Do not build or install on a phone."
    )

    update_stage_digests(manifest)
    manifest["revision"] += 1
    manifest["updatedAt"] = NOW
    manifest["model"]["status"] = (
        "v3-tri-spinner-slab-gate12-r009-rejected-r010-draft"
    )
    current = manifest["currentState"]
    current["activeStageId"] = "12-shipping"
    current["activeStageStatus"] = "draft"
    current["activeIteration"] = "v3-gate12-r010-static-preview-audited"
    current["shippingAssetUnchanged"] = True
    current["visualApproval"] = (
        "Gate 12 R009 rejected; R010 static content/rarity preview awaits "
        "direction feedback; complete recording and soft-focus still pending"
    )
    current["deviceStatus"] = "not-built-not-installed-not-device-tested"
    current["gate12R010"] = {
        "status": "draft-static-preview-audited",
        "candidatePrefab": rel(PREFAB),
        "evidenceRoot": rel(E10),
        "previewArtifactIds": preview_ids,
        "tests": "75/75",
        "fanCardGuardrails": "pass-7.590-mm",
        "factoryStillPointsAt": "Gacha/PremiumDisplayCaseGate12R004/PresentationRoot",
        "visualApproved": False,
        "phoneInstalled": False,
    }
    for item in current.get("plannedChanges", {}).get("trackB", []):
        item["status"] = "r010-static-candidate-visual-pending"
    current["diagnosis"] += (
        " 22:25 用户退回 Gate 12 R009：三叶斜视宏观图视觉偏心，四产品矩阵因重复 ±90°、"
        "来源场景未关闭和单一厚度缩放出现小点、侧躺与穿画面；R009 已保留为 rejected history。"
        "R010 关闭来源场景后再抓 renderer，使用 V3 专属朝向、机械轴心/可见中心和真实 mesh 顶点"
        "圆井 fit；四款中心与完整帧门禁通过，75/75 测试与 Fan Card 7.590 mm 门禁通过。"
        "R010 静态预览待反馈；soft-focus 与完整 runtime recording 未完成，未推送手机。"
    )

    events = [
        {
            "id": str(uuid.uuid4()),
            "modelId": "premium-display-case",
            "manifestRevision": manifest["revision"],
            "timestamp": NOW,
            "variantId": VARIANT,
            "type": "gate-rejected",
            "stageId": "12-shipping",
            "revision": 9,
            "sourceId": REJECTION_SOURCE,
            "notes": REJECTION_WORDING,
            "decision": rejection_decision,
        },
        {
            "id": str(uuid.uuid4()),
            "modelId": "premium-display-case",
            "manifestRevision": manifest["revision"],
            "timestamp": NOW,
            "variantId": VARIANT,
            "type": "stage-revised",
            "stageId": "12-shipping",
            "revision": 10,
            "notes": (
                "R010 replaces R009 content capture isolation, orientation, "
                "centering, circular fit and rarity CMF. Static preview only."
            ),
        },
        {
            "id": str(uuid.uuid4()),
            "modelId": "premium-display-case",
            "manifestRevision": manifest["revision"],
            "timestamp": NOW,
            "variantId": VARIANT,
            "type": "stage-draft-evidence-updated",
            "stageId": "12-shipping",
            "revision": 10,
            "notes": (
                "Real Unity R010 static captures pass numeric and image gates; "
                "complete runtime recording and soft-focus remain pending."
            ),
        },
    ]

    PIPELINE.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with HISTORY.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "manifestRevision": manifest["revision"],
                "stageRevision": stage["revision"],
                "status": stage["status"],
                "artifactCount": len(ids),
                "previewArtifactIds": preview_ids,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
