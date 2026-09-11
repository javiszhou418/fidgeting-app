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
const root =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/12-shipping/rev-004-lighting";
const exactDecision =
  "The user selected lighting Variant B in the review UI: balanced brighter "
  + "+0.55 EV, Neutral tone map, ambient 1.25×, reflection/key/fill "
  + "0.70/0.68/0.54.";
const approvalPath = `${root}/variant-b-shipping-approval.json`;
const approval = JSON.parse(fs.readFileSync(
  resolveRepoPath(approvalPath),
  "utf8"));
const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${root}/lighting-review-report.json`),
  "utf8"));
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);

if (
  !["ready_for_review", "approved"].includes(gate12?.status)
  || gate12.revision !== 5
  || approval.exactUserDecision !== exactDecision
  || approval.selectedVariant !== "B-balanced-brighter"
  || report.defaultSourceVariant !== "BalancedBrighter"
  || report.sceneSha256After !== approval.shippingSceneSha256
  || !report.pass
  || !report.protectedRuntimeUnchanged
) {
  throw new Error("Variant B approval evidence does not match Gate 12 rev 4.");
}

const approvalAsset = {
  id: "magnetic-slide-tile-gate12-lighting-variant-b-approval-r004",
  stageId,
  slot: "shipping-visual-approval",
  path: approvalPath,
  sha256: sha256File(resolveRepoPath(approvalPath)),
  exists: true,
  sizeBytes: fs.statSync(resolveRepoPath(approvalPath)).size,
  role: "validation",
  producer: {
    name: "Gate 12 review UI",
    version: "2026-09-01",
    recipe: `${root}/approve_variant_b_shipping.mjs`,
  },
  provenance: {
    origin: "user-provided",
    contentClass: "explicit-visual-approval",
    assertedBy: "user",
    mechanismEvidenceContractSha256:
      "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    selectedVariant: "B-balanced-brighter",
    exactUserDecision: exactDecision,
    reviewedAt: approval.reviewedAt,
  },
  sourceAssetIds: gate12.reviewArtifactIds,
  sourceClaimIds: [],
};
const assetIndex = manifest.assets.findIndex(
  (asset) => asset.id === approvalAsset.id);
if (assetIndex >= 0) manifest.assets[assetIndex] = approvalAsset;
else manifest.assets.push(approvalAsset);
if (!gate12.artifactIds.includes(approvalAsset.id))
  gate12.artifactIds.push(approvalAsset.id);

const refreshPaths = [
  "unity/FidgetingApp/Assets/_EDC/Tests/Editor/"
    + "MagneticSlideLightingRevisionTests.cs",
  "tools/model-provenance-explorer/tests/mechanism-evidence-contract.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/workflow-three-phase.test.mjs",
  `${root}/editmode-results.xml`,
  `${root}/editmode-tests.log`,
  `${root}/playmode-results.xml`,
  `${root}/playmode-tests.log`,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/runtime-recovery-build42/"
    + "run_build42_device_delivery.sh",
  ...fs.readdirSync(resolveRepoPath("tools/model-provenance-explorer/tests"))
    .filter((name) => name.startsWith("magnetic-slide-")
      && name.endsWith(".test.mjs"))
    .map((name) => `tools/model-provenance-explorer/tests/${name}`),
];
for (const path of refreshPaths) {
  const absolute = resolveRepoPath(path);
  for (const asset of manifest.assets.filter((item) => item.path === path)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
  }
}

const claim = manifest.claims.find(
  (item) => item.id === "slider-gate12-r004-build42-dark-lighting-review");
claim.statement =
  "Build 42 interaction is a partial device success and its dark lighting is "
  + "rejected. The user explicitly approved Gate 12 lighting rev 4 Variant B: "
  + "+0.55 EV, HDR, Neutral tone map, ambient 1.25× and "
  + "reflection/key/fill 0.70/0.68/0.54.";
claim.assertedBy = "user-and-measurement";
claim.decisionState = "approved-variant-b";
claim.deliveryState = "shipping-source-approved-new-build-pending";
claim.sourceAssetIds = [
  ...new Set([...claim.sourceAssetIds, approvalAsset.id]),
];

gate12.status = "approved";
gate12.decision = {
  action: "approve",
  notes: exactDecision,
  decidedBy: "user-review-ui",
  decidedAt: approval.reviewedAt,
  scope: "Gate 12 lighting rev 4 Variant B shipping lighting",
  selectedVariant: approval.selectedVariant,
  parameterSnapshot: approval.parameters,
  reviewedArtifactSha256: approval.reviewedArtifacts.map(
    (artifact) => artifact.sha256),
  mechanismEvidenceContractSha256:
    approval.mechanismEvidenceContractSha256,
  interactionMode: approval.interactionMode,
};
gate12.validations = gate12.validations.filter(
  (item) => item.id !== "variant-b-explicit-visual-approval");
gate12.validations.push({
  id: "variant-b-explicit-visual-approval",
  status: "pass",
  evidence:
    "Review UI selected B-balanced-brighter with +0.55 EV, HDR, Neutral, "
    + "ambient 1.25× and reflection/key/fill 0.70/0.68/0.54.",
});
gate12.shippingSpec.recommendationApproved = true;
gate12.shippingSpec.selectedVariant = approval.selectedVariant;
gate12.shippingSpec.approvedLighting = approval.parameters;
gate12.shippingSpec.visualApproval =
  "gate12-r004-variant-b-approved-review-ui";
gate12.shippingSpec.buildInstallPhone = false;
gate12.shippingSpec.deviceAcceptance =
  "pending-new-build-and-user-validation";
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 12 lighting rev 4 Variant B is visually approved. "
    + "A fresh monotonic development build is authorized.",
};
gate12.deliveryState = {
  decisionState: "approved-variant-b",
  shippingPromotion: "shipping-source-approved",
  build42: "partial-interaction-success-visual-rejected-dark",
  newDevelopmentBuild: "authorized-not-started",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-new-build-and-user-validation",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((item) => item.stageId === stage.id)
    .map((item) => JSON.stringify(item));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.overallStatus = "approved";
manifest.currentState.visualApproval =
  "gate12-r004-variant-b-approved-review-ui";
manifest.currentState.unityStatus =
  "variant-b-shipping-source-approved-build-pending";
manifest.currentState.deviceStatus =
  "build42-partial-interaction-success-visual-rejected-dark";
manifest.currentState.diagnosis =
  "Variant B is the approved replacement for Build 42 dark lighting. "
  + "Shipping source is ready for a fresh monotonic development build.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r004-variant-b-approved",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  gateRevision: gate12.revision,
  evidenceRevision: 4,
  exactUserDecision: exactDecision,
  selectedVariant: approval.selectedVariant,
  parameters: approval.parameters,
  reviewedArtifacts: approval.reviewedArtifacts,
  interactionMode: approval.interactionMode,
  protectedRuntimeUnchanged: true,
  build42Acceptance: "partial-interaction-success-visual-rejected-dark",
  newDevelopmentBuild: "authorized",
  appStoreSubmitted: false,
  deviceAcceptance: "pending-new-build-and-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gateStatus: gate12.status,
  selectedVariant: gate12.shippingSpec.selectedVariant,
  visualApproval: saved.currentState.visualApproval,
}, null, 2));
