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
const jobId = "magnetic-slide-build44-20260903T003750Z-snapshot";
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
const editMode = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/unity-editmode-results.xml`),
  "utf8");
const playMode = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/unity-playmode-results.xml`),
  "utf8");
const runtimeLog = fs.readFileSync(
  resolveRepoPath(`${jobRoot}/runtime-console.log`),
  "utf8");

if (
  snapshotHashes !== afterHashes
  || !result.unityExportSucceeded
  || !result.xcodeBuildSucceeded
  || !result.signed
  || !result.installed
  || !result.launched
  || result.appStoreSubmitted
  || result.buildNumber !== "44"
  || !editMode.includes('testcasecount="43" result="Passed"')
  || !playMode.includes('testcasecount="5" result="Passed"')
) {
  throw new Error("Build 44 delivery evidence is incomplete.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
const contract =
  "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const definitions = [
  ["recorder", "build44-success-recorder",
    `${root}/record_build44_delivery_success.mjs`, "process"],
  ["runner", "build44-success-runner",
    `${root}/run_build42_device_delivery.sh`, "process"],
  ["job", "build44-success-job", `${jobRoot}/job.env`, "validation"],
  ["preflight", "build44-success-pipeline-preflight",
    `${jobRoot}/model-pipeline-preflight.json`, "validation"],
  ["prepare-log", "build44-success-prepare-log",
    `${jobRoot}/unity-prepare-snapshot.log`, "validation"],
  ["snapshot-hashes", "build44-success-snapshot-hashes",
    `${jobRoot}/source-hashes-snapshot.txt`, "validation"],
  ["after-hashes", "build44-success-after-export-hashes",
    `${jobRoot}/source-hashes-after-export.txt`, "validation"],
  ["editmode", "build44-success-editmode-results",
    `${jobRoot}/unity-editmode-results.xml`, "validation"],
  ["playmode", "build44-success-playmode-results",
    `${jobRoot}/unity-playmode-results.xml`, "validation"],
  ["export-log", "build44-success-unity-export-log",
    `${jobRoot}/unity-export.log`, "validation"],
  ["xcode-log", "build44-success-xcode-log",
    `${jobRoot}/xcode-build.log`, "validation"],
  ["install", "build44-success-install",
    `${jobRoot}/install.json`, "validation"],
  ["launch", "build44-success-launch",
    `${jobRoot}/launch.json`, "validation"],
  ["runtime", "build44-success-runtime-log",
    `${jobRoot}/runtime-console.log`, "validation"],
  ["processes", "build44-success-processes",
    `${jobRoot}/processes.json`, "validation"],
  ["result", "build44-success-result",
    `${jobRoot}/delivery-result.json`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-build44-success-${suffix}-r001`,
    stageId: gateId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Magnetic Slide Build 44 device delivery",
      version: "2026-09-03",
      recipe: `${root}/run_build42_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contract,
      buildNumber: "44",
      appStoreSubmission: false,
      rev14HybridMaterial: true,
      variantBLighting: true,
      rotationDirectionFix: true,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-gate11-r014-final-visual-approval",
      "magnetic-slide-tile-report-rotation-direction-r001",
    ],
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

const statusPath = "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md";
for (const asset of manifest.assets.filter(
  (candidate) => candidate.path === statusPath)) {
  asset.sha256 = sha256File(resolveRepoPath(statusPath));
  asset.sizeBytes = fs.statSync(resolveRepoPath(statusPath)).size;
}

const rotationClaim = manifest.claims.find(
  (item) => item.id === "slider-rotation-direction-build42-rejected");
if (rotationClaim) {
  rotationClaim.deliveryState =
    "build-44-installed-launched-pending-user-validation";
  rotationClaim.sourceAssetIds = [
    ...new Set([
      ...rotationClaim.sourceAssetIds,
      ...records.map((record) => record.id),
    ]),
  ];
}

gate12.validations = gate12.validations.filter(
  (validation) => ![
    "build44-unity-export",
    "build44-xcode-sign-install-launch",
    "build44-device-runtime",
  ].includes(validation.id));
gate12.validations.push(
  {
    id: "build44-unity-export",
    status: "pass",
    evidence:
      "Pipeline 12/12 preflight, EditMode 43/43, PlayMode 5/5, protected "
      + "source hashes stable before and after export.",
  },
  {
    id: "build44-xcode-sign-install-launch",
    status: "pass",
    evidence:
      "Xcode Release build succeeded; 0.1.0 (44) installed and launched; "
      + `PID ${result.launchedProcessIdentifier} verified alive.`,
  },
  {
    id: "build44-device-runtime",
    status: "partial",
    evidence:
      "Device console captured Unity/Metal startup and Input System init. "
      + "MagneticSlideRuntime interaction markers were not captured in the "
      + "18s console window; user validation remains pending.",
  },
);

gate12.shippingSpec.buildJobId = jobId;
gate12.shippingSpec.buildKey = result.buildKey;
gate12.shippingSpec.buildNumber = "44";
gate12.shippingSpec.unityExportSucceeded = true;
gate12.shippingSpec.protectedSourceStableAfterExport = true;
gate12.shippingSpec.xcodeBuildSucceeded = true;
gate12.shippingSpec.signed = true;
gate12.shippingSpec.installed = true;
gate12.shippingSpec.launched = true;
gate12.shippingSpec.launchedProcessIdentifier =
  result.launchedProcessIdentifier;
gate12.shippingSpec.buildInstallPhone = true;
gate12.shippingSpec.runtimeStartupMarkersCaptured =
  result.runtimeStartupMarkersCaptured;
gate12.shippingSpec.runtimeInteractionMarkersCaptured = false;
gate12.shippingSpec.runtimeAudioPlaybackCaptured = false;
gate12.shippingSpec.iOSGraphicsApiMode = "automatic-default-metal-only";
gate12.shippingSpec.rev14HybridMaterial = true;
gate12.shippingSpec.variantBLighting = true;
gate12.shippingSpec.rotationDirectionFix = true;
gate12.shippingSpec.deviceAcceptance = "pending-user-validation";
gate12.shippingSpec.appStoreSubmitted = false;
gate12.shippingSpec.build44 = {
  requested: true,
  numberConsumed: true,
  devicePreflight: "pass",
  snapshotCreated: true,
  unityExportStarted: true,
  xcodeBuildStarted: true,
  signed: true,
  installed: true,
  launched: true,
  reusable: false,
  jobId,
  exportPath: result.exportPath,
};
gate12.deliveryState.developmentBuild = "0.1.0 (44)-installed-launched";
gate12.deliveryState.build44 =
  "installed-launched-pending-user-validation";
gate12.deliveryState.signed = true;
gate12.deliveryState.installed = true;
gate12.deliveryState.launched = true;
gate12.deliveryState.appStoreSubmitted = false;
gate12.deliveryState.deviceAcceptance = "pending-user-validation";
gate12.readiness = {
  ready: true,
  blockers: [],
  note:
    "Build 44 installed with rev14 hybrid material, Variant B lighting, and "
    + "rotation-direction fix. Device acceptance remains pending user.",
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
manifest.currentState.deviceStatus =
  "build-44-installed-launched-pending-user-validation";
manifest.currentState.unityStatus =
  "rev14-variant-b-shipping-build44-installed";
manifest.currentState.visualApproval =
  "gate11-r014-approved-build44-installed";
manifest.currentState.diagnosis =
  "Build 44 passed pipeline preflight, Unity export, Xcode signing, install "
  + "and launch on wired iPhone 15 Pro Max. Runtime interaction markers were "
  + "not captured in the initial console window. Device acceptance pending.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build-44-installed-launched",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  jobId,
  buildNumber: "44",
  editModeTests: "43/43",
  playModeInputTests: "5/5",
  unityBuildReport: "succeeded",
  xcodeBuild: "succeeded",
  installed: true,
  launched: true,
  runtimeMarkersCaptured: result.runtimeStartupMarkersCaptured,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  jobId,
  pid: result.launchedProcessIdentifier,
}, null, 2));
