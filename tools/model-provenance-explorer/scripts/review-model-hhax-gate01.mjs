import {
  approveStageFromDelegation,
  loadManifest,
  saveStageReviewEvidence
} from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/01-intake/rev-003";
const governing = "hhax-intake-nxedc-source-metadata-r002";
let manifest = loadManifest(modelId);
manifest = saveStageReviewEvidence(modelId, "01-intake", {
  expectedRevision: manifest.revision,
  assets: [
    {
      id: "hhax-gate01-source-inspector-recording-r003",
      slot: "source-inspector-recording",
      path: `${base}/source-inspector-recording.mp4`,
      role: "validation",
      sourceAssetIds: [governing, "hhax-intake-nxedc-video-r002", "model-hhax-intake-r1-f2576ce0"],
      contentClass: "complete-source-inspector-recording",
      description: "完整浏览同款拆解联系表、演示视频、开启结构与用户定制外观来源。"
    },
    {
      id: "hhax-gate01-source-review-snapshot-r003",
      slot: "parameter-snapshot",
      path: `${base}/source-review-parameters.json`,
      role: "validation",
      sourceAssetIds: [governing, "hhax-intake-nxedc-video-r002", "model-hhax-intake-r1-f2576ce0"],
      contentClass: "source-review-parameter-snapshot",
      description: "来源分类、数量、公开标称资格和链接核对快照。"
    },
    {
      id: "hhax-gate01-published-source-qualification-r003",
      slot: "source-qualification",
      path: `${base}/published-source-qualification.json`,
      role: "validation",
      sourceAssetIds: [governing, "hhax-intake-nxedc-source-notes-r002"],
      contentClass: "published-source-qualification",
      description: "把零售页数值限定为同款公开标称，禁止解释成独立实测或制造公差。"
    },
    {
      id: "hhax-gate01-source-inspector-frame-r003",
      slot: "source-inspector-frame",
      path: `${base}/source-inspector-frame.png`,
      role: "validation",
      sourceAssetIds: ["hhax-intake-nxedc-teardown-sheet-r002"],
      contentClass: "source-inspector-still",
      description: "来源检查工作台静帧。"
    }
  ],
  reviewedArtifactId: "hhax-gate01-source-inspector-recording-r003",
  governingContractAssetId: governing,
  parameterSnapshotAssetId: "hhax-gate01-source-review-snapshot-r003",
  completedChecklist: [
    "original-user-sources-preserved",
    "external-source-classification-reviewed",
    "source-links-reviewed"
  ],
  interactionMode: "complete-source-inspector-recording",
  browserTimestamp: new Date().toISOString(),
  reviewDevice: "Chromium desktop 1440×1000",
  recipe: "Gate 01 complete source inspector review"
});
manifest = approveStageFromDelegation(modelId, "01-intake", {
  expectedRevision: manifest.revision,
  notes: "来源归档、分类、公开链接和公开标称边界均经完整录屏复核；用户定制外观与公共机构资料未混用。"
});
console.log(JSON.stringify({ revision: manifest.revision, status: manifest.stages[0].status, decision: manifest.stages[0].decision }, null, 2));
