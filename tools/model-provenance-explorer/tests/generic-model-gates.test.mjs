import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  addIntakeFile,
  createModelPipeline,
  loadManifest,
  pipelineDirectory,
  readHistory,
  resolveRepoPath,
  saveAnalysisResearchRevision,
  saveArchitecturePlan,
  saveManifest,
  saveMeasurementSource,
  saveModelingContract,
  stageReadiness,
  updateModelMechanism
} from "../pipeline-core.mjs";
import { MEASUREMENT_BASIS_TYPES, REQUIRED_CORE_MEASUREMENTS } from "../measurement-contract-core.mjs";

const modelId = `zz-test-generic-slider-${process.pid.toString(36)}`;
const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });

function approveFixtureStage(stageId) {
  const manifest = loadManifest(modelId);
  const stage = manifest.stages.find((candidate) => candidate.id === stageId);
  stage.status = "approved";
  stage.decision = {
    action: "approve",
    notes: "temporary test fixture approval",
    decidedBy: "test",
    decidedAt: new Date().toISOString()
  };
  saveManifest(manifest, null);
}

function analysisPaths() {
  const directory = path.join(pipelineDirectory(modelId), "evidence/02-analysis/rev-001");
  fs.mkdirSync(directory, { recursive: true });
  const discovery = path.join(directory, "discovery-log.json");
  const board = path.join(directory, "analysis-board.png");
  fs.writeFileSync(discovery, JSON.stringify({ finding: "linear magnetic slider", dimensionsMm: null }));
  fs.writeFileSync(board, Buffer.from([0x89, 0x50, 0x4e, 0x47, 1, 2, 3, 4]));
  return {
    discovery: path.relative(resolveRepoPath("."), discovery).split(path.sep).join("/"),
    board: path.relative(resolveRepoPath("."), board).split(path.sep).join("/")
  };
}

const known = (valueMm, uncertaintyMm = 0.1) => ({
  state: "known",
  unknown: false,
  valueMm,
  uncertaintyMm,
  source: "用户提供",
  method: "用户按工作台指引提供"
});

test("an ordinary new slider can safely enter Gate 03 and Gate 04", (t) => {
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "普通磁吸推牌", mechanism: "other" });
  const intake = addIntakeFile(modelId, { filename: "reference.png", bytes: Buffer.from("reference") });
  approveFixtureStage("01-intake");

  const paths = analysisPaths();
  const analysis = saveAnalysisResearchRevision(modelId, {
    expectedRevision: intake.manifest.revision,
    recipe: "generic model Gate 02 test",
    assets: [
      { id: `${modelId}-discovery-r001`, slot: "discovery-log", path: paths.discovery, sourceAssetIds: [intake.asset.id] },
      { id: `${modelId}-board-r001`, slot: "analysis-board", path: paths.board, sourceAssetIds: [intake.asset.id] }
    ],
    claims: [
      { id: `${modelId}-mechanism-r001`, category: "mechanism", statement: "这是线性磁吸推牌。", confidence: "medium", sourceAssetIds: [intake.asset.id] },
      { id: `${modelId}-dimensions-r001`, category: "dimension", statement: "照片没有可靠毫米参照，尺寸未知。", confidence: "high", sourceAssetIds: [intake.asset.id] }
    ],
    validations: [
      { id: "no-mm-inference", status: "pass", evidence: "No millimetres were inferred." }
    ]
  });
  assert.throws(
    () => updateModelMechanism(modelId, { expectedRevision: analysis.revision, mechanism: "linear-magnetic-slider" }),
    /Gate 02/
  );
  approveFixtureStage("02-analysis");

  const updated = updateModelMechanism(modelId, {
    expectedRevision: analysis.revision,
    mechanism: "linear-magnetic-slider",
    note: "approved Gate 02 mechanism classification"
  });
  assert.equal(updated.model.mechanism, "linear-magnetic-slider");
  assert.equal(updated.revision, analysis.revision + 1);
  assert.equal(readHistory(modelId)[0].type, "model-mechanism-updated");

  const unknownMeasurements = Object.fromEntries(REQUIRED_CORE_MEASUREMENTS.map(({ id }) => [id, {
    state: "unknown",
    unknown: true
  }]));
  const blocked = saveModelingContract(modelId, {
    expectedRevision: updated.revision,
    measurementSchemaVersion: 2,
    requiredMeasurements: unknownMeasurements
  });
  assert.equal(blocked.manifest.stages[2].status, "blocked");
  assert.equal(blocked.contract.completeness.requiredComplete, 0);
  assert.ok(Object.values(blocked.contract.measurements.required).every((entry) => entry.state === "unknown"));
  assert.equal(stageReadiness(loadManifest(modelId), "03-contract").ready, false);

  const requiredMeasurements = {
    closedOverallLength: known(60, 0.2),
    overallWidth: known(38, 0.2),
    totalClosedThickness: known(9.5, 0.2),
    topPlateThickness: known(4.5),
    bottomPlateThickness: known(4.7),
    maximumSlideTravel: known(20, 0.2),
    fixedAxisOffsetFromNearestEnd: known(12),
    rotatingCarrierDiameter: known(20),
    closedSeamGap: known(0.3, 0.05)
  };
  const ready = saveModelingContract(modelId, {
    expectedRevision: blocked.manifest.revision,
    measurementSchemaVersion: 2,
    requiredMeasurements
  });
  assert.equal(ready.manifest.stages[2].status, "ready_for_review");
  assert.equal(ready.contract.completeness.complete, true);
  assert.equal(ready.contract.approvedGate02EvidenceSha256, analysis.stages[1].outputDigest);
  assert.deepEqual(ready.contract.sourceClaimIds.sort(), [
    `${modelId}-dimensions-r001`,
    `${modelId}-mechanism-r001`
  ].sort());
  assert.equal(stageReadiness(loadManifest(modelId), "03-contract").ready, true);

  approveFixtureStage("03-contract");
  const architectureDirectory = path.join(pipelineDirectory(modelId), "evidence/04-architecture/rev-001");
  fs.mkdirSync(architectureDirectory, { recursive: true });
  const partTree = path.join(architectureDirectory, "part-tree.svg");
  const explodedPlan = path.join(architectureDirectory, "exploded-plan.svg");
  fs.writeFileSync(partTree, '<svg xmlns="http://www.w3.org/2000/svg"><text>part tree</text></svg>');
  fs.writeFileSync(explodedPlan, '<svg xmlns="http://www.w3.org/2000/svg"><text>exploded plan</text></svg>');
  const architecture = saveArchitecturePlan(modelId, {
    expectedRevision: ready.manifest.revision,
    partTreePath: path.relative(resolveRepoPath("."), partTree).split(path.sep).join("/"),
    explodedPlanPath: path.relative(resolveRepoPath("."), explodedPlan).split(path.sep).join("/"),
    recipe: "generic source-linked architecture test"
  });
  assert.equal(architecture.stages[3].status, "ready_for_review");
  assert.equal(architecture.stages[3].architectureSpec, undefined, "ordinary output remains visible in the generic asset renderer");
  assert.equal(architecture.stages[3].reviewArtifactIds.length, 2);
  assert.ok(architecture.stages[3].validations.every((validation) => validation.status === "pass"));
  assert.equal(stageReadiness(loadManifest(modelId), "04-architecture").ready, true);
});

