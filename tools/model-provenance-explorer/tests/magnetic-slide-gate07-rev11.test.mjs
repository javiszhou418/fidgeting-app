import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-011"
);
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(evidence, filename), "utf8"));

test("Gate 06 rev 4 approval evidence remains preserved under rev 5", () => {
  assert.equal(gate06.status, "approved");
  assert.equal(gate06.geometrySpec.revision, 5);
  assert.ok(manifest.assets.some((asset) => asset.id === "magnetic-slide-tile-geometry-blend-r004"));
  assert.equal(manifest.currentStageId, "12-shipping");
});

test("Gate 07 rev 11 assets remain preserved under rev 13", () => {
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.materialSpec.revision, 13);
  assert.equal(gate07.materialSpec.sourceGate06Revision, 5);
  assert.equal(gate07.materialSpec.governingContractSha256, "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571");
  assert.ok(manifest.assets.some((asset) => asset.id === "magnetic-slide-tile-material-lookdev-r011"));
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
});

test("Gate 07 preserves approved geometry across every material pose", () => {
  const report = readJson("material-validation.json");
  assert.equal(report.pass, true);
  assert.equal(report.geometryDigestBefore, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(report.geometryDigestAfter, report.geometryDigestBefore);
  for (const digest of Object.values(report.poseGeometryDigests)) assert.equal(digest, report.geometryDigestBefore);
  assert.equal(report.checks.zeroSelfMotion, true);
  assert.equal(report.checks.oldShippingUntouched, true);
});

test("source-backed masks remain distinct, editable and immutable", () => {
  const report = readJson("texture-lineage.json");
  assert.equal(report.pass, true);
  assert.equal(report.sourceMasks.upper.sha256, "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36");
  assert.equal(report.sourceMasks.lower.sha256, "7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60bd81c1b88ec42dfa7c2");
  assert.equal(report.sourceMasks.border.sha256, "2179bf26210994c8b3d279337bf6ad0f4beaee3c7285ae97d1cd888db2bd64fc");
  assert.equal(report.independentlyReplaceable, true);
  assert.equal(report.lowerDirectPixels, 118942);
  assert.equal(report.lowerReconstructedPixels, 102670);
});

test("material and image audits pass without emission or visible clipping", () => {
  const blender = readJson("blender-material-audit.json");
  const image = readJson("image-material-audit.json");
  assert.equal(blender.pass, true);
  assert.equal(blender.checks.glbEmbeddedImages, true);
  assert.equal(blender.checks.zeroEmission, true);
  assert.equal(image.pass, true);
  assert.ok(image.maximumClippedFraction < 0.001);
  assert.equal(image.fullBlackPerimeter.upperBlackFractionWithinBorderMask, 1);
  assert.equal(image.fullBlackPerimeter.lowerBlackFractionWithinBorderMask, 1);
});

test("interactive GLB, real turntable and source boards are registered", () => {
  const required = [
    "magnetic-slide-tile-material-lookdev-r011",
    "magnetic-slide-tile-material-turntable-r011",
    "magnetic-slide-tile-material-source-comparison-r011",
    "magnetic-slide-tile-material-board-r011",
    "magnetic-slide-tile-material-closeups-r011",
  ];
  for (const id of required) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset);
    assert.equal(asset.sha256, sha256File(path.join(repoRoot, asset.path)));
  }
});

test("workbench exposes material environment and exposure controls", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 07 rev 11/);
  assert.match(app, /data-environment/);
  assert.match(app, /data-exposure/);
  assert.match(app, /viewerEnvironment/);
  assert.match(app, /viewerExposure/);
});

test("docs record Gate 07 approval and no device work", () => {
  const status = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  const bible = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  assert.match(status, /Gate 07 rev 11 已由用户以原话“继续”批准/);
  assert.match(status, /视觉批准待确认，未推送手机/);
  assert.match(status, /旧 shipping Unity 模型仍为默认/);
  assert.match(bible, /FDB-SLD-047/);
  assert.match(bible, /那你继续呗/);
});

