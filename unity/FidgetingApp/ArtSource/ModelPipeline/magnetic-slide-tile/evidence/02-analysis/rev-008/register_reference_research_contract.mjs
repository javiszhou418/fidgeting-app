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

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const expectedRevision = Number(process.env.EXPECTED_REVISION || 122);
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (!stage) throw new Error("Missing Gate 02.");
const contractPath = path.join(here, "mechanism-evidence-contract.json");
const contract = JSON.parse(fs.readFileSync(contractPath, "utf8"));
const contractHash = sha256File(contractPath);
const createdAt = new Date().toISOString();
const revision = manifest.revision + 1;
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const addAsset = (spec) => {
  if (manifest.assets.some((asset) => asset.id === spec.id)) throw new Error(`Duplicate asset ${spec.id}`);
  const absolutePath = path.resolve(repoRoot, spec.path);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing asset file ${spec.path}`);
  const asset = {
    id: spec.id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
    path: toRepoPath(absolutePath),
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: spec.contentClass.includes("schema") || spec.contentClass.includes("builder") ? "process" : "analysis",
    producer: {
      name: "fidgeting-model-pipeline",
      version: "1",
      recipe: "Immutable Gate 02 executable evidence contract"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: spec.contentClass,
      assertedBy: "assistant",
      note: spec.note
    },
    sourceAssetIds: contract.sourceInventory.assetIds
  };
  manifest.assets.push(asset);
  if (!stage.artifactIds.includes(asset.id)) stage.artifactIds.push(asset.id);
  return asset;
};
const assetSpecs = [
  {
    id: "slider-analysis-mechanism-evidence-contract-r008",
    path: path.relative(repoRoot, contractPath),
    contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
    note: "Executable source-linked constraints for all later CAD, Blender, Unity, Haptics and tests."
  },
  {
    id: "slider-analysis-mechanism-evidence-contract-builder-r008",
    path: path.relative(repoRoot, path.join(here, "build_mechanism_evidence_contract.mjs")),
    contentClass: "deterministic-evidence-contract-builder",
    note: "Rebuilds the contract from hashed pipeline sources and fails on missing source assets."
  },
  {
    id: "slider-analysis-mechanism-evidence-contract-schema-r008",
    path: "tools/model-provenance-explorer/mechanism-evidence-contract.schema.json",
    contentClass: "mechanism-evidence-contract-json-schema",
    note: "Schema for required values, states, source regions, decisions and downstream consumers."
  }
];
for (const spec of assetSpecs) {
  addAsset(spec);
}

const rootClaimId = "slider-analysis-evidence-contract-authority-r008";
for (const claim of manifest.claims) {
  if (
    claim.stageId === "02-analysis"
    && claim.state !== "superseded"
    && claim.id !== rootClaimId
  ) {
    claim.state = "superseded";
    claim.decisionState = "superseded-by-executable-evidence-contract";
    claim.supersededBy = rootClaimId;
  }
}
manifest.claims.push({
  id: rootClaimId,
  stageId: "02-analysis",
  category: "mechanism-contract",
  statement: "All downstream mechanism generation must consume the Gate 02 rev 8 evidence contract and record its SHA-256.",
  confidence: "high",
  sourceAssetIds: contract.sourceInventory.assetIds,
  sourceRegions: [],
  state: "pending-review",
  decisionState: "pending-user-approval",
  analysisRevision: "008",
  assertedBy: "assistant",
  verificationMethod: "schema, source-link, region and no-duplicate-default validation",
  boundary: "No CAD, Blender, Unity or Haptics generation before explicit Gate 02 approval."
});
for (const constraint of contract.constraints) {
  manifest.claims.push({
    id: `slider-analysis-${constraint.id.toLowerCase()}-r008`,
    stageId: "02-analysis",
    category: "mechanism",
    statement: constraint.decisionNote,
    confidence: constraint.confidence,
    sourceAssetIds: constraint.sourceAssetIds,
    sourceRegions: constraint.regions,
    downstreamConsumers: constraint.downstreamConsumers,
    state: constraint.state === "unknown" ? "unknown" : "pending-review",
    evidenceState: constraint.state,
    decisionState: "pending-user-approval",
    analysisRevision: "008",
    assertedBy: "assistant",
    verificationMethod: `contract constraint ${constraint.id}`,
    boundary: constraint.decisionNote
  });
}

stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 02 rev 8 asks only whether the executable evidence constraints are correct enough to unlock interactive CAD."
};
stage.analysisSpec = {
  revision: 8,
  phase: "step-1-reference-research",
  gateGrouping: ["01-intake", "02-analysis"],
  reviewMode: "source-to-constraint-application",
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r008",
  contractSha256: contractHash,
  sourceInventory: contract.sourceInventory.counts,
  constraintIds: contract.constraints.map((constraint) => constraint.id),
  coverageTopics: contract.coverageMatrix.map((row) => row.topic),
  conclusions: contract.conclusions,
  unknowns: contract.unknowns,
  cadGeneration: {
    locked: true,
    unlockCondition: "explicit Gate 02 approval",
    configSource: "slider-analysis-mechanism-evidence-contract-r008",
    duplicateDefaultsForbidden: true
  },
  downstreamHashPolicy: contract.downstreamPolicy,
  reviewQuestion: contract.reviewQuestion
};
stage.reviewArtifactIds = [
  "slider-analysis-mechanism-evidence-contract-r008",
  "slider-analysis-official-mechanism-board-r002",
  "slider-intake-user-contact-sheet",
  "slider-intake-obsidian-contact-sheet",
  "slider-intake-nxedc-contact-sheet",
  "slider-intake-haloo-official-07"
];
for (const id of stage.reviewArtifactIds) {
  if (!stage.artifactIds.includes(id)) stage.artifactIds.push(id);
}
for (const spec of assetSpecs) {
  if (!stage.artifactIds.includes(spec.id)) stage.artifactIds.push(spec.id);
}
for (const staleStage of manifest.stages.filter((candidate) => {
  const gate = Number(candidate.id.slice(0, 2));
  return gate >= 3 && gate <= 11;
})) {
  staleStage.status = "stale";
  staleStage.readiness = {
    ready: false,
    blockers: ["Gate 02 rev 8 evidence contract is awaiting approval."],
    note: "Downstream work is stale until the reference contract is approved."
  };
}
const gate12 = manifest.stages.find((candidate) => candidate.id === "12-shipping");
gate12.status = "rejected";
gate12.readiness = {
  ready: false,
  blockers: ["Gate 02 rev 8 is not approved; shipping review remains blocked."],
  note: "No shipping review before the reference contract and all downstream gates are approved."
};
manifest.currentStageId = "02-analysis";
manifest.overallStatus = "in_progress";
stage.validations.push({
  id: "mechanism-evidence-contract-source-first-r008",
  status: "pass",
  evidence: `${contract.sourceInventory.counts.uniqueAssets} hashed sources, ${contract.constraints.length} executable constraints and ${contract.coverageMatrix.length} coverage rows.`
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision = revision;
manifest.updatedAt = createdAt;
manifest.currentState.visualApproval = "gate02-rev8-executable-evidence-contract-review-pending";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 8 converts all reference research into source-linked executable constraints. Interactive CAD remains locked; Gates 03–11 are stale and Gate 12 is blocked/rejected. No Blender, Unity, build, install or phone work ran.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-reference-research-contract-ready",
  modelId: manifest.model.id,
  manifestRevision: revision,
  timestamp: createdAt,
  stageId: "02-analysis",
  analysisEvidenceRevision: 8,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r008",
  contractSha256: contractHash,
  sourceCount: contract.sourceInventory.counts.uniqueAssets,
  constraintCount: contract.constraints.length,
  coverageRowCount: contract.coverageMatrix.length,
  priorRevision: 7,
  priorDecision: "requested_revision",
  decisionState: "ready_for_review",
  deliveryState: "reference-contract-only-no-generation",
  cadLocked: true,
  reason: "Reference analysis now becomes executable source-linked constraints instead of a passive gallery.",
  reviewQuestion: contract.reviewQuestion
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  contractSha256: contractHash,
  sources: contract.sourceInventory.counts.uniqueAssets,
  constraints: contract.constraints.length,
  currentStageId: manifest.currentStageId
}, null, 2));
