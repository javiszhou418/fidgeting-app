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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-007";
const manifest = loadManifest(modelId);
const stage = manifest.stages[6];
if (manifest.revision !== 63 || stage.status !== "rejected" || stage.materialSpec?.revision !== 6) {
  throw new Error("Expected rejected Gate 07 rev 6 at manifest revision 63.");
}

const definitions = [
  ["review-registrar", "registration-source", "register_border_daylight_review.mjs"],
  ["artwork-preparer", "artwork-source", "prepare_wide_border_artwork.py"],
  ["artwork-upper-mask", "artwork-mask", "artwork-upper-mask.png"],
  ["artwork-lower-mask", "artwork-mask", "artwork-lower-mask.png"],
  ["artwork-border-mask", "artwork-mask", "artwork-top-perimeter-border-mask.png"],
  ["border-settings", "artwork-config", "border-settings.json"],
  ["artwork-config", "artwork-config", "artwork-layers.json"],
  ["artwork-lineage", "source-manifest", "artwork-lineage.json"],
  ["artwork-border-validation", "validation-report", "artwork-border-validation.json"],
  ["top-face-boundary-diagram", "material-process-board", "top-face-boundary-diagram.png"],
  ["blood-red-analysis", "color-analysis", "blood-red-source-analysis.json"],
  ["material-builder", "material-source", "build_wide_border_d65_silver.py"],
  ["material-blend", "material-blend", "magnetic-slide-tile-material-r007.blend"],
  ["material-validation", "validation-report", "material-validation.json"],
  ["material-board", "material-board", "neutral-pbr-material-board.png"],
  ["material-closeup", "material-closeup", "neutral-pbr-material-closeup.png"],
  ["blood-red-closeup", "material-closeup", "blood-red-closeup.png"],
  ["material-open-artwork", "material-open-artwork", "open-slide-lower-artwork.png"],
  ["material-process-board", "material-process-board", "editable-artwork-layer-board.png"],
  ["rev6-border-same-camera", "material-comparison", "rev6-border-same-camera.png"],
  ["wide-border-same-camera", "material-comparison", "wide-border-same-camera.png"],
  ["black-border-comparison", "material-comparison", "black-border-comparison-same-camera.png"],
  ["rev6-silver-neutral-studio", "material-comparison", "rev6-silver-neutral-studio-same-camera.png"],
  ["rev7-silver-neutral-studio", "material-comparison", "daylight-neutral-silver-neutral-studio-same-camera.png"],
  ["neutral-studio-silver-comparison", "material-comparison", "neutral-studio-silver-comparison.png"],
  ["silver-environment-diagnosis", "material-comparison", "silver-environment-diagnosis-same-camera.png"],
  ["outdoor-d65-hero", "material-side-reflection", "outdoor-d65-hero-neutral-card.png"],
  ["outdoor-d65-side", "material-side-reflection", "outdoor-d65-silver-side-direct.png"],
  ["material-image-validator", "validation-source", "validate_border_daylight_silver.py"],
  ["material-image-validation", "validation-report", "image-material-validation.json"],
  ["material-blender-audit-source", "validation-source", "audit_blender_rev7.py"],
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
  "magnetic-slide-tile-material-blend-r006",
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
const borderReport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/artwork-border-validation.json`)));
const blenderAudit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-audit.json`)));
const artwork = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/artwork-layers.json`)));
const borderSettings = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/border-settings.json`)));
if (![materialReport, imageReport, borderReport, blenderAudit].every((report) => report.pass)
  || materialReport.materialRevision !== 7
  || artwork.reuseClass !== "user-authorized-prior-material-design-reuse-with-editable-border-overlay") {
  throw new Error("Gate 07 rev 7 evidence did not pass.");
}

