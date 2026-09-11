import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import {
  cadConfigFromEvidenceContract,
  computeCadGeometry,
  computeCadSweepEnvelope,
  resolveEndpointInterlock,
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
  expectedContractSha256: stage.analysisSpec.contractSha256,
});

test("binds endpoint interlock to the current contract hash", () => {
  assert.equal(contract.revision, 17);
  assert.equal(sha256File(resolveRepoPath(contractAsset.path)), stage.analysisSpec.contractSha256);
  assert.equal(geometryConfig.contractSha256, stage.analysisSpec.contractSha256);
  assert.equal(config.endpointRotationOnly, true);
  assert.equal(config.simultaneousMotionForbidden, true);
});

test("blocks rotation at every sampled position below sMax", () => {
  for (let sample = 0; sample < 1000; sample += 1) {
    const travelL = config.maxTravelL * sample / 1000;
    const resolved = resolveEndpointInterlock(
      { travelL, angleDeg: 0 },
      { angleDeg: 12 + sample % 29 * 12, intent: "rotate" },
      config
    );
    assert.equal(resolved.travelL, travelL);
    assert.equal(resolved.angleDeg, 0);
    assert.equal(resolved.rotationBlocked, true);
  }
});

test("unlocks exactly 30 detents only at sMax", () => {
  const detents = [];
  for (let index = 0; index < config.detentCount; index += 1) {
    const resolved = resolveEndpointInterlock(
      { travelL: config.maxTravelL, angleDeg: index === 0 ? 0 : (index - 1) * 12 },
      { angleDeg: index * config.detentStepDeg, intent: "rotate" },
      config
    );
    assert.equal(resolved.rotationBlocked, false);
    assert.equal(resolved.travelL, config.maxTravelL);
    detents.push(resolved.angleDeg);
  }
  assert.deepEqual(detents, Array.from({ length: 30 }, (_, index) => index * 12));
});

test("locks slide while rotated and permits return after alignment", () => {
  const turned = resolveEndpointInterlock(
    { travelL: config.maxTravelL, angleDeg: 120 },
    { travelL: config.maxTravelL / 2, intent: "slide" },
    config
  );
  assert.equal(turned.slideBlocked, true);
  assert.equal(turned.travelL, config.maxTravelL);
  const aligned = resolveEndpointInterlock(
    { travelL: config.maxTravelL, angleDeg: 0.05 },
    { travelL: config.maxTravelL / 2, intent: "slide" },
    config
  );
  assert.equal(aligned.slideBlocked, false);
  assert.equal(aligned.angleDeg, 0);
  assert.equal(aligned.travelL, config.maxTravelL / 2);
});

test("allows only legal serial poses in the current sweep", () => {
  const sweep = computeCadSweepEnvelope(config);
  assert.equal(sweep.sampleCount, 34);
  assert.equal(sweep.allValid, true);
  assert.ok(sweep.samples.every((sample) => sample.endpointInterlockLegal));
  assert.equal(sweep.samples.filter((sample) => sample.angleDeg !== 0).every((sample) => sample.slideFraction === 1), true);
});

test("keeps fixed pivot, containment and render metadata unchanged", () => {
  const axis = computeCadGeometry({ travelL: 0, angleDeg: 0 }, config).axis.world;
  for (const angleDeg of Array.from({ length: 31 }, (_, index) => index * 12)) {
    const pose = computeCadGeometry({ travelL: config.maxTravelL, angleDeg }, config);
    assert.deepEqual(pose.axis.world, axis);
    assert.equal(pose.carrier.translation[0], 0);
    assert.equal(pose.carrier.translation[1], 0);
    assert.equal(pose.minimumOverlapDisk.fullyCovered, true);
    assert.equal(pose.layerOrder.topAboveBottom, true);
    assert.equal(pose.interlock.legalPose, true);
  }
});
