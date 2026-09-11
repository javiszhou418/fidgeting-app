import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../../..");
const manifest = JSON.parse(fs.readFileSync(path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
)));
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate08Rev5 = gate08.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 5,
);
const gate07Rev12 = gate07.historicalRevisions.find(
  (revision) => revision.revision === 12,
);
const audit = JSON.parse(fs.readFileSync(path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005/lighting-parity-audit.json",
)));
const motion = JSON.parse(fs.readFileSync(path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005/legal-lighting-turntable-report.json",
)));

test("persists Gate 07 rev 12 approval wording as history", () => {
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.materialSpec.revision, 13);
  assert.equal(gate07Rev12.decision.notes, "继续");
});

test("preserves Gate 08 rev 5 as stale evidence", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate08.status, "approved");
  assert.equal(gate08Rev5.status, "invalidated");
  assert.equal(gate08Rev5.lightingSpec.revision, 5);
  assert.equal(gate08Rev5.lightingSpec.sourceMaterialRevision, 12);
  assert.equal(gate08Rev5.lightingSpec.sourceMaterialSha256, "953929045453e1d9c3bb46612da85a70eb1a078a115a103040778d2703988588");
  assert.equal(gate08Rev5.lightingSpec.geometryDigest, "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952");
  assert.equal(gate08Rev5.lightingSpec.mechanismContractSha256, "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571");
});

test("preserves the shared HDR and measures full-frame parity", () => {
  assert.equal(audit.pass, true);
  assert.equal(audit.checks.sharedEnvironment, true);
  assert.equal(audit.checks.sharedDisplay, true);
  assert.equal(audit.checks.unityHdrHalf, true);
  assert.ok(audit.parity.ssim > 0.9);
  assert.ok(audit.parity.alignment.intersectionOverUnion > 0.85);
  assert.equal(audit.parity.independentCropping, false);
  assert.equal(audit.parity.postAlignment, false);
});

test("records only legal endpoint motion", () => {
  assert.equal(motion.pass, true);
  assert.equal(motion.frameCount, 90);
  assert.equal(motion.checks.rotationOnlyAtEndpoint, true);
  assert.equal(motion.checks.slideReturnOnlyAligned, true);
  assert.equal(motion.checks.full360Covered, true);
  assert.equal(motion.maximumFixedAxisVarianceMm, 0);
  assert.equal(motion.maximumPitchRollRadians, 0);
});

test("preserves downstream approvals after environment review", () => {
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(gate08.lightingSpec.deliveryState.shippingSceneModified, false);
  assert.equal(gate08.lightingSpec.deliveryState.buildInstallPhone, false);
});
