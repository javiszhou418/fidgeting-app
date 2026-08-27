import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import {
  PHYSICAL_FIELDS,
  cadConfigFromEvidenceContract,
  cadViewportTransform,
  computeCadGeometry,
  computeCadSweepEnvelope,
  computeMinimumOverlapContainmentSweep,
  createCadViewport,
  createCapsuleGeometry,
  deriveCadTravelBounds,
  derivePhysicalDimensions,
  displayDimension,
  inverseCadPoint,
  panCadViewport,
  refreshCadTravelBounds,
  solveDirectTopPose,
  topLocalPointFromWorld,
  topWorldPointFromLocal,
  zoomCadViewport
} from "../mechanism-cad-core.mjs";

const contract = JSON.parse(fs.readFileSync(new URL(
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/mechanism-evidence-contract.json",
  import.meta.url
), "utf8"));
const cadReviewConfig = JSON.parse(fs.readFileSync(new URL(
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/interactive-cad-geometry-config.json",
  import.meta.url
), "utf8"));
const config = cadConfigFromEvidenceContract(contract, {
  ...cadReviewConfig,
  expectedContractSha256: cadReviewConfig.contractSha256
});
const geometry = (pose = {}) => computeCadGeometry(pose, config);

test("loads minimum-overlap disk and dual-bound values from rev 15 contract", () => {
  assert.ok(Math.abs(config.maxTravelL - 0.3615286624203821) < 1e-12);
  assert.equal(config.detentCount, 30);
  assert.equal(config.componentLayers.length, 10);
  assert.equal(config.carrierRadiusL, 0.23);
  assert.equal(config.closedStopL, 0);
  assert.equal(config.negativeTravelForbidden, true);
  assert.equal(config.grooveStartFromTopL, 0.32);
  assert.equal(config.grooveEndFromTopL, 0.78);
  assert.ok(Math.abs(config.grooveEndpointLimitL - (config.grooveEndFromTopL - config.grooveStartFromTopL)) < 1e-12);
  assert.ok(config.maxTravelL < config.grooveEndpointLimitL);
  assert.equal(config.limitingCause, "MinimumOverlapDisk");
  assert.ok(Math.abs(config.minimumOverlapDiskRadiusL - 1 / (2 * config.aspectRatioLW)) < 1e-12);
  assert.equal(config.topZ > config.bottomZ, true);
  assert.throws(
    () => cadConfigFromEvidenceContract(contract, { ...cadReviewConfig, expectedContractSha256: "drift" }),
    /CAD contract hash drift/
  );
});

test("defines exact closed overlap and clamps all negative travel", () => {
  const closed = geometry({ travelL: 0, angleDeg: 0 });
  const negative = geometry({ travelL: -0.25, angleDeg: 0 });
  assert.deepEqual(closed.top.localTranslation, [0, 0]);
  assert.deepEqual(negative.top.localTranslation, [0, 0]);
  assert.equal(closed.closedStop.silhouettesCoincident, true);
  assert.equal(negative.closedStop.silhouettesCoincident, true);
  assert.equal(negative.closedStop.inputClamped, true);
  assert.equal(negative.closedStop.penetrationL, 0);
  assert.equal(geometry({ travelL: -Number.EPSILON, angleDeg: 0 }).closedStop.penetrationL, 0);
});

test("keeps nonzero-angle closed poses nonnegative without claiming aligned silhouettes", () => {
  const turned = geometry({ travelL: -0.1, angleDeg: 36 });
  assert.deepEqual(turned.top.localTranslation, [0, 0]);
  assert.equal(turned.closedStop.atStop, true);
  assert.equal(turned.closedStop.silhouettesCoincident, false);
  assert.equal(turned.axis.world[0], geometry().axis.world[0]);
  assert.equal(turned.carrier.translation[0], 0);
});

