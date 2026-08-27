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
const expectedManifestRevision = 108;
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-010";
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedManifestRevision) {
  throw new Error(`Expected manifest revision ${expectedManifestRevision}, got ${manifest.revision}.`);
}
const material = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/material-axis-validation.json`), "utf8"));
const fidelity = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/source-fidelity-validation.json`), "utf8"));
const lower = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/lower-artwork-provenance.json`), "utf8"));
const review = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/review-board-report.json`), "utf8"));
if (!material.pass || !fidelity.pass || !lower.pass || !material.geometry.unchanged) {
  throw new Error("Gate 07 rev 10 validation is incomplete.");
}

const sourceAssetIds = material.sourceAssetIds;
const definitions = [
  ["correction-decision", "decision-source", "record_rev9_internal_rejection.mjs", "process"],
  ["lower-reconstructor", "material-source", "reconstruct_lower_artwork.py", "process"],
  ["builder", "material-source", "build_material_and_axis_review.py", "process"],
  ["review-builder", "review-source", "build_full_resolution_review.py", "process"],
  ["validator", "validation-source", "validate_rev10.py", "process"],
  ["blend", "blender-source", "magnetic-slide-tile-material-r010.blend", "source-model"],
  ["recipe", "material-recipe", "material-recipe-r010.json", "validation"],
  ["material-report", "validation-report", "material-axis-validation.json", "validation"],
  ["validation", "validation-report", "source-fidelity-validation.json", "validation"],
  ["lower-report", "validation-report", "lower-artwork-provenance.json", "validation"],
  ["review-report", "validation-report", "review-board-report.json", "validation"],
  ["lower-mask", "material-mask", "artwork-lower-mask-r010.png", "validation"],
  ["lower-direct-mask", "material-mask", "artwork-lower-direct-mask-r010.png", "validation"],
  ["lower-reconstructed-mask", "material-mask", "artwork-lower-reconstructed-mask-r010.png", "validation"],
  ["lower-provenance-map", "validation-overlay", "artwork-lower-provenance-map-r010.png", "validation"],
  ["lower-provenance", "material-process-board", "lower-artwork-direct-vs-reconstructed.png", "validation"],
  ["upper-front", "material-front", "upper-front.png", "blender-render"],
  ["oblique", "material-comparison", "oblique-crystal.png", "blender-render"],
  ["side", "material-side-reflection", "side-rim.png", "blender-render"],
  ["open", "material-open-artwork", "slide-open-21mm-0deg.png", "blender-render"],
  ["lower-open", "material-open-artwork", "lower-open-macro.png", "blender-render"],
  ["microflake", "material-closeup", "crystal-microflake-macro.png", "blender-render"],
  ["spin-00", "axis-angle-evidence", "spin-00deg.png", "blender-render"],
  ["spin-12", "axis-angle-evidence", "spin-12deg.png", "blender-render"],
  ["spin-36", "axis-angle-evidence", "spin-36deg.png", "blender-render"],
  ["source-review", "material-board", "source-fidelity-review-board.png", "validation"],
  ["closeups", "material-closeup", "material-closeups-board.png", "validation"],
  ["axis", "axis-angle-board", "axis-angle-evidence-board.png", "validation"],
];
const records = definitions.map(([suffix, slot, filename, role]) => {
  const path = `${evidenceRoot}/${filename}`;
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-material-rev10-${suffix}-r010`,
    stageId: "07-material",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: filename.endsWith(".blend") || filename.endsWith(".png")
        ? "Blender 5.2.0 LTS / deterministic bpy / Pillow"
        : filename.endsWith(".py")
          ? "Python 3 / bpy / Pillow / OpenCV"
          : "Gate 07 rev 10 registrar",
      version: "2026-08-26",
      recipe: `${evidenceRoot}/build_material_and_axis_review.py`,
    },
    provenance: {
      origin: "repository-generated",
      assertedBy: "assistant",
      contentClass: slot,
      gate07Revision: 10,
      appearanceAuthority: "original user frames primary; official exact-product image only for labeled occlusion reconstruction language",
      geometryChanged: false,
      unityTouched: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

const claimId = "slider-gate07-rev10-material-axis-review-r010";
manifest.claims.push({
  id: claimId,
  stageId: "07-material",
  statement: "Gate 07 rev 10 preserves approved geometry and motion while correcting the distinct lower artwork and granular blood-red crystal. The review explicitly shows the [0,-9.5,0] +Z point axis at 0°, 12° and 36°, with zero spin translation and zero pivot drift.",
  confidence: "high",
  state: "active",
  sourceAssetIds,
  sourceRegions: lower.sources,
  decisionState: "review-pending-after-rev9-provisional-visual-acceptance",
  deliveryState: "gate07-ready-for-review-gates08-to11-stale-gate12-blocked-old-shipping-default",
});

const stage = manifest.stages[6];
if (stage.revision !== 21 || stage.status !== "draft") {
  throw new Error(`Expected Gate 07 draft stage revision 21, got ${stage.revision}/${stage.status}.`);
}
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-material-rev10-source-review-r010`,
  `${modelId}-material-rev10-closeups-r010`,
  `${modelId}-material-rev10-axis-r010`,
  `${modelId}-material-rev10-lower-provenance-r010`,
];
stage.validations = [
  {
    id: "geometry-digest-and-matrices-unchanged",
    status: "pass",
    evidence: `${material.geometry.digestAfter}; base matrices unchanged.`,
  },
  {
    id: "lower-artwork-distinct-and-editable",
    status: "pass",
    evidence: `Upper/lower hashes differ; binary difference ${lower.mask.binaryDifferenceFraction}; direct and reconstructed regions remain separate.`,
  },
  {
    id: "direct-versus-reconstructed-provenance",
    status: "pass",
    evidence: `Direct ${lower.directTrace.pixelCount} px from user frames 03/05/10; occluded region is labeled reconstruction, not exact trace.`,
  },
  {
    id: "crystal-granular-variation-and-microflakes",
    status: "pass",
    evidence: `Front/oblique red σ ${fidelity.metrics.front.redLumaStd}/${fidelity.metrics.oblique.redLumaStd}; macro sparkle ${fidelity.metrics.macro.sparklePixelCount} px across ${fidelity.metrics.macro.sparkleQuadrantsPopulated} quadrants.`,
  },
  {
    id: "silver-and-dark-side-response",
    status: "pass",
    evidence: `Neutral p05–p95 range ${fidelity.metrics.side.neutralP05P95Range}; dark fraction ${fidelity.metrics.side.darkFraction}; bright reflection fraction ${fidelity.metrics.side.brightReflectionFraction}.`,
  },
  {
    id: "zero-emission-bloom-clipping",
    status: "pass",
    evidence: "Emission 0; Bloom false; maximum material-review clipping remains below 0.03%.",
  },
  {
    id: "detent-aligned-preview-angles",
    status: "pass",
    evidence: "Spin poses are exactly 0°/12°/36° = detents 0/1/3; 360° / 12° = 30; 45° is not a primary pose.",
  },
  {
    id: "exact-point-axis-transform",
    status: "pass",
    evidence: "[0,-9.5,0] mm +Z; every spin pose has translation 0 mm and pivot drift 0 mm.",
  },
  {
    id: "separate-slide-open-pose",
    status: "pass",
    evidence: "UpperTranslation [0,+21,0] mm with 0° rotation; not mixed with a spin pose.",
  },
  {
    id: "shipping-safety-preserved",
    status: "pass",
    evidence: "No Unity, build, install or phone action ran. The old shipping model remains default.",
  },
];
stage.decision = null;
delete stage.staleReason;
stage.materialRebuildSpec = {
  revision: 10,
  authority: "original product references",
  userQuote: "我暂时确认了 rev 9，但是我希望你下一次再找我确认的时候，能把轴心旋转的角度也带上.",
  rev9DecisionState: "provisional-visual-acceptance-only-not-formal-gate-approval",
  geometryDigest: material.geometry.digestAfter,
  geometryChanged: false,
  artworkPlacementChanged: false,
  maskFilesRemainExternal: true,
  lowerArtworkProvenance: {
    directTrace: lower.directTrace,
    reconstruction: lower.reconstruction,
    upperMaskSha256: lower.mask.upperSha256,
    lowerMaskSha256: lower.mask.lowerSha256,
    hashesDistinct: lower.mask.hashesDistinct,
  },
  motionEvidence: material.motionEvidence,
  recipe: material.recipe,
  reviewQuestion: review.reviewQuestion,
  technicalDetailsCollapsed: true,
  approvalBasisAssetIds: stage.reviewArtifactIds,
  supportingOnlyAssetIds: [
    `${modelId}-material-rev10-validation-r010`,
    `${modelId}-material-rev10-material-report-r010`,
  ],
};
stage.materialSpec = {
  ...stage.materialSpec,
  authorityStatus: "rev10-corrected-from-original-references-review-pending",
  polishedSilver: material.recipe.silver,
  crystal: material.recipe.crystal,
  motif: material.recipe.motif,
  perimeter: material.recipe.perimeter,
  lowerArtwork: material.recipe.lowerArtwork,
  colorManagement: material.recipe.colorManagement,
  productionChemistryClaim: material.recipe.chemistryClaim,
};

const staleReason =
  "Gate 07 rev 10 material, distinct lower artwork and point-axis review are pending explicit approval. Gates 08–11 remain stale.";
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
manifest.currentState.visualApproval = "gate07-rev10-material-artwork-axis-review-pending";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "Gate 07 rev 9 has provisional visual acceptance only, not formal approval. Gate 07 rev 10 corrects distinct lower artwork and granular blood-red crystal, and shows [0,-9.5,0] +Z spin poses at 0°/12°/36° plus a separate +21 mm/0° slide pose. Gates 08–11 remain stale; Gate 12 remains blocked/rejected; no Unity, build, install or phone work ran.";

const event = {
  id: crypto.randomUUID(),
  type: "stage-material-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 10,
  userQuote: stage.materialRebuildSpec.userQuote,
  rev9FormalApproval: false,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  motionEvidence: material.motionEvidence,
  staleStageIds: ["08-lighting", "09-environment", "10-export", "11-unity-parity"],
  gate12Status: "blocked",
  oldShippingModelDefault: true,
  unityBuildInstallPhone: "not-started",
  autoApproved: false,
  reviewQuestion: review.reviewQuestion,
};
saveManifest(manifest, event);
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  gate07Status: stage.status,
  reviewArtifactIds: stage.reviewArtifactIds,
  staleStageIds: event.staleStageIds,
  gate12Status: manifest.stages[11].status,
}, null, 2));
