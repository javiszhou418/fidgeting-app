#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 237) {
  throw new Error(`Expected pipeline revision 237, got ${manifest.revision}.`);
}

const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
if (gate07?.status !== "ready_for_review" || gate07.materialSpec?.revision !== 13) {
  throw new Error("Gate 07 rev 13 is not ready for approval.");
}
if (gate07.materialSpec.sideWallArtworkPixels !== 0
  || gate07.materialSpec.undersideArtworkPixels !== 0) {
  throw new Error("Gate 07 rev 13 material partitions are not clean.");
}

const now = new Date().toISOString();
const exactUserWording = "通过";
gate07.status = "approved";
gate07.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 07 rev 13 corrected cap/side/rim/underside material review",
};
gate07.readiness = {
  ready: true,
  blockers: [],
  note: `Approved in chat with exact wording “${exactUserWording}”.`,
};
gate07.validations.push({
  id: "chat-approval-rev13",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; GLB ${gate07.materialSpec.interactiveGlbSha256}; turntable ${gate07.materialSpec.turntableSha256}.`,
});

gate08.historicalRevisions = gate08.historicalRevisions || [];
if (!gate08.historicalRevisions.some((entry) => entry.evidenceRevision === 5)) {
  gate08.historicalRevisions.push({
    evidenceRevision: 5,
    stageRevision: gate08.revision,
    status: "invalidated",
    artifactIds: [...gate08.artifactIds],
    reviewArtifactIds: [...gate08.reviewArtifactIds],
    validations: structuredClone(gate08.validations),
    lightingSpec: structuredClone(gate08.lightingSpec),
    invalidatedBy: "Gate 07 rev 13 corrected material partitions",
    preservedForHistory: true,
  });
}

gate08.revision = 9;
gate08.status = "draft";
gate08.artifactIds = [];
gate08.reviewArtifactIds = [];
gate08.validations = [];
gate08.decision = null;
gate08.lightingSpec = {
  revision: 6,
  evidenceRevision: 6,
  sourceMaterialRevision: 13,
  sourceMaterialAssetId: "magnetic-slide-tile-material-blend-r013",
  sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  baseline: "Gate 08 rev 4 portable shared HDR plus neutral-display-v1",
  expectedEnvironmentSha256: "a5b310c8c7fc17bda4110adb80e68913f1b5d623ffe01d935574813b80d1a872",
  materialPartitions: structuredClone(gate07.materialSpec.partitions),
  appearanceChanged: false,
  geometryChanged: false,
  endpointInterlockOnly: true,
  diagnosticPassPolicy: "duplicate scene and duplicate mesh datablocks; source objects remain untouched",
  legalPoses: [
    "closed-0",
    "mid-slide-0",
    "max-open-0",
    "max-open-12",
    "max-open-36",
    "max-open-360",
  ],
  simulatorUsed: false,
  unityUsed: false,
  shippingSceneModified: false,
  buildInstallPhone: false,
};
gate08.readiness = {
  ready: false,
  blockers: ["Gate 08 rev 6 evidence is building."],
  note: "Regenerating the shared-HDR lighting evidence from approved Gate 07 rev 13 partitions.",
};
delete gate08.staleReason;

for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 08 rev 6 corrected-partition lighting review is not approved.";
}

manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval = "gate07-rev13-approved-gate08-rev6-building";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate08-rev6-partition-safe-lighting-building";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate08-lighting";
manifest.currentState.diagnosis = "Gate 07 rev 13 approved. Gate 08 rev 6 regenerates shared-HDR evidence from corrected cap/side/rim/underside partitions with non-destructive diagnostic passes.";
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev13-approved-gate08-rev6-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "07-material",
  approvedRevision: 13,
  reviewedArtifactId: "magnetic-slide-tile-material-lookdev-r013",
  reviewedArtifactSha256: gate07.materialSpec.interactiveGlbSha256,
  contractSha256: gate07.materialSpec.governingContractSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  parameterSnapshot: {
    sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
    sideWallArtworkPixels: gate07.materialSpec.sideWallArtworkPixels,
    undersideArtworkPixels: gate07.materialSpec.undersideArtworkPixels,
    textureAddressMode: gate07.materialSpec.textureAddressMode,
    partitionDigests: Object.fromEntries(
      Object.entries(gate07.materialSpec.partitions)
        .map(([name, partition]) => [name, partition.partitionDigest]),
    ),
    endpointInterlockOnly: true,
  },
  completedChecklist: [
    "interactive corrected-material GLB reviewed",
    "real Blender legal-motion turntable reviewed",
    "top/side/rim/underside closeups reviewed",
    "zero side-wall artwork validation reviewed",
  ],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "08-lighting",
  shippingChanged: false,
  simulatorUsed: false,
  unityUsed: false,
  deviceWork: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate07: "approved",
  gate08: "draft",
  exactUserWording,
}, null, 2));
