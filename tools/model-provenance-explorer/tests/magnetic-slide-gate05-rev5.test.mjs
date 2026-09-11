import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { loadManifest, resolveRepoPath, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const asset = (id) => manifest.assets.find((candidate) => candidate.id === id);
const readAsset = (id) => JSON.parse(fs.readFileSync(resolveRepoPath(asset(id).path), "utf8"));
const report = readAsset("magnetic-slide-tile-blockout-validation-r005");
const contract = readAsset("magnetic-slide-tile-authorized-provisional-contract-r011");
const architecture = readAsset("magnetic-slide-tile-approved-four-track-architecture-r013");
const reusePlan = readAsset("magnetic-slide-tile-reuse-plan-r011");

test("preserves historical white models after Gate 05 reopens", () => {
  assert.deepEqual(manifest.stages.slice(0, 4).map((stage) => stage.status), Array(4).fill("approved"));
  assert.equal(gate05.status, "approved");
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.ok(manifest.assets.some((candidate) => candidate.id === "magnetic-slide-tile-blockout-interactive-r004"));
  assert.ok(manifest.assets.some((candidate) => candidate.id === "magnetic-slide-tile-blockout-interactive-r005"));
  assert.ok(manifest.assets.some((candidate) => candidate.id === "magnetic-slide-tile-blockout-interactive-r006"));
});

test("consumes the exact four-track raised-axis contract", () => {
  const mechanism = asset("slider-analysis-mechanism-evidence-contract-r016");
  assert.equal(sha256File(resolveRepoPath(mechanism.path)), report.contractSha256);
  assert.equal(contract.governingMechanismContractSha256, report.contractSha256);
  assert.equal(architecture.governingMechanismContractSha256, report.contractSha256);
  assert.equal(report.checks.contractHashConsumed, true);
  assert.equal(report.checks.fourGrooves, true);
  assert.equal(report.checks.outerInnerRoles, true);
  assert.equal(report.checks.raisedAxisBoss, true);
  assert.equal(report.checks.noRecessedCavity, true);
});

test("keeps provisional ranges and unknown engineering explicit", () => {
  assert.equal(contract.dimensionsMm.overallLength.state, "user-authorized-provisional");
  assert.deepEqual(report.dimensionsMm.overallLength.range, [46.8, 57.8]);
  assert.deepEqual(report.dimensionsMm.overallWidth.range, [30.8, 35.7]);
  assert.deepEqual(report.dimensionsMm.ballDiameterRange, [2, 3]);
  assert.deepEqual(report.dimensionsMm.trackWidthRange, [1.8, 3]);
  assert.ok(contract.unknownEngineering.includes("contact preload"));
  assert.equal(report.checks.unknownEngineeringPreserved, true);
});

test("passes dense containment, hierarchy, manifold and self-motion checks", () => {
  assert.equal(report.pass, true);
  assert.equal(report.denseSweep.sampleCount, 3600);
  assert.equal(report.denseSweep.angularStepDegrees, 0.5);
  assert.equal(report.denseSweep.allValid, true);
  assert.equal(report.checks.hierarchyExact, true);
  assert.equal(report.checks.axisInvariant, true);
  assert.equal(report.checks.topAlwaysAboveBottom, true);
  assert.equal(report.checks.zeroAnimationAndSelfMotion, true);
  for (const metrics of Object.values(report.meshAudit)) assert.equal(metrics.nonmanifoldEdges, 0);
});

test("preserves approved look inputs without reusing rejected geometry", () => {
  assert.ok(reusePlan.reusedAssets.some((item) => item.id === "magnetic-slide-tile-artwork-upper-mask-r007"));
  assert.ok(reusePlan.reusedAssets.some((item) => item.id === "magnetic-slide-tile-material-rev10-recipe-r010"));
  assert.ok(reusePlan.reusedAssets.some((item) => item.id === "magnetic-slide-tile-lighting-validation-r001"));
  assert.ok(reusePlan.staleNotReused.some((item) => item.gate === "05-blockout" && item.revision === 4));
});

test("exports a real interactive GLB and authoritative blend", () => {
  for (const id of ["magnetic-slide-tile-blockout-interactive-r005", "magnetic-slide-tile-blockout-blend-r005"]) {
    const record = asset(id);
    const absolute = resolveRepoPath(record.path);
    assert.ok(fs.statSync(absolute).size > 1024);
    assert.equal(sha256File(absolute), record.sha256);
  }
  const glb = fs.readFileSync(resolveRepoPath(asset("magnetic-slide-tile-blockout-interactive-r005").path));
  assert.equal(glb.subarray(0, 4).toString("ascii"), "glTF");
});
