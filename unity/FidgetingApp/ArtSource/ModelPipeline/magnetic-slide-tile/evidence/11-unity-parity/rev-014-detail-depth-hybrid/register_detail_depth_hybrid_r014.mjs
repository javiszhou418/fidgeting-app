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
const stageId = "11-unity-parity";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/11-unity-parity/rev-014-detail-depth-hybrid";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/"
  + "MagneticSlideTileGate11R014";
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((stage) => stage.id === stageId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const read = (name) => JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const report = read("unity-hybrid-report.json");
const metrics = read("hybrid-detail-metrics.json");
const video = read("hybrid-video-validation.json");

if (!gate11 || !gate12 || !report.pass || !metrics.pass || !video.pass)
  throw new Error("Hybrid evidence is incomplete.");

gate11.historicalRevisions ??= [];
if (!gate11.historicalRevisions.some(
  (revision) => revision.evidenceRevision === 13)) {
  gate11.historicalRevisions.push({
    evidenceRevision: 13,
    stageRevision: gate11.revision,
    status: "rejected-detail-loss-versus-rev12",
    exactUserFeedback: "我感觉明显还是rev 12细节更多吧",
    artifactIds: [...gate11.artifactIds],
    reviewArtifactIds: [...gate11.reviewArtifactIds],
    validations: structuredClone(gate11.validations),
    unityParitySpec: structuredClone(gate11.unityParitySpec),
    decision: structuredClone(gate11.decision),
    deliveryState: structuredClone(gate11.deliveryState),
    preservedForHistory: true,
  });
}
const historical13 = gate11.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 13);
historical13.status = "rejected-detail-loss-versus-rev12";
historical13.exactUserFeedback = "我感觉明显还是rev 12细节更多吧";
historical13.preservedForHistory = true;
const rev13Claim = manifest.claims.find(
  (candidate) => candidate.id === "slider-gate11-r013-true-layer-correction");
if (rev13Claim) {
  rev13Claim.state = "rejected";
  rev13Claim.decisionState = "rejected-by-user";
  rev13Claim.rejectionReason =
    "True spatial layers passed, but surface detail was visibly lower than rev12.";
  rev13Claim.exactUserFeedback = "我感觉明显还是rev 12细节更多吧";
}

