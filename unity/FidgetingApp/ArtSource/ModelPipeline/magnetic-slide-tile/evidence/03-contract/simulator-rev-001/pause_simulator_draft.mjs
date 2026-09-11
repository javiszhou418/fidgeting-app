#!/usr/bin/env node
import crypto from "node:crypto";
import { loadManifest, saveManifest } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 152) throw new Error(`Expected revision 152, got ${manifest.revision}.`);
const now = new Date().toISOString();
const gate02 = manifest.stages.find((stage) => stage.id === "02-analysis");
const gate03 = manifest.stages.find((stage) => stage.id === "03-contract");
if (gate02.status !== "approved") throw new Error("Gate 02 approval must remain unchanged.");
gate02.analysisSpec.simulatorGeneration = {
  ...gate02.analysisSpec.simulatorGeneration,
  locked: true,
  eligible: false,
  generated: false,
  activeControls: 0,
  status: "paused-by-latest-user-instruction"
};
gate03.status = "stale";
gate03.staleReason = "Simulator paused by latest explicit user instruction; no review artifact was registered or delivered.";
gate03.readiness = {
  ready: false,
  blockers: ["Simulator implementation is paused by the latest explicit user instruction."],
  note: "Gate 02 remains approved. Gate 03 did not advance."
};
manifest.currentState.visualApproval = "gate02-rev15-approved-simulator-paused";
manifest.currentState.simulatorStatus = "paused-not-delivered";
manifest.currentState.blenderModelingStatus = "not-started";
manifest.currentState.diagnosis = "Gate 02 rev 15 remains approved. The unregistered Simulator draft is paused/internal and was not delivered. Gate 03 remains stale; Blender, Unity, build, install and phone work did not start.";
manifest.revision += 1;
manifest.updatedAt = now;
const event = {
  id: crypto.randomUUID(),
  type: "simulator-implementation-paused",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "03-contract",
  exactUserInstruction: "immediately stop the active Simulator implementation",
  gate02Status: "approved",
  gate03Status: "stale",
  simulatorArtifactRegistered: false,
  simulatorDelivered: false,
  simulatorDraftDisposition: "internal-superseded-paused",
  blenderModelingStarted: false,
  unityChanged: false,
  buildInstallPhonePush: false
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  gate02: saved.stages.find((stage) => stage.id === "02-analysis").status,
  gate03: saved.stages.find((stage) => stage.id === "03-contract").status,
  simulatorStatus: saved.currentState.simulatorStatus,
  blenderModelingStatus: saved.currentState.blenderModelingStatus
}, null, 2));
