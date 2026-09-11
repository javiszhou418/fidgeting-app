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
  `${evidenceRoot}/build44-unavailable-preflight-retry-20260903T0018Z.json`;
const scriptPath =
  `${evidenceRoot}/record_build44_unavailable_preflight_retry.mjs`;
const statusPath =
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md";
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);
const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(reportPath), "utf8"));
if (
  manifest.revision !== 306
  || gate12?.status !== "approved"
  || report.build44NumberConsumed
) {
  throw new Error("Build 44 retry state is invalid.");
}

for (const [id, slot, path] of [
  [
    "magnetic-slide-build44-unavailable-preflight-retry-20260903T0018Z",
    "device-preflight",
    reportPath,
  ],
  [
    "magnetic-slide-build44-unavailable-preflight-retry-recorder",
    "pipeline-recorder",
    scriptPath,
  ],
]) {
  const absolute = resolveRepoPath(path);
  const record = {
    id,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "validation",
    producer: {
      name: "Build 44 device preflight retry",
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
      "magnetic-slide-build44-unavailable-preflight-20260903",
    ],
    sourceClaimIds: [],
  };
  const index = manifest.assets.findIndex((asset) => asset.id === id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
  if (!gate12.artifactIds.includes(id)) gate12.artifactIds.push(id);
}
for (const asset of manifest.assets.filter(
  (candidate) => candidate.path === statusPath)) {
  asset.sha256 = sha256File(resolveRepoPath(statusPath));
  asset.sizeBytes = fs.statSync(resolveRepoPath(statusPath)).size;
}

gate12.shippingSpec.build44.retryCount = 2;
gate12.shippingSpec.build44.lastRetryAt = report.timestamp;
gate12.shippingSpec.build44.diskFreeGiB = report.diskFreeGiB;
gate12.shippingSpec.build44.lastConnectionDate =
  report.device.lastConnectionDate;
gate12.deliveryState.build44 =
  "authorized-blocked-device-provider-unavailable-after-second-retry";
gate12.readiness.blockers = [
  "Physical iPhone CoreDevice provider and DDI tunnel remain unavailable.",
];

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
  "build44-second-retry-coredevice-provider-unavailable-number-unconsumed";
manifest.currentState.diagnosis =
  "Second connection retry is unchanged: pairing and Developer Mode remain "
  + "valid, but CoreDevice has no provider, tunnel is unavailable, DDI is "
  + "false, and the last connection timestamp did not advance.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build44-device-preflight-retry-blocked",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId,
  retry: 2,
  requestedBuildNumber: 44,
  buildNumberConsumed: false,
  deviceIdentifier: report.device.identifier,
  pairingState: report.device.pairingState,
  developerModeStatus: report.device.developerModeStatus,
  tunnelState: report.device.tunnelState,
  ddiServicesAvailable: report.device.ddiServicesAvailable,
  passcodeRequired: report.device.passcodeRequired,
  blocker: report.diagnosis,
  buildLocksAcquired: false,
  unityPreflightStarted: false,
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
  retry: 2,
  build44NumberConsumed: false,
  deviceStatus: saved.currentState.deviceStatus,
}, null, 2));
