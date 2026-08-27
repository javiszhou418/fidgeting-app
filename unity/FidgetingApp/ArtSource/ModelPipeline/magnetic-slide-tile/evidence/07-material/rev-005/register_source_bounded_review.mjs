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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-005";
const manifest = loadManifest(modelId);
const stage = manifest.stages[6];
if (manifest.revision !== 58 || stage.status !== "rejected" || stage.materialSpec?.revision !== 4) {
  throw new Error("Expected rejected Gate 07 rev 4 at manifest revision 58.");
}

const definitions = [
  ["review-registrar", "registration-source", "register_source_bounded_review.mjs"],
  ["artwork-deriver", "artwork-source", "derive_blood_red_artwork_with_boundaries.py"],
  ["artwork-upper-source", "artwork-source-crop", "upper-source-rectified.png"],
  ["artwork-lower-source", "artwork-source-crop", "lower-visible-source-rectified.png"],
  ["artwork-upper-mask", "artwork-mask", "artwork-upper-mask.png"],
  ["artwork-lower-direct-mask", "artwork-mask", "artwork-lower-direct-trace-mask.png"],
  ["artwork-lower-unknown", "artwork-unknown-mask", "artwork-lower-occluded-unknown.png"],
  ["artwork-lower-reconstructed-mask", "artwork-mask", "artwork-lower-reconstructed-mask.png"],
  ["artwork-lower-mask", "artwork-mask", "artwork-lower-mask.png"],
  ["artwork-config", "artwork-config", "artwork-layers.json"],
  ["supplemental-source-config", "source-manifest", "supplemental-source-manifest.json"],
  ["artwork-source-boundary-board", "material-process-board", "artwork-source-boundary-board.png"],
  ["blood-red-analysis", "color-analysis", "blood-red-source-analysis.json"],
  ["artwork-derivation-validation", "validation-report", "artwork-derivation-validation.json"],
  ["material-builder", "material-source", "build_blood_red_editable_artwork.py"],
  ["material-blend", "material-blend", "magnetic-slide-tile-material-r005.blend"],
  ["material-comparison", "material-comparison", "blood-red-source-comparison.png"],
  ["material-front", "material-front", "neutral-front-blood-red.png"],
  ["material-board", "material-board", "neutral-pbr-material-board.png"],
  ["material-closeup", "material-closeup", "neutral-pbr-material-closeup.png"],
  ["material-second-light", "material-second-light", "diagnostic-second-light-crystal-response.png"],
  ["material-side-reflection", "material-side-reflection", "diagnostic-side-direct-reflection.png"],
  ["material-open-artwork", "material-open-artwork", "open-slide-lower-artwork.png"],
  ["material-process-board", "material-process-board", "editable-artwork-layer-board.png"],
  ["material-image-validator", "validation-source", "validate_blood_red_artwork.py"],
  ["material-image-validation", "validation-report", "image-artwork-validation.json"],
  ["material-blender-audit-source", "validation-source", "audit_blender_rev5.py"],
  ["material-blender-audit", "validation-report", "blender-audit.json"],
  ["material-validation", "validation-report", "material-validation.json"],
  ["supplemental-ch-plus-page", "supplemental-reference", "supplemental/chromehearts-ch-plus-matchstick-holder.html"],
  ["supplemental-ch-plus-image", "supplemental-reference", "supplemental/chromehearts-ch-plus-matchstick-holder.png"],
  ["supplemental-crosstail-page", "supplemental-reference", "supplemental/chromehearts-crosstail-water.html"],
  ["supplemental-crosstail-image", "supplemental-reference", "supplemental/chromehearts-crosstail-water.png"],
  ["supplemental-stencil-page", "supplemental-reference", "supplemental/chromehearts-stencil-dagger-socks.html"],
  ["supplemental-stencil-image", "supplemental-reference", "supplemental/chromehearts-stencil-dagger-socks.png"],
];
const sourceUrls = {
  "supplemental-ch-plus-page": "https://www.chromehearts.com/scents/matchstick-holder/148310SLVXXX186.html",
  "supplemental-ch-plus-image": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw9d7b3726/img_products/hi-res/148310SLVXXX186_1.png?sw=1600&sh=2000",
  "supplemental-crosstail-page": "https://www.chromehearts.com/baccarat/water/177732CRYXXX042.html",
  "supplemental-crosstail-image": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw2513c62d/img_products/hi-res/503177732CRYXXX042_0632.png?sw=1600&sh=2000",
  "supplemental-stencil-page": "https://www.chromehearts.com/socks/stencil-socks/176354MB3XXX465.html",
  "supplemental-stencil-image": "https://www.chromehearts.com/dw/image/v2/BFBV_PRD/on/demandware.static/-/Sites-ch-master-catalog/default/dw35e5a211/img_products/hi-res/316176354MB3MED465_1.png?sw=1600&sh=2000",
};
const sourceAssetIds = [
  "magnetic-slide-tile-geometry-blend-r001",
  "slider-intake-haloo-official-04",
  "slider-intake-nxedc-ref-01",
];
const sourceClaimIds = [
  "slider-analysis-claim-material-language",
  "slider-blockout-point-axis-distinction-r003",
  "slider-ratchet-30-detent-requirement-r001",
];
const materialReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/material-validation.json`)));
const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/image-artwork-validation.json`)));
const artwork = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/artwork-layers.json`)));
const supplemental = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/supplemental-source-manifest.json`)));
if (materialReport.materialRevision !== 5 || !imageReport.pass || artwork.sourcePriority[0] !== "exact-product-direct-trace") {
  throw new Error("Gate 07 rev 5 evidence did not pass.");
}