test("blocks inward pointer penetration but preserves tangential rotation at closed", () => {
  const pose = { travelL: 0, angleDeg: 0 };
  const closed = geometry(pose);
  const local = [closed.axis.local[0] + 70, closed.axis.local[1] + 90];
  const start = topWorldPointFromLocal(local, pose, config);
  const inward = solveDirectTopPose({
    pointer: [start[0], start[1] + 50],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.equal(inward.nextTravelL, 0);
  assert.equal(inward.nextAngleDeg, 0);
  assert.equal(inward.closedClamped, true);
  const tangential = solveDirectTopPose({
    pointer: [start[0] + 45, start[1]],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.equal(tangential.nextTravelL, 0);
  assert.notEqual(tangential.nextAngleDeg, 0);
  const diagonal = solveDirectTopPose({
    pointer: [start[0] + 40, start[1] + 80],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.equal(diagonal.nextTravelL, 0);
  assert.notEqual(diagonal.nextAngleDeg, 0);
  assert.equal(diagonal.closedClamped, true);
});

test("returns from open to exact zero without floating undershoot", () => {
  const pose = { travelL: 0.2, angleDeg: 0 };
  const open = geometry(pose);
  const local = [open.axis.local[0] + 60, open.axis.local[1] + 100];
  const start = topWorldPointFromLocal(local, pose, config);
  const closed = solveDirectTopPose({
    pointer: [start[0], start[1] + 200],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.equal(closed.nextTravelL, 0);
  const repeated = solveDirectTopPose({
    pointer: [start[0], start[1] + 400],
    grabbedLocalPoint: local,
    travelL: closed.nextTravelL,
    angleDeg: closed.nextAngleDeg,
    config
  });
  assert.equal(repeated.nextTravelL, 0);
  assert.ok(!Object.is(repeated.nextTravelL, -0));
});

test("retains finite groove endpoint as the non-active candidate bound", () => {
  const closed = geometry({ travelL: 0, angleDeg: 0 });
  const open = geometry({ travelL: config.maxTravelL, angleDeg: 0 });
  assert.equal(closed.grooves.finite, true);
  assert.equal(closed.grooves.lengthL, config.grooveEndpointLimitL);
  assert.equal(closed.followers.uFromTopL, config.grooveStartFromTopL);
  assert.equal(closed.followers.distanceToStartL, 0);
  assert.ok(Math.abs(closed.followers.distanceToEndL - config.grooveEndpointLimitL) < 1e-12);
  assert.equal(closed.followers.atClosedEndpoint, true);
  assert.ok(Math.abs(open.followers.uFromTopL - (config.grooveStartFromTopL + config.maxTravelL)) < 1e-12);
  assert.ok(open.followers.distanceToEndL > 0);
  assert.equal(open.followers.atOpenEndpoint, false);
  assert.equal(open.followers.engaged, true);
  assert.equal(open.coverage.axisCovered, true);
});

test("keeps followers inside finite grooves for representative full travel", () => {
  for (let index = 0; index <= 100; index += 1) {
    const pose = geometry({ travelL: config.maxTravelL * index / 100, angleDeg: 216 });
    assert.ok(pose.followers.distanceToStartL >= -1e-12);
    assert.ok(pose.followers.distanceToEndL >= -1e-12);
    assert.equal(pose.followers.engaged, true);
  }
  assert.equal(geometry({ travelL: -1, angleDeg: 0 }).followers.atClosedEndpoint, true);
  assert.equal(geometry({ travelL: 1, angleDeg: 0 }).followers.atOpenEndpoint, false);
});

test("keeps the top above the bottom across all 30 detents and slide samples", () => {
  const sweep = computeCadSweepEnvelope(config);
  assert.equal(sweep.sampleCount, 30 * config.sweepSlideSampleFractions.length);
  assert.equal(new Set(sweep.samples.map((sample) => sample.angleDeg)).size, 30);
  assert.equal(sweep.allValid, true);
  assert.deepEqual(sweep.invalidSamples, []);
  assert.equal(sweep.topZ > sweep.bottomZ, true);
  assert.equal(sweep.bottomMasksTop, false);
  assert.ok(sweep.samples.every((sample) => sample.followerEngaged && sample.axisCovered && sample.topAboveBottom));
});

test("clamps at the overlap-disk boundary while rotation remains legal", () => {
  const pose = { travelL: config.maxTravelL, angleDeg: 0 };
  const open = geometry(pose);
  const local = [open.axis.local[0] + 70, open.axis.local[1] + 90];
  const start = topWorldPointFromLocal(local, pose, config);
  const beyond = solveDirectTopPose({
    pointer: [start[0], start[1] - 80],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.equal(beyond.nextTravelL, config.maxTravelL);
  assert.equal(beyond.openClamped, true);
  const rotated = geometry({ travelL: config.maxTravelL, angleDeg: 120 });
  assert.equal(rotated.followers.atOpenEndpoint, false);
  assert.equal(rotated.followers.engaged, true);
  assert.equal(rotated.layerOrder.topAboveBottom, true);
  assert.equal(rotated.minimumOverlapDisk.fullyCovered, true);
  assert.equal(rotated.minimumOverlapDisk.boundaryContact, true);
});

test("derives actual travel from groove and analytic disk-containment bounds", () => {
  const bounds = deriveCadTravelBounds(config);
  assert.ok(Math.abs(bounds.capsuleRadiusL - config.minimumOverlapDiskRadiusL) < 1e-12);
  assert.ok(Math.abs(bounds.overlapContainmentLimitL - (1 - config.axisNormalizedY - config.minimumOverlapDiskRadiusL)) < 1e-12);
  assert.equal(bounds.actualSMaxL, bounds.overlapContainmentLimitL);
  assert.equal(bounds.limitingCause, "MinimumOverlapDisk");
  assert.equal(bounds.angleInvariant, true);
});

test("keeps the full minimum overlap disk contained at closed and exact max tangency", () => {
  const closed = geometry({ travelL: 0, angleDeg: 0 });
  const maximum = geometry({ travelL: config.maxTravelL, angleDeg: 237 });
  assert.equal(closed.minimumOverlapDisk.fullyCovered, true);
  assert.ok(closed.minimumOverlapDisk.containment.marginL >= -1e-12);
  assert.equal(maximum.minimumOverlapDisk.fullyCovered, true);
  assert.ok(Math.abs(maximum.minimumOverlapDisk.containment.bottomMarginL) < 1e-12);
  assert.equal(maximum.minimumOverlapDisk.boundaryContact, true);
  assert.equal(maximum.minimumOverlapDisk.activeLimitingCause, "MinimumOverlapDisk");
  assert.ok(maximum.followers.distanceToEndL > 0);
});

test("proves dense full-360 containment and rejects any boundary penetration", () => {
  const sweep = computeMinimumOverlapContainmentSweep(config);
  assert.equal(sweep.angleSampleCount, 360);
  assert.equal(sweep.sampleCount, 1800);
  assert.equal(sweep.allValid, true);
  assert.deepEqual(sweep.invalidSamples, []);
  assert.equal(sweep.analyticContinuous, true);
  assert.equal(sweep.angleInvariant, true);
  assert.equal(sweep.exactBoundaryTangency, true);
  assert.equal(sweep.beyondBoundaryInvalid, true);
});

test("switches the active sMax source and responds to normalized parameters", () => {
  const candidate = { ...config };
  candidate.minimumOverlapDiskRadiusL = 0.1;
  refreshCadTravelBounds(candidate);
  assert.equal(candidate.limitingCause, "FiniteGrooveEndpoint");
  assert.equal(candidate.maxTravelL, candidate.grooveEndpointLimitL);
  candidate.grooveEndpointLimitL = 0.2;
  refreshCadTravelBounds(candidate);
  assert.equal(candidate.maxTravelL, 0.2);
  candidate.aspectRatioLW = 1.8;
  candidate.minimumOverlapDiskRadiusL = 0.3;
  candidate.grooveEndpointLimitL = 0.46;
  refreshCadTravelBounds(candidate);
  assert.equal(candidate.limitingCause, "MinimumOverlapDisk");
  assert.ok(candidate.maxTravelL < 0.4);
});

test("builds a normalized tangent capsule", () => {
  const capsule = createCapsuleGeometry({ aspectRatioLW: config.aspectRatioLW });
  assert.equal(capsule.length / capsule.width, config.aspectRatioLW);
  assert.equal(capsule.radius, capsule.width / 2);
  assert.equal(capsule.tangentPoints.length, 4);
});

test("keeps smooth bottom exterior and fixed axis invariant", () => {
  const poses = [
    geometry({ travelL: 0, angleDeg: 0 }),
    geometry({ travelL: 0.23, angleDeg: 90 }),
    geometry({ travelL: 0.46, angleDeg: 216 })
  ];
  assert.ok(poses.every((pose) => pose.bottom.transform === "identity"));
  assert.ok(poses.every((pose) => pose.bottom.exteriorFront === "smooth"));
  assert.ok(poses.every((pose) => pose.bottom.exteriorBack === "smooth"));
  assert.ok(poses.every((pose) => pose.bottom.exposedRailCount === 0));
  assert.deepEqual(poses.map((pose) => pose.axis.world), [
    poses[0].axis.world,
    poses[0].axis.world,
    poses[0].axis.world
  ]);
  assert.ok(poses.every((pose) => pose.axis.attachment === "fixed-axis-center-in-bottom"));
});

test("rotates carrier without translation", () => {
  const zero = geometry({ travelL: 0.2, angleDeg: 0 });
  const turned = geometry({ travelL: 0.2, angleDeg: 90 });
  assert.deepEqual(zero.carrier.translation, [0, 0]);
  assert.deepEqual(turned.carrier.translation, [0, 0]);
  assert.notEqual(zero.carrier.transform, turned.carrier.transform);
  assert.deepEqual(turned.carrier.center, zero.carrier.center);
});

test("keeps two top grooves parallel to two carrier followers", () => {
  for (const angleDeg of [0, 36, 90, 180]) {
    const pose = geometry({ travelL: 0.3, angleDeg });
    assert.equal(pose.grooves.count, 2);
    assert.equal(pose.followers.count, 2);
    assert.equal(pose.grooves.owner, "TopPlate underside");
    assert.equal(pose.followers.owner, "RotatingCarrier");
    assert.equal(pose.grooves.parallelToFollowers, true);
    const vectors = pose.grooves.world.map((groove) => [
      groove.end[0] - groove.start[0],
      groove.end[1] - groove.start[1]
    ]);
    const cross = vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0];
    assert.ok(Math.abs(cross) < 1e-8);
  }
});

test("uses carrier-local translation after fixed-axis rotation", () => {
  const travelL = 0.2;
  const zero = geometry({ travelL, angleDeg: 0 });
  const ninety = geometry({ travelL, angleDeg: 90 });
  assert.match(zero.top.transform, /^rotate\(0 .+\) translate\(0 -/);
  assert.match(ninety.top.transform, /^rotate\(90 .+\) translate\(0 -/);
  const local = [zero.upper.centerX, zero.upper.centerY];
  const zeroWorld = topWorldPointFromLocal(local, { travelL, angleDeg: 0 }, config);
  const ninetyWorld = topWorldPointFromLocal(local, { travelL, angleDeg: 90 }, config);
  assert.ok(zeroWorld[1] < local[1]);
  assert.ok(ninetyWorld[0] > local[0]);
});

test("preserves fixed-axis coverage at maximum travel", () => {
  for (const angleDeg of [0, 90, 180, 270]) {
    const pose = geometry({ travelL: config.maxTravelL, angleDeg });
    assert.equal(pose.coverage.axisCovered, true);
    assert.ok(Math.abs(pose.coverage.coverResidualL - config.minimumOverlapDiskRadiusL) < 1e-9);
    assert.equal(pose.coverage.exactPhysicalMarginKnown, false);
  }
});

test("exposes the required ten-part component tree", () => {
  assert.deepEqual(geometry().componentLayers.map((layer) => layer.id), [
    "BottomExterior",
    "FixedAxis",
    "MinimumOverlapDisk",
    "RotatingCarrier",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "TopPlate",
    "TopGrooveLeft",
    "TopGrooveRight",
    "UnknownContacts"
  ]);
});

test("direct drag follows screen direction at cardinal carrier angles", () => {
  for (const [angleDeg, pointerDelta] of [
    [0, [0, -30]],
    [90, [30, 0]],
    [180, [0, 30]],
    [270, [-30, 0]]
  ]) {
    const pose = { travelL: 0.18, angleDeg };
    const current = geometry(pose);
    const local = [current.axis.local[0] + 42, current.axis.local[1] + 74];
    const start = topWorldPointFromLocal(local, pose, config);
    const pointer = [start[0] + pointerDelta[0], start[1] + pointerDelta[1]];
    const solved = solveDirectTopPose({ pointer, grabbedLocalPoint: local, ...pose, config });
    const end = topWorldPointFromLocal(local, {
      travelL: solved.nextTravelL,
      angleDeg: solved.nextAngleDeg
    }, config);
    const actual = [end[0] - start[0], end[1] - start[1]];
    const dot = actual[0] * pointerDelta[0] + actual[1] * pointerDelta[1];
    assert.ok(dot > 0, `direction mismatch at ${angleDeg}°`);
    assert.ok(solved.nextTravelL > pose.travelL);
    assert.ok(solved.residualPx < 0.05);
  }
});

test("diagonal direct drag changes local slide and angle together", () => {
  const pose = { travelL: 0.2, angleDeg: 36 };
  const current = geometry(pose);
  const local = [current.axis.local[0] + 70, current.axis.local[1] + 90];
  const start = topWorldPointFromLocal(local, pose, config);
  const solved = solveDirectTopPose({
    pointer: [start[0] + 35, start[1] - 28],
    grabbedLocalPoint: local,
    ...pose,
    config
  });
  assert.notEqual(solved.nextTravelL, pose.travelL);
  assert.notEqual(solved.nextAngleDeg, pose.angleDeg);
  assert.ok(solved.residualPx < 0.05);
  const inverse = topLocalPointFromWorld(
    topWorldPointFromLocal(local, { travelL: solved.nextTravelL, angleDeg: solved.nextAngleDeg }, config),
    geometry({ travelL: solved.nextTravelL, angleDeg: solved.nextAngleDeg })
  );
  assert.ok(Math.hypot(inverse[0] - local[0], inverse[1] - local[1]) < 1e-8);
});

test("keeps physical dimensions unknown until entered", () => {
  const state = derivePhysicalDimensions({});
  assert.equal(Object.keys(state.inputs).length, PHYSICAL_FIELDS.length);
  assert.ok(Object.values(state.inputs).every((value) => value === null));
  assert.deepEqual(state.derived, {});
  assert.equal(displayDimension(null), "? mm · 未知");
});

test("zooms, pans and inverses CAD coordinates", () => {
  const initial = createCadViewport();
  const zoomed = zoomCadViewport(initial, 1.5, [320, 240]);
  const panned = panCadViewport(zoomed, 40, -20);
  const source = [280, 180];
  const screen = [source[0] * panned.zoom + panned.panX, source[1] * panned.zoom + panned.panY];
  assert.deepEqual(inverseCadPoint(screen, panned), source);
  assert.match(cadViewportTransform(panned), /^translate\(.+\) scale\(.+\)$/);
});
