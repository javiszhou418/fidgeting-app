#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const gateId = "12-shipping";
const jobId = "magnetic-slide-g12-r003-20260901T004637Z-49f0fed4";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003";
const jobRoot = `${evidenceRoot}/device-delivery/${jobId}`;
const exportRoot =
  `unity/FidgetingApp/Builds/iOS/DeviceJobs/${jobId}/Export`;
const appRoot =
  `unity/FidgetingApp/Builds/iOS/DeviceJobs/${jobId}/DerivedData`
  + "/Build/Products/Release-iphoneos/FidgetSpinner.app";
const result = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/delivery-result.json`), "utf8"));
const install = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/install.json`), "utf8"));
const launch = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/launch.json`), "utf8"));
const processes = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/processes.json`), "utf8"));

if (
  result.jobId !== jobId
  || !result.unityExportSucceeded
  || !result.xcodeBuildSucceeded
  || !result.signed
  || !result.installed
  || !result.launched
  || result.appStoreSubmitted
  || install.info?.outcome !== "success"
  || launch.info?.outcome !== "success"
) {
  throw new Error("Development device delivery did not complete.");
}
const launchedPid = launch.result?.process?.processIdentifier;
const running = processes.result?.runningProcesses?.some(
  (process) =>
    process.processIdentifier === launchedPid
    && process.executable?.includes("/FidgetSpinner.app/FidgetSpinner"));
if (!running)
  throw new Error("The launched app process is not present on the iPhone.");

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
if (
  gate12?.status !== "approved"
  || gate12?.decision?.notes !== "这个是对的"
  || gate12?.shippingSpec?.shippingPromotion !== "complete"
) {
  throw new Error("Expected approved and promoted Gate 12 rev 3.");
}

const definitions = [
  ["success-recorder", "delivery-registration-source",
    `${evidenceRoot}/record_device_delivery_success.mjs`, "process"],
  ["job", "device-delivery-job", `${jobRoot}/job.env`, "validation"],
  ["device-details", "physical-device-details",
    `${jobRoot}/device-details.json`, "validation"],
  ["device-lock", "physical-device-lock",
    `${jobRoot}/device-lock.json`, "validation"],
  ["unity-log", "unity-device-export-log",
    `${jobRoot}/unity-export.log`, "validation"],
  ["xcode-log", "xcode-device-build-log",
    `${jobRoot}/xcode-build.log`, "validation"],
  ["install", "physical-device-install-result",
    `${jobRoot}/install.json`, "validation"],
  ["launch", "physical-device-launch-result",
    `${jobRoot}/launch.json`, "validation"],
  ["processes", "physical-device-process-list",
    `${jobRoot}/processes.json`, "validation"],
  ["result", "device-delivery-result",
    `${jobRoot}/delivery-result.json`, "validation"],
  ["build-manifest", "unity-build-manifest",
    `${exportRoot}/FidgetingBuildManifest.json`, "export"],
  ["pbxproj", "xcode-project",
    `${exportRoot}/Unity-iPhone.xcodeproj/project.pbxproj`, "export"],
  ["export-plist", "xcode-info-plist",
    `${exportRoot}/Info.plist`, "export"],
  ["app-plist", "signed-app-info-plist",
    `${appRoot}/Info.plist`, "export"],
  ["app-binary", "signed-app-binary",
    `${appRoot}/FidgetSpinner`, "export"],
];

const contractSha256 =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing delivery artifact: ${assetPath}`);
  return {
    id: `${modelId}-gate12-${suffix}-r003-device`,
    stageId: gateId,
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "export"
        ? "Unity 6000.5.6f1 / Xcode 26.4"
        : "Gate 12 rev 3 development device workflow",
      version: "2026-09-01",
      recipe: `${evidenceRoot}/run_development_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha256,
      gate12ApprovalExactWording: "这个是对的",
      buildJobId: result.jobId,
      buildKey: result.buildKey,
      bundleIdentifier: result.bundleIdentifier,
      version: result.version,
      buildNumber: result.buildNumber,
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
  id: "slider-gate12-r003-development-device-delivered",
  stageId: gateId,
  topic: "development-device-delivery",
  statement:
    "Gate 12 rev 3 shipping default was exported by Unity, signed by Xcode, "
    + "installed and launched on the paired physical iPhone. Process "
    + `${launchedPid} was verified. Device acceptance remains pending user validation.`,
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "approved",
  deliveryState: "installed-launched-pending-user-validation",
};
const claimIndex = manifest.claims.findIndex(
  (candidate) => candidate.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

gate12.shippingSpec = {
  ...gate12.shippingSpec,
  buildJobId: result.jobId,
  buildKey: result.buildKey,
  sourceDigest: result.sourceDigest,
  unityVersion: result.unityVersion,
  xcodeVersion: result.xcodeVersion,
  developmentConfiguration: result.configuration,
  exportPath: result.exportPath,
  appPath: result.appPath,
  bundleIdentifier: result.bundleIdentifier,
  version: result.version,
  buildNumber: result.buildNumber,
  unityExportSucceeded: true,
  xcodeBuildSucceeded: true,
  signed: true,
  installed: true,
  launched: true,
  launchedProcessIdentifier: launchedPid,
  deliveryBlocker: null,
  buildInstallPhone: true,
  deviceAcceptance: "pending-user-validation",
  appStoreSubmitted: false,
};
gate12.deliveryState = {
  decisionState: "approved",
  shippingPromotion: "complete",
  developmentBuild: "complete",
  signed: true,
  installed: true,
  launched: true,
  launchedProcessIdentifier: launchedPid,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
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
manifest.currentState.visualApproval =
  "gate12-r003-approved-exact-wording";
manifest.currentState.unityStatus =
  "approved-candidate-shipping-default";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.deviceStatus =
  "development-build-installed-launched-pending-user-validation";
manifest.currentState.diagnosis =
  "Gate 12 rev 3 is approved, promoted, exported, signed, installed and "
  + "launched on the physical iPhone. User device validation remains pending.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-development-device-installed-launched",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  gateRevision: 3,
  exactApprovalWording: "这个是对的",
  buildJobId: result.jobId,
  buildKey: result.buildKey,
  sourceDigest: result.sourceDigest,
  unityVersion: result.unityVersion,
  xcodeVersion: result.xcodeVersion,
  exportPath: result.exportPath,
  bundleIdentifier: result.bundleIdentifier,
  version: result.version,
  buildNumber: result.buildNumber,
  installed: true,
  launched: true,
  launchedProcessIdentifier: launchedPid,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  jobId: result.jobId,
  bundleIdentifier: result.bundleIdentifier,
  version: result.version,
  buildNumber: result.buildNumber,
  launchedProcessIdentifier: launchedPid,
}, null, 2));
