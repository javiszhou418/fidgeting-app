import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const root = path.resolve(import.meta.dirname, "../../..");
const pipeline = JSON.parse(fs.readFileSync(path.join(root, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json"), "utf8"));
const evidence = path.join(root, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012");

test("Gate 05 rev 12 returns to one fixed pivot", () => {
  const gate05 = pipeline.stages.find(stage => stage.id === "05-blockout");
  assert.equal(pipeline.currentStageId, "12-shipping");
  assert.equal(gate05.revision, 12);
  assert.equal(gate05.status, "approved");
  assert.equal(gate05.blockoutSpec.exactlyOnePivotId, "FixedAxis");
  assert.deepEqual(gate05.blockoutSpec.productRendererWhitelist, ["BottomExterior", "MovingTopBody"]);
  assert.match(gate05.blockoutSpec.correctedTransform, /T\(P\).*Rz\(theta\).*T\(-q\(s\)\)/);
  assert.equal(gate05.blockoutSpec.finalMaterialsApplied, false);
  assert.equal(gate05.blockoutSpec.fullRotationReview.decisionState, "rejected-invalid-partial-slide-rotation");
  assert.equal(gate05.blockoutSpec.endpointInterlockReview.exactUserWording, "上片只有在推到顶部的时候，才可以进行360度旋转");
  assert.equal(gate05.blockoutSpec.endpointInterlockReview.sourceGeometryChanged, false);
  assert.equal(pipeline.stages[6].status, "approved");
  assert.equal(pipeline.stages[7].status, "approved");
  assert.equal(pipeline.stages[8].status, "approved");
  assert.equal(pipeline.stages[9].status, "approved");
  assert.equal(pipeline.stages[10].status, "approved");
  assert.equal(pipeline.stages[11].status, "approved");
});

test("dense Blender and Unity motion validations pass", () => {
  const geometry = JSON.parse(fs.readFileSync(path.join(evidence, "geometry-validation.json"), "utf8"));
  const motion = JSON.parse(fs.readFileSync(path.join(evidence, "unity-preview/motion-video-validation.json"), "utf8"));
  const fullMotion = JSON.parse(fs.readFileSync(path.join(evidence, "unity-preview/full-rotation-video-validation.json"), "utf8"));
  const endpointMotion = JSON.parse(fs.readFileSync(path.join(evidence, "unity-preview/endpoint-interlock-video-validation.json"), "utf8"));
  assert.equal(geometry.pass, true);
  assert.equal(geometry.denseValidation.samples, 13357);
  assert.equal(geometry.denseValidation.maxPivotVarianceMm, 0);
  assert.ok(geometry.denseValidation.maxResidualMm <= 1e-6);
  assert.equal(geometry.bottomTopPlaneDeviationMm, 0);
  assert.deepEqual(geometry.pivotObjects, ["FixedAxis"]);
  assert.equal(motion.pass, true);
  assert.equal(motion.frameCount, 300);
  assert.equal(motion.unityTransformValidation.fixedPivotVarianceMeters, 0);
  assert.ok(motion.unityTransformValidation.constraintResidualMeters <= 1e-7);
  assert.deepEqual(motion.unityTransformValidation.rendererWhitelist, ["BottomExterior", "MovingTopBody"]);
  assert.equal(fullMotion.pass, true);
  assert.equal(fullMotion.frameCount, 570);
  assert.equal(fullMotion.video.codec, "h264");
  assert.equal(fullMotion.video.width, 1920);
  assert.equal(fullMotion.video.height, 1080);
  assert.equal(fullMotion.video.frames, 570);
  assert.equal(fullMotion.video.durationSeconds, 19);
  assert.deepEqual(fullMotion.unityTransformValidation.visitedDetentIndices, Array.from({ length: 30 }, (_, index) => index));
  assert.equal(fullMotion.unityTransformValidation.partialRevolution.endUnwrappedDegrees, 360);
  assert.equal(fullMotion.unityTransformValidation.maximumRevolution.endUnwrappedDegrees, 360);
  assert.equal(fullMotion.unityTransformValidation.containmentRayMisses, 0);
  assert.equal(fullMotion.unityTransformValidation.finalOrientationClosureDegrees, 0);
  assert.equal(fullMotion.quickTime.videoSampleCount, 570);
  assert.equal(endpointMotion.pass, true);
  assert.equal(endpointMotion.frameCount, 450);
  assert.equal(endpointMotion.video.durationSeconds, 15);
  assert.equal(endpointMotion.checks.rotationBlockedBelowMaximum, true);
  assert.equal(endpointMotion.checks.rotationOnlyAtMaximum, true);
  assert.equal(endpointMotion.checks.slideBlockedWhileNonzero, true);
  assert.equal(endpointMotion.checks.noSimultaneousVelocities, true);
  assert.equal(endpointMotion.quickTime.videoSampleCount, 450);
});

test("rejection evidence and plain geometry review remain registered", () => {
  const rejection = JSON.parse(fs.readFileSync(path.join(evidence, "user-rejection-evidence.json"), "utf8"));
  assert.equal(rejection.earliestAffectedGate, "05-blockout");
  assert.equal(rejection.files.length, 2);
  const app = fs.readFileSync(path.join(root, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 05 rev 12 · 最大端点旋转互锁复核/);
  assert.match(app, /30 × 12° 卡位/);
  const bible = fs.readFileSync(path.join(root, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  assert.match(bible, /FDB-SLD-057/);
  assert.match(bible, /FDB-SLD-058/);
  assert.match(bible, /FDB-SLD-059/);
  assert.match(bible, /上片只有在推到顶部的时候，才可以进行360度旋转/);
  const status = fs.readFileSync(path.join(root, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  assert.match(status, /Gate 05 rev 12 固定轴／遮挡纠正/);
  const priorVideo = pipeline.assets.find(asset => asset.id === "magnetic-slide-g05-r012-unity-video");
  assert.equal(priorVideo.provenance.evidenceStatus, "valid-partial-evidence-superseded-for-full-rotation-approval");
  const rejectedVideo = pipeline.assets.find(asset => asset.id === "magnetic-slide-g05-r012-unity-full360-video");
  assert.equal(rejectedVideo.provenance.evidenceStatus, "rejected-invalid-partial-slide-rotation");
  assert.equal(pipeline.stages[4].reviewArtifactIds[0], "magnetic-slide-g05-r012-endpoint-interlock-video");
});

