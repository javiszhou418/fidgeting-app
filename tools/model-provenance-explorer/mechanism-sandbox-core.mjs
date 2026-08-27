export const endpointAxisLocalL = (aspectRatioLW) => {
  if (!Number.isFinite(Number(aspectRatioLW))) throw new Error("Endpoint axis requires contract-derived L/W.");
  return [0, 0.5 - 1 / (2 * Math.max(1, Number(aspectRatioLW)))];
};
export const KINEMATIC_LAYOUT = Object.freeze({
  upperTransform: Object.freeze({ translationL: Object.freeze([0, 0]), rotationDeg: 0 })
});
const constraintById = (contract, id) => {
  const constraint = contract?.constraints?.find((candidate) => candidate.id === id);
  if (!constraint) throw new Error(`Mechanism evidence contract missing ${id}.`);
  return constraint;
};

export function mechanismConfigFromEvidenceContract(contract) {
  if (contract?.modelId !== "magnetic-slide-tile" || contract?.gate !== "02-analysis") {
    throw new Error("Invalid magnetic-slide-tile mechanism evidence contract.");
  }
  const aspect = constraintById(contract, "MEC-SILHOUETTE-ASPECT").value.aspectRatioLW;
  const travel = constraintById(contract, "MEC-TRAVEL-NORMALIZED").value;
  const detents = constraintById(contract, "MEC-DETENTS").value;
  const rotation = constraintById(contract, "MEC-ROTATION-RANGE").value;
  const pivot = constraintById(contract, "MEC-PIVOT-ENDPOINT-ATTACHMENT").value;
  const rails = constraintById(contract, "MEC-RAILS-BILATERAL-LOWER-REVERSE").value;
  if (pivot.localSliding !== false) throw new Error("Contract drift: endpoint pivot must not slide locally.");
  return Object.freeze({
    contractRevision: contract.revision,
    aspectRatioLW: (aspect[0] + aspect[1]) / 2,
    aspectRatioRange: Object.freeze([...aspect]),
    maxTravelL: travel.supportedRange[1],
    supportedTravelRangeL: Object.freeze([...travel.supportedRange]),
    observedPeakTravelL: travel.observedPeak,
    rotationRangeDeg: rotation,
    detentStepDeg: detents.stepDegrees,
    detentCount: detents.countPerRevolution,
    pivotAttachment: pivot.localAttachment,
    pivotLocalSliding: pivot.localSliding,
    railCount: rails.count,
    railOwnerFace: rails.ownerFace,
    railGeometryState: rails.upperFollowerCoupling === "unknown" ? "unknown-awaiting-approved-cad" : "defined"
  });
}

export function assertNoMechanismDefaultDrift(contract, candidate) {
  const authoritative = mechanismConfigFromEvidenceContract(contract);
  for (const key of [
    "aspectRatioLW",
    "maxTravelL",
    "observedPeakTravelL",
    "rotationRangeDeg",
    "detentStepDeg",
    "detentCount",
    "pivotAttachment",
    "pivotLocalSliding",
    "railCount",
    "railOwnerFace",
    "railGeometryState"
  ]) {
    if (JSON.stringify(candidate[key]) !== JSON.stringify(authoritative[key])) {
      throw new Error(`Duplicate mechanism default drift: ${key}.`);
    }
  }
  return true;
}

const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));

export function wrapAngleDeg(angleDeg) {
  const wrapped = angleDeg % 360;
  return wrapped < 0 ? wrapped + 360 : wrapped;
}

export function nearestDetentIndex(angleDeg, config) {
  return Math.round(wrapAngleDeg(angleDeg) / config.detentStepDeg) % config.detentCount;
}

export function detentAngleDeg(index, config) {
  return wrapAngleDeg(index * config.detentStepDeg);
}

export function shortestAngleDeltaDeg(fromDeg, toDeg) {
  return ((toDeg - fromDeg + 540) % 360) - 180;
}

export function decayByHalfLife(value, deltaSeconds, halfLifeSeconds) {
  if (halfLifeSeconds <= 0) return 0;
  return value * Math.pow(0.5, Math.max(0, deltaSeconds) / halfLifeSeconds);
}

export function composeMechanismTransforms(travelL, angleDeg, config) {
  if (!config) throw new Error("Mechanism config must come from the evidence contract.");
  const translation = [0, clamp(travelL, 0, config.observedPeakTravelL)];
  const axisLocalL = endpointAxisLocalL(config.aspectRatioLW);
  const axisWorldL = [
    axisLocalL[0] + translation[0],
    axisLocalL[1] + translation[1]
  ];
  return {
    upper: KINEMATIC_LAYOUT.upperTransform,
    lower: {
      translationL: translation,
      rotationDeg: wrapAngleDeg(angleDeg),
      rotationPivotWorldL: axisWorldL
    },
    axis: {
      owner: "lower-carrier",
      localL: axisLocalL,
      localToLowerL: axisLocalL,
      worldL: axisWorldL,
      attachment: "fixed-bottom-endcap-center",
      independentDof: false
    },
    rails: {
      owner: "lower-carrier",
      bilateral: true,
      count: config.railCount,
      ownerFace: config.railOwnerFace,
      geometryState: config.railGeometryState,
      localL: [],
      worldL: [],
      relativeConstraintBetweenPlates: true,
      pivotTraversesRailsIndependently: false
    }
  };
}

