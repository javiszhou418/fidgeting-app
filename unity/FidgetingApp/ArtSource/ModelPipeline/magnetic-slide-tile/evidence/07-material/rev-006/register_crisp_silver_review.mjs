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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-006";
const manifest = loadManifest(modelId);
const stage = manifest.stages[6];
if (manifest.revision !== 60 || stage.status !== "rejected" || stage.materialSpec?.revision !== 5) {
  throw new Error("Expected rejected Gate 07 rev 5 at manifest revision 60.");
}

const definitions = [
  ["review-registrar", "registration-source", "register_crisp_silver_review.mjs"],
  ["artwork-preparer", "artwork-source", "prepare_crisp_artwork.py"],
  ["artwork-upper-mask", "artwork-mask", "artwork-upper-mask.png"],
  ["artwork-lower-mask", "artwork-mask", "artwork-lower-mask.png"],
  ["artwork-config", "artwork-config", "artwork-layers.json"],
  ["artwork-lineage", "source-manifest", "artwork-lineage.json"],
  ["artwork-lineage-validation", "validation-report", "artwork-lineage-validation.json"],
  ["artwork-lineage-board", "material-process-board", "mask-lineage-sharpness-board.png"],
  ["blood-red-analysis", "color-analysis", "blood-red-source-analysis.json"],
  ["material-builder", "material-source", "build_crisp_blood_red_pure_silver.py"],
  ["material-blend", "material-blend", "magnetic-slide-tile-material-r006.blend"],
  ["material-validation", "validation-report", "material-validation.json"],
  ["material-front", "material-front", "neutral-front-blood-red.png"],
  ["material-board", "material-board", "neutral-pbr-material-board.png"],
  ["material-closeup", "material-closeup", "neutral-pbr-material-closeup.png"],
  ["material-open-artwork", "material-open-artwork", "open-slide-lower-artwork.png"],
  ["material-process-board", "material-process-board", "editable-artwork-layer-board.png"],
  ["mask-noisy-same-camera", "material-comparison", "rev5-noisy-mask-same-camera.png"],
  ["mask-crisp-same-camera", "material-comparison", "restored-crisp-mask-same-camera.png"],
  ["mask-comparison", "material-comparison", "mask-comparison-same-camera.png"],
  ["silver-gray-same-camera", "material-comparison", "gray-edge-same-camera.png"],
  ["silver-pure-same-camera", "material-comparison", "pure-silver-edge-same-camera.png"],
  ["silver-comparison", "material-comparison", "silver-comparison-same-camera.png"],
  ["material-second-light", "material-second-light", "diagnostic-second-light-crystal-response.png"],
  ["material-side-reflection", "material-side-reflection", "diagnostic-side-white-card-reflection.png"],
  ["material-side-reflection-alias", "material-side-reflection", "diagnostic-side-direct-reflection.png"],
  ["silver-reflection-cards", "material-side-reflection", "diagnostic-silver-reflection-cards.png"],
  ["material-image-validator", "validation-source", "validate_crisp_silver.py"],
  ["material-image-validation", "validation-report", "image-material-validation.json"],
  ["material-blender-audit-source", "validation-source", "audit_blender_rev6.py"],
  ["material-blender-audit", "validation-report", "blender-audit.json"],
  ["workbench-capture-source", "validation-source", "capture_gate07_workbench.py"],
  ["material-workbench", "material-process-board", "gate07-workbench.png"],
  ["fixed-view-capture-report", "validation-report", "fixed-views/capture-report.json"],
  ["fixed-view-wrapper-report", "validation-report", "fixed-views/capture-wrapper-report.json"],
  ...["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"]
    .map((view) => [`fixed-${view}`, `material-fixed-${view}`, `fixed-views/${view}.png`]),
];
const sourceAssetIds = [
  "magnetic-slide-tile-geometry-blend-r001",
  "magnetic-slide-tile-motif-mask-r002",
  "slider-intake-haloo-official-04",
  "slider-intake-nxedc-ref-01",
];
const sourceClaimIds = [
  "slider-analysis-claim-material-language",
  "slider-blockout-point-axis-distinction-r003",
  "slider-ratchet-30-detent-requirement-r001",
];
const materialReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/material-validation.json`)));
const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/image-material-validation.json`)));
const lineageReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/artwork-lineage-validation.json`)));
const blenderAudit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-audit.json`)));
const artwork = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/artwork-layers.json`)));
if (![materialReport, imageReport, lineageReport, blenderAudit].every((report) => report.pass)
  || materialReport.materialRevision !== 6
  || artwork.reuseClass !== "user-authorized-prior-material-design-reuse") {
  throw new Error("Gate 07 rev 6 evidence did not pass.");
}

const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isSource = /\.(py|mjs)$/.test(file);
  const isJson = file.endsWith(".json");
  const isBlend = file.endsWith(".blend");
  return {
    id: `${modelId}-${suffix}-r006`,
    stageId: "07-material",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "process",
    producer: {
      name: isBlend || file.endsWith(".png") ? "Blender/Pillow evidence pipeline" : "Python/Node.js",
      version: isBlend || file.endsWith(".png") ? materialReport.blender : "Python 3 / Node.js",
      recipe: `${root}/${isSource || isJson ? file : "build_crisp_blood_red_pure_silver.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 07 rev 6 restores the registered rev 2/3 clean motif by explicit user authority, retains blood red, and applies a polished pure-silver appearance target without claiming silver production material.",
      userClaimIds: sourceClaimIds,
      lineageAssetId: "magnetic-slide-tile-motif-mask-r002",
      lineageSha256: artwork.slots.Artwork_Upper.maskSha256,
      notNewExactTraceClaim: true,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const userClaimId = "slider-clean-motif-pure-silver-r006";
manifest.claims.push({
  id: userClaimId,
  stageId: "07-material",
  topic: "clean-prior-motif-blood-red-polished-pure-silver",
  statement: "用户否决 Gate 07 rev 5 的噪点式直接 trace，授权无损复用 Gate 07 rev 2／3 的完整清晰 motif，并保持深血红晶体。外框、边缘和可见侧面改为高抛光 pure-silver 视觉目标；准确产品来源仍只确认 Steel，pure silver 不构成生产材料声明。上下 artwork 保持独立外部槽。",
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
  "artwork-lineage-board",
  "mask-comparison",
  "silver-comparison",
  "silver-reflection-cards",
  "material-side-reflection",
  "material-open-artwork",
  "material-process-board",
  "material-board",
  "material-closeup",
  "material-workbench",
].map((suffix) => `${modelId}-${suffix}-r006`);
stage.materialSpec = {
  ...stage.materialSpec,
  revision: 6,
  supersedesRevision: 5,
  recommendedVariant: "blood-red-clean-prior-motif-polished-pure-silver",
  zoneIds: [
    "polished-pure-silver-visual-target-exterior",
    "deep-blood-red-crystal-face",
  ],
  artwork: {
    configAssetId: `${modelId}-artwork-config-r006`,
    lineageAssetId: `${modelId}-artwork-lineage-r006`,
    sourceAssetId: "magnetic-slide-tile-motif-mask-r002",
    sourceMaterialRevision: 2,
    unchangedInMaterialRevision: 3,
    sourceSha256: artwork.slots.Artwork_Upper.maskSha256,
    upperMaskAssetId: `${modelId}-artwork-upper-mask-r006`,
    lowerMaskAssetId: `${modelId}-artwork-lower-mask-r006`,
    nodeGroups: ["Artwork_Upper", "Artwork_Lower"],
    independentlySwappable: true,
    initialHashesIntentionallyEqual: true,
    losslessPriorDesignReuse: true,
    reuseClass: artwork.reuseClass,
    notNewExactTraceClaim: true,
    geometryRebuildRequired: false,
  },
  silverAppearance: {
    exactProductMaterial: "steel",
    targetAppearance: "polished-pure-silver",
    productionMaterialClaim: false,
    material: "M07R6_PolishedPureSilver_VisualTarget",
    baseColor: [0.94, 0.94, 0.92, 1],
    metallic: 1,
    roughness: 0.045,
    anisotropy: 0.22,
    anisotropyRotation: 0.08,
    coatWeight: 0.12,
    coatRoughness: 0.025,
    emissionStrength: 0,
  },
  imageMetrics: imageReport,
  userClaimId,
};
stage.validations = [
  { id: "rev5-rejected-preserved", status: "pass", evidence: "Rev 5 remains immutable; rev 6 is additive." },
  { id: "lossless-clean-mask-lineage", status: "pass", evidence: `Upper/lower bytes equal rev 2/3 SHA-256 ${artwork.slots.Artwork_Upper.maskSha256}.` },
  { id: "not-new-exact-trace", status: "pass", evidence: "Lineage is user-authorized prior design reuse, not a new exact-product trace claim." },
  { id: "editable-artwork-slots", status: "pass", evidence: "Upper/lower use distinct external paths and node groups." },
  { id: "pattern-sharpness", status: "pass", evidence: `Laplacian variance ${imageReport.motifSharpness.rev5Rejected.laplacianVariance} → ${imageReport.motifSharpness.rev6Restored.laplacianVariance}; edges ${imageReport.motifSharpness.rev5Rejected.cannyEdgePixels} → ${imageReport.motifSharpness.rev6Restored.cannyEdgePixels}.` },
  { id: "open-lower-pattern", status: "pass", evidence: `Lower Laplacian ${imageReport.openLowerArtwork.laplacianVariance}; ${imageReport.openLowerArtwork.cannyEdgePixels} edge pixels.` },
  { id: "blood-red-no-pink", status: "pass", evidence: `Hue ${imageReport.bloodRed.signedHueMedianDegrees}°; pink ${imageReport.bloodRed.pinkFraction}; blood red ${imageReport.bloodRed.bloodRedFraction}.` },
  { id: "pure-silver-claim-boundary", status: "pass", evidence: "Steel remains the exact-product claim; pure silver is appearance-only." },
  { id: "silver-neutral-highlight", status: "pass", evidence: `Median neutral luma ${imageReport.silverComparison.rev5Gray.neutralMedianLuma} → ${imageReport.silverComparison.rev6PureSilverTarget.neutralMedianLuma}; clip ${imageReport.silverComparison.rev6PureSilverTarget.neutralClipAbove250Fraction}.` },
  { id: "calibrated-reflection-cards", status: "pass", evidence: `White/gray/black render luma ${imageReport.reflectionCards.white}/${imageReport.reflectionCards.gray}/${imageReport.reflectionCards.black}.` },
  { id: "side-white-card-reflection", status: "pass", evidence: `Neutral reflection span ${imageReport.sideWhiteCard.maximumNeutralHighlightSpanPx}px.` },
  { id: "no-emission", status: "pass", evidence: "Crystal and silver emission strengths are 0." },
  { id: "geometry-and-mechanism-preserved", status: "pass", evidence: `Digest ${materialReport.geometryPreservation.digestAfterRenders}; hidden mechanism unchanged; 30 detents specified-only.` },
  { id: "real-workbench-and-fixed-views", status: "pass", evidence: "Real Blender Workbench screenshot and ten fixed views were captured." },
  { id: "gate08-blocked", status: "pass", evidence: "No Gate 08, Unity, runtime, Haptic, build, install, or phone work." },
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
manifest.currentState.diagnosis = "Gate 07 rev 5 已因噪点式图案被否决并不可变保留。rev 6 无损复用 rev 2／3 清晰完整 motif（上下独立槽），保持深血红晶体，并将外框／边缘／侧面改为 user-authorized polished pure-silver 视觉目标；准确产品材料仍只声明 Steel。真实 Blender PBR、同机位对比、反射卡、侧面白卡、打开下片、Workbench 与 fixed views 均已验证。等待视觉批准；不得进入 Gate 08、Unity 或手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  materialRevision: 6,
  supersedesMaterialRevision: 5,
  artifactIds: stage.artifactIds,
  reusedMaskAssetId: "magnetic-slide-tile-motif-mask-r002",
  reusedMaskSha256: artwork.slots.Artwork_Upper.maskSha256,
  silverAppearanceTarget: "polished-pure-silver",
  exactProductMaterialClaim: "steel",
  autoApproved: false,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[6].status,
  materialRevision: saved.stages[6].materialSpec.revision,
  artifacts: saved.stages[6].artifactIds.length,
}, null, 2));
