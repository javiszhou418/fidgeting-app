import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import {
  KINEMATIC_LAYOUT,
  assertNoMechanismDefaultDrift,
  composeMechanismTransforms,
  createMechanismSandbox,
  decayByHalfLife,
  detentAngleDeg,
  endpointAxisLocalL,
  mechanismConfigFromEvidenceContract,
  nearestDetentIndex,
  wrapAngleDeg
} from "../mechanism-sandbox-core.mjs";

const contract = JSON.parse(fs.readFileSync(new URL(
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-008/mechanism-evidence-contract.json",
  import.meta.url
), "utf8"));
const evidenceConfig = mechanismConfigFromEvidenceContract(contract);
const testTuning = Object.freeze({
  slideResistance: 0.34,
  rotationResistance: 0.28,
  detentStrength: 0.68,
  breakaway: 0.32,
  damping: 0.48,
  inertiaHalfLife: 0.22,
  endStopSoftness: 0.06,
  endStopStiffness: 0.82,
  captureSpeedDegPerSecond: 24,
  captureWindowDeg: 3.2
});
const createSandbox = (overrides = {}) => createMechanismSandbox(contract, { ...testTuning, ...overrides });
const compose = (travelL, angleDeg) => composeMechanismTransforms(travelL, angleDeg, evidenceConfig);

test("maps exactly 30 detents at 12 degrees", () => {
  assert.equal(evidenceConfig.detentCount, 30);
  assert.equal(evidenceConfig.detentStepDeg, 12);
  assert.deepEqual(
    Array.from({ length: evidenceConfig.detentCount }, (_, index) => detentAngleDeg(index, evidenceConfig)),
    Array.from({ length: evidenceConfig.detentCount }, (_, index) => index * 12)
  );
  assert.equal(nearestDetentIndex(359, evidenceConfig), 0);
});

test("loads authoritative mechanism values and rejects duplicate drift", () => {
  assert.equal(evidenceConfig.maxTravelL, 0.46);
  assert.deepEqual(evidenceConfig.supportedTravelRangeL, [0.38, 0.46]);
  assert.equal(evidenceConfig.observedPeakTravelL, 0.5);
  assert.equal(evidenceConfig.pivotLocalSliding, false);
  assert.equal(assertNoMechanismDefaultDrift(contract, evidenceConfig), true);
  assert.throws(
    () => assertNoMechanismDefaultDrift(contract, { ...evidenceConfig, detentStepDeg: 10 }),
    /Duplicate mechanism default drift/
  );
  assert.throws(() => createMechanismSandbox(contract), /requires explicit test\/user input/);
});

test("starts and resets with no self-spin", () => {
  const sandbox = createSandbox();
  assert.equal(sandbox.snapshot().angularVelocityDegPerSecond, 0);
  sandbox.rotateByPointer(18, 1);
  assert.notEqual(sandbox.snapshot().angularVelocityDegPerSecond, 0);
  const reset = sandbox.reset();
  assert.equal(reset.angleDeg, 0);
  assert.equal(reset.travelL, 0);
  assert.equal(reset.angularVelocityDegPerSecond, 0);
  assert.equal(reset.captured, true);
  sandbox.step(1);
  assert.equal(sandbox.snapshot().angleDeg, 0);
});

test("uses frame-rate-independent half-life damping", () => {
  const once = decayByHalfLife(120, 1, 0.25);
  let many = 120;
  for (let index = 0; index < 120; index += 1) {
    many = decayByHalfLife(many, 1 / 120, 0.25);
  }
  assert.ok(Math.abs(once - many) < 1e-9);
});

test("holds below breakaway and captures a detent", () => {
  const sandbox = createSandbox({ breakaway: 0.5 });
  sandbox.rotateByPointer(8, 0.4);
  assert.equal(sandbox.snapshot().angleDeg, 0);
  assert.equal(sandbox.snapshot().lastEvent, "held-below-breakaway");
  sandbox.rotateByPointer(12.4, 0.8, 0.5);
  sandbox.releaseRotation();
  for (let index = 0; index < 180 && !sandbox.snapshot().captured; index += 1) {
    sandbox.step(1 / 120);
  }
  assert.equal(sandbox.snapshot().captured, true);
  assert.equal(sandbox.snapshot().angleDeg % 12, 0);
});

test("slides only outward from closed and reverses to close", () => {
  const sandbox = createSandbox({ maxTravelL: 0.44, endStopSoftness: 0 });
  assert.equal(sandbox.setSlideTravel(-0.1).travelL, 0);
  assert.equal(sandbox.setSlideTravel(0.3).travelL, 0.3);
  assert.equal(sandbox.setSlideTravel(0.12).travelL, 0.12);
  assert.equal(sandbox.setSlideTravel(0).travelL, 0);
  assert.equal(sandbox.setSlideTravel(0.2).travelL, 0.2);
});

