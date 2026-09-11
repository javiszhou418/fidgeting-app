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
  + "evidence/11-unity-parity/rev-013-true-layers";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/"
  + "MagneticSlideTileGate11R013";
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((stage) => stage.id === stageId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const report = read("unity-true-layer-report.json");
const metrics = read("true-layer-image-metrics.json");

if (!gate11 || !gate12 || !report.pass || !metrics.pass)
  throw new Error("True-layer evidence is incomplete.");

gate11.historicalRevisions ??= [];
const rev12 = gate11.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 12);
if (rev12) {
  rev12.status = "rejected-no-visible-layer-depth";
  rev12.exactUserFeedback = "我还是没看出层次感";
  rev12.preservedForHistory = true;
} else {
  gate11.historicalRevisions.push({
    evidenceRevision: 12,
    stageRevision: gate11.revision,
    status: "rejected-no-visible-layer-depth",
    exactUserFeedback: "我还是没看出层次感",
    artifactIds: [...gate11.artifactIds],
    reviewArtifactIds: [...gate11.reviewArtifactIds],
    validations: structuredClone(gate11.validations),
    unityParitySpec: structuredClone(gate11.unityParitySpec),
    decision: structuredClone(gate11.decision),
    deliveryState: structuredClone(gate11.deliveryState),
    preservedForHistory: true,
  });
}
const rev12Claim = manifest.claims.find(
  (claim) => claim.id === "slider-gate11-r012-layered-material-correction");
if (rev12Claim) {
  rev12Claim.state = "rejected";
  rev12Claim.decisionState = "rejected-by-user";
  rev12Claim.rejectionReason =
    "One opaque pass did not show visible layer depth.";
  rev12Claim.exactUserFeedback = "我还是没看出层次感";
}

