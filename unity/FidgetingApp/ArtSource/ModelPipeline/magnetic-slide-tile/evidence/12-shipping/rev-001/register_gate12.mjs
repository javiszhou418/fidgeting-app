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
const root =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001";
const manifest = loadManifest(modelId);
const gate11 = manifest.stages[10];
const stage = manifest.stages[11];
if (manifest.revision !== 93
  || gate11.status !== "approved"
  || gate11.decision?.notes !== "确认"
  || stage.status !== "blocked") {
  throw new Error("Expected exact Gate 11 approval and blocked Gate 12 at revision 93.");
}

const definitions = [
  ["magnetic-slide-tile-gate12-registrar-r001", "registration-source", `${root}/register_gate12.mjs`, "process"],
  ["magnetic-slide-tile-gate12-builder-source-r001", "unity-builder-source", "unity/FidgetingApp/Assets/_EDC/Candidate/Editor/MagneticSlideTileGate12Builder.cs", "process"],
  ["magnetic-slide-tile-gate12-settings-source-r001", "runtime-source", "unity/FidgetingApp/Assets/_EDC/Candidate/Runtime/MagneticSlideTileCandidateSettings.cs", "process"],
  ["magnetic-slide-tile-gate12-controller-source-r001", "runtime-source", "unity/FidgetingApp/Assets/_EDC/Candidate/Runtime/MagneticSlideTileCandidateController.cs", "process"],
  ["magnetic-slide-tile-gate12-activation-source-r001", "runtime-source", "unity/FidgetingApp/Assets/_EDC/Candidate/Runtime/MagneticSlideTileCandidateActivation.cs", "process"],
  ["magnetic-slide-tile-gate12-shader-source-r001", "shader-source", "unity/FidgetingApp/Assets/_EDC/Candidate/Shaders/MagneticCrystalMobile.shader", "process"],
  ["magnetic-slide-tile-gate12-editmode-source-r001", "test-source", "unity/FidgetingApp/Assets/_EDC/Tests/Editor/MagneticSlideTileGate12Tests.cs", "validation"],
  ["magnetic-slide-tile-gate12-playmode-source-r001", "test-source", "unity/FidgetingApp/Assets/_EDC/Tests/PlayMode/MagneticSlideTileCandidatePlayModeTests.cs", "validation"],
  ["magnetic-slide-tile-gate12-review-source-r001", "review-builder-source", `${root}/build_gate12_review.py`, "process"],
  ["magnetic-slide-tile-gate12-shipping-scene-r001", "shipping-scene", "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["magnetic-slide-tile-gate12-candidate-prefab-r001", "candidate-prefab", "unity/FidgetingApp/Assets/_EDC/Candidate/Prefabs/MagneticSlideTileCandidate.prefab", "source-model"],
  ["magnetic-slide-tile-gate12-settings-r001", "shared-mechanism-settings", "unity/FidgetingApp/Assets/_EDC/Candidate/Settings/MagneticSlideTileCandidateSettings.asset", "source-model"],
  ["magnetic-slide-tile-gate12-silver-material-r001", "shipping-material", "unity/FidgetingApp/Assets/_EDC/Candidate/Materials/M_Gate12_PolishedSilver.mat", "source-model"],
  ["magnetic-slide-tile-gate12-upper-material-r001", "shipping-material", "unity/FidgetingApp/Assets/_EDC/Candidate/Materials/M_Gate12_CrystalUpper.mat", "source-model"],
  ["magnetic-slide-tile-gate12-lower-material-r001", "shipping-material", "unity/FidgetingApp/Assets/_EDC/Candidate/Materials/M_Gate12_CrystalLower.mat", "source-model"],
  ["magnetic-slide-tile-gate12-reflection-r001", "shipping-reflection", "unity/FidgetingApp/Assets/_EDC/Candidate/Materials/Gate12_ShippingReflection.cubemap", "source-model"],
  ["magnetic-slide-tile-gate12-report-r001", "shipping-report", `${root}/gate12-shipping-report.json`, "validation"],
  ["magnetic-slide-tile-gate12-image-validation-r001", "shipping-image-validation", `${root}/gate12-image-validation.json`, "validation"],
  ["magnetic-slide-tile-gate12-review-board-r001", "shipping-review-board", `${root}/gate12-shipping-board.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-motion-board-r001", "shipping-motion-board", `${root}/gate12-motion-board.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-library-r001", "shipping-library", `${root}/library.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-hero-r001", "shipping-hero", `${root}/hero.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-top-r001", "shipping-top", `${root}/top.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-left-r001", "shipping-left-oblique", `${root}/left-oblique.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-right-r001", "shipping-right-oblique", `${root}/right-oblique.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-low-r001", "shipping-low", `${root}/low.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-phone-r001", "shipping-phone", `${root}/phone.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-slide-open-r001", "shipping-slide-open", `${root}/slide-open.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-ratchet-r001", "shipping-ratchet", `${root}/ratchet-60deg.png`, "unity-render"],
  ["magnetic-slide-tile-gate12-unity-log-r001", "unity-log", `${root}/unity-gate12.log`, "validation"],
  ["magnetic-slide-tile-gate12-editmode-results-r001", "editmode-results", `${root}/editmode-results.xml`, "validation"],
  ["magnetic-slide-tile-gate12-editmode-log-r001", "editmode-log", `${root}/editmode-tests.log`, "validation"],
  ["magnetic-slide-tile-gate12-playmode-results-r001", "playmode-results", `${root}/playmode-results.xml`, "validation"],
  ["magnetic-slide-tile-gate12-playmode-log-r001", "playmode-log", `${root}/playmode-tests.log`, "validation"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-unity-parity-rev2-environment-r002",
  "magnetic-slide-tile-unity-parity-rev2-upper-basecolor-r002",
  "magnetic-slide-tile-unity-parity-rev2-lower-basecolor-r002",
  "magnetic-slide-tile-unity-parity-rev2-before-after-r002",
];
const records = definitions.map(([id, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id,
    stageId: "12-shipping",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role.startsWith("unity") ? "Unity" : "Gate 12 deterministic workflow",
      version: role.startsWith("unity") ? "6000.5.6f1" : "2026-08-25",
      recipe: `${root}/build_gate12_review.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate12Revision: 1,
      candidatePreviewOnly: true,
    },
    sourceAssetIds,
    sourceClaimIds: ["slider-gate11-rev2-approval-r001"],
  };
});

