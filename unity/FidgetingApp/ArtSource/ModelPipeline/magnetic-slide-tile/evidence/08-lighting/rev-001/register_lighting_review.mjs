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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-001";
const manifest = loadManifest(modelId);
const materialStage = manifest.stages[6];
const stage = manifest.stages[7];
if (manifest.revision !== 66
  || materialStage.status !== "approved"
  || materialStage.decision?.notes !== "可以"
  || stage.artifactIds.length !== 0) {
  throw new Error("Expected exact Gate 07 approval at manifest revision 66 and an empty Gate 08.");
}

const definitions = [
  ["review-registrar", "registration-source", "register_lighting_review.mjs"],
  ["lighting-builder", "lighting-source", "build_lighting_validation.py"],
  ["lighting-blend", "lighting-blend", "magnetic-slide-tile-lighting-r001.blend"],
  ["lighting-validation", "validation-report", "lighting-validation.json"],
  ["image-validator", "validation-source", "validate_lighting_images.py"],
  ["image-validation", "validation-report", "image-lighting-validation.json"],
  ["blender-audit-source", "validation-source", "audit_blender_lighting.py"],
  ["blender-audit", "validation-report", "blender-lighting-audit.json"],
  ["unity-plan-source", "specification-source", "prepare_unity_reflection_plan.py"],
  ["unity-reflection-plan", "specification", "unity-reflection-plan.json"],
  ["hero", "hero", "hero.png"],
  ["left-oblique", "left-oblique", "left-oblique.png"],
  ["right-oblique", "right-oblique", "right-oblique.png"],
  ["low-angle", "low-angle", "low-angle.png"],
  ["pass-beauty", "pass-beauty", "pass-beauty.png"],
  ["pass-clay", "pass-clay", "pass-clay.png"],
  ["pass-normal", "pass-normal", "pass-normal.png"],
  ["pass-depth", "pass-depth", "pass-depth.png"],
  ["pass-roughness", "pass-roughness", "pass-roughness.png"],
  ["open-side-reflection", "lighting-diagnostic", "open-side-reflection.png"],
  ["lighting-view-board", "lighting-review-board", "lighting-view-board.png"],
  ["lighting-pass-board", "lighting-review-board", "lighting-pass-board.png"],
  ["workbench-capture-source", "validation-source", "capture_gate08_workbench.py"],
  ["lighting-workbench", "lighting-review-board", "gate08-workbench.png"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-material-blend-r007",
  "magnetic-slide-tile-material-validation-r007",
  "magnetic-slide-tile-material-image-validation-r007",
  "magnetic-slide-tile-geometry-blend-r001",
];
const sourceClaimIds = [
  "slider-wide-black-border-d65-silver-r007",
  "slider-blockout-point-axis-distinction-r003",
  "slider-ratchet-30-detent-requirement-r001",
];
const lighting = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/lighting-validation.json`)));
const image = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/image-lighting-validation.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-lighting-audit.json`)));
const unityPlan = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/unity-reflection-plan.json`)));
if (![lighting, image, audit, unityPlan].every((report) => report.pass)
  || lighting.sourceGate07.approvalWording !== "可以"
  || lighting.geometry.unchanged !== true
  || unityPlan.deliveryState !== "specified-only-not-integrated") {
  throw new Error("Gate 08 rev 1 evidence did not pass.");
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
    stageId: "08-lighting",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "process",
    producer: {
      name: isBlend || isImage ? "Blender/Pillow lighting evidence pipeline" : "Python/Node.js",
      version: isBlend || isImage ? lighting.lightingRecipe.blender : "Python 3 / Node.js",
      recipe: `${root}/${isSource ? file : "build_lighting_validation.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 08 rev 1 uses approved Gate 07 rev 7 materials and unchanged geometry. It records controlled lighting only; Unity reflection remains specified-only and Gate 09 environment work remains blocked.",
      approvedGate07Decision: "可以",
      sourceGeometryDigest: lighting.geometry.expectedDigest,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const approvalClaimId = "slider-gate07-r007-user-approval-r001";
manifest.claims.push({
  id: approvalClaimId,
  stageId: "07-material",
  topic: "gate07-rev7-approval",
  statement: "用户以原文“可以”批准 Gate 07 rev 7。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["magnetic-slide-tile-material-blend-r007"],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "locked",
  deliveryState: "gate07-approved-gate08-lighting-review-pending",
});
const reflectionClaimId = "slider-unity-scene-reflection-plan-r001";
manifest.claims.push({
  id: reflectionClaimId,
  stageId: "08-lighting",
  topic: "unity-scene-reflection",
  statement: "银色镜面主体可在 Unity URP 17.5 中通过 local reflection probes 与 skybox/HDRI 获得近似 cubemap 场景反射；Mobile_RPAsset 已启用 probe blending、box projection 与 atlas。realtime probes 只在必要时更新，不每帧更新。这不是 ray-traced／per-pixel true mirror。水晶 transmission／iridescence 需要 URP Shader Graph 或 custom approximation。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [`${modelId}-unity-reflection-plan-r001`],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "specified",
  deliveryState: "specified-only-not-integrated-gate09-and-gate11-verification-pending-device-acceptance-pending",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "lighting-view-board",
  "hero",
  "left-oblique",
  "right-oblique",
  "low-angle",
  "lighting-pass-board",
  "pass-beauty",
  "pass-clay",
  "pass-normal",
  "pass-depth",
  "pass-roughness",
  "open-side-reflection",
  "lighting-workbench",
].map((suffix) => `${modelId}-${suffix}-r001`);
stage.lightingSpec = {
  revision: 1,
  sourceMaterialRevision: 7,
  sourceMaterialApprovalWording: "可以",
  sourceGeometryDigest: lighting.geometry.expectedDigest,
  controlledRig: lighting.lightingRecipe,
  cameras: lighting.cameras,
  outputs: lighting.outputs,
  imageMetrics: image,
  unityReflection: {
    planAssetId: `${modelId}-unity-reflection-plan-r001`,
    decisionState: unityPlan.decisionState,
    deliveryState: unityPlan.deliveryState,
    reflectionType: unityPlan.laterUnityStrategy.reflectionType,
    verificationGates: ["09-environment", "11-unity-parity"],
    deviceAcceptance: "pending",
  },
  environmentCompositionDeferredToGate09: true,
};
stage.validations = [
  { id: "gate07-exact-approval", status: "pass", evidence: "Gate 07 rev 7 is approved with exact user wording “可以”." },
  { id: "geometry-preserved", status: "pass", evidence: `Digest ${lighting.geometry.expectedDigest}; object matrices and closed pose unchanged.` },
  { id: "material-language-preserved", status: "pass", evidence: "Full black top perimeter, blood-red crystal, clean motif, silver sides, clean lower plane, and point-axis semantics remain unchanged." },
  { id: "controlled-lighting-rig", status: "pass", evidence: "Four documented area lights, uniform neutral world, fixed EV 0, 6504 K white balance, and four camera-hidden reflection cards." },
  { id: "required-views", status: "pass", evidence: "Authored Hero, left oblique, right oblique, and low angle are real Blender renders." },
  { id: "required-passes", status: "pass", evidence: "Beauty, Clay, Normal, Depth, and Roughness passes are present and quantitatively distinct." },
  { id: "silver-neutral-bright", status: "pass", evidence: `Hero neutral highlight L*/C*/b* ${image.views.hero.silver.medianLStar}/${image.views.hero.silver.medianCStar}/${image.views.hero.silver.medianBStar}; left ${image.views.leftOblique.silver.medianLStar}/${image.views.leftOblique.silver.medianCStar}/${image.views.leftOblique.silver.medianBStar}.` },
  { id: "clipping-controlled", status: "pass", evidence: `Whole-image clipping fractions remain between ${Math.min(...Object.values(image.views).map((view) => view.silver.wholeImageClipAbove250Fraction))} and ${Math.max(...Object.values(image.views).map((view) => view.silver.wholeImageClipAbove250Fraction))}.` },
  { id: "blood-red-no-pink", status: "pass", evidence: `Hero hue ${image.views.hero.bloodRed.signedHueMedianDegrees}°; pink fraction ${image.views.hero.bloodRed.pinkFraction}; blood-red fraction ${image.views.hero.bloodRed.bloodRedFraction}.` },
  { id: "seams-and-motif-visible", status: "pass", evidence: `Hero Laplacian ${image.views.hero.structure.laplacianVariance}; ${image.views.hero.structure.cannyEdgePixels} edge pixels.` },
  { id: "shipping-no-emission", status: "pass", evidence: "All approved shipping material emission strengths remain 0. Technical unlit overrides are isolated pass materials only." },
  { id: "unity-reflection-specified-only", status: "pass", evidence: "URP 17.5 reflection-probe plan is specified-only, not integrated; Gate 09/11 and device acceptance remain pending." },
  { id: "gate08-only", status: "pass", evidence: "No Gate 09, Unity edits, runtime, reflection probe, Shader Graph, Haptic, build, install, or phone push work was performed." },
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
manifest.currentState.visualApproval = "gate08-lighting-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 07 rev 7 已以用户原文“可以”批准。Gate 08 rev 1 使用获批材质和未变 geometry，以 4 灯 neutral controlled rig、fixed EV 0、6504 K white balance 与 reflection cards 生成 Hero／左右斜视／低角及 Beauty／Clay／Normal／Depth／Roughness。Unity URP 17.5 场景反射方案仅 specified-only：local probes + skybox/HDRI，非 true mirror；Gate 09/11 验证和真机验收待完成。当前等待 Gate 08 视觉批准，未推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  lightingRevision: 1,
  sourceMaterialRevision: 7,
  sourceMaterialApprovalWording: "可以",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  unityReflectionDeliveryState: unityPlan.deliveryState,
  geometryDigest: lighting.geometry.expectedDigest,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  stageRevision: saved.stages[7].revision,
  status: saved.stages[7].status,
  artifacts: saved.stages[7].artifactIds.length,
  reviewArtifacts: saved.stages[7].reviewArtifactIds.length,
  approvalClaimId,
  reflectionClaimId,
}, null, 2));
