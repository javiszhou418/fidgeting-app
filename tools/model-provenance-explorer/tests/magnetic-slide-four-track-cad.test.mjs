import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import {
  cadConfigFromEvidenceContract,
  computeCadGeometry,
  computeMinimumOverlapContainmentSweep,
  solveCompoundDragDelta
} from "../mechanism-cad-core.mjs";
import { loadManifest, resolveRepoPath, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const contractAsset = manifest.assets.find((asset) => asset.id === stage.analysisSpec.contractAssetId);
const configAsset = manifest.assets.find((asset) => asset.id === stage.analysisSpec.geometryConfigAssetId);
const contract = JSON.parse(fs.readFileSync(resolveRepoPath(contractAsset.path), "utf8"));
const geometryConfig = JSON.parse(fs.readFileSync(resolveRepoPath(configAsset.path), "utf8"));
const config = cadConfigFromEvidenceContract(contract, {
  ...geometryConfig,
  expectedContractSha256: stage.analysisSpec.contractSha256
});

test("binds the current CAD to its exact contract hash", () => {
  assert.equal(sha256File(resolveRepoPath(contractAsset.path)), stage.analysisSpec.contractSha256);
  assert.equal(configAsset.sha256, sha256File(resolveRepoPath(configAsset.path)));
  assert.equal(geometryConfig.contractSha256, stage.analysisSpec.contractSha256);
});

test("exposes four finite tracks with separate roles", () => {
  const geometry = computeCadGeometry({ travelL: config.maxTravelL * 0.55, angleDeg: 36 }, config);
  assert.equal(geometry.grooves.count, 4);
  assert.equal(geometry.grooves.local.filter((groove) => groove.role === "fore-aft-slide").length, 2);
  assert.equal(geometry.grooves.local.filter((groove) => groove.role === "central-axis-link").length, 2);
  assert.deepEqual(geometry.grooves.local.map((groove) => groove.id), [
    "TopOuterGrooveLeft", "TopInnerGrooveLeft", "TopInnerGrooveRight", "TopOuterGrooveRight"
  ]);
  assert.equal(geometry.followers.count, 2);
  assert.equal(geometry.followers.engaged, true);
});

test("requires a raised axis boss and forbids the rejected cavity", () => {
  const geometry = computeCadGeometry({}, config);
  assert.ok(geometry.axisBoss.protrusionMm > 0);
  assert.equal(geometry.axisBoss.protrusionPositive, true);
  assert.equal(geometry.axisBoss.recessedAxis, false);
  assert.equal(geometry.axisBoss.visibleCavityAllowed, false);
  assert.equal(geometry.minimumOverlapDisk.owner, "BottomBase");
});

test("keeps ball and track estimates inside authorized ranges", () => {
  assert.ok(config.ballDiameterMm >= 2 && config.ballDiameterMm <= 3);
  assert.ok(config.trackWidthMm <= 3);
  assert.deepEqual(config.ballDiameterRangeMm, [2, 3]);
});

test("fails closed for track count, cavity, ball, width or hash drift", () => {
  const cases = [
    (candidate) => candidate.constraints.find((item) => item.id === "MEC-TOP-UNDERSIDE-GROOVES").value.count = 3,
    (candidate) => candidate.constraints.find((item) => item.id === "MEC-RAISED-AXIS-BOSS").value.recessedAxis = true,
    (candidate) => candidate.constraints.find((item) => item.id === "MEC-BALL-CONTACT-CANDIDATES").value.ballDiameterMm = [1, 3],
    (candidate) => candidate.constraints.find((item) => item.id === "MEC-TOP-UNDERSIDE-GROOVES").value.widthMm.maximum = 3.1
  ];
  for (const mutate of cases) {
    const candidate = structuredClone(contract);
    mutate(candidate);
    assert.throws(() => cadConfigFromEvidenceContract(candidate, {
      ...geometryConfig,
      expectedContractSha256: geometryConfig.contractSha256
    }));
  }
  assert.throws(() => cadConfigFromEvidenceContract(contract, {
    ...geometryConfig,
    expectedContractSha256: "wrong"
  }), /hash drift/);
});

test("preserves containment, top order and direct pointer direction", () => {
  const sweep = computeMinimumOverlapContainmentSweep(config);
  assert.equal(sweep.sampleCount, 1800);
  assert.equal(sweep.allValid, true);
  const start = computeCadGeometry({ travelL: config.maxTravelL * 0.3, angleDeg: 24 }, config);
  const grabbed = [start.upper.centerX + 35, start.upper.centerY - 40];
  const delta = [26, -18];
  const solved = solveCompoundDragDelta({
    previousPointer: grabbed,
    currentPointer: [grabbed[0] + delta[0], grabbed[1] + delta[1]],
    travelL: config.maxTravelL * 0.3,
    angleDeg: 24,
    config
  });
  assert.ok(Number.isFinite(solved.nextTravelL));
  assert.ok(Number.isFinite(solved.nextAngleDeg));
  assert.ok(solved.residualPx < 3);
});

test("records anthropometric provenance and unresolved engineering values", () => {
  const reportAsset = manifest.assets.find((asset) => asset.id === "slider-measurement-anthropometric-video-report-r010");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportAsset.path), "utf8"));
  assert.match(report.classification, /not production measured/);
  assert.equal(report.frames.filter((frame) => frame.state === "accepted").length, 2);
  assert.equal(report.frames.filter((frame) => frame.state.startsWith("rejected")).length, 1);
  assert.ok(report.sources.some((source) => source.url.includes("aist.go.jp")));
  assert.deepEqual(report.internalFeatureEstimateMm.ballDiameter.range, [2, 3]);
  assert.equal(report.internalFeatureEstimateMm.trackWidth.range[1], 3);
  assert.ok(report.remainingUnknowns.includes("contact preload"));
});
