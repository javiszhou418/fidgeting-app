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
const root =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/12-shipping/runtime-recovery-build42";
const reportPath =
  `${root}/build44-wired-claim-provider-block-20260903T0023Z.json`;
const scriptPath =
  `${root}/record_build44_wired_claim_provider_block.mjs`;
const statusPath =
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md";
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);
const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(reportPath), "utf8"));
if (
  manifest.revision !== 307
  || gate12?.status !== "approved"
  || report.build44NumberConsumed
) {
  throw new Error("Build 44 third preflight state is invalid.");
}

for (const [id, slot, path] of [
  [
    "magnetic-slide-build44-wired-claim-provider-block-20260903T0023Z",
    "device-preflight",
    reportPath,
  ],
  [
    "magnetic-slide-build44-wired-claim-provider-block-recorder",
    "pipeline-recorder",
    scriptPath,
  ],
]) {
  const absolute = resolveRepoPath(path);
  const asset = {
    id,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "validation",
    producer: {
      name: "Build 44 wired-claim device preflight",
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
      "magnetic-slide-build44-unavailable-preflight-retry-20260903T0018Z",
    ],
    sourceClaimIds: [],
  };
  const existing = manifest.assets.findIndex((item) => item.id === id);
  if (existing >= 0) manifest.assets[existing] = asset;
  else manifest.assets.push(asset);
  if (!gate12.artifactIds.includes(id)) gate12.artifactIds.push(id);
}
for (const asset of manifest.assets.filter(
  (item) => item.path === statusPath)) {
  asset.sha256 = sha256File(resolveRepoPath(statusPath));
  asset.sizeBytes = fs.statSync(resolveRepoPath(statusPath)).size;
}

gate12.shippingSpec.build44.retryCount = 3;
gate12.shippingSpec.build44.lastRetryAt = report.timestamp;
gate12.shippingSpec.build44.userReportedState = report.userReportedState;
gate12.shippingSpec.build44.observedState = report.observedState;
gate12.shippingSpec.build44.numberConsumed = false;
gate12.deliveryState.build44 =
  "authorized-third-retry-provider-unavailable-number-unconsumed";
gate12.readiness.blockers = [
  "CoreDevice provider is absent despite the user-reported wired state.",
];

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((id) =>
    manifest.assets.find((asset) => asset.id === id)?.sha256);
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
manifest.currentState.deviceStatus =
  "build44-third-retry-provider-unavailable-number-unconsumed";
manifest.currentState.diagnosis =
  "The user reported a wired connected device, but local devicectl still "
  + "reports CoreDeviceError 1002, tunnel unavailable and DDI false. "
  + "Lock-state lookup fails with CoreDeviceError 1011.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build44-wired-claim-provider-block",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId,
  retry: 3,
  requestedBuildNumber: 44,
  buildNumberConsumed: false,
  userReportedState: report.userReportedState,
  observedState: report.observedState,
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
  build44NumberConsumed: false,
  deviceStatus: saved.currentState.deviceStatus,
}, null, 2));
