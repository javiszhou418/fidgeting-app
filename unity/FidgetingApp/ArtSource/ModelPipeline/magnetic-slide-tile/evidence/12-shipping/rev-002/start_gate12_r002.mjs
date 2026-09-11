#!/usr/bin/env node
import crypto from "node:crypto";
import {
  digestValues,
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  manifest.revision !== 256
  || gate11?.revision !== 11
  || gate11?.status !== "ready_for_review"
  || gate12?.status !== "blocked"
) {
  throw new Error("Expected Gate 11 rev 11 ready and Gate 12 blocked at revision 256.");
}

const exactUserWording = "可以的，继续";
const decidedAt = new Date().toISOString();
gate11.status = "approved";
gate11.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt,
  scope: "Gate 11 rev 11 Unity parity and endpoint-interlock recording",
};
gate11.deliveryState = {
  decisionState: "approved",
  gate12Advanced: true,
  shippingScenePromoted: false,
  buildInstallPhone: false,
  deviceAcceptance: "pending",
};

gate12.historicalRevisions = gate12.historicalRevisions || [];
gate12.historicalRevisions.push({
  evidenceRevision: gate12.shippingSpec?.revision ?? 1,
  stageRevision: gate12.revision,
  status: gate12.status,
  artifactIds: [...gate12.artifactIds],
  reviewArtifactIds: [...gate12.reviewArtifactIds],
  validations: [...gate12.validations],
  shippingSpec: gate12.shippingSpec,
  decision: gate12.decision,
  staleReason: gate12.staleReason,
  preservedForHistory: true,
});
gate12.revision += 1;
gate12.status = "draft";
gate12.artifactIds = [];
gate12.reviewArtifactIds = [];
gate12.validations = [];
gate12.decision = null;
delete gate12.staleReason;
gate12.shippingSpec = {
  revision: 2,
  sourceGate11Revision: 11,
  sourceGate11ApprovalExactWording: exactUserWording,
  sourceCandidateFolder:
    "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R011",
  freshCandidateFolder:
    "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002",
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  candidateDefaultActive: false,
  oldShippingModelDefaultActive: true,
  runtimeInputIntegrated: false,
  hapticsIntegrated: false,
  buildInstallPhone: false,
  deviceAcceptance: "pending",
};
gate12.readiness = {
  ready: false,
  blockers: [
    "Fresh real-scene integration, runtime/Haptic wiring, shipping views, recording, and tests are pending.",
  ],
  note: "Gate 11 is approved. Gate 12 rev 2 is in progress.",
};

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
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map(stableJson);
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = decidedAt;
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate11-rev11-approved-exact-wording-gate12-r002-in-progress";
manifest.currentState.unityStatus = "gate12-r002-real-scene-preview-in-progress";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.workbench = "persistent-seven-tab-current-gate12-unity";
manifest.currentState.diagnosis =
  "The user approved Gate 11 rev 11 with exact wording “可以的，继续”. Gate 12 rev 2 starts from the approved Gate 11 candidate; old Gate 12 evidence remains immutable history.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate11-rev11-approved-gate12-r002-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: decidedAt,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "11-unity-parity",
  approvedRevision: 11,
  reviewedArtifactIds: gate11.reviewArtifactIds,
  reviewedArtifactSha256: manifest.assets.find(
    (asset) => asset.id === "magnetic-slide-tile-unity-parity-playmode-video-r011"
  )?.sha256,
  contractSha256:
    "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  parameterSnapshot: {
    maximumTravelMeters: gate11.unityParitySpec.parityMetrics
      ? 0.018076433
      : null,
    detentCount: 30,
    detentStepDegrees: 12,
    geometryDigest: gate11.unityParitySpec.geometryDigest,
    sourceGlbSha256: gate11.unityParitySpec.sourceGlbSha256,
  },
  completedChecklist: [
    "same-camera appearance board reviewed",
    "Unity-only endpoint recording reviewed",
    "geometry and material partitions reviewed",
  ],
  interactionMode: "chat-after-unity-runtime-evidence",
  nextGate: "12-shipping",
  shippingPromoted: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  exactUserWording,
}, null, 2));
