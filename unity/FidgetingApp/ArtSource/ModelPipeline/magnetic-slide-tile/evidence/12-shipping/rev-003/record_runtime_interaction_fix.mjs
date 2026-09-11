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
const gateId = "12-shipping";
const root =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003";
const candidate =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const wiring = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${root}/runtime-interaction-wiring-report.json`), "utf8"));
const testXml = fs.readFileSync(
  resolveRepoPath(`${root}/runtime-interaction-tests.xml`), "utf8");
if (
  !wiring.pass
  || wiring.visualGeometryChanged
  || wiring.materialChanged
  || wiring.hiddenDebugCollidersEnabled !== 0
  || !testXml.includes('testcasecount="9" result="Passed"')
) {
  throw new Error("Runtime interaction fix evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
if (
  gate12?.status !== "approved"
  || gate12?.decision?.notes !== "这个是对的"
) {
  throw new Error("Expected visually approved Gate 12 rev 3.");
}

const definitions = [
  ["runtime-fix-recorder", "runtime-fix-registration-source",
    `${root}/record_runtime_interaction_fix.mjs`, "process"],
  ["runtime-wiring-report", "runtime-interaction-wiring-report",
    `${root}/runtime-interaction-wiring-report.json`, "validation"],
  ["runtime-wiring-log", "runtime-interaction-wiring-log",
    `${root}/runtime-interaction-wiring.log`, "validation"],
  ["runtime-tests", "runtime-interaction-test-results",
    `${root}/runtime-interaction-tests.xml`, "validation"],
  ["runtime-test-log", "runtime-interaction-test-log",
    `${root}/runtime-interaction-tests.log`, "validation"],
  ["shipping-scene-runtime", "shipping-scene",
    "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["slider-controller", "runtime-input-controller",
    "unity/FidgetingApp/Assets/_EDC/Runtime/EdcSliderController.cs",
    "source-model"],
  ["shipping-coordinator-runtime", "runtime-coordinator-source",
    `${candidate}/Runtime/MagneticSlideTileShippingCoordinator.cs`,
    "source-model"],
  ["shipping-mechanism-runtime", "runtime-mechanism-source",
    `${candidate}/Runtime/MagneticSlideTileShippingMechanism.cs`,
    "source-model"],
  ["runtime-builder", "runtime-wiring-builder-source",
    `${candidate}/Editor/MagneticSlideTileGate12R003MotionReviewBuilder.cs`,
    "process"],
  ["runtime-test-source", "runtime-interaction-test-source",
    `${candidate}/Tests/Editor/MagneticSlideTileGate12R002Tests.cs`,
    "validation"],
];
const contractSha256 =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing runtime fix artifact: ${assetPath}`);
  return {
    id: `${modelId}-gate12-${suffix}-r003`,
    stageId: gateId,
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 12 rev 3 runtime interaction fix",
      version: "2026-08-31",
      recipe: `${candidate}/Editor/MagneticSlideTileGate12R003MotionReviewBuilder.cs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha256,
      gate12ApprovalExactWording: "这个是对的",
      previousRejectedBuild: "0.1.0 (40)",
      visualGeometryChanged: false,
      materialChanged: false,
      appStoreSubmission: false,
    },
    sourceAssetIds: gate12.reviewArtifactIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
  if (!gate12.artifactIds.includes(record.id))
    gate12.artifactIds.push(record.id);
}

const claim = {
  id: "slider-gate12-r003-runtime-interaction-fixed",
  stageId: gateId,
  topic: "runtime-interaction",
  statement:
    "Device build 0.1.0 (40) was rejected as noninteractive. The approved "
    + "candidate now owns the active EdcSliderController and legal top-surface "
    + "collider; pointer input drives slide, endpoint rotation, detents and "
    + "aligned closure without changing geometry or materials.",
  confidence: "verified",
  state: "active",
  assertedBy: "user-and-measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "visual-approval-unchanged",
  deliveryState: "runtime-fix-tested-new-device-build-required",
};
const claimIndex = manifest.claims.findIndex(
  (candidateClaim) => candidateClaim.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

gate12.shippingSpec = {
  ...gate12.shippingSpec,
  sceneSha256: wiring.shippingSceneSha256,
  runtimeInteractionIntegrated: true,
  runtimeInteractionController: wiring.inputController,
  interactionSurface: wiring.interactionSurface,
  interactionCamera: wiring.interactionCamera,
  hiddenDebugCollidersEnabled: 0,
  visualGeometryChanged: false,
  materialChanged: false,
  previousDeviceAttempt: {
    jobId: "magnetic-slide-g12-r003-20260831T094630Z-4a901ebf",
    bundleIdentifier: "com.jiaweizhou.fidgetspinner.codex",
    version: "0.1.0",
    buildNumber: "40",
    installed: true,
    launched: true,
    deviceAcceptance: "failed-noninteractive",
    exactUserFeedback: "这个磁吸推牌不可交互",
  },
  buildJobId: null,
  buildKey: null,
  unityExportSucceeded: false,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  launchedProcessIdentifier: null,
  buildInstallPhone: false,
  deviceAcceptance: "failed-build-40-new-build-required",
  appStoreSubmitted: false,
};
gate12.deliveryState = {
  decisionState: "approved",
  shippingPromotion: "complete",
  previousBuild: "0.1.0 (40)-rejected-noninteractive",
  runtimeFix: "tested",
  developmentBuild: "new-build-required",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-new-build-and-user-validation",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((candidateClaim) => candidateClaim.stageId === stage.id)
    .map((candidateClaim) => JSON.stringify(candidateClaim));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentState.visualApproval =
  "gate12-r003-approved-runtime-only-fix";
manifest.currentState.unityStatus =
  "approved-candidate-interaction-wired";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.deviceStatus =
  "build-40-rejected-noninteractive-new-build-required";
manifest.currentState.diagnosis =
  "The visual candidate did not inherit the disabled fallback model's "
  + "EdcSliderController or collider. Runtime wiring is fixed and tested; "
  + "build 40 is rejected and must not be reused.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-build-40-rejected-runtime-interaction-fixed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  gateRevision: 3,
  exactUserFeedback: "这个磁吸推牌不可交互",
  previousBuild: "0.1.0 (40)",
  previousDeviceAcceptance: "failed-noninteractive",
  rootCause:
    "Approved candidate had no active EdcSliderController or collider.",
  sceneSha256: wiring.shippingSceneSha256,
  focusedTests: "9/9",
  visualGeometryChanged: false,
  materialChanged: false,
  newBuildRequired: true,
  appStoreSubmitted: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  sceneSha256: wiring.shippingSceneSha256,
  focusedTests: "9/9",
}, null, 2));
