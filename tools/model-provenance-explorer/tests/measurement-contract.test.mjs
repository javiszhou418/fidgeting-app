import assert from "node:assert/strict";
import test from "node:test";
import {
  MANUFACTURING_LATER_FIELDS,
  MEASUREMENT_BASIS_TYPES,
  OPTIONAL_ENGINEERING_MEASUREMENTS,
  REQUIRED_CORE_MEASUREMENTS,
  validateMeasurementContract
} from "../measurement-contract-core.mjs";

const measured = (valueMm, uncertaintyMm = 0.1, source = "卡尺") => ({
  valueMm,
  uncertaintyMm,
  source,
  method: "controlled orthogonal measurement"
});

const validRequired = () => ({
  closedOverallLength: measured(60, 0.2),
  overallWidth: measured(38, 0.2),
  totalClosedThickness: measured(9.5, 0.2),
  topPlateThickness: measured(4.5, 0.1),
  bottomPlateThickness: measured(4.7, 0.1),
  maximumSlideTravel: measured(20, 0.2),
  fixedAxisOffsetFromNearestEnd: measured(12, 0.1),
  rotatingCarrierDiameter: measured(20, 0.1),
  closedSeamGap: measured(0.3, 0.05)
});

test("defines exactly nine required core measurements", () => {
  assert.equal(REQUIRED_CORE_MEASUREMENTS.length, 9);
  assert.deepEqual(REQUIRED_CORE_MEASUREMENTS.map(({ id }) => id), [
    "closedOverallLength",
    "overallWidth",
    "totalClosedThickness",
    "topPlateThickness",
    "bottomPlateThickness",
    "maximumSlideTravel",
    "fixedAxisOffsetFromNearestEnd",
    "rotatingCarrierDiameter",
    "closedSeamGap"
  ]);
});

test("keeps optional and manufacturing-only fields nonblocking", () => {
  assert.equal(OPTIONAL_ENGINEERING_MEASUREMENTS.length, 7);
  assert.deepEqual(MANUFACTURING_LATER_FIELDS.map(({ id }) => id), [
    "operatingClearance",
    "manufacturingAllowance",
    "manufacturingTolerance"
  ]);
  const result = validateMeasurementContract({
    requiredMeasurements: validRequired(),
    optionalMeasurements: {},
    cadConfig: { actualSMaxL: 0.3615286624203821 }
  });
  assert.equal(result.readyForModelingContractReview, true);
  assert.ok(Object.values(result.optionalMeasurements).every(({ valueMm }) => valueMm === null));
  assert.ok(Object.values(result.manufacturingMeasurements).every(({ blocking }) => blocking === false));
});

test("blocks a thickness stack outside stated uncertainty", () => {
  const required = validRequired();
  required.totalClosedThickness = measured(12, 0.05);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    cadConfig: { actualSMaxL: 0.3615286624203821 }
  });
  assert.equal(result.readyForModelingContractReview, false);
  assert.ok(result.errors.some(({ id }) => id === "thickness-stack"));
});

test("blocks carrier geometry that cannot fit the bottom footprint", () => {
  const required = validRequired();
  required.rotatingCarrierDiameter = measured(42);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    cadConfig: { actualSMaxL: 0.3615286624203821 }
  });
  assert.ok(result.errors.some(({ id }) => id === "axis-carrier-fit"));
});

test("blocks travel beyond the approved finite-groove and overlap limit", () => {
  const required = validRequired();
  required.maximumSlideTravel = measured(25, 0.1);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    cadConfig: { actualSMaxL: 0.3615286624203821 }
  });
  assert.ok(result.errors.some(({ id }) => id === "travel-containment"));
});

test("treats video aspect as a warning instead of overriding measurements", () => {
  const required = validRequired();
  required.overallWidth = measured(30);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    cadConfig: { actualSMaxL: 0.5 }
  });
  assert.equal(result.requiredMeasurements.overallWidth.valueMm, 30);
  assert.ok(result.warnings.some(({ id }) => id === "video-aspect"));
});

test("requires value uncertainty source and method for each core field", () => {
  const required = validRequired();
  required.closedSeamGap = { valueMm: 0.3, source: "卡尺" };
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    cadConfig: { actualSMaxL: 0.3615286624203821 }
  });
  assert.equal(result.progress.complete, 8);
  assert.deepEqual(result.fieldErrors.closedSeamGap, ["缺少不确定度", "缺少测量方法"]);
});