test("supports soft stops and hard maximum clamp", () => {
  const soft = createSandbox({
    maxTravelL: 0.42,
    endStopSoftness: 0.08,
    endStopStiffness: 0.8
  });
  const nearStop = soft.setSlideTravel(0.4).travelL;
  assert.ok(nearStop > 0.4 && nearStop <= 0.42);
  assert.equal(soft.setSlideTravel(0.9).travelL, 0.42);

  const hard = createSandbox({
    maxTravelL: 0.42,
    endStopSoftness: 0
  });
  assert.equal(hard.setSlideTravel(0.4).travelL, 0.4);
  assert.equal(hard.setSlideTravel(0.9).travelL, 0.42);
});

test("wraps angles in both directions", () => {
  assert.equal(wrapAngleDeg(361), 1);
  assert.equal(wrapAngleDeg(-1), 359);
  const sandbox = createSandbox();
  sandbox.rotateByPointer(-24, 1);
  assert.ok(sandbox.snapshot().angleDeg >= 0 && sandbox.snapshot().angleDeg < 360);
});

test("applies parameter changes and restores contract-derived configuration", () => {
  const sandbox = createSandbox();
  const changed = sandbox.setParameters({ maxTravelL: 0.46, breakaway: 0.7 });
  assert.equal(changed.parameters.maxTravelL, 0.46);
  assert.equal(changed.parameters.breakaway, 0.7);
  assert.equal(changed.userTuned, true);
  const restored = sandbox.restoreEvidenceDefaults();
  assert.equal(restored.parameters.maxTravelL, 0.46);
  assert.equal(restored.userTuned, false);
  assert.equal(restored.angularVelocityDegPerSecond, 0);
});

test("keeps the upper plate transform fixed", () => {
  const closed = compose(0, 0);
  const translated = compose(0.42, 0);
  const rotated = compose(0.31, 132);
  assert.deepEqual(closed.upper, KINEMATIC_LAYOUT.upperTransform);
  assert.deepEqual(translated.upper, closed.upper);
  assert.deepEqual(rotated.upper, closed.upper);
});

test("moves the lower carrier and axis together", () => {
  const closed = compose(0, 0);
  const opened = compose(0.37, 0);
  assert.deepEqual(opened.lower.translationL, [0, 0.37]);
  assert.equal(opened.axis.worldL[0], closed.axis.worldL[0]);
  assert.ok(Math.abs(opened.axis.worldL[1] - closed.axis.worldL[1] - 0.37) < 1e-12);
  assert.deepEqual(opened.lower.rotationPivotWorldL, opened.axis.worldL);
});

test("keeps one endpoint axis fixed to the lower carrier", () => {
  const expectedLocal = endpointAxisLocalL(evidenceConfig.aspectRatioLW);
  const poses = [
    compose(0, 0),
    compose(0.21, 36),
    compose(0.46, 216)
  ];
  assert.ok(poses.every((pose) => JSON.stringify(pose.axis.localToLowerL) === JSON.stringify(expectedLocal)));
  assert.ok(poses.every((pose) => pose.axis.attachment === "fixed-bottom-endcap-center"));
  assert.ok(poses.every((pose) => pose.axis.independentDof === false));
  assert.ok(poses.every((pose) => pose.rails.pivotTraversesRailsIndependently === false));
});

test("rotates the lower carrier around its translated axis without inventing rail geometry", () => {
  const zero = compose(0.31, 0);
  const turned = compose(0.31, 36);
  assert.deepEqual(turned.lower.rotationPivotWorldL, zero.axis.worldL);
  assert.deepEqual(turned.axis.worldL, zero.axis.worldL);
  assert.equal(turned.rails.geometryState, "unknown-awaiting-approved-cad");
  assert.deepEqual(turned.rails.worldL, []);
});

test("keeps the evidence-backed bilateral rail ownership without guessed positions", () => {
  const closed = compose(0, 0);
  const opened = compose(0.21, 0);
  assert.equal(closed.rails.bilateral, true);
  assert.equal(closed.rails.count, 2);
  assert.equal(closed.rails.ownerFace, "lower reverse/mechanism face");
  assert.equal(opened.rails.owner, "lower-carrier");
  assert.deepEqual(opened.rails.localL, []);
});

