#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 240) {
  throw new Error(`Expected pipeline revision 240, got ${manifest.revision}.`);
}
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
if (gate08?.status !== "ready_for_review" || gate08.lightingSpec?.revision !== 6) {
  throw new Error("Gate 08 rev 6 is not ready for approval.");
}
if (!gate08.lightingSpec.immutableSourceSnapshot?.byteElementIdentical) {
  throw new Error("Gate 08 rev 6 immutable source validation is not current.");
}

const now = new Date().toISOString();
const exactUserWording = "你开始吧";
gate08.status = "approved";
gate08.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 08 rev 6 partition-safe portable lighting review",
};
gate08.readiness = {
  ready: true,
  blockers: [],
  note: `Approved in chat with exact wording “${exactUserWording}”.`,
};
gate08.validations.push({
  id: "chat-approval-rev6",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; GLB ${gate08.lightingSpec.interactiveLookdev.sha256}; turntable ${gate08.lightingSpec.legalMotionRecording.sha256}.`,
});

gate09.historicalRevisions = gate09.historicalRevisions || [];
if (!gate09.historicalRevisions.some((entry) => entry.evidenceRevision === 8)) {
  gate09.historicalRevisions.push({
    evidenceRevision: 8,
    stageRevision: gate09.revision,
    status: "stale-superseded",
    artifactIds: [...gate09.artifactIds],
    reviewArtifactIds: [...gate09.reviewArtifactIds],
    validations: structuredClone(gate09.validations),
    environmentSpec: structuredClone(gate09.environmentSpec),
    invalidatedBy: "Gate 08 rev 6 corrected lighting and Gate 07 rev 13 material partitions",
    preservedForHistory: true,
  });
}

gate09.revision = 9;
gate09.status = "draft";
gate09.artifactIds = [];
gate09.reviewArtifactIds = [];
gate09.validations = [];
gate09.decision = null;
gate09.environmentSpec = {
  revision: 9,
  evidenceRevision: 9,
  sourceLightingRevision: 6,
  sourceLightingAssetId: "magnetic-slide-tile-lighting-blend-r006",
  sourceLightingSha256: manifest.assets.find(
    (asset) => asset.id === "magnetic-slide-tile-lighting-blend-r006",
  ).sha256,
  sourceMaterialRevision: 13,
  sourceMaterialSha256: gate08.lightingSpec.sourceMaterialSha256,
  sourceGeometryDigest: gate08.lightingSpec.geometryDigest,
  governingContractSha256: gate08.lightingSpec.mechanismContractSha256,
  sourceLightingApprovalWording: exactUserWording,
  neutralEnvironmentSha256: gate08.lightingSpec.portableRecipe.environmentSha256,
  displayTransform: gate08.lightingSpec.portableRecipe.displayTransform,
  comparisons: {
    environments: ["neutral-control", "target-shipping-like"],
    identical: [
      "camera",
      "model-transform",
      "material-slots",
      "polygon-material-indices",
      "uvs",
      "lights",
      "display-transform",
      "exposure",
    ],
    onlyChanged: ["environment-texture-input"],
  },
  geometryChanged: false,
  materialsChanged: false,
  lightingChanged: false,
  simulatorUsed: false,
  unityUsed: false,
  shippingSceneModified: false,
  buildInstallPhone: false,
};
gate09.readiness = {
  ready: false,
  blockers: ["Gate 09 rev 9 environment evidence is building."],
  note: "Building neutral versus target environment evidence from current Gate 08 rev 6.",
};
delete gate09.staleReason;
for (const downstream of manifest.stages.slice(9)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 09 rev 9 current environment review is not approved.";
}

manifest.currentStageId = "09-environment";
manifest.currentState.visualApproval = "gate08-rev6-approved-gate09-rev9-building";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate09-rev9-current-environment-building";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate09-environment";
manifest.currentState.diagnosis = "Gate 08 rev 6 approved. Gate 09 rev 9 revalidates neutral and target shipping-like environments against current geometry, corrected material partitions, portable lighting, and display mapping.";
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-rev6-approved-gate09-rev9-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "08-lighting",
  approvedRevision: 6,
  reviewedArtifactId: gate08.lightingSpec.interactiveLookdev.assetId,
  reviewedArtifactSha256: gate08.lightingSpec.interactiveLookdev.sha256,
  reviewedTurntableAssetId: gate08.lightingSpec.legalMotionRecording.assetId,
  reviewedTurntableSha256: gate08.lightingSpec.legalMotionRecording.sha256,
  contractSha256: gate08.lightingSpec.mechanismContractSha256,
  geometryDigest: gate08.lightingSpec.geometryDigest,
  parameterSnapshot: {
    sourceLightingSha256: gate09.environmentSpec.sourceLightingSha256,
    sourceMaterialSha256: gate09.environmentSpec.sourceMaterialSha256,
    neutralEnvironmentSha256: gate09.environmentSpec.neutralEnvironmentSha256,
    displayTransform: gate09.environmentSpec.displayTransform,
    sideArtwork: 0,
    undersideArtwork: 0,
    endpointInterlockOnly: true,
  },
  completedChecklist: [
    "interactive Gate 08 lighting GLB reviewed",
    "real Blender endpoint turntable reviewed",
    "four standard views and five passes reviewed",
    "top, side, and silver rim closeups reviewed",
  ],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "09-environment",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: "approved",
  gate09: "draft",
  exactUserWording,
}, null, 2));
