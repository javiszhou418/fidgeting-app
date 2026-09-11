import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import test from "node:test";
import { loadManifest, resolveRepoPath } from "../pipeline-core.mjs";

test("Gate 08 rev 4 remains immutable history under rev 5", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  assert.ok(manifest.revision >= 213);
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(
    manifest.currentState.visualApproval,
    "gate12-r004-variant-b-approved-review-ui",
  );
  assert.equal(manifest.currentState.shippingAssetUnchanged, false);
  assert.equal(manifest.stages[7].lightingSpec.revision, 6);
  const rev4 = manifest.stages[7].historicalRevisions.find(
    (revision) => revision.evidenceRevision === 4,
  );
  assert.ok(rev4);
  const spec = rev4.lightingSpec;
  assert.equal(spec.revision, 4);
  assert.equal(spec.portableRecipe.reflectionSourceCount, 1);
  assert.equal(spec.portableRecipe.directLightCount, 0);
  assert.equal(spec.portableRecipe.groundCount, 0);
  assert.equal(spec.parityAudit.environment.nonzeroRgb, true);
  assert.equal(spec.parityAudit.environment.unitySourceTextureFormat, "R16G16B16A16_SFloat");
  assert.equal(spec.parityAudit.alignmentPolicy.independentCropping, false);
  assert.equal(spec.parityAudit.humanVisualGate.reviewable, true);
  assert.equal(spec.parityAudit.humanVisualGate.approved, false);
  assert.equal(spec.deliveryState.buildInstallPhone, false);
  assert.equal(spec.motionInvariant.movingTop.yawAxis, "+Z only");
  assert.equal(spec.motionInvariant.negativeScaleOrInversion, false);
  assert.equal(
    spec.interactiveReviewArtifactId,
    "magnetic-slide-tile-lighting-corrected-synchronized-preview-r004",
  );
  const rev3 = manifest.stages[7].historicalRevisions.find(
    (revision) => revision.evidenceRevision === 3,
  );
  assert.equal(rev3.status, "superseded-not-visually-acceptable");
  assert.equal(rev3.preservedForHistory, true);
  const rejectedPreview = manifest.stages[7].historicalRevisions.find(
    (revision) => revision.evidenceRevision === "4-invalid-preview-attempt-1",
  );
  assert.equal(
    rejectedPreview.status,
    "rejected-internal-impossible-vertical-flip",
  );
  assert.deepEqual(rejectedPreview.reviewArtifactIds, []);
  const videoAsset = manifest.assets.find(
    (asset) =>
      asset.id
      === "magnetic-slide-tile-lighting-corrected-synchronized-preview-r004",
  );
  const videoBytes = fs.readFileSync(resolveRepoPath(videoAsset.path));
  assert.equal(
    crypto.createHash("sha256").update(videoBytes).digest("hex"),
    videoAsset.sha256,
  );
  const report = spec.correctedRecording;
  assert.equal(report.video.durationSeconds, 12);
  assert.equal(report.video.frameCount, 360);
  assert.equal(report.alignment.transformValidatorsPassedEveryFrame, true);
  assert.equal(report.alignment.minimumSilhouetteIoU > 0.999, true);
  assert.equal(report.state.gate08, "blocked-pending-corrected-visual-review");
});

test("portable review evidence remains full-frame and parity-blocked", () => {
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-003/portability-root-cause-report.json",
  )));
  assert.deepEqual(report.alignmentPolicy.resolution, [1400, 1100]);
  assert.equal(report.fullFrame.ssim > 0.78, true);
  assert.equal(report.fullFrame.heatmapAreaFractionOver24 < 0.03, true);
  assert.equal(report.fullFrame.regionalDeltaE76.object.median, 3);
  assert.equal(report.checks.visualParityReady, false);
  assert.equal(report.checks.renewedGate08ReviewRequired, true);
  assert.equal(report.checks.shippingUntouched, true);
});
