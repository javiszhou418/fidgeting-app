import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../../..");
const evidence = path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-009",
);
const manifest = JSON.parse(fs.readFileSync(path.join(
  root,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
)));
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
const build = JSON.parse(fs.readFileSync(path.join(evidence, "environment-build-validation.json")));
const blender = JSON.parse(fs.readFileSync(path.join(evidence, "blender-environment-audit.json")));
const images = JSON.parse(fs.readFileSync(path.join(evidence, "image-environment-audit.json")));
const motion = JSON.parse(fs.readFileSync(path.join(evidence, "environment-turntable-validation.json")));
const portability = JSON.parse(fs.readFileSync(path.join(evidence, "portability-validation.json")));

test("persists the exact Gate 08 rev 6 approval", () => {
  assert.equal(gate08.status, "approved");
  assert.equal(gate08.lightingSpec.revision, 6);
  assert.equal(gate08.decision.action, "approve");
  assert.equal(gate08.decision.notes, "你开始吧");
});

test("uses current geometry material lighting and contract hashes", () => {
  assert.equal(gate09.environmentSpec.revision, 9);
  assert.equal(
    build.source.geometryDigest,
    "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
  );
  assert.equal(
    build.source.materialSha256,
    "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c",
  );
  assert.equal(
    build.source.sha256,
    "897484bd6e740454ee23c6a891eb8faa2fdf48af543792f08c3f4b78ff8780fe",
  );
  assert.equal(
    build.source.mechanismContractSha256,
    "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  );
});

test("changes only the environment input in matched pairs", () => {
  assert.equal(build.pass, true);
  assert.equal(build.checks.sourceSnapshotIdentical, true);
  assert.equal(build.checks.matchedPairState, true);
  for (const pair of Object.values(build.pairs)) {
    assert.equal(pair.stateIdentical, true);
    assert.notEqual(pair.neutral.environmentSha256, pair.target.environmentSha256);
  }
  assert.equal(images.checks.pairDimensions, true);
  assert.equal(images.checks.pairSilhouetteBbox, true);
  assert.equal(images.checks.environmentDifferenceVisible, true);
});

test("provides revalidated seamless HDR and Unity cubemap", () => {
  assert.equal(build.neutral.revalidatedFromCurrentGate08, true);
  assert.equal(build.neutral.nonzeroRgbFraction, 1);
  assert.equal(build.neutral.seamMaximumLinearDelta, 0);
  assert.equal(build.target.nonzeroRgbFraction, 1);
  assert.equal(build.target.seamMaximumLinearDelta, 0);
  assert.ok(build.target.dynamicRangeStopsP01P99 >= 4);
  assert.equal(Object.keys(build.cubemap.faces).length, 6);
  assert.ok(build.cubemap.brightestDirectionAngularErrorDegrees <= 1);
  assert.equal(blender.checks.cubemapFaceHashes, true);
  assert.equal(blender.checks.cubemapRgbNonzero, true);
});

test("preserves top side rim and underside partitions", () => {
  assert.equal(blender.pass, true);
  assert.equal(blender.checks.glbPartitions, true);
  assert.equal(blender.checks.glbClampNoWrap, true);
  for (const object of Object.values(blender.glb.importedObjects)) {
    assert.equal(object.sideArtworkTriangles, 0);
    assert.equal(object.undersideArtworkTriangles, 0);
    assert.ok(object.zoneTriangleCounts.topArtwork > 0);
    assert.ok(object.zoneTriangleCounts.polishedSilverRim > 0);
  }
  assert.equal(images.checks.bloodRedVisible, true);
  assert.equal(images.checks.darkSideVisible, true);
  assert.equal(images.checks.silverRimVisible, true);
  assert.equal(images.checks.clippingBounded, true);
});

test("records legal endpoint motion in both environments", () => {
  assert.equal(motion.pass, true);
  assert.equal(motion.sourceFrameCountPerEnvironment, 60);
  assert.equal(motion.checks.rotationOnlyAtEndpoint, true);
  assert.equal(motion.checks.returnOnlyAligned, true);
  assert.equal(motion.checks.full360, true);
  assert.equal(motion.checks.fixedAxisInvariant, true);
  assert.equal(motion.checks.noFlip, true);
  assert.equal(motion.checks.noProxy, true);
});

test("locks the downstream Unity portability contract", () => {
  assert.equal(portability.pass, true);
  assert.match(portability.contractSha256, /^[0-9a-f]{64}$/);
  for (const value of Object.values(portability.checks)) assert.equal(value, true);
});

test("preserves Gate 09 approval through Gate 12 review", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate09.status, "approved");
  assert.equal(gate09.decision.notes, "继续");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(gate09.environmentSpec.deliveryState.simulatorUsed, false);
  assert.equal(gate09.environmentSpec.deliveryState.unityUsed, false);
  assert.equal(gate09.environmentSpec.deliveryState.shippingSceneModified, false);
  assert.equal(gate09.environmentSpec.deliveryState.buildInstallPhone, false);
});
