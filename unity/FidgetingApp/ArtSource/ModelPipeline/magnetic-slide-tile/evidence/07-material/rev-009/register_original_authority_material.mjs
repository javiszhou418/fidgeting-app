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
const expectedManifestRevision = 105;
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-009";
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedManifestRevision) {
  throw new Error(`Expected manifest revision ${expectedManifestRevision}, got ${manifest.revision}.`);
}
const blender = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/blender-material-validation.json`), "utf8"));
const fidelity = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/source-fidelity-validation.json`), "utf8"));
if (!blender.pass || !fidelity.pass || !blender.geometry.unchanged) {
  throw new Error("Gate 07 rev 9 validation is incomplete.");
}

const sourceAssetIds = blender.sourceAssetIds;
const definitions = [
  ["rollback", "decision-source", `${evidenceRoot}/record_rollback_decision.mjs`, "process"],
  ["builder", "material-source", `${evidenceRoot}/build_original_authority_material.py`, "process"],
  ["review-builder", "review-source", `${evidenceRoot}/build_source_fidelity_review.py`, "process"],
  ["blend", "blender-source", `${evidenceRoot}/magnetic-slide-tile-material-r009.blend`, "source-model"],
  ["recipe", "material-recipe", `${evidenceRoot}/material-recipe.json`, "validation"],
  ["blender-report", "validation-report", `${evidenceRoot}/blender-material-validation.json`, "validation"],
  ["fidelity-report", "validation-report", `${evidenceRoot}/source-fidelity-validation.json`, "validation"],
  ["front", "material-front", `${evidenceRoot}/corrected-front.png`, "blender-render"],
  ["oblique", "material-comparison", `${evidenceRoot}/corrected-oblique.png`, "blender-render"],
  ["side", "material-side-reflection", `${evidenceRoot}/corrected-side.png`, "blender-render"],
  ["open", "material-open-artwork", `${evidenceRoot}/corrected-open.png`, "blender-render"],
  ["crystal", "material-closeup", `${evidenceRoot}/crystal-macro.png`, "blender-render"],
  ["silver", "material-side-reflection", `${evidenceRoot}/silver-reflection-closeup.png`, "blender-render"],
  ["perimeter", "material-closeup", `${evidenceRoot}/black-perimeter-closeup.png`, "blender-render"],
  ["source-front", "source-normalized-crop", `${evidenceRoot}/source-normalized-front.png`, "validation"],
  ["source-oblique", "source-normalized-crop", `${evidenceRoot}/source-normalized-oblique.png`, "validation"],
  ["source-open", "source-normalized-crop", `${evidenceRoot}/source-normalized-open.png`, "validation"],
  ["review", "material-board", `${evidenceRoot}/gate07-rev9-source-fidelity-review.png`, "validation"],
  ["closeups", "material-closeup", `${evidenceRoot}/gate07-rev9-material-closeups.png`, "validation"],
  ["layers", "material-process-board", `${evidenceRoot}/gate07-rev9-editable-layer-board.png`, "validation"],
  ["heatmap", "validation-overlay", `${evidenceRoot}/gate07-rev9-supporting-heatmap.png`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-material-original-authority-rev9-${suffix}-r009`,
    stageId: "07-material",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.endsWith(".blend") || path.endsWith(".png")
        ? "Blender 5.2.0 LTS / deterministic bpy"
        : path.endsWith(".py")
          ? "Python 3 / bpy / Pillow / OpenCV"
          : "Gate 07 rev 9 registrar",
      version: "2026-08-26",
      recipe: `${evidenceRoot}/build_original_authority_material.py`,
    },
    provenance: {
      origin: "repository-generated",
      assertedBy: "assistant",
      contentClass: slot,
      gate07Revision: 9,
      appearanceAuthority: "original user frames primary; official exact-product images corroboration only",
      geometryChanged: false,
      unityTouched: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

const claimId = "slider-gate07-rev9-original-authority-material-r009";
manifest.claims.push({
  id: claimId,
  stageId: "07-material",
  statement: "Gate 07 rev 9 rebuilds only the Blender look from original product references: deep blood-red layered crystal, polished silver with bright and dark reflections, and a reflective full black perimeter. Geometry and accepted editable artwork placement remain unchanged.",
  confidence: "high",
  state: "active",
  sourceAssetIds,
  sourceRegions: fidelity.sourceNormalization,
  decisionState: "review-pending",
  deliveryState: "gate07-ready-for-review-gates08-to11-stale-gate12-blocked-old-shipping-default",
});

const stage = manifest.stages[6];
if (stage.revision !== 19 || stage.status !== "draft") {
  throw new Error(`Expected Gate 07 draft revision 9, got ${stage.revision}/${stage.status}.`);
}
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-material-original-authority-rev9-review-r009`,
  `${modelId}-material-original-authority-rev9-closeups-r009`,
  `${modelId}-material-original-authority-rev9-layers-r009`,
];
stage.validations = [
  {
    id: "geometry-digest-and-matrices-unchanged",
    status: "pass",
    evidence: `${blender.geometry.digestAfter}; object matrices unchanged; no geometry edit.`,
  },
  {
    id: "original-reference-authority",
    status: "pass",
    evidence: "User frames 01/05/10 are primary. Official exact-product images corroborate material behavior only.",
  },
  {
    id: "source-steel-normalization",
    status: "pass",
    evidence: "Each user frame records a steel sample rectangle, neutral-pixel rule, selected count and RGB channel scale.",
  },
  {
    id: "silver-bright-dark-reflection",
    status: "pass",
    evidence: `Silver macro luma p0.1/p50/p99.9: ${fidelity.metrics.silver.lumaP001P50P999.join("/")}.`,
  },
  {
    id: "crystal-local-variation-and-depth",
    status: "pass",
    evidence: `Crystal red luma σ ${fidelity.metrics.crystal.redLumaStd}; Laplacian ${fidelity.metrics.crystal.laplacianVariance}; view-dependent blue/green pixels ${fidelity.metrics.oblique.blueGreenAnglePixelCount}.`,
  },
  {
    id: "black-perimeter-reflectance",
    status: "pass",
    evidence: `Perimeter luma p0.1/p50/p99.9: ${fidelity.metrics.perimeter.lumaP001P50P999.join("/")}.`,
  },
  {
    id: "artwork-identity-editability",
    status: "pass",
    evidence: `Upper ${blender.artwork.upperMaskSha256}; lower ${blender.artwork.lowerMaskSha256}; perimeter ${blender.artwork.borderMaskSha256}. Separate external files remain replaceable.`,
  },
  {
    id: "motif-sharpness-and-open-legibility",
    status: "pass",
    evidence: `Crystal edge density ${fidelity.metrics.crystal.edgeDensity}; open red pixels ${fidelity.metrics.open.redPixelCount}; open edge density ${fidelity.metrics.open.edgeDensity}.`,
  },
  {
    id: "zero-emission-clipping",
    status: "pass",
    evidence: "Silver and crystal emission are 0. All review renders remain below 1% white clipping.",
  },
  {
    id: "shipping-safety-preserved",
    status: "pass",
    evidence: "No Unity, build, install or phone action ran. The old shipping model remains default.",
  },
];
stage.decision = null;
delete stage.staleReason;
stage.authorityAuditSpec = {
  ...stage.authorityAuditSpec,
  reviewState: "rollback-approved",
  userQuote: "退回，我们要优先保证模型的质量",
  correctedMaterialCreated: true,
  correctedMaterialRevision: 9,
};
stage.materialRebuildSpec = {
  revision: 9,
  authority: "original product references",
  userQuote: "退回，我们要优先保证模型的质量",
  geometryDigest: blender.geometry.digestAfter,
  geometryChanged: false,
  artworkPlacementChanged: false,
  maskFilesRemainExternal: true,
  recipe: blender.recipe,
  sourceNormalization: fidelity.sourceNormalization,
  reviewQuestion: fidelity.reviewQuestion,
  technicalDetailsCollapsed: true,
  approvalBasisAssetIds: stage.reviewArtifactIds,
  supportingOnlyAssetIds: [`${modelId}-material-original-authority-rev9-heatmap-r009`],
};
stage.materialSpec = {
  ...stage.materialSpec,
  authorityStatus: "corrected-from-original-references-review-pending",
  polishedSilver: blender.recipe.silver,
  crystal: blender.recipe.crystal,
  motif: blender.recipe.motif,
  perimeter: blender.recipe.perimeter,
  colorManagement: blender.recipe.colorManagement,
  productionChemistryClaim: blender.recipe.chemistryClaim,
};

const staleReason =
  "Gate 07 rev 9 material is ready for original-reference visual review. Gates 08–11 remain stale until explicit Gate 07 approval.";
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
manifest.currentState.visualApproval = "gate07-rev9-original-authority-material-pending";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "The user explicitly said “退回，我们要优先保证模型的质量”. Gate 07 rev 9 now rebuilds Blender material from original product references and is ready for visual review. Gates 08–11 remain stale; Gate 12 remains blocked/rejected; the old shipping model remains default; no Unity, build, install or phone work ran.";

const event = {
  id: crypto.randomUUID(),
  type: "stage-material-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 9,
  userQuote: "退回，我们要优先保证模型的质量",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  staleStageIds: ["08-lighting", "09-environment", "10-export", "11-unity-parity"],
  gate12Status: "blocked",
  oldShippingModelDefault: true,
  unityBuildInstallPhone: "not-started",
  autoApproved: false,
  reviewQuestion: fidelity.reviewQuestion,
};
saveManifest(manifest, event);
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  gate07Status: stage.status,
  reviewArtifactIds: stage.reviewArtifactIds,
  staleStageIds: event.staleStageIds,
  gate12Status: manifest.stages[11].status,
}, null, 2));
