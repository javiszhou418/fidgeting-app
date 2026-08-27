import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

// Covers the preserved internal draft only; no review artifact is registered.
import {
  EVIDENCE_CONSTRAINED_FEEL_DEFAULTS,
  createFeelSimulator,
  decayByHalfLife
} from "../mechanism-feel-simulator-core.mjs";

const contract = JSON.parse(fs.readFileSync(new URL(
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/mechanism-evidence-contract.json",
  import.meta.url
), "utf8"));
const cadConfig = JSON.parse(fs.readFileSync(new URL(
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/interactive-cad-geometry-config.json",
  import.meta.url
), "utf8"));
const create = (tuning = {}) => createFeelSimulator(contract, cadConfig, {
  expectedContractSha256: cadConfig.contractSha256,
  tuning
});

test("starts and resets with zero velocities and no self-motion", () => {
  const simulator = create();
  assert.deepEqual(simulator.snapshot().linearVelocityLPerSecond, 0);
  assert.deepEqual(simulator.snapshot().angularVelocityDegPerSecond, 0);
  assert.deepEqual(simulator.step(2).travelL, 0);
  assert.deepEqual(simulator.step(2).angleDeg, 0);
  simulator.applyPointer({ slideDeltaL: 0.2, angleDeltaDeg: 30, effort: 1 });
  const reset = simulator.reset();
  assert.equal(reset.travelL, 0);
  assert.equal(reset.angleDeg, 0);
  assert.equal(reset.linearVelocityLPerSecond, 0);
  assert.equal(reset.angularVelocityDegPerSecond, 0);
});

test("uses frame-rate-independent half-life damping", () => {
  assert.ok(Math.abs(decayByHalfLife(100, 1, 0.5) - 25) < 1e-12);
  const sixty = Array.from({ length: 60 }).reduce((value) => decayByHalfLife(value, 1 / 60, 0.5), 100);
  assert.ok(Math.abs(sixty - 25) < 1e-9);
});

test("holds angular motion below breakaway while slide remains available", () => {
  const simulator = create();
  const state = simulator.applyPointer({ slideDeltaL: 0.1, angleDeltaDeg: 24, effort: 0.2 });
  assert.ok(state.travelL > 0);
  assert.equal(state.angleDeg, 0);
  assert.equal(state.lastEvent, "slide-held-detent");
});

test("supports simultaneous slide and rotation above breakaway", () => {
  const state = create().applyPointer({ slideDeltaL: 0.16, angleDeltaDeg: 36, effort: 1 });
  assert.ok(state.travelL > 0);
  assert.ok(state.angleDeg > 0);
  assert.equal(state.lastEvent, "compound-motion");
});

test("preserves finite grooves and minimum-overlap containment at stops", () => {
  const simulator = create({ slideResistance: 0 });
  const maximum = simulator.applyPointer({ slideDeltaL: 2, effort: 1 });
  assert.ok(Math.abs(maximum.travelL - maximum.cad.maxTravelL) < 1e-12);
  assert.equal(maximum.activeStop, "minimum-overlap-disk");
  assert.equal(maximum.constraints.diskCovered, true);
  assert.equal(maximum.constraints.followerEngaged, true);
  assert.ok(maximum.constraints.grooveEndDistanceL > 0);
  const closed = simulator.applyPointer({ slideDeltaL: -2, effort: 1 });
  assert.equal(closed.travelL, 0);
  assert.equal(closed.activeStop, "closed");
});

test("captures the nearest 12-degree detent at low speed", () => {
  const simulator = create({
    rotationResistance: 0,
    detentStrength: 1,
    angularDampingHalfLife: 0.03,
    captureWindowDeg: 6
  });
  simulator.applyPointer({ angleDeltaDeg: 13, effort: 1, deltaSeconds: 0.2 });
  simulator.release();
  let state;
  for (let index = 0; index < 240; index += 1) state = simulator.step(1 / 120);
  assert.equal(state.angleDeg, 12);
  assert.equal(state.detentIndex, 1);
  assert.equal(state.captured, true);
});

test("records deterministic parameter snapshots and audio toggles", () => {
  const simulator = create();
  const tuned = simulator.setParameters({ clickAudio: true, slideResistance: 0.6 });
  assert.equal(tuned.parameters.clickAudio, true);
  assert.equal(tuned.parameters.slideResistance, 0.6);
  assert.equal(tuned.userTuned, true);
  assert.deepEqual(tuned.evidenceDefaults, EVIDENCE_CONSTRAINED_FEEL_DEFAULTS);
  const restored = simulator.restoreDefaults();
  assert.equal(restored.parameters.clickAudio, false);
  assert.equal(restored.userTuned, false);
});

test("rejects contract hash drift", () => {
  assert.throws(
    () => createFeelSimulator(contract, cadConfig, { expectedContractSha256: "drift" }),
    /contract hash drift/
  );
});