manifest.claims.push({
  id: "slider-gate11-rev2-approval-r001",
  stageId: "11-unity-parity",
  topic: "user-approval",
  statement: "确认",
  confidence: "user-authoritative",
  sourceAssetIds: [
    "magnetic-slide-tile-unity-parity-rev2-location-r002",
    "magnetic-slide-tile-unity-parity-rev2-before-after-r002",
    "magnetic-slide-tile-unity-parity-rev2-wire-proof-r002",
  ],
  sourceClaimIds: [],
  regions: [],
  notes: "Exact Gate 11 rev 2 approval. It permits Gate 12 review work only.",
});
manifest.assets.push(...records);
stage.status = "ready_for_review";
stage.revision = 1;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "magnetic-slide-tile-gate12-review-board-r001",
  "magnetic-slide-tile-gate12-motion-board-r001",
  "magnetic-slide-tile-gate12-phone-r001",
];
stage.validations = [
  {
    id: "real-shipping-scene-preview",
    status: "pass",
    evidence: "Nine frames were rendered from Assets/_EDC/Scenes/MeshyEDC.unity with the controlled candidate switch active only during capture.",
  },
  {
    id: "candidate-safe-default",
    status: "pass",
    evidence: "Current EDC_Root remains active and the candidate prefab remains inactive in the saved shipping scene.",
  },
  {
    id: "candidate-geometry-material-artwork",
    status: "pass",
    evidence: "50 × 31 × 12 mm, 4,096 triangles, two render meshes, zero emission, filtered reflection and independent upper/lower materials passed.",
  },
  {
    id: "candidate-mechanism-scope",
    status: "pass",
    evidence: "One settings asset defines 21 mm and 30 × 12°. Preview poses reset to zero velocity. Runtime input and Haptics remain explicitly not integrated.",
  },
  {
    id: "unity-tests",
    status: "pass",
    evidence: "Gate 12 EditMode 7/7 and PlayMode 1/1 passed.",
  },
  {
    id: "shipping-image-checks",
    status: "pass",
    evidence: "Required views, portrait phone composition, deep red artwork, bright unclipped silver and open lower artwork passed.",
  },
];
delete stage.staleReason;
stage.shippingSpec = {
  revision: 1,
  scenePath: "Assets/_EDC/Scenes/MeshyEDC.unity",
  candidateActivation: {
    control: "MagneticSlideTile_CandidateSwitch",
    currentShippingModelDefaultActive: true,
    candidateDefaultActive: false,
  },
  geometry: {
    boundsMeters: [0.05, 0.031, 0.012],
    renderMeshes: 2,
    triangles: 4096,
  },
  presentation: {
    silver: "URP Lit polished warm-neutral silver with local continuous Reflection Probe",
    crystal: "mobile one-pass opaque clearcoat/transmission/iridescence approximation",
    emission: 0,
    upperLowerArtworkIndependent: true,
    remainingGap: "No physical refraction, volume absorption, Blender thin-film spectral transport or device HDR validation.",
  },
  motion: {
    sharedSettingsAsset: "Assets/_EDC/Candidate/Settings/MagneticSlideTileCandidateSettings.asset",
    slideTravelMeters: 0.021,
    detentCount: 30,
    detentStepDegrees: 12,
    initialAndResetVelocity: 0,
    runtimeInputIntegrated: false,
    hapticsIntegrated: false,
  },
  review: {
    approval: "pending",
    deliveryState: "real-shipping-scene-candidate-preview-only",
    deviceAcceptance: "pending",
    buildInstallPhonePush: "not-started",
  },
};

manifest.currentState.visualApproval =
  "gate12-real-shipping-scene-rev1-pending-candidate-default-disabled";
manifest.currentState.diagnosis =
  "Gate 11 rev 2 approved with exact note 确认. Gate 12 rev 1 uses the real MeshyEDC shipping scene behind a saved default-off candidate switch. The current EDC_Root remains default active. Nine Unity frames show the approved 4,096-triangle model, independent artwork, 21 mm open pose and 30 × 12° review pose. Runtime input and Haptics are not integrated. No build, install or phone push occurred.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  revision: 1,
  gate11Approval: "确认",
  artifactIds: records.map((record) => record.id),
  reviewArtifactIds: stage.reviewArtifactIds,
  candidateDefaultActive: false,
  currentShippingModelDefaultActive: true,
  runtimeInputIntegrated: false,
  hapticsIntegrated: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[11].status,
  reviewArtifactIds: saved.stages[11].reviewArtifactIds,
  shippingReady: saved.currentState.shippingReady,
}, null, 2));
