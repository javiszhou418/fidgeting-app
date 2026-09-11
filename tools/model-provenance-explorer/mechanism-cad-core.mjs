export const CAD_STATUS = Object.freeze({
  observed: "实测",
  video: "视频比例",
  user: "用户输入",
  unknown: "未知"
});

export function deriveCadTravelBounds({
  aspectRatioLW,
  axisNormalizedY,
  minimumOverlapDiskRadiusL,
  grooveEndpointLimitL
}) {
  const capsuleRadiusL = 1 / (2 * aspectRatioLW);
  const closedMarginL = Math.min(
    capsuleRadiusL,
    axisNormalizedY,
    1 - axisNormalizedY
  ) - minimumOverlapDiskRadiusL;
  const overlapContainmentLimitL = Math.max(
    0,
    1 - axisNormalizedY - minimumOverlapDiskRadiusL
  );
  const actualSMaxL = Math.min(grooveEndpointLimitL, overlapContainmentLimitL);
  const limitingCause = overlapContainmentLimitL < grooveEndpointLimitL - 1e-12
    ? "MinimumOverlapDisk"
    : grooveEndpointLimitL < overlapContainmentLimitL - 1e-12
      ? "FiniteGrooveEndpoint"
      : "Both";
  return {
    capsuleRadiusL,
    closedMarginL,
    grooveEndpointLimitL,
    overlapContainmentLimitL,
    actualSMaxL,
    limitingCause,
    angleInvariant: true
  };
}

export function minimumOverlapContainmentMargin(travelL, config) {
  const bounds = deriveCadTravelBounds(config);
  const diskCenterInTopL = config.axisNormalizedY + Number(travelL);
  const sideMarginL = bounds.capsuleRadiusL - config.minimumOverlapDiskRadiusL;
  const topMarginL = diskCenterInTopL - config.minimumOverlapDiskRadiusL;
  const bottomMarginL = 1 - diskCenterInTopL - config.minimumOverlapDiskRadiusL;
  const marginL = Math.min(sideMarginL, topMarginL, bottomMarginL);
  return {
    marginL,
    sideMarginL,
    topMarginL,
    bottomMarginL,
    valid: marginL >= -1e-9,
    boundaryContact: Math.abs(bottomMarginL) <= 1e-9 || Math.abs(marginL) <= 1e-9,
    diskCenterInTopL,
    angleInvariant: true
  };
}

export function refreshCadTravelBounds(config) {
  const bounds = deriveCadTravelBounds(config);
  config.overlapContainmentLimitL = bounds.overlapContainmentLimitL;
  config.maxTravelL = bounds.actualSMaxL;
  config.limitingCause = bounds.limitingCause;
  return bounds;
}

const constraintById = (contract, id) => {
  const constraint = contract?.constraints?.find((candidate) => candidate.id === id);
  if (!constraint) throw new Error(`Mechanism evidence contract missing ${id}.`);
  return constraint;
};

