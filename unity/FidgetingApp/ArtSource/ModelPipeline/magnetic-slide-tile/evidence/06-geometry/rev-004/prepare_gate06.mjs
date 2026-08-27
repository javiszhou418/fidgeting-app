#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 174) throw new Error(`Expected pipeline revision 174, got ${manifest.revision}.`);
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
if (gate05.status !== "ready_for_review" || gate05.blockoutSpec?.revision !== 6) {
  throw new Error("Gate 05 rev 6 is not the current review.");
}
const contractHash = gate05.blockoutSpec.governingContractSha256;
const sourceBlend = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-006/magnetic-slide-tile-blockout-r006.blend"
);
const sourceGlb = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-006/magnetic-slide-tile-blockout-r006-review.glb"
);
const now = new Date().toISOString();
const exactUserWording = "可以的";
const parameterSnapshot = {
  exteriorMm: [50, 31, 12],
  dimensionState: "user-authorized-provisional-not-production-measured",
  bottomTopPlaneZMm: 5.875,
  bottomTopPlaneToleranceMm: 0.001,
  axisBossExposedProtrusionMm: 0.2,
  carrierClearanceBelowPlaneMm: gate05.blockoutSpec.carrierPacking.clearanceBelowPlaneMm,
  grooveCount: 4,
  grooveWidthRangeMm: [1.8, 3],
  ballCandidateRangeMm: [2, 3],
  maxTravelMm: gate05.blockoutSpec.dimensionsMm.maxTravel,
  detentCount: 30,
  detentStepDegrees: 12,
  transform: gate05.blockoutSpec.topTransform,
  mechanismContractSha256: contractHash,
  gate05BlendSha256: sha256File(sourceBlend),
  reviewedGlbSha256: sha256File(sourceGlb)
};

gate05.status = "approved";
gate05.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 05 rev 6 flat-plane white-model structure and kinematics"
};
gate05.readiness = {
  ready: true,
  blockers: [],
  note: "Approved in chat with exact wording 可以的 after interactive rev 6 GLB review."
};
gate05.validations.push({
  id: "chat-approval-rev6",
  status: "pass",
  evidence: `Exact user wording “${exactUserWording}”; reviewed GLB SHA-256 ${parameterSnapshot.reviewedGlbSha256}; source blend SHA-256 ${parameterSnapshot.gate05BlendSha256}.`
});

gate06.revision += 1;
gate06.status = "draft";
gate06.artifactIds = [];
gate06.reviewArtifactIds = [];
gate06.validations = [];
gate06.decision = null;
gate06.geometrySpec = {
  revision: 4,
  governingContractSha256: contractHash,
  gate05SourceAssetId: "magnetic-slide-tile-blockout-blend-r006",
  gate05SourceSha256: parameterSnapshot.gate05BlendSha256,
  parameterSnapshot,
  requiredViews: [
    "front", "back", "top", "bottom", "left", "right", "workbench",
    "dimensions", "pivot", "exploded", "underside-four-groove",
    "flat-plane-raised-axis", "section-aa", "tangency-step",
    "closed", "max-open", "detent-12", "detent-36"
  ],
  materialScope: "white-clay-only",
  unknownEngineering: [
    "hidden groove cross-section",
    "ball material and exact count",
    "spring layout",
    "contact preload",
    "operating clearance",
    "manufacturing allowance",
    "manufacturing tolerance"
  ],
  unityAssetChanged: false
};
gate06.readiness = {
  ready: false,
  blockers: ["Gate 06 evidence build and validation are in progress."],
  note: "Gate 05 source is approved and immutable."
};
delete gate06.staleReason;
for (let index = 6; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 06 rev 4 geometry review has not been approved.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "06-geometry";
manifest.currentState.visualApproval = "gate05-rev6-approved-gate06-building";
manifest.currentState.blenderModelingStatus = "gate06-geometry-evidence-building-from-approved-rev6";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-gate06";
manifest.currentState.diagnosis = "User approved Gate 05 rev 6 with 可以的. Gate 06 now validates the same immutable geometry across structural views.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-rev6-chat-approved-gate06-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "05-blockout",
  approvedRevision: 6,
  reviewedArtifactId: "magnetic-slide-tile-blockout-interactive-r006",
  reviewedArtifactSha256: parameterSnapshot.reviewedGlbSha256,
  sourceBlendSha256: parameterSnapshot.gate05BlendSha256,
  contractSha256: contractHash,
  parameterSnapshot,
  completedChecklist: [
    "continuous flat BottomExterior top plane",
    "no recess or cavity",
    "separate raised FixedAxisBoss",
    "carrier hidden below plane",
    "four MovingTop underside grooves",
    "compound slide and rotation",
    "finite endpoints and minimum-overlap containment",
    "interactive GLB reviewed"
  ],
  interactionMode: "chat-after-interactive-workbench",
  browserEvidenceAssetId: "magnetic-slide-tile-workspace-browser-report-r006",
  deviceTimestamp: now,
  nextGate: "06-geometry",
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  gate06: saved.stages[5].status,
  currentStageId: saved.currentStageId,
  exactUserWording
}, null, 2));