test("keeps detent review poses separate from normalized slide", () => {
  const reviewPoses = {
    detents: [
      { travelL: 0, angleDeg: 0 },
      { travelL: 0, angleDeg: evidenceConfig.detentStepDeg },
      { travelL: 0, angleDeg: evidenceConfig.detentStepDeg * 3 }
    ],
    slide: { travelL: evidenceConfig.maxTravelL / 2, angleDeg: 0 }
  };
  assert.deepEqual(reviewPoses.detents, [
    { travelL: 0, angleDeg: 0 },
    { travelL: 0, angleDeg: 12 },
    { travelL: 0, angleDeg: 36 }
  ]);
  assert.deepEqual(reviewPoses.slide, { travelL: 0.23, angleDeg: 0 });
  assert.ok(reviewPoses.detents.every((pose) => pose.travelL === 0));
  assert.equal(reviewPoses.slide.angleDeg, 0);
  const sandbox = createSandbox();
  assert.equal(sandbox.setDetentIndex(1).angleDeg, 12);
  assert.equal(sandbox.setDetentIndex(3).angleDeg, 36);
  assert.equal(sandbox.setDetentIndex(2).angleDeg, 24);
  const slide = sandbox.setPose(reviewPoses.slide);
  assert.equal(slide.travelL, 0.23);
  assert.equal(slide.angleDeg, 0);
  assert.equal(slide.angularVelocityDegPerSecond, 0);
});

test("updates slide and rotation in one compound pointer step", () => {
  const sandbox = createSandbox({ rotationResistance: 0, endStopSoftness: 0 });
  const moved = sandbox.applyCompoundPointer({
    slideDeltaL: 0.18,
    angleDeltaDeg: 24,
    effort: 1,
    deltaSeconds: 0.1
  });
  assert.equal(moved.travelL, 0.18);
  assert.equal(moved.angleDeg, 24);
  assert.notEqual(moved.linearVelocityLPerSecond, 0);
  assert.notEqual(moved.angularVelocityDegPerSecond, 0);
  assert.equal(moved.lastEvent, "compound-motion");
});

test("supports compound motion at partial and maximum slide", () => {
  const sandbox = createSandbox({ rotationResistance: 0, endStopSoftness: 0, maxTravelL: 0.42 });
  sandbox.setPose({ travelL: 0.2, angleDeg: 0 });
  const partial = sandbox.applyCompoundPointer({ slideDeltaL: 0.08, angleDeltaDeg: 12, effort: 1 });
  assert.equal(partial.travelL, 0.28);
  assert.equal(partial.angleDeg, 12);
  sandbox.setPose({ travelL: 0.42, angleDeg: 12 });
  const maximum = sandbox.applyCompoundPointer({ slideDeltaL: 0.2, angleDeltaDeg: 24, effort: 1 });
  assert.equal(maximum.travelL, 0.42);
  assert.equal(maximum.angleDeg, 36);
});

test("reverses rotation while closing", () => {
  const sandbox = createSandbox({ rotationResistance: 0, endStopSoftness: 0 });
  sandbox.setPose({ travelL: 0.36, angleDeg: 36 });
  const closing = sandbox.applyCompoundPointer({
    slideDeltaL: -0.12,
    angleDeltaDeg: -24,
    effort: 1
  });
  assert.equal(closing.travelL, 0.24);
  assert.equal(closing.angleDeg, 12);
  assert.ok(closing.linearVelocityLPerSecond < 0);
  assert.ok(closing.angularVelocityDegPerSecond < 0);
});

test("captures angular detent while slide remains active", () => {
  const sandbox = createSandbox({
    rotationResistance: 0,
    breakaway: 0,
    endStopSoftness: 0,
    damping: 0.8
  });
  sandbox.setPose({ travelL: 0.2, angleDeg: 0 });
  sandbox.applyCompoundPointer({ slideDeltaL: 0.02, angleDeltaDeg: 12.4, effort: 1, deltaSeconds: 1 });
  const moving = sandbox.applyCompoundPointer({ slideDeltaL: 0.02, angleDeltaDeg: 0, effort: 1, deltaSeconds: 0.1 });
  const travelBeforeCapture = moving.travelL;
  const captured = sandbox.step(1 / 60);
  assert.equal(captured.angleDeg, 12);
  assert.equal(captured.captured, true);
  assert.ok(captured.travelL > travelBeforeCapture);
});

test("reset zeros both compound velocities", () => {
  const sandbox = createSandbox({ rotationResistance: 0 });
  sandbox.applyCompoundPointer({ slideDeltaL: 0.2, angleDeltaDeg: 24, effort: 1 });
  const reset = sandbox.reset();
  assert.equal(reset.travelL, 0);
  assert.equal(reset.angleDeg, 0);
  assert.equal(reset.linearVelocityLPerSecond, 0);
  assert.equal(reset.angularVelocityDegPerSecond, 0);
  sandbox.step(1);
  assert.equal(sandbox.snapshot().travelL, 0);
  assert.equal(sandbox.snapshot().angleDeg, 0);
});
