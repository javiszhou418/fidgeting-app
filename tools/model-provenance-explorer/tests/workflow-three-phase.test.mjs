import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const read = (relative) => fs.readFileSync(new URL(`../../../${relative}`, import.meta.url), "utf8");
const manifest = JSON.parse(read(
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json"
));

test("keeps exactly 12 gates mapped once into three user phases", () => {
  assert.equal(manifest.stages.length, 12);
  const phases = manifest.currentState.workflowPhases;
  assert.deepEqual(phases.map((phase) => phase.id), [
    "interaction-form",
    "blender-modeling-textures",
    "unity-scene-rendering"
  ]);
  assert.deepEqual(phases.flatMap((phase) => phase.gates), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
  const app = read("tools/model-provenance-explorer/app.js");
  assert.match(app, /参考 \+ 交互形式/);
  assert.match(app, /Blender 建模 \+ 贴图/);
  assert.match(app, /Unity \+ 场景 \+ 渲染/);
  assert.match(app, /12 个 Gate 固定不变，归为 3 个易懂阶段/);
});

test("removes standalone Simulator as an active pre-Blender requirement", () => {
  const activePolicy = [
    read("AGENTS.md"),
    read("skills/fidgeting-model-pipeline/SKILL.md"),
    read("skills/fidgeting-model-pipeline/references/pipeline-contract.md"),
    read("tools/model-provenance-explorer/pipeline-contract.mjs")
  ].join("\n");
  assert.doesNotMatch(activePolicy, /Simulator approval is required before Blender/);
  assert.doesNotMatch(activePolicy, /Simulator 批准后才允许 Blender/);
  assert.match(activePolicy, /standalone hand-feel Simulator is not a pre-Blender gate|独立手感 Simulator 不是前置门禁/);
  assert.equal(manifest.currentState.simulatorStatus, "not-used");
  assert.equal(manifest.assets.some((asset) => asset.id.includes("feel-simulator")), false);
});

test("continues from corrected geometry into material review", () => {
  const gate02 = manifest.stages.find((stage) => stage.id === "02-analysis");
  const gate03 = manifest.stages.find((stage) => stage.id === "03-contract");
  const gate04 = manifest.stages.find((stage) => stage.id === "04-architecture");
  const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
  assert.equal(gate02.status, "approved");
  assert.equal(gate03.status, "approved");
  assert.equal(gate04.status, "approved");
  assert.equal(gate05.status, "approved");
  assert.deepEqual(gate03.requiredPhysicalDimensions, []);
  assert.deepEqual(gate03.manufacturingLaterDimensions, [
    "operatingClearance",
    "manufacturingAllowance",
    "manufacturingTolerance"
  ]);
  assert.equal(gate03.measurementProgress.complete, 9);
  assert.equal(gate03.measurementProgress.total, 9);
  assert.equal(gate03.measurementProgress.mode, "user-authorized-anthropometric-video-provisional");
  assert.equal(
    manifest.currentState.blenderModelingStatus,
    "gate10-rev11-approved-exact-wording-continued",
  );
  assert.equal(manifest.currentState.shippingAssetUnchanged, false);
  assert.equal(manifest.currentState.workflowPhases.length, 3);
  assert.equal(manifest.model.status, "shipping-current-rebuild-requested");
  assert.equal(
    manifest.currentState.deviceStatus,
    "build42-rejected-rotation-build43-nonreusable-device-disconnected",
  );
});

test("active Gate 03 contract labels anthropometric estimates and blockers", () => {
  const gate03 = manifest.stages.find((stage) => stage.id === "03-contract");
  const asset = manifest.assets.find((candidate) => candidate.id === "magnetic-slide-tile-provisional-modeling-contract-r010");
  const contract = JSON.parse(read(asset.path));
  assert.equal(contract.schemaVersion, 4);
  assert.match(contract.kind, /anthropometric-video-provisional/);
  assert.match(contract.dimensionClass, /not production measured/);
  assert.equal(contract.dimensionsMm.overallLength.provisional, 50);
  assert.equal(contract.dimensionsMm.overallWidth.provisional, 31);
  assert.equal(contract.mechanism.trackCount, 4);
  assert.equal(contract.mechanism.recessedAxis, false);
  assert.deepEqual(contract.dimensionsMm.ballDiameter.range, [2, 3]);
  assert.equal(contract.generationBlockers.trackWidthMaximumMm, 3);
});

test("records the latest workflow decision in the design bible and history", () => {
  const bible = read("unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md");
  const history = read(
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/history.ndjson"
  );
  assert.match(bible, /FDB-SLD-038/);
  assert.match(bible, /FDB-SLD-040/);
  assert.match(bible, /FDB-SLD-041/);
  assert.match(bible, /确定交互形式后，是开始建模\+贴图的流程，然后 Unity\+场景\+渲染/);
  assert.match(history, /"type":"workflow-sequence-superseded"/);
  assert.match(history, /"type":"gate03-gate04-user-authorized-provisional-migration-approved"/);
  assert.match(history, /"type":"gate05-approved-cad-white-blockout-ready-for-review"/);
  assert.match(history, /"canonicalGateCount":12/);
});
