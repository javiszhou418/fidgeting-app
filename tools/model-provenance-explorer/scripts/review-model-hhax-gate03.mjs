import { approveStageFromDelegation, loadManifest, saveStageReviewEvidence } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/03-contract/rev-002";
const contract = "model-hhax-measurement-modeling-contract-r001";
let manifest = loadManifest(modelId);
manifest = saveStageReviewEvidence(modelId, "03-contract", {
  expectedRevision: manifest.revision,
  assets: [
    { id: "hhax-gate03-form-review-recording-r002", slot: "workbench-form-review-recording", path: `${base}/workbench-form-review-recording.mp4`, role: "validation", sourceAssetIds: [contract], sourceClaimIds: ["hhax-claim-product-envelope-r002", "hhax-claim-hidden-boundary-r002"], contentClass: "complete-contract-workbench-recording", description: "完整滚动复核九项数值、来源、不确定度和比例校准。" },
    { id: "hhax-gate03-contract-review-snapshot-r002", slot: "parameter-snapshot", path: `${base}/contract-review-parameters.json`, role: "validation", sourceAssetIds: [contract], sourceClaimIds: ["hhax-claim-product-envelope-r002", "hhax-claim-hidden-boundary-r002"], contentClass: "contract-review-parameter-snapshot", description: "九项完整性、分类、堆叠、包含关系与保留警告快照。" },
    { id: "hhax-gate03-form-review-frame-r002", slot: "workbench-form-review-frame", path: `${base}/workbench-form-review-frame.png`, role: "validation", sourceAssetIds: [contract], sourceClaimIds: ["hhax-claim-hidden-boundary-r002"], contentClass: "contract-review-still", description: "拆解比例字段与校准证据静帧。" }
  ],
  reviewedArtifactId: "hhax-gate03-form-review-recording-r002",
  governingContractAssetId: contract,
  parameterSnapshotAssetId: "hhax-gate03-contract-review-snapshot-r002",
  completedChecklist: ["all-required-dimensions-reviewed", "measurement-sources-reviewed", "measurement-uncertainties-reviewed"],
  interactionMode: "workbench-form-review-recording",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop 1440×1000",
  recipe: "Gate 03 nine-field workbench form review"
});
manifest = approveStageFromDelegation(modelId, "03-contract", {
  expectedRevision: manifest.revision,
  notes: "九项均经完整工作台录屏逐卡复核：3 项同款公开标称、6 项哈希绑定公开拆解数字校准；所有非用户值均不作实测、物理定值或加工尺寸声明。"
});
console.log(JSON.stringify({ revision: manifest.revision, gate03: manifest.stages[2].status, decision: manifest.stages[2].decision }, null, 2));
