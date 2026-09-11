import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import {
  loadManifest,
  repoRoot,
  sha256File,
  stageReadiness,
} from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const currentGate11 = manifest.stages.find(
  (stage) => stage.id === "11-unity-parity");
const gate11 = currentGate11.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 10);
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010"
);
const read = (name) => JSON.parse(fs.readFileSync(path.join(evidence, name), "utf8"));

test("Gate 11 rev 10 remains blocked stale history", () => {
  assert.ok(manifest.revision >= 205);
  assert.equal(gate11.stageRevision, 10);
  assert.equal(gate11.status, "stale");
  assert.equal(stageReadiness(manifest, "11-unity-parity").ready, true);
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(gate11.unityParitySpec.reviewStatus, "blocked-not-ready-for-review");
  assert.equal(gate11.unityParitySpec.reviewQuestion, null);
  assert.equal(gate11.decision, null);
  assert.equal(gate11.unityParitySpec.deliveryState.shippingSceneModified, false);
  assert.equal(gate11.unityParitySpec.deliveryState.gate12Started, false);
  assert.equal(gate11.unityParitySpec.deliveryState.buildInstallPhoneRun, false);
  assert.equal(gate11.unityParitySpec.deliveryState.visualApproval, "blocked-not-requested");
});

test("raw full-frame validator measures camera, background, hotspot and clay", () => {
  const report = read("full-frame-parity-report.json");
  assert.equal(report.pass, false);
  assert.deepEqual(report.alignmentPolicy.resolution, [1400, 1100]);
  assert.equal(report.alignmentPolicy.sameFullFrame, true);
  assert.equal(report.alignmentPolicy.independentCropping, false);
  assert.equal(report.alignmentPolicy.postAlignment, false);
  assert.ok(report.cameraAndObjectBeforeAlignment.silhouetteIou >= 0.999);
  assert.ok(report.cameraAndObjectBeforeAlignment.centroidErrorPixels < 1);
  assert.ok(report.fullFrame.globalSsim < report.tolerances.fullFrameSsimMin);
  assert.ok(
    report.fullFrame.heatmapAreaFractionOver24
      > report.tolerances.heatmapAreaOver24Max
  );
  assert.ok(report.fullFrame.backgroundMeanAbsoluteError > 0);
  assert.ok(report.fullFrame.regionalDeltaE76.background.mean >= 0);
  assert.equal(report.checks.hotspot, false);
  assert.equal(report.checks.clayGradient, false);
  assert.equal(report.checks.contactShadow, false);
});

test("Unity transport passes while visual parity remains blocked", () => {
  const unity = read("unity-import-parity-report.json");
  const validation = read("final-validation.json");
  assert.equal(unity.pass, true);
  assert.equal(unity.shippingSceneModified, false);
  assert.equal(unity.gate12Started, false);
  assert.equal(unity.buildInstallDevice, false);
  assert.equal(validation.pass, true);
  assert.equal(validation.checks.visualParityCorrectlyBlocked, true);
  assert.equal(validation.checks.focusedUnityTestsPassed, true);
  assert.equal(validation.tests.passed, 7);
  assert.equal(validation.video.streams[0].nb_frames, "72");
  assert.equal(validation.video.format.duration, "6.000000");
});

test("registered Unity review evidence is complete and hashed", () => {
  assert.deepEqual(gate11.reviewArtifactIds, [
    "magnetic-slide-tile-unity-playmode-runtime-recording-r004",
    "magnetic-slide-tile-unity-playmode-runtime-poster-r004",
    "magnetic-slide-tile-unity-playmode-runtime-validation-r004",
    "magnetic-slide-tile-unity-playmode-capture-report-r004",
    "magnetic-slide-tile-unity-parity-interactive-recording-r010",
    "magnetic-slide-tile-unity-parity-full-frame-board-r010",
    "magnetic-slide-tile-unity-parity-unity-target-r010",
    "magnetic-slide-tile-unity-parity-heatmap-r010",
  ]);
  for (const assetId of gate11.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    assert.ok(asset);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(fs.existsSync(absolute), true);
    assert.equal(sha256File(absolute), asset.sha256);
  }
});

test("rev 9 render evidence remains immutable rejected history", () => {
  const rejected = currentGate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 9
  );
  assert.ok(rejected);
  assert.equal(rejected.status, "rejected");
  assert.equal(rejected.preservedForHistory, true);
  assert.equal(rejected.immutableAssetCount, 44);
  for (const assetId of rejected.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(sha256File(absolute), asset.sha256);
    assert.equal(asset.reviewState, "rejected-history");
  }
});
