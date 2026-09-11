import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import {
  loadManifest,
  repoRoot,
  sha256File,
  stageReadiness,
} from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const rev2 = gate12.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 2);
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-002"
);
const read = (name) => JSON.parse(
  fs.readFileSync(path.join(evidence, name), "utf8"));

test("Gate 12 rev 2 preserves partial approval history", () => {
  assert.ok(manifest.revision >= 258);
  assert.equal(rev2.shippingSpec.revision, 2);
  assert.equal(rev2.status, "partially-approved-revision-requested");
  assert.equal(rev2.decision.acceptedViews.length, 7);
  assert.equal(gate12.shippingSpec.revision, 4);
  assert.equal(gate12.status, "approved");
  assert.equal(gate12.decision.action, "approve");
  assert.equal(stageReadiness(manifest, "12-shipping").ready, true);
  assert.equal(
    gate12.shippingSpec.visualApproval,
    "gate12-r004-variant-b-approved-review-ui");
  assert.equal(
    gate12.shippingSpec.deviceAcceptance,
    "pending-build44-install-and-user-validation",
  );
  assert.equal(gate12.shippingSpec.buildInstallPhone, false);
});

test("rev 2 report preserves the former disabled candidate", () => {
  const report = read("gate12-shipping-report.json");
  assert.equal(report.pass, true);
  assert.equal(report.candidateDefaultActive, false);
  assert.equal(report.oldShippingModelDefaultActive, true);
  assert.equal(
    report.shippingSceneSha256,
    "b73676a208659c9f769bae438913cc6bfcba35ba1fb0ef06ae0683687f62117c",
  );
  assert.equal(report.triangles, 99280);
});

test("runtime and Haptics share endpoint detents", () => {
  const report = read("gate12-shipping-report.json");
  assert.equal(report.maximumTravelMeters, 0.01807643286883831);
  assert.equal(report.detentCount, 30);
  assert.equal(report.detentStepDegrees, 12);
  assert.equal(report.runtimeInputIntegrated, true);
  assert.equal(report.hapticsIntegrated, true);
  assert.match(report.semanticRoute, /FidgetSemanticEvent -> FidgetHapticRouter/);
});

test("Unity-only recording proves endpoint interlock", () => {
  const capture = read("unity-playmode-frames/capture-report.json");
  const validation = read("gate12-image-validation.json");
  const probe = read("video-probe.json");
  assert.equal(capture.unityOnly, true);
  assert.equal(capture.sourceScene, "Assets/_EDC/Scenes/MeshyEDC.unity");
  assert.equal(capture.candidateExplicitlyEnabled, true);
  assert.equal(capture.detentCount, 30);
  assert.ok(capture.transitions.includes("rotation-locked-until-maximum-travel"));
  assert.ok(capture.transitions.includes("slide-locked-until-angle-aligns"));
  assert.ok(capture.transitions.includes("endpoint-detent-29"));
  assert.ok(capture.transitions.includes("angle-aligned-slide-unlocked"));
  assert.equal(capture.zeroInitialAndResetVelocity, true);
  assert.equal(capture.wholeProductPitchRollDegrees, 0);
  assert.equal(validation.pass, true);
  assert.equal(probe.streams[0].nb_read_frames, "240");
});

test("registered review artifacts retain their hashes", () => {
  for (const assetId of rev2.reviewArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    assert.ok(asset);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(fs.existsSync(absolute), true);
    assert.equal(sha256File(absolute), asset.sha256);
  }
});
