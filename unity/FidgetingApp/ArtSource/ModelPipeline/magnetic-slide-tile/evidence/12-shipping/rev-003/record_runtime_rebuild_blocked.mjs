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
const blockerPath =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
  + "evidence/12-shipping/rev-003/runtime-rebuild-blocker-locked-retry.json";
const blocker = JSON.parse(fs.readFileSync(
  resolveRepoPath(blockerPath), "utf8"));
if (
  blocker.pairingState !== "paired"
  || blocker.developerModeStatus !== "enabled"
  || blocker.tunnelState !== "connected"
  || blocker.ddiServicesAvailable !== true
  || blocker.passcodeRequired !== true
  || blocker.canonicalUnityBuildStarted
) {
  throw new Error("Unexpected runtime rebuild blocker evidence.");
}

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === gateId);
if (
  gate12?.shippingSpec?.runtimeInteractionIntegrated !== true
  || gate12?.shippingSpec?.previousDeviceAttempt?.deviceAcceptance
    !== "failed-noninteractive"
) {
  throw new Error("Runtime interaction fix state is missing.");
}

const assetId = `${modelId}-gate12-runtime-rebuild-locked-r003`;
const asset = {
  id: assetId,
  stageId: gateId,
  slot: "runtime-rebuild-device-blocker",
  path: blockerPath,
  sha256: sha256File(resolveRepoPath(blockerPath)),
  exists: true,
  sizeBytes: fs.statSync(resolveRepoPath(blockerPath)).size,
  role: "validation",
  producer: {
    name: "xcrun devicectl physical-device preflight",
    version: "518.27",
    recipe: "device info details --timeout 30",
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "physical-device-preflight",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256:
      "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    appStoreSubmission: false,
  },
  sourceAssetIds: gate12.reviewArtifactIds,
  sourceClaimIds: [],
};
const assetIndex = manifest.assets.findIndex(
  (candidate) => candidate.id === assetId);
if (assetIndex >= 0) manifest.assets[assetIndex] = asset;
else manifest.assets.push(asset);
if (!gate12.artifactIds.includes(assetId))
  gate12.artifactIds.push(assetId);

gate12.shippingSpec = {
  ...gate12.shippingSpec,
  deliveryBlocker:
    "Physical iPhone is paired, wired, Developer Mode enabled, tunnel "
    + "connected and DDI true, but passcodeRequired is true.",
  unityExportSucceeded: false,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  buildInstallPhone: false,
  deviceAcceptance: "pending-new-build-and-user-validation",
};
gate12.deliveryState = {
  ...gate12.deliveryState,
  developmentBuild: "blocked-before-export",
  blocker: "physical-iphone-locked",
  installed: false,
  launched: false,
  deviceAcceptance: "pending-new-build-and-user-validation",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((id) =>
    manifest.assets.find((candidate) => candidate.id === id)?.sha256);
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
  "runtime-fix-tested-rebuild-blocked-physical-iphone-locked";
manifest.currentState.diagnosis =
  "Build 40 is rejected as noninteractive. The runtime-only fix passes 9/9, "
  + "and the iPhone now has a connected tunnel and DDI services, but "
  + "passcodeRequired is true. No replacement export or install started.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-runtime-rebuild-blocked-physical-iphone-locked",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: gateId,
  gateRevision: 3,
  previousBuild: "0.1.0 (40)-rejected-noninteractive",
  runtimeFixTests: "9/9",
  pairingState: blocker.pairingState,
  developerModeStatus: blocker.developerModeStatus,
  tunnelState: blocker.tunnelState,
  ddiServicesAvailable: blocker.ddiServicesAvailable,
  passcodeRequired: blocker.passcodeRequired,
  replacementBuildStarted: false,
  appStoreSubmitted: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  replacementBuildStarted: false,
}, null, 2));