export function createMechanismSandbox(contract, overrides = {}) {
  const evidenceConfig = mechanismConfigFromEvidenceContract(contract);
  const requiredTuning = [
    "slideResistance",
    "rotationResistance",
    "detentStrength",
    "breakaway",
    "damping",
    "inertiaHalfLife",
    "endStopSoftness",
    "endStopStiffness",
    "captureSpeedDegPerSecond",
    "captureWindowDeg"
  ];
  for (const key of requiredTuning) {
    if (!Number.isFinite(Number(overrides[key]))) {
      throw new Error(`Unmeasured sandbox tuning requires explicit test/user input: ${key}.`);
    }
  }
  const initialTuning = Object.fromEntries(requiredTuning.map((key) => [key, Number(overrides[key])]));
  let parameters = { ...evidenceConfig, ...initialTuning, ...overrides };
  const state = {
    travelL: 0,
    linearVelocityLPerSecond: 0,
    angleDeg: 0,
    angularVelocityDegPerSecond: 0,
    captured: true,
    lastEvent: "reset",
    userTuned: false
  };

  const enforceParameters = () => {
    parameters.maxTravelL = clamp(Number(parameters.maxTravelL), 0.05, evidenceConfig.observedPeakTravelL);
    parameters.slideResistance = clamp(Number(parameters.slideResistance), 0, 1);
    parameters.rotationResistance = clamp(Number(parameters.rotationResistance), 0, 1);
    parameters.detentStrength = clamp(Number(parameters.detentStrength), 0, 1);
    parameters.breakaway = clamp(Number(parameters.breakaway), 0, 1);
    parameters.damping = clamp(Number(parameters.damping), 0, 1);
    parameters.inertiaHalfLife = clamp(Number(parameters.inertiaHalfLife), 0.04, 2);
    parameters.endStopSoftness = clamp(Number(parameters.endStopSoftness), 0, 0.2);
    parameters.endStopStiffness = clamp(Number(parameters.endStopStiffness), 0, 1);
  };
  enforceParameters();

  const snapshot = () => ({
    ...state,
    detentIndex: nearestDetentIndex(state.angleDeg, evidenceConfig),
    transforms: composeMechanismTransforms(state.travelL, state.angleDeg, evidenceConfig),
    parameters: { ...parameters }
  });

  const reset = () => {
    state.travelL = 0;
    state.linearVelocityLPerSecond = 0;
    state.angleDeg = 0;
    state.angularVelocityDegPerSecond = 0;
    state.captured = true;
    state.lastEvent = "reset";
    return snapshot();
  };

  const setParameters = (changes, { markUserTuned = true } = {}) => {
    parameters = { ...parameters, ...changes };
    enforceParameters();
    state.travelL = clamp(state.travelL, 0, parameters.maxTravelL);
    if (markUserTuned) state.userTuned = true;
    state.lastEvent = "parameters";
    return snapshot();
  };

  const restoreEvidenceDefaults = () => {
    parameters = { ...evidenceConfig, ...initialTuning };
    state.userTuned = false;
    enforceParameters();
    return reset();
  };

  const setSlideTravel = (requestedTravelL) => {
    const requested = Number.isFinite(requestedTravelL) ? requestedTravelL : state.travelL;
    const bounded = clamp(requested, 0, parameters.maxTravelL);
    const edgeDistance = Math.min(bounded, parameters.maxTravelL - bounded);
    if (edgeDistance < parameters.endStopSoftness && parameters.endStopSoftness > 0) {
      const edge = bounded < parameters.maxTravelL / 2 ? 0 : parameters.maxTravelL;
      const blend = parameters.endStopStiffness * (1 - edgeDistance / parameters.endStopSoftness);
      state.travelL = bounded + (edge - bounded) * clamp(blend, 0, 1);
    } else {
      state.travelL = bounded;
    }
    state.lastEvent = requested < 0
      ? "closed-stop"
      : requested > parameters.maxTravelL
        ? "open-stop"
        : state.travelL === 0
          ? "closed"
          : "sliding";
    return snapshot();
  };

  const applyCompoundPointer = ({
    slideDeltaL = 0,
    angleDeltaDeg = 0,
    effort = 1,
    deltaSeconds = 1 / 60
  } = {}) => {
    const previousTravel = state.travelL;
    setSlideTravel(previousTravel + (Number(slideDeltaL) || 0));
    const dt = Math.max(1 / 1000, Number(deltaSeconds) || 1 / 60);
    state.linearVelocityLPerSecond = (state.travelL - previousTravel) / dt;
    const slideChanged = Math.abs(state.travelL - previousTravel) > 1e-9;
    const previousAngle = state.angleDeg;
    rotateByPointer(angleDeltaDeg, effort, dt);
    const angleChanged = Math.abs(shortestAngleDeltaDeg(previousAngle, state.angleDeg)) > 1e-9;
    state.lastEvent = slideChanged && angleChanged
      ? "compound-motion"
      : slideChanged
        ? "sliding"
        : angleChanged
          ? state.lastEvent
          : "held";
    return snapshot();
  };

  const rotateByPointer = (deltaDeg, effort = 1, deltaSeconds = 1 / 60) => {
    const signedDelta = Number.isFinite(deltaDeg) ? deltaDeg : 0;
    const normalizedEffort = clamp(Math.abs(effort), 0, 1);
    if (state.captured && normalizedEffort < parameters.breakaway) {
      state.angularVelocityDegPerSecond = 0;
      state.lastEvent = "held-below-breakaway";
      return snapshot();
    }
    if (state.captured) {
      state.captured = false;
      state.lastEvent = "breakaway";
    } else {
      state.lastEvent = "rotating";
    }
    const resistanceScale = 1 - parameters.rotationResistance * 0.72;
    const appliedDelta = signedDelta * resistanceScale;
    state.angleDeg = wrapAngleDeg(state.angleDeg + appliedDelta);
    state.angularVelocityDegPerSecond = deltaSeconds > 0 ? appliedDelta / deltaSeconds : 0;
    return snapshot();
  };

  const setDetentIndex = (index) => {
    const count = evidenceConfig.detentCount;
    const normalizedIndex = ((Math.round(Number(index) || 0) % count) + count) % count;
    state.angleDeg = detentAngleDeg(normalizedIndex, evidenceConfig);
    state.angularVelocityDegPerSecond = 0;
    state.captured = true;
    state.lastEvent = "capture";
    return snapshot();
  };

  const setPose = ({ travelL = state.travelL, angleDeg = state.angleDeg } = {}) => {
    setSlideTravel(travelL);
    state.linearVelocityLPerSecond = 0;
    state.angleDeg = wrapAngleDeg(Number(angleDeg) || 0);
    state.angularVelocityDegPerSecond = 0;
    state.captured = true;
    state.lastEvent = "pose";
    return snapshot();
  };

  const releaseRotation = () => {
    state.lastEvent = "released";
    return snapshot();
  };

  const releaseCompound = () => {
    state.lastEvent = "released";
    return snapshot();
  };

  const step = (deltaSeconds) => {
    const dt = Math.max(0, Number(deltaSeconds) || 0);
    state.linearVelocityLPerSecond = decayByHalfLife(
      state.linearVelocityLPerSecond,
      dt,
      parameters.inertiaHalfLife * (1 - parameters.slideResistance * 0.72)
    );
    if (Math.abs(state.linearVelocityLPerSecond) < 0.0005) {
      state.linearVelocityLPerSecond = 0;
    } else {
      const previousTravel = state.travelL;
      setSlideTravel(state.travelL + state.linearVelocityLPerSecond * dt);
      if (state.travelL === previousTravel || state.travelL === 0 || state.travelL === parameters.maxTravelL) {
        state.linearVelocityLPerSecond = 0;
      }
    }
    if (state.captured) {
      state.angularVelocityDegPerSecond = 0;
      return snapshot();
    }
    state.angularVelocityDegPerSecond = decayByHalfLife(
      state.angularVelocityDegPerSecond,
      dt,
      parameters.inertiaHalfLife * (1 - parameters.damping * 0.72)
    );
    state.angleDeg = wrapAngleDeg(state.angleDeg + state.angularVelocityDegPerSecond * dt);
    const target = detentAngleDeg(nearestDetentIndex(state.angleDeg, evidenceConfig), evidenceConfig);
    const targetDelta = shortestAngleDeltaDeg(state.angleDeg, target);
    const canCapture = Math.abs(state.angularVelocityDegPerSecond) <= parameters.captureSpeedDegPerSecond
      && Math.abs(targetDelta) <= parameters.captureWindowDeg + parameters.detentStrength * 2.8;
    if (canCapture) {
      state.angleDeg = target;
      state.angularVelocityDegPerSecond = 0;
      state.captured = true;
      state.lastEvent = "capture";
    }
    return snapshot();
  };

  return {
    snapshot,
    reset,
    setParameters,
    restoreEvidenceDefaults,
    setSlideTravel,
    applyCompoundPointer,
    rotateByPointer,
    setDetentIndex,
    setPose,
    releaseRotation,
    releaseCompound,
    step
  };
}