export function cadConfigFromEvidenceContract(contract, simulatorConfig = {}) {
  const aspect = constraintById(contract, "MEC-SILHOUETTE-ASPECT").value.aspectRatioLW;
  const travel = constraintById(contract, "MEC-TRAVEL-NORMALIZED").value;
  const detents = constraintById(contract, "MEC-DETENTS").value;
  const bottom = constraintById(contract, "MEC-BOTTOM-EXTERIOR-NO-RAILS").value;
  const axis = constraintById(contract, "MEC-AXIS-MODULE-FIXED").value;
  const carrier = constraintById(contract, "MEC-ROTATING-CARRIER").value;
  const followers = constraintById(contract, "MEC-CARRIER-FOLLOWERS-BILATERAL").value;
  const grooves = constraintById(contract, "MEC-TOP-UNDERSIDE-GROOVES").value;
  const topTransform = constraintById(contract, "MEC-TOP-CARRIER-LOCAL-TRANSLATION").value;
  const coverage = constraintById(contract, "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL").value;
  const finiteGroove = constraintById(contract, "MEC-FINITE-GROOVE-ENDPOINT-STOPS").value;
  const overlapDisk = constraintById(contract, "MEC-MINIMUM-OVERLAP-DISK").value;
  const dualBound = constraintById(contract, "MEC-ACTUAL-TRAVEL-DUAL-BOUND").value;
  const continuousContainment = constraintById(contract, "MEC-CONTINUOUS-OVERLAP-CONTAINMENT").value;
  const endpointInterlock = contract.constraints
    .find((candidate) => candidate.id === "MEC-ENDPOINT-ROTATION-INTERLOCK")?.value;
  const fourTrackRoles = contract.constraints.find((candidate) => candidate.id === "MEC-FOUR-TRACK-ROLES")?.value;
  const raisedAxisBoss = contract.constraints.find((candidate) => candidate.id === "MEC-RAISED-AXIS-BOSS")?.value;
  const ballContacts = contract.constraints.find((candidate) => candidate.id === "MEC-BALL-CONTACT-CANDIDATES")?.value;
  if (simulatorConfig.contractSha256 !== simulatorConfig.expectedContractSha256) {
    throw new Error("CAD contract hash drift.");
  }
  if (
    axis.independentSlidingDof !== false
    || axis.localPosition !== "constant"
    || axis.worldPosition !== "constant"
    || bottom.exposedRailCount !== 0
    || bottom.exposedGrooveCount !== 0
    || carrier.translation !== false
    || followers.count !== 2
    || ![2, 4].includes(grooves.count)
    || topTransform.carrierAngleShared !== true
    || coverage.axisMustRemainInsideTopSilhouette !== true
    || finiteGroove.grooveCount !== grooves.count
    || finiteGroove.followerCount !== 2
    || finiteGroove.sMin !== 0
    || finiteGroove.maximumOpenEndpoint.fixedAxisCovered !== true
    || finiteGroove.maximumOpenEndpoint.followerEngaged !== true
    || overlapDisk.owner !== "BottomBase"
    || overlapDisk.center !== "FixedAxis"
    || dualBound.angleInvariant !== true
    || continuousContainment.analyticCheck !== true
    || (endpointInterlock && endpointInterlock.noSimultaneousVelocitiesBelowEndpoint !== true)
    || (endpointInterlock && endpointInterlock.hiddenLatchGeometry !== "unknown-not-modeled")
  ) {
    throw new Error("Unsupported rotating-carrier mechanism contract.");
  }
  if (grooves.count === 4 && (
    fourTrackRoles?.outerTrackCount !== 2
    || fourTrackRoles?.innerTrackCount !== 2
    || raisedAxisBoss?.protrusionPositive !== true
    || raisedAxisBoss?.recessedAxis !== false
    || ballContacts?.ballDiameterMm?.[0] !== 2
    || ballContacts?.ballDiameterMm?.[1] !== 3
    || grooves.widthMm?.maximum > 3
  )) throw new Error("Four-track raised-axis contract blockers failed.");
  const diagram = simulatorConfig.diagrammaticGeometry || {};
  const normalizedAspectRatio = (aspect[0] + aspect[1]) / 2;
  const grooveEndpointLimitL = finiteGroove.grooveEndNormalizedFromTopL - finiteGroove.grooveStartNormalizedFromTopL;
  const bounds = deriveCadTravelBounds({
    aspectRatioLW: normalizedAspectRatio,
    axisNormalizedY: diagram.axisNormalizedY,
    minimumOverlapDiskRadiusL: overlapDisk.radiusNormalizedL,
    grooveEndpointLimitL
  });
  return {
    aspectRatioLW: normalizedAspectRatio,
    aspectRatioRange: Object.freeze([...aspect]),
    supportedTravelRangeL: Object.freeze([...travel.supportedRange]),
    maxTravelL: bounds.actualSMaxL,
    grooveEndpointLimitL,
    overlapContainmentLimitL: bounds.overlapContainmentLimitL,
    limitingCause: bounds.limitingCause,
    observedPeakTravelL: travel.observedPeak,
    detentCount: detents.countPerRevolution,
    detentStepDeg: detents.stepDegrees,
    axisNormalizedY: diagram.axisNormalizedY,
    carrierRadiusL: diagram.carrierRadiusL,
    carrierSideCutoutHalfWidthL: diagram.carrierSideCutoutHalfWidthL,
    followerOffsetXL: diagram.followerOffsetXL,
    grooveOffsetXL: diagram.grooveOffsetXL,
    innerGrooveOffsetXL: diagram.innerGrooveOffsetXL || diagram.grooveOffsetXL,
    outerGrooveOffsetXL: diagram.outerGrooveOffsetXL || diagram.grooveOffsetXL,
    trackCount: grooves.count,
    trackWidthMm: diagram.trackWidthMm || null,
    ballDiameterMm: diagram.ballDiameterMm || null,
    ballDiameterRangeMm: ballContacts?.ballDiameterMm || null,
    axisBossProtrusionMm: diagram.axisBossProtrusionMm || null,
    recessedAxis: raisedAxisBoss?.recessedAxis ?? null,
    grooveStartFromTopL: finiteGroove.grooveStartNormalizedFromTopL,
    grooveEndFromTopL: finiteGroove.grooveEndNormalizedFromTopL,
    diagrammaticResidualAtEvidenceMaxL: coverage.diagrammaticResidualAtEvidenceMaxL,
    componentLayers: Object.freeze([...(simulatorConfig.componentLayers || [])]),
    minimumPhysicalCoverMarginL: null,
    closedStopL: finiteGroove.sMin,
    closedStopThetaDeg: 0,
    closedStopVectorTolerance: 1e-9,
    negativeTravelForbidden: true,
    grooveLengthL: grooveEndpointLimitL,
    minimumOverlapDiskRadiusL: overlapDisk.radiusNormalizedL,
    minimumOverlapDiskPhysicalMm: null,
    overlapDiskSourceStatus: simulatorConfig.overlapDisk?.sourceStatus || "用户输入 · reviewed CAD normalized",
    denseSweepDegrees: continuousContainment.denseSweepDegrees,
    topZ: 2,
    bottomZ: 0,
    carrierZ: 1,
    sweepSlideSampleFractions: Object.freeze([0, 0.25, 0.5, 0.75, 1]),
    rotationUnlockTravelL: bounds.actualSMaxL,
    endpointToleranceL: 1e-9,
    alignmentToleranceDeg: endpointInterlock?.alignmentToleranceDegrees ?? 0,
    endpointRotationOnly: Boolean(endpointInterlock),
    simultaneousMotionForbidden: Boolean(endpointInterlock)
  };
}

