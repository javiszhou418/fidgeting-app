import { loadManifest, saveStageReviewEvidence } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const contract = "model-hhax-measurement-modeling-contract-r001";
const coreGlb = "hhax-gate05-white-glb-r003";
const snapshot = "hhax-gate05-white-snapshot-r003";
const manifest = loadManifest(modelId);
const next = saveStageReviewEvidence(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: [{
    id: "hhax-gate05-interactive-review-r004",
    slot: "interactive-white-model-review",
    path: "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-004/white-model-review.glb",
    role: "validation",
    sourceAssetIds: [contract, coreGlb, snapshot],
    sourceClaimIds: [
      "hhax-claim-product-envelope-r002", "hhax-claim-mechanical-linkage-r002",
      "hhax-claim-shell-topology-r002", "hhax-claim-hidden-boundary-r002"
    ],
    contentClass: "interactive-white-model-review",
    description: "工作台可旋转、缩放并播放完整直推与背部自轴旋转的白模。"
  }],
  reviewedArtifactId: "hhax-gate05-interactive-review-r004",
  governingContractAssetId: contract,
  parameterSnapshotAssetId: snapshot,
  completedChecklist: ["silhouette-reviewed", "proportion-reviewed", "thickness-reviewed", "full-motion-range-reviewed"],
  interactionMode: "interactive-3d",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop 1440×1000 WebGL",
  recipe: "Gate 05 real GLB interaction review after two retained preflight failures"
});

console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, review: next.stages[4].reviewEvidenceSpec }, null, 2));
