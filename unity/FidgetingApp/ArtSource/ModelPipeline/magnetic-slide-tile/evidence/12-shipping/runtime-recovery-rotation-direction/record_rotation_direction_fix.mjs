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
  + "evidence/12-shipping/runtime-recovery-rotation-direction";
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === stageId);
const report = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${root}/rotation-direction-fix-report.json`),
  "utf8",
));
if (
  report.deviceAcceptance !== "failed-rotation-direction"
  || !report.delivery.build44SourceReady
  || report.delivery.build44Attempted
) {
  throw new Error("Rotation direction report is inconsistent.");
}

const definitions = [
  ["report", "rotation-direction-fix-report",
    `${root}/rotation-direction-fix-report.json`],
  ["edit-results", "rotation-direction-editmode-results",
    `${root}/editmode-results.xml`],
  ["edit-log", "rotation-direction-editmode-log",
    `${root}/editmode-tests.log`],
  ["play-results", "rotation-direction-playmode-results",
    `${root}/playmode-results.xml`],
  ["play-log", "rotation-direction-playmode-log",
    `${root}/playmode-tests.log`],
  ["recorder", "rotation-direction-registration-source",
    `${root}/record_rotation_direction_fix.mjs`],
];
const records = definitions.map(([suffix, slot, path]) => {
  const absolute = resolveRepoPath(path);
  return {
    id: `${modelId}-${suffix}-rotation-direction-r001`,
    stageId,
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: suffix === "recorder" ? "process" : "validation",
    producer: {
      name: "Magnetic Slide rotation direction recovery",
      version: "2026-09-01",
      recipe: `${root}/record_rotation_direction_fix.mjs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      reportedBuild: "42",
      build43Reusable: false,
      build44Attempted: false,
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

const refreshedPaths = [
  "unity/FidgetingApp/Assets/_EDC/Runtime/EdcSliderController.cs",
  "unity/FidgetingApp/Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs",
  "unity/FidgetingApp/Assets/_EDC/Candidates/"
    + "MagneticSlideTileGate12R002/Runtime/"
    + "MagneticSlideTileShippingMechanism.cs",
  "unity/FidgetingApp/Assets/Scripts/Product/FidgetAppCoordinator.cs",
  "unity/FidgetingApp/Assets/Scripts/FidgetSpinner/IosHaptics.cs",
  "unity/FidgetingApp/Assets/_EDC/Candidates/"
    + "MagneticSlideTileGate12R002/Tests/PlayMode/"
    + "MagneticSlideTileInputPlayModeTests.cs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate12-runtime-interaction.test.mjs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate12-lighting-rev4.test.mjs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate12-rev2.test.mjs",
  "tools/model-provenance-explorer/tests/workflow-three-phase.test.mjs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate06-rev4.test.mjs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate06-rev5.test.mjs",
  "tools/model-provenance-explorer/tests/"
    + "magnetic-slide-gate07-rev12.test.mjs",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
];
for (const path of refreshedPaths) {
  const absolute = resolveRepoPath(path);
  for (const asset of manifest.assets.filter((item) => item.path === path)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
  }
}

gate12.validations = gate12.validations.filter(
  (item) => item.id !== "build42-rotation-direction-recovery");
gate12.validations.push({
  id: "build42-rotation-direction-recovery",
  status: "pass",
  evidence:
    "Build 42 device acceptance failed because rotation was reversed. "
    + "World-plane touch arcs now follow oriented local +Z at authored, "
    + "orbited, and pinched camera states. EditMode 37/37 and real Input "
    + "System PlayMode 4/4 passed. Build 44 was not attempted.",
});
gate12.shippingSpec.build42 ??= {};
gate12.shippingSpec.build42.rotationDirectionAcceptance =
  "failed-device-validation";
gate12.shippingSpec.build42.exactUserFeedback =
  "现在旋转方向是反的";
gate12.shippingSpec.rotationDirectionFix = {
  sourceReady: true,
  mapping:
    "screen-ray-to-interaction-plane-signed-angle-around-oriented-local-plus-z",
  editModeTests: "37/37",
  playModeInputSystemTests: "4/4",
  visualsChanged: false,
  slideDirectionChanged: false,
  emptySpaceOrbitDirectionChanged: false,
  pinchChanged: false,
  audioRecipeChanged: false,
  hapticRecipeChanged: false,
  directionMetadataCorrected: true,
};
gate12.shippingSpec.deviceAcceptance =
  "pending-build44-install-and-user-validation";
gate12.deliveryState.build42 =
  "device-rejected-dark-lighting-and-reversed-rotation";
gate12.deliveryState.build43 =
  "unity-export-valid-xcode-failed-disk-full-non-reusable";
gate12.deliveryState.nextDevelopmentBuild =
  "44-after-device-reconnect";
gate12.deliveryState.installed = false;
gate12.deliveryState.launched = false;
gate12.deliveryState.appStoreSubmitted = false;
gate12.deliveryState.deviceAcceptance =
  "pending-build44-install-and-user-validation";

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
manifest.currentState.unityStatus =
  "build44-rotation-direction-fix-source-tested";
manifest.currentState.deviceStatus =
  "build42-rejected-rotation-build43-nonreusable-device-disconnected";
manifest.currentState.diagnosis =
  "Build 42 mapped screen atan2 directly to local +Z, reversing visual "
  + "rotation from the shipping camera. Oriented interaction-plane mapping "
  + "and signed detent metadata now pass 37 EditMode and 4 PlayMode tests. "
  + "Disk has 57 GiB free, but the paired iPhone is disconnected. Build 44 "
  + "was not attempted.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "build42-rotation-direction-rejected-source-fixed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: stageId,
  exactUserFeedback: "现在旋转方向是反的",
  build42DeviceAcceptance: "failed-rotation-direction",
  rootCause:
    "screen-space-atan2-sign-applied-directly-to-oriented-local-plus-z",
  correctedMapping:
    "screen-ray-to-plane-signed-angle-around-oriented-local-plus-z",
  editModeTests: "37/37",
  playModeInputSystemTests: "4/4",
  build43Reusable: false,
  build44SourceReady: true,
  build44Attempted: false,
  freeDiskGiB: 57,
  deviceState: "paired-disconnected",
  signed: false,
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-build44-install-and-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  deviceStatus: saved.currentState.deviceStatus,
  editModeTests: "37/37",
  playModeInputSystemTests: "4/4",
  build44SourceReady: true,
  build44Attempted: false,
}, null, 2));
