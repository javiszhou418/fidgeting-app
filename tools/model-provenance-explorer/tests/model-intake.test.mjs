import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  INTAKE_MAX_BYTES,
  modelThumbnail,
  requestStageWork,
  MODEL_MECHANISMS,
  PipelineError,
  addIntakeFile,
  createModelPipeline,
  listModelIds,
  loadManifest,
  pipelineDirectory,
  readHistory,
  stageReadiness
} from "../pipeline-core.mjs";

const modelId = `zz-test-intake-${process.pid.toString(36)}`;
const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });

test("createModelPipeline writes a manifest that the workbench can list and load", (t) => {
  t.after(cleanup);
  cleanup();
  const derived = createModelPipeline({ id: modelId, name: "测试陀螺", mechanism: "rotor" });
  assert.equal(derived.model.id, modelId);
  assert.equal(derived.model.name, "测试陀螺");
  assert.equal(derived.stages.length, 12);
  assert.equal(derived.stages[0].status, "draft");
  assert.equal(derived.derived.earliestProblem.stageId, "01-intake");
  assert.ok(listModelIds().includes(modelId));
  assert.ok(fs.existsSync(path.join(pipelineDirectory(modelId), "evidence/01-intake/rev-001")));
  assert.equal(readHistory(modelId)[0].type, "pipeline-created");
  assert.throws(() => createModelPipeline({ id: modelId, name: "重复" }), (error) => error instanceof PipelineError && error.statusCode === 409);
  assert.throws(() => createModelPipeline({ id: "Bad_ID", name: "x" }), PipelineError);
  assert.throws(() => createModelPipeline({ id: "ok-id", name: "" }), PipelineError);
  assert.throws(() => createModelPipeline({ id: "ok-id", name: "x", mechanism: "warp-drive" }), PipelineError);
  assert.ok(MODEL_MECHANISMS.some((option) => option.id === "rotor"));
});

test("addIntakeFile archives user references and makes Gate 01 reviewable", (t) => {
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "测试陀螺" });
  const png = Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47]), Buffer.alloc(64, 1)]);
  const first = addIntakeFile(modelId, { filename: "IMG 0001 正面.PNG", bytes: png });
  assert.equal(first.asset.slot, "original-reference");
  assert.equal(first.asset.role, "user-input");
  assert.equal(first.asset.provenance.origin, "user-provided");
  assert.equal(first.asset.provenance.contentClass, "user-photo");
  assert.match(first.asset.path, /evidence\/01-intake\/rev-001\/IMG-0001-正面\.png$/);
  assert.ok(fs.existsSync(path.join(pipelineDirectory(modelId), "evidence/01-intake/rev-001/IMG-0001-正面.png")));
  const second = addIntakeFile(modelId, { filename: "IMG 0001 正面.PNG", bytes: png, note: "背面" });
  assert.match(second.asset.path, /IMG-0001-正面-2\.png$/, "same filename does not overwrite");
  const doc = addIntakeFile(modelId, { filename: "spec.pdf", bytes: Buffer.from("%PDF-1.4") });
  const manifest = loadManifest(modelId);
  const gate01 = manifest.stages[0];
  assert.equal(gate01.status, "ready_for_review");
  assert.equal(gate01.revision, 1);
  assert.deepEqual(gate01.artifactIds, [first.asset.id, second.asset.id, doc.asset.id]);
  assert.deepEqual(gate01.reviewArtifactIds, [first.asset.id, second.asset.id], "documents are archived but not review images");
  assert.ok(gate01.validations.every((validation) => validation.status === "pass"));
  assert.equal(stageReadiness(manifest, "01-intake").ready, true);
  assert.equal(manifest.revision, 4);
  assert.equal(readHistory(modelId).filter((event) => event.type === "gate01-user-reference-added").length, 3);
  assert.throws(() => addIntakeFile(modelId, { filename: "model.exe", bytes: png }), /不支持的文件类型/);
  assert.throws(() => addIntakeFile(modelId, { filename: "empty.png", bytes: Buffer.alloc(0) }), /上传内容为空/);
  assert.ok(INTAKE_MAX_BYTES >= 256 * 1024 * 1024, "phone videos must fit");
});

test("adding a reference to an approved Gate 01 opens a new revision and stales downstream", (t) => {
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "测试陀螺" });
  const png = Buffer.alloc(32, 7);
  addIntakeFile(modelId, { filename: "a.png", bytes: png });
  const file = path.join(pipelineDirectory(modelId), "pipeline.json");
  const manifest = JSON.parse(fs.readFileSync(file, "utf8"));
  manifest.stages[0].status = "approved";
  manifest.stages[1].status = "ready_for_review";
  fs.writeFileSync(file, JSON.stringify(manifest));
  const result = addIntakeFile(modelId, { filename: "b.png", bytes: png });
  assert.equal(result.manifest.stages[0].revision, 2);
  assert.equal(result.manifest.stages[0].status, "ready_for_review");
  assert.equal(result.manifest.stages[1].status, "stale");
  assert.equal(result.manifest.stages[2].status, "blocked");
  assert.match(result.asset.path, /rev-002\/b\.png$/);
});

test("work requests are state + history for agent-produced gates", (t) => {
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "测试陀螺" });
  const before = loadManifest(modelId);
  assert.throws(() => requestStageWork(modelId, "01-intake", { expectedRevision: before.revision }), /Gate 01/);
  assert.throws(() => requestStageWork(modelId, "02-analysis", { expectedRevision: 99 }), (error) => error.statusCode === 409);
  const requested = requestStageWork(modelId, "02-analysis", { expectedRevision: before.revision });
  assert.equal(requested.currentState.workRequests["02-analysis"].status, "requested");
  assert.deepEqual(requested.currentState.workRequests["02-analysis"].deliverables, ["discovery-log", "analysis-board"]);
  assert.match(requested.currentState.diagnosis, /已请求 agent 开始/);
  assert.equal(requested.stages[1].status, "blocked", "requesting does not pretend the gate progressed");
  const withdrawn = requestStageWork(modelId, "02-analysis", { expectedRevision: requested.revision, action: "withdraw" });
  assert.equal(withdrawn.currentState.workRequests["02-analysis"], undefined);
  const types = readHistory(modelId).map((event) => event.type);
  assert.ok(types.includes("stage-work-requested") && types.includes("stage-work-withdrawn"));
});

test("model thumbnail prefers the shipping app's product thumbnail", () => {
  const manifest = loadManifest("metal-three-blade");
  assert.equal(modelThumbnail(manifest), "unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png");
});
