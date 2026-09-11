#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 234) throw new Error(`Expected pipeline revision 234, got ${manifest.revision}.`);
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const rejectionPath =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-013/user-rejection-side-artwork-wrap.png";
const rejectionAbsolute = resolveRepoPath(rejectionPath);
if (gate06.status !== "approved" || gate07.status !== "approved" || gate07.revision !== 12) {
  throw new Error("Expected approved Gate 06 rev 5 and Gate 07 rev 12.");
}
if (!fs.existsSync(rejectionAbsolute)) throw new Error("Missing archived user rejection image.");
const now = new Date().toISOString();
gate07.historicalRevisions ??= [];
gate07.historicalRevisions.push({
  revision: 12,
  status: "rejected-superseded",
  artifactIds: [...gate07.artifactIds],
  reviewArtifactIds: [...gate07.reviewArtifactIds],
  materialSpec: gate07.materialSpec,
  decision: gate07.decision,
  rejectedAt: now,
  exactUserWording: "边缘没有图案填充",
  reason: "Artwork was visibly stretched onto upper and lower vertical side walls.",
});
manifest.assets.push({
  id: `${modelId}-material-side-wrap-rejection-r013`,
  stageId: "07-material",
  slot: "user-rejection",
  path: rejectionPath,
  sha256: sha256File(rejectionAbsolute),
  exists: true,
  sizeBytes: fs.statSync(rejectionAbsolute).size,
  role: "user-input",
  producer: {
    name: "Cursor chat attachment",
    version: "2026-08-29",
    recipe: "Archived byte-for-byte from the user-provided screenshot.",
  },
  provenance: {
    origin: "user-provided",
    contentClass: "material-boundary-rejection",
    assertedBy: "user",
    exactUserWording: "边缘没有图案填充",
    interpretation: "Both upper and lower vertical side walls must contain zero artwork pixels. Motif and blood-red crystal are top-cap only.",
    geometryChangeAuthorized: false,
    mechanismEvidenceContractSha256: gate07.materialSpec.governingContractSha256,
  },
  sourceAssetIds: [],
  sourceClaimIds: [],
});
gate07.revision = 13;
gate07.status = "draft";
gate07.artifactIds = [`${modelId}-material-side-wrap-rejection-r013`];
gate07.reviewArtifactIds = [];
gate07.validations = [];
gate07.decision = null;
gate07.materialSpec = {
  revision: 13,
  sourceGate06Revision: 5,
  sourceGate06AssetId: "magnetic-slide-tile-geometry-blend-r005",
  sourceGate06Sha256: gate07.historicalRevisions.at(-1).materialSpec.sourceGate06Sha256,
  sourceGate07Revision: 12,
  sourceGate07BlendAssetId: "magnetic-slide-tile-material-blend-r012",
  sourceGate07BlendSha256: gate07.historicalRevisions.at(-1).materialSpec.authoritativeBlendSha256,
  evaluatedGeometryDigest: gate07.historicalRevisions.at(-1).materialSpec.evaluatedGeometryDigest,
  governingContractSha256: gate07.historicalRevisions.at(-1).materialSpec.governingContractSha256,
  appearanceAuthority: "approved-rev12-top-cap-appearance-with-user-rejected-side-wrap-removed",
  rootCause: "Artwork materials had repeating image nodes and no export-stable cap-only partition contract. Import-time renderer remapping could place the artwork shader on side primitives.",
  zoning: {
    topCap: "independent upper/lower blood-red crystal artwork",
    sideWall: "solid dark exterior; exact artwork coverage 0",
    rimBevel: "polished bright silver",
    underside: "approved exterior or neutral technical zone",
    internals: "separate technical materials",
  },
  textureAddressMode: "CLIP",
  geometryChanged: false,
  mechanismChanged: false,
  endpointInterlockOnly: true,
  unityUsed: false,
  simulatorUsed: false,
};
gate07.readiness = {
  ready: false,
  blockers: ["Gate 07 rev 13 corrected cap/side/rim evidence is building."],
  note: "User rejected side-wall artwork wrap. Geometry and mechanism remain approved and unchanged.",
};
delete gate07.staleReason;
for (let index = 7; index < 12; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 07 rev 13 material-boundary correction is not approved.";
  manifest.stages[index].decision = null;
}
manifest.currentStageId = "07-material";
manifest.currentState.visualApproval = "gate07-rev13-side-partition-fix-building";
manifest.currentState.blenderModelingStatus = "gate07-rev13-material-boundary-correction";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-current-gate07-material";
manifest.currentState.diagnosis = "User rejected artwork on vertical side walls. Gate 07 rev 13 introduces deterministic cap-only artwork and solid side/rim partitions without geometry changes.";
manifest.issues = manifest.issues.filter((issue) => issue.stageId !== "08-lighting");
manifest.issues.push({
  id: "slider-gate07-r013-side-partition-review",
  stageId: "07-material",
  assetId: `${modelId}-material-side-wrap-rejection-r013`,
  severity: "blocker",
  note: "Correct cap/side/rim partition and obtain Gate 07 visual approval before any downstream work.",
});
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev12-rejected-side-wrap-gate07-rev13-started",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "07-material",
  rejectedRevision: 12,
  newRevision: 13,
  exactUserWording: "边缘没有图案填充",
  rejectionAssetId: `${modelId}-material-side-wrap-rejection-r013`,
  rejectionAssetSha256: sha256File(rejectionAbsolute),
  interpretation: "Artwork and blood-red crystal are top-cap only; side walls are solid dark; rim strips are polished silver.",
  geometryChanged: false,
  mechanismChanged: false,
  downstream: "08-12 stale",
  deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate07: "draft", downstream: "stale", rejectionSha256: sha256File(rejectionAbsolute) }, null, 2));
