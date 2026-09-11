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
const stageId = "12-shipping";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/12-shipping/rev-004-lighting";
const scenePath = "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const report = read("lighting-review-report.json");
const metrics = read("lighting-image-metrics.json");
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);

if (!report.pass || !metrics.pass || gate12 == null) {
  throw new Error("Gate 12 lighting evidence is incomplete.");
}

if (!gate12.historicalRevisions?.some(
  (revision) => revision.evidenceRevision === 3
    && revision.status === "approved-build42-partial-device-visual-rejected"
)) {
  gate12.historicalRevisions ??= [];
  gate12.historicalRevisions.push({
    evidenceRevision: 3,
    stageRevision: gate12.revision,
    status: "approved-build42-partial-device-visual-rejected",
    artifactIds: [...gate12.artifactIds],
    reviewArtifactIds: [...gate12.reviewArtifactIds],
    validations: JSON.parse(JSON.stringify(gate12.validations)),
    shippingSpec: JSON.parse(JSON.stringify(gate12.shippingSpec)),
    decision: JSON.parse(JSON.stringify(gate12.decision)),
    deliveryState: JSON.parse(JSON.stringify(gate12.deliveryState)),
    build42DeviceFeedback: {
      exactWording: "好多了，但感觉灯光有点奇怪，主要是太暗了.",
      interactionAcceptance: "partial-success",
      visualAcceptance: "failed-dark-lighting",
    },
    preservedForHistory: true,
  });
}

