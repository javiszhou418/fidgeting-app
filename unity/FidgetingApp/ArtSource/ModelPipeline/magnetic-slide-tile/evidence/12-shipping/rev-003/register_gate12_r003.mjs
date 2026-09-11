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
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  !["draft", "ready_for_review"].includes(gate12?.status)
  || gate12?.shippingSpec?.revision !== 3
) {
  throw new Error("Expected Gate 12 rev 3 draft.");
}

const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const feedback = read("user-feedback.json");
const report = read("gate12-motion-fix-report.json");
const validation = read("gate12-motion-validation.json");
const capture = read("unity-playmode-frames/capture-report.json");
const probe = read("video-probe.json");
const browser = read("browser-mobile-modal-validation.json");
const tests = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`), "utf8");
const scenePath =
  "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity";
if (
  !report.pass
  || !validation.pass
  || feedback.screenshotSha256
    !== "d36fb987ee46313fe401337a61552d6e80c3310f9ccdb9852938edee4191015b"
  || capture.maximumTopStackResidualMeters > 5e-9
  || capture.maximumOutOfPlaneSlideResidualMeters > 1e-9
  || capture.maximumFixedAxisConstraintResidual > 1e-9
  || !capture.renderersAttachedEveryFrame
  || !capture.detentsStayedAtMaximumTravel
  || capture.observedDetentMask !== 1073741823
  || probe.streams[0].nb_read_frames !== "240"
  || !browser.pass
  || !tests.includes('result="Passed" total="6" passed="6"')
  || report.shippingSceneSha256
    !== sha256File(resolveRepoPath(scenePath))
) {
  throw new Error("Gate 12 rev 3 evidence is incomplete or stale.");
}

const definitions = [
  ["starter", "revision-transition-source",
    `${evidenceRoot}/start_gate12_r003.mjs`, "process"],
  ["registrar", "registration-source",
    `${evidenceRoot}/register_gate12_r003.mjs`, "process"],
  ["review-builder", "review-build-source",
    `${evidenceRoot}/build_gate12_motion_review.py`, "process"],
  ["unity-builder", "unity-builder-source",
    `${candidateRoot}/Editor/MagneticSlideTileGate12R003MotionReviewBuilder.cs`,
    "process"],
  ["mechanism-source", "runtime-mechanism-source",
    `${candidateRoot}/Runtime/MagneticSlideTileShippingMechanism.cs`,
    "source-model"],
  ["capture-source", "runtime-capture-source",
    `${candidateRoot}/Runtime/MagneticSlideTileGate12PlayModeCapture.cs`,
    "source-model"],
  ["test-source", "test-source",
    `${candidateRoot}/Tests/Editor/MagneticSlideTileGate12R002Tests.cs`,
    "validation"],
  ["node-test-source", "test-source",
    "tools/model-provenance-explorer/tests/magnetic-slide-gate12-rev3.test.mjs",
    "validation"],
  ["feedback", "user-feedback-metadata",
    `${evidenceRoot}/user-feedback.json`, "user-input"],
  ["feedback-screenshot", "user-feedback-screenshot",
    `${evidenceRoot}/user-feedback-exploded-motion-r002.png`, "user-input"],
  ["shipping-scene", "shipping-scene", scenePath, "source-model"],
  ["prefab", "shipping-candidate-prefab",
    `${candidateRoot}/Prefabs/MagneticSlideTileGate12R002Candidate.prefab`,
    "source-model"],
  ["settings", "shared-mechanism-settings",
    `${candidateRoot}/Settings/MagneticSlideTileMechanismSettingsR002.asset`,
    "source-model"],
  ["motion-fix-report", "motion-fix-report",
    `${evidenceRoot}/gate12-motion-fix-report.json`, "validation"],
  ["motion-validation", "motion-validation",
    `${evidenceRoot}/gate12-motion-validation.json`, "validation"],
  ["capture-report", "runtime-validation",
    `${evidenceRoot}/unity-playmode-frames/capture-report.json`, "validation"],
  ["video-probe", "video-validation",
    `${evidenceRoot}/video-probe.json`, "validation"],
  ["browser-validation", "browser-mobile-modal-validation",
    `${evidenceRoot}/browser-mobile-modal-validation.json`, "validation"],
  ["editmode-results", "test-results",
    `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["shipping-board", "shipping-review-board",
    `${evidenceRoot}/gate12-shipping-board-r003.png`, "unity-render"],
  ["motion-board", "motion-review-board",
    `${evidenceRoot}/gate12-motion-board-r003.png`, "unity-render"],
  ["playmode-video", "unity-runtime-recording",
    `${evidenceRoot}/magnetic-slide-gate12-r003-unity-playmode.mp4`,
    "unity-render"],
  ...[
    "library", "hero", "top", "left-oblique", "right-oblique", "low",
    "phone", "max-open", "endpoint-12deg", "endpoint-36deg",
    "endpoint-360deg",
  ].map((view) => [
    `view-${view}`,
    `shipping-view-${view}`,
    `${evidenceRoot}/${view}.png`,
    "unity-render",
  ]),
];

