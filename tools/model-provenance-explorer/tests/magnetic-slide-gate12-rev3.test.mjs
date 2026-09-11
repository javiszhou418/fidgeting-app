import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import {
  loadManifest,
  repoRoot,
  sha256File,
} from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const approvedRev3 = gate12.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 3
    && revision.status === "approved-build42-partial-device-visual-rejected");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/rev-003",
);
const read = (name) => JSON.parse(
  fs.readFileSync(path.join(evidence, name), "utf8"));

test("Gate 12 rev 3 preserves partial approval and final approval", () => {
  assert.ok(approvedRev3);
  assert.equal(approvedRev3.shippingSpec.revision, 3);
  assert.equal(approvedRev3.decision.notes, "这个是对的");
  assert.equal(approvedRev3.shippingSpec.gate12Approval, "approved");
  const prior = gate12.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 2);
  assert.equal(prior.status, "partially-approved-revision-requested");
  assert.equal(prior.decision.acceptedViews.length, 7);
  assert.equal(
    prior.decision.screenshotSha256,
    "d36fb987ee46313fe401337a61552d6e80c3310f9ccdb9852938edee4191015b",
  );
});

test("accepted shipping views remain byte-identical", () => {
  const validation = read("gate12-motion-validation.json");
  assert.equal(validation.checks.acceptedViewsByteIdentical, true);
  for (const hashes of Object.values(validation.acceptedViewHashes))
    assert.equal(hashes.rev2, hashes.rev3);
});

test("motion stays connected and in plane for every frame", () => {
  const capture = read("unity-playmode-frames/capture-report.json");
  assert.ok(capture.maximumTopStackResidualMeters <= 5e-9);
  assert.ok(capture.maximumOutOfPlaneSlideResidualMeters <= 1e-9);
  assert.ok(capture.maximumFixedAxisConstraintResidual <= 1e-9);
  assert.equal(capture.renderersAttachedEveryFrame, true);
  assert.equal(capture.detentsStayedAtMaximumTravel, true);
  assert.equal(capture.observedDetentMask, 1073741823);
  assert.equal(capture.wholeProductPitchRollDegrees, 0);
});

test("runtime uses corrected converted coordinate axes", () => {
  const source = fs.readFileSync(
    path.join(
      repoRoot,
      "unity/FidgetingApp/Assets/_EDC/Candidates/"
        + "MagneticSlideTileGate12R002/Runtime/"
        + "MagneticSlideTileShippingMechanism.cs",
    ),
    "utf8",
  );
  assert.match(source, /AngleAxis\(AngleDegrees, Vector3\.forward\)/);
  assert.match(source, /closedSlidePosition \+ Vector3\.down \* TravelMeters/);
  assert.doesNotMatch(
    source,
    /closedSlidePosition \+ Vector3\.forward \* TravelMeters/,
  );
});

test("current review assets exist and retain registered hashes", () => {
  for (const assetId of approvedRev3.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    assert.ok(asset);
    assert.equal(sha256File(path.join(repoRoot, asset.path)), asset.sha256);
  }
  assert.equal(approvedRev3.shippingSpec.candidateDefaultActive, true);
  assert.equal(approvedRev3.shippingSpec.oldShippingModelDefaultActive, false);
  assert.equal(approvedRev3.shippingSpec.shippingPromotion, "complete");
  assert.equal(approvedRev3.shippingSpec.unityExportSucceeded, true);
  assert.equal(approvedRev3.shippingSpec.xcodeBuildSucceeded, true);
  assert.equal(approvedRev3.shippingSpec.signed, true);
  assert.equal(approvedRev3.shippingSpec.installed, true);
  assert.equal(approvedRev3.shippingSpec.launched, true);
  assert.equal(approvedRev3.shippingSpec.buildNumber, "42");
  assert.equal(approvedRev3.shippingSpec.deliveryBlocker, null);
  assert.equal(approvedRev3.shippingSpec.buildInstallPhone, true);
  assert.equal(
    approvedRev3.shippingSpec.deviceAcceptance,
    "pending-user-validation",
  );
});
