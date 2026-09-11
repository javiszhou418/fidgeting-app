import { loadManifest, saveStageReviewEvidence } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/04-architecture/rev-002";
const contract = "model-hhax-measurement-modeling-contract-r001";
const manifest = loadManifest(modelId);
const next = saveStageReviewEvidence(modelId, "04-architecture", {
  expectedRevision: manifest.revision,
  assets: [
    { id: "hhax-gate04-interactive-architecture-r002", slot: "interactive-architecture", path: `${base}/exploded-architecture-review.glb`, role: "validation", sourceAssetIds: [contract, "model-hhax-part-tree-r001", "model-hhax-exploded-plan-r001"], sourceClaimIds: ["hhax-claim-shell-topology-r002", "hhax-claim-mechanical-linkage-r002", "hhax-claim-three-art-surfaces-r002"], contentClass: "interactive-exploded-architecture", description: "可旋转爆炸装配，检查两壳、轨道、载体、三表面和封晶层。" },
    { id: "hhax-gate04-architecture-snapshot-r002", slot: "parameter-snapshot", path: `${base}/architecture-review-parameters.json`, role: "validation", sourceAssetIds: [contract, "model-hhax-part-tree-r001", "model-hhax-exploded-plan-r001"], sourceClaimIds: ["hhax-claim-hidden-boundary-r002"], contentClass: "architecture-parameter-snapshot", description: "零件所有权、运动轴、材质区和未知边界快照。" }
  ],
  reviewedArtifactId: "hhax-gate04-interactive-architecture-r002",
  governingContractAssetId: contract,
  parameterSnapshotAssetId: "hhax-gate04-architecture-snapshot-r002",
  completedChecklist: ["part-tree-reviewed", "assembly-motion-reviewed", "material-zones-reviewed"],
  interactionMode: "interactive-3d",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop WebGL",
  recipe: "Gate 04 interactive exploded architecture review"
});
console.log(JSON.stringify({ revision: next.revision, status: next.stages[3].status, review: next.stages[3].reviewEvidenceSpec }, null, 2));
