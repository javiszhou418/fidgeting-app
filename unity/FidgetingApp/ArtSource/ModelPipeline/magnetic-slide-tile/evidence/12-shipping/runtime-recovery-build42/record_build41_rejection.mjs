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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/"
  + "12-shipping/runtime-recovery-build42";
const candidate =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const preflightJob =
  "magnetic-slide-build42-20260901T023014Z-95a418b8";
const preflightRoot = `${root}/device-delivery/${preflightJob}`;

const wiring = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${root}/runtime-interaction-wiring-report.json`),
  "utf8"));
const deviceDetails = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${preflightRoot}/device-details.json`),
  "utf8"));
const deviceLock = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${preflightRoot}/device-lock.json`),
  "utf8"));
const editMode = fs.readFileSync(
  resolveRepoPath(`${root}/editmode-focused-tests.xml`),
  "utf8");
const playMode = fs.readFileSync(
  resolveRepoPath(`${root}/playmode-input-tests.xml`),
  "utf8");
const buildNumberTest = fs.readFileSync(
  resolveRepoPath(`${root}/build42-number-test.xml`),
  "utf8");

if (
  !wiring.pass
  || wiring.visualGeometryChanged
  || wiring.materialChanged
  || wiring.hiddenDebugCollidersEnabled !== 0
  || !editMode.includes(
    'testcasecount="33" result="Passed" total="33" passed="33" failed="0"')
  || !playMode.includes(
    'testcasecount="3" result="Passed" total="3" passed="3" failed="0"')
  || !buildNumberTest.includes(
    'testcasecount="1" result="Passed" total="1" passed="1" failed="0"')
  || deviceDetails.result?.deviceProperties?.ddiServicesAvailable !== true
  || deviceDetails.result?.connectionProperties?.tunnelState !== "connected"
  || deviceLock.result?.passcodeRequired !== true
) {
  throw new Error("Build 41 rejection or Build 42 recovery evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
if (
  gate12?.status !== "approved"
  || gate12?.decision?.notes !== "这个是对的"
) {
  throw new Error("Expected visually approved Gate 12 rev 3.");
}
const evidenceRefresh =
  manifest.currentState?.deviceStatus
  === "build-41-rejected-build-42-blocked-before-export-device-locked";

const definitions = [
  ["recovery-recorder", "runtime-recovery-registration-source",
    `${root}/record_build41_rejection.mjs`, "process"],
  ["runtime-wiring-report", "runtime-production-wiring-report",
    `${root}/runtime-interaction-wiring-report.json`, "validation"],
  ["runtime-wiring-log", "runtime-production-wiring-log",
    `${root}/runtime-wiring.log`, "validation"],
  ["editmode-results", "runtime-editmode-results",
    `${root}/editmode-focused-tests.xml`, "validation"],
  ["editmode-log", "runtime-editmode-log",
    `${root}/editmode-focused-tests.log`, "validation"],
  ["playmode-results", "runtime-playmode-input-results",
    `${root}/playmode-input-tests.xml`, "validation"],
  ["playmode-log", "runtime-playmode-input-log",
    `${root}/playmode-input-tests.log`, "validation"],
  ["build42-number-results", "build42-number-results",
    `${root}/build42-number-test.xml`, "validation"],
  ["build42-number-log", "build42-number-log",
    `${root}/build42-number-test.log`, "validation"],
  ["build42-runner", "build42-device-runner",
    `${root}/run_build42_device_delivery.sh`, "process"],
  ["build42-job", "build42-blocked-job",
    `${preflightRoot}/job.env`, "validation"],
  ["build42-device-list", "build42-device-list",
    `${preflightRoot}/device-list.json`, "validation"],
  ["build42-device-details", "build42-device-details",
    `${preflightRoot}/device-details.json`, "validation"],
  ["build42-device-lock", "build42-device-lock",
    `${preflightRoot}/device-lock.json`, "validation"],
  ["shipping-scene", "shipping-scene",
    "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["input-controller", "runtime-input-controller",
    "unity/FidgetingApp/Assets/_EDC/Runtime/EdcSliderController.cs",
    "source-model"],
  ["presentation-gestures", "runtime-presentation-gestures",
    "unity/FidgetingApp/Assets/_EDC/Runtime/SharedPresentationGestureController.cs",
    "source-model"],
  ["camera-framer", "runtime-camera-framer",
    "unity/FidgetingApp/Assets/_EDC/Runtime/EdcPortraitCameraFramer.cs",
    "source-model"],
  ["audio-renderer", "runtime-audio-renderer",
    "unity/FidgetingApp/Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs",
    "source-model"],
  ["shipping-coordinator", "runtime-shipping-coordinator",
    `${candidate}/Runtime/MagneticSlideTileShippingCoordinator.cs`,
    "source-model"],
  ["shipping-mechanism", "runtime-shipping-mechanism",
    `${candidate}/Runtime/MagneticSlideTileShippingMechanism.cs`,
    "source-model"],
  ["mechanism-settings", "runtime-mechanism-settings",
    `${candidate}/Runtime/MagneticSlideTileMechanismSettings.cs`,
    "source-model"],
  ["runtime-builder", "runtime-wiring-builder-source",
    `${candidate}/Editor/MagneticSlideTileGate12R003MotionReviewBuilder.cs`,
    "process"],
  ["playmode-tests", "runtime-playmode-input-test-source",
    `${candidate}/Tests/PlayMode/MagneticSlideTileInputPlayModeTests.cs`,
    "validation"],
  ["playmode-assembly", "runtime-playmode-test-assembly",
    `${candidate}/Tests/PlayMode/FidgetingApp.MagneticSlide.PlayModeTests.asmdef`,
    "validation"],
  ["ios-build-pipeline", "build42-unity-pipeline-source",
    "unity/FidgetingApp/Assets/Editor/IosBuildPipeline.cs", "source-model"],
  ["project-settings", "build42-project-settings",
    "unity/FidgetingApp/ProjectSettings/ProjectSettings.asset", "source-model"],
];

const contractSha256 =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing recovery artifact: ${assetPath}`);
  return {
    id: `${modelId}-${suffix}-build42-r001`,
    stageId: gateId,
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Magnetic Slide Build 42 runtime recovery",
      version: "2026-09-01",
      recipe: `${root}/run_build42_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha256,
      gate12ApprovalExactWording: "这个是对的",
      rejectedBuild: "0.1.0 (41)",
      nextBuildNumber: "42",
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

const build41Claim = manifest.claims.find(
  (claim) => claim.id === "slider-gate12-r003-development-device-delivered");
if (build41Claim) {
  build41Claim.statement =
    "Build 41 was exported, signed, installed and launched, then rejected by "
    + "the user because only direct slide worked; endpoint rotation, pinch, "
    + "orbit/reposition and sound did not.";
  build41Claim.state = "historical-rejected";
  build41Claim.decisionState = "gate12-visual-approval-unchanged";
  build41Claim.deliveryState = "build-41-installed-launched-rejected";
}

const priorRuntimeClaim = manifest.claims.find(
  (claim) => claim.id === "slider-gate12-r003-runtime-interaction-fixed");
if (priorRuntimeClaim) {
  priorRuntimeClaim.state = "superseded-rejected";
  priorRuntimeClaim.deliveryState =
    "build-41-low-fi-runtime-rejected-by-device-use";
}

const recoveryClaim = {
  id: "slider-build41-rejected-production-runtime-recovered",
  stageId: gateId,
  topic: "runtime-interaction-recovery",
  statement:
    "Build 41 is rejected. The active candidate now reuses the shipping input, "
    + "camera, gesture, audio and Haptic coordinators. EditMode 33/33 and real "
    + "PlayMode Input System touch 3/3 passed. Build 42 stopped before Unity "
    + "export because the paired DDI-ready iPhone was locked.",
  confidence: "verified",
  state: "active",
  assertedBy: "user-and-measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "gate12-visual-approval-unchanged",
  deliveryState: "build-42-blocked-before-export-device-locked",
};
const recoveryClaimIndex = manifest.claims.findIndex(
  (claim) => claim.id === recoveryClaim.id);
if (recoveryClaimIndex >= 0)
  manifest.claims[recoveryClaimIndex] = recoveryClaim;
else
  manifest.claims.push(recoveryClaim);

gate12.validations = gate12.validations.filter(
  (validation) => !validation.id.startsWith("build42-runtime-"));
gate12.validations.push(
  {
    id: "build42-runtime-production-wiring",
    status: "pass",
    evidence:
      "Active TopLocalSlide collider, candidate camera target, six audio "
      + "voices and FidgetAppCoordinator semantic routing passed.",
  },
  {
    id: "build42-runtime-editmode",
    status: "pass",
    evidence: "Focused magnetic-slide EditMode suite passed 33/33.",
  },
  {
    id: "build42-runtime-real-input-playmode",
    status: "pass",
    evidence:
      "Dedicated PlayMode suite passed 3/3 using queued TouchState events "
      + "through the shipping scene; no controller method drove motion.",
  },
  {
    id: "build42-runtime-device-preflight",
    status: "blocked",
    evidence:
      "Paired, connected, Developer Mode and DDI ready; passcodeRequired=true. "
      + "No Unity export, Xcode build, install or launch occurred.",
  },
);

const build40 = gate12.shippingSpec?.previousDeviceAttempt;
gate12.shippingSpec = {
  ...gate12.shippingSpec,
  sceneSha256: wiring.shippingSceneSha256,
  runtimeInteractionIntegrated: true,
  runtimeInteractionController: wiring.inputController,
  interactionSurface: wiring.interactionSurface,
  interactionSurfaceParent: "TopLocalSlide",
  interactionCamera: wiring.interactionCamera,
  cameraTarget: wiring.cameraTarget,
  stableCameraBounds: wiring.stableCameraBounds,
  authoredCameraPosePreserved: wiring.authoredCameraPosePreserved,
  audioRenderer: wiring.audioRenderer,
  audioVoices: wiring.audioVoices,
  hapticRoute: wiring.hapticRoute,
  hiddenDebugCollidersEnabled: 0,
  visualGeometryChanged: false,
  materialChanged: false,
  rejectedBuild: {
    jobId: "magnetic-slide-g12-r003-20260901T004637Z-49f0fed4",
    bundleIdentifier: "com.jiaweizhou.fidgetspinner.codex",
    version: "0.1.0",
    buildNumber: "41",
    installed: true,
    launched: true,
    deviceAcceptance: "rejected-low-fi-noninteractive",
    userFailure:
      "Only simple slide worked; no endpoint rotation, pinch, standard "
      + "orbit/reposition or sound.",
  },
  historicalDeviceAttempts: [build40].filter(Boolean),
  nextBuildNumber: "42",
  build42Preflight: {
    jobId: preflightJob,
    buildKey: fs.readFileSync(
      resolveRepoPath(`${preflightRoot}/job.env`),
      "utf8").match(/^buildKey=(.+)$/m)?.[1],
    pairingState: deviceDetails.result?.connectionProperties?.pairingState,
    transportType: deviceDetails.result?.connectionProperties?.transportType,
    tunnelState: deviceDetails.result?.connectionProperties?.tunnelState,
    developerMode:
      deviceDetails.result?.deviceProperties?.developerModeStatus,
    ddiServicesAvailable:
      deviceDetails.result?.deviceProperties?.ddiServicesAvailable,
    passcodeRequired: deviceLock.result?.passcodeRequired,
    status: "blocked-before-unity-export-device-locked",
  },
  buildJobId: null,
  buildKey: null,
  buildNumber: null,
  unityExportSucceeded: false,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  launchedProcessIdentifier: null,
  buildInstallPhone: false,
  deviceAcceptance: "pending-build-42-and-user-validation",
  appStoreSubmitted: false,
};

gate12.deliveryState = {
  decisionState: "approved",
  shippingPromotion: "complete",
  previousBuild: "0.1.0 (41)-rejected-low-fi-noninteractive",
  runtimeFix: "production-stack-tested",
  developmentBuild: "build-42-blocked-before-export-device-locked",
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build-42-and-user-validation",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map((claim) => JSON.stringify(claim));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentState.visualApproval =
  "gate12-r003-approved-exact-wording";
manifest.currentState.unityStatus =
  "approved-candidate-production-runtime-tested";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.deviceStatus =
  "build-41-rejected-build-42-blocked-before-export-device-locked";
manifest.currentState.diagnosis =
  "Build 41 used incomplete runtime wiring. Production gesture, camera, audio "
  + "and Haptic integration now passes real touch tests. Build 42 has not been "
  + "produced because the paired DDI-ready iPhone is locked.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: evidenceRefresh
    ? "build-41-rejection-evidence-refreshed"
    : "build-41-rejected-production-runtime-recovered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  gateRevision: 3,
  visualApprovalExactWording: "这个是对的",
  rejectedBuild: "0.1.0 (41)",
  userFailure:
    "Only simple slide worked; no endpoint rotation, pinch, standard "
    + "orbit/reposition or sound.",
  rootCauses: [
    "Interaction collider did not follow TopLocalSlide.",
    "Camera framer targeted the inactive fallback.",
    "Candidate audio was inactive and semantic routing bypassed the app coordinator.",
    "Build 41 tests did not inject real PlayMode touch or pinch events.",
  ],
  editModeTests: "33/33",
  playModeInputTests: "3/3",
  nextBuildNumber: "42",
  build42Status: "blocked-before-unity-export-device-locked",
  build42JobId: preflightJob,
  visualGeometryChanged: false,
  materialChanged: false,
  appStoreSubmitted: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  editModeTests: "33/33",
  playModeInputTests: "3/3",
  build42JobId: preflightJob,
}, null, 2));
