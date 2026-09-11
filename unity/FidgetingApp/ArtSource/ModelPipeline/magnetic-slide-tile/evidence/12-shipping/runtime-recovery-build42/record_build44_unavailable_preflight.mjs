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
const stageId = "12-shipping";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/12-shipping/runtime-recovery-build42";
const reportPath =
  `${evidenceRoot}/build44-unavailable-preflight-20260903.json`;
const scriptPath =
  `${evidenceRoot}/record_build44_unavailable_preflight.mjs`;
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);
const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(reportPath), "utf8"));
if (
  manifest.revision !== 305
  || gate12?.status !== "approved"
  || report.build44.numberConsumed
) {
  throw new Error("Build 44 unavailable-device preflight state is invalid.");
}

const records = [
  {
    id: "magnetic-slide-build44-unavailable-preflight-20260903",
    slot: "device-preflight",
    path: reportPath,
  },
  {
    id: "magnetic-slide-build44-unavailable-preflight-recorder",
    slot: "pipeline-recorder",
    path: scriptPath,
  },
].map(({ id, slot, path }) => {
  const absolute = resolveRepoPath(path);
  return {
    id,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "validation",
    producer: {
      name: "Build 44 device preflight",
      version: "2026-09-03",
      recipe: scriptPath,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      evidenceRevision: 7,
      buildNumberConsumed: false,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-gate11-r014-final-visual-approval",
    ],
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex(
    (asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
  if (!gate12.artifactIds.includes(record.id))
    gate12.artifactIds.push(record.id);
}

const statusPath =
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md";
for (const asset of manifest.assets.filter(
  (candidate) => candidate.path === statusPath)) {
  asset.sha256 = sha256File(resolveRepoPath(statusPath));
  asset.sizeBytes = fs.statSync(resolveRepoPath(statusPath)).size;
}

gate12.shippingSpec.build44 = {
  requested: true,
  numberConsumed: false,
  devicePreflight: "blocked",
  blocker:
    "CoreDeviceError 1002: No provider was found. Pairing is retained, "
    + "Developer Mode is enabled, tunnel is unavailable, and DDI is false.",
  device: {
    marketingName: report.device.marketingName,
    identifier: report.device.identifier,
    udid: report.device.udid,
    pairingState: report.device.pairingState,
    developerModeStatus: report.device.developerModeStatus,
    tunnelState: report.device.tunnelState,
    ddiServicesAvailable: report.device.ddiServicesAvailable,
    passcodeRequired: report.device.passcodeRequired,
    lastConnectionDate: report.device.lastConnectionDate,
  },
  snapshotCreated: false,
  unityExportStarted: false,
  xcodeBuildStarted: false,
  signed: false,
  installed: false,
  launched: false,
  reusable: false,
};
gate12.deliveryState.build44 =
  "authorized-blocked-device-provider-unavailable-number-unconsumed";
gate12.deliveryState.installed = false;
gate12.deliveryState.launched = false;
gate12.deliveryState.appStoreSubmitted = false;
gate12.deliveryState.deviceAcceptance =
  "pending-build44-install-and-user-validation";
gate12.readiness = {
  ready: true,
  blockers: [
    "Physical iPhone CoreDevice provider and DDI tunnel are unavailable.",
  ],
  note:
    "Rev14 and Variant B remain approved. Build 44 is unconsumed and must "
    + "use a fresh unique export after the device reconnects.",
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
manifest.currentState.deviceStatus =
  "build44-blocked-coredevice-provider-unavailable-number-unconsumed";
manifest.currentState.unityStatus =
  "rev14-variant-b-approved-no-build-started";
manifest.currentState.diagnosis =
  "Unlock retry confirmed a physical paired iPhone with Developer Mode "
  + "enabled. CoreDevice has no provider, tunnel is unavailable, and DDI "
  + "is false. Passcode state is not queryable. Build 44 remains unconsumed.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build44-device-preflight-blocked",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId,
  requestedBuildNumber: 44,
  buildNumberConsumed: false,
  deviceIdentifier: report.device.identifier,
  deviceUdid: report.device.udid,
  pairingState: report.device.pairingState,
  developerModeStatus: report.device.developerModeStatus,
  tunnelState: report.device.tunnelState,
  ddiServicesAvailable: report.device.ddiServicesAvailable,
  passcodeRequired: report.device.passcodeRequired,
  blocker: report.diagnosis.error,
  unityExportStarted: false,
  xcodeBuildStarted: false,
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: report.deviceAcceptance,
});

console.log(JSON.stringify({
  revision: saved.revision,
  build44NumberConsumed: false,
  deviceStatus: saved.currentState.deviceStatus,
}, null, 2));
