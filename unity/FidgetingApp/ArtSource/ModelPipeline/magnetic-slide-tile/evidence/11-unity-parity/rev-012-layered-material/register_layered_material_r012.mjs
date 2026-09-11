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
  + "evidence/11-unity-parity/rev-012-layered-material";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/"
  + "MagneticSlideTileGate11R012";
const scenePath = "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity";
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((stage) => stage.id === stageId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const report = read("unity-layered-material-report.json");
const metrics = read("layered-material-image-metrics.json");

if (!gate11 || !gate12 || !report.pass || !metrics.pass)
  throw new Error("Layered material evidence is incomplete.");

gate11.historicalRevisions ??= [];
if (!gate11.historicalRevisions.some(
  (revision) => revision.evidenceRevision === 11
    && revision.status === "approved-before-device-material-rejection")) {
  gate11.historicalRevisions.push({
    evidenceRevision: 11,
    stageRevision: gate11.revision,
    status: "approved-before-device-material-rejection",
    artifactIds: [...gate11.artifactIds],
    reviewArtifactIds: [...gate11.reviewArtifactIds],
    validations: structuredClone(gate11.validations),
    unityParitySpec: structuredClone(gate11.unityParitySpec),
    decision: structuredClone(gate11.decision),
    deliveryState: structuredClone(gate11.deliveryState),
    preservedForHistory: true,
  });
}

gate12.historicalRevisions ??= [];
if (!gate12.historicalRevisions.some(
  (revision) => revision.evidenceRevision === 5
    && revision.status === "approved-lighting-build42-material-rejected")) {
  gate12.historicalRevisions.push({
    evidenceRevision: 5,
    stageRevision: gate12.revision,
    status: "approved-lighting-build42-material-rejected",
    artifactIds: [...gate12.artifactIds],
    reviewArtifactIds: [...gate12.reviewArtifactIds],
    validations: structuredClone(gate12.validations),
    shippingSpec: structuredClone(gate12.shippingSpec),
    decision: structuredClone(gate12.decision),
    deliveryState: structuredClone(gate12.deliveryState),
    deviceVisualFeedback: {
      exactWording:
        "red face flattened; material depth, color variation and distinct "
        + "reflection characteristics are missing",
      build42: "rejected",
      build44InstallAuthorized: false,
    },
    preservedForHistory: true,
  });
}

const definitions = [
  ["registrar", "unity-parity-registrar",
    `${evidenceRoot}/register_layered_material_r012.mjs`, "validation"],
  ["shader", "unity-shader",
    `${candidateRoot}/Shaders/MagneticSlideTileLayeredOpticsR012.shader`,
    "source-model"],
  ["upper-material", "unity-material",
    `${candidateRoot}/Materials/M_G11R012_UpperLayeredTop.mat`, "source-model"],
  ["lower-material", "unity-material",
    `${candidateRoot}/Materials/M_G11R012_LowerLayeredTop.mat`, "source-model"],
  ["builder", "unity-builder",
    `${candidateRoot}/Editor/MagneticSlideTileGate11R012MaterialReviewBuilder.cs`,
    "source-model"],
  ["editor-tests", "test-source",
    "unity/FidgetingApp/Assets/_EDC/Tests/Editor/"
      + "MagneticSlideLayeredMaterialRevisionTests.cs", "validation"],
  ["playmode-tests", "test-source",
    "unity/FidgetingApp/Assets/_EDC/Candidates/"
      + "MagneticSlideTileGate12R002/Tests/PlayMode/"
      + "MagneticSlideTileInputPlayModeTests.cs", "validation"],
  ["pipeline-test", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "magnetic-slide-gate11-layered-material-r12.test.mjs", "validation"],
  ["browser-test", "test-source",
    "tools/model-provenance-explorer/tests/"
      + "browser-gate11-layered-material-r12.mjs", "validation"],
  ["scene", "unity-scene", scenePath, "source-model"],
  ["report", "unity-parity-report",
    `${evidenceRoot}/unity-layered-material-report.json`, "validation"],
  ["metrics", "image-validation",
    `${evidenceRoot}/layered-material-image-metrics.json`, "validation"],
  ["review-builder", "review-builder-source",
    `${evidenceRoot}/build_material_review.py`, "validation"],
  ["authority-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r012-material-authority-board.png`, "unity-render"],
  ["comparison-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r012-flat-layered-comparison.png`, "unity-render"],
  ["shipping-views-board", "unity-parity-board",
    `${evidenceRoot}/gate11-r012-layered-shipping-views.png`, "unity-render"],
  ["reflection-video", "unity-runtime-recording",
    `${evidenceRoot}/magnetic-slide-layered-reflection-r012.mp4`, "unity-render"],
  ["browser-report", "browser-validation",
    `${evidenceRoot}/browser-mobile-modal-validation.json`, "validation"],
  ["editmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideLayeredR012EditMode.xml", "validation"],
  ["editmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideLayeredR012EditMode.log", "validation"],
  ["playmode-results", "test-results",
    "unity/FidgetingApp/Logs/MagneticSlideLayeredR012PlayMode.xml", "validation"],
  ["playmode-log", "test-log",
    "unity/FidgetingApp/Logs/MagneticSlideLayeredR012PlayMode.log", "validation"],
];
for (const variant of ["A-current-flat-unity", "B-layered-unity"]) {
  for (const view of [
    "front", "hero", "left-oblique", "right-oblique",
    "grazing", "low", "phone", "max-open",
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
  "magnetic-slide-tile-unity-parity-scene-r011",
  "magnetic-slide-tile-unity-parity-shader-r011",
  "magnetic-slide-tile-export-glb-r011",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing layered material artifact: ${path}`);
  return {
    id: `${modelId}-unity-layered-${suffix}-r012`,
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
        : "Gate 11 layered material correction",
      version: "2026-09-02",
      recipe:
        `${candidateRoot}/Editor/`
        + "MagneticSlideTileGate11R012MaterialReviewBuilder.cs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      evidenceRevision: 12,
      geometryChanged: false,
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
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
}

const claim = {
  id: "slider-gate11-r012-layered-material-correction",
  stageId,
  topic: "unity-layered-material",
  statement:
    "Build 42 flattened the approved red optical stack. The corrected Unity "
    + "candidate uses one opaque pass with separate blood-red substrate, black "
    + "motif and IOR 1.52 clear-cap responses. Geometry and runtime hashes stay unchanged.",
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

gate11.revision = 12;
gate11.status = "ready_for_review";
gate11.artifactIds = records.map((record) => record.id);
gate11.reviewArtifactIds = [
  `${modelId}-unity-layered-reflection-video-r012`,
  `${modelId}-unity-layered-authority-board-r012`,
  `${modelId}-unity-layered-comparison-board-r012`,
  `${modelId}-unity-layered-shipping-views-board-r012`,
  `${modelId}-unity-layered-B-layered-unity-hero-r012`,
  `${modelId}-unity-layered-B-layered-unity-grazing-r012`,
  `${modelId}-unity-layered-B-layered-unity-max-open-r012`,
];
gate11.validations = [
  {
    id: "root-cause-current-material-path",
    status: "pass",
    evidence:
      "PortablePBRR011 is OPAQUE with transmission 0 and merges base, roughness, "
      + "normal and weak clearcoat into one BRDF. It cannot preserve the approved stack.",
  },
  {
    id: "layered-optics-architecture",
    status: "pass",
    evidence:
      "One opaque URP pass separates deep-red substrate, black motif and IOR "
      + "1.52 clear-cap responses. No shell, transparent sorting or bounds growth.",
  },
  {
    id: "shader-mobile-compile",
    status: "pass",
    evidence:
      "Metal shader target 3.5 compiles with zero shader errors/warnings and a "
      + "single UnityPerMaterial CBUFFER.",
  },
  {
    id: "material-image-quality",
    status: "pass",
    evidence:
      "Median luminance 0.135→0.217; red saturation 0.393→0.500; red local "
      + "variation P90 0.0133→0.0322; clipped pixels 0%.",
  },
  {
    id: "partition-and-side-wall",
    status: "pass",
    evidence:
      "Upper/lower masks remain independent. Artwork is top-cap only. Dark side, "
      + "silver rim and underside material slots remain unchanged.",
  },
  {
    id: "protected-runtime-and-geometry",
    status: "pass",
    evidence:
      "Seven runtime/prefab/settings/audio/Haptic hashes, mesh identities, "
      + "renderer count and bounds are unchanged.",
  },
  {
    id: "unity-editmode",
    status: "pass",
    evidence: "Layered material EditMode tests passed 3/3.",
  },
  {
    id: "unity-playmode",
    status: "pass",
    evidence:
      "Shipping Input System PlayMode suite passed 5/5, including material wiring.",
  },
  {
    id: "review-recording",
    status: "pass",
    evidence:
      "6.0 s, 1280×720, 30 fps real Unity camera motion shows reflection, "
      + "microvariation and clear-cap response.",
  },
];
gate11.decision = null;
gate11.unityParitySpec = {
  revision: 12,
  sourceGate11Revision: 11,
  sourceShader: "PortablePBRR011",
  correctedShader: "LayeredOpticsR012",
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  sceneSha256: report.sceneSha256After,
  architecture: report.architecture,
  materialValues: {
    coatIor: report.coatIor,
    coatRoughness: report.coatRoughness,
    coatStrength: report.coatStrength,
    layerDepthUv: report.layerDepthUv,
    micaScale: report.micaScale,
    microflakeScale: report.microflakeScale,
    microflakeStrength: report.microflakeStrength,
    iridescenceStrength: report.iridescenceStrength,
    motifRoughness: report.motifRoughness,
    motifMetallic: report.motifMetallic,
    motifReliefUv: report.motifReliefUv,
    emission: 0,
  },
  performance: {
    topPasses: 1,
    addedRenderers: 0,
    addedDrawCalls: 0,
    textureSamplesPerTopPixel: 5,
    cubemapSamplesPerTopPixel: 4,
    transparentOverdraw: false,
    estimate: report.estimatedMobileCost,
  },
  imageMetrics: metrics,
  protectedRuntimeUnchanged: true,
  geometryChanged: false,
  interactionChanged: false,
  audioChanged: false,
  hapticsChanged: false,
  sideWallMaterialChanged: false,
  visualApproval: "pending",
  buildInstallPhone: false,
  build44InstallAuthorized: false,
  deviceAcceptance: "failed-build42-material-flatness",
  reviewQuestion:
    "这个 Unity 分层材质是否恢复了实物和 Blender 中的血红层次、黑纹理与清漆反射？",
  interactiveDeepLink:
    "?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity"
    + "&asset=magnetic-slide-tile-unity-layered-reflection-video-r012",
};
gate11.readiness = {
  ready: true,
  blockers: [],
  note:
    "Gate 11 rev 12 layered material correction is ready for visual review. "
    + "No device build or install is authorized.",
};
gate11.deliveryState = {
  decisionState: "pending-material-visual-approval",
  shippingSource: "layered-material-candidate",
  build42: "rejected-material-flatness",
  build44: "not-built-install-blocked",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "failed-build42-awaiting-approved-preview",
};

gate12.revision = 6;
gate12.status = "stale";
gate12.decision = null;
gate12.staleReason =
  "Gate 11 material response changed after Build 42 device rejection. "
  + "Gate 12 must wait for explicit Gate 11 rev 12 visual approval.";
gate12.readiness = {
  ready: false,
  blockers: [
    "Gate 11 rev 12 layered material visual approval is pending.",
  ],
  note: "Build 44 source must not be installed before a fresh shipping preview approval.",
};
gate12.deliveryState = {
  decisionState: "blocked-on-gate11-material-approval",
  build42: "rejected-material-flatness",
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
  "gate11-r012-layered-material-ready-for-review";
manifest.currentState.unityStatus =
  "layered-material-source-previewed-build44-install-blocked";
manifest.currentState.deviceStatus =
  "build42-rejected-material-flatness-build44-not-installed";
manifest.currentState.diagnosis =
  "Build42 flattened the approved optical stack. Gate11 rev12 restores "
  + "separate substrate, motif and clear-cap response in one URP pass. "
  + "Visual approval is pending; Build44 installation is blocked.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate11-r012-layered-material-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  gateRevision: gate11.revision,
  exactUserFeedback:
    "red face flattened: material depth, color variation and distinct "
    + "reflection characteristics are missing",
  build42VisualAcceptance: "failed-material-flatness",
  build44InstallAuthorized: false,
  architecture: report.architecture,
  protectedRuntimeUnchanged: true,
  geometryChanged: false,
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
