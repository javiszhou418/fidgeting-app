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
if (manifest.revision !== 177) throw new Error(`Expected pipeline revision 177, got ${manifest.revision}.`);
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (gate06.status !== "ready_for_review" || gate06.geometrySpec?.revision !== 4) {
  throw new Error("Gate 06 rev 4 is not the current review.");
}
const sourceBlend = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-004/magnetic-slide-tile-geometry-r004.blend"
);
const sourceGlb = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-004/magnetic-slide-tile-geometry-r004-review.glb"
);
const exactUserWording = "那你继续呗";
const now = new Date().toISOString();
const parameterSnapshot = {
  geometryRevision: 4,
  geometryDigest: gate06.geometrySpec.canonicalGeometryDigest,
  gate06BlendSha256: sha256File(sourceBlend),
  reviewedGlbSha256: sha256File(sourceGlb),
  mechanismContractSha256: gate06.geometrySpec.governingContractSha256,
  boundsMm: gate06.geometrySpec.exactBoundsMm,
  topPlaneZMm: gate06.geometrySpec.topPlane.minimumZMm,
  axisBossProtrusionMm: 0.2,
  grooveCount: 4,
  maxTravelMm: gate06.geometrySpec.parameterSnapshot.maxTravelMm
};
gate06.status = "approved";
gate06.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 06 rev 4 same-source geometry"
};
gate06.readiness = {
  ready: true,
  blockers: [],
  note: "Approved in chat with exact wording 那你继续呗 after interactive Gate 06 review."
};
gate06.validations.push({
  id: "chat-approval-rev4",
  status: "pass",
  evidence: `Exact user wording “${exactUserWording}”; reviewed GLB SHA-256 ${parameterSnapshot.reviewedGlbSha256}; source blend SHA-256 ${parameterSnapshot.gate06BlendSha256}.`
});

gate07.revision += 1;
gate07.status = "draft";
gate07.artifactIds = [];
gate07.reviewArtifactIds = [];
gate07.validations = [];
gate07.decision = null;
gate07.materialSpec = {
  revision: 11,
  sourceGate06Revision: 4,
  sourceGate06AssetId: "magnetic-slide-tile-geometry-blend-r004",
  sourceGate06Sha256: parameterSnapshot.gate06BlendSha256,
  evaluatedGeometryDigest: parameterSnapshot.geometryDigest,
  governingContractSha256: parameterSnapshot.mechanismContractSha256,
  appearanceAuthority: "original-user-blood-red-product-imagery-only",
  reuseAssets: [
    { id: "magnetic-slide-tile-artwork-upper-mask-r007", sha256: "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36", purpose: "clean upper motif mask" },
    { id: "magnetic-slide-tile-material-rev10-lower-mask-r010", sha256: "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2", purpose: "distinct lower direct/reconstructed artwork" },
    { id: "magnetic-slide-tile-artwork-border-mask-r007", sha256: "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc", purpose: "full black top perimeter" },
    { id: "magnetic-slide-tile-material-rev10-recipe-r010", purpose: "blood-red crystal, polished silver and dark-side recipe" },
    { id: "magnetic-slide-tile-material-rev10-lower-provenance-r010", purpose: "direct/reconstructed lower provenance" }
  ],
  values: {
    silver: { baseColorLinear: [0.78, 0.77, 0.74, 1], metallic: 1, roughness: 0.075, anisotropy: 0.16, emission: 0 },
    crystal: {
      deepBloodRedLinear: [0.18, 0.003, 0.008, 1],
      roughnessMinMax: [0.022, 0.11],
      ior: 1.52,
      coatWeight: 0.48,
      coatRoughness: 0.035,
      transmissionMinMax: [0.05, 0.3],
      thinFilmIor: 1.38,
      thinFilmThicknessNm: [365, 455],
      microflakeScale: 85,
      granularVariationScale: 28,
      emission: 0
    },
    darkSide: { baseColorLinear: [0.018, 0.02, 0.024, 1], metallic: 0.24, roughness: 0.18, coatWeight: 0.55 },
    blackPerimeter: { borderMaskWidthPx: 64, outerInsetPx: 0 },
    internalTechnical: "neutral-inspection-only-not-material-claim"
  },
  independentArtworkSlots: ["Artwork_Upper", "Artwork_Lower"],
  staleGeometryReuse: false,
  unityApproximationReuse: false,
  simulatorUsed: false,
  unityAssetChanged: false
};
gate07.readiness = {
  ready: false,
  blockers: ["Gate 07 rev 11 material evidence and interactive lookdev are in progress."],
  note: "Approved Gate 06 geometry and source-backed appearance lineage are immutable inputs."
};
delete gate07.staleReason;
for (let index = 7; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 07 rev 11 material review has not been approved.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "07-material";
manifest.currentState.visualApproval = "gate06-rev4-approved-gate07-material-building";
manifest.currentState.blenderModelingStatus = "gate07-material-rebuild-on-approved-gate06-geometry";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-gate07-material";
manifest.currentState.diagnosis = "User approved Gate 06 rev 4 with 那你继续呗. Gate 07 now reapplies source-backed appearance lineage to the corrected geometry.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate06-rev4-chat-approved-gate07-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "06-geometry",
  approvedRevision: 4,
  reviewedArtifactId: "magnetic-slide-tile-geometry-interactive-r004",
  reviewedArtifactSha256: parameterSnapshot.reviewedGlbSha256,
  sourceBlendSha256: parameterSnapshot.gate06BlendSha256,
  contractSha256: parameterSnapshot.mechanismContractSha256,
  parameterSnapshot,
  completedChecklist: [
    "same geometry digest across structural views",
    "exact provisional bounds and thickness stack",
    "flat BottomExterior top and raised axis boss",
    "four grooves and follower alignment",
    "finite endpoints and dense containment",
    "interactive Gate 06 GLB reviewed"
  ],
  interactionMode: "chat-after-interactive-workbench",
  browserEvidenceAssetId: "magnetic-slide-tile-geometry-browser-report-r004",
  deviceTimestamp: now,
  nextGate: "07-material",
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate06: saved.stages[5].status,
  gate07: saved.stages[6].status,
  currentStageId: saved.currentStageId,
  exactUserWording
}, null, 2));

