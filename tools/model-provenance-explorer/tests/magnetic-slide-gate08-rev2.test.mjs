import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate07Rev12 = gate07.historicalRevisions.find(
  (revision) => revision.revision === 12,
);
const historicalGate08 = gate08.historicalRevisions.find(
  (revision) => revision.evidenceRevision === 2,
);
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-002"
);
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(evidence, filename), "utf8"));

test("Gate 07 rev 11 and rev 12 approvals remain preserved during rev 13", () => {
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.materialSpec.revision, 13);
  assert.equal(gate07.materialSpec.sourceGate07Revision, 12);
  assert.equal(gate07Rev12.decision.notes, "继续");
  assert.ok(manifest.assets.some((asset) => asset.id === "magnetic-slide-tile-material-lookdev-r011"));
});

test("Gate 08 rev 2 remains approved stale history after geometry rejection", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate08.status, "approved");
  assert.equal(historicalGate08.decision.notes, "进行下一步吧");
  assert.equal(historicalGate08.lightingSpec.revision, 2);
  assert.equal(historicalGate08.lightingSpec.sourceMaterialRevision, 11);
  assert.deepEqual(historicalGate08.lightingSpec.lightingModes, ["neutral", "studio", "daylight"]);
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
});

test("lighting preserves approved geometry and material hashes", () => {
  const report = readJson("lighting-validation.json");
  assert.equal(report.pass, true);
  assert.equal(report.sourceGate07.approvalWording, "继续");
  assert.equal(report.geometry.before, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(report.geometry.after, report.geometry.before);
  assert.equal(report.materials.after, report.materials.before);
  assert.ok(Object.values(report.materials.approvedEmission).every((value) => value === 0));
  assert.equal(report.checks.matricesRestored, true);
  assert.equal(report.checks.zeroSelfMotion, true);
  assert.equal(report.checks.oldShippingUntouched, true);
});

test("required views, passes and lighting modes pass image audit", () => {
  const report = readJson("image-lighting-audit.json");
  assert.equal(report.pass, true);
  assert.equal(report.checks.requiredViewSize, true);
  assert.equal(report.checks.passesDistinct, true);
  assert.equal(report.checks.bloodRedHue, true);
  assert.equal(report.checks.noPinkDrift, true);
  assert.equal(report.checks.neutralSilver, true);
  assert.equal(report.checks.noBlueGraySilver, true);
  assert.equal(report.checks.mechanicalReadable, true);
  assert.ok(report.maximumBeautyClippedFraction < 0.001);
});

test("independent Blender audit confirms rig and embedded GLB", () => {
  const report = readJson("blender-lighting-audit.json");
  assert.equal(report.pass, true);
  assert.equal(report.checks.fourDocumentedLights, true);
  assert.equal(report.checks.requiredCameras, true);
  assert.equal(report.checks.reflectionCards, true);
  assert.equal(report.checks.approvedEmissionZero, true);
  assert.equal(report.checks.glbEmbeddedImages, true);
});

test("interactive lookdev, turntable, boards and pass evidence are registered", () => {
  const required = [
    "magnetic-slide-tile-lighting-lookdev-r002",
    "magnetic-slide-tile-lighting-turntable-r002",
    "magnetic-slide-tile-lighting-mode-comparison-r002",
    "magnetic-slide-tile-lighting-pass-board-r002",
    "magnetic-slide-tile-lighting-mechanical-board-r002",
  ];
  for (const id of required) {
    assert.ok(historicalGate08.reviewArtifactIds.includes(id));
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset);
    assert.equal(asset.sha256, sha256File(path.join(repoRoot, asset.path)));
  }
});

test("workbench exposes three lighting modes, orbit, zoom and exposure", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 08 rev 2/);
  assert.match(app, /data-lighting-mode/);
  assert.match(app, /neutral/);
  assert.match(app, /studio/);
  assert.match(app, /daylight/);
  assert.match(app, /viewerLightingMode/);
  assert.match(app, /OrbitControls/);
  assert.match(app, /data-exposure/);
});

test("docs record lighting approval and no device work", () => {
  const status = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  const bible = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  assert.match(status, /Gate 08 rev 2 后由用户以原话“进行下一步吧”批准/);
  assert.match(status, /视觉批准待确认，未推送手机/);
  assert.match(status, /旧 shipping Unity 模型仍为默认/);
  assert.match(bible, /FDB-SLD-048/);
  assert.match(bible, /FDB-SLD-048.*用户以原话“进行下一步吧”批准/s);
});

