#!/usr/bin/env node
import crypto from "node:crypto";
import {
  digestValues,
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate10 = manifest.stages.find((stage) => stage.id === "10-export");
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  manifest.revision !== 250
  || gate10.status !== "ready_for_review"
  || gate10.exportSpec?.revision !== 11
  || gate11.status !== "stale"
) {
  throw new Error("Expected Gate 10 rev 11 review at pipeline revision 250.");
}

const exactUserWording = "继续";
gate10.status = "approved";
gate10.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: new Date().toISOString(),
  scope: "Gate 10 rev 11 corrected real-GLB review",
};
gate10.deliveryState = {
  visualApproval: "approved",
  gate11Advanced: true,
  buildInstallPhone: false,
};

gate11.historicalRevisions = gate11.historicalRevisions || [];
gate11.historicalRevisions.push({
  evidenceRevision: 10,
  stageRevision: gate11.revision,
  status: gate11.status,
  artifactIds: [...gate11.artifactIds],
  reviewArtifactIds: [...gate11.reviewArtifactIds],
  validations: [...gate11.validations],
  unityParitySpec: gate11.unityParitySpec,
  decision: gate11.decision,
  staleReason: gate11.staleReason,
  preservedForHistory: true,
});
gate11.revision = 11;
gate11.status = "draft";
gate11.artifactIds = [];
gate11.reviewArtifactIds = [];
gate11.validations = [];
gate11.decision = null;
delete gate11.staleReason;
gate11.unityParitySpec = {
  revision: 11,
  sourceGate10Revision: 11,
  sourceGate10ApprovalExactWording: exactUserWording,
  sourceGlbAssetId: "magnetic-slide-tile-export-glb-r011",
  sourceGlbSha256: gate10.exportSpec.glbSha256,
  sourceFbxAssetId: "magnetic-slide-tile-export-fbx-r011",
  sourceFbxSha256: gate10.exportSpec.fbxSha256,
  sourceBlendAssetId: "magnetic-slide-tile-export-blend-r011",
  sourceBlendSha256: gate10.exportSpec.authoritativeBlendSha256,
  sourceEnvironmentSha256: gate10.exportSpec.environmentSha256,
  governingContractSha256: gate10.exportSpec.governingContractSha256,
  portabilityContractSha256: gate10.exportSpec.portabilityContractSha256,
  geometryDigest: gate10.exportSpec.geometryDigest,
  materialStateDigest: gate10.exportSpec.materialStateDigest,
  uvDigest: gate10.exportSpec.uvDigest,
  importFolder:
    "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R011",
  shippingSceneModified: false,
  buildInstallPhone: false,
};
gate11.readiness = {
  ready: false,
  blockers: ["Fresh Unity import, parity evidence, runtime recording, and validation are pending."],
  note: "Gate 10 is approved. Gate 11 is isolated and in progress.",
};

gate12.status = "blocked";
gate12.staleReason =
  "Gate 11 rev 11 requires explicit Unity parity approval before Gate 12.";
gate12.decision = null;

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map(stableJson);
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = gate10.decision.decidedAt;
manifest.currentStageId = "11-unity-parity";
manifest.currentState.visualApproval =
  "gate11-rev11-in-progress-not-pushed";
manifest.currentState.blenderModelingStatus =
  "gate10-rev11-approved-exact-wording-continued";
manifest.currentState.unityStatus =
  "gate11-rev11-isolated-import-in-progress";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.workbench = "persistent-seven-tab-current-gate11-unity";
manifest.currentState.diagnosis =
  "The user approved Gate 10 rev 11 with exact wording “继续”. Gate 11 now starts from a fresh isolated import; old Unity candidates remain historical only.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev11-approved-gate11-rev11-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "10-export",
  approvedRevision: 11,
  reviewedArtifactId: "magnetic-slide-tile-export-glb-r011",
  reviewedArtifactSha256: gate10.exportSpec.glbSha256,
  contractSha256: gate10.exportSpec.governingContractSha256,
  parameterSnapshot: {
    geometryDigest: gate10.exportSpec.geometryDigest,
    materialStateDigest: gate10.exportSpec.materialStateDigest,
    uvDigest: gate10.exportSpec.uvDigest,
    environmentSha256: gate10.exportSpec.environmentSha256,
    endpointInterlockOnly: true,
  },
  completedChecklist: ["real corrected GLB loaded", "orbit completed", "zoom completed"],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "11-unity-parity",
  shippingChanged: false,
  simulatorUsed: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate10: saved.stages[9].status,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
}, null, 2));
