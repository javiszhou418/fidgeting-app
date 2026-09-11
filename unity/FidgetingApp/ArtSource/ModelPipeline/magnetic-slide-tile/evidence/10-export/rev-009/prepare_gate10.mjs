#!/usr/bin/env node
import crypto from "node:crypto";
import path from "node:path";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 191) throw new Error(`Expected revision 191, got ${manifest.revision}.`);
const gate09 = manifest.stages[8];
const gate10 = manifest.stages[9];
if (gate09.status !== "ready_for_review" || gate09.environmentSpec?.revision !== 8) throw new Error("Gate 09 rev 8 is not current.");
const wording = "你给我看一下最终在 Unity 里边的呈现吧。";
const source = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-008");
const reviewedGlbSha256 = sha256File(path.join(source, "magnetic-slide-tile-environment-r008-lookdev.glb"));
const reviewedTurntableSha256 = sha256File(path.join(source, "magnetic-slide-tile-environment-comparison-r008.mp4"));
const now = new Date().toISOString();
gate09.status = "approved";
gate09.decision = {
  action: "approve",
  notes: wording,
  decidedBy: "user",
  decidedAt: now,
  scope: "Gate 09 rev 8 portable shipping environment",
  authorization: "Proceed toward Unity through Gate 10 export first; Unity import remains gated on Gate 10 approval.",
};
gate09.validations.push({
  id: "chat-approval-r008",
  status: "pass",
  evidence: `Exact user wording “${wording}”; reviewed GLB SHA-256 ${reviewedGlbSha256}; matched environment turntable SHA-256 ${reviewedTurntableSha256}.`,
});
gate10.revision += 1;
gate10.status = "draft";
gate10.artifactIds = [];
gate10.reviewArtifactIds = [];
gate10.validations = [];
gate10.decision = null;
delete gate10.staleReason;
gate10.exportSpec = {
  revision: 9,
  sourceGate09Revision: 8,
  sourceGate09ApprovalWording: wording,
  sourceBlendSha256: gate09.environmentSpec.authoritativeBlendSha256,
  geometryDigest: gate09.environmentSpec.geometryDigestAfter,
  materialDigest: gate09.environmentSpec.materialDigestAfter,
  lightDigest: gate09.environmentSpec.lightDigestAfter,
  cameraDigest: gate09.environmentSpec.cameraDigestAfter,
  environmentSha256: gate09.environmentSpec.environmentAsset.sha256,
  portabilityContractSha256: gate09.environmentSpec.portabilityContractSha256,
  governingContractSha256: gate09.environmentSpec.governingContractSha256,
  defaultPose: "closed-zero-motion",
  simulatorUsed: false,
  unityImportApplied: false,
  buildInstallDevice: false,
};
gate10.readiness = { ready: false, blockers: ["Gate 10 rev 9 export package is in progress."], note: "Unity import is not authorized before Gate 10 review approval." };
manifest.stages[10].status = "stale";
manifest.stages[10].staleReason = "Gate 10 rev 9 export awaits approval.";
manifest.stages[11].status = "rejected";
manifest.currentStageId = "10-export";
manifest.currentState.visualApproval = "gate09-rev8-approved-gate10-export-building";
manifest.currentState.blenderModelingStatus = "gate10-export-package-building";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default-gate10-only";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-gate10-export";
manifest.currentState.diagnosis = "Gate 09 rev 8 is approved. Gate 10 exports only the corrected four-track source; Unity import remains blocked.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-r008-chat-approved-gate10-started",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording: wording,
  approvedGate: "09-environment",
  approvedRevision: 8,
  reviewedArtifactId: "magnetic-slide-tile-environment-lookdev-r008",
  reviewedArtifactSha256: reviewedGlbSha256,
  fallbackRecordingAssetId: "magnetic-slide-tile-environment-turntable-r008",
  fallbackRecordingSha256: reviewedTurntableSha256,
  contractSha256: gate09.environmentSpec.governingContractSha256,
  portabilityContractSha256: gate09.environmentSpec.portabilityContractSha256,
  completedChecklist: ["interactive Neutral/Shipping lookdev", "matched closed/open/reflection pairs", "portable EXR review", "real Blender comparison turntable"],
  interactionMode: "chat-after-interactive-environment-lookdev",
  nextGate: "10-export",
  unityChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate09: saved.stages[8].status, gate10: saved.stages[9].status, wording }, null, 2));