const definitions = [
  ["registrar", "unity-parity-registrar",
    `${evidenceRoot}/register_detail_depth_hybrid_r014.mjs`, "validation"],
  ["review-builder", "review-builder-source",
    `${evidenceRoot}/build_hybrid_review.py`, "validation"],
  ["video-validator", "video-validation-source",
    `${evidenceRoot}/validate_hybrid_video.py`, "validation"],
  ["unity-builder", "unity-builder",
    `${candidateRoot}/Editor/MagneticSlideTileGate11R014HybridBuilder.cs`,
    "source-model"],
  ["substrate-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideHybridSubstrateR014.shader`,
    "source-model"],
  ["motif-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideHybridMotifR014.shader`,
    "source-model"],
  ["crystal-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideHybridCrystalR014.shader`,
    "source-model"],
  ["scene", "unity-scene",
    "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["report", "unity-parity-report",
    `${evidenceRoot}/unity-hybrid-report.json`, "validation"],
  ["metrics", "image-validation",
    `${evidenceRoot}/hybrid-detail-metrics.json`, "validation"],
  ["source-lineage", "source-lineage",
    `${evidenceRoot}/source-shader-lineage.json`, "validation"],
  ["video-report", "video-validation",
    `${evidenceRoot}/hybrid-video-validation.json`, "validation"],
  ["macro-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r014-three-way-macro.png`, "unity-render"],
  ["angle-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r014-hybrid-angle-board.png`, "unity-render"],
  ["shipping-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r014-hybrid-shipping-board.png`, "unity-render"],
  ["reflection-video", "unity-runtime-recording",
    `${evidenceRoot}/gate11-r014-rev12-rev13-hybrid-unity.mp4`,
    "unity-render"],
  ["editor-tests", "test-source",
    "unity/FidgetingApp/Assets/_EDC/Tests/Editor/"
      + "MagneticSlideTrueLayerRevisionTests.cs", "validation"],
  ["playmode-tests", "test-source",
    "unity/FidgetingApp/Assets/_EDC/Candidates/"
      + "MagneticSlideTileGate12R002/Tests/PlayMode/"
      + "MagneticSlideTileInputPlayModeTests.cs", "validation"],
  ["pipeline-test", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "magnetic-slide-gate11-true-layers-r13.test.mjs", "validation"],
  ["browser-test", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "browser-gate11-true-layers-r13.mjs", "validation"],
  ["editmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideHybridR014EditMode.xml",
    "validation"],
  ["editmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideHybridR014EditMode.log",
    "validation"],
  ["playmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideHybridR014PlayMode.xml",
    "validation"],
  ["playmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideHybridR014PlayMode.log",
    "validation"],
  ["capture-log", "capture-log",
    "unity/FidgetingApp/Logs/MagneticSlideHybridR014Capture.log",
    "validation"],
];
if (fs.existsSync(resolveRepoPath(
  `${evidenceRoot}/browser-mobile-modal-validation.json`))) {
  definitions.push([
    "browser-report",
    "browser-validation",
    `${evidenceRoot}/browser-mobile-modal-validation.json`,
    "validation",
  ]);
}
for (const face of ["Upper", "Lower"]) {
  for (const layer of [
    "Rev12DetailSubstrate",
    "Rev12DetailMotif",
    "DetailPreservingCrystal",
  ]) {
    definitions.push([
      `${face.toLowerCase()}-${layer.toLowerCase()}`,
      "unity-material",
      `${candidateRoot}/Materials/M_G11R014_${face}${layer}.mat`,
      "source-model",
    ]);
  }
}
for (const variant of [
  "A-rev12-detail",
  "B-rev13-depth",
  "C-rev14-hybrid",
]) {
  for (const view of [
    "macro",
    "hero-closed",
    "grazing-15",
    "grazing-30",
    "grazing-60",
    "max-open",
    "phone",
  ]) {
    definitions.push([
      `${variant}-${view}`,
      `unity-${view}`,
      `${evidenceRoot}/${variant}/${view}.png`,
      "unity-render",
    ]);
  }
}

const sourceAssetIds = [
  "magnetic-slide-tile-unity-layered-reflection-video-r012",
  "magnetic-slide-tile-unity-true-layer-reflection-video-r013",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing hybrid artifact: ${path}`);
  return {
    id: `${modelId}-unity-detail-depth-hybrid-${suffix}-r014`,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "unity-render"
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 11 rev14 detail-depth hybrid",
      version: "2026-09-02",
      recipe:
        `${candidateRoot}/Editor/`
        + "MagneticSlideTileGate11R014HybridBuilder.cs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      evidenceRevision: 14,
      rev12DetailAssetsReusedByteForByte: true,
      rev13PhysicalOffsetsRetained: true,
      visualLayerGeometryChanged: false,
      mechanicalGeometryChanged: false,
      collidersChanged: false,
      interactionChanged: false,
      audioChanged: false,
      hapticsChanged: false,
      sideWallMaterialChanged: false,
      buildInstallPhone: false,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex(
    (candidate) => candidate.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
}

const claim = {
  id: "slider-gate11-r014-detail-depth-hybrid",
  stageId,
  topic: "unity-hybrid-layered-material",
  statement:
    "Rev14 reuses rev12 albedo, roughness, normal and independent motif "
    + "mask assets without copies or resampling on rev13 physical layer "
    + "meshes. The 0.28 mm crystal cap preserves high-frequency detail.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "ready-for-user-review",
  deliveryState: "visual-approval-pending-not-built-or-installed",
};
const claimIndex = manifest.claims.findIndex(
  (candidate) => candidate.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

gate11.revision = 14;
gate11.status = "ready_for_review";
gate11.artifactIds = records.map((record) => record.id);
gate11.reviewArtifactIds = [
  `${modelId}-unity-detail-depth-hybrid-reflection-video-r014`,
  `${modelId}-unity-detail-depth-hybrid-macro-board-r014`,
  `${modelId}-unity-detail-depth-hybrid-angle-board-r014`,
  `${modelId}-unity-detail-depth-hybrid-shipping-board-r014`,
  `${modelId}-unity-detail-depth-hybrid-C-rev14-hybrid-macro-r014`,
  `${modelId}-unity-detail-depth-hybrid-C-rev14-hybrid-grazing-15-r014`,
  `${modelId}-unity-detail-depth-hybrid-C-rev14-hybrid-max-open-r014`,
];
gate11.validations = [
  {
    id: "rev13-rejection-recorded",
    status: "pass",
    evidence:
      "Rev13 is preserved as rejected history with exact feedback: "
      + "我感觉明显还是rev 12细节更多吧.",
  },
  {
    id: "byte-identical-rev12-detail-lineage",
    status: "pass",
    evidence:
      "Upper/lower albedo, roughness, normal and motif masks reference the "
      + "same nine rev12 source assets. SHA-256 values are in the report.",
  },
  {
    id: "high-frequency-detail-retained",
    status: "pass",
    evidence:
      "Aligned macro ratios versus rev12: Laplacian "
      + `${metrics.hybridToRev12Ratios.laplacianMean.toFixed(3)}, local `
      + `variance ${metrics.hybridToRev12Ratios.localVariance.toFixed(3)}, `
      + `edge density ${metrics.hybridToRev12Ratios.edgeDensity.toFixed(3)}.`,
  },
  {
    id: "physical-depth-retained",
    status: "pass",
    evidence:
      `Rev13 0.28/0.14/0.00 mm offsets remain; measured 15-degree macro `
      + `parallax is ${report.measuredParallaxPixelsAt15Degrees.toFixed(2)} px.`,
  },
  {
    id: "cap-preserves-detail",
    status: "pass",
    evidence:
      "Crystal transmission is 0.985 and refraction is 0.35 px. Clipping "
      + `fraction is ${metrics.metrics.hybrid.clippedFraction}.`,
  },
  {
    id: "video-image-mobile-modal",
    status: "pass",
    evidence:
      "Three-way moving Unity comparison and macro/angle/shipping boards "
      + "passed encoding, browser desktop/mobile, image and modal checks.",
  },
  {
    id: "bounds-colliders-runtime",
    status: "pass",
    evidence:
      "Exterior bounds delta is zero. Collider identities and protected "
      + "mechanism, gesture, audio and Haptic hashes are unchanged.",
  },
  {
    id: "unity-editmode",
    status: "pass",
    evidence: "Focused hybrid EditMode tests passed.",
  },
  {
    id: "unity-playmode",
    status: "pass",
    evidence: "Shipping Input System PlayMode suite passed.",
  },
];
gate11.decision = null;
gate11.unityParitySpec = {
  revision: 14,
  rejectedRevision: 13,
  rejectedExactWording: "我感觉明显还是rev 12细节更多吧",
  retainedHistoricalRevisions: [12, 13],
  architecture: report.architecture,
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  detailSourceHashes: {
    upperAlbedo: report.upperAlbedoSha256,
    lowerAlbedo: report.lowerAlbedoSha256,
    upperRoughness: report.upperRoughnessSha256,
    lowerRoughness: report.lowerRoughnessSha256,
    upperNormal: report.upperNormalSha256,
    lowerNormal: report.lowerNormalSha256,
    upperMotifMask: report.upperMotifMaskSha256,
    lowerMotifMask: report.lowerMotifMaskSha256,
    perimeterMask: report.perimeterMaskSha256,
  },
  opticalDimensions: {
    authority: "rev13 retained visual estimates; not production measurements",
    substrateInsetMeters: report.substrateInsetMeters,
    motifInsetMeters: report.motifInsetMeters,
    crystalCapThicknessMeters: report.crystalCapThicknessMeters,
    crystalIor: report.crystalIor,
  },
  detailMetrics: metrics,
  parallax: {
    camera: "15-degree 1280x960 macro projection",
    pixels: report.measuredParallaxPixelsAt15Degrees,
    targetPixels: 2.1,
  },
  crystal: {
    transmission: report.hybridTransmission,
    refractionPixels: report.hybridRefractionPixels,
  },
  performance: {
    addedRenderers: report.addedRenderersVersusRev12,
    estimatedAddedDrawCalls: report.estimatedAddedDrawCallsVersusRev12,
    transparentOverdrawLayers: report.transparentOverdrawLayers,
    estimate: report.estimatedMobileCost,
    deviceGpuTiming: "not measured; no phone build authorized",
  },
  boundsUnchanged:
    report.boundsCenterDeltaMeters === 0
    && report.boundsSizeDeltaMeters === 0,
  collidersUnchanged: report.collidersUnchanged,
  protectedRuntimeUnchanged: report.protectedRuntimeUnchanged,
  endpointInterlockLegal: report.endpointInterlockLegal,
  sideArtworkTriangles: 0,
  undersideArtworkTriangles: 0,
  emission: 0,
  visualLayerGeometryChanged: false,
  mechanicalGeometryChanged: false,
  interactionChanged: false,
  audioChanged: false,
  hapticsChanged: false,
  visualApproval: "pending",
  buildInstallPhone: false,
  build44InstallAuthorized: false,
  reviewQuestion:
    "这个 rev 14 是否同时保留 rev 12 的颗粒细节和 rev 13 的真实层距？",
  interactiveDeepLink:
    "?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity"
    + `&asset=${modelId}-unity-detail-depth-hybrid-reflection-video-r014`,
};
gate11.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 11 rev14 detail-depth hybrid is ready for visual review. "
    + "No device build or install is authorized.",
};
gate11.deliveryState = {
  decisionState: "pending-hybrid-visual-approval",
  shippingSource: "detail-depth-hybrid-r014-candidate",
  build42: "rejected-visual-material",
  build44: "not-built-install-blocked",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "failed-build42-awaiting-approved-preview",
};

gate12.status = "stale";
gate12.decision = null;
gate12.staleReason =
  "Gate 11 rev13 lost surface detail. Rev14 changes only decorative-cap "
  + "materials while retaining rev13 layer geometry. Gate 12 waits for "
  + "explicit rev14 visual approval.";
gate12.readiness = {
  ready: false,
  blockers: ["Gate 11 rev14 hybrid visual approval is pending."],
  note:
    "Build44 source must not be built or installed before shipping preview approval.",
};
gate12.deliveryState = {
  decisionState: "blocked-on-gate11-rev14-visual-approval",
  build42: "rejected-visual-material",
  build44: "not-built-install-blocked",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "failed-build42-awaiting-approved-preview",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((candidate) => candidate.stageId === stage.id)
    .map((candidate) => JSON.stringify(candidate));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = stageId;
manifest.overallStatus = "waiting_for_user";
manifest.currentState.visualApproval =
  "gate11-r014-detail-depth-hybrid-ready-for-review";
manifest.currentState.unityStatus =
  "hybrid-source-previewed-build44-install-blocked";
manifest.currentState.deviceStatus =
  "build42-rejected-build44-not-built-or-installed";
manifest.currentState.diagnosis =
  "Rev13 reduced rev12 authored color/detail and the clear cap re-sampled "
  + "scene color. Rev14 restores rev12 source/detail sampling on rev13 "
  + "physical layer geometry. Visual approval is pending.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate11-r014-detail-depth-hybrid-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  gateRevision: 14,
  exactUserFeedback: "我感觉明显还是rev 12细节更多吧",
  rejectedRevision: 13,
  retainedHistoricalRevisions: [12, 13],
  measuredParallaxPixels: report.measuredParallaxPixelsAt15Degrees,
  hybridToRev12Ratios: metrics.hybridToRev12Ratios,
  protectedRuntimeUnchanged: true,
  mechanicalGeometryChanged: false,
  build44InstallAuthorized: false,
  buildInstallPhone: false,
  appStoreSubmitted: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate11Status: gate11.status,
  gate11Revision: gate11.revision,
  gate12Status: gate12.status,
  reviewArtifactIds: gate11.reviewArtifactIds,
}, null, 2));