test("mechanism updates stop once Gate 03 has evidence", (t) => {
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "已有尺寸的模型", mechanism: "other" });
  const manifest = loadManifest(modelId);
  manifest.stages[1].status = "approved";
  manifest.assets.push({
    id: `${modelId}-contract-placeholder`,
    stageId: "03-contract",
    slot: "modeling-contract",
    path: "AGENTS.md",
    sha256: "placeholder",
    exists: true,
    role: "contract",
    producer: { name: "test", version: "1" },
    sourceAssetIds: []
  });
  saveManifest(manifest, null);
  assert.throws(
    () => updateModelMechanism(modelId, { expectedRevision: manifest.revision, mechanism: "linear-magnetic-slider" }),
    (error) => error.statusCode === 409
  );
});

test("Gate 03 persists hash-linked official specs and calibrated digital reconstruction targets", (t) => {
  const strictModelId = `zz-test-strict-measurement-${process.pid.toString(36)}`;
  const strictCleanup = () => fs.rmSync(pipelineDirectory(strictModelId), { recursive: true, force: true });
  t.after(strictCleanup);
  strictCleanup();
  createModelPipeline({ id: strictModelId, name: "严格尺寸来源测试", mechanism: "linear-magnetic-slider" });
  const intake = addIntakeFile(strictModelId, { filename: "reference.png", bytes: Buffer.from("reference") });
  let manifest = loadManifest(strictModelId);
  manifest.stages[0].status = "approved";
  manifest.stages[0].decision = { action: "approve", notes: "fixture", decidedBy: "test", decidedAt: new Date().toISOString() };
  saveManifest(manifest, null);
  const analysisDirectory = path.join(pipelineDirectory(strictModelId), "evidence/02-analysis/rev-001");
  fs.mkdirSync(analysisDirectory, { recursive: true });
  const discoveryAbsolute = path.join(analysisDirectory, "discovery-log.json");
  const boardAbsolute = path.join(analysisDirectory, "analysis-board.png");
  fs.writeFileSync(discoveryAbsolute, JSON.stringify({ finding: "linear magnetic slider", dimensionsMm: null }));
  fs.writeFileSync(boardAbsolute, Buffer.from("analysis-board"));
  const discoveryId = `${strictModelId}-discovery-r001`;
  const boardId = `${strictModelId}-board-r001`;
  const analysis = saveAnalysisResearchRevision(strictModelId, {
    expectedRevision: intake.manifest.revision,
    assets: [
      { id: discoveryId, slot: "discovery-log", path: path.relative(resolveRepoPath("."), discoveryAbsolute).split(path.sep).join("/"), sourceAssetIds: [intake.asset.id] },
      { id: boardId, slot: "analysis-board", path: path.relative(resolveRepoPath("."), boardAbsolute).split(path.sep).join("/"), sourceAssetIds: [intake.asset.id] }
    ],
    claims: [{
      id: `${strictModelId}-mechanism-r001`,
      category: "mechanism",
      statement: "这是线性磁吸推牌；尺寸须由严格来源给出。",
      confidence: "high",
      sourceAssetIds: [intake.asset.id]
    }],
    validations: [{ id: "no-generic-mm-inference", status: "pass", evidence: "No category-level millimetres were inferred." }]
  });
  manifest = loadManifest(strictModelId);
  manifest.stages[1].status = "approved";
  manifest.stages[1].decision = { action: "approve", notes: "fixture", decidedBy: "test", decidedAt: new Date().toISOString() };
  saveManifest(manifest, null);

  const official = saveMeasurementSource(strictModelId, {
    expectedRevision: analysis.revision,
    basisType: MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec,
    filename: "official-spec.png",
    mimeType: "image/png",
    dataBase64: Buffer.from("official-spec").toString("base64"),
    sourceUrl: "https://example.invalid/same-model/spec"
  });
  const teardown = saveMeasurementSource(strictModelId, {
    expectedRevision: official.manifest.revision,
    basisType: MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration,
    filename: "teardown.png",
    mimeType: "image/png",
    dataBase64: Buffer.from("teardown").toString("base64"),
    sourceUrl: "https://example.invalid/same-model/teardown"
  });
  assert.equal(official.sourceAsset.provenance.contentClass, "same-model-official-spec");
  assert.equal(teardown.sourceAsset.provenance.contentClass, "same-model-public-teardown-image");
  assert.match(official.sourceAsset.sha256, /^[a-f0-9]{64}$/);

  const officialEntry = (valueMm, uncertaintyMm = 0.1) => ({
    state: "known",
    unknown: false,
    valueMm,
    uncertaintyMm,
    source: "同款正式规格",
    basisType: MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec,
    sourceAssetIds: [official.assetId],
    method: "逐字抄录同款正式规格"
  });
  const calibratedEntry = (valueMm, targetPixelSpan, uncertaintyMm = 0.1) => ({
    state: "known",
    unknown: false,
    valueMm,
    uncertaintyMm,
    source: "同款公开拆解校准",
    basisType: MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration,
    sourceAssetIds: [official.assetId, teardown.assetId],
    method: "用同款正式长度锚点校准公开拆解图像像素比例",
    calibration: {
      anchorFieldId: "closedOverallLength",
      anchorOfficialValueMm: 50.5,
      imagePixelSpan: 505,
      targetPixelSpan,
      sourceAssetId: teardown.assetId
    }
  });
  const requiredMeasurements = {
    closedOverallLength: officialEntry(50.5),
    overallWidth: officialEntry(30.9),
    totalClosedThickness: officialEntry(13.6),
    topPlateThickness: calibratedEntry(6.5, 65),
    bottomPlateThickness: calibratedEntry(6.8, 68),
    maximumSlideTravel: calibratedEntry(18, 180, 0.2),
    fixedAxisOffsetFromNearestEnd: calibratedEntry(12, 120),
    rotatingCarrierDiameter: calibratedEntry(20, 200),
    closedSeamGap: calibratedEntry(0.3, 3, 0.05)
  };
  const saved = saveModelingContract(strictModelId, {
    expectedRevision: teardown.manifest.revision,
    measurementSchemaVersion: 2,
    measurementProvenanceVersion: 1,
    requiredMeasurements
  });
  assert.equal(saved.manifest.stages[2].status, "ready_for_review");
  assert.equal(saved.contract.completeness.complete, true);
  assert.equal(saved.contract.measurementProvenanceVersion, 1);
  assert.deepEqual(saved.contract.provenance.officialSpecificationFields.sort(), [
    "closedOverallLength", "overallWidth", "totalClosedThickness"
  ].sort());
  assert.equal(saved.contract.provenance.calibratedDigitalTargetFields.length, 6);
  assert.equal(saved.contract.measurements.required.topPlateThickness.claimClass, "provisional-digital-reconstruction-target");
  assert.equal(saved.contract.measurements.required.topPlateThickness.provisional, true);
  assert.equal(saved.contract.measurements.required.topPlateThickness.reversible, true);
  assert.equal(saved.contract.measurements.required.topPlateThickness.measured, false);
  assert.equal(saved.contract.measurements.required.topPlateThickness.manufacturingDimension, false);
  assert.equal(saved.contract.measurements.required.topPlateThickness.calibration.derivedValueMm, 6.5);
  assert.deepEqual(saved.contract.provenance.sourceEvidence.map(({ assetId }) => assetId).sort(), [official.assetId, teardown.assetId].sort());
  assert.ok(saved.contract.provenance.sourceEvidence.every(({ sha256 }) => /^[a-f0-9]{64}$/.test(sha256)));
});
