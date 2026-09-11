import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { loadManifest, resolveRepoPath, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const asset = (id) => manifest.assets.find((candidate) => candidate.id === id);
const readAsset = (id) => JSON.parse(fs.readFileSync(resolveRepoPath(asset(id).path), "utf8"));

test("preserves Gate 06 rev 4 evidence after Gate 06 rev 5 opens", () => {
  assert.equal(gate05.status, "approved");
  assert.equal(gate06.status, "approved");
  assert.equal(gate06.geometrySpec.revision, 5);
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.ok(manifest.assets.some((candidate) => candidate.id === "magnetic-slide-tile-geometry-interactive-r004"));
  assert.equal(manifest.stages[6].status, "approved");
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
});

test("consumes approved source and current mechanism contract hashes", () => {
  const report = readAsset("magnetic-slide-tile-geometry-validation-r004");
  assert.equal(report.contractSha256, "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea");
  assert.equal(report.gate05Source.sha256, "fc0676107d7d9846959a6495edd808e0ffe7dbb7e7625ba2dcc5c7a7287c4f7b");
  assert.equal(report.gate05Source.approvalWording, "可以的");
  assert.equal(report.canonicalGeometryDigest, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.ok(Object.values(report.viewGeometryDigests).every((digest) => digest === report.canonicalGeometryDigest));
});

test("keeps exact provisional envelope and flat raised-axis stack", () => {
  const report = readAsset("magnetic-slide-tile-geometry-validation-r004");
  assert.deepEqual(report.dimensions.bounds.sizeMm, [31, 50, 12]);
  assert.equal(report.dimensions.state, "user-authorized-provisional-not-production-measured");
  assert.deepEqual(report.dimensions.thicknessStack, { bottomMm: 5.875, gapMm: 0.25, topMm: 5.875, sumMm: 12 });
  assert.equal(report.topPlane.maximumDeviationMm, 0);
  assert.equal(report.topPlane.toleranceMm, 0.001);
  assert.equal(report.dimensions.axisBossProtrusionMm, 0.2);
  assert.ok(report.carrierPacking.clearanceBelowPlaneMm >= 0.049);
  assert.equal(report.checks.noCavity, true);
});

test("preserves four grooves, followers, balls and compound motion", () => {
  const report = readAsset("magnetic-slide-tile-geometry-validation-r004");
  assert.equal(report.checks.fourGrooves, true);
  assert.equal(report.checks.grooveRoles, true);
  assert.equal(report.checks.grooveWidthAuthorized, true);
  assert.equal(report.checks.ballCandidatesAuthorized, true);
  assert.equal(report.checks.followersAligned, true);
  assert.equal(report.checks.fixedAxisInvariant, true);
  assert.equal(report.checks.compoundTransform, true);
  assert.equal(report.checks.finiteEndpoints, true);
  assert.equal(report.denseSweep.sampleCount, 3600);
  assert.equal(report.denseSweep.allValid, true);
});

test("passes manifold, normal, UV, tangent and self-motion audits", () => {
  const report = readAsset("magnetic-slide-tile-geometry-validation-r004");
  const audit = readAsset("magnetic-slide-tile-geometry-audit-r004");
  assert.equal(report.checks.manifold, true);
  assert.equal(report.checks.normals, true);
  assert.equal(report.checks.uvs, true);
  assert.equal(report.checks.tangents, true);
  assert.ok(Object.values(report.uvTangentAudit).every((value) => value.invalidGeometricTangents === 0));
  assert.equal(audit.pass, true);
  assert.deepEqual(audit.animatedObjects, []);
});

test("registers the primary GLB and every required view", () => {
  const ids = [
    "magnetic-slide-tile-geometry-interactive-r004",
    "magnetic-slide-tile-geometry-front-r004",
    "magnetic-slide-tile-geometry-back-r004",
    "magnetic-slide-tile-geometry-top-r004",
    "magnetic-slide-tile-geometry-bottom-r004",
    "magnetic-slide-tile-geometry-left-r004",
    "magnetic-slide-tile-geometry-right-r004",
    "magnetic-slide-tile-geometry-workbench-r004",
    "magnetic-slide-tile-geometry-dimensions-r004",
    "magnetic-slide-tile-geometry-pivot-r004",
    "magnetic-slide-tile-geometry-exploded-r004",
    "magnetic-slide-tile-geometry-underside-r004",
    "magnetic-slide-tile-geometry-flat-axis-r004",
    "magnetic-slide-tile-geometry-section-aa-r004",
    "magnetic-slide-tile-geometry-tangency-r004",
    "magnetic-slide-tile-geometry-closed-r004",
    "magnetic-slide-tile-geometry-max-open-r004",
    "magnetic-slide-tile-geometry-detent12-r004",
    "magnetic-slide-tile-geometry-detent36-r004"
  ];
  for (const id of ids) {
    const record = asset(id);
    assert.ok(record);
    const absolute = resolveRepoPath(record.path);
    assert.ok(fs.statSync(absolute).size > 1024);
    assert.equal(sha256File(absolute), record.sha256);
    assert.equal(record.provenance.geometryDigest, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  }
  const glb = fs.readFileSync(resolveRepoPath(asset(ids[0]).path));
  assert.equal(glb.subarray(0, 4).toString("ascii"), "glTF");
});

test("keeps historical material and Simulator scope", () => {
  assert.equal(gate06.geometrySpec.materialScope, "white-clay-only");
  assert.equal(gate06.geometrySpec.finalUnityUsed, false);
  assert.equal(manifest.currentState.simulatorStatus, "not-used");
  assert.equal(
    manifest.currentState.unityStatus,
    "build44-rotation-direction-fix-source-tested"
  );
});

