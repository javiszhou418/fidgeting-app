#!/usr/bin/env node
import crypto from "node:crypto";
import path from "node:path";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 186) throw new Error(`Expected pipeline revision 186, got ${manifest.revision}.`);
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
if (gate08.status !== "ready_for_review" || gate08.lightingSpec?.revision !== 2) {
  throw new Error("Gate 08 rev 2 is not the current interactive review.");
}
const source = (filename) => path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-002",
  filename
);
const exactUserWording = "进行下一步吧";
const exactFinalGoal = "transfer to Unity with no avoidable loss and run on iPhone";
const now = new Date().toISOString();
const parameterSnapshot = {
  lightingRevision: 2,
  geometryDigest: gate08.lightingSpec.geometryDigestAfter,
  materialDigest: gate08.lightingSpec.materialDigestAfter,
  gate08BlendSha256: sha256File(source("magnetic-slide-tile-lighting-r002.blend")),
  reviewedGlbSha256: sha256File(source("magnetic-slide-tile-lighting-r002-lookdev.glb")),
  reviewedTurntableSha256: sha256File(source("magnetic-slide-tile-lighting-r002-turntable.mp4")),
  finalValidationSha256: sha256File(source("final-validation.json")),
  mechanismContractSha256: gate08.lightingSpec.governingContractSha256,
  approvedEmission: 0,
};
gate08.status = "approved";
gate08.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 08 rev 2 controlled lighting on approved Gate 07 rev 11 materials",
  finalGoal: exactFinalGoal,
};
gate08.readiness = {
  ready: true,
  blockers: [],
  note: "Approved in chat with exact wording 进行下一步吧 after interactive lighting review."
};
gate08.validations.push({
  id: "chat-approval-r002",
  status: "pass",
  evidence: `Exact user wording “${exactUserWording}”; reviewed GLB SHA-256 ${parameterSnapshot.reviewedGlbSha256}; turntable SHA-256 ${parameterSnapshot.reviewedTurntableSha256}.`
});

gate09.revision += 1;
gate09.status = "draft";
gate09.artifactIds = [];
gate09.reviewArtifactIds = [];
gate09.validations = [];
gate09.decision = null;
gate09.environmentSpec = {
  revision: 8,
  sourceLightingRevision: 2,
  sourceLightingAssetId: "magnetic-slide-tile-lighting-blend-r002",
  sourceLightingSha256: parameterSnapshot.gate08BlendSha256,
  sourceGeometryDigest: parameterSnapshot.geometryDigest,
  sourceMaterialDigest: parameterSnapshot.materialDigest,
  governingContractSha256: parameterSnapshot.mechanismContractSha256,
  sourceLightingApprovalWording: exactUserWording,
  finalGoal: exactFinalGoal,
  losslessDefinition: {
    exactDeterministic: ["geometry", "hierarchy", "pivot", "uv", "artwork-mask-hashes"],
    measuredParity: ["procedural-material-response", "lighting-response", "tone-mapped-color"],
    portableInputs: ["linear-equirectangular-exr", "reflection-probe-contract", "pbr-pack-plan", "color-management-plan"],
    blenderProceduralNodesByteIdenticalInUnity: false,
    iphonePerformanceAndAcceptanceGate: "after Gate 12 visual approval",
  },
  comparisons: {
    environments: ["neutral", "target-shipping"],
    identical: ["camera", "pose", "lights", "exposure", "geometry", "materials"],
  },
  geometryChanged: false,
  materialsChanged: false,
  lightingChanged: false,
  simulatorUsed: false,
  unityImportApplied: false,
  buildInstallDevice: false,
};
gate09.readiness = {
  ready: false,
  blockers: ["Gate 09 rev 8 portable environment evidence is in progress."],
  note: "Approved geometry, materials, lights, cameras and exposure are immutable environment inputs."
};
delete gate09.staleReason;
for (let index = 9; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 09 rev 8 environment review has not been approved.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "09-environment";
manifest.currentState.visualApproval = "gate08-rev2-approved-gate09-portable-environment-building";
manifest.currentState.blenderModelingStatus = "gate09-portable-environment-on-approved-lighting";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-gate09-environment";
manifest.currentState.diagnosis = "User approved Gate 08 rev 2 with 进行下一步吧 and locked loss-aware Unity/iPhone delivery as the final goal. Gate 09 remains Blender-only.";
manifest.currentState.finalDeliveryGoal = {
  exactUserGoal: exactFinalGoal,
  geometryHierarchyPivotUvArtwork: "exact deterministic preservation",
  proceduralShaders: "measured visual parity because Blender nodes cannot transfer one-to-one to URP",
  environmentReflectionColorManagement: "portable and documented",
  iphonePerformanceAndAcceptance: "future work after Gate 12 visual approval",
};
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-r002-chat-approved-gate09-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  exactFinalGoal,
  decisionSource: "latest-explicit-chat",
  approvedGate: "08-lighting",
  approvedRevision: 2,
  reviewedArtifactId: "magnetic-slide-tile-lighting-lookdev-r002",
  reviewedArtifactSha256: parameterSnapshot.reviewedGlbSha256,
  fallbackRecordingAssetId: "magnetic-slide-tile-lighting-turntable-r002",
  fallbackRecordingSha256: parameterSnapshot.reviewedTurntableSha256,
  sourceBlendSha256: parameterSnapshot.gate08BlendSha256,
  contractSha256: parameterSnapshot.mechanismContractSha256,
  parameterSnapshot,
  completedChecklist: [
    "orbit and zoom material-bearing GLB",
    "neutral, studio and daylight lighting modes",
    "real Blender lighting turntable",
    "Hero, left/right oblique and low-angle views",
    "Beauty, Clay, Normal, Depth and Roughness passes",
    "flat plane, raised axis, four grooves and carrier clearance",
  ],
  interactionMode: "chat-after-interactive-lighting-lookdev",
  browserEvidenceAssetId: "magnetic-slide-tile-lighting-browser-report-r002",
  deviceTimestamp: now,
  nextGate: "09-environment",
  unityChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate09: saved.stages[8].status,
  currentStageId: saved.currentStageId,
  exactUserWording,
  exactFinalGoal,
}, null, 2));