export const PHYSICAL_FIELDS = Object.freeze([
  Object.freeze({ id: "overallLength", label: "总长 L", unit: "mm" }),
  Object.freeze({ id: "overallWidth", label: "总宽 W", unit: "mm" }),
  Object.freeze({ id: "totalThickness", label: "总厚度", unit: "mm" }),
  Object.freeze({ id: "upperThickness", label: "上片厚度", unit: "mm" }),
  Object.freeze({ id: "lowerThickness", label: "下片厚度", unit: "mm" }),
  Object.freeze({ id: "closedGap", label: "闭合缝隙", unit: "mm" }),
  Object.freeze({ id: "railSpacing", label: "双轨中心距", unit: "mm" }),
  Object.freeze({ id: "railWidth", label: "单轨宽度", unit: "mm" }),
  Object.freeze({ id: "axisDiameter", label: "轴心直径", unit: "mm" }),
  Object.freeze({ id: "upperStepHeight", label: "上片台阶高", unit: "mm" }),
  Object.freeze({ id: "lowerStepHeight", label: "下片台阶高", unit: "mm" }),
  Object.freeze({ id: "clearance", label: "活动间隙", unit: "mm" }),
  Object.freeze({ id: "manufacturingAllowance", label: "加工余量", unit: "mm" }),
  Object.freeze({ id: "tolerance", label: "制造公差 ±", unit: "mm" }),
  Object.freeze({ id: "maxTravelMm", label: "最大行程", unit: "mm" })
]);

const clamp = (value, minimum, maximum) => Math.min(maximum, Math.max(minimum, value));
const normalizedAngle = (value) => ((Number(value) % 360) + 360) % 360;
const signedAlignmentError = (value) => {
  const wrapped = normalizedAngle(value);
  return Math.min(wrapped, 360 - wrapped);
};

