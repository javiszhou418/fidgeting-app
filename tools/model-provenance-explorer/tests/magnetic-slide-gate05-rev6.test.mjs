import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { loadManifest, resolveRepoPath, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const asset = (id) => manifest.assets.find((candidate) => candidate.id === id);
const readAsset = (id) => JSON.parse(fs.readFileSync(resolveRepoPath(asset(id).path), "utf8"));
const report = readAsset("magnetic-slide-tile-blockout-validation-r006");
const audit = readAsset("magnetic-slide-tile-blockout-audit-r006");
const comparison = readAsset("magnetic-slide-tile-blockout-comparison-r006");

test("persists rev 5 partial approval and opens rev 6", () => {
  assert.equal(report.partialApproval.accepted, "Gate 05 rev 5 hierarchy and kinematics");
  assert.equal(report.partialApproval.rejected, "recessed/concave BottomExterior top surface");
  assert.equal(report.partialApproval.supersedesRevision, 5);
  assert.equal(gate05.blockoutSpec.revision, 6);
  assert.equal(gate05.status, "ready_for_review");
  assert.equal(manifest.currentStageId, "05-blockout");
  assert.ok(gate05.reviewArtifactIds.includes("magnetic-slide-tile-blockout-interactive-r006"));
  assert.ok(manifest.assets.some((candidate) => candidate.id === "magnetic-slide-tile-blockout-interactive-r005"));
});

test("proves the visible bottom top skin is one flat plane", () => {
  assert.equal(report.flatPlaneMetrics.sampleCount, 1218);
  assert.equal(report.flatPlaneMetrics.stepMm, 1);
  assert.equal(report.flatPlaneMetrics.toleranceMm, 0.001);
  assert.equal(report.flatPlaneMetrics.maximumDeviationMm, 0);
  assert.equal(report.flatPlaneMetrics.minimumZMm, 5.875);
  assert.equal(report.flatPlaneMetrics.maximumZMm, 5.875);
  assert.equal(report.flatPlaneMetrics.minimumTopFacingVertexZMm, 5.875);
  assert.equal(report.checks.flatPlaneWithinTolerance, true);
  assert.equal(report.checks.noTopSkinVertexBelowPlane, true);
});

test("blocks every rejected recess representation", () => {
  assert.equal(report.checks.noBottomRecessModifier, true);
  assert.equal(report.checks.noNegativeRecessDepth, true);
  assert.equal(report.checks.noConcaveCircularSurface, true);
  assert.equal(audit.checks.noBottomModifiers, true);
  assert.equal(audit.checks.noRecessDepth, true);
  assert.equal(audit.checks.noCavity, true);
});

test("keeps the axis raised and carrier under the plane", () => {
  assert.ok(report.dimensionsMm.axisBossExposedProtrusion > 0);
  assert.equal(report.carrierPacking.exteriorVisible, false);
  assert.ok(report.carrierPacking.clearanceBelowPlaneMm >= 0.049);
  assert.equal(report.checks.axisBossPositive, true);
  assert.equal(report.checks.carrierHiddenBelowPlane, true);
});

test("changes only rejected bottom geometry", () => {
  assert.equal(comparison.pass, true);
  assert.equal(comparison.checks.acceptedMeshesUnchanged, true);
  assert.equal(comparison.checks.bottomExteriorChanged, true);
  assert.equal(comparison.checks.rejectedUpperRimRemoved, true);
  assert.deepEqual(comparison.changedGeometry, ["BottomExterior"]);
  for (const unchanged of Object.values(comparison.unchangedMeshes)) assert.equal(unchanged, true);
});

test("preserves four grooves, transforms and containment", () => {
  assert.equal(report.checks.fourTopUndersideGrooves, true);
  assert.equal(report.checks.hierarchyExact, true);
  assert.equal(report.checks.axisInvariant, true);
  assert.equal(report.checks.topAlwaysAbovePlane, true);
  assert.equal(report.denseSweep.sampleCount, 3600);
  assert.equal(report.denseSweep.angularStepDegrees, 0.5);
  assert.equal(report.denseSweep.allValid, true);
  assert.equal(report.checks.zeroAnimationAndSelfMotion, true);
});

test("exports immutable blend, GLB and real Blender views", () => {
  const ids = [
    "magnetic-slide-tile-blockout-blend-r006",
    "magnetic-slide-tile-blockout-interactive-r006",
    "magnetic-slide-tile-blockout-flat-plane-r006",
    "magnetic-slide-tile-blockout-axis-closeup-r006"
  ];
  for (const id of ids) {
    const record = asset(id);
    const absolute = resolveRepoPath(record.path);
    assert.ok(fs.statSync(absolute).size > 1024);
    assert.equal(sha256File(absolute), record.sha256);
  }
  const glb = fs.readFileSync(resolveRepoPath(asset("magnetic-slide-tile-blockout-interactive-r006").path));
  assert.equal(glb.subarray(0, 4).toString("ascii"), "glTF");
});

test("keeps downstream and device scope unchanged", () => {
  assert.deepEqual(manifest.stages.slice(5, 11).map((stage) => stage.status), Array(6).fill("stale"));
  assert.equal(manifest.stages[11].status, "rejected");
  assert.equal(manifest.currentState.simulatorStatus, "internal-superseded-not-current");
  assert.equal(manifest.currentState.unityStatus, "not-started-old-shipping-model-default");
});

