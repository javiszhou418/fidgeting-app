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
if (manifest.revision !== 181) throw new Error(`Expected pipeline revision 181, got ${manifest.revision}.`);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
if (gate07.status !== "ready_for_review" || gate07.materialSpec?.revision !== 11) {
  throw new Error("Gate 07 rev 11 is not the current interactive review.");
}
const sourceBlend = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-011/magnetic-slide-tile-material-r011.blend"
);
const sourceGlb = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-011/magnetic-slide-tile-material-r011-lookdev.glb"
);
const sourceTurntable = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-011/magnetic-slide-tile-material-r011-turntable.mp4"
);
const exactUserWording = "继续";
const now = new Date().toISOString();
const parameterSnapshot = {
  materialRevision: 11,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  gate07BlendSha256: sha256File(sourceBlend),
  reviewedGlbSha256: sha256File(sourceGlb),
  reviewedTurntableSha256: sha256File(sourceTurntable),
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  upperMaskSha256: gate07.materialSpec.textureLineage.upper.sha256,
  lowerMaskSha256: gate07.materialSpec.textureLineage.lower.sha256,
  borderMaskSha256: gate07.materialSpec.textureLineage.border.sha256,
  emission: 0
};
gate07.status = "approved";
gate07.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 07 rev 11 materials on approved Gate 06 rev 4 geometry"
};
gate07.readiness = {
  ready: true,
  blockers: [],
  note: "Approved in chat with exact wording 继续 after interactive material lookdev."
};
gate07.validations.push({
  id: "chat-approval-r011",
  status: "pass",
  evidence: `Exact user wording “${exactUserWording}”; reviewed GLB SHA-256 ${parameterSnapshot.reviewedGlbSha256}; turntable SHA-256 ${parameterSnapshot.reviewedTurntableSha256}.`
});

gate08.revision += 1;
gate08.status = "draft";
gate08.artifactIds = [];
gate08.reviewArtifactIds = [];
gate08.validations = [];
gate08.decision = null;
gate08.lightingSpec = {
  revision: 2,
  sourceMaterialRevision: 11,
  sourceMaterialAssetId: "magnetic-slide-tile-material-blend-r011",
  sourceMaterialSha256: parameterSnapshot.gate07BlendSha256,
  sourceGeometryDigest: parameterSnapshot.geometryDigest,
  governingContractSha256: parameterSnapshot.mechanismContractSha256,
  sourceMaterialApprovalWording: exactUserWording,
  requiredViews: ["hero", "left-oblique", "right-oblique", "low"],
  requiredPasses: ["beauty", "clay", "normal", "depth", "roughness"],
  lightingModes: ["neutral", "studio", "daylight"],
  hdri: null,
  geometryChanged: false,
  materialsChanged: false,
  simulatorUsed: false,
  unityAssetChanged: false
};
gate08.readiness = {
  ready: false,
  blockers: ["Gate 08 rev 2 lighting evidence is in progress."],
  note: "Approved geometry and materials are immutable lighting inputs."
};
delete gate08.staleReason;
for (let index = 8; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 08 rev 2 lighting review has not been approved.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval = "gate07-rev11-approved-gate08-lighting-building";
manifest.currentState.blenderModelingStatus = "gate08-lighting-on-approved-materials";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-gate08-lighting";
manifest.currentState.diagnosis = "User approved Gate 07 rev 11 with 继续. Gate 08 now lights the unchanged geometry and materials.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-r011-chat-approved-gate08-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "07-material",
  approvedRevision: 11,
  reviewedArtifactId: "magnetic-slide-tile-material-lookdev-r011",
  reviewedArtifactSha256: parameterSnapshot.reviewedGlbSha256,
  fallbackRecordingAssetId: "magnetic-slide-tile-material-turntable-r011",
  fallbackRecordingSha256: parameterSnapshot.reviewedTurntableSha256,
  sourceBlendSha256: parameterSnapshot.gate07BlendSha256,
  contractSha256: parameterSnapshot.mechanismContractSha256,
  parameterSnapshot,
  completedChecklist: [
    "orbit and zoom material-bearing GLB",
    "environment and exposure toggles",
    "real Blender material turntable",
    "source comparison",
    "upper and lower artwork distinction",
    "blood-red crystal, black perimeter, silver rim and dark side response"
  ],
  interactionMode: "chat-after-interactive-lookdev",
  browserEvidenceAssetId: "magnetic-slide-tile-material-browser-report-r011",
  deviceTimestamp: now,
  nextGate: "08-lighting",
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  gate08: saved.stages[7].status,
  currentStageId: saved.currentStageId,
  exactUserWording
}, null, 2));

