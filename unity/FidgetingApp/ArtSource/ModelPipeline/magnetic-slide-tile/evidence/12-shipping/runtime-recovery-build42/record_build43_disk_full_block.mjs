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
const jobId = "magnetic-slide-build43-20260901T075038Z-snapshot";
const jobRoot = `${root}/device-delivery/${jobId}`;
const result = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/delivery-result.json`),
  "utf8"));
if (
  result.buildNumber !== "43"
  || !result.unityExportSucceeded
  || result.xcodeBuildSucceeded
  || result.reusable
  || result.installed
  || result.launched
) {
  throw new Error("Build 43 disk-full result is inconsistent.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);
const definitions = [
  ["job", "build43-job", `${jobRoot}/job.env`],
  ["device-list", "build43-device-list", `${jobRoot}/device-list.json`],
  ["device-details", "build43-device-details", `${jobRoot}/device-details.json`],
  ["device-lock", "build43-device-lock", `${jobRoot}/device-lock.json`],
  ["snapshot-hashes", "build43-source-snapshot",
    `${jobRoot}/source-hashes-snapshot.txt`],
  ["after-export-hashes", "build43-source-after-export",
    `${jobRoot}/source-hashes-after-export.txt`],
  ["unity-prepare", "build43-unity-prepare-log",
    `${jobRoot}/unity-prepare-snapshot.log`],
  ["unity-export", "build43-unity-export-log", `${jobRoot}/unity-export.log`],
  ["xcode-build", "build43-xcode-build-log", `${jobRoot}/xcode-build.log`],
  ["result", "build43-delivery-result", `${jobRoot}/delivery-result.json`],
  ["runner", "build43-delivery-runner",
    `${root}/run_build42_device_delivery.sh`],
];
const records = definitions.map(([suffix, slot, path]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-${suffix}-build43-disk-full-r001`,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: suffix === "runner" ? "process" : "validation",
    producer: {
      name: "Magnetic Slide Build 43 device delivery",
      version: "2026-09-01",
      recipe: `${root}/run_build42_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      selectedVariant: "B-balanced-brighter",
      buildNumber: "43",
      protectedSourceHashesStableAfterExport: true,
      reusable: false,
      appStoreSubmitted: false,
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
const lightingTestPath =
  "tools/model-provenance-explorer/tests/"
  + "magnetic-slide-gate12-lighting-rev4.test.mjs";
for (const asset of manifest.assets.filter(
  (item) => item.path === lightingTestPath)) {
  const absolute = resolveRepoPath(lightingTestPath);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}

gate12.validations = gate12.validations.filter(
  (item) => item.id !== "build43-disk-full-block");
gate12.validations.push({
  id: "build43-disk-full-block",
  status: "pass",
  evidence:
    "Build 43 Unity BuildReport succeeded and protected hashes stayed equal. "
    + "Xcode failed before a valid app at dSYM/build.db with 119 MiB free. "
    + "The job is permanently non-reusable; install and launch did not run.",
});
gate12.shippingSpec.build43 = {
  jobId,
  buildKey: result.buildKey,
  sourceDigest: result.sourceDigest,
  variant: result.variant,
  unityExportSucceeded: true,
  protectedSourceHashesStableAfterExport: true,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  reusable: false,
  blocker: result.blocker,
  postFailureDeviceState: result.postFailureDeviceState,
};
gate12.shippingSpec.deviceAcceptance =
  "pending-valid-build-install-and-user-validation";
gate12.deliveryState = {
  decisionState: "approved-variant-b",
  shippingPromotion: "shipping-source-approved",
  build42: "partial-interaction-success-visual-rejected-dark",
  build43: "unity-export-valid-xcode-failed-disk-full-non-reusable",
  nextDevelopmentBuild: "44-or-later-after-disk-and-device-recovery",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-valid-build-install-and-user-validation",
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
manifest.currentState.visualApproval =
  "gate12-r004-variant-b-approved-review-ui";
manifest.currentState.unityStatus =
  "build43-unity-export-success-xcode-failed-disk-full";
manifest.currentState.deviceStatus =
  "paired-disconnected-after-build43-xcode-disk-full";
manifest.currentState.diagnosis =
  "Build 43 protected source hashes stayed stable and Unity export succeeded. "
  + "Xcode failed with only 119 MiB free; no valid signed app, install or launch. "
  + "The paired iPhone is now disconnected.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build43-xcode-disk-full-block",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  jobId,
  buildNumber: "43",
  selectedVariant: "B-balanced-brighter",
  unityBuildReport: "Success",
  protectedSourceHashesStableAfterExport: true,
  xcodeBuildSucceeded: false,
  reusable: false,
  blocker: result.blocker,
  postFailureDeviceState: result.postFailureDeviceState,
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-valid-build-install-and-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  jobId,
  buildNumber: 43,
  unityExportSucceeded: true,
  xcodeBuildSucceeded: false,
  reusable: false,
}, null, 2));
