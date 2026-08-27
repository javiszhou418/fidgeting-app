#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-003";
const manifest = loadManifest(modelId);
const stage = manifest.stages[9];
if (manifest.revision !== 84
  || stage.status !== "rejected"
  || stage.exportSpec?.revision !== 2
  || !stage.decision?.notes?.includes("review presentation is rejected as incomprehensible")) {
  throw new Error("Expected rejected Gate 10 rev 2 presentation at manifest revision 84.");
}
const renderReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/plain-review-render-recipe.json`)));
const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/plain-review-image-validation.json`)));
if (!renderReport.pass
  || !imageReport.pass
  || imageReport.actualBeforeAfterDifference.visuallyObvious !== false
  || imageReport.checks.cropAtLeast3xInDefaultBoard !== true) {
  throw new Error("Plain Gate 10 review evidence did not pass.");
}

const previousArtifactIds = [...stage.artifactIds];
const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r001",
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-export-manifest-r002",
  "magnetic-slide-tile-smoothing-normal-validation-r002",
];
const definitions = [
  ["plain-review-registrar", "registration-source", "register_plain_review.mjs", "process", "register_plain_review.mjs"],
  ["plain-review-renderer", "review-source", "render_plain_round_edge_review.py", "process", "render_plain_round_edge_review.py"],
  ["plain-review-render-recipe", "validation-report", "plain-review-render-recipe.json", "validation", "render_plain_round_edge_review.py"],
  ["plain-review-before-full", "reimport-review", "plain-full-before.png", "blender-render", "render_plain_round_edge_review.py"],
  ["plain-review-after-full", "reimport-review", "plain-full-after.png", "blender-render", "render_plain_round_edge_review.py"],
  ["plain-review-builder", "review-source", "build_plain_round_edge_review.py", "process", "build_plain_round_edge_review.py"],
  ["plain-review-image-validation", "validation-report", "plain-review-image-validation.json", "validation", "build_plain_round_edge_review.py"],
  ["round-edge-location", "round-edge-location", "round-edge-location.png", "blender-render", "build_plain_round_edge_review.py"],
  ["round-edge-before-after", "round-edge-comparison", "round-edge-before-after.png", "blender-render", "build_plain_round_edge_review.py"],
];
const records = definitions.map(([suffix, slot, file, role, recipe]) => {
  const path = `${root}/${file}`;
  const absolutePath = resolveRepoPath(path);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r003`,
    stageId: "10-export",
    slot,
    path,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: file.endsWith(".png") ? "Blender/Pillow review pipeline" : "Python/Node.js",
      version: file.endsWith(".png") ? "Blender 5.2.0 LTS / Pillow" : "Python 3 / Node.js",
      recipe: `${root}/${recipe}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      technicalExportRevision: 2,
      reviewRevision: 3,
      note: "Plain-Chinese review presentation derived from immutable rev 1/rev 2 actual exports. It does not modify geometry or export settings.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

const claimId = "slider-gate10-plain-review-r003";
manifest.claims.push({
  id: claimId,
  stageId: "10-export",
  topic: "gate10-review-clarity",
  statement: "Gate 10 默认评审只回答“圆弧看起来还会不会一节一节？”。主界面只显示检查位置图和同位置约 4 倍放大图；技术术语与非外观碰撞证据默认收起。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["magnetic-slide-tile-export-fbx-r002"],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "requested-and-executed",
  deliveryState: "gate10-plain-review-ready-unity-not-started",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = [...previousArtifactIds, ...records.map((record) => record.id)];
stage.reviewArtifactIds = [
  "magnetic-slide-tile-round-edge-location-r003",
  "magnetic-slide-tile-round-edge-before-after-r003",
];
stage.exportSpec = {
  ...stage.exportSpec,
  revision: 3,
  exportRevision: 2,
  reviewRevision: 3,
  rejectedPresentation: {
    revision: 2,
    status: "rejected-preserved",
    notes: stage.decision.notes,
  },
  presentation: {
    question: "圆弧看起来还会不会一节一节？",
    approvalQuestion: "右边修复后的圆边是否连续、没有一节一节的棱角？",
    defaultAssets: stage.reviewArtifactIds,
    sourceRoiPx: imageReport.roiSourcePixels,
    closeupScaleMinimum: 3,
    actualDifferenceVisuallyObvious: false,
    honestyPolicy: imageReport.honestyPolicy,
    technicalDetailsCollapsed: true,
    collisionRemovedFromPrimaryReview: true,
  },
};
stage.validations = [
  ...stage.validations.filter((validation) => validation.status === "pass"),
  { id: "plain-review-location", status: "pass", evidence: "Full-model image marks the exact front curved side with one orange rectangle and arrow." },
  { id: "plain-review-matched-crop", status: "pass", evidence: "Actual rev 1/rev 2 images use the same 3200×1800 camera, light, exposure, and [540,1040,1200,1700] crop; default closeups are over 3× larger than the marked region." },
  { id: "plain-review-honesty", status: "pass", evidence: `Actual p99 crop delta is ${imageReport.actualBeforeAfterDifference.p99RgbLevels} RGB level, so the board states that the visual difference is subtle instead of inventing a faceted before image.` },
  { id: "plain-review-progressive-disclosure", status: "pass", evidence: "Default review shows two plain-Chinese images and one question. Export jargon and non-visible collision evidence remain under collapsed technical details." },
  { id: "gate10-only-rev3", status: "pass", evidence: "Rev 2 exports are reused unchanged. No geometry, export settings, Gate 11, Unity, build, install, or phone push occurred." },
];
stage.decision = null;
delete stage.staleReason;

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claims]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.currentState.visualApproval = "gate10-plain-review-rev3-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 10 rev 2 的技术 export 证据保持有效且不可变，但默认评审表达已按用户反馈判定 incomprehensible/rejected。rev 3 只重做评审：第一张用完整模型和橙框标出前端圆弧侧边，第二张用完全相同相机／灯光／曝光与 crop 显示实际前后约 4 倍放大。实际 p99 差异仅 0.333 RGB level，因此不伪造“一格一格”的 before；默认只问右图圆边是否连续。技术数据和非外观碰撞图默认收起。未进入 Unity，视觉批准待确认，未推送手机。";
const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  exportRevision: 2,
  reviewRevision: 3,
  rejectedPresentationPreserved: 2,
  artifactIds: records.map((record) => record.id),
  reviewArtifactIds: stage.reviewArtifactIds,
  actualDifferenceVisuallyObvious: false,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[9].status,
  artifactIds: saved.stages[9].artifactIds.length,
  reviewArtifactIds: saved.stages[9].reviewArtifactIds,
  claimId,
}, null, 2));
