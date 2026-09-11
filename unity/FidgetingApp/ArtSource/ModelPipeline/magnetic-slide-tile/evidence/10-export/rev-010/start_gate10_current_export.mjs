#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 243) {
  throw new Error(`Expected pipeline revision 243, got ${manifest.revision}.`);
}
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
const gate10 = manifest.stages.find((stage) => stage.id === "10-export");
if (gate09?.status !== "ready_for_review" || gate09.environmentSpec?.revision !== 9) {
  throw new Error("Gate 09 rev 9 is not ready for approval.");
}
const lookdev = manifest.assets.find((asset) => asset.id === gate09.environmentSpec.interactiveReviewArtifactId);
const turntable = manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-environment-turntable-r009");
if (!lookdev || !turntable) throw new Error("Gate 09 interactive evidence is missing.");

const now = new Date().toISOString();
const exactUserWording = "继续";
gate09.status = "approved";
gate09.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 09 rev 9 current environment review",
};
gate09.readiness = {
  ready: true,
  blockers: [],
  note: `Approved in chat with exact wording “${exactUserWording}”.`,
};
gate09.validations.push({
  id: "chat-approval-rev9",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; GLB ${lookdev.sha256}; turntable ${turntable.sha256}.`,
});
gate09.deliveryState = {
  ...gate09.deliveryState,
  visualApproval: "approved",
  gate10Advanced: true,
};

gate10.historicalRevisions = gate10.historicalRevisions || [];
if (!gate10.historicalRevisions.some((entry) => entry.evidenceRevision === 9)) {
  gate10.historicalRevisions.push({
    evidenceRevision: 9,
    stageRevision: gate10.revision,
    status: "stale-superseded",
    artifactIds: [...gate10.artifactIds],
    reviewArtifactIds: [...gate10.reviewArtifactIds],
    validations: structuredClone(gate10.validations),
    exportSpec: structuredClone(gate10.exportSpec),
    invalidatedBy: "Gate 09 rev 9 current environment, Gate 08 rev 6 lighting, and Gate 07 rev 13 material partitions",
    preservedForHistory: true,
  });
}

gate10.revision = 11;
gate10.status = "draft";
gate10.artifactIds = [];
gate10.reviewArtifactIds = [];
gate10.validations = [];
gate10.decision = null;
gate10.exportSpec = {
  revision: 10,
  evidenceRevision: 10,
  sourceGate09Revision: 9,
  sourceGate09ApprovalWording: exactUserWording,
  sourceBlendAssetId: "magnetic-slide-tile-environment-blend-r009",
  sourceBlendSha256: manifest.assets.find(
    (asset) => asset.id === "magnetic-slide-tile-environment-blend-r009",
  ).sha256,
  geometryDigest: gate09.environmentSpec.sourceGeometryDigest,
  materialDigest: gate09.environmentSpec.sourceMaterialSha256,
  lightingSha256: gate09.environmentSpec.sourceLightingSha256,
  environmentSha256: gate09.environmentSpec.targetEnvironmentSha256,
  portabilityContractSha256: gate09.environmentSpec.portabilityContractSha256,
  governingContractSha256: gate09.environmentSpec.governingContractSha256,
  defaultPose: "closed-zero-motion",
  simulatorUsed: false,
  unityImportApplied: false,
  shippingSceneModified: false,
  buildInstallDevice: false,
};
gate10.readiness = {
  ready: false,
  blockers: ["Gate 10 rev 10 fresh export package is building."],
  note: "Building a fresh hash-locked export from approved Gate 09 rev 9.",
};
delete gate10.staleReason;
for (const downstream of manifest.stages.slice(10)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 10 rev 10 export review is not approved.";
}

manifest.currentStageId = "10-export";
manifest.currentState.visualApproval = "gate09-rev9-approved-gate10-rev10-building";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate10-rev10-current-export-building";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate10-export";
manifest.currentState.diagnosis = "Gate 09 rev 9 approved. Gate 10 rev 10 rebuilds and independently reimports the current export package.";
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-rev9-approved-gate10-rev10-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "09-environment",
  approvedRevision: 9,
  reviewedArtifactId: lookdev.id,
  reviewedArtifactSha256: lookdev.sha256,
  reviewedTurntableAssetId: turntable.id,
  reviewedTurntableSha256: turntable.sha256,
  contractSha256: gate09.environmentSpec.portabilityContractSha256,
  geometryDigest: gate09.environmentSpec.sourceGeometryDigest,
  parameterSnapshot: {
    sourceBlendSha256: gate10.exportSpec.sourceBlendSha256,
    sourceMaterialSha256: gate10.exportSpec.materialDigest,
    targetEnvironmentSha256: gate10.exportSpec.environmentSha256,
    displayTransform: gate09.environmentSpec.displayMapping,
    sideArtwork: 0,
    undersideArtwork: 0,
    endpointInterlockOnly: true,
  },
  completedChecklist: [
    "interactive Gate 09 environment GLB reviewed",
    "neutral versus target environment turntable reviewed",
    "closed and endpoint poses reviewed",
    "HDR and cubemap portability reviewed",
  ],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "10-export",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate09: "approved",
  gate10: "draft",
  exactUserWording,
}, null, 2));
