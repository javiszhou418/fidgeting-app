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
const gate11Id = "11-unity-parity";
const gate12Id = "12-shipping";
const exactDecision = "批准 rev 14，构建并安装 Build 44";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/11-unity-parity/rev-014-detail-depth-hybrid";
const approvalPath = `${evidenceRoot}/rev14-final-visual-approval.json`;
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((stage) => stage.id === gate11Id);
const gate12 = manifest.stages.find((stage) => stage.id === gate12Id);
if (
  gate11?.revision !== 14
  || !["ready_for_review", "approved"].includes(gate11.status)
  || !gate12
) {
  throw new Error("Gate 11 rev14 is not approval-ready.");
}

const reviewedArtifacts = gate11.reviewArtifactIds.map((id) => {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing reviewed artifact: ${id}`);
  return { id, path: asset.path, sha256: asset.sha256 };
});
const materialPaths = [
  "M_G11R014_UpperRev12DetailSubstrate.mat",
  "M_G11R014_UpperRev12DetailMotif.mat",
  "M_G11R014_UpperDetailPreservingCrystal.mat",
  "M_G11R014_LowerRev12DetailSubstrate.mat",
  "M_G11R014_LowerRev12DetailMotif.mat",
  "M_G11R014_LowerDetailPreservingCrystal.mat",
].map((name) =>
  `unity/FidgetingApp/Assets/_EDC/Candidates/`
  + `MagneticSlideTileGate11R014/Materials/${name}`);
const materials = materialPaths.map((path) => ({
  path,
  sha256: sha256File(resolveRepoPath(path)),
}));
const approval = {
  schemaVersion: 1,
  modelId,
  gate: gate11Id,
  gateRevision: 14,
  decisionState: "approved",
  exactUserDecision: exactDecision,
  decisionSource: "review-choice",
  decidedAt: new Date().toISOString(),
  interactionMode: "unity-moving-comparison-and-shipping-review",
  mechanismEvidenceContractSha256:
    "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  reviewedArtifacts,
  materials,
  shippingScene: {
    path: "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity",
    sha256: sha256File(resolveRepoPath(
      "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity")),
  },
  approvedComposition: {
    detail: "rev12 authored RGB, mica, microflake, roughness, normal and motif",
    depth: "rev13 substrate/motif/crystal physical layer offsets",
    lighting: "B-balanced-brighter",
  },
  preserved: {
    darkSideNoArtwork: true,
    silverRim: true,
    geometry: true,
    colliders: true,
    endpointInterlock: true,
    clockwiseCounterclockwiseMapping: true,
    pinchOrbit: true,
    audio: true,
    haptics: true,
  },
  build44: {
    authorized: true,
    attempted: false,
    blocker: "iPhone 15 Pro Max is paired but unavailable.",
  },
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build44-install-and-user-validation",
};
fs.writeFileSync(
  resolveRepoPath(approvalPath),
  `${JSON.stringify(approval, null, 2)}\n`);

const approvalAsset = {
  id: "magnetic-slide-tile-gate11-r014-final-visual-approval",
  stageId: gate11Id,
  slot: "user-approval",
  path: approvalPath,
  sha256: sha256File(resolveRepoPath(approvalPath)),
  exists: true,
  sizeBytes: fs.statSync(resolveRepoPath(approvalPath)).size,
  role: "validation",
  producer: {
    name: "Gate 11 rev14 approval recorder",
    version: "2026-09-03",
    recipe: `${evidenceRoot}/approve_r014_build44_blocked_device.mjs`,
  },
  provenance: {
    origin: "user-provided",
    contentClass: "user-approval",
    assertedBy: "user",
    evidenceRevision: 14,
    mechanismEvidenceContractSha256:
      "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  },
  sourceAssetIds: [...gate11.reviewArtifactIds],
  sourceClaimIds: [],
};
const approvalIndex = manifest.assets.findIndex(
  (asset) => asset.id === approvalAsset.id);
if (approvalIndex >= 0) manifest.assets[approvalIndex] = approvalAsset;
else manifest.assets.push(approvalAsset);
if (!gate11.artifactIds.includes(approvalAsset.id))
  gate11.artifactIds.push(approvalAsset.id);

const refreshedPaths = [
  `${evidenceRoot}/approve_r014_build44_blocked_device.mjs`,
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate11-true-layers-r13.test.mjs",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
];
for (const path of refreshedPaths) {
  const absolute = resolveRepoPath(path);
  for (const asset of manifest.assets.filter((item) => item.path === path)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
  }
}

const claim = manifest.claims.find(
  (candidate) => candidate.id === "slider-gate11-r014-detail-depth-hybrid");
if (claim) {
  claim.state = "approved";
  claim.decisionState = "approved-by-user";
  claim.deliveryState =
    "shipping-source-applied-build44-authorized-device-unavailable";
  claim.exactUserDecision = exactDecision;
  if (!claim.sourceAssetIds.includes(approvalAsset.id))
    claim.sourceAssetIds.push(approvalAsset.id);
}

gate11.status = "approved";
gate11.decision = {
  action: "approve",
  decidedBy: "user",
  decidedAt: approval.decidedAt,
  notes: exactDecision,
  source: "review-choice",
  reviewedArtifactSha256: reviewedArtifacts.map((item) => item.sha256),
  governingContractSha256:
    approval.mechanismEvidenceContractSha256,
};
gate11.unityParitySpec.visualApproval = "approved-rev14";
gate11.unityParitySpec.build44InstallAuthorized = true;
gate11.unityParitySpec.deviceGpuTiming =
  "pending-build44-install-and-device-validation";
gate11.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 11 rev14 is approved. Build 44 is authorized; the paired iPhone "
    + "is unavailable, so delivery has not started.",
};
gate11.deliveryState = {
  decisionState: "approved-rev14",
  shippingSource: "detail-depth-hybrid-r014-applied",
  build42: "rejected-visual-material-and-rotation-direction",
  build43: "non-reusable-xcode-disk-full",
  build44: "authorized-not-started-device-unavailable",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build44-install-and-user-validation",
};

gate12.status = "approved";
gate12.decision = {
  action: "approve",
  decidedBy: "user",
  decidedAt: approval.decidedAt,
  notes: exactDecision,
  sourceGate11Revision: 14,
};
gate12.staleReason = null;
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Rev14 material and approved Variant B lighting are current shipping "
    + "source. Device delivery is blocked only by unavailable hardware.",
};
gate12.shippingSpec.materialApproval = {
  gate11Revision: 14,
  exactUserDecision: exactDecision,
  approvalAssetId: approvalAsset.id,
  composition: approval.approvedComposition,
  shippingSceneSha256: approval.shippingScene.sha256,
};
gate12.shippingSpec.deviceAcceptance =
  "pending-build44-install-and-user-validation";
gate12.deliveryState = {
  decisionState: "approved-rev14-variant-b",
  shippingPromotion: "shipping-source-applied",
  build42: "rejected",
  build43: "non-reusable",
  build44: "authorized-not-started-device-unavailable",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build44-install-and-user-validation",
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
manifest.updatedAt = approval.decidedAt;
manifest.currentStageId = gate12Id;
manifest.overallStatus = "approved";
manifest.currentState.visualApproval =
  "gate11-r014-approved-build44-authorized";
manifest.currentState.unityStatus =
  "rev14-shipping-source-applied-build44-authorized";
manifest.currentState.deviceStatus =
  "paired-unavailable-build44-not-started";
manifest.currentState.diagnosis =
  "Rev14 is approved and already applied to MeshyEDC with Variant B "
  + "lighting. Disk has 159 GiB free and no build writer is active. "
  + "devicectl reports the paired iPhone unavailable, so Build 44 did not "
  + "start.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate11-r014-approved-build44-device-unavailable",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gate11Id,
  gateRevision: 14,
  exactUserDecision: exactDecision,
  decisionSource: "review-choice",
  approvalAssetId: approvalAsset.id,
  reviewedArtifactSha256: reviewedArtifacts.map((item) => item.sha256),
  governingContractSha256: approval.mechanismEvidenceContractSha256,
  shippingSceneSha256: approval.shippingScene.sha256,
  build44Authorized: true,
  build44Attempted: false,
  deviceState: "paired-unavailable",
  freeDiskGiB: 159,
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build44-install-and-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate11Status: gate11.status,
  gate12Status: gate12.status,
  visualApproval: saved.currentState.visualApproval,
  build44Authorized: true,
  build44Attempted: false,
  deviceStatus: saved.currentState.deviceStatus,
}, null, 2));