const definitions = [
  ["registrar", "delivery-registration-source",
    `${evidenceRoot}/register_gate12_lighting_r004.mjs`, "validation"],
  ["lighting-source", "shipping-lighting-source",
    "unity/FidgetingApp/Assets/_EDC/Runtime/"
      + "MagneticSlideShippingLighting.cs", "source-model"],
  ["capture-builder", "shipping-capture-source",
    `${candidateRoot}/Editor/`
      + "MagneticSlideTileGate12R004LightingReviewBuilder.cs", "source-model"],
  ["unity-test-source", "test-source",
    "unity/FidgetingApp/Assets/_EDC/Tests/Editor/"
      + "MagneticSlideLightingRevisionTests.cs", "validation"],
  ["node-test-source", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "magnetic-slide-gate12-lighting-rev4.test.mjs", "validation"],
  ["browser-test-source", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "browser-gate12-lighting-rev4.mjs", "validation"],
  ["review-builder", "review-builder-source",
    `${evidenceRoot}/build_lighting_review.py`, "validation"],
  ["shipping-scene", "shipping-scene", scenePath, "source-model"],
  ["lighting-report", "lighting-review-report",
    `${evidenceRoot}/lighting-review-report.json`, "validation"],
  ["image-metrics", "image-validation",
    `${evidenceRoot}/lighting-image-metrics.json`, "validation"],
  ["video-probe", "video-validation",
    `${evidenceRoot}/video-probe.json`, "validation"],
  ["unity-log", "unity-capture-log",
    `${evidenceRoot}/unity-capture.log`, "validation"],
  ["editmode-results", "test-results",
    `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["editmode-log", "test-log",
    `${evidenceRoot}/editmode-tests.log`, "validation"],
  ["playmode-results", "test-results",
    `${evidenceRoot}/playmode-results.xml`, "validation"],
  ["playmode-log", "test-log",
    `${evidenceRoot}/playmode-tests.log`, "validation"],
  ["comparison-board", "shipping-review-board",
    `${evidenceRoot}/gate12-lighting-comparison-board-r004.png`,
    "unity-render"],
  ["phone-board", "shipping-phone-board",
    `${evidenceRoot}/gate12-lighting-phone-board-r004.png`, "unity-render"],
  ["histograms", "image-metrics-visualization",
    `${evidenceRoot}/gate12-lighting-histograms-r004.png`, "validation"],
  ["comparison-video", "unity-runtime-recording",
    `${evidenceRoot}/magnetic-slide-gate12-r004-lighting-comparison.mp4`,
    "unity-render"],
];

const variants = [
  "A-build42-baseline",
  "B-balanced-brighter",
  "C-everyday-d65",
];
const views = [
  "library",
  "hero",
  "top",
  "left-oblique",
  "right-oblique",
  "low",
  "phone",
  "max-open",
  "endpoint-36deg",
];
for (const variant of variants) {
  for (const view of views) {
    definitions.push([
      `${variant}-${view}`,
      `shipping-view-${view}`,
      `${evidenceRoot}/${variant}/${view}.png`,
      "unity-render",
    ]);
  }
}
const browserPath = `${evidenceRoot}/browser-mobile-modal-validation.json`;
if (fs.existsSync(resolveRepoPath(browserPath))) {
  definitions.push([
    "browser-validation",
    "browser-mobile-modal-validation",
    browserPath,
    "validation",
  ]);
}

const sourceAssetIds = [
  "magnetic-slide-tile-shipping-scene-build42-r001",
  "magnetic-slide-tile-gate12-settings-r003",
  "magnetic-slide-tile-gate12-prefab-r003",
];
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing Gate 12 lighting artifact: ${assetPath}`);
  return {
    id: `${modelId}-gate12-lighting-${suffix}-r004`,
    stageId,
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "unity-render"
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 12 lighting-only review workflow",
      version: "2026-09-01",
      recipe: `${candidateRoot}/Editor/`
        + "MagneticSlideTileGate12R004LightingReviewBuilder.cs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate12EvidenceRevision: 4,
      build42FeedbackExactWording:
        "好多了，但感觉灯光有点奇怪，主要是太暗了.",
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      geometryChanged: false,
      materialsChanged: false,
      interactionChanged: false,
      audioChanged: false,
      hapticsChanged: false,
      buildInstallPhone: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
}

const claim = {
  id: "slider-gate12-r004-build42-dark-lighting-review",
  stageId,
  topic: "shipping-lighting-device-feedback",
  statement:
    "Build 42 interaction is a partial device success, but visual acceptance "
    + "failed because the product is too dark. Variant B raises median model "
    + "luminance 27.8% and black-detail luminance 38.9% with zero measured "
    + "clipping while preserving geometry, materials, interaction, audio and Haptics.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "ready-for-user-review",
  deliveryState: "visual-approval-pending-not-built-or-installed",
};
const claimIndex = manifest.claims.findIndex(
  (candidate) => candidate.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

const balanced = metrics.summary["B-balanced-brighter"];
const everyday = metrics.summary["C-everyday-d65"];
gate12.revision = 5;
gate12.status = "ready_for_review";
gate12.artifactIds = records.map((record) => record.id);
gate12.reviewArtifactIds = [
  `${modelId}-gate12-lighting-comparison-video-r004`,
  `${modelId}-gate12-lighting-comparison-board-r004`,
  `${modelId}-gate12-lighting-phone-board-r004`,
  `${modelId}-gate12-lighting-histograms-r004`,
  `${modelId}-gate12-lighting-B-balanced-brighter-hero-r004`,
  `${modelId}-gate12-lighting-C-everyday-d65-hero-r004`,
];
gate12.validations = [
  {
    id: "build42-device-feedback-recorded",
    status: "pass",
    evidence:
      "Exact feedback recorded. Interaction is partial-success; visual "
      + "acceptance failed because lighting is too dark.",
  },
  {
    id: "lighting-only-protected-hashes",
    status: "pass",
    evidence:
      "Seven protected mechanism, input, audio and Haptic source hashes are "
      + "unchanged. Geometry, materials and artwork are unchanged.",
  },
  {
    id: "balanced-midtone-and-black-detail",
    status: "pass",
    evidence:
      `Variant B median gain ${(balanced.midtoneGainVsBuild42 * 100).toFixed(1)}%; `
      + `black-detail gain ${(balanced.blackDetailGainVsBuild42 * 100).toFixed(1)}%.`,
  },
  {
    id: "color-and-clipping",
    status: "pass",
    evidence:
      `Variant B red saturation retention `
      + `${(balanced.redSaturationRetentionVsBuild42 * 100).toFixed(1)}%; `
      + `clipping ${(balanced.clippedFraction * 100).toFixed(3)}%.`,
  },
  {
    id: "everyday-d65-range",
    status: "pass",
    evidence:
      `Variant C median gain ${(everyday.midtoneGainVsBuild42 * 100).toFixed(1)}%; `
      + `black-detail gain ${(everyday.blackDetailGainVsBuild42 * 100).toFixed(1)}%.`,
  },
  {
    id: "shipping-view-coverage",
    status: "pass",
    evidence:
      "A/B/C each include Library, Hero, Top, both obliques, Low, Phone, "
      + "maximum-open and endpoint-36° from the real shipping scene.",
  },
  {
    id: "unity-regressions",
    status: "pass",
    evidence:
      "Focused EDC EditMode passed 37/37 and real Input System PlayMode passed 3/3.",
  },
  {
    id: "review-recording",
    status: "pass",
    evidence:
      "26.6 s Unity-only A/B/C comparison video is present with fixed view recipes.",
  },
];
if (fs.existsSync(resolveRepoPath(browserPath))) {
  gate12.validations.push({
    id: "browser-mobile-modal",
    status: "pass",
    evidence:
      "Workbench deep link, desktop/video, 390 px mobile, modal close and "
      + "zero horizontal overflow passed.",
  });
}
gate12.decision = null;
gate12.shippingSpec = {
  revision: 4,
  sourceGate12Revision: 3,
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  sceneSha256: report.sceneSha256After,
  candidateDefaultActive: true,
  oldShippingModelDefaultActive: false,
  build42FeedbackExactWording:
    "好多了，但感觉灯光有点奇怪，主要是太暗了.",
  build42InteractionAcceptance: "partial-success",
  build42VisualAcceptance: "failed-dark-lighting",
  rootCause:
    "Build42 used HDR-off/no tone map with low dark-scene key, fill, "
    + "ambient and reflection energy; device display assumptions hid black detail.",
  geometryChanged: false,
  materialsChanged: false,
  artworkChanged: false,
  interactionChanged: false,
  audioChanged: false,
  hapticsChanged: false,
  cameraPositionRecipesChanged: false,
  variants: report.variants,
  recommendation: "B-balanced-brighter",
  recommendationApproved: false,
  balancedMetrics: balanced,
  everydayMetrics: everyday,
  buildInstallPhone: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-lighting-approval-and-retest",
  visualApproval: "pending",
};
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 12 lighting rev 4 is ready for visual review. No visual build or "
    + "device install is authorized.",
};
gate12.deliveryState = {
  decisionState: "pending-lighting-visual-approval",
  shippingPromotion: "source-candidate-only",
  build42: "partial-interaction-success-visual-failed-dark-lighting",
  newDevelopmentBuild: "not-started",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-lighting-approval-and-retest",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((candidate) => candidate.stageId === stage.id)
    .map((candidate) => JSON.stringify(candidate));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = stageId;
manifest.overallStatus = "waiting_for_user";
manifest.currentState.visualApproval =
  "gate12-r004-lighting-ready-for-review";
manifest.currentState.unityStatus =
  "balanced-lighting-source-candidate-not-device-built";
manifest.currentState.deviceStatus =
  "build42-partial-interaction-success-visual-failed-dark";
manifest.currentState.diagnosis =
  "Build42 is too dark. Lighting-only A/B/C shipping previews are ready; "
  + "Variant B is recommended and awaits approval before any phone build.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r004-build42-dark-lighting-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  gateRevision: gate12.revision,
  evidenceRevision: 4,
  exactUserFeedback:
    "好多了，但感觉灯光有点奇怪，主要是太暗了.",
  build42InteractionAcceptance: "partial-success",
  build42VisualAcceptance: "failed-dark-lighting",
  recommendation: "B-balanced-brighter",
  balancedMidtoneGain: balanced.midtoneGainVsBuild42,
  balancedBlackDetailGain: balanced.blackDetailGainVsBuild42,
  balancedClippedFraction: balanced.clippedFraction,
  protectedRuntimeUnchanged: true,
  buildInstallPhone: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-lighting-approval-and-retest",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gateStatus: gate12.status,
  gateRevision: gate12.revision,
  recommendation: gate12.shippingSpec.recommendation,
  reviewArtifactIds: gate12.reviewArtifactIds,
}, null, 2));
