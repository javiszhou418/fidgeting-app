#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 246) {
  throw new Error(`Expected pipeline revision 246, got ${manifest.revision}.`);
}
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
const gate10 = manifest.stages.find((stage) => stage.id === "10-export");
if (
  gate09?.status !== "approved"
  || gate09.decision?.notes !== "继续"
  || gate10?.status !== "ready_for_review"
  || gate10.exportSpec?.revision !== 10
) {
  throw new Error("Expected approved Gate 09 rev 9 and reviewable Gate 10 rev 10.");
}
const here = path.dirname(fileURLToPath(import.meta.url));
const sourceRejection = "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-92303f5f-923d-4ae9-b65a-6d871a070381.jpg";
const archivedRejection = path.join(here, "user-rejection-washed-out-r010.jpg");
fs.copyFileSync(sourceRejection, archivedRejection);
const exactUserWording = "almost entirely white/washed out";
const now = new Date().toISOString();

gate10.decision = {
  action: "reject",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 10 rev 10 exported GLB/reimport appearance",
};
gate10.historicalRevisions = gate10.historicalRevisions || [];
gate10.historicalRevisions.push({
  evidenceRevision: 10,
  stageRevision: gate10.revision,
  status: "rejected",
  artifactIds: [...gate10.artifactIds],
  reviewArtifactIds: [...gate10.reviewArtifactIds],
  validations: structuredClone(gate10.validations),
  exportSpec: structuredClone(gate10.exportSpec),
  decision: structuredClone(gate10.decision),
  rejectionEvidence: {
    path: "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-011/user-rejection-washed-out-r010.jpg",
    sha256: sha256File(archivedRejection),
  },
  invalidatedBy: "User rejected the rev 10 white/washed-out real-GLB/reimport presentation.",
  preservedForHistory: true,
});

gate10.revision = 12;
gate10.status = "draft";
gate10.artifactIds = [];
gate10.reviewArtifactIds = [];
gate10.validations = [];
gate10.decision = null;
gate10.exportSpec = {
  revision: 11,
  evidenceRevision: 11,
  sourceGate09Revision: 9,
  sourceGate09ApprovalWording: "继续",
  sourceBlendAssetId: "magnetic-slide-tile-environment-blend-r009",
  sourceBlendSha256: gate10.historicalRevisions.at(-1).exportSpec.sourceBlendSha256,
  sourceGate10Revision: 10,
  rejectedGlbSha256: gate10.historicalRevisions.at(-1).exportSpec.glbSha256,
  geometryDigest: gate10.historicalRevisions.at(-1).exportSpec.geometryDigest,
  materialSourceSha256: gate10.historicalRevisions.at(-1).exportSpec.materialDigest,
  materialStateDigest: gate10.historicalRevisions.at(-1).exportSpec.materialStateDigest,
  uvDigest: gate10.historicalRevisions.at(-1).exportSpec.uvDigest,
  environmentSha256: gate10.historicalRevisions.at(-1).exportSpec.environmentSha256,
  portabilityContractSha256: gate10.historicalRevisions.at(-1).exportSpec.portabilityContractSha256,
  governingContractSha256: gate10.historicalRevisions.at(-1).exportSpec.governingContractSha256,
  rejectionExactWording: exactUserWording,
  rejectionEvidenceSha256: sha256File(archivedRejection),
  correctionScope: "portable GLB PBR transport and neutral review calibration only",
  geometryChanged: false,
  hierarchyChanged: false,
  mechanismChanged: false,
  simulatorUsed: false,
  unityImportApplied: false,
  shippingSceneModified: false,
  buildInstallDevice: false,
};
gate10.readiness = {
  ready: false,
  blockers: ["Gate 10 rev 11 portable GLB appearance correction is building."],
  note: "Diagnosing GLB material transport and preview calibration without changing approved geometry or mechanism.",
};
for (const downstream of manifest.stages.slice(10)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 10 rev 11 correction awaits review.";
}
manifest.currentStageId = "10-export";
manifest.currentState.visualApproval = "gate10-rev10-rejected-rev11-correcting";
manifest.currentState.blenderModelingStatus = "gate10-rev11-portable-glb-correcting";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.diagnosis = "Gate 10 rev 10 was rejected as white/washed out. Rev 11 isolates GLB PBR transport from Blender reimport and Three.js viewer calibration.";
manifest.issues = manifest.issues.filter((issue) => issue.id !== "slider-gate10-r010-review");
manifest.issues.push({
  id: "slider-gate10-r011-washout-correction",
  stageId: "10-export",
  assetId: "magnetic-slide-tile-export-glb-r010",
  severity: "blocker",
  note: "Rev 10 was rejected as white/washed out. Correct portable materials and neutral review calibration before approval.",
  status: "correcting",
});
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev10-rejected-rev11-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  rejectedGate: "10-export",
  rejectedRevision: 10,
  rejectedArtifactId: "magnetic-slide-tile-export-glb-r010",
  rejectedArtifactSha256: gate10.exportSpec.rejectedGlbSha256,
  rejectionEvidencePath: path.relative(process.cwd(), archivedRejection).split(path.sep).join("/"),
  rejectionEvidenceSha256: sha256File(archivedRejection),
  preservedGeometryDigest: gate10.exportSpec.geometryDigest,
  preservedMaterialStateDigest: gate10.exportSpec.materialStateDigest,
  preservedUvDigest: gate10.exportSpec.uvDigest,
  nextRevision: 11,
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate10Rev10: "rejected-preserved",
  gate10Rev11: "draft",
  exactUserWording,
  rejectionEvidenceSha256: sha256File(archivedRejection),
}, null, 2));
