#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const expectedRevision = 119;
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}
const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 6) {
  throw new Error("Gate 02 rev 6 must remain ready_for_review.");
}
const timestamp = new Date().toISOString();
const sourceClaim = manifest.claims.find((claim) => claim.id === "slider-analysis-rotation-across-slide-r003");
const claim = {
  id: "slider-analysis-simultaneous-two-dof-r006",
  stageId: "02-analysis",
  category: "motion",
  statement: "滑动与旋转可同时操作；同一次直接拖动可同时改变 s 与 θ，沙盒中所有用户授权滑位均允许旋转。",
  confidence: "user-authoritative",
  sourceRegions: sourceClaim.sourceRegions,
  sourceAssetIds: sourceClaim.sourceAssetIds,
  state: "pending-review",
  decisionState: "pending-user-approval",
  analysisRevision: "009",
  assertedBy: "assistant",
  boundary: "视频分别证明部分与近最大滑位旋转；每个精确滑位可转是用户权威玩法规则。"
};
manifest.claims.push(claim);
stage.analysisSpec.claimIds.push(claim.id);
stage.analysisSpec.compoundInteraction = {
  degreesOfFreedom: 2,
  simultaneous: true,
  defaultDirectManipulation: "moving-lower-body",
  isolatedSlideRotateModesInDefaultUi: false,
  solve: "longitudinal-pointer-component-to-s-and-tangential-component-to-theta",
  grabbedLocalPointPreserved: true,
  ringRole: "secondary-precision-rotation-handle",
  rotationAtEveryAuthorizedSlidePosition: "user-authoritative",
  individualVideoProof: ["partial-travel", "near-maximum-travel"],
  angularDetentDoesNotBlockSlide: true,
  translationClampDoesNotBlockRotation: true,
  resetLinearVelocityLPerSecond: 0,
  resetAngularVelocityDegPerSecond: 0
};
Object.assign(stage.analysisSpec.mechanismSandbox, {
  simultaneousSlideAndRotation: true,
  directBodyDrag: true,
  pathTrace: true,
  linearVelocityChannel: true,
  angularVelocityChannel: true
});

const absolutePath = fileURLToPath(import.meta.url);
const asset = {
  id: "slider-analysis-compound-correction-registrar-r006",
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: toRepoPath(absolutePath),
  sha256: sha256File(absolutePath),
  exists: true,
  sizeBytes: fs.statSync(absolutePath).size,
  role: "process",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "1",
    recipe: "Revision-guarded simultaneous two-DOF correction"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "user-authoritative-compound-interaction-correction",
    assertedBy: "assistant",
    note: "同一 rev 6 增加滑动与旋转同时操作规则；不恢复默认分离模式。"
  },
  sourceAssetIds: ["slider-analysis-cad-review-contract-r006"]
};
manifest.assets.push(asset);
stage.artifactIds.push(asset.id);
stage.validations.push({
  id: "simultaneous-two-dof-contract",
  status: "pass",
  evidence: "One direct body drag updates s and theta; angular detent and translation limits remain channel-specific."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (id) => manifest.assets.find((candidate) => candidate.id === id)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev6-compound-cad-review-pending";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 6 is ready for review with simultaneous slide+rotation direct manipulation, translated lower axis, bilateral rails and synchronized CAD views. Rev 5 remains rejected. Gates 03–11 are stale; Gate 12 remains blocked/rejected. No Blender, Unity, build, install or phone work ran.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-compound-interaction-correction-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 6,
  userCorrection: "slide-and-rotation-are-simultaneous-two-dof",
  claimId: claim.id,
  defaultSeparatedModes: false,
  directBodyDrag: true,
  rotationRingRole: "secondary-precision-handle",
  gateStatus: stage.status,
  downstreamStatus: "gates03-11-stale-gate12-blocked-rejected"
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  analysisRevision: stage.analysisSpec.revision,
  simultaneous: stage.analysisSpec.compoundInteraction.simultaneous,
  status: stage.status
}, null, 2));
