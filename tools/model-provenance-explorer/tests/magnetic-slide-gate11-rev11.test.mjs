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
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-011"
);
const read = (name) => JSON.parse(
  fs.readFileSync(path.join(evidence, name), "utf8"));

test("Gate 11 rev 11 remains approved with exact wording", () => {
  assert.ok(manifest.revision >= 258);
  assert.equal(gate11.revision, 11);
  assert.equal(gate11.status, "approved");
  assert.equal(stageReadiness(manifest, "11-unity-parity").ready, true);
  assert.equal(gate11.decision.notes, "可以的，继续");
  assert.equal(gate12.status, "approved");
  assert.equal(gate11.deliveryState.shippingScenePromoted, false);
  assert.equal(gate11.deliveryState.buildInstallPhone, false);
  assert.equal(gate11.deliveryState.deviceAcceptance, "pending");
});

test("same-camera geometry and strict appearance parity pass", () => {
  const report = read("parity-validation.json");
  assert.equal(report.pass, true);
  assert.equal(report.sameCamera.independentCropping, false);
  assert.equal(report.sameCamera.postAlignment, false);
  assert.ok(report.geometry.glbUnitySilhouetteIou > 0.999);
  assert.ok(report.fullFrame.glbUnitySsim > 0.90);
  assert.ok(report.fullFrame.glbUnityObjectSsim > 0.80);
  assert.ok(report.regionalDeltaE76.silver.median < 12);
  assert.ok(report.hotspot.centroidErrorPixels < 50);
  assert.ok(report.hotspot.relativeAreaError < 0.25);
  assert.equal(report.materialPartitions.sideArtworkTriangles, 0);
  assert.equal(report.materialPartitions.undersideArtworkTriangles, 0);
  assert.equal(report.humanInspection.status, "complete");
});

test("Unity PlayMode evidence covers endpoint interlock", () => {
  const capture = read("unity-playmode-frames/unity-playmode-capture-report.json");
  const video = read("unity-playmode-video-validation.json");
  assert.equal(capture.runtimeLevel, "Editor PlayMode");
  assert.equal(capture.frameCount, 540);
  assert.equal(capture.durationSeconds, 18);
  assert.equal(capture.fullRotationDetents, 30);
  assert.equal(capture.endpointInterlock, true);
  assert.equal(capture.productPitchRollDegrees, 0);
  assert.equal(capture.cameraRollDegrees, 0);
  assert.equal(capture.buildInstallPhone, false);
  assert.equal(video.pass, true);
  assert.equal(video.probe.streams[0].width, 1920);
  assert.equal(video.probe.streams[0].height, 1080);
  assert.equal(video.probe.streams[0].nb_read_frames, "540");
});

test("review artifacts exist and retain registered hashes", () => {
  for (const assetId of gate11.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    assert.ok(asset);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(fs.existsSync(absolute), true);
    assert.equal(sha256File(absolute), asset.sha256);
  }
});
