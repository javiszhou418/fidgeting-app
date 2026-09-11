#!/usr/bin/env node
import crypto from "node:crypto";
import { loadManifest, saveManifest } from "../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision === 155 && manifest.currentState?.workflowPhases?.length === 3) {
  console.log(JSON.stringify({
    revision: manifest.revision,
    approved: `${manifest.stages.filter((stage) => stage.status === "approved").length}/12`,
    gate02: manifest.stages.find((stage) => stage.id === "02-analysis").status,
    gate03: manifest.stages.find((stage) => stage.id === "03-contract").status,
    requiredPhysicalDimensions: manifest.currentState.requiredPhysicalDimensions
  }, null, 2));
  process.exit(0);
}
if (manifest.revision === 154 && manifest.currentState?.workflowPhases?.length === 3) {
  const now = new Date().toISOString();
  manifest.currentStageId = "03-contract";
  manifest.revision += 1;
  manifest.updatedAt = now;
  const saved = saveManifest(manifest, {
    id: crypto.randomUUID(),
    type: "workflow-current-gate-corrected",
    modelId: manifest.model.id,
    manifestRevision: manifest.revision,
    timestamp: now,
    currentStageId: "03-contract",
    reason: "Gate 02 is approved and Gate 03 is the blocked next gate."
  });
  console.log(JSON.stringify({
    revision: saved.revision,
    approved: `${saved.stages.filter((stage) => stage.status === "approved").length}/12`,
    gate02: saved.stages.find((stage) => stage.id === "02-analysis").status,
    gate03: saved.stages.find((stage) => stage.id === "03-contract").status,
    requiredPhysicalDimensions: saved.currentState.requiredPhysicalDimensions
  }, null, 2));
  process.exit(0);
}
if (manifest.revision !== 153) throw new Error(`Expected revision 153, got ${manifest.revision}.`);
const now = new Date().toISOString();
const gate02 = manifest.stages.find((stage) => stage.id === "02-analysis");
const gate03 = manifest.stages.find((stage) => stage.id === "03-contract");
if (gate02.status !== "approved") throw new Error("Gate 02 approval must remain unchanged.");

const requiredPhysicalDimensions = [
  "overallLength",
  "overallWidth",
  "totalThickness",
  "upperThickness",
  "lowerThickness",
  "closedGap",
  "railSpacing",
  "railWidth",
  "axisDiameter",
  "upperStepHeight",
  "lowerStepHeight",
  "clearance",
  "manufacturingAllowance",
  "tolerance",
  "maxTravelMm"
];

gate02.analysisSpec.phase = "interaction-form-approved";
gate02.analysisSpec.approvalSpec.approvalEffect = "approves-gate02-interaction-form-for-gate03-dimension-contract";
gate02.analysisSpec.simulatorGeneration = {
  locked: true,
  eligible: false,
  generated: false,
  activeControls: 0,
  status: "internal-superseded-not-current",
  note: "A standalone Simulator is not a pre-Blender gate."
};

if (gate03.decision) {
  gate03.supersededDecision = {
    ...gate03.decision,
    supersededAt: now,
    supersededReason: "Replaced by the approved Gate 02 mechanism and the real-dimensions contract blocker."
  };
  delete gate03.decision;
}
gate03.status = "blocked";
gate03.staleReason = null;
gate03.blockedReason = "Required real physical dimensions have not been supplied.";
gate03.requiredPhysicalDimensions = requiredPhysicalDimensions;
gate03.readiness = {
  ready: false,
  blockers: requiredPhysicalDimensions.map((field) => `Missing user measurement: ${field}.`),
  note: "Gate 03 is next. Blender must not start until the real dimensions and refreshed modeling contract are complete."
};

manifest.currentState.visualApproval = "gate02-rev15-approved-gate03-dimensions-blocked";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.blenderModelingStatus = "not-started-blocked-by-real-dimensions";
manifest.currentState.workflowPhases = [
  { id: "interaction-form", gates: [1, 2, 3, 4] },
  { id: "blender-modeling-textures", gates: [5, 6, 7, 8, 9, 10] },
  { id: "unity-scene-rendering", gates: [11, 12] }
];
manifest.currentState.requiredPhysicalDimensions = requiredPhysicalDimensions;
manifest.currentState.diagnosis = "Gate 02 rev 15 interaction-form CAD is approved. Gate 03 is blocked on real physical dimensions. The next active flow is modeling contract, then Blender modeling/textures, then Unity scene/rendering; no standalone Simulator prerequisite exists.";
manifest.revision += 1;
manifest.updatedAt = now;

const event = {
  id: crypto.randomUUID(),
  type: "workflow-sequence-superseded",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording: "确定交互形式后，是开始建模+贴图的流程，然后 Unity+场景+渲染.",
  canonicalGateCount: 12,
  phaseMapping: manifest.currentState.workflowPhases,
  standaloneSimulatorBeforeBlenderRequired: false,
  simulatorDraftDisposition: "internal-superseded-not-current",
  gate02Status: "approved",
  gate03Status: "blocked",
  blocker: "real-physical-dimensions",
  requiredPhysicalDimensions,
  blenderStarted: false,
  unityChanged: false,
  oldShippingModelDefault: true
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  approved: `${saved.stages.filter((stage) => stage.status === "approved").length}/12`,
  gate02: saved.stages.find((stage) => stage.id === "02-analysis").status,
  gate03: saved.stages.find((stage) => stage.id === "03-contract").status,
  requiredPhysicalDimensions: saved.currentState.requiredPhysicalDimensions
}, null, 2));
