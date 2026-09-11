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
const jobId = "magnetic-slide-build42-20260901T035013Z-snapshot";
const jobRoot = `${root}/device-delivery/${jobId}`;
const jobEnv = fs.readFileSync(resolveRepoPath(`${jobRoot}/job.env`), "utf8");
const exportLog = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/unity-export.log`),
  "utf8");
const mutation = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/source-mutation.json`),
  "utf8"));
const deviceLock = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/device-lock.json`),
  "utf8"));
const expectedPath =
  "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/"
  + "ProjectSettings/ProjectSettings.asset";

if (
  !exportLog.includes("Build Finished, Result: Success.")
  || !exportLog.includes("iOS Device Xcode project created")
  || exportLog.includes("ConfigureIosBuild (bool,string")
  || deviceLock.result?.passcodeRequired !== false
  || mutation.changes?.length !== 1
  || mutation.changes[0].path !== expectedPath
  || mutation.changes[0].beforeSha256
    !== "fc6985e3123990dc73ae0f6c22db049a11fe8eab047fca54b480e7f8956e525e"
  || mutation.changes[0].afterSha256
    !== "1ba8056260584f82a22891706f5a63caf05f7a3b3361b928a31c4cfa4df65ede"
) {
  throw new Error("Repeated Build 42 mutation evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
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
const contract =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const definitions = [
  ["recorder", "build42-repeated-mutation-recorder",
    `${root}/record_build42_repeated_source_mutation.mjs`, "process"],
  ["runner", "build42-snapshot-safe-runner",
    `${root}/run_build42_device_delivery.sh`, "process"],
  ["job", "build42-repeated-invalidated-job",
    `${jobRoot}/job.env`, "validation"],
  ["prepare-log", "build42-snapshot-prepare-log",
    `${jobRoot}/unity-prepare-snapshot.log`, "validation"],
  ["snapshot-hashes", "build42-snapshot-source-hashes",
    `${jobRoot}/source-hashes-snapshot.txt`, "validation"],
  ["after-hashes", "build42-after-export-source-hashes",
    `${jobRoot}/source-hashes-after-export.txt`, "validation"],
  ["mutation", "build42-exact-source-mutation",
    `${jobRoot}/source-mutation.json`, "validation"],
  ["export-log", "build42-repeated-invalidated-export-log",
    `${jobRoot}/unity-export.log`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-build42-repeated-mutation-${suffix}-r001`,
    stageId: gateId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Magnetic Slide Build 42 snapshot-safe delivery",
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

const claim = manifest.claims.find(
  (item) => item.id === "slider-build41-rejected-production-runtime-recovered");
claim.statement =
  "Build 41 remains rejected and production runtime tests pass. Build 42 "
  + `${jobId} prepared PlayerSettings before its immutable digest and passed `
  + "5-second ProjectSettings plus 3-second source stability intervals. Unity "
  + "then normalized iOS graphics API automatic mode from 0 to 1 during export, "
  + "changing only ProjectSettings.asset. The job stopped before Xcode.";
claim.deliveryState =
  "build-42-repeated-export-invalidated-unity-graphics-api-normalization";
claim.sourceAssetIds = [
  ...new Set([...claim.sourceAssetIds, ...records.map((record) => record.id)]),
];

gate12.validations = gate12.validations.filter(
  (validation) => validation.id !== "build42-unity-export");
gate12.validations.push({
  id: "build42-unity-export",
  status: "blocked",
  evidence:
    `Job ${jobId} passed immutable snapshot preparation and Unity BuildReport. `
    + "Unity changed ProjectSettings iOSSupport m_Automatic from 0 to 1 during "
    + "export; the protected hash changed fc6985e3… to 1ba80562….",
});

gate12.shippingSpec.build42RepeatedInvalidatedAttempt = {
  jobId,
  buildKey: jobEnv.match(/^buildKey=(.+)$/m)?.[1],
  buildNumber: "42",
  projectSettingsHashBefore:
    jobEnv.match(/^projectSettingsHashBefore=(.+)$/m)?.[1],
  projectSettingsHashSnapshot:
    jobEnv.match(/^projectSettingsHashSnapshot=(.+)$/m)?.[1],
  projectSettingsStableIntervalSeconds: 5,
  sourceStableIntervalSeconds: 3,
  unityBuildReportSucceeded: true,
  xcodeProjectMarkersPresent: true,
  exactMutation:
    "m_BuildTargetGraphicsAPIs[iOSSupport].m_Automatic: 0 -> 1",
  mutationWriter: "Unity BuildPipeline normalization",
  concurrentCanonicalWriterObserved: false,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  reusable: false,
};
gate12.shippingSpec.deviceAcceptance =
  "pending-valid-build-and-user-validation";
gate12.deliveryState.developmentBuild =
  "build-42-repeated-export-invalidated-unity-graphics-api-normalization";

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
  "build-41-rejected-build-42-repeated-export-invalidated";
manifest.currentState.diagnosis =
  "The original mutation was coordinator-owned PlayerSettings setup after "
  + "snapshot. After moving setup before the snapshot, Unity BuildPipeline "
  + "still normalized iOS graphics API m_Automatic from 0 to 1 during export. "
  + "No concurrent canonical writer was present; both exports remain non-reusable.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build-42-repeated-export-invalidated",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  jobId,
  buildNumber: "42",
  projectSettingsStableSeconds: 5,
  sourceStableSeconds: 3,
  unityBuildReport: "succeeded",
  exactMutation:
    "m_BuildTargetGraphicsAPIs[iOSSupport].m_Automatic: 0 -> 1",
  mutationWriter: "Unity BuildPipeline normalization",
  concurrentCanonicalWriterObserved: false,
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