export function resolveEndpointInterlock(current = {}, request = {}, config) {
  if (!config?.endpointRotationOnly) throw new Error("Endpoint interlock requires the current mechanism contract.");
  const currentTravelL = clamp(Number(current.travelL) || 0, 0, config.maxTravelL);
  const currentAngleDeg = normalizedAngle(current.angleDeg || 0);
  const requestedTravelL = clamp(
    Number.isFinite(Number(request.travelL)) ? Number(request.travelL) : currentTravelL,
    0,
    config.maxTravelL
  );
  const requestedAngleDeg = normalizedAngle(
    Number.isFinite(Number(request.angleDeg)) ? Number(request.angleDeg) : currentAngleDeg
  );
  const atEndpoint = currentTravelL >= config.maxTravelL - config.endpointToleranceL;
  const aligned = signedAlignmentError(currentAngleDeg) <= config.alignmentToleranceDeg;
  const intent = request.intent || "pose";
  if (intent === "rotate") {
    if (!atEndpoint) {
      return {
        travelL: currentTravelL,
        angleDeg: 0,
        state: currentTravelL <= config.endpointToleranceL ? "closed-aligned" : "sliding-aligned",
        rotationBlocked: true,
        slideBlocked: false,
        reason: "rotation-locked-until-sMax"
      };
    }
    return {
      travelL: config.maxTravelL,
      angleDeg: requestedAngleDeg,
      state: signedAlignmentError(requestedAngleDeg) <= config.alignmentToleranceDeg
        ? "endpoint-aligned"
        : "endpoint-rotating",
      rotationBlocked: false,
      slideBlocked: signedAlignmentError(requestedAngleDeg) > config.alignmentToleranceDeg,
      reason: "rotation-unlocked-at-sMax"
    };
  }
  if (intent === "slide") {
    if (!aligned) {
      return {
        travelL: config.maxTravelL,
        angleDeg: currentAngleDeg,
        state: "endpoint-rotating",
        rotationBlocked: false,
        slideBlocked: true,
        reason: "slide-locked-until-0-or-360"
      };
    }
    return {
      travelL: requestedTravelL,
      angleDeg: 0,
      state: requestedTravelL >= config.maxTravelL - config.endpointToleranceL
        ? "endpoint-aligned"
        : requestedTravelL <= config.endpointToleranceL
          ? "closed-aligned"
          : "sliding-aligned",
      rotationBlocked: requestedTravelL < config.maxTravelL - config.endpointToleranceL,
      slideBlocked: false,
      reason: "aligned-slide"
    };
  }
  if (signedAlignmentError(requestedAngleDeg) > config.alignmentToleranceDeg) {
    return {
      travelL: config.maxTravelL,
      angleDeg: requestedAngleDeg,
      state: "endpoint-rotating",
      rotationBlocked: false,
      slideBlocked: true,
      reason: "projected-to-legal-endpoint-pose"
    };
  }
  return resolveEndpointInterlock(current, { ...request, angleDeg: 0, intent: "slide" }, config);
}
const positiveNumber = (value) => {
  if (value === "" || value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : null;
};

const rotatePoint = (point, pivot, angleDeg) => {
  const radians = angleDeg * Math.PI / 180;
  const cosine = Math.cos(radians);
  const sine = Math.sin(radians);
  const dx = point[0] - pivot[0];
  const dy = point[1] - pivot[1];
  return [
    pivot[0] + dx * cosine - dy * sine,
    pivot[1] + dx * sine + dy * cosine
  ];
};

export function createCapsuleGeometry({
  x = 210,
  y = 105,
  width = 240,
  aspectRatioLW
} = {}) {
  if (!Number.isFinite(Number(aspectRatioLW))) throw new Error("CAD geometry requires contract-derived L/W.");
  const length = width * aspectRatioLW;
  const radius = width / 2;
  const bottom = y + length;
  const topTangentY = y + radius;
  const bottomTangentY = bottom - radius;
  const centerX = x + radius;
  const endcapCenters = {
    top: [centerX, topTangentY],
    bottom: [centerX, bottomTangentY]
  };
  return {
    x,
    y,
    width,
    length,
    radius,
    centerX,
    centerY: y + length / 2,
    topTangentY,
    bottomTangentY,
    endcapCenters,
    endpointAxisCandidate: endcapCenters.bottom,
    tangentPoints: [
      [x, topTangentY],
      [x + width, topTangentY],
      [x, bottomTangentY],
      [x + width, bottomTangentY]
    ],
    path: [
      `M ${centerX} ${y}`,
      `A ${radius} ${radius} 0 0 1 ${x + width} ${topTangentY}`,
      `L ${x + width} ${bottomTangentY}`,
      `A ${radius} ${radius} 0 0 1 ${centerX} ${bottom}`,
      `A ${radius} ${radius} 0 0 1 ${x} ${bottomTangentY}`,
      `L ${x} ${topTangentY}`,
      `A ${radius} ${radius} 0 0 1 ${centerX} ${y}`,
      "Z"
    ].join(" ")
  };
}

export function computeCadGeometry({
  travelL = 0,
  angleDeg = 0,
  debugAllowInvalid = false
} = {}, config) {
  if (!config) throw new Error("CAD config must come from the mechanism evidence contract.");
  const travelBounds = refreshCadTravelBounds(config);
  const bottom = createCapsuleGeometry({ aspectRatioLW: config.aspectRatioLW });
  const geometricCoverageLimitL = 1 - config.axisNormalizedY;
  const requestedTravelL = Number.isFinite(Number(travelL)) ? Number(travelL) : 0;
  const boundedTravelL = clamp(
    requestedTravelL,
    0,
    debugAllowInvalid
      ? geometricCoverageLimitL
      : Math.min(config.maxTravelL, geometricCoverageLimitL)
  );
  const localTranslation = [0, boundedTravelL === 0 ? 0 : -boundedTravelL * bottom.length];
  const axisLocal = [bottom.centerX, bottom.y + config.axisNormalizedY * bottom.length];
  const axisWorld = [...axisLocal];
  const carrierRadius = config.carrierRadiusL * bottom.length;
  const followerLocal = [
    { side: "left", point: [axisLocal[0] - config.followerOffsetXL * bottom.length, axisLocal[1]] },
    { side: "right", point: [axisLocal[0] + config.followerOffsetXL * bottom.length, axisLocal[1]] }
  ];
  const followerWorld = followerLocal.map((follower) => ({
    side: follower.side,
    point: rotatePoint(follower.point, axisWorld, angleDeg)
  }));
  const grooveDefinitions = config.trackCount === 4
    ? [
        ["TopOuterGrooveLeft", "outer-left", -1, config.outerGrooveOffsetXL, "fore-aft-slide"],
        ["TopInnerGrooveLeft", "inner-left", -1, config.innerGrooveOffsetXL, "central-axis-link"],
        ["TopInnerGrooveRight", "inner-right", 1, config.innerGrooveOffsetXL, "central-axis-link"],
        ["TopOuterGrooveRight", "outer-right", 1, config.outerGrooveOffsetXL, "fore-aft-slide"]
      ]
    : [
        ["TopGrooveLeft", "left", -1, config.grooveOffsetXL, "central-axis-link"],
        ["TopGrooveRight", "right", 1, config.grooveOffsetXL, "central-axis-link"]
      ];
  const grooveLocal = grooveDefinitions.map(([id, side, sign, offsetL, role]) => {
    return {
      id,
      side,
      role,
      start: [
        axisLocal[0] + sign * offsetL * bottom.length,
        bottom.y + config.grooveStartFromTopL * bottom.length
      ],
      end: [
        axisLocal[0] + sign * config.grooveOffsetXL * bottom.length,
        bottom.y + config.grooveEndFromTopL * bottom.length
      ]
    };
  });
  const transformTopPoint = (point) => rotatePoint(
    [point[0] + localTranslation[0], point[1] + localTranslation[1]],
    axisWorld,
    angleDeg
  );
  const grooveWorld = grooveLocal.map((groove) => ({
    side: groove.side,
    role: groove.role,
    start: transformTopPoint(groove.start),
    end: transformTopPoint(groove.end)
  }));
  const axisInTopLocal = [
    axisLocal[0] - localTranslation[0],
    axisLocal[1] - localTranslation[1]
  ];
  const coverResidualL = (bottom.y + bottom.length - axisInTopLocal[1]) / bottom.length;
  const axisCovered = coverResidualL >= -1e-9;
  const followerUFromTopL = config.grooveStartFromTopL + boundedTravelL;
  const followerDistanceToStartL = followerUFromTopL - config.grooveStartFromTopL;
  const followerDistanceToEndL = config.grooveEndFromTopL - followerUFromTopL;
  const followerEngaged = followerDistanceToStartL >= -config.closedStopVectorTolerance
    && followerDistanceToEndL >= -config.closedStopVectorTolerance;
  const overlapContainment = minimumOverlapContainmentMargin(boundedTravelL, config);
  const requestedOverlapContainment = minimumOverlapContainmentMargin(requestedTravelL, config);
  const overlapBoundaryLocal = [
    axisWorld[0],
    axisWorld[1] + config.minimumOverlapDiskRadiusL * bottom.length
  ];
  const overlapBoundaryWorld = rotatePoint(overlapBoundaryLocal, axisWorld, angleDeg);
  const normalizedAngleDeg = ((Number(angleDeg) % 360) + 360) % 360;
  const alignmentErrorDeg = signedAlignmentError(normalizedAngleDeg);
  const atMaximumTravel = boundedTravelL >= config.maxTravelL - config.endpointToleranceL;
  const angleAligned = alignmentErrorDeg <= config.alignmentToleranceDeg;
  const atClosedStop = boundedTravelL <= config.closedStopVectorTolerance;
  const closedSilhouettesCoincident = atClosedStop
    && Math.min(normalizedAngleDeg, 360 - normalizedAngleDeg) <= config.closedStopVectorTolerance;
  return {
    upper: bottom,
    bottom: {
      geometry: bottom,
      transform: "identity",
      exteriorFront: "smooth",
      exteriorBack: "smooth",
      exposedRailCount: 0,
      exposedGrooveCount: 0,
      z: config.bottomZ
    },
    top: {
      localTranslation,
      angleDeg,
      transform: `rotate(${angleDeg} ${axisWorld[0]} ${axisWorld[1]}) translate(${localTranslation[0]} ${localTranslation[1]})`,
      axisInLocal: axisInTopLocal,
      z: config.topZ,
      alwaysAboveBottom: config.topZ > config.bottomZ
    },
    axis: {
      local: axisLocal,
      localToBottom: axisLocal,
      world: axisWorld,
      attachment: "fixed-axis-center-in-bottom",
      independentDof: false,
      construction: {
        source: "user-selected-perspective-images",
        normalizedYFromTop: config.axisNormalizedY,
        physicalPosition: "unknown"
      }
    },
    carrier: {
      center: axisWorld,
      angleDeg,
      radius: carrierRadius,
      sideCutoutHalfWidth: config.carrierSideCutoutHalfWidthL * bottom.length,
      transform: `rotate(${angleDeg} ${axisWorld[0]} ${axisWorld[1]})`,
      translation: [0, 0],
      z: config.carrierZ
    },
    followers: {
      local: followerLocal,
      world: followerWorld,
      owner: "RotatingCarrier",
      count: 2,
      uFromTopL: followerUFromTopL,
      distanceToStartL: followerDistanceToStartL,
      distanceToEndL: followerDistanceToEndL,
      engaged: followerEngaged,
      atClosedEndpoint: followerDistanceToStartL <= config.closedStopVectorTolerance,
      atOpenEndpoint: followerDistanceToEndL <= config.closedStopVectorTolerance
    },
    grooves: {
      local: grooveLocal,
      world: grooveWorld,
      owner: "TopPlate underside",
      count: grooveLocal.length,
      parallelToFollowers: true,
      finite: true,
      startFromTopL: config.grooveStartFromTopL,
      endFromTopL: config.grooveEndFromTopL,
      lengthL: config.grooveLengthL
    },
    rotationRing: {
      center: axisWorld,
      radius: 148,
      detentCount: config.detentCount
    },
    interlock: {
      state: !config.endpointRotationOnly
        ? "legacy-unrestricted"
        : atMaximumTravel
        ? angleAligned ? "endpoint-aligned" : "endpoint-rotating"
        : atClosedStop ? "closed-aligned" : "sliding-aligned",
      rotationUnlocked: !config.endpointRotationOnly || atMaximumTravel,
      rotationBlocked: config.endpointRotationOnly && !atMaximumTravel,
      slideBlocked: config.endpointRotationOnly && !angleAligned,
      angleAligned,
      alignmentErrorDeg,
      legalPose: !config.endpointRotationOnly || angleAligned || atMaximumTravel,
      endpointOnly: config.endpointRotationOnly,
      hiddenLatchGeometry: "unknown-not-modeled"
    },
    side: {
      bottomTransform: "translate(0 0)",
      topTranslationX: boundedTravelL * 255,
      axisLocalFraction: (axisLocal[1] - bottom.y) / bottom.length,
      angleDeg,
      carrierTransform: `rotate(${angleDeg})`
    },
    section: {
      bottomTransform: "translate(0 0)",
      topTranslationX: boundedTravelL * 180,
      axisLocalInvariant: true,
      axisWorldInvariant: true,
      angleDeg
    },
    coverage: {
      axisCovered,
      coverResidualL,
      geometricLimitL: geometricCoverageLimitL,
      configuredMaxTravelL: config.maxTravelL,
      physicalMinimumMarginL: config.minimumPhysicalCoverMarginL,
      exactPhysicalMarginKnown: false
    },
    closedStop: {
      valueL: 0,
      atStop: atClosedStop,
      requestedTravelL,
      inputClamped: requestedTravelL < 0,
      negativeTravelForbidden: true,
      penetrationL: 0,
      closedThetaDeg: 0,
      silhouettesCoincident: closedSilhouettesCoincident,
      vectorTolerance: config.closedStopVectorTolerance,
      type: "hard-cad-kinematic"
    },
    layerOrder: {
      bottomZ: config.bottomZ,
      carrierZ: config.carrierZ,
      topZ: config.topZ,
      topAboveBottom: config.topZ > config.bottomZ,
      bottomMasksTop: false
    },
    minimumOverlapDisk: {
      id: "MinimumOverlapDisk",
      owner: "BottomBase",
      center: [...axisWorld],
      radiusL: config.minimumOverlapDiskRadiusL,
      radiusPx: config.minimumOverlapDiskRadiusL * bottom.length,
      physicalRadiusMm: null,
      containment: overlapContainment,
      requestedContainment: requestedOverlapContainment,
      fullyCovered: overlapContainment.valid,
      boundaryContact: overlapContainment.boundaryContact,
      boundaryContactWorld: overlapBoundaryWorld,
      activeLimitingCause: travelBounds.limitingCause,
      derivedSMaxL: travelBounds.actualSMaxL,
      grooveEndpointLimitL: travelBounds.grooveEndpointLimitL,
      overlapContainmentLimitL: travelBounds.overlapContainmentLimitL,
      angleInvariant: travelBounds.angleInvariant,
      debugInvalidPose: debugAllowInvalid && !overlapContainment.valid
    },
    axisBoss: {
      protrusionMm: config.axisBossProtrusionMm,
      protrusionPositive: Number(config.axisBossProtrusionMm) > 0,
      recessedAxis: config.recessedAxis === true,
      visibleCavityAllowed: false
    },
    ballContacts: {
      diameterMm: config.ballDiameterMm,
      authorizedRangeMm: config.ballDiameterRangeMm,
      count: null,
      material: "unknown"
    },
    componentLayers: config.trackCount === 4 ? [
      { id: "BottomExterior", parent: null, state: "user-authoritative", transform: "identity" },
      { id: "FixedAxisBoss", parent: "BottomExterior", state: "user-authoritative", transform: "identity" },
      { id: "MinimumOverlapDisk", parent: "BottomExterior", state: "validation-only", transform: "identity" },
      { id: "RotatingCarrier", parent: "FixedAxisBoss", state: "user-authoritative", transform: `R(${angleDeg}deg)` },
      { id: "CarrierFollowerLeft", parent: "RotatingCarrier", state: "user-authoritative-role", transform: `R(${angleDeg}deg)` },
      { id: "CarrierFollowerRight", parent: "RotatingCarrier", state: "user-authoritative-role", transform: `R(${angleDeg}deg)` },
      { id: "BallCandidateLeft", parent: "RotatingCarrier", state: "range-only", transform: `R(${angleDeg}deg)` },
      { id: "BallCandidateRight", parent: "RotatingCarrier", state: "range-only", transform: `R(${angleDeg}deg)` },
      { id: "MovingTop", parent: null, state: "user-authoritative", transform: `R(${angleDeg}deg)*T_local(${boundedTravelL}L)` },
      ...grooveLocal.map((groove) => ({ id: groove.id, parent: "MovingTop", state: "user-authoritative", transform: `R(${angleDeg}deg)*T_local(${boundedTravelL}L)` })),
      { id: "UnknownSprings", parent: "RotatingCarrier", state: "unknown", transform: "metadata-only" },
      { id: "UnknownPreload", parent: "RotatingCarrier", state: "unknown", transform: "metadata-only" }
    ] : [
      { id: "BottomExterior", parent: null, state: "user-authoritative", transform: "identity" },
      { id: "FixedAxis", parent: "BottomExterior", state: "user-authoritative", transform: "identity" },
      { id: "MinimumOverlapDisk", parent: "BottomExterior", state: "user-authoritative", transform: "identity" },
      { id: "RotatingCarrier", parent: "BottomExterior", state: "user-authoritative", transform: `R(${angleDeg}deg)` },
      { id: "CarrierFollowerLeft", parent: "RotatingCarrier", state: "unknown", transform: `R(${angleDeg}deg)` },
      { id: "CarrierFollowerRight", parent: "RotatingCarrier", state: "unknown", transform: `R(${angleDeg}deg)` },
      { id: "TopPlate", parent: null, state: "user-authoritative", transform: `R(${angleDeg}deg)*T_local(${boundedTravelL}L)` },
      { id: "TopGrooveLeft", parent: "TopPlate", state: "user-authoritative", transform: `R(${angleDeg}deg)*T_local(${boundedTravelL}L)` },
      { id: "TopGrooveRight", parent: "TopPlate", state: "user-authoritative", transform: `R(${angleDeg}deg)*T_local(${boundedTravelL}L)` },
      { id: "UnknownContacts", parent: "TopPlate", state: "unknown", transform: "candidate-dashed" }
    ]
  };
}

export function computeCadSweepEnvelope(config) {
  if (!config) throw new Error("Sweep envelope requires contract-derived CAD config.");
  const samples = [];
  for (let detentIndex = 0; detentIndex < config.detentCount; detentIndex += 1) {
    const angleDeg = detentIndex * config.detentStepDeg;
    const legalSlideFractions = !config.endpointRotationOnly || detentIndex === 0
      ? config.sweepSlideSampleFractions
      : [1];
    for (const slideFraction of legalSlideFractions) {
      const travelL = config.maxTravelL * slideFraction;
      const geometry = computeCadGeometry({ travelL, angleDeg }, config);
      samples.push({
        detentIndex,
        angleDeg,
        slideFraction,
        travelL,
        followerEngaged: geometry.followers.engaged,
        axisCovered: geometry.coverage.axisCovered,
        topAboveBottom: geometry.layerOrder.topAboveBottom,
        bottomMasksTop: geometry.layerOrder.bottomMasksTop,
        endpointInterlockLegal: geometry.interlock.legalPose,
        legalOverhang: travelL > 0 || angleDeg !== 0,
        valid: geometry.followers.engaged
          && geometry.coverage.axisCovered
          && geometry.layerOrder.topAboveBottom
          && geometry.interlock.legalPose
          && !geometry.layerOrder.bottomMasksTop
      });
    }
  }
  return {
    samples,
    sampleCount: samples.length,
    invalidSamples: samples.filter((sample) => !sample.valid),
    allValid: samples.every((sample) => sample.valid),
    topZ: config.topZ,
    bottomZ: config.bottomZ,
    bottomMasksTop: false
  };
}

export function computeMinimumOverlapContainmentSweep(config, {
  angleStepDeg = config.denseSweepDegrees || 1,
  slideFractions = config.sweepSlideSampleFractions || [0, 0.25, 0.5, 0.75, 1]
} = {}) {
  refreshCadTravelBounds(config);
  const samples = [];
  for (let angleDeg = 0; angleDeg < 360; angleDeg += angleStepDeg) {
    for (const slideFraction of slideFractions) {
      const travelL = config.maxTravelL * slideFraction;
      const geometry = computeCadGeometry({ travelL, angleDeg }, config);
      samples.push({
        angleDeg,
        slideFraction,
        travelL,
        marginL: geometry.minimumOverlapDisk.containment.marginL,
        valid: geometry.minimumOverlapDisk.fullyCovered,
        followerEngaged: geometry.followers.engaged,
        topAboveBottom: geometry.layerOrder.topAboveBottom
      });
    }
  }
  const boundary = minimumOverlapContainmentMargin(config.maxTravelL, config);
  const beyond = minimumOverlapContainmentMargin(config.maxTravelL + 1e-6, config);
  return {
    samples,
    sampleCount: samples.length,
    angleSampleCount: Math.ceil(360 / angleStepDeg),
    invalidSamples: samples.filter((sample) => !sample.valid),
    allValid: samples.every((sample) => sample.valid),
    analyticContinuous: true,
    angleInvariant: true,
    boundaryMarginL: boundary.bottomMarginL,
    exactBoundaryTangency: Math.abs(boundary.bottomMarginL) <= 1e-9,
    beyondBoundaryInvalid: beyond.marginL < -1e-9,
    minimumMarginL: Math.min(...samples.map((sample) => sample.marginL))
  };
}

export function topLocalPointFromWorld(point, geometry) {
  const unrotated = rotatePoint(point, geometry.axis.world, -geometry.top.angleDeg);
  return [
    unrotated[0] - geometry.top.localTranslation[0],
    unrotated[1] - geometry.top.localTranslation[1]
  ];
}

const shortestAngleDelta = (fromDeg, toDeg) => ((toDeg - fromDeg + 540) % 360) - 180;

export function topWorldPointFromLocal(localPoint, pose, config) {
  const geometry = computeCadGeometry(pose, config);
  return rotatePoint(
    [
      localPoint[0] + geometry.top.localTranslation[0],
      localPoint[1] + geometry.top.localTranslation[1]
    ],
    geometry.axis.world,
    pose.angleDeg
  );
}

export function solveDirectTopPose({
  pointer,
  grabbedLocalPoint,
  travelL,
  angleDeg,
  config
}) {
  let nextTravelL = clamp(Number(travelL) || 0, 0, config.maxTravelL);
  let nextAngleDeg = Number(angleDeg) || 0;
  const initialPoint = topWorldPointFromLocal(grabbedLocalPoint, {
    travelL: nextTravelL,
    angleDeg: nextAngleDeg
  }, config);
  const initialRadians = nextAngleDeg * Math.PI / 180;
  const outward = [Math.sin(initialRadians), -Math.cos(initialRadians)];
  const tangent = [Math.cos(initialRadians), Math.sin(initialRadians)];
  const pointerDelta = [pointer[0] - initialPoint[0], pointer[1] - initialPoint[1]];
  const requestedSlideDeltaL = (
    pointerDelta[0] * outward[0] + pointerDelta[1] * outward[1]
  ) / computeCadGeometry({ travelL: nextTravelL, angleDeg: nextAngleDeg }, config).upper.length;
  if (nextTravelL + requestedSlideDeltaL <= config.closedStopVectorTolerance && requestedSlideDeltaL < 0) {
    const tangentPixels = pointerDelta[0] * tangent[0] + pointerDelta[1] * tangent[1];
    const radius = Math.max(1, Math.hypot(
      initialPoint[0] - computeCadGeometry({}, config).axis.world[0],
      initialPoint[1] - computeCadGeometry({}, config).axis.world[1]
    ));
    nextAngleDeg += tangentPixels / radius * 180 / Math.PI;
    const normalizedAngleDeg = ((nextAngleDeg % 360) + 360) % 360;
    const solvedPoint = topWorldPointFromLocal(grabbedLocalPoint, {
      travelL: 0,
      angleDeg: normalizedAngleDeg
    }, config);
    return {
      nextTravelL: 0,
      nextAngleDeg: normalizedAngleDeg,
      residualPx: Math.hypot(pointer[0] - solvedPoint[0], pointer[1] - solvedPoint[1]),
      closedClamped: true,
      openClamped: false
    };
  }
  for (let iteration = 0; iteration < 8; iteration += 1) {
    const geometry = computeCadGeometry({ travelL: nextTravelL, angleDeg: nextAngleDeg }, config);
    const predicted = topWorldPointFromLocal(grabbedLocalPoint, {
      travelL: nextTravelL,
      angleDeg: nextAngleDeg
    }, config);
    const error = [pointer[0] - predicted[0], pointer[1] - predicted[1]];
    const radians = nextAngleDeg * Math.PI / 180;
    const slideJacobian = [
      Math.sin(radians) * geometry.upper.length,
      -Math.cos(radians) * geometry.upper.length
    ];
    const relative = [predicted[0] - geometry.axis.world[0], predicted[1] - geometry.axis.world[1]];
    const angleJacobian = [
      -relative[1] * Math.PI / 180,
      relative[0] * Math.PI / 180
    ];
    const determinant = slideJacobian[0] * angleJacobian[1] - angleJacobian[0] * slideJacobian[1];
    if (Math.abs(determinant) < 1e-8) break;
    const deltaTravel = (error[0] * angleJacobian[1] - angleJacobian[0] * error[1]) / determinant;
    const deltaAngle = (slideJacobian[0] * error[1] - error[0] * slideJacobian[1]) / determinant;
    nextTravelL = clamp(nextTravelL + deltaTravel, 0, config.maxTravelL);
    nextAngleDeg += deltaAngle;
    if (Math.hypot(error[0], error[1]) < 0.01) break;
  }
  const normalizedAngleDeg = ((nextAngleDeg % 360) + 360) % 360;
  const solvedPoint = topWorldPointFromLocal(grabbedLocalPoint, {
    travelL: nextTravelL,
    angleDeg: normalizedAngleDeg
  }, config);
  const finalRadians = normalizedAngleDeg * Math.PI / 180;
  const finalOutward = [Math.sin(finalRadians), -Math.cos(finalRadians)];
  const finalError = [pointer[0] - solvedPoint[0], pointer[1] - solvedPoint[1]];
  const closedClamped = nextTravelL <= config.closedStopVectorTolerance
    && finalError[0] * finalOutward[0] + finalError[1] * finalOutward[1] < -config.closedStopVectorTolerance;
  const openClamped = nextTravelL >= config.maxTravelL - config.closedStopVectorTolerance
    && finalError[0] * finalOutward[0] + finalError[1] * finalOutward[1] > config.closedStopVectorTolerance;
  return {
    nextTravelL,
    nextAngleDeg: normalizedAngleDeg,
    residualPx: Math.hypot(pointer[0] - solvedPoint[0], pointer[1] - solvedPoint[1]),
    closedClamped,
    openClamped
  };
}

export function solveCompoundDragDelta({
  previousPointer,
  currentPointer,
  travelL,
  angleDeg,
  grabbedLocalPoint = null,
  config
}) {
  const previousGeometry = computeCadGeometry({ travelL, angleDeg }, config);
  const localPoint = grabbedLocalPoint || topLocalPointFromWorld(previousPointer, previousGeometry);
  const solved = solveDirectTopPose({
    pointer: currentPointer,
    grabbedLocalPoint: localPoint,
    travelL,
    angleDeg,
    config
  });
  return {
    slideDeltaL: solved.nextTravelL - travelL,
    angleDeltaDeg: shortestAngleDelta(angleDeg, solved.nextAngleDeg),
    grabbedLocalPoint: localPoint,
    nextTravelL: solved.nextTravelL,
    nextAngleDeg: solved.nextAngleDeg,
    residualPx: solved.residualPx,
    closedClamped: solved.closedClamped,
    openClamped: solved.openClamped
  };
}

export function derivePhysicalDimensions(values = {}) {
  const inputs = Object.fromEntries(PHYSICAL_FIELDS.map((field) => [
    field.id,
    positiveNumber(values[field.id])
  ]));
  const derived = {};
  if (inputs.overallLength && inputs.overallWidth) {
    derived.aspectRatioLW = {
      value: inputs.overallLength / inputs.overallWidth,
      unit: "L/W",
      status: "user"
    };
  }
  if (inputs.totalThickness && inputs.upperThickness && inputs.lowerThickness && inputs.closedGap) {
    derived.stackResidual = {
      value: inputs.totalThickness - inputs.upperThickness - inputs.lowerThickness - inputs.closedGap,
      unit: "mm",
      status: "user"
    };
  }
  if (inputs.maxTravelMm && inputs.overallLength) {
    derived.travelL = {
      value: inputs.maxTravelMm / inputs.overallLength,
      unit: "L",
      status: "user"
    };
  }
  if (inputs.overallWidth && inputs.railSpacing && inputs.railWidth) {
    derived.railEdgeClearance = {
      value: (inputs.overallWidth - inputs.railSpacing - inputs.railWidth) / 2,
      unit: "mm",
      status: "user"
    };
  }
  return { inputs, derived };
}

export function displayDimension(value, unit = "mm", status = "unknown") {
  if (!Number.isFinite(value)) return `? ${unit} · ${CAD_STATUS.unknown}`;
  const precision = Math.abs(value) < 1 ? 3 : 2;
  return `${value.toFixed(precision)} ${unit} · ${CAD_STATUS[status] || CAD_STATUS.unknown}`;
}

export function createCadViewport(overrides = {}) {
  return {
    zoom: clamp(Number(overrides.zoom) || 1, 0.6, 2.5),
    panX: Number(overrides.panX) || 0,
    panY: Number(overrides.panY) || 0
  };
}

export function zoomCadViewport(viewport, factor, anchor = [500, 350]) {
  const nextZoom = clamp(viewport.zoom * factor, 0.6, 2.5);
  const ratio = nextZoom / viewport.zoom;
  return {
    zoom: nextZoom,
    panX: anchor[0] - (anchor[0] - viewport.panX) * ratio,
    panY: anchor[1] - (anchor[1] - viewport.panY) * ratio
  };
}

export function panCadViewport(viewport, dx, dy) {
  return { ...viewport, panX: viewport.panX + dx, panY: viewport.panY + dy };
}

export function cadViewportTransform(viewport) {
  return `translate(${viewport.panX} ${viewport.panY}) scale(${viewport.zoom})`;
}

export function inverseCadPoint(point, viewport) {
  return [
    (point[0] - viewport.panX) / viewport.zoom,
    (point[1] - viewport.panY) / viewport.zoom
  ];
}