const sourceAssetIds = [
  "magnetic-slide-tile-unity-parity-scene-r011",
  "magnetic-slide-tile-gate12-settings-r002",
  "magnetic-slide-tile-gate12-prefab-r002",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing Gate 12 rev 3 artifact: ${path}`);
  return {
    id: `${modelId}-gate12-${suffix}-r003`,
    stageId: "12-shipping",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "unity-render"
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 12 rev 3 motion correction workflow",
      version: "2026-08-31",
      recipe:
        `${candidateRoot}/Editor/`
        + "MagneticSlideTileGate12R003MotionReviewBuilder.cs",
    },
    provenance: {
      origin: role === "user-input"
        ? "user-provided"
        : "repository-generated",
      contentClass: slot,
      assertedBy: role === "user-input" ? "user" : "assistant",
      gate12Revision: 3,
      candidatePreviewOnly: true,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      sourceEvidenceRevision: 2,
      acceptedStaticViewsPreserved:
        validation.checks.acceptedViewsByteIdentical,
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
  id: "slider-gate12-r003-connected-product-motion",
  stageId: "12-shipping",
  topic: "shipping-motion-review",
  statement:
    "Gate 12 rev 3 preserves seven accepted rev 2 views byte for byte and "
    + "corrects only motion. Travel is TopLocalSlide local -Y, rotation is "
    + "local +Z, top stack residual is 2.794 nm, fixed-axis residual is zero, "
    + "and all 30 detents remain at sMax.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "ready-for-user-review",
  deliveryState: "shipping-scene-candidate-preview-only-not-device",
};
const claimIndex = manifest.claims.findIndex((item) => item.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

gate12.status = "ready_for_review";
gate12.artifactIds = records.map((record) => record.id);
gate12.reviewArtifactIds = [
  `${modelId}-gate12-playmode-video-r003`,
  `${modelId}-gate12-shipping-board-r003`,
  `${modelId}-gate12-motion-board-r003`,
  `${modelId}-gate12-view-max-open-r003`,
  `${modelId}-gate12-view-endpoint-12deg-r003`,
];
gate12.validations = [
  {
    id: "accepted-static-views-preserved",
    status: "pass",
    evidence:
      "Library, Hero, Top, both obliques, Low and Phone match rev 2 SHA-256 byte for byte.",
  },
  {
    id: "connected-product-transform",
    status: "pass",
    evidence:
      `Maximum stack residual ${capture.maximumTopStackResidualMeters} m; `
      + `out-of-plane slide ${capture.maximumOutOfPlaneSlideResidualMeters} m; `
      + `fixed-axis residual ${capture.maximumFixedAxisConstraintResidual}.`,
  },
  {
    id: "endpoint-motion",
    status: "pass",
    evidence:
      "sMax is translation-only at 0°. Endpoint 12°/36°/360° and all 30 detents use local +Z rotation while travel remains sMax.",
  },
  {
    id: "runtime-hierarchy",
    status: "pass",
    evidence:
      "Every renderer remains attached; no pitch, roll, flip, vertical lift, detached component or product-facing exploded pose occurs.",
  },
  {
    id: "focused-unity-tests",
    status: "pass",
    evidence:
      "Focused Unity EditMode/UnityTest suite passed 6/6, including the full connected-product motion sweep.",
  },
  {
    id: "unity-playmode-recording",
    status: "pass",
    evidence:
      "240-frame Unity-only recording covers illegal mid-travel rotation, sMax unlock, 30 detents, illegal return, alignment and close.",
  },
  {
    id: "browser-mobile-modal",
    status: "pass",
    evidence:
      "Gate 12 deep link restored at 390 × 844 mobile viewport; rev 3 motion board modal opened with zero horizontal overflow.",
  },
];
gate12.shippingSpec = {
  ...gate12.shippingSpec,
  sceneSha256: report.shippingSceneSha256,
  candidateDefaultActive: false,
  oldShippingModelDefaultActive: true,
  acceptedStaticViewsPreserved: true,
  maximumTopStackResidualMeters:
    capture.maximumTopStackResidualMeters,
  maximumOutOfPlaneSlideResidualMeters:
    capture.maximumOutOfPlaneSlideResidualMeters,
  maximumFixedAxisConstraintResidual:
    capture.maximumFixedAxisConstraintResidual,
  renderersAttachedEveryFrame: capture.renderersAttachedEveryFrame,
  detentsStayedAtMaximumTravel: capture.detentsStayedAtMaximumTravel,
  observedDetentMask: capture.observedDetentMask,
  gate12Approval: "pending",
  deliveryState: "real-shipping-scene-candidate-preview-only",
  deviceHapticAcceptance: "pending",
  buildInstallPhone: false,
};
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Corrected connected-product motion evidence is ready for explicit visual approval. Device acceptance remains pending.",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((item) => item.stageId === stage.id)
    .map((item) => JSON.stringify(item));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate12-r003-motion-ready-static-views-approved-not-pushed";
manifest.currentState.unityStatus =
  "canonical-scene-connected-motion-candidate-default-disabled";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "pending-not-installed";
manifest.currentState.workbench = "persistent-seven-tab-current-gate12-unity";
manifest.currentState.diagnosis =
  "Gate 12 rev 3 replaces only rejected motion evidence. Converted axes now "
  + "preserve one connected product with zero out-of-plane slide.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-connected-product-motion-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "12-shipping",
  gateRevision: 3,
  decisionState: "motion-visual-approval-pending",
  deliveryState: "shipping-scene-candidate-preview-only",
  sceneSha256: report.shippingSceneSha256,
  acceptedStaticViewsPreserved: true,
  transformMetrics: validation.transformMetrics,
  detentMask: capture.observedDetentMask,
  candidateDefaultActive: false,
  oldShippingModelDefaultActive: true,
  buildInstallPhone: false,
  deviceAcceptance: "pending",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate12: saved.stages[11].status,
  evidenceRevision: saved.stages[11].shippingSpec.revision,
  reviewArtifactIds: saved.stages[11].reviewArtifactIds,
}, null, 2));
