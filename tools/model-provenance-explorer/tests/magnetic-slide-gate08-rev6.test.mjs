import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../../..");
const evidence = path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-006",
);
const manifest = JSON.parse(fs.readFileSync(path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
)));
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const blender = JSON.parse(fs.readFileSync(path.join(evidence, "blender-lighting-report.json")));
const audit = JSON.parse(fs.readFileSync(path.join(evidence, "lighting-material-audit.json")));
const motion = JSON.parse(fs.readFileSync(path.join(evidence, "legal-lighting-turntable-report.json")));

test("persists the exact Gate 07 rev 13 approval", () => {
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.materialSpec.revision, 13);
  assert.equal(gate07.decision.notes, "通过");
  assert.equal(gate07.decision.action, "approve");
});

test("uses only the approved corrected material source", () => {
  assert.equal(gate08.status, "approved");
  assert.equal(gate08.lightingSpec.revision, 6);
  assert.equal(gate08.lightingSpec.sourceMaterialRevision, 13);
  assert.equal(
    gate08.lightingSpec.sourceMaterialSha256,
    "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c",
  );
  assert.equal(
    gate08.lightingSpec.geometryDigest,
    "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
  );
});

test("keeps every diagnostic pass non-destructive", () => {
  assert.equal(blender.pass, true);
  assert.equal(blender.sourceMeshDataElementIdentical, true);
  assert.equal(blender.checks.materialSlotsIdentical, true);
  assert.equal(blender.checks.polygonMaterialIndicesByteIdentical, true);
  assert.equal(blender.checks.uvsByteIdentical, true);
  assert.equal(blender.checks.geometryUnchanged, true);
  for (const result of Object.values(blender.diagnosticPasses)) {
    assert.equal(result.duplicateScene, true);
    assert.equal(result.duplicateMeshData, true);
    assert.equal(result.sourceUnchanged, true);
  }
});

test("preserves cap side rim and underside partitions", () => {
  assert.equal(audit.pass, true);
  assert.equal(audit.checks.glbPartitions, true);
  assert.equal(audit.checks.glbClampNoWrap, true);
  for (const object of Object.values(audit.importedGlb)) {
    assert.equal(object.sideArtworkTriangles, 0);
    assert.equal(object.undersideArtworkTriangles, 0);
    assert.ok(object.zoneTriangleCounts.topArtwork > 0);
    assert.ok(object.zoneTriangleCounts.polishedSilverRim > 0);
  }
});

test("reuses the portable shared HDR and valid cameras", () => {
  assert.equal(audit.checks.sharedHdrCurrent, true);
  assert.equal(
    audit.sourceHashes.environment,
    "a5b310c8c7fc17bda4110adb80e68913f1b5d623ffe01d935574813b80d1a872",
  );
  assert.equal(audit.checks.cameraClippingValid, true);
  assert.equal(audit.checks.standardViewsClippingBounded, true);
  assert.equal(audit.checks.closeupSpecularClippingBounded, true);
});

test("records only legal endpoint motion", () => {
  assert.equal(motion.pass, true);
  assert.equal(motion.frameCount, 90);
  assert.equal(motion.checks.allFramesPartitionValidated, true);
  assert.equal(motion.checks.allFramesSourceSnapshotIdentical, true);
  assert.equal(motion.checks.rotationOnlyAtEndpoint, true);
  assert.equal(motion.checks.slideReturnOnlyAligned, true);
  assert.equal(motion.checks.full360Covered, true);
  assert.equal(motion.checks.fixedAxisInvariant, true);
  assert.equal(motion.checks.noPitchRollFlip, true);
  assert.equal(motion.checks.approvedNoPenetrationAudit, true);
});

test("preserves Gate 08 approval through Gate 12 review", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate08.decision.notes, "你开始吧");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(gate08.lightingSpec.deliveryState.simulatorUsed, false);
  assert.equal(gate08.lightingSpec.deliveryState.unityUsed, false);
  assert.equal(gate08.lightingSpec.deliveryState.shippingSceneModified, false);
  assert.equal(gate08.lightingSpec.deliveryState.buildInstallPhone, false);
});
