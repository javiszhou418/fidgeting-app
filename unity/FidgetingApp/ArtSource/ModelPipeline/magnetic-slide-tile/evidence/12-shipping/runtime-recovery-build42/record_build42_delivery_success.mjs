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
const jobId = "magnetic-slide-build42-20260901T035903Z-snapshot";
const jobRoot = `${root}/device-delivery/${jobId}`;
const result = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/delivery-result.json`),
  "utf8"));
const snapshotHashes = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/source-hashes-snapshot.txt`),
  "utf8");
const afterHashes = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/source-hashes-after-export.txt`),
  "utf8");
const runtimeLog = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/runtime-console-interaction.log`),
  "utf8");
const editMode = fs.readFileSync(
  resolveRepoPath(`${root}/editmode-focused-tests.xml`),
  "utf8");
const playMode = fs.readFileSync(
  resolveRepoPath(`${root}/playmode-input-tests.xml`),
  "utf8");
const buildNumber = fs.readFileSync(
  resolveRepoPath(`${root}/build42-number-test.xml`),
  "utf8");

if (
  snapshotHashes !== afterHashes
  || !result.unityExportSucceeded
  || !result.protectedSourceStableAfterExport
  || !result.xcodeBuildSucceeded
  || !result.codesignVerified
  || !result.installed
  || !result.launched
  || result.appStoreSubmitted
  || !runtimeLog.includes("[MagneticSlideRuntime] audio-ready")
  || !runtimeLog.includes("[MagneticSlideRuntime] shipping-coordinator-ready")
  || !runtimeLog.includes("[MagneticSlideRuntime] input-ready")
  || !runtimeLog.includes("[MagneticSlideRuntime] touch-begin")
  || !runtimeLog.includes("[MagneticSlideRuntime] audio-play")
  || !editMode.includes('testcasecount="33" result="Passed"')
  || !playMode.includes('testcasecount="3" result="Passed"')
  || !buildNumber.includes('testcasecount="1" result="Passed"')
) {
  throw new Error("Build 42 delivery evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
const contract =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const definitions = [
  ["recorder", "build42-success-recorder",
    `${root}/record_build42_delivery_success.mjs`, "process"],
  ["runner", "build42-stable-metal-runner",
    `${root}/run_build42_device_delivery.sh`, "process"],
  ["pipeline", "build42-stable-metal-unity-pipeline",
    "unity/FidgetingApp/Assets/Editor/IosBuildPipeline.cs", "source-model"],
  ["job", "build42-success-job", `${jobRoot}/job.env`, "validation"],
  ["prepare-log", "build42-success-prepare-log",
    `${jobRoot}/unity-prepare-snapshot.log`, "validation"],
  ["snapshot-hashes", "build42-success-snapshot-hashes",
    `${jobRoot}/source-hashes-snapshot.txt`, "validation"],
  ["after-hashes", "build42-success-after-export-hashes",
    `${jobRoot}/source-hashes-after-export.txt`, "validation"],
  ["export-log", "build42-success-unity-export-log",
    `${jobRoot}/unity-export.log`, "validation"],
  ["xcode-log", "build42-success-xcode-log",
    `${jobRoot}/xcode-build.log`, "validation"],
  ["install", "build42-success-install",
    `${jobRoot}/install.json`, "validation"],
  ["inventory", "build42-success-device-inventory",
    `${jobRoot}/app-inventory.json`, "validation"],
  ["runtime", "build42-success-runtime-interaction-log",
    `${jobRoot}/runtime-console-interaction.log`, "validation"],
  ["launch", "build42-success-final-launch",
    `${jobRoot}/final-launch.json`, "validation"],
  ["processes", "build42-success-final-processes",
    `${jobRoot}/final-processes.json`, "validation"],
  ["post-device", "build42-post-delivery-device-status",
    `${jobRoot}/post-delivery-device-list.json`, "validation"],
  ["result", "build42-success-result",
    `${jobRoot}/delivery-result.json`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-build42-success-${suffix}-r001`,
    stageId: gateId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Magnetic Slide Build 42 device delivery",
      version: "2026-09-01",
      recipe: `${root}/run_build42_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contract,
      buildNumber: "42",
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

const refreshedEvidence = [
  ["magnetic-slide-tile-editmode-results-build42-r001",
    `${root}/editmode-focused-tests.xml`],
  ["magnetic-slide-tile-editmode-log-build42-r001",
    `${root}/editmode-focused-tests.log`],
  ["magnetic-slide-tile-playmode-results-build42-r001",
    `${root}/playmode-input-tests.xml`],
  ["magnetic-slide-tile-playmode-log-build42-r001",
    `${root}/playmode-input-tests.log`],
  ["magnetic-slide-tile-build42-number-results-build42-r001",
    `${root}/build42-number-test.xml`],
  ["magnetic-slide-tile-build42-number-log-build42-r001",
    `${root}/build42-number-test.log`],
];
for (const [assetId, path] of refreshedEvidence) {
  const asset = manifest.assets.find((item) => item.id === assetId);
  const absolute = resolveRepoPath(path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}

const claim = manifest.claims.find(
  (item) => item.id === "slider-build41-rejected-production-runtime-recovered");
claim.statement =
  "Build 41 remains rejected. Build 42 uses automatic/default iOS graphics "
  + "APIs, which Unity 6 resolves to Metal-only. Job "
  + `${jobId} passed immutable source checks, Unity export, Xcode signing, `
  + "installation and final launch. Device logs contain input, orbit, slide "
  + "and audible semantic-event playback. User device acceptance is pending.";
claim.deliveryState = "build-42-installed-launched-pending-user-validation";
claim.sourceAssetIds = [
  ...new Set([...claim.sourceAssetIds, ...records.map((record) => record.id)]),
];

gate12.validations = gate12.validations.filter(
  (validation) => ![
    "build42-unity-export",
    "build42-xcode-sign-install-launch",
    "build42-device-runtime",
  ].includes(validation.id));
gate12.validations.push(
  {
    id: "build42-unity-export",
    status: "pass",
    evidence:
      "Automatic/default iOS graphics APIs remained stable and resolved to "
      + "Metal-only. Snapshot and after-export protected hashes are identical.",
  },
  {
    id: "build42-xcode-sign-install-launch",
    status: "pass",
    evidence:
      "Xcode Release build and strict codesign passed; device inventory reports "
      + "0.1.0 (42); final process PID 7593 remained alive after 5 seconds.",
  },
  {
    id: "build42-device-runtime",
    status: "pass",
    evidence:
      "Device console captured audio-ready, shipping-coordinator-ready, "
      + "input-ready, touch/orbit/slide input and semantic audio playback.",
  },
);

gate12.shippingSpec.buildJobId = jobId;
gate12.shippingSpec.buildKey = result.buildKey;
gate12.shippingSpec.buildNumber = "42";
gate12.shippingSpec.unityExportSucceeded = true;
gate12.shippingSpec.protectedSourceStableAfterExport = true;
gate12.shippingSpec.xcodeBuildSucceeded = true;
gate12.shippingSpec.signed = true;
gate12.shippingSpec.installed = true;
gate12.shippingSpec.launched = true;
gate12.shippingSpec.launchedProcessIdentifier = 7593;
gate12.shippingSpec.buildInstallPhone = true;
gate12.shippingSpec.runtimeStartupMarkersCaptured = true;
gate12.shippingSpec.runtimeInteractionMarkersCaptured = true;
gate12.shippingSpec.runtimeAudioPlaybackCaptured = true;
gate12.shippingSpec.iOSGraphicsApiMode = "automatic-default-metal-only";
gate12.shippingSpec.postDeliveryConnection = "tunnel-unavailable";
gate12.shippingSpec.deviceAcceptance = "pending-user-validation";
gate12.shippingSpec.appStoreSubmitted = false;
gate12.deliveryState.developmentBuild = "0.1.0 (42)-installed-launched";
gate12.deliveryState.signed = true;
gate12.deliveryState.installed = true;
gate12.deliveryState.launched = true;
gate12.deliveryState.appStoreSubmitted = false;
gate12.deliveryState.deviceAcceptance = "pending-user-validation";

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
manifest.currentState.deviceStatus =
  "build-42-installed-launched-pending-user-validation";
manifest.currentState.diagnosis =
  "Unity 6 iOS automatic/default graphics API mode is the stable Metal-only "
  + "setting. Build 42 passed protected source checks, export, signing, install "
  + "and launch. PID 7593 was verified after relaunch; the device tunnel became "
  + "unavailable during the later confirmation. Device acceptance remains pending.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build-42-installed-launched",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  jobId,
  buildNumber: "42",
  graphicsApiMode: "automatic-default-metal-only",
  sourceStableAfterExport: true,
  editModeTests: "33/33",
  playModeInputTests: "3/3",
  buildNumberTest: "1/1",
  unityBuildReport: "succeeded",
  xcodeBuild: "succeeded",
  codesign: "verified",
  installed: true,
  launched: true,
  runtimeMarkersCaptured: true,
  postDeliveryConnection: "tunnel-unavailable",
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  jobId,
}, null, 2));
