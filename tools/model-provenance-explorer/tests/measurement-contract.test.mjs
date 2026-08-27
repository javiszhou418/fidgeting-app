import assert from "node:assert/strict";
import test from "node:test";
import {
  MANUFACTURING_LATER_FIELDS,
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
