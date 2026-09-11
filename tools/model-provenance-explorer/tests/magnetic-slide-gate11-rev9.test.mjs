import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009"
);
const read = (name) => JSON.parse(fs.readFileSync(path.join(evidence, name), "utf8"));

test("Gate 11 rev 9 remains rejected immutable history", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(gate11.revision, 11);
  assert.equal(gate11.status, "approved");
  const rejected = gate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 9
  );
  assert.ok(rejected);
  assert.equal(rejected.status, "rejected");
  assert.match(rejected.decision.notes, /Internal quality review rejects Gate 11 rev 9/);
  assert.equal(rejected.preservedForHistory, true);
  assert.equal(rejected.immutableAssetCount, 44);
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(manifest.currentState.shippingAssetUnchanged, false);
  assert.equal(
    manifest.currentState.visualApproval,
    "gate12-r004-variant-b-approved-review-ui"
  );
});

test("Unity import preserves exact four-track transport and provisional envelope", () => {
  const report = read("unity-import-parity-report.json");
  assert.equal(report.pass, true);
  assert.deepEqual(report.sortedBoundsMeters.map((value) => Number(value.toFixed(3))), [
    0.012,
    0.031,
    0.05,
  ]);
  assert.equal(report.renderMeshCount, 8);
  assert.equal(report.renderVertexCount, 80102);
  assert.equal(report.renderTriangleCount, 99280);
  assert.deepEqual(report.collisionTriangleCounts, [108, 108]);
  assert.equal(report.fixedAxisFound, true);
  assert.equal(report.fourGroovesFound, true);
  assert.equal(report.detentCount, 30);
  assert.equal(report.detentStepDegrees, 12);
  assert.equal(report.provisionalDimensions, true);
  assert.equal(report.shippingSceneModified, false);
  assert.equal(report.buildInstallDevice, false);
});

test("rev 9 keeps its measured metrics without claiming full-frame parity", () => {
  const report = read("parity-report.json");
  assert.equal(report.pass, true);
  assert.ok(report.visual.silhouetteIoU >= 0.995);
  assert.ok(report.visual.silhouetteSsim >= 0.995);
  assert.ok(report.visual.edgeDistancePixels.max <= 1);
  assert.ok(report.material.bloodRed.deltaE2000 <= 4);
  assert.ok(report.material.brightReflection.deltaE2000 <= 6);
  assert.ok(report.material.black.deltaE2000 <= 2.5);
  assert.ok(report.material.highlightCoverage.relativeError <= 0.05);
  assert.ok(report.material.highlightCoverage.centroidMaxAxisErrorPixels <= 2);
  assert.equal(report.material.clippedUnityPixelFraction, 0);
  assert.equal(report.material.zeroEmission, true);
  const rejected = gate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 9
  );
  assert.match(rejected.decision.notes, /despite passing silhouette metrics/);
});

test("final validation covers interactive recording and focused Unity tests", () => {
  const validation = read("final-validation.json");
  assert.equal(validation.pass, true);
  assert.equal(validation.tests.total, 6);
  assert.equal(validation.tests.passed, 6);
  assert.equal(validation.tests.failed, 0);
  assert.equal(validation.video.streams[0].nb_frames, "72");
  assert.equal(validation.video.format.duration, "6.000000");
  assert.ok(Object.values(validation.checks).every(Boolean));
});

test("Gate 11 rev 9 visual review assets keep their original hashes", () => {
  const rejected = gate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 9
  );
  assert.deepEqual(rejected.reviewArtifactIds, [
    "magnetic-slide-tile-unity-parity-interactive-recording-r009",
    "magnetic-slide-tile-unity-parity-parity-board-r009",
    "magnetic-slide-tile-unity-parity-unity-target-r009",
    "magnetic-slide-tile-unity-parity-unity-open-r009",
  ]);
  for (const assetId of rejected.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    assert.ok(asset);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(fs.existsSync(absolute), true);
    assert.equal(sha256File(absolute), asset.sha256);
  }
});

test("stable Unity workbench gates approval on the complete runtime recording", () => {
  const browser = read("browser-validation.json");
  const app = fs.readFileSync(
    path.join(repoRoot, "tools/model-provenance-explorer/app.js"),
    "utf8"
  );
  assert.equal(browser.pass, true);
  assert.equal(browser.desktop.currentGate, "11");
  assert.equal(browser.desktop.approved, "10");
  assert.equal(browser.desktop.roadmap, 12);
  assert.equal(browser.desktop.workspaceTabs, 7);
  assert.equal(browser.desktop.approvalDisabled, true);
  assert.equal(browser.unlocked.approvalDisabled, false);
  assert.equal(browser.restored.approvalDisabled, false);
  assert.doesNotMatch(browser.restored.route, /asset=/);
  assert.equal(browser.mobile.bodyWidth, 390);
  assert.equal(browser.runtimeExceptionCount, 0);
  assert.equal(browser.loadingFailureCount, 0);
  assert.match(app, /magnetic-slide-tile-gate11-r009-recording-complete/);
  assert.match(app, /请先完整播放 6 秒真实 Unity 录屏/);
  assert.match(app, /Gate 10 四轨 FBX SHA-256/);
  assert.match(app, /const shouldReturnThroughHistory/);
});

