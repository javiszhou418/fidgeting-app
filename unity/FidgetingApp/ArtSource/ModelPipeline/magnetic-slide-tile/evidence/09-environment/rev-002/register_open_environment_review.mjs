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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-002";
const manifest = loadManifest(modelId);
const lightingStage = manifest.stages[7];
const stage = manifest.stages[8];
if (manifest.revision !== 72
  || lightingStage.status !== "approved"
  || stage.status !== "rejected"
  || stage.decision?.notes !== "Gate 09 rev 1 never showed the slide-open appearance.") {
  throw new Error("Expected rejected Gate 09 rev 1 at manifest revision 72.");
}

const definitions = [
  ["open-review-registrar", "registration-source", "register_open_environment_review.mjs"],
  ["open-environment-builder", "environment-source", "build_open_environment_revision.py"],
  ["open-environment-blend", "environment-blend", "magnetic-slide-tile-environment-open-r002.blend"],
  ["open-environment-validation", "validation-report", "open-environment-validation.json"],
  ["open-image-validator", "validation-source", "validate_open_images.py"],
  ["open-image-validation", "validation-report", "open-image-validation.json"],
  ["open-blender-audit-source", "validation-source", "audit_open_blender.py"],
  ["open-blender-audit", "validation-report", "blender-open-audit.json"],
  ["open-neutral-hero", "neutral-environment", "open-neutral-hero.png"],
  ["open-shipping-hero", "shipping-environment", "open-shipping-hero.png"],
  ["open-shipping-oblique", "environment-diagnostic", "open-shipping-oblique.png"],
  ["open-shipping-top", "environment-diagnostic", "open-shipping-top.png"],
  ["open-neutral-layer-closeup", "environment-diagnostic", "open-neutral-layer-closeup.png"],
  ["open-shipping-layer-closeup", "environment-diagnostic", "open-shipping-layer-closeup.png"],
  ["open-sequence-00", "environment-sequence", "sequence-00-00mm.png"],
  ["open-sequence-07", "environment-sequence", "sequence-01-07mm.png"],
  ["open-sequence-14", "environment-sequence", "sequence-02-14mm.png"],
  ["open-sequence-21", "environment-sequence", "sequence-03-21mm.png"],
  ["open-environment-comparison-board", "environment-review-board", "open-environment-comparison-board.png"],
  ["open-style-review-board", "environment-review-board", "open-style-review-board.png"],
  ["closed-open-sequence-board", "environment-review-board", "closed-open-sequence-board.png"],
  ["lower-artwork-visibility-board", "environment-review-board", "lower-artwork-visibility-board.png"],
  ["open-reflection-closeup-board", "environment-review-board", "open-reflection-closeup-board.png"],
  ["open-workbench-source", "validation-source", "capture_open_workbench.py"],
  ["open-workbench", "environment-review-board", "gate09-open-workbench.png"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-environment-blend-r001",
  "magnetic-slide-tile-environment-optimization-decision-r001",
  "magnetic-slide-tile-lighting-blend-r001",
  "magnetic-slide-tile-material-blend-r007",
  "magnetic-slide-tile-geometry-blend-r001",
];
const sourceClaimIds = [
  "slider-gate08-r001-user-approval-r001",
  "slider-unity-scene-reflection-plan-r001",
  "slider-wide-black-border-d65-silver-r007",
  "slider-blockout-point-axis-distinction-r003",
];
const environment = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/open-environment-validation.json`)));
const image = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/open-image-validation.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-open-audit.json`)));
if (![environment, image, audit].every((report) => report.pass)
  || environment.approvedContracts.openTravelMm !== 21
  || environment.approvedContracts.openRotationDegrees !== 0
  || image.checks.lowerPatternVisible !== true
  || audit.checks.mechanismConcealed !== true) {
  throw new Error("Gate 09 rev 2 open evidence did not pass.");
}

