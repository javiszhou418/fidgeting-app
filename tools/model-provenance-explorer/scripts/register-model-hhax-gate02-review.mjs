import { loadManifest, saveStageReviewEvidence } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/02-analysis/rev-003";
const governing = "hhax-analysis-discovery-log-r002";
const manifest = loadManifest(modelId);
const next = saveStageReviewEvidence(modelId, "02-analysis", {
  expectedRevision: manifest.revision,
  assets: [
    {
      id: "hhax-gate02-interactive-cad-review-r003",
      slot: "interactive-cad-review",
      path: `${base}/interactive-cad-review.glb`,
      role: "validation",
      sourceAssetIds: [governing, "hhax-analysis-interactive-cad-r002"],
      contentClass: "interactive-structural-cad-review",
      description: "可旋转结构 CAD，自审两个主壳、直轨、圆轨、中央调节区和未知包络。"
    },
    {
      id: "hhax-gate02-cad-review-snapshot-r003",
      slot: "parameter-snapshot",
      path: `${base}/cad-review-parameters.json`,
      role: "validation",
      sourceAssetIds: [governing, "hhax-analysis-parameter-snapshot-r002"],
      contentClass: "cad-review-parameter-snapshot",
      description: "交互 CAD 的尺寸、动作与未知边界快照。"
    }
  ],
  reviewedArtifactId: "hhax-gate02-interactive-cad-review-r003",
  governingContractAssetId: governing,
  parameterSnapshotAssetId: "hhax-gate02-cad-review-snapshot-r003",
  completedChecklist: ["all-sources-inspected", "mechanism-motion-tested", "uncertainties-reviewed"],
  interactionMode: "interactive-cad",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop WebGL",
  recipe: "Gate 02 interactive structural CAD review"
});
console.log(JSON.stringify({ revision: next.revision, status: next.stages[1].status, review: next.stages[1].reviewEvidenceSpec }, null, 2));