const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isSource = /\.(py|mjs)$/.test(file);
  const isJson = file.endsWith(".json");
  const isBlend = file.endsWith(".blend");
  return {
    id: `${modelId}-${suffix}-r007`,
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
      recipe: `${root}/${isSource || isJson ? file : "build_wide_border_d65_silver.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 07 rev 7 adds a parameterized full-perimeter black top-face border and D65 daylight-neutral silver diagnostics. It preserves rev 6 geometry, blood red, and rev 2/3 clean motif lineage.",
      userClaimIds: sourceClaimIds,
      lineageAssetId: "magnetic-slide-tile-motif-mask-r002",
      lineageSha256: artwork.slots.Artwork_Upper.maskSha256,
      borderMaskSha256: artwork.topPerimeterBorder.maskSha256,
      notNewExactTraceClaim: true,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const userClaimId = "slider-wide-black-border-d65-silver-r007";
manifest.claims.push({
  id: userClaimId,
  stageId: "07-material",
  topic: "wide-black-top-perimeter-and-daylight-neutral-silver",
  statement: "用户否决／要求修订 Gate 07 rev 6：黑色装饰顶面边框加宽并连续延伸到顶面完整外周；结构竖直侧壁和金属 rim 保持 silver。边框必须通过可编辑 mask／参数实现，不得改 geometry。silver 须在 D65 日光诊断下呈明亮中性银白，低蓝偏、无 clipping、无 emission；Gate 08 仍阻塞。",
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
  "black-border-comparison",
  "top-face-boundary-diagram",
  "silver-environment-diagnosis",
  "outdoor-d65-hero",
  "outdoor-d65-side",
  "blood-red-closeup",
  "material-open-artwork",
  "material-process-board",
  "material-board",
  "material-closeup",
  "material-workbench",
].map((suffix) => `${modelId}-${suffix}-r007`);
stage.materialSpec = {
  ...stage.materialSpec,
  revision: 7,
  supersedesRevision: 6,
  recommendedVariant: "blood-red-clean-motif-wide-black-top-perimeter-daylight-neutral-silver",
  zoneIds: [
    "polished-pure-silver-visual-target-exterior",
    "deep-blood-red-crystal-face",
    "blackened-top-face-full-perimeter",
  ],
  artwork: {
    configAssetId: `${modelId}-artwork-config-r007`,
    lineageAssetId: `${modelId}-artwork-lineage-r007`,
    sourceAssetId: "magnetic-slide-tile-motif-mask-r002",
    sourceMaterialRevision: 2,
    unchangedInMaterialRevisions: [3, 6, 7],
    sourceSha256: artwork.slots.Artwork_Upper.maskSha256,
    upperMaskAssetId: `${modelId}-artwork-upper-mask-r007`,
    lowerMaskAssetId: `${modelId}-artwork-lower-mask-r007`,
    nodeGroups: ["Artwork_Upper", "Artwork_Lower"],
    independentlySwappable: true,
    initialHashesIntentionallyEqual: true,
    losslessPriorDesignReuse: true,
    reuseClass: artwork.reuseClass,
    notNewExactTraceClaim: true,
    geometryRebuildRequired: false,
    topPerimeterBorder: {
      maskAssetId: `${modelId}-artwork-border-mask-r007`,
      settingsAssetId: `${modelId}-border-settings-r007`,
      maskSha256: artwork.topPerimeterBorder.maskSha256,
      compositionOperation: artwork.topPerimeterBorder.compositionOperation,
      widthPx: borderSettings.borderWidthPx,
      widthFractionMinorAxis: borderSettings.borderWidthFractionMinorAxis,
      approxVisualWidthMm: borderSettings.approxVisualWidthMm,
      outerPerimeterInsetPx: borderSettings.outerPerimeterInsetPx,
      appliesTo: borderSettings.appliesTo,
      blackZone: borderSettings.topologyBoundary.black,
      silverZone: borderSettings.topologyBoundary.silver,
      independentlyEditable: true,
    },
  },
  silverAppearance: {
    exactProductMaterial: "steel",
    targetAppearance: "polished-pure-silver",
    productionMaterialClaim: false,
    material: "M07R7_DaylightNeutralPolishedSilver",
    baseColor: [0.97, 0.965, 0.94, 1],
    metallic: 1,
    roughness: 0.03,
    anisotropy: 0.14,
    anisotropyRotation: 0.08,
    coatWeight: 0.06,
    coatRoughness: 0.02,
    emissionStrength: 0,
    d65Diagnostic: materialReport.diagnosticLighting.d65Daylight,
  },
  imageMetrics: imageReport,
  userClaimId,
};
stage.validations = [
  { id: "rev6-rejected-preserved", status: "pass", evidence: "Rev 6 remains immutable; rev 7 is additive." },
  { id: "full-black-top-perimeter", status: "pass", evidence: `External mask reaches 0 px inset on all sides; width ${borderSettings.borderWidthPx}px (${(borderSettings.borderWidthFractionMinorAxis * 100).toFixed(2)}%, ≈${borderSettings.approxVisualWidthMm} mm).` },
  { id: "black-silver-boundary", status: "pass", evidence: "Black applies only to the decorative top-face perimeter; structural vertical side wall and visible rim remain silver." },
  { id: "lossless-clean-mask-lineage", status: "pass", evidence: `Upper/lower motif bytes remain rev 2/3 SHA-256 ${artwork.slots.Artwork_Upper.maskSha256}.` },
  { id: "editable-artwork-and-border", status: "pass", evidence: "Upper/lower motif paths are independent; full-perimeter border is a third external mask and parameterized setting." },
  { id: "rendered-border-width", status: "pass", evidence: `Dark top-face fraction ${imageReport.borderComparison.rev6.darkFraction} → ${imageReport.borderComparison.rev7.darkFraction}.` },
  { id: "silver-blue-bias-diagnosis", status: "pass", evidence: `Rev 6 blue-biased fraction ${imageReport.silverDiagnosis.rev6OriginalBlueStudio.blueBiasBelowMinus2Fraction}; rev 7 neutral studio median b* ${imageReport.silverDiagnosis.rev7ShaderNeutralStudio.medianBStar}.` },
  { id: "d65-bright-neutral-silver", status: "pass", evidence: `Hero L*/C*/b* ${imageReport.d65Silver.hero.medianLStar}/${imageReport.d65Silver.hero.medianCStar}/${imageReport.d65Silver.hero.medianBStar}; side ${imageReport.d65Silver.sideDirect.medianLStar}/${imageReport.d65Silver.sideDirect.medianCStar}/${imageReport.d65Silver.sideDirect.medianBStar}.` },
  { id: "d65-clipping", status: "pass", evidence: `Hero/side clip ${imageReport.d65Silver.hero.roiClipAbove250Fraction}/${imageReport.d65Silver.sideDirect.roiClipAbove250Fraction}.` },
  { id: "d65-reference-cards", status: "pass", evidence: `White/gray/black luma ${imageReport.d65ReferenceCards.white80}/${imageReport.d65ReferenceCards.gray18}/${imageReport.d65ReferenceCards.black}.` },
  { id: "blood-red-no-pink", status: "pass", evidence: `Hue ${imageReport.bloodRed.signedHueMedianDegrees}°; pink ${imageReport.bloodRed.pinkFraction}; blood red ${imageReport.bloodRed.bloodRedFraction}.` },
  { id: "open-lower-pattern", status: "pass", evidence: `Lower Laplacian ${imageReport.openLowerArtwork.laplacianVariance}; ${imageReport.openLowerArtwork.cannyEdgePixels} edge pixels.` },
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
manifest.currentState.diagnosis = "Gate 07 rev 6 已按用户要求否决并不可变保留。rev 7 以独立 64 px（10.32%，约 3.2 mm）external mask 将黑色装饰边框连续延伸到顶面 0 px 外周，结构竖直侧壁／rim 保持 silver，geometry digest 不变。rev 6 的蓝偏主要来自 mirror metal 反射蓝色 studio world；rev 7 改用中性 studio，并用 D65 6504 K、固定 EV 0、neutral ground／reference cards 验证 bright silver-white。等待 Gate 07 视觉批准；Gate 08、Unity 和手机仍阻塞。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  materialRevision: 7,
  supersedesMaterialRevision: 6,
  artifactIds: stage.artifactIds,
  reusedMaskAssetId: "magnetic-slide-tile-motif-mask-r002",
  reusedMaskSha256: artwork.slots.Artwork_Upper.maskSha256,
  borderMaskSha256: artwork.topPerimeterBorder.maskSha256,
  borderWidthPx: borderSettings.borderWidthPx,
  borderOuterInsetPx: borderSettings.outerPerimeterInsetPx,
  d65Kelvin: materialReport.diagnosticLighting.d65Daylight.correlatedColorTemperatureKelvin,
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
