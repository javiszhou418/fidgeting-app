import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

import {
  loadManifest,
  resolveRepoPath,
} from "../pipeline-core.mjs";

test("magnetic slide records layered material review and blocks Build 44", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
  const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
  const evidence =
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/11-unity-parity/rev-012-layered-material";
  const report = JSON.parse(fs.readFileSync(
    resolveRepoPath(`${evidence}/unity-layered-material-report.json`),
    "utf8"));
  const metrics = JSON.parse(fs.readFileSync(
    resolveRepoPath(`${evidence}/layered-material-image-metrics.json`),
    "utf8"));

  assert.equal(gate11.revision, 12);
  assert.equal(gate11.status, "ready_for_review");
  assert.equal(gate11.decision, null);
  assert.equal(gate12.status, "stale");
  assert.ok(
    Math.abs(gate11.unityParitySpec.materialValues.coatIor - 1.52) < 1e-5);
  assert.equal(gate11.unityParitySpec.materialValues.emission, 0);
  assert.equal(gate11.unityParitySpec.performance.topPasses, 1);
  assert.equal(gate11.unityParitySpec.performance.addedRenderers, 0);
  assert.equal(gate11.unityParitySpec.performance.addedDrawCalls, 0);
  assert.equal(gate11.unityParitySpec.build44InstallAuthorized, false);
  assert.equal(report.protectedRuntimeUnchanged, true);
  assert.equal(report.geometryMeshInstancesUnchanged, true);
  assert.equal(report.boundsCenterDeltaMeters, 0);
  assert.equal(report.boundsSizeDeltaMeters, 0);
  assert.equal(metrics.pass, true);
  assert.equal(metrics.checks.deepRedPresent, true);
  assert.equal(metrics.checks.localVariationVisible, true);
  assert.equal(metrics.checks.highlightClippingBelowHalfPercent, true);
  assert.match(
    manifest.currentState.deviceStatus,
    /build42-rejected-material-flatness/);
  assert.match(
    manifest.currentState.unityStatus,
    /build44-install-blocked/);
  for (const id of gate11.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset, id);
    assert.ok(fs.existsSync(resolveRepoPath(asset.path)), asset.path);
  }
});
