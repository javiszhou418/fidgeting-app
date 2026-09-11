#!/usr/bin/env node
import crypto from "node:crypto";
import {
  digestValues,
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  gate12?.status !== "ready_for_review"
  || gate12?.shippingSpec?.revision !== 3
) {
  throw new Error("Expected Gate 12 rev 3 ready for review.");
}

const exactUserWording = "这个是对的";
const decidedAt = new Date().toISOString();
gate12.status = "approved";
gate12.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt,
  scope:
    "Gate 12 rev 3 corrected attached in-plane motion and preserved static views",
  reviewedArtifactIds: [...gate12.reviewArtifactIds],
  interactionMode: "chat-after-unity-runtime-evidence",
  deviceAcceptance: "pending-user-validation",
};
gate12.shippingSpec = {
  ...gate12.shippingSpec,
  gate12Approval: "approved",
  gate12ApprovalExactWording: exactUserWording,
  gate12ApprovedAt: decidedAt,
  shippingPromotion: "authorized-pending-integration",
  buildInstallPhone: false,
  deviceAcceptance: "pending-user-validation",
};
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 12 rev 3 visual is approved. Shipping promotion and authorized development-device delivery are pending.",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map((claim) => JSON.stringify(claim));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = decidedAt;
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate12-r003-approved-exact-wording";
manifest.currentState.unityStatus =
  "shipping-promotion-authorized-pending-integration";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus =
  "development-build-authorized-pending";
manifest.currentState.diagnosis =
  "The user approved Gate 12 rev 3 with exact wording “这个是对的”. "
  + "Promotion and a physical-device development build are authorized.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-approved-development-device-delivery-authorized",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: decidedAt,
  gate: "12-shipping",
  gateRevision: 3,
  exactUserWording,
  reviewedArtifactIds: gate12.reviewArtifactIds,
  reviewedArtifactSha256: gate12.reviewArtifactIds.map((assetId) => ({
    assetId,
    sha256: manifest.assets.find((asset) => asset.id === assetId)?.sha256,
  })),
  contractSha256:
    "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  parameterSnapshot: {
    maximumTravelMeters: gate12.shippingSpec.maximumTravelMeters,
    detentCount: gate12.shippingSpec.detentCount,
    detentStepDegrees: gate12.shippingSpec.detentStepDegrees,
    maximumTopStackResidualMeters:
      gate12.shippingSpec.maximumTopStackResidualMeters,
    observedDetentMask: gate12.shippingSpec.observedDetentMask,
  },
  completedChecklist: [
    "seven preserved shipping views",
    "corrected maximum-open attached motion",
    "corrected endpoint 12/36/360 degree rotation",
    "Unity-only full endpoint recording",
  ],
  shippingPromotionAuthorized: true,
  developmentBuildInstallLaunchAuthorized: true,
  appStoreSubmissionAuthorized: false,
  deviceAcceptance: "pending-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate12: saved.stages[11].status,
  exactUserWording,
  shippingPromotion: saved.stages[11].shippingSpec.shippingPromotion,
}, null, 2));