test("persists an explicit unknown without treating it as a completed measurement", () => {
  const required = validRequired();
  required.rotatingCarrierDiameter = {
    state: "unknown",
    unknown: true,
    valueMm: 99,
    uncertaintyMm: 1,
    source: "用户提供",
    method: "当前无法看到内部载体"
  };
  const result = validateMeasurementContract({ requiredMeasurements: required });
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.state, "unknown");
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.unknown, true);
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.valueMm, null);
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.uncertaintyMm, null);
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.source, null);
  assert.equal(result.requiredMeasurements.rotatingCarrierDiameter.method, "当前无法看到内部载体");
  assert.deepEqual(result.fieldErrors.rotatingCarrierDiameter, ["当前不知道"]);
  assert.equal(result.progress.complete, 8);
  assert.equal(result.readyForModelingContractReview, false);
});

test("accepts user-provided as a measurement source", () => {
  const required = validRequired();
  required.closedOverallLength.source = "用户提供";
  const result = validateMeasurementContract({ requiredMeasurements: required });
  assert.equal(result.requiredMeasurements.closedOverallLength.source, "用户提供");
  assert.equal(result.fieldErrors.closedOverallLength, undefined);
});

const strictSourceAssets = () => ([
  {
    id: "same-model-official-spec",
    sha256: "a".repeat(64),
    exists: true,
    current: true,
    contentClass: "same-model-official-spec"
  },
  {
    id: "same-model-public-teardown",
    sha256: "b".repeat(64),
    exists: true,
    current: true,
    contentClass: "same-model-public-teardown-image"
  }
]);

function official(valueMm, uncertaintyMm = 0.1) {
  return {
    valueMm,
    uncertaintyMm,
    source: "同款正式规格",
    basisType: MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec,
    sourceAssetIds: ["same-model-official-spec"],
    method: "从同款厂商正式规格表逐项抄录"
  };
}

function calibrated(valueMm, targetPixelSpan, uncertaintyMm = 0.1) {
  return {
    valueMm,
    uncertaintyMm,
    source: "同款公开拆解校准",
    basisType: MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration,
    sourceAssetIds: ["same-model-official-spec", "same-model-public-teardown"],
    method: "在同一张正交拆解图中，以正式总长为锚点换算目标像素跨度",
    calibration: {
      anchorFieldId: "closedOverallLength",
      anchorOfficialValueMm: 60,
      imagePixelSpan: 600,
      targetPixelSpan
    }
  };
}

test("accepts hash-linked same-model official specs and auditable teardown calibration", () => {
  const required = validRequired();
  required.closedOverallLength = official(60, 0.1);
  required.topPlateThickness = calibrated(4.5, 45, 0.05);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    sourceAssets: strictSourceAssets(),
    strictProvenance: true
  });
  assert.equal(result.readyForModelingContractReview, true);
  assert.equal(result.fieldErrors.closedOverallLength, undefined);
  assert.equal(result.fieldErrors.topPlateThickness, undefined);
  assert.equal(result.requiredMeasurements.topPlateThickness.calibration.scaleMmPerPixel, 0.1);
  assert.equal(result.requiredMeasurements.topPlateThickness.calibration.derivedValueMm, 4.5);
});

test("strict non-user dimensions require an explicit basis and current hashed source", () => {
  const required = validRequired();
  required.closedOverallLength = {
    ...official(60),
    basisType: undefined
  };
  const sources = strictSourceAssets();
  sources[0].current = false;
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    sourceAssets: sources,
    strictProvenance: true
  });
  assert.match(result.fieldErrors.closedOverallLength.join(" "), /basisType/);
  assert.match(result.fieldErrors.closedOverallLength.join(" "), /过期/);
  assert.equal(result.readyForModelingContractReview, false);
});

test("calibrated targets must reproduce the stated ratio within uncertainty", () => {
  const required = validRequired();
  required.closedOverallLength = official(60);
  required.topPlateThickness = calibrated(5.2, 45, 0.05);
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    sourceAssets: strictSourceAssets(),
    strictProvenance: true
  });
  assert.match(result.fieldErrors.topPlateThickness.join(" "), /4\.500 mm/);
  assert.equal(result.readyForModelingContractReview, false);
});

test("non-user dimensions cannot masquerade as measured or manufacturing dimensions", () => {
  const required = validRequired();
  required.closedOverallLength = { ...official(60), measured: true, manufacturingDimension: true };
  const result = validateMeasurementContract({
    requiredMeasurements: required,
    sourceAssets: strictSourceAssets(),
    strictProvenance: true
  });
  assert.match(result.fieldErrors.closedOverallLength.join(" "), /不得标为实测/);
});

test("strict provenance rejects the legacy generic estimate source", () => {
  const required = validRequired();
  required.topPlateThickness = measured(4.5, 0.1, "估算");
  const result = validateMeasurementContract({ requiredMeasurements: required, strictProvenance: true });
  assert.match(result.fieldErrors.topPlateThickness.join(" "), /泛化估算/);
});
