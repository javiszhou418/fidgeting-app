import {
  cadConfigFromEvidenceContract,
  computeCadGeometry
} from "./mechanism-cad-core.mjs";

// Internal paused draft. It is not registered, exposed, or eligible for review.

const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
const wrap = (degrees) => ((degrees % 360) + 360) % 360;
const shortestDelta = (from, to) => ((to - from + 540) % 360) - 180;
export const decayByHalfLife = (value, seconds, halfLife) => (
  halfLife <= 0 ? 0 : value * Math.pow(0.5, Math.max(0, seconds) / halfLife)
);

export const EVIDENCE_CONSTRAINED_FEEL_DEFAULTS = Object.freeze({
  slideResistance: 0.28,
  rotationResistance: 0.22,
  breakawayThreshold: 0.38,
  detentStrength: 0.52,
  linearInertia: 0.70,
  angularInertia: 0.76,
  linearDampingHalfLife: 0.18,
  angularDampingHalfLife: 0.26,
  captureSpeedDegPerSecond: 42,
  captureWindowDeg: 4.5,
  endStopStiffness: 0.82,
  endStopSoftnessL: 0.025,
  clickAudio: false
});

export function createFeelSimulator(contract, cadConfigAsset, {
  expectedContractSha256,
  tuning = {}
} = {}) {
  if (cadConfigAsset.contractSha256 !== expectedContractSha256) throw new Error("Simulator contract hash drift.");
  const cad = cadConfigFromEvidenceContract(contract, {
    ...cadConfigAsset,
    expectedContractSha256
  });
  let parameters = { ...EVIDENCE_CONSTRAINED_FEEL_DEFAULTS, ...tuning };
  const state = {
    travelL: 0,
    angleDeg: 0,
    linearVelocityLPerSecond: 0,
    angularVelocityDegPerSecond: 0,
    captured: true,
    activeStop: "closed",
    lastEvent: "reset",
    userTuned: false,
    clickSequence: 0
  };
  const enforceParameters = () => {
    parameters.slideResistance = clamp(Number(parameters.slideResistance), 0, 0.95);
    parameters.rotationResistance = clamp(Number(parameters.rotationResistance), 0, 0.95);
    parameters.breakawayThreshold = clamp(Number(parameters.breakawayThreshold), 0, 1);
    parameters.detentStrength = clamp(Number(parameters.detentStrength), 0, 1);
    parameters.linearInertia = clamp(Number(parameters.linearInertia), 0, 1);
    parameters.angularInertia = clamp(Number(parameters.angularInertia), 0, 1);
    parameters.linearDampingHalfLife = clamp(Number(parameters.linearDampingHalfLife), 0.02, 3);
    parameters.angularDampingHalfLife = clamp(Number(parameters.angularDampingHalfLife), 0.02, 3);
    parameters.captureSpeedDegPerSecond = clamp(Number(parameters.captureSpeedDegPerSecond), 1, 360);
    parameters.captureWindowDeg = clamp(Number(parameters.captureWindowDeg), 0.25, cad.detentStepDeg / 2);
    parameters.endStopStiffness = clamp(Number(parameters.endStopStiffness), 0, 1);
    parameters.endStopSoftnessL = clamp(Number(parameters.endStopSoftnessL), 0, Math.min(0.1, cad.maxTravelL / 2));
    parameters.clickAudio = Boolean(parameters.clickAudio);
  };
  enforceParameters();

  const nearestDetentIndex = () => Math.round(wrap(state.angleDeg) / cad.detentStepDeg) % cad.detentCount;
  const constraintState = () => {
    const geometry = computeCadGeometry({ travelL: state.travelL, angleDeg: state.angleDeg }, cad);
    if (!geometry.minimumOverlapDisk.fullyCovered) throw new Error("Simulator entered invalid overlap state.");
    return {
      activeLimitCause: geometry.minimumOverlapDisk.activeLimitingCause,
      minimumOverlapMarginL: geometry.minimumOverlapDisk.containment.marginL,
      grooveEndDistanceL: geometry.followers.distanceToEndL,
      diskCovered: geometry.minimumOverlapDisk.fullyCovered,
      followerEngaged: geometry.followers.engaged,
      topAboveBottom: geometry.layerOrder.topAboveBottom
    };
  };
  const snapshot = () => ({
    ...state,
    detentIndex: nearestDetentIndex(),
    detentAngleDeg: nearestDetentIndex() * cad.detentStepDeg,
    parameters: { ...parameters },
    evidenceDefaults: { ...EVIDENCE_CONSTRAINED_FEEL_DEFAULTS },
    cad: {
      contractRevision: contract.revision,
      maxTravelL: cad.maxTravelL,
      grooveEndpointLimitL: cad.grooveEndpointLimitL,
      overlapContainmentLimitL: cad.overlapContainmentLimitL,
      minimumOverlapDiskRadiusL: cad.minimumOverlapDiskRadiusL,
      detentCount: cad.detentCount,
      detentStepDeg: cad.detentStepDeg
    },
    constraints: constraintState()
  });
  const emitClick = (beforeIndex) => {
    if (parameters.clickAudio && beforeIndex !== nearestDetentIndex()) state.clickSequence += 1;
  };
  const clampTravel = (requested) => {
    const bounded = clamp(requested, 0, cad.maxTravelL);
    state.activeStop = requested < 0
      ? "closed"
      : requested > cad.maxTravelL
        ? "minimum-overlap-disk"
        : bounded === 0
          ? "closed"
          : bounded === cad.maxTravelL
            ? "minimum-overlap-disk"
            : "none";
    state.travelL = bounded;
  };
  const applyPointer = ({
    slideDeltaL = 0,
    angleDeltaDeg = 0,
    effort = 1,
    deltaSeconds = 1 / 60
  } = {}) => {
    const dt = Math.max(1 / 1000, Number(deltaSeconds) || 1 / 60);
    const beforeTravel = state.travelL;
    const beforeAngle = state.angleDeg;
    const beforeIndex = nearestDetentIndex();
    const slideGain = 1 - parameters.slideResistance;
    const rotationGain = 1 - parameters.rotationResistance;
    clampTravel(state.travelL + (Number(slideDeltaL) || 0) * slideGain);
    const normalizedEffort = clamp(Math.abs(Number(effort) || 0), 0, 1);
    if (state.captured && normalizedEffort < parameters.breakawayThreshold) {
      state.angularVelocityDegPerSecond = 0;
      state.lastEvent = state.travelL !== beforeTravel ? "slide-held-detent" : "held-below-breakaway";
    } else {
      state.captured = false;
      state.angleDeg = wrap(state.angleDeg + (Number(angleDeltaDeg) || 0) * rotationGain);
      state.angularVelocityDegPerSecond = shortestDelta(beforeAngle, state.angleDeg) / dt;
      state.lastEvent = state.travelL !== beforeTravel && state.angleDeg !== beforeAngle
        ? "compound-motion"
        : state.angleDeg !== beforeAngle
          ? "rotation"
          : "slide";
      emitClick(beforeIndex);
    }
    state.linearVelocityLPerSecond = (state.travelL - beforeTravel) / dt;
    constraintState();
    return snapshot();
  };
  const release = () => {
    state.lastEvent = "released";
    return snapshot();
  };
  const step = (deltaSeconds = 1 / 60) => {
    const dt = Math.max(0, Number(deltaSeconds) || 0);
    if (dt === 0) return snapshot();
    const beforeIndex = nearestDetentIndex();
    const nextTravel = state.travelL + state.linearVelocityLPerSecond * dt * parameters.linearInertia;
    clampTravel(nextTravel);
    state.angleDeg = wrap(state.angleDeg + state.angularVelocityDegPerSecond * dt * parameters.angularInertia);
    state.linearVelocityLPerSecond = decayByHalfLife(
      state.linearVelocityLPerSecond,
      dt,
      parameters.linearDampingHalfLife
    );
    state.angularVelocityDegPerSecond = decayByHalfLife(
      state.angularVelocityDegPerSecond,
      dt,
      parameters.angularDampingHalfLife
    );
    const detentAngle = nearestDetentIndex() * cad.detentStepDeg;
    const detentDelta = shortestDelta(state.angleDeg, detentAngle);
    if (
      Math.abs(state.angularVelocityDegPerSecond) <= parameters.captureSpeedDegPerSecond
      && Math.abs(detentDelta) <= parameters.captureWindowDeg
    ) {
      const capture = 1 - Math.exp(-parameters.detentStrength * 18 * dt);
      state.angleDeg = wrap(state.angleDeg + detentDelta * capture);
      if (Math.abs(detentDelta) < 0.02 && Math.abs(state.angularVelocityDegPerSecond) < 0.5) {
        state.angleDeg = wrap(detentAngle);
        state.angularVelocityDegPerSecond = 0;
        state.captured = true;
        state.lastEvent = "detent-capture";
      }
    }
    if (state.travelL === 0 || state.travelL === cad.maxTravelL) {
      state.linearVelocityLPerSecond *= 1 - parameters.endStopStiffness;
      if (Math.abs(state.linearVelocityLPerSecond) < 1e-6) state.linearVelocityLPerSecond = 0;
    }
    emitClick(beforeIndex);
    constraintState();
    return snapshot();
  };
  const setParameters = (changes, { userTuned = true } = {}) => {
    parameters = { ...parameters, ...changes };
    enforceParameters();
    state.userTuned = userTuned;
    state.lastEvent = "parameters";
    return snapshot();
  };
  const reset = () => {
    state.travelL = 0;
    state.angleDeg = 0;
    state.linearVelocityLPerSecond = 0;
    state.angularVelocityDegPerSecond = 0;
    state.captured = true;
    state.activeStop = "closed";
    state.lastEvent = "reset";
    state.clickSequence = 0;
    return snapshot();
  };
  const restoreDefaults = () => {
    parameters = { ...EVIDENCE_CONSTRAINED_FEEL_DEFAULTS };
    enforceParameters();
    state.userTuned = false;
    return reset();
  };
  return {
    snapshot,
    applyPointer,
    release,
    step,
    setParameters,
    reset,
    restoreDefaults
  };
}
