#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 230) throw new Error(`Expected revision 230, got ${manifest.revision}.`);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
if (gate07.status !== "ready_for_review" || gate07.materialSpec?.revision !== 12) {
  throw new Error("Gate 07 rev 12 is not ready for approval.");
}
const now = new Date().toISOString();
const exactUserWording = "继续";
gate07.status = "approved";
gate07.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 07 rev 12 endpoint-interlock material review",
};
gate07.readiness = { ready: true, blockers: [], note: `Approved in chat with exact wording “${exactUserWording}”.` };
gate07.validations.push({
  id: "chat-approval-rev12",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; GLB ${gate07.materialSpec.interactiveGlbSha256}; turntable ${gate07.materialSpec.turntableSha256}.`,
});
gate08.historicalRevisions = gate08.historicalRevisions || [];
if (!gate08.historicalRevisions.some((entry) => entry.evidenceRevision === 4)) {
  gate08.historicalRevisions.push({
    evidenceRevision: 4,
    status: gate08.status,
    artifactIds: [...gate08.artifactIds],
    reviewArtifactIds: [...gate08.reviewArtifactIds],
    validations: structuredClone(gate08.validations),
    lightingSpec: structuredClone(gate08.lightingSpec),
    preservedForHistory: true,
  });
}
gate08.revision = 8;
gate08.status = "draft";
gate08.artifactIds = [];
gate08.reviewArtifactIds = [];
gate08.validations = [];
gate08.decision = null;
gate08.lightingSpec = {
  revision: 5,
  sourceMaterialRevision: 12,
  sourceMaterialAssetId: "magnetic-slide-tile-material-blend-r012",
  sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  baseline: "Gate 08 rev 4 single shared HDR plus neutral-display-v1",
  baselineEnvironmentSha256: "e0a2d012a06e599f00bfbdd152351a726df186e212c1bad394284db1de1c3d90",
  appearanceChanged: false,
  geometryChanged: false,
  endpointInterlockOnly: true,
  legalPoses: ["closed-0", "mid-slide-0", "max-open-0", "max-open-12", "max-open-36", "max-open-360"],
  simulatorUsed: false,
  shippingSceneModified: false,
  buildInstallPhone: false,
};
gate08.readiness = { ready: false, blockers: ["Gate 08 rev 5 evidence is building."], note: "Portable rev 4 lighting baseline is being regenerated on approved rev 12 materials." };
delete gate08.staleReason;
for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 08 rev 5 endpoint-safe lighting review is not approved.";
}
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval = "gate07-rev12-approved-gate08-rev5-building";
manifest.currentState.blenderModelingStatus = "gate08-portable-shared-hdr-endpoint-lighting-building";
manifest.currentState.unityStatus = "isolated-lighting-validation-only-old-shipping-default";
manifest.currentState.workbench = "persistent-seven-tab-current-gate08-lighting";
manifest.currentState.diagnosis = "Gate 07 rev 12 approved. Gate 08 rev 5 regenerates the portable shared-HDR baseline using endpoint-only legal motion.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev12-approved-gate08-rev5-started",
  modelId: manifest.modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "07-material",
  approvedRevision: 12,
  reviewedArtifactId: "magnetic-slide-tile-material-lookdev-r012",
  reviewedArtifactSha256: gate07.materialSpec.interactiveGlbSha256,
  contractSha256: gate07.materialSpec.governingContractSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  parameterSnapshot: {
    sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
    upperTextureSha256: gate07.materialSpec.generatedTextures.upper.albedoSha256,
    lowerTextureSha256: gate07.materialSpec.generatedTextures.lower.albedoSha256,
    endpointInterlockOnly: true,
  },
  completedChecklist: ["interactive material GLB reviewed", "real Blender turntable reviewed", "source comparison reviewed", "endpoint-only legal poses reviewed"],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "08-lighting",
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate07: "approved", gate08: "draft", exactUserWording }, null, 2));
