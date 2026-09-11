import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import {
  loadManifest,
  repoRoot,
} from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/rev-004-lighting",
);
const report = JSON.parse(fs.readFileSync(
  path.join(evidence, "lighting-review-report.json"), "utf8"));
const metrics = JSON.parse(fs.readFileSync(
  path.join(evidence, "lighting-image-metrics.json"), "utf8"));
const approval = JSON.parse(fs.readFileSync(
  path.join(evidence, "variant-b-shipping-approval.json"), "utf8"));
const build42Hashes = fs.readFileSync(path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/runtime-recovery-build42/device-delivery/"
    + "magnetic-slide-build42-20260901T035903Z-snapshot/"
    + "source-hashes-snapshot.txt",
), "utf8");

test("Variant B is the approved Gate 12 shipping lighting", () => {
  assert.equal(gate12.status, "approved");
  assert.equal(gate12.shippingSpec.revision, 4);
  assert.equal(
    gate12.shippingSpec.build42FeedbackExactWording,
    "好多了，但感觉灯光有点奇怪，主要是太暗了.",
  );
  assert.equal(
    gate12.shippingSpec.build42InteractionAcceptance,
    "partial-success",
  );
  assert.equal(
    gate12.shippingSpec.build42VisualAcceptance,
    "failed-dark-lighting",
  );
  assert.equal(gate12.shippingSpec.recommendationApproved, true);
  assert.equal(gate12.shippingSpec.selectedVariant, "B-balanced-brighter");
  assert.deepEqual(gate12.shippingSpec.approvedLighting, approval.parameters);
  assert.equal(
    gate12.shippingSpec.deviceAcceptance,
    "pending-build44-install-and-user-validation",
  );
});

test("lighting approval snapshot changed no protected runtime or model source", () => {
  assert.equal(report.pass, true);
  assert.equal(report.protectedRuntimeUnchanged, true);
  assert.equal(report.geometryChanged, false);
  assert.equal(report.materialsChanged, false);
  assert.equal(report.artworkChanged, false);
  assert.equal(report.interactionChanged, false);
  assert.equal(report.audioChanged, false);
  assert.equal(report.hapticsChanged, false);
  for (const source of report.protectedSources) {
    const absolute = path.join(repoRoot, "unity/FidgetingApp", source.path);
    assert.match(
      build42Hashes,
      new RegExp(`${source.sha256}  ${absolute.replaceAll("\\", "\\\\")}`),
      `${source.path} must remain byte-equivalent to installed Build 42`,
    );
  }
});

test("approval limits shipping changes to reviewed lighting fields", () => {
  assert.equal(approval.decisionState, "approved");
  assert.equal(approval.selectedVariant, "B-balanced-brighter");
  assert.deepEqual(approval.preserved, {
    geometry: true,
    materialTexturesAndPartitions: true,
    cameraPositionRecipes: true,
    runtimeInteraction: true,
    endpointInterlock: true,
    pinchOrbit: true,
    audio: true,
    haptics: true,
  });
  assert.deepEqual(approval.parameters, {
    postExposureEv: 0.55,
    hdr: true,
    tonemapping: "Neutral",
    ambientMultiplier: 1.25,
    reflectionIntensity: 0.70,
    keyIntensity: 0.68,
    fillIntensity: 0.54,
    whiteBalanceTemperature: 0.0,
    whiteBalanceTint: 0.0,
  });
});

test("balanced recommendation lifts midtones without clipping or color loss", () => {
  assert.equal(metrics.pass, true);
  assert.equal(metrics.recommendation, "B-balanced-brighter");
  const balanced = metrics.summary["B-balanced-brighter"];
  assert.ok(balanced.midtoneGainVsBuild42 >= 0.15);
  assert.ok(balanced.blackDetailGainVsBuild42 > 0);
  assert.ok(balanced.redSaturationRetentionVsBuild42 >= 0.90);
  assert.ok(balanced.clippedFraction < 0.005);
  assert.equal(metrics.qualityChecks.noExposurePumping, true);
  assert.equal(metrics.qualityChecks.neutralWhiteBalance, true);
});

test("every variant has all shipping and legal motion views", () => {
  const variants = [
    "A-build42-baseline",
    "B-balanced-brighter",
    "C-everyday-d65",
  ];
  const views = [
    "library",
    "hero",
    "top",
    "left-oblique",
    "right-oblique",
    "low",
    "phone",
    "max-open",
    "endpoint-36deg",
  ];
  for (const variant of variants) {
    for (const view of views) {
      assert.ok(
        fs.statSync(path.join(evidence, variant, `${view}.png`)).size > 10_000,
        `${variant}/${view}`,
      );
    }
  }
});

test("review includes comparison boards and Unity-only video", () => {
  for (const file of [
    "gate12-lighting-comparison-board-r004.png",
    "gate12-lighting-phone-board-r004.png",
    "gate12-lighting-histograms-r004.png",
    "magnetic-slide-gate12-r004-lighting-comparison.mp4",
  ]) {
    assert.ok(fs.statSync(path.join(evidence, file)).size > 10_000, file);
  }
  const scene = fs.readFileSync(
    path.join(
      repoRoot,
      "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity",
    ),
    "utf8",
  );
  assert.match(scene, /MagneticSlideShippingLightingController/);
  assert.match(scene, /variant: 1/);
});