const definitions = [
  ["registrar", "unity-parity-registrar",
    `${evidenceRoot}/register_true_layers_r013.mjs`, "validation"],
  ["review-builder", "review-builder-source",
    `${evidenceRoot}/build_true_layer_review.py`, "validation"],
  ["unity-builder", "unity-builder",
    `${candidateRoot}/Editor/MagneticSlideTileGate11R013TrueLayerBuilder.cs`,
    "source-model"],
  ["runtime", "unity-runtime",
    `${candidateRoot}/Runtime/MagneticSlideTrueLayerAssembly.cs`,
    "source-model"],
  ["substrate-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideTrueSubstrateR013.shader`,
    "source-model"],
  ["motif-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideTrueMotifR013.shader`,
    "source-model"],
  ["crystal-shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideTrueCrystalCapR013.shader`,
    "source-model"],
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
  ["scene", "unity-scene",
    "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["report", "unity-parity-report",
    `${evidenceRoot}/unity-true-layer-report.json`, "validation"],
  ["metrics", "image-validation",
    `${evidenceRoot}/true-layer-image-metrics.json`, "validation"],
  ["comparison-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r013-r012-true-layer-comparison.png`,
    "unity-render"],
  ["angle-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r013-depth-angle-board.png`, "unity-render"],
  ["shipping-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r013-shipping-poses-board.png`, "unity-render"],
  ["technical-board", "unity-technical-board",
    `${evidenceRoot}/gate11-r013-true-layer-technical-board.png`,
    "unity-render"],
  ["reflection-video", "unity-runtime-recording",
    `${evidenceRoot}/magnetic-slide-true-layer-reflection-r013.mp4`,
    "unity-render"],
  ["browser-report", "browser-validation",
    `${evidenceRoot}/browser-mobile-modal-validation.json`, "validation"],
  ["editmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideTrueLayerR013EditMode.xml",
    "validation"],
  ["editmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideTrueLayerR013EditMode.log",
    "validation"],
  ["playmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideTrueLayerR013PlayMode.xml",
    "validation"],
  ["playmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideTrueLayerR013PlayMode.log",
    "validation"],
  ["capture-log", "capture-log",
    "unity/FidgetingApp/Logs/MagneticSlideTrueLayerR013Capture.log",
    "validation"],
];
for (const face of ["Upper", "Lower"]) {
  for (const layer of [
    "BloodRedSubstrate", "EtchedBlackMotif", "CrystalCap",
  ]) {
    definitions.push([
      `${face.toLowerCase()}-${layer.toLowerCase()}`,
      "unity-material",
      `${candidateRoot}/Materials/M_G11R013_${face}${layer}.mat`,
      "source-model",
    ]);
  }
}
for (const object of ["MovingTopBody", "BottomExterior"]) {
  for (const mesh of ["CapOnly", "TrueLayerBody"]) {
    definitions.push([
      `${object.toLowerCase()}-${mesh.toLowerCase()}`,
      "unity-mesh",
      `${candidateRoot}/Generated/${object}_${mesh}_R013.asset`,
      "source-model",
    ]);
  }
}
for (const variant of ["A-one-pass-r012", "B-true-layers-r013"]) {
  for (const view of [
    "front", "grazing-15", "grazing-30", "grazing-60",
    "hero-closed", "hero-max-open", "lower-artwork-max-open", "side-macro",
  ]) {
    definitions.push([
      `${variant}-${view}`,
      `unity-${view}`,
      `${evidenceRoot}/${variant}/${view}.png`,
      "unity-render",
    ]);
  }
}
definitions.push([
  "B-true-layers-r013-phone-closed",
  "unity-phone",
  `${evidenceRoot}/B-true-layers-r013/phone-closed.png`,
  "unity-render",
]);

const sourceAssetIds = [
  "magnetic-slide-tile-unity-layered-reflection-video-r012",
  "magnetic-slide-tile-unity-parity-scene-r011",
  "magnetic-slide-tile-export-glb-r011",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing true-layer artifact: ${path}`);
  return {
    id: `${modelId}-unity-true-layer-${suffix}-r013`,
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
        : "Gate 11 true-layer correction",
      version: "2026-09-02",
      recipe:
        `${candidateRoot}/Editor/`
        + "MagneticSlideTileGate11R013TrueLayerBuilder.cs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      evidenceRevision: 13,
      visualLayerGeometryChanged: true,
      mechanicalGeometryChanged: false,
      collidersChanged: false,
      interactionChanged: false,
      audioChanged: false,
      hapticsChanged: false,
      sideWallMaterialChanged: false,
      buildInstallPhone: false,
      opticalDimensionsAuthority:
        "source-faithful visual estimate; not production measurement",
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
}

const claim = {
  id: "slider-gate11-r013-true-layer-correction",
  stageId,
  topic: "unity-true-layer-material",
  statement:
    "Upper and lower decorative caps each use physically separated "
    + "blood-red substrate, etched black motif and transparent IOR 1.52 "
    + "crystal renderers nested inside the existing exterior bounds.",
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

gate11.revision = 13;
gate11.status = "ready_for_review";
gate11.artifactIds = records.map((record) => record.id);
gate11.reviewArtifactIds = [
  `${modelId}-unity-true-layer-reflection-video-r013`,
  `${modelId}-unity-true-layer-comparison-board-r013`,
  `${modelId}-unity-true-layer-angle-board-r013`,
  `${modelId}-unity-true-layer-technical-board-r013`,
  `${modelId}-unity-true-layer-shipping-board-r013`,
  `${modelId}-unity-true-layer-B-true-layers-r013-hero-closed-r013`,
  `${modelId}-unity-true-layer-B-true-layers-r013-grazing-15-r013`,
  `${modelId}-unity-true-layer-B-true-layers-r013-hero-max-open-r013`,
];
gate11.validations = [
  {
    id: "rev12-rejection-recorded",
    status: "pass",
    evidence:
      "Rev12 is preserved as rejected history with exact feedback: "
      + "我还是没看出层次感.",
  },
  {
    id: "physical-three-layer-assembly",
    status: "pass",
    evidence:
      "Each face has separate cap-only substrate, alpha-tested motif and "
      + "transparent crystal meshes at 0.28/0.14/0.00 mm inset.",
  },
  {
    id: "measurable-screen-parallax",
    status: "pass",
    evidence:
      `${report.measuredScreenParallaxPixelsAt15Degrees.toFixed(2)} px `
      + "motif/substrate separation in the 15-degree Unity macro camera.",
  },
  {
    id: "shader-mobile-compile",
    status: "pass",
    evidence:
      "Three target 3.5 URP shaders compile with zero errors and use "
      + "UnityPerMaterial CBUFFERs.",
  },
  {
    id: "sorting-and-z-fighting",
    status: "pass",
    evidence:
      "Opaque 2020, alpha-test 2480 ZWrite, and crystal 3090 DepthOnly/"
      + "transparent passes; minimum gap is 14x estimated depth precision.",
  },
  {
    id: "image-and-video-quality",
    status: "pass",
    evidence:
      "Real shipping renders pass deep-red, local variation, no-white-"
      + "washout and nonblank checks. H.264 video is 8 s at 1280x720/30.",
  },
  {
    id: "bounds-colliders-runtime",
    status: "pass",
    evidence:
      "Exterior bounds delta is zero. Collider identities and protected "
      + "mechanism, gesture, audio and Haptic source hashes are unchanged.",
  },
  {
    id: "unity-editmode",
    status: "pass",
    evidence: "True-layer EditMode tests passed 3/3.",
  },
  {
    id: "unity-playmode",
    status: "pass",
    evidence:
      "Shipping Input System PlayMode suite passed 5/5, including true-layer wiring.",
  },
];
gate11.decision = null;
gate11.unityParitySpec = {
  revision: 13,
  rejectedRevision: 12,
  rejectedExactWording: "我还是没看出层次感",
  architecture: report.architecture,
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  opticalDimensions: {
    authority: report.opticalDimensionsAuthority,
    substrateInsetMeters: report.substrateInsetMeters,
    motifInsetMeters: report.motifInsetMeters,
    motifThicknessMeters: report.motifPhysicalThicknessMeters,
    crystalCapThicknessMeters: report.crystalCapThicknessMeters,
    crystalIor: report.crystalIor,
  },
  parallax: {
    camera: "15-degree macro",
    pixels: report.measuredScreenParallaxPixelsAt15Degrees,
  },
  performance: {
    addedRenderers: report.addedRenderers,
    estimatedAddedDrawCalls: report.estimatedAddedDrawCalls,
    transparentLayerDraws: report.transparentLayerDraws,
    transparentOverdrawLayers: report.transparentOverdrawLayers,
    estimate: report.estimatedMobileCost,
    deviceGpuTiming: "not measured; no phone build authorized",
  },
  imageMetrics: metrics,
  boundsUnchanged: report.boundsWithinExistingExterior,
  collidersUnchanged: report.colliderIdentitiesUnchanged,
  protectedRuntimeUnchanged: report.protectedRuntimeUnchanged,
  endpointInterlockLegal: report.endpointInterlockLegal,
  visualLayerGeometryChanged: true,
  mechanicalGeometryChanged: false,
  interactionChanged: false,
  audioChanged: false,
  hapticsChanged: false,
  sideWallMaterialChanged: false,
  visualApproval: "pending",
  buildInstallPhone: false,
  build44InstallAuthorized: false,
  reviewQuestion:
    "这个真实三层 Unity 红面是否终于能看出基底、黑纹和透明晶体层次？",
  interactiveDeepLink:
    "?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity"
    + "&asset=magnetic-slide-tile-unity-true-layer-reflection-video-r013",
};
gate11.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 11 rev 13 true-layer correction is ready for visual review. "
    + "No device build or install is authorized.",
};
gate11.deliveryState = {
  decisionState: "pending-true-layer-visual-approval",
  shippingSource: "true-layer-r013-candidate",
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
  "Gate 11 rev12 was rejected and rev13 changes the decorative-cap visual "
  + "assembly. Gate 12 waits for explicit rev13 visual approval.";
gate12.readiness = {
  ready: false,
  blockers: [
    "Gate 11 rev 13 true-layer visual approval is pending.",
  ],
  note:
    "Build 44 source must not be built or installed before fresh shipping preview approval.",
};
gate12.deliveryState = {
  decisionState: "blocked-on-gate11-rev13-visual-approval",
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
  "gate11-r013-true-layers-ready-for-review";
manifest.currentState.unityStatus =
  "true-layer-source-previewed-build44-install-blocked";
manifest.currentState.deviceStatus =
  "build42-rejected-build44-not-built-or-installed";
manifest.currentState.diagnosis =
  "Rev12 was rejected because one opaque surface did not show layer depth. "
  + "Rev13 uses real nested substrate, motif and crystal renderers. "
  + "Visual approval is pending and Build44 remains blocked.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate11-r013-true-layers-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  gateRevision: gate11.revision,
  exactUserFeedback: "我还是没看出层次感",
  rejectedRevision: 12,
  build42VisualAcceptance: "failed",
  build44InstallAuthorized: false,
  architecture: report.architecture,
  opticalDimensionsAuthority: report.opticalDimensionsAuthority,
  measuredParallaxPixels:
    report.measuredScreenParallaxPixelsAt15Degrees,
  protectedRuntimeUnchanged: true,
  mechanicalGeometryChanged: false,
  visualLayerGeometryChanged: true,
  buildInstallPhone: false,
  appStoreSubmitted: false,
  deviceAcceptance: "failed-build42-awaiting-approved-preview",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate11Status: gate11.status,
  gate11Revision: gate11.revision,
  gate12Status: gate12.status,
  reviewArtifactIds: gate11.reviewArtifactIds,
}, null, 2));
