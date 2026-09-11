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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-001";
const manifest = loadManifest(modelId);
const lightingStage = manifest.stages[7];
const stage = manifest.stages[8];
if (manifest.revision !== 69
  || lightingStage.status !== "approved"
  || lightingStage.decision?.notes !== "可以吧，然后你继续"
  || stage.artifactIds.length !== 0) {
  throw new Error("Expected exact Gate 08 approval at manifest revision 69 and an empty Gate 09.");
}

const definitions = [
  ["environment-review-registrar", "registration-source", "register_environment_review.mjs"],
  ["environment-optimization-source", "decision-source", "prepare_optimization_decision.py"],
  ["environment-optimization-decision", "decision-report", "optimization-decision.json"],
  ["environment-builder", "environment-source", "build_environment_comparison.py"],
  ["environment-blend", "environment-blend", "magnetic-slide-tile-environment-r001.blend"],
  ["environment-validation", "validation-report", "environment-validation.json"],
  ["environment-image-validator", "validation-source", "validate_environment_images.py"],
  ["environment-image-validation", "validation-report", "image-environment-validation.json"],
  ["environment-blender-audit-source", "validation-source", "audit_blender_environment.py"],
  ["environment-blender-audit", "validation-report", "blender-environment-audit.json"],
  ["neutral-environment", "neutral-environment", "neutral-environment.png"],
  ["shipping-environment", "shipping-environment", "shipping-environment.png"],
  ["neutral-side-reflection", "environment-diagnostic", "neutral-side-reflection.png"],
  ["shipping-side-reflection", "environment-diagnostic", "shipping-side-reflection.png"],
  ["environment-comparison-board", "environment-review-board", "environment-comparison-board.png"],
  ["reflection-closeup-comparison", "environment-review-board", "reflection-closeup-comparison.png"],
  ["environment-difference-map", "environment-diagnostic", "environment-difference-map.png"],
  ["environment-workbench-capture-source", "validation-source", "capture_gate09_workbench.py"],
  ["environment-workbench", "environment-review-board", "gate09-workbench.png"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-lighting-blend-r001",
  "magnetic-slide-tile-pass-beauty-r001",
  "magnetic-slide-tile-right-oblique-r001",
  "magnetic-slide-tile-unity-reflection-plan-r001",
  "magnetic-slide-tile-material-blend-r007",
  "magnetic-slide-tile-geometry-blend-r001",
];
const sourceClaimIds = [
  "slider-wide-black-border-d65-silver-r007",
  "slider-blockout-point-axis-distinction-r003",
  "slider-ratchet-30-detent-requirement-r001",
  "slider-unity-scene-reflection-plan-r001",
];
const environment = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/environment-validation.json`)));
const image = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/image-environment-validation.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-environment-audit.json`)));
const optimization = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/optimization-decision.json`)));
if (![environment, image, audit, optimization].every((report) => report.pass)
  || environment.sourceGate08.approvalWording !== "可以吧，然后你继续"
  || environment.invariants.geometryUnchanged !== true
  || image.differences.neutralBaselineVsGate08Beauty.maxChannelDelta !== 0
  || optimization.measuredModel.totalTriangles !== 4096) {
  throw new Error("Gate 09 rev 1 evidence did not pass.");
}

const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isSource = /\.(py|mjs)$/.test(file);
  const isBlend = file.endsWith(".blend");
  const isImage = file.endsWith(".png");
  return {
    id: `${modelId}-${suffix}-r001`,
    stageId: "09-environment",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "process",
    producer: {
      name: isBlend || isImage ? "Blender/Pillow environment evidence pipeline" : "Python/Node.js",
      version: isBlend || isImage ? environment.matchedComparison.blender : "Python 3 / Node.js",
      recipe: `${root}/${isSource ? file : "build_environment_comparison.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 09 rev 1 isolates the canonical shipping-like environment from the approved Gate 08 camera, light, geometry, pose, and material contracts. Blender reflections are preview evidence, not Unity integration.",
      approvedGate08Decision: "可以吧，然后你继续",
      sourceGeometryDigest: environment.invariants.expectedGeometryDigest,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const approvalClaimId = "slider-gate08-r001-user-approval-r001";
manifest.claims.push({
  id: approvalClaimId,
  stageId: "08-lighting",
  topic: "gate08-rev1-approval",
  statement: "用户以原文“可以吧，然后你继续”批准 Gate 08 rev 1，并授权继续至 Gate 09。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["magnetic-slide-tile-lighting-blend-r001"],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "locked",
  deliveryState: "gate08-approved-gate09-environment-review-pending",
});
const optimizationClaimId = "slider-model-optimization-r001";
manifest.claims.push({
  id: optimizationClaimId,
  stageId: "09-environment",
  topic: "model-optimization",
  statement: "保留当前 4,096 三角面的单一近景模型，不创建 high/low 或 LOD；上下 artwork mask 保持独立替换。只有 Unity 多模型同屏 profiling 证明需要时才创建简化 Library 模型。未来 high-poly 只用于 bake 且永不 shipping；ASTC/channel packing 留至 Gate 10/Unity import，尚未交付。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [`${modelId}-environment-optimization-decision-r001`],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: optimization.decisionState,
  deliveryState: "single-model-preserved-no-lod-created-library-simplification-conditional-astc-channel-packing-gate10-pending",
});
const environmentClaimId = "slider-gate09-canonical-environment-r001";
manifest.claims.push({
  id: environmentClaimId,
  stageId: "09-environment",
  topic: "canonical-shipping-like-environment",
  statement: "Gate 09 target uses the canonical near-black, low-saturation top-down adaptive field and a unified dark ground. The Blender world preview shows the environment response that polished silver could sample from a skybox/local probe; it is not Unity Reflection Probe integration.",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [`${modelId}-environment-comparison-board-r001`, `${modelId}-reflection-closeup-comparison-r001`],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "specified-for-review",
  deliveryState: "blender-preview-ready-unity-integration-not-started",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "environment-comparison-board",
  "shipping-environment",
  "neutral-environment",
  "reflection-closeup-comparison",
  "shipping-side-reflection",
  "neutral-side-reflection",
  "environment-difference-map",
  "environment-workbench",
].map((suffix) => `${modelId}-${suffix}-r001`);
stage.environmentSpec = {
  revision: 1,
  sourceLightingRevision: 1,
  sourceLightingApprovalWording: "可以吧，然后你继续",
  sourceGeometryDigest: environment.invariants.expectedGeometryDigest,
  matchedComparison: environment.matchedComparison,
  neutralEnvironment: environment.neutralEnvironment,
  shippingLikeEnvironment: environment.shippingLikeEnvironment,
  isolatedDifferences: environment.isolatedDifferences,
  imageMetrics: image.metrics,
  imageDifferences: image.differences,
  blenderReflectionDeliveryState: "preview-only-not-unity-integration",
  optimization: {
    decisionAssetId: `${modelId}-environment-optimization-decision-r001`,
    decisionState: optimization.decisionState,
    deliveryState: optimization.deliveryState,
    triangles: optimization.measuredModel.totalTriangles,
    noLodOrGeometryChange: true,
  },
};
stage.validations = [
  { id: "gate08-exact-approval", status: "pass", evidence: "Gate 08 rev 1 is approved with exact user wording “可以吧，然后你继续”." },
  { id: "neutral-baseline-identical", status: "pass", evidence: "The Gate 09 neutral image is pixel-identical to Gate 08 pass-beauty: max channel delta 0." },
  { id: "environment-only-isolation", status: "pass", evidence: "Geometry digest, object matrices, camera transforms/lenses, material hashes/assignments, pose, light rig, EV, white balance, and reflection-card transforms are identical." },
  { id: "canonical-environment-authority", status: "pass", evidence: "Shipping-like world follows FDB-SCN-001/002 and MeshyEDC camera background; no new visual direction was introduced." },
  { id: "environment-reflection-visible", status: "pass", evidence: `Matched-camera mean absolute channel delta ${image.differences.fullMatchedCamera.meanAbsoluteChannelDelta}; side reflection ROI delta ${image.differences.sideReflectionRoi.meanAbsoluteChannelDelta}.` },
  { id: "silver-neutral-bright", status: "pass", evidence: `Shipping silver body L*/C*/b* ${image.metrics.shipping.silver.neutralSilverBody.medianLStar}/${image.metrics.shipping.silver.neutralSilverBody.medianCStar}/${image.metrics.shipping.silver.neutralSilverBody.medianBStar}; bright reflection L* ${image.metrics.shipping.silver.brightSilverReflection.medianLStar}.` },
  { id: "blood-red-no-pink", status: "pass", evidence: `Shipping hue ${image.metrics.shipping.bloodRed.signedHueMedianDegrees}°; pink ${image.metrics.shipping.bloodRed.pinkFraction}; blood red ${image.metrics.shipping.bloodRed.bloodRedFraction}.` },
  { id: "motif-and-border-readable", status: "pass", evidence: `Shipping motif contrast ratio ${image.metrics.shipping.motif.redDarkContrastRatio}; Laplacian ${image.metrics.shipping.motif.laplacianVariance}; ${image.metrics.shipping.motif.cannyEdgePixels} edges.` },
  { id: "clipping-and-emission-controlled", status: "pass", evidence: `Shipping clipping ${image.metrics.shipping.silver.wholeImageClipAbove250Fraction}; all approved shipping emission strengths are 0.` },
  { id: "optimization-decision", status: "pass", evidence: "One 4,096-triangle close-up model remains; no high/low variants, LODs, geometry changes, export, ASTC, or channel-packing work was created." },
  { id: "unity-reflection-preview-only", status: "pass", evidence: "Blender environment response is labeled preview-only. No Unity skybox, local probe, Shader Graph, runtime, or Haptic integration occurred." },
  { id: "gate09-only", status: "pass", evidence: "No Gate 10 export, Unity edit, build, install, or phone push was performed." },
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
  const claimRecords = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claimRecords]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claimRecords]);
}
manifest.currentState.visualApproval = "gate09-environment-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 08 rev 1 已以用户原文“可以吧，然后你继续”批准。Gate 09 rev 1 用完全相同的获批相机、geometry、material、pose、EV、white balance 与四灯 rig，对比 Gate 08 中性环境和 canonical shipping-like 随形微光环境；只有 world、ground 与环境反射输入变化。Blender 反射仅为 preview，未集成 Unity。4,096 三角面单模型优化决定已锁定；未创建 LOD，Gate 10 ASTC/channel packing 未开始。当前等待 Gate 09 视觉批准，未推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "09-environment",
  environmentRevision: 1,
  sourceLightingRevision: 1,
  sourceLightingApprovalWording: "可以吧，然后你继续",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  geometryDigest: environment.invariants.expectedGeometryDigest,
  optimizationDecisionState: optimization.decisionState,
  unityReflectionDeliveryState: "preview-only-not-integrated",
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  stageRevision: saved.stages[8].revision,
  status: saved.stages[8].status,
  artifacts: saved.stages[8].artifactIds.length,
  reviewArtifacts: saved.stages[8].reviewArtifactIds.length,
  approvalClaimId,
  optimizationClaimId,
  environmentClaimId,
}, null, 2));