const records = definitions.map(([suffix, slot, file]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isSource = /\.(py|mjs)$/.test(file);
  const isBlend = file.endsWith(".blend");
  const isImage = file.endsWith(".png");
  return {
    id: `${modelId}-${suffix}-r002`,
    stageId: "09-environment",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "process",
    producer: {
      name: isBlend || isImage ? "Blender/Pillow slide-open evidence pipeline" : "Python/Node.js",
      version: isBlend || isImage ? audit.blender : "Python 3 / Node.js",
      recipe: `${root}/${isSource ? file : "build_open_environment_revision.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 09 rev 2 preserves rev 1 environment and all approved upstream contracts while adding unmistakable +21 mm slide-open evidence at 0° rotation.",
      sourceGate09Rev1Status: "rejected-incomplete-no-open-view",
      sourceGeometryDigest: environment.approvedContracts.closedGeometryDigest,
      openTravelMm: 21,
      openAxis: "+Y",
      openRotationDegrees: 0,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const revisionClaimId = "slider-gate09-r001-user-revision-request-r001";
manifest.claims.push({
  id: revisionClaimId,
  stageId: "09-environment",
  topic: "gate09-rev1-open-evidence-omission",
  statement: "用户指出 Gate 09 rev 1 从未展示 slide-open appearance，因此 rev 1 不完整并要求修订。rev 2 必须在 +Y 精确 21 mm、0° rotation 下展示 neutral/shipping 同机位 open 对比、shipping hero/oblique、near-top lower artwork、双片 silver reflection closeup 和 closed→open sequence。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["magnetic-slide-tile-environment-blend-r001"],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "requested-revision",
  deliveryState: "gate09-rev1-rejected-preserved-gate09-rev2-ready-for-review",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "open-environment-comparison-board",
  "open-style-review-board",
  "closed-open-sequence-board",
  "lower-artwork-visibility-board",
  "open-reflection-closeup-board",
  "open-shipping-hero",
  "open-shipping-top",
  "open-workbench",
].map((suffix) => `${modelId}-${suffix}-r002`);
stage.environmentSpec = {
  ...stage.environmentSpec,
  revision: 2,
  sourceRevision: {
    revision: 1,
    status: "rejected-incomplete",
    reason: "Gate 09 rev 1 never showed the slide-open appearance.",
    preservedAssetIds: manifest.assets
      .filter((asset) => asset.stageId === "09-environment" && asset.id.endsWith("-r001"))
      .map((asset) => asset.id),
  },
  openPose: {
    travelMm: 21,
    axis: "+Y",
    rotationDegrees: 0,
    translationMatrix: environment.pose.translationMatrixOpen,
    upperWorldMatrix: environment.pose.upperMatrixOpen,
    lowerWorldMatrix: environment.pose.lowerMatrixAfter,
    pointAxisClosedLocalMm: [0, -9.5, 0],
    pointAxisOpenWorldMm: environment.pose.pivotWorldMm,
  },
  cameras: environment.cameras,
  matchedOpenEnvironmentPair: environment.comparison,
  artwork: environment.invariants.artwork,
  imageMetrics: image.metrics,
  sequenceMetrics: image.sequence,
  imageDifferences: image.differences,
  blenderReflectionDeliveryState: "preview-only-not-unity-integration",
  geometryOrLodChanged: false,
};
stage.validations = [
  { id: "rev1-rejected-preserved", status: "pass", evidence: "Gate 09 rev 1 is rejected as incomplete with exact note “Gate 09 rev 1 never showed the slide-open appearance.” Its assets and hashes remain immutable." },
  { id: "exact-open-pose", status: "pass", evidence: "UpperTranslation is [0,21,0] mm; upper world Y is 21 mm; translation, pivot, and upper local rotations remain 0°." },
  { id: "fixed-lower-plane", status: "pass", evidence: "Lower matrix remains identity translation except Z=-3 mm in closed, intermediate, and open frames." },
  { id: "geometry-material-light-environment-preserved", status: "pass", evidence: `Local mesh hash ${environment.invariants.localMeshHashAfter}; shipping material hashes, four-light rig, reflection-card transforms, shipping world hash, and ground material are unchanged.` },
  { id: "matched-open-environment-pair", status: "pass", evidence: `Neutral/shipping open Hero share ${environment.comparison.neutralShippingCamera.name}, +21 mm pose, 0° rotation, EV 0, 6504 K white balance, and identical lights.` },
  { id: "open-style-unmistakable", status: "pass", evidence: `Open sequence shows ${image.sequence.closedRedArtworkPixels} → ${image.sequence.openRedArtworkPixels} red artwork pixels, ratio ${image.sequence.openToClosedArtworkRatio}; closed-to-open changed-pixel fraction ${image.differences.closedToOpen.fractionPixelsMaxDeltaAbove12}.` },
  { id: "lower-artwork-visible", status: "pass", evidence: `Lower ROI has ${image.metrics.shippingTop.lowerArtwork.redArtworkPixels} red artwork pixels, contrast ${image.metrics.shippingTop.lowerArtwork.contrastRatio}, Laplacian ${image.metrics.shippingTop.lowerArtwork.laplacianVariance}, and ${image.metrics.shippingTop.lowerArtwork.cannyEdgePixels} edges.` },
  { id: "independent-artwork-slots", status: "pass", evidence: "Artwork_Upper and Artwork_Lower remain separate node groups and external paths; both retain the approved clean-mask SHA-256." },
  { id: "mechanism-concealed", status: "pass", evidence: "ConcealedCircularEnvelope_Metadata remains a hidden EMPTY with geometry=none; no internal mechanism mesh renders." },
  { id: "silver-neutral-reflective", status: "pass", evidence: `Hero silver body L*/C*/b* ${image.metrics.shippingHero.silver.silverBody.medianLStar}/${image.metrics.shippingHero.silver.silverBody.medianCStar}/${image.metrics.shippingHero.silver.silverBody.medianBStar}; bright reflection L* ${image.metrics.shippingHero.silver.brightReflection.medianLStar}; open layer environment delta ${image.differences.neutralShippingLayer.meanAbsoluteChannelDelta}.` },
  { id: "blood-red-no-pink", status: "pass", evidence: `Hero hue ${image.metrics.shippingHero.bloodRed.signedHueMedianDegrees}°; pink ${image.metrics.shippingHero.bloodRed.pinkFraction}; blood-red ${image.metrics.shippingHero.bloodRed.bloodRedFraction}.` },
  { id: "clipping-and-emission", status: "pass", evidence: `Maximum reviewed clipping remains below 0.014%; all approved shipping material emission strengths remain 0.` },
  { id: "gate09-only", status: "pass", evidence: "No Gate 10, export, Unity, Reflection Probe, runtime, Haptic, build, install, or phone push work was performed." },
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
manifest.currentState.visualApproval = "gate09-environment-open-rev2-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 09 rev 1 因未展示 slide-open appearance 已按用户原文标记 rejected/incomplete 并不可变保留。Gate 09 rev 2 在完全不改 geometry、material、Gate 08 lighting 或 Gate 09 environment 的前提下，新增 +Y 精确 21 mm、0° rotation 的 neutral/shipping open 对比、shipping hero/oblique、near-top lower artwork、双片 reflection closeup 和 0/7/14/21 mm sequence。下片固定、机构隐藏、上下 artwork 独立。当前等待 Gate 09 rev 2 视觉批准，未进入 Gate 10，未推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "09-environment",
  environmentRevision: 2,
  sourceRevision: 1,
  sourceRevisionStatus: "rejected-incomplete",
  openTravelMm: 21,
  openAxis: "+Y",
  openRotationDegrees: 0,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  geometryDigest: environment.approvedContracts.closedGeometryDigest,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  stageRevision: saved.stages[8].revision,
  status: saved.stages[8].status,
  artifacts: saved.stages[8].artifactIds.length,
  reviewArtifacts: saved.stages[8].reviewArtifactIds.length,
  revisionClaimId,
}, null, 2));
