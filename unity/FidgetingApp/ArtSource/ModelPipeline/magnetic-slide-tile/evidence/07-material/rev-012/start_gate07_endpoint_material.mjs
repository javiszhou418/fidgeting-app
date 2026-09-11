#!/usr/bin/env node
import crypto from "node:crypto";
import path from "node:path";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 226) throw new Error(`Expected revision 226, got ${manifest.revision}.`);
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (gate06.status !== "ready_for_review" || gate06.revision !== 5) {
  throw new Error("Gate 06 rev 5 is not ready for approval.");
}
const sourceBlend = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-005/magnetic-slide-tile-geometry-r005.blend");
const sourceGlb = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-005/magnetic-slide-tile-geometry-r005-review.glb");
const exactUserWording = "继续，继续";
const now = new Date().toISOString();
const parameterSnapshot = {
  geometryRevision: 5,
  geometryDigest: gate06.geometrySpec.canonicalGeometryDigest,
  gate06BlendSha256: sha256File(sourceBlend),
  reviewedGlbSha256: sha256File(sourceGlb),
  mechanismContractSha256: gate06.geometrySpec.governingContractSha256,
  maximumTravelMm: 18.076433121019107,
  endpointInterlock: gate06.geometrySpec.endpointInterlock,
};
gate06.status = "approved";
gate06.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 06 rev 5 endpoint-interlock geometry",
};
gate06.readiness = { ready: true, blockers: [], note: `Approved in chat with exact wording “${exactUserWording}”.` };
gate06.validations.push({
  id: "chat-approval-rev5",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; GLB ${parameterSnapshot.reviewedGlbSha256}; contract ${parameterSnapshot.mechanismContractSha256}.`,
});
gate07.revision = 12;
gate07.status = "draft";
gate07.artifactIds = [];
gate07.reviewArtifactIds = [];
gate07.validations = [];
gate07.decision = null;
gate07.materialSpec = {
  revision: 12,
  sourceGate06Revision: 5,
  sourceGate06AssetId: "magnetic-slide-tile-geometry-blend-r005",
  sourceGate06Sha256: parameterSnapshot.gate06BlendSha256,
  evaluatedGeometryDigest: parameterSnapshot.geometryDigest,
  governingContractSha256: parameterSnapshot.mechanismContractSha256,
  appearanceAuthority: "approved-gate07-rev11-source-faithful-materials",
  sourceGate07Revision: 11,
  geometryChanged: false,
  motionChanged: true,
  endpointInterlockOnly: true,
  legalPoses: ["closed-0", "mid-slide-0", "max-open-0", "max-open-12", "max-open-36", "max-open-360"],
  prohibitedCurrentEvidence: ["mid-slide-rotation"],
  simulatorUsed: false,
  unityAssetChanged: false,
};
gate07.readiness = {
  ready: false,
  blockers: ["Gate 07 rev 12 material evidence is building."],
  note: "Appearance is reused unchanged; only legal endpoint-interlock poses are regenerated.",
};
delete gate07.staleReason;
for (let index = 7; index < 12; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 07 rev 12 material review is not approved.";
}
manifest.currentStageId = "07-material";
manifest.currentState.visualApproval = "gate06-rev5-approved-gate07-rev12-building";
manifest.currentState.blenderModelingStatus = "gate07-material-endpoint-interlock-revalidation";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-current-gate07-material";
manifest.currentState.diagnosis = "Gate 06 rev 5 approved. Gate 07 reuses approved appearance on unchanged geometry with endpoint-only rotation.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate06-rev5-approved-gate07-rev12-started",
  modelId: manifest.modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "06-geometry",
  approvedRevision: 5,
  reviewedArtifactId: "magnetic-slide-tile-geometry-interactive-r005",
  reviewedArtifactSha256: parameterSnapshot.reviewedGlbSha256,
  contractSha256: parameterSnapshot.mechanismContractSha256,
  parameterSnapshot,
  completedChecklist: [
    "interactive geometry reviewed",
    "fixed world pivot",
    "four underside grooves",
    "endpoint-only full rotation",
    "no visible proxy or penetration",
  ],
  interactionMode: "chat-after-interactive-workbench",
  nextGate: "07-material",
  unityChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate06: "approved", gate07: "draft", exactUserWording }, null, 2));