const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const sourceUrl = sourceUrls[suffix];
  const generatedWithPython = file.endsWith(".py") || file.endsWith(".mjs") || file.endsWith(".json");
  return {
    id: `${modelId}-${suffix}-r005`,
    stageId: "07-material",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "process",
    producer: {
      name: sourceUrl ? "Chrome Hearts official web archive" : generatedWithPython ? "Pillow/OpenCV/Python" : "Blender",
      version: sourceUrl ? "retrieved 2026-08-24" : generatedWithPython ? "Python 3 / OpenCV 4.13 / Pillow" : materialReport.blender,
      recipe: sourceUrl || `${root}/${generatedWithPython ? file : "build_blood_red_editable_artwork.py"}`,
    },
    provenance: {
      origin: sourceUrl ? "external" : "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: sourceUrl
        ? "Primary official Chrome Hearts supplemental reference; not exact-product evidence; unreadable motif regions only."
        : "Gate 07 rev 5 source-bounded material evidence.",
      userClaimIds: sourceClaimIds,
      ...(sourceUrl ? { sourceUrl, notExactProductEvidence: true } : {}),
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const userClaimId = "slider-artwork-source-boundary-r005";
manifest.claims.push({
  id: userClaimId,
  stageId: "07-material",
  topic: "exact-product-first-supplemental-motif-boundary",
  statement: "精确 HALOOPLAYER/NXEDC 产品图始终优先；仅在原图不可读区域才可使用独立归档的 Chrome Hearts 官方 gothic cross／floral／pointed-arch／blackened-silver 语言。manifest 与 review board 必须区分直接 trace、occluded/incomplete 和明确标注的 Chrome Hearts-style reconstruction，并保留上下 mask 独立替换。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds,
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "locked",
  deliveryState: "gate07-review-pending",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "artwork-source-boundary-board",
  "material-comparison",
  "material-second-light",
  "material-side-reflection",
  "material-open-artwork",
  "material-process-board",
  "material-board",
  "material-closeup",
].map((suffix) => `${modelId}-${suffix}-r005`);
stage.materialSpec = {
  ...stage.materialSpec,
  revision: 5,
  supersedesRevision: 4,
  recommendedVariant: "blood-red-source-bounded-editable-artwork",
  artwork: {
    configAssetId: `${modelId}-artwork-config-r005`,
    upperMaskAssetId: `${modelId}-artwork-upper-mask-r005`,
    lowerMaskAssetId: `${modelId}-artwork-lower-mask-r005`,
    lowerDirectMaskAssetId: `${modelId}-artwork-lower-direct-mask-r005`,
    lowerUnknownAssetId: `${modelId}-artwork-lower-unknown-r005`,
    lowerReconstructedMaskAssetId: `${modelId}-artwork-lower-reconstructed-mask-r005`,
    supplementalSourceManifestAssetId: `${modelId}-supplemental-source-config-r005`,
    sourceBoundaryBoardAssetId: `${modelId}-artwork-source-boundary-board-r005`,
    nodeGroups: ["Artwork_Upper", "Artwork_Lower"],
    independentlySwappable: true,
    geometryRebuildRequired: false,
    exactProductFirst: true,
    sourceBoundaryClasses: [
      "directly-traced-exact-product",
      "occluded-incomplete",
      "chrome-hearts-style-reconstructed",
    ],
    confidenceByRegion: {
      upperDirect: "high",
      lowerDirect: "medium",
      lowerOccluded: "none-for-exact-detail",
      lowerReconstructed: "low",
    },
    supplementalOnlyWhereUnreadable: true,
  },
  imageMetrics: imageReport,
  userClaimId,
};
stage.validations = [
  { id: "rev4-superseded-preserved", status: "pass", evidence: "Rev 4 remains immutable; rev 5 is additive." },
  { id: "exact-product-first", status: "pass", evidence: "sourcePriority starts with exact-product-direct-trace." },
  { id: "source-boundary-classes", status: "pass", evidence: "Manifest and review board expose all three source classes." },
  { id: "supplemental-primary-official-archive", status: "pass", evidence: `${supplemental.sources.length} official source pairs record URL/path/SHA-256/provenance.` },
  { id: "reconstruction-confined-to-unknown", status: "pass", evidence: "Reconstruction is a subset of unknown and disjoint from direct trace." },
  { id: "region-confidence", status: "pass", evidence: "Upper direct high; lower direct medium; occluded none; reconstructed low." },
  { id: "editable-artwork-slots", status: "pass", evidence: "Upper/lower external masks remain independently swappable." },
  { id: "blood-red-and-pink-suppression", status: "pass", evidence: `Hue ${imageReport.frontBloodRed.signedHueMedianDegrees}°; pink ${imageReport.frontBloodRed.pinkFraction}.` },
  { id: "lower-pattern-visible-open", status: "pass", evidence: `Lower red ${imageReport.lowerArtwork.redSurfaceFraction}; dark ${imageReport.lowerArtwork.darkPatternFraction}.` },
  { id: "geometry-digest-preserved", status: "pass", evidence: `Digest ${materialReport.geometryPreservation.digestAfterRenders}.` },
  { id: "diagnostic-second-light", status: "pass", evidence: "Second-light crystal response passed." },
  { id: "side-direct-reflection", status: "pass", evidence: `Reflection span ${imageReport.sideReflection.maximumReflectionSpanPx}px.` },
  { id: "no-clipping-or-emission", status: "pass", evidence: "No clipping; emission 0." },
  { id: "gate08-blocked", status: "pass", evidence: "Gate 08, Unity, build, install, and phone remain unchanged pending approval." },
];
stage.decision = null;
delete stage.staleReason;

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claimRecords]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claimRecords]);
}
manifest.currentState.diagnosis = "Gate 07 rev 4 已因来源边界要求被否决并不可变保留。rev 5 保持深血红、第二测试灯、侧面直接迎光和打开下片图案；精确产品图优先，直接 trace／遮挡未知／Chrome Hearts-style 重建三区分离，官方补充来源独立归档。等待视觉批准，不得进入 Gate 08、Unity 或手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  materialRevision: 5,
  supersedesMaterialRevision: 4,
  artifactIds: stage.artifactIds,
  sourceBoundaryClasses: stage.materialSpec.artwork.sourceBoundaryClasses,
  supplementalSourceCount: supplemental.sources.length,
  exactProductFirst: true,
  autoApproved: false,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[6].status,
  materialRevision: saved.stages[6].materialSpec.revision,
  artifacts: saved.stages[6].artifactIds.length,
}, null, 2));
