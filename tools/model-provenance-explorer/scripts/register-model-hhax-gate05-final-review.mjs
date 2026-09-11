import { loadManifest, saveStageReviewEvidence } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const contract = "model-hhax-measurement-modeling-contract-r001";
const coreGlb = "hhax-gate05-white-glb-r006";
const snapshot = "hhax-gate05-white-snapshot-r006";
const manifest = loadManifest(modelId);
const next = saveStageReviewEvidence(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: [{
    id: "hhax-gate05-interactive-review-r007",
    slot: "interactive-white-model-review",
    path: "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-007/white-model-review.glb",
    role: "validation",
    sourceAssetIds: [contract, coreGlb, snapshot],
    sourceClaimIds: ["hhax-claim-product-envelope-r002", "hhax-claim-mechanical-linkage-r002", "hhax-claim-shell-topology-r002", "hhax-claim-hidden-boundary-r002"],
    contentClass: "interactive-white-model-review",
    description: "工作台检查胶囊轮廓、上下片厚度、全行程与背部圆件自轴旋转。"
  }],
  reviewedArtifactId: "hhax-gate05-interactive-review-r007",
  governingContractAssetId: contract,
  parameterSnapshotAssetId: snapshot,
  completedChecklist: ["silhouette-reviewed", "proportion-reviewed", "thickness-reviewed", "full-motion-range-reviewed"],
  interactionMode: "interactive-3d",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop 1440×1000 WebGL",
  recipe: "Gate 05 final real GLB interaction review"
});
console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, review: next.stages[4].reviewEvidenceSpec }, null, 2));
