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
const jobId = "magnetic-slide-build42-20260901T034218Z-380ac0e4";
const jobRoot = `${root}/device-delivery/${jobId}`;
const jobEnv = fs.readFileSync(resolveRepoPath(`${jobRoot}/job.env`), "utf8");
const exportLog = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/unity-export.log`),
  "utf8");
const deviceDetails = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/device-details.json`),
  "utf8"));
const deviceLock = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/device-lock.json`),
  "utf8"));

if (
  !exportLog.includes("Build Finished, Result: Success.")
  || !exportLog.includes("iOS Device Xcode project created")
  || deviceDetails.result?.connectionProperties?.pairingState !== "paired"
  || deviceDetails.result?.connectionProperties?.tunnelState !== "connected"
  || deviceDetails.result?.deviceProperties?.developerModeStatus !== "enabled"
  || deviceDetails.result?.deviceProperties?.ddiServicesAvailable !== true
  || deviceLock.result?.passcodeRequired !== false
) {
  throw new Error("Build 42 export-guard evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
const definitions = [
  ["recorder", "build42-export-guard-recorder",
    `${root}/record_build42_export_guard_block.mjs`, "process"],
  ["job", "build42-invalidated-export-job",
    `${jobRoot}/job.env`, "validation"],
  ["device-list", "build42-unlocked-device-list",
    `${jobRoot}/device-list.json`, "validation"],
  ["device-details", "build42-unlocked-device-details",
    `${jobRoot}/device-details.json`, "validation"],
  ["device-lock", "build42-unlocked-device-lock",
    `${jobRoot}/device-lock.json`, "validation"],
  ["unity-log", "build42-invalidated-unity-export-log",
    `${jobRoot}/unity-export.log`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-build42-export-guard-${suffix}-r001`,
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
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
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

const claim = manifest.claims.find(
  (item) => item.id === "slider-build41-rejected-production-runtime-recovered");
claim.statement =
  "Build 41 remains rejected. Production runtime tests pass. Build 42 job "
  + `${jobId} reached a successful Unity BuildReport and complete Xcode export, `
  + "but the source-integrity guard invalidated it because ProjectSettings.asset "
  + "changed during export. No Xcode build, signing, install or launch occurred.";
claim.deliveryState = "build-42-export-invalidated-source-drift";
claim.sourceAssetIds = [
  ...new Set([...claim.sourceAssetIds, ...records.map((record) => record.id)]),
];

gate12.validations = gate12.validations.filter(
  (validation) => ![
    "build42-runtime-device-preflight",
    "build42-unity-export",
  ].includes(validation.id));
gate12.validations.push(
  {
    id: "build42-runtime-device-preflight",
    status: "pass",
    evidence:
      "Paired, wired, tunnel connected, Developer Mode enabled, DDI ready "
      + "and passcodeRequired=false.",
  },
  {
    id: "build42-unity-export",
    status: "blocked",
    evidence:
      `Job ${jobId} had a successful BuildReport and complete Xcode markers. `
      + "The export was invalidated before Xcode because ProjectSettings.asset "
      + "changed after the protected source digest was captured.",
  },
);

gate12.shippingSpec.build42Preflight = {
  jobId,
  buildKey: jobEnv.match(/^buildKey=(.+)$/m)?.[1],
  pairingState: deviceDetails.result?.connectionProperties?.pairingState,
  transportType: deviceDetails.result?.connectionProperties?.transportType,
  tunnelState: deviceDetails.result?.connectionProperties?.tunnelState,
  developerMode: deviceDetails.result?.deviceProperties?.developerModeStatus,
  ddiServicesAvailable:
    deviceDetails.result?.deviceProperties?.ddiServicesAvailable,
  passcodeRequired: deviceLock.result?.passcodeRequired,
  status: "passed",
};
gate12.shippingSpec.build42InvalidatedAttempt = {
  jobId,
  sourceDigest: jobEnv.match(/^sourceDigest=(.+)$/m)?.[1],
  exportPath: jobEnv.match(/^exportPath=(.+)$/m)?.[1],
  unityBuildReportSucceeded: true,
  xcodeProjectMarkersPresent: true,
  invalidatedBy: "source-integrity-guard",
  changedProtectedSource:
    "unity/FidgetingApp/ProjectSettings/ProjectSettings.asset",
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  reusable: false,
};
gate12.shippingSpec.deviceAcceptance =
  "pending-valid-build-and-user-validation";
gate12.deliveryState.developmentBuild =
  "build-42-export-invalidated-source-drift";
gate12.deliveryState.deviceAcceptance =
  "pending-valid-build-and-user-validation";

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
  "build-41-rejected-build-42-export-invalidated-source-drift";
manifest.currentState.diagnosis =
  "Build 42 device preflight passed and Unity exported successfully. "
  + "The protected source digest changed when ProjectSettings.asset was "
  + "serialized during export, so the job stopped before Xcode and is not reusable.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build-42-export-invalidated-source-drift",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  gateRevision: 3,
  jobId,
  buildNumber: "42",
  devicePreflight: "passed",
  unityBuildReport: "succeeded",
  xcodeProjectMarkers: "present",
  invalidatedBy: "source-integrity-guard",
  changedProtectedSource:
    "unity/FidgetingApp/ProjectSettings/ProjectSettings.asset",
  xcodeBuild: "not-run",
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  jobId,
}, null, 2));
