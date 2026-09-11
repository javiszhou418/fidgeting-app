#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest
} from "../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== 91) {
  throw new Error(`Expected pipeline revision 91; found ${manifest.revision}.`);
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== 24 || stage.status !== "draft") {
  throw new Error("Gate 04 R012 state is not eligible for normalization.");
}

const now = new Date().toISOString();
const state = manifest.currentState;
state.motionCorrection = {
  ...state.motionCorrection,
  currentArchitectureRevision: 7,
  rejectedEvidenceRevisions: [8, 9, 11, 12]
};
state.blockoutCompatibility = {
  ...state.blockoutCompatibility,
  gate05Status: "stale",
  gate06Status: "stale"
};
state.geometryRevalidation = {
  ...state.geometryRevalidation,
  gate06Status: "stale",
  gate07Status: "stale"
};
state.materialRevalidation = {
  ...state.materialRevalidation,
  gate07Status: "stale",
  gate08Status: "stale"
};
state.lightingRevalidation = {
  ...state.lightingRevalidation,
  gate08Status: "stale",
  gate09Status: "stale"
};
state.environmentRevalidation = {
  ...state.environmentRevalidation,
  gate09Status: "stale",
  gate10Status: "stale"
};
state.exportReview = {
  ...state.exportReview,
  gate10Status: "stale",
  gate11Status: "stale"
};
state.unityParity = {
  ...state.unityParity,
  gate11Status: "stale",
  gate12Status: "stale"
};
state.affectedGateAssessment = {
  earliestAffectedGate: "04-architecture",
  reason:
    "R012 physical-tear visual self-rejection blocks all downstream gates.",
  geometryMaterialLightingEnvironmentExportUnityParityInvalidated: true,
  upstreamApprovedGatesUnchanged: [
    "01-intake",
    "02-analysis",
    "03-contract"
  ]
};

manifest.revision += 1;
manifest.updatedAt = now;
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r012-state-normalized",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  note:
    "Marked every Gate 05–12 current-state projection stale after R012 self-rejection.",
  approvalRequestAllowed: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText: "视觉批准待确认，未推送手机"
};
saveManifest(manifest, event);
console.log(JSON.stringify({
  pipelineRevision: manifest.revision,
  stageRevision: stage.revision,
  stageStatus: stage.status
}, null, 2));
