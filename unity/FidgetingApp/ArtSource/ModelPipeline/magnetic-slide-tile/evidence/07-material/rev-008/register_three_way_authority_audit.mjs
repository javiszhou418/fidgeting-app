#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const expectedManifestRevision = 103;
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-008";
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedManifestRevision) {
  throw new Error(`Expected manifest revision ${expectedManifestRevision}, got ${manifest.revision}.`);
}

const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/three-way-authority-audit.json`), "utf8"));
if (!report.pass || report.diagnosis.earliestDivergenceGate !== "07-material") {
  throw new Error("The three-way source-of-truth audit is incomplete.");
}

const sourceAssetIds = report.sourceAssetIds;
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_three_way_authority_audit.mjs`, "process"],
  ["builder", "audit-source", `${evidenceRoot}/build_three_way_authority_audit.py`, "process"],
  ["original", "source-normalized-crop", `${evidenceRoot}/normalized-original-authority.png`, "validation"],
  ["blender", "blender-normalized-crop", `${evidenceRoot}/normalized-blender-current.png`, "validation"],
  ["unity", "unity-normalized-crop", `${evidenceRoot}/normalized-unity-current.png`, "validation"],
  ["report", "validation-report", `${evidenceRoot}/three-way-authority-audit.json`, "validation"],
  ["board", "material-board", `${evidenceRoot}/gate07-rev8-three-way-authority-audit.png`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-material-authority-audit-rev8-${suffix}-r008`,
    stageId: "07-material",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.endsWith(".py") || path.endsWith(".mjs")
        ? "source-linked authority audit"
        : "Python 3 / Pillow / OpenCV",
      version: "2026-08-26",
      recipe: `${evidenceRoot}/build_three_way_authority_audit.py`,
    },
    provenance: {
      origin: "repository-generated",
      assertedBy: "assistant",
      contentClass: slot,
      gate07Revision: 8,
      note: "Three-way audit only. It does not approve or replace the Gate 07 material.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

const claimId = "slider-gate07-rev8-original-authority-correction-r008";
manifest.claims.push({
  id: claimId,
  stageId: "07-material",
  statement: "Original user and exact-product appearance references outrank Blender and Unity outputs. Blender Gate 07 already diverges in crystal depth, red highlight breakup and layered bright-silver response, so Gate 11 tuning must stop.",
  confidence: "high",
  state: "active",
  sourceAssetIds,
  sourceRegions: report.regions,
  decisionState: "review-pending",
  deliveryState: "gate07-authority-audit-ready-for-review-gates08-to11-stale-gate12-blocked",
});

const stage = manifest.stages[6];
stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [`${modelId}-material-authority-audit-rev8-board-r008`];
stage.validations = [
  {
    id: "original-reference-authority-restored",
    status: "pass",
    evidence: "Authority order is original user/exact-product reference, then Blender implementation, then Unity implementation.",
  },
  {
    id: "source-linked-normalized-regions",
    status: "pass",
    evidence: "The audit records exact pixel regions for user red, official red, Blender and Unity crops. Different cameras are not used for silhouette pixel claims.",
  },
  {
    id: "earliest-divergence-gate",
    status: "pass",
    evidence: "Gate 07 Blender already lacks source-authoritative crystal depth and layered silver response. Gate 11 is downstream, not the root correction.",
  },
  {
    id: "locked-geometry-artwork-preserved",
    status: "pass",
    evidence: "Geometry, face count, pivot, slide semantics, motif mask and accepted artwork placement are unchanged.",
  },
  {
    id: "shipping-safety-preserved",
    status: "pass",
    evidence: "Gate 12 remains blocked, the old shipping model remains default, and no build, install or phone push was run.",
  },
];
stage.priorDecision = stage.decision;
stage.decision = null;
delete stage.staleReason;
stage.authorityAuditSpec = {
  revision: 8,
  authorityOrder: report.authorityOrder,
  earliestDivergenceGate: "07-material",
  correctedMaterialCreated: false,
  lockedDecisionsPreserved: report.lockedDecisionsPreserved,
  currentBlenderStatus: "invalidated-as-final-appearance-target",
  reviewQuestion: report.reviewQuestion,
  technicalDetailsCollapsed: true,
  boardAssetId: `${modelId}-material-authority-audit-rev8-board-r008`,
};
stage.materialSpec = {
  ...stage.materialSpec,
  authorityStatus: "invalidated-by-original-reference-audit",
  priorApprovalPreservedAsHistory: true,
};

const staleReason =
  "Gate 07 authority audit found that the approved Blender appearance diverged from original user/exact-product references. Rebuild and approve Gate 07 before revalidating Gates 08–11.";
for (let index = 7; index <= 10; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = staleReason;
}
manifest.stages[11].status = "blocked";
manifest.stages[11].staleReason =
  `${staleReason} Gate 12 rev 1 rejection remains preserved.`;

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}
for (let index = 0; index < manifest.stages.length; index += 1) {
  const candidate = manifest.stages[index];
  const assetHashes = candidate.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims
    .filter((claim) => claim.stageId === candidate.id)
    .map(stableJson);
  candidate.inputDigest = index === 0
    ? digestValues([...assetHashes, ...claimRecords])
    : manifest.stages[index - 1].outputDigest;
  candidate.outputDigest = digestValues([...assetHashes, ...claimRecords]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentState.visualApproval = "gate07-rev8-original-authority-audit-pending";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "The original product references are the appearance authority. Blender Gate 07 already flattened the blood-red crystal response and polished silver reflection, so Unity Gate 11 tuning is paused. Gate 07 rev 8 is an audit-only review; Gates 08–11 are stale, Gate 12 remains blocked, and the old shipping model remains default.";

const event = {
  id: crypto.randomUUID(),
  type: "stage-authority-audit-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 8,
  earliestDivergenceGate: "07-material",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  staleStageIds: ["08-lighting", "09-environment", "10-export", "11-unity-parity"],
  gate12Status: "blocked",
  autoApproved: false,
  reviewQuestion: report.reviewQuestion,
};
saveManifest(manifest, event);
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  gate07Status: stage.status,
  staleStageIds: event.staleStageIds,
  gate12Status: manifest.stages[11].status,
  reviewArtifactIds: stage.reviewArtifactIds,
}, null, 2));
