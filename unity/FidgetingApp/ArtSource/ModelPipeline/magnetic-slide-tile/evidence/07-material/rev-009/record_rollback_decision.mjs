#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const userQuote = "退回，我们要优先保证模型的质量";
const manifest = loadManifest(modelId);
if (manifest.revision !== 104) {
  throw new Error(`Expected manifest revision 104, got ${manifest.revision}.`);
}
const stage = manifest.stages[6];
if (stage.status !== "ready_for_review" || stage.authorityAuditSpec?.revision !== 8) {
  throw new Error("Gate 07 rev 8 authority audit is not the active review.");
}

stage.priorAuditDecision = {
  action: "approve-rollback",
  userQuote,
  decidedAt: new Date().toISOString(),
  approvedScope: "Return to Gate 07 and rebuild Blender material from original product references.",
  excludedScope: "No geometry, Unity, Gate 08+, build, install or phone work.",
};
stage.status = "draft";
stage.decision = null;
stage.revision += 1;
stage.artifactIds = [];
stage.reviewArtifactIds = [];
stage.validations = [];
stage.authorityAuditSpec.reviewState = "rollback-approved";
stage.authorityAuditSpec.userQuote = userQuote;
stage.authorityAuditSpec.correctedMaterialCreated = false;
manifest.revision += 1;
manifest.updatedAt = stage.priorAuditDecision.decidedAt;
manifest.currentState.visualApproval = "gate07-rev9-original-authority-material-in-progress";
manifest.currentState.diagnosis =
  "The user explicitly approved rollback with the exact quote “退回，我们要优先保证模型的质量”. Gate 07 is rebuilding Blender material from original product references. Gates 08–11 remain stale; Gate 12 remains blocked; the old shipping model remains default.";

const event = {
  id: crypto.randomUUID(),
  type: "gate07-original-authority-rollback-approved",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  auditRevision: 8,
  targetMaterialRevision: 9,
  action: "approve-rollback",
  userQuote,
  staleStageIds: ["08-lighting", "09-environment", "10-export", "11-unity-parity"],
  gate12Status: "blocked",
  shippingAssetUnchanged: true,
  buildInstallPhone: "not-started",
};
saveManifest(manifest, event);
console.log(JSON.stringify(event, null, 2));
