import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  sha256File,
} from "../pipeline-core.mjs";

const repoRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)), "../../..");
const manifest = loadManifest("magnetic-slide-tile");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
const build42 = gate12.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 3
    && revision.status === "approved-build42-partial-device-visual-rejected");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/runtime-recovery-build42",
);
const directionEvidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/runtime-recovery-rotation-direction",
);

test("build 41 is rejected and build 42 delivery remains preserved", () => {
  assert.ok(build42);
  assert.equal(build42.decision.notes, "这个是对的");
  assert.equal(
    build42.shippingSpec.rejectedBuild.buildNumber,
    "41",
  );
  assert.equal(
    build42.shippingSpec.rejectedBuild.deviceAcceptance,
    "rejected-low-fi-noninteractive",
  );
  assert.equal(build42.shippingSpec.runtimeInteractionIntegrated, true);
  assert.equal(build42.shippingSpec.visualGeometryChanged, false);
  assert.equal(build42.shippingSpec.materialChanged, false);
  assert.equal(build42.shippingSpec.buildInstallPhone, true);
  assert.equal(build42.shippingSpec.nextBuildNumber, "42");
  assert.equal(
    build42.shippingSpec.build42Preflight.status,
    "passed",
  );
  assert.equal(build42.shippingSpec.build42Preflight.passcodeRequired, false);
});

test("shipping scene owns a valid candidate input path", () => {
  const report = JSON.parse(fs.readFileSync(
    path.join(evidence, "runtime-interaction-wiring-report.json"), "utf8"));
  assert.equal(report.pass, true);
  assert.equal(report.candidateDefaultActive, true);
  assert.equal(report.fallbackDefaultActive, false);
  assert.equal(report.hiddenDebugCollidersEnabled, 0);
  assert.equal(report.inputController, "FidgetingApp.EDC.EdcSliderController");
  assert.equal(report.cameraTarget, "MagneticSlideTileGate12R002Candidate");
  assert.equal(report.audioVoices, 6);
  assert.equal(
    report.shippingSceneSha256,
    build42.shippingSpec.sceneSha256,
  );
  assert.notEqual(
    report.shippingSceneSha256,
    sha256File(path.join(
      repoRoot, "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity")),
  );
});

test("focused tests use real PlayMode Input System touch state", () => {
  const xml = fs.readFileSync(
    path.join(evidence, "playmode-input-tests.xml"), "utf8");
  assert.match(xml, /testcasecount="3" result="Passed".*passed="3"/);
  const tests = fs.readFileSync(path.join(
    repoRoot,
    "unity/FidgetingApp/Assets/_EDC/Candidates/"
      + "MagneticSlideTileGate12R002/Tests/PlayMode/"
      + "MagneticSlideTileInputPlayModeTests.cs",
  ), "utf8");
  assert.match(tests, /InputSystem\.QueueStateEvent\(/);
  assert.match(tests, /new TouchState/);
  assert.match(tests, /TouchEventsArbitrateToyOrbitAndPinch/);
  assert.match(tests, /context\.DetentCount/);
  assert.doesNotMatch(tests, /SendMessage\("Update"\)/);
});

test("runtime keeps semantic Haptics and endpoint interlock", () => {
  const controller = fs.readFileSync(path.join(
    repoRoot, "unity/FidgetingApp/Assets/_EDC/Runtime/EdcSliderController.cs",
  ), "utf8");
  const coordinator = fs.readFileSync(path.join(
    repoRoot,
    "unity/FidgetingApp/Assets/_EDC/Candidates/"
      + "MagneticSlideTileGate12R002/Runtime/"
      + "MagneticSlideTileShippingCoordinator.cs",
  ), "utf8");
  const appCoordinator = fs.readFileSync(path.join(
    repoRoot,
    "unity/FidgetingApp/Assets/Scripts/Product/FidgetAppCoordinator.cs",
  ), "utf8");
  assert.match(controller, /UpdateShippingInput\(\)/);
  assert.match(controller, /TryApplySlideInput\(requested\)/);
  assert.match(controller, /TryApplyRotationInput\(requested\)/);
  assert.match(controller, /SemanticEventRaised \+=/);
  assert.match(appCoordinator, /FidgetHapticRouter\.EmitMagneticSlider/);
  assert.doesNotMatch(coordinator, /FidgetHapticRouter/);
  assert.doesNotMatch(controller, /IosHaptics\./);
  assert.doesNotMatch(coordinator, /IosHaptics\./);
});

test("device-reported rotation direction uses oriented plane touch arcs", () => {
  const report = JSON.parse(fs.readFileSync(path.join(
    directionEvidence,
    "rotation-direction-fix-report.json",
  ), "utf8"));
  const xml = fs.readFileSync(
    path.join(directionEvidence, "playmode-results.xml"),
    "utf8",
  );
  const controller = fs.readFileSync(path.join(
    repoRoot,
    "unity/FidgetingApp/Assets/_EDC/Runtime/EdcSliderController.cs",
  ), "utf8");
  const tests = fs.readFileSync(path.join(
    repoRoot,
    "unity/FidgetingApp/Assets/_EDC/Candidates/"
      + "MagneticSlideTileGate12R002/Tests/PlayMode/"
      + "MagneticSlideTileInputPlayModeTests.cs",
  ), "utf8");

  assert.equal(report.deviceAcceptance, "failed-rotation-direction");
  assert.equal(report.fix.cameraRobust, true);
  assert.equal(report.delivery.build43Reusable, false);
  assert.equal(report.delivery.build44SourceReady, true);
  assert.equal(report.delivery.build44Attempted, false);
  assert.match(xml, /testcasecount="4" result="Passed".*passed="4"/);
  assert.match(controller, /camera\.ScreenPointToRay\(position\)/);
  assert.match(controller, /Vector3\.SignedAngle\(/);
  assert.match(controller, /TransformDirection\(Vector3\.forward\)/);
  assert.doesNotMatch(controller, /Mathf\.Atan2\(radial\.y, radial\.x\)/);
  assert.match(
    tests,
    /TouchArcsPreserveVisualDirectionAcrossOrbitAndZoom/,
  );
  assert.match(tests, /clockwiseDirection \* 360f/);
  assert.match(tests, /AssertDirectionMetadata/);
});
