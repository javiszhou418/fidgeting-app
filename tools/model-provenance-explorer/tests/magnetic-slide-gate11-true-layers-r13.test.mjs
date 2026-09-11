import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

import {
  loadManifest,
  resolveRepoPath,
} from "../pipeline-core.mjs";

test("magnetic slide approves hybrid rev14 for Build 44", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
  const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
  const spec = gate11.unityParitySpec;
  const evidence =
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/11-unity-parity/rev-014-detail-depth-hybrid";
  const report = JSON.parse(fs.readFileSync(
    resolveRepoPath(`${evidence}/unity-hybrid-report.json`), "utf8"));
  const metrics = JSON.parse(fs.readFileSync(
    resolveRepoPath(`${evidence}/hybrid-detail-metrics.json`), "utf8"));

  assert.equal(gate11.revision, 14);
  assert.equal(gate11.status, "approved");
  assert.equal(gate11.decision.action, "approve");
  assert.equal(
    gate11.decision.notes,
    "批准 rev 14，构建并安装 Build 44");
  assert.equal(gate12.status, "approved");
  assert.equal(spec.rejectedRevision, 13);
  assert.equal(
    spec.rejectedExactWording,
    "我感觉明显还是rev 12细节更多吧");
  assert.deepEqual(spec.retainedHistoricalRevisions, [12, 13]);
  assert.equal(spec.opticalDimensions.substrateInsetMeters, 0.0002800000074785203);
  assert.equal(spec.opticalDimensions.motifInsetMeters, 0.00014000000373926014);
  assert.equal(spec.opticalDimensions.crystalCapThicknessMeters, 0.0002800000074785203);
  assert.ok(Math.abs(spec.opticalDimensions.crystalIor - 1.52) < 1e-5);
  assert.ok(spec.parallax.pixels >= 2.1);
  assert.equal(spec.performance.addedRenderers, 6);
  assert.equal(spec.performance.estimatedAddedDrawCalls, 4);
  assert.equal(spec.boundsUnchanged, true);
  assert.equal(spec.collidersUnchanged, true);
  assert.equal(spec.protectedRuntimeUnchanged, true);
  assert.equal(spec.endpointInterlockLegal, true);
  assert.equal(spec.build44InstallAuthorized, true);
  assert.equal(spec.visualApproval, "approved-rev14");
  assert.equal(report.pass, true);
  assert.equal(metrics.pass, true);
  assert.ok(metrics.hybridToRev12Ratios.laplacianMean >= 0.95);
  assert.ok(metrics.hybridToRev12Ratios.localVariance >= 0.95);
  assert.ok(metrics.hybridToRev12Ratios.edgeDensity >= 0.95);
  assert.match(
    manifest.currentState.deviceStatus,
    /paired-unavailable-build44-not-started/);
  const rejectedRev12 = gate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 12);
  assert.equal(rejectedRev12.status, "rejected-no-visible-layer-depth");
  assert.equal(rejectedRev12.exactUserFeedback, "我还是没看出层次感");
  const rejectedRev13 = gate11.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 13);
  assert.equal(rejectedRev13.status, "rejected-detail-loss-versus-rev12");
  assert.equal(
    rejectedRev13.exactUserFeedback,
    "我感觉明显还是rev 12细节更多吧");
  for (const id of gate11.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset, id);
    assert.ok(fs.existsSync(resolveRepoPath(asset.path)), asset.path);
  }
});
